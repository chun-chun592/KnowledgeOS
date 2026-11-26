"""Windows handle-bound reads with non-reparse, pinned ancestors."""

from __future__ import annotations

import ctypes
import hashlib
import json
import msvcrt
import os
import time
from contextlib import ExitStack, contextmanager
from ctypes import wintypes
from pathlib import Path, PurePosixPath
from typing import Callable

from .errors import ConflictError, PathSecurityError


class FileIdInfo(ctypes.Structure):
    _fields_ = [("volume", ctypes.c_uint64), ("identifier", ctypes.c_ubyte * 16)]


class AttributeTagInfo(ctypes.Structure):
    _fields_ = [("attributes", wintypes.DWORD), ("tag", wintypes.DWORD)]


class StandardInfo(ctypes.Structure):
    _fields_ = [
        ("allocation", ctypes.c_int64), ("size", ctypes.c_int64), ("links", wintypes.DWORD),
        ("delete_pending", ctypes.c_ubyte), ("directory", ctypes.c_ubyte),
    ]


class DirectoryEntry(ctypes.Structure):
    _fields_ = [
        ("next_offset", wintypes.DWORD), ("index", wintypes.DWORD),
        ("timestamps_and_sizes", ctypes.c_int64 * 6),
        ("attributes", wintypes.DWORD), ("name_length", wintypes.DWORD),
        ("ea_size", wintypes.DWORD), ("reparse_tag", wintypes.DWORD),
        ("identifier", ctypes.c_ubyte * 16),
    ]


def directory_entries(handle: int) -> dict[str, tuple[bytes, int]]:
    """Read names and 128-bit IDs directly from the open directory."""
    entries = {}
    buffer = ctypes.create_string_buffer(65536)
    info_class = 20  # FileIdExtdDirectoryRestartInfo
    header_size = ctypes.sizeof(DirectoryEntry)
    while kernel.GetFileInformationByHandleEx(handle, info_class, buffer, len(buffer)):
        info_class = 19  # FileIdExtdDirectoryInfo
        offset = 0
        while True:
            entry = DirectoryEntry.from_buffer(buffer, offset)
            end = offset + header_size + entry.name_length
            if end > len(buffer) or entry.name_length % 2:
                raise PathSecurityError("Invalid Windows directory record.")
            name = buffer[offset + header_size:end].decode("utf-16-le")
            if name not in {".", ".."}:
                entries[name] = (bytes(entry.identifier), entry.attributes)
            if not entry.next_offset:
                break
            if entry.next_offset < header_size + entry.name_length:
                raise PathSecurityError("Invalid Windows directory record offset.")
            offset += entry.next_offset
    error = ctypes.get_last_error()
    if error != 18:  # ERROR_NO_MORE_FILES
        raise ctypes.WinError(error)
    return entries


class UnicodeString(ctypes.Structure):
    _fields_ = [("length", wintypes.USHORT), ("maximum", wintypes.USHORT), ("buffer", wintypes.LPWSTR)]


class ObjectAttributes(ctypes.Structure):
    _fields_ = [
        ("length", wintypes.ULONG), ("root", wintypes.HANDLE), ("name", ctypes.POINTER(UnicodeString)),
        ("flags", wintypes.ULONG), ("security", wintypes.LPVOID), ("quality", wintypes.LPVOID),
    ]


class IoStatusBlock(ctypes.Structure):
    _fields_ = [("status", ctypes.c_void_p), ("information", ctypes.c_size_t)]


class RenameInfo(ctypes.Structure):
    _fields_ = [
        ("replace", wintypes.DWORD), ("root", wintypes.HANDLE),
        ("name_length", wintypes.DWORD), ("name", wintypes.WCHAR * 1),
    ]


kernel = ctypes.WinDLL("kernel32", use_last_error=True)
native = ctypes.WinDLL("ntdll")
native.NtCreateFile.argtypes = [
    ctypes.POINTER(wintypes.HANDLE), wintypes.ULONG, ctypes.POINTER(ObjectAttributes),
    ctypes.POINTER(IoStatusBlock), wintypes.LPVOID, wintypes.ULONG, wintypes.ULONG,
    wintypes.ULONG, wintypes.ULONG, wintypes.LPVOID, wintypes.ULONG,
]
native.NtCreateFile.restype = wintypes.LONG
native.RtlNtStatusToDosError.argtypes = [wintypes.LONG]
native.RtlNtStatusToDosError.restype = wintypes.ULONG
native.NtSetInformationFile.argtypes = [
    wintypes.HANDLE, ctypes.POINTER(IoStatusBlock), wintypes.LPVOID, wintypes.ULONG, ctypes.c_int,
]
native.NtSetInformationFile.restype = wintypes.LONG
kernel.SetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD]
kernel.SetFileInformationByHandle.restype = wintypes.BOOL
kernel.ReOpenFile.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD]
kernel.ReOpenFile.restype = wintypes.HANDLE
kernel.GetFinalPathNameByHandleW.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
kernel.GetFinalPathNameByHandleW.restype = wintypes.DWORD
kernel.CreateFileW.argtypes = [
    wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
    wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
]
kernel.CreateFileW.restype = wintypes.HANDLE
kernel.GetFileInformationByHandleEx.argtypes = [
    wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD,
]
kernel.GetFileInformationByHandleEx.restype = wintypes.BOOL
kernel.CloseHandle.argtypes = [wintypes.HANDLE]
kernel.CloseHandle.restype = wintypes.BOOL

INVALID_HANDLE = ctypes.c_void_p(-1).value
OPEN_EXISTING = 3
OPEN_ALWAYS = 4
OPEN_REPARSE_POINT = 0x00200000
BACKUP_SEMANTICS = 0x02000000
SHARE_READ = 1
SHARE_WRITE = 2
SHARE_DELETE = 4
SHARE_ALL = SHARE_READ | SHARE_WRITE | SHARE_DELETE
DELETE_ACCESS = 0x10000
READ_ATTRIBUTES = 0x80
SYNCHRONIZE = 0x100000
NT_OPEN = 1
NT_CREATE = 2
NT_OPEN_IF = 3
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
ATTR_DIRECTORY = 0x10
ATTR_REPARSE_POINT = 0x400


def _open(path: Path, access: int, sharing: int = SHARE_READ) -> int:
    handle = kernel.CreateFileW(
        str(path), access, sharing, None, OPEN_EXISTING,
        OPEN_REPARSE_POINT | BACKUP_SEMANTICS, None,
    )
    if handle == INVALID_HANDLE:
        error = ctypes.get_last_error()
        if error in {2, 3}:
            raise FileNotFoundError(str(path))
        raise ctypes.WinError(error)
    return handle


def _identity(handle: int, *, directory: bool) -> tuple[int, bytes]:
    attributes = AttributeTagInfo()
    identity = FileIdInfo()
    for info_class, result in ((9, attributes), (18, identity)):
        if not kernel.GetFileInformationByHandleEx(handle, info_class, ctypes.byref(result), ctypes.sizeof(result)):
            raise ctypes.WinError(ctypes.get_last_error())
    if attributes.attributes & ATTR_REPARSE_POINT or bool(attributes.attributes & ATTR_DIRECTORY) != directory:
        raise PathSecurityError("Unexpected Windows object type or reparse point.")
    identifier = bytes(identity.identifier)
    if not any(identifier):
        raise PathSecurityError("Windows file identity is unavailable.")
    return identity.volume, identifier


def _leaf_bytes(name: str) -> bytes:
    if not name or name.endswith((" ", ".")) or any(ord(char) < 32 or char in '\\/:*?"<>|' for char in name):
        raise PathSecurityError("Windows relative operations require an unambiguous single component.")
    encoded = name.encode("utf-16-le")
    if len(encoded) > 510:
        raise PathSecurityError("Windows relative component exceeds 255 UTF-16 units.")
    return encoded


def _require_case_insensitive(handle: int) -> None:
    flags = wintypes.ULONG()
    if not kernel.GetFileInformationByHandleEx(handle, 23, ctypes.byref(flags), ctypes.sizeof(flags)):
        raise PathSecurityError("Windows directory case-sensitivity could not be established.") from ctypes.WinError(
            ctypes.get_last_error()
        )
    if flags.value:
        raise PathSecurityError("Windows handle-relative operations do not support case-sensitive directories.")


def _relative(parent: int, name: str, access: int, sharing: int, disposition: int, *, directory: bool = False) -> int:
    encoded = _leaf_bytes(name)
    buffer = ctypes.create_unicode_buffer(name, len(encoded) // 2 + 1)
    text = UnicodeString(len(encoded), len(encoded) + 2, ctypes.cast(buffer, wintypes.LPWSTR))
    attrs = ObjectAttributes(ctypes.sizeof(ObjectAttributes), parent, ctypes.pointer(text), 0x40, None, None)
    handle = wintypes.HANDLE()
    status = native.NtCreateFile(
        ctypes.byref(handle), access | SYNCHRONIZE, ctypes.byref(attrs), ctypes.byref(IoStatusBlock()),
        None, 0, sharing, disposition, OPEN_REPARSE_POINT | 0x20 | (1 if directory else 0x40), None, 0,
    )
    if status < 0:
        raise ctypes.WinError(native.RtlNtStatusToDosError(status))
    return handle.value


@contextmanager
def bound_parent(path: Path, *, create: bool = False):
    with ExitStack() as stack:
        root, *parents = reversed(path.parents)
        if len(root.drive) != 2 or not root.drive.endswith(":"):
            raise PathSecurityError("Windows handle-relative operations require a local drive path.")
        parent = _open(root, GENERIC_READ, SHARE_READ | SHARE_WRITE)
        stack.callback(kernel.CloseHandle, parent)
        volume, _ = _identity(parent, directory=True)
        _require_case_insensitive(parent)
        for component in parents:
            parent = _relative(
                parent, component.name, GENERIC_READ, SHARE_READ | SHARE_WRITE,
                NT_OPEN_IF if create else NT_OPEN, directory=True,
            )
            stack.callback(kernel.CloseHandle, parent)
            if _identity(parent, directory=True)[0] != volume:
                raise PathSecurityError("Windows directory chain crosses a volume.")
            _require_case_insensitive(parent)
        yield parent, volume


def _require_canonical_name(handle: int, path: Path) -> None:
    buffer = ctypes.create_unicode_buffer(32768)
    size = kernel.GetFinalPathNameByHandleW(handle, buffer, len(buffer), 0)
    if not size:
        raise ctypes.WinError(ctypes.get_last_error())
    if size >= len(buffer) or buffer.value.casefold() != ("\\\\?\\" + str(path)).casefold():
        raise PathSecurityError("Windows note writes require a canonical path; short names and other aliases are unsupported.")


def note_parent_key(parent: int, path: Path) -> str:
    _require_canonical_name(parent, path.parent)
    volume, identity = _identity(parent, directory=True)
    return f"note-dir-{volume:016x}-{identity.hex()}"


def validate_note_target(parent: int, path: Path, volume: int) -> None:
    try:
        handle = _relative(parent, path.name, READ_ATTRIBUTES, SHARE_ALL, NT_OPEN)
    except FileNotFoundError:
        return
    try:
        if _identity(handle, directory=False)[0] != volume:
            raise PathSecurityError("Windows note target crosses a volume.")
        _require_canonical_name(handle, path)
        standard = StandardInfo()
        if not kernel.GetFileInformationByHandleEx(handle, 1, ctypes.byref(standard), ctypes.sizeof(standard)):
            raise ctypes.WinError(ctypes.get_last_error())
        if standard.links != 1 or standard.delete_pending:
            raise PathSecurityError("Windows note writes require a single non-deleting link.")
    finally:
        kernel.CloseHandle(handle)


def _delete(handle: int) -> None:
    flag = ctypes.c_ubyte(1)
    if not kernel.SetFileInformationByHandle(handle, 4, ctypes.byref(flag), ctypes.sizeof(flag)):
        raise ctypes.WinError(ctypes.get_last_error())


def validate_single_link(handle: int) -> None:
    standard = StandardInfo()
    if not kernel.GetFileInformationByHandleEx(handle, 1, ctypes.byref(standard), ctypes.sizeof(standard)):
        raise ctypes.WinError(ctypes.get_last_error())
    if standard.links != 1 or standard.delete_pending:
        raise PathSecurityError("File must have a single live link.")


@contextmanager
def _open_backup_entry(parent: int, volume: int, name: str, identifier: bytes, *, directory: bool = False):
    handle = _relative(parent, name, GENERIC_READ | DELETE_ACCESS, 0, NT_OPEN, directory=directory)
    try:
        if _identity(handle, directory=directory) != (volume, identifier):
            raise PathSecurityError("Backup entry identity changed after enumeration.")
        if directory:
            _require_case_insensitive(handle)
        else:
            validate_single_link(handle)
        yield handle
    finally:
        kernel.CloseHandle(handle)


def _read_duplicated_handle(handle: int) -> bytes:
    # Duplicate the handle because the CRT owns the descriptor it opens.
    kernel.DuplicateHandle.argtypes = [
        wintypes.HANDLE, wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.HANDLE),
        wintypes.DWORD, wintypes.BOOL, wintypes.DWORD,
    ]
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    process = kernel.GetCurrentProcess()
    duplicate = wintypes.HANDLE()
    if not kernel.DuplicateHandle(process, handle, process, ctypes.byref(duplicate), 0, False, 2):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        descriptor = msvcrt.open_osfhandle(duplicate.value, os.O_RDONLY | os.O_BINARY)
    except BaseException:
        kernel.CloseHandle(duplicate)
        raise
    with os.fdopen(descriptor, "rb") as stream:
        return stream.read()


def prune_backup_run(parent: int, volume: int, name: str, identifier: bytes,
                     can_prune: Callable[[str | None], bool]) -> None:
    """Delete a recorded backup and its directories from verified handles."""
    receipt_name = ".receipt.json"
    with _open_backup_entry(parent, volume, name, identifier, directory=True) as run:
        entries = directory_entries(run)
        if receipt_name not in entries:
            raise PathSecurityError("No backup ownership receipt.")
        with _open_backup_entry(run, volume, receipt_name, entries.pop(receipt_name)[0]) as receipt_handle:
            receipt = json.loads(_read_duplicated_handle(receipt_handle))
            if not isinstance(receipt, dict) or receipt.get("version") != 1:
                raise PathSecurityError("Unsupported backup ownership receipt.")
            raw_path = receipt.get("path")
            if not isinstance(raw_path, str):
                raise PathSecurityError("Invalid receipt path.")
            path = PurePosixPath(raw_path)
            if path.is_absolute() or not path.parts:
                raise PathSecurityError("Invalid receipt path.")
            for component in path.parts:
                _leaf_bytes(component)
            owner = receipt.get("operation_id")
            if owner is not None and not isinstance(owner, str):
                raise PathSecurityError("Invalid backup operation ID.")
            if not can_prune(owner):
                return

            def prune_entry(directory: int, children: dict[str, tuple[bytes, int]], parts: tuple[str, ...]) -> None:
                leaf, *remaining = parts
                if children.keys() != {leaf}:
                    raise PathSecurityError("Unexpected backup directory contents.")
                file_id, _ = children[leaf]
                if not remaining and file_id.hex() != receipt.get("file_id"):
                    raise PathSecurityError("Backup ownership identity changed.")
                with _open_backup_entry(directory, volume, leaf, file_id, directory=bool(remaining)) as child:
                    if remaining:
                        prune_entry(child, directory_entries(child), tuple(remaining))
                    elif hashlib.sha256(_read_duplicated_handle(child)).hexdigest() != receipt.get("sha256"):
                        raise PathSecurityError("Backup contents do not match the ownership receipt.")
                    _delete(child)

            prune_entry(run, entries, path.parts)
            _delete(receipt_handle)
        _delete(run)


def _rename(handle: int, parent: int, destination: str, *, replace: bool = True) -> None:
    name = _leaf_bytes(destination)
    buffer = ctypes.create_string_buffer(max(ctypes.sizeof(RenameInfo), RenameInfo.name.offset + len(name) + 2))
    info = RenameInfo.from_buffer(buffer)
    info.replace = int(replace)
    info.root = parent
    info.name_length = len(name)
    ctypes.memmove(ctypes.addressof(buffer) + RenameInfo.name.offset, name, len(name))
    status = native.NtSetInformationFile(handle, ctypes.byref(IoStatusBlock()), buffer, len(buffer), 10)
    if status < 0:
        raise ctypes.WinError(native.RtlNtStatusToDosError(status))


def publish_internal(
    path: Path, temp_name: str, data: bytes, deadline: float, *,
    replace: bool, expected_sha256: str | None = None,
    expected_parent: tuple[int, str] | None = None,
    expected_old_id: str | None = None,
    record_stage: Callable[[str, str], None] | None = None,
    existing_stage: tuple[str, str] | None = None,
) -> None:
    _leaf_bytes(path.name)
    with bound_parent(path, create=expected_parent is None) as (parent, volume):
        if expected_parent is not None and (volume, _identity(parent, directory=True)[1].hex()) != expected_parent:
            raise ConflictError("NEEDS_REVIEW: replacement parent identity changed.")
        handle = None
        if existing_stage is not None:
            stage_name, recorded_id = existing_stage
            try:
                handle = _relative(parent, stage_name, GENERIC_READ | DELETE_ACCESS, 0, NT_OPEN)
            except FileNotFoundError as exc:
                if not replace:
                    raise ConflictError("NEEDS_REVIEW: recorded stage and target are both missing.") from exc
        reused = handle is not None
        if not reused:
            handle = _relative(parent, temp_name, GENERIC_WRITE | READ_ATTRIBUTES | DELETE_ACCESS, 0, NT_CREATE)
        published = False
        descriptor = None
        try:
            stage_volume, stage_id = _identity(handle, directory=False)
            if stage_volume != volume:
                raise PathSecurityError("Windows state staging crosses a volume.")
            if reused:
                validate_single_link(handle)
                if stage_id.hex() != recorded_id or _read_duplicated_handle(handle) != data:
                    raise ConflictError("NEEDS_REVIEW: staged file identity or contents changed.")
            else:
                descriptor = msvcrt.open_osfhandle(handle, os.O_WRONLY | os.O_BINARY)
                with os.fdopen(descriptor, "wb", closefd=False) as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(descriptor)
                if record_stage is not None:
                    record_stage(temp_name, stage_id.hex())
            if not replace:
                try:
                    _rename(handle, parent, path.name, replace=False)
                except FileExistsError as exc:
                    raise ConflictError(f"Internal target already exists: {path.name}") from exc
                published = True
                return
            while True:
                try:
                    try:
                        access = READ_ATTRIBUTES if expected_sha256 is None else GENERIC_READ
                        sharing = SHARE_ALL if expected_sha256 is None else SHARE_READ
                        destination = _relative(parent, path.name, access, sharing, NT_OPEN)
                    except FileNotFoundError:
                        if expected_sha256 is not None:
                            raise ConflictError("The expected replacement target is missing.")
                    else:
                        if expected_sha256 is None:
                            try:
                                if _identity(destination, directory=False)[0] != volume:
                                    raise PathSecurityError("Windows state destination crosses a volume.")
                            finally:
                                kernel.CloseHandle(destination)
                        else:
                            leaf_id, current = _snapshot_handle(destination, volume, path)
                            if expected_old_id is not None and leaf_id != expected_old_id:
                                raise ConflictError("NEEDS_REVIEW: replacement leaf identity changed.")
                            if hashlib.sha256(current).hexdigest() != expected_sha256:
                                raise ConflictError("The original file changed before replacement.")
                    _rename(handle, parent, path.name)
                    published = True
                    break
                except OSError as exc:
                    if exc.winerror not in {5, 32, 33}:
                        raise
                    if time.monotonic() >= deadline:
                        raise ConflictError("Windows could not replace the internal transaction file. Retry the same operation.") from exc
                    time.sleep(0.05)
        finally:
            try:
                if not published and not reused:
                    _delete(handle)
            finally:
                if descriptor is None:
                    kernel.CloseHandle(handle)
                else:
                    os.close(descriptor)


def replace_state(path: Path, temp_name: str, data: bytes, deadline: float) -> None:
    publish_internal(path, temp_name, data, deadline, replace=True)


def create_marker(parent: int, name: str) -> int:
    handle = _relative(parent, name, GENERIC_WRITE, SHARE_ALL, NT_CREATE)
    try:
        return msvcrt.open_osfhandle(handle, os.O_WRONLY | os.O_BINARY)
    except BaseException:
        kernel.CloseHandle(handle)
        raise


def marker_witness(descriptor: int, stack: ExitStack) -> int:
    original = msvcrt.get_osfhandle(descriptor)
    handle = kernel.ReOpenFile(original, READ_ATTRIBUTES, SHARE_ALL, OPEN_REPARSE_POINT)
    if handle == INVALID_HANDLE:
        raise ctypes.WinError(ctypes.get_last_error())
    stack.callback(kernel.CloseHandle, handle)
    _identity(handle, directory=False)
    return handle


def _delete_marker_if(
    parent: int, name: str, matches: Callable[[bytes, float], bool], deadline: float,
    *, expected: tuple[int, bytes] | None = None,
) -> bool:
    while True:
        try:
            handle = _relative(parent, name, GENERIC_READ | DELETE_ACCESS, SHARE_READ, NT_OPEN)
            descriptor = None
            try:
                identity = _identity(handle, directory=False)
                if expected is not None and identity != expected:
                    return False
                descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
                with os.fdopen(descriptor, "rb", closefd=False) as stream:
                    age = max(0.0, time.time() - os.fstat(descriptor).st_mtime)
                    if not matches(stream.read(), age):
                        return False
                _delete(handle)
            finally:
                if descriptor is None:
                    kernel.CloseHandle(handle)
                else:
                    os.close(descriptor)
            return True
        except FileNotFoundError:
            return True
        except OSError as exc:
            if exc.winerror not in {5, 32, 33} or time.monotonic() >= deadline:
                return False
            time.sleep(0.02)


def release_marker(parent: int, name: str, witness: int, token: str, deadline: float) -> None:
    def owned(data: bytes, age: float) -> bool:
        try:
            payload = json.loads(data.decode("utf-8"))
        except ValueError:
            return False
        return isinstance(payload, dict) and payload.get("token") == token

    _delete_marker_if(parent, name, owned, deadline, expected=_identity(witness, directory=False))


def reclaim_marker(parent: int, name: str, reclaimable: Callable[[bytes, float], bool]) -> bool:
    return _delete_marker_if(parent, name, reclaimable, time.monotonic())


def file_snapshot(path: Path) -> tuple[tuple[int, str], str | None, bytes | None]:
    """Capture parent identity, leaf identity and bytes from bound handles."""
    with bound_parent(path) as (parent, volume):
        parent_id = _identity(parent, directory=True)[1].hex()
        try:
            handle = _relative(parent, path.name, GENERIC_READ, SHARE_READ, NT_OPEN)
        except FileNotFoundError:
            return (volume, parent_id), None, None
        identity, data = _snapshot_handle(handle, volume, path)
        return (volume, parent_id), identity, data


def _snapshot_handle(handle: int, volume: int, path: Path) -> tuple[str, bytes]:
    try:
        identity = _identity(handle, directory=False)[1].hex()
    except BaseException:
        kernel.CloseHandle(handle)
        raise
    return identity, _read_handle(handle, volume, canonical_path=path)


def read_bytes(path: Path) -> bytes:
    with bound_parent(path) as (parent, volume):
        handle = _relative(parent, path.name, GENERIC_READ, SHARE_READ, NT_OPEN)
        return _read_handle(handle, volume)


def _read_handle(handle: int, volume: int, *, canonical_path: Path | None = None) -> bytes:
    descriptor = None
    try:
        if _identity(handle, directory=False)[0] != volume:
            raise PathSecurityError("Windows target crosses a volume.")
        if canonical_path is not None:
            _require_canonical_name(handle, canonical_path)
            standard = StandardInfo()
            if not kernel.GetFileInformationByHandleEx(handle, 1, ctypes.byref(standard), ctypes.sizeof(standard)):
                raise ctypes.WinError(ctypes.get_last_error())
            if standard.links != 1 or standard.delete_pending:
                raise PathSecurityError("Windows replacement requires a single non-deleting link.")
        descriptor = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            return stream.read()
    finally:
        if descriptor is None:
            kernel.CloseHandle(handle)
        else:
            os.close(descriptor)


def read_internal(path: Path) -> bytes:
    with bound_parent(path) as (parent, volume):
        return _read_handle(_relative(parent, path.name, GENERIC_READ, SHARE_ALL, NT_OPEN), volume)


def delete_internal(path: Path) -> None:
    with bound_parent(path) as (parent, volume):
        handle = _relative(parent, path.name, READ_ATTRIBUTES | DELETE_ACCESS, 0, NT_OPEN)
        try:
            if _identity(handle, directory=False)[0] != volume:
                raise PathSecurityError("Windows internal target crosses a volume.")
            _delete(handle)
        finally:
            kernel.CloseHandle(handle)


@contextmanager
def exclusive_lock(path: Path, deadline: float):
    with bound_parent(path, create=True) as (parent, volume):
        while True:
            try:
                handle = _relative(parent, path.name, GENERIC_WRITE | READ_ATTRIBUTES, SHARE_READ, NT_OPEN_IF)
                break
            except OSError as exc:
                if exc.winerror != 32:
                    raise
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ConflictError(f"Could not acquire lock '{path.stem}': Windows sharing violation.")
            time.sleep(min(0.05, remaining))
        try:
            identity = _identity(handle, directory=False)
            if identity[0] != volume:
                raise PathSecurityError("Windows lock object crosses a volume.")
            yield identity
        finally:
            if not kernel.CloseHandle(handle):
                raise ctypes.WinError(ctypes.get_last_error())
