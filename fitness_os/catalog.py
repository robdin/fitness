from __future__ import annotations
from pathlib import Path
from .common import OSFailure, identifier, read_json, fingerprint, file_hash, rooted


def pilot_paths(root):
    return sorted((Path(root) / "content/pilots").glob("*/pilot.json"))


def load_pilot(root, pilot_id):
    return read_json(rooted(root, f"content/pilots/{identifier(pilot_id)}/pilot.json"))


def load_claims(root):
    claims = read_json(Path(root) / "research/claims.json")
    if len({x["id"] for x in claims}) != len(claims):
        raise OSFailure("Duplicate claim IDs.")
    return {x["id"]: x for x in claims}


def validate(root):
    """Read-only structural check. Does not approve scientific or creative quality."""
    root = Path(root)
    errors, warnings = [], []
    try:
        brand = read_json(root / "config/brand.json")
        identifier(brand["id"])
        claims = load_claims(root)
        sources = read_json(root / "research/sources.json")
        source_ids = {x["id"] for x in sources}
        if len(source_ids) != len(sources):
            errors.append("Duplicate source IDs")
        for claim in claims.values():
            if not claim.get("source_ids") or not set(claim["source_ids"]) <= source_ids:
                errors.append(f"Unresolved sources for {claim['id']}")
        for path in pilot_paths(root):
            pilot = read_json(path)
            identifier(pilot["id"])
            if path.parent.name != pilot["id"] or pilot["brand_id"] != brand["id"]:
                errors.append(f"Identity mismatch in {path}")
            beats = pilot["beats"]
            beat_ids = {b["id"] for b in beats}
            if len(beat_ids) != len(beats) or not beats:
                errors.append(f"Invalid beats in {pilot['id']}")
            for beat in beats:
                identifier(beat["id"])
                if not beat["narration"].strip() or not beat["lines"]:
                    errors.append(f"Empty beat {pilot['id']}/{beat['id']}")
                if not set(beat.get("claim_ids", [])) <= set(claims):
                    errors.append(f"Unknown claims in {pilot['id']}/{beat['id']}")
                if len(beat["lines"]) > 4 or any(len(x) > 100 for x in beat["lines"]):
                    errors.append(f"Excessive screen text in {pilot['id']}/{beat['id']}")
            for variant, order in pilot["variants"].items():
                identifier(variant)
                if set(order) != beat_ids or len(order) != len(beats):
                    errors.append(f"Variant {pilot['id']}/{variant} must use every beat once")
            warnings.append(f"{pilot['id']}: publication needs evidence, audio, rights, and final review")
        rounds = read_json(root / "research/workstreams.json")
        if {x["id"] for x in rounds} != {f"W{i:02}" for i in range(1, 21)}:
            errors.append("Research coverage must explicitly include W01–W20")
        for experiment in (root / "experiments").glob("*.json"):
            data = read_json(experiment)
            if data["type"] == "screening":
                for cell in data["cells"]:
                    p = load_pilot(root, cell["pilot"])
                    if cell["variant"] not in p["variants"]:
                        errors.append(f"Unknown cell in {experiment}")
    except (OSFailure, KeyError, TypeError) as exc:
        errors.append(str(exc))
    return {"valid": not errors, "errors": errors, "warnings": warnings}


def inputs(root, pilot_id, variant, mode):
    root = Path(root)
    pilot = load_pilot(root, pilot_id)
    if variant not in pilot["variants"] or mode not in ("preview", "recorded"):
        raise OSFailure("Unknown variant or render mode")
    claims = load_claims(root)
    relevant = sorted({c for b in pilot["beats"] for c in b.get("claim_ids", [])})
    audio = {}
    caption_record = None
    if mode == "recorded":
        for beat in pilot["beats"]:
            record = read_json(root / f".local/audio/{pilot_id}/{beat['id']}.json")
            path = rooted(root, record["path"])
            if record["script_hash"] != fingerprint(beat["narration"]) or file_hash(path) != record["sha256"]:
                raise OSFailure(f"Stale audio for {pilot_id}/{beat['id']}; review and import the current take.")
            audio[beat["id"]] = record
        caption_path = root/f".local/captions/{pilot_id}/{variant}.json"
        if caption_path.exists():
            from .captions import binding
            caption_record = read_json(caption_path)
            if caption_record["binding_hash"] != binding(pilot, variant, audio) or file_hash(rooted(root, caption_record["path"])) != caption_record["sha256"]:
                raise OSFailure("Caption corrections are stale; review and import current captions")
    tool_versions = {p.name: file_hash(p) for p in sorted((root / "fitness_os").glob("*.py"))}
    return {"pilot": pilot, "brand": read_json(root / "config/brand.json"),
            "claims": [claims[x] for x in relevant], "audio": audio, "caption_override": caption_record,
            "sources": read_json(root / "research/sources.json"),
            "variant": variant, "mode": mode, "tool_versions": tool_versions}
