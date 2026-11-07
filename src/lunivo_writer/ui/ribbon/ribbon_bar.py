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


from lunivo_writer.ui.ribbon.ribbon_knoepfe import BandKnopfBaustein
from lunivo_writer.ui.ribbon.ribbon_gruppen import BandGruppenBaustein
from lunivo_writer.ui.ribbon.ribbon_bausteine import (
    KURZ, STANDARD_VERSTECKT, _BandSeite, _FelderDict, _GruppenTrenner,
    _ReiterLeiste, _SperrKasten, _kurz, _mit_kuerzel, _zweizeilig,
)


class RegisterBand(BandKnopfBaustein, BandGruppenBaustein, QWidget):
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

    def _reiter_gewaehlt(self, i: int) -> None:
        self._seite_bauen(i)
        self.stapel.setCurrentIndex(i)

    def _seite_bauen(self, i: int) -> None:
        eintrag = self._offen.pop(i, None)
        if eintrag is None:
            return
        scroll, r = eintrag
        seite = QWidget()
        h = QHBoxLayout(seite)
        h.setContentsMargins(*RAND_BANDREITER)
        h.setSpacing(0)
        for n, g in enumerate(r["gruppen"]):
            if n:
                h.addWidget(_GruppenTrenner())
            h.addWidget(self._gruppe(g))
        h.addStretch(1)
        scroll.setWidget(seite)
        self.aktualisieren(self._hat_dok)                  # Zustand (aktiv/Haken) auch für die neuen Knöpfe

    def _alle_bauen(self) -> None:
        for i in list(self._offen):
            self._seite_bauen(i)

    def _im_leerlauf_bauen(self) -> None:
        """Nach dem Anzeigen: je Durchlauf einen Reiter bauen, damit die Oberfläche dazwischen bedienbar bleibt."""
        try:
            if self._offen:
                self._seite_bauen(next(iter(self._offen)))
            if self._offen:
                QTimer.singleShot(0, self._im_leerlauf_bauen)
        except RuntimeError:                                    # Band wurde inzwischen abgebaut
            pass

    einklappbar = True          # Optionen ▸ Doppelklick blendet das Band aus
    _eingeklappt = False

    def _reiter_geklickt(self, _i):
        if self._eingeklappt:
            self._eingeklappt = False
            self.stapel.setVisible(True)

    def einklappen_umschalten(self):
        if not self.einklappbar:
            return
        self._eingeklappt = not self._eingeklappt
        self.stapel.setVisible(not self._eingeklappt)

    def _trenner(self):
        self.kopf.addWidget(trennlinie(senkrecht=True, tief=True))

    # ---- Schnellzugriff -------------------------------------------------------------------------------
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

    def _plan_angepasst(self) -> list[dict]:
        """Reiter in der Reihenfolge der Struktur — ausgeblendete weglassen, eigene Reihenfolge beachten (Register anpassen)."""
        alle = plan(self.daten)
        haupt = [r for r in alle if not r.get("kontext")]
        kontext = [r for r in alle if r.get("kontext")]
        ordnung = self.cfg.get("reihenfolge") or []
        versteckt = set(self.cfg["versteckt"] if "versteckt" in self.cfg else STANDARD_VERSTECKT) - {"Datei"}
        haupt.sort(key=lambda r: ordnung.index(r["name"]) if r["name"] in ordnung else 999)
        return [r for r in haupt if r["name"] not in versteckt] + kontext

    def _tausch_rechtsklick(self, k: QToolButton, sym: str) -> None:
        """Rechtsklick auf einen Knopf: Fenster „Symbol austauschen“ mit der Zeichnung dieses Knopfes."""
        if not icons.hat(sym):
            return
        k.setContextMenuPolicy(Qt.CustomContextMenu)
        k.customContextMenuRequested.connect(lambda _p, s=sym: self.b.symbolTauschen(None, s))

    def _schnellzugriff(self):
        liste = self.SCHNELL if self._schnell_wahl is None else [e for e in self.SCHNELL_ALLE if e[2] in self._schnell_wahl]
        for sym, name, aktion in liste:
            k = QToolButton()
            k.setAutoRaise(True)
            k.setToolTip(_mit_kuerzel(name))
            k.setIcon(icons.icon(sym, ICON_GROSS, kopf_symbolfarbe()))
            k.setIconSize(QSize(ICON_GROSS, ICON_GROSS))
            k.clicked.connect(lambda _=False, a=aktion: self.b.tun(a))
            self._tausch_rechtsklick(k, sym)
            self.schnell.addWidget(k)
            self.knoepfe.append((k, aktion, sym in ("speichern", "pdf", "drucken", "vorschau", "zurueck", "vor")))

    def ki_schnell(self, aktionen: list, ausfuehren) -> None:
        """„Schnelle KI-Aktionen“ mit Zugriff „Schnellzugriff“: je ein Knopf hinter den übrigen der Schnellzugriffsleiste."""
        for k in getattr(self, "_ki_schnell_knoepfe", []):
            self.schnell.removeWidget(k); k.hide(); k.setParent(None); k.deleteLater()
        self._ki_schnell_knoepfe = []
        for a in aktionen:
            k = QToolButton(); k.setAutoRaise(True); k.setToolTip("KI: " + a["name"])
            k.setIcon(icons.icon("assistent", ICON_GROSS, kopf_symbolfarbe())); k.setIconSize(QSize(ICON_GROSS, ICON_GROSS))
            k.clicked.connect(lambda _=False, a=a: ausfuehren(a))
            self.schnell.addWidget(k)
            self._ki_schnell_knoepfe.append(k)

    # ---- Reiter und Gruppen -------------------------------------------------------------------------------
    def _reiter(self, r: dict):
        scroll = _BandSeite()
        scroll.setObjectName("bandSeite")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.stapel.addWidget(scroll)
        i = self.reiter.addTab(r["name"])
        self._offen[i] = (scroll, r)                              # Inhalt wird beim ersten Wählen oder im Leerlauf gebaut
        if r.get("kontext"):
            if r["kontext"] in self.kontext_index:
                self.kontext_weitere.setdefault(r["kontext"], []).append(i)
            else:
                self.kontext_index[r["kontext"]] = i
            self.reiter.setTabVisible(i, False)
            self.reiter.setTabData(i, "kontext")

    def _stile(self, spalten: int = 3) -> QWidget:
        host = QWidget()
        g = tabellen_gitter(host, abstand=ABSTAND_DICHT)
        self._stile_host, self._stile_gitter, self._stil_knoepfe = host, g, []
        self.stile_aktualisieren()
 # wie in der Vorlage: drei Spalten sichtbar (``"spalten": N`` im Gruppeneintrag nimmt weniger), der Rest wird durchgescrollt
        sa = QScrollArea()
        sa.setObjectName("stileGalerie")
        sa.setWidget(host)
        sa.setWidgetResizable(False)
        sa.setFrameShape(QFrame.NoFrame)
        sa.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sa.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        host.adjustSize()
        sa.setFixedWidth(spalten * 85 + 4)
        sa.setFixedHeight(host.sizeHint().height() + 2)
        sa.setStyleSheet("QScrollArea#stileGalerie, QScrollArea#stileGalerie > QWidget > QWidget { background: transparent; }")
        pfeil = QToolButton(); pfeil.setIcon(icons.icon("klappe", ICON_KLEIN)); pfeil.setIconSize(QSize(ICON_KLEIN, ICON_KLEIN)); pfeil.setAutoRaise(True); pfeil.setFixedWidth(BREITE_AUFKLAPPPFEIL)
        pfeil.setToolTip("Alle Formatvorlagen")
        pfeil.clicked.connect(lambda: self._stile_popup(pfeil))
        sa.viewport().installEventFilter(self)
        self._stile_scroll = sa
        aussen = QWidget()
        h = QHBoxLayout(aussen); h.setContentsMargins(*RAND_KEIN); h.setSpacing(0)
        h.addWidget(sa); h.addWidget(pfeil, 0, Qt.AlignVCenter)
        return aussen

    def _stile_popup(self, unter: QWidget) -> None:
        """Alle Formatvorlagen als Galerie (Pfeil rechts neben der Reihe): Probe in der Vorlage, Name darunter; Überfahren zeigt live."""
        from lunivo_writer.editor import stile
        from lunivo_writer.ui.baukasten import GalerieAuswahl
        w = self.b.w
        m = GalerieAuswahl(w, titel="Stile")
        e = w.current_editor()
        aktuell = e.current_style() if e is not None else None
        aktuell = "Standard" if aktuell == "Fließtext" else aktuell
        mehr = w.settings.get_bool("ui/stile_mehr", True)
        selten = {f"Überschrift {i}" for i in range(5, 10)}               # „Weitere Stile“: die selten gebrauchten
        for name in STILE_KATALOG + [n for n in stile.namen() if n not in STILE_KATALOG]:
            if not mehr and name in selten and name != aktuell:
                continue
            d = stile.definition(name)
            f = QFont("Liberation Sans")
            f.setPointSizeF(min(15.0, max(9.0, float(d["groesse"] or 10) * 0.8)))
            f.setBold(name.startswith("Überschrift") or name == "Titel" or bool(d["fett"]))
            f.setItalic(name in ("Untertitel", "Zitat") or bool(d["kursiv"]))
            m.kachel(name, name, f, farbe=d["farbe"] or None, aktuell=name == aktuell,
                     tipp=name + (" (eigene Vorlage)" if stile.ist_eigen(name) else ""))
        m.gewaehlt.connect(self.b.stilAnwenden)
        m.ueberfahren.connect(lambda name: w.vorschau.zeigen(lambda ed: self.b.stilVorschau(name, ed)))
        m.verlassen.connect(w.vorschau.ende)
        m.aktion("Neue Formatvorlage …", lambda: self.b.neueFormatvorlage(), icons.icon("pinsel", ICON_GROSS))
        m.aktion("Stil löschen", lambda: self.b.formatvorlageLoeschen(aktuell), icons.icon("radierer", ICON_GROSS),
                 aktiv=bool(aktuell) and stile.ist_eigen(aktuell))
        m.aktion("Weitere Stile anzeigen", lambda an: w.settings.set("ui/stile_mehr", an), haken=mehr)

        def kontext(name, pos):
            from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
            km = MenueListe(m)
            km.eintrag("Ändern …", lambda: (m.close(), self.b.formatvorlageAendern(name)))
            if stile.ist_eigen(name):
                km.eintrag("Löschen", lambda: (m.close(), self.b.formatvorlageLoeschen(name)))
            km.exec(pos)
        m.kontext.connect(kontext)
        m.aboutToHide.connect(w.vorschau.ende)
        from PySide6.QtCore import QPoint
        m.popup(unter.mapToGlobal(QPoint(-m.sizeHint().width() + unter.width() + 4, unter.height())))

    def stile_aktualisieren(self) -> None:
        """Die Galerie neu füllen — die eingebauten Vorlagen und die selbst angelegten (editor/stile.py)."""
        from lunivo_writer.editor import stile
        from lunivo_writer.ui.widgets.live_vorschau import Ueberfahren
        g = self._stile_gitter
        alt = {id(k) for k in self._stil_knoepfe}
        self.knoepfe = [e for e in self.knoepfe if id(e[0]) not in alt]
        for k in self._stil_knoepfe:
            g.removeWidget(k); k.hide(); k.setParent(None); k.deleteLater()
        self._stil_knoepfe = []
        for i, name in enumerate(STILE_KATALOG + [n for n in stile.namen() if n not in STILE_KATALOG]):
            k = QToolButton()
            k.setAutoRaise(True)
            k.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            d = stile.definition(name)
            k.setText(f"Aa\n{name}")
            f = k.font()
            f.setPointSizeF(8)
            if name.startswith("Überschrift") or name == "Titel" or (stile.ist_eigen(name) and d["fett"]):
                f.setBold(True)
            if name in ("Untertitel", "Zitat") or (stile.ist_eigen(name) and d["kursiv"]):
                f.setItalic(True)
            k.setFont(f)
            k.setFixedWidth(BREITE_VORLAGEN_AKTUALISIEREN)
            k.setToolTip(name + (" (eigene Vorlage)" if stile.ist_eigen(name) else ""))
            k.clicked.connect(lambda _=False, n=name: self.b.stilAnwenden(n))
            fl = Ueberfahren(self.b.w.vorschau, lambda e, n=name: self.b.stilVorschau(n, e))
            k.installEventFilter(fl)
            k._ueberfahren = fl                                  # am Knopf festhalten, sonst räumt Python den Filter ab
            g.addWidget(k, i % 2, i // 2)
            self.knoepfe.append((k, None, True))
            self._stil_knoepfe.append(k)
        self._stile_host.adjustSize()

    def eventFilter(self, obj, ev):
        from PySide6.QtCore import QEvent
        sa = getattr(self, "_stile_scroll", None)
        if sa is not None and obj is sa.viewport() and ev.type() == QEvent.Wheel:
            sa.horizontalScrollBar().setValue(sa.horizontalScrollBar().value() - ev.angleDelta().y() // 2)
            return True
        return super().eventFilter(obj, ev)

    def _raender(self) -> QWidget:
        host = QWidget()
        h = QHBoxLayout(host)
        h.setContentsMargins(*RAND_KEIN)
        h.setSpacing(ABSTAND_ENG)
        for art, text in self.b.galerie_randVorgaben():
            k = QToolButton()
            k.setAutoRaise(True)
            k.setText(text)
            k.setFixedSize(BREITE_BAND_GRUPPENKNOPF, HOEHE_BAND_GRUPPENKNOPF_KOMPAKT if self.kompakt else HOEHE_BAND_GRUPPENKNOPF)
            k.clicked.connect(lambda _=False, a=art: (self.b.randVorgabeWaehlen(a), self.aktualisieren()))
            h.addWidget(k)
            self.knoepfe.append((k, None, True))
        return host

    def kontext(self, name: str, sichtbar: bool, aktivieren: bool = False) -> None:
        """Kontext-Register (Tabellentools, Bildtools …) ein- oder ausblenden; ``aktivieren``: gleich öffnen."""
        i = self.kontext_index.get(name)
        if i is None:
            return
        alle = (i, *self.kontext_weitere.get(name, ()))              # die weiteren Reiter des Kontexts folgen dem ersten
        if sichtbar and aktivieren:
            for j in alle:
                self.reiter.setTabVisible(j, True)
            self.reiter.setCurrentIndex(i)
            return
        if self.reiter.isTabVisible(i) == sichtbar:
            return
        war_aktiv = self.reiter.currentIndex() in alle                 # Qt springt beim Ausblenden selbst zu einem Nachbarn: vorher merken
        for j in alle:
            self.reiter.setTabVisible(j, sichtbar)
        if not sichtbar and war_aktiv:
            self.reiter.setCurrentIndex(self._start_index())

    def _start_index(self) -> int:
        for i in range(self.reiter.count()):
            if self.reiter.tabText(i) == "Start":
                return i
        return 0

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
