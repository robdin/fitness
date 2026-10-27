"""Synthetic evidence only; never writes production measurement records."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/video'))
from evaluate_month_one_v3 import evaluate
from month_one_evidence import TASKS, load_labor_evidence, validate_labor_batches


def read(path):
    return json.loads((ROOT / path).read_text())


class V6MeasurementTests(unittest.TestCase):
    def fixture(self, series='v6'):
        plan = read(f'experiments/month-one-{series}.json')
        content = read(plan['content'])
        rows = []
        for episode in content['episodes'][:12]:
            pub = datetime.fromisoformat(episode['publish_at'])
            rows.append(dict(episode_id=episode['id'], platform='youtube_shorts',
                             published_at=pub.isoformat(), observed_at=(pub + timedelta(days=7)).isoformat(),
                             window_hours=168, reporting_window='first_168_hours', engaged_views=100,
                             stayed_to_watch_pct=65, average_percentage_viewed=75,
                             source_export='SYNTHETIC_TEST_ONLY'))
        ops = dict(comprehension_checks=10, comprehension_passes=8, distinct_useful_responses=5,
                   unresolved_recurring_critical_error=False, simplification_attempted=False,
                   representative_production_batches=[])
        records, verified = {}, {}
        for index in range(2):
            start = datetime.fromisoformat('2026-11-02T09:00:00-05:00') + timedelta(days=7 * index)
            bid = f'SYNTHETIC-W{index + 1}'
            ids = [f'SYNTHETIC-DRAFT-{index}-{i}' for i in range(4)]
            ref = f'measurement/synthetic-week-{index + 1}.jsonl'
            events = []
            for offset, task in enumerate(task for task in TASKS if task != 'corrections'):
                stamp = start + timedelta(hours=offset)
                events.append(dict(event_id=f'{bid}-{task}', batch_id=bid, classification='recurring',
                                   task=task, started_at=stamp.isoformat(),
                                   ended_at=(stamp + timedelta(hours=1)).isoformat(),
                                   active_minutes=60, unattended_minutes=300,
                                   draft_ids=ids if task == 'script' else []))
            body = ''.join(json.dumps(row) + '\n' for row in events).encode()
            digest = hashlib.sha256(body).hexdigest()
            batch = dict(batch_id=bid, week_start=start.date().isoformat(), timezone='America/New_York',
                         completed_drafts=[dict(draft_id=did, change_type='new',
                                                completed_at=(start + timedelta(days=4)).isoformat(),
                                                completion_note='Synthetic completed draft for test only') for did in ids],
                         core_videos_created_or_substantially_reworked=4,
                         source_labor_log=ref, source_labor_sha256=digest, hands_on_hours=9,
                         scope_review={task: {'status': 'logged'} for task in TASKS})
            batch['scope_review']['corrections'] = dict(status='not_needed', reason='Synthetic review needed no correction')
            ops['representative_production_batches'].append(batch)
            records[ref], verified[ref] = events, digest
        return rows, ops, plan, content, records, verified

    def evaluate_fixture(self, fixture):
        rows, ops, plan, content, records, verified = fixture
        return evaluate(rows, ops, plan, content, labor_records=records, verified_labor_sources=verified)

    def test_v6_cli_empty_state(self):
        proc = subprocess.run([sys.executable, str(ROOT / 'tools/video/evaluate_month_one_v3.py'), '--series', 'v6'],
                              cwd=ROOT, capture_output=True, text=True, check=True)
        result = json.loads(proc.stdout)
        self.assertEqual(result['decision'], 'INSUFFICIENT_EVIDENCE')
        self.assertEqual(result['labor_evidence']['verified_representative_weeks'], [])
        self.assertEqual(result['joint_attention_diagnostic']['complete_episodes'], 0)

    def test_valid_two_week_records_pass_and_exclude_unattended_time(self):
        result = self.evaluate_fixture(self.fixture())
        self.assertEqual(result['decision'], 'GO_BOUNDED_MONTH_TWO')
        self.assertEqual([w['hands_on_hours'] for w in result['labor_evidence']['verified_representative_weeks']], [9, 9])

    def test_legacy_aggregate_assertions_do_not_pass_v6(self):
        rows, ops, plan, content, _, _ = self.fixture()
        batch = dict(core_videos_created_or_substantially_reworked=4,
                     source_labor_log='NONEXISTENT_SYNTHETIC_REF', hands_on_hours=12)
        ops['representative_production_batches'] = [batch, copy.deepcopy(batch)]
        result = evaluate(rows, ops, plan, content)
        self.assertEqual(result['decision'], 'INSUFFICIENT_EVIDENCE')
        self.assertFalse(result['gates']['sustainable'])

    def test_unverified_reference_is_insufficient(self):
        rows, ops, plan, content, records, _ = self.fixture()
        result = evaluate(rows, ops, plan, content, labor_records=records)
        self.assertEqual(result['decision'], 'INSUFFICIENT_EVIDENCE')

    def test_duplicate_batch_and_same_week_rejected(self):
        for key in ('batch_id', 'week_start'):
            fixture = self.fixture()
            batches = fixture[1]['representative_production_batches']
            batches[1][key] = batches[0][key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.evaluate_fixture(fixture)

    def test_missing_week_is_insufficient_and_naive_time_rejected(self):
        fixture = self.fixture()
        del fixture[1]['representative_production_batches'][0]['week_start']
        self.assertEqual(self.evaluate_fixture(fixture)['decision'], 'INSUFFICIENT_EVIDENCE')
        fixture = self.fixture()
        fixture[1]['representative_production_batches'][0]['completed_drafts'][0]['completed_at'] = '2026-11-06T09:00:00'
        with self.assertRaises(ValueError):
            self.evaluate_fixture(fixture)

    def test_reusing_draft_ids_in_another_week_rejected(self):
        fixture = self.fixture()
        batches = fixture[1]['representative_production_batches']
        batches[1]['completed_drafts'][0]['draft_id'] = batches[0]['completed_drafts'][0]['draft_id']
        with self.assertRaises(ValueError):
            self.evaluate_fixture(fixture)

    def test_four_unique_completed_drafts_required(self):
        fixture = self.fixture()
        batch = fixture[1]['representative_production_batches'][0]
        batch['completed_drafts'].pop()
        batch['core_videos_created_or_substantially_reworked'] = 3
        self.assertEqual(self.evaluate_fixture(fixture)['decision'], 'INSUFFICIENT_EVIDENCE')
        fixture = self.fixture()
        fixture[1]['representative_production_batches'][0]['completed_drafts'][0]['change_type'] = 'upload_only'
        with self.assertRaises(ValueError):
            self.evaluate_fixture(fixture)

    def test_overlapping_active_intervals_and_duplicate_events_rejected(self):
        for mutation in ('overlap', 'duplicate'):
            fixture = self.fixture()
            events = next(iter(fixture[4].values()))
            if mutation == 'overlap':
                events[1]['started_at'], events[1]['ended_at'] = events[0]['started_at'], events[0]['ended_at']
            else:
                events[1]['event_id'] = events[0]['event_id']
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.evaluate_fixture(fixture)

    def test_claimed_hours_and_active_timer_must_reconcile(self):
        fixture = self.fixture()
        fixture[1]['representative_production_batches'][0]['hands_on_hours'] = 1
        with self.assertRaises(ValueError):
            self.evaluate_fixture(fixture)
        fixture = self.fixture()
        next(iter(fixture[4].values()))[0]['active_minutes'] = 1
        with self.assertRaises(ValueError):
            self.evaluate_fixture(fixture)

    def test_setup_and_out_of_week_work_cannot_prove_recurring_scope(self):
        for mutation in ('setup', 'outside_week'):
            fixture = self.fixture()
            event = next(iter(fixture[4].values()))[0]
            if mutation == 'setup':
                event['classification'] = 'setup'
            else:
                event['started_at'] = '2026-11-01T09:00:00-05:00'
                event['ended_at'] = '2026-11-01T10:00:00-05:00'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.evaluate_fixture(fixture)

    def test_completion_needs_linked_draft_work(self):
        fixture = self.fixture()
        for row in next(iter(fixture[4].values())):
            row['draft_ids'] = []
        result = self.evaluate_fixture(fixture)
        self.assertEqual(result['decision'], 'INSUFFICIENT_EVIDENCE')
        self.assertTrue(any('lack linked production labor' in item for item in result['missing']))

    def test_omitted_operating_work_stays_insufficient(self):
        fixture = self.fixture()
        batch = fixture[1]['representative_production_batches'][0]
        ref = batch['source_labor_log']
        fixture[4][ref] = [r for r in fixture[4][ref] if r['task'] not in ('publishing', 'community', 'measurement', 'supporting_posts')]
        batch['hands_on_hours'] = 5
        result = self.evaluate_fixture(fixture)
        self.assertEqual(result['decision'], 'INSUFFICIENT_EVIDENCE')
        self.assertTrue(any('publishing recurring work not measured' in reason for reason in result['missing']))

    def test_disjoint_attention_is_exposed_without_changing_gate(self):
        fixture = self.fixture()
        for index, row in enumerate(fixture[0]):
            row['stayed_to_watch_pct'], row['average_percentage_viewed'] = (80, 60) if index < 6 else (40, 90)
        result = self.evaluate_fixture(fixture)
        self.assertEqual(result['decision'], 'GO_BOUNDED_MONTH_TWO')
        self.assertEqual(result['joint_attention_diagnostic']['passing_both_count'], 0)
        self.assertEqual(result['joint_attention_diagnostic']['complete_episodes'], 12)

    def test_joint_diagnostic_respects_missing_and_string_metrics(self):
        fixture = self.fixture()
        fixture[0][0]['average_percentage_viewed'] = '  '
        fixture[0][1]['average_percentage_viewed'] = '75'
        result = self.evaluate_fixture(fixture)
        self.assertEqual(result['decision'], 'INSUFFICIENT_EVIDENCE')
        self.assertEqual(result['joint_attention_diagnostic']['complete_episodes'], 11)

    def test_cap_uses_reconciled_hours_and_records_are_not_mutated(self):
        fixture = self.fixture()
        before = copy.deepcopy(fixture)
        self.evaluate_fixture(fixture)
        self.assertEqual(fixture, before)
        fixture[2]['weekly_operator_hours_limit'] = 8
        self.assertEqual(self.evaluate_fixture(fixture)['decision'], 'ITERATE')
        fixture[1]['simplification_attempted'] = True
        self.assertEqual(self.evaluate_fixture(fixture)['decision'], 'NO_GO_CURRENT_FORMAT')

    def test_cli_loader_requires_real_matching_immutable_snapshot(self):
        _, ops, _, _, records, _ = self.fixture()
        batch = ops['representative_production_batches'][0]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / batch['source_labor_log']
            path.parent.mkdir()
            loaded, verified, missing = load_labor_evidence([batch], root)
            self.assertFalse(loaded)
            self.assertTrue(missing)
            path.write_text(''.join(json.dumps(row) + '\n' for row in records[batch['source_labor_log']]))
            loaded, verified, missing = load_labor_evidence([batch], root)
            self.assertEqual(loaded[batch['source_labor_log']], records[batch['source_labor_log']])
            self.assertEqual(verified[batch['source_labor_log']], batch['source_labor_sha256'])
            self.assertFalse(missing)
            with path.open('a') as handle:
                handle.write('\n')
            with self.assertRaises(ValueError):
                load_labor_evidence([batch], root)

    def test_loader_rejects_external_paths(self):
        _, ops, _, _, _, _ = self.fixture()
        batch = ops['representative_production_batches'][0]
        with tempfile.TemporaryDirectory() as directory:
            for ref in ('../outside.jsonl', '/tmp/outside.jsonl', 'measurement/not-jsonl.env'):
                batch['source_labor_log'] = ref
                with self.subTest(ref=ref), self.assertRaises(ValueError):
                    load_labor_evidence([batch], directory)

    def test_v3_and_v5_legacy_behavior_is_preserved(self):
        for series in ('v3', 'v5'):
            rows, ops, plan, content, _, _ = self.fixture(series)
            ops['representative_production_batches'] = [dict(core_videos_created_or_substantially_reworked=4,
                source_labor_log='SYNTHETIC_LEGACY_TEST_ONLY', hands_on_hours=hours) for hours in (11, 12)]
            with self.subTest(series=series):
                self.assertEqual(evaluate(rows, ops, plan, content)['decision'], 'GO_BOUNDED_MONTH_TWO')
                ops['representative_production_batches'] = []
                ops['weekly_operator_hours'] = [1, 1]
                self.assertEqual(evaluate(rows, ops, plan, content)['decision'], 'INSUFFICIENT_EVIDENCE')


if __name__ == '__main__':
    unittest.main()
