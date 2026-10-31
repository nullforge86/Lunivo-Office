"""Das Fenster „Eingeschlossene Zeichen“ als Baustein: Vorlage (Ohne, Text reduzieren, Symbol erweitern), Text und Form (Kreis, Quadrat, Dreieck, Raute).

    d = UmschlosseneZeichenDialog(parent, "Hal", "kreis", "reduzieren")
    if d.exec(): d.werte()                              # {"text": str, "form": str, "vorlage": str}

Das Fenster ändert keinen Text; der Aufrufer setzt ``P_UMSCHLOSSEN`` (``Befehle.umschlosseneZeichen``). Gezeichnet wird in ``editor/textfx.py``.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPixmap, QPolygonF
from PySide6.QtWidgets import QButtonGroup, QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QToolButton, QVBoxLayout, QWidget

from lunivo_writer.editor.zeichenzusatz import FORMEN, VORLAGEN
from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
from lunivo_writer.ui.baukasten.formular_gitter import abschnittstitel
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig

VORSCHLAEGE = ("√", "A", "a", "!", "?", "1", "2", "3", "★", "●", "✓", "※")


def form_bild(form: str, px: int = 18, gross: bool = False, text: str = "") -> QPixmap:
    """Die Form als kleines Bild (für die Liste) oder, mit ``text``, als Beispiel für die Vorlage."""
    pm = QPixmap(px, px); pm.fill(Qt.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor("#343a40"), 1.3)); r = QRectF(px * 0.12, px * 0.12, px * 0.76, px * 0.76)
    if text:
        f = QFont(); f.setPixelSize(int(px * (0.42 if gross else 0.5))); p.setFont(f)
    if form == "kreis":
        p.drawEllipse(r)
    elif form == "quadrat":
        p.drawRect(r)
    elif form == "dreieck":
        p.drawPolygon(QPolygonF([QPointF(r.center().x(), r.top()), QPointF(r.right(), r.bottom()), QPointF(r.left(), r.bottom())]))
    elif form == "raute":
        p.drawPolygon(QPolygonF([QPointF(r.center().x(), r.top()), QPointF(r.right(), r.center().y()), QPointF(r.center().x(), r.bottom()),
                                 QPointF(r.left(), r.center().y())]))
    if text:
        p.drawText(pm.rect(), Qt.AlignCenter, text)
    p.end()
    return pm


def _vorlagenbild(vorlage: str) -> QIcon:
    pm = QPixmap(56, 40); pm.fill(Qt.white)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing); p.setPen(QColor("#212529"))
    f = QFont("Liberation Serif"); f.setPixelSize(22 if vorlage == "ohne" else 15); p.setFont(f)
    if vorlage == "ohne":
        p.drawText(pm.rect(), Qt.AlignCenter, "I")
    else:
        p.drawEllipse(QRectF(16, 6, 24, 24) if vorlage == "reduzieren" else QRectF(13, 3, 30, 30))
        p.drawText(pm.rect().adjusted(0, -1, 0, -4), Qt.AlignCenter, "1")
    p.end()
    return QIcon(pm)


class UmschlosseneZeichenDialog(PanelFaehig, QDialog):
    def __init__(self, parent=None, text: str = "", form: str = "kreis", vorlage: str = "reduzieren"):
        super().__init__(parent)
        self.setWindowTitle("Eingeschlossene Zeichen")
        v = QVBoxLayout(self)
        v.addWidget(abschnittstitel("Formatvorlage"))
        zeile = QHBoxLayout(); zeile.setSpacing(8)
        self._vorlage = QButtonGroup(self)
        for i, (k, t) in enumerate(VORLAGEN):
            b = QToolButton(); b.setCheckable(True); b.setChecked(k == vorlage); b.setText(t); b.setIcon(_vorlagenbild(k)); b.setIconSize(QSize(56, 40))
            b.setToolButtonStyle(Qt.ToolButtonTextUnderIcon); b.setAutoRaise(False); b.setMinimumWidth(96)
            self._vorlage.addButton(b, i); zeile.addWidget(b)
        zeile.addStretch(1)
        v.addLayout(zeile)
        v.addWidget(abschnittstitel("Umschließen"))
        spalten = QHBoxLayout(); spalten.setSpacing(10)
        links = QVBoxLayout(); links.addWidget(QLabel("Text:"))
        self.text = QLineEdit(text); links.addWidget(self.text)
        self.vorschlaege = QListWidget(); self.vorschlaege.setMaximumHeight(120)
        self.vorschlaege.addItems(VORSCHLAEGE)
        self.vorschlaege.itemClicked.connect(lambda i: self.text.setText(i.text()))
        links.addWidget(self.vorschlaege)
        rechts = QVBoxLayout(); rechts.addWidget(QLabel("Umschließen mit:"))
        self.formen = QListWidget(); self.formen.setIconSize(QSize(20, 20)); self.formen.setMaximumHeight(150)
        for k, t in FORMEN:
            it = QListWidgetItem(QIcon(form_bild(k, 20)), ""); it.setData(Qt.UserRole, k); it.setToolTip(t); self.formen.addItem(it)
            if k == form:
                self.formen.setCurrentItem(it)
        rechts.addWidget(self.formen)
        spalten.addLayout(links, 1); spalten.addLayout(rechts, 1)
        v.addLayout(spalten); v.addStretch(1)
        fussleiste(self, v)

    def werte(self) -> dict:
        it = self.formen.currentItem()
        return {"text": self.text.text(), "form": it.data(Qt.UserRole) if it else "kreis", "vorlage": VORLAGEN[max(0, self._vorlage.checkedId())][0]}
