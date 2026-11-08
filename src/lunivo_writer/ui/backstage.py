"""Backstage-Ansicht des Reiters „Datei“: links die Befehlsliste, rechts die Seite zum gewählten Befehl.

Das Menü links folgt Kays Vorbild (Bildschirmfoto „Menü“). Befehle ohne eigene Seite (Speichern, Beenden)
führen sofort aus und schließen die Ansicht; PDF- und Bildexport, Neu (Vorlagen), Öffnen (Zuletzt verwendet und Dateiauswahl),
Speichern unter, Drucken, Dokumentverschlüsselung, Hilfe und Optionen zeigen ihre Seite rechts.
"""
from __future__ import annotations

import os

from datetime import datetime

from PySide6.QtCore import QSize, Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QKeySequence, QPainter, QPalette, QPen, QShortcut
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QScrollArea, QStackedWidget,
    QStyledItemDelegate, QToolButton, QVBoxLayout, QWidget,
)

from lunivo_writer.ui.baukasten.medien.datei_symbole import datei_symbol
from lunivo_writer.ui.baukasten.controls.formular_gitter import FormularGitter
from lunivo_writer.ui.widgets import icons

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.controls.spalten import ZweiSpalter
from lunivo_writer.ui.baukasten.basis.mass import (
    ABSTAND_ENG,
    ABSTAND_GROSS,
    ABSTAND_KEIN,
    ABSTAND_KLEIN,
    ABSTAND_MITTEL,
    BREITE_FELD_BACKSTAGE,
    BREITE_FELD_ORT,
    BREITE_NAMENSFELD,
    BREITE_NAVIGATION_BACKSTAGE,
    BREITE_NAVIGATION_OPTIONEN,
    BREITE_ZEILENHINWEIS,
    BREITE_ZEILE_BACKSTAGE,
    GROESSE_KNOPF_MIN,
    HOEHE_ABSTAND_LISTE,
    HOEHE_KNOPF,
    HOEHE_TRENNER_LISTE,
    HOEHE_ZEILE_ZULETZT,
    ICON_GROSS,
    ICON_KACHEL,
    ICON_KLEIN,
    ICON_KNOPF_GROSS,
    ICON_LISTE,
    ICON_NORMAL,
    PADDING_BACKSTAGE_FERTIG,
    PADDING_BACKSTAGE_KNOPF,
    PADDING_BACKSTAGE_ZURUECK,
    PADDING_LINKS_BACKSTAGE_LISTE,
    PADDING_NAVIGATION_EINTRAG,
    RADIUS_FELD,
    RADIUS_KLEIN,
    RAND_BACKSTAGE_SEITE,
    RAND_FUSS_BACKSTAGE,
    RAND_FUSS_RECHTS,
    RAND_KEIN,
    RAND_KOPF_LINKS,
    RAND_LISTENKOPF,
    RAND_ZEILE,
    RAND_ZEILE_BACKSTAGE,
    RAND_ZULETZT_ZEILE,
    SCHRIFT_LISTE,
    SCHRIFT_UEBERSCHRIFT,
    SCHRIFT_UEBERSCHRIFT_KLEIN,
)

# Das Menü links nach Kays Vorbild (Bildschirmfoto „Menü“): große Zeilen mit Liniensymbol, Pfeil bei Einträgen mit eigener Seite.
# (Schlüssel, Beschriftung, Symbol, Art: "seite" | "tun" | "trenner", Seite bzw. Befehl)
EINTRAEGE = [
    ("neu", "Neu", "neu", "seite", "vorlage"),
    ("oeffnen", "Öffnen", "oeffnen", "seite", "zuletzt"),
    ("speichern", "Speichern", "speichern", "tun", "speichern"),
    ("speichern_als", "Speichern unter", "speichern_unter", "seite", "speichern_als"),
    ("pdf", "Als PDF exportieren", "pdf", "seite", "pdf"),
    ("bild", "Als Bild exportieren", "bild", "seite", "bild"),
    ("drucken", "Drucken", "drucken", "seite", "drucken"),
    ("-1", "", "", "trenner", None),
    ("schuetzen", "Dokumentverschlüsselung", "schutz", "seite", "schuetzen"),
    ("-2", "", "", "trenner", None),
    ("hilfe", "Hilfe", "hilfe", "seite", "hilfe"),
    ("optionen", "Optionen", "optionen", "seite", "optionen"),
    ("beenden", "Beenden", "beenden", "tun", "beenden"),
]
MIT_DOKUMENT = ("speichern", "speichern_als", "pdf", "bild", "drucken", "schuetzen")

# Symbolnamen aus dem zentralen Lucide-Katalog.
SYMBOLE = {
    "neu": "file-plus", "oeffnen": "folder-open", "speichern": "save",
    "speichern_unter": "file-pen", "pdf": "file-text", "bild": "image", "drucken": "printer",
    "schutz": "file-lock", "hilfe": "circle-question-mark", "optionen": "settings",
    "beenden": "log-out", "datei": "file-text", "neu_laden": "refresh-cw", "weg": "x",
}


def symbol(name: str, px: int = ICON_LISTE):
    return icons.icon(SYMBOLE[name], px)

class _Zeile(QStyledItemDelegate):
    """Zeichnet die Trennlinien quer über die Liste und den kleinen Pfeil rechts bei Einträgen mit eigener Seite."""

    def paint(self, p: QPainter, opt, idx):
        art = idx.data(ART)
        if art == "trenner":
            p.save()
            p.setPen(QPen(opt.palette.color(QPalette.Mid).lighter(130), 1))
            y = opt.rect.center().y()
            p.drawLine(opt.rect.left(), y, opt.rect.right(), y)
            p.restore()
            return
        super().paint(p, opt, idx)
        if idx.data(PFEIL):
            p.save()
            pm = icons.icon("chevron-right", ICON_KLEIN).pixmap(ICON_KLEIN, ICON_KLEIN)
            p.drawPixmap(opt.rect.right() - 18, opt.rect.center().y() - 7, pm)
            p.restore()


ART, PFEIL = Qt.UserRole + 1, Qt.UserRole + 2
MIT_PFEIL = ("neu", "oeffnen", "speichern_als", "pdf", "bild", "drucken", "schuetzen", "hilfe")

EXPORTE = [("PDF-Dokument (.pdf)", "speichernPdf"), ("Word-Dokument (.docx)", "exportierenDocx"),
           ("OpenDocument-Text (.odt)", "exportierenOdt"),
           ("Rich-Text-Format (.rtf)", "exportierenRtf"), ("Nur Text (.txt)", "exportierenTxt"),
           ("Bild der Seite (.png)", "exportierenPng")]

EXPORT_ENDUNG = {"speichernPdf": ".pdf", "exportierenDocx": ".docx", "exportierenOdt": ".odt",
                 "exportierenRtf": ".rtf", "exportierenTxt": ".txt", "exportierenPng": ".png"}

BREITE = BREITE_ZEILE_BACKSTAGE

def stil() -> str:
    """Stylesheet beim Aufruf formatiert, damit das Thema gilt."""
    return ('\nQWidget#bsLinks { background: palette(window); }\nQListWidget#bsListe { background: transparent; border: none; outline: none; }\nQListWidget#bsListe { font-size: ' f"{SCHRIFT_LISTE}" 'pt; }\nQListWidget#bsListe::item { padding-left: ' f"{PADDING_LINKS_BACKSTAGE_LISTE}" '; border: none; }\nQListWidget#bsListe::item:selected, QListWidget#bsListe::item:hover:enabled { background: palette(midlight); color: palette(window-text); }\nQListWidget#bsListe::item:disabled { color: palette(mid); }\nQLabel#bsZuletzt { font-size: ' f"{SCHRIFT_LISTE}" 'pt; }\nQPushButton#bsDatei { border: none; background: transparent; text-align: left; padding: ' f"{PADDING_NAVIGATION_EINTRAG}" '; border-radius: ' f"{RADIUS_KLEIN}" 'px; }\nQPushButton#bsDatei:hover:enabled { background: palette(midlight); }\nQToolButton#bsKlein { border: none; background: transparent; border-radius: ' f"{RADIUS_KLEIN}" 'px; }\nQToolButton#bsKlein:hover { background: palette(midlight); }\nQWidget#bsRechts, QScrollArea#bsSeite, QScrollArea#bsSeite > QWidget > QWidget { background: palette(base); }\nQLabel#bsTitel { font-size: ' f"{SCHRIFT_UEBERSCHRIFT}" 'pt; }\nQWidget#optLinks { background: palette(window); border-right: 1px solid palette(midlight); }\nQWidget#optKopf { border: none; }\nQPushButton#optZurueck { border: none; background: transparent; font-size: ' f"{SCHRIFT_UEBERSCHRIFT_KLEIN}" 'pt; font-weight: 600; text-align: left; padding: ' f"{PADDING_BACKSTAGE_ZURUECK}" '; }\nQPushButton#optFertig { border: none; border-radius: ' f"{RADIUS_FELD}" 'px; padding: ' f"{PADDING_BACKSTAGE_FERTIG}" '; font-weight: 600; }\nQLabel#bsGruppe { font-size: ' f"{SCHRIFT_LISTE}" 'pt; font-weight: 600; }\nQLabel#bsHinweis { color: palette(mid); }\nQPushButton#bsKnopf { border: none; background: transparent; padding: ' f"{PADDING_BACKSTAGE_KNOPF}" '; text-align: left; border-radius: ' f"{RADIUS_FELD}" 'px; }\nQPushButton#bsKnopf:hover:enabled { background: palette(midlight); }\nQPushButton#bsKnopf:disabled { color: palette(mid); }\n')


class Backstage(QWidget):
    schliessen = Signal()

    def __init__(self, fenster):
        super().__init__()
        self.w = fenster
        self.setStyleSheet(stil())
        links = QWidget()
        links.setObjectName("bsLinks")
        ll = QVBoxLayout(links)
        ll.setContentsMargins(*RAND_LISTENKOPF)
        self.liste = QListWidget()
        self.liste.setObjectName("bsListe")
        self.liste.setIconSize(QSize(ICON_LISTE, ICON_LISTE))
        self.liste.setFocusPolicy(Qt.StrongFocus)
        self.liste.setAccessibleName("Datei-Navigation")
        self.liste.setAccessibleDescription("Mit Pfeiltasten wählen, mit Eingabe öffnen, Esc schließt die Datei-Ansicht")
        self.liste.setItemDelegate(_Zeile(self.liste))
        self.liste.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.liste.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        ll.addWidget(self.liste, 1)
        self._links = links                                          # bei den Optionen ausgeblendet
        self.rechts = QWidget()
        self.rechts.setObjectName("bsRechts")
        rl = QVBoxLayout(self.rechts)
        rl.setContentsMargins(*RAND_KEIN)
        self.stapel = QStackedWidget()
        rl.addWidget(self.stapel)
        # bildschirmbreit: die Menüleiste steht immer links (breit_ab=0 = ohne Umbruch), aber aus dem gemeinsamen Baustein
        self.spalten = ZweiSpalter(links, self.rechts, breit_ab=0, links_breite=BREITE_NAVIGATION_BACKSTAGE)
        lay = QVBoxLayout(self); lay.setContentsMargins(*RAND_KEIN); lay.setSpacing(ABSTAND_KEIN); lay.addWidget(self.spalten)
        self.zeilen: dict[str, QListWidgetItem] = {}
        for schl, text, sym, art, _b in EINTRAEGE:
            it = QListWidgetItem(text)
            it.setData(ART, art)
            it.setData(PFEIL, schl in MIT_PFEIL)
            if art == "trenner":
                it.setFlags(Qt.NoItemFlags)
                it.setSizeHint(QSize(BREITE_ZEILENHINWEIS, HOEHE_TRENNER_LISTE))
                it.setText("")
            else:
                it.setIcon(symbol(sym))
                it.setSizeHint(QSize(BREITE_ZEILENHINWEIS, HOEHE_ABSTAND_LISTE))
            self.zeilen[schl] = it
            self.liste.addItem(it)
        self.liste.itemClicked.connect(self._gewaehlt)
        self.liste.itemActivated.connect(self._aktiviert)
        self.seiten: dict[str, QWidget] = {}
        QShortcut(QKeySequence(Qt.Key_Escape), self, activated=self.schliessen.emit)
        self._frischen_sich_selbst = True

    # ---- Aufbau der Seiten (bei jedem Öffnen frisch, damit Zahlen und Listen stimmen) ----------------------------
    def oeffnen(self, seite: str = "zuletzt", unter: str | None = None):
        """``unter``: bei „optionen“ die Seite der Optionen, die gleich offen sein soll (z. B. „ki“)."""
        self._optionen_unter = unter
        self._links.show()
        while self.stapel.count():
            w = self.stapel.widget(0)
            self.stapel.removeWidget(w)
            w.deleteLater()
        self.seiten.clear()
        haben_dok = self.w.current_tab() is not None
        for schl in MIT_DOKUMENT:
            self.zeilen[schl].setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable if haben_dok else Qt.NoItemFlags)
        bauer = {"zuletzt": self._zuletzt, "speichern_als": self._speichern_als, "drucken": self._drucken, "vorlage": self._vorlage, "pdf": self._pdf,
                 "bild": self._bild, "hilfe": self._hilfe, "schuetzen": self._schuetzen, "info": self._info, "oeffnen_mit": self._oeffnen_mit, "optionen": self._optionen}
        for schl, f in bauer.items():
            seite_w = f()
            self.seiten[schl] = seite_w
            self.stapel.addWidget(seite_w)
        if seite not in self.seiten or (not haben_dok and seite not in ("zuletzt", "optionen")):
            seite = "zuletzt"
        self._zeigen(seite)

    def optionen_seite(self) -> str | None:
        """Schlüssel der Optionenseite, die gerade offen ist (z. B. „ansicht“)."""
        a = getattr(self.seiten.get("optionen"), "_ansicht", None)
        it = a.baum.currentItem() if a is not None else None
        return it.data(0, 0x100) if it is not None else None

    def _optionen(self) -> QWidget:
        """Platzhalter: die Optionen werden erst gebaut, wenn die Seite zum ersten Mal gezeigt wird."""
        ph = QWidget()
        QVBoxLayout(ph).setContentsMargins(*RAND_KEIN)
        ph._ansicht = None
        return ph

    def _optionen_zeigen(self) -> None:
        from lunivo_writer.ui.dialogs.optionen import OptionenAnsicht
        ph = self.seiten["optionen"]
        self._links.hide()                                           # die Optionen füllen die ganze Breite; das Menü ist für die Dauer weg
        if ph._ansicht is None:
            v = ph.layout(); v.setSpacing(ABSTAND_KEIN)                         # keine Lücke zwischen Optionen und Fußleiste: die linke Fläche bleibt ganz
            kopf = QWidget(); kopf.setObjectName("optKopf")
            kh = QHBoxLayout(kopf); kh.setContentsMargins(*RAND_KEIN); kh.setSpacing(ABSTAND_KEIN)
            kopf_links = QWidget(); kopf_links.setObjectName("optLinks"); kopf_links.setFixedWidth(BREITE_NAVIGATION_OPTIONEN)         # die linke Fläche beginnt schon in der Kopfzeile
            kopf_links.setAttribute(Qt.WA_StyledBackground, True)
            kl = QHBoxLayout(kopf_links); kl.setContentsMargins(*RAND_KOPF_LINKS)
            zurueck = QPushButton("Optionen"); zurueck.setIcon(icons.icon("arrow-left", ICON_NORMAL))
            zurueck.setObjectName("optZurueck"); zurueck.setFlat(True); zurueck.setCursor(Qt.PointingHandCursor)
            zurueck.setToolTip("Optionen verlassen")
            zurueck.clicked.connect(self.schliessen)
            kl.addWidget(zurueck); kl.addStretch(1)
            kh.addWidget(kopf_links); kh.addStretch(1)
            ph._ansicht = OptionenAnsicht(self.w, getattr(self, "_optionen_unter", None))
            fuss = QWidget(); fh = QHBoxLayout(fuss); fh.setContentsMargins(*RAND_KEIN); fh.setSpacing(ABSTAND_KEIN)
            unten_links = QWidget(); unten_links.setObjectName("optLinks"); unten_links.setFixedWidth(BREITE_NAVIGATION_OPTIONEN)     # die linke Fläche läuft bis ganz unten durch
            unten_links.setAttribute(Qt.WA_StyledBackground, True)
            rechts_fuss = QHBoxLayout(); rechts_fuss.setContentsMargins(*RAND_FUSS_RECHTS)
            fertig = QPushButton("Fertig"); fertig.setObjectName("optFertig"); fertig.setCursor(Qt.PointingHandCursor)
            fertig.clicked.connect(self.schliessen)
            rechts_fuss.addStretch(1); rechts_fuss.addWidget(fertig)
            fh.addWidget(unten_links); fh.addLayout(rechts_fuss, 1)
            ph._kopf, ph._fertig, ph._zurueck = kopf, fertig, zurueck
            v.addWidget(kopf); v.addWidget(ph._ansicht, 1); v.addWidget(fuss)
        elif getattr(self, "_optionen_unter", None):
            ph._ansicht.gehe_zu(self._optionen_unter)

    def _zeigen(self, schl: str):
        if schl == "optionen":
            self._optionen_zeigen()
        elif schl == "drucken":
            self._drucken_zeigen()
        elif schl == "vorlage":
            self._vorlage_zeigen()
        elif schl == "pdf":
            self._pdf_zeigen()
        elif schl == "bild":
            self._bild_zeigen()
        self.stapel.setCurrentWidget(self.seiten[schl])
        zeile = next((self.zeilen[e[0]] for e in EINTRAEGE if e[3] == "seite" and e[4] == schl), None)
        if zeile is None:
            self.liste.clearSelection()
            self.liste.setCurrentItem(None)
        else:
            self.liste.setCurrentItem(zeile)

    def _aktiviert(self, it: QListWidgetItem):
        """Eingabetaste in der Liste; ein Mausklick meldet sich zugleich über ``itemClicked`` und darf nicht doppelt wirken."""
        if QApplication.mouseButtons() == Qt.NoButton:
            self._gewaehlt(it)

    def _gewaehlt(self, it: QListWidgetItem):
        schl = next(k for k, v in self.zeilen.items() if v is it)
        art, ziel = next((e[3], e[4]) for e in EINTRAEGE if e[0] == schl)
        if art == "seite":
            self._zeigen(ziel)
        elif art == "tun":
            self.schliessen.emit()
            self.w.befehle.tun(ziel)

    def _speicherort(self):
        t = self.w.current_tab()
        if t and t.path and os.path.exists(t.path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(os.path.abspath(t.path))))
        else:
            self.w.statusBar().showMessage("Das Dokument ist noch nicht gespeichert — es gibt noch keinen Speicherort.", 5000)

    # ---- Bausteine -------------------------------------------------------------------------------------------
    def _seite(self, titel: str) -> tuple[QScrollArea, QVBoxLayout]:
        sa = QScrollArea()
        sa.setObjectName("bsSeite")
        sa.setWidgetResizable(True)
        sa.setFrameShape(QFrame.NoFrame)
        inh = QWidget()
        v = QVBoxLayout(inh)
        v.setContentsMargins(*RAND_BACKSTAGE_SEITE)
        v.setSpacing(ABSTAND_MITTEL)
        if titel:
            t = QLabel(titel)
            t.setObjectName("bsTitel")
            v.addWidget(t)
            v.addSpacing(14)
        sa.setWidget(inh)
        return sa, v

    @staticmethod
    def _gruppe(v: QVBoxLayout, text: str, hinweis: str = ""):
        v.addSpacing(8)
        g = QLabel(text)
        g.setObjectName("bsGruppe")
        v.addWidget(g)
        if hinweis:
            h = QLabel(hinweis)
            h.setObjectName("bsHinweis")
            h.setWordWrap(True)
            v.addWidget(h)

    def _knopf(self, v: QVBoxLayout, text: str, befehl: str, icon: str | None = None, schliessen: bool = True,
               datei: str | None = None):
        k = QPushButton(text)
        k.setObjectName("bsKnopf")
        sym = datei_symbol(datei) if datei else None
        if sym is not None and not sym.isNull():                       # eigenes, vollständiges Dateiformatblatt
            k.setIcon(sym); k.setIconSize(QSize(ICON_KNOPF_GROSS, ICON_KNOPF_GROSS))
        elif icon and icons.hat(icon):
            icons.setze(k, icon, ICON_GROSS)
        k.setEnabled(self.w.befehle.hat(befehl))
        k.setCursor(Qt.PointingHandCursor)
        k.setFixedWidth(BREITE)                               # alle Zeilen gleich breit, keine Kästen
        k.clicked.connect(lambda _=False, b=befehl: (self.schliessen.emit() if schliessen else None, self.w.befehle.tun(b)))
        v.addWidget(k)
        return k

    # ---- Seiten ------------------------------------------------------------------------------------------------
    def _zuletzt(self):
        """Rechts neben dem Menü: die zuletzt verwendeten Dateien (Name, Ordner, Datum; ✕ nimmt sie aus der Liste)."""
        sa, v = self._seite("")
        v.setContentsMargins(*RAND_ZEILE_BACKSTAGE)
        v.setSpacing(ABSTAND_ENG)
        kopf = QHBoxLayout()
        t = QLabel("Zuletzt verwendete Dokumente"); t.setObjectName("bsZuletzt")
        oeffnen = QPushButton("Weitere Dokumente öffnen …")
        oeffnen.setObjectName("bsKnopf")
        oeffnen.setIcon(symbol("oeffnen", ICON_GROSS)); oeffnen.setIconSize(QSize(ICON_GROSS, ICON_GROSS))
        oeffnen.setCursor(Qt.PointingHandCursor)
        oeffnen.setToolTip("Datei im Dateiauswahldialog suchen")
        oeffnen.clicked.connect(lambda: (self.schliessen.emit(), self.w.open_dialog()))
        neu = QToolButton(); neu.setObjectName("bsKlein"); neu.setIcon(symbol("neu_laden", ICON_NORMAL)); neu.setIconSize(QSize(ICON_NORMAL, ICON_NORMAL))
        neu.setToolTip("Liste neu laden"); neu.setCursor(Qt.PointingHandCursor)
        neu.clicked.connect(lambda: self.oeffnen("zuletzt"))
        kopf.addWidget(t); kopf.addStretch(1); kopf.addWidget(oeffnen); kopf.addWidget(neu)
        v.addLayout(kopf)
        v.addSpacing(6)
        pfade = self.w.settings.recent()
        if not pfade:
            h = QLabel("Noch keine Dokumente geöffnet.")
            h.setObjectName("bsHinweis")
            v.addWidget(h)
        heim = os.path.expanduser("~")
        for p in pfade:
            zeile = QHBoxLayout(); zeile.setSpacing(ABSTAND_KLEIN)
            k = QPushButton()
            k.setObjectName("bsDatei")
            k.setCursor(Qt.PointingHandCursor)
            ordner = os.path.dirname(p)
            ordner = ("~" + ordner[len(heim):] if ordner.startswith(heim) else ordner) + "/"
            k.setAccessibleName(os.path.basename(p))               # sichtbar sind Name, Ordner und Datum als eigene Zeilen
            k.setToolTip(p)
            sym = datei_symbol(p)                                    # vollständiges, formatspezifisches Blatt
            k.setIcon(sym if not sym.isNull() else symbol("datei", ICON_KACHEL))
            k.setIconSize(QSize(ICON_KACHEL, ICON_KACHEL))
            k.setEnabled(os.path.exists(p))
            k.clicked.connect(lambda _=False, p=p: (self.schliessen.emit(), self.w.open_path(p)))
            text = QVBoxLayout(); text.setSpacing(ABSTAND_KEIN); text.setContentsMargins(*RAND_KEIN)
            name = QLabel(os.path.basename(p)); name.setAttribute(Qt.WA_TransparentForMouseEvents)
            ort = QLabel(ordner); ort.setObjectName("bsHinweis"); ort.setAttribute(Qt.WA_TransparentForMouseEvents)
            ort.setMaximumWidth(BREITE_FELD_ORT)
            ort.setText(ort.fontMetrics().elidedText(ordner, Qt.ElideRight, 380))
            text.addWidget(name); text.addWidget(ort)
            innen = QHBoxLayout(k); innen.setContentsMargins(*RAND_ZULETZT_ZEILE)
            innen.addLayout(text); innen.addStretch(1)
            try:
                datum = datetime.fromtimestamp(os.path.getmtime(p))
                heute = datetime.now().date() == datum.date()
                d = QLabel(("Heute " + datum.strftime("%H:%M")) if heute else datum.strftime("%d.%m. %H:%M"))
            except OSError:
                d = QLabel("")
            d.setObjectName("bsHinweis"); d.setAttribute(Qt.WA_TransparentForMouseEvents)
            innen.addWidget(d)
            k.setMinimumHeight(HOEHE_ZEILE_ZULETZT)
            weg = QToolButton(); weg.setObjectName("bsKlein"); weg.setIcon(symbol("weg", ICON_KLEIN)); weg.setIconSize(QSize(ICON_KLEIN, ICON_KLEIN))
            weg.setToolTip("Aus der Liste nehmen"); weg.setCursor(Qt.PointingHandCursor)
            weg.clicked.connect(lambda _=False, p=p: (self.w.settings.remove_recent(p), self.oeffnen("zuletzt")))
            zeile.addWidget(k, 1); zeile.addWidget(weg)
            v.addLayout(zeile)
        v.addStretch(1)
        return sa

    def _speichern_als(self):
        sa, v = self._seite("Speichern als")
        self._gruppe(v, "Dokument", "Das Dokument unter neuem Namen oder als Kopie speichern.")
        self._knopf(v, "Speichern unter …", "speichernUnter", "speichern")
        self._knopf(v, "Kopie speichern …", "kopieSpeichern", "kopie")
        self._gruppe(v, "Exportieren", "Die Ausgabe wird als Datei geschrieben; das geöffnete Dokument bleibt unverändert.")
        for text, b in EXPORTE:
            self._knopf(v, text, b, "pdf" if b == "speichernPdf" else "ausdatei", datei=EXPORT_ENDUNG.get(b))
        self._gruppe(v, "Weiteres")
        for text, ziel, sym in (("Informationen und Eigenschaften", "info", "inhalt"), ("Öffnen mit …", "oeffnen_mit", "buch")):
            k = QPushButton(text); k.setObjectName("bsKnopf"); k.setFixedWidth(BREITE); k.setCursor(Qt.PointingHandCursor)
            icons.setze(k, sym, ICON_GROSS)
            k.clicked.connect(lambda _=False, z=ziel: self._zeigen(z))
            v.addWidget(k)
        ort = QPushButton("Dateispeicherort öffnen"); ort.setObjectName("bsKnopf"); ort.setFixedWidth(BREITE)
        icons.setze(ort, "oeffnen", ICON_GROSS); ort.setCursor(Qt.PointingHandCursor); ort.clicked.connect(self._speicherort)
        v.addWidget(ort)
        v.addStretch(1)
        return sa

    def _vorlage(self) -> QWidget:
        """Platzhalter: die Galerie mit den Vorschauen wird erst gebaut, wenn die Seite gezeigt wird."""
        ph = QWidget()
        QVBoxLayout(ph).setContentsMargins(*RAND_KEIN)
        ph._ansicht = None
        return ph

    def _vorlage_zeigen(self) -> None:
        from lunivo_writer.ui.baukasten.vorlagen.vorlagen_galerie import VorlagenGalerie
        ph = self.seiten["vorlage"]
        if ph._ansicht is None:
            g = VorlagenGalerie(self.w.settings, self.w.current_tab() is not None, self.w.benutzerdaten())
            g.gewaehlt.connect(lambda art, wert: (self.schliessen.emit(), self.w.neu_aus_wahl(art, wert)))
            g.als_vorlage.connect(lambda ziel: (self.schliessen.emit(), self.w.als_vorlage_speichern(ziel or None)))
            ph.layout().addWidget(g); ph._ansicht = g
        else:
            ph._ansicht.neu_lesen()

    def _drucken(self) -> QWidget:
        """Platzhalter: das Druckfenster samt Vorschau wird erst gebaut, wenn die Seite gezeigt wird."""
        ph = QWidget()
        QVBoxLayout(ph).setContentsMargins(*RAND_KEIN)
        ph._ansicht = None
        return ph

    def _pdf(self) -> QWidget:
        """Platzhalter für den eingebetteten PDF-Export, frisch je Öffnen des Datei-Menüs."""
        ph = QScrollArea()
        ph.setObjectName("bsSeite")
        ph.setWidgetResizable(True)
        ph.setFrameShape(QFrame.NoFrame)
        ph._ansicht = None
        return ph

    def _pdf_zeigen(self) -> None:
        ph = self.seiten["pdf"]
        if ph._ansicht is None:
            ph._ansicht = self.w.pdf_export_widget()
            ph.setWidget(ph._ansicht)

    def _bild(self) -> QWidget:
        """Platzhalter für den Bildexport in der rechten Menüspalte."""
        ph = QScrollArea()
        ph.setObjectName("bsSeite")
        ph.setWidgetResizable(True)
        ph.setFrameShape(QFrame.NoFrame)
        ph._ansicht = None
        return ph

    def _bild_zeigen(self) -> None:
        ph = self.seiten["bild"]
        if ph._ansicht is None:
            ph._ansicht = self.w.bild_export_widget()
            ph.setWidget(ph._ansicht)

    def _drucken_zeigen(self) -> None:
        ph = self.seiten["drucken"]
        t = self.w.current_tab()
        if ph._ansicht is not None or t is None:
            return
        v = ph.layout()
        ph._ansicht = self.w.druck_ansicht(t)
        v.addWidget(ph._ansicht, 1)
        fuss = QHBoxLayout(); fuss.setContentsMargins(*RAND_FUSS_BACKSTAGE)
        hilfe = QPushButton("Hilfe"); hilfe.clicked.connect(self.w.druck_hilfe)
        drucken = QPushButton("Drucken"); drucken.setObjectName("optFertig"); drucken.setDefault(True); drucken.setCursor(Qt.PointingHandCursor)
        drucken.setMinimumSize(*GROESSE_KNOPF_MIN); hilfe.setMinimumHeight(HOEHE_KNOPF)
        drucken.clicked.connect(lambda: (self.schliessen.emit(), self.w.drucke_nach_wahl(t, ph._ansicht.ergebnis())))
        ph._ansicht.geaendert.connect(lambda: drucken.setEnabled(ph._ansicht.gueltig()))
        fuss.addWidget(hilfe); fuss.addStretch(1); fuss.addWidget(drucken)
        v.addLayout(fuss)

    def _hilfe(self):
        sa, v = self._seite("Hilfe")
        self._knopf(v, "Handbuch", "handbuch", "buch")
        self._knopf(v, "Tastenkürzel", "tastenHilfe", "tasten")
        self._knopf(v, "Erweiterungen", "erweiterungen", "zahnrad")
        self._knopf(v, "Über Lunivo Writer", "ueber", "inhalt")
        v.addStretch(1)
        return sa

    def _schuetzen(self):
        sa, v = self._seite("Dokumentverschlüsselung")
        t = self.w.current_tab()
        self._gruppe(v, "Kennwortschutz", "Das Kennwort schützt das Öffnen der DOCX-Datei. Die Verschlüsselung wird beim nächsten Speichern angewendet.")
        kennwort_form = QWidget(); kg = FormularGitter(kennwort_form); kg.setContentsMargins(*RAND_ZEILE); kg.einspaltig = True; kg.beschriftung_voll = True
        kg.beschriftungsabstand = ABSTAND_GROSS; kg.zeilenabstand = ABSTAND_MITTEL
        kennwort = QLineEdit(); kennwort.setEchoMode(QLineEdit.Password); kennwort.setPlaceholderText("Dokumentkennwort")
        bestaetigung = QLineEdit(); bestaetigung.setEchoMode(QLineEdit.Password); bestaetigung.setPlaceholderText("Kennwort erneut eingeben")
        kennwort.setAccessibleName("Dokumentkennwort"); bestaetigung.setAccessibleName("Bestätigung des Dokumentkennworts")
        kennwort.setEnabled(t is not None); bestaetigung.setEnabled(t is not None)
        kg.zeile("Dokumentkennwort:", kennwort); kg.zeile("Erneut eingeben:", bestaetigung)
        v.addWidget(kennwort_form)

        hinweis = QLabel("Ein vergessenes Kennwort kann nicht wiederhergestellt werden. Bewahre es an einem sicheren Ort auf.")
        hinweis.setWordWrap(True); hinweis.setObjectName("bsHinweis"); v.addWidget(hinweis)
        status = QLabel(); status.setWordWrap(True); status.setObjectName("bsHinweis")
        if t is None:
            status.setText("Kein Dokument geöffnet.")
        elif t.meta.get("kennwort"):
            status.setText("Dieses Dokument wird beim nächsten Speichern mit einem Kennwort verschlüsselt.")
        else:
            status.setText("Dieses Dokument ist derzeit nicht kennwortgeschützt.")
        v.addWidget(status)

        aktionen = QHBoxLayout()
        setzen = QPushButton("Kennwort setzen / ändern"); setzen.setObjectName("optFertig"); setzen.setEnabled(t is not None)
        entfernen = QPushButton("Kennwort entfernen"); entfernen.setEnabled(bool(t and t.meta.get("kennwort")))
        aktionen.addWidget(setzen); aktionen.addWidget(entfernen); aktionen.addStretch(1); v.addLayout(aktionen)

        def setze_kennwort():
            if not kennwort.text():
                status.setText("Bitte gib ein Dokumentkennwort ein."); kennwort.setFocus(); return
            if kennwort.text() != bestaetigung.text():
                status.setText("Die beiden Kennworteingaben stimmen nicht überein."); bestaetigung.setFocus(); return
            t.meta["kennwort"] = kennwort.text(); t.editor.document().setModified(True)
            kennwort.clear(); bestaetigung.clear(); entfernen.setEnabled(True)
            status.setText("Kennwort gesetzt. Die DOCX-Datei wird beim nächsten Speichern verschlüsselt.")

        def entferne_kennwort():
            t.meta.pop("kennwort", None); t.editor.document().setModified(True)
            kennwort.clear(); bestaetigung.clear(); entfernen.setEnabled(False)
            status.setText("Kennwort entfernt. Die Änderung gilt ab dem nächsten Speichern.")

        setzen.clicked.connect(setze_kennwort); entfernen.clicked.connect(entferne_kennwort)

        self._gruppe(v, "Datenschutzoptionen", "Diese Einstellungen gelten für das Öffnen und Speichern in Lunivo.")
        for key, label, default in (
            ("sicherheit/markup_oeffnen", "Ausgeblendete Markups beim Öffnen oder Speichern anzeigen", True),
            ("sicherheit/personendaten_weg", "Beim Speichern persönliche Daten aus Dateieigenschaften entfernen", False),
        ):
            box = QCheckBox(label); box.setChecked(self.w.settings.get_bool(key, default))
            box.toggled.connect(lambda an, k=key: self.w.settings.set(k, an))
            v.addWidget(box)

        self._gruppe(v, "Dokument", "Weitere Dokumentaktionen")
        eigenschaften = QPushButton("Eigenschaften …")
        eigenschaften.setObjectName("bsKnopf"); eigenschaften.setFixedWidth(BREITE)
        eigenschaften.setCursor(Qt.PointingHandCursor); icons.setze(eigenschaften, "info", ICON_GROSS)
        eigenschaften.setToolTip("Dokumentangaben wie Titel und Verfasser anzeigen und bearbeiten.")
        eigenschaften.clicked.connect(lambda: self._zeigen("info"))
        v.addWidget(eigenschaften)
        self._gruppe(v, "Bearbeitung", "Bearbeitung sperren oder freigeben — wirkt in diesem Fenster.")
        sperren = QCheckBox("Bearbeitung sperren")
        sperren.setChecked(bool(t and getattr(t, "gesperrt", False))); sperren.setEnabled(t is not None)
        sperren.toggled.connect(lambda an: t and an != bool(getattr(t, "gesperrt", False)) and self.w.toggle_sperre())
        v.addWidget(sperren)
        self._gruppe(v, "Mit Signatur", "Digitale Signaturen sind in dieser Fassung noch nicht verfügbar.")
        k = QPushButton("Digitale Signatur hinzufügen")
        k.setObjectName("bsKnopf")
        k.setEnabled(False)
        k.setFixedWidth(BREITE)
        v.addWidget(k)
        v.addStretch(1)
        return sa

    def _info(self):
        sa, v = self._seite("Informationen zum Dokument")
        t = self.w.current_tab()
        if t is None:
            h = QLabel("Kein Dokument geöffnet.")
            h.setObjectName("bsHinweis")
            v.addWidget(h)
            v.addStretch(1)
            return sa
        ed = t.editor
        text = ed.document().toPlainText()
        absaetze = sum(1 for z in text.split("\n") if z.strip())
        groesse = os.path.getsize(t.path) if t.path and os.path.exists(t.path) else None
        self._gruppe(v, "Allgemein")
        for name, wert in (("Name", t.title), ("Ort", t.path or "noch nicht gespeichert"),
                           ("Größe", f"{groesse / 1024:.1f} KB" if groesse is not None else "–"),
                           ("Papier", f"{t.page.paper_name()} {'quer' if t.page.landscape else 'hoch'}")):
            self._zeile(v, name, QLabel(str(wert)))
        self._gruppe(v, "Statistiken")
        for name, wert in (("Seiten", ed.page_count), ("Absätze", absaetze), ("Wörter", ed.word_count()),
                           ("Zeichen", len(text.replace(" ", "").replace("\n", ""))), ("Zeichen mit Leerzeichen", len(text.replace("\n", "")))):
            self._zeile(v, name, QLabel(str(wert)))
        self._gruppe(v, "Eigenschaften", "Werden mit dem Dokument gespeichert (DOCX: Titel und Verfasser).")
        for schl, name in (("author", "Verfasser"), ("title", "Titel")):
            e = QLineEdit(t.meta.get(schl, "") or "")
            e.setFixedWidth(BREITE_FELD_BACKSTAGE)
            e.editingFinished.connect(lambda e=e, s=schl, t=t: self._meta_setzen(t, s, e.text()))
            self._zeile(v, name, e)
        v.addStretch(1)
        return sa

    def _meta_setzen(self, t, schl: str, wert: str):
        if (t.meta.get(schl, "") or "") != wert:
            t.meta[schl] = wert
            t.editor.document().setModified(True)

    @staticmethod
    def _zeile(v: QVBoxLayout, name: str, feld: QWidget):
        row = QHBoxLayout()
        n = QLabel(name)
        n.setFixedWidth(BREITE_NAMENSFELD)
        row.addWidget(n)
        row.addWidget(feld)
        row.addStretch(1)
        v.addLayout(row)

    def _oeffnen_mit(self):
        sa, v = self._seite("Öffnen mit …")
        self._gruppe(v, "Teilen")
        self._knopf(v, "Dokument teilen (optional)", "dokumentTeilen", "verknuepft")
        v.addStretch(1)
        return sa
