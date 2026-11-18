#!/usr/bin/env bash
# Baut Lunivo-Office_VERSION_macOS.dmg aus dist/"Lunivo Office.app" (PyInstaller). Nur unter macOS lauffähig.
# Optional (siehe README.md): APPLE_SIGN_IDENTITY="Developer ID Application: …" signiert die .app.
set -euo pipefail
HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VERSION="${1:-$(sed -n 's/^version *= *"\(.*\)"/\1/p' "$HIER/pyproject.toml" | head -1)}"
APP="$HIER/dist/Lunivo Office.app"
[ -d "$APP" ] || { echo "Fehlt: $APP (erst PyInstaller ausführen)." >&2; exit 1; }
if [ -n "${APPLE_SIGN_IDENTITY:-}" ]; then
  codesign --force --deep --options runtime --timestamp --sign "$APPLE_SIGN_IDENTITY" "$APP"
else
  codesign --force --deep --sign - "$APP"          # Ad-hoc-Signatur: nötig, damit Apple-Silicon-Macs die App überhaupt starten
fi
STAGE="$HIER/erstellung/dmg"
rm -rf "$STAGE"; mkdir -p "$STAGE"
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
AUS="$HIER/erstellung/Lunivo-Office_${VERSION}_macOS.dmg"
rm -f "$AUS"
hdiutil create -volname "Lunivo Office" -srcfolder "$STAGE" -ov -format UDZO "$AUS"
if [ -n "${APPLE_SIGN_IDENTITY:-}" ]; then codesign --force --sign "$APPLE_SIGN_IDENTITY" --timestamp "$AUS"; fi
if [ -n "${APPLE_ID:-}" ] && [ -n "${APPLE_TEAM_ID:-}" ] && [ -n "${APPLE_APP_PASSWORD:-}" ]; then
  xcrun notarytool submit "$AUS" --apple-id "$APPLE_ID" --team-id "$APPLE_TEAM_ID" --password "$APPLE_APP_PASSWORD" --wait
  xcrun stapler staple "$AUS"
fi
echo "Fertig: $AUS"
