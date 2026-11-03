# Der Aufbau des Bandes

Quelle des Bandes: `src/lunivo_writer/resources/register.json` und die Reiter-Module unter
`src/lunivo_writer/ui/ribbon/tabs/`; zusammengesetzt werden sie in `src/lunivo_writer/ui/ribbon/plan.py`. Die Kontext-Reiter stehen unter
`src/lunivo_writer/ui/contextual/`. Eine lokale Funktionsprüfung lässt sich mit
`werkzeug/funktionspruefung.py` gezielt für einzelne Reiter ausführen.

Das Band hat zehn Reiter. Standardmäßig sind acht sichtbar: Der Reiter *Datei* bleibt verborgen, weil seine Befehle im **☰ Menü** links vor dem Schnellzugriff
stehen, und *Sendungen* ist ausgeblendet; er lässt sich über *Ansicht ▸ Oberfläche ▸ Register anpassen* einblenden. Dazu kommen neun Kontext-Reiter,
die nur bei passender Auswahl erscheinen. Das Band zeigt einen Reiter; welchen, sagt die Reiterzeile.
Dieselben Befehle stehen auch in der Menüleiste und in den beiden
Symbolleisten — welche Oberfläche sichtbar ist, sagt
*Ansicht ▸ Oberfläche ▸ Benutzeroberfläche*.

Die Bäume unten zeigen die Gruppen des Bandes und ihre Knöpfe; Einträge unter einem Knopf sind feste Menüpunkte. Viele Knöpfe mit ▾ öffnen
zusätzlich ein Klappmenü, dessen Einträge im Programm erzeugt werden und hier nicht einzeln stehen.

## Die Reiter im Überblick

| Reiter | Wofür |
|---|---|
| [Datei](#datei) | Neu, Öffnen, Speichern, Exportieren, Drucken, Dokumentinformationen (als ☰ Menü sichtbar, der Reiter selbst ist verborgen) |
| [Start](#start) | Zwischenablage, Schrift, Absatz, Formatvorlagen, Suchen |
| [Einfügen](#einfügen) | Alles, was in den Text hineinkommt |
| [Seitenlayout](#seitenlayout) | Designs, Ränder, Seite einrichten, Seitenhintergrund, Anordnen |
| [Verweise](#verweise) | Verzeichnisse, Fußnoten, Beschriftungen, Index, Zitate |
| [Überprüfen](#überprüfen) | Prüfen, Kommentare, Änderungen verfolgen, Vergleichen, Schützen |
| [Schreibhilfe](#schreibhilfe) | Was das Lesen und Schreiben erleichtert — der zentrale Reiter |
| [Ansicht](#ansicht) | Ansichten, Zoom, Fenster, Helligkeit, Oberfläche |
| [Abschnitt](#abschnitt) | Abschnitte, Seitenformat und Kopf-/Fußzeile je Abschnitt |
| [Sendungen](#sendungen) | Umschläge, Etiketten, Seriendruck (standardmäßig ausgeblendet) |
| [Kontext-Reiter](#kontext-reiter) | Tabellentools, Bildtools, Zeichentools, SmartArt-Design, Diagrammtools, Texttools, Kopf- und Fußzeile, Mailings |

---

## Datei

```
DATEI
├── Neu
│ ├── Leeres Dokument
│ ├── Aus Vorlage erstellen
│ └── Vorlagen durchsuchen
├── Öffnen
│ ├── Öffnen
│ └── Zuletzt verwendete Dokumente
├── Speichern
│ ├── Speichern
│ ├── Speichern unter
│ └── Kopie speichern
├── Exportieren
│ ├── Als PDF exportieren
│ ├── Als DOCX exportieren
│ ├── Als RTF exportieren
│ ├── Als TXT exportieren
│ ├── Als ODT exportieren
│ └── Als Bild exportieren (PNG)
├── Drucken
│ ├── Drucken
│ ├── Druckvorschau
│ ├── Drucker auswählen
│ ├── Seitenbereich
│ └── Druckeinstellungen
├── Dokument
│ ├── Dokumentinformationen
│ ├── Dokument schützen
│ └── Dokument teilen (optional)
└── Programm
  ├── Optionen / Einstellungen
  └── Schließen
```

---

## Start

```
START
├── Zwischenablage
│ ├── Einfügen
│ ├── Ausschneiden
│ ├── Kopieren
│ └── Format übertragen
├── Schriftart
│ ├── Schrift vergrößern
│ ├── Schrift verkleinern
│ ├── Formatierung löschen
│ ├── Groß-/Kleinschreibung
│ ├── Fett
│ ├── Kursiv
│ ├── Unterstrichen
│ ├── Durchgestrichen
│ ├── Hochgestellt
│ ├── Tiefgestellt
│ ├── Texteffekte
│ ├── Hervorheben
│ ├── Schriftfarbe
│ └── Zeichenschattierung
├── Absatz
│ ├── Aufzählung
│ ├── Nummerierung
│ ├── Einzug verringern
│ ├── Einzug vergrößern
│ ├── Textrichtung
│ │ ├── Von links nach rechts
│ │ └── Von rechts nach links
│ ├── Sortieren
│ ├── Umbrüche
│ │ ├── Zeilenumbruch
│ │ ├── Seitenumbruch
│ │ ├── Spaltenumbruch
│ │ └── Textflussumbruch
│ ├── Tabulatoren
│ ├── Linksbündig
│ ├── Zentriert
│ ├── Rechtsbündig
│ ├── Blocksatz
│ ├── Verteilt
│ ├── Zeilenabstand
│ ├── Absatzschattierung
│ └── Absatzrahmen
├── Stile
├── Extras
│ └── Wort-Extras
├── Suchen
│ └── Suchen oder ersetzen
├── Auswählen
│ └── Auswählen
└── Einstellungen
  └── Einstellungen
```

---

## Einfügen

```
EINFÜGEN
├── Seiten
│ ├── Deckblatt
│ ├── Leere Seite
│ └── Umbrüche
├── Tabellen
│ └── Tabelle
├── Illustrationen
│ ├── Bild
│ ├── Formen
│ ├── Diagramm
│ └── SmartArt
├── Kommentar
│ └── Kommentar
├── Kopf- und Fußzeile
│ ├── Kopf- und Fußzeile
│ ├── Seitenzahl
│ └── Wasserzeichen
├── Text
│ ├── Textfeld
│ ├── WordArt
│ ├── Datum und Uhrzeit
│ ├── Objekt
│ │ ├── Objekt einfügen
│ │ └── Objekt aus Datei
│ ├── Initiale
│ └── Schnellbausteine
├── Symbole
│ ├── Symbol
│ ├── Gleichung
│ └── Zahl
├── Links
│ ├── Hyperlink
│ ├── Querverweis
│ └── Lesezeichen
└── Formulare
  └── Formulare
    ├── Textfeld
    ├── Auswahlliste
    ├── Datumsfeld
    ├── Kontrollkästchen
    ├── Schaltfläche
    └── Felder zurücksetzen
```

---

## Seitenlayout

```
SEITENLAYOUT
├── Designs
│ ├── Designs
│ ├── Farben
│ ├── Schriftarten
│ └── Effekte
├── Ränder
│ └── Ränder
├── Seite einrichten
│ ├── Orientierung
│ ├── Größe
│ ├── Spalten
│ ├── Textrichtung
│ ├── Umbrüche
│ └── Zeilennummern
├── Seitenhintergrund
│ ├── Seitenfarbe
│ ├── Seitenränder
│ └── Genko-Einstellung
├── Anordnen
│ ├── Textfluss
│ ├── Ausrichten
│ ├── Gruppieren
│ ├── Drehen
│ └── Auswahlbereich
└── Absatz
  ├── Einzug
  └── Absatzabstand
```

---

## Verweise

```
VERWEISE
├── Inhaltsverzeichnis
│ ├── Inhaltsverzeichnis
│ └── Inhaltsverzeichnis aktualisieren
├── Fußnoten
│ ├── Fußnote einfügen
│ ├── Endnote einfügen
│ ├── Zur Note springen
│ │ ├── Vorherige Fußnote
│ │ ├── Nächste Fußnote
│ │ ├── Vorherige Endnote
│ │ └── Nächste Endnote
│ ├── Fußnote/Endnotentrennlinie
│ └── Notenbereich
├── Beschriftungen
│ ├── Beschriftung
│ ├── Abbildungsverzeichnis
│ └── Querverweis
├── Index
│ ├── Eintrag festlegen
│ └── Index
│   ├── Index einfügen
│   └── Index aktualisieren
├── Seriendruck
│ └── Seriendruck
└── Zitate und Literatur
  ├── Zitat einfügen
  ├── Neue Quelle
  ├── Quellen verwalten
  ├── Zitierweise
  └── Literaturverzeichnis
```

---

## Überprüfen

```
ÜBERPRÜFEN
├── Dokumentprüfung
│ ├── Rechtschreibprüfung
│ └── Wörter zählen
├── Kommentare
│ ├── Kommentar einfügen
│ ├── Löschen
│ ├── Vorherige
│ └── Weiter
├── Nachverfolgung
│ ├── Änderungen nachverfolgen
│ ├── Anzeige zur Überprüfung
│ └── Überprüfen
├── Änderungen
│ ├── Annehmen
│ ├── Ablehnen
│ ├── Vorherige
│ └── Weiter
├── Vergleichen
│ └── Vergleichen
├── Freihand
│ └── Freihand
└── Schützen
  └── Bearbeitung einschränken
```

---

## Schreibhilfe

```
SCHREIBHILFE
├── Lesen
│ ├── Zeilenfokus
│ ├── Lesemodus
│ ├── Silben farbig
│ └── Lesehilfe
├── Prüfen
│ └── Dokumentprüfung
│   ├── Prüfen
│   ├── Gründlich prüfen
│   ├── KI-Korrektur
│   ├── Verbesserungsvorschläge
│   ├── Barrierefreiheit prüfen
│   ├── Welche Hilfe wann
│   └── Korrektursprache …
├── Beim Schreiben
│ ├── Wellenlinien
│ ├── Wortvorhersage
│ └── AutoKorrektur
├── Vorlesen
│ └── Vorlesen
│   ├── Vorlesen
│   ├── Ab hier vorlesen
│   ├── Anhalten
│   └── Stimme und Tempo
├── Sprache
│ ├── Thesaurus
│ ├── Sprache
│ ├── Übersetzen
│ └── Silbentrennung
├── Bausteine
│ └── Textbausteine
│   ├── Bausteine verwalten…
│   └── Schnellbaustein einfügen
├── KI
│ ├── Text mit KI
│ │ ├── Text entwerfen
│ │ ├── Text umformulieren
│ │ ├── Text zusammenfassen
│ │ └── Text in Bild
│ ├── KI-Chat
│ ├── KI-Aktionen
│ └── KI-Einstellungen
└── Anzeigen
  └── Seitenleiste Schreibhilfe
```

---

## Ansicht

```
ANSICHT
├── Dokumentansichten
│ ├── Drucklayout
│ ├── Lesemodus
│ └── Weitere Ansichten
│   ├── Vollbild
│   ├── Weblayout
│   └── Gliederung
├── Anzeigen
│ ├── Navigationsbereich
│ ├── Lineal
│ ├── Gitternetzlinien
│ └── Weitere Anzeigen
│   ├── Vertikales Lineal
│   ├── Textbegrenzungen
│   ├── Steuerzeichen
│   └── Ausgeblendeter Text
├── Zoom
│ ├── Zoom
│ ├── 100 %
│ ├── Seitenbreite
│ ├── Eine Seite
│ ├── Zwei Seiten
│ ├── Vergrößern
│ └── Verkleinern
├── Helligkeit
│ ├── Wie das System
│ ├── Immer hell
│ └── Immer dunkel
├── Fenster
│ ├── Neues Fenster
│ └── Anordnen
│   ├── Nebeneinander
│   ├── Untereinander
│   ├── Kacheln
│   └── Fensterliste
└── Oberfläche
  ├── Register anpassen
  ├── Symbol austauschen
  ├── Benutzeroberfläche
  ├── Menüleiste
  ├── Symbolleisten
  └── Vorlagen zurücksetzen
```

---

## Abschnitt

```
ABSCHNITT
├── Navigation
│ └── Abschnittsnavigationsbereich
├── Seite
│ ├── Deckblätter
│ ├── Ränder
│ │ ├── Normal
│ │ ├── Schmal
│ │ ├── Moderat
│ │ ├── Breit
│ │ └── Benutzerdefinierte Seitenränder…
│ ├── Orientierung
│ │ ├── Hochformat
│ │ └── Querformat
│ └── Größe
│   ├── A4
│   ├── A3
│   ├── A5
│   ├── B5
│   ├── Letter
│   ├── Legal
│   ├── Umschlag DIN lang
│   ├── Umschlag C5
│   ├── Umschlag C6
│   └── Weitere Papierformate…
├── Abschnitte
│ ├── Abschnitt hinzufügen
│ │ ├── Abschnittsumbruch auf nächster Seite
│ │ ├── Fortlaufender Abschnittsumbruch
│ │ ├── Abschnittsumbruch (gerade Seite)
│ │ └── Abschnittsumbruch auf ungerader Seite
│ ├── Abschnitt löschen
│ ├── Abschnitt einrichten …
│ ├── Vorheriger Abschnitt
│ └── Nächster Abschnitt
├── Kopf- und Fußzeile
│ ├── Seitenzahl
│ ├── Erste Seite anders
│ ├── Gerade und ungerade Seiten sind unterschiedlich
│ ├── Kopf- und Fußzeile
│ ├── Link zu vorheriger Kopfzeile
│ └── Mit voriger Fußzeile verknüpfen
└── Einstellungen
  └── Einstellungen
    └── Optionen …
```

---

## Sendungen

```
SENDUNGEN
├── Erstellen
│ ├── Umschlag
│ └── Etiketten
├── Seriendruck
│ ├── Seriendruck-Assistent
│ ├── Seriendruckfeld
│ ├── Adressblock
│ └── Regeln
├── Vorschau
│ └── Ergebnisse anzeigen
└── Formular
  ├── Textfeld
  ├── Kontrollkästchen
  ├── Schaltfläche
  ├── Auswahlliste
  ├── Datumsfeld
  └── Felder zurücksetzen
```

---

## Kontext-Reiter

Diese Reiter erscheinen am rechten Ende der Reiterzeile, sobald das passende Objekt markiert ist (Tabelle, Bild, Form, SmartArt, Diagramm, Textfeld oder WordArt), in Kopf- oder Fußzeile bzw. im Seriendruck.

| Reiter | Erscheint bei |
|---|---|
| Tabellentools | Zeiger in einer Tabelle |
| Bildtools | markiertes Bild |
| Zeichentools | markierte Form |
| SmartArt-Design | markiertes SmartArt |
| Diagrammtools | markiertes Diagramm |
| Zeichentools | Zeichnen/markiertes Zeichenobjekt |
| Texttools | markiertes WordArt oder Textfeld |
| Kopf- und Fußzeile | Bearbeitung von Kopf- oder Fußzeile |
| Mailings | Seriendruck (Verweise ▸ Seriendruck) |

```
TABELLENTOOLS
├── Tabellenformatvorlagen
│ ├── Tabellenformatvorlagen
│ ├── Kopfzeile
│ ├── Gebänderte Zeilen
│ └── Erste Spalte
├── Entwurf: Rahmen und Farbe
│ ├── Rahmenlinien ein/aus
│ └── Zellenschattierung
├── Layout: Zeilen und Spalten
│ ├── Zeile oberhalb einfügen
│ ├── Zeile unterhalb einfügen
│ ├── Spalte links einfügen
│ ├── Spalte rechts einfügen
│ ├── Zeile löschen
│ ├── Spalte löschen
│ └── Tabelle löschen
├── Zellen
│ ├── Zellen verbinden
│ ├── Zelle teilen
│ └── Tabelle sortieren
└── Ausrichtung
  ├── Oben ausrichten
  ├── Mittig ausrichten
  └── Unten ausrichten
```

```
BILDTOOLS
├── Bild
│ ├── Bild einfügen
│ ├── Bild ändern
│ └── Formen
├── Komprimieren
│ └── Bilder komprimieren
├── Größe
│ ├── Zuschneiden
│ ├── Seitenverhältnis sperren
│ └── Größe zurücksetzen
├── Farbe
│ ├── Transparente Farbe einstellen
│ ├── Farbe
│ ├── Heller
│ ├── Dunkler
│ ├── Kontrast erhöhen
│ ├── Kontrast verringern
│ ├── Um 90° nach rechts drehen
│ ├── Um 90° nach links drehen
│ ├── Bildeffekte
│ ├── Rahmen
│ └── Bild zurücksetzen
├── Anordnen
│ ├── Frei drehen
│ ├── Gruppieren
│ ├── Ausrichten
│ ├── Textumbruch Stil
│ ├── Eine Ebene nach vorne
│ └── Eine Ebene nach hinten
└── Weitere
  ├── Größe und Seitenverhältnis …
  ├── Auf Seitenbreite
  ├── Originalgröße
  ├── Alternativtext …
  ├── Bild entfernen
  └── Zuschneiden nach Maß …
```

```
ZEICHENTOOLS
├── Formen
│ └── Formen einfügen
├── Formvorlagen
│ └── Formvorlagen
├── Formenstile
│ ├── Formfüllung
│ ├── Formkontur
│ └── Text in der Form …
└── Anordnen
  ├── Gruppieren
  ├── Gruppierung aufheben
  └── Textumbruch / Position
```

```
SMARTART-DESIGN
├── Grafik erstellen
│ ├── Form einfügen
│ ├── Aufzählungszeichen einfügen
│ ├── Level erhöhen
│ ├── Level reduzieren
│ ├── Vorwärts
│ ├── Rückwärts
│ ├── Layout von rechts nach links
│ └── Layout
├── Layouts
│ ├── Layout ändern
│ └── Farben ändern
├── SmartArt-Stile
├── Anordnen
│ ├── Textfluss
│ ├── Ausrichten
│ ├── Auswahlbereich
│ ├── Eine Ebene nach vorne
│ └── Eine Ebene nach hinten
└── Größe
```

```
DIAGRAMMTOOLS
├── Elemente
│ ├── Diagrammelement hinzufügen
│ ├── Schnelllayout
│ └── Farbe ändern
├── Diagrammstile
├── Diagrammtyp
│ ├── Diagrammtyp ändern
│ ├── Diagrammtyp: Säule
│ ├── Diagrammtyp: Kombination
│ ├── Diagrammtyp: Balken
│ ├── Diagrammtyp: Fläche
│ ├── Diagrammtyp: Linie
│ ├── Diagrammtyp: Kreis
│ ├── Diagrammtyp: Netz
│ ├── Diagrammtyp: Ring
│ ├── Diagrammtyp: Kurs
│ └── Diagrammtyp: Punkt (XY)
├── Daten
│ ├── Daten auswählen
│ └── Daten bearbeiten
└── Bereich
```

```
ZEICHENTOOLS
├── Linien
├── Formen
│ ├── Formen einfügen
│ ├── Textfeld
│ └── Form bearbeiten
├── Formstile
├── Formen formatieren
│ ├── Formfüllung
│ ├── Gliederung
│ ├── Format übertragen
│ └── Formeffekte
├── Anordnen
│ ├── Ausrichten
│ ├── Gruppieren
│ ├── Drehen
│ ├── Textumbruch Stil
│ ├── Eine Ebene nach vorne
│ ├── Eine Ebene nach hinten
│ └── Auswahlbereich
└── Größe
```

```
TEXTTOOLS
├── Textfeld
│ └── Textfeld
├── Format
│ └── Format übertragen
├── Schriftart
│ ├── Schrift vergrößern
│ ├── Schrift verkleinern
│ ├── Formatierung löschen
│ ├── Fett
│ ├── Kursiv
│ ├── Unterstrichen
│ ├── Durchgestrichen
│ ├── Hochgestellt
│ ├── Tiefgestellt
│ ├── Hervorhebung
│ └── Schriftfarbe
├── Absatz
│ ├── Aufzählung
│ ├── Nummerierung
│ ├── Einzug verringern
│ ├── Einzug vergrößern
│ ├── Textrichtung
│ ├── Sortieren
│ ├── Linksbündig
│ ├── Zentriert
│ ├── Rechtsbündig
│ ├── Blocksatz
│ ├── Verteilt
│ └── Zeilenabstand
├── WordArt-Stile
├── Text
│ ├── Textfüllung
│ ├── Textkontur
│ └── Texteffekte
├── Formstile
├── Form
│ ├── Füllung
│ ├── Kontur
│ └── Formeffekte
├── Verknüpfung
│ ├── Verknüpfung erstellen
│ ├── Voriges Textobjekt
│ └── Nächstes Textobjekt
└── Einstellungen
  └── Einstellungen
```

```
KOPF- UND FUSSZEILE
├── Einfügen
│ ├── Kopf-/Fußzeilengruppe
│ ├── Kopfzeile
│ ├── Fußzeile
│ ├── Seitenzahl
│ └── Kopfzeilen
├── Felder
│ ├── Datum und Uhrzeit
│ ├── Bild
│ └── Felder
├── Navigation
│ ├── Zwischen Kopf- und Fußzeile wechseln
│ ├── Vorige Kopfzeile
│ ├── Nächste Kopfzeile
│ └── Mit vorheriger verknüpfen
├── Optionen
│ ├── Optionen für Kopf- und Fußzeile
│ ├── Ausrichtungstabstopp einfügen
│ ├── Kopfzeilenhöhe
│ └── Fußzeilenhöhe
└── Schließen
  ├── Einstellungen
  └── Schließen
```

```
MAILINGS
├── Datenquelle
│ ├── Datenquelle öffnen
│ └── Seriendruckempfänger
├── Felder
│ ├── Seriendruckfeld einfügen
│ ├── Nächstes Feld einfügen
│ ├── Seriendruckfelder hervorheben
│ └── Übereinstimmende Felder festlegen
├── Vorschau
│ ├── Seriendruck-Vorschau
│ ├── Erster Datensatz
│ ├── Vorheriger Datensatz
│ ├── Datensatz
│ ├── Nächster Datensatz
│ └── Letzter Datensatz
└── Fertigstellen
  ├── In neuem Dokument zusammenführen
  ├── In anderem neuen Dokument zusammenführen
  ├── An Drucker zusammenführen
  └── Seriendruck schließen
```

---

## Wo finde ich was?

Alphabetisch. Steht ein Befehl an mehreren Stellen, sind alle
genannt — das ist Absicht: ein Schalter, mehrere Stellen, ein Zustand.

| Befehl | Wo er steht |
|---|---|
| 100 % | Ansicht ▸ Zoom |
| A3 | Abschnitt ▸ Seite |
| A4 | Abschnitt ▸ Seite |
| A5 | Abschnitt ▸ Seite |
| Ab hier vorlesen | Schreibhilfe ▸ Vorlesen |
| Abbildungsverzeichnis | Verweise ▸ Beschriftungen |
| Ablehnen | Überprüfen ▸ Änderungen |
| Absatzabstand | Seitenlayout ▸ Absatz |
| Absatzrahmen | Start ▸ Absatz |
| Absatzschattierung | Start ▸ Absatz |
| Abschnitt einrichten … | Abschnitt ▸ Abschnitte |
| Abschnitt hinzufügen | Abschnitt ▸ Abschnitte |
| Abschnitt löschen | Abschnitt ▸ Abschnitte |
| Abschnittsnavigationsbereich | Abschnitt ▸ Navigation |
| Abschnittsumbruch (gerade Seite) | Abschnitt ▸ Abschnitte |
| Abschnittsumbruch auf nächster Seite | Abschnitt ▸ Abschnitte |
| Abschnittsumbruch auf ungerader Seite | Abschnitt ▸ Abschnitte |
| Adressblock | Sendungen ▸ Seriendruck |
| Als Bild exportieren (PNG) | Datei ▸ Exportieren |
| Als DOCX exportieren | Datei ▸ Exportieren |
| Als ODT exportieren | Datei ▸ Exportieren |
| Als PDF exportieren | Datei ▸ Exportieren |
| Als RTF exportieren | Datei ▸ Exportieren |
| Als TXT exportieren | Datei ▸ Exportieren |
| Alternativtext … | Bildtools ▸ Weitere |
| An Drucker zusammenführen | Mailings ▸ Fertigstellen |
| Änderungen nachverfolgen | Überprüfen ▸ Nachverfolgung |
| Anhalten | Schreibhilfe ▸ Vorlesen |
| Annehmen | Überprüfen ▸ Änderungen |
| Anordnen | Ansicht ▸ Fenster |
| Anzeige zur Überprüfung | Überprüfen ▸ Nachverfolgung |
| Auf Seitenbreite | Bildtools ▸ Weitere |
| Aufzählung | Start ▸ Absatz · Texttools ▸ Absatz |
| Aufzählungszeichen einfügen | SmartArt-Design ▸ Grafik erstellen |
| Aus Vorlage erstellen | Datei ▸ Neu |
| Ausgeblendeter Text | Ansicht ▸ Anzeigen |
| Ausrichten | Seitenlayout ▸ Anordnen · Bildtools ▸ Anordnen · SmartArt-Design ▸ Anordnen · Zeichentools ▸ Anordnen |
| Ausrichtungstabstopp einfügen | Kopf- und Fußzeile ▸ Optionen |
| Ausschneiden | Start ▸ Zwischenablage |
| Auswahlbereich | Seitenlayout ▸ Anordnen · SmartArt-Design ▸ Anordnen · Zeichentools ▸ Anordnen |
| Auswählen | Start ▸ Auswählen |
| Auswahlliste | Einfügen ▸ Formulare · Sendungen ▸ Formular |
| AutoKorrektur | Schreibhilfe ▸ Beim Schreiben |
| B5 | Abschnitt ▸ Seite |
| Barrierefreiheit prüfen | Schreibhilfe ▸ Prüfen |
| Bausteine verwalten… | Schreibhilfe ▸ Bausteine |
| Bearbeitung einschränken | Überprüfen ▸ Schützen |
| Benutzerdefinierte Seitenränder… | Abschnitt ▸ Seite |
| Benutzeroberfläche | Ansicht ▸ Oberfläche |
| Beschriftung | Verweise ▸ Beschriftungen |
| Bild | Einfügen ▸ Illustrationen · Kopf- und Fußzeile ▸ Felder |
| Bild ändern | Bildtools ▸ Bild |
| Bild einfügen | Bildtools ▸ Bild |
| Bild entfernen | Bildtools ▸ Weitere |
| Bild zurücksetzen | Bildtools ▸ Farbe |
| Bildeffekte | Bildtools ▸ Farbe |
| Bilder komprimieren | Bildtools ▸ Komprimieren |
| Blocksatz | Start ▸ Absatz · Texttools ▸ Absatz |
| Breit | Abschnitt ▸ Seite |
| Daten auswählen | Diagrammtools ▸ Daten |
| Daten bearbeiten | Diagrammtools ▸ Daten |
| Datenquelle öffnen | Mailings ▸ Datenquelle |
| Datensatz | Mailings ▸ Vorschau |
| Datum und Uhrzeit | Einfügen ▸ Text · Kopf- und Fußzeile ▸ Felder |
| Datumsfeld | Einfügen ▸ Formulare · Sendungen ▸ Formular |
| Deckblatt | Einfügen ▸ Seiten |
| Deckblätter | Abschnitt ▸ Seite |
| Designs | Seitenlayout ▸ Designs |
| Diagramm | Einfügen ▸ Illustrationen |
| Diagrammelement hinzufügen | Diagrammtools ▸ Elemente |
| Diagrammtyp ändern | Diagrammtools ▸ Diagrammtyp |
| Diagrammtyp: Balken | Diagrammtools ▸ Diagrammtyp |
| Diagrammtyp: Fläche | Diagrammtools ▸ Diagrammtyp |
| Diagrammtyp: Kombination | Diagrammtools ▸ Diagrammtyp |
| Diagrammtyp: Kreis | Diagrammtools ▸ Diagrammtyp |
| Diagrammtyp: Kurs | Diagrammtools ▸ Diagrammtyp |
| Diagrammtyp: Linie | Diagrammtools ▸ Diagrammtyp |
| Diagrammtyp: Netz | Diagrammtools ▸ Diagrammtyp |
| Diagrammtyp: Punkt (XY) | Diagrammtools ▸ Diagrammtyp |
| Diagrammtyp: Ring | Diagrammtools ▸ Diagrammtyp |
| Diagrammtyp: Säule | Diagrammtools ▸ Diagrammtyp |
| Dokument schützen | Datei ▸ Dokument |
| Dokument teilen (optional) | Datei ▸ Dokument |
| Dokumentinformationen | Datei ▸ Dokument |
| Dokumentprüfung | Schreibhilfe ▸ Prüfen |
| Drehen | Seitenlayout ▸ Anordnen · Zeichentools ▸ Anordnen |
| Druckeinstellungen | Datei ▸ Drucken |
| Drucken | Datei ▸ Drucken |
| Drucker auswählen | Datei ▸ Drucken |
| Drucklayout | Ansicht ▸ Dokumentansichten |
| Druckvorschau | Datei ▸ Drucken |
| Dunkler | Bildtools ▸ Farbe |
| Durchgestrichen | Start ▸ Schriftart · Texttools ▸ Schriftart |
| Effekte | Seitenlayout ▸ Designs |
| Eine Ebene nach hinten | Bildtools ▸ Anordnen · SmartArt-Design ▸ Anordnen · Zeichentools ▸ Anordnen |
| Eine Ebene nach vorne | Bildtools ▸ Anordnen · SmartArt-Design ▸ Anordnen · Zeichentools ▸ Anordnen |
| Eine Seite | Ansicht ▸ Zoom |
| Einfügen | Start ▸ Zwischenablage |
| Einstellungen | Start ▸ Einstellungen · Abschnitt ▸ Einstellungen · Texttools ▸ Einstellungen · Kopf- und Fußzeile ▸ Schließen |
| Eintrag festlegen | Verweise ▸ Index |
| Einzug | Seitenlayout ▸ Absatz |
| Einzug vergrößern | Start ▸ Absatz · Texttools ▸ Absatz |
| Einzug verringern | Start ▸ Absatz · Texttools ▸ Absatz |
| Endnote einfügen | Verweise ▸ Fußnoten |
| Ergebnisse anzeigen | Sendungen ▸ Vorschau |
| Erste Seite anders | Abschnitt ▸ Kopf- und Fußzeile |
| Erste Spalte | Tabellentools ▸ Tabellenformatvorlagen |
| Erster Datensatz | Mailings ▸ Vorschau |
| Etiketten | Sendungen ▸ Erstellen |
| Farbe | Bildtools ▸ Farbe |
| Farbe ändern | Diagrammtools ▸ Elemente |
| Farben | Seitenlayout ▸ Designs |
| Farben ändern | SmartArt-Design ▸ Layouts |
| Felder | Kopf- und Fußzeile ▸ Felder |
| Felder zurücksetzen | Einfügen ▸ Formulare · Sendungen ▸ Formular |
| Fensterliste | Ansicht ▸ Fenster |
| Fett | Start ▸ Schriftart · Texttools ▸ Schriftart |
| Form bearbeiten | Zeichentools ▸ Formen |
| Form einfügen | SmartArt-Design ▸ Grafik erstellen |
| Format übertragen | Start ▸ Zwischenablage · Zeichentools ▸ Formen formatieren · Texttools ▸ Format |
| Formatierung löschen | Start ▸ Schriftart · Texttools ▸ Schriftart |
| Formeffekte | Zeichentools ▸ Formen formatieren · Texttools ▸ Form |
| Formen | Einfügen ▸ Illustrationen · Bildtools ▸ Bild |
| Formen einfügen | Zeichentools ▸ Formen |
| Formfüllung | Zeichentools ▸ Formenstile · Zeichentools ▸ Formen formatieren |
| Formkontur | Zeichentools ▸ Formenstile |
| Formulare | Einfügen ▸ Formulare |
| Formvorlagen | Zeichentools ▸ Formvorlagen |
| Fortlaufender Abschnittsumbruch | Abschnitt ▸ Abschnitte |
| Frei drehen | Bildtools ▸ Anordnen |
| Freihand | Überprüfen ▸ Freihand |
| Füllung | Texttools ▸ Form |
| Fußnote einfügen | Verweise ▸ Fußnoten |
| Fußnote/Endnotentrennlinie | Verweise ▸ Fußnoten |
| Fußzeile | Kopf- und Fußzeile ▸ Einfügen |
| Fußzeilenhöhe | Kopf- und Fußzeile ▸ Optionen |
| Gebänderte Zeilen | Tabellentools ▸ Tabellenformatvorlagen |
| Genko-Einstellung | Seitenlayout ▸ Seitenhintergrund |
| Gerade und ungerade Seiten sind unterschiedlich | Abschnitt ▸ Kopf- und Fußzeile |
| Gitternetzlinien | Ansicht ▸ Anzeigen |
| Gleichung | Einfügen ▸ Symbole |
| Gliederung | Ansicht ▸ Dokumentansichten · Zeichentools ▸ Formen formatieren |
| Groß-/Kleinschreibung | Start ▸ Schriftart |
| Größe | Seitenlayout ▸ Seite einrichten · Abschnitt ▸ Seite |
| Größe und Seitenverhältnis … | Bildtools ▸ Weitere |
| Größe zurücksetzen | Bildtools ▸ Größe |
| Gründlich prüfen | Schreibhilfe ▸ Prüfen |
| Gruppieren | Seitenlayout ▸ Anordnen · Bildtools ▸ Anordnen · Zeichentools ▸ Anordnen |
| Gruppierung aufheben | Zeichentools ▸ Anordnen |
| Heller | Bildtools ▸ Farbe |
| Hervorheben | Start ▸ Schriftart |
| Hervorhebung | Texttools ▸ Schriftart |
| Hochformat | Abschnitt ▸ Seite |
| Hochgestellt | Start ▸ Schriftart · Texttools ▸ Schriftart |
| Hyperlink | Einfügen ▸ Links |
| Immer dunkel | Ansicht ▸ Helligkeit |
| Immer hell | Ansicht ▸ Helligkeit |
| In anderem neuen Dokument zusammenführen | Mailings ▸ Fertigstellen |
| In neuem Dokument zusammenführen | Mailings ▸ Fertigstellen |
| Index | Verweise ▸ Index |
| Index aktualisieren | Verweise ▸ Index |
| Index einfügen | Verweise ▸ Index |
| Inhaltsverzeichnis | Verweise ▸ Inhaltsverzeichnis |
| Inhaltsverzeichnis aktualisieren | Verweise ▸ Inhaltsverzeichnis |
| Initiale | Einfügen ▸ Text |
| Kacheln | Ansicht ▸ Fenster |
| KI-Aktionen | Schreibhilfe ▸ KI |
| KI-Chat | Schreibhilfe ▸ KI |
| KI-Einstellungen | Schreibhilfe ▸ KI |
| KI-Korrektur | Schreibhilfe ▸ Prüfen |
| Kommentar | Einfügen ▸ Kommentar |
| Kommentar einfügen | Überprüfen ▸ Kommentare |
| Kontrast erhöhen | Bildtools ▸ Farbe |
| Kontrast verringern | Bildtools ▸ Farbe |
| Kontrollkästchen | Einfügen ▸ Formulare · Sendungen ▸ Formular |
| Kontur | Texttools ▸ Form |
| Kopf- und Fußzeile | Einfügen ▸ Kopf- und Fußzeile · Abschnitt ▸ Kopf- und Fußzeile |
| Kopf-/Fußzeilengruppe | Kopf- und Fußzeile ▸ Einfügen |
| Kopfzeile | Tabellentools ▸ Tabellenformatvorlagen · Kopf- und Fußzeile ▸ Einfügen |
| Kopfzeilen | Kopf- und Fußzeile ▸ Einfügen |
| Kopfzeilenhöhe | Kopf- und Fußzeile ▸ Optionen |
| Kopie speichern | Datei ▸ Speichern |
| Kopieren | Start ▸ Zwischenablage |
| Korrektursprache … | Schreibhilfe ▸ Prüfen |
| Kursiv | Start ▸ Schriftart · Texttools ▸ Schriftart |
| Layout | SmartArt-Design ▸ Grafik erstellen |
| Layout ändern | SmartArt-Design ▸ Layouts |
| Layout von rechts nach links | SmartArt-Design ▸ Grafik erstellen |
| Leere Seite | Einfügen ▸ Seiten |
| Leeres Dokument | Datei ▸ Neu |
| Legal | Abschnitt ▸ Seite |
| Lesehilfe | Schreibhilfe ▸ Lesen |
| Lesemodus | Schreibhilfe ▸ Lesen · Ansicht ▸ Dokumentansichten |
| Lesezeichen | Einfügen ▸ Links |
| Letter | Abschnitt ▸ Seite |
| Letzter Datensatz | Mailings ▸ Vorschau |
| Level erhöhen | SmartArt-Design ▸ Grafik erstellen |
| Level reduzieren | SmartArt-Design ▸ Grafik erstellen |
| Lineal | Ansicht ▸ Anzeigen |
| Link zu vorheriger Kopfzeile | Abschnitt ▸ Kopf- und Fußzeile |
| Linksbündig | Start ▸ Absatz · Texttools ▸ Absatz |
| Literaturverzeichnis | Verweise ▸ Zitate und Literatur |
| Löschen | Überprüfen ▸ Kommentare |
| Menüleiste | Ansicht ▸ Oberfläche |
| Mit vorheriger verknüpfen | Kopf- und Fußzeile ▸ Navigation |
| Mit voriger Fußzeile verknüpfen | Abschnitt ▸ Kopf- und Fußzeile |
| Mittig ausrichten | Tabellentools ▸ Ausrichtung |
| Moderat | Abschnitt ▸ Seite |
| Nächste Endnote | Verweise ▸ Fußnoten |
| Nächste Fußnote | Verweise ▸ Fußnoten |
| Nächste Kopfzeile | Kopf- und Fußzeile ▸ Navigation |
| Nächster Abschnitt | Abschnitt ▸ Abschnitte |
| Nächster Datensatz | Mailings ▸ Vorschau |
| Nächstes Feld einfügen | Mailings ▸ Felder |
| Nächstes Textobjekt | Texttools ▸ Verknüpfung |
| Navigationsbereich | Ansicht ▸ Anzeigen |
| Nebeneinander | Ansicht ▸ Fenster |
| Neue Quelle | Verweise ▸ Zitate und Literatur |
| Neues Fenster | Ansicht ▸ Fenster |
| Normal | Abschnitt ▸ Seite |
| Notenbereich | Verweise ▸ Fußnoten |
| Nummerierung | Start ▸ Absatz · Texttools ▸ Absatz |
| Oben ausrichten | Tabellentools ▸ Ausrichtung |
| Objekt | Einfügen ▸ Text |
| Objekt aus Datei | Einfügen ▸ Text |
| Objekt einfügen | Einfügen ▸ Text |
| Öffnen | Datei ▸ Öffnen |
| Optionen / Einstellungen | Datei ▸ Programm |
| Optionen für Kopf- und Fußzeile | Kopf- und Fußzeile ▸ Optionen |
| Optionen … | Abschnitt ▸ Einstellungen |
| Orientierung | Seitenlayout ▸ Seite einrichten · Abschnitt ▸ Seite |
| Originalgröße | Bildtools ▸ Weitere |
| Prüfen | Schreibhilfe ▸ Prüfen |
| Quellen verwalten | Verweise ▸ Zitate und Literatur |
| Querformat | Abschnitt ▸ Seite |
| Querverweis | Einfügen ▸ Links · Verweise ▸ Beschriftungen |
| Rahmen | Bildtools ▸ Farbe |
| Rahmenlinien ein/aus | Tabellentools ▸ Entwurf: Rahmen und Farbe |
| Ränder | Seitenlayout ▸ Ränder · Abschnitt ▸ Seite |
| Rechtsbündig | Start ▸ Absatz · Texttools ▸ Absatz |
| Rechtschreibprüfung | Überprüfen ▸ Dokumentprüfung |
| Regeln | Sendungen ▸ Seriendruck |
| Register anpassen | Ansicht ▸ Oberfläche |
| Rückwärts | SmartArt-Design ▸ Grafik erstellen |
| Schaltfläche | Einfügen ▸ Formulare · Sendungen ▸ Formular |
| Schließen | Datei ▸ Programm · Kopf- und Fußzeile ▸ Schließen |
| Schmal | Abschnitt ▸ Seite |
| Schnellbaustein einfügen | Schreibhilfe ▸ Bausteine |
| Schnellbausteine | Einfügen ▸ Text |
| Schnelllayout | Diagrammtools ▸ Elemente |
| Schrift vergrößern | Start ▸ Schriftart · Texttools ▸ Schriftart |
| Schrift verkleinern | Start ▸ Schriftart · Texttools ▸ Schriftart |
| Schriftarten | Seitenlayout ▸ Designs |
| Schriftfarbe | Start ▸ Schriftart · Texttools ▸ Schriftart |
| Seitenbereich | Datei ▸ Drucken |
| Seitenbreite | Ansicht ▸ Zoom |
| Seitenfarbe | Seitenlayout ▸ Seitenhintergrund |
| Seitenleiste Schreibhilfe | Schreibhilfe ▸ Anzeigen |
| Seitenränder | Seitenlayout ▸ Seitenhintergrund |
| Seitenumbruch | Start ▸ Absatz |
| Seitenverhältnis sperren | Bildtools ▸ Größe |
| Seitenzahl | Einfügen ▸ Kopf- und Fußzeile · Abschnitt ▸ Kopf- und Fußzeile · Kopf- und Fußzeile ▸ Einfügen |
| Seriendruck | Verweise ▸ Seriendruck |
| Seriendruck schließen | Mailings ▸ Fertigstellen |
| Seriendruck-Assistent | Sendungen ▸ Seriendruck |
| Seriendruck-Vorschau | Mailings ▸ Vorschau |
| Seriendruckempfänger | Mailings ▸ Datenquelle |
| Seriendruckfeld | Sendungen ▸ Seriendruck |
| Seriendruckfeld einfügen | Mailings ▸ Felder |
| Seriendruckfelder hervorheben | Mailings ▸ Felder |
| Silben farbig | Schreibhilfe ▸ Lesen |
| Silbentrennung | Schreibhilfe ▸ Sprache |
| SmartArt | Einfügen ▸ Illustrationen |
| Sortieren | Start ▸ Absatz · Texttools ▸ Absatz |
| Spalte links einfügen | Tabellentools ▸ Layout: Zeilen und Spalten |
| Spalte löschen | Tabellentools ▸ Layout: Zeilen und Spalten |
| Spalte rechts einfügen | Tabellentools ▸ Layout: Zeilen und Spalten |
| Spalten | Seitenlayout ▸ Seite einrichten |
| Spaltenumbruch | Start ▸ Absatz |
| Speichern | Datei ▸ Speichern |
| Speichern unter | Datei ▸ Speichern |
| Sprache | Schreibhilfe ▸ Sprache |
| Steuerzeichen | Ansicht ▸ Anzeigen |
| Stimme und Tempo | Schreibhilfe ▸ Vorlesen |
| Suchen oder ersetzen | Start ▸ Suchen |
| Symbol | Einfügen ▸ Symbole |
| Symbol austauschen | Ansicht ▸ Oberfläche |
| Symbolleisten | Ansicht ▸ Oberfläche |
| Tabelle | Einfügen ▸ Tabellen |
| Tabelle löschen | Tabellentools ▸ Layout: Zeilen und Spalten |
| Tabelle sortieren | Tabellentools ▸ Zellen |
| Tabellenformatvorlagen | Tabellentools ▸ Tabellenformatvorlagen |
| Tabulatoren | Start ▸ Absatz |
| Text entwerfen | Schreibhilfe ▸ KI |
| Text in Bild | Schreibhilfe ▸ KI |
| Text in der Form … | Zeichentools ▸ Formenstile |
| Text mit KI | Schreibhilfe ▸ KI |
| Text umformulieren | Schreibhilfe ▸ KI |
| Text zusammenfassen | Schreibhilfe ▸ KI |
| Textbausteine | Schreibhilfe ▸ Bausteine |
| Textbegrenzungen | Ansicht ▸ Anzeigen |
| Texteffekte | Start ▸ Schriftart · Texttools ▸ Text |
| Textfeld | Einfügen ▸ Text · Einfügen ▸ Formulare · Sendungen ▸ Formular · Zeichentools ▸ Formen · Texttools ▸ Textfeld |
| Textfluss | Seitenlayout ▸ Anordnen · SmartArt-Design ▸ Anordnen |
| Textflussumbruch | Start ▸ Absatz |
| Textfüllung | Texttools ▸ Text |
| Textkontur | Texttools ▸ Text |
| Textrichtung | Start ▸ Absatz · Seitenlayout ▸ Seite einrichten · Texttools ▸ Absatz |
| Textumbruch / Position | Zeichentools ▸ Anordnen |
| Textumbruch Stil | Bildtools ▸ Anordnen · Zeichentools ▸ Anordnen |
| Thesaurus | Schreibhilfe ▸ Sprache |
| Tiefgestellt | Start ▸ Schriftart · Texttools ▸ Schriftart |
| Transparente Farbe einstellen | Bildtools ▸ Farbe |
| Übereinstimmende Felder festlegen | Mailings ▸ Felder |
| Überprüfen | Überprüfen ▸ Nachverfolgung |
| Übersetzen | Schreibhilfe ▸ Sprache |
| Um 90° nach links drehen | Bildtools ▸ Farbe |
| Um 90° nach rechts drehen | Bildtools ▸ Farbe |
| Umbrüche | Start ▸ Absatz · Einfügen ▸ Seiten · Seitenlayout ▸ Seite einrichten |
| Umschlag | Sendungen ▸ Erstellen |
| Umschlag C5 | Abschnitt ▸ Seite |
| Umschlag C6 | Abschnitt ▸ Seite |
| Umschlag DIN lang | Abschnitt ▸ Seite |
| Unten ausrichten | Tabellentools ▸ Ausrichtung |
| Untereinander | Ansicht ▸ Fenster |
| Unterstrichen | Start ▸ Schriftart · Texttools ▸ Schriftart |
| Verbesserungsvorschläge | Schreibhilfe ▸ Prüfen |
| Vergleichen | Überprüfen ▸ Vergleichen |
| Vergrößern | Ansicht ▸ Zoom |
| Verkleinern | Ansicht ▸ Zoom |
| Verknüpfung erstellen | Texttools ▸ Verknüpfung |
| Verteilt | Start ▸ Absatz · Texttools ▸ Absatz |
| Vertikales Lineal | Ansicht ▸ Anzeigen |
| Vollbild | Ansicht ▸ Dokumentansichten |
| Von links nach rechts | Start ▸ Absatz |
| Von rechts nach links | Start ▸ Absatz |
| Vorherige | Überprüfen ▸ Kommentare · Überprüfen ▸ Änderungen |
| Vorherige Endnote | Verweise ▸ Fußnoten |
| Vorherige Fußnote | Verweise ▸ Fußnoten |
| Vorheriger Abschnitt | Abschnitt ▸ Abschnitte |
| Vorheriger Datensatz | Mailings ▸ Vorschau |
| Vorige Kopfzeile | Kopf- und Fußzeile ▸ Navigation |
| Voriges Textobjekt | Texttools ▸ Verknüpfung |
| Vorlagen durchsuchen | Datei ▸ Neu |
| Vorlagen zurücksetzen | Ansicht ▸ Oberfläche |
| Vorlesen | Schreibhilfe ▸ Vorlesen |
| Vorwärts | SmartArt-Design ▸ Grafik erstellen |
| Wasserzeichen | Einfügen ▸ Kopf- und Fußzeile |
| Weblayout | Ansicht ▸ Dokumentansichten |
| Weiter | Überprüfen ▸ Kommentare · Überprüfen ▸ Änderungen |
| Weitere Ansichten | Ansicht ▸ Dokumentansichten |
| Weitere Anzeigen | Ansicht ▸ Anzeigen |
| Weitere Papierformate… | Abschnitt ▸ Seite |
| Welche Hilfe wann | Schreibhilfe ▸ Prüfen |
| Wellenlinien | Schreibhilfe ▸ Beim Schreiben |
| Wie das System | Ansicht ▸ Helligkeit |
| WordArt | Einfügen ▸ Text |
| Wort-Extras | Start ▸ Extras |
| Wörter zählen | Überprüfen ▸ Dokumentprüfung |
| Wortvorhersage | Schreibhilfe ▸ Beim Schreiben |
| Zahl | Einfügen ▸ Symbole |
| Zeichenschattierung | Start ▸ Schriftart |
| Zeile löschen | Tabellentools ▸ Layout: Zeilen und Spalten |
| Zeile oberhalb einfügen | Tabellentools ▸ Layout: Zeilen und Spalten |
| Zeile unterhalb einfügen | Tabellentools ▸ Layout: Zeilen und Spalten |
| Zeilenabstand | Start ▸ Absatz · Texttools ▸ Absatz |
| Zeilenfokus | Schreibhilfe ▸ Lesen |
| Zeilennummern | Seitenlayout ▸ Seite einrichten |
| Zeilenumbruch | Start ▸ Absatz |
| Zelle teilen | Tabellentools ▸ Zellen |
| Zellen verbinden | Tabellentools ▸ Zellen |
| Zellenschattierung | Tabellentools ▸ Entwurf: Rahmen und Farbe |
| Zentriert | Start ▸ Absatz · Texttools ▸ Absatz |
| Zitat einfügen | Verweise ▸ Zitate und Literatur |
| Zitierweise | Verweise ▸ Zitate und Literatur |
| Zoom | Ansicht ▸ Zoom |
| Zuletzt verwendete Dokumente | Datei ▸ Öffnen |
| Zur Note springen | Verweise ▸ Fußnoten |
| Zuschneiden | Bildtools ▸ Größe |
| Zuschneiden nach Maß … | Bildtools ▸ Weitere |
| Zwei Seiten | Ansicht ▸ Zoom |
| Zwischen Kopf- und Fußzeile wechseln | Kopf- und Fußzeile ▸ Navigation |

---

[← Zurück zum README](../README.md) · [Der Aufbau der Optionen](aufbau-optionen.md)
