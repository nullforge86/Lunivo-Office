"""Farb palette: aus ``vcl.qt.widgets.menues.dropdown.auswahl.farbpalette`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import QLabel, QLayout, QWidget
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil
from vcl.qt.widgets.bausteine.farben import farben as F
from vcl.qt.widgets.bausteine.interaktion.felder.karten_raster import kachel_gitter
from framework.schnittstellen.datentypen.farben import Farbe
from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
from vcl.qt.widgets.bausteine.abstaende.mass import SCHRIFT_GRUPPENTITEL_PX, ABSTAND_ENG, ICON_KLEIN, PADDING_PALETTE_TITEL_OBEN
from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
from vcl.qt.widgets.menues.dropdown.auswahl.farbpalette_hilfen import _BildKachel, _Kachel, _VerlaufKachel


def weitere_farben_unter(parent, fertig, start=None, titel: str = "Farbe") -> None:
    """Wie ``weitere_farben``, aber als Unterfenster: Liegt ``parent`` in einem ``FensterStapel``, öffnet sich „Farben“ als Seite im selben Fenster;
    ``fertig(farbe)`` läuft nach „OK“ (sonst öffnet sich das Fenster wie bisher)."""
    from vcl.qt.widgets.bausteine.interaktion.felder.farben_dialog import FarbenDialog
    from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import zeige_unter
    d = FarbenDialog(parent, start, titel)

    def ok() -> None:
        c = d.farbe()
        F.zuletzt_merken(c.name())
        fertig(c)
    zeige_unter(parent, d, ok)


class FarbPalette(MenueListe):
    """Popup mit „Keine Farbe“, Themenfarben (Grundfarben + Abstufungen), Standardfarben, zuletzt Benutzten, „Weitere Farben …“."""

    gewaehlt = Signal(object)        # QColor — oder None für „Keine Farbe“
    ueberfahren = Signal(object)     # QColor unter der Maus (für Live-Vorschau)
    verlassen = Signal()
    verlauf_gewaehlt = Signal(object)  # QColor: die Farbe der gewählten „Graduellen Füllung“ (nur mit ``verlauf=True``)
    reihe_gewaehlt = Signal(str)       # Schlüssel einer Kachel aus ``reihen`` (z. B. „muster:pct20“)

    def __init__(self, parent=None, *, keine_text: str | None = "Keine Farbe", start=None, titel: str = "Farbe",
                 zuletzt: bool = True, weitere: bool = True, verlauf: bool = False, verlauf_titel: str = "Graduelle Füllung",
                 weitere_text: str = "Weitere Farben …", automatisch: str | None = None,
                 pipette: bool = True, standard: bool = True, reihen: list[tuple[str, list[tuple[str, QPixmap, str]]]] | None = None):
        super().__init__(parent)
        self._start, self._titel = start, titel
        wid = QWidget()
        v = _spalte("panel", wid)
        if keine_text:
            keine = knopf("standard", keine_text, ohne_rand=True); keine.setProperty("listenzeile", True)
            keine.setIcon(self._keine_symbol()); keine.clicked.connect(lambda: self.waehle(None))
            v.addWidget(keine)
        v.addWidget(self._titel_zeile("Thema-Farben"))
        v.addLayout(self._raster(F.thema_raster()))
        if standard:
            v.addWidget(self._titel_zeile("Standard-Farben"))
            v.addLayout(self._raster([list(F.STANDARD_FARBEN)]))
        if verlauf: # „Graduelle Füllung“ wie in der Vorlage: dieselben Farben als Verläufe
            v.addWidget(self._titel_zeile(verlauf_titel))
            v.addLayout(kachel_gitter([_VerlaufKachel(self, farbe) for farbe in F.STANDARD_FARBEN], len(F.STANDARD_FARBEN), abstand=ABSTAND_ENG, oben_links=True))
        for titel_reihe, kacheln in (reihen or []):        # weitere Kachelreihen im Stil der Palette: (Titel, [(Schlüssel, Bild, Tipp)])
            v.addWidget(self._titel_zeile(titel_reihe))
            v.addLayout(kachel_gitter([_BildKachel(self, schl, bild, tipp) for schl, bild, tipp in kacheln], max(1, len(kacheln)), abstand=ABSTAND_ENG, oben_links=True))
        letzte = F.zuletzt_laden() if zuletzt else []
        if letzte:
            v.addWidget(self._titel_zeile("Zuletzt benutzt"))
            v.addLayout(self._raster([letzte]))
        if automatisch:                                    # „Automatisch“ mit schwarzem Feld (Vorlage: Füllung)
            auto = knopf("standard", automatisch, ohne_rand=True); auto.setProperty("listenzeile", True)
            pm = QPixmap(14, 14); pm.fill(QColor(Farbe.SCHWARZ)); auto.setIcon(QIcon(pm)); auto.clicked.connect(lambda: self.waehle(QColor(Farbe.SCHWARZ)))
            v.addWidget(auto)
        if weitere:
            mehr = knopf("standard", weitere_text, ohne_rand=True); mehr.setProperty("listenzeile", True); mehr.setIcon(symbole.icon("palette", ICON_KLEIN))
            mehr.clicked.connect(self._weitere)
            v.addWidget(mehr)
            from vcl.qt.widgets.bausteine.interaktion.felder import pipette as _pip
            if _pip.AKTIV and pipette:
                pip = knopf("standard", "Pipette", ohne_rand=True); pip.setProperty("listenzeile", True); pip.setIcon(symbole.icon("pipette", ICON_KLEIN))
                pip.clicked.connect(self._pipette)
                v.addWidget(pip)
        self._spalte = v
        self.widget(wid)

    def zusatz_eintrag(self, text: str, aktion) -> None:
        """Ein weiterer Eintrag unter „Weitere Farben …“ (z. B. „Rahmen und Schattierung …“); schließt die Palette und ruft ``aktion``."""
        k = knopf("standard", text, ohne_rand=True); k.setProperty("listenzeile", True)
        k.clicked.connect(lambda: (self.close(), aktion()))
        self._spalte.addWidget(k)

    @staticmethod
    def _titel_zeile(text: str) -> QLabel:
        l = QLabel(text)
        hinweis_stil(l, zusatz="font-size: " f"{SCHRIFT_GRUPPENTITEL_PX}" "px; padding-top: " f"{PADDING_PALETTE_TITEL_OBEN}" ";")
        return l

    @staticmethod
    def _keine_symbol() -> QIcon:
        return symbole.icon("ban", ICON_KLEIN)

    def _raster(self, zeilen: list[list[str]]) -> QLayout:
        g = kachel_gitter((), 1, abstand=ABSTAND_ENG, oben_links=True)
        for z, zeile in enumerate(zeilen):
            for s, farbe in enumerate(zeile):
                g.addWidget(_Kachel(self, farbe), z, s)
        return g

    def waehle(self, farbe: QColor | None) -> None:
        """Farbe übernehmen: merken, melden, Popup schließen."""
        if farbe is not None:
            F.zuletzt_merken(farbe.name())
        self.gewaehlt.emit(farbe)
        self.close()

    def _pipette(self) -> None:
        """„Pipette“: eine Farbe vom Bildschirm aufnehmen."""
        from vcl.qt.widgets.bausteine.interaktion.felder.pipette import farbe_vom_bildschirm
        self.close()
        c = farbe_vom_bildschirm(self.parentWidget())
        if c is not None:
            F.zuletzt_merken(c.name())
            self.gewaehlt.emit(c)

    def _weitere(self) -> None:
        self.close()
        weitere_farben_unter(self.parentWidget(), self.gewaehlt.emit, self._start, self._titel)
