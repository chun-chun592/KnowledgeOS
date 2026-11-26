"""Vault path handling, atomic writes, backups and cooperative locks.

Security notes
--------------
Every path used for a write is normalized, checked for ``..`` components, checked for
symlinks/junctions in every existing component, and resolved inside the vault root.
This is a *tool-level* control: a process that ignores the CLI can still write to the vault.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import stat
import threading
import time
import uuid
from contextlib import ExitStack, contextmanager, nullcontext
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Iterator, Sequence

from .config import Config, load_config
from .errors import ConflictError, PathSecurityError, VaultStructureError

if TYPE_CHECKING:
    from .schema import Document


PROTECTED_DIR_NAMES = frozenset({".git", ".obsidian", ".knowledgeos", ".trash", ".hilighter"})
_PROTECTED_FOLDED = frozenset(name.casefold() for name in PROTECTED_DIR_NAMES)
BACKUP_DIR = Path(".knowledgeos") / "backups"
LOCK_DIR = Path(".knowledgeos") / "locks"
LOCK_GUARD_DIR = Path(".knowledgeos") / "lock-guards"
MAX_BACKUP_RUNS = 25
WINDOWS_TRANSACTION_PATH_UNITS = 1024


def _validate_windows_transaction_path(path: Path) -> None:
    if len(str(path).encode("utf-16-le")) // 2 > WINDOWS_TRANSACTION_PATH_UNITS:
        raise PathSecurityError(f"Windows transaction path exceeds the supported {WINDOWS_TRANSACTION_PATH_UNITS} UTF-16 units.")


def _is_link_like(path: Path) -> bool:
    """True for symlinks and (on Windows) junctions / reparse points."""
    try:
        if path.is_symlink():
            return True
    except OSError:
        return True
    try:
        info = path.lstat()
    except OSError:
        return False
    if os.name == "nt":
        if getattr(info, "st_reparse_tag", 0):
            return True
        attributes = getattr(info, "st_file_attributes", 0) or 0
        return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))
    return stat.S_ISLNK(info.st_mode)


def _reject_windows_stream(path: Path) -> None:
    if os.name == "nt" and any(":" in part for part in path.parts):
        parts = path.parts[1:] if path.anchor else path.parts
        if any(":" in part for part in parts) or (path.drive and not path.root):
            raise PathSecurityError("Windows alternate data streams and drive-relative paths are not allowed.")


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        pass
    if os.name == "nt":
        child_s = os.path.normcase(os.path.abspath(str(child)))
        parent_s = os.path.normcase(os.path.abspath(str(parent)))
        return child_s == parent_s or child_s.startswith(parent_s + os.sep)
    return False


def _has_parent_reference(value: str) -> bool:
    normalized = value.replace("\\", "/")
    return any(part == ".." for part in normalized.split("/"))


@dataclass(frozen=True)
class Vault:
    """A configured vault root with safe path helpers."""

    root: Path
    config: Config

    @classmethod
    def load(
        cls,
        vault: str | Path | None = None,
        config_path: str | Path | None = None,
        agent_id: str | None = None,
    ) -> "Vault":
        configured = config_path or os.environ.get("KNOWLEDGEOS_CONFIG", "").strip()
        if vault is not None:
            supplied = Path(vault).expanduser()
        elif configured:
            directory = Path(configured).expanduser().parent
            supplied = directory.parent if directory.name == ".knowledgeos" else directory
        else:
            environment_vault = os.environ.get("KNOWLEDGEOS_VAULT", "").strip()
            supplied = Path(environment_vault).expanduser() if environment_vault else Path.cwd()
        _reject_windows_stream(supplied)
        absolute = supplied.absolute()
        for component in (absolute, *absolute.parents):
            if _is_link_like(component):
                raise PathSecurityError(f"Vault root path contains a symbolic link or reparse point: {component}")
        config = load_config(vault, config_path, agent_id)
        if not config.vault.is_dir():
            raise VaultStructureError(f"Vault root is not a directory: {config.vault}")
        return cls(root=config.vault, config=config)

    # ------------------------------------------------------------------
    # Path normalization
    # ------------------------------------------------------------------
    def relative(self, path: str | Path) -> str:
        """Return the POSIX vault-relative path after a security check."""
        absolute = self.resolve(path)
        return absolute.relative_to(self.root).as_posix()

    def resolve(self, path: str | Path, *, for_write: bool = False) -> Path:
        """Normalize *path* and prove it stays inside the vault.

        Raises:
            PathSecurityError: on traversal, symlink/junction, protected directory,
                or an absolute path outside the vault.
        """
        raw = str(path).strip()
        if not raw:
            raise PathSecurityError("Empty path is not allowed.")
        if _has_parent_reference(raw):
            raise PathSecurityError(f"Path traversal ('..') is not allowed: {raw}")

        expanded = os.path.expandvars(os.path.expanduser(raw))
        candidate = Path(expanded)
        _reject_windows_stream(candidate)
        if not candidate.is_absolute():
            candidate = self.root / candidate

        try:
            lexical = Path(os.path.abspath(os.path.normpath(str(candidate))))
        except (OSError, ValueError) as exc:
            raise PathSecurityError(f"Invalid path: {raw}") from exc

        if not _is_within(lexical, self.root):
            raise PathSecurityError(f"Path escapes the vault: {raw}")

        # Reject links anywhere in the existing chain, even if they point inside.
        self._reject_links(lexical)

        try:
            resolved = lexical if os.name == "nt" else lexical.resolve(strict=False)
        except (OSError, RuntimeError) as exc:
            raise PathSecurityError(f"Cannot resolve path: {raw}") from exc
        if not _is_within(resolved, self.root):
            raise PathSecurityError(f"Path resolves outside the vault: {raw}")

        relative = resolved.relative_to(self.root)
        if relative.parts and relative.parts[0].casefold() in _PROTECTED_FOLDED:
            raise PathSecurityError(
                f"Refusing to operate on protected directory '{relative.parts[0]}'."
            )
        if for_write and relative.suffix.lower() in {".lnk", ".url"}:
            raise PathSecurityError("Refusing to write shortcut files.")

        return resolved

    def _reject_links(self, absolute: Path) -> None:
        try:
            relative = absolute.relative_to(self.root)
        except ValueError as exc:
            raise PathSecurityError(f"Path escapes the vault: {absolute}") from exc
        current = self.root
        for component in relative.parts:
            current = current / component
            if not (current.exists() or current.is_symlink()):
                continue
            if _is_link_like(current):
                raise PathSecurityError(
                    "Symbolic links and junctions are not allowed inside the vault: "
                    f"{current.relative_to(self.root).as_posix()}"
                )

    def is_protected(self, path: str | Path) -> bool:
        try:
            relative = self.resolve(path).relative_to(self.root)
        except PathSecurityError:
            return True
        return bool(relative.parts and relative.parts[0].casefold() in _PROTECTED_FOLDED)

    def region_of(self, path: str | Path) -> str:
        """Return the ownership region name for a path (no policy decision)."""
        relative = self.resolve(path).relative_to(self.root).as_posix()
        first = relative.split("/", 1)[0]
        cfg = self.config
        if first.casefold() in _PROTECTED_FOLDED:
            return "protected"
        if first == cfg.human_dir:
            return "human"
        if first == cfg.agent_dir:
            rest = relative[len(cfg.agent_dir) :].lstrip("/")
            if rest.startswith(cfg.raw_subdir + "/"):
                return "agent_raw"
            if rest.startswith(cfg.wiki_subdir + "/"):
                return "agent_wiki"
            return "agent"
        if first == cfg.exchange_dir:
            rest = relative[len(cfg.exchange_dir) :].lstrip("/")
            sub = rest.split("/", 1)[0]
            if sub in {"human-to-agent", "agent-to-human", "agent-to-agent", "write-requests", "locks"}:
                return f"exchange:{sub}"
            return "exchange"
        if first == cfg.system_dir:
            return "system"
        if first == cfg.archive_dir:
            return "archive"
        if relative == "AGENTS.md":
            return "system"
        return "unknown"

    def display(self, path: str | Path) -> str:
        """Vault-relative display path; never leaks an absolute local path."""
        try:
            return self.resolve(path).relative_to(self.root).as_posix()
        except (PathSecurityError, ValueError):
            return str(path)

    # ------------------------------------------------------------------
    # I/O
    # ------------------------------------------------------------------
    def read_text(self, path: str | Path) -> str:
        return self.read_bytes(path).decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")

    def read_bytes(self, path: str | Path) -> bytes:
        return self._read_bytes(self.resolve(path))

    def read_document(self, path: Path) -> Document:
        from .schema import parse_text

        target = self.resolve(path)
        text = self._read_bytes(target).decode("utf-8-sig")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        return parse_text(text, target, target.relative_to(self.root).as_posix())

    def _read_bytes(self, path: Path) -> bytes:
        if os.name == "nt":
            from ._windows_fs import read_bytes

            return read_bytes(path)
        return path.read_bytes()

    def write_text(
        self,
        path: str | Path,
        text: str,
        *,
        backup: bool = True,
        encoding: str = "utf-8",
        expected_sha256: str | None = None,
        expected_parent: tuple[int, str] | None = None,
        expected_old_id: str | None = None,
        record_stage: Callable[[str, str], None] | None = None,
        existing_stage: tuple[str, str] | None = None,
    ) -> Path:
        """Atomically replace a file. Callers must consult :mod:`policy` first."""
        from .errors import PermissionDenied as LegacyWriteDenied
        raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")
        target = self.resolve(path, for_write=True)
        if os.name == "nt":
            from ._windows_fs import file_snapshot, publish_internal

            if expected_old_id is None:
                try:
                    observed_parent, observed_id, original = file_snapshot(target)
                except FileNotFoundError:
                    observed_parent, observed_id, original = None, None, None
                if original is None:
                    if expected_sha256 is not None:
                        raise ConflictError("The expected replacement target is missing.")
                    return self._create_bytes(target, text.encode(encoding), expected_parent=observed_parent)
                expected_parent = expected_parent or observed_parent
                expected_old_id = observed_id
                if expected_sha256 is None:
                    expected_sha256 = hashlib.sha256(original).hexdigest()
            if backup:
                self.backup(target)
            deadline = time.monotonic() + min(self.config.lock_timeout, 2.0)
            publish_internal(
                target, f".publish.{uuid.uuid4().hex}.tmp", text.encode(encoding), deadline,
                replace=True, expected_sha256=expected_sha256,
                expected_parent=expected_parent, expected_old_id=expected_old_id,
                record_stage=record_stage, existing_stage=existing_stage,
            )
            return target
        if expected_sha256 is not None and hashlib.sha256(self._read_bytes(target)).hexdigest() != expected_sha256:
            raise ConflictError("The original file changed before replacement.")
        target.parent.mkdir(parents=True, exist_ok=True)
        return self._replace_text(target, text, backup=backup, encoding=encoding)

    def _replace_text(self, target: Path, text: str, *, backup: bool, encoding: str) -> Path:
        from .errors import PermissionDenied as LegacyWriteDenied
        raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")
        if target.exists():
            if target.is_dir():
                raise ConflictError(f"Target is a directory: {self.display(target)}")
            if backup:
                self.backup(target)
        temp = target.with_name(f".{target.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
        handle = temp.open("x", encoding=encoding, newline="\n")
        try:
            with handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, target)
        finally:
            if temp.exists():
                try:
                    temp.unlink()
                except OSError:
                    pass
        return target

    def create_bytes(
        self, path: str | Path, data: bytes, *,
        expected_parent: tuple[int, str] | None = None,
        record_stage: Callable[[str, str], None] | None = None,
        existing_stage: tuple[str, str] | None = None,
    ) -> Path:
        """Publish a complete file only if its destination is absent."""
        from .errors import PermissionDenied as LegacyWriteDenied
        raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")
        return self._create_bytes(self.resolve(path, for_write=True), data,
                                  expected_parent=expected_parent, record_stage=record_stage,
                             existing_stage=existing_stage)

    def create_internal_bytes(self, path: Path, data: bytes) -> Path:
        from .errors import PermissionDenied as LegacyWriteDenied
        raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")
        if os.name == "nt":
            from ._windows_fs import publish_internal

            target = self._windows_internal_target(path)
            publish_internal(target, f".publish.{uuid.uuid4().hex}.tmp", data, time.monotonic(), replace=False)
            return target
        return self._create_bytes(self.internal_path(path), data)

    def read_internal_bytes(self, path: Path) -> bytes:
        if os.name == "nt":
            from ._windows_fs import read_internal

            return read_internal(self._windows_internal_target(path))
        return self.internal_path(path).read_bytes()

    def delete_internal_file(self, path: Path) -> None:
        from .errors import PermissionDenied as LegacyWriteDenied
        raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")
        if os.name == "nt":
            from ._windows_fs import delete_internal

            delete_internal(self._windows_internal_target(path))
        else:
            self.internal_path(path).unlink()

    def write_internal_bytes(self, path: Path, data: bytes, *, transaction_state: bool = False) -> Path:
        """Atomically replace a file inside ``.knowledgeos`` (temp + replace).

        Transaction state files are updated in place as an operation advances;
        ``create_internal_bytes`` cannot do that because it refuses to overwrite.
        Transaction callers opt in to the native path budget; the legacy
        general-purpose state writer retains its 259-unit boundary.
        """
        from .errors import PermissionDenied as LegacyWriteDenied
        raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")
        if os.name == "nt":
            from ._windows_fs import replace_state

            target = self._windows_internal_target(path) if transaction_state else self.internal_path(path)
            if not transaction_state and len(str(target).encode("utf-16-le")) >= 520:
                raise PathSecurityError("Windows internal state destination exceeds the supported 259 UTF-16 units.")
            deadline = time.monotonic() + min(self.config.lock_timeout, 2.0)
            replace_state(target, f".state.{uuid.uuid4().hex}.tmp", data, deadline)
            return target
        target = self.internal_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        return self._replace_internal_bytes(target, data)

    def _replace_internal_bytes(self, target: Path, data: bytes) -> Path:
        from .errors import PermissionDenied as LegacyWriteDenied
        raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")
        temp = target.with_name(f".state.{uuid.uuid4().hex}.tmp")
        handle = temp.open("xb")
        try:
            with handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, target)
        finally:
            if temp.exists():
                try:
                    temp.unlink()
                except OSError:
                    pass
        return target

    def _create_bytes(
        self, target: Path, data: bytes, *,
        expected_parent: tuple[int, str] | None = None,
        record_stage: Callable[[str, str], None] | None = None,
        existing_stage: tuple[str, str] | None = None,
    ) -> Path:
        from .errors import PermissionDenied as LegacyWriteDenied
        raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")
        if os.name == "nt":
            from ._windows_fs import publish_internal

            deadline = time.monotonic() + min(self.config.lock_timeout, 2.0)
            publish_internal(target, f".publish.{uuid.uuid4().hex}.tmp", data, deadline, replace=False,
                             expected_parent=expected_parent, record_stage=record_stage,
                             existing_stage=existing_stage)
            return target
        target.parent.mkdir(parents=True, exist_ok=True)
        return self._publish_new_bytes(target, data)

    def _publish_new_bytes(self, target: Path, data: bytes) -> Path:
        from .errors import PermissionDenied as LegacyWriteDenied
        raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")
        temp = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
        handle = temp.open("xb")
        try:
            with handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(temp, target)
            except FileExistsError as exc:
                raise ConflictError(f"Target already exists: {self.display(target)}") from exc
        finally:
            temp.unlink(missing_ok=True)
        return target

    def _internal_target(self, relative: Path) -> Path:
        _reject_windows_stream(relative)
        if relative.is_absolute() or relative.parts[:1] != (".knowledgeos",) or ".." in relative.parts:
            raise PathSecurityError("Invalid KnowledgeOS internal path.")
        return self.root / relative

    def _windows_internal_target(self, relative: Path) -> Path:
        target = self._internal_target(relative)
        _validate_windows_transaction_path(target)
        return target

    def internal_path(self, relative: Path) -> Path:
        """Resolve a caller-owned internal path without accepting reparse points."""
        target = self._internal_target(relative)
        self._reject_links(target)
        return target

    def ensure_dir(self, path: str | Path) -> Path:
        from .errors import PermissionDenied as LegacyWriteDenied
        raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")
        target = self.resolve(path, for_write=True)
        target.mkdir(parents=True, exist_ok=True)
        return target

    def backup(self, path: str | Path, *, operation_id: str | None = None) -> Path:
        """Copy an existing file into ``.knowledgeos/backups/<stamp>/<rel>``."""
        from .errors import PermissionDenied as LegacyWriteDenied
        raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")
        source = self.resolve(path)
        if not source.exists():
            raise FileNotFoundError(self.display(source))
        stamp = datetime.now().strftime("%Y%m%dT%H%M%S") + f"-{uuid.uuid4().hex[:6]}"
        relative = source.relative_to(self.root)
        backup_relative = BACKUP_DIR / stamp / relative
        original = self._read_bytes(source)
        with self.lock("backup-retention") if os.name == "nt" else nullcontext():
            if os.name == "nt":
                from ._windows_fs import file_snapshot

                published_id = None

                def capture_id(_name: str, file_id: str) -> None:
                    nonlocal published_id
                    published_id = file_id

                destination = self._create_bytes(self._windows_internal_target(backup_relative),
                                                 original, record_stage=capture_id)
                _, file_id, verified = file_snapshot(destination)
                if file_id != published_id:
                    raise ConflictError("Backup object changed before verification.")
            else:
                destination = self.create_internal_bytes(backup_relative, original)
                verified = self.read_internal_bytes(backup_relative)
            if verified != original:
                raise ConflictError("Backup verification failed.")
            if os.name == "nt":
                receipt = {"version": 1, "path": relative.as_posix(), "file_id": file_id,
                           "sha256": hashlib.sha256(original).hexdigest(), "operation_id": operation_id}
                self.create_internal_bytes(BACKUP_DIR / stamp / ".receipt.json", json.dumps(receipt).encode("utf-8"))
                self._prune_windows_backups(current_run=stamp)
            else:
                self._prune_backups()
            return destination

    def _prune_backups(self) -> None:
        from .errors import PermissionDenied as LegacyWriteDenied
        raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")
        if os.name == "nt":
            with self.lock("backup-retention"):
                self._prune_windows_backups()
            return
        base = self.internal_path(BACKUP_DIR)
        if not base.is_dir():
            return
        runs = sorted((entry for entry in base.iterdir() if entry.is_dir() and not _is_link_like(entry)), reverse=True)
        for old in runs[MAX_BACKUP_RUNS:]:
            for child in sorted(old.rglob("*"), reverse=True):
                try:
                    child.unlink() if child.is_file() else child.rmdir()
                except OSError:
                    pass
            try:
                old.rmdir()
            except OSError:
                pass

    def _prune_windows_backups(self, *, current_run: str | None = None) -> None:
        from .errors import PermissionDenied as LegacyWriteDenied
        raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")

    def lock(self, name: str) -> "FileLock":
        return FileLock(self, name)

    @contextmanager
    def note_lock(self, path: Path) -> Iterator[None]:
        target = self.resolve(path)
        if os.name != "nt":
            with self.lock(f"note:{self.display(target)}"):
                yield
            return
        from ._windows_fs import bound_parent, note_parent_key, validate_note_target

        with ExitStack() as stack:
            try:
                parent, volume = stack.enter_context(bound_parent(target))
            except FileNotFoundError as exc:
                raise PathSecurityError("Windows note writes require an existing destination directory.") from exc
            key = note_parent_key(parent, target)
            with self.lock(key):
                if note_parent_key(parent, target) != key:
                    raise PathSecurityError("Windows note parent identity changed while waiting for its lock.")
                validate_note_target(parent, target, volume)
                yield

    def iter_markdown(self, regions: Sequence[str] | None = None) -> Iterator[Path]:
        """Yield Markdown files in the requested regions (default: human + agent)."""
        selected = list(regions) if regions else ["human", "agent"]
        roots = self._region_roots(selected)
        seen: set[Path] = set()
        for base in roots:
            if not base.exists() or not base.is_dir():
                continue
            try:
                self.resolve(base)
            except PathSecurityError:
                continue
            for dirpath, dirnames, filenames in os.walk(base, followlinks=False):
                dirnames[:] = sorted(
                    name for name in dirnames
                    if not name.startswith(".") and not _is_link_like(Path(dirpath) / name)
                )
                for filename in sorted(filenames):
                    if not filename.lower().endswith(".md"):
                        continue
                    candidate = Path(dirpath) / filename
                    try:
                        resolved = self.resolve(candidate)
                    except (OSError, PathSecurityError):
                        continue
                    if resolved in seen:
                        continue
                    seen.add(resolved)
                    yield resolved

    def _region_roots(self, regions: Sequence[str]) -> list[Path]:
        cfg = self.config
        mapping: dict[str, list[Path]] = {
            "human": [cfg.human_path],
            "agent": [cfg.agent_path],
            "agent_raw": [cfg.raw_path],
            "agent_wiki": [cfg.wiki_path],
            "exchange": [cfg.exchange_path],
            "system": [cfg.system_path],
            "archive": [cfg.archive_path],
            "all": [cfg.human_path, cfg.agent_path, cfg.exchange_path, cfg.system_path, cfg.archive_path],
        }
        roots: list[Path] = []
        for region in regions:
            if region not in mapping:
                raise ValueError(
                    f"Unknown region {region!r}. Use: {', '.join(sorted(mapping))}."
                )
            roots.extend(mapping[region])
        return roots


def _process_start(pid: int) -> tuple[bool, int | None]:
    """Return whether a process might be alive and its Windows creation time."""
    if pid <= 0:
        return False, None
    if os.name != "nt":
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False, None
        except PermissionError:
            pass
        return True, None

    import ctypes
    from ctypes import wintypes

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    time_pointer = ctypes.POINTER(wintypes.FILETIME)
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE] + [time_pointer] * 4
    handle = kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        # ERROR_INVALID_PARAMETER indicates there is no such process.
        return ctypes.get_last_error() != 87, None
    try:
        created, exited, kernel_time, user_time = (wintypes.FILETIME() for _ in range(4))
        if not kernel.GetProcessTimes(handle, created, exited, kernel_time, user_time):
            return True, None
        stamp = (created.dwHighDateTime << 32) | created.dwLowDateTime
        return not (exited.dwHighDateTime or exited.dwLowDateTime), stamp
    finally:
        kernel.CloseHandle(handle)


@dataclass(frozen=True)
class LockInspection:
    """Facts about an existing lock file, used for reclaim decisions.

    ``orphan`` means the recorded owner is provably gone (process absent, or
    the PID now belongs to a different process) and the lock may be reclaimed
    immediately. ``active`` means the recorded owner is (probably) alive and
    must never be displaced. Everything else is *unattributable*: cooperative
    writers only reclaim it after ``lock_stale_after``.
    """

    path: Path
    readable: bool  # False: the file vanished or could not be opened at all
    attributable: bool  # payload parsed and carries a positive integer PID
    corrupt: bool  # file exists but the payload is not a valid lock object
    pid: int | None
    owner: str | None
    acquired: str | None
    recorded_start: int | None
    alive: bool  # only meaningful when attributable
    pid_reused: bool  # a different process now owns the recorded PID
    age_seconds: float
    token: str | None = None

    @property
    def orphan(self) -> bool:
        return self.attributable and (not self.alive or self.pid_reused)

    @property
    def active(self) -> bool:
        return self.attributable and self.alive and not self.pid_reused


def inspect_lock_file(path: Path) -> LockInspection:
    """Inspect a lock file without modifying it (used by FileLock and doctor)."""
    try:
        age = max(0.0, time.time() - path.stat().st_mtime)
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return LockInspection(path=path, readable=False, attributable=False, corrupt=False,
                              pid=None, owner=None, acquired=None, recorded_start=None,
                              alive=False, pid_reused=False, age_seconds=0.0)
    return _inspect_lock_text(path, raw, age)


def _inspect_lock_text(path: Path, raw: str, age: float) -> LockInspection:
    payload: dict = {}
    corrupt = False
    try:
        parsed = json.loads(raw)
    except ValueError:
        corrupt = True
    else:
        if isinstance(parsed, dict):
            payload = parsed
        else:
            corrupt = True
    pid = payload.get("pid")
    attributable = isinstance(pid, int) and not isinstance(pid, bool) and pid > 0
    alive = False
    pid_reused = False
    recorded_start = payload.get("process_start")
    if isinstance(recorded_start, bool) or not isinstance(recorded_start, int):
        recorded_start = None
    if attributable:
        alive, live_start = _process_start(pid)
        if alive and recorded_start is not None and live_start is not None \
                and recorded_start != live_start:
            pid_reused = True
    return LockInspection(
        path=path,
        readable=True,
        attributable=attributable,
        corrupt=corrupt,
        pid=pid if attributable else None,
        owner=payload.get("owner") if isinstance(payload.get("owner"), str) else None,
        acquired=payload.get("acquired") if isinstance(payload.get("acquired"), str) else None,
        recorded_start=recorded_start,
        alive=alive,
        pid_reused=pid_reused,
        age_seconds=age,
        token=payload.get("token") if isinstance(payload.get("token"), str) else None,
    )


def _reclaimable(state: LockInspection, stale_after: float) -> bool:
    """Whether a blocked acquirer may remove this lock right now."""
    if state.orphan:
        return True  # TXN-2: the owner is provably dead; no waiting.
    if not state.attributable:
        return state.age_seconds > stale_after  # corrupt/legacy: conservative.
    return False  # active owner: protected, never reclaimed here.


class FileLock:
    """A cooperative, cross-process lock using O_EXCL creation.

    This prevents two cooperating agents from interleaving index/log writes.
    It is not an OS advisory lock and cannot stop a process that ignores it.

    Reclamation rules (Phase 4 Work Block 1, TXN-2):

    - The recorded owner PID is checked *before* any staleness judgement.
      A lock whose owner process is provably dead is reclaimed immediately,
      which removes the former 300 s (`lock_stale_after`) blocking window
      after every hard crash (Phase 3 P0-C / W10).
    - PID reuse is detected via the recorded process creation time: if a
      different process now owns the PID, the original owner is considered
      gone and the lock is reclaimed.
    - A lock whose owner is (probably) alive is never reclaimed, no matter
      how old its mtime looks.
    - A lock without a verifiable owner (corrupt payload, empty file, or a
      legacy payload without a PID) can only be reclaimed after
      ``lock_stale_after``; ``doctor`` reports such locks explicitly with a
      manual-recovery hint.
    """

    def __init__(self, vault: Vault, name: str, timeout: float | None = None) -> None:
        self.vault = vault
        self.name = name
        self.timeout = vault.config.lock_timeout if timeout is None else timeout
        safe = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in name)[:80]
        self.path = vault.internal_path(LOCK_DIR / f"{safe}.lock")
        self._owned = False
        self._token = uuid.uuid4().hex
        self._native = ExitStack()
        self._exit_lock = threading.Lock()
        self._marker_parent: int | None = None
        self._marker_witness: int | None = None

    def __enter__(self) -> "FileLock":
        from .errors import PermissionDenied as LegacyWriteDenied
        raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")
        deadline = time.monotonic() + self.timeout
        with ExitStack() as stack:
            if os.name == "nt":
                from ._windows_fs import bound_parent, exclusive_lock

                guard = self.vault.internal_path(LOCK_GUARD_DIR / self.path.with_suffix(".guard").name)
                try:
                    stack.enter_context(exclusive_lock(guard, deadline))
                except ConflictError as exc:
                    try:
                        blocker = inspect_lock_file(self.path)
                    except OSError:
                        blocker = None
                    raise ConflictError(self._timeout_message(blocker, self.vault.config.lock_stale_after)) from exc
                self._marker_parent, _ = stack.enter_context(bound_parent(self.path, create=True))
            self._token = uuid.uuid4().hex
            self._acquire_marker(deadline, stack)
            self._native = stack.pop_all()
        return self

    def _acquire_marker(self, deadline: float, stack: ExitStack) -> "FileLock":
        from .errors import PermissionDenied as LegacyWriteDenied
        raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")
        if self._marker_parent is None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        else:
            from ._windows_fs import create_marker, marker_witness
        stale_after = self.vault.config.lock_stale_after
        blocker: LockInspection | None = None
        while True:
            self.vault.internal_path(self.path.relative_to(self.vault.root))
            try:
                if self._marker_parent is None:
                    descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                else:
                    descriptor = create_marker(self._marker_parent, self.path.name)
            except (FileExistsError, PermissionError):
                pass
            else:
                payload = {
                    "lock": True,
                    "name": self.name,
                    "owner": self.vault.config.agent_id,
                    "pid": os.getpid(),
                    "process_start": _process_start(os.getpid())[1],
                    "token": self._token,
                    "acquired": datetime.now().astimezone().isoformat(timespec="seconds"),
                }
                try:
                    # Write the payload through the raw descriptor: a process
                    # killed right after acquisition still leaves an
                    # attributable lock (owner PID readable) instead of an
                    # empty file that would block writers for stale_after.
                    os.write(descriptor, json.dumps(payload, ensure_ascii=False).encode("utf-8"))
                    os.fsync(descriptor)
                    if self._marker_parent is not None:
                        self._marker_witness = marker_witness(descriptor, stack)
                finally:
                    os.close(descriptor)
                verification = inspect_lock_file(self.path)
                expected = payload["process_start"]
                if (not verification.readable or verification.pid != payload["pid"]
                        or verification.recorded_start != expected or verification.token != self._token):
                    raise ConflictError(
                        f"Lock '{self.name}' changed immediately after acquisition; "
                        "another process may be manipulating lock files. Nothing was "
                        "written under this lock. Inspect "
                        f"{self.path.relative_to(self.vault.root).as_posix()}."
                    )
                self._owned = True
                return self
            try:
                blocker = inspect_lock_file(self.path)
            except OSError:
                blocker = None  # momentarily unreadable (Windows delete-pending)
            if blocker is None or not blocker.readable:
                # The lock vanished or cannot be inspected right now (owner
                # released it, a reclaimer moved it, or Windows still reports
                # a sharing violation): retry the create instead of guessing.
                if time.monotonic() >= deadline:
                    raise ConflictError(self._timeout_message(None, stale_after))
                time.sleep(0.05)
                continue
            if _reclaimable(blocker, stale_after) and self._steal():
                continue
            if time.monotonic() >= deadline:
                raise ConflictError(self._timeout_message(blocker, stale_after))
            time.sleep(0.05)

    def _steal(self) -> bool:
        """Move a reclaimable lock aside atomically, then delete it.

        ``os.rename`` has a single winner, so concurrent reclaimers of the
        same orphan lock cannot end up with two owners: losers observe
        ``FileNotFoundError`` and simply retry the create. If the quarantine
        copy cannot be deleted (rare sharing violation) it stays behind as an
        inert ``*.orphan`` file that ``doctor`` reports.
        """
        from .errors import PermissionDenied as LegacyWriteDenied
        raise LegacyWriteDenied("LEGACY_WRITE_DISABLED: use the Broker-backed client")
        if self._marker_parent is not None:
            from ._windows_fs import reclaim_marker

            def reclaimable(data: bytes, age: float) -> bool:
                state = _inspect_lock_text(self.path, data.decode("utf-8", errors="replace"), age)
                return _reclaimable(state, self.vault.config.lock_stale_after)

            return reclaim_marker(self._marker_parent, self.path.name, reclaimable)
        quarantine = self.path.with_name(f"{self.path.name}.{uuid.uuid4().hex[:8]}.orphan")
        try:
            os.rename(self.path, quarantine)
        except FileNotFoundError:
            return True  # someone else reclaimed it first
        except OSError:
            return False  # transient sharing violation; re-inspect and retry
        try:
            quarantine.unlink()
        except OSError:
            pass  # quarantined but undeletable; doctor flags it
        return True

    def _timeout_message(self, state: "LockInspection | None", stale_after: float) -> str:
        base = f"Could not acquire lock '{self.name}' within {self.timeout:g}s."
        if state is None or not state.readable:
            return base + " The lock file changed while waiting; retry the operation."
        relative = self.path.relative_to(self.vault.root).as_posix()
        if state.active:
            holder = f"pid {state.pid}"
            if state.owner:
                holder += f", owner '{state.owner}'"
            return (
                base + f" Held by a live process ({holder}; held {state.age_seconds:.0f}s). "
                "Wait for the owner to finish or investigate it before intervening. "
                f"Lock file: {relative}."
            )
        if state.orphan:
            return (
                base + f" The owner process (pid {state.pid}) is dead, but the lock file could "
                "not be removed yet (transient sharing violation). Retry; if it persists, delete "
                f"{relative} manually."
            )
        return (
            base + " The lock file has no verifiable owner (corrupt or legacy payload), so "
            f"cooperative writers reclaim it only after lock_stale_after={stale_after:g}s. To "
            "recover sooner: confirm no KnowledgeOS process is running, then delete "
            f"{relative} manually."
        )

    def __exit__(self, exc_type, exc, traceback) -> None:
        with self._exit_lock, self._native:
            self._release_marker()

    def _release_marker(self) -> None:
        if not self._owned:
            return
        if self._marker_parent is not None:
            from ._windows_fs import release_marker

            try:
                if self._marker_witness is None:
                    raise PathSecurityError("Windows lock marker identity is unavailable.")
                release_marker(self._marker_parent, self.path.name, self._marker_witness,
                               self._token, time.monotonic() + 2.0)
            finally:
                self._owned = False
            return
        try:
            self.vault.internal_path(self.path.relative_to(self.vault.root))
            owner = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            owner = None
        if not isinstance(owner, dict) or owner.get("token") != self._token:
            self._owned = False
            return
        # Release with a bounded retry: Windows may transiently refuse the
        # unlink with a sharing violation while another process (antivirus,
        # indexer, or a concurrent inspector) holds the handle. A silently
        # leaked lock would block every cooperative writer for up to
        # stale_after, so releasing must be as reliable as acquiring.
        deadline = time.monotonic() + 2.0
        while True:
            try:
                self.path.unlink()
                break
            except FileNotFoundError:
                break  # already gone
            except PermissionError:
                if time.monotonic() >= deadline:
                    break  # persistent refusal; doctor reports the residue
                time.sleep(0.02)
            except OSError:
                break
        self._owned = False


def atomic_append(vault: Vault, path: str | Path, text: str, *, lock_name: str | None = None) -> Path:
    """Append text under a lock, preserving existing content byte-for-byte."""
    target = vault.resolve(path, for_write=True)
    with vault.lock(lock_name or f"append-{target.name}"):
        try:
            original = vault.read_bytes(target)
        except FileNotFoundError:
            return vault.create_bytes(target, (text.rstrip() + "\n").encode("utf-8"))
        existing = original.decode("utf-8")
        ending = existing.replace("\r\n", "\n").replace("\r", "\n")
        separator = "" if ending.endswith("\n\n") or not ending else ("\n" if ending.endswith("\n") else "\n\n")
        return vault.write_text(
            target, existing + separator + text.rstrip() + "\n", backup=False,
            expected_sha256=hashlib.sha256(original).hexdigest(),
        )
