"""Anbindung der Oberfläche an ``core.listen.mehrstufig.mehrstufig`` über ``framework.anbindung.mehrstufig``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import cache

import framework.anbindung.mehrstufig as _fw
from writer.werte import eigene_kopie


@cache
def ebenen():
    return eigene_kopie(_fw.ebenen())


@cache
def glyphen():
    return eigene_kopie(_fw.glyphen())


@cache
def platzhalter():
    return eigene_kopie(_fw.platzhalter())


@cache
def vorlagen():
    return eigene_kopie(_fw.vorlagen())


def aufzaehlung(zeichen: str) -> Mapping:
    """Aufzählung mit einem Zeichen (◆ ✤ ➤ ✓ ✧ …), das Lunivo selbst zeichnet; Ebenen wie bei einer Gliederung eingerückt."""
    return eigene_kopie(_fw.aufzaehlung(zeichen))


def ebene_aus(x: Mapping) -> Mapping:
    """Eine Ebene aus einem Wörterbuch (JSON, Dialog) mit allen bekannten Feldern neu aufbauen."""
    return eigene_kopie(_fw.ebene_aus(x))


def ist_aufzaehlung(defn: Mapping) -> bool:
    """Gliederung ohne einen einzigen Platzhalter für Nummern: eine Aufzählung mit eigenem Zeichen."""
    return eigene_kopie(_fw.ist_aufzaehlung(defn))


def liste_als_text(spec: Mapping | None) -> str:
    """Eine Liste (einfach oder mehrstufig) als Text für eine Formatvorlage; ein leerer Text heißt: keine Liste."""
    return eigene_kopie(_fw.liste_als_text(spec))


def liste_aus_text(text: str | None) -> Mapping | None:
    """Die Liste (einfach oder mehrstufig) aus dem Text einer Formatvorlage."""
    return eigene_kopie(_fw.liste_aus_text(text))


def nummer_der_ebene(defn: Mapping, zaehler: Sequence[int], ebene_nr: int) -> str:
    """Die Nummer als Text für einen Absatz der Ebene ``ebene_nr`` (1…9) bei diesen Zählerständen."""
    return eigene_kopie(_fw.nummer_der_ebene(defn, zaehler, ebene_nr))


def zaehlen(zaehler: list[int], defn: dict, ebene_nr: int) -> None:
    """Zählerstand nach einem Absatz der Ebene ``ebene_nr``: diese Ebene weiter, tiefere neu (``zaehler`` wird fortgeschrieben)."""
    zaehler[:] = _fw.zaehlen(zaehler, defn, ebene_nr)
