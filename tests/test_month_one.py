import copy
import json
import sys
import unittest
import tempfile
import wave
import struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/video'))
from month_one_core import load_episodes,make_timeline,normalized,script,caption_chunks,fit_caption_timing
from month_one_metrics import analyze
from synthesize_month_one import finalize_stream_wav

class MonthOneTests(unittest.TestCase):
    def setUp(self):
        self.plan=json.loads((ROOT/'experiments/month-one-v1.json').read_text())

    def test_streaming_wav_header_finalized_without_changing_samples(self):
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'stream.wav'; target=Path(directory)/'final.wav'
            samples=struct.pack('<4h',0,32767,-32768,1234)*100
            with wave.open(str(source),'wb') as writer:
                writer.setparams((1,2,44100,0,'NONE','not compressed'));writer.writeframes(samples)
            raw=bytearray(source.read_bytes())
            raw[4:8]=struct.pack('<I',0xffffffff);raw[40:44]=struct.pack('<I',0xfffffffe)
            source.write_bytes(raw)
            result=finalize_stream_wav(source,target)
            self.assertEqual(result['finalized_frames'],400)
            self.assertAlmostEqual(result['duration'],400/44100)
            with wave.open(str(target)) as reader:
                self.assertEqual(reader.getnframes(),400)
                self.assertEqual(reader.readframes(1000),samples)

    def test_caption_timing_borrows_pause_with_bounded_sync_and_fails_if_impossible(self):
        captions=[{'text':'A short opening.', 'spoken_start':.12,'spoken_end':1.2},
                  {'text':'This longer phrase needs more reading time.', 'spoken_start':1.5,'spoken_end':3.3},
                  {'text':'Last line.', 'spoken_start':3.5,'spoken_end':4.2}]
        fit_caption_timing(captions,5)
        for i,c in enumerate(captions):
            self.assertLessEqual(c['cps'],20.001)
            if i:
                self.assertAlmostEqual(c['start'],captions[i-1]['end'])
                self.assertGreaterEqual(c['start'],c['spoken_start']-.450001)
                self.assertLessEqual(c['start'],captions[i-1]['spoken_end']+.450001)
        with self.assertRaisesRegex(ValueError,'cannot fit'):
            fit_caption_timing(captions,1)

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
