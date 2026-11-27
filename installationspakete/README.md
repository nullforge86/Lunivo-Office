# Installationspakete

Gemeinsam: `lunivo-office.spec` (PyInstaller, Einstieg `main.py`) und `icons_erzeugen.py` (`.ico`/`.icns` aus dem Programmsymbol).
Je Betriebssystem: `linux-deb/`, `windows/`, `macos/`. Gebaut wird in GitHub Actions (`.github/workflows/build-installers.yml`); Artefakte erscheinen im Lauf, bei veröffentlichtem Release auch als Release-Assets. Ergebnisse landen lokal in `erstellung/` (nicht im Repository).

## Zusatzpakete
Die Offline-Übersetzung (Argos, mit CPU-torch) und die Sprachpakete Deutsch↔Englisch sind **eingebaut**: `argostranslate` und Abhängigkeiten über die Spezifikation, die `.argosmodel`-Dateien aus `werkzeuge/erstellung/argos-holen.sh` im Ordner `argos/` neben dem Programm (macOS: `Contents/argos`), wo das Modul `src/system/pfade` (`argos_dirs`) sie sucht.
Das Modul `system.pfade` ist der eine Eingang für alle Orte: Es erkennt Benutzerordner je Betriebssystem (Linux XDG, Windows `%APPDATA%`/`%LOCALAPPDATA%`, macOS `~/Library`) und sucht jedes Zusatzpaket im Benutzerordner (`lunivo-office/<paket>`), beim Programm (`<paket>/` neben dem Programm) und in den Ordnern der Umgebungsvariablen `LUNIVO_ZUSATZPAKETE`.
Folge: Pakete sind groß (lokal: Linux-`.deb` ca. 760 MB, entpackt ca. 1,5 GB). Weitere Sprachen lädt das Programm bei Bedarf nach.
Nicht enthalten: Piper-Stimmen und nachladbare Schriften (`skripte/stimme-holen.sh`, `schrift-holen.sh` sind Linux-Shellskripte).
