"""Bilder und Formen im Dokumentenmodell ohne Qt: verlustfreie Umwandlung, Lage auf dem Blatt, Bildformate, Zeichnen über das Backend."""
import struct

import pytest

from lunivo_writer.core.document import bildformat as BF
from lunivo_writer.core.document.objekte import Anchor, FillStyle, ImageObject, ShapeObject, VectorPath
from lunivo_writer.core.geometry import Rect
from lunivo_writer.core.layout.objekte import objekt_rechteck
from lunivo_writer.core.rendering.objekte import fuellstil, heller

ANGABE = {"b": 120.0, "h": 80.0, "bh": "seite", "xh": 10.0, "ah": "center", "bv": "rand", "yv": 5.0, "av": "bottom", "hinter": True, "ellipse": True, "dreh": 15.0,
          "rand": {"b": 2.0, "farbe": "#ff0000", "art": "gestrichelt"}, "fuell": {"art": "verlauf", "farbe": "#00ff00"}, "zu": [0.1, 0, 0, 0.2], "maske": "stern",
          "fx": {"weich": {"radius": 3}}, "unbekannt": 7, "n": "frei-1", "alt": "Ein Bild"}


def test_bildobjekt_verlustfrei():
    o = ImageObject.aus_angabe(ANGABE, b"daten")
    assert o.zu_angabe() == ANGABE and o.transform.rotation == 15.0 and o.wrap.behind and o.stroke.dash == "gestrichelt"
    assert ImageObject.aus_angabe({"b": 1, "h": 2}).zu_angabe() == {"b": 1.0, "h": 2.0, "bh": "spalte", "xh": 0.0, "bv": "absatz", "yv": 0.0}      # Standardwerte kommen hinzu


def test_formobjekt_verlustfrei():
    p = {"form": "ellipse", "breite": 50.0, "hoehe": 30.0, "fuell": "#123456", "linie": "#000000", "strich": 2.0, "text": "Hi", "adj": [0.3], "punkte": [[0, 0], [1, 1]], "x": 1}
    s = ShapeObject.aus_parametern(p)
    assert s.zu_parametern() == p and s.path == VectorPath.polygon([(0, 0), (1, 1)])
    assert VectorPath.rounded_rect(0, 0, 10, 10, 2).ops[0][0] == "M" and VectorPath.arrow(0, 0, 10, 0).ops[0] == ("M", 0, 0)


def test_lage_auf_dem_blatt():
    r = objekt_rechteck(Anchor("seite", 0, "center", "seite", 0, "bottom"), 100, 50, 800, 1000, 100, 100, 600, 800)
    assert r == Rect(350, 950, 100, 50)
    r = objekt_rechteck(Anchor("rand", 0, "inside", "absatz", 7), 100, 50, 800, 1000, 100, 100, 600, 800, absatz_y=300, seite=2)
    assert r == Rect(600, 307, 100, 50)                                                        # gerade Seite: innen = rechts
    assert objekt_rechteck(Anchor("spalte", 12, "", "absatz", 3), 10, 10, 800, 1000, 100, 100, 600, 800, 400, spalte_x=350) == Rect(362, 403, 10, 10)


def _riff(typ: bytes, kopf: bytes) -> bytes:
    return b"RIFF" + b"\0\0\0\0" + b"WEBP" + typ + kopf


def test_bildformate_und_masse():
    assert BF.masse(b"\x89PNG\r\n\x1a\n" + b"\0\0\0\rIHDR" + struct.pack(">II", 37, 21)) == (37, 21)
    assert BF.masse(b"GIF89a" + struct.pack("<HH", 14, 9)) == (14, 9) and BF.format_erkennen(b"GIF89a") == "gif"
    bmp = b"BM" + b"\0" * 16 + struct.pack("<ii", 33, -22)
    assert BF.masse(bmp) == (33, 22)
    assert BF.masse(_riff(b"VP8X", b"\0" * 8 + (99).to_bytes(3, "little") + (49).to_bytes(3, "little"))) == (100, 50)
    assert BF.masse(b'<svg width="10mm" height="5mm"/>') == pytest.approx((37.795, 18.898), abs=0.01)
    assert BF.masse(b"nichts") is None and BF.format_erkennen(b"nichts") is None
    assert BF.seitenverhaeltnis(b"GIF89a" + struct.pack("<HH", 20, 10)) == 2.0


def test_zeichnen_ueber_backend():
    assert heller((0, 128, 0, 255)) == (0, 205, 0, 255)
    o = ImageObject.aus_angabe({"b": 10, "h": 10, "fuell": {"art": "muster", "key": "x"}})
    assert type(fuellstil(o.fill, Rect(0, 0, 1, 1)).fill).__name__ == "PatternFill" and fuellstil(FillStyle("bild"), Rect(0, 0, 1, 1)) is None
    assert type(fuellstil(FillStyle("bild"), Rect(0, 0, 1, 1), b"x").fill).__name__ == "ImageFill"
    assert fuellstil(FillStyle("farbe", "#112233"), Rect(0, 0, 1, 1)).color == (0x11, 0x22, 0x33, 255)


def test_backend_zeichnet_formen_und_bilder(app):
    from PySide6 import QtGui as gui
    from lunivo_writer.adapter.qt.pfad import pfad_zu_vektor, vektor_zu_pfad
    from lunivo_writer.adapter.qt.rendering import QtRenderBackend
    from lunivo_writer.core.document.objekte import FillStyle, StrokeStyle
    from lunivo_writer.core.rendering.objekte import zeichne_bild, zeichne_form
    img = gui.QImage(120, 80, gui.QImage.Format_RGB32)
    img.fill(gui.QColor("white"))
    p = gui.QPainter(img)
    rb = QtRenderBackend(p)
    assert zeichne_form(rb, ShapeObject("ellipse", 60, 40, FillStyle("farbe", "#ff0000"), StrokeStyle("#000000", 2.0)), Rect(10, 10, 60, 40))
    assert not zeichne_form(rb, ShapeObject("unbekannt", 10, 10), Rect(0, 0, 10, 10))
    zeichne_bild(rb, ImageObject(30, 20, None, stroke=StrokeStyle("#0000ff", 2.0)), Rect(80, 50, 30, 20))                       # fehlendes Bild: Platzhalter
    p.end()
    assert img.pixelColor(40, 30).name() == "#ff0000" and img.pixelColor(2, 2).name() == "#ffffff"
    assert img.pixelColor(95, 60).name() != "#ffffff"                                                                           # Platzhalter gezeichnet
    v = pfad_zu_vektor(vektor_zu_pfad(VectorPath.rounded_rect(0, 0, 40, 20, 5)))
    assert v.ops[0] == ("M", 5.0, 0.0) and any(o[0] == "C" for o in v.ops)


def test_frei_positioniertes_bild_wandert_mit_dem_modell(app):
    """Ein frei positioniertes Bild (Name im Absatz, Bild im Ressourcenspeicher) geht über das Modell nicht verloren."""
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QColor, QImage, QTextCursor, QTextDocument
    from lunivo_writer.adapter.qt.dokument import document_from_qt, document_to_qt
    from lunivo_writer.editor.objekte import freie_bilder as FB
    d = QTextDocument()
    d.setPlainText("Hallo")
    img = QImage(40, 30, QImage.Format_RGB32)
    img.fill(QColor("red"))
    name = FB.neuer_name(d)
    d.addResource(QTextDocument.ImageResource, QUrl(name), img)
    FB.an_absatz(QTextCursor(d.firstBlock()), {"n": name, "b": 40.0, "h": 30.0, "bh": "seite", "xh": 1.0, "bv": "seite", "yv": 2.0})
    modell = document_from_qt(d)
    assert name in modell.media and modell.media[name].raster_png
    neu = document_to_qt(modell)
    assert FB.bild_im_dokument(neu, name) is not None and FB.aus_absatz(neu.firstBlock().blockFormat())[0]["n"] == name
