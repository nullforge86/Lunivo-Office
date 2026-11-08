# Technische Optimierungsanalyse

> Erste Bestandsaufnahme auf Basis der Repository-Dateien. Dies ist eine priorisierte Prüfliste, keine vollständige Codeprüfung und keine Aussage über bereits gemessene Laufzeitprobleme.

## Geprüfte Ausgangspunkte

- `pyproject.toml`: Python >= 3.10; PySide6/Qt Widgets; optionale Offline-Übersetzung; Ruff ist derzeit auf ausgewählte Fehlerregeln begrenzt (`E9`, `F63`, `F7`, `F82`).
- `tests/test_schichten.py`: prüft, dass `editor/`, `services/`, `models/` und `proofing/` nicht aus `ui/` importieren. Die Ausnahmeliste ist leer.
- `proofing/proofing_service.py`: Schreibhilfe führt Prüfungen in einem `QThreadPool` mit maximal einem Worker aus, prüft Dokumentrevisionen und verwirft veraltete Ergebnisse.
- `core/befehle/datei.py`: enthält einen direkten Import eines UI-Eingabedialogs. Das ist nicht durch den aktuellen Schichtentest verboten, zeigt aber eine Kopplung zwischen Befehlslogik und Oberfläche.
- `core/application.py`: initialisiert die Anwendung und greift für Theme- und Accessibility-Setup direkt auf UI-Module zu. Das kann für den Composition Root angemessen sein; die Grenze sollte bewusst dokumentiert bleiben.

## Priorisierte Maßnahmen

### P0 – Architekturgrenzen messbar machen

1. Abhängigkeiten zwischen `core`, `editor`, `services`, `models`, `proofing` und `ui` vollständig erfassen.
2. Direkte UI-Abhängigkeiten in `core/befehle/` einzeln prüfen. Dialoge möglichst über injizierte Schnittstellen oder UI-seitige Adapter bereitstellen, sofern dadurch keine unnötige Abstraktion entsteht.
3. Schichtentests um die gewünschte Abhängigkeitsrichtung ergänzen. Die bereits leere Ausnahmeliste beibehalten.

**Abnahmekriterium:** Architekturregeln sind automatisiert getestet; neue UI-Abhängigkeiten in fachlichen Modulen schlagen in CI fehl.

### P1 – Test- und Qualitätsbasis erweitern

1. Bestehende pytest-Sammlung und CI-Läufe als Baseline erfassen.
2. Ruff-Regeln schrittweise erweitern, zunächst ohne pauschale Formatierungsänderungen.
3. Tests für kritische Dokumentpfade ergänzen: öffnen, bearbeiten, speichern, erneut öffnen und exportieren.
4. Fehlerfälle für beschädigte oder nicht unterstützte Dateien abdecken.

**Abnahmekriterium:** Jede Erweiterung der Lint-Regeln und jedes neue Testpaket läuft in CI; bestehende Funktionen bleiben unverändert.

### P1 – Schreibhilfe robust halten

1. Tests für verspätete Worker-Ergebnisse, Dokumentwechsel und schnelle Folgeänderungen ergänzen.
2. Prüfen, ob Worker-Ergebnisse nach dem Schließen/Wechseln eines Dokuments sicher ignoriert werden.
3. Fehlerzustände und Statusmeldungen der Hintergrundprüfung testen.
4. Performance nur anhand repräsentativer Dokumente messen, bevor Caching oder Parallelisierung geändert wird.

**Abnahmekriterium:** Keine veralteten Prüfergebnisse werden auf einen geänderten Dokumentstand angewendet; UI bleibt während der Prüfung bedienbar.

### P2 – Formatkompatibilität und Performance

1. DOCX-/ODT-/RTF-Roundtrip-Testfälle anhand realitätsnaher Beispieldokumente ausbauen.
2. Tabellen, Bilder, Kopf-/Fußzeilen, Listen und Formatvorlagen separat prüfen.
3. Startzeit, Speicherverbrauch und Reaktionszeit bei großen Dokumenten messen.
4. Optimierungen erst nach Profiling umsetzen.

**Abnahmekriterium:** Keine Regression in den dokumentierten Formatfällen; Performanceänderungen sind mit Vorher-/Nachher-Messungen belegt.

## Empfohlene Reihenfolge

1. CI- und Testbaseline dokumentieren.
2. Abhängigkeitsanalyse vervollständigen.
3. Einen kleinen, isolierten Architekturverbesserungsschritt umsetzen.
4. Dokument-Roundtrip-Tests ausbauen.
5. Erst danach Performance- und UI-Optimierungen angehen.

## Noch nicht geprüft

- Vollständiger Modul-/Importgraph
- Testabdeckung und tatsächliche CI-Ergebnisse
- Laufzeitprofile und Speicherprofile
- Vollständige Import-/Export-Kompatibilität
- Plattformverhalten unter Windows und macOS

Diese Punkte benötigen eine vertiefte Prüfung des gesamten Quellbestands und – für Laufzeit- und CI-Aussagen – tatsächliche Testläufe.
