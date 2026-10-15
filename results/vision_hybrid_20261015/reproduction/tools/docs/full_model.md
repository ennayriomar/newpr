# SAFAL full research model

Project: **Support-Adequacy-Aware Few-Shot Anomaly Localization for Reliable
Industrial Inspection**. Working method: **SAFAL**.

This guide describes the independent executable research implementation and its
information budgets. It does not establish faithful reproduction of published
SubspaceAD/VisionAD recipes, a validated adequacy event, improved accuracy or
deployment reliability. Verified paper/source identities and recipe differences
remain in [literature_review.md](literature_review.md); the unresolved scientific
questions are in [research_gap.md](research_gap.md).

## Model components and attribution

The frozen spatial encoder supplies patch descriptors to two independently
implemented branches. The raw-feature branch fits a normal PCA subspace and
scores reconstruction residuals, inspired by
[SubspaceAD](https://github.com/CLendering/SubspaceAD). The retrieval branch
normalizes patch descriptors and performs exact cosine nearest-neighbor search,
inspired by the VisionAD paper
[*Search is All You Need for Few-shot Anomaly Detection*](https://arxiv.org/abs/2504.11895)
and its [official repository](https://github.com/Qiqigeww/VisionAD).

No VisionAD source is copied or vendored. Its inspected source terms remain
unresolved. The independent research branches must be named as adaptations,
not labeled as faithful published-method reproduction. The frozen encoder,
resolution, layers, preprocessing, augmentations and score/map aggregation are
recorded explicitly in the configuration and fitted-model metadata.

For a raw patch descriptor x, normal support mean μ and fitted PCA projector P,
the subspace evidence is the squared reconstruction residual:

    R_sub(x) = ||(I − P)(x − μ)||².

For separately unit-normalized query and support descriptors, retrieval evidence
is exact cosine distance:

    R_search(x) = min_s [1 − <x̂, ŝ>].

These scores have different units. Their normalization uses declared normal
calibration data; evaluation queries must not set their scales. Both raw maps
are preserved together with normalized maps and every fusion result.

The core fits unwhitened PCA using float64 SVD with the configured explained-
variance fraction. It computes image evidence as the mean of the largest
`max(1, floor(0.01 × patch_count))` raw patch scores. Normal calibration fits
four separate empirical quantiles: image/search, image/subspace, patch/search
and patch/subspace. The default quantile is 0.95 with linear interpolation;
pooled calibration patches remain correlated. This differs from earlier
mean-plus-three-standard-deviations pilot calibration. It does not guarantee a
false-alarm rate. Zero, negative or nonfinite cutoff scales are rejected.

The comparison includes individual branches, fixed averaging, a fixed max
control and adequacy-conditioned fusion. Adaptive fusion uses a bounded
diagnostic and a constrained weight function recorded in the model. A max
control can preserve either branch's fixed-cutoff alert but increase false
alarms; weighted averaging can suppress an individual branch's alert. Neither
strategy mathematically guarantees better accuracy or localization.

## Adequacy, uncertainty and optional error calibration

Support adequacy is a bounded diagnostic in `[0,1]`. Its intended use is to
describe relevant normal-reference coverage, not to declare a query normal or
predict correctness by definition. The model records its diagnostic formula
and feature/support assumptions. Density, entropy, stability and reference
counts are proxies that still need construct validation. A bounded score or
sigmoid is not a calibrated probability.

In the implemented core, let r_search and r_sub be raw patch scores divided by
their separately fitted patch cutoffs. The exact diagnostic and weight are:

    C_search = 1 / (1 + r_search)
    C_sub = 1 / (1 + r_sub)
    A_patch = (C_search + C_sub) / 2
    w_search = clip(0.9 − 0.8 × A_patch, 0.1, 0.9)
    w_sub = 1 − w_search
    M_safal = w_search × r_search + w_sub × r_sub

The image-level `A` is the mean of `A_patch`. Low compatibility favors the
search branch under this predeclared heuristic. That direction is unverified.
The diagnostic is a deterministic function of branch evidence; it is not an
independently learned or externally validated normal-mode coverage estimator.
The reported leave-image-out fields are diagnostics, not inputs to this weight.

Patch uncertainty is the mean of branch disagreement and `1 − A_patch`, where
disagreement is `abs(r_search − r_sub) / (r_search + r_sub)`. When both branch
scores are zero, disagreement is defined as zero. The image-level `U` is the
mean patch uncertainty. This is a bounded diagnostic, not an error probability.
The present fusion weight depends on adequacy alone; the uncertainty field is
exposed for separate error/review analysis, not a claimed uncertainty-conditioned
fusion result.

Separate support-only statistics from query-conditioned evidence. Unseen
legitimate normal appearance and genuine defects can both produce unusual
query features. That ambiguity is part of the research problem, not resolved
merely by naming a map “adequacy.” Leave-one-reference-image-out sensitivity is
undefined at k=1 and must be represented as missing, not as zero sensitivity.

Optional error calibration is a separate source-only component with an explicit
prediction-error target. Its training labels and diagnostics must come from
permitted development groups, with source-image/parent separation from its
validation/calibration samples. It must not fit on final-query labels or masks.
An error probability, if provided, is neither an adequacy probability nor a
ground-truth reference-sufficiency estimate. A model fitted on synthetic source
defects needs an explicit transfer limitation for native defects.

If no error calibrator is fitted, inference must say it is absent. Never fill a
missing calibrator with the adequacy score and call the result confidence.
Review/abstention decisions must preserve raw maps and evidence flags and be
evaluated jointly with coverage, conditional error, false alarms and missed
defects. A visually plausible uncertainty map is not verification.

Image and patch normalization are separate. Component image scores use each
branch's raw top-patch score divided by its image cutoff. Fixed average and max
combine those image ratios; the adaptive image score aggregates patch-weighted
raw branch scores divided by image cutoffs. Patch weights are computed from
patch-normalized evidence. All locked core image alerts use a threshold of one.

## Support, calibration and evaluation roles

Support images are verified normal training images. The support bank contains
exactly the declared number of original references; augmented views, patch
tokens and independent original images are counted separately. Additional
normal calibration images must be disjoint from their support bank and query
evaluation images, with IDs and hashes saved.

A model using k support images plus n extra normal calibration images has a
k+n original-image information budget. Reporting its detector bank as k-shot
does not make the complete experiment a strict total-k-image protocol. State
whether calibration normals are target-category data or reserved source/
calibration-category data; the transfer and false-alarm assumptions differ.

Source-meta training, validation model selection, normal score calibration and
locked evaluation retain separate roles. Query labels/masks are used only for
offline evaluation under a frozen configuration. They cannot enter descriptor
construction, PCA fitting, support selection, diagnostic features or cutoff
fitting. Any optional learned fusion/error component adds a development-data
budget that must be declared alongside the normal-reference budget.

Previously inspected images/categories are recorded in the exposure ledger;
they must not be described as untouched final holdouts. The existing M3 and
strict-hybrid outcomes remain historical, separate evidence. Their negative
findings are preserved when a new configuration is evaluated.

## Installation and independent model artifacts

The checked research runtime is Linux/Python 3.12 with pinned CPU PyTorch.
Historical pipeline scripts still use the documented `/workspace` layout. The
new SAFAL encoder accepts explicit source, checkpoint and feature-cache paths;
it does not require a copied historical weight-verification report.

Its encoder always verifies the actual ViT-B/14 checkpoint hash and strictly
loads the pretrained state dictionary. Source verification accepts either a
clean pinned official Git checkout or a bundled source snapshot with its trusted
manifest. The source manifest is anchored to the pinned official Python-file
and license digest; an arbitrary local manifest cannot authorize modified code.
The preparation command obtains the pinned source and verified weights over
the official download path. No dataset is downloaded by encoder preparation.

Dataset images remain prerequisites for native-image experiments. The source
ZIP excludes raw datasets, encoder weight binaries, virtual environments and
large feature caches. GPU behavior and broad cross-platform compatibility are
unverified; explicit path configuration alone is not evidence of either.

SAFAL fitted artifacts and the frozen DINOv2 checkpoint are distinct:

- The fitted SAFAL NPZ/JSON pair records the support-dependent representation,
  calibration, fusion/diagnostic settings and model provenance.
- The frozen encoder checkpoint supplies pretrained visual features. Fitting
  SAFAL does not fine-tune or replace these weights.
- Dataset images/masks remain separately obtained inputs. Model serialization
  cannot replace them for a new real-data evaluation.

The NPZ contains the raw support tensors. JSON records cutoffs, support and
calibration IDs, feature hashes, implementation hashes and the NPZ checksum.
Reload verifies source and tensor provenance, then reconstructs PCA/search/LOO
models on CPU from the saved support tensors. It does not deserialize a Python
pickle or claim that a frozen PCA basis was stored separately. Round-trip
prediction tests are distinct from cross-version/hardware reproducibility.

Read the release's `BUNDLE_README.md` for restore paths and pinned dependencies.
Keep original licenses/notices with any bundled permitted dependency snapshots.
Use new output directories for new data/config/code; copied reports are not
portable resume inputs because ledgers reference actual absolute input paths
and hashes.

## Command interface and reproducibility

The command interface is `python -m safe_iad.safal_cli`, with `prepare`, `train`,
`evaluate`, `predict` and `demo` subcommands. The arguments below match its CLI;
the supplied experiment configuration is `configs/safal_demo.json`.

From `tools/` in the extracted code ZIP, or `framework/` in the GitHub checkout:

```bash
bash install_safal.sh
source .venv/bin/activate
python -m safe_iad.safal_cli --help
python -m safe_iad.safal_cli prepare --destination ../safal_assets
```

The installer uses Python 3.12 and pinned CPU requirements. Its optional first
argument chooses another virtual-environment directory. `prepare` obtains the
official pinned source and checkpoint, verifies them, and prints their paths.
It can reuse valid existing inputs. The checkpoint is excluded from the code ZIP
and must be obtained separately; its pinned hash was recorded from the prior
official download, not asserted as a publisher-provided checksum.

Copy `configs/safal_demo.json` for a new run and edit `encoder.source_dir`,
`encoder.checkpoint`, `encoder.cache_root` and the two `roots` paths for your
machine. The prepared source is `../safal_assets/dinov2-source`; the checkpoint is
`../safal_assets/dinov2_vitb14_pretrain.pth`. A trusted bundled source snapshot is
also supported through `source_manifest`. Preserve representation settings when
using an existing fitted model: changed layers/resolution/preprocessing fail
the encoder-binding check.

Run the complete small source-proxy/normal-calibration/native-validation workflow:

```bash
python -m safe_iad.safal_cli demo --config configs/safal_demo.json --output ../reports/my_safal_run
```

Choose a fresh output directory. The supplied demo evaluates reserved validation
categories `hazelnut` and `pcb2`, using k=1,2,4,8, two support seeds and four extra
target-category normal calibration images. It fits the separate error estimator
from original-normal/CutPaste pairs in four source meta-training categories.
Its selected queries are descriptive validation data, not a full benchmark.

The output contains `config.json`, `manifest.json`, `used_inputs.json`, fitted
episode `model.json`/`model.npz`, encoder/episode metadata, prediction tables,
metrics, reliability results, summary and completion ledgers. The separate
`error_calibrator.json` has a source-normal/CutPaste prediction-error event;
its native-defect calibration remains unverified.

### Fit and evaluate a single episode

`train` and `evaluate` use a separate JSON with these keys:

| Key | Required content |
| --- | --- |
| `roots` | Dataset-name to actual native dataset root mapping |
| `encoder` | Verified source/checkpoint/cache paths and declared feature settings |
| `normal_calibration_quantile` | The declared empirical quantile, such as 0.95 |
| `episode.dataset` / `episode.category` | Supported dataset and one category |
| `episode.shots` | Number of original support images |
| `episode.support_ids` | Native relative IDs of distinct normal training images |
| `episode.calibration_ids` | Disjoint normal training-image IDs |
| `episode.query_ids` | Empty for training; declared native test/public IDs for evaluation |
| `episode.k_plus_calibration` | Support count plus extra normal calibration count |

Support, normal calibration and query ID sets must be disjoint. The supplied
`configs/safal_train_example.json` and `configs/safal_evaluate_example.json`
contain actual k=2, seed=5 `hazelnut` support/calibration IDs. The training
example has empty `query_ids`; the evaluation example contains the four known
validation queries. Edit the encoder/root paths for your machine. This reuses
a recorded validation example, not a fresh final test. For a different product,
create an explicit episode with its verified normal references and calibration
images rather than treating these fitted references as universal.

```bash
python -m safe_iad.safal_cli train --config configs/safal_train_example.json --output ../models/my_hazelnut
python -m safe_iad.safal_cli evaluate --config configs/safal_evaluate_example.json --model ../models/my_hazelnut/model --output ../reports/my_hazelnut_eval
```

Training creates `model.json`, `model.npz`, `encoder.json` and `episode.json`.
Evaluation requires the episode's support IDs to match the fitted model and
uses that model's locked calibration; an evaluation config cannot refit it.
Add `--error-calibrator PATH` only when intentionally using the separately fitted
source error estimator.

### Predict one real image

The source bundle includes example k=2, seed=5 fitted episodes for `hazelnut`
and `pcb2`. They are limited-category research examples, not a general-purpose
industrial checkpoint. Copy the matching episode's `encoder.json` and change
only its `runtime_config` source/checkpoint/cache paths to match your machine.

```bash
python -m safe_iad.safal_cli predict --model ../reports/safal_full_model/episodes/mvtec_ad-hazelnut-k2-seed5/model --image /path/to/hazelnut_query.png --encoder-config configs/my_encoder.json --output ../predictions/hazelnut_query
```

This produces `maps.npz` and `prediction.json` without a query-label argument.
For source-proxy error estimates, optionally add
`--error-calibrator ../reports/safal_full_model/error_calibrator.json`. Prediction
records the unverified probability-transfer scope; this option does not turn
the source estimator into calibrated deployment confidence.

The `predict` maps are float32 at the original query-image resolution. Demo and
evaluation maps/metrics instead use a declared 256×256 grid: score maps use
bilinear interpolation and binary masks use nearest-neighbor resizing. Their
pixel metrics are not native-resolution benchmark results. A defect lost during
mask resizing aborts evaluation. Branch/weighted image scores remain defined
from the original patch grid.

Training creates a fitted model and its provenance. Evaluation uses locked
models/configurations and records image/pixel results against actual masks.
Prediction writes branch/fusion/diagnostic maps and image decisions for a real
query without query-label access. A demo or feature-contract check is separate
from a native-image benchmark; every command's input and evaluation scope must
be stated explicitly.

Verification must distinguish unit/contract tests, real pretrained-weight/image
execution, artifact hash checks, completed-run resume checks and independent
re-extraction. Passing one is not evidence that all occurred. Serialization
must reload without silently changing descriptors, calibration or predictions.
No report may substitute mock accuracy or published numbers for measured
outputs from this implementation.

## Executed v0.5.0 validation pilot

The checked final pilot used actual frozen pretrained ViT-B/14 descriptors and
eight unique native queries: four normal and four anomalous images across
`hazelnut`/`pcb2`. Four nested shot settings and two support draws produced 16
fitted episodes, 64 repeated query/support cases and 320 method records. Its
source error-estimation set had 64 original-normal/CutPaste rows from 32 normal
parent images across four meta-training categories. These are additional source
data, not part of the k+4 target-normal budget. Source fitting/audit parents are
separate. All 159 unit/contract tests passed; those tests are distinct from the
actual pretrained-image pilot.

Independent encoder checks used both a manifest-verified bundled source and a
fresh pinned Git checkout, with the existing verified pretrained checkpoint.
They reproduced the float32 features exactly. This does not establish a fresh
weight download, a fresh virtual-environment installation or cross-hardware
reproducibility. Separate command/replay checks are recorded in the release's
run report rather than conflated with a full independent benchmark rerun.

The measured mean-episode results in `summary.json` are:

| Method | Locked image accuracy | Image AUROC | Pixel AP, 256×256 |
| --- | ---: | ---: | ---: |
| Search | 0.87500 | 0.96875 | 0.28166 |
| PCA subspace | 0.96875 | 1.00000 | 0.31710 |
| Fixed average | 0.93750 | 0.98438 | 0.30725 |
| Max control | 0.89063 | 1.00000 | 0.32508 |
| SAFAL adaptive | 0.93750 | 0.96875 | 0.30143 |

**The pilot does not show an accuracy gain.** SAFAL tied the fixed average's
locked accuracy and had lower pixel AP; the PCA branch had higher accuracy.
No fusion parameter or cutoff was tuned after these outcomes. The final rerun
corrected implementation/provenance exports and dependent-shot bookkeeping,
not scientific settings. Nested-shot differences are averaged within each
query/true support draw before the conditional crossed bootstrap. Its observed
zero paired-accuracy difference is not proof of population equivalence.

The results describe only the fixed sampled categories, eight queries and two
support draws. They do not validate support adequacy, native error-probability
calibration, full benchmarks or deployment reliability. The fitted examples and
source-proxy error estimator are included so the implementation can be inspected
and exercised; their presence is not an endorsement for industrial deployment.

## Historical evidence and remaining scientific limits

The earlier strict hybrid's entropy/density adequacy was not established as
reliable decision support. The M3 learned-acquisition pilot improved declared
mean utility but caused four correlated newly missed defect inspections and
reduced defect-pixel recall; its matched support-omission controls did not
establish the proposed false-alarm mechanism. That negative gate and its
limited scope remain in the preserved reports. They do not prove all adequacy
models impossible and do not validate this new implementation.

Executable SAFAL can support controlled experiments while the operational
adequacy event, native-defect generalization, probability calibration, adaptive-
versus-fixed gains and baseline fidelity remain unproven. Full published
benchmark recipes, Real-IAD, private AD2/server results, production readiness,
novelty and journal acceptance are not established. Report actual checked
configuration and limits with the downloadable code bundle.
