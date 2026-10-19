# Saved-file text audit — 2026-10-19

Source snapshot: ennayriomar/newpr, branch `controlled-full-image-20261018`, commit `05c0fcea1b3289f0daf2f658c56b08c2848b71e9`. All source citations below are relative to `results/controlled_full_image_20261018/` at that commit; line numbers are 1-based original text lines, including blank lines. Links can be formed with `https://github.com/ennayriomar/newpr/blob/05c0fcea1b3289f0daf2f658c56b08c2848b71e9/results/controlled_full_image_20261018/<file>#L<line>`.

This is a text inspection and manual arithmetic audit. No experiment, model, test, bootstrap, hash calculation, or repository code was run. Only GitHub read operations and creation of this new audit branch/file were used. No source result file was edited. No change to any number is recommended.

## 1. README versus summary

**checked from files only; not re-run.** No mismatches found in the requested displayed macro metrics, paired mean differences, or interval endpoints, allowing normal rounding to the README's displayed precision. This is agreement between saved reports, not independent validation of the metrics. Sources: `README_results.md:7–26`; `summary.json:10–40,74–131`.

**checked from files only; not re-run.** Complete macro comparison below. Values are summary values rounded to four decimal places; each equals its README entry. Balanced accuracy is absent from the README macro table, so there is no README macro value to compare for that metric. Sources: `README_results.md:7–11`; `summary.json:11–40`.

| Method | Image AUROC | Pixel AUROC | AU-PRO | Image FPR | Recall | Pixel IoU | Pixel F1 | Source lines |
|---|---|---|---|---|---|---|---|---|
| baseline | .9344 | .9799 | .9300 | .0000 | .0000 | .2486 | .3866 | README:9; summary:12–19 |
| hybrid | .9407 | .9817 | .9378 | .0000 | .0144 | .2600 | .4037 | README:10; summary:22–29 |
| lambda_zero | .9344 | .9799 | .9300 | .0000 | .0000 | .2486 | .3866 | README:11; summary:32–39 |

**checked from files only; not re-run.** Complete paired comparison below. Each rounded difference and endpoint equals the corresponding README entry. Source summary fields are within `summary.json:74–131`; the README source line is given per row.

| Metric | Summary difference rounded to 5 places | Summary interval rounded to 5 places | README line | Result |
|---|---|---|---|---|
| image_auroc | +.00630 | [+.00071,+.01252] | 19 | match |
| pixel_auroc | +.00179 | [+.00044,+.00341] | 20 | match |
| au_pro | +.00781 | [+.00537,+.01051] | 21 | match |
| image_fpr | +.00000 | [+.00000,+.00000] | 22 | match |
| recall | +.01444 | [+.00000,+.03444] | 23 | match |
| balanced_accuracy | +.00722 | [+.00000,+.01722] | 24 | match |
| pixel_iou | +.01139 | [-.00356,+.02729] | 25 | match |
| pixel_f1 | +.01715 | [-.00202,+.03718] | 26 | match |

**checked from files only; not re-run.** The pooled hybrid false-alarm statement also matches: 0 false alarms / 2886 normal query/draw cases, FPR 0.0, and correlated cases. Sources: `README_results.md:13`; `summary.json:53–61`.

## 2. CSV macro arithmetic

**checked from files only; not re-run.** The CSV contains bottle rows as well as VisA rows. For comparison to the VisA summary, I use only the 12 VisA category rows per method, excluding bottle. Each VisA row already has draws=3; the category means therefore receive equal weight. Sources: `per_category.csv:1–40`; `summary.json:5–10`; `README_results.md:5,30`.

**checked from files only; not re-run.** Arithmetic convention and precision limitation: the following explicit sums use CSV operands rounded individually to six decimal places for auditable hand addition. Each mean is therefore within 0.0000005 of the mean of the full saved CSV decimals. The comparison column gives the saved summary rounded to six decimals. All saved summary means lie within that bound of these manual results. Thus this check finds no macro discrepancy at this precision; it does not certify equality of the final floating-point digits. Sources: `per_category.csv:5–40`; `summary.json:12–39`.

**checked from files only; not re-run.** Baseline operands are in category order candle, capsules, cashew, chewinggum, fryum, macaroni1, macaroni2, pcb1, pcb2, pcb3, pcb4, pipe_fryum, at CSV lines 5,8,11,14,17,20,23,26,29,32,35,38. These lines are the source of every baseline sum below; summary comparison sources are `summary.json:12–19`.

| Metric | Explicit hand addition and division | Saved summary (6 decimals) |
|---|---|---|
| image_auroc | (.957033+.939167+.962333+.991467+.959933+.953867+.722100+.924267+.936367+.908845+.994488+.962733)/12 = 11.212600/12 = .9343833333… | .934383 |
| pixel_auroc | (.993636+.983795+.985331+.996052+.939771+.996399+.992466+.991329+.961797+.970976+.959647+.987446)/12 = 11.758645/12 = .9798870833… | .979887 |
| au_pro | (.965206+.957251+.976633+.957932+.910674+.948492+.936262+.926664+.873124+.886641+.841484+.979093)/12 = 11.159456/12 = .9299546667… | .929955 |
| image_fpr | (0+0+0+0+0+0+0+0+0+0+0+0)/12 = 0 | .000000 |
| recall | (0+0+0+0+0+0+0+0+0+0+0+0)/12 = 0 | .000000 |
| balanced_accuracy | (.5+.5+.5+.5+.5+.5+.5+.5+.5+.5+.5+.5)/12 = 6/12 = .5 | .500000 |
| pixel_iou | (.280711+.370612+.168350+.406674+.105434+.140311+.102600+.388832+.277653+.326548+.175930+.239512)/12 = 2.983167/12 = .24859725 | .248597 |
| pixel_f1 | (.438344+.540205+.287956+.578187+.190747+.245966+.185387+.559884+.434604+.492134+.299160+.386135)/12 = 4.638709/12 = .3865590833… | .386559 |

**checked from files only; not re-run.** Hybrid uses the same category order, CSV lines 6,9,12,15,18,21,24,27,30,33,36,39. These lines are the source of every hybrid sum below; summary comparison sources are `summary.json:22–29`.

| Metric | Explicit hand addition and division | Saved summary (6 decimals) |
|---|---|---|
| image_auroc | (.960833+.947222+.970267+.992267+.966067+.969067+.755600+.930867+.939367+.897129+.993201+.966267)/12 = 11.288154/12 = .9406795 | .940679 |
| pixel_auroc | (.994232+.986244+.986698+.996673+.948379+.997262+.994564+.991978+.963527+.968828+.963879+.987831)/12 = 11.780095/12 = .9816745833… | .981675 |
| au_pro | (.967731+.966648+.982427+.962995+.921454+.958413+.947627+.935497+.881316+.889010+.859629+.980420)/12 = 11.253167/12 = .9377639167… | .937764 |
| image_fpr | (0+0+0+0+0+0+0+0+0+0+0+0)/12 = 0 | .000000 |
| recall | (0+0+0+.10666666666666667+0+0+0+0+0+0+0+.06666666666666667)/12 ≈ .17333333333333334/12 ≈ .014444444444444445 | .014444 |
| balanced_accuracy | (10×.5+.5533333333333333+.5333333333333333)/12 ≈ 6.0866666666666666/12 ≈ .5072222222222222 | .507222 |
| pixel_iou | (.268113+.358868+.210350+.378295+.131776+.176084+.115172+.396879+.271169+.321626+.177455+.314113)/12 = 3.119900/12 = .2599916667… | .259992 |
| pixel_f1 | (.422845+.527595+.347242+.548878+.232863+.299389+.205211+.568202+.426628+.486430+.301326+.477920)/12 = 4.844529/12 = .40371075 | .403711 |

**checked from files only; not re-run.** For lambda_zero, all eight metric operands equal the corresponding baseline operands category by category. Its sums and means are consequently exactly the same decimal expressions as the baseline table above; its saved summary also repeats the baseline values. Sources: baseline CSV lines 5,8,11,14,17,20,23,26,29,32,35,38 versus lambda_zero lines 7,10,13,16,19,22,25,28,31,34,37,40; `summary.json:12–19,32–39`.

## 3. Protocol contents and README description

**checked from files only; not re-run.** Frozen lambda is explicitly 0.25, and config SHA-256 is explicitly `de82b811f771708dfb8fa2f14eefb71cc7842a5241fb4365a3678b7c89320990`. A freeze timestamp is saved. These are recorded strings, not freshly verified hashes or proof of execution chronology. Sources: `protocol.json:2–4`; README lambda agrees at `README_results.md:3`.

**checked from files only; not re-run.** All candidate cutoff pairs are present; the locked decision is strict `score > cutoff`, with 0.05 calibration FPR targets and source-normal-only flags. Sources: `protocol.json:105–185`; README's corresponding description is `README_results.md:13,34,41`.

| Lambda | Image cutoff | Pixel cutoff | Protocol lines |
|---|---|---|---|
| 0.0 | 1.9804482460021973 | 1.179829716682434 | 105–124 |
| 0.1 | 2.1134612560272217 | 1.2640646696090698 | 126–144 |
| 0.25 | 2.343151807785034 | 1.3915828466415405 | 146–164 |
| 0.5 | 2.696584463119507 | 1.6066844463348389 | 166–184 |

**checked from files only; not re-run.** The stop rule is present: complete bottle and all 12 VisA categories with three support draws; stop without tuning if the paired interval includes zero or balanced-accuracy gain disappears under per-method calibration. The primary metric is mean per-category image AUROC difference, with calibrated balanced accuracy also required to improve. Sources: `protocol.json:69–70`.

**checked from files only; not re-run.** README agrees with saved protocol on geometry, one-shot/seeds, PCA variance, uniform gate, AD2-only selection and calibration, candidate-specific cutoffs, AU-PRO limit/grid, and listed deviations. Sources: `README_results.md:5,30,34–45`; `protocol.json:11–16,39–70,79–90`. The protocol additionally gives the precise selection tie-breaks and stop rule that the README does not spell out. Sources: `protocol.json:63,69–70`; `README_results.md:28,32–45`.

**checked from files only; not re-run.** The source-selection result records selected lambda 0.25, matching protocol and README. Source: `source_selection.json:192`; comparisons `protocol.json:3`; `README_results.md:3`. This does not establish that the selection procedure was executed correctly.

## 4. Leakage counts and IDs

**checked from files only; not re-run.** The saved leakage report states support=45, calibration=160, source_query=80, evaluation=2245, ID overlaps=0 and resolved-path overlaps=0. These are claims made by the saved report, not independently established merely by reading its passed=true field. Source: `leakage_check.json:2–11`.

**checked from files only; not re-run.** Calibration count matches by manual inspection: eight category blocks of 20 distinct image IDs, totaling 20+20+20+20+20+20+20+20=160. All inspected calibration records say dataset mvtec_ad2, split train and label normal. Source: `calibration_ids.json:2–1601`, with block ranges below; comparison `leakage_check.json:5`; protocol per-category setting `protocol.json:49`.

| Category | Record lines | Count |
|---|---|---|
| can | 2–201 | 20 |
| fabric | 202–401 | 20 |
| fruit_jelly | 402–601 | 20 |
| rice | 602–801 | 20 |
| sheet_metal | 802–1001 | 20 |
| vial | 1002–1201 | 20 |
| wallplugs | 1202–1401 | 20 |
| walnuts | 1402–1601 | 20 |

**checked from files only; not re-run — NOT VERIFIED.** The required comparison against support IDs in `per_image.jsonl` could not be completed. The GitHub line reader returned an empty content string when asked for lines 1–2, despite returning a file blob SHA. A separate raw-file read failed with a size/unsupported-content error. No content lines were obtained, so no `per_image.jsonl` line citation or support-ID count can honestly be supplied. This is an access limitation, not evidence that the file is empty or absent. The report's support=45 claim (`leakage_check.json:4`) remains unverified against that file. Likewise source_query=80 and evaluation=2245 (`leakage_check.json:6–7`) and both zero-overlap claims (`leakage_check.json:9–10`) have not been independently enumerated across all roles. Reading calibration path strings cannot verify filesystem path resolution.

## 5. Inconsistencies, omissions and limits of saved evidence

**checked from files only; not re-run.** Interpretation needs care: the saved image AUROC, pixel AUROC and AU-PRO paired intervals are positive, while recall and balanced-accuracy intervals include zero and IoU/F1 intervals cross zero. Thus the headline “no demonstrated benefit” must not be read as a statement that every saved metric interval includes zero. Sources: `README_results.md:3,19–28`; `summary.json:74–131`; stop-rule context `protocol.json:69–70`. This is an interpretation qualification, not a numeric mismatch.

**checked from files only; not re-run.** The stop rule's balanced-accuracy requirement says it “must also improve” but does not explicitly specify in that sentence whether a positive point estimate suffices or whether its interval must exclude zero. The saved point difference is positive, but its interval starts at zero. The overall saved stop decision therefore cannot be assessed as unambiguously compelled by that sentence alone. Sources: `protocol.json:69–70`; `summary.json:2–3,110–116`; `README_results.md:24,28`. No claim is made here that the stop decision is wrong.

**checked from files only; not re-run.** The README omits the literal config hash, numerical cutoff values, full selection tie-break rule and full stop rule. Those details are saved in protocol, so they are omissions from the README, not absent experiment records. Sources: `README_results.md:32–45`; `protocol.json:4,63,69–70,105–185`.

**checked from files only; not re-run.** Claims about pre-inference recording/sealing and trying no new settings are historical assertions that this audit does not establish. The protocol supplies a freeze timestamp and hash strings, but those alone cannot prove absence of unrecorded activity. Sources: `README_results.md:28,34`; `protocol.json:2–4,92–103`. They are not labeled false or unsupported by every possible repository file; their complete provenance remains unchecked.

**checked from files only; not re-run.** A post-freeze caption amendment is explicitly saved and scoped as presentation-only. Its timestamp is later than the protocol freeze timestamp. This is disclosed, not evidence of numerical tuning. Sources: `protocol.json:2`; `presentation_caption_amendment.json:2–5,9–14`.

**checked from files only; not re-run.** The README's “unit-tested” claim does have a saved log: it records 28 tests and OK. This audit only read that log and did not run those tests. Sources: `README_results.md:95`; `unit_tests.log:1–33`.

**checked from files only; not re-run.** The reproducibility file contains saved identical-score flags and encoder-inference-repeated flags, for example the bottle and candle records. These are saved assertions from an earlier run, not reproduction performed during this audit, nor proof that every image was repeated. Source: `reproducibility.json:2–36`.

**checked from files only; not re-run.** Weight verification cannot be independently established from a path and hash string: protocol references an external checkpoint path and source-cache directory, while README labels weights real-weights verified. Sources: `protocol.json:7–10`; `README_results.md:96`. Checkpoint bytes were not inspected or hashed in this audit. This is unverified evidence, not a finding that the checkpoint is missing.

**checked from files only; not re-run.** README claims saved per-category intervals, bootstrap multiplicities, sampled curves and raw figure maps/metadata. This audit did not inspect every such artifact or binary; it therefore does not certify complete coverage or mark any uninspected artifact missing. Sources for these claims: `README_results.md:28,49–87`. No definite “claimed without any saved file” conclusion is supported by the limited files inspected. In particular, an unreadable file is not a missing file.

## Audit disposition

**checked from files only; not re-run.** README/summary comparisons: no displayed numeric mismatches found (`README_results.md:9–26`; `summary.json:12–39,74–131`). CSV/summary: consistent within the explicit manual rounding bound, with full-final-digit equality not certified (`per_category.csv:5–40`; `summary.json:12–39`). Protocol required fields: present (`protocol.json:2–4,63,69–70,105–185`). Calibration count: matches (`calibration_ids.json:2–1601`; `leakage_check.json:5`). Support-ID and full leakage comparison: incomplete because `per_image.jsonl` contents were not obtainable; the saved claims at `leakage_check.json:4,6–10` remain unverified. This audit is not a complete leakage certification.
