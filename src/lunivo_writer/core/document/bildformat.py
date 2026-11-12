"""Bilddateien erkennen und vermessen, ohne Qt und ohne Bildbibliothek: Format am Dateikopf, Pixelgröße, Seitenverhältnis, gepackte Bilder (SVGZ, EMZ, WMZ).

Erkannt werden PNG, JPEG, GIF, BMP, TIFF, WebP, SVG, EMF und WMF. Die Größe kommt aus dem Dateikopf (PNG IHDR, JPEG SOF, GIF, BMP, TIFF IFD, WebP VP8/VP8L/VP8X,
SVG ``width``/``height``/``viewBox``, EMF-Kopf); ``None``, wenn der Kopf sie nicht hergibt. Die Pixel selbst decodiert das Rendering-Backend."""
from __future__ import annotations

import gzip
import io
import re
import struct

# Format → (Dateiendung, Medientyp)
FORMATE: dict[str, tuple[str, str]] = {
    "png": ("png", "image/png"), "jpeg": ("jpg", "image/jpeg"), "gif": ("gif", "image/gif"), "bmp": ("bmp", "image/bmp"),
    "tiff": ("tiff", "image/tiff"), "webp": ("webp", "image/webp"), "svg": ("svg", "image/svg+xml"),
    "emf": ("emf", "image/x-emf"), "wmf": ("wmf", "image/x-wmf"),
}
MAX_ENTPACKT_BYTES = 50 * 1024 * 1024               # gzip-Bilder dürfen entpackt nicht größer sein (Schutz vor gepackten Bomben)


class BildFehler(ValueError):
    """Bilddatei nicht verwendbar; die Meldung ist für den Benutzer."""


def format_erkennen(blob: bytes) -> str | None:
    """Das Bildformat am Dateikopf (nicht an der Endung); None, wenn es keines der bekannten ist."""
    k = blob[:16]
    if k.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if k.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if k.startswith((b"GIF87a", b"GIF89a")):
        return "gif"
    if k.startswith((b"II*\x00", b"MM\x00*")):
        return "tiff"
    if k[:4] == b"RIFF" and k[8:12] == b"WEBP":
        return "webp"
    if len(blob) >= 44 and blob[40:44] == b" EMF":
        return "emf"
    if k.startswith(b"\xd7\xcd\xc6\x9a") or (k[:2] in (b"\x01\x00", b"\x02\x00") and k[2:4] == b"\x09\x00" and k[4:6] in (b"\x00\x01", b"\x00\x03")):
        return "wmf"                                           # mit Platzhalterkopf oder (wie in RTF) nur der Metafile-Kopf
    if k.startswith(b"BM"):
        return "bmp"
    kopf = blob[:1024].lstrip(b"\xef\xbb\xbf \t\r\n")
    if kopf.startswith(b"<svg") or (kopf.startswith(b"<?xml") and b"<svg" in blob[:1024]) or (kopf.startswith(b"<!--") and b"<svg" in blob[:1024]):
        return "svg"
    return None


def entpacken(blob: bytes, grenze: int = MAX_ENTPACKT_BYTES) -> bytes:
    """gzip-gepackte Bilddaten (SVGZ, EMZ, WMZ) entpacken, höchstens ``grenze`` Bytes; andere Daten bleiben unverändert."""
    if not blob.startswith(b"\x1f\x8b"):
        return blob
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(blob)) as g:
            roh = g.read(grenze + 1)
    except (OSError, EOFError):
        raise BildFehler("Die gepackte Bilddatei ist beschädigt.") from None
    if len(roh) > grenze:
        raise BildFehler("Die gepackte Bilddatei ist entpackt zu groß.")
    return roh


def _jpeg(b: bytes):
    i = 2
    while i + 9 < len(b):
        if b[i] != 0xFF:
            i += 1
            continue
        m = b[i + 1]
        if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        n = struct.unpack(">H", b[i + 2:i + 4])[0]
        if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack(">HH", b[i + 5:i + 9])
            return w, h
        i += 2 + n
    return None


def _tiff(b: bytes):
    le = b[:2] == b"II"
    e = "<" if le else ">"
    try:
        ifd = struct.unpack(e + "I", b[4:8])[0]
        n = struct.unpack(e + "H", b[ifd:ifd + 2])[0]
        w = h = None
        for i in range(n):
            tag, typ, _cnt = struct.unpack(e + "HHI", b[ifd + 2 + 12 * i:ifd + 10 + 12 * i])
            raw = b[ifd + 10 + 12 * i:ifd + 14 + 12 * i]
            wert = struct.unpack(e + ("H" if typ == 3 else "I"), raw[:2] if typ == 3 else raw)[0]
            if tag == 256:
                w = wert
            elif tag == 257:
                h = wert
        return (w, h) if w and h else None
    except (struct.error, IndexError):
        return None


def _webp(b: bytes):
    art = b[12:16]
    try:
        if art == b"VP8X":
            return 1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little")
        if art == b"VP8L":
            bits = int.from_bytes(b[21:25], "little")
            return 1 + (bits & 0x3FFF), 1 + ((bits >> 14) & 0x3FFF)
        if art == b"VP8 ":
            w, h = struct.unpack("<HH", b[26:30])
            return w & 0x3FFF, h & 0x3FFF
    except (struct.error, ValueError):
        pass
    return None


def _zahl(text: str | None):
    if not text:
        return None
    m = re.match(r"\s*([0-9.]+)\s*(px|pt|mm|cm|in)?\s*$", text)
    if not m:
        return None
    f = {"px": 1.0, "pt": 96 / 72, "mm": 96 / 25.4, "cm": 96 / 2.54, "in": 96.0, None: 1.0}[m.group(2)]
    return float(m.group(1)) * f


def _svg(b: bytes):
    kopf = b[:4096].decode("utf-8", "ignore")
    tag = re.search(r"<svg\b[^>]*>", kopf, re.S)
    if not tag:
        return None
    t = tag.group(0)
    attr = lambda n: (re.search(r"\b" + n + r"\s*=\s*[\"']([^\"']*)[\"']", t) or [None, None])[1]            # noqa: E731
    w, h = _zahl(attr("width")), _zahl(attr("height"))
    if (not w or not h) and attr("viewBox"):
        try:
            v = [float(x) for x in re.split(r"[ ,]+", attr("viewBox").strip())]
            w, h = w or v[2], h or v[3]
        except (ValueError, IndexError):
            pass
    return (w, h) if w and h else None


def masse(blob: bytes) -> tuple[float, float] | None:
    """Pixelgröße (Vektorformate: Größe in Bildpunkten bei 96 dpi) aus dem Dateikopf; ``None``, wenn nicht lesbar."""
    fmt = format_erkennen(blob)
    try:
        if fmt == "png":
            return struct.unpack(">II", blob[16:24])
        if fmt == "gif":
            return struct.unpack("<HH", blob[6:10])
        if fmt == "bmp":
            w, h = struct.unpack("<ii", blob[18:26])
            return abs(w), abs(h)
        if fmt == "jpeg":
            return _jpeg(blob)
        if fmt == "tiff":
            return _tiff(blob)
        if fmt == "webp":
            return _webp(blob)
        if fmt == "svg":
            return _svg(blob)
        if fmt == "emf":
            l, o, r, u = struct.unpack("<iiii", blob[24:40])                   # Bezugsrechteck in Geräteeinheiten des Metafiles (0,01 mm in Millimetern: Bounds 8..24)
            rl, ro, rr, ru = struct.unpack("<iiii", blob[72:88]) if len(blob) >= 88 else (0, 0, 0, 0)
            w, h = (rr - rl) / 100 * 96 / 25.4, (ru - ro) / 100 * 96 / 25.4
            return (w, h) if w > 0 and h > 0 else (r - l, u - o)
    except (struct.error, IndexError, TypeError):
        return None
    return None


def seitenverhaeltnis(blob: bytes) -> float | None:
    """Breite / Höhe des Bildes (aus dem Dateikopf)."""
    m = masse(blob)
    return m[0] / m[1] if m and m[1] else None
