"""Check the active brand's public copy. This is a style lint, not an AI detector."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STOCK_PHRASES = (
    "delve into", "unlock your potential", "elevate your fitness",
    "game-changer", "game changer", "in today's fast-paced world",
    "embark on your fitness journey", "seamlessly integrate",
    "take your fitness to the next level", "leverage the power of",
)


def strings(value, path):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from strings(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from strings(child, f"{path}[{index}]")


def calendar_strings(data):
    for episode in [data["orientation_asset"], *data["episodes"]]:
        prefix = episode["id"]
        for key in ("title", "alternate_hook_not_scheduled", "caption", "cta", "age_scope", "caption_overrides"):
            yield from strings(episode.get(key, ""), f"{prefix}.{key}")
        for index, beat in enumerate(episode["beats"]):
            yield f"{prefix}.beats[{index}].narration", beat["narration"]
    for post in data["supporting_posts"]:
        for key in ("title", "slides", "frames", "caption", "source_note"):
            yield from strings(post.get(key, ""), f"{post['id']}.{key}")


def issues(entries):
    result = []
    for path, text in entries:
        # URLs are identifiers, not prose; never rewrite them to satisfy a style rule.
        prose = re.sub(r"https?://\S+", "", text)
        if "\u2014" in prose:
            result.append({"path": path, "rule": "no_em_dash"})
        normalized = " ".join(prose.lower().replace("\u2019", "'").split())
        for phrase in STOCK_PHRASES:
            if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", normalized):
                result.append({"path": path, "rule": "stock_phrase", "phrase": phrase})
    return result


def require_clean(entries):
    found = issues(entries)
    if found:
        raise ValueError("Public copy needs revision: " + json.dumps(found, ensure_ascii=False))


def public_source_title(title):
    """Use plain punctuation for display; preserve the original research record."""
    return re.sub(r"\s*\u2014\s*", ": ", title)


def active_entries(scope="all"):
    if scope in ("all", "month"):
        data = json.loads((ROOT / "content/month-one-v6/calendar.json").read_text())
        yield from calendar_strings(data)
        production = json.loads((ROOT / "content/month-one-v6/production.json").read_text())
        yield from strings(production["episodes"], "production")
    if scope in ("all", "profiles"):
        copy = json.loads((ROOT / "brand/blueprint/profiles/profile-copy.json").read_text())
        for platform in ("instagram", "youtube", "tiktok"):
            for key in ("name", "bio", "description"):
                yield from strings(copy[platform].get(key, ""), f"profiles.{platform}.{key}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=("all", "month", "profiles"), default="all")
    parser.add_argument("--review-dir", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    entries = list(active_entries(args.scope))
    if args.review_dir:
        files = sorted(args.review_dir.rglob("posting-copy.json"))
        if not files:
            parser.error("No posting-copy.json files found in review directory")
        for path in files:
            yield_name = str(path.relative_to(args.review_dir))
            entries.extend(strings(json.loads(path.read_text()), yield_name))
    found = issues(entries)
    report = {"status": "failed" if found else "passed", "strings_checked": len(entries),
              "issues": found, "scope": args.scope,
              "limitation": "Pattern checks only. Not an AI detector, human-authorship proof or audience test."}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(found))


if __name__ == "__main__":
    main()
