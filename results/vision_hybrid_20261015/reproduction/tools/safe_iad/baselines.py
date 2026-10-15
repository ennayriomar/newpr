"""Official scoring-core integrations with fully declared backbone variants.

These are controlled ViT-B/14 comparisons, not published-table reproductions.
AnomalyDINO's supported force_no_mask_no_rotation setting is used. SubspaceAD
calls the official linear PCA/reconstruction/postprocessing implementation,
with the common backbone and declared layers, resolution and no augmentation.
"""
import importlib
import importlib.util
from pathlib import Path
import subprocess
import sys

import numpy as np
import torch

from .dense_features import restore_dense
from .hybrid import SupportHybrid, distances


SOURCE_PINS = {
    'anomalydino': ('/workspace/.cache/anomalydino-source', 'b9d1c2648e3a5247437d4d953d907a8f3d994457', 'https://github.com/dammsi/AnomalyDINO'),
    'subspacead': ('/workspace/.cache/subspacead-source', 'ef56d5c8ab2f1feb7dda1c93b25cc3f73f0960d7', 'https://github.com/CLendering/SubspaceAD'),
}


def verify_sources():
    records = {}
    for name, (path, pin, url) in SOURCE_PINS.items():
        head = subprocess.check_output(['git', '-C', path, 'rev-parse', 'HEAD'], text=True).strip()
        status = subprocess.check_output(['git', '-C', path, 'status', '--porcelain', '--untracked-files=no'], text=True).strip()
        if head != pin or status:
            raise ValueError(f'Official {name} dependency changed; no fallback is permitted.')
        records[name] = dict(source_url=url, commit=head, license='Apache-2.0', claim='official scoring core; declared common-backbone variant, not published-table reproduction')
    return records


def official_modules():
    verify_sources()
    # The upstream SubspaceAD tree tracks .pyc files. Importing must not rewrite
    # that dependency's tracked artifacts or invalidate the source audit.
    sys.dont_write_bytecode = True
    # The official scoring modules are imported without changing their code.
    sys.path.insert(0, SOURCE_PINS['anomalydino'][0])
    sys.path.insert(0, str(Path(SOURCE_PINS['subspacead'][0]) / 'src'))
    adino_utils = importlib.import_module('src.utils')
    adino_eval = importlib.import_module('src.post_eval')
    pca = importlib.import_module('subspacead.core.pca')
    scoring = importlib.import_module('subspacead.post_process.scoring')
    return adino_utils, adino_eval, pca, scoring


METHODS = ('transparent_nn', 'anomalydino', 'subspacead', 'support_hybrid')


class FittedMethod:
    def __init__(self, method, support_bundles, settings):
        if method not in METHODS or not support_bundles:
            raise ValueError('A known method and nonempty support set are required.')
        self.method = method
        self.mode = 'anomalydino' if method == 'anomalydino' else 'subspacead' if method == 'subspacead' else 'hybrid'
        if any(b.mode != self.mode for b in support_bundles):
            raise ValueError('Support extraction mode disagrees with method.')
        memory = torch.cat([b.tokens for b in support_bundles])
        self.metadata = dict(method=method, base_normal_images=len(support_bundles), augmented_images=0, memory_tokens=len(memory), feature_dim=memory.shape[1], candidate_pool_size=0, acquisition_budget=0)
        if method == 'support_hybrid':
            self.engine = SupportHybrid(memory, **settings['hybrid'])
            self.metadata.update(self.engine.metadata())
        elif method == 'transparent_nn':
            self.memory = memory
            self.metadata.update(baseline='internal exact normalized patch NN; not a full PatchCore reproduction')
        elif method == 'anomalydino':
            import faiss
            faiss.omp_set_num_threads(3)
            self.utils, self.evaluation, _, _ = official_modules()
            memory_np = memory.numpy().astype('float32', copy=True)
            faiss.normalize_L2(memory_np)
            self.engine = faiss.IndexFlatL2(memory_np.shape[1])
            self.engine.add(memory_np)
            self.metadata.update(preprocessing='official supported force_no_mask_no_rotation', knn_metric='L2_normalized squared distance / 2 = 1-cosine', neighbors=1, image_aggregation='official floor top1% patches, max if <100 patches', map='official cv2 bilinear + scipy Gaussian sigma=4', deviations='ViT-B/14, configured resolution, paired support IDs; not default ViT-S/14 448 agnostic results')
        else:
            _, _, official_pca, self.scoring = official_modules()
            arrays = [b.tokens.numpy().astype('float32') for b in support_bundles]
            pca = official_pca.PCAModel(ev=settings['subspace_explained_variance'], whiten=False)
            self.engine = pca.fit(lambda: iter(arrays), memory.shape[1], len(memory), len(arrays))
            self.metadata.update(pca_components=self.engine['k'], pca_ev=settings['subspace_explained_variance'], score_method='official squared reconstruction', feature_aggregation='unnormalized mean of declared ViT-B blocks', map='official square-resolution cv2 bilinear + 3x3 Gaussian sigma=4; then native bilinear', image_aggregation='official floor top1% of square-resolution processed map', deviations='common official DINOv2 ViT-B/14 source, configured resolution/layers and aug_count=0; not published ViT-G/registers 672 augmented benchmarks')

    def predict(self, bundle):
        if bundle.mode != self.mode:
            raise ValueError('Query extraction mode disagrees with fitted model.')
        adequate = None
        if self.method == 'support_hybrid':
            fields = self.engine.predict(bundle.tokens)
            raw = fields['defect']
            maps = {name: restore_dense(value, bundle).astype('float32') for name, value in fields.items()}
            adequate = float(maps['adequacy'].mean())
            score = float(raw.topk(max(1, int(len(raw)*.01))).values.mean())
        elif self.method == 'transparent_nn':
            raw = torch.cat([d.min(dim=1).values for d in distances(bundle.tokens, self.memory)])
            maps = dict(defect=restore_dense(raw, bundle).astype('float32'))
            score = float(raw.topk(max(1, int(len(raw)*.01))).values.mean())
        elif self.method == 'anomalydino':
            import faiss
            query = bundle.tokens.numpy().astype('float32', copy=True)
            faiss.normalize_L2(query)
            raw = np.maximum(self.engine.search(query, 1)[0][:, 0] / 2, 0)
            w, h = bundle.original_size
            maps = dict(defect=self.utils.dists2map(raw.reshape(bundle.grid), (h, w, 3)).astype('float32'))
            score = float(self.evaluation.mean_top1p(raw))
        else:
            raw = self.scoring.calculate_anomaly_scores(bundle.tokens.numpy(), self.engine, 'reconstruction', drop_k=0)
            square = self.scoring.post_process_map(raw.reshape(bundle.grid), bundle.padded_size[0])
            score = self.scoring.aggregate_image_score(square, 'mtop1p')
            w, h = bundle.original_size
            import cv2
            maps = dict(defect=cv2.resize(square, (w, h), interpolation=cv2.INTER_LINEAR).astype('float32'))
        if not np.isfinite(score) or any(not np.isfinite(m).all() for m in maps.values()):
            raise ValueError('Model produced nonfinite evidence; refusing silent replacement.')
        return dict(image_score=score, mean_adequacy=adequate, maps=maps)
