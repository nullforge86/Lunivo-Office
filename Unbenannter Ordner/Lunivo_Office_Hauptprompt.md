# LUNIVO OFFICE – VERBINDLICHER HAUPTPROMPT FÜR DEN VOLLSTÄNDIGEN NEUAUFBAU DES DOKUMENTENKERNS

## 1\. AUFTRAG

Entwickle einen vollständig integrierten, einheitlichen Dokumentenkern für Lunivo Office. Verwende dafür geeignete Teile des separaten, bereits Qt-freien `document_core` als bevorzugte technische Grundlage und entwickle fehlende oder ungeeignete Teile neu.

Die bisherige Qt-gebundene Dokumentverarbeitung, überholte Kernimplementierungen, die bisherige Textsatz- und Layoutarchitektur, das Rendering und die bisherige Dokument-Zeichenfläche werden durch eine einheitliche Architektur ersetzt. Geeignete Implementierungen des separaten Qt-freien `document_core` dürfen und sollen darin weiterverwendet werden.

**Ausschließlich die vorhandene grafische Benutzeroberfläche und sämtliche vorhandenen Bedienelemente bleiben erhalten.**

PySide6 bleibt für die Benutzeroberfläche und die grafische Ausgabe erhalten.

### Verbindliches Endziel

- Ein einziges Qt-unabhängiges Python-Dokumentmodell, vorzugsweise auf Basis geeigneter Teile des separaten `document_core`.
- Eine zentrale Dokumentbearbeitung mit Rückgängig und Wiederholen, vorzugsweise unter Wiederverwendung geeigneter Teile des separaten `document_core`.
- Eine neue Textsatz- und Layout-Engine.
- Eine neue Dokument-Zeichenfläche.
- Ein neues Rendering-System.
- Eine einheitliche Verarbeitung von Text, Tabellen, Bildern, Formen und weiteren Dokumentobjekten.
- Eine neue Dokumentnavigation einschließlich Schreibmarke und Auswahl.
- Eine direkte Anbindung sämtlicher vorhandener Bedienelemente.
- Laden und Speichern über das neue Dokumentmodell.
- Drucken und PDF-Ausgabe über die neue Layout- und Rendering-Architektur.
- Vollständiger Erhalt sämtlicher vorhandener Dokumentfunktionen.
- Entfernung überholter oder paralleler Dokumentkern-Implementierungen nach der Übernahme ihrer benötigten Funktionen.

**Am Ende existiert genau ein Dokumentmodell, eine maßgebliche Bearbeitungsarchitektur, eine Layout-Engine und eine Dokument-Zeichenfläche.**

---

## 2\. PROJEKT UND ARBEITSMODUS

Projektwurzel:

`~/Videos/Lunivo-Office-aufgeraeumt/Lunivo-Office-aufgeraeumt/`

Verwende ausschließlich diese innere Projektwurzel, nicht den gleichnamigen übergeordneten Ordner mit eigener `.venv`.

### ARBEITSMODUS: DIREKT IMPLEMENTIEREN

- Arbeite direkt am tatsächlichen Programmcode.
- Entwickle den neuen Dokumentenkern vollständig.
- Verwende die vorhandene grafische Oberfläche weiter.
- Erhalte sämtliche bestehenden Bedienelemente.
- Neue Verzeichnisse sind nur nach meiner ausdrücklichen Zustimmung erlaubt.
- Nutze vorhandene Projektverzeichnisse für die neue Architektur, soweit fachlich sinnvoll.
- Keine zweite parallele Dokument-Engine als dauerhafte Lösung.
- Keine Qt-Dokumentspiegelungen.
- Keine Qt-Rückfallwege.
- Keine Platzhalter oder leeren Ersatzfunktionen.
- Keine blinden Massenersetzungen.
- Keine unnötigen kosmetischen Änderungen.
- Keine Git-Befehle, GitHub-Abfragen, Branches oder Commits.
- Keine MD-Dateien, Statusdateien oder Fortschrittsberichte.
- Keine wiederholten vollständigen Projektanalysen.
- Keine destruktiven Änderungen an nicht betroffenen Projektteilen.
- Keine eigenständigen automatischen Prüfungen.

**Die tatsächliche Entwicklung des neuen Dokumentenkerns hat Vorrang vor Berichten, Diagnosen und Dokumentation.**

---

## 3\. VERBINDLICHE REGEL ZUM ERHALT DER BENUTZEROBERFLÄCHE

Die vorhandene grafische Benutzeroberfläche bildet die unveränderliche Grundlage des Neuaufbaus.

### 3.1 Unbedingt erhalten

- Hauptfenster und Fensterverwaltung.
- Menüband und sämtliche Registerkarten.
- Symbolleisten und Minisymbolleisten.
- Dialogfenster.
- Kontextmenüs.
- Seitenleisten.
- Statusleiste.
- Dokument-Tabs.
- Vorhandene Schaltflächen und Eingabefelder.
- Tastenkürzel.
- Grafische Gestaltung und vorhandene Bedienelemente.
- Vorhandene Benutzerabläufe.

Die Benutzeroberfläche darf nicht eigenständig neu gestaltet, vereinfacht oder durch eine andere Oberfläche ersetzt werden.

### 3.2 Erlaubte Änderungen

Die interne Anbindung der Bedienelemente darf und muss geändert werden, damit sämtliche Dokumentoperationen über den neuen Kern laufen.

Dazu gehören notwendige Änderungen an Signalverbindungen, Befehlsaufrufen, Zustandsabfragen und Dokumentzugriffen.

### 3.3 Dokument-Zeichenfläche ist ausdrücklich ausgenommen

Die bisherige Dokument-Zeichenfläche gehört nicht zu den zu erhaltenden Oberflächenkomponenten.

Sie wird vollständig durch eine neue, eigens entwickelte Dokument-Zeichenfläche ersetzt.

Das umgebende Dokumentfenster, seine Bedienelemente und seine Integration in die Benutzeroberfläche bleiben erhalten.

---

## 4\. OBERSTE ARBEITSREGEL – ZUERST IMPLEMENTIEREN

Solange der neue Dokumentenkern nicht vollständig implementiert ist, wird zielgerichtet programmiert.

### 4.1 Prioritäten

1. Zielarchitektur aufbauen und geeignete Teile des separaten Qt-freien `document_core` gezielt integrieren.
2. Ein einheitliches Dokumentmodell fertigstellen, vorhandene geeignete Implementierungen wiederverwenden.
3. Zentrale Bearbeitungssitzung auf dieser Grundlage fertigstellen.
4. Neue Textsatz- und Layout-Engine implementieren.
5. Neue Dokument-Zeichenfläche entwickeln.
6. Schreibmarke, Auswahl und Eingaben integrieren.
7. Vorhandene Bedienelemente anbinden.
8. Sämtliche weiteren Dokumentfunktionen durch gezielte Wiederverwendung oder Neuentwicklung vollständig bereitstellen.
9. Dateiformate und Ausgabe integrieren.
10. Überholte Dokumentkern-Implementierungen entfernen.

### 4.2 Automatische Prüfungen sind verboten

Ohne meine ausdrückliche Aufforderung dürfen nicht durchgeführt werden:

- Automatische Tests und Testläufe.
- Syntaxprüfungen.
- Importprüfungen.
- Regressionstests.
- Wiederholte Programmstarts zur Fehlersuche.
- Automatische Validierungsdurchläufe.
- Wiederkehrende Diagnose- und Reparaturschleifen.
- Prüfungen nach jeder Datei oder Funktion.
- Prüfberichte und Testprotokolle.

Auch kurze automatische Prüfungen sind nicht eigenständig erlaubt.

#### Verbindliche Begrenzung ausdrücklich genehmigter Prüfungen

Wenn ich Tests, Syntaxprüfungen, Importprüfungen oder sonstige Validierungen ausdrücklich erlaube oder anordne, gilt diese Erlaubnis ausschließlich für die konkret betroffenen Änderungen und die zur Beurteilung zwingend erforderlichen unmittelbaren Abhängigkeiten.

1. **Keine Volltests:** Vollständige Projekt-, System- oder Regressionstests bleiben untersagt, sofern ich diese nicht ausdrücklich und gesondert anordne.
2. **Minimaler Prüfumfang:** Prüfe nur die geänderten Funktionen, Module und unmittelbar relevanten Schnittstellen, soweit dies zur Beurteilung der konkreten Änderungen erforderlich ist.
3. **Abhängigkeiten nur bei Bedarf:** Weitere Aufrufstellen, Imports oder abhängige Funktionen dürfen nur einbezogen werden, wenn sie von der Änderung tatsächlich betroffen sind und ihre Prüfung notwendig ist.
4. **Keine eigenständige Ausweitung:** Die Genehmigung einer Prüfung erlaubt keine zusätzlichen Tests anderer Projektbereiche, keine pauschalen Prüfungen und keine umfassenden Validierungsdurchläufe.
5. **Keine automatischen Testketten:** Wiederholte Testläufe, umfassende Regressionstests und eigenständige Diagnose- oder Reparaturschleifen sind nicht durch eine begrenzte Testfreigabe gedeckt.
6. **Keine dauerhafte Freigabe:** Jede Genehmigung gilt nur für den jeweiligen konkreten Auftrag und berechtigt nicht zu späteren Prüfungen ohne erneute Erlaubnis.
7. **Implementierung hat Vorrang:** Der Prüfaufwand ist auf das technisch notwendige Minimum zu begrenzen. Unnötige Prüfungen dürfen die Entwicklungsarbeit nicht verdrängen.

**Oberste Regel:** Auch bei ausdrücklich erlaubten oder angeordneten Tests gilt stets der kleinstmögliche technisch notwendige Prüfumfang. Eine allgemeine Testfreigabe ist niemals als Erlaubnis für Volltests auszulegen. Nur eine ausdrücklich und gesondert angeordnete vollständige Prüfung hebt diese Begrenzung für den bezeichneten Auftrag auf.

### 4.3 Arbeitsablauf

1. Ermittle die konkret benötigte Fähigkeit.
2. Lies ausschließlich den dafür erforderlichen bestehenden Code.
3. Implementiere die neue Fähigkeit vollständig.
4. Verbinde sie mit den notwendigen Aufrufstellen.
5. Setze die nächste Implementierung fort.

Offensichtliche Fehler im gerade bearbeiteten Code sind unmittelbar zu beheben.

Eine Implementierung darf ohne Prüfung nicht als getestet oder nachweislich fehlerfrei bezeichnet werden.

---

## 5\. GRUNDREGEL FÜR DEN VOLLSTÄNDIGEN NEUAUFBAU

### Verbindliche Sonderregel: separater Qt-freier `document_core`

Diese vom Projektinhaber ausdrücklich genehmigte Sonderregel hat **Vorrang vor jeder Formulierung dieses Hauptprompts, die eine grundsätzliche Neuentwicklung bereits geeigneter Qt-freier Funktionen verlangt**. Alle übrigen Anforderungen und Arbeitsverbote gelten unverändert.

**Referenzverzeichnis (außerhalb der inneren Projektwurzel):**

`/home/kaysiebke/Videos/Lunivo-Office-aufgeraeumt/document_core`

- Dieser separate Kern enthält 17 Python-Dateien. In der bisherigen statischen Übersicht wurden keine direkten PySide-/PyQt-Imports gefunden. Das ist **kein Nachweis**, dass alle Funktionen vollständig oder fehlerfrei sind.
- Vorhanden sind unter anderem `model.py`, `engine.py`, `kern.py`, Text-, Format-, Tabellen-, Objekt- und Abschnittsoperationen, Zusatzfunktionen sowie Serialisierung.
- Die `DokumentEngine` bündelt Bearbeitungsoperationen; `Kern` enthält Änderungsverlauf, Auswahl und Rückgängig/Wiederholen. Geeignete Implementierungen sind **bevorzugt zu übernehmen**, statt sie grundlos neu zu schreiben.
- **Nur konkret benötigte Teile gezielt lesen und auf Eignung beurteilen**; keine vollständige erneute Projektanalyse und keine automatischen Tests ohne ausdrücklichen Auftrag.
- `layout.py` enthält eine Qt-freie Seitenaufteilung mit externem Höhenmesser, aber **keine nachgewiesene vollständige Textsatz-, Layout- oder Rendering-Engine**. Fehlende Fähigkeiten wie Zeilenbildung, Aufteilung übergroßer Blöcke, Tabellen- und Objektlayout, Textumfluss, Rendering und die neue Dokument-Zeichenfläche müssen nach den Anforderungen dieses Hauptprompts umgesetzt werden.
- Der separate Kern bleibt **zunächst unverändert am bisherigen Ort**. Keine pauschale Kopie und keine dauerhafte Abhängigkeit vom außerhalb der Projektwurzel liegenden Verzeichnis. Geeignete Teile werden bei konkretem Bedarf in die bestehende Zielstruktur unter `src/lunivo_writer/` integriert.
- Es darf am Ende **nur ein maßgebliches Dokumentmodell, eine Bearbeitungsarchitektur und eine Layout-Engine** geben. Keine zweite parallele `DokumentEngine`, keine Qt-Dokumentspiegelung und kein dauerhafter Adapter als Ersatz für die Integration.
- Die vorhandene GUI und sämtliche Bedienelemente bleiben erhalten; die bisherige Dokument-Zeichenfläche wird ersetzt. Überholte Komponenten erst entfernen, wenn ihre Aufgaben und Aufrufstellen übernommen sind.
- Die Sonderregel **genehmigt keine neuen Verzeichnisse**, keine Git-Aktionen, keine MD-Berichte und keine eigenständigen Prüfungen.

**Der bisherige Qt-gebundene Dokumentenkern ist keine verpflichtende Grundlage. Der separate Qt-freie `document_core` ist dagegen die bevorzugte technische Grundlage für geeignete Dokumentmodell- und Bearbeitungsfunktionen.**

### Verbindliche Vorgaben

1. Keine bisherige Qt-gebundene Dokument-Engine als dauerhafte Grundlage übernehmen. Die geeignete `DokumentEngine` des separaten Qt-freien `document_core` darf bevorzugt integriert werden.
2. Keine unzureichende bisherige Layout-Engine unverändert als vollständige Lösung übernehmen. Die vorhandene Qt-freie Seitenaufteilung darf als Ausgangspunkt dienen, muss aber um eigenständigen Textsatz, Blockaufteilung und vollständiges Layout ergänzt oder ersetzt werden.
3. Keine alte Dokument-Zeichenfläche weiterverwenden.
4. Keine Qt-Dokumentklassen als Dokumentmodell verwenden.
5. Keine parallelen Dokumentdatenhaltungen schaffen.
6. Keine dauerhaften Spiegelungen zwischen altem und neuem Kern.
7. Keine vorhandenen Benutzerfunktionen ersatzlos entfernen.
8. Keine Funktionen absichtlich deaktivieren.
9. Keine leeren Platzhalter einsetzen.
10. Keine unnötigen Kompatibilitätsschichten aufbauen.

Die alte Implementierung wird schrittweise durch die neue Architektur ersetzt.

**Entferne alte Komponenten erst dann, wenn ihre benötigten Aufgaben im neuen Kern implementiert und ihre Aufrufstellen umgestellt wurden.**

Während des Neuaufbaus dürfen technisch notwendige unfertige Zwischenstände existieren. Sie dürfen nicht als vollständig oder funktionsfähig ausgegeben werden.

---

## 6\. VERBINDLICHE NEUE ZIELARCHITEKTUR

### SCHICHT 1 – NEUES PYTHON-DOKUMENTMODELL

Stelle ein einheitliches, Qt-unabhängiges Dokumentmodell bereit. Prüfe dafür zuerst die geeigneten Datenstrukturen des separaten Qt-freien `document_core` und übernimm sie nach Bedarf.

Es verwaltet:

- Dokumente und Dokumentabschnitte.
- Absätze und Textläufe.
- Zeichen- und Absatzformatierungen.
- Formatvorlagen.
- Listen und Nummerierungen.
- Tabellen und Tabellenzellen.
- Bilder, Formen und Textfelder.
- Objektanker und Textumfluss.
- Seitenparameter.
- Kopf- und Fußzeilen.
- Fußnoten und Endnoten.
- Kommentare und Änderungsverfolgung.
- Felder und Verweise.
- Weitere vorhandene Dokumentstrukturen.

Das Modell ist die einzige maßgebliche Quelle für sämtliche Dokumentinhalte.

Es darf keine Abhängigkeit von `QTextDocument`, `QTextCursor` oder anderen Qt-Dokumentklassen besitzen.

### SCHICHT 2 – NEUE DOKUMENTBEARBEITUNG

Stelle eine zentrale Bearbeitungsarchitektur bereit. Nutze dafür bevorzugt geeignete Teile der Qt-freien `DokumentEngine` und ihres Änderungsprotokolls.

Sie übernimmt:

- Texteingabe.
- Textlöschung.
- Einfügen und Ersetzen.
- Zeichen- und Absatzformatierung.
- Tabellenoperationen.
- Objektbearbeitung.
- Schreibmarke.
- Auswahl.
- Rückgängig und Wiederholen.
- Dokumentänderungsstatus.
- Bearbeitungstransaktionen.
- Dokumentbezogene Befehle.

Alle Änderungen am Dokumentmodell laufen über diese zentrale Bearbeitungsarchitektur.

Die Benutzeroberfläche darf das Dokumentmodell nicht über unabhängige Bearbeitungswege verändern.

### SCHICHT 3 – NEUE TEXTSATZ-ENGINE

Entwickle eine neue Textsatzarchitektur.

Sie übernimmt:

- Unicode-Textverarbeitung.
- Schrift- und Glyphenverarbeitung.
- Textmessung.
- Zeilenbildung.
- Wortumbrüche.
- Zeichenabstände.
- Tabstopps.
- Textausrichtung.
- Absatzabstände.
- Mehrsprachige Textdarstellung.
- Bidirektionalen Text.
- Textpositionen für Schreibmarke und Auswahl.

Vorhandene geeignete Bibliotheken dürfen für grundlegende Schrift- und Textsatzfunktionen verwendet werden.

Die eigentliche Dokumentstruktur und Dokumentlayoutlogik müssen jedoch unabhängig von Qt-Dokumentklassen bleiben.

### SCHICHT 4 – NEUE LAYOUT-ENGINE

Entwickle eine vollständig neue Layout-Engine.

Sie berechnet:

- Absatzlayout.
- Zeilenpositionen.
- Seitenaufteilung.
- Seitenumbrüche.
- Abschnittsumbrüche.
- Tabellenlayout.
- Objektpositionierung.
- Textumfluss.
- Kopf- und Fußzeilen.
- Fußnoten.
- Seitenränder.
- Spaltenlayout.
- Schreibmarkengeometrie.
- Auswahlgeometrie.
- Dokumentnavigation.

Das Layout wird aus dem Dokumentmodell berechnet.

Es darf keine zweite maßgebliche Dokumentdatenhaltung entstehen.

### SCHICHT 5 – NEUES RENDERING

Entwickle ein neues Rendering-System auf Grundlage der neuen Layout-Ergebnisse.

Es übernimmt:

- Textdarstellung.
- Absatzdarstellung.
- Tabellen.
- Bilder.
- Formen.
- Textfelder.
- Seitenhintergründe.
- Rahmen.
- Schreibmarke.
- Auswahlmarkierungen.
- Dokumentobjekte.

`QPainter` darf als grafisches Ausgabe-Backend verwendet werden.

Qt darf jedoch nicht die Dokumentstruktur, Textbearbeitung oder Seitenaufteilung bestimmen.

### SCHICHT 6 – NEUE DOKUMENT-ZEICHENFLÄCHE

Entwickle eine vollständig neue Dokument-Zeichenfläche.

Sie ersetzt die bisherige `ModellAnsicht` und den bisherigen Qt-Dokumenteditor.

Die neue Zeichenfläche übernimmt:

- Darstellung sämtlicher Dokumentseiten.
- Schreibmarkendarstellung.
- Textauswahl.
- Mausbedienung.
- Tastaturbedienung.
- Texteingabe.
- Navigation.
- Scrollen.
- Zoom.
- Dokumentobjektauswahl.
- Tabelleninteraktion.
- Seitenansichten.
- Aktualisierung nach Dokumentänderungen.

Sie verwendet ausschließlich das neue Dokumentmodell, die neue Bearbeitungsarchitektur und die neue Layout-Engine.

Es darf keine zweite Dokument-Zeichenfläche entstehen.

### SCHICHT 7 – BESTEHENDE PYSIDE6-BENUTZEROBERFLÄCHE

Die vorhandene Benutzeroberfläche bleibt bestehen.

Sämtliche Dokumentbefehle werden über eindeutige Schnittstellen mit dem neuen Kern verbunden.

Die grafische Oberfläche enthält keine eigene Dokumentbearbeitungslogik und keine parallele Dokumentdatenhaltung.

---

## 7\. PHASE 1 – NEUES TECHNISCHES FUNDAMENT

Diese Phase hat absolute Priorität.

### 7.1 Neue Dokumentzuständigkeit

Der Dokument-Tab besitzt das neue Dokumentmodell und die zugehörige Bearbeitungssitzung.

Ein neues Dokument beginnt mit einem leeren Modell.

Jedes geöffnete Dokument besitzt einen eigenständigen Dokumentzustand.

### 7.2 Neue Dokument-Zeichenfläche

Entwickle die neue Zeichenfläche und integriere sie in den bestehenden Dokument-Tab.

Die bisherigen umgebenden Bedienelemente bleiben erhalten.

### 7.3 Grundlegende Dokumentbearbeitung

Implementiere:

- Texteingabe und Textlöschung.
- Absätze und Zeilenumbrüche.
- Schreibmarke und Auswahl.
- Tastatur- und Mausnavigation.
- Zwischenablage.
- Rückgängig und Wiederholen.
- Dokumentwechsel.
- Änderungsstatus.
- Grundlegende Textformatierung.
- Laden und Speichern.

### 7.4 Grundlegendes Layout

Implementiere:

- Textmessung.
- Zeilenbildung.
- Absatzlayout.
- Seitenaufteilung.
- Darstellung mehrseitiger Dokumente.
- Schreibmarkenpositionierung.
- Auswahlgeometrie.

### 7.5 Zusammenhängende Umsetzung

Die neue Dokumentzuständigkeit, Bearbeitung, Layoutberechnung und Zeichenfläche müssen als zusammenhängende Architektur entwickelt werden.

Keine Phase als abgeschlossen melden, wenn dafür erforderliche Komponenten nur durch Platzhalter ersetzt wurden.

Keine automatischen Prüfungen zum Phasenabschluss durchführen.

---

## 8\. PHASE 2 – VOLLSTÄNDIGE DOKUMENTFUNKTIONEN

Jeder Funktionsbereich umfasst:

- Datenstrukturen im neuen Modell.
- Bearbeitungsoperationen.
- Layoutunterstützung.
- Rendering.
- Anbindung der vorhandenen Bedienelemente.

### Arbeitspaket 1 – Zeichenformatierung

Implementiere sämtliche vorhandenen Zeichenformatfunktionen:

- Fett und Kursiv.
- Unterstreichen und Durchstreichen.
- Hoch- und Tiefstellen.
- Schriftart und Schriftgröße.
- Schriftfarbe und Hervorhebung.
- Kapitälchen.
- Zeichenabstände.
- Texteffekte.
- Formatierung löschen.
- Format übertragen.
- Schreibformat an der Schreibmarke.
- Effektive Formatabfrage bei gemischten Auswahlen.

Binde sämtliche vorhandenen Menübandbefehle, Dialoge, Kontextmenüs und Tastenkürzel an.

### Arbeitspaket 2 – Absätze, Listen und Formatvorlagen

Implementiere:

- Absatzausrichtung.
- Einzüge.
- Absatzabstände.
- Zeilenabstände.
- Tabstopps.
- Aufzählungen.
- Nummerierungen.
- Mehrstufige Listen.
- Formatvorlagen.
- Formatvorlagenvererbung.
- Absatzoptionen.

### Arbeitspaket 3 – Tabellen

Implementiere:

- Tabellen einfügen und bearbeiten.
- Zeilen und Spalten.
- Zellen verbinden und teilen.
- Zellformatierungen.
- Tabellenformatvorlagen.
- Rahmen.
- Zellgrößen.
- Zellenauswahl.
- Tabellennavigation.
- Sortieren.
- Text in Tabelle.
- Tabelle in Text.

### Arbeitspaket 4 – Bilder und Objekte

Implementiere:

- Bilder.
- Formen.
- Textfelder.
- Diagramme.
- SmartArt-Funktionen.
- Sonderzeichen.
- Objektanker.
- Objektpositionierung.
- Textumfluss.
- Objektformatierung.
- Objektbearbeitung.
- Zwischenablage für Dokumentobjekte.

### Arbeitspaket 5 – Seiten und Abschnitte

Implementiere:

- Seitenformate.
- Seitenränder.
- Dokumentabschnitte.
- Seitenumbrüche.
- Abschnittsumbrüche.
- Kopf- und Fußzeilen.
- Fußnoten und Endnoten.
- Seitenzahlen.
- Deckblätter.
- Wasserzeichen.
- Seitenrahmen.
- Zeilennummerierung.

### Arbeitspaket 6 – Verweise und Felder

Implementiere:

- Inhaltsverzeichnisse.
- Abbildungsverzeichnisse.
- Tabellenverzeichnisse.
- Textmarken.
- Querverweise.
- Dokumentfelder.
- Indexeinträge.
- Literaturverzeichnisse.
- Formularfelder.

### Arbeitspaket 7 – Textwerkzeuge und Überprüfung

Implementiere:

- Suchen und Ersetzen.
- Rechtschreib- und Korrekturfunktionen.
- Textstatistiken.
- Kommentare.
- Änderungsverfolgung.
- Dokumentvergleich.
- Dokumentfassungen.
- Vorhandene KI-Funktionen.
- Serienbrieffunktionen.

### Arbeitspaket 8 – Weitere Bedienelemente und Ansichten

Binde alle übrigen dokumentbezogenen Funktionen an.

Dazu gehören:

- Hauptfenster.
- Menüband.
- Dialoge.
- Kontextmenüs.
- Seitenleisten.
- Statusleiste.
- Tastenkürzel.
- Weblayout.
- Drucklayout.
- Zwei-Seiten-Ansicht.
- Seitenvorschau.
- Zoom und Navigation.

Nach jedem Arbeitspaket mit der nächsten notwendigen Implementierung fortfahren.

Keine eigenständigen Prüfserien beginnen.

---

## 9\. PHASE 3 – DATEIFORMATE UND AUSGABE

Die neue Architektur muss sämtliche bisher unterstützten Dokumentformate und Ausgabewege übernehmen.

### Dateiformate

- DOCX.
- ODT.
- RTF.
- PDF-Ausgabe.
- Weitere bisher unterstützte Formate.

Vorhandene Leser und Schreiber dürfen als Referenz für unterstützte Funktionen und Dateiformate dienen.

Ihre Dokumentverarbeitung wird an das neue Modell angepasst oder neu implementiert, soweit erforderlich.

### Ausgabe

Implementiere:

- Dokumentladen.
- Dokument speichern.
- Speichern unter.
- Wiederherstellung.
- Druckausgabe.
- Druckvorschau.
- PDF-Export.
- Seitenbilder.

Druck, Vorschau und PDF-Ausgabe müssen dieselbe maßgebliche Layoutberechnung verwenden wie die Dokument-Zeichenfläche.

Bestehende Dateiformatfunktionen dürfen nicht absichtlich entfallen.

---

## 10\. PHASE 4 – LEISTUNG UND DOKUMENTVERARBEITUNG

Die neue Architektur muss auch für größere Dokumente geeignet sein.

Berücksichtige bereits bei der Implementierung:

- Inkrementelle Layoutberechnung.
- Wiederverwendung unveränderter Layout-Ergebnisse.
- Gezielte Neuberechnung nach Änderungen.
- Effiziente Textbearbeitung.
- Effiziente Dokumentnavigation.
- Speicherbewusste Dokumentstrukturen.
- Seitenweises Rendering.
- Sichtbarkeitsabhängige Darstellung.
- Flüssiges Scrollen und Zoomen.
- Einheitliche Darstellung in Editor, Vorschau, Druck und PDF.

Keine zweite Layout-Engine für einzelne Ausgabewege entwickeln.

Keine eigenständigen Leistungsprüfungen ohne meine ausdrückliche Aufforderung durchführen.

---

## 11\. PHASE 5 – ALTEN DOKUMENTENKERN VOLLSTÄNDIG ENTFERNEN

Sobald die benötigten Aufgaben durch die neue Architektur übernommen wurden, entferne die bisherigen Implementierungen.

### Betroffene bisherige Komponenten

Insbesondere:

- `src/lunivo_writer/core/document/`
- `src/lunivo_writer/core/editing/`
- `src/lunivo_writer/core/layout/`
- `src/lunivo_writer/core/textlayout/`
- `src/lunivo_writer/core/rendering/`
- `src/lunivo_writer/oberflaeche/dokument/ansicht/modell_ansicht.py`
- `src/lunivo_writer/adapter/qt/bearbeitung.py`
- `src/lunivo_writer/adapter/qt/dokument.py`
- `src/lunivo_writer/editor/layout/seitenlauf.py`

Die genannten Verzeichnisse dürfen für die neue Implementierung weiterverwendet werden.

Es geht um den vollständigen Austausch ihrer bisherigen Dokumentkern-Logik, nicht um das zwingende Löschen ihrer Verzeichnisnamen.

### Verbotene dauerhafte Dokumentabhängigkeiten

Folgende Qt-Klassen dürfen nicht mehr für Dokumentmodell, Bearbeitung oder Layout verwendet werden:

- `QTextDocument`
- `QTextCursor`
- `QTextEdit`
- `QTextTable`
- `QTextTableCell`
- `QTextCharFormat`
- `QTextBlockFormat`
- `QTextFrame`
- `QAbstractTextDocumentLayout`

Die alte `ModellAnsicht`, der `ModellSpiegel`, die bisherige Qt-Dokumentverarbeitung und überholte Umschalter wie `LUNIVO_KERN_ANSICHT` werden entfernt, sobald sie nicht mehr benötigt werden.

**Keine alten Implementierungen vorzeitig löschen, solange dadurch benötigte Funktionen oder die erhaltene Benutzeroberfläche beschädigt würden.**

---

## 12\. LANGFRISTIG STABILE IMPORTPFADE

Die neue Architektur muss von Anfang an übersichtliche und langfristig stabile Importpfade erhalten.

### 12.1 Öffentliche Paketschnittstellen

Nutze vorhandene `__init__.py`-Dateien, um ausgewählte stabile Klassen und Funktionen bereitzustellen.

Andere Pakete sollen möglichst über diese öffentlichen Schnittstellen importieren.

Beispiel:

Statt:

``` python
from lunivo_writer.core.editing.sitzung import Sitzung
```

Nach Möglichkeit:

``` python
from lunivo_writer.core.editing import Sitzung
```

### 12.2 Kleine Schnittstellen

Exportiere nur tatsächlich benötigte öffentliche APIs.

Keine pauschalen Sammelimporte oder unnötigen Abstraktionsschichten.

### 12.3 Zirkuläre Importe vermeiden

Ordne Abhängigkeiten fachlich eindeutig zu.

Keine provisorischen Laufzeit-Hacks oder dynamischen Importumgehungen.

### 12.4 Bestehende Aufrufstellen berücksichtigen

Ermittle bei konkreten Umstrukturierungen die unmittelbar betroffenen Importpfade und Funktionsaufrufe.

Passe sie gezielt an die neue Architektur an.

Vorübergehende reine Python-Importweiterleitungen sind nur zulässig, wenn sie für die kontrollierte Umstellung erforderlich sind.

Sie dürfen keine alte Dokumentverarbeitung oder Qt-Rückfallwege erhalten.

### 12.5 Keine unnötige Importbereinigung

Keine eigenständige projektweite Import-Reorganisation durchführen.

Vereinfache Importpfade im Rahmen der tatsächlich notwendigen Implementierungen.

Keine automatischen Importprüfungen ohne meine ausdrückliche Anweisung.

---

## 13\. UMGANG MIT TECHNISCHEN ABHÄNGIGKEITEN

Wenn eine Funktion nicht unmittelbar neu implementiert werden kann:

1. Ermittle die konkrete technische Abhängigkeit anhand der unmittelbar betroffenen Dateien.
2. Implementiere die fehlende Grundlage in der neuen Architektur.
3. Berücksichtige zwingend zusammenhängende Funktionen.
4. Passe die betroffenen Aufrufstellen an.
5. Setze die nächste notwendige Implementierung fort.

Wenn eine wesentliche Entscheidung außerhalb des vereinbarten Umfangs oder ein neues Verzeichnis erforderlich wird, frage mich vorher.

Keine provisorischen Qt-Rückfallwege, Funktionsdeaktivierungen oder Platzhalter einsetzen.

Eine technische Abhängigkeit ist vorrangig eine Implementierungsaufgabe und kein Anlass für umfangreiche Prüfserien.

---

### 13.1 Verbindliche Regel zur plattformübergreifenden Architektur

Lunivo Office wird vorrangig für **Linux** entwickelt. Linux ist die primäre Entwicklungs-, Integrations- und Zielplattform. Die Architektur muss jedoch von Anfang an eine spätere vollständige Unterstützung von **Windows und macOS** ermöglichen, ohne dass der Dokumentenkern oder andere zentrale Komponenten grundlegend neu entwickelt werden müssen.

1. **Linux hat Vorrang:** Die aktuelle Implementierung und Integration erfolgen primär unter Linux. Windows- und macOS-spezifische Funktionen müssen nicht vorzeitig vollständig umgesetzt werden.
2. **Eine gemeinsame Codebasis:** Dokumentmodell, Bearbeitung, Textsatz, Layout, Rendering und Dokumentverarbeitung werden nicht für jedes Betriebssystem separat implementiert. Parallele Dokumentkerne oder Layout-Engines sind verboten.
3. **Klare Trennung:** Plattformabhängige Funktionen sind von der allgemeinen Fachlogik zu trennen und auf die technisch notwendigen Stellen zu begrenzen. Plattformübergreifende Möglichkeiten von Python und PySide6 sind bevorzugt zu nutzen.
4. **Dateisystem und Systemintegration:** Betriebssystemunterschiede bei Pfaden, Benutzer- und Konfigurationsverzeichnissen, Zugriffsrechten, Groß-/Kleinschreibung von Dateinamen, Dateidialogen, Dateizuordnungen und Systemdiensten sind zu berücksichtigen. Fest codierte Linux-Pfade und unnötige Linux-spezifische Abhängigkeiten im allgemeinen Programmcode sind zu vermeiden. Die ausdrücklich festgelegten Linux-Projekt- und Arbeitsverzeichnisse für die aktuelle Entwicklung bleiben davon unberührt.
5. **Schriften und Textsatz:** Schriftverfügbarkeit, Schriftmetriken, Textrendering, Umbruchverhalten und Skalierungsfaktoren können je nach Betriebssystem variieren. Die Architektur muss diese Unterschiede berücksichtigen, ohne getrennte Textsatz- oder Layout-Engines zu schaffen. Eine pixelidentische Ausgabe auf allen Plattformen darf nicht ungeprüft vorausgesetzt werden.
6. **Bedienung und Ausgabe:** Betriebssystemspezifische Tastenkombinationen, Zwischenablage, Drag-and-drop, Fensterintegration, Bildschirmauflösungen, Drucken und PDF-Ausgabe sind bei den betreffenden Implementierungen zu berücksichtigen.
7. **Benutzeroberfläche erhalten:** Die bestehende PySide6-Oberfläche und sämtliche vorhandenen Bedienelemente bleiben nach den übrigen Hauptprompt-Regeln erhalten. Erforderliche Plattformanpassungen dürfen nicht zu unabhängigen Oberflächenarchitekturen führen.
8. **Keine zusätzlichen Prüfungen:** Diese Vorgabe ist keine Genehmigung für Windows- oder macOS-Testläufe, vollständige Projektprüfungen oder sonstige automatische Validierungen. Es gelten unverändert die Prüfverbote und die Begrenzung ausdrücklich genehmigter Prüfungen aus Abschnitt 4.2.
9. **Keine unnötige Verzögerung:** Plattformübergreifende Architekturentscheidungen sind bei der jeweils anstehenden Implementierung zu berücksichtigen. Sie rechtfertigen weder eine umfassende zusätzliche Projektanalyse noch eine vorgezogene Entwicklung nicht benötigter Plattformfunktionen.

**Oberste Regel:** Linux zuerst entwickeln, aber die gemeinsame Architektur von Anfang an für Linux, Windows und macOS auslegen. Plattformunterschiede gezielt kapseln; keine parallelen Systeme schaffen und die Linux-Entwicklung nicht unnötig verzögern.

---

### 13.2 Verbindliche Regel für Zusatzpakete, Sprachdienste und externe Erweiterungen

Diese Regel ergänzt Abschnitt 13.1. **Linux bleibt die primäre Entwicklungsplattform**, aber optionale Zusatzfunktionen müssen so eingebunden werden, dass Windows und macOS später ohne grundlegenden Umbau der gemeinsamen Funktionslogik unterstützt werden können. Die bestehenden Vorgaben zu Arbeitsverzeichnissen, Erhalt der Oberfläche, Wiederverwendung und Prüfverboten bleiben unverändert.

1. **Einheitliche Schnittstellen:** Sprachausgabe und Vorlesen, Offline-Übersetzung, Rechtschreib- und Grammatikdienste, KI-Anbindungen, Wörterbücher, zusätzliche Schriften und andere externe Werkzeuge sind über klar abgegrenzte Schnittstellen anzubinden. Die allgemeine Funktionslogik darf nicht unmittelbar von einem bestimmten Betriebssystem, Shellskript oder ausführbaren Zusatzprogramm abhängen.
2. **Vorhandene Lösungen bevorzugen:** Bereits geeignete Funktionen, Dienste und Pfadverwaltungen sind gezielt zu prüfen und weiterzuverwenden. Insbesondere vorhandene Ansätze für Piper und Systemsprachausgabe, Argos Translate, LanguageTool, Ollama, Schriftdateien und `QStandardPaths` dürfen nicht grundlos durch parallele Implementierungen ersetzt werden. Die tatsächliche Eignung ist jeweils anhand des konkret benötigten Codes zu beurteilen.
3. **Plattformabhängige Ausführung kapseln:** Linux-spezifische Befehle wie `spd-say`, `paplay`, `aplay`, Shellskripte und Linux-Binärdateien dürfen nicht als allgemeine Voraussetzung für Windows und macOS gelten. Unterschiede bei ausführbaren Dateien, Prozessstart und -beendigung, Audioausgabe, Bibliotheken und Installationsverfahren sind in den jeweils notwendigen Plattformanbindungen zu behandeln. Eine gemeinsame Funktionsschnittstelle bleibt maßgeblich.
4. **Optionale Python-Pakete:** Nicht für die Grundfunktionen benötigte Bibliotheken bleiben optional. Bei nativen Abhängigkeiten sind Betriebssystem, Prozessorarchitektur, Python-Version und verfügbare kompatible Pakete zu berücksichtigen. Ein fehlendes oder nicht unterstütztes Zusatzpaket darf den Start und die grundlegende Dokumentbearbeitung nicht verhindern.
5. **Modelle und Zusatzdaten:** Sprachstimmen, Übersetzungsmodelle, Wörterbücher, Schriften und KI-Modelle sind getrennt vom Dokumentenkern zu verwalten. Für Downloads sind Herkunft, Speicherbedarf und Zielort soweit verfügbar verständlich anzugeben. Downloads und Installationen dürfen nur nach ausdrücklicher Benutzeraktion erfolgen; bereits mitgelieferte oder installierte Ressourcen dürfen ohne unnötiges erneutes Herunterladen verwendet werden.
6. **Betriebssystemgerechte Speicherorte:** Für neue benutzerbezogene Daten sind geeignete plattformabhängige Standardverzeichnisse zu verwenden, vorzugsweise über die vorhandene zentrale Pfadverwaltung. Bestehende Linux-Speicherorte und Benutzerdaten bleiben erhalten; notwendige ältere Suchorte können aus Kompatibilitätsgründen weiter berücksichtigt werden. Keine pauschalen Verschiebungen oder Löschungen.
7. **Fehlerbehandlung und Bedienung:** Nicht installierte, nicht verfügbare oder nicht unterstützte Erweiterungen müssen verständlich gemeldet werden. Die bestehende PySide6-Oberfläche und ihre Bedienelemente bleiben erhalten. Fehlende Zusatzdienste dürfen nicht zum Ausfall der Textverarbeitung, des Dokumentmodells oder der Dateioperationen führen.
8. **Sicherheit und Datenschutz:** Externe Programme und heruntergeladene Dateien sind nur aus nachvollziehbaren Quellen einzubinden; vorhandene Lizenz- und Sicherheitsvorgaben bleiben maßgeblich. Eine lokale Zusatzfunktion darf Dokumentinhalte nicht ohne ausdrückliche Benutzerentscheidung an Online-Dienste übertragen.
9. **Entwicklungspriorität:** Die plattformübergreifende Vorbereitung erfolgt nur im Rahmen der jeweils konkret anstehenden Implementierung. Windows- und macOS-spezifische Installationsprogramme, Backends und Paketierungen müssen nicht vorzeitig vollständig entwickelt werden. Keine unnötige Neuentwicklung der bestehenden Linux-Funktionen und keine zweite Erweiterungsarchitektur.
10. **Prüfungen bleiben beschränkt:** Diese Regel erlaubt weder eigenständige Tests noch plattformübergreifende Testreihen, Syntax- oder Importprüfungen. Es gelten unverändert Abschnitt 4.2 und der dort festgelegte kleinstmögliche Prüfumfang bei ausdrücklicher Freigabe.

**Oberste Regel:** Eine gemeinsame Lunivo-Office-Codebasis mit klar getrennten, optionalen Plattformanbindungen und Zusatzdiensten. Linux zuerst; Windows und macOS architektonisch mitdenken. Keine erzwungenen Zusatzinstallationen, keine parallelen Dokumentkerne und keine dauerhaften Linux-spezifischen Abhängigkeiten in der gemeinsamen Funktionslogik.

---

### 13.3 Verbindliche Modulbauweise mit zentralem Eingang für optionale Zusatzdienste

Die Regeln 13.1 und 13.2 werden durch **einen zentralen, gemeinsamen Moduleingang** konkretisiert. Diese Regel betrifft optionale Zusatzdienste und ihre Ressourcen, **nicht** das interne Python-Modulsystem als Ganzes und **nicht** den Dokumentenkern.

1. **Ein zentraler Eingang:** Die bestehende Oberfläche und fachliche Aufrufstellen verwenden für optionale Zusatzdienste eine kleine, stabile, einheitliche Dienstschnittstelle beziehungsweise eine zentrale Modulverwaltung. Sie sollen nicht jeweils eigene Paket-, Pfad-, Installations- und Betriebssystemlogik duplizieren. Die konkrete API ergibt sich aus den vorhandenen, gezielt untersuchten Aufrufstellen; keine erfundenen Pflichtklassennamen.
2. **Getrennte Verantwortlichkeiten:** Modulverwaltung (Registrierung, Auswahl, Verfügbarkeit, Zustände), bestehende Pfadverwaltung (Speicherorte und ältere Suchpfade), konkrete Dienstmodule (Vorlesen, Übersetzen, Grammatik, KI, Schriften, Wörterbücher) und Plattformanbindungen (Prozesse, Audio, Betriebssystemunterschiede) sind fachlich zu trennen. Der Eingang darf keine übergroße Sammeldatei werden.
3. **Kein zweiter Kern:** Zusatzdienste dürfen Dokumentinhalte nur über die dafür vorgesehenen öffentlichen Dokument- und Bearbeitungsschnittstellen lesen beziehungsweise ändern. Keine eigene Dokumentdatenhaltung, keine zweite Bearbeitungs-Engine und keine Abhängigkeit des Qt-freien Dokumentkerns von optionalen Modulen, Qt, Paketinstallern oder Online-Diensten.
4. **Vorhandenes gezielt integrieren:** Bestehende Dienste, Modulaufrufe und die Pfadverwaltung, insbesondere `plattform/pfade.py`, sowie Vorlesen/Piper, Argos Translate, LanguageTool und Ollama sind als mögliche Grundlagen zu berücksichtigen. Ihre konkreten Namen und Speicherorte im tatsächlich bearbeiteten Projekt sind gezielt festzustellen. Keine vorschnelle Umbenennung, Massenverschiebung oder parallele neue Erweiterungsverwaltung.
5. **Optionale, unabhängige Module:** Jeder Zusatzdienst meldet nachvollziehbar, ob er verfügbar, nicht eingerichtet oder auf der aktuellen Plattform nicht unterstützt ist. Fehlende oder defekte Zusatzpakete dürfen weder den Programmstart noch die grundlegende Dokumentbearbeitung beeinträchtigen. Module sollen voneinander unabhängig bleiben, soweit keine echte fachliche Abhängigkeit besteht.
6. **Pfade und Ressourcen:** Der Moduleingang fragt Pfade über die vorhandene zentrale Pfadverwaltung ab, statt eigene feste Linux-Verzeichnisse zu definieren. Binärdateien, Stimmen, Sprachpakete, Modelle und Schriften sind getrennt vom Dokumentkern und nach Plattform beziehungsweise Benutzerprofil zu verwalten. Bestehende Daten und ältere Linux-Suchorte bleiben erhalten.
7. **Ausführung nach Plattform:** Ein gemeinsamer Dienstvertrag kann unter Linux, Windows und macOS unterschiedliche geeignete Backends nutzen. Linux-spezifische Skripte, `spd-say`, `paplay`, `aplay` und Linux-Binärdateien sind keine Voraussetzung für alle Plattformen. Windows- und macOS-Backends werden nicht ohne konkreten Auftrag vorzeitig vollständig umgesetzt.
8. **Downloads und Datenschutz:** Installation, Download, Aktualisierung oder Entfernung von Zusatzpaketen und Modellen erfolgen nur nach ausdrücklicher Benutzerentscheidung. Keine heimliche Übertragung von Dokumentinhalten an Online-Dienste. Bestehende Lizenz-, Sicherheits- und Datenschutzregeln bleiben gültig.
9. **Oberfläche und Priorität:** Bestehende Bedienelemente, Dialoge und Benutzerabläufe bleiben erhalten. Eine neue zentrale Erweiterungsoberfläche, ein Plugin-Marktplatz oder ein dynamisches Drittanbieter-Plugin-System sind **nicht** automatisch beauftragt. Die Fertigstellung des einen Dokumentenkerns behält Vorrang; die Modularchitektur wird nur im jeweils betroffenen Umfang umgesetzt.
10. **Arbeitsgrenzen:** Keine neuen Projektverzeichnisse ohne ausdrückliche Zustimmung, keine unnötigen neuen Dateien, keine Git-Aktionen, keine vollständigen Projektanalysen und keine eigenständigen Prüfungen. Bei ausdrücklich genehmigten Prüfungen gilt unverändert Abschnitt 4.2.

**Oberste Regel:** Ein gemeinsamer, schlanker Eingang für optionale Zusatzdienste; getrennte Pfad-, Dienst- und Plattformzuständigkeiten; keine parallele Architektur und keinerlei Abhängigkeit des Dokumentenkerns von optionalen Paketen.

---

## 14\. VERBINDLICHE ABSCHLUSSBEDINGUNGEN

Der Neuaufbau ist auf Implementierungsebene erst abgeschlossen, wenn:

1. Ein einziges vollständig integriertes, Qt-unabhängiges Python-Dokumentmodell existiert; geeignete Implementierungen des separaten `document_core` dürfen übernommen sein.
2. Dieses Modell die einzige maßgebliche Dokumentdatenquelle ist.
3. Eine einzige integrierte Bearbeitungsarchitektur sämtliche Dokumentänderungen verwaltet.
4. Rückgängig und Wiederholen über die neue Architektur funktionieren sollen und vollständig implementiert sind.
5. Die neue Textsatz-Engine die Textverarbeitung übernimmt.
6. Die neue Layout-Engine sämtliche Dokumentseiten berechnet.
7. Die neue Dokument-Zeichenfläche die bisherige vollständig ersetzt.
8. Die vorhandene grafische Benutzeroberfläche erhalten geblieben ist.
9. Sämtliche vorhandenen Bedienelemente mit dem neuen Kern verbunden sind.
10. Alle bisherigen Dokumentfunktionen in der neuen Architektur implementiert sind.
11. Laden und Speichern das neue Dokumentmodell verwenden.
12. Drucken und PDF-Ausgabe die neue Layoutarchitektur verwenden.
13. Keine alte Qt-Dokumentverarbeitung mehr benötigt wird.
14. Keine alte Dokument-Zeichenfläche mehr verwendet wird.
15. Keine parallele Dokumentdatenhaltung existiert.
16. Die überholte Kernimplementierung entfernt wurde.
17. Die öffentlichen Paketschnittstellen fachlich eindeutig und langfristig wartbar sind.
18. Keine vorhandene Benutzerfunktion absichtlich deaktiviert oder ersatzlos entfernt wurde.

Diese Bedingungen sind Implementierungsziele.

Sie sind keine Erlaubnis für automatische Tests, Prüfungen oder Validierungsdurchläufe.

Ob die Anwendung anschließend geprüft wird und welche Prüfungen stattfinden, entscheide ausschließlich ich.

---

## 15\. STARTANWEISUNG

Beginne mit dem frühesten noch nicht implementierten Arbeitsschritt des vollständigen Neuaufbaus.

Arbeite direkt am vorhandenen Programmcode.

Erhalte ausschließlich die vorhandene grafische Benutzeroberfläche und ihre Bedienelemente als verbindliche Grundlage.

Stelle den gesamten Dokumentenkern fertig, indem du geeignete Teile des separaten Qt-freien `document_core` wiederverwendest und fehlende Bestandteile einschließlich der neuen Dokument-Zeichenfläche entwickelst.

Verwende den bisherigen Qt-gebundenen Kern nur zur gezielten Ermittlung bestehender Funktionen, Abhängigkeiten und Bedienabläufe. Prüfe den separaten Qt-freien `document_core` dagegen vorrangig auf konkrete Wiederverwendung.

Baue keine dauerhaften Abhängigkeiten zur alten Dokumentverarbeitung auf.

Ersetze die alte Architektur schrittweise und vollständig durch die neue.

Arbeite selbstständig weiter, solange die Änderungen innerhalb des beschriebenen Umfangs und der bestehenden Verzeichnisvorgaben liegen.

Frage nur nach, wenn eine wesentliche technische Entscheidung oder ein neues Verzeichnis meine ausdrückliche Zustimmung erfordert.

**Keine Git-Aktionen. Keine GitHub-Abfragen. Keine MD-Dateien. Keine automatischen Tests. Keine Syntaxprüfungen. Keine Importprüfungen. Keine Prüfungsorgien. Keine unnötigen Berichte.**

### OBERSTE PRIORITÄT

**ZUERST DEN EINHEITLICHEN DOKUMENTENKERN DURCH GEZIELTE WIEDERVERWENDUNG GEEIGNETER QT-FREIER IMPLEMENTIERUNGEN UND NEUENTWICKLUNG FEHLENDER TEILE FERTIGSTELLEN.**

**DANN DIE NEUE DOKUMENT-ZEICHENFLÄCHE UND ALLE NOTWENDIGEN FUNKTIONEN ANBINDEN.**

**DANN SÄMTLICHE VORHANDENEN DOKUMENTFUNKTIONEN VOLLSTÄNDIG ÜBERNEHMEN.**

**DANN DIE ÜBERHOLTE DOKUMENTVERARBEITUNG ENTFERNEN.**

**DIE BESTEHENDE GRAFISCHE OBERFLÄCHE UND IHRE BEDIENELEMENTE BLEIBEN ERHALTEN.**

**PRÜFUNGEN AUSSCHLIESSLICH AUF MEINE AUSDRÜCKLICHE ANWEISUNG.**

Das endgültige Ziel ist ein vollständig integrierter, einheitlicher, langfristig wartbarer und von Qt-Dokumentklassen unabhängiger Python-Dokumentenkern für Lunivo Office, unter gezielter Wiederverwendung geeigneter Teile des separaten Qt-freien `document_core`, einschließlich einer neuen Dokument-Zeichenfläche, unter vollständigem Erhalt der bestehenden grafischen Benutzeroberfläche und sämtlicher vorhandener Dokumentfunktionen.
