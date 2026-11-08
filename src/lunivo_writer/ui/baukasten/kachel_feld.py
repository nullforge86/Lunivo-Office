"""Beschriftete Kacheln zum Anklicken, immer genau eine gewählt (zum Beispiel die Umbruchart eines Bildes).

    k = KachelFeld(spalten=4, groesse=QSize(44, 44))
    k.hinzu("quadrat", "Quadrat", zeichner)          # zeichner: f(QPainter, QRectF), QIcon oder QPixmap
    k.gewaehlt.connect(lambda schluessel: ...)

Tastatur: Tab erreicht das Feld einmal (die gewählte Kachel, sonst die erste), Pfeiltasten bewegen den Fokus,
Leertaste oder Eingabe wählen. Jede Kachel trägt ihren Text als Namen für Bildschirmleser.
"""
from __future__ import annotations

from PySide6.QtCore import QEvent, QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QToolButton, QWidget

from lunivo_writer.ui.baukasten.karten_raster import kachel_gitter
from lunivo_writer.ui.baukasten.dropdown.raster_auswahl import _symbol
from lunivo_writer.ui.baukasten.mass import ABSTAND_KLEIN, GROESSE_KACHELFELD_STANDARD, RADIUS_KLEIN, RAND_KEIN


class KachelFeld(QWidget):
    gewaehlt = Signal(str)

    def __init__(self, parent=None, *, spalten: int = 4, groesse: QSize = QSize(*GROESSE_KACHELFELD_STANDARD), mit_text: bool = True, fliessend: bool = False):
        super().__init__(parent)
        self._spalten, self._groesse, self._text, self._fliessend = spalten, groesse, mit_text, fliessend
        self._gitter = kachel_gitter((), spalten, eltern=self, abstand=ABSTAND_KLEIN)
        self.knoepfe: dict[str, QToolButton] = {}
        self._aktuell: str | None = None
        self.setStyleSheet("QToolButton:focus { border: 2px solid palette(highlight); border-radius: " f"{RADIUS_KLEIN}" "px; }")

    def hinzu(self, schluessel: str, text: str, bild=None) -> QToolButton:
        b = QToolButton(); b.setCheckable(True); b.setAutoRaise(True); b.setFocusPolicy(Qt.ClickFocus)
        b.setAccessibleName(text); b.installEventFilter(self)
        b.setIcon(_symbol(bild, self._groesse) if bild is not None else QIcon()); b.setIconSize(self._groesse)
        b.setToolTip(text)
        if self._text:
            b.setText(text); b.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        b.clicked.connect(lambda _c=False, k=schluessel: self.setze(k, True))
        n = len(self.knoepfe)
        self._gitter.addWidget(b, n // self._spalten, n % self._spalten)
        self.knoepfe[schluessel] = b
        self._fokus_ziel()
        return b

    def _neu_legen(self, spalten: int) -> None:
        """Kacheln in ``spalten`` Spalten neu ins Raster setzen (nur Anordnung, Auswahl und Signale bleiben)."""
        self._spalten = spalten
        for b in self.knoepfe.values():
            self._gitter.removeWidget(b)
        for n, b in enumerate(self.knoepfe.values()):
            self._gitter.addWidget(b, n // spalten, n % spalten)

    def minimumSizeHint(self) -> QSize:
        if self._fliessend and self.knoepfe:
            return next(iter(self.knoepfe.values())).sizeHint()
        return super().minimumSizeHint()

    def resizeEvent(self, ev) -> None:
        """Mit ``fliessend=True`` so viele Spalten, wie in die Breite passen (``spalten`` ist das Höchstmaß)."""
        super().resizeEvent(ev)
        if self._fliessend and self.knoepfe:
            zelle = max(b.sizeHint().width() for b in self.knoepfe.values()) + self._gitter.spacing()
            n = max(1, min(len(self.knoepfe), int((ev.size().width() + self._gitter.spacing()) // zelle)))
            if n != self._spalten:
                self._neu_legen(n)

    def _fokus_ziel(self) -> None:
        """Nur eine Kachel ist per Tab erreichbar: die gewählte, sonst die erste."""
        ziel = self._aktuell if self._aktuell in self.knoepfe else next(iter(self.knoepfe), None)
        for k, b in self.knoepfe.items():
            b.setFocusPolicy(Qt.StrongFocus if k == ziel else Qt.ClickFocus)

    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.KeyPress and obj in self.knoepfe.values():
            schluessel = list(self.knoepfe)
            i = list(self.knoepfe.values()).index(obj)
            if ev.key() in (Qt.Key_Return, Qt.Key_Enter):
                obj.click(); return True
            schritt = {Qt.Key_Left: -1, Qt.Key_Right: 1, Qt.Key_Up: -self._spalten, Qt.Key_Down: self._spalten}.get(ev.key())
            if schritt is not None:
                j = i + schritt
                if 0 <= j < len(schluessel):
                    self.knoepfe[schluessel[j]].setFocus(Qt.TabFocusReason)
                return True
        return super().eventFilter(obj, ev)

    def setze(self, schluessel: str | None, melden: bool = False) -> None:
        self._aktuell = schluessel
        for k, b in self.knoepfe.items():
            b.setChecked(k == schluessel)
        self._fokus_ziel()
        if melden and schluessel is not None:
            self.gewaehlt.emit(schluessel)

    def aktuell(self) -> str | None:
        return self._aktuell
