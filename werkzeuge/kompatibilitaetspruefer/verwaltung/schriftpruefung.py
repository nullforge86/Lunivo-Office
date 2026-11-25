"""Schriftvorprüfung: Welche Schriften verwenden die Dokumente, und sind sie (oder ein metrisch kompatibler Ersatz) installiert?

Die Auswertung der Dateien liest nur die Schriftangaben aus dem XML (kein Lunivo, keine Qt-Klassen) und ist deshalb für einen Hintergrund-Thread geeignet. Die Bewertung gegen die installierten
Schriften (``bewerte``) braucht Qt und läuft im Programm bzw. im Prüfprozess."""
from __future__ import annotations

import re
import zipfile

# Metrisch kompatible Ersatzschriften: gleiche Zeichenbreiten, daher gleiche Zeilen- und Seitenumbrüche wie im Original.
ERSATZ = {
    "calibri": ("carlito",), "cambria": ("caladea",), "arial": ("liberation sans", "arimo"), "helvetica": ("liberation sans", "arimo"),
    "times new roman": ("liberation serif", "tinos"), "courier new": ("liberation mono", "cousine"), "arial narrow": ("liberation sans narrow",),
}
_MAX_BYTES = 4 * 1024 * 1024
_DOCX_TEILE = ("word/document.xml", "word/styles.xml", "word/header1.xml", "word/footer1.xml")
_DOCX_MUSTER = re.compile(r'w:(?:ascii|hAnsi)="([^"]+)"')
_ODT_MUSTER = re.compile(r'(?:style:font-name|fo:font-family|svg:font-family|style:font-name-asian)="([^"]+)"')


def _bereinigt(name: str) -> str:
    return name.strip().strip("'\"").strip()


def schriften_aus_datei(pfad: str, endung: str) -> set[str]:
    """Die in einer DOCX-/ODT-Datei angegebenen Schriftnamen (leer bei anderen Formaten oder Fehlern)."""
    endung = endung.lower()
    namen: set[str] = set()
    try:
        with zipfile.ZipFile(pfad) as z:
            if endung == ".docx":
                teile, muster = [t for t in z.namelist() if t in _DOCX_TEILE or re.match(r"word/(header|footer)\d+\.xml$", t)], _DOCX_MUSTER
            elif endung in (".odt", ".ott"):
                teile, muster = [t for t in ("content.xml", "styles.xml") if t in z.namelist()], _ODT_MUSTER
            else:
                return set()
            for t in teile:
                info = z.getinfo(t)
                if info.file_size > _MAX_BYTES:
                    continue
                text = z.read(t).decode("utf-8", "replace")
                namen.update(_bereinigt(n) for n in muster.findall(text))
    except (OSError, zipfile.BadZipFile, KeyError, RuntimeError):
        return set()
    return {n for n in namen if n}


def bewerte(namen) -> tuple[list[str], dict[str, str]]:
    """→ (wirklich fehlende Schriften, {Schrift: installierter metrisch kompatibler Ersatz}). Braucht Qt (QFontDatabase)."""
    from PySide6.QtGui import QFontDatabase
    vorhanden = {f.casefold(): f for f in QFontDatabase.families()}
    fehlend: list[str] = []
    ersatz: dict[str, str] = {}
    for n in sorted({str(x) for x in namen if x}):
        if n.casefold() in vorhanden:
            continue
        treffer = next((vorhanden[a] for a in ERSATZ.get(n.casefold(), ()) if a in vorhanden), None)
        if treffer:
            ersatz[n] = treffer
        else:
            fehlend.append(n)
    return fehlend, ersatz
