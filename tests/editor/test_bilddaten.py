"""Originalbytes von Bildern (Phase 1): JPEG bleibt beim Speichern bytegleich, bearbeitete Bilder werden PNG, Formate am Dateikopf."""
import io
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import zipfile

import pytest
from PySide6.QtGui import QColor, QImage

from lunivo_writer.editor.objekte import bilddaten as BD


@pytest.fixture
def fenster(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.dienste.einstellungen_dienst import Settings
    from lunivo_writer.oberflaeche.programmfenster import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document(); w.resize(1200, 800); w.show()
    yield w
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def _jpeg(pfad):
    img = QImage(64, 32, QImage.Format_RGB32)
    img.fill(QColor("orange"))
    assert img.save(str(pfad), "JPEG", 77)
    return open(pfad, "rb").read()


def test_format_erkennen_am_kopf():
    assert BD.format_erkennen(b"\x89PNG\r\n\x1a\n....") == "png"
    assert BD.format_erkennen(b"\xff\xd8\xff\xe0") == "jpeg"
    assert BD.format_erkennen(b'<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"/>') == "svg"
    assert BD.format_erkennen(b"RIFF\x00\x00\x00\x00WEBPVP8 ") == "webp"
    assert BD.format_erkennen(b"kein bild") is None


def test_zu_grosse_datei_und_gepackte_bombe(tmp_path, monkeypatch):
    p = tmp_path / "gross.png"
    p.write_bytes(b"\x89PNG" + b"0" * 100)
    monkeypatch.setattr(BD, "MAX_DATEI_BYTES", 50)
    with pytest.raises(BD.BildFehler, match="zu groß"):
        BD.bild_aus_datei(str(p))
    assert BD.bild_aus_datei(str(p), still=True).isNull()
    import gzip
    monkeypatch.setattr(BD, "MAX_ENTPACKT_BYTES", 100)
    with pytest.raises(BD.BildFehler):
        BD.entpacken(gzip.compress(b"0" * 5000))


def test_jpeg_bleibt_in_docx_odt_rtf_bytegleich(fenster, tmp_path):
    from lunivo_writer.dienste import docx_schreiber, odt_schreiber, rtf_schreiber
    ed = fenster.current_editor()
    original = _jpeg(tmp_path / "foto.jpg")
    assert ed.insert_image(str(tmp_path / "foto.jpg"))
    d = docx_schreiber.docx_daten(ed.document(), ed.page, {})[0]
    with zipfile.ZipFile(io.BytesIO(d)) as z:
        medien = [n for n in z.namelist() if n.startswith("word/media/")]
        assert [z.read(n) for n in medien] == [original] and medien[0].endswith(".jpg")
    o = odt_schreiber.odt_daten(ed.document(), ed.page, {})[0]
    with zipfile.ZipFile(io.BytesIO(o)) as z:
        bilder = [n for n in z.namelist() if n.startswith("Pictures/")]
        assert [z.read(n) for n in bilder] == [original] and bilder[0].endswith(".jpg")
        assert 'media-type="image/jpeg" manifest:full-path="Pictures/' in z.read("META-INF/manifest.xml").decode()
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QTextDocument, QTextImageFormat
    img = BD.bild_aus_datei(str(tmp_path / "foto.jpg"))            # Bild im Text (RTF schreibt keine frei positionierten Bilder)
    ed.document().addResource(QTextDocument.ImageResource, QUrl("im-text"), img)
    f = QTextImageFormat(); f.setName("im-text"); f.setWidth(64); f.setHeight(32)
    ed.textCursor().insertImage(f)
    assert b"\\jpegblip" in rtf_schreiber.rtf_daten(ed.document(), ed.page, {})[0]


def test_bearbeitetes_bild_wird_png(fenster, tmp_path):
    from lunivo_writer.dienste import docx_schreiber
    from lunivo_writer.editor.objekte import bildlayout as BL
    ed = fenster.current_editor()
    _jpeg(tmp_path / "foto.jpg")
    assert ed.insert_image(str(tmp_path / "foto.jpg"))
    assert BL.frei_bild_ersetzen(ed, BL.ziel(ed), lambda i: i.flipped())
    d = docx_schreiber.docx_daten(ed.document(), ed.page, {})[0]
    with zipfile.ZipFile(io.BytesIO(d)) as z:
        assert all(n.endswith(".png") for n in z.namelist() if n.startswith("word/media/"))


# ---- Phase 2: SVG als Vektor ----------------------------------------------------------------------------------------------------
SVG = (b'<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" width="200" height="100" viewBox="0 0 200 100">'
       b'<rect width="200" height="100" fill="#ff0000"/><circle cx="100" cy="50" r="40" fill="#0000ff"/></svg>')


def _svg_einfuegen(ed, tmp_path):
    (tmp_path / "bild.svg").write_bytes(SVG)
    assert ed.insert_image(str(tmp_path / "bild.svg"))


def _frei_bilder(ed):
    from lunivo_writer.editor.objekte import freie_bilder as FB
    d = ed.document()
    b = d.firstBlock()
    while b.isValid():
        for a in FB.aus_absatz(b.blockFormat()):
            yield a, FB.bild_im_dokument(d, a["n"])
        b = b.next()


def test_svg_startgroesse_ersatz_und_sicherheit():
    img = BD.bild_aus_svg(SVG)
    assert BD.ist_svg(img) and max(img.width(), img.height()) == BD.ERSATZ_SEITE and BD.anzeigegroesse(img) == (200.0, 100.0)
    assert BD.quelle_zu(img).ersatz_png.startswith(b"\x89PNG")
    boese = b'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><image xlink:href="/etc/passwd" width="9" height="9"/></svg>'
    assert b"passwd" not in BD.svg_bereinigen(boese)


def test_svg_docx_wie_word_und_zurueck(fenster, tmp_path):
    from lunivo_writer.dienste import docx_leser, docx_schreiber
    ed = fenster.current_editor()
    _svg_einfuegen(ed, tmp_path)
    pfad = str(tmp_path / "s.docx")
    docx_schreiber.write_docx(pfad, ed.document(), ed.page, {})
    with zipfile.ZipFile(pfad) as z:
        xml = z.read("word/document.xml").decode()
        svgs = [n for n in z.namelist() if n.endswith(".svg")]
        assert 'uri="{96DAC541-7B7A-43D3-8B79-37D633B846F1}"' in xml and "svgBlip" in xml
        assert len(svgs) == 1 and z.read(svgs[0]) == SVG
        assert 'image/svg+xml' in z.read("[Content_Types].xml").decode()
        assert any(n.endswith(".png") for n in z.namelist() if n.startswith("word/media/"))
    doc, *_ = docx_leser.read_docx(pfad)
    gelesen = list(_frei_bilder(type("E", (), {"document": lambda self: doc})()))
    assert len(gelesen) == 1 and BD.ist_svg(gelesen[0][1]) and BD.quelle_zu(gelesen[0][1]).daten == SVG


def test_svg_aus_word_datei_wird_gelesen(tmp_path):
    """Eine DOCX, wie Word sie schreibt (PNG-Ersatz im Blip, SVG per Erweiterung), unabhängig von Lunivos Schreiber aus python-docx gebaut."""
    import docx
    from docx.opc.constants import RELATIONSHIP_TYPE as RT
    from docx.opc.packuri import PackURI
    from docx.opc.part import Part
    from docx.shared import Emu
    from lxml import etree
    from lunivo_writer.dienste import docx_leser
    png = BD.png_bytes(BD.svg_raster(SVG, 100))
    d = docx.Document()
    run = d.add_paragraph().add_run()
    run.add_picture(io.BytesIO(png), width=Emu(1905000), height=Emu(952500))
    teil = Part(PackURI("/word/media/image9.svg"), "image/svg+xml", SVG, d.part.package)
    rid = d.part.relate_to(teil, RT.IMAGE)
    blip = run._r.xpath(".//a:blip")[0]
    ext = etree.SubElement(etree.SubElement(blip, "{http://schemas.openxmlformats.org/drawingml/2006/main}extLst"),
                           "{http://schemas.openxmlformats.org/drawingml/2006/main}ext")
    ext.set("uri", "{96DAC541-7B7A-43D3-8B79-37D633B846F1}")
    etree.SubElement(ext, "{%s}svgBlip" % BD.NS_SVG, nsmap={"asvg": BD.NS_SVG}).set(
        "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed", rid)
    pfad = str(tmp_path / "word.docx")
    d.save(pfad)
    doc, *_ = docx_leser.read_docx(pfad)
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QTextDocument
    namen = [k for k in ("docx-bild-1",) if doc.resource(QTextDocument.ImageResource, QUrl(k)) is not None]
    assert namen
    img = doc.resource(QTextDocument.ImageResource, QUrl(namen[0]))
    assert BD.ist_svg(img) and BD.quelle_zu(img).daten == SVG and BD.quelle_zu(img).ersatz_png == png


def test_svg_odt_zwei_bilder_und_zurueck(fenster, tmp_path):
    from lunivo_writer.dienste import odt_leser, odt_schreiber
    ed = fenster.current_editor()
    _svg_einfuegen(ed, tmp_path)
    daten = odt_schreiber.odt_daten(ed.document(), ed.page, {})[0]
    with zipfile.ZipFile(io.BytesIO(daten)) as z:
        inhalt = z.read("content.xml").decode()
        assert inhalt.index(".svg") < inhalt.index(".png") and inhalt.count("<draw:image ") == 2
        assert 'media-type="image/svg+xml"' in z.read("META-INF/manifest.xml").decode()
    pfad = tmp_path / "s.odt"
    pfad.write_bytes(daten)
    doc, *_ = odt_leser.read_odt(str(pfad))
    gelesen = list(_frei_bilder(type("E", (), {"document": lambda self: doc})()))
    assert len(gelesen) == 1 and BD.ist_svg(gelesen[0][1]) and BD.quelle_zu(gelesen[0][1]).daten == SVG


def test_svg_im_pdf_bleibt_vektor(fenster, tmp_path):
    import pypdf
    from lunivo_writer.editor.seite import seiten_aufteilung as SA
    ed = fenster.current_editor()
    _svg_einfuegen(ed, tmp_path)
    pdf = str(tmp_path / "s.pdf")
    SA.export_pdf(pdf, ed.document(), ed.page)
    seite = pypdf.PdfReader(pdf).pages[0]
    inhalt = seite.get_contents().get_data()
    assert len(list(seite.images)) == 0 and b"/Im" not in inhalt                 # kein Rasterbild
    assert b" f" in inhalt or b"\nf" in inhalt                                    # gefüllte Vektorpfade (Rechteck und Kreis)


# ---- Phase 3: dekorative Bilder ---------------------------------------------------------------------------------------------------
def _dekor_docx(ed, pfad):
    from lunivo_writer.dienste import docx_schreiber
    docx_schreiber.write_docx(pfad, ed.document(), ed.page, {})
    with zipfile.ZipFile(pfad) as z:
        return z.read("word/document.xml").decode()


def test_dekorativ_docx_und_vorlesen_frei(fenster, tmp_path):
    from lunivo_writer.dienste import docx_leser, vorlesen
    from lunivo_writer.editor.objekte import bildlayout as BL
    ed = fenster.current_editor()
    _svg_einfuegen(ed, tmp_path)
    ed.textCursor().insertText("Hallo Welt")
    BL.frei_aendern(ed, BL.ziel(ed), alt="Ein rotes Feld")
    assert "Bild: Ein rotes Feld." in vorlesen.vorlesetext(ed.document())          # mit Beschreibung: angesagt
    xml = _dekor_docx(ed, str(tmp_path / "a.docx"))
    assert 'descr="Ein rotes Feld"' in xml and "adec:decorative" not in xml
    BL.frei_aendern(ed, BL.ziel(ed), dekor=True)
    pfad = str(tmp_path / "d.docx")
    xml = _dekor_docx(ed, pfad)
    assert 'uri="{C183D7F6-B498-43B3-948B-1728B52AA6E4}"' in xml and 'adec:decorative' in xml and 'val="1"' in xml and 'descr="Ein rotes Feld"' not in xml
    text = vorlesen.vorlesetext(ed.document())
    assert "Bild" not in text and "Hallo Welt" in text                              # dekorativ: übersprungen
    doc, *_ = docx_leser.read_docx(pfad)
    assert any(a.get("dekor") for a, _b in _frei_bilder(type("E", (), {"document": lambda self: doc})()))


def test_dekorativ_im_text_und_barrierefreiheit(fenster, tmp_path):
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QImage, QTextDocument, QTextImageFormat
    from lunivo_writer.dienste import docx_leser, vorlesen
    from lunivo_writer.dienste.docx_teile.lesen_gemeinsam import STYLE_PROP
    from lunivo_writer.editor.dokument.zusatz import P_DEKORATIV
    ed = fenster.current_editor()
    img = QImage(10, 10, QImage.Format_RGB32); img.fill(0)
    ed.document().addResource(QTextDocument.ImageResource, QUrl("t"), img)
    f = QTextImageFormat(); f.setName("t"); f.setWidth(10); f.setHeight(10); f.setProperty(STYLE_PROP + 1, "Logo")
    ed.textCursor().insertImage(f)
    assert "Bild: Logo." in vorlesen.vorlesetext(ed.document())
    from PySide6.QtGui import QTextCursor
    c = ed.textCursor(); c.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor); ed.setTextCursor(c)
    ed.bild_setzen(dekor=True)
    assert "Bild" not in vorlesen.vorlesetext(ed.document())
    xml = _dekor_docx(ed, str(tmp_path / "t.docx"))
    assert 'adec:decorative' in xml and 'val="1"' in xml and 'descr="Logo"' not in xml
    doc, *_ = docx_leser.read_docx(str(tmp_path / "t.docx"))
    from lunivo_writer.editor.text.fragmente import absatz_fragmente
    b = doc.firstBlock(); dek = []
    while b.isValid():
        dek += [fr.charFormat().toImageFormat().hasProperty(P_DEKORATIV) for fr in absatz_fragmente(b) if fr.charFormat().isImageFormat()]
        b = b.next()
    assert dek == [True]


def test_alternativtext_seitenleiste_dekorativ_sperrt_feld(fenster, tmp_path):
    from lunivo_writer.editor.objekte import bildlayout as BL
    ed = fenster.current_editor()
    _svg_einfuegen(ed, tmp_path)
    fenster.befehle.tun("bildAltText")
    panel = fenster.sidebar.format_panel("bildalt")
    assert panel is not None and panel.minimumSizeHint().width() <= 300                 # passt in die Seitenleiste
    panel.abschnitt.text_feld.setPlainText("Rotes Feld")
    panel.abschnitt._timer.timeout.emit()
    assert BL.ziel(ed)[2]["alt"] == "Rotes Feld" and panel.abschnitt.text_feld.isEnabled()
    panel.abschnitt.dekorativ.setChecked(True)
    assert BL.ziel(ed)[2]["dekor"] is True and not panel.abschnitt.text_feld.isEnabled()


# ---- Phase 4: EMF/WMF ----------------------------------------------------------------------------------------------------------
import struct


def _emf(rot=True, vorher: bytes = b"") -> bytes:
    """Ein kleines EMF von Hand: rotes Rechteck über die ganze Fläche (Geräteeinheiten 0..100 × 0..50, Rahmen 25,4 × 12,7 mm = 96 × 48 px)."""
    def satz(typ, *nutz):
        daten = b"".join(nutz)
        return struct.pack("<II", typ, 8 + len(daten)) + daten
    teile = [satz(39, struct.pack("<IIII", 1, 0, 0x0000FF if rot else 0xFF0000, 0)),     # Pinsel 1: Farbe 0x00BBGGRR
             satz(37, struct.pack("<I", 1)), vorher, satz(43, struct.pack("<iiii", 0, 0, 100, 50)), satz(14, struct.pack("<III", 0, 16, 20))]
    koerper = b"".join(teile)
    kopf = struct.pack("<II4i4i", 1, 88, 0, 0, 100, 50, 0, 0, 2540, 1270) + b" EMF" + struct.pack("<IIIHHIIIii", 0x10000, 88 + len(koerper), len(teile) + 1, 2, 0, 0, 0, 0, 100, 50)
    kopf += struct.pack("<ii", 25, 13)
    return kopf + koerper


def _emf_datei(tmp_path, name="m.emf", **kw):
    p = tmp_path / name
    p.write_bytes(_emf(**kw))
    return str(p)


def test_emf_lesen_vektor_und_startgroesse(tmp_path):
    from PySide6.QtCore import QRectF
    from PySide6.QtGui import QPainter
    img = BD.bild_aus_datei(_emf_datei(tmp_path))
    assert not img.isNull() and BD.quelle_zu(img).format == "emf" and BD.anzeigegroesse(img) == (96.0, 48.0)
    assert img.pixelColor(img.width() // 2, img.height() // 2).red() > 200
    gross = QImage(960, 480, QImage.Format_ARGB32_Premultiplied); gross.fill(0)          # zehnfach: bleibt scharf, weil neu gezeichnet
    p = QPainter(gross); BD.zeichnen(p, QRectF(100, 100, 400, 200), img); p.end()
    assert gross.pixelColor(110, 110).red() > 200 and gross.pixelColor(90, 110).alpha() == 0 and gross.pixelColor(495, 295).red() > 200 and gross.pixelColor(505, 305).alpha() == 0


def test_emf_defekter_befehl_wird_uebersprungen(tmp_path):
    kaputt = struct.pack("<II", 54, 8)                 # LINETO ohne Koordinaten
    img = BD.bild_aus_datei(_emf_datei(tmp_path, vorher=kaputt))
    assert img.pixelColor(img.width() // 2, img.height() // 2).red() > 200       # das Rechteck dahinter ist trotzdem da


def test_emf_beschaedigt_nie_absturz(tmp_path):
    import random
    from lunivo_writer.dienste import vektor_bilder as V
    gut = _emf()
    zufall = random.Random(7)
    for _ in range(150):
        b = bytearray(gut)
        for _k in range(zufall.randint(1, 12)):
            b[zufall.randrange(len(b))] = zufall.randrange(256)
        V.bild_lesen(bytes(b[: zufall.randint(40, len(b))]))                    # darf Bild oder leer liefern, aber nicht abstürzen
    riesig = bytearray(gut); struct.pack_into("<4i", riesig, 24, 0, 0, 2_000_000_000, 2_000_000_000)
    img = V.bild_lesen(bytes(riesig))
    assert img.isNull() or max(img.width(), img.height()) <= V.MAX_SEITE_PX


def test_emf_original_in_docx_odt_rtf_und_zurueck(fenster, tmp_path):
    from lunivo_writer.dienste import docx_leser, docx_schreiber, odt_schreiber, rtf_schreiber
    ed = fenster.current_editor()
    assert ed.insert_image(_emf_datei(tmp_path))
    original = _emf()
    pfad = str(tmp_path / "m.docx")
    docx_schreiber.write_docx(pfad, ed.document(), ed.page, {})
    with zipfile.ZipFile(pfad) as z:
        medien = [n for n in z.namelist() if n.startswith("word/media/")]
        assert medien == ["word/media/metafile1.emf"] and z.read(medien[0]) == original
        assert "image/x-emf" in z.read("[Content_Types].xml").decode()
    doc, *_ = docx_leser.read_docx(pfad)
    gelesen = list(_frei_bilder(type("E", (), {"document": lambda self: doc})()))
    assert len(gelesen) == 1 and BD.quelle_zu(gelesen[0][1]).format == "emf" and BD.quelle_zu(gelesen[0][1]).daten == original
    with zipfile.ZipFile(io.BytesIO(odt_schreiber.odt_daten(ed.document(), ed.page, {})[0])) as z:
        assert [z.read(n) for n in z.namelist() if n.startswith("Pictures/")] == [original]
        assert 'media-type="image/x-emf"' in z.read("META-INF/manifest.xml").decode()
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QTextDocument, QTextImageFormat
    ed.document().addResource(QTextDocument.ImageResource, QUrl("im-text"), BD.bild_aus_datei(_emf_datei(tmp_path)))
    f = QTextImageFormat(); f.setName("im-text"); f.setWidth(96); f.setHeight(48)
    ed.textCursor().insertImage(f)
    assert b"\\emfblip" in rtf_schreiber.rtf_daten(ed.document(), ed.page, {})[0]


def test_emz_gepackt_wird_gelesen(tmp_path):
    import gzip
    p = tmp_path / "m.emz"
    p.write_bytes(gzip.compress(_emf()))
    img = BD.bild_aus_datei(str(p))
    assert BD.quelle_zu(img).format == "emf" and BD.quelle_zu(img).daten == _emf()


def test_wmf_lesen_als_vektor(tmp_path):
    def satz(fn, *nutz):
        daten = b"".join(nutz)
        return struct.pack("<IH", 3 + len(daten) // 2, fn) + daten
    koerper = (satz(0x02FC, struct.pack("<HIH", 0, 0x0000FF, 0)) + satz(0x012D, struct.pack("<H", 0))
               + satz(0x041B, struct.pack("<hhhh", 50, 100, 0, 0)) + satz(0))
    kopf = struct.pack("<HHHIHIH", 1, 9, 0x300, 9 + len(koerper) // 2, 1, 10, 0)
    platz = struct.pack("<IHhhhhHIH", 0x9AC6CDD7, 0, 0, 0, 100, 50, 100, 0, 0)         # 100 Einheiten je Zoll: 96 × 48 px
    blob = platz + kopf + koerper
    p = tmp_path / "m.wmf"; p.write_bytes(blob)
    img = BD.bild_aus_datei(str(p))
    assert not img.isNull() and BD.quelle_zu(img).format == "wmf" and BD.anzeigegroesse(img) == pytest.approx((96.0, 48.0), abs=1)
    assert img.pixelColor(img.width() // 2, img.height() // 2).red() > 200


# ---- Echte Dateien, von LibreOffice geschrieben (tests/editor/daten; erzeugt aus eigenen Testbildern, siehe daten/LIESMICH.md) ----------
DATEN = os.path.join(os.path.dirname(__file__), "daten")


def _ist_rot_blau(img):
    """Rotes Feld mit blauem Kreis in der Mitte, Ecke rot (wie das Quell-SVG)."""
    mitte, ecke = img.pixelColor(img.width() // 2, img.height() // 2), img.pixelColor(4, 4)
    return mitte.blue() > 200 and mitte.red() < 60 and ecke.red() > 200 and ecke.blue() < 60


@pytest.mark.parametrize("name,format", [("libreoffice.emf", "emf"), ("libreoffice.wmf", "wmf")])
def test_echtes_metafile_von_libreoffice(name, format):
    img = BD.bild_aus_datei(os.path.join(DATEN, name))
    assert BD.quelle_zu(img).format == format and _ist_rot_blau(img)
    from PySide6.QtCore import QRectF
    from PySide6.QtGui import QPainter
    gross = QImage(1000, 500, QImage.Format_ARGB32_Premultiplied); gross.fill(0)
    p = QPainter(gross); BD.zeichnen(p, QRectF(0, 0, 1000, 500), img); p.end()
    assert _ist_rot_blau(gross)                                                  # Vektor in anderer Größe


def test_echte_libreoffice_dateien_svg_und_dekorativ():
    from lunivo_writer.dienste import docx_leser, odt_leser
    from lunivo_writer.dienste.docx_teile.lesen_gemeinsam import STYLE_PROP  # noqa: F401
    from lunivo_writer.editor.dokument.zusatz import P_DEKORATIV
    from lunivo_writer.editor.text.fragmente import absatz_fragmente
    leer = type("E", (), {})
    for datei, lesen in (("libreoffice_svg.odt", odt_leser.read_odt), ("libreoffice_svg.docx", docx_leser.read_docx)):
        doc = lesen(os.path.join(DATEN, datei))[0]
        bilder = list(_frei_bilder(type("E", (), {"document": lambda self, d=doc: d})()))
        assert len(bilder) == 1 and BD.ist_svg(bilder[0][1]), datei
    doc = odt_leser.read_odt(os.path.join(DATEN, "libreoffice_dekorativ.odt"))[0]
    b, dek = doc.firstBlock(), []
    while b.isValid():
        dek += [f.charFormat().toImageFormat().hasProperty(P_DEKORATIV) for f in absatz_fragmente(b) if f.charFormat().isImageFormat()]
        b = b.next()
    assert dek == [True]                                                         # loext:decorative von LibreOffice


def test_odt_dekorativ_fuer_libreoffice(fenster, tmp_path):
    """Das Schreiben folgt LibreOffice: ``loext:decorative="true"`` an der Rahmenvorlage, im Text und bei freien Bildern."""
    from lunivo_writer.dienste import odt_schreiber
    from lunivo_writer.editor.objekte import bildlayout as BL
    ed = fenster.current_editor()
    _svg_einfuegen(ed, tmp_path)
    BL.frei_aendern(ed, BL.ziel(ed), dekor=True)
    inhalt = zipfile.ZipFile(io.BytesIO(odt_schreiber.odt_daten(ed.document(), ed.page, {})[0])).read("content.xml").decode()
    assert 'loext:decorative="true"' in inhalt and "xmlns:loext=" in inhalt


# ---- Rest: EXIF-Drehung, WebP/TIFF/GIF, RTF-WMF, Diagramm dekorativ ----------------------------------------------------------------
def _jpeg_mit_exif(drehung: int) -> bytes:
    img = QImage(60, 20, QImage.Format_RGB32)
    img.fill(QColor("red"))
    puffer = io.BytesIO()
    from PySide6.QtCore import QBuffer, QIODevice
    b = QBuffer(); b.open(QIODevice.WriteOnly); img.save(b, "JPEG", 90)
    jpeg = bytes(b.data())
    tiff = b"MM\x00*\x00\x00\x00\x08" + struct.pack(">H", 1) + struct.pack(">HHIHH", 0x0112, 3, 1, drehung, 0) + b"\x00\x00\x00\x00"
    app1 = b"Exif\x00\x00" + tiff
    return jpeg[:2] + b"\xff\xe1" + struct.pack(">H", len(app1) + 2) + app1 + jpeg[2:]


def test_exif_drehung_wird_angewendet_original_bleibt():
    from lunivo_writer.editor.objekte.freie_bilder import bild_aus_daten
    jpeg = _jpeg_mit_exif(6)                                   # 6 = 90° im Uhrzeigersinn: aus 60 × 20 wird 20 × 60
    img = bild_aus_daten(jpeg)
    assert (img.width(), img.height()) == (20, 60) and BD.quelle_zu(img).daten == jpeg
    assert bild_aus_daten(_jpeg_mit_exif(1)).size().toTuple() == (60, 20)


@pytest.mark.parametrize("format", ["webp", "tiff", "gif", "bmp"])
def test_weitere_rasterformate_bleiben_original(fenster, tmp_path, format):
    from PySide6.QtCore import QBuffer, QIODevice
    from lunivo_writer.dienste import docx_schreiber, odt_schreiber
    ed = fenster.current_editor()
    img = QImage(30, 20, QImage.Format_RGB32); img.fill(QColor("green"))
    b = QBuffer(); b.open(QIODevice.WriteOnly)
    if format == "gif":                                         # Qt schreibt kein GIF: ein winziges von Hand
        original = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
    elif not img.save(b, format.upper()):
        pytest.skip(f"Qt schreibt {format} hier nicht")
    else:
        original = bytes(b.data())
    p = tmp_path / f"b.{format}"; p.write_bytes(original)
    assert ed.insert_image(str(p))
    assert BD.format_erkennen(original) == BD.quelle_zu(BD.bild_aus_datei(str(p))).format
    with zipfile.ZipFile(io.BytesIO(odt_schreiber.odt_daten(ed.document(), ed.page, {})[0])) as z:
        assert [z.read(n) for n in z.namelist() if n.startswith("Pictures/")] == [original]
    with zipfile.ZipFile(io.BytesIO(docx_schreiber.docx_daten(ed.document(), ed.page, {})[0])) as z:
        medien = [z.read(n) for n in z.namelist() if n.startswith("word/media/")]
    assert medien == ([original] if format != "webp" else medien) and (format != "webp" or medien[0].startswith(b"\x89PNG"))


def test_wmf_in_rtf_hin_und_zurueck(fenster, tmp_path):
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QTextDocument, QTextImageFormat
    from lunivo_writer.dienste import rtf_schreiber
    from lunivo_writer.dienste.rtf.leser import read_rtf
    ed = fenster.current_editor()
    img = BD.bild_aus_datei(os.path.join(DATEN, "libreoffice.wmf"))
    ed.document().addResource(QTextDocument.ImageResource, QUrl("w"), img)
    f = QTextImageFormat(); f.setName("w"); f.setWidth(189); f.setHeight(89)
    ed.textCursor().insertImage(f)
    daten = rtf_schreiber.rtf_daten(ed.document(), ed.page, {})[0]
    assert b"\\wmetafile8" in daten
    pfad = tmp_path / "w.rtf"; pfad.write_bytes(daten)
    from lunivo_writer.editor.text.fragmente import absatz_fragmente
    doc = read_rtf(str(pfad))[0]
    b, gelesen = doc.firstBlock(), []
    while b.isValid():
        gelesen += [doc.resource(QTextDocument.ImageResource, QUrl(fr.charFormat().toImageFormat().name())) for fr in absatz_fragmente(b) if fr.charFormat().isImageFormat()]
        b = b.next()
    assert len(gelesen) == 1 and BD.quelle_zu(gelesen[0]).format == "wmf" and _ist_rot_blau(gelesen[0])


def test_diagramm_dekorativ_ohne_beschreibung(fenster, tmp_path):
    from lunivo_writer.dienste import docx_schreiber
    from lunivo_writer.editor.objekte import bildlayout as BL
    from lunivo_writer.editor.objekte import frei_objekt as FO
    ed = fenster.current_editor()
    FO.einfuegen(ed, "diagramm", {"art": "saeule_gruppiert", "titel": "T", "kategorien": ["a", "b"], "reihen": {"R": [1, 2]}, "alt_beschreibung": "Säulen"}, 300, 200)
    assert 'descr="Säulen"' in _dekor_docx(ed, str(tmp_path / "x.docx"))
    BL.frei_aendern(ed, BL.ziel(ed), dekor=True)
    xml = _dekor_docx(ed, str(tmp_path / "y.docx"))
    assert "adec:decorative" in xml and 'descr="Säulen"' not in xml


# ---- Fund an echten Dateien der Prüfdatenbank (~/Lunivo-Testdateien) ---------------------------------------------------------------------
def test_wmf_mit_negativer_fensterausdehnung_wird_gespiegelt(tmp_path):
    """Office schreibt SETWINDOWEXT mit negativer Höhe (y nach oben) und die Angaben zweimal; die letzte gilt, die Zeichnung steht nicht auf dem Kopf."""
    def satz(fn, *nutz):
        daten = b"".join(nutz)
        return struct.pack("<IH", 3 + len(daten) // 2, fn) + daten
    koerper = (satz(0x020B, struct.pack("<hh", 0, 0)) + satz(0x020C, struct.pack("<hh", 100, 100))            # y, x
               + satz(0x020B, struct.pack("<hh", 100, 0)) + satz(0x020C, struct.pack("<hh", -100, 100))        # y nach oben: Ursprung unten
               + satz(0x02FC, struct.pack("<HIH", 0, 0x0000FF, 0)) + satz(0x012D, struct.pack("<H", 0))
               + satz(0x041B, struct.pack("<hhhh", 20, 100, 0, 0)) + satz(0))                                  # rotes Band an der Unterkante (y 0..20)
    kopf = struct.pack("<HHHIHIH", 1, 9, 0x300, 9 + len(koerper) // 2, 1, 10, 0)
    platz = struct.pack("<IHhhhhHIH", 0x9AC6CDD7, 0, 0, 0, 100, 100, 100, 0, 0)
    p = tmp_path / "f.wmf"; p.write_bytes(platz + kopf + koerper)
    img = BD.bild_aus_datei(str(p))
    assert img.pixelColor(img.width() // 2, img.height() - 3).red() > 200 and img.pixelColor(img.width() // 2, 3).alpha() == 0


MS_VORLAGE = os.path.expanduser("~/Lunivo-Testdateien/11_Microsoft_Originale/template example.docx")


@pytest.mark.skipif(not os.path.isfile(MS_VORLAGE), reason="Prüfdatenbank nicht vorhanden")
def test_microsoft_vorlage_gruppe_dekorativ_hin_und_zurueck(app):
    """Eine Originaldatei von Microsoft: die Gruppe ist dekorativ markiert; alle ihre Teile gelten so und die Markierung wird zurückgeschrieben."""
    from lunivo_writer.dienste import docx_leser, docx_schreiber, vorlesen
    from lunivo_writer.editor.objekte import freie_bilder as FB
    from lunivo_writer.modelle.seite import PageSettings
    doc = docx_leser.read_docx(MS_VORLAGE)[0]
    angaben, b = [], doc.firstBlock()
    while b.isValid():
        angaben += FB.aus_absatz(b.blockFormat()); b = b.next()
    dekor = [a for a in angaben if a.get("dekor")]
    assert len(dekor) == 7                                                   # die 7 Teile der markierten Gruppe (die Textfelder in der Zeile sind es nicht)
    xml = zipfile.ZipFile(io.BytesIO(docx_schreiber.docx_daten(doc, PageSettings(), {})[0])).read("word/document.xml").decode()
    assert xml.count("adec:decorative") >= len(dekor)                   # dazu der durchsichtige Platzhalter einer Gruppe in der Zeile (ebenfalls dekorativ)
    assert "Bild" not in vorlesen.vorlesetext(doc)


# ---- Fund an den LibreOffice-Testdokumenten der Prüfdatenbank (~/Lunivo-Testdateien/13_LibreOffice_Testdokumente) ----------------------
LO_DATEN = os.path.expanduser("~/Lunivo-Testdateien/13_LibreOffice_Testdokumente")


@pytest.mark.skipif(not os.path.isdir(LO_DATEN), reason="Prüfdatenbank nicht vorhanden")
@pytest.mark.parametrize("datei,format", [("ooxmlimport/tdf115094.docx", "tiff"), ("ooxmlexport/tdf170516_drawingBeforePlainText.docx", "svg")])
def test_bild_im_schwebenden_rahmen_einer_zelle_bleibt_erhalten(app, datei, format):
    """Zwei Dateien mit Bild im Textumfluss-Rahmen in einer Tabelle: Lesen stürzte ab (Layout beim Lesen schwebender Tabellen), das Speichern verlor das Bild."""
    from lunivo_writer.dienste import docx_leser, docx_schreiber
    from lunivo_writer.modelle.seite import PageSettings
    doc = docx_leser.read_docx(os.path.join(LO_DATEN, datei))[0]
    z = zipfile.ZipFile(io.BytesIO(docx_schreiber.docx_daten(doc, PageSettings(), {})[0]))
    medien = [n for n in z.namelist() if n.startswith("word/media/")]
    assert any(n.endswith(("." + format, ".tiff") if format == "tiff" else ".svg") for n in medien), medien
