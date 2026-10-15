"""Synthetic policy/decision contracts, separate from actual-data pilot evidence."""
import unittest
import numpy as np
import torch
from safe_iad.acquisition import InferenceInputs,select_learned_reference
from safe_iad.counterfactual import support_diagnostics
from safe_iad.support_decision import adequacy_field,action
from safe_iad.run_benefit_pilot import validate_pilot_config


class ObservableModel:
    def predict(self,vectors,**kwargs):
        return np.asarray(vectors)[:,0]


class SyntheticBenefitPilotTests(unittest.TestCase):
    def inputs(self,ids=('a','b')):
        return InferenceInputs(torch.tensor([1.,0.]),torch.tensor([[1.,0.]]),
                               torch.tensor([[1.,0.],[0.,1.]]),ids,7,'opaque-query')

    def test_learned_selection_has_no_mask_argument(self):
        with self.assertRaises(TypeError):
            select_learned_reference(self.inputs(),[[1.],[2.]],ObservableModel(),budget=1,
                                     feature_names=['observable'],provenance={},truth=np.ones((2,2)))

    def test_equal_reference_forced_and_optional_abstention(self):
        index,predictions=select_learned_reference(self.inputs(),[[-2.],[-1.]],ObservableModel(),
                                                  budget=1,feature_names=['observable'],provenance={})
        self.assertEqual(index,1)
        self.assertEqual(predictions,[-2.,-1.])
        index,_=select_learned_reference(self.inputs(),[[-2.],[-1.]],ObservableModel(),budget=1,
                                         feature_names=['observable'],provenance={},minimum_benefit=0)
        self.assertIsNone(index)

    def test_budget_and_duplicate_candidates_rejected(self):
        for inputs,budget in [(self.inputs(),2),(self.inputs(('a','a')),1)]:
            with self.assertRaises(ValueError):
                select_learned_reference(inputs,[[1.],[2.]],ObservableModel(),budget=budget,
                                         feature_names=['observable'],provenance={})

    def test_weak_diagnostics_preserve_defect_evidence(self):
        query=torch.tensor([[0.,1.]])
        reference=torch.tensor([[1.,0.],[.9,.1]])
        diagnostics=support_diagnostics(query,[reference])
        original=diagnostics['nearest_distance'].clone()
        field=adequacy_field(diagnostics)
        self.assertTrue(torch.equal(original,diagnostics['nearest_distance']))
        self.assertIsNone(diagnostics['loo_sensitivity'])
        self.assertFalse(bool(diagnostics['loo_valid'].any()))
        decision,evidence=action(1.2,float(field.mean()),.5)
        self.assertEqual(decision,'unresolved/reference-insufficient')
        self.assertTrue(evidence)

    def test_runner_rejects_final_category_relabeling_and_unimplemented_budget(self):
        config={'acquisition_budget':1,'evaluation_shots':[1,2],'seeds':[0,1,2],
                'validation_categories':{'d':'v'},'category_roles':{'d':{'validation':['v'],'final_test':['f']}}}
        validate_pilot_config(config)
        with self.assertRaises(ValueError):validate_pilot_config({**config,'acquisition_budget':2})
        with self.assertRaises(ValueError):validate_pilot_config({**config,'validation_categories':{'d':'f'}})


if __name__=='__main__':
    unittest.main()
