"""Die Layout-Engine: legt ein ``Dokument`` auf Seiten. Ohne Qt."""
from __future__ import annotations

from lunivo_writer.kern.dokument.dokument import Dokument, absaetze_in
from lunivo_writer.kern.dokument.listen import listenmarken
from lunivo_writer.kern.textsatz.engine import TextLayoutEngine
from .ergebnis import Ergebnis
from .kopf_fusslayout import kopf_fuss_setzen
from .geometrie import WEB_RAND
from .seitenlayout import _Fluss


class LayoutEngine:
    """Berechnet das Layout eines ``Dokument``. ``engine`` liefert Schriftmaße und Vorschübe (Standard: ``HarfBuzzEngine``)."""

    def __init__(self, engine: TextLayoutEngine | None = None, optionen: dict | None = None):
        self.optionen = optionen if optionen is not None else {}      # Ansicht: buchstaben, wort, zeilenluft (Lesehilfe), versteckt (Text zeigen)
        if engine is None:
            from ..schrift import HarfBuzzEngine
            engine = HarfBuzzEngine()
        self.engine = engine

    def berechnen(self, dok: Dokument) -> Ergebnis:
        """Das Dokument auf Seiten legen."""
        frei_an: dict = {}
        for o in dok.objekte.values():
            frei_an.setdefault(o.anker, []).append(o)
        f = _Fluss(self.engine, dok, listenmarken(dok), frei_an, self.optionen)
        for nr, abschnitt in enumerate(dok.abschnitte):
            f.abschnitt_beginnt(nr, abschnitt)
            f.blocks(abschnitt.bloecke)
        if not f.erg.seiten:
            f.neue_seite()
        f.endnoten_setzen()
        if self.optionen.get("web"):
            seite = f.erg.seiten[0]
            seite.breite_px = float(self.optionen["web"])
            seite.hoehe_px = max([p.rect.bottom for p in seite.plaetze] + [f.rand_oben + f.y]) + WEB_RAND
        else:
            f.noten_platzieren()
            kopf_fuss_setzen(self.engine, dok, f.erg)
        f.erg.reihenfolge = [a.id for a in dok.absaetze() if a.id in f.erg.absaetze and f.erg.absaetze[a.id].zeilen]
        return f.erg

    def hoehe_von_bloecken(self, dok: Dokument, bloecke: list, breite: float) -> float:
        """Summe der Zeilenhöhen der Absätze in den Blöcken bei der festen Breite ``breite`` (ohne Absatzabstände)."""
        fluss = _Fluss(self.engine, dok, listenmarken(dok), None)
        fluss.teilfluss(bloecke, breite)
        return sum(fluss.erg.absaetze[a.id].satz.hoehe for a in absaetze_in(bloecke) if a.id in fluss.erg.absaetze)
