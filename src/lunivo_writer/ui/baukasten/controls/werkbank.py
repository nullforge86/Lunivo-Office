"""Werkbank: die Funktionen eines Reiters der Schreibhilfe als große, selbsterklärende Zeilen (Symbol, Name, Hinweis, Tastenkürzel, bei Schaltern „an/aus“).

Die Zeilen kommen aus ``ui/schreibhilfe_katalog.py`` und rufen dieselben Befehle wie das Band. Nichts ist grau ohne Weg weiter: Fehlt etwas (Text, KI), führt der Klick
in das passende Fenster oder erklärt es — die Befehle selbst sorgen dafür."""
from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from lunivo_writer.ui.baukasten.controls.karten_raster import KartenRaster
from lunivo_writer.ui.schreibhilfe_katalog import Funktion, fuer_reiter
from lunivo_writer.ui.widgets import icons

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.basis.karte import als_karte
from lunivo_writer.ui.baukasten.basis.texte import hinweis_label
from lunivo_writer.ui.baukasten.controls.schalter import CHIP_B, CHIP_H, schalter_an_stil, schalter_aus_stil
from lunivo_writer.ui.baukasten.basis.mass import ABSTAND_KLEIN, ABSTAND_MITTEL, BREITE_FUNKTIONSSYMBOL, ICON_KLEIN, ICON_MITTEL, RAND_FUNKTIONSZEILE, RAND_KEIN
_an, AUS = schalter_an_stil, schalter_aus_stil()   # alte Namen bleiben


class FunktionsZeile(QFrame):
    """Eine große, anklickbare Zeile; mit Tastatur bedienbar (Tab, Leertaste oder Eingabe) und mit Fokusrahmen."""
    clicked = Signal()

    def __init__(self, f: Funktion, fenster):
        super().__init__()
        self.setObjectName("funktionsZeile")
        self.f, self.fenster = f, fenster
        als_karte(self, "zeile")
        self.setMinimumHeight(0)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAccessibleName(f.name)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        h = QHBoxLayout(self); h.setContentsMargins(*RAND_FUNKTIONSZEILE); h.setSpacing(ABSTAND_MITTEL)
        sym = QLabel(); sym.setFixedWidth(BREITE_FUNKTIONSSYMBOL); sym.setAttribute(Qt.WA_TransparentForMouseEvents)
        if icons.hat(f.symbol):
            sym.setPixmap(icons.icon(f.symbol, ICON_MITTEL).pixmap(ICON_MITTEL, ICON_MITTEL))
            sym.setProperty("symbolName", f.symbol); sym.setProperty("symbolPx", 22)       # Farbwechsel: Symbol neu beziehen (icons.alle_neu)
        h.addWidget(sym)
        mitte = QVBoxLayout(); mitte.setSpacing(0); mitte.addStretch(1)                 # überschüssige Höhe (gleiche Zeileneinheit) verteilt sich oben und unten, nichts wird gestreckt
        self.titel = QLabel(f.name); ft = self.titel.font(); ft.setBold(True); self.titel.setFont(ft)
        self.untertitel = hinweis_label(f.hinweis, klein=True)
        for w in (self.titel, self.untertitel):
            w.setAttribute(Qt.WA_TransparentForMouseEvents)
        kopf = QHBoxLayout(); kopf.setSpacing(ABSTAND_MITTEL); kopf.addWidget(self.titel)                 # Titelzeile: nur der Name, kein Tastenkürzel im Knopf (einheitlich; das Kürzel steht in Kurzinfo und Kürzelübersicht)
        kopf.addStretch(1)
        mitte.addLayout(kopf)
        if f.hinweis:
            mitte.addWidget(self.untertitel)
        mitte.addStretch(1)
        h.addLayout(mitte, 1)
        self.zustand = QLabel(); self.zustand.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.zustand.setAlignment(Qt.AlignCenter); self.zustand.setFixedSize(CHIP_B, CHIP_H)      # „an“ und „aus“ gleich groß, nicht auf den Text gequetscht
        if f.art == "schalter":
            h.addWidget(self.zustand, 0, Qt.AlignVCenter)                  # Chip so hoch wie sein Text, nicht auf die Kartenhöhe gezogen
        elif f.art == "menue":
            pf = QLabel(); pf.setPixmap(icons.icon("chevron-down", ICON_KLEIN).pixmap(ICON_KLEIN, ICON_KLEIN)); pf.setAttribute(Qt.WA_TransparentForMouseEvents); h.addWidget(pf, 0, Qt.AlignVCenter)
        self.setToolTip(f.hinweis or f.name)
        self.clicked.connect(self._los)
        self.aktualisieren()

    def mouseReleaseEvent(self, e) -> None:
        if e.button() == Qt.LeftButton and self.rect().contains(e.position().toPoint()):
            self.clicked.emit()

    def keyPressEvent(self, e) -> None:
        if e.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.clicked.emit()
        else:
            super().keyPressEvent(e)

    def _los(self) -> None:
        b = self.fenster.befehle
        if self.f.art == "menue":
            m = b.klappe(self.f.klappe)
            if m is not None:
                m.popup(self.mapToGlobal(QPoint(0, self.height())))
                self._menue = m
            return
        fenster = self.fenster
        fenster.zusatz_seite = "links" if self._in_navigation() else "rechts"      # ein Fenster öffnet sich in der Leiste, in der man geklickt hat
        try:
            b.tun(self.f.tun, self)
        finally:
            fenster.zusatz_seite = "rechts"
        self.aktualisieren()

    def _in_navigation(self) -> bool:
        w = self.parentWidget()
        while w is not None:
            if type(w).__name__ == "NavigationPanel":
                return True
            w = w.parentWidget()
        return False

    def _beschreibung(self, an: bool | None = None) -> str:
        """Was ein Bildschirmleser zusätzlich zum Namen hört: Art, Zustand, Hinweis, Kürzel."""
        teile = {"schalter": "Schalter, " + ("an" if an else "aus"), "menue": "Menü, öffnet mit Eingabe oder Leertaste"}.get(self.f.art, "Knopf, Eingabe oder Leertaste führt aus")
        return ". ".join(t for t in (teile, self.f.hinweis, f"Tastenkürzel {self.f.kuerzel}" if self.f.kuerzel else "") if t)

    def aktualisieren(self) -> None:
        if self.f.art == "schalter":
            an = bool(self.fenster.befehle.zustand(self.f.tun))
            self.zustand.setText("an" if an else "aus"); self.zustand.setStyleSheet(schalter_an_stil() if an else schalter_aus_stil())
            self.setAccessibleDescription(self._beschreibung(an))
        else:
            self.setAccessibleDescription(self._beschreibung())
        if self.f.tun == "w.kiUebersetzenErsetzen":
            self.untertitel.setText("Nach " + self.fenster.ki.konfig["sprache"])


class Werkbank(QScrollArea):
    """Die Zeilen eines Reiters; ``oben`` (optional) ist ein Widget über den Zeilen, etwa ein Hinweis."""

    def __init__(self, fenster, reiter: str, oben: QWidget | None = None, nur: set | None = None, ohne: set | None = None):
        super().__init__()
        self.setWidgetResizable(True); self.setFrameShape(QFrame.NoFrame)
        self.setProperty("tafel", True)                                  # Fläche im Thema (Mint)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)           # der Rollbalken steht auf JEDER Seite (links und rechts): alle Karten gleich breit, gleiche Abstände
        host = QWidget(); v = QVBoxLayout(host); v.setContentsMargins(0, 0, ABSTAND_MITTEL, 0); v.setSpacing(ABSTAND_KLEIN)      # rechts Abstand zum Rollbalken
        if oben is not None:
            v.addWidget(oben)
        self.zeilen = [FunktionsZeile(f, fenster) for f in fuer_reiter(reiter) if (nur is None or f.tun in nur) and (ohne is None or f.tun not in ohne)]
        raster = KartenRaster(abstand=6, spalten_fest=1)              # Raster-Baustein, eine Spalte untereinander; alle Karten gleich groß (gleiche Zeileneinheit)
        for z in self.zeilen:
            raster.addWidget(z)
        v.addLayout(raster)
        v.addStretch(1)
        self.setWidget(host)

    def aktualisieren(self) -> None:
        for z in self.zeilen:
            z.aktualisieren()
