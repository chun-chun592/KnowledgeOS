"""Synthetic authorization lifecycle backed by the Writer's existing SQLite ledger."""

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import re
from uuid import uuid4

from server import safe_name
from write_transport import encode


OPERATIONS = frozenset({"authorization_request", "authorization_status",
                        "authorization_approve", "authorization_reject", "authorization_revoke"})
HEX = re.compile(r"[0-9a-f]{64}")
ID = re.compile(r"[0-9a-f]{32}")
TEST_TARGET = "R75H12-Human-Authorization/human-authorization-fixture.md"


def initialize(db):
    db.execute("""CREATE TABLE IF NOT EXISTS human_authorizations (
        authorization_id TEXT PRIMARY KEY, human_sid TEXT NOT NULL, agent_sid TEXT NOT NULL,
        operation_scope TEXT NOT NULL, target_scope TEXT NOT NULL, issued_at_utc TEXT,
        expires_at_utc TEXT, authorization_state TEXT NOT NULL CHECK(authorization_state IN
            ('PENDING','APPROVED','REJECTED','REVOKED','EXPIRED')),
        revoked_at_utc TEXT, request_nonce TEXT NOT NULL, request_hash TEXT NOT NULL,
        audit_transaction_id TEXT NOT NULL REFERENCES transactions(transaction_id), expected_identity TEXT NOT NULL,
        expected_sha256 TEXT NOT NULL, proposed_sha256 TEXT NOT NULL,
        ttl_seconds INTEGER NOT NULL, UNIQUE(agent_sid,request_nonce)
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS human_authorization_consumption (
        authorization_id TEXT PRIMARY KEY REFERENCES human_authorizations(authorization_id),
        transaction_id TEXT NOT NULL UNIQUE REFERENCES transactions(transaction_id)
    )""")


def permits_update(db, agent, human, request, transaction_id=None):
    row = db.execute("""SELECT a.*, c.transaction_id AS consumed_by FROM human_authorizations a
        LEFT JOIN human_authorization_consumption c USING(authorization_id)
        WHERE a.authorization_id=? AND a.agent_sid=? AND a.human_sid=?""",
        (request["authorization_id"], agent, human)).fetchone()
    if row is None or row["consumed_by"] != transaction_id:
        return False
    now = datetime.now(timezone.utc).isoformat()
    if (row["authorization_state"] != "APPROVED"
            or not row["issued_at_utc"] <= now < row["expires_at_utc"]):
        return False
    expected = {"operation": "authorization_request", "target": request["path"], "change": "update",
                "expected_identity": request["expected_identity"], "expected_sha256": request["expected_sha256"],
                "proposed_sha256": sha256(request["markdown"].encode()).hexdigest(),
                "request_nonce": request["request_nonce"], "ttl_seconds": row["ttl_seconds"]}
    return (row["operation_scope"] == "update" and row["target_scope"] == request["path"]
            and row["request_hash"] == request["request_hash"] == sha256(encode(expected)).hexdigest())


def record(db, authorization_id, actor, operation, request, now):
    event = uuid4().hex
    payload = encode({"operation": operation, "authorization_id": authorization_id, "request": request})
    db.execute("""INSERT INTO transactions
        (transaction_id,authenticated_principal,idempotency_key,request_fingerprint,request_json,transaction_state,accepted_utc)
        VALUES (?,?,?,?,?,'REQUEST_ACCEPTED',?)""", (event, actor, event, sha256(payload).hexdigest(), payload.decode(), now))
    return event


def dispatch(db, peer, agent, human, request, targets):
    action = request["operation"]
    is_request = action == "authorization_request"
    is_status = action == "authorization_status"
    if peer not in ({agent} if is_request else {agent, human} if is_status else {human}):
        return {"code": "DENIED"}
    now = datetime.now(timezone.utc).isoformat()
    if is_request:
        fields = {"operation", "target", "change", "expected_identity", "expected_sha256",
                  "proposed_sha256", "request_nonce", "ttl_seconds"}
        if set(request) != fields:
            return {"code": "INVALID_REQUEST"}
        target = request["target"]
        if (request["change"] != "update" or not safe_name(target) or target not in targets
                or target != TEST_TARGET):
            return {"code": "DENIED"}
        if (not all(HEX.fullmatch(request[key]) for key in ("expected_sha256", "proposed_sha256"))
                or not re.fullmatch(r"[0-9]+:[0-9]+", request["expected_identity"])
                or not ID.fullmatch(request["request_nonce"])
                or type(request["ttl_seconds"]) is not int or not 1 <= request["ttl_seconds"] <= 3600):
            return {"code": "INVALID_REQUEST"}
        if db.execute("SELECT 1 FROM human_authorizations WHERE agent_sid=? AND request_nonce=?",
                      (peer, request["request_nonce"])).fetchone():
            return {"code": "DENIED", "reason": "REPLAY"}
        identifier = uuid4().hex
        event = record(db, identifier, peer, action, request, now)
        db.execute("""INSERT INTO human_authorizations
            (authorization_id,human_sid,agent_sid,operation_scope,target_scope,authorization_state,
             request_nonce,request_hash,audit_transaction_id,expected_identity,expected_sha256,proposed_sha256,ttl_seconds)
            VALUES (?,?,?,?,?,'PENDING',?,?,?,?,?,?,?)""",
                   (identifier, human, agent, "update", target, request["request_nonce"],
                    sha256(encode(request)).hexdigest(), event, request["expected_identity"],
                    request["expected_sha256"], request["proposed_sha256"], request["ttl_seconds"]))
    else:
        identifier = request["authorization_id"]
        fields = {"operation", "authorization_id"}
        if action == "authorization_approve":
            fields.add("request_hash")
        if set(request) != fields or not ID.fullmatch(identifier):
            return {"code": "INVALID_REQUEST"}
    row = db.execute("SELECT * FROM human_authorizations WHERE authorization_id=? AND agent_sid=? AND human_sid=?",
                     (identifier, agent, human)).fetchone()
    if row is None:
        return {"code": "NOT_FOUND"}
    state = row["authorization_state"]
    if state == "APPROVED" and row["expires_at_utc"] <= now:
        record(db, identifier, peer, "authorization_expire", {}, now)
        db.execute("UPDATE human_authorizations SET authorization_state='EXPIRED' WHERE authorization_id=?",
                   (identifier,))
        state = "EXPIRED"
    if not (is_status or is_request):
        previous, following = {
            "authorization_approve": ("PENDING", "APPROVED"),
            "authorization_reject": ("PENDING", "REJECTED"),
            "authorization_revoke": ("APPROVED", "REVOKED"),
        }[action]
        if (state != previous or (following == "APPROVED" and
                (request["request_hash"] != row["request_hash"] or row["target_scope"] not in targets))):
            return {"code": "DENIED"}
        record(db, identifier, peer, action, request, now)
        expiry = (datetime.fromisoformat(now) + timedelta(seconds=row["ttl_seconds"])).isoformat()
        db.execute("""UPDATE human_authorizations SET authorization_state=?,
            issued_at_utc=COALESCE(issued_at_utc,?), expires_at_utc=COALESCE(expires_at_utc,?), revoked_at_utc=?
            WHERE authorization_id=?""", (following, now if following == "APPROVED" else None,
                                           expiry if following == "APPROVED" else None,
                                           now if following == "REVOKED" else None, identifier))
    return {"code": "AUTHORIZATION_STATUS", **dict(db.execute(
        "SELECT * FROM human_authorizations WHERE authorization_id=?", (identifier,)).fetchone())}
