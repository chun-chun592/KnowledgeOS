"""Internal SQLite admission component. Use only behind an authenticated Broker.

A receipt proves durable request registration, never authorization or publication.
This module is not connected to MCP or to the live Vault.
"""

from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import re
import sqlite3
from uuid import uuid4


class IdempotencyConflict(ValueError):
    """The authenticated principal reused a key for a different request."""


@dataclass(frozen=True)
class Receipt:
    transaction_id: str
    state: str


class AdmissionLedger:
    """Persist request acceptance in an isolated Writer-owned ledger."""

    def __init__(self, database: Path):
        self.database = database

    def initialize(self) -> None:
        # Explicit provisioning keeps request handling from creating a database.
        with closing(sqlite3.connect(self.database)) as connection, connection:
            connection.execute("PRAGMA journal_mode=DELETE")
            connection.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    authenticated_principal TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    request_fingerprint TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    transaction_state TEXT NOT NULL CHECK(transaction_state = 'REQUEST_ACCEPTED'),
                    accepted_utc TEXT NOT NULL,
                    UNIQUE(authenticated_principal, idempotency_key)
                )
            """)

    def accept(self, authenticated_sid: str, key: str, canonical_request: bytes) -> Receipt:
        """Register bytes already validated and canonicalized by the caller."""
        if not re.fullmatch(r"S-1-[0-9]+(?:-[0-9]+)+", authenticated_sid):
            raise ValueError("Expected a trusted canonical Windows SID")
        if not key or len(key) > 256 or not 0 < len(canonical_request) <= 256 * 1024:
            raise ValueError("Invalid request size or key")
        request_json = canonical_request.decode("utf-8")
        fingerprint = sha256(canonical_request).hexdigest()
        uri = self.database.absolute().as_uri() + "?mode=rw"
        with closing(sqlite3.connect(uri, uri=True, timeout=5)) as connection, connection:
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                """SELECT transaction_id, request_fingerprint, transaction_state FROM transactions
                   WHERE authenticated_principal = ? AND idempotency_key = ?""",
                (authenticated_sid, key),
            ).fetchone()
            if row is not None:
                transaction_id, existing, state = row
                if existing != fingerprint:
                    raise IdempotencyConflict("Idempotency key already binds a different request")
                return Receipt(transaction_id, state)
            receipt = Receipt(uuid4().hex, "REQUEST_ACCEPTED")
            connection.execute(
                "INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?)",
                (receipt.transaction_id, authenticated_sid, key, fingerprint, request_json,
                 receipt.state, datetime.now(timezone.utc).isoformat()),
            )
            return receipt
