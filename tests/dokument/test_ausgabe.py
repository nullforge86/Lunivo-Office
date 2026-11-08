from PySide6.QtCore import QSettings

from lunivo_writer.services.settings_service import Settings
from lunivo_writer.ui.main_window import MainWindow


def _fenster(tmp_path):
    return MainWindow(Settings(QSettings(str(tmp_path / 's.ini'), QSettings.IniFormat)))


def test_standard_ausgabeziel_ppi(app, tmp_path):
    w = _fenster(tmp_path)
    for t in ("96 ppi (Bildschirm)", "220 ppi (Druck)", "330 ppi (hohe Qualität)"):
        w.settings.set("ausgabe/ppi", t)
        assert w.ausgabe_ppi() == int(t.split()[0])
    w.settings.set("ausgabe/ppi", "Unsinn")
    assert w.ausgabe_ppi() == 150
    for t in list(w._doc_tabs()):
        t.editor.document().setModified(False)


def test_png_export_nutzt_ppi(app, tmp_path, monkeypatch):
    from PySide6.QtGui import QImage
    from lunivo_writer.ui.dialogs import optionen
    w = _fenster(tmp_path)
    w.new_document()
    t = w.current_tab(); t.editor.setPlainText("Hallo")
    w.settings.set("ausgabe/ppi", "220 ppi (Druck)")
    t.title = "x"
    ansicht = w.bild_export_widget()                                  # die Bildexport-Seite im Datei-Menü (Qualität kommt aus den Optionen: 220 ppi)
    ansicht.ordner.setText(str(tmp_path))
    assert ansicht.qualitaet.currentData() == 220
    ansicht._exportieren()
    img = QImage(str(tmp_path / "x.png"))
    breite = round(210 / 25.4 * 220)
    assert abs(img.width() - breite) <= 2
    t.editor.document().setModified(False)
