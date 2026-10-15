"""Observable diagnostics and offline losses; no adequacy score suppresses evidence."""
import numpy as np
import torch
import torch.nn.functional as F

from .acquisition import global_descriptor
from .patch_nn import patch_nearest_neighbor


FEATURE_NAMES = ['nn_mean','nn_std','nn_max','top_one_percent','knn_mean','knn_std','distinct_reference_mean','dispersion_mean','dispersion_std','loo_sensitivity_imputed','loo_missing','global_support_distance','candidate_query_global_distance','candidate_support_global_distance','candidate_nn_mean','candidate_nn_std','candidate_nn_max','score_drop_mean','score_drop_max']


def support_diagnostics(query, references):
    if not references:
        raise ValueError('Empty reference memory.')
    memory = torch.cat(references)
    q,m = F.normalize(query,dim=1),F.normalize(memory,dim=1)
    distance = (2-2*(q@m.T)).clamp_min(0).sqrt()
    nearest, indices = distance.topk(min(5,len(memory)),dim=1,largest=False)
    reference_index = torch.cat([torch.full((len(ref),),i,dtype=torch.long) for i,ref in enumerate(references)])
    contributors = reference_index[indices].sort(dim=1).values
    distinct = 1+(contributors[:,1:]!=contributors[:,:-1]).sum(dim=1)
    neighbors=m[indices]
    dispersion=((neighbors-neighbors.mean(dim=1,keepdim=True))**2).sum(dim=2).mean(dim=1)
    defect=patch_nearest_neighbor(query,memory)
    if len(references)==1:
        loo=None
        valid=torch.zeros(len(query),dtype=torch.bool)
    else:
        leave_out=torch.stack([distance[:,reference_index!=i].min(dim=1).values for i in range(len(references))])
        loo=(leave_out-defect).abs().max(dim=0).values
        valid=torch.ones(len(query),dtype=torch.bool)
    globals=torch.stack([global_descriptor(ref) for ref in references])
    global_distance=torch.linalg.vector_norm(globals-global_descriptor(query),dim=1).min()
    return {'nearest_distance':defect,'mean_five_nearest':nearest.mean(dim=1),'distinct_reference_count':distinct,'dispersion_trace':dispersion,'loo_sensitivity':loo,'loo_valid':valid,'global_support_distance':global_distance,'global_local_disagreement':(defect-global_distance).abs()}


def inference_feature_vector(query, references, candidate, diagnostics, after_scores):
    nn=diagnostics['nearest_distance']
    candidate_nn=patch_nearest_neighbor(query,candidate)
    candidate_global=global_descriptor(candidate)
    support_globals=torch.stack([global_descriptor(ref) for ref in references])
    loo=diagnostics['loo_sensitivity']
    values=[nn.mean(),nn.std(unbiased=False),nn.max(),torch.topk(nn,max(1,int(np.ceil(len(nn)*.01)))).values.mean(),diagnostics['mean_five_nearest'].mean(),diagnostics['mean_five_nearest'].std(unbiased=False),diagnostics['distinct_reference_count'].float().mean(),diagnostics['dispersion_trace'].mean(),diagnostics['dispersion_trace'].std(unbiased=False),loo.mean() if loo is not None else torch.tensor(0.),torch.tensor(float(loo is None)),diagnostics['global_support_distance'],torch.linalg.vector_norm(candidate_global-global_descriptor(query)),torch.linalg.vector_norm(support_globals-candidate_global,dim=1).min(),candidate_nn.mean(),candidate_nn.std(unbiased=False),candidate_nn.max(),(nn-after_scores).mean(),(nn-after_scores).max()]
    return [float(value) for value in values]


def offline_loss(score_map, truth, specification, *, image_score=None):
    if score_map.shape != truth.shape:
        raise ValueError('Prediction/truth dimensions differ.')
    margin=float(specification['margin'])
    if margin<=0:
        raise ValueError('Loss margin must be positive.')
    positive=np.asarray(truth,dtype=bool)
    if specification['type']=='image_margin_mse':
        if image_score is None:
            raise ValueError('Image-level loss requires the detector image score, not a new aggregation.')
        return float(max(0,margin-float(image_score))**2 if positive.any() else float(image_score)**2)
    if specification['type']!='balanced_pixel_margin_mse':
        raise ValueError('Unsupported predeclared offline loss.')
    negative=~positive
    normal_loss=float(np.square(score_map[negative]).mean()) if negative.any() else 0.
    if not positive.any():
        return normal_loss
    defect_loss=float(np.square(np.maximum(0,margin-score_map[positive])).mean())
    return (normal_loss+defect_loss)/2 if negative.any() else defect_loss


def evaluation_oracle(observed_benefits):
    """Unattainable label-informed best *forced* one-reference intervention.

    It is not an AUROC oracle and never supplies training or tuning decisions.
    """
    values=np.asarray(observed_benefits)
    if values.ndim!=1 or not len(values) or not np.isfinite(values).all():
        raise ValueError('Oracle requires finite offline candidate benefits.')
    return int(values.argmax())
