"""Protocol/geometry/statistics unit tests; not substitute benchmark data."""
import tempfile
from pathlib import Path
import unittest

import numpy as np
from PIL import Image
import torch

from controlled_common import (cluster_bootstrap, full_prediction, full_truth,
                              measured_metrics, normal_cutoff, paired_bootstrap,
                              select_figures, validate_roles)
from controlled_experiment import choose_support


class ControlledTests(unittest.TestCase):
    def test_calibration_fails_on_id_overlap_even_with_distinct_paths(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/"a",Path(d)/"b";a.touch();b.touch()
            cal=dict(image_id="ad2:a",path=str(a),dataset="mvtec_ad2",split="train",label="normal")
            other=dict(cal,path=str(b))
            with self.assertRaisesRegex(ValueError,"leakage"):
                validate_roles({"calibration":[cal],"support":[other]})

    def test_calibration_fails_on_path_alias_and_target_or_anomaly(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/"a";a.touch()
            cal=dict(image_id="ad2:a",path=str(a),dataset="mvtec_ad2",split="train",label="normal")
            with self.assertRaisesRegex(ValueError,"leakage"):
                validate_roles({"calibration":[cal],"evaluation":[dict(cal,image_id="visa:a")]})
            for changes in ({"dataset":"visa"},{"split":"test_public"},{"label":"anomaly"}):
                with self.assertRaisesRegex(ValueError,"SOURCE"):
                    validate_roles({"calibration":[dict(cal,**changes)]})
            self.assertTrue(validate_roles({"calibration":[cal],"support":[]})["passed"])

    def test_upper_quantile_and_strict_ties_control_empirical_fpr(self):
        for values in (np.arange(40,dtype=np.float32),np.ones(40),np.arange(20)//3):
            cutoff=normal_cutoff(values,.05)
            self.assertLessEqual(cutoff["realised_calibration_fpr"],.05)
            self.assertEqual(cutoff["realised_calibration_fpr"],float((values>cutoff["cutoff"]).mean()))
        with self.assertRaises(ValueError):normal_cutoff([np.nan],.05)

    def test_full_gt_keeps_all_four_border_defects_and_matches_map(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            Image.new("RGB",(448,448)).save(root/"image.png")
            mask=np.zeros((448,448),np.uint8)
            mask[0,:]=255;mask[-1,:]=255;mask[:,0]=255;mask[:,-1]=255
            Image.fromarray(mask).save(root/"mask.png")
            truth=full_truth(root/"image.png",root/"mask.png")
            np.testing.assert_array_equal(truth,mask>0)
            Image.new("L",(400,448)).save(root/"wrong.png")
            with self.assertRaises(ValueError):full_truth(root/"image.png",root/"wrong.png")

    def test_zero_control_is_exact_and_positive_lambda_changes_real_fusion(self):
        search={slot:torch.arange(4,dtype=torch.float64)+.1 for slot in ("identity","vflip","clamp")}
        residual={slot:torch.ones(4,dtype=torch.float64) for slot in search}
        raw={"search":search,"residual":{"1":{"0.95":residual}}}
        a,sa=full_prediction(raw,0,2)
        b,sb=full_prediction(raw,0.,2)
        c,sc=full_prediction(raw,.1,2)
        self.assertEqual(a.shape,(448,448));np.testing.assert_array_equal(a,b);self.assertEqual(sa,sb)
        self.assertGreater(np.max(abs(c-a)),0);self.assertGreater(sc,sa)

    def test_cluster_bootstrap_averages_draws_before_resampling_categories(self):
        samples,indices=cluster_bootstrap({"a":[0.,0.,0.],"b":[1.]},100,17)
        np.testing.assert_array_equal(samples,np.mean(np.array([0.,1.])[indices],axis=1))
        np.testing.assert_array_equal(samples,cluster_bootstrap({"a":[0.,0.,0.],"b":[1.]},100,17)[0])

    def test_support_draws_are_repeatable_nested_and_train_normal_only(self):
        rows=[dict(image_id=str(i),split="train",label="normal") for i in range(20)]
        rows += [dict(image_id="never",split="test",label="anomaly")]
        self.assertEqual(choose_support(rows,17),choose_support(rows,17))
        self.assertEqual(choose_support(rows,17,1),choose_support(rows,17,3)[:1])
        self.assertNotIn("never",choose_support(rows,17,3))

    def test_rule_selection_reports_absent_events(self):
        rows=[dict(image_id="normal",label=0,scores={"hybrid":0.},truth_pixels=0,hybrid_pixel_iou=None),
              dict(image_id="small",label=1,scores={"hybrid":2.},truth_pixels=1,hybrid_pixel_iou=.1)]
        chosen=select_figures(rows,1.)
        self.assertEqual(chosen["true_negative"],"normal")
        self.assertIsNone(chosen["false_positive"]);self.assertIsNone(chosen["miss"])
        self.assertEqual(chosen["smallest_defect"],"small")

    def test_bootstrap_resamples_images_and_matches_direct_pixel_auc_and_counts(self):
        from sklearn.metrics import roc_auc_score
        truth=[np.zeros((3,4),bool) for _ in range(4)]
        truth[2][1,1]=True;truth[3][1:,2]=True
        rng=np.random.default_rng(17)
        maps=[rng.integers(0,5,size=(3,4)).astype(np.float32) for _ in range(4)]
        other=[m+.2*t for m,t in zip(maps,truth)]
        rows=[dict(label=int(t.any()),scores={"baseline":float(m.max()),"hybrid":float(h.max())})
              for t,m,h in zip(truth,maps,other)]
        cuts={method:{"image":{"cutoff":3.},"pixel":{"cutoff":2.}}
              for method in ("baseline","hybrid")}
        boot=paired_bootstrap(truth,{"baseline":maps,"hybrid":other},rows,cuts,30,17)
        for i,weights in enumerate(boot["image_multiplicities"]):
            indices=np.repeat(np.arange(4),weights)
            for method,values in (("baseline",maps),("hybrid",other)):
                labels=np.concatenate([truth[j].ravel() for j in indices])
                scores=np.concatenate([values[j].ravel() for j in indices])
                self.assertAlmostEqual(roc_auc_score(labels,scores),boot[method+"_pixel_auroc"][i])
                tp=((scores>2)&labels).sum();fp=((scores>2)&~labels).sum();fn=((scores<=2)&labels).sum()
                self.assertAlmostEqual(tp/(tp+fp+fn),boot[method+"_pixel_iou"][i])
        measured=measured_metrics(truth,maps,[r["label"] for r in rows],
                                 [r["scores"]["baseline"] for r in rows],cuts["baseline"])
        flat_truth=np.concatenate([t.ravel() for t in truth])
        flat_scores=np.concatenate([m.ravel() for m in maps])
        tp=((flat_scores>2)&flat_truth).sum();fp=((flat_scores>2)&~flat_truth).sum();fn=((flat_scores<=2)&flat_truth).sum()
        self.assertAlmostEqual(measured["pixel_iou"],tp/(tp+fp+fn))
        self.assertEqual(measured["cutoff_decision"],"strict >")


if __name__=="__main__":unittest.main()
