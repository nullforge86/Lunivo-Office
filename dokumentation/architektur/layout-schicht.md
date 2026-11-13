# Layout-Schicht

Die aktive Dokumentpipeline ist Qt-frei im Paket `core/`: `core/document` hält das Modell, `core/textlayout` setzt Absätze, `core/layout` bricht Seiten um und `core/rendering` zeichnet sie über ein Backend. `adapter/qt/` bindet diese Pipeline an die Qt-Oberfläche. Die `ModellAnsicht` ist standardmäßig aktiv; `LUNIVO_KERN_ANSICHT=0` schaltet auf den älteren Qt-Dokumentpfad zurück.

Die folgenden Phasen beschreiben diesen Qt-Kompatibilitätspfad (`editor/layout/` und `QTextDocument.setDocumentLayout`). Sie bleiben für den Rückfall und bestehende Qt-Druckwege relevant, sind aber nicht die Beschreibung der aktiven Kernpipeline.

## Schichten

| Schicht | Aufgabe | Stand |
|---|---|---|
| Dokumentmodell | `core/document` hält Inhalt, Formate, Tabellen, Objekte und Noten; `adapter/qt/dokument.py` überträgt Qt-Dokumente verlustfrei | Modellansicht und Bearbeitungssitzung sind verbunden |
| Textsatz | `core/textlayout` misst und bricht Text ohne Qt um | eigene Engine mit Qt-Textbackend als Plattformadapter |
| Seitenlayout | `core/layout` setzt Abschnitte, Spalten, Tabellen, Fußnoten und Objekte auf Seiten | aktiv in der Standardansicht und im Modell-PDF |
| Rendering | `core/rendering` zeichnet Seiten über `RenderTarget`; `adapter/qt/seitenbild.py` verbindet Qt | für Ansicht, PDF und Vorschaubilder angebunden |
| Qt-Kompatibilitätspfad | `editor/layout/seitenlauf.py` setzt `QTextDocument` über `QAbstractTextDocumentLayout` | Rückfall bei `LUNIVO_KERN_ANSICHT=0`; Details und Grenzen folgen unten |

Wichtige Erkenntnis (2026-11-12, mit Prototyp belegt): Das `QTextEdit` fragt für Cursor, Markierung, Hit-Test und Eingabe nur die Layout-Klasse des
Dokuments (`QTextDocument.setDocumentLayout`) und die `QTextLayout` der Absätze. Eine eigene Layout-Klasse in PySide6 funktioniert deshalb mit dem
vorhandenen Eingabe-Widget (Cursor, Tippen, Klicken) — so macht es Calligra Words. Ein eigenes Cursor-Widget (frühere Phase 5) ist nicht nötig; Phase 3
bis 5 des ersten Plans werden zur Arbeit am Seitenlauf.

Regeln: Layout und Zeichnen getrennt; die Schicht liest das Modell und schreibt nichts zurück; jede Phase löscht, was sie ersetzt, und trägt den Baustein in
`dokumentation/entwicklung/baukasten.md` ein. `unterstuetzt(doc)` erlaubt den Seitenlauf für alle Dokumente; für komplexe Dokumente ist der Lauf noch nicht inkrementell.

## Messnetz

`werkzeuge/pruefungen/layout_messnetz.py` hält je Testdatei Seitenzahl und Absatzseiten fest und vergleicht später alt gegen neu
(`festhalten` / `vergleichen`). Stand vor dem Umbau: `~/Lunivo-Testdateien/layout_messnetz_stand_2026-11-12.json` (146 Dateien, 1790 Seiten).
Eine Phase darf erst umschalten, wenn der Vergleich keine Verschlechterung zeigt.

## Phase 1: Seitenplan (erledigt)

> Die folgenden Phasen dokumentieren ausschließlich den Qt-Kompatibilitätspfad. Die gleichnamigen Kernaufgaben liegen in `core/layout/` und `core/rendering/`.

- `PageSettings.spalten_raster_mm` und `spaltenraster_px()`: ungleich breite Spalten, die einzige Stelle, die das Raster berechnet.
- DOCX liest und schreibt `w:cols` mit `w:col` (`equalWidth="0"`).
- `Seitenplan.aus_dokument` gliedert in `Bereich`e mit Einrichtung, Beginn, `neue_seite` und Spalten; `abschnitte.teile` baut darauf auf.
- Fortlaufende Abschnitte mit geänderter Geometrie bleiben auf demselben Blatt, wenn Blattgröße und Seitenhöhe gleich bleiben; der Seitenlauf übernimmt dort
  ab dem Abschnittsbeginn Ränder und Spalten.

## Phase 2/3: Stand

- Der Editor beginnt Abschnitte „nächste Seite“ auf einem neuen Blatt (`abschnittsanfaenge`, nur Anzeige).
- `Seitenlauf` setzt Absätze nach dem Seitenplan: Blattgröße und Ränder je Abschnitt, Spalten (auch ungleich breit), Absatz über mehrere Seiten und
  Spalten, Seitenumbruch davor, Ausrichtung, Einzüge, Zeilenabstand; `hitTest` und `blockBoundingRect` für das `QTextEdit`. Tests: `tests/editor/test_seitenlauf.py`.
- Im Editor angeschlossen: Absätze, Listen, Tabellen und verschachtelte Tabellen, Bilder in und neben dem Text, Rahmen, Fußnoten, Seitenzeichnung, Zoom und Auswahl.
- Tabellenzeilen werden im Ganzen auf die nächste Seite gesetzt; eine einzelne Zeile, die höher als der verfügbare Seitenraum ist, wird noch nicht geteilt.
- Inkrementelles Setzen greift nur bei einfachem Text ohne Tabellen, Rahmen oder Fußnoten am Seitenfuß.

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
- **Schwebende Rahmenbreite:** feste Breiten und Prozentbreiten werden aus der aktuellen Spaltenbreite berechnet; Prozentbreiten passen sich damit an Abschnitt und Spalte an.
- **Setzen ab dem geänderten Absatz:** bei Text ohne Tabellen/Rahmen auf oberster Ebene und ohne Fußnoten am Fuß, mit Abbruch bei gleichem Stand
  (`Seitenlauf._setzen`, `_ende`); sonst wird ganz neu gesetzt. Ein Tastendruck in 3000 Absätzen braucht 0,006 s.
- Zeilennummern und Spaltenlinien im Editor je Blatt: `oberflaeche/dokument/bearbeitung/editor_lauf.py`; `BLATT_ABSTAND_PX` steht nur im Seitenlauf.
