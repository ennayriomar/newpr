"""Normal-training feature groups for a controlled missing-support stress test.

The caller must pass verified normal *training* images from one category and
the corresponding frozen global descriptors. IDs cannot in general prove a
dataset's split (VisA's CSV defines its split), so eligibility still belongs to
the dataset loader/manifest. This module has no masks or query-label argument.
Feature clusters are proxy appearance groups, not annotated semantic modes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import PurePosixPath

import numpy as np
import sklearn
from sklearn.cluster import KMeans
from threadpoolctl import threadpool_limits

from .splits import validate_partition


def _positive_integer(value, name, minimum=1):
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < minimum:
        raise ValueError(f'{name} must be an integer >= {minimum}.')
    return int(value)


def missing_support_plan(normal_ids, normal_globals, seed, shots=1,
                         pool_size=8, queries_per_group=2, clusters=3,
                         with_control=False):
    """Return a disjoint support/pool/query plan omitting a normal feature group.

    Exactly ``shots`` supports come from outside the selected omitted group.
    Exactly ``queries_per_group`` normal queries are held back from that group,
    and the ``pool_size`` reference pool includes another image from it. All
    input features are used solely to construct this explicit stress condition;
    only selected supports/references may enter the detector memory.

    With ``with_control=True``, reserve a separate omitted-group normal and
    replace just the first support with it in ``covered_support_ids``. Both
    conditions use the same shots, queries and candidate pool. Pool and query
    images exclude the union of both support conditions. This first-position
    replacement keeps group coverage when a caller uses nested k=1/2 prefixes.

    Insufficient data or an infeasible partition raises ``ValueError``. There
    is no fallback that changes the requested shot count, pool size, or groups.
    """
    shots = _positive_integer(shots, 'shots')
    pool_size = _positive_integer(pool_size, 'pool_size')
    queries_per_group = _positive_integer(queries_per_group, 'queries_per_group')
    clusters = _positive_integer(clusters, 'clusters', minimum=2)
    seed = _positive_integer(seed, 'seed', minimum=0)
    if not isinstance(with_control, bool):
        raise ValueError('with_control must be a boolean.')
    if seed > np.iinfo(np.uint32).max:
        raise ValueError('seed must fit the uint32 random_state used by KMeans.')

    ids = list(normal_ids)
    if any(not isinstance(identifier, str) or not identifier.strip() for identifier in ids):
        raise ValueError('Normal training IDs must be nonempty strings.')
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate normal training image IDs.')
    forbidden_parts = {'test', 'test_public', 'test_private', 'validation',
                       'ground_truth', 'anomaly', 'anomalous', 'bad'}
    for identifier in ids:
        parts = {part.lower() for part in PurePosixPath(identifier.replace('\\', '/')).parts}
        if parts & forbidden_parts:
            raise ValueError('Missing-support grouping accepts normal training images only; '
                             f'forbidden split/label in ID: {identifier}')

    try:
        features = np.asarray(normal_globals, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError('Global features must be a numeric matrix.') from exc
    if features.ndim != 2 or features.shape[0] != len(ids) or features.shape[1] < 1:
        raise ValueError('Global features must have one nonempty vector per image ID.')
    if not np.isfinite(features).all():
        raise ValueError('Global features must be finite.')
    if len(ids) < max(clusters, shots + pool_size + queries_per_group + int(with_control)):
        raise ValueError('Insufficient normal training images for the requested disjoint partition.')
    norms = np.linalg.norm(features, axis=1)
    if not np.isfinite(norms).all() or np.any(norms <= 0):
        raise ValueError('Global features must have finite nonzero norms.')

    # Canonical order makes a plan independent of the input enumeration order.
    order = np.argsort(np.asarray(ids), kind='stable')
    ids = [ids[index] for index in order]
    features = np.ascontiguousarray(features[order] / norms[order, None], dtype=np.float64)
    if len(np.unique(features, axis=0)) < clusters:
        raise ValueError('Insufficient distinct global descriptors for the requested clusters.')
    kmeans = KMeans(n_clusters=clusters, random_state=seed, n_init=10, algorithm='lloyd')
    with threadpool_limits(limits=1):
        original_labels = kmeans.fit_predict(features)
    if len(set(original_labels.tolist())) != clusters:
        raise ValueError('KMeans did not produce the requested nonempty groups.')

    # The group numbers encode centroid order rather than arbitrary fit labels.
    centroid_order = sorted(range(clusters), key=lambda index: tuple(kmeans.cluster_centers_[index]))
    relabel = {old: new for new, old in enumerate(centroid_order)}
    labels = np.asarray([relabel[int(label)] for label in original_labels], dtype=np.int64)
    feasible_groups = [group for group in range(clusters)
                       if np.count_nonzero(labels == group) >= queries_per_group + 1 + int(with_control)
                       and np.count_nonzero(labels != group) >= shots]
    if not feasible_groups:
        raise ValueError('No feature group has held-out queries, an omitted-group '
                         'candidate, and sufficient supports outside it.')
    rng = np.random.default_rng(seed)
    omitted_group = int(rng.choice(feasible_groups))
    in_group = np.flatnonzero(labels == omitted_group)
    outside_group = np.flatnonzero(labels != omitted_group)
    query_indices = rng.choice(in_group, size=queries_per_group, replace=False)
    support_indices = rng.choice(outside_group, size=shots, replace=False)
    reserved = set(query_indices.tolist()) | set(support_indices.tolist())
    covered_reference = None
    if with_control:
        available = [int(index) for index in in_group if index not in reserved]
        covered_reference = int(rng.choice(available))
        reserved.add(covered_reference)
    same_group_candidates = [int(index) for index in in_group if index not in reserved]
    required_candidate = int(rng.choice(same_group_candidates))
    remaining = [index for index in range(len(ids))
                 if index not in reserved and index != required_candidate]
    if len(remaining) < pool_size - 1:
        raise ValueError('Insufficient remaining references for the declared candidate pool.')
    extra_candidates = rng.choice(remaining, size=pool_size - 1, replace=False).tolist()
    candidate_indices = [required_candidate] + extra_candidates
    candidate_indices = rng.permutation(candidate_indices).tolist()
    supports = [ids[int(index)] for index in support_indices]
    candidates = [ids[int(index)] for index in candidate_indices]
    queries = [ids[int(index)] for index in query_indices]
    validate_partition(supports, candidates, queries)

    assignments = {identifier: int(label) for identifier, label in zip(ids, labels)}
    input_digest = hashlib.sha256()
    input_digest.update(json.dumps(ids, separators=(',', ':'), ensure_ascii=False).encode())
    input_digest.update(features.astype('<f8', copy=False).tobytes())
    plan = {
        'initial_support_ids': supports,
        'candidate_ids': candidates,
        'query_ids': queries,
        'omitted_group': omitted_group,
        'cluster_assignments': assignments,
        'grouping_provenance': {
            'method': 'KMeans on L2-normalized frozen normal-training global descriptors',
            'seed': seed,
            'clusters': clusters,
            'n_init': 10,
            'algorithm': 'lloyd',
            'sklearn_version': sklearn.__version__,
            'global_feature_vectors_scanned': len(ids),
            'global_feature_dimension': features.shape[1],
            'normalized_features_and_ids_sha256': input_digest.hexdigest(),
            'group_sizes': {str(group): int(np.count_nonzero(labels == group))
                            for group in range(clusters)},
            'source_eligibility': 'caller must enforce verified-normal training membership '
                                  'with the dataset split manifest; recognizable test/label paths rejected',
            'query_role': 'held-out normal training images from the omitted feature group',
            'query_features_used_for_grouping': True,
            'query_features_enter_detector_memory': False,
            'native_test_labels_used': False,
            'limitation': 'Feature clusters are proxy appearance groups; semantic modes and '
                          'lighting conditions are not annotated or inferred as ground truth.',
        },
    }
    if with_control:
        covered_supports = [ids[covered_reference]] + supports[1:]
        validate_partition(sorted(set(supports + covered_supports)), candidates, queries)
        plan['covered_support_ids'] = covered_supports
        plan['grouping_provenance']['matched_coverage_control'] = {
            'support_reference_replaced': supports[0],
            'covered_group_reference': covered_supports[0],
            'changed_support_positions': [0],
            'support_count_per_condition': shots,
            'same_query_ids': True,
            'same_candidate_pool': True,
            'pool_excludes_union_of_support_conditions_and_queries': True,
            'coverage_in_every_nonempty_support_prefix': True,
            'semantics': 'One permitted omitted-group reference replaces an outside-group '
                         'reference at equal initial support count; proxy coverage control.',
        }
    return plan
