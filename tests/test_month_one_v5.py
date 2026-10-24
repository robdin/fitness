import copy,json,sys,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/video'),str(ROOT/'tools/calendar')]
import produce_month_one_v5 as producer
from produce_month_one_v5 import episodes,CONFIG,TOKENS
from month_one_core import script,make_timeline,digest
from build_month_one_v5 import load,validate,outputs

class BlueprintTests(unittest.TestCase):
    def test_calendar_and_generated_copy_agree(self):
        d,s,p=load();self.assertTrue(validate(d,s,p))
        for name,body in outputs(d,s,p).items():self.assertEqual((ROOT/'content/month-one-v5'/name).read_bytes(),body.encode())

    def test_reused_narration_is_exact_and_new_topics_have_new_identity(self):
        old={e['id']:e for e in json.loads((ROOT/'content/month-one-v3/calendar.json').read_text())['episodes']}
        retained=[];new=[]
        for e in episodes():
            if e['voice_reuse_from']:
                self.assertEqual(script(e),' '.join(b['narration'] for b in old[e['voice_reuse_from']]['beats']))
                retained.append(e['id'])
            else:new.append(e['id'])
        self.assertEqual(len(retained),11)
        self.assertEqual(new,['BP04','BP07','BP11','BP14','BP15'])

    def test_citation_pair_changes_only_source_visibility(self):
        a,b=episodes()[2],episodes(False)[2]
        self.assertTrue(a['graphics'].pop('source_cue_visible'))
        self.assertFalse(b['graphics'].pop('source_cue_visible'))
        self.assertEqual(a,b)

    def test_cues_do_not_invent_study_support_for_editorial_work(self):
        for e in episodes():
            c=e['graphics']['source_cue']
            self.assertTrue(set(c['source_ids']).issubset(e['evidence_ids']))
            if c['kind']=='editorial':self.assertEqual(c['source_ids'],[])
        self.assertEqual(episodes()[2]['graphics']['source_cue']['source_ids'],['E16'])

    def test_caption_override_preserves_words_and_rejects_dropped_qualification(self):
        e=episodes()[10];tl=make_timeline(e)
        self.assertEqual(' '.join(c['text'] for c in tl['captions']),script(e))
        bad=copy.deepcopy(e);bad['caption_overrides']['0']=['Lunch is perfect.']
        with self.assertRaisesRegex(ValueError,'exact spoken text'):make_timeline(bad)

    def test_plan_has_no_results_or_stale_pillar_balance_claim(self):
        d,s,p=load()
        self.assertIn('not balanced by pillar',p['organic_comparison'])
        self.assertEqual(p['weekly_operator_hours_limit'],12)
        self.assertFalse(p['brand_screen']['conducted'])
        self.assertEqual(d['brand'],'blueprint')
        self.assertIsNone(json.loads(TOKENS.read_text())['public_name'])

    def test_restored_voice_needs_no_historical_audio_and_rejects_corruption(self):
        import hashlib
        ep=episodes()[0]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);work=root/'v5';target=work/'voice'/ep['id'];target.mkdir(parents=True)
            (target/'narration.wav').write_bytes(b'retained audio fixture')
            (target/'alignment.json').write_text('{}')
            (target/'generation.json').write_text(json.dumps(dict(status='complete',script_sha256=hashlib.sha256(script(ep).encode()).hexdigest(),audio_sha256=digest(target/'narration.wav'),alignment_sha256=digest(target/'alignment.json'))))
            with patch.object(producer,'ROOT',root),patch.object(producer,'WORKSPACE',work):
                self.assertTrue(producer.retain_voice(ep))
                (target/'narration.wav').write_bytes(b'changed')
                with self.assertRaises(AssertionError):producer.retain_voice(ep)

    def test_empty_blueprint_measurements_stay_insufficient(self):
        from evaluate_month_one_v3 import evaluate
        content,_,plan=load()
        ops=json.loads((ROOT/'measurement/month-one-v5-operations.json').read_text())
        result=evaluate([],ops,plan,content)
        self.assertEqual(result['decision'],'INSUFFICIENT_EVIDENCE')

if __name__=='__main__':unittest.main()
