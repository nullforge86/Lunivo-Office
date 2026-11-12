"""Ein Bild, dessen Daten in der DOCX-Datei fehlen oder nicht lesbar sind, wird nicht verworfen: an seiner Stelle steht ein Platzhalter in der vorgesehenen Größe."""
import zipfile

import pytest

from lunivo_writer.dienste import datei_dienst


def test_unlesbares_bild_wird_platzhalter(tmp_path, app):
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
    g = datei_dienst.load(str(tmp_path / "b.docx"))
    from lunivo_writer.adapter.qt.dokument import document_from_qt
    from lunivo_writer.core.document.model import Image
    m = document_from_qt(g.doc, g.page)
    bilder = [r for s in m.sections for b in s.content for r in getattr(b, "runs", []) if isinstance(r, Image)]
    assert len(bilder) == 1 and bilder[0].format.properties.get("ImageWidth") == 200.0 and bilder[0].format.properties.get("ImageHeight") == 150.0
    assert any("Platzhalter" in w for w in g.report.warnings)
