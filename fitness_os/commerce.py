"""Offline signed-event import; not a deployed checkout or webhook server."""
import hashlib
import hmac
import json
import time
from .common import OSFailure, utcnow


def verify_event(body, signature, secret, now=None, tolerance=300):
    if not secret or tolerance <= 0:
        raise OSFailure("A webhook secret and positive timestamp tolerance are required")
    parts = [x.strip().split("=", 1) for x in signature.split(",") if "=" in x]
    stamps = [v for k,v in parts if k == "t"]
    try:
        timestamp = int(stamps[0]) if len(stamps) == 1 else None
    except ValueError:
        timestamp = None
    if timestamp is None or abs((time.time() if now is None else now)-timestamp) > tolerance:
        raise OSFailure("Invalid or stale webhook timestamp")
    expected = hmac.new(secret.encode(), str(timestamp).encode()+b"."+body, hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(v, expected) for k,v in parts if k == "v1"):
        raise OSFailure("Invalid webhook signature")
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise OSFailure("Invalid event JSON") from exc


def import_event(store, event):
    """Record minimal provider facts; payment is never inferred from checkout creation."""
    if not isinstance(event.get("id"), str) or not event["id"].startswith("evt_"):
        raise OSFailure("Invalid provider event identity")
    obj = event.get("data", {}).get("object", {})
    kind = event.get("type", "unknown")
    allowed = {"checkout.session.completed", "checkout.session.async_payment_succeeded",
               "invoice.paid", "invoice.payment_failed", "customer.subscription.deleted", "charge.refunded"}
    if kind not in allowed:
        return {"status": "ignored", "type": kind}
    # Keep provider event type: invoice and checkout events are not additive revenue.
    amount = obj.get("amount_paid") if kind == "invoice.paid" else None
    if kind == "charge.refunded":
        amount = obj.get("amount_refunded")
    customer = obj.get("customer")
    if isinstance(customer, dict):
        customer = customer.get("id")
    content_id = obj.get("metadata", {}).get("content_id")
    with store.connection() as db:
        count = db.execute("INSERT OR IGNORE INTO commerce VALUES (?,?,?,?,?,?,?,?)", (event["id"], utcnow(), kind, customer, content_id, amount, obj.get("currency"), int(not event.get("livemode", False)))).rowcount
        store.event(db, "commerce_import", {"event_id": event["id"], "inserted": bool(count)})
    return {"status": "recorded" if count else "duplicate", "event_id": event["id"], "type": kind,
            "note": "Provider observation only; no product access, email, or revenue aggregation was performed."}
