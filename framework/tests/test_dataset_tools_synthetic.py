"""Synthetic failure tests for data tools, not model or benchmark evidence."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

import numpy as np
from PIL import Image

from safe_iad.verify_dataset import Sample, contained_path, inspect_sample


class SyntheticDatasetToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()

    def tearDown(self):
        self.temp.cleanup()

    def image(self, name, values=None):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(values if values is not None else np.zeros((8, 8, 3), dtype=np.uint8)).save(path)
        return path

    def test_synthetic_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            contained_path(self.root, '../outside.png')

    def test_synthetic_missing_mask_reported(self):
        self.image('image.png')
        result = inspect_sample(self.root, 'mvtec_ad', Sample('cat', 'test', 'anomaly', 'image.png', 'missing.png'))
        self.assertTrue(any('FileNotFoundError' in error for error in result['errors']))

    def test_synthetic_misaligned_mask_reported(self):
        self.image('image.png')
        self.image('mask.png', np.full((4, 4), 255, dtype=np.uint8))
        result = inspect_sample(self.root, 'mvtec_ad', Sample('cat', 'test', 'anomaly', 'image.png', 'mask.png'))
        self.assertIn('image_mask_size_mismatch', result['errors'])

    def test_synthetic_visa_multiclass_mask_allowed(self):
        self.image('image.png')
        values = np.zeros((8, 8), dtype=np.uint8)
        values[1, 1], values[2, 2] = 1, 2
        self.image('mask.png', values)
        result = inspect_sample(self.root, 'visa', Sample('cat', 'test', 'anomaly', 'image.png', 'mask.png'))
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['anomaly_pixels'], 2)

    def test_synthetic_leakage_causes_nonzero_cli_exit(self):
        self.image('cat/train/good/000.png')
        self.image('cat/test/good/000.png')
        command = [sys.executable, '-m', 'safe_iad.verify_dataset', '--dataset', 'mvtec_ad', '--root', str(self.root), '--output', str(self.root / 'report')]
        process = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(process.returncode, 1, process.stderr)
        report = json.loads((self.root / 'report/mvtec_ad/verification.json').read_text())
        self.assertEqual(report['total_images'], 2)
        self.assertTrue(any(issue['kind'] == 'identical_image_content_across_native_splits' for issue in report['issues']))

    def archive(self, name):
        path = self.root / 'fixture.tar'
        with tarfile.open(path, 'w') as archive:
            info = tarfile.TarInfo(name)
            info.size = 7
            archive.addfile(info, io.BytesIO(b'fixture'))
        return path

    def acquire(self, archive, checksum):
        return subprocess.run([sys.executable, '/workspace/tools/acquire_public_data.py', '--archive', str(archive), '--sha256', checksum, '--root', str(self.root / 'data'), '--report', str(self.root / 'acquisition.json'), '--reserve-gib', '0'], capture_output=True, text=True)

    def test_synthetic_bad_checksum_never_publishes_data(self):
        archive = self.archive('image.bin')
        process = self.acquire(archive, '0' * 64)
        self.assertNotEqual(process.returncode, 0)
        self.assertFalse((self.root / 'data').exists())
        report = json.loads((self.root / 'acquisition.json').read_text())
        self.assertEqual(report['status'], 'failed_unverified')
        self.assertIn('SHA-256', report['error'])

    def test_synthetic_unsafe_archive_never_escapes_staging(self):
        archive = self.archive('../outside.bin')
        checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
        process = self.acquire(archive, checksum)
        self.assertNotEqual(process.returncode, 0)
        self.assertFalse((self.root / 'outside.bin').exists())
        self.assertFalse((self.root / 'data').exists())

    def test_synthetic_existing_data_is_preserved(self):
        archive = self.archive('image.bin')
        checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
        data = self.root / 'data'
        data.mkdir()
        (data / 'user.txt').write_text('preserve me')
        process = self.acquire(archive, checksum)
        self.assertNotEqual(process.returncode, 0)
        self.assertEqual((data / 'user.txt').read_text(), 'preserve me')


if __name__ == '__main__':
    unittest.main()
