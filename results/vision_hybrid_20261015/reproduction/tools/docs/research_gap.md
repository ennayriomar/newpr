# SAFAL research gap and testable hypothesis — Phase A

Project: **Support-Adequacy-Aware Few-Shot Anomaly Localization for Reliable
Industrial Inspection**. Working method: **SAFAL**.

This document completes a foundation assessment only. It proposes research
questions and requirements for later phases; it does not implement an adequacy
estimator, establish novelty, start new experiments or draft manuscript results.
The verified sources and bounded search evidence are in
[literature_review.md](literature_review.md) and
[source_verification.json](source_verification.json). Runtime/data constraints
and the staged development plan are documented separately.

## What the verified methods already provide

[SubspaceAD](https://github.com/CLendering/SubspaceAD) models frozen normal patch
features with an unwhitened PCA subspace and scores squared reconstruction
residuals. Its verified official benchmark recipe includes a giant/registers
backbone, high-resolution inputs and support augmentation. The current project's
smaller common-backbone scoring-core adapter is an explicitly modified variant.

The relevant [VisionAD](https://github.com/Qiqigeww/VisionAD) accompanies
[*Search is All You Need for Few-shot Anomaly Detection*](https://arxiv.org/abs/2504.11895).
It combines frozen multilayer features, normalized patch retrieval, augmented
support/query views and visual memory. Its inspected large/registers recipe
differs from the current ViT-B/14, 224-pixel prototypes. Its advertised
visualization evaluator does not return measured numerical accuracy at the
verified revision, and its source redistribution license is unresolved.

PCA residuals, nearest-neighbor search, normal feature-density/coverage
diagnostics, augmentation, calibration and rejection are established building
blocks. Combining them does not itself establish a new contribution. Existing
PatchCore, PaDiM, AnomalyDINO and selective-prediction references are identified
in the literature review; their relevance must be assessed through their actual
definitions rather than through method names.

The bounded search found no verified published method named
“SubspaceAD–VisionAD,” but name searches and blocked academic endpoints cannot
establish absence of related adaptive hybrids. A comprehensive novelty claim
remains unsupported. The VisionAD licensing limitation restricts source reuse;
it is neither evidence of a research gap nor permission to vendor its code.

## The narrower unresolved question

The proposed hypothesis is that **an explicitly defined estimate of relevant
normal-support coverage can condition fusion of verified subspace and retrieval
branches, improving localization and inspection reliability compared with
component-only and fixed-fusion controls under matched information budgets**.

This hypothesis has several separate burdens of evidence:

- Define what support adequacy means and validate its measurement independently
  of merely naming an entropy, density, distance or disagreement score.
- Establish whether the estimator detects missing legitimate normal variation
  rather than treating every true defect or distribution shift as inadequate
  support.
- Show that adequacy-conditioned fusion adds useful information beyond branch
  scores, fixed weights, generic uncertainty and support cardinality.
- Measure any gain together with false alarms, missed defects, pixel recall,
  localization quality, review coverage and cost. An improved average alone does
  not justify a reliability claim.

Neither branch is intrinsically a pure “defect” or “support insufficiency”
measurement. Both can respond to legitimate unseen normal appearance, and both
can sometimes explain or match an actual defect. Conditional fusion might help,
do nothing or worsen defect preservation. Its direction and benefit must not be
assumed from the branch labels.

## An operational adequacy event is still required

Before Phase C, specify the event or criterion that the intended `A_support` is
to estimate. It must distinguish four concepts:

| Quantity | Intended meaning | What it does not establish |
| --- | --- | --- |
| Support adequacy | Coverage of relevant legitimate normal appearance by the permitted support set | A query's anomaly label or prediction correctness |
| Anomaly evidence | Departure from a fitted normal representation | Why the departure occurred |
| Error/confidence estimate | A defined decision or localization error event under a locked rule | Reference-set completeness |
| Acquisition benefit | Change in a specified loss after adding a permitted normal reference | A universal adequacy probability |

Choose explicitly between support-only adequacy `A(S)` and query-conditioned
adequacy `A(S,q)`. A support-only diversity score cannot by itself identify which
normal mode a particular query requires. A query-conditioned score may mistake
a defect for uncovered normal variation. These are different estimands and need
different controls; neither is defined simply by bounding a number in `[0,1]`.

A possible later validation design is to predefine legitimate normal-mode
groups using audited acquisition/context information, then omit and restore
normal references from one group while keeping query identities, labels,
initial reference counts and allowed added-reference budgets matched. Such
groups require justification. Clusters computed from training features are a
coverage proxy, not automatically ground-truth industrial appearance modes.
Existing datasets may lack the metadata needed for an external adequacy label;
that limitation must remain explicit.

A second possible target is a predeclared counterfactual criterion: whether
adding an eligible normal reference materially changes a specified normal-query
loss or coverage statistic. Define the reference universe, loss, tolerance,
support/query exclusion and intervention budget in advance. A criterion built
from the same detector being evaluated is model-relative and potentially
circular; it does not establish independently valid reference sufficiency.
Synthetic defect queries must retain their provenance and cannot stand in for
native industrial defect validity.

Validate adequacy on held-out normal queries and controlled omission/coverage
conditions, then separately test behavior on genuine defects. Support and
candidate images must be verified training normals. Native evaluation masks may
measure offline outcomes, but must not construct deployed diagnostics, select
references, tune fusion or fit thresholds. A correctness/coverage curve measures
decision reliability; label it accordingly rather than calling it adequacy
precision. k=1 leave-image-out stability is undefined/missing, not zero or perfect
stability. Entropy, density and reference counts require construct validation.

## Fair adaptive-versus-fixed comparisons

First establish Phase B branch fidelity. Keep exact reference recipes distinct
from paired common-backbone variants, with explicit layers, normalization,
geometry, augmentation, map processing and image aggregation. Do not attribute
published recipe scores to simplified branch implementations.

For later controlled fusion, preserve raw branch maps and normalize their
incompatible score units using declared development/normal calibration data.
Do not use per-query or evaluation-set min/max scaling. Lock normalization,
weights, cutoffs and model selection before final evaluation. Compare each
branch, fixed average or another predeclared fixed rule, and adaptive fusion on
the same normal references, queries and support draws.

Count original support images, augmented views, extra calibration normals,
candidate-image access and acquisition separately. A detector with k references
and additional target-normal calibration images is not a total-k-image protocol.
An adaptive model trained on source categories or synthetic supervision has an
additional information budget that the baseline description must disclose.

Fit source-meta parameters only on permitted development data with image/parent
group separation. Reserve distinct validation choices and calibration inputs;
keep final categories/images locked. Normal-only score calibration does not
automatically calibrate an adequacy probability or conditional error rate.
Probability claims need a defined event and independent outcome calibration.
Previously inspected categories or query images must be listed in an exposure
ledger and cannot be relabeled as pristine final holdouts.

An independently normalized max union is a useful fixed control, not evidence
of adaptive fusion or novelty. With positive, fixed branch cutoffs, its binary
union preserves each branch's alert but can increase false positives. It does
not guarantee better ranking, localization or accuracy. Changing those cutoffs
or averaging pixel maps changes the preservation argument. Adaptive weighting
must also be tested for suppressing genuine defect evidence; a low adequacy
estimate must not silently erase raw maps or missed-defect events.

## What earlier negative and preliminary work establishes

The retained strict hybrid pilot produced weak reliable-decision evidence: its
entropy/density diagnostic accepted many incorrect decisions and rejected some
well-ranked inspections. Those repeated-query observations challenge that
particular diagnostic; they do not prove all adequacy estimation impossible.

The historical M3 acquisition pilot improved its declared mean utility but
introduced four correlated newly missed defect inspection records, reduced
defect-pixel recall and failed the proposed matched missing-support mechanism
check. Its negative stopping decision and exact scope remain in the archived
report. It is evidence against advancing that acquisition configuration, not
permission to tune on those locked outcomes or a general theorem about SAFAL.

The three earlier preliminary PCA/search/fixed-union variants do not fulfill
the newly requested adequacy-conditioned architecture. They do not establish
faithful published branch reproduction, an externally justified adequacy event,
validated adaptive fusion or inspection reliability. Their source and outputs
remain preserved as preliminary material; they are not a substitute for the
new Phase A–B foundation and parity requirements.

## Phase boundary and practical limits

Phase A ends with these verified foundations and an explicit unresolved
hypothesis. Proceeding through Phase B requires source/recipe contracts, license
handling, independently measured metrics, spatial alignment and actual small
branch checks. Full Phase E comparisons must not precede that foundation or a
complete, audited small adaptive-versus-fixed experiment.

The audited environment has four CPU equivalents of quota, five CPUs in
affinity and no GPU. It retains 20,089 images across MVTec AD, VisA and public
MVTec AD 2; Real-IAD is absent. Workspace storage is nearly full and temporary
storage is also bounded. These resources and dataset terms do not support a
claim that full large/giant-backbone or private-server benchmarks are ready.
See [dataset_readiness.md](dataset_readiness.md) and
[phase_a_report.md](phase_a_report.md) for precise audited scope.

No new implementation or experiment is initiated by this document. Novelty,
SOTA, calibrated reliability, publication suitability and journal acceptance
remain research outcomes to establish, not promised deliverables.
