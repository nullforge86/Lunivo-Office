# Lunivo Office – Technische Übergabe zum Neuaufbau

Diese Übergabe ergänzt die beiden Hauptprompts, ohne deren Anforderungen zu ändern. Maßgebliche Rangfolge und Arbeitsgrenzen stehen in `CLAUDE.md`; Funktionsumfang, Prüfregeln und Abschlussbedingungen im `Lunivo_Office_Hauptprompt.md`.

## Projekt und Referenzen

- **Zielpaket:** `/home/kaysiebke/Videos/Lunivo-Office-aufgeraeumt/Lunivo-Office-aufgeraeumt/src/lunivo_writer/`.
- **Separater Qt-freier Kern (nur lesend):** `/home/kaysiebke/Videos/Lunivo-Office-aufgeraeumt/document_core/`.
- **Weitere Qt-freie Bausteine (nur lesend):** `/home/kaysiebke/Videos/Lunivo-Office-aufgeraeumt/Qt-freie-Bausteine/` (36 Module: `text/` 22, `dokument/` 14).

## Wiederverwendung: technischer Befund

Die verbindliche Sonderregel und ihre Grenzen stehen in Hauptprompt § 5. Die bisherige Sichtung des separaten `document_core` ergab ein Qt-freies Dokumentmodell, eine zentrale `DokumentEngine`, Bearbeitungsoperationen, Rückgängig/Wiederholen, Text- und Formatoperationen, Tabellen, Objekte, Abschnitte, Zusatzfunktionen und Serialisierung. **Die Vollständigkeit einzelner Funktionen ist nicht nachgewiesen.**

Für konkrete Aufgaben geeignete Teile in `document_core` und `Qt-freie-Bausteine` gezielt sichten und in die bestehende Zielstruktur integrieren. Insbesondere die bisherige Seitenaufteilung nicht mit einer vollständigen Textsatz-, Layout- und Rendering-Engine gleichsetzen. Keine zweite maßgebliche Dokumentdatenhaltung aufbauen. Die übrigen Regeln zu Wiederverwendung, Oberflächenerhalt, schrittweiser Ablösung und Verboten gelten unmittelbar aus Hauptprompt §§ 3–5.

## Bestehender Quellcode und technische Orientierung

Der bisherige Qt-gebundene Code dient als Referenz für Funktionen, Datenformate, Schnittstellen, Aufrufstellen und Bedienabläufe, **nicht** als dauerhaftes Dokumentmodell. Bereits vorbereitete `core/`-Module sind nicht automatisch verpflichtende Architekturgrundlagen.

- `KI_NEUAUFBAU_sauber(2).md`: bisherige Erkenntnisse, wiederverwendbare Komponenten und offene Punkte.
- `KI_PROJEKTUEBERSICHT.md`: statisch erfasste Projektstruktur, Module, Klassen, Funktionen und Imports.

Beide sind Nachschlagewerke. Nur die für den jeweiligen Implementierungsschritt nötigen Teile lesen.

## Durchführung

Die technische Reihenfolge und Arbeitsgrenzen stehen in Hauptprompt §§ 2, 4 und 5. Bei jedem konkreten Schritt die betroffenen Funktionen und Aufrufstellen bestimmen, passende Referenzimplementierungen sichten, gezielt integrieren oder ergänzen und die bestehenden Bedienelemente anbinden. Prüffreigaben bleiben auf den Umfang nach Hauptprompt § 4.2 beschränkt.

## Optionale Zusatzdienste

Die verbindliche Architektur steht in Hauptprompt § 13.3 und `writing-block.md`. Als vorhandene Kandidaten bei konkretem Bedarf Vorlesen, Argos, LanguageTool, Ollama und Ressourcen prüfen; keine pauschale Migration sämtlicher Dienste.

## Abschluss

Für Endergebnis, vollständigen Funktionserhalt, Arbeitsreihenfolge und Abschlussbedingungen gelten die beiden Hauptprompts. Diese Datei ist eine technische Übergabe, keine zusätzliche Spezifikation des Funktionsumfangs.
