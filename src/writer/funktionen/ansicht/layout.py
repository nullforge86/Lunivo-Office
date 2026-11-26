"""Das gesetzte Dokument für die Oberfläche: Das Framework rechnet und hält das Layout; hier entstehen daraus die Werte der Oberfläche
(``Rechteck``, ``Punkt``, ``Stelle``). Die Oberfläche bekommt nie ein Objekt des Kerns."""
from __future__ import annotations

from typing import NamedTuple

from framework.befehle import ansicht as _fw
from writer.werte import Punkt, Rechteck, Stelle


class Platz(NamedTuple):
    """Ein Stück Seite: Absatzzeile, Tabellenzelle, Rahmen, freies Objekt, Note oder der Trennstrich über den Noten."""
    art: str
    rect: Rechteck
    block_id: int
    zeile: int
    spalte: int
    kopie: bool


class Seite(NamedTuple):
    index: int
    abschnitt: int
    einrichtung: _fw.Blattangabe | None
    plaetze: tuple[Platz, ...]
    oben: float
    nummer: int
    breite_px: float
    hoehe_px: float


class _Seiten:
    """Die Seiten des Layouts; jede wird beim ersten Zugriff vom Framework geholt."""

    def __init__(self, kennung: int):
        self._kennung = kennung
        self._anzahl = _fw.layout_seitenzahl(kennung)
        self._geholt: dict[int, Seite] = {}

    def __len__(self) -> int:
        return self._anzahl

    def __getitem__(self, i: int) -> Seite:
        if i < 0:
            i += self._anzahl
        if not 0 <= i < self._anzahl:
            raise IndexError(i)
        seite = self._geholt.get(i)
        if seite is None:
            s = _fw.layout_seite(self._kennung, i)
            seite = self._geholt[i] = Seite(s.index, s.abschnitt, s.einrichtung,
                                            tuple(Platz(p.art, Rechteck(*p.rect), p.block_id, p.zeile, p.spalte, p.kopie) for p in s.plaetze),
                                            s.oben, s.nummer, s.breite_px, s.hoehe_px)
        return seite

    def __iter__(self):
        return (self[i] for i in range(self._anzahl))


class Layoutsicht:
    """Ein Stand des Layouts eines Dokuments: Seiten, Plätze, Objekte und Stellen als Werte der Oberfläche."""

    def __init__(self, kennung: int):
        self.kennung = kennung
        self.stand = _fw.layout_berechnen(kennung)
        self.seiten = _Seiten(kennung)
        self._objekte: dict | None = None
        self._blattmasse: tuple | None = None
        self._reihenfolge: list | None = None

    @property
    def blattmasse(self) -> tuple:
        """Je Seite (Breite und Höhe in Bildpunkten im Weblayout, sonst 0; Blattbreite und -höhe in mm oder ``None``; y der Blattoberkante im Blattraum)."""
        if self._blattmasse is None:
            self._blattmasse = _fw.layout_blattmasse(self.kennung)
        return self._blattmasse

    @property
    def objekte(self) -> dict:
        """Id eines freien Objekts → (Seitenindex, Rechteck)."""
        if self._objekte is None:
            self._objekte = {oid: (seite, Rechteck(*r)) for oid, (seite, r) in _fw.layout_objekte(self.kennung).items()}
        return self._objekte

    @property
    def reihenfolge(self) -> list:
        """Ids der gesetzten Absätze in Lesereihenfolge."""
        if self._reihenfolge is None:
            self._reihenfolge = list(_fw.layout_reihenfolge(self.kennung))
        return self._reihenfolge

    def cursor(self, absatz_id: int, index: int):
        """(Seite, Punkt) der oberen linken Ecke der Zeile, in der die Schreibmarke vor dem Zeichen ``index`` steht."""
        c = _fw.layout_cursor(self.kennung, (absatz_id, index))
        return None if c is None else (c[0], Punkt(*c[1]))

    def treffer(self, seite: int, punkt) -> Stelle | None:
        """Die Textstelle für einen Punkt auf der Seite (die nächste Textzeile); ``None``, wenn die Seite keinen Text hat."""
        t = _fw.layout_treffer(self.kennung, seite, punkt.x, punkt.y)
        return None if t is None else Stelle(*t)

    def objekt_bei(self, seite: int, punkt) -> int | None:
        """Id des obersten freien Objekts an dem Punkt der Seite, sonst ``None``."""
        return _fw.layout_objekt_bei(self.kennung, seite, punkt.x, punkt.y)

    def seite_von(self, absatz_id: int) -> int | None:
        """Der Index der Seite, auf der der Absatz beginnt."""
        return _fw.layout_seite_von(self.kennung, absatz_id)


def berechnen(kennung: int) -> Layoutsicht:
    """Das Layout zum jetzigen Stand des Dokuments (nur nach ``verwerfen`` neu gerechnet)."""
    return Layoutsicht(kennung)


def verwerfen(kennung: int) -> None:
    """Das Dokument oder eine Option hat sich geändert: beim nächsten Zugriff wird neu gesetzt."""
    _fw.layout_verwerfen(kennung)


def option_setzen(kennung: int, name: str, wert) -> bool:
    """Eine Option des Layouts der Ansicht; → ob sie sich geändert hat."""
    return _fw.layout_option_setzen(kennung, name, wert)


def cursor_rechteck(kennung: int, stelle: tuple[int, int]) -> tuple[int, Rechteck] | None:
    """(Seitenindex, Rechteck der Schreibmarke) an der Stelle oder ``None``, wenn der Absatz nicht gesetzt ist."""
    c = _fw.layout_cursor_rechteck(kennung, (stelle[0], stelle[1]))
    return None if c is None else (c[0], Rechteck(*c[1]))


def bewegen(kennung: int, stelle: tuple[int, int], art: str, x: float | None = None) -> tuple[Stelle, float | None]:
    """Die Stelle nach der Bewegung ``art`` und der gemerkte x-Wert (Spalte bei „hoch“/„runter“)."""
    ziel, x_neu = _fw.layout_bewegen(kennung, (stelle[0], stelle[1]), art, x)
    return Stelle(*ziel), x_neu


def wort_bei(kennung: int, stelle: tuple[int, int]) -> tuple[Stelle, Stelle]:
    """Anfang und Ende des Wortes an der Stelle (für den Doppelklick)."""
    von, bis = _fw.layout_wort_bei(kennung, (stelle[0], stelle[1]))
    return Stelle(*von), Stelle(*bis)


def silben_setzen(kennung: int, einstellung) -> bool:
    """Lesehilfe „Silbenfarben“ für das Layout der Ansicht (``einstellung``: ``SilbenEinstellung`` vom Framework); → ob sich die Option geändert hat."""
    return _fw.layout_silben_setzen(kennung, einstellung)
