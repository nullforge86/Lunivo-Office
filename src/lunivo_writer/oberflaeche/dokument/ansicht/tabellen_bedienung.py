"""Tabellen auf dem Blatt bedienen: Griffe an der Tabelle, Spalten- und Zeilenränder ziehen, Tabelle zeichnen (Stift) und Linien löschen (Radiergummi).

Die Mischklasse ``TabellenBedienung`` gehört zur Zeichenfläche (``dokument_ansicht.py``). Lage und Maße der Zellen kommen aus dem Layoutergebnis (Plätze der Art
``zelle``). Die Zeichenfläche ändert das Dokument nie selbst: Sie ruft die Rückrufe auf, die der Editor mit Operationen der Bearbeitungssitzung belegt.

* Verschiebegriff oben links: Klick wählt die ganze Tabelle (Minileiste), „+“ rechts und unten hängt eine Spalte bzw. Zeile an, der Aufziehgriff unten rechts
  ändert die Größe der ganzen Tabelle.
* Ränder zwischen Spalten und Zeilen lassen sich mit der Maus ziehen.
* Stift: ein Rechteck aufziehen, dort entsteht eine Tabelle; Radiergummi: ein Klick auf eine Zellenlinie verbindet die beiden Zellen daneben.
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, QPointF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen

GRIFF = 14.0                    # Seitenlänge der Griffe (Bildpunkte der Ansicht)
RAND_TREFFER = 4.0              # Abstand zu einem Zellenrand, bis zu dem er getroffen wird
ZELLE_B, ZELLE_H = 56.0, 20.0   # Zellengröße beim Zeichnen mit dem Stift (Bildpunkte bei 100 %)
BLAU = QColor(47, 111, 181)


class TabellenBedienung:
    def _tabelle_init(self) -> None:
        self.tabelle_aktiv = lambda: None            # Rückruf: Id der Tabelle an der Schreibmarke (sonst ``None``)
        self.tabelle_aendern = None                  # Rückruf(Art, Tabellen-Id, Wert) nach dem Ziehen oder Klicken
        self.tabelle_waehlen = None                  # Rückruf(Tabellen-Id) beim Klick auf den Verschiebegriff
        self.tabelle_zeichnen = None                 # Rückruf(Stelle, Zeilen, Spalten) beim Loslassen des Stifts
        self.tabelle_linie_loeschen = None           # Rückruf(Tabellen-Id, (Zeile, Spalte), (Zeile, Spalte)) beim Klick des Radiergummis
        self.tabellen_modus = None                   # None | "stift" | "radierer"
        self._tab_zug = None

    # ---- Geometrie -------------------------------------------------------------------------------------------------------------------
    def _zellplaetze(self, tid: int) -> list:
        """[(Seite, Platz)] der Zellen der Tabelle (ohne wiederholte Kopfzeilen)."""
        return [(s.index, p) for s in self.ergebnis().seiten for p in s.plaetze if p.art == "zelle" and p.block_id == tid and not p.kopie]

    def _tabellen_rahmen(self, tid: int):
        """(Seite, Rechteck der Tabelle in Seitenkoordinaten) auf der ersten Seite, auf der sie steht; sonst ``None``."""
        zellen = self._zellplaetze(tid)
        if not zellen:
            return None
        seite = zellen[0][0]
        r = [p.rect for s, p in zellen if s == seite]
        x1, y1 = min(c.x for c in r), min(c.y for c in r)
        x2, y2 = max(c.right for c in r), max(c.bottom for c in r)
        return seite, QRectF(x1, y1, x2 - x1, y2 - y1)

    def _v(self, seite: int, x: float, y: float) -> QPointF:
        b = self.blatt(seite)
        return QPointF(b.left() + x * self.zoom, b.top() + y * self.zoom)

    def _ansicht_rect(self, seite: int, r: QRectF) -> QRectF:
        return QRectF(self._v(seite, r.x(), r.y()), self._v(seite, r.x() + r.width(), r.y() + r.height()))

    def tabellen_griffe(self) -> dict:
        """{Name: QRectF} der Griffe der Tabelle an der Schreibmarke in Koordinaten der Ansicht; leer ohne Tabelle."""
        tid = None if self.nur_lesen or self.tabellen_modus else self.tabelle_aktiv()
        rahmen = self._tabellen_rahmen(tid) if tid is not None else None
        if rahmen is None:
            return {}
        seite, r = rahmen
        a = self._ansicht_rect(seite, r)
        g = GRIFF
        return {"move": QRectF(a.left() - g - 4, a.top() - g - 4, g, g),
                "spalte_plus": QRectF(a.right() + 4, a.center().y() - g / 2, g, g),
                "zeile_plus": QRectF(a.center().x() - g / 2, a.bottom() + 4, g, g),
                "aufziehen": QRectF(a.right() + 2, a.bottom() + 2, g * 0.7, g * 0.7)}

    @staticmethod
    def _spanne(zelle, breit: bool) -> int:
        return zelle.spaltenspanne if breit else zelle.zeilenspanne

    def _rand_bei(self, pos):
        """(Art, Tabelle, Index) des Zellenrands unter dem Punkt der Ansicht; Art ``spalte`` oder ``zeile``; ``Index``: letzte Spalte links bzw. letzte Zeile
        oberhalb des Rands. Sonst ``None``."""
        tid = None if self.nur_lesen else self.tabelle_aktiv()
        if tid is None:
            return None
        t = self.sitzung._tabelle(tid)
        for seite, p in self._zellplaetze(tid):
            if p.zeile < 0 or p.spalte < 0:
                continue
            z = t.zellen[p.zeile][p.spalte]
            a, b = self._v(seite, p.rect.right, p.rect.y), self._v(seite, p.rect.right, p.rect.bottom)
            if abs(pos.x() - a.x()) <= RAND_TREFFER and a.y() <= pos.y() <= b.y() and p.spalte + z.spaltenspanne < t.spalten:
                return "spalte", tid, p.spalte + z.spaltenspanne - 1
            a, b = self._v(seite, p.rect.x, p.rect.bottom), self._v(seite, p.rect.right, p.rect.bottom)
            if abs(pos.y() - a.y()) <= RAND_TREFFER and a.x() <= pos.x() <= b.x() and p.zeile + z.zeilenspanne < t.zeilen:
                return "zeile", tid, p.zeile + z.zeilenspanne - 1
        return None

    # ---- Zeichnen --------------------------------------------------------------------------------------------------------------------
    def tabellen_zeichnen(self, p: QPainter) -> None:
        """Griffe der Tabelle, die Vorschau beim Ziehen und die Stift-Vorschau (in Koordinaten der Ansicht)."""
        from lunivo_writer.oberflaeche.bauteile import symbole
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        for name, rc in self.tabellen_griffe().items():
            p.setPen(QPen(QColor(120, 130, 150), 1))
            p.setBrush(QColor(255, 255, 255, 235))
            if name == "aufziehen":
                p.drawRect(rc)
                continue
            p.drawRoundedRect(rc, 3, 3)
            symbole.in_rechteck(p, "move" if name == "move" else "plus", rc, "#283c5a", rand=2)      # Lucide statt Schriftzeichen ✥/+
        z = self._tab_zug
        if z is not None and z.get("vorschau") is not None:
            p.setPen(QPen(BLAU, 1.2, Qt.DashLine))
            p.setBrush(QColor(47, 111, 181, 30))
            p.drawRect(z["vorschau"])
            if z["art"] == "stift":
                p.setPen(BLAU)
                p.drawText(z["vorschau"].adjusted(4, 2, 0, 0), Qt.AlignTop | Qt.AlignLeft, f"{z['zeilen']} × {z['spalten']}")
        elif z is not None and z["art"] in ("spalte", "zeile"):
            p.setPen(QPen(BLAU, 1.5, Qt.DashLine))
            if z["art"] == "spalte":
                p.drawLine(QPointF(z["start"].x() + z["delta"] * self.zoom, 0), QPointF(z["start"].x() + z["delta"] * self.zoom, self.height()))
            else:
                p.drawLine(QPointF(0, z["start"].y() + z["delta"] * self.zoom), QPointF(self.width(), z["start"].y() + z["delta"] * self.zoom))
        p.restore()

    # ---- Maus ------------------------------------------------------------------------------------------------------------------------
    def tabellen_maus_druecken(self, ev) -> bool:
        pos = ev.position()
        if self.tabellen_modus == "stift":
            stelle = self.stelle(pos)
            if stelle is not None:
                self._tab_zug = {"art": "stift", "start": pos, "stelle": stelle, "vorschau": QRectF(pos, pos), "zeilen": 1, "spalten": 1}
            return True
        if self.tabellen_modus == "radierer":
            self._radieren(pos)
            return True
        if self.nur_lesen:
            return False
        for name, rc in self.tabellen_griffe().items():
            if not rc.contains(pos):
                continue
            tid = self.tabelle_aktiv()
            if name == "move" and self.tabelle_waehlen is not None:
                self.tabelle_waehlen(tid)
            elif name in ("spalte_plus", "zeile_plus") and self.tabelle_aendern is not None:
                self.tabelle_aendern(name, tid, None)
            elif name == "aufziehen":
                seite, r = self._tabellen_rahmen(tid)
                self._tab_zug = {"art": "aufziehen", "start": pos, "tid": tid, "seite": seite, "rect0": r, "vorschau": self._ansicht_rect(seite, r), "faktor": (1.0, 1.0)}
            return True
        rand = self._rand_bei(pos)
        if rand is not None:
            self._tab_zug = {"art": rand[0], "start": pos, "tid": rand[1], "index": rand[2], "vorschau": None, "delta": 0.0}
            return True
        return False

    def tabellen_maus_bewegen(self, ev) -> bool:
        z, pos = self._tab_zug, ev.position()
        if z is None:
            if self.tabellen_modus == "stift":
                self.setCursor(Qt.CrossCursor)
                return True
            if self.tabellen_modus == "radierer":
                self.setCursor(Qt.PointingHandCursor)
                return True
            if self.nur_lesen:
                return False
            for name, rc in self.tabellen_griffe().items():
                if rc.contains(pos):
                    self.setCursor(Qt.SizeFDiagCursor if name == "aufziehen" else Qt.PointingHandCursor)
                    return True
            rand = self._rand_bei(pos)
            if rand is not None:
                self.setCursor(Qt.SplitHCursor if rand[0] == "spalte" else Qt.SplitVCursor)
                return True
            return False
        if z["art"] == "stift":
            r = QRectF(z["start"], pos).normalized()
            z["vorschau"] = r
            z["spalten"], z["zeilen"] = max(1, round(r.width() / self.zoom / ZELLE_B)), max(1, round(r.height() / self.zoom / ZELLE_H))
        elif z["art"] == "aufziehen":
            r0 = z["rect0"]
            fb = max(0.1, (r0.width() + (pos.x() - z["start"].x()) / self.zoom) / max(1.0, r0.width()))
            fh = max(0.1, (r0.height() + (pos.y() - z["start"].y()) / self.zoom) / max(1.0, r0.height()))
            z["faktor"] = (fb, fh)
            z["vorschau"] = self._ansicht_rect(z["seite"], QRectF(r0.x(), r0.y(), r0.width() * fb, r0.height() * fh))
        else:
            z["delta"] = ((pos.x() - z["start"].x()) if z["art"] == "spalte" else (pos.y() - z["start"].y())) / self.zoom
        self.update()
        return True

    def tabellen_maus_loslassen(self, ev) -> bool:
        z, self._tab_zug = self._tab_zug, None
        if z is None:
            return False
        if z["art"] == "stift":
            if self.tabelle_zeichnen is not None and z["vorschau"].width() > 6 and z["vorschau"].height() > 6:
                self.tabelle_zeichnen(z["stelle"], z["zeilen"], z["spalten"])
            self.tabellen_modus_setzen(None)
        elif z["art"] == "aufziehen":
            if self.tabelle_aendern is not None and z["faktor"] != (1.0, 1.0):
                self.tabelle_aendern("skalieren", z["tid"], z["faktor"])
        elif self.tabelle_aendern is not None and abs(z["delta"]) > 0.5:
            self.tabelle_aendern(z["art"], z["tid"], (z["index"], z["delta"]))
        self.update()
        return True

    def tabellen_modus_setzen(self, modus: str | None) -> None:
        """``"stift"``, ``"radierer"`` oder ``None`` (aus)."""
        self.tabellen_modus = modus
        self._tab_zug = None
        if modus is None:
            self.unsetCursor()
        self.update()

    def _radieren(self, pos) -> None:
        """Eine Zellenlinie unter dem Punkt löschen: die beiden Zellen daneben werden zu einer."""
        if self.tabelle_linie_loeschen is None:
            return
        for s in self.ergebnis().seiten:
            for p in s.plaetze:
                if p.art != "zelle" or p.kopie or p.zeile < 0 or p.spalte < 0:
                    continue
                t = self.sitzung._tabelle(p.block_id)
                z = t.zellen[p.zeile][p.spalte]
                a, b = self._v(s.index, p.rect.right, p.rect.y), self._v(s.index, p.rect.right, p.rect.bottom)
                if abs(pos.x() - a.x()) <= RAND_TREFFER and a.y() <= pos.y() <= b.y() and p.spalte + z.spaltenspanne < t.spalten:
                    self.tabelle_linie_loeschen(t.id, (p.zeile, p.spalte), (p.zeile, p.spalte + z.spaltenspanne))
                    return
                a, b = self._v(s.index, p.rect.x, p.rect.bottom), self._v(s.index, p.rect.right, p.rect.bottom)
                if abs(pos.y() - a.y()) <= RAND_TREFFER and a.x() <= pos.x() <= b.x() and p.zeile + z.zeilenspanne < t.zeilen:
                    self.tabelle_linie_loeschen(t.id, (p.zeile, p.spalte), (p.zeile + z.zeilenspanne, p.spalte))
                    return
