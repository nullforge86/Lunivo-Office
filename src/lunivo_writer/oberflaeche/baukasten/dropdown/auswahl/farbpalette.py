"""Die eine Farbpalette des Programms: Popup, Farbfeld für Dialoge und geteilter Knopf fürs Band.

Das Popup kennt seinen Aufrufer nicht — es meldet nur eine Farbe (oder ``None`` für „Keine Farbe“) und lässt den
Aufrufer damit tun, was er will: Schriftfarbe, Schattierung, Seitenfarbe, Rahmen, Füllung …
"""
from __future__ import annotations

from PySide6.QtCore import QPoint, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QLabel, QLayout, QMenu, QPushButton, QToolButton, QVBoxLayout, QWidget, QWidgetAction,
)

from lunivo_writer.oberflaeche.baukasten.basis.texte import hinweis_stil
from lunivo_writer.oberflaeche.baukasten.basis import farben as F
from lunivo_writer.oberflaeche.baukasten.felder.karten_raster import kachel_gitter


from lunivo_writer.kern.farben import Farbe
from lunivo_writer.oberflaeche.bauteile import symbole
from lunivo_writer.oberflaeche.baukasten.basis.mass import DROPDOWN_FARBKACHEL, DROPDOWN_HOEHE, DROPDOWN_INNEN_FARBE, SCHRIFT_GRUPPENTITEL_PX, ABSTAND_ENG, ABSTAND_KLEIN, ICON_KLEIN, ICON_MITTEL, PADDING_PALETTE_TITEL_OBEN, RAND_KEIN, RAND_PANEL_KLEIN
from lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste import MenueListe
def weitere_farben(parent, start=None, titel: str = "Farbe") -> QColor | None:
    """„Weitere Farben …“: das Fenster „Farben“ (Standard · Benutzerdefiniert · Erweitert). Gibt die Farbe zurück oder ``None`` bei Abbruch."""
    from lunivo_writer.oberflaeche.baukasten.felder.farbwaehler import FarbenDialog
    d = FarbenDialog(parent, start, titel)
    if not d.exec():
        return None
    c = d.farbe()
    F.zuletzt_merken(c.name())
    return c


def weitere_farben_unter(parent, fertig, start=None, titel: str = "Farbe") -> None:
    """Wie ``weitere_farben``, aber als Unterfenster: Liegt ``parent`` in einem ``FensterStapel``, öffnet sich „Farben“ als Seite im selben Fenster;
    ``fertig(farbe)`` läuft nach „OK“ (sonst öffnet sich das Fenster wie bisher)."""
    from lunivo_writer.oberflaeche.baukasten.felder.farbwaehler import FarbenDialog
    from lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel import zeige_unter
    d = FarbenDialog(parent, start, titel)

    def ok() -> None:
        c = d.farbe()
        F.zuletzt_merken(c.name())
        fertig(c)
    zeige_unter(parent, d, ok)


def farb_symbol(farbe: str | None, groesse: int = 14) -> QIcon:
    pm = QPixmap(groesse, groesse)
    pm.fill(QColor(farbe) if farbe else Qt.transparent)
    return QIcon(pm)


class _Kachel(QWidget):
    """Ein Farbfeld der Palette; meldet Überfahren und Klick an die Palette."""

    def __init__(self, palette: "FarbPalette", farbe: str, seite: int = DROPDOWN_FARBKACHEL):
        super().__init__()
        self._p, self.farbe, self._an = palette, farbe, False
        self.setFixedSize(seite, seite)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(farbe)

    def enterEvent(self, e):
        self._an = True; self.update(); self._p.ueberfahren.emit(QColor(self.farbe))

    def leaveEvent(self, e):
        self._an = False; self.update(); self._p.verlassen.emit()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self.rect().contains(e.position().toPoint()):
            self._p.waehle(QColor(self.farbe))

    def paintEvent(self, e):
        p = QPainter(self)
        r = QRectF(self.rect()).adjusted(DROPDOWN_INNEN_FARBE, DROPDOWN_INNEN_FARBE, -DROPDOWN_INNEN_FARBE, -DROPDOWN_INNEN_FARBE)
        p.fillRect(r, QColor(self.farbe))
        pal = self.palette()
        stift = QPen(pal.highlight().color() if self._an else pal.mid().color(), 2 if self._an else 1)
        p.setPen(stift); p.setBrush(Qt.NoBrush); p.drawRect(r)


class _VerlaufKachel(_Kachel):
    """Kachel der Zeile „Graduelle Füllung“: ein Farbverlauf von hell nach dunkel in der Farbe; ein Klick meldet die Farbe als Verlauf."""

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self.rect().contains(e.position().toPoint()):
            self._p.verlauf_gewaehlt.emit(QColor(self.farbe)); self._p.close()

    def paintEvent(self, e):
        from PySide6.QtGui import QLinearGradient
        p = QPainter(self)
        r = QRectF(self.rect()).adjusted(DROPDOWN_INNEN_FARBE, DROPDOWN_INNEN_FARBE, -DROPDOWN_INNEN_FARBE, -DROPDOWN_INNEN_FARBE)
        g = QLinearGradient(r.topLeft(), r.bottomRight())
        g.setColorAt(0, QColor(self.farbe).lighter(150)); g.setColorAt(1, QColor(self.farbe).darker(140))
        p.fillRect(r, g)
        pal = self.palette()
        p.setPen(QPen(pal.highlight().color() if self._an else pal.mid().color(), 2 if self._an else 1)); p.setBrush(Qt.NoBrush); p.drawRect(r)


class _BildKachel(_Kachel):
    """Kachel einer Bildreihe („Musterfüllung“, „Strukturfüllung“): zeigt ein Bild; ein Klick meldet ihren Schlüssel."""

    def __init__(self, palette: "FarbPalette", schluessel: str, bild: QPixmap, tipp: str, seite: int = DROPDOWN_FARBKACHEL):
        super().__init__(palette, schluessel, seite)
        self._bild = bild; self.setToolTip(tipp)

    def enterEvent(self, e):
        self._an = True; self.update()

    def leaveEvent(self, e):
        self._an = False; self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self.rect().contains(e.position().toPoint()):
            self._p.reihe_gewaehlt.emit(self.farbe); self._p.close()

    def paintEvent(self, e):
        p = QPainter(self)
        r = QRectF(self.rect()).adjusted(DROPDOWN_INNEN_FARBE, DROPDOWN_INNEN_FARBE, -DROPDOWN_INNEN_FARBE, -DROPDOWN_INNEN_FARBE)
        p.drawPixmap(r.toRect(), self._bild)
        pal = self.palette()
        p.setPen(QPen(pal.highlight().color() if self._an else pal.mid().color(), 2 if self._an else 1)); p.setBrush(Qt.NoBrush); p.drawRect(r)


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
        v = QVBoxLayout(wid)
        v.setContentsMargins(*RAND_PANEL_KLEIN); v.setSpacing(ABSTAND_KLEIN)
        if keine_text:
            keine = QPushButton(keine_text); keine.setFlat(True); keine.setProperty("listenzeile", True)
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
            auto = QPushButton(automatisch); auto.setFlat(True); auto.setProperty("listenzeile", True)
            pm = QPixmap(14, 14); pm.fill(QColor(Farbe.SCHWARZ)); auto.setIcon(QIcon(pm)); auto.clicked.connect(lambda: self.waehle(QColor(Farbe.SCHWARZ)))
            v.addWidget(auto)
        if weitere:
            mehr = QPushButton(weitere_text); mehr.setFlat(True); mehr.setProperty("listenzeile", True); mehr.setIcon(symbole.icon("palette", ICON_KLEIN))
            mehr.clicked.connect(self._weitere)
            v.addWidget(mehr)
            from lunivo_writer.oberflaeche.baukasten.felder import pipette as _pip
            if _pip.AKTIV and pipette:
                pip = QPushButton("Pipette"); pip.setFlat(True); pip.setProperty("listenzeile", True); pip.setIcon(symbole.icon("pipette", ICON_KLEIN))
                pip.clicked.connect(self._pipette)
                v.addWidget(pip)
        self._spalte = v
        self.widget(wid)

    def zusatz_eintrag(self, text: str, aktion) -> None:
        """Ein weiterer Eintrag unter „Weitere Farben …“ (z. B. „Rahmen und Schattierung …“); schließt die Palette und ruft ``aktion``."""
        k = QPushButton(text); k.setFlat(True); k.setProperty("listenzeile", True)
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
        from lunivo_writer.oberflaeche.baukasten.felder.pipette import farbe_vom_bildschirm
        self.close()
        c = farbe_vom_bildschirm(self.parentWidget())
        if c is not None:
            F.zuletzt_merken(c.name())
            self.gewaehlt.emit(c)

    def _weitere(self) -> None:
        self.close()
        weitere_farben_unter(self.parentWidget(), self.gewaehlt.emit, self._start, self._titel)


class FarbFeld(QPushButton):
    """Knopf für Dialoge, der seine Farbe zeigt; ein Klick öffnet die Palette. ``farbe`` ist ein Hex-Text ('' = keine)."""

    farbeGeaendert = Signal(str)
    verlaufGewaehlt = Signal(str)          # Farbe, die als Farbverlauf gemeint ist (nur mit ``verlauf=True``)

    def __init__(self, farbe: str | None = None, titel: str = "Farbe", keine_text: str | None = None, parent=None, verlauf: bool = False):
        super().__init__(parent)
        self.setMinimumHeight(DROPDOWN_HOEHE); self.setProperty("dropdownFeld", True)          # Höhe wie jedes Dropdown
        farbe = Farbe.SCHWARZ if farbe is None else farbe
        self.farbe, self.titel, self.keine_text, self._verlauf = farbe, titel, keine_text, verlauf
        self.clicked.connect(self._waehle)
        self._zeige()

    def setFarbe(self, farbe: str) -> None:
        self.farbe = farbe
        self._zeige()

    def _waehle(self) -> None:
        pal = FarbPalette(self, keine_text=self.keine_text, start=self.farbe or None, titel=self.titel, verlauf=self._verlauf)
        pal.gewaehlt.connect(self._uebernehmen)
        pal.verlauf_gewaehlt.connect(lambda c: self.verlaufGewaehlt.emit(c.name()))
        self._zeige_popup(pal)

    def _zeige_popup(self, pal: QMenu) -> None:
        pal.exec(self.mapToGlobal(QPoint(0, self.height())))

    def _uebernehmen(self, c: QColor | None) -> None:
        self.farbe = c.name() if c is not None else ""
        self._zeige()
        self.farbeGeaendert.emit(self.farbe)

    def _zeige(self) -> None:
        """Ruhig und sachlich: ein kleines Farbfeld mit Rand und der Name daneben — kein Knopf, der selbst bunt wird."""
        if not self.farbe:
            self.setText(self.keine_text or "Keine")
            pm = QPixmap(14, 14); pm.fill(Qt.transparent)
            p = QPainter(pm); p.setPen(QPen(QColor(Farbe.GRAU), 1)); p.drawRect(0, 0, 13, 13); p.drawLine(0, 13, 13, 0); p.end()
            self.setIcon(QIcon(pm))
        else:
            self.setText(self.farbe.upper())
            pm = QPixmap(14, 14); pm.fill(QColor(self.farbe))
            p = QPainter(pm); p.setPen(QPen(QColor(Farbe.GRAU), 1)); p.setBrush(Qt.NoBrush); p.drawRect(0, 0, 13, 13); p.end()
            self.setIcon(QIcon(pm))
        self.setProperty("feldknopf", True)


class FarbKnopf(QToolButton):
    """Geteilter Knopf fürs Band: Klick auf das Symbol wendet die letzte Farbe an, der Pfeil klappt die Palette auf."""

    angewendet = Signal(object)      # QColor oder None

    def __init__(self, symbol: QIcon | None = None, text: str = "", farbe: str | None = None, *, keine_text: str | None = "Keine Farbe",
                 titel: str = "Farbe", parent=None):
        super().__init__(parent)
        farbe = Farbe.ROT if farbe is None else farbe
        self._symbol, self.farbe, self._titel, self._keine = symbol, farbe, titel, keine_text
        self.setText(text); self.setToolTip(text or titel)
        self.setPopupMode(QToolButton.MenuButtonPopup)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly if symbol else Qt.ToolButtonTextOnly)
        self.setIconSize(QSize(ICON_MITTEL, ICON_MITTEL))
        self.clicked.connect(lambda: self.angewendet.emit(QColor(self.farbe)))
        self.menu_neu()
        self._balken()

    def menu_neu(self) -> None:
        pal = FarbPalette(self, keine_text=self._keine, start=self.farbe, titel=self._titel)
        pal.gewaehlt.connect(self._gewaehlt)
        self.setMenu(pal)
        self._palette = pal

    def _gewaehlt(self, c: QColor | None) -> None:
        if c is not None:
            self.farbe = c.name(); self._balken()
        self.angewendet.emit(c)
        self.menu_neu()                                   # „Zuletzt benutzt“ aktualisieren

    def _balken(self) -> None:
        if self._symbol is None:
            return
        pm = self._symbol.pixmap(ICON_MITTEL, ICON_MITTEL)
        p = QPainter(pm); p.fillRect(2, pm.height() - 5, pm.width() - 4, 4, QColor(self.farbe)); p.end()
        self.setIcon(QIcon(pm))
