# Lunivo Office – Übergabe für den KI-Neuaufbau

## Einordnung und Projektverzeichnis

Technisches Nachschlagewerk zum bisher untersuchten Stand, kein eigenständiger Arbeitsauftrag. Verbindliche Regeln, Projektpfade und Prioritäten stehen in `CLAUDE.md`. Bestandsangaben sind vor konkreter Übernahme gezielt am aktuellen Quellcode zu prüfen, ohne damit nicht genehmigte automatische Prüfungen auszulösen.

## Ziel und Geltungsbereich

Dieses Dokument hält technische Erkenntnisse aus dem bisherigen Quellcode fest. Verbindliches Ziel, Erhalt der GUI einschließlich Ausnahme für die Dokument-Zeichenfläche und Wiederverwendungsregeln stehen in `Lunivo_Office_Hauptprompt.md` §§ 1, 3 und 5.

## Architektur

Der Python-Quellcode befindet sich unter `src/lunivo_writer/`.

Der unabhängige Dokumentkern bleibt innerhalb von
`lunivo_writer.core`. Er soll nicht separat paketiert werden.

### Dokumentkern

`core/` enthält:
- `document`: Dokumentstruktur und Inhalte
- `geometry`: Geometrie und Maßeinheiten
- `textlayout`: Textsatz
- `editing`: Bearbeitungslogik
- `layout`: Seiten- und Dokumentlayout
- `rendering`: Darstellung

Diese Bereiche wurden von direkten Qt- und GUI-Abhängigkeiten
entkoppelt. Vorhandene öffentliche Zugriffe wurden bei
Umstrukturierungen soweit möglich erhalten.

### Datenmodelle

- `modelle/bericht.py`: IOReport, DocumentIOError, PasswortNoetig;
  nur Python-Standardbibliothek.
- `modelle/korrektur.py`: ProofingIssue und weitere Strukturen
  zur Textkorrektur; nur Python-Standardbibliothek.
- `modelle/seite.py`: HeaderFooter und PageSettings;
  abhängig von core.geometry und kern.farben.

### Dateiverarbeitung

- `dienste/formate.py`: Formatbeschreibungen; Standardbibliothek.
- `dienste/import_grenzen.py`: Sicherheitsgrenzen beim Import.
- `dienste/sicher_schreiben.py`: Sicheres Schreiben von Dateien;
  verwendet data_dir direkt aus plattform.pfade.
- `dienste/txt_modell.py`: TXT-Verarbeitung über das Dokumentmodell.
- `dienste/modell_laden.py`: Einheitliche Modellschnittstelle zum Laden.
- `dienste/modell_speichern.py`: Einheitliche Modellschnittstelle
  zum Speichern.

### DOCX

Es existieren zwei Exportwege:
- `dienste/docx_schreiber.py`: Umfangreicher Qt-basierter Export.
- `docx_modell_daten()`: Direkter Export einfacher Dokumentmodelle.

Der direkte Export unterstützt unter anderem einfache Absätze,
Zeichenformatierungen, Bilder und bestimmte Tabellen.

Bei nicht unterstützten Dokumenteigenschaften liefert er `None`.
Der bisherige Exportweg übernimmt dann die Verarbeitung.

Es existieren außerdem zwei Importwege:
- `dienste/docx_leser.py`: Qt-basierter Import.
- `dienste/docx_modell_leser.py`: Modellorientierter Import,
  der weiterhin Qt-Klassen und Editorfunktionen benötigt.

Diese vorhandenen Implementierungen nicht vorschnell ersetzen.

### Benutzeroberfläche und Befehle

- `oberflaeche/`: Bestehende Benutzeroberfläche.
- `editor/`: Editorbezogene Funktionen.
- `kern/befehle/`: Vorhandene Befehlsstruktur für Haupt- und
  Kontextreiter.
- `adapter/qt/`: Verbindung zwischen Qt und Dokumentmodell.

Die Befehlsmodule dienen als wichtige Funktionsreferenz für
den späteren Neuaufbau.

## Vorgehen beim Neuaufbau

Für Implementierungsreihenfolge, Übernahme geeigneter Fachlogik, Umstellung von Aufrufstellen und vollständigen Datenerhalt gelten Hauptprompt §§ 4–5 sowie die technische Übergabe `KI_NEUAUFBAU_AUFTRAG.md`. Die hier dokumentierten Module sind gezielt als Bestandsreferenz zu nutzen.

## Noch offen

- Indirekte Abhängigkeiten einzelner Dienstmodule überprüfen.
- `kern.farben` auf unabhängige Wiederverwendbarkeit prüfen.
- DOCX-Modellimport vollständig von Qt lösen.
- Weitere Dateiformate modellorientiert anbinden.
- Bestehende Befehle beim Neuaufbau systematisch zuordnen.

## Hinweis

Diese Übersicht dokumentiert den bisher untersuchten Stand.
Sie ist keine Bestätigung, dass sämtliche Funktionen bereits
unabhängig ausführbar sind.

## Bestätigte Wiederverwendbarkeit: Farben und Seitenmodell

- `kern/farben.py` enthält die zentrale Klasse `Farbe`.
- Das Modul verwendet keine externen Bibliotheken und keine
  anderen Projektmodule.
- Zahlreiche Module nutzen die bestehenden Farbnamen.
- Die Farbnamen beim Neuaufbau möglichst beibehalten.
- `modelle/seite.py` verwendet `core.geometry.units` und
  `kern.farben`. Beide direkten Abhängigkeiten sind Qt-frei.
- `modelle/bericht.py` und `modelle/korrektur.py` verwenden
  ausschließlich die Python-Standardbibliothek.

Diese Module sind wichtige Kandidaten für die direkte Übernahme.

## Dokumentverwaltung und Wiederherstellung

- `kern/dokument_verwaltung.py` enthält `DocumentManager`.
- Die Klasse verwaltet Laden, Speichern, zuletzt verwendete
  Dateien, automatische Sicherung und Wiederherstellung.
- Sie unterstützt bereits das direkte Speichern von
  `core.document.Document` über `modell_speichern`.
- `DocumentManager` weiterhin als Vorlage verwenden.
  Die Klasse ist noch an Einstellungen und teilweise
  an die bisherige Editoroberfläche gekoppelt.

- `dienste/wiederherstellung.py` verwaltet Sicherungsdateien,
  Wiederherstellungsmetadaten und zusätzliche Sicherungsstände.
- Der Dienst verwendet `data_dir` direkt aus `plattform.pfade`
  und benötigt selbst kein Qt.
- Die bestehenden Funktionen und Dateiformate beim Neuaufbau
  möglichst erhalten.

## Programmstart und Lebenszyklus

- `kern/anwendung.py` enthält den Qt-basierten Programmstart.
- `LunivoApplication` initialisiert QApplication, Protokollierung,
  Einstellungen, Übersetzungen, Design und Hauptfenster.
- Die Datei ist bewusst Qt-abhängig und soll beim Neuaufbau
  als funktionale Vorlage dienen.

Wichtige Startreihenfolge:

1. Dateien aus den Programmargumenten öffnen.
2. Ohne übergebene Dateien eine Wiederherstellung anbieten.
3. Falls aktiviert, das zuletzt verwendete Dokument öffnen.
4. Wenn noch kein Dokument geöffnet ist, ein leeres erstellen.

- `programm_symbol()` lädt die vorhandenen Symbolgrößen.
- `_abbauen()` behandelt die kontrollierte Freigabe von
  Qt-Objekten beim Beenden.
- Bei der Integration der neuen Dokument-Zeichenfläche die Startlogik erhalten,
  aber nur die für die neue Dokumentarchitektur notwendige interne Anbindung anpassen.


## Optionale Zusatzdienste

Dies ist eine **Zielvorgabe, keine Bestandsfeststellung**. Verbindlich sind Hauptprompt § 13.3 und `writing-block.md` (zentraler Moduleingang, getrennte Dienst- und Plattformverantwortung, keine Abhängigkeit des Dokumentenkerns). Vorhandene Dienstimplementierungen, Aufrufstellen und Pfadfunktionen bei konkretem Bedarf gezielt prüfen.

