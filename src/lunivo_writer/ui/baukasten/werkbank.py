"""Werkbank: die Funktionen eines Reiters der Schreibhilfe als große, selbsterklärende Zeilen (Symbol, Name, Hinweis, Tastenkürzel, bei Schaltern „an/aus“).

Die Zeilen kommen aus ``ui/schreibhilfe_katalog.py`` und rufen dieselben Befehle wie das Band. Nichts ist grau ohne Weg weiter: Fehlt etwas (Text, KI), führt der Klick
in das passende Fenster oder erklärt es — die Befehle selbst sorgen dafür."""
from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from lunivo_writer.ui.baukasten.karten_raster import KartenRaster
from lunivo_writer.ui.schreibhilfe_katalog import Funktion, fuer_reiter
from lunivo_writer.ui.widgets import icons

from lunivo_writer.core.farben import Farbe
ZEILE = (('QFrame#funktionsZeile { border: 1px solid palette(midlight); border-radius: 8px; background: transparent; }QFrame#funktionsZeile:hover { background: palette(alternate-base); border-color: palette(mid); }QFrame#funktionsZeile:focus { border: 2px solid ' + Farbe.AKZENT + '; }'))
CHIP_B, CHIP_H = 52, 26                      # Schalter-Chip „an/aus“: feste, großzügige Größe (Kapsel, Radius = halbe Höhe)


def _an() -> str:
    return "background: %s; color: %s; border: 1px solid %s; border-radius: %dpx; font-weight: bold;" % (Farbe.AN, Farbe.AN_SCHRIFT, Farbe.AN, CHIP_H // 2)



AUS = "background: transparent; color: palette(mid); border: 1px solid palette(mid); border-radius: %dpx;" % (CHIP_H // 2)


class FunktionsZeile(QFrame):
    """Eine große, anklickbare Zeile; mit Tastatur bedienbar (Tab, Leertaste oder Eingabe) und mit Fokusrahmen."""
    clicked = Signal()

    def __init__(self, f: Funktion, fenster):
        super().__init__()
        self.setObjectName("funktionsZeile")
        self.f, self.fenster = f, fenster
        self.setStyleSheet(ZEILE)
        self.setMinimumHeight(0)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAccessibleName(f.name)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        h = QHBoxLayout(self); h.setContentsMargins(8, 3, 8, 3); h.setSpacing(8)
        sym = QLabel(); sym.setFixedWidth(22); sym.setAttribute(Qt.WA_TransparentForMouseEvents)
        if icons.hat(f.symbol):
            sym.setPixmap(icons.icon(f.symbol, 22).pixmap(22, 22))
            sym.setProperty("symbolName", f.symbol); sym.setProperty("symbolPx", 22)       # Farbwechsel: Symbol neu beziehen (icons.alle_neu)
        h.addWidget(sym)
        mitte = QVBoxLayout(); mitte.setSpacing(0); mitte.addStretch(1)                 # überschüssige Höhe (gleiche Zeileneinheit) verteilt sich oben und unten, nichts wird gestreckt
        self.titel = QLabel(f.name); ft = self.titel.font(); ft.setBold(True); self.titel.setFont(ft)
        self.untertitel = QLabel(f.hinweis); self.untertitel.setStyleSheet("color: palette(mid); font-size: 9pt;"); self.untertitel.setWordWrap(True)
        for w in (self.titel, self.untertitel):
            w.setAttribute(Qt.WA_TransparentForMouseEvents)
        kopf = QHBoxLayout(); kopf.setSpacing(8); kopf.addWidget(self.titel)                 # Titelzeile: Name, rechts daneben das Kürzel; der Hinweis darunter hat die volle Breite
        if f.kuerzel:
            k = QLabel(f.kuerzel); k.setStyleSheet("color: palette(mid); font-size: 8pt; border: 1px solid palette(midlight); border-radius: 3px; padding: 0 5px;")
            k.setAttribute(Qt.WA_TransparentForMouseEvents); kopf.addWidget(k, 0, Qt.AlignVCenter)
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
            pf = QLabel(); pf.setPixmap(icons.icon("chevron-down", 14).pixmap(14, 14)); pf.setAttribute(Qt.WA_TransparentForMouseEvents); h.addWidget(pf, 0, Qt.AlignVCenter)
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
        b.tun(self.f.tun, self)
        self.aktualisieren()

    def _beschreibung(self, an: bool | None = None) -> str:
        """Was ein Bildschirmleser zusätzlich zum Namen hört: Art, Zustand, Hinweis, Kürzel."""
        teile = {"schalter": "Schalter, " + ("an" if an else "aus"), "menue": "Menü, öffnet mit Eingabe oder Leertaste"}.get(self.f.art, "Knopf, Eingabe oder Leertaste führt aus")
        return ". ".join(t for t in (teile, self.f.hinweis, f"Tastenkürzel {self.f.kuerzel}" if self.f.kuerzel else "") if t)

    def aktualisieren(self) -> None:
        if self.f.art == "schalter":
            an = bool(self.fenster.befehle.zustand(self.f.tun))
            self.zustand.setText("an" if an else "aus"); self.zustand.setStyleSheet(_an() if an else AUS)
            self.setAccessibleDescription(self._beschreibung(an))
        else:
            self.setAccessibleDescription(self._beschreibung())
        if self.f.tun == "w.kiUebersetzen":
            self.untertitel.setText("Nach " + self.fenster.ki.konfig["sprache"])


class Werkbank(QScrollArea):
    """Die Zeilen eines Reiters; ``oben`` (optional) ist ein Widget über den Zeilen, etwa ein Hinweis."""

    def __init__(self, fenster, reiter: str, oben: QWidget | None = None, nur: set | None = None):
        super().__init__()
        self.setWidgetResizable(True); self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        host = QWidget(); v = QVBoxLayout(host); v.setContentsMargins(8, 6, 8, 6); v.setSpacing(4)
        if oben is not None:
            v.addWidget(oben)
        self.zeilen = [FunktionsZeile(f, fenster) for f in fuer_reiter(reiter) if nur is None or f.tun in nur]
        raster = KartenRaster(abstand=6, spalten_fest=1)              # Raster-Baustein, eine Spalte untereinander; alle Karten gleich groß (gleiche Zeileneinheit)
        for z in self.zeilen:
            raster.addWidget(z)
        v.addLayout(raster)
        v.addStretch(1)
        self.setWidget(host)

    def aktualisieren(self) -> None:
        for z in self.zeilen:
            z.aktualisieren()
