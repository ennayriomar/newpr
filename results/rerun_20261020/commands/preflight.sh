python - <<'PY'
import os, json, hashlib
paths = [
'/tmp/safal_controlled_assets/dinov2_vitl14_reg4_pretrain.pth',
'/workspace/.cache/dinov2-source',
'/workspace/datasets/mvtec_ad2_public/mvtec_ad_2',
'/workspace/datasets/mvtec_ad',
'/workspace/datasets/visa',
'/workspace/scratch/87bcf964428f/controlled_experiment.py',
'/workspace/scratch/87bcf964428f/results/controlled_full_image_20261018/per_image.jsonl',
]
for path in paths:
    try:
        st = os.stat(path)
        row = {'path': path, 'result': 'present', 'is_directory': os.path.isdir(path), 'bytes': st.st_size}
        if path.endswith('.pth'):
            h = hashlib.sha256()
            with open(path, 'rb') as f:
                for block in iter(lambda: f.read(1024*1024), b''):
                    h.update(block)
            row['sha256'] = h.hexdigest()
    except OSError as e:
        row = {'path': path, 'error_type': type(e).__name__, 'errno': e.errno, 'error': str(e)}
    print(json.dumps(row, sort_keys=True))
print('PREFLIGHT ONLY: no features extracted, PCA fitted, inference, calibration, metrics, leakage enumeration, or model reruns performed.')
PY
