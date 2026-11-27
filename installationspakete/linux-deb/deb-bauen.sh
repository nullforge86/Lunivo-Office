#!/usr/bin/env bash
# Baut Lunivo-Office_VERSION_ARCH.deb aus dem PyInstaller-Ergebnis (dist/lunivo-office).
# Voraussetzung: im Projektwurzelordner wurde  pyinstaller installationspakete/lunivo-office.spec  ausgeführt
#                und  python installationspakete/icons_erzeugen.py.
# Aufruf: installationspakete/linux-deb/deb-bauen.sh [VERSION]    Ergebnis: erstellung/Lunivo-Office_VERSION_ARCH.deb
set -euo pipefail
HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VERSION="${1:-$(sed -n 's/^version *= *"\(.*\)"/\1/p' "$HIER/pyproject.toml" | head -1)}"
ARCH="$(dpkg --print-architecture)"
QUELLE="$HIER/dist/lunivo-office"
[ -x "$QUELLE/lunivo-office" ] || { echo "Fehlt: $QUELLE/lunivo-office (erst PyInstaller ausführen)." >&2; exit 1; }
ROOT="$HIER/erstellung/deb/lunivo-office_${VERSION}_${ARCH}"
APP=/opt/lunivo-office
rm -rf "$ROOT"
mkdir -p "$ROOT/DEBIAN" "$ROOT$APP" "$ROOT/usr/bin" "$ROOT/usr/share/applications" "$ROOT/usr/share/doc/lunivo-office"
cp -a "$QUELLE/." "$ROOT$APP/"
ln -s "$APP/lunivo-office" "$ROOT/usr/bin/lunivo-office"
cp "$HIER/LICENSE" "$ROOT/usr/share/doc/lunivo-office/copyright"

# Programmicon in allen Größen (hicolor), damit Menü, Dock und Desktop-Verknüpfung es finden
for px in 16 24 32 48 64 128 256 512; do
  q="$HIER/ressourcen/symbole/varianten/Abstrakt/icon-$px.png"
  [ -f "$q" ] || continue
  mkdir -p "$ROOT/usr/share/icons/hicolor/${px}x${px}/apps"
  cp "$q" "$ROOT/usr/share/icons/hicolor/${px}x${px}/apps/lunivo-office.png"
done

cat > "$ROOT/usr/share/applications/lunivo-writer.desktop" <<D
[Desktop Entry]
Type=Application
Name=Lunivo Office
GenericName=Textverarbeitung
Comment=Textverarbeitung mit DOCX-Unterstützung
Exec=lunivo-office %F
Icon=lunivo-office
Terminal=false
StartupWMClass=lunivo-writer
Categories=Office;WordProcessor;
MimeType=application/vnd.openxmlformats-officedocument.wordprocessingml.document;
D

cat > "$ROOT/DEBIAN/postinst" <<'P'
#!/bin/sh
set -e
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database -q /usr/share/applications || true
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
exit 0
P
cp "$ROOT/DEBIAN/postinst" "$ROOT/DEBIAN/postrm"
chmod 755 "$ROOT/DEBIAN/postinst" "$ROOT/DEBIAN/postrm"

GROESSE="$(du -sk "$ROOT" | cut -f1)"
cat > "$ROOT/DEBIAN/control" <<C
Package: lunivo-office
Version: $VERSION
Section: editors
Priority: optional
Architecture: $ARCH
Depends: libc6, libgl1, libegl1, libxkbcommon0, libxkbcommon-x11-0, libxcb-cursor0, libxcb-icccm4, libxcb-image0, libxcb-keysyms1, libxcb-render-util0, libxcb-shape0, libdbus-1-3, libfontconfig1
Installed-Size: $GROESSE
Maintainer: Lunivo <noreply@lunivo.invalid>
Homepage: https://github.com/nullforge86/Lunivo-Office
Description: Lunivo Office - Textverarbeitung
 Native Textverarbeitung (Python, Qt) mit DOCX-Unterstützung.
 Python und alle Bibliotheken sind im Paket enthalten.
C
find "$ROOT" -type d -exec chmod 755 {} +
find "$ROOT" -type f -exec chmod go-w {} +
mkdir -p "$HIER/erstellung"
AUS="$HIER/erstellung/Lunivo-Office_${VERSION}_${ARCH}.deb"
dpkg-deb --root-owner-group -Zgzip --build "$ROOT" "$AUS"
echo "Fertig: $AUS"
