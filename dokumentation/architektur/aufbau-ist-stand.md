# Aufbau und aktueller Quellcode

> **Stand 2026-11-18 (gilt vor allem Folgenden):** Der Dokumentweg ist Qt-frei: `Dokument` (`core/document`) → `Bearbeitungssitzung` (`core/editing`) → `LayoutEngine` (`core/layout`, mit Silbentrennung) → `DokumentRenderer` (`core/rendering`) → Qt-Oberfläche. Gelöscht sind `adapter/qt/dokument.py` (`document_to_qt`/`document_from_qt`), `pdf_modell.py`, `seitenbild.py`, `editor/layout/seitenlauf.py`, `editor/seite/seiten_aufteilung*.py` und die übrigen QTextDocument-Module in `editor/`, das Altmodell (`core/document/model.py`), der zweite Seitenumbruch (`core/layout/seitenumbruch.py`) und `dienste/modell_umwandlung.py`. PDF, Druck und Bildexport laufen über `adapter/qt/pdf_ausgabe.py`, `dienste/drucken.py` und `dienste/bild_export.py` (PDF-Struktur: `dienste/pdf_struktur.py`). Wo dieses Dokument die genannten Module noch als vorhanden beschreibt, ist das ein früherer Stand.

Diese Seite verweist auf die aktuellen Quellen statt eine zweite, manuell gepflegte Kopie der Register- und Optionsstruktur zu führen.

## Oberfläche

- [Aufbau des Bandes](aufbau-band.md) beschreibt die zehn Reiter, die Kontext-Reiter und ihre Befehle (standardmäßig sind acht Reiter sichtbar).
- [Aufbau der Optionen](aufbau-optionen.md) beschreibt die sechs Optionsseiten.
- [Baukasten der Oberfläche](../entwicklung/baukasten.md) dokumentiert wiederverwendete Qt-Widgets.

## Quellcode

- Registerdefinitionen: `src/lunivo_writer/ressourcen/register.json`
- Registermodule: `src/lunivo_writer/oberflaeche/band/reiter/`; Kontext-Reiter: `src/lunivo_writer/oberflaeche/kontext/`; Zusammenbau: `src/lunivo_writer/oberflaeche/band/plan.py`
- Optionen: `src/lunivo_writer/oberflaeche/dialoge/optionen.py` und `optionen_seiten/`
- Dokumentoperationen: `src/lunivo_writer/editor/`.
- Dokumentenkern: Modell `core/document/dokument.py`, Bearbeitung `core/editing/bearbeitungssitzung.py` (`Bearbeitungssitzung`), Layout `core/layout/seitenlayout.py` (`LayoutEngine`), Rendering `core/rendering/seitenrenderer.py` (`DokumentRenderer`).
- Der Dokument-Tab: Zeichenfläche `oberflaeche/dokument/ansicht/dokument_ansicht.py` (Eingabe und Zwischenablage in `eingabe.py`) und Editor-Schnittstelle `oberflaeche/dokument/bearbeitung/kern_editor.py` (`KernEditor`, mit `kern_befehle.py` und `kern_objekte.py`). Der frühere Qt-Texteditor (`dokument_editor.py`, `editor_*.py`) ist entfernt. Befehle ohne Anbindung meldet `KernEditor` als „noch nicht angebunden“ im Protokoll.
- Laden und Speichern: `dienste/modell_laden.py`, `modell_speichern.py`; `modell_umwandlung.py` übersetzt zwischen Altmodell (DOCX/ODT/RTF/TXT-Leser und -Schreiber) und `Dokument`.
- Synchronisierung von Dokument, Ribbon und Statusleiste liegt in `src/lunivo_writer/oberflaeche/hauptfenster/dokument_sync.py`; `oberflaeche/programmfenster.py` bindet diese Verantwortlichkeit über einen Mixin ein.
- Der KI-Dienst ist in `src/lunivo_writer/ki/` fachlich getrennt: `ki_anfragen.py` (Kontext, Einwilligung und Hintergrundaufträge), `ki_aktionen.py` (Textaktionen), `ki_dauerbetrieb.py` (laufende Assistenz), `ki_chat.py` (Chat und Antwortbezug) sowie `arbeitslauf.py` (Worker). `ki_dienst.py` bleibt die öffentliche `KIDienst`-Fassade.
- Bandbefehle für Zeichen, Absatz und Formatvorlagen sind in `kern/befehle/hauptreiter/text_zeichen.py`, `text_absatz.py` und `text_vorlagen.py` getrennt; `kern/befehle/hauptreiter/text.py` bleibt als kompatible Fassade bestehen.
- Dateiformate und Einstellungen: `src/lunivo_writer/dienste/`

Die übergeordneten Modulgrenzen sind in [Projektaufbau](../README.md) erklärt.
