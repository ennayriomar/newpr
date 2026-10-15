"""Verify actual image/mask files and native splits without model training.

No synthetic fixtures, inferred calibration split, or private-test labels are used.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, ImageDraw


EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'}


@dataclass(frozen=True)
class Sample:
    category: str
    split: str
    label: str
    image: str
    mask: str | None


def contained_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f'Path escapes dataset root: {relative}')
    return path


def discover(root: Path, dataset: str, split_csv: Path | None):
    samples, issues = [], []
    if dataset == 'visa':
        split_csv = split_csv or root / 'split_csv/1cls.csv'
        with split_csv.open(newline='') as f:
            reader = csv.DictReader(f)
            if not {'object', 'split', 'label', 'image', 'mask'}.issubset(reader.fieldnames or []):
                raise ValueError(f'Unexpected VisA split schema: {reader.fieldnames}')
            for row in reader:
                if row['label'] not in {'normal', 'anomaly'} or row['split'] not in {'train', 'test'}:
                    raise ValueError(f'Unexpected official VisA label/split: {row}')
                samples.append(Sample(row['object'], row['split'], row['label'], row['image'], row['mask'] or None))
        categories = sorted({s.category for s in samples})
        for cat in categories:
            with (root / cat / 'image_anno.csv').open(newline='') as f:
                annotated = {row['image'] for row in csv.DictReader(f)}
            listed = {s.image for s in samples if s.category == cat}
            if annotated != listed:
                issues.append({'kind': 'annotation_split_mismatch', 'category': cat, 'missing_from_split': sorted(annotated - listed), 'missing_from_annotations': sorted(listed - annotated)})
        actual = {str(p.relative_to(root)) for cat in categories for p in (root / cat / 'Data/Images').rglob('*') if p.suffix.lower() in EXTENSIONS}
        mask_paths = {str(p.relative_to(root)) for cat in categories for p in (root / cat / 'Data/Masks').rglob('*') if p.suffix.lower() in EXTENSIONS}
    else:
        categories = sorted(p.name for p in root.iterdir() if p.is_dir() and (p / 'train').is_dir())
        if not categories:
            raise ValueError(f'No category/train directories in {root}')
        splits = ['train', 'test'] if dataset == 'mvtec_ad' else ['train', 'validation', 'test_public']
        actual, mask_paths = set(), set()
        for cat in categories:
            category_root = root / cat
            for split in splits:
                directory = category_root / split
                if not directory.is_dir():
                    issues.append({'kind': 'missing_split', 'category': cat, 'split': split})
                    continue
                for p in sorted(directory.rglob('*')):
                    if p.suffix.lower() not in EXTENSIONS or 'ground_truth' in p.relative_to(directory).parts:
                        continue
                    label = 'normal' if p.parent.name == 'good' else 'anomaly'
                    if label == 'anomaly':
                        if dataset == 'mvtec_ad':
                            mask = category_root / 'ground_truth' / p.parent.name / (p.stem + '_mask.png')
                        else:
                            mask = directory / 'ground_truth' / p.parent.name / (p.stem + '_mask.png')
                    else:
                        mask = None
                    relative = str(p.relative_to(root))
                    actual.add(relative)
                    samples.append(Sample(cat, split, label, relative, str(mask.relative_to(root)) if mask else None))
            mask_dir = category_root / 'ground_truth' if dataset == 'mvtec_ad' else category_root / 'test_public/ground_truth'
            mask_paths.update(str(p.relative_to(root)) for p in mask_dir.rglob('*') if p.suffix.lower() in EXTENSIONS)
    listed = {s.image for s in samples}
    if actual != listed:
        issues.append({'kind': 'unlisted_or_missing_images', 'unlisted': sorted(actual - listed), 'missing': sorted(listed - actual)})
    referenced_masks = {s.mask for s in samples if s.mask}
    if mask_paths != referenced_masks:
        issues.append({'kind': 'mask_inventory_mismatch', 'orphan_masks': sorted(mask_paths - referenced_masks), 'missing_masks': sorted(referenced_masks - mask_paths)})
    return samples, categories, issues, split_csv


def inspect_sample(root, dataset, sample):
    result = asdict(sample)
    result['image_id'] = f'{dataset}:{sample.image}'
    result['errors'] = []
    try:
        image = contained_path(root, sample.image)
        with image.open('rb') as f:
            result['image_sha256'] = hashlib.file_digest(f, 'sha256').hexdigest()
        with Image.open(image) as im:
            im.load()
            result.update(width=im.width, height=im.height, image_mode=im.mode)
        if sample.mask:
            with Image.open(contained_path(root, sample.mask)) as mask:
                mask.load()
                result['mask_size'] = list(mask.size)
                values = np.asarray(mask)
                if mask.size != (result['width'], result['height']):
                    result['errors'].append('image_mask_size_mismatch')
                if values.ndim != 2 or not np.issubdtype(values.dtype, np.integer):
                    result['errors'].append('mask_not_integer_grayscale')
                unique = np.unique(values)
                result['mask_values'] = unique.tolist()
                result['anomaly_pixels'] = int(np.count_nonzero(values))
                if dataset != 'visa' and not set(unique.tolist()).issubset({0, 255}):
                    result['errors'].append('nonbinary_mvtec_mask')
                if not result['anomaly_pixels']:
                    result['errors'].append('anomalous_image_has_empty_mask')
        elif sample.label == 'anomaly':
            result['errors'].append('anomalous_image_has_no_mask')
        else:
            result.update(mask_values=[0], anomaly_pixels=0, mask_representation='implicit_zero_for_normal')
        if sample.split in {'train', 'validation'} and sample.label != 'normal':
            result['errors'].append('anomaly_in_normal_training_or_validation_split')
    except Exception as exc:
        result['errors'].append(f'{type(exc).__name__}: {exc}')
    return result


def visual_samples(root, samples, output):
    output.mkdir(exist_ok=True)
    for category in sorted({s.category for s in samples}):
        chosen = []
        for label in ['normal', 'anomaly']:
            candidates = [s for s in samples if s.category == category and s.label == label and s.split in {'test', 'test_public'}]
            if candidates:
                chosen.append(sorted(candidates, key=lambda s: s.image)[0])
        canvas = Image.new('RGB', (512, 288 * len(chosen)), 'white')
        draw = ImageDraw.Draw(canvas)
        for i, sample in enumerate(chosen):
            with Image.open(contained_path(root, sample.image)) as im:
                image = ImageOps.contain(im.convert('RGB'), (256, 256))
            overlay = image.copy()
            if sample.mask:
                with Image.open(contained_path(root, sample.mask)) as im:
                    mask = im.resize(image.size, Image.Resampling.NEAREST)
                    binary = Image.fromarray((np.asarray(mask) > 0).astype(np.uint8) * 120)
                red = Image.new('RGB', image.size, (255, 0, 0))
                overlay = Image.composite(red, image, binary)
            canvas.paste(image, (0, i * 288 + 24))
            canvas.paste(overlay, (256, i * 288 + 24))
            draw.text((5, i * 288 + 4), f'{category} / {sample.split} / {sample.label}', fill='black')
        if chosen:
            canvas.save(output / f'{category}.png')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', required=True, choices=['mvtec_ad', 'mvtec_ad2', 'visa'])
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--split-csv', type=Path)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    if '.unverified' in root.parts or any(p.endswith('.unverified') for p in root.parts):
        raise ValueError('Refusing to evaluate data staged before checksum verification.')
    samples, categories, issues, split_csv = discover(root, args.dataset, args.split_csv)
    if not samples:
        raise ValueError('Zero images discovered; verification cannot pass.')
    output = args.output / args.dataset
    output.mkdir(parents=True, exist_ok=True)
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        for i, result in enumerate(executor.map(lambda s: inspect_sample(root, args.dataset, s), samples), 1):
            results.append(result)
            if i % 1000 == 0 or i == len(samples):
                print(json.dumps({'dataset': args.dataset, 'checked': i, 'total': len(samples)}), flush=True)
    ids = [r['image_id'] for r in results]
    if len(ids) != len(set(ids)):
        issues.append({'kind': 'duplicate_image_ids'})
    hashes = defaultdict(list)
    for result in results:
        if result.get('image_sha256'):
            hashes[result['image_sha256']].append(result)
        if result['errors']:
            issues.append({'kind': 'image_or_mask_validation', 'image': result['image'], 'errors': result['errors']})
    cross_split = []
    for matches in hashes.values():
        if len({r['split'] for r in matches}) > 1:
            cross_split.append([{'image': r['image'], 'split': r['split']} for r in matches])
    if cross_split:
        issues.append({'kind': 'identical_image_content_across_native_splits', 'groups': cross_split})
    counts = Counter((r['category'], r['split'], r['label']) for r in results)
    report = {
        'dataset': args.dataset, 'root': str(root), 'status': 'passed' if not issues else 'failed',
        'real_data': True, 'pretrained_weights_used': False,
        'categories': categories, 'total_images': len(results),
        'counts': [{'category': cat, 'split': split, 'label': label, 'count': count} for (cat, split, label), count in sorted(counts.items())],
        'split_csv': str(split_csv) if split_csv else None,
        'native_splits_checked': sorted({r['split'] for r in results}),
        'experimental_manifest_status': 'not_created; no experimental support/validation/calibration assignment is claimed',
        'mask_semantics': 'VisA native integer class IDs are binarized as >0 for visuals only; MVTec masks must use 0/255.',
        'private_test_evaluation': 'not_performed', 'issues': issues,
        'versions': {'numpy': np.__version__, 'pillow': Image.__version__},
    }
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    with (output / 'images.jsonl').open('w') as f:
        for result in results:
            f.write(json.dumps(result) + '\n')
    valid = {r['image'] for r in results if not r['errors']}
    visual_samples(root, [s for s in samples if s.image in valid], output / 'visuals')
    print(json.dumps({k: report[k] for k in ['dataset', 'status', 'total_images', 'native_splits_checked']}), flush=True)
    raise SystemExit(0 if not issues else 1)


if __name__ == '__main__':
    main()
