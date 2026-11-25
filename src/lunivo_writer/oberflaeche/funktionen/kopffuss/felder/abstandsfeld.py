"""Höhenfeld „Kopfzeilenhöhe“ / „Fußzeilenhöhe“ im Band: Abstand des Kopf- oder Fußbereichs zum Blattrand. Nur Darstellung; Werte kommen vom Framework."""
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QLocale, QSize
from PySide6.QtWidgets import QLabel, QToolButton, QWidget

from lunivo_writer.oberflaeche.baukasten.basis.darstellung import zahlfeld_ohne_pfeilknoepfe
from lunivo_writer.oberflaeche.baukasten.basis.mass import BREITE_ZAHLFELD_BAND, GROESSE_ZAHLFELD_KNOPF, HOEHE_ZAHLFELD_BAND, ICON_ZAHLFELD
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FlussLayout
from lunivo_writer.oberflaeche.baukasten.felder.schiebe_feld import SchrittFeld
from lunivo_writer.oberflaeche.bauteile import symbole


class _Zeile(QWidget):
    neu_laden = None

    def showEvent(self, ev):                       # beim Einblenden den aktuellen Wert des Abschnitts holen
        if self.neu_laden:
            self.neu_laden()
        super().showEvent(ev)


def abstandsfeld(name: str, symbol: str, lesen: Callable[[], float | None], schreiben: Callable[[float], None]) -> QWidget:
    """``lesen`` liefert den Wert in mm (``None``: kein Dokument), ``schreiben`` übergibt eine Änderung an das Framework."""
    host = _Zeile()
    h = FlussLayout(6)
    host.setLayout(h)
    h.setContentsMargins(0, 0, 0, 0)
    bild = QLabel()
    bild.setPixmap(symbole.icon(symbol, ICON_ZAHLFELD).pixmap(QSize(ICON_ZAHLFELD, ICON_ZAHLFELD)))
    h.addWidget(bild)
    h.addWidget(QLabel(name + ":"))
    f = SchrittFeld(0.0, 100.0, " mm", 0.5, 1)
    f.feld.setLocale(QLocale(QLocale.German, QLocale.Germany))
    f.feld.setButtonSymbols(f.feld.ButtonSymbols.UpDownArrows)       # „NoButtons“ lässt im Thema kein Textfeld übrig
    f.feld.setMinimumWidth(BREITE_ZAHLFELD_BAND)
    zahlfeld_ohne_pfeilknoepfe(f.feld)
    f.feld.setAccessibleName(name)
    f.setToolTip(name)
    for k in f.findChildren(QToolButton):
        k.setFixedSize(*GROESSE_ZAHLFELD_KNOPF)
    f.feld.setFixedHeight(HOEHE_ZAHLFELD_BAND)
    h.addWidget(f)

    def laden():
        wert = lesen()
        if wert is not None:
            f.feld.blockSignals(True)
            f.setValue(wert)
            f.feld.blockSignals(False)

    laden()
    host.neu_laden = laden
    f.valueChanged.connect(schreiben)
    host.feld = f
    return host
