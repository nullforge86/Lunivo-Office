# Installation und Start

Lunivo Writer läuft unter Linux, Windows und macOS. Es gibt je Betriebssystem drei Wege:

| Weg | Linux | Windows | macOS |
|---|---|---|---|
| Installieren | `.deb`-Paket | `Setup.exe` | `.dmg` |
| Ohne Installation testen | portables `tar.gz` | portables `zip` | portables `zip` mit der App |
| Aus dem Quellcode starten | `./skripte/starten-qt.sh` | `python main.py` | `python3 main.py` |

Die Pakete und portablen Archive bringen Python und alle Bibliotheken mit; auf dem Rechner muss dafür nichts vorinstalliert sein. Sie entstehen in GitHub Actions (Artefakte des Laufs „Installationspakete bauen“, bei einem Release als Release-Dateien). Wie sie gebaut werden, steht in `installationspakete/README.md`.

**Stand der Erprobung:** Linux ist getestet. Die Pakete für Windows und macOS sind vorbereitet, aber noch nicht auf echten Rechnern erprobt.

## Linux (Debian, Ubuntu, Mint)

### Installieren

```bash
sudo apt install ./Lunivo-Office_0.1.0_amd64.deb
```

Das Programm liegt danach unter `/opt/lunivo-office`, im Anwendungsmenü steht „Lunivo Office“, im Terminal startet `lunivo-office`. Entfernen:

```bash
sudo apt remove lunivo-office
```

Benutzerdaten bleiben dabei erhalten.

### Ohne Installation testen

```bash
tar -xzf Lunivo-Office_0.1.0_linux-portable.tar.gz
./lunivo-office/lunivo-office
```

Der entpackte Ordner kann überall liegen und wird zum Entfernen einfach gelöscht. Auf dem System müssen die Qt-Bibliotheken vorhanden sein:

```bash
sudo apt install libxcb-cursor0 libegl1 libgl1 libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-shape0
```

### Aus dem Quellcode starten

Benötigt Python 3.10 oder neuer. Der Start richtet eine eigene `.venv` im Projektordner ein; das System-Python wird nicht verändert.

```bash
sudo apt install python3 python3-venv libxcb-cursor0 libegl1 libxkbcommon-x11-0 libxcb-icccm4 libxcb-keysyms1 libxcb-shape0
./skripte/starten-qt.sh
```

Beim ersten Start lädt das Skript die Abhängigkeiten aus `requirements.txt`; dafür wird einmalig eine Internetverbindung benötigt. Eine Datei kann direkt angegeben werden:

```bash
./skripte/starten-qt.sh brief.docx
```

Mit `./skripte/starten-qt.sh --eintrag` wird Lunivo im Anwendungsmenü eingetragen. `./skripte/starten-qt.sh --weg` entfernt den Menüeintrag, aber nicht die virtuelle Umgebung oder Dokumente.

## Windows

### Installieren

`Lunivo-Office_0.1.0_Setup.exe` ausführen. Der Assistent fragt nach dem Installationsordner und bietet eine Desktop-Verknüpfung an; das Programm steht danach im Startmenü. Entfernen über „Apps & Features“.

Der Installer ist nicht signiert. Windows SmartScreen zeigt deshalb eine Warnung: „Weitere Informationen“ → „Trotzdem ausführen“.

### Ohne Installation testen

`Lunivo-Office_0.1.0_windows-portable.zip` entpacken und `lunivo-office\lunivo-office.exe` starten. Zum Entfernen den Ordner löschen.

### Aus dem Quellcode starten

Benötigt Python 3.10 oder neuer von python.org. In der Eingabeaufforderung im Projektordner:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

Die ersten beiden Zeilen sind nur beim ersten Mal nötig.

## macOS

### Installieren

`Lunivo-Office_0.1.0_macOS.dmg` (Apple Silicon) oder `Lunivo-Office_0.1.0_macOS_Intel.dmg` öffnen und „Lunivo Office“ in den Ordner „Programme“ ziehen. Zum Entfernen die App aus „Programme“ löschen.

Die App ist nicht notarisiert. Beim ersten Start: Rechtsklick auf die App → „Öffnen“ → „Öffnen“.

### Ohne Installation testen

Das portable `zip` entpacken und „Lunivo Office.app“ per Rechtsklick → „Öffnen“ starten. Die App kann an jedem Ort liegen.

### Aus dem Quellcode starten

Benötigt Python 3.10 oder neuer. Im Terminal im Projektordner:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

Die ersten beiden Zeilen sind nur beim ersten Mal nötig.

## Was je Betriebssystem unterschiedlich ist

Jedes Paket wird auf seinem eigenen Betriebssystem gebaut. Dabei lädt die Paketverwaltung von Python für jede Bibliothek (Qt, Schriftsatz, Übersetzung) die Fassung für genau dieses System, und der Bau packt sie fest in das Paket. Beim Installieren wird deshalb nichts erkannt oder nachgeladen: Wer das Windows-Paket nimmt, hat die Windows-Bibliotheken schon darin.

Zur Laufzeit erkennt das Programm selbst, wo es läuft (Modul `system.pfade`), und wählt danach die Ordner:

| | Linux | Windows | macOS |
|---|---|---|---|
| Einstellungen (`einstellungen.json`) | `~/.config/lunivo/` | `%APPDATA%\lunivo\` | `~/Library/Application Support/lunivo/` |
| Anwendungsdaten | `~/.local/share/Lunivo/Lunivo Writer/` | `%APPDATA%\Lunivo\Lunivo Writer\` | `~/Library/Application Support/Lunivo/Lunivo Writer/` |
| Zwischenspeicher, Protokolle | `~/.cache/Lunivo/Lunivo Writer/` | `%LOCALAPPDATA%\Lunivo\Lunivo Writer\` | `~/Library/Caches/Lunivo/Lunivo Writer/` |
| Schriften des Systems | `/usr/share/fonts`, `~/.local/share/fonts` … | `C:\Windows\Fonts` … | `/Library/Fonts`, `~/Library/Fonts` … |

Anwendungsdaten sind gelernte Schreibweisen, KI-Konfiguration und Wiederherstellungsdateien. Dokumente liegen an den von dir gewählten Speicherorten.

## Zusatzpakete

Zusatzpakete sucht das Programm selbst, in dieser Reihenfolge:

1. im Benutzerordner: `lunivo-office/<paket>` unter dem Datenordner des Systems (Linux `~/.local/share`, Windows `%APPDATA%`, macOS `~/Library/Application Support`),
2. beim Programm: ein Ordner `<paket>` neben dem Programm (dort liegt Mitgeliefertes der Installationspakete),
3. in jedem Ordner der Umgebungsvariablen `LUNIVO_ZUSATZPAKETE`, jeweils im Unterordner `<paket>`.

| Zusatzpaket | Ordnername | In den Paketen enthalten | Nachladen |
|---|---|---|---|
| Offline-Übersetzung (Argos) | `argos` | Deutsch ↔ Englisch | weitere Sprachen im Programm |
| Aufgenommene Stimmen (Piper) | `piper` | nein | Linux: `./skripte/stimme-holen.sh` |
| Leseschriften | Schriftordner `fonts/lunivo-office` | nein | Linux: `./skripte/schrift-holen.sh` |

Die beiden Lade-Skripte sind Shell-Skripte für Linux; für Windows und macOS gibt es sie noch nicht. Beim Start aus dem Quellcode ist die Offline-Übersetzung nur vorhanden, wenn zusätzlich `argostranslate` installiert wird.

Weitere optionale Erweiterungen:

| Funktion | Voraussetzung | Speicherort |
|---|---|---|
| Gründlichere Grammatikprüfung | LanguageTool und Java | Ordner `languagetool` in den Anwendungsdaten |
| Lokale KI | Ollama und ein heruntergeladenes Modell | Ollama verwaltet das Modell |
| Online-KI | Unterstützter Anbieter und eigener API-Schlüssel | Schlüssel in Lunivos Benutzerbereich |

Ohne diese Erweiterungen startet die Anwendung; die zugehörigen Funktionen bleiben optional.

## Tests für die Entwicklung

Gezielte Tests laufen ohne Bildschirm:

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/dokument/formate/test_formate.py
```
