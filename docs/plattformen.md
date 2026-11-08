# Unterstützte Plattformen

- **Linux (Ubuntu):** offiziell unterstützt. Die CI führt alle Tests aus (`.github/workflows/pruefen.yml`, Auftrag „pruefen“) und blockiert bei Fehlern.
- **Windows und macOS:** noch **nicht** offiziell unterstützt. Die CI läuft dort mit einer Auswahl plattformnaher Tests (Pfade, Sperre, Speichern, Formate, Importgrenzen, Korpus, Schreibhilfe)
  mit `continue-on-error`. Erst wenn diese Läufe grün sind und `continue-on-error` entfällt, gelten sie als unterstützt.
- Betriebssystemabhängiges (Prozessstart/-ende, Dateisperren, `fsync`) liegt nur in `src/lunivo_writer/plattform/`; der Wächtertest
  `tests/editor/test_schichten.py::test_betriebssystemabhaengiges_nur_in_plattform` hält das ein.

## Paket (.deb)

`werkzeug/deb-bauen.sh` baut genau eine `.deb` (Anwendung unter `/opt/stevie-empire/lunivo-office/`, Starter `stevie-lunivo-office.desktop`,
Symlink `/usr/bin/lunivo-office`). `torch` kommt nur als CPU-Version hinein (sonst mehrere GB durch CUDA). Die Argos-Sprachpakete
Deutsch<->Englisch lädt `werkzeug/argos-holen.sh` zur Bauzeit nach `/opt/stevie-empire/lunivo-office/argos/`; weitere Sprachen lädt das Programm
nur auf Wunsch (`ai/argos.py`). Nicht in der CI ausgeführt.
