"""Cheap encoder contract checks; these are not pretrained-model evidence."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image
import torch

from safe_iad.safal_features import (
    SAFALEncoder, SOURCE_PIN, SOURCE_MANIFEST_NAME, SOURCE_FILES_SHA256,
    _canonical, _manifest_digest, _read_cache, _sha256,
    feature_cache_key, preprocess_rgb, validate_configuration, verify_source,
)


class SAFALFeatureContracts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.metadata = dict(source_commit=SOURCE_PIN, checkpoint_sha256='synthetic-test-only',
                             layers=[2, 5, 8, 11], resolution=28)

    def tearDown(self):
        self.temporary.cleanup()

    def cache(self, **changes):
        payload = dict(tokens=np.zeros((4, 768), dtype=np.float32),
                       metadata=np.array(_canonical(self.metadata)), grid=np.array([2, 2]),
                       original_size=np.array([9, 5]), resized_size=np.array([28, 28]),
                       padded_size=np.array([28, 28]))
        payload.update(changes)
        target = self.root / 'features.npz'
        np.savez(target, **payload)
        return target

    def test_square_rgb_preprocessing_and_imagenet_values(self):
        image = Image.new('L', (9, 5), color=0)
        tensor = preprocess_rgb(image, 28)
        self.assertEqual(tuple(tensor.shape), (1, 3, 28, 28))
        self.assertEqual(tensor.dtype, torch.float32)
        np.testing.assert_allclose(tensor[0, :, 0, 0].numpy(),
                                   -np.array([.485, .456, .406]) / np.array([.229, .224, .225]), rtol=1e-6)

    def test_invalid_geometry_and_layer_configuration_rejected(self):
        for resolution, layers, threads in [(225, (2, 5), 3), (0, (2, 5), 3),
                                            (28, (5, 2), 3), (28, (2, 2), 3),
                                            (28, (12,), 3), (28, (), 3),
                                            (28, (True,), 3), (28, (11,), 0)]:
            with self.subTest(resolution=resolution, layers=layers, threads=threads):
                with self.assertRaises(ValueError):
                    validate_configuration(resolution, layers, threads)

    def test_valid_cache_restores_declared_native_geometry(self):
        bundle = _read_cache(self.cache(), self.metadata, 28, (9, 5))
        self.assertEqual(bundle.original_size, (9, 5))
        self.assertEqual(bundle.grid, (2, 2))
        self.assertEqual(tuple(bundle.tokens.shape), (4, 768))
        self.assertEqual(bundle.mode, 'subspacead')
        self.assertTrue(bundle.cache_hit)

    def test_cache_rejects_changed_checkpoint_or_layers(self):
        target = self.cache()
        for field, value in [('checkpoint_sha256', 'another-checkpoint'), ('layers', [11])]:
            modified = dict(self.metadata, **{field: value})
            with self.assertRaisesRegex(ValueError, 'provenance'):
                _read_cache(target, modified, 28, (9, 5))
            self.assertNotEqual(feature_cache_key(modified), feature_cache_key(self.metadata))

    def test_cache_rejects_native_size_and_grid_mismatch(self):
        for change in [dict(original_size=np.array([5, 9])), dict(grid=np.array([1, 4])),
                       dict(padded_size=np.array([28, 42])), dict(grid=np.array([2., 2.]))]:
            with self.subTest(change=change):
                with self.assertRaisesRegex(ValueError, 'geometry'):
                    _read_cache(self.cache(**change), self.metadata, 28, (9, 5))

    def test_cache_rejects_nonfinite_float64_and_wrong_shape(self):
        arrays = [np.full((4, 768), np.nan, dtype=np.float32),
                  np.zeros((4, 768), dtype=np.float64), np.zeros((3, 768), dtype=np.float32)]
        for values in arrays:
            with self.assertRaisesRegex(ValueError, 'float32'):
                _read_cache(self.cache(tokens=values), self.metadata, 28, (9, 5))

    def test_cache_never_loads_pickled_object_arrays(self):
        with self.assertRaises(ValueError):
            _read_cache(self.cache(tokens=np.array([{'unsafe': 'object'}], dtype=object)),
                        self.metadata, 28, (9, 5))

    def test_cache_rejects_extra_payload_members(self):
        with self.assertRaisesRegex(ValueError, 'schema'):
            _read_cache(self.cache(extra=np.zeros(1)), self.metadata, 28, (9, 5))

    def test_bundle_without_trusted_manifest_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'manifest'):
            verify_source(self.root)
        (self.root / SOURCE_MANIFEST_NAME).write_text(json.dumps(dict(source_commit=SOURCE_PIN,
                    files={}, file_manifest_sha256=SOURCE_FILES_SHA256)))
        with self.assertRaisesRegex(ValueError, 'differs'):
            verify_source(self.root)

    def synthetic_source(self):
        (self.root / 'hubconf.py').write_text('# synthetic source verification test\n')
        (self.root / 'LICENSE').write_text('synthetic test only\n')
        files = {name: _sha256(self.root / name) for name in ['hubconf.py', 'LICENSE']}
        digest = _manifest_digest(files)
        (self.root / SOURCE_MANIFEST_NAME).write_text(json.dumps(dict(source_commit=SOURCE_PIN,
                    files=files, file_manifest_sha256=digest)))
        return digest

    def test_manifest_rejects_source_tampering_and_injected_python(self):
        digest = self.synthetic_source()
        with patch('safe_iad.safal_features.SOURCE_FILES_SHA256', digest):
            self.assertEqual(verify_source(self.root)['source_commit'], SOURCE_PIN)
            (self.root / 'injected.py').write_text('# added code\n')
            with self.assertRaisesRegex(ValueError, 'Unexpected'):
                verify_source(self.root)
            (self.root / 'injected.py').unlink()
            (self.root / 'hubconf.py').write_text('# changed code\n')
            with self.assertRaisesRegex(ValueError, 'SHA256'):
                verify_source(self.root)

    def test_bad_checkpoint_is_rejected_before_constructing_a_model(self):
        checkpoint = self.root / 'incorrect.pth'
        checkpoint.write_bytes(b'not the real pretrained weights')
        with patch('safe_iad.safal_features.verify_source', return_value={}), \
             patch('torch.hub.load') as load:
            with self.assertRaisesRegex(ValueError, 'checkpoint failed'):
                SAFALEncoder(self.root, checkpoint, self.root / 'cache')
            load.assert_not_called()


if __name__ == '__main__':
    unittest.main()
