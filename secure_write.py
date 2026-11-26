"""Synthetic-only Windows Broker and Secure Writer entry points."""

from __future__ import annotations

from release_paths import protected_vault

import argparse
from contextlib import closing
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
import logging
import os
from pathlib import Path, PurePosixPath
import re
import sqlite3
from urllib.parse import quote
from uuid import uuid4

import pywintypes
import win32con
import win32file
import win32security as sec

from ledger_admission import AdmissionLedger, IdempotencyConflict
import human_authorization
from projection_recovery import FileEvidence, PreparedProjection, _observe, identity, observe_bytes, reconcile
from server import Wiki, safe_name, is_link
from mcp.server.fastmcp.exceptions import ToolError
from write_transport import OutcomeUnknown, call, decode, encode, process_sid, serve


SID = re.compile(r"S-1-[0-9]+(?:-[0-9]+)+")
HASH = re.compile(r"[0-9a-f]{64}")
KEY = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}")
SCOPE = PurePosixPath("10_Agent/wiki")
MARKER = ".knowledgeos-r6-synthetic"
TRUSTED_SYSTEM = {"S-1-5-18", "S-1-5-32-544"}
LOG = logging.getLogger("knowledgeos.secure_write")


def validate(request):
    op = request.get("operation")
    if op == "human_update" or op in human_authorization.OPERATIONS:
        raise PermissionError("HUMAN_WRITE_AUTHORIZATION_REQUIRED")
    if op == "ping" and set(request) == {"operation"}:
        return
    if op == "sync_wiki" and set(request) == {"operation"}:
        return
    if op == "audit":
        if (set(request) != {"operation", "offset", "limit"}
                or type(request["offset"]) is not int or not 0 <= request["offset"] <= 1_000_000
                or type(request["limit"]) is not int or not 1 <= request["limit"] <= 20):
            raise ValueError("invalid audit page")
        return
    if op in {"status", "delete_status"}:
        if set(request) != {"operation", "key"} or not KEY.fullmatch(request["key"]):
            raise ValueError("invalid status")
        return
    fields = {"operation", "key", "path", "expected_sha256", "expected_identity"}
    if op in {"restore", "restore_deleted"}:
        fields.add("backup_transaction")
    elif op in {"create", "update"}:
        fields.add("markdown")
    if op not in {"create", "update", "restore", "delete", "restore_deleted"} or set(request) != fields:
        raise ValueError("invalid request")
    path = request["path"]
    if not safe_name(path) or not KEY.fullmatch(request["key"]):
        raise ValueError("invalid request")
    rel = PurePosixPath(path)
    if rel.parts[0].casefold() == "00_human":
        raise PermissionError("HUMAN_WRITE_AUTHORIZATION_REQUIRED")
    elif SCOPE not in rel.parents or rel.suffix != ".md" or rel.name.casefold() in {"index.md", "log.md", "readme.md"}:
        raise PermissionError("PATH_DENIED")
    digest, expected_id = request["expected_sha256"], request["expected_identity"]
    if op in {"restore", "restore_deleted"} and not re.fullmatch(r"[0-9a-f]{32}", request["backup_transaction"]):
        raise ValueError("restore requires the source transaction ID")
    if op in {"create", "update"} and not request["markdown"].strip():
        raise ValueError("empty Markdown")
    if op in {"update", "restore", "delete"}:
        if not HASH.fullmatch(digest or "") or not isinstance(expected_id, str) or not re.fullmatch(r"[0-9]+:[0-9]+", expected_id):
            raise ValueError("update requires SHA-256 and file identity")
    elif digest is not None or expected_id is not None:
        raise ValueError("create requires absence")


def descriptor(writer, readers=()):
    text = f"O:{writer}D:P(A;;FA;;;{writer})" + "".join(f"(A;;FR;;;{sid})" for sid in readers)
    return sec.ConvertStringSecurityDescriptorToSecurityDescriptor(text, 1)


class Writer:
    def __init__(self, config):
        self.root = Path(config["root"])
        self.writer = config["writer_sid"]
        self.agent = config["agent_sid"]
        self.human = config["human_sid"]
        self.human_targets = frozenset(config.get("human_authorization_targets", ()))
        if self.human_targets and self.human_targets != {human_authorization.TEST_TARGET}:
            raise PermissionError("Human projection requires the dedicated synthetic test file")
        self.delete_targets = frozenset(config.get("delete_targets", ()))
        real = protected_vault()
        if (self.root.resolve().is_relative_to(real.resolve()) or self.root != self.root.resolve()
                or not self.root.is_absolute() or is_link(self.root)):
            raise PermissionError("synthetic root must be a plain absolute directory")
        # This marker and every used directory must be protected before service start.
        self.assert_acl(self.root, require_writer=True)
        self.root_id = identity(self.root.stat())
        if list(self.root_id) != config["root_identity"]:
            raise PermissionError("configured synthetic root identity does not match")
        marker = self.root / MARKER
        if is_link(marker):
            raise PermissionError("synthetic marker is linked")
        self.assert_acl(marker, require_writer=True)
        if marker.read_bytes() != b"KnowledgeOS R6 synthetic only\n":
            raise PermissionError("synthetic marker missing")
        self.state = self.root / ".knowledgeos/wb3d2"
        self.check_parent(self.state, private=True)
        self.database = self.state / "ledger.sqlite3"
        if self.database.exists():
            if is_link(self.database) or self.database.stat().st_nlink != 1:
                raise PermissionError("unexpected ledger file")
            self.assert_acl(self.database, private=True)
        self.ledger = AdmissionLedger(self.database)
        self.ledger.initialize()
        with closing(self.connect()) as db, db:
            human_authorization.initialize(db)
            db.execute("CREATE TABLE IF NOT EXISTS wiki_index_cache (path TEXT PRIMARY KEY, title TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS wiki_index_pending (path TEXT PRIMARY KEY)")
            db.execute("CREATE TABLE IF NOT EXISTS wiki_index_initialized (id INTEGER PRIMARY KEY CHECK(id=1))")
            db.execute("""CREATE TABLE IF NOT EXISTS projection_receipts (
                tx TEXT PRIMARY KEY REFERENCES transactions(transaction_id),
                target TEXT NOT NULL, evidence TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('PREPARED','COMMITTED','NEEDS_REVIEW'))
            )""")
            db.execute("""CREATE UNIQUE INDEX IF NOT EXISTS active_projection
                ON projection_receipts(target COLLATE NOCASE)
                WHERE state IN ('PREPARED','NEEDS_REVIEW')""")
            db.execute("""CREATE TABLE IF NOT EXISTS projection_backups (
                tx TEXT PRIMARY KEY REFERENCES projection_receipts(tx),
                file_identity TEXT NOT NULL, sha256 TEXT NOT NULL, content BLOB NOT NULL
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS commit_audit (
                tx TEXT PRIMARY KEY REFERENCES projection_receipts(tx),
                committed_utc TEXT NOT NULL
            )""")
            db.execute("""CREATE VIEW IF NOT EXISTS committed_knowledge AS
                SELECT t.transaction_id, t.authenticated_principal AS actor_identity,
                       t.idempotency_key, t.request_fingerprint AS request_hash,
                       json_extract(t.request_json, '$.operation') AS operation,
                       p.target, json_extract(p.evidence, '$.previous.digest') AS previous_hash,
                       json_extract(p.evidence, '$.replacement.digest') AS resulting_hash,
                       json_extract(p.evidence, '$.replacement.identity') AS resulting_identity,
                       a.committed_utc, p.state
                FROM transactions t JOIN projection_receipts p ON p.tx=t.transaction_id
                LEFT JOIN commit_audit a ON a.tx=p.tx WHERE p.state='COMMITTED'""")

    def assert_acl(self, path, require_writer=False, private=False):
        sd = sec.GetFileSecurity(str(path), sec.OWNER_SECURITY_INFORMATION | sec.DACL_SECURITY_INFORMATION)
        owner = sec.ConvertSidToStringSid(sd.GetSecurityDescriptorOwner())
        trusted = TRUSTED_SYSTEM | {self.writer}
        if owner not in trusted:
            raise PermissionError("untrusted directory or file owner")
        acl = sd.GetSecurityDescriptorDacl()
        # No ACE other than explicit, ordinary allows; only Writer/trusted OS may write.
        if acl is None:
            raise PermissionError("null DACL")
        writer_allowed = False
        for i in range(acl.GetAceCount()):
            (kind, flags), mask, sid = acl.GetAce(i)
            name = sec.ConvertSidToStringSid(sid)
            if kind != 0:
                raise PermissionError("unsupported ACL entry")
            if name == self.writer and not flags & 8 and mask & 2:
                writer_allowed = True
            if (name == self.human and not private and not flags and not mask & ~0x00120089
                    and path == self.root / human_authorization.TEST_TARGET and self.human_targets):
                continue
            if name not in trusted and (private or name != self.agent or mask & ~0x001200A9):
                raise PermissionError("unexpected effective or inheritable rights")
        if require_writer and (not writer_allowed or not sd.GetSecurityDescriptorControl()[0] & 0x1000):
            raise PermissionError("protected Writer directory required")

    def check_parent(self, parent, private=False):
        if self.root.resolve(strict=True) != self.root or identity(self.root.stat()) != self.root_id:
            raise PermissionError("root identity drift")
        for current in (parent, *parent.parents):
            if not current.is_relative_to(self.root):
                break
            if is_link(current) or not current.is_dir():
                raise PermissionError("unsafe directory ancestry")
            if current.is_relative_to(self.root):
                self.assert_acl(current, require_writer=True, private=private and current != self.root)

    def connect(self):
        db = sqlite3.connect(self.database.absolute().as_uri() + "?mode=rw", uri=True)
        db.execute("PRAGMA synchronous=FULL")
        db.execute("PRAGMA foreign_keys=ON")
        db.row_factory = sqlite3.Row
        return db

    def finalize(self, db, tx, receipt, wire):
        target = self.root / receipt.target
        human = receipt.target in self.human_targets
        self.check_parent(target.parent)
        state = reconcile(self.root, receipt, wire)
        if state == "PROJECTED":
            if receipt.previous is not None:
                backup = db.execute("SELECT * FROM projection_backups WHERE tx=?", (tx,)).fetchone()
                if (not backup or backup["sha256"] != receipt.previous.digest
                        or sha256(backup["content"]).hexdigest() != receipt.previous.digest
                        or backup["file_identity"] != ":".join(map(str, receipt.previous.identity))):
                    db.execute("UPDATE projection_receipts SET state='NEEDS_REVIEW' WHERE tx=?", (tx,))
                    return {"code": "RECOVERY_REQUIRED", "transaction_id": tx}
            # The staged file has a protected private ACL until its identity is verified.
            protection_flags = (sec.DACL_SECURITY_INFORMATION | 0x80000000) - (1 << 32)
            sec.SetFileSecurity(str(target), protection_flags,
                                descriptor(self.writer, (self.human,) if human else (self.agent,)))
            self.assert_acl(target)
            if reconcile(self.root, receipt, wire) == "PROJECTED":
                db.execute("UPDATE projection_receipts SET state='COMMITTED' WHERE tx=?", (tx,))
                db.execute("INSERT INTO commit_audit VALUES (?, ?)", (tx, datetime.now(timezone.utc).isoformat()))
                if not human:
                    db.execute("INSERT OR IGNORE INTO wiki_index_pending VALUES (?)", (receipt.target,))
                db.commit()
                LOG.info("projection committed transaction_id=%s", tx)
                return self.committed(tx, receipt.replacement.digest)
        if state == "PREPARED":
            return {"code": "RECOVERY_REQUIRED", "transaction_id": tx}
        db.execute("UPDATE projection_receipts SET state='NEEDS_REVIEW' WHERE tx=?", (tx,))
        return {"code": "RECOVERY_REQUIRED", "transaction_id": tx}

    def dispatch(self, _broker, envelope):
        if set(envelope) != {"principal", "request", "digest"}:
            return {"code": "DENIED"}
        request = envelope["request"]
        wire = encode(request)
        if sha256(wire).hexdigest() != envelope["digest"]:
            return {"code": "INVALID_REQUEST"}
        try:
            peer = envelope["principal"]
            if peer != self.agent:
                return {"code": "DENIED"}
            validate(request)
            if request["operation"] in {"delete", "restore_deleted"} and request["path"] not in self.delete_targets:
                return {"code": "DENIED"}
            return self.submit(request, wire)
        except IdempotencyConflict:
            return {"code": "CONFLICT"}
        except PermissionError as exc:
            return {"code": str(exc) if str(exc) in {"HUMAN_WRITE_AUTHORIZATION_REQUIRED", "PATH_DENIED"} else "DENIED"}
        except (OSError, sqlite3.Error, pywintypes.error):
            return {"code": "RECOVERY_REQUIRED"}

    def submit(self, request, wire):
        if request["operation"] == "ping":
            return {"code": "AVAILABLE"}
        if request["operation"] == "sync_wiki":
            return {"code": self.sync_wiki()}
        if request["operation"] == "audit":
            with closing(self.connect()) as db:
                limit, offset = request["limit"], request["offset"]
                events = db.execute("""SELECT transaction_id, actor_identity, operation, target,
                    request_hash, previous_hash, resulting_hash, committed_utc, state
                    FROM committed_knowledge WHERE actor_identity=? AND target GLOB '10_Agent/wiki/*'
                    ORDER BY committed_utc, transaction_id LIMIT ? OFFSET ?""",
                    (self.agent, limit + 1, offset)).fetchall()
            return {"code": "AUDIT_PAGE", "items": [dict(row) for row in events[:limit]],
                    "next_offset": offset + limit if len(events) > limit else None}
        if request["operation"] in {"status", "delete_status"}:
            with closing(self.connect()) as db, db:
                row = db.execute("""SELECT t.*, p.state, p.evidence FROM transactions t
                    LEFT JOIN projection_receipts p ON p.tx=t.transaction_id
                    WHERE authenticated_principal=? AND idempotency_key=?""", (self.agent, request["key"])).fetchone()
                if not row:
                    return {"code": "NOT_FOUND"}
                if request["operation"] == "delete_status" and json.loads(row["request_json"])["operation"] != "delete":
                    return {"code": "NOT_FOUND"}
                result = {"transaction_id": row["transaction_id"]}
                if row["state"] == "COMMITTED":
                    return {**result, "code": "COMMITTED",
                            "sha256": (json.loads(row["evidence"]).get("replacement") or {}).get("digest")}
                original = json.loads(row["request_json"])
                if (row["state"] == "PREPARED" and original["operation"] == "human_update"
                        and original["path"] in self.human_targets and db.execute(
                            "SELECT 1 FROM human_authorization_consumption WHERE authorization_id=? AND transaction_id=?",
                            (original["authorization_id"], row["transaction_id"])).fetchone()):
                    return self.status(db, row, row["transaction_id"], encode(original))
                return {**result, "code": "RECOVERY_REQUIRED" if row["state"] else "REQUEST_ACCEPTED"}
        human = request["operation"] == "human_update"
        if human:
            if request["path"] not in self.human_targets:
                return {"code": "DENIED"}
            with closing(self.connect()) as db:
                if not human_authorization.permits_update(db, self.agent, self.human, request):
                    return {"code": "DENIED"}
        accepted = self.ledger.accept(self.agent, request["key"], wire)
        tx = accepted.transaction_id
        LOG.info("request registered transaction_id=%s", tx)
        with closing(self.connect()) as db, db:
            if human:
                db.execute("BEGIN IMMEDIATE")
                if not human_authorization.permits_update(db, self.agent, self.human, request):
                    return {"code": "DENIED"}
            row = db.execute("SELECT * FROM projection_receipts WHERE tx=?", (tx,)).fetchone()
            if row:
                if request["operation"] == "delete":
                    return self.complete_delete(db, tx, row, wire)
                return self.status(db, row, tx, wire)
            target = self.root / request["path"]
            self.check_parent(target.parent)
            if db.execute("""SELECT 1 FROM projection_receipts WHERE target=? COLLATE NOCASE
                          AND state IN ('PREPARED','NEEDS_REVIEW')""", (request["path"],)).fetchone():
                return {"code": "RECOVERY_REQUIRED"}
            snapshot = observe_bytes(target)
            previous = snapshot[0] if snapshot is not None else None
            if previous is not None:
                self.assert_acl(target)
            if request["operation"] in {"create", "restore_deleted"}:
                if previous is not None:
                    return {"code": "CONFLICT"}
            elif previous is None or previous.digest != request["expected_sha256"] or (
                ":".join(map(str, previous.identity)) != request["expected_identity"]
            ):
                return {"code": "CONFLICT"}
            projection = request
            if request["operation"] == "delete":
                evidence = {"target": request["path"], "previous": asdict(previous), "replacement": None,
                            "parent_identity": identity(target.parent.stat()), "request_digest": sha256(wire).hexdigest(),
                            "authorization_id": "synthetic-delete-allowlist"}
                db.execute("INSERT INTO projection_receipts VALUES (?, ?, ?, 'PREPARED')",
                           (tx, request["path"], json.dumps(evidence)))
                db.execute("INSERT INTO projection_backups VALUES (?, ?, ?, ?)",
                           (tx, ":".join(map(str, previous.identity)), previous.digest, snapshot[1]))
                db.commit()
                row = db.execute("SELECT * FROM projection_receipts WHERE tx=?", (tx,)).fetchone()
                return self.complete_delete(db, tx, row, wire)
            if request["operation"] in {"restore", "restore_deleted"}:
                backup = db.execute("""SELECT b.content,b.sha256,p.target
                    FROM projection_backups b JOIN projection_receipts p ON p.tx=b.tx
                    JOIN transactions t ON t.transaction_id=p.tx
                    WHERE b.tx=? AND p.state='COMMITTED' AND t.authenticated_principal=?
                    AND (json_extract(t.request_json,'$.operation')='delete')=?""",
                    (request["backup_transaction"], self.agent, request["operation"] == "restore_deleted")).fetchone()
                if not backup or backup["target"] != request["path"]:
                    return {"code": "DENIED"}
                if sha256(backup["content"]).hexdigest() != backup["sha256"]:
                    return {"code": "RECOVERY_REQUIRED"}
                projection = {**request, "markdown": backup["content"].decode("utf-8")}
            stage = target.with_name("r6-" + tx + ".stage")
            receipt = self.prepare(stage, target, projection, wire, previous)
            db.execute("INSERT INTO projection_receipts VALUES (?, ?, ?, 'PREPARED')",
                       (tx, receipt.target, json.dumps(asdict(receipt))))
            if snapshot is not None:
                db.execute("INSERT INTO projection_backups VALUES (?, ?, ?, ?)",
                           (tx, ":".join(map(str, previous.identity)), previous.digest, snapshot[1]))
            if human:
                db.execute("INSERT INTO human_authorization_consumption VALUES (?,?)",
                           (request["authorization_id"], tx))
            db.commit()
            LOG.info("projection prepared transaction_id=%s", tx)
            if human:
                db.execute("BEGIN IMMEDIATE")
                if not human_authorization.permits_update(db, self.agent, self.human, request, tx):
                    db.execute("UPDATE projection_receipts SET state='NEEDS_REVIEW' WHERE tx=?", (tx,))
                    return {"code": "DENIED", "transaction_id": tx}
            self.check_parent(target.parent)
            if reconcile(self.root, receipt, wire) != "PREPARED":
                db.execute("UPDATE projection_receipts SET state='NEEDS_REVIEW' WHERE tx=?", (tx,))
                return {"code": "RECOVERY_REQUIRED", "transaction_id": tx}
            if human and not human_authorization.permits_update(db, self.agent, self.human, request, tx):
                db.execute("UPDATE projection_receipts SET state='NEEDS_REVIEW' WHERE tx=?", (tx,))
                return {"code": "DENIED", "transaction_id": tx}
            if previous is not None:
                self.assert_acl(target)
                os.replace(stage, target)
            else:
                os.rename(stage, target)  # Windows refuses an existing target.
            return self.finalize(db, tx, receipt, wire)

    def complete_delete(self, db, tx, row, wire):
        if row["state"] == "COMMITTED":
            return {"code": "COMMITTED", "transaction_id": tx, "sha256": None}
        if row["state"] != "PREPARED":
            return {"code": "RECOVERY_REQUIRED", "transaction_id": tx}
        data = json.loads(row["evidence"])
        target = self.root / data["target"]
        tombstone = self.state / ("deleted-" + tx + ".bin")
        old = FileEvidence(tuple(data["previous"]["identity"]), data["previous"]["digest"])
        backup = db.execute("SELECT * FROM projection_backups WHERE tx=?", (tx,)).fetchone()
        self.check_parent(target.parent)
        self.check_parent(self.state, private=True)
        if (backup and sha256(backup["content"]).hexdigest() == backup["sha256"] == old.digest
                and backup["file_identity"] == ":".join(map(str, old.identity))
                and data["request_digest"] == sha256(wire).hexdigest()
                and tuple(data["parent_identity"]) == identity(target.parent.stat())
                and identity(self.state.stat())[0] == old.identity[0]):
            current, retained = _observe(target), _observe(tombstone)
            if current == old and retained is None:
                self.assert_acl(target)
                protection_flags = (sec.DACL_SECURITY_INFORMATION | 0x80000000) - (1 << 32)
                sec.SetFileSecurity(str(target), protection_flags, descriptor(self.writer))
                if _observe(target) == old:
                    os.rename(target, tombstone)  # Windows rename refuses an existing destination.
                current, retained = _observe(target), _observe(tombstone)
            if current is None and retained == old:
                self.assert_acl(tombstone, private=True)
                db.execute("UPDATE projection_receipts SET state='COMMITTED' WHERE tx=?", (tx,))
                db.execute("INSERT INTO commit_audit VALUES (?, ?)", (tx, datetime.now(timezone.utc).isoformat()))
                db.execute("INSERT OR IGNORE INTO wiki_index_pending VALUES (?)", (data["target"],))
                db.commit()
                LOG.info("delete committed transaction_id=%s", tx)
                return self.committed(tx, None)
        db.execute("UPDATE projection_receipts SET state='NEEDS_REVIEW' WHERE tx=?", (tx,))
        return {"code": "RECOVERY_REQUIRED", "transaction_id": tx}

    def committed(self, tx, digest):
        return {"code": "COMMITTED", "transaction_id": tx, "sha256": digest,
                "wiki_projection": self.sync_wiki(rebuild=False)}

    def index_entries(self, wiki, rebuild):
        with closing(self.connect()) as db, db:
            if rebuild or not db.execute("SELECT 1 FROM wiki_index_initialized").fetchone():
                notes, skipped, _ = wiki.snapshot("agent")
                if skipped:
                    raise OSError("incomplete Agent wiki snapshot")
                db.execute("DELETE FROM wiki_index_cache")
                db.executemany("INSERT INTO wiki_index_cache VALUES (?,?)",
                               ((n.path, n.document.title) for n in notes if
                                PurePosixPath(n.path).name.casefold() not in {"index.md", "log.md", "readme.md"}))
                db.execute("INSERT OR IGNORE INTO wiki_index_initialized VALUES (1)")
            else:
                for row in db.execute("SELECT path FROM wiki_index_pending"):
                    path = row["path"]
                    try:
                        note = wiki.read(path)
                    except ToolError as exc:
                        if not str(exc).startswith("NOTE_NOT_FOUND:"):
                            raise
                        db.execute("DELETE FROM wiki_index_cache WHERE path=? COLLATE NOCASE", (path,))
                    else:
                        canonical = (self.root / path).resolve(strict=True).relative_to(self.root).as_posix()
                        db.execute("DELETE FROM wiki_index_cache WHERE path=? COLLATE NOCASE", (path,))
                        db.execute("INSERT OR REPLACE INTO wiki_index_cache VALUES (?,?)",
                                   (canonical, note.document.title))
            db.execute("DELETE FROM wiki_index_pending")
            return db.execute("SELECT path,title FROM wiki_index_cache").fetchall()

    def sync_wiki(self, rebuild=True):
        try:
            parent = self.root / SCOPE
            self.check_parent(parent)
            entries = self.index_entries(Wiki(self.root), rebuild)
            lines = ["## Agent knowledge", ""]
            for entry in sorted(entries, key=lambda row: (row["title"].casefold(), row["path"])):
                title = " ".join(entry["title"].split())
                title = re.sub(r"([\\`*_[\]<>])", r"\\\1", title)
                relative = PurePosixPath(entry["path"]).relative_to(SCOPE).as_posix()
                lines.append(f"- [{title}]({quote(relative, safe='/')})")
            self.sync_block(parent / "index.md", "index", "# Agent Wiki Index", lines)
            with closing(self.connect()) as db:
                rows = db.execute("""SELECT transaction_id, committed_utc, operation, target,
                    actor_identity, previous_hash, resulting_hash FROM committed_knowledge
                    WHERE target GLOB '10_Agent/wiki/*' ORDER BY committed_utc, transaction_id""").fetchall()
            history = ["## Committed transactions", ""]
            history.extend("    " + json.dumps(dict(row), ensure_ascii=False) for row in rows)
            self.sync_block(parent / "log.md", "log", "# Agent Wiki Log", history)
            return "SYNCED"
        except (OSError, ValueError, sqlite3.Error, pywintypes.error, ToolError):
            LOG.exception("derived wiki projection pending")
            return "SYNC_PENDING"

    def sync_block(self, target, name, title, lines):
        start = f"<!-- knowledgeos:{name}:start -->"
        end = f"<!-- knowledgeos:{name}:end -->"
        block = "\n".join((start, *lines, end))
        snapshot = observe_bytes(target)
        previous = snapshot[0] if snapshot else None
        text = snapshot[1].decode("utf-8") if snapshot else title + "\n"
        if snapshot:
            self.assert_acl(target)
        if text.count(start) == text.count(end) == 0:
            updated = text + ("\n" if text.endswith("\n") else "\n\n") + block + "\n"
        elif text.count(start) == text.count(end) == 1 and text.index(start) < text.index(end):
            updated = text[:text.index(start)] + block + text[text.index(end) + len(end):]
        else:
            raise ValueError("invalid managed projection block")
        protection = (sec.DACL_SECURITY_INFORMATION | 0x80000000) - (1 << 32)
        if updated != text:
            stage = target.with_name("r6-" + uuid4().hex + ".stage")
            self.write_stage(stage, updated.encode("utf-8"))
            try:
                self.check_parent(target.parent)
                if _observe(target) != previous:
                    raise OSError("wiki projection changed before replacement")
                if previous is None:
                    os.rename(stage, target)
                else:
                    os.replace(stage, target)
            finally:
                stage.unlink(missing_ok=True)
        sec.SetFileSecurity(str(target), protection, descriptor(self.writer, (self.agent,)))
        self.assert_acl(target)

    def write_stage(self, stage, payload):
        sa = pywintypes.SECURITY_ATTRIBUTES()
        sa.SECURITY_DESCRIPTOR = descriptor(self.writer)
        handle = win32file.CreateFile(str(stage), win32con.GENERIC_WRITE, 0, sa,
                                      win32con.CREATE_NEW, win32con.FILE_ATTRIBUTE_NORMAL, None)
        try:
            if win32file.WriteFile(handle, payload)[1] != len(payload):
                raise OSError("incomplete stage")
            win32file.FlushFileBuffers(handle)
        finally:
            handle.Close()
        self.assert_acl(stage, private=True)

    def prepare(self, stage, target, request, wire, previous):
        self.write_stage(stage, request["markdown"].encode())
        # The staged sibling is private by ACL until the target is verified.
        return PreparedProjection(request["path"], stage.relative_to(self.root).as_posix(),
                                  self.root_id, identity(target.parent.stat()), sha256(wire).hexdigest(),
                                  previous, _observe(stage))

    def status(self, db, row, tx, wire):
        state = row["state"]
        if not state:
            return {"code": "REQUEST_ACCEPTED", "transaction_id": tx}
        data = json.loads(row["evidence"])
        if state == "COMMITTED":
            return {"code": "COMMITTED", "transaction_id": tx, "sha256": data["replacement"]["digest"]}
        if state == "NEEDS_REVIEW":
            return {"code": "RECOVERY_REQUIRED", "transaction_id": tx}
        for key in ("root_identity", "parent_identity"):
            data[key] = tuple(data[key])
        for key in ("previous", "replacement"):
            if data[key] is not None:
                data[key] = FileEvidence(tuple(data[key]["identity"]), data[key]["digest"])
        return self.finalize(db, tx, PreparedProjection(**data), wire)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=("broker", "writer"))
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config = decode(args.config.read_bytes())
    sid = {name: config[name + "_sid"] for name in ("broker", "writer", "agent", "human")}
    if len(set(sid.values())) != 4 or not all(SID.fullmatch(value) for value in sid.values()):
        parser.error("four distinct Windows SIDs required")
    if process_sid() != sid[args.role]:
        parser.error("service process TokenUser does not match configured SID")
    administrators = sec.ConvertStringSidToSid("S-1-5-32-544")
    if sec.CheckTokenMembership(None, administrators) or sid[args.role] in TRUSTED_SYSTEM:
        parser.error("elevated or system tokens cannot run the synthetic service")
    if args.role == "writer":
        serve(config["writer_pipe"], sid["writer"], {sid["broker"]}, Writer(config).dispatch)
    else:
        def dispatch(peer, request):
            try:
                if peer != sid["agent"]:
                    return {"code": "DENIED"}
                validate(request)
                if request["operation"] in {"delete", "restore_deleted"} and request["path"] not in config.get("delete_targets", ()):
                    return {"code": "DENIED"}
                return call(config["writer_pipe"], sid["writer"],
                            {"principal": peer, "request": request, "digest": sha256(encode(request)).hexdigest()})
            except PermissionError as exc:
                return {"code": str(exc) if str(exc) in {"PATH_DENIED", "HUMAN_WRITE_AUTHORIZATION_REQUIRED"} else "DENIED"}
            except OutcomeUnknown:
                return {"code": "OUTCOME_UNKNOWN"}
            except pywintypes.error:
                return {"code": "SECURE_WRITER_UNAVAILABLE"}
        serve(config["broker_pipe"], sid["broker"], {sid["agent"]}, dispatch)


if __name__ == "__main__":
    main()
