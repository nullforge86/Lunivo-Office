# Layout-Schicht

Ziel: Lunivo setzt Dokumente mit einer eigenen Layout-Schicht wie Word und WPS, statt das Ergebnis von Qt nachträglich zu korrigieren.
Grundlage ist der Plan des Architektur-Agenten vom 2026-11-12; der Eigentümer hat den ganzen Weg freigegeben.

## Schichten

| Schicht | Aufgabe | Stand |
|---|---|---|
| Dokumentmodell | `QTextDocument` hält Inhalt, Formate, Undo; Leser und Schreiber hängen daran | bleibt |
| Seitenplan | Bereiche (Abschnitte), Spaltenraster, Ränder — eine Quelle | Phase 1 erledigt: `editor/layout/seitenplan.py` |
| Seitenlauf | eigene Dokument-Layout-Klasse (`QAbstractTextDocumentLayout`): Absätze nach dem Seitenplan auf Blätter und Spalten setzen, `QTextLayout` je Absatz für Shaping und Zeilenumbruch | erster Baustein: `editor/layout/seitenlauf.py` (Absätze, Abschnitte, Spalten, Seitenumbruch) |
| Tabellen, Rahmen, Objekte im Lauf | Tabellenlayout, Bilder in der Zeile, Umfluss, Fußnoten | folgt |
| Anzeige | Zeichnen der Blätter, Zoom, Spaltenlinien | folgt |
| Inkrementeller Reflow | nur ab dem geänderten Block neu setzen | folgt |

Wichtige Erkenntnis (2026-11-12, mit Prototyp belegt): Das `QTextEdit` fragt für Cursor, Markierung, Hit-Test und Eingabe nur die Layout-Klasse des
Dokuments (`QTextDocument.setDocumentLayout`) und die `QTextLayout` der Absätze. Eine eigene Layout-Klasse in PySide6 funktioniert deshalb mit dem
vorhandenen Eingabe-Widget (Cursor, Tippen, Klicken) — so macht es Calligra Words. Ein eigenes Cursor-Widget (frühere Phase 5) ist nicht nötig; Phase 3
bis 5 des ersten Plans werden zur Arbeit am Seitenlauf.

Regeln: Layout und Zeichnen getrennt; die Schicht liest das Modell und schreibt nichts zurück; jede Phase löscht, was sie ersetzt, und trägt den Baustein in
`dokumentation/entwicklung/baukasten.md` ein. Dokumente mit Tabellen oder Rahmen bleiben, bis der Seitenlauf sie kennt (`unterstuetzt`), bei der Qt-Anordnung.

## Messnetz

`werkzeuge/pruefungen/layout_messnetz.py` hält je Testdatei Seitenzahl und Absatzseiten fest und vergleicht später alt gegen neu
(`festhalten` / `vergleichen`). Stand vor dem Umbau: `~/Lunivo-Testdateien/layout_messnetz_stand_2026-11-12.json` (146 Dateien, 1790 Seiten).
Eine Phase darf erst umschalten, wenn der Vergleich keine Verschlechterung zeigt.

## Phase 1: Seitenplan (erledigt)

- `PageSettings.spalten_raster_mm` und `spaltenraster_px()`: ungleich breite Spalten, die einzige Stelle, die das Raster berechnet.
- DOCX liest und schreibt `w:cols` mit `w:col` (`equalWidth="0"`).
- `Seitenplan.aus_dokument` gliedert in `Bereich`e mit Einrichtung, Beginn, `neue_seite` und Spalten; `abschnitte.teile` baut darauf auf.
- Noch offen: Die Ausgabe kennt zwei Geometrien auf einer Seite nicht. Ein fortlaufender Abschnitt mit anderen Rändern oder Spalten beginnt noch auf
  einer neuen Seite (`Bereich.neue_seite`, Hinweis im Plan). Das lösen Phase 2 (Abschnitte im Editor) und Phase 3 (Absatzfluss mit Spaltenraster).

## Phase 2/3: Stand

- Der Editor beginnt Abschnitte „nächste Seite“ auf einem neuen Blatt (`abschnittsanfaenge`, nur Anzeige).
- `Seitenlauf` setzt Absätze nach dem Seitenplan: Blattgröße und Ränder je Abschnitt, Spalten (auch ungleich breit), Absatz über mehrere Seiten und
  Spalten, Seitenumbruch davor, Ausrichtung, Einzüge, Zeilenabstand; `hitTest` und `blockBoundingRect` für das `QTextEdit`. Tests: `tests/editor/test_seitenlauf.py`.
- Noch nicht im Editor angeschlossen. Es fehlen: Tabellen, Rahmen, Bilder in der Zeile, Fußnoten, Listen, Zeichnen der Blätter mit Zoom und Auswahl, inkrementelles Setzen.

## Stand 2026-11-12: Blattweg für Druck und PDF, wiederholte Kopfzeilen

- **Blattweg:** Druck, PDF, `seitenzahl` und `seiten_bilder` (`seiten_aufteilung.render_blaetter`, `_gesetzt`, `_blatt_zeichnen`) setzen das ganze Dokument einmal mit
  dem Seitenlauf in Blattkoordinaten (`paginated_copy(..., blaetter=True)`) und zeichnen jedes Blatt: Schmuck, Bilder, Kopf-/Fußzeile, Fußnoten am Seitenfuß,
  Zeilennummern, Spaltenlinie, Text, Änderungsbalken, Blasen, Druckmarken. Leerseiten („gerade/ungerade Seite“), neu startende Seitennummern, Seitenauswahl,
  Silbentrennung, Silbenfarben und Endnoten laufen mit. Der Weg je Abschnitt (`render`, `AB.teile`) bleibt nur als Rückfall bei `LUNIVO_SEITENLAUF=0`.
- **Ort statt Seitenfluss:** Lesezeichen, Kommentarstellen, Notenlinks und Blasen fragen `ort(y) → (Seite, y ab Textrand)`. Im Blattweg liefert `Seitenlauf.ort`
  die Antwort, im Textfluss einer Druckkopie `pdf_struktur.fluss_ort`.
- **Fußnoten am Seitenfuß:** `Seitenlauf.fussnoten` ({Id: Text}); der Lauf setzt so oft neu, bis die Höhe der Fußnoten je Blatt (`reserve`) zum Text passt;
  `erg.fussnoten[Blatt]` hält Lage und Textdokumente.
- **Wiederholte Tabellenkopfzeilen:** Der Seitenlauf setzt beim Blattwechsel einer Tabelle mit `headerRowCount` die Kopfzeilen oben noch einmal (`erg.kopien`); der Text
  wird mit `QTextLayout.draw` an verschobener Stelle noch einmal gezeichnet. Tabellen in Zellen laufen nie über ein Blatt und brauchen das nicht.
- **Setzen ab dem geänderten Absatz:** bei Text ohne Tabellen/Rahmen auf oberster Ebene und ohne Fußnoten am Fuß, mit Abbruch bei gleichem Stand
  (`Seitenlauf._setzen`, `_ende`); sonst wird ganz neu gesetzt. Ein Tastendruck in 3000 Absätzen braucht 0,006 s.
- Zeilennummern und Spaltenlinien im Editor je Blatt: `oberflaeche/dokument/bearbeitung/editor_lauf.py`; `BLATT_ABSTAND_PX` steht nur im Seitenlauf.
