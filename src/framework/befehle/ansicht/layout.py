"""Das gesetzte Dokument der Ansicht: Das Framework rechnet und hält das Layout je Dokument; die Oberfläche fragt nur nach Seiten, Plätzen,
Treffern und Stellen – als unveränderliche Angaben und einfache Tupel. Koordinaten sind Bildpunkte in Seitenkoordinaten (96 dpi).

Eine Stelle ist ``(Absatz-Id, Zeichenstelle)``, ein Rechteck ``(x, y, Breite, Höhe)``."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from framework.anbindung import Daten
from framework.schnittstellen import SilbenEinstellung
from framework.sitzungen import sitzung as _steuerung

Stelle = tuple[int, int]
Kasten = tuple[float, float, float, float]


@dataclass(frozen=True)
class Blattangabe:
    """Maße des Blattes einer Seite (aus der Seiteneinrichtung des Abschnitts)."""
    width_mm: float
    height_mm: float
    margin_left_mm: float
    margin_top_mm: float
    margin_right_mm: float
    margin_bottom_mm: float
    content_width_px: float
    content_height_px: float


@dataclass(frozen=True)
class Platzangabe:
    """Ein Stück Seite: Absatzzeile, Tabellenzelle, Rahmen, freies Objekt, Note oder der Trennstrich über den Noten."""
    art: str
    rect: Kasten
    block_id: int
    zeile: int
    spalte: int
    kopie: bool


@dataclass(frozen=True)
class Seitenangabe:
    index: int
    abschnitt: int
    einrichtung: Blattangabe | None
    plaetze: tuple[Platzangabe, ...]
    oben: float
    nummer: int
    breite_px: float
    hoehe_px: float


class _Layout:
    """Layoutrechner, Optionen und Ergebnis eines Dokuments; ``stand`` zählt die Berechnungen."""

    def __init__(self) -> None:
        from core.layout import LayoutEngine
        from core.layout.drucklayout.ausgabe import DokumentRenderer
        self.optionen: dict = {}
        self.rechner = LayoutEngine(None, self.optionen)
        self.renderer = DokumentRenderer(self.rechner.engine)
        self.erg = None
        self.stand = 0
        self.markup = None                 # (Stand, Schalter, Farben, Flächen je Seite)
        self.ueber = None                  # (Überlagerung, Flächen je Seite) des letzten Zeichnens
        self.ueber_stand: dict = {}        # Seite → (Schlüssel, Nummer)
        self.ueber_nummer = 0


def _layout(kennung: int) -> _Layout:
    satz = _steuerung._sitzungen[kennung]
    if satz.ansichtslayout is None:
        satz.ansichtslayout = _Layout()
    return satz.ansichtslayout


def _sitzung(kennung: int):
    return _steuerung._sitzungen[kennung].sitzung


def _ergebnis(kennung: int):
    l = _layout(kennung)
    if l.erg is None:
        l.erg = l.rechner.berechnen(_sitzung(kennung).dokument)
        l.stand += 1
    return l.erg


def _kasten(r) -> Kasten:
    return r.x, r.y, r.width, r.height


def _position(stelle: Stelle):
    from core.dokument import Position
    return Position(int(stelle[0]), int(stelle[1]))


def berechnen(kennung: int) -> int:
    """Das Layout zum jetzigen Stand des Dokuments (nur nach ``verwerfen`` neu gerechnet); → Nummer des Standes."""
    _ergebnis(kennung)
    return _layout(kennung).stand


def verwerfen(kennung: int) -> None:
    """Das Dokument oder eine Option hat sich geändert: beim nächsten Zugriff wird neu gesetzt."""
    satz = _steuerung._sitzungen.get(kennung)
    if satz is not None and satz.ansichtslayout is not None:
        satz.ansichtslayout.erg = None


def option_setzen(kennung: int, name: str, wert: Daten) -> bool:
    """Eine Option des Layouts der Ansicht (``buchstaben``, ``wort``, ``zeilenluft``, ``versteckt``, ``web``, ``gliederung`` …); → ob sie sich geändert hat."""
    l = _layout(kennung)
    if l.optionen.get(name) == wert:
        return False
    l.optionen[name] = wert
    return True


def silben_setzen(kennung: int, einstellung: SilbenEinstellung | None) -> bool:
    """Lesehilfe „Silbenfarben“ für das Layout der Ansicht (reine Anzeige, das Dokument bleibt unverändert); → ob sich die Option geändert hat."""
    wert = None
    if einstellung and einstellung.an:
        from core.layout.drucklayout.ausgabe import rgba
        from framework.befehle.ansicht.silbenfarben import farben, silben
        wert = {"funktion": lambda w: silben(w, einstellung.sprache), "farben": [rgba(f) for f in farben(einstellung)], "darstellung": einstellung.darstellung,
                "einsilbig": einstellung.einsilbig, "neu_pro_wort": einstellung.neu_pro_wort, "mindestens": einstellung.mindestens}
    l = _layout(kennung)
    if l.optionen.get("silben") == wert:
        return False
    l.optionen["silben"] = wert
    return True


def seitenzahl(kennung: int) -> int:
    return len(_ergebnis(kennung).seiten)


def blattmasse(kennung: int) -> tuple[tuple[float, float, float | None, float | None, float], ...]:
    """Je Seite (Breite und Höhe in Bildpunkten im Weblayout, sonst 0; Blattbreite und -höhe in mm oder ``None``; y der Blattoberkante im Blattraum)."""
    return tuple((s.breite_px, s.hoehe_px, None if s.einrichtung is None else s.einrichtung.width_mm,
                  None if s.einrichtung is None else s.einrichtung.height_mm, s.oben) for s in _ergebnis(kennung).seiten)


def seite(kennung: int, index: int) -> Seitenangabe:
    """Die Seite ``index`` mit ihren Plätzen."""
    s = _ergebnis(kennung).seiten[index]
    e = s.einrichtung
    blatt = None if e is None else Blattangabe(e.width_mm, e.height_mm, e.margin_left_mm, e.margin_top_mm, e.margin_right_mm, e.margin_bottom_mm,
                                               e.content_width_px, e.content_height_px)
    return Seitenangabe(s.index, s.abschnitt, blatt, tuple(Platzangabe(p.art, _kasten(p.rect), p.block_id, p.zeile, p.spalte, p.kopie) for p in s.plaetze),
                        s.oben, s.nummer, s.breite_px, s.hoehe_px)


def objekte(kennung: int) -> Mapping[int, tuple[int, Kasten]]:
    """Id eines freien Objekts → (Seitenindex, Rechteck)."""
    return MappingProxyType({oid: (seite_nr, _kasten(r)) for oid, (seite_nr, r) in _ergebnis(kennung).objekte.items()})


def cursor(kennung: int, stelle: Stelle) -> tuple[int, tuple[float, float]] | None:
    """(Seite, Punkt) der oberen linken Ecke der Zeile, in der die Schreibmarke vor der Stelle steht."""
    c = _ergebnis(kennung).cursor(stelle[0], stelle[1])
    return None if c is None else (c[0], (c[1].x, c[1].y))


def cursor_rechteck(kennung: int, stelle: Stelle) -> tuple[int, Kasten] | None:
    """(Seitenindex, Rechteck der Schreibmarke) an der Stelle oder ``None``, wenn der Absatz nicht gesetzt ist."""
    from core.layout.drucklayout import cursor_rechteck as _cursor_rechteck
    c = _cursor_rechteck(_ergebnis(kennung), _position(stelle))
    return None if c is None else (c[0], _kasten(c[1]))


def treffer(kennung: int, seite_nr: int, x: float, y: float) -> Stelle | None:
    """Die Textstelle für einen Punkt auf der Seite (die nächste Textzeile); ``None``, wenn die Seite keinen Text hat."""
    from core.geometrie import Point
    t = _ergebnis(kennung).treffer(seite_nr, Point(x, y))
    return None if t is None else (t[0], t[1])


def objekt_bei(kennung: int, seite_nr: int, x: float, y: float) -> int | None:
    """Id des obersten freien Objekts an dem Punkt der Seite, sonst ``None``."""
    from core.geometrie import Point
    return _ergebnis(kennung).objekt_bei(seite_nr, Point(x, y))


def seite_von(kennung: int, absatz_id: int) -> int | None:
    """Der Index der Seite, auf der der Absatz beginnt."""
    return _ergebnis(kennung).seite_von(absatz_id)


def reihenfolge(kennung: int) -> tuple[int, ...]:
    """Ids der gesetzten Absätze in Lesereihenfolge."""
    return tuple(_ergebnis(kennung).reihenfolge)


def bewegen(kennung: int, stelle: Stelle, art: str, x: float | None = None) -> tuple[Stelle, float | None]:
    """Die Stelle nach der Bewegung ``art`` und der gemerkte x-Wert (Spalte bei „hoch“/„runter“)."""
    from core.layout.drucklayout import bewegen as _bewegen
    ziel, x_neu = _bewegen(_ergebnis(kennung), _position(stelle), art, x)
    return (ziel[0], ziel[1]), x_neu


def wort_bei(kennung: int, stelle: Stelle) -> tuple[Stelle, Stelle]:
    """Anfang und Ende des Wortes an der Stelle (für den Doppelklick)."""
    from core.layout.drucklayout import wort_bei as _wort_bei
    von, bis = _wort_bei(_ergebnis(kennung), _position(stelle))
    return (von[0], von[1]), (bis[0], bis[1])
