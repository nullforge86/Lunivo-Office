"""Fremde Programme starten und sicher beenden — die einzige Stelle, die dabei auf das Betriebssystem Rücksicht nimmt.

    p = starten(["java", "-jar", ...], cwd=...)     # eigene Prozessgruppe (POSIX) bzw. Gruppe (Windows), Umgebung ohne Geheimnisse
    beenden(p)                                       # erst freundlich, nach ``warte`` Sekunden hart; bei POSIX mit allen Kindprozessen
"""
from __future__ import annotations

import os
import signal
import subprocess

_GEHEIM = ("KEY", "TOKEN", "SECRET", "PASSWORD", "PASSWD", "CREDENTIAL", "AUTHORIZATION", "COOKIE")      # nicht „AUTH“ allein: XAUTHORITY braucht X11


def bereinigte_umgebung(basis: dict[str, str] | None = None) -> dict[str, str]:
    """Die Umgebung ohne Variablen, die nach Zugangsdaten aussehen (API-Schlüssel, Tokens, Kennwörter)."""
    return {k: v for k, v in (basis if basis is not None else os.environ).items() if not any(m in k.upper() for m in _GEHEIM)}


def starten(args: list[str], **kw) -> subprocess.Popen:
    """``subprocess.Popen`` mit eigener Prozessgruppe und bereinigter Umgebung (``env`` überschreibt)."""
    kw.setdefault("env", bereinigte_umgebung())
    if os.name == "nt":
        kw.setdefault("creationflags", subprocess.CREATE_NEW_PROCESS_GROUP)
    else:
        kw.setdefault("start_new_session", True)
    return subprocess.Popen(args, **kw)


def _signal(p: subprocess.Popen, hart: bool) -> None:
    try:
        if os.name == "nt":
            p.kill() if hart else p.terminate()
        else:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL if hart else signal.SIGTERM)
    except (OSError, ProcessLookupError):
        pass


def beenden(p: subprocess.Popen | None, warte: float = 3.0) -> None:
    """Beendet den Prozess (und bei POSIX seine Gruppe) und wartet auf ihn, damit kein Zombie bleibt."""
    if p is None or p.poll() is not None:
        return
    _signal(p, hart=False)
    try:
        p.wait(timeout=warte)
    except subprocess.TimeoutExpired:
        _signal(p, hart=True)
        try:
            p.wait(timeout=warte)
        except subprocess.TimeoutExpired:
            pass
