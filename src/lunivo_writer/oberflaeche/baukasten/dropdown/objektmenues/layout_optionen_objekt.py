"""Das Popup „Layoutoptionen“ eines freien Objekts nach der Vorlage: ✕ im Kopf, größere Kacheln, beide Radios leer bei SmartArt.

    p = LayoutOptionenObjekt(parent, art, mit_text)
    p.verschieben_wahl = "mit_text" | "fest" | None            # None: keins gewählt (SmartArt); Werte aus ``editor/objekte/bildlayout.verschieben_wahl``

Baut auf ``LayoutOptionen`` (layout_optionen.py, unverändert) auf; Signale und Bedienung sind dieselben.
"""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QHBoxLayout, QToolButton

from lunivo_writer.oberflaeche.baukasten.felder.kachel_feld import KachelFeld
from lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.layout_optionen import LayoutOptionen
from lunivo_writer.oberflaeche.baukasten.medien.umbruch_symbole import umbruch_zeichner
from lunivo_writer.oberflaeche.baukasten.basis.mass import GROESSE_OBJEKTLAYOUT_KACHEL, GROESSE_SCHLIESSEN_KNOPF, RAND_KEIN

KACHEL = QSize(*GROESSE_OBJEKTLAYOUT_KACHEL)                                   # wie in der Vorlage (bei 300 px Breite: 3 Kacheln = rund 160 px)
UMBRUCH = (("quadrat", "Quadrat"), ("passend", "Passend"), ("transparent", "Transparent"), ("obenunten", "Oben und Unten"),
           ("hinter", "Hinter den Text"), ("vor", "Vor dem Text"))


class LayoutOptionenObjekt(LayoutOptionen):
    def __init__(self, parent=None, art: str = "textfluss", mit_text: bool = False):
        super().__init__(parent, art, mit_text)
        self._kopf_mit_schliessen()
        self._kacheln_gross()
        self.layout().setAlignment(self.zeile, Qt.AlignLeft)
        self._gruppe = self.r_mit.group()
        for r in (self.r_mit, self.r_fest):
            r.toggled.connect(lambda an, g=self._gruppe: an and g.setExclusive(True))       # nach der ersten Wahl wieder „genau eins“
        self.setze(art)

    # ---- Kopf mit ✕ ----------------------------------------------------------------------------------------------------------
    def _kopf_mit_schliessen(self) -> None:
        v = self.layout()
        kopf = v.itemAt(0).widget()
        v.removeWidget(kopf)
        x = QToolButton(); x.setText("✕"); x.setAutoRaise(True); x.setCursor(Qt.PointingHandCursor); x.setToolTip("Schließen")
        x.setAccessibleName("Schließen"); x.setFixedSize(*GROESSE_SCHLIESSEN_KNOPF); x.clicked.connect(self.close)
        reihe = QHBoxLayout(); reihe.setContentsMargins(*RAND_KEIN)
        reihe.addWidget(kopf, 1); reihe.addWidget(x)
        v.insertLayout(0, reihe)

    # ---- größere Kacheln -----------------------------------------------------------------------------------------------------
    def _kacheln_gross(self) -> None:
        v = self.layout()
        alt_zeile, alt_umbruch = self.zeile, self.umbruch
        self.zeile = KachelFeld(spalten=1, groesse=KACHEL, mit_text=False)
        self.zeile.hinzu("textfluss", "Im Textfluss", umbruch_zeichner("textfluss"))
        self.umbruch = KachelFeld(spalten=3, groesse=KACHEL, mit_text=False)
        for schl, text in UMBRUCH:
            self.umbruch.hinzu(schl, text, umbruch_zeichner(schl))
        for alt, neu in ((alt_zeile, self.zeile), (alt_umbruch, self.umbruch)):
            v.replaceWidget(alt, neu); alt.hide(); alt.deleteLater()
            neu.gewaehlt.connect(self._klick)

    # ---- Vorwahl der Radios --------------------------------------------------------------------------------------------------
    @property
    def verschieben_wahl(self) -> str | None:
        return "mit_text" if self.r_mit.isChecked() else "fest" if self.r_fest.isChecked() else None

    @verschieben_wahl.setter
    def verschieben_wahl(self, wahl: str | None) -> None:
        for r in (self.r_mit, self.r_fest):
            r.blockSignals(True)
        if wahl is None:
            self._gruppe.setExclusive(False)
            self.r_mit.setChecked(False); self.r_fest.setChecked(False)
        else:
            self._gruppe.setExclusive(True)
            (self.r_mit if wahl == "mit_text" else self.r_fest).setChecked(True)
        for r in (self.r_mit, self.r_fest):
            r.blockSignals(False)
