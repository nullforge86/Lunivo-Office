"""Vergleicht die Seitenzahl des Qt-freien Seitenumbruchs (``core.layout`` mit HarfBuzz/FreeType) mit der des Seitenlaufs (Qt) an den Dateien der Prüfdatenbank.

    .venv/bin/python werkzeuge/pruefungen/seitenumbruch_modell_vergleich.py [Ordner] [--ab N] [--max N]   (große Ordner in Abschnitten: ein einzelnes Riesenbild kann Qt abstürzen lassen)

Ausgabe als Markdown-Tabelle auf der Standardausgabe. Dient zum Abgleich beim Weiterentwickeln des Qt-freien Umbruchs; kein Bestandteil der Anwendung."""
from __future__ import annotations

import glob
import os
import sys
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtGui import QGuiApplication  # noqa: E402

app = QGuiApplication.instance() or QGuiApplication([])

from lunivo_writer.core.layout import umbrechen  # noqa: E402
from lunivo_writer.core.textlayout.hb_engine import HarfBuzzEngine  # noqa: E402
from lunivo_writer.dienste.modell_laden import lade_modell  # noqa: E402
from lunivo_writer.dienste import datei_dienst  # noqa: E402
from lunivo_writer.editor.seite.seiten_aufteilung import paginated_copy  # noqa: E402

ENDUNGEN = (".docx", ".odt", ".rtf", ".txt")


def vergleichen(ordner: str, maximal: int, ab: int = 0) -> list[tuple]:
    eng = HarfBuzzEngine()
    dateien = sorted(f for f in glob.glob(os.path.join(os.path.expanduser(ordner), "**", "*"), recursive=True) if f.lower().endswith(ENDUNGEN))[ab:ab + maximal]
    res = []
    for f in dateien:
        try:
            g = datei_dienst.load(f)
            qt = paginated_copy(g.doc, g.page).pageCount()
            from lunivo_writer.adapter.qt.dokument import document_from_qt
            modell = document_from_qt(g.doc, g.page)
            t0 = time.time()
            erg = umbrechen(modell, eng)
            res.append((os.path.relpath(f, os.path.expanduser(ordner)), qt, len(erg.seiten), time.time() - t0, ",".join(erg.hinweise)))
        except Exception as e:  # noqa: BLE001
            res.append((os.path.relpath(f, os.path.expanduser(ordner)), -1, -1, 0.0, f"Fehler: {type(e).__name__}: {e}"[:80]))
    return res


if __name__ == "__main__":
    ordner = next((a for a in sys.argv[1:] if not a.startswith("--") and not a.isdigit()), "~/Lunivo-Testdateien")
    maximal = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 10_000
    ab = int(sys.argv[sys.argv.index("--ab") + 1]) if "--ab" in sys.argv else 0
    zeilen = vergleichen(ordner, maximal, ab)
    gleich = sum(1 for z in zeilen if z[1] == z[2])
    print("| Datei | Qt | Modell | Sekunden | Hinweise |\n|---|---|---|---|---|")
    for z in zeilen:
        print(f"| {z[0]} | {z[1]} | {z[2]} | {z[3]:.2f} | {z[4]} |")
    nah = sum(1 for z in zeilen if z[1] > 0 and abs(z[1] - z[2]) <= max(1, round(z[1] * 0.1)))
    print(f"\nSeitenzahl gleich: {gleich} von {len(zeilen)}; innerhalb 10 %: {nah}")
