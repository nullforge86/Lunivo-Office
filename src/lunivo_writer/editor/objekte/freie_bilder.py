"""Frei positionierte Bilder: Bilder, die nicht im Text stehen, sondern an einer Stelle des Blattes (DOCX ``wp:anchor`` ohne Umbruch).

Sie kommen an zwei Orten vor:

* **im Text** — an einem Absatz verankert. Die Angaben stehen als JSON-Liste in der Absatz-Eigenschaft ``B_BILDANKER``
  (sie wandern mit dem Absatz, auch beim Kopieren und in die Kopie fürs Drucken); die Bilddaten liegen als Ressource
  ``frei-<n>`` im Dokument.
* **in Kopf- und Fußzeilen** — ``PageSettings.bilder``; jede Angabe trägt ihr Bild selbst (``bild``) und ``ort``:
  ``kopf`` | ``fuss`` | ``kopf1`` | ``fuss1`` (letztere nur auf der ersten Seite, wenn „Erste Seite anders“ gilt).

Eine Angabe (alle Maße in Bildpunkten, 96 dpi):
``b``, ``h`` Größe · ``bh`` Bezug waagerecht (``seite`` | ``rand`` | ``spalte``), ``xh`` Versatz, ``ah`` Ausrichtung (``left`` | ``center`` ·
``right`` | ``inside`` | ``outside`` oder leer) · ``bv`` Bezug senkrecht (``seite`` | ``rand`` | ``absatz``), ``yv``, ``av`` (``top`` | ``center`` |
``bottom``) · ``hinter`` hinter dem Text · ``ellipse`` Bild in einer Ellipse beschnitten · ``zu`` Zuschnitt, ``maske`` Zuschneideform (``bildzuschnitt``).
Gezeichnet wird in Blattkoordinaten (Ursprung links oben); der Editor, der Druck, das PDF und die Vorschau benutzen dieselben Funktionen.
"""
from __future__ import annotations

import json

from PySide6.QtCore import QRectF, QUrl
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath

from lunivo_writer.adapter.qt.geometrie import rect_from_qt, rect_to_qt
from lunivo_writer.adapter.qt.rendering import QtRenderBackend
from lunivo_writer.core.document.objekte import Anchor, FillStyle, ImageObject, StrokeStyle, Transform
from lunivo_writer.core.geometry import Rect
from lunivo_writer.core.rendering.objekte import zeichne_bild
from lunivo_writer.core.layout.objekte import objekt_rechteck
from lunivo_writer.editor.objekte import bilddaten as BD

from lunivo_writer.kern.farben import Farbe
EMU_PX = 9525.0                                              # 1 px bei 96 dpi


def emu_zu_px(emu) -> float:
    try:
        return float(emu) / EMU_PX
    except (TypeError, ValueError):
        return 0.0


# ---- Bilddaten lesen (auch EMF mit eingebettetem Bild) ----------------------------------------------------------------------
MAX_BILDPUNKTE = 100_000_000          # größere Bilder aus fremden Dokumenten werden nicht dekodiert (Speicher: 4 Byte je Bildpunkt)


def _zu_gross(blob: bytes) -> bool:
    """Liest nur die Maße aus dem Bildkopf; Bilder über ``MAX_BILDPUNKTE`` werden abgelehnt, bevor Qt sie anlegt."""
    from PySide6.QtCore import QBuffer, QByteArray, QIODevice
    from PySide6.QtGui import QImageReader
    daten = QByteArray(blob)
    puffer = QBuffer(daten)
    puffer.open(QIODevice.ReadOnly)
    leser = QImageReader(puffer)
    groesse = leser.size()
    del leser                                                      # der Leser muss vor Puffer und Bytes enden (sonst Absturz bei TIFF)
    return groesse.isValid() and groesse.width() * groesse.height() > MAX_BILDPUNKTE


def bild_aus_daten(blob: bytes) -> QImage:
    """Ein Bild aus Dateidaten. Qt kennt kein EMF; viele DOCX-Bilder (eingescannte Unterschriften) sind aber EMF-Hüllen um ein Bitmap
    (Aufzeichnung ``EMR_STRETCHDIBITS``) — das Bitmap wird herausgeholt. Echte Vektorzeichnungen bleiben unlesbar (leeres Bild)."""
    img = QImage()
    if _zu_gross(blob):
        return img
    if BD.format_erkennen(blob) == "svg":
        return BD.bild_aus_svg(blob)                                  # Vektor: Rasterfassung als Anzeige, SVG als Quelle
    img = BD.mit_ausrichtung_lesen(blob)
    if not img.isNull():
        BD.merken(img, blob)
        return img
    import struct
    if len(blob) < 44 or struct.unpack_from("<I", blob, 0)[0] != 1 or blob[40:44] != b" EMF":
        return QImage()
    pos = 0
    while pos + 8 <= len(blob):
        typ, groesse = struct.unpack_from("<II", blob, pos)
        if groesse < 8:
            break
        if typ == 81 and pos + 80 <= len(blob):                      # EMR_STRETCHDIBITS
            off_bmi, cb_bmi, off_bits, cb_bits = struct.unpack_from("<IIII", blob, pos + 48)
            bmi = blob[pos + off_bmi: pos + off_bmi + cb_bmi]
            bits = blob[pos + off_bits: pos + off_bits + cb_bits]
            if bmi and bits:
                kopf = b"BM" + struct.pack("<IHHI", 14 + len(bmi) + len(bits), 0, 0, 14 + len(bmi))
                if img.loadFromData(kopf + bmi + bits, "BMP"):
                    BD.merken(img, blob, nur_raster=True)
                    return img
        pos += groesse
    return QImage()


# ---- Zweifarbig („Duoton“) ------------------------------------------------------------------------------------------------
SCHEMA = {"tx1": Farbe.SCHWARZ, "dk1": Farbe.SCHWARZ, "bg1": Farbe.WEISS, "lt1": Farbe.WEISS, "tx2": "#1f497d", "dk2": "#1f497d", "bg2": "#eeece1",
          "lt2": "#eeece1", "accent1": "#4f81bd", "accent2": "#c0504d", "accent3": "#9bbb59", "accent4": "#8064a2", "accent5": "#4bacc6",
          "accent6": "#f79646"}


def farbe_aus_element(el, ns) -> "QColor":
    """Eine DrawingML-Farbe (srgbClr, prstClr, schemeClr) mit lumMod, lumOff, satMod, tint und shade. ``ns``: Namensräume für XPath."""
    from PySide6.QtGui import QColor
    tag = el.tag.rsplit("}", 1)[-1]
    wert = el.get("val") or ""
    if tag == "srgbClr":
        c = QColor("#" + wert)
    elif tag == "prstClr":
        c = QColor({"black": Farbe.SCHWARZ, "white": Farbe.WEISS}.get(wert, "#808080"))
    else:
        c = QColor(SCHEMA.get(wert, "#808080"))
    for m in el:
        name = m.tag.rsplit("}", 1)[-1]
        try:
            v = int(m.get("val") or 0) / 100000.0
        except ValueError:
            continue
        h, sa, l, al = c.hslHueF(), c.hslSaturationF(), c.lightnessF(), c.alphaF()
        if name == "lumMod":
            l = min(1.0, l * v)
        elif name == "lumOff":
            l = min(1.0, max(0.0, l + v))
        elif name == "satMod":
            sa = min(1.0, sa * v)
        elif name in ("tint", "shade"):
            ziel = 1.0 if name == "tint" else 0.0
            c = QColor.fromRgbF(*[min(1.0, max(0.0, x * v + ziel * (1 - v))) for x in (c.redF(), c.greenF(), c.blueF())])
            continue
        else:
            continue
        c = QColor.fromHslF(max(0.0, h), sa, l, al)
    return c


def duoton(img: QImage, dunkel, hell) -> QImage:
    """Das Bild in zwei Farben: Schwarz wird ``dunkel``, Weiß wird ``hell``, dazwischen Verlauf (DrawingML ``a:duotone``). Durchsicht bleibt."""
    from PySide6.QtGui import QColor, qRgb
    grau = img.convertToFormat(QImage.Format_Grayscale8)
    w, h = grau.width(), grau.height()
    roh = QImage(bytes(grau.constBits()), w, h, grau.bytesPerLine(), QImage.Format_Indexed8).copy()
    tabelle = []
    for i in range(256):
        t = i / 255.0
        tabelle.append(qRgb(round(dunkel.red() + (hell.red() - dunkel.red()) * t), round(dunkel.green() + (hell.green() - dunkel.green()) * t),
                            round(dunkel.blue() + (hell.blue() - dunkel.blue()) * t)))
    roh.setColorTable(tabelle)
    aus = roh.convertToFormat(QImage.Format_ARGB32)
    if img.hasAlphaChannel():
        aus.setAlphaChannel(img.convertToFormat(QImage.Format_ARGB32).getAlphaChannel() if hasattr(QImage, "getAlphaChannel") else
                            img.convertToFormat(QImage.Format_Alpha8))
    return aus


# ---- Lage auf dem Blatt ---------------------------------------------------------------------------------------------------
def rechteck(a: dict, blatt_b: float, blatt_h: float, ml: float, mt: float, inhalt_b: float, inhalt_h: float, absatz_y: float = 0.0,
             spalte_x: float | None = None, seite: int = 1) -> QRectF:
    """Das Rechteck des Bildes auf dem Blatt. ``absatz_y``: oberer Rand des Absatzes (Blattkoordinate), ``spalte_x``: linker Rand der Spalte.
    Gerechnet wird im Layoutkern (``core/layout/objekte.py``)."""
    anker = Anchor(str(a.get("bh", "spalte")), float(a.get("xh", 0)), a.get("ah") or "", str(a.get("bv", "absatz")), float(a.get("yv", 0)), a.get("av") or "")
    return rect_to_qt(objekt_rechteck(anker, float(a.get("b", 0)), float(a.get("h", 0)), blatt_b, blatt_h, ml, mt, inhalt_b, inhalt_h, absatz_y, spalte_x, seite))


def fuell_pinsel(fuell: dict | None, r: QRectF, fuellbild: QImage | None = None):
    """Der Pinsel für die Füllung eines Bildes (hinter durchsichtigen Stellen): ``farbe``, ``verlauf``, ``graduell`` (zwei Farben), ``muster``,
    ``textur`` oder ``bild``. ``None``: keine Füllung."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QBrush, QColor, QLinearGradient
    if not fuell:
        return None
    art = fuell.get("art", "farbe")
    if art == "farbe":
        return QBrush(QColor(fuell["farbe"]))
    if art in ("verlauf", "graduell"):
        dunkel = QColor(fuell["farbe"]) if art == "verlauf" else QColor(fuell.get("dunkel", fuell.get("farbe")))
        hell = QColor(fuell["farbe"]).lighter(160) if art == "verlauf" else QColor(fuell.get("hell", Farbe.WEISS))
        g = QLinearGradient(r.topLeft(), r.bottomLeft()); g.setColorAt(0, hell); g.setColorAt(1, dunkel)
        return QBrush(g)
    if art == "muster":
        from lunivo_writer.editor.text import muster as M
        return M.pinsel(fuell.get("key", "rein"), fuell.get("farbe", Farbe.SCHWARZ), fuell.get("grund") or Farbe.WEISS)
    if art == "textur":
        from lunivo_writer.editor.text.textur import textur
        return QBrush(textur(fuell.get("key", "papier"), 64))
    if art == "bild" and fuellbild is not None and not fuellbild.isNull():
        return QBrush(fuellbild.scaled(int(max(1, r.width())), int(max(1, r.height()))))
    return QBrush(Qt.NoBrush)


def _stift(rand: dict):
    """Die Kontur eines Bildes als Stift (Stärke in Bildpunkten, Art wie bei den Linien)."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QPen
    from lunivo_writer.editor.objekte.linie import STILE
    pen = QPen(QColor(rand.get("farbe", Farbe.WEISS)), float(rand.get("b", 1.0)))
    strich = STILE.get(rand.get("art", "einfach"), STILE["einfach"])[1]
    if isinstance(strich, tuple):
        pen.setDashPattern(list(strich))
    else:
        pen.setStyle(strich)
    return pen


def _text_gerade(dreh: float, fx: dict | None) -> bool:
    """„Text nicht drehen“: Form und Füllung gedreht, der Text bleibt aufrecht."""
    return bool(dreh and ((fx or {}).get("drehung") or {}).get("text_gerade"))


_PNG_ABLAGE: dict = {}


def _png_daten(bild: QImage) -> bytes:
    """Die Bildpunkte als PNG für das Backend (kleine Ablage nach ``cacheKey``, damit nicht bei jedem Zeichnen neu kodiert wird)."""
    schluessel = bild.cacheKey()
    daten = _PNG_ABLAGE.get(schluessel)
    if daten is None:
        if len(_PNG_ABLAGE) >= 48:
            _PNG_ABLAGE.pop(next(iter(_PNG_ABLAGE)))
        daten = _PNG_ABLAGE[schluessel] = BD.png_bytes(bild)
    return daten


def _ueber_backend(p: QPainter, bild: QImage, r: QRectF, ellipse: bool, rand: dict | None, dreh: float, fuell: dict | None, fuellbild: QImage | None = None,
                   fx: dict | None = None) -> None:
    """Bild mit Füllung, Kontur, Drehung und Effekten über ``core.rendering`` zeichnen. Vektorbilder (SVG, EMF/WMF) gehen mit ihren Originalbytes an das Backend."""
    q = BD.quelle_zu(bild)
    daten = q.daten if q is not None and q.format in ("svg", "emf", "wmf") and not q.nur_raster else _png_daten(bild)
    obj = ImageObject(r.width(), r.height(), None, ellipse=ellipse, transform=Transform(dreh), fill=FillStyle.aus_dict(fuell), stroke=StrokeStyle.aus_dict(rand), effects=fx or None)
    zeichne_bild(QtRenderBackend(p), obj, rect_from_qt(r), daten, _png_daten(fuellbild) if fuellbild is not None and not fuellbild.isNull() else None)


def bild_zeichnen(p: QPainter, bild: QImage, r: QRectF, ellipse: bool = False, rand: dict | None = None, dreh: float = 0.0,
                  fuell: dict | None = None, fuellbild: QImage | None = None, fx: dict | None = None) -> None:
    """Bild in ``r``; ``ellipse``: in einer Ellipse beschnitten; ``rand``: {"b": px, "farbe": "#rrggbb", "art": Linienart} eine Linie um die Form;
    ``dreh``: Grad um die Mitte; ``fuell``: Füllung hinter dem Bild (siehe ``fuell_pinsel``)."""
    if bild is None or bild.isNull() or r.width() <= 0 or r.height() <= 0:
        return
    if _text_gerade(dreh, fx):
        leer = QImage(1, 1, QImage.Format_ARGB32); leer.fill(0)
        bild_zeichnen(p, leer, r, ellipse, rand, dreh, fuell, fuellbild, None)
        bild_zeichnen(p, bild, r, ellipse, None, 0.0, None, None, {k: v for k, v in fx.items() if k not in ("drehung", "d3")} or None)
        return
    _ueber_backend(p, bild, r, ellipse, rand, dreh, fuell, fuellbild, fx)              # Effekte, Füllung, Bild, Ausschnitt, Kontur und Drehung zeichnet das Backend


# ---- Alle Bilder eines Blattes -----------------------------------------------------------------------------------------------
def versatz_fuer(a: dict, r: QRectF, page, n: int) -> dict:
    """Die Angaben ``xh``/``yv`` (ohne Ausrichtung), mit denen das Bild im Rechteck ``r`` steht — zum Verschieben und Verändern der Größe."""
    from lunivo_writer.modelle.seite import mm_to_px
    bw, bh = mm_to_px(page.width_mm), mm_to_px(page.height_mm)
    ml, mt = mm_to_px(page.margin_left_mm), mm_to_px(page.margin_top_mm)
    null = dict(a, ah="", av="", xh=0.0, yv=0.0)
    basis = rechteck(null, bw, bh, ml, mt, page.content_width_px, page.content_height_px, a.get("_ay", 0.0), a.get("_sx"), n)
    return dict(a, ah="", av="", xh=r.x() - basis.x(), yv=r.y() - basis.y(), b=r.width(), h=r.height())


def ohne_hilfsangaben(a: dict) -> dict:
    return {k: v for k, v in a.items() if not k.startswith("_")}


def vorne_hinten(objekte, hinter: bool):
    return [o for o in objekte if bool(o[0].get("hinter")) == hinter]
