import json
import math
from statistics import NormalDist, mean
from pathlib import Path
from datetime import datetime, timezone
from .common import OSFailure, read_json, fingerprint, identifier, rooted, file_hash
from .catalog import load_pilot


def current_protocol(root, experiment_id):
    root = Path(root)
    protocol = read_json(root/f"experiments/{identifier(experiment_id)}.json")
    if protocol["id"] != experiment_id or protocol["type"] != "screening":
        raise OSFailure("Use a matching screening protocol; native YouTube tests stay in Studio")
    protocol["content_fingerprints"] = {cell["pilot"]: fingerprint(load_pilot(root, cell["pilot"])) for cell in protocol["cells"]}
    protocol["claim_fingerprint"] = fingerprint(read_json(root/"research/claims.json"))
    protocol["brand_fingerprint"] = fingerprint(read_json(root/"config/brand.json"))
    protocol["instrument_fingerprint"] = fingerprint(read_json(root/protocol["instrument"]))
    protocol["stimulus_fingerprints"] = {s["path"]: file_hash(rooted(root, s["path"])/"manifest.json") for s in protocol.get("activation", {}).get("stimuli", [])}
    return protocol


def assert_screening_ready(root, protocol):
    from .pipeline import check_bundle
    activation = protocol.get("activation", {})
    if protocol.get("status") != "ready_for_recruitment" or not activation.get("reviewer") or len(activation.get("review_note", "")) < 20:
        raise OSFailure("Finish the stimulus, instrument and consent review before participant assignment")
    try:
        started = datetime.fromisoformat(protocol["recruitment_started_at"])
        if started.tzinfo is None or started > datetime.now(timezone.utc):
            raise ValueError("Recruitment clock must be a past timezone-aware time")
    except (KeyError, TypeError, ValueError) as exc:
        raise OSFailure("Record the actual recruitment start time with timezone") from exc
    expected = {(c["pilot"], c["variant"]) for c in protocol["cells"]}
    seen = set()
    for stimulus in activation.get("stimuli", []):
        bundle = rooted(root, stimulus["path"])
        manifest = check_bundle(root, bundle)
        cell = (manifest["pilot_id"], manifest["variant"])
        if manifest["mode"] != "recorded" or cell in seen or cell not in expected:
            raise OSFailure("Review exactly one current narrated stimulus for every screening cell")
        if any(c.get("review_status") != "approved" or not c.get("reviewer") for c in read_json(bundle/"inputs.json")["claims"]):
            raise OSFailure("Screening stimuli still contain unreviewed claims")
        seen.add(cell)
    if seen != expected:
        raise OSFailure("Every screening cell needs a retained, reviewed narrated stimulus")


def sample_size(baseline, absolute_lift, power=0.8, alpha=0.05, comparisons=1):
    if not 0 < baseline < 1 or not 0 < baseline + absolute_lift < 1 or absolute_lift <= 0 or comparisons < 1 or not 0 < alpha < 1 or not 0.5 < power < 1:
        raise OSFailure("Invalid power-analysis inputs")
    other = baseline + absolute_lift
    pooled = (baseline + other) / 2
    z = NormalDist().inv_cdf(1 - alpha / comparisons / 2)
    zp = NormalDist().inv_cdf(power)
    n = math.ceil((z * math.sqrt(2 * pooled * (1-pooled)) + zp * math.sqrt(baseline*(1-baseline)+other*(1-other)))**2 / absolute_lift**2)
    return {"per_arm": n, "total_per_comparison": 2*n, "comparisons": comparisons,
            "family_alpha": alpha, "power": power, "baseline": baseline, "absolute_lift": absolute_lift,
            "method": "Approximate independent two-proportion fixed-horizon design; Bonferroni-adjusted alpha",
            "limitations": "Assumes independent observations and valid instrument. Add attrition; not a YouTube traffic forecast."}


def wilson(successes, count):
    if not count:
        return None
    p, z = successes / count, 1.95996398454
    denominator = 1 + z*z/count
    middle = (p+z*z/(2*count))/denominator
    half = z*math.sqrt((p*(1-p)+z*z/(4*count))/count)/denominator
    return [max(0, middle-half), min(1, middle+half)]


def analyze(store, experiment_id):
    with store.connection() as db:
        exp = db.execute("SELECT * FROM experiments WHERE id=?", (experiment_id,)).fetchone()
        if not exp:
            raise OSFailure("Experiment not registered")
        protocol = json.loads(exp["protocol"])
        rows = db.execute("SELECT a.cell,r.correct,r.critical_error,r.trust,r.useful FROM assignments a LEFT JOIN responses r USING(experiment_id,participant_id) WHERE a.experiment_id=?", (experiment_id,)).fetchall()
    cells = []
    for cell in protocol["cells"]:
        assigned = [r for r in rows if json.loads(r["cell"]) == cell]
        observed = [r for r in assigned if r["correct"] is not None]
        passed = sum(r["correct"] >= 2 and not r["critical_error"] for r in observed)
        cells.append({**cell, "assigned": len(assigned), "responses": len(observed),
                      "missing_responses": len(assigned)-len(observed), "passed": passed,
                      "pass_rate": passed/len(observed) if observed else None,
                      "wilson_95_descriptive": wilson(passed, len(observed)),
                      "critical_errors": sum(r["critical_error"] for r in observed),
                      "mean_trust": mean(r["trust"] for r in observed) if observed else None,
                      "mean_usefulness": mean(r["useful"] for r in observed) if observed else None})
    # A ratio check is a diagnostic, never a treatment effect test.
    total = len(rows)
    expected = total/len(cells) if total else 0
    ratio_chi2 = sum((c["assigned"]-expected)**2/expected for c in cells) if expected else None
    return {"experiment": experiment_id, "state": exp["state"], "cells": cells,
            "sample_ratio_chi2_descriptive": ratio_chi2,
            "sample_ratio_note": "Compare assignment counts with equal allocation. Small samples often vary; investigate instrumentation before effect analysis.",
            "decision": "no_data" if not total else "exploratory_only",
            "winner": None,
            "limitations": "No automatic winner. Check missingness, comprehension errors, recruitment, fixed horizon, and uncertainty; do not pool topic differences as randomized format effects."}
