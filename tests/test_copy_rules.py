import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/brand'))
from check_copy import calendar_strings, issues, public_source_title, require_clean


class PublicCopyRules(unittest.TestCase):
    def test_decoded_json_em_dash_is_detected(self):
        text = json.loads('"Busy\\u2014try this."')
        self.assertEqual(issues([('caption', text)])[0]['rule'], 'no_em_dash')

    def test_curly_apostrophe_and_whitespace_do_not_hide_stock_phrase(self):
        self.assertEqual(issues([('bio', 'In today’s\nfast-paced world, train.')])[0]['rule'], 'stock_phrase')

    def test_factual_language_and_urls_are_not_rewritten(self):
        text = "You don't need powder. The best stopping point is uncertain. https://example.com/a—b"
        self.assertFalse(issues([('caption', text)]))

    def test_alternate_hooks_and_story_options_are_checked(self):
        data = json.loads((ROOT/'content/month-one-v6/calendar.json').read_text())
        data['episodes'][0]['alternate_hook_not_scheduled'] = 'New gym—now what?'
        data['supporting_posts'][0]['frames'][0]['options'][0] = 'Unlock your potential'
        paths = [i['path'] for i in issues(calendar_strings(data))]
        self.assertIn('BC01.alternate_hook_not_scheduled', paths)
        self.assertTrue(any('.options[0]' in p for p in paths))

    def test_blocker_raises_before_a_build_can_continue(self):
        with self.assertRaisesRegex(ValueError, 'Public copy needs revision'):
            require_clean([('narration', 'A game-changer for your routine.')])

    def test_source_display_keeps_words_and_original_record(self):
        title = '2023 review — free weights versus machines'
        self.assertEqual(public_source_title(title), '2023 review: free weights versus machines')
        self.assertIn('—', title)


if __name__ == '__main__':
    unittest.main()
