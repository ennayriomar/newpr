# Complete SAFAL v0.5.0 model outputs

This separate archive retains every fitted source/target normal-bank checkpoint, full-precision replay probe and all resized metric score-map arrays from the measured run, plus compact reports/verification. It excludes dataset images, generated CutPaste images, pretrained backbone weights and feature caches. See manifest.json for archive/part SHA256 checksums.

Run the verified downloader from framework/ (also bundled in the source ZIP):

```bash
python download_safal_results.py --destination ./safal_results_download
unzip ./safal_results_download/safal_full_results_v0.5.0.zip
```

Use --ref PUBLISHED_COMMIT for immutable downloads. Every part and the reassembled ZIP are checksum-verified. Read the extracted MODEL_ARTIFACT_NOTICE.md and research_report.md. There are eight unique native query images, not 320 independent test images. Adaptive SAFAL did not establish higher accuracy. Error probabilities use source proxy events and carry no native calibration guarantee. The completed-run ledgers retain original absolute input paths; a new independent benchmark needs verified inputs and a new output directory.
