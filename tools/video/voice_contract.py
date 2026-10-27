"""Standard-library verification of retained speech and nonsecret input identity.

Legacy receipts can verify their recorded model/delivery and exact artifacts,
but cannot establish a historical voice profile that was never recorded.
"""
import hashlib
import json
import math
import re
import wave
from pathlib import Path
from month_one_core import alignment_words, digest, normalized, script

CONTRACT_VERSION = 1
_HEX = re.compile(r"[0-9a-f]{64}\Z")


def profile_fingerprint(profile):
    """An opaque, domain-separated identity; never persist the raw profile ID."""
    if not isinstance(profile, str) or not profile.strip():
        raise ValueError('A nonempty voice profile is required')
    return hashlib.sha256(b'fish-voice-profile-v1\0' + profile.encode()).hexdigest()


def input_contract(text, model, delivery_tag, prosody_speed, profile_sha256):
    if not isinstance(model, str) or not model:
        raise ValueError('A synthesis model is required')
    if not isinstance(delivery_tag, str):
        raise ValueError('Delivery direction must be text')
    if isinstance(prosody_speed, bool) or not isinstance(prosody_speed, (int, float)) or not math.isfinite(prosody_speed) or prosody_speed <= 0:
        raise ValueError('Synthesis speed must be positive and finite')
    if not isinstance(profile_sha256, str) or not _HEX.fullmatch(profile_sha256):
        raise ValueError('Invalid voice profile fingerprint')
    fields = dict(voice_contract_version=CONTRACT_VERSION,
                  script_sha256=hashlib.sha256(text.encode()).hexdigest(),
                  model=model, delivery_tag=delivery_tag,
                  prosody_speed=float(prosody_speed),
                  voice_profile_sha256=profile_sha256)
    identity = hashlib.sha256(json.dumps(fields, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {**fields, 'voice_input_sha256': identity}


def validate_voice_receipt(episode, voice_folder, *, expected_model=None,
                           expected_delivery_tag=None, expected_prosody_speed=None,
                           expected_profile_fingerprint=None, allow_legacy_profile=True):
    """Verify local inputs without provider, profile-file or ASR access.

    An expected profile requires a recorded matching fingerprint. Callers that
    retain legacy audio must leave expected_profile_fingerprint unset and keep
    the returned legacy_unknown status explicit; this never upgrades a receipt.
    """
    folder = Path(voice_folder)
    receipt = json.loads((folder / 'generation.json').read_text())
    text = script(episode)
    script_sha = hashlib.sha256(text.encode()).hexdigest()
    prefix = str(episode['id']) + ': '

    def require(condition, message):
        if not condition:
            raise RuntimeError(prefix + message)

    require(receipt.get('status') == 'complete', 'narration receipt is not complete; reconcile before retry')
    require(receipt.get('script_sha256') == script_sha, 'narration script mismatch')
    for name, expected in [('model', expected_model), ('delivery_tag', expected_delivery_tag), ('prosody_speed', expected_prosody_speed)]:
        if expected is not None:
            require(receipt.get(name) == expected, name + ' does not match expected narration settings')
    request_sha = hashlib.sha256(((receipt.get('delivery_tag', '') + ' ' + text).strip()).encode()).hexdigest()
    if 'request_text_sha256' in receipt:
        require(receipt['request_text_sha256'] == request_sha, 'request text identity mismatch')

    contract_keys = ('voice_contract_version', 'voice_profile_sha256', 'voice_input_sha256')
    if any(k in receipt for k in contract_keys):
        require(all(k in receipt for k in contract_keys), 'incomplete narration input contract')
        require(receipt['voice_contract_version'] == CONTRACT_VERSION, 'unsupported narration input contract')
        try:
            contract = input_contract(text, receipt['model'], receipt['delivery_tag'], receipt['prosody_speed'], receipt['voice_profile_sha256'])
        except (KeyError, ValueError, TypeError):
            raise RuntimeError(prefix + 'invalid narration input contract') from None
        require(receipt['voice_input_sha256'] == contract['voice_input_sha256'], 'narration input identity mismatch')
        if expected_profile_fingerprint is not None:
            require(receipt['voice_profile_sha256'] == expected_profile_fingerprint, 'voice profile identity mismatch')
        profile_status = 'matched_expected' if expected_profile_fingerprint is not None else 'fingerprinted_not_independently_matched'
    else:
        require(allow_legacy_profile and expected_profile_fingerprint is None,
                'legacy voice profile is unknown; retain for rendering or reconcile before synthesis reuse')
        contract = None
        profile_status = 'legacy_unknown'

    audio = folder / 'narration.wav'
    alignment_path = folder / 'alignment.json'
    require(audio.is_file() and alignment_path.is_file(), 'complete receipt has missing artifacts; restore them')
    audio_sha, alignment_sha = digest(audio), digest(alignment_path)
    require(receipt.get('audio_sha256') == audio_sha, 'retained audio hash mismatch')
    require(receipt.get('alignment_sha256') == alignment_sha, 'retained alignment hash mismatch')
    with wave.open(str(audio), 'rb') as reader:
        rate, channels, width, frames = reader.getframerate(), reader.getnchannels(), reader.getsampwidth(), reader.getnframes()
        pcm_bytes = 0
        while block := reader.readframes(65536):
            pcm_bytes += len(block)
    require(frames > 0 and rate > 0 and pcm_bytes == frames * channels * width, 'invalid or truncated narration WAV')
    duration = frames / rate
    words = alignment_words(json.loads(alignment_path.read_text()), lead=0)
    require(bool(words), 'empty narration alignment')
    require(''.join(normalized(w['text']) for w in words) == normalized(text), 'alignment does not match narration script')
    require(all(math.isfinite(w['start']) and math.isfinite(w['end']) and 0 <= w['start'] <= w['end'] <= duration + .05 for w in words),
            'alignment exceeds decoded narration bounds')
    return dict(script_sha256=script_sha, audio_sha256=audio_sha, alignment_sha256=alignment_sha,
                voice_input_sha256=contract['voice_input_sha256'] if contract else None,
                voice_profile_status=profile_status, duration_seconds=duration,
                model=receipt.get('model'), delivery_tag=receipt.get('delivery_tag'), prosody_speed=receipt.get('prosody_speed'))
