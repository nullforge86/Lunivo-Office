# UI-Technologie

Lunivo Writer ist eine native Desktop-Anwendung. Die Oberfläche besteht ausschließlich aus **Python 3 und PySide6 (Qt for Python) mit Qt Widgets**. 

## Bausteine

| Bereich | Technik | Ort |
|---|---|---|
| Fenster, Dialoge, Seitenleisten | Qt Widgets (`QMainWindow`, `QDialog`, `QWidget`), Layouts | `ui/` |
| Dokumenttext | `QTextEdit` mit `QTextDocument`, `QTextCursor`, `QTextCharFormat`, `QTextBlockFormat`, `QTextTable` — niemals `toHtml`/`setHtml` | `ui/document/document_editor.py`, `editor/` |
| Seitenansicht | Eigene Zeichnung der Blätter, Spalten und Seitenränder in `paintEvent` mit `QPainter` auf dem Textfluss | `ui/document/editor_spalten.py`, `editor/pagination.py` |
| Registerband | Aufbau aus `resources/register.json` und `ui/ribbon/tabs/`; Befehle werden über `core/befehle/` vermittelt | `ui/ribbon/` |
| Gemeinsame Bausteine | Farbpalette, Linien, Menüs, Dialoggerüst, `FormularGitter`, `FlussLayout` | `ui/baukasten/`, [baukasten.md](baukasten.md) |
| Aussehen hell/dunkel | Stil „Fusion“ mit `QPalette`; Stylesheets (`QSS`) nur für einzelne Feinheiten, nicht fürs Grundlayout | `ui/theme.py` |
| Symbole | Lucide-Liniensymbole als SVG-Pfade, per `QSvgRenderer` in den Farben der Palette gezeichnet | `ui/widgets/icons.py`, `assets/` |
| Hilfe- und Infotexte | Markdown mit `QTextBrowser.setMarkdown` | `resources/handbuch.md` |
| Formeln, Vorschauen, Diagramme, SmartArt | `QTextDocument` und `QPainter` | `editor/`, `ui/baukasten/` |
| Drucken und PDF | `QPrinter`, `QPdfWriter` | `editor/druck.py`, `services/pdf_export.py` |
| Hintergrundarbeit | KI-Aufrufe laufen in `QThreadPool`/`QRunnable`, Ergebnisse kommen über Qt-Signale zurück | `ai/ai_service.py`, `ui/sidebar/sidebar.py` |

## Dateiformate

DOCX, ODT, FODT, RTF und TXT liest und schreibt Lunivo selbst (`services/`), ohne LibreOffice oder andere externe Programme; PDF und PNG gibt es nur als Export (Einzelheiten: [SPEICHERN.md](SPEICHERN.md)). DOCX nutzt `python-docx`. Eigene Daten (Textbausteine u. a.) sind JSON ohne Markup; Einstellungen liegen in `QSettings` (`services/settings_service.py`).

## Abhängigkeiten

`PySide6`, `python-docx`, `msoffcrypto-tool`, `pyphen`, `pypdf` (siehe `requirements.txt`, `pyproject.toml`). Start: `./starten-qt.sh` oder `python -m lunivo_writer`.

## Schichten

Oberfläche und `core` verwenden `editor`, `models` und `services`; Fachlogik liegt nicht in den Widgets. Ordnerübersicht: [README.md](README.md). Alle Module, Klassen und Funktionen: [interne-funktionen.md](interne-funktionen.md).
