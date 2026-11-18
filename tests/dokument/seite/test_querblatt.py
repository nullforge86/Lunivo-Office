"""Querformat-Blatt zwischen Hochformat-Blättern (Einfügen ▸ Leere Seite ▸ Horizontal): der Editor zeigt jedes Blatt in seiner
eigenen Größe untereinander, gespeichert wird ohne den Zusatz der Anzeige (``editor/seite/querblatt.py``)."""
from __future__ import annotations

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication

from lunivo_writer.editor.seite import querblatt
from lunivo_writer.modelle.seite import mm_to_px
from lunivo_writer.dienste import docx_leser


@pytest.fixture
def fenster(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.dienste.einstellungen_dienst import Settings
    from lunivo_writer.oberflaeche.programmfenster import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document()
    yield w
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def _warte(ms=400):
    from PySide6.QtCore import QElapsedTimer
    t = QElapsedTimer(); t.start()
    while t.elapsed() < ms:
        QApplication.processEvents()


def _hoch_quer_hoch(w, quertext="Querblatt. " * 40):
    e = w.current_editor()
    e.selectAll(); e.textCursor().removeSelectedText()
    e.insertPlainText("Hochformat oben. " * 10)
    w.befehle.leereSeite(None, True); _warte(200)
    e.insertPlainText(quertext); _warte(300)
    w.befehle.leereSeite(None, False); _warte(200)
    e.insertPlainText("Wieder hoch. " * 5)
    e._recount(); _warte(600)
    return e






