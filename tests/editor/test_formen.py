import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor

from lunivo_writer.editor.dokument import einfuegen as E
from lunivo_writer.editor.objekte import formen
from lunivo_writer.modelle.seite import PageSettings
from lunivo_writer.dienste import datei_dienst as formats
from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor


def _form(ed, name="Rechteck", **d):
    daten = {"form": name}; daten.update(d)
    E.qimage_einfuegen(ed, E.form_bild(name), "Form", "form", daten)


def _vor_bild(ed, nr=0):
    c = QTextCursor(ed.document()); c.setPosition(nr); ed.setTextCursor(c)


def test_fuellung_kontur_vorlage(app):
    ed = DocumentEditor()
    _form(ed)
    _vor_bild(ed)
    assert formen.aendern(ed, fuell="#ff0000")
    assert formen.aendern(ed, linie="#00ff00", strich=5.0)
    o = formen.objekt(ed.bild_format())
    assert o["daten"]["fuell"] == "#ff0000" and o["daten"]["linie"] == "#00ff00" and o["daten"]["strich"] == 5.0
    assert formen.vorlage(ed, "Nur Kontur")
    assert formen.objekt(ed.bild_format())["daten"]["fuell"] == ""
    img = ed.document().resource(2, __import__("PySide6.QtCore", fromlist=["QUrl"]).QUrl(ed.bild_format().name()))
    assert img.pixelColor(img.width() // 2, img.height() // 2).alpha() == 0     # ohne Füllung transparent


def test_gruppieren_aufheben_docx(app, tmp_path):
    ed = DocumentEditor()
    _form(ed, "Rechteck"); _form(ed, "Ellipse", fuell="#ff0000")
    c = QTextCursor(ed.document()); c.select(QTextCursor.Document); ed.setTextCursor(c)
    assert formen.gruppieren(ed) == ""
    _vor_bild(ed)
    o = formen.objekt(ed.bild_format())
    assert o["art"] == "gruppe" and len(o["daten"]["kinder"]) == 2
    pfad = str(tmp_path / "g.docx")
    formats.save(pfad, ed.document(), PageSettings())
    neu = DocumentEditor(); neu.setDocument(formats.load(pfad).doc)
    _vor_bild(neu)
    assert formen.objekt(neu.bild_format())["art"] == "gruppe"
    assert formen.gruppe_aufheben(neu) == ""
    _vor_bild(neu)
    assert formen.objekt(neu.bild_format())["daten"]["form"] == "Rechteck"
    assert neu.document().toPlainText().count("￼") == 2

    # Eine Word-Gruppe mit einer gedrehten, asymmetrischen Kindform durch den normalen Import-/Modellrenderpfad.
    from zipfile import ZIP_DEFLATED, ZipFile
    from lxml import etree
    from lunivo_writer.adapter.qt.seitenbild import seiten_aus_modell
    from lunivo_writer.dienste.datei_dienst import load
    from lunivo_writer.core.document.objekte import P_BILDANKER
    from lunivo_writer.core.document.model import Paragraph
    word = tmp_path / "word_gruppe.docx"
    source = tmp_path / "word_gruppe_basis.docx"
    from docx import Document as WordDocument
    basis = WordDocument(); basis.add_paragraph(); basis.save(source)
    namespaces = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
        "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
        "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
        "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    }
    q = lambda ns, tag: f"{{{namespaces[ns]}}}{tag}"
    drawing = etree.Element(q("w", "drawing"), nsmap=namespaces)
    anchor = etree.SubElement(drawing, q("wp", "anchor"), {"distT": "0", "distB": "0", "distL": "0", "distR": "0", "simplePos": "0",
                                                               "relativeHeight": "1", "behindDoc": "0", "locked": "0", "layoutInCell": "1", "allowOverlap": "1"})
    etree.SubElement(anchor, q("wp", "simplePos"), {"x": "0", "y": "0"})
    ph = etree.SubElement(anchor, q("wp", "positionH"), {"relativeFrom": "page"}); etree.SubElement(ph, q("wp", "posOffset")).text = "1000000"
    pv = etree.SubElement(anchor, q("wp", "positionV"), {"relativeFrom": "page"}); etree.SubElement(pv, q("wp", "posOffset")).text = "1000000"
    etree.SubElement(anchor, q("wp", "extent"), {"cx": "762000", "cy": "381000"})
    etree.SubElement(anchor, q("wp", "effectExtent"), {"l": "0", "t": "0", "r": "0", "b": "0"})
    etree.SubElement(anchor, q("wp", "wrapNone"))
    etree.SubElement(anchor, q("wp", "docPr"), {"id": "1", "name": "Rotierte Gruppe"})
    etree.SubElement(anchor, q("wp", "cNvGraphicFramePr"))
    graphic = etree.SubElement(anchor, q("a", "graphic")); data = etree.SubElement(graphic, q("a", "graphicData"), {"uri": namespaces["wpg"]})
    group = etree.SubElement(data, q("wpg", "wgp")); etree.SubElement(group, q("wpg", "cNvGrpSpPr"))
    gp = etree.SubElement(group, q("wpg", "grpSpPr")); gx = etree.SubElement(gp, q("a", "xfrm"))
    etree.SubElement(gx, q("a", "off"), {"x": "0", "y": "0"}); etree.SubElement(gx, q("a", "ext"), {"cx": "762000", "cy": "381000"})
    etree.SubElement(gx, q("a", "chOff"), {"x": "0", "y": "0"}); etree.SubElement(gx, q("a", "chExt"), {"cx": "762000", "cy": "381000"})
    shape = etree.SubElement(group, q("wps", "wsp")); etree.SubElement(shape, q("wps", "cNvSpPr"))
    props = etree.SubElement(shape, q("wps", "spPr")); sx = etree.SubElement(props, q("a", "xfrm"), {"rot": "2700000", "flipH": "1", "flipV": "1"})
    etree.SubElement(sx, q("a", "off"), {"x": "0", "y": "0"}); etree.SubElement(sx, q("a", "ext"), {"cx": "762000", "cy": "381000"})
    geom = etree.SubElement(props, q("a", "prstGeom"), {"prst": "triangle"}); etree.SubElement(geom, q("a", "avLst"))
    fill = etree.SubElement(props, q("a", "solidFill")); etree.SubElement(fill, q("a", "srgbClr"), {"val": "FF0000"})
    with ZipFile(source) as zin:
        xml = etree.fromstring(zin.read("word/document.xml"))
        body = xml.find(".//" + q("w", "body"))
        paragraph = body.find(q("w", "p"))
        run = etree.SubElement(paragraph, q("w", "r")); run.append(drawing)
        document_xml = etree.tostring(xml, xml_declaration=True, encoding="UTF-8", standalone=True)
        with ZipFile(word, "w", ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                zout.writestr(item, document_xml if item.filename == "word/document.xml" else zin.read(item.filename))
    geladen = formats.load(str(word))
    assert geladen.modell is not None
    angabe = next(json.loads(block.format.properties[P_BILDANKER])[0]
                  for section in geladen.modell.sections for block in section.content
                  if isinstance(block, Paragraph) and P_BILDANKER in block.format.properties)
    from copy import deepcopy
    from lunivo_writer.core.document.objekte import ImageObject
    obj = ImageObject.aus_angabe(angabe)
    assert angabe["dreh"] == 45.0 and angabe["flipH"] and angabe["flipV"]
    assert obj.transform.flip_h and obj.transform.flip_v and obj.zu_angabe()["flipH"] and obj.zu_angabe()["flipV"]
    ohne_flip = deepcopy(geladen.modell)
    for section in ohne_flip.sections:
        for block in section.content:
            if isinstance(block, Paragraph) and P_BILDANKER in block.format.properties:
                items = json.loads(block.format.properties[P_BILDANKER])
                for item in items:
                    item.pop("flipH", None); item.pop("flipV", None)
                block.format.properties[P_BILDANKER] = json.dumps(items)
    bild = seiten_aus_modell(geladen.modell)[0]
    bild_ohne_flip = seiten_aus_modell(ohne_flip)[0]
    assert bytes(bild.constBits()) != bytes(bild_ohne_flip.constBits())
    rote = [(x, y) for y in range(bild.height()) for x in range(bild.width()) if bild.pixelColor(x, y).red() > 220 and bild.pixelColor(x, y).green() < 40]
    assert rote and max(y for _x, y in rote) - min(y for _x, y in rote) > 45
    exportiert = tmp_path / "word_gruppe_flags.docx"
    formats.save(str(exportiert), geladen.doc, geladen.page)
    with ZipFile(exportiert) as archiv:
        xml_export = etree.fromstring(archiv.read("word/document.xml"))
    rotierte_xfrm = [x for x in xml_export.iter(q("a", "xfrm")) if x.get("rot") == "2700000"]
    assert rotierte_xfrm and rotierte_xfrm[0].get("flipH") == "1" and rotierte_xfrm[0].get("flipV") == "1"


def test_gruppieren_braucht_zwei(app):
    ed = DocumentEditor()
    _form(ed)
    c = QTextCursor(ed.document()); c.select(QTextCursor.Document); ed.setTextCursor(c)
    assert formen.gruppieren(ed)


def test_tabellenvorlage_docx(app, tmp_path):
    from PySide6.QtGui import QTextCharFormat, QTextTableFormat
    from lunivo_writer.editor.tabelle import tabellenstil as TS
    ed = DocumentEditor()
    t = ed.textCursor().insertTable(3, 2, QTextTableFormat())
    assert TS.anwenden(t, "Blau", kopf=True, streifen=True, spalte=False)
    assert t.cellAt(0, 0).format().background().color().name() == "#2f6fb5"
    assert t.cellAt(2, 0).format().background().color().name() == "#e7f0fa"
    assert t.cellAt(1, 0).format().background().style() == Qt.NoBrush
    cf = t.cellAt(2, 1).format().toTableCellFormat()
    cf.setVerticalAlignment(QTextCharFormat.AlignMiddle); t.cellAt(2, 1).setFormat(cf)
    pfad = str(tmp_path / "t.docx")
    formats.save(pfad, ed.document(), PageSettings())
    doc = formats.load(pfad).doc
    n = doc.rootFrame().childFrames()[0]
    assert n.cellAt(0, 0).format().background().color().name() == "#2f6fb5"
    assert n.cellAt(2, 0).format().background().color().name() == "#e7f0fa"
    assert n.cellAt(2, 1).format().toTableCellFormat().verticalAlignment() == QTextCharFormat.AlignMiddle
    assert n.format().border() == 1
