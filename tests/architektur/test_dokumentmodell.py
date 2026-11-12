"""Rundlauf Qt-Dokument → Modell (``core.document``) → Qt-Dokument: Text, Formate, Listen, Tabellen, Rahmen, Bilder und Abschnitte bleiben gleich."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import (QBrush, QColor, QImage, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument, QTextFrameFormat, QTextImageFormat,
                           QTextListFormat, QTextTableFormat)

from lunivo_writer.adapter.qt.dokument import document_from_qt, document_to_qt, vergleichen
from lunivo_writer.core.document import Frame, Image, Paragraph, Table
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
    assert vergleichen(q.doc, document_to_qt(m.document)) == []
