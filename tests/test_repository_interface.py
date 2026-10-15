"""Dataset roles, frozen selection and portable configuration contracts."""
from pathlib import Path
import csv
import json
import tempfile
import unittest

from PIL import Image
import torch

from dataset import IndustrialDataset, MVTecDataset, VisADataset
from train_study import resolved_config
from utils import PROJECT_ROOT, file_sha256, model_config, new_directory


def image(path, color=100):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (32, 32), (color, color, color)).save(path)


def mvtec_fixture(root):
    for name in ("train/good/000.png", "train/good/001.png", "test/good/002.png", "test/crack/003.png"):
        image(root / "bottle" / name)
    mask = root / "bottle/ground_truth/crack/003_mask.png"
    mask.parent.mkdir(parents=True)
    value = Image.new("L", (32, 32));value.putpixel((16, 16), 255);value.save(mask)
    return mask


class RepositoryInterfaceTests(unittest.TestCase):
    def test_support_selection_rejects_test_images_and_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);mvtec_fixture(root)
            data = MVTecDataset(root, "bottle", phase="train")
            self.assertEqual(data.support_ids(1, 17), data.support_ids(1, 17))
            self.assertEqual(len(data.support_ids(2, 17)), 2)
            for shots, explicit in [(1, ["bottle/test/good/002.png"]),
                                    (2, ["bottle/train/good/000.png"] * 2)]:
                with self.assertRaises(ValueError):data.support_ids(shots, 17, explicit)
            with self.assertRaises(ValueError):data.support_ids(3, 17)

    def test_dataset_geometry_and_native_label_survive_empty_crop(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);mask = mvtec_fixture(root)
            value = Image.new("L", (32, 32));value.putpixel((0, 0), 255);value.save(mask)
            data = MVTecDataset(root, "bottle")
            item = next(data[i] for i in range(len(data)) if data.samples[i].label == "anomaly")
            self.assertEqual(item["image"].shape, (3, 392, 392))
            self.assertEqual(item["mask"].shape, (256, 256))
            self.assertEqual(item["mask"].dtype, torch.bool)
            self.assertEqual(item["label"], 1)
            self.assertFalse(item["mask"].any())

    def test_smoke_queries_include_both_classes_without_changing_native_split(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);mvtec_fixture(root)
            data = MVTecDataset(root, "bottle")
            self.assertEqual({s.label for s in data.queries(2)}, {"normal", "anomaly"})
            self.assertTrue(all(s.split == "test" for s in data.queries()))
            with self.assertRaises(ValueError):data.queries(0)
            with self.assertRaises(ValueError):data.support_ids()

    def test_visa_uses_original_csv_roles_and_masks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = [dict(object="capsules", split="train", label="normal",
                         image="capsules/Data/Images/Normal/000.JPG", mask=""),
                    dict(object="capsules", split="test", label="normal",
                         image="capsules/Data/Images/Normal/001.JPG", mask=""),
                    dict(object="capsules", split="test", label="anomaly",
                         image="capsules/Data/Images/Anomaly/002.JPG",
                         mask="capsules/Data/Masks/Anomaly/002.png")]
            for row in rows:image(root / row["image"])
            path = root / rows[-1]["mask"];path.parent.mkdir(parents=True)
            Image.new("L", (32, 32), 255).save(path)
            (root / "split_csv").mkdir()
            for path in (root / "split_csv/1cls.csv", root / "capsules/image_anno.csv"):
                with path.open("w", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
            train = VisADataset(root, "capsules", "train")
            self.assertEqual(train.support_ids(), [rows[0]["image"]])
            test = VisADataset(root, "capsules")
            self.assertEqual(len(test), 2)
            self.assertTrue(test[0]["mask"].any())

    def test_configuration_paths_follow_config_location_and_preserve_preset(self):
        settings, lock = model_config(PROJECT_ROOT / "configs/hybrid.json")
        self.assertEqual(Path(settings["checkpoint"]).parent, PROJECT_ROOT / "checkpoints")
        self.assertEqual(lock["decision"]["params"],
                         {"clusters": 1, "variance": .95, "strength": .5, "gate": "uniform"})
        self.assertEqual(lock["loaded_selection_sha256"],
                         file_sha256(PROJECT_ROOT / "configs/protocol/selection.lock.json"))

    def test_tampered_or_leaky_selection_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);config = json.loads((PROJECT_ROOT / "configs/hybrid.json").read_text())
            lock = json.loads((PROJECT_ROOT / "configs/protocol/selection.lock.json").read_text())
            lock["verification_inference_seen"] = True
            (root / "selection.json").write_text(json.dumps(lock))
            config["selection"]["file"] = "selection.json"
            path = root / "config.json";path.write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError, "checksum"):model_config(path)
            config["selection"]["sha256"] = file_sha256(root / "selection.json")
            path.write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError, "exposure"):model_config(path)

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);(root / "keep.txt").write_text("existing result")
            with self.assertRaises(ValueError):new_directory(root)
            self.assertEqual((root / "keep.txt").read_text(), "existing result")

    def test_study_configuration_resolves_every_historical_input(self):
        config = resolved_config(PROJECT_ROOT / "configs/study.json", {})
        for name in ("development_manifest", "known_exposure", "previous_verification_lock"):
            self.assertTrue(Path(config[name]).is_file())
        self.assertIn("already known", config["claim_scope"])
        override = resolved_config(PROJECT_ROOT / "configs/study.json", {"mvtec_ad": "/tmp/custom-mvtec"})
        self.assertEqual(override["roots"]["mvtec_ad"], "/tmp/custom-mvtec")


if __name__ == "__main__":
    unittest.main()
