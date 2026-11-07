# Aufbau und aktueller Quellcode

Diese Seite verweist auf die aktuellen Quellen statt eine zweite, manuell gepflegte Kopie der Register- und Optionsstruktur zu führen.

## Oberfläche

- [Aufbau des Bandes](aufbau-band.md) beschreibt die zehn Reiter, die Kontext-Reiter und ihre Befehle (standardmäßig sind acht Reiter sichtbar).
- [Aufbau der Optionen](aufbau-optionen.md) beschreibt die sechs Optionsseiten.
- [Baukasten der Oberfläche](baukasten.md) dokumentiert wiederverwendete Qt-Widgets.

## Quellcode

- Registerdefinitionen: `src/lunivo_writer/resources/register.json`
- Registermodule: `src/lunivo_writer/ui/ribbon/tabs/`; Kontext-Reiter: `src/lunivo_writer/ui/contextual/`; Zusammenbau: `src/lunivo_writer/ui/ribbon/plan.py`
- Optionen: `src/lunivo_writer/ui/dialogs/optionen.py` und `optionen_seiten/`
- Dokumentoperationen: `src/lunivo_writer/editor/`.
- Der Qt-Editor liegt in `src/lunivo_writer/ui/document/document_editor.py`; Einfügen aus der Zwischenablage und Einfügevarianten sind in `editor_einfuegen.py` gekapselt.
- Synchronisierung von Dokument, Ribbon und Statusleiste liegt in `src/lunivo_writer/ui/hauptfenster/dokument_sync.py`; `ui/main_window.py` bindet diese Verantwortlichkeit über einen Mixin ein.
- Dateiformate und Einstellungen: `src/lunivo_writer/services/`

Die übergeordneten Modulgrenzen sind in [Projektaufbau](README.md) erklärt.
