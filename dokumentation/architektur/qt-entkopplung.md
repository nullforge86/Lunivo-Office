# Qt-Entkopplung des Dokumentenkerns

Stand 2026-11-12. Auftrag des Eigentümers: Dokumenten-, Seiten- und Textlayout-Logik schrittweise unabhängig von Qt machen; PySide6 bleibt für die Oberfläche.
Dieses Dokument hält den Ist-Zustand (Phase 1), den Zielzustand und die Phasen fest. Gebaut sind bisher Phase 1 bis 3.

## Zielbild und Regeln

```
oberflaeche → adapter/qt → core          (Oberfläche darf Kern und Adapter nutzen, nie umgekehrt)
core:  document → textlayout → layout → rendering
```

- `core/` importiert weder PySide6/PyQt noch `adapter`, `oberflaeche`, `editor`, `dienste`, `kern`, `ki`, `korrektur`; Qt-Datentypen stehen in keiner öffentlichen Schnittstelle.
  Wächter: `tests/architektur/test_core_ohne_qt.py` (liest die Importe von `core/` mit `ast`).
- Maße: Bildpunkte bei 96 dpi, y nach unten (wie `modelle/seite.py`, `mm_to_px`). `modelle/seite.py` (`PageSettings`) enthält schon kein Qt und kann in `core` einziehen/hineinzeigen.
- Qt-Importe gehören nach `adapter/qt/` und `oberflaeche/`.

## Phase 1: Ist-Zustand (Dateien mit PySide6-Import je Schicht)

| Schicht | mit Qt / alle Dateien | Bedeutung |
|---|---|---|
| `modelle` | 0 / 4 | schon frei von Qt (`PageSettings`, Seitenmaße) |
| `editor/layout/seitenplan.py` | nur `QTextDocument` als Eingabe von `Seitenplan.aus_dokument` | Plan selbst ist reine Datenstruktur (`Bereich`, `Spalte`) |
| `editor` | 74 / 98 | Textdokument, Layout, Seitenaufteilung, Objekte, Diagramme |
| `dienste` | 24 / 57 | DOCX/ODT/RTF lesen und schreiben direkt in `QTextDocument` |
| `kern` | 25 / 39 | Befehle (Cursor-Aktionen) |
| `korrektur`, `ki`, `plattform` | 2/12, 6/31, 1/6 | Randbereiche |
| `oberflaeche` | 212 / 284 | Oberfläche: bleibt bei Qt |

### Qt-Klassen nach Aufgabe (Dateien je Schicht)

| Gruppe | Klasse (Auswahl) | dienste | editor | kern | oberflaeche |
|---|---|---|---|---|---|
| Geometrie | `QRectF` / `QPointF` / `QSizeF` / `QMarginsF` | 2 / 1 / – / – | 33 / 19 / 5 / 1 | 3 | 49 / 23 / 2 |
| Dokument | `QTextDocument` | 12 | 30 | – | 10 |
| | `QTextCursor` | 9 | 32 | 10 | 23 |
| | `QTextCharFormat` / `QTextBlockFormat` | 7 / 7 | 24 / 13 | 5 / 1 | 17 / 9 |
| | `QTextTable` / `QTextFrame` / `QTextImageFormat` | 4 / 2 / 3 | 5 / 2 / 5 | – | – / – / 5 |
| | `QTextBlock` / `QTextFragment` | 3 / – | 7 / 2 | – | – |
| Textlayout | `QTextLayout` / `QTextLine` | – | 1 / 1 (alles in `seitenlauf.py`) | – | – |
| | `QFontMetricsF` / `QFont` | – / 9 | 12 / 25 | – / 3 | 2 / 34 |
| Zeichnen | `QPainter` / `QPen` / `QBrush` / `QColor` | 2 / 1 / 6 / 8 | 28 / 23 / 23 / 39 | 2 / – / 1 / 5 | 54 / 39 / 8 / 68 |
| | `QImage` / `QPixmap` / `QPainterPath` | 9 / 1 / 1 | 21 / 3 / 14 | 1 / 1 | 15 / 34 / 6 |
| Ausgabe | `QPdfWriter` / `QPrinter` / `QPageLayout` / `QPageSize` | – | 1 / 1 / 2 / 2 | – | – / 1 |

Rohdaten (alle Klassen mit Dateien): bei Bedarf mit dem Skript im Bericht der Sitzung neu erzeugbar; die Zählung steht oben.

### Wo der Kern heute an Qt hängt

- **Dokumentmodell = `QTextDocument`.** Es ist die einzige Wahrheit für Inhalt und Format: Editor (`editor/dokument`, `editor/text`, `editor/tabelle`), Import/Export
  (`dienste/docx_leser.py`, `dienste/docx_teile/lesen_*.py`, `schreiben_*.py`, ODT, RTF), Befehle (`kern/befehle`). Zusatzdaten (Abschnitte, Rahmen, Notenmarken, Änderungen)
  stehen als benutzerdefinierte Eigenschaften (`B_ABSCHNITT`, `P_NOTE`, `P_AENDERUNG` …) in Qt-Formaten.
- **Textsatz = `QTextLayout`/`QTextLine`** (Formen, Umbrechen, Zeilenhöhen) in `editor/layout/seitenlauf.py`; Schriftmaße über `QFont`/`QFontMetricsF` (`editor/text`, Wörterbuch, Zeilenabstand).
- **`Seitenlauf` = Unterklasse von `QAbstractTextDocumentLayout`** (damit `QTextEdit` ihn nutzt): Eingabe `QTextDocument`, Ausgabe `QRectF`-Rechtecke je Block, `QTextTable`-Zellen, Hit-Test, Zeichnen über `QPainter`.
- **Seitenausgabe** (`editor/seite/seiten_aufteilung.py`): `QPainter` auf `QPdfWriter`/`QPrinter`/`QImage`, Seitenlayout `QPageLayout`.
- **Zeichnen von Objekten** (Formen, Diagramme, Bilder, Wasserzeichen): `QPainter`, `QPainterPath`, `QLinearGradient`.

### Einordnung

| Bereich | Einordnung | Ersatz im Kern |
|---|---|---|
| Geometrie (`QRectF`…) | ersetzen | `core/geometry` — **gebaut (Phase 2)**, Adapter **gebaut (Phase 3)** |
| `QTextDocument` samt Formaten, `QTextCursor` | ersetzen, größter Block | `core/document` (Phase 4), Import/Export schrittweise darauf (Phase 5) |
| `QTextLayout`, `QFont*`, Glyphen | hinter Schnittstelle | `core/textlayout` (`TextLayoutEngine`, Phase 6); Qt-Implementierung bleibt zunächst Standard |
| `Seitenplan` | fast frei | nur `aus_dokument` auf das neue Modell umstellen (Phase 7) |
| `Seitenlauf` | schrittweise | Phase 7: erst Geometrie, dann Dokumentzugriff und Textsatz über Schnittstellen |
| `QPainter` im Seitenaufbau | hinter Schnittstelle | `core/rendering` (`RenderBackend`, Phase 8); Qt-Backend zuerst |
| `QTextEdit`-Anbindung (`editor_lauf.py`, Cursor, Auswahl, Hit-Test) | bleibt Oberfläche | `adapter/qt` (Phase 9) |
| Widgets, Dialoge, Band, Seitenleiste, `QPalette`, `QPixmap` für Symbole | bleibt in `oberflaeche` | – |

## Phasen

| Phase | Inhalt | Stand |
|---|---|---|
| 1 | Abhängigkeiten erfassen, dokumentieren | erledigt (dieses Dokument) |
| 2 | `core/geometry`: `Point`, `Size`, `Rect`, `Margins` | erledigt |
| 3 | `adapter/qt/geometrie.py` | erledigt; die vorhandenen Dateien nutzen noch `QRectF` und sind **nicht** umgestellt |
| 4 | Dokumentenmodell `core/document` | erledigt als **zusätzliches** Modell mit verlustfreier Brücke (`adapter/qt/dokument.py`); der Editor arbeitet weiter auf `QTextDocument` |
| 5 | DOCX-Import an das Modell anbinden | 5a erledigt; 5b **teilweise**: neuer Modell-Leser (`dienste/docx_modell_leser.py`) ist im DOCX-Import angeschlossen (`datei_dienst._docx_lesen`), mit Rückfall auf den alten Leser für 43 von 104 Prüfdateien |
| 6 | `core/textlayout` | Schnittstelle `TextLayoutEngine` und Qt-Umsetzung (`adapter/qt/textlayout.py`) erledigt; eine Qt-freie Umsetzung (HarfBuzz/FreeType) nicht begonnen |
| 7 | `Seitenplan`/`Seitenlauf` entkoppeln | **teilweise**: Rechtecke im Seitenlauf sind `core.geometry.Rect` (Commit `32e2e62`); Umrechnung zu Qt nur an der Grenze. Blätter, Zellen, Stand/Ergebnis und die Platzvergabe (Spalten, Seitenwechsel, Ausschlüsse) stehen Qt-frei in `editor/layout/seitenplatz.py` (Wächter `test_seitenplatz_ohne_qt.py`); Text, Tabellen und Rahmen laufen weiter über `QTextDocument`/`QTextLayout` (Blocker: Phase 6) |
| 8 | `core/rendering` | Schnittstelle `RenderBackend` und Qt-Backend (`adapter/qt/rendering.py`) erledigt; Spaltenlinien, Änderungsbalken, Fußnoten-Trennlinie, Zeilennummern, Seitenfarbe, Druckmarken, Kunstrahmen (`draw_path`), Wasserzeichen (`push_state`/`pop_state` für Deckkraft, Verschiebung, Drehung) und einfache Kopf-/Fußzeilen laufen darüber (`Style` kennt auch `dashed`); Pixelvergleich alt/neu identisch; der übrige Seitenaufbau noch nicht |
| 9 | Adapter für Oberfläche vervollständigen | teilweise: Geometrie, Dokument, Textsatz und Zeichnen haben je einen Adapter; die Oberfläche selbst ist noch nicht umgestellt |
| 10 | Abschlussdokumentation | Stand dieses Dokuments; siehe Abschnitt „Stand am Ende der Sitzung“ |

### Blockaden und Risiken für Phase 4 bis 9 (vor dem Weitergehen zu entscheiden)

1. **Umfang Phase 4/5.** 74 Dateien in `editor`, 24 in `dienste` und 25 in `kern` arbeiten direkt auf `QTextDocument`/`QTextCursor`. Ein eigenes Dokumentenmodell ersetzt nicht nur die Daten, sondern die
   gesamte Bearbeitung (Einfügen, Löschen, Rückgängig/Wiederherstellen, Auswahl, Formatänderung). Phase 4 ist machbar als **zusätzliches** Modell mit Konvertierung in beide Richtungen
   (Adapter), aber ein Umstieg des Editors darauf wäre ein eigenes, großes Vorhaben mit Zwischenzustand zweier Wahrheiten. Das verlangt eine Entscheidung des Eigentümers.
2. **Rückgängig/Wiederherstellen** liefert heute `QTextDocument` (Undo-Stack). Ein Qt-freier Kern braucht eine eigene Änderungsliste, sonst geht Undo verloren.
3. **`Seitenlauf` ist auch die Qt-Layout-Klasse.** Das `QTextEdit` fragt `hitTest`, `blockBoundingRect`, `draw`. Ein Qt-freier Seitenlauf braucht eine dünne Qt-Hülle im Adapter (`QAbstractTextDocumentLayout`-Unterklasse),
   die an den freien Kern delegiert; die Hülle bleibt gleich groß wie heute die Schnittstelle (ca. 10 Methoden).
4. **Textsatz.** Ohne `QTextLayout` fehlen Formen (HarfBuzz), Zeilenumbruch, Bidi, Kerning; der Auftrag schließt eine eigene Font-Engine aus. Bis eine Implementierung (HarfBuzz/FreeType) vorliegt, bleibt Qt die
   einzige Implementierung der Schnittstelle `TextLayoutEngine`; der Kern wäre dann entkoppelt, aber nicht ohne Qt lauffähig.
5. **Formatvielfalt.** `QTextCharFormat`/`QTextBlockFormat` tragen über 100 benutzerdefinierte Eigenschaften (Effekte, Notenmarken, Änderungen, Abschnittsdaten …). Das Modell muss alle erhalten
   (Auftrag: kein Formatverlust) — dafür zuerst eine vollständige Liste aus `editor/dokument/zusatz.py` und den `P_*`/`B_*`-Konstanten.

Empfehlung: Phase 4 mit einer **Rundlauf-Prüfung** beginnen (Qt-Dokument → Modell → Qt-Dokument, Vergleich von Text, Formaten, Tabellen), an den echten Dateien der Prüfdatenbank, bevor Import/Export umgestellt werden.

## Phase 4: Dokumentenmodell (Stand 2026-11-12)

- **Modell** (`core/document/`): `Document` → `Section` (Beginn, `PageSettings`) → `Paragraph` (Format, `TextRun`/`Image`), `Table` (`TableRow`, `TableCell` mit Spannen und Inhalt), `Frame`, `ListFormat`,
  `Footnote`. Formate sind benannte Eigenschaften (`FontWeight`, `BlockAlignment`, …, eigene als `user:<Zahl>`) mit neutralen Werten (`Color`, `Brush`, `Length`, `TabStop`, Tupel).
  Das Modell hält jede Eigenschaft, die ein Qt-Format trägt; fachliche Namen (fett, Größe) folgen später.
- **Brücke** (`adapter/qt/dokument.py`): `document_from_qt(doc, page)`, `document_to_qt(modell)`, `vergleichen(a, b)`. Abschnittsmarken (`B_ABSCHNITT`) werden zu `Section`, Listen zu `list_id`,
  Bilder zu `Image` (Rasterfassung als PNG, dazu Originalbytes und Ersatzgrafik aus `bilddaten`, bleiben also für das Speichern erhalten).
- **Grenzen, die ausdrücklich Fehler melden (`NichtUebertragbar`) statt zu verlieren:** Pinsel mit Farbverlauf oder Bildmuster, OpenType-Schriftmerkmale (`FontFeatures`), unbekannte Werttypen.
- **PySide-Eigenheit:** `QTextFormat.properties()` stürzt ab, wenn das Format die Zuordnung `FontFeatures` (aus `QTextCharFormat.setFont`, zum Beispiel in `deckblatt.py`) trägt. Der Adapter kopiert das
  Format ohne diese (leere) Zuordnung. Leere Zuordnungen (Schriftmerkmale, Variationsachsen) gelten als Standardwert und werden nicht übernommen.
- **Noch Qt in der Hülle:** `Section.page` ist `PageSettings`; dessen Liste `bilder` hält `QImage` (Bilder in Kopf-/Fußzeilen). `Footnote` ist angelegt, wird aber vom Adapter noch nicht befüllt
  (die Noten liegen heute im Editor, die Marken stehen als `user:`-Eigenschaft im Text und gehen verlustfrei mit).
- **Rundlauf Qt → Modell → Qt** an 76 Dateien der Prüfdatenbank (DOCX, ODT, RTF, Eigene Tests, Microsoft-Originale, Webkorpus, LibreOffice): 75 gleich in Text, Absatz-, Zeichen-, Listen-, Tabellen-,
  Zellen-, Rahmen- und Bildformaten sowie Bildpunkten; 1 Datei lässt der ODT-Leser aus Sicherheitsgründen nicht zu (kein Befund des Modells).

## Phase 5: DOCX-Import (Stand 2026-11-12)

**5a, erledigt:** `dienste/modell_laden.py` mit `lade_modell(path, kennwort=None) → ModellGeladen(document, page, meta, report)` für DOCX, DOTX, DOCM, ODT, FODT, RTF und TXT.
Der Leser läuft unverändert (`docx_leser.read_docx` schreibt in ein `QTextDocument`, meldet Nichtübernommenes im `IOReport`); die Brücke `adapter/qt/dokument.py` macht daraus das Modell.
Code, der den Inhalt Qt-frei braucht, ruft nur diese Funktion; kein bestehender Aufruf ist geändert. Prüfung: `tests/architektur/test_dokumentmodell.py::test_docx_als_modell_laden`
(Modell → Qt-Dokument gleicht dem direkt gelesenen). Der Rundlauf an 75 Dateien aus Phase 4 deckt DOCX, ODT und RTF ab.

**5b, nicht begonnen:** Der Leser soll selbst ins Modell schreiben, ohne den Umweg über `QTextDocument`. Der Umfang ist gemessen: `docx_leser.py` und `docx_teile/lesen_*.py` haben 3533 Zeilen;
direkt am Cursor hängen etwa 40 Aufrufe (`insertText`, `insertBlock`, `setBlockFormat`, `setBlockCharFormat`, `mergeCharFormat`, `insertImage`, `addResource`, Tabellen- und Rahmenanlage) in
`lesen_absatz.py` (13), `lesen_objekte.py` (8), `lesen_runs.py` (7), `lesen_tabellen.py` (1). Das schwere Stück sind die **Formate**: der Leser baut sie mit den Settern von `QTextCharFormat`,
`QTextBlockFormat`, `QTextTableFormat` (Schrift, Abstände, Einzüge, Zeilenabstand, Rahmen …), und das Modell kennt statt der Setter nur benannte Eigenschaften. Ein Qt-freier Leser braucht deshalb zuerst
eine Zuordnung Fachwert → Eigenschaftsname (die fachliche Benennung aus Phase 4) und einen `DokumentSchreiber` mit zwei Umsetzungen (Qt-Cursor wie heute, Modell-Baumeister). Wegen der
Regel „keine Zwischenlösung, die Formate verliert“ ist dieser Schritt nicht nebenbei gemacht worden; Reihenfolge-Vorschlag: (1) Schnittstelle `DokumentSchreiber` mit der Qt-Umsetzung, Leser darauf
umstellen, Rundlauf gegen die Prüfdatenbank; (2) Baumeister für das Modell; (3) Formate Stück für Stück auf Eigenschaftsnamen.

### 5b: Befund (2026-11-12) — der geplante `DokumentSchreiber` trägt nicht

Der Plan oben ging von einer Schnittstelle mit zwei Umsetzungen (Qt-Cursor, Modell-Baumeister) aus. Die Untersuchung der Aufrufstellen zeigt, dass das nicht reicht:

1. **Der Leser arbeitet mit Textpositionen und dem fertigen Dokument.** `cursor.position()`/`setPosition` merken Stellen für Textmarken (`_lz_pos`, `lesen_absatz.py`), das zuletzt eingefügte Stück für XE-Felder (`_letzter`)
   und setzen schwebende Bilder in den Text (`lesen_objekte.py`: `schwebend_einfuegen(self.doc, cursor.block().position(), …)`, `absatz_nach_rahmen`). `lesen_absatz.py` wählt einen Bereich mit `KeepAnchor` und
   mischt Zeichenformate nachträglich. `docx_leser.py`, `lesen_seite.py`, `lesen_tabellen.py`, `lesen_textfelder.py` greifen mit `self.doc.…` auf das Dokument zu; `_ketten_bereinigen` und die Textfelder
   gehen nach dem Lesen über alle Absätze. Tabellenzeilenhöhen brauchen Schriftmaße (`QFontMetricsF` über das Dokument).
2. Ein Baumeister, der dieselben Aufrufe annimmt, müsste ein kleines `QTextDocument` nachbauen (Positionen, Auswahl, nachträgliches Formatieren). Das wäre eine zweite Textengine neben Qt.
3. Eine dünne Qt-Umsetzung allein (nur Umbenennung von `QTextCursor`) bringt keinen Nutzen, solange es keine zweite Umsetzung gibt.

**Neuer Plan für Phase 5b** (zweistufig statt Cursor-Nachbau): ein **neuer** Leser `docx_modell_leser`, der python-docx-Elemente in `core.document` übersetzt, ohne Positionen — Textmarken und XE-Felder als Marken am
Textstück, schwebende Bilder als `Frame`/Bild mit Umfluss-Eigenschaften, Tabellenhöhen erst im Layout (Phase 6/7) statt im Leser. Der alte Leser bleibt, bis der neue auf den Dateien der Prüfdatenbank dieselben Ergebnisse
liefert (Vergleich mit `adapter/qt/dokument.vergleichen` über `document_to_qt`). Reihenfolge nach Anteil an den Prüfdateien: Absätze und Textstücke, Listen, Tabellen, Seiteneinrichtung und Abschnitte, Bilder, Rahmen und Formen,
Felder und Verweise. Der Umfang ist der des heutigen Lesers (rund 3500 Zeilen); jedes Stück wird einzeln gegen den Bestand geprüft, keines ersetzt den alten Weg vor dem Vergleich.
Zwei Voraussetzungen aus den anderen Phasen: die fachliche Benennung der Formateigenschaften (Phase 4, Folgearbeit) und eine Qt-freie Schriftmessung (Phase 6) für alles, was heute im Leser Zeilenhöhen misst.

## Phase 5b: Stand (2026-11-12)

- **Modell-Leser** (`dienste/docx_modell_leser.py`): liest DOCX in `core.document`, ohne `QTextDocument` als Zwischenschritt. Schreibmarke `ModellCursor`, Tabellen über eine
  Hilfstabelle für Formate und Verbinden, Bilder als `Image`, Abschnittsmarken, Listen.
- **Rückfall:** `NichtImModell` wird ausgelöst bei Zeilenhöhen nach Textmaß (`cell.begin`), bei Feldern mit nachträglicher Formatierung (`feld`) und bei Positionen (`block.position`).
  Dann liest `docx_leser.read_docx` wie bisher.
- **Import:** `datei_dienst._docx_lesen` versucht zuerst den Modell-Leser und wandelt das Ergebnis mit `document_to_qt` in ein `QTextDocument`; sonst der alte Leser.
- **Prüfung:** 104 Prüfdateien: 61 identisch in Text, Formaten, Seite, Metadaten und Bericht, 43 über den Rückfall. Gezielte Tests: `test_docx_hin_und_zurueck`, `test_lo_dokument`,
  `test_docx_zeile_textfeld`, `tests/architektur` grün.
- **Offen:** Zeilenhöhen nach Textmaß und Positionen brauchen den Textsatz aus Phase 6; Felder mit Nachformatierung brauchen eine Nachbildung im Modell.
  Der alte Leser bleibt, bis beides im Modell steht.

## Phasen 6 bis 10: Stand (2026-11-12)

- **Phase 6:** `core/textlayout/engine.py` mit `FontSpec`, `FontMetrics`, `GlyphPosition`, `LineBox` und der Schnittstelle `TextLayoutEngine` (`font_metrics`, `measure_text`, `shape_text`,
  `layout_paragraph`). Die Basisklasse meldet jede fehlende Umsetzung. `adapter/qt/textlayout.py` setzt sie mit `QFontMetricsF` und `QTextLayout` um. Eine Qt-freie Umsetzung fehlt.
- **Phase 7 (nicht begonnen):** `editor/layout/seitenlauf.py` (1188 Zeilen) ist eine `QAbstractTextDocumentLayout`-Unterklasse und benutzt `QTextDocument`, `QTextBlock`, `QTextLayout`,
  `QRectF`, `QPointF`, `QSizeF`, `QPainter`-nahe Typen. Die Umstellung braucht zuerst: (a) den Seitenlauf auf `core.document` und `core.textlayout` schreiben, (b) die Qt-Hülle als
  Adapter herausziehen, (c) den Cursor-Hit-Test im Adapter lassen. Das ist ein eigenes Vorhaben mit der Bedingung „keine Funktion verlieren“ (Vergleich über das Messnetz).
- **Phase 8:** `core/rendering/backend.py` mit `RenderBackend` (`draw_text`, `draw_rect`, `draw_image`, `draw_line`) und `Style`. `adapter/qt/rendering.py` setzt es auf `QPainter` um.
  In `seiten_aufteilung.py` laufen bisher die Spaltenlinien und die Änderungsbalken über das Backend (`_spaltenlinien_zeichnen`, `_aenderungsbalken`, `_balken_blatt`). Kopf- und Fußzeilen ohne Effekte (auch mit Hervorheben) laufen über `RenderBackend.draw_text_box`/`text_bounds` (`_draw_hf` in `seiten_aufteilung_deko.py`). Effekte, Textläufe, Text, Formen und Bilder rufen `QPainter` noch direkt auf; das Backend deckt dafür Pinsel, Schriften und Pfade noch nicht ab.
- **Phase 9:** Adapter vorhanden für Geometrie, Dokument (`adapter/qt/dokument.py`), Textsatz und Zeichnen. Die Oberfläche (`oberflaeche/`, 212 Dateien mit Qt-Importen) nutzt sie noch nicht.
- **Phase 5b:** siehe oben; der Modell-Leser ist an den DOCX-Import angeschlossen. 68 von 104 Prüfdateien identisch, 36 über den Rückfall (Zeilenhöhen nach Textmaß,
  Positionen für schwebende Bilder und Textmarken, Felder außerhalb der XE-Stichworte).
- **Wächter:** `tests/architektur/test_core_ohne_qt.py` prüft, dass `core/` keine Qt-Importe und keine alten Schichten importiert. Alle Module in `core/` (geometry, document, textlayout, rendering) bestehen ihn.

## Stand nach dem Ausführungsauftrag (2026-11-12, später Teil)

**Aufgabenliste** (nur erledigt, wenn umgesetzt, eingebunden und geprüft; Prüfung nennt, womit):

| Paket | Stand | Prüfung |
|---|---|---|
| Rendering-Schnittstelle `core/rendering` | erledigt: Linien, Rechtecke, Ellipsen, Pfade (auch Vereinigung), Verläufe (linear, rund), Textfelder, Bilder, Ausschnitt (Rechteck, Ellipse), Deckkraft, Verschiebung, Drehung, Glättung, Strichart, Eckenart | Pixelvergleich alt/neu: Spalten, Seitenfarbe, Zeilennummern, Druckmarken, Kunstrahmen (5), Wasserzeichen (5), Deckblätter (17 × 3), Katalogformen (81 × 2) |
| Zeichnen über das Backend eingebunden | `seiten_aufteilung*.py`, `seitenrahmen.py`, `wasserzeichen.py`, `deckblatt.py`, freie Bilder (`freie_bilder.bild_zeichnen` ohne Effekte), Formen (`einfuegen.form_bild` für Katalog-, Frei- und Anpassungsformen) | wie oben; Farbverläufe weichen höchstens um 1 von 255 ab |
| Textsatz ohne Qt `core/textlayout` | erledigt: `HarfBuzzEngine` (FreeType-Maße, HarfBuzz-Formen, Zeilenumbruch), `fontdb.py` (Schriftsuche ohne Fremdprogramme), `paragraph.py` (Läufe, Bilder in der Zeile, Einzüge, links/rechts/zentriert/Blocksatz, Zeilenabstand, Cursorstelle, Treffertest) | `tests/architektur/test_textsatz_hb.py`; Maße und Umbrüche gleich der Qt-Umsetzung (Abweichung der Breite unter 0,5 %) |
| Seitenumbruch ohne Qt `core/layout` | erledigt für Abschnitte, Spalten, Absätze, Tabellen (Spaltenbreiten, verbundene Zellen), Bilder in der Zeile, Rahmen als Block; **nicht berücksichtigt** (in `Ergebnis.hinweise`): Fußnoten, Textumfluss, Absatzregeln, Zeilennummern, Kopf-/Fußzeilen-Platz | `tests/architektur/test_seitenumbruch_modell.py`; Vergleich mit dem Seitenlauf an der Prüfdatenbank: `werkzeuge/pruefungen/seitenumbruch_modell_vergleich.py` (Seitenzahl, siehe unten) |
| Bilder und Formen im Modell `core/document/objekte.py` | erledigt: `ImageObject`, `ShapeObject`, `VectorPath`, `FillStyle`, `StrokeStyle`, `Shadow`, `Transform`, `Anchor`, `WrapSettings`; verlustfreie Umwandlung zum gespeicherten JSON (`aus_angabe`/`zu_angabe`, `aus_parametern`/`zu_parametern`) | `test_objekte_modell.py` |
| Bildformate `core/document/bildformat.py` | erledigt: PNG, JPEG, GIF, BMP, TIFF, WebP, SVG, EMF/WMF erkennen, Größe aus dem Kopf, Seitenverhältnis; `bilddaten.py` nutzt es | `test_bilddaten.py`, `test_objekte_modell.py` |
| Lage von Objekten im Layoutkern | erledigt: `core/layout/objekte.objekt_rechteck`; `freie_bilder.rechteck` ruft sie | gleiche Formel, Test `test_lage_auf_dem_blatt` |
| Bildplatzhalter | erledigt: fehlende oder unlesbare Bilder im DOCX-Import werden zum Platzhalter in der vorgesehenen Größe (statt verworfen), Hinweis im Bericht | `tests/dokument/test_bild_platzhalter.py` |
| Fußnoten, Textumfluss, Absatzregeln, Zeilennummern, Kopfzeilen-Versatz im Qt-freien Seitenumbruch | erledigt (`core/layout/seitenumbruch.py`); Textumfluss und Rahmen vergleichen mit dem Seitenlauf bei den geprüften Dateien seitengleich | `test_seitenumbruch_modell.py` |
| Effekte, Muster-/Textur-/Bildfüllung, SVG/EMF, Texteffekte im Backend | erledigt als Backend-Operationen (`draw_effects_behind`, `apply_image_effects`, `draw_text_effects`, `draw_shadow`, `PatternFill`, `TextureFill`, `ImageFill`, Vektorbilder in `draw_image`); die Qt-Umsetzung nutzt die vorhandenen Effektbausteine; freie Bilder und Kopf-/Fußzeilen-Effekte laufen darüber | Pixelvergleich alt/neu |
| Bilddaten im Modell | **Fehler behoben**: frei positionierte Bilder gingen beim DOCX-Import über den Modell-Leser verloren; `Document.media` trägt sie jetzt mit | `test_frei_positioniertes_bild_wandert_mit_dem_modell`, DOCX/ODT-Rundlauf von Inline-, freiem und Kopfzeilenbild geprüft; RTF meldet, was es nicht speichert |
| Seitenlauf (`editor/layout/seitenlauf.py`) ohne Qt | **offen**: er ist die `QAbstractTextDocumentLayout` des `QTextDocument` und bleibt Qt-Hülle; Blatt/Platz/Ergebnis sind Qt-frei (`seitenplatz.py`) | — |
| DOCX-Import ohne Umweg über Qt | **teilweise**: Modell-Leser mit Rückfall; Zeilenhöhen mit dem Qt-freien Textsatz und schwebende Bilder sind jetzt im Modell; Rückfall bleibt bei verschachtelten Tabellen und einigen Formaten (Umriss-Stift, Farbverlauf als Hintergrund). Von 120 Prüfdateien liest der Modell-Leser 114 selbst | `werkzeuge/pruefungen/docx_modellleser_vergleich.py` |
| Oberfläche nur über Adapter | **offen**: 212 Dateien in `oberflaeche/` benutzen Qt-Dokumentklassen direkt; Editor, Cursor, Auswahl, Einfügen, Löschen und Formatieren arbeiten auf `QTextDocument` | — |
| WordArt, SmartArt, Diagramme | **offen**: werden von Qt-Code (`einfuegen.wordart_vorlage_bild`, `smartart_zeichnen.py`, `diagramme/`) in Bilder gezeichnet; das Dokument speichert Bild und Parameter | — |
| DOCX-Export aus dem Objektmodell | **offen**: der Schreiber liest weiter das `QTextDocument`; die Bilder bleiben dabei erhalten (Rundlauf-Tests), werden aber nicht aus `ImageObject` geschrieben | — |

**Messung** (2026-11-12, `werkzeuge/pruefungen/seitenumbruch_modell_vergleich.py`, Prüfdatenbank): von 166 lesbaren Dateien (ohne 8 absichtlich kaputte und 6 Manifest-Listen) hat der Qt-freie Umbruch bei **124 dieselbe Seitenzahl** wie der Seitenlauf, bei **153 höchstens 10 % Abweichung**.
Ursachen der Abweichungen, soweit untersucht: (1) Schriften, die auf dem Rechner fehlen — Qt ersetzt sie über Fontconfig, die Qt-freie Schriftsuche über eine feste Ersatztabelle (`fontdb.ERSATZ`), die Zeilenhöhen weichen dann ab; (2) Textumfluss um schwebende Bilder, Fußnoten, Absatzregeln (Witwen/Waisen, Zusammenhalten) und Tabellenrahmen sind im Qt-freien Umbruch nicht abgebildet. Gleich geblieben ist die Zeilenlogik: Umbrüche und Schriftmaße gleichen der Qt-Umsetzung, wo die Schrift installiert ist.

**Dringender Hinweis zur Fertigstellung:** Der Dokumentenkern `core/` ist frei von Qt (Wächtertest grün). Die Qt-Entkopplung der gesamten Anwendung ist **nicht** abgeschlossen: Seitenlauf, Editor, Schreiber und Oberfläche hängen weiter an `QTextDocument`.

## Stand Ende der Bausitzung (2026-11-12, nach Aufgabenliste oben)

**Neu gebaut und eingebunden (Dateien):**

| Baustein | Dateien | Eingebunden in |
|---|---|---|
| Bearbeiten ohne Qt: Schreibmarke, Auswahl, Einfügen, Löschen, Zeichen-/Absatzformat, Bild einfügen, Rückgängig/Wiederholen, Gruppen | `core/editing/sitzung.py` | über den Spiegel |
| Spiegel Textdokument ↔ Sitzung (Modell bleibt gleich der Ansicht, Änderungen laufen Oberfläche → Adapter → Kern → Ansicht) | `adapter/qt/bearbeitung.py` | `DocumentEditor`: alle Zeichenformat-Befehle (`_merge`), alle Absatzformat-Befehle (`_block_merge`), Ersetzen (`text_ersetzen`: Rechtschreibung, Suchen/Ersetzen, Autokorrektur), Tabelle einfügen (`insert_table`) |
| Seiten aus dem Modell: Modell → `core.layout.umbrechen` → `core.rendering.seite` → Backend | `core/rendering/seite.py`, `adapter/qt/seitenbild.py` | Vorlagenkacheln (`vorlagen_galerie._blatt_bild`) |
| Tabellenzellen als Zeichenanweisungen | `core/rendering/tabelle.py` | `Seitenlauf._tabellen_zeichnen` |
| Listenzeichen über das Backend | `Seitenlauf._listenzeichen` | Seitenlauf (pixelgleich) |
| Pinsel mit Verlauf, Bildmuster, Stift als Modellwerte | `core/document/values.py`, `adapter/qt/dokument.py` | DOCX-Import (kein Rückfall mehr bei Textkontur und Verlaufshintergrund) |
| Modell speichern | `dienste/modell_speichern.py` | DOCX/ODT/RTF/TXT |
| Verschachtelte Tabellen im Modell-Leser | `dienste/docx_modell_leser.py` (`_zelle_mit_tabelle`) | DOCX-Import |
| Bilddaten im Modell (`Document.media`) | `core/document/model.py`, Brücke | DOCX-Import (frei positionierte Bilder gingen vorher verloren) |

**Fertigstellungsstatus:** Der Kern (`core/`) ist frei von Qt; Bearbeitung, Seitenumbruch, Rendering und Bilder/Formen laufen über Modell und Backend. **Nicht fertig:** Tippen, Einfügen aus der Zwischenablage, Tabellen- und Bildbefehle, Auswahlverhalten und die Anzeige des Editors (`QTextEdit` mit dem Seitenlauf) arbeiten weiter direkt am `QTextDocument`; der Seitenlauf ist weiter die Qt-Hülle. Das Seitenbild aus dem Modell kennt Kopf-/Fußzeile, Seitenrahmen und Wasserzeichen nur über die Qt-Bausteine des Editors (`seitenschmuck`, `_kopf_fuss_zeichnen`).

**Nächster Schritt:** die übrigen Befehle der Reiter „Tabelle“ (Zeilen/Spalten, Verbinden, Zellformat) und „Einfügen“ (Bild, Form) wie `insert_table` über `ModellSpiegel` führen (Sitzung um Tabellen- und Rahmenoperationen erweitern), danach das Tippen (`keyPressEvent`/`inputMethodEvent`) über `ModellSpiegel.einfuegen`; zuletzt den Seitenlauf auf `core.layout` stützen.


### Nachtrag (später Teil der Bausitzung)

| Baustein | Dateien | Eingebunden in |
|---|---|---|
| Tabellenstruktur im Kern (Zeilen/Spalten einfügen und löschen, Zellen verbinden, mit verbundenen Zellen) | `core/editing/tabelle.py`, `Sitzung.tabelle_aendern`, `Sitzung.zellen_verbinden` | Tabellentools (`kern/befehle/kontextreiter/tabellen.py`) über `ModellSpiegel` |
| Freie Bilder einfügen, Listen anlegen/aufheben, Tippen | `Sitzung.freies_bild_einfuegen`, `liste_anlegen`, `liste_entfernen`, `ModellSpiegel.tippen` | `frei_objekt.bild_einfuegen` (gemeinsamer Weg aller freien Bilder), `toggle_list`, `keyPressEvent` (getippter Text: ein Rückgängig-Schritt wie bei Qt) |
| Formatvorlagen auf Absätze | `editor_stilformat._stil_auf_block` | Absatz- und Zeichenformat laufen über den Spiegel |
| Umbruchregeln, Zeilenhöhe: eine Stelle | `core/layout/regeln.py`, `core/textlayout/paragraph.zeilenhoehe` | Qt-freier Seitenumbruch **und** Seitenlauf |
| Kopf-/Fußzeile, Seitenschmuck, Wasserzeichen, Seitenrahmen, Linienarten | `core/rendering/kopffuss.py`, `seitenschmuck.py`, `wasserzeichen.py`, `seitenrahmen.py`, `linien.py` | Modell-Seitenbild und Editor (Qt-Hüllen rufen den Kern); 19 Linienarten pixelgleich |
| Zeilennummern im Modell-Seitenbild | `core/rendering/seite.zeichne_zeilennummern` | `adapter/qt/seitenbild.py` |

| Löschen (Rückschritt, Entf, Auswahl), Zellen teilen, Zellformat und Tabellenformat | `ModellSpiegel.entfernen`, `Sitzung.zelle_teilen`, `zellformat`, `tabellenformat` | `keyPressEvent`, Tabellentools |
| Modell als PDF | `adapter/qt/pdf_modell.py`, `dienste/modell_speichern.py` | Speichern aus dem Modell (`.pdf`) |

Weiterhin direkt am `QTextDocument`: Auswahl und Cursorbewegung, Löschen über Absatz- und Zellgrenzen, Zwischenablage (fremder Inhalt), Eingabemethoden und Überschreibmodus, WordArt/SmartArt/Diagramme, der Seitenlauf selbst und die Anzeige. Ab 1500 Absätzen führen die Befehle das Modell nicht nach (Schwelle `GROSS` in `adapter/qt/bearbeitung.py`), weil der Neuaufbau nach Änderungen der Oberfläche sonst zu langsam wäre; ein Spiegel mit schrittweisem Abgleich ist der nächste Schritt dafür.

### Nachtrag 2 (nach dem Aufräumen der Versionsverwaltung)

| Baustein | Dateien | Eingebunden in |
|---|---|---|
| Ausschneiden und Einfügen von reinem Text über Modell und Sitzung | `ModellSpiegel.loeschen/ersetzen`, `editor_schreibhilfe.cut`, `editor_einfuegen._einfuegen_mit` | Strg+X, Einfügen „Nur Text“ und Einfügen ohne Formatierung |
| WordArt-Vorlagen ohne Qt | `core/rendering/wordart.py`, Backend-Operation `draw_text_path` | `einfuegen.wordart_vorlage_bild` (15 Stile pixelgleich) |
| Cursor/Auswahl zwischen Qt und Sitzung | `ModellSpiegel.cursor_uebernehmen/cursor_setzen` | Sitzung (Navigation und Auswahl im Modell) |
| Doppelte Konstanten entfernt | Fußnotenmaße (`core/layout/seitenumbruch.py`), Mindestbreite neben Rahmen (`core/textlayout/paragraph.py`) | `editor/seite/fussnoten.py`, `editor/layout/seitenplatz.py` |
| Zwei alte Tests | `test_seitenfluss_*` prüfen die Qt-Anordnung (``seitenfluss.py``) und wählen sie jetzt ausdrücklich | `tests/oberflaeche/test_baukasten.py` |

**Bleibt Qt (bewusste Grenze):** Auswahl und Cursorbewegung der Ansicht (`QTextCursor` ist die Quelle, die Sitzung übernimmt sie), Einfügen von Inhalten mit Formatierung aus fremden Programmen (Ausnahme der Projektregel „Kein HTML“), Eingabemethoden, SmartArt (`smartart_zeichnen.py`, 739 Zeilen Qt-Zeichnen in Bilder) und Diagramme, der Seitenlauf als `QAbstractTextDocumentLayout` des Editors.

### Befund: Geometrie der Ansicht gegen den Kern-Seitenumbruch (SampleDoc.docx)

Der Editor fragt pro Absatz das Rechteck beim Seitenlauf ab (`Seitenlauf.blockBoundingRect` aus `erg.rechtecke`). Der Kern-Seitenumbruch (`core/layout`) liefert für dieselben Absätze andere y-Werte:

- Seite 1: Der Kern liegt um rund 96–100 px über Qt, weil er den oberen Seitenrand in den Rechtecken mitführt, Qt nicht.
- Ab Seite 2 kommt ein zweiter, mit dem Blattabstand wachsender Versatz dazu.

Eine Umstellung der Ansicht auf den Kern würde deshalb jede Seite verschieben. Vorher muss der Kern das Blatt wie der Seitenlauf in Blattkoordinaten (mit Blattabstand und ohne Randversatz in den Rechtecken) liefern; erst dann ist ein Pixelvergleich sinnvoll.

**Nachtrag:** Der Kern-Seitenumbruch setzt jede Seite jetzt mit ihrer Blattoberkante (`Seite.oben`, Blattabstand wie im Seitenlauf). Die Kern-Rechtecke der Folgeseiten stimmen mit dem Seitenlauf überein (Seite 2 beginnt bei 96 px im Blatt). Die verbleibende Abweichung zu den Qt-Werten kommt aus einer anderen Blattbasis der Ansicht, nicht aus dem Umbruch. Damit ist die Geometrie vergleichbar; die Ansicht selbst ist noch nicht umgestellt.

### Befund: Zeilenhöhen Kern gegen Seitenlauf (0013bcb8)

Bei 4 von 5 geprüften Dokumenten stimmt die Seitenzahl des Kern-Umbruchs mit dem Seitenlauf überein. Bei 0013bcb8 erzeugt der Kern im letzten Abschnitt zwei Seiten mehr, weil er die Zeilen höher setzt (13 px gegen 9 bis 11 px an derselben Stelle). Ursache ist die Zeilenhöhe der Schrift und des Zeilenabstands, nicht die Seitenlogik. Die Ansicht ist deshalb noch nicht auf den Kern umgestellt; nächster Schritt: Zeilenhöhen im Textsatz an die Qt-Werte angleichen (ganzzahlige Zeilenhöhen, Zeilenabstand wie `QTextBlockFormat`).

### Nachtrag 3 (2026-11-12): Kern-Seitenumbruch und Seitenbild erweitert

| Baustein | Dateien | Wirkt in |
|---|---|---|
| Tabstopps (links, rechts, zentriert, Standardabstand des Dokuments, hängender Einzug als Stopp) | `core/textlayout/paragraph.py` (`absatz_setzen(tabs, tab_abstand)`), `core/layout/eigenschaften.tabstopps` | Kern-Seitenumbruch, Modell-Seitenbild, Modell-PDF |
| Tabellen wie im Seitenlauf: Tabellenbreite und -ausrichtung, Außenrand, Rahmenstärke, Zellabstand je Seite, senkrechte Ausrichtung, Mindesthöhe der Zeile, wiederholte Kopfzeilen (`Platz.kopie`), verschachtelte Tabellen mit ihren Zellen | `core/layout/seitenumbruch.py` (`tabelle`, `spaltenbreiten`, `tabellenbreite`) | wie oben |
| Tabellenzeile höher als eine Seite: wird zwischen ihren Textzeilen geteilt (der Seitenlauf kann das nicht) | `_Fluss.zeile_teilen` | wie oben |
| Rahmen als Block mit Rand, Rahmenstrich, Innenabstand, Füllung, fester Breite/Höhe | `_Fluss.rahmen`, `core/rendering/tabelle.rahmen_anweisungen` | wie oben |
| Endnoten am Dokumentende (kleine römische Nummern, fließen über Seiten), Trennstrich über Fuß- und Endnoten (`notenlinie`) | `_Fluss.endnoten_setzen`, `core/rendering/seite.py` | wie oben |
| Absatzhintergrund, hoch-/tiefgestellt, Schreibweise (groß, klein, Wortanfänge), Laufweite, Wortabstand, Unterstreichungsart und -farbe, Überstreichen | `core/layout/eigenschaften.py` (`stil`, `schreibweise`, `hintergrund`), `core/rendering/seite.zeichne_zeile` | wie oben |

Prüfung: `tests/architektur/test_seitenumbruch_modell.py` (13 Tests), `test_textsatz_hb.py`, `test_core_ohne_qt.py` grün. Seitenzahl Kern gegen Seitenlauf an den ersten 60 Prüfdateien
(`seitenumbruch_modell_vergleich.py --max 60`): vorher 53 gleich, jetzt 56, keine Datei schlechter. Nicht geprüft: das Aussehen der neuen Teile im Modell-Seitenbild (kein Bildvergleich).

**Offen im Kern:** Kapitälchen, Absatzrahmen, Füllzeichen an Tabstopps, Dezimal-Tabstopp, Blocksatz vor Tabulatoren. **Nächster Schritt:** die Ansicht des Editors auf den Kern stützen
(`LUNIVO_KERN_RECHTECKE` zum Standard machen: Tabellenzellen und Rahmen des Seitenlaufs aus `Ergebnis.seiten[*].plaetze`), danach der DOCX-Schreiber aus dem Modell.
