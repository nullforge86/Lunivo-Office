"""RTF-Bilder: Steuerwörter einer ``\\pict``-Gruppe sammeln; die Bildbytes bleiben im Original (Qt-frei)."""
from __future__ import annotations

import re

_ARTEN = ("pngblip", "jpegblip", "emfblip", "wmetafile", "dibitmap", "wbitmap", "macpict")
_MASSE = {"picw": "w", "pich": "h", "picwgoal": "gw", "pichgoal": "gh", "picscalex": "sx", "picscaley": "sy"}
_LESBAR = ("pngblip", "jpegblip", "emfblip", "wmetafile", None)


def neues_bild() -> dict:
    return {"hex": [], "art": None, "w": None, "h": None, "gw": None, "gh": None, "sx": 100, "sy": 100}


def bild_wort(b: dict, w: str, z: int | None) -> None:
    if w in _ARTEN:
        b["art"] = w
    elif w in _MASSE and z is not None:
        b[_MASSE[w]] = z


def _bilddaten(b: dict) -> bytes:
    if "bin" in b:
        return b["bin"]
    roh = re.sub(rb"[^0-9a-fA-F]", b"", b"".join(b["hex"]))
    return bytes.fromhex(roh[: len(roh) // 2 * 2].decode("ascii"))


def bilddaten(b: dict) -> bytes:
    """Die Bytes einer ``\\pict``-Gruppe (Hexdaten oder ``\\bin``); leer, wenn die Gruppe keine enthält."""
    try:
        return _bilddaten(b)
    except ValueError:
        return b""


def dib_zu_png(daten: bytes) -> bytes | None:
    """Ein Windows-DIB (``\\dibitmap``: BITMAPINFOHEADER, Palette, Bildpunkte) als PNG; ``None``, wenn das Format nicht unterstützt wird (nur unkomprimiert, 1/4/8/24/32 Bit)."""
    import struct
    import zlib
    if len(daten) < 40:
        return None
    gr, breite, hoehe, _ebenen, bits, komp, _gb, _xp, _yp, farbanz, _wichtig = struct.unpack("<IiiHHIIiiII", daten[:40])
    if gr < 40 or komp not in (0, 3) or bits not in (1, 4, 8, 24, 32) or breite <= 0 or hoehe == 0 or breite > 20000 or abs(hoehe) > 20000:
        return None
    oben = hoehe < 0
    hoehe = abs(hoehe)
    palette = []
    if bits <= 8:
        n = farbanz or (1 << bits)
        for i in range(n):
            p = daten[gr + 4 * i:gr + 4 * i + 4]
            if len(p) < 4:
                return None
            palette.append((p[2], p[1], p[0]))
        start = gr + 4 * n
    else:
        start = gr + (12 if komp == 3 else 0)
    zeile = ((breite * bits + 31) // 32) * 4
    if len(daten) < start + zeile * hoehe:
        return None
    reihen = []
    for r in range(hoehe):
        q = r if oben else hoehe - 1 - r
        roh = daten[start + q * zeile:start + (q + 1) * zeile]
        aus = bytearray()
        if bits == 24:
            for x in range(breite):
                aus += bytes((roh[3 * x + 2], roh[3 * x + 1], roh[3 * x]))
        elif bits == 32:
            for x in range(breite):
                aus += bytes((roh[4 * x + 2], roh[4 * x + 1], roh[4 * x]))
        else:
            for x in range(breite):
                bit = x * bits
                wert = (roh[bit // 8] >> (8 - bits - bit % 8)) & ((1 << bits) - 1)
                aus += bytes(palette[wert] if wert < len(palette) else (0, 0, 0))
        reihen.append(b"\x00" + bytes(aus))

    def chunk(art: bytes, inhalt: bytes) -> bytes:
        return struct.pack(">I", len(inhalt)) + art + inhalt + struct.pack(">I", zlib.crc32(art + inhalt) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", breite, hoehe, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(b"".join(reihen))) + chunk(b"IEND", b""))


def bild_lauf_modell(b: dict) -> tuple | None:
    """Qt-freier Bildlauf: Originalbytes und Zielgröße; die Rasterung gehört zum Renderadapter. ``\\dibitmap`` wird verlustfrei nach PNG umgesetzt."""
    daten = bilddaten(b)
    if b.get("art") == "dibitmap" and daten:
        daten = dib_zu_png(daten) or daten
    from lunivo_writer.core.dokument.bildformat import format_erkennen, masse
    art = format_erkennen(daten)
    if not daten or art not in ("png", "jpeg", "emf", "wmf"):
        return None
    groesse = masse(daten)
    bw = (b["gw"] / 15 if b["gw"] else groesse[0] if groesse else 64.0) * b["sx"] / 100
    bh = (b["gh"] / 15 if b["gh"] else groesse[1] if groesse else 64.0) * b["sy"] / 100
    return ("b_raw", daten, (bw, bh), art)
