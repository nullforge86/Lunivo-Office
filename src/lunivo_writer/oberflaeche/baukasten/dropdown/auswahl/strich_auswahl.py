"""Auswahlfeld, das einen Strich zeigt (Kombinierter Typ, Strichtyp): im Feld die schwarze Strichvorschau, im Popup eine Zeile je Eintrag.

    a = StrichAuswahl([("einfach", zeichner), ("doppelt", zeichner2), …])     # zeichner(painter, QRectF, QColor) malt den Strich
    a.gewaehlt.connect(lambda schluessel: …)
    a.setze("doppelt")                                                          # still: meldet nichts

Das Feld kennt nur Schlüssel und Zeichner; was sie bedeuten, weiß der Aufrufer. Das Popup ist das ``VoreinstellungMenue`` (eine Spalte).
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QIcon, QPainter, QPalette, QPixmap, QPolygonF
from PySide6.QtWidgets import QPushButton, QSizePolicy, QStyle, QStyleOptionButton, QStylePainter

from lunivo_writer.oberflaeche.baukasten.dropdown.voreinstellung_menue import VoreinstellungMenue
from lunivo_writer.oberflaeche.baukasten.basis.mass import DROPDOWN_HOEHE, DROPDOWN_INNEN_FORM, BREITE_REGLER_MIN, GROESSE_STRICHART_KACHEL, HOEHE_KNOPF_GROSS

_KACHEL = QSize(*GROESSE_STRICHART_KACHEL)


class StrichAuswahl(QPushButton):
    gewaehlt = Signal(str)

    def __init__(self, eintraege, parent=None):
        super().__init__(parent)
        self._eintraege = list(eintraege)
        self._aktuell = self._eintraege[0][0] if self._eintraege else ""
        self.setMinimumHeight(DROPDOWN_HOEHE); self.setProperty("dropdownFeld", True); self.setMinimumWidth(BREITE_REGLER_MIN); self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.clicked.connect(self._popup)

    def aktuell(self) -> str:
        return self._aktuell

    def setze(self, schluessel: str) -> None:
        if any(e[0] == schluessel for e in self._eintraege):
            self._aktuell = schluessel
            self.update()

    def _namen(self):
        return [(e[0], e[1], e[2] if len(e) > 2 else e[0]) for e in self._eintraege]

    def _zeichner(self, schluessel: str):
        return next((e[1] for e in self._eintraege if e[0] == schluessel), None)

    def _bild(self, zeichner, groesse: QSize) -> QPixmap:
        pm = QPixmap(groesse); pm.fill(self.palette().color(QPalette.Base))
        p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
        zeichner(p, QRectF(6, 0, groesse.width() - 12, groesse.height()), self.palette().color(QPalette.Text))
        p.end()
        return pm

    def paintEvent(self, _e) -> None:
        sp = QStylePainter(self)
        opt = QStyleOptionButton(); self.initStyleOption(opt); opt.text = ""; opt.icon = QIcon()
        sp.drawPrimitive(QStyle.PE_PanelButtonCommand, opt)
        r = QRectF(self.rect()).adjusted(DROPDOWN_INNEN_FORM, DROPDOWN_INNEN_FORM, -DROPDOWN_INNEN_FORM, -DROPDOWN_INNEN_FORM)
        sp.setRenderHint(QPainter.Antialiasing)
        pal = self.palette()
        sp.fillRect(r, pal.color(QPalette.Base if self.isEnabled() else QPalette.Window))
        z = self._zeichner(self._aktuell)
        if z is not None:
            sp.save(); sp.setClipRect(r)
            z(sp, QRectF(r.left() + 6, r.top(), r.width() - 26, r.height()), pal.color(QPalette.Text if self.isEnabled() else QPalette.Mid))
            sp.restore()
        x, y = r.right() - 10, r.center().y()                                    # Pfeil nach unten am rechten Rand
        sp.setPen(Qt.NoPen); sp.setBrush(pal.color(QPalette.Text if self.isEnabled() else QPalette.Mid))
        sp.drawPolygon(QPolygonF([QPointF(x - 3.5, y - 1.5), QPointF(x + 3.5, y - 1.5), QPointF(x, y + 2.5)]))

    def _popup(self) -> None:
        m = VoreinstellungMenue(self, keine=None, kachel=_KACHEL)
        m.aktuell = self._aktuell
        m._gitter([(k, QIcon(self._bild(z, _KACHEL)), n) for k, z, n in self._namen()], 1)
        m.gewaehlt.connect(self._waehle)
        m.exec(self.mapToGlobal(self.rect().bottomLeft()))

    def _waehle(self, schluessel: str) -> None:
        if schluessel != self._aktuell:
            self.setze(schluessel)
            self.gewaehlt.emit(schluessel)
