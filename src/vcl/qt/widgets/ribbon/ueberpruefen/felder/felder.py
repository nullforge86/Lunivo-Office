"""Feld „Anzeige zur Überprüfung“ im Reiter: die Auswahl der Fassung und darunter das Markup-Menü."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QWidget

from writer.anbindung.ueberpruefen_anzeige import anzeigen as anzeige_namen
from vcl.qt.widgets.bausteine.abstaende.mass import DROPDOWN_BREITE_MIN
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.menues.dropdown.dropdown_knopf import DropdownKnopf
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte


class UeberpruefenFelder:
    def feld_anzeige(self):
        """Die Auswahl über „Markup anzeigen“ wie in der Vorlage: die Fassung, darunter das Markup-Menü."""
        halter = QWidget()
        v = spalte("bandhalter", halter)
        cb = Auswahlfeld(popup_min=DROPDOWN_BREITE_MIN); cb.addItems(list(anzeige_namen())); cb.rolle("anzeige", "band", mindest=True)   # schmal im Band, die Liste zeigt die Namen
        cb.setAccessibleName("Anzeige zur Überprüfung"); cb.setToolTip("Anzeige zur Überprüfung")
        modell = cb.model()
        if isinstance(modell, QStandardItemModel):
            it = modell.item(2)
            it.setEnabled(False); it.setToolTip("Lunivo zeigt das Original ohne Markup; mit Markup kommt noch.")
        cb.activated.connect(lambda i: (self.ueberpruefenAnzeige(None, i), self.w.band.aktualisieren()))
        markup = DropdownKnopf(); markup.setAutoRaise(True); markup.setText("Markup anzeigen"); markup.setToolTip("Markup anzeigen")
        markup.setIcon(self._sym("markupzeigen")); markup.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        markup.band_zeile()
        menue = self.menue_markupKlappe()
        markup.menue_setzen(menue, geteilt=False, besitzen=True)
        v.addWidget(cb); v.addWidget(markup, 0, Qt.AlignLeft); v.addStretch(1)
        halter.anzeige, halter.markup = cb, markup

        def auffrischen():
            cb.blockSignals(True); cb.setCurrentIndex(self._anzeige_index()); cb.blockSignals(False)
            cb.setEnabled(self.ed is not None); markup.setEnabled(self.ed is not None)
        halter.auffrischen = auffrischen
        auffrischen()
        return halter
