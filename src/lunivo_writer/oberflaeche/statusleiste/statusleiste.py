"""Statusleiste: Meldung, Wörter/Zeichen, Seite, Zoom (− Regler + Anzeige)."""
from __future__ import annotations

from lunivo_writer.oberflaeche.baukasten.basis.darstellung import eigenschaft

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QSlider, QStatusBar
from lunivo_writer.oberflaeche.baukasten.bausteine.knopf.knopf import knopf, werkzeugknopf
from lunivo_writer.oberflaeche.baukasten.basis.mass import BREITE_ZOOM_REGLER, RAND_STATUSLEISTE


class StatusBar(QStatusBar):
    zoom_kleiner = Signal()
    zoom_groesser = Signal()
    zoom_stufe = Signal()
    zoom_geaendert = Signal(int)          # Prozent, vom Regler
    thema_wechseln = Signal()             # Hell ↔ Dunkel
    lesemodus_beenden = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizeGripEnabled(True)
        self.lbl_msg = QLabel("")
        self.addWidget(self.lbl_msg, 1)
        self.lesen_ende = knopf("leseende", "Lesemodus beenden", tooltip="Zurück zum Bearbeiten (Strg+Umschalt+L)", name="Lesemodus beenden", hand=True,
                                aktion=self.lesemodus_beenden.emit)
        self.lesen_ende.hide()
        eigenschaft(self.lesen_ende, rolle="lese_ende_status")
        self.addPermanentWidget(self.lesen_ende)
        self.lbl_words = QLabel("0 Wörter, 0 Zeichen")
        self.lbl_page = QLabel("Seite 1 von 1")
        for w in (self.lbl_words, self.lbl_page):
            w.setContentsMargins(*RAND_STATUSLEISTE)
            self.addPermanentWidget(w)
        self.thema = werkzeugknopf("thema", "Hell / Dunkel", tooltip="Zwischen hell und dunkel wechseln (Strg+Umschalt+D)",
                                   name="Zwischen hell und dunkel wechseln", aktion=self.thema_wechseln.emit)
        self.addPermanentWidget(self.thema)
        self.zoom_minus = werkzeugknopf("standard", symbol="minus", symbolgroesse="klein", tooltip="Verkleinern", aktion=self.zoom_kleiner.emit)
        self.zoom_plus = werkzeugknopf("standard", symbol="plus", symbolgroesse="klein", tooltip="Vergrößern", aktion=self.zoom_groesser.emit)
        self.zoom_regler = QSlider(Qt.Horizontal); self.zoom_regler.setRange(10, 500); self.zoom_regler.setValue(100); self.zoom_regler.setAccessibleName("Zoom")
        self.zoom_regler.setFixedWidth(BREITE_ZOOM_REGLER)
        self.lbl_zoom = werkzeugknopf("zoomanzeige", "100 %", tooltip="Zoom …", aktion=self.zoom_stufe.emit)
        self.zoom_regler.valueChanged.connect(self.zoom_geaendert)
        for w in (self.zoom_minus, self.zoom_regler, self.zoom_plus, self.lbl_zoom):
            self.addPermanentWidget(w)

    def thema_zeigen(self, dunkel: bool) -> None:
        self.thema.setText("Dunkel" if dunkel else "Hell")

    def meldung(self, text: str) -> None:
        self.lbl_msg.setText(text)

    def zaehler(self, woerter: int, zeichen: int) -> None:
        self.lbl_words.setText(f"{woerter} Wörter, {zeichen} Zeichen")

    def seite(self, aktuell: int | None, gesamt: int | None) -> None:
        self.lbl_page.setText("Seite – von –" if aktuell is None else f"Seite {aktuell} von {gesamt}")

    def zoom_zeigen(self, faktor: float) -> None:
        self.lbl_zoom.setText(f"{round(faktor * 100)} %")
        self.zoom_regler.blockSignals(True)
        self.zoom_regler.setValue(int(round(faktor * 100)))
        self.zoom_regler.blockSignals(False)
