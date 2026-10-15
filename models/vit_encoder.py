"""Frozen DINOv2 ViT-L/14 register encoder and declared image geometry."""
from utils import use_local_framework

use_local_framework()

from safe_iad.vision_hybrid_features import RegisterEncoder, preprocess, roi_mask


class Encoder(RegisterEncoder):
    """Verified official weights, fixed support augmentation and query slots."""


__all__ = ["Encoder", "preprocess", "roi_mask"]
