# macOS: Disk-Image (.dmg)

Ergebnis: `Lunivo-Office_VERSION_macOS.dmg` (Apple Silicon, arm64) und `Lunivo-Office_VERSION_macOS_Intel.dmg` (x86_64). Je ein `Lunivo Office.app` (PyInstaller, Python eingebettet) plus Verknüpfung auf „Programme“ – App per Ziehen installieren.
Das Icon (`.icns`) wird aus `ressourcen/symbole/varianten/Abstrakt/icon-1024.png` erzeugt. Ein einziges Universal-Binary wird nicht gebaut, weil nicht alle Abhängigkeiten (z. B. `uharfbuzz`, `freetype-py`, `lxml`) als universal2-Wheels vorliegen; die Intel-Variante ist in der CI optional.

```bash
python3 -m pip install -r requirements.txt pyinstaller pillow
python3 installationspakete/icons_erzeugen.py
pyinstaller installationspakete/lunivo-office.spec --noconfirm
installationspakete/macos/dmg-bauen.sh
```

Ohne Installation: `…_portable.zip` entpacken und die `.app` per Rechtsklick → „Öffnen“ starten.

## Code-Signierung und Notarisierung
Ohne Apple-Developer-Konto (99 USD/Jahr) wird die App nur ad-hoc signiert; Gatekeeper warnt beim ersten Start (Rechtsklick → Öffnen, oder `xattr -dr com.apple.quarantine "/Applications/Lunivo Office.app"`).
Für Weitergabe ohne Warnung:
1. Zertifikat „Developer ID Application“ erzeugen, als `.p12` exportieren und in der CI in eine Keychain importieren.
2. Umgebungsvariablen bzw. GitHub-Secrets setzen: `APPLE_SIGN_IDENTITY`, `APPLE_ID`, `APPLE_TEAM_ID`, `APPLE_APP_PASSWORD` (app-spezifisches Passwort). `dmg-bauen.sh` signiert dann mit Hardened Runtime, notarisiert per `notarytool` und heftet das Ticket an (`stapler`).
3. Der Workflow enthält den Keychain-Import **nicht**; er muss mit dem eigenen Zertifikat ergänzt werden. Eventuell sind Entitlements nötig (nicht getestet).
