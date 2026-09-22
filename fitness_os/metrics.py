"""Import explicitly mapped, aggregate Studio exports. Never invent unavailable metrics."""
import csv
import io
from datetime import date, datetime
from pathlib import Path
from .common import OSFailure, read_json, write_json, atomic_write, file_hash, identifier, utcnow

FIELDS = ["content_id", "video_id", "period_start", "period_end", "exported_at", "traffic_source",
          "views", "impressions", "impressions_ctr_pct", "watch_minutes", "avg_view_duration_seconds"]
NUMBERS = FIELDS[6:]


def import_csv(root, path):
    source = Path(path)
    raw = source.read_bytes()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if reader.fieldnames != FIELDS:
        raise OSFailure("Map aggregate Studio data to the exact measurement template columns first")
    rows, keys = [], set()
    for row in reader:
        identifier(row["content_id"])
        if not row["video_id"] or not row["traffic_source"]:
            raise OSFailure("Video identity and traffic source are required")
        try:
            start, end = date.fromisoformat(row["period_start"]), date.fromisoformat(row["period_end"])
            exported = datetime.fromisoformat(row["exported_at"])
            if start > end or exported.tzinfo is None:
                raise ValueError("Invalid period or missing export timezone")
            for field in NUMBERS:
                row[field] = float(row[field]) if row[field].strip() else None
                value = row[field]
                if value is not None and (not 0 <= value < float("inf") or (field == "impressions_ctr_pct" and value > 100)):
                    raise ValueError("Invalid metric value")
                if field in ("views", "impressions") and value is not None and not value.is_integer():
                    raise ValueError("Counts must be integers")
        except (ValueError, TypeError, AttributeError) as exc:
            raise OSFailure(f"Invalid metric row: {exc}") from exc
        key = tuple(row[f] for f in FIELDS[:6])
        if key in keys:
            raise OSFailure("Duplicate observation grain within an import")
        keys.add(key); rows.append(row)
    if not rows:
        raise OSFailure("No observations in file; empty template is not audience data")
    digest = file_hash(source)
    dest = Path(root)/f".local/metrics/{digest}"
    if (dest/"receipt.json").exists():
        if file_hash(dest/"mapped.csv") != digest:
            raise OSFailure("Previously imported source changed")
        return {"status": "duplicate", "sha256": digest}
    atomic_write(dest/"mapped.csv", raw)
    write_json(dest/"receipt.json", {"sha256": digest, "imported_at": utcnow(), "source": "operator-mapped YouTube Studio export", "rows": rows})
    return {"status": "imported", "sha256": digest, "rows": len(rows)}


def observations(root):
    receipts = [read_json(p) for p in sorted((Path(root)/".local/metrics").glob("*/receipt.json"))]
    return {"imports": len(receipts), "observations": [row for receipt in receipts for row in receipt["rows"]],
            "status": "no_data" if not receipts else "raw_observations",
            "note": "Snapshots and traffic-source slices may overlap. Do not sum across imports or average CTR without its eligible-impression denominator."}
