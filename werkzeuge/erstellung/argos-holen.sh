#!/usr/bin/env bash
#
# argos-holen.sh — lädt die Argos-Sprachpakete Englisch→Deutsch und Deutsch→Englisch (.argosmodel) in einen Ordner.
#
# Läuft zur BAUZEIT (von deb-bauen.sh aufgerufen), nicht beim Benutzer. Die Dateien werden nicht ins Repository eingecheckt.
# Alle anderen Sprachen sind optional und werden nur auf Wunsch im Programm nachgeladen.
#
#   werkzeuge/erstellung/argos-holen.sh ZIELORDNER [PYTHON]    PYTHON braucht argostranslate (Standard: .venv/bin/python)
set -euo pipefail
HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ZIEL="${1:?Aufruf: argos-holen.sh ZIELORDNER [PYTHON]}"
PY="${2:-$HIER/.venv/bin/python}"
"$PY" -c 'import argostranslate' 2>/dev/null || { echo "argostranslate fehlt in $PY." >&2; exit 1; }
mkdir -p "$ZIEL"
"$PY" -I - "$ZIEL" <<'PY'
import os, shutil, sys
import argostranslate.package as p

ziel = sys.argv[1]
p.update_package_index()
verfuegbar = p.get_available_packages()
for von, nach in (("en", "de"), ("de", "en")):
    pk = next((x for x in verfuegbar if x.from_code == von and x.to_code == nach), None)
    if pk is None:
        sys.exit(f"Kein Sprachpaket {von} -> {nach} im Argos-Verzeichnis gefunden.")
    pfad = pk.download()
    shutil.copy(pfad, os.path.join(ziel, f"{von}_{nach}.argosmodel"))
    print(f"{von} -> {nach}: geladen")
PY
ls -l "$ZIEL"
