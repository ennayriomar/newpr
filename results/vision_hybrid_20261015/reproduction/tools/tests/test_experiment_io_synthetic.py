"""Synthetic stage-ledger tests; no dataset/backbone results are asserted."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from safe_iad.build_benefit_targets import TARGET_IMPLEMENTATIONS, build
from safe_iad.experiment_io import (complete_stage, implementation_hashes,
                                    input_fingerprints, git_revision, sha256, verify_stage, write_json)


class SyntheticExperimentIOTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.stage = self.root/'stage'
        self.stage.mkdir()
        self.output = self.stage/'result.json'
        write_json(self.output, {'synthetic': True})
        self.source = self.root/'source.png'
        self.source.write_bytes(b'synthetic source bytes')
        self.implementation = self.root/'used.py'
        self.implementation.write_text('# synthetic implementation\n')

    def extra(self):
        return {'input_verification_version': 1,
                'input_sha256': input_fingerprints([self.source]),
                'implementation_sha256': {str(self.implementation): sha256(self.implementation)}}

    def complete(self):
        complete_stage(self.stage, ['result.json'], self.extra())

    def test_missing_stage_returns_false(self):
        self.assertFalse(verify_stage(self.stage, require_inputs=True))

    def test_output_input_and_code_fingerprints_verified(self):
        self.complete()
        self.assertTrue(verify_stage(self.stage, require_inputs=True,
                                     implementation_files=[str(self.implementation)]))
        ledger = json.loads((self.stage/'completion.json').read_text())
        self.assertEqual(set(ledger['input_sha256']), {str(self.source.absolute())})

    def test_changed_source_checkpoint_or_generated_input_rejected(self):
        for name in ['source.png', 'candidate.png', 'generated.png', 'generated_mask.png',
                     'checkpoint.pth', 'provenance.json', 'split.csv']:
            with self.subTest(input=name), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                used = directory/name
                used.write_bytes(b'original synthetic input')
                write_json(directory/'output.json', {'synthetic': True})
                extra = {'input_verification_version': 1, 'input_sha256': input_fingerprints([used]),
                         'implementation_sha256': implementation_hashes(['experiment_io.py'])}
                complete_stage(directory, ['output.json'], extra)
                used.write_bytes(b'changed synthetic input')
                with self.assertRaisesRegex(ValueError, 'input changed'):
                    verify_stage(directory, require_inputs=True)

    def test_missing_input_rejected(self):
        self.complete()
        self.source.unlink()
        with self.assertRaisesRegex(ValueError, 'input is missing'):
            verify_stage(self.stage, require_inputs=True)

    def test_output_hash_checks_preserved(self):
        self.complete()
        self.output.write_text('{}\n')
        with self.assertRaisesRegex(ValueError, 'artifact changed'):
            verify_stage(self.stage, require_inputs=True)

    def test_used_implementation_changed_rejected(self):
        self.complete()
        self.implementation.write_text('# changed synthetic implementation\n')
        with self.assertRaisesRegex(ValueError, 'implementation changed'):
            verify_stage(self.stage, require_inputs=True)

    def test_unrelated_module_addition_does_not_invalidate_stage(self):
        self.complete()
        (self.root/'unrelated.py').write_text('# unrelated synthetic module\n')
        self.assertTrue(verify_stage(self.stage, require_inputs=True,
                                     implementation_files=[str(self.implementation)]))
        with patch('pathlib.Path.glob', side_effect=AssertionError('must not scan the package')):
            self.assertEqual(set(implementation_hashes(['experiment_io.py'])), {'experiment_io.py'})

    def test_dependency_set_change_rejected(self):
        self.complete()
        with self.assertRaisesRegex(ValueError, 'dependency set changed'):
            verify_stage(self.stage, require_inputs=True,
                         implementation_files=[str(self.implementation), 'extra.py'])

    def test_legacy_input_unverified_completion_rejected_for_targets(self):
        complete_stage(self.stage, ['result.json'])
        with self.assertRaisesRegex(ValueError, 'Legacy completion.*new output directory'):
            verify_stage(self.stage, require_inputs=True)
        # Other callers can explicitly retain output-only compatibility.
        self.assertTrue(verify_stage(self.stage))

    def test_changed_dependency_during_computation_prevents_completion(self):
        snapshot = self.extra()
        self.source.write_bytes(b'changed after snapshot')
        with self.assertRaisesRegex(ValueError, 'input changed'):
            complete_stage(self.stage, ['result.json'], snapshot)
        self.assertFalse((self.stage/'completion.json').exists())

    def test_configured_symlink_target_change_invalidates_input(self):
        original = self.root/'original'
        replacement = self.root/'replacement'
        original.write_bytes(b'original input')
        replacement.write_bytes(b'replacement input')
        configured = self.root/'configured'
        configured.symlink_to(original)
        extra = self.extra()
        extra['input_sha256'] = input_fingerprints([configured])
        complete_stage(self.stage, ['result.json'], extra)
        configured.unlink()
        configured.symlink_to(replacement)
        with self.assertRaisesRegex(ValueError, 'input changed'):
            verify_stage(self.stage, require_inputs=True)

    def test_git_revision_checked_before_resume(self):
        extra = self.extra()
        extra['git_revisions'] = {str(self.root/'synthetic-checkout'): 'original-revision'}
        with patch('safe_iad.experiment_io.git_revision', return_value='original-revision'):
            complete_stage(self.stage, ['result.json'], extra)
            self.assertTrue(verify_stage(self.stage, require_inputs=True))
        with patch('safe_iad.experiment_io.git_revision', return_value='changed-revision'):
            with self.assertRaisesRegex(ValueError, 'source revision changed'):
                verify_stage(self.stage, require_inputs=True)

    def test_dirty_backbone_source_checkout_rejected(self):
        with patch('safe_iad.experiment_io.subprocess.check_output',
                   side_effect=['synthetic-revision\n', ' M synthetic-backbone.py\n']):
            with self.assertRaisesRegex(ValueError, 'tracked local changes'):
                git_revision(self.root/'synthetic-checkout')

    def test_builder_rejects_legacy_before_loading_backbone(self):
        config = {'output': str(self.root)}
        target = self.root/'targets'
        write_json(target/'config.json', config)
        complete_stage(target, ['config.json'])
        with patch('safe_iad.build_benefit_targets.FrozenDINOv2', side_effect=AssertionError('must not load weights')):
            with self.assertRaisesRegex(ValueError, 'Legacy completion'):
                build(config)

    def test_builder_verifies_all_dependencies_before_resumed_return(self):
        config = {'output': str(self.root)}
        target = self.root/'targets'
        write_json(target/'config.json', config)
        summary = {'synthetic_test_only': True}
        write_json(target/'summary.json', summary)
        extra = {'input_verification_version': 1, 'input_sha256': input_fingerprints([self.source]),
                 'implementation_sha256': implementation_hashes(TARGET_IMPLEMENTATIONS)}
        complete_stage(target, ['config.json', 'summary.json'], extra)
        with patch('safe_iad.build_benefit_targets.FrozenDINOv2', side_effect=AssertionError('must not load weights')):
            self.assertEqual(build(config), summary)
            self.source.write_bytes(b'changed source after completion')
            with self.assertRaisesRegex(ValueError, 'input changed'):
                build(config)


if __name__ == '__main__':
    unittest.main()
