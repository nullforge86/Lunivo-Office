"""Das Band (Register): Reiter → Gruppen → Knöpfe, gebaut aus resources/register.json.

register.json beschreibt Reiter, Gruppen und Knöpfe. Was `Befehle` nicht kennt, steht ausgegraut da.
"""
from __future__ import annotations

import json
import os
from lunivo_writer.ui.baukasten.texte import hinweis_stil, trennlinie
from lunivo_writer.core import paths

from PySide6.QtCore import QPropertyAnimation, QRectF, QSize, QTimer, Qt, Signal
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPainter
from PySide6.QtWidgets import (
    QCheckBox, QFontComboBox, QFrame, QHBoxLayout, QLabel, QMenu, QScrollArea, QSizePolicy, QStackedWidget, QToolButton,
    QVBoxLayout, QWidget,
)

from lunivo_writer.ui.baukasten.dropdown.bild_diagramm_menues import FELDER, GALERIEN, KLAPPEN
from lunivo_writer.ui.baukasten.text_format import groesse_feld, schrift_feld
from lunivo_writer.ui.document.document_editor import STYLES
from lunivo_writer.ui.widgets import icons
from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
from lunivo_writer.ui.baukasten.flache_reiter_leiste import UeberlaufLeiste
from lunivo_writer.ui.baukasten.formular_gitter import tabellen_gitter
from lunivo_writer.ui.baukasten.karten_raster import kachel_gitter
from lunivo_writer.ui.theme import kopf_symbolfarbe
from lunivo_writer.ui.ribbon.plan import plan

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.mass import (
    DROPDOWN_HOEHE,
    ABSTAND_DICHT,
    ABSTAND_ENG,
    ABSTAND_KLEIN,
    BREITE_AUFKLAPPPFEIL,
    BREITE_BAND_GRUPPENKNOPF,
    BREITE_GRUPPENTRENNER,
    BREITE_MASSFELD_BAND,
    BREITE_RANDFELD_BAND,
    BREITE_VORLAGEN_AKTUALISIEREN,
    GROESSE_BANDKNOPF_ICON_KLEIN,
    GROESSE_GRUPPEN_STARTER,
    HOEHE_BAND_GRUPPENKNOPF,
    HOEHE_BAND_GRUPPENKNOPF_KOMPAKT,
    ICON_GROSS,
    ICON_KLEIN,
    ICON_NORMAL,
    PADDING_BANDKNOPF,
    RAND_BANDGALERIE,
    RAND_BANDREITER,
    RAND_KEIN,
    RAND_POPUP_KOPF,
    SCHRIFT_BANDGRUPPE_TITEL,
    SCHRIFT_BANDKNOPF,
)
from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Schriftauswahl
from lunivo_writer.ui.baukasten.dropdown.dropdown_knopf import DropdownKnopf
NICHT_DA = "{} — in der nativen Fassung noch nicht umgesetzt"
STILE_KATALOG = ["Standard", "Überschrift 1", "Überschrift 2", "Überschrift 3", "Überschrift 4", "Überschrift 5", "Überschrift 6", "Überschrift 7", "Überschrift 8", "Überschrift 9", "Titel", "Untertitel", "Zitat", "Kein Abstand"]
MIN_KNOPF = 36                                                  # kleinste Breite eines Bandknopfes in px
TEXTSYMBOLE = {"F": QFont.Bold, "K": None, "U": None}


def lade_register() -> dict:
    with open(os.path.join(paths.RESSOURCEN, "register.json"), encoding="utf-8") as fh:
        d = json.load(fh)
    # Start ▸ Stile: Startknopf für „Formatvorlagen verwalten“ (alt: Dialog unter „Neue Formatvorlage“)
    for t in d["register"]:
        for g in t.get("gruppen", []):
            pass
    return d


from lunivo_writer.ui.ribbon.ribbon_stile import BandStileBaustein
from lunivo_writer.ui.ribbon.ribbon_reiter import BandReiterBaustein
from lunivo_writer.ui.ribbon.ribbon_raender import BandRaenderBaustein
from lunivo_writer.ui.ribbon.ribbon_schnellzugriff import BandSchnellzugriffBaustein
from lunivo_writer.ui.ribbon.ribbon_knoepfe import BandKnopfBaustein
from lunivo_writer.ui.ribbon.ribbon_gruppen import BandGruppenBaustein
from lunivo_writer.ui.ribbon.ribbon_bausteine import (
    KURZ, STANDARD_VERSTECKT, _BandSeite, _FelderDict, _GruppenTrenner,
    _ReiterLeiste, _SperrKasten, _kurz, _mit_kuerzel, _zweizeilig,
)


class RegisterBand(BandSchnellzugriffBaustein, BandReiterBaustein, BandRaenderBaustein, BandStileBaustein, BandKnopfBaustein, BandGruppenBaustein, QWidget):
    """Kopfzeile (☰, Schnellzugriff, Reiter) und darunter das Band des gewählten Reiters."""

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
        lay = QVBoxLayout(self)
        lay.setContentsMargins(*RAND_KEIN)
        lay.setSpacing(0)
        self.kopf = QHBoxLayout()
        self.kopf.setContentsMargins(*RAND_POPUP_KOPF)
        self.kopf.setSpacing(ABSTAND_ENG)
        self.menue_knopf = QToolButton()
        self.menue_knopf.setText("Menü")
        self.menue_knopf.setIcon(icons.icon("menu", ICON_NORMAL, kopf_symbolfarbe())); self.menue_knopf.setIconSize(QSize(ICON_NORMAL, ICON_NORMAL))
        self.menue_knopf.setToolButtonStyle(Qt.ToolButtonTextBesideIcon); self.menue_knopf.setLayoutDirection(Qt.RightToLeft)
        self.menue_knopf.setAutoRaise(True); self.menue_knopf.setObjectName("menueKnopf")
        self.kopf.addWidget(self.menue_knopf)
        self.schnell = QHBoxLayout()
        self.schnell.setSpacing(0)
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

    # ---- Zustand -----------------------------------------------------------------------------------------------
    def aktualisieren(self, hat_dokument: bool | None = None):
        if hat_dokument is not None:
            self._hat_dok = hat_dokument
        for k, name in self.wechsler:
            n = self.b.symbolname(name)
            if n:
                k.defaultAction().setIcon(icons.icon(n, k.iconSize().width()))
        for k, name in self.schalter:
            z = self.b.zustand(name) if name else None
            a = k.defaultAction()
            a.blockSignals(True)
            a.setChecked(bool(z))
            a.blockSignals(False)
        if hat_dokument is not None:
            for k, name, braucht in self.knoepfe:
                if braucht and not k.property("fehlt"):
                    k.setEnabled(hat_dokument)
        for k, name, _braucht in self.knoepfe:                    # Befehle mit eigener Bedingung (kann_<Befehl>) bleiben sonst grau
            if name and not k.property("fehlt"):
                frei = self.b.kann(name)
                if frei is not None:
                    k.setEnabled(bool(frei) and hat_dokument is not False)
        for f in self.felder.values():                            # Felder aus band_feld ziehen ihren Zustand selbst nach (auffrischen)
            auf = getattr(f, "auffrischen", None)
            if callable(auf):
                auf()
