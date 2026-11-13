"""Kopf-/Fußbilder bleiben beim Modell-Rendern und beim DOCX/ODT-Rundlauf erhalten."""
from pathlib import Path

import pytest
from PySide6.QtGui import QColor, QImage, QTextCursor, QTextDocument, QTextFormat

from lunivo_writer.adapter.qt.dokument import document_from_qt
from lunivo_writer.adapter.qt.seitenbild import seiten_aus_modell
from lunivo_writer.dienste import datei_dienst as dateien
from lunivo_writer.editor.objekte import bilddaten as BD
from lunivo_writer.editor.seite import abschnitte as AB
from lunivo_writer.editor.seite.wasserzeichen import bild_zu_text
from lunivo_writer.modelle.seite import PageSettings


def _bild(farbe: str, breite: int = 24, hoehe: int = 24) -> QImage:
    img = QImage(breite, hoehe, QImage.Format_ARGB32)
    img.fill(QColor(farbe))
    return img


def _seitenbild(ort: str, bild: QImage, *, hinter: bool = False, x: float = 20, y: float = 20, b: float | None = None, h: float | None = None) -> dict:
    return {"ort": ort, "bild": bild, "b": float(b if b is not None else bild.width()), "h": float(h if h is not None else bild.height()), "bh": "seite", "bv": "seite",
            "xh": x, "yv": y, "ah": "", "av": "", "hinter": hinter}


def test_modell_rendern_zeichnet_seitenbilder_und_bildwasserzeichen(app):
    doc = QTextDocument()
    cursor = QTextCursor(doc)
    cursor.insertText("Erste Seite")
    cursor.insertBlock()
    bf = cursor.blockFormat(); bf.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore); cursor.setBlockFormat(bf)
    cursor.insertText("Zweite Seite")

    page = PageSettings()
    page.diff_first = True
    page.bilder = [_seitenbild("kopf", _bild("red")), _seitenbild("kopf1", _bild("blue"), hinter=True)]
    page.watermark = {"bild": bild_zu_text(_bild("yellow", 8, 8)), "ganzseitig": True, "transparenz": 0, "auswaschen": False}
    seiten = seiten_aus_modell(document_from_qt(doc, page))

    assert len(seiten) == 2
    assert seiten[0].pixelColor(22, 22) == QColor("blue")            # erste Seite verwendet kopf1
    assert seiten[1].pixelColor(22, 22) == QColor("red")             # Folgeseite verwendet kopf
    assert seiten[0].pixelColor(80, 80) == QColor("yellow")          # Bildwasserzeichen aus PageSettings


def test_docx_und_odt_rundlauf_erhaelt_kopf_fussbilder_im_modell_rendern(app, tmp_path):
    doc = QTextDocument(); QTextCursor(doc).insertText("Briefinhalt")
    page = PageSettings()
    page.bilder = [_seitenbild("kopf", _bild("blue"), hinter=True), _seitenbild("fuss", _bild("red"), x=70, y=70)]
    for endung in ("docx", "odt"):
        path = tmp_path / f"brief.{endung}"
        assert not dateien.save(str(path), doc, page, {}).warnings
        geladen = dateien.load(str(path))
        assert not geladen.report.warnings
        bildseite = seiten_aus_modell(document_from_qt(geladen.doc, geladen.page))[0]
        assert bildseite.pixelColor(22, 22) == QColor("blue")
        assert bildseite.pixelColor(72, 72) == QColor("red")


def test_docx_kopfzeilenbild_mit_wrapthrough_wird_im_modell_gezeichnet(app, tmp_path):
    from copy import deepcopy
    from io import BytesIO
    from docx import Document
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from PySide6.QtCore import QBuffer, QByteArray, QIODevice

    logo = _bild("#3366cc", 16, 16)
    puffer = QByteArray(); ausgabe = QBuffer(puffer); ausgabe.open(QIODevice.WriteOnly)
    logo.save(ausgabe, "PNG"); ausgabe.close()
    dokument = Document()
    dokument.add_paragraph("Dokumentinhalt")
    header = dokument.sections[0].header
    run = header.paragraphs[0].add_run()
    run.add_picture(BytesIO(bytes(puffer)))
    inline = run._r.xpath("./w:drawing/wp:inline")[0]
    anchor = OxmlElement("wp:anchor")
    for schluessel, wert in (("distT", "0"), ("distB", "0"), ("distL", "0"), ("distR", "0"),
                             ("simplePos", "0"), ("relativeHeight", "0"), ("behindDoc", "0"),
                             ("locked", "0"), ("layoutInCell", "1"), ("allowOverlap", "1")):
        anchor.set(schluessel, wert)
    simple = OxmlElement("wp:simplePos"); simple.set("x", "0"); simple.set("y", "0")
    position_h = OxmlElement("wp:positionH"); position_h.set("relativeFrom", "page")
    offset_h = OxmlElement("wp:posOffset"); offset_h.text = str(20 * 9525); position_h.append(offset_h)
    position_v = OxmlElement("wp:positionV"); position_v.set("relativeFrom", "page")
    offset_v = OxmlElement("wp:posOffset"); offset_v.text = str(20 * 9525); position_v.append(offset_v)
    wrap = OxmlElement("wp:wrapThrough"); wrap.set("wrapText", "bothSides")
    anchor.append(simple); anchor.append(position_h); anchor.append(position_v)
    for tag in ("extent", "effectExtent"):
        el = inline.find(qn("wp:" + tag))
        if el is not None:
            anchor.append(deepcopy(el))
    anchor.append(wrap)
    for tag in ("docPr", "cNvGraphicFramePr", "graphic"):
        el = inline.find(qn("wp:" + tag))
        if el is None and tag == "graphic":
            el = inline.find(qn("a:graphic"))
        if el is not None:
            anchor.append(deepcopy(el))
    inline.addprevious(anchor); inline.getparent().remove(inline)

    pfad = tmp_path / "kopf_wrapthrough.docx"
    dokument.save(pfad)
    geladen = dateien.load(str(pfad))
    assert len(geladen.page.bilder) == 1
    bildseite = seiten_aus_modell(document_from_qt(geladen.doc, geladen.page))[0]
    assert bildseite.pixelColor(22, 22) == QColor("#3366cc")


def test_normaler_pdf_export_nutzt_modellpfad_mit_seitenbild(app, tmp_path, monkeypatch):
    from pypdf import PdfReader
    import lunivo_writer.editor.seite.seiten_aufteilung as SA
    doc = QTextDocument(); QTextCursor(doc).insertText("PDF mit Kopfzeilenbild")
    page = PageSettings(); page.bilder = [_seitenbild("kopf", _bild("blue"))]
    monkeypatch.setattr(SA, "render_dokument", lambda *a, **k: (_ for _ in ()).throw(AssertionError("Qt-Rückfall unerwartet")))
    path = tmp_path / "kopf.pdf"
    assert SA.export_pdf(str(path), doc, page) == 1
    pdfseite = PdfReader(str(path)).pages[0]
    assert "PDF mit Kopfzeilenbild" in " ".join(pdfseite.extract_text().split())
    assert pdfseite["/Resources"].get_object().get("/XObject")


def test_docx_abschnitt_erhaelt_svg_quelle_der_kopfzeile_im_rundlauf(app, tmp_path):
    from lunivo_writer.editor.objekte.bilddaten import bild_aus_svg

    doc = QTextDocument(); cursor = QTextCursor(doc); cursor.insertText("Erster Abschnitt")
    page = PageSettings()
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="32" height="24"><rect width="32" height="24" fill="#3366cc"/></svg>'
    logo = bild_aus_svg(svg)
    AB.einfuegen(doc, cursor, "naechste", page)
    abschnitt = AB.einrichtung(doc, page, 1)
    abschnitt.bilder = [_seitenbild("kopf", logo)]
    AB.setzen(doc, 1, abschnitt)

    path = tmp_path / "svg.docx"
    assert not dateien.save(str(path), doc, page, {}).warnings
    geladen = dateien.load(str(path))
    abschnitt_zurueck = AB.einrichtung(geladen.doc, geladen.page, 1)
    quelle = BD.quelle_zu(abschnitt_zurueck.bilder[0]["bild"])
    assert quelle is not None and quelle.format == "svg" and quelle.daten == svg

    zweiter_lauf = tmp_path / "svg-zweiter-lauf.docx"
    assert not dateien.save(str(zweiter_lauf), geladen.doc, geladen.page, {}).warnings
    with __import__("zipfile").ZipFile(zweiter_lauf) as archiv:
        assert any(n.endswith(".svg") for n in archiv.namelist())


@pytest.mark.parametrize(("name", "format"), [("libreoffice.emf", "emf"), ("libreoffice.wmf", "wmf")])
def test_modell_rendern_zeichnet_vektorquelle_statt_nur_raster(app, name, format):
    daten = Path(__file__).parents[2] / "editor" / "daten" / name
    logo = BD.bild_aus_datei(str(daten))
    assert BD.quelle_zu(logo).format == format
    breite, hoehe = BD.anzeigegroesse(logo)
    doc = QTextDocument(); QTextCursor(doc).insertText("Briefinhalt")
    page = PageSettings()
    page.bilder = [_seitenbild("kopf", logo, b=breite, h=hoehe)]
    gerendert = seiten_aus_modell(document_from_qt(doc, page))[0]
    ecke, mitte = gerendert.pixelColor(24, 24), gerendert.pixelColor(round(20 + breite / 2), round(20 + hoehe / 2))
    assert ecke.red() > 200 and ecke.blue() < 80
    assert mitte.blue() > 200 and mitte.red() < 80


@pytest.mark.parametrize("endung", ["docx", "odt"])
@pytest.mark.parametrize(("name", "format"), [("libreoffice.emf", "emf"), ("libreoffice.wmf", "wmf")])
def test_docx_odt_rundlauf_erhaelt_metafile_quelle_in_kopfzeile(app, tmp_path, endung, name, format):
    daten = Path(__file__).parents[2] / "editor" / "daten" / name
    logo = BD.bild_aus_datei(str(daten))
    original = BD.quelle_zu(logo).daten
    doc = QTextDocument(); QTextCursor(doc).insertText("Briefinhalt")
    page = PageSettings(); page.bilder = [_seitenbild("kopf", logo)]
    pfad = tmp_path / f"metafile.{endung}"
    assert not dateien.save(str(pfad), doc, page, {}).warnings
    geladen = dateien.load(str(pfad))
    quelle = BD.quelle_zu(geladen.page.bilder[0]["bild"])
    assert quelle is not None and quelle.format == format and quelle.daten == original
