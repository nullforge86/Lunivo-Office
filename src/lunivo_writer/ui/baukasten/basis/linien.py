"""Linien: Stärke, Art, Farbe — als Wert, als Auswahlzeile für Dialoge und als Rahmen-Menü (unten, oben, links, rechts …)."""
from __future__ import annotations

from enum import Flag, auto

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPalette, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QWidget

from lunivo_writer.editor.linie import ALLE_SEITEN, LINIENARTEN, LINIENBREITEN, Linie  # noqa: F401
from lunivo_writer.ui.baukasten.dropdown.farbpalette import FarbFeld
from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe


from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.basis.mass import GROESSE_LINIENART_AUSWAHL_BILD, GROESSE_LINIENART_BILD, HOEHE_LINIENZEILE, RAND_KEIN
from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Auswahlfeld
from lunivo_writer.ui.baukasten.basis.mass import DROPDOWN_ZEICHEN_SCHMAL, DROPDOWN_ZEICHEN_ZAHL
def linien_symbol(art: str, groesse: QSize = QSize(*GROESSE_LINIENART_BILD), farbe: str | None = None, breite_pt: float = 1.5) -> QIcon:
    farbe = Farbe.TINTE if farbe is None else farbe
    pm = QPixmap(groesse); pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    Linie(farbe, breite_pt, art).zeichne(p, 2, groesse.height() / 2, groesse.width() - 2, groesse.height() / 2, 96 / 72)
    p.end()
    return QIcon(pm)


class LinienZeile(QWidget):
    """Eine Zeile in einem Menü: links ein Text (kann leer sein), rechts die Linie in ihrer Art und Stärke — wie die Auswahl „Linienart“ und
    „Strichart“ der Vorlage. Meldet den Klick mit ``angeklickt``."""

    angeklickt = Signal()

    def __init__(self, text: str, art: str = "einfach", breite_pt: float = 1.5, farbe: str | None = None, parent=None, maler=None):
        """``maler(painter, x0, y, x1, farbe)`` zeichnet statt einer Rahmenlinie etwas anderes, zum Beispiel eine Unterstreichungsart."""
        super().__init__(parent)
        self._text, self._art, self._breite, self._farbe, self._maler = text, art, breite_pt, farbe, maler
        self.setMouseTracking(True); self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(HOEHE_LINIENZEILE); self.setMinimumWidth(190 if text else 150)
        self._hover = False

    def enterEvent(self, e):
        self._hover = True; self.update()

    def leaveEvent(self, e):
        self._hover = False; self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.angeklickt.emit()

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        pal = self.palette()
        if self._hover:
            p.fillRect(self.rect(), pal.color(QPalette.Highlight).lighter(170) if pal.color(QPalette.Window).lightness() > 128 else pal.color(QPalette.Midlight))
        p.setPen(pal.color(QPalette.WindowText))
        rand = 10
        if self._text:
            p.drawText(QRectF(rand, 0, 70, self.height()), Qt.AlignVCenter | Qt.AlignLeft, self._text)
        x1 = rand + (80 if self._text else 0)
        farbe = self._farbe or pal.color(QPalette.WindowText).name()
        if self._maler is not None:
            self._maler(p, x1, self.height() / 2, self.width() - rand, farbe)
            return
        Linie(farbe, self._breite, self._art).zeichne(p, x1, self.height() / 2, self.width() - rand, self.height() / 2, 96 / 72)


def linien_menue_zeile(menue, text: str, art: str, breite_pt: float, aktion, maler=None) -> LinienZeile:
    """Hängt eine ``LinienZeile`` als Eintrag in ein Menü; ein Klick ruft ``aktion`` und schließt das Menü."""
    z = LinienZeile(text, art, breite_pt, maler=maler)
    menue.widget(z)
    z.angeklickt.connect(lambda: (aktion(), menue.hide(), [m.hide() for m in QApplication.topLevelWidgets() if m.isVisible() and m.inherits("QMenu")]))
    return z


class LinienWahl(QWidget):
    """Eine Zeile aus Art, Stärke und Farbe. Meldet jede Änderung als ``Linie``."""

    geaendert = Signal(object)

    def __init__(self, linie: Linie | None = None, *, arten=tuple(LINIENARTEN), breiten=LINIENBREITEN, frei: bool = False, parent=None):
        """``frei``: eine Stärke, die nicht in der Liste steht, kommt als eigener Eintrag dazu (statt auf die nächste zu runden)."""
        super().__init__(parent)
        self._frei = frei
        linie = linie or Linie()
        h = QHBoxLayout(self); h.setContentsMargins(*RAND_KEIN)
        self.art = Auswahlfeld(); self.art.setIconSize(QSize(*GROESSE_LINIENART_AUSWAHL_BILD))
        for k in arten:
            self.art.addItem(linien_symbol(k), LINIENARTEN[k][0], k)
        self.breite = Auswahlfeld()
        for b in breiten:
            self.breite.addItem(f"{b:g}".replace(".", ",") + " pt", b)
        self._n_liste = self.breite.count()
        self.farbe = FarbFeld(linie.farbe, "Linienfarbe")
        for c, n in ((self.art, DROPDOWN_ZEICHEN_SCHMAL), (self.breite, DROPDOWN_ZEICHEN_ZAHL)):                    # die Zeile darf schmal werden (300 px): Art und Stärke geben nach, die Farbe bleibt sichtbar
            c.zeichen(n)
        h.addWidget(self.art, 3); h.addWidget(self.breite, 2); h.addWidget(self.farbe, 0)
        self.setLinie(linie)
        self.art.currentIndexChanged.connect(self._aend)
        self.breite.currentIndexChanged.connect(self._aend)
        self.farbe.farbeGeaendert.connect(lambda _f: self._aend())

    def setLinie(self, linie: Linie) -> None:
        i = self.art.findData(linie.art); self.art.setCurrentIndex(max(0, i))
        self.breite.blockSignals(True)
        if self._frei:
            while self.breite.count() > self._n_liste:                   # ein früherer freier Wert fällt weg
                self.breite.removeItem(self.breite.count() - 1)
            if self.breite.findData(linie.breite_pt) < 0:
                self.breite.addItem(f"{linie.breite_pt:g}".replace(".", ",") + " pt", linie.breite_pt)
        self.breite.blockSignals(False)
        j = min(range(self.breite.count()), key=lambda k: abs(self.breite.itemData(k) - linie.breite_pt))
        self.breite.setCurrentIndex(j)
        self.farbe.setFarbe(linie.farbe)

    def linie(self) -> Linie:
        return Linie(self.farbe.farbe or Farbe.SCHWARZ, float(self.breite.currentData()), str(self.art.currentData()))

    def _aend(self) -> None:
        self.geaendert.emit(self.linie())


class RahmenSeiten(Flag):
    KEINE = 0
    OBEN = auto()
    UNTEN = auto()
    LINKS = auto()
    RECHTS = auto()
    INNEN_H = auto()
    INNEN_V = auto()
    AUSSEN = OBEN | UNTEN | LINKS | RECHTS
    ALLE = AUSSEN | INNEN_H | INNEN_V


RAHMEN_EINTRAEGE = (
    ("unten", "Rahmenlinie unten", RahmenSeiten.UNTEN), ("oben", "Rahmenlinie oben", RahmenSeiten.OBEN),
    ("links", "Rahmenlinie links", RahmenSeiten.LINKS), ("rechts", "Rahmenlinie rechts", RahmenSeiten.RECHTS),
    None,
    ("kein", "Kein Rahmen", RahmenSeiten.KEINE), ("alle", "Alle Rahmenlinien", RahmenSeiten.ALLE),
    ("aussen", "Rahmenlinien außen", RahmenSeiten.AUSSEN),
    ("innen_h", "Innere horizontale Rahmenlinie", RahmenSeiten.INNEN_H), ("innen_v", "Innere vertikale Rahmenlinie", RahmenSeiten.INNEN_V),
)


def rahmen_symbol(seiten: RahmenSeiten, groesse: int = 16) -> QIcon:
    """Kleines Quadrat, in dem nur die gemeinten Linien kräftig sind."""
    pm = QPixmap(groesse, groesse); pm.fill(Qt.transparent)
    p = QPainter(pm)
    r = QRectF(1.5, 1.5, groesse - 3, groesse - 3)
    pal = QApplication.palette()                       # Farben der Oberfläche — im dunklen Design sonst kaum zu sehen
    blass = QPen(pal.color(QPalette.Mid), 1, Qt.DotLine)
    stark = QPen(pal.color(QPalette.WindowText), max(2.0, groesse / 8), Qt.SolidLine, Qt.RoundCap)
    mitte_x, mitte_y = r.center().x(), r.center().y()
    for flagge, linie in ((RahmenSeiten.OBEN, (r.left(), r.top(), r.right(), r.top())), (RahmenSeiten.UNTEN, (r.left(), r.bottom(), r.right(), r.bottom())),
                          (RahmenSeiten.LINKS, (r.left(), r.top(), r.left(), r.bottom())), (RahmenSeiten.RECHTS, (r.right(), r.top(), r.right(), r.bottom())),
                          (RahmenSeiten.INNEN_H, (r.left(), mitte_y, r.right(), mitte_y)), (RahmenSeiten.INNEN_V, (mitte_x, r.top(), mitte_x, r.bottom()))):
        p.setPen(stark if flagge in seiten else blass)
        p.drawLine(*[int(v) for v in linie])
    p.end()
    return QIcon(pm)


