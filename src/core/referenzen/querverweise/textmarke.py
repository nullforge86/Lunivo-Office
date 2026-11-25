"""Textmarken (Lesezeichen): Liste, Namen prüfen, setzen, löschen, hinspringen und interne Sprünge (``#name``)."""
from __future__ import annotations

import re

from core.suche.textsuche.suche import position_zu_offset


def lesezeichen_liste(ed, versteckte: bool = True) -> list[dict]:
    """[{name, von, bis}] — Textmarken mit ihren Stellen im Rohtext. ``versteckte=False`` lässt die Marken weg, die mit „_“ beginnen
    (z. B. „_Toc…“ des Inhaltsverzeichnisses)."""
    d = ed.sitzung.dokument
    aus = [{"name": n, "von": position_zu_offset(d, a.anker), "bis": position_zu_offset(d, a.kopf)} for n, a in ed.sitzung.textmarken().items()]
    return sorted((x for x in aus if versteckte or not x["name"].startswith("_")), key=lambda x: x["von"])


_NAME = re.compile(r"^[A-Za-zÄÖÜäöüß][A-Za-z0-9ÄÖÜäöüß_]{0,39}$")


def lesezeichen_name_gueltig(name: str) -> bool:
    return bool(_NAME.match(name))


def lesezeichen_setzen(ed, name: str) -> bool:
    """Setzt die Textmarke auf die Auswahl (ohne Auswahl: auf das Wort an der Schreibmarke); eine gleichnamige wird versetzt."""
    s = ed.sitzung
    if s.auswahl.leer and not s._absatz(s.auswahl.kopf.absatz_id).text():
        return False
    return ed.ansicht._aendern(lambda sitz: sitz.textmarke_setzen(name))


def lesezeichen_loeschen(ed, name: str) -> None:
    ed.ansicht._aendern(lambda s: s.textmarke_loeschen(name))


def lesezeichen_gehe(ed, name: str) -> bool:
    for d in lesezeichen_liste(ed):
        if d["name"] == name:
            ed.select_range(d["von"], d["bis"])
            ed.ensureCursorVisible()
            return True
    return False


def intern_springen(ed, href: str) -> bool:
    return href.startswith("#") and lesezeichen_gehe(ed, href[1:])
