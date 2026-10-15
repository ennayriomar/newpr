"""Output metric semantics, macro averaging and visualization geometry."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
from PIL import Image

from outputs import (METRICS, export_evaluation, maximum_f1, metric_line,
                     normalized_display, render_case, save_tables)
from summarize import collect_results


class OutputStyleTests(unittest.TestCase):
    def test_benchmark_f1_uses_raw_ranking_without_changing_inputs(self):
        truth = np.array([0, 0, 1, 1])
        score = np.array([.1, .7, .5, .9])
        before = score.copy()
        self.assertAlmostEqual(maximum_f1(truth, score), .8)
        np.testing.assert_array_equal(score, before)
        self.assertIsNone(maximum_f1([0, 0], [.1, .2]))
        with self.assertRaises(ValueError):maximum_f1([0, 1], [0, np.nan])

    def test_display_normalization_is_copy_only_and_handles_constant_maps(self):
        raw = np.array([[2., 3.], [4., 5.]], dtype=np.float32)
        before = raw.copy()
        np.testing.assert_allclose(normalized_display(raw, 1, 5), [[.25, .5], [.75, 1]])
        np.testing.assert_array_equal(raw, before)
        self.assertFalse(normalized_display(np.ones((2, 2))).any())

    def test_reference_metric_line_uses_four_decimals_and_na(self):
        values = {key: .9 for key in METRICS};values["P-F1"] = None
        line = metric_line("bottle", values)
        self.assertTrue(line.startswith("bottle: I-Auroc:0.9000, I-AP:0.9000"))
        self.assertIn("P-F1:NA", line)

    def test_mean_gives_equal_weight_to_categories_after_draw_average(self):
        def record(category, seed, value):
            return dict(dataset="mvtec_ad", category=category, seed=seed, method="hybrid",
                        **{key: value for key in METRICS})
        records = [record("bottle", 17, .2), record("bottle", 29, .4), record("pill", 17, .9)]
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            rows = save_tables(records, Path(directory), "Known test data")
            mean = next(row for row in rows if row["category"] == "Mean")
            self.assertAlmostEqual(mean["I-Auroc"], .6)
            self.assertTrue((Path(directory) / "metrics.csv").is_file())
            self.assertNotIn(b"\r\n", (Path(directory) / "metrics.csv").read_bytes())
            self.assertIn("evaluation F1-max", (Path(directory) / "metrics.md").read_text())

    def test_five_panels_use_the_center_roi_and_preserve_raw_arrays(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = np.zeros((448, 448, 3), dtype=np.uint8)
            original[:] = [255, 0, 0];original[28:420, 28:420] = [0, 200, 0]
            Image.fromarray(original).save(root / "input.png")
            score = np.arange(256 * 256, dtype=np.float32).reshape(256, 256)
            before = score.copy();truth = np.zeros((256, 256), bool);truth[100:120, 100:120] = True
            files = render_case(root / "input.png", score, truth, root / "visuals", stem="sample",
                                global_bounds=(0, float(score.max())), title="Test ROI")
            self.assertEqual(set(files), {"ori", "gt", "global", "local", "gt_red", "compound"})
            with Image.open(files["ori"]) as image:
                self.assertEqual(image.size, (256, 256))
                np.testing.assert_array_equal(np.array(image)[128, 128], [0, 200, 0])
            with Image.open(files["gt_red"]) as image:
                np.testing.assert_array_equal(np.array(image)[110, 110], [255, 0, 0])
            np.testing.assert_array_equal(score, before)
            with self.assertRaises(ValueError):
                render_case(root / "input.png", score, truth, root / "visuals", stem="../escape",
                            global_bounds=(0, 1))

    def test_collection_rejects_duplicate_cohorts_and_unmarked_subset_aggregation(self):
        result = dict(dataset="mvtec_ad", category="bottle", seed=17, shots=1,
                      model_json_sha256="model", cohort_sha256="cohort", subset=True,
                      records=[dict(dataset="mvtec_ad", category="bottle", method="hybrid")])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.json";path.write_text(json.dumps(result))
            with self.assertRaisesRegex(ValueError, "Subset"):collect_results([path])
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                collect_results([path, path], include_subsets=True)

    def test_table_only_export_needs_no_dataset_images_or_saved_maps(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            root = Path(directory);run = root / "run";evaluation = root / "evaluation";output = root / "output"
            for folder in (run, evaluation, output):folder.mkdir()
            (run / "training.json").write_text(json.dumps({"data_path": str(root / "missing-dataset")}))
            (run / "model.json").write_text(json.dumps({"provenance": {"encoder": {"resize": 448, "crop": 392}}}))
            detection = dict(auroc=1., ap=1., f1=1., accuracy=1., false_alarm_rate=0., threshold=.5)
            summary = dict(dataset="mvtec_ad", category="bottle", shots=1, seed=17,
                           subset=True, queries=2, metric_region="ROI", model_json_sha256="model",
                           methods={method: {"detection": detection} for method in ("baseline", "hybrid")})
            path = evaluation / "metrics.json";path.write_text(json.dumps(summary));before = path.read_bytes()
            rows = [dict(sample_id=f"image-{label}", method=method, label=label, score=float(label))
                    for label in (0, 1) for method in ("baseline", "hybrid")]
            (evaluation / "predictions.jsonl").write_text("\n".join(json.dumps(row) for row in rows))
            result = export_evaluation(evaluation, run, destination=output, visualize=False)
            self.assertEqual(path.read_bytes(), before)
            self.assertIsNone(result["records"][0]["P-F1"])
            self.assertFalse(result["operational_thresholds_changed"])
            self.assertEqual(result["visualizations"], [])


if __name__ == "__main__":
    unittest.main()
