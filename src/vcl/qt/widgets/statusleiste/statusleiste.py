"""Statusleiste: Meldung, Wörter/Zeichen, Seite; rechts Ansichtswahl, Einpassen, Zoom (Anzeige mit Klappe, − Regler +) und Vollbild.

Die Ansichtsknöpfe stehen in ``ansichtswahl.py``, die Zoom-Klappe in ``zoomklappe.py``; diese Datei setzt die Leiste zusammen."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.farben.darstellung import eigenschaft

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QSlider, QStatusBar, QToolButton
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf, werkzeugknopf
from vcl.qt.widgets.bausteine.abstaende.mass import BREITE_ZOOM_REGLER, RAND_STATUSLEISTE
from vcl.qt.widgets.statusleiste.ansichtswahl import Ansichtswahl
from vcl.qt.widgets.statusleiste.zoomklappe import ZoomKlappe
from writer.funktionen.ansicht import ZOOM_PROZENT_MAX, ZOOM_PROZENT_MIN


class StatusBar(QStatusBar):
    zoom_kleiner = Signal()
    zoom_groesser = Signal()
    zoom_geaendert = Signal(int)          # Prozent, vom Regler oder aus der Zoom-Klappe
    zoom_breite = Signal()                # Einpassen und Zoom-Klappe: Seitenbreite
    zoom_text = Signal()                  # Zoom-Klappe: Textbreite
    zoom_seite = Signal()                 # Zoom-Klappe: ganze Seite
    augenschutz_umschalten = Signal()
    ansicht_gewaehlt = Signal(str)        # Kennung der Dokumentansicht (blatt, gliederung, lesen, web)
    vollbild_umschalten = Signal()
    thema_wechseln = Signal()             # Hell ↔ Dunkel
    lesemodus_beenden = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizeGripEnabled(True)
        self.lbl_words = QLabel("0 Wörter, 0 Zeichen")
        self.lbl_page = QLabel("Seite 1 von 1")
        for w in (self.lbl_words, self.lbl_page):                 # links: was zum Dokument gehört; rechts: Design, Ansicht und Zoom
            w.setContentsMargins(*RAND_STATUSLEISTE)
            self.addWidget(w)
        self.lbl_msg = QLabel("")
        self.addWidget(self.lbl_msg, 1)
        self.lesen_ende = knopf("leseende", "Lesemodus beenden", tooltip="Zurück zum Bearbeiten (Strg+Umschalt+L)", name="Lesemodus beenden", hand=True,
                                aktion=self.lesemodus_beenden.emit)
        self.lesen_ende.hide()
        eigenschaft(self.lesen_ende, rolle="lese_ende_status")
        self.addPermanentWidget(self.lesen_ende)
        self.thema = werkzeugknopf("thema", "Hell / Dunkel", tooltip="Zwischen hell und dunkel wechseln (Strg+Umschalt+D)",
                                   name="Zwischen hell und dunkel wechseln", aktion=self.thema_wechseln.emit)
        self.addPermanentWidget(self.thema)
        self.augenschutz = werkzeugknopf("standard", symbol="augenschutz", tooltip="Augenschutzmodus: das Blatt in sanftem Grün", name="Augenschutzmodus",
                                         umschaltbar=True, symbol_merken=True, aktion=self.augenschutz_umschalten.emit)
        self.ansichten = Ansichtswahl(self)
        self.ansichten.gewaehlt.connect(self.ansicht_gewaehlt)
        self.einpassen = werkzeugknopf("standard", symbol="einpassen", tooltip="Seite an das Fenster anpassen: die Seite füllt die Breite des Dokumentbereichs",
                                       name="Seite an das Fenster anpassen", symbol_merken=True, aktion=self.zoom_breite.emit)
        self.zoom_klappe = ZoomKlappe(self)
        self.zoom_klappe.prozent_gewaehlt.connect(self.zoom_geaendert)
        self.zoom_klappe.breite_gewaehlt.connect(self.zoom_breite)
        self.zoom_klappe.text_gewaehlt.connect(self.zoom_text)
        self.zoom_klappe.seite_gewaehlt.connect(self.zoom_seite)
        self.lbl_zoom = werkzeugknopf("zoomanzeige", "100 %", tooltip="Zoomfaktor wählen", name="Zoomfaktor")
        self.lbl_zoom.setMenu(self.zoom_klappe)
        self.lbl_zoom.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.zoom_minus = werkzeugknopf("standard", symbol="minus", symbolgroesse="klein", tooltip="Verkleinern", aktion=self.zoom_kleiner.emit)
        self.zoom_plus = werkzeugknopf("standard", symbol="plus", symbolgroesse="klein", tooltip="Vergrößern", aktion=self.zoom_groesser.emit)
        self.zoom_regler = QSlider(Qt.Horizontal); self.zoom_regler.setRange(ZOOM_PROZENT_MIN, ZOOM_PROZENT_MAX); self.zoom_regler.setValue(100)
        self.zoom_regler.setAccessibleName("Zoom")
        self.zoom_regler.setFixedWidth(BREITE_ZOOM_REGLER)
        self.zoom_regler.valueChanged.connect(self.zoom_geaendert)
        self.vollbild = werkzeugknopf("standard", symbol="vollbild", tooltip="Vollbild (F11)", name="Vollbild", umschaltbar=True, symbol_merken=True,
                                      aktion=self.vollbild_umschalten.emit)
        for w in (self.augenschutz, *self.ansichten.knoepfe.values(), self.einpassen, self.lbl_zoom, self.zoom_minus, self.zoom_regler, self.zoom_plus, self.vollbild):
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
        prozent = int(round(faktor * 100))
        self.lbl_zoom.setText(f"{prozent} %")
        self.zoom_regler.blockSignals(True)
        self.zoom_regler.setValue(prozent)
        self.zoom_regler.blockSignals(False)
        self.zoom_klappe.zeigen(prozent)

    def ansicht_zeigen(self, kennung: str, vollbild: bool, augenschutz: bool) -> None:
        """Zeigt die geltende Dokumentansicht, den Vollbild-Zustand und den Augenschutz an den Knöpfen, ohne eine Aktion auszulösen."""
        self.ansichten.zeigen(kennung)
        self.vollbild.setChecked(vollbild)
        self.augenschutz.setChecked(augenschutz)
