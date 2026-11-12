# Projektaufbau

Lunivo Writer ist eine native Desktop-Anwendung mit Python 3 und PySide6/Qt Widgets. Das Programm startet über `./skripte/starten-qt.sh` oder mit `python -m lunivo_writer`; es verwendet keine Weboberfläche.

## Verzeichnisübersicht

```text
src/lunivo_writer/
  app.py, __main__.py       Einstiegspunkte
  kern/                     Anwendung, Dokumentverwaltung und Befehlssteuerung
    befehle/                Befehle: hauptreiter/ (Datei, Text, Einfügen, Seite, Verweise, Überprüfen …), kontextreiter/ (Bild-, Form-, Diagramm-, SmartArt-, Text-, Kopf-/Fußzeilen-Tools), hilfen.py
  oberflaeche/              Fenster und Qt-Oberfläche
    programmfenster.py      Hauptfenster
    backstage.py            Datei-Menü und Dokumentaktionen
    band/                   Registerband, Symbolleisten und Menüleiste
    kontext/                Kontext-Reiter (Tabellen, Bilder, Formen, Diagramme, Text, Kopf-/Fußzeile, Seriendruck)
    hauptfenster/           Bausteine des Hauptfensters (Dateien, Bearbeiten, Oberfläche, Datei-Ansicht)
    dokument/               Dokumenteditor und Dokumentfenster: bearbeitung/ (Editor und seine Mixins), dokumentfenster/ (Dokument, Reiter, linke Seitenleiste), ansicht/ (Lineal, Sprechblasen, Seitenansicht), kopffuss/, tabelle/
    seitenleiste/           Schreibhilfe- und KI-Seitenleisten
    dialoge/                Dialoge und Optionen: einfuegen/, ki/, verweise/, sendungen/, lesen_hilfe/ sowie Optionen und kleine Dialoge
    baukasten/               Gemeinsame Oberflächenbausteine, nach Zuständigkeit in Unterpaketen:
      basis/                 Palette (farben), Maße (mass), Texte, Linien, Karte, Dialoggerüst
      geruest/               Fenster- und Panelgerüst: Zusatzpanel, Fensterstapel, Einklappgruppe, Aktionsleiste, Werkbank
      felder/                Eingabeelemente: Maßfelder, Formular-Gitter, Reiterleiste, Schieber, Schalter, Farbwähler
      dropdown/              Auswahlfeld, Menüs, Popup-Verhalten; auswahl/ (Farbpalette, Raster, Symbole), objektmenues/ (Bild-, Form-, Diagramm-Menüs, Voreinstellungen)
      formatierung/          Format-Panels und -Dialoge (Absatz, Schrift, Objekt, Text-Effekte, Formatvorlagen)
      dokument/              Dialoge rund um Dokument und Seite (Layout, Druck, Liste, Eingabe, Erstellen)
      diagramme/             Format-Panels für Diagramm und SmartArt
      medien/                Bild-, Datei-, Listen-, Umbruch- und Seitensymbole, Bild-Export
      vorlagen/              Vorlagen-Galerie
      chat/                  Bausteine der KI-Seitenleiste
    statusleiste/           Statusleiste
  plattform/                Betriebssystem-Abhängiges an einer Stelle: pfade (QStandardPaths), sperre (Dateisperre), protokoll (Logdatei)
  editor/                   Dokumentoperationen und Textlogik, nach Zuständigkeit in Unterpaketen:
    seite/                  Seitenumbruch, Seitenfluss, Abschnitte, Kopf-/Fußbereich-Hilfen, Druck, Deckblatt
    text/                   Zeichen- und Absatzformat, Stile, Listen, Suchen, Texteffekte, Muster, Zahlformate
    objekte/                Bilder, Formen, freie Objekte, SmartArt, Linien, Sprechblasen
    tabelle/                Tabellenstil, -zustand, -eigenschaften, Text in Tabelle
    dokument/               Einfügen, Felder, Formular, Verweise, Verzeichnisse, Vergleich, Sendungen, Vorlagen
    diagramme/              Diagrammzeichnung, Geometrie, Formatierung und Teil-Auswahl
  modelle/                  Dokument- und Seitendaten
  dienste/                  Datei-, Einstellungs-, Wiederherstellungs- und Exportdienste; rtf/ (RTF-Import: Zerleger, Steuerwörter, Gruppen, Aufbau), docx_teile/ (DOCX), odt_*.py (ODT)
  ki/                       KI-Anbieter und KI-Aufgaben; ki.py (Klasse KI) mit ki_transport, ki_claude, ki_ollama, ki_eigen, ki_werkzeugschleife, ki_textaktionen, ki_bildgenerierung
  korrektur/                Rechtschreibprüfung, Vorhersage und Barrierefreiheit
  ressourcen/               Handbuch, Registerdefinitionen und Wörterdaten
ressourcen/                 Symbole (icons/, symbole/), Bilder (bilder/), Schriftarten (schriftarten/) und weitere Laufzeitressourcen
dokumentation/              benutzerhandbuch/, entwicklung/, architektur/, konzepte/; berichte/ enthält die Prüf-, Test- und Abschlussberichte
tests/                      Gezielte pytest-Tests
werkzeuge/                  Entwicklungs- und Prüfhilfen: pruefungen/ (funktionspruefung.py: Band; seitenleistenpruefung.py: Seitenleiste „Formatierung“ durchklicken; importpruefung.py: Importpfade; speicherpruefung.py; kontrast.py; docx_korpus.py; darstellung_korpus.py: Prüfdatenbank der Darstellung, vergleicht die DOCX-Sammlung mit ihren Referenz-PDFs, Bericht in dokumentation/berichte/darstellung-korpus.md), erstellung/ (inventar_bauen.py: dokumentation/entwicklung/interne-funktionen.md neu erzeugen; module_verschieben.py; deb-bauen.sh; titelbild.py), symbole/ (Symbol-Werkzeuge)
skripte/                    Startskript (starten-qt.sh) und Lade-Skripte (schrift-holen.sh, stimme-holen.sh)
```

## Architekturübersicht

![Architektur: Anwendungsstart, gemeinsam genutzte Dienste, Dokumentenverwaltung, Bearbeitung und Layout sowie Schreibunterstützung mit ihren Beziehungen](../ressourcen/bilder/architektur.png)

## Zuständigkeiten

- **kern** steuert den Programmablauf und vermittelt Befehle.
- **oberflaeche** zeigt Dokumente, Register, Seitenleisten und Dialoge.
- **editor** führt Dokumentänderungen aus.
- **editor/** ist in `seite`, `text`, `objekte`, `tabelle`, `dokument` und `diagramme` gegliedert. Alte Weiterleitungen gibt es nicht mehr; `werkzeuge/pruefungen/importpruefung.py` (und `tests/plattform/test_importpfade.py`) prüft nach jedem Verschieben alle Importpfade. `werkzeuge/erstellung/module_verschieben.py` verschiebt Module und zieht alle Verweise mit.
- **modelle** hält Dokument- und Seitendaten.
- **dienste** liest und schreibt Dateien, Einstellungen und Sicherungen.
- **plattform** kapselt Pfade, Dateisperre und Protokoll; nur dort steht Code, der je nach Betriebssystem verschieden ist.
- **korrektur** prüft und erklärt Textstellen (jeder Prüfer in `korrektur/pruefung.py` hat einen Namen und lässt sich über `schreibhilfe/pruefer_<name>` ausschalten; `modelle/korrektur.py` hat das gemeinsame Fundmodell `ProofingIssue`); **ai** stellt optionale KI-Aufgaben bereit.

Die Richtung der Abhängigkeiten bleibt einfach: Oberfläche und kern verwenden editor, modelle und dienste. Fachlogik liegt nicht in den Widgets.

Diese Richtung prüft `tests/editor/test_schichten.py`: `editor/`, `dienste/`, `modelle/` und `korrektur/` importieren nichts aus `oberflaeche/`. Zwei Altfälle stehen als Ausnahme in der Liste des Tests (`editor/dokument/formular.py`, `editor/dokument/einfuegen.py`); sie darf nur kleiner werden. `kern/befehle/` ist die Anwendungsschicht zwischen Oberfläche und Editor und darf `oberflaeche/` verwenden.

## Abhängigkeiten, Prüfungen, Plattformen

- **Pakete:** `pyproject.toml` ist die Quelle. `requirements*.txt` (für `./skripte/starten-qt.sh` und pip) führen dieselben Pakete, das prüft `tests/plattform/test_abhaengigkeiten.py`. Reproduzierbar installieren: `uv sync --frozen --extra dev` (Lock: `uv.lock`). Qt kommt als `PySide6-Essentials`, `-Addons` und `-Pdf`, ohne das Web-Sammelpaket.
- **Python:** ab 3.10. **Fehlerprüfung:** `ruff check .` (nur echte Fehler). **Tests:** gezielt, `python -m pytest <Datei> -k <Name>`; die Gesamtprüfung macht die CI.
- **Plattformen:** Linux ist getestet. Windows und macOS sind vorbereitet (Pfade, Dateisperre, Start); ob sie laufen, zeigt erst der CI-Job „Prüfen (windows/macos, Auswahl)“, der noch nicht blockiert.
- **Protokoll:** Fehler beim Laden, Speichern und Prüfen stehen in `logs/lunivo.log` im Zwischenspeicher-Ordner des Benutzers.
- **Bekannte offene Punkte:** zwei Ausnahmen in `tests/editor/test_schichten.py`. Die DOCX-Ein-/Ausgabe ist in fachliche Mixins unter `dienste/docx_teile/` aufgeteilt; `docx_leser.py` und `docx_schreiber.py` bleiben als kompatible Fassaden. Die Roundtrip-Absicherung liegt in `tests/dokument/formate/test_docx_hin_und_zurueck.py` und muss nach strukturellen Änderungen in CI ausgeführt werden.

## Einstiegspunkte

- Banddefinition und Reiter: `src/lunivo_writer/ressourcen/register.json` und `src/lunivo_writer/oberflaeche/band/reiter/`.
- Gemeinsame Qt-Bausteine: `src/lunivo_writer/oberflaeche/baukasten/`; Konventionen stehen in [baukasten.md](entwicklung/baukasten.md).
- Dokumentformate: `src/lunivo_writer/dienste/`; DOCX-Lese- und Schreiblogik ist nach Metadaten, Absätzen, Runs, Dokumentaufbau und Tabellen/Objekten getrennt in `dienste/docx_teile/`.
- Eingebautes Handbuch: `src/lunivo_writer/ressourcen/handbuch.md`.
- Abhängigkeiten und Start: `pyproject.toml`, `requirements.txt` und `skripte/starten-qt.sh`.

Die wichtigsten Benutzerfunktionen sind in der [Oberfläche](benutzerhandbuch/oberflaeche.md), den [Einstellungen](benutzerhandbuch/einstellungen.md) und unter [Speichern und Dateiformate](benutzerhandbuch/speichern.md) beschrieben.

## Weitere Dokumentation

- [Qt-Entkopplung](architektur/qt-entkopplung.md): Ist-Zustand der Qt-Abhängigkeiten, Zielbild (`core`, `adapter/qt`), Phasen und Blockaden.
- [Layout-Schicht](architektur/layout-schicht.md): Ziel, Schichten, Phasen, Messnetz und Stand der eigenen Layout-Schicht (Seitenplan, Absatzfluss, Display-Liste).
- [UI-Technologie](architektur/ui-technologie.md): Qt Widgets, Zeichnung der Seiten, Theme, Symbole, Formate, Abhängigkeiten.
- [Interne Funktionen](entwicklung/interne-funktionen.md): vollständiges Inventar der Module, Klassen, Funktionen und Methoden. Wird mit `werkzeuge/erstellung/inventar_bauen.py` aus dem Quelltext erzeugt.
- [Lies mich](benutzerhandbuch/liesmich.md), [Installation](benutzerhandbuch/installation.md), [Lesen und Schreiben](benutzerhandbuch/lesen-und-schreiben.md), [Prüfung, Vorhersage und KI](benutzerhandbuch/pruefung-und-ki.md), [Schreiben und Dokumente](benutzerhandbuch/schreiben-und-dokumente.md), [Tabellen und Steuerung](benutzerhandbuch/tabellen-und-steuerung.md): Benutzerdokumentation.
- [Aufbau: Registerband](architektur/aufbau-band.md), [Aufbau: Ist-Stand](architektur/aufbau-ist-stand.md), [Aufbau: Optionen](architektur/aufbau-optionen.md), [Konzept: Optionen](konzepte/konzept-optionen.md), [Erweiterungen](entwicklung/erweiterungen.md): Aufbau und Konzepte.
- [Entstehung](entwicklung/entstehung.md) und [Wohin Lunivo gehen soll](konzepte/richtung.md): Hintergrund und Richtung.
