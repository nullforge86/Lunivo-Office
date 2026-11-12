"""Gemeinsame XML-Namensräume und Hilfsfunktionen für ODT/FODT."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    "svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
    "xlink": "http://www.w3.org/1999/xlink",
    "dc": "http://purl.org/dc/elements/1.1/",
    "meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
    "loext": "urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0",       # LibreOffice-Erweiterung (loext:decorative am Rahmenstil)
}
GRENZE_BYTES = 512 * 1024 * 1024          # entpackt höchstens so viel (Schutz vor „ZIP-Bomben“ und Speicherüberlauf)
MAX_WIEDERHOLUNG = 1000                   # table:number-rows/columns-repeated: leere Füllzeilen nicht ins Unendliche
_PX = {"in": 96.0, "cm": 96 / 2.54, "mm": 96 / 25.4, "pt": 96 / 72, "pc": 16.0, "px": 1.0}


_PRAEFIX = {v: k for k, v in NS.items()}


def _kurz(attr: str) -> str:
    if attr.startswith("{"):
        uri, lokal = attr[1:].split("}")
        return f"{_PRAEFIX.get(uri, '?')}:{lokal}"
    return attr


def _q(name: str) -> str:
    pre, lokal = name.split(":")
    return f"{{{NS[pre]}}}{lokal}"


def _px(wert: str | None, standard: float = 0.0) -> float:
    m = re.fullmatch(r"\s*(-?[\d.]+)\s*([a-z]*)\s*", wert or "")
    if not m:
        return standard
    try:
        return float(m.group(1)) * _PX.get(m.group(2) or "px", 1.0)
    except ValueError:
        return standard


def _pt(wert: str | None) -> float | None:
    if not wert or wert.endswith("%"):
        return None
    px = _px(wert, -1)
    return px * 72 / 96 if px > 0 else None


def _text_von(el: ET.Element) -> str:
    """Reiner Text eines Elements samt Kindern (für Kopf- und Fußzeilen); Seitenzahl-Felder werden zu {PAGE}/{PAGES}."""
    teile = [el.text or ""]
    for k in el:
        if k.tag == _q("text:page-number"):
            teile.append("{PAGE}")
        elif k.tag == _q("text:page-count"):
            teile.append("{PAGES}")
        elif k.tag == _q("text:s"):
            teile.append(" " * int(k.get(_q("text:c"), "1") or 1))
        elif k.tag == _q("text:tab"):
            teile.append("\t")
        else:
            teile.append(_text_von(k))
        teile.append(k.tail or "")
    return "".join(teile)
