import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
from PIL import Image
from sklearn.decomposition import PCA
import torch
import torch.nn.functional as F

from safe_iad.vision_hybrid_features import preprocess,transform,support_inputs,roi_mask,metric_map,image_score,SLOTS
from safe_iad.vision_hybrid_model import LocalSubspaces,HybridParameters,VisionHybrid,fuse_raw,parameter_grid


class FeatureGeometryTests(unittest.TestCase):
    def test_crop_and_normalization_match_independent_pillow(self):
        rng=np.random.default_rng(7);im=Image.fromarray(rng.integers(0,256,(71,89,3),dtype=np.uint8))
        x=preprocess(im,56,28)
        expected=np.asarray(im.resize((56,56),Image.Resampling.BILINEAR).crop((14,14,42,42)),dtype=np.float32)/255.
        expected=(expected-np.array([.485,.456,.406],np.float32))/np.array([.229,.224,.225],np.float32)
        np.testing.assert_array_equal(x[0].permute(1,2,0).numpy(),expected)

    def test_group_reuse_keeps_all_six_views_per_slot(self):
        x=torch.arange(3*4*4,dtype=torch.float32).reshape(1,3,4,4)-20
        unique,slots=support_inputs(x)
        self.assertEqual(len(unique),14)
        for slot in SLOTS:
            self.assertEqual(len(slots[slot]),6)
            for i,view in zip(slots[slot],('identity','rot90','rot180','rot270','vflip','hflip')):
                self.assertTrue(torch.equal(unique[i],transform(transform(x,slot),view)))
        self.assertTrue(torch.equal(transform(transform(x,'vflip'),'vflip'),x))

    def test_mask_crop_drops_border_without_warping_it(self):
        mask=np.zeros((56,56),np.uint8);mask[0:4]=255;mask[20:23,21:24]=255
        got=roi_mask(Image.fromarray(mask),56,28,28)
        self.assertEqual(int(got.sum()),9)
        self.assertTrue(got[6:9,7:10].all())

    def test_top_fraction_is_of_processed_metric_map(self):
        x=torch.arange(16,dtype=torch.float64)
        got=metric_map(x,4)
        expected=F.interpolate(x.float().reshape(1,1,4,4),(256,256),mode='bilinear',align_corners=False)[0,0].numpy()
        np.testing.assert_array_equal(got,expected)
        self.assertEqual(image_score(got),float(torch.tensor(expected).flatten().topk(655).values.mean()))


class HybridMathematicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):torch.set_num_threads(1)

    def test_global_relative_residual_matches_sklearn_pca(self):
        rng=np.random.default_rng(3);support=rng.normal(size=(100,8))*np.arange(1,9);query=rng.normal(size=(17,8))
        sub=LocalSubspaces(support,1,(.95,.99),threads=1)
        values=sub.score(query);energy=((support-support.mean(0))**2).sum()/len(support)
        for v in [.95,.99]:
            p=PCA(n_components=v,svd_solver='full').fit(support)
            expected=((query-p.inverse_transform(p.transform(query)))**2).sum(1)/energy
            np.testing.assert_allclose(values[str(v)].numpy(),expected,rtol=1e-10,atol=1e-11)
            self.assertEqual(sub.groups[0]['ranks'][str(v)],p.n_components_)

    def test_local_subspaces_use_nearest_normal_centroid(self):
        rng=np.random.default_rng(5)
        support=np.concatenate([rng.normal([10,0,0,0],[.1,.6,.1,.1],(80,4)),rng.normal([0,10,0,0],[.6,.1,.1,.1],(80,4))])
        sub=LocalSubspaces(support,2,(.95,),threads=1)
        q=np.array([[10,0,0,0],[0,10,0,0]],float)
        self.assertNotEqual(int(sub.assign(q)[0]),int(sub.assign(q)[1]))
        for i,group in enumerate(sub.groups):
            indices=sub.assign(support).numpy()==i;ref=PCA(n_components=.95,svd_solver='full').fit(support[indices])
            chosen=sub.assign(q).numpy()==i
            expected=((q[chosen]-ref.inverse_transform(ref.transform(q[chosen])))**2).sum(1)/group['energy']
            np.testing.assert_allclose(sub.score(q)['0.95'].numpy()[chosen],expected,atol=1e-10)

    def test_zero_correction_and_vertical_map_alignment(self):
        raw={'search':{s:torch.arange(4,dtype=torch.float64) for s in SLOTS},'residual':{}}
        p=HybridParameters();got=fuse_raw(raw,p,2)
        expected=torch.arange(4,dtype=torch.float64)*2+torch.arange(4,dtype=torch.float64).reshape(2,2).flip(0).flatten()
        self.assertTrue(torch.equal(got['raw_sum'],expected))
        np.testing.assert_array_equal(got['map'],metric_map(expected,2))

    def test_nonnegative_correction_preserves_baseline_alerts_at_same_threshold(self):
        rng=np.random.default_rng(8)
        raw={'search':{s:torch.tensor(rng.random(16)) for s in SLOTS},'residual':{'4':{'0.99':{s:torch.tensor(rng.random(16)) for s in SLOTS}}}}
        baseline=fuse_raw(raw,HybridParameters(),4)
        for gate in ['uniform','residual_ratio']:
            got=fuse_raw(raw,HybridParameters(4,.99,.5,gate),4)
            self.assertTrue((got['map']>=baseline['map']).all())
            self.assertGreaterEqual(got['image_score'],baseline['image_score'])
        # Zero/zero has a defined zero gate, rather than epsilon normalization.
        for v in raw['search'].values():v.zero_()
        for v in raw['residual']['4']['0.99'].values():v.zero_()
        self.assertEqual(fuse_raw(raw,HybridParameters(4,.99,.5,'residual_ratio'),4)['image_score'],0.)

    def test_grid_and_invalid_inputs(self):
        grid=parameter_grid();self.assertEqual(len(grid),25);self.assertEqual(len({p.id for p in grid}),25)
        for kwargs in [dict(strength=-1),dict(strength=float('nan')),dict(clusters=True),dict(variance=0),dict(gate='probability'),dict(clusters=4)]:
            with self.assertRaises((ValueError,TypeError)):HybridParameters(**kwargs)
        for bad in [np.zeros((10,4)),np.ones((1,4)),np.full((10,4),np.nan)]:
            with self.assertRaises(ValueError):LocalSubspaces(bad,1)
        with self.assertRaises(ValueError):LocalSubspaces(np.ones((10,4)),1)

    def test_checkpoint_replay_and_tamper_rejection(self):
        rng=np.random.default_rng(11);views=[rng.normal(size=(16,8)).astype(np.float32) for _ in range(14)]
        _,slots=support_inputs(torch.arange(48,dtype=torch.float32).reshape(1,3,4,4)-20)
        model=VisionHybrid(views,slots,['normal/train/one.png'],threads=1)
        p=HybridParameters(4,.95,.1,'residual_ratio');query={s:rng.normal(size=(16,8)).astype(np.float32) for s in SLOTS}
        expected=model.predict(query,p)
        with tempfile.TemporaryDirectory() as d:
            prefix=Path(d)/'model';model.save(prefix,p,.5,{'encoder':'synthetic fixture'})
            restored=VisionHybrid.load(prefix);got=restored.predict(query)
            self.assertEqual(got['image_score'],expected['image_score'])
            np.testing.assert_array_equal(got['map'],expected['map'])
            with self.assertRaises(ValueError):model.save(prefix,p,.5,{})
            data=prefix.with_suffix('.npz').read_bytes();prefix.with_suffix('.npz').write_bytes(data+b'x')
            with self.assertRaises(ValueError):VisionHybrid.load(prefix)


if __name__=='__main__':unittest.main()
