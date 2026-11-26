"""Textstellen und Auswahl eines Dokuments für die Ansicht: Abfragen und Sprünge anhand der Kennung. Eine Stelle ist ``(Absatz-Id, Zeichenstelle)``.

Die Abfragen ändern das Dokument nicht; das Setzen der Auswahl meldet nichts (die Ansicht zeigt die Stelle selbst)."""
from __future__ import annotations

import base64
import json
from collections.abc import Mapping, Sequence

from framework.anbindung import Daten, fest
from framework.sitzungen import sitzung as _steuerung

Stelle = tuple[int, int]


def _sitzung(kennung: int):
    return _steuerung._sitzungen[kennung].sitzung


def _stelle(pos) -> Stelle:
    return pos[0], pos[1]


def auswahl(kennung: int) -> tuple[Stelle, Stelle]:
    """(Anker, Kopf) der Auswahl; beide gleich: nur die Schreibmarke."""
    a = _sitzung(kennung).auswahl
    return _stelle(a.anker), _stelle(a.kopf)


def bereich(kennung: int) -> tuple[Stelle, Stelle]:
    """(Anfang, Ende) der Auswahl in Dokumentreihenfolge."""
    start, ende = _sitzung(kennung)._bereich()
    return _stelle(start), _stelle(ende)


def auswahl_setzen(kennung: int, anker: Stelle, kopf: Stelle) -> None:
    _sitzung(kennung).setze_auswahl(anker, kopf)


def gehen(kennung: int, ziel: Stelle, auswaehlen: bool) -> None:
    """Die Schreibmarke an ``ziel`` setzen; mit ``auswaehlen`` bleibt der Anker stehen."""
    s = _sitzung(kennung)
    s.setze_auswahl(s.auswahl.anker if auswaehlen else ziel, ziel)


def alles_auswaehlen(kennung: int) -> None:
    s = _sitzung(kennung)
    d = s.dokument
    s.setze_auswahl(d.anfang(), d.ende())


def zeichenformat_bei(kennung: int, stelle: Stelle) -> Mapping[str, Daten]:
    """Das Zeichenformat an der Stelle (unveränderliche Kopie)."""
    from core.dokument import Position
    return fest(dict(_sitzung(kennung).zeichenformat_bei(Position(stelle[0], stelle[1]))))


def lauf_format_bei(kennung: int, stelle: Stelle) -> Mapping[str, Daten]:
    """Das eigene Format des Textstücks, das an der Stelle beginnt bzw. sie enthält (leer am Absatzende)."""
    from core.dokument import teile
    rest = teile(_sitzung(kennung)._absatz(stelle[0]).inhalte, stelle[1])[1]
    return fest(dict(rest[0].format)) if rest else fest({})


def _zeichen_an_marke(s) -> dict:
    from core.dokument import Position
    from core.layout.drucklayout import zeichenformat
    start, _ende = s._bereich()
    a = s._absatz(start.absatz_id)
    fmt = s.zeichenformat_bei(start if s.auswahl.leer else Position(start.absatz_id, min(start.versatz + 1, a.laenge)))
    return zeichenformat(s.dokument, a, fmt)


def wirksames_zeichenformat(kennung: int) -> Mapping[str, Daten]:
    """Das wirksame Zeichenformat an der Schreibmarke (am Anfang einer Auswahl: das erste Zeichen), Vorlagen aufgelöst."""
    return fest(_zeichen_an_marke(_sitzung(kennung)))


def wirksames_absatzformat(kennung: int) -> Mapping[str, Daten]:
    """Das wirksame Absatzformat des Absatzes an der Schreibmarke, Vorlagen aufgelöst."""
    from core.layout.drucklayout import absatzformat
    s = _sitzung(kennung)
    return fest(absatzformat(s.dokument, s._absatz(s.auswahl.kopf.absatz_id)))


def absatzformat_von(kennung: int, absatz_id: int) -> Mapping[str, Daten]:
    """Das wirksame Absatzformat des Absatzes ``absatz_id``, Vorlagen aufgelöst."""
    from core.layout.drucklayout import absatzformat
    s = _sitzung(kennung)
    return fest(absatzformat(s.dokument, s._absatz(absatz_id)))


def absatz_formatwert(kennung: int, name: str) -> float:
    """Ein Zahlenwert des wirksamen Absatzformats an der Schreibmarke (0, wenn er fehlt oder keine Zahl ist)."""
    from core.layout.drucklayout import absatzformat
    s = _sitzung(kennung)
    v = absatzformat(s.dokument, s._absatz(s.auswahl.kopf.absatz_id)).get(name)
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else 0.0


def absatz_schriftgroesse(kennung: int) -> float:
    """Die Schriftgröße (pt) des Absatzes an der Schreibmarke ohne eigenes Zeichenformat (Vorlagen aufgelöst; 11, wenn keine gesetzt ist)."""
    from core.layout.drucklayout import zeichenformat
    s = _sitzung(kennung)
    return float(zeichenformat(s.dokument, s._absatz(s.auswahl.kopf.absatz_id), {}).get("groesse_pt") or 11.0)


def absatz_laenge(kennung: int, absatz_id: int) -> int:
    return _sitzung(kennung)._absatz(absatz_id).laenge


def stelle_im_text(kennung: int, stelle: Stelle) -> int:
    """Die Stelle als Zeichenstelle im Rohtext (Absätze durch ein Zeichen getrennt)."""
    from core.dokument import Position
    from core.suche.textsuche import position_zu_offset
    return position_zu_offset(_sitzung(kennung).dokument, Position(stelle[0], stelle[1]))


def stelle_von(kennung: int, im_text: int) -> Stelle:
    """Die Zeichenstelle im Rohtext als ``(Absatz-Id, Zeichenstelle)``."""
    from core.suche.textsuche import offset_zu_position
    return _stelle(offset_zu_position(_sitzung(kennung).dokument, im_text))


def objekt_vorhanden(kennung: int, objekt_id: int) -> bool:
    """Gibt es das frei positionierte Objekt (noch)?"""
    return objekt_id in _sitzung(kennung).dokument.objekte


# ---- Tabellen ------------------------------------------------------------------------------------------------------------------------
def tabellenzellen(kennung: int, absatz_id: int) -> tuple[int, int, tuple[tuple[int, int], ...], tuple[int, int]] | None:
    """Die Tabelle, in deren Zelle der Absatz steht: (Tabellen-Id, Zeilenzahl, sichtbare Zellen in Lesereihenfolge, Zelle des Absatzes);
    ``None`` im Fließtext."""
    stelle = _sitzung(kennung).tabelle_von(absatz_id)
    if stelle is None:
        return None
    t, z, sp = stelle
    zellen = tuple((zz, ss) for zz in range(t.zeilen) for ss in range(t.spalten) if t.zellen[zz][ss].verdeckt_von is None)
    return t.id, t.zeilen, zellen, tuple(t.anker(z, sp))


def sichtbare_zellen(kennung: int, tabellen_id: int) -> tuple[tuple[int, int], ...]:
    """Die sichtbaren Zellen der Tabelle (ohne verbundene, verdeckte) in Lesereihenfolge."""
    t = _sitzung(kennung)._tabelle(tabellen_id)
    return tuple((zz, ss) for zz in range(t.zeilen) for ss in range(t.spalten) if t.zellen[zz][ss].verdeckt_von is None)


def zelle_anfang(kennung: int, tabellen_id: int, zeile: int, spalte: int) -> Stelle:
    """Die erste Textstelle der Zelle."""
    return _stelle(_sitzung(kennung).zelle_anfang(tabellen_id, zeile, spalte))


def tabellenmasse(kennung: int, tabellen_id: int) -> tuple[int, int, Mapping[tuple[int, int], tuple[int, int]]]:
    """(Zeilen, Spalten, (Zeile, Spalte) → (Zeilenspanne, Spaltenspanne)) der Tabelle."""
    t = _sitzung(kennung)._tabelle(tabellen_id)
    return t.zeilen, t.spalten, fest({(z, sp): (t.zellen[z][sp].zeilenspanne, t.zellen[z][sp].spaltenspanne) for z in range(t.zeilen) for sp in range(t.spalten)})


# ---- Zwischenablage ----------------------------------------------------------------------------------------------------------------
def ausschnitt_kopieren(kennung: int) -> tuple[str, str] | None:
    """Die Auswahl für die Zwischenablage: (reiner Text, Ausschnitt mit Formaten und Bildern als JSON-Text); ``None`` ohne Auswahl."""
    from core.dokument import InlineObjekt, absaetze_in, bloecke_zu_daten
    s = _sitzung(kennung)
    if s.auswahl.leer:
        return None
    text = s.text(s.auswahl)
    bloecke = s.ausschnitt(s.auswahl)
    ressourcen = {x.ressource: base64.b64encode(s.dokument.ressourcen[x.ressource]).decode("ascii")
                  for a in absaetze_in(bloecke) for x in a.inhalte
                  if isinstance(x, InlineObjekt) and x.ressource in s.dokument.ressourcen}
    return text, json.dumps({"bloecke": bloecke_zu_daten(bloecke), "ressourcen": ressourcen})


def _ausschnitt_lesen(inhalt: str) -> tuple:
    from core.dokument import bloecke_aus_daten
    try:
        daten = json.loads(inhalt)
        bloecke = bloecke_aus_daten(daten["bloecke"])
        ressourcen = {k: base64.b64decode(v) for k, v in daten.get("ressourcen", {}).items()}
    except (ValueError, KeyError, TypeError):
        bloecke, ressourcen = [], {}
    return bloecke, ressourcen


def ausschnitt_gueltig(inhalt: str) -> bool:
    """Enthält der JSON-Text aus der Zwischenablage einen lesbaren Ausschnitt mit Inhalt?"""
    return bool(_ausschnitt_lesen(inhalt)[0])


def ausschnitt_einsetzen(kennung: int, inhalt: str) -> bool:
    """Den Ausschnitt (JSON-Text aus ``ausschnitt_kopieren``) an der Auswahl einfügen, als ein Schritt; ``False``, wenn der Kern ablehnt."""
    from core.bearbeitung import BearbeitungsFehler
    bloecke, ressourcen = _ausschnitt_lesen(inhalt)
    s = _sitzung(kennung)
    try:
        with s.gruppe("Einfügen"):
            for name, roh in ressourcen.items():
                if s.dokument.ressourcen.get(name) != roh:
                    s.ressource_setzen(name, roh)
            s.ausschnitt_einfuegen(bloecke)
    except BearbeitungsFehler:
        return False
    return True


# ---- Vorlagen und Tabellen ------------------------------------------------------------------------------------------------------------
def geruest_schreiben(kennung: int, zeilen: Sequence[str], benutzer: Mapping[str, str], heute: str) -> bool:
    """Schreibt das Gerüst einer Dokumentvorlage in das (leere) Dokument: Absätze, Auszeichnungen und die Lücken « … » zum Ausfüllen."""
    from core.bearbeitung import BearbeitungsFehler
    from core.dokument import geruest_schreiben as schreiben
    try:
        schreiben(_sitzung(kennung), zeilen, benutzer, heute)
    except BearbeitungsFehler:
        return False
    return True


def tabelle_teilen(kennung: int, tabellen_id: int, ab_zeile: int) -> bool:
    """Teilt die Tabelle oberhalb der Zeile ``ab_zeile``: Die Zeilen ab dort bilden eine neue Tabelle darunter (ein Schritt)."""
    import copy
    from core.bearbeitung import BearbeitungsFehler
    from core.dokument import Absatz, Tabelle
    s = _sitzung(kennung)
    try:
        with s.gruppe("Tabelle teilen"):
            tab = s._tabelle(tabellen_id)
            _bes, bloecke, i, _t = s.dokument.finde(tab.id)
            unten = copy.deepcopy(tab.zellen[ab_zeile:])
            breiten, hoehen = list(tab.spaltenbreiten), tab.zeilenhoehen[ab_zeile:]
            neu = Tabelle(s._id(), unten, breiten, list(hoehen), dict(tab.format))
            s._neue_ids([neu])
            for zeile in neu.zellen:                       # verdeckte Zellen verweisen auf Zeilen relativ zur neuen Tabelle
                for zelle in zeile:
                    if zelle.verdeckt_von is not None:
                        zelle.verdeckt_von = (zelle.verdeckt_von[0] - ab_zeile, zelle.verdeckt_von[1])
            s.zeilen_loeschen(tab.id, ab_zeile, tab.zeilen - ab_zeile)
            s._liste(bloecke, i + 1, 0, [Absatz(s._id()), neu])
            s._beruehrt(neu.id)
    except BearbeitungsFehler:
        return False
    return True
