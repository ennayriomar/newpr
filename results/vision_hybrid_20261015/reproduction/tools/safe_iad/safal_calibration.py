"""Source-only logistic estimates of image prediction error, with held-out audit.

The target is correctness of an already locked image decision, not defect
presence or intervention utility. A fitted sigmoid is an estimated probability;
neither fitting nor a held-out source audit guarantees calibration on native
industrial queries. Original-image groups separate fitting from the audit.
"""
from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath

import numpy as np
from scipy.special import expit
from sklearn.linear_model import LogisticRegression
from threadpoolctl import threadpool_limits

from .research_metrics import risk_coverage


ERROR_FEATURE_NAMES = (
    'absolute_score_margin', 'support_adequacy', 'branch_disagreement', 'uncertainty',
)
SOURCE_DOMAINS = frozenset({
    'source', 'source_normal_plus_cutpaste', 'source_labeled_validation',
    'source_industrial_validation',
})
TARGET = 'prediction_error'
FORMAT_VERSION = 1


def _names(names):
    names = tuple(names)
    forbidden = {'label', 'truth', 'mask', 'query_label', 'query_mask', 'error_label',
                 'correctness', 'is_correct', 'target', 'observed_benefit'}
    if len(names) != 4 or len(set(names)) != 4 or any(not isinstance(name, str) or not name for name in names):
        raise ValueError('Calibration needs an explicit ordered four-feature schema.')
    if forbidden.intersection(names):
        raise ValueError('Labels, masks and correctness cannot be inference features.')
    return names


def _features(values, names):
    array = np.asarray(values, dtype=np.float64)
    if array.ndim == 1:
        array = array.reshape(1, -1)
    if array.ndim != 2 or array.shape[1] != len(names) or not len(array) or not np.isfinite(array).all():
        raise ValueError('Calibration features must be a nonempty finite matrix with the ordered schema.')
    if tuple(names) == ERROR_FEATURE_NAMES:
        if (array < 0).any() or (array[:, 1] > 1).any():
            raise ValueError('Margins/disagreement/uncertainty must be nonnegative; adequacy lies in [0,1].')
    return array


def _binary(labels):
    labels = np.asarray(labels)
    if labels.ndim != 1 or not len(labels) or not np.isin(labels, [0, 1]).all():
        raise ValueError('Prediction-error labels must be actual binary 0/1 events.')
    return labels.astype(np.int64)


def calibration_feature_vector(score, adequacy, disagreement, uncertainty):
    """Observable ordered inputs; the locked decision boundary is score=1."""
    vector = [abs(float(score)-1.), float(adequacy), float(disagreement), float(uncertainty)]
    return _features(vector, ERROR_FEATURE_NAMES)[0].tolist()


def _groups(values):
    output = []
    for group in values:
        if not isinstance(group, (tuple, list)) or len(group) != 3 or any(not isinstance(part, str) or not part for part in group):
            raise ValueError('Original-image groups must be dataset/category/source-ID triples.')
        output.append(tuple(group))
    if len(output) != len(set(output)):
        raise ValueError('Stored original-image group IDs must be unique.')
    return sorted(output)


@dataclass
class ErrorCalibrator:
    feature_names: tuple
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    coefficients: np.ndarray
    intercept: float
    source_domain: str
    fit_group_ids: list
    calibration_group_ids: list
    seed: int = 0
    regularization_c: float = 1.0
    target: str = TARGET

    def __post_init__(self):
        self.feature_names = _names(self.feature_names)
        for name in ['feature_mean', 'feature_scale', 'coefficients']:
            value = np.asarray(getattr(self, name), dtype=np.float64)
            if value.shape != (len(self.feature_names),) or not np.isfinite(value).all():
                raise ValueError('Invalid calibration coefficient/scaler dimensions or values.')
            setattr(self, name, value)
        self.intercept = float(self.intercept)
        self.regularization_c = float(self.regularization_c)
        if not np.isfinite([self.intercept, self.regularization_c]).all() or self.regularization_c <= 0 or (self.feature_scale <= 0).any():
            raise ValueError('Finite intercept and positive feature scales/regularization are required.')
        if self.source_domain not in SOURCE_DOMAINS or self.target != TARGET:
            raise ValueError('Calibrator must retain its source-only prediction-error event.')
        if isinstance(self.seed, bool) or not isinstance(self.seed, (int, np.integer)) or not 0 <= self.seed <= np.iinfo(np.uint32).max:
            raise ValueError('Calibration seed must be a uint32 integer.')
        self.seed = int(self.seed)
        self.fit_group_ids = _groups(self.fit_group_ids)
        self.calibration_group_ids = _groups(self.calibration_group_ids)
        if not self.fit_group_ids or not self.calibration_group_ids or set(self.fit_group_ids) & set(self.calibration_group_ids):
            raise ValueError('Nonempty fitting/audit original-image groups must be disjoint.')

    def predict(self, vectors, *, feature_names=ERROR_FEATURE_NAMES, domain='source'):
        """Estimate P(image prediction is wrong); labels never enter inference."""
        if _names(feature_names) != self.feature_names:
            raise ValueError('Calibration inference feature order differs from fitting.')
        self.prediction_metadata(domain)  # require explicit nonempty domain
        features = _features(vectors, self.feature_names)
        return expit(((features-self.feature_mean)/self.feature_scale) @ self.coefficients + self.intercept)

    def prediction_metadata(self, domain):
        if not isinstance(domain, str) or not domain:
            raise ValueError('Prediction domain must be recorded explicitly.')
        return dict(target=self.target, event='1=wrong locked-threshold image decision; 0=correct',
                    source_domain=self.source_domain, prediction_domain=domain,
                    domain_shift=domain != self.source_domain,
                    calibration_transfer_verified=False, probability_calibration_claim=False,
                    semantics='source-fitted error-probability estimate; native-domain calibration is unverified')

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = dict(format_version=FORMAT_VERSION, model_type='binary_logistic_error_calibrator',
                       feature_names=list(self.feature_names), feature_mean=self.feature_mean.tolist(),
                       feature_scale=self.feature_scale.tolist(), coefficients=self.coefficients.tolist(),
                       intercept=self.intercept, source_domain=self.source_domain, target=self.target,
                       fit_group_ids=[list(group) for group in self.fit_group_ids],
                       calibration_group_ids=[list(group) for group in self.calibration_group_ids],
                       seed=self.seed, regularization_c=self.regularization_c,
                       standardization_fit_scope='fit_rows_only', probability_calibration_claim=False)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False)+'\n')

    @classmethod
    def load(cls, path):
        payload = json.loads(Path(path).read_text())
        if (payload.get('format_version') != FORMAT_VERSION or payload.get('model_type') != 'binary_logistic_error_calibrator'
                or payload.get('standardization_fit_scope') != 'fit_rows_only' or payload.get('probability_calibration_claim') is not False):
            raise ValueError('Unsupported calibration artifact or event/provenance scope.')
        try:
            return cls(**{key:payload[key] for key in [
                'feature_names', 'feature_mean', 'feature_scale', 'coefficients', 'intercept',
                'source_domain', 'target', 'fit_group_ids', 'calibration_group_ids', 'seed', 'regularization_c',
            ]})
        except KeyError as error:
            raise ValueError('Incomplete calibration artifact.') from error


def _source_rows(rows, category_roles, role, names):
    rows = list(rows)
    if not rows:
        raise ValueError('Nonempty source fitting and held-out calibration rows are required.')
    vectors, labels, groups, domains = [], [], [], set()
    for row in rows:
        if row.get('experiment_role') != role or row.get('target') != TARGET or row.get('domain') not in SOURCE_DOMAINS:
            raise ValueError('Only the declared source role/domain and prediction-error event are eligible.')
        if (row.get('final_test_labels_used', False) or row.get('target_test_labels_used', False)
                or row.get('oracle_labels_used', False) or row.get('query_label_used_for_selection', False)
                or (role == 'meta_training' and row.get('never_use_for_training', False))):
            raise ValueError('Final/target-test or label-informed selection rows cannot fit calibration.')
        dataset, category, original = row.get('dataset'), row.get('category'), row.get('query_source_id')
        if any(not isinstance(value, str) or not value for value in [dataset, category, original]):
            raise ValueError('Source dataset/category/original-image IDs are required.')
        assigned = [key for key, categories in category_roles.get(dataset, {}).items() if category in categories]
        if assigned != ['meta_training']:
            raise ValueError('Calibration parents must be exclusively declared source meta-training categories.')
        split = row.get('native_query_source_split')
        parts = {part.lower() for part in PurePosixPath(original.replace('\\', '/')).parts}
        if (split is not None and split not in {'train', 'validation', 'source_validation'}) or parts & {'test', 'test_public', 'test_private', 'final_test'}:
            raise ValueError('Final/native-test original-image groups cannot enter source calibration.')
        if _names(row.get('feature_names', names)) != names:
            raise ValueError('Source rows have a mixed feature schema.')
        vector = _features(row.get('features'), names)
        if vector.shape != (1, len(names)):
            raise ValueError('Each calibration row requires exactly one feature vector.')
        label = _binary([row.get('error_label')])[0]
        vectors.append(vector[0]); labels.append(label)
        groups.append((dataset, category, original)); domains.add(row['domain'])
    if len(domains) != 1:
        raise ValueError('A calibration fit/audit must preserve one explicit source-domain mixture.')
    return np.stack(vectors), np.asarray(labels), sorted(set(groups)), next(iter(domains))


def error_probability_metrics(error_labels, error_probabilities, n_bins=10):
    """Brier/NLL/ECE and selective risk for actual binary error events only."""
    errors = _binary(error_labels)
    probability = np.asarray(error_probabilities, dtype=np.float64)
    if probability.shape != errors.shape or not np.isfinite(probability).all() or ((probability < 0) | (probability > 1)).any():
        raise ValueError('Error probabilities must match labels and lie in [0,1].')
    if isinstance(n_bins, bool) or not isinstance(n_bins, (int, np.integer)) or n_bins < 1:
        raise ValueError('ECE requires a positive integer bin count.')
    bins = np.minimum((probability*n_bins).astype(int), n_bins-1)
    reliability = []
    ece = 0.
    for index in range(n_bins):
        selected = bins == index
        count = int(selected.sum())
        mean_probability = float(probability[selected].mean()) if count else None
        observed_error = float(errors[selected].mean()) if count else None
        if count:
            ece += count/len(errors)*abs(mean_probability-observed_error)
        reliability.append(dict(lower=index/n_bins, upper=(index+1)/n_bins, count=count,
                                mean_error_probability=mean_probability, observed_error_rate=observed_error))
    clipped = np.clip(probability, 1e-15, 1-1e-15)
    return dict(event=TARGET, samples=len(errors), observed_error_rate=float(errors.mean()),
                brier=float(np.mean((probability-errors)**2)),
                nll=float(-np.mean(errors*np.log(clipped)+(1-errors)*np.log1p(-clipped))),
                nll_probability_clip=1e-15, ece=float(ece), ece_bins=int(n_bins),
                ece_bin_rule='equal width; [lower,upper), with probability=1 included in last bin',
                reliability_diagram=reliability, risk_coverage=risk_coverage(errors, 1-probability),
                semantics='empirical binary prediction-error metrics; no calibration guarantee')


def fit_error_calibrator(fit_rows, calibration_rows, category_roles, *, feature_names=ERROR_FEATURE_NAMES, seed=0):
    """Fit on source rows only; audit untouched original-image-disjoint rows.

    Held-out rows never fit coefficients, standardization or hyperparameters.
    Both error classes are required in fitting. A one-class audit is allowed
    but explicitly cannot evaluate both sides of calibration/error detection.
    """
    names = _names(feature_names)
    x, y, fit_groups, domain = _source_rows(fit_rows, category_roles, 'meta_training', names)
    held_x, held_y, held_groups, held_domain = _source_rows(calibration_rows, category_roles, 'source_calibration', names)
    if domain != held_domain or set(fit_groups) & set(held_groups):
        raise ValueError('Source domains must match and original-image fit/calibration groups must be disjoint.')
    if len(np.unique(y)) != 2:
        raise ValueError('Fitting requires both correct and incorrect source prediction events.')
    mean, scale = x.mean(axis=0), x.std(axis=0)
    scale[scale < 1e-12] = 1.
    with threadpool_limits(limits=1):
        fitted = LogisticRegression(C=1., solver='lbfgs', max_iter=1000, random_state=seed).fit((x-mean)/scale, y)
    model = ErrorCalibrator(names, mean, scale, fitted.coef_[0], float(fitted.intercept_[0]),
                            domain, fit_groups, held_groups, seed=seed)
    probability = model.predict(held_x, feature_names=names, domain=domain)
    report = dict(fit_rows=len(y), fit_groups=len(fit_groups), calibration_rows=len(held_y),
                  calibration_groups=len(held_groups), fit_group_ids=[list(group) for group in fit_groups],
                  calibration_group_ids=[list(group) for group in held_groups], group_overlap=0,
                  feature_names=list(names), source_domain=domain, target=TARGET,
                  fit_class_counts={str(value):int(np.count_nonzero(y == value)) for value in [0, 1]},
                  calibration_class_counts={str(value):int(np.count_nonzero(held_y == value)) for value in [0, 1]},
                  heldout_metrics=error_probability_metrics(held_y, probability),
                  heldout_has_both_error_classes=len(np.unique(held_y)) == 2,
                  standardization_fit_scope='fit_rows_only', heldout_used_for_fitting=False,
                  category_role='meta_training only; held-out rows have source_calibration experiment role',
                  event='1=wrong locked-threshold image decision; 0=correct',
                  sibling_group_isolation='dataset/category/original image; normal and synthetic siblings stay together',
                  domain_transfer_verified=False, probability_calibration_claim=False,
                  row_dependence='siblings and repeated support draws may be correlated; no independent-row confidence interval',
                  regularization_c=1., seed=int(seed))
    return model, report


def predict_error_probability(calibrator, vectors, *, feature_names=ERROR_FEATURE_NAMES, domain='source'):
    """Absent calibration produces no probability, rather than a fabricated value."""
    if calibrator is None:
        return None
    return calibrator.predict(vectors, feature_names=feature_names, domain=domain)


def probability_metrics(errors, probabilities, n_bins=10):
    """Runner alias for metrics on binary prediction-error events, not defect labels."""
    return error_probability_metrics(errors, probabilities, n_bins=n_bins)
