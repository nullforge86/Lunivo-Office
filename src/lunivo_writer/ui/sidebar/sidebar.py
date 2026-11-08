"""Die Schreibhilfe-Seitenleiste: Prüfen, Wellen/Vorhersage/AutoKorr, Funde, „Für wen?“, KI-Knöpfe."""
from __future__ import annotations

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QComboBox, QButtonGroup, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QStackedWidget, QToolButton, QSizePolicy,
    QVBoxLayout, QWidget,
)

from lunivo_writer.ui.schreibhilfe_katalog import VORLESEN
from lunivo_writer.ui.baukasten.controls.panel_rahmen import PanelRahmen, rollflaeche
from lunivo_writer.proofing.vorhersage import EMPFAENGER
from lunivo_writer.ui.sidebar.panels.writing_panel import FundKarte, HinweisKarte
from lunivo_writer.ui.widgets import icons

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.theme import karte_einrichten, karten_rand
from lunivo_writer.ui.baukasten.basis.texte import hinweis_label, kleintext_label, trennlinie
from lunivo_writer.ui.baukasten.basis.mass import (
    BREITE_AKTIONSKNOPF_MIN,
    BREITE_SEITENLEISTE_PANEL,
    ABSTAND_KLEIN,
    ABSTAND_MITTEL,
    ABSTAND_NORMAL,
    BREITE_SCHREIBHILFE_MAX,
    BREITE_SCHREIBHILFE_MIN,
    HOEHE_KNOPF_GROSS,
    HOEHE_LISTE_HOCH,
    ICON_NORMAL,
    PADDING_HINWEIS,
    PADDING_SEITENLEISTE_REITER,
    PADDING_SEITENLEISTE_WARNUNG,
    RAND_KEIN,
    RAND_SCHREIBHILFE_BANNER,
    RAND_SEITENLEISTE_TABS,
)
from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Auswahlfeld
from lunivo_writer.ui.baukasten.dropdown.dropdown_knopf import DropdownKnopf
def werk_reiter_stil() -> str:
    """Stylesheet beim Aufruf formatiert, damit das Thema gilt."""
    return (('QPushButton { border: none; border-bottom: 3px solid transparent; border-radius: 0; padding: ' f"{PADDING_SEITENLEISTE_REITER}" '; font-weight: bold; color: palette(mid); background: transparent; }QPushButton:checked { color: palette(window-text); border-bottom: 3px solid palette(highlight); }QPushButton:hover { color: palette(window-text); }QPushButton:focus { border-bottom: 3px solid palette(highlight); }'))
from lunivo_writer.ui.baukasten.controls.schalter import chip_gruen_stil as chip_gruen, chip_stil   # alte Namen bleiben
LEER = ("Nichts gefunden. Das heißt nicht, dass alles richtig ist — die Schreibhilfe sucht nur die Fehler, "
        "die ein Rechtschreibprüfer nicht finden kann.")
class SchreibhilfePanel(QWidget):
    _ollama_gefunden = Signal(list)
    bereich_geaendert = Signal(int)

    BREITE = BREITE_SEITENLEISTE_PANEL                                   # die Seitenleiste ist immer so breit (innerhalb 300–420); der Inhalt passt sich an, nie umgekehrt

    def sizeHint(self):
        from PySide6.QtCore import QSize
        return QSize(self.BREITE + 2 * karten_rand(), super().sizeHint().height())

    def __init__(self, assistent, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)     # Rahmen und Fläche aus dem Thema (Mint) sichtbar
        self.a = assistent
        self.setMinimumWidth(BREITE_SCHREIBHILFE_MIN)
        self.setMaximumWidth(BREITE_SCHREIBHILFE_MAX)
        aussen = QVBoxLayout(self)
        aussen.setContentsMargins(*RAND_KEIN)
        karte_einrichten(self, aussen)                      # gemeinsames Aussehen mit den Feldern links (theme.py)
        aussen.setSpacing(0)
        self.stapel = QStackedWidget()
        aussen.addWidget(self.stapel, 1)
        seite0 = QWidget()
        self.stapel.addWidget(seite0)
        w0 = QVBoxLayout(seite0); w0.setContentsMargins(*RAND_KEIN); w0.setSpacing(0)
        # Werkbank: vier Reiter nach dem, was man gerade braucht — Prüfen (die Funde), Lesen, Schreiben, KI
        from lunivo_writer.ui.schreibhilfe_katalog import REITER
        leiste = QHBoxLayout(); leiste.setContentsMargins(*RAND_SEITENLEISTE_TABS); leiste.setSpacing(ABSTAND_KLEIN)
        self.werk_reiter = QButtonGroup(self)
        self._werk_namen = list(REITER)
        for i, name in enumerate(REITER):
            b = QPushButton(name); b.setCheckable(True); b.setChecked(i == 0); b.setMinimumHeight(HOEHE_KNOPF_GROSS); b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet(werk_reiter_stil())
            self.werk_reiter.addButton(b, i); leiste.addWidget(b, 1)
        self._werk_leiste = QWidget(); self._werk_leiste.setLayout(leiste); self._werk_leiste.hide()      # die Reiter stehen in der Leiste rechts (Seitenleiste), nicht mehr oben: mehr Platz
        self.werk_stapel = QStackedWidget()
        w0.addWidget(self.werk_stapel, 1)
        self.werk_reiter.idClicked.connect(self.werk_stapel.setCurrentIndex)
        pruef_seite = QWidget()
        self.werk_stapel.addWidget(pruef_seite)
        pl = QVBoxLayout(pruef_seite); pl.setContentsMargins(*RAND_KEIN); pl.setSpacing(0)
        rahmen = PanelRahmen("Schreibhilfe", schliessbar=False, titel_teile=(("Schreib", None), (" | ", "AKZENT"), ("hilfe", None)),
                             knoepfe=(("circle-question-mark", "Welche Hilfe wann? (F6)", self.welche_hilfe),))
        rahmen.knoepfe[0].setAccessibleName("Welche Hilfe wann")
        pl.addWidget(rahmen)
        v = rahmen.inhalt                                                  # Kopfzeile und Abstände aus dem gemeinsamen Baustein
        self.chips = {}                                   # We/Vo/Ko stehen jetzt auf dem Reiter „Schreiben“ — hier bleibt mehr Platz für die Funde
        self._einfuehrung = []
        self.liste = QVBoxLayout()
        self.liste.setSpacing(ABSTAND_NORMAL)
        host = QWidget()
        host.setLayout(self.liste)
        self.meldung = hinweis_label("Noch nicht geprüft.", zusatz="padding: " f"{PADDING_HINWEIS}" ";")
        self.liste.addWidget(self.meldung)
        self.liste.addStretch(1)
        sc = rollflaeche(host)                                                       # nie seitlich rollen müssen: alles auf der Karte bleibt erreichbar
        sc.setMinimumHeight(HOEHE_LISTE_HOCH)                                        # der Hauptinhalt: die Funde bekommen immer Platz, auch auf kleinen Bildschirmen
        v.addWidget(sc, 1)
        self.alle = QPushButton("Alle sicheren Fehler ändern")
        self.alle.clicked.connect(self._alle)
        self.alle.hide()
        v.addWidget(self.alle)
        # Für wen?
        v.addWidget(trennlinie(tief=True))
        # Eine Zeile statt zwei Reihen Chips: „Für wen?“ als Auswahl, daneben „Worum geht's?“ — der Platz gehört den Funden
        from lunivo_writer.ui.baukasten.controls.formular_gitter import FlussLayout, FormularGitter
        kontext = QWidget(); kontext_gitter = FormularGitter(kontext); kontext_gitter.setContentsMargins(*RAND_KEIN)
        fw = kleintext_label("Für wen")
        self.thema = Auswahlfeld()
        for name in EMPFAENGER:
            self.thema.addItem(name)
        self.thema.setCurrentText(self.a.thema)
        self.thema.an_inhalt()
        self.thema.setToolTip("Für wen schreiben Sie? Danach richtet sich, was als Fehler zählt und welche Wörter vorgeschlagen werden.")
        self.thema.setAccessibleName("Für wen")
        self.thema.currentTextChanged.connect(self.a.setze_thema)
        self.worum = QLineEdit()
        self.worum.setPlaceholderText("Worum geht's? (freiwillig)")
        self.worum.setAccessibleName("Worum geht es im Text (freiwillig)")
        self.worum.setMaxLength(300)
        self.worum.setStyleSheet("QLineEdit { border: none; border-bottom: 1px dashed %s; background: transparent; "
                                 "padding: " f"{PADDING_SEITENLEISTE_WARNUNG}" "; border-radius: 0; }" % Farbe.WARNUNG)
        pal = self.worum.palette(); pal.setColor(QPalette.PlaceholderText, QColor(Farbe.WARNUNG)); self.worum.setPalette(pal)
        fw2 = QLabel("Worum geht's?"); fw2.setStyleSheet(fw.styleSheet())
        kontext_gitter.reihe((fw, self.thema), (fw2, self.worum), gewichte=(2, 3))
        v.addWidget(kontext)
        # Unten, wo man nach dem Schreiben hinschaut: „Prüfen“ mit seiner Erklärung, darunter die beiden KI-Wege
        from lunivo_writer.ui.baukasten.controls.karten_raster import KartenRaster
        zk = KartenRaster(min_breite=BREITE_AKTIONSKNOPF_MIN, abstand=ABSTAND_NORMAL)  # Raster: Prüfen · KI-Korrektur · Vorschläge gleich breit und gleich hoch
        self.pruefen = QPushButton("Prüfen")
        self.pruefen.setToolTip("Prüfen (F7) — sucht die Fehler, die ein Rechtschreibprüfer nicht finden kann")
        self.pruefen.clicked.connect(lambda: self.a.pruefen(True))
        self.ki_korrektur = QPushButton("KI-Korrektur"); self.ki_korrektur.setToolTip("KI-Korrektur (F8)")
        self.ki_vorschlaege = QPushButton("Vorschläge"); self.ki_vorschlaege.setToolTip("Verbesserungsvorschläge")
        for b_ in (self.pruefen, self.ki_korrektur, self.ki_vorschlaege):
            b_.setMinimumWidth(b_.sizeHint().width())                    # Beschriftung nie abschneiden: Zelle mindestens so breit wie der Text samt Rand
            zk.addWidget(b_)
        v.addLayout(zk)
        self.ki_info = hinweis_label("")                                 # steht auf dem Reiter KI, solange kein Modell verbunden ist
        self.ki_aktion = QPushButton("")
        self._ki_fn = None
        self.ki_aktion.clicked.connect(lambda: self._ki_fn() if self._ki_fn else None)
        self.a.fundeGeaendert.connect(self.zeige)
        self.a.schalterGeaendert.connect(self._schalter_nachziehen)
        self.a.themaGeaendert.connect(self._thema_nachziehen)
        self._ollama_gefunden.connect(self._ollama_da)
        self._seite_ki = rollflaeche()                                              # der Chat passt sich der Breite an, nichts wird seitlich abgeschnitten
        self.stapel.addWidget(self._seite_ki)

    # ---- KI ------------------------------------------------------------------------------------
    def verbinde_ki(self, dienst, fenster) -> None:
        self.ki, self.fenster = dienst, fenster
        self._werk_bauen()
        self.ki_korrektur.clicked.connect(lambda: fenster.befehle.tun("kiKorrektur"))            # ohne KI führt der Klick in die KI-Einstellungen
        self.ki_vorschlaege.clicked.connect(lambda: fenster.befehle.tun("kiVorschlaege"))
        self.worum.textChanged.connect(dienst.zettel)
        dienst.vorschlaege.connect(self.zeige_vorschlaege)
        dienst.hinweis.connect(self.zeige_hinweis)
        dienst.laeuft.connect(lambda an: self.ki_aktualisieren(an))
        dienst.geaendert.connect(self.ki_aktualisieren)
        self.ki_aktualisieren()
        QTimer.singleShot(300, self._ollama_pruefen)

    # ---- Verbindung mit den Optionen: was dort (oder anderswo) umgestellt wird, steht hier sofort richtig -----------------------
    def _schalter_nachziehen(self, name: str, an: bool) -> None:
        b = self.chips.get(name)
        if b is not None and b.isChecked() != an:
            b.blockSignals(True); b.setChecked(an); b.blockSignals(False)
            b.setToolTip(b.toolTip().rsplit(" — ", 1)[0] + (" — an" if an else " — aus"))

    def _thema_nachziehen(self, name: str) -> None:
        if self.thema.currentText() != name:
            self.thema.blockSignals(True); self.thema.setCurrentText(name); self.thema.blockSignals(False)

    def ki_aktualisieren(self, laeuft: bool = False) -> None:
        """Ohne Modell steht oben auf dem Reiter KI der Weg dorthin; die Zeilen selbst bleiben bedienbar (ein Klick führt in die KI-Einstellungen)."""
        ok = self.ki.verfuegbar()
        if ok:
            ziel = self.ki.ki.schickt_nach_aussen()
            info = ("Die KI läuft auf diesem Rechner — der Text verlässt ihn nicht." if ziel is None
                    else f"Beim Drücken geht der Text an „{ziel}“ (nur nach Ihrer Zustimmung).")
            for z in self.werk["KI"].zeilen:
                z.setToolTip((z.f.hinweis + " — " if z.f.hinweis else "") + info)
            self.ki_banner.hide()
        else:
            self.ki_info.setText("Es ist noch kein KI-Modell verbunden. Ollama auf diesem Rechner geht ohne Schlüssel und ohne Geld. "
                                 "Verbinden Sie es unten unter „KI-Einstellungen“.")
            self._ki_fn = None
            self.ki_aktion.hide()                           # den Weg dorthin gibt es schon einmal: die Zeile „KI-Einstellungen“
            self.ki_banner.show()
        self.werkbank_aktualisieren()

    # ---- Werkbank --------------------------------------------------------------------------------
    def _werk_bauen(self) -> None:
        """Die Reiter Lesen, Schreiben und KI aus dem Katalog; der Reiter Prüfen sind die Funde plus die Wege dahin."""
        from lunivo_writer.ui.baukasten.controls.werkbank import Werkbank
        self.ki_banner = QWidget()
        bl = QVBoxLayout(self.ki_banner); bl.setContentsMargins(*RAND_SCHREIBHILFE_BANNER)
        bl.addWidget(self.ki_info); bl.addWidget(self.ki_aktion)
        self.werk = {}
        for name in self._werk_namen[1:]:
            self.werk[name] = Werkbank(self.fenster, name, self.ki_banner if name == "KI" else None, ohne=VORLESEN if name == "Lesen" else None)
            seite = PanelRahmen(name, schliessbar=False)                 # Kopfzeile wie bei „Schreibhilfe“ und den Feldern links
            seite.inhalt.addWidget(self.werk[name], 1)
            self.werk_stapel.addWidget(seite)
        self.a.schalterGeaendert.connect(lambda *_: self.werkbank_aktualisieren())

    def werkbank_aktualisieren(self) -> None:
        for w in getattr(self, "werk", {}).values():
            w.aktualisieren()

    @property
    def aktueller_reiter(self) -> str:
        return self._werk_namen[self.werk_stapel.currentIndex()]

    def zeige_reiter(self, name: str) -> None:
        """Einen Reiter der Werkbank öffnen (und die Seitenleiste auf die Schreibhilfe stellen)."""
        i = self._werk_namen.index(name)
        self.werk_reiter.button(i).setChecked(True)
        self.werk_stapel.setCurrentIndex(i)
        self.zeige_bereich(0)

    def _ollama_pruefen(self) -> None:
        from PySide6.QtCore import QRunnable, QThreadPool

        panel = self

        class _O(QRunnable):
            def run(s_):
                try:
                    panel._ollama_gefunden.emit(panel.ki.ki.ollama_modelle())
                except Exception:
                    pass
        if not hasattr(self, "_ollama_gefunden"):
            return
        QThreadPool.globalInstance().start(_O())

    def _ollama_da(self, modelle: list) -> None:
        if self.ki.verfuegbar() or not modelle:
            return
        m = modelle[0]
        self.ki_info.setText("Auf diesem Rechner läuft Ollama — damit gehen die Knöpfe ohne Schlüssel und ohne Geld.")
        self.ki_aktion.setText(f"{m} nehmen")
        self._ki_fn = lambda: (self.ki.konfig.setze("modell", "ollama:" + m), self.ki_aktualisieren())
        self.ki_aktion.show()

    def zeige_vorschlaege(self, lst: list) -> None:
        self._funde_zeigen()                                 # die Karten kommen als Funde (quelle „ki“) über fundeGeaendert
        if not lst:
            self._leer("Die KI findet nichts, was sich leichter sagen ließe.")

    def _funde_zeigen(self) -> None:
        """Ergebnisse (Hinweise, Vorschläge, Übersetzung) erscheinen auf dem Reiter Prüfen — die Seitenleiste wird dafür geöffnet und umgestellt."""
        if self.isHidden() and hasattr(self.fenster, "toggle_sidebar"):
            self.fenster.toggle_sidebar()
        self.zeige_reiter("Prüfen")

    def zeige_hinweis(self, titel: str, text: str, cent) -> None:
        self._karten_leeren()
        self.liste.insertWidget(0, HinweisKarte(titel, text, cent, self.fenster, self))
        self._funde_zeigen()

    def _karten_leeren(self) -> None:
        while self.liste.count() > 1:
            it = self.liste.takeAt(0)
            w_ = it.widget()
            if w_ is not None:
                w_.hide(); w_.setParent(None); w_.deleteLater()

    def _leer(self, text: str) -> None:
        m = hinweis_label(text, zusatz="padding: " f"{PADDING_HINWEIS}" ";")
        self.liste.insertWidget(0, m)

    # ---- Bereich „Formatierung“: ein Register für Texteffekte, Objekt (Bild, Form …) und Diagrammteil ---------------------------------
    # schluessel -> (Modul, Panel-Klasse, Menütext, Signale des Panels). Ein neues Panel = ein Eintrag hier.
    FORMATE = {
        "texteffekte": ("formatierung.texteffekt_dialog", "TexteffektPanel", "Texteffekte formatieren", ("geaendert",)),
        "objekt": ("formatierung.objektformat_panel", "ObjektFormatPanel", "Objekt formatieren", ("geaendert", "bild_gewuenscht")),
        "diagramm": ("diagramme.diagramm_format_panel", "DiagrammFormatPanel", "Diagramm formatieren", ("geaendert", "alt_geaendert", "bild_gewuenscht", "teil_gewaehlt")),
        "smartart": ("diagramme.smartart_format_panel", "SmartArtFormatPanel", "SmartArt formatieren", ("geaendert", "bild_gewuenscht")),
    }

    def _format_zustand(self) -> dict:
        return self.__dict__.setdefault("_format_zustand_", {})

    def format_panel(self, schluessel: str):
        z = self._format_zustand().get(schluessel)
        return z[0] if z else None

    effekt_panel = property(lambda self: self.format_panel("texteffekte"))
    objekt_panel = property(lambda self: self.format_panel("objekt"))
    diagramm_panel = property(lambda self: self.format_panel("diagramm"))

    def _bereiche_menue(self, eltern, menue_text: str):
        """Das Menü am Titel „Formatierung ▾“: die Bereiche der Seitenleiste wie in der Vorlage (der eigene Bereich trägt den Haken)."""
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        from lunivo_writer.ui.widgets import icons
        m = MenueListe(eltern)
        tun = lambda name: (lambda: self.fenster.befehle.tun(name))
        m.eintrag("Formatvorlagen und Formatierung", tun("formatvorlagenBereich"), symbol=icons.icon("pen-line", ICON_NORMAL))
        m.eintrag("Auswahlbereich", tun("auswahlbereich"), symbol=icons.icon("mouse-pointer", ICON_NORMAL))
        m.eintrag("Bearbeitung einschränken", tun("bearbeitungEinschraenken"), symbol=icons.icon("lock", ICON_NORMAL))
        m.eintrag("Formatierung", None, symbol=icons.icon("sliders-horizontal", ICON_NORMAL), haken=True)
        m.eintrag("Sicherungsverwaltung", self._sicherungen_zeigen, symbol=icons.icon("rotate-ccw", ICON_NORMAL))
        return m

    @staticmethod
    def _sicherungen_zeigen() -> None:
        """Der Ordner mit den Sicherungskopien (derselbe wie in den Optionen)."""
        import os
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        from lunivo_writer.services import sicher_schreiben
        ordner = sicher_schreiben.sicherungs_ordner()
        os.makedirs(ordner, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(ordner))

    def _formatierung_host(self, panel_klasse, menue_text: str, werte: dict):
        """Der gemeinsame Rahmen der Bereiche „Formatierung“: Kopf mit „Formatierung ▾“, Anheften und Schließen, darunter das Panel."""
        from lunivo_writer.ui.baukasten.controls.zusatz_panel import FLACHE_REITER, zusatz_knopf
        from lunivo_writer.ui.baukasten.controls.panel_rahmen import PANEL_INHALT_RAND, panel_kopf
        host = QWidget(); host.setStyleSheet(FLACHE_REITER)        # dieselben flachen Reiter wie in den anderen Seitenleistenfenstern
        v = QVBoxLayout(host); v.setContentsMargins(*RAND_KEIN); v.setSpacing(0)
        titel = DropdownKnopf(); titel.setText("Formatierung"); titel.setAutoRaise(True)
        from lunivo_writer.ui.widgets import icons as _ic
        titel.setToolButtonStyle(Qt.ToolButtonTextBesideIcon); titel.setIcon(_ic.icon("chevron-down", 12))           # der Pfeil „▾“ ist sichtbar: das Titelmenü
        titel.setLayoutDirection(Qt.RightToLeft)   # Symbol hinter dem Text
        tf = titel.font(); tf.setBold(True); tf.setPointSizeF(tf.pointSizeF() + 1); titel.setFont(tf)       # Titel wie in der Titelzeile der anderen Seitenleistenfenster
        titel.menue_setzen(self._bereiche_menue(titel, menue_text), geteilt=False)
        anheften = zusatz_knopf("pin", "Anheften: der Bereich folgt der Markierung und bleibt offen", None, "Anheften"); anheften.setCheckable(True)
        zu = zusatz_knopf("x", "Schließen", lambda: self.zeige_bereich(0))
        stretch = QWidget(); stretch.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        v.addWidget(panel_kopf(titel, stretch, anheften, zu, dehnen=stretch))
        rumpf = QWidget(); rv = QVBoxLayout(rumpf); rv.setContentsMargins(*PANEL_INHALT_RAND); v.addWidget(rumpf, 1)      # Innenrand wie in allen Seitenleistenfenstern
        panel = panel_klasse(rumpf, werte)
        from lunivo_writer.ui.baukasten.controls.formular_gitter import felder_angleichen
        felder_angleichen(panel)                                                     # Felder und beschriftete Knöpfe gleich hoch (FELDHOEHE)
        rv.addWidget(panel, 1)
        from lunivo_writer.ui.baukasten.controls.flache_reiter_leiste import alle_flach
        alle_flach(host)                                                             # alle Reiter: dieselbe flache Leiste wie in allen Seitenleisten-Fenstern
        return host, panel, anheften

    def zeige_format(self, schluessel: str, werte: dict, **verbindungen) -> None:
        """Den Bereich „Formatierung“ für ``schluessel`` zeigen. ``verbindungen``: Signalname des Panels -> Empfänger (``None`` wird übergangen)."""
        import importlib
        from lunivo_writer.ui.baukasten.controls.formular_gitter import felder_angleichen
        modul, klasse, menue_text, signale = self.FORMATE[schluessel]
        zustand = self._format_zustand()
        if schluessel not in zustand:
            panel_klasse = getattr(importlib.import_module(f"lunivo_writer.ui.baukasten.{modul}"), klasse)
            host, panel, anheften = self._formatierung_host(panel_klasse, menue_text, werte)
            zustand[schluessel] = (panel, anheften, self.stapel.addWidget(host))
        else:
            panel = zustand[schluessel][0]
            for name in signale:
                try:
                    getattr(panel, name).disconnect()
                except (RuntimeError, TypeError):
                    pass
            panel.setze({**werte})
            felder_angleichen(panel)                                                 # nachgebaute Felder (Typ-/Abschnittswechsel) ebenfalls
        for name, empfaenger in verbindungen.items():
            if empfaenger is not None:
                getattr(panel, name).connect(empfaenger)
        self.zeige_bereich(zustand[schluessel][2])

    def format_sichtbar(self, schluessel: str) -> bool:
        z = self._format_zustand().get(schluessel)
        return z is not None and self.stapel.currentIndex() == z[2] and not self.isHidden()

    def aktualisiere_format(self, schluessel: str, werte: dict) -> None:
        """Die Werte des Panels an die Markierung anpassen (wenn der Benutzer gerade nicht darin bedient)."""
        from PySide6.QtWidgets import QApplication
        from lunivo_writer.ui.baukasten.controls.formular_gitter import felder_angleichen
        panel = self.format_panel(schluessel)
        f = QApplication.focusWidget()
        if panel is not None and not (f is not None and panel.isAncestorOf(f)):
            panel.setze(werte)
            felder_angleichen(panel)

    # Die bisherigen Namen bleiben als dünne Aufrufer.
    def zeige_texteffekte(self, werte: dict, anwenden) -> None:
        self.zeige_format("texteffekte", werte, geaendert=anwenden)

    def texteffekte_sichtbar(self) -> bool:
        return self.format_sichtbar("texteffekte")

    def aktualisiere_texteffekte(self, werte: dict) -> None:
        self.aktualisiere_format("texteffekte", werte)

    def zeige_objektformat(self, werte: dict, anwenden, reiter: int = 0, bild_wunsch=None) -> None:
        """``reiter``: 0 = Füllung und Linie, 1 = Effekte."""
        self.zeige_format("objekt", werte, geaendert=anwenden, bild_gewuenscht=bild_wunsch)
        self.objekt_panel.reiter.setCurrentIndex(reiter)

    def objektformat_sichtbar(self) -> bool:
        return self.format_sichtbar("objekt")

    def aktualisiere_objektformat(self, werte: dict) -> None:
        self.aktualisiere_format("objekt", werte)

    def zeige_diagrammformat(self, werte: dict, anwenden, alt_anwenden, bild_wunsch=None, teil_wunsch=None) -> None:
        self.zeige_format("diagramm", werte, geaendert=anwenden, alt_geaendert=alt_anwenden, bild_gewuenscht=bild_wunsch, teil_gewaehlt=teil_wunsch)

    def diagrammformat_sichtbar(self) -> bool:
        return self.format_sichtbar("diagramm")

    def aktualisiere_diagrammformat(self, werte: dict) -> None:
        self.aktualisiere_format("diagramm", werte)

    def zeige_smartartformat(self, werte: dict, anwenden, bild_wunsch=None) -> None:
        self.zeige_format("smartart", werte, geaendert=anwenden, bild_gewuenscht=bild_wunsch)

    def zusatz_ausfuehren(self, d) -> bool:
        """Ein Zusatzfenster als Seite hier in der Seitenleiste zeigen, solange man es bearbeitet (wie ``d.exec()``). Die Breite bleibt."""
        from lunivo_writer.ui.baukasten.controls.zusatz_panel import ZusatzPanel, ausfuehren_in
        if getattr(self, "_zusatz", None) is not None:                       # es ist schon eines offen: das neue legt sich als Seite darüber
            return self._zusatz.unter_ausfuehren(d)
        seite = ZusatzPanel()
        seite.verfuegbar = max(300, self.width()) - 36                      # Seitenleiste ohne Ränder und Rollbalken
        seite.verfuegbar_hoehe = max(300, self.height() - 140)                      # ohne Kopf und Knopfzeile
        self._zusatz = seite
        i = self.stapel.addWidget(seite)
        vorher = (self.stapel.currentIndex(), self.isHidden())

        def zeigen() -> None:
            if self.isHidden():
                self.show()
            self.stapel.setCurrentIndex(i)
            self.bereich_geaendert.emit(i)

        def zurueck() -> None:
            self.stapel.setCurrentIndex(vorher[0])
            self.stapel.removeWidget(seite); seite.deleteLater()
            self._zusatz = None
            if vorher[1]:
                self.hide()
            self.bereich_geaendert.emit(vorher[0])
            t = self.fenster.current_tab() if hasattr(self.fenster, "current_tab") else None
            if t is not None:
                t.editor.setFocus()                                 # Fenster zu: weiterschreiben, wo man war
        return ausfuehren_in(seite, d, zeigen, zurueck)

    def zeige_bereich(self, i: int) -> None:
        """0 = Schreibhilfe, 1 = KI-Chat."""
        self.stapel.setCurrentIndex(i)
        self.bereich_geaendert.emit(i)

    def setze_bereiche(self, band=None, ki_gruppen=None) -> None:
        """Den KI-Bereich bauen: nur der Chat (Verlauf, Eingabe) — alles andere steht im Reiter Schreibhilfe und im Fenster „KI-Einstellungen“."""
        host = QWidget()
        lay = QVBoxLayout(host)
        lay.setContentsMargins(*RAND_KEIN)                      # Kopf und Ränder bringt der Rahmen des Chats mit
        lay.setSpacing(ABSTAND_MITTEL)
        from lunivo_writer.ui.sidebar.panels.ai_panel import ChatPanel
        self.chat = ChatPanel(self.ki, self.fenster)
        self.chat.zurueck.connect(lambda: self.zeige_bereich(0))
        lay.addWidget(self.chat, 1)
        self._seite_ki.setWidget(host)

    def zeige(self, funde: list) -> None:
        while self.liste.count() > 1:
            it = self.liste.takeAt(0)
            w_ = it.widget()                                  # einmal holen: nach setParent(None) kennt der Eintrag sein Widget nicht mehr
            if w_ is not None:
                w_.hide()
                w_.setParent(None)
                w_.deleteLater()
        if not funde:
            self.meldung = hinweis_label(LEER if self.a._geprueft_rev >= 0 else "Noch nicht geprüft.", zusatz="padding: " f"{PADDING_HINWEIS}" ";")
            self.liste.insertWidget(0, self.meldung)
        for i, f in enumerate(funde):
            self.liste.insertWidget(i, FundKarte(f, self.a, dienst=getattr(self, "ki", None)))
        self.alle.setVisible(any(f.art == "fehler" and f.neu for f in funde))
        for w in self._einfuehrung:                                 # mit Funden steht die Liste ganz oben, wie in der ersten Fassung
            w.setVisible(not funde)

    def _alle(self):
        n = self.a.alle_aendern()
        self.a.status.emit(f"{n} Korrektur(en) übernommen.")

    def welche_hilfe(self):
        from lunivo_writer.ui.dialogs.welche_hilfe import HilfeWannDialog
        HilfeWannDialog(self.fenster).exec()
