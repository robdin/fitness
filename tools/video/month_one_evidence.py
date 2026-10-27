"""Auditable V6 labor evidence; actual records remain caller-owned and read-only."""
import hashlib
import json
import math
import re
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

SCHEMA = 'v6-evidence-v1'
LOCAL_ZONE = ZoneInfo('America/New_York')
TASKS = ('research', 'script', 'claim_review', 'visuals', 'audio_review',
         'corrections', 'supporting_posts', 'publishing', 'community', 'measurement')
HASH = re.compile(r'^[0-9a-f]{64}$')


def uses_v6_evidence(plan):
    return (plan.get('evidence_schema') == SCHEMA
            or str(plan.get('protocol_version', '')).split('.')[0] == '6')


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f'{label} must be finite and nonnegative')
    return value


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} must be a nonempty string')
    if value != value.strip():
        raise ValueError(f'{label} must not have surrounding whitespace')
    return value


def _timestamp(value, label):
    try:
        stamp = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f'{label} must be an ISO timestamp') from None
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError(f'{label} needs a timezone')
    return stamp.astimezone(timezone.utc)


def load_labor_evidence(batches, root):
    """Verify immutable local JSONL snapshots; no arbitrary outside-root reads.

    Missing files are unavailable evidence, not zero hours. Invalid paths, hashes
    and malformed files are errors. Returned values are explicitly injectable in
    evaluate() so pure tests need no fabricated filesystem references.
    """
    records, verified, missing = {}, {}, []
    root = Path(root).resolve()
    if not isinstance(batches, list):
        raise ValueError('Production batches must be a list')
    for batch in batches:
        if not isinstance(batch, dict):
            raise ValueError('Each production batch must be an object')
        ref, expected = batch.get('source_labor_log'), batch.get('source_labor_sha256')
        if not ref or not expected:
            continue  # The schema validator reports missing fields.
        _text(ref, 'source_labor_log')
        if not isinstance(expected, str) or not HASH.fullmatch(expected):
            raise ValueError('source_labor_sha256 must be a lowercase SHA-256')
        relative = Path(ref)
        path = (root / relative).resolve()
        if relative.is_absolute() or not path.is_relative_to(root) or path.suffix != '.jsonl':
            raise ValueError('Labor references must be repository-relative JSONL files inside the repository')
        if ref in verified:
            if verified[ref] != expected:
                raise ValueError('Conflicting hashes for the same labor source')
            continue
        if not path.is_file():
            missing.append(f'Labor snapshot not found: {ref}')
            continue
        body = path.read_bytes()
        actual = hashlib.sha256(body).hexdigest()
        if actual != expected:
            raise ValueError(f'Labor snapshot hash mismatch: {ref}')
        try:
            parsed = [json.loads(line) for line in body.decode('utf-8').splitlines() if line.strip()]
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError(f'Invalid labor JSONL: {ref}') from None
        if any(not isinstance(row, dict) for row in parsed):
            raise ValueError(f'Labor JSONL rows must be objects: {ref}')
        records[ref], verified[ref] = parsed, actual
    return records, verified, missing


def validate_labor_batches(batches, labor_records=None, verified_labor_sources=None):
    """Return reconciled week hours, missing evidence and an audit summary.

    Trust boundary: callers injecting records must also supply hashes verified
    against those immutable source files. CLI callers use load_labor_evidence.
    This validates records, not the honesty or quality of claimed human work.
    """
    if not isinstance(batches, list):
        raise ValueError('Production batches must be a list')
    records = labor_records or {}
    verified = verified_labor_sources or {}
    if not isinstance(records, dict) or not isinstance(verified, dict):
        raise ValueError('Injected labor records and verified sources must be mappings')
    seen_batches, seen_weeks, seen_drafts, seen_events = set(), set(), set(), set()
    intervals, summaries, missing = [], [], []
    for index, batch in enumerate(batches):
        if not isinstance(batch, dict):
            raise ValueError('Each production batch must be an object')
        label = f'Production batch {index + 1}'
        required = ('batch_id', 'week_start', 'timezone', 'completed_drafts',
                    'source_labor_log', 'source_labor_sha256', 'hands_on_hours', 'scope_review')
        absent = [field for field in required if field not in batch or batch[field] is None or batch[field] == '']
        if absent:
            missing.append(f'{label} lacks evidence fields: {", ".join(absent)}')
            continue
        bid = _text(batch['batch_id'], 'batch_id')
        if bid in seen_batches:
            raise ValueError('Duplicate production batch_id')
        seen_batches.add(bid)
        if batch['timezone'] != LOCAL_ZONE.key:
            raise ValueError('Production weeks must use America/New_York')
        try:
            week = date.fromisoformat(batch['week_start'])
        except (TypeError, ValueError):
            raise ValueError('week_start must be an ISO local date') from None
        if week.weekday() != 0:
            raise ValueError('week_start must be a local Monday')
        if week in seen_weeks:
            raise ValueError('Representative production batches require distinct local weeks')
        seen_weeks.add(week)
        lower = datetime.combine(week, time.min, LOCAL_ZONE).astimezone(timezone.utc)
        upper = datetime.combine(week + timedelta(days=7), time.min, LOCAL_ZONE).astimezone(timezone.utc)
        drafts = batch['completed_drafts']
        if not isinstance(drafts, list):
            raise ValueError('completed_drafts must be a list')
        draft_ids = set()
        for draft in drafts:
            if not isinstance(draft, dict):
                raise ValueError('Completed draft entries must be objects')
            did = _text(draft.get('draft_id'), 'draft_id')
            if did in draft_ids or did in seen_drafts:
                raise ValueError('Completed draft IDs must be unique within and across production weeks')
            if draft.get('change_type') not in ('new', 'substantial_revision'):
                raise ValueError('Only new or substantially revised completed drafts qualify')
            completed = _timestamp(draft.get('completed_at'), 'completed_at')
            if not lower <= completed < upper:
                raise ValueError('Draft completion must fall inside its representative local week')
            _text(draft.get('completion_note'), 'completion_note')
            draft_ids.add(did)
        seen_drafts.update(draft_ids)
        if len(draft_ids) < 4:
            missing.append(f'{bid}: fewer than four unique completed core drafts')
        if 'core_videos_created_or_substantially_reworked' in batch:
            count = batch['core_videos_created_or_substantially_reworked']
            if isinstance(count, bool) or not isinstance(count, int) or count != len(draft_ids):
                raise ValueError('Claimed core-video count does not match completed_drafts')
        claimed_hours = _number(batch['hands_on_hours'], 'hands_on_hours')
        ref = _text(batch['source_labor_log'], 'source_labor_log')
        expected = batch['source_labor_sha256']
        if not isinstance(expected, str) or not HASH.fullmatch(expected):
            raise ValueError('source_labor_sha256 must be a lowercase SHA-256')
        if ref not in records or ref not in verified:
            missing.append(f'{bid}: verified labor snapshot unavailable')
            continue
        if verified[ref] != expected:
            raise ValueError('Injected source hash does not match the batch receipt')
        entries = records[ref]
        if not isinstance(entries, list):
            raise ValueError('Labor snapshot must contain a list of rows')
        minutes = 0.0
        task_minutes, worked_drafts = {}, set()
        for row in entries:
            if not isinstance(row, dict):
                raise ValueError('Labor rows must be objects')
            eid = _text(row.get('event_id'), 'event_id')
            if eid in seen_events:
                raise ValueError('Duplicate labor event_id')
            seen_events.add(eid)
            if row.get('batch_id') != bid:
                raise ValueError('Each immutable weekly snapshot must contain only its own batch')
            if row.get('classification') != 'recurring':
                raise ValueError('Representative weekly snapshots contain recurring active work only; keep setup separate')
            task = row.get('task')
            if task not in TASKS:
                raise ValueError(f'Unknown recurring task: {task}')
            start = _timestamp(row.get('started_at'), 'started_at')
            end = _timestamp(row.get('ended_at'), 'ended_at')
            if not lower <= start < end <= upper:
                raise ValueError('Active labor intervals must be positive and inside their local week')
            active = _number(row.get('active_minutes'), 'active_minutes')
            if abs(active - (end - start).total_seconds() / 60) > 1 / 60:
                raise ValueError('Active minutes must reconcile with active timer start/end')
            _number(row.get('unattended_minutes', 0), 'unattended_minutes')
            ids = row.get('draft_ids', [])
            if not isinstance(ids, list) or any(not isinstance(item, str) or not item.strip() or item != item.strip() for item in ids) or len(set(ids)) != len(ids):
                raise ValueError('draft_ids must be unique nonempty strings')
            if task in ('research', 'script', 'claim_review', 'visuals', 'audio_review', 'corrections'):
                worked_drafts.update(ids)
            intervals.append((start, end, eid))
            task_minutes[task] = task_minutes.get(task, 0) + active
            minutes += active
        scope = batch['scope_review']
        if not isinstance(scope, dict):
            raise ValueError('scope_review must be an object')
        batch_missing = []
        for task in TASKS:
            review = scope.get(task)
            if not isinstance(review, dict):
                batch_missing.append(f'{task} scope review missing')
            elif task_minutes.get(task, 0) > 0:
                if review.get('status') != 'logged':
                    raise ValueError(f'{task} has active time but is not marked logged')
            elif task == 'corrections' and review.get('status') == 'not_needed' and isinstance(review.get('reason'), str) and review['reason'].strip():
                pass
            else:
                batch_missing.append(f'{task} recurring work not measured')
        if not draft_ids.issubset(worked_drafts):
            batch_missing.append('completed drafts lack linked production labor rows')
        if abs(claimed_hours - minutes / 60) > 0.0051:
            raise ValueError('hands_on_hours does not reconcile with active labor rows (round to 0.01 hours)')
        if len(draft_ids) < 4:
            batch_missing.append('four completed core drafts required')
        missing.extend(f'{bid}: {reason}' for reason in batch_missing)
        if not batch_missing:
            summaries.append(dict(batch_id=bid, week_start=week.isoformat(),
                                  completed_core_drafts=len(draft_ids),
                                  hands_on_hours=minutes / 60,
                                  active_minutes_by_task=task_minutes,
                                  source_labor_log=ref, source_labor_sha256=expected))
    intervals.sort()
    for previous, current in zip(intervals, intervals[1:]):
        if current[0] < previous[1]:
            raise ValueError('Overlapping active labor intervals cannot be counted twice')
    summaries.sort(key=lambda item: item['week_start'])
    return [item['hands_on_hours'] for item in summaries], missing, summaries
