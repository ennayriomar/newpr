# Support-Adequacy-Aware Few-Shot Anomaly Localization: Milestone 3 research report

The predeclared feasibility gate failed. Learned acquisition improved the declared mean counterfactual loss relative to simple selectors in this small pilot, but produced four newly missed inspection records for two unique VisA defects at locked cutoffs. Every missed record returned the action normal. Acquisition also reduced defect-pixel recall and did not establish a consistent missing-support false-alarm effect. No full experiments were authorized by the gate. No model or cutoff was tuned after observing these outcomes.

The report uses executed artifact JSON and the generated benefit_summary.csv. Earlier M1/M2 results are historical evidence, separate from the new M3 run. all_tests.log records a fresh 97-test successful run; these unit/contract tests are separate from real pretrained-weight/data experiments. Completed artifact validation, two fresh-cache real-weight probes and a completed-run resume verification also passed; their scopes are recorded below.

**Repository audit and prior evidence.** repository_audit.json preserves the before-extension audit: 44 existing tests passed freshly, benefit learning and missing-support experiments were absent, and reliability/intervention metrics were incomplete. The safe_iad interfaces, working backbone and existing scoring adapters were retained.

| Prior component | Recorded evidence | Scope |
| --- | --- | --- |
| Dataset/weight verification | 20089 retained real images; verified DINOv2 ViT-B/14 pretrained loading, frozen parameters/eval mode and deterministic extraction | Historical verification; no random fallback |
| M1 internal NN baseline | 24 summaries, 192 records, 16 unique queries; k=1,2,4,8 | Historical real-data feasibility, zero acquisition |
| M2 counterfactual/policy pilot | 384 source target rows; 240 policy inspection records from 16 unique queries | Historical k=1,b=0/1; no learned benefit model |
| Separate strict hybrid/scoring adapters | 720 evaluation records, 20 unique evaluation queries | Historical scoring-core variants; full published recipes not reproduced |
| AD2 prediction export | 36 public float16 TIFF/binary PNG pairs passed official per-file checks | Historical public preview; complete private submission correctly rejected |

Prior adapter parity covers supported official AnomalyDINO/SubspaceAD scoring cores at declared common settings. It does not establish faithful reproduction of published full recipes. The M3 detector is the existing internal DINOv2 normalized-patch NN detector, not PatchCore or a newly reproduced external method.

**Method and assumptions.** For fixed frozen patch features z, raw defect evidence is d(p,S)=min over normal support patches s of ||normalize(z(p))−normalize(z(s))||₂. The image score averages the largest one percent of patch distances. M3 preserves the M2 RGB bicubic resize to 224×224 and final-layer 16×16 patch-grid contract; it can alter image aspect ratio. Native maps use bilinear restoration. Metrics consume float32 native maps; saved maps explicitly use float16. This differs from the separate aspect-preserving multilayer hybrid pipeline.

The offline target is U(q,S,r)=L(f(q,S),y)−L(f(q,S∪{r}),y). L is class-balanced pixel margin MSE at margin 1 in uncalibrated NN-score units: normal-region mean m² and defect-region mean max(0,1−m)² receive equal weights when both regions exist. Real normal training queries have zero masks; deterministic source-image cut/paste queries provide synthetic masks. Their realism as industrial defects is unverified. Final-test defect labels do not construct targets. Added references remain verified normal training images.

The 19 observable summaries include distances, dispersion, distinct-reference contributions, LOO sensitivity with explicit k=1 missingness, candidate/global distances and label-free candidate score changes. The learned U estimate is a signed scalar, not a spatial benefit field. A_support is a predeclared untrained sigmoid of diagnostics, separate from the raw defect map; it is not a calibrated probability or validated adequacy event. The three-way action preserves the raw defect-evidence flag when review is requested. Defect evidence is never multiplied by adequacy. Logistic/MLP adequacy fitting and full requested diagnostic ablations remain unrun.

**Source-only learning.**

| Targets | Candidate rows | Original normal source images | Negative-U rows | Source groups with negative U |
| --- | --- | --- | --- | --- |
| Training | 1536 | 48 | 9 | 6 |
| Held-out normal/synthetic validation | 384 | 12 | 0 | 0 |

The training sources are mvtec_ad:carpet, mvtec_ad:grid, visa:candle, visa:cashew. Each original image, its synthetic derivative and all its candidate/shot rows stay together in grouped source CV. Feature and target scalers are fitted inside each training fold. This is source-image CV, not category-disjoint CV; rows sharing support memories remain dependent. Harmful supervision remains sparse despite broadening from M2. For normal queries, raw NN loss cannot increase when the normal bank expands, so positive normal-query U partly follows the detector/loss definition.

| Model | Source-group OOF MSE | Primary selected by source CV | Held-out normal/synthetic RMSE | Mean candidate Spearman |
| --- | --- | --- | --- | --- |
| ridge | 0.00007909 | no | 0.009514 | 0.9008 |
| mlp | 0.00007347 | yes | 0.007718 | 0.9127 |

The MLP has 16 tanh hidden units with fixed hyperparameters. Held-out validation contains 12 original normal images plus synthetic derivatives and zero negative candidate targets; its favorable rankings do not evaluate harmful interventions or real-defect reliability. Those validation outputs did not choose the primary model.

**Locked paired real-data pilot.** MVTec AD cable and VisA macaroni2 use 8 unique native test images from declared validation categories (two normal and two anomalous per category), reused across seeds [0, 1, 2] and k=[1, 2]. These produce 48 paired query/support/k cases, six policies, and 288 policy inspection records. First-sorted, label-stratified query sampling was predeclared. These records are correlated repetitions of eight images, not independent new queries or full-benchmark results.

Each acquisition policy accesses the same 8-image normal candidate pool and adds exactly one reference per query; the no-acquisition control adds zero. Initial supports, pools, queries, seed, preprocessing and detector settings are paired. This is budgeted Protocol B, not strict k-shot learning. Learned selection probes every candidate patch memory and is charged accordingly; global policies scan global descriptors. Shared pilot timings are not isolated deployment latency benchmarks. Oracle uses evaluation masks offline and is unattainable at deployment. It maximizes the declared loss benefit, not AUROC or AP.

Normal training images from reserved mvtec_ad/capsule, visa/fryum categories supply cutoffs: each seed holds out four normals, with 12 unique calibration query images per dataset. Supports exclude all reserved calibration queries. Mean+3std image/pixel cutoffs remain locked before and after acquisition. Dataset-level category-disjoint transfer of these cutoffs offers no false-alarm guarantee. Native validation masks enter only after all deployable selections. No final categories or private data were evaluated.

Values below are means across three support-draw episodes within each category. Harm counts sum 12 repeated query/support inspection records per dataset/k/policy; harmful means U<−1e−8. IoU uses pooled pixel counts within an episode before averaging episodes. Missed/false-alarm rates use the locked detector cutoffs.

| Dataset/category | k | Policy | Mean U | Image AUROC | Pixel AP | AU-PRO | IoU | Miss rate | False-alarm rate | Harm /12 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mvtec_ad/cable | 1 | none | 0.000000 | 1.0000 | 0.5091 | 0.9665 | 0.0625 | 0.3333 | 0.1667 | 0 |
| mvtec_ad/cable | 1 | random | 0.025377 | 1.0000 | 0.5482 | 0.9692 | 0.1005 | 0.3333 | 0.0000 | 0 |
| mvtec_ad/cable | 1 | nearest_global | 0.045589 | 1.0000 | 0.5351 | 0.9719 | 0.1348 | 0.3333 | 0.0000 | 0 |
| mvtec_ad/cable | 1 | diversity | 0.014042 | 1.0000 | 0.5403 | 0.9676 | 0.0975 | 0.5000 | 0.0000 | 0 |
| mvtec_ad/cable | 1 | learned | 0.046888 | 1.0000 | 0.5184 | 0.9677 | 0.1426 | 0.3333 | 0.0000 | 0 |
| mvtec_ad/cable | 1 | oracle | 0.048162 | 1.0000 | 0.5373 | 0.9732 | 0.1439 | 0.3333 | 0.0000 | 0 |
| mvtec_ad/cable | 2 | none | 0.000000 | 1.0000 | 0.5456 | 0.9750 | 0.0284 | 0.0000 | 0.3333 | 0 |
| mvtec_ad/cable | 2 | random | 0.014308 | 1.0000 | 0.5584 | 0.9736 | 0.0344 | 0.0000 | 0.0000 | 0 |
| mvtec_ad/cable | 2 | nearest_global | 0.029620 | 1.0000 | 0.5520 | 0.9748 | 0.0453 | 0.0000 | 0.0000 | 0 |
| mvtec_ad/cable | 2 | diversity | 0.007954 | 1.0000 | 0.5418 | 0.9737 | 0.0321 | 0.0000 | 0.1667 | 0 |
| mvtec_ad/cable | 2 | learned | 0.031122 | 1.0000 | 0.5408 | 0.9721 | 0.0486 | 0.0000 | 0.0000 | 0 |
| mvtec_ad/cable | 2 | oracle | 0.032230 | 1.0000 | 0.5544 | 0.9759 | 0.0482 | 0.0000 | 0.0000 | 0 |
| visa/macaroni2 | 1 | none | 0.000000 | 1.0000 | 0.0230 | 0.8813 | 0.0067 | 0.6667 | 0.0000 | 0 |
| visa/macaroni2 | 1 | random | 0.026253 | 1.0000 | 0.0389 | 0.9246 | 0.0157 | 0.8333 | 0.0000 | 0 |
| visa/macaroni2 | 1 | nearest_global | 0.033714 | 1.0000 | 0.0270 | 0.9074 | 0.0196 | 0.8333 | 0.0000 | 0 |
| visa/macaroni2 | 1 | diversity | 0.019823 | 1.0000 | 0.0263 | 0.9070 | 0.0122 | 0.6667 | 0.0000 | 0 |
| visa/macaroni2 | 1 | learned | 0.035188 | 1.0000 | 0.0286 | 0.9123 | 0.0201 | 0.8333 | 0.0000 | 0 |
| visa/macaroni2 | 1 | oracle | 0.037734 | 1.0000 | 0.0464 | 0.9407 | 0.0208 | 0.8333 | 0.0000 | 0 |
| visa/macaroni2 | 2 | none | 0.000000 | 1.0000 | 0.0261 | 0.8927 | 0.0060 | 0.1667 | 0.1667 | 0 |
| visa/macaroni2 | 2 | random | 0.013033 | 1.0000 | 0.0403 | 0.9177 | 0.0106 | 0.5000 | 0.0000 | 0 |
| visa/macaroni2 | 2 | nearest_global | 0.019014 | 1.0000 | 0.0338 | 0.9250 | 0.0139 | 0.6667 | 0.0000 | 1 |
| visa/macaroni2 | 2 | diversity | 0.009071 | 1.0000 | 0.0287 | 0.9135 | 0.0085 | 0.5000 | 0.1667 | 0 |
| visa/macaroni2 | 2 | learned | 0.019566 | 1.0000 | 0.0352 | 0.9235 | 0.0151 | 0.6667 | 0.0000 | 1 |
| visa/macaroni2 | 2 | oracle | 0.021511 | 1.0000 | 0.0450 | 0.9421 | 0.0146 | 0.5000 | 0.0000 | 0 |

AU-PRO integrates pooled normal-pixel FPR over [0,0.3], divides by 0.3, and weights every 8-connected defect component equally. It samples at most 256 distinct native-score rank thresholds plus endpoints and interpolates the FPR boundary; it is a sampled curve estimate. Pixel AP/AUROC use input float32 maps without score quantization. Risk–coverage artifacts define risk as locked-cutoff 0/1 classification error, accept complete confidence-tie groups, and use a right-step AURC integral. Confidence is an untrained diagnostic ranking, not a probability.

The image AUROC of 1.0 in these tiny strata coexists with severe locked-cutoff misses. VisA k=2 learned acquisition raises missed-defect rate from 0.1667 to 0.6667. Improved mean U or localization overlap therefore cannot be equated with reliable defect detection.

**Preservation and stopping decision.**

| Dataset | k | Utility pass | Harm pass | Preservation pass | New image misses | Mean defect-pixel recall change | Mean defect IoU change |
| --- | --- | --- | --- | --- | --- | --- | --- |
| mvtec_ad | 1 | True | True | False | 0 | -0.009193 | 0.069138 |
| mvtec_ad | 2 | True | True | False | 0 | -0.000597 | 0.026362 |
| visa | 1 | True | True | False | 1 | -0.172862 | 0.022182 |
| visa | 2 | True | True | False | 3 | -0.061110 | 0.012877 |

All per-dataset/k utility and harm checks passed, while all preservation checks failed. The four new image misses correspond to two unique VisA defect images, macaroni2/Data/Images/Anomaly/000.JPG and 001.JPG, across repeated support draws/k. Every one of these four learned-policy records returned the action normal. They are correlated inspection events, not four independently sampled defects. Defect-pixel recall decreased on every dataset/k slice despite positive mean IoU changes. The gate requires no new image misses, nonzero initial defect detection, no observed defect-pixel recall loss in any evaluated anomalous case (all cases are checked, not only the mean), and no mean defect-IoU deterioration. Overall advance_to_full_experiments=false.

**Matched missing-support stress.** Groups use only allowed normal-training global features. They are proxy appearance clusters, not semantic or known lighting modes. Omitted supports and their matched controls use the same queries, pool, seed and k; exactly one initial reference is replaced by a query-group reference in the control. The 144 omitted and 144 control policy inspection records reuse the same 12 unique normal training query images across k/conditions/policies. Each dataset/k check below has six normal query/support inspections.

| Dataset | k | Omitted-support false alarms | Matched-control false alarms | After learned acquisition | Omission increased FPs | Acquisition reduced FPs |
| --- | --- | --- | --- | --- | --- | --- |
| mvtec_ad | 1 | 0/6 | 0/6 | 0/6 | False | False |
| mvtec_ad | 2 | 2/6 | 2/6 | 1/6 | False | True |
| visa | 1 | 0/6 | 1/6 | 0/6 | False | False |
| visa | 2 | 1/6 | 1/6 | 1/6 | False | False |

No matched slice showed increased false alarms from omission. Only MVTec k=2 showed a reduction after learned acquisition, and its covered control initially had the same false-alarm count as omission. This setup did not establish the proposed missing-normal-coverage mechanism. The small slice and proxy grouping do not falsify that mechanism generally. missing_support_gate_pass=false.

**Conditional paired uncertainty.** The following values are copied from evaluation/gate.json. They compare learned U with each simple policy at equal added-reference budget, averaging the two fixed dataset/category strata equally.

| Comparator | k | Mean paired U difference | 95% percentile interval |
| --- | --- | --- | --- |
| random | 1 | 0.015222819143673405 | [0.007993604217093286, 0.021274506217741868] |
| random | 2 | 0.011673457736227041 | [0.00508993291805382, 0.01713053539521448] |
| nearest_global | 1 | 0.0013863848677525916 | [-0.0010503300155202543, 0.004761255501459039] |
| nearest_global | 2 | 0.001026832226974269 | [-0.0009557693789247423, 0.00412147409903506] |
| diversity | 1 | 0.024105337157379836 | [0.01175418193888618, 0.03878366179657556] |
| diversity | 2 | 0.016831470100441948 | [0.008290679609247797, 0.02700486914836801] |

Intervals use 2,000 paired crossed-bootstrap resamples, independently resampling query IDs and seed-defined support/pool/calibration draws within each dataset/category. Each stratum contains four query IDs and three draw units (12 paired rows), all flagged limited replication. Categories remain fixed; pixels and candidate rows are not resampling units. Intervals are conditional pilot uncertainty over observed units, not confidence in unsampled categories, full benchmarks or deployment prevalence. Both nearest-global macro intervals cross zero. Positive point differences do not establish robust learned-selector superiority. No multiple-comparison correction or population significance claim is made.

**Implemented, tested and evaluated status.** status_table.csv distinguishes code/contracts, actual real-data evaluations and deferred work. The 97 passing tests establish local contracts, not research correctness or production reliability. Source-only benefit fitting, label-blind policies, budgets, missingness, native map restoration, recorded calibration provenance, dependent statistics and explanation-away diagnostics ran concretely. The completed artifact audit and limited fresh-cache reproduction are documented below.

**Completed verification and reproduction.** validation.json reports status passed for all 576 prediction records and 39 completed-stage ledgers. It verified support budgets, six-policy pairing, source-only model selection, normal-only category-disjoint cutoff provenance, oracle-label isolation, LOO missingness, finite float16 native exports, preserved raw defect maps/evidence flags, and absence of final-category/private results. It read 672 native map exports and 672 diagnostic exports. The audit performed 3,787 output-hash checks, 7,467 input-hash checks and 862 implementation-hash checks, with 1,903 unique output files and 547 unique input files hash-verified. Repeated checks across nested ledgers are not extra unique files or independent observations. This is a completed artifact/provenance/contract audit; it does not independently re-extract every backbone feature or rerun all float32 metrics.

real_weight_reproduction.json reports two passed fresh-cache probes, one actual anomalous query per main dataset: cable/test/bent_wire/000.png at seed=0,k=1 and macaroni2/Data/Images/Anomaly/000.JPG at seed=0,k=2. These newly recomputed frozen-backbone features matched float32 features bitwise; stored pre/post float16 maps and adequacy maps matched bitwise; image scores, selected reference and signed benefit matched exactly. The VisA probe retained its detected-to-missed failure. This checks two query cases only, not a full independent rerun of all episodes or a cross-hardware reproducibility guarantee.

completed_resume.log records completed artifact verification and the unchanged failed feasibility gate after repeating the evaluation command. This verifies completed-run reuse, not a new experiment. all_tests.log records 97 freshly passing unit/contract tests; synthetic tests remain separate from real-data evidence.

**Unverified work and supported claims.** This supports a reproducible small learned-benefit feasibility experiment and a negative preservation/stress finding. It does not establish calibrated probabilities, a validated support-adequacy event, spatial U_ref, causal separation of missing support from defects, theoretical guarantees, novelty, state-of-the-art performance, production readiness or publication acceptance. Stage4 AD2 lighting robustness, full benchmarks, private-server evaluation, source-only AD2-to-VisA transfer, probability calibration/Brier/NLL/ECE, complete requested ablations, spatial benefit learning and sequential b=2/4 acquisition are unimplemented or unrun. LOCO remains optional and unrun. The negative gate stopped expansion; neither this model nor its cutoff was retuned after the gate.

Reproduction commands for the declared pilot (dataset/checkpoint paths and setup are documented in the bundle):

```bash
PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m safe_iad.build_benefit_targets --config /workspace/tools/configs/milestone3.json
PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m safe_iad.train_benefit --config /workspace/tools/configs/milestone3.json
PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m safe_iad.run_benefit_pilot --config /workspace/tools/configs/milestone3.json
/workspace/venvs/safe_iad/bin/python /workspace/tools/plot_benefit_pilot.py --results /tmp/safe_iad_milestone3/evaluation/episodes.json --output /tmp/safe_iad_milestone3/benefit_summary.png
```

The prior strict fixed-shot full-plan entry point is `python -m safe_iad.run_pipeline --config configs/experiment_full.yaml`; it is unrun and distinct from a complete M3 learned-acquisition benchmark. There is no validated Stage4 learned-acquisition full command to claim as completed. The feasibility gate requires stopping before that expansion.

Artifact sources: repository_audit.json; targets/summary.json and split_manifest.json; models/training_report.json and heldout_validation.json; evaluation/config.json, calibration.json, split_manifest.json, episodes.json, gate.json and provenance.json; validation.json, real_weight_reproduction.json, completed_resume.log and all_tests.log; benefit_summary.csv and native/matched-stress PNG/PDF plots. Existing M1/M2/hybrid validations referenced above remain historical files under /workspace/reports and are bundled separately where available.
