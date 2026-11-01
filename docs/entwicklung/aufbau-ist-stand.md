# Aufbau und aktueller Quellcode

Diese Seite verweist auf die aktuellen Quellen statt eine zweite, manuell gepflegte Kopie der Register- und Optionsstruktur zu führen.

## Oberfläche

- [Aufbau des Bandes](aufbau-band.md) beschreibt die acht Register und ihre Befehle.
- [Aufbau der Optionen](aufbau-optionen.md) beschreibt die sechs Optionsseiten.
- [Baukasten der Oberfläche](baukasten.md) dokumentiert wiederverwendete Qt-Widgets.

## Quellcode

- Registerdefinitionen: `src/lunivo_writer/resources/register.json`
- Registermodule: `src/lunivo_writer/ui/ribbon/tabs/`
- Optionen: `src/lunivo_writer/ui/dialogs/optionen.py` und `optionen_seiten/`
- Dokumentoperationen: `src/lunivo_writer/editor/`
- Dateiformate und Einstellungen: `src/lunivo_writer/services/`

Die übergeordneten Modulgrenzen sind in [Projektaufbau](README.md) erklärt.
