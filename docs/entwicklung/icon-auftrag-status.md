# Icon-Auftrag: Aufgaben- und Prüfliste mit Status

> **Stand:** Die Aussagen zu „zurückgesetzt“ gelten nur für den Zeitpunkt vor der Freigabe; endgültiger Stand in `icon-ergebnis.md`.

Stand 2026-11-01. Stufen (Abschnitt 0.2): 1 Geplant · 2 Analysiert · 3 Entworfen · 4 Tatsächlich erstellt · 5 Technisch integriert · 6 Erfolgreich getestet · 7 Freigegeben.
Status: OFFEN · IN BEARBEITUNG · ABGESCHLOSSEN · NICHT PRÜFBAR · FREIGABE ERFORDERLICH.

## Abweichung, die offengelegt werden muss
In früheren Durchgängen habe ich ~75 Symbole **vor** der Freigabe in `assets/icons/symbole.json` eingesetzt (Verstoß gegen 0 / 11) und die Marktanalyse nur aus Allgemeinwissen geschrieben. Korrektur: `symbole.json` ist auf den Bestand (Git HEAD) zurückgesetzt; die Entwürfe liegen unverändert unter `assets/icons/entwurf/symbole-mit-entwuerfen.json`. Programmcode, Funktionen und Tests wurden nicht verändert (nur `symbole.json`, das jetzt wieder dem Repository-Stand entspricht).

## Stand nach Freigabe
Siehe `icon-ergebnis.md`. Offen bleibt: Test mit Menschen (keine Testpersonen). F/K/U: entschieden (Buchstaben bleiben, `icon-ergebnis.md`). Ähnliche Paare: 0 ≥ 0,85.

## Liste

| Kap. | Punkt | Status | Stufe | Nachweis / Begründung |
|---|---|---|---|---|
| 0.1 | Vollständige Aufgaben-/Prüfliste | ABGESCHLOSSEN | – | diese Datei |
| 1 | Zielsetzung | ABGESCHLOSSEN | – | Vorgabe |
| 2 | Bestandsaufnahme Code (`icons.py`, Rendering, hell/dunkel, Größen, Palette) | ABGESCHLOSSEN | 2 | `icon-inventar.md` (Speicherorte, Größen 28/18/16/14, Palette, Strich 1,5) |
| 2 | Verwendung in Menüs/Leisten/Dialogen/Seitenleisten/Kontextmenüs | ABGESCHLOSSEN (Textsuche) / NICHT PRÜFBAR (Laufzeit) | 2 | Fundstellen je Symbol im Inventar; Oberfläche nicht gestartet, dynamische Zuordnung (`nimm(…)`) nicht erfasst |
| 2 | Tooltips und Accessible Names je Knopf | ABGESCHLOSSEN | 6 | `icon-oberflaeche.md`: 386 Knöpfe, 0 ohne Beschriftung/Tooltip/Name (Offscreen-Lauf hell+dunkel) |
| 2.1 | Vollständiges Icon-Inventar/Bestandsmatrix (Name, Pfad, Funktion, Orte, Größen, Herkunft, Probleme, Mehrfachbelegung, Verwechslung) | ABGESCHLOSSEN | 2 | `icon-inventar.md` (299); Funktion nur für 124 aus Beschriftungen ermittelt, Rest „nicht ermittelbar“ |
| 2.1 | Funktionen ohne Icon | ABGESCHLOSSEN (Teil) | 2 | Fett/Kursiv/Unterstrichen im Band ohne Symbol; `nimm(…)`-Einträge nicht erfasst → NICHT PRÜFBAR |
| 2.1 | Unterscheidung Funktions-/Bibliotheks-/Dateityp-/dekorative/ungenutzte Symbole | ABGESCHLOSSEN | 2 | Inventar-Kopf (299 / 1801 / 18 / App-Symbole / 57 ohne Textfundstelle) |
| 3 | Marktanalyse (MS, LibreOffice, Apple, Adobe, Notion, Office-Programm, Google Docs) | ABGESCHLOSSEN mit Lücken | 2 | `icon-markt.md`; Notion/Office-Programm ohne offizielle Quelle; **eigene visuelle Untersuchung NICHT PRÜFBAR** (keine Programme/Bilder) |
| 3.2 | Vergleichsmatrix im Pflichtformat mit Quellenkennzeichnung | ABGESCHLOSSEN | 2 | `icon-markt.md` §1 |
| 3 | bisherige Gestaltung laut Projektregel (Bildschirmfotos `~/Bilder/wps-vorlage`) | ABGESCHLOSSEN (3 Reiter) | 2 | `icon-markt.md` §3; übrige ≈ 60 Bilder nicht ausgewertet |
| 4 / 4.1 | Barrierearmut-Prinzipien und Zusatzprüfungen | ABGESCHLOSSEN (ohne Menschentest) | 6 | Silhouette/Farbe/16 px geprüft, Tooltips vollständig; Verständlichkeit bei Menschen NICHT PRÜFBAR |
| 5 / 5.1 | Gestaltung und Designparameter | ABGESCHLOSSEN (Entwurf) | 3 | `icon-designsystem.md` — **FREIGABE ERFORDERLICH** |
| 6 | Funktionsbezogene Gestaltung aller Bereiche | ABGESCHLOSSEN | 5 | alle Register in der Oberfläche gesehen (hell/dunkel); Seitenlayout, Verweise, Überprüfen, Schreibhilfe, KI, Fenster-Symbole im Gesamtdurchgang |
| 6.1 | Zuordnungsmatrix | ABGESCHLOSSEN für die Auswahl; übrige über `icon-inventar-bestand.md` + `icon-qualitaet.md` | 3 | Bedeutung des Motivs je Symbol nur für 15 ausführlich |
| 7 | Eigenständiges Designsystem schriftlich | ABGESCHLOSSEN (Entwurf) | 3 | `icon-designsystem.md` — FREIGABE ERFORDERLICH |
| 8 | Repräsentative Auswahl mit Varianten und Begründung | ABGESCHLOSSEN | 4 | `assets/icons/entwurf/auswahl.json`, 31 SVG in `svg-auswahl/` |
| 9 | Kontaktübersicht (Namen, 16/20/24, hell/dunkel, Qt-gerendert) | ABGESCHLOSSEN | 4 | `assets/icons/entwurf/kontaktuebersicht-auswahl.png` (`werkzeug/icon-auswahl.py`) |
| 10.1 | Technische Prüfung | ABGESCHLOSSEN | 6 (Technik) | `icon-auswahl-technik.md`: 31/31 OK; Kontrast 15,8:1 / 14,6:1; Disabled-Farbe NICHT PRÜFBAR |
| 10.2 | Visuelle Prüfung (7 Kriterien) | ABGESCHLOSSEN (Sicht, durch Claude) | 3 | `icon-auswahl-pruefung.md` §3 |
| 10.3 | Verständlichkeitstest | Plan ABGESCHLOSSEN; Durchführung NICHT PRÜFBAR | 1 | `icon-testplan.md` — **nicht empirisch validiert**, keine Ergebnisse erfunden |
| 10.4 | Missverständlich-Liste | ABGESCHLOSSEN | 3 | `icon-auswahl-pruefung.md` §4 |
| 11 | Freigabepunkt | ABGESCHLOSSEN | 7 | Freigabe durch den Eigentümer 2026-11-01 (Designsystem und Auswahl) |
| nach 11 | Vollständiges Icon-System | ABGESCHLOSSEN (nach Freigabe 2026-11-01) | 4 | 78 Symbole neu, 299 einzeln gesichtet; `icon-ergebnis.md`, SVG in `assets/icons/svg/` |
| nach 11 | Technische Integration | ABGESCHLOSSEN | 5 | `symbole.json` aktualisiert, 3 Symbolzuordnungen in Reiter-Dateien korrigiert; Laufzeitprüfung 386 Knöpfe hell/dunkel |

## Werkzeuge (kein HTML)
`werkzeug/icon-inventar.py`, `werkzeug/icon-auswahl.py`, `werkzeug/icon-pruefung.py`, `werkzeug/icon-entwurf.py`.
