"""Mathematical/contract tests; fixtures are never benchmark evidence."""
from pathlib import Path
import tempfile
import unittest

import numpy as np
from sklearn.decomposition import PCA
from sklearn.metrics import average_precision_score, roc_auc_score
import torch

from safe_iad.baselines import FittedMethod, official_modules
from safe_iad.dense_features import DenseFeatures, letterbox_geometry, restore_dense
from safe_iad.hybrid import DecisionThresholds, SupportHybrid, decide
from safe_iad.official_ad2 import export_map, official_checker, relative_output, validate_complete_submission
from safe_iad.pipeline_metrics import PixelHistogram, best_f1, metrics
from safe_iad.run_pipeline import immutable_json, require_calibration_role


torch.set_num_threads(3)


def bundle(tokens, mode):
    return DenseFeatures(tokens, (4, 4), (50, 30), (56, 56), (56, 56), mode, 'unit-fixture', False)


class HybridPipelineTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(3)

    def test_aspect_resize_padding_geometry(self):
        self.assertEqual(letterbox_geometry((600, 300), 224), ((224, 112), (224,112)))
        resized, padded = letterbox_geometry((641, 313), 224)
        self.assertLess(abs(resized[0]/resized[1]-641/313), .02)
        self.assertTrue(all(x % 14 == 0 for x in padded))

    def test_native_restore_removes_padding(self):
        b = DenseFeatures(torch.zeros(4,2), (2,2), (40,20), (28,14), (28,28), 'hybrid', 'fixture', False)
        m = restore_dense(torch.tensor([1.,1.,9.,9.]), b)
        self.assertEqual(m.shape, (20,40))
        # With identical token values native maps remain identical after trim.
        np.testing.assert_allclose(restore_dense(torch.ones(4),b),1,atol=1e-6)
        self.assertLess(float(m.mean()), 5)

    def test_pca_dual_projector_matches_independent_sklearn(self):
        memory = torch.randn(32,8)
        engine = SupportHybrid(memory, explained_variance=.9)
        normalized = torch.nn.functional.normalize(memory,dim=1).numpy()
        reference = PCA(n_components=.9,svd_solver='full').fit(normalized)
        actual = engine.components.numpy() @ engine.components.numpy().T
        expected = reference.components_.T @ reference.components_
        np.testing.assert_allclose(actual,expected,atol=2e-5)

    def test_adequacy_bounded_and_density_sensitive(self):
        engine = SupportHybrid(torch.tensor([[1.,0.,0.],[.9,.1,0.],[.8,.2,0.],[.7,.3,0.]]))
        out = engine.predict(torch.tensor([[.9,.1,0.],[0.,0.,1.]]))
        self.assertTrue(((out['adequacy']>=0)&(out['adequacy']<=1)).all())
        self.assertGreater(float(out['adequacy'][0]),float(out['adequacy'][1]))

    def test_degenerate_support_has_no_invented_spectral_diversity(self):
        engine = SupportHybrid(torch.ones(8,3))
        out = engine.predict(torch.ones(2,3))
        self.assertEqual(engine.components.shape[1],0)
        self.assertEqual(engine.normalized_entropy,0)
        self.assertTrue(torch.isfinite(out['defect']).all())
        self.assertTrue((out['adequacy']==0).all())

    def test_low_adequacy_cannot_erase_raw_evidence(self):
        engine = SupportHybrid(torch.randn(16,4))
        out = engine.predict(torch.randn(12,4))
        self.assertTrue((out['defect']>=out['local']).all())
        self.assertTrue((out['defect']>=out['global_residual']).all())

    def test_low_adequacy_review_preserves_high_evidence_flag(self):
        cut = DecisionThresholds(.4,.3,.5,('calibration:1',))
        self.assertEqual(decide(.8,.1,cut),('unresolved/reference-insufficient',True))
        self.assertEqual(decide(.8,.8,cut),('defective',True))
        self.assertEqual(decide(.2,.8,cut),('normal',False))

    def test_calibration_cannot_accept_final_role(self):
        with self.assertRaises(ValueError):
            require_calibration_role(dict(role='final_test'))

    def test_calibration_rejects_native_test_defect_labels(self):
        with self.assertRaisesRegex(ValueError,'Native-test'):
            require_calibration_role(dict(role='calibration',queries=[dict(split='test',label='anomaly')]))

    def test_threshold_requires_calibration_provenance(self):
        with self.assertRaises(ValueError):
            DecisionThresholds(.1,.1,.5,())

    def test_offline_f1_max_does_not_replace_locked_cutoff(self):
        out = metrics([0,1],[.1,.8],.9)
        self.assertEqual(out['f1_max_offline'],1)
        self.assertEqual(out['locked_threshold'],.9)
        self.assertEqual(out['locked_f1'],0)

    def test_official_anomalydino_supported_core_matches_manual_cosine(self):
        s,q=torch.randn(16,8),torch.randn(16,8)
        model=FittedMethod('anomalydino',[bundle(s,'anomalydino')],{})
        actual=model.predict(bundle(q,'anomalydino'))
        normalized_s=torch.nn.functional.normalize(s,dim=1)
        normalized_q=torch.nn.functional.normalize(q,dim=1)
        manual=(1-normalized_q@normalized_s.T).min(dim=1).values.numpy()
        utils, evaluation,_,_=official_modules()
        self.assertAlmostEqual(actual['image_score'],evaluation.mean_top1p(manual),places=5)
        np.testing.assert_allclose(actual['maps']['defect'],utils.dists2map(manual.reshape(4,4),(30,50,3)),atol=1e-6)

    def test_official_subspacead_core_matches_independent_reconstruction(self):
        s,q=torch.randn(16,8),torch.randn(16,8)
        model=FittedMethod('subspacead',[bundle(s,'subspacead')],{'subspace_explained_variance':.9})
        _,_,_,scoring=official_modules()
        actual=scoring.calculate_anomaly_scores(q.numpy(),model.engine,'reconstruction')
        independent=PCA(n_components=.9,svd_solver='full').fit(s.numpy())
        residual=((q.numpy()-independent.inverse_transform(independent.transform(q.numpy())))**2).sum(axis=1)
        np.testing.assert_allclose(actual,residual,atol=1e-5)

    def test_native_float16_histogram_auc_ap_f1_matches_sklearn(self):
        rng=np.random.default_rng(12)
        truth=rng.integers(0,2,500).astype(bool)
        scores=rng.random(500).astype('float16').astype('float32')
        h=PixelHistogram(); h.update(truth[:200],scores[:200]); h.update(truth[200:],scores[200:])
        out=h.metrics(.5)
        self.assertAlmostEqual(out['auroc'],roc_auc_score(truth,scores),places=12)
        self.assertAlmostEqual(out['ap'],average_precision_score(truth,scores),places=12)
        self.assertAlmostEqual(out['f1_max_offline'],best_f1(truth,scores)[0],places=12)

    def test_immutable_metrics_refuse_overwrite(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as d:
            p=Path(d)/'metrics.json'; immutable_json(p,{'a':1}); immutable_json(p,{'a':1})
            with self.assertRaisesRegex(ValueError,'Immutable'):
                immutable_json(p,{'a':2})

    def test_real_official_export_checker_validates_float16_and_binary(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as d:
            record=export_map(d,'can/test_public/bad/001.png',np.arange(24,dtype='float32').reshape(4,6)/24,.5)
            self.assertEqual(record['dtype'],'float16')
            self.assertEqual(record['scope'],'local_public_or_validation_only')
            checker=official_checker(); checker._check_ad_images(Path(record['path']))
            checker._check_thresholded_ad_images(Path(record['thresholded_path']))
            with self.assertRaises(checker.SubmissionException):
                # Imported checker classes have distinct module instances.
                checker.check_anomaly_image_dir(Path(d)/'anomaly_images','.tiff')

    def test_export_rejects_escape_nan_and_float16_overflow(self):
        with self.assertRaises(ValueError):
            relative_output('../can/test_public/001.png')
        with tempfile.TemporaryDirectory(dir='/tmp') as d:
            for value in [np.nan,70000.]:
                with self.assertRaises(ValueError):
                    export_map(d,'can/test_public/bad/001.png',np.full((3,3),value))


if __name__=='__main__':
    unittest.main()
