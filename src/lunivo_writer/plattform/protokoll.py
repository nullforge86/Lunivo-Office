"""Protokoll: eine Logdatei im Zwischenspeicher-Ordner, damit Fehler beim Laden, Speichern und Prüfen nicht still verschwinden.

Module holen sich ``logging.getLogger("lunivo.<bereich>")``; ``einrichten()`` wird einmal beim Programmstart aufgerufen.
Ohne Aufruf (z. B. in Tests) schreibt nichts in eine Datei.

Drei Arten von Fehlern, drei Aufrufe:

- ``benutzerfehler(log, e)``   — erwartet (Datei fehlt, Kennwort falsch, Format nicht unterstützt): eine Zeile, ohne Ablaufspur.
- ``technischer_fehler(log, kontext, e)`` — Umgebung macht Ärger (Platte voll, Dienst nicht erreichbar): Warnung mit Art des Fehlers und Betriebssystemcode.
- ``unerwartet(log, kontext, e)`` — Programmfehler: Fehlermeldung mit vollständiger Ablaufspur und Umgebung (Programm-, Python-, Qt-Version, System).

In die Datei gelangen nie Dokumentinhalte, Kennwörter oder KI-Schlüssel: ``SchutzFilter`` ersetzt Schlüssel, Tokens, Kennwörter und Pfadinhalte
in Meldungen und Ablaufspuren durch „***“. Die Ablaufspur enthält keine Werte lokaler Variablen.
"""
from __future__ import annotations

import logging
import logging.handlers
import os
import platform
import re
import sys
import threading

from lunivo_writer.plattform import pfade

NAME = "lunivo"
DATEI = "lunivo.log"
_MAX_BYTES = 512 * 1024
_SICHERUNGEN = 2


_GEHEIM = re.compile(
    r"(?i)(sk-[A-Za-z0-9_\-]{8,}|bearer\s+[A-Za-z0-9._\-]{8,}|"
    r"(?:api[_-]?key|apikey|x-api-key|authorization|passwort|kennwort|password|passwd|secret|token)([\"'\s:=]+)(?:bearer\s+)?[^\s\"',;}]+)")


def schwaerzen(text: str) -> str:
    """Schlüssel, Tokens und Kennwörter in einem Text durch „***“ ersetzen."""
    def ersatz(m: re.Match) -> str:
        return (m.group(0).split(m.group(2))[0] + m.group(2) + "***") if m.group(2) else "***"
    return _GEHEIM.sub(ersatz, text)


class SchutzFilter(logging.Filter):
    """Schwärzt Meldung und Ablaufspur, bevor sie in die Logdatei geschrieben werden."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            record.msg, record.args = schwaerzen(record.getMessage()), ()
            if record.exc_info:
                import traceback
                record.exc_text = schwaerzen("".join(traceback.format_exception(*record.exc_info)))
                record.exc_info = None
        except Exception:                          # das Protokoll darf nie selbst das Programm stören
            pass
        return True


def umgebung() -> str:
    try:
        from PySide6 import __version__ as qt
    except Exception:
        qt = "?"
    return f"Python {platform.python_version()}, PySide6 {qt}, {platform.system()} {platform.release()}"


def benutzerfehler(log: logging.Logger, fehler: BaseException) -> None:
    """Erwartet und für den Benutzer bestimmt: eine Zeile ohne Ablaufspur."""
    log.info("Hinweis an den Benutzer: %s", fehler)


def technischer_fehler(log: logging.Logger, kontext: str, fehler: BaseException) -> None:
    """Die Umgebung versagt (Platte, Netz, Dienst): Art des Fehlers und Systemcode, ohne Ablaufspur."""
    code = getattr(fehler, "errno", None)
    log.warning("%s: %s%s", kontext, type(fehler).__name__, f" (errno {code})" if code else "")


def unerwartet(log: logging.Logger, kontext: str, fehler: BaseException) -> None:
    """Ein Programmfehler: vollständige Ablaufspur und Umgebung, damit er sich nachstellen lässt."""
    log.error("Unerwarteter Fehler bei „%s“ [%s]", kontext, umgebung(), exc_info=(type(fehler), fehler, fehler.__traceback__))


def logdatei() -> str:
    d = os.path.join(pfade.cache_dir(), "logs")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, DATEI)


def einrichten(stufe: int = logging.INFO) -> str | None:
    """Logdatei einrichten und nicht abgefangene Fehler protokollieren; liefert den Pfad (oder None, wenn nicht schreibbar)."""
    log = logging.getLogger(NAME)
    log.setLevel(stufe)
    bestehend = next((h for h in log.handlers if isinstance(h, logging.handlers.RotatingFileHandler)), None)
    if bestehend is not None:
        return bestehend.baseFilename
    try:
        pfad = logdatei()
        h = logging.handlers.RotatingFileHandler(pfad, maxBytes=_MAX_BYTES, backupCount=_SICHERUNGEN, encoding="utf-8")
    except OSError:
        return None
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    h.addFilter(SchutzFilter())
    log.addHandler(h)
    _alt = sys.excepthook

    def _haken(art, wert, spur):
        log.critical("Nicht abgefangener Fehler [%s]", umgebung(), exc_info=(art, wert, spur))
        _alt(art, wert, spur)

    def _faden_haken(args):
        log.critical("Nicht abgefangener Fehler im Arbeitsfaden „%s“ [%s]", getattr(args.thread, "name", "?"), umgebung(),
                     exc_info=(args.exc_type, args.exc_value, args.exc_traceback))

    sys.excepthook = _haken
    threading.excepthook = _faden_haken
    return pfad
