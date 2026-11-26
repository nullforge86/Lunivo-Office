"""Ausgabe eines Dokuments für Druck, Druckvorschau und Bildexport: einmal gesetzt, jede Seite lässt sich in beliebiger Auflösung rastern oder
als PDF schreiben – dieselbe Layoutberechnung und derselbe Renderer wie die Zeichenfläche.

Das Framework hält die Ausgabe unter einer Nummer; die Oberfläche gibt nur diese Nummer, Seitenindex und Maßstab."""
from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence

from framework.schnittstellen import BlasenEinstellung, Sprechblase
from framework.sitzungen import sitzung as _steuerung
from framework.zeichnen import Rasterbild

STANDARD_BLATT_MM = (210.0, 297.0)


class _Anschluss:
    """Der Änderungs-Port (``lesen``/``aendern``) für ein Dokument ohne Editor: jede Anfrage läuft auf einer eigenen Sitzung über dasselbe Dokument."""

    def __init__(self, dokument):
        self._dokument = dokument

    def _sitzung(self):
        from core.bearbeitung import Bearbeitungssitzung
        return Bearbeitungssitzung(self._dokument)

    def lesen(self, abfrage):
        return abfrage(self._sitzung())

    def aendern(self, aenderung) -> bool:
        aenderung(self._sitzung())
        return True


class _Ausgabe:
    def __init__(self, dokument, versteckt: bool, blasen: BlasenEinstellung | None):
        from core.layout import LayoutEngine
        from core.layout.drucklayout import schrift
        from core.layout.drucklayout.ausgabe import DokumentRenderer
        self.dokument = dokument
        self.layout_opt = {"versteckt": True} if versteckt else None
        self.layout = LayoutEngine(None, self.layout_opt)
        self.erg = self.layout.berechnen(dokument)
        self.blasen_je_seite = self._blasen_sammeln(blasen) if blasen else {}
        self.renderer = DokumentRenderer(self.layout.engine)
        self.grund = schrift(dict(dokument.standardformat))

    def _blasen_sammeln(self, k: BlasenEinstellung) -> dict:
        """Seite (0-basiert) → [(Blase, y der Textstelle auf dem Blatt)] der Kommentare und Änderungen, die als Sprechblasen neben der Seite stehen."""
        from core.suche.textsuche import offset_zu_position
        from framework.befehle.ansicht.sprechblasen import aktiv, sammeln
        if not aktiv(k):
            return {}
        je_seite: dict = {}
        for bl in sammeln(_Anschluss(self.dokument), k.verwenden):    # nur lesen: dasselbe Dokument, keine Kopie
            pos = offset_zu_position(self.dokument, bl.von)
            stelle = self.erg.cursor(pos.absatz_id, pos.versatz)
            if stelle is not None:
                je_seite.setdefault(stelle[0], []).append((bl, stelle[1].y))
        return je_seite


_AUSGABEN: dict[int, _Ausgabe] = {}
_naechste = [1]


def _anlegen(dokument, versteckt: bool = False, blasen: BlasenEinstellung | None = None) -> int:
    nummer = _naechste[0]
    _naechste[0] += 1
    _AUSGABEN[nummer] = _Ausgabe(dokument, versteckt, blasen)
    return nummer


def ausgabe_oeffnen(kennung: int, nur_formular: bool = False, versteckt: bool = False, blasen: BlasenEinstellung | None = None) -> int:
    """Das Dokument ``kennung`` für die Ausgabe setzen; → Nummer der Ausgabe. ``nur_formular``: in einer Kopie bleibt nur der Inhalt der Felder sichtbar;
    ``versteckt``: ausgeblendeten Text mitsetzen; ``blasen``: Kommentare und Änderungen als Sprechblasen neben der Seite."""
    dokument = _steuerung._sitzungen[kennung].sitzung.dokument
    if nur_formular:
        from framework.befehle.felder import nur_formulardaten
        dokument = copy.deepcopy(dokument)
        nur_formulardaten(_Anschluss(dokument))
    return _anlegen(dokument, versteckt, blasen)


def ausgabe_aus_geruest(zeilen: Sequence[str], benutzer: Mapping[str, str], heute: str) -> int:
    """Die Ausgabe eines neuen Dokuments mit dem Gerüst einer Dokumentvorlage (für das Vorschaubild der Vorlage); → Nummer der Ausgabe."""
    from core.bearbeitung import Bearbeitungssitzung
    from core.dokument import geruest_schreiben, neues_dokument
    sitzung = Bearbeitungssitzung(neues_dokument())
    geruest_schreiben(sitzung, zeilen, benutzer, heute)
    return _anlegen(sitzung.dokument)


def ausgabe_aus_datei(pfad: str) -> int:
    """Die Ausgabe einer Datei (für das Vorschaubild einer Vorlage); → Nummer der Ausgabe. Eine Datei, die sich nicht lesen lässt, löst den Fehler des Ladens aus."""
    from framework.dokumentverwaltung.dateizugriff import lade_modell
    return _anlegen(lade_modell(pfad).document)


def ausgabe_schliessen(nummer: int) -> None:
    _AUSGABEN.pop(nummer, None)


def ausgabe_anzahl(nummer: int) -> int:
    return len(_AUSGABEN[nummer].erg.seiten)


def ausgabe_seite_mm(nummer: int, index: int) -> tuple[float, float]:
    """Breite und Höhe der Seite ``index`` (ab 0) in Millimetern."""
    e = _AUSGABEN[nummer].erg.seiten[index].einrichtung
    return (e.width_mm, e.height_mm) if e is not None else STANDARD_BLATT_MM


def ausgabe_blasen(nummer: int, index: int) -> tuple[tuple[Sprechblase, float], ...]:
    """(Blase, y der Textstelle auf dem Blatt) der Sprechblasen neben der Seite ``index``."""
    return tuple(_AUSGABEN[nummer].blasen_je_seite.get(index, ()))


def ausgabe_seitenbild(nummer: int, index: int, faktor: float, wasserzeichen: str = "", wasserzeichen_farbe: str = "") -> Rasterbild:
    """Die Seite ``index`` in der Auflösung ``faktor``; ``wasserzeichen``: Text, der schräg und blass über der Seite steht (Bildexport)."""
    from core.geometrie import Rect, mm_to_px
    from core.layout.drucklayout.ausgabe import RasterZiel
    a = _AUSGABEN[nummer]
    einr = a.erg.seiten[index].einrichtung
    b, h = (mm_to_px(einr.width_mm), mm_to_px(einr.height_mm)) if einr is not None else (mm_to_px(210), mm_to_px(297))
    ziel = RasterZiel(a.layout.engine, b, h, faktor)
    a.renderer.zeichne_seite(ziel, a.dokument, a.erg, index, a.grund)
    if wasserzeichen:
        from core.layout.drucklayout.ausgabe.seite import zeichne
        zeichne(ziel, a.layout.engine, {"text": wasserzeichen, "farbe": wasserzeichen_farbe, "transparenz": 73, "winkel": -35}, Rect(0, 0, b, h))
    breite, hoehe, roh = ziel.als_rgba()
    return Rasterbild(breite, hoehe, bytes(roh))


def ausgabe_als_pdf(nummer: int, ziel: str, seiten: Sequence[int]) -> int:
    """Die Seiten ``seiten`` (ab 1, in dieser Reihenfolge) als Vektor-PDF nach ``ziel`` schreiben; → Zahl der geschriebenen Seiten."""
    from filter.pdf import dokument_als_pdf
    a = _AUSGABEN[nummer]
    return dokument_als_pdf(a.dokument, ziel, seiten=list(seiten), layout_optionen=a.layout_opt)
