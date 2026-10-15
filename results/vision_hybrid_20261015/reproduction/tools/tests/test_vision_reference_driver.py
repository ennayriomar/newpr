import unittest
import numpy as np
import torch

from benchmark_vision_reference import patch_search,reference_map
from safe_iad.vision_hybrid_model import HybridParameters,fuse_raw
from safe_iad.vision_hybrid_features import SLOTS


class ReferenceDriverTests(unittest.TestCase):
    def test_cosine_nearest_neighbour_against_closed_form(self):
        query=np.array([[1,0],[0,1],[1,1],[-1,0]],np.float32)
        memory=np.array([[1,0],[0,1]],np.float32)
        np.testing.assert_allclose(patch_search(query,memory).numpy(),[0,0,1-1/np.sqrt(2),1],atol=1e-7)
        with self.assertRaises(ValueError):patch_search(np.zeros((2,2),np.float32),memory)

    def test_full_driver_and_study_share_baseline_math(self):
        rng=np.random.default_rng(41)
        query={s:torch.from_numpy(rng.normal(size=(4,8)).astype(np.float32)) for s in SLOTS}
        memory={s:torch.from_numpy(rng.normal(size=(12,8)).astype(np.float32)) for s in SLOTS}
        raw={'search':{s:patch_search(query[s],memory[s]).double() for s in SLOTS},'residual':{}}
        expected=fuse_raw(raw,HybridParameters(),2)['map']
        np.testing.assert_array_equal(reference_map(query,memory,2),expected)


if __name__=='__main__':unittest.main()
