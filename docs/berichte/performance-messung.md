# Performance-Messung (2026-11-07)

Gemessen auf dem Entwicklungsrechner, `QT_QPA_PLATFORM=offscreen`, Testdokumente aus synthetischem Text (5 / 50 / 200 Seiten, DOCX).
Zeiten sind Einzelmessungen (keine Mittelwerte über viele Läufe) und gelten nur für diese Dokumente und diesen Rechner.

| Bereich | Engpass | Änderung | Vorher | Nachher |
|---|---|---|---|---|
| Programmstart | 19 Band-Reiter (alle Knöpfe, Menüs) wurden vor dem ersten Anzeigen gebaut (`ui/ribbon/ribbon_bar.py`) | Reiter werden erst beim Wählen oder im Leerlauf nach dem Anzeigen gebaut; Zugriff auf `felder`/`bandfehler` baut alle | Fenster bauen 5,1 s | 1,3 s |
| Tippen, 200 Seiten | `_hat_effekt` (ganzes Dokument je Zeichen), `abschnitte.umbrueche`, `_bereiche` | Effekt-Stand inkrementell; Abschnitte und Bereiche je Dokumentrevision zwischengespeichert | 127 ms je Zeichen | 46 ms |
| Tippen, 50 Seiten | dieselben | dieselben | 21 ms | 13 ms |
| Öffnen DOCX, 200 Seiten | Zeichenformat jedes Textlaufs wurde neu aufgelöst (`services/docx_teile/lesen_stile.py`) | Zwischenspeicher je Datei | 2,57 s | 2,0 s |
| Öffnen DOCX, 50 Seiten | dieselbe | dieselbe | 0,73 s | 0,58 s |
| Prüfung (`proofing_service`) | `toPlainText()` je Fund in `_zeigen` | Text je Dokumentrevision einmal | ca. 230 ms je Aktualisierung bei 200 Funden (hochgerechnet aus 1,15 ms je Aufruf) | ca. 1 ms (nicht am laufenden Programm gemessen) |
| Ollama, warm | Antwort erst nach Ende sichtbar | Streaming | erstes Zeichen nach 8,2 s | 0,1 s (Gesamtdauer unverändert, 8,6 s) |
| Ollama, kalt | Modell wird geladen | `keep_alive` 30 min | erstes Zeichen nach 7,5 s (Streaming) | gilt nur beim ersten Mal |

Modell: `llama3.2:3b`, lokale Ollama-Instanz, eine Frage mit drei Sätzen Antwort.

## Unverändert gemessen

- Seitenfluss (`seitenfluss.anwenden`): 5 / 49 / 190 ms bei 5 / 50 / 200 Seiten. Ein Versuch, ihn zu beschleunigen, brachte nichts und wurde zurückgenommen.
- Speicher (RSS) nach dem Öffnen: Start 275 MB; 5 Seiten 289 MB; 50 Seiten 320 MB; 200 Seiten 437 MB.
- Scrollen mit Neuzeichnen je Schritt: 2 / 5 / 13 ms (5 / 50 / 200 Seiten).
- Qt-Seitenlayout beim Öffnen (200 Seiten): rund 0,7 s, nicht beeinflussbar ohne Eingriff in Qt.

## Grenzen

- Der Band-Aufbau im Leerlauf verlagert Arbeit, er spart sie nicht: bis alle Reiter gebaut sind, vergehen dieselben Sekunden, aber die Oberfläche ist vorher bedienbar.
- Ein Effekt-Stand „ja“ bleibt, bis etwas umformatiert wird; dann wird neu gesucht. Das kann kurzzeitig langsamer zeichnen, nie falsch.
- Messungen am echten Bildschirm (nicht offscreen) und mit echten Kundendokumenten stehen aus.

## Nachtrag 2026-11-10

Gleiche Bedingungen (offscreen, synthetischer Text, Einzelmessungen). Die Dokumente wurden mit `setPlainText` gefüllt (4 / 44 / 178 Seiten), nicht aus DOCX geladen.

| Bereich | Engpass | Änderung | Vorher | Nachher |
|---|---|---|---|---|
| Vollständige Prüfung, 200 Seiten | `_klang_fund_wort` kopierte und durchsuchte je unbekanntem Wort den ganzen Text davor (`text[:stelle]`, `re.search(…$)`): quadratisch | `_am_satzanfang` schaut nur bis zum letzten Zeichen davor; Tippfehler-Vorschläge je Wort zwischengespeichert (`proofing/pruefung.py`) | 26,1 s (50 Seiten: 2,5 s) | 2,9 s (50 Seiten: 0,7 s) |
| Erster Tastendruck nach dem Laden, 200 Seiten | Die laufende Prüfung im Hintergrundfaden bremst den Hauptfaden (Python-Sperre, GIL) | dieselbe Änderung: die Prüfung ist fertig, bevor getippt wird | 16–18 s | 46 ms |
| Tippen, 200 Seiten | Zeichnen durchlief alle Blätter; drei Absatz-Suchläufe je Zeichenvorgang; Wörterzählen zweimal je Taste | sichtbarer Blattbereich (`_blatt_bereich`), ein Suchlauf je Revision (`_hat_blockzusatz`), Zähler je Revision | 46,7 ms je Zeichen (Median) | 29,8 ms |
| Tippen, 50 / 5 Seiten | dieselben | dieselben | 15,8 / 6,6 ms | 11,2 / 5,6 ms |
| KI: Chat neben fortlaufendem Assistenten | Chat wurde abgelehnt, solange ein Assistent lief | Chat verdrängt den Assistenten (`dauer_verdraengen`): Verbindung wird geschlossen, Ergebnis verworfen, der Absatz kommt danach wieder dran | — | nicht mit laufendem Ollama gemessen |

Die Darstellung wurde vor und nach der Änderung verglichen: 16 Ausschnitte (1/2/3 Spalten, Zoom 0,75/1,0/1,5) sind bildpunktgleich. Blätter verschiedener Größe (Querblatt) sind nur durch `tests/dokument/seite/test_querblatt.py` abgedeckt.

### Offen

- Der Tippfehler-Zwischenspeicher wirkt im Testtext stärker als in echten Texten, weil sich dort dieselben Wörter ständig wiederholen.
- Solange eine vollständige Prüfung läuft (jetzt rund 3 s bei 200 Seiten), reagiert die Oberfläche weiter träge; das behebt erst eine Prüfung in einem eigenen Prozess oder in Abschnitten.
- Nach einer Schreibpause: `seitenfluss.anwenden` rund 210 ms und `_recount` (Druckkopie des Dokuments) rund 230 ms bei 200 Seiten — ein einmaliger Ruck von etwa 0,3 s, unverändert.
- `num_ctx` je Aufgabe wurde bewusst nicht eingeführt: Ollama lädt das Modell neu, sobald sich die Kontextgröße ändert; wechselnde Größen zwischen Chat und Assistenten wären langsamer als eine feste.
