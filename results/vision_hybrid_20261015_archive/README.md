# Complete measured study archive

This contains all 20 one-shot fitted support banks (10 development and 10
verification), selected and unselected metadata, raw branch scores, 200 paired
baseline/hybrid maps, 10 feature probes, manifests, selection lock, tests,
audits and reproduction source. Model aliases are TAR hardlinks to their
matching feature banks. Dataset images and the external 1.22 GB DINOv2 weight
file are separate. Derived features retain the dataset licensing conditions.

Use `framework/download_vision_hybrid_results.py --ref PAYLOAD_COMMIT --extract`.
The release README records the immutable payload commit. Every part and the
whole compressed archive are SHA256 checked before safe extraction; the
internal manifest verifies extracted artifacts. The compact ZIP provides full
code and one fixed example bank. Preserve the original run's absolute paths
when resuming its ledgers; portable prediction uses explicit path overrides.
