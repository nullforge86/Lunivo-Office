# Icon-System — Markt- und Wettbewerbsanalyse (Phase 3)

Stand 2026-11-01. Basis je Aussage: **[O]** offizielle Dokumentation (gelesen, Link unten) · **[V]** eigene visuelle Untersuchung der Oberfläche (**nicht durchgeführt**: keine Programme/Bildschirmfotos verfügbar) · **[E]** begründete Einschätzung aus Allgemeinwissen (nicht geprüft).
Keine Icon-Dateien fremder Programme kopiert oder eingebaut.

## 1. Vergleichsmatrix

| Anwendung | Bildsprache | Linienführung | Detailgrad | Kleine Größen | Verständlichkeit | Stärken | Schwächen | Erkenntnisse für Lunivo |
|---|---|---|---|---|---|---|---|---|
| Microsoft 365 / Office („Monoline“, Fluent 2) | schlicht, Windows-nah; Fluent: Stile Regular (Orientierung) und Filled (ausgewählt) [O]; Icons als wörtliche Metaphern, nach der Form benannt („Shield“ statt „Security“) [O] | Strich 1 px bei 16–32 px, 2 px bei 40–80, 3 px bei 96; Kantenlücke gleich Strichbreite [O] | höchstens 2 Elemente (Basis + Modifier); Text in Icons meiden [O] | Pflichtgrößen 16/20/32 px; Randabstand 0–1 px bei 16–24 [O]; unter 48 px vereinfachen [O] | Regel „gleiches Konzept = gleiches Element“ (Post immer Umschlag) [O]; Verständlichkeit selbst: [E] hoch durch Gewöhnung | klare Bauregeln, Zusatzzeichen unten rechts, wenig Farbe (nur eine Zusatzfarbe) [O] | Strich 1 px sehr dünn für unser Ziel [E]; Farbe teils bedeutungstragend (Monoline-Palette) [O] | Bauregeln („Basis + Modifier“, ≤ 2 Elemente, wörtliche Metaphern) übernehmen; Strich kräftiger; Farbe nie Träger |
| LibreOffice (Writer) | mehrere Themen (Colibre, Elementary, Breeze, Sifr, Karasa Jaga, Tango), je Plattform [O, Forum]; Colibre = Windows-Stil, Breeze = KDE, Elementary/Sifr = GNOME [O, Forum] | je Thema unterschiedlich [E] | je Thema unterschiedlich [E] | Breeze/Sifr mit Dunkelvariante, Colibre ohne [O, Fehlerbericht] | Befehle sind benannt (`alignleft`, `accepttrackedchange` …) [O, Repository] — Motive je Thema uneinheitlich [E] | Auswahl pro Plattform, Hochkontrast über Sifr [O] | Uneinheitlichkeit zwischen Themen, fehlende Symbole als Fehler gemeldet [O] | **ein** Thema für alles; Hell/Dunkel über Palettenfarbe statt zweiter Symbolsatz |
| Apple iWork (Pages/Numbers/Keynote) | SF Symbols für Standardaktionen (Schere, zwei Dokumente, Dokument-auf-Klemmbrett, Bogenpfeile, Drucker, Lupe …) [O, HIG-Tabelle]; ob iWork selbst genau diese nutzt: [E] | Strich an Schriftgewicht gekoppelt, einheitlich über alle Symbole [O] | „stark vereinfacht“, Text nur wenn nötig, Absatztext als abstrakte Zeilen [O] | Symbole richten sich an Schriftgrößen aus; Randausgleich (optisch zentrieren) [O] | vertraute Metaphern, direkt zur Aktion [O] | konsistentes Raster, Alternativtexte Pflicht (VoiceOver) [O] | Strich sehr fein in leichten Gewichten [E] | Standardmetaphern direkt übernehmen (siehe `icon-vergleich.md`), Alternativtexte (Accessible Names) sicherstellen |
| Adobe (Spectrum) | Workflow-Icons, plattformweit gleiche Größe je Plattform [O] | Desktop 1 oder 2 px, mobil 1,5 oder 2 px; dünner Strich für waagerechte/senkrechte Linien üblich, 2 px wo mehr Gewicht nötig; Desktop auf ganze Pixel gerastert [O] | konsistente Eckenradien und Proportionen je Größe [O] | je Größe eigene Zeichnung statt bloßer Skalierung [O] | Spezialmotive für Grafik [E] | Strichstärken-Regel, Pixelraster [O] | viele Spezialsymbole, wenig Textverarbeitung [E] | 1,5 px liegt im Bereich der Adobe-Mobil-Werte; Pixelraster als Prüfziel |
| Notion | minimalistisch, dünn [E]; **keine offizielle Quelle gefunden** (nur Drittanbieter-Packs/Fan-Seiten) | [E] | [E] | [E] | teils abstrakt [E] | wenig Details [E] | dünn, teils abstrakt [E] | **NICHT PRÜFBAR** (keine belastbare Quelle) — nur als Gegenbeispiel „zu dünn/abstrakt“ geführt, ohne Beleg |
| WPS Office | Office-nahes Aussehen [E]; Versionshinweise nennen „einheitlichen visuellen Stil“ der Oberflächen [O, Changelog], aber keine Icon-Details | [E] | [E] | [E] | [E] | wiedererkennbar für Office-Umsteiger [E] | keine Dokumentation zu Icons gefunden [O-Lücke] | Aussehens-Vorbild nur über Kays Bildschirmfotos (`~/Bilder/wps-vorlage`), **hier nicht ausgewertet** (kein Zugriff in dieser Sitzung) — FREIGABE/EINGABE ERFORDERLICH |
| Google Docs (Material Symbols) | Material Symbols (Outlined/Rounded/Sharp); Docs-Werkzeugleiste nach Material Design 3 überarbeitet [O, Presse] | Gewicht 100–700, normal 400; 24-px-Entwurf, 20 und 24 px pixelgenau [O] | Füllung als Zustandsachse (0–100) [O] | optische Größe 20–48 px [O] | Standardmetaphern [E] | Variable Schrift: Gewicht, Füllung, Grad (−50 für helle Symbole auf dunkel) [O] | Docs-Symbole selbst: kein offizielles Dokument gefunden [O-Lücke] | Dunkel-Ausgleich (Grad) entspricht unserem minimalen Strichausgleich in `icons.py`; Zustand über Füllung als Option |

## 2. Querschnitt zu den geforderten Eigenschaften (3.1)

| Frage | Befund | Basis |
|---|---|---|
| Wie werden vergleichbare Funktionen dargestellt? | siehe `icon-vergleich.md` §2 (Schere, zwei Blätter, Klemmbrett, Bogenpfeile, Drucker, Lupe, Zeilenstapel für Ausrichtung) | Apple [O], übrige [E] |
| Schnell verständliche Symbole | solche mit wörtlicher Alltagsform: Schere, Drucker, Lupe, Umschlag, Papierkorb [O Apple/MS], Klemmbrett | [O]/[E] |
| Leicht unterscheidbar | verschiedene Grundformen statt Detailunterschied; MS: nur 2 Elemente | [O] |
| Professionell/zeitgemäß | einfarbige Linie, ruhiger Strich, keine Verläufe/Schatten (MS: flache Farben, keine Verläufe) | [O] |
| Zu abstrakt/missverständlich | Einstellungen (Zahnrad gelernt), PDF (Buchstaben), „Überprüfen“ | [E] |
| Kleine Größen | MS: vereinfachen < 48 px; Adobe: eigene Zeichnung je Größe; Apple: Details reduzieren bei kleinen Dokument-Icons | [O] |
| Liniengewichte | MS 1 px; Adobe 1/1,5/2 px; Material 400 ≈ 2 px bei 24; Apple = Schriftgewicht; **Lunivo 1,5 px** | [O] |
| Zustände aktiv/inaktiv/ausgewählt | Apple: ausgewählt = Akzentfarbe; Fluent: ausgewählt = Filled-Stil; Material: Füllachse; Lunivo heute: Disabled-Palettenfarbe (grau), Auswahl über Knopfhintergrund des Programms (nicht geprüft) | [O] / Lunivo [E] |
| Hell/dunkel | LibreOffice: Sifr/Breeze mit Dunkelvariante; Material: Grad −50; Lunivo: eine Zeichnung, Palettenfarbe | [O] |
| Komplexe Funktionen vereinfachen | Basis + Modifier (MS), Abstraktzeilen (Apple), Details je Größe weglassen (Adobe/Fluent) | [O] |

## 3. Eigene visuelle Untersuchung (WPS-Vorlage, Bildschirmfotos `~/Bilder/wps-vorlage`)
Ausgewertet: `01-reiter-start.png`, `03-reiter-seitenlayout.png`, `05-reiter-ueberpruefen.png` (nur Aussehens-Vorbild, nichts übernommen). [V]
- **Linie:** sehr dünn (≈ 1 px), grau, viele Kleinsymbole 16 px; Hervorhebung nur durch Hintergrund (aktiver Knopf), deaktiviert = hellgrau (Ausschneiden, Löschen, Textfluss).
- **Motive:** Schere/zwei Blätter/Klemmbrett/Pinsel/Drucker/Lupe wie Apple/Office; **B / I / U als Buchstaben** (Fett, Kursiv, Unterstrichen); Zahnrad für Einstellungen (oben rechts); Lupe für Suchen; „Wörter zählen“ = Zeilen + Zählfeld; „Genko-Einstellung“ = Seite mit Kästchenraster; „Vorherige/Weiter“ = Blase mit Pfeil (nicht Rückgängig-Pfeil); Annehmen/Ablehnen = Seite mit Haken/Kreuz.
- **Folgen für Lunivo (umgesetzt):** Genko jetzt Raster (`kacheln`), „Vorherige/Weiter“ im Reiter Überprüfen nicht mehr mit Rückgängig/Wiederholen-Symbol, Annehmen/Ablehnen als Seite mit Haken/Kreuz, Zahnrad. **Abweichung:** Lunivo-Strich 1,5 statt ≈ 1 (Auftrag: starke Linien); Fett/Kursiv/Unterstrichen bleiben Buchstabenknöpfe (F, K, U) wie im Bestand — Programmcode wird nicht geändert.
- Nicht ausgewertet: übrige Bilder des Ordners (Dropdowns/Dialoge, ≈ 60 Dateien) — nur Reiter Start, Seitenlayout, Überprüfen geprüft.

## 4. Offene Icon-Projekte im direkten Funktionsvergleich (eigene visuelle Untersuchung)
Basis **[V]**: 6 Projekte, 30 Funktionen, 178 von 180 Symbolen geladen und mit Qt neben die Lunivo-Symbole gerendert (`werkzeug/icon-vergleich-extern.py`; Fremdsymbole werden nur in einen Temp-Ordner geladen, nicht im Projekt gespeichert, nichts übernommen).

| Projekt | Lizenz | Stil | Linie |
|---|---|---|---|
| [Tabler Icons](https://github.com/tabler/tabler-icons) | MIT | Linie, rund | 2 px bei 24 |
| [Phosphor](https://github.com/phosphor-icons/core) | MIT | Linie (Regular), viele Stile | ≈ 1,5 px |
| [Bootstrap Icons](https://github.com/twbs/icons) | MIT | gefüllt/Kontur, 16-px-Raster | ≈ 1 px |
| [Fluent UI System Icons](https://github.com/microsoft/fluentui-system-icons) | MIT | Regular/Filled | ≈ 1,5 px |
| [Material Symbols](https://github.com/google/material-design-icons) | Apache-2.0 | variabel, hier Outlined | ≈ 2 px |
| [KDE Breeze](https://github.com/KDE/breeze-icons) | LGPL-3.0 | 22 px, dünn, grau | ≈ 1 px |
| Lunivo (jetzt) | eigene Zeichnung | Linie, rund | 1,5 px |

Ergebnis je Funktion (Konsens = mindestens 4 von 6 Projekten zeigen dasselbe Motiv):

| Funktion | Konsens der Projekte | Lunivo | Befund |
|---|---|---|---|
| Speichern, Öffnen, Neu, Drucken | Diskette, offener Ordner, Seite+Plus, Drucker | gleich | in Ordnung |
| Ausschneiden, Kopieren, Einfügen | Schere, zwei Blätter, Klemmbrett | gleich | in Ordnung |
| Rückgängig/Wiederholen | gebogener Pfeil links/rechts (Phosphor/Bootstrap als Kreispfeil) | gebogener Pfeil | in Ordnung |
| Suchen | Lupe | Lupe (ohne Plus) | in Ordnung (vorher mit Plus = Zoom) |
| Ersetzen | zwei Pfeile gegenläufig (Tabler/Bootstrap/Fluent), Lupe+Pfeile (Material/Breeze) | zwei Pfeile gegenläufig | in Ordnung |
| Ausrichtung links/Mitte/rechts/Block | Zeilenstapel, Länge der Zeilen | gleich | in Ordnung |
| Aufzählung/Nummerierung | Punkte bzw. Ziffern vor Zeilen | gleich | in Ordnung |
| Tabelle | Raster | Raster | in Ordnung |
| Zeile/Spalte einfügen | Tabellenausschnitt + Plus am Rand | Zeile ja; **Spalte fehlte** | `tabellespalte` ergänzt |
| Kommentar | Sprechblase mit Zeilen oder Plus | Blase + Plus | in Ordnung |
| Einstellungen | Zahnrad (5 von 6; Breeze: Regler) | Zahnrad (acht Zähne, eigene Zeichnung) | angepasst — vorher Zahnrad-Feld (wirkte wie Fadenkreuz), nicht marktüblich |
| Link, Bild, Rechtschreibung | Kette, Bild mit Berg/Sonne, A/ABC mit Haken | gleich | in Ordnung |
| Seitenspalten | senkrechte Streifen | Seite mit Teilung | in Ordnung |
| Exportieren/Teilen | Pfeil nach oben aus Kasten (4 von 6), Seite+Pfeil (Breeze) | Seite + Pfeil heraus | beide Konventionen vorhanden; Lunivo folgt Breeze |
| Markieren | Textmarkerstift | Stift | in Ordnung |
| Löschen | **Papierkorb (alle 6)** | kein Papierkorb im Satz (nur Radierer = Formatierung löschen) | `loeschen` (Papierkorb) ergänzt, noch ohne Verwendung |

Weitere Beobachtungen: Dicke Linien (Material, Tabler 2 px) sind bei 16 px am besten lesbar; Bootstrap/Breeze (≈ 1 px) sind es am wenigsten — Lunivo (1,5) liegt in der Mitte und bleibt. Kein Projekt nutzt Farbe zur Unterscheidung außer Breeze (graue Akzente). Buchstabensymbole nutzen nur Rechtschreibung (A/ABC) und Textmarker (T bei Breeze).

## 5. Lücken (ehrlich)
Notion und WPS: keine offizielle Quelle gefunden. Adobe-18-px-Angabe stammt nur aus einer Drittseite und wird **nicht** verwendet. Eigene visuelle Untersuchung der Programme: nicht möglich in dieser Sitzung.

## Quellen
[MS Monoline](https://learn.microsoft.com/en-us/office/dev/add-ins/design/add-in-icons) · [Fluent 2 Iconography](https://fluent2.microsoft.design/iconography) · [Apple HIG Icons](https://developer.apple.com/design/human-interface-guidelines/icons.md) · [Material Symbols](https://github.com/google/material-design-icons) · [Adobe Spectrum Iconography](https://spectrum.adobe.com/page/iconography) · [LibreOffice-Themen (Forum)](https://ask.libreoffice.org/t/different-icon-set-on-tool-bar/43176) · [Colibre-Dateiliste](https://github.com/LibreOffice/core/tree/master/icon-themes/colibre/cmd) · [WPS-Changelog](https://www.softpedia.com/progChangelog/Kingsoft-Office-Free-Changelog-237109.html) · [Google-Docs-Redesign](https://techradar.com/news/a-load-of-top-google-workspace-programs-are-about-to-look-a-lot-different)
