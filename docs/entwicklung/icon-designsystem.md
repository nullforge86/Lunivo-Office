# Lunivo-Icon-Designsystem (Entwurf zur Freigabe — Phase 4, 5, 7)

Status: **ENTWORFEN, FREIGABE ERFORDERLICH.** Nichts davon ist im Programm aktiv (`symbole.json` ist auf den Bestand zurückgesetzt).

## 1. Grundidee und Identität
**„Seite und Linie“:** Lunivo ist eine Schreibanwendung; das Leitmotiv ist die **Seite** (aufrechtes Rechteck, 16 × 20) und die **Textzeile** (waagerechte Linie). Funktionen entstehen aus Seite + höchstens einem Zusatzzeichen. Ruhige, gleichmäßige Linie, runde Enden — sachlich, nicht verspielt, keine Verläufe, keine Schatten.
Wiedererkennungsmerkmale: (1) Dateien = Seite mit Falzecke, Seitenlayout = Seite ohne Falz; (2) Bänder (Kopf-/Fußzeile, Zeile, Spalte) = drei eng gesetzte Linien statt Füllfläche; (3) Zusatzzeichen (Plus, Haken, Pfeil) sitzen mittig/innen in der Grundform; (4) eine Zeichnung für alle Zustände, Zustand über Knopf und Palette.

## 2. Parameter (verbindlich)
| Parameter | Wert | Begründung |
|---|---|---|
| Raster | 24 × 24, viewBox `0 0 24 24` | wie Material/Fluent; Prüfgrößen 16/20/24 |
| Strichstärke | **1,5** (alle Symbole gleich) | Auftrag „starke Linien“; liegt zwischen MS 1 px und Material ≈ 2 px (Markt: `icon-markt.md`) |
| Linienenden / -verbindungen | rund / rund | freundlich, bei kleinen Größen ohne Spitzen |
| Zeichenfläche | 1…23 (Rand ≥ 1, Normalfall 2…22) | im Test geprüft (`icon-auswahl-technik.md`) |
| Abstand zwischen Linien | ≥ 3 Einheiten (Ausnahme Bänder: 1,7 = bewusst „gefüllt“) | getrennte Linien müssen bei 16 px getrennt bleiben |
| Optische Zentrierung | Mittelpunkt (12,12); asymmetrische Motive bis 1 Einheit versetzt | Apple-Regel (optisch statt geometrisch) |
| Detailgrad | ≤ 2 Elemente (Basis + Zusatz); Ausnahmen dokumentiert | MS-Regel; 23 Symbole im Bestand verletzen sie (`icon-auswahl-pruefung.md`) |
| Mindestgrößen | 16 px (Pflicht), 20 px (Standard Band klein/Menü 18), 24 px; Band groß 28 | Auftrag + Programm (`icon-inventar.md`) |
| Kontrast | ≥ 3:1 (Nicht-Text); gemessen hell 15,8:1, dunkel 14,6:1 | WCAG-Formel, `icon-auswahl-technik.md` |
| Hell / Dunkel | **eine** Zeichnung, Farbe aus der Palette (`ButtonText`, dunkel `#f4f6f8`); dunkel +0,05 Strich | wie bisher `icons.py` |
| Gefüllte Flächen | keine; Gewicht über Linien | Auftrag: Farbe/Fläche nie allein; Pfad-Format des Bestands kennt nur Strich |
| Zusammengesetzte Symbole | Basis + 1 Zusatz, Zusatz innen; MS-Variante „unten rechts mit Lücke“ bewusst **nicht** übernommen (bei 16 px verkleinert sie die Basis) | begründete Abweichung |
| Text in Icons | nur Zeichenformat-Symbole (A, x², …) und immer mit zusätzlicher Form | Apple erlaubt, MS meidet; Legasthenie → Buchstabe nie einziges Merkmal |
| Farbe | nie Bedeutungsträger; Ausnahme Farbstriche unter Schriftfarbe/Marker (Funktion = Farbe wählen) | Auftrag |
| Zustände | aktiv = Palettenfarbe; deaktiviert = Disabled-Palette; „ausgewählt“ = Knopfhintergrund des Programms (nicht Symbol) | Apple/Fluent-Muster; Laufzeit **NICHT PRÜFBAR** |

## 3. Regeln für Funktionsgruppen und komplexe Funktionen
- Dateien: Seite mit Falz + Zusatz (Plus = neu, Pfeil oben = Export, Haken = angenommen).
- Bearbeiten: wörtliche Werkzeuge (Schere, zwei Blätter, Klemmbrett, Bogenpfeile).
- Formatierung: Zeilenstapel für Absatz, Buchstabe + Linie für Zeichen.
- Tabellen: Rahmen + Teilungen; Zeile/Spalte = **Band** in Tabelle.
- Kommunikation: Sprechblase (Kommentar), Umschlag (Post), Klebezettel (Notiz) — nie vermischt.
- Komplexe Funktionen: auf die Kernmetapher reduzieren; ist das nicht möglich → Beschriftung trägt die Bedeutung (Pflicht-Tooltip), Symbol wird bewusst allgemein gehalten und in der Missverständlich-Liste geführt.

## 4. Abweichungen vom Markt (begründet)
Strich 1,5 statt 1; Zusatz innen statt unten rechts; Buchstaben nur im Zeichenformat; Zahnrad für Einstellungen (Marktstandard).
