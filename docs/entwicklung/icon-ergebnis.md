# Icon-System Lunivo: Ergebnis nach Freigabe (2026-11-01)

Stufen: **Integriert und in der laufenden Oberfläche geprüft**; Verständlichkeit mit Menschen: **NICHT EMPIRISCH VALIDIERT**.

## Was jetzt aktiv ist
- `assets/icons/symbole.json`: 299 Bestandssymbole + 3 neue Namen (`zeileWahl`, `spalteWahl`, …); **78 Symbole neu gezeichnet**, Rest unverändert (Sichtprüfung bestanden, gleiche Strichsprache). Zustandsliste: `icon-qualitaet.md`, Bestand vorher: `icon-inventar-bestand.md`.
- Zusätzlich als eigenständige SVG-Referenz: `assets/icons/svg/` (302 Dateien, erzeugt mit `werkzeug/icon-svg-export.py`, XML/viewBox/Renderbarkeit/Zeichenfläche geprüft: 0 Befunde). Das Programm lädt weiter `symbole.json`.
- Code-Änderungen (nur Symbolzuordnung, keine Funktion): `review_tab.py` („Vorherige/Weiter“ → `vorherSatz`/`weiterSatz`, vorher Rückgängig/Wiederholen), `references_tab.py` („TOC einfügen“ → `ebenen`, vorher Dokumentinfo-Symbol), `layout_tab.py` („Genko-Einstellung“ → `kacheln`, vorher Radar-Netz).

## Laufzeitprüfung (`werkzeug/icon-oberflaeche.py`, `icon-oberflaeche.md`)
18 Register, hell und dunkel, 386 sichtbare Knöpfe mit Symbol: **alle** haben Beschriftung, Tooltip oder Accessible Name; kein Symbol unsichtbar. Bilder je Register: `assets/icons/oberflaeche/`. Deaktiviert = graue Palettenfarbe (gesehen in Überprüfen: Löschen, Weiter, Freihand), ausgewählt = Knopfhintergrund.

## Beim Bildvergleich gefundene Fehler (behoben)
Rückgängig-Pfeil für „Vorherige Kommentar/Änderung“; Dokumentinformation-Symbol für „TOC einfügen“; Radar-Symbol für „Genko-Einstellung“.

## Weiter offen
1. **Test mit Menschen** (`icon-testplan.md`) — keine Testpersonen verfügbar, keine Ergebnisse.
2. Fett/Kursiv/Unterstrichen/Durchgestrichen: **Entscheidung (2026-11-01): Buchstabenknöpfe F, K, U, S bleiben.** Begründung: WPS (Bildschirmfoto Start: B I U), Word, Apple (HIG erlaubt Text „bei Textformatierung“, SF-Symbole `bold`/`italic`/`underline` sind Buchstaben) und Material/Tabler zeigen Buchstaben-Glyphen — das gelernte Zeichen; ein gezeichnetes Symbol wäre weniger verständlich. Die Knöpfe haben Tooltip mit Tastenkürzel, Form (fett/schräg/unterstrichen) ist zusätzlich Merkmal. Kein Bandcode geändert.
3. Ähnlichkeit (Pixelüberdeckung bei 16 px, `icon-qualitaet.md`): **0 Paare ≥ 0,85** (vorher 21). Zusätzlich zu den früher genannten wurden unterscheidbar gezeichnet: `annehmen/ablehnen` (Kreis mit Haken/Kreuz) gegen `haken/schliessen` (nur Haken/Kreuz), `kommentarweg` (durchgestrichene Blase) gegen `kommentarloeschen` (X), `sprechblase` (Punkte), `hervorheben` (Textzeile mit Markierung) gegen `marker` (Stift), `pinselchen`, `einstellungen` (Zahnrad-Feld) gegen `zahnrad`/`optionen`, `ohneformat` (T durchgestrichen) gegen `einfUnformatiert`, `trefferRunter` (Pfeil auf Linie) gegen `klappe`, `Duden` (Buch mit Lesezeichen) gegen `woerterbuch`, `kanteAussen` (Doppelrahmen) gegen `kaestchen`. Hinweis: Quadratische Symbole (`kaestchen`, `kanteAussen`, `rahmen`) unterscheiden sich bei 16 px weiter nur durch das Innenzeichen.
4. Übrige WPS-Bilder (Dialoge, Dropdowns) nicht ausgewertet.

## Vergleich mit offenen Projekten (nachgeholt)
`icon-markt.md` §4: Tabler, Phosphor, Bootstrap Icons, Fluent UI, Material Symbols, KDE Breeze — 30 Funktionen gerendert und verglichen. Folgen: `einstellungen` neues Zahnrad, `tabellespalte` und `loeschen` (Papierkorb) ergänzt (304 Symbole). **Bandprüfung `funktionspruefung.py`: nach 580 s abgebrochen (Zeitlimit), nicht ausgewertet.**
