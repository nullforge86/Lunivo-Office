"""Gruppenübersicht eines Reiters: je Gruppe ein Eintrag (Name und Symbol) für das Gruppen-Icon.

Der Reiter „Start“ zeigt seine Arbeitsleiste, „Datei“ die Datei-Ansicht und die Kontext-Reiter ihre Werkzeuge direkt; alle übrigen Reiter zeigen
zuerst diese Übersicht und nach dem Klick auf ein Gruppen-Icon die Befehle der Gruppe."""
from __future__ import annotations

OHNE_UEBERSICHT = ("Datei", "Start")
ZEILENWECHSEL = "//"                                   # kein Symbol, sondern die Marke für eine neue Knopfzeile


def hat_uebersicht(reiter: dict) -> bool:
    """Ob der Reiter zuerst seine Gruppen als Icons zeigt."""
    return not reiter.get("kontext") and reiter["name"] not in OHNE_UEBERSICHT


def _symbol(gruppe: dict) -> str:
    """Das Symbol der Gruppe: das eigene (``symbol``), sonst das ihres ersten Knopfes."""
    eigenes = gruppe.get("symbol")
    if eigenes:
        return eigenes
    return next((e["symbol"] for e in gruppe.get("knoepfe", []) if e.get("symbol") and e["symbol"] != ZEILENWECHSEL), "")


def kacheln(gruppe: dict) -> dict:
    """Die Gruppe für das Gruppendetail: jeder Knopf als große Kachel (Symbol oben, Text darunter), alle nebeneinander in der Reihenfolge der Gruppe.
    Befehl, Klappe, Menü und Haken jedes Knopfes bleiben, wie sie sind; Eingabefelder bleiben Felder."""
    knoepfe = [e if e.get("feld") else dict(e, gross=True)
               for e in gruppe.get("knoepfe", []) if not e.get("zeilenumbruch") and e.get("symbol") != ZEILENWECHSEL]
    return dict(gruppe, knoepfe=knoepfe)


def uebersicht(reiter: dict) -> list[dict]:
    """Die Gruppen-Icons des Reiters in der Reihenfolge seiner Gruppen; ``kachel`` im Gruppeneintrag nennt eine eigene Beschriftung."""
    return [{"name": g.get("kachel") or g["name"], "symbol": _symbol(g)} for g in reiter["gruppen"]]
