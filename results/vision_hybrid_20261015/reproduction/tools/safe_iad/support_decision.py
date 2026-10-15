"""Configurable empirical diagnostics; raw detector evidence is always separate."""
import numpy as np
import torch


DEFAULT_SIGMOID = {
    'kind':'sigmoid','bias':1.5,'nearest_distance':-2.0,'mean_five_nearest':-1.0,
    'distinct_reference_count':0.5,'dispersion_trace':0.0,'loo_sensitivity':-2.0,
    'global_local_disagreement':-0.25,'loo_missing_bias':0.0,
    'adequacy_threshold':0.5,
    'semantics':'predeclared empirical diagnostic; no support-adequacy ground truth or probability fit',
}


def adequacy_field(diagnostics, specification=None):
    specification=specification or DEFAULT_SIGMOID
    kind=specification['kind']
    if kind in {'none','diagnostics_only'}:
        return None
    if kind!='sigmoid':
        raise ValueError('Only predeclared sigmoid or raw diagnostic ablations are fitted in M3; learned adequacy needs its own justified event')
    nearest=diagnostics['nearest_distance']
    logit=torch.full_like(nearest,float(specification['bias']))
    for key in ['nearest_distance','mean_five_nearest','dispersion_trace','global_local_disagreement']:
        logit=logit+float(specification[key])*diagnostics[key]
    logit=logit+float(specification['distinct_reference_count'])*(diagnostics['distinct_reference_count'].float()-1)
    sensitivity=diagnostics['loo_sensitivity']
    if sensitivity is None:
        if diagnostics['loo_valid'].any():
            raise ValueError('Missing LOO sensitivity cannot be marked valid')
        logit=logit+float(specification['loo_missing_bias'])
    else:
        logit=logit+float(specification['loo_sensitivity'])*sensitivity
    field=torch.sigmoid(logit)
    if not torch.isfinite(field).all() or not ((field>=0)&(field<=1)).all():
        raise ValueError('Invalid empirical adequacy field')
    return field


def action(image_score, adequacy, image_threshold, adequacy_threshold=0.5):
    if not np.isfinite(image_score) or not np.isfinite(image_threshold):
        raise ValueError('Finite locked detector cutoff required')
    evidence=image_score>=image_threshold
    if adequacy is not None and (not 0<=adequacy<=1):
        raise ValueError('Diagnostic adequacy must lie in [0,1]')
    if adequacy is not None and adequacy<adequacy_threshold:
        return 'unresolved/reference-insufficient',bool(evidence)
    return ('defective' if evidence else 'normal'),bool(evidence)
