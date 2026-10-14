# Complete measured tuning outputs

The15 primary fitted banks,15 replay probes,300 three-method metric map files,
development raw scores, full parameter grid, frozen selection/query locks,
reports and audits are in this complete archive. Superseded attempt banks and
logs are also retained under attempts/ and explicitly counted separately in
manifest.json; these are not additional primary runs. Original run files and the
assembled ZIP are retained in the cloud workspace. Raw dataset images,
external feature caches and pretrained backbone weights are separate.

Download this folder's manifest.json and join.py, then assemble/check public
parts without retaining a second part copy:

```bash
python join.py --base-url https://raw.githubusercontent.com/ennayriomar/newpr/PUBLISHED_COMMIT/ARCHIVE_DIRECTORY --destination safal_tuning_full_results_20261014.zip
```

Replace PUBLISHED_COMMIT/ARCHIVE_DIRECTORY with the published immutable location.
For already downloaded local parts, use --parts-dir /path/to/parts. Every part
and the assembled ZIP SHA256 is checked. The ZIP's internal manifest checks
each uncompressed file; read the measured report and artifact license notice.
Copied cloud paths do not claim a new-machine verified resume.
