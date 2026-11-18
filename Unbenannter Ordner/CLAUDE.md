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
