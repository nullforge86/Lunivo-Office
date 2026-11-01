# Icon-System — Befund und Konzeptvorschlag (zur Freigabe)

Stand: 2026-11-01. Status: **Entwurf, nichts am Programm geändert.** Das volle Icon-System entsteht erst nach Freigabe.

## 1. Bestand
- 299 Funktionssymbole in `assets/icons/symbole.json` (Name → 24×24-Pfad), gezeichnet als Strichsymbole aus Lucide (ISC-Lizenz,
  `assets/icons/LIZENZ-LUCIDE.txt`), Katalog mit 1801 weiteren Symbolen in `symbolkatalog.json`.
- Rendering in `src/lunivo_writer/ui/widgets/icons.py` mit Qt (`QSvgRenderer`), Farbe zur Laufzeit, Strichstärke `STRICH = 1.05`.
- Kontaktübersicht des Ist-Stands (16/20/24 px, hell/dunkel): `python3 werkzeug/symbol-uebersicht.py [Ziel.png] [--dunkel]`.

## 2. Befunde aus der Kontaktübersicht
- **Strich zu dünn:** 1,05 px bei 24-px-Raster wird bei 16 und 20 px sehr hell. Das widerspricht „ausreichend starke Linien“.
- **Zu ähnliche Gruppen** (Unterscheidung nur an Details, bei 16 px kaum): `kante*` (Rahmenseiten), `spalte1/2/3`, `ebeneHoch/Tief`,
  `kopfz/fussz/kopfhoehe*`, `weEinzug/weLeerEin/weLeerWeg/…` (Absatz-/Zeilenwechsel), `punkte/zeilennr/gliederung`, `mehr/weniger`.
- **Abstrakte statt konkreter Motive:** z. B. `ueberprog`, `assistent`, `automatisch`, `trefferHoch/Runter`, `ebenen`, `ecken`.
- **Mehrfachbelegung:** `drucker2`, `kopfhoehe2`, `fusshoehe2` neben ihren Gegenstücken — Zweck nicht erkennbar.
- Stärken: einheitliche Formensprache (Strich, runde Enden), kein Comic-Stil, Farbe ist nirgends alleiniges Merkmal.

## 3. Vergleich mit anderen Anwendungen (Einschätzung aus Allgemeinwissen, **keine Live-Recherche, nicht getestet**)
| Anwendung | Stil | Stärke | Schwäche für unsere Zwecke |
|---|---|---|---|
| Microsoft Office | farbig, Fluent, gefüllt/Linie | sehr eingeübte Motive (Schere, Diskette, Pinsel) | viele Details, Farbe trägt Bedeutung |
| LibreOffice | Strich/Flach, mehrere Themes | konkrete Motive | uneinheitlich zwischen Themes |
| Apple iWork | feine Linie (SF Symbols) | konsistentes Raster | dünn, bei kleinen Größen zart |
| Adobe | monochrom, Spectrum | klare Silhouetten | Spezialmotive für Grafik |
| Notion | sehr reduziert, dünn | wenig Details | teils abstrakt |

Folgerung: eingeübte Motive übernehmen (Schere, Lupe, Drucker, Diskette …), Formen aber selbst zeichnen; Strich kräftiger als iWork/Notion.

## 4. Konzeptvorschlag
- Raster 24×24, Strichstärke **1,5 px** (Test bei 16/20/24 px gegen 1,05), runde Enden, ein Motiv + höchstens ein Zusatzzeichen.
- Silhouette zuerst: Symbol muss bei 16 px an der Umrisssilhouette erkennbar bleiben.
- Ähnliche Funktionen bekommen **verschiedene Grundformen**, nicht nur ein anderes Detail (z. B. Kopf-/Fußzeile: Seite mit Balken oben bzw. unten, gefüllt).
- Immer Text-Tooltip/Beschriftung zusätzlich — Symbol allein ist nie die einzige Information.
- Verständlichkeit wird mit einer Prüfliste bewertet (Erkennbar ohne Überlegung? Unterscheidbar? 16 px? Hell/Dunkel?), nicht pauschal behauptet.

## 5. Vorschlag für den ersten Schritt (nach deiner Freigabe)
1. ~~`STRICH` auf 1,5~~ — umgesetzt (2026-11-01), im Vergleich bei 16 px deutlich besser lesbar.
2. Die 8 Problemgruppen aus Abschnitt 2 neu zeichnen (ca. 40 Symbole), Muster-Übersicht zur Abnahme.
3. Erst danach restliche Symbole angleichen.

## 6. Stand der Umsetzung (2026-11-01)
- Strichstärke 1,5 umgesetzt.
- Neu gezeichnet: `kopfz`, `fussz` (Seitenumriss + Trennlinie oben/unten) und `spalte1/2/3` (Seitenumriss + 0/1/2 Trennlinien).
- **Verworfen:** `kante*` als gepunktetes Quadrat mit durchgezogener Seite — bei 16 px zerfallen die Punkte, die Seite geht unter. Alte Symbole bleiben.
- Neu gezeichnet (2. Runde): `weEinzug` (Pfeil an erster Zeile, vorher identisch mit `mehr`/`einzug`), `weLeerEin`/`weLeerWeg` (großes Plus/Minus zwischen zwei Linien).
- **Verworfen:** `ebeneHoch/Tief` als Punkt-Treppe — Punkte zerfallen bei 16 px; die alten Pfeil-Symbole bleiben.
- Offen: `mehr/weniger` (gleich mit `einzug`), übrige `we*`, `punkte/zeilennr/gliederung`, `kopfhoehe2/fusshoehe2`, `drucker2`; mögliche Fehldeutungen sind dort am größten.
- Nicht geprüft: Verständlichkeit mit Menschen (nur Sichtprüfung bei 16/20/24 px, hell/dunkel).
