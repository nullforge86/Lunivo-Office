# Installation unter Linux Mint

Lunivo Writer benötigt Python 3.9 oder neuer. Der Start richtet eine eigene `.venv` im Projektordner ein; das System-Python wird dabei nicht verändert.

```bash
sudo apt install python3 python3-venv libxcb-cursor0 libegl1 libxkbcommon-x11-0 libxcb-icccm4 libxcb-keysyms1 libxcb-shape0
./starten-qt.sh
```

Beim ersten Start lädt das Skript die Abhängigkeiten aus `requirements.txt`: PySide6, `python-docx`, `msoffcrypto-tool`, `pyphen` und `pypdf`. Dafür wird beim Einrichten eine Internetverbindung benötigt. Danach kann Lunivo ohne Internet für lokale Schreib- und Dateifunktionen verwendet werden.

Eine Datei kann direkt beim Start angegeben werden:

```bash
./starten-qt.sh brief.docx
```

Mit `./starten-qt.sh --eintrag` wird Lunivo im Anwendungsmenü eingetragen. `./starten-qt.sh --weg` entfernt den Menüeintrag, aber nicht die virtuelle Umgebung oder Dokumente.

## Optionale Erweiterungen

| Funktion | Voraussetzung | Speicherort |
|---|---|---|
| Gründlichere Grammatikprüfung | LanguageTool und Java | `~/.local/share/Lunivo/Lunivo Writer/languagetool/` |
| Aufgenommene Stimmen | Piper und die gewählte Stimme | Installation mit `./stimme-holen.sh` |
| Leseschriften | OpenDyslexic, Lexend oder Atkinson Hyperlegible | Installation mit `./schrift-holen.sh` |
| Lokale KI | Ollama und ein heruntergeladenes Modell | Ollama verwaltet das Modell |
| Online-KI | Unterstützter Anbieter und eigener API-Schlüssel | Schlüssel in Lunivos Benutzerbereich |

Ohne diese Erweiterungen startet die Anwendung; die zugehörigen Funktionen bleiben optional.

## Benutzerdaten

Einstellungen speichert Qt unter `~/.config/Lunivo/Lunivo Writer.conf`. Anwendungsdaten wie gelernte Schreibweisen, KI-Konfiguration und Wiederherstellungsdateien liegen unter `~/.local/share/Lunivo/Lunivo Writer/`. Dokumente werden an den von dir gewählten Speicherorten abgelegt.

## Tests für die Entwicklung

Gezielte Tests laufen ohne Bildschirm:

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_formats.py
```

Die vollständige lokale Testausführung über `./starten-qt.sh --test` installiert bei Bedarf die Entwicklungsabhängigkeiten und startet pytest.
