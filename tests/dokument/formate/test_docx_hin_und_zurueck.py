"""DOCX → Dokumentenmodell → DOCX: Inhalt und Formate bleiben erhalten (Lesen und Schreiben ohne Qt-Textdokument)."""
import io

import docx
import pytest
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Mm, Pt, RGBColor
from PySide6.QtGui import QColor, QImage

from lunivo_writer.core.document.dokument import Auswahl, InlineObjekt, Lauf, Position
from lunivo_writer.core.document.formatvorlagen import ueberschriftsebene, wirksames_absatzformat
from lunivo_writer.core.layout import formatwerte as F
from lunivo_writer.dienste.docx_modell_schreiber import docx_dokument_daten
from lunivo_writer.dienste.modell_laden import lade_modell
from lunivo_writer.modelle.bericht import DocumentIOError
from lunivo_writer.modelle.seite import PageSettings
from tests.hilfen_dokument import docx_rundlauf, sitzung


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


def _schreiben(g, pfad):
    daten, bericht = docx_dokument_daten(g.document, g.page, g.meta)
    with open(pfad, "wb") as f:
        f.write(daten)
    return bericht


def test_read_basic(app, sample):
    g = lade_modell(sample)
    txt = g.document.text()
    for w in ("Titel Eins", "fett kursiv rot", "zentriert", "Punkt A", "Zwei", "A1", "B2", "Seite zwei"):
        assert w in txt
    assert abs(g.page.margin_left_mm - 30) < 0.1
    assert g.page.footer.text == "Fuß"
    assert ueberschriftsebene(g.document, next(iter(g.document.absaetze()))) == 1


def test_read_uses_docx_paragraph_defaults_after_style_values(app, tmp_path):
    from docx.enum.style import WD_STYLE_TYPE
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    d = docx.Document()
    ppr_default = d.styles.element.find(qn("w:docDefaults") + "/" + qn("w:pPrDefault") + "/" + qn("w:pPr"))
    if ppr_default is None:
        ppr_default = OxmlElement("w:pPr")
        ppr_default_default = d.styles.element.find(qn("w:docDefaults") + "/" + qn("w:pPrDefault"))
        if ppr_default_default is None:
            ppr_default_default = OxmlElement("w:pPrDefault")
            d.styles.element.find(qn("w:docDefaults")).append(ppr_default_default)
        ppr_default_default.append(ppr_default)
    spacing = ppr_default.find(qn("w:spacing"))
    if spacing is None:
        spacing = OxmlElement("w:spacing")
        ppr_default.append(spacing)
    spacing.set(qn("w:after"), "200")
    spacing.set(qn("w:line"), "276")
    spacing.set(qn("w:lineRule"), "auto")

    explicit = d.styles.add_style("Explicit Paragraph", WD_STYLE_TYPE.PARAGRAPH)
    explicit.base_style = d.styles["Normal"]
    explicit.paragraph_format.space_after = Pt(3)
    explicit.paragraph_format.line_spacing = 1.5
    d.add_paragraph("Dokumentstandard")
    d.add_paragraph("Stilvorgabe", style=explicit)
    path = tmp_path / "doc-defaults.docx"
    d.save(path)

    g = lade_modell(str(path))
    absaetze = list(g.document.absaetze())
    standard = F.absatzformat(g.document, absaetze[0])
    stil = F.absatzformat(g.document, absaetze[-1])
    assert F.abstaende(standard)[1] == pytest.approx(200 * 96 / 1440)
    assert F.zeilenabstand(standard) == ("proportional", pytest.approx(115))
    assert F.abstaende(stil)[1] == pytest.approx(3 * 96 / 72)
    assert F.zeilenabstand(stil) == ("proportional", pytest.approx(150))


def test_vml_objekt_wird_erhalten_und_zurueckgeschrieben(app, tmp_path):
    """Ein VML-Objekt (hier ein Strich) im Text lässt sich im Modell nicht abbilden: Es bleibt erhalten, der Bericht meldet es, und es wird wieder geschrieben."""
    from docx.oxml import OxmlElement, parse_xml
    import zipfile
    d = docx.Document()
    pict = OxmlElement("w:pict")
    pict.append(parse_xml('<v:rect xmlns:v="urn:schemas-microsoft-com:vml" id="_x0000_i1025" style="width:226.9pt;height:1pt"/>'))
    d.add_paragraph().add_run()._r.append(pict)
    pfad = tmp_path / "vml-rect.docx"
    d.save(pfad)
    g = lade_modell(str(pfad))
    objekte = [x for a in g.document.absaetze() for x in a.inhalte if isinstance(x, InlineObjekt)]
    assert len(objekte) == 1 and objekte[0].art in ("roh", "form")
    assert g.report.warnings or objekte[0].art == "form"
    _gelesen, schreib, _lese, aus = docx_rundlauf(g.document, tmp_path, "vml-zurueck.docx")
    assert not schreib.warnings
    assert "_x0000_i1025" in zipfile.ZipFile(aus).read("word/document.xml").decode()


def test_roundtrip_preserves_content_and_format(app, sample, tmp_path):
    g = lade_modell(sample)
    out = str(tmp_path / "out.docx")
    _schreiben(g, out)
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
    punkte = [p for p in ps if p.text.startswith("Punkt")]
    zahlen = [p for p in ps if p.text in ("Eins", "Zwei")]
    assert len(punkte) == 2 and len(zahlen) == 2 and all(p._p.pPr is not None and p._p.pPr.numPr is not None for p in punkte + zahlen)
    assert punkte[0]._p.pPr.numPr.numId.val == punkte[1]._p.pPr.numPr.numId.val != zahlen[0]._p.pPr.numPr.numId.val
    assert len(d.tables) == 1 and d.tables[0].cell(1, 1).text == "B2"
    assert len(d.inline_shapes) == 1
    assert any(p.paragraph_format.page_break_before for p in ps if p.text == "Seite zwei")
    assert abs(d.sections[0].left_margin.mm - 30) < 0.1
    assert d.sections[0].footer.paragraphs[0].text == "Fuß"


def test_second_roundtrip_is_stable(app, sample, tmp_path):
    g = lade_modell(sample)
    a = str(tmp_path / "a.docx"); _schreiben(g, a)
    g2 = lade_modell(a)
    b = str(tmp_path / "b.docx"); _schreiben(g2, b)
    assert texts(a) == texts(b)
    assert g2.document.text() == g.document.text()


def test_numbering_restarts_per_list(app, tmp_path):
    s = sitzung("a\nb\nZwischentext\nc")
    a = list(s.dokument.absaetze())
    erste = s.liste_anlegen("dezimal")
    s.liste_anwenden(erste, Auswahl(Position(a[0].id, 0), Position(a[1].id, 1)))
    zweite = s.liste_anlegen("dezimal")
    s.liste_anwenden(zweite, Auswahl(Position(a[3].id, 0), Position(a[3].id, 1)))
    _gelesen, _s, _l, out = docx_rundlauf(s.dokument, tmp_path, "n.docx")
    d = docx.Document(str(out))
    nums = {p.text: p._p.pPr.numPr.numId.val for p in d.paragraphs if p._p.pPr is not None and p._p.pPr.numPr is not None}
    assert nums["a"] == nums["b"] != nums["c"]


def test_invalid_file(app, tmp_path):
    bad = tmp_path / "kaputt.docx"; bad.write_bytes(b"kein zip")
    with pytest.raises(DocumentIOError):
        lade_modell(str(bad))


def test_unsupported_content_is_reported(app, tmp_path):
    """Etwas, das weder abgebildet noch erhalten werden kann, wird benannt: Die Datei wird nicht unvollständig geöffnet."""
    d = docx.Document(); p = d.add_paragraph("x")
    from docx.oxml import OxmlElement
    r = OxmlElement("w:r"); tb = OxmlElement("w:txbxContent"); r.append(tb); p._p.append(r)
    f = tmp_path / "f.docx"; d.save(f)
    with pytest.raises(DocumentIOError, match="nicht abbilden"):
        lade_modell(str(f))


def test_seitenfarbe_und_rahmen_roundtrip(app, tmp_path):
    pg = PageSettings(color="#ffeecc", border={"art": "doppelt", "farbe": "#336699", "breite_pt": 1.5, "abstand_mm": 10.0},
                      watermark={"text": "ENTWURF", "farbe": "#c0c0c0", "winkel": -45, "groesse_pt": 80})
    gelesen, _schreib, _lese, _pfad = docx_rundlauf(sitzung("Seite", pg).dokument, tmp_path, "s.docx", pg)
    p2 = gelesen.abschnitte[0].seite
    assert p2.color == "#ffeecc"
    assert p2.border["art"] == "doppelt" and p2.border["farbe"] == "#336699"
    assert abs(p2.border["breite_pt"] - 1.5) < 0.2 and abs(p2.border["abstand_mm"] - 10) < 0.6
    assert p2.watermark and p2.watermark.get("text") == "ENTWURF"


def test_zeilennummern_und_textrichtung_roundtrip(app, tmp_path):
    pg = PageSettings(zeilennummern=True)
    s = sitzung("Eins\nZwei", pg)
    s.absatzformat_anwenden({"richtung": "rtl"}, absatz_ids=[next(iter(s.dokument.absaetze())).id])
    gelesen, _schreib, _lese, _pfad = docx_rundlauf(s.dokument, tmp_path, "z.docx", pg)
    assert gelesen.abschnitte[0].seite.zeilennummern is True
    a = list(gelesen.absaetze())
    assert F.richtung(F.absatzformat(gelesen, a[0])) == "rtl" and F.richtung(F.absatzformat(gelesen, a[1])) != "rtl"


def test_unterstreichungsart_zeichenabstand_umriss_roundtrip(app, tmp_path):
    s = sitzung("Welle Strich Umriss Weit")
    a = next(iter(s.dokument.absaetze()))

    def fmt(von, bis, **f):
        s.zeichenformat_anwenden(f, Auswahl(Position(a.id, von), Position(a.id, bis)))
    fmt(0, 5, unterstrichen=True, unter_art="wellig")
    fmt(6, 12, unterstrichen=True, unter_art="gestrichelt")
    fmt(13, 19, effekt={"kontur": True})
    fmt(20, 24, zeichenabstand=4.0)
    gelesen, schreib, _lese, pfad = docx_rundlauf(s.dokument, tmp_path, "u.docx")
    import zipfile
    xml = zipfile.ZipFile(pfad).read("word/document.xml").decode()
    assert 'w:u w:val="wave"' in xml and 'w:u w:val="dash"' in xml and 'w:spacing w:val="80"' in xml
    assert "textOutline" in xml and not any("effekt" in w for w in schreib.warnings)       # der Umriss steht als w14-Effekt in der Datei
    assert gelesen.text() == "Welle Strich Umriss Weit"
