"""Verzeichnis der Anbindungen an andere Programme und Dienste — eine Stelle, die für jede sagt, was sie ist, wohin Daten gehen und was erst
nach Zustimmung geschieht. Die Oberfläche zeigt daraus die Datenschutzübersicht, ohne etwas über einzelne Integrationen zu wissen.

Eine Integration hat: ``schluessel``, ``name``, ``art`` (siehe ARTEN), ``verlaesst_rechner`` (True / False / None = je nach Einstellung),
``zustimmung`` (was gefragt wird) und eine Funktion ``zustand(kontext) → (Kurztext, wohin)``. Neue Anbindungen tragen sich in ``INTEGRATIONEN`` ein.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

ARTEN = {
    "lokaler_prozess": "Programm, das Lunivo selbst startet und beendet",
    "lokaler_dienst": "Dienst auf diesem Rechner, den ein anderes Programm betreibt",
    "internet": "Dienst im Internet",
    "fremdprogramm": "Programm, das der Benutzer einträgt und das mit seinen Rechten läuft",
}


@dataclass(frozen=True)
class Integration:
    schluessel: str
    name: str
    art: str
    verlaesst_rechner: bool | None
    zustimmung: str
    zustand: Callable[[dict], tuple[str, str]]


def _languagetool(_k: dict) -> tuple[str, str]:
    from lunivo_writer.dienste.integrationen import languagetool as LT
    st = LT.status()
    if st["art"] == "eigen":
        return "läuft (eigener Prozess)", f"Text geht nur an 127.0.0.1:{st['port']}, den Prozess von Lunivo"
    if st["art"] == "fremd":
        return "fremder lokaler Dienst ausdrücklich erlaubt", f"Text geht an 127.0.0.1:{st['port']}"
    return ("startbereit" if LT.verfuegbar() else "nicht eingerichtet"), "Text bleibt auf diesem Rechner"


def _ki(k: dict) -> tuple[str, str]:
    ki = k.get("ki")
    if ki is None:
        return "nicht verbunden", "–"
    ziel = ki.schickt_nach_aussen()
    if ziel is None:
        return "lokal", "Text bleibt auf diesem Rechner"
    gegeben = [e for e in ki.k.einwilligungen() if e["anbieter"] == ziel]
    return ("Zustimmung liegt vor" if gegeben else "ohne Zustimmung gesperrt"), f"Text geht an {ziel} im Internet (nur nach Zustimmung)"


def _mcp(k: dict) -> tuple[str, str]:
    ki = k.get("ki")
    n = len([m for m in (ki.k["mcp"] if ki else []) if m.get("an")])
    return (f"{n} Server eingetragen" if n else "keine Server"), "Start und jeder Werkzeugaufruf werden einzeln gefragt"


INTEGRATIONEN: tuple[Integration, ...] = (
    Integration("languagetool", "LanguageTool", "lokaler_prozess", False, "keine (läuft nur lokal)", _languagetool),
    Integration("ki", "KI-Anbieter", "internet", None, "vor dem ersten Senden je Anbieter und Umfang (Auszug / ganzes Dokument)", _ki),
    Integration("mcp", "KI-Werkzeuge (MCP-Server)", "fremdprogramm", None, "vor dem Start und vor jedem Werkzeugaufruf", _mcp),
)


def uebersicht(kontext: dict | None = None) -> list[dict]:
    """Für die Datenschutzanzeige: je Integration Name, Art, Zustand, Datenweg und Zustimmung."""
    k = kontext or {}
    out = []
    for i in INTEGRATIONEN:
        zustand, wohin = i.zustand(k)
        out.append({"schluessel": i.schluessel, "name": i.name, "art": ARTEN[i.art], "zustand": zustand, "wohin": wohin, "zustimmung": i.zustimmung})
    return out
