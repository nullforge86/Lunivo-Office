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
