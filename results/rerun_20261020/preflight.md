# External-path preflight — 2026-10-20

No pipeline was run. No repository code was imported or executed. This task only read saved files/code, parsed JSON and probed filesystem paths. All results describe the current execution environment, not another machine. Existing results remain unchanged.

Source repository: ennayriomar/newpr; source commit: 05c0fcea1b3289f0daf2f658c56b08c2848b71e9. Destination: rerun-20261020, results/rerun_20261020/preflight.md.

## Files read

Complete saved protocol.json, calibration_ids.json and source_plan.json from results/controlled_full_image_20261018/; complete code controlled_experiment.py, controlled_common.py, utils.py, framework/safe_iad/vision_hybrid_features.py, safal_features.py, safal_cli.py, verify_dataset.py and vision_hybrid_model.py. Source-plan blob read: 193bcd8851f537810a8673efe7ce9f4c3ffeabe4. Source line references below refer to that frozen commit, and dataset-record references are to the first source_plan.json occurrence of each path.

## Main required inputs

| Input | Exact expected path | Exists here | Actual size / SHA-256 | Source |
|---|---|---|---|---|
| Checkpoint | /tmp/safal_controlled_assets/dinov2_vitl14_reg4_pretrain.pth | no | unavailable: absent | protocol.json:8–9; vision_hybrid_features.py:98–115 |
| DINOv2 source | /workspace/.cache/dinov2-source | no | unavailable: absent | protocol.json:10; controlled_experiment.py:122–124 |
| AD2 source and calibration root | /workspace/datasets/mvtec_ad2_public/mvtec_ad_2 | no | unavailable: absent | protocol.json:36; controlled_experiment.py:66–80 |
| MVTec AD root | /workspace/datasets/mvtec_ad | no | unavailable: absent | protocol.json:37; controlled_experiment.py:66–68 |
| VisA root | /workspace/datasets/visa | no | unavailable: absent | protocol.json:38; controlled_experiment.py:66–68 |

Expected checkpoint SHA-256: 36e4deffbaef061a2576705b0c36f93621e2ae20bf6274694821b0b492551b51 (protocol.json:8; vision_hybrid_features.py:24). Expected length: 1217607321 bytes (vision_hybrid_features.py:25). These are saved expectations; neither actual size nor hash could be measured because the checkpoint is absent.

## Code-derived dependencies and coverage

- DINOv2 source: safal_features.py:75–113 requires a clean pinned Git checkout OR a verified source_manifest.sha256.json bundle. The two provenance formats are alternatives. The expected source pin is 7764ea0f912e53c92e82eb78a2a1631e92725fc8 and manifest digest is 9ed9679525be8520b45cd087ce2bff1cd684f438ac82bc0d6080e36487adf340 (safal_features.py:30–37). Local hub loading also needs hubconf.py and its source modules (vision_hybrid_features.py:114). Without the source tree/manifest, the individual DINOv2 module files cannot be exhaustively enumerated.
- VisA metadata: split_csv/1cls.csv, each category's image_anno.csv, Data/Images and Data/Masks inventories (verify_dataset.py:42–59). Concrete paths are listed below.
- Dataset inventory: MVTec AD train/test and AD2 train/validation/test_public directories plus anomaly masks (verify_dataset.py:61–88). A fresh prepare scans all native entries, including images not selected into the saved plan. Unrecorded individual filenames cannot be recovered from the missing dataset roots.
- Calibration is not a separate root. It uses the 160 exact AD2 train-normal image paths in calibration_ids.json and source_plan.json roles.calibration (controlled_experiment.py:69–82,174–184,214). Every calibration image is individually listed below; all are absent. Normal records with mask=null introduce no calibration-mask input.
- The saved plan contains 2530 unique image records: support 45, calibration 160, source_query 80 and evaluation 2245. These are parsed saved-plan counts, not a successful dataset inventory or new leakage check. All recorded image paths and non-null mask paths are probed below.
- Run-relative prerequisites are <run>/experiment_config.json, <run>/source_plan.json, <run>/source_plan.json.sha256, <run>/protocol.json and <run>/protocol.json.sha256 (controlled_experiment.py:63,114–117,228–230). These are generated/saved run artifacts, not extra external datasets. No runnable new experiment directory was populated. Code-hash inputs are relative to the code checkout (controlled_experiment.py:40–44). No old result was treated as a writable run directory.
- The controlled pipeline constructs RegisterEncoder (controlled_experiment.py:122–124). SAFALEncoder's different checkpoint/cache_root settings elsewhere in safal_features.py are not extra inputs to this run. Support banks are fitted from support images rather than loaded as a required pretrained bank (controlled_experiment.py:127–143).

This list is exhaustive for concrete external paths in the frozen plan and the stated code-derived metadata/directory entries. It does not claim an exhaustive inventory of files under missing dataset roots or in the missing DINOv2 manifest. Python package binaries and OS libraries were not inventoried as external experiment-data paths.

## Filesystem output

3914 distinct concrete paths checked; 3914 absent; 0 present; 0 indeterminate. Every failure was FileNotFoundError, errno 2. A missing ancestor also makes its descendants unavailable. No file size or SHA-256 was therefore obtained. A present regular file would have been hashed with SHA-256; a present directory would have its recursive regular-file byte total reported with traversal errors. No image decoding, feature extraction, PCA, model loading, calibration or metric calculation was performed.

Full commands and untruncated stdout/process metadata are saved alongside this report as [preflight_probe_1408_1.json](preflight_probe_1408_1.json), [preflight_probe_1408_2.json](preflight_probe_1408_2.json), [preflight_probe_1408_3.json](preflight_probe_1408_3.json), and [preflight_probe_1408_4.json](preflight_probe_1408_4.json). Exit code 0 means the probe completed while catching and printing missing-file errors; it is not a successful pipeline result.

Each row prints the exact expected path, observed existence and size/hash availability. Conditional provenance entries are labeled accordingly.

| Exact expected path | Role | Exists | Actual size / SHA-256 | Source |
|---|---|---|---|---|
| /tmp/safal_controlled_assets/dinov2_vitl14_reg4_pretrain.pth | checkpoint | no (errno 2) | unavailable | protocol.json config.checkpoint |
| /workspace/.cache/dinov2-source | source_dir | no (errno 2) | unavailable | protocol.json config.source_dir |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2 | source_root | no (errno 2) | unavailable | protocol.json config.source_root |
| /workspace/datasets/mvtec_ad | bottle_root | no (errno 2) | unavailable | protocol.json config.bottle_root |
| /workspace/datasets/visa | visa_root | no (errno 2) | unavailable | protocol.json config.visa_root |
| /workspace/.cache/dinov2-source/source_manifest.sha256.json | conditional manifest | no (errno 2) | unavailable | safal_features.py:88–106 |
| /workspace/.cache/dinov2-source/.git | alternative Git provenance | no (errno 2) | unavailable | safal_features.py:79–86 |
| /workspace/.cache/dinov2-source/hubconf.py | local hub entry | no (errno 2) | unavailable | vision_hybrid_features.py:114 |
| /workspace/.cache/dinov2-source/LICENSE | source verification | no (errno 2) | unavailable | safal_features.py:84–106 |
| /workspace/datasets/visa/split_csv/1cls.csv | VisA split CSV | no (errno 2) | unavailable | verify_dataset.py:42–50 |
| /workspace/datasets/visa/candle/image_anno.csv | VisA annotation CSV | no (errno 2) | unavailable | verify_dataset.py:52–57 |
| /workspace/datasets/visa/candle/Data/Images | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/candle/Data/Masks | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/capsules/image_anno.csv | VisA annotation CSV | no (errno 2) | unavailable | verify_dataset.py:52–57 |
| /workspace/datasets/visa/capsules/Data/Images | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/capsules/Data/Masks | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/cashew/image_anno.csv | VisA annotation CSV | no (errno 2) | unavailable | verify_dataset.py:52–57 |
| /workspace/datasets/visa/cashew/Data/Images | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/cashew/Data/Masks | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/chewinggum/image_anno.csv | VisA annotation CSV | no (errno 2) | unavailable | verify_dataset.py:52–57 |
| /workspace/datasets/visa/chewinggum/Data/Images | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/chewinggum/Data/Masks | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/fryum/image_anno.csv | VisA annotation CSV | no (errno 2) | unavailable | verify_dataset.py:52–57 |
| /workspace/datasets/visa/fryum/Data/Images | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/fryum/Data/Masks | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/macaroni1/image_anno.csv | VisA annotation CSV | no (errno 2) | unavailable | verify_dataset.py:52–57 |
| /workspace/datasets/visa/macaroni1/Data/Images | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/macaroni1/Data/Masks | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/macaroni2/image_anno.csv | VisA annotation CSV | no (errno 2) | unavailable | verify_dataset.py:52–57 |
| /workspace/datasets/visa/macaroni2/Data/Images | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/macaroni2/Data/Masks | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/pcb1/image_anno.csv | VisA annotation CSV | no (errno 2) | unavailable | verify_dataset.py:52–57 |
| /workspace/datasets/visa/pcb1/Data/Images | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/pcb1/Data/Masks | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/pcb2/image_anno.csv | VisA annotation CSV | no (errno 2) | unavailable | verify_dataset.py:52–57 |
| /workspace/datasets/visa/pcb2/Data/Images | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/pcb2/Data/Masks | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/pcb3/image_anno.csv | VisA annotation CSV | no (errno 2) | unavailable | verify_dataset.py:52–57 |
| /workspace/datasets/visa/pcb3/Data/Images | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/pcb3/Data/Masks | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/pcb4/image_anno.csv | VisA annotation CSV | no (errno 2) | unavailable | verify_dataset.py:52–57 |
| /workspace/datasets/visa/pcb4/Data/Images | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/pcb4/Data/Masks | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/pipe_fryum/image_anno.csv | VisA annotation CSV | no (errno 2) | unavailable | verify_dataset.py:52–57 |
| /workspace/datasets/visa/pipe_fryum/Data/Images | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks | VisA inventory directory | no (errno 2) | unavailable | verify_dataset.py:58–59 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/267_regular.png | support | no (errno 2) | unavailable | source_plan.json:7630 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/267_regular.png | support | no (errno 2) | unavailable | source_plan.json:7950 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/212_regular.png | support | no (errno 2) | unavailable | source_plan.json:8280 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/267_regular.png | support | no (errno 2) | unavailable | source_plan.json:8610 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/133_regular.png | support | no (errno 2) | unavailable | source_plan.json:8950 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/267_regular.png | support | no (errno 2) | unavailable | source_plan.json:9250 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/267_regular.png | support | no (errno 2) | unavailable | source_plan.json:9550 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/267_regular.png | support | no (errno 2) | unavailable | source_plan.json:9810 |
| /workspace/datasets/mvtec_ad/bottle/train/good/133.png | support | no (errno 2) | unavailable | source_plan.json:10720 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0045.JPG | support | no (errno 2) | unavailable | source_plan.json:11790 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0585.JPG | support | no (errno 2) | unavailable | source_plan.json:12250 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0612.JPG | support | no (errno 2) | unavailable | source_plan.json:12260 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/045.JPG | support | no (errno 2) | unavailable | source_plan.json:13820 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/085.JPG | support | no (errno 2) | unavailable | source_plan.json:13850 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/593.JPG | support | no (errno 2) | unavailable | source_plan.json:14370 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/022.JPG | support | no (errno 2) | unavailable | source_plan.json:15420 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/292.JPG | support | no (errno 2) | unavailable | source_plan.json:15650 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/305.JPG | support | no (errno 2) | unavailable | source_plan.json:15660 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/022.JPG | support | no (errno 2) | unavailable | source_plan.json:16950 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/291.JPG | support | no (errno 2) | unavailable | source_plan.json:17170 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/304.JPG | support | no (errno 2) | unavailable | source_plan.json:17180 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/022.JPG | support | no (errno 2) | unavailable | source_plan.json:18480 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/292.JPG | support | no (errno 2) | unavailable | source_plan.json:18710 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/305.JPG | support | no (errno 2) | unavailable | source_plan.json:18720 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0045.JPG | support | no (errno 2) | unavailable | source_plan.json:20040 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0585.JPG | support | no (errno 2) | unavailable | source_plan.json:20500 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0612.JPG | support | no (errno 2) | unavailable | source_plan.json:20510 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0045.JPG | support | no (errno 2) | unavailable | source_plan.json:22070 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0585.JPG | support | no (errno 2) | unavailable | source_plan.json:22530 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0612.JPG | support | no (errno 2) | unavailable | source_plan.json:22540 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0045.JPG | support | no (errno 2) | unavailable | source_plan.json:24100 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0585.JPG | support | no (errno 2) | unavailable | source_plan.json:24560 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0612.JPG | support | no (errno 2) | unavailable | source_plan.json:24570 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0045.JPG | support | no (errno 2) | unavailable | source_plan.json:26130 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0585.JPG | support | no (errno 2) | unavailable | source_plan.json:26590 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0612.JPG | support | no (errno 2) | unavailable | source_plan.json:26600 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0045.JPG | support | no (errno 2) | unavailable | source_plan.json:28160 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0585.JPG | support | no (errno 2) | unavailable | source_plan.json:28620 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0612.JPG | support | no (errno 2) | unavailable | source_plan.json:28630 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0045.JPG | support | no (errno 2) | unavailable | source_plan.json:30200 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0585.JPG | support | no (errno 2) | unavailable | source_plan.json:30660 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0612.JPG | support | no (errno 2) | unavailable | source_plan.json:30670 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/022.JPG | support | no (errno 2) | unavailable | source_plan.json:32210 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/292.JPG | support | no (errno 2) | unavailable | source_plan.json:32440 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/305.JPG | support | no (errno 2) | unavailable | source_plan.json:32450 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/401_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7700 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/102_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7550 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/168_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7590 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/400_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7690 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/032_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7520 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/234_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7600 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/257_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7610 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/280_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7650 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/406_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7710 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/059_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7530 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/113_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7560 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/028_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7510 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/317_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7670 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/139_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7580 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/131_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7570 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/295_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7660 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/095_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7540 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/375_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7680 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/277_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7640 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train/good/260_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7620 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/302_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7980 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/165_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7910 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/371_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8010 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/061_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7840 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/108_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7860 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/240_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7940 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/277_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7960 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/149_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7890 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/136_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7870 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/367_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8000 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/014_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7830 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/178_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7920 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/070_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7850 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/002_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7820 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/372_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8020 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/280_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7970 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/150_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7900 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/225_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7930 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/330_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7990 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train/good/138_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:7880 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/236_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8300 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/160_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8260 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/108_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8220 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/247_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8310 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/031_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8150 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/254_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8320 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/041_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8170 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/075_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8190 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/016_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8130 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/165_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8270 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/261_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8330 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/104_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8210 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/033_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8160 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/126_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8250 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/219_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8290 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/046_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8180 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/113_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8240 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/109_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8230 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/078_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8200 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train/good/025_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8140 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/280_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8620 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/197_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8550 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/298_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8630 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/005_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8450 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/195_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8540 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/207_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8570 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/160_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8530 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/119_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8520 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/246_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8600 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/204_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8560 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/000_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8440 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/112_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8510 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/009_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8460 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/027_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8470 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/301_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8640 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/031_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8480 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/061_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8500 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/236_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8590 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/209_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8580 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train/good/046_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8490 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/090_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8920 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/072_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8900 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/044_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8830 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/012_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8770 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/061_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8890 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/058_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8870 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/060_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8880 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/000_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8750 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/033_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8810 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/015_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8780 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/050_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8850 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/049_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8840 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/078_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8910 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/027_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8790 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/038_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8820 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/130_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8940 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/029_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8800 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/055_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8860 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/115_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8930 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train/good/001_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:8760 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/129_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9130 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/135_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9150 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/103_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9100 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/274_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9260 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/180_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9190 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/123_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9120 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/187_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9210 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/011_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9070 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/208_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9240 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/039_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9090 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/204_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9220 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/104_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9110 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/159_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9170 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/177_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9180 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/151_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9160 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/132_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9140 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/181_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9200 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/022_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9080 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/206_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9230 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train/good/010_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9060 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/090_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9430 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/038_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9390 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/157_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9460 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/009_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9370 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/098_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9440 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/270_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9560 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/031_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9380 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/287_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9570 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/044_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9400 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/173_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9470 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/262_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9540 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/257_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9530 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/177_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9480 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/204_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9490 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/081_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9410 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/089_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9420 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/242_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9510 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/222_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9500 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/249_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9520 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train/good/136_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9450 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/217_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9780 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/194_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9760 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/400_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9870 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/115_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9730 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/100_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9720 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/347_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9830 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/369_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9850 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/293_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9820 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/227_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9800 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/036_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9690 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/419_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9880 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/209_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9770 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/186_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9750 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/073_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9710 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/393_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9860 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/354_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9840 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/069_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9700 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/026_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9680 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/173_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9740 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train/good/225_regular.png | calibration | no (errno 2) | unavailable | source_plan.json:9790 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public/good/004_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:7490 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public/good/007_regular.png | source_query | no (errno 2) | unavailable | source_plan.json:7500 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public/good/001_shift_2.png | source_query | no (errno 2) | unavailable | source_plan.json:7480 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public/good/000_underexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:7470 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public/good/000_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:7460 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public/bad/013_underexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:7450 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public/ground_truth/bad/013_underexposed_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:7452 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public/bad/004_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:7430 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public/ground_truth/bad/004_shift_1_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:7432 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public/bad/007_regular.png | source_query | no (errno 2) | unavailable | source_plan.json:7440 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public/ground_truth/bad/007_regular_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:7442 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public/bad/001_shift_2.png | source_query | no (errno 2) | unavailable | source_plan.json:7420 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public/ground_truth/bad/001_shift_2_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:7422 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public/bad/000_underexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:7410 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public/ground_truth/bad/000_underexposed_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:7412 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public/good/010_regular.png | source_query | no (errno 2) | unavailable | source_plan.json:7810 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public/good/004_shift_2.png | source_query | no (errno 2) | unavailable | source_plan.json:7780 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public/good/000_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:7770 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public/good/005_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:7790 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public/good/009_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:7800 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public/bad/010_regular.png | source_query | no (errno 2) | unavailable | source_plan.json:7740 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public/ground_truth/bad/010_regular_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:7742 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public/bad/011_overexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:7750 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public/ground_truth/bad/011_overexposed_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:7752 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public/bad/013_overexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:7760 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public/ground_truth/bad/013_overexposed_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:7762 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public/bad/004_shift_2.png | source_query | no (errno 2) | unavailable | source_plan.json:7730 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public/ground_truth/bad/004_shift_2_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:7732 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public/bad/000_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:7720 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public/ground_truth/bad/000_shift_1_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:7722 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public/good/003_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:8100 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public/good/004_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:8120 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public/good/004_overexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:8110 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public/good/003_overexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:8090 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public/good/002_regular.png | source_query | no (errno 2) | unavailable | source_plan.json:8080 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public/bad/007_overexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:8050 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public/ground_truth/bad/007_overexposed_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8052 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public/bad/009_regular.png | source_query | no (errno 2) | unavailable | source_plan.json:8070 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public/ground_truth/bad/009_regular_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8072 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public/bad/008_regular.png | source_query | no (errno 2) | unavailable | source_plan.json:8060 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public/ground_truth/bad/008_regular_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8062 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public/bad/006_overexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:8040 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public/ground_truth/bad/006_overexposed_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8042 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public/bad/004_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:8030 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public/ground_truth/bad/004_shift_1_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8032 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public/good/005_shift_2.png | source_query | no (errno 2) | unavailable | source_plan.json:8420 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public/good/001_underexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:8390 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public/good/002_underexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:8400 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public/good/003_shift_3.png | source_query | no (errno 2) | unavailable | source_plan.json:8410 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public/good/006_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:8430 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public/bad/011_regular.png | source_query | no (errno 2) | unavailable | source_plan.json:8370 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public/ground_truth/bad/011_regular_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8372 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public/bad/003_shift_3.png | source_query | no (errno 2) | unavailable | source_plan.json:8340 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public/ground_truth/bad/003_shift_3_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8342 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public/bad/005_underexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:8350 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public/ground_truth/bad/005_underexposed_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8352 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public/bad/007_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:8360 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public/ground_truth/bad/007_shift_1_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8362 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public/bad/012_underexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:8380 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public/ground_truth/bad/012_underexposed_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8382 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public/good/003_overexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:8730 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public/good/002_shift_3.png | source_query | no (errno 2) | unavailable | source_plan.json:8720 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public/good/001_regular.png | source_query | no (errno 2) | unavailable | source_plan.json:8700 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public/good/003_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:8740 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public/good/002_overexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:8710 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public/bad/012_overexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:8680 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public/ground_truth/bad/012_overexposed_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8682 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public/bad/010_shift_3.png | source_query | no (errno 2) | unavailable | source_plan.json:8670 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public/ground_truth/bad/010_shift_3_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8672 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public/bad/005_overexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:8650 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public/ground_truth/bad/005_overexposed_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8652 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public/bad/013_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:8690 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public/ground_truth/bad/013_shift_1_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8692 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public/bad/008_regular.png | source_query | no (errno 2) | unavailable | source_plan.json:8660 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public/ground_truth/bad/008_regular_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8662 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public/good/004_shift_2.png | source_query | no (errno 2) | unavailable | source_plan.json:9040 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public/good/001_shift_2.png | source_query | no (errno 2) | unavailable | source_plan.json:9020 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public/good/001_shift_3.png | source_query | no (errno 2) | unavailable | source_plan.json:9030 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public/good/000_shift_4.png | source_query | no (errno 2) | unavailable | source_plan.json:9010 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public/good/004_underexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:9050 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public/bad/013_shift_4.png | source_query | no (errno 2) | unavailable | source_plan.json:9000 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public/ground_truth/bad/013_shift_4_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:9002 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public/bad/010_shift_2.png | source_query | no (errno 2) | unavailable | source_plan.json:8980 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public/ground_truth/bad/010_shift_2_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8982 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public/bad/011_underexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:8990 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public/ground_truth/bad/011_underexposed_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8992 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public/bad/009_overexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:8970 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public/ground_truth/bad/009_overexposed_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8972 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public/bad/002_underexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:8960 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public/ground_truth/bad/002_underexposed_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:8962 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public/good/008_shift_3.png | source_query | no (errno 2) | unavailable | source_plan.json:9360 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public/good/001_underexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:9340 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public/good/007_regular.png | source_query | no (errno 2) | unavailable | source_plan.json:9350 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public/good/000_overexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:9320 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public/good/000_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:9330 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public/bad/003_shift_3.png | source_query | no (errno 2) | unavailable | source_plan.json:9290 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public/ground_truth/bad/003_shift_3_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:9292 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public/bad/014_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:9300 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public/ground_truth/bad/014_shift_1_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:9302 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public/bad/000_overexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:9270 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public/ground_truth/bad/000_overexposed_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:9272 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public/bad/000_underexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:9280 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public/ground_truth/bad/000_underexposed_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:9282 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public/bad/014_shift_3.png | source_query | no (errno 2) | unavailable | source_plan.json:9310 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public/ground_truth/bad/014_shift_3_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:9312 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public/good/009_overexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:9660 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public/good/009_shift_3.png | source_query | no (errno 2) | unavailable | source_plan.json:9670 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public/good/000_overexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:9630 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public/good/003_shift_1.png | source_query | no (errno 2) | unavailable | source_plan.json:9640 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public/good/004_shift_3.png | source_query | no (errno 2) | unavailable | source_plan.json:9650 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public/bad/000_regular.png | source_query | no (errno 2) | unavailable | source_plan.json:9580 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public/ground_truth/bad/000_regular_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:9582 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public/bad/006_shift_3.png | source_query | no (errno 2) | unavailable | source_plan.json:9600 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public/ground_truth/bad/006_shift_3_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:9602 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public/bad/009_shift_2.png | source_query | no (errno 2) | unavailable | source_plan.json:9610 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public/ground_truth/bad/009_shift_2_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:9612 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public/bad/011_underexposed.png | source_query | no (errno 2) | unavailable | source_plan.json:9620 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public/ground_truth/bad/011_underexposed_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:9622 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public/bad/005_regular.png | source_query | no (errno 2) | unavailable | source_plan.json:9590 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public/ground_truth/bad/005_regular_mask.png | source_query mask | no (errno 2) | unavailable | source_plan.json:9592 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/000.png | evaluation | no (errno 2) | unavailable | source_plan.json:9890 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/000_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:9892 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/001.png | evaluation | no (errno 2) | unavailable | source_plan.json:9900 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/001_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:9902 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/002.png | evaluation | no (errno 2) | unavailable | source_plan.json:9910 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/002_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:9912 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/003.png | evaluation | no (errno 2) | unavailable | source_plan.json:9920 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/003_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:9922 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/004.png | evaluation | no (errno 2) | unavailable | source_plan.json:9930 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/004_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:9932 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/005.png | evaluation | no (errno 2) | unavailable | source_plan.json:9940 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/005_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:9942 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/006.png | evaluation | no (errno 2) | unavailable | source_plan.json:9950 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/006_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:9952 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/007.png | evaluation | no (errno 2) | unavailable | source_plan.json:9960 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/007_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:9962 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/008.png | evaluation | no (errno 2) | unavailable | source_plan.json:9970 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/008_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:9972 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/009.png | evaluation | no (errno 2) | unavailable | source_plan.json:9980 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/009_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:9982 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/010.png | evaluation | no (errno 2) | unavailable | source_plan.json:9990 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/010_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:9992 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/011.png | evaluation | no (errno 2) | unavailable | source_plan.json:10000 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/011_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10002 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/012.png | evaluation | no (errno 2) | unavailable | source_plan.json:10010 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/012_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10012 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/013.png | evaluation | no (errno 2) | unavailable | source_plan.json:10020 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/013_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10022 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/014.png | evaluation | no (errno 2) | unavailable | source_plan.json:10030 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/014_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10032 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/015.png | evaluation | no (errno 2) | unavailable | source_plan.json:10040 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/015_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10042 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/016.png | evaluation | no (errno 2) | unavailable | source_plan.json:10050 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/016_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10052 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/017.png | evaluation | no (errno 2) | unavailable | source_plan.json:10060 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/017_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10062 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/018.png | evaluation | no (errno 2) | unavailable | source_plan.json:10070 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/018_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10072 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_large/019.png | evaluation | no (errno 2) | unavailable | source_plan.json:10080 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_large/019_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10082 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/000.png | evaluation | no (errno 2) | unavailable | source_plan.json:10090 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/000_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10092 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/001.png | evaluation | no (errno 2) | unavailable | source_plan.json:10100 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/001_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10102 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/002.png | evaluation | no (errno 2) | unavailable | source_plan.json:10110 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/002_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10112 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/003.png | evaluation | no (errno 2) | unavailable | source_plan.json:10120 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/003_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10122 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/004.png | evaluation | no (errno 2) | unavailable | source_plan.json:10130 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/004_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10132 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/005.png | evaluation | no (errno 2) | unavailable | source_plan.json:10140 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/005_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10142 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/006.png | evaluation | no (errno 2) | unavailable | source_plan.json:10150 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/006_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10152 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/007.png | evaluation | no (errno 2) | unavailable | source_plan.json:10160 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/007_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10162 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/008.png | evaluation | no (errno 2) | unavailable | source_plan.json:10170 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/008_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10172 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/009.png | evaluation | no (errno 2) | unavailable | source_plan.json:10180 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/009_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10182 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/010.png | evaluation | no (errno 2) | unavailable | source_plan.json:10190 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/010_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10192 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/011.png | evaluation | no (errno 2) | unavailable | source_plan.json:10200 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/011_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10202 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/012.png | evaluation | no (errno 2) | unavailable | source_plan.json:10210 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/012_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10212 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/013.png | evaluation | no (errno 2) | unavailable | source_plan.json:10220 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/013_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10222 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/014.png | evaluation | no (errno 2) | unavailable | source_plan.json:10230 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/014_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10232 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/015.png | evaluation | no (errno 2) | unavailable | source_plan.json:10240 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/015_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10242 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/016.png | evaluation | no (errno 2) | unavailable | source_plan.json:10250 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/016_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10252 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/017.png | evaluation | no (errno 2) | unavailable | source_plan.json:10260 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/017_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10262 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/018.png | evaluation | no (errno 2) | unavailable | source_plan.json:10270 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/018_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10272 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/019.png | evaluation | no (errno 2) | unavailable | source_plan.json:10280 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/019_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10282 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/020.png | evaluation | no (errno 2) | unavailable | source_plan.json:10290 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/020_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10292 |
| /workspace/datasets/mvtec_ad/bottle/test/broken_small/021.png | evaluation | no (errno 2) | unavailable | source_plan.json:10300 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/broken_small/021_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10302 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/000.png | evaluation | no (errno 2) | unavailable | source_plan.json:10310 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/000_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10312 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/001.png | evaluation | no (errno 2) | unavailable | source_plan.json:10320 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/001_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10322 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/002.png | evaluation | no (errno 2) | unavailable | source_plan.json:10330 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/002_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10332 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/003.png | evaluation | no (errno 2) | unavailable | source_plan.json:10340 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/003_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10342 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/004.png | evaluation | no (errno 2) | unavailable | source_plan.json:10350 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/004_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10352 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/005.png | evaluation | no (errno 2) | unavailable | source_plan.json:10360 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/005_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10362 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/006.png | evaluation | no (errno 2) | unavailable | source_plan.json:10370 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/006_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10372 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/007.png | evaluation | no (errno 2) | unavailable | source_plan.json:10380 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/007_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10382 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/008.png | evaluation | no (errno 2) | unavailable | source_plan.json:10390 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/008_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10392 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/009.png | evaluation | no (errno 2) | unavailable | source_plan.json:10400 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/009_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10402 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/010.png | evaluation | no (errno 2) | unavailable | source_plan.json:10410 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/010_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10412 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/011.png | evaluation | no (errno 2) | unavailable | source_plan.json:10420 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/011_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10422 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/012.png | evaluation | no (errno 2) | unavailable | source_plan.json:10430 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/012_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10432 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/013.png | evaluation | no (errno 2) | unavailable | source_plan.json:10440 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/013_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10442 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/014.png | evaluation | no (errno 2) | unavailable | source_plan.json:10450 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/014_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10452 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/015.png | evaluation | no (errno 2) | unavailable | source_plan.json:10460 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/015_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10462 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/016.png | evaluation | no (errno 2) | unavailable | source_plan.json:10470 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/016_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10472 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/017.png | evaluation | no (errno 2) | unavailable | source_plan.json:10480 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/017_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10482 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/018.png | evaluation | no (errno 2) | unavailable | source_plan.json:10490 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/018_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10492 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/019.png | evaluation | no (errno 2) | unavailable | source_plan.json:10500 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/019_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10502 |
| /workspace/datasets/mvtec_ad/bottle/test/contamination/020.png | evaluation | no (errno 2) | unavailable | source_plan.json:10510 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth/contamination/020_mask.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10512 |
| /workspace/datasets/mvtec_ad/bottle/test/good/000.png | evaluation | no (errno 2) | unavailable | source_plan.json:10520 |
| /workspace/datasets/mvtec_ad/bottle/test/good/001.png | evaluation | no (errno 2) | unavailable | source_plan.json:10530 |
| /workspace/datasets/mvtec_ad/bottle/test/good/002.png | evaluation | no (errno 2) | unavailable | source_plan.json:10540 |
| /workspace/datasets/mvtec_ad/bottle/test/good/003.png | evaluation | no (errno 2) | unavailable | source_plan.json:10550 |
| /workspace/datasets/mvtec_ad/bottle/test/good/004.png | evaluation | no (errno 2) | unavailable | source_plan.json:10560 |
| /workspace/datasets/mvtec_ad/bottle/test/good/005.png | evaluation | no (errno 2) | unavailable | source_plan.json:10570 |
| /workspace/datasets/mvtec_ad/bottle/test/good/006.png | evaluation | no (errno 2) | unavailable | source_plan.json:10580 |
| /workspace/datasets/mvtec_ad/bottle/test/good/007.png | evaluation | no (errno 2) | unavailable | source_plan.json:10590 |
| /workspace/datasets/mvtec_ad/bottle/test/good/008.png | evaluation | no (errno 2) | unavailable | source_plan.json:10600 |
| /workspace/datasets/mvtec_ad/bottle/test/good/009.png | evaluation | no (errno 2) | unavailable | source_plan.json:10610 |
| /workspace/datasets/mvtec_ad/bottle/test/good/010.png | evaluation | no (errno 2) | unavailable | source_plan.json:10620 |
| /workspace/datasets/mvtec_ad/bottle/test/good/011.png | evaluation | no (errno 2) | unavailable | source_plan.json:10630 |
| /workspace/datasets/mvtec_ad/bottle/test/good/012.png | evaluation | no (errno 2) | unavailable | source_plan.json:10640 |
| /workspace/datasets/mvtec_ad/bottle/test/good/013.png | evaluation | no (errno 2) | unavailable | source_plan.json:10650 |
| /workspace/datasets/mvtec_ad/bottle/test/good/014.png | evaluation | no (errno 2) | unavailable | source_plan.json:10660 |
| /workspace/datasets/mvtec_ad/bottle/test/good/015.png | evaluation | no (errno 2) | unavailable | source_plan.json:10670 |
| /workspace/datasets/mvtec_ad/bottle/test/good/016.png | evaluation | no (errno 2) | unavailable | source_plan.json:10680 |
| /workspace/datasets/mvtec_ad/bottle/test/good/017.png | evaluation | no (errno 2) | unavailable | source_plan.json:10690 |
| /workspace/datasets/mvtec_ad/bottle/test/good/018.png | evaluation | no (errno 2) | unavailable | source_plan.json:10700 |
| /workspace/datasets/mvtec_ad/bottle/test/good/019.png | evaluation | no (errno 2) | unavailable | source_plan.json:10710 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/000.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10730 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/000.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10732 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/001.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10740 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/001.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10742 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/002.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10750 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/002.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10752 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/003.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10760 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/003.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10762 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/004.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10770 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/004.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10772 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/005.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10780 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/005.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10782 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/006.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10790 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/006.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10792 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/007.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10800 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/007.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10802 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/008.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10810 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/008.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10812 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/009.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10820 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/009.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10822 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/010.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10830 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/010.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10832 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10840 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/011.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10842 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/012.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10850 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/012.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10852 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10860 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/013.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10862 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/014.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10870 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/014.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10872 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/015.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10880 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/015.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10882 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10890 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/016.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10892 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/017.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10900 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/017.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10902 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/018.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10910 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/018.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10912 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/019.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10920 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/019.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10922 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/020.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10930 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/020.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10932 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/021.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10940 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/021.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10942 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/022.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10950 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/022.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10952 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/023.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10960 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/023.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10962 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10970 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/024.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10972 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/025.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10980 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/025.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10982 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:10990 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/026.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:10992 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11000 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/027.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11002 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/028.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11010 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/028.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11012 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/029.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11020 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/029.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11022 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/030.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11030 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/030.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11032 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/031.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11040 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/031.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11042 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/032.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11050 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/032.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11052 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/033.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11060 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/033.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11062 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/034.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11070 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/034.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11072 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/035.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11080 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/035.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11082 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/036.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11090 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/036.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11092 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/037.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11100 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/037.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11102 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/038.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11110 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/038.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11112 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/039.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11120 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/039.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11122 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/040.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11130 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/040.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11132 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/041.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11140 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/041.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11142 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/042.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11150 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/042.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11152 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/043.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11160 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/043.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11162 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/044.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11170 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/044.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11172 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/045.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11180 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/045.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11182 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11190 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/046.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11192 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/047.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11200 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/047.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11202 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/048.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11210 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/048.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11212 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/049.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11220 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/049.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11222 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/050.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11230 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/050.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11232 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/051.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11240 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/051.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11242 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/052.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11250 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/052.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11252 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/053.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11260 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/053.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11262 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/054.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11270 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/054.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11272 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/055.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11280 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/055.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11282 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/056.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11290 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/056.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11292 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/057.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11300 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/057.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11302 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/058.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11310 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/058.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11312 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/059.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11320 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/059.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11322 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/060.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11330 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/060.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11332 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/061.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11340 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/061.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11342 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/062.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11350 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/062.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11352 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/063.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11360 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/063.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11362 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/064.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11370 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/064.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11372 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/065.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11380 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/065.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11382 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/066.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11390 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/066.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11392 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/067.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11400 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/067.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11402 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/068.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11410 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/068.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11412 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/069.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11420 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/069.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11422 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/070.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11430 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/070.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11432 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/071.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11440 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/071.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11442 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/072.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11450 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/072.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11452 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/073.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11460 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/073.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11462 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/074.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11470 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/074.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11472 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/075.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11480 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/075.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11482 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/076.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11490 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/076.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11492 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/077.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11500 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/077.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11502 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/078.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11510 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/078.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11512 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/079.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11520 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/079.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11522 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/080.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11530 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/080.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11532 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/081.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11540 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/081.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11542 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/082.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11550 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/082.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11552 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/083.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11560 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/083.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11562 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/084.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11570 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/084.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11572 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/085.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11580 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/085.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11582 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/086.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11590 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/086.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11592 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/087.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11600 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/087.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11602 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/088.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11610 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/088.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11612 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/089.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11620 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/089.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11622 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/090.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11630 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/090.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11632 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/091.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11640 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/091.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11642 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/092.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11650 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/092.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11652 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/093.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11660 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/093.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11662 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/094.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11670 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/094.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11672 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/095.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11680 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/095.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11682 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/096.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11690 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/096.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11692 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/097.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11700 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/097.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11702 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/098.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11710 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/098.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11712 |
| /workspace/datasets/visa/candle/Data/Images/Anomaly/099.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11720 |
| /workspace/datasets/visa/candle/Data/Masks/Anomaly/099.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:11722 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11730 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11740 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11750 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11760 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11770 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11780 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11800 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0100.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11810 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0107.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11820 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0159.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11830 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0168.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11840 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0170.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11850 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0172.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11860 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0174.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11870 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0178.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11880 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0187.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11890 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0196.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11900 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0208.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11910 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0214.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11920 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0215.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11930 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0237.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11940 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0261.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11950 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0286.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11960 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0294.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11970 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0297.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11980 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0303.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:11990 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0306.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12000 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0320.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12010 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0333.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12020 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0363.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12030 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0377.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12040 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0394.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12050 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0400.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12060 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0402.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12070 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0417.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12080 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0423.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12090 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0427.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12100 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0457.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12110 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0469.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12120 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0479.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12130 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0483.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12140 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0484.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12150 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0488.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12160 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0490.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12170 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0514.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12180 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0518.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12190 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0520.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12200 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0525.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12210 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0545.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12220 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0552.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12230 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0569.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12240 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0615.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12270 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0617.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12280 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0619.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12290 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0621.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12300 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0629.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12310 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0631.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12320 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0648.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12330 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0654.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12340 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0657.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12350 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0659.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12360 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0674.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12370 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0684.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12380 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0685.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12390 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0688.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12400 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0690.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12410 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0694.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12420 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0705.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12430 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0725.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12440 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0730.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12450 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0735.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12460 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0739.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12470 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0751.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12480 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0755.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12490 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0764.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12500 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0768.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12510 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0779.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12520 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0784.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12530 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0790.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12540 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0796.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12550 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0797.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12560 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0800.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12570 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0804.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12580 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0811.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12590 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0844.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12600 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0869.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12610 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0871.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12620 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0892.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12630 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0900.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12640 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0920.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12650 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0923.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12660 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0935.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12670 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0952.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12680 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0953.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12690 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0964.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12700 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0967.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12710 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0974.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12720 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0985.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12730 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0994.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12740 |
| /workspace/datasets/visa/candle/Data/Images/Normal/0996.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12750 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/000.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12760 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/000.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12762 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/001.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12770 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/001.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12772 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/002.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12780 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/002.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12782 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/003.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12790 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/003.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12792 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/004.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12800 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/004.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12802 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/005.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12810 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/005.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12812 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/006.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12820 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/006.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12822 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/007.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12830 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/007.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12832 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/008.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12840 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/008.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12842 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/009.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12850 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/009.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12852 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/010.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12860 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/010.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12862 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12870 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/011.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12872 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/012.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12880 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/012.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12882 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12890 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/013.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12892 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/014.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12900 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/014.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12902 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/015.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12910 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/015.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12912 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12920 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/016.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12922 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/017.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12930 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/017.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12932 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/018.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12940 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/018.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12942 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/019.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12950 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/019.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12952 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/020.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12960 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/020.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12962 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/021.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12970 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/021.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12972 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/022.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12980 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/022.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12982 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/023.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:12990 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/023.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:12992 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13000 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/024.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13002 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/025.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13010 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/025.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13012 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13020 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/026.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13022 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13030 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/027.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13032 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/028.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13040 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/028.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13042 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/029.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13050 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/029.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13052 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/030.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13060 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/030.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13062 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/031.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13070 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/031.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13072 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/032.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13080 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/032.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13082 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/033.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13090 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/033.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13092 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/034.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13100 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/034.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13102 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/035.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13110 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/035.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13112 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/036.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13120 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/036.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13122 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/037.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13130 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/037.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13132 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/038.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13140 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/038.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13142 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/039.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13150 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/039.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13152 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/040.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13160 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/040.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13162 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/041.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13170 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/041.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13172 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/042.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13180 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/042.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13182 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/043.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13190 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/043.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13192 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/044.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13200 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/044.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13202 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/045.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13210 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/045.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13212 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13220 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/046.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13222 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/047.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13230 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/047.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13232 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/048.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13240 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/048.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13242 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/049.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13250 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/049.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13252 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/050.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13260 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/050.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13262 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/051.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13270 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/051.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13272 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/052.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13280 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/052.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13282 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/053.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13290 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/053.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13292 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/054.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13300 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/054.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13302 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/055.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13310 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/055.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13312 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/056.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13320 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/056.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13322 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/057.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13330 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/057.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13332 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/058.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13340 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/058.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13342 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/059.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13350 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/059.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13352 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/060.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13360 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/060.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13362 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/061.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13370 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/061.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13372 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/062.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13380 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/062.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13382 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/063.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13390 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/063.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13392 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/064.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13400 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/064.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13402 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/065.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13410 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/065.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13412 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/066.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13420 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/066.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13422 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/067.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13430 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/067.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13432 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/068.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13440 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/068.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13442 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/069.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13450 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/069.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13452 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/070.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13460 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/070.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13462 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/071.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13470 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/071.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13472 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/072.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13480 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/072.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13482 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/073.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13490 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/073.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13492 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/074.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13500 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/074.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13502 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/075.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13510 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/075.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13512 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/076.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13520 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/076.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13522 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/077.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13530 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/077.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13532 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/078.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13540 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/078.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13542 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/079.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13550 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/079.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13552 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/080.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13560 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/080.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13562 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/081.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13570 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/081.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13572 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/082.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13580 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/082.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13582 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/083.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13590 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/083.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13592 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/084.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13600 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/084.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13602 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/085.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13610 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/085.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13612 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/086.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13620 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/086.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13622 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/087.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13630 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/087.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13632 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/088.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13640 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/088.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13642 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/089.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13650 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/089.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13652 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/090.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13660 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/090.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13662 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/091.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13670 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/091.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13672 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/092.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13680 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/092.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13682 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/093.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13690 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/093.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13692 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/094.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13700 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/094.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13702 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/095.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13710 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/095.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13712 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/096.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13720 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/096.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13722 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/097.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13730 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/097.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13732 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/098.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13740 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/098.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13742 |
| /workspace/datasets/visa/capsules/Data/Images/Anomaly/099.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13750 |
| /workspace/datasets/visa/capsules/Data/Masks/Anomaly/099.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:13752 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13760 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13770 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13780 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13790 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13800 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13810 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13830 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/062.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13840 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/100.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13860 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/107.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13870 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/152.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13880 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/159.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13890 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/168.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13900 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/170.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13910 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/172.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13920 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/174.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13930 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/178.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13940 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/179.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13950 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/187.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13960 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/196.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13970 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/208.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13980 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/214.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:13990 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/215.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14000 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/237.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14010 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/240.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14020 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/261.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14030 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/286.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14040 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/288.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14050 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/294.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14060 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/297.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14070 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/303.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14080 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/306.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14090 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/320.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14100 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/324.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14110 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/333.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14120 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/363.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14130 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/377.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14140 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/394.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14150 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/400.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14160 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/402.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14170 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/417.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14180 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/423.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14190 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/427.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14200 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/457.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14210 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/469.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14220 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/479.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14230 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/483.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14240 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/484.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14250 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/488.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14260 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/490.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14270 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/514.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14280 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/518.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14290 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/520.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14300 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/525.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14310 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/545.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14320 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/552.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14330 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/569.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14340 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/576.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14350 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/580.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14360 |
| /workspace/datasets/visa/capsules/Data/Images/Normal/594.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14380 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/000.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14390 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/000.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14392 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/001.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14400 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/001.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14402 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/002.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14410 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/002.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14412 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/003.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14420 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/003.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14422 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/004.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14430 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/004.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14432 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/005.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14440 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/005.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14442 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/006.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14450 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/006.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14452 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/007.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14460 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/007.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14462 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/008.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14470 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/008.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14472 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/009.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14480 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/009.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14482 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/010.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14490 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/010.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14492 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14500 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/011.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14502 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/012.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14510 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/012.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14512 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14520 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/013.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14522 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/014.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14530 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/014.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14532 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/015.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14540 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/015.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14542 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14550 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/016.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14552 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/017.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14560 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/017.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14562 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/018.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14570 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/018.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14572 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/019.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14580 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/019.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14582 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/020.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14590 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/020.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14592 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/021.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14600 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/021.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14602 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/022.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14610 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/022.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14612 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/023.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14620 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/023.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14622 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14630 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/024.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14632 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/025.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14640 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/025.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14642 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14650 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/026.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14652 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14660 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/027.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14662 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/028.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14670 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/028.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14672 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/029.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14680 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/029.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14682 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/030.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14690 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/030.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14692 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/031.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14700 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/031.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14702 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/032.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14710 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/032.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14712 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/033.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14720 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/033.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14722 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/034.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14730 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/034.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14732 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/035.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14740 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/035.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14742 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/036.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14750 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/036.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14752 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/037.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14760 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/037.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14762 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/038.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14770 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/038.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14772 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/039.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14780 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/039.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14782 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/040.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14790 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/040.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14792 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/041.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14800 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/041.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14802 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/042.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14810 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/042.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14812 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/043.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14820 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/043.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14822 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/044.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14830 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/044.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14832 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/045.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14840 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/045.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14842 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14850 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/046.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14852 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/047.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14860 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/047.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14862 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/048.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14870 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/048.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14872 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/049.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14880 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/049.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14882 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/050.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14890 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/050.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14892 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/051.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14900 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/051.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14902 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/052.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14910 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/052.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14912 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/053.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14920 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/053.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14922 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/054.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14930 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/054.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14932 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/055.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14940 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/055.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14942 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/056.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14950 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/056.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14952 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/057.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14960 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/057.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14962 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/058.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14970 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/058.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14972 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/059.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14980 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/059.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14982 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/060.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:14990 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/060.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:14992 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/061.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15000 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/061.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15002 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/062.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15010 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/062.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15012 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/063.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15020 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/063.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15022 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/064.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15030 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/064.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15032 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/065.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15040 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/065.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15042 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/066.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15050 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/066.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15052 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/067.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15060 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/067.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15062 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/068.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15070 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/068.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15072 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/069.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15080 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/069.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15082 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/070.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15090 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/070.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15092 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/071.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15100 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/071.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15102 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/072.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15110 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/072.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15112 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/073.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15120 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/073.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15122 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/074.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15130 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/074.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15132 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/075.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15140 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/075.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15142 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/076.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15150 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/076.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15152 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/077.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15160 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/077.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15162 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/078.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15170 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/078.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15172 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/079.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15180 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/079.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15182 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/080.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15190 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/080.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15192 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/081.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15200 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/081.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15202 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/082.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15210 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/082.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15212 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/083.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15220 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/083.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15222 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/084.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15230 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/084.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15232 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/085.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15240 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/085.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15242 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/086.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15250 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/086.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15252 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/087.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15260 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/087.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15262 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/088.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15270 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/088.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15272 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/089.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15280 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/089.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15282 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/090.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15290 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/090.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15292 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/091.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15300 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/091.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15302 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/092.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15310 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/092.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15312 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/093.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15320 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/093.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15322 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/094.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15330 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/094.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15332 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/095.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15340 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/095.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15342 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/096.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15350 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/096.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15352 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/097.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15360 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/097.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15362 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/098.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15370 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/098.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15372 |
| /workspace/datasets/visa/cashew/Data/Images/Anomaly/099.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15380 |
| /workspace/datasets/visa/cashew/Data/Masks/Anomaly/099.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15382 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/006.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15390 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/012.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15400 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15410 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/023.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15430 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/050.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15440 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/084.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15450 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/087.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15460 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/089.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15470 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/093.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15480 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/098.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15490 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/104.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15500 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/130.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15510 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/143.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15520 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/148.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15530 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/166.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15540 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/181.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15550 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/213.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15560 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/228.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15570 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/239.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15580 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/244.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15590 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/245.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15600 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/260.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15610 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/272.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15620 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/276.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15630 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/284.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15640 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/307.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15670 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/309.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15680 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/324.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15690 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/337.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15700 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/342.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15710 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/344.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15720 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/352.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15730 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/367.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15740 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/369.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15750 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/377.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15760 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/384.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15770 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/389.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15780 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/392.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15790 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/398.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15800 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/400.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15810 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/402.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15820 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/405.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15830 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/435.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15840 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/446.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15850 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/460.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15860 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/461.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15870 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/467.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15880 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/482.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15890 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/484.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15900 |
| /workspace/datasets/visa/cashew/Data/Images/Normal/487.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15910 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/000.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15920 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/000.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15922 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/001.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15930 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/001.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15932 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/002.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15940 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/002.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15942 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/003.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15950 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/003.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15952 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/004.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15960 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/004.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15962 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/005.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15970 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/005.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15972 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/006.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15980 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/006.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15982 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/007.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:15990 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/007.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:15992 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/008.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16000 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/008.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16002 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/009.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16010 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/009.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16012 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/010.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16020 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/010.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16022 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16030 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/011.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16032 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/012.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16040 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/012.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16042 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16050 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/013.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16052 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/014.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16060 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/014.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16062 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/015.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16070 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/015.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16072 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16080 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/016.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16082 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/017.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16090 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/017.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16092 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/018.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16100 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/018.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16102 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/019.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16110 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/019.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16112 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/020.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16120 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/020.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16122 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/021.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16130 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/021.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16132 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/022.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16140 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/022.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16142 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/023.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16150 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/023.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16152 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16160 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/024.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16162 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/025.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16170 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/025.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16172 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16180 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/026.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16182 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16190 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/027.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16192 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/028.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16200 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/028.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16202 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/029.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16210 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/029.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16212 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/030.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16220 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/030.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16222 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/031.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16230 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/031.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16232 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/032.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16240 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/032.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16242 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/033.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16250 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/033.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16252 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/034.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16260 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/034.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16262 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/035.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16270 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/035.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16272 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/036.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16280 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/036.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16282 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/037.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16290 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/037.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16292 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/038.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16300 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/038.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16302 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/039.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16310 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/039.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16312 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/040.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16320 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/040.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16322 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/041.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16330 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/041.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16332 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/042.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16340 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/042.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16342 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/043.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16350 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/043.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16352 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/044.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16360 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/044.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16362 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/045.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16370 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/045.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16372 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16380 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/046.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16382 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/047.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16390 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/047.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16392 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/048.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16400 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/048.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16402 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/049.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16410 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/049.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16412 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/050.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16420 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/050.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16422 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/051.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16430 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/051.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16432 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/052.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16440 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/052.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16442 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/053.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16450 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/053.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16452 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/054.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16460 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/054.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16462 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/055.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16470 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/055.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16472 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/056.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16480 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/056.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16482 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/057.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16490 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/057.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16492 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/058.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16500 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/058.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16502 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/059.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16510 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/059.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16512 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/060.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16520 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/060.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16522 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/061.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16530 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/061.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16532 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/062.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16540 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/062.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16542 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/063.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16550 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/063.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16552 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/064.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16560 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/064.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16562 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/065.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16570 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/065.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16572 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/066.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16580 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/066.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16582 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/067.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16590 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/067.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16592 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/068.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16600 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/068.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16602 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/069.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16610 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/069.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16612 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/070.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16620 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/070.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16622 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/071.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16630 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/071.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16632 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/072.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16640 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/072.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16642 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/073.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16650 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/073.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16652 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/074.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16660 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/074.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16662 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/075.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16670 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/075.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16672 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/076.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16680 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/076.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16682 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/077.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16690 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/077.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16692 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/078.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16700 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/078.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16702 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/079.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16710 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/079.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16712 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/080.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16720 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/080.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16722 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/081.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16730 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/081.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16732 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/082.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16740 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/082.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16742 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/083.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16750 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/083.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16752 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/084.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16760 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/084.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16762 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/085.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16770 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/085.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16772 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/086.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16780 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/086.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16782 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/087.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16790 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/087.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16792 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/088.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16800 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/088.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16802 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/089.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16810 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/089.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16812 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/090.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16820 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/090.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16822 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/091.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16830 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/091.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16832 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/092.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16840 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/092.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16842 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/093.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16850 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/093.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16852 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/094.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16860 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/094.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16862 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/095.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16870 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/095.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16872 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/096.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16880 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/096.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16882 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/097.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16890 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/097.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16892 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/098.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16900 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/098.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16902 |
| /workspace/datasets/visa/chewinggum/Data/Images/Anomaly/099.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16910 |
| /workspace/datasets/visa/chewinggum/Data/Masks/Anomaly/099.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:16912 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/006.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16920 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/012.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16930 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16940 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/050.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16960 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/084.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16970 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/087.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16980 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/089.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:16990 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/093.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17000 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/098.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17010 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/104.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17020 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/130.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17030 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/143.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17040 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/148.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17050 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/166.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17060 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/181.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17070 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/213.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17080 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/228.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17090 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/239.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17100 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/244.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17110 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/245.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17120 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/260.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17130 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/272.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17140 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/276.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17150 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/284.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17160 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/307.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17190 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/309.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17200 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/324.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17210 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/337.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17220 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/342.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17230 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/344.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17240 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/352.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17250 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/367.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17260 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/369.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17270 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/377.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17280 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/384.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17290 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/389.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17300 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/392.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17310 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/398.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17320 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/400.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17330 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/402.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17340 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/405.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17350 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/435.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17360 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/446.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17370 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/460.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17380 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/461.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17390 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/467.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17400 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/482.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17410 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/486.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17420 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/487.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17430 |
| /workspace/datasets/visa/chewinggum/Data/Images/Normal/497.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17440 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/000.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17450 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/000.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17452 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/001.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17460 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/001.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17462 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/002.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17470 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/002.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17472 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/003.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17480 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/003.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17482 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/004.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17490 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/004.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17492 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/005.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17500 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/005.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17502 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/006.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17510 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/006.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17512 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/007.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17520 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/007.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17522 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/008.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17530 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/008.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17532 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/009.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17540 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/009.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17542 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/010.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17550 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/010.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17552 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17560 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/011.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17562 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/012.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17570 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/012.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17572 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17580 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/013.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17582 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/014.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17590 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/014.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17592 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/015.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17600 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/015.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17602 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17610 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/016.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17612 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/017.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17620 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/017.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17622 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/018.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17630 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/018.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17632 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/019.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17640 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/019.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17642 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/020.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17650 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/020.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17652 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/021.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17660 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/021.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17662 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/022.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17670 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/022.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17672 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/023.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17680 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/023.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17682 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17690 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/024.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17692 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/025.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17700 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/025.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17702 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17710 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/026.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17712 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17720 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/027.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17722 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/028.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17730 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/028.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17732 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/029.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17740 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/029.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17742 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/030.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17750 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/030.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17752 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/031.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17760 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/031.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17762 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/032.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17770 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/032.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17772 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/033.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17780 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/033.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17782 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/034.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17790 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/034.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17792 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/035.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17800 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/035.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17802 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/036.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17810 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/036.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17812 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/037.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17820 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/037.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17822 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/038.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17830 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/038.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17832 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/039.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17840 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/039.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17842 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/040.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17850 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/040.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17852 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/041.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17860 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/041.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17862 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/042.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17870 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/042.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17872 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/043.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17880 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/043.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17882 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/044.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17890 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/044.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17892 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/045.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17900 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/045.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17902 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17910 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/046.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17912 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/047.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17920 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/047.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17922 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/048.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17930 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/048.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17932 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/049.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17940 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/049.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17942 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/050.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17950 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/050.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17952 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/051.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17960 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/051.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17962 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/052.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17970 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/052.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17972 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/053.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17980 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/053.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17982 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/054.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:17990 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/054.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:17992 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/055.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18000 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/055.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18002 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/056.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18010 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/056.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18012 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/057.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18020 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/057.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18022 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/058.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18030 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/058.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18032 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/059.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18040 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/059.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18042 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/060.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18050 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/060.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18052 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/061.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18060 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/061.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18062 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/062.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18070 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/062.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18072 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/063.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18080 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/063.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18082 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/064.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18090 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/064.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18092 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/065.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18100 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/065.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18102 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/066.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18110 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/066.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18112 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/067.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18120 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/067.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18122 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/068.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18130 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/068.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18132 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/069.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18140 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/069.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18142 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/070.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18150 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/070.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18152 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/071.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18160 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/071.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18162 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/072.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18170 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/072.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18172 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/073.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18180 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/073.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18182 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/074.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18190 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/074.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18192 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/075.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18200 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/075.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18202 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/076.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18210 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/076.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18212 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/077.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18220 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/077.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18222 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/078.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18230 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/078.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18232 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/079.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18240 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/079.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18242 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/080.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18250 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/080.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18252 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/081.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18260 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/081.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18262 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/082.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18270 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/082.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18272 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/083.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18280 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/083.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18282 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/084.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18290 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/084.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18292 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/085.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18300 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/085.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18302 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/086.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18310 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/086.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18312 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/087.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18320 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/087.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18322 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/088.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18330 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/088.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18332 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/089.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18340 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/089.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18342 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/090.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18350 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/090.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18352 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/091.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18360 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/091.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18362 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/092.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18370 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/092.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18372 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/093.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18380 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/093.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18382 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/094.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18390 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/094.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18392 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/095.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18400 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/095.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18402 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/096.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18410 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/096.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18412 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/097.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18420 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/097.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18422 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/098.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18430 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/098.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18432 |
| /workspace/datasets/visa/fryum/Data/Images/Anomaly/099.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18440 |
| /workspace/datasets/visa/fryum/Data/Masks/Anomaly/099.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18442 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/006.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18450 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/012.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18460 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18470 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/023.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18490 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/050.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18500 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/084.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18510 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/087.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18520 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/089.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18530 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/093.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18540 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/098.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18550 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/104.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18560 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/130.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18570 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/143.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18580 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/148.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18590 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/166.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18600 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/181.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18610 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/213.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18620 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/228.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18630 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/239.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18640 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/244.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18650 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/245.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18660 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/260.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18670 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/272.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18680 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/276.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18690 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/284.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18700 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/307.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18730 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/309.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18740 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/324.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18750 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/337.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18760 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/342.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18770 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/344.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18780 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/352.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18790 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/367.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18800 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/369.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18810 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/377.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18820 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/384.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18830 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/389.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18840 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/392.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18850 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/398.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18860 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/400.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18870 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/402.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18880 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/405.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18890 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/435.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18900 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/446.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18910 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/460.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18920 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/461.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18930 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/467.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18940 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/482.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18950 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/484.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18960 |
| /workspace/datasets/visa/fryum/Data/Images/Normal/487.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18970 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/000.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18980 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/000.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18982 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/001.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:18990 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/001.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:18992 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/002.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19000 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/002.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19002 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/003.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19010 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/003.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19012 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/004.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19020 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/004.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19022 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/005.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19030 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/005.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19032 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/006.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19040 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/006.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19042 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/007.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19050 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/007.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19052 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/008.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19060 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/008.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19062 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/009.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19070 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/009.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19072 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/010.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19080 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/010.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19082 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19090 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/011.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19092 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/012.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19100 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/012.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19102 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19110 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/013.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19112 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/014.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19120 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/014.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19122 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/015.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19130 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/015.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19132 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19140 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/016.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19142 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/017.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19150 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/017.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19152 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/018.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19160 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/018.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19162 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/019.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19170 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/019.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19172 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/020.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19180 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/020.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19182 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/021.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19190 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/021.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19192 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/022.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19200 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/022.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19202 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/023.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19210 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/023.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19212 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19220 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/024.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19222 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/025.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19230 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/025.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19232 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19240 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/026.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19242 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19250 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/027.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19252 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/028.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19260 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/028.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19262 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/029.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19270 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/029.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19272 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/030.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19280 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/030.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19282 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/031.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19290 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/031.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19292 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/032.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19300 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/032.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19302 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/033.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19310 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/033.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19312 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/034.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19320 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/034.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19322 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/035.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19330 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/035.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19332 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/036.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19340 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/036.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19342 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/037.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19350 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/037.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19352 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/038.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19360 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/038.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19362 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/039.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19370 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/039.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19372 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/040.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19380 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/040.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19382 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/041.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19390 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/041.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19392 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/042.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19400 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/042.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19402 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/043.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19410 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/043.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19412 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/044.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19420 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/044.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19422 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/045.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19430 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/045.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19432 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19440 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/046.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19442 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/047.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19450 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/047.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19452 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/048.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19460 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/048.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19462 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/049.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19470 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/049.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19472 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/050.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19480 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/050.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19482 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/051.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19490 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/051.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19492 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/052.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19500 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/052.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19502 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/053.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19510 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/053.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19512 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/054.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19520 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/054.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19522 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/055.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19530 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/055.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19532 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/056.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19540 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/056.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19542 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/057.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19550 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/057.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19552 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/058.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19560 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/058.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19562 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/059.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19570 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/059.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19572 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/060.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19580 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/060.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19582 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/061.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19590 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/061.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19592 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/062.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19600 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/062.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19602 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/063.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19610 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/063.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19612 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/064.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19620 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/064.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19622 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/065.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19630 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/065.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19632 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/066.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19640 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/066.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19642 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/067.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19650 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/067.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19652 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/068.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19660 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/068.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19662 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/069.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19670 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/069.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19672 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/070.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19680 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/070.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19682 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/071.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19690 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/071.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19692 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/072.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19700 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/072.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19702 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/073.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19710 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/073.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19712 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/074.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19720 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/074.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19722 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/075.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19730 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/075.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19732 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/076.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19740 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/076.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19742 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/077.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19750 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/077.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19752 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/078.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19760 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/078.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19762 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/079.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19770 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/079.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19772 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/080.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19780 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/080.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19782 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/081.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19790 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/081.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19792 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/082.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19800 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/082.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19802 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/083.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19810 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/083.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19812 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/084.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19820 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/084.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19822 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/085.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19830 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/085.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19832 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/086.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19840 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/086.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19842 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/087.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19850 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/087.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19852 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/088.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19860 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/088.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19862 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/089.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19870 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/089.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19872 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/090.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19880 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/090.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19882 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/091.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19890 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/091.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19892 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/092.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19900 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/092.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19902 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/093.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19910 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/093.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19912 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/094.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19920 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/094.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19922 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/095.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19930 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/095.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19932 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/096.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19940 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/096.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19942 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/097.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19950 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/097.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19952 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/098.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19960 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/098.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19962 |
| /workspace/datasets/visa/macaroni1/Data/Images/Anomaly/099.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19970 |
| /workspace/datasets/visa/macaroni1/Data/Masks/Anomaly/099.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:19972 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19980 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:19990 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20000 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20010 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20020 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20030 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20050 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0100.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20060 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0107.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20070 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0159.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20080 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0168.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20090 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0170.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20100 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0172.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20110 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0174.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20120 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0178.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20130 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0187.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20140 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0196.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20150 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0208.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20160 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0214.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20170 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0215.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20180 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0237.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20190 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0261.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20200 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0286.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20210 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0294.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20220 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0297.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20230 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0303.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20240 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0306.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20250 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0320.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20260 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0333.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20270 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0363.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20280 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0377.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20290 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0394.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20300 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0400.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20310 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0402.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20320 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0417.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20330 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0423.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20340 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0427.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20350 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0457.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20360 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0469.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20370 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0479.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20380 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0483.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20390 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0484.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20400 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0488.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20410 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0490.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20420 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0514.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20430 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0518.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20440 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0520.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20450 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0525.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20460 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0545.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20470 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0552.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20480 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0569.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20490 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0615.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20520 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0617.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20530 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0619.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20540 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0621.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20550 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0629.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20560 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0631.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20570 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0648.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20580 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0654.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20590 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0657.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20600 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0659.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20610 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0674.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20620 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0684.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20630 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0685.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20640 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0688.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20650 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0690.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20660 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0694.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20670 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0705.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20680 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0725.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20690 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0730.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20700 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0735.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20710 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0739.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20720 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0751.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20730 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0755.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20740 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0764.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20750 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0768.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20760 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0779.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20770 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0784.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20780 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0790.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20790 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0796.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20800 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0797.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20810 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0800.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20820 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0804.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20830 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0811.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20840 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0844.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20850 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0869.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20860 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0871.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20870 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0892.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20880 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0900.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20890 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0920.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20900 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0923.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20910 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0935.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20920 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0952.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20930 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0953.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20940 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0964.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20950 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0967.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20960 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0974.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20970 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0985.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20980 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0994.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:20990 |
| /workspace/datasets/visa/macaroni1/Data/Images/Normal/0996.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21000 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/000.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21010 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/000.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21012 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/001.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21020 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/001.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21022 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/002.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21030 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/002.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21032 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/003.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21040 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/003.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21042 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/004.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21050 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/004.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21052 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/005.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21060 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/005.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21062 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/006.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21070 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/006.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21072 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/007.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21080 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/007.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21082 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/008.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21090 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/008.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21092 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/009.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21100 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/009.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21102 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/010.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21110 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/010.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21112 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21120 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/011.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21122 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/012.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21130 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/012.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21132 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21140 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/013.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21142 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/014.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21150 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/014.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21152 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/015.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21160 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/015.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21162 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21170 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/016.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21172 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/017.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21180 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/017.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21182 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/018.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21190 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/018.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21192 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/019.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21200 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/019.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21202 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/020.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21210 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/020.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21212 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/021.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21220 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/021.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21222 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/022.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21230 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/022.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21232 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/023.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21240 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/023.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21242 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21250 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/024.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21252 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/025.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21260 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/025.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21262 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21270 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/026.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21272 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21280 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/027.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21282 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/028.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21290 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/028.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21292 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/029.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21300 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/029.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21302 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/030.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21310 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/030.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21312 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/031.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21320 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/031.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21322 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/032.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21330 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/032.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21332 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/033.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21340 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/033.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21342 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/034.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21350 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/034.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21352 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/035.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21360 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/035.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21362 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/036.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21370 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/036.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21372 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/037.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21380 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/037.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21382 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/038.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21390 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/038.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21392 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/039.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21400 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/039.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21402 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/040.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21410 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/040.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21412 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/041.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21420 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/041.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21422 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/042.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21430 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/042.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21432 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/043.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21440 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/043.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21442 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/044.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21450 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/044.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21452 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/045.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21460 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/045.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21462 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21470 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/046.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21472 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/047.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21480 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/047.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21482 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/048.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21490 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/048.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21492 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/049.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21500 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/049.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21502 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/050.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21510 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/050.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21512 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/051.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21520 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/051.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21522 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/052.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21530 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/052.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21532 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/053.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21540 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/053.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21542 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/054.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21550 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/054.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21552 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/055.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21560 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/055.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21562 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/056.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21570 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/056.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21572 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/057.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21580 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/057.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21582 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/058.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21590 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/058.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21592 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/059.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21600 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/059.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21602 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/060.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21610 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/060.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21612 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/061.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21620 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/061.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21622 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/062.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21630 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/062.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21632 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/063.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21640 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/063.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21642 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/064.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21650 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/064.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21652 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/065.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21660 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/065.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21662 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/066.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21670 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/066.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21672 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/067.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21680 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/067.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21682 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/068.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21690 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/068.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21692 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/069.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21700 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/069.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21702 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/070.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21710 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/070.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21712 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/071.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21720 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/071.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21722 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/072.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21730 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/072.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21732 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/073.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21740 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/073.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21742 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/074.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21750 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/074.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21752 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/075.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21760 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/075.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21762 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/076.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21770 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/076.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21772 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/077.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21780 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/077.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21782 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/078.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21790 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/078.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21792 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/079.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21800 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/079.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21802 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/080.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21810 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/080.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21812 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/081.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21820 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/081.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21822 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/082.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21830 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/082.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21832 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/083.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21840 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/083.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21842 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/084.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21850 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/084.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21852 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/085.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21860 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/085.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21862 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/086.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21870 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/086.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21872 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/087.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21880 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/087.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21882 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/088.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21890 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/088.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21892 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/089.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21900 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/089.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21902 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/090.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21910 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/090.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21912 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/091.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21920 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/091.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21922 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/092.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21930 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/092.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21932 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/093.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21940 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/093.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21942 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/094.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21950 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/094.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21952 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/095.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21960 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/095.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21962 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/096.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21970 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/096.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21972 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/097.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21980 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/097.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21982 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/098.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:21990 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/098.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:21992 |
| /workspace/datasets/visa/macaroni2/Data/Images/Anomaly/099.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22000 |
| /workspace/datasets/visa/macaroni2/Data/Masks/Anomaly/099.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:22002 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22010 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22020 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22030 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22040 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22050 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22060 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22080 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0100.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22090 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0107.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22100 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0159.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22110 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0168.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22120 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0170.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22130 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0172.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22140 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0174.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22150 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0178.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22160 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0187.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22170 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0196.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22180 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0208.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22190 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0214.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22200 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0215.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22210 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0237.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22220 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0261.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22230 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0286.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22240 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0294.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22250 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0297.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22260 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0303.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22270 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0306.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22280 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0320.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22290 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0333.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22300 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0363.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22310 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0377.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22320 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0394.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22330 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0400.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22340 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0402.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22350 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0417.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22360 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0423.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22370 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0427.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22380 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0457.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22390 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0469.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22400 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0479.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22410 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0483.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22420 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0484.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22430 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0488.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22440 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0490.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22450 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0514.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22460 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0518.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22470 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0520.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22480 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0525.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22490 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0545.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22500 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0552.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22510 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0569.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22520 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0615.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22550 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0617.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22560 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0619.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22570 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0621.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22580 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0629.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22590 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0631.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22600 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0648.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22610 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0654.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22620 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0657.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22630 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0659.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22640 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0674.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22650 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0684.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22660 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0685.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22670 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0688.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22680 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0690.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22690 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0694.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22700 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0705.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22710 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0725.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22720 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0730.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22730 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0735.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22740 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0739.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22750 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0751.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22760 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0755.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22770 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0764.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22780 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0768.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22790 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0779.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22800 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0784.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22810 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0790.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22820 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0796.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22830 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0797.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22840 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0800.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22850 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0804.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22860 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0811.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22870 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0844.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22880 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0869.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22890 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0871.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22900 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0892.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22910 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0900.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22920 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0920.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22930 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0923.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22940 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0935.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22950 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0952.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22960 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0953.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22970 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0964.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22980 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0967.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:22990 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0974.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23000 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0985.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23010 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0994.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23020 |
| /workspace/datasets/visa/macaroni2/Data/Images/Normal/0996.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23030 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/000.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23040 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/000.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23042 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/001.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23050 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/001.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23052 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/002.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23060 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/002.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23062 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/003.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23070 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/003.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23072 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/004.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23080 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/004.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23082 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/005.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23090 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/005.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23092 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/006.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23100 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/006.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23102 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/007.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23110 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/007.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23112 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/008.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23120 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/008.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23122 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/009.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23130 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/009.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23132 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/010.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23140 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/010.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23142 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23150 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/011.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23152 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/012.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23160 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/012.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23162 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23170 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/013.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23172 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/014.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23180 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/014.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23182 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/015.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23190 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/015.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23192 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23200 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/016.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23202 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/017.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23210 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/017.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23212 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/018.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23220 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/018.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23222 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/019.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23230 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/019.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23232 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/020.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23240 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/020.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23242 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/021.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23250 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/021.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23252 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/022.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23260 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/022.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23262 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/023.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23270 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/023.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23272 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23280 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/024.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23282 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/025.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23290 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/025.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23292 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23300 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/026.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23302 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23310 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/027.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23312 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/028.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23320 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/028.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23322 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/029.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23330 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/029.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23332 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/030.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23340 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/030.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23342 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/031.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23350 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/031.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23352 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/032.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23360 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/032.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23362 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/033.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23370 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/033.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23372 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/034.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23380 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/034.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23382 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/035.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23390 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/035.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23392 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/036.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23400 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/036.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23402 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/037.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23410 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/037.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23412 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/038.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23420 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/038.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23422 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/039.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23430 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/039.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23432 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/040.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23440 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/040.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23442 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/041.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23450 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/041.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23452 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/042.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23460 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/042.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23462 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/043.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23470 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/043.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23472 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/044.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23480 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/044.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23482 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/045.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23490 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/045.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23492 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23500 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/046.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23502 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/047.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23510 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/047.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23512 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/048.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23520 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/048.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23522 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/049.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23530 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/049.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23532 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/050.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23540 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/050.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23542 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/051.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23550 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/051.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23552 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/052.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23560 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/052.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23562 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/053.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23570 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/053.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23572 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/054.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23580 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/054.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23582 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/055.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23590 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/055.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23592 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/056.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23600 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/056.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23602 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/057.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23610 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/057.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23612 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/058.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23620 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/058.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23622 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/059.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23630 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/059.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23632 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/060.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23640 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/060.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23642 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/061.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23650 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/061.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23652 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/062.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23660 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/062.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23662 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/063.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23670 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/063.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23672 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/064.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23680 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/064.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23682 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/065.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23690 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/065.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23692 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/066.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23700 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/066.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23702 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/067.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23710 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/067.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23712 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/068.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23720 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/068.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23722 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/069.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23730 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/069.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23732 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/070.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23740 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/070.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23742 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/071.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23750 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/071.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23752 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/072.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23760 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/072.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23762 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/073.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23770 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/073.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23772 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/074.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23780 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/074.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23782 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/075.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23790 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/075.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23792 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/076.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23800 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/076.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23802 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/077.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23810 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/077.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23812 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/078.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23820 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/078.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23822 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/079.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23830 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/079.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23832 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/080.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23840 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/080.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23842 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/081.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23850 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/081.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23852 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/082.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23860 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/082.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23862 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/083.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23870 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/083.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23872 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/084.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23880 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/084.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23882 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/085.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23890 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/085.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23892 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/086.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23900 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/086.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23902 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/087.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23910 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/087.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23912 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/088.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23920 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/088.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23922 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/089.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23930 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/089.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23932 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/090.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23940 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/090.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23942 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/091.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23950 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/091.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23952 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/092.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23960 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/092.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23962 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/093.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23970 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/093.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23972 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/094.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23980 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/094.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23982 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/095.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:23990 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/095.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:23992 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/096.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24000 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/096.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:24002 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/097.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24010 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/097.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:24012 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/098.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24020 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/098.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:24022 |
| /workspace/datasets/visa/pcb1/Data/Images/Anomaly/099.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24030 |
| /workspace/datasets/visa/pcb1/Data/Masks/Anomaly/099.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:24032 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24040 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24050 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24060 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24070 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24080 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24090 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24110 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0100.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24120 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0107.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24130 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0159.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24140 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0168.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24150 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0170.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24160 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0172.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24170 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0174.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24180 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0178.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24190 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0187.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24200 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0196.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24210 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0208.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24220 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0214.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24230 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0215.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24240 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0237.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24250 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0261.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24260 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0286.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24270 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0294.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24280 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0297.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24290 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0303.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24300 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0306.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24310 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0320.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24320 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0333.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24330 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0363.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24340 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0377.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24350 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0394.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24360 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0400.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24370 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0402.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24380 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0417.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24390 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0423.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24400 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0427.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24410 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0457.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24420 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0469.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24430 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0479.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24440 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0483.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24450 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0484.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24460 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0488.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24470 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0490.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24480 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0514.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24490 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0518.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24500 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0520.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24510 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0525.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24520 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0545.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24530 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0552.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24540 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0569.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24550 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0615.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24580 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0617.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24590 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0619.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24600 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0621.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24610 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0629.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24620 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0631.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24630 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0648.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24640 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0654.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24650 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0657.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24660 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0659.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24670 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0674.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24680 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0684.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24690 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0685.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24700 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0688.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24710 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0690.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24720 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0694.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24730 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0705.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24740 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0725.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24750 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0730.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24760 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0735.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24770 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0739.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24780 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0751.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24790 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0755.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24800 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0764.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24810 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0768.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24820 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0779.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24830 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0784.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24840 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0796.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24850 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0797.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24860 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0800.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24870 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0804.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24880 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0811.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24890 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0844.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24900 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0869.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24910 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0871.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24920 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0892.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24930 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0900.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24940 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0920.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24950 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0923.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24960 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0935.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24970 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0940.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24980 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0952.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:24990 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0957.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25000 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0964.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25010 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0971.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25020 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0974.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25030 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0989.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25040 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/0994.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25050 |
| /workspace/datasets/visa/pcb1/Data/Images/Normal/1000.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25060 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/000.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25070 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/000.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25072 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/001.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25080 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/001.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25082 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/002.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25090 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/002.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25092 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/003.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25100 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/003.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25102 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/004.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25110 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/004.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25112 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/005.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25120 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/005.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25122 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/006.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25130 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/006.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25132 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/007.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25140 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/007.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25142 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/008.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25150 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/008.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25152 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/009.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25160 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/009.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25162 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/010.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25170 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/010.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25172 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25180 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/011.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25182 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/012.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25190 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/012.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25192 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25200 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/013.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25202 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/014.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25210 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/014.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25212 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/015.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25220 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/015.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25222 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25230 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/016.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25232 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/017.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25240 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/017.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25242 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/018.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25250 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/018.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25252 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/019.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25260 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/019.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25262 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/020.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25270 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/020.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25272 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/021.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25280 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/021.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25282 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/022.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25290 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/022.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25292 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/023.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25300 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/023.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25302 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25310 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/024.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25312 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/025.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25320 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/025.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25322 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25330 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/026.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25332 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25340 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/027.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25342 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/028.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25350 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/028.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25352 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/029.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25360 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/029.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25362 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/030.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25370 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/030.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25372 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/031.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25380 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/031.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25382 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/032.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25390 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/032.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25392 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/033.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25400 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/033.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25402 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/034.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25410 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/034.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25412 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/035.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25420 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/035.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25422 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/036.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25430 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/036.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25432 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/037.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25440 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/037.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25442 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/038.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25450 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/038.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25452 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/039.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25460 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/039.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25462 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/040.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25470 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/040.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25472 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/041.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25480 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/041.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25482 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/042.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25490 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/042.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25492 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/043.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25500 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/043.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25502 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/044.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25510 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/044.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25512 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/045.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25520 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/045.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25522 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25530 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/046.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25532 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/047.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25540 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/047.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25542 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/048.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25550 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/048.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25552 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/049.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25560 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/049.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25562 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/050.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25570 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/050.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25572 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/051.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25580 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/051.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25582 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/052.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25590 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/052.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25592 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/053.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25600 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/053.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25602 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/054.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25610 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/054.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25612 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/055.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25620 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/055.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25622 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/056.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25630 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/056.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25632 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/057.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25640 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/057.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25642 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/058.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25650 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/058.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25652 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/059.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25660 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/059.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25662 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/060.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25670 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/060.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25672 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/061.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25680 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/061.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25682 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/062.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25690 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/062.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25692 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/063.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25700 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/063.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25702 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/064.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25710 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/064.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25712 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/065.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25720 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/065.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25722 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/066.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25730 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/066.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25732 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/067.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25740 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/067.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25742 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/068.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25750 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/068.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25752 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/069.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25760 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/069.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25762 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/070.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25770 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/070.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25772 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/071.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25780 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/071.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25782 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/072.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25790 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/072.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25792 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/073.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25800 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/073.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25802 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/074.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25810 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/074.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25812 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/075.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25820 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/075.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25822 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/076.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25830 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/076.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25832 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/077.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25840 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/077.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25842 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/078.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25850 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/078.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25852 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/079.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25860 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/079.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25862 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/080.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25870 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/080.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25872 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/081.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25880 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/081.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25882 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/082.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25890 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/082.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25892 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/083.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25900 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/083.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25902 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/084.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25910 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/084.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25912 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/085.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25920 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/085.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25922 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/086.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25930 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/086.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25932 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/087.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25940 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/087.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25942 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/088.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25950 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/088.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25952 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/089.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25960 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/089.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25962 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/090.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25970 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/090.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25972 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/091.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25980 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/091.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25982 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/092.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:25990 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/092.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:25992 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/093.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26000 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/093.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:26002 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/094.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26010 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/094.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:26012 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/095.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26020 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/095.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:26022 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/096.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26030 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/096.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:26032 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/097.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26040 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/097.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:26042 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/098.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26050 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/098.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:26052 |
| /workspace/datasets/visa/pcb2/Data/Images/Anomaly/099.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26060 |
| /workspace/datasets/visa/pcb2/Data/Masks/Anomaly/099.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:26062 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26070 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26080 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26090 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26100 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26110 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26120 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26140 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0100.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26150 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0107.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26160 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0159.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26170 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0168.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26180 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0170.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26190 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0172.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26200 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0174.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26210 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0178.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26220 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0187.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26230 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0196.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26240 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0208.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26250 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0214.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26260 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0215.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26270 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0237.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26280 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0261.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26290 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0286.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26300 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0294.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26310 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0297.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26320 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0303.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26330 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0306.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26340 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0320.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26350 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0333.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26360 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0363.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26370 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0377.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26380 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0394.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26390 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0400.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26400 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0402.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26410 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0417.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26420 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0423.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26430 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0427.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26440 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0457.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26450 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0469.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26460 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0479.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26470 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0483.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26480 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0484.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26490 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0488.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26500 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0490.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26510 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0514.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26520 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0518.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26530 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0520.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26540 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0525.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26550 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0545.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26560 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0552.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26570 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0569.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26580 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0615.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26610 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0617.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26620 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0619.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26630 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0621.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26640 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0629.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26650 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0631.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26660 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0648.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26670 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0654.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26680 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0657.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26690 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0659.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26700 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0674.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26710 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0684.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26720 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0685.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26730 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0688.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26740 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0690.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26750 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0694.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26760 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0705.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26770 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0725.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26780 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0730.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26790 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0735.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26800 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0739.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26810 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0751.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26820 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0755.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26830 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0764.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26840 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0768.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26850 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0779.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26860 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0784.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26870 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0796.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26880 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0797.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26890 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0800.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26900 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0804.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26910 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0811.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26920 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0844.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26930 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0869.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26940 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0871.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26950 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0892.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26960 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0900.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26970 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0920.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26980 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0923.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:26990 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0935.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27000 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0940.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27010 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0952.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27020 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0954.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27030 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0964.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27040 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0968.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27050 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0974.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27060 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0986.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27070 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0994.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27080 |
| /workspace/datasets/visa/pcb2/Data/Images/Normal/0997.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27090 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/000.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27100 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/000.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27102 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/001.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27110 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/001.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27112 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/002.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27120 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/002.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27122 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/003.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27130 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/003.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27132 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/004.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27140 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/004.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27142 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/005.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27150 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/005.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27152 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/006.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27160 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/006.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27162 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/007.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27170 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/007.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27172 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/008.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27180 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/008.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27182 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/009.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27190 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/009.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27192 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/010.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27200 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/010.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27202 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27210 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/011.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27212 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/012.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27220 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/012.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27222 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27230 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/013.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27232 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/014.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27240 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/014.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27242 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/015.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27250 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/015.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27252 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27260 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/016.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27262 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/017.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27270 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/017.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27272 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/018.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27280 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/018.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27282 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/019.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27290 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/019.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27292 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/020.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27300 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/020.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27302 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/021.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27310 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/021.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27312 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/022.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27320 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/022.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27322 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/023.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27330 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/023.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27332 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27340 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/024.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27342 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/025.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27350 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/025.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27352 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27360 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/026.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27362 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27370 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/027.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27372 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/028.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27380 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/028.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27382 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/029.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27390 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/029.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27392 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/030.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27400 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/030.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27402 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/031.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27410 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/031.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27412 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/032.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27420 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/032.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27422 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/033.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27430 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/033.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27432 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/034.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27440 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/034.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27442 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/035.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27450 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/035.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27452 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/036.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27460 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/036.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27462 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/037.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27470 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/037.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27472 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/038.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27480 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/038.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27482 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/039.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27490 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/039.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27492 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/040.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27500 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/040.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27502 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/041.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27510 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/041.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27512 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/042.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27520 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/042.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27522 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/043.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27530 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/043.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27532 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/044.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27540 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/044.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27542 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/045.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27550 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/045.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27552 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27560 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/046.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27562 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/047.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27570 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/047.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27572 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/048.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27580 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/048.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27582 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/049.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27590 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/049.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27592 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/050.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27600 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/050.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27602 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/051.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27610 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/051.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27612 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/052.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27620 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/052.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27622 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/053.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27630 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/053.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27632 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/054.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27640 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/054.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27642 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/055.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27650 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/055.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27652 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/056.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27660 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/056.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27662 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/057.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27670 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/057.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27672 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/058.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27680 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/058.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27682 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/059.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27690 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/059.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27692 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/060.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27700 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/060.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27702 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/061.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27710 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/061.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27712 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/062.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27720 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/062.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27722 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/063.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27730 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/063.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27732 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/064.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27740 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/064.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27742 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/065.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27750 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/065.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27752 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/066.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27760 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/066.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27762 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/067.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27770 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/067.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27772 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/068.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27780 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/068.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27782 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/069.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27790 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/069.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27792 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/070.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27800 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/070.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27802 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/071.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27810 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/071.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27812 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/072.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27820 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/072.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27822 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/073.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27830 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/073.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27832 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/074.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27840 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/074.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27842 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/075.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27850 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/075.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27852 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/076.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27860 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/076.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27862 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/077.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27870 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/077.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27872 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/078.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27880 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/078.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27882 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/079.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27890 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/079.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27892 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/080.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27900 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/080.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27902 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/081.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27910 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/081.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27912 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/082.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27920 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/082.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27922 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/083.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27930 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/083.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27932 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/084.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27940 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/084.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27942 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/085.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27950 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/085.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27952 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/086.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27960 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/086.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27962 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/087.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27970 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/087.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27972 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/088.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27980 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/088.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27982 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/089.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:27990 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/089.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:27992 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/090.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28000 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/090.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:28002 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/091.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28010 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/091.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:28012 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/092.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28020 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/092.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:28022 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/093.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28030 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/093.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:28032 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/094.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28040 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/094.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:28042 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/095.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28050 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/095.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:28052 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/096.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28060 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/096.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:28062 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/097.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28070 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/097.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:28072 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/098.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28080 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/098.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:28082 |
| /workspace/datasets/visa/pcb3/Data/Images/Anomaly/099.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28090 |
| /workspace/datasets/visa/pcb3/Data/Masks/Anomaly/099.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:28092 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28100 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28110 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28120 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28130 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28140 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28150 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28170 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0100.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28180 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0107.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28190 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0159.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28200 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0168.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28210 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0170.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28220 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0172.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28230 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0174.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28240 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0178.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28250 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0187.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28260 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0196.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28270 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0208.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28280 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0214.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28290 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0215.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28300 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0237.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28310 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0261.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28320 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0286.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28330 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0294.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28340 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0297.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28350 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0303.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28360 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0306.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28370 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0320.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28380 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0333.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28390 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0363.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28400 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0377.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28410 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0394.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28420 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0400.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28430 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0402.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28440 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0417.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28450 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0423.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28460 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0427.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28470 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0457.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28480 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0469.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28490 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0479.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28500 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0483.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28510 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0484.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28520 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0488.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28530 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0490.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28540 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0514.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28550 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0518.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28560 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0520.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28570 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0525.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28580 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0545.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28590 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0552.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28600 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0569.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28610 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0615.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28640 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0617.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28650 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0619.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28660 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0621.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28670 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0629.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28680 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0631.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28690 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0648.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28700 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0654.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28710 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0657.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28720 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0659.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28730 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0674.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28740 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0684.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28750 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0685.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28760 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0688.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28770 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0690.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28780 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0694.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28790 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0705.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28800 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0725.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28810 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0730.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28820 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0735.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28830 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0739.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28840 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0751.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28850 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0755.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28860 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0764.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28870 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0768.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28880 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0779.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28890 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0784.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28900 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0796.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28910 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0797.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28920 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0800.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28930 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0804.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28940 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0811.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28950 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0844.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28960 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0869.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28970 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0871.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28980 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0892.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:28990 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0900.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29000 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0920.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29010 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0923.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29020 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0935.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29030 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0940.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29040 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0952.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29050 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0958.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29060 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0964.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29070 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0972.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29080 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0974.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29090 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0977.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29100 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0991.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29110 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/0994.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29120 |
| /workspace/datasets/visa/pcb3/Data/Images/Normal/1002.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29130 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/000.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29140 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/000.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29142 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/001.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29150 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/001.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29152 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/002.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29160 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/002.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29162 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/003.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29170 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/003.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29172 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/004.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29180 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/004.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29182 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/005.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29190 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/005.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29192 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/006.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29200 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/006.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29202 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/007.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29210 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/007.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29212 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/008.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29220 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/008.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29222 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/009.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29230 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/009.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29232 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/010.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29240 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/010.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29242 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29250 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/011.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29252 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/012.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29260 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/012.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29262 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29270 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/013.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29272 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/014.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29280 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/014.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29282 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/015.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29290 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/015.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29292 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29300 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/016.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29302 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/017.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29310 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/017.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29312 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/018.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29320 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/018.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29322 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/019.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29330 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/019.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29332 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/020.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29340 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/020.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29342 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/021.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29350 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/021.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29352 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/022.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29360 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/022.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29362 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/023.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29370 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/023.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29372 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29380 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/024.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29382 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/025.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29390 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/025.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29392 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29400 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/026.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29402 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29410 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/027.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29412 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/028.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29420 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/028.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29422 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/029.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29430 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/029.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29432 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/030.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29440 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/030.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29442 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/031.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29450 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/031.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29452 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/032.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29460 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/032.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29462 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/033.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29470 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/033.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29472 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/034.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29480 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/034.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29482 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/035.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29490 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/035.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29492 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/036.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29500 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/036.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29502 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/037.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29510 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/037.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29512 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/038.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29520 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/038.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29522 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/039.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29530 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/039.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29532 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/040.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29540 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/040.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29542 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/041.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29550 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/041.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29552 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/042.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29560 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/042.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29562 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/043.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29570 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/043.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29572 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/044.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29580 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/044.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29582 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/045.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29590 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/045.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29592 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29600 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/046.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29602 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/047.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29610 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/047.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29612 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/048.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29620 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/048.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29622 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/049.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29630 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/049.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29632 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/050.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29640 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/050.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29642 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/051.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29650 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/051.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29652 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/052.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29660 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/052.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29662 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/053.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29670 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/053.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29672 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/054.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29680 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/054.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29682 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/055.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29690 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/055.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29692 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/056.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29700 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/056.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29702 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/057.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29710 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/057.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29712 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/058.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29720 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/058.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29722 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/059.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29730 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/059.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29732 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/060.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29740 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/060.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29742 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/061.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29750 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/061.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29752 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/062.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29760 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/062.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29762 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/063.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29770 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/063.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29772 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/064.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29780 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/064.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29782 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/065.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29790 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/065.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29792 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/066.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29800 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/066.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29802 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/067.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29810 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/067.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29812 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/068.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29820 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/068.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29822 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/069.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29830 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/069.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29832 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/070.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29840 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/070.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29842 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/071.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29850 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/071.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29852 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/072.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29860 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/072.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29862 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/073.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29870 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/073.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29872 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/074.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29880 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/074.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29882 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/075.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29890 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/075.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29892 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/076.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29900 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/076.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29902 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/077.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29910 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/077.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29912 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/078.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29920 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/078.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29922 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/079.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29930 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/079.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29932 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/080.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29940 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/080.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29942 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/081.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29950 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/081.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29952 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/082.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29960 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/082.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29962 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/083.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29970 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/083.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29972 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/084.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29980 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/084.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29982 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/085.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:29990 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/085.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:29992 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/086.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30000 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/086.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:30002 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/087.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30010 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/087.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:30012 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/088.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30020 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/088.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:30022 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/089.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30030 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/089.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:30032 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/090.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30040 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/090.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:30042 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/091.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30050 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/091.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:30052 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/092.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30060 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/092.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:30062 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/093.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30070 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/093.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:30072 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/094.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30080 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/094.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:30082 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/095.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30090 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/095.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:30092 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/096.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30100 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/096.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:30102 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/097.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30110 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/097.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:30112 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/098.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30120 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/098.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:30122 |
| /workspace/datasets/visa/pcb4/Data/Images/Anomaly/099.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30130 |
| /workspace/datasets/visa/pcb4/Data/Masks/Anomaly/099.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:30132 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30140 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30150 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30160 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30170 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30180 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30190 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30210 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0100.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30220 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0107.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30230 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0159.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30240 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0168.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30250 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0170.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30260 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0172.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30270 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0174.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30280 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0178.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30290 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0187.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30300 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0196.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30310 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0208.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30320 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0214.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30330 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0215.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30340 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0237.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30350 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0261.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30360 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0286.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30370 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0294.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30380 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0297.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30390 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0303.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30400 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0306.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30410 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0320.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30420 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0333.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30430 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0363.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30440 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0377.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30450 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0394.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30460 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0400.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30470 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0402.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30480 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0417.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30490 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0423.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30500 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0427.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30510 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0457.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30520 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0469.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30530 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0479.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30540 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0483.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30550 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0484.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30560 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0488.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30570 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0490.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30580 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0514.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30590 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0518.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30600 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0520.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30610 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0525.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30620 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0545.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30630 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0552.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30640 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0569.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30650 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0615.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30680 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0617.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30690 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0619.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30700 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0621.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30710 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0629.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30720 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0631.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30730 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0648.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30740 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0654.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30750 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0657.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30760 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0659.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30770 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0674.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30780 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0684.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30790 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0685.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30800 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0688.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30810 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0690.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30820 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0694.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30830 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0705.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30840 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0725.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30850 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0730.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30860 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0735.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30870 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0739.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30880 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0751.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30890 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0755.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30900 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0764.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30910 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0768.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30920 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0779.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30930 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0784.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30940 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0796.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30950 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0797.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30960 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0800.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30970 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0804.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30980 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0811.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:30990 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0844.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31000 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0869.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31010 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0871.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31020 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0892.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31030 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0900.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31040 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0920.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31050 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0923.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31060 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0935.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31070 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0940.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31080 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0952.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31090 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0957.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31100 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0964.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31110 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0971.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31120 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0974.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31130 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0977.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31140 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0990.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31150 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/0994.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31160 |
| /workspace/datasets/visa/pcb4/Data/Images/Normal/1001.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31170 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/000.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31180 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/000.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31182 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/001.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31190 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/001.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31192 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/002.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31200 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/002.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31202 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/003.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31210 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/003.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31212 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/004.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31220 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/004.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31222 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/005.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31230 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/005.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31232 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/006.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31240 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/006.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31242 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/007.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31250 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/007.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31252 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/008.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31260 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/008.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31262 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/009.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31270 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/009.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31272 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/010.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31280 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/010.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31282 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/011.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31290 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/011.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31292 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/012.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31300 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/012.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31302 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31310 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/013.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31312 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/014.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31320 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/014.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31322 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/015.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31330 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/015.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31332 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/016.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31340 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/016.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31342 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/017.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31350 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/017.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31352 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/018.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31360 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/018.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31362 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/019.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31370 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/019.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31372 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/020.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31380 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/020.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31382 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/021.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31390 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/021.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31392 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/022.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31400 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/022.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31402 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/023.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31410 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/023.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31412 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/024.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31420 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/024.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31422 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/025.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31430 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/025.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31432 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/026.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31440 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/026.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31442 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/027.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31450 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/027.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31452 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/028.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31460 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/028.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31462 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/029.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31470 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/029.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31472 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/030.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31480 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/030.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31482 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/031.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31490 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/031.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31492 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/032.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31500 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/032.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31502 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/033.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31510 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/033.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31512 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/034.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31520 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/034.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31522 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/035.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31530 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/035.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31532 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/036.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31540 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/036.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31542 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/037.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31550 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/037.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31552 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/038.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31560 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/038.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31562 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/039.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31570 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/039.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31572 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/040.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31580 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/040.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31582 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/041.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31590 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/041.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31592 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/042.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31600 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/042.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31602 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/043.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31610 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/043.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31612 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/044.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31620 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/044.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31622 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/045.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31630 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/045.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31632 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/046.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31640 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/046.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31642 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/047.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31650 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/047.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31652 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/048.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31660 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/048.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31662 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/049.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31670 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/049.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31672 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/050.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31680 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/050.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31682 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/051.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31690 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/051.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31692 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/052.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31700 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/052.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31702 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/053.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31710 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/053.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31712 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/054.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31720 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/054.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31722 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/055.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31730 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/055.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31732 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/056.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31740 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/056.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31742 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/057.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31750 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/057.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31752 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/058.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31760 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/058.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31762 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/059.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31770 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/059.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31772 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/060.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31780 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/060.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31782 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/061.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31790 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/061.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31792 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/062.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31800 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/062.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31802 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/063.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31810 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/063.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31812 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/064.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31820 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/064.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31822 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/065.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31830 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/065.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31832 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/066.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31840 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/066.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31842 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/067.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31850 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/067.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31852 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/068.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31860 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/068.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31862 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/069.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31870 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/069.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31872 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/070.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31880 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/070.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31882 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/071.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31890 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/071.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31892 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/072.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31900 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/072.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31902 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/073.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31910 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/073.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31912 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/074.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31920 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/074.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31922 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/075.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31930 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/075.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31932 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/076.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31940 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/076.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31942 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/077.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31950 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/077.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31952 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/078.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31960 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/078.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31962 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/079.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31970 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/079.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31972 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/080.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31980 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/080.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31982 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/081.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:31990 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/081.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:31992 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/082.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32000 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/082.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32002 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/083.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32010 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/083.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32012 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/084.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32020 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/084.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32022 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/085.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32030 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/085.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32032 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/086.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32040 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/086.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32042 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/087.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32050 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/087.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32052 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/088.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32060 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/088.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32062 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/089.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32070 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/089.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32072 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/090.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32080 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/090.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32082 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/091.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32090 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/091.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32092 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/092.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32100 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/092.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32102 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/093.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32110 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/093.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32112 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/094.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32120 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/094.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32122 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/095.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32130 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/095.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32132 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/096.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32140 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/096.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32142 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/097.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32150 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/097.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32152 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/098.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32160 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/098.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32162 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Anomaly/099.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32170 |
| /workspace/datasets/visa/pipe_fryum/Data/Masks/Anomaly/099.png | evaluation mask | no (errno 2) | unavailable | source_plan.json:32172 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/006.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32180 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/012.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32190 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/013.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32200 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/023.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32220 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/050.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32230 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/084.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32240 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/087.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32250 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/089.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32260 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/093.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32270 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/098.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32280 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/104.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32290 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/130.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32300 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/143.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32310 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/148.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32320 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/166.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32330 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/181.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32340 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/213.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32350 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/228.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32360 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/239.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32370 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/244.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32380 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/245.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32390 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/260.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32400 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/272.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32410 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/276.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32420 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/284.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32430 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/307.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32460 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/309.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32470 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/324.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32480 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/337.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32490 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/342.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32500 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/344.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32510 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/352.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32520 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/367.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32530 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/369.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32540 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/377.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32550 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/384.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32560 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/389.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32570 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/392.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32580 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/398.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32590 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/400.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32600 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/402.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32610 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/405.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32620 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/435.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32630 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/446.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32640 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/460.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32650 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/461.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32660 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/467.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32670 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/482.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32680 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/484.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32690 |
| /workspace/datasets/visa/pipe_fryum/Data/Images/Normal/487.JPG | evaluation | no (errno 2) | unavailable | source_plan.json:32700 |
| /workspace/datasets/mvtec_ad/bottle/train | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad/bottle/test | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad/bottle/ground_truth | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/train | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/validation | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/can/test_public/ground_truth | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/train | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/validation | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fabric/test_public/ground_truth | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/train | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/validation | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/fruit_jelly/test_public/ground_truth | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/train | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/validation | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/rice/test_public/ground_truth | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/train | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/validation | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/sheet_metal/test_public/ground_truth | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/train | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/validation | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/vial/test_public/ground_truth | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/train | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/validation | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/wallplugs/test_public/ground_truth | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/train | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/validation | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |
| /workspace/datasets/mvtec_ad2_public/mvtec_ad_2/walnuts/test_public/ground_truth | dataset inventory directory | no (errno 2) | unavailable | verify_dataset.py:61–88 |

Status: written. No pipeline execution or reproduction claim is made.
