"""Small signed-utility regressors trained only on declared source-training rows.

Predictions are loss reductions, not probabilities or evidence of correctness.
All derivatives and support draws of one source image stay in the same CV fold.
Both feature and target standardization are fitted inside each training fold.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import numpy as np


FORMAT_VERSION = 1
PROVENANCE_KEYS = (
    'checkpoint_sha256', 'source_commit', 'preprocessing_version',
    'feature_layer_configuration', 'loss_specification',
)
HYPERPARAMETERS = {
    'ridge': {'alpha': 1.0},
    'mlp': {'hidden_units': 16, 'activation': 'tanh', 'epochs': 400,
            'learning_rate': 0.01, 'weight_decay': 0.001},
}


def _finite(array, description):
    value = np.asarray(array, dtype=np.float64)
    if not np.isfinite(value).all():
        raise ValueError(f'{description} must contain finite numbers.')
    return value


def _provenance(value):
    if not isinstance(value, dict):
        raise ValueError('Explicit checkpoint/preprocessing/loss provenance is required.')
    try:
        result = {key: value[key] for key in PROVENANCE_KEYS}
    except KeyError as exc:
        raise ValueError(f'Missing provenance field: {exc.args[0]}') from exc
    for key in PROVENANCE_KEYS[:-1]:
        if not isinstance(result[key], str) or not result[key]:
            raise ValueError(f'Invalid provenance field: {key}')
    if not isinstance(result['loss_specification'], dict) or not result['loss_specification']:
        raise ValueError('An explicit loss specification is required.')
    # Copy nested dictionaries; forbid nonportable NaN and opaque Python values.
    try:
        return json.loads(json.dumps(result, sort_keys=True, allow_nan=False))
    except (TypeError, ValueError) as exc:
        raise ValueError('Provenance must be finite JSON data.') from exc


def _feature_names(names):
    if not isinstance(names, (list, tuple)) or not names:
        raise ValueError('A nonempty ordered feature schema is required.')
    if any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names):
        raise ValueError('Feature names must be unique nonempty strings.')
    forbidden = {'query_label', 'query_mask', 'label', 'truth', 'is_correct',
                 'observed_benefit', 'offline_observed_benefit', 'loss_before', 'loss_after'}
    if forbidden.intersection(names):
        raise ValueError('Labels, masks, correctness and observed losses are not inference features.')
    if ('loo_sensitivity_imputed' in names) != ('loo_missing' in names):
        raise ValueError('Imputed LOO sensitivity requires an explicit missingness feature.')
    return list(names)


@dataclass
class BenefitModel:
    """Portable signed-U model; weights and scalers are plain JSON arrays."""

    name: str
    feature_names: list[str]
    provenance: dict[str, Any]
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    target_mean: float
    target_scale: float
    parameters: dict[str, np.ndarray]
    seed: int = 0

    def __post_init__(self):
        self.feature_names = _feature_names(self.feature_names)
        self.provenance = _provenance(self.provenance)
        dimension = len(self.feature_names)
        self.feature_mean = _finite(self.feature_mean, 'Feature means')
        self.feature_scale = _finite(self.feature_scale, 'Feature scales')
        if self.feature_mean.shape != (dimension,) or self.feature_scale.shape != (dimension,):
            raise ValueError('Scaler dimensions disagree with the feature schema.')
        if (self.feature_scale <= 0).any():
            raise ValueError('Feature scales must be positive.')
        self.target_mean = float(self.target_mean)
        self.target_scale = float(self.target_scale)
        if not np.isfinite([self.target_mean, self.target_scale]).all() or self.target_scale <= 0:
            raise ValueError('Target standardization must be finite with positive scale.')
        shapes = ({'weight': (dimension,), 'bias': ()} if self.name == 'ridge' else
                  {'weight1': (dimension, 16), 'bias1': (16,), 'weight2': (16,), 'bias2': ()}
                  if self.name == 'mlp' else None)
        if shapes is None or set(self.parameters) != set(shapes):
            raise ValueError('Unsupported benefit architecture or parameter schema.')
        self.parameters = {key: _finite(value, f'Parameter {key}') for key, value in self.parameters.items()}
        if any(self.parameters[key].shape != shape for key, shape in shapes.items()):
            raise ValueError('Benefit parameter dimensions disagree with the architecture.')

    def check_contract(self, feature_names, provenance):
        """Call at the inference boundary with the extractor's actual contract."""
        if _feature_names(feature_names) != self.feature_names or _provenance(provenance) != self.provenance:
            raise ValueError('Benefit model checkpoint/preprocessing/features/loss contract mismatch.')

    def predict(self, vectors, *, feature_names=None, provenance=None):
        if (feature_names is None) != (provenance is None):
            raise ValueError('Provide both feature names and provenance for contract checking.')
        if provenance is not None:
            self.check_contract(feature_names, provenance)
        features = _finite(vectors, 'Inference features')
        if features.ndim == 1:
            features = features.reshape(1, -1)
        if features.ndim != 2 or features.shape[1] != len(self.feature_names):
            raise ValueError('Inference features disagree with the trained schema.')
        _validate_missingness(features, self.feature_names)
        x = (features - self.feature_mean) / self.feature_scale
        p = self.parameters
        if self.name == 'ridge':
            raw = x @ p['weight'] + p['bias']
        else:
            raw = np.tanh(x @ p['weight1'] + p['bias1']) @ p['weight2'] + p['bias2']
        return _finite(raw * self.target_scale + self.target_mean, 'Predicted signed benefit')

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            'format_version': FORMAT_VERSION, 'name': self.name,
            'feature_names': self.feature_names, 'provenance': self.provenance,
            'feature_mean': self.feature_mean.tolist(), 'feature_scale': self.feature_scale.tolist(),
            'target_mean': self.target_mean, 'target_scale': self.target_scale,
            'parameters': {key: value.tolist() for key, value in self.parameters.items()},
            'seed': self.seed, 'hyperparameters': HYPERPARAMETERS[self.name],
            'semantics': 'signed reduction in the declared offline loss; not a probability',
        }
        path.write_text(json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + '\n')

    @classmethod
    def load(cls, path):
        payload = json.loads(Path(path).read_text())
        if payload.get('format_version') != FORMAT_VERSION:
            raise ValueError('Unsupported benefit model file format.')
        try:
            if payload['hyperparameters'] != HYPERPARAMETERS.get(payload['name']):
                raise ValueError('Unsupported benefit model hyperparameter contract.')
            return cls(**{key: payload[key] for key in (
                'name', 'feature_names', 'provenance', 'feature_mean', 'feature_scale',
                'target_mean', 'target_scale', 'parameters', 'seed',
            )})
        except KeyError as exc:
            raise ValueError(f'Incomplete benefit model file: {exc.args[0]}') from exc


def _validate_missingness(features, names):
    if 'loo_missing' not in names:
        return
    missing = features[:, names.index('loo_missing')]
    if not np.isin(missing, [0., 1.]).all():
        raise ValueError('LOO missingness must be an explicit binary indicator.')
    imputed = features[:, names.index('loo_sensitivity_imputed')]
    if (imputed[missing == 1] != 0).any():
        raise ValueError('Missing LOO sensitivity must use its declared zero imputation.')


def _source_rows(rows, category_roles):
    rows = list(rows)
    if not rows:
        raise ValueError('No source-training benefit rows.')
    names = _feature_names(rows[0].get('feature_names'))
    contract = _provenance(rows[0])
    groups, features, targets = [], [], []
    for row in rows:
        if row.get('experiment_role') != 'meta_training' or row.get('native_query_source_split') != 'train':
            raise ValueError('Benefit fitting accepts declared meta-training native-train sources only.')
        if (row.get('never_use_for_training', False) or row.get('final_test_labels_used') is not False
                or row.get('policy') == 'oracle' or row.get('oracle_labels_used', False)
                or row.get('query_label_used_for_selection', False)):
            raise ValueError('Evaluation, final-label or oracle rows cannot train benefit models.')
        dataset, category = row.get('dataset'), row.get('category')
        roles = category_roles.get(dataset, {})
        assigned = [role for role, categories in roles.items() if category in categories]
        if assigned != ['meta_training']:
            raise ValueError('Benefit source categories must be exclusively meta-training.')
        if _feature_names(row.get('feature_names')) != names or _provenance(row) != contract:
            raise ValueError('Training rows have mixed checkpoint/preprocessing/features/loss contracts.')
        source = row.get('query_source_id')
        if not isinstance(source, str) or not source:
            raise ValueError('Source image ID is required for derivative-safe grouped CV.')
        if row.get('native_query_source_label', 'normal') != 'normal':
            raise ValueError('Benefit query origins must be source-training normal images.')
        kind = row.get('query_kind', '')
        if kind == 'real_normal_training_query':
            if row.get('query_id') != source:
                raise ValueError('Normal query must match its source image ID.')
        elif isinstance(kind, str) and kind.startswith('synthetic_'):
            synthetic = row.get('synthetic_provenance')
            if not isinstance(synthetic, dict) or synthetic.get('source_image_id') != source:
                raise ValueError('Synthetic derivative must declare its matching source image.')
        else:
            raise ValueError('Only real normal or documented synthetic source-training queries are allowed.')
        if source in row.get('support_ids', []) or source in row.get('candidate_pool_ids', []):
            raise ValueError('Source query overlaps its support/candidate memory.')
        if row.get('candidate_id') == source:
            raise ValueError('Source query cannot be its own candidate reference.')
        vector = _finite(row.get('features'), 'Training features')
        if vector.shape != (len(names),):
            raise ValueError('Training feature vector length disagrees with its schema.')
        _validate_missingness(vector.reshape(1, -1), names)
        if 'loo_missing' in names:
            missing = int(vector[names.index('loo_missing')])
            if ('loo_defined' in row and row['loo_defined'] != (missing == 0)) or (
                    'loo_missing_indicator' in row and row['loo_missing_indicator'] != missing):
                raise ValueError('LOO metadata disagrees with its missingness feature.')
        target = _finite(row.get('observed_benefit'), 'Observed signed benefit')
        if target.shape != ():
            raise ValueError('Observed benefit must be a scalar.')
        groups.append(json.dumps([dataset, category, source], separators=(',', ':')))
        features.append(vector)
        targets.append(float(target))
    return rows, np.stack(features), np.asarray(targets), np.asarray(groups), names, contract


def _fit(name, features, targets, names, provenance, seed):
    mean = features.mean(axis=0)
    scale = features.std(axis=0)
    scale[scale < 1e-12] = 1.
    target_mean = float(targets.mean())
    target_scale = max(float(targets.std()), 1e-12)
    if target_scale == 1e-12:
        target_scale = 1.
    x, y = (features - mean) / scale, (targets - target_mean) / target_scale
    if name == 'ridge':
        alpha = HYPERPARAMETERS[name]['alpha']
        parameters = {'weight': np.linalg.solve(x.T @ x + alpha * np.eye(x.shape[1]), x.T @ y),
                      'bias': np.asarray(0.)}
    else:
        rng = np.random.default_rng(seed)
        parameters = {'weight1': rng.normal(0, 1 / np.sqrt(x.shape[1]), (x.shape[1], 16)),
                      'bias1': np.zeros(16), 'weight2': rng.normal(0, 0.1, 16), 'bias2': np.asarray(0.)}
        first = {key: np.zeros_like(value) for key, value in parameters.items()}
        second = {key: np.zeros_like(value) for key, value in parameters.items()}
        hp = HYPERPARAMETERS[name]
        for step in range(1, hp['epochs'] + 1):
            hidden = np.tanh(x @ parameters['weight1'] + parameters['bias1'])
            derivative = 2 * (hidden @ parameters['weight2'] + parameters['bias2'] - y) / len(y)
            hidden_derivative = derivative[:, None] * parameters['weight2'] * (1 - hidden ** 2)
            gradients = {'weight2': hidden.T @ derivative + hp['weight_decay'] * parameters['weight2'],
                         'bias2': np.asarray(derivative.sum()),
                         'weight1': x.T @ hidden_derivative + hp['weight_decay'] * parameters['weight1'],
                         'bias1': hidden_derivative.sum(axis=0)}
            for key in parameters:
                first[key] = .9 * first[key] + .1 * gradients[key]
                second[key] = .999 * second[key] + .001 * gradients[key] ** 2
                parameters[key] -= hp['learning_rate'] * (first[key] / (1 - .9 ** step)) / (
                    np.sqrt(second[key] / (1 - .999 ** step)) + 1e-8)
    return BenefitModel(name, names, provenance, mean, scale, target_mean, target_scale, parameters, seed)


def fit_benefit_models(rows, category_roles, seed=0):
    """Fit ridge/MLP; select the primary via source-image-grouped OOF MSE.

    Fixed hyperparameters and a maximum of three folds keep this feasibility
    model small. Group-balanced MSE counts each source image once. The source
    CV is not category-disjoint validation and does not justify calibration.
    """
    rows, x, y, groups, names, provenance = _source_rows(rows, category_roles)
    unique = np.unique(groups)
    if len(unique) < 2:
        raise ValueError('At least two independent source images are required for grouped CV.')
    ordering = np.random.default_rng(seed).permutation(unique)
    folds = np.array_split(ordering, min(3, len(unique)))
    oof = {name: np.empty(len(rows), dtype=np.float64) for name in HYPERPARAMETERS}
    fold_reports = []
    for index, held_out in enumerate(folds):
        validation = np.isin(groups, held_out)
        train = ~validation
        fold_reports.append({'fold': index, 'train_source_groups': sorted(set(groups[train])),
                             'held_out_source_groups': sorted(set(groups[validation])),
                             'training_rows': int(train.sum()), 'held_out_rows': int(validation.sum())})
        for name in HYPERPARAMETERS:
            model = _fit(name, x[train], y[train], names, provenance, int(seed) + index)
            oof[name][validation] = model.predict(x[validation])
    scores = {name: float(np.mean([np.mean((prediction[groups == group] - y[groups == group]) ** 2)
                                  for group in unique])) for name, prediction in oof.items()}
    primary = min(scores, key=lambda name: (scores[name], name != 'ridge'))
    models = {name: _fit(name, x, y, names, provenance, int(seed)) for name in HYPERPARAMETERS}
    constant = [name for name, spread in zip(names, np.ptp(x, axis=0)) if spread < 1e-12]
    negative_groups = sorted(set(groups[y < -1e-8]))
    report = {
        'primary_model': primary, 'model_selection_role': 'source_training_grouped_cv_only',
        'source_target_rows': len(rows), 'unique_source_groups': len(unique),
        'source_categories': sorted({f"{row['dataset']}:{row['category']}" for row in rows}),
        'positive_targets': int((y > 1e-8).sum()), 'negative_targets': int((y < -1e-8).sum()),
        'unique_negative_source_groups': len(negative_groups), 'negative_source_groups': negative_groups,
        'constant_columns': constant, 'feature_names': names, 'provenance': provenance,
        'seed': int(seed), 'hyperparameters': HYPERPARAMETERS,
        'grouped_cv': {'unit': 'dataset/category/original source image; all derivatives and support draws together',
                       'folds': fold_reports, 'source_group_balanced_mse': scores,
                       'oof_predictions': {name: prediction.tolist() for name, prediction in oof.items()},
                       'oof_source_groups': groups.tolist(), 'observed_benefits': y.tolist(),
                       'standardization': 'feature and target statistics fitted on each training fold only'},
        'final_test_labels_used': False, 'validation_labels_used_for_model_selection': False,
        'calibration_labels_used': False, 'prediction_semantics': 'signed loss benefit, not a probability',
        'limitations': ['Source-image grouped CV is not held-out-category evidence.',
                        'Rows sharing support memories can remain dependent across source groups.',
                        'Sparse harmful-source groups cannot support calibrated harmful-event probabilities.'],
    }
    return models, report
