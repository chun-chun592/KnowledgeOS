from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest

from ledger_admission import AdmissionLedger, IdempotencyConflict


SID = "S-1-5-21-11-22-33-1001"
REQUEST = b'{"operation":"knowledge.new"}'


def test_concurrent_replay_and_principal_binding(tmp_path):
    database = tmp_path / "ledger.sqlite3"
    ledger = AdmissionLedger(database)
    ledger.initialize()
    with ThreadPoolExecutor(max_workers=8) as pool:
        receipts = list(pool.map(lambda _: ledger.accept(SID, "key", REQUEST), range(24)))
    assert len(set(receipts)) == 1
    assert receipts[0].state == "REQUEST_ACCEPTED"
    with pytest.raises(IdempotencyConflict):
        ledger.accept(SID, "key", b'{"operation":"knowledge.update"}')
    assert ledger.accept("S-1-5-21-11-22-33-1002", "key", REQUEST) != receipts[0]
    with closing(sqlite3.connect(database)) as con:
        assert con.execute("SELECT count(*) FROM transactions").fetchone() == (2,)


def test_process_exit_rolls_back_incomplete_admission(tmp_path):
    database = tmp_path / "ledger.sqlite3"
    ledger = AdmissionLedger(database)
    ledger.initialize()
    acknowledged = ledger.accept(SID, "acknowledged", REQUEST)
    script = """
import os, sqlite3, sys
con = sqlite3.connect(sys.argv[1])
con.execute('PRAGMA cache_size=1')
con.execute('PRAGMA synchronous=FULL')
con.execute('BEGIN IMMEDIATE')
con.execute('INSERT INTO transactions SELECT ?, authenticated_principal, ?, request_fingerprint, ?, transaction_state, accepted_utc FROM transactions',
            ('unacknowledged', 'pending', 'x' * 60000))
os._exit(83)
"""
    result = subprocess.run([sys.executable, "-B", "-c", script, str(database)], timeout=15)
    assert result.returncode == 83
    assert AdmissionLedger(database).accept(SID, "acknowledged", REQUEST) == acknowledged
    with closing(sqlite3.connect(database)) as con:
        assert con.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert con.execute("SELECT transaction_id FROM transactions").fetchone() == (acknowledged.transaction_id,)
        assert con.execute("SELECT count(*) FROM transactions").fetchone() == (1,)
