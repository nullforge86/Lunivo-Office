"""Auswahlfeld: das eine Dropdown für ganz Lunivo.

Drop-in für ``QComboBox`` (gleiche API). Zusätzlich:
- Die Feldbreite folgt dem Layout (``AdjustToMinimumContentsLengthWithIcon``); lange Einträge machen das Feld nicht breiter.
  Eine gesetzte feste Breite bleibt unangetastet.
- Die Aufklappliste ist nie breiter als das Fenster/die Seitenleiste des Felds und bleibt im Bildschirm.
- Zeilen so kompakt wie die Menüzeilen (Schrifthöhe + 2 × ``DROPDOWN_ZEILE_PAD_V``); zu lange Texte werden in der Mitte gekürzt (Anfang und Ende bleiben lesbar).
Keine Farben im Widget-Stylesheet: das Aussehen kommt aus ``ui/theme.py``.
"""
from __future__ import annotations

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtWidgets import (QComboBox, QFontComboBox, QStyle, QStyledItemDelegate, QStyleOptionComboBox, QStylePainter,
                               QStyleOptionViewItem)

from lunivo_writer.ui.baukasten.mass import (ABSTAND_GROSS, ABSTAND_KLEIN, ABSTAND_MITTEL, DROPDOWN_MAX_ZEILEN, DROPDOWN_MIN_ZEICHEN,
                                                DROPDOWN_ZEILE_PAD_V)
from lunivo_writer.ui.baukasten.popup_lage import popup_klemmen

MAX_ZEILEN = DROPDOWN_MAX_ZEILEN


class _KuerzDelegate(QStyledItemDelegate):
    """Zeilenhöhe wie in den Menüs (Schrifthöhe + 2 × Abstand aus mass.py), Text mittig gekürzt."""

    def sizeHint(self, option, index) -> QSize:
        s = super().sizeHint(option, index)
        return QSize(s.width(), option.fontMetrics.height() + 2 * DROPDOWN_ZEILE_PAD_V)

    def paint(self, painter, option, index) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        breite = max(ABSTAND_GROSS, opt.rect.width() - 2 * ABSTAND_MITTEL)
        opt.text = opt.fontMetrics.elidedText(opt.text, Qt.TextElideMode.ElideMiddle, breite)
        stil = opt.widget.style() if opt.widget else None
        if stil is None:
            super().paint(painter, option, index)
            return
        stil.drawControl(QStyle.ControlElement.CE_ItemViewItem, opt, painter, opt.widget)


def popup_begrenzen(combo: QComboBox, popup_min: int = 0) -> None:
    """Nach ``showPopup()`` aufrufen: Größe der Liste (Breite, sichtbare Zeilen); die Lage in Fenster und Bildschirm bestimmt ``popup_klemmen``."""
    view = combo.view()
    pop = view.window() if view is not None else None
    if pop is None or pop is combo.window() or not pop.isVisible():
        return
    fenster = combo.window()
    bs = combo.screen().availableGeometry() if combo.screen() else QRect(0, 0, 10000, 10000)
    g = pop.geometry()
    breite = min(max(g.width(), popup_min), fenster.width(), bs.width())
    zeilen = min(combo.maxVisibleItems(), combo.count()) if combo.count() else 1
    hoehe = min(g.height(), bs.height(), max(zeilen * (combo.fontMetrics().height() + 2 * DROPDOWN_ZEILE_PAD_V), 1) + ABSTAND_MITTEL)      # nie höher als die sichtbaren Zeilen und nie höher als der Bildschirm
    pop.setMinimumWidth(0); pop.setMaximumWidth(breite)         # der Behälter meldet sonst die Breite des längsten Eintrags als Mindestmaß
    pop.resize(breite, hoehe)
    popup_klemmen(pop, fenster)


class Auswahlfeld(QComboBox):
    def __init__(self, parent=None, *, min_zeichen: int = DROPDOWN_MIN_ZEICHEN, popup_min: int = 0):
        super().__init__(parent)
        self._popup_min = popup_min
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.setMinimumContentsLength(min_zeichen)
        self.setMaxVisibleItems(MAX_ZEILEN)
        self.setItemDelegate(_KuerzDelegate(self))

    def showPopup(self) -> None:
        self.view().window().setMaximumWidth(16777215)
        super().showPopup()
        popup_begrenzen(self, self._popup_min)

    def paintEvent(self, event) -> None:
        if self.isEditable():
            super().paintEvent(event)
            return
        p = QStylePainter(self)
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        p.drawComplexControl(QStyle.ComplexControl.CC_ComboBox, opt)
        feld = self.style().subControlRect(QStyle.ComplexControl.CC_ComboBox, opt,
                                           QStyle.SubControl.SC_ComboBoxEditField, self)
        icon = opt.iconSize.width() + ABSTAND_KLEIN if not opt.currentIcon.isNull() else 0
        opt.currentText = opt.fontMetrics.elidedText(opt.currentText, Qt.TextElideMode.ElideMiddle,
                                                     max(ABSTAND_GROSS, feld.width() - icon - ABSTAND_KLEIN))
        p.drawControl(QStyle.ControlElement.CE_ComboBoxLabel, opt)


class Schriftauswahl(QFontComboBox):
    """Schriftart-Auswahl; behält die Schriftvorschau der Einträge, begrenzt nur die Liste."""

    def __init__(self, parent=None, *, min_zeichen: int = DROPDOWN_MIN_ZEICHEN):
        super().__init__(parent)
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.setMinimumContentsLength(min_zeichen)
        self.setMaxVisibleItems(MAX_ZEILEN)

    def showPopup(self) -> None:
        self.view().window().setMaximumWidth(16777215)
        super().showPopup()
        popup_begrenzen(self)
