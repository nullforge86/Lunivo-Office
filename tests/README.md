# Tests

Automatische Tests mit pytest, ohne Bildschirm (`QT_QPA_PLATFORM=offscreen`). Lokal immer nur gezielt ausführen, die Gesamtprüfung macht die CI bei Push und Pull Request:

```bash
.venv/bin/python -m pytest tests/test_formats.py
.venv/bin/python -m pytest tests/test_editor.py -k fett
```

- `test_*.py`: ein Thema je Datei (Dateiformate, Editor, Registerband, Schreibhilfe, Plattform, Oberfläche).
- `conftest.py`, `blatt_dokument.py`, `fake_mcp_server.py`, `silben_gold.py`: gemeinsame Hilfen und Prüfdaten, keine eigenen Tests.
- `daten/lo_dokument.docx`: Testdokument für `test_lo_dokument.py`; `silben_hart.txt`: Prüfwörter für die Silbentrennung.
- `test_schichten.py` und `test_main_window.py::test_kein_html_im_projekt` sichern die Architekturregeln.
