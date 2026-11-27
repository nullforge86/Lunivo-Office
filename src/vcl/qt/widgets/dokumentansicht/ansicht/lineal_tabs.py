"""Tabstopps im waagerechten Lineal: anzeigen, per Klick setzen, mit der Maus verschieben, nach unten herausziehen (löschen), Art wählen.

Ein Baustein von ``LinealH``. Nur Bedienung und Darstellung: die Stopps liest er aus dem wirksamen Absatzformat an der Schreibmarke, die geänderte Liste
meldet das Lineal mit ``tabsGeaendert`` (Millimeter ab der linken Textkante, Ausrichtung, Füllzeichen) – gesetzt wird sie wie im Fenster „Tabstopps“.

Das Wahlfeld ganz links im Lineal zeigt die Art des nächsten Tabstopps; jeder Klick darauf schaltet weiter (links, zentriert, rechts, dezimal).
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen

from writer.anbindung.formatwerte import tabstopps
from writer.werte import px_zu_mm
from vcl.qt.widgets.bausteine.abstaende import LINEAL_FANG, LINEAL_MARKE_RAND, LINEAL_TAB_ARM, LINEAL_TAB_PUNKT, LINEAL_TAB_WEG, STIFT_LINEAL_TAB
from vcl.qt.widgets.bausteine.farben import Farbe

ARTEN = ("links", "mitte", "rechts", "dezimal")                     # Reihenfolge im Wahlfeld
ART_NAMEN = {"links": "Tabstopp links", "mitte": "Tabstopp zentriert", "rechts": "Tabstopp rechts", "dezimal": "Tabstopp dezimal"}
_ART_NACH_NUMMER = dict(enumerate(("links", "rechts", "mitte", "dezimal")))   # Nummern der Arten im Absatzformat


def tab_zeichen(p: QPainter, x: float, y: float, art: str, farbe: QColor) -> None:
    """Das Zeichen eines Tabstopps mit dem Fuß bei (x, y): Winkel nach rechts (links), nach links (rechts), umgekehrtes T (zentriert), mit Punkt (dezimal)."""
    stift = QPen(farbe, STIFT_LINEAL_TAB)
    stift.setCapStyle(Qt.FlatCap)
    p.setPen(stift)
    p.drawLine(QPointF(x, y - LINEAL_TAB_ARM), QPointF(x, y))
    links = x - LINEAL_TAB_ARM if art == "rechts" else x - LINEAL_TAB_ARM / 2 if art in ("mitte", "dezimal") else x
    rechts = x + LINEAL_TAB_ARM if art == "links" else x + LINEAL_TAB_ARM / 2 if art in ("mitte", "dezimal") else x
    p.drawLine(QPointF(links, y), QPointF(rechts, y))
    if art == "dezimal":
        p.setPen(Qt.NoPen)
        p.setBrush(farbe)
        p.drawEllipse(QPointF(x + LINEAL_TAB_ARM / 2, y - LINEAL_TAB_ARM / 2), LINEAL_TAB_PUNKT, LINEAL_TAB_PUNKT)


class LinealTabs:
    """Zustand: ``_tab_art`` (Art des nächsten Stopps), beim Ziehen ``_tab_liste`` (Arbeitskopie), ``_tab_zieh`` (Nummer darin), ``_tab_weg`` (herausgezogen)."""
    _tab_art = ARTEN[0]
    _tab_liste = None
    _tab_zieh = None
    _tab_weg = False

    # ---- Lesen ------------------------------------------------------------------------------------------------------------------------
    def tabs(self) -> list[list]:
        """Die Tabstopps des Absatzes an der Schreibmarke: [[Millimeter, Ausrichtung, Füllzeichen], …]."""
        af = self.e.absatzformat()
        fuell = {}
        for teil in str(af.get("tabfuell") or "").split(";"):          # „Position:Schlüssel;…“ wie ``set_tabstopps`` es schreibt
            pos, _trenner, schluessel = teil.partition(":")
            try:
                fuell[float(pos)] = schluessel
            except ValueError:
                continue
        return [[round(px_zu_mm(pos), 1), _ART_NACH_NUMMER.get(art, ARTEN[0]), next((f for q, f in fuell.items() if abs(q - pos) < 1), "")]
                for pos, art, _zeichen in tabstopps(af)]

    def _tab_stand(self) -> list[list]:
        return self._tab_liste if self._tab_liste is not None else self.tabs()

    def _tab_fuss(self) -> float:
        return self.height() - LINEAL_MARKE_RAND

    def _wahlfeld(self) -> QRectF:
        return QRectF(0, 0, self.height(), self.height())

    # ---- Zeichnen ---------------------------------------------------------------------------------------------------------------------
    def tabs_zeichnen(self, p: QPainter, m: dict, c: dict) -> None:
        """Die Stopps auf dem Lineal und das Wahlfeld der Art; der gezogene Stopp in der Akzentfarbe, ein herausgezogener gar nicht."""
        zahl, _strich = self.stifte(c)
        for nr, (mm, art, _fuell) in enumerate(self._tab_stand()):
            gezogen = nr == self._tab_zieh
            if gezogen and self._tab_weg:
                continue
            tab_zeichen(p, m["links"] + self.px(mm), self._tab_fuss(), art, QColor(Farbe.AKZENT_DUNKEL) if gezogen else c["schrift"])
        feld = self._wahlfeld()
        p.setPen(Qt.NoPen)
        p.setBrush(c["grund"])
        p.drawRect(feld)
        mitte = feld.center()
        tab_zeichen(p, mitte.x(), mitte.y() + LINEAL_TAB_ARM / 2, self._tab_art, zahl)

    # ---- Maus -------------------------------------------------------------------------------------------------------------------------
    def tab_treffer(self, x: float, y: float, m: dict):
        """Nummer des Stopps unter der Maus (untere Hälfte des Lineals) oder ``None``."""
        if y < self.height() / 2:
            return None
        for nr, (mm, _art, _fuell) in enumerate(self._tab_stand()):
            if abs(x - m["links"] - self.px(mm)) <= LINEAL_FANG:
                return nr
        return None

    def tab_hinweis(self, x: float, y: float) -> str:
        return ART_NAMEN[self._tab_art] + " – Klick wählt die nächste Art" if self._wahlfeld().contains(x, y) else ""

    def tab_druecken(self, x: float, y: float, m: dict) -> bool:
        """Klick ins Lineal: Wahlfeld schaltet die Art weiter, ein Stopp wird gegriffen, eine freie Stelle im Textbereich bekommt einen neuen. → behandelt?"""
        if self._wahlfeld().contains(x, y):
            self._tab_art = ARTEN[(ARTEN.index(self._tab_art) + 1) % len(ARTEN)]
            self.update()
            return True
        nr = self.tab_treffer(x, y, m)
        if nr is None and not (y >= self.height() / 2 and m["links"] <= x <= m["rechts"]):
            return False
        self._tab_liste = [list(t) for t in self.tabs()]
        if nr is None:
            self._tab_liste.append([0.0, self._tab_art, ""])
            nr = len(self._tab_liste) - 1
        self._tab_zieh, self._tab_weg = nr, False
        self.tab_ziehen(x, y, m)
        return True

    def tab_ziehen(self, x: float, y: float, m: dict) -> None:
        """Der gegriffene Stopp folgt der Maus innerhalb des Textbereichs; weit unter das Lineal gezogen ist er zum Löschen vorgemerkt."""
        breite = px_zu_mm((m["rechts"] - m["links"]) / self.e.zoom)
        mm = px_zu_mm((x - m["links"]) / self.e.zoom)
        self._tab_liste[self._tab_zieh][0] = round(max(0.0, min(mm, breite)), 1)
        self._tab_weg = y > self.height() + LINEAL_TAB_WEG
        if self._tab_weg:
            self.hilfslinie.weg()
        else:
            self.hilfslinie.zeigen(m["links"] + self.px(self._tab_liste[self._tab_zieh][0]))
        self.update()

    def tab_loslassen(self) -> list[tuple]:
        """Das Ziehen beenden. → die neue Liste der Stopps, aufsteigend (ohne den herausgezogenen)."""
        liste = [tuple(t) for nr, t in enumerate(self._tab_liste) if not (nr == self._tab_zieh and self._tab_weg)]
        self._tab_liste = self._tab_zieh = None
        self._tab_weg = False
        self.hilfslinie.weg()
        self.update()
        return sorted(liste)
