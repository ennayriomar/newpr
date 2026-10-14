"""Synthetic guards for the external tuning auditor; no inference or file edits.

The fixtures reuse native ID/schema/encoder metadata from existing JSON records.
All mutations happen to deep copies in memory. Placeholder tensor/archive hashes
are not scientific evidence and are never used to load checkpoint arrays.
Run only after /tmp/audit_safal_tuning_20261014.py is ready.
"""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest


AUDIT_PATH = Path('/tmp/audit_safal_tuning_20261014.py')
PLAN_ROOT = Path('/tmp/safal_tuning_20261014')
RUN_ROOT = Path('/tmp/safal_training_20261014')
TOOLS_ROOT = Path('/workspace/tools')
AUDITOR = None


def read_json(path):
    return json.loads(Path(path).read_text())


def parameter_id(params):
    payload = json.dumps(params, sort_keys=True, separators=(',', ':'), allow_nan=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def setUpModule():
    global AUDITOR
    if not AUDIT_PATH.is_file():
        raise RuntimeError('External audit helper is not ready; do not run these tests yet.')
    sys.path.insert(0, str(TOOLS_ROOT))
    spec = importlib.util.spec_from_file_location('external_safal_tuning_audit_tests', AUDIT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    for name in ['check_model_document', 'check_query_isolation']:
        if not callable(getattr(module, name, None)):
            raise RuntimeError('External audit helper does not expose '+name)
    AUDITOR = module


def model_fixture():
    config = read_json(TOOLS_ROOT/'configs/safal_tuning_20261014.json')
    development = read_json(RUN_ROOT/'manifest.json')
    episode = next(e for e in development['episodes']
                   if e['id'] == 'mvtec_ad-cable-k4-seed17')
    original = read_json(RUN_ROOT/'episodes'/episode['id']/'model.json')
    feature = deepcopy(config['feature_configs'][0])
    params = dict(explained_variance=.99, normal_quantile=.95, aggregation='top1',
                  fusion='adaptive_original', search_weight=.5, image_threshold=1.)
    pid = parameter_id(params)
    calibration_ids = deepcopy(episode['calibration_ids'])
    calibration = dict(image_search=.1, image_subspace=2., pixel_search=.2,
                       pixel_subspace=3., calibration_ids=calibration_ids)
    calibration_meta = dict(
        parameters_id=pid, calibration_ids=deepcopy(calibration_ids),
        normal_quantile=params['normal_quantile'], aggregation=params['aggregation'],
        explained_variance=params['explained_variance'],
        raw_normal_score_sha256={identifier: {'search': '1'*64, 'subspace': '2'*64}
                                 for identifier in calibration_ids},
        procedure='Separate branch-image and pooled-raw-token normal quantiles; linear interpolation',
        extra_normal_calibration_images=4, support_overlap=0,
        caller_declared_normal=True, query_labels_accepted=False,
        probability_calibration=False)
    document = dict(
        schema_version=1, kind='TunableSubspaceSearch',
        support_ids=deepcopy(episode['support_ids']),
        support_array_keys=[f'support_{i:03d}' for i in range(4)],
        variances=[.9, .95, .99, .995], chunk=256,
        params=deepcopy(params), parameters_id=pid,
        calibration=calibration, calibration_metadata=calibration_meta,
        provenance=dict(encoder=deepcopy(original['provenance']['encoder']),
                        feature_id=feature['id'], episode=deepcopy(episode),
                        k_plus_calibration=8, strict_k_image_few_shot=False,
                        parameter_selection='Synthetic valid audit fixture',
                        error_head=None, probabilities=False),
        support_feature_sha256={identifier: '3'*64 for identifier in episode['support_ids']},
        implementation_sha256={name: hashlib.sha256((TOOLS_ROOT/'safe_iad'/name).read_bytes()).hexdigest()
                               for name in ['safal_tunable.py', 'subspace_search.py']},
        npz_sha256='4'*64)
    winner = dict(id=pid, params=deepcopy(params), eligible=True, feasible=True,
                  feature_id=feature['id'], feature_changes=0,
                  losses_vs_original=0, losses_vs_fixed=0)
    lock = dict(schema_version=1, params=deepcopy(params), parameters_id=pid,
                winner=winner, stage1_winner=deepcopy(winner), feature=feature,
                verification_scores_seen=False, verification_masks_seen=False)
    return deepcopy(lock), deepcopy(document), deepcopy(episode)


def query_fixture():
    return (read_json(PLAN_ROOT/'known_exposure.json'),
            read_json(PLAN_ROOT/'verification_query_lock.json'),
            read_json(RUN_ROOT/'manifest.json'))


class ModelDocumentGuards(unittest.TestCase):
    def setUp(self):
        self.lock, self.document, self.episode = model_fixture()

    def reject(self):
        with self.assertRaises(ValueError):
            AUDITOR.check_model_document(self.lock, self.document, self.episode)

    def test_valid_document_passes(self):
        AUDITOR.check_model_document(self.lock, self.document, self.episode)

    def test_document_parameters_differ_from_locked_parameters(self):
        self.document['params']['normal_quantile'] = .9
        self.document['parameters_id'] = parameter_id(self.document['params'])
        self.reject()

    def test_document_parameter_fingerprint_tampered(self):
        self.document['parameters_id'] = '0'*64
        self.reject()

    def test_lock_parameter_fingerprint_tampered(self):
        self.lock['parameters_id'] = '0'*64
        self.reject()

    def test_winner_parameters_differ_from_locked_parameters(self):
        self.lock['winner']['params']['image_threshold'] = .75
        self.reject()

    def test_winner_parameter_fingerprint_tampered(self):
        self.lock['winner']['id'] = '0'*64
        self.reject()

    def test_saved_feature_identity_differs_from_lock(self):
        self.document['provenance']['feature_id'] = 'late224'
        self.reject()

    def test_winner_feature_identity_differs_from_lock(self):
        self.lock['winner']['feature_id'] = 'late224'
        self.reject()

    def test_encoder_resolution_differs_from_locked_feature(self):
        self.document['provenance']['encoder']['resolution'] = 336
        self.reject()

    def test_encoder_layers_differ_from_locked_feature(self):
        self.document['provenance']['encoder']['layers'] = [8, 9, 10, 11]
        self.reject()

    def test_encoder_checkpoint_is_not_pinned(self):
        self.document['provenance']['encoder']['checkpoint_sha256'] = '0'*64
        self.reject()

    def test_encoder_is_not_frozen(self):
        self.document['provenance']['encoder']['frozen'] = False
        self.reject()

    def test_support_ids_differ_from_authoritative_episode(self):
        self.document['support_ids'][0] = self.episode['calibration_ids'][0]
        self.reject()

    def test_support_budget_has_only_three_images(self):
        self.document['support_ids'].pop()
        self.reject()

    def test_calibration_ids_differ_from_authoritative_episode(self):
        self.document['calibration']['calibration_ids'][0] = self.episode['support_ids'][0]
        self.reject()

    def test_calibration_budget_has_only_three_images(self):
        self.document['calibration']['calibration_ids'].pop()
        self.reject()

    def test_calibration_metadata_parameter_id_is_inconsistent(self):
        self.document['calibration_metadata']['parameters_id'] = '0'*64
        self.reject()

    def test_calibration_metadata_settings_are_inconsistent(self):
        for field, changed in [('normal_quantile', .9), ('aggregation', 'max'),
                               ('explained_variance', .95)]:
            with self.subTest(field=field):
                self.lock, self.document, self.episode = model_fixture()
                self.document['calibration_metadata'][field] = changed
                self.reject()

    def test_calibration_metadata_ids_are_inconsistent(self):
        self.document['calibration_metadata']['calibration_ids'][0] = self.episode['support_ids'][0]
        self.reject()

    def test_calibration_metadata_normal_budget_is_inconsistent(self):
        self.document['calibration_metadata']['extra_normal_calibration_images'] = 3
        self.reject()

    def test_declared_total_budget_cannot_claim_strict_four_shot(self):
        self.document['provenance']['strict_k_image_few_shot'] = True
        self.reject()


class QueryIsolationGuards(unittest.TestCase):
    def setUp(self):
        self.exposure, self.query_lock, self.development = query_fixture()

    def reject(self):
        with self.assertRaises(ValueError):
            AUDITOR.check_query_isolation(self.exposure, self.query_lock, self.development)

    def test_existing_fresh_query_lock_passes(self):
        AUDITOR.check_query_isolation(self.exposure, self.query_lock, self.development)

    def test_known_exposure_overlap_is_rejected(self):
        e = self.query_lock['episodes'][0]
        self.exposure['native_query_ids'].append(e['dataset']+':'+e['query_ids'][0])
        self.reject()

    def test_development_query_overlap_is_rejected(self):
        e = self.query_lock['episodes'][0]
        development = next(d for d in self.development['episodes'] if d['id'] == e['id'])
        development['query_ids'][0] = e['query_ids'][0]
        self.reject()

    def test_unique_query_count_reduced_to_ninety_nine_is_rejected(self):
        first = self.query_lock['episodes'][0]
        lost, replacement = first['query_ids'][:2]
        for e in self.query_lock['episodes']:
            if e['dataset'] == first['dataset'] and e['category'] == first['category']:
                e['query_ids'] = [replacement if q == lost else q for q in e['query_ids']]
        self.reject()

    def test_missing_bank_is_rejected(self):
        self.query_lock['episodes'].pop()
        self.reject()

    def test_duplicate_bank_identity_is_rejected(self):
        self.query_lock['episodes'][-1] = deepcopy(self.query_lock['episodes'][0])
        self.reject()

    def test_support_bank_identity_differs_from_development(self):
        e = self.query_lock['episodes'][0]
        e['support_ids'][0] = e['calibration_ids'][0]
        self.reject()

    def test_calibration_bank_identity_differs_from_development(self):
        e = self.query_lock['episodes'][0]
        e['calibration_ids'][0] = e['support_ids'][0]
        self.reject()

    def test_matched_bank_cannot_change_seed(self):
        self.query_lock['episodes'][0]['seed'] = 999
        self.reject()

    def test_matched_bank_cannot_change_shot_budget(self):
        self.query_lock['episodes'][0]['shots'] = 8
        self.reject()


if __name__ == '__main__':
    unittest.main(verbosity=2)
