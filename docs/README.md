# Projektaufbau

Lunivo Writer ist eine native Desktop-Anwendung mit Python 3 und PySide6/Qt Widgets. Das Programm startet über `./starten-qt.sh` oder mit `python -m lunivo_writer`; es verwendet keine Weboberfläche.

## Verzeichnisübersicht

```text
src/lunivo_writer/
  app.py, __main__.py       Einstiegspunkte
  core/                     Anwendung, Dokumentverwaltung und Befehlssteuerung
  ui/                       Fenster und Qt-Oberfläche
    main_window.py          Hauptfenster
    backstage.py            Datei-Menü und Dokumentaktionen
    ribbon/                 Registerband, Symbolleisten und Menüleiste
    document/               Dokumenteditor, Seitenfläche, Lineale und Dokumentreiter
    sidebar/                 Schreibhilfe- und KI-Seitenleisten
    dialogs/                 Dialoge und Optionen
    baukasten/               Gemeinsame Oberflächenbausteine
    statusbar/               Statusleiste
  editor/                   Dokumentoperationen und Textlogik
  models/                   Dokument- und Seitendaten
  services/                 Datei-, Einstellungs-, Wiederherstellungs- und Exportdienste
  ai/                       KI-Anbieter und KI-Aufgaben
  proofing/                 Rechtschreibprüfung, Vorhersage und Barrierefreiheit
  resources/                Handbuch, Registerdefinitionen und Wörterdaten
assets/                     Symbole, Logos und weitere Laufzeitressourcen
docs/                       Projekt- und Benutzerdokumentation
tests/                      Gezielte pytest-Tests
werkzeug/                   Entwicklungs- und Prüfhilfen (funktionspruefung.py: Band; seitenleistenpruefung.py: Seitenleiste „Formatierung“ durchklicken, Bericht docs/seitenleistenstand.md)
```

## Zuständigkeiten

- **core** steuert den Programmablauf und vermittelt Befehle.
- **ui** zeigt Dokumente, Register, Seitenleisten und Dialoge.
- **editor** führt Dokumentänderungen aus.
- **models** hält Dokument- und Seitendaten.
- **services** liest und schreibt Dateien, Einstellungen und Sicherungen.
- **proofing** prüft und erklärt Textstellen; **ai** stellt optionale KI-Aufgaben bereit.

Die Richtung der Abhängigkeiten bleibt einfach: Oberfläche und core verwenden editor, models und services. Fachlogik liegt nicht in den Widgets.

## Einstiegspunkte

- Banddefinition und Reiter: `src/lunivo_writer/resources/register.json` und `src/lunivo_writer/ui/ribbon/tabs/`.
- Gemeinsame Qt-Bausteine: `src/lunivo_writer/ui/baukasten/`; Konventionen stehen in [baukasten.md](baukasten.md).
- Dokumentformate: `src/lunivo_writer/services/`.
- Eingebautes Handbuch: `src/lunivo_writer/resources/handbuch.md`.
- Abhängigkeiten und Start: `pyproject.toml`, `requirements.txt` und `starten-qt.sh`.

Die wichtigsten Benutzerfunktionen sind in der [Oberfläche](oberflaeche.md), den [Einstellungen](einstellungen.md) und unter [Speichern und Dateiformate](SPEICHERN.md) beschrieben.
