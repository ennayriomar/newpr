from pathlib import Path
import tempfile
import unittest

from safe_iad.vision_hybrid_cli import paired_auc_interval,select_candidate,stage_lock


class ProtocolTests(unittest.TestCase):
    def test_source_pixel_guard_can_reject_best_image_auc(self):
        baseline={'id':'base','params':{'strength':0.,'clusters':1},'mean_image_auroc':.9,'mean_pixel_ap':.5}
        harmful={'id':'harm','params':{'strength':.1,'clusters':4},'mean_image_auroc':.99,'mean_pixel_ap':.49}
        useful={'id':'use','params':{'strength':.1,'clusters':4},'mean_image_auroc':.91,'mean_pixel_ap':.51}
        self.assertEqual(select_candidate([baseline,harmful,useful]),useful)
        self.assertEqual(select_candidate([baseline,harmful]),baseline)

    def test_exact_tie_prefers_no_correction(self):
        baseline={'id':'z','params':{'strength':0.,'clusters':1},'mean_image_auroc':.9,'mean_pixel_ap':.5}
        candidate={'id':'a','params':{'strength':.1,'clusters':4},'mean_image_auroc':.9,'mean_pixel_ap':.5}
        self.assertEqual(select_candidate([candidate,baseline]),baseline)

    def test_auc_bootstrap_handles_ties_and_paired_strata(self):
        rows=[]
        for category in ['a','b']:
            for seed in [17,29]:
                for label in [0,1]:
                    for method in ['baseline','hybrid']:
                        if category=='a':score=(.4 if label else .6) if method=='baseline' else (.7 if label else .6)
                        else:score=(.6 if label else .4) if method=='baseline' else .5
                        rows.append(dict(dataset='synthetic',category=category,seed=seed,query_id=str(label),
                                         method=method,label=label,score=score))
        # First category gains1.0 AUC, second loses0.5; macro difference0.25.
        got=paired_auc_interval(rows,n_bootstrap=100,seed=3)
        self.assertEqual(got['estimate'],.25)
        self.assertEqual(got['interval'],[.25,.25])
        with self.assertRaises(ValueError):paired_auc_interval(rows[:-1],n_bootstrap=10)

    def test_exclusive_stage_guard_releases_after_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            with stage_lock(Path(directory)):
                with self.assertRaises(ValueError):
                    with stage_lock(Path(directory)):pass
            with stage_lock(Path(directory)):pass


if __name__=='__main__':unittest.main()
