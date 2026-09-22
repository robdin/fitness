import hashlib
import hmac
import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from fitness_os.common import OSFailure, fingerprint, rooted, write_json, file_hash
from fitness_os.store import Store
from fitness_os.experiments import analyze, sample_size, wilson, assert_screening_ready
from fitness_os.commerce import verify_event, import_event
from fitness_os.pipeline import check_bundle, approve
from fitness_os.catalog import validate
from fitness_os.metrics import import_csv, observations, FIELDS
from fitness_os.economics import scenario
from fitness_os.captions import validate_srt, binding

ROOT=Path(__file__).resolve().parents[1]


class Controls(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.store=Store(self.root,create=True)

    def tearDown(self):
        self.temp.cleanup()

    def test_parallel_budget_reservations_cannot_overspend(self):
        self.store.budget("openart",100,1)
        def reserve(index):
            try:
                return self.store.reserve("openart",f"asset-{index}",fingerprint(index),60)
            except OSFailure:
                return None
        with ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(reserve,range(16)))
        self.assertEqual(sum(x is not None for x in results),1)
        self.assertEqual(sum(j["reserved_cents"] for j in self.store.jobs()),60)

    def test_duplicate_request_does_not_reserve_twice(self):
        self.store.budget("openart",100,1)
        args=("openart","P01",fingerprint("same"),60)
        first=self.store.reserve(*args)
        second=self.store.reserve(*args)
        self.assertEqual(first["id"],second["id"])
        self.assertEqual(len(self.store.jobs()),1)

    def test_unknown_request_retains_budget_and_concurrency(self):
        self.store.budget("openart",100,1)
        a=self.store.reserve("openart","P01",fingerprint(1),60)
        b=self.store.reserve("openart","P02",fingerprint(2),40)
        self.store.start(a["id"])
        self.store.reconcile(a["id"],"unknown",request_id="provider-123")
        with self.assertRaises(OSFailure):self.store.start(b["id"])
        with self.assertRaises(OSFailure):self.store.reserve("openart","P03",fingerprint(3),1)
        self.store.reconcile(a["id"],"failed",actual_cents=0)
        self.store.start(b["id"])

    def test_actual_cost_overrun_is_preserved_and_blocks_more_work(self):
        self.store.budget("openart",100,1)
        a=self.store.reserve("openart","P01",fingerprint(1),60)
        self.store.start(a["id"])
        self.store.reconcile(a["id"],"succeeded","receipt",130,"asset-location")
        self.assertEqual(self.store.jobs()[0]["actual_cents"],130)
        with self.assertRaises(OSFailure):self.store.reserve("openart","P02",fingerprint(2),1)

    def test_disabled_spending(self):
        with self.assertRaises(OSFailure):self.store.reserve("provider","P01",fingerprint(0),10)

    def protocol(self):
        return {"id":"test","cells":[{"pilot":"P01","variant":"A"},{"pilot":"P01","variant":"B"}]}

    def test_assignment_is_persistent_and_response_unique(self):
        self.store.register_experiment(self.protocol())
        a=self.store.assign("test","subject-1")
        self.assertEqual(a,self.store.assign("test","subject-1"))
        self.store.respond("test","subject-1",3,0,4,4)
        with self.assertRaises(OSFailure):self.store.respond("test","subject-1",0,1,1,1)

    def test_missing_response_is_not_a_zero_score(self):
        self.store.register_experiment(self.protocol())
        self.store.assign("test","subject-1")
        result=analyze(self.store,"test")
        self.assertEqual(sum(x["missing_responses"] for x in result["cells"]),1)
        self.assertTrue(all(x["pass_rate"] is None for x in result["cells"]))
        self.assertIsNone(result["winner"])

    def test_protocol_change_and_closed_experiment_rejected(self):
        self.store.register_experiment(self.protocol())
        changed=self.protocol();changed["new_metric"]="changed"
        with self.assertRaises(OSFailure):self.store.register_experiment(changed)
        self.store.close_experiment("test")
        with self.assertRaises(OSFailure):self.store.assign("test","subject-1")

    def test_followup_window_accepts_existing_viewers_only(self):
        self.store.register_experiment(self.protocol())
        self.store.assign("test","subject-1")
        self.store.stop_enrollment("test")
        with self.assertRaises(OSFailure):self.store.assign("test","subject-2")
        self.store.respond("test","subject-1",2,0,4,3)
        self.store.close_experiment("test")
        with self.assertRaises(OSFailure):self.store.respond("test","subject-1",2,0,4,3)

    def test_current_protocol_must_match_frozen_protocol(self):
        protocol=self.protocol()
        self.store.register_experiment(protocol)
        self.store.assert_protocol(protocol)
        protocol["claim_fingerprint"]="changed"
        with self.assertRaises(OSFailure):self.store.assert_protocol(protocol)

    def test_draft_stimuli_cannot_recruit_participants(self):
        with self.assertRaises(OSFailure):assert_screening_ready(self.root,{"status":"draft_protocol_no_participants"})

    def test_metric_import_preserves_missingness_and_deduplicates(self):
        path=self.root/"synthetic.csv"
        path.write_text(",".join(FIELDS)+"\nP01-time,synthetic-video,2026-09-01,2026-09-07,2026-09-08T12:00:00+00:00,all,10,,,4,24\n")
        self.assertEqual(import_csv(self.root,path)["status"],"imported")
        self.assertEqual(import_csv(self.root,path)["status"],"duplicate")
        self.assertIsNone(observations(self.root)["observations"][0]["impressions"])
        path.write_text(",".join(FIELDS)+"\n")
        with self.assertRaises(OSFailure):import_csv(self.root,path)

    def test_economics_counts_labor_and_refuses_invalid_values(self):
        data=dict(members=100,monthly_price=19,fee_refund_fraction=.06,variable_cost_per_member=4,fixed_monthly_cost=600,founder_hours=40,hourly_value=50)
        result=scenario(data)
        self.assertEqual(result["cash_contribution"],786)
        self.assertEqual(result["after_founder_time"],-1214)
        self.assertEqual(result["labor_inclusive_breakeven_members"],188)
        data["members"]="NaN"
        with self.assertRaises(OSFailure):scenario(data)

    def test_caption_timing_and_audio_binding(self):
        self.assertEqual(validate_srt("1\n00:00:00,000 --> 00:00:01,000\nHello\n", 2),1)
        with self.assertRaises(OSFailure):validate_srt("1\n00:00:00,000 --> 00:00:03,000\nHello\n",2)
        pilot={"beats":[{"id":"hook","narration":"Hello"}],"variants":{"A":["hook"]}}
        self.assertNotEqual(binding(pilot,"A",{"hook":{"sha256":"old"}}),binding(pilot,"A",{"hook":{"sha256":"new"}}))

    def test_lowered_budget_blocks_starting_reserved_work(self):
        self.store.budget("openart",100,1)
        job=self.store.reserve("openart","P01",fingerprint(1),60)
        self.store.budget("openart",50,1)
        with self.assertRaises(OSFailure):self.store.start(job["id"])

    def test_wilson_and_power_sanity(self):
        low,high=wilson(5,10)
        self.assertAlmostEqual(low,0.23659,places=4)
        self.assertAlmostEqual(high,0.76341,places=4)
        self.assertGreater(sample_size(.5,.15,comparisons=3)["per_arm"],sample_size(.5,.15)["per_arm"])
        with self.assertRaises(OSFailure):sample_size(.95,.1)

    def test_signed_event_rejects_tamper_replay_and_bad_scheme(self):
        body=b'{"id":"evt_test","type":"invoice.paid","data":{"object":{}}}'
        sig=hmac.new(b"secret",b"1000."+body,hashlib.sha256).hexdigest()
        self.assertEqual(verify_event(body,f"t=1000,v1={sig}","secret",now=1001)["id"],"evt_test")
        for payload,header,now in [(body+b" ",f"t=1000,v1={sig}",1001),(body,f"t=1000,v1={sig}",2000),(body,f"t=1000,v0={sig}",1001)]:
            with self.assertRaises(OSFailure):verify_event(payload,header,"secret",now=now)

    def test_commerce_deduplicates_without_email_storage(self):
        event={"id":"evt_test","type":"invoice.paid","livemode":False,"data":{"object":{"amount_paid":2900,"currency":"usd","customer":"cus_123","customer_email":"private@example.invalid"}}}
        self.assertEqual(import_event(self.store,event)["status"],"recorded")
        self.assertEqual(import_event(self.store,event)["status"],"duplicate")
        with self.store.connection() as db:
            rows=[dict(x) for x in db.execute("SELECT * FROM commerce")]
        self.assertEqual(len(rows),1)
        self.assertNotIn("private@",json.dumps(rows))

    def test_bundle_tampering_and_stale_inputs_are_rejected(self):
        bundle=self.root/".local/builds/fixture"
        bundle.mkdir(parents=True)
        (bundle/"video.mp4").write_bytes(b"synthetic-test-fixture-not-media")
        manifest={"pilot_id":"P01","variant":"A","mode":"preview","input_hash":fingerprint({"current":1}),"files":{"video.mp4":file_hash(bundle/"video.mp4")}}
        write_json(bundle/"manifest.json",manifest)
        with patch("fitness_os.pipeline.effective_inputs",return_value={"current":1}):
            self.assertEqual(check_bundle(self.root,bundle),manifest)
            (bundle/"video.mp4").write_bytes(b"tampered")
            with self.assertRaises(OSFailure):check_bundle(self.root,bundle)
        with patch("fitness_os.pipeline.effective_inputs",return_value={"current":2}):
            with self.assertRaises(OSFailure):check_bundle(self.root,bundle)

    def test_preview_cannot_be_approved_for_publication(self):
        with patch("fitness_os.pipeline.check_bundle",return_value={"mode":"preview"}):
            with self.assertRaises(OSFailure):approve(self.root,"irrelevant","reviewer",[],"This is a test, not a real approval.")

    def test_path_escape_blocked(self):
        for path in ["../outside",".git/config"]:
            with self.assertRaises(OSFailure):rooted(self.root,path)

    def test_repository_check_is_read_only(self):
        before={str(p.relative_to(ROOT)):file_hash(p) for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and ".local" not in p.parts and "__pycache__" not in p.parts}
        result=validate(ROOT)
        self.assertTrue(result["valid"],result)
        after={str(p.relative_to(ROOT)):file_hash(p) for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and ".local" not in p.parts and "__pycache__" not in p.parts}
        self.assertEqual(before,after)


if __name__=="__main__":
    unittest.main()
