"""Schnellzugriffsleiste und schnelle KI-Aktionen des Menübands."""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QToolButton

from lunivo_writer.oberflaeche.bauteile import symbole
from lunivo_writer.oberflaeche.baukasten.bausteine.knopf.knopf import werkzeugknopf
from lunivo_writer.oberflaeche.baukasten.basis.mass import ICON_GROSS, ICON_MITTEL
from lunivo_writer.oberflaeche.baukasten.thema.thema import kopf_symbolfarbe
from lunivo_writer.oberflaeche.band.band_bausteine import _mit_kuerzel


class BandSchnellzugriffBaustein:
    """Baut die Schnellzugriffsleiste und ihre KI-Aktionsknöpfe."""

    SCHNELL = [("oeffnen", "Öffnen", "oeffnen"), ("vorlage", "Neu aus Vorlage", "neuAusVorlage"), ("speichern", "Speichern", "speichern"),
               ("pdf", "Als PDF exportieren", "speichernPdf"), ("drucken", "Drucken", "drucken"),
               ("vorschau", "Druckvorschau", "vorschau"), ("zurueck", "Rückgängig", "rueckgaengig"),
               ("vor", "Wiederholen", "wiederholen")]

    SCHNELL_ALLE = SCHNELL + [("drucker2", "Drucker auswählen", "druckerWaehlen"), ("neu", "Neu", "neu"), ("unter", "Speichern unter", "speichernUnter"), ("kleben", "Einfügen", "einfuegen"),
                              ("schere", "Ausschneiden", "ausschneiden"), ("kopie", "Kopieren", "kopieren"),
                              ("lupe", "Suchen und Ersetzen", "suchen"), ("haken", "Prüfen", "rechtschreibung"),
                              ("umbruch", "Seitenumbruch", "seitenumbruch"), ("bild", "Bild", "bild"), ("kette", "Hyperlink", "hyperlink"),
                              ("notiz", "Neuer Kommentar", "kommentar"), ("verfolgt", "Änderungen verfolgen", "verfolgen"),
                              ("F", "Fett", "fett"), ("K", "Kursiv", "kursiv")]

    def _tausch_rechtsklick(self, k: QToolButton, sym: str) -> None:
        """Rechtsklick auf einen Knopf: Fenster „Symbol austauschen“ mit der Zeichnung dieses Knopfes."""
        if not symbole.hat(sym):
            return
        k.setContextMenuPolicy(Qt.CustomContextMenu)
        k.customContextMenuRequested.connect(lambda _p, s=sym: self.b.symbolTauschen(None, s))

    def _schnellzugriff(self):
        liste = self.SCHNELL if self._schnell_wahl is None else [e for e in self.SCHNELL_ALLE if e[2] in self._schnell_wahl]
        for sym, name, aktion in liste:
            k = werkzeugknopf("standard", symbol=sym, symbolgroesse="mittel", symbolfarbe=kopf_symbolfarbe(), symbol_einpassen=True,
                              tooltip=_mit_kuerzel(name), aktion=lambda a=aktion: self.b.tun(a))
            self._tausch_rechtsklick(k, sym)
            self.schnell.addWidget(k)
            self.knoepfe.append((k, aktion, sym in ("speichern", "pdf", "drucken", "vorschau", "zurueck", "vor")))

    def ki_schnell(self, aktionen: list, ausfuehren) -> None:
        """„Schnelle KI-Aktionen“ mit Zugriff „Schnellzugriff“: je ein Knopf hinter den übrigen der Schnellzugriffsleiste."""
        for k in getattr(self, "_ki_schnell_knoepfe", []):
            self.schnell.removeWidget(k); k.hide(); k.setParent(None); k.deleteLater()
        self._ki_schnell_knoepfe = []
        for a in aktionen:
            k = werkzeugknopf("standard", symbol="assistent", symbolgroesse="mittel", symbolfarbe=kopf_symbolfarbe(), symbol_einpassen=True,
                              tooltip="KI: " + a["name"], aktion=lambda a=a: ausfuehren(a))
            self.schnell.addWidget(k)
            self._ki_schnell_knoepfe.append(k)
