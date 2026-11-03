# Abschlussbericht: Sicherheit, Integrität, Architektur, Bedienbarkeit (2026-11-03)

Nichts committet. Tests nur gezielt (keine Vollsuite). Praxisprüfung mit Screenreader (Orca/NVDA) und Skalierung 125–200 % **nicht** durchgeführt.

## Erledigt
| Bereich | Änderung | Dateien |
|---|---|---|
| Import-Grenzen | Dateigröße, Teilezahl, tatsächlich entpackte Größe, Kompressionsverhältnis, XML-Größe, DTD/Entitäten, XML-Tiefe, Bildpunkte; Prüfung vor jeder Verarbeitung | `services/import_grenzen.py`, `docx_reader.py`, `odt_reader.py`, `file_service.py`, `editor/freie_bilder.py` |
| MCP | Zeilen-, Nachrichten-, Ergebnis-, Laufzeitgrenze; Prozessgruppe beenden; Umgebung ohne Zugangsdaten; Rückfrage mit Startbefehl; Aktionsart + volle Argumente je Aufruf | `ai/mcp.py`, `ai/ki.py`, `ai/ai_service.py`, `plattform/prozess.py` |
| LanguageTool | nur eigener Prozess auf freiem Port; fremder Dienst nur mit ausdrücklicher Erlaubnis; Status/Identität | `services/integrations/languagetool.py` |
| KI-Datenschutz | Einwilligung je Anbieter und Umfang mit Datum, Widerruf (Reiter „Datenschutz“), Sperre an der Sendestelle, robuste Antwortauswertung, `file://`-Bildadresse abgelehnt, Lücke in `ist_lokale_url` geschlossen | `ai/ki.py`, `ai/ai_service.py`, `ui/dialogs/ki_dialoge.py` |
| Speichern | Stand-Vergleich innerhalb der Sperre (`SchreibKonflikt`) | `services/sicher_schreiben.py`, `file_service.py`, `core/document_manager.py`, `ui/hauptfenster/dateien.py` |
| Fehler gefunden | Verbundene Tabellenzellen gingen beim DOCX-Lesen/Speichern verloren (Spannweite wurde beim Befüllen gelöscht) – behoben | `docx_teile/lesen_tabellen.py` |
| Schichten | beide Ausnahmen entfernt (`core/piktogramme.py`, Anbieter-Einhängung); Wächter für Betriebssystemaufrufe | `editor/formular.py`, `editor/einfuegen.py`, `tests/test_schichten.py` |
| Schreibhilfe | `ProofingIssue` ist Vertrag am Fund-Eingang (`bereinigen`) | `models/proofing.py`, `proofing/fund.py`, `proofing_service.py` |
| DOCX-Aufbau | Reader/Writer in fachliche Teile (Stile, Tabellen, Seite, Objekte, Zusatz) | `services/docx_teile/` |
| Korpus | 9 selbst erzeugte Dokumente, Roundtrip-Vergleich, Bericht | `werkzeug/docx_korpus.py`, `docs/docx-korpus-bericht.md` |
| Fehlerprotokoll | drei Fehlerarten, Schwärzung von Schlüsseln/Kennwörtern, Faden-Hook | `plattform/protokoll.py` |
| Formate/Integrationen/Plattform | Verzeichnisse und Dokumentation; `fsync`/Prozesse in `plattform/` | `services/formate.py`, `integrations/verzeichnis.py`, `plattform/dateisystem.py`, `docs/formate.md`, `docs/plattformen.md` |
| CI | ruff mit festen „echten Fehler“-Regeln, `ruff` in dev; Auswahl für Windows/macOS erweitert (weiter nicht blockierend) | `pyproject.toml`, `.github/workflows/pruefen.yml` |
| Bedienbarkeit | Kachelfeld, Backstage-Liste, Handbuch-Liste, Vorlagenregister, Bandpfeile tastaturbedienbar; Namen für Schrift/Größe/Vorlage/Zoom/„Worum“; Beschreibung der Funktionszeilen; Wächter und Ausnahmeliste | siehe `docs/pruefbericht-barrierefreiheit-2026-11-03.md` |
| Kontrast | rechnerische Prüfung aller Themen | `werkzeug/kontrast.py`, `docs/kontrast-bericht.md` |

## Offen / Einschränkungen
- Kontrast: behoben (Farben leicht angepasst), siehe docs/kontrast-bericht.md.
- Screenreader-Rollen (`QAccessible`) der selbstgebauten Widgets, Skalierung 125–200 %, Sichtprüfung der Fokusrahmen: nicht geprüft.
- Korpus: nur selbst erzeugte Dokumente; Dokumente aus Word/LibreOffice fehlen (Ordner `tests/korpus_extern/` wird mitgeprüft, sobald vorhanden).
- DOCX-Writer/Reader sind aufgeteilt, die Kernklassen bleiben groß; weitere Schnitte (Absatz/Lauf, Listen) nicht begonnen.
- `ProofingIssue` prüft am Eingang; die Schreibhilfe-Teile dahinter arbeiten weiter mit Wörterbüchern (schrittweise Umstellung offen).
- Die ZIP-Prüfung entpackt einmal zum Zählen (Zeitaufwand bei sehr großen Paketen).
- Beobachtet, nicht geändert: `core/befehle/seite.py` definiert `seitenraenderRahmen` doppelt; Windows/macOS-CI bleibt nicht blockierend.
- Gesamtlauf (CI) steht aus: lokal nur gezielte Tests.
