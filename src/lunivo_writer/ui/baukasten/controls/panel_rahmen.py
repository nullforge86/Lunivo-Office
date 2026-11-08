"""Rahmen eines Feldes in einer Seitenleiste: Titel, davor/dahinter Knöpfe, ein Menü (⋯ oder ⚙) und ✕ zum Schließen; darunter der Inhalt.

Dieselbe Hülle für alle Felder links (Suchen und ersetzen, Kommentare, Überschriften …): gleiche Kopfzeile, gleiche Abstände, gleiche Bedienung."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMenu, QToolButton, QVBoxLayout, QWidget
from lunivo_writer.ui.widgets import icons
from lunivo_writer.ui.baukasten.basis.texte import trennlinie
from lunivo_writer.ui.baukasten.basis.mass import ABSTAND_MITTEL, ICON_NORMAL, RAND_KEIN
from lunivo_writer.ui.baukasten.dropdown.dropdown_knopf import DropdownKnopf


PANEL_KOPF_RAND = (14, 8, 8, 8)           # Rand der Kopfzeile eines Seitenleistenfensters (links, oben, rechts, unten)
PANEL_INHALT_RAND = (14, 10, 14, 10)      # Rand des Inhalts darunter
PANEL_KOPF_ABSTAND = 2                    # Abstand zwischen Titel und Knöpfen der Kopfzeile


def panel_kopf(*teile: QWidget, dehnen: QWidget | None = None) -> QWidget:
    """Die Kopfzeile aller Seitenleistenfenster samt Trennlinie darunter: ``teile`` von links nach rechts.
    ``dehnen`` nimmt den freien Platz; ohne Angabe jedes QLabel. Benutzt von ``PanelRahmen``, ``zusatz_kopf`` (Zusatzfenster, Formatierung)."""
    ganz = QWidget(); gv = QVBoxLayout(ganz); gv.setContentsMargins(*RAND_KEIN); gv.setSpacing(0)
    kopf = QWidget(); h = QHBoxLayout(kopf); h.setContentsMargins(*PANEL_KOPF_RAND); h.setSpacing(PANEL_KOPF_ABSTAND)
    for t in teile:
        h.addWidget(t, 1 if (t is dehnen if dehnen is not None else isinstance(t, QLabel)) else 0)
    gv.addWidget(kopf)
    gv.addWidget(trennlinie())
    return ganz


def _knopf(symbol: str, tipp: str) -> DropdownKnopf:
    b = DropdownKnopf()
    if icons.hat(symbol): b.setIcon(icons.icon(symbol, ICON_NORMAL))
    else: b.setText(symbol); b.setStyleSheet("QToolButton { font-weight: bold; }")          # kein Symbol dieses Namens: der Text selbst (z. B. „?“)
    b.setToolTip(tipp); b.setAccessibleName(tipp); b.setAutoRaise(True); b.setCursor(Qt.PointingHandCursor)
    b.groesse_rolle("panel", "kopf")
    return b


class PanelRahmen(QWidget):
    schliessen = Signal()

    def __init__(self, titel: str, menue_zeichen: str = "", menue: QMenu | None = None, knoepfe: tuple = (),
                 schliessbar: bool = True, titel_teile: tuple = ()):
        """``knoepfe``: Folge von (Lucide-Name oder Text, Tooltip, Funktion) — stehen vor dem Menü.
        ``schliessbar=False`` blendet ✕ aus. ``titel_teile``: ((Text, Farbtoken oder Farbe oder None), …) für einen mehrfarbigen Titel."""
        super().__init__()
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_KEIN); v.setSpacing(0)
        self.titel = QLabel(titel); f = self.titel.font(); f.setBold(True); f.setPointSizeF(f.pointSizeF() + 1); self.titel.setFont(f)
        if titel_teile:
            from lunivo_writer.core.farben import Farbe
            self.titel = QWidget(); t = QHBoxLayout(self.titel); t.setContentsMargins(*RAND_KEIN); t.setSpacing(0)
            for teil, farbe in titel_teile:
                lb = QLabel(teil); lb.setFont(f)
                if farbe == "AKZENT": lb.setProperty("akzentSchrift", True)                       # Akzentfarbe nur aus dem Thema (ui/theme.py)
                elif farbe: lb.setStyleSheet("color: %s;" % getattr(Farbe, farbe, farbe))          # Farbe erst jetzt lesen (Thema gilt)
                t.addWidget(lb)
            t.addStretch(1)
        teile = [self.titel]
        self.knoepfe = []
        for zeichen, tipp, fn in knoepfe:
            b = _knopf(zeichen, tipp); b.clicked.connect(lambda _=False, fn=fn: fn()); teile.append(b); self.knoepfe.append(b)
        self.menue_knopf = None
        if menue is not None:
            self.menue_knopf = _knopf(menue_zeichen or "ellipsis", "Weitere Einstellungen")
            self.menue_knopf.menue_setzen(menue, geteilt=False)
            teile.append(self.menue_knopf)
        zu = _knopf("x", "Schließen"); zu.clicked.connect(self.schliessen.emit); teile.append(zu); zu.setVisible(schliessbar)
        v.addWidget(panel_kopf(*teile, dehnen=self.titel))
        self.inhalt = QVBoxLayout(); self.inhalt.setContentsMargins(*PANEL_INHALT_RAND); self.inhalt.setSpacing(ABSTAND_MITTEL)
        v.addLayout(self.inhalt, 1)


def rollflaeche(inhalt: QWidget | None = None, *, immer: bool = False):
    """Der Rollbereich in Seitenleisten-Panels: ohne Rahmen, nie seitlich rollend, Rollbalken nach Bedarf — mit ``immer=True`` steht er immer
    (die Werkbank: alle Seiten haben dann gleich breite Karten). EINE Stelle für alle Rollbereiche der Panels."""
    from PySide6.QtWidgets import QScrollArea
    sa = QScrollArea()
    sa.setWidgetResizable(True)
    sa.setFrameShape(QFrame.NoFrame)
    sa.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    if immer:
        sa.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    if inhalt is not None:
        sa.setWidget(inhalt)
    return sa
