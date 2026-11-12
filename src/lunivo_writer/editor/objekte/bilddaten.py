"""Originaldaten von Bildern: Bytes und Format der Datei, aus der ein Bild stammt.

Das ``QImage`` in der Dokumentressource bleibt die Anzeige. Die Originalbytes liegen daneben in einer Ablage und gehören zum Bild über
den Schlüssel der Pixeldaten (``QImage.cacheKey``): Jede Änderung der Bildpunkte (Zuschnitt löschen, Farbe, Verkleinern, Effekt)
erzeugt neue Pixeldaten und damit einen neuen Schlüssel — dann gibt es kein Original mehr und die Schreiber nehmen wie bisher PNG.
Kopien desselben Bildes unter anderem Ressourcennamen (Bild ändern, Einfügen aus anderen Dokumenten) behalten das Original.
Zuschnitt, Helligkeit und Kontrast stehen als Angaben am Bild (nicht in den Bildpunkten) und ändern das Original nicht.

SVG bleibt Vektor: das ``QImage`` ist nur die Rasterfassung (Anzeige im Text, Ersatzgrafik zum Speichern, längste Seite ``ERSATZ_SEITE``),
die Bildquelle trägt das SVG. ``zeichnen`` malt es mit ``QSvgRenderer`` scharf in jeder Größe, auch auf den PDF-Painter. Es wird nur QtSvg
benutzt (keine Skripte); Verweise auf andere Dateien werden vor dem Zeichnen entfernt.

Gebraucht von den Lesern (``bild_aus_daten``, ``bild_lesen``), dem Einfügen und den Schreibern (DOCX, ODT, RTF)."""
from __future__ import annotations

import gzip
import io
import os
import re
from collections import OrderedDict
from dataclasses import dataclass

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QRectF, QSizeF, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

from lunivo_writer.core.document.bildformat import FORMATE, BildFehler, format_erkennen  # noqa: F401  (Qt-freie Erkennung im Kern)
from lunivo_writer.core.document.bildformat import MAX_ENTPACKT_BYTES, entpacken as _entpacken

MAX_DATEI_BYTES = 50 * 1024 * 1024                  # größere Bilddateien werden beim Einfügen abgelehnt
NS_SVG = "http://schemas.microsoft.com/office/drawing/2016/SVG/main"      # Word-Erweiterung für SVG in DOCX (a:blip/a:extLst/asvg:svgBlip)
ERSATZ_SEITE = 1200                                 # längste Seite der Rasterfassung (Ersatzgrafik) eines SVG in Bildpunkten
MAX_ABLAGE_BYTES = 256 * 1024 * 1024                # Ablage der Originale; die ältesten fallen heraus (dann wird PNG geschrieben)


@dataclass(frozen=True)
class BildQuelle:
    """Originalbytes eines Bildes. ``ersatz_png``: Pixelersatz für Vektorformate (SVG, EMF, WMF)."""
    daten: bytes
    format: str
    ersatz_png: bytes | None = None
    nur_raster: bool = False                    # Metafile, dessen Anzeige aus einem eingebetteten Bitmap kommt: nicht als Vektor zeichnen

    @property
    def endung(self) -> str:
        return FORMATE[self.format][0]

    @property
    def medientyp(self) -> str:
        return FORMATE[self.format][1]


def entpacken(blob: bytes) -> bytes:
    """gzip-gepackte Bilddaten (SVGZ, EMZ, WMZ) entpacken, höchstens ``MAX_ENTPACKT_BYTES``."""
    return _entpacken(blob, MAX_ENTPACKT_BYTES)


# ---- Ablage -----------------------------------------------------------------------------------------------------------------
_ABLAGE: "OrderedDict[int, BildQuelle]" = OrderedDict()
_ablage_bytes = 0


def merken(img: QImage, blob: bytes, ersatz_png: bytes | None = None, nur_raster: bool = False) -> BildQuelle | None:
    """Die Originalbytes zu diesem Bild ablegen. None, wenn das Bild leer oder das Format unbekannt ist."""
    global _ablage_bytes
    if img is None or img.isNull() or not blob:
        return None
    fmt = format_erkennen(blob)
    if fmt is None:
        return None
    q = BildQuelle(bytes(blob), fmt, ersatz_png, nur_raster)
    schluessel = img.cacheKey()
    alt = _ABLAGE.pop(schluessel, None)
    if alt is not None:
        _ablage_bytes -= len(alt.daten)
    _ABLAGE[schluessel] = q
    _ablage_bytes += len(q.daten)
    while _ablage_bytes > MAX_ABLAGE_BYTES and len(_ABLAGE) > 1:
        _, aelter = _ABLAGE.popitem(last=False)
        _ablage_bytes -= len(aelter.daten)
    return q


def quelle_zu(img: QImage | None) -> BildQuelle | None:
    """Das Original zu diesem Bild, solange seine Bildpunkte unverändert sind; sonst None (dann PNG schreiben)."""
    if img is None or img.isNull():
        return None
    return _ABLAGE.get(img.cacheKey())


def uebernehmen(von: QImage, nach: QImage) -> None:
    """Ein Bild mit gleichen Bildpunkten, aber eigenem Schlüssel (zum Beispiel nach einer verlustfreien Kopie) behält das Original."""
    q = quelle_zu(von)
    if q is not None and not nach.isNull():
        merken(nach, q.daten, q.ersatz_png)


# ---- Fürs Speichern -----------------------------------------------------------------------------------------------------------
# Formate, die der jeweilige Schreiber als Original ablegen kann; alles andere (und jedes bearbeitete Bild) wird als PNG geschrieben
ORIGINAL_DOCX = frozenset({"png", "jpeg", "gif", "bmp", "tiff"})
ORIGINAL_ODT = frozenset({"png", "jpeg", "gif", "bmp", "tiff", "webp", "emf", "wmf"})
ORIGINAL_DOCX_METAFILE = frozenset({"emf", "wmf"})           # DOCX: als eigener Bildteil (python-docx nimmt sie nicht an), siehe schreiben_objekte._metafile_anhaengen


def png_bytes(img: QImage) -> bytes:
    puffer = QByteArray()
    geraet = QBuffer(puffer)
    geraet.open(QIODevice.WriteOnly)
    img.save(geraet, "PNG")
    geraet.close()
    return bytes(puffer.data())


def fuer_schreiben(img: QImage, erlaubt: frozenset[str]) -> tuple[bytes, str, str]:
    """→ (Bytes, Dateiendung, Medientyp) für das Speichern: das Original, wenn die Bildpunkte unverändert sind und der Schreiber das Format
    kennt (``erlaubt``), sonst PNG."""
    q = quelle_zu(img)
    if q is not None and q.format == "svg" and q.ersatz_png:          # Vektor ohne Vektor-Schreiber: die Ersatzgrafik
        return q.ersatz_png, "png", "image/png"
    if q is not None and q.format in erlaubt:
        return q.daten, q.endung, q.medientyp
    return png_bytes(img), "png", "image/png"


# ---- Lesen ---------------------------------------------------------------------------------------------------------------------
def mit_ausrichtung_lesen(blob: bytes) -> QImage:
    """Bilddaten lesen und eine EXIF-Drehung/-Spiegelung (Fotos von Kameras und Telefonen) anwenden — so zeigt Word das Bild und so bleibt das
    gespeicherte Original (mit seiner EXIF-Angabe) zur Anzeige stimmig. Leeres QImage, wenn Qt das Format nicht liest."""
    from PySide6.QtGui import QImageReader
    daten = QByteArray(blob)
    puffer = QBuffer(daten)
    puffer.open(QIODevice.ReadOnly)
    leser = QImageReader(puffer)
    leser.setAutoTransform(True)
    img = leser.read()
    del leser                                               # der Leser muss vor Puffer und Bytes enden (sonst Absturz bei TIFF)
    puffer.close()
    return img


# ---- SVG ----------------------------------------------------------------------------------------------------------------------
_EXTERN = re.compile(rb"""((?:xlink:)?href\s*=\s*)(["'])(?!\s*(?:data:|#))[^"']*\2""", re.I)
_RENDERER: "OrderedDict[int, QSvgRenderer]" = OrderedDict()
_RENDERER_MAX = 64


def svg_bereinigen(svg: bytes) -> bytes:
    """Verweise auf andere Dateien oder Adressen entfernen (nur ``data:`` und ``#``-Verweise im Bild bleiben)."""
    return _EXTERN.sub(rb'\1\2\2', svg)


def _renderer(q: BildQuelle) -> QSvgRenderer | None:
    schluessel = id(q.daten)
    r = _RENDERER.get(schluessel)
    if r is not None and r.property("quelle") is q.daten:
        _RENDERER.move_to_end(schluessel)
        return r
    r = QSvgRenderer(svg_bereinigen(q.daten))
    if not r.isValid():
        return None
    r.setProperty("quelle", q.daten)                              # hält die Bytes am Leben, damit ``id`` nicht wiederverwendet wird
    _RENDERER[schluessel] = r
    while len(_RENDERER) > _RENDERER_MAX:
        _RENDERER.popitem(last=False)
    return r


def _svg_groesse(r: QSvgRenderer) -> QSizeF:
    g = r.defaultSizeF() if hasattr(r, "defaultSizeF") else QSizeF(r.defaultSize())
    return g if g.width() > 0 and g.height() > 0 else QSizeF(300.0, 150.0)


def svg_raster(svg: bytes, seite: int = ERSATZ_SEITE) -> QImage:
    """Rasterfassung eines SVG (transparent, längste Seite ``seite``); leeres QImage, wenn QtSvg es nicht lesen kann."""
    r = _renderer(BildQuelle(svg, "svg"))
    if r is None:
        return QImage()
    g = _svg_groesse(r)
    f = seite / max(g.width(), g.height())
    img = QImage(max(1, round(g.width() * f)), max(1, round(g.height() * f)), QImage.Format_ARGB32_Premultiplied)
    img.fill(0)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    r.render(p, QRectF(0, 0, img.width(), img.height()))
    p.end()
    return img


def bild_aus_svg(svg: bytes, ersatz_png: bytes | None = None) -> QImage:
    """Ein SVG als Bild mit Vektorquelle. ``ersatz_png``: vorhandene Ersatzgrafik (aus DOCX/ODT) als Rasterfassung; sonst wird gerastert."""
    img = QImage()
    if ersatz_png and format_erkennen(ersatz_png) == "png" and img.loadFromData(ersatz_png) and not img.isNull():
        merken(img, svg, ersatz_png)
        return img
    img = svg_raster(svg)
    if not img.isNull():
        merken(img, svg, png_bytes(img))
    return img


def ist_svg(img: QImage | None) -> bool:
    q = quelle_zu(img)
    return q is not None and q.format == "svg"


def anzeigegroesse(img: QImage) -> tuple[float, float]:
    """Startgröße auf dem Blatt in px: bei SVG das Maß aus ``width``/``height`` bzw. ``viewBox``, sonst die Bildgröße."""
    q = quelle_zu(img)
    if q is not None and q.format == "svg":
        r = _renderer(q)
        if r is not None:
            g = _svg_groesse(r)
            return g.width(), g.height()
    if q is not None and q.format in ("emf", "wmf"):
        from lunivo_writer.dienste.vektor_bilder import masse_px
        m = masse_px(q.daten)
        if m is not None:
            return m
    return float(img.width()), float(img.height())


def zeichnen(p: QPainter, r: QRectF, img: QImage) -> None:
    """Das Bild in ``r`` zeichnen; ein unverändertes SVG als Vektor (scharf in jeder Zoomstufe, auch im PDF), sonst die Bildpunkte."""
    q = quelle_zu(img)
    if q is not None and q.format == "svg":
        rd = _renderer(q)
        if rd is not None:
            rd.render(p, r)
            return
    if q is not None and q.format in ("emf", "wmf") and not q.nur_raster:
        from lunivo_writer.dienste import vektor_bilder as V
        if (V.emf_zeichnen if q.format == "emf" else V.wmf_zeichnen)(q.daten, p, r):
            return
    p.drawImage(r, img)


# ---- Bilddatei laden ----------------------------------------------------------------------------------------------------------
def platzhalter(breite: float, hoehe: float) -> QImage:
    """Ersatz für ein Bild, dessen Daten fehlen oder nicht lesbar sind: graue Fläche mit Rahmen und Kreuz in der Größe des Bildes (gezeichnet über das Rendering-Backend)."""
    from lunivo_writer.adapter.qt.rendering import QtRenderBackend
    from lunivo_writer.core.geometry import Rect
    from lunivo_writer.core.rendering.objekte import zeichne_platzhalter
    b, h = max(8, round(breite)), max(8, round(hoehe))
    img = QImage(b, h, QImage.Format_ARGB32)
    img.fill(0)
    p = QPainter(img)
    zeichne_platzhalter(QtRenderBackend(p), Rect(0.5, 0.5, b - 1, h - 1))
    p.end()
    return img


def bild_aus_datei(pfad: str, still: bool = False) -> QImage:
    """Eine Bilddatei als QImage laden und ihr Original ablegen. Leeres QImage, wenn sie sich nicht lesen lässt;
    ``BildFehler`` mit Meldung, wenn sie zu groß ist (über ``MAX_DATEI_BYTES``); mit ``still`` stattdessen ein leeres QImage."""
    try:
        return _aus_datei(pfad)
    except BildFehler:
        if still:
            return QImage()
        raise


def _aus_datei(pfad: str) -> QImage:
    try:
        groesse = os.path.getsize(pfad)
    except OSError:
        return QImage()
    if groesse > MAX_DATEI_BYTES:
        raise BildFehler(f"Die Bilddatei ist zu groß ({groesse // (1024 * 1024)} MB). Erlaubt sind höchstens {MAX_DATEI_BYTES // (1024 * 1024)} MB.")
    try:
        with open(pfad, "rb") as f:
            blob = entpacken(f.read())
    except OSError:
        return QImage()
    from lunivo_writer.dienste.vektor_bilder import bild_lesen
    img = bild_lesen(blob)
    if img.isNull():
        img = QImage(pfad)                      # Rückfall: Qt entscheidet nach Dateiendung
        if not img.isNull():
            merken(img, blob)
    return img
