"""Textmarken (Lesezeichen): Liste, Namen prüfen, setzen, löschen, hinspringen und interne Sprünge (``#name``)."""
from __future__ import annotations

import re

from core.suche.textsuche.suche import position_zu_offset


def lesezeichen_liste(k, versteckte: bool = True) -> list[dict]:
    """[{name, von, bis}] — Textmarken mit ihren Stellen im Rohtext. ``versteckte=False`` lässt die Marken weg, die mit „_“ beginnen
    (z. B. „_Toc…“ des Inhaltsverzeichnisses)."""
    d = k.sitzung.dokument
    aus = [{"name": n, "von": position_zu_offset(d, a.anker), "bis": position_zu_offset(d, a.kopf)} for n, a in k.sitzung.textmarken().items()]
    return sorted((x for x in aus if versteckte or not x["name"].startswith("_")), key=lambda x: x["von"])


_NAME = re.compile(r"^[A-Za-zÄÖÜäöüß][A-Za-z0-9ÄÖÜäöüß_]{0,39}$")


def lesezeichen_name_gueltig(name: str) -> bool:
    return bool(_NAME.match(name))


def lesezeichen_setzen(k, name: str) -> bool:
    """Setzt die Textmarke auf die Auswahl (ohne Auswahl: auf das Wort an der Schreibmarke); eine gleichnamige wird versetzt."""
    s = k.sitzung
    if s.auswahl.leer and not s._absatz(s.auswahl.kopf.absatz_id).text():
        return False
    return k.aendern(lambda sitz: sitz.textmarke_setzen(name))


def lesezeichen_loeschen(k, name: str) -> None:
    k.aendern(lambda s: s.textmarke_loeschen(name))


def lesezeichen_gehe(k, name: str) -> bool:
    for d in lesezeichen_liste(k):
        if d["name"] == name:
            k.auswaehlen(d["von"], d["bis"])
            return True
    return False


def intern_springen(k, href: str) -> bool:
    return href.startswith("#") and lesezeichen_gehe(k, href[1:])
