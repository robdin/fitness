import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/video'))
from month_one_core import load_episodes,make_timeline,normalized,script,caption_chunks
from month_one_metrics import analyze

class MonthOneTests(unittest.TestCase):
    def setUp(self):
        self.plan=json.loads((ROOT/'experiments/month-one-v1.json').read_text())

    def test_content_coverage_and_source_resolution(self):
        eps=load_episodes();self.assertEqual(len(eps),16)
        self.assertEqual(len({e['id'] for e in eps}),16)
        sources={s['id'] for s in json.loads((ROOT/'research/month-one-sources.json').read_text())['sources']}
        support=json.loads((ROOT/'content/month-one/supporting-posts.json').read_text())
        days=[e['day'] for e in eps]+[c['day'] for c in support['carousels']]+[s['day'] for s in support['stories']]
        self.assertEqual(sorted(days),list(range(1,29)))
        for e in eps:
            self.assertTrue(set(e['source_ids'])<=sources)
            self.assertTrue(e['disclosure'] and e['comprehension']['answer'])
            self.assertLessEqual(len(script(e).split()),110)

    def test_every_draft_preserves_script_and_caption_bounds(self):
        for e in load_episodes():
            tl=make_timeline(e)
            self.assertEqual(normalized(script(e)),normalized(' '.join(c['text'] for c in tl['captions'])))
            last=0
            for c in tl['captions']:
                self.assertGreaterEqual(c['start'],last-.001)
                self.assertGreater(c['end'],c['start'])
                self.assertLessEqual(c['end'],tl['duration'])
                self.assertLessEqual(len(c['lines']),2)
                self.assertLessEqual(max(map(len,c['lines'])),34)
                self.assertLessEqual(c['cps'],20.01)
                last=c['end']

    def test_changed_script_rejects_stale_provider_alignment(self):
        ep=load_episodes()[0]
        bad={'0':{'offset':0,'alignment':{'segments':[{'text':'Old narration','start':0,'end':1}]}}}
        with self.assertRaisesRegex(ValueError,'does not match'):make_timeline(ep,bad,2)

    def test_empty_metrics_never_imply_failure_or_success(self):
        out=analyze([],{},self.plan)
        self.assertEqual(out['decision'],'INSUFFICIENT_EVIDENCE')
        self.assertIsNone(out['median_stayed_to_watch_pct'])

    def rows(self):
        # Synthetic fixtures only; never written to measurement observations.
        return [{'episode_id':f'M{i:02}','platform':'youtube_shorts','published_at':'2026-11-01T18:00:00-05:00','observed_at':'2026-11-08T18:00:00-05:00','window_hours':'168','engaged_views':'200','stayed_to_watch_pct':'65','average_percentage_viewed':'80','source_export':'SYNTHETIC_TEST_ONLY'} for i in range(1,13)]

    def ops(self):
        return {'comprehension_checks':10,'comprehension_passes':9,'distinct_useful_responses':6,'unresolved_recurring_critical_error':False,'weekly_operator_hours':[8,9],'simplification_attempted':False}

    def test_decision_gates_require_real_completeness(self):
        rows=self.rows();ops=self.ops()
        self.assertEqual(analyze(rows,ops,self.plan)['decision'],'GO_BOUNDED_MONTH_TWO')
        rows[0]['average_percentage_viewed']=''
        self.assertEqual(analyze(rows,ops,self.plan)['decision'],'INSUFFICIENT_EVIDENCE')
        rows=self.rows()
        for r in rows:r.update(stayed_to_watch_pct='30',average_percentage_viewed='40')
        ops['distinct_useful_responses']=0
        self.assertEqual(analyze(rows,ops,self.plan)['decision'],'NO_GO_CURRENT_FORMAT')

    def test_duplicate_or_immature_windows_rejected(self):
        rows=self.rows()
        with self.assertRaisesRegex(ValueError,'Duplicate'):analyze(rows+[rows[0]],self.ops(),self.plan)
        rows[0]['observed_at']='2026-11-02T18:00:00-05:00'
        with self.assertRaisesRegex(ValueError,'not mature'):analyze(rows,self.ops(),self.plan)

    def test_reels_not_pooled_with_youtube_and_no_causal_gate(self):
        rows=self.rows()
        for r in rows:r['platform']='instagram_reels'
        self.assertEqual(analyze(rows,self.ops(),self.plan)['mature_youtube_episodes'],0)
        ops=self.ops();ops['unresolved_recurring_critical_error']=True
        self.assertEqual(analyze(self.rows(),ops,self.plan)['decision'],'ITERATE')

if __name__=='__main__':unittest.main()
