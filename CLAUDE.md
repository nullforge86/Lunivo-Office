# Lunivo Writer — Regeln für dieses Projekt

**Lunivo ist eine native Desktop-Anwendung in Python 3 mit PySide6 (Qt Widgets). Es ist keine Web-Anwendung und war nie eine.**

## Kein HTML — nirgends

Das gilt ausnahmslos und auch „nur intern“: **kein HTML, kein JavaScript, kein CSS, kein Browser, kein WebEngine/WebKit,
kein lokaler Webserver** — weder als Oberfläche noch als Dateiformat, Datenformat, Zwischenformat, Vorschau, Bericht oder
Werkzeug-Ausgabe. Sobald irgendwo HTML steckt, baut die nächste Arbeit darauf auf und das Projekt kippt Richtung Webanwendung.
Deshalb gar nicht erst anfangen.

- Text im Dokument: `QTextDocument`, `QTextCursor`, `QTextCharFormat`, `QTextBlockFormat` — niemals `toHtml`, `setHtml`,
  `insertHtml`, `fromHtml`.
- Speichern und Öffnen: DOCX, ODT, TXT, PDF (keine Webseite).
- Eigene Daten (Textbausteine u. a.): JSON ohne Markup, siehe `src/lunivo_writer/editor/textdaten.py`.
- Hilfe- und Infotexte: Markdown mit `QTextBrowser.setMarkdown`, Formeln und Vorschauen mit `QTextDocument` und `QPainter`.
- Berichte und Dokumentation: Markdown. Werkzeuge in `werkzeug/` schreiben kein HTML.
- Sieht eine Aufgabe nach HTML aus, einen Qt-Weg suchen. Gibt es keinen, dem Eigentümer melden — nicht ausweichen.

Gemeint sind Lunivos **eigene** Dateien, Daten und Code. Einzige Ausnahme: das Einfügen aus der Zwischenablage nimmt Inhalte aus
fremden Programmen an (`ui/document/base.py`, `document_editor.py`) — das ist keine Datei und kein Format von Lunivo.

Der Wächtertest `tests/test_main_window.py::test_kein_html_im_projekt` muss grün bleiben. Seine Liste `HTML_NOCH_ERLAUBT` darf
nur kleiner werden, nie größer.

## Arbeitsweise

- Ablauf für jede Aufgabe: relevante Dateien und Regeln prüfen → kleinste nötige Änderung umsetzen → nur bei geändertem Verhalten die direkt passende Prüfung ausführen → knapp berichten. Bei reiner Doku/Optik keine Funktionstests.
- Nur Kontext laden, der für den Auftrag gebraucht wird. Keine umfassende Bestandsaufnahme, langen Pläne oder Wiederholung bereits bekannter Regeln.
- Aufbau des Projekts: `docs/README.md`. Gemeinsame Oberflächen-Bausteine (Farbpalette, Linien, Menüs, Dialoggerüst):
  `src/lunivo_writer/ui/baukasten/` und `docs/baukasten.md` — dort nachsehen, bevor etwas Neues gebaut wird.
- **Fensterbau (Pflicht):** Fenster öffnen in der rechten Seitenleiste. Felder immer mit `FormularGitter` (`zeile`, `reihe`, `breit`),
  `UmbruchSchalter`, `FlussLayout`, `abschnittstitel` aus `ui/baukasten/formular_gitter.py` bauen — Muster `ui/baukasten/absatz_dialog.py`.
  Kein festes `QGridLayout`, kein `schmal_nein`, keine breiten Mindestmaße. Was in der Vorlage rechts steht (Vorschau), kommt darunter.
  Bei 300 px Breite darf nichts herausragen.
- Gezielter Test bei relevanter Verhaltensänderung: `.venv/bin/python -m pytest <testdatei> -k <testname>`. Nie `pytest` ohne Auswahl starten. Bandprüfung nur bei Änderungen am Band: `werkzeug/funktionspruefung.py`.
- Das Projekt liegt nicht unter Git. Vor größeren Löschungen oder Umbauten eine Sicherung anlegen.
- Bildschirmfotos sind nur ein Aussehens-Vorbild. Keine fremden Dateien, Grafiken oder Farbtabellen übernehmen.

## Arbeitsauftrag: modular entwickeln, Tests risikobasiert (verbindlich)

Festgelegt vom Eigentümer am 2026-10-22. Gilt für jede Aufgabe an diesem Projekt.

### 1. Grundprinzip
Das Projekt musste zunächst in Module zerlegt werden. Die modulare Architektur ist die zentrale Voraussetzung für die weitere Entwicklung und
darf nicht durch unnötige Änderungen, Vermischung von Zuständigkeiten oder überflüssige Gesamtprüfungen unterlaufen werden.

- Baukastenprinzip: Jedes Modul hat eine klar definierte Aufgabe, feste Schnittstellen und möglichst wenige Abhängigkeiten.
- Bestehende Module und gemeinsame Bausteine wiederverwenden. Keine parallelen Lösungen erfinden, wenn passende Komponenten vorhanden sind.

### 2. Vor jeder Änderung
- Nur betroffene Module, Schnittstellen und nötige Dokumentation untersuchen.
- Änderung auf den nötigen Umfang begrenzen; bestehende Funktionen und Schnittstellen bewahren.
- Keine unabhängigen Module ändern und keine umfassenden Refactorings ohne sachlichen Grund starten.

### 3. Prüfungen: nur passend zur Änderung
- Keine Tests für reine Dokumentation oder Änderungen ohne Auswirkung auf ausführbares Verhalten.
- Bei Verhaltensänderungen nur den direkt passenden Test ausführen, sofern vorhanden und aussagekräftig. Direkte Abhängigkeiten nur prüfen, wenn die Änderung sie betreffen kann.
- Bei Schnittstellen oder gemeinsam genutzten Bausteinen gezielt deren betroffene Integrationen prüfen. Umfang am Risiko ausrichten; keine lokale Vollsuite.
- Neue Tests nur ergänzen, wenn sie die geänderte Funktion direkt absichern. Keine Tests „vorsorglich“ oder nur zur Erhöhung der Abdeckung.
- Keine lokalen Volltests: sie dauern über 30 Minuten und verbrauchen das Sitzungslimit; die Gesamtprüfung macht die CI.

### 4. Keine unnötigen Wiederholungen
- Erfolgreiche Tests nicht wiederholen, wenn sich der getestete Code seitdem nicht relevant geändert hat; gültige Ergebnisse weiterverwenden.
- Fehlgeschlagene Tests nur wiederholen, wenn der Fehler behoben wurde, die Ursache untersucht wird oder die Wiederholung fachlich begründet ist.
- Zusammengehörige Änderungen gemeinsam prüfen, nicht nach jedem Zwischenschritt.

### 5. Projektregeln und technische Grenzen
- Bei der vorhandenen Python-/PySide6-Architektur bleiben; den bestehenden UI-Baukasten und die dokumentierten Konventionen verwenden.
- Keine Webtechnologien oder Architekturen einführen, die den Projektregeln widersprechen (siehe „Kein HTML“).
- Die CI-Konfiguration nicht ändern, nur um lokal weniger zu testen. Die automatische Gesamtprüfung bei Push und Pull Request bleibt als Sicherheitsnetz.

### 6. Knapp berichten
Nenne Ergebnis und geänderte Dateien. Tests, Architekturbegründung, Risiken und offene Punkte nur erwähnen, wenn sie für diese Änderung relevant sind. Tatsächliche Prüfergebnisse korrekt wiedergeben; nichts als geprüft ausgeben, was nicht geprüft wurde.

**Oberste Priorität:** Modular entwickeln. Nur betroffene Bereiche prüfen. Volltests risikobasiert und gezielt einsetzen. Keine unnötigen
Wiederholungen, keine unnötigen Umbauten, keine Änderungen außerhalb des erforderlichen Umfangs.

## Agenten (`.claude/agents/`)

| Bereich | Agent |
|---|---|
| Qt-Oberfläche | `design-agent` |
| Geschäftslogik/Verhalten | `coding-agent` |
| Architekturfragen | `architektur-agent` (liest und empfiehlt) |
| Sicherheit/Datenschutz | `security-agent` (liest und meldet) |
| Unabhängige QA | `qa-agent` (nur bei Bedarf) |
| Mehrere Zuständigkeiten/Abhängigkeiten | `coordinator` |

Ein klarer Einzelauftrag braucht keinen Coordinator. Delegierte Pakete enthalten nur Ziel, relevante Dateien, Grenzen und erwartetes Ergebnis. Abhängiges nacheinander bearbeiten; parallel nur bei unabhängigen Paketen. Nie gleichzeitig an derselben Datei schreiben. QA nur auf ausdrücklichen Wunsch oder bei konkret erhöhtem Risiko. Jeder Agent liest nur nötigen Kontext und berichtet knapp; der Coordinator fasst einmal zusammen. Vor größeren Umbauten, neuen Abhängigkeiten, kostenpflichtigen Diensten oder nicht umkehrbaren Aktionen Zustimmung einholen.

### Verbindlicher Ablauf bei Aufgaben mit Oberfläche oder Zuständen (Eigentümer, 2026-11-03)

Gilt in **jeder** Sitzung automatisch; der Eigentümer muss nicht daran erinnern. Die Agenten (der Eigentümer nennt sie „Konnektoren“) sind dafür eingeführt, Layout und Funktionen getrennt zu bearbeiten. Die Hauptsitzung ist Vermittler und trägt die Verantwortung, dass dieser Ablauf eingehalten wird.

1. **Zuerst `architektur-agent` (nur lesend).** Bevor etwas gebaut wird, klärt er: Welche Bausteine, Fenster, Befehle und Menüs gibt es schon (`docs/baukasten.md`, `docs/interne-funktionen.md`, grep)? Welche Zustände und **Zustandswechsel** sind betroffen (Auswahl, Modus, Kontext — z. B. Text in einer Zelle ↔ mehrere Zellen ↔ Tabelle ↔ außerhalb)? Was zeigen die Vorbild-Bilder des Eigentümers (Reihenfolge, Symbole, Breite, Abstände)? Ergebnis: kurzer Plan mit Zuständigkeiten und Dateien.
2. **Dann `coding-agent`** (Logik, Befehle, Zustände), **danach `design-agent`** (Qt-Oberfläche), strikt nacheinander, nie zwei gleichzeitig; jede Aufgabe genau einem Bearbeiter. Aufträge nennen den Plan des Architekten, vorhandene Bausteine zum Wiederverwenden und die Vorbild-Bilder.
3. **Bestand vor Neubau:** Nie ein zweites Fenster, einen zweiten Befehl oder eine zweite Leiste neben einem vorhandenen bauen; den vorhandenen Baustein erweitern.
4. **Kontextabhängig:** Bedienelemente zeigen nur, was im aktuellen Zustand gilt (Tabelle: Tabellenfunktionen; reine Textbearbeitung: nur Textfunktionen) und schalten bei Zustandswechsel sofort um.
5. **Vermittler prüft jeden Bericht** gegen Auftrag und Vorbild-Bilder und schickt zurück, was fehlt (z. B. „Vorlage nicht angesehen“, „Zustand nicht geprüft“). Erst danach dem Eigentümer berichten; Nicht-Geprüftes offen nennen.
6. Fehlen die Agentenprofile unter `.claude/agents/`, aus einer Sicherung wiederherstellen oder melden, bevor gearbeitet wird.
7. **Zeitlimit für Agenten (Eigentümer, 2026-11-03):** Jeder Agentenauftrag bekommt beim Start ein Zeitlimit (Lesen/Messen 15 Minuten, Umsetzen 25 Minuten) mit einem Hintergrund-Wecker (`sleep` im Hintergrund). Ist 10 Minuten lang weder eine neue Änderung im Arbeitsbaum (`git status`) noch eine neue Datei im Scratchpad entstanden (die Ausgabedatei des Agenten ist KEIN Fortschrittsanzeiger: sie hat immer nur wenige Byte), oder läuft das Limit ab, wird der Agent gestoppt (`TaskStop`), das Teilergebnis geprüft und dem Eigentümer gemeldet. Agenten dürfen das Sitzungslimit des Eigentümers nicht durch Hängen verbrauchen.

## Ergänzende Eigentümer-Regeln (2026-10-25 bis 2026-10-28)

Gelten für alle Agenten zusätzlich zu den Regeln oben; bei Widerspruch gilt die jüngere Regel.

- **Eigenständig:** keine Abhängigkeit von externen Programmen, auch nicht für Dateiformate — Formate selbst schreiben.
- **Vorlagen eng nachbauen:** Kays Bildschirmfotos (PC: Ordner mit den Vorlagen-Bildschirmfotos unter `~/Bilder`) sind das Aussehens-Vorbild; keine freien
  Interpretationen, klar erkennbare Symbole, Felder/Knöpfe nicht schmaler als ~36 px. Fertig erst nach Bildvergleich mit der Vorlage.
- **Paketierung (Ziel):** genau eine `.deb`; Anwendung unter `/opt/stevie-empire/lunivo-office/`, Starter
  `/usr/share/applications/stevie-lunivo-office.desktop`, Symlink `/usr/bin/lunivo-office`; Benutzerdaten nur in XDG-Verzeichnissen.

## Orchestrator-Regeln und Replica Skill (Eigentümer, 2026-11-03)

Ergänzung zu den Regeln oben; bei Widerspruch gelten die Abschnitte oben („Kein HTML“, Tests, Agenten). Der Master-Prompt ist hier in
seinen verbindlichen Kernpunkten übernommen.

### Aufgabenverteilung
- Der Orchestrator zerlegt einen Auftrag nur so weit wie nötig. Jede Teilaufgabe hat genau einen Bearbeiter (Agent oder Konnektor):
  keine Doppelvergabe, keine parallele Bearbeitung derselben Aufgabe, keine konkurrierenden Änderungen an derselben Datei.
- Untergeordnete Agenten und Konnektoren verteilen nichts weiter und starten keine weiteren Konnektoren. Unklare Zuständigkeit geht
  zurück an den Orchestrator. Eine Aufgabe, die ohne Agent erledigt werden kann, wird direkt erledigt.
- Zuständigkeiten bleiben wie in der Tabelle „Agenten“: Coding = Fachlogik und Zustand, Design = Qt-Oberfläche, Architektur und
  Security = lesen und empfehlen, QA = nur gezielte Prüfung, Coordinator = Planung ohne Produktionscode. Die Agentenprofile gelten weiter.

### Konnektoren
- Konnektoren laufen strikt nacheinander: Ergebnis prüfen, erst dann den nächsten starten. Nie gleichzeitig, auch nicht im Hintergrund.
- Sparsam einsetzen: nur wenn nötig, nur mit abgegrenztem Auftrag, keine Wiederholung erfolgreicher Aufrufe, Ergebnisse weiterverwenden.

### Tests
- Keine Volltests, keine vollständigen Suiten, keine ungezielten Regressionstests, auch nicht durch Agenten oder Konnektoren.
- Nur der direkt zur Aufgabe passende Test. Ist keiner möglich, das im Bericht sagen; nie ersatzweise eine Vollsuite starten.

### Funktions- und Zustandslogik
- Jede Benutzeraktion löst die richtige Funktion aus; keine rein optischen Elemente, keine funktionslosen Schaltflächen.
- Eine Datenquelle je Zustand (Dokument, Auswahl, Formatierung, aktive Vorlage, Bearbeitungsmodus, Schreibschutz); die Oberfläche
  leitet daraus ab. Vorhandene Signale, Slots und Modelle wiederverwenden, keine Doppelimplementierung.
- Kontextabhängig: Werkzeuge ohne gültigen Kontext deaktivieren, benötigte nicht verstecken. Bei Vorlagenwechsel veraltete
  Werkzeugauswahl zurücksetzen, ohne Benutzerinhalte zu verlieren. Vorlagenzustände speichern und wiederherstellen.
- Fehlgeschlagene Aktionen lassen einen konsistenten Zustand zurück und melden verständlich. Änderungen laufen über die vorhandene
  Undo-/Redo-Architektur, keine parallele Lösung.

### Replica Skill (`Jakeschincariol/replica-skill`)
- Einsatz nur zur Analyse und Dokumentation von Referenzprogrammen (Funktionen, Abläufe, Komponenten, Zustandsmodelle, Menüs, Dialoge)
  und zum Vergleich mit der Umsetzung. Ergebnisse als Markdown, nie als HTML.
- Umsetzung ausschließlich in Python und PySide6 (Qt Widgets) mit den vorhandenen Lunivo-Bausteinen. Keine fremden Quellcodes, Logos,
  geschützten Texte oder proprietären Inhalte übernehmen; Bedienkonzepte eigenständig umsetzen (siehe auch Regel „Bildschirmfotos“).
- Ablauf: Replica Recon (Analyse) → Architektur-Agent (Machbarkeit) → Design-Agent (Oberfläche) und Coding-Agent (Logik) → Security-Agent
  bei sicherheitsrelevanten Teilen → QA-Agent nur gezielt. Jede Aufgabe hat genau einen Bearbeiter.
