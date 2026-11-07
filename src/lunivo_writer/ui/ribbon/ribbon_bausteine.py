"""Hilfswidgets und Kurztexte des Menübandes."""
from __future__ import annotations

from PySide6.QtCore import QPropertyAnimation, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QCheckBox, QScrollArea, QSizePolicy, QToolButton, QWidget

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.flache_reiter_leiste import UeberlaufLeiste
from lunivo_writer.ui.baukasten.mass import BREITE_GRUPPENTRENNER, PADDING_BANDKNOPF, SCHRIFT_BANDKNOPF


class _GruppenTrenner(QWidget):
    """Dezenter Gruppentrenner im Band: genau ein physischer Bildpunkt breit, oben und unten eingerückt, Farbe aus der aktuellen Palette
    (Bandhintergrund leicht zur Mittelfarbe gemischt); folgt dem Themenwechsel von selbst, weil bei jedem Zeichnen neu gemischt wird."""
    EINRUECKEN = 6
    MISCHUNG = 0.30

    def __init__(self):
        super().__init__()
        self.setFixedWidth(BREITE_GRUPPENTRENNER)
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
            b.setCursor(Qt.ArrowCursor); b.setFocusPolicy(Qt.StrongFocus)
            b.setToolTip("Weiter nach " + seite); b.setAccessibleName("Band nach " + seite + " blättern")
            b.setStyleSheet("QToolButton { border: none; border-radius: 0; font-size: " f"{SCHRIFT_BANDKNOPF}" "pt; font-weight: 600; padding: " f"{PADDING_BANDKNOPF}" "; "
                            "background: palette(window); color: palette(window-text); }"
                            "QToolButton:hover { background: palette(midlight); }"
                            "QToolButton:focus { border: 2px solid palette(highlight); }")
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


class _ReiterLeiste(UeberlaufLeiste):
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
        akzent = QColor(Farbe.KONTEXT or (Farbe.AKZENT_DUNKEL if dunkel else Farbe.AKZENT))
        erster = True
        for i in range(self.count()):
            if not self.gezeigt(i) or not self.ist_kontext(i):
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
            p.setPen(QColor(Farbe.KONTEXT_SCHRIFT) if aktiv else (QColor(Farbe.KONTEXT_TEXT) if dunkel else akzent))
            p.drawText(r, Qt.AlignCenter, self.tabText(i))
        p.end()


class _SperrKasten(QCheckBox):
    """Kontrollkästchen „Seitenverhältnis sperren“: Klick ruft ``bildSeitenverhaeltnis``; ``auffrischen`` holt den Zustand vom Bild."""

    def __init__(self, text: str, befehle):
        super().__init__(text)
        self._b = befehle
        self.clicked.connect(self._klick)

    def _klick(self, an: bool):
        if bool(self._b.an_bildSeitenverhaeltnis()) != an:
            self._b.bildSeitenverhaeltnis()
        self.auffrischen()

    def auffrischen(self):
        an = bool(self._b.an_bildSeitenverhaeltnis())
        if an != self.isChecked():
            self.blockSignals(True); self.setChecked(an); self.blockSignals(False)


class _FelderDict(dict):
    """Felder des Bandes: Reiter werden erst nach dem Anzeigen fertig gebaut; wer ein noch fehlendes Feld braucht, bekommt zuerst alle Reiter."""

    def __init__(self, band):
        super().__init__()
        self._band = band

    def __missing__(self, key):
        self._band._alle_bauen()
        return dict.__getitem__(self, key)

    def get(self, key, default=None):
        if key not in self:
            self._band._alle_bauen()
        return dict.get(self, key, default)

    def __contains__(self, key):
        if not dict.__contains__(self, key):
            self._band._alle_bauen()
        return dict.__contains__(self, key)


