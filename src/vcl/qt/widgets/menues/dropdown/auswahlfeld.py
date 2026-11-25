from __future__ import annotations
from PySide6.QtCore import QPoint, QSize, Qt
from PySide6.QtWidgets import QComboBox, QStyle, QStyledItemDelegate, QStyleOptionComboBox, QStylePainter, QStyleOptionViewItem
from vcl.qt.widgets.bausteine.abstaende.mass import QWIDGETSIZE_MAX
from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_GROSS, ABSTAND_KLEIN, ABSTAND_MITTEL, DROPDOWN_HOEHE, DROPDOWN_MIN_ZEICHEN, DROPDOWN_ZEILE_PAD_V
from vcl.qt.widgets.menues.dropdown.auswahlfeld_hilfen import MAX_ZEILEN, popup_begrenzen
from vcl.qt.widgets.menues.dropdown.feldlaenge import _Feldlaenge


class _KuerzDelegate(QStyledItemDelegate):
    """Zeilenhöhe wie in den Menüs (Schrifthöhe + 2 × Abstand), Text mittig gekürzt."""

    def sizeHint(self, option, index) -> QSize:
        s = super().sizeHint(option, index)
        return QSize(
            s.width(),
            option.fontMetrics.height() + 2 * DROPDOWN_ZEILE_PAD_V,
        )

    def paint(self, painter, option, index) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        breite = max(
            ABSTAND_GROSS,
            opt.rect.width() - 2 * ABSTAND_MITTEL,
        )
        opt.text = opt.fontMetrics.elidedText(
            opt.text,
            Qt.TextElideMode.ElideMiddle,
            breite,
        )

        stil = opt.widget.style() if opt.widget else None
        if stil is None:
            super().paint(painter, option, index)
            return

        stil.drawControl(
            QStyle.ControlElement.CE_ItemViewItem,
            opt,
            painter,
            opt.widget,
        )


class Auswahlfeld(_Feldlaenge, QComboBox):
    def __init__(
        self,
        parent=None,
        *,
        min_zeichen: int = DROPDOWN_MIN_ZEICHEN,
        popup_min: int = 0,
    ):
        super().__init__(parent)

        self._popup_min = popup_min
        self._menue_oben = False

        self.setMinimumHeight(DROPDOWN_HOEHE)
        self.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.setMinimumContentsLength(min_zeichen)
        self.setMaxVisibleItems(MAX_ZEILEN)
        self.setItemDelegate(_KuerzDelegate(self))

    def als_menue_nach_oben(self, an: bool = True, zusatz=None) -> None:
        """Statt der Liste eine MenueListe über dem Feld anzeigen."""
        self._menue_oben = an
        self._menue_zusatz = zusatz

    def _menue_zeigen(self) -> None:
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe

        m = self._menue = MenueListe(self)
        m.setMinimumWidth(self.width())

        for i in range(self.count()):
            m.eintrag(
                self.itemText(i).replace("&", "&&"),
                lambda i=i: self.setCurrentIndex(i),
                kuerzel="✓" if i == self.currentIndex() else "",
            )

        if getattr(self, "_menue_zusatz", None) is not None:
            m.trenner()
            self._menue_zusatz(m)

        m.ensurePolished()
        m.popup(
            self.mapToGlobal(self.rect().topLeft())
            - QPoint(0, m.sizeHint().height())
        )

    def showPopup(self) -> None:
        if self._menue_oben:
            self._menue_zeigen()
            return

        view = self.view()
        pop = view.window() if view is not None else None
        if pop is not None:
            pop.setMinimumWidth(0)
            pop.setMaximumWidth(QWIDGETSIZE_MAX)
            view.setMinimumWidth(0)
            view.setMaximumWidth(QWIDGETSIZE_MAX)

        super().showPopup()
        popup_begrenzen(self, self._popup_min)

    def hidePopup(self) -> None:
        if (
            self._menue_oben
            and getattr(self, "_menue", None) is not None
        ):
            self._menue.hide()

        super().hidePopup()

    def paintEvent(self, event) -> None:
        if self.isEditable():
            super().paintEvent(event)
            return

        p = QStylePainter(self)
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)

        p.drawComplexControl(
            QStyle.ComplexControl.CC_ComboBox,
            opt,
        )

        feld = self.style().subControlRect(
            QStyle.ComplexControl.CC_ComboBox,
            opt,
            QStyle.SubControl.SC_ComboBoxEditField,
            self,
        )
        icon = (
            opt.iconSize.width() + ABSTAND_KLEIN
            if not opt.currentIcon.isNull()
            else 0
        )

        opt.currentText = opt.fontMetrics.elidedText(
            opt.currentText,
            Qt.TextElideMode.ElideMiddle,
            max(
                ABSTAND_GROSS,
                feld.width() - icon - ABSTAND_KLEIN,
            ),
        )

        p.drawControl(
            QStyle.ControlElement.CE_ComboBoxLabel,
            opt,
        )
