"""Ein Bild, dessen Daten in der DOCX-Datei nicht lesbar sind, wird nicht verworfen: Es bleibt als aufbewahrtes Objekt in der vorgesehenen Größe im Dokument
(Platzhalter in der Anzeige), der Bericht meldet es, und beim Speichern als DOCX wird es unverändert zurückgeschrieben."""
import zipfile

import pytest

from lunivo_writer.core.document.dokument import InlineObjekt
from lunivo_writer.dienste.modell_laden import lade_modell


def test_unlesbares_bild_bleibt_als_objekt_erhalten(tmp_path, app):
    docx = pytest.importorskip("docx")
    from docx.shared import Emu
    from PySide6.QtGui import QColor, QImage
    png = tmp_path / "in.png"
    img = QImage(40, 30, QImage.Format_RGB32)
    img.fill(QColor("red"))
    img.save(str(png))
    d = docx.Document()
    d.add_paragraph("Vorher")
    d.add_picture(str(png), width=Emu(200 * 9525), height=Emu(150 * 9525))
    d.save(str(tmp_path / "a.docx"))
    with zipfile.ZipFile(tmp_path / "a.docx") as zin, zipfile.ZipFile(tmp_path / "b.docx", "w") as zout:
        for n in zin.namelist():
            zout.writestr(n, b"kaputt" if n.startswith("word/media/") else zin.read(n))
    g = lade_modell(str(tmp_path / "b.docx"))
    objekte = [x for a in g.document.absaetze() for x in a.inhalte if isinstance(x, InlineObjekt)]
    assert len(objekte) == 1 and objekte[0].art == "roh" and objekte[0].breite == 200.0 and objekte[0].hoehe == 150.0
    assert g.report.warnings                                           # der Verlust der Darstellung wird gemeldet
    from tests.hilfen_dokument import docx_rundlauf
    _gelesen, schreib, _lese, pfad = docx_rundlauf(g.document, tmp_path, "c.docx")
    assert not schreib.warnings
    with zipfile.ZipFile(pfad) as archiv:
        assert any(archiv.read(n) == b"kaputt" for n in archiv.namelist() if n.startswith("word/media/"))      # die Daten sind unverändert zurückgeschrieben
