"""Das Fenster „Textbausteine“ in der Seitenleiste (Kay, 2026-10-28): ein Titel, Felder untereinander, Liste und Vorschau in voller Breite."""
from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QTextEdit, QWidget

from lunivo_writer.ui.baukasten.zusatz_panel import ZusatzPanel
from lunivo_writer.ui.dialogs.einfuegen_dialoge import BausteinDialog


def _offen(app, breite, ed=None):
    p = ZusatzPanel(); p.verfuegbar, p.verfuegbar_hoehe = breite, 587; p.resize(breite + 36, 727)
    d = BausteinDialog(None, ed or QTextEdit())
    p.oeffne(d); p.show(); app.processEvents(); app.processEvents()
    return p, d


@pytest.mark.parametrize("breite", [300, 360, 444])
def test_baustein_passt_und_ist_aufgeraeumt(app, breite):
    p, d = _offen(app, breite)
    vp = p.stapel.currentWidget().sa.viewport()
    zu = [type(c).__name__ for c in d.findChildren(QWidget) if c.isVisible() and c.width() > 0
          and (c.mapTo(vp, c.rect().topLeft()).x() < -1 or c.mapTo(vp, c.rect().topRight()).x() > vp.width())]
    assert not zu, zu
    assert not d.liste.horizontalScrollBar().isVisible()
    assert d.liste.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOff
    assert d.liste.width() >= vp.width() - 40                                          # volle Breite
    assert d.name.y() <= d.kuerzel.y()                                                 # Gitter: untereinander, bei Platz nebeneinander
    assert not [b for b in d.findChildren(QPushButton) if b.text() == "Schließen"]
    assert not [l for l in d.findChildren(QLabel) if l.text() == "Textbausteine"]      # Titel nur im Panelkopf
    p.close()


def test_baustein_einfuegen_wirkt(app):
    ed = QTextEdit()
    p, d = _offen(app, 360, ed)
    d.einfuegen_knopf.click()
    assert ed.toPlainText().strip() != ""
    p.close()
