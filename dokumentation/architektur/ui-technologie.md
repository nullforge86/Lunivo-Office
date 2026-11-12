# UI-Technologie

Lunivo Writer ist eine native Desktop-Anwendung. Die Oberfläche besteht ausschließlich aus **Python 3 und PySide6 (Qt for Python) mit Qt Widgets**. 

## Bausteine

| Bereich | Technik | Ort |
|---|---|---|
| Fenster, Dialoge, Seitenleisten | Qt Widgets (`QMainWindow`, `QDialog`, `QWidget`), Layouts | `oberflaeche/` |
| Dokumenttext | `QTextEdit` mit `QTextDocument`, `QTextCursor`, `QTextCharFormat`, `QTextBlockFormat`, `QTextTable` — niemals `toHtml`/`setHtml` | `oberflaeche/dokument/bearbeitung/dokument_editor.py`, `editor/` |
| Seitenansicht | Eigene Zeichnung der Blätter, Spalten und Seitenränder in `paintEvent` mit `QPainter` auf dem Textfluss | `oberflaeche/dokument/bearbeitung/editor_spalten.py`, `editor/seite/seiten_aufteilung.py` |
| Registerband | Aufbau aus `ressourcen/register.json` und `oberflaeche/band/reiter/`; Befehle werden über `kern/befehle/` vermittelt | `oberflaeche/band/` |
| Gemeinsame Bausteine | Farbpalette, Linien, Menüs, Dialoggerüst, `FormularGitter`, `FlussLayout` | `oberflaeche/baukasten/`, [baukasten.md](../entwicklung/baukasten.md) |
| Aussehen hell/dunkel | Stil „Fusion“ mit `QPalette`; Stylesheets (`QSS`) nur für einzelne Feinheiten, nicht fürs Grundlayout | `oberflaeche/thema.py` |
| Symbole | Lucide-Liniensymbole als SVG-Pfade, per `QSvgRenderer` in den Farben der Palette gezeichnet | `oberflaeche/bauteile/symbole.py`, `ressourcen/` |
| Hilfe- und Infotexte | Markdown mit `QTextBrowser.setMarkdown` | `ressourcen/handbuch.md` |
| Formeln, Vorschauen, Diagramme, SmartArt | `QTextDocument` und `QPainter` | `editor/`, `oberflaeche/baukasten/` |
| Drucken und PDF | `QPrinter`, `QPdfWriter` | `editor/seite/druck.py`, `dienste/pdf_export.py` |
| Hintergrundarbeit | KI-Aufrufe laufen in `QThreadPool`/`QRunnable`, Ergebnisse kommen über Qt-Signale zurück | `ki/ki_dienst.py`, `oberflaeche/seitenleiste/seitenleiste.py` |

## Dateiformate

DOCX, ODT, FODT, RTF und TXT liest und schreibt Lunivo selbst (`dienste/`), ohne externe Programme; PDF und PNG gibt es nur als Export (Einzelheiten: [speichern.md](../benutzerhandbuch/speichern.md)). DOCX nutzt `python-docx`. Eigene Daten (Textbausteine u. a.) sind JSON ohne Markup; Einstellungen liegen in `QSettings` (`dienste/einstellungen_dienst.py`).

## Abhängigkeiten

`PySide6`, `python-docx`, `msoffcrypto-tool`, `pyphen`, `pypdf` (siehe `requirements.txt`, `pyproject.toml`). Start: `./skripte/starten-qt.sh` oder `python -m lunivo_writer`.

## Schichten

Oberfläche und `core` verwenden `editor`, `models` und `services`; Fachlogik liegt nicht in den Widgets. Ordnerübersicht: [README.md](../README.md). Alle Module, Klassen und Funktionen: [interne-funktionen.md](../entwicklung/interne-funktionen.md).
