from __future__ import annotations
import json
import secrets
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from .common import OSFailure, canonical, fingerprint, utcnow, identifier

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS budgets(provider TEXT PRIMARY KEY, ceiling_cents INTEGER NOT NULL CHECK(ceiling_cents>=0), concurrency INTEGER NOT NULL CHECK(concurrency>0));
CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, provider TEXT NOT NULL, content_id TEXT NOT NULL, input_hash TEXT NOT NULL, status TEXT NOT NULL, reserved_cents INTEGER NOT NULL, actual_cents INTEGER NOT NULL DEFAULT 0, request_id TEXT, result TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, UNIQUE(provider,content_id,input_hash));
CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY, at TEXT NOT NULL, action TEXT NOT NULL, payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS experiments(id TEXT PRIMARY KEY, protocol_hash TEXT NOT NULL, protocol TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'open');
CREATE TABLE IF NOT EXISTS assignments(experiment_id TEXT NOT NULL, participant_id TEXT NOT NULL, cell TEXT NOT NULL, created_at TEXT NOT NULL, PRIMARY KEY(experiment_id,participant_id));
CREATE TABLE IF NOT EXISTS responses(experiment_id TEXT NOT NULL, participant_id TEXT NOT NULL, correct INTEGER NOT NULL, critical_error INTEGER NOT NULL, trust INTEGER NOT NULL, useful INTEGER NOT NULL, created_at TEXT NOT NULL, PRIMARY KEY(experiment_id,participant_id));
CREATE TABLE IF NOT EXISTS commerce(event_id TEXT PRIMARY KEY, at TEXT NOT NULL, kind TEXT NOT NULL, customer_ref TEXT, content_id TEXT, amount_cents INTEGER, currency TEXT, test_mode INTEGER NOT NULL);
"""


class Store:
    def __init__(self, root, create=False):
        self.path = Path(root) / ".local/state.sqlite3"
        if create:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.connection() as db:
                db.executescript(SCHEMA)
                db.execute("INSERT OR IGNORE INTO settings VALUES ('assignment_salt',?)", (secrets.token_hex(32),))
        elif not self.path.exists():
            raise OSFailure("State has not been initialized. Run: python -m fitness_os init")

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.row_factory = sqlite3.Row
        try:
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def event(self, db, action, payload):
        db.execute("INSERT INTO audit(at,action,payload) VALUES (?,?,?)", (utcnow(), action, json.dumps(payload, sort_keys=True)))

    def budget(self, provider, ceiling_cents, concurrency):
        identifier(provider)
        if ceiling_cents < 0 or concurrency < 1:
            raise OSFailure("Invalid budget or concurrency")
        with self.connection() as db:
            db.execute("INSERT INTO budgets VALUES (?,?,?) ON CONFLICT(provider) DO UPDATE SET ceiling_cents=excluded.ceiling_cents,concurrency=excluded.concurrency", (provider, ceiling_cents, concurrency))
            self.event(db, "budget_configured", {"provider": provider, "ceiling_cents": ceiling_cents, "concurrency": concurrency})

    def reserve(self, provider, content_id, input_hash, estimated_cents):
        identifier(provider); identifier(content_id)
        if len(input_hash) != 64 or any(c not in "0123456789abcdef" for c in input_hash) or estimated_cents <= 0:
            raise OSFailure("Require a SHA-256 fingerprint and a positive cost reservation")
        with self.connection() as db:
            old = db.execute("SELECT * FROM jobs WHERE provider=? AND content_id=? AND input_hash=?", (provider, content_id, input_hash)).fetchone()
            if old:
                return dict(old)
            budget = db.execute("SELECT * FROM budgets WHERE provider=?", (provider,)).fetchone()
            if not budget:
                raise OSFailure("Provider spending is disabled until an explicit budget is configured")
            committed = db.execute("SELECT COALESCE(SUM(actual_cents+reserved_cents),0) FROM jobs WHERE provider=?", (provider,)).fetchone()[0]
            if committed + estimated_cents > budget["ceiling_cents"]:
                raise OSFailure("Reservation exceeds the remaining cumulative provider budget")
            jid = secrets.token_hex(12)
            now = utcnow()
            db.execute("INSERT INTO jobs(id,provider,content_id,input_hash,status,reserved_cents,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?)", (jid, provider, content_id, input_hash, "reserved", estimated_cents, now, now))
            self.event(db, "reserved", {"job_id": jid, "cents": estimated_cents})
            return dict(db.execute("SELECT * FROM jobs WHERE id=?", (jid,)).fetchone())

    def start(self, job_id):
        with self.connection() as db:
            job = self._job(db, job_id)
            if job["status"] != "reserved":
                raise OSFailure("Only a reserved job can start; reconcile uncertain requests")
            committed = db.execute("SELECT COALESCE(SUM(actual_cents+reserved_cents),0) FROM jobs WHERE provider=?", (job["provider"],)).fetchone()[0]
            ceiling = db.execute("SELECT ceiling_cents FROM budgets WHERE provider=?", (job["provider"],)).fetchone()[0]
            if committed > ceiling:
                raise OSFailure("Committed cost exceeds the current budget; do not start more work")
            limit = db.execute("SELECT concurrency FROM budgets WHERE provider=?", (job["provider"],)).fetchone()[0]
            active = db.execute("SELECT COUNT(*) FROM jobs WHERE provider=? AND status IN ('running','unknown')", (job["provider"],)).fetchone()[0]
            if active >= limit:
                raise OSFailure("Shared provider concurrency is exhausted")
            db.execute("UPDATE jobs SET status='running',updated_at=? WHERE id=?", (utcnow(), job_id))
            self.event(db, "job_started", {"job_id": job_id})

    def reconcile(self, job_id, status, request_id=None, actual_cents=None, result=None):
        if status not in ("unknown", "succeeded", "failed", "cancelled"):
            raise OSFailure("Unsupported reconciliation status")
        with self.connection() as db:
            job = self._job(db, job_id)
            if job["status"] in ("succeeded", "failed", "cancelled"):
                raise OSFailure("Terminal jobs cannot be overwritten")
            if status == "unknown":
                if job["status"] not in ("running", "unknown"):
                    raise OSFailure("Only an attempted request can become unknown")
                cost, reserved = job["actual_cents"], job["reserved_cents"]
            else:
                if actual_cents is None or actual_cents < 0:
                    raise OSFailure("Terminal state requires a verified actual cost, including zero")
                if status == "succeeded" and (not request_id or not result or job["status"] == "reserved"):
                    raise OSFailure("Success needs an attempted request, provider receipt, and result location")
                cost, reserved = actual_cents, 0
            db.execute("UPDATE jobs SET status=?,request_id=COALESCE(?,request_id),actual_cents=?,reserved_cents=?,result=?,updated_at=? WHERE id=?", (status, request_id, cost, reserved, result, utcnow(), job_id))
            self.event(db, "job_reconciled", {"job_id": job_id, "status": status, "actual_cents": cost})

    @staticmethod
    def _job(db, job_id):
        row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if not row:
            raise OSFailure("Unknown job")
        return row

    def jobs(self):
        with self.connection() as db:
            return [dict(row) for row in db.execute("SELECT * FROM jobs ORDER BY created_at")]

    def register_experiment(self, protocol):
        with self.connection() as db:
            old = db.execute("SELECT protocol_hash FROM experiments WHERE id=?", (protocol["id"],)).fetchone()
            phash = fingerprint(protocol)
            if old and old[0] != phash:
                raise OSFailure("Registered protocol changed; create a new experiment ID")
            db.execute("INSERT OR IGNORE INTO experiments(id,protocol_hash,protocol) VALUES (?,?,?)", (protocol["id"], phash, canonical(protocol).decode()))

    def assign(self, experiment_id, participant_id):
        identifier(participant_id)
        with self.connection() as db:
            exp = db.execute("SELECT * FROM experiments WHERE id=?", (experiment_id,)).fetchone()
            if not exp or exp["state"] != "open":
                raise OSFailure("Experiment is missing or closed")
            old = db.execute("SELECT cell FROM assignments WHERE experiment_id=? AND participant_id=?", (experiment_id, participant_id)).fetchone()
            if old:
                return json.loads(old[0])
            protocol = json.loads(exp["protocol"])
            salt = db.execute("SELECT value FROM settings WHERE key='assignment_salt'").fetchone()[0]
            index = int(fingerprint([salt, experiment_id, participant_id]), 16) % len(protocol["cells"])
            cell = protocol["cells"][index]
            db.execute("INSERT INTO assignments VALUES (?,?,?,?)", (experiment_id, participant_id, json.dumps(cell, sort_keys=True), utcnow()))
            return cell

    def assert_protocol(self, protocol):
        with self.connection() as db:
            row = db.execute("SELECT protocol_hash FROM experiments WHERE id=?", (protocol["id"],)).fetchone()
            if not row or row[0] != fingerprint(protocol):
                raise OSFailure("Current protocol or content differs from registration; use a new experiment ID")

    def stop_enrollment(self, experiment_id):
        with self.connection() as db:
            changed = db.execute("UPDATE experiments SET state='followup' WHERE id=? AND state='open'", (experiment_id,)).rowcount
            if not changed:
                raise OSFailure("No open experiment with that ID")
            self.event(db, "enrollment_stopped", {"experiment_id": experiment_id})

    def respond(self, experiment_id, participant_id, correct, critical_error, trust, useful):
        if correct not in range(4) or critical_error not in (0, 1) or trust not in range(1, 6) or useful not in range(1, 6):
            raise OSFailure("Responses require correct=0..3, critical_error=0/1, and ratings=1..5")
        with self.connection() as db:
            exp = db.execute("SELECT state FROM experiments WHERE id=?", (experiment_id,)).fetchone()
            assigned = db.execute("SELECT 1 FROM assignments WHERE experiment_id=? AND participant_id=?", (experiment_id, participant_id)).fetchone()
            if not exp or exp[0] not in ("open", "followup") or not assigned:
                raise OSFailure("An open response window and a prior assignment are required")
            try:
                db.execute("INSERT INTO responses VALUES (?,?,?,?,?,?,?)", (experiment_id, participant_id, correct, critical_error, trust, useful, utcnow()))
            except sqlite3.IntegrityError as exc:
                raise OSFailure("Response already exists; do not overwrite collected evidence") from exc

    def close_experiment(self, experiment_id):
        with self.connection() as db:
            changed = db.execute("UPDATE experiments SET state='closed' WHERE id=? AND state IN ('open','followup')", (experiment_id,)).rowcount
            if not changed:
                raise OSFailure("No open experiment with that ID")
            self.event(db, "experiment_closed", {"experiment_id": experiment_id})
