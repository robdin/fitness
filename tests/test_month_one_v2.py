"""Content-contract and decision failure paths; all numeric audience rows are synthetic."""
import copy
import sys
import unittest
import tempfile
import zipfile
from html.parser import HTMLParser
from urllib.parse import urlsplit
from datetime import datetime, timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/calendar'))
sys.path.insert(0,str(ROOT/'tools/video'))
from build_month_one_v2 import load, validate, make_ics, generated_files
from month_one_metrics import analyze, descriptive_groups
from package_month_one_v2 import package


class DemandCalendarTests(unittest.TestCase):
    def setUp(self):
        self.data,self.sources,self.plan=load()

    def rows(self):
        return [dict(episode_id=e['id'],platform='youtube_shorts',published_at=e['publish_at'],observed_at=(datetime.fromisoformat(e['publish_at'])+timedelta(hours=168)).isoformat(),window_hours='168',reporting_window='first_168_hours',engaged_views='200',stayed_to_watch_pct='65',average_percentage_viewed='80',source_export='SYNTHETIC_TEST_ONLY') for e in self.data['episodes']]

    def ops(self):
        return dict(comprehension_checks=10,comprehension_passes=8,distinct_useful_responses=5,unresolved_recurring_critical_error=False,weekly_operator_hours=[11,12],simplification_attempted=False)

    def test_schedule_source_links_capacity_and_generated_artifacts_are_current(self):
        report=validate(self.data,self.sources,self.plan)
        self.assertEqual(report['episodes'],16)
        self.assertFalse(report['audience_tests_conducted'])
        for path,content in generated_files(self.data,self.sources,self.plan).items():
            self.assertEqual(path.read_bytes(),content.encode(),str(path))

    def test_broken_sources_and_weekday_confounded_hooks_are_rejected(self):
        bad=copy.deepcopy(self.data)
        bad['episodes'][0]['evidence_ids']=['MISSING_SOURCE']
        with self.assertRaisesRegex(ValueError,'unresolved'):validate(bad,self.sources,self.plan)
        bad=copy.deepcopy(self.data)
        # Two hooks per week and topic alone are insufficient: weekday confounding matters.
        for i,e in enumerate(bad['episodes']):e['hook_type']='Q' if i%2==0 else 'A'
        with self.assertRaisesRegex(ValueError,'weekday'):validate(bad,self.sources,self.plan)

    def test_unbudgeted_work_and_premature_readout_are_rejected(self):
        bad=copy.deepcopy(self.data);bad['weekly_capacity'][0]['hours']=20
        with self.assertRaisesRegex(ValueError,'capacity'):validate(bad,self.sources,self.plan)
        bad=copy.deepcopy(self.data);bad['final_readout_at']='2026-11-30T18:00:00-05:00'
        with self.assertRaisesRegex(ValueError,'last seven-day'):validate(bad,self.sources,self.plan)

    def test_ics_is_folded_unique_utc_and_contains_all_posts(self):
        raw=make_ics(self.data)
        for line in raw.split('\r\n'):
            self.assertLessEqual(len(line.encode()),75)
        unfolded=raw.replace('\r\n ','')
        events=unfolded.split('BEGIN:VEVENT\r\n')[1:]
        self.assertEqual(len(events),34)  # 28 posts + 4 weekly reviews + interim + final
        uids=[]
        for event in events:
            fields=dict(line.split(':',1) for line in event.split('\r\n') if ':' in line)
            uids.append(fields['UID'])
            start=datetime.strptime(fields['DTSTART'],'%Y%m%dT%H%M%SZ')
            end=datetime.strptime(fields['DTEND'],'%Y%m%dT%H%M%SZ')
            self.assertGreater(end,start)
            self.assertEqual(fields['STATUS'],'TENTATIVE')
        self.assertEqual(len(set(uids)),len(uids))
        self.assertIn('DTSTART:20261101T230000Z',unfolded)  # EST after Nov 1 DST change
        self.assertIn('DTSTART:20261205T230000Z',unfolded)

    def test_v2_ids_accept_and_v1_ids_do_not_mix(self):
        self.assertEqual(analyze(self.rows(),self.ops(),self.plan)['decision'],'GO_BOUNDED_MONTH_TWO')
        rows=self.rows();rows[0]['episode_id']='M01'
        with self.assertRaisesRegex(ValueError,'Unknown episode'):analyze(rows,self.ops(),self.plan)

    def test_fixed_reporting_window_required_and_late_lifetime_snapshot_rejected(self):
        rows=self.rows();rows[0].pop('reporting_window')
        with self.assertRaisesRegex(ValueError,'reporting window'):analyze(rows,self.ops(),self.plan)
        rows=self.rows();rows[0]['reporting_window']='lifetime'
        with self.assertRaisesRegex(ValueError,'reporting window'):analyze(rows,self.ops(),self.plan)
        rows=self.rows();rows[0]['observed_at']=(datetime.fromisoformat(rows[0]['published_at'])+timedelta(hours=193)).isoformat()
        with self.assertRaisesRegex(ValueError,'grace'):analyze(rows,self.ops(),self.plan)
        rows[0]['observed_at']=(datetime.fromisoformat(rows[0]['published_at'])+timedelta(hours=180)).isoformat()
        self.assertEqual(analyze(rows,self.ops(),self.plan)['decision'],'GO_BOUNDED_MONTH_TWO')

    def test_empty_or_low_reach_stays_insufficient(self):
        self.assertEqual(analyze([],{},self.plan)['decision'],'INSUFFICIENT_EVIDENCE')
        rows=self.rows()
        for row in rows:row['engaged_views']='20'
        self.assertEqual(analyze(rows,self.ops(),self.plan)['decision'],'INSUFFICIENT_EVIDENCE')

    def test_decision_matrix_and_all_weeks_retained(self):
        rows=self.rows();ops=self.ops()
        for row in rows:row.update(stayed_to_watch_pct='30',average_percentage_viewed='40')
        self.assertEqual(analyze(rows,ops,self.plan)['decision'],'ITERATE')
        ops['distinct_useful_responses']=0
        self.assertEqual(analyze(rows,ops,self.plan)['decision'],'NO_GO_CURRENT_FORMAT')
        ops=self.ops();ops.update(weekly_operator_hours=[10,11,13,14],simplification_attempted=True)
        self.assertEqual(analyze(self.rows(),ops,self.plan)['decision'],'NO_GO_CURRENT_FORMAT')
        ops.update(weekly_operator_hours=[14,13,11,12])
        self.assertEqual(analyze(self.rows(),ops,self.plan)['decision'],'GO_BOUNDED_MONTH_TWO')
        ops['unresolved_recurring_critical_error']=True
        self.assertEqual(analyze(self.rows(),ops,self.plan)['decision'],'ITERATE')

    def test_nonfinite_labor_or_fractional_people_cannot_pass(self):
        for patch in ({'weekly_operator_hours':[8,float('nan')]},{'weekly_operator_hours':[8,float('inf')]},{'comprehension_passes':8.5},{'distinct_useful_responses':True},{'unresolved_recurring_critical_error':'false'}):
            with self.subTest(patch=patch),self.assertRaises(ValueError):
                ops=self.ops();ops.update(patch);analyze(self.rows(),ops,self.plan)

    def test_descriptive_groups_separate_platforms_and_missing_from_zero(self):
        rows=self.rows();rows[0]['platform']='instagram_reels'
        analyze(rows,self.ops(),self.plan)
        result=descriptive_groups(rows,self.data,self.plan)
        self.assertEqual(result['groups']['hook_type']['Q']['mature'],7)
        self.assertEqual(result['groups']['hook_type']['A']['mature'],8)
        empty=descriptive_groups([],self.data,self.plan)
        self.assertIsNone(empty['groups']['hook_type']['Q']['median_stayed_to_watch_pct'])

    def test_portable_archive_includes_only_public_allowlist(self):
        with tempfile.TemporaryDirectory() as directory:
            result=package(Path(directory)/'package')
            with zipfile.ZipFile(result['archive']) as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(len(archive.namelist()),20)
                self.assertIn('content/month-one-v2/calendar.ics',archive.namelist())
                self.assertFalse(any('.local' in name or name.endswith('.env') or 'fish-profile' in name for name in archive.namelist()))
            class Links(HTMLParser):
                links=[]
                def handle_starttag(self,tag,attrs):
                    if tag=='a':self.links.append(dict(attrs).get('href',''))
            review=Path(result['review']);parser=Links();parser.feed(review.read_text())
            for href in parser.links:
                url=urlsplit(href)
                if not url.scheme and url.path:
                    self.assertTrue((review.parent/url.path).resolve().is_file(),href)


if __name__=='__main__':unittest.main()
