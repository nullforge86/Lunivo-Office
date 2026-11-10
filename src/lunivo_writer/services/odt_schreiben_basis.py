"""Gemeinsame Bausteine zum Schreiben von ODT: Namensräume, Maße, Tabellen-Elemente, Bilder und frei positionierte Rahmen.

Genutzt von ``odt_writer`` (Inhalt), ``odt_seite_schreiben`` (Seitenvorlage, Kopf-/Fußzeile) und ``rtf_writer`` (Bilder, Zellenspannen).
"""
from __future__ import annotations

from xml.sax.saxutils import escape

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QUrl
from PySide6.QtGui import QImage, QPixmap, QTextDocument, QTextTable

MIMETYPE = b"application/vnd.oasis.opendocument.text"
_NS = ('xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
       'xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" '
       'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" '
       'xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" '
       'xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" '
       'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" '
       'xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" '
       'xmlns:xlink="http://www.w3.org/1999/xlink" '
       'xmlns:dc="http://purl.org/dc/elements/1.1/" '
       'xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" '
       'xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"')


def _mm(wert: float) -> str:
    return f"{max(0.0, float(wert)):.2f}mm"



def bild_aus_format(doc: QTextDocument, cf) -> QImage | None:
    """Das Bild hinter einem Bildformat (Ressource im Dokument oder Datei), sonst None."""
    name = cf.toImageFormat().name()
    res = doc.resource(QTextDocument.ImageResource, QUrl(name))
    if isinstance(res, QImage):
        img = res
    elif isinstance(res, (bytes, QByteArray)):
        img = QImage.fromData(res)
    elif isinstance(res, QPixmap):
        img = res.toImage()
    else:
        img = QImage(name)
    return None if img.isNull() else img


def spannweite(t: QTextTable, r: int, c: int) -> tuple[int, int]:
    """Wie viele Spalten und Zeilen die Zelle mit Ursprung (r, c) überdeckt (gezählt, nicht columnSpan(): das liefert für
    verbundene Zellen aus DOCX nicht immer den echten Wert)."""
    def gleich(rr: int, cc: int) -> bool:
        z = t.cellAt(rr, cc)
        return z.row() == r and z.column() == c
    breit = 1
    while c + breit < t.columns() and gleich(r, c + breit):
        breit += 1
    hoch = 1
    while r + hoch < t.rows() and gleich(r + hoch, c):
        hoch += 1
    return breit, hoch


def _png(img: QImage) -> bytes:
    puffer = QByteArray()
    geraet = QBuffer(puffer)
    geraet.open(QIODevice.WriteOnly)
    img.save(geraet, "PNG")
    geraet.close()
    return bytes(puffer)


def _odf(element: str, attr: dict | None = None, inhalt: str | None = None) -> str:
    """Ein Element des ODF-Tabellenmodells (Namensraum ``table:``) als XML-Text."""
    name = "table:" + element
    a = "".join(f' {k}="{escape(v, {chr(34): "&quot;"})}"' for k, v in (attr or {}).items())
    return f"<{name}{a}/>" if inhalt is None else f"<{name}{a}>{inhalt}</{name}>"


def _laenge(px: float) -> str:
    return f"{px * 25.4 / 96:.2f}mm"


# Frei positionierte Bilder (editor/objekte/freie_bilder.py) ↔ ODF-Rahmen am Absatz: Bezug und Ausrichtung je Achse.
BEZUG_H = {"seite": "page", "rand": "page-content", "spalte": "paragraph"}
BEZUG_V = {"seite": "page", "rand": "page-content", "absatz": "paragraph"}
AUSR_H = {"left": "left", "center": "center", "right": "right", "inside": "inside", "outside": "outside"}
AUSR_V = {"top": "top", "center": "middle", "bottom": "bottom"}


def _frei_stil(name: str, a: dict) -> str:
    """Rahmenvorlage (Familie „graphic“) für ein frei positioniertes Bild: ohne Textumfluss, vor oder hinter dem Text."""
    return (f'<style:style style:name="{name}" style:family="graphic"><style:graphic-properties style:wrap="run-through" '
            f'style:run-through="{"background" if a.get("hinter") else "foreground"}" '
            f'style:horizontal-pos="{AUSR_H.get(a.get("ah") or "", "from-left")}" '
            f'style:horizontal-rel="{BEZUG_H.get(a.get("bh"), "paragraph")}" '
            f'style:vertical-pos="{AUSR_V.get(a.get("av") or "", "from-top")}" '
            f'style:vertical-rel="{BEZUG_V.get(a.get("bv"), "paragraph")}"/></style:style>')


def _frei_rahmen(a: dict, img: QImage, nr: int, stil: str, bilder: dict[str, bytes]) -> str:
    """Ein frei positioniertes Bild als draw:frame am Absatz; die Bilddaten kommen nach ``bilder`` (Pictures/…)."""
    name = f"Pictures/frei{nr}.png"
    bilder[name] = _png(img)
    b, h = float(a.get("b") or img.width()), float(a.get("h") or img.height())
    lage = ""
    if not AUSR_H.get(a.get("ah") or ""):
        lage += f' svg:x="{_laenge(float(a.get("xh") or 0))}"'
    if not AUSR_V.get(a.get("av") or ""):
        lage += f' svg:y="{_laenge(float(a.get("yv") or 0))}"'
    return (f'<draw:frame draw:style-name="{stil}" draw:name="Frei{nr}" text:anchor-type="paragraph"{lage} '
            f'svg:width="{_laenge(b)}" svg:height="{_laenge(h)}" draw:z-index="{0 if a.get("hinter") else nr}">'
            f'<draw:image xlink:href="{name}" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/></draw:frame>')
