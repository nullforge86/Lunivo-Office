"""Die vier Hauptbereiche des Dashboards (Dokumente · Prüfung · Ergebnisse · Fehlerbericht) und ihre kleinen gemeinsamen Bausteine.

Dieses Modul ordnet nur an und zeigt an: Prüflogik, Datenbank, Warteschlange und Renderingfunktionen bleiben unverändert und kommen von den bestehenden Komponenten. Alle Zahlen stammen aus
den tatsächlich gespeicherten Ergebnissen bzw. dem Stand der Prüfwarteschlange."""
from __future__ import annotations

from kompatibilitaetspruefer.oberflaeche.layout import RasterSpalte, RasterZeile
from html import escape as esc

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QButtonGroup, QFrame, QHeaderView, QLabel, QListWidget, QMenu, QProgressBar, QPushButton, QScrollArea,
    QStackedWidget, QTableView, QTableWidget, QTableWidgetItem, QToolButton, QWidget, QComboBox, QLineEdit,
)

from kompatibilitaetspruefer.oberflaeche.modelle import FARBEN, REF_NAMEN, FilterKnopf, FilterProxy, TabellenModell
from kompatibilitaetspruefer.oberflaeche.layout import FlussLayout
from kompatibilitaetspruefer.pruefung import klassifikation as K
from kompatibilitaetspruefer.oberflaeche.layout import (
    ABSTAND_SPALTE,
    ABSTAND_NORMAL,
    textzeile,
    ABSTAND_BLOCK, ABSTAND_ENG, ABSTAND_GROSS, ABSTAND_KLEIN, ABSTAND_MITTEL, BREITEN_SPALTEN_ERGEBNISLISTE,
    BREITE_NAVIGATION, FARBEN, HOEHE_AKTIVITAET_MIN, HOEHE_ARTEN_MAX, HOEHE_ARTEN_MIN, HOEHE_BALKEN,
    HOEHE_DATEIEN_MIN, HOEHE_DETAIL_KOPF_MAX, HOEHE_NAV_KNOPF, HOEHE_REFERENZ_MAX, HOEHE_ZEILE_ERGEBNISLISTE, Kachelzeile,
    RAND_KEIN, RAND_KENNZAHL, RAND_NAVIGATION, RAND_PRUEFUNG, RAND_SEITE, SCHRIFT_PLUS_KENNZAHL,
    SCHRIFT_PLUS_NAVIGATION, SCHRIFT_PLUS_PRUEFTITEL, SCHRIFT_PLUS_PRUEFZEILE, SCHRIFT_PLUS_SEITENTITEL, STIL_HINWEIS, STIL_HTML_GROSS,
    STIL_KLEIN, schrift_stufe, stil_farbe,
)

STATUS_FILTER = (K.BESTANDEN, K.TEILWEISE, K.AUFFAELLIG, K.FEHLGESCHLAGEN, "nicht_pruefbar", K.ABGEBROCHEN)
_STATUS_RANG = {K.FEHLGESCHLAGEN: 0, K.AUFFAELLIG: 1, K.TEILWEISE: 2, "nicht_pruefbar": 3, K.ABGEBROCHEN: 4, K.BESTANDEN: 5, K.OFFEN: 6}


def zahl(n: int) -> str:
    """1103 → „1.103“ (deutsche Tausendertrennung)."""
    return f"{n:,}".replace(",", ".")


def kurz(text: str, n: int = 110) -> str:
    text = " ".join(str(text or "").split())
    return text if len(text) <= n else text[: n - 1] + "…"


def seitentitel(text: str, untertitel: str = "") -> QWidget:
    w = QWidget()
    l = RasterSpalte(w)
    l.setContentsMargins(*RAND_KEIN)
    l.setSpacing(ABSTAND_ENG)
    t = QLabel(text)
    schrift_stufe(t, SCHRIFT_PLUS_SEITENTITEL, fett=True)
    l.addWidget(t)
    if untertitel:
        u = QLabel(untertitel)
        u.setWordWrap(True)
        u.setStyleSheet(STIL_HINWEIS)
        l.addWidget(u)
    return w


class Kennzahl(QFrame):
    """Eine Kennzahl mit Beschriftung."""

    def __init__(self, beschriftung: str, farbe: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("karte")
        self.wert = QLabel("0")
        schrift_stufe(self.wert, SCHRIFT_PLUS_KENNZAHL, fett=True)
        self.wert.setAlignment(Qt.AlignCenter)
        if farbe:
            self.wert.setStyleSheet(stil_farbe(farbe))
        text = QLabel(beschriftung)
        text.setAlignment(Qt.AlignCenter)
        text.setWordWrap(True)
        text.setStyleSheet(STIL_KLEIN)
        l = RasterSpalte(self)
        l.setContentsMargins(*RAND_KENNZAHL)
        l.setSpacing(ABSTAND_ENG)
        l.addWidget(self.wert)
        l.addWidget(text)

    def setze(self, n: int) -> None:
        self.wert.setText(zahl(n))


class Aufklapper(QWidget):
    """Aufklappbarer Bereich: erst bei Bedarf sichtbar, damit die Hauptansicht ruhig bleibt."""

    def __init__(self, titel: str, inhalt: QWidget, offen: bool = False, parent=None):
        super().__init__(parent)
        self.titel = titel
        self.inhalt = inhalt
        self.knopf = QToolButton()
        self.knopf.setCheckable(True)
        self.knopf.setChecked(offen)
        self.knopf.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.knopf.setAutoRaise(True)
        self.knopf.setText(("▾ " if offen else "▸ ") + titel)
        inhalt.setVisible(offen)
        self.knopf.toggled.connect(self._umschalten)
        l = RasterSpalte(self)
        l.setContentsMargins(*RAND_KEIN)
        l.setSpacing(ABSTAND_ENG)
        l.addWidget(self.knopf, 0, Qt.AlignLeft)
        l.addWidget(inhalt)

    def _umschalten(self, an: bool) -> None:
        self.inhalt.setVisible(an)
        self.knopf.setText(("▾ " if an else "▸ ") + self.titel)


class Navigation(QFrame):
    """Schmale Seitenleiste mit den vier Hauptbereichen."""
    gewaehlt = Signal(int)

    def __init__(self, eintraege: list[str], parent=None):
        super().__init__(parent)
        self.setObjectName("navigation")
        self.setFixedWidth(BREITE_NAVIGATION)
        lay = RasterSpalte(self)
        lay.setContentsMargins(*RAND_NAVIGATION)
        lay.setSpacing(ABSTAND_KLEIN)
        titel = QLabel("Lunivo\nCompatibility Tester")
        schrift_stufe(titel, SCHRIFT_PLUS_NAVIGATION, fett=True)
        lay.addWidget(titel)
        lay.addSpacing(ABSTAND_SPALTE)
        self.gruppe = QButtonGroup(self)
        self.gruppe.setExclusive(True)
        self.knoepfe: list[QPushButton] = []
        for i, text in enumerate(eintraege):
            b = QPushButton(text)
            b.setObjectName("nav")
            b.setCheckable(True)
            b.setMinimumHeight(HOEHE_NAV_KNOPF)
            self.gruppe.addButton(b, i)
            self.knoepfe.append(b)
            lay.addWidget(b)
        self.gruppe.idClicked.connect(self.gewaehlt)
        lay.addStretch(1)
        self.status = QLabel("Bereit")
        self.status.setWordWrap(True)
        self.status.setStyleSheet(STIL_HINWEIS)
        lay.addWidget(self.status)

    def waehle(self, i: int) -> None:
        if 0 <= i < len(self.knoepfe):
            self.knoepfe[i].setChecked(True)

    def vor_status(self, widget: QWidget) -> None:
        """Fügt ein Bedienelement unten in der Leiste ein, direkt über der Statusanzeige."""
        self.layout().insertWidget(self.layout().count() - 1, widget)


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
class DokumenteSeite(QWidget):
    """Vorbereitung einer Prüfung: Dokumente laden, Referenzen, Prüfung einrichten."""

    def _auswahlknopf(self, text: str, name: str, tipp: str) -> QToolButton:
        """Knopf mit zwei Wahlmöglichkeiten: einzelne Dateien oder ganzen Ordner."""
        k = QToolButton()
        k.setText(text)
        k.setObjectName(name)
        k.setToolTip(tipp)
        k.setPopupMode(QToolButton.InstantPopup)
        k.setMenu(QMenu(k))
        k.dateien_aktion = k.menu().addAction("Einzelne Dateien auswählen …")
        k.ordner_aktion = k.menu().addAction("Ganzen Ordner auswählen …")
        return k

    def __init__(self, dateien: QWidget, referenz: QWidget, einrichten: QWidget, parent=None):
        super().__init__(parent)
        self.b_dateien = self._auswahlknopf("＋  Dokumente hinzufügen", "haupt", "Word-, ODT-, RTF-Dateien … zur Prüfliste hinzufügen")
        self.b_ref = self._auswahlknopf("📄  PDF-Referenzen hinzufügen", "haupt2", "PDFs aus Word, LibreOffice oder ONLYOFFICE als Vergleichsvorlage; Zuordnung über gleichen Dateinamen")
        self.b_entfernen = QPushButton("Auswahl entfernen")
        self.b_entfernen.setToolTip("Entfernt die markierten Dokumente aus der Liste (die Dateien selbst bleiben unverändert)")
        self.info = QLabel("Noch keine Dokumente.")
        self.info.setWordWrap(True)
        zeile = FlussLayout(ABSTAND_GROSS)
        for w in (self.b_dateien, self.b_ref):
            zeile.addWidget(w)
        inforeihe = RasterZeile()
        inforeihe.addWidget(self.info, 1)
        inforeihe.addWidget(self.b_entfernen)
        bereich = QScrollArea()
        bereich.setWidget(referenz)
        bereich.setWidgetResizable(True)
        bereich.setMaximumHeight(HOEHE_REFERENZ_MAX)
        bereich.setFrameShape(QFrame.NoFrame)
        dateien.setMinimumHeight(HOEHE_DATEIEN_MIN)
        inhalt = QWidget()                                                       # bei kleinem Fenster scrollt die ganze Seite, statt dass etwas zusammengequetscht wird
        lay = RasterSpalte(inhalt)
        lay.setContentsMargins(*RAND_SEITE)
        lay.setSpacing(ABSTAND_GROSS)
        lay.addWidget(seitentitel("Dokumente", "Wählen Sie die Dokumente für die Prüfung. Dateien und Ordner lassen sich auch einfach in dieses Fenster ziehen."))
        lay.addLayout(zeile)
        lay.addLayout(inforeihe)
        lay.addWidget(dateien, 1)
        lay.addWidget(Aufklapper("Details und Referenz des markierten Dokuments", bereich))
        lay.addWidget(einrichten)
        aussen = QScrollArea()
        aussen.setWidget(inhalt)
        aussen.setWidgetResizable(True)
        aussen.setFrameShape(QFrame.NoFrame)
        a = RasterSpalte(self)
        a.setContentsMargins(*RAND_KEIN)
        a.addWidget(aussen)

    def setze_info(self, text: str) -> None:
        self.info.setText(text)


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
class PruefungSeite(QWidget):
    """Ruhige Fortschrittsansicht: große Anzeige, Zähler, laufende Kurzbilanz und eine optionale Aktivitätsliste."""
    ergebnisse_gewuenscht = Signal()

    TITEL = {"bereit": "Bereit zur Prüfung", "laeuft": "Dokumentprüfung läuft", "abbrechend": "Prüfung wird abgebrochen …", "abgebrochen": "Prüfung abgebrochen",
             "erfolgreich": "Prüfung abgeschlossen", "fehler": "Prüfung abgeschlossen – mit Fehlern"}

    def __init__(self, start: QPushButton, stopp: QPushButton, parent=None):
        super().__init__(parent)
        self.titel = QLabel(self.TITEL["bereit"])
        schrift_stufe(self.titel, SCHRIFT_PLUS_PRUEFTITEL, fett=True)
        self.zeile = textzeile("")
        schrift_stufe(self.zeile, SCHRIFT_PLUS_PRUEFZEILE)
        self.balken = QProgressBar()
        self.balken.setRange(0, 1)
        self.balken.setValue(0)
        self.balken.setMinimumHeight(HOEHE_BALKEN)
        self.balken.setTextVisible(True)
        self.zaehler = QLabel("")
        self.aktuell = QLabel("")
        self.aktuell.setWordWrap(True)
        self.karten = {"ok": Kennzahl("Bisher ohne Abweichung", FARBEN["bestanden"]), "auffaellig": Kennzahl("Auffällige Dokumente", FARBEN["auffaellig"]),
                       "fehler": Kennzahl("Fehlgeschlagene Dokumente", FARBEN["fehlgeschlagen"]), "teil": Kennzahl("Noch nicht abschließend bewertet", FARBEN["teilweise"])}
        karten = Kachelzeile()
        for k in self.karten.values():
            karten.hinzu(k)
        self.hinweis = QLabel("")
        self.hinweis.setWordWrap(True)
        self.hinweis.setStyleSheet(STIL_HINWEIS)
        self.b_ergebnisse = QPushButton("Ergebnisse ansehen")
        self.b_ergebnisse.setEnabled(False)
        self.b_ergebnisse.clicked.connect(self.ergebnisse_gewuenscht)
        knoepfe = RasterZeile()
        for b in (start, stopp, self.b_ergebnisse):
            knoepfe.addWidget(b)
        knoepfe.addStretch(1)
        self.liste = QListWidget()
        self.liste.setMinimumHeight(HOEHE_AKTIVITAET_MIN)
        self.aufklapper = Aufklapper("Aktivität anzeigen", self.liste)
        lay = RasterSpalte(self)
        lay.setContentsMargins(*RAND_PRUEFUNG)
        lay.setSpacing(ABSTAND_BLOCK)
        lay.addWidget(self.titel)
        lay.addWidget(self.zeile)
        lay.addWidget(self.balken)
        lay.addWidget(self.zaehler)
        lay.addWidget(self.aktuell)
        lay.addSpacing(ABSTAND_NORMAL)
        lay.addLayout(knoepfe)
        lay.addSpacing(ABSTAND_GROSS)
        lay.addWidget(karten)
        lay.addWidget(self.hinweis)
        lay.addWidget(self.aufklapper)
        lay.addStretch(1)

    def zeige(self, zustand: str, s: dict, hat_dokumente: bool) -> None:
        """``s``: Stand der Prüfwarteschlange (gesamt, fertig, offen, aktuell …) — die Anzeige beruht nur auf diesen Werten."""
        self.titel.setText(self.TITEL.get(zustand, ""))
        gesamt, fertig = int(s.get("gesamt", 0)), int(s.get("fertig", 0))
        self.balken.setRange(0, max(1, gesamt))
        self.balken.setValue(min(fertig, max(1, gesamt)))
        if gesamt:
            self.zeile.setText(f"{zahl(fertig)} von {zahl(gesamt)} Dokumenten verarbeitet")
            self.zaehler.setText(f"Gesamt: {zahl(gesamt)} · Verarbeitet: {zahl(fertig)} · Noch offen: {zahl(int(s.get('offen', max(0, gesamt - fertig))))}")
        else:
            self.zeile.setText("Noch keine Prüfung gestartet." if hat_dokumente else "Noch keine Dokumente geladen – im Bereich „Dokumente“ hinzufügen.")
            self.zaehler.setText("")
        aktuell = ", ".join(s.get("aktuell", [])[:3]) + (" …" if len(s.get("aktuell", [])) > 3 else "")
        self.aktuell.setText(f"Aktuell geprüft: {aktuell}" if aktuell and zustand in ("laeuft", "abbrechend") else "")

    def setze_zaehler(self, stati: dict) -> None:
        """``stati``: Datei-Id → Statusliste ihrer Prüfarten. Getrennt gezählt: verarbeitete Dokumente, vollständig geprüfte (bestanden/auffällig), teilweise geprüfte und einzelne Prüfart-Ergebnisse."""
        zaehl: dict[str, int] = {}
        for v in stati.values():
            g = K.gesamt_status(v)
            zaehl[g] = zaehl.get(g, 0) + 1
        ok, au, fe = zaehl.get(K.BESTANDEN, 0), zaehl.get(K.AUFFAELLIG, 0), zaehl.get(K.FEHLGESCHLAGEN, 0)
        teil = zaehl.get(K.TEILWEISE, 0) + zaehl.get("nicht_pruefbar", 0)
        verarbeitet = sum(n for g, n in zaehl.items() if g not in (K.OFFEN, K.ABGEBROCHEN))
        self.karten["ok"].setze(ok)
        self.karten["auffaellig"].setze(au)
        self.karten["fehler"].setze(fe)
        self.karten["teil"].setze(teil)
        self.hinweis.setText(f"Verarbeitet: {zahl(verarbeitet)} Dokumente · davon vollständig geprüft (bestanden oder auffällig): {zahl(ok + au)} · teilweise geprüft: {zahl(teil)} · "
                             f"fehlgeschlagen: {zahl(fe)} · einzelne Prüfart-Ergebnisse insgesamt: {zahl(sum(len(v) for v in stati.values()))}")
        self.b_ergebnisse.setEnabled(verarbeitet > 0)

    def aktivitaet(self, text: str) -> None:
        self.liste.insertItem(0, text)
        while self.liste.count() > 300:
            self.liste.takeItem(self.liste.count() - 1)

    def leeren(self) -> None:
        self.liste.clear()
        self.setze_zaehler({})


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
class ErgebnisSeite(QWidget):
    """Ergebnisse: Kurzbilanz, Dokumentliste (ein Dokument = eine Zeile), Detailseite zum gewählten Dokument und die große Vergleichsansicht — jeweils als eigene Seite, nie nebeneinander gequetscht."""
    gewaehlt = Signal(dict)                  # Ergebniszeile (Datei × Prüfart), für die Detailansicht
    vergleich_gewuenscht = Signal(dict)

    def __init__(self, db, details: QWidget, vergleich: QWidget, parent=None):
        super().__init__(parent)
        self.db = db
        self.details = details
        self._art_zeilen: list[dict] = []
        self._doc_id: int | None = None
        self._sig: tuple = ()
        self._fuellt = False
        self.stack = QStackedWidget()

        # --- Seite 0: Liste
        self.karten = {"geprueft": Kennzahl("Geprüfte Dokumente"), "bestanden": Kennzahl("Ohne festgestellte Abweichung", FARBEN["bestanden"]),
                       "auffaellig": Kennzahl("Auffällige Dokumente", FARBEN["auffaellig"]), "fehlgeschlagen": Kennzahl("Fehlgeschlagene Dokumente", FARBEN["fehlgeschlagen"]),
                       "teilweise": Kennzahl("Nicht vollständig prüfbar", FARBEN["teilweise"])}
        karten = Kachelzeile()
        for k in self.karten.values():
            karten.hinzu(k)
        self.modell = TabellenModell([("Dokument", "name"), ("Format", "format"), ("Ergebnis", "status"), ("Wichtigster festgestellter Fehler", "fehler")])
        self.proxy = FilterProxy(self)
        self.proxy.setSourceModel(self.modell)
        self.suche = QLineEdit()
        self.suche.setPlaceholderText("Dokument suchen …")
        self.suche.setClearButtonEnabled(True)
        self.suche.textChanged.connect(self._suche)
        self.f = {"endung": QComboBox(), "status": QComboBox(), "fehlerart": QComboBox(), "schwere": QComboBox(), "programm": QComboBox()}
        for schl, name in (("endung", "Alle Formate"), ("status", "Alle Ergebnisse"), ("fehlerart", "Alle Fehlerarten"), ("schwere", "Alle Schweregrade"), ("programm", "Alle Programme")):
            self.f[schl].addItem(name, "")
            self.f[schl].currentIndexChanged.connect(self._filter)
        for s in STATUS_FILTER:
            self.f["status"].addItem(K.STATUS_NAMEN.get(s, s), s)
        for a in K.FEHLERARTEN:
            self.f["fehlerart"].addItem(a, a)
        for s in K.SCHWEREN:
            self.f["schwere"].addItem(s, s)
        self.filterknopf = FilterKnopf([("Format", self.f["endung"]), ("Ergebnis", self.f["status"]), ("Fehlerart", self.f["fehlerart"]), ("Schweregrad", self.f["schwere"]),
                                        ("Ursprungsprogramm", self.f["programm"])])
        such = RasterZeile()
        such.addWidget(self.suche, 1)
        such.addWidget(self.filterknopf)
        self.tabelle = QTableView()
        self.tabelle.setModel(self.proxy)
        self.tabelle.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabelle.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabelle.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabelle.setAlternatingRowColors(True)
        self.tabelle.setShowGrid(False)
        self.tabelle.verticalHeader().setVisible(False)
        self.tabelle.verticalHeader().setDefaultSectionSize(HOEHE_ZEILE_ERGEBNISLISTE)
        self.tabelle.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tabelle.horizontalHeader().setStretchLastSection(True)
        for spalte, breite in enumerate(BREITEN_SPALTEN_ERGEBNISLISTE):
            self.tabelle.setColumnWidth(spalte, breite)
        self.tabelle.clicked.connect(self._angeklickt)
        self.anzahl = QLabel("")
        self.anzahl.setStyleSheet(STIL_HINWEIS)
        liste = QWidget()
        ll = RasterSpalte(liste)
        ll.setContentsMargins(*RAND_KEIN)
        ll.setSpacing(ABSTAND_GROSS)
        ll.addWidget(karten)
        ll.addLayout(such)
        ll.addWidget(self.tabelle, 1)
        ll.addWidget(self.anzahl)

        # --- Seite 1: Details eines Dokuments
        self.b_zurueck = QPushButton("←  Zur Ergebnisliste")
        self.b_zurueck.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.b_vergleich = QPushButton("Dokumentvergleich öffnen")
        self.b_vergleich.setObjectName("haupt")
        self.b_vergleich.clicked.connect(self._vergleich_klick)
        self.doc_kopf = QLabel("")
        self.doc_kopf.setWordWrap(True)
        self.doc_kopf.setTextFormat(Qt.RichText)
        self.art_tabelle = QTableWidget(0, 5)
        self.art_tabelle.setHorizontalHeaderLabels(["Prüfart", "Ergebnis", "Fehlerart", "Schwere", "Hinweis"])
        self.art_tabelle.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.art_tabelle.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.art_tabelle.setSelectionMode(QAbstractItemView.SingleSelection)
        self.art_tabelle.verticalHeader().setVisible(False)
        self.art_tabelle.horizontalHeader().setStretchLastSection(True)
        self.art_tabelle.setMinimumHeight(HOEHE_ARTEN_MIN)
        self.art_tabelle.setMaximumHeight(HOEHE_ARTEN_MAX)
        self.art_tabelle.itemSelectionChanged.connect(self._art_gewaehlt)
        if hasattr(details, "knopf"):
            details.knopf.setVisible(False)                         # der Vergleich wird oben auf der Seite angeboten
        if hasattr(details, "kopf"):
            details.kopf.setMaximumHeight(HOEHE_DETAIL_KOPF_MAX)
        detail = QWidget()
        dl = RasterSpalte(detail)
        dl.setContentsMargins(*RAND_KEIN)
        dl.setSpacing(ABSTAND_MITTEL)
        oben = RasterZeile()
        oben.addWidget(self.b_zurueck)
        oben.addStretch(1)
        oben.addWidget(self.b_vergleich)
        dl.addLayout(oben)
        dl.addWidget(self.doc_kopf)
        dl.addWidget(self.art_tabelle)
        dl.addWidget(details, 1)

        # --- Seite 2: Vergleich in voller Breite
        self.b_zurueck2 = QPushButton("←  Zurück zu den Details")
        self.b_zurueck2.clicked.connect(lambda: self.stack.setCurrentIndex(1 if self._doc_id is not None else 0))
        seite = QWidget()
        vl = RasterSpalte(seite)
        vl.setContentsMargins(*RAND_KEIN)
        kopf2 = RasterZeile()
        kopf2.addWidget(self.b_zurueck2)
        kopf2.addStretch(1)
        vl.addLayout(kopf2)
        vl.addWidget(vergleich, 1)
        for w in (liste, detail, seite):
            self.stack.addWidget(w)
        lay = RasterSpalte(self)
        lay.setContentsMargins(*RAND_SEITE)
        lay.setSpacing(ABSTAND_GROSS)
        lay.addWidget(seitentitel("Ergebnisse", "Wählen Sie ein Dokument, um Einzelheiten und den Seitenvergleich zu sehen."))
        lay.addWidget(self.stack, 1)

    # ---- Filter ---------------------------------------------------------------------------------------------------------
    def _suche(self, t: str) -> None:
        self.proxy.setze_suche(t)
        self._zaehl()

    def _filter(self) -> None:
        self.proxy.setze_filter(**{k: c.currentData() for k, c in self.f.items()})
        self._zaehl()

    def _zaehl(self) -> None:
        self.anzahl.setText(f"{zahl(self.proxy.rowCount())} von {zahl(self.modell.rowCount())} Dokumenten")

    def _combo_nachfuellen(self, schl: str, werte: list, name) -> None:
        c = self.f[schl]
        aktuell = c.currentData()
        c.blockSignals(True)
        c.clear()
        c.addItem({"endung": "Alle Formate", "programm": "Alle Programme"}[schl], "")
        for w in werte:
            c.addItem(name(w), w)
        c.setCurrentIndex(max(0, c.findData(aktuell)))
        c.blockSignals(False)
        self.filterknopf.aktualisieren()

    # ---- Daten ----------------------------------------------------------------------------------------------------------
    def sichtbare_ergebnisse(self) -> list[dict]:
        """Ergebniszeilen (Datei × Prüfart) der Dokumente, die der Filter gerade zeigt — für den Export."""
        sichtbar = {z["datei_id"] for z in self.proxy.zeilen_sichtbar()}
        return [r for r in self._art_zeilen if r["datei_id"] in sichtbar]

    def setze(self, dateien: list[dict], dateistatus: dict[int, list[str]], zeilen: list[dict]) -> None:
        for z in zeilen:
            z["format"] = z["endung"].lstrip(".").upper()
        self._art_zeilen = zeilen
        je_datei: dict[int, list[dict]] = {}
        for z in zeilen:
            je_datei.setdefault(z["datei_id"], []).append(z)
        docs = []
        for d in dateien:
            rs = je_datei.get(d["id"])
            if not rs:
                continue
            status = K.gesamt_status(dateistatus.get(d["id"], []))
            schlecht = [r for r in rs if r["status"] in (K.AUFFAELLIG, K.FEHLGESCHLAGEN)]
            worst = min(schlecht, key=lambda r: (0 if r["status"] == K.FEHLGESCHLAGEN else 1, K.SCHWERE_RANG.get(r["schwere"], 9))) if schlecht else None
            if worst is not None:
                fehler = f"{K.PRUEFART_NAMEN.get(worst['art'], worst['art'])}: {worst['fehlerart'] or K.STATUS_NAMEN.get(worst['status'], '')} – {kurz(worst['beschreibung'])}"
            else:
                hinweis = [r for r in rs if r["status"] in (K.TEILWEISE, "nicht_pruefbar")]
                fehler = ("Nicht vollständig prüfbar: " + kurz(hinweis[0]["beschreibung"])) if hinweis else "–"
            docs.append({"datei_id": d["id"], "name": d["name"], "pfad": d["pfad"], "endung": d["endung"], "format": d["endung"].lstrip(".").upper(), "status": status,
                         "fehler": fehler, "beschreibung": fehler, "fehlerart": worst["fehlerart"] if worst else "", "schwere": worst["schwere"] if worst else "",
                         "programm": d["programm"]})
        docs.sort(key=lambda x: (_STATUS_RANG.get(x["status"], 9), K.SCHWERE_RANG.get(x["schwere"], 9), x["name"].casefold()))
        self.modell.setze(docs)
        self._combo_nachfuellen("endung", sorted({z["endung"] for z in docs}), lambda e: e.lstrip(".").upper())
        self._combo_nachfuellen("programm", sorted({z["programm"] for z in docs if z["programm"]}), str)
        stati = [x["status"] for x in docs]
        verarbeitet = [s for s in stati if s not in (K.OFFEN, K.ABGEBROCHEN)]
        self.karten["geprueft"].setze(len(verarbeitet))
        self.karten["bestanden"].setze(stati.count(K.BESTANDEN))
        self.karten["auffaellig"].setze(stati.count(K.AUFFAELLIG))
        self.karten["fehlgeschlagen"].setze(stati.count(K.FEHLGESCHLAGEN))
        self.karten["teilweise"].setze(stati.count(K.TEILWEISE) + stati.count("nicht_pruefbar"))
        self._zaehl()
        if self._doc_id is not None and self.stack.currentIndex() == 1:
            self._art_tabelle_fuellen(aktualisierung=True)

    # ---- Detailseite ------------------------------------------------------------------------------------------------------
    def _angeklickt(self, index) -> None:
        z = self.proxy.data(index, Qt.UserRole)
        if z:
            self.zeige_dokument(z["datei_id"])

    def zeige_dokument(self, datei_id: int) -> None:
        self._doc_id = datei_id
        self._sig = ()
        self._art_tabelle_fuellen(aktualisierung=False)
        self.stack.setCurrentIndex(1)

    def _zeilen_des_dokuments(self) -> list[dict]:
        return sorted((r for r in self._art_zeilen if r["datei_id"] == self._doc_id), key=lambda r: list(K.PRUEFART_NAMEN).index(r["art"]) if r["art"] in K.PRUEFART_NAMEN else 99)

    def _art_tabelle_fuellen(self, aktualisierung: bool) -> None:
        rs = self._zeilen_des_dokuments()
        sig = tuple((r["art"], r["status"], r["ergebnis_id"]) for r in rs)
        if aktualisierung and sig == self._sig:
            return
        self._sig = sig
        if not rs:
            self.doc_kopf.setText("<i>Für dieses Dokument liegen keine Ergebnisse mehr vor.</i>")
            self.art_tabelle.setRowCount(0)
            return
        aktuell = self.art_tabelle.currentRow()
        ausgewaehlt_art = self._last[aktuell]["art"] if aktualisierung and 0 <= aktuell < len(self._last) else None
        self._last = rs
        erste = rs[0]
        status = K.gesamt_status([r["status"] for r in rs])
        schlecht = [r for r in rs if r["status"] in (K.AUFFAELLIG, K.FEHLGESCHLAGEN)]
        seiten = sorted({int(r["seite"]) for r in rs if r.get("seite")})
        farbe = FARBEN.get(status, "")
        self.doc_kopf.setText(
            f"<span style='{STIL_HTML_GROSS}'><b>{esc(erste['name'])}</b></span><br>"
            f"Format: <b>{esc(erste['format'])}</b> &nbsp;·&nbsp; Gesamtergebnis: <b style='color:{farbe}'>{esc(K.STATUS_NAMEN.get(status, status))}</b> &nbsp;·&nbsp; "
            f"Referenz: <b>{esc(REF_NAMEN.get(erste['referenz'], erste['referenz']))}</b><br>"
            f"Erkannte Fehler: <b>{len(schlecht)}</b> &nbsp;·&nbsp; Betroffene Seiten: <b>{esc(', '.join(str(s) for s in seiten[:12])) if seiten else 'keine bestimmte Seite'}</b>")
        self._fuellt = True
        t = self.art_tabelle
        t.setRowCount(len(rs))
        for r, z in enumerate(rs):
            werte = (K.PRUEFART_NAMEN.get(z["art"], z["art"]), K.STATUS_NAMEN.get(z["status"], z["status"]), z["fehlerart"] or "–", z["schwere"], kurz(z["beschreibung"], 140))
            for c, w in enumerate(werte):
                it = QTableWidgetItem(str(w))
                it.setToolTip(z["beschreibung"])
                if c == 1 and z["status"] in FARBEN:
                    it.setForeground(self._farbe(z["status"]))
                t.setItem(r, c, it)
        t.resizeColumnsToContents()
        t.horizontalHeader().setStretchLastSection(True)
        self._fuellt = False
        wahl = next((i for i, z in enumerate(rs) if z["art"] == ausgewaehlt_art), None)
        if wahl is None:
            wahl = next((i for i, z in enumerate(rs) if z["status"] in (K.FEHLGESCHLAGEN, K.AUFFAELLIG)), 0)
        t.selectRow(wahl)

    _last: list[dict] = []

    @staticmethod
    def _farbe(name: str):
        from PySide6.QtGui import QColor
        return QColor(FARBEN[name])

    def _art_gewaehlt(self) -> None:
        if self._fuellt:
            return
        r = self.art_tabelle.currentRow()
        rs = self._last
        if 0 <= r < len(rs):
            self.gewaehlt.emit(rs[r])

    def _vergleich_klick(self) -> None:
        rs = self._zeilen_des_dokuments()
        if not rs:
            return
        layout = next((z for z in rs if z["art"] == "layout"), None)
        r = self.art_tabelle.currentRow()
        self.vergleich_gewuenscht.emit(layout or (rs[r] if 0 <= r < len(rs) else rs[0]))

    def zeige_vergleich(self) -> None:
        self.stack.setCurrentIndex(2)

    def zeige_liste(self) -> None:
        self.stack.setCurrentIndex(0)

    def zuruecksetzen(self) -> None:
        self._doc_id = None
        self._sig = ()
        self._last = []
        self.suche.clear()
        self.filterknopf.zuruecksetzen()
        self.stack.setCurrentIndex(0)


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
class FehlerSeite(QWidget):
    """„Fehlerbericht“: Fehlergruppen, Entwicklung und Vorher/Nachher als drei Umschalter über einer gemeinsamen Fläche (keine zweite Registerleiste)."""

    def __init__(self, fehler: QWidget, verbesserung, parent=None):
        super().__init__(parent)
        self.verbesserung = verbesserung
        verbesserung.tabs.tabBar().hide()
        self.stack = QStackedWidget()
        self.stack.addWidget(fehler)
        self.stack.addWidget(verbesserung)
        self.gruppe = QButtonGroup(self)
        self.gruppe.setExclusive(True)
        self.knoepfe: list[QPushButton] = []
        kopf = RasterZeile()
        for i, text in enumerate(("Fehlergruppen", "Entwicklung", "Vorher / Nachher")):
            b = QPushButton(text)
            b.setObjectName("segment")
            b.setCheckable(True)
            self.gruppe.addButton(b, i)
            self.knoepfe.append(b)
            kopf.addWidget(b)
        kopf.addStretch(1)
        self.knoepfe[0].setChecked(True)
        self.gruppe.idClicked.connect(self.waehle)
        lay = RasterSpalte(self)
        lay.setContentsMargins(*RAND_SEITE)
        lay.setSpacing(ABSTAND_GROSS)
        lay.addWidget(seitentitel("Fehlerbericht", "Der Prüfer behebt nichts selbst. Er fasst die gefundenen Fehler zu Gruppen zusammen; diesen Bericht geben Sie an eine Entwickler-KI oder Entwickler weiter, die Lunivo korrigieren. Danach hier erneut prüfen, ob der Fehler weg ist."))
        lay.addLayout(kopf)
        lay.addWidget(self.stack, 1)

    def waehle(self, i: int) -> None:
        self.knoepfe[i].setChecked(True)
        if i == 0:
            self.stack.setCurrentIndex(0)
        else:
            self.stack.setCurrentIndex(1)
            self.verbesserung.tabs.setCurrentIndex(i - 1)
