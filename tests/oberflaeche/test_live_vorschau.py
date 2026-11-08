"""Live-Vorschau: das Überfahren einer Formatvorlage darf getippten Text nie entfernen (ein Befehl zählt in availableUndoSteps mehrfach)."""
from PySide6.QtCore import QSettings
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest


def test_vorschau_einer_formatvorlage_laesst_den_text_stehen(app, tmp_path):
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document(); w.resize(1300, 800); w.show()
    try:
        ed = w.current_editor(); ed.setFocus()
        QTest.keyClicks(ed, "Hallo Welt wie geht es")
        c = ed.textCursor(); c.select(QTextCursor.Document); ed.setTextCursor(c)
        for name in ("Überschrift 1", "Titel", "Überschrift 2"):
            w.vorschau.zeigen(lambda e, n=name: e.apply_style(n))
            assert ed.toPlainText() == "Hallo Welt wie geht es"
            w.vorschau.ende()
            assert ed.toPlainText() == "Hallo Welt wie geht es", name
        ed.apply_style("Überschrift 1")                       # der Klick selbst
        assert ed.toPlainText() == "Hallo Welt wie geht es"
        assert ed.document().isUndoAvailable()                # der Text lässt sich weiter rückgängig machen
    finally:
        for t in w._doc_tabs():
            t.editor.document().setModified(False)
        w.close()
