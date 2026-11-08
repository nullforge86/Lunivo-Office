"""Statusleiste: Meldung, Wörter/Zeichen, Seite, Zoom (− Regler + Anzeige)."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QSlider, QStatusBar, QToolButton
from lunivo_writer.ui.widgets import icons
from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.basis.mass import (
    BREITE_ZOOMANZEIGE,
    BREITE_ZOOM_REGLER,
    HOEHE_LESEENDE_KNOPF,
    HOEHE_THEMAKNOPF,
    ICON_KLEIN,
    PADDING_LESEENDE_STATUS,
    RADIUS_FELD,
    RAND_STATUSLEISTE,
)


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
        self.lesen_ende = QPushButton("Lesemodus beenden"); self.lesen_ende.setMinimumHeight(HOEHE_LESEENDE_KNOPF); self.lesen_ende.setCursor(Qt.PointingHandCursor)
        self.lesen_ende.setToolTip("Zurück zum Bearbeiten (Strg+Umschalt+L)"); self.lesen_ende.hide()
        self.lesen_ende.setStyleSheet("QPushButton { background: palette(highlight); color: palette(highlighted-text); border: none; "
                                      "border-radius: " f"{RADIUS_FELD}" "px; padding: " f"{PADDING_LESEENDE_STATUS}" "; font-weight: bold; }"
                                      "QPushButton:hover { background: palette(link); color: %s; }" % Farbe.SCHWARZ)
        self.lesen_ende.clicked.connect(self.lesemodus_beenden)
        self.addPermanentWidget(self.lesen_ende)
        self.lbl_words = QLabel("0 Wörter, 0 Zeichen")
        self.lbl_page = QLabel("Seite 1 von 1")
        for w in (self.lbl_words, self.lbl_page):
            w.setContentsMargins(*RAND_STATUSLEISTE)
            self.addPermanentWidget(w)
        self.thema = QToolButton(); self.thema.setAutoRaise(True); self.thema.setMinimumHeight(HOEHE_THEMAKNOPF)
        self.thema.setText("Hell / Dunkel"); self.thema.setToolTip("Zwischen hell und dunkel wechseln (Strg+Umschalt+D)")
        self.thema.setAccessibleName("Zwischen hell und dunkel wechseln")
        self.thema.clicked.connect(self.thema_wechseln)
        self.addPermanentWidget(self.thema)
        self.zoom_minus = QToolButton(); self.zoom_minus.setIcon(icons.icon("minus", ICON_KLEIN)); self.zoom_minus.setAutoRaise(True); self.zoom_minus.setToolTip("Verkleinern")
        self.zoom_plus = QToolButton(); self.zoom_plus.setIcon(icons.icon("plus", ICON_KLEIN)); self.zoom_plus.setAutoRaise(True); self.zoom_plus.setToolTip("Vergrößern")
        self.zoom_regler = QSlider(Qt.Horizontal); self.zoom_regler.setRange(10, 500); self.zoom_regler.setValue(100); self.zoom_regler.setAccessibleName("Zoom")
        self.zoom_regler.setFixedWidth(BREITE_ZOOM_REGLER)
        self.lbl_zoom = QToolButton(); self.lbl_zoom.setText("100 %"); self.lbl_zoom.setAutoRaise(True)
        self.lbl_zoom.setToolTip("Zoom …"); self.lbl_zoom.setMinimumWidth(BREITE_ZOOMANZEIGE)
        self.zoom_minus.clicked.connect(self.zoom_kleiner)
        self.zoom_plus.clicked.connect(self.zoom_groesser)
        self.lbl_zoom.clicked.connect(self.zoom_stufe)
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
