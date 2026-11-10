"""Chat mit MCP-Werkzeugen über die OpenAI-kompatible Schnittstelle (Ollama und eigene Anbieter): Das Modell darf Werkzeuge verlangen; jeder
Aufruf wird erst nach Rückfrage beim Benutzer ausgeführt. ``ki`` ist die ``KI``-Instanz (Rückfragen ``server_frage``/``werkzeug_frage``)."""
from __future__ import annotations

import json
import urllib.error

from lunivo_writer.ai import ki_transport as T
from lunivo_writer.ai import mcp as M
from lunivo_writer.ai import modellfaehigkeit as MF

MAX_RUNDEN = 6
ERGEBNIS_GRENZE = 8000


class _Sitzung:
    """Die gestarteten Werkzeug-Server und ihre Werkzeuge (``wo``: Name -> (Client, Werkzeugname, Servername, Art))."""

    def __init__(self):
        self.clients, self.tools, self.wo = [], [], {}

    def starten(self, ki, server: list[dict]):
        """Startet jeden erlaubten Server. Fehler als Wörterbuch, sonst None."""
        for sv in server:
            fehler = self._erlaubnis(ki, sv)
            if fehler is not None:
                return fehler
            try:
                c = M.McpClient(sv["befehl"])
            except M.McpFehler as e:
                return {"fehler": f"KI-Werkzeug „{sv['name']}“: {e}"}
            self.clients.append(c)
            self._werkzeuge_aufnehmen(c, sv["name"])
        return None

    @staticmethod
    def _erlaubnis(ki, sv: dict):
        if sv["befehl"] in ki._server_erlaubt:
            return None
        if not ki.server_frage(sv["name"], sv["befehl"]):
            return {"fehler": f"Der Start des KI-Werkzeugs „{sv['name']}“ wurde nicht erlaubt."}
        ki._server_erlaubt = ki._server_erlaubt | {sv["befehl"]}
        return None

    def _werkzeuge_aufnehmen(self, c, servername: str) -> None:
        for t in c.werkzeuge():
            n = t["name"] if t["name"] not in self.wo else f"{servername}_{t['name']}"
            self.wo[n] = (c, t["name"], servername, M.art_des_werkzeugs(t))
            self.tools.append({"type": "function", "function": {
                "name": n, "description": t.get("description", ""),
                "parameters": t.get("inputSchema") or {"type": "object", "properties": {}}}})

    def schliessen(self) -> None:
        for c in self.clients:
            c.schliessen()


def _bitte(name: str, nachrichten: list, tools: list, optionen: dict, effort) -> dict:
    bitte = {"model": name, "messages": nachrichten, "tools": tools, "temperature": float(optionen.get("temperatur", 0.2))}
    if optionen.get("topP") is not None:
        bitte["top_p"] = float(optionen["topP"])
    if optionen.get("maxLaenge"):
        bitte["max_tokens"] = int(optionen["maxLaenge"])
    if effort is not None:
        bitte["reasoning_effort"] = effort
    return bitte


def _senden(url: str, kopf: dict, bitte: dict, effort):
    """(Antwort, Denktiefe). Kennt das Modell keine Denktiefe (400), geht es ohne sie noch einmal — dauerhaft für dieses Gespräch."""
    try:
        with T.post(url, kopf, bitte, 300) as r:
            return T.json_dict(r), effort
    except urllib.error.HTTPError as e:
        if e.code != 400 or effort is None:
            raise
    bitte.pop("reasoning_effort", None)
    with T.post(url, kopf, bitte, 300) as r:
        return T.json_dict(r), None


def _aufrufe(msg: dict) -> list[dict]:
    roh = msg.get("tool_calls")
    return [a for a in roh if isinstance(a, dict)] if isinstance(roh, list) else []


def _argumente(f: dict) -> dict:
    roh = f.get("arguments")
    if not isinstance(roh, str):
        return roh or {}
    try:
        return json.loads(roh or "{}")
    except ValueError:
        return {}


def _ausfuehren(ki, ziel, arg: dict, modus: str) -> str:
    if ziel is None:
        return "Dieses Werkzeug gibt es nicht."
    if not (MF.werkzeug_erlaubt(modus, ziel[3]) or ki.werkzeug_frage(ziel[1], arg, ziel[2], ziel[3])):
        return "Der Benutzer hat den Aufruf abgelehnt."
    try:
        return ziel[0].aufrufen(ziel[1], arg)
    except M.McpFehler as e:
        return f"Fehler: {e}"


def _tool_antwort(ki, wo: dict, aufruf: dict, modus: str) -> dict:
    f = aufruf.get("function") or {}
    ergebnis = _ausfuehren(ki, wo.get(f.get("name", "")), _argumente(f), modus)
    return {"role": "tool", "tool_call_id": aufruf.get("id", ""), "content": str(ergebnis)[:ERGEBNIS_GRENZE]}


def _runden(ki, sitzung: _Sitzung, system: str, verlauf: list[dict], ziel: tuple, optionen: dict) -> dict:
    url, name, kopf = ziel
    nachrichten = [{"role": "system", "content": system}] + T.nachrichten(verlauf, "openai")
    effort = T.stufe(optionen)["openai"]
    modus = optionen.get("werkzeuge", "fragen")
    for _runde in range(MAX_RUNDEN):
        bitte = _bitte(name, nachrichten, sitzung.tools, optionen, effort)
        daten, effort = _senden(url, kopf, bitte, effort)
        msg = T.erste_nachricht(daten)
        aufrufe = _aufrufe(msg)
        if not aufrufe:
            erg = T.ohne_gruebeln(msg.get("content") or "").strip()
            return {"text": erg} if erg else {"fehler": "Es kam keine Antwort zurück."}
        nachrichten.append({"role": "assistant", "content": msg.get("content") or "", "tool_calls": aufrufe})
        nachrichten.extend(_tool_antwort(ki, sitzung.wo, aufruf, modus) for aufruf in aufrufe)
    return {"fehler": "Die KI hat zu viele Werkzeugaufrufe gebraucht. Bitte die Frage genauer stellen."}


def _fehler_http(e: urllib.error.HTTPError, verlauf: list[dict]) -> dict:
    bild = any(z.get("bilder") for z in verlauf[-1:])
    return {"fehler": f"Der Anbieter meldet Fehler {e.code} — unterstützt das Modell Werkzeuge" + (" und Bilder?" if bild else "?")}


def chat(ki, system: str, verlauf: list[dict], server: list[dict], ziel: tuple, optionen: dict) -> dict:
    """``ziel``: (Adresse der Chat-Schnittstelle, Modellname beim Anbieter, Kopfzeilen)."""
    sitzung = _Sitzung()
    try:
        fehler = sitzung.starten(ki, server)
        return fehler if fehler is not None else _runden(ki, sitzung, system, verlauf, ziel, optionen)
    except M.McpFehler as e:
        return {"fehler": f"KI-Werkzeug: {e}"}
    except urllib.error.HTTPError as e:
        return _fehler_http(e, verlauf)
    except (urllib.error.URLError, OSError, ValueError) as e:
        return {"fehler": f"Es hat nicht geklappt: {getattr(e, 'reason', e)}"}
    finally:
        sitzung.schliessen()
