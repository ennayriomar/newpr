# Dataset acquisition and verification

All three archive SHA-256 checks passed. Real-file decoding, image-mask pairing/alignment, mask values, unique IDs and native-split content-overlap checks passed for every retained image. Normal masks are represented as implicit zeros. No experimental calibration/validation split is implied by these native-split checks.

| Dataset | Categories | Images checked | Root | Retained scope |
|---|---:|---:|---|---|
| mvtec_ad | 15 | 5,354 | `/workspace/datasets/mvtec_ad` | Complete official archive |
| visa | 12 | 10,821 | `/workspace/datasets/visa` | Complete official archive |
| mvtec_ad2 | 8 | 3,914 | `/workspace/datasets/mvtec_ad2_public/mvtec_ad_2` | Train, validation, public test; private splits excluded |

MVTec AD and VisA were downloaded and extracted from the original archive endpoints recorded in download_manifest.json. The user-supplied Kaggle mirror remained blocked, so the official Amazon VisA source was used without Kaggle credentials. Verified redundant main-benchmark archives were removed after extraction.

The full MVTec AD 2 archive is 32,739,596,982 bytes and could not fit locally alongside the main datasets. It was streamed completely with its SHA-256 verified, retaining all public/train/validation files (16,338,191,665 bytes). Private test files were not retained or evaluated. The original archive inventory, including skipped paths and sizes, is saved in mvtec_ad2_extraction.json.

Official AD 2 loader/submission utilities were downloaded into `/workspace/datasets/official_ad2_tools`. Their code was inspected; official private prediction export/server evaluation has not run.

## Exact verification commands (executed successfully)

```bash
PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m safe_iad.verify_dataset --dataset mvtec_ad --root /workspace/datasets/mvtec_ad --output /workspace/reports/dataset_verification --workers 4
PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m safe_iad.verify_dataset --dataset visa --root /workspace/datasets/visa --output /workspace/reports/dataset_verification --workers 4
PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m safe_iad.verify_dataset --dataset mvtec_ad2 --root /workspace/datasets/mvtec_ad2_public/mvtec_ad_2 --output /workspace/reports/dataset_verification --workers 4
```

For each dataset, see `/workspace/reports/dataset_verification/<dataset>/verification.json`, `images.jsonl` and `visuals/`. Source URLs, checksum references, license notes and acquisition outcomes are in download_manifest.json. MVTec licenses are CC BY-NC-SA 4.0; VisA is CC BY 4.0.

Reusable install_script and start_skill are saved in the environment draft. Saving does not publish or establish restoration in another task. Review/save the settings and publish through the environment UI when ready.
