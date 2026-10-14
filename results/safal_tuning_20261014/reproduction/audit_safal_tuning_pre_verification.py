"""Audit frozen SAFAL tuning artifacts without writing scientific artifacts."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
from sklearn.metrics import roc_auc_score
import torch
import torch.nn.functional as F

sys.path.insert(0, '/workspace/tools')
from safe_iad.experiment_io import sha256, read_jsonl, write_json, implementation_hashes
from safe_iad.safal_features import CHECKPOINT_SHA256, SOURCE_PIN, SOURCE_FILES_SHA256
from safe_iad.safal_tunable import Parameters, TunableSubspaceSearch, _array_hash
from safe_iad.safal_tune import (CODE, parameter_grid, eligible, candidate_metrics,
                                selection_key, select_candidate, verify_lock)
from safe_iad.safal_cli import inventory
from safe_iad.research_metrics import (localization_metrics, thresholded_detection_metrics,
                                      paired_crossed_bootstrap)


def require(value, message):
    if not value:
        raise ValueError(message)


def document(path):
    return json.loads(Path(path).read_text())


def close(actual, expected, message, tolerance=1e-10):
    require(np.isfinite(actual) and np.isfinite(expected)
            and abs(float(actual)-float(expected)) <= tolerance*max(1., abs(float(expected))), message)


def compare(actual, expected, context='JSON'):
    if isinstance(expected, dict):
        require(isinstance(actual, dict) and set(actual) == set(expected), context+' keys differ.')
        for key in expected:
            compare(actual[key], expected[key], context+'.'+key)
    elif isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected), context+' list differs.')
        for index, (a, b) in enumerate(zip(actual, expected)):
            compare(a, b, context+f'[{index}]')
    elif isinstance(expected, float):
        close(actual, expected, context+' numeric value differs.')
    else:
        require(actual == expected, context+' value differs.')


def check_query_isolation(exposure, query_lock, dev_manifest):
    dev = [e for e in dev_manifest['episodes'] if e['shots'] == 4]
    checks = query_lock['episodes']
    require(len(dev) == len(checks) == 15, 'Expected 15 matched k4 bank configurations.')
    dev_ids, new_ids, reserved = set(), set(), defaultdict(set)
    bank_ids = set()
    query_sets = defaultdict(set)
    for a, b in zip(dev, checks):
        for key in ['id', 'dataset', 'category', 'seed', 'shots', 'support_ids', 'calibration_ids']:
            require(a[key] == b[key], 'Development/verification bank differs: '+key)
        require(a['id'] not in bank_ids, 'Duplicate bank ID.')
        bank_ids.add(a['id'])
        for e in (a, b):
            groups = [e[k] for k in ['support_ids', 'calibration_ids', 'query_ids']]
            require(len(groups[0]) == len(groups[1]) == 4 and len(groups[2]) == 20,
                    'Original information budget must be k4+calibration4 with20 queries.')
            require(e['shots'] == 4 and e['k_plus_calibration'] == 8
                    and e['strict_k_image_few_shot'] is False, 'Incorrect information-budget declaration.')
            require(all(len(g) == len(set(g)) for g in groups), 'Duplicate episode image ID.')
            require(all(not set(groups[x]) & set(groups[y]) for x in range(3) for y in range(x+1, 3)),
                    'Support/calibration/query overlap.')
        reserved[a['dataset'], a['category']].update(a['calibration_ids'])
        dev_ids.update(a['dataset']+':'+i for i in a['query_ids'])
        new_ids.update(b['dataset']+':'+i for i in b['query_ids'])
        query_sets[b['dataset'], b['category']].add(tuple(b['query_ids']))
    require(len(dev_ids) == len(new_ids) == 100, 'Expected100 unique images in each partition.')
    require(not dev_ids & new_ids and not set(exposure['native_query_ids']) & new_ids,
            'Verification overlaps development or a known native query exposure.')
    require(len(query_sets) == 5 and all(len(v) == 1 for v in query_sets.values()),
            'Query pairing changed between support draws.')
    for e in checks:
        require(not set(e['support_ids']) & reserved[e['dataset'], e['category']],
                'Globally reserved calibration image entered a support draw.')
    return dict(development_unique_queries=100, verification_unique_queries=100,
                paired_configurations=15, known_exposure_overlap=0, development_overlap=0)


def check_model_document(lock, saved, episode):
    params = Parameters(**lock['params'])
    require(lock['parameters_id'] == params.id and lock['winner']['id'] == params.id
            and lock['winner']['params'] == asdict(params), 'Selection lock parameters/ID/winner mismatch.')
    require(lock['winner']['feature_id'] == lock['feature']['id'], 'Selected feature identity mismatch.')
    require(saved['params'] == asdict(params) and saved['parameters_id'] == params.id,
            'Frozen model parameters do not match selection lock.')
    support, normal = episode['support_ids'], episode['calibration_ids']
    require(len(support) == len(normal) == 4 and len(set(support)) == len(set(normal)) == 4
            and not set(support) & set(normal), 'Frozen model needs disjoint4+4 original normals.')
    require(saved['support_ids'] == support and saved['calibration']['calibration_ids'] == normal,
            'Saved support/normal cutoff IDs mismatch.')
    require(all(np.isfinite(saved['calibration'][key]) and saved['calibration'][key] > 0
                for key in ['image_search', 'pixel_search', 'image_subspace', 'pixel_subspace']),
            'Branch cutoffs must be finite and positive.')
    meta = saved['calibration_metadata']
    require(meta['parameters_id'] == params.id and meta['normal_quantile'] == params.normal_quantile
            and meta['aggregation'] == params.aggregation
            and meta['explained_variance'] == params.explained_variance
            and meta['calibration_ids'] == normal and meta['extra_normal_calibration_images'] == 4
            and meta['support_overlap'] == 0 and meta['query_labels_accepted'] is False
            and meta['probability_calibration'] is False, 'Saved calibration/parameter scope mismatch.')
    provenance = saved['provenance']
    require(provenance['feature_id'] == lock['feature']['id'] and provenance['episode'] == episode,
            'Frozen feature or bank provenance mismatch.')
    require(provenance['k_plus_calibration'] == 8 and provenance['strict_k_image_few_shot'] is False
            and provenance['error_head'] is None and provenance['probabilities'] is False,
            'Frozen checkpoint information budget/probability scope differs.')
    encoder = provenance['encoder']
    require(encoder['resolution'] == lock['feature']['resolution']
            and encoder['layers'] == lock['feature']['layers'], 'Frozen encoder semantic feature mismatch.')
    require(encoder['backbone'] == 'dinov2_vitb14' and encoder['checkpoint_sha256'] == CHECKPOINT_SHA256
            and encoder['source_commit'] == SOURCE_PIN and encoder['source_manifest_sha256'] == SOURCE_FILES_SHA256,
            'Frozen model lacks actual pinned DINO source/checkpoint provenance.')
    require(encoder['pretrained_weights_loaded'] is True and encoder['frozen'] is True
            and encoder['evaluation_mode'] is True and encoder['dtype'] == 'float32'
            and encoder['device'] == 'cpu', 'Frozen/eval/pretrained encoder contract differs.')


def raw_adapter(episode, variances):
    """Use saved raw fields only; this object never fits/encodes a query."""
    model = TunableSubspaceSearch.__new__(TunableSubspaceSearch)
    model.support_ids = tuple(episode['support_ids'])
    model.retained_ranks = {str(float(v)): 0 for v in variances}
    model._calibration_records = {}
    return model


def load_raw_banks(run, episodes, feature, variances):
    banks, cases = [], []
    for episode in episodes:
        rows = document(run/'development'/feature['id']/episode['id']/'raw_manifest.json')
        ids = episode['calibration_ids']+episode['query_ids']
        require(len(rows) == 24 and [r['image_id'] for r in rows] == ids, 'Raw development case ordering differs.')
        raws = []
        for index, record in enumerate(rows):
            path = Path(record['path'])
            require(path == run/'development'/feature['id']/episode['id']/f'raw-{index:03d}.npz'
                    and sha256(path) == record['sha256'], 'Raw development provenance/checksum differs.')
            require(record['role'] == ('normal_calibration' if index < 4 else 'development_query'),
                    'Raw calibration/query role differs.')
            with np.load(path, allow_pickle=False) as archive:
                keys = {'search'} | {'subspace_'+str(float(v)) for v in variances}
                require(set(archive.files) == keys, 'Raw variance-grid schema differs.')
                arrays = {k: archive[k].copy() for k in archive.files}
            tokens = (feature['resolution']//14)**2
            require(all(a.dtype == np.float64 and a.shape == (tokens,) and np.isfinite(a).all()
                        and (a >= 0).all() for a in arrays.values()), 'Invalid full-precision raw development fields.')
            require(record['grid'] == [feature['resolution']//14]*2 and record['raw_dtype'] == 'float64',
                    'Saved raw feature geometry/dtype differs.')
            raws.append(dict(search=torch.from_numpy(arrays['search']),
                             subspace={str(float(v)): torch.from_numpy(arrays['subspace_'+str(float(v))]) for v in variances}))
        banks.append(dict(episode=episode, model=raw_adapter(episode, variances), normals=raws[:4], queries=raws[4:]))
    return banks


def score_saved_raw(banks, params):
    scores = []
    for bank in banks:
        model = bank['model']
        calibration = model.calibration_from_raw(bank['normals'], bank['episode']['calibration_ids'], params)
        scores.extend(model.predict_from_raw(raw, params, calibration)['image_score'] for raw in bank['queries'])
    return np.asarray(scores, dtype=np.float64)


def audit_development(run, config_path):
    lock = verify_lock(config_path, run)
    pre = document(run/'preflight.json');config = document(config_path)
    torch.set_num_threads(config['encoder']['threads']);torch.use_deterministic_algorithms(True)
    dev_manifest = document(config['development_manifest'])
    query_lock = document(config['verification_query_lock']);exposure = document(config['known_exposure'])
    split_counts = check_query_isolation(exposure, query_lock, dev_manifest)
    require(sha256(config['verification_query_lock']) == config['verification_query_lock_sha256']
            and sha256(config['known_exposure']) == query_lock['known_exposure_sha256'], 'Prelocked history changed.')
    episodes = [e for e in dev_manifest['episodes'] if e['shots'] == 4]
    lookups = {ds: inventory(config, ds) for ds in config['roots']}
    for row in query_lock['selected_queries']:
        require(len(row['normal_ids']) == len(row['anomaly_ids']) == 10
                and row['query_ids'] == row['normal_ids']+row['anomaly_ids'], 'Balanced query lock differs.')
        lookup = lookups[row['dataset']][1]
        for label in ['normal', 'anomaly']:
            require(all(lookup[i].label == label and lookup[i].split in {'test', 'test_public'}
                        and lookup[i].category == row['category'] for i in row[label+'_ids']),
                    'Balanced lock metadata differs from native inventory.')
    cases = []
    baseline = {'original': [], 'fixed_avg': []}
    for e in episodes:
        lookup = lookups[e['dataset']][1]
        cases.extend(dict(dataset=e['dataset'], category=e['category'], seed=e['seed'], episode_id=e['id'],
                          query_id=i, label=int(lookup[i].label != 'normal')) for i in e['query_ids'])
        previous = read_jsonl(Path(config['previous_run'])/'episodes'/e['id']/'predictions.jsonl')
        for name, method in [('original', 'safal'), ('fixed_avg', 'fixed_avg')]:
            selected = [r for r in previous if r['method'] == method]
            require(len(selected) == 20 and {r['query_id'] for r in selected} == set(e['query_ids']), 'Legacy case pairing differs.')
            rows = {r['query_id']: r for r in selected}
            baseline[name].extend(rows[i]['image_score'] for i in e['query_ids'])
    compare(document(run/'development'/'cases.json'), cases, 'Saved development cases')
    grid_params = parameter_grid(config)
    require(len(grid_params) == 768 and sum(eligible(p) for p in grid_params) == 576, 'Predeclared grid counts differ.')
    banks = load_raw_banks(run, episodes, config['feature_configs'][0], config['grid']['explained_variance'])
    originals = score_saved_raw(banks, Parameters());fixed = score_saved_raw(banks, Parameters(fusion='fixed'))
    for name, scores in [('original', originals), ('fixed_avg', fixed)]:
        require(np.max(np.abs(scores-np.asarray(baseline[name]))) <= 1e-12
                and np.array_equal(scores >= 1, np.asarray(baseline[name]) >= 1), 'Legacy score/decision parity fails.')
    labels = np.asarray([c['label'] for c in cases], dtype=bool)
    correct = {name: int(np.count_nonzero((np.asarray(values) >= 1) == labels)) for name, values in baseline.items()}
    require(correct == {'original': 243, 'fixed_avg': 240}, 'Legacy k4 development counts changed.')
    parity = document(run/'development'/'baseline_parity.json')
    require(parity['correct'] == correct and parity['matched_shots'] == 4 and parity['total_cases'] == 300,
            'Saved parity scope/counts differ.')
    fallback_p = Parameters(fusion='max', image_threshold=.5)
    fallback = candidate_metrics(fallback_p, score_saved_raw(banks, fallback_p), cases, baseline, config['feature_configs'][0]['id'])
    require(fallback['feasible'], 'Predeclared fallback violates direct case-preservation constraints.')
    compare(document(run/'development'/'fallback.json'), fallback, 'Fallback')
    cache = {};recomputed = [];score_rows = []
    for p in grid_params:
        key = (p.explained_variance, p.normal_quantile, p.aggregation, p.fusion, p.search_weight)
        if key not in cache:cache[key] = score_saved_raw(banks, p)
        scores = cache[key];score_rows.append(scores)
        recomputed.append(candidate_metrics(p, scores, cases, baseline, config['feature_configs'][0]['id']))
    compare(document(run/'development'/'grid.json'), recomputed, '768-cell development grid')
    with np.load(run/'development'/'grid_scores.npz', allow_pickle=False) as archive:
        require(set(archive.files) == {'scores', 'ids', 'original', 'fixed_avg'} and archive['scores'].shape == (768, 300)
                and np.isfinite(archive['scores']).all(), 'Grid score archive schema differs.')
        require(np.array_equal(archive['ids'], np.array([p.id for p in grid_params])), 'Grid parameter pairing differs.')
        require(np.allclose(archive['scores'], np.stack(score_rows), rtol=1e-12, atol=1e-12), 'Saved grid scores differ from raw recomputation.')
        require(np.array_equal(archive['original'], np.array(baseline['original']))
                and np.array_equal(archive['fixed_avg'], np.array(baseline['fixed_avg'])), 'Grid baseline score pairing differs.')
    stage1 = select_candidate(recomputed)
    compare(document(run/'development'/'stage1_selection.json'), dict(winner=stage1,
            unconstrained_best=min([r for r in recomputed if r['eligible']], key=selection_key),
            best_endpoint_control=min([r for r in recomputed if not r['eligible']], key=selection_key),
            feasible_hybrids=sum(r['eligible'] and r['feasible'] for r in recomputed)), 'Stage1 selection')
    compare(lock['stage1_winner'], stage1, 'Locked stage1 winner')
    params = Parameters(**stage1['params']);comparisons = [stage1]
    feature_banks = {config['feature_configs'][0]['id']: banks}
    feature_scores = {config['feature_configs'][0]['id']: score_saved_raw(banks, params)}
    for feature in config['feature_configs'][1:]:
        new_banks = load_raw_banks(run, episodes, feature, config['grid']['explained_variance'])
        scores = score_saved_raw(new_banks, params)
        comparisons.append(candidate_metrics(params, scores, cases, baseline, feature['id'], 1))
        feature_banks[feature['id']] = new_banks;feature_scores[feature['id']] = scores
    compare(document(run/'development'/'feature_comparison.json'), comparisons, 'Feature comparisons')
    final = select_candidate(comparisons)
    compare(lock['winner'], final, 'Final feature winner')
    require(lock['params'] == stage1['params'] and lock['parameters_id'] == params.id
            and lock['feature'] in config['feature_configs'] and lock['feature']['id'] == final['feature_id'], 'Global winner lock differs.')
    final_scores = feature_scores[final['feature_id']]
    expected = [c | dict(method='selected', score=float(s), threshold=params.image_threshold,
                         decision=bool(s >= params.image_threshold), image_correct=bool((s >= params.image_threshold) == c['label']))
                for c, s in zip(cases, final_scores)]
    compare(read_jsonl(run/'development'/'selected_predictions.jsonl'), expected, 'Selected development predictions')
    models = {}
    for e, bank in zip(episodes, feature_banks[final['feature_id']]):
        folder = run/'models'/e['id'];saved = document(folder/'model.json')
        check_model_document(lock, saved, e)
        model = TunableSubspaceSearch.load(folder/'model')
        require(str(params.explained_variance) in model.retained_ranks
                and 0 <= model.retained_ranks[str(params.explained_variance)] <= model.numerical_rank,
                'Selected PCA retained rank invalid.')
        encoder = saved['provenance']['encoder']
        require(encoder['torch_version'] == str(torch.__version__) and encoder['numpy_version'] == np.__version__,
                'Audit runtime libraries differ from fitted model.')
        for relative, digest in encoder['source_files_sha256'].items():
            require(pre['input_sha256'][str(Path(config['encoder']['source_dir'])/relative)] == digest,
                    'Checkpoint encoder source file is not fingerprinted.')
        calibration = bank['model'].calibration_from_raw(bank['normals'], e['calibration_ids'], params)
        compare(asdict(model.calibration), asdict(calibration), 'Saved normal cutoffs')
        meta = bank['model']._calibration_records[params.id]
        compare(saved['calibration_metadata'], meta, 'Raw normal calibration ancestry')
        require(len(model.support_images) == 4 and all(x.dtype == torch.float64
                and tuple(x.shape) == ((lock['feature']['resolution']//14)**2, 768)
                and bool(torch.isfinite(x).all()) for x in model.support_images), 'Saved support feature dimensions/budget invalid.')
        models[e['id']] = model
    require(pre['input_sha256'][config['encoder']['checkpoint']] == CHECKPOINT_SHA256, 'Actual checkpoint fingerprint missing.')
    return dict(status='passed', mode='pre-verification', run=str(run), **split_counts,
                grid_cells_recomputed=768, eligible_hybrids=576, endpoint_controls=192,
                raw_feature_variants_checked=len(config['feature_configs']), frozen_models_checked=len(models),
                input_hashes_checked=len(pre['input_sha256']), frozen_artifacts_checked=len(lock['artifact_sha256']),
                selection_lock_sha256=sha256(run/'selection.lock.json'), winner=final,
                verification_inference_performed=False, verification_masks_read=False,
                source_probability_head_used=False, image_holdout_in_development_exposed_categories=True), config, lock, models, lookups


def metric_map(tokens, grid):
    return F.interpolate(tokens.detach().float().reshape(1, 1, *grid), (256, 256),
                         mode='bilinear', align_corners=False)[0, 0].numpy()


def audit_complete(run, config_path):
    report, config, lock, models, lookups = audit_development(run, config_path)
    destination = run/'verification';complete = document(destination/'completion.json')
    require(complete['selection_lock_sha256'] == sha256(run/'selection.lock.json')
            and complete['implementation_sha256'] == implementation_hashes(CODE), 'Verification completion lock/code mismatch.')
    for key in ['artifact_sha256', 'mask_input_sha256']:
        for path, expected in complete[key].items():require(sha256(path) == expected, 'Verification completion hash differs: '+path)
    require(complete['unique_queries'] == 100 and complete['paired_cases'] == 300 and complete['method_rows'] == 900
            and complete['masks_used_for_selection'] is False, 'Verification completion count/scope differs.')
    query_lock = document(config['verification_query_lock']);rows = read_jsonl(destination/'predictions.jsonl')
    require(len(rows) == 900, 'Expected900 three-method paired records.')
    by_case = defaultdict(list)
    for row in rows:by_case[row['episode_id'], row['query_id']].append(row)
    masks = {};seen_maps = set();metrics = [];pairs = {'original': [], 'fixed_avg': []}; totals = defaultdict(Counter)
    params = Parameters(**lock['params'])
    for episode in query_lock['episodes']:
        root, lookup = lookups[episode['dataset']];folder = destination/episode['id']
        truths=[];maps={method:[] for method in ['original','fixed_avg','selected']};scores={method:[] for method in maps};labels=[]
        for index, identifier in enumerate(episode['query_ids']):
            case=by_case[episode['id'],identifier]
            require(len(case)==3 and {r['method'] for r in case}==set(maps), 'Verification method/query pairing differs.')
            sample=lookup[identifier];label=int(sample.label != 'normal');labels.append(label)
            if sample.mask:
                masks[str(root/sample.mask)]=sha256(root/sample.mask)
                with Image.open(root/sample.mask) as image:truth=np.asarray(image.convert('L').resize((256,256),Image.Resampling.NEAREST))>0
            else:truth=np.zeros((256,256),dtype=bool)
            require(bool(truth.any())==bool(label), 'Native anomaly disappeared from metric truth.')
            path=folder/f'query-{index:03d}.npz'
            with np.load(path,allow_pickle=False) as archive:
                require(set(archive.files)=={'truth','original','fixed_avg','selected'}, 'Verification map schema differs.')
                fields={k:archive[k].copy() for k in archive.files}
            require(fields['truth'].dtype==np.uint8 and fields['truth'].shape==(256,256)
                    and np.array_equal(fields['truth'],truth.astype(np.uint8)), 'Saved/native resized truth differs.')
            truths.append(truth);seen_maps.add(path)
            lookup_rows={r['method']:r for r in case}
            for method,row in lookup_rows.items():
                threshold=params.image_threshold if method=='selected' else 1.
                expected_params=params if method=='selected' else Parameters(fusion='fixed') if method=='fixed_avg' else Parameters()
                require((row['dataset'],row['category'],row['seed'],row['shots'],row['k_plus_calibration'])
                        ==(episode['dataset'],episode['category'],episode['seed'],4,8), 'Verification budget/case identity differs.')
                require(row['label']==label and row['threshold']==threshold and row['parameters_id']==expected_params.id
                        and row['decision']==(row['score']>=threshold) and row['image_correct']==(row['decision']==bool(label)), 'Verification decision/label/parameters differ.')
                require(row['metric_geometry']==[256,256] and row['pixel_threshold']==1.
                        and row['map_dtype']=='float32' and row['probabilities'] is None
                        and row['map_file']==str(path) and row['selection_lock_sha256']==sha256(run/'selection.lock.json'), 'Verification geometry/probability/lock differs.')
                require(np.isfinite(row['score']) and row['score']>=0 and all(np.isfinite(row[k]) and 0<=row[k]<=1 for k in ['A','U']), 'Invalid scalar diagnostic.')
                field=fields[method]
                require(field.dtype==np.float32 and field.shape==(256,256) and np.isfinite(field).all()
                        and (field>=0).all(), 'Invalid full-precision metric map.')
                maps[method].append(field);scores[method].append(row['score'])
                totals[method]['cases']+=1;totals[method]['correct']+=int(row['image_correct'])
                totals[method]['misses']+=int(label and not row['decision']);totals[method]['false_positives']+=int(not label and row['decision'])
            for comparator in pairs:
                pairs[comparator].append(dict(dataset=episode['dataset'],category=episode['category'],query_id=identifier,
                    seed=episode['seed'],paired_difference=int(lookup_rows['selected']['image_correct'])-int(lookup_rows[comparator]['image_correct'])))
        for method in maps:
            threshold=params.image_threshold if method=='selected' else 1.
            metrics.append(dict(dataset=episode['dataset'],category=episode['category'],seed=episode['seed'],episode_id=episode['id'],method=method,
                detection=thresholded_detection_metrics(labels,scores[method],threshold),
                localization=localization_metrics(truths,maps[method],1.,max_thresholds=128)))
        with np.load(folder/'replay_probe.npz',allow_pickle=False) as archive:
            require(set(archive.files)=={'tokens','grid','expected_score','expected_map','query_id'}, 'Replay probe schema differs.')
            probe={k:archive[k].copy() for k in archive.files}
        require(probe['query_id'].item()==episode['query_ids'][0] and probe['tokens'].dtype==np.float32
                and probe['tokens'].shape==((lock['feature']['resolution']//14)**2,768)
                and np.isfinite(probe['tokens']).all(), 'Replay token/query schema differs.')
        model=models[episode['id']];raw=model.score_raw(torch.from_numpy(probe['tokens']))
        result=model.predict_from_raw(raw,params,model.calibration)
        close(result['image_score'],probe['expected_score'].item(),'Frozen query image replay differs.',1e-11)
        require(np.array_equal(result['map'].numpy(),probe['expected_map']), 'Frozen token map replay differs.')
        selected=next(r for r in by_case[episode['id'],episode['query_ids'][0]] if r['method']=='selected')
        close(result['image_score'],selected['score'],'Replay/prediction scalar differs.')
        with np.load(folder/'query-000.npz',allow_pickle=False) as archive:
            require(np.array_equal(archive['selected'],metric_map(result['map'],tuple(probe['grid'].tolist()))), 'Frozen resized metric-map replay differs.')
    require(set(by_case)=={(e['id'],i) for e in query_lock['episodes'] for i in e['query_ids']}, 'Unexpected verification cases.')
    require(set(destination.glob('*/query-*.npz'))==seen_maps and len(seen_maps)==300, 'Unread/unreferenced verification maps.')
    require(masks==complete['mask_input_sha256'], 'Verification native-mask fingerprint coverage differs.')
    compare(document(destination/'episode_metrics.json'),metrics,'Recomputed verification metrics')
    overall={method:dict(counts,accuracy=counts['correct']/counts['cases']) for method,counts in totals.items()}
    paired={method:paired_crossed_bootstrap(values,n_bootstrap=1000,seed=917) for method,values in pairs.items()}
    report.update(mode='complete',verification_inference_performed=True,verification_masks_read=True,
        verification_method_records=900,verification_cases=300,verification_unique_queries=100,
        resized_float32_maps_checked=300,serialized_query_replays=15,native_masks_fingerprint_checked=len(masks),
        verification_artifact_hashes_checked=len(complete['artifact_sha256']),verification_metrics_recomputed=True,
        verification_results=overall,paired_selected_minus_comparator_accuracy=paired,
        native_resolution_localization_replayed=False,native_probability_calibration_claim=False,
        limitations=['100 fresh images in five development-exposed categories; no unseen-category/full-benchmark guarantee.',
                     'Metrics use resized256x256 maps and nearest-resized truth; no native-resolution claim.',
                     'Paired cases reuse100 queries across3 support draws; they are not300 independent images.',
                     'Development native labels selected the global configuration; verification did not select parameters.'])
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,default=Path('/tmp/safal_tuning_20261014'))
    parser.add_argument('--config',type=Path,default=Path('/workspace/tools/configs/safal_tuning_20261014.json'))
    parser.add_argument('--output',type=Path)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--pre-verification',action='store_true');mode.add_argument('--complete',action='store_true')
    args=parser.parse_args();run=args.run.absolute()
    output=args.output or run/('development_audit.json' if args.pre_verification else 'artifact_audit.json')
    try:
        report=audit_development(run,args.config)[0] if args.pre_verification else audit_complete(run,args.config)
    except Exception as exc:
        report=dict(status='failed',mode='pre-verification' if args.pre_verification else 'complete',run=str(run),
                    exception=type(exc).__name__,reason=str(exc))
        write_json(output,report);print(json.dumps(report));raise SystemExit(1)
    write_json(output,report);print(json.dumps(report,allow_nan=False))


if __name__=='__main__':
    main()
