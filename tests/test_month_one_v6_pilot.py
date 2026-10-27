import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/video'))
from prepare_month_one_v6_pilot import status_for,check_current_inputs

class PilotReviewTests(unittest.TestCase):
    def fixture(self):
        account={'native_id':'SYNTHETIC','public_url':'https://example.invalid/test','verified_by':'TEST','verified_at':'2026-10-27T10:00:00-04:00','timezone':'America/New_York'}
        review={'episode_id':'BC01','media_sha256':'hash-a','kind':'listening','reviewer':'TEST','reviewed_at':'2026-10-27T10:00:00-04:00','result':'pass','notes':'Synthetic fixture only'}
        return {'accounts':{p:copy.deepcopy(account) for p in ['youtube_shorts','instagram_reels']},'reviews':[review]+[{**review,'kind':'native_preview','platform':p,'account_native_id':'SYNTHETIC'} for p in ['youtube_shorts','instagram_reels']]}
    def test_empty_ledger_cannot_approve(self):
        self.assertFalse(status_for('BC01','hash-a',{})['release_review_complete'])
    def test_exact_hash_and_both_platforms_required(self):
        ops=self.fixture();self.assertTrue(status_for('BC01','hash-a',ops)['release_review_complete'])
        self.assertFalse(status_for('BC01','hash-b',ops)['release_review_complete'])
        ops['reviews'].pop();self.assertFalse(status_for('BC01','hash-a',ops)['release_review_complete'])
    def test_newer_fix_request_revokes_previous_pass(self):
        ops=self.fixture();ops['reviews'].append({**ops['reviews'][0],'reviewed_at':'2026-10-27T11:00:00-04:00','result':'needs_fix'})
        self.assertFalse(status_for('BC01','hash-a',ops)['release_review_complete'])
    def test_naive_timestamp_or_missing_account_is_not_verified(self):
        ops=self.fixture();ops['reviews'][0]['reviewed_at']='2026-10-27T10:00:00'
        self.assertFalse(status_for('BC01','hash-a',ops)['release_review_complete'])
    def test_account_change_invalidates_old_native_preview(self):
        ops=self.fixture();ops['accounts']['instagram_reels']['native_id']='DIFFERENT_ACCOUNT'
        self.assertFalse(status_for('BC01','hash-a',ops)['release_review_complete'])
    def test_conflicting_latest_reviews_fail_closed(self):
        ops=self.fixture();ops['reviews'].append({**ops['reviews'][0],'result':'needs_fix'})
        self.assertFalse(status_for('BC01','hash-a',ops)['release_review_complete'])
    def test_changed_canonical_script_rejects_retained_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);file=folder/'BC01-motion.mp4'
            original={'id':'BC01','beats':[['hook','Original words']]}
            (folder/'timeline.json').write_text(json.dumps({'episode':original}))
            changed={**original,'beats':[['hook','Changed words']]}
            with self.assertRaisesRegex(ValueError,'not been rendered'):
                check_current_inputs(changed,file,{},folder/'renderer.cjs',folder/'voice')
        ops=self.fixture();ops['accounts']['instagram_reels']=None
        self.assertFalse(status_for('BC01','hash-a',ops)['release_review_complete'])

if __name__=='__main__':unittest.main()
