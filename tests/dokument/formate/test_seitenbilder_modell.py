"""Kopf-/Fußbilder (``PageSettings.bilder``) bleiben beim Rendern, im PDF und beim DOCX-Rundlauf erhalten — alles über das Dokumentenmodell."""
import base64
import zipfile
from pathlib import Path

import pytest
from PySide6.QtCore import QBuffer, QByteArray, QIODevice
from PySide6.QtGui import QColor, QImage

from lunivo_writer.modelle.seite import PageSettings
from tests.hilfen_dokument import als_pdf, dokument, docx_rundlauf, seiten_dokument

DATEN = Path(__file__).parents[2] / "editor" / "daten"


def _png(farbe: str, breite: int = 24, hoehe: int = 24) -> bytes:
    img = QImage(breite, hoehe, QImage.Format_ARGB32)
    img.fill(QColor(farbe))
    puffer = QByteArray(); ziel = QBuffer(puffer); ziel.open(QIODevice.WriteOnly)
    img.save(ziel, "PNG"); ziel.close()
    return bytes(puffer)


def _seitenbild(ort: str, daten: bytes, *, hinter: bool = False, x: float = 20, y: float = 20, b: float = 24, h: float = 24) -> dict:
    return {"ort": ort, "bild": daten, "b": float(b), "h": float(h), "bh": "seite", "bv": "seite", "xh": x, "yv": y, "ah": "", "av": "", "hinter": hinter}


def _seite(dok, n: int = 1) -> QImage:
    from lunivo_writer.dienste.drucken import Ausgabe
    return Ausgabe(dok).bild(n)


def test_rendern_zeichnet_seitenbilder_und_bildwasserzeichen(app):
    page = PageSettings()
    page.diff_first = True
    page.bilder = [_seitenbild("kopf", _png("red")), _seitenbild("kopf1", _png("blue"), hinter=True)]
    page.watermark = {"bild": base64.b64encode(_png("yellow", 8, 8)).decode(), "ganzseitig": True, "transparenz": 0, "auswaschen": False}
    d = seiten_dokument(2, "Seite {n}", page)
    assert _seite(d, 1).pixelColor(22, 22) == QColor("blue")           # erste Seite verwendet kopf1
    assert _seite(d, 2).pixelColor(22, 22) == QColor("red")            # Folgeseite verwendet kopf
    assert _seite(d, 1).pixelColor(80, 80) == QColor("yellow")         # Bildwasserzeichen aus PageSettings


def test_docx_rundlauf_erhaelt_kopf_fussbilder(app, tmp_path):
    page = PageSettings()
    page.bilder = [_seitenbild("kopf", _png("blue"), hinter=True), _seitenbild("fuss", _png("red"), x=70, y=70)]
    gelesen, schreib, lese, _pfad = docx_rundlauf(dokument("Briefinhalt", page), tmp_path)
    assert not schreib.warnings and not lese.warnings
    seite = _seite(gelesen)
    assert seite.pixelColor(22, 22) == QColor("blue") and seite.pixelColor(72, 72) == QColor("red")


def test_docx_kopfzeilenbild_mit_wrapthrough_wird_gezeichnet(app, tmp_path):
    from copy import deepcopy
    from io import BytesIO
    from docx import Document
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from lunivo_writer.dienste.modell_laden import lade_modell

    dok = Document()
    dok.add_paragraph("Dokumentinhalt")
    run = dok.sections[0].header.paragraphs[0].add_run()
    run.add_picture(BytesIO(_png("#3366cc", 16, 16)))
    inline = run._r.xpath("./w:drawing/wp:inline")[0]
    anchor = OxmlElement("wp:anchor")
    for schluessel, wert in (("distT", "0"), ("distB", "0"), ("distL", "0"), ("distR", "0"), ("simplePos", "0"), ("relativeHeight", "0"), ("behindDoc", "0"),
                             ("locked", "0"), ("layoutInCell", "1"), ("allowOverlap", "1")):
        anchor.set(schluessel, wert)
    simple = OxmlElement("wp:simplePos"); simple.set("x", "0"); simple.set("y", "0")
    ph = OxmlElement("wp:positionH"); ph.set("relativeFrom", "page")
    oh = OxmlElement("wp:posOffset"); oh.text = str(20 * 9525); ph.append(oh)
    pv = OxmlElement("wp:positionV"); pv.set("relativeFrom", "page")
    ov = OxmlElement("wp:posOffset"); ov.text = str(20 * 9525); pv.append(ov)
    wrap = OxmlElement("wp:wrapThrough"); wrap.set("wrapText", "bothSides")
    anchor.append(simple); anchor.append(ph); anchor.append(pv)
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
    dok.save(pfad)
    geladen = lade_modell(str(pfad))
    assert len(geladen.page.bilder) == 1
    assert _seite(geladen.document).pixelColor(22, 22) == QColor("#3366cc")


def test_pdf_export_zeichnet_seitenbild(app, tmp_path):
    from pypdf import PdfReader
    page = PageSettings(); page.bilder = [_seitenbild("kopf", _png("blue"))]
    pfad = tmp_path / "kopf.pdf"
    assert als_pdf(dokument("PDF mit Kopfzeilenbild", page), pfad) == 1
    pdfseite = PdfReader(str(pfad)).pages[0]
    assert "PDF mit Kopfzeilenbild" in " ".join(pdfseite.extract_text().split())
    assert pdfseite["/Resources"].get_object().get("/XObject")


def test_docx_rundlauf_erhaelt_svg_quelle_der_kopfzeile(app, tmp_path):
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="32" height="24"><rect width="32" height="24" fill="#3366cc"/></svg>'
    page = PageSettings(); page.bilder = [_seitenbild("kopf", svg, b=32, h=24)]
    gelesen, schreib, _lese, pfad = docx_rundlauf(dokument("Inhalt", page), tmp_path)
    bilder = gelesen.abschnitte[0].seite.bilder
    assert len(bilder) == 1 and gelesen.ressourcen[bilder[0]["ressource"]] == svg
    assert any("SVG" in w for w in schreib.warnings)                    # die Einschränkung wird gemeldet, nicht verschwiegen
    with zipfile.ZipFile(pfad) as archiv:
        assert any(n.endswith(".svg") for n in archiv.namelist())


@pytest.mark.parametrize("name", ["libreoffice.emf", "libreoffice.wmf"])
def test_docx_rundlauf_erhaelt_metafile_quelle_in_kopfzeile(app, tmp_path, name):
    original = (DATEN / name).read_bytes()
    page = PageSettings(); page.bilder = [_seitenbild("kopf", original, b=48, h=48)]
    gelesen, schreib, _lese, _pfad = docx_rundlauf(dokument("Briefinhalt", page), tmp_path)
    bilder = gelesen.abschnitte[0].seite.bilder
    assert len(bilder) == 1 and gelesen.ressourcen[bilder[0]["ressource"]] == original
    assert not schreib.warnings
