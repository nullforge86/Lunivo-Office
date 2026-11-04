"""Textfüllung der Diagramm-Textoptionen mit fünf Arten wie in der Vorlage: Keine Füllung · Einfarbige Füllung · Farbverlauf · Bild- oder Texturfüllung · Musterfüllung.

Mixin für ``DiagrammTextPanel`` (vor ``TextKopfMenueMixin``); die Basis ``texteffekt_dialog.py`` kennt nur die ersten drei und bleibt unverändert.
``_text_fuellarten_bauen()`` hängt die zwei fehlenden Radios (``r_bild``, ``r_muster``) hinter den Farbverlauf und ordnet die Felder darunter:

- Bild oder Textur: Auswahl der Textur (``p_textur``) und „Bilddatei wählen …“ (``p_bildknopf``; das Bild wird mit ``diagramm_format.bild_kodieren`` gespeichert),
- Muster: Muster (``p_muster``), Vorder- (``p_vorn``) und Hintergrundfarbe (``p_grund``).

``werte()`` liefert dann ``fuell`` = „muster“ bzw. „bild“ und ``fuell_pinsel`` (``{"art": "muster"|"textur"|"bild", "key", "farbe", "grund", "bild_b64"}``, Format von
``textfx.fuell_pinsel_von``); ``_setze_fuellung`` liest es zurück. Ohne gewählte neue Art ändert sich nichts (Standard bleibt „Einfarbige Füllung“).
"""
from __future__ import annotations

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QComboBox, QFileDialog, QPushButton, QRadioButton, QWidget

from lunivo_writer.core.farben import Farbe
from lunivo_writer.editor import diagramm_format as DF
from lunivo_writer.editor import muster as M
from lunivo_writer.ui.baukasten.farbpalette import FarbFeld
from lunivo_writer.ui.baukasten.formular_gitter import FormularGitter
from lunivo_writer.ui.baukasten.objekt_menues import TEXTUREN

_BILD_FILTER = "Bilder (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;Alle Dateien (*)"


class TextFuellartenMixin:
    def _text_fuellarten_bauen(self) -> None:
        a = self.a_fuell
        self._p_art, self._p_bild = "textur", ""
        self.r_bild, self.r_muster = QRadioButton("Bild- oder Texturfüllung"), QRadioButton("Musterfüllung")
        g = a.gitter
        for w in (self.f_einfarbig, self.f_verlauf):                  # die Felder der alten Arten kommen hinter die neuen Radios
            for i in range(g.count()):
                if g.itemAt(i).widget() is w:
                    g.takeAt(i)
                    break
        for x in (self.r_bild, self.r_muster, self.f_einfarbig, self.f_verlauf):
            a.breit(x)
        self.p_textur = QComboBox()
        for schl, name in TEXTUREN:
            self.p_textur.addItem(name, schl)
        self.p_bildknopf = QPushButton("Bilddatei wählen …")
        self.f_bild = QWidget(); fb = FormularGitter(self.f_bild)
        fb.zeile("Textur:", self.p_textur); fb.breit(self.p_bildknopf)
        self.p_muster = QComboBox()
        for schl, _n, _o in M.MUSTER:
            if schl != "loeschen":
                self.p_muster.addItem(M.name_von(schl), schl)
        self.p_vorn, self.p_grund = FarbFeld(Farbe.SCHWARZ, "Vordergrundfarbe"), FarbFeld(Farbe.WEISS, "Hintergrundfarbe", keine_text="Keine")
        self.f_muster = QWidget(); fm = FormularGitter(self.f_muster)
        fm.zeile("Muster:", self.p_muster); fm.zeile("Vordergrund:", self.p_vorn); fm.zeile("Hintergrund:", self.p_grund)
        a.breit(self.f_bild); a.breit(self.f_muster)
        for r in (self.r_bild, self.r_muster):
            r.toggled.connect(self._neu)
        self.p_textur.currentIndexChanged.connect(lambda *_: self._pinsel_wahl("textur"))
        self.p_bildknopf.clicked.connect(self._bild_waehlen)
        self.p_muster.currentIndexChanged.connect(lambda *_: self._pinsel_wahl("muster"))
        self.p_vorn.farbeGeaendert.connect(lambda *_: self._pinsel_wahl("muster"))
        self.p_grund.farbeGeaendert.connect(lambda *_: self._pinsel_wahl("muster"))
        self._sichtbar()

    def _pinsel_wahl(self, art: str) -> None:
        """Ein Feld einer neuen Art wurde bedient: damit ist diese Art gewählt."""
        if art == "muster":
            self.r_muster.setChecked(True)
        else:
            self._p_art = "textur"; self.r_bild.setChecked(True)
        self._neu()

    def _bild_waehlen(self) -> None:
        pfad, _ = QFileDialog.getOpenFileName(self, "Bilddatei wählen", "", _BILD_FILTER)
        if not pfad:
            return
        text = DF.bild_kodieren(QImage(pfad))
        if not text:
            return                                                   # keine lesbare Bilddatei: Zustand bleibt, wie er war
        self._p_bild, self._p_art = text, "bild"
        self.r_bild.setChecked(True)
        self._neu()

    def _sichtbar(self) -> None:
        super()._sichtbar()
        if hasattr(self, "f_bild"):
            self.f_bild.setVisible(self.r_bild.isChecked()); self.f_muster.setVisible(self.r_muster.isChecked())
            self.a_fuell.gitter.invalidate(); self.a_fuell.updateGeometry()          # die Höhe folgt den eben ein-/ausgeblendeten Feldern

    def _setze_fuellung(self, w: dict) -> None:
        super()._setze_fuellung(w)
        if not hasattr(self, "r_bild"):
            return
        p = w.get("fuell_pinsel") or {}
        art = p.get("art")
        felder = (self.r_bild, self.r_muster, self.p_textur, self.p_muster, self.p_vorn, self.p_grund)
        for x in felder:
            x.blockSignals(True)
        self.r_muster.setChecked(art == "muster"); self.r_bild.setChecked(art in ("textur", "bild"))
        self._p_art = "bild" if art == "bild" and p.get("bild_b64") else "textur"
        self._p_bild = p.get("bild_b64", "") if art == "bild" else ""
        self.p_textur.setCurrentIndex(max(0, self.p_textur.findData(p.get("key") if art == "textur" else "papier")))
        self.p_muster.setCurrentIndex(max(0, self.p_muster.findData(p.get("key") if art == "muster" else "rein")))
        self.p_vorn.setFarbe(p.get("farbe") or Farbe.SCHWARZ if art == "muster" else Farbe.SCHWARZ)
        self.p_grund.setFarbe(p.get("grund") or Farbe.WEISS if art == "muster" else Farbe.WEISS)
        for x in felder:
            x.blockSignals(False)

    def werte(self) -> dict:
        w = super().werte()
        if not hasattr(self, "r_bild"):
            return w
        if self.r_muster.isChecked():
            w["fuell"] = "muster"
            w["fuell_pinsel"] = {"art": "muster", "key": self.p_muster.currentData() or "rein", "farbe": self.p_vorn.farbe or Farbe.SCHWARZ}
            if self.p_grund.farbe:
                w["fuell_pinsel"]["grund"] = self.p_grund.farbe
        elif self.r_bild.isChecked():
            w["fuell"] = "bild"
            if self._p_art == "bild" and self._p_bild:
                w["fuell_pinsel"] = {"art": "bild", "bild_b64": self._p_bild}
            else:
                w["fuell_pinsel"] = {"art": "textur", "key": self.p_textur.currentData() or "papier"}
        return w
