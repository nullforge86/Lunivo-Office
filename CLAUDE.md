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
  Kein festes `QGridLayout`, kein `schmal_nein`, keine breiten Mindestmaße. Was in der WPS-Vorlage rechts steht (Vorschau), kommt darunter.
  Bei 300 px Breite darf nichts herausragen.
- Gezielter Test bei relevanter Verhaltensänderung: `.venv/bin/python -m pytest <testdatei> -k <testname>`. Nie `pytest` ohne Auswahl starten. Bandprüfung nur bei Änderungen am Band: `werkzeug/funktionspruefung.py`.
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

## Ergänzende Eigentümer-Regeln (2026-10-25 bis 2026-10-28)

Gelten für alle Agenten zusätzlich zu den Regeln oben; bei Widerspruch gilt die jüngere Regel.

- **Eigenständig:** keine Abhängigkeit von LibreOffice oder anderen externen Programmen, auch nicht für Dateiformate — Formate selbst schreiben.
- **WPS-Vorlagen eng nachbauen:** Kays Bildschirmfotos (PC: `~/Bilder/wps-vorlage`) sind das Aussehens-Vorbild; keine freien
  Interpretationen, klar erkennbare Symbole, Felder/Knöpfe nicht schmaler als ~36 px. Fertig erst nach Bildvergleich mit der Vorlage.
- **Paketierung (Ziel):** genau eine `.deb`; Anwendung unter `/opt/stevie-empire/lunivo-office/`, Starter
  `/usr/share/applications/stevie-lunivo-office.desktop`, Symlink `/usr/bin/lunivo-office`; Benutzerdaten nur in XDG-Verzeichnissen.
