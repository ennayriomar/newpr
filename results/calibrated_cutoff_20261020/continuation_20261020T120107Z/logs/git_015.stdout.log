"""Offline pilot metrics; no thresholds, probabilities, or selectors are fitted.

Raw score maps are read without alteration. AU-PRO is a sampled-threshold
estimate with equal weight per connected defect component. Bootstrap inputs
are already paired policy differences, not pixels or candidate-level targets.
"""
from collections import defaultdict

import numpy as np
from scipy.ndimage import label as connected_components
from sklearn.metrics import average_precision_score, roc_auc_score


def _binary(values, name):
    array = np.asarray(values)
    if not np.isin(array, [0, 1]).all():
        raise ValueError(f'{name} must contain binary 0/1 values.')
    return array.astype(bool, copy=False)


def _scores(values, name='scores'):
    array = np.asarray(values)
    if not (np.issubdtype(array.dtype, np.integer) or np.issubdtype(array.dtype, np.floating)) or not np.isfinite(array).all():
        raise ValueError(f'{name} must contain finite numeric values.')
    return array


def _threshold(value):
    value = float(value)
    if not np.isfinite(value):
        raise ValueError('The externally selected threshold must be finite.')
    return value


def _counts(truth, prediction):
    return dict(tp=int(np.count_nonzero(truth & prediction)),
                fp=int(np.count_nonzero(~truth & prediction)),
                fn=int(np.count_nonzero(truth & ~prediction)),
                tn=int(np.count_nonzero(~truth & ~prediction)))


def _overlap(counts):
    tp, fp, fn = counts['tp'], counts['fp'], counts['fn']
    return dict(iou=tp/(tp+fp+fn) if tp+fp+fn else None,
                pixel_f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None)


def thresholded_detection_metrics(labels, scores, threshold):
    """Binary detection metrics at a caller-supplied, already locked cutoff."""
    truth = _binary(labels, 'labels').ravel()
    scores = _scores(scores).ravel()
    threshold = _threshold(threshold)
    if not len(truth) or truth.shape != scores.shape:
        raise ValueError('Nonempty labels and scores must have matching shapes.')
    counts = _counts(truth, scores >= threshold)
    tp, fp, fn, tn = (counts[key] for key in ['tp', 'fp', 'fn', 'tn'])
    return counts | dict(threshold=threshold, queries=len(truth),
                         f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,
                         missed_defect_rate=fn/(tp+fn) if tp+fn else None,
                         false_alarm_rate=fp/(fp+tn) if fp+tn else None,
                         auroc=float(roc_auc_score(truth, scores)) if truth.any() and not truth.all() else None,
                         ap=float(average_precision_score(truth, scores)) if truth.any() else None,
                         threshold_origin='externally selected; never optimized by this metric')


def _map_pairs(truths, maps):
    truths, maps = list(truths), list(maps)
    if not truths or len(truths) != len(maps):
        raise ValueError('Nonempty truth/map lists must have matching lengths.')
    pairs = []
    for truth, score in zip(truths, maps):
        truth, score = _binary(truth, 'truth mask'), _scores(score, 'score map')
        if truth.ndim != 2 or not truth.size or truth.shape != score.shape:
            raise ValueError('Each truth/map pair must be a matching nonempty 2D array.')
        pairs.append((truth, score))
    return pairs


def _au_pro(pairs, fpr_limit, max_thresholds):
    if not 0 < fpr_limit <= 1:
        raise ValueError('AU-PRO FPR integration limit must lie in (0,1].')
    if isinstance(max_thresholds, bool) or int(max_thresholds) != max_thresholds or max_thresholds < 2:
        raise ValueError('AU-PRO needs at least two sampled score thresholds.')
    region_scores = []
    normal_scores = []
    for truth, scores in pairs:
        components, count = connected_components(truth, structure=np.ones((3, 3), dtype=int))
        region_scores.extend(np.sort(scores[components == region]) for region in range(1, count+1))
        normal_scores.append(scores[~truth])
    normal = np.sort(np.concatenate(normal_scores))
    base = dict(au_pro_fpr_limit=float(fpr_limit), au_pro_num_regions=len(region_scores),
                au_pro_connectivity=8,
                au_pro_semantics='normalized area over pooled normal-pixel FPR; equal weight per connected defect region; sampled thresholds',
                au_pro_threshold_sampling='uniform ranks of distinct native scores, plus +inf/-inf endpoints')
    if not region_scores or not len(normal):
        return base | dict(au_pro=None, au_pro_curve=[], au_pro_threshold_count=0,
                           au_pro_unavailable_reason='Requires a defect component and at least one normal pixel.')
    distinct = np.unique(np.concatenate([scores.ravel() for _, scores in pairs]))
    ranks = np.unique(np.linspace(0, len(distinct)-1, min(int(max_thresholds), len(distinct))).astype(int))
    thresholds = np.r_[np.inf, distinct[ranks][::-1], -np.inf]
    fpr = np.array([(len(normal)-np.searchsorted(normal, t, side='left'))/len(normal) for t in thresholds])
    pro = np.array([np.mean([(len(region)-np.searchsorted(region, t, side='left'))/len(region)
                             for region in region_scores]) for t in thresholds])
    # Keep vertical segments at repeated FPR. Collapsing duplicate FPR to its
    # maximum PRO would incorrectly spread a late vertical jump to earlier FPR.
    stop = int(np.searchsorted(fpr, fpr_limit, side='right'))
    x, y = fpr[:stop], pro[:stop]
    clipped_thresholds = thresholds[:stop].tolist()
    if x[-1] < fpr_limit:
        right, left = stop, stop-1
        boundary = y[-1] + (pro[right]-y[-1])*(fpr_limit-x[-1])/(fpr[right]-x[-1])
        x, y = np.r_[x, fpr_limit], np.r_[y, boundary]
        clipped_thresholds.append(None)  # interpolated FPR boundary, no deployed cutoff
    curve = [dict(fpr=float(xx), pro=float(yy), threshold=float(t) if t is not None and np.isfinite(t) else None)
             for xx, yy, t in zip(x, y, clipped_thresholds)]
    return base | dict(au_pro=float(np.trapezoid(y, x)/fpr_limit), au_pro_curve=curve,
                       au_pro_threshold_count=len(thresholds),
                       au_pro_score_representation='input score-map dtype; no quantization performed')


def localization_metrics(truths, maps, threshold, fpr_limit=0.3, max_thresholds=256):
    """Pooled pixel metrics and component-weighted sampled AU-PRO.

    Thresholds for AU-PRO trace a descriptive ranking curve; they never select
    the externally locked cutoff used for IoU/pixel F1.
    """
    pairs = _map_pairs(truths, maps)
    threshold = _threshold(threshold)
    truth = np.concatenate([mask.ravel() for mask, _ in pairs])
    scores = np.concatenate([score.ravel() for _, score in pairs])
    counts = _counts(truth, scores >= threshold)
    return counts | _overlap(counts) | dict(
        pixel_auroc=float(roc_auc_score(truth, scores)) if truth.any() and not truth.all() else None,
        pixel_ap=float(average_precision_score(truth, scores)) if truth.any() else None,
        pixel_threshold=threshold, images=len(pairs), pixels=len(truth),
        overlap_aggregation='pooled pixel counts; empty union yields null',
        threshold_origin='externally selected; not optimized using evaluation masks',
    ) | _au_pro(pairs, float(fpr_limit), max_thresholds)


def defect_preservation(before, after, truth, image_before, image_after, image_threshold, pixel_threshold):
    """Offline intervention diagnostics, including explicit detected-to-missed transitions."""
    pairs = _map_pairs([truth, truth], [before, after])
    truth, before = pairs[0]
    _, after = pairs[1]
    image_before, image_after = float(image_before), float(image_after)
    if not np.isfinite([image_before, image_after]).all():
        raise ValueError('Pre/post image scores must be finite.')
    image_threshold, pixel_threshold = _threshold(image_threshold), _threshold(pixel_threshold)
    before_overlap = _overlap(_counts(truth, before >= pixel_threshold))
    after_overlap = _overlap(_counts(truth, after >= pixel_threshold))
    anomalous = bool(truth.any())
    missed_before = image_before < image_threshold if anomalous else None
    missed_after = image_after < image_threshold if anomalous else None
    transition = 'not_anomalous' if not anomalous else (
        'detected_to_missed' if not missed_before and missed_after else
        'missed_to_detected' if missed_before and not missed_after else
        'stays_missed' if missed_before else 'stays_detected')
    iou_before, iou_after = before_overlap['iou'], after_overlap['iou']
    f1_before, f1_after = before_overlap['pixel_f1'], after_overlap['pixel_f1']
    return dict(anomalous_query=anomalous, image_score_before=image_before, image_score_after=image_after,
                image_threshold=image_threshold, pixel_threshold=pixel_threshold,
                defect_region_score_before=float(before[truth].mean()) if anomalous else None,
                defect_region_score_after=float(after[truth].mean()) if anomalous else None,
                defect_region_score_drop=float(np.mean(before[truth].astype(np.float64)-after[truth])) if anomalous else None,
                defect_pixel_recall_before=float((before[truth] >= pixel_threshold).mean()) if anomalous else None,
                defect_pixel_recall_after=float((after[truth] >= pixel_threshold).mean()) if anomalous else None,
                missed_defect_before=missed_before, missed_defect_after=missed_after,
                miss_transition=transition, detected_to_missed=transition == 'detected_to_missed',
                iou_before=iou_before, iou_after=iou_after,
                iou_change=iou_after-iou_before if iou_before is not None and iou_after is not None else None,
                pixel_f1_before=f1_before, pixel_f1_after=f1_after,
                pixel_f1_change=f1_after-f1_before if f1_before is not None and f1_after is not None else None,
                semantics='Offline score/overlap/sensitivity diagnostics; lower declared loss alone does not establish defect preservation.')


def risk_coverage(errors, confidence):
    """Selective 0/1 risk using whole tied-confidence groups.

    The caller constructs errors at an already locked detector cutoff. AURC is
    the right-step integral: each coverage increment receives the risk after
    accepting its complete confidence group. No favorable order within ties.
    """
    errors = _binary(errors, 'errors').ravel()
    confidence = _scores(confidence, 'confidence').astype(np.float64).ravel()
    if not len(errors) or errors.shape != confidence.shape:
        raise ValueError('Nonempty errors/confidence arrays must have matching shapes.')
    order = np.argsort(-confidence, kind='stable')
    ranked_confidence, ranked_errors = confidence[order], errors[order]
    ends = np.r_[np.flatnonzero(ranked_confidence[1:] != ranked_confidence[:-1])+1, len(errors)]
    cumulative = np.cumsum(ranked_errors)
    curve = [dict(coverage=0., accepted=0, errors=0, risk=None, confidence_threshold=None)]
    aurc, previous = 0., 0.
    for end in ends:
        coverage, risk = float(end/len(errors)), float(cumulative[end-1]/end)
        aurc += (coverage-previous)*risk
        curve.append(dict(coverage=coverage, accepted=int(end), errors=int(cumulative[end-1]),
                          risk=risk, confidence_threshold=float(ranked_confidence[end-1])))
        previous = coverage
    return dict(aurc=float(aurc), error_detection_auroc=float(roc_auc_score(errors, -confidence)) if errors.any() and not errors.all() else None,
                curve=curve, queries=len(errors), risk_definition='mean 0/1 classification error at the caller-locked detector threshold',
                confidence_semantics='ranking input; not assumed to be a calibrated probability',
                tie_handling='accept all equal-confidence queries together',
                integration='right-step risk times each whole-group coverage increment')


def paired_crossed_bootstrap(records, value_key='paired_difference', query_key='query_id', support_key='seed',
                             n_bootstrap=2000, confidence_level=0.95, seed=0):
    """Conditional paired crossed query/support percentile bootstrap.

    One row must represent one precomputed paired policy difference for one
    query/support draw. Each dataset/category stratum must form a complete
    query x support grid. Categories are held fixed and weighted equally.
    Independent query/support multiplicities retain the entire paired value;
    pixels and candidates are never resampling units. This small-pilot interval
    does not estimate uncertainty over unsampled categories or test populations.
    """
    records = list(records)
    if not records or isinstance(n_bootstrap, bool) or int(n_bootstrap) != n_bootstrap or n_bootstrap < 1:
        raise ValueError('Nonempty records and a positive integer bootstrap count are required.')
    if not 0 < confidence_level < 1:
        raise ValueError('Confidence level must lie in (0,1).')
    grouped = defaultdict(list)
    for row in records:
        try:
            if any(row[key] is None for key in ['dataset', 'category', query_key, support_key]):
                raise ValueError('Null identifiers are not allowed.')
            group = (str(row['dataset']), str(row['category']))
            query, support, value = str(row[query_key]), str(row[support_key]), float(row[value_key])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError('Each paired row needs dataset, category, query/support IDs and finite paired difference.') from error
        if not all(group) or not query or not support or not np.isfinite(value):
            raise ValueError('Paired records require nonempty identifiers and finite differences.')
        grouped[group].append((query, support, value))
    rng = np.random.default_rng(seed)
    samples, groups, point_estimates = [], [], []
    alpha = (1-confidence_level)/2
    for (dataset, category), rows in sorted(grouped.items()):
        queries, supports = sorted({q for q, _, _ in rows}), sorted({s for _, s, _ in rows})
        q_index, s_index = {q:i for i, q in enumerate(queries)}, {s:i for i, s in enumerate(supports)}
        matrix = np.full((len(queries), len(supports)), np.nan)
        for query, support, value in rows:
            i, j = q_index[query], s_index[support]
            if np.isfinite(matrix[i, j]):
                raise ValueError('Duplicate query/support paired row; candidate or pixel rows are invalid bootstrap units.')
            matrix[i, j] = value
        if not np.isfinite(matrix).all():
            raise ValueError('Crossed bootstrap requires a complete query x support paired grid in every category.')
        q_counts = rng.multinomial(len(queries), np.full(len(queries), 1/len(queries)), size=int(n_bootstrap))
        s_counts = rng.multinomial(len(supports), np.full(len(supports), 1/len(supports)), size=int(n_bootstrap))
        draws = np.einsum('bi,ij,bj->b', q_counts, matrix, s_counts)/(len(queries)*len(supports))
        estimate = float(matrix.mean())
        interval = np.quantile(draws, [alpha, 1-alpha]).tolist()
        groups.append(dict(dataset=dataset, category=category, estimate=estimate, interval=interval,
                           unique_queries=len(queries), support_draws=len(supports), paired_rows=len(rows),
                           limited_replication=len(queries) < 5 or len(supports) < 5))
        samples.append(draws)
        point_estimates.append(estimate)
    macro = np.mean(samples, axis=0)
    return dict(estimate=float(np.mean(point_estimates)), interval=np.quantile(macro, [alpha, 1-alpha]).tolist(),
                groups=groups, n_bootstrap=int(n_bootstrap), confidence_level=float(confidence_level), seed=int(seed),
                method='paired crossed query/support percentile bootstrap',
                aggregation='equal weight across the fixed sampled dataset/category strata',
                resampling_units=[query_key, support_key], categories_resampled=False,
                scope='conditional on sampled categories and observed query/support units; descriptive pilot uncertainty, not full-benchmark generalization',
                paired_input_semantics='policy minus comparator per query/support draw; caller must preserve pairing',
                pixels_or_candidates_resampled=False)
