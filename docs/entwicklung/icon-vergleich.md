# Icon-Vergleich mit anderen Schreibprogrammen

> Ergänzung: Die vollständige Marktmatrix im Auftragsformat steht in `icon-markt.md`; Abschnitt 4 hier („geändert“) bezieht sich auf den zurückgesetzten Durchgang und ist nur Vorschlag.

Stand 2026-11-01. Quellenstufe je Aussage: **[Q]** in der Quelle gelesen (Link unten), **[W]** Allgemeinwissen über das Programm, nicht in dieser Sitzung geprüft.
Nicht erreicht: Bildschirmfotos der Programme (keine Programme/Bilder verfügbar), Recherche zu Notion und Office-Programm (nur [W]). Keine Icon-Dateien fremder Programme kopiert.

## 1. Gestaltungsprinzipien der Programme

| Programm | Prinzipien | Quelle | Folge für Lunivo |
|---|---|---|---|
| Microsoft Office („Monoline") | einfach, klar, nur nötige Elemente, **höchstens zwei Elemente** je Icon; gleiches Konzept = gleiches Element (Post = immer Umschlag); **Text in Icons vermeiden**; Zusatzzeichen unten rechts mit Lücke; Strich 1 px bei 16–32 px; Pflichtgrößen 16/20/32 [Q] | [MS Learn](https://learn.microsoft.com/en-us/office/dev/add-ins/design/add-in-icons) | Einfachheit und „gleiches Konzept, gleiches Element" übernommen; Strich bewusst kräftiger (1,5), weil der Auftrag stärkere Linien fordert |
| Apple (HIG, SF Symbols) | ein Konzept pro Icon, stark vereinfacht, vertraute Metaphern; einheitliche Größe, Detailgrad, **Strichstärke**; Strich zur Schrift passend; Text nur, wenn nötig (z. B. Textformatierung); Textabsätze abstrakt als Zeilen; neutrale Figuren; Alternativtexte [Q] | [Apple HIG Icons](https://developer.apple.com/design/human-interface-guidelines/icons.md) | Tooltips/Alternativtexte bleiben Pflicht; Buchstaben nur in Zeichenformat-Symbolen |
| Google Docs / Material Symbols | 24-px-Raster, 20/24 px pixelgenau, Strichstärke einstellbar 100–700 (Normal 400), Füllung als Zustand [Q]; Docs-Symbole für Funktionen: [W] | [Material Symbols](https://github.com/google/material-design-icons) | gleiches 24er-Raster; Füllung nur als Zustand denkbar, nicht als Unterscheidungsmerkmal |
| LibreOffice Writer | mehrere Themen (Colibre, Elementary, Breeze, Sifr …), je nach Plattform; Colibre ohne Dunkelvariante, Sifr/Breeze mit [Q]; Symbole sind benannte Befehle (`alignleft`, `accepttrackedchange` …) [Q] | [Ask LibreOffice](https://ask.libreoffice.org/t/different-icon-set-on-tool-bar/43176), [GitHub colibre](https://github.com/LibreOffice/core/tree/master/icon-themes/colibre/cmd) | **Ein** Thema für alles (kein Zwang, Themen zu wechseln); hell/dunkel über Palettenfarbe |
| Notion, Textverarbeitungsprogramm | minimal/dünn bzw. Office-nah [W] | — | Office-Programm nur Aussehens-Vorbild laut Projektregel |
| Barrierefreiheit | Studie (12 Kinder): gut gewählte Icons werden ohne Zusatzhilfe erkannt [Q]; Icons neben Schlüsselwörtern stützen das Lesen [Q]; WCAG hat keine eigenen Legasthenie-Kriterien [Q, Anbieter-Blog] | [UTM-Studie](https://journals.utm.my/jurnalteknologi/article/download/5050/3485/14266), [UXcel](https://uxcel.com/lessons/designing-for-dyslexia-081) | Symbol immer **mit** Beschriftung/Tooltip; Buchstaben als Merkmal meiden |

## 2. Funktionsvergleich (Motiv je Programm)

Apple-Spalte: nur [Q] aus der HIG-Tabelle. Übrige Spalten [W], daher nur Tendenz.

| Funktion | Apple [Q] | Word / Docs / Writer [W] | Lunivo jetzt | Befund |
|---|---|---|---|---|
| Ausschneiden | Schere | Schere | Schere | gleich |
| Kopieren | zwei Dokumente | zwei Blätter | zwei Blätter | gleich |
| Einfügen | Dokument vor Klemmbrett | Klemmbrett | Klemmbrett mit Zeilen | gleich |
| Rückgängig / Wiederholen | Bogenpfeil links / rechts | Bogenpfeil | Bogenpfeil | gleich |
| Speichern | Häkchen („Fertig/Sichern") | Diskette | Diskette | Abweichung zu Apple; Diskette ist in Office-Programmen die gelernte Metapher → behalten |
| Drucken | Drucker | Drucker | Drucker | gleich |
| Exportieren / PDF | Pfeil nach **oben** aus Quadrat | Seite mit „PDF" | Seite mit Pfeil nach oben | **angepasst** (war Pfeil nach unten = „Herunterladen") |
| Ausrichtung links/Mitte/rechts/Block | vier Zeilen; Block = vier gleiche | vier Zeilen | vier Zeilen | gleich (Anzahl der Zeilen jetzt wie Apple) |
| Suchen | Lupe; Suchen in Dokument = Lupe über Seite | Lupe | Lupe | gleich |
| Hoch-/Tiefgestellt | A mit hoher/tiefer 1 | x² / x₂ | x² / x₂ | Buchstabe/Ziffer = Text im Icon, hier nötig (Apple erlaubt) |
| Auswahl/Bestätigen | Haken im Kreis | Haken | Haken | gleich |
| Abbrechen/Schließen | Kreuz | Kreuz | Kreuz | gleich |
| Anhang | Büroklammer | Büroklammer | (kein Symbol nötig) | — |
| Einstellungen | (nicht in Tabelle) | Zahnrad | Zahnrad | **angepasst** (Entwurf Regler verworfen: Markt nutzt einheitlich Zahnrad; Regler bleibt `anpassen`/Filter-Bedeutung) |
| Kommentar | — | Sprechblase (+ Plus) | Sprechblase + Plus | gleich |
| Änderungen annehmen/ablehnen | Haken/Kreuz | Haken/Kreuz | Seite mit Haken/Kreuz | gleich (Writer-Befehle `accepttrackedchange`) |
| Schichtreihenfolge | gestapelte Quadrate, eines gefüllt | gestapelte Formen | `anordnen` (Stapel) | gleich |
| Tabelle | — | Raster | Raster | gleich |

## 3. Abgleich mit den Microsoft-Regeln (alle 300 Symbole)
- **Höchstens zwei Elemente:** 23 Symbole bestehen aus mehr als 6 Teilzeichnungen und sind damit zu komplex: `abschnittgerade/-laufend/-ungerade`, `abstand`, `allesmark`, `auswahlbereich`, `autokorr`, `datumuhrzeit`, `ebenen`, `ecken`, `ersetzen`, `gruppieren`, `hell`, `inhalt`, `kurs`, `silben`, `tabelleZeichnen`, `tabstopp`, `tasten`, `verfolgoptionen`, `verteilt`, `weSmart`, `zeilennr`. Davon sind `hell` (Sonne), `tasten`, `tabstopp` und Diagramme sachlich begründet; die übrigen sind Kandidaten zum Vereinfachen (offen).
- **Text in Icons:** `groesserA`, `kleinerA`, `hoch`, `tief`, `wordart`, `schriftfarbe`, `betonung`, `unterart`, `umriss`, `Stil`, `initiale`, `schreibweise`, `woerter`, `durchgestrichen`, `formel`, `omega`, `zeichenschattierung`, `eingeschlossen`. Alle gehören zur Zeichenformatierung (Apple: erlaubt, wenn nötig; Microsoft: meiden). Legasthenie-Aspekt: Buchstaben als einziges Merkmal vermeiden → alle haben zusätzlich eine Form (Unterstreichung, Pfeil, Rahmen) und einen Tooltip.
- **Gleiches Konzept, gleiches Element:** Post = Umschlag (`briefumschlag`, `empfaenger`, `serie`), Dokument = Seite mit Ecke, Ordner = Mappe — eingehalten. Sprechblase für Kommentar/Chat/Notiz ist getrennt (Notiz = Klebezettel).
- **Zusatzzeichen unten rechts mit Lücke (Microsoft):** nicht übernommen. Lunivo setzt Plus/Haken in die Mitte der Grundform; bei 1,5 px Strich und 16 px bleibt es so lesbarer. Bewusste Abweichung.
- **Strichstärke:** Microsoft 1 px, Material Normal 2 px bei 24, Lunivo 1,5 px — dazwischen, begründet mit Auftrag „ausreichend starke Linien".

## 4. Was daraus geändert wurde
`pdf` (Pfeil nach oben, nach Apple-Export), `einstellungen` (Zahnrad statt Regler). Alles andere bestätigte den vorhandenen Stand.
