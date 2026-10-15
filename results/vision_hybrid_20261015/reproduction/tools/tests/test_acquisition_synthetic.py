"""Synthetic policy/leakage/missingness tests; no benchmark evidence."""
import unittest

import numpy as np
import torch

from safe_iad.acquisition import InferenceInputs, add_reference, select_reference
from safe_iad.counterfactual import evaluation_oracle, offline_loss, support_diagnostics
from safe_iad.patch_nn import patch_nearest_neighbor
from safe_iad.splits import require_training_source, validate_category_roles, validate_partition
from safe_iad.verify_dataset import Sample


class SyntheticAcquisitionTests(unittest.TestCase):
    def inputs(self):
        return InferenceInputs(torch.tensor([1.,0.]),torch.tensor([[1.,0.]]),torch.tensor([[1.,0.],[0.,1.]]),('a','b'),123,'opaque-query-id')

    def test_synthetic_one_reference_loo_is_missing(self):
        query=torch.tensor([[1.,0.],[0.,1.]])
        result=support_diagnostics(query,[query])
        self.assertIsNone(result['loo_sensitivity'])
        self.assertFalse(result['loo_valid'].any())

    def test_synthetic_diagnostics_preserve_detector_evidence(self):
        query=torch.tensor([[1.,1.],[0.,1.]])
        references=[torch.tensor([[1.,0.],[1.,0.]]),torch.tensor([[0.,1.],[0.,1.]])]
        result=support_diagnostics(query,references)
        torch.testing.assert_close(result['nearest_distance'],patch_nearest_neighbor(query,torch.cat(references)))
        self.assertTrue(result['loo_valid'].all())

    def test_synthetic_nearest_and_diversity_use_features(self):
        self.assertEqual(select_reference('nearest_global',self.inputs(),budget=1),0)
        self.assertEqual(select_reference('diversity',self.inputs(),budget=1),1)

    def test_synthetic_random_is_deterministic(self):
        actual=[select_reference('random',self.inputs(),budget=1) for _ in range(5)]
        self.assertEqual(len(set(actual)),1)

    def test_synthetic_policy_input_rejects_query_labels(self):
        with self.assertRaises(TypeError):
            InferenceInputs(torch.tensor([1.,0.]),torch.tensor([[1.,0.]]),torch.tensor([[1.,0.]]),('a',),1,'q',query_label=1)

    def test_synthetic_oracle_rejected_in_deployment(self):
        with self.assertRaisesRegex(ValueError,'offline evaluation'):
            select_reference('oracle',self.inputs(),budget=1)

    def test_synthetic_budget_and_repeat_enforced(self):
        with self.assertRaises(ValueError):
            select_reference('random',self.inputs(),budget=0)
        with self.assertRaises(ValueError):
            add_reference(['a'],'a',budget=1)
        with self.assertRaises(ValueError):
            add_reference(['a'],'b',budget=0)

    def test_synthetic_candidate_query_overlap_rejected(self):
        with self.assertRaises(ValueError):
            validate_partition(['a'],['b'],['b'])

    def test_synthetic_calibration_and_test_sources_rejected(self):
        config={'category_roles':{'mvtec_ad':{'meta_training':['source'],'validation':['val'],'calibration':['cal'],'final_test':['test']}}}
        for category in ['val','cal','test']:
            with self.assertRaises(ValueError):
                require_training_source('mvtec_ad',Sample(category,'train','normal','img',None),config)
        with self.assertRaises(ValueError):
            require_training_source('mvtec_ad',Sample('source','test','anomaly','img','mask'),config)

    def test_synthetic_category_roles_overlap_rejected(self):
        roles={'meta_training':['a'],'validation':['b'],'calibration':['b'],'final_test':['c']}
        with self.assertRaises(ValueError):
            validate_category_roles(roles,['a','b','c'])

    def test_synthetic_loss_detects_defect_explanation_away(self):
        truth=np.ones((2,2),dtype=bool)
        loss={'type':'balanced_pixel_margin_mse','margin':1.}
        before=offline_loss(np.ones((2,2)),truth,loss)
        after=offline_loss(np.zeros((2,2)),truth,loss)
        self.assertLess(before-after,0.)

    def test_synthetic_image_loss_uses_actual_image_score(self):
        loss={'type':'image_margin_mse','margin':1.}
        truth=np.zeros((2,2),dtype=bool)
        with self.assertRaises(ValueError):
            offline_loss(np.ones((2,2)),truth,loss)
        self.assertEqual(offline_loss(np.ones((2,2)),truth,loss,image_score=.5),.25)

    def test_synthetic_oracle_can_have_negative_best_benefit(self):
        self.assertEqual(evaluation_oracle([-2.,-.1,-1.]),1)


if __name__=='__main__':
    unittest.main()
