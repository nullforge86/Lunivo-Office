# UI-Technologie

Lunivo Writer ist eine native Desktop-Anwendung. Die Oberfläche besteht ausschließlich aus **Python 3 und PySide6 (Qt for Python) mit Qt Widgets**. 

## Bausteine

| Bereich | Technik | Ort |
|---|---|---|
| Fenster, Dialoge, Seitenleisten | Qt Widgets (`QMainWindow`, `QDialog`, `QWidget`), Layouts | `oberflaeche/` |
| Dokumenttext | Qt-freies Modell `Dokument` mit `Bearbeitungssitzung`; Schreibmarke, Auswahl und Eingabe über die eigene Zeichenfläche, nicht über `QTextEdit` | `core/document`, `core/editing`, `oberflaeche/dokument/bearbeitung/kern_editor.py` |
| Seitenansicht | `LayoutEngine` setzt die Seiten, `DokumentRenderer` zeichnet sie über `QtRenderBackend` (`QPainter` ist nur Ausgabe) | `core/layout`, `core/rendering`, `adapter/qt/rendering.py`, `oberflaeche/dokument/ansicht/dokument_ansicht.py` |
| Registerband | Aufbau aus `ressourcen/register.json` und `oberflaeche/band/reiter/`; Befehle werden über `kern/befehle/` vermittelt | `oberflaeche/band/` |
| Gemeinsame Bausteine | Farbpalette, Linien, Menüs, Dialoggerüst, `FormularGitter`, `FlussLayout` | `oberflaeche/baukasten/`, [baukasten.md](../entwicklung/baukasten.md) |
| Aussehen hell/dunkel | Stil „Fusion“ mit `QPalette`; Stylesheets (`QSS`) nur für einzelne Feinheiten, nicht fürs Grundlayout | `oberflaeche/thema.py` |
| Symbole | Lucide-Liniensymbole als SVG-Pfade, per `QSvgRenderer` in den Farben der Palette gezeichnet | `oberflaeche/bauteile/symbole.py`, `ressourcen/` |
| Hilfe- und Infotexte | Markdown mit `QTextBrowser.setMarkdown` | `ressourcen/handbuch.md` |
| Formeln, Vorschauen, Diagramme, SmartArt | `QPainter`; teils noch `QTextDocument` im Altpfad | `editor/`, `oberflaeche/baukasten/` |
| Drucken und PDF | `QPrinter`, `QPdfWriter`; das PDF entsteht aus dem Kernlayout | `adapter/qt/pdf_modell.py`, `dienste/pdf_export.py` (Drucken ist im Kern-Editor noch nicht angebunden) |
| Hintergrundarbeit | KI-Aufrufe laufen in `QThreadPool`/`QRunnable`, Ergebnisse kommen über Qt-Signale zurück | `ki/ki_dienst.py`, `oberflaeche/seitenleiste/seitenleiste.py` |

## Dateiformate

DOCX, ODT, FODT, RTF und TXT liest und schreibt Lunivo selbst (`dienste/`), ohne externe Programme; PDF und PNG gibt es nur als Export (Einzelheiten: [speichern.md](../benutzerhandbuch/speichern.md)). DOCX nutzt `python-docx`. Eigene Daten (Textbausteine u. a.) sind JSON ohne Markup; Einstellungen liegen in `QSettings` (`dienste/einstellungen_dienst.py`).

## Abhängigkeiten

`PySide6`, `python-docx`, `msoffcrypto-tool`, `pyphen`, `pypdf` (siehe `requirements.txt`, `pyproject.toml`). Start: `./skripte/starten-qt.sh` oder `python -m lunivo_writer`.

## Schichten

Oberfläche verwendet `core`, `adapter/qt`, `editor`, `modelle` und `dienste`; `core` kennt kein Qt; Fachlogik liegt nicht in den Widgets. Ordnerübersicht: [README.md](../README.md). Alle Module, Klassen und Funktionen: [interne-funktionen.md](../entwicklung/interne-funktionen.md).
