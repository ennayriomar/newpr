"""Offline metrics and calibration; test F1-Max never supplies a decision cutoff."""
import numpy as np
from sklearn.metrics import average_precision_score, precision_recall_curve, roc_auc_score


def finite_arrays(truth, scores):
    truth, scores = np.asarray(truth, dtype=bool).ravel(), np.asarray(scores, dtype=np.float64).ravel()
    if truth.shape != scores.shape or not len(truth) or not np.isfinite(scores).all():
        raise ValueError('Metric inputs must have matching finite, nonempty arrays.')
    return truth, scores


def best_f1(truth, scores):
    truth, scores = finite_arrays(truth, scores)
    if not truth.any():
        return None, None
    precision, recall, thresholds = precision_recall_curve(truth, scores)
    f1 = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-15)
    index = int(np.argmax(f1))
    return float(f1[index]), float(thresholds[index])


def metrics(truth, scores, locked_threshold):
    truth, scores = finite_arrays(truth, scores)
    pred = scores >= locked_threshold
    tp, fp, fn = (int(np.count_nonzero(x)) for x in (pred & truth, pred & ~truth, ~pred & truth))
    max_f1, _ = best_f1(truth, scores)
    return dict(auroc=float(roc_auc_score(truth, scores)) if truth.any() and not truth.all() else None,
                ap=float(average_precision_score(truth, scores)) if truth.any() else None,
                f1_max_offline=max_f1, locked_f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,
                locked_threshold=float(locked_threshold), tp=tp, fp=fp, fn=fn,
                f1_max_semantics='test-set diagnostic only; maximizing threshold is neither exported nor used for decisions')


def calibrate(image_truth, image_scores, pixel_truth, pixel_scores, normal_only=False):
    if normal_only:
        if np.asarray(image_truth).any() or np.asarray(pixel_truth).any():
            raise ValueError('AD2 normal-only calibration received anomaly labels.')
        # MVTec's utility suggests mean+3std on normal validation scores.
        return dict(image_threshold=float(np.mean(image_scores)+3*np.std(image_scores)),
                    pixel_threshold=float(np.mean(pixel_scores)+3*np.std(pixel_scores)),
                    procedure='normal-only validation mean+3std; no guaranteed false-alarm rate')
    _, image_threshold = best_f1(image_truth, image_scores)
    _, pixel_threshold = best_f1(pixel_truth, pixel_scores)
    if image_threshold is None or pixel_threshold is None:
        raise ValueError('Supervised calibration requires positive examples, from calibration roles only.')
    return dict(image_threshold=image_threshold, pixel_threshold=pixel_threshold,
                procedure='empirical F1 cutoff on reserved calibration-category queries only; not probability calibration')


def adequacy_precision_curve(mean_adequacy, image_truth, image_scores, locked_threshold):
    a = np.asarray(mean_adequacy)
    if not np.isfinite(a).all() or ((a < 0) | (a > 1)).any():
        raise ValueError('Adequacy diagnostic outside [0,1].')
    correct = (np.asarray(image_scores) >= locked_threshold) == np.asarray(image_truth, dtype=bool)
    rows = []
    for threshold in sorted(set([0., 1., *a.tolist()])):
        selected = a >= threshold
        rows.append(dict(adequacy_threshold=float(threshold), coverage=float(selected.mean()), accepted=int(selected.sum()),
                         precision_correct_decision=float(correct[selected].mean()) if selected.any() else None))
    return dict(event='image decision correct at locked calibration cutoff; empirical correctness proxy, NOT ground-truth support adequacy', curve=rows)


class PixelHistogram:
    """Exact ranking metrics for all pixels AFTER explicit float16 quantization.

    Positive finite float16 bit patterns are monotonically ordered. Two 65536
    count arrays bound memory independently of image count/resolution. This is
    NOT called an exact metric for the original float32 anomaly maps.
    """
    def __init__(self):
        self.positive = np.zeros(65536, dtype=np.int64)
        self.negative = np.zeros(65536, dtype=np.int64)

    def update(self, truth, scores):
        truth, scores = finite_arrays(truth, scores)
        if (scores < 0).any() or (scores > np.finfo(np.float16).max).any():
            raise ValueError('Histogram scores must be nonnegative finite float16 values.')
        values = scores.astype(np.float16)
        values[values == 0] = 0  # normalize negative zero
        keys = values.view(np.uint16)
        self.positive += np.bincount(keys[truth], minlength=65536)
        self.negative += np.bincount(keys[~truth], minlength=65536)

    def curves(self):
        used = np.flatnonzero(self.positive+self.negative)[::-1]
        thresholds = used.astype(np.uint16).view(np.float16).astype(np.float64)
        tp, fp = np.cumsum(self.positive[used]), np.cumsum(self.negative[used])
        return thresholds, tp, fp

    def best_threshold(self):
        thresholds, tp, fp = self.curves()
        total_positive = int(self.positive.sum())
        if not total_positive:
            raise ValueError('Positive calibration pixels required for supervised cutoff.')
        f1 = 2*tp/np.maximum(tp+fp+total_positive, 1)
        return float(thresholds[np.flatnonzero(f1 == f1.max())[-1]])

    def normal_threshold(self):
        if self.positive.sum():
            raise ValueError('Normal-only calibration histogram contains defect pixels.')
        ids = np.flatnonzero(self.negative)
        scores = ids.astype(np.uint16).view(np.float16).astype(np.float64)
        count = self.negative[ids]
        mean = float(np.average(scores, weights=count))
        variance = float(np.average((scores-mean)**2, weights=count))
        return mean+3*np.sqrt(variance)

    def metrics(self, threshold):
        thresholds, tp, fp = self.curves()
        pos, neg = int(self.positive.sum()), int(self.negative.sum())
        recall = tp/pos if pos else np.zeros_like(tp, dtype=float)
        fpr = fp/neg if neg else np.zeros_like(fp, dtype=float)
        precision = tp/np.maximum(tp+fp, 1)
        auroc = float(np.trapezoid(np.r_[0., recall], np.r_[0., fpr])) if pos and neg else None
        ap = float(np.sum(np.diff(np.r_[0., recall])*precision)) if pos else None
        f1 = 2*tp/np.maximum(tp+fp+pos, 1)
        accepted = thresholds >= threshold
        last = int(np.flatnonzero(accepted)[-1]) if accepted.any() else None
        ntp, nfp = (int(tp[last]), int(fp[last])) if last is not None else (0,0)
        nfn = pos-ntp
        return dict(auroc=auroc, ap=ap, f1_max_offline=float(f1.max()) if pos else None,
                    locked_f1=2*ntp/(2*ntp+nfp+nfn) if 2*ntp+nfp+nfn else None,
                    locked_threshold=float(threshold), tp=ntp, fp=nfp, fn=nfn,
                    representation='all native pixels quantized to float16; exact for quantized scores, not original float32',
                    f1_max_semantics='test diagnostic; its maximizing cutoff is not deployed')
