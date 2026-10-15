"""Normal-only local subspaces and a nonnegative correction to patch search.

This is an experimental independent implementation. The residual-ratio gate is
a heuristic, not a probability. A zero correction is the unchanged search
control. Any gate/strength choice belongs exclusively to development data.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import sklearn
from sklearn.cluster import MiniBatchKMeans
from threadpoolctl import threadpool_limits
import torch
import torch.nn.functional as F

from .vision_hybrid_features import SLOTS, metric_map, image_score


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def array_hash(value):
    a=np.asarray(value)
    return hashlib.sha256(canonical({'shape':list(a.shape),'dtype':str(a.dtype)}).encode()+a.tobytes()).hexdigest()


def source_hashes():
    root=Path(__file__).parent
    return {name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in
            ['vision_hybrid_model.py','vision_hybrid_features.py','safal_features.py']}


def features(value):
    x=torch.as_tensor(value).detach().cpu().to(torch.float64).contiguous()
    if x.ndim!=2 or min(x.shape)<2 or not torch.isfinite(x).all() or torch.any(torch.linalg.vector_norm(x,dim=1)==0):
        raise ValueError('Finite nonzero patch descriptors with shape [tokens,channels] required.')
    return x


@dataclass(frozen=True)
class HybridParameters:
    clusters: int=1
    variance: float=.99
    strength: float=0.
    gate: str='uniform'

    def __post_init__(self):
        if type(self.clusters) is not int or self.clusters<1:
            raise ValueError('Positive integer cluster count required.')
        if isinstance(self.variance,bool) or not math.isfinite(self.variance) or not 0<self.variance<=1:
            raise ValueError('Variance must be finite in (0,1].')
        if isinstance(self.strength,bool) or not math.isfinite(self.strength) or self.strength<0:
            raise ValueError('Correction strength must be finite and nonnegative.')
        if self.gate not in ('uniform','residual_ratio'):
            raise ValueError('Unknown declared gate.')
        if self.strength==0 and (self.clusters!=1 or self.variance!=.99 or self.gate!='uniform'):
            raise ValueError('Use the canonical zero-correction baseline parameters.')

    @property
    def id(self):return hashlib.sha256(canonical(asdict(self)).encode()).hexdigest()


def parameter_grid():
    return [HybridParameters()]+[HybridParameters(k,v,w,g) for k in (1,4)
                                for v in (.95,.99) for w in (.1,.25,.5)
                                for g in ('uniform','residual_ratio')]


class LocalSubspaces:
    def __init__(self, support, clusters, variances=(.95,.99), seed=20261015, threads=3):
        x=features(support)
        if type(clusters) is not int or clusters<1 or len(x)<2*clusters:
            raise ValueError('Too few support patches for requested subspaces.')
        self.clusters,self.variances=clusters,tuple(variances)
        if not self.variances or any(isinstance(v,bool) or not math.isfinite(v) or not 0<v<=1 for v in self.variances):
            raise ValueError('Invalid variance grid.')
        unit=F.normalize(x,dim=1)
        with threadpool_limits(limits=threads):
            if clusters==1:self.centers=unit.mean(0,keepdim=True)
            else:
                km=MiniBatchKMeans(n_clusters=clusters,n_init=3,batch_size=1024,max_iter=50,
                                  random_state=seed,reassignment_ratio=0.)
                km.fit(unit.float().numpy())
                self.centers=torch.from_numpy(km.cluster_centers_.copy()).double()
        assignments=self.assign(x)
        self.groups=[]
        for group in range(clusters):
            rows=x[assignments==group]
            if len(rows)<2:raise ValueError('A fitted subspace has fewer than two patches.')
            mean=rows.mean(0);centered=rows-mean
            energy=float(centered.square().sum()/len(rows))
            if not math.isfinite(energy) or energy<=0:
                raise ValueError('Degenerate normal subspace; no hidden epsilon scale.')
            covariance=centered.T@centered/len(rows)
            eigenvalues,vectors=torch.linalg.eigh(covariance)
            eigenvalues=eigenvalues.flip(0).clamp_min(0);vectors=vectors.flip(1).T
            tolerance=float(eigenvalues[0])*max(rows.shape)*torch.finfo(torch.float64).eps
            rank=int((eigenvalues>tolerance).sum())
            if rank==0:raise ValueError('Normal covariance has zero numerical rank.')
            cumulative=eigenvalues[:rank].cumsum(0)/eigenvalues[:rank].sum()
            ranks={str(v):min(rank,int(torch.searchsorted(cumulative,torch.tensor(v,dtype=torch.float64)))+1)
                   for v in self.variances}
            self.groups.append(dict(mean=mean,basis=vectors[:max(ranks.values())].contiguous(),
                                    energy=energy,ranks=ranks,count=len(rows),numerical_rank=rank))

    def assign(self,x):
        unit=F.normalize(features(x),dim=1)
        return torch.cdist(unit,self.centers).argmin(1)

    def score(self,query):
        query=features(query);assignments=self.assign(query)
        values={str(v):torch.empty(len(query),dtype=torch.float64) for v in self.variances}
        for i,group in enumerate(self.groups):
            indices=assignments==i
            if not indices.any():continue
            centered=query[indices]-group['mean']
            for v in self.variances:
                basis=group['basis'][:group['ranks'][str(v)]]
                residual=centered-(centered@basis.T)@basis
                values[str(v)][indices]=residual.square().sum(1)/group['energy']
        if any(not torch.isfinite(v).all() or (v<0).any() for v in values.values()):
            raise ValueError('Invalid relative reconstruction residual.')
        return values

    def metadata(self):
        return dict(clusters=self.clusters,variances=list(self.variances),
                    group_counts=[g['count'] for g in self.groups],
                    numerical_ranks=[g['numerical_rank'] for g in self.groups],
                    retained_ranks=[g['ranks'] for g in self.groups],
                    energy_scales=[g['energy'] for g in self.groups],
                    normalization='Residual squared norm / mean total centered normal feature energy in assigned cluster',
                    independent_original_images_not_patch_count=True)


def fuse_raw(raw,params,grid):
    if not isinstance(params,HybridParameters):raise ValueError('Validated parameters required.')
    combined=torch.zeros(grid*grid,dtype=torch.float64)
    residual_total=torch.zeros_like(combined)
    for slot in SLOTS:
        search=torch.as_tensor(raw['search'][slot],dtype=torch.float64).flatten()
        if search.numel()!=grid*grid or not torch.isfinite(search).all() or (search<0).any():
            raise ValueError('Finite nonnegative aligned patch search scores required.')
        if params.strength==0:
            residual=torch.zeros_like(search);correction=residual
        else:
            residual=torch.as_tensor(raw['residual'][str(params.clusters)][str(params.variance)][slot],dtype=torch.float64).flatten()
            if residual.shape!=search.shape or not torch.isfinite(residual).all() or (residual<0).any():
                raise ValueError('Finite nonnegative aligned residuals required.')
            if params.gate=='uniform':gate=torch.ones_like(search)
            else:
                denominator=residual+search
                gate=torch.where(denominator>0,residual/torch.where(denominator>0,denominator,torch.ones_like(denominator)),torch.zeros_like(denominator))
            correction=params.strength*gate*residual
        value=search+correction
        if slot=='vflip':
            value=value.reshape(grid,grid).flip(0).flatten()
            residual=residual.reshape(grid,grid).flip(0).flatten()
        combined+=value;residual_total+=residual
    score_map=metric_map(combined,grid)
    return dict(image_score=image_score(score_map),map=score_map,
                raw_sum=combined,relative_residual_sum=residual_total,
                parameters_id=params.id,probabilities=False)


class VisionHybrid:
    def __init__(self,support_features,slot_indices,support_ids,*,clusters=(1,4),variances=(.95,.99),threads=3):
        self.support_ids=tuple(support_ids)
        if not self.support_ids or len(set(self.support_ids))!=len(self.support_ids) or any(not isinstance(i,str) or not i for i in self.support_ids):
            raise ValueError('Unique original support IDs required.')
        self.support_features=[features(x).float() for x in support_features]
        if not self.support_features:raise ValueError('Support descriptors are required.')
        self.grid=math.isqrt(len(self.support_features[0]))
        shape=self.support_features[0].shape
        if self.grid*self.grid!=shape[0] or any(x.shape!=shape for x in self.support_features):
            raise ValueError('Every view must use the same square descriptor grid/dimension.')
        self.slot_indices={slot:list(slot_indices[slot]) for slot in SLOTS}
        for indices in self.slot_indices.values():
            if len(indices)!=6*len(self.support_ids) or any(type(i) is not int or not 0<=i<len(self.support_features) for i in indices):
                raise ValueError('Six support views per original image and slot required.')
        self.memory={slot:F.normalize(torch.cat([self.support_features[i] for i in indices]),dim=1)
                     for slot,indices in self.slot_indices.items()}
        pooled=torch.cat(self.support_features)
        self.clusters,self.variances,self.threads=tuple(clusters),tuple(variances),threads
        if len(set(self.clusters))!=len(self.clusters):raise ValueError('Duplicate cluster settings.')
        self.subspaces={str(k):LocalSubspaces(pooled,k,self.variances,threads=threads) for k in self.clusters}
        self.params=None;self.threshold=None;self.provenance={}

    def raw(self,query):
        raw={'search':{},'residual':{str(k):{str(v):{} for v in self.variances} for k in self.clusters}}
        for slot in SLOTS:
            x=features(query[slot]).float()
            if x.shape!=self.support_features[0].shape:raise ValueError('Query feature geometry differs from support.')
            unit=F.normalize(x,dim=1)
            # Identical cosine-NN mathematics; chunking bounds temporary RAM.
            search=torch.cat([(1-(part@self.memory[slot].T).max(1).values).clamp_min(0)
                              for part in unit.split(128)])
            raw['search'][slot]=search.double()
            for k,subspace in self.subspaces.items():
                for v,values in subspace.score(x).items():raw['residual'][k][v][slot]=values
        return raw

    def predict(self,query,params=None):
        params=params or self.params
        if params is None:raise ValueError('Selected parameters required.')
        return fuse_raw(self.raw(query),params,self.grid)

    def metadata(self):
        return dict(support_ids=list(self.support_ids),original_support_images=len(self.support_ids),
                    extra_target_calibration_images=0,grid=self.grid,dimension=self.support_features[0].shape[1],
                    unique_support_feature_inputs=len(self.support_features),slot_indices=self.slot_indices,
                    subspaces={k:s.metadata() for k,s in self.subspaces.items()},
                    correction='Nonnegative additive residual; unchanged baseline when strength=0',
                    gate_semantics='Heuristic residual/(residual+cosine-distance), not calibrated reliability',
                    strict_target_support_budget=True,probabilities=False)

    def save(self,prefix,params,threshold,provenance,*,pixel_threshold=None):
        if not isinstance(params,HybridParameters) or not math.isfinite(threshold):raise ValueError('Validated locked parameters/cutoff required.')
        prefix=Path(prefix);prefix.parent.mkdir(parents=True,exist_ok=True)
        arrays={f'view_{i:03d}':x.numpy() for i,x in enumerate(self.support_features)}
        npz=prefix.with_suffix('.npz');meta=prefix.with_suffix('.json')
        if npz.exists() or meta.exists():raise ValueError('Refuse checkpoint overwrite.')
        np.savez_compressed(npz,**arrays)
        document=dict(schema_version=1,kind='VisionHybrid',params=asdict(params),parameters_id=params.id,
                      threshold=threshold,pixel_threshold=pixel_threshold,support_ids=list(self.support_ids),slot_indices=self.slot_indices,
                      clusters=list(self.clusters),variances=list(self.variances),threads=self.threads,
                      array_hashes={k:array_hash(v) for k,v in arrays.items()},
                      npz_sha256=hashlib.sha256(npz.read_bytes()).hexdigest(),source_hashes=source_hashes(),
                      provenance=provenance,model_metadata=self.metadata(),
                      software_versions={'numpy':np.__version__,'torch':str(torch.__version__),'sklearn':sklearn.__version__})
        meta.write_text(json.dumps(document,indent=2,allow_nan=False)+'\n')

    @classmethod
    def load(cls,prefix):
        prefix=Path(prefix).with_suffix('');doc=json.loads(prefix.with_suffix('.json').read_text())
        if doc.get('kind')!='VisionHybrid' or doc.get('schema_version')!=1:raise ValueError('Unknown model schema.')
        if doc['software_versions']!={'numpy':np.__version__,'torch':str(torch.__version__),'sklearn':sklearn.__version__}:
            raise ValueError('Checkpoint requires its recorded numerical software versions for reproducible refitting.')
        if doc['source_hashes']!=source_hashes():raise ValueError('Checkpoint scoring/encoder source changed.')
        npz=prefix.with_suffix('.npz')
        if hashlib.sha256(npz.read_bytes()).hexdigest()!=doc['npz_sha256']:raise ValueError('Checkpoint NPZ checksum mismatch.')
        with np.load(npz,allow_pickle=False) as saved:
            if set(saved.files)!=set(doc['array_hashes']):raise ValueError('Checkpoint feature schema mismatch.')
            arrays=[saved[k].copy() for k in sorted(saved.files)]
            if any(array_hash(saved[k])!=h for k,h in doc['array_hashes'].items()):raise ValueError('Support feature checksum mismatch.')
        torch.set_num_threads(doc['threads'])
        model=cls(arrays,doc['slot_indices'],doc['support_ids'],clusters=doc['clusters'],variances=doc['variances'],threads=doc['threads'])
        model.params=HybridParameters(**doc['params']);model.threshold=float(doc['threshold']);model.provenance=doc['provenance']
        model.pixel_threshold=doc['pixel_threshold']
        if model.params.id!=doc['parameters_id']:raise ValueError('Parameters ID mismatch.')
        if model.metadata()!=doc['model_metadata']:raise ValueError('Reconstructed model metadata differs.')
        return model
