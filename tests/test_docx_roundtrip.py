import io

import docx
from docx.shared import Pt, RGBColor, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PySide6.QtGui import QImage, QColor, QTextCursor

from lunivo_writer.services.docx_reader import read_docx
from lunivo_writer.services.docx_writer import write_docx
from lunivo_writer.models.report import DocumentIOError
import pytest


def _png():
    img = QImage(40, 20, QImage.Format_RGB32)
    img.fill(QColor("red"))
    from PySide6.QtCore import QBuffer, QIODevice
    b = QBuffer(); b.open(QIODevice.WriteOnly); img.save(b, "PNG")
    return io.BytesIO(bytes(b.data()))


@pytest.fixture
def sample(tmp_path):
    d = docx.Document()
    s = d.sections[0]
    s.page_width, s.page_height = Mm(210), Mm(297)
    s.left_margin = Mm(30)
    d.add_heading("Titel Eins", 1)
    p = d.add_paragraph()
    r = p.add_run("fett "); r.bold = True
    r = p.add_run("kursiv "); r.italic = True
    r = p.add_run("rot"); r.font.color.rgb = RGBColor(255, 0, 0); r.font.size = Pt(18); r.font.name = "DejaVu Serif"
    q = d.add_paragraph("zentriert"); q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    q.paragraph_format.left_indent = Mm(10)
    d.add_paragraph("Punkt A", style="List Bullet")
    d.add_paragraph("Punkt B", style="List Bullet")
    d.add_paragraph("Eins", style="List Number")
    d.add_paragraph("Zwei", style="List Number")
    t = d.add_table(rows=2, cols=2); t.style = "Table Grid"
    t.cell(0, 0).text = "A1"; t.cell(0, 1).text = "B1"; t.cell(1, 0).text = "A2"; t.cell(1, 1).text = "B2"
    d.add_picture(_png(), width=Mm(30))
    d.add_page_break()
    d.add_paragraph("Seite zwei")
    s.footer.is_linked_to_previous = False
    s.footer.paragraphs[0].text = "Fuß"
    f = tmp_path / "in.docx"; d.save(f)
    return str(f)


def texts(path):
    return [p.text for p in docx.Document(path).paragraphs]


def test_read_basic(app, sample):
    qd, page, meta, rep = read_docx(sample)
    txt = qd.toPlainText()
    for w in ("Titel Eins", "fett kursiv rot", "zentriert", "Punkt A", "Zwei", "A1", "B2", "Seite zwei"):
        assert w in txt
    assert abs(page.margin_left_mm - 30) < 0.1
    assert page.footer.text == "Fuß"
    assert qd.firstBlock().blockFormat().headingLevel() == 1


def test_roundtrip_preserves_content_and_format(app, sample, tmp_path):
    qd, page, meta, _ = read_docx(sample)
    out = str(tmp_path / "out.docx")
    write_docx(out, qd, page, meta)
    d = docx.Document(out)
    ps = d.paragraphs
    assert ps[0].style.name == "Heading 1" and ps[0].text == "Titel Eins"
    runs = ps[1].runs
    assert runs[0].bold and "fett" in runs[0].text
    assert any(r.italic for r in runs)
    red = [r for r in runs if r.font.color.rgb == RGBColor(255, 0, 0)]
    assert red and red[0].font.size == Pt(18) and red[0].font.name == "DejaVu Serif"
    cen = [p for p in ps if p.text == "zentriert"][0]
    assert cen.alignment == WD_ALIGN_PARAGRAPH.CENTER
    assert abs(cen.paragraph_format.left_indent.mm - 10) < 0.5
    assert [p.style.name for p in ps if p.text.startswith("Punkt")] == ["List Bullet"] * 2
    assert [p.style.name for p in ps if p.text in ("Eins", "Zwei")] == ["List Number"] * 2
    assert len(d.tables) == 1 and d.tables[0].cell(1, 1).text == "B2"
    assert len(d.inline_shapes) == 1
    assert any(p.paragraph_format.page_break_before for p in ps if p.text == "Seite zwei")
    assert abs(d.sections[0].left_margin.mm - 30) < 0.1
    assert d.sections[0].footer.paragraphs[0].text == "Fuß"


def test_second_roundtrip_is_stable(app, sample, tmp_path):
    qd, page, meta, _ = read_docx(sample)
    a = str(tmp_path / "a.docx"); write_docx(a, qd, page, meta)
    qd2, page2, meta2, _ = read_docx(a)
    b = str(tmp_path / "b.docx"); write_docx(b, qd2, page2, meta2)
    assert texts(a) == texts(b)
    assert qd2.toPlainText() == qd.toPlainText()


def test_numbering_restarts_per_list(app, tmp_path):
    from PySide6.QtGui import QTextDocument, QTextListFormat
    qd = QTextDocument(); c = QTextCursor(qd)
    lf = QTextListFormat(); lf.setStyle(QTextListFormat.ListDecimal)
    c.insertList(lf); c.insertText("a"); c.insertBlock(); c.insertText("b")
    c.insertBlock(); c.setBlockFormat(__import__("PySide6.QtGui", fromlist=["x"]).QTextBlockFormat())
    c.insertText("Zwischentext")
    lf2 = QTextListFormat(); lf2.setStyle(QTextListFormat.ListDecimal)
    c.insertList(lf2); c.insertText("c")
    out = str(tmp_path / "n.docx")
    from lunivo_writer.models.page import PageSettings
    write_docx(out, qd, PageSettings(), {})
    d = docx.Document(out)
    nums = {p.text: p._p.pPr.numPr.numId.val for p in d.paragraphs if p.style.name == "List Number"}
    assert nums["a"] == nums["b"] != nums["c"]


def test_invalid_file(app, tmp_path):
    bad = tmp_path / "kaputt.docx"; bad.write_bytes(b"kein zip")
    with pytest.raises(DocumentIOError):
        read_docx(str(bad))


def test_unsupported_content_is_reported(app, tmp_path):
    d = docx.Document(); p = d.add_paragraph("x")
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    r = OxmlElement("w:r"); tb = OxmlElement("w:txbxContent"); r.append(tb); p._p.append(r)
    f = tmp_path / "f.docx"; d.save(f)
    _, _, _, rep = read_docx(str(f))
    assert any("Textfelder" in w for w in rep.warnings)


def test_seitenfarbe_und_rahmen_roundtrip(tmp_path):
    from PySide6.QtGui import QTextDocument
    from lunivo_writer.services import docx_reader, docx_writer
    from lunivo_writer.models.page import PageSettings
    d = QTextDocument(); d.setPlainText("Seite")
    pg = PageSettings(color="#ffeecc", border={"art": "doppelt", "farbe": "#336699", "breite_pt": 1.5, "abstand_mm": 10.0},
                      watermark={"text": "ENTWURF", "farbe": "#c0c0c0", "winkel": -45, "groesse_pt": 80})
    out = str(tmp_path / "s.docx")
    rep = docx_writer.write_docx(out, d, pg, {})
    assert any("Wasserzeichen" in w for w in rep.warnings)          # wird gemeldet, nicht still verworfen
    _, p2, _, _ = docx_reader.read_docx(out)
    assert p2.color == "#ffeecc"
    assert p2.border["art"] == "doppelt" and p2.border["farbe"] == "#336699"
    assert abs(p2.border["breite_pt"] - 1.5) < 0.2 and abs(p2.border["abstand_mm"] - 10) < 0.6
    assert p2.watermark is None


def test_zeilennummern_und_textrichtung_roundtrip(tmp_path):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QTextBlockFormat, QTextCursor, QTextDocument
    from lunivo_writer.services import docx_reader, docx_writer
    from lunivo_writer.models.page import PageSettings
    d = QTextDocument(); d.setPlainText("Eins\nZwei")
    c = QTextCursor(d.firstBlock()); bf = c.blockFormat(); bf.setLayoutDirection(Qt.RightToLeft); c.setBlockFormat(bf)
    out = str(tmp_path / "z.docx")
    docx_writer.write_docx(out, d, PageSettings(zeilennummern=True), {})
    doc2, p2, _, _ = docx_reader.read_docx(out)
    assert p2.zeilennummern is True
    assert doc2.firstBlock().blockFormat().layoutDirection() == Qt.RightToLeft
    assert doc2.firstBlock().next().blockFormat().layoutDirection() != Qt.RightToLeft


def test_unterstreichungsart_umriss_zeichenabstand_roundtrip(tmp_path):
    from PySide6.QtGui import QColor, QFont, QPen, QTextCharFormat, QTextCursor, QTextDocument
    from lunivo_writer.services import docx_reader, docx_writer
    from lunivo_writer.models.page import PageSettings
    d = QTextDocument(); d.setPlainText("Welle Strich Umriss Weit")
    def fmt(von, bis, f):
        c = QTextCursor(d); c.setPosition(von); c.setPosition(bis, QTextCursor.KeepAnchor); c.mergeCharFormat(f)
    f1 = QTextCharFormat(); f1.setUnderlineStyle(QTextCharFormat.WaveUnderline); fmt(0, 5, f1)
    f2 = QTextCharFormat(); f2.setUnderlineStyle(QTextCharFormat.DashUnderline); fmt(6, 12, f2)
    f3 = QTextCharFormat(); f3.setTextOutline(QPen(QColor("#000000"))); fmt(13, 19, f3)
    f4 = QTextCharFormat(); f4.setFontLetterSpacingType(QFont.AbsoluteSpacing); f4.setFontLetterSpacing(4.0); fmt(20, 24, f4)
    out = str(tmp_path / "u.docx")
    docx_writer.write_docx(out, d, PageSettings(), {})
    d2, _, _, _ = docx_reader.read_docx(out)
    def at(pos):
        c = QTextCursor(d2); c.setPosition(pos + 1); return c.charFormat()
    assert at(0).underlineStyle() == QTextCharFormat.WaveUnderline
    assert at(6).underlineStyle() == QTextCharFormat.DashUnderline
    assert at(13).textOutline().style().value != 0
    assert abs(at(20).fontLetterSpacing() - 4.0) < 0.2
    assert at(14).underlineStyle() == QTextCharFormat.NoUnderline


def test_kopf_und_fusszeile_mit_seitenzahlfeldern_roundtrip(app, tmp_path):
    from PySide6.QtGui import QTextDocument
    from lunivo_writer.services import docx_reader, docx_writer
    from lunivo_writer.models.page import HeaderFooter, PageSettings
    d = QTextDocument(); d.setPlainText("Inhalt")
    pg = PageSettings(header=HeaderFooter("Kopf", "left"), footer=HeaderFooter("Seite {PAGE} von {PAGES}", "right"))
    out = str(tmp_path / "k.docx")
    docx_writer.write_docx(out, d, pg, {})
    _, p2, _, _ = docx_reader.read_docx(out)
    assert p2.header.text == "Kopf" and p2.header.align == "left"
    assert p2.footer.text == "Seite {PAGE} von {PAGES}" and p2.footer.align == "right"


def _lies_schreibe_lies(app, pfad, tmp_path):
    qd, page, meta, _ = read_docx(pfad)
    out = str(tmp_path / "rt.docx")
    write_docx(out, qd, page, meta)
    return read_docx(out)


def test_tabelle_verbunden_schattiert_roundtrip(app, tmp_path):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    d = docx.Document()
    t = d.add_table(rows=3, cols=3); t.style = "Table Grid"
    t.cell(0, 0).merge(t.cell(0, 1))
    t.cell(0, 0).text = "Kopf"
    t.cell(1, 0).text = "x"; t.cell(2, 2).text = "z"
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), "FFCC00")
    t.cell(1, 0)._tc.get_or_add_tcPr().append(shd)
    p = str(tmp_path / "t.docx"); d.save(p)
    qd, _, _, _ = _lies_schreibe_lies(app, p, tmp_path)
    assert "Kopf" in qd.toPlainText() and "z" in qd.toPlainText()
    t2 = docx.Document(str(tmp_path / "rt.docx")).tables[0]
    assert len(t2.rows) == 3 and t2.cell(2, 2).text == "z"
    assert t2.cell(0, 0).text == "Kopf"
    assert "FFCC00" in t2.cell(1, 0)._tc.xml.upper()


def test_hyperlink_und_absatzformate_roundtrip(app, tmp_path):
    from docx.enum.text import WD_LINE_SPACING
    d = docx.Document()
    p = d.add_paragraph("Vor ")
    rid = d.part.relate_to("https://example.org/", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), rid)
    r = OxmlElement("w:r"); t = OxmlElement("w:t"); t.text = "Link"; r.append(t); h.append(r); p._p.append(h)
    q = d.add_paragraph("Abstand")
    q.paragraph_format.space_before, q.paragraph_format.space_after = Pt(12), Pt(6)
    q.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    q.paragraph_format.first_line_indent = Mm(8)
    q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    f = str(tmp_path / "h.docx"); d.save(f)
    _lies_schreibe_lies(app, f, tmp_path)
    d2 = docx.Document(str(tmp_path / "rt.docx"))
    assert "https://example.org/" in [r.target_ref for r in d2.part.rels.values() if r.is_external]
    assert "Link" in d2.paragraphs[0].text
    pf = d2.paragraphs[1].paragraph_format
    assert pf.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY
    assert abs(pf.space_before.pt - 12) < 0.6 and abs(pf.space_after.pt - 6) < 0.6
    assert pf.first_line_indent is not None and abs(pf.first_line_indent.mm - 8) < 0.6


def test_hochformat_querformat_und_ränder_roundtrip(app, tmp_path):
    from docx.enum.section import WD_ORIENT
    d = docx.Document()
    s = d.sections[0]
    s.orientation = WD_ORIENT.LANDSCAPE
    s.page_width, s.page_height = Mm(297), Mm(210)
    s.top_margin, s.bottom_margin, s.right_margin = Mm(15), Mm(20), Mm(25)
    d.add_paragraph("quer")
    f = str(tmp_path / "q.docx"); d.save(f)
    _, page, _, _ = _lies_schreibe_lies(app, f, tmp_path)
    assert page.width_mm > page.height_mm
    assert abs(page.margin_top_mm - 15) < 0.2 and abs(page.margin_bottom_mm - 20) < 0.2 and abs(page.margin_right_mm - 25) < 0.2
