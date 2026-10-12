# Safe IAD full result archive

This archive preserves all 4,580 original files generated under `/workspace/reports`, totaling 4.91 GB before compression. It includes raw anomaly maps (`.npz`), public AD 2 prediction TIFFs, metrics, plots, per-episode records, split manifests, provenance, calibration records, verification reports, logs, and implementation snapshots. Datasets, pretrained checkpoint binaries, environments, and feature caches are separate.

Start with `reports/hybrid_framework_report.md` and `reports/hybrid_pipeline_strict/metrics.csv`. The strict pilot is the current result: five categories, 20 unique evaluation queries, and three support draws at k=1,2,4. The full 20-category evaluation and private AD 2 evaluation have not been run.

`hybrid_pipeline` and its implementation snapshot preserve the superseded exploratory calibration run. `hybrid_pipeline_preprocessing_audit_attempt` preserves an interrupted attempt. `baseline_pilot` and `milestone2` preserve earlier completed experiments. Their original provenance and limitations remain in the reports.

## Download and extract automatically

Download `download_results.py` from this directory, then run it with Python 3.9 or newer:

```bash
python download_results.py --output ./downloaded_results
```

The script downloads all numbered parts, verifies SHA256 checksums, and extracts the archive while checking every file against the manifest. It uses only Python's standard library. Allow about 5 GB of free storage for the extracted results, plus a small temporary download buffer. The archive has been split into 8 MiB pieces because the cloud network blocks the release upload endpoint and limits large GitHub API requests.

## Manual download

Download every `safe_iad_full_results.tar.gz.part-NNN` listed in `DOWNLOAD_MANIFEST.json`, plus `safe_iad_full_results.parts.sha256`, into one directory. On Linux or macOS:

```bash
sha256sum -c safe_iad_full_results.parts.sha256
cat safe_iad_full_results.tar.gz.part-* | tar -xz
```

On macOS, use `shasum -a 256 -c safe_iad_full_results.parts.sha256` if `sha256sum` is unavailable. On Windows, the Python downloader above avoids manual binary concatenation.

The extracted `safe_iad_full_results/RESULTS_MANIFEST.json` records every original result file's SHA256 and byte count. `DOWNLOAD_MANIFEST.json` additionally records all archive parts and the complete archive checksum. Absolute `/workspace` paths in the experiments refer to the original cloud execution environment.
