"""Vergleicht die Seitenzahl der Layout-Engine des Kerns (``core.layout.LayoutEngine`` mit HarfBuzz/FreeType) mit der Seitenzahl, die das Textprogramm der Datei selbst
vermerkt hat (DOCX: ``docProps/app.xml``, Eintrag ``Pages``), an den Dateien der Prüfdatenbank.

    .venv/bin/python werkzeuge/pruefungen/seitenumbruch_modell_vergleich.py [Ordner] [--ab N] [--max N]

Ausgabe als Markdown-Tabelle auf der Standardausgabe. Dient zum Abgleich beim Weiterentwickeln des Umbruchs; kein Bestandteil der Anwendung. Dateien ohne vermerkte
Seitenzahl (ODT, RTF, TXT, DOCX ohne ``Pages``) erscheinen mit ``-``. Es gibt keinen zweiten Seitenumbruch als Gegenprobe."""
from __future__ import annotations

import glob
import os
import re
import sys
import time
import zipfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from core.layout import LayoutEngine  # noqa: E402
from core.formatierung.schrift import HarfBuzzEngine  # noqa: E402
from framework.dokumentverwaltung.dateizugriff.modell_laden import lade_modell  # noqa: E402

ENDUNGEN = (".docx", ".odt", ".rtf", ".txt")


def vermerkte_seiten(pfad: str) -> int | None:
    """Die Seitenzahl, die das Textprogramm in die DOCX-Datei geschrieben hat; sonst ``None``."""
    if not pfad.lower().endswith(".docx"):
        return None
    try:
        with zipfile.ZipFile(pfad) as z:
            m = re.search(rb"<Pages>(\d+)</Pages>", z.read("docProps/app.xml"))
        return int(m.group(1)) if m else None
    except (OSError, KeyError, zipfile.BadZipFile):
        return None


def vergleichen(ordner: str, maximal: int, ab: int = 0) -> list[tuple]:
    layout = LayoutEngine(HarfBuzzEngine())
    dateien = sorted(f for f in glob.glob(os.path.join(os.path.expanduser(ordner), "**", "*"), recursive=True) if f.lower().endswith(ENDUNGEN))[ab:ab + maximal]
    res = []
    for f in dateien:
        name = os.path.relpath(f, os.path.expanduser(ordner))
        try:
            g = lade_modell(f)
            t0 = time.time()
            erg = layout.berechnen(g.document)
            res.append((name, vermerkte_seiten(f), len(erg.seiten), time.time() - t0, ",".join(erg.hinweise)))
        except Exception as e:  # noqa: BLE001
            res.append((name, None, -1, 0.0, f"Fehler: {type(e).__name__}: {e}"[:80]))
    return res


if __name__ == "__main__":
    ordner = next((a for a in sys.argv[1:] if not a.startswith("--") and not a.isdigit()), "~/Lunivo-Testdateien")
    maximal = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 10_000
    ab = int(sys.argv[sys.argv.index("--ab") + 1]) if "--ab" in sys.argv else 0
    zeilen = vergleichen(ordner, maximal, ab)
    print("| Datei | vermerkt | Kern | Sekunden | Hinweise |\n|---|---|---|---|---|")
    for z in zeilen:
        print(f"| {z[0]} | {z[1] if z[1] is not None else '-'} | {z[2]} | {z[3]:.2f} | {z[4]} |")
    mit = [z for z in zeilen if z[1] is not None and z[2] > 0]
    gleich = sum(1 for z in mit if z[1] == z[2])
    nah = sum(1 for z in mit if abs(z[1] - z[2]) <= max(1, round(z[1] * 0.1)))
    print(f"\nMit vermerkter Seitenzahl: {len(mit)}; gleich: {gleich}; innerhalb 10 %: {nah}")
