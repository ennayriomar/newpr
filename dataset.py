"""Native MVTec AD and VisA datasets with explicit normal-support roles."""
from __future__ import annotations

from pathlib import Path
import random

import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset

from utils import use_local_framework

use_local_framework()

from safe_iad.safal_cli import inventory
from safe_iad.vision_hybrid_features import preprocess, roi_mask


class IndustrialDataset(Dataset):
    """Return normalized images, cropped masks, native labels and image IDs."""

    def __init__(self, root, dataset, category, phase="test"):
        if dataset not in {"mvtec_ad", "visa"} or phase not in {"train", "test"}:
            raise ValueError("Use mvtec_ad/visa and native train/test phases.")
        self.root, self.lookup = inventory({"roots": {dataset: str(root)}}, dataset)
        self.dataset, self.category, self.phase = dataset, category, phase
        self.samples = sorted(
            (sample for sample in self.lookup.values()
             if sample.category == category and sample.split == phase),
            key=lambda sample: sample.image,
        )
        if not self.samples:
            raise ValueError(f"No {phase} images for category {category!r}.")
        if phase == "train" and any(sample.label != "normal" for sample in self.samples):
            raise ValueError("Only native normal training images may fit a target bank.")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        sample = self.samples[index]
        with Image.open(self.root / sample.image) as image:
            tensor = preprocess(image)[0]
        mask = self.mask(sample)
        return {"image": tensor, "mask": torch.from_numpy(mask),
                "label": int(sample.label != "normal"), "sample_id": sample.image,
                "image_path": str(self.root / sample.image)}

    def mask(self, sample, resize=448, crop=392):
        if sample.mask:
            with Image.open(self.root / sample.mask) as image:
                return roi_mask(image, resize=resize, crop=crop)
        return np.zeros((256, 256), dtype=bool)

    def support_ids(self, shots=1, seed=17, explicit=None):
        if self.phase != "train" or type(shots) is not int or shots < 1:
            raise ValueError("Positive shots and the native training split are required.")
        available = [sample.image for sample in self.samples]
        if explicit:
            selected = list(explicit)
            if len(selected) != shots or len(set(selected)) != shots:
                raise ValueError("Explicit support IDs must be distinct and match --shots.")
            if not set(selected).issubset(available):
                raise ValueError("Support IDs must be normal native train images of this category.")
            return selected
        if shots > len(available):
            raise ValueError("Not enough original normal references for the requested shots.")
        return random.Random(seed).sample(available, shots)

    def queries(self, limit=None):
        if self.phase != "test":
            raise ValueError("Queries must use the native test split.")
        if limit is None:
            return list(self.samples)
        if type(limit) is not int or limit < 1:
            raise ValueError("--max-images must be positive.")
        groups = [[s for s in self.samples if (s.label != "normal") == label]
                  for label in (False, True)]
        interleaved = []
        for i in range(max(map(len, groups))):
            interleaved.extend(group[i] for group in groups if i < len(group))
        return interleaved[:limit]


class MVTecDataset(IndustrialDataset):
    def __init__(self, root, category, phase="test"):
        super().__init__(root, "mvtec_ad", category, phase)


class VisADataset(IndustrialDataset):
    def __init__(self, root, category, phase="test"):
        super().__init__(root, "visa", category, phase)
