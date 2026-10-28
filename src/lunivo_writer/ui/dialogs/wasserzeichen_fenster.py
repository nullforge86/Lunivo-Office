"""Fenster „Wasserzeichen“ nach der WPS-Vorlage: oben Bildwasserzeichen, darunter Textwasserzeichen, Transparenz, rechts die Vorschau
und „Übernehmen für“. Höchstens eine der beiden Arten ist angekreuzt; ohne Kreuz gibt es kein Wasserzeichen.

    d = WasserzeichenDialog(parent, page.watermark, page)
    if d.exec(): d.ergebnis(), d.bereich()      # Wasserzeichen-Wörterbuch (oder None), "dokument" | "abschnitt"

Das Fenster ändert das Dokument nicht. Aufbau des Wörterbuchs: ``editor/wasserzeichen.py``.
"""
from __future__ import annotations

import os

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QPen
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QFontComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QSpinBox, QVBoxLayout,
)

from lunivo_writer.editor import wasserzeichen as WZ
from lunivo_writer.models.page import PageSettings, mm_to_px
from lunivo_writer.ui.baukasten.dialog_rahmen import VorschauFlaeche, fussleiste
from lunivo_writer.ui.baukasten.farbpalette import FarbFeld
from lunivo_writer.ui.baukasten.mass_feld import MassSpin
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig

AUTOMATISCH = "Automatisch"


def _titel(text: str, feld) -> QLabel:
    t = QLabel(text); t.setBuddy(feld)
    return t


def _feld(w, breite: int = 130):
    w.setMinimumHeight(34); w.setMinimumWidth(breite)
    return w


class WasserzeichenDialog(PanelFaehig, QDialog):
    BEREICHE = (("dokument", "Gesamtes Dokument"), ("abschnitt", "Aktueller Abschnitt"))

    def __init__(self, parent=None, aktuell: dict | None = None, page: PageSettings | None = None, ordner: str = ""):
        super().__init__(parent)
        a = dict(aktuell or {})
        self._page = page or PageSettings()
        self._ordner = ordner
        self._bild_text = a.get("bild") or ""
        self.entfernt = False
        self.setWindowTitle("Wasserzeichen")
        haupt = QVBoxLayout(self)
        haupt.addWidget(QLabel("Wasserzeichen einstellen"))
        h = QHBoxLayout(); haupt.addLayout(h, 1)
        links = QVBoxLayout(); h.addLayout(links, 3)
        g = QGridLayout(); g.setHorizontalSpacing(8); links.addLayout(g)
        g.setProperty("schmal_nein", True)                            # Raster bleibt auch in der Seitenleiste ein Raster
        z = 0
        # ---- Bildwasserzeichen ----
        self.mit_bild = QCheckBox("&Bildwasserzeichen"); g.addWidget(self.mit_bild, z, 0, 1, 4); z += 1
        self.bild_knopf = _feld(QPushButton("Bild a&uswählen"), 120); self.bild_name = QLabel("(Keine Grafik)")
        g.addWidget(self.bild_knopf, z, 0); g.addWidget(self.bild_name, z, 1, 1, 3); z += 1
        self.zoom = _feld(QComboBox()); self.zoom.addItem(AUTOMATISCH, 0)
        for n in WZ.ZOOMS:
            self.zoom.addItem(f"{n} %", n)
        self.auswaschen = QCheckBox("Aus&waschen")
        g.addWidget(_titel("&Zoom:", self.zoom), z, 0); g.addWidget(self.zoom, z, 1); g.addWidget(self.auswaschen, z, 2, 1, 2); z += 1
        self.bild_format, self.bild_h, self.bild_h_mm, self.bild_v, self.bild_v_mm = self._lage_felder(g, z, "")
        z += 3
        self._bild_teile = [self.bild_knopf, self.bild_name, self.zoom, self.auswaschen, self.bild_format, self.bild_h, self.bild_h_mm,
                            self.bild_v, self.bild_v_mm]
        # ---- Textwasserzeichen ----
        self.mit_text = QCheckBox("Te&xtwasserzeichen"); g.addWidget(self.mit_text, z, 0, 1, 4); z += 1
        self.inhalt = _feld(QComboBox(), 180); self.inhalt.setEditable(True); self.inhalt.addItems(list(WZ.VORGABEN))
        self.schrift = _feld(QFontComboBox(), 180); self.schrift.setMaximumWidth(260)
        self.groesse = _feld(QComboBox(), 120); self.groesse.setEditable(True); self.groesse.addItem(AUTOMATISCH)
        for n in WZ.GROESSEN:
            self.groesse.addItem(str(n))
        self.farbe = _feld(FarbFeld(a.get("farbe") or WZ.STANDARD_FARBE, "Farbe"), 120)
        for text, feld in (("&Inhalt:", self.inhalt), ("&Schriftart:", self.schrift), ("&Größe:", self.groesse), ("&Farbe:", self.farbe)):
            g.addWidget(_titel(text, feld), z, 0); g.addWidget(feld, z, 1, 1, 2); z += 1
        self.text_format, self.text_h, self.text_h_mm, self.text_v, self.text_v_mm = self._lage_felder(g, z, "t")
        z += 3
        self._text_teile = [self.inhalt, self.schrift, self.groesse, self.farbe, self.text_format, self.text_h, self.text_h_mm,
                            self.text_v, self.text_v_mm]
        # ---- Transparenz ----
        self.transparenz = QSlider(Qt.Horizontal); self.transparenz.setRange(0, 100)
        self.transparenz_zahl = _feld(QSpinBox(), 80); self.transparenz_zahl.setRange(0, 100); self.transparenz_zahl.setSuffix(" %")
        g.addWidget(_titel("&Transparenz:", self.transparenz), z, 0); g.addWidget(self.transparenz, z, 1, 1, 2)
        g.addWidget(self.transparenz_zahl, z, 3)
        for t, f in ((self.transparenz, self.transparenz_zahl), (self.transparenz_zahl, self.transparenz)):
            t.valueChanged.connect(f.setValue)
        g.setColumnStretch(1, 1)
        links.addStretch(1)
        # ---- rechts: Vorschau, Übernehmen für ----
        rechts = QVBoxLayout(); h.addLayout(rechts, 2)
        rechts.addWidget(QLabel("Vorschau"))
        self.vorschau = VorschauFlaeche(self._male, 280)
        self.vorschau.setMinimumWidth(200)
        rechts.addWidget(self.vorschau, 1)
        self.bereich_wahl = _feld(QComboBox(), 200)
        for k, t in self.BEREICHE:
            self.bereich_wahl.addItem(t, k)
        rechts.addWidget(_titel("Ü&bernehmen für:", self.bereich_wahl)); rechts.addWidget(self.bereich_wahl)
        fussleiste(self, haupt)
        self._vorbelegen(a)
        # Verbindungen
        self.mit_bild.toggled.connect(lambda an: self._art(an, self.mit_text))
        self.mit_text.toggled.connect(lambda an: self._art(an, self.mit_bild))
        self.bild_knopf.clicked.connect(self._bild_waehlen)
        for w in (self.zoom, self.bild_format, self.bild_h, self.bild_v, self.groesse, self.text_format, self.text_h, self.text_v):
            w.currentIndexChanged.connect(self._zustand)
        for w in (self.bild_h_mm, self.bild_v_mm, self.text_h_mm, self.text_v_mm, self.transparenz):
            w.valueChanged.connect(self._zustand)
        self.auswaschen.toggled.connect(self._zustand)
        self.inhalt.currentTextChanged.connect(self._zustand); self.groesse.currentTextChanged.connect(self._zustand)
        self.schrift.currentFontChanged.connect(self._zustand); self.farbe.farbeGeaendert.connect(self._zustand)
        self._zustand()

    def _lage_felder(self, g: QGridLayout, z: int, kuerzel: str):
        """Format, Horizontal und Vertikal (je Liste und Abstand vom Rand) ab Zeile ``z``."""
        fmt = _feld(QComboBox())
        for w, t in WZ.FORMATE:
            fmt.addItem(t, w)
        felder = [fmt]
        g.addWidget(_titel("F&ormat:" if kuerzel else "Fo&rmat:", fmt), z, 0); g.addWidget(fmt, z, 1)
        for i, (titel, werte) in enumerate((("&Horizontal:" if not kuerzel else "Hori&zontal:", WZ.HORIZONTAL),
                                             ("Verti&kal:" if not kuerzel else "&Vertikal:", WZ.VERTIKAL))):
            c = _feld(QComboBox())
            for k, t in werte:
                c.addItem(t, k)
            m = _feld(MassSpin(), 90); m.setRange(0, 300); m.setDecimals(1); m.setAccessibleName(titel.replace("&", "") + " Abstand")
            g.addWidget(_titel(titel, c), z + 1 + i, 0); g.addWidget(c, z + 1 + i, 1); g.addWidget(m, z + 1 + i, 2, 1, 2)
            felder += [c, m]
        return tuple(felder)

    def _vorbelegen(self, a: dict) -> None:
        bild = bool(a.get("bild"))
        text = bool((a.get("text") or "").strip()) and not bild
        self.mit_bild.setChecked(bild); self.mit_text.setChecked(text)
        if bild:
            self.bild_name.setText(a.get("bild_name") or "(Bild)")
            self.zoom.setCurrentIndex(max(0, self.zoom.findData(int(a.get("zoom", 0) or 0))))
        self.auswaschen.setChecked(bool(a.get("auswaschen", True)))
        if text:
            self.inhalt.setCurrentText(a["text"])
        if a.get("schrift"):
            self.schrift.setCurrentFont(QFont(a["schrift"]))
        pt = int(a.get("groesse_pt", 0) or 0) if "transparenz" in a or not text else int(a.get("groesse_pt", 80) or 0)
        self.groesse.setCurrentText(str(pt) if pt else AUTOMATISCH)
        for fmt, hz, hm, vt, vm in ((self.bild_format, self.bild_h, self.bild_h_mm, self.bild_v, self.bild_v_mm),
                                    (self.text_format, self.text_h, self.text_h_mm, self.text_v, self.text_v_mm)):
            fmt.setCurrentIndex(max(0, fmt.findData(int(a.get("winkel", 0 if fmt is self.bild_format else -45) or 0))))
            hz.setCurrentIndex(max(0, hz.findData(a.get("h", "mitte")))); hm.setValue(float(a.get("h_mm", 0)))
            vt.setCurrentIndex(max(0, vt.findData(a.get("v", "mitte")))); vm.setValue(float(a.get("v_mm", 0)))
        self.transparenz.setValue(int(a.get("transparenz", 50)))
        self.bereich_wahl.setCurrentIndex(1 if a.get("abschnitt") else 0)

    def _art(self, an: bool, andere: QCheckBox) -> None:
        if an and andere.isChecked():
            andere.setChecked(False)
        self._zustand()

    def _bild_waehlen(self) -> None:
        from lunivo_writer.ui.baukasten.speichern_fenster import datei_waehlen
        wahl = datei_waehlen(self, "Bild auswählen", self._ordner or os.path.expanduser("~"),
                             "Bilder (*.png *.jpg *.jpeg *.bmp *.gif *.svg *.webp);;Alle Dateien (*)")
        if wahl:
            self.bild_laden(wahl[0])

    def bild_laden(self, pfad: str) -> bool:
        img = QImage(pfad)
        if img.isNull():
            self.bild_name.setText("(Bild lässt sich nicht lesen)")
            return False
        if max(img.width(), img.height()) > 2000:                     # klein genug für die Einrichtung des Dokuments
            img = img.scaled(2000, 2000, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._bild_text = WZ.bild_zu_text(img)
        self.bild_name.setText(os.path.basename(pfad))
        self._zustand()
        return True

    def _zustand(self, *_a) -> None:
        for w in self._bild_teile:
            w.setEnabled(self.mit_bild.isChecked())
        self.bild_name.setEnabled(True)
        for w in self._text_teile:
            w.setEnabled(self.mit_text.isChecked())
        aktiv = self.mit_bild.isChecked() or self.mit_text.isChecked()
        self.transparenz.setEnabled(aktiv); self.transparenz_zahl.setEnabled(aktiv)
        for hz, hm, vt, vm, an in ((self.bild_h, self.bild_h_mm, self.bild_v, self.bild_v_mm, self.mit_bild.isChecked()),
                                   (self.text_h, self.text_h_mm, self.text_v, self.text_v_mm, self.mit_text.isChecked())):
            hm.setEnabled(an and hz.currentData() != "mitte"); vm.setEnabled(an and vt.currentData() != "mitte")
        self.vorschau.update()

    def _male(self, p, r) -> None:
        pw, ph = mm_to_px(self._page.width_mm), mm_to_px(self._page.height_mm)
        f = min(r.width() / pw, r.height() / ph)
        blatt = QRectF(r.center().x() - pw * f / 2, r.center().y() - ph * f / 2, pw * f, ph * f)
        p.save()
        p.setPen(QColor("#a0a0a0"))                                  # Eckmarken des Satzspiegels wie in der Vorlage
        ml, mr = mm_to_px(self._page.margin_left_mm) * f, mm_to_px(self._page.margin_right_mm) * f
        mt, mb = mm_to_px(self._page.margin_top_mm) * f, mm_to_px(self._page.margin_bottom_mm) * f
        l = 6
        for x, y, dx, dy in ((blatt.left() + ml, blatt.top() + mt, -1, -1), (blatt.right() - mr, blatt.top() + mt, 1, -1),
                             (blatt.left() + ml, blatt.bottom() - mb, -1, 1), (blatt.right() - mr, blatt.bottom() - mb, 1, 1)):
            p.setPen(QPen(QColor("#a0a0a0"), 1))
            p.drawLine(x, y, x + dx * l, y); p.drawLine(x, y, x, y + dy * l)
        p.translate(blatt.topLeft()); p.scale(f, f)
        WZ.zeichnen(p, self.ergebnis(), QRectF(0, 0, pw, ph))
        p.restore()

    def ergebnis(self) -> dict | None:
        """Das eingestellte Wasserzeichen; None, wenn keine Art angekreuzt ist (oder kein Bild bzw. kein Text da ist)."""
        if self.entfernt:
            return None
        w = {"transparenz": self.transparenz.value()}
        if self.bereich_wahl.currentData() == "abschnitt":
            w["abschnitt"] = True
        if self.mit_bild.isChecked() and self._bild_text:
            w.update(bild=self._bild_text, bild_name=self.bild_name.text(), zoom=self.zoom.currentData(), auswaschen=self.auswaschen.isChecked(),
                     winkel=self.bild_format.currentData(), h=self.bild_h.currentData(), h_mm=self.bild_h_mm.value(),
                     v=self.bild_v.currentData(), v_mm=self.bild_v_mm.value())
            return w
        text = self.inhalt.currentText().strip()
        if self.mit_text.isChecked() and text:
            g = self.groesse.currentText().strip()
            w.update(text=text, schrift=self.schrift.currentFont().family(), groesse_pt=int(g) if g.isdigit() else 0, farbe=self.farbe.farbe,
                     winkel=self.text_format.currentData(), h=self.text_h.currentData(), h_mm=self.text_h_mm.value(),
                     v=self.text_v.currentData(), v_mm=self.text_v_mm.value())
            return w
        return None

    def bereich(self) -> str:
        return self.bereich_wahl.currentData()
