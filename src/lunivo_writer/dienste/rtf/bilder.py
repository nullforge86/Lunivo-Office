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


def bild_lauf_modell(b: dict) -> tuple | None:
    """Qt-freier Bildlauf: Originalbytes und Zielgröße; die Rasterung gehört zum Renderadapter."""
    daten = _bilddaten(b)
    from lunivo_writer.core.document.bildformat import format_erkennen, masse
    art = format_erkennen(daten)
    if not daten or art not in ("png", "jpeg", "emf", "wmf"):
        return None
    groesse = masse(daten)
    bw = (b["gw"] / 15 if b["gw"] else groesse[0] if groesse else 64.0) * b["sx"] / 100
    bh = (b["gh"] / 15 if b["gh"] else groesse[1] if groesse else 64.0) * b["sy"] / 100
    return ("b_raw", daten, (bw, bh), art)
