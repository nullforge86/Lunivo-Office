"""Auswahlfeld hilfen: aus ``vcl.qt.widgets.menues.dropdown.auswahlfeld`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QComboBox
from vcl.qt.widgets.bausteine.abstaende.mass import DROPDOWN_MAX_ZEILEN
from vcl.qt.widgets.menues.dropdown.popup_lage import popup_bereich, popup_klemmen


MAX_ZEILEN = DROPDOWN_MAX_ZEILEN


def popup_begrenzen(combo: QComboBox, popup_min: int = 0) -> None:
    """Verbreitert das Popup-Fenster und hält es danach nach den gemeinsamen Öffnungsregeln (``popup_klemmen``) ganz im Bildschirm."""
    view = combo.view()
    pop = view.window() if view is not None else None

    if pop is None or pop is combo.window() or not pop.isVisible():
        return

    bs = (
        combo.screen().availableGeometry()
        if combo.screen()
        else QRect(0, 0, 10000, 10000)
    )
    bereich = popup_bereich(combo, bs)

    breite_inhalt = max(
        (
            view.fontMetrics().horizontalAdvance(combo.itemText(i))
            for i in range(combo.count())
        ),
        default=0,
    ) + 48

    gewuenschte_breite = max(
        pop.width(),
        combo.width(),
        popup_min,
        breite_inhalt,
    )
    breite = min(gewuenschte_breite, bereich.width())

    # Mindestbreite der Ansicht und des Fensters setzen, damit Qt die Liste
    # tatsächlich verbreitert. Keine Höhen- oder Positionsänderung.
    view.setMinimumWidth(breite)
    pop.setMinimumWidth(breite)
    pop.resize(breite, pop.height())
    popup_klemmen(pop, combo)                                                        # Qt legt lange Listen sonst über den Bildschirmrand
