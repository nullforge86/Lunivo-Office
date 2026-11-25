"""Ersatzfamilien für Schriften, die auf dem System fehlen. Ohne Oberfläche, ohne fremde Programme.

Zwei Quellen, in dieser Reihenfolge: die Regeln der Fontconfig-Konfiguration (``/etc/fonts/conf.d``, ``~/.config/fontconfig``) — gelesen und auf eine Familienliste
angewendet, so landet eine fehlende Familie bei derselben Ersatzschrift wie in den anderen Programmen des Systems — und die Tabelle ``METRISCH_GLEICH`` mit Schriften
gleicher Zeichenbreiten (damit der Umbruch eines Word-Dokuments erhalten bleibt). Danach gelten die Standardschriften.

Berücksichtigt werden ``<alias>`` (prefer, accept, default) und ``<match>`` mit Tests nur auf ``family`` und Änderungen an ``family`` (assign, prepend, append …);
Regeln mit anderen Tests (Sprache, Größe, Schriftdatei) werden übersprungen."""
from __future__ import annotations

import glob
import os
import xml.etree.ElementTree as ET

METRISCH_GLEICH = {
    "arial": "liberation sans", "helvetica": "liberation sans", "calibri": "carlito", "cambria": "caladea",
    "times new roman": "liberation serif", "times": "liberation serif", "courier new": "liberation mono", "courier": "liberation mono",
    "segoe ui": "dejavu sans", "tahoma": "dejavu sans", "verdana": "dejavu sans", "georgia": "dejavu serif",
    "book antiqua": "noto sans", "garamond": "noto serif", "bookman old style": "urw bookman", "palatino linotype": "p052",
}
STANDARDSCHRIFTEN = ("liberation sans", "dejavu sans", "carlito")

_ORDNER = ("/etc/fonts/conf.d", "~/.config/fontconfig/conf.d")
_DATEIEN = ("/etc/fonts/local.conf", "~/.config/fontconfig/fonts.conf", "~/.fonts.conf")
_regeln: list | None = None


def _zeichenketten(element) -> list[str]:
    return [(s.text or "").strip() for s in element.findall("string")]


def _regeln_aus_datei(pfad: str, regeln: list) -> None:
    try:
        wurzel = ET.parse(pfad).getroot()
    except (ET.ParseError, OSError):
        return
    for el in wurzel:
        if el.tag == "alias":
            familien = [(f.text or "").strip() for f in el.findall("family")]
            if not familien:
                continue
            for liste, modus in (("prefer", "prepend"), ("accept", "append"), ("default", "append_last")):
                namen = [(f.text or "").strip() for k in el.findall(liste) for f in k.findall("family")]
                if namen:
                    regeln.append((familien, modus, namen))
        elif el.tag == "match":
            tests = el.findall("test")
            if el.get("target", "pattern") != "pattern" or not tests or any(t.get("name") != "family" or t.get("compare", "eq") != "eq" for t in tests):
                continue
            ziele = [n for t in tests for n in _zeichenketten(t)]
            for e in el.findall("edit"):
                if e.get("name") == "family":
                    regeln.append((ziele, e.get("mode", "assign"), _zeichenketten(e)))


def _alle_regeln() -> list:
    global _regeln
    if _regeln is None:
        gefunden: list = []
        dateien: list[str] = []
        for ordner in _ORDNER:
            dateien += sorted(glob.glob(os.path.join(os.path.expanduser(ordner), "*.conf")), key=os.path.basename)
        dateien += [os.path.expanduser(d) for d in _DATEIEN if os.path.exists(os.path.expanduser(d))]
        for datei in sorted(dateien, key=lambda p: os.path.basename(p) if "conf.d" in p else "~" + p):
            _regeln_aus_datei(datei, gefunden)
        _regeln = gefunden
    return _regeln


def ersatzfamilien(name: str) -> list[str]:
    """Die Familien, die in dieser Reihenfolge für ``name`` versucht werden (kleingeschrieben, ohne Doppelte): Fontconfig-Regeln, metrisch gleiche Schrift, Standardschriften."""
    liste = [name.lower()]
    for ziele, modus, namen in _alle_regeln():
        ziele_klein = [z.lower() for z in ziele]
        stelle = next((i for i, f in enumerate(liste) if f in ziele_klein), None)
        if stelle is None:
            continue
        neu = [n.lower() for n in namen]
        if modus == "assign":
            liste = neu
        elif modus == "assign_replace":
            liste = liste[:stelle] + neu + liste[stelle + 1:]
        elif modus == "prepend":
            liste[stelle:stelle] = neu
        elif modus == "prepend_first":
            liste[0:0] = neu
        elif modus == "append":
            liste[stelle + 1:stelle + 1] = neu
        elif modus == "append_last":
            liste += neu
    gleich = METRISCH_GLEICH.get(name.lower())
    if gleich:
        liste.append(gleich)
    liste += STANDARDSCHRIFTEN
    gesehen: set[str] = set()
    return [f for f in liste if not (f in gesehen or gesehen.add(f))]
