import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools/video'),str(ROOT/'tools/calendar')]
from produce_month_one_v6 import episodes,TOKENS
from build_month_one_v6 import load,validate,outputs
from month_one_core import script,make_timeline

class ConversationalBlueprintTests(unittest.TestCase):
    def test_compiled_copy_and_calendar_are_current(self):
        d,s,p=load();self.assertTrue(validate(d,s,p))
        for name,body in outputs(d,s,p).items():self.assertEqual((ROOT/'content/month-one-v6'/name).read_bytes(),body.encode())

    def test_intro_is_separate_and_all_new_scripts_need_new_audio(self):
        d,s,p=load();self.assertEqual(len(d['episodes']),16)
        self.assertEqual(d['orientation_asset']['id'],'BC00');self.assertNotIn('BC00',p['episode_ids'])
        self.assertFalse(p['orientation_asset']['counted_in_core_cohort'])
        old={e['id']:e for e in json.loads((ROOT/'content/month-one-v5/calendar.json').read_text())['episodes']}
        for e in episodes(include_intro=False):
            self.assertIsNone(e['voice_reuse_from'])
            self.assertNotEqual(script(e),' '.join(b['narration'] for b in old[e['prior_slot_id']]['beats']))

    def test_citation_pair_preserves_every_other_input(self):
        a=next(e for e in episodes() if e['id']=='BC03');b=next(e for e in episodes(False) if e['id']=='BC03')
        self.assertTrue(a['graphics'].pop('source_cue_visible'));self.assertFalse(b['graphics'].pop('source_cue_visible'))
        self.assertEqual(a,b)

    def test_editorial_examples_do_not_inherit_scientific_authority(self):
        for e in episodes():
            cue=e['graphics']['source_cue'];self.assertTrue(set(cue['source_ids']).issubset(e['evidence_ids']))
            if cue['kind']=='editorial':self.assertEqual(cue['source_ids'],[])
            self.assertEqual(' '.join(c['text'] for c in make_timeline(e)['captions']),script(e))
        for id in ['BC01','BC05','BC08']:
            e=next(e for e in episodes() if e['id']==id)
            self.assertEqual(e['evidence_ids'],[])

    def test_current_brand_and_capacity_remain_explicit(self):
        d,s,p=load();tokens=json.loads(TOKENS.read_text())
        self.assertEqual(tokens['id'],'blueprint-v5');self.assertEqual(tokens['bg'],'#2348C6');self.assertIsNone(tokens['public_name'])
        self.assertEqual(p['weekly_operator_hours_limit'],12)
        self.assertFalse(p['motion_screen']['conducted']);self.assertFalse(p['brand_screen']['conducted'])
        self.assertTrue(all('model' not in e for e in d['episodes']))

if __name__=='__main__':unittest.main()
