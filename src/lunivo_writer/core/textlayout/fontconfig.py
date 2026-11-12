"""Ersatzfamilien wie bei Fontconfig, ohne das Programm: die Regeln der Konfigurationsdateien (``/etc/fonts/conf.d``, ``~/.config/fontconfig``) werden gelesen und auf eine
Familienliste angewendet. Berücksichtigt werden ``<alias>`` (prefer, accept, default) und ``<match>`` mit Tests nur auf ``family`` und Änderungen an ``family``
(assign, prepend, append …); Regeln mit anderen Tests (Sprache, Größe, Schriftdatei) werden übersprungen. So landet eine fehlende Familie (zum Beispiel Tahoma) bei derselben
Ersatzschrift wie in Qt, das Fontconfig fragt."""
from __future__ import annotations

import glob
import os
import xml.etree.ElementTree as ET

ORDNER = ("/etc/fonts/conf.d", "~/.config/fontconfig/conf.d")
DATEIEN = ("/etc/fonts/local.conf", "~/.config/fontconfig/fonts.conf", "~/.fonts.conf")
_regeln: list | None = None


def _texte(el) -> list[str]:
    return [(s.text or "").strip() for s in el.findall("string")]


def _lesen_datei(pfad: str, regeln: list) -> None:
    try:
        wurzel = ET.parse(pfad).getroot()
    except (ET.ParseError, OSError):
        return
    for el in wurzel:
        if el.tag == "alias":
            fam = [(f.text or "").strip() for f in el.findall("family")]
            if not fam:
                continue
            for liste, modus in (("prefer", "prepend"), ("accept", "append"), ("default", "append_last")):
                namen = [(f.text or "").strip() for k in el.findall(liste) for f in k.findall("family")]
                if namen:
                    regeln.append((fam, modus, namen))
        elif el.tag == "match":
            tests = el.findall("test")
            if el.get("target", "pattern") != "pattern" or not tests or any(t.get("name") != "family" or t.get("compare", "eq") != "eq" for t in tests):
                continue
            ziele = [n for t in tests for n in _texte(t)]
            for e in el.findall("edit"):
                if e.get("name") == "family":
                    regeln.append((ziele, e.get("mode", "assign"), _texte(e)))


def regeln() -> list:
    global _regeln
    if _regeln is None:
        res: list = []
        dateien: list[str] = []
        for o in ORDNER:
            dateien += sorted(glob.glob(os.path.join(os.path.expanduser(o), "*.conf")), key=os.path.basename)
        dateien += [os.path.expanduser(d) for d in DATEIEN if os.path.exists(os.path.expanduser(d))]
        for d in sorted(dateien[: len(dateien)], key=lambda p: (os.path.basename(p) if "conf.d" in p else "~" + p)):
            _lesen_datei(d, res)
        _regeln = res
    return _regeln


def familien_liste(name: str) -> list[str]:
    """Die Familien, die Fontconfig für ``name`` in dieser Reihenfolge ausprobieren würde (kleingeschrieben, ohne Doppelte)."""
    liste = [name.lower()]
    for ziele, modus, namen in regeln():
        ziele_l = [z.lower() for z in ziele]
        treffer = next((i for i, f in enumerate(liste) if f in ziele_l), None)
        if treffer is None:
            continue
        neu = [n.lower() for n in namen]
        if modus in ("assign", "assign_replace"):
            liste = neu if modus == "assign" else liste[:treffer] + neu + liste[treffer + 1:]
        elif modus == "prepend":
            liste[treffer:treffer] = neu
        elif modus == "prepend_first":
            liste[0:0] = neu
        elif modus == "append":
            liste[treffer + 1:treffer + 1] = neu
        elif modus == "append_last":
            liste += neu
    gesehen: set[str] = set()
    return [f for f in liste if not (f in gesehen or gesehen.add(f))]
