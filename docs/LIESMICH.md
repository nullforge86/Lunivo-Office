# Lunivo Writer – ausführlicher Überblick

Lunivo Writer ist eine native Textverarbeitung für Linux. Die Anwendung ist mit Python 3 und PySide6/Qt Widgets gebaut. Dokumente werden lokal bearbeitet; die Speicherorte wählst du selbst.

Die Schreibhilfe prüft Text auf häufige Rechtschreib-, Grammatik- und Zeichensetzungsfehler. Funde erscheinen mit Erklärung und Vorschlag neben dem Dokument. Sie werden nicht automatisch übernommen.

## Schreiben und Prüfen

Der Reiter **Schreibhilfe** bündelt Prüfung, Wortvorhersage, AutoKorrektur, Vorlesen, Silbentrennung, Übersetzung und Thesaurus. Die rechte Seitenleiste lässt sich mit **F5** öffnen oder schließen. **F6** zeigt, welche Hilfe sich für den jeweiligen Arbeitsschritt eignet.

KI-Korrektur und Textvorschläge sind optional. Sie können mit einem lokalen Modell über Ollama oder mit einem eingerichteten Online-Anbieter verwendet werden. Bei Online-KI wird der gewählte Text an diesen Anbieter übertragen.

## Dokumente und Formate

Lunivo öffnet DOCX, DOTX, DOCM, ODT, FODT, RTF und TXT. Es speichert DOCX, ODT, RTF und TXT; PDF und PNG sind Exportformate. Alte DOC/DOT-Dateien, Tabellenkalkulationen und Präsentationen werden nicht unterstützt. Einzelheiten und Grenzen stehen unter [Speichern und Dateiformate](SPEICHERN.md).

Ein Dokument kann Tabellen, Bilder, Formen, Diagramme, Formeln, Formatvorlagen, Kopf- und Fußzeilen, Notizen, Verzeichnisse und Seriendruck enthalten. Beim Öffnen oder Speichern weist Lunivo auf Inhalte hin, die ein Format nicht vollständig übernehmen kann.

## Oberfläche und Einstellungen

Das Programm bietet acht Register sowie zusätzliche kontextabhängige Register für ausgewählte Dokumentobjekte. Die Oberfläche lässt sich als Registerband oder Symbolleisten anzeigen. Eine rechte Seitenleiste zeigt die Schreibhilfe und optionale KI-Funktionen.

Die sechs Optionsseiten heißen **Lesen**, **Anzeige**, **Schreiben**, **Speichern**, **Drucken und PDF** sowie **Name und KI**. Öffnen mit **F9**; Änderungen werden unmittelbar übernommen.

## Tastenkürzel

| Taste | Funktion |
|---|---|
| `Strg+N`, `Strg+O`, `Strg+S` | Neues Dokument, Öffnen, Speichern |
| `Strg+Umschalt+S` | Speichern unter |
| `Strg+P` | Drucken |
| `Strg+W`, `Strg+Tab` | Dokument schließen, zum nächsten Dokument wechseln |
| `Strg+Z`, `Strg+Y` | Rückgängig, Wiederholen |
| `Strg+F`, `Strg+H` | Suchen, Ersetzen |
| `F3` | Textbaustein einfügen |
| `F4` | Vorlesen |
| `F5` | Seitenleiste ein- oder ausblenden |
| `F6` | Hilfe zur Wahl der Schreibhilfe öffnen |
| `F7` | Dokument prüfen |
| `F8` | KI-Korrektur |
| `F9` | Optionen öffnen |

## Dokumentation

- [Installation](INSTALLATION.md)
- [Lesen und Schreiben](lesen-und-schreiben.md)
- [Prüfung, Vorhersage und KI](pruefung-und-ki.md)
- [Schreiben und Dokumente](schreiben-und-dokumente.md)
- [Einstellungen](einstellungen.md)
- [Oberfläche](oberflaeche.md)

---

[Zurück zur README](../README.md)
