
#!/usr/bin/env bash
#
# starten-qt.sh — startet Lunivo Writer mit nativer Qt-Oberfläche.
#
# Befehle:
#   ./skripte/starten-qt.sh
#   ./skripte/starten-qt.sh dokument.docx
#   ./skripte/starten-qt.sh --eintrag
#   ./skripte/starten-qt.sh --test
#   ./skripte/starten-qt.sh --weg
#
set -euo pipefail

# Projektordner automatisch ermitteln
HIER="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

VENV="$HIER/.venv"
EINTRAG="$HOME/.local/share/applications/lunivo-writer.desktop"
STARTER="$HOME/.local/bin/lunivo-office"
KONFIG="$HOME/.config/lunivo-office/projektpfad"
ICON="$HIER/ressourcen/symbole/varianten/Abstrakt/icon-256.png"

# --------------------------------------------------
# Menüeintrag entfernen
# --------------------------------------------------

if [[ "${1:-}" == "--weg" ]]; then
    rm -f "$EINTRAG"
    rm -f "$STARTER"
    rm -f "$KONFIG"

    echo "Lunivo Office wurde aus dem Anwendungsmenü entfernt."
    echo "Projekt, Python-Umgebung und Dokumente bleiben erhalten."
    exit 0
fi

# --------------------------------------------------
# Menüeintrag erstellen
# --------------------------------------------------

if [[ "${1:-}" == "--eintrag" ]]; then

    mkdir -p "$(dirname "$EINTRAG")"
    mkdir -p "$(dirname "$STARTER")"
    mkdir -p "$(dirname "$KONFIG")"

    # Aktuellen Projektordner speichern
    printf '%s\n' "$HIER" > "$KONFIG"

    # Universellen Starter erstellen
    cat > "$STARTER" <<'STARTSCRIPT'
#!/usr/bin/env bash
set -euo pipefail

KONFIG="$HOME/.config/lunivo-office/projektpfad"

if [[ ! -f "$KONFIG" ]]; then
    echo "Lunivo Office: Projektkonfiguration fehlt." >&2
    exit 1
fi

IFS= read -r PROJEKT < "$KONFIG"

SKRIPT="$PROJEKT/skripte/starten-qt.sh"

if [[ ! -f "$SKRIPT" ]]; then
    echo "Lunivo Office: Projekt nicht gefunden: $PROJEKT" >&2
    echo "Bitte den Menüeintrag am neuen Projektort erneut einrichten." >&2
    exit 1
fi

exec bash "$SKRIPT" "$@"
STARTSCRIPT

    chmod +x "$STARTER"

    # Desktop-Datei erstellen
    cat > "$EINTRAG" <<DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=Lunivo Office
GenericName=Textverarbeitung
Comment=Lunivo Writer mit nativer Qt-Oberfläche
Exec=$STARTER %F
Icon=$ICON
Terminal=false
StartupNotify=true
StartupWMClass=lunivo-writer
Categories=Office;WordProcessor;
MimeType=application/vnd.openxmlformats-officedocument.wordprocessingml.document;text/plain;
DESKTOP

    chmod 644 "$EINTRAG"

    echo "Lunivo Office wurde eingerichtet."
    echo "Projekt: $HIER"
    echo "Starter: $STARTER"
    echo "Menüeintrag: $EINTRAG"

    shift

    # Nur einrichten, falls keine weiteren Argumente
    if [[ $# -eq 0 ]]; then
        exit 0
    fi
fi

# --------------------------------------------------
# Python überprüfen
# --------------------------------------------------

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 fehlt." >&2
    echo "Installation: sudo apt install python3 python3-venv" >&2
    exit 1
fi

if ! python3 -c \
    'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "Python 3.10 oder neuer wird benötigt." >&2
    exit 1
fi

if ! python3 -c 'import venv, ensurepip' 2>/dev/null; then
    echo "python3-venv fehlt." >&2
    echo "Installation: sudo apt install python3-venv" >&2
    exit 1
fi

# --------------------------------------------------
# Virtuelle Python-Umgebung
# --------------------------------------------------

if [[ ! -x "$VENV/bin/python" ]]; then
    echo "Erstelle virtuelle Python-Umgebung ..."
    python3 -m venv "$VENV"
fi

# --------------------------------------------------
# Abhängigkeiten installieren
# --------------------------------------------------

if ! "$VENV/bin/python" -c \
    'import PySide6, docx, pypdf' 2>/dev/null; then

    echo "Installiere benötigte Python-Pakete ..."

    "$VENV/bin/python" -m pip install \
        --quiet --upgrade pip

    if ! "$VENV/bin/python" -m pip install \
        --quiet -r "$HIER/requirements.txt"; then

        echo "Installation fehlgeschlagen." >&2
        echo "Bitte Internetverbindung überprüfen." >&2
        exit 1
    fi
fi

# --------------------------------------------------
# Tests ausführen
# --------------------------------------------------

if [[ "${1:-}" == "--test" ]]; then

    echo "Starte Lunivo-Writer-Tests ..."

    "$VENV/bin/python" -m pip install \
        --quiet -r "$HIER/requirements-dev.txt"

    cd "$HIER"

    QT_QPA_PLATFORM=offscreen \
        exec "$VENV/bin/python" -m pytest tests -q
fi

# --------------------------------------------------
# Zugriffsrechte der Quellordner reparieren
# --------------------------------------------------

if [[ -d "$HIER/src" ]]; then

    find "$HIER/src" \
        -type d \
        ! -perm -u+rwx \
        -exec chmod u+rwx {} + \
        2>/dev/null || true

fi

# --------------------------------------------------
# Verdächtige Dateien melden
# --------------------------------------------------

if [[ -d "$HIER/src" ]]; then

    while IFS= read -r -d '' DATEI; do
        echo "Hinweis: Möglicherweise unerwünschte Datei:" >&2
        echo "$DATEI" >&2
    done < <(
        find "$HIER/src" \
            -maxdepth 4 \
            -type f \
            ! -name '*.*' \
            -size +1M \
            -print0 2>/dev/null
    )

fi

# --------------------------------------------------
# Lunivo Writer starten
# --------------------------------------------------

cd "$HIER"

export PYTHONPATH="$HIER/src"

exec "$VENV/bin/python" "$(dirname "$0")/../main.py" "$@"

