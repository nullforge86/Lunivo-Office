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

- Aufbau des Projekts: `docs/README.md`. Gemeinsame Oberflächen-Bausteine (Farbpalette, Linien, Menüs, Dialoggerüst):
  `src/lunivo_writer/ui/baukasten/` und `docs/baukasten.md` — dort nachsehen, bevor etwas Neues gebaut wird.
- **Fensterbau (Pflicht):** Fenster öffnen in der rechten Seitenleiste. Felder immer mit `FormularGitter` (`zeile`, `reihe`, `breit`),
  `UmbruchSchalter`, `FlussLayout`, `abschnittstitel` aus `ui/baukasten/formular_gitter.py` bauen — Muster `ui/baukasten/absatz_dialog.py`.
  Kein festes `QGridLayout`, kein `schmal_nein`, keine breiten Mindestmaße. Was in der WPS-Vorlage rechts steht (Vorschau), kommt darunter.
  Bei 300 px Breite darf nichts herausragen.
- Tests: `.venv/bin/python -m pytest` (laufen ohne Bildschirm). Funktionsprüfung des Bandes: `werkzeug/funktionspruefung.py`.
- Das Projekt liegt nicht unter Git. Vor größeren Löschungen oder Umbauten eine Sicherung anlegen.
- WPS Office ist nur ein Aussehens-Vorbild (Bildschirmfotos). Keine WPS-Dateien, -Grafiken oder -Farbtabellen übernehmen.

## Arbeitsauftrag: modular entwickeln, Tests risikobasiert (verbindlich)

Festgelegt vom Eigentümer am 2026-10-22. Gilt für jede Aufgabe an diesem Projekt.

### 1. Grundprinzip
Das Projekt musste zunächst in Module zerlegt werden. Die modulare Architektur ist die zentrale Voraussetzung für die weitere Entwicklung und
darf nicht durch unnötige Änderungen, Vermischung von Zuständigkeiten oder überflüssige Gesamtprüfungen unterlaufen werden.

- Baukastenprinzip: Jedes Modul hat eine klar definierte Aufgabe, feste Schnittstellen und möglichst wenige Abhängigkeiten.
- Bestehende Module und gemeinsame Bausteine wiederverwenden. Keine parallelen Lösungen erfinden, wenn passende Komponenten vorhanden sind.

### 2. Vor jeder Änderung
- Zuerst die vorhandene Projektstruktur und die betroffenen Module untersuchen; die relevanten Anweisungen und Dokumentationen lesen.
- Ermitteln, welche Dateien, Schnittstellen und Abhängigkeiten tatsächlich betroffen sind. Die Änderung auf den erforderlichen Umfang begrenzen.
- Keine unabhängigen Module ändern und keine umfassenden Refactorings ohne sachlichen Grund starten.
- Bestehende Funktionen und Schnittstellen bewahren, sofern eine Änderung nicht ausdrücklich erforderlich ist.

### 3. Teststrategie: nach Risiko, nicht nach Gewohnheit
Nicht nach jeder kleinen Änderung die komplette Testsuite ausführen. Den Umfang am tatsächlichen Risiko ausrichten:

1. **Kleine, isolierte Änderung:** nur die unmittelbar relevanten Tests. Reine Dokumentationsänderungen und Änderungen ohne Auswirkung auf
   ausführbares Verhalten brauchen keine Funktionstests. Keine Volltests ohne konkreten Grund.
2. **Änderung innerhalb eines Moduls:** die gezielten Tests dieses Moduls. Direkte Abhängigkeiten nur, wenn die Änderung sie betreffen kann.
3. **Schnittstellen oder gemeinsame Bausteine:** das geänderte Modul und die unmittelbar abhängigen Module. Beim gemeinsamen UI-Baukasten die
   tatsächlich betroffenen Komponenten und Integrationen.
4. **Architekturänderung oder hohes Risiko** (Modulgrenzen, zentrale Schnittstellen, globale Konfiguration, mehrere abhängige Bereiche):
   umfassendere Tests. Die komplette Suite insbesondere vor einem größeren Abschluss, einer relevanten Zusammenführung oder Veröffentlichung.

### 4. Keine unnötigen Testwiederholungen
- Erfolgreiche Tests nicht wiederholen, wenn sich der getestete Code seitdem nicht relevant geändert hat; gültige Ergebnisse weiterverwenden.
- Fehlgeschlagene Tests nur wiederholen, wenn der Fehler behoben wurde, die Ursache untersucht wird oder die Wiederholung fachlich begründet ist.
- Nicht aus Gewohnheit nach jedem Bearbeitungsschritt die ganze Suite starten. Bei mehreren zusammengehörigen kleinen Änderungen zuerst die
  erforderlichen gezielten Tests, nicht nach jeder einzelnen einen Volltest.

### 5. Projektregeln und technische Grenzen
- Bei der vorhandenen Python-/PySide6-Architektur bleiben; den bestehenden UI-Baukasten und die dokumentierten Konventionen verwenden.
- Keine Webtechnologien oder Architekturen einführen, die den Projektregeln widersprechen (siehe „Kein HTML“).
- Die CI-Konfiguration nicht ändern, nur um lokal weniger zu testen. Die automatische Gesamtprüfung bei Push und Pull Request bleibt als Sicherheitsnetz.

### 6. Transparenz: nach jeder Aufgabe kurz angeben
1. Welche Module oder Dateien geändert wurden.
2. Warum die Änderung in die vorhandene Architektur passt.
3. Welche gezielten Tests ausgeführt wurden und weshalb.
4. Ob ein Volltest erforderlich war; falls nicht, knapp warum die gezielten Prüfungen genügen.
5. Welche bekannten Risiken oder offenen Punkte bleiben.

Niemals behaupten, Tests seien erfolgreich gewesen, wenn sie nicht tatsächlich ausgeführt wurden.

**Oberste Priorität:** Modular entwickeln. Nur betroffene Bereiche prüfen. Volltests risikobasiert und gezielt einsetzen. Keine unnötigen
Wiederholungen, keine unnötigen Umbauten, keine Änderungen außerhalb des erforderlichen Umfangs.

## Multi-Agent-Aufbau (`.claude/agents/`)

Spezialisten mit getrennten Zuständigkeiten. Für einfache Aufgaben genügt der zuständige Spezialist; nicht alle Agenten starten.

| Agent | Zuständig für | Schreibt? |
|---|---|---|
| `coordinator` | Plan, Arbeitspakete, Routing, Integration, Konflikte, Abschlussbericht | nein (delegiert) |
| `coding-agent` | Geschäftslogik, Funktionen, Fehlerbehebung, zugehörige Tests | ja |
| `design-agent` | UI/UX: Layout, Optik, Farben, Abstände, Barrierefreiheit | ja (nur UI) |
| `architektur-agent` | Struktur, Abhängigkeiten, Schnittstellen; Empfehlung vor Umbau | nein |
| `qa-agent` | Unabhängige Prüfung, Tests, Regression, Reproduktionsschritte | nein |
| `security-agent` | Sicherheit, Datenschutz, Code-Review | nein |

Regeln:
- UI/Design → design-agent · Geschäftslogik → coding-agent · Architektur/Abhängigkeiten → architektur-agent (Freigabe vor Umsetzung) ·
  Tests/Qualitätskontrolle → qa-agent · Sicherheit → security-agent · Integration und Konflikte → coordinator.
- Berührt ein Paket mehrere Bereiche, teilt der Coordinator es auf und benennt die Übergabepunkte.
- Gemeinsame Dateien oder abhängige Ergebnisse: nacheinander. Nur unabhängige Pakete parallel. Niemand überschreibt Änderungen anderer stillschweigend.
- Reihenfolge: Plan → Untersuchung (lesend) → Umsetzungsentscheidung → Umsetzung → unabhängige QA → Integration/Bericht.
- Rückfrage beim Eigentümer vor größeren Umbauten, neuen Abhängigkeiten, kostenpflichtigen Diensten, nicht umkehrbaren Aktionen.
- Berichte kurz: Ergebnis, geänderte Dateien, Tests, offene Probleme.
- Aufruf: `claude --agent coordinator` (Coordinator als Hauptagent), oder gezielt „Nutze den coding-agent für …“ / `@coding-agent`. `/agents` zeigt die Liste.
- Hinweis: Subagenten können keine weiteren Subagenten starten; Delegation läuft deshalb über den Hauptagenten (Coordinator).

## Ergänzende Eigentümer-Regeln (2026-10-25 bis 2026-10-28)

Gelten für alle Agenten zusätzlich zu den Regeln oben; bei Widerspruch gilt die jüngere Regel.

- **Keine lokalen Volltests** (2026-10-28, ersetzt „komplette Suite vor Abschluss“ in §3): Ein Volltest dauert über 30 Minuten und
  verbraucht das Sitzungslimit. Lokal nur die Tests der gerade gebauten Funktion (`pytest <datei> -k <name>`); die Gesamtprüfung macht die CI.
- **Eigenständig:** keine Abhängigkeit von LibreOffice oder anderen externen Programmen, auch nicht für Dateiformate — Formate selbst schreiben.
- **WPS-Vorlagen eng nachbauen:** Kays Bildschirmfotos (PC: `~/Bilder/wps-vorlage`) sind das Aussehens-Vorbild; keine freien
  Interpretationen, klar erkennbare Symbole, Felder/Knöpfe nicht schmaler als ~36 px. Fertig erst nach Bildvergleich mit der Vorlage.
- **Paketierung (Ziel):** genau eine `.deb`; Anwendung unter `/opt/stevie-empire/lunivo-office/`, Starter
  `/usr/share/applications/stevie-lunivo-office.desktop`, Symlink `/usr/bin/lunivo-office`; Benutzerdaten nur in XDG-Verzeichnissen.
- **Kurz berichten:** Der Eigentümer schreibt mit eingeschränkter Hand; Berichte knapp halten, keine Testläufe per Subagent ohne Grund.
