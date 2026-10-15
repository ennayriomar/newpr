# VisionAD-style repository organization

The inspected reference is
[VisionAD revision 2d5e36f](https://github.com/Qiqigeww/VisionAD/tree/2d5e36f357409125ccd9646ba016824005599df4).
Its layout is used as a structural example. The new files are independent
interfaces around this project's existing numerical implementation.

| Reference location | SAFAL location | Purpose |
|---|---|---|
| models/uad.py | models/uad.py | Public anomaly-detection model |
| models/vit_encoder.py | models/vit_encoder.py | Frozen visual encoder |
| dataset.py | dataset.py | Native dataset classes and sample roles |
| utils.py | utils.py | Configuration and reproducibility utilities |
| dade_mvtec_test.py | hybrid_mvtec_test.py | MVTec AD experiment entry point |
| dade_visa_test.py | hybrid_visa_test.py | VisA experiment entry point |
| test_mvtec.sh / test_visa.sh | same shell entry-point names | Dataset evaluation |
| prepare_data/ | prepare_data/ | Dataset setup documentation |
| requirements.txt | requirements.txt | Pinned CPU environment |
| README.md | README.md | Setup, data, fitting, evaluation and actual results |

`train.py`, `test.py`, `predict.py` and `train_study.py` provide additional
explicit stages. Single-category fitting uses the frozen existing scoring
preset; it does not rerun selection on target test labels. The separate study
driver preserves source selection followed by frozen evaluation.

The checkpoint-producing/scoring modules under `framework/safe_iad` remain
byte-identical. Public classes subclass that shared engine so old checkpoint
source hashes and numerical behavior remain valid. No older archive, trained
model or report is renamed or overwritten. Metadata for new category banks
records exact original support IDs, source-selection lock, software versions
and the interface hashes used for fitting.

This organization is not a full reproduction of VisionAD or evidence of a
new accuracy gain. Native single-category evaluation can include images used
by earlier research. Smoke subsets are explicitly marked, and no full-paper
benchmark or fresh holdout claim follows from them.
