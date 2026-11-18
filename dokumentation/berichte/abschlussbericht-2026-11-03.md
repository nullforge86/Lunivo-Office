# Abschlussbericht: Sicherheit, Integrität, Architektur, Bedienbarkeit (2026-11-03)

Nichts committet. Tests nur gezielt (keine Vollsuite). Praxisprüfung mit Screenreader (Orca/NVDA) und Skalierung 125–200 % **nicht** durchgeführt.

## Erledigt
| Bereich | Änderung | Dateien |
|---|---|---|
| Import-Grenzen | Dateigröße, Teilezahl, tatsächlich entpackte Größe, Kompressionsverhältnis, XML-Größe, DTD/Entitäten, XML-Tiefe, Bildpunkte; Prüfung vor jeder Verarbeitung | `dienste/import_grenzen.py`, `docx_leser.py`, `odt_leser.py`, `datei_dienst.py`, `editor/objekte/freie_bilder.py` |
| MCP | Zeilen-, Nachrichten-, Ergebnis-, Laufzeitgrenze; Prozessgruppe beenden; Umgebung ohne Zugangsdaten; Rückfrage mit Startbefehl; Aktionsart + volle Argumente je Aufruf | `ki/mcp.py`, `ki/ki.py`, `ki/ki_dienst.py`, `plattform/prozess.py` |
| LanguageTool | nur eigener Prozess auf freiem Port; fremder Dienst nur mit ausdrücklicher Erlaubnis; Status/Identität | `dienste/integrationen/languagetool.py` |
| KI-Datenschutz | Einwilligung je Anbieter und Umfang mit Datum, Widerruf (Reiter „Datenschutz“), Sperre an der Sendestelle, robuste Antwortauswertung, `file://`-Bildadresse abgelehnt, Lücke in `ist_lokale_url` geschlossen | `ki/ki.py`, `ki/ki_dienst.py`, `oberflaeche/dialoge/ki/ki_dialoge.py` |
| Speichern | Stand-Vergleich innerhalb der Sperre (`SchreibKonflikt`) | `dienste/sicher_schreiben.py`, `datei_dienst.py`, `kern/dokument_verwaltung.py`, `oberflaeche/hauptfenster/dateien.py` |
| Fehler gefunden | Verbundene Tabellenzellen gingen beim DOCX-Lesen/Speichern verloren (Spannweite wurde beim Befüllen gelöscht) – behoben | `docx_teile/lesen_tabellen.py` |
| Schichten | beide Ausnahmen entfernt (`kern/piktogramme.py`, Anbieter-Einhängung); Wächter für Betriebssystemaufrufe | `editor/dokument/formular.py`, `editor/dokument/einfuegen.py`, `tests/editor/test_schichten.py` |
| Schreibhilfe | `ProofingIssue` ist Vertrag am Fund-Eingang (`bereinigen`) | `modelle/korrektur.py`, `korrektur/fund.py`, `korrektur_dienst.py` |
| DOCX-Aufbau | Reader/Writer in fachliche Teile (Stile, Tabellen, Seite, Objekte, Zusatz) | `dienste/docx_teile/` |
| Korpus | 9 selbst erzeugte Dokumente, Roundtrip-Vergleich, Bericht | `werkzeuge/pruefungen/docx_korpus.py`, `dokumentation/berichte/docx-korpus-bericht.md` |
| Fehlerprotokoll | drei Fehlerarten, Schwärzung von Schlüsseln/Kennwörtern, Faden-Hook | `plattform/protokoll.py` |
| Formate/Integrationen/Plattform | Verzeichnisse und Dokumentation; `fsync`/Prozesse in `plattform/` | `dienste/formate.py`, `integrationen/verzeichnis.py`, `plattform/dateisystem.py`, `dokumentation/benutzerhandbuch/formate.md`, `dokumentation/entwicklung/plattformen.md` |
| CI | ruff mit festen „echten Fehler“-Regeln, `ruff` in dev; Auswahl für Windows/macOS erweitert (weiter nicht blockierend) | `pyproject.toml`, `.github/workflows/pruefen.yml` |
| Bedienbarkeit | Kachelfeld, Backstage-Liste, Handbuch-Liste, Vorlagenregister, Bandpfeile tastaturbedienbar; Namen für Schrift/Größe/Vorlage/Zoom/„Worum“; Beschreibung der Funktionszeilen; Wächter und Ausnahmeliste | siehe `dokumentation/berichte/pruefbericht-barrierefreiheit-2026-11-03.md` |
| Kontrast | rechnerische Prüfung aller Themen | `werkzeuge/pruefungen/kontrast.py`, `dokumentation/berichte/kontrast-bericht.md` |

## Offen / Einschränkungen
- Kontrast: behoben (Farben leicht angepasst), siehe dokumentation/berichte/kontrast-bericht.md.
- Screenreader-Rollen (`QAccessible`) der selbstgebauten Widgets, Skalierung 125–200 %, Sichtprüfung der Fokusrahmen: nicht geprüft.
- Korpus: nur selbst erzeugte Dokumente; Dokumente aus Word/LibreOffice fehlen (Ordner `tests/korpus_extern/` wird mitgeprüft, sobald vorhanden).
- DOCX-Writer/Reader sind aufgeteilt, die Kernklassen bleiben groß; weitere Schnitte (Absatz/Lauf, Listen) nicht begonnen.
- `ProofingIssue` ist jetzt durchgängig der Typ der Schreibhilfe (Prüfer bis Editor); Dicts nur noch als Brücke für Daten von außen.
- Die ZIP-Prüfung entpackt einmal zum Zählen (Zeitaufwand bei sehr großen Paketen).
- Beobachtet, nicht geändert: `kern/befehle/hauptreiter/seite.py` definiert `seitenraenderRahmen` doppelt; Windows/macOS-CI bleibt nicht blockierend.
- Gesamtlauf (CI) steht aus: lokal nur gezielte Tests.
