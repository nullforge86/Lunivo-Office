"""Prüft den DOCX-Leser (``dienste/docx_dokument_leser``) an den DOCX-Dateien der Prüfdatenbank: Wird die Datei gelesen, und bleibt ihr Text nach dem Schreiben und erneuten
Lesen (Rundlauf über das Dokumentenmodell) derselbe?

    .venv/bin/python werkzeuge/pruefungen/docx_modellleser_vergleich.py [Ordner] [--ab N] [--max N]

Je Datei: ``gleich`` (gelesen, Rundlauf ohne Textabweichung), ``anders`` (Rundlauf ändert den Text), ``abgelehnt`` (der Leser meldet, was er nicht abbilden kann) oder
``Fehler``. Ausgabe als Markdown-Tabelle; kein Bestandteil der Anwendung. Es gibt keinen zweiten Leser als Gegenprobe."""
from __future__ import annotations

import glob
import os
import sys
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from lunivo_writer.dienste.docx_modell_schreiber import docx_dokument_daten  # noqa: E402
from lunivo_writer.dienste.modell_laden import lade_modell  # noqa: E402
from lunivo_writer.modelle.bericht import DocumentIOError  # noqa: E402


def pruefen(pfad: str) -> tuple[str, str]:
    try:
        erst = lade_modell(pfad)
    except DocumentIOError as e:
        return "abgelehnt", str(e)[:120]
    except Exception as e:  # noqa: BLE001
        return "Fehler", f"{type(e).__name__}: {e}"[:80]
    try:
        daten, _bericht = docx_dokument_daten(erst.document, erst.page, erst.meta)
        with tempfile.TemporaryDirectory(prefix="modellleser-") as tmp:
            aus = os.path.join(tmp, "zurueck.docx")
            with open(aus, "wb") as f:
                f.write(daten)
            zweit = lade_modell(aus)
    except Exception as e:  # noqa: BLE001
        return "Fehler", f"Rundlauf: {type(e).__name__}: {e}"[:80]
    a, b = erst.document.text(), zweit.document.text()
    return ("gleich", "") if a == b else ("anders", f"Zeichen {len(a)} → {len(b)}")


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
        if art != "gleich":
            print(f"| {os.path.relpath(f, os.path.expanduser(ordner))[-70:]} | {art} | {grund} |", flush=True)
    print("\n" + ", ".join(f"{k}: {v}" for k, v in sorted(zaehler.items())))
