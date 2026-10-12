# newpr

## Safe IAD full code

[Download the full code ZIP](https://github.com/ennayriomar/newpr/raw/refs/heads/main/safe_iad_full_code.zip)

The ZIP contains the framework, configs, tests, setup scripts, documentation, measured reports, and pinned dependency sources with their licenses. Datasets and pretrained weights are separate downloads. The included pilot results do not establish production reliability.

Verify the download and extract it:

```bash
sha256sum -c safe_iad_full_code.zip.sha256
unzip safe_iad_full_code.zip
```

Download the [SHA256 checksum](safe_iad_full_code.zip.sha256) into the same directory before running the verification command. Start with `safe_iad_full_code/BUNDLE_README.md` after extraction.

## Full results

[Browse reports and plots](results/README.md) · [Download reports and figures ZIP](https://github.com/ennayriomar/newpr/raw/refs/heads/main/safe_iad_reports.zip) · [Download the complete results archive](https://github.com/ennayriomar/newpr/tree/main/results_archive)

The complete archive contains 4,580 result files (4.91 GB before compression), including raw anomaly maps and public prediction TIFFs. Use the automatic downloader, or download all numbered parts and verify the checksum file. Follow [the extraction instructions](results/RESULTS_README.md).

The current completed run is a five-category pilot with 20 unique evaluation queries. The full 20-category and private AD 2 evaluations have not been run.
