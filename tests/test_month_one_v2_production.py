import hashlib
import json
import sys
import unittest
import tempfile
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/video'))
from produce_month_one_v2 import episodes, WORKSPACE
from month_one_core import script, normalized, make_timeline, caption_chunks, digest
import package_month_one_v2_media as media

class ProductionTests(unittest.TestCase):
    def test_short_tail_captions_are_balanced_without_changing_words(self):
        speech='Research includes useful results from twice-weekly resistance training.'
        chunks=caption_chunks(speech,balanced=True)
        self.assertEqual(' '.join(c['text'] for c in chunks),speech)
        self.assertTrue(all(len(c['text'].split())>=2 and len(c['text'])>=20 for c in chunks))
        self.assertTrue(all(len(c['text'])<=62 and len(c['lines'])<=2 for c in chunks))
        self.assertEqual(caption_chunks(speech)[-1]['text'],'training.')

    def test_packaging_rejects_changed_graphics_and_mutated_video(self):
        ep=episodes()[0]
        with tempfile.TemporaryDirectory() as directory,patch.object(media,'REVIEW',Path(directory)):
            folder=Path(directory)/ep['id'];folder.mkdir()
            timeline={'episode':ep,'script_sha256':hashlib.sha256(script(ep).encode()).hexdigest()}
            target=folder/'N01-motion.mp4';target.write_bytes(b'original')
            timeline_path=folder/'timeline.json';timeline_path.write_text(json.dumps(timeline))
            receipt={'script_sha256':timeline['script_sha256'],'sha256':digest(target),'timeline_sha256':digest(timeline_path),'renderer_sha256':digest(media.RENDERER)}
            (folder/'verification-motion.json').write_text(json.dumps(receipt))
            changed=json.loads(json.dumps(ep));changed['graphics']['headlines'][0]=['DIFFERENT','CLAIM']
            with self.assertRaisesRegex(ValueError,'stale script or graphic'):media.verify_export(changed,'motion')
            target.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'stale media'):media.verify_export(ep,'motion')

    def test_production_preserves_all_source_scripts_and_hook_assignments(self):
        canonical=json.loads((ROOT/'content/month-one-v2/calendar.json').read_text())['episodes']
        self.assertEqual(len(episodes()),16)
        for original,adapted in zip(canonical,episodes()):
            self.assertEqual(script(adapted),' '.join(b['narration'] for b in original['beats']))
            self.assertEqual(adapted['original_brief'],original['beats'])
            self.assertEqual(adapted['hook_type'],original['hook_type'])
            self.assertEqual(adapted['canonical_sha256'],hashlib.sha256(json.dumps(original,sort_keys=True).encode()).hexdigest())
            tl=make_timeline(adapted)
            self.assertEqual(normalized(script(adapted)),normalized(' '.join(c['text'] for c in tl['captions'])))
            self.assertEqual(tl['timing'],'estimated_visual_draft')
            self.assertEqual(len(adapted['graphics']['headlines']),6)
        self.assertEqual(WORKSPACE,ROOT/'.local/month-one-v2')

if __name__=='__main__':unittest.main()
