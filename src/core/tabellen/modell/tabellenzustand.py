"""Der Zustand der Schreibmarke gegenüber einer Tabelle - an einer Stelle festgelegt (keine Oberfläche).

    zustand(sitzung, nur_lesen=False)                                        # einer der Namen unten
    tabellenmodus(sitzung, nur_lesen=False, rechtsklick=False, per_griff=False)   # True = Tabellenfunktionen anbieten

``sitzung`` ist die Bearbeitungssitzung; maßgeblich ist ihre Auswahl (Anker und Kopf).

Zustände: ``aussen`` (nicht in einer Tabelle) · ``text_in_zelle`` (Schreibmarke oder Text innerhalb einer Zelle) · ``mehrere_zellen`` ·
``ganze_tabelle`` · ``einzelzelle_ganz`` (Tabelle mit nur einer Zelle, deren Inhalt ganz markiert ist) · ``nur_lesen``.

Regel: Tabellenfunktionen bei mehreren Zellen, ganzer Tabelle, über den Verschiebegriff und beim Rechtsklick ohne Textmarkierung in einer Zelle.
Nur Textfunktionen bei Text in einer Zelle oder außerhalb; nie im Nur-Lesen-Modus.
"""
from __future__ import annotations

from core.dokument import Position, absaetze_in
from core.suche.textsuche import position_zu_offset

AUSSEN, TEXT_IN_ZELLE, MEHRERE_ZELLEN, GANZE_TABELLE, EINZELZELLE_GANZ, NUR_LESEN = (
    "aussen", "text_in_zelle", "mehrere_zellen", "ganze_tabelle", "einzelzelle_ganz", "nur_lesen")


def _zelle_ganz(sitzung, tabelle, zeile: int, spalte: int) -> bool:
    """Deckt die Auswahl den ganzen Inhalt der Zelle ab?"""
    absaetze = list(absaetze_in(tabelle.zellen[zeile][spalte].bloecke))
    if not absaetze:
        return False
    d, aus = sitzung.dokument, sitzung.auswahl
    a, k = position_zu_offset(d, aus.anker), position_zu_offset(d, aus.kopf)
    return (min(a, k) <= position_zu_offset(d, Position(absaetze[0].id, 0))
            and max(a, k) >= position_zu_offset(d, Position(absaetze[-1].id, absaetze[-1].laenge)))


def zustand(sitzung, nur_lesen: bool = False) -> str:
    if sitzung is None:
        return AUSSEN
    if nur_lesen:
        return NUR_LESEN
    aus = sitzung.auswahl
    am_kopf = sitzung.tabelle_von(aus.kopf.absatz_id)
    if am_kopf is None:
        return AUSSEN
    if aus.leer:
        return TEXT_IN_ZELLE
    tabelle, z_k, s_k = am_kopf
    am_anker = sitzung.tabelle_von(aus.anker.absatz_id)
    if am_anker is None or am_anker[0] is not tabelle:
        return MEHRERE_ZELLEN                                          # die Auswahl reicht über die Tabelle hinaus
    _t, z_a, s_a = am_anker
    if (z_a, s_a) == (z_k, s_k):
        if tabelle.zeilen * tabelle.spalten == 1 and _zelle_ganz(sitzung, tabelle, z_k, s_k):
            return EINZELZELLE_GANZ
        return TEXT_IN_ZELLE
    zeilen, spalten = abs(z_a - z_k) + 1, abs(s_a - s_k) + 1
    return GANZE_TABELLE if zeilen >= tabelle.zeilen and spalten >= tabelle.spalten else MEHRERE_ZELLEN


def tabellenmodus(sitzung, nur_lesen: bool = False, rechtsklick: bool = False, per_griff: bool = False) -> bool:
    """``True``, wenn Tabellenfunktionen (Einfügen/Löschen, Rahmen, Schattierung …) angeboten werden."""
    z = zustand(sitzung, nur_lesen)
    if z in (AUSSEN, NUR_LESEN):
        return False
    if per_griff:                                                  # Verschiebegriff: auch bei einer Tabelle mit nur einer Zelle
        return True
    if z in (MEHRERE_ZELLEN, GANZE_TABELLE):
        return True
    if z == TEXT_IN_ZELLE:
        return bool(rechtsklick) and sitzung.auswahl.leer
    return False                                                   # einzelzelle_ganz ohne Griff: nur Text
