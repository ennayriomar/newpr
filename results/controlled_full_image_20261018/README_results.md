# Controlled experiment in progress

This branch preserves the fixed source-only design and actual execution artifacts.
The complete VisA benchmark has NOT finished and no benefit is claimed here.
The source-plan hash and scoring implementation are recorded before target inference.
The chosen lambda will be sealed in protocol.json before any target scoring.

Methods are an internal baseline and adapted implementations, not official paper
reproductions. Full-image fields/GT are resized to448x448. AD2 train normals alone
calibrate per-method cutoffs; AD2 public-test queries alone select lambda. No
target image calibrates a threshold or selects a parameter. Full data roles,
source budgets, metrics, bootstrap rules, deviations and stop conditions are in
experiment_config.json and source_plan.json. Progress artifacts contain only
commands actually executed; partial source results are not target performance.

MVTec-derived maps/features retain CC BY-NC-SA4.0 (MVTec Software GmbH;
Bergmann et al., CVPR2019; Heckler-Kram et al., arXiv2503.21622,2025).
VisA-derived maps/features retain CC BY4.0 (Zou et al., ECCV2022).
Official Meta DINOv2 foundation weights and native dataset images are separate.
