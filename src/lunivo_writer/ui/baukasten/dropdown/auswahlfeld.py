"""Auswahlfeld: das eine Dropdown für ganz Lunivo.

Drop-in für ``QComboBox`` (gleiche API). Zusätzlich:
- Die Feldbreite folgt dem Layout (``AdjustToMinimumContentsLengthWithIcon``); lange Einträge machen das Feld nicht breiter.
  Eine gesetzte feste Breite bleibt unangetastet.
- Die Aufklappliste ist nie breiter als das Fenster/die Seitenleiste des Felds und bleibt im Bildschirm.
- Zeilen so kompakt wie die Menüzeilen (Schrifthöhe + 2 × ``DROPDOWN_ZEILE_PAD_V``); zu lange Texte werden in der Mitte gekürzt (Anfang und Ende bleiben lesbar).
Keine Farben im Widget-Stylesheet: das Aussehen kommt aus ``ui/theme.py``.
"""
from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import (QComboBox, QFontComboBox, QStyle, QStyledItemDelegate, QStyleOptionComboBox, QStylePainter,
                               QStyleOptionViewItem)

from lunivo_writer.ui.baukasten.mass import (DROPDOWN_BREITE, ABSTAND_GROSS, ABSTAND_KLEIN, ABSTAND_MITTEL, DROPDOWN_HOEHE, DROPDOWN_MAX_ZEILEN, DROPDOWN_MIN_ZEICHEN,
                                                DROPDOWN_ZEILE_PAD_V)
from lunivo_writer.ui.baukasten.dropdown.popup_lage import popup_bereich, popup_klemmen

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
    bs = combo.screen().availableGeometry() if combo.screen() else QRect(0, 0, 10000, 10000)
    bereich = popup_bereich(combo, bs)
    g = pop.geometry()
    breite = min(max(g.width(), popup_min), bereich.width())
    zeilen = min(combo.maxVisibleItems(), combo.count()) if combo.count() else 1
    hoehe = min(g.height(), bs.height(), max(zeilen * (combo.fontMetrics().height() + 2 * DROPDOWN_ZEILE_PAD_V), 1) + ABSTAND_MITTEL)      # nie höher als die sichtbaren Zeilen und nie höher als der Bildschirm
    pop.setMinimumWidth(0); pop.setMaximumWidth(breite)         # der Behälter meldet sonst die Breite des längsten Eintrags als Mindestmaß
    pop.resize(breite, hoehe)
    unten = combo.mapToGlobal(QPoint(0, combo.height()))         # Qt setzt die Liste so, dass der gewählte Eintrag über dem Feld liegt; nach dem Kürzen sitzt sie dann falsch: unter das Feld, ist dort kein Platz, darüber
    oben = combo.mapToGlobal(QPoint(0, 0)).y() - hoehe
    pop.move(pop.x(), unten.y() if unten.y() + hoehe <= bs.bottom() or oben < bs.top() else oben)
    popup_klemmen(pop, combo)


class _Feldlaenge:
    """Gemeinsam für ``Auswahlfeld`` und ``Schriftauswahl``: die Länge des Feldes in Zeichen (Rolle statt fester Zahl am Aufrufer)."""

    def zeichen(self, n: int) -> None:
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.setMinimumContentsLength(n)

    def rolle(self, rolle: str, variante: str, *, mindest: bool = False) -> None:
        """Die Breite des Feldes aus der zentralen Tabelle ``DROPDOWN_BREITE`` (Rolle × Layoutvariante: band, leiste, mini, dialog, feld).
        ``mindest``: nur Mindestbreite (das Feld darf wachsen), sonst feste Breite."""
        b = DROPDOWN_BREITE[(rolle, variante)]
        self.setMinimumWidth(b) if mindest else self.setFixedWidth(b)

    def an_inhalt(self) -> None:
        """Das Feld ist so breit wie sein längster Eintrag (z. B. kurze feste Listen)."""
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)


class Auswahlfeld(_Feldlaenge, QComboBox):
    def __init__(self, parent=None, *, min_zeichen: int = DROPDOWN_MIN_ZEICHEN, popup_min: int = 0):
        super().__init__(parent)
        self._popup_min = popup_min
        self.setMinimumHeight(DROPDOWN_HOEHE)
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.setMinimumContentsLength(min_zeichen)
        self.setMaxVisibleItems(MAX_ZEILEN)
        self.setItemDelegate(_KuerzDelegate(self))
        self._menue_oben = False

    def als_menue_nach_oben(self, an: bool = True, zusatz=None) -> None:
        """Statt der Liste öffnet das Feld eine ``MenueListe`` über sich (Häkchen rechts am gewählten Eintrag); Auswahl setzt wie gewohnt den Index.
        ``zusatz(menue)``: füllt bei jedem Öffnen weitere Zeilen unter einer Trennlinie unter die Liste (z. B. Zeilen mit Untermenü)."""
        self._menue_oben = an
        self._menue_zusatz = zusatz

    def _menue_zeigen(self) -> None:
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = self._menue = MenueListe(self)
        m.setMinimumWidth(self.width())
        for i in range(self.count()):
            m.eintrag(self.itemText(i).replace("&", "&&"), lambda i=i: self.setCurrentIndex(i), kuerzel="✓" if i == self.currentIndex() else "")
        if getattr(self, "_menue_zusatz", None) is not None:
            m.trenner()
            self._menue_zusatz(m)
        m.ensurePolished()
        m.popup(self.mapToGlobal(self.rect().topLeft()) - QPoint(0, m.sizeHint().height()))

    def showPopup(self) -> None:
        if self._menue_oben:
            self._menue_zeigen()
            return
        self.view().window().setMaximumWidth(16777215)
        super().showPopup()
        popup_begrenzen(self, self._popup_min)

    def hidePopup(self) -> None:
        if self._menue_oben and getattr(self, "_menue", None) is not None:
            self._menue.hide()
        super().hidePopup()

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


class Schriftauswahl(_Feldlaenge, QFontComboBox):
    """Schriftart-Auswahl; behält die Schriftvorschau der Einträge, begrenzt nur die Liste."""

    def __init__(self, parent=None, *, min_zeichen: int = DROPDOWN_MIN_ZEICHEN):
        super().__init__(parent)
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.setMinimumContentsLength(min_zeichen)
        self.setMaxVisibleItems(MAX_ZEILEN)
        self.setMinimumHeight(DROPDOWN_HOEHE)

    def showPopup(self) -> None:
        self.view().window().setMaximumWidth(16777215)
        super().showPopup()
        popup_begrenzen(self)
