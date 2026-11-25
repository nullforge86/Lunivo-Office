"""Sperre auf eine Sperrdatei, die auch zwischen Lunivo-Fenstern (Prozessen) gilt: fcntl unter Linux/macOS, msvcrt unter Windows."""
from __future__ import annotations

import errno
import os
import tempfile

try:
    import fcntl
except ImportError:                                      # Windows
    fcntl = None
    import msvcrt


class SperreBelegt(Exception):
    """Ein anderer Prozess hält die Sperre."""


def sperr_ordner() -> str:
    """Ordner für die Sperrdateien (nur für den Benutzer); wird bei Bedarf angelegt."""
    if hasattr(os, "getuid"):
        kennung = str(os.getuid())
    else:
        import getpass
        kennung = getpass.getuser()
    basis = os.environ.get("XDG_RUNTIME_DIR") or os.path.join(tempfile.gettempdir(), f"lunivo-{kennung}")
    d = os.path.join(basis, "lunivo-sperren")
    os.makedirs(d, mode=0o700, exist_ok=True)
    return d


def sperre_oeffnen(datei: str) -> int:
    """Sperrdatei öffnen und sofort sperren; gibt den Dateideskriptor zurück. Belegt → SperreBelegt, sonst OSError."""
    fd = os.open(datei, os.O_RDWR | os.O_CREAT, 0o600)
    try:
        if fcntl is not None:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        else:
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
    except BlockingIOError as e:
        os.close(fd)
        raise SperreBelegt() from e
    except OSError as e:
        os.close(fd)
        if fcntl is None and e.errno in (errno.EACCES, errno.EDEADLK):
            raise SperreBelegt() from e
        raise
    return fd


def sperre_freigeben(fd: int) -> None:
    try:
        if fcntl is not None:
            fcntl.flock(fd, fcntl.LOCK_UN)
        else:
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    finally:
        os.close(fd)
