# Icon-Auswahl: technische Prüfung (Phase 10.1)

Erzeugt mit `werkzeug/icon-auswahl.py`. Strich 1.5 px, Rendering mit `QSvgRenderer` (1× – strenger als die 2×-Darstellung im Programm).

## Kontrast (WCAG-Formel, Nicht-Text-Kontrast Mindestwert 3:1)
- hell: #1f2328 auf #ffffff = 15.8:1
- dunkel: #f4f6f8 auf #1f2328 = 14.6:1
- deaktiviert: Palettenfarbe des Programms (Disabled); hier nicht gemessen (**NICHT PRÜFBAR** ohne laufende Oberfläche)

| Symbol | XML gültig | viewBox 0 0 24 24 | QSvgRenderer gültig | Zeichnung innerhalb 1…23 | Tinte 16 px | Ergebnis |
|---|---|---|---|---|---|---|
| Dokument (neu) A (`neu-A.svg`) | ja | ja | ja | ja (4.0…20.0 / 2.0…22.0) | 24 % | OK |
| Dokument (neu) B (`neu-B.svg`) | ja | ja | ja | ja (4.0…20.0 / 2.0…22.0) | 19 % | OK |
| Speichern A (`speichern-A.svg`) | ja | ja | ja | ja (3.0…21.0 / 3.0…21.0) | 39 % | OK |
| Speichern B (`speichern-B.svg`) | ja | ja | ja | ja (3.0…21.0 / 3.0…21.0) | 38 % | OK |
| Drucken A (`drucken-A.svg`) | ja | ja | ja | ja (3.0…21.0 / 3.0…21.0) | 33 % | OK |
| Drucken B (`drucken-B.svg`) | ja | ja | ja | ja (2.0…22.0 / 2.0…22.0) | 36 % | OK |
| Ausschneiden A (`schere-A.svg`) | ja | ja | ja | ja (3.0…21.0 / 3.0…21.0) | 19 % | OK |
| Ausschneiden B (`schere-B.svg`) | ja | ja | ja | ja (3.0…20.0 / 3.0…21.0) | 21 % | OK |
| Kopieren A (`kopie-A.svg`) | ja | ja | ja | ja (3.0…21.0 / 3.0…21.0) | 33 % | OK |
| Kopieren B (`kopie-B.svg`) | ja | ja | ja | ja (2.0…22.0 / 2.0…22.0) | 20 % | OK |
| Einfügen A (`kleben-A.svg`) | ja | ja | ja | ja (4.0…20.0 / 2.0…22.0) | 28 % | OK |
| Einfügen B (`kleben-B.svg`) | ja | ja | ja | ja (4.0…20.0 / 2.0…22.0) | 22 % | OK |
| Suchen A (`lupe-A.svg`) | ja | ja | ja | ja (3.0…21.0 / 3.0…21.0) | 17 % | OK |
| Suchen B (`lupe-B.svg`) | ja | ja | ja | ja (3.0…21.0 / 3.0…21.0) | 19 % | OK |
| Ersetzen A (`ersetzen-A.svg`) | ja | ja | ja | ja (4.0…20.0 / 4.0…20.0) | 13 % | OK |
| Ersetzen B (`ersetzen-B.svg`) | ja | ja | ja | ja (3.0…21.0 / 4.0…20.0) | 20 % | OK |
| Ersetzen C (`ersetzen-C.svg`) | ja | ja | ja | ja (3.0…21.0 / 3.0…21.0) | 18 % | OK |
| Formatierung A (`schriftFenster-A.svg`) | ja | ja | ja | ja (3.0…21.0 / 4.0…21.0) | 21 % | OK |
| Formatierung B (`schriftFenster-B.svg`) | ja | ja | ja | ja (2.0…22.0 / 2.0…22.0) | 20 % | OK |
| Tabelle A (`tabelle-A.svg`) | ja | ja | ja | ja (3.0…21.0 / 3.0…21.0) | 50 % | OK |
| Tabelle B (`tabelle-B.svg`) | ja | ja | ja | ja (3.0…21.0 / 3.0…21.0) | 53 % | OK |
| Zeile (Tabelle) A (`zeile-A.svg`) | ja | ja | ja | ja (3.0…21.0 / 3.0…21.0) | 51 % | OK |
| Zeile (Tabelle) B (`zeile-B.svg`) | ja | ja | ja | ja (2.0…22.0 / 9.0…15.0) | 14 % | OK |
| Spalte (Tabelle) A (`spalte-A.svg`) | ja | ja | ja | ja (3.0…21.0 / 3.0…21.0) | 51 % | OK |
| Spalte (Tabelle) B (`spalte-B.svg`) | ja | ja | ja | ja (9.0…15.0 / 2.0…22.0) | 13 % | OK |
| Kommentar A (`kommentarneu-A.svg`) | ja | ja | ja | ja (3.0…21.0 / 4.0…21.0) | 27 % | OK |
| Kommentar B (`kommentarneu-B.svg`) | ja | ja | ja | ja (2.0…22.0 / 3.0…22.0) | 29 % | OK |
| Einstellungen A (`zahnrad-A.svg`) | ja | ja | ja | ja (1.0…23.0 / 1.0…23.0) | 28 % | OK |
| Einstellungen B (`zahnrad-B.svg`) | ja | ja | ja | ja (4.0…20.0 / 3.5…20.5) | 31 % | OK |
| Navigation A (`navigation-A.svg`) | ja | ja | ja | ja (3.0…21.0 / 4.0…20.0) | 35 % | OK |
| Navigation B (`navigation-B.svg`) | ja | ja | ja | ja (3.0…21.0 / 3.0…21.0) | 23 % | OK |
