"""SmartArt-Auswahl nach der Vorlage (Foto „Grafik auswählen“): Reiter „Alle“, große Kacheln, darunter Vorschau mit Name und Beschreibung, ein blauer OK-Knopf.

``SmartArtDialogFoto`` ist ``SmartArtDialog`` (``einfuegen_dialoge.py``, bleibt unverändert; er dient weiter dem Bearbeiten) mit anderer Anordnung für das Einfügen.
Die Kacheln sind 126 x 76 px (Foto: etwa 130 x 78): in der Seitenleiste bei 300 px stehen zwei nebeneinander, die Spaltenzahl folgt der Breite.
"""
from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QVBoxLayout

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.basis.dialog_rahmen import knopfzeile
from lunivo_writer.ui.baukasten.controls.flache_reiter_leiste import HAUPT, FlacheReiterLeiste
from lunivo_writer.ui.dialogs.einfuegen_dialoge import SmartArtDialog, _layout_bildchen, _LayoutGalerie
from lunivo_writer.ui.baukasten.basis.mass import GROESSE_KACHEL_FOTO

KACHEL_B, KACHEL_H = GROESSE_KACHEL_FOTO                      # Außenmaß einer Kachel (Foto etwa 130 x 78)
ABSTAND = 4


def _weg(w) -> None:
    w.hide(); w.setParent(None); w.deleteLater()


class _GrosseGalerie(_LayoutGalerie):
    """Die Layout-Galerie mit Kacheln im Seitenverhältnis des Fotos."""

    def __init__(self, namen, zeichner, aktuell):
        super().__init__(namen, zeichner, aktuell)
        self._bauen(2)                                # Start schmal (Seitenleiste 300 px); breiter wird beim Anpassen der Breite

    def _bauen(self, spalten: int) -> None:
        from lunivo_writer.ui.baukasten.controls.kachel_feld import KachelFeld
        if self.feld is not None:
            self._v.removeWidget(self.feld); _weg(self.feld)
        self._spalten = spalten
        self.feld = KachelFeld(spalten=spalten, groesse=QSize(KACHEL_B - 10, KACHEL_H - 10), mit_text=False)
        for n in self._namen:
            self.feld.hinzu(n, n, lambda p, r, n=n: self._zeichner(p, r, n))
            k = self.feld.knoepfe[n]
            k.setAccessibleName(n); k.setFixedSize(KACHEL_B, KACHEL_H)
            k.setProperty("kachel", True)
        self.feld.gewaehlt.connect(self._klick)
        self.feld.setze(self._aktuell)
        self._v.addWidget(self.feld)
        self.updateGeometry()

    def resizeEvent(self, ev) -> None:
        super(_LayoutGalerie, self).resizeEvent(ev)
        s = max(1, min(len(self._namen), (self.width() + ABSTAND) // (KACHEL_B + ABSTAND)))
        if s != self._spalten:
            self._bauen(s)


class SmartArtDialogFoto(SmartArtDialog):
    def __init__(self, parent, daten: dict | None = None):
        super().__init__(parent, daten)
        v: QVBoxLayout = self.layout()
        # Reiter „Alle“ statt der Überschrift „Layout“
        titel = v.itemAt(0).widget()
        self.reiter = FlacheReiterLeiste(HAUPT); self.reiter.addTab("Alle")
        v.replaceWidget(titel, self.reiter); _weg(titel)
        # große Kacheln statt der kleinen
        alt = self.galerie
        self.galerie = _GrosseGalerie([e["schluessel"] for e in self.SA.LAYOUT_KATALOG], _layout_bildchen, alt.aktuell())
        v.replaceWidget(alt, self.galerie); _weg(alt)
        self.galerie.gewaehlt.connect(self._layout)
        # Reihenfolge wie im Foto: Vorschau, darunter Name und Beschreibung
        for w in (self.name, self.beschreibung):
            v.removeWidget(w)
        v.insertWidget(v.indexOf(self.bearbeiten), self.name); v.insertWidget(v.indexOf(self.bearbeiten), self.beschreibung)
        v.insertWidget(v.indexOf(self.name), self.vorschau)
        # nur der blaue OK-Knopf
        alt_ok = v.itemAt(v.count() - 1).widget()
        v.removeWidget(alt_ok); _weg(alt_ok)
        self.knoepfe = knopfzeile(self, nur_ok=True)
        self.knoepfe.ok.setProperty("hervorgehoben", True)
        v.addWidget(self.knoepfe)
        self.aktualisieren()
