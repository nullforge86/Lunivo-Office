
#!/usr/bin/env python3
"""
Lunivo Office – Diagnose des möglichen Textverlusts.
Liest Projektdateien und protokolliert Hinweise.
Ändert keine Quelldateien und startet Lunivo Office nicht automatisch.
"""

from pathlib import Path
import os
import platform
import subprocess
import sys
from datetime import datetime

LOG = Path("lunivo_diagnose.log")
ROOT = Path.cwd()

SUCHBEGRIFFE = (
    "_seitenfluss",
    "contentsChanged",
    "QTimer",
    "setPageSize",
    "setPlainText",
    "clear()",
    "removeSelectedText",
    "deleteChar",
    "undo()",
)

def protokoll(text):
    print(text)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(text + "\n")

def ausfuehren(cmd):
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return (result.stdout + result.stderr).strip()
    except Exception as e:
        return f"Fehler: {e}"

def main():
    LOG.write_text(
        f"Lunivo-Diagnose\n"
        f"Zeit: {datetime.now().isoformat()}\n"
        f"System: {platform.platform()}\n"
        f"Python: {sys.version}\n"
        f"Projektordner: {ROOT}\n\n",
        encoding="utf-8",
    )

    protokoll("=== GIT STATUS ===")
    protokoll(ausfuehren(["git", "status", "--short"]))

    protokoll("\n=== PYTHON-UMGEBUNG ===")
    protokoll(f"Python-Pfad: {sys.executable}")
    protokoll(f"VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'nicht gesetzt')}")

    protokoll("\n=== MÖGLICHE STARTDATEIEN ===")
    startdateien = (
        "main.py",
        "run.py",
        "app.py",
        "__main__.py",
        "pyproject.toml",
        "README.md",
    )

    for name in startdateien:
        datei = ROOT / name
        if datei.is_file():
            protokoll(f"Gefunden: {datei}")

    protokoll("\n=== DIAGNOSE RELEVANTER QUELLCODE ===")
    src = ROOT / "src"

    if not src.exists():
        protokoll("Kein src/-Ordner gefunden.")
        protokoll("Bitte das Skript im Lunivo-Office-Projektordner starten.")
        return

    dateien = list(src.rglob("*.py"))

    for datei in dateien:
        try:
            zeilen = datei.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            protokoll(f"Datei nicht lesbar: {datei}: {e}")
            continue

        treffer = []
        for nummer, zeile in enumerate(zeilen, start=1):
            if any(begriff in zeile for begriff in SUCHBEGRIFFE):
                treffer.append((nummer, zeile.strip()))

        if treffer:
            protokoll(f"\nDatei: {datei}")
            for nummer, zeile in treffer:
                protokoll(f"  Zeile {nummer}: {zeile}")

    protokoll("\n=== ENDE ===")
    protokoll(f"Diagnose gespeichert in: {LOG.resolve()}")

if __name__ == "__main__":
    main()

