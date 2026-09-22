"""Export bounded context for a chosen AI assistant; never calls a model itself."""
from pathlib import Path
from .common import OSFailure, read_json, fingerprint
from .catalog import load_pilot, load_claims

ROLES = ("research", "draft", "evidence_review", "production", "analyst", "support")


def packet(root, pilot_id, role):
    if role not in ROLES:
        raise OSFailure("Unknown task role")
    root = Path(root)
    pilot = load_pilot(root, pilot_id)
    all_claims = load_claims(root)
    claims = [all_claims[c] for c in sorted({c for b in pilot["beats"] for c in b.get("claim_ids", [])})]
    sources = {s for c in claims for s in c["source_ids"]}
    context = {"pilot":pilot,"brand":read_json(root/"config/brand.json"),"claims":claims,
               "sources":[s for s in read_json(root/"research/sources.json") if s["id"] in sources],
               "instructions":(root/f"prompts/{role}.md").read_text()}
    return {"role":role,"input_hash":fingerprint(context),"context":context,
            "handoff":"Return a proposed artifact plus unresolved issues. Operator reviews and applies the diff against current inputs.",
            "execution":"No model request submitted. This packet is context for the selected assistant.",
            "permissions":{"spend":False,"publish":False,"contact_people":False,"approve_claims":False,"write_runtime_state":False}}
