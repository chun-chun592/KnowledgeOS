"""Windows token boundary for a future Broker's connected local pipe."""

from contextlib import contextmanager

import pywintypes
import win32api
import win32con
import win32security
import winerror


class PeerDenied(PermissionError):
    """The pipe peer could not be authenticated under the configured policy."""


@contextmanager
def _peer_token(pipe):
    thread = win32api.GetCurrentThread()
    try:
        existing = win32security.OpenThreadToken(thread, win32con.TOKEN_QUERY, True)
    except pywintypes.error as exc:
        if exc.winerror != winerror.ERROR_NO_TOKEN:
            raise
    else:
        existing.Close()
        raise PeerDenied("Broker worker is already impersonating")
    win32security.ImpersonateNamedPipeClient(pipe)
    try:
        token = win32security.OpenThreadToken(thread, win32con.TOKEN_QUERY, True)
        try:
            yield token
        finally:
            token.Close()
    finally:
        try:
            win32security.RevertToSelf()
        except pywintypes.error as exc:
            raise SystemExit("Broker must exit after failing to revert impersonation") from exc


def authenticate_peer(pipe, allowed_sids: frozenset[str]) -> str:
    """Read TokenUser after a request is read from a connected local server pipe.

    The service must configure local-only transport, a protected pipe DACL,
    and a trusted allowlist. This function never consumes a request SID field.
    """
    try:
        with _peer_token(pipe) as token:
            level = win32security.GetTokenInformation(token, win32security.TokenImpersonationLevel)
            if level < win32security.SecurityIdentification:
                raise PeerDenied("Peer token is anonymous")
            sid, _attributes = win32security.GetTokenInformation(token, win32security.TokenUser)
            actual = win32security.ConvertSidToStringSid(sid)
    except pywintypes.error as exc:
        raise PeerDenied("Windows peer token unavailable") from exc
    if actual not in allowed_sids:
        raise PeerDenied("Peer is outside the Broker allowlist")
    return actual
