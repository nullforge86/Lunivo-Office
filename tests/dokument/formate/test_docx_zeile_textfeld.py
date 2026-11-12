"""Aus einer Formular-DOCX (PDF-Umwandlung): „mindestens“-Zeilenabstand, Textfeld-Innenabstand, Gruppe in der Zeile."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import io
import zipfile

from PySide6.QtGui import QTextBlockFormat, QTextCursor, QTextDocument

from lunivo_writer.dienste import docx_leser, docx_schreiber
from lunivo_writer.modelle.seite import PageSettings


def test_zeilenabstand_mindestens_hin_und_zurueck(app, tmp_path):
    from lunivo_writer.adapter.qt.dokument import document_from_qt, document_to_qt
    from lunivo_writer.core.document import LineSpacing
    d = QTextDocument()
    c = QTextCursor(d)
    bf = QTextBlockFormat()
    bf.setLineHeight(20.0, QTextBlockFormat.LineHeightTypes.MinimumHeight.value)
    c.setBlockFormat(bf)
    c.insertText("Zeile")
    modell = document_from_qt(d, PageSettings())
    assert modell.sections[0].content[0].format.line_spacing == LineSpacing("minimum", 20.0)
    d = document_to_qt(modell)
    daten = docx_schreiber.docx_daten(d, PageSettings(), {})[0]
    assert 'w:lineRule="atLeast"' in zipfile.ZipFile(io.BytesIO(daten)).read("word/document.xml").decode()
    p = tmp_path / "m.docx"
    p.write_bytes(daten)
    gelesen = docx_leser.read_docx(str(p))[0]
    assert int(gelesen.firstBlock().blockFormat().lineHeightType()) == QTextBlockFormat.LineHeightTypes.MinimumHeight.value


def test_textfeld_innenabstand_null_setzt_text_an_den_rand(app):
    from lunivo_writer.editor.objekte import frei_objekt_text as T
    d = {"text": "XXXX", "schrift": "Liberation Sans", "pt": 11, "farbe": "#000000"}
    mit = T.textfeld_zeichnen(d, 120, 30)                                  # Standard: 8 px Innenabstand
    ohne = T.textfeld_zeichnen({**d, "innen": [0, 0, 0, 0]}, 120, 30)

    def erste_spalte(img):
        for x in range(img.width()):
            if any(img.pixelColor(x, y).alpha() > 0 for y in range(img.height())):
                return x / T._SS
    assert erste_spalte(ohne) < 3 <= 8 - 1 < erste_spalte(mit) + 1
