import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'tools/video'),str(ROOT/'tools/calendar')]
from build_month_one_v3 import load,validate,outputs
from produce_month_one_v3 import episodes
from month_one_core import make_timeline
from package_month_one_v3 import validate_identity
from evaluate_month_one_v3 import evaluate

class BeginnerProductionTests(unittest.TestCase):
 def test_calendar_source_resolution_and_balance(self):
  d,s,p=load();self.assertTrue(validate(d,s,p))
  for name,body in outputs(d,s,p).items():self.assertEqual((ROOT/'content/month-one-v3'/name).read_bytes(),body.encode())
 def test_unknown_source_is_rejected(self):
  d,s,p=load();d['episodes'][0]['evidence_ids']=['MISSING']
  with self.assertRaises(AssertionError):validate(d,s,p)
 def test_caption_and_brand_staleness_are_rejected(self):
  e=episodes()[0];tl=make_timeline(e);tl['timing']='provider_word_alignment';receipt={'script_sha256':tl['script_sha256']};validate_identity(e,receipt,tl)
  for key in ['brand','tokens_sha256','font_sha256']:
   changed=copy.deepcopy(e);changed['graphics'][key]='changed'
   with self.assertRaises(ValueError):validate_identity(changed,receipt,tl)
  bad=copy.deepcopy(tl);bad['captions'][0]['text']='wrong'
  with self.assertRaises(ValueError):validate_identity(e,receipt,bad)
 def fixture(self):
  d,s,p=load();rows=[]
  for e in d['episodes'][:12]:
   from datetime import datetime,timedelta
   pub=datetime.fromisoformat(e['publish_at']);rows.append(dict(episode_id=e['id'],platform='youtube_shorts',published_at=pub.isoformat(),observed_at=(pub+timedelta(days=7)).isoformat(),window_hours=168,reporting_window='first_168_hours',engaged_views=100,stayed_to_watch_pct=65,average_percentage_viewed=75,source_export='synthetic_unit_test_only'))
  ops=dict(comprehension_checks=10,comprehension_passes=9,distinct_useful_responses=5,unresolved_recurring_critical_error=False,simplification_attempted=False,representative_production_batches=[dict(core_videos_created_or_substantially_reworked=4,source_labor_log='synthetic_unit_test_only',hands_on_hours=h) for h in [11,12]])
  return d,p,rows,ops
 def test_prebuilt_publishing_hours_cannot_pass_production_gate(self):
  d,p,rows,ops=self.fixture();ops.pop('representative_production_batches');ops['weekly_operator_hours']=[1,1]
  self.assertEqual(evaluate(rows,ops,p,d)['decision'],'INSUFFICIENT_EVIDENCE')
 def test_synthetic_decision_paths(self):
  d,p,rows,ops=self.fixture();self.assertEqual(evaluate(rows,ops,p,d)['decision'],'GO_BOUNDED_MONTH_TWO')
  ops['distinct_useful_responses']=1
  for r in rows:r['stayed_to_watch_pct']=30;r['average_percentage_viewed']=40
  self.assertEqual(evaluate(rows,ops,p,d)['decision'],'NO_GO_CURRENT_FORMAT')
  rows[0]['episode_id']='N01'
  with self.assertRaises(ValueError):evaluate(rows,ops,p,d)
 def test_empty_observations_are_not_failure(self):
  d,s,p=load();ops=json.loads((ROOT/'measurement/month-one-v3-operations.json').read_text());self.assertEqual(evaluate([],ops,p,d)['decision'],'INSUFFICIENT_EVIDENCE')
if __name__=='__main__':unittest.main()
