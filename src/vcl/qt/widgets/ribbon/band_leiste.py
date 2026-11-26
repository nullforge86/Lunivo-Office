"""Das Band (Register): Reiter → Gruppen → Knöpfe, gebaut aus ressourcen/register.json.

register.json beschreibt Reiter, Gruppen und Knöpfe. Was `Befehle` nicht kennt, steht ausgegraut da.
"""
from __future__ import annotations

from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte

import json
import os

from system.plattform import ressourcen_pfade as pfade
from vcl.qt.widgets.bausteine.schrift.texte import trennlinie

from PySide6.QtCore import QSize, QTimer, Qt, Signal
from PySide6.QtWidgets import QStackedWidget, QToolButton, QWidget

from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import werkzeugknopf
from vcl.qt.widgets.bausteine.farben.thema.thema import kopf_symbolfarbe
from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_ENG, ICON_NORMAL, RAND_KEIN, RAND_POPUP_KOPF

NICHT_DA = "{} — in der nativen Fassung noch nicht umgesetzt"
STILE_KATALOG = ["Standard", "Überschrift 1", "Überschrift 2", "Überschrift 3", "Überschrift 4", "Überschrift 5", "Überschrift 6", "Überschrift 7", "Überschrift 8", "Überschrift 9", "Titel", "Untertitel", "Zitat", "Kein Abstand"]
MIN_KNOPF = 36                                                  # kleinste Breite eines Bandknopfes in px


def lade_register() -> dict:
    with open(os.path.join(pfade.RESSOURCEN, "register.json"), encoding="utf-8") as fh:
        d = json.load(fh)
    # Start ▸ Stile: Startknopf für „Formatvorlagen verwalten“ (alt: Dialog unter „Neue Formatvorlage“)
    for t in d["register"]:
        for g in t.get("gruppen", []):
            pass
    return d


from vcl.qt.widgets.ribbon.band_stile import BandStileBaustein
from vcl.qt.widgets.ribbon.band_reiter import BandReiterBaustein
from vcl.qt.widgets.ribbon.band_raender import BandRaenderBaustein
from vcl.qt.widgets.ribbon.band_zustand import BandZustandBaustein
from vcl.qt.widgets.ribbon.band_schnellzugriff import BandSchnellzugriffBaustein
from vcl.qt.widgets.ribbon.band_knoepfe import BandKnopfBaustein
from vcl.qt.widgets.ribbon.band_gruppen import BandGruppenBaustein
from vcl.qt.widgets.ribbon.band_uebersicht import BandUebersichtBaustein
from vcl.qt.widgets.ribbon.band_start import BandStartBaustein
from vcl.qt.widgets.ribbon.band_bausteine import KURZ, STANDARD_VERSTECKT, _BandSeite, _FelderDict, _GruppenTrenner, _ReiterLeiste, _SperrKasten, _kurz, _mit_kuerzel, _zweizeilig


class RegisterBand(BandSchnellzugriffBaustein, BandReiterBaustein, BandUebersichtBaustein, BandStartBaustein, BandRaenderBaustein, BandZustandBaustein, BandStileBaustein, BandKnopfBaustein, BandGruppenBaustein, QWidget):
    """Kopfzeile (☰, Schnellzugriff, Reiter) und darunter das Band des gewählten Reiters."""

    seiteGebaut = Signal()

    # Maße des Bandes: normal und kompakt (Optionen ▸ Ansicht ▸ „Kompaktes Menüband“): niedrigeres Band, keine Gruppenunterschriften
    BAND_HOEHE = {False: 112, True: 88}
    GROSS_ICON = {False: 28, True: 24}

    def __init__(self, befehle, daten: dict | None = None, cfg: dict | None = None, schnell: list | None = None, kompakt: bool = True):
        super().__init__()
        self.setObjectName("bandKopf"); self.setAttribute(Qt.WA_StyledBackground, True)      # Thema Mint: Kopfzeile in einem Farbton
        self.kompakt = kompakt
        self.cfg = cfg or {}
        self._schnell_wahl = schnell
        self.b = befehle
        self.daten = daten or lade_register()
        self.schalter: list[tuple[QToolButton, str]] = []     # (Knopf, Aktionsname) für Haken
        self.wechsler: list[tuple[QToolButton, str]] = []     # Knöpfe, deren Symbol dem zuletzt gewählten Menüeintrag folgt (Groß-/Kleinschreibung)
        self.knoepfe: list[tuple[QToolButton, str | None, bool]] = []   # (Knopf, Name, braucht Dokument)
        self.felder: dict[str, QWidget] = _FelderDict(self)
        self.fehlend: list[str] = []
        self._offen: dict[int, tuple] = {}                    # Stapelindex → (Seite, Reiter): noch nicht gebaute Reiter
        self._hat_dok = None
        self._ansichten: dict = {}                            # Stapelindex → Gruppenübersicht und Gruppendetail des Reiters
        lay = _spalte("kein", self)
        self.kopf = _reihe("popup")
        self.menue_knopf = werkzeugknopf("band_menue_kopf", "Menü", symbol="menu", symbolfarbe=kopf_symbolfarbe(), symbol_einpassen=True)
        self.menue_knopf.setObjectName("menueKnopf")
        self.kopf.addWidget(self.menue_knopf)
        self.schnell = _reihe("kein")
        self.kopf.addLayout(self.schnell)
        self._trenner()
        self.reiter = _ReiterLeiste()
        self.reiter.setObjectName("bandReiter")
        self.reiter.setDrawBase(False)
        self.reiter.setExpanding(False)
        self.reiter.setProperty("kompakt", kompakt)
        self.kopf.addWidget(self.reiter, 1)
        zeile = QWidget(); zeile.setObjectName("bandKopfZeile"); zeile.setAttribute(Qt.WA_StyledBackground, True)     # Thema Mint: Kopfzeile als grüne Fläche mit runden unteren Ecken
        zeile.setLayout(self.kopf)
        lay.addWidget(zeile)
        self.stapel = QStackedWidget()
        self.stapel.setObjectName("bandStapel")
        self.stapel.setFixedHeight(self.BAND_HOEHE[kompakt])
        lay.addWidget(self.stapel)
        linie = self.linie = trennlinie(tief=True)
        linie.setObjectName("bandLinie")                          # das Thema nimmt ihr die harte Kante: die Bandkarte grenzt das Band ab
        lay.addWidget(linie)
        self._schnellzugriff()
        self.kontext_index: dict[str, int] = {}
        self.kontext_weitere: dict[str, list[int]] = {}               # weitere Reiter desselben Kontexts (Tabellenstil neben Tabellentools)
        for r in self._plan_angepasst():
            self._reiter(r)
        self.reiter.currentChanged.connect(self._reiter_gewaehlt)
        self.reiter.tabBarClicked.connect(self._reiter_geklickt)
        self.reiter.doppelt.connect(self.einklappen_umschalten)
        self.reiter.setCurrentIndex(self._start_index())          # Start
        QTimer.singleShot(0, self._im_leerlauf_bauen)

    @property
    def bandfehler(self) -> list[str]:
        self._alle_bauen()
        return sorted(set(self.fehlend))

    einklappbar = True          # Optionen ▸ Doppelklick blendet das Band aus
    _eingeklappt = False

    def _trenner(self):
        self.kopf.addWidget(trennlinie(senkrecht=True, tief=True))

    # ---- Reiter und Gruppen -------------------------------------------------------------------------------


    def gruppe_widget(self, g: dict) -> QWidget:
        """Eine Gruppe als eigenständiges Widget (für die Seitenleiste)."""
        return self._gruppe(g)

