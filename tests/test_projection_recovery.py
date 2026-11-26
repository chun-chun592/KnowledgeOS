from dataclasses import replace
from hashlib import sha256
import os

from projection_recovery import FileEvidence, PreparedProjection, identity, reconcile


def test_reconcile_actual_file_identity_and_digest(tmp_path):
    parent = tmp_path / "wiki"
    parent.mkdir()
    target = parent / "note.md"
    stage = parent / "note.stage"
    target.write_bytes(b"old")
    stage.write_bytes(b"new")
    request = b'{"operation":"knowledge.update"}'

    def evidence(path):
        return FileEvidence(identity(path.stat()), sha256(path.read_bytes()).hexdigest())

    receipt = PreparedProjection(
        "wiki/note.md", "wiki/note.stage", identity(tmp_path.stat()), identity(parent.stat()),
        sha256(request).hexdigest(), evidence(target), evidence(stage),
    )
    assert reconcile(tmp_path, receipt, request) == "PREPARED"
    assert reconcile(tmp_path, receipt, b"changed") == "NEEDS_REVIEW"
    assert reconcile(tmp_path, replace(receipt, target="../note.md"), request) == "NEEDS_REVIEW"
    target.write_bytes(b"external edit")
    assert reconcile(tmp_path, receipt, request) == "NEEDS_REVIEW"
    assert target.read_bytes() == b"external edit"
    # Simulate the on-disk shape after a previously authorized replace.
    os.replace(stage, target)
    assert reconcile(tmp_path, receipt, request) == "PROJECTED"
    assert reconcile(tmp_path, receipt, request) == "PROJECTED"
    os.rename(target, parent / "original-object.md")
    target.write_bytes(b"new")
    assert reconcile(tmp_path, receipt, request) == "NEEDS_REVIEW"


def test_multiple_hard_links_require_review(tmp_path):
    target, stage = tmp_path / "new.md", tmp_path / "new.stage"
    stage.write_bytes(b"new")
    request = b'{"operation":"knowledge.new"}'
    root_id = identity(tmp_path.stat())
    receipt = PreparedProjection(
        target.name, stage.name, root_id, root_id, sha256(request).hexdigest(), None,
        FileEvidence(identity(stage.stat()), sha256(b"new").hexdigest()),
    )
    assert reconcile(tmp_path, receipt, request) == "PREPARED"
    os.link(stage, target)
    assert reconcile(tmp_path, receipt, request) == "NEEDS_REVIEW"
