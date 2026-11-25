"""Die Layout-Engine: berechnet aus dem Dokumentmodell Seiten, Zeilen, Tabellen, Rahmen, Objekte und Noten. Ohne Qt.

Das Layout liest das Modell und verändert es nie. Abschnitte (neue Seite, fortlaufend mit neuer Spalteneinteilung, gerade/ungerade Seite), Spalten,
Absätze (Läufe in verschiedenen Schriften, Objekte in der Zeile, Ausrichtung, Einzüge, Listenmarken, Abstände mit Zusammenfall, Zeilenabstand,
Umbruch davor/danach, Witwen- und Waisenregeln), Tabellen (Spaltenbreiten, verbundene Zellen, wiederholte Kopfzeilen, Teilung zu hoher Zeilen),
Rahmen (im Fluss und schwebend), frei positionierte Objekte mit Textumfluss, Fußnoten am Seitenende und Endnoten am Dokumentende.

Die Seiteneinrichtung eines Abschnitts (``PageSettings``) wird nur gelesen.
"""
from __future__ import annotations

import re

from lunivo_writer.core.document.dokument import Absatz, Dokument, Rahmen, Tabelle
from lunivo_writer.core.geometry import Rect, mm_to_px
from lunivo_writer.core.textlayout.engine import TextLayoutEngine
from .ergebnis import Ergebnis, Platz, Seite
from .absatzlayout import AbsatzLayout
from .fussnotenlayout import FussnotenLayout
from .tabellenlayout import TabellenLayout
from .textumfluss import TextUmfluss
from .geometrie import BLATT_ABSTAND_PX, FORTLAUFEND, GERADE, UNGERADE, WEB_RAND  # noqa: F401  (BLATT_ABSTAND_PX u. a. waren hier zu Hause)



class _Fluss(AbsatzLayout, TabellenLayout, FussnotenLayout, TextUmfluss):
    def __init__(self, engine: TextLayoutEngine, dok: Dokument, marken: dict, frei_an: dict | None, optionen: dict | None = None):
        self.engine, self.dok, self.marken = engine, dok, marken
        self.opt = optionen or {}
        self.frei_an = frei_an                      # Absatz-Id → freie Objekte (nur im Hauptfluss)
        self.erg = Ergebnis()
        self.abschnitt = -1
        self.einr = None
        self.spalten: list = []
        self.rand_links = self.rand_oben = 0.0
        self.hoehe = 0.0
        self.spalte = 0
        self.y = 0.0
        self.seite: Seite | None = None
        self.unten = 0.0                    # Abstand unter dem letzten Absatz (fällt mit dem oberen des nächsten zusammen)
        self.leer = True
        self.y0 = 0.0
        self.noten_text = {n.id: n.text for n in dok.noten.get("f", {}).values()}
        self.noten: dict = {}               # Seitenindex → [(laufende Nummer, Id)]
        self.noten_zaehler = 0
        self.ausschluesse: list = []        # (Seitenindex, Spalte, Rect, "links" | "rechts" | "voll"): Flächen, um die der Text läuft
        self.endnoten: list = []
        self.seitennummer = 0
        self.start_nummer = 0

    # ---- Seiten und Spalten ----
    def neue_seite(self) -> None:
        oben = 0.0
        if self.erg.seiten:
            letzte = self.erg.seiten[-1]
            oben = letzte.oben + (mm_to_px(letzte.einrichtung.height_mm) if letzte.einrichtung is not None else 0.0) + BLATT_ABSTAND_PX
        if self.start_nummer:
            self.seitennummer, self.start_nummer = self.start_nummer, 0
        else:
            self.seitennummer += 1
        self.seite = Seite(len(self.erg.seiten), self.abschnitt, self.einr, oben=oben, nummer=self.seitennummer)
        self.erg.seiten.append(self.seite)
        self.spalte, self.y, self.y0, self.leer, self.unten = 0, 0.0, 0.0, True, 0.0

    def weiter(self) -> None:
        if self.spalte + 1 < len(self.spalten):
            self.spalte += 1
            self.y, self.leer, self.unten = self.y0, True, 0.0
        else:
            self.neue_seite()

    def breite(self) -> float:
        return self.spalten[self.spalte][1]

    def links(self) -> float:
        return self.rand_links + self.spalten[self.spalte][0]

    def frei(self) -> float:
        """Höhe der Spalte auf dieser Seite abzüglich des Platzes, den die Fußnoten unten brauchen."""
        return self.hoehe - self.noten_hoehe(self.noten.get(self.seite.index, []))

    def platz_fuer(self, h: float, extra: float = 0.0) -> None:
        if self.y + h > self.frei() - extra + 0.01 and not self.leer:
            self.weiter()

    def abstand_vor(self, a: float) -> None:
        """Abstand vor einem Block: fällt mit dem Abstand unter dem vorigen zusammen und entfällt am Anfang der Spalte."""
        a, self.unten = max(0.0, a - self.unten), 0.0
        if not self.leer or (self.seite.index == 0 and self.spalte == 0):      # am Anfang der ersten Seite bleibt der Abstand vor dem ersten Block (wie in Word)
            self.y += a

    def abschnitt_beginnt(self, nr: int, abschnitt) -> None:
        p = abschnitt.seite
        self.abschnitt, self.einr = nr, p
        web = self.opt.get("web")
        fortlaufend = self.seite is not None and (web or abschnitt.beginn == FORTLAUFEND) and nr > 0
        oben_vorher, hoehe_vorher, einr_vorher = self.rand_oben, self.hoehe, self.einr
        if web:                                                     # Weblayout: eine endlose Seite in der Breite des Fensters
            self.rand_links = self.rand_oben = WEB_RAND
            self.hoehe = 1e9
            self.spalten = [(0.0, max(200.0, float(web) - 2 * WEB_RAND))]
        else:
            self.rand_links = mm_to_px(p.margin_left_mm)
            self.rand_oben = mm_to_px(p.margin_top_mm)
            self.hoehe = p.content_height_px
            self.spalten = list(p.spaltenraster_px())
        if fortlaufend:
            if not web:                                             # Ober- und Unterrand sowie Seitengröße bestimmt der Abschnitt, der die Seite begonnen hat; ``y`` zählt ab dessen Oberrand
                self.rand_oben, self.hoehe, self.einr = oben_vorher, hoehe_vorher, einr_vorher
            self.spalte, self.y0, self.leer = 0, self.y, True       # neue Spalteneinteilung ab hier, auf derselben Seite
            return
        if p.seiten_start:
            self.start_nummer = int(p.seiten_start)
        self.neue_seite()
        if nr == 0:
            self.y = self.y0 = float(p.erste_seite_versatz_px())    # lange Kopfzeile: der Text der ersten Seite beginnt darunter
        if abschnitt.beginn in (GERADE, UNGERADE):
            if (self.seitennummer % 2 == 0) != (abschnitt.beginn == GERADE):
                self.neue_seite()                                   # Leerseite

    # ---- Noten ----




    # ---- Blöcke ----

    def blocks(self, bloecke: list) -> None:
        for i, b in enumerate(bloecke):
            if isinstance(b, Absatz):
                self.absatz(b, bloecke[i + 1:i + 5])
            elif isinstance(b, Tabelle):
                self.tabelle(b)
            elif isinstance(b, Rahmen):
                self.rahmen(b)



    _WORT = re.compile(r"[^\W\d_]{2,}", re.UNICODE)






    # ---- Teilflüsse (Zelle, Rahmen) ----
    def teilfluss(self, bloecke: list, breite: float):
        """Blöcke in einer festen Breite setzen (Zelle, Rahmen): → (Höhe, Plätze relativ zur oberen linken Ecke). Die Zeilenrechtecke der Absätze
        setzt der Aufrufer an ihrem Ort auf der Seite."""
        fl = _Fluss(self.engine, self.dok, self.marken, self.frei_an, self.opt)
        fl.spalten, fl.hoehe, fl.rand_links, fl.rand_oben = [(0.0, breite)], 1e12, 0.0, 0.0
        fl.seite = Seite(-1, self.abschnitt, self.einr)
        fl.abschnitt, fl.einr = self.abschnitt, self.einr
        fl.noten_text = {}
        fl.blocks(bloecke)
        for k, v in fl.erg.absaetze.items():
            v.zeilen = []
            self.erg.absaetze[k] = v
        self.endnoten.extend(fl.endnoten)
        return fl.y, fl.seite.plaetze

    def auf_seite_setzen(self, plaetze: list, dx: float, dy: float, seite: Seite | None = None, kopie: bool = False) -> None:
        """Plätze aus einem Teilfluss (Zeilen, Zellen und Rahmen darin) an ihren Ort auf der Seite verschieben und eintragen."""
        seite = seite or self.seite
        for p in plaetze:
            r = Rect(dx + p.rect.x, dy + p.rect.y, p.rect.width, p.rect.height)
            ist_kopie = kopie or p.kopie
            seite.plaetze.append(Platz(p.art, r, p.block_id, p.zeile, p.spalte, p.daten, ist_kopie))
            if p.art == "objekt" and not ist_kopie and seite.index >= 0:
                self.erg.objekte[p.block_id] = (seite.index, r)
            ort =self.erg.absaetze.get(p.block_id) if p.art == "zeile" and not ist_kopie else None
            if ort is not None:
                ort.zeilen.append((seite.index, p.zeile, r))

    # ---- Rahmen ----


    # ---- Tabellen ----



    # ---- Endnoten und Fußnoten ----




