"""„Als Bild exportieren“: die Bildlayoutkarten und Einstellungen in der rechten Spalte des Datei-Menüs.

Oben zwei Karten — **Jede Seite** (eine Datei je Seite) und **Langes Bild** (alle Seiten untereinander) —, darunter Wasserzeichen,
Qualität, Format und Zielordner, rechts unten **Exportieren**. Die Bildchen auf den Karten zeichnet ``QPainter``; geschrieben wird
in ``dienste/bild_export.py``.
"""
from __future__ import annotations

from lunivo_writer.oberflaeche.baukasten.basis.mass import ABSTAND_BLOCK as _A_BLOCK, ABSTAND_GROSS as _A_GROSS, ABSTAND_MITTEL as _A_MITTEL

from lunivo_writer.oberflaeche.baukasten.basis.darstellung import eigenschaft, rolle as _rolle

from lunivo_writer.oberflaeche.baukasten.geruest.rollen import anwenden, raender, reihe as _reihe, spalte as _spalte

from lunivo_writer.oberflaeche.baukasten.basis.daten import text as _t

import os
from typing import Callable

from PySide6.QtCore import QPointF, QRectF, QSize, QStandardPaths, Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QPainter, QPainterPath, QPalette, QPen
from PySide6.QtWidgets import QAbstractButton, QButtonGroup, QComboBox, QLabel, QLineEdit, QLayout, QPushButton, QWidget

from lunivo_writer.oberflaeche.baukasten.farben.farben import Farbe
from lunivo_writer.oberflaeche.baukasten.basis.mass import ABSTAND_EXPORT_ABSCHNITT, ABSTAND_MITTEL, GROESSE_EXPORTKARTE, HOEHE_KNOPF_GROSS, ICON_GROSS, RAND_EXPORT_BILD, RAND_OBEN_SEITE, RAND_ZEILE_LOCKER
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld import Auswahlfeld

# Sinnbild „dunkles Blatt“ im Exportdialog: bewusst feste Farben, unabhängig vom Thema.
BILDCHEN_BLATT_DUNKEL = "#3a3f45"
BILDCHEN_AKZENT_DUNKEL = "#6b5442"
from lunivo_writer.dienste.bild_export import FORMATE, QUALITAET, BildWahl

from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FELDHOEHE, FlussLayout, FormularGitter, abschnittstitel


class _Karte(QAbstractButton):
    """Eine wählbare Karte mit Bildchen und Beschriftung; gewählt mit blauem Rand und Haken in der Ecke."""

    def __init__(self, text: str, lang: bool):
        super().__init__()
        self.setText(text)
        self.lang = lang
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(*GROESSE_EXPORTKARTE)
        self.setAccessibleName(text)

    def sizeHint(self) -> QSize:
        return QSize(*GROESSE_EXPORTKARTE)

    def paintEvent(self, _e) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pal = self.palette()
        dunkel = pal.color(QPalette.Window).lightness() < 128
        grund = pal.color(QPalette.Base).darker(104 if not dunkel else 90)
        akzent = QColor(Farbe.AKZENT_DUNKEL if dunkel else Farbe.AKZENT)
        rahmen = akzent if self.isChecked() else pal.color(QPalette.Mid).lighter(125)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        p.fillRect(r, grund)
        p.setPen(QPen(rahmen, 2 if self.isChecked() else 1))
        p.drawRect(r)
        p.save(); p.translate((self.width() - 130) / 2, 0); p.scale(0.5, 0.5)       # das Bildchen ist für 260 × 200 gezeichnet
        self._bildchen(p, dunkel)
        p.restore()
        p.setPen(pal.color(QPalette.Text) if self.isChecked() else pal.color(QPalette.PlaceholderText))
        p.drawText(QRectF(0, r.bottom() - 34, r.width(), 24), Qt.AlignCenter, self.text())
        if self.isChecked():                                           # Haken in der Ecke rechts unten
            ecke = QPainterPath()
            ecke.moveTo(r.right(), r.bottom() - 36); ecke.lineTo(r.right(), r.bottom()); ecke.lineTo(r.right() - 36, r.bottom())
            ecke.closeSubpath()
            p.fillPath(ecke, akzent)
            p.setPen(QPen(QColor(Farbe.WEISS), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawPolyline([QPointF(r.right() - 17, r.bottom() - 9), QPointF(r.right() - 12, r.bottom() - 5),
                            QPointF(r.right() - 5, r.bottom() - 13)])

    def _bildchen(self, p: QPainter, dunkel: bool) -> None:
        blatt = QColor(Farbe.WEISS) if not dunkel else QColor(BILDCHEN_BLATT_DUNKEL)
        linie = QColor(Farbe.GRAU_HELL)
        block = QColor(Farbe.AKZENT).lighter(170) if not dunkel else QColor(Farbe.AKZENT_DUNKEL).darker(130)
        p.setPen(QPen(QColor(Farbe.GRAU_HELL), 1))

        def seite(x: float, y: float, b: float, h: float, zeilen: int) -> None:
            p.setBrush(blatt)
            p.drawRoundedRect(QRectF(x, y, b, h), 3, 3)
            p.fillRect(QRectF(x + 7, y + 8, b * 0.18, b * 0.16), block)
            p.save(); p.setPen(QPen(linie, 1.4))
            p.drawLine(QPointF(x + 7 + b * 0.26, y + 12), QPointF(x + b - 8, y + 12))
            for k in range(zeilen):
                yy = y + 22 + k * ((h - 30) / max(1, zeilen))
                p.drawLine(QPointF(x + 7, yy), QPointF(x + b - 8, yy))
            p.restore()

        if not self.lang:
            for i, (x, y) in enumerate(((80, 28), (134, 28), (80, 92), (134, 92))):
                seite(x, y, 46, 56, 3)
        else:
            x, y, b, h = 88, 24, 82, 128
            p.setBrush(blatt)
            p.drawRoundedRect(QRectF(x, y, b, h), 3, 3)
            p.fillRect(QRectF(x + 10, y + 10, 20, 18), block)
            p.save(); p.setPen(QPen(linie, 1.4))
            for yy in (14, 22):
                p.drawLine(QPointF(x + 36, y + yy), QPointF(x + b - 10, y + yy))
            for yy in (38, 46, 62, 70, 78, 96, 104, 112):
                links = x + 30 if yy > 86 else x + 10                  # neben dem kleinen Bild unten links
                p.drawLine(QPointF(links, y + yy), QPointF(x + (b - 30 if 54 < yy < 86 else b - 10), y + yy))
            p.restore()
            p.fillRect(QRectF(x + b - 26, y + 54, 16, 24), QColor(Farbe.ORANGE).lighter(175) if not dunkel else QColor(BILDCHEN_AKZENT_DUNKEL))
            p.fillRect(QRectF(x + 10, y + 90, 14, 14), linie)


class BildExportAnsicht(QWidget):
    """Bildexport als Seite in der zweiten Spalte des Datei-Menüs."""

    def __init__(self, parent, startordner: str, dpi: int, exportieren: Callable[[BildWahl], list[str]], zurueck: Callable[[], None]):
        super().__init__(parent)
        self._exportieren_cb = exportieren
        self._zurueck = zurueck
        v = _spalte("fenster", self)
        titel = QLabel(_t("bild.als_bild_exportieren")); titel.setObjectName("bsTitel"); v.addWidget(titel)
        intro = QLabel(_t("bild.waehle_das_bildlayout_die_qualitaet_und"))
        intro.setWordWrap(True); intro.setObjectName("bsHinweis"); v.addWidget(intro)

        karten = FlussLayout(12)
        self.k_seite = _Karte(_t("bild.jede_seite"), False)
        self.k_lang = _Karte(_t("bild.langes_bild"), True)
        gruppe = QButtonGroup(self); gruppe.setExclusive(True)
        for k in (self.k_seite, self.k_lang):
            gruppe.addButton(k); karten.addWidget(k)
        self.k_seite.setChecked(True)
        v.addWidget(_abschnitt(_t("bild.1_bildlayout"), _t("bild.waehle_eine_bilddatei_pro_seite_oder_ein"), karten))

        g = FormularGitter()
        self.wasser = QLineEdit(); self.wasser.setPlaceholderText(_t("bild.zum_beispiel_vertraulich"))
        self.qualitaet = Auswahlfeld()
        for name, wert in QUALITAET:
            self.qualitaet.addItem(_t("bild.0_1_dpi").format(name, wert), wert)
        if dpi not in [d for _n, d in QUALITAET]:                  # die Auflösung aus den Optionen steht dann zuoberst
            self.qualitaet.insertItem(0, _t("bild.wie_in_den_optionen_0_dpi").format(dpi), dpi)
        self.qualitaet.setCurrentIndex(self.qualitaet.findData(dpi))
        self.format = Auswahlfeld()
        for name in FORMATE:
            self.format.addItem(name)
        self.format.setCurrentText("PNG")
        self.ordner = QLineEdit(startordner or _bilder_ordner())
        from lunivo_writer.oberflaeche.bauteile import symbole
        waehlen = self.ordner.addAction(symbole.icon("ellipsis", ICON_GROSS), QLineEdit.TrailingPosition)
        waehlen.setToolTip(_t("bild.ordner_waehlen"))
        waehlen.triggered.connect(self._ordner_waehlen)
        self.k_export = QPushButton(_t("bild.exportieren")); self.k_export.setObjectName("optFertig"); self.k_export.setDefault(True)
        self.k_export.setCursor(Qt.PointingHandCursor)
        self.k_export.clicked.connect(self._exportieren)
        self.wasser.setToolTip(_t("bild.optionaler_blasser_schriftzug_auf_jeder"))
        self.qualitaet.setToolTip(_t("bild.hoehere_aufloesung_ergibt_schaerfere_abe"))
        self.format.setToolTip(_t("bild.waehle_png_jpg_bmp_oder_tif"))
        for text, feld in (("&Wasserzeichen", self.wasser), ("&Qualität", self.qualitaet),
                           ("&Format", self.format), (_t("bild.speichern_in"), self.ordner)):
            g.reihe((text, feld))
        for feld in (self.wasser, self.ordner):                       # Textfelder; die Auswahlfelder behalten DROPDOWN_HOEHE
            feld.setMinimumHeight(FELDHOEHE)
        v.addWidget(_abschnitt(_t("bild.2_ausgabe_festlegen"), _t("bild.lege_wasserzeichen_bildqualitaet_dateifo"), g))
        self.k_export.setText(_t("bild.bilder_exportieren"))
        self.ordner.setAccessibleName(_t("bild.ordner_fuer_die_exportierten_bilder"))
        self.wasser.setAccessibleName(_t("bild.wasserzeichen_optional"))
        self.qualitaet.setAccessibleName(_t("bild.bildqualitaet"))
        self.format.setAccessibleName(_t("bild.bildformat"))
        self._wahl: BildWahl | None = None
        self._dateien: list[str] = []

        self.meldung = QLabel(); self.meldung.setWordWrap(True); self.meldung.setObjectName("bsHinweis"); self.meldung.hide()
        v.addWidget(self.meldung)
        aktionen = FlussLayout(8)
        self._datei_oeffnen = QPushButton(_t("bild.bild_oeffnen")); self._datei_oeffnen.setEnabled(False)
        self._ordner_oeffnen = QPushButton(_t("bild.ordner_oeffnen")); self._ordner_oeffnen.setEnabled(False)
        self._datei_oeffnen.hide(); self._ordner_oeffnen.hide()
        self._datei_oeffnen.clicked.connect(self._erstes_bild_oeffnen)
        self._ordner_oeffnen.clicked.connect(self._zielordner_oeffnen)
        aktionen.addWidget(self._datei_oeffnen); aktionen.addWidget(self._ordner_oeffnen)
        v.addLayout(aktionen)
        v.addStretch(1)
        fuss = FlussLayout(_A_MITTEL); raender(fuss, "oben")
        self.zurueck_knopf = _rolle(QPushButton(_t("bild.zurueck_zum_dokument")), "aktion"); self.zurueck_knopf.clicked.connect(self._zurueck)
        fuss.addWidget(self.zurueck_knopf); fuss.addWidget(self.k_export)
        v.addLayout(fuss)

    def _ordner_waehlen(self) -> None:
        from lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster import ordner_waehlen
        neu = ordner_waehlen(self, _t("bild.ordner_fuer_die_bilder"), self.ordner.text() or _bilder_ordner())
        if neu:
            self.ordner.setText(neu)

    def _exportieren(self) -> None:
        ordner = os.path.expanduser(self.ordner.text().strip())
        if not os.path.isdir(ordner):
            self.meldung.setText(_t("bild.der_gewaehlte_ordner_0_ist_nicht_vorhand").format(ordner))
            self.meldung.show(); self.ordner.setFocus()
            return
        self._wahl = BildWahl(lang=self.k_lang.isChecked(), wasserzeichen=self.wasser.text(), dpi=int(self.qualitaet.currentData()),
                              format=self.format.currentText(), ordner=ordner)
        self._dateien = []
        self._datei_oeffnen.setEnabled(False); self._datei_oeffnen.hide()
        self._ordner_oeffnen.setEnabled(False); self._ordner_oeffnen.hide()
        _rolle(self.meldung, "text")
        self.k_export.setEnabled(False); self.meldung.setText(_t("bild.bilder_werden_erstellt")); self.meldung.show()
        from PySide6.QtWidgets import QApplication
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            dateien = self._exportieren_cb(self._wahl)
        except OSError as e:
            self.meldung.setText(_t("bild.export_nicht_moeglich_0").format(e))
            _rolle(self.meldung, "fehler")
            self.ordner.setFocus()
            return
        finally:
            QApplication.restoreOverrideCursor()
            self.k_export.setEnabled(True)
        self._dateien = dateien
        if not dateien:
            self.meldung.setText(_t("bild.es_wurden_keine_seiten_zum_exportieren_g"))
            return
        _rolle(self.meldung, "text")
        self.meldung.setText(_t("bild.0_bild_1_gespeichert").format(len(dateien), 'er' if len(dateien) != 1 else ''))
        self.meldung.show()
        self._datei_oeffnen.setEnabled(True)
        self._ordner_oeffnen.setEnabled(True)
        self._datei_oeffnen.show(); self._ordner_oeffnen.show()

    def _erstes_bild_oeffnen(self) -> None:
        if self._dateien:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self._dateien[0]))

    def _zielordner_oeffnen(self) -> None:
        if self._dateien:
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(self._dateien[0])))


def _abschnitt(titel: str, hilfe: str, layout: QLayout) -> QWidget:
    w = QWidget(); v = _spalte("zeile", w)
    t = abschnittstitel(titel)
    h = QLabel(hilfe); h.setObjectName("bsHinweis"); h.setWordWrap(True)
    v.addWidget(t); v.addWidget(h); v.addLayout(layout)
    return w


def _bilder_ordner() -> str:
    return QStandardPaths.writableLocation(QStandardPaths.PicturesLocation) or os.path.expanduser("~")
