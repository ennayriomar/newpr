# SAFAL Phase A report

Audit date: **2026-10-14**, using the user's Asia/Shanghai date context.
Raw source-retrieval timestamps are retained separately in UTC.

This report completes the requested **Phase A only** foundation audit for
**Support-Adequacy-Aware Few-Shot Anomaly Localization for Reliable Industrial
Inspection**, working method name **SAFAL**. No new detector development,
baseline experiment, full benchmark or manuscript result was started after
the Phase-A-only instruction. Earlier work remains preliminary evidence.

## Repository and execution environment

The user-selected research repository is
[ennayriomar/newpr](https://github.com/ennayriomar/newpr). Its public main was
`834426fbda8bfd3a36781ba682ec2da99729adaf` at inspection and contains the
published v0.4.0 framework and preserved code/results archives. The local
`/workspace/newpr` checkout is clean but behind that revision. The profile
checkout `/workspace/ennayriomar` is also clean and preserved. A filtered bare
Git repository is available for publishing small documentation changes without
downloading the multi-gigabyte results archive.

Executable research source is in `/workspace/tools`; the installed editable
package is `safe-iad-research` v0.4.0. Additional prototype source and outputs
from the preceding request are retained locally and have not been published
as a new package release. Phase A does not rename the package or replace prior
scientific artifacts.

| Capability | Observed status |
| --- | --- |
| Python | 3.12.14, Linux |
| PyTorch / torchvision | 2.7.1+cpu / 0.22.1+cpu |
| CPU | Five CPUs in affinity; cgroup quota is four CPU equivalents |
| Container memory limit | 32 GiB |
| CUDA / GPUs | CUDA build absent; zero available GPUs; `nvidia-smi` absent |
| `/workspace` free space | About 637 MiB at audit |
| Separate `/tmp` free space | About 12.7 GiB at audit |
| Services | No background service is required for the current library workflow |

Dependency versions, precise disk bytes and current dataset inventories are
recorded in [environment_and_data_audit.json](environment_and_data_audit.json).
CPU availability does not establish feasible runtime for the published giant
or large backbone recipes. GPU peak memory and full-recipe throughput are
unmeasured.

The official local dependency checkouts have no tracked changes:

| Source | Verified local revision |
| --- | --- |
| DINOv2 | `7764ea0f912e53c92e82eb78a2a1631e92725fc8` |
| SubspaceAD | `ef56d5c8ab2f1feb7dda1c93b25cc3f73f0960d7` |
| AnomalyDINO | `b9d1c2648e3a5247437d4d953d907a8f3d994457` |

Prior real-weight checks loaded the actual frozen DINOv2 ViT-B/14 checkpoint,
whose locally computed SHA256 is
`0b8b82f85de91b424aded121c7e1dcc2b7bc6d0adeea651bf73a13307fad8c73`.
This is not verification of the larger register-equipped checkpoints required
by the exact reference recipes.

## Research foundations and baseline fidelity

The relevant VisionAD is
[Qiqigeww/VisionAD](https://github.com/Qiqigeww/VisionAD), accompanying
*Search is All You Need for Few-shot Anomaly Detection*. It is distinct from
the similarly named benchmarking library. Its verified source revision is
`2d5e36f357409125ccd9646ba016824005599df4`.

The [literature review](literature_review.md) records the exact inspected
SubspaceAD and VisionAD recipes, support/view budgets, feature normalization,
map construction and evaluation differences. It also examines PatchCore,
PaDiM, AnomalyDINO, calibration and selective prediction through verified
primary sources.

Two material VisionAD issues remain: no source redistribution license was
found at the inspected revision, and the advertised visualization evaluator
returns zero-valued numerical metrics. Its original Python/CUDA requirements
also differ from the installed CPU runtime. These facts require a documented
Phase B integration strategy; a successful script launch would not prove
accuracy or recipe fidelity.

The existing official SubspaceAD PCA/scoring adapter is a declared
ViT-B/14, 224-pixel common-backbone variant. The earlier and newly retained
independent PCA/search prototypes likewise do not reproduce the published
giant/registers, 672-pixel SubspaceAD or large/registers, multi-view VisionAD
recipes. No published performance figure is copied into our measured results.

The related-work search was bounded. Some academic-search endpoints were
proxy-blocked. Combining PCA, patch search, calibration and rejection is not
established novelty. The [research-gap assessment](research_gap.md) defines
what remains to be shown about support adequacy and adaptive fusion.

## Data availability and protocol limits

Fresh metadata/file-inventory checks completed with **zero inventory issues**:

| Dataset | Current local images | Categories | Retained scope |
| --- | ---: | ---: | --- |
| MVTec AD | 5,354 | 15 | Normal training, mixed test, pixel masks |
| VisA | 10,821 | 12 | Official one-class split CSV and masks |
| MVTec AD 2 | 3,914 | 8 | Training, defect-free validation, public test only |
| Real-IAD | Absent | Not locally verified | No images or official split JSONs restored |

These are current inventories. Whole-dataset decoding/checksum verification
is historical; recently selected pilot inputs were separately physically
verified. Phase A did not rerun full image decoding or download dataset
archives.

MVTec AD/AD 2 data licenses are CC BY-NC-SA 4.0; VisA data is CC BY 4.0.
Real-IAD's dataset terms and completed access remain unverified because the
data host was proxy-blocked. The official page advertises approximately 53 GB
and 507 GB releases, both beyond current available storage. Its website and
experiment-code licenses must not be mistaken for image-dataset rights.
Real-IAD also requires physical-part grouping across its five views and
explicit image-versus-part support budgets. See
[dataset_readiness.md](dataset_readiness.md) for source evidence and protocol
details.

No private AD 2 images, server scores or complete private submission are
available. Existing public export checks do not establish a private benchmark.

## Existing evidence and what it does not establish

Before the latest instruction, the local code passed **122 unit/contract
tests**, including the separate prototype tests. These tests are not faithful
baseline reproduction or independent full benchmarks. Existing M1/M2/M3 and
strict-hybrid artifacts remain preserved, including negative results.

Three recent, distinct preliminary PCA/search validation pilots completed.
Each used 24 unique native validation images, 216 paired query/support cases
and 648 branch/fusion records. All three advancement gates were negative.
The third used k references plus four extra target-normal calibration images
per inspection and explicitly did not claim strict k-image few-shot learning.
Their query sets and calibration protocols differ, so cross-pilot aggregate
numbers cannot isolate the causal effect of a component.

Earlier artifact audits and limited fresh-feature probes have explicit scopes.
An integrity check is not a full independent rerun. Where verification of the
newest artifacts is incomplete, those outputs remain preliminary. No robust
accuracy improvement, calibrated support-adequacy event, faithful VisionAD
reproduction, novelty, SOTA result or publication acceptance is established.

## Files produced and next actions

Phase A creates the literature review, research-gap assessment, dataset
readiness audit, this report, the machine-readable environment/source evidence,
and [implementation_plan.md](implementation_plan.md). The plan adapts the
existing package rather than generating a replacement codebase or placeholder
module tree.

The next concrete phase is a small **Phase B reference-branch reproduction**:
fix the exact recipes and score-export contracts, resolve VisionAD code terms,
choose resources and pin the required checkpoints. Only afterward should new
adequacy-conditioned fusion, uncertainty, calibration and large experiments be
treated as the SAFAL research implementation. The mathematical adequacy target,
unexposed evaluation roles and added target-normal information budget must be
specified before fitting the method.

Phase A is complete when these documents and source observations are reviewed
for consistency. No user preference is required to finish this audit, and no
later phase is claimed complete by this report.
