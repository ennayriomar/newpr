# Dataset readiness — Phase A

This is a documentation and protocol audit. No dataset archive was downloaded,
no access request or evaluation submission was sent, and no experiment was run.
Raw retrieved pages and the split CSV remain in the local evidence file
`/tmp/safal_phase_a/dataset_online_verification.json`. The published
[metadata export](dataset_source_verification.json) records source URLs, hashes,
retrieval errors and factual findings without redistributing source bodies.

The existing three datasets can support a carefully scoped pilot. Original
Real-IAD is a planned evaluation dataset: its images and official split JSONs are
absent locally, its dataset terms could not be inspected, and the advertised full
release does not fit available storage.

| Dataset | Published protocol and locally retained scope | Dataset license verified online | Readiness |
| --- | --- | --- | --- |
| MVTec AD | Official page describes 15 categories, normal-only training, mixed normal/anomalous test images and pixel masks. Earlier verified local inventory: 5,354 images. | CC BY-NC-SA 4.0 | Existing data; current manifests and role separation still need checking before an approved run. |
| VisA | Official 12-category release: 10,821 images, 9,621 normal and 1,200 anomalous. The retrieved official one-class CSV has 8,659 normal training images, 962 normal test images and 1,200 anomalous test images. Earlier verified local inventory: 10,821 images. | CC BY 4.0 | Existing data with an authoritative split CSV. |
| MVTec AD 2 | Official eight-scenario dataset has more than 8,000 images. Earlier verified local inventory retains 3,914 train/validation/public-test images; private test splits are excluded. | CC BY-NC-SA 4.0 | Public-only stress evaluation; incomplete for the full official benchmark. |
| Original Real-IAD | The original paper reports 30 objects, 151,050 images, 99,721 normal and 51,329 anomalous images, with five views per physical sample. These are published counts, not a local inventory. | Unverified | Absent locally; access, license, exact archives, checksums and storage remain unresolved. |

The prior local image counts are retained evidence from the existing project.
The coordinator's fresh local inventory is the authoritative current-state
check. Dataset availability does not establish an untouched final holdout: some
test categories and images have already been used by historical pilots.

## Authoritative sources and retrieval

- [MVTec AD](https://www.mvtec.com/research-teaching/datasets/mvtec-ad):
  HTTP 200. The page directly states its data license and displays an embedded
  dataset-download form. No form was submitted.
- [MVTec AD 2](https://www.mvtec.com/research-teaching/datasets/mvtec-ad-2):
  HTTP 200. The page directly states its data license, normal-only training and
  validation sets, public masks, and private ground truth evaluated through the
  official public evaluation server. No server submission was made.
- [VisA official repository](https://github.com/amazon-science/spot-diff):
  official README, `LICENSE-DATASET`, repository `LICENSE`, preparation source
  and `split_csv/1cls.csv` were retrieved successfully. Observed repository HEAD:
  `2a692ab575001cbde74d402d897a7286086c6199`.
  `LICENSE-DATASET` is Attribution 4.0 International; the repository code license
  is Apache-2.0. The README links the
  [official VisA archive](https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar),
  which was not fetched in Phase A.
- [Real-IAD original project page](https://realiad4ad.github.io/Real-IAD/):
  blocked by the environment proxy with `Tunnel connection failed: 403 Forbidden`.
  Its authoritative
  [GitHub-hosted page source](https://github.com/realiad4ad/Real-IAD/blob/8f774faa776cd01b974d1ed4283473190201a178/index.html)
  was retrieved successfully instead. That source links original Real-IAD,
  Real-IAD D³, and Real-IAD Variety as separate projects. This audit concerns
  original Real-IAD, not those later variants.
- [Real-IAD paper, arXiv 2403.12580v1](https://arxiv.org/html/2403.12580):
  HTTP 200. Table 1 supplies the published image counts. The collection uses one
  top camera and four cameras at approximately 45 degrees, with pixel-level
  defect masks. Sample-level performance combines multiple views; the paper
  also defines a top-view single-view subset.
- [Current official Real-IAD experiment example](https://github.com/Tencent/AnomalyDetection_Real-IAD/tree/98c28ffbe95b380d17a3777d77219152368c19e9):
  README, license, loader, single-view config and multiview config retrieved
  successfully. The previous
  [TencentYoutuResearch repository](https://github.com/TencentYoutuResearch/AnomalyDetection_Real-IAD)
  now contains a README pointing to this transferred repository.
- [Real-IAD data on Hugging Face](https://huggingface.co/datasets/Real-IAD/Real-IAD):
  both the public API metadata endpoint and dataset README were blocked by the
  same proxy error. Current dataset-card terms, file inventory and access
  approval are therefore unverified.

## Real-IAD release, access and license boundaries

The retrieved project page source advertises:

| Release item | Advertised scope | Advertised size |
| --- | --- | --- |
| `realiad_1024` | Images downsampled to 1024 × 1024 | Around 53 GB |
| `realiad_raw` | Original high-resolution images | Approximately 507 GB |
| `realiad_jsons.zip` | Official structured split metadata | Not stated in the retrieved source |

These are published size descriptions, not verified archive byte counts or
expanded-size measurements. The official example describes one image ZIP per
object. Individual archive sizes and checksums were not available in the
retrieved sources, so a partial download cannot yet be declared feasible.

The current page source says that access requests on Hugging Face are
automatically approved. No request was submitted or approval verified. The
older repository also contains an access-request email template; it does not
establish current access by this project.

The page's CC BY-SA 4.0 statement explicitly licenses the **website source**.
The current experiment repository licenses its **software** under Apache-2.0
with named third-party exceptions. Neither establishes the downloadable image
dataset's license. The dataset license remains unknown until the official
dataset terms can be inspected and recorded. The paper's arXiv publication
license likewise does not establish image-dataset rights.

## Protocol decisions required before an approved run

For MVTec AD and VisA, supports and acquired candidates must come from the
permitted normal training split. Calibration images must be disjoint from
supports, candidate pools and evaluation queries. Source-category fitting,
validation choice, calibration and final evaluation roles must be recorded
explicitly. VisA should retain `split_csv/1cls.csv` as the one-class authority.
The original VisA masks contain multiple anomaly classes; the official
preparation code maps anomaly classes to 255 and normal to 0. Normal masks are
not stored and should be represented as verified zero masks.

For retained MVTec AD 2, distinguish the defect-free validation split from
public test data. Lighting shifts may appear in test data but not in training.
Report local public-test performance with its retained scope. Private-test
results require the official evaluation server and cannot be inferred from
public masks or an incomplete local dataset.

For Real-IAD, preserve the official JSONs and establish a physical-part group
key before creating any new splits. All views of one physical sample must
remain together across fitting, support, acquisition candidates, calibration
and evaluation; otherwise another view of a query can leak into its references.
The official example's evaluation command supplies a sample-key pattern that
removes the camera/view suffix. Its correctness and actual view completeness
still require validation against the downloaded metadata.

A fair first comparison with the existing single-view datasets should declare
the official top-view subset in advance and count each support image as one
shot. A separate multiview arm must state whether `k` counts physical parts or
images, how many views are supplied, and every image charged to acquisition.
Five views of one support part must not silently be treated as one image-shot.
Keep image-level, pixel-level and physical-sample-level results separate.

The official Real-IAD example includes single-view UIAD, multiview UIAD and
contaminated FUIAD protocols. Its loader expects JSON `meta`, `train` and `test`
sections, with sample fields `category`, `anomaly_class`, `image_path` and
`mask_path`. Notably, the example assigns training records label zero
unconditionally. That behavior is not evidence that a FUIAD training split is
normal-only. This project's normal-support requirement must be checked against
the declared UIAD metadata rather than inherited from the loader's label value.

## Resource readiness

The task coordinator reports five CPUs in affinity, a four-CPU cgroup quota, and no GPU. This audit
observed approximately 637 MiB free on the 32 GB `/workspace` overlay and 12.7 GiB
free on the separate 17 GB `/tmp` filesystem. These are snapshots, not reserved
capacity. Either advertised full Real-IAD image release exceeds available
storage before accounting for feature caches, maps and outputs.

Use the existing verified datasets for an explicitly approved, small protocol
with disk and runtime estimates. Keep full Real-IAD planned until its access,
dataset license, selected version, per-object archive sizes, expanded storage,
hashes, split schema and grouping are checked. Moving a cache into `/tmp` alone
does not make the full 53 GB release fit. The official UniAD example documents
an eight-GPU execution setup; it has not been installed or reproduced here and
is not a CPU runtime guarantee for the proposed method.

## Remaining unknowns

- Real-IAD current data license, completed access, archive inventory, exact
  sizes, hashes, official JSON bytes and view-group completeness.
- Which existing categories and images remain untouched by all earlier method
  choices and pilot evaluations; final roles require an exposure ledger.
- CPU runtime and output-storage needs of the proposed hybrid at its selected
  resolution. No new timing or accuracy experiment was run during this audit.

