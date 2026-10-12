"""Deployment-time one-reference selectors: features and IDs only, no labels."""
from dataclasses import dataclass
import hashlib

import numpy as np
import torch
import torch.nn.functional as F


@dataclass(frozen=True, slots=True)
class InferenceInputs:
    query_global: torch.Tensor
    support_globals: torch.Tensor
    candidate_globals: torch.Tensor
    candidate_ids: tuple[str, ...]
    seed: int
    query_id: str


def global_descriptor(patches):
    return F.normalize(F.normalize(patches, dim=1).mean(dim=0), dim=0)


def select_reference(policy, inputs, *, budget):
    if budget not in {0, 1}:
        raise ValueError('This validated milestone supports one-step budgets 0/1 only.')
    if policy=='none':
        return None
    if budget != 1 or not inputs.candidate_ids:
        raise ValueError('Acquisition requires budget 1 and a nonempty candidate pool.')
    if len(set(inputs.candidate_ids)) != len(inputs.candidate_ids):
        raise ValueError('Candidate IDs must be unique.')
    if len(inputs.candidate_globals) != len(inputs.candidate_ids):
        raise ValueError('Candidate features/IDs mismatch.')
    if policy=='random':
        seed = int.from_bytes(hashlib.sha256(f'{inputs.seed}:{inputs.query_id}'.encode()).digest()[:8], 'little')
        return int(np.random.default_rng(seed).integers(len(inputs.candidate_ids)))
    if policy=='nearest_global':
        return int(((inputs.candidate_globals-inputs.query_global)**2).sum(dim=1).argmin())
    if policy=='diversity':
        distance = torch.cdist(inputs.candidate_globals, inputs.support_globals).min(dim=1).values
        return int(distance.argmax())
    raise ValueError('Unknown deployment policy. Oracle selection belongs only in offline evaluation.')


def add_reference(support_ids, candidate_id, *, budget):
    if budget != 1 or candidate_id in support_ids:
        raise ValueError('Invalid one-step acquisition or repeated reference.')
    return list(support_ids)+[candidate_id]
