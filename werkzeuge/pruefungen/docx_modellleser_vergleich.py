"""Vergleicht den DOCX-Modell-Leser (``dienste/docx_modell_leser``) mit dem alten Leser (``docx_leser.read_docx``) an den DOCX-Dateien der Prüfdatenbank.

    .venv/bin/python werkzeuge/pruefungen/docx_modellleser_vergleich.py [Ordner] [--ab N] [--max N]

Je Datei: ``direkt`` (Modell-Leser, gleich dem alten Leser in Text, Formaten, Listen, Tabellen, Rahmen und Bildern), ``anders`` (Modell-Leser liest, Ergebnis weicht ab), ``Rückfall``
(der Modell-Leser meldet ``NichtImModell`` mit Grund) oder ``Fehler``. Ausgabe als Markdown-Tabelle; kein Bestandteil der Anwendung."""
from __future__ import annotations

import glob
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtGui import QGuiApplication  # noqa: E402

app = QGuiApplication.instance() or QGuiApplication([])

from lunivo_writer.adapter.qt.dokument import document_from_qt, document_to_qt, vergleichen  # noqa: E402
from lunivo_writer.dienste import docx_leser, docx_modell_leser as M  # noqa: E402


def pruefen(pfad: str) -> tuple[str, str]:
    try:
        neu = M._ModellReader(pfad).run_modell()
    except M.NichtImModell as e:
        return "Rückfall", str(e)
    except Exception as e:  # noqa: BLE001
        return "Fehler", f"{type(e).__name__}: {e}"[:80]
    try:
        alt_doc, alt_seite, *_ = docx_leser.read_docx(pfad)
        unterschiede = vergleichen(alt_doc, document_to_qt(neu[0]))
    except Exception as e:  # noqa: BLE001
        return "Fehler", f"Vergleich: {type(e).__name__}: {e}"[:80]
    return ("direkt", "") if not unterschiede else ("anders", unterschiede[0][:400])


if __name__ == "__main__":
    ordner = next((a for a in sys.argv[1:] if not a.startswith("--") and not a.isdigit()), "~/Lunivo-Testdateien")
    ab = int(sys.argv[sys.argv.index("--ab") + 1]) if "--ab" in sys.argv else 0
    maximal = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 100000
    dateien = sorted(f for f in glob.glob(os.path.join(os.path.expanduser(ordner), "**", "*.docx"), recursive=True))[ab:ab + maximal]
    zaehler: dict[str, int] = {}
    print("| Datei | Ergebnis | Grund |\n|---|---|---|")
    for f in dateien:
        art, grund = pruefen(f)
        zaehler[art] = zaehler.get(art, 0) + 1
        if art != "direkt":
            print(f"| {os.path.relpath(f, os.path.expanduser(ordner))[-70:]} | {art} | {grund} |", flush=True)
    print("\n" + ", ".join(f"{k}: {v}" for k, v in sorted(zaehler.items())))
