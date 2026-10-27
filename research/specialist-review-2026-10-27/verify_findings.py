"""Reproduce review findings without modifying production, metrics or provider state.

All decision examples below are synthetic and remain in memory. A reported GO
is a demonstration of evaluator behavior, never an actual pilot result.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools/video"))
from evaluate_month_one_v3 import evaluate


def load(relative):
    return json.loads((ROOT / relative).read_text())


def synthetic_rows(plan, mixed=False):
    """Twelve hypothetical mature posts; no audience records are imported."""
    rows = []
    for i, episode_id in enumerate(plan["episode_ids"][:12]):
        stw, apv = ((100, 40) if i < 6 else (20, 100)) if mixed else (70, 80)
        rows.append({
            "episode_id": episode_id, "platform": "youtube_shorts",
            "published_at": "2026-11-01T18:00:00-05:00",
            "observed_at": "2026-11-08T18:00:00-05:00",
            "window_hours": 168, "reporting_window": "first_168_hours",
            "duration_seconds": 24, "views": 250, "engaged_views": 150,
            "stayed_to_watch_pct": stw, "average_percentage_viewed": apv,
            "average_view_duration_seconds": 24 * apv / 100,
            "source_export": "SYNTHETIC_NOT_AN_EXPORT",
        })
    return rows


def main():
    if load('experiments/month-one-v6.json').get('protocol_version') != '6.0':
        print('Historical audit retired after protocol 6.0. verification.json preserves its baseline receipt. Run tests/test_month_one_v6_* for current regression checks.')
        return
    calendar = load("content/month-one-v6/calendar.json")
    production = load("content/month-one-v6/production.json")
    plan = load("experiments/month-one-v6.json")
    actual_ops = load("measurement/month-one-v6-operations.json")
    actual_rows = load("measurement/month-one-v6-observations.json")
    untouched = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for pattern in ["content/month-one-v6/*", "measurement/month-one-v6*",
                        "experiments/month-one-v6.json"]
        for p in ROOT.glob(pattern) if p.is_file()
    }
    generic = "Optional discussion: What would make this easier in your own week?"
    caption_count = sum(e["cta"] == generic for e in calendar["episodes"])
    assert caption_count == 13
    assert len(production["episodes"]) == 17
    assert all("example_card" in e for e in production["episodes"].values())

    command = [sys.executable, "tools/video/evaluate_month_one_v3.py", "--series", "v6"]
    cli = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert cli.returncode == 2 and "invalid choice" in cli.stderr
    actual = evaluate(actual_rows, actual_ops, plan, calendar)
    assert actual["decision"] == "INSUFFICIENT_EVIDENCE"

    batch = {"core_videos_created_or_substantially_reworked": 4,
             "source_labor_log": "SYNTHETIC_NONEXISTENT_LOG", "hands_on_hours": 10}
    ops = {"comprehension_checks": 10, "comprehension_passes": 8,
           "distinct_useful_responses": 5,
           "unresolved_recurring_critical_error": False,
           "simplification_attempted": False,
           "representative_production_batches": [copy.deepcopy(batch), copy.deepcopy(batch)]}
    duplicate = evaluate(synthetic_rows(plan), ops, plan, calendar)
    assert duplicate["decision"] == "GO_BOUNDED_MONTH_TWO"

    # Separate-median rule is implemented as written; this is a diagnostic limit.
    ops["representative_production_batches"][0]["week"] = "synthetic-week-A"
    ops["representative_production_batches"][1]["week"] = "synthetic-week-B"
    mixed_rows = synthetic_rows(plan, mixed=True)
    mixed = evaluate(mixed_rows, ops, plan, calendar)
    jointly_passing = sum(r["stayed_to_watch_pct"] >= 60 and
                         r["average_percentage_viewed"] >= 70 for r in mixed_rows)
    assert mixed["decision"] == "GO_BOUNDED_MONTH_TWO" and jointly_passing == 0

    archive = ROOT.parent / "fitness-deliverables/month-one-v6-conversational/Conversational_Blueprint_Month_Sources.zip"
    archive_evidence = {"available": archive.is_file()}
    if archive.is_file():
        with zipfile.ZipFile(archive) as z:
            names = set(z.namelist())
        archive_evidence.update(
            sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
            audio_checker_present="fitness/tools/video/check_month_one_audio.py" in names,
            legacy_episodes_present="fitness/content/month-one/episodes.json" in names,
        )
        assert archive_evidence["audio_checker_present"]
        assert not archive_evidence["legacy_episodes_present"]

    for relative, digest in untouched.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
    names = ["CONTENT_CREATION.md", "MONETIZATION.md", "ENGAGEMENT.md",
             "DIGITAL_MARKETING.md", "EXPERIMENTATION.md", "PRODUCTION.md"]
    reports = {name: (HERE / name).is_file() for name in names}
    assert all(reports.values()), "A specialist report is still missing"
    result = {
        "review_date": "2026-10-27",
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "scope": "Reproduced repository findings, not an audience or production-cost experiment",
        "specialist_reports_present": reports,
        "generic_core_caption_prompts": caption_count,
        "core_caption_prompts_with_editorial_prefix": sum(e["cta"].startswith("Optional discussion:") for e in calendar["episodes"]),
        "episodes_with_example_cards": 17,
        "v6_cli": {"returncode": cli.returncode, "supports_v6": False,
                   "callable_evaluator_supports_v6": True},
        "actual_current_pilot_decision": actual["decision"],
        "synthetic_duplicate_undated_batches": {
            "decision": duplicate["decision"], "finding": "Distinct production weeks and labor evidence are not enforced"},
        "synthetic_split_attention_metrics": {
            "decision": mixed["decision"], "median_stayed_to_watch_pct": mixed["median_stayed_to_watch_pct"],
            "median_average_percentage_viewed": mixed["median_average_percentage_viewed"],
            "episodes_meeting_both": jointly_passing,
            "finding": "Matches the written separate-median rule; add a descriptive joint-performance check"},
        "source_archive": archive_evidence,
        "canonical_and_actual_measurement_files_unchanged": True,
        "audience_effects_validated": False,
        "provider_requests": 0,
        "synthetic_data_written_to_measurement": False,
    }
    (HERE / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
