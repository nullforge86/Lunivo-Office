"""Anbindung an ``core.listen.mehrstufig.mehrstufig``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Collection, Hashable, Mapping, Sequence
from functools import cache

import core.listen.mehrstufig as _k
from framework.anbindung import fest


@cache
def ebenen() -> int:
    return fest(_k.EBENEN)


@cache
def glyphen() -> tuple[str, ...]:
    return fest(_k.GLYPHEN)


@cache
def platzhalter() -> str:
    return fest(_k.PLATZHALTER)


@cache
def vorlagen() -> tuple[tuple[str, Mapping[str, Sequence[Mapping[Collection | Hashable, Collection | Hashable]]]], ...]:
    return fest(_k.VORLAGEN)


def aufzaehlung(zeichen: str) -> Mapping:
    """Aufzählung mit einem Zeichen (◆ ✤ ➤ ✓ ✧ …), das Lunivo selbst zeichnet; Ebenen wie bei einer Gliederung eingerückt."""
    return fest(_k.aufzaehlung(zeichen))


def ebene_aus(x: Mapping) -> Mapping:
    """Eine Ebene aus einem Wörterbuch (JSON, Dialog) mit allen bekannten Feldern neu aufbauen."""
    return fest(_k.ebene_aus(x))


def ist_aufzaehlung(defn: Mapping) -> bool:
    """Gliederung ohne einen einzigen Platzhalter für Nummern: eine Aufzählung mit eigenem Zeichen."""
    return fest(_k.ist_aufzaehlung(defn))


def liste_als_text(spec: Mapping | None) -> str:
    """Eine Liste (einfach oder mehrstufig) als Text für eine Formatvorlage; ein leerer Text heißt: keine Liste."""
    return fest(_k.liste_als_text(spec))


def liste_aus_text(text: str | None) -> Mapping | None:
    """Die Liste (einfach oder mehrstufig) aus dem Text einer Formatvorlage."""
    return fest(_k.liste_aus_text(text))


def nummer_der_ebene(defn: Mapping, zaehler: Sequence[int], ebene_nr: int) -> str:
    """Die Nummer als Text für einen Absatz der Ebene ``ebene_nr`` (1…9) bei diesen Zählerständen."""
    return fest(_k.nummer_der_ebene(defn, zaehler, ebene_nr))
