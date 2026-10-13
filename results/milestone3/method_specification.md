# Milestone 3: benefit prediction and controlled missing support

The frozen DINOv2 patch nearest-neighbor detector remains fixed. For normalized
query patches q and support memory B(S), defect evidence is
M_defect(p) = min_{s in B(S)} ||q_p - s||_2. Its image score is the mean of the
largest ceil(0.01 P) patch scores. Normal-bank expansion can lower true-defect
scores, so lower scores do not establish improved inspection.

Support diagnostics D(q,S) include nearest/mean-neighbor distances, distinct
reference contributions, local dispersion, global/local disagreement and
leave-one-reference-out sensitivity. At one support image, leave-one-out
sensitivity is undefined and its valid mask is false. A configurable empirical
adequacy field may summarize these diagnostics; it is not a calibrated
probability. Neither the field nor predicted benefit multiplies defect evidence.

Offline supervision is U(q,S,r) = L(f(q,S),y_q) - L(f(q,S union {r}),y_q), using
the declared image-margin or class-balanced pixel-margin loss. Training queries
are source-training normals with zero masks and explicitly synthetic edits of
source-training normals. Validation and calibration have declared disjoint
category/image roles. Native final-test masks enter offline evaluation only.

A small linear regressor and optional small MLP estimate signed U from the
19 inference-only query/support/candidate diagnostic summaries. This is a
scalar loss-benefit prediction, not a probability of defect, correctness or
support adequacy. Candidate nearest-neighbor/prospective-drop inputs require
patch probes of every scanned candidate; those scans and their time must be
charged separately from selected-reference counts and backbone extraction.

One-step acquisition compares none, random, nearest-global, diversity, learned
benefit and an unattainable offline oracle. All share exactly the same initial
support, permitted normal candidate pool, query, seed, preprocessing and base
detector. The selected detector bank adds at most one candidate image per
inspection. The oracle uses evaluation labels and never trains/selects the
learner or chooses thresholds. Record pre/post evidence, diagnostics, selected
IDs, signed observed benefit and harmful interventions. Missed-defect and
defect-region score changes remain separate from loss benefit.

Missing-support stress groups use deterministic KMeans of L2-normalized frozen
global descriptors from caller-verified normal training data. A chosen group
is absent from initial supports. Queries are held-out normal training images
from that group; the disjoint candidate pool includes another image from it.
All grouping features are counted, including held-back query descriptors used
to construct the stress condition; queries never enter detector memory.
Clusters are proxy appearance groups, not semantic modes or lighting labels.
This API rejects insufficient data rather than reducing budgets silently.

Three-way actions need separately declared validation/calibration thresholds;
benefit predictions alone do not justify a reliable normal/defective/unresolved
decision. Stop before full experiments if learned acquisition fails against
simple selection at equal reference budgets or harms defect preservation.
Small correlated pilot episodes do not establish production reliability,
probability calibration, state-of-the-art performance or statistical guarantees.
