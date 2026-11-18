# LUNIVO OFFICE – ZWEITER HAUPTPROMPT: ORDNER- UND DATEISTRUKTUR DES NEUEN DOKUMENTENKERNS

## 1\. AUFTRAG

Verwende die nachfolgende fachliche Aufteilung als verbindliches Architektur- und Organisationsmuster für den vollständigen Neuaufbau des Lunivo-Office-Dokumentenkerns.

Dieser Prompt ergänzt den Hauptprompt zum vollständigen Neuaufbau.

**Die vorhandene grafische Benutzeroberfläche und sämtliche Bedienelemente bleiben erhalten.**

Der Dokumentenkern, die Textverarbeitung, die Layout-Engine, das Rendering und die Dokument-Zeichenfläche werden neu entwickelt.

Die neue Architektur muss übersichtlich, modular, wartbar und langfristig erweiterbar sein.

## 2\. PROJEKTWURZEL

``` text
~/Videos/Lunivo-Office-aufgeraeumt/
└── Lunivo-Office-aufgeraeumt/
    └── src/
        └── lunivo_writer/
```

Verwende ausschließlich die innere Projektwurzel.

## 3\. VORGESCHLAGENE ZIELSTRUKTUR

Die folgende Struktur beschreibt die verbindlichen Paketverantwortlichkeiten; einzelne Dateinamen sind ein Zielmuster, keine Pflicht, jede Datei anzulegen.

Bestehende passende Verzeichnisse werden weiterverwendet. Neue Verzeichnisse dürfen erst nach meiner ausdrücklichen Zustimmung erstellt werden.

``` text
src/
└── lunivo_writer/
    │
    ├── core/
    │   │
    │   ├── document/
    │   │   ├── __init__.py
    │   │   ├── model.py
    │   │   ├── abschnitt.py
    │   │   ├── absatz.py
    │   │   ├── textlauf.py
    │   │   ├── formatierung.py
    │   │   ├── formatvorlagen.py
    │   │   ├── listen.py
    │   │   ├── tabellen.py
    │   │   ├── objekte.py
    │   │   ├── seitenparameter.py
    │   │   ├── kopf_fusszeilen.py
    │   │   ├── fussnoten.py
    │   │   ├── kommentare.py
    │   │   └── felder.py
    │   │
    │   ├── editing/
    │   │   ├── __init__.py
    │   │   ├── sitzung.py
    │   │   ├── befehle.py
    │   │   ├── transaktionen.py
    │   │   ├── verlauf.py
    │   │   ├── schreibmarke.py
    │   │   ├── auswahl.py
    │   │   ├── texteingabe.py
    │   │   ├── absatzbearbeitung.py
    │   │   ├── formatbearbeitung.py
    │   │   ├── tabellenbearbeitung.py
    │   │   ├── objektbearbeitung.py
    │   │   └── zwischenablage.py
    │   │
    │   ├── textlayout/
    │   │   ├── __init__.py
    │   │   ├── engine.py
    │   │   ├── schrift.py
    │   │   ├── glyphen.py
    │   │   ├── textmessung.py
    │   │   ├── zeilenumbruch.py
    │   │   ├── wortumbruch.py
    │   │   ├── bidi.py
    │   │   ├── tabstopps.py
    │   │   └── textpositionen.py
    │   │
    │   ├── layout/
    │   │   ├── __init__.py
    │   │   ├── engine.py
    │   │   ├── ergebnis.py
    │   │   ├── absatzlayout.py
    │   │   ├── seitenlayout.py
    │   │   ├── seitenumbruch.py
    │   │   ├── tabellenlayout.py
    │   │   ├── objektlayout.py
    │   │   ├── textumfluss.py
    │   │   ├── kopf_fusslayout.py
    │   │   ├── fussnotenlayout.py
    │   │   ├── navigation.py
    │   │   └── geometrie.py
    │   │
    │   └── rendering/
    │       ├── __init__.py
    │       ├── renderer.py
    │       ├── seitenrenderer.py
    │       ├── textrenderer.py
    │       ├── tabellenrenderer.py
    │       ├── objektrenderer.py
    │       ├── auswahlrenderer.py
    │       └── qt_backend.py
    │
    ├── oberflaeche/
    │   └── dokument/
    │       │
    │       ├── dokumentfenster/
    │       │   └── dokument_bereich.py
    │       │
    │       └── ansicht/
    │           ├── __init__.py
    │           ├── dokument_ansicht.py
    │           ├── eingabe.py
    │           ├── maus.py
    │           ├── tastatur.py
    │           ├── scrollen.py
    │           ├── zoom.py
    │           └── seitenanzeige.py
    │
    └── dienste/
        ├── docx_leser.py
        ├── docx_schreiber.py
        ├── odt_leser.py
        ├── odt_schreiber.py
        ├── rtf_leser.py
        ├── rtf_schreiber.py
        ├── pdf_export.py
        ├── drucken.py
        └── wiederherstellung.py
```

**Wichtig:** Diese Darstellung ist ein Strukturmuster und keine Anweisung, alle aufgeführten Dateien sofort anzulegen.

Die tatsächliche Aufteilung erfolgt anhand der benötigten Funktionen.

## 4\. VERANTWORTLICHKEITEN DER PAKETE

### `core/document/`

Enthält ausschließlich die Dokumentdaten und ihre fachlichen Strukturen.

Keine PySide6-Abhängigkeiten.

Keine Darstellung.

Keine Layoutberechnung.

Keine direkte Benutzeroberflächenlogik.

### `core/editing/`

Enthält sämtliche Dokumentänderungen.

Die zentrale `Sitzung` verwaltet Bearbeitung, Auswahl, Schreibmarke, Transaktionen und Rückgängig/Wiederholen.

Es darf keinen zweiten unabhängigen Bearbeitungsweg geben.

### `core/textlayout/`

Übernimmt Schriftverarbeitung, Textmessung, Glyphenpositionierung und Zeilenbildung.

Die Textsatzarchitektur wird von der Seitenaufteilung getrennt.

### `core/layout/`

Berechnet die endgültige Geometrie der Dokumentinhalte.

Die Layout-Engine verwendet das Dokumentmodell und die Textsatz-Ergebnisse.

Sie verändert keine Dokumentinhalte.

### `core/rendering/`

Zeichnet die berechneten Layout-Ergebnisse.

Das Qt-Backend verwendet bei Bedarf `QPainter`.

Die Rendering-Schicht darf keine eigene Dokumentstruktur oder Bearbeitungslogik besitzen.

### `oberflaeche/dokument/ansicht/`

Enthält die neue Dokument-Zeichenfläche und ihre Benutzerinteraktion.

Die neue `dokument_ansicht.py` ersetzt die bisherige `modell_ansicht.py`.

Die Zeichenfläche verarbeitet Eingabeereignisse und leitet Dokumentänderungen an die zentrale Bearbeitungssitzung weiter.

### `dienste/`

Enthält Dokumentimport, Dokumentexport, Druckausgabe und Wiederherstellung.

Die Dienste verwenden das neue Dokumentmodell.

Sie dürfen keine zweite Dokumentdatenhaltung aufbauen.

## 5\. VERBINDLICHE ABHÄNGIGKEITSRICHTUNG

Die Architektur muss eindeutige Zuständigkeiten besitzen.

``` text
BESTEHENDE BENUTZEROBERFLÄCHE
             │
             ▼
    NEUE DOKUMENT-ANSICHT
             │
             ├──► BEARBEITUNG
             │         │
             │         ▼
             │    DOKUMENTMODELL
             │
             └──► RENDERING
                       │
                       ▼
                     LAYOUT
                       │
                       ▼
                   TEXTLAYOUT
```

Die Darstellung ist eine vereinfachte Verantwortlichkeitsübersicht.

Verbindlich gelten zusätzlich:

- Die Bearbeitung verändert das Dokumentmodell.
- Das Layout liest Dokumentdaten, verändert sie aber nicht.
- Das Rendering zeichnet Layout-Ergebnisse.
- Die Zeichenfläche verarbeitet Benutzerinteraktionen.
- Die Oberfläche verwendet öffentliche Kern-Schnittstellen.
- Import- und Exportdienste lesen beziehungsweise erzeugen Dokumentmodelle.
- Keine zyklischen Paketabhängigkeiten.
- Keine gegenseitige Abhängigkeit zwischen Kern und Benutzeroberfläche.

## 6\. ZENTRALE ÖFFENTLICHE SCHNITTSTELLEN

Die jeweiligen `__init__.py`-Dateien sollen kleine, stabile öffentliche Schnittstellen anbieten.

Beispiel einer möglichen Verwendung:

``` python
from lunivo_writer.core.document import Dokument
from lunivo_writer.core.editing import Sitzung
from lunivo_writer.core.layout import LayoutEngine
from lunivo_writer.core.rendering import DokumentRenderer
```

Diese Klassennamen sind vorgeschlagene öffentliche APIs und müssen mit der tatsächlichen Implementierung übereinstimmen.

Interne Dateinamen dürfen sich später ändern, ohne dass sämtliche aufrufenden Pakete angepasst werden müssen.

Exportiere keine unnötigen internen Klassen.

Vermeide zirkuläre Importe.

## 7\. DATEI- UND MODULREGELN

1. Jede Datei erhält eine eindeutige fachliche Aufgabe.
2. Verwandte Funktionen werden sinnvoll zusammengefasst.
3. Keine unnötige Aufteilung in zahlreiche Kleinstdateien.
4. Keine übergroßen Sammelmodule mit fachlich unabhängigen Aufgaben.
5. Keine doppelten Implementierungen derselben Funktion.
6. Keine unnötigen Adapter.
7. Keine provisorischen Import-Hacks.
8. Keine parallelen Dokumentmodelle.
9. Keine zweite Layout-Engine.
10. Keine zweite Dokument-Zeichenfläche.
11. Keine Vermischung von Dokumentdaten und Rendering.
12. Keine direkte Bearbeitung des Dokumentmodells durch die grafische Oberfläche.

Neue Module werden nur erstellt, wenn sie tatsächlich eine notwendige Funktion übernehmen.

## 8\. UMGANG MIT BESTEHENDEN DATEIEN

Vor einer konkreten Umstrukturierung:

1. Lies die betroffenen vorhandenen Dateien.
2. Ermittle ihre fachlichen Aufgaben.
3. Ermittle die unmittelbar betroffenen Import- und Aufrufstellen.
4. Ordne die neue Implementierung dem zuständigen Paket zu.
5. Implementiere die neue Funktion.
6. Verbinde die vorhandenen Bedienelemente mit der neuen Funktion.
7. Entferne überholten Code erst, wenn seine Aufgabe übernommen wurde.

Keine vollständige Projektanalyse durchführen, wenn die unmittelbar betroffenen Dateien ausreichen.

Die bisherige grafische Oberfläche darf nicht versehentlich entfernt werden.

## 9\. KEINE UNNÖTIGEN NEUEN VERZEICHNISSE

Die vorgeschlagene Struktur verwendet überwiegend bereits im Hauptprompt genannte Projektbereiche.

Neue Verzeichnisse dürfen nicht eigenständig angelegt werden.

Falls eine zusätzliche Verzeichnisstruktur fachlich erforderlich wird, benenne die konkrete Notwendigkeit und hole meine Zustimmung ein.

Neue Python-Dateien innerhalb bestehender Verzeichnisse dürfen erstellt werden, wenn sie für die vereinbarte Implementierung erforderlich sind.

Keine leeren Vorratsmodule erstellen.

## 10\. SCHRITTWEISE UMSETZUNG

Beginne mit den grundlegenden Modulen:

1. Dokumentmodell.
2. Bearbeitungssitzung.
3. Textsatz.
4. Layout.
5. Rendering.
6. Dokument-Zeichenfläche.
7. Eingabeverarbeitung.
8. Anbindung des Dokument-Tabs.
9. Anbindung der vorhandenen Bedienelemente.
10. Erweiterte Dokumentfunktionen.
11. Dateiformate und Ausgabe.
12. Entfernung überholter Implementierungen.

Diese Reihenfolge beschreibt die technischen Prioritäten.

Zwingend voneinander abhängige Funktionen werden gemeinsam implementiert.

Keine künstlich isolierten Zwischenlösungen erzeugen.

## 11\. VERBOTENE TÄTIGKEITEN

Es gelten unverändert Hauptprompt §§ 2 und 4.2 sowie `CLAUDE.md`, einschließlich der engen Grenzen ausdrücklich genehmigter Prüfungen.

## 12\. VERBINDLICHES ENDERGEBNIS

Der neue Dokumentenkern besitzt eine übersichtliche, fachlich getrennte und langfristig wartbare Ordner- und Dateistruktur.

Jedes Paket hat eine eindeutige Verantwortung.

Öffentliche Schnittstellen reduzieren die Abhängigkeit von internen Dateinamen.

Die vorhandene grafische Benutzeroberfläche und sämtliche Bedienelemente bleiben erhalten.

Die neue Dokument-Zeichenfläche ersetzt die bisherige vollständig.

Das neue Dokumentmodell ist die einzige maßgebliche Datenquelle.

Bearbeitung, Textsatz, Layout, Rendering, Dateiformate und Druckausgabe verwenden eine einheitliche Architektur.

Der bisherige Dokumentenkern und die alte Qt-Dokumentverarbeitung werden nach vollständiger Übernahme ihrer Aufgaben entfernt.

### Verbindliche Auslegung des Strukturmusters

Die fachliche Aufteilung und Abhängigkeitsrichtung sind verbindlich. Bestehende passende Verzeichnisse weiterverwenden; keine Dateien oder Verzeichnisse nur zur Vervollständigung der Beispielstruktur erstellen. Bestehende Oberfläche erhalten, neue Zeichenfläche integrieren, alte Verarbeitung erst nach Übernahme ihrer Aufgaben entfernen. Für Wiederverwendung und Arbeitsverbote gelten Hauptprompt und `CLAUDE.md`.

## Ergänzung: Zentraler Moduleingang für optionale Zusatzdienste

Diese Ergänzung konkretisiert Abschnitt 13.3 des ersten Hauptprompts. Die oben festgelegte Zielstruktur des **Dokumentenkerns** bleibt unverändert; der zentrale Moduleingang ist eine **separate Dienstarchitektur** außerhalb von `core/`.

- **Moduleingang / Modulverwaltung:** eine kleine öffentliche Schnittstelle für die Auswahl und Verfügbarkeit optionaler Dienste; keine zweite Dokument-Engine und kein zentraler Sammelort für sämtliche Fachlogik.
- **Dienstimplementierungen:** Vorlesen, Übersetzen, Grammatik, KI und weitere optionale Ressourcen bleiben fachlich getrennt. Vorhandene passende Bereiche wie `dienste/`, `ki/` und vorhandene Dienstimplementierungen werden bevorzugt weiterverwendet.
- **Pfadverwaltung:** bestehende zentrale Pfadfunktionen in `plattform/` weiterverwenden; Ressourcen- und Installationspfade nicht in jedem Dienst duplizieren.
- **Plattformadapter:** ausschließlich tatsächlich erforderliche Unterschiede für Prozessstart, Audio, ausführbare Dateien und Betriebssystemdienste kapseln.
- **Abhängigkeitsrichtung:** `Oberfläche / Befehle → Moduleingang → optionaler Dienst → erforderlicher Plattformadapter bzw. Pfadverwaltung`. Der Dokumentenkern importiert **keine** Zusatzmodule; notwendige Dokumentänderungen erfolgen über seine öffentliche Bearbeitungsschnittstelle.
- **Dateien und Verzeichnisse:** Dies ist ein Verantwortlichkeitsmuster, **keine** Anweisung, ein neues Verzeichnis `module/` oder Vorratsdateien anzulegen. Neue Verzeichnisse benötigen die ausdrückliche Zustimmung des Projektinhabers. Vorhandene Dateien werden nur bei konkret nötigen Änderungen angepasst.
- **Umsetzung:** Die Fertigstellung des Dokumentenkerns hat Vorrang. Kein automatischer Plugin-Marktplatz, keine ungefragten Downloads und keine eigenständigen Tests. Abschnitt 4.2 des ersten Hauptprompts bleibt uneingeschränkt gültig.

