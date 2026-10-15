"""SAFAL reference-memory model with a source-selected PCA correction.

The shared numerical implementation stays in framework/safe_iad so the
previous fitted banks keep their verified source hashes and scoring behavior.
"""
from utils import use_local_framework

use_local_framework()

from safe_iad.vision_hybrid_model import HybridParameters, VisionHybrid, fuse_raw


class SAFAL(VisionHybrid):
    """Fit augmented normal descriptors, then score query descriptors.

    ``raw`` exposes the search and PCA branches. ``predict`` uses parameters
    loaded from a selected checkpoint. The foundation encoder is separate.
    """


__all__ = ["SAFAL", "HybridParameters", "fuse_raw"]
