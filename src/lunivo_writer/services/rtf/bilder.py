"""RTF-Bilder: Steuerwörter einer ``\\pict``-Gruppe sammeln und die Bilddaten in ein QImage umsetzen."""
from __future__ import annotations

import re

from PySide6.QtGui import QImage

_ARTEN = ("pngblip", "jpegblip", "emfblip", "wmetafile", "dibitmap", "wbitmap", "macpict")
_MASSE = {"picw": "w", "pich": "h", "picwgoal": "gw", "pichgoal": "gh", "picscalex": "sx", "picscaley": "sy"}
_LESBAR = ("pngblip", "jpegblip", "emfblip", None)


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


def bild_lauf(b: dict) -> tuple | None:
    """→ ("b", QImage, (Breite, Höhe)) oder None, wenn das Format nicht lesbar ist. Twip → px: 15 Twip = 1 px."""
    from lunivo_writer.editor.objekte.freie_bilder import bild_aus_daten
    daten = _bilddaten(b)
    img = bild_aus_daten(daten) if b["art"] in _LESBAR else QImage()
    if img.isNull():
        return None
    bw = (b["gw"] / 15 if b["gw"] else img.width()) * b["sx"] / 100
    bh = (b["gh"] / 15 if b["gh"] else img.height()) * b["sy"] / 100
    return ("b", img, (bw, bh))
