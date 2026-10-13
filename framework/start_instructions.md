# Current SAFAL v0.5.0 startup

The user's latest request authorizes the full executable SAFAL model after the
historical Phase A audit. Current implementation is documented in
`docs/full_model.md`. Use the existing isolated checkout; do not create a Git
worktree unless the user explicitly requests one. Preserve all earlier code,
datasets, fitted models and measured results.

```bash
bash /workspace/tools/install_safal.sh /workspace/venvs/safe_iad
cd /workspace/tools
source /workspace/venvs/safe_iad/bin/activate
python -m unittest discover -s tests -v
python -m safe_iad.safal_cli --help
```

All 159 unit/contract tests passed. The real full-model validation run is
`/tmp/safal_full_model_v050_final`: k1/2/4/8, two draws, eight unique native
queries, 16 episodes and 320 method records. SAFAL accuracy matched fixed
averaging and fell below the PCA branch. No accuracy gain is established.
Cutoffs use k+4 normal target images; error probabilities use source
normal/CutPaste proxy labels with unverified native transfer. Adequacy and
uncertainty are compatibility diagnostics, not reliability probabilities.

Train/evaluate/predict and verified completed-run resume commands passed with
the real pretrained encoder. Native prediction maps and resized 256x256
evaluation maps have distinct geometry. Portable plain-vendor and freshly
fetched Git sources reproduced actual float32 features exactly. These are
current-instance checks, not a fresh-environment restoration or full benchmark.
Compact evidence and genuinely fitted k2 examples are in the v0.5.0 source ZIP
and `results/safal_full_model/` on GitHub. Download the pretrained checkpoint
separately with `python -m safe_iad.safal_cli prepare --destination PATH`; keep
its SHA256 and pinned source verification enabled. Adjust JSON runtime paths
for local inference. No background service needs restarting.

For an unchanged completed run, use
`python -m safe_iad.safal_cli demo --config configs/safal_demo.json --output /tmp/safal_full_model_v050_final`.
The resume verifies output, input and implementation hashes. For fresh
experiments, use a new output directory and verified datasets; never reuse
labels from final categories for fitting or tuning. Real-IAD and full/private
AD2 benchmarks remain unrun. The model runs on the pinned CPU runtime; this
environment has no CUDA GPU.

## Historical Safe IAD v0.4.0 workflow

The research repository is https://github.com/ennayriomar/newpr. Its executable
source is under `framework/`; restore that package as `/workspace/tools` for the
documented runtime. Preserve the selected profile checkout, earlier code/result
archives, current datasets and measured runs. Repository selection is resolved.

Use Linux and Python 3.12 with the pinned CPU runtime. The installer needs the
documented `/workspace` layout and network access to clone the pinned official
DINOv2, AnomalyDINO and SubspaceAD Git dependencies. Vendor source snapshots
retain licenses but have no Git metadata. The real pretrained checkpoint,
verified native datasets and official AD2 utilities are separate prerequisites;
no random-weight fallback, CUDA runtime or arbitrary-path install is claimed.
See `README.md` and the source ZIP's `BUNDLE_README.md` for exact restore paths
and fresh-input verification commands. Use at most four verification workers.

```bash
bash /workspace/tools/install_runtime.sh
cd /workspace/tools
source /workspace/venvs/safe_iad/bin/activate
python -m unittest discover -s tests -v
python -m safe_iad.build_benefit_targets --config configs/milestone3.json
python -m safe_iad.train_benefit --config configs/milestone3.json
python -m safe_iad.run_benefit_pilot --config configs/milestone3.json
```

The existing completed M3 run is `/tmp/safe_iad_milestone3`. Its gate failed:
utility improved in the small paired pilot, but four correlated newly missed
defect inspection records, falling defect-pixel recall and an unestablished
missing-support false-alarm effect stopped expansion. Read `research_report.md`,
`evaluation/gate.json`, `validation.json` and `real_weight_reproduction.json`.
Do not run larger experiments or retune from these locked outcomes.

All 97 unit/contract tests passed. The real-output audit verified 39 ledgers,
1,903 output files and 547 input files across 576 records/20 unique query images.
Two cache-bypassed real-query probes reproduced features, selections and maps.
These checks are neither a complete independent rerun nor a reliability claim.

For a fresh M3 run, copy its JSON config and choose new `output`, `generated_root`
and `feature_cache` paths. Changing code/config/data requires new outputs and
renewed validation. Copied reports cannot replace absolute-path input files in
resume ledgers. Raw datasets, checkpoints and feature caches are excluded from
the code ZIP. Never use staged `.unverified` datasets.

M1/M2 and the separate strict hybrid are retained historical pilots; their
commands and caveats are in `start_instructions_strict.md`. No full published
benchmark, private AD2 result, lighting stress study, calibrated probability or
validated production system is established. AD2 data locally retains only
train/validation/public splits; public previews must not be renamed as private
predictions. Preserve actual source/validation/calibration roles and source-only
training restrictions.

