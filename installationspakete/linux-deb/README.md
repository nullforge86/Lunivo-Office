# Linux: Debian-/Ubuntu-Paket (.deb)

Ergebnis: `Lunivo-Office_VERSION_amd64.deb` (Version aus `pyproject.toml`).

Das Paket enthält das mit PyInstaller gebaute Programm samt Python und allen Bibliotheken (`/opt/lunivo-office`), einen Starter `/usr/bin/lunivo-office`,
den Menüeintrag `lunivo-writer.desktop` (Name passt zu `setDesktopFileName` im Programm, damit Fenster und Symbol zusammenfinden) und das Programmicon in `hicolor`.
Nur Systembibliotheken für Qt sind als `Depends` eingetragen.

```bash
installationspakete/linux-deb/deb-bauen.sh          # nach: pyinstaller installationspakete/lunivo-office.spec
sudo apt install ./erstellung/Lunivo-Office_0.1.0_amd64.deb
sudo apt remove lunivo-office                        # saubere Deinstallation; Benutzerdaten (~/.local/share) bleiben
```

Desktop-Verknüpfung: Unter Debian/Ubuntu liegt der Menüeintrag im Anwendungsmenü; eine Verknüpfung auf dem Desktop legt man per Rechtsklick „Zum Desktop hinzufügen“ an (Pakete dürfen keine Dateien in Benutzerordner schreiben).

Ohne Installation: `Lunivo-Office_VERSION_linux-portable.tar.gz` entpacken und `lunivo-office/lunivo-office` starten.
Aus dem Quellcode: `./skripte/starten-qt.sh`.
Benutzerdaten: `~/.config/lunivo`, `~/.local/share/Lunivo/Lunivo Writer`, `~/.cache/Lunivo/Lunivo Writer`.
Alle Wege für alle Systeme: `dokumentation/benutzerhandbuch/installation.md`.

Enthalten: die Offline-Übersetzung (Argos) mit den Sprachpaketen Deutsch↔Englisch, siehe `../README.md`.
Nicht enthalten: Stimmen und nachladbare Schriften – sie werden wie bisher separat nachgeladen (`skripte/stimme-holen.sh`, `skripte/schrift-holen.sh`).
Nur `amd64` wird in der CI gebaut.
