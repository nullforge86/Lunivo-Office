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










# ---- Phase 3: dekorative Bilder ---------------------------------------------------------------------------------------------------
def _dekor_docx(ed, pfad):
    from lunivo_writer.dienste import docx_schreiber
    docx_schreiber.write_docx(pfad, ed.document(), ed.page, {})
    with zipfile.ZipFile(pfad) as z:
        return z.read("word/document.xml").decode()








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
