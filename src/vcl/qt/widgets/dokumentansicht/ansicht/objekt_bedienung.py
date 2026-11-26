"""Objekte auf dem Blatt bedienen: auswählen, verschieben, in der Größe ändern, drehen und die Schaltflächen neben dem Objekt.

Die Mischklasse ``ObjektBedienung`` gehört zur Zeichenfläche (``dokument_ansicht.py``). Sie verändert das Dokument nie selbst: Nach dem Ziehen ruft sie
die Rückrufe der Ansicht auf (``objekt_geaendert``, ``objekt_gedreht``, ``inline_groesse``), die der Editor mit Operationen der Bearbeitungssitzung belegt.

Zwei Arten von Objekten: **frei** (``FreiesObjekt``, Rechteck aus dem Layout) und **im Text** (``InlineObjekt``, Rechteck der Zeichenstelle).
Der Auswahlrahmen hat acht Griffe; frei positionierte Objekte haben dazu den Drehgriff über der Oberkante. An den Ecken bleibt das Seitenverhältnis,
mit Umschalt ändert sich die Form frei.
"""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen

from writer.werte import Rechteck

GRIFF_TREFFER = 7.0                    # Trefferfläche eines Griffs (Bildpunkte der Ansicht)
GRIFF_GROESSE = 7.0
ROT_ABSTAND = 24.0                     # Drehgriff: so weit über der Oberkante (Bildpunkte der Ansicht)
MIN_OBJEKT = 8.0
KNOPF = 24.0                           # Seitenlänge einer Schaltfläche
OBJEKT_RAHMEN = ((47, 111, 181, 255), 1.5)      # Farbe und Strichstärke des Auswahlrahmens und der Griffe
WEISS = (255, 255, 255, 255)                    # Fläche der Griffe
CURSOR = {"nw": Qt.SizeFDiagCursor, "se": Qt.SizeFDiagCursor, "ne": Qt.SizeBDiagCursor, "sw": Qt.SizeBDiagCursor,
          "n": Qt.SizeVerCursor, "s": Qt.SizeVerCursor, "w": Qt.SizeHorCursor, "e": Qt.SizeHorCursor, "rot": Qt.PointingHandCursor}
ECKEN = ("nw", "ne", "se", "sw")
# Schaltflächen je Objektart (Name, Lucide-Symbol, Hinweis); die Namen verarbeitet ``freie_bilder_knoepfe.py``
_LAYOUT = ("layout", "text-wrap", "Layoutoptionen")
_FORM = (_LAYOUT, ("formstile", "palette", "Formenformatvorlagen"), ("fuell", "paint-bucket", "Fülleffekt"), ("kontur", "pen-line", "Kontur"))
KNOEPFE = {
    "bild": (_LAYOUT, ("lupe", "zoom-in", "Vergrößern"), ("zuschnitt", "crop", "Zuschneiden")),
    "piktogramm": (_LAYOUT, ("lupe", "zoom-in", "Vergrößern"), ("zuschnitt", "crop", "Zuschneiden")),
    "form": _FORM,
    "textfeld": _FORM,
    "wordart": _FORM,
    "diagramm": (_LAYOUT, ("dg_element", "plus", "Diagrammelemente"), ("dg_stile", "paintbrush", "Diagrammformatvorlagen"),
                 ("dg_filter", "funnel", "Diagrammfilter"), ("zahnrad", "settings", "Formatieren")),
    "smartart": (("sa_form", "shapes", "Form"), ("sa_layout", "layout-template", "Layout"), ("sa_level", "list-indent-increase", "Ebene"),
                 ("sa_stil", "paintbrush", "Stile"), ("sa_bullet", "list", "Aufzählung"), ("zahnrad", "settings", "Formatieren")),
}
STANDARD_KNOEPFE = (_LAYOUT,)
from vcl.qt.widgets.bausteine.farben.farben import KNOPF_SYMBOLFARBE, OBJEKT_KNOPF_FLAECHE, OBJEKT_KNOPF_RAND
from vcl.qt.widgets.bausteine.abstaende.mass import RADIUS_ZEICHNUNG_GROSS # Symbole auf dem hellen Knopfgrund (in jedem Thema gleich)


class ObjektBedienung:
    def _objekt_init(self) -> None:
        self.gewaehltes_objekt: int | None = None  # frei positioniertes Objekt (Id)
        self._objekt_zug = None                    # laufendes Ziehen (Verschieben, Größe, Drehen)
        self.objekt_geaendert = None               # Rückruf(Id, Seitenindex, Rechteck) nach Verschieben oder Größe ändern
        self.objekt_gedreht = None                 # Rückruf(Id, Winkel) nach dem Drehen
        self.inline_gewaehlt_id = lambda: None     # Id des gewählten Objekts im Text
        self.inline_rechteck = lambda i: None      # (Seite, Rechteck) eines Objekts im Text
        self.inline_bei = lambda ziel, punkt: None
        self.inline_waehlen = lambda i: None
        self.inline_groesse = None                 # Rückruf(Id, Breite, Höhe)
        self.objekt_art_von = lambda art, i: None  # Objektart („bild“ …) für die Schaltflächen
        self.objekt_doppelklick = None             # Rückruf(Id) bei Doppelklick auf ein freies Objekt
        self.freiform_hook = None                  # Rückruf(Art, Ereignis) → True: die Freiform-Punktebearbeitung hat das Ereignis genommen
        self.freiform_taste = None
        self.nach_zeichnen = None                  # Rückruf(Maler): zusätzliche Zeichnung über dem Blatt (Punkte der Freiform)
        self.objekt_teil_klick = None              # Rückruf(Punkt): Klick in das gewählte Diagramm oder SmartArt
        self.objekt_teil_rahmen = None             # Rückruf(Rechteck des Objekts in der Ansicht) → (Drehwinkel, Mitte, [(Rechteck, Griffpunkte)]) des gewählten Diagrammteils bzw. SmartArt-Knotens
        self.objekt_teil_tipp = None               # Rückruf(Ereignis): Maus über dem gewählten Objekt (Tooltip des Diagrammteils)
        self.objekt_teil_taste = None              # Rückruf(Ereignis) → True: die Taste schreibt im gewählten SmartArt-Knoten
        self.objekt_wahl_endet = None              # Rückruf(): das gewählte Objekt wird gleich abgewählt (Teil bzw. Knoten abwählen)
        self.zuschnitt_aktiv = lambda: False       # Zuschneiden-Modus an?
        self.zuschnitt_geaendert = None            # Rückruf(Id, Seite, Rechteck, Anteile) nach dem Ziehen eines Zuschneidegriffs
        self.zuschnitt_lesen = lambda i: (0.0, 0.0, 0.0, 0.0)
        self.setMouseTracking(True)

    # ---- Auswahl und Geometrie -----------------------------------------------------------------------------------------------------
    def sitzung_objekt_rechteck(self, objekt_id: int):
        """(Seitenindex, Rechteck in Seitenkoordinaten) eines frei positionierten Objekts."""
        return self.ergebnis().objekte[objekt_id]

    def _auswahl_objekt(self):
        """(Art, Id, Seite, Rechteck) des gewählten Objekts; Art ``frei`` oder ``inline``; ``None``, wenn keines gewählt ist."""
        erg = self.ergebnis()
        if self.gewaehltes_objekt is not None and self.gewaehltes_objekt in erg.objekte:
            seite, r = erg.objekte[self.gewaehltes_objekt]
            return "frei", self.gewaehltes_objekt, seite, r
        i = self.inline_gewaehlt_id()
        if i is not None:
            res = self.inline_rechteck(i)
            if res is not None:
                return "inline", i, res[0], res[1]
        return None

    def _rahmen(self, sel) -> Rechteck:
        zug = self._objekt_zug
        return zug["rect"] if zug is not None and zug.get("id") == sel[1] else sel[3]

    def _ansicht_punkt(self, seite: int, x: float, y: float) -> tuple:
        blatt = self.blatt(seite)
        return blatt.left() + x * self.zoom, blatt.top() + y * self.zoom

    def _seiten_punkt(self, pos) -> tuple:
        """Ein Punkt der Ansicht in den Koordinaten des nächsten Blattes."""
        i = self._naechstes_blatt(pos)
        blatt = self.blatt(i)
        return (pos.x() - blatt.left()) / self.zoom, (pos.y() - blatt.top()) / self.zoom

    @staticmethod
    def _griffe(r) -> dict:
        mx, my = r.x + r.width / 2, r.y + r.height / 2
        return {"nw": (r.x, r.y), "n": (mx, r.y), "ne": (r.right, r.y), "e": (r.right, my), "se": (r.right, r.bottom), "s": (mx, r.bottom),
                "sw": (r.x, r.bottom), "w": (r.x, my)}

    def _griffe_ansicht(self, sel) -> dict:
        r = self._rahmen(sel)
        aus = {n: self._ansicht_punkt(sel[2], gx, gy) for n, (gx, gy) in self._griffe(r).items()}
        if sel[0] == "frei":
            x, y = aus["n"]
            aus["rot"] = (x, y - ROT_ABSTAND)
        elif sel[0] == "inline":
            aus = {n: p for n, p in aus.items() if n in ECKEN}
        return aus

    def griff_bei(self, pos, sel=None) -> str | None:
        """Der Griff („nw“ … „se“ oder „rot“) des gewählten Objekts unter dem Punkt der Ansicht, sonst ``None``."""
        sel = sel or self._auswahl_objekt()
        if sel is None:
            return None
        for name, (vx, vy) in self._griffe_ansicht(sel).items():
            if abs(pos.x() - vx) <= GRIFF_TREFFER and abs(pos.y() - vy) <= GRIFF_TREFFER:
                return name
        return None

    # ---- Schaltflächen ---------------------------------------------------------------------------------------------------------------
    def knopf_liste(self, sel) -> list:
        """[(Name, Symbol, Hinweis, Rechteck in der Ansicht)] der Schaltflächen neben dem gewählten Objekt."""
        art = self.objekt_art_von(sel[0], sel[1]) or "bild"
        liste = KNOEPFE.get(art, STANDARD_KNOEPFE)
        r = self._rahmen(sel)
        rechts, oben = self._ansicht_punkt(sel[2], r.right, r.y)
        links = self._ansicht_punkt(sel[2], r.x, r.y)[0]
        x = rechts + 10.0
        if x + KNOPF > self.width():
            x = max(2.0, links - 10.0 - KNOPF)
        return [(n, z, h, QRectF(x, oben + i * (KNOPF + 3.0), KNOPF, KNOPF)) for i, (n, z, h) in enumerate(liste)]

    def knopf_bei(self, pos, sel=None):
        sel = sel or self._auswahl_objekt()
        if sel is None or self._objekt_zug is not None:
            return None
        for n, _z, h, rc in self.knopf_liste(sel):
            if rc.contains(pos):
                return n, h
        return None

    # ---- Zeichnen --------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _rahmen_malen(p: QPainter, r) -> None:
        """Ein Rechteck als Linie in der Farbe des Auswahlrahmens."""
        p.save()
        p.setPen(QPen(QColor(*OBJEKT_RAHMEN[0]), OBJEKT_RAHMEN[1]))
        p.setBrush(Qt.NoBrush)
        p.drawRect(QRectF(r.x, r.y, r.width, r.height))
        p.restore()

    @staticmethod
    def _flaeche_malen(p: QPainter, r) -> None:
        """Ein Rechteck als weiße Fläche ohne Linie."""
        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(*WEISS)))
        p.fillRect(QRectF(r.x, r.y, r.width, r.height), QBrush(QColor(*WEISS)))
        p.restore()

    def objekt_zeichnen(self, p: QPainter, seite: int) -> None:
        """Auswahlrahmen, Griffe und Drehgriff auf der Seite ``seite`` (Seitenkoordinaten, ``p`` ist auf das Blatt skaliert)."""
        sel = self._auswahl_objekt()
        if sel is None or sel[2] != seite:
            return
        r = self._rahmen(sel)
        self._rahmen_malen(p, r)
        g = GRIFF_GROESSE / self.zoom
        punkte = self._griffe(r)
        if sel[0] == "inline":
            punkte = {n: pt for n, pt in punkte.items() if n in ECKEN}
        if sel[0] == "frei":
            mx = r.x + r.width / 2
            p.save()
            p.setPen(QPen(QColor(*OBJEKT_RAHMEN[0]), OBJEKT_RAHMEN[1]))
            p.drawLine(QPointF(mx, r.y), QPointF(mx, r.y - ROT_ABSTAND / self.zoom))
            p.restore()
            kreis = Rechteck(mx - g / 2 - 1 / self.zoom, r.y - ROT_ABSTAND / self.zoom - g / 2, g + 2 / self.zoom, g + 2 / self.zoom)
            self._flaeche_malen(p, kreis)
            self._rahmen_malen(p, kreis)
        for gx, gy in punkte.values():
            quadrat = Rechteck(gx - g / 2, gy - g / 2, g, g)
            self._flaeche_malen(p, quadrat)
            self._rahmen_malen(p, quadrat)

    def teil_rahmen_zeichnen(self, p: QPainter) -> None:
        """Rahmen und Griffe um den gewählten Diagrammteil bzw. SmartArt-Knoten (in den Koordinaten der Ansicht, mit der Drehung des Objekts)."""
        sel = self._auswahl_objekt()
        if sel is None or sel[0] != "frei" or self.objekt_teil_rahmen is None or self._objekt_zug is not None:
            return
        r = sel[3]
        links, oben = self._ansicht_punkt(sel[2], r.x, r.y)
        winkel, mitte, teile = self.objekt_teil_rahmen(QRectF(links, oben, r.width * self.zoom, r.height * self.zoom))
        if not teile:
            return
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        if winkel:
            p.translate(mitte)
            p.rotate(winkel)
            p.translate(-mitte)
        g = GRIFF_GROESSE / 2                                               # kleiner als die Griffe des Objekts: kleine Teile (Titel) bleiben lesbar
        for r, punkte in teile:
            self._rahmen_malen(p, Rechteck(r.x(), r.y(), r.width(), r.height()))
            for c in punkte:
                quadrat = Rechteck(c.x() - g / 2, c.y() - g / 2, g, g)
                self._flaeche_malen(p, quadrat)
                self._rahmen_malen(p, quadrat)
        p.restore()

    def objekt_abwahl_melden(self) -> None:
        """Vor dem Abwählen des gewählten freien Objekts: der Editor wählt dessen Diagrammteil bzw. SmartArt-Knoten ab."""
        if self.gewaehltes_objekt is not None and self.objekt_wahl_endet is not None and not self.nur_lesen:
            self.objekt_wahl_endet()

    def knoepfe_zeichnen(self, p: QPainter) -> None:
        """Die Schaltflächen neben dem gewählten Objekt (in den Koordinaten der Ansicht)."""
        sel = self._auswahl_objekt()
        if sel is None or self.nur_lesen or self._objekt_zug is not None:
            return
        from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        for _n, symbol, _h, rc in self.knopf_liste(sel):
            p.setPen(QPen(QColor(*OBJEKT_KNOPF_RAND), 1))
            p.setBrush(QColor(*OBJEKT_KNOPF_FLAECHE))
            p.drawRoundedRect(rc, RADIUS_ZEICHNUNG_GROSS, RADIUS_ZEICHNUNG_GROSS)
            symbole.in_rechteck(p, symbol, rc, KNOPF_SYMBOLFARBE)
        p.restore()

    # ---- Maus ------------------------------------------------------------------------------------------------------------------------
    def objekt_maus_druecken(self, ev) -> bool:
        """``True``, wenn der Mausdruck ein Objekt, einen Griff oder eine Schaltfläche betraf."""
        pos = ev.position()
        sel = self._auswahl_objekt()
        if sel is not None and not self.nur_lesen:
            k = self.knopf_bei(pos, sel)
            if k is not None:
                self.objektKnopf.emit(k[0], ev.globalPosition().toPoint())
                return True
            g = self.griff_bei(pos, sel)
            if g is not None:
                r = self._rahmen(sel)
                if sel[0] == "frei" and g != "rot" and self.zuschnitt_aktiv():          # Zuschneiden: die Griffe schneiden ab statt die Größe zu ändern
                    g = "z:" + g
                self._objekt_zug = {"modus": g, "start": pos, "seite": sel[2], "rect0": r, "rect": r, "art": sel[0], "id": sel[1], "winkel": 0.0}
                return True
        objekt = self.objekt_bei(pos)
        if objekt is not None:
            if objekt == self.gewaehltes_objekt and self.objekt_teil_klick is not None:
                self.objekt_teil_klick(pos)
            if objekt != self.gewaehltes_objekt:
                self.objekt_abwahl_melden()
                self.gewaehltes_objekt = objekt
                self.freiAuswahlGeaendert.emit()
            seite, r = self.sitzung_objekt_rechteck(objekt)
            if not self.nur_lesen:
                self._objekt_zug = {"modus": "verschieben", "start": pos, "seite": seite, "rect0": r, "rect": r, "art": "frei", "id": objekt, "winkel": 0.0}
            self.update()
            return True
        ziel = self.stelle(pos)
        if ziel is not None:
            i = self.inline_bei(ziel, self._seiten_punkt(pos))
            if i is not None:
                if self.gewaehltes_objekt is not None:
                    self.objekt_abwahl_melden()
                    self.gewaehltes_objekt = None
                    self.freiAuswahlGeaendert.emit()
                self.inline_waehlen(i)
                sel = self._auswahl_objekt()
                if sel is not None and not self.nur_lesen:
                    r = sel[3]
                    self._objekt_zug = {"modus": "gewaehlt", "start": pos, "seite": sel[2], "rect0": r, "rect": r, "art": "inline", "id": i, "winkel": 0.0}
                self.update()
                return True
        return False

    def objekt_maus_bewegen(self, ev) -> bool:
        zug = self._objekt_zug
        pos = ev.position()
        if zug is None:
            sel = self._auswahl_objekt()
            if sel is not None:
                g = self.griff_bei(pos, sel)
                if g is not None:
                    self.setCursor(CURSOR.get(g, Qt.ArrowCursor))
                    return True
                if self.knopf_bei(pos, sel) is not None:
                    self.setCursor(Qt.PointingHandCursor)
                    return True
                if sel[0] == "frei" and self.objekt_bei(pos) == sel[1]:
                    if self.objekt_teil_tipp is not None:
                        self.objekt_teil_tipp(ev)
                    self.setCursor(Qt.SizeAllCursor)
                    return True
            self.setCursor(Qt.IBeamCursor)
            return False
        if self.nur_lesen or zug["modus"] == "gewaehlt":
            return True
        m = zug["modus"]
        zuschnitt = m.startswith("z:")
        m = m[2:] if zuschnitt else m
        r = zug["rect0"]
        if m == "rot":
            vx, vy = self._ansicht_punkt(zug["seite"], r.x + r.width / 2, r.y + r.height / 2)
            winkel = math.degrees(math.atan2(pos.x() - vx, vy - pos.y())) % 360.0
            if ev.modifiers() & Qt.ShiftModifier:
                winkel = round(winkel / 15.0) * 15.0 % 360.0
            zug["winkel"] = winkel
            self.setToolTip(f"{winkel:.0f}°")
            self.update()
            return True
        dx = (pos.x() - zug["start"].x()) / self.zoom
        dy = (pos.y() - zug["start"].y()) / self.zoom
        x1, y1, x2, y2 = r.x, r.y, r.right, r.bottom
        if m == "verschieben":
            x1, x2, y1, y2 = x1 + dx, x2 + dx, y1 + dy, y2 + dy
        else:
            if "w" in m:
                x1 = min(x1 + dx, x2 - MIN_OBJEKT)
            if "e" in m:
                x2 = max(x2 + dx, x1 + MIN_OBJEKT)
            if "n" in m:
                y1 = min(y1 + dy, y2 - MIN_OBJEKT)
            if "s" in m:
                y2 = max(y2 + dy, y1 + MIN_OBJEKT)
            if m in ECKEN and not zuschnitt and not ev.modifiers() & Qt.ShiftModifier and r.height > 0:      # an den Ecken bleibt das Seitenverhältnis
                verh = r.width / r.height
                breite, hoehe = x2 - x1, y2 - y1
                if breite / max(hoehe, 1e-6) > verh:
                    breite = hoehe * verh
                else:
                    hoehe = breite / verh
                if "w" in m:
                    x1 = x2 - breite
                else:
                    x2 = x1 + breite
                if "n" in m:
                    y1 = y2 - hoehe
                else:
                    y2 = y1 + hoehe
        zug["rect"] = Rechteck(x1, y1, x2 - x1, y2 - y1)
        self.update()
        return True

    def objekt_maus_loslassen(self, ev) -> bool:
        zug, self._objekt_zug = self._objekt_zug, None
        if zug is None:
            return False
        self.setToolTip("")
        if zug["modus"] == "gewaehlt":
            return True
        if zug["modus"] == "rot":
            if self.objekt_gedreht is not None:
                self.objekt_gedreht(zug["id"], zug["winkel"])
        elif zug["rect"] != zug["rect0"] and zug["modus"].startswith("z:"):
            if self.zuschnitt_geaendert is not None:
                r0, r1 = zug["rect0"], zug["rect"]
                l, o, ru, u = self.zuschnitt_lesen(zug["id"])
                sx, sy = r0.width / max(0.05, 1 - l - ru), r0.height / max(0.05, 1 - o - u)
                neu = (max(0.0, l + (r1.x - r0.x) / sx), max(0.0, o + (r1.y - r0.y) / sy), max(0.0, ru + (r0.right - r1.right) / sx), max(0.0, u + (r0.bottom - r1.bottom) / sy))
                self.zuschnitt_geaendert(zug["id"], zug["seite"], r1, neu)
        elif zug["rect"] != zug["rect0"]:
            if zug["art"] == "frei" and self.objekt_geaendert is not None:
                self.objekt_geaendert(zug["id"], zug["seite"], zug["rect"])
            elif zug["art"] == "inline" and self.inline_groesse is not None:
                self.inline_groesse(zug["id"], zug["rect"].width, zug["rect"].height)
        self.nach_aenderung()
        self.update()
        return True
