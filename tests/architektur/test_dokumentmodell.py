"""Rundlauf Qt-Dokument → Modell (``core.document``) → Qt-Dokument: Text, Formate, Listen, Tabellen, Rahmen, Bilder und Abschnitte bleiben gleich."""
import os
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import (QBrush, QColor, QImage, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument, QTextFrameFormat, QTextImageFormat,
                           QTextListFormat, QTextTableFormat)

from lunivo_writer.adapter.qt.dokument import document_from_qt, document_to_qt, vergleichen
from lunivo_writer.core.document import Frame, Image, Paragraph, Table
from lunivo_writer.core.document import RowHeight
from lunivo_writer.editor.seite import abschnitte as AB
from lunivo_writer.modelle.seite import PageSettings


def _beispiel() -> QTextDocument:
    d = QTextDocument()
    c = QTextCursor(d)
    fett = QTextCharFormat(); fett.setFontWeight(75); fett.setForeground(QBrush(QColor("red"))); fett.setAnchor(True); fett.setAnchorHref("#x")
    c.insertText("Anfang "); c.insertText("fett", fett)
    bf = QTextBlockFormat(); bf.setAlignment(Qt.AlignRight); bf.setTopMargin(7.5); c.insertBlock(bf)
    lf = QTextListFormat(); lf.setStyle(QTextListFormat.ListDecimal)
    c.insertText("eins"); c.createList(lf); c.insertBlock(); c.insertText("zwei")
    c.insertBlock(QTextBlockFormat()); c.insertText("Liste vorbei")
    img = QImage(8, 4, QImage.Format_ARGB32); img.fill(QColor("blue"))
    d.addResource(QTextDocument.ImageResource, QUrl("bild1"), img)
    fi = QTextImageFormat(); fi.setName("bild1"); fi.setWidth(16); fi.setHeight(8)
    c.insertBlock(); c.insertImage(fi); c.insertText(" nach dem Bild")
    c.insertBlock()
    tf = QTextTableFormat(); tf.setBorder(1); tf.setCellPadding(3)
    t = c.insertTable(3, 3, tf)
    t.mergeCells(0, 0, 1, 2)
    t.cellAt(0, 0).firstCursorPosition().insertText("verbunden")
    t.cellAt(2, 2).firstCursorPosition().insertText("unten")
    c.setPosition(t.lastPosition() + 1)
    ff = QTextFrameFormat(); ff.setPosition(QTextFrameFormat.FloatRight); ff.setWidth(80)
    fr = c.insertFrame(ff); fr.firstCursorPosition().insertText("im Rahmen")
    c.setPosition(fr.lastPosition() + 1)
    c.insertText("Schluss")
    AB.einfuegen(d, c, "naechste", PageSettings())
    c.insertText(" zweiter Abschnitt")
    return d


def test_rundlauf_qt_modell_qt_ohne_verlust():
    d = _beispiel()
    m = document_from_qt(d, PageSettings())
    assert len(m.sections) == 2 and m.sections[1].kind == "naechste"
    inhalt = [b for s in m.sections for b in s.content]
    assert any(isinstance(b, Table) for b in inhalt) and any(isinstance(b, Frame) for b in inhalt)
    assert any(isinstance(r, Image) and r.raster_png for b in inhalt if isinstance(b, Paragraph) for r in b.runs)
    assert m.lists and any(isinstance(b, Paragraph) and b.format.list_id for b in inhalt)
    assert vergleichen(d, document_to_qt(m)) == []


def test_docx_als_modell_laden(app):
    from lunivo_writer.dienste.datei_dienst import load
    from lunivo_writer.dienste.modell_laden import lade_modell
    pfad = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dokument", "formate", "daten", "lo_dokument.docx")
    m = lade_modell(pfad)
    q = load(pfad)
    assert m.page.width_mm == q.page.width_mm and m.document.sections[0].page is m.page
    assert "".join(p.text for s in m.document.sections for p in s.content if isinstance(p, Paragraph)).strip()
    assert any(n.kind == "f" and n.text == "Die Fußnote von LibreOffice." for n in m.document.notes)
    ausrichtungen = {1: "left", 2: "right", 4: "center", 8: "justify"}
    for s in m.document.sections:
        for p in (b for b in s.content if isinstance(b, Paragraph)):
            if "BlockAlignment" in p.format.properties:
                horizontal = int(p.format.properties["BlockAlignment"]) & 0xF
                assert p.format.alignment == ausrichtungen.get(horizontal)
    assert vergleichen(q.doc, document_to_qt(m.document)) == []


def test_normaler_docx_ladepfad_uebergibt_importiertes_modell_an_documenttab(app):
    from lunivo_writer.dienste.datei_dienst import load
    from lunivo_writer.oberflaeche.dokument.dokumentfenster.dokument_bereich import DocumentTab
    pfad = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dokument", "formate", "daten", "lo_dokument.docx")
    geladen = load(pfad)
    assert geladen.modell is not None
    tab = DocumentTab(geladen, pfad)
    tab.set_layout("kern")
    assert tab.widget().sitzung().dok is geladen.modell


def test_docx_zeilenmindesthoehe_als_modell_und_qt_property(app, tmp_path):
    from docx import Document as WordDocument
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from lunivo_writer.dienste.datei_dienst import load
    from lunivo_writer.editor.tabelle.tabelleneigenschaften import Z_MINHOEHE

    docx = WordDocument()
    t = docx.add_table(rows=2, cols=2)
    for ri, art in enumerate(("atLeast", "exact")):
        row = t.rows[ri]
        row.cells[0].text = f"Links {art}"
        row.cells[1].text = f"Rechts {art}"
        trpr = row._tr.get_or_add_trPr()
        height = OxmlElement("w:trHeight")
        height.set(qn("w:val"), str(720 + ri * 240))
        height.set(qn("w:hRule"), art)
        trpr.append(height)
    pfad = tmp_path / "zeilenhoehe.docx"
    docx.save(pfad)

    geladen = load(str(pfad))
    tab = next(b for s in geladen.modell.sections for b in s.content if isinstance(b, Table))
    assert tab.table_rows[0].row_height == RowHeight("minimum", 48.0)
    assert tab.table_rows[1].row_height.kind == "exact"
    assert tab.table_rows[1].row_height.value_px == pytest.approx(64.0)
    qt = document_to_qt(geladen.modell)
    tabelle = next(f for f in qt.rootFrame().childFrames() if hasattr(f, "cellAt"))
    assert tabelle.cellAt(0, 0).format().property(Z_MINHOEHE) == pytest.approx(48.0)
    from lunivo_writer.dienste.docx_schreiber import write_docx
    ausgabe = tmp_path / "zeilenhoehe_rundlauf.docx"
    write_docx(str(ausgabe), qt, geladen.page, geladen.meta)
    zurueck = WordDocument(str(ausgabe))
    rules = [r._tr.xpath("w:trPr/w:trHeight/@w:hRule")[0] for r in zurueck.tables[0].rows]
    assert rules == ["atLeast", "exact"]
