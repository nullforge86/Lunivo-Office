"""MCP-Server (Model Context Protocol) über die Standard-Ein-/Ausgabe: Werkzeuge auflisten und aufrufen.

Ein Server ist ein Programm, das der Benutzer selbst einträgt (``befehl``, etwa „npx -y @modelcontextprotocol/server-filesystem ~/Dokumente“).
Gesprochen wird JSON-RPC 2.0, je Nachricht eine Zeile. Lunivo startet den Server nur für die Dauer einer Frage.

Der Server ist ein fremdes Programm und eine Vertrauensgrenze: Zeilenlänge, Nachrichtenzahl, Ausgabegröße und Lebensdauer sind begrenzt, die
Umgebung enthält keine Zugangsdaten, und beim Schließen wird die ganze Prozessgruppe beendet."""
from __future__ import annotations

import json
import queue
import shlex
import subprocess
import threading
import time

from lunivo_writer.plattform import prozess

ZEIT = 25.0                                    # Sekunden je Antwort des Servers
LEBENSDAUER = 600.0                            # Sekunden, die ein Server höchstens läuft
MAX_ZEILE = 1024 * 1024                        # Byte je Nachricht des Servers
MAX_NACHRICHTEN = 500                          # ungelesene Nachrichten, bevor der Server als außer Kontrolle gilt
MAX_ERGEBNIS = 64 * 1024                       # Zeichen, die ein Werkzeug zurückgeben darf


class McpFehler(Exception):
    pass


class McpClient:
    def __init__(self, befehl: str):
        try:
            teile = shlex.split(befehl)
        except ValueError as e:
            raise McpFehler(f"Der Befehl ist nicht lesbar: {e}")
        if not teile:
            raise McpFehler("Es ist kein Befehl eingetragen.")
        try:
            self.p = prozess.starten(teile, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
        except OSError as e:
            raise McpFehler(f"Der Server startet nicht: {e.strerror or e}")
        self.q: queue.Queue = queue.Queue()
        self.nr = 0
        self.ende = time.monotonic() + LEBENSDAUER
        self.zu_viel = False
        threading.Thread(target=self._lesen, daemon=True).start()
        try:
            self._starten()
        except McpFehler:
            self.schliessen()
            raise

    def _starten(self) -> None:
        self._senden({"jsonrpc": "2.0", "id": self._neu(), "method": "initialize",
                      "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "Lunivo Writer", "version": "1"}}})
        self._antwort(self.nr)
        self._senden({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _neu(self) -> int:
        self.nr += 1
        return self.nr

    def _lesen(self) -> None:
        while True:
            try:
                zeile = self.p.stdout.readline(MAX_ZEILE + 1)
            except (OSError, ValueError):
                break
            if not zeile:
                break
            if len(zeile) > MAX_ZEILE or self.q.qsize() >= MAX_NACHRICHTEN:
                self.zu_viel = True                           # außer Kontrolle: nicht weiter lesen, Prozess wird beendet
                prozess.beenden(self.p, 1.0)
                break
            try:
                self.q.put(json.loads(zeile))
            except ValueError:
                continue                                      # Ausgaben, die kein JSON sind, überspringen
        self.q.put(None)

    def _senden(self, nachricht: dict) -> None:
        try:
            self.p.stdin.write(json.dumps(nachricht) + "\n"); self.p.stdin.flush()
        except (OSError, ValueError):
            raise McpFehler("Der Server antwortet nicht mehr.")

    def _antwort(self, nr: int) -> dict:
        while True:
            rest = self.ende - time.monotonic()
            if rest <= 0:
                raise McpFehler("Der Server läuft schon zu lange und wird beendet.")
            try:
                m = self.q.get(timeout=min(ZEIT, rest))
            except queue.Empty:
                raise McpFehler("Der Server hat zu lange gebraucht.")
            if m is None:
                raise McpFehler("Der Server hat zu viele oder zu große Nachrichten geschickt und wurde beendet."
                                if self.zu_viel else "Der Server hat sich beendet.")
            if m.get("id") == nr:
                if "error" in m:
                    raise McpFehler(str((m["error"] or {}).get("message", "Fehler des Servers")))
                return m.get("result") or {}

    def werkzeuge(self) -> list[dict]:
        """[{name, description, inputSchema}] des Servers."""
        self._senden({"jsonrpc": "2.0", "id": self._neu(), "method": "tools/list", "params": {}})
        return self._antwort(self.nr).get("tools", [])

    def aufrufen(self, name: str, argumente: dict) -> str:
        self._senden({"jsonrpc": "2.0", "id": self._neu(), "method": "tools/call", "params": {"name": name, "arguments": argumente or {}}})
        r = self._antwort(self.nr)
        text = "\n".join(t.get("text", "") for t in r.get("content", []) if t.get("type") == "text")
        if len(text) > MAX_ERGEBNIS:
            text = text[:MAX_ERGEBNIS] + "\n[… Ausgabe des Werkzeugs gekürzt]"
        return ("Fehler des Werkzeugs: " + text) if r.get("isError") else text

    def schliessen(self) -> None:
        try:
            self.p.stdin.close()
        except OSError:
            pass
        prozess.beenden(self.p)


def pruefen(befehl: str) -> list[dict]:
    """Verbindung testen: die Werkzeuge des Servers (für „Testen“ im Fenster KI-Einstellungen)."""
    c = McpClient(befehl)
    try:
        return c.werkzeuge()
    finally:
        c.schliessen()


def art_des_werkzeugs(werkzeug: dict) -> str:
    """Grobe Einstufung eines Werkzeugs für die Rückfrage: „lesen“, „schreiben“, „löschen“, „netzwerk“ oder „unbekannt“.

    Maßgeblich sind die Hinweise (``annotations``), die der Server selbst mitliefert; fehlen sie, entscheidet der Name. Im Zweifel „unbekannt“
    — das wird in der Rückfrage ausdrücklich so gezeigt und nie als harmlos dargestellt."""
    a = werkzeug.get("annotations") or {}
    name = (werkzeug.get("name") or "").lower()
    if a.get("destructiveHint") or any(w in name for w in ("delete", "remove", "rm_", "drop", "kill", "loesch", "lösch")):
        return "löschen"
    if a.get("openWorldHint") or any(w in name for w in ("http", "fetch", "download", "request", "url", "web", "search", "send", "post")):
        return "netzwerk"
    if a.get("readOnlyHint") is False or any(w in name for w in ("write", "create", "edit", "update", "move", "rename", "save", "put", "exec", "run")):
        return "schreiben"
    if a.get("readOnlyHint") or any(w in name for w in ("read", "list", "get", "view", "show", "stat", "find", "open")):
        return "lesen"
    return "unbekannt"
