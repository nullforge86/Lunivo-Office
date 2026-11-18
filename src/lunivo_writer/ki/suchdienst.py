"""Die lokale Dokumentensuche als MCP-Server (Standard-Ein-/Ausgabe, JSON-RPC 2.0, eine Nachricht je Zeile).

Aufruf (trägt Lunivo selbst ein, Reiter „Dokumente“ ▸ „Als KI-Werkzeug eintragen“):

    python suchdienst.py --index <dokumentindex.sqlite> --ordner <Ordner> [--ordner <Ordner> …]

Der Server liest nur den fertigen Suchindex und nur Treffer aus den mit ``--ordner`` freigegebenen Ordnern; er öffnet keine Dokumente, hat
keinen Netzzugriff und schreibt nichts. Der Index wird in Lunivo aufgebaut (Reiter „Dokumente“ ▸ „Jetzt indexieren“). Der Start benötigt
kein Qt und wenig Speicher; Lunivo startet den Server nur für die Dauer einer Frage (siehe ``mcp.py``), jeder Aufruf wird dort erst nach
Rückfrage ausgeführt."""
from __future__ import annotations

import argparse
import json
import os
import sys

if __package__ in (None, ""):                                  # als Skript gestartet: das Projekt (src) auffindbar machen
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lunivo_writer.ki import dokumentensuche as DS             # noqa: E402

PROTOKOLL = "2024-11-05"
MAX_ANTWORT = 12000                                            # Zeichen je Antwort

WERKZEUGE = [
    {"name": "dokumente_durchsuchen",
     "description": "Durchsucht die vom Benutzer freigegebenen Dokumente nach den Wörtern der Frage und liefert die besten Abschnitte mit Dateiname und Ort.",
     "inputSchema": {"type": "object", "properties": {"frage": {"type": "string", "description": "Suchbegriffe oder Frage"},
                                                      "anzahl": {"type": "integer", "minimum": 1, "maximum": 10, "description": "Zahl der Abschnitte (Vorgabe 4)"}},
                     "required": ["frage"]},
     "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False}},
    {"name": "ordner_auflisten",
     "description": "Nennt die Ordner, die der Benutzer für die Dokumentensuche freigegeben hat, und die Größe des Index.",
     "inputSchema": {"type": "object", "properties": {}},
     "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False}},
]


def _text(t: str, fehler: bool = False) -> dict:
    return {"content": [{"type": "text", "text": t[:MAX_ANTWORT]}], "isError": fehler}


def aufrufen(name: str, argumente: dict, index: DS.Index, ordner: list[str]) -> dict:
    if name == "ordner_auflisten":
        d, a = index.anzahl()
        return _text("Freigegebene Ordner:\n" + "\n".join(ordner) + f"\n\nIm Index: {d} Dateien, {a} Abschnitte.")
    if name == "dokumente_durchsuchen":
        frage = str((argumente or {}).get("frage") or "")[:300]
        try:
            n = max(1, min(10, int((argumente or {}).get("anzahl") or 4)))
        except (TypeError, ValueError):
            n = 4
        if not frage.strip():
            return _text("Es fehlt die Frage.", True)
        treffer = index.suchen(frage, ordner, n)
        return _text(DS.als_text(treffer) if treffer else "Keine passenden Abschnitte gefunden (ist der Index in Lunivo aufgebaut?).")
    return _text(f"Unbekanntes Werkzeug: {name}", True)


def behandle(nachricht: dict, index: DS.Index, ordner: list[str]) -> dict | None:
    """Antwort auf eine Nachricht; ``None`` für Benachrichtigungen (ohne ``id``)."""
    if not isinstance(nachricht, dict):
        return None
    i, methode, p = nachricht.get("id"), nachricht.get("method"), nachricht.get("params") or {}
    if i is None:
        return None
    if methode == "initialize":
        r = {"protocolVersion": PROTOKOLL, "capabilities": {"tools": {}}, "serverInfo": {"name": "Lunivo Dokumentensuche", "version": "1"}}
    elif methode == "tools/list":
        r = {"tools": WERKZEUGE}
    elif methode == "tools/call":
        r = aufrufen(str(p.get("name") or ""), p.get("arguments") or {}, index, ordner)
    elif methode == "ping":
        r = {}
    else:
        return {"jsonrpc": "2.0", "id": i, "error": {"code": -32601, "message": f"Unbekannte Methode: {methode}"}}
    return {"jsonrpc": "2.0", "id": i, "result": r}


def main(argv: list[str] | None = None) -> int:
    a = argparse.ArgumentParser(description="Lunivo Dokumentensuche (MCP-Server)")
    a.add_argument("--index", required=True)
    a.add_argument("--ordner", action="append", default=[])
    arg = a.parse_args(argv)
    ordner = [os.path.abspath(o) for o in arg.ordner if os.path.isdir(o)]
    index = DS.Index(arg.index)
    for zeile in sys.stdin:
        try:
            antwort = behandle(json.loads(zeile), index, ordner)
        except ValueError:
            continue
        if antwort is not None:
            sys.stdout.write(json.dumps(antwort, ensure_ascii=False) + "\n"); sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
