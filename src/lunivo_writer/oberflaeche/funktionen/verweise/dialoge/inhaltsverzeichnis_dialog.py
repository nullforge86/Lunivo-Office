"""Dialog „Inhaltsverzeichnis“: links Füllzeichen, Ebenen anzeigen, Seitenzahlen anzeigen/rechtsbündig, Hyperlinks verwenden; rechts die Seitenansicht.

    d = InhaltsverzeichnisDialog(parent, {"fuell": "punkt", "ebenen": 3, …})   # if d.exec(): d.ergebnis() → dict

Das Fenster ändert das Dokument nicht; der Aufrufer setzt das Ergebnis um."""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFontMetricsF, QPainter
from PySide6.QtWidgets import QDialog, QLabel, QSpinBox, QWidget

from lunivo_writer.farmwork.funktionen.verweise.konstanten import FUELLZEICHEN, INHALTSVERZEICHNIS_FUELL, INHALTSVERZEICHNIS_VORGABE
from lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen import VorschauFlaeche, fussleiste
from lunivo_writer.oberflaeche.baukasten.basis.mass import (ABSTAND_BLOCK, DROPDOWN_ZEICHEN_KURZ, HOEHE_KNOPF, HOEHE_KNOPF_GROSS, RAND_KEIN,
                                                                      SCHRIFT_VORSCHAU_VERZEICHNIS)
from lunivo_writer.oberflaeche.baukasten.bausteine.haken.haken import haken
from lunivo_writer.oberflaeche.baukasten.bausteine.knopf.knopf import knopf
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld import Auswahlfeld
from lunivo_writer.farmwork.datentypen.farben import Farbe
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FormularGitter, gruppe
from lunivo_writer.oberflaeche.baukasten.geruest.rollen import reihe as _reihe, spalte as _spalte
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import PanelFaehig
from lunivo_writer.oberflaeche.funktionen.verweise.dialoge.dialog_hilfen import titel as _titel

_FUELL_ANZEIGE = {"": "(ohne)", "punkt": "." * 24, "strich": "-" * 20, "linie": "_" * 18}


class InhaltsverzeichnisDialog(PanelFaehig, QDialog):
    """Links Füllzeichen, Ebenen anzeigen, Seitenzahlen anzeigen/rechtsbündig, Hyperlinks verwenden; rechts die Seitenansicht."""

    def __init__(self, parent=None, opt: dict | None = None):
        super().__init__(parent)
        o = {**INHALTSVERZEICHNIS_VORGABE, **(opt or {})}
        self.setWindowTitle("Inhaltsverzeichnis")
        v = _spalte("standard", self)
        box = gruppe("Inhaltsverzeichnis"); h = _reihe("standard", box); h.setSpacing(ABSTAND_BLOCK)
        links = _spalte("standard")
        self.fuell = Auswahlfeld(); self.fuell.setAccessibleName("Füllzeichen")
        for schl in INHALTSVERZEICHNIS_FUELL:
            self.fuell.addItem(_FUELL_ANZEIGE[schl], schl)
        self.fuell.zeichen(DROPDOWN_ZEICHEN_KURZ)
        self.fuell.setCurrentIndex(max(0, self.fuell.findData(o["fuell"])))
        self.ebenen = QSpinBox(); self.ebenen.setRange(1, 9); self.ebenen.setValue(int(o["ebenen"])); self.ebenen.setMinimumHeight(HOEHE_KNOPF)
        self.ebenen.setAccessibleName("Ebenen anzeigen")
        self.seitenzahlen = haken("standard", "Seitenza&hlen anzeigen", an=bool(o["seitenzahlen"]))
        self.rechts = haken("standard", "Seitenzahlen &rechtsbündig", an=bool(o["rechts"]))
        self.links = haken("standard", "&Hyperlinks verwenden", an=bool(o["links"]))
        optionen = knopf("gross", "&Optionen…", aktiv=False)   # Vorlagen den Ebenen zuordnen: fehlt noch
        fw = QWidget(); fg = FormularGitter(fw); fg.setContentsMargins(*RAND_KEIN)
        fg.reihe((_titel("Füllzei&chen:", self.fuell), self.fuell))
        fg.reihe((_titel("&Ebenen anzeigen:", self.ebenen), self.ebenen))
        links.addWidget(fw)
        for w in (self.seitenzahlen, self.rechts, self.links):
            links.addWidget(w)
        z = _reihe("standard"); z.addWidget(optionen); z.addStretch(1); links.addLayout(z)
        links.addStretch(1)
        h.addLayout(links)
        rechts = _spalte("standard")
        rechts.addWidget(QLabel("Seitenansicht"))
        self.vorschau = VorschauFlaeche(self._male, 190)
        rechts.addWidget(self.vorschau, 1)
        h.addLayout(rechts, 1)
        v.addWidget(box)
        self._teile = h
        fussleiste(self, v)
        for w in (self.seitenzahlen, self.rechts, self.links):
            w.toggled.connect(self._auffrischen)
        self.fuell.currentIndexChanged.connect(self._auffrischen); self.ebenen.valueChanged.connect(self._auffrischen)
        self._auffrischen()

    def kompakt_machen(self) -> None:
        """In der Seitenleiste: die Seitenansicht unter den Einstellungen."""
        self._teile.senkrecht_stellen()
        self.vorschau.setMinimumWidth(0)

    def ergebnis(self) -> dict:
        return {"fuell": self.fuell.currentData() or "", "ebenen": self.ebenen.value(), "seitenzahlen": self.seitenzahlen.isChecked(),
                "rechts": self.rechts.isChecked(), "links": self.links.isChecked()}

    def _auffrischen(self, *_):
        self.rechts.setEnabled(self.seitenzahlen.isChecked())
        self.fuell.setEnabled(self.seitenzahlen.isChecked() and self.rechts.isChecked())
        self.vorschau.update()

    def _male(self, p: QPainter, r) -> None:
        o = self.ergebnis()
        f = p.font(); f.setPixelSize(SCHRIFT_VORSCHAU_VERZEICHNIS); p.setFont(f)
        fm = QFontMetricsF(f)
        p.setPen(QColor(Farbe.TINTE_DUNKEL))
        zeichen = FUELLZEICHEN.get(o["fuell"], ("", "", ""))[1] if o["rechts"] else ""
        y = r.top() + 2
        for i in range(min(o["ebenen"], 7)):
            x = r.left() + 10 * i
            text, zahl = f"Überschrift {i + 1}", str(1 + 2 * i)
            p.drawText(QRectF(x, y, r.right() - x, fm.height()), Qt.AlignLeft | Qt.AlignVCenter, text)
            if o["seitenzahlen"]:
                if o["rechts"]:
                    p.drawText(QRectF(r.left(), y, r.width(), fm.height()), Qt.AlignRight | Qt.AlignVCenter, zahl)
                    if zeichen:
                        von, bis = x + fm.horizontalAdvance(text) + 3, r.right() - fm.horizontalAdvance(zahl) - 3
                        n = max(0, int((bis - von) // fm.horizontalAdvance(zeichen)))
                        p.drawText(QRectF(von, y, bis - von, fm.height()), Qt.AlignLeft | Qt.AlignVCenter, zeichen * n)
                else:
                    p.drawText(QRectF(x + fm.horizontalAdvance(text + " "), y, r.width(), fm.height()), Qt.AlignLeft | Qt.AlignVCenter, zahl)
            y += fm.height() + 6
