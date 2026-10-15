# Native dataset layout

Download [MVTec AD](https://www.mvtec.com/research-teaching/datasets/mvtec-ad)
and [VisA](https://github.com/amazon-science/spot-diff) from their original
sources, retaining the applicable dataset licenses.

```text
data/
├── mvtec_ad/
│   └── bottle/
│       ├── train/good/*.png
│       ├── test/good/*.png
│       ├── test/broken_large/*.png
│       └── ground_truth/broken_large/*_mask.png
└── visa/
    ├── split_csv/1cls.csv
    └── capsules/
        ├── image_anno.csv
        └── Data/
            ├── Images/Normal/
            ├── Images/Anomaly/
            └── Masks/Anomaly/
```

The native VisA CSV split is consumed directly; no copy into a renamed MVTec
layout is needed. Keep paths in split_csv/1cls.csv and image_anno.csv unchanged.
Dataset paths can be located elsewhere and passed with `--data_path`.

Target training uses only original normal images in the native training split.
Test images cannot be supplied as explicit normal support IDs. Binary masks
are resized with nearest interpolation in the center-cropped ROI, matching
this project's declared evaluation geometry. Image labels remain native.
This entry-point layout supports MVTec AD and VisA; historical AD2 tooling
remains separately documented in framework.
