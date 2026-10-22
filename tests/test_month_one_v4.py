import copy
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

    def test_character_controls_change_only_asset(self):
        variants=[episodes(x) for x in ['M','R','G']]
        for trio in zip(*variants):
            normalized=[]
            for e in trio:
                e=copy.deepcopy(e)
                for field in ['character','character_asset','character_sha256']:e['graphics'].pop(field)
                normalized.append(e)
            self.assertEqual(normalized[0],normalized[1]);self.assertEqual(normalized[1],normalized[2])

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

    def test_asset_manifest_matches_bytes(self):
        m=json.loads((ROOT/'brand/v4/character-manifest.json').read_text())
        self.assertEqual(len(m['assets']),2)
        for a in m['assets']:
            self.assertEqual(a['sha256'],digest(ROOT/a['path']))
            self.assertEqual(a['dimensions'],[1024,1536])
            self.assertGreater(a['transparent_pixels'],0)
            self.assertGreater(a['near_opaque_pixels'],0)

if __name__=='__main__':unittest.main()
