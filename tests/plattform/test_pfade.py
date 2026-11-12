import os

from lunivo_writer.plattform import pfade
from lunivo_writer.dienste import einstellungen_dienst


def test_datenordner_wird_angelegt_und_bleibt_ueber_settings_service_erreichbar(app):
    d = pfade.data_dir()
    assert os.path.isdir(d)
    assert einstellungen_dienst.data_dir() == d


def test_zusatzorte_liegen_unter_dem_generischen_datenordner(app):
    assert pfade.schriften_dir().endswith(os.path.join("fonts", "lunivo-office"))
    orte = pfade.piper_dirs()
    assert orte[0].endswith(os.path.join("lunivo-office", "piper"))
    assert orte[1].endswith(os.path.join("schreibhilfe", "piper"))


def test_vorlagenordner_vorgabe_und_eigene_wahl(app):
    from lunivo_writer.editor.dokument import vorlagen

    class S:
        def __init__(self, wert):
            self.wert = wert

        def get(self, key, default=None):
            return self.wert

    assert vorlagen.vorlagenordner(S("")) == pfade.vorlagen_dir()
    assert vorlagen.vorlagenordner(S("/x/y")) == "/x/y"
