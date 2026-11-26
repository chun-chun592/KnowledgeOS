"""Local Windows transport for the Broker and the private Writer handoff."""

import json
import logging
import re
from contextlib import contextmanager

import pywintypes
import win32api
import win32con
import win32file
import win32pipe
import win32security
import winerror

from windows_peer import PeerDenied, authenticate_peer

LIMIT = 256 * 1024
LOG = logging.getLogger("knowledgeos.secure_write.transport")


class OutcomeUnknown(OSError):
    """The request may have reached its destination before the connection failed."""


@contextmanager
def closing(handle):
    try:
        yield handle
    finally:
        handle.Close()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate field")
        result[key] = value
    return result


def encode(value):
    wire = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    if len(wire) > LIMIT:
        raise ValueError("message too large")
    return wire


def decode(wire):
    obj = json.loads(wire.decode("utf-8"), object_pairs_hook=unique_object)
    if not isinstance(obj, dict):
        raise ValueError("expected object")
    encode(obj)
    return obj


def pipe_path(name):
    if not re.fullmatch(r"KnowledgeOS-R6-[A-Za-z0-9-]{1,64}", name):
        raise ValueError("invalid synthetic endpoint")
    return "\\\\.\\pipe\\" + name


def process_sid(pid=None):
    process = (win32api.OpenProcess(0x1000, False, pid) if pid is not None
               else win32api.GetCurrentProcess())
    try:
        token = win32security.OpenProcessToken(process, win32con.TOKEN_QUERY)
        try:
            return win32security.ConvertSidToStringSid(
                win32security.GetTokenInformation(token, win32security.TokenUser)[0]
            )
        finally:
            token.Close()
    finally:
        if pid is not None:
            process.Close()


def call(name, expected_server_sid, request):
    path = pipe_path(name)
    win32pipe.WaitNamedPipe(path, 2000)
    # Specific pipe rights exclude FILE_CREATE_PIPE_INSTANCE.
    with closing(win32file.CreateFile(path, 0x00100183, 0, None, win32con.OPEN_EXISTING,
                                     0x00100000 | 0x00010000, None)) as pipe:
        if process_sid(win32pipe.GetNamedPipeServerProcessId(pipe)) != expected_server_sid:
            raise PeerDenied("unexpected server TokenUser")
        win32pipe.SetNamedPipeHandleState(pipe, win32pipe.PIPE_READMODE_MESSAGE, None, None)
        wire = encode(request)
        try:
            win32file.WriteFile(pipe, wire)
            return decode(win32file.ReadFile(pipe, LIMIT)[1])
        except (pywintypes.error, ValueError) as exc:
            mutations = {"create", "update", "human_update", "restore", "delete", "restore_deleted", "sync_wiki",
                         "authorization_request", "authorization_approve", "authorization_reject",
                         "authorization_revoke"}
            if request.get("operation") in mutations or request.get("request", {}).get("operation") in mutations:
                raise OutcomeUnknown("No verified response; query the original key") from exc
            raise


def serve(name, owner, clients, dispatch):
    if process_sid() != owner or owner in clients:
        raise PeerDenied("service must run as its independent configured identity")
    sddl = f"O:{owner}D:P(A;;GA;;;{owner})" + "".join(
        f"(A;;0x00100183;;;{sid})" for sid in sorted(clients)
    )
    sa = pywintypes.SECURITY_ATTRIBUTES()
    sa.SECURITY_DESCRIPTOR = win32security.ConvertStringSecurityDescriptorToSecurityDescriptor(sddl, 1)
    with closing(win32pipe.CreateNamedPipe(
        pipe_path(name), win32pipe.PIPE_ACCESS_DUPLEX | 0x00080000,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | 8,
        1, LIMIT, LIMIT, 2000, sa,
    )) as pipe:
        LOG.info("endpoint listening name=%s", name)
        while True:
            try:
                try:
                    win32pipe.ConnectNamedPipe(pipe, None)
                except pywintypes.error as exc:
                    if exc.winerror != winerror.ERROR_PIPE_CONNECTED:
                        raise
                wire = win32file.ReadFile(pipe, LIMIT)[1]
                try:
                    peer = authenticate_peer(pipe, frozenset(clients))
                    result = dispatch(peer, decode(wire))
                except PeerDenied:
                    result = {"code": "DENIED"}
                except (ValueError, TypeError, KeyError):
                    result = {"code": "INVALID_REQUEST"}
                win32file.WriteFile(pipe, encode(result))
                # Client consumes the reply before closing the handle.
                win32file.FlushFileBuffers(pipe)
            except pywintypes.error as exc:
                if exc.winerror not in (winerror.ERROR_BROKEN_PIPE, winerror.ERROR_NO_DATA,
                                       winerror.ERROR_MORE_DATA, winerror.ERROR_PIPE_NOT_CONNECTED):
                    raise
            finally:
                try:
                    win32pipe.DisconnectNamedPipe(pipe)
                except pywintypes.error as exc:
                    if exc.winerror != winerror.ERROR_PIPE_NOT_CONNECTED:
                        raise
