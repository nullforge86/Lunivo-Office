from PySide6.QtCore import QSettings

from lunivo_writer.dienste.einstellungen_dienst import Settings
from lunivo_writer.oberflaeche.programmfenster import MainWindow


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


