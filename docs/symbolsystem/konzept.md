# Symbolsystem Lunivo Office — Bestand, Analyse, Konzept, Musterauswahl

Stand: Schritte 1–8 des Arbeitsablaufs. **Das vollständige Symbolsystem ist noch nicht erstellt und nichts ist integriert** — das folgt erst nach Freigabe (Schritt 9 und 10).

## 1. Bestand (gemessen, nicht geschätzt)

Das Hauptfenster wurde unsichtbar gestartet und jede Symbolanforderung mitgeschrieben (`werkzeug`-Skript im Sitzungsordner). Ergebnis: **325 verschiedene Symbole** werden beim Start tatsächlich angefordert, ein Teil davon erst beim Öffnen von Dialogen.

| Quelle | Anzahl | Wo |
|---|---|---|
| Eigene, nach Bedeutung benannte Zeichnungen | 260 | `assets/icons/symbole.json` (322 Namen, Pfaddaten im 24er-Raster) |
| Lucide-Symbole (ISC-Lizenz) direkt verwendet | 65 | `assets/icons/symbolkatalog.json` (1801 Symbole) |
| Nicht auffindbar | 0 | — |

Wiedergabe: `src/lunivo_writer/ui/widgets/icons.py` setzt **genau einen `<path>`** je Symbol in ein SVG im Speicher, Strich `STRICH = 1.05`, runde Enden/Ecken, Farbe aus der Palette (hell/dunkel, deaktiviert grau), `QSvgRenderer`, Zwischenspeicher je (Name, Farbe, Größe). Austausch zur Laufzeit über `uebersteuern()`. `assets/symbole/varianten/` enthält Programm-/Logo-Bilder, keine Oberflächensymbole; `assets/icons/filetypes/` die Dateityp-Symbole.

**Befunde am Bestand**
1. **Strich zu dünn:** 1,05 auf 24 Einheiten sind bei 16 px nur **0,7 px**, bei 20 px 0,9 px. Auf dem Kontaktbogen sind die bisherigen Symbole bei 16 px blass und fransig.
2. **Zwei Stile gemischt:** Lucide (Kontur) und eigene Zeichnungen unterscheiden sich in Flächenfüllung, Eckenradius und Detailgrad.
3. **Mehrdeutige Namen:** `zurueck`/`vor` zeigen heute Rückgängig-/Wiederholen-Pfeile, `ersetzen` ein Rahmenmotiv. Bei der Integration muss je Verwendungsstelle geprüft werden, welche Funktion gemeint ist.
4. **288 der 322 eigenen Namen** werden im Start-Fenster nicht angefordert (Dialoge/Menüs, evtl. ungenutzt) — vor Schritt 9 klären, welche wirklich gebraucht werden.

## 2. Marktanalyse

**Ehrliche Grenze:** Ich konnte die Symbolsätze der Vergleichsprogramme nicht selbst durchblättern. Die Matrix stützt sich auf die veröffentlichten Gestaltungsrichtlinien (Microsoft Fluent, Apple HIG, LibreOffice-Themes) und meine Kenntnis der Oberflächen; Adobe und Notion sind aus dem Gedächtnis eingeordnet und **nicht belegt**. Nichts davon wurde kopiert; es fließen nur Prinzipien ein.

Quellen: [Fluent 2 Iconography](https://fluent2.microsoft.design/iconography), [Windows Iconography](https://learn.microsoft.com/windows/apps/design/iconography/), [Fluent-Symbole, Entwicklerbericht](https://medium.com/microsoft-design/developing-an-open-source-icon-system-at-microsoft-b1796315df9f), [Apple HIG: SF Symbols](https://developer.apple.com/design/human-interface-guidelines/sf-symbols.md), [LibreOffice-Themes (Forum)](https://ask.libreoffice.org/t/change-icon-style-system-wide-linux-on-dark-theme-default-icons-are-mostly-unrecognizable/97282). Für Legasthenie gibt es Richtlinien zu Text (z. B. British Dyslexia Association), **aber keine gefundene Richtlinie speziell für Symbole** — die Anforderungen unten sind daher eigene Ableitungen und müssen getestet werden.

| Programm | Stil | Strich/Gewicht | Stärken | Schwächen für unser Ziel | Beleg |
|---|---|---|---|---|---|
| Microsoft 365 / Windows (Fluent) | Kontur und gefüllt als zwei Varianten, Größen 16–48 einzeln gezeichnet | Windows: 1 epx einstrichig; mobile Sätze ca. 1,5 px | Eine feste Größenstaffel, Zustand über Füllung (aktiv = gefüllt) | Viele sehr ähnliche Dokument-Symbole; Mikrodetails bei 16 px | Richtlinien |
| LibreOffice (Colibre, Breeze, Elementary, Sifr) | Themen wählbar, teils farbig, teils flach | je Thema verschieden | Wahlmöglichkeit, Dunkelvariante bei Breeze | Uneinheitlich zwischen Modulen; Farbe trägt Bedeutung | Forum/Fehlerberichte |
| Apple iWork / SF Symbols | Kontur, 9 Gewichte, passend zur Schrift | an Textgewicht gekoppelt | Einheitlicher Strich, Standardsymbole für Standardaktionen | Teils abstrakt (Teilen, Inspektor) | HIG |
| Adobe (Spectrum / Creative Cloud) | Kontur, sehr reduziert | nicht belegt | Sehr klare Formen | Viele abstrakte Werkzeugsymbole | nicht belegt |
| Notion | Minimal, Kontur, wenig Detail | nicht belegt | Wenige Elemente, gut lesbar | Wenig Fachfunktionen; Text trägt viel | nicht belegt |

**Erkenntnisse**
- **Verständlich auf einen Blick:** Standardmetaphern, die seit Jahrzehnten gleich sind (Diskette, Drucker, Lupe, Schere, Zahnrad, Absatzausrichtung als Zeilen, Pfeile für Rückgängig). Hier nicht neu erfinden.
- **Gut unterscheidbar:** Grundobjekt + **ein** Zusatz (Plus, Kreuz, Pfeil). Die Position des Zusatzes trägt die Bedeutung (Tabelle + Plus *oben* ≠ *unten*).
- **Professionell/zeitgemäß:** einheitlicher Strich, gleicher Eckenradius, Ränder im Raster, kein Mischstil.
- **Zu abstrakt/missverständlich:** Teilen, „Inspektor“, Ebenen/Formatvorlagen, Mischungen aus zwei Objekten.
- **Klein lesbar:** wenige, kräftige Linien, Abstand zwischen Linien ≥ 2 Einheiten, Details nicht kleiner als der Strich.

## 3. Designkonzept „Lunivo Klar“

| Eigenschaft | Festlegung | Begründung |
|---|---|---|
| Raster | 24 × 24, Zeichenfläche 3–21, Ränder 2–3 | wie bisher, bestehende Pfadformate bleiben gültig |
| Strich | **1,25** (bisher 1,05; 1,6 war dem Eigentümer zu fett) → 0,83 px bei 16, 1,04 bei 20, 1,25 bei 24 px | Kompromiss: etwas kräftiger als zuvor, aber nicht schwer |
| Enden/Ecken | rund, Ecken von Behältern Radius 1,5 | freundlich-sachlich, einheitlich |
| Aufbau | **Grundobjekt + höchstens ein Zusatz**, Zusatz in einer Ecke bzw. an der Position seiner Wirkung | Funktionen unterscheiden sich durch Zusatz, nicht durch Detail |
| Farbe | einfarbig; Farbe nur aus der Palette (hell/dunkel/deaktiviert). Farbstriche (Schriftfarbe, Marker) sind zusätzlich als **Form** (Balken) vorhanden | Farbe nie einziges Merkmal |
| Buchstaben | nur wo sie die Funktion *sind* (B, I, U, A). Keine Buchstaben in anderen Symbolen (z. B. kein „PDF“) | Buchstabenverwechslung vermeiden |
| Ziffern | höchstens zwei Zeilen (1, 2) | dritte Ziffer war bei 16 px nicht lesbar |
| Verboten | Füllungen, Schatten, Verläufe, Comic-Formen | Vorgabe |
| Technik | weiterhin **ein einziger `<path>`**, kompatibel zu `symbole.json` und `_svg()`; nur `STRICH` ändert sich | Architektur bleibt erhalten |

## 4. Musterauswahl und Prüfung

48 Symbole in 8 Bereichen: `assets/icons/entwurf/*.svg` (Quelle der Pfade: `entwurf.json`). Absichtlich enthalten sind **die Paare, die sich leicht verwechseln lassen**: Zeile oben/unten einfügen, Zeile löschen, Verbinden/Teilen, Annehmen/Ablehnen, Rückgängig/Wiederholen, Einzug mehr/weniger, vier Ausrichtungen.

Bilder (Entwurf links, bisher rechts; 72 px sowie 16, 20, 24 px ohne Hochskalierung):
- [kontaktbogen-hell.png](kontaktbogen-hell.png)
- [kontaktbogen-dunkel.png](kontaktbogen-dunkel.png)

Erzeugt mit `.venv/bin/python werkzeug/symbol-kontaktbogen.py` (QPainter, kein HTML).

**Gemessen** (16 px, Entwurf gegen bisher, alle Symbole der Auswahl mit Gegenstück):
- Mittlere Tintenmenge: 0,19 gegenüber 0,13.
- Anteil kräftiger Pixel: 0,21 gegenüber 0,11 — fast doppelt so viele Pixel sind klar gesetzt.
- Ähnlichkeit (Kosinus der 16-px-Bilder, 1,0 = identisch). Ähnlichste Paare Entwurf: Neu/PDF 0,94; Ausrichtung zentriert/Blocksatz 0,92; Ausrichtung/Einzug 0,91. Bisher: Zeile oben/Zeile löschen 0,98; Neu/Annehmen/Ablehnen 0,96; Verbinden/Teilen 0,95. Der Entwurf ist in den kritischen Paaren deutlicher abgesetzt, aber **alle zehn ähnlichsten Paare liegen über 0,9** — die Ausrichtungssymbole sind bauartbedingt ähnlich.

**Ausdrücklich nicht geprüft:** Verständlichkeit durch echte Menschen, auch nicht durch Menschen mit Legasthenie. Die Zahlen belegen Lesbarkeit und Unterscheidbarkeit der Pixelbilder, nicht Verständnis. Vorschlag für den Test (kann Kay oder jemand aus dem Umfeld durchführen): 20 Symbole ohne Beschriftung zeigen, Funktion benennen lassen (Trefferquote und Zeit), danach Paarungs-Test mit den unten gelisteten Verwechslungskandidaten; Ziel ≥ 90 % richtig bei Standardsymbolen.

## 5. Liste möglicherweise missverständlicher Symbole

| Symbol | Risiko | Gegenmaßnahme |
|---|---|---|
| Neu / PDF | Seite + Zusatz, ähnlich (0,94) | Tooltip + Text im Menü; Zusatz bleibt Plus vs. Pfeil mit Grundlinie |
| Text-Ausrichtung (4) | nur Zeilenlänge unterscheidet | Konvention, überall gleiche Reihenfolge; Tooltip |
| Einzug mehr / weniger | nur Pfeilrichtung | Gruppe bleibt zusammen, Pfeilspitze deutlich |
| Zeile oben / unten einfügen | Position des Plus ist der einzige Unterschied | Test mit Beschriftung; Plus bewusst außerhalb der Tabelle |
| Zeile löschen | Kreuz neben der Tabelle statt Mülleimer | im Test prüfen; Rückfall: Mülleimer-Zusatz |
| Verbinden / Teilen | Pfeile zueinander / voneinander + Mittellinie nur bei Teilen | Mittellinie ist der feste Unterschied |
| Nachverfolgen | Stift + Zeilen, ähnlich „Bearbeiten“ | Test; evtl. eigener Zusatz |
| Ersetzen | Wechselpfeile bedeuten sonst „Umschalten/Tauschen“ | Tooltip „Ersetzen“; im Test prüfen |
| Nummerierte Liste | nur zwei Ziffern | bewusst so gewählt |
| Vorlage | Seite mit Kopfblock, könnte „Dokument“ heißen | im Test prüfen |
| Rechtschreibung | Zeilen + Haken ähnlich „Annehmen“ | Zeilen bleiben tragendes Merkmal |

## 6. Offene Entscheidungen für die Freigabe

1. **Strichstärke 1,6** und der etwas kräftigere Gesamteindruck — freigeben oder anpassen?
2. **Bedeutung von `zurueck`/`vor`/`ersetzen`:** In der Auswahl sind sie Navigationspfeile (zurück/vor) und Austausch; die bisherigen Symbole sahen nach Rückgängig/Wiederholen bzw. anderem Motiv aus. Welche Funktion ist je Stelle gemeint? Das lege ich vor der Integration anhand der Aufrufstellen fest.
3. **Umfang Schritt 9:** nur die 260 eigenen Zeichnungen, die Lucide-Symbole mit (65) oder auch die ungenutzten (288 im Startfenster nicht angefordert)? Empfehlung: erst die tatsächlich angeforderten 325.
4. **Test mit Menschen** vor oder nach der Vollversion?

## 7. Integration (Stand nach Stufe 2)

**Strich:** Nach Rückmeldung des Eigentümers („zu fett, die alte war besser“) steht `STRICH` in `src/lunivo_writer/ui/widgets/icons.py` auf **1,25** statt 1,6. Der Wert ist eine einzige Zahl; 1,05 stellt den alten Zustand wieder her. Die Bögen in `docs/symbolsystem/` sind mit 1,25 gezeichnet (Entwurf) gegen 1,05 (bisher).

**Neu gezeichnet: 128 von 325** (Stufe 3: Serienbrief, Diagramme, Listen, Hyperlink, Vorschau, Export u. a., Funktion jeweils an der Beschriftung der Aufrufstelle geprüft) angeforderten Symbolen (Quelle: `assets/icons/entwurf/`, eingebaut in `assets/icons/symbole.json`). Stufe 2 brachte Text/Farbe, Datei, Kommentar, Tabelle, Seite und Spalten. Etliche Namen sind Verweise auf ein bereits gezeichnetes Symbol (z. B. `save` → `speichern`), damit gleiche Funktionen gleich aussehen.

**Bewusst nicht ersetzt**, weil das bisherige Symbol eine andere Funktion zeigt als meine Annahme: `naechstes`/`voriges` (Pfeil auf/ab), `eineSeite` (Ansicht „ganze Seite“), `kreis` (Kreisdiagramm), `kopfz`/`fussz`/`kopffuss`. Lehre: vor dem Neuzeichnen jeden Namen an der Aufrufstelle klären.

**Offen:** 197 Symbole behalten bewusst ihre Zeichnung, jetzt mit Strich 1,25. Das sind einfache Lucide-Symbole (Pfeile, Plus, Minus, Kreuz, Menü, Zahnräder u. ä.), Symbole, deren bisheriges Bild die Funktion schon gut zeigt (z. B. Datensatz-Pfeile, Datum/Uhrzeit, Textmarke, KI-Funken), und solche ohne erkennbare Beschriftung an der Aufrufstelle (`weLeer*`, `kante*`, `initiale`, `tafel` u. a.). In Stufe 3 zusätzlich zurückgenommen, weil das bisherige Bild die Funktion besser trifft: `seriefeld` (Klammern), `stift` (Füllfederhalter), `kurs` (Kursdiagramm). Wer diese Gruppen vereinheitlichen will, braucht für die Namen ohne Beschriftung erst die Bedeutung vom Eigentümer.

**Geprüft:** Hauptfenster zeichnet unsichtbar mit den neuen Symbolen; Wächtertest `test_kein_html_im_projekt` grün. **Nicht geprüft:** Dunkelmodus der neuen Symbole im Programm, Dialoge und Menüs, Verständlichkeit mit Menschen.

**Prüfung im Programm (Dunkelmodus, unsichtbar gestartet, Bildschirmfotos angesehen):** Band-Reiter Start, Seitenlayout und Tabellentools, die Datei-Ansicht und der Absatz-Dialog zeigen die neuen Symbole in hellen Farben gut erkennbar; deaktivierte Symbole sind grau, aber noch zu erkennen. Beim Ausprobieren fiel auf, dass im Reiter „Seitenlayout“ „Seitenränder“ das Symbol des Seitenrahmens trägt — das ist keine Folge der Umstellung, die Zuordnung war schon vorher so.
Nicht angesehen: alle übrigen Reiter, Klappmenüs und Dialoge einzeln; 609 von 865 Menüeinträgen haben bewusst oder bisher kein Symbol (nicht mit dem Stand davor verglichen).
