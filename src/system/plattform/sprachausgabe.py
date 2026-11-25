"""Plattformanbindung der Sprachausgabe: Audio-Abspieler für Piper und der Sprachdienst des Systems.

Die Fachlogik (``dienste/vorlesen.py``) kennt nur diese Funktionen. Unter Linux sind es ``paplay``/``aplay`` und speech-dispatcher
(``spd-say``); andere Systeme melden hier „nicht unterstützt“ (``None`` / ``False`` / leere Liste), bis ein eigener Zweig dafür beauftragt ist.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

from system.plattform import prozess

LINUX = sys.platform.startswith("linux")


def programmname(name: str) -> str:
    """Dateiname einer ausführbaren Datei auf diesem System (Windows: mit ``.exe``)."""
    return name + ".exe" if os.name == "nt" else name


def abspieler() -> list[str] | None:
    """Befehl, der rohe 16-Bit-Töne (22,05 kHz, mono) von stdin abspielt; ``None``, wenn dieses System keinen eingerichtet hat."""
    if not LINUX:
        return None
    if shutil.which("paplay"):
        return ["paplay", "--raw", "--rate=22050", "--format=s16le", "--channels=1"]
    if shutil.which("aplay"):
        return ["aplay", "-q", "-r", "22050", "-f", "S16_LE", "-c", "1", "-t", "raw", "-"]
    return None


def system_da() -> bool:
    return LINUX and shutil.which("spd-say") is not None


def system_stimmen() -> list[dict]:
    """Deutsche Stimmen des Sprachdienstes: ``[{"kennung", "name"}]``."""
    if not system_da():
        return []
    liste: list[dict] = []
    try:
        r = subprocess.run(["spd-say", "-L"], capture_output=True, encoding="utf-8", errors="replace", timeout=15)
        for z in r.stdout.splitlines():
            t = z.split()
            if len(t) >= 2 and t[1] == "de":
                liste.append({"kennung": t[0], "name": t[0] + " (Sprachdienst)"})
    except (OSError, subprocess.SubprocessError):
        pass
    return liste


def system_stoppen() -> None:
    if system_da():
        try:
            subprocess.run(["spd-say", "-C"], timeout=5)
        except (OSError, subprocess.SubprocessError):
            pass


def system_sprechen(text: str, stimme: str, tempo: int) -> subprocess.Popen:
    befehl = ["spd-say", "-l", "de", "-w"] + (["-y", stimme] if stimme else []) + ["-r", str(tempo), text]
    return prozess.starten(befehl, env=dict(os.environ))


def hinweis_fehlt() -> str:
    """Verständliche Meldung, wenn keine Sprachausgabe eingerichtet ist."""
    if LINUX:
        return ("Auf diesem Rechner ist keine Sprachausgabe eingerichtet. Installieren Sie speech-dispatcher "
                "(sudo apt install speech-dispatcher) oder holen Sie mit ./skripte/stimme-holen.sh die Stimme Piper.")
    return "Auf diesem System ist die Sprachausgabe noch nicht unterstützt."
