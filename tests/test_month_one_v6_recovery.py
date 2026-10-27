"""Negative cache and isolated recovery checks; no provider or ASR calls."""
import base64
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/video'))
import synthesize_month_one_v6 as synthesis
from month_one_core import digest, script
from voice_contract import input_contract, profile_fingerprint, validate_voice_receipt

MODEL = 's2.1-pro-free'
TAG = '[warm, relaxed]'
SPEED = .85
PROFILE = 'synthetic-profile-not-a-real-identifier'
EPISODE = {'id': 'TEST', 'beats': [['hook', 'A simple test sentence.']]}


def fixture(folder, episode=EPISODE, *, legacy=False):
    folder.mkdir(parents=True, exist_ok=True)
    with wave.open(str(folder / 'narration.wav'), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframes(b'\0\0' * 44100)
    text = script(episode)
    alignment = {'0': {'offset': 0, 'alignment': {'segments': [{'text': text, 'start': 0, 'end': .5}]}}}
    (folder / 'alignment.json').write_text(json.dumps(alignment))
    receipt = dict(status='complete', model=MODEL, delivery_tag=TAG, prosody_speed=SPEED,
                   script_sha256=hashlib.sha256(text.encode()).hexdigest(),
                   request_text_sha256=hashlib.sha256((TAG + ' ' + text).encode()).hexdigest(),
                   audio_sha256=digest(folder / 'narration.wav'), alignment_sha256=digest(folder / 'alignment.json'))
    if not legacy:
        receipt.update(input_contract(text, MODEL, TAG, SPEED, profile_fingerprint(PROFILE)))
    (folder / 'generation.json').write_text(json.dumps(receipt))
    return receipt


class VoiceContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='v6-voice-test-')
        self.root = Path(self.temp.name)
        self.folder = self.root / 'TEST'

    def tearDown(self):
        self.temp.cleanup()

    def test_cache_rejects_changed_model_profile_direction_or_speed_without_network(self):
        fixture(self.folder)
        cases = [('other-model', PROFILE, TAG, SPEED),
                 (MODEL, 'other-profile', TAG, SPEED),
                 (MODEL, PROFILE, '[different direction]', SPEED),
                 (MODEL, PROFILE, TAG, .9)]
        with patch.object(synthesis.urllib.request, 'urlopen', side_effect=AssertionError('Network forbidden')) as network:
            for model, profile, tag, speed in cases:
                with self.subTest(model=model, profile=profile, tag=tag, speed=speed):
                    with self.assertRaises(RuntimeError):
                        synthesis.generate(EPISODE, 'unused', profile, model, self.root, tag, speed)
            synthesis.generate(EPISODE, 'unused', PROFILE, MODEL, self.root, TAG, SPEED)
            network.assert_not_called()

    def test_legacy_receipt_remains_renderable_but_does_not_claim_profile_identity(self):
        before = fixture(self.folder, legacy=True)
        result = validate_voice_receipt(EPISODE, self.folder, expected_model=MODEL,
                                       expected_delivery_tag=TAG, expected_prosody_speed=SPEED)
        self.assertEqual(result['voice_profile_status'], 'legacy_unknown')
        self.assertIsNone(result['voice_input_sha256'])
        self.assertEqual(before, json.loads((self.folder / 'generation.json').read_text()))
        with patch.object(synthesis.urllib.request, 'urlopen', side_effect=AssertionError('Network forbidden')) as network:
            with self.assertRaisesRegex(RuntimeError, 'legacy voice profile is unknown'):
                synthesis.generate(EPISODE, 'unused', PROFILE, MODEL, self.root, TAG, SPEED)
            network.assert_not_called()
        for expected in [dict(expected_model='other'), dict(expected_delivery_tag='other'), dict(expected_prosody_speed=.9)]:
            with self.subTest(expected=expected), self.assertRaises(RuntimeError):
                validate_voice_receipt(EPISODE, self.folder, **expected)

    def test_new_contract_cannot_be_partial_or_have_a_tampered_fingerprint(self):
        original = fixture(self.folder)
        for mode in ['partial', 'changed-profile', 'changed-hash', 'unsupported-version']:
            receipt = dict(original)
            if mode == 'partial': del receipt['voice_input_sha256']
            elif mode == 'changed-profile': receipt['voice_profile_sha256'] = '0' * 64
            elif mode == 'changed-hash': receipt['voice_input_sha256'] = '0' * 64
            else: receipt['voice_contract_version'] = 2
            (self.folder / 'generation.json').write_text(json.dumps(receipt))
            with self.subTest(mode=mode), self.assertRaises(RuntimeError):
                validate_voice_receipt(EPISODE, self.folder)

    def test_artifact_and_alignment_changes_are_rejected_even_with_a_matching_script(self):
        receipt = fixture(self.folder)
        (self.folder / 'narration.wav').write_bytes(b'tampered')
        with self.assertRaisesRegex(RuntimeError, 'audio hash mismatch'):
            validate_voice_receipt(EPISODE, self.folder)
        receipt = fixture(self.folder)
        alignment = json.loads((self.folder / 'alignment.json').read_text())
        alignment['0']['alignment']['segments'][0]['text'] = 'Different text'
        (self.folder / 'alignment.json').write_text(json.dumps(alignment))
        receipt['alignment_sha256'] = digest(self.folder / 'alignment.json')
        (self.folder / 'generation.json').write_text(json.dumps(receipt))
        with self.assertRaisesRegex(RuntimeError, 'alignment does not match'):
            validate_voice_receipt(EPISODE, self.folder)

    def test_a_new_receipt_records_only_profile_fingerprint_and_complete_input_identity(self):
        # One deterministic in-memory provider event, never a network request.
        pcm = io.BytesIO()
        with wave.open(pcm, 'wb') as wav:
            wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(44100)
            wav.writeframes(b'\0\0' * 44100)
        event = {'audio_base64': base64.b64encode(pcm.getvalue()).decode(), 'chunk_seq': 0,
                 'chunk_audio_offset_sec': 0, 'alignment': {'segments': [{'text': script(EPISODE), 'start': 0, 'end': .5}]}}
        response = io.BytesIO(b'data: ' + json.dumps(event).encode() + b'\n')
        response.headers = {'Content-Type': 'text/event-stream'}
        with patch.object(synthesis.urllib.request, 'urlopen', return_value=response):
            synthesis.generate(EPISODE, 'unused-synthetic-key', PROFILE, MODEL, self.root, TAG, SPEED)
        stored = (self.folder / 'generation.json').read_text()
        self.assertNotIn(PROFILE, stored)
        self.assertNotIn('unused-synthetic-key', stored)
        verified = validate_voice_receipt(EPISODE, self.folder, expected_model=MODEL,
                                         expected_delivery_tag=TAG, expected_prosody_speed=SPEED,
                                         expected_profile_fingerprint=profile_fingerprint(PROFILE),
                                         allow_legacy_profile=False)
        self.assertEqual(verified['voice_profile_status'], 'matched_expected')
        self.assertEqual(len(verified['voice_input_sha256']), 64)


class SourceSubsetRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='v6-subset-test-')
        self.root = Path(self.temp.name) / 'fitness'
        # Deliberately omit every legacy calendar and all site packages/models.
        for source in (ROOT / 'tools/video').glob('*.py'):
            dest = self.root / source.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
        for relative in ['tools/brand/check_copy.py', 'content/month-one-v6/calendar.json', 'content/month-one-v6/production.json',
                         'brand/blueprint/tokens.json', 'brand/blueprint/fonts/Fraunces-Italic.ttf',
                         'content/mvp/time-audit/fonts/SpaceGrotesk.ttf']:
            dest = self.root / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, dest)
        data = json.loads((self.root / 'content/month-one-v6/calendar.json').read_text())
        original = data['orientation_asset']
        self.episode = {**original, 'beats': [[b['role'], b['narration']] for b in original['beats']]}
        folder = self.root / '.local/month-one-v6-conversational/voice/BC00'
        receipt = fixture(folder, self.episode, legacy=True)
        voice = json.loads((self.root / 'content/month-one-v6/production.json').read_text())['voice']
        receipt['delivery_tag'] = voice['delivery_tag']; receipt['prosody_speed'] = voice['prosody_speed']
        receipt['request_text_sha256'] = hashlib.sha256((voice['delivery_tag'] + ' ' + script(self.episode)).encode()).hexdigest()
        (folder / 'generation.json').write_text(json.dumps(receipt))

    def tearDown(self):
        self.temp.cleanup()

    def run_check(self, *args):
        return subprocess.run([sys.executable, '-S', 'tools/video/check_month_one_audio.py', '--series', 'v6', *args],
                              cwd=self.root, text=True, capture_output=True)

    def test_v6_input_check_works_without_old_calendar_or_asr_dependencies(self):
        self.assertFalse((self.root / 'content/month-one/episodes.json').exists())
        result = self.run_check('--check-inputs', '--ids', 'BC00')
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['count'], 1)
        self.assertFalse(report['asr_run'])
        self.assertEqual(report['provider_requests'], 0)
        self.assertEqual(report['inputs'][0]['voice_profile_status'], 'legacy_unknown')

    def test_unknown_ids_fail_before_asr_imports_or_input_processing(self):
        result = self.run_check('--ids', 'NOT_AN_EPISODE')
        self.assertEqual(result.returncode, 2)
        self.assertIn('Unknown IDs: NOT_AN_EPISODE', result.stderr)
        self.assertNotIn('numpy', result.stderr)
        self.assertNotIn('faster_whisper', result.stderr)

    def test_restored_subset_enforces_public_copy_rule(self):
        path = self.root / 'content/month-one-v6/calendar.json'
        data = json.loads(path.read_text())
        data['orientation_asset']['beats'][0]['narration'] = 'New here—start here.'
        path.write_text(json.dumps(data))
        result = self.run_check('--check-inputs', '--ids', 'BC00')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('no_em_dash', result.stderr)
        self.assertNotIn('faster_whisper', result.stderr)


if __name__ == '__main__':
    unittest.main()
