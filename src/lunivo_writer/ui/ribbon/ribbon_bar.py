"""Das Band (Register): Reiter → Gruppen → Knöpfe, gebaut aus resources/register.json.

register.json beschreibt Reiter, Gruppen und Knöpfe. Was `Befehle` nicht kennt, steht ausgegraut da.
"""
from __future__ import annotations

import json
import os
from lunivo_writer.core import paths

from PySide6.QtCore import QPropertyAnimation, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPainter
from PySide6.QtWidgets import (
    QComboBox, QFontComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QMenu, QScrollArea,
    QSizePolicy, QStackedWidget, QTabBar, QToolButton, QVBoxLayout, QWidget,
)

from lunivo_writer.ui.baukasten.bild_diagramm_menues import FELDER, GALERIEN, KLAPPEN
from lunivo_writer.ui.baukasten.text_format import groesse_feld, schrift_feld
from lunivo_writer.ui.document.document_editor import STYLES
from lunivo_writer.ui.widgets import icons
from lunivo_writer.ui.ribbon.plan import plan

from lunivo_writer.core.farben import Farbe
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


class _GruppenTrenner(QWidget):
    """Dezenter Gruppentrenner im Band: genau ein physischer Bildpunkt breit, oben und unten eingerückt, Farbe aus der aktuellen Palette
    (Bandhintergrund leicht zur Mittelfarbe gemischt); folgt dem Themenwechsel von selbst, weil bei jedem Zeichnen neu gemischt wird."""
    EINRUECKEN = 6
    MISCHUNG = 0.30

    def __init__(self):
        super().__init__()
        self.setFixedWidth(3)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def paintEvent(self, _ev):
        pal = self.palette()
        a, b, m = pal.color(self.backgroundRole()), pal.color(pal.ColorRole.Mid), self.MISCHUNG
        farbe = QColor(*(round(x * (1 - m) + y * m) for x, y in ((a.red(), b.red()), (a.green(), b.green()), (a.blue(), b.blue()))))
        d = self.devicePixelRatioF() or 1.0
        p = QPainter(self)
        x = round(self.width() / 2 * d) / d                               # auf einen physischen Punkt gerastert
        p.fillRect(QRectF(x, self.EINRUECKEN, 1.0 / d, max(0, self.height() - 2 * self.EINRUECKEN)), farbe)


class _BandSeite(QScrollArea):
    """Eine Seite des Bandes. Ist sie breiter als das Fenster, erscheinen am Rand Pfeile zum Blättern (‹ und ›), wie in der Vorlage Writer;
    das Mausrad blättert ebenfalls. Der Rollbalken bleibt weg — er würde die Knöpfe verdecken."""
    SCHRITT = 0.6                              # Anteil der sichtbaren Breite je Klick

    def __init__(self):
        super().__init__()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.pfeile: dict[str, QToolButton] = {}
        for seite, zeichen in (("links", "‹"), ("rechts", "›")):
            b = QToolButton(self)
            b.setText(zeichen); b.setAutoRepeat(True); b.setAutoRepeatDelay(350); b.setAutoRepeatInterval(120)
            b.setCursor(Qt.ArrowCursor); b.setFocusPolicy(Qt.NoFocus)
            b.setToolTip("Weiter nach " + seite)
            b.setStyleSheet("QToolButton { border: none; border-radius: 0; font-size: 16pt; font-weight: 600; padding: 0 3px; "
                            "background: palette(window); color: palette(window-text); }"
                            "QToolButton:hover { background: palette(midlight); }")
            b.clicked.connect(lambda _c=False, s=seite: self.blaettern(-1 if s == "links" else 1))
            b.hide()
            self.pfeile[seite] = b
        leiste = self.horizontalScrollBar()
        leiste.valueChanged.connect(self._pfeile_zeigen)
        leiste.rangeChanged.connect(self._pfeile_zeigen)
        self._anim = QPropertyAnimation(leiste, b"value", self)
        self._anim.setDuration(160)

    def blaettern(self, richtung: int) -> None:
        leiste = self.horizontalScrollBar()
        ziel = leiste.value() + richtung * max(120, int(self.viewport().width() * self.SCHRITT))
        self._anim.stop()
        self._anim.setStartValue(leiste.value())
        self._anim.setEndValue(max(leiste.minimum(), min(leiste.maximum(), ziel)))
        self._anim.start()

    def _pfeile_zeigen(self, *_) -> None:
        leiste = self.horizontalScrollBar()
        mehr = leiste.maximum() > 0
        self.pfeile["links"].setVisible(mehr and leiste.value() > 0)
        self.pfeile["rechts"].setVisible(mehr and leiste.value() < leiste.maximum())
        self._pfeile_legen()

    def _pfeile_legen(self) -> None:
        h = self.viewport().height()
        w = 22
        self.pfeile["links"].setGeometry(0, 0, w, h)
        self.pfeile["rechts"].setGeometry(self.width() - w, 0, w, h)
        for b in self.pfeile.values():
            b.raise_()

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._pfeile_zeigen()

    def wheelEvent(self, ev):
        leiste = self.horizontalScrollBar()
        if leiste.maximum() > 0:
            d = ev.angleDelta().x() or ev.angleDelta().y()
            leiste.setValue(leiste.value() - d)
            ev.accept()
        else:
            super().wheelEvent(ev)


# Sichtbare Kurztexte der Knöpfe: kurz, einfache Wörter, leicht lesbar (auch bei Lese-Rechtschreib-Schwäche). Der volle Name bleibt der Hinweistext
# und der Schlüssel der Funktion; Menüeinträge behalten den vollen Namen.
KURZ = {
    'Gerade und ungerade Seiten sind unterschiedlich': 'Links/rechts anders',
    'In anderem neuen Dokument zusammenführen': 'Als anderes Dokument',
    'In neuem Dokument zusammenführen': 'Als Dokument',
    'An Drucker zusammenführen': 'Zum Drucker',
    'Übereinstimmende Felder festlegen': 'Felder zuordnen',
    'Seriendruckfelder hervorheben': 'Felder markieren',
    'Seriendruckfeld einfügen': 'Feld einfügen',
    'Nächstes Feld einfügen': 'Nächstes Feld',
    'Seriendruck schließen': 'Schließen',
    'Seriendruckempfänger': 'Empfänger',
    'Seriendruck-Vorschau': 'Vorschau',
    'Vorheriger Datensatz': 'Zurück',
    'Nächster Datensatz': 'Weiter',
    'Datenquelle öffnen': 'Daten öffnen',
    'Letzter Datensatz': 'Letzter',
    'Erster Datensatz': 'Erster',
    'Seriendruck-Assistent': 'Assistent',
    'Ergebnisse anzeigen': 'Ergebnisse',
    'Seriendruckfeld': 'Feld',
    'Zwischen Kopf- und Fußzeile wechseln': 'Kopf/Fuß wechseln',
    'Optionen für Kopf- und Fußzeile': 'Optionen',
    'Ausrichtungstabstopp einfügen': 'Tabstopp',
    'Link zu vorheriger Kopfzeile': 'Wie vorher',
    'Mit vorheriger verknüpfen': 'Wie vorher',
    'Mit voriger Fußzeile verknüpfen': 'Wie vorher',
    'Kopf-/Fußzeilengruppe': 'Kopf/Fuß-Gruppe',
    'Nächste Kopfzeile': 'Weiter',
    'Vorige Kopfzeile': 'Zurück',
    'Transparente Farbe einstellen': 'Transparenz',
    'Größe und Seitenverhältnis …': 'Größe',
    'Seitenverhältnis sperren': 'Maße sperren',
    'Verhältnis sperren': 'Maße sperren',
    'Eine Ebene nach hinten': 'Nach hinten',
    'Eine Ebene nach vorne': 'Nach vorn',
    'Zuschneiden nach Maß …': 'Auf Maß',
    'Bilder komprimieren': 'Komprimieren',
    'Kontrast verringern': 'Kontrast −',
    'Kontrast erhöhen': 'Kontrast +',
    'Größe zurücksetzen': 'Größe zurück',
    'Bild zurücksetzen': 'Zurücksetzen',
    'Textumbruch Stil': 'Umbruch',
    'Textumbruch / Position': 'Umbruch',
    'Auf Seitenbreite': 'Seitenbreite',
    'Alternativtext …': 'Alt-Text',
    'Bild entfernen': 'Entfernen',
    'Layout von rechts nach links': 'Von rechts',
    'Aufzählungszeichen einfügen': 'Aufzählung',
    'Level reduzieren': 'Ebene runter',
    'Level erhöhen': 'Ebene hoch',
    'Diagrammelement hinzufügen': 'Element +',
    'Diagrammtyp ändern': 'Typ ändern',
    'Daten bearbeiten': 'Daten',
    'Daten auswählen': 'Auswählen',
    'Seitenleiste Schreibhilfe': 'Seitenleiste',
    'Dokumentprüfung': 'Prüfung',
    'Wortvorhersage': 'Vorhersage',
    'Silbentrennung': 'Trennung',
    'Abschnittsnavigationsbereich': 'Abschnitte',
    'Abschnitt einrichten …': 'Einrichten',
    'Abschnitt hinzufügen': 'Abschnitt +',
    'Abschnitt löschen': 'Abschnitt −',
    'Vorheriger Abschnitt': 'Zurück',
    'Nächster Abschnitt': 'Weiter',
    'Änderungen nachverfolgen': 'Änderungen',
    'Bearbeitung einschränken': 'Einschränken',
    'Kommentar einfügen': 'Kommentar',
    'Tabellenformatvorlagen': 'Tabellenstile',
    'Rahmenlinien ein/aus': 'Rahmen',
    'Zellenschattierung': 'Zellfarbe',
    'Gebänderte Zeilen': 'Zeilenband',
    'Gruppierung aufheben': 'Lösen',
    'Text in der Form …': 'Text in Form',
    'Formen einfügen': 'Formen',
    'Form bearbeiten': 'Bearbeiten',
    'Verknüpfung erstellen': 'Verknüpfen',
    'Suchen oder ersetzen': 'Suchen',
    'Kopf- und Fußzeile': 'Kopf/Fuß',
    'Datum und Uhrzeit': 'Datum',
    'Abbildungsverzeichnis': 'Abbildungen',
    'Literaturverzeichnis': 'Literatur',
    'Inhaltsverzeichnis': 'Inhalt',
    'Zur Note springen': 'Zur Note',
    'Eintrag festlegen': 'Eintrag',
    'Quellen verwalten': 'Quellen',
    'Fußnote einfügen': 'Fußnote',
    'Endnote einfügen': 'Endnote',
    'Zitat einfügen': 'Zitat',
    'Navigationsbereich': 'Navigation',
    'Weitere Ansichten': 'Ansichten',
    'Register anpassen': 'Anpassen',
    'Gitternetzlinien': 'Seitenraster',
    'Weitere Anzeigen': 'Mehr',
    'Genko-Einstellung': 'Genko',
    'Auswahlbereich': 'Auswahl',
    'Formatvorlage zurücksetzen': 'Stil zurück',
    'Gitternetzlinien anzeigen': 'Tabellenlinien',
    'Tabelleneigenschaften': 'Eigenschaften',
    'Darüber einfügen': 'Zeile oben',
    'Darunter einfügen': 'Zeile unten',
    'Links einfügen': 'Spalte links',
    'Rechts einfügen': 'Spalte rechts',
    'Tabelle sortieren': 'Sortieren',
    'Originalgröße': 'Original',
    'AutoKorrektur': 'Korrektur',
    'Silben farbig': 'Silbenfarben',
    'Thesaurus': 'Synonyme',
    'Markup anzeigen': 'Markierungen',
    'Einstellungen': 'Optionen',
    'Tabelle zeichnen': 'Zeichnen',
    'Absatzabstand': 'Abstand',
    'Format übertragen': 'Format kopieren',
}


def _kurz(name: str) -> str:
    return KURZ.get(name, name)


def _mit_kuerzel(name: str) -> str:
    """Hinweistext eines Knopfes; steht der Name in der Kürzel-Tabelle (``ui/kuerzel.py``), kommt das Tastenkürzel dahinter."""
    from lunivo_writer.ui.kuerzel import HILFE
    for _gruppe, zeilen in HILFE:
        for taste, text in zeilen:
            if text == name and " / " not in taste:
                return f"{name} ({taste})"
    return name


def _zweizeilig(text: str) -> str:
    if len(text) <= 12 or " " not in text:
        return text
    mitte = len(text) // 2
    i = min((i for i, c in enumerate(text) if c == " "), key=lambda i: abs(i - mitte))
    return text[:i] + "\n" + text[i + 1:]


# „Sendungen“ gehört nicht zur neuen Struktur (Datei … Ansicht): vorhanden, aber erst nach Register anpassen sichtbar —
# bis dahin über die Menüleiste (Ansicht ▸ Oberfläche ▸ Menüleiste) erreichbar.
STANDARD_VERSTECKT = ("Sendungen",)


class _ReiterLeiste(QTabBar):
    doppelt = Signal()
    LUECKE = 10          # Abstand links und rechts um einen Kontext-Reiter
    LUECKE_KOMPAKT = 5

    def mouseDoubleClickEvent(self, ev):
        self.doppelt.emit()
        super().mouseDoubleClickEvent(ev)

    def ist_kontext(self, i: int) -> bool:
        return self.tabData(i) == "kontext"

    def tabSizeHint(self, i):
        sz = super().tabSizeHint(i)
        if self.ist_kontext(i):
            sz.setWidth(sz.width() + 2 * self._luecke())
        return sz

    def _luecke(self) -> int:
        return self.LUECKE_KOMPAKT if self.property("kompakt") else self.LUECKE

    def paintEvent(self, ev):
        super().paintEvent(ev)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        dunkel = self.palette().window().color().lightness() < 128
        akzent = QColor(Farbe.AKZENT_DUNKEL if dunkel else Farbe.AKZENT)
        erster = True
        for i in range(self.count()):
            if not self.isTabVisible(i) or not self.ist_kontext(i):
                continue
            tr = self.tabRect(i)
            p.fillRect(tr.adjusted(0, tr.height() - 4, 0, 0), self.parentWidget().palette().window())   # Stylesheet-Unterstrich weg
            r = tr.adjusted(self._luecke(), 3, -self._luecke(), -3)
            if erster:                       # Trenner zwischen normalen und Kontext-Reitern
                x = self.tabRect(i).left() + 2
                p.setPen(self.palette().mid().color())
                p.drawLine(x, r.top() + 2, x, r.bottom() - 2)
                erster = False
            aktiv = i == self.currentIndex()
            if aktiv:
                p.setPen(Qt.NoPen); p.setBrush(akzent)
            else:
                fl = QColor(akzent); fl.setAlpha(40)
                p.setPen(akzent); p.setBrush(fl)
            p.drawRoundedRect(r, r.height() / 2, r.height() / 2)
            f = QFont(self.font()); f.setBold(aktiv); p.setFont(f)
            p.setPen(QColor("#ffffff") if aktiv else (QColor("#9cc4f0") if dunkel else akzent))
            p.drawText(r, Qt.AlignCenter, self.tabText(i))
        p.end()


class RegisterBand(QWidget):
    """Kopfzeile (☰, Schnellzugriff, Reiter) und darunter das Band des gewählten Reiters."""

    # Maße des Bandes: normal und kompakt (Optionen ▸ Ansicht ▸ „Kompaktes Menüband“): niedrigeres Band, keine Gruppenunterschriften
    BAND_HOEHE = {False: 112, True: 88}
    GROSS_HOEHE = {False: 68, True: 66}
    GROSS_ICON = {False: 28, True: 24}

    def __init__(self, befehle, daten: dict | None = None, cfg: dict | None = None, schnell: list | None = None, kompakt: bool = True):
        super().__init__()
        self.kompakt = kompakt
        self.cfg = cfg or {}
        self._schnell_wahl = schnell
        self.b = befehle
        self.daten = daten or lade_register()
        self.schalter: list[tuple[QToolButton, str]] = []     # (Knopf, Aktionsname) für Haken
        self.wechsler: list[tuple[QToolButton, str]] = []     # Knöpfe, deren Symbol dem zuletzt gewählten Menüeintrag folgt (Groß-/Kleinschreibung)
        self.knoepfe: list[tuple[QToolButton, str | None, bool]] = []   # (Knopf, Name, braucht Dokument)
        self.felder: dict[str, QWidget] = {}
        self.fehlend: list[str] = []
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.kopf = QHBoxLayout()
        self.kopf.setContentsMargins(6, 2, 6, 0)
        self.kopf.setSpacing(2)
        self.menue_knopf = QToolButton()
        self.menue_knopf.setText("Menü")
        self.menue_knopf.setIcon(icons.icon("menu", 16)); self.menue_knopf.setIconSize(QSize(16, 16))
        self.menue_knopf.setToolButtonStyle(Qt.ToolButtonTextBesideIcon); self.menue_knopf.setLayoutDirection(Qt.RightToLeft)
        self.menue_knopf.setAutoRaise(True)
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
        lay.addLayout(self.kopf)
        self.stapel = QStackedWidget()
        self.stapel.setObjectName("bandStapel")
        self.stapel.setFixedHeight(self.BAND_HOEHE[kompakt])
        lay.addWidget(self.stapel)
        linie = self.linie = QFrame()
        linie.setFrameShape(QFrame.HLine)
        linie.setFrameShadow(QFrame.Sunken)
        lay.addWidget(linie)
        self._schnellzugriff()
        self.kontext_index: dict[str, int] = {}
        self.kontext_weitere: dict[str, list[int]] = {}               # weitere Reiter desselben Kontexts (Tabellenstil neben Tabellentools)
        for r in self._plan_angepasst():
            self._reiter(r)
        self.reiter.currentChanged.connect(self.stapel.setCurrentIndex)
        self.reiter.tabBarClicked.connect(self._reiter_geklickt)
        self.reiter.doppelt.connect(self.einklappen_umschalten)
        self.reiter.setCurrentIndex(self._start_index())          # Start
        self.bandfehler = sorted(set(self.fehlend))

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
        s = QFrame()
        s.setFrameShape(QFrame.VLine)
        s.setFrameShadow(QFrame.Sunken)
        self.kopf.addWidget(s)

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
            k.setIcon(icons.icon(sym, 18))
            k.setIconSize(QSize(18, 18))
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
            k.setIcon(icons.icon("assistent", 18)); k.setIconSize(QSize(18, 18))
            k.clicked.connect(lambda _=False, a=a: ausfuehren(a))
            self.schnell.addWidget(k)
            self._ki_schnell_knoepfe.append(k)

    # ---- Reiter und Gruppen -------------------------------------------------------------------------------
    def _reiter(self, r: dict):
        scroll = _BandSeite()
        scroll.setObjectName("bandSeite")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        seite = QWidget()
        h = QHBoxLayout(seite)
        h.setContentsMargins(6, 2, 6, 0)
        h.setSpacing(0)
        for i, g in enumerate(r["gruppen"]):
            s = None
            if i:
                s = _GruppenTrenner()
                h.addWidget(s)
            rahmen = self._gruppe(g)
            h.addWidget(rahmen)
        h.addStretch(1)
        scroll.setWidget(seite)
        self.stapel.addWidget(scroll)
        i = self.reiter.addTab(r["name"])
        if r.get("kontext"):
            if r["kontext"] in self.kontext_index:
                self.kontext_weitere.setdefault(r["kontext"], []).append(i)
            else:
                self.kontext_index[r["kontext"]] = i
            self.reiter.setTabVisible(i, False)
            self.reiter.setTabData(i, "kontext")

    def _gruppe(self, g: dict) -> QWidget:
        rahmen = QWidget()
        v = QVBoxLayout(rahmen)
        v.setContentsMargins(1 if self.kompakt else 3, 2, 1 if self.kompakt else 3, 0)
        v.setSpacing(0)
        if self.kompakt:
            rahmen.setToolTip(g["name"])                 # die Unterschrift entfällt; der Name steht im Hinweis
        inhalt = QHBoxLayout()
        inhalt.setSpacing(1)
        inhalt.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        v.addLayout(inhalt, 1)
        if g.get("katalog") == "raender":
            inhalt.addWidget(self._raender())
        elif g.get("katalog"):
            inhalt.addWidget(self._stile(int(g.get("spalten") or 3)))
        else:
            self._knoepfe(g, inhalt)
        if self.kompakt and not g.get("pfeil"):
            if not g.get("ohne_titel"):
                QLabel(g["name"].upper(), rahmen).hide()           # Unterschrift bleibt als verborgene Beschriftung (Aufbau prüfbar)
            return rahmen
        fuss = QHBoxLayout()
        fuss.setContentsMargins(0, 0, 0, 0)
        t = QLabel("" if g.get("ohne_titel") else g["name"].upper())     # Kontext-Reiter wie in der Vorlage: Gruppen ohne Unterschrift
        t.setVisible(not self.kompakt)
        t.setAlignment(Qt.AlignCenter)
        t.setStyleSheet("font-size: 7pt; color: palette(mid); letter-spacing: 1px;")
        fuss.addStretch(1)
        fuss.addWidget(t)
        if g.get("pfeil"):
            p = QToolButton()
            p.setText("↘")
            p.setAutoRaise(True)
            p.setFixedSize(14, 14)
            p.setStyleSheet("font-size: 7pt;")
            p.setToolTip(g["name"] + " — Einstellungen")
            p.clicked.connect(lambda _=False, a=g["pfeil"]: self.b.tun(a))
            p.setEnabled(self.b.hat(g["pfeil"]))
            if not self.b.hat(g["pfeil"]):
                self.fehlend.append(g["pfeil"])
            fuss.addWidget(p)
        fuss.addStretch(1)
        v.addLayout(fuss)
        return rahmen

    def _knoepfe_geordnet(self, g: dict, inhalt: QHBoxLayout):
        """Knöpfe in der Reihenfolge der Liste: große stehen allein, aufeinanderfolgende kleine bilden eine Spalte aus zwei Zeilen."""
        lauf: list[dict] = []
        felder: list = []                                     # aufeinanderfolgende Eingabefelder stehen übereinander (wie die Kleinknöpfe)

        def feldspalte():
            if felder:
                host = QWidget()
                v = QVBoxLayout(host)
                v.setContentsMargins(0, 0, 0, 0)
                v.setSpacing(1)
                for w in felder:
                    v.addWidget(w)
                v.addStretch(1)
                inhalt.addWidget(host, 0, Qt.AlignTop)
                felder.clear()

        def spalte(felder_behalten=False):
            if not felder_behalten:
                feldspalte()
            for i in range(0, len(lauf), 2):                    # je Spalte zwei Zeilen
                host = QWidget()
                v = QVBoxLayout(host)
                v.setContentsMargins(0, 0, 0, 0)
                v.setSpacing(1)
                for e in lauf[i:i + 2]:
                    v.addWidget(self._knopf(e, False))
                v.addStretch(1)
                inhalt.addWidget(host, 0, Qt.AlignTop)
            lauf.clear()
        for e in g["knoepfe"]:
            if e.get("feld"):                                     # ein Eingabefeld, das der Befehls-Baustein liefert (band_feld)
                spalte(felder_behalten=True)
                bau = FELDER.get(e["feld"])                    # erst die Felder der Oberfläche, sonst ``feld_<name>`` des Befehlsbausteins
                w = bau(self.b) if bau else self.b.band_feld(e["feld"])
                if w is not None:
                    self.felder[e["feld"]] = w
                    felder.append(w)
            elif e.get("gross"):
                spalte()
                inhalt.addWidget(self._knopf(e, True))
            else:
                feldspalte()
                lauf.append(e)
        spalte()

    def _knoepfe_schrift(self, g: dict, inhalt: QHBoxLayout):
        """Wie in der Vorlage: oben Schriftname und -größe, daneben die Größen-/Löschknöpfe; darunter die Zeichenformate."""
        from lunivo_writer.ui.widgets.live_vorschau import VorschauCombo, VorschauFontCombo
        vs = self.b.w.vorschau

        def _zu_pt(t):
            try:
                return float(t.replace(",", "."))
            except ValueError:
                return None
        font = schrift_feld(VorschauFontCombo(lambda n: vs.zeigen(lambda e: e.set_font_family(n)), vs.ende))
        groesse = groesse_feld(VorschauCombo(lambda t: (pt := _zu_pt(t)) is not None and vs.zeigen(lambda e: e.set_font_size(pt)), vs.ende))
        stil = VorschauCombo(lambda n: vs.zeigen(lambda e: e.apply_style("Standard" if n == "Fließtext" else n)), vs.ende)
        stil.addItems(["Fließtext"] + [n for n in STYLES if n != "Standard"])
        stil.setParent(self)                                   # die Stile stehen in der Galerie; die Auswahl bleibt nur für den Abgleich
        stil.hide()
        self.felder.update(stil=stil, font=font, groesse=groesse)
        zeilen, aktuell = [], []
        for e in g["knoepfe"]:
            if e.get("zeilenumbruch"):
                zeilen.append(aktuell)
                aktuell = []
            else:
                aktuell.append(e)
        zeilen.append(aktuell)
        v = QVBoxLayout()
        v.setSpacing(2)
        v.setContentsMargins(0, 0, 0, 0)
        for i, zeile in enumerate(zeilen):
            h = QHBoxLayout()
            h.setSpacing(1)
            h.setContentsMargins(0, 0, 0, 0)
            if i == 0:
                h.addWidget(font)
                h.addWidget(groesse)
                h.addSpacing(3)
            for e in zeile:
                h.addWidget(self._knopf(e, False))
            h.addStretch(1)
            v.addLayout(h)
        v.addStretch(1)
        inhalt.addLayout(v)

    def _knoepfe_tt_schrift(self, g: dict, inhalt: QHBoxLayout, art: str = "tt"):
        """Texttools: Schriftname und -größe oben (wirken auf das markierte WordArt/Textfeld), darunter die Zeichenformate — wie bei Start.
        ``art="tab"`` (Tabellentools): dieselben Felder, aber sie wirken auf den Text der Schreibmarke / der markierten Zellen (Felder ``tab_font``, ``tab_groesse``)."""
        font = schrift_feld(QFontComboBox())
        groesse = groesse_feld()
        if art == "tab":
            def pt_setzen(*_):
                try:
                    pt = float(groesse.currentText().replace(",", "."))
                except ValueError:
                    return
                self.b.w._ed(lambda e: (e.set_font_size(pt), e.setFocus()))
            font.activated.connect(lambda _i: self.b.w._ed(lambda e: (e.set_font_family(font.currentFont().family()), e.setFocus())))
            groesse.activated.connect(pt_setzen)
            groesse.lineEdit().editingFinished.connect(pt_setzen)
        else:
            font.activated.connect(lambda _i: self.b.ttSchriftart(font.currentText()))
            groesse.activated.connect(lambda _i: self.b.ttGroesse(groesse.currentText()))
            groesse.lineEdit().returnPressed.connect(lambda: self.b.ttGroesse(groesse.currentText()))
        self.felder.update({art + "_font": font, art + "_groesse": groesse})
        zeilen, aktuell = [], []
        for e in g["knoepfe"]:
            if e.get("zeilenumbruch"):
                zeilen.append(aktuell)
                aktuell = []
            else:
                aktuell.append(e)
        zeilen.append(aktuell)
        v = QVBoxLayout()
        v.setSpacing(2)
        v.setContentsMargins(0, 0, 0, 0)
        for i, zeile in enumerate(zeilen):
            h = QHBoxLayout()
            h.setSpacing(1)
            h.setContentsMargins(0, 0, 0, 0)
            if i == 0:
                h.addWidget(font)
                h.addWidget(groesse)
                h.addSpacing(3)
            for e in zeile:
                h.addWidget(self._knopf(e, False))
            h.addStretch(1)
            v.addLayout(h)
        v.addStretch(1)
        inhalt.addLayout(v)

    def _knoepfe_galerie(self, g: dict, inhalt: QHBoxLayout):
        """Eine Galerie wie in der Vorlage: drei Kacheln zum Anklicken und daneben ein Pfeil mit der ganzen Auswahl (Befehl ``galerie_<name>``)."""
        bau = GALERIEN.get(g["galerie"])                          # erst die Bausteine der Oberfläche, sonst ``galerie_<name>`` des Befehlsbausteins
        spec = (lambda: bau(self.b)) if bau else getattr(self.b, "galerie_" + g["galerie"], None)
        if spec is None:
            self.fehlend.append("galerie_" + g["galerie"])
            return
        spec = spec()
        spec = dict(spec, kacheln=spec["kacheln"][:int(g.get("kacheln") or len(spec["kacheln"]))])   # ``"kacheln": N``: nur N Kacheln im Band, alle Einträge bleiben im Pfeil-Menü
        rahmen = QFrame()
        rahmen.setFrameShape(QFrame.StyledPanel)
        h = QHBoxLayout(rahmen)
        h.setContentsMargins(3, 3, 3, 3)
        h.setSpacing(2)
        zeilen = int(g.get("zeilen") or 1)                       # ``"zeilen": 2``: Kacheln in mehreren Reihen (Linien und Pfeile)
        raster = QGridLayout() if zeilen > 1 else None
        if raster is not None:
            raster.setContentsMargins(0, 0, 0, 0); raster.setSpacing(2)
            h.addLayout(raster)
        spalten = -(-len(spec["kacheln"]) // zeilen)
        for nr, (tipp, pm, tun) in enumerate(spec["kacheln"]):
            k = QToolButton()
            k.setAutoRaise(True)
            k.setIcon(QIcon(pm))
            k.setIconSize(pm.size())
            k.setFixedSize(pm.width() + 8, pm.height() + 8)
            k.setToolTip(tipp)
            k.clicked.connect(lambda _=False, f=tun: (f(), self.aktualisieren()))
            if raster is not None:
                raster.addWidget(k, nr // spalten, nr % spalten)
            else:
                h.addWidget(k)
            self.knoepfe.append((k, None, True))
        mehr = QToolButton()
        mehr.setAutoRaise(True)
        mehr.setArrowType(Qt.DownArrow)
        mehr.setToolTip(spec["name"])
        mehr.setPopupMode(QToolButton.InstantPopup)
        spec["menue"].setParent(mehr, Qt.Popup)
        mehr.setMenu(spec["menue"])
        mehr.setFixedWidth(16)
        h.addWidget(mehr)
        self.knoepfe.append((mehr, None, True))
        inhalt.addWidget(rahmen, 0, Qt.AlignTop)

    def _knoepfe_raender(self, g: dict, inhalt: QHBoxLayout):
        """Der Rand-Knopf und daneben wie in der Vorlage die vier Maßfelder Oben/Unten/Links/Rechts (in der gewählten Maßeinheit)."""
        from lunivo_writer.ui.dialogs.dokument_dialoge import _MassSpin
        self._knoepfe_geordnet(g, inhalt)
        host = QWidget()
        gitter = QGridLayout(host)
        gitter.setContentsMargins(0, 0, 0, 0)
        gitter.setHorizontalSpacing(4)
        gitter.setVerticalSpacing(2)
        spins = {}
        for zeile, spalte, schl, name in ((0, 0, "oben", "Oben:"), (0, 2, "unten", "Unten:"), (1, 0, "links", "Links:"), (1, 2, "rechts", "Rechts:")):
            sp = _MassSpin()
            sp.setRange(0.0, 200.0)
            sp.setDecimals(1)
            sp.setSingleStep(1.0)
            sp.setKeyboardTracking(False)
            sp.setFixedWidth(72)
            gitter.addWidget(QLabel(name), zeile, spalte)
            gitter.addWidget(sp, zeile, spalte + 1)
            spins[schl] = sp
            self.felder["rand_" + schl] = sp
            self.knoepfe.append((sp, None, True))
        for sp in spins.values():
            sp.valueChanged.connect(lambda _v, sps=spins: self.b.w.set_margins(
                sps["oben"].value(), sps["unten"].value(), sps["links"].value(), sps["rechts"].value()))
        inhalt.addWidget(host, 0, Qt.AlignTop)

    def _knoepfe_masse(self, g: dict, inhalt: QHBoxLayout):
        """Höhe und Breite des markierten Bildes (Zeichentools); „Seitenverhältnis sperren“ hält das Verhältnis beim Ändern.
        ``"sperre": "bild"`` (Bildtools): Breite oben, Höhe unten; rechts daneben stehen die ersten beiden Knöpfe der Gruppe
        (Sperre = Schalter ``bildSeitenverhaeltnis``, dann „Größe zurücksetzen“).
        ``"befehl"`` nennt den Aufruf (Vorgabe ``zeichenMasse(breite_mm, hoehe_mm)``); ``"verhaeltnis": False`` lässt Sperre und Verhältnis weg
        und meldet nur das geänderte Maß (Tabellentools: ``tabelleMasse``)."""
        from lunivo_writer.ui.dialogs.dokument_dialoge import _MassSpin
        from PySide6.QtWidgets import QCheckBox
        bild = g.get("sperre") == "bild"
        befehl = g.get("befehl", "zeichenMasse")
        verh = g.get("verhaeltnis", True)
        vor = g.get("praefix") or ("bt_" if bild else "bild_")   # eigene Feldnamen: Bildtools, Zeichentools und SmartArt-Design haben je ein Paar
        host = QWidget()
        gitter = QGridLayout(host)
        gitter.setContentsMargins(0, 0, 0, 0); gitter.setHorizontalSpacing(4); gitter.setVerticalSpacing(2)
        spins = {}
        if bild:                                                  # große Knöpfe (Zuschneiden) stehen links vor den Feldern
            for e in (e for e in g["knoepfe"] if e.get("gross")):
                inhalt.addWidget(self._knopf(e, True))
        zeilen = (("breite", "Breite:"), ("hoehe", "Höhe:")) if bild else (("hoehe", "Höhe:"), ("breite", "Breite:"))
        for zeile, (schl, name) in enumerate(zeilen):
            sp = _MassSpin(); sp.setRange(1.0, 2000.0); sp.setDecimals(1); sp.setSingleStep(1.0); sp.setKeyboardTracking(False); sp.setFixedWidth(64)
            gitter.addWidget(QLabel(name), zeile, 0); gitter.addWidget(sp, zeile, 1)
            spins[schl] = sp
            self.felder[vor + schl] = sp
            self.knoepfe.append((sp, None, True))
        sperre = None
        if bild:
            for zeile, e in enumerate([e for e in g["knoepfe"] if not e.get("gross")][:2]):
                gitter.addWidget(self._knopf(e, False), zeile, 2)
        elif verh:
            sperre = QCheckBox("Seitenverhältnis sperren"); sperre.setChecked(True)
            gitter.addWidget(sperre, 2, 0, 1, 2)
            self.felder[vor + "sperre"] = sperre
        verhaeltnis = [1.0]

        def gesperrt() -> bool:
            if not verh:
                return False
            return bool(self.b.an_bildSeitenverhaeltnis()) if bild else sperre.isChecked()

        def geaendert(wer: str):
            b, h = spins["breite"].value(), spins["hoehe"].value()
            if not verh:
                getattr(self.b, befehl)(**{("breite_mm" if wer == "breite" else "hoehe_mm"): b if wer == "breite" else h})
                return
            if gesperrt() and verhaeltnis[0] > 0:
                for sp in spins.values():
                    sp.blockSignals(True)
                if wer == "breite":
                    h = b / verhaeltnis[0]; spins["hoehe"].setValue(h)
                else:
                    b = h * verhaeltnis[0]; spins["breite"].setValue(b)
                for sp in spins.values():
                    sp.blockSignals(False)
            else:
                verhaeltnis[0] = b / max(0.1, h)
            getattr(self.b, befehl)(b, h)
        spins["breite"].valueChanged.connect(lambda _v: geaendert("breite"))
        spins["hoehe"].valueChanged.connect(lambda _v: geaendert("hoehe"))
        self.felder[vor + "verhaeltnis"] = verhaeltnis
        inhalt.addWidget(host, 0, Qt.AlignTop)

    def _knoepfe(self, g: dict, inhalt: QHBoxLayout):
        if g.get("felder") == "raender":
            return self._knoepfe_raender(g, inhalt)
        if g.get("felder") == "masse":
            return self._knoepfe_masse(g, inhalt)
        if g.get("felder") == "zeile":
            return self._knoepfe_schrift(g, inhalt)
        if g.get("felder") == "tt_zeile":
            return self._knoepfe_tt_schrift(g, inhalt)
        if g.get("felder") == "tab_zeile":
            return self._knoepfe_tt_schrift(g, inhalt, "tab")
        if g.get("galerie"):
            return self._knoepfe_galerie(g, inhalt)
        if g.get("reihenfolge"):
            return self._knoepfe_geordnet(g, inhalt)
        eintraege = g["knoepfe"]
        if g.get("felder"):
            spalte = QVBoxLayout()
            spalte.setSpacing(2)
            from lunivo_writer.ui.widgets.live_vorschau import VorschauCombo, VorschauFontCombo
            vs = self.b.w.vorschau

            def _zu_pt(t):
                try:
                    return float(t.replace(",", "."))
                except ValueError:
                    return None
            stil = VorschauCombo(lambda n: vs.zeigen(lambda e: e.apply_style("Standard" if n == "Fließtext" else n)), vs.ende)
            stil.setFixedWidth(150)
            stil.addItems(["Fließtext"] + [n for n in STYLES if n != "Standard"])
            font = schrift_feld(VorschauFontCombo(lambda n: vs.zeigen(lambda e: e.set_font_family(n)), vs.ende))
            groesse = groesse_feld(VorschauCombo(lambda t: (pt := _zu_pt(t)) is not None and vs.zeigen(lambda e: e.set_font_size(pt)), vs.ende))
            for w in (stil, font, groesse):
                spalte.addWidget(w)
            inhalt.addLayout(spalte)
            self.felder.update(stil=stil, font=font, groesse=groesse)
        grosse = [e for e in eintraege if e.get("gross")]
        kleine = [e for e in eintraege if not e.get("gross") and not e.get("hinweis") and e.get("symbol") != "//"]
        for e in grosse:
            inhalt.addWidget(self._knopf(e, True))
        # Zeilen: '//' beginnt eine neue; sonst zwei Zeilen, spaltenweise gefüllt
        zeilen, aktuell, explizit = [], [], False
        for e in eintraege:
            if e.get("zeilenumbruch") or e.get("symbol") == "//":
                explizit = True
                zeilen.append(aktuell)
                aktuell = []
            elif not e.get("gross") and not e.get("hinweis"):
                aktuell.append(e)
        zeilen.append(aktuell)
        gitter = QGridLayout()
        gitter.setSpacing(1)
        if explizit:
            for r, zeile in enumerate(zeilen):
                for c, e in enumerate(zeile):
                    gitter.addWidget(self._knopf(e, False), r, c)
        else:
            for i, e in enumerate(kleine):
                gitter.addWidget(self._knopf(e, False), i % 2, i // 2)
        if kleine:
            host = QWidget()
            host.setLayout(gitter)
            inhalt.addWidget(host, 0, Qt.AlignTop)

    def _stile(self, spalten: int = 3) -> QWidget:
        host = QWidget()
        g = QGridLayout(host)
        g.setSpacing(1)
        g.setContentsMargins(0, 0, 0, 0)
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
        pfeil = QToolButton(); pfeil.setIcon(icons.icon("klappe", 14)); pfeil.setIconSize(QSize(14, 14)); pfeil.setAutoRaise(True); pfeil.setFixedWidth(18)
        pfeil.setToolTip("Alle Formatvorlagen")
        pfeil.clicked.connect(lambda: self._stile_popup(pfeil))
        sa.viewport().installEventFilter(self)
        self._stile_scroll = sa
        aussen = QWidget()
        h = QHBoxLayout(aussen); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(0)
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
        m.gewaehlt.connect(w.stil_anwenden)
        m.ueberfahren.connect(lambda name: w.vorschau.zeigen(lambda ed: ed.apply_style("Standard" if name == "Fließtext" else name)))
        m.verlassen.connect(w.vorschau.ende)
        m.aktion("Neue Formatvorlage …", lambda: self.b.neueFormatvorlage(), icons.icon("pinsel", 18))
        m.aktion("Stil löschen", lambda: self.b.formatvorlageLoeschen(aktuell), icons.icon("radierer", 18),
                 aktiv=bool(aktuell) and stile.ist_eigen(aktuell))
        m.aktion("Weitere Stile anzeigen", lambda an: w.settings.set("ui/stile_mehr", an), haken=mehr)

        def kontext(name, pos):
            km = QMenu(m)
            km.addAction("Ändern …", lambda: (m.close(), self.b.formatvorlageAendern(name)))
            if stile.ist_eigen(name):
                km.addAction("Löschen", lambda: (m.close(), self.b.formatvorlageLoeschen(name)))
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
            k.setFixedWidth(84)
            k.setToolTip(name + (" (eigene Vorlage)" if stile.ist_eigen(name) else ""))
            k.clicked.connect(lambda _=False, n=name: self.b.w.stil_anwenden(n))
            fl = Ueberfahren(self.b.w.vorschau, lambda e, n=name: e.apply_style("Standard" if n == "Fließtext" else n))
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
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(2)
        for art, text in (("normal", "Normal\n25 / 32 mm"), ("schmal", "Schmal\n13 mm"),
                          ("moderat", "Moderat\n25 / 19 mm"), ("breit", "Breit\n25 / 51 mm")):
            k = QToolButton()
            k.setAutoRaise(True)
            k.setText(text)
            k.setFixedSize(84, 56 if self.kompakt else 62)
            k.clicked.connect(lambda _=False, a=art: (self.b.tun('w.setzeRandVorgabe:["%s"]' % a), self.aktualisieren()))
            h.addWidget(k)
            self.knoepfe.append((k, None, True))
        return host

    def _knopf(self, e: dict, gross: bool) -> QToolButton:
        name = e["name"]
        sym = e.get("symbol", "")
        k = QToolButton()
        k.setAutoRaise(True)
        tun, klappe, menue = e.get("tun"), e.get("klappe"), e.get("menue")
        akt = QAction(k)
        akt.setText(sym if not icons.hat(sym) else _kurz(name))
        akt.setToolTip(_mit_kuerzel(name))
        if icons.hat(sym):
            gi = self.GROSS_ICON[self.kompakt]
            akt.setIcon(icons.icon(sym, gi if gross else 18))
            k.setIconSize(QSize(gi, gi) if gross else QSize(18, 18))
        k.setDefaultAction(akt)
        k.setToolTip(_mit_kuerzel(name))
        k.setAccessibleName(name)                      # Screenreader lesen den vollen Namen, nicht den Kurztext
        self._tausch_rechtsklick(k, sym)
        if not icons.hat(sym):
            f = k.font()
            if sym == "F":
                f.setBold(True)
            if sym == "K":
                f.setItalic(True)
            if sym == "U":
                f.setUnderline(True)
            k.setFont(f)
        if gross:
            k.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            k.setText(_zweizeilig(_kurz(name)))
            akt.setText(_zweizeilig(_kurz(name)))               # der Knopf übernimmt später den Text der Aktion
            breit = max(k.fontMetrics().horizontalAdvance(z) for z in _zweizeilig(_kurz(name)).split("\n"))
            k.setMinimumWidth(max(44 if self.kompakt else 48, breit + (6 if self.kompakt else 10)))
            k.setFixedHeight(self.GROSS_HOEHE[self.kompakt])
        elif icons.hat(sym) and e.get("text"):
            k.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            k.setText(_kurz(name))
        elif icons.hat(sym):
            k.setToolButtonStyle(Qt.ToolButtonIconOnly)
            k.setMinimumWidth(MIN_KNOPF)                                # Projektvorgabe: Knöpfe nicht schmaler als ~36 px
        else:
            k.setMinimumWidth(max(MIN_KNOPF, 40) if (klappe or menue) else MIN_KNOPF)
        ok = False
        menu = None
        if menue:
            menu = QMenu(k)
            ok = self._menue_fuellen(menu, menue)
            k.setPopupMode(QToolButton.MenuButtonPopup)             # Symbol und Pfeil getrennt: der Pfeil sitzt nicht im Symbol
            akt.triggered.connect(lambda _=False, kk=k: kk.showMenu())
        elif klappe and (menu := self._klappe(klappe)) is not None:
            menu.setParent(k, Qt.Popup)
            k.setPopupMode(QToolButton.MenuButtonPopup)
            if not tun:
                akt.triggered.connect(lambda _=False, kk=k: kk.showMenu())
            ok = True
        if menu is not None:
            k.setMenu(menu)
            if gross:
                k.setMinimumWidth(k.minimumWidth() + 12)
                # (Platz für den Pfeil-Bereich, damit die Beschriftung nicht gekürzt wird)
        if tun:
            ok = ok or self.b.hat(tun)
            akt.triggered.connect(lambda _=False, t=tun, kk=k: (self.b.tun(t, kk), self.aktualisieren()))
        elif not menu:
            ok = False
        if tun and self.b.symbolname(tun) is not None:
            self.wechsler.append((k, tun))
            akt.setIcon(icons.icon(self.b.symbolname(tun), k.iconSize().width()))
        if e.get("haken") or (tun and self.b.zustand(tun) is not None):
            akt.setCheckable(True)
            self.schalter.append((k, tun))
        for n in (tun, klappe):
            if n and not self.b.hat(n) and not (n == klappe and (n in KLAPPEN or self.b.klappe(n) is not None)):
                self.fehlend.append(n)
        if not ok:
            k.setProperty("fehlt", True)
            k.setEnabled(False)
            k.setToolTip(NICHT_DA.format(name))
        self.knoepfe.append((k, tun, True))
        return k

    def _klappe(self, name: str):
        """Das Menü einer Klappe: erst die Bausteine der Oberfläche (``KLAPPEN``), sonst ``menue_<name>`` des Befehlsbausteins."""
        bau = KLAPPEN.get(name)
        return bau(self.b) if bau else self.b.klappe(name)

    def _menue_fuellen(self, menu: QMenu, items: list) -> bool:
        ok = False
        for it in items:
            if it.get("trenner"):
                menu.addSeparator()
            elif it.get("menue"):
                sub = menu.addMenu(it["name"])
                ok |= self._menue_fuellen(sub, it["menue"])
            elif it.get("klappe"):                           # das vorhandene Klappmenü eines anderen Knopfes als Untermenü (mehrere Knöpfe hinter einem)
                sub = self._klappe(it["klappe"])
                if sub is not None:
                    sub.setTitle(it["name"])
                    sub.setParent(menu, Qt.Popup)
                    menu.addMenu(sub)
                    ok = True
                else:
                    self.fehlend.append(it["klappe"])
            elif it.get("name"):
                a = menu.addAction(it["name"])
                t = it.get("tun")
                if t and self.b.hat(t):
                    if it.get("haken"):
                        a.setCheckable(True)
                        menu.aboutToShow.connect(lambda a=a, it=it: a.setChecked(bool(self.b.haken_wert(it))))
                        a.triggered.connect(lambda _=False, t=t, it=it: self.b.haken_wert(it) or self.b.tun(t))
                    else:
                        a.triggered.connect(lambda _=False, t=t: self.b.tun(t))
                    ok = True
                else:
                    a.setEnabled(False)
                    a.setToolTip(NICHT_DA.format(it["name"]))
                    if t:
                        self.fehlend.append(t)
        return ok

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
