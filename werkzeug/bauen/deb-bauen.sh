#!/usr/bin/env bash
#
# deb-bauen.sh — baut genau EINE .deb von Lunivo Office.
#
#   Anwendung  /opt/stevie-empire/lunivo-office/   (Quelltext, eigene Python-Umgebung, Sprachpakete in argos/)
#   Starter    /usr/share/applications/stevie-lunivo-office.desktop
#   Symlink    /usr/bin/lunivo-office
#   Benutzerdaten nur in XDG-Verzeichnissen (das Programm schreibt nie nach /opt; Argos-Pakete landen unter data_dir()/argos-pakete).
#
#   werkzeug/bauen/deb-bauen.sh [VERSION]      Ergebnis: build/lunivo-office_VERSION_ARCH.deb
#
# Braucht Internet (pip, Argos-Sprachpakete) und dpkg-deb. Wird vom Eigentümer ausgeführt, nicht von der CI.
set -euo pipefail
HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VERSION="${1:-$(sed -n 's/^version *= *"\(.*\)"/\1/p' "$HIER/pyproject.toml" | head -1)}"
ARCH="$(dpkg --print-architecture)"
APP=/opt/stevie-empire/lunivo-office
BAU="$HIER/build/deb"
ROOT="$BAU/lunivo-office_${VERSION}_${ARCH}"
SPRACHEN="$HIER/build/argos-modelle"          # nicht im Repository (build/ ist kein Quellordner)

command -v dpkg-deb >/dev/null || { echo "dpkg-deb fehlt (Paket dpkg)." >&2; exit 1; }
command -v python3 >/dev/null || { echo "python3 fehlt." >&2; exit 1; }

rm -rf "$ROOT"
mkdir -p "$ROOT/DEBIAN" "$ROOT$APP" "$ROOT/usr/bin" "$ROOT/usr/share/applications"

# 1. Programm: nur der Quelltext und die Dateien, die er braucht
cp -r "$HIER/src" "$ROOT$APP/src"
cp -r "$HIER/assets" "$ROOT$APP/assets"
find "$ROOT$APP" -name __pycache__ -type d -prune -exec rm -rf {} +

# 2. Eigene Python-Umgebung am Zielort-Namen. --copies: kein Verweis auf das Bauverzeichnis.
python3 -m venv --copies "$ROOT$APP/venv"
VPY="$ROOT$APP/venv/bin/python"
"$VPY" -m pip install --quiet --upgrade pip
# torch NUR als CPU-Version: Argos zieht torch über stanza nach. Der Standard-Wheel von PyPI bringt CUDA-Bibliotheken mit
# (mehrere GB). Lunivo übersetzt auf der CPU; die CPU-Version ist einige hundert MB groß. Darum zuerst von der CPU-Quelle,
# damit pip die schon erfüllte Abhängigkeit nicht durch die CUDA-Version ersetzt.
"$VPY" -m pip install --quiet torch --index-url https://download.pytorch.org/whl/cpu
"$VPY" -m pip install --quiet -r "$HIER/requirements.txt" argostranslate
if "$VPY" -m pip list 2>/dev/null | grep -qi '^nvidia-'; then
  echo "Abbruch: CUDA-Pakete (nvidia-*) in der Umgebung — torch ist nicht die CPU-Version." >&2; exit 1
fi
# Pfade des Bauverzeichnisses aus Startskripten der Umgebung entfernen (Aufruf läuft über python -m, nicht über bin/*)
grep -rIl "$ROOT" "$ROOT$APP/venv/bin" 2>/dev/null | xargs -r sed -i "s#$ROOT##g"

# 3. Sprachpakete Deutsch<->Englisch (alle anderen Sprachen lädt das Programm nur auf Wunsch)
"$HIER/werkzeug/bauen/argos-holen.sh" "$SPRACHEN" "$VPY"
mkdir -p "$ROOT$APP/argos"
cp "$SPRACHEN"/*.argosmodel "$ROOT$APP/argos/"

# 4. Starter, Symlink, Menüeintrag
cat > "$ROOT$APP/lunivo-office" <<'S'
#!/bin/sh
D=/opt/stevie-empire/lunivo-office
PYTHONPATH="$D/src" exec "$D/venv/bin/python" -m lunivo_writer "$@"
S
chmod 755 "$ROOT$APP/lunivo-office"
ln -s "$APP/lunivo-office" "$ROOT/usr/bin/lunivo-office"
cat > "$ROOT/usr/share/applications/stevie-lunivo-office.desktop" <<D
[Desktop Entry]
Type=Application
Name=Lunivo Office
Comment=Textverarbeitung
Exec=lunivo-office %F
Icon=$APP/assets/symbole/varianten/Abstrakt/icon-256.png
Terminal=false
StartupWMClass=Lunivo Writer
Categories=Office;WordProcessor;
MimeType=application/vnd.openxmlformats-officedocument.wordprocessingml.document;text/plain;
D

# 5. Paketangaben
GROESSE="$(du -sk "$ROOT" | cut -f1)"
cat > "$ROOT/DEBIAN/control" <<C
Package: lunivo-office
Version: $VERSION
Section: editors
Priority: optional
Architecture: $ARCH
Depends: python3 (>= 3.10), libxcb-cursor0, libgl1
Installed-Size: $GROESSE
Maintainer: Kay Siebke
Description: Lunivo Office - native Textverarbeitung (Python, Qt)
 Enthält die lokale Offline-Übersetzung Deutsch und Englisch.
 Weitere Sprachen lädt das Programm nur auf ausdrücklichen Wunsch.
C
find "$ROOT" -type d -exec chmod 755 {} +
dpkg-deb --root-owner-group --build "$ROOT" "$HIER/build/lunivo-office_${VERSION}_${ARCH}.deb"
echo "Fertig: $HIER/build/lunivo-office_${VERSION}_${ARCH}.deb"
