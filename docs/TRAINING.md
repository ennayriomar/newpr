# Train and evaluate SAFAL

Training fits a nearest-neighbour memory bank and PCA subspaces from normal
reference images. DINOv2 stays frozen. There is no optimizer, learning rate or
epoch count in this method. The published preset was chosen using separate
source-category development labels and masks.

## Install and prepare

Use Linux/WSL with Python 3.12. From the repository root:

```bash
bash setup_environment.sh
source .venv/bin/activate
python prepare.py --destination checkpoints
```

Preparation fetches the pinned licensed official Meta source and the real
1.22 GB DINOv2 ViT-L/14 register checkpoint. Every load verifies its SHA256.
The default installer uses CPU Torch. CUDA requires a compatible GPU build
and new banks fitted under that numerical environment; GPU operation has not
been validated by the existing CPU experiments.

## Fit a category

MVTec AD must retain category/train/good, category/test and ground_truth
folders. VisA must retain its native Data folders, image_anno.csv files and
split_csv/1cls.csv. See [dataset setup](../prepare_data/README.md).

```bash
python train.py --dataset mvtec_ad --data_path data/mvtec_ad \
  --category bottle --shots 1 --seed 17 --output runs/bottle

python hybrid_mvtec_test.py --run-dir runs/bottle --localization --save-maps
```

For VisA:

```bash
python train.py --dataset visa --data_path data/visa \
  --category capsules --shots 1 --seed 17 --output runs/capsules

python hybrid_visa_test.py --run-dir runs/capsules --localization
```

The matching MVTec entry point is `hybrid_mvtec_test.py`; shell entry points
are `test_mvtec.sh` and `test_visa.sh`. Each test script evaluates the category
bank supplied through `--run-dir`. Repeat with a fresh output for each
category/draw. New draws use sorted native train IDs and seeded Python
sampling; they are not advertised as the exact reference paper's draws.
Use repeated `--support-id category/train/good/image.png` arguments to specify
known normal references explicitly, with the matching `--shots` value.

`train.py` saves `model.npz`, `model.json` and `training.json`. The model stores
normal support descriptors and verifies source/software hashes when reloaded.
The external encoder checkpoint remains separate. `test.py` saves
`evaluation/metrics.json` and `predictions.jsonl`, plus optional cropped maps.
Results include both the unchanged search baseline and the selected hybrid.
The same source-derived cutoff is retained for both methods.

A fast smoke test with formatted outputs is:

```bash
python hybrid_mvtec_test.py --run-dir runs/bottle --max-images 2 --output runs/bottle/smoke
```

This evaluates a metadata-stratified subset, marks it as such and does not
replace a full evaluation. Existing output directories are never overwritten.
Native labels and masks provide evaluation metrics and do not tune parameters;
the smoke subset uses native label metadata for its sampling order.
The full native test split may overlap prior research history; these simple
category scripts make no claim of a newly reserved cohort.

The dataset scripts and `evaluate.py` produce reference-style metric lines,
tables and diagnostic PNGs by default. See [output options](OUTPUTS.md) for
`--save_dir`, `--save_name`, category means, global/local display scaling and
exporting existing results. `test.py` remains the original raw evaluator.

## Predict your image

```bash
python predict.py --model runs/bottle/model --image /path/to/bottle.png \
  --output runs/my_prediction
```

Prediction accepts no labels or masks. The output is an image decision and a
256×256 map covering the center-cropped ROI. Outer borders are unscored.
Scores are not calibrated probabilities.

## Reproduce development selection

The separate study driver preserves the original finite 25-cell search,
source-category labels/masks, frozen selection and subsequent evaluation:

```bash
python train_study.py --mvtec-root data/mvtec_ad --visa-root data/visa \
  --output runs/study --stage develop
python train_study.py --output runs/study --stage evaluate
python train_study.py --output runs/study --stage report
```

`configs/study.json` resolves all paths relative to its own directory.
Historical split/exposure manifests are bundled under `configs/protocol`.
The study uses 100 development and 100 already-known verification image IDs,
five categories per group, and two one-shot support draws. Repeating this
protocol is reproduction, not a new independent validation. Change scoring
parameters only through development selection, freeze the choice and reserve
additional untouched data before making a new improvement claim.

The existing CPU study's hybrid AUROC was 98.70% versus 97.80% search, but
accuracy at the shared cutoff declined from 78.50% to 75.50% through additional
false alarms. Its AUROC interval includes zero. This reorganization does not
change those results or establish improvement over VisionAD.
