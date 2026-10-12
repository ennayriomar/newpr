"""Real float16 TIFF exporter following MVTec's provided source utilities."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
from PIL import Image
import tifffile


OFFICIAL_DIR = Path('/workspace/datasets/official_ad2_tools/MVTecAD2_public_code_utils')


def official_checker():
    spec = importlib.util.spec_from_file_location('safe_iad_official_ad2_utils', OFFICIAL_DIR / 'utils.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def relative_output(image_id, thresholded=False):
    relative = Path(image_id)
    if relative.is_absolute() or '..' in relative.parts or len(relative.parts) < 3:
        raise ValueError('Expected contained category/split/image path.')
    category, split = relative.parts[:2]
    official = official_checker()
    if category not in official.MVTEC_AD_2_OBJECTS or split not in {'test_public', 'validation', *official.TEST_SET_DIRECTORIES}:
        raise ValueError('Not an official MVTec AD 2 export split/category.')
    if relative.suffix.lower() != '.png':
        raise ValueError('MVTec AD 2 inputs must be PNG images.')
    base = 'anomaly_images_thresholded' if thresholded else 'anomaly_images'
    return Path(base) / relative.with_suffix('.png' if thresholded else '.tiff')


def export_map(output, image_id, array, threshold=None):
    array = np.asarray(array)
    if array.ndim != 2 or not np.isfinite(array).all() or (np.abs(array) > np.finfo(np.float16).max).any():
        raise ValueError('Export requires a finite native-resolution 2D map representable in float16.')
    output = Path(output)
    target = output / relative_output(image_id)
    target.parent.mkdir(parents=True, exist_ok=True)
    values = array.astype(np.float16)
    if target.exists():
        if not np.array_equal(tifffile.imread(target), values):
            raise ValueError('Immutable exported evidence differs; use a new output directory.')
    else:
        temp = target.with_suffix('.tmp.tiff')
        tifffile.imwrite(temp, values, photometric='minisblack', metadata=None)
        temp.replace(target)
    checker = official_checker()
    checker._check_ad_images(target)
    record = dict(image_id=image_id, path=str(target), shape=list(array.shape), dtype='float16',
                  scope='server_private' if 'private' in Path(image_id).parts[1] else 'local_public_or_validation_only',
                  sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    if threshold is not None:
        if not np.isfinite(threshold):
            raise ValueError('Threshold must be finite and fitted without final-query labels.')
        binary = (array >= threshold).astype('uint8') * 255
        target_binary = output / relative_output(image_id, True)
        target_binary.parent.mkdir(parents=True, exist_ok=True)
        if target_binary.exists():
            if not np.array_equal(np.asarray(Image.open(target_binary)), binary):
                raise ValueError('Immutable thresholded export differs.')
        else:
            Image.fromarray(binary).save(target_binary)
        checker._check_thresholded_ad_images(target_binary)
        record.update(thresholded_path=str(target_binary), pixel_threshold=float(threshold))
    return record


def validate_complete_submission(output):
    """Call the official directory and file checks; public previews cannot pass."""
    output = Path(output)
    checker = official_checker()
    paths = checker.check_anomaly_image_dir(output/'anomaly_images', '.tiff')
    checker.check_images(paths, False)
    required = {'anomaly_images'}
    if (output/'anomaly_images_thresholded').exists():
        checker.check_images(checker.check_anomaly_image_dir(output/'anomaly_images_thresholded', '.png'), True)
        required.add('anomaly_images_thresholded')
    checker.compare_found_vs_required(required, set(), output)
    return dict(status='official_format_check_passed', private_server_scores='not_requested_or_simulated', maps=len(paths))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--submission', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate_complete_submission(args.submission)))


if __name__ == '__main__':
    main()
