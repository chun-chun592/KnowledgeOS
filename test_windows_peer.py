from uuid import uuid4

import pytest

win32api = pytest.importorskip("win32api")
import pywintypes
import win32con
import win32file
import win32pipe
import win32security
import winerror

from windows_peer import PeerDenied, authenticate_peer


@pytest.mark.parametrize("allow", [True, False])
def test_native_pipe_uses_kernel_sid_not_payload(allow):
    process = win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32con.TOKEN_QUERY)
    try:
        actual = win32security.ConvertSidToStringSid(
            win32security.GetTokenInformation(process, win32security.TokenUser)[0]
        )
    finally:
        process.Close()
    claimed = "S-1-5-21-111-222-333-1234"
    name = rf"\\.\pipe\knowledgeos-r5-{uuid4().hex}"
    pipe = win32pipe.CreateNamedPipe(name, win32pipe.PIPE_ACCESS_DUPLEX,
                                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | 8,
                                    1, 1024, 1024, 1000, None)
    try:
        handle = win32file.CreateFile(name, win32con.GENERIC_WRITE, 0, None,
                                      win32con.OPEN_EXISTING, 0, None)
        try:
            try:
                win32pipe.ConnectNamedPipe(pipe, None)
            except pywintypes.error as exc:
                if exc.winerror != winerror.ERROR_PIPE_CONNECTED:
                    raise
            win32file.WriteFile(handle, claimed.encode())
            assert win32file.ReadFile(pipe, 1024)[1].decode() == claimed
            if allow:
                assert authenticate_peer(pipe, frozenset({actual})) == actual
            else:
                with pytest.raises(PeerDenied):
                    authenticate_peer(pipe, frozenset({claimed}))
            with pytest.raises(pywintypes.error) as raised:
                win32security.OpenThreadToken(win32api.GetCurrentThread(), win32con.TOKEN_QUERY, True)
            assert raised.value.winerror == winerror.ERROR_NO_TOKEN
        finally:
            handle.Close()
    finally:
        pipe.Close()
