import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/video'))
from produce_month_one_v3 import episodes as v3
from produce_month_one_v4 import episodes, CONFIG, digest
from month_one_core import script

class ProductionV4Tests(unittest.TestCase):
    def test_scripts_and_schedule_preserved(self):
        for a,b in zip(v3(),episodes()):
            self.assertEqual(script(a),script(b))
            self.assertEqual(a['canonical_sha256'],b['canonical_sha256'])
            self.assertEqual(a['publish_at'],b['publish_at'])
            self.assertEqual(b['graphics']['production_sha256'],digest(CONFIG))

    def test_production_has_no_character_dependency(self):
        for e in episodes():
            self.assertEqual(e['visual'],'v4.1-graphics')
            self.assertEqual(e['graphics']['layout'],'full-width-graphics')
            self.assertFalse(any('character' in key for key in e['graphics']))

    def test_citation_control_changes_only_cue_visibility(self):
        for a,b in zip(episodes(),episodes(citation=False)):
            self.assertTrue(a['graphics'].pop('source_cue_visible'))
            self.assertFalse(b['graphics'].pop('source_cue_visible'))
            self.assertEqual(a,b)

    def test_source_cues_are_bounded_and_resolve(self):
        for e in episodes():
            cue=e['graphics']['source_cue']
            self.assertTrue(cue['label'])
            self.assertLessEqual(len(cue['label']),60)
            self.assertTrue(set(cue['source_ids']).issubset(e['evidence_ids']))
            if cue['kind']=='editorial':self.assertEqual(cue['source_ids'],[])
        self.assertEqual(episodes()[2]['graphics']['source_cue']['source_ids'],['E16'])

if __name__=='__main__':unittest.main()
