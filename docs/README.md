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
    contextual/             Kontext-Reiter (Tabellen, Bilder, Formen, Diagramme, Text, Kopf-/Fußzeile, Seriendruck)
    hauptfenster/           Bausteine des Hauptfensters (Dateien, Bearbeiten, Oberfläche, Datei-Ansicht)
    document/               Dokumenteditor, Seitenfläche, Lineale und Dokumentreiter
    sidebar/                 Schreibhilfe- und KI-Seitenleisten
    dialogs/                 Dialoge und Optionen
    baukasten/               Gemeinsame Oberflächenbausteine
    statusbar/               Statusleiste
  plattform/                Betriebssystem-Abhängiges an einer Stelle: pfade (QStandardPaths), sperre (Dateisperre), protokoll (Logdatei)
  editor/                   Dokumentoperationen und Textlogik
  models/                   Dokument- und Seitendaten
  services/                 Datei-, Einstellungs-, Wiederherstellungs- und Exportdienste
  ai/                       KI-Anbieter und KI-Aufgaben
  proofing/                 Rechtschreibprüfung, Vorhersage und Barrierefreiheit
  resources/                Handbuch, Registerdefinitionen und Wörterdaten
assets/                     Symbole, Logos und weitere Laufzeitressourcen
docs/                       Projekt- und Benutzerdokumentation
tests/                      Gezielte pytest-Tests
werkzeug/                   Entwicklungs- und Prüfhilfen (inventar-bauen.py: docs/interne-funktionen.md neu erzeugen; funktionspruefung.py: Band; seitenleistenpruefung.py: Seitenleiste „Formatierung“ durchklicken, Bericht docs/seitenleistenstand.md)
```

## Zuständigkeiten

- **core** steuert den Programmablauf und vermittelt Befehle.
- **ui** zeigt Dokumente, Register, Seitenleisten und Dialoge.
- **editor** führt Dokumentänderungen aus.
- **models** hält Dokument- und Seitendaten.
- **services** liest und schreibt Dateien, Einstellungen und Sicherungen.
- **plattform** kapselt Pfade, Dateisperre und Protokoll; nur dort steht Code, der je nach Betriebssystem verschieden ist.
- **proofing** prüft und erklärt Textstellen (jeder Prüfer in `proofing/pruefung.py` hat einen Namen und lässt sich über `schreibhilfe/pruefer_<name>` ausschalten; `models/proofing.py` hat das gemeinsame Fundmodell `ProofingIssue`); **ai** stellt optionale KI-Aufgaben bereit.

Die Richtung der Abhängigkeiten bleibt einfach: Oberfläche und core verwenden editor, models und services. Fachlogik liegt nicht in den Widgets.

Diese Richtung prüft `tests/test_schichten.py`: `editor/`, `services/`, `models/` und `proofing/` importieren nichts aus `ui/`. Zwei Altfälle stehen als Ausnahme in der Liste des Tests (`editor/formular.py`, `editor/einfuegen.py`); sie darf nur kleiner werden. `core/befehle/` ist die Anwendungsschicht zwischen Oberfläche und Editor und darf `ui/` verwenden.

## Abhängigkeiten, Prüfungen, Plattformen

- **Pakete:** `pyproject.toml` ist die Quelle. `requirements*.txt` (für `./starten-qt.sh` und pip) führen dieselben Pakete, das prüft `tests/test_abhaengigkeiten.py`. Reproduzierbar installieren: `uv sync --frozen --extra dev` (Lock: `uv.lock`). Qt kommt als `PySide6-Essentials`, `-Addons` und `-Pdf`, ohne das Web-Sammelpaket.
- **Python:** ab 3.10. **Fehlerprüfung:** `ruff check .` (nur echte Fehler). **Tests:** gezielt, `python -m pytest <Datei> -k <Name>`; die Gesamtprüfung macht die CI.
- **Plattformen:** Linux ist getestet. Windows und macOS sind vorbereitet (Pfade, Dateisperre, Start); ob sie laufen, zeigt erst der CI-Job „Prüfen (windows/macos, Auswahl)“, der noch nicht blockiert.
- **Protokoll:** Fehler beim Laden, Speichern und Prüfen stehen in `logs/lunivo.log` im Zwischenspeicher-Ordner des Benutzers.
- **Bekannte offene Punkte:** zwei Ausnahmen in `tests/test_schichten.py`; die großen Dateien `services/docx_reader.py` und `docx_writer.py` sind ungeteilt, weil die Absicherung des DOCX-Roundtrips noch nicht gemessen ist.

## Einstiegspunkte

- Banddefinition und Reiter: `src/lunivo_writer/resources/register.json` und `src/lunivo_writer/ui/ribbon/tabs/`.
- Gemeinsame Qt-Bausteine: `src/lunivo_writer/ui/baukasten/`; Konventionen stehen in [baukasten.md](baukasten.md).
- Dokumentformate: `src/lunivo_writer/services/`.
- Eingebautes Handbuch: `src/lunivo_writer/resources/handbuch.md`.
- Abhängigkeiten und Start: `pyproject.toml`, `requirements.txt` und `starten-qt.sh`.

Die wichtigsten Benutzerfunktionen sind in der [Oberfläche](oberflaeche.md), den [Einstellungen](einstellungen.md) und unter [Speichern und Dateiformate](SPEICHERN.md) beschrieben.

## Weitere Dokumentation

- [UI-Technologie](ui-technologie.md): Qt Widgets, Zeichnung der Seiten, Theme, Symbole, Formate, Abhängigkeiten.
- [Interne Funktionen](interne-funktionen.md): vollständiges Inventar der Module, Klassen, Funktionen und Methoden. Wird mit `werkzeug/inventar-bauen.py` aus dem Quelltext erzeugt.
- [Lies mich](LIESMICH.md), [Installation](INSTALLATION.md), [Lesen und Schreiben](lesen-und-schreiben.md), [Prüfung, Vorhersage und KI](pruefung-und-ki.md), [Schreiben und Dokumente](schreiben-und-dokumente.md), [Tabellen und Steuerung](tabellen-und-steuerung.md): Benutzerdokumentation.
- [Aufbau: Registerband](aufbau-band.md), [Aufbau: Ist-Stand](aufbau-ist-stand.md), [Aufbau: Optionen](aufbau-optionen.md), [Konzept: Optionen](konzept-optionen.md), [Erweiterungen](erweiterungen.md): Aufbau und Konzepte.
- [Entstehung](ENTSTEHUNG.md) und [Wohin Lunivo gehen soll](RICHTUNG.md): Hintergrund und Richtung.
