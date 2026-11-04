"""Dropdowns in den Köpfen von „TEXTFÜLLUNG“ und „TEXTKONTUR“ der Textoptionen des Diagramms (Vorlage): Mixin vor ``TexteffektPanel``/``_TextPanel``.

Die Basis (``texteffekt_dialog.py``) bleibt unverändert: ``_text_kopf_bauen()`` blendet deren Kopfwidgets (``fuell_farbe_kopf``, ``linie_knopf``) aus und hängt je ein
``KopfDropdown`` in den Kopf von ``a_fuell`` und ``a_kontur``. Die Wahl im Popup ruft die vorhandenen Slots des Panels (``_kopffarbe``, ``_kopf_verlauf``,
``_linie_gewaehlt``); das Feld zeigt das Ergebnis und wird in ``_neu`` und ``_setze_fuellung`` nachgeführt.

Schlüssel der Füllung: ``farbe:#hex``, ``graduell:#hex``, ``""`` = keine; der Linie ``art|form|breite_pt``, ``""`` = keine (Arten: ``texteffekt.KONTUR_ARTEN``).
Automatische Textfarbe (leer) zeigt das Feld schwarz wie in der Vorlage.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap

from lunivo_writer.core.farben import Farbe
from lunivo_writer.editor import texteffekt as T
from lunivo_writer.ui.baukasten.fuell_voreinstellungen import FuellPalette, fuell_bild
from lunivo_writer.ui.baukasten.farbpalette import FarbPalette
from lunivo_writer.ui.baukasten.kopf_dropdown import KopfDropdown
from lunivo_writer.ui.baukasten.linien_voreinstellungen import linien_bild, linien_menue, linien_schluessel


def text_fuell_menue(parent=None, aktuell: str = "") -> FarbPalette:
    """„Keine Füllung“, die Farbpalette und graduelle Füllung (Muster und Struktur gibt es beim Text nicht)."""
    return FuellPalette(parent, aktuell, keine_text="Keine Füllung", verlauf=True, titel="Textfüllung")


def _text_bild(text: str, groesse) -> QPixmap:
    pm = QPixmap(groesse); pm.fill(Qt.transparent)
    p = QPainter(pm); p.setPen(QColor("#212529")); p.drawText(pm.rect(), Qt.AlignCenter, text); p.end()
    return pm


class TextKopfMenueMixin:
    def _text_kopf_bauen(self) -> None:
        self.fuell_farbe_kopf.hide(); self.linie_knopf.hide()
        arten = {k: v[0] for k, v in T.KONTUR_ARTEN.items()}
        self.kopf_fuell = KopfDropdown(lambda p: text_fuell_menue(p, self._text_fuell_schluessel()))
        self.kopf_fuell.gewaehlt.connect(self._text_fuell_wahl); self.kopf_fuell.an(self.a_fuell)
        self.kopf_fuell.setAccessibleName("Textfüllung wählen"); self.kopf_fuell.setToolTip("Textfüllung wählen")
        self.kopf_linie = KopfDropdown(lambda p: linien_menue(p, self._text_linien_schluessel(), arten))
        self.kopf_linie.gewaehlt.connect(self._linie_gewaehlt); self.kopf_linie.an(self.a_kontur)
        self.kopf_linie.setAccessibleName("Textkontur wählen"); self.kopf_linie.setToolTip("Textkontur wählen")
        self._text_kopf_aktualisieren()

    def _text_fuell_wahl(self, schluessel: str) -> None:
        art, _, wert = schluessel.partition(":")
        if art == "graduell":
            self._kopf_verlauf(wert)
        else:
            self._kopffarbe(wert)                      # "" = keine Füllung

    def _text_fuell_schluessel(self) -> str:
        if self.r_keine.isChecked():
            return ""
        if self.r_verlauf.isChecked():
            return f"graduell:{QColor(self.v1.farbe).name()}" if self.v1.farbe else ""
        return f"farbe:{QColor(self.farbe.farbe or Farbe.SCHWARZ).name()}"

    def _text_linien_schluessel(self) -> str:
        if not self.k_linie.isChecked():
            return ""
        return linien_schluessel(self.k_art.currentData(), self.k_form.currentData(), self.k_breite.value())

    def _text_kopf_aktualisieren(self) -> None:
        if not getattr(self, "kopf_fuell", None) or not hasattr(self, "k_breite"):
            return
        if self.r_keine.isChecked():
            spec = {"art": "keine"}
        elif self.r_verlauf.isChecked():
            spec = {"art": "graduell", "dunkel": self.v1.farbe, "hell": self.v2.farbe}
        else:
            spec = {"art": "farbe", "farbe": self.farbe.farbe or Farbe.SCHWARZ}
        self.kopf_fuell.setSymbol(QIcon(fuell_bild(spec, KopfDropdown.SYMBOL)))
        if self.k_keine.isChecked():
            self.kopf_linie.setSymbol(QIcon(_text_bild("Keine", KopfDropdown.SYMBOL)))
        else:
            farbe = (self.kv1.farbe if self.k_verlauf.isChecked() else self.k_farbe.farbe) or Farbe.SCHWARZ
            self.kopf_linie.setSymbol(QIcon(linien_bild({"art": self.k_art.currentData(), "form": self.k_form.currentData(),
                                                         "breite": self.k_breite.value(), "farbe": farbe}, KopfDropdown.SYMBOL)))

    def _neu(self, *a) -> None:
        super()._neu(*a)
        self._text_kopf_aktualisieren()

    def _setze_fuellung(self, w: dict) -> None:
        super()._setze_fuellung(w)
        self._text_kopf_aktualisieren()
