# Icon-System — Entwurfsbericht (zur Freigabe)

> **ÜBERHOLT (2026-11-01):** Dieser Bericht beschreibt einen früheren Durchgang, in dem Entwürfe bereits in `symbole.json` eingesetzt wurden. Das widersprach dem Auftrag (erst Freigabe). Die Einsetzung wurde rückgängig gemacht (`symbole.json` = Bestand); alle Entwürfe liegen in `assets/icons/entwurf/symbole-mit-entwuerfen.json`. Maßgeblich ist `icon-auftrag-status.md`.

Stand: 2026-11-01. **Nichts am Programm geändert, nichts integriert.** Ergänzt `icon-konzept.md` (Bestand, Befunde).
Erzeugt mit `.venv/bin/python werkzeug/icon-entwurf.py` → `assets/icons/entwurf/` (31 SVG in `svg/`, Quelle `entwurf.json`,
Kontaktübersichten `kontaktuebersicht-hell.png` / `-dunkel.png`: Entwurf links, heutiges Symbol rechts, 16/20/24/48 px, 1× gerendert = strenger als in der Anwendung).

## 1. Bestand (Kurzfassung)
299 Funktionssymbole (`assets/icons/symbole.json`, Name → ein 24×24-Pfad, Strich 1,5, Lucide/ISC), 1801 Katalogsymbole, Rendering
`ui/widgets/icons.py` (QSvgRenderer, Palettenfarbe, hell/dunkel). Dateityp-Symbole in `assets/icons/filetypes/`. Die Architektur bleibt:
Entwurf nutzt dasselbe Format (ein Pfad, nur Strich), lässt sich also ohne Codeänderung in `symbole.json` tauschen.

## 2. Vergleichsmatrix
**Diese Matrix ist die Kurzfassung aus Allgemeinwissen; die geprüfte Recherche mit Quellen steht in `icon-vergleich.md` (Abschnitt 8 unten fasst zusammen).** Bewertung 1 (schwach) – 3 (stark) für unsere Zwecke.

| Anwendung | Stil | Wiedererkennbarkeit | Unterscheidbarkeit ähnlicher Funktionen | Lesbarkeit 16 px | Detailarmut | Auffällig |
|---|---|---|---|---|---|---|
| Microsoft 365 | farbig, Linie+Fläche | 3 (Diskette, Schere, Pinsel) | 2 (Farbe trägt Bedeutung) | 3 | 2 | Farbe als Unterscheidung → für uns tabu |
| LibreOffice | flach/Linie, je Theme anders | 3 | 2 | 2 | 2 | Themes uneinheitlich |
| Apple iWork / SF Symbols | feine Linie, einheitliches Raster | 3 | 3 | 2 | 3 | sehr dünn, bei 16 px zart |
| Adobe Spectrum | monochrom, klare Silhouette | 2 (Spezialmotive) | 3 | 3 | 3 | Silhouette zuerst |
| Notion | minimal, dünn | 2 | 2 | 2 | 3 | teils abstrakt |

Erkenntnisse: (1) Eingeübte Motive (Diskette, Schere, Lupe, Drucker, Büroklammer) sind am schnellsten verständlich → übernehmen, aber selbst zeichnen.
(2) Ähnliche Funktionen unterscheiden sich in guten Systemen über die **Grundform**, nicht über ein Detail. (3) Dünne Linien (iWork, Notion) verlieren bei 16 px.
(4) Zu abstrakt/missverständlich bei allen: Einstellungen (Zahnrad vs. Regler), PDF (Buchstaben), „Überprüfen“.

## 3. Designkonzept
- Raster 24×24, Strich **1,5**, runde Enden/Ecken, **einfarbig** (Palettenfarbe, hell/dunkel) — Farbe ist nie Bedeutungsträger.
- Ein Motiv + höchstens ein Zusatzzeichen (Plus, Stift, Pfeil). Keine Füllflächen-Kombinationen, kein Comic, keine Schatten.
- Silhouette zuerst: Umriss muss bei 16 px tragen. Bänder (Kopf-/Fußzeile) als eng gesetzte Dreifachlinie = „gefüllt“, ohne Fülltechnik.
- Rand 2–3 Einheiten, sichtbares Gewicht gleich über alle Symbole (Seitenform 16×20, Kreise Ø 18, Pfeile gleiche Strichlänge).
- Jedes Symbol bekommt weiterhin Tooltip/Beschriftung; das Symbol ist nie die einzige Information.

## 4. Prüfergebnis des Entwurfs
Prüfkriterien siehe Auftrag Abschnitt 8. **Nur Sichtprüfung bei 16/20/24/48 px in hell und dunkel plus ein Maß für Pixelüberdeckung bei 16 px; keine Tests mit Menschen.**
Überdeckung = Anteil gemeinsamer Pixel (1 = identisch); Richtwert „prüfen“ ab 0,6. Rahmengleiche Symbole (Seite, Kreis) treiben den Wert künstlich hoch.

| Gruppe | ähnlichstes Paar (Entwurf) | Überdeckung Entwurf | Überdeckung heute | Urteil |
|---|---|---|---|---|
| Ausrichtung | rechts ↔ block | 0,83 | 0,82 | prüfen — Unterschied nur das Zeilenende, bei 16 px schwach (wie heute) |
| Seitenaufbau | kopfz ↔ spalte3 | 0,56 | 0,37 | ok, Kopf-/Fußband bei 16 px aber nur knapp sichtbar |
| Datei | neu ↔ pdf | 0,80 | 0,73 | prüfen — gleiche Seitenform, nur Plus bzw. „P“ |
| Zwischenablage | kopie ↔ kleben | 0,31 | 0,16 | ok |
| Entscheidung | annehmen ↔ ablehnen | 0,70 | 0,05 | Kreis gemeinsam; Haken vs. Kreuz klar, **heutige Symbole (ohne Kreis) trennen besser** |
| Tabelle | tabelle ↔ tabellezeile | 0,43 | — | ok |
| Liste/Verlauf | zurueck ↔ vor | 0,26 | 0,26 | ok |

Beobachtungen aus der Kontaktübersicht:
- Besser als heute: `kopfz/fussz` (Band statt Linie), `kleben` (Klemmbrett mit Zeilen statt leerem Brett), `nachverfolgen` (Seite + Stift), `tabellezeile` (neu, Plus unter Tabelle), `einstellungen` (siehe unten), `punkte` (Punkte größer, bei 16 px sichtbar).
- Gleich gut: Ausrichtung, Datei, Drucken, Schere, Kopie, Lupe, Rückgängig/Wiederholen, Kommentar, Umschlag.
- **Schlechter oder unklar:** `annehmen/ablehnen` mit Kreis (gleiche Umrisse, nur Innenzeichen; heute reiner Haken/Kreuz klarer — Empfehlung: heutigen Stand behalten); `spalte2/spalte3` als Seite mit Trennlinien — bei 16 px lesbar, aber „Seite mit senkrechten Strichen“ lässt sich auch als Tabelle lesen; `kopfz/fussz` bei 16 px nur durch Bandposition unterscheidbar.
- `naechstes`: heutiges Symbol ist ein **Pfeil nach unten** — Name und Bild passen nicht; Entwurf (Winkel nach rechts) ist eindeutiger.

## 5. Möglicherweise missverständliche Symbole
| Symbol | Risiko |
|---|---|
| `einstellungen` (Entwurf: Regler) | Zahnrad ist der übliche Marker; Regler bedeutet bei manchen „Filter/Anpassen“. Entscheidung nötig (Abschnitt 6) |
| `pdf` (Seite mit „P“) | Buchstabe wird bei 16 px zum Fleck; für Menschen mit Legasthenie Buchstaben als Merkmal möglichst vermeiden |
| `neu` ↔ `pdf` ↔ `speichern` | Alle Datei-Symbole; Unterschied klein bei 16 px |
| `rechts` ↔ `block` | nur Zeilenenden |
| `kopfz` ↔ `fussz` | Position des Bands entscheidet |
| `nachverfolgen` | „Änderungen verfolgen“ ist abstrakt; Stift + Seite sagt „bearbeiten“, nicht „nachverfolgen“ |
| `vorlesen` | Lautsprecher wird auch als „Ton/Stumm“ gelesen |
| aus `icon-konzept.md` unverändert: `weLeerModus`, `weNeu`, `weSmart`, `ueberprog`, `assistent`, `automatisch`, `ebenen`, `ecken` | abstrakt, nur mit Tooltip verständlich |

## 6. Entscheidungen, die ich von dir brauche
1. **Stil bestätigen:** Strich 1,5, einfarbig, Motive wie im Entwurf — oder kräftiger (1,75)?
2. **Einstellungen:** Regler (Entwurf) oder Zahnrad (üblich, aber schwer zu zeichnen bei 16 px)?
3. **Annehmen/Ablehnen:** heutiges reines Haken/Kreuz behalten (Empfehlung) oder Kreis-Variante?
4. **PDF:** Buchstabe „P“ behalten oder buchstabenfrei (Seite + Pfeil)?
5. **Umfang nach Freigabe:** nur die ca. 60 am häufigsten genutzten Symbole neu, Rest angleichen (Empfehlung), oder alle 299?
6. **Nutzertest:** echte Tests mit Menschen mit Legasthenie (z. B. 5–8 Personen, Zuordnung „Symbol → Funktion“ ohne Beschriftung) — das kann ich nicht ersetzen; Vorschlag: Testbogen als Markdown erstellen.

Nicht gestartet (erst nach Freigabe): vollständiges Icon-System, Integration in `symbole.json`, Aufräumen ungenutzter Symbole (`kopfhoehe2`, `fusshoehe2`, `drucker2`).

## 7. Umsetzung nach Freigabe (2026-11-01)
Entscheidungen: Empfehlungen übernommen — Strich 1,5, Einstellungen als Regler, Annehmen/Ablehnen unverändert, PDF **buchstabenfrei** (Seite + Pfeil nach unten),
Umfang = die am häufigsten genutzten Symbole.
- In `assets/icons/symbole.json` ersetzt (32) bzw. ergänzt (`tabellezeile`): die 29 Entwurfssymbole aus Abschnitt 4 ohne `annehmen/ablehnen`, dazu neu gezeichnet `pdf`, `zahl` (vorher ein Bildschirm), `assistent` (vorher ein Plus), `raender` (vorher vier Ecken), `ebenen` (Inhaltsverzeichnis mit Seitenzahlen). Code (`icons.py`) unverändert; die Entwürfe in `entwurf/` bleiben als Quelle.
- **Nicht angefasst, weiter zu prüfen:** `farbe`, `bild`, `abstand`, `linie` (zeigt ein Liniendiagramm), `kreis` (Kreisdiagramm), `netz` (Fünfeck), `feld`, `rahmen`, `ausrichtung`, `umbruch`, `smartart`, `wordart`, `ki`, `sprache` — Bedeutung je Verwendungsstelle klären, bevor sie gezeichnet werden. Rest der 299 unverändert (gleicher Strich, gleiche Formensprache).
- `pdf` ↔ `neu` überdecken sich bei 16 px zu 0,84 (gleiche Seitenform); Plus bzw. Pfeil sind die einzigen Unterschiede → im Nutzertest prüfen (`icon-testplan.md`).
- Die Spalte „heute“ der Kontaktübersicht zeigt jetzt dasselbe wie der Entwurf; der alte Stand liegt in Git.

## 8. Gesamtdurchgang aller 300 Symbole (2026-11-01)
Alle Symbole wurden einzeln gesichtet (`assets/icons/uebersicht/alle-hell.png`, `alle-dunkel.png`) und mit `werkzeug/icon-pruefung.py` vermessen
(Ergebnis je Symbol: `icon-qualitaet.md`). Maßstab: Funktion erkennbar, von ähnlichen unterscheidbar, 16 px lesbar, hell/dunkel, gleiche Strichsprache (Strich 1,5, runde Enden — gilt für alle über `icons.py`).
- **Neu gezeichnet insgesamt: ca. 70** (Abschnitte 6/7 plus diese Runde). Diese Runde: `eineSeite` (war ein Doppelpfeil), `ecken`, `anpassen`, `halt`, `fussnote` (war ein Fußabdruck), `endnote`, `notiz`, `inhalt`, `weblayout`, `netz`, `zeilennr`, `zuletzt`, `ausrichtung`, `woerter`, `wellen`, `phonetisch`, `papiergroesse`, `texteffekt`, `tabelleWahl`, `handbuch`, `fensterliste`, `fensterNeben`, `fensterUnter`, `eintrag`, `navigation`, `empfaenger`, `allesmark`, `alleAb`, `aehnlich`, `gehezu`, `leisten`, `kanteKeine`, `tabellenblatt`, `aenderungannehmen/-ablehnen`, `ueberpruefenfenster`, `naechstesfeld`.
- **Behalten** (Sichtprüfung bestanden, Strichstärke einheitlich): übrige Symbole, vor allem Diagramme, Rahmenkanten (`kante*`), Einfügen-Varianten (`einf*`), Absatz/Zeichen-Fenster, Medien, Korrespondenz, Rechtschreibung.
- **Gleiche Zeichnung für gleiche Funktion (gewollt):** `annehmen/haken`, `ablehnen/schliessen`, `kommentarloeschen/kommentarweg`, `hervorheben/marker`, `autokorr/weSmart`, `Duden/woerterbuch`, `einfUnformatiert/ohneformat`, `klappe/trefferRunter`.
- **Bleibt unterscheidungsschwach bei 16 px (Überdeckung ≥ 0,85, verschiedene Funktion):** `tabelle/tabellenblatt`, `ebeneHoch/ebeneTief`, `kanteAlle/kanteAussen`, `Stil/umriss`, `datum/schnelltab`, `kacheln/spalten`, `abspielen/aufnahmeende`, `aufnahme/ueberprog`, `einfInhalte/einfUnformatiert`, `buch/lesen`, `absatzrahmen/kanteInnen`. Hier muss der Tooltip tragen; Nutzertest empfohlen.
- **Weiter abstrakt/missverständlich:** `ueberprog`, `weLeerModus`, `weNeu`, `weSmart`, `weFuehrend`, `trennung`, `silben`, `wasserzeichen`, `vorlesen` (Ton/Stumm), `pdf` (Pfeil = Download?), `einstellungen` (Regler statt Zahnrad), `ebenen` (Inhaltsverzeichnis).
- Geprüft: Kontaktübersichten hell/dunkel bei 16/20/24 px per Sicht, Pixelmaß, Tests `symbole_tauschen`, `programm_symbol`, `kein_html`. **Nicht geprüft:** Verständlichkeit mit Menschen, Darstellung in der laufenden Oberfläche (Band, Dialoge) — Bildvergleich dort steht aus.

## 9. Marktvergleich nachgeholt
Siehe `icon-vergleich.md`: Microsoft-Monoline-Richtlinie, Apple HIG (Tabelle Standardsymbole), Material Symbols, LibreOffice-Themen, Barrierefreiheitsquellen. Folge: `pdf` mit Pfeil nach oben, `einstellungen` wieder Zahnrad (ersetzt Entscheidung 2 aus Abschnitt 6). Offen: 23 zu komplexe Symbole vereinfachen; Bildvergleich in der laufenden Oberfläche; Nutzertest.
