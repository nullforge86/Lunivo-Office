# LUNIVO OFFICE – VERBINDLICHER EINSTIEG

## Anweisungsrangfolge

1. `Lunivo_Office_Hauptprompt.md` – verbindliches Ziel, Funktionsumfang, Arbeitsregeln und Abschlussbedingungen.
2. `writing-block.md` – ergänzende Zielarchitektur, Paketverantwortlichkeiten und Abhängigkeitsrichtung.
3. `KI_NEUAUFBAU_AUFTRAG.md` – technische Übergabe und konkrete Durchführung; darf die Hauptprompts nicht ändern.
4. `KI_NEUAUFBAU_sauber(2).md` – bisherige technische Erkenntnisse; Nachschlagewerk, kein zusätzlicher Arbeitsauftrag.
5. `KI_PROJEKTUEBERSICHT.md` – statisch erfasste Module, Klassen, Funktionen und Imports; Nachschlagewerk, kein zusätzlicher Arbeitsauftrag.

Bei Widersprüchen gelten die Hauptprompts in obiger Reihenfolge. Die im ersten Hauptprompt ausdrücklich genehmigte Sonderregel zur Wiederverwendung des separaten Qt-freien `document_core` hat Vorrang vor allgemeinen Forderungen nach vollständiger Neuentwicklung bereits geeigneter Funktionen. Sonstige Vorgaben bleiben verbindlich.

## Arbeitsbereich und verbindliche Grenzen

- **Ziel für Codeänderungen:** `/home/kaysiebke/Videos/Lunivo-Office-aufgeraeumt/Lunivo-Office-aufgeraeumt/src/lunivo_writer/`.
- **Nur lesende Referenzen:** `/home/kaysiebke/Videos/Lunivo-Office-aufgeraeumt/document_core/` und `/home/kaysiebke/Videos/Lunivo-Office-aufgeraeumt/Qt-freie-Bausteine/`. Geeignete Funktionen gezielt prüfen und in den Zielcode integrieren; keine pauschalen Kopien oder dauerhaften externen Abhängigkeiten.
- **Erhalt:** Bestehende PySide6-Oberfläche, Bedienelemente und Bedienabläufe erhalten; die bisherige Dokument-Zeichenfläche ersetzen.
- **Verbote:** Keine Git-/GitHub-Aktionen, keine zusätzlichen Markdown-/Statusberichte, keine neuen Verzeichnisse ohne Zustimmung, keine eigenständigen automatischen Tests, Syntax-, Import- oder Validierungsprüfungen, keine leeren Platzhalter, keine `QTextDocument`-/`QTextCursor`-Abhängigkeit im neuen Kern. Für ausdrücklich genehmigte Prüfungen gilt ausschließlich der begrenzte Umfang aus Hauptprompt § 4.2.
- **Architektur:** Ein maßgeblicher Qt-freier Dokumentenkern. Optionale Zusatzdienste über einen schlanken zentralen Moduleingang gemäß Hauptprompt § 13.3 und `writing-block.md`; keine Zusatzpaket-Abhängigkeit im Dokumentenkern. Linux zuerst, Windows/macOS vorbereiten. Kein ungefragter Komplettumbau aller Zusatzdienste.

Für konkrete Implementierungsdetails die zuständigen Abschnitte lesen, nicht alle Nachschlagewerke vollständig erneut analysieren.

## Kontextsparender Arbeitsablauf

1. Zu Beginn `CLAUDE.md` und die für den Auftrag maßgeblichen Abschnitte der beiden Hauptprompts lesen. **Alle verbindlichen Vorgaben gelten weiterhin**, auch wenn nicht jeder Abschnitt erneut in den aktiven Kontext kopiert wird. Bei Unsicherheit die einschlägige Passage nachlesen, nicht raten.
2. Für die konkrete Aufgabe nur die passenden Kapitel aus `KI_NEUAUFBAU_AUFTRAG.md`, `KI_NEUAUFBAU_sauber(2).md` und `KI_PROJEKTUEBERSICHT.md` nachschlagen; die gesamte Projektübersicht nicht routinemäßig vollständig einlesen.
3. Vor Änderungen betroffene Funktionen, Aufrufstellen und gegebenenfalls die passenden Qt-freien Referenzmodule gezielt sichten. Bestandsangaben aus den Nachschlagewerken nicht als Nachweis des aktuellen Codezustands behandeln.
4. Änderungen ausschließlich innerhalb der genehmigten Arbeitsgrenzen durchführen. Eine Prüfung nur nach ausdrücklicher Freigabe und im Umfang von Hauptprompt § 4.2 ausführen. Ohne Prüfung niemals behaupten, die Implementierung sei getestet oder lauffähig nachgewiesen.
5. Bei fehlender Freigabe für notwendige neue Verzeichnisse oder Prüfungen gezielt um Erlaubnis bitten, statt die Grenze zu umgehen.

## Architektursperre: Qt-freier Dokumentenkern (verbindlich, ändert keine Rangfolge)

Vorrang vor kurzfristigen Fehlerkorrekturen, Testergebnissen und Ergebnissen des Compatibility Testers. Kein Komplettumbau; nur Sicherung der bestehenden Architektur.

- **Genau eine** Architektur: Dokumentmodell (`core/document`) → Bearbeitung (`core/editing`) → Textsatz (`core/textlayout`) → Layout (`core/layout`) → Rendering (`core/rendering`) → Qt-Oberfläche. Es gibt kein zweites Dokumentmodell, keinen zweiten Bearbeitungsweg, keine zweite Layout-Engine, keine zweite Zeichenfläche und keinen Qt-Rückfallweg.
- **Verboten** im Kern, in der Bearbeitung, im Textsatz, im Layout und in den Dokument-Adaptern (Import/Export): `QTextDocument`, `QTextCursor`, `QTextEdit`, `QPlainTextEdit`, `QTextBlock`, `QTextFrame`, `QTextTable`, `QTextLayout` als Textsatz-Ersatz, `QTextDocumentLayout`, Qt-basierte Dokumentmodelle oder -kopien und verdeckte Qt-Dokumentspiegelungen, auch nicht indirekt über Hilfsmodule.
- **Erlaubt** Qt/PySide6 nur in der Oberfläche: Fenster, Menüs, Dialoge, Leisten, Scrollbereiche, Maus/Tastatur, Darstellung fertig berechneter Seiten über die Rendering-Adapter (`adapter/qt`). Qt führt kein eigenes Dokumentmodell und entscheidet nicht über Aufbau von Absätzen, Tabellen oder Seiten.
- **Richtung:** GUI → Anwendungsschnittstellen → Dokumentkern. Verboten: Kern → GUI, Kern → Qt-Dokumenteditor, Layout → Qt-Dokumentlayout, Import/Export → zweite Dokument-Engine.
- **Kompatibilitätsfehler** (auch aus dem Compatibility Tester) werden in der zuständigen bestehenden Komponente behoben (Normalisierung, Formatvorlage, Schriftmetrik, Tabellenbreite, Seitenumbruchregel, Objektposition). Nie mit `QTextDocument`, altem Import-Rückfall, `QTextLayout` oder alter Zeichenfläche.
- **Vor jeder Änderung** an Dokumentverarbeitung, Import, Export, Textsatz, Layout, Rendering prüfen: Welche Komponente ist zuständig? Bleibt das Modell Qt-frei? Bleibt die Bearbeitung zentral und die Layout-Engine maßgeblich? Entsteht keine zweite Dokumentrepräsentation und kein Qt-Rückfall? Bleibt die GUI auf ihre Aufgaben beschränkt? Bei einem Verstoß nicht umsetzen, sondern eine konforme Lösung entwickeln. Im Zweifel den Eigentümer fragen, bevor Qt irgendwo im Dokumentweg verwendet wird.
- **Vorabsperre (aktiv):** Hook `werkzeuge/pruefungen/architektursperre_hook.py`, eingetragen in `.claude/settings.json` (PreToolUse für Edit, Write, MultiEdit, Bash). Er blockiert jede Änderung unter `src/lunivo_writer`, die einen neuen Architekturverstoß einführt, und Shell-Befehle, die Qt-Bezeichner in Dokument-Quelldateien schreiben. Den Hook oder die Einstellung nicht ändern, abschwächen oder umgehen.
- **Dauerhafte Regel für jede künftige Kompatibilitätskorrektur** (DOCX, ODT, RTF, TXT, Compatibility Tester, Fehlerberichte): Die Qt-freie Dokumentarchitektur bleibt erhalten. Bei fehlerhaften oder lückenhaften Dateien darf die Entwickler-KI nicht auf `QTextDocument` zurückgreifen, nicht die alte Dokument-Zeichenfläche oder den alten Editor (`editor/`) reaktivieren, keinen Qt-basierten Fallback einbauen, keine zweite Dokumentkopie führen (auch keine „nur für den Export“ oder „nur für die Vorschau“) und keine zweite Layoutberechnung einführen. Was ein Leser, Schreiber, die Bearbeitung, das Layout oder der Renderer nicht kann, wird dort ergänzt, oder der Verlust wird ausdrücklich im `IOReport` gemeldet — nie still verschluckt und nie als vollständiger Erfolg ausgegeben.
- **Ausgabe (PDF, Druck, Bildexport, Vorschau):** immer `dienste/drucken.py` (`Ausgabe`) bzw. `adapter/qt/pdf_ausgabe.py` auf dem maßgeblichen `Dokument` mit `LayoutEngine` und `DokumentRenderer`; PDF-Struktur (Lesezeichen, Hyperlinks, Notizen) über `dienste/pdf_struktur.py`. Qt liefert nur Zeichner und Druckgerät.
- **Technische Sperre:** `werkzeuge/pruefungen/architekturpruefung.py` (statisch, `ast`; geschützte Bereiche, GUI-Schicht und Regeln AQ-1 bis AQ-4, AQ-6 und AQ-7 stehen im Kopf der Datei). AQ-6: Qt-Dokumentklassen in der GUI-Schicht nur zusammen mit einem eigenen Qt-Textfeld (`QPlainTextEdit`, `QTextEdit`, `QTextBrowser`) in derselben Datei. AQ-7: keine `document_to_qt`/`document_from_qt`-Spiegelung. Die Prüfung ist für genehmigte Entwicklungsabläufe vorgesehen; ein Verstoß liefert Exitcode 1. Ein Verstoß ist blockierend und gilt nicht als erfolgreich abgeschlossen. Die Prüfung darf nicht abgeschwächt, deaktiviert oder durch Ausnahmelisten umgangen werden; neue Ausnahmen nur mit ausdrücklicher Genehmigung des Eigentümers. Ausgeführt wird sie nur nach ausdrücklicher Freigabe, eine automatische Einbindung braucht eine gesonderte Genehmigung. Nicht ausgeführte Prüfungen werden nie als bestanden bezeichnet.
