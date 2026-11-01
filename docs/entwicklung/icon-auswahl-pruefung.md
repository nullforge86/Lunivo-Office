# Icon-Auswahl: Zuordnung, visuelle Prüfung, Missverständlich-Liste (Phase 6.1, 8, 10.2, 10.4)

Stand 2026-11-01. Kontaktübersicht: `assets/icons/entwurf/kontaktuebersicht-auswahl.png` (hell/dunkel, 16/20/24 px, 48 px Vergrößerung, 31 Varianten, Namen angezeigt). SVG: `assets/icons/entwurf/svg-auswahl/`. Technik: `icon-auswahl-technik.md` (alle 31 Varianten: XML, viewBox, QSvgRenderer, Zeichenfläche — **OK**).
**Status: ENTWORFEN und per Sicht geprüft (durch Claude, nicht durch Menschen). FREIGABE ERFORDERLICH.** Nicht integriert.

## 1. Funktionszuordnung der Auswahl (6.1)
Bisheriges Icon = Bestand (`symbole.json` HEAD). „Abgrenzung“ = nächstähnliches Symbol im Bestand (Pixelüberdeckung 16 px, `icon-qualitaet.md`).

| Funktion | Bisheriges Icon | Geplantes Icon | Bedeutung des Motivs | Abgrenzung zu ähnlichen Funktionen | Status |
|---|---|---|---|---|---|
| Dokument (neu) | `neu` Seite+Plus | A: Seite mit Falz + Plus (leicht überarbeitet) | neues leeres Blatt | `oeffnen` (Ordner), `speichern` (Diskette); Plus = Aktion; Risiko `pdf` (gleiche Seitenform) | ENTWORFEN |
| Speichern | `speichern` Diskette | A: Diskette, größere Flächen | gelernte Metapher (Office) | `neu`, `unter` (Diskette+Kopie) | ENTWORFEN — kaum Unterschied zu Bestand |
| Drucken | `drucken` Drucker | A: Drucker, einfacher | Gerät | `drucker2` (Mehrfachbelegung im Bestand) | ENTWORFEN — kaum Unterschied |
| Ausschneiden | `schere` | A: Schere mit durchlaufenden Klingen | Werkzeug | `radierer`, `kopie` | ENTWORFEN |
| Kopieren | `kopie` | A: zwei Blätter, Rückblatt als Winkel | Duplikat | `kleben` (Klemmbrett) | ENTWORFEN |
| Einfügen | `kleben` leeres Brett | A: Klemmbrett mit Textzeilen | Einfügen von Text aus der Ablage | `einfFormatiert/-Unformatiert/-Inhalte` (Varianten), `notiz` | ENTWORFEN |
| Suchen | `lupe` mit Plus (= Zoom) | A: Lupe ohne Zusatz | Suchen/Finden | `kleinerLupe`, Zoom-Symbole; **Bestand `lupe` ist Zoom-Lupe** | ENTWORFEN — Bestand mehrdeutig |
| Ersetzen | `ersetzen` gestrichelter Kasten + Pfeil | A: Tauschpfeile ⇄ | Austausch A↔B | `wechseln` (Pfeilschleife), `zuordnen` (⇄ im Bestand!) | ENTWORFEN — Abgrenzung zu `zuordnen` **FREIGABE ERFORDERLICH** |
| Formatierung | `schriftFenster` (Buchstabe A) | A: A mit Linie | Zeichenformat | `unterart` (U), `wordart`, `schriftfarbe` (alle A-Motive) | ENTWORFEN — A-Familie schwer unterscheidbar |
| Tabelle | `tabelle` | A: Raster mit Kopfzeile | Tabelle | `tabellenblatt` (0,90), `kacheln` | ENTWORFEN |
| Zeile (Tabelle) | — (kein Einzelsymbol) | A: Tabelle mit Zeilenband | Zeile im Raster | `kanteWaage`, `tabellezeile` | ENTWORFEN (neu) |
| Spalte (Tabelle) | `spalte1/2/3` (Seitenspalten) | A: Tabelle mit Spaltenband | Spalte im Raster | `spalten`, `spalte2` (Seitenlayout!) | ENTWORFEN — Verwechslung Tabellenspalte/Seitenspalte möglich |
| Kommentar | `kommentarneu` | A: Sprechblase + Plus | Anmerkung hinzufügen | `sprechblase`, `chat`, `notiz` | ENTWORFEN |
| Einstellungen | `einstellungen` (Raster + Schraubenschlüssel) | A: Zahnrad | Marktstandard | `optionen`, `zahnrad` (gleiche Zeichnung, gewollt) | ENTWORFEN |
| Navigation | `navigation` (Fenster mit Spalte) | A: Fenster mit Listenfeld links | Navigationsbereich | `fensterNeben`, `bereich` | ENTWORFEN — Bedeutung nur mit Beschriftung klar |

## 2. Varianten und Begründung (Auswahl der „schwierigen“ Funktionen)
| Funktion | Gewählt | Verworfen | Warum |
|---|---|---|---|
| Ersetzen | A Tauschpfeile | B zwei Kästen + Pfeil (wirkt „verschieben“); C Bestand (Strichelung zerfällt bei 16 px) | A: ein Motiv, 2 Elemente, bei 16 px lesbar |
| Einstellungen | A Zahnrad | B Regler | Zahnrad in allen Vergleichsprogrammen üblich; Regler = „Filter/Anpassen“ |
| Zeile/Spalte | A Band in Tabelle | B reiner Pfeil | B hat keinen Tabellenbezug |
| Formatierung | A Buchstabe+Linie | B Pinsel | Pinsel = „Format übertragen“ (andere Funktion) |
| Navigation | A Seitenfenster | B Kompass | Kompass = „Karte/Ort“ |
| Suchen | A Lupe pur | B Lupe+Plus | B = Zoom |

## 3. Visuelle Prüfung der gewählten Varianten (10.2)
Kriterien: (1) ohne Überlegung erkennbar, (2) unterscheidbar, (3) klein lesbar, (4) professionell, (5) passt zur Bildsprache, (6) hell/dunkel, (7) technisch sauber. Wertung **j** = ja, **t** = teilweise, **n** = nein; Einschätzung durch Claude am gerenderten Bild, **keine Nutzerdaten**.

| Funktion | 1 | 2 | 3 | 4 | 5 | 6 | 7 | Anmerkung |
|---|---|---|---|---|---|---|---|---|
| Dokument (neu) | j | t | j | j | j | j | j | Plus klein bei 16 px; ähnlich `pdf` |
| Speichern | j | j | j | j | j | j | j | |
| Drucken | j | j | j | j | j | j | j | |
| Ausschneiden | j | j | j | j | j | j | j | |
| Kopieren | j | j | j | j | j | j | j | |
| Einfügen | j | j | j | j | j | j | j | |
| Suchen | j | j | j | j | j | j | j | |
| Ersetzen | t | t | j | j | j | j | j | ⇄ kann auch „Tauschen/Wechseln“ bedeuten |
| Formatierung | t | t | j | j | j | j | j | A-Familie |
| Tabelle | j | t | j | j | j | j | j | nahe `tabellenblatt` |
| Zeile | t | t | t | j | j | j | j | Band bei 16 px schwer von „dicke Linie“ zu trennen |
| Spalte | t | t | t | j | j | j | j | wie Zeile; Seitenspalte-Verwechslung |
| Kommentar | j | j | j | j | j | j | j | |
| Einstellungen | j | j | t | j | j | j | j | Zacken bei 16 px dicht |
| Navigation | t | t | j | j | j | j | j | abstrakt |

**Befund ehrlich:** Für Speichern, Drucken, Ausschneiden, Kopieren, Suchen unterscheidet sich der Entwurf kaum vom Bestand (Gewinn gering). Wirklich verbessert: Einfügen, Suchen (Zoom-Lupe), Ersetzen. Zeile/Spalte/Navigation sind **noch nicht überzeugend**.

## 4. Missverständlich-Liste (10.4)
| Symbol | Bisheriges Motiv | Vermutete Fehlinterpretation | Funktion | Alternative | Erforderliche Verbesserung |
|---|---|---|---|---|---|
| `lupe` (Bestand) | Lupe mit Plus | „Zoom“ statt „Suchen“ | Suchen | Lupe ohne Plus (Entwurf) | austauschen; Zoom-Symbole getrennt führen |
| `kleben` | leeres Klemmbrett | „Notiz/Aufgabe“ | Einfügen | Klemmbrett mit Zeilen | austauschen |
| `ersetzen` | gestrichelter Kasten + Pfeil | „Auswahl verschieben“ | Ersetzen | Tauschpfeile | austauschen, Abgrenzung zu `zuordnen` klären |
| `eineSeite` | Doppelpfeil senkrecht | „Zeilenabstand“ | Eine Seite anzeigen | Einzelseite (Entwurf) | austauschen |
| `fussnote` | Fußabdrücke | wörtlich „Fußspuren“ | Fußnote | Seite mit Trennlinie | austauschen |
| `zahl` | Bildschirm | „Anzeige“ | Zahl einfügen | „#“ | austauschen |
| `assistent` | Plus | „Hinzufügen“ | KI-Aktionen | Sprechblase + Funkeln | austauschen |
| `raender` | vier Ecken | „Vollbild/Auswahl“ | Seitenränder | Seite mit Textfeld | austauschen |
| `linie` | Liniendiagramm | „Linie zeichnen“ | Diagramm Linie | in Diagrammkontext lassen, Beschriftung | prüfen |
| `netz` | Fünfeck | „Form“ | Netzdiagramm | Netz mit Speichen | austauschen |
| `zuletzt` / `uhrzeit` | Uhr / Uhr | identisch | Zuletzt verwendet vs. Uhrzeit | Uhr mit Rückpfeil | austauschen |
| `naechstes` | Pfeil nach unten | „Download“ | Weiter | — | **behalten**: bildet mit `voriges` (Pfeil nach oben) in Fußnoten/Kopfzeile ein stimmiges Paar |
| `spalte1/2/3` vs. Tabellenspalte | Seite mit Linien | „Tabelle“ | Seitenspalten | Seite mit Teilern (Entwurf) | Abgrenzung klären |
| `einstellungen` (Bestand) | Raster + Schlüssel | „Werkzeuge/Apps“ | Einstellungen | Zahnrad | austauschen |
| `weLeerModus`, `weNeu`, `weSmart`, `weFuehrend`, `ueberprog`, `trennung`, `silben`, `wasserzeichen`, `vorlesen` | abstrakt | s. `icon-entwurf-bericht.md` | je Funktion | Tooltip trägt Bedeutung | Konzept offen |
| `pdf` | Seite + Zeilen/Pfeil | „Herunterladen“ | PDF-Export | Seite + Pfeil auf | FREIGABE ERFORDERLICH |
| `annehmen`/`haken` | identische Zeichnung | gleiche Funktion, ok | — | — | keine |

Fett/Kursiv/Unterstrichen: im Band **ohne** Funktionssymbol (Buchstabenknöpfe F, K, U) → nicht legasthenie-freundlich als einziges Merkmal; Symbolentscheidung offen (`FREIGABE ERFORDERLICH`).
