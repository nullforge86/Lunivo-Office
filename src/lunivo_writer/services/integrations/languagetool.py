"""LanguageTool als zweite Meinung (eigener Java-Prozess, nur auf diesem Rechner, 127.0.0.1).

LanguageTool steht unter LGPL-2.1; als getrennter Prozess bleibt die Lizenz dieses Programms unberührt.

Vertrauen: Lunivo schickt Text nur an den Prozess, den es selbst gestartet hat (languagetool-server.jar unter
~/.local/share/<App>/languagetool, auf einem vom System frei gewählten Port, nur 127.0.0.1). Ein Dienst, der zufällig schon auf einem Port
lauscht, ist nicht vertrauenswürdig und wird nicht benutzt — es sei denn, der Benutzer erlaubt ihn ausdrücklich (``fremd_erlauben``).
Der Prozess läuft in eigener Gruppe ohne Zugangsdaten in der Umgebung und endet mit dem Programm (``beenden``).
Es wird nichts heruntergeladen. Der Text verlässt den Rechner nicht; er geht nur an den eigenen Prozess (oder den erlaubten lokalen Dienst).
"""
from __future__ import annotations

import atexit
import json
import os
import shutil
import socket
import subprocess
import time
import urllib.parse
import urllib.request

from lunivo_writer.plattform import prozess
from lunivo_writer.services.settings_service import data_dir

PORT = 8081                                  # übliche Nummer eines von Hand gestarteten Servers; wird nur mit ausdrücklicher Erlaubnis benutzt
MAX_ANTWORT = 5 * 1024 * 1024                # Byte, die ein Dienst zurückgeben darf
_lauf = {"proc": None, "port": None, "jar": None, "fremd": None}


class LanguageToolFehler(Exception):
    pass


def ordner() -> str:
    return os.path.join(data_dir(), "languagetool")


def laeuft(port: int = PORT) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def jar_finden() -> str | None:
    for wurzel, _d, dateien in os.walk(ordner()):
        if "languagetool-server.jar" in dateien:
            return os.path.join(wurzel, "languagetool-server.jar")
    return None


def fremd_erlauben(port: int | None) -> None:
    """Erlaubt (``port``) oder verbietet (None) die Nutzung eines bereits laufenden lokalen LanguageTool-Dienstes auf diesem Port."""
    _lauf["fremd"] = port


def eigener_prozess_laeuft() -> bool:
    p = _lauf["proc"]
    return p is not None and p.poll() is None and _lauf["port"] is not None and laeuft(_lauf["port"])


def status() -> dict:
    """Wer bedient die Prüfung? Für Anzeige und Datenschutzhinweis: ``art`` ist „eigen“, „fremd“ oder „keiner“."""
    p = _lauf["proc"]
    if eigener_prozess_laeuft():
        return {"art": "eigen", "port": _lauf["port"], "pid": p.pid, "jar": _lauf["jar"]}
    if _lauf["fremd"] and laeuft(_lauf["fremd"]):
        return {"art": "fremd", "port": _lauf["fremd"], "pid": None, "jar": None}
    return {"art": "keiner", "port": None, "pid": None, "jar": None}


def verfuegbar(port: int | None = None) -> bool:
    """Gibt es einen Weg, zu prüfen: eigener Prozess startbar (Jar und Java) oder ausdrücklich erlaubter lokaler Dienst?"""
    if _lauf["fremd"] and laeuft(_lauf["fremd"]):
        return True
    return jar_finden() is not None and shutil.which("java") is not None


def _freier_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def starten(port: int | None = None, warte_s: int = 30) -> int:
    """Stellt sicher, dass ein vertrauenswürdiger Dienst läuft. → Portnummer. Ohne ``port`` wählt das System einen freien."""
    if eigener_prozess_laeuft():
        return _lauf["port"]
    if _lauf["fremd"] and laeuft(_lauf["fremd"]):
        return _lauf["fremd"]
    jar = jar_finden()
    if not jar:
        raise LanguageToolFehler("LanguageTool ist nicht eingerichtet. Es gehört nach " + ordner() + ".")
    if not shutil.which("java"):
        raise LanguageToolFehler("Für LanguageTool wird Java gebraucht; es ist nicht installiert.")
    beenden()                                                  # ein hängengebliebener eigener Prozess wird erst entsorgt
    port = port or _freier_port()
    _lauf.update(proc=prozess.starten(
        ["java", "-cp", jar, "org.languagetool.server.HTTPServer", "--port", str(port)],
        cwd=os.path.dirname(jar), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL), port=port, jar=jar)
    for _ in range(warte_s * 2):
        if _lauf["proc"].poll() is not None:
            break
        if laeuft(port):
            return port
        time.sleep(0.5)
    beenden()
    raise LanguageToolFehler("LanguageTool ist nicht hochgekommen.")


def pruefe(text: str, sprache: str = "de-DE", port: int | None = None) -> list[dict]:
    """→ Funde im selben Format wie die eigene Prüfung (von, bis, alt, neu, grund, art)."""
    port = starten(port)
    daten = urllib.parse.urlencode({"language": sprache, "text": text[:60000],
                                    "disabledCategories": "TYPOS"}).encode("utf-8")
    try:
        antwort = urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{port}/v2/check", data=daten),
                                         timeout=90)
        roh = json.loads(antwort.read(MAX_ANTWORT + 1)[:MAX_ANTWORT].decode("utf-8"))
    except (OSError, ValueError) as e:
        raise LanguageToolFehler(f"LanguageTool antwortet nicht: {e}") from e
    funde = []
    for m in roh.get("matches", []):
        von = m.get("offset", 0)
        bis = von + m.get("length", 0)
        ers = m.get("replacements") or []
        neu = ers[0].get("value", "") if ers else ""
        funde.append({"von": von, "bis": bis, "alt": text[von:bis], "neu": neu,
                      "grund": (m.get("message") or "") + " (LanguageTool)",
                      "art": "tipp" if neu else "hinweis", "wortEbene": False})
    return funde[:200]


def beenden() -> None:
    """Beendet den selbst gestarteten Prozess (nie einen fremden Dienst)."""
    p = _lauf.get("proc")
    prozess.beenden(p)
    _lauf.update(proc=None, port=None, jar=None)


atexit.register(beenden)
