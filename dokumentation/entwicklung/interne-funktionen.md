# Interne Funktionen — Inventar

Vollständiges Inventar der Module, Klassen, Funktionen und Methoden von `src/lunivo_writer`. Erzeugt mit `werkzeuge/erstellung/inventar_bauen.py` aus dem Quelltext (`ast`, ohne Import); nicht von Hand ändern, sondern neu erzeugen. Die Beschreibung stammt aus der ersten Docstring-Zeile.

Stand: 633 Module, 647 Klassen, 7565 Funktionen und Methoden.

## Inhalt

- `(Wurzel)` — 3 Module
- `adapter` — 1 Module
- `adapter/qt` — 8 Module
- `core` — 1 Module
- `core/document` — 14 Module
- `core/editing` — 13 Module
- `core/geometry` — 6 Module
- `core/layout` — 18 Module
- `core/rendering` — 18 Module
- `core/textlayout` — 14 Module
- `dienste` — 43 Module
- `dienste/docx_teile` — 20 Module
- `dienste/integrationen` — 3 Module
- `dienste/rtf` — 8 Module
- `editor` — 1 Module
- `editor/diagramme` — 11 Module
- `editor/dokument` — 20 Module
- `editor/layout` — 4 Module
- `editor/objekte` — 18 Module
- `editor/seite` — 20 Module
- `editor/tabelle` — 5 Module
- `editor/text` — 22 Module
- `kern` — 8 Module
- `kern/befehle` — 2 Module
- `kern/befehle/hauptreiter` — 17 Module
- `kern/befehle/kontextreiter` — 12 Module
- `ki` — 31 Module
- `korrektur` — 12 Module
- `modelle` — 4 Module
- `oberflaeche` — 7 Module
- `oberflaeche/band` — 13 Module
- `oberflaeche/band/reiter` — 12 Module
- `oberflaeche/baukasten` — 1 Module
- `oberflaeche/baukasten/basis` — 9 Module
- `oberflaeche/baukasten/chat` — 6 Module
- `oberflaeche/baukasten/diagramme` — 7 Module
- `oberflaeche/baukasten/dokument` — 16 Module
- `oberflaeche/baukasten/dropdown` — 14 Module
- `oberflaeche/baukasten/dropdown/auswahl` — 7 Module
- `oberflaeche/baukasten/dropdown/objektmenues` — 10 Module
- `oberflaeche/baukasten/felder` — 15 Module
- `oberflaeche/baukasten/formatierung` — 15 Module
- `oberflaeche/baukasten/geruest` — 12 Module
- `oberflaeche/baukasten/medien` — 11 Module
- `oberflaeche/baukasten/vorlagen` — 4 Module
- `oberflaeche/bauteile` — 8 Module
- `oberflaeche/dialoge` — 6 Module
- `oberflaeche/dialoge/einfuegen` — 9 Module
- `oberflaeche/dialoge/ki` — 5 Module
- `oberflaeche/dialoge/lesen_hilfe` — 5 Module
- `oberflaeche/dialoge/optionen_seiten` — 8 Module
- `oberflaeche/dialoge/sendungen` — 3 Module
- `oberflaeche/dialoge/verweise` — 3 Module
- `oberflaeche/dokument` — 1 Module
- `oberflaeche/dokument/ansicht` — 9 Module
- `oberflaeche/dokument/bearbeitung` — 8 Module
- `oberflaeche/dokument/dokumentfenster` — 5 Module
- `oberflaeche/dokument/kopffuss` — 4 Module
- `oberflaeche/dokument/tabelle` — 1 Module
- `oberflaeche/hauptfenster` — 20 Module
- `oberflaeche/kontext` — 7 Module
- `oberflaeche/seitenleiste` — 2 Module
- `oberflaeche/seitenleiste/panels` — 3 Module
- `oberflaeche/statusleiste` — 2 Module
- `plattform` — 8 Module

## `(Wurzel)`

### `__init__.py`

Lunivo Writer — native Textverarbeitung (Python 3, PySide6/Qt Widgets).


### `__main__.py`


### `app.py`

Einstieg: python -m lunivo_writer [Datei …]

- `main(argv)`

## `adapter`

### `adapter/__init__.py`

Adapter zwischen dem Qt-unabhängigen Kern (``core``) und der Qt-Oberfläche. Qt-Importe gehören hierher und in ``oberflaeche``, nie in ``core``.


## `adapter/qt`

### `adapter/qt/__init__.py`

Qt-Adapter: Umrechnung von Geometrie (``geometrie.py``); Dokument, Zeichnen und Auswahl folgen in den späteren Phasen.


### `adapter/qt/dokument.py`

Qt-Textdokument ↔ ``core.document.Document``: verlustfreie Umwandlung in beide Richtungen.

- **class `NichtUebertragbar`**(Exception) — Ein Wert oder Aufbau des Qt-Dokuments hat im Modell (noch) keine Entsprechung.
- `_name(i)`
- `_id(name)`
- `_wert(v, name)`
- `_verlauf(g)`
- `_verlauf_zurueck(v)`
- `_farbe(c)`
- `_zurueck(v)`
- `eigenschaften(fmt)` — Alle Eigenschaften eines Formats als {Name: neutraler Wert}.
- `_setzen(fmt, props)`
- `absatzformat_aus_qt(fmt, char_format, list_id, visible)` — Absatzformat samt unverändertem Qt-Eigenschaften-Bag und semantischen Ausrichtungs-, Abstands- und Einzugswerten lesen.
- `absatzformat_zu_qt_properties(fmt)` — Semantische Absatzwerte in den Qt-Eigenschafts-Bag schreiben; unbekannte Werte und Alignment-Bits bleiben erhalten.
- `zeichenformat_aus_qt(fmt)` — Zeichenformat samt verlustfreiem Qt-Eigenschaften-Bag und häufigen semantischen Feldern lesen.
- `zeichenformat_zu_qt_properties(fmt)` — Semantische Zeichenfelder in den verlustfreien Qt-Eigenschaften-Bag überführen; unbekannte Werte bleiben erhalten.
- **class `_Lesen`**
  - `__init__(doc)`
- `_bild_daten(doc, name)`
- `_png(img)`
- `_bild(cf, ctx, name)`
- `_bild_aus_modell(bild)` — Rasterbytes des Modells an der Qt-Grenze dekodieren, einschließlich Vektorquellen.
- `bild_aus_qimage(img)` — Ein ``QImage`` (mit seinem Original aus der Ablage) als Modell-``Image``.
- `seite_bilder_zu_qt(page)` — Qt-freie Bytes in Seiteneinrichtungen an der Oberfläche als Bilder bereitstellen.
- `bild_aus_format(cf, doc)` — Das Bild zu einem Bildformat (Name → Bild im Ressourcenspeicher von ``doc``) als Modell-``Image``.
- `_absatz(b, ctx, oberste_ebene)`
- `_inhalt(it, ctx, oberste_ebene, abschnitte)`
- `_tabelle(t, ctx)`
- `_enum(v)`
- `textoption_lesen(o)`
- `textoption_setzen(o, w)`
- `schnitte_bilden(oben, marken, page)` — Die obersten Blöcke an den Abschnittsmarken in ``Section`` teilen: ``marken`` = [(Zahl der Blöcke bis einschließlich des Marken-Absatzes, (Beginn, PageSettings des folgenden Abschnitts))].
- `medien_sammeln(modell, doc)` — Die Bilder, auf die Absätze nur mit einem Namen verweisen (frei positionierte Bilder und ihre Füllbilder, ``B_BILDANKER``), aus dem Ressourcenspeicher von ``doc``
- `document_from_qt(doc, page)` — Das Qt-Dokument als Modell. ``page``: Seiteneinrichtung des ersten Abschnitts (``PageSettings``); spätere Abschnitte kommen aus den Abschnittsmarken des Dokuments.
- **class `_Schreiben`**
  - `__init__(doc, modell)`
- `_runs_schreiben(cursor, p, ctx)`
- `_absatz_schreiben(cursor, p, ctx, frisch, marke)`
- `_inhalt_schreiben(cursor, bloecke, ctx, frisch, letzte_marke)`
- `document_to_qt(modell)` — Aus dem Modell ein neues ``QTextDocument`` (Abschnittsmarken, Listen, Tabellen, Rahmen und Bilder inbegriffen).
- `_signatur(it, doc, aus, tiefe)`
- `vergleichen(a, b)` — Unterschiede zweier Qt-Dokumente in Text, Formaten, Listen, Tabellen, Rahmen und Bildern (leer: gleich). Für die Rundlaufprüfung Qt → Modell → Qt.

### `adapter/qt/geometrie.py`

Qt-Geometrie ↔ ``core.geometry`` (alle Maße in Bildpunkten, y nach unten — wie bei Qt, also ohne Umrechnung der Einheit).

- `point_from_qt(p)` — ``QPointF`` oder ``QPoint`` → ``Point``.
- `point_to_qt(p)`
- `size_from_qt(s)` — ``QSizeF`` oder ``QSize`` → ``Size``.
- `size_to_qt(s)`
- `rect_from_qt(r)` — ``QRectF`` oder ``QRect`` → ``Rect``.
- `rect_to_qt(r)`
- `margins_from_qt(m)` — ``QMarginsF`` oder ``QMargins`` → ``Margins``.
- `margins_to_qt(m)`

### `adapter/qt/pdf_modell.py`

Das Dokumentenmodell als PDF: Modell → Qt-freier Seitenumbruch → Rendering-Backend auf einem ``QPdfWriter`` (Text bleibt Text, Vektoren bleiben Vektoren), ohne ``QTextDocument``.

- `modell_als_pdf(modell, pfad, titel, engine, *, autor, erste, letzte)` — Das Modell als PDF schreiben (jede Seite in der Größe ihrer Seiteneinrichtung), optional auf einen Seitenbereich begrenzt. → Zahl geschriebener Seiten.

### `adapter/qt/pfad.py`

Pfade zwischen Qt und dem Modell: ``QPainterPath`` → ``core.document.objekte.VectorPath`` (und zurück). Der Formenkatalog baut seine Umrisse mit Qt-Geometrie;

- `pfad_zu_vektor(pfad)`
- `vektor_zu_pfad(v)`

### `adapter/qt/rendering.py`

Qt-Backend der Rendering-Schnittstelle: setzt die Zeichenanweisungen auf einem ``QPainter`` um. Qt bleibt aus dem Kern draußen (``tests/architektur/test_core_ohne_qt.py``),

- `_farbe(style)`
- `_stufen(verlauf, g)`
- `_bild(data)` — Die Bilddatei als ``QImage``; dieselben Bytes liefern dasselbe Objekt (die Effekte merken sich ihre Ergebnisse je Bildobjekt).
- `_png(img)`
- `_pinsel(style, rect)` — Füllung des Stils: Verlauf, Muster, Textur oder Bild, wenn angegeben, sonst die Farbe.
- `_qfont(font)`
- `_ausgewaschen(img, grad)` — Das Bild um ``grad`` (0…1) zum Weiß hin aufgehellt, Durchsichtiges bleibt durchsichtig.
- `_qrect(r)`
- `_flags(align, wrap, valign)`
- **class `QtRenderBackend`**(RenderBackend)
  - `__init__(painter)`
  - `_stift(style)`
  - `draw_text(text, position, font, style)`
  - `draw_text_box(text, rect, font, style, align, wrap, valign)`
  - `text_bounds(text, rect, font, align, wrap)`
  - `draw_rect(rect, style)`
  - `draw_ellipse(center, rx, ry, style)`
  - `_pfade(ops)` — Teilpfade der Anweisungen: ein neues ``M``, ``E`` oder ``R`` beginnt einen eigenen Pfad.
  - `_vereinigt(teile, union)`
  - `draw_path(ops, style, antialias, union)`
  - `push_state(opacity, translate, rotate, clip, antialias, clip_ellipse, flip_h, flip_v)`
  - `pop_state()`
  - `draw_image(data, rect, smooth, wash, source_rect)`
  - `apply_image_effects(data, rect, ellipse, effects)`
  - `draw_effects_behind(data, rect, ellipse, effects)`
  - `draw_text_effects(text, font, origin, color, effects, contour, highlight, width, line_height, ascent, underline)`
  - `draw_text_path(text, font, origin, style)`
  - `draw_shadow(ops, color, blur, dx, dy)`
  - `draw_line(start, end, style)`

### `adapter/qt/seitenbild.py`

Seiten aus dem Dokumentenmodell als Bild: Modell → Qt-freier Seitenumbruch → Rendering-Backend (Qt) — ohne ``QTextDocument`` dazwischen.

- `_kopf_fuss(p, einr, n, nr_offset, total, grund, engine)` — Kopf- und Fußzeile: Qt-frei über ``core.rendering.kopffuss``; Zeilen mit Texteffekten zeichnet der Editor.
- `grundschrift(modell)` — Die Grundschrift des Modells als ``QFont`` (für Kopf-/Fußzeile und Zeilennummern).
- `seite_malen(p, modell, erg, i, engine, grund, darunter)` — Seite ``i`` des gesetzten Modells auf den Painter (Ursprung = obere linke Blattecke, 96 dpi): Seitenschmuck, Kopf-/Fußzeile, Inhalt, Zeilennummern.
- `seiten_bilder_modell(modell, faktor, engine, layout)` — Die Seiten des Modells einzeln als ``(Seitennummer, Bild, Seiteneinrichtung)`` liefern (``faktor`` 1.0 = 96 dpi).
- `seiten_aus_modell(modell, faktor, engine)` — Alle Seiten des Modells als Bilder (``faktor`` 1.0 = 96 dpi).

### `adapter/qt/textlayout.py`

Qt-Umsetzung von ``core.textlayout.TextLayoutEngine``: Schriftmaße aus ``QFontMetricsF``, Umbruch aus ``QTextLayout``.

- `_schrift(font)`
- **class `QtTextLayoutEngine`**(TextLayoutEngine)
  - `font_metrics(font)`
  - `measure_text(text, font)`
  - `shape_text(text, font)`
  - `layout_paragraph(text, font, width)`
- `_fontspec_aus(f)` — ``FontSpec`` zu einem ``QFont`` (Größe in Punkt, wie ``_schrift`` sie wieder in ganze Bildpunkte rechnet).

## `core`

### `core/__init__.py`

Qt-unabhängiger Kern von Lunivo: Geometrie, später Dokumentenmodell, Textlayout, Layout und Rendering.


## `core/document`

### `core/document/__init__.py`

Dokumentenmodell ohne Qt.


### `core/document/bildformat.py`

Bilddateien erkennen und vermessen, ohne Qt und ohne Bildbibliothek: Format am Dateikopf, Pixelgröße, Seitenverhältnis, gepackte Bilder (SVGZ, EMZ, WMZ).

- **class `BildFehler`**(ValueError) — Bilddatei nicht verwendbar; die Meldung ist für den Benutzer.
- `format_erkennen(blob)` — Das Bildformat am Dateikopf (nicht an der Endung); None, wenn es keines der bekannten ist.
- `entpacken(blob, grenze)` — gzip-gepackte Bilddaten (SVGZ, EMZ, WMZ) entpacken, höchstens ``grenze`` Bytes; andere Daten bleiben unverändert.
- `_jpeg(b)`
- `_tiff(b)`
- `_webp(b)`
- `_zahl(text)`
- `_svg(b)`
- `masse(blob)` — Pixelgröße (Vektorformate: Größe in Bildpunkten bei 96 dpi) aus dem Dateikopf; ``None``, wenn nicht lesbar.
- `seitenverhaeltnis(blob)` — Breite / Höhe des Bildes (aus dem Dateikopf).

### `core/document/dokument.py`

Das maßgebliche Dokumentmodell — reine Python-Daten, ohne Qt.

- **class `Position`**(NamedTuple)
- **class `Auswahl`**(NamedTuple)
  - `leer()`
- **class `Lauf`** — Ein Textstück mit einheitlichem Zeichenformat.
- **class `InlineObjekt`** — Ein Objekt, das wie ein Zeichen im Text steht (Bild, Form, Textfeld, Formel …). Zählt als eine Textstelle.
- **class `Absatz`**
  - `laenge()`
  - `text()`
- **class `Zelle`**
- **class `Tabelle`**
  - `zeilen()`
  - `spalten()`
  - `anker(zeile, spalte)` — Die Gitterstelle der sichtbaren Zelle, zu der (zeile, spalte) gehört.
  - `zelle(zeile, spalte)`
- **class `Rahmen`** — Ein Textrahmen im Fluss: enthält eigene Blöcke, hat Rahmen, Ränder, Breite und Umfluss. Wie eine Tabelle steht er immer hinter
- **class `Abschnitt`**
- **class `ListenEbene`**
- **class `ListenDefinition`**
- **class `Formatvorlage`**
- **class `Kommentar`**
- **class `Note`**
- **class `FreiesObjekt`** — Ein frei positioniertes Objekt, an einem Absatz verankert (Bild, Form, Textfeld …).
- **class `Dokument`**
  - `neue_id()`
  - `behaelter()` — Alle Blocklisten in Dokumentreihenfolge als (Besitzer, Liste); Besitzer ist ein Abschnitt, eine Zelle oder ein Rahmen.
  - `absaetze()` — Alle Absätze in Dokumentreihenfolge — der Inhalt einer Tabelle steht an der Stelle der Tabelle, Zelle für Zelle.
  - `tabellen()` — Alle Tabellen in Dokumentreihenfolge, eine äußere vor den Tabellen in ihren Zellen.
  - `finde(block_id)` — (Besitzer, Blockliste, Index, Block) zu einer Absatz-, Tabellen- oder Rahmen-Id; ``None``, wenn es sie nicht gibt.
  - `absatz(absatz_id)`
  - `tabelle(tabellen_id)`
  - `abschnitt_von(block_id)`
  - `reihenfolge()` — Absatz-Id → laufende Nummer in Dokumentreihenfolge (zum Vergleichen von Positionen).
  - `text()`
  - `anfang()`
  - `ende()`
- `_behaelter(besitzer)`
- `absaetze_in(bloecke)` — Alle Absätze einer Blockliste, auch die in Tabellen und Rahmen, in Dokumentreihenfolge.
- `_tabellen(bloecke)`
- `neues_dokument(seite)` — Ein leeres Dokument: ein Abschnitt mit einem leeren Absatz.
- `normalisiere(inhalte)` — Leere Läufe weglassen, benachbarte Läufe mit gleichem Format zusammenziehen.
- `teile(inhalte, versatz)` — Teilt eine Inhaltsliste an der Textstelle ``versatz`` in (davor, danach).
- `format_an(absatz, versatz)` — Das Zeichenformat, mit dem an dieser Stelle weitergeschrieben wird (das des Zeichens davor, am Absatzanfang das des ersten).

### `core/document/formate.py`

Formate des Dokumentmodells: Zeichen, Absatz, Tabelle, Zelle, Rahmen — als einfache Wörterbücher mit festem Schema.

- **class `FormatFehler`**(ValueError) — Ein Format enthält einen unbekannten Namen oder einen Wert der falschen Art.
- `pruefe(art, werte, *, leer_erlaubt)` — Prüft ``werte`` gegen das Schema ``art`` und gibt eine Kopie zurück. ``None`` ist nur mit ``leer_erlaubt`` zulässig
- `verschmelze(basis, aenderung)` — Neues Format: ``basis`` mit den Werten aus ``aenderung``; ein Wert ``None`` entfernt die Eigenschaft.

### `core/document/formatvorlagen.py`

Auflösen von Formatvorlagen (reine Funktionen über dem Dokumentmodell).

- `vorlagenkette(dokument, name)` — Die Vorlage und ihre Basisvorlagen, von der allgemeinsten zur genannten.
- `wirksames_absatzformat(dokument, absatz)` — Absatzformat mit allem, was die Formatvorlage des Absatzes vorgibt; eigene Angaben gewinnen.
- `wirksames_zeichenformat(dokument, absatz, zeichenformat)` — Zeichenformat eines Laufs: Absatzvorlage, dann Zeichenvorlage, dann die eigenen Angaben.
- `ueberschriftsebene(dokument, absatz)` — 1…9 für Überschriften, 0 für Fließtext.
- `eingebaute_vorlagen()` — Name → ``Formatvorlage`` für die eingebauten Stile; alle bauen auf „Standard“ auf, Überschriften folgt „Standard“.

### `core/document/kompatibilitaet.py`

Kompatibilitätsregeln für Dateiformate (zuerst DOCX): Welche Eigenschaft einer Datei das Modell abbildet, erhält oder nicht kennt. Ohne Qt.

- **class `Regel`**
- `_r(element, umgang, wirkt, quelle, modell, verlust)`
- `regel(element)` — Die Regel zu einem Pfad wie ``w:rPr/w:spacing``; ``None``, wenn keine Vorgabe dazu aufgenommen ist.
- `umgang(art, name)` — Wie mit dem Element ``name`` (ohne Namensraum, zum Beispiel ``spacing``) unter ``art`` (``rPr``, ``pPr``, ``tblPr``, ``trPr``, ``tcPr``, ``sectPr``) umgegangen wird; ``None``: unbekannt.
- `erhaltene_elemente(dok)` — Zählt die erhaltenen (nicht dargestellten) Elemente im Dokument: Name („rPr/spacing“) → Anzahl. Nur Elemente, deren Regel sichtbare Wirkung angibt oder die keine Regel haben.
- `hinweis_erhalten(dok)` — Ein Satz für den Importbericht über Eigenschaften, die erhalten, aber nicht dargestellt werden; ``None``, wenn es keine gibt.

### `core/document/listen.py`

Listen und Nummerierung: Zahlenarten und die Marken (Nummer oder Aufzählungszeichen) aller Listenabsätze.

- `nummer_text(stil, n)` — Die Zahl ``n`` in der Zahlenart ``stil`` (dezimal, klein, gross, roem_klein, roem_gross).
- `listenmarken(dokument)` — Absatz-Id → Text der Nummer oder des Aufzählungszeichens, für alle Listenabsätze in Dokumentreihenfolge.

### `core/document/model.py`

Das Dokumentenmodell ohne Qt: Abschnitte mit Seiteneinrichtung, Absätze mit Textstücken, Tabellen, Bilder, Rahmen, Fußnoten.

- **class `CharacterFormat`**
  - `get(name, default)`
- **class `ParagraphFormat`**
- **class `ListFormat`**
- **class `TextRun`**
- **class `Image`** — Ein Bild in der Zeile. ``raster_png`` enthält das decodierbare Raster oder, solange das Backend es direkt decodieren kann, die Originalbytes; ``original`` erhält die Quelle (JPEG, SVG, EMF usw.), falls vorhanden.
- **class `Paragraph`**
  - `text()`
- **class `TableCell`**
- **class `TableRow`**
- **class `Table`**
- **class `Frame`** — Ein Rahmen im Text (zum Beispiel ein schwebendes Bild mit Textumfluss).
- **class `PageLayout`**(Protocol) — Schreibgeschützte Seiteneinrichtung, die ein Dokumentabschnitt zum Umbruch bereitstellt.
  - `spaltenraster_px()`
- **class `Footnote`** — Fuß- oder Endnote: ``kind`` ist ``f`` oder ``e``; im Text steht die Marke als Eigenschaft des Textstücks.
- **class `Section`** — Ein Abschnitt: wie er beginnt und seine Qt-unabhängig konsumierte Seiteneinrichtung.
- **class `Document`**

### `core/document/objekte.py`

Bilder und dekorative Objekte im Dokumentenmodell, ohne Qt: Bildobjekt, Formobjekt, Vektorpfad, Füllung, Kontur, Schatten, Transformation, Verankerung, Textumfluss.

- `_rest(d, bekannt)`
- **class `Transform`** — Drehung um die Mitte des Objekts und Spiegelung.
- **class `Anchor`** — Lage auf dem Blatt. Waagerecht: Bezug ``seite`` \| ``rand`` \| ``spalte``, Versatz ``x`` oder Ausrichtung ``left`` \| ``center`` \| ``right`` \| ``inside`` \| ``outside``.
- **class `WrapSettings`** — Textumfluss: ``behind`` = hinter dem Text (sonst davor), ``mode`` = ``none`` (frei, ohne Umfluss) oder die Umbruchart des Fensters „Layout“; Abstände zum Text.
- **class `FillStyle`** — Füllung: ``kind`` = ``farbe`` \| ``verlauf`` \| ``graduell`` \| ``muster`` \| ``textur`` \| ``bild``; die Angaben der Art stehen in ``params``.
  - `aus_dict(d)`
  - `zu_dict()`
- **class `StrokeStyle`** — Kontur: Farbe, Stärke, Linienart (``einfach``, ``gestrichelt`` …).
  - `aus_dict(d)`
  - `zu_dict()`
- **class `Shadow`**
- **class `VectorPath`** — Pfad aus Anweisungen wie bei ``RenderBackend.draw_path``: ``("M", x, y)``, ``("L", x, y)``, ``("Q", cx, cy, x, y)``, ``("C", …)``, ``("Z",)``, ``("E", mx, my, rx, ry)``, ``("R", x, y, b, h)``.
  - `polygon(punkte)`
  - `rounded_rect(x, y, b, h, r)`
  - `arrow(x0, y0, x1, y1, kopf)`
  - `zu_liste()`
  - `aus_liste(liste)`
- **class `ImageObject`** — Ein Bild als Objekt: Bilddaten (Originalbytes) oder Platzhalter (fehlende Datei), Größe, Lage, Umfluss, Zuschnitt, Maske, Füllung, Kontur, Drehung, Beschriftung.
  - `format()`
  - `placeholder()`
  - `pixel_size()`
  - `scaled_to_width(b)` — Auf Breite ``b`` skaliert, Seitenverhältnis bleibt.
  - `aus_angabe(a, data)` — Aus der Angabe eines frei positionierten Bildes (``freie_bilder``).
  - `zu_angabe()` — Die Angabe im Format von ``freie_bilder``; Schlüssel, die nicht gesetzt waren, bleiben weg.
- **class `ShapeObject`** — Eine Form: Art (``rechteck``, ``abgerundet``, ``ellipse``, ``linie``, ``pfeil``, ``vieleck``, ``freihand``, Katalogname), Größe, Füllung, Kontur, Text, Schatten, Pfad.
  - `aus_parametern(d)` — Aus den Formparametern (``formen.STANDARD``: ``fuell`` Farbe, ``linie`` Farbe, ``strich`` Stärke).
  - `zu_parametern()`

### `core/document/position.py`

Gemeinsame Positionsangaben innerhalb eines Dokuments.

- **class `Caret`**

### `core/document/pruefung.py`

Prüfung des Dokumentaufbaus. Ohne Qt.

- `pruefe_dokument(d)` — Gibt die Fehler als Texte zurück; eine leere Liste heißt: Der Aufbau stimmt.

### `core/document/serialisierung.py`

Das Dokumentmodell als einfache Daten (JSON-tauglich, ohne Markup) und zurück. Ohne Qt.

- `seite_zu_daten(seite)`
- `seite_aus_daten(daten)`
- `_fmt(fmt)`
- `bloecke_zu_daten(bloecke)`
- `bloecke_aus_daten(daten)`
- `dokument_zu_daten(d)`
- `dokument_aus_daten(daten)`

### `core/document/values.py`

Neutrale Werte für Formateigenschaften (ohne Qt): was eine Eigenschaft eines Zeichen-, Absatz-, Tabellen- oder Rahmenformats annehmen kann.

- **class `Color`**
- **class `Brush`** — Pinsel; ``style`` ist der Musterindex (0 = kein Pinsel, 1 = Vollfarbe, weitere Muster zählen wie in Qt). Farbverläufe und Bildmuster kennt das Modell noch nicht.
- **class `GradientBrush`** — Pinsel mit Farbverlauf: ``kind`` ``linear`` (``punkte`` = x1, y1, x2, y2), ``radial`` (Mitte x, y, Radius, Brennpunkt x, y) oder ``conical`` (Mitte x, y, Winkel);
- **class `TextureBrush`** — Pinsel mit Bildmuster: ``style`` der Musterindex, ``png`` das Muster als PNG.
- **class `Pen`** — Stift (zum Beispiel die Kontur von Text): Pinsel, Breite, Strichart, Linienende und Ecken (Zahlen wie bei Qt).
- **class `Length`** — Längenangabe: ``kind`` ist ``variable``, ``fixed`` (Bildpunkte) oder ``percentage`` (Prozent).
- **class `LineSpacing`** — Absatzzeilenabstand: ``single``, ``proportional`` (Prozent), ``multiple`` (Faktor), ``fixed`` oder ``minimum`` (Bildpunkte).
- **class `RowHeight`** — Tabellenzeilenhöhe: ``minimum`` oder ``exact`` in Bildpunkten.
- **class `TabStop`** — Tabstopp: Position in Bildpunkten, Art (Zählung wie in Qt: 0 links, 1 rechts, 2 zentriert, 3 Trennzeichen) und Trennzeichen.

### `core/document/zugriff.py`

Zugriff auf Dokumentelemente anhand ihrer Pfade.

- `behaelter(dok, pfad)` — Die Blockliste, in der der Absatz mit dem Pfad ``pfad + (index,)`` steht.
- `absatz_bei(dok, pfad)`

## `core/editing`

### `core/editing/__init__.py`

Bearbeiten des Dokumentmodells ohne Qt.


### `core/editing/abschnittsbearbeitung.py`

Abschnittsoperationen der Sitzung: Abschnittswechsel, Seiteneinrichtung, Kopf- und Fußzeilen, Dokumenteigenschaften. Ohne Qt.

- **class `AbschnittTeil`**
  - `_abschnitt(index)`
  - `abschnitt_index(block_id)` — Der Abschnitt (Index), in dem der Absatz oder die Tabelle steht.
  - `abschnitt_einfuegen(pos, beginn, seite)` — Beginnt an der Stelle einen neuen Abschnitt (nur im Fließtext, nicht in einer Tabelle). Der neue Abschnitt übernimmt die
  - `abschnitt_vor_einfuegen(block_id, beginn, seite)` — Beginnt einen neuen Abschnitt unmittelbar vor dem Block (Absatz, Tabelle oder Rahmen) im Haupttext — der Block davor beschließt
  - `abschnitt_entfernen(index, behalte)` — Hebt den Wechsel vor dem Abschnitt ``index`` auf: Sein Text gehört danach zum Abschnitt davor. ``behalte`` bestimmt,
  - `abschnitt_beginn_setzen(index, beginn)`
  - `seite_setzen(index, einrichtung, **felder)` — Ändert die Seiteneinrichtung eines Abschnitts (``index``; ``None``: aller Abschnitte) — entweder ganz (``einrichtung``)
  - `seite_ersetzen(index, einrichtung, ressourcen)` — Setzt die Seiteneinrichtung eines Abschnitts ganz; ``ressourcen`` sind die Bilddaten, auf die sie (Kopf-/Fußzeilenbilder)
  - `kopf_fuss_setzen(index, welche, text, align, fmt)` — Setzt Text, Ausrichtung oder Format einer Kopf-/Fußzeile (``welche``: header, footer, first_header, first_footer,
  - `eigenschaft_setzen(name, wert)` — Titel, Autor, Sprache, Zitierweise, Kennwort … — ``None`` entfernt die Eigenschaft.

### `core/editing/auswahl.py`

Schreibmarke und Auswahl der Bearbeitungssitzung. Ohne Qt.

- **class `AuswahlTeil`** — Hält ``self._auswahl`` (Anker und Kopf; ist die Auswahl leer, ist der Kopf die Schreibmarke).
  - `auswahl()`
  - `setze_auswahl(anker, kopf)`
  - `auswahl_nachtragen(auswahl)` — Setzt die Auswahl nach einem Schritt, der sie nicht kannte (Eingabe in der Ansicht): sie gilt auch als Auswahl nach dem
  - `_setze(pos)`
  - `_pruefe_position(pos)`
  - `_absatz(absatz_id)`
  - `_bereich(auswahl)` — (Anfang, Ende) der Auswahl in Dokumentreihenfolge.
  - `_stuecke(start, ende)` — Die Absätze zwischen zwei Stellen als (Absatz, von, bis) in Dokumentreihenfolge.
  - `_ziel_absaetze(auswahl, absatz_ids)`
  - `_auswahl_retten(ersatz)` — Nach einer Operation, die Text entfernt hat: Eine Schreibmarke hinter dem Absatzende rückt ans Ende; steht sie in einem

### `core/editing/bearbeitungssitzung.py`

Die zentrale Bearbeitungssitzung — der eine Weg, auf dem ein ``Dokument`` fachlich geändert wird. Ohne Qt.

- **class `Bearbeitungssitzung`**(TextTeil, SuchTeil, ZwischenablageTeil, FormatTeil, TabellenTeil, ObjektTeil, AbschnittTeil, ZusatzTeil, ErsatzTeil, AuswahlTeil, Verlauf)
  - `__init__(dokument)`
  - `pruefe()` — Prüft den Aufbau des Dokuments; gibt die gefundenen Fehler als Texte zurück (leer = in Ordnung).
  - `dokument_ersetzen(neu)` — Setzt den ganzen Inhalt des Dokuments (Abschnitte, Vorlagen, Listen, Zusatzdaten …) auf den von ``neu`` — etwa nach dem

### `core/editing/ersatzbearbeitung.py`

Ersetzen ganzer Absatzfolgen und der Zusatzdaten als je ein Schritt (Übernahme von Ergebnissen, die außerhalb der Sitzung entstehen: Lesen einer

- **class `ErsatzTeil`**
  - `absatzfolge_ersetzen(erste_id, anzahl, neue, listen, ressourcen, tippen, anhaengen, objekte)` — Ersetzt ``anzahl`` aufeinanderfolgende Absätze ab ``erste_id`` (im selben Textfluss) durch ``neue``.
  - `zusatzdaten_ersetzen(kommentare, noten, quellen, eigenschaften, anhaengen)` — Setzt Kommentare, Noten, Quellen und Dokumenteigenschaften (so wie sie die Oberfläche in ihrem Meta-Wörterbuch führt).

### `core/editing/formatbearbeitung.py`

Formatoperationen der Sitzung: Zeichen- und Absatzformat, Formatvorlagen, Listen und Nummerierung. Ohne Qt.

- **class `FormatTeil`**
  - `zeichenformat_anwenden(aenderung, auswahl, ersetzen)` — Setzt Eigenschaften im Bereich (``None`` als Wert entfernt eine). Ohne markierten Text gilt das Format für den Text, der
  - `zeichenformat_bei(pos)` — Das Zeichenformat an der Schreibmarke (das Tippformat, wenn eines gesetzt ist).
  - `absatzformat_anwenden(aenderung, auswahl, absatz_ids, ersetzen)`
  - `absatz_zeichenformat_anwenden(aenderung, auswahl, absatz_ids, ersetzen)` — Das Zeichenformat der Absatzmarke (gilt für Text, der in den leeren Absatz getippt wird).
  - `vorlage_setzen(vorlage)` — Legt eine Formatvorlage an oder ersetzt die gleichnamige.
  - `vorlage_loeschen(name)` — Entfernt die Vorlage; Text, der sie trägt, fällt auf ihre Basisvorlage zurück.
  - `vorlage_umbenennen(alt, neu)`
  - `_absaetze_mit_vorlage(name)`
  - `_vorlage_umhaengen(alt, neu)`
  - `vorlage_anwenden(name, auswahl, absatz_ids)` — Weist eine Vorlage zu. Absatzvorlage: das Absatzformat wird auf die Vorlage zurückgesetzt (Ortsangaben wie Seitenumbruch
  - `liste_anlegen(ebenen, name)` — Legt eine Listendefinition an. ``ebenen``: Liste von ``ListenEbene`` oder der Name einer Zahlen-/Aufzählungsart für eine
  - `_ebenen(ebenen)`
  - `liste_aendern(liste_id, ebenen, name)`
  - `_liste_holen(liste_id)`
  - `liste_anwenden(liste_id, auswahl, absatz_ids, ebene)`
  - `liste_entfernen(auswahl, absatz_ids)`
  - `listenebene_aendern(schritte, auswahl, absatz_ids)` — Stuft Listenabsätze tiefer (``+1``) oder höher (``-1``).
  - `liste_neu_beginnen(absatz_id, start)` — Die Zählung beginnt an diesem Absatz mit ``start``; ``None`` setzt die Zählung wieder fort.
  - `listenmarken()`

### `core/editing/objektbearbeitung.py`

Objektoperationen der Sitzung: Bilder, Formen, Textfelder und andere grafische Objekte — im Text oder frei positioniert —

- **class `ObjektTeil`**
  - `ressource_setzen(schluessel, daten)` — Legt Bilddaten unter einem Schlüssel ab; ``None`` entfernt sie.
  - `ressourcen_bereinigen()` — Entfernt Bilddaten, auf die kein Objekt mehr verweist. Gibt die Zahl der entfernten Einträge zurück.
  - `_pruefe_objekt(art, breite, hoehe, ressource)`
  - `_ablegen(objekt_id, bilddaten)`
  - `objekt_einfuegen(art, breite, hoehe, pos, *, ressource, bilddaten, daten, alt_text, format)` — Fügt ein Objekt wie ein Zeichen in den Text ein. ``bilddaten`` werden als Ressource abgelegt. Gibt die Objekt-Id zurück.
  - `objekt(objekt_id)` — Das Objekt mit dieser Id — ``InlineObjekt`` oder ``FreiesObjekt``; ``None``, wenn es keines gibt.
  - `objekt_position(objekt_id)` — Die Textstelle vor einem Objekt im Text; bei einem freien Objekt der Anfang seines Ankerabsatzes.
  - `_inline(objekt_id)`
  - `objekt_aendern(objekt_id, **felder)` — Ändert Eigenschaften eines Objekts (Größe, Daten, Alternativtext, bei freien Objekten auch Lage, Umbruch, Anker …).
  - `objekt_entfernen(objekt_id)`
  - `objekt_frei_einfuegen(art, breite, hoehe, anker, *, bilddaten, **felder)` — Legt ein frei positioniertes Objekt an, verankert am Absatz ``anker`` (sonst am Absatz der Schreibmarke).
  - `objekt_zu_frei(objekt_id, umbruch, **felder)` — Löst ein Objekt aus dem Text und positioniert es frei (Textumbruch). Die Id bleibt.
  - `objekt_zu_inline(objekt_id, pos)` — Setzt ein frei positioniertes Objekt wie ein Zeichen in den Text (an ``pos``, sonst an den Anfang seines Ankerabsatzes).
  - `objekt_ebene(objekt_id, wohin)` — Stapelreihenfolge: ``vorn``, ``hinten``, ``vor`` (eine Ebene nach vorn), ``zurueck``.
  - `objekte_an(absatz_id)` — Die frei positionierten Objekte, die an diesem Absatz verankert sind, in Stapelreihenfolge.
  - `_rahmen(rahmen_id)`
  - `rahmen_einfuegen(format, pos)` — Fügt einen leeren Textrahmen ein — am Absatzanfang vor dem Absatz, sonst wird der Absatz geteilt. Die Schreibmarke steht
  - `rahmen_loeschen(rahmen_id)` — Entfernt den Rahmen samt Inhalt.
  - `rahmenformat_anwenden(rahmen_id, aenderung, ersetzen)`

### `core/editing/suche.py`

Suchen und Ersetzen im Dokumentmodell, ohne Qt.

- **class `Suchauftrag`**
  - `hat_format()`
  - `leer()`
- `_besitzer(dok)` — Absatz-Id → Besitzer der Blockliste (Abschnitt, Zelle oder Rahmen), in dem er steht.
- `roh_text(dok)` — Der Text des Dokuments, eine Stelle je Position (Absätze durch ein Zeichen getrennt), mit Kennzeichen für Noten, Felder, Grafiken und Umbrüche.
- `offset_zu_position(dok, offset)` — Die Textstelle zu einer Stelle im Rohtext (hinter dem Ende: das Dokumentende).
- `position_zu_offset(dok, pos)`
- `_woertlich(text)` — Suchtext ohne Platzhalter → Liste von Regex-Stücken (ein Stück je Zeichen oder Sonderzeichen).
- `_klammer(text, i)` — ``{n,m}`` (Wiederholung) oder ``[abc]``/``[!x]`` (Zeichenklasse) ab Stelle ``i`` → (Regex-Stück, Stelle des letzten verbrauchten Zeichens).
- `_platzhalter(text)` — Platzhalter: ? ein Zeichen, * beliebig viele, [abc] [a-z] [!x] eines davon/keines, {n,m} Wiederholung, @ eins oder mehr,
- `_ignoriert(a)` — Die Zeichen, über die die Suche hinweggeht (Satzzeichen, Leerzeichen); mit Platzhaltern gilt das nicht.
- `muster(a)` — Der reguläre Ausdruck des Auftrags; ``None`` bei leerem Text (dann sucht nur die Formatierung) oder ungültigen Platzhaltern.
- `gueltig(a)`
- `ersatz_text(a, ersatz, gefunden, zwischenablage)` — Der Ersatztext mit seinen Sonderzeichen: ^p Absatz, ^t Tab, ^l Zeilenumbruch, ^m Seiten-, ^n Spaltenumbruch, ^& der gefundene Text,
- `_stuecke_im_bereich(dok, von, bis)` — (Absatz, Anfang im Absatz, Ende im Absatz) der Absätze, die der Bereich [von, bis) berührt.
- `_zeichen_passen(dok, von, bis, a)`
- `_nur_format(dok, a, von, bis)` — Ohne Suchtext: jede zusammenhängende Strecke mit der gesuchten Formatierung (je Absatz).
- `treffer(dok, a, von, bis, grenze)` — Alle Treffer im Bereich [von, bis) als (von, bis).
- `naechster(dok, a, ab, rueckwaerts, von, bis, umlauf)` — Der nächste Treffer hinter (oder vor) ``ab``; mit ``umlauf`` geht es am Ende vorn weiter (und umgekehrt).
- **class `SuchTeil`**
  - `ersetzen_durch(von, bis, neu, format, absatzformat)` — Ersetzt den Bereich [von, bis) des Rohtextes durch ``neu`` (Text mit Kennzeichen aus ``ersatz_text``). Die Formatierung des ersetzten Textes
  - `alle_ersetzen_auftrag(a, ersatz, von, bis, format, absatzformat, zwischenablage)` — Alle Treffer im Bereich ersetzen, als ein Schritt für Rückgängig. → Zahl der Ersetzungen.

### `core/editing/tabellenbearbeitung.py`

Tabellenoperationen der Sitzung: anlegen, löschen, Zeilen und Spalten, Zellen verbinden und teilen, Formate, Tabelle ↔ Text.

- `gedreht(gitter)` — Zeilen und Spalten vertauscht — so gilt jede Zeilenoperation auch für Spalten.
- `abgleichen(gitter, frisch)` — Bringt Platzhalter und Spannen in Ordnung: Spannen enden am Tabellenrand, jede bedeckte Stelle ist ein Platzhalter, jede
- `_anker(gitter)`
- `zeilen_einfuegen(gitter, index, anzahl)`
- `zeilen_loeschen(gitter, index, anzahl)`
- `zeilen_dehnen(gitter, index, anzahl)` — Fügt Zeilen ein, die keine neuen Zellen bringen: Jede Zelle, die bis zur Zeile ``index - 1`` reicht, wird höher.
- `verbinden(gitter, zeile, spalte, zeilen, spalten)` — Verbindet das Rechteck zu einer Zelle. Gibt (Gitter, weggefallene leere Absätze) zurück.
- `ist_leer(zelle)`
- `_aufteilung(gesamt, teile_)`
- **class `TabellenTeil`**
  - `_tabelle(tabellen_id)`
  - `_frische_zelle(vorbild)`
  - `_gitter_setzen(t, gitter, vorbild, weg_bloecke)` — Setzt das neue Gitter; räumt auf, was an weggefallenen Absätzen hing; rettet die Schreibmarke.
  - `tabelle_einfuegen(zeilen, spalten, pos, format, spaltenbreiten, zellformat)` — Fügt eine Tabelle ein — am Absatzanfang vor dem Absatz, sonst wird der Absatz geteilt. Die Schreibmarke steht danach in
  - `tabelle_loeschen(tabellen_id)`
  - `zeilen_einfuegen(tabellen_id, index, anzahl)` — Neue Zeilen vor der Zeile ``index`` (``index == Zeilenzahl``: am Ende). Sie übernehmen das Format der Nachbarzeile.
  - `spalten_einfuegen(tabellen_id, index, anzahl, breite)`
  - `zeilen_loeschen(tabellen_id, index, anzahl)` — Löscht Zeilen; fällt die letzte weg, verschwindet die Tabelle.
  - `spalten_loeschen(tabellen_id, index, anzahl)`
  - `zellen_verbinden(tabellen_id, zeile, spalte, zeilen, spalten)` — Verbindet das Rechteck ab (zeile, spalte). Der Inhalt aller Zellen bleibt, leere Zellen bringen nichts mit.
  - `zelle_teilen(tabellen_id, zeile, spalte, zeilen, spalten)` — Teilt die Zelle in ``zeilen`` × ``spalten`` Zellen. Eine verbundene Zelle zerfällt zuerst entlang ihrer Gitterlinien;
  - `zellen_leeren(tabellen_id, zellen)` — Löscht den Inhalt der genannten Zellen (``[(zeile, spalte)]``; ohne Angabe: aller Zellen), der Aufbau bleibt.
  - `_zellen(t, zellen)`
  - `zellformat_anwenden(tabellen_id, aenderung, zellen, ersetzen)`
  - `tabellenformat_anwenden(tabellen_id, aenderung, ersetzen)`
  - `spaltenbreiten_setzen(tabellen_id, breiten)` — Setzt alle Spaltenbreiten (Liste) oder einzelne (``{Spalte: Breite}``); 0 = automatisch.
  - `zeilenhoehen_setzen(tabellen_id, hoehen)` — Setzt die Mindesthöhen aller Zeilen (Liste) oder einzelner (``{Zeile: Höhe}``); 0 = automatisch.
  - `spalten_gleich(tabellen_id, von, bis)` — Die Spalten ``von`` bis ``bis`` (einschließlich) bekommen dieselbe Breite; ihre Gesamtbreite bleibt.
  - `zeilen_gleich(tabellen_id, hoehe, von, bis)` — Die Zeilen bekommen dieselbe Mindesthöhe (die gemessene Höhe liefert das Layout).
  - `tabelle_skalieren(tabellen_id, faktor_breite, faktor_hoehe)`
  - `tabelle_zu_text(tabellen_id, trenner, geschachtelt)` — Ersetzt die Tabelle durch Textabsätze, ohne Läufe oder Objekte in Klartext umzuwandeln.
  - `text_zu_tabelle(auswahl, trenner, spalten)` — Macht aus den markierten Absätzen eines Textflusses eine Tabelle: je Absatz eine Zeile, Zellen an ``trenner`` getrennt.
  - `zelle_anfang(tabellen_id, zeile, spalte)` — Die erste Textstelle der Zelle.
  - `zellen_im_bereich(auswahl)` — (Tabellen-Id, [(zeile, spalte)]) der Zellen, die die Auswahl in einer Tabelle überstreicht (das Rechteck zwischen

### `core/editing/texteingabe.py`

Textoperationen der Sitzung: einfügen, löschen, ersetzen, Absätze teilen, suchen. Ohne Qt.

- `ohne_marken(fmt)`
- `tippformat_bei(a, versatz)` — Das Format für Text, der an dieser Stelle getippt wird: das des Zeichens davor. Markierungen (Verknüpfung, Feld, Textmarke …)
- `alle_absaetze(bloecke)` — Alle Absätze einer Blockliste, auch die in Tabellen und Rahmen.
- **class `TextTeil`**
  - `text_einfuegen(text, pos, format)` — Fügt Text ein; ``\n`` beginnt einen neuen Absatz (U+2029 ebenso, U+2028 bleibt ein Zeilenumbruch im Absatz). Ohne ``pos``
  - `_einsetzen(a, versatz, elemente)`
  - `absatz_teilen(pos)` — Neuer Absatz an der Stelle (Eingabetaste). Gibt den Anfang des neuen Absatzes zurück.
  - `_teilen(pos)`
  - `loeschen(auswahl)` — Löscht den markierten Bereich. Liegen Anfang und Ende im selben Textfluss, fallen die Blöcke dazwischen weg und die
  - `_schneiden(a, von, bis)`
  - `_loeschen_markieren(start, ende)` — Nachverfolgtes Löschen: selbst eingefügter Text verschwindet, alles andere wird als gelöscht markiert.
  - `_bloecke_entfernen(bloecke, index, anzahl)` — Nimmt Blöcke aus einer Liste und mit ihnen die Objekte, die an ihren Absätzen verankert sind.
  - `_umankern(von_id, zu_id)`
  - `_verwaiste_entfernen(entfernt)` — Kommentare und Noten, deren letzte Markierung gerade gelöscht wurde, fallen aus dem Dokument.
  - `zeichen_loeschen(vorwaerts)` — Entf (``vorwaerts``) oder Rücktaste. Am Absatzrand wachsen zwei Absätze zusammen; vor und hinter Tabellen geschieht nichts.
  - `ersetzen(text, auswahl, format)` — Ersetzt den Bereich durch Text; ohne ``format`` behält der neue Text das Format des Bereichsanfangs.
  - `inhalt_setzen(text)` — Der ganze Dokumenttext wird durch reinen Text ersetzt (ein Abschnitt, Absätze je Zeile).
  - `absaetze_umstellen(absatz_ids, ordnung)` — Stellt aufeinanderfolgende Absätze eines Textflusses um: ``ordnung`` sind die Indizes in ``absatz_ids`` in der neuen Reihenfolge.
  - `suche(muster, *, gross_klein, ganzes_wort, regex)` — Alle Fundstellen als ``Auswahl`` in Dokumentreihenfolge (Treffer reichen nicht über Absatzgrenzen).
  - `alle_ersetzen(muster, ersatz, **optionen)`
  - `text(auswahl)`
  - `ist_im_haupttext(absatz_id)`
  - `nachbar(block_id, schritt_weite)` — Der nächste (``+1``) oder vorige (``-1``) Block im selben Textfluss, sonst ``None``.
  - `tabelle_von(absatz_id)` — (Tabelle, Zeile, Spalte) der innersten Zelle, in der der Absatz steht — ``None`` im Fließtext.

### `core/editing/verlauf.py`

Änderungsprotokoll der Bearbeitungssitzung: Schritte, Rückgängig/Wiederholen, Ereignisse, Änderungsstatus. Ohne Qt.

- **class `BearbeitungsFehler`**(Exception) — Eine Operation ist an dieser Stelle oder mit diesen Angaben nicht möglich. Das Dokument ist unverändert.
- **class `Aenderung`** — Was ein Schritt geändert hat — Layout und Ansicht gleichen damit ihre Darstellung ab.
- **class `_Schritt`**
- `schritt(name, bereich)` — Macht aus einer Methode eine Operation: ein Schritt im Verlauf, bei Fehler alles zurück.
- **class `Verlauf`** — Grundlage der Sitzung: Protokoll, Transaktionen, Beobachter. Erwartet ``self.dokument`` und ``self._auswahl`` (siehe ``AuswahlTeil``).
  - `__init__()`
  - `beobachte(ruf)`
  - `vergiss(ruf)`
  - `beobachte_zwischen(ruf)` — Wie ``beobachte``, aber ``ruf`` hört auch innerhalb eines offenen Blocks nach jeder Operation, was seit der letzten Meldung
  - `vergiss_zwischen(ruf)`
  - `_nach_op()`
  - `_zwischenmeldung()`
  - `block_beginnen(name, anhaengen)` — Beginnt einen Schritt, den die Aufrufer selbst beenden. Verschachtelt sich (Zähler); alles darin ist ein Rückgängig.
  - `block_beenden()`
  - `block_abbrechen(fehler)` — Rollt einen von außen geöffneten Bearbeitungsblock vollständig zurück.
  - `block_offen()`
  - `block_schliessen()` — Schließt einen vergessenen Block.
  - `_melde(s, herkunft)`
  - `gruppe(name)` — Fasst mehrere Operationen zu einem Schritt zusammen (ein Rückgängig).
  - `_struktur_ordnen()` — Regel des Modells: Vor jeder Tabelle und jedem Rahmen und am Ende jedes Textflusses steht ein Absatz. Fehlende werden leer ergänzt.
  - `_abschliessen(s)`
  - `kann_rueckgaengig()`
  - `kann_wiederholen()`
  - `rueckgaengig()`
  - `wiederholen()`
  - `verlauf_laenge()`
  - `verlauf_zurueck_auf(laenge)` — Nimmt Schritte zurück, bis der Verlauf wieder ``laenge`` Schritte hat, und verwirft die Wiederholen-Schritte (Vorschauen).
  - `verlauf_leeren()`
  - `geaendert()`
  - `als_gespeichert_merken()`
  - `schrittnamen()` — (Name des nächsten Rückgängig-Schritts, Name des nächsten Wiederholen-Schritts) — leer, wenn es keinen gibt.
  - `_muss_offen()`
  - `_attr(obj, name, neu)`
  - `_liste(liste, index, anzahl, neu)` — Ersetzt ``liste[index:index+anzahl]`` durch ``neu``.
  - `_dict(d, schluessel, neu)` — Setzt ``d[schluessel]``; ohne ``neu`` wird der Eintrag entfernt.
  - `_id()`
  - `_beruehrt(*block_ids)`
- `_zurueck(e)`
- `_vorwaerts(e)`

### `core/editing/zusatzbearbeitung.py`

Zusatzdaten der Sitzung: Kommentare, Fuß-/Endnoten, Textmarken, Felder, Verweise, Stichwörter, Zitate und Quellen,

- **class `ZusatzTeil`**
  - `_markiere(start, ende, wandle)` — Wendet ``wandle(format) -> format`` auf alle Inhalte des Bereichs an.
  - `_wandle_ueberall(trifft, wandle)` — Ändert das Format aller Inhalte im Dokument, auf die ``trifft(format)`` zutrifft.
  - `bereiche(trifft, wert)` — Zusammenhängende Bereiche (je Absatz), deren Format ``trifft(format)`` erfüllt, als ``Auswahl`` in Dokumentreihenfolge.
  - `_wort_bei(pos)` — Das Wort um die Stelle; gibt es keines, das Zeichen daneben. Leerer Absatz: Fehler.
  - `_bereich_oder_wort(auswahl)`
  - `kommentar_einfuegen(text, autor, initialen, datum, auswahl, antwort_auf)` — Kommentiert den markierten Text (ohne Markierung: das Wort an der Schreibmarke). Mit ``antwort_auf`` entsteht eine
  - `kommentar_aendern(kommentar_id, text, geloest)`
  - `kommentar_loeschen(kommentar_id)` — Löscht einen Kommentar samt Antworten und Markierung; ohne Id alle Kommentare.
  - `note_einfuegen(text, art, pos)` — Fügt an der Stelle das Notenzeichen ein (hochgestellt) und legt den Notentext ab. ``art``: ``f`` Fußnote, ``e`` Endnote.
  - `note_aendern(art, note_id, text)`
  - `note_loeschen(art, note_id)`
  - `_noten_nummerieren()` — Schreibt die Notenzeichen in Dokumentreihenfolge neu: Fußnoten 1, 2, 3 …, Endnoten i, ii, iii …
  - `noten_reihenfolge(art)` — Die Ids der Noten in der Reihenfolge ihrer Zeichen im Text.
  - `textmarke_setzen(name, auswahl)` — Setzt eine Textmarke auf den markierten Text (ohne Markierung: auf das Wort an der Schreibmarke). Eine gleichnamige
  - `_marke_weg(name)`
  - `textmarke_loeschen(name)`
  - `textmarken()` — Name → ``Auswahl`` (vom Anfang des ersten bis zum Ende des letzten markierten Stücks).
  - `link_setzen(ziel, auswahl, text)` — Macht den markierten Text zur Verknüpfung auf ``ziel`` (Adresse oder ``#Textmarke``); ``None`` hebt sie auf. Mit ``text``
  - `feld_einfuegen(anweisung, ergebnis, pos, format)` — Fügt ein Feld ein: Der sichtbare Text ist das Feldergebnis, die Feldanweisung hängt am Format. Gibt die Stelle dahinter zurück.
  - `felder()` — Alle Felder als (Auswahl, Anweisung, Ergebnistext) in Dokumentreihenfolge. Aufeinanderfolgende Stücke mit derselben
  - `felder_aktualisieren(rechner, auswahl)` — Rechnet Feldergebnisse neu: ``rechner(anweisung, bisheriger_text, absatz_id) -> str \| None`` (``None``: unverändert).
  - `querverweis_einfuegen(marke, text, pos)` — Verweist auf eine Textmarke: ein Feld ``REF marke \h``, das zugleich dorthin springt.
  - `index_eintragen(stichwort, optionen, auswahl)` — Merkt den markierten Text (oder das Wort an der Schreibmarke) für das Stichwortverzeichnis vor; ``None`` entfernt den Eintrag.
  - `quelle_setzen(quelle)` — Legt eine Literaturquelle an oder ersetzt die mit demselben ``tag``.
  - `quelle_loeschen(tag)`
  - `zitat_einfuegen(tag, text, pos)` — Fügt den Zitattext ein und verknüpft ihn mit der Quelle ``tag``.
  - `beschriftung_einfuegen(bezeichnung, text, nach_block, davor, zahlenart)` — Setzt unter (oder über) den Block einen Beschriftungsabsatz „Abbildung 3: Text“ mit zählendem SEQ-Feld. Gibt die Id des
  - `beschriftungen_nummerieren()` — Zählt alle SEQ-Felder je Bezeichnung in Dokumentreihenfolge durch.
  - `ueberschriften()` — (Absatz-Id, Ebene, Text) aller Überschriften in Dokumentreihenfolge.
  - `verzeichnis_setzen(art, titel, zeilen, pos, optionen)` — Schreibt ein Verzeichnis (``toc`` Inhalt, ``abb``, ``tab``, ``index``, ``lit``): einen Kopfabsatz und je Eintrag eine Zeile
  - `verzeichnis_entfernen(art)`
  - `aenderungen()` — Alle nachverfolgten Änderungen als (Auswahl, Art ``ins``/``del``, Autor, Datum).
  - `_aenderungen_abschliessen(auswahl, weg)` — Entfernt die Stücke der Art ``weg`` und nimmt den übrigen die Markierung.
  - `aenderungen_annehmen(auswahl)` — Nimmt Änderungen an (im Bereich, an der Schreibmarke — oder mit ``None`` alle): Eingefügtes bleibt, Gelöschtes verschwindet.
  - `aenderungen_ablehnen(auswahl)` — Lehnt Änderungen ab: Eingefügtes verschwindet, Gelöschtes bleibt.

### `core/editing/zwischenablage.py`

Ausschnitte der Sitzung: Bereiche als Blockliste kopieren und einfügen (Zwischenablage, Textbausteine). Ohne Qt.

- **class `ZwischenablageTeil`**
  - `ausschnitt(auswahl)` — Eine unabhängige Kopie des Bereichs als Blockliste. Liegt der Bereich in einem Textfluss, sind Tabellen dazwischen
  - `ausschnitt_einfuegen(bloecke, pos)` — Fügt eine Blockliste (aus ``ausschnitt`` oder selbst gebaut) ein. Ein einzelner Absatz fließt in den Text; bei mehreren
  - `_neue_ids(bloecke)`

## `core/geometry`

### `core/geometry/__init__.py`

Eigene Geometrie ohne Qt: Maße in Bildpunkten (96 dpi), y wächst nach unten. Umrechnung zu und von Qt: ``adapter/qt/geometrie.py``.


### `core/geometry/margins.py`

Ränder (links, oben, rechts, unten) in Bildpunkten (96 dpi).

- **class `Margins`**
  - `horizontal()`
  - `vertical()`

### `core/geometry/point.py`

Punkt in Bildpunkten (96 dpi, wie ``modelle/seite.py``), y wächst nach unten.

- **class `Point`**
  - `translated(dx, dy)`

### `core/geometry/rect.py`

Rechteck in Bildpunkten (96 dpi): Ursprung links oben, y wächst nach unten.

- **class `Rect`**
  - `from_edges(left, top, right, bottom)`
  - `from_point_size(point, size)`
  - `left()`
  - `top()`
  - `right()`
  - `bottom()`
  - `top_left()`
  - `size()`
  - `center()`
  - `is_empty()`
  - `contains(point)` — Liegt der Punkt im Rechteck? Links und oben gehören dazu, rechts und unten nicht.
  - `intersects(other)` — Überlappen sich beide Flächen? Rechtecke, die sich nur an der Kante berühren, überlappen nicht.
  - `intersected(other)` — Die gemeinsame Fläche, ``None`` ohne Überlappung.
  - `united(other)` — Das kleinste Rechteck, das beide enthält (ein leeres Rechteck zählt nicht mit).
  - `translated(dx, dy)`
  - `adjusted(left, top, right, bottom)` — Kanten verschieben (wie Qt): positive Werte rücken die Kante nach rechts bzw. unten.
  - `shrunk(margins)` — Das Rechteck innerhalb der Ränder (die Textfläche einer Seite).
  - `grown(margins)`

### `core/geometry/size.py`

Größe in Bildpunkten (96 dpi).

- **class `Size`**
  - `is_empty()`
  - `scaled(factor)`

### `core/geometry/units.py`

Einheiten der Qt-freien Geometrie: Seiteneinstellungen in Millimetern, Layoutkoordinaten in Bildpunkten bei 96 dpi.

- `mm_to_px(mm)`
- `px_to_mm(px)`
- `umbruchraster(px)` — Auf 1/64 Bildpunkt abschneiden, damit Qt-Zeilengrenzen seitenübergreifend stabil bleiben.

## `core/layout`

### `core/layout/__init__.py`

Layout ohne Qt: Absatzzeilen, Objektpositionen und Seitenumbruch des Dokumentenmodells.


### `core/layout/absatzlayout.py`

Absatzsatz im Fluss: Läufe, Listenmarken, Objekte in der Zeile, Absatzregeln. Ohne Qt. Teil des Flusses in ``seitenlayout.py``.

- **class `AbsatzLayout`** — Absatzsatz im Fluss: Läufe, Listenmarken, Objekte in der Zeile, Absatzregeln.
  - `marken_von(a, art)` — [(Zeichenstelle, Noten-Id)] der Notenmarken im Absatz; ``art`` „f“ Fußnoten, „e“ Endnoten.
  - `regeln_an()` — Die Umbruchregeln gelten im Seitenfluss mit gleich breiten Spalten (nicht in Zellen und Rahmen).
  - `satz(a, af, breite, ausschluss)` — Den Absatz setzen: → (Absatzsatz, (Abstand davor, Abstand danach), Listenmarke, Abstand der Marke vom linken Rand).
  - `silben_stuecke(text, stil)` — Der Text in Stücke je Silbe mit abwechselnden Farben (Lesehilfe „Silbenfarben“); ``opt["silben"]``: ``funktion`` (Wort → Silben), ``farben``
  - `lese_stil(stil, z)` — Der Stil eines Textstücks mit den Einstellungen der Lesehilfe (Buchstaben- und Wortabstand) und ohne ausgeblendeten Text.
  - `umbruch_stelle(hs, w, folge)`
  - `objekte_platzieren(a)` — Frei positionierte Objekte dieses Absatzes auf die Seite legen; Objekte mit Umfluss engen den folgenden Text ein.
  - `absatz(a, folge)`

### `core/layout/eigenschaften.py`

Fachliche Zugriffe auf die benannten Eigenschaften des Dokumentenmodells (Namen wie die Eigenschaften von Qt-Formaten, siehe ``core/document/model.py``).

- `_zahl(v, standard)`
- `schrift(cf, grund)` — Die Schrift eines Textstücks; was es nicht setzt, kommt aus der Grundschrift des Dokuments, dann aus den Standards.
- `ausrichtung(pf, standard)`
- `abstaende(pf)`
- `einzuege(pf, einrueck_breite)` — (links, rechts, erste Zeile zusätzlich): Rand plus Einrückungsstufe mal Stufenbreite.
- `zeilenabstand(pf)`
- `umbruch_vor(pf)`
- `umbruch_nach(pf)`
- `laenge(v, gesamt)` — Eine Längenangabe in Bildpunkten; ``None`` bei variabler Länge.
- `tabstopps(pf, dok)` — ((Position, Art, Trennzeichen), …) der Tabstopps des Absatzes (sonst die des Dokuments), aufsteigend, und der Standardabstand.
- `tabfuellung(pf)` — Position (Bildpunkte) → Füllzeichen der Tabstopps des Absatzes (``P_TABFUELL``: „Position:Schlüssel;…“).
- `absatzrahmen(pf)` — Die Rahmenangabe des Absatzes („Farbe\|Breite pt\|Art\|Seiten\|Abstände“, siehe ``core/rendering/linien.rahmen_aus_text``) oder ``None``.
- `kapitaelchen(cf, grund)`
- `kapitaelchen_stuecke(text, font)` — Der Text als Kapitälchen: Kleinbuchstaben werden zu verkleinerten Großbuchstaben, alles andere bleibt; → [(Text, Schrift)] mit gleicher Zeichenzahl.
- `hintergrund(pf)` — Füllfarbe des Absatzes (Schattierung) oder ``None``.
- `grundschrift(dok)`
- `_brush_farbe(b)`
- `stil(cf, grund)` — Stil eines Textstücks für Satz und Zeichnen: Farbe, Unterstreichen (Art, Farbe), Überstreichen, Durchstreichen, Hervorheben, Versatz der Grundlinie (hoch-/tiefgestellt), Laufweite und Wortabstand; was fehlt, kommt aus der Grundschrift.
- `_farbwert(v)`
- `schreibweise(text, cf, grund)` — Der Text in der Schreibweise des Formats (Großbuchstaben, Kleinbuchstaben, Wortanfänge groß); die Zeichenzahl bleibt gleich (ein Zeichen, das dabei mehrere würde, bleibt stehen).
- `_roemisch(n)`
- `_buchstaben(n)`
- `listenzeichen(stil_nr, n, vor, nach)` — Aufzählungszeichen oder Nummer des ``n``-ten Absatzes einer Liste; ``stil_nr`` wie ``QTextListFormat.Style`` (Punkt -1, Kreis -2, Quadrat -3, Zahl -4, a -5, A -6, i -7, I -8).

### `core/layout/engine.py`

Die Layout-Engine: legt ein ``Dokument`` auf Seiten. Ohne Qt.

- **class `LayoutEngine`** — Berechnet das Layout eines ``Dokument``. ``engine`` liefert Schriftmaße und Vorschübe (Standard: ``HarfBuzzEngine``).
  - `__init__(engine, optionen)`
  - `berechnen(dok)` — Das Dokument auf Seiten legen.
  - `hoehe_von_bloecken(dok, bloecke, breite)` — Summe der Zeilenhöhen der Absätze in den Blöcken bei der festen Breite ``breite`` (ohne Absatzabstände).

### `core/layout/ergebnis.py`

Das Ergebnis der Layoutberechnung: Seiten mit ihren Plätzen (Zeilen, Zellen, Rahmen, Objekte, Noten) und die gesetzten Absätze. Ohne Qt.

- **class `AbsatzOrt`** — Wo ein Absatz steht: je Zeile Seite und Rechteck.
- **class `Platz`** — Ein Stück Seite: eine Absatzzeile, eine Tabellenzelle, ein Rahmen, ein freies Objekt, eine Note oder der Trennstrich über den Noten.
- **class `Seite`**
- **class `Ergebnis`**
  - `cursor(absatz_id, index)` — (Seite, Punkt) der oberen linken Ecke der Zeile, in der die Schreibmarke vor dem Zeichen ``index`` steht.
  - `zeilennummern(art)` — (Seitenindex, y auf der Seite, Zeilenhöhe, Nummer) für jede nummerierte Zeile in Lesereihenfolge; ``art`` „seite“: auf jeder Seite neu ab 1.
  - `treffer(seite, punkt)` — (Absatz-Id, Zeichenstelle) für einen Punkt auf der Seite (die nächste Textzeile); ``None``, wenn die Seite keinen Text hat.
  - `objekt_bei(seite, punkt)` — Id des obersten freien Objekts an dem Punkt der Seite, sonst ``None``.
  - `seite_von(absatz_id)` — Der Index der Seite, auf der der Absatz beginnt.

### `core/layout/formatwerte.py`

Fachliche Zugriffe auf die Formate des Dokumentmodells (``core/document/formate.py``) für Textsatz und Layout. Ohne Qt.

- `_zahl(v, standard)`
- `farbwert(text)` — ``#rrggbb`` oder ``#rrggbbaa`` als (r, g, b, a); sonst ``None``.
- `zeichenformat(dok, absatz, fmt)` — Das wirksame Zeichenformat eines Textstücks (Vorlagen aufgelöst); die Grundschrift des Dokuments steht darunter.
- `absatzformat(dok, absatz)`
- `schrift(z)` — Die Schrift eines Textstücks aus dem wirksamen Zeichenformat.
- `kapitaelchen(z)`
- `kapitaelchen_stuecke(text, font)` — Der Text als Kapitälchen: Kleinbuchstaben werden zu verkleinerten Großbuchstaben; → [(Text, Schrift)] mit gleicher Zeichenzahl.
- `schreibweise(text, z)` — Der Text in Großbuchstaben, wenn das Format es verlangt; die Zeichenzahl bleibt gleich (ein Zeichen, das dabei mehrere würde, bleibt stehen).
- `stil(z)` — Stil eines Textstücks für Satz und Zeichnen: Farbe, Unterstreichen, Überstreichen, Durchstreichen, Hervorheben, Versatz der Grundlinie,
- `ausrichtung(a)`
- `abstaende(a)`
- `einzuege(a)` — (links, rechts, erste Zeile zusätzlich).
- `zeilenabstand(a)`
- `richtung(a)` — „rtl“ oder „ltr“, wenn der Absatz die Schreibrichtung festlegt; sonst ``None`` (das erste starke Zeichen entscheidet).
- `umbruch_vor(a)`
- `umbruch_nach(a)`
- `spaltenumbruch_vor(a)`
- `regeln(a)` — Die Umbruchregeln eines Absatzes: ``kontrolle`` (Witwen/Waisen, Vorgabe an), ``nicht_trennen`` (mit dem nächsten zusammen),
- `option(a, name)`
- `tabstopps(a, dok)` — ((Position, Art, Trennzeichen), …) der Tabstopps des Absatzes, aufsteigend, und der Standardabstand.
- `tabfuellung(a)` — Position (Bildpunkte) → Füllzeichen der Tabstopps („Position:Schlüssel;…“).
- `hintergrund(a)`
- `absatzrahmen(a)`
- `listen_einzug(ebene)` — (Beginn der Nummer, Beginn des Textes) einer Listenebene in Bildpunkten vom linken Rand.

### `core/layout/fussnotenlayout.py`

Fußnoten am Seitenende und Endnoten am Dokumentende. Ohne Qt. Teil des Flusses in ``seitenlayout.py``.

- **class `FussnotenLayout`** — Fußnoten am Seitenende und Endnoten am Dokumentende.
  - `noten_hoehe(eintraege)`
  - `note_satz(nr, nid)`
  - `noten_satz(marke, text, breite)` — Eine Fuß- oder Endnote gesetzt: Marke, zwei Leerzeichen, Text in der kleineren Notenschrift.
  - `endnoten_setzen()` — Die Endnoten am Ende des Dokuments: Trennstrich, dann jede Note mit kleiner römischer Nummer in der Reihenfolge ihrer Marken.
  - `noten_platzieren()` — Die Fußnoten unten auf jede Seite mit Marken setzen (Rechtecke in Seitenkoordinaten).
  - `noten_hoehe_seite(eintraege, breite, hoehe)`

### `core/layout/geometrie.py`

Maße und Kleinteile des Seitenlayouts: Blattabstand, Zellenpolster, Notenmaße, Mindestgrößen; die Gitterstelle einer Tabellenzelle.

- **class `_Z`** — Eine sichtbare Tabellenzelle an ihrer Gitterstelle.

### `core/layout/kopf_fusslayout.py`

Kopf- und Fußzeilen der Seiten, ohne Qt: aus der Seiteneinrichtung des Abschnitts den gesetzten Text je Seite, mit Seitenzahl in der gewählten

- `_ausrichtung(align, nummer)` — links/mitte/rechts, oder aussen/innen: auf ungeraden Seiten steht „außen“ rechts, auf geraden links.
- `_kapitelnummern(dok, erg, ebene)` — Seitenindex → Nummer der letzten Überschrift der Ebene ``ebene``, die auf oder vor der Seite steht (0: noch keine).
- `kopf_fuss_setzen(engine, dok, erg)` — Setzt Kopf- und Fußzeile jeder Seite und trägt sie als Plätze ein.

### `core/layout/navigation.py`

Bewegung der Schreibmarke auf dem gesetzten Dokument: Zeichen, Wort, Zeile, Zeilenanfang/-ende, Seite, Dokumentanfang/-ende; Wortgrenzen. Ohne Qt,

- `_zeile(erg, pos)` — (Seite, Zeilenindex im Satz, Rechteck) der Zeile, in der die Stelle steht.
- `_zeilen_der_seite(erg, seite)`
- `_stelle_in(erg, platz, x)`
- `_senkrecht(erg, seite, r, x, runter)` — Die Stelle in der nächsten Zeile unter (über) der Zeile ``r``: zuerst eine Zeile, über der x liegt (dieselbe Spalte oder Zelle), sonst die
- `_wortgrenze(text, i, vor)` — Die nächste Wortgrenze rechts (``vor``) oder links von ``i`` im Text eines Absatzes.
- `wort_bei(erg, pos)` — Anfang und Ende des Wortes an der Stelle (für den Doppelklick).
- `bewegen(erg, pos, art, x)` — Die Stelle nach der Bewegung ``art`` (siehe ``BEWEGUNGEN``) und der gemerkte x-Wert: bei „hoch“/„runter“ und Seitenwechsel bleibt die

### `core/layout/objekte.py`

Lage von Bildern und Formen auf dem Blatt, ohne Qt: aus Verankerung und Größe das Rechteck in Blattkoordinaten (Ursprung links oben, Bildpunkte).

- `objekt_rechteck(anker, b, h, blatt_b, blatt_h, ml, mt, inhalt_b, inhalt_h, absatz_y, spalte_x, seite)` — Das Rechteck des Objekts auf dem Blatt. ``absatz_y``: oberer Rand des Absatzes (Blattkoordinate), ``spalte_x``: linker Rand der Spalte,

### `core/layout/objektlayout.py`

Lage frei positionierter Objekte auf dem Blatt, ohne Qt: aus Verankerung und Größe das Rechteck in Blattkoordinaten (Ursprung links oben, Bildpunkte).

- `objekt_rechteck(o, blatt_b, blatt_h, ml, mt, inhalt_b, inhalt_h, absatz_y, spalte_x, seite, spalte_b)` — Das Rechteck des Objekts auf dem Blatt. ``absatz_y``: oberer Rand des Ankerabsatzes (Blattkoordinate), ``spalte_x`` und ``spalte_b``:

### `core/layout/regeln.py`

Umbruchregeln eines Absatzes (Witwen/Waisen, Absatz zusammenhalten, mit dem nächsten Absatz zusammen), ohne Qt: die eine Stelle, die der Qt-freie Seitenumbruch (``seitenumbruch.py``)

- `umbruch_stelle(hs, regeln, rest, ganz, oben, folge)` — Vor welcher Zeile (0 = vor dem ganzen Absatz) beginnt die nächste Spalte oder Seite, damit die Regeln gelten? ``None``: kein Umbruch nötig.

### `core/layout/schreibmarke.py`

Schreibmarke und Auswahl auf dem gesetzten Dokument, ohne Qt: wo die Schreibmarke steht, welche Flächen eine Auswahl bedeckt und wohin eine

- `cursor_rechteck(erg, pos)` — (Seitenindex, Rechteck der Schreibmarke in Seitenkoordinaten) oder ``None``, wenn der Absatz nicht gesetzt ist.
- `auswahl_rechtecke(erg, auswahl)` — Seitenindex → Flächen der Auswahl (je Zeile ein Rechteck; ein mitgewähltes Absatzende zeigt sich als schmales Stück hinter der letzten Zeile).

### `core/layout/seitenlayout.py`

Die Layout-Engine: berechnet aus dem Dokumentmodell Seiten, Zeilen, Tabellen, Rahmen, Objekte und Noten. Ohne Qt.

- **class `_Fluss`**(AbsatzLayout, TabellenLayout, FussnotenLayout, TextUmfluss)
  - `__init__(engine, dok, marken, frei_an, optionen)`
  - `neue_seite()`
  - `weiter()`
  - `breite()`
  - `links()`
  - `frei()` — Höhe der Spalte auf dieser Seite abzüglich des Platzes, den die Fußnoten unten brauchen.
  - `platz_fuer(h, extra)`
  - `abstand_vor(a)` — Abstand vor einem Block: fällt mit dem Abstand unter dem vorigen zusammen und entfällt am Anfang der Spalte.
  - `abschnitt_beginnt(nr, abschnitt)`
  - `blocks(bloecke)`
  - `teilfluss(bloecke, breite)` — Blöcke in einer festen Breite setzen (Zelle, Rahmen): → (Höhe, Plätze relativ zur oberen linken Ecke). Die Zeilenrechtecke der Absätze
  - `auf_seite_setzen(plaetze, dx, dy, seite, kopie)` — Plätze aus einem Teilfluss (Zeilen, Zellen und Rahmen darin) an ihren Ort auf der Seite verschieben und eintragen.

### `core/layout/seitenumbruch.py`

Seitenumbruch über dem Dokumentenmodell, ohne Qt.

- **class `AbsatzOrt`** — Wo ein Absatz steht: je Zeile Seite, Spalte und Rechteck (Seitenkoordinaten, Bildpunkte).
- **class `Platz`** — Ein Stück Seite: eine Absatzzeile, eine Tabellenzelle, ein Rahmen, eine Note oder der Trennstrich über den Noten (für Zeichnen, Treffertest und Cursor).
- **class `Seite`**
- **class `Ergebnis`**
  - `cursor(pfad, index)` — Seite und Punkt (Seitenkoordinaten, obere linke Ecke der Zeile) des Cursors vor dem Zeichen ``index`` des Absatzes ``pfad``.
  - `zeilennummern(art)` — (Seitenindex, y auf der Seite, Zeilenhöhe, Nummer) für jede nummerierte Zeile in Lesereihenfolge; ``art`` „seite“: auf jeder Seite neu ab 1.
  - `treffer(seite, punkt)` — Absatz (Pfad) und Zeichenstelle für einen Punkt auf der Seite (die nächste Textzeile); ``None``, wenn die Seite keinen Text hat.
- **class `_Fluss`**
  - `__init__(engine, dok)`
  - `neue_seite()`
  - `weiter()`
  - `breite()`
  - `links()`
  - `frei()` — Höhe der Spalte auf dieser Seite abzüglich des Platzes, den die Fußnoten unten brauchen.
  - `platz_fuer(h, extra)`
  - `noten_hoehe(eintraege)`
  - `note_satz(nr, nid)`
  - `noten_satz(marke, text, breite)` — Eine Fuß- oder Endnote gesetzt: Marke, zwei Leerzeichen, Text in der kleineren Notenschrift.
  - `abschnitt_beginnt(nr, s)`
  - `absatz_opt(p, name)`
  - `absatz_regeln(p)` — Die Umbruchregeln eines Absatzes: ``kontrolle`` (Witwen/Waisen, Vorgabe an), ``nicht_trennen`` (mit dem nächsten zusammen), ``zusammen`` (Absatz nicht teilen).
  - `regeln_an()` — Die Umbruchregeln gelten im Seitenfluss mit gleich breiten Spalten (nicht in Zellen und Rahmen).
  - `umbruch_stelle(hs, w, folge)` — Wo beginnt die nächste Spalte oder Seite, damit die Umbruchregeln gelten (``regeln.umbruch_stelle``)? ``None``: kein Umbruch nötig.
  - `blocks(bloecke, pfad)`
  - `ausschluss_fuer()` — Funktion (y, h) → (Einengung links, Einengung rechts, Unterkante): wie weit schwebende Rahmen die Zeilen ab dem jetzigen Stand einengen.
  - `satz(p, breite, ausschluss)`
  - `marken_von(p, art)` — [(Zeichenstelle, Noten-Id)] der Notenmarken im Absatz; ``art`` „f“ Fußnoten, „e“ Endnoten.
  - `listenmarke(p)` — Aufzählungszeichen oder Nummer des Absatzes in seiner Liste (zählt die Absätze der Liste in Dokumentreihenfolge).
  - `absatz(p, pfad, folge)`
  - `teilfluss(bloecke, breite, pfad)` — Blöcke in einer festen Breite setzen (Zelle, Rahmen): → (Höhe, Plätze relativ zur oberen linken Ecke). Die Absätze werden mit ihren Sätzen vermerkt, ihre Rechtecke setzt der Aufrufer.
  - `auf_seite_setzen(plaetze, dx, dy, seite, kopie)` — Plätze aus einem Teilfluss (Zeilen, Zellen und Rahmen darin) an ihren Ort auf der Seite verschieben und eintragen.
  - `abstand_vor(a)` — Abstand vor einem Block: fällt mit dem Abstand unter dem vorigen zusammen und entfällt am Anfang der Spalte.
  - `rahmen(fr, pfad)` — Ein Rahmen im Text. Schwebend (links oder rechts): am Rand der Spalte an der aktuellen Höhe, der folgende Text läuft darum herum.
  - `tabellenbreite(eig, verfuegbar)`
  - `spaltenbreiten(t, breite_tab, luecke)` — Spaltenbreiten aus den Vorgaben (fest, Prozent, frei): freie Spalten teilen sich den Rest; passt die Summe nicht, wird auf die Tabellenbreite gebracht.
  - `tabelle(t, pfad)` — Eine Tabelle setzen: Spaltenbreiten aus den Vorgaben, Zeilenhöhen aus dem Inhalt (und der Mindesthöhe), Zeilen untereinander. Passt eine Zeile nicht mehr, beginnt sie in der
  - `zeile_teilen(zellen, inhalt, innen, zelle_platz, rand, luecke)` — Eine Tabellenzeile, die höher ist als eine ganze Seite, über mehrere Seiten setzen: je Seite so viele Zeilen jeder Zelle, wie passen; die Zelle steht auf jeder Seite mit ihrem Teil.
  - `endnoten_setzen()` — Die Endnoten am Ende des Dokuments: Trennstrich, dann jede Note mit kleiner römischer Nummer in der Reihenfolge ihrer Marken; sie fließen wie Text über die Seiten.
- `_noten_platzieren()` — Die Fußnoten unten auf jede Seite mit Marken setzen (Rechtecke in Seitenkoordinaten).
- `hoehe_von_bloecken(dok, engine, bloecke, breite)` — Summe der Zeilenhöhen der Absätze in den Blöcken bei der festen Breite ``breite`` (ohne Absatzabstände): wie ``QTextDocumentLayout.blockBoundingRect`` summiert,
- `umbrechen(dok, engine)` — Das Dokument auf Seiten legen. ``engine`` liefert Schriftmaße und Vorschübe (zum Beispiel ``HarfBuzzEngine``).

### `core/layout/tabellenlayout.py`

Tabellen im Fluss: Spaltenbreiten, verbundene Zellen, wiederholte Kopfzeilen, Teilung hoher Zeilen. Ohne Qt. Teil des Flusses in ``seitenlayout.py``.

- **class `TabellenLayout`** — Tabellen im Fluss: Spaltenbreiten, verbundene Zellen, wiederholte Kopfzeilen, Teilung hoher Zeilen.
  - `masz(wert, art, gesamt)` — Eine Maßangabe (Bildpunkte, Art fest/prozent/auto) in Bildpunkten; ``None`` bei automatischer Größe.
  - `spaltenbreiten(t, breite_tab, luecke)` — Spaltenbreiten aus den Vorgaben (größer 0 = fest, 0 = frei): freie Spalten teilen sich den Rest; passt die Summe nicht, wird auf die
  - `tabelle(t)` — Eine Tabelle setzen: Spaltenbreiten aus den Vorgaben, Zeilenhöhen aus dem Inhalt (und der Mindesthöhe), Zeilen untereinander. Passt eine
  - `zeile_teilen(zellen, inhalt, innen, zelle_platz, rand, luecke)` — Eine Tabellenzeile, die höher ist als eine ganze Seite, über mehrere Seiten setzen: je Seite so viele Zeilen jeder Zelle, wie passen.

### `core/layout/textumfluss.py`

Rahmen im Fluss und Flächen, um die der Text läuft (schwebende Objekte). Ohne Qt. Teil des Flusses in ``seitenlayout.py``.

- **class `TextUmfluss`** — Rahmen im Fluss und Flächen, um die der Text läuft (schwebende Objekte).
  - `ausschluss_fuer()` — Funktion (y, h) → (Einengung links, Einengung rechts, Unterkante): wie weit Flächen den Text ab dem jetzigen Stand einengen.
  - `rahmen(fr)` — Ein Rahmen im Text. Schwebend (links oder rechts): am Rand der Spalte an der aktuellen Höhe, der folgende Text läuft darum herum.

## `core/rendering`

### `core/rendering/__init__.py`

Rendering-Schnittstelle ohne Qt (Phase 8 der Qt-Entkopplung). Die Layout-Schicht liefert Zeichenanweisungen, ein Backend setzt sie um.


### `core/rendering/auswahlrenderer.py`

Auswahl, Schreibmarke und Formatierungszeichen auf dem Blatt zeichnen, ohne Qt. Alle Maße kommen aus dem Layout (``core.layout.schreibmarke``).

- `zeichne_auswahl(b, rechtecke, farbe)` — Die Flächen einer Auswahl auf der Seite (``core.layout.navigation.auswahl_rechtecke``) in der Auswahlfarbe.
- `zeichne_cursor(b, rect, farbe)` — Die Schreibmarke (``core.layout.navigation.cursor_rechteck``).
- `zeichne_formatzeichen(b, erg, index, absatzmarken, leerzeichen)` — Formatierungszeichen auf der Seite: ¶ am Ende jedes Absatzes, ↵ am Zeilenwechsel, · für Leerzeichen und → für Tabulatoren.

### `core/rendering/backend.py`

Die Schnittstelle des Zeichnens. Koordinaten in Bildpunkten (96 dpi), y nach unten. Jede Methode muss vom Backend umgesetzt werden.

- **class `LinearGradient`** — Linearer Farbverlauf von ``start`` nach ``end``; ``stops`` = ((Stelle 0…1, Farbe), …).
- **class `RadialGradient`** — Runder Farbverlauf um ``center`` mit ``radius``; ``stops`` wie beim linearen Verlauf.
- **class `PatternFill`** — Muster (``key`` wie in der Mustergalerie) in ``color`` über der Grundfarbe ``ground``.
- **class `TextureFill`** — Eine der mitgelieferten Texturen (``papier``, ``granit``, ``holz``, ``stoff``, ``marmor``, ``sand``).
- **class `ImageFill`** — Ein Bild (Bytes einer Bilddatei), auf die Fläche gestreckt.
- **class `Style`** — Linien- und Füllangaben: Farbe als (r, g, b, a), Strichstärke in Bildpunkten (0 = keine Linie), Füllung ja/nein, gestrichelt ja/nein.
- `rgba(text, alpha)` — Farbe aus ``#rrggbb`` oder ``#rrggbbaa`` (``#rgb`` auch); ``alpha`` gilt, wenn der Text keinen eigenen Alphawert hat.
- **class `RenderTarget`**(Protocol) — Struktureller Zeichenvertrag: ein Backend implementiert diese Operationen ohne Qt-Basisklasse.
  - `state(opacity, translate, rotate, clip, antialias, clip_ellipse, flip_h, flip_v)`
  - `draw_text(text, position, font, style)`
  - `draw_text_box(text, rect, font, style, align, wrap, valign)`
  - `text_bounds(text, rect, font, align, wrap)`
  - `draw_rect(rect, style)`
  - `push_state(opacity, translate, rotate, clip, antialias, clip_ellipse, flip_h, flip_v)`
  - `pop_state()`
  - `draw_image(data, rect, smooth, wash, source_rect)`
  - `apply_image_effects(data, rect, ellipse, effects)`
  - `draw_effects_behind(data, rect, ellipse, effects)`
  - `draw_text_effects(text, font, origin, color, effects, contour, highlight, width, line_height, ascent, underline)`
  - `draw_text_path(text, font, origin, style)`
  - `draw_shadow(ops, color, blur, dx, dy)`
  - `draw_path(ops, style, antialias, union)`
  - `draw_ellipse(center, rx, ry, style)`
  - `draw_line(start, end, style)`
- **class `RenderBackend`**
  - `state(opacity, translate, rotate, clip, antialias, clip_ellipse, flip_h, flip_v)` — Zeichenzustand begrenzt ändern und bei jedem Ausgang sicher wiederherstellen.
  - `draw_text(text, position, font, style)`
  - `draw_text_box(text, rect, font, style, align, wrap, valign)` — Text in einem Rechteck: vertikal nach ``valign`` ("top", "center"), horizontal nach ``align`` ("left", "center", "right"), mit Zeilenumbruch bei ``wrap``.
  - `text_bounds(text, rect, font, align, wrap)` — Die Fläche, die ``draw_text_box`` mit denselben Angaben belegen würde.
  - `draw_rect(rect, style)`
  - `push_state(opacity, translate, rotate, clip, antialias, clip_ellipse, flip_h, flip_v)` — Zeichenzustand sichern und ändern: Ausschnitt ``clip`` (Rechteck) oder ``clip_ellipse`` (Ellipse im Rechteck, im bisherigen Koordinatensystem), Kantenglättung, Deckkraft (mit der bisherigen multipliziert),
  - `pop_state()` — Den mit ``push_state`` gesicherten Zustand wiederherstellen.
  - `draw_image(data, rect, smooth, wash, source_rect)` — Bild aus Bytes zeichnen. ``source_rect`` wählt einen normalisierten Quellausschnitt (0…1), ohne Quelldaten zu verändern.
  - `apply_image_effects(data, rect, ellipse, effects)` — Effekte, die das Bild selbst verändern (weiche Kanten, 3D-Format, 3D-Drehung): → (neue Bilddaten als PNG, ob die Ellipsenform noch gilt).
  - `draw_effects_behind(data, rect, ellipse, effects)` — Leuchten, Schatten, Tiefe und Spiegelung hinter dem Bild.
  - `draw_text_effects(text, font, origin, color, effects, contour, highlight, width, line_height, ascent, underline)` — Eine Textzeile mit Texteffekten (Schatten, Spiegelung, Leuchten, 3D, Kontur, Füllarten …): ``origin`` = Anfang der Grundlinie, ``width`` = Breite der Zeile,
  - `draw_text_path(text, font, origin, style)` — Den Umriss der Buchstaben als Pfad füllen und/oder mit einer Kontur zeichnen (``origin`` = Anfang der Grundlinie; Füllung auch als Verlauf).
  - `draw_shadow(ops, color, blur, dx, dy)` — Schatten eines Pfades: die Fläche in ``color`` (mit ihrem Alphawert), um (dx, dy) versetzt und mit Radius ``blur`` weichgezeichnet.
  - `draw_path(ops, style, antialias, union)` — Linienzug oder Fläche aus Anweisungen: ``("M", x, y)``, ``("L", x, y)``, ``("Q", cx, cy, x, y)``, ``("C", x1, y1, x2, y2, x, y)``, ``("Z",)`` (Teilpfad schließen),
  - `draw_ellipse(center, rx, ry, style)`
  - `draw_line(start, end, style)`

### `core/rendering/dokument.py`

Zusammenspiel von Dokumentmodell, Seitenlayout und Renderbackend für eine Dokumentseite.

- `zeichne_dokumentseite(backend, dokument, layout, index, engine, zeilennummern_schrift, vor_inhalt, nach_inhalt)` — Zeichnet eine berechnete Seite samt Seitenschmuck und optionalen Adapter-Erweiterungen.

### `core/rendering/kopffuss.py`

Kopf- und Fußzeile einer Seite zeichnen, ohne Qt: Textstücke mit eigener Schrift, Farbe, Unterstreichen, Durchstreichen und Hervorheben, Zeile für Zeile ausgerichtet, vertikal in der

- `schrift(grund, fmt)` — Schrift einer Kopf-/Fußzeile aus ihrem Zeichenformat (``family``, ``size_pt``, ``bold``, ``italic``, ``script`` hoch/tief verkleinert).
- `_mit_effekt(hf)`
- `zeichne_zeile(b, engine, hf, rect, text_fn, ausrichtung, grund)` — Eine Kopf- oder Fußzeile in ``rect``. ``text_fn`` ersetzt Felder (Seitenzahl …) im Text. ``False``, wenn sie Texteffekte trägt und der Aufrufer sie anders zeichnen muss.

### `core/rendering/linien.py`

Linienarten ohne Qt: einfach, gepunktet, gestrichelt, Strich-Punkt, doppelt, dreifach, Dünn-Dick-Folgen und Wellenlinien, als Zeichenanweisungen für ein ``RenderTarget``.

- `_bauen()`
- `zeichne_linie(b, farbe, breite_pt, art, x1, y1, x2, y2, massstab)` — Eine einzelne Linie in ihrer Art; ``massstab`` rechnet pt in Bildpunkte um (96/72 am Bildschirm, mal Zoom).
- `zeichne_rahmen(b, farbe, breite_pt, art, seiten, r, massstab, innen_y)` — Die gemeinten Seiten (``t``, ``b``, ``l``, ``r``; ``h`` = Linien zwischen Absätzen bei ``innen_y``) eines Rechtecks in der Linienart.
- `rahmen_aus_text(text)` — Die Rahmenangabe eines Absatzes „Farbe\|Breite pt\|Art\|Seiten\|oben,unten,links,rechts“ → (Farbe, Breite pt, Art, Seiten, Abstände pt oder ``None``).
- `zeichne_absatzrahmen(b, text, flaeche, innen_y)` — Der Rahmen um die Fläche zusammenhängender Absätze (``flaeche`` = ihre Zeilen auf der Seite), mit dem Abstand der Angabe zum Text.

### `core/rendering/objekte.py`

Bilder und Formen über das Rendering-Backend zeichnen (ohne Qt): Füllung, Bild, Ausschnitt (Ellipse), Kontur und Drehung eines Bildobjekts; Formen aus Grundformen und Pfaden.

- `heller(farbe, faktor)` — Aufhellen wie ``QColor.lighter``: der Hellwert (V) wird mit ``faktor`` / 100 multipliziert; was über 255 hinausgeht, nimmt die Sättigung weg.
- `fuellstil(f, r, bild)` — Der Stil für die Füllung eines Rechtecks; ``None``, wenn es keine Füllung gibt (oder eine Bildfüllung ohne ``bild``). ``bild``: Bytes des Füllbildes.
- `kontur_stil(s)`
- `zeichne_bild(b, obj, rect, daten, fuellbild)` — Das Bildobjekt in ``rect`` zeichnen: Drehung um die Mitte, Effekte hinter dem Bild, Füllung, Bild (bei ``ellipse`` im Oval beschnitten), Kontur innerhalb des Rechtecks.
- `zeichne_platzhalter(b, r)` — Ersatz für ein fehlendes Bild: graue Fläche mit Rahmen und Kreuz.
- `form_pfad(s, r)` — Der Umriss der einfachen Grundformen in ``r``; ``None`` für Katalogformen, die das Backend nicht aus Grundformen baut.
- `zeichne_form(b, s, rect)` — Eine Form in ``rect`` zeichnen (Schatten, Füllung, Kontur, Drehung, Deckkraft). ``False``, wenn die Art nur das Qt-Zeichnen der Anwendung kennt.

### `core/rendering/objektrenderer.py`

Objekte des Dokumentmodells (``InlineObjekt``, ``FreiesObjekt``) über das Rendering-Backend zeichnen, ohne Qt.

- `zeichne_objekt(b, dok, art, breite, hoehe, ressource, daten, rect)` — Ein Objekt in ``rect`` zeichnen.
- `zeichne_textfeld(b, obj, rect, daten)` — Ein Klartextfeld mit einem Format nativ zeichnen; für Runs, Ketten und Effekte bleibt das Bild der Rückfall.

### `core/rendering/renderer.py`

Der Dokument-Renderer: zeichnet Seiten des Layout-Ergebnisses über das Dokumentmodell auf ein ``RenderTarget``. Seitenaufbau in ``seitenrenderer.py``, Text in

- **class `DokumentRenderer`**(SeitenRenderer)
  - `zeichne_seiten(b, dok, erg, indizes, zeilennummern_schrift)` — Mehrere Seiten nacheinander auf dasselbe Ziel (der Ursprung liegt für jede Seite an ihrer linken oberen Ecke; das Ziel richtet das der Aufrufer ein).

### `core/rendering/seite.py`

Eine Seite aus dem Ergebnis des Qt-freien Seitenumbruchs (``core.layout.umbrechen``) auf ein ``RenderTarget`` zeichnen: Seitenfarbe, Tabellenzellen (Füllung, Rahmen), Absatzzeilen mit

- `zeichne_absatzrahmen_der_seite(b, erg, index)` — Die Rahmen um Absätze der Seite: aufeinanderfolgende Absätze mit gleicher Rahmenangabe teilen sich einen Rahmen (mit Linien dazwischen, wenn die Angabe „h“ nennt).
- `zeichne_freie_bilder(b, dok, erg, index, hinter)` — Frei positionierte Bilder und Formen der Absätze auf dieser Seite; Formen werden nativ gezeichnet, sofern unterstützt.
- `zeichne_seite(b, erg, index, engine, hintergrund, dok)` — Seite ``index`` des Layout-Ergebnisses: erst Seitenfarbe und Zellen (hinter dem Text), dann Zeilen, Aufzählungszeichen und Fußnoten.

### `core/rendering/seitenrahmen.py`

Der Rahmen um die Seite („Rahmen und Schattierung“ ▸ Seitenrand) ohne Qt: Lage, Abstände, Kunstrahmen und Linienrahmen als Zeichenanweisungen für ein ``RenderTarget``.

- `abstaende_pt(b)` — (oben, unten, links, rechts) in pt.
- `rechteck(b, page, seite)` — Das Rechteck des Rahmens in Bildpunkten, auf einer Seite mit dem Rechteck ``seite``.
- `_vieleck(punkte)`
- `_figur(art, mitte, groesse)` — Umriss einer Figur als Pfadanweisungen (``core.rendering.RenderTarget.draw_path``).
- `kunst_zeichnen(backend, rect, art, breite_px, farbe)` — Einen Kunstrahmen entlang der Kanten: Figuren in regelmäßigem Abstand (Zickzack als Linienzug).
- `zeichnen(backend, b, page, seite)` — Den Seitenrahmen auf eine Seite zeichnen (Linie in ihrer Art oder Kunstrahmen).

### `core/rendering/seitenrenderer.py`

Der Dokument-Renderer: zeichnet eine Seite des Layout-Ergebnisses (``core.layout.LayoutErgebnis``) über das Dokumentmodell auf ein ``RenderTarget``.

- **class `SeitenRenderer`**
  - `__init__(engine)`
  - `zeichne_seite(b, dok, erg, index, zeilennummern_schrift)` — Seite ``index`` zeichnen. Der Ursprung des Backends liegt an der linken oberen Ecke der Seite.
  - `_satz(b, satz, rect)` — Alle Zeilen eines gesetzten Textes (Note, Kopf-/Fußzeile) ab der Oberkante von ``rect``.
  - `_inline_objekte(dok, erg, seite)` — Id → ``InlineObjekt`` für die Absätze der Seite.
  - `_freie_objekte(b, dok, seite, hinten)` — Frei positionierte Objekte der Seite in Stapelreihenfolge, hinter oder vor dem Text.
  - `_absatzrahmen(b, erg, seite)` — Rahmen um Absätze: aufeinanderfolgende Absätze mit gleicher Angabe teilen sich einen Rahmen (mit Linien dazwischen, wenn die Angabe „h“ nennt).

### `core/rendering/seitenschmuck.py`

Seitenschmuck ohne Qt: Seitenfarbe, Seitenrahmen und Wasserzeichen einer Seite in der richtigen Reihenfolge und Schicht (hinter oder vor dem Text).

- `zeichne_seitenschmuck(b, engine, page, hintergrund, flaeche, rahmen, wasserzeichen)` — Seitenfarbe, Seitenrahmen und Wasserzeichen. Maße in 96-dpi-Bildpunkten, Ursprung links oben; ``flaeche`` überschreibt das Seitenrechteck.

### `core/rendering/tabelle.py`

Füllung und Rahmen einer Tabellenzelle (und eines Rahmens im Text) als Zeichenanweisungen, ohne Qt: aus den Eigenschaften des Zellformats und des Tabellenformats (Namen wie im Modell, siehe ``core/document``)

- `_farbe(b)`
- `_kante(name, r)`
- `zelle_anweisungen(rect, zelle, tabelle, rand, zoom)` — ``rect``: die Zelle auf dem Blatt; ``rand``: Rahmenstärke der Tabelle (mit Zoom); ``zelle``/``tabelle``: Eigenschaften der Formate.
- `rahmen_anweisungen(rect, rahmen)` — Füllung und Rahmenstrich eines Rahmens im Text (``rahmen``: Eigenschaften des Rahmenformats).
- `ausfuehren(backend, anweisungen)`

### `core/rendering/tabellenrenderer.py`

Füllung und Rahmen von Tabellenzellen und Textrahmen des Dokumentmodells, ohne Qt: aus den Formaten (``core/document/formate.py``) entstehen

- `_fuellung(text)`
- `_kante(angabe)` — (Farbe, Breite in Bildpunkten, Art) einer Kantenangabe „Farbe\|Breite pt\|Art“; ``None`` ohne gültige Angabe.
- `_linie(b, k, r, farbe, breite, art)`
- `zeichne_zelle(b, rect, zelle, tabelle)` — Füllung und Rahmen einer Zelle auf dem Blatt (``rect``); ``zelle`` und ``tabelle`` sind die Formate.
- `zeichne_textrahmen(b, rect, rahmen)` — Füllung und Rahmenstrich eines Textrahmens im Text (``rahmen``: sein Format).

### `core/rendering/textrenderer.py`

Text auf dem Blatt zeichnen, ohne Qt: Zeilen eines gesetzten Absatzes mit Läufen (Schrift, Farbe, Unterstreichen, Hervorheben, hoch-/tiefgestellt,

- `zeichne_zeile(b, satz, zeile, rect, objekt_zeichner)` — Zeile ``zeile`` des gesetzten Absatzes; ``rect`` = ihr Rechteck auf der Seite (Oberkante der Zeile, linker Rand der Spalte).
- `_stuecke(satz, zeile)` — (Lauf, Anfang, Ende) der Stücke einer Zeile: je Lauf eines; bei Text mit Zeichen rechts nach links je Lauf und Richtungsebene.
- `zeichne_tabfuellung(b, satz, zeile, rect)` — Die Füllzeichen (Punkte, Striche, Linie) in den Strecken der Tabulatoren dieser Zeile, als Linie knapp unter der Grundlinie.
- `_woerter(text)` — Der Text in Wörter und Leerzeichen-Folgen (zusammen ergeben sie den Text).
- `zeichne_marke(b, engine, satz, marke, rect)` — Aufzählungszeichen oder Nummer links vor der ersten Zeile (wie bei Qt: Zeichen als Form, Nummer als Text).
- `zeichne_zeilennummern(b, erg, index, grund)` — Zeilennummern links neben dem Text der Seite (kleine graue Schrift, rechtsbündig), wenn die Seiteneinrichtung ``zeilennummern`` verlangt.
- `zeichne_listenmarke(b, engine, satz, marke, marke_x, rect)` — Aufzählungszeichen oder Nummer einer Liste an ihrer Stelle (``marke_x`` vom linken Rand der Spalte, wie das Layout sie liefert) in der ersten Zeile.

### `core/rendering/wasserzeichen.py`

Wasserzeichen einer Seite ohne Qt: Text oder Bild mit Lage, Größe, Drehung und Deckkraft als Zeichenanweisungen für ein ``RenderTarget``.

- `da(w)` — Ob das Wasserzeichen etwas zeigt (Text oder Bild).
- `bild_bytes(text)` — Die Bilddatei aus dem Base64-Text; ``None``, wenn sie fehlt oder kein bekanntes Bildformat ist.
- `deckkraft(w)`
- `lage(w, r, b, h)` — Mittelpunkt des Wasserzeichens (Breite b, Höhe h) im Seitenrechteck r.
- `schrift(engine, w, r)` — Schrift des Textwasserzeichens; „automatisch“ füllt die Seite (waagerecht 80 % der Breite, schräg 78 % der Diagonale).
- `zeichne(b, engine, w, r)` — Das Wasserzeichen ``w`` auf die Seite ``r`` (96-dpi-Bildpunkte) zeichnen.

### `core/rendering/wordart.py`

WordArt ohne Qt: Text mit Farbverlauf, Kontur und Schatten als Zeichenanweisungen für ein ``RenderTarget`` (die Galerie „Formatvorlage“ von WordArt).

- `masse(engine, text, schrift, pt)` — Größe des Bildes (Breite, Höhe) für den Text.
- `zeichne(b, engine, text, vorlage, schrift, pt)` — WordArt nach einer Vorlage ``(Name, Füllung oben, Füllung unten, Kontur oder None, Konturbreite, Schatten oder None)``: Schatten, dann Verlaufsfüllung mit Kontur.

## `core/textlayout`

### `core/textlayout/__init__.py`

Textsatz-Schnittstelle ohne Qt (Phase 6 der Qt-Entkopplung, siehe ``dokumentation/architektur/qt-entkopplung.md``).


### `core/textlayout/bidi.py`

Bidirektionaler Text (Unicode-Algorithmus UAX #9, ohne Qt und ohne fremde Bibliothek): Ebenen der Zeichen eines Absatzes und die Anzeigereihenfolge

- `klassen(text)`
- `hat_rechts_nach_links(text)`
- `basis_ebene(text, richtung)` — 0 (links nach rechts) oder 1 (rechts nach links): ausdrücklich nach ``richtung`` („ltr“/„rtl“), sonst nach dem ersten starken Zeichen.
- `ebenen(text, richtung)` — (Ebene je Zeichen, Basisebene) des Absatzes — ``None``, wenn weder der Text noch die Richtung rechts nach links verlangt.
- `zeilen_reihenfolge(text, e, basis, start, ende)` — Die Zeichenstellen ``start`` bis ``ende`` (ausschließlich) einer Zeile in Anzeigereihenfolge von links nach rechts (L1, L2).

### `core/textlayout/engine.py`

Die Schnittstelle des Textsatzes. Maße in Bildpunkten (96 dpi), y wächst nach unten.

- **class `FontSpec`** — Eine Schrift: Familie, Größe in Punkt, Gewicht (Qt-Skala: 400 normal, 700 fett) und Kursiv.
- **class `FontMetrics`**
- **class `GlyphPosition`** — Stelle eines Zeichens in einer Zeile: ``index`` ist die Zeichenstelle im Text, ``x`` der Abstand vom Zeilenanfang, ``advance`` die Breite.
- **class `LineBox`** — Eine umgebrochene Zeile: Zeichenbereich im Absatz, Breite, Höhe und Ausrichtung ihrer Glyphen.
- **class `TextLayoutEngine`** — Schnittstelle. Umsetzungen überschreiben alle Methoden; die Basisklasse meldet das fehlende Stück, statt zu raten.
  - `font_metrics(font)`
  - `measure_text(text, font)` — Breite eines Textes in einer Zeile (ohne Umbruch).
  - `shape_text(text, font)` — Glyphen-Positionen eines Textes in einer Zeile (ohne Umbruch).
  - `layout_paragraph(text, font, width)` — Zeilen eines Absatzes bei der Breite ``width``, mit Wortumbruch (lange Wörter an der Zeichengrenze).

### `core/textlayout/fontconfig.py`

Ersatzfamilien wie bei Fontconfig, ohne das Programm: die Regeln der Konfigurationsdateien (``/etc/fonts/conf.d``, ``~/.config/fontconfig``) werden gelesen und auf eine

- `_texte(el)`
- `_lesen_datei(pfad, regeln)`
- `regeln()`
- `familien_liste(name)` — Die Familien, die Fontconfig für ``name`` in dieser Reihenfolge ausprobieren würde (kleingeschrieben, ohne Doppelte).

### `core/textlayout/fontdb.py`

Schriftsuche ohne Qt und ohne fremde Programme: die Schriftdateien der üblichen Ordner werden mit FreeType gelesen (Familie, Schnitt) und nach

- `ersatz_von_qt(familie)` — Die Ersatzfamilie, die Qt für ``familie`` wählt (leer, wenn sie nicht in ``QT_ERSATZ`` steht).
- **class `Schnitt`**
- **class `SchriftDatenbank`**
  - `__init__(ordner)`
  - `_lesen()`
  - `familien()`
  - `hat_familie(familie)`
  - `finden(familie, gewicht, kursiv)` — Der Schnitt, der Familie, Gewicht (ab 600 fett) und Kursiv am besten trifft; ohne die Familie ihr Ersatz, sonst die Standardschrift.

### `core/textlayout/glyphen.py`

Glyphen und Vorschübe: HarfBuzz formt den Text einer Zeile, der Vorschub je Cluster verteilt sich gleichmäßig auf die Zeichen (Ligaturen, Zeichenhaufen). Ohne Qt.

- `vorschuebe(text, s)` — Vorschub je Zeichen (Bildpunkte).
- `glyphen_positionen(vorschuebe_je_zeichen)` — Stelle, Abstand vom Zeilenanfang und Breite jedes Zeichens.

### `core/textlayout/hb_engine.py`

Textsatz ohne Qt: Schriftmaße aus FreeType, Glyphen und Vorschübe aus HarfBuzz, Zeilenumbruch nach Wortgrenzen.

- **class `HarfBuzzEngine`**(TextLayoutEngine)
  - `__init__(datenbank)`
  - `_schrift(font)`
  - `font_metrics(font)`
  - `_vorschuebe(text, s)`
  - `measure_text(text, font)`
  - `shape_text(text, font)`
  - `layout_paragraph(text, font, width)`

### `core/textlayout/paragraph.py`

Absatzsatz über eine beliebige ``TextLayoutEngine``: Läufe in verschiedenen Schriften und Bilder in der Zeile, Zeilen mit Einzug und Ausrichtung

- **class `Objekt`** — Ein Bild (oder anderes Stück fester Größe) in der Zeile; steht im Text als U+FFFC. Es steht auf der Grundlinie.
- **class `SatzZeile`** — Eine gesetzte Zeile: ``box`` (Zeichenbereich, Breite, Höhe), Versatz ``x`` vom linken Rand der Spalte, ``y`` vom Absatzanfang, Zeilenhöhe ``hoehe`` (nach Zeilenabstand)
  - `ende()`
- **class `Lauf`** — Ein Stück des Absatztextes in einer Schrift (oder ein Objekt) mit seinem Stil (Farbe, Unterstreichen … für das Zeichnen).
- **class `Absatzsatz`**(TextPositionen)
  - `hoehe()`
- `_lauf_maße(engine, laeufe, richtung)` — Text, Vorschub je Zeichen, (Oberlänge, Zeilenhöhe) je Zeichen, die Läufe aus ``(text, FontSpec \| Objekt[, Stil])``, die bidirektionalen Ebenen
- `absatz_setzen(engine, laeufe, breite, ausrichtung, einzug_erste, einzug_links, einzug_rechts, zeilen_art, zeilen_wert, leer_schrift, ausschluss, tabs, tab_abstand, tab_fuell, richtung)` — Den Absatz in Zeilen setzen. ``laeufe`` = [(Text, FontSpec)] (ein Bild: (U+FFFC, Objekt)). ``einzug_erste`` gilt zusätzlich in der ersten Zeile

### `core/textlayout/schrift.py`

Eine geladene Schrift (HarfBuzz-Font samt Maßen) der Textsatz-Engine.

- **class `Schrift`**

### `core/textlayout/tabstopps.py`

Tabstopps: Breite jedes Tabulators (links, rechts, zentriert, Dezimalstopp, Standardabstand, hängender Einzug). Ohne Qt.

- `naechster_stopp(x, tabs, abstand, haengend)` — Der nächste Tabstopp rechts von ``x`` (vom linken Rand der Spalte): ein gesetzter Stopp, der linke Einzug bei hängendem Einzug, sonst das nächste Vielfache des Standardabstands.
- `tab_vorschuebe(text, adv, plan, tabs, abstand, einzug_links, einzug_erste)` — (Breite, Stopp) jedes Tabulators bei diesem Zeilenplan: bis zum nächsten Stopp; bei rechtsbündigem oder zentriertem Stopp rückt das folgende Stück an bzw. um den Stopp,

### `core/textlayout/textmessung.py`

Zeilenmaße: Zeilenhöhe nach Zeilenabstand, Oberlänge und Unterlänge einer Schrift. Ohne Qt.

- `zeilenhoehe(natuerlich, art, wert)` — Zeilenhöhe nach Zeilenabstand: ``single`` (wert ignoriert), ``proportional`` (Prozent), ``fixed`` (Bildpunkte), ``min`` (mindestens Bildpunkte).
- `zeilenmasse(engine, font)` — (Oberlänge, Unterlänge) einer Zeile in dieser Schrift: wie bei Qt auf ganze Bildpunkte aufgerundet (die Zeilenhöhe von ``QTextLine`` ist ganzzahlig).

### `core/textlayout/textpositionen.py`

Stellen im gesetzten Absatz: Zeile eines Zeichens, Zeichenpositionen, Auswahlstreifen, Schreibmarkenstelle und Treffertest (Punkt → Zeichen). Ohne Qt.

- **class `TextPositionen`** — Abfragen auf den Zeilen eines gesetzten Absatzes; setzt ``zeilen``, ``text``, ``vorschuebe``, ``ebenen``, ``basis`` und ``_zeilenpos`` voraus.
  - `zeile_von(index)`
  - `zeichenpositionen(zeile)` — Bei Text mit Zeichen rechts nach links: (Zeichenstelle → (linke, rechte Kante vom linken Rand der Spalte), Zeichenstelle → Ebene nach
  - `segment(von, bis, zeile)` — Linke und rechte Kante der Zeichen ``von`` bis ``bis`` (ausschließlich) in der Zeile, vom linken Rand der Spalte.
  - `auswahl_x(von, bis, zeile)` — Die Streifen (links, rechts) der Zeichen ``von`` bis ``bis`` in der Zeile; bei gemischter Schreibrichtung können es mehrere sein.
  - `cursor_x(index, zeile)` — Stelle des Cursors vor dem Zeichen ``index`` vom linken Rand der Spalte (in der Zeile, die ``index`` enthält, oder in ``zeile``).
  - `zeile_bei_y(y)`
  - `treffer(x, y)` — Zeichenstelle des Cursors für den Punkt (x, y) im Absatz: die Zeile nach y, darin die nächste Zeichengrenze.

### `core/textlayout/wortumbruch.py`

Wortgrenzen: wo eine Zeile enden darf (Leerzeichen, Bindestriche, weiche Trennstellen). Ohne Qt, ohne Schrift.

- `umbruch_stellen(text)` — Stellen, an denen eine Zeile enden darf: der Index des ersten Zeichens der nächsten Zeile (nach Leerzeichen, Bindestrich usw.; Zeilenumbruch erzwingt).

### `core/textlayout/zeilenumbruch.py`

Zeilenumbruch aus den Vorschüben der Zeichen: Wortumbruch, zu lange Wörter brechen an der Zeichengrenze. Ohne Qt.

- `zeilen_umbrechen(text, vorschuebe, breite, hoehe, steig)` — Zeilen aus den Vorschüben: Wortumbruch, ein zu langes Wort bricht an der Zeichengrenze. Leerzeichen am Zeilenende zählen nicht zur Breite.

## `dienste`

### `dienste/__init__.py`

Dienste: Dateien (DOCX/ODT/…), Einstellungen, Wiederherstellung, Bausteine, Vorlesen, Anbindungen.


### `dienste/bausteine.py`

Textbausteine: markierter Text mit Formatierung unter einem Namen merken und später einfügen.

- `_pfad()`
- `laden()`
- `speichern(liste)`
- `standard()` — Die mitgelieferten Bausteine (Briefe, Bewerbungen …); sie lassen sich einfügen, aber nicht ändern.
- `alle()` — Mitgelieferte und eigene Bausteine (Eigene zuletzt).
- `finde_kuerzel(kuerzel)` — Der Baustein zu einem Kürzel (Eigene gehen vor den mitgelieferten).
- `hinzufuegen(name, bloecke, kuerzel)` — Merkt den Ausschnitt (``Bearbeitungssitzung.ausschnitt``: Blöcke des Dokumentmodells) unter ``name``.
- `entfernen(name)`
- `_alte_bloecke(absaetze)` — Bausteine im älteren Format (``absaetze``: Textstücke mit ``fett``, ``kursiv`` … je Absatz) als Absätze des Dokumentmodells.
- `einfuegen(editor, baustein)` — Fügt den Baustein mit seiner Formatierung an der Schreibmarke ein; ein Eintrag ohne Blockdaten kommt als einfacher Text.

### `dienste/bild_export.py`

Das Dokument als Bild schreiben: jede Seite als eigene Datei oder alle Seiten untereinander als ein langes Bild.

- **class `BildWahl`**
- `_frei(pfad)` — Ein Dateiname, den es noch nicht gibt (nichts Vorhandenes wird überschrieben): „Brief (2).png“.
- `wasserzeichen(img, text)` — Den Text schräg und blass über das ganze Bild legen.
- `_speichern(img, pfad, fmt)`
- `bilder_schreiben(doc, page, noten, name, wahl)` — Schreibt die Bilder nach ``wahl.ordner``. → die geschriebenen Dateien.
- `_seitenbilder_schreiben(doc, page, noten, stamm, endung, faktor, wahl)`
- `_langes_bild_schreiben(doc, page, noten, stamm, endung, faktor, wahl)` — Langes Bild: zuerst die Höhe abschätzen, damit es nicht zu groß für das Bildformat wird.
- `_langes_modellbild_schreiben(modell, stamm, endung, faktor, wahl)` — Rendert ein Modell-Langbild direkt über Layout und Seitengenerator, ohne QDoc-Zwischenmodell.

### `dienste/datei_dienst.py`

Eine Stelle für alle Dateiformate: laden und speichern nach Endung.

- `endung_zum_filter(filter_text)` — Filtertext aus dem Speichern-Fenster → Endung (z. B. „OpenDocument-Text (*.odt)“ → „.odt“).
- **class `Loaded`**
- `ext(path)`
- `_verschluesselt(path)`
- `_entschluesseln(path, kennwort, ziel)`
- `_docx_lesen(path)` — DOCX → Qt-Dokument, Seiteneinrichtung, Metadaten, Bericht und optional das bereits gelesene Modell.
- `_docx_laden(path, kennwort)`
- `_txt_laden(path)` — Eine Textdatei als einfaches Textdokument (für Aufrufer, die ein ``QTextDocument`` brauchen, etwa die Dokumentensuche der KI).
- `load(path, kennwort)`
- `_kopf_pruefen(path, e)` — Ein falsch benanntes oder kaputtes Dokument wird als solches gemeldet, nicht „irgendwie“ geöffnet.
- `_has_rich_content(doc)`
- `save(path, doc, page, meta, sicherung, erwartet)` — Speichert nach Endung über den sicheren Schreibweg (``sicher_schreiben``): Temp-Datei, Prüfung, Sicherungskopie der
- `save_docx_daten(path, data, report, meta, sicherung, erwartet)` — Schreibt bereits gebaute DOCX-Bytes mit demselben Kennwort- und sicheren Austauschweg wie ``save``.
- `_als_docx(path, ziel)` — DOTX (Vorlage) und DOCM (mit Makros) sind DOCX-Pakete mit anderem Inhaltstyp des Hauptteils; für den DOCX-Leser wird nur
- `_verschluesseln(data, kennwort)`

### `dienste/docx_dokument_leser.py`

DOCX direkt in das Dokumentmodell (``core.document.Dokument``) lesen — ohne ``QTextDocument`` und ohne das bisherige Modell als Zwischenschritt.

- **class `_Nicht`**(Exception) — Etwas, das dieser Leser nicht abbildet: der Aufrufer nimmt den bisherigen Weg.
- `_name(e)`
- `_val(e, attr)`
- `_an(e, attr)` — Ein- und Ausschalter wie ``w:b``: vorhanden und nicht ausdrücklich aus.
- `_zahl(wert, standard)`
- `_farbe(wert)`
- **class `_Stile`** — Docdefaults und Formatvorlagen (mit ``basedOn``-Kette) aus ``styles.xml``.
  - `__init__(wurzel)`
  - `kette(stil_id)`
- `_rpr_dict(rpr)`
- `_ppr_dict(ppr)`
- `_bereinigt(f)`
- **class `_Leser`**
  - `__init__(pfad)`
  - `_teil(endung)` — Der Dokumentteil zu einer Beziehung (``footnotes``, ``endnotes``, ``comments``) als XML-Wurzel, sonst ``None``.
  - `_noten_lesen(endung)`
  - `_kommentare_lesen()`
  - `_kommentar_id(nummer)`
  - `_note(kind, art, f, aus)`
  - `_zeichenformat(stil_id, run_stil, rpr)`
  - `_roh(eltern, art, extra, ausser)` — Die Kinder von ``eltern``, die der Leser nicht abbildet, als XML-Texte (siehe ``docx_erhalt``).
  - `_stilkette_xml(stil_id)` — Der Stil und seine Basisstile (der allgemeinste zuerst) als XML-Texte.
  - `_zeichenvorlage(stil_id)` — Ein Zeichenstil der Datei als ``Formatvorlage`` der Art ``zeichen`` (einmal je Stil); ``None`` für den Standard-Absatzstil und unbekannte Stile.
  - `_tabellenvorlage(stil_id)` — Ein Tabellenstil der Datei als ``Formatvorlage`` der Art ``tabelle`` (einmal je Stil); der Standardtabellenstil gilt als keiner.
  - `_absatzformat(stil_id, ppr)` — Wirksames Absatzformat (Docdefaults, Stilkette, direkte Angaben) und die direkten Angaben allein. Tabulatoren der Stufen werden vereinigt, ``clear`` entfernt einen.
  - `_nummerierung()`
  - `_liste(num_id)`
  - `_bild(drawing, inline)`
  - `_zeichnung(drawing, aus)` — Eine Zeichnung im Lauf: im Text (``wp:inline``) oder frei verankert (``wp:anchor``).
  - `_objekt(drawing, huelle)` — Bild, Form oder Textfeld der Zeichnung als Objekt des Modells (``huelle``: ``wp:inline`` oder ``wp:anchor``).
  - `_frei_objekt(drawing, anker)` — Ein am Absatz oder an der Seite verankertes Bild als ``FreiesObjekt`` (Lage, Größe, Textumbruch).
  - `_laeufe(absatz_el, stil_id, aus)`
  - `_sdt_laeufe(sdt, stil_id, aus)` — Ein Inhaltssteuerelement im Text: die Läufe darin tragen ``docx_sdt`` (Gruppe und ``w:sdtPr``); der Schreiber fasst gleiche Gruppen wieder zusammen.
  - `_sdt_bloecke(sdt)` — Ein Inhaltssteuerelement zwischen Absätzen (Block): die Absätze darin, jeder mit ``docx_sdt`` (Gruppe, ``w:sdtPr``, ``w:sdtEndPr``).
  - `_lauf(r, stil_id, aus, link, marke)`
  - `_laenge(aus)`
  - `_text(text, f, aus)`
  - `_vorlage(stil_id)` — Eine eigene Formatvorlage der Datei als ``Formatvorlage`` des Modells (einmal je Stil); ``None`` bei Zeichen- und Tabellenstilen.
  - `absatz(p, ende_ok)`
  - `_rahmen(tblpr, stil_id)`
  - `_sechs_gleich(bd)` — Ob ``w:tblBorders`` alle sechs Kanten mit derselben Linie nennt (nur dann fasst das Modell sie vollständig).
  - `tabelle(tbl)`
  - `_zelle(tc)`
  - `bloecke(eltern)`
  - `_text_hf(teil, vorher)`
  - `_raise(grund)`
  - `seite(index, vorher)` — Seiteneinrichtung und Beginn des Abschnitts ``index`` (``w:sectPr`` in Dokumentreihenfolge).
  - `_ordnen(bloecke)` — Vor jeder Tabelle und am Ende eines Abschnitts steht ein Absatz.
  - `lesen()`
- `lese_docx_dokument(path)` — → ``(Dokument, PageSettings, meta, IOReport)`` oder ``None``, wenn die Datei etwas enthält, das dieser Leser nicht abbildet (dann der bisherige Weg).

### `dienste/docx_erhalt.py`

Unbekannte DOCX-Eigenschaften im Modell erhalten (ohne Qt).

- **class `Beziehung`**(ValueError) — Das Element verweist auf einen anderen Teil der Datei und lässt sich deshalb nicht allein erhalten.
- `_name(e)`
- `als_text(element)` — Ein Element mit seinen Namensraumangaben als eigenständigen XML-Text.
- `hat_beziehung(element)` — Ob das Element oder ein Nachfahre ein Attribut aus dem Namensraum der Beziehungen (``r:``) trägt.
- `sammeln(eltern, art, extra_bekannt, ausser)` — Die Kinder von ``eltern`` (``w:rPr`` …), die der Leser nicht abbildet, als XML-Texte. ``extra_bekannt``: weitere Namen, die der Aufrufer selbst übernimmt; ``ausser``:
- `ordnen(eltern, art)` — Die Kinder von ``eltern`` stabil in die Reihenfolge des Schemas bringen (Unbekanntes bleibt am Ende in seiner Reihenfolge).
- `einsetzen(eltern, texte, art)` — Erhaltene Elemente (XML-Texte) in ``eltern`` setzen und die Reihenfolge nach dem Schema herstellen. Ein Element, das es dort schon gibt, bleibt unverändert.
- `in_format(format, texte)` — ``format`` mit den erhaltenen Elementen (wenn es welche gibt).

### `dienste/docx_formen.py`

DOCX: Formen, Textfelder, Seitenrahmen, Absatzrahmen und Wasserzeichen zwischen XML und Dokumentmodell (ohne Qt).

- `_x(el, pfad)`
- `absatzrahmen_aus_xml(bdr)` — ``w:pBdr`` → Rahmenangabe des Absatzes („Farbe\|Breite pt\|Art\|Seiten\|oben,unten,links,rechts“). ``None``, wenn nichts sichtbar ist oder die Seiten verschiedene
- `absatzrahmen_zu_xml(text)` — Rahmenangabe des Absatzes → ``w:pBdr``; ``None``, wenn die Angabe nicht lesbar ist.
- `_name(e)`
- `seitenrahmen_aus_xml(pb, einstellungen)` — ``w:pgBorders`` (und die Angaben dazu in ``settings.xml``) → ``PageSettings.border``. Haben die Seiten verschiedene Linien, steht das Element zusätzlich als ``docx_roh`` im
- `seitenrahmen_zu_xml(b)` — ``PageSettings.border`` → ``w:pgBorders``.
- `seitenrahmen_einstellungen(b)` — Welche Elemente in ``settings.xml`` zum Seitenrahmen gehören: Name → an/aus.
- `ist_wasserzeichen(pict)`
- `wasserzeichen_aus_xml(pict)` — ``w:pict`` mit einer Textform „PowerPlusWaterMarkObject“ → ``PageSettings.watermark``; ``None`` für Bild-Wasserzeichen und andere Formen.
- `wasserzeichen_zu_xml(w, nummer)` — ``PageSettings.watermark`` (Text) → ``w:r`` mit ``w:pict`` für die Kopfzeile; ``None`` ohne Text.
- `ist_form(drawing)`
- `_farbe_von(fill)` — Farbe einer ``a:solidFill`` als „#rrggbb“; leer, wenn es keine einfache RGB-Farbe ist.
- `_absaetze_text(txbx)` — Text eines Textfelds (``w:txbxContent``) mit Schrift, Größe, Farbe und Fettdruck des ersten Laufs.
- `form_aus_zeichnung(drawing, huelle)` — Form oder Textfeld (``w:drawing`` mit ``wps:wsp``) → {"art", "breite", "hoehe", "alt", "daten"}; ``Beziehung`` bei Verweisen auf andere Teile (Bildfüllung …),
- `_emu(px)`
- `_absatz_xml(zeile, innen)`
- `_fuellung_xml(fuell)`
- `_linie_xml(linie, strich)`
- `zeichnung_neu(art, breite, hoehe, daten, nummer, hinter)` — XML-Text einer neuen ``w:drawing`` (Form oder Textfeld) ohne Verankerung: das Ergebnis enthält ``wp:inline``; ``zu_anker`` macht daraus die Verankerung.
- `groesse_setzen(drawing, breite, hoehe, nummer)` — Größe (``wp:extent`` und ``a:ext``) und Kennung (``wp:docPr/@id``) einer erhaltenen Zeichnung auf die Werte des Modells setzen.

### `dienste/docx_leser.py`

DOCX → QTextDocument (python-docx).

- **class `_Reader`**(LesenMetadatenMixin, LesenAbsatzMixin, LesenRunsMixin, StilMixin, TabellenMixin, SeiteMixin, ObjekteMixin, TextfeldMixin, VmlMixin)
  - `__init__(path)`
  - `_standardvorlage_sichern()` — Ein Dokument ohne Standard-Absatzvorlage (leere styles.xml kommt vor) bekommt eine leere: alles Weitere findet dann eine Vorlage
  - `run()`
  - `_nicht_unterstuetztes_melden(body)`
  - `_koerper_lesen(body)`
  - `_meta_lesen()`
- `_kinder(eltern)` — Die Blockelemente eines Körpers; Inhaltssteuerelemente (``w:sdt``) werden aufgelöst.
- `_schriften_ersatz()` — DOCX-Schriften ohne Entsprechung im System ersetzt Qt sonst durch irgendeine breite Schrift (so wurde aus „Calibri Light“ Noto Sans).
- `read_docx(path)` — → (QTextDocument, PageSettings, meta-dict, IOReport). Wirft DocumentIOError.

### `dienste/docx_modell_leser.py`

DOCX → ``core.document.Document`` direkt, ohne ``QTextDocument`` als Zwischenschritt (Phase 5b der Qt-Entkopplung).

- **class `NichtImModell`**(Exception) — Der Leser braucht etwas, das das Modell an dieser Stelle noch nicht aufnimmt.
- **class `_Absatz`**
  - `__init__(bf, cf)`
- **class `_Fertig`** — Ein schon fertiger Block des Modells (zum Beispiel ein schwebendes Bild mit seinem Anker), der vor dem aktuellen Absatz steht.
  - `__init__(block)`
- **class `_BlockRef`**
  - `__init__(a)`
  - `isValid()`
  - `blockFormat()`
  - `__getattr__(name)`
- **class `_ListRef`**
  - `__init__(nummer)`
  - `add(block)`
- **class `_ZelleRef`** — Eine Zelle der Tabelle: Format und Verbundenes rechnet die Zelle der Hilfstabelle (``_TabelleRef``), der Inhalt geht in eine eigene Schreibmarke.
  - `__init__(tabelle, zelle)`
  - `firstCursorPosition()`
  - `lastCursorPosition()`
  - `begin()`
  - `__getattr__(name)`
- **class `_TabelleRef`** — Eine Tabelle im Modell. Formate, Verbinden und Zellformate rechnet eine kleine Hilfstabelle von Qt (wie bisher, nur ohne Inhalt); der Inhalt jeder Zelle steht in einer eigenen Schreibmarke.
  - `__init__(rows, cols, tf, bilder)`
  - `inhalt(r, c)`
  - `_zellformat_ersetzen(r, c, cf)` — Wie in Qt: Das Zeichenformat des ersten Absatzes einer Zelle ist das Format der Zelle selbst; es setzt ein früheres Zellformat zurück.
  - `cellAt(r, c)`
  - `__getattr__(name)`
  - `als_modell()`
- **class `ModellCursor`** — Die Schreibmarke des Lesers, aber in das Modell: Absätze mit Textstücken, Listen, Tabellen und Zählung der Position wie bei Qt.
  - `__init__(doc, verschachtelt, erstes_zeichenformat)`
  - `_aktuell()`
  - `insertTable(rows, cols, tf)` — Wie Qt: die Tabelle steht nach dem aktuellen Absatz, danach folgt ein leerer Absatz.
  - `als_modell()` — Die Blöcke als Modell (Absätze und Tabellen).
  - `vorab_einfuegen(bloecke, zeichen)` — Fertige Blöcke vor den aktuellen Absatz setzen; ``zeichen`` = so viele Stellen belegen sie im Qt-Dokument (die Zählung der Position bleibt wie bei Qt).
  - `insertImage(fmt)`
  - `insertBlock(bf, cf)`
  - `insertText(text, cf)`
  - `format_bereich(von, bis, nf)` — Wie ``QTextCursor.mergeCharFormat`` über [von, bis): die Textstücke werden an den Grenzen geteilt, nur der markierte Teil bekommt ``nf``.
  - `setBlockFormat(bf)`
  - `setBlockCharFormat(cf)`
  - `mergeBlockFormat(bf)`
  - `blockFormat()`
  - `block()`
  - `createList(lf)`
  - `position()`
  - `__getattr__(name)`
- **class `_ModellReader`**(docx_leser._Reader) — Der alte Leser mit einer Modell-Schreibmarke.
  - `__init__(path)`
  - `_zelle_ende(qt, r0, c0)`
  - `_schwebend_setzen(cursor, imf, seite, versatz)` — Das umflossene Bild als Schwebeobjekt (Anker-Absatz und Rahmen mit dem Bild) vor den aktuellen Absatz des Modells setzen. Die Form von Anker und Rahmen baut dieselbe
  - `_zeilenhoehen(qt, table)` — w:trHeight je Zeile als Mindesthöhe übernehmen (wie der alte Leser); die Höhe des Zellinhalts kommt hier aus dem Qt-freien Textsatz (``core.layout``) statt aus dem Qt-Layout.
  - `_block_format_setzen(block, vf)`
  - `_feld_ende()` — XE-Stichworte: die Markierung des zuletzt eingefügten Textes im Modell setzen (wie ``_feld_ende`` des alten Lesers). Liegt die Stelle in
  - `_zelle_fuellen(qt, r0, c0, cell)`
  - `_zelle_mit_tabelle(qt, r0, c0, cell)` — Zelle mit verschachtelter Tabelle: der Inhalt wird mit dem Leser auf einem Hilfsdokument gebaut (Qt legt Absatz, Tabelle und den Absatz dahinter so an, wie der alte Leser es
  - `_cursor_ans_ende()`
  - `_ketten_bereinigen()`
  - `run_modell()`
- `lese_docx_modell(path)` — → ``(Document, PageSettings, meta, IOReport)`` oder ``None``, wenn das Dokument etwas enthält, das der Modell-Leser noch nicht kennt (dann ``docx_leser.read_docx`` nehmen).

### `dienste/docx_modell_schreiber.py`

DOCX direkt aus dem Dokumentmodell (``core.document.Dokument``) schreiben — ohne ``QTextDocument`` und ohne Umwandlung ins bisherige Modell.

- `_markenname(name)` — Textmarken in Word: Buchstaben, Ziffern und Unterstrich, höchstens 40 Zeichen, nicht mit einer Ziffer beginnend.
- **class `_StilHuelle`** — Ein Stil als Ziel für ``_absatzformat`` (das ``paragraph_format`` und das Element, an dem ``w:pPr`` hängt).
  - `__init__(stil)`
- **class `_Nicht`**(Exception) — Etwas, das dieser Schreiber nicht abbildet: der Aufrufer nimmt den bisherigen Weg.
- `_pruefen(dok, page, meta)`
- `_einfuegen(eltern, element, nachfolger)` — ``element`` vor das erste vorhandene Nachfolgerelement setzen (Reihenfolge nach dem Schema), sonst ans Ende.
- `_themenschrift_entfernen(stil)` — Die Schriftart eines Stils gilt nur, wenn keine Themenschrift (``asciiTheme`` …) darüber steht.
- `_farbe(wert)`
- **class `_Schreiber`**
  - `__init__(dok, page, meta)`
  - `_zeichen(run, f)`
  - `_stil_xml_einsetzen(v)` — Die Stile (Basisstile zuerst), die der Leser als XML erhalten hat, in ``styles.xml`` setzen, soweit es ihre Kennung dort noch nicht gibt.
  - `_zeichenstil(name)` — Eine Zeichenvorlage des Modells als Zeichenstil der Datei anlegen (einmal).
  - `_tabellenstil(name)` — Eine Tabellenvorlage des Modells als Tabellenstil der Datei anlegen (einmal); ``True``, wenn es sie jetzt gibt.
  - `_schattierung(eltern, fuell)` — ``w:shd`` an die schemagerechte Stelle von ``w:rPr``, ``w:pPr`` oder ``w:tcPr`` setzen.
  - `_absatzformat(para, f)`
  - `_numbering_teil()`
  - `_abstrakte_liste(lid)`
  - `_num(lid, neu_bei)`
  - `_lauf(para, x, a)`
  - `_frei(para, o)` — Ein frei verankertes Bild als ``wp:anchor`` (Lage, Größe, Textumbruch) im Absatz.
  - `_form_lauf(para, art, breite, hoehe, daten, lage)` — Form oder Textfeld als Lauf mit ``w:drawing``: das erhaltene Original (mit Größe aus dem Modell) oder, ohne Original, eine neu erzeugte Zeichnung.
  - `_form_frei(para, o)`
  - `_verankern(zeichnung, o)` — Die Verankerung der Zeichnung (``wp:anchor``) mit Lage und Umbruch des Modells: Ein erhaltenes ``wp:anchor`` bekommt nur die Lage, ein ``wp:inline`` wird zum Anker.
  - `_marken(para, namen)` — Textmarken öffnen und schließen, damit genau die Läufe von ``namen`` in ihnen stehen.
  - `_marke_ende(para, name)`
  - `_feld(para, anweisung, laeufe, a)` — Ein Feld: Anfang, Anweisung, Trenner, das Ergebnis (die Läufe des Modells) und Ende.
  - `_notenreferenz(para, marke, f)` — Das Notenzeichen im Text als Verweis auf die Fuß- oder Endnote (Text der Note steht in ``footnotes.xml`` bzw. ``endnotes.xml``).
  - `_noten_teile()` — ``footnotes.xml`` und ``endnotes.xml`` mit den Texten der Noten; Trennlinien haben die Nummern −1 und 0, die Noten zählen ab 1.
  - `_kommentare()`
  - `_bildbytes(roh, breite)` — Die Bytes eines Bildes in einem Format, das Word im Bildteil annimmt (JPEG, PNG, GIF, BMP, TIFF im Original, sonst PNG); ``None`` bei unlesbaren Bildern.
  - `_bild(para, x)`
  - `absatz(container, a)`
  - `_sdt_gruppe(x)` — Die Gruppe des Inhaltssteuerelements, in dem der Lauf oder das Objekt steht (``None``: in keinem).
  - `_inhalte_schreiben(para, inhalte, a)` — Läufe, Objekte und Felder eines Stücks des Absatzes.
  - `_sdt_umhuellen(eltern, vorher, marke)` — Alles, was seit ``vorher`` in ``eltern`` hinzugekommen ist, in ein ``w:sdt`` mit den erhaltenen Angaben (``w:sdtPr``, ggf. ``w:sdtEndPr``) setzen.
  - `_kante(angabe)`
  - `tabelle(container, t)`
  - `_block_sdt(b)`
  - `_block(container, b)`
  - `bloecke(container, bloecke, erste_leer)` — Blöcke schreiben; in Zellen gehört der vorhandene leere Absatz dem ersten Block.
  - `seite_einrichten(s, p, beginn, k, vorher)` — Seiteneinrichtung des Abschnitts ``k`` (``s``: ``Section``); Kopf- und Fußzeilen, die denen des Abschnitts davor gleichen, bleiben mit ihnen verknüpft.
  - `_seitenschmuck(s, p)` — Seitenrahmen (``w:pgBorders`` samt Einstellungen des Dokuments) und die erhaltenen Eigenschaften des Abschnitts.
  - `_wasserzeichen(s, p, k)` — Wasserzeichen mit Text als VML-Textform in der Kopfzeile (und der Kopfzeile der ersten Seite); Bild-Wasserzeichen bleiben außen vor und werden gemeldet.
  - `_spalten(s, p)` — Textspalten als ``w:cols`` (gleich breit oder mit eigenen Breiten).
  - `_abschnittsende(ab, k, vorher)` — Der Abschnitt ``k`` endet: seine Einrichtung kommt als ``w:sectPr`` in den letzten Absatz.
  - `kopf_fuss(teil, hf, davor)`
  - `_kopf_format(run, fmt)`
  - `stile()` — Die Eigenschaften der benutzten eingebauten Vorlagen aus dem Modell auf die Word-Stile übertragen.
  - `_eigener_stil(name)` — Eine eigene Absatzvorlage des Modells als Word-Stil anlegen (einmal) und ihren Namen geben.
  - `schreiben()`
- `_xml(s)`
- `docx_dokument_daten(dok, page, meta)` — Baut die DOCX-Datei im Speicher. ``None``: Das Dokument enthält etwas, das dieser Schreiber nicht abbildet (der Aufrufer nimmt den bisherigen Weg).

### `dienste/docx_schreiber.py`

QTextDocument → DOCX (python-docx).

- **class `_Writer`**(SchreibenDokumentMixin, SchreibenAbsatzMixin, SchreibenRunsMixin, SeiteSchreiber, TabellenSchreiber, ObjekteSchreiber, TextfeldSchreiber, ZusatzSchreiber)
  - `__init__(qdoc, page, meta)`
  - `_kompatibilitaet()`
  - `run()`
  - `_trim_trailing_empty()`
- `docx_daten(qdoc, page, meta)` — Baut die DOCX-Datei im Speicher. → (Inhalt, Bericht). Wirft DocumentIOError.
- `docx_modell_daten(modell, page, meta)` — Schreibt einfache Modellabsätze, eingebettete Bilder und Tabellen direkt als DOCX; ``None`` bedeutet: Modell über den Qt-Schreiber sichern.
- `write_docx(path, qdoc, page, meta, sicherung)` — Schreibt über den sicheren Schreibweg (Temp-Datei, Prüfung, Umbenennen). Wirft DocumentIOError.

### `dienste/drucken.py`

Drucken und Druckvorschau des Dokuments: dieselbe Layoutberechnung und derselbe Renderer wie die Zeichenfläche und das PDF.

- `papier_name(b_mm, h_mm)` — „A4“ für 210 × 297 (mit 2 mm Toleranz, in beiden Lagen), sonst „Benutzerdefiniert“.
- `bereich_lesen(text, gesamt)` — „1-3, 5“ → [1, 2, 3, 5]. Seiten außerhalb 1..gesamt fallen weg; ungültige Eingabe oder nichts Übriges → None.
- `seiten_nach_wahl(ein, gesamt)` — Welche Seiten das Druckfenster meint (aufsteigend); ohne gültigen Bereich alle.
- `blatt_zeichnen(p, rect, bilder, pro_blatt, rand)` — Setzt die Seitenbilder in einem Raster auf das Blatt; jedes wird ins eigene Feld eingepasst (Seitenverhältnis bleibt).
- **class `Ausgabe`** — Das Dokument einmal gesetzt; jede Seite lässt sich in beliebiger Größe rastern oder auf einen Zeichner malen (Vorschau, Druck).
  - `__init__(dokument, engine, nur_formular)`
  - `anzahl()`
  - `seite_mm(n)` — Breite und Höhe der Seite ``n`` (ab 1) in Millimetern.
  - `groesse_px(n, zoom)` — Größe der Seite n bei 96 dpi mal Zoom.
  - `malen(p, n)` — Die Seite ``n`` mit dem Ursprung links oben auf den Zeichner malen (Maße in 96-dpi-Bildpunkten).
  - `bild(n, zoom)`
- **class `Zwischenseiten`**(Ausgabe) — Die Seiten der Druckvorschau.
  - `__init__(dokument, opt)`
- `seitenzahl(dokument)`
- `vorschau_bild(dokument, nummern, breite_px)` — Die Seiten ``nummern`` (ab 1) auf die gewünschte Breite gerastert — für die Vorschau im Druckfenster.
- `drucken(printer, dokument, ein)` — Druckt nach der Wahl ``ein`` (Ergebnis des Druckfensters). → Zahl der gedruckten Blätter.

### `dienste/einstellungen_dienst.py`

Einstellungen und Pfade (XDG, über QStandardPaths). Nichts liegt im Programmordner.

- **class `Settings`** — Dünne Hülle um QSettings mit festen Schlüsseln und Vorgaben.
  - `__init__(qsettings)`
  - `get(key, default)`
  - `set(key, value)`
  - `remove(key)`
  - `get_bool(key, default)`
  - `get_int(key, default)`
  - `recent()`
  - `add_recent(path)`
  - `remove_recent(path)`
  - `clear_recent()`

### `dienste/formate.py`

Verzeichnis der Dateiformate: was Lunivo öffnen und speichern kann, was dabei unterstützt wird und was nicht.

- **class `FormatInfo`**
- `finde(endung)`
- `lesbar()`
- `speicherbar()`
- `als_markdown()` — Tabelle für Handbuch und Dokumentation (Markdown, kein HTML).

### `dienste/gelernt.py`

Das Gedächtnis der Prüfung: was dieser Mensch korrigiert oder stehen gelassen hat.

- **class `Gelernt`**
  - `__init__(pfad)`
  - `laden()`
  - `speichern()`
  - `wort_ebene(fund)`
  - `gewaehlt(fund)`
  - `merke_gezeigt(funde)` — Beim ausdrücklichen Prüfen: wer denselben Fund fünfmal stehen lässt, meint es so (Wort kommt in Ruhe).
  - `ki_vermerken(vorschlag, angenommen)` — Die Sicherheit (konfidenz) eines KI-Vorschlags und ob er angenommen wurde — für die Trefferquote je Sicherheitsstufe.
  - `ki_trefferquote(stufe)`
  - `vergessen()`

### `dienste/import_grenzen.py`

Grenzen für fremde Dokumente: werden geprüft, bevor ein Leser (DOCX, ODT, RTF) das Dokument verarbeitet.

- **class `Grenzen`**
- `_mb(n)`
- `pruefe_dateigroesse(pfad, art, grenze)` — Größe der Datei gegen die Grenze prüfen. → Größe in Byte.
- `_zu_gross(art, was)`
- `pruefe_paket(pfad, art)` — Prüft ein ZIP-Paket, bevor irgendetwas daraus gelesen wird. Wirft DocumentIOError, sonst Rückkehr ohne Wert.
- `_entpacken_zaehlen(z, info, art, grenze, rest, dtd_pruefen)` — Entpackt einen Eintrag nur zum Zählen. Prüft Größe, Gesamtgröße, Verhältnis und (bei XML) DTD/Entitäten.
- `_tiefe_pruefen(daten)`
- `sicheres_xml(daten)` — XML lesen wie ``ET.fromstring``, aber ohne DTD und Entitäten und mit Tiefengrenze. Wirft DocumentIOError.
- `lxml_parser()` — lxml-Parser für selbst gelesene Teile: keine Entitäten, kein Netz, keine DTD, keine Riesenknoten.

### `dienste/modell_laden.py`

Dateien als ``core.document.Dokument`` laden. Die vorhandenen Leser (DOCX, ODT, RTF, TXT) liefern noch das bisherige Modell; ``modell_umwandlung`` übersetzt es

- **class `ModellGeladen`**
- `lade_modell(path, kennwort)` — Datei laden und als Dokument liefern. Wirft ``DocumentIOError`` wie ``datei_dienst.load``.
- `_docx_direkt(path, kennwort)` — DOCX direkt ins Dokumentmodell lesen; ``None``, wenn die Datei etwas enthält, das der direkte Leser nicht abbildet (dann der bisherige Weg).

### `dienste/modell_speichern.py`

Das ``core.document.Dokument`` als Datei speichern. PDF entsteht aus derselben Layout- und Renderarchitektur wie die Anzeige; für DOCX, ODT, RTF und TXT

- `dokument_als_pdf(dokument, ziel, titel, autor, engine, erste, letzte)` — Das Dokument als PDF schreiben: dieselbe Layoutberechnung und derselbe Renderer wie die Zeichenfläche, ein Blatt je Seite. ``erste`` und
- `speichere_modell(path, modell, page, meta, sicherung, erwartet)` — Wirft ``DocumentIOError`` wie ``datei_dienst.save``; liefert den ``IOReport`` des Schreibens.

### `dienste/modell_umwandlung.py`

Übergang für Dateileser und -schreiber: Das bisherige Modell (``core.document.Document`` mit Qt-Formatnamen, das die vorhandenen DOCX-, ODT-, RTF- und

- `_user(name)`
- `_hex(c)`
- `_farbe_von(v)`
- `_color(text)`
- `_zahl(v, standard)`
- `zeichenformat_neu(cf)`
- `absatzformat_neu(pf)`
- **class `_AltNeu`**
  - `__init__(alt, meta)`
  - `laufen()`
  - `vorlagen()` — Die Formatvorlagen des Katalogs (eingebaute mit den Änderungen des Benutzers und die aus der Datei mitgebrachten eigenen) als Vorlagen des Dokuments.
  - `zusatzdaten()` — Kommentare, Notentexte, Quellen und Eigenschaften aus dem Meta-Wörterbuch des bisherigen Editors.
  - `ordnen(bloecke, haupttext)` — Vor jeder Tabelle und jedem Rahmen und am Ende steht ein Absatz.
  - `bloecke(inhalt)`
  - `absatz(p)`
  - `bild(r)`
  - `freie_bilder(a, roh)`
  - `liste(alt_id)` — (Definition, Ebene, Einrückung in Bildpunkten) einer Liste des bisherigen Modells. Aufeinanderfolgende Listenabsätze teilen sich
  - `rahmenformat(p)`
  - `tabelle(t)`
  - `tabellenformat(p)`
  - `zellformat(p)`
- `alt_zu_neu(alt, meta)` — Das bisherige Modell (samt Meta-Wörterbuch des Editors: Kommentare, Noten, Quellen, Eigenschaften) als ``Dokument``.
- `meta_aus_dokument(neu, meta)` — Das Meta-Wörterbuch der Schreiber aus den Zusatzdaten des Dokuments; Einträge, die das Dokument nicht kennt, bleiben aus ``meta`` erhalten.
- `zeichenformat_alt(d)`
- `absatzformat_alt(d, zeichen, liste_alt)`
- **class `_NeuAlt`**
  - `__init__(neu)`
  - `laufen()`
  - `bloecke(bloecke)`
  - `liste(nid, ebene)` — Die Liste des bisherigen Modells für eine Definition und Ebene (Einrückung ``ListIndent`` = Ebene + 1).
  - `absatz(a)`
  - `bild(x)`
  - `freies_bild(o)`
  - `rahmenformat(d)`
  - `tabelle(t)`
  - `zellformat(d)`
- `neu_zu_alt(neu)` — Das maßgebliche Modell als bisheriges Modell, für die vorhandenen Schreiber.

### `dienste/odt_bilder.py`

Bildimport und Rahmenbehandlung für den ODT-Reader.

- **class `_ODTBilder`**
  - `_bild_laden(bild)`
  - `_rahmen_bild(frame)` — Das Bild eines Rahmens. Mehrere ``draw:image``: zuerst das SVG, danach seine PNG-Ersatzgrafik (so schreibt es LibreOffice).
  - `_bild_daten(bild)`
  - `_frei_angabe(frame, form)` — Ein Rahmen am Absatz oder an der Seite, den kein Text umfließt → Angabe wie in editor/objekte/freie_bilder.py, sonst None.
  - `form(node, cur)` — Einfache freie ODT-Rechtecke und Ellipsen als native Formangabe übernehmen.
  - `rahmen(frame, cur)`

### `dienste/odt_dokument_leser.py`

ODT/FODT direkt in das Dokumentmodell (``core.document.Dokument``) lesen — ohne das bisherige Modell und ohne ``QTextDocument`` als Zwischenschritt.

- `_zeichen(p, stile)`
- `_absatz(p)`
- **class `_DokLeser`**(_Leser)
  - `__init__(*args, **kwargs)`
  - `_bytes(element)`
  - `_ressource(frame)` — Der Bildschlüssel im Dokument; bei SVG mit PNG-Ersatz zählt das SVG (wie bei LibreOffice).
  - `_frei_lage(frame, form)`
  - `_rahmen(frame, aus)`
  - `_form(node)`
  - `_lauf(text, props, aus, extra)`
  - `_note(node, props, aus)`
  - `_laeufe(node, props, aus, extra)`
  - `_liste_id(name)`
  - `_paragraph(node, listen)`
  - `_inhalte(nodes)`
  - `_liste(node, aus, stil, ebene)`
  - `_tabelle(node)`
  - `dokument()`
- `lese_odt_dokument(path, flach)` — → ``(Dokument, PageSettings, meta, IOReport)``.

### `dienste/odt_leser.py`

Qt-Importadapter für ODT und FODT (OpenDocument-Text), wenn Inhalte im Modell-Leser noch nicht vollständig abgebildet sind.

- **class `_Ort`** — Wohin der nächste Absatz kommt: ein Cursor und ob dessen Block noch leer und frei ist.
  - `__init__(cur, frei)`
- `_leerzeichen_anzahl(el)` — ``text:s``: Anzahl der Leerzeichen (1 bis 1000, bei ungültigem Wert 1).
- **class `_Leser`**(_ODTBilder, _ODTSeite, _ODTListen)
  - `__init__(inhalt, stil_wurzel, meta, bilder)`
  - `absatz(el, ort, liste)`
  - `inline(el, cur, eltern)`
  - `_inline_kind(k, cur, eltern, cf)`
  - `_note(node, cur, cf)` — ODT-Fuß-/Endnote: sichtbare Marke im Text, Inhalt in den Dokumentzusatzdaten.
  - `tabelle(el, ort)`
  - `bereich(kinder, ort)`
  - `_standardschrift()`
  - `_meta()` — Titel und Autor aus ``meta.xml`` (bzw. ``office:meta``), dazu die leeren Zusatzfelder.
  - `run()`
- `_xml(daten)`
- `read_odt(path)` — → (QTextDocument, PageSettings, meta-dict, IOReport). Wirft DocumentIOError.
- `read_fodt(path)` — Flaches ODT (eine XML-Datei).

### `dienste/odt_listen_lesen.py`

ODT lesen: Listen (``text:list``) → Listen im QTextDocument, Aufzählungs- und Nummernart aus der Listenvorlage.

- **class `_ODTListen`**
  - `listenpunkt(cur, listen, stil, ebene)`
  - `_listenart(stil, ebene)`
  - `liste(el, ort, listen, stil, ebene)`

### `dienste/odt_modell_leser.py`

Qt-freier ODT/FODT-Leser für Textabsätze, Zeichenformate und Listen.

- **class `NichtImModell`**(Exception) — ODT-Inhalt, der noch nicht ohne Qt vollständig übernommen wird.
- **class `_Stile`**
  - `__init__()`
  - `lesen(wurzel)`
  - `eigenschaften(familie, name, art)`
  - `liste_von(absatzstil)`
- `_farbe(wert)`
- `_format(p, stile)`
- `_absatzformat(p, zeichen, level, list_id)`
- **class `_Leser`**
  - `__init__(inhalt, stilelement, metaelement, bild_laden)`
  - `_runs(node, inherited, aus)`
  - `_text(text, props, aus)`
  - `_inline_bild(frame)`
  - `_listenstil(name, ebene)`
  - `_paragraph(node, listen)`
  - `_inhalte(nodes)`
  - `_repeat(node, key)`
  - `_tabelle(node)`
  - `_liste(node, out, stil, ebene)`
  - `_seite()`
  - `run()`
- `_xml(data)`
- `lese_odt_modell(path, flach)` — → (Document, PageSettings, meta, report), oder None bei Konstrukten mit Qt-Rückfall.

### `dienste/odt_modell_schreiber.py`

ODT direkt aus dem Dokumentmodell (``core.document.Dokument``) schreiben — ohne ``QTextDocument`` und ohne Umwandlung ins bisherige Modell.

- `_bild(roh)` — Das Bild hinter den Bytes; das Original (JPEG, SVG, Metafile …) bleibt für das Schreiben erhalten.
- **class `_InhaltModell`**(_Inhalt) — ``content.xml`` aus dem Modell: überschreibt die Teile von ``_Inhalt``, die am QTextDocument hängen.
  - `__init__(dok, rep)`
  - `_absatz_stil_modell(f)`
  - `_text_stil_modell(f)`
  - `_listen_stil_modell(lid)`
  - `_bild_modell(x)`
  - `_freie_objekte(a)`
  - `_note_modell(text, marke, f)`
  - `absatz_modell(a)`
  - `tabelle_modell(t)`
  - `bloecke_modell(bloecke)`
  - `xml_modell()`
- `odt_modell_daten(dok, page, meta)` — Baut die ODT-Datei im Speicher. → (Inhalt, Bericht über nicht Übernommenes).

### `dienste/odt_schreiben_basis.py`

Gemeinsame Bausteine zum Schreiben von ODT: Namensräume, Maße, Tabellen-Elemente, Bilder und frei positionierte Rahmen.

- `_mm(wert)`
- `bild_aus_format(doc, cf)` — Das Bild hinter einem Bildformat (Ressource im Dokument oder Datei), sonst None.
- `spannweite(t, r, c)` — Wie viele Spalten und Zeilen die Zelle mit Ursprung (r, c) überdeckt (gezählt, nicht columnSpan(): das liefert für
- `_odf(element, attr, inhalt)` — Ein Element des ODF-Tabellenmodells (Namensraum ``table:``) als XML-Text.
- `_laenge(px)`
- `_dekorativ(a_oder_bool)` — Das Attribut „Als dekorativ markiert“ für ``style:graphic-properties`` (so schreibt es LibreOffice: ``loext:decorative="true"``).
- `_bild_stil(name)` — Rahmenvorlage eines dekorativen Bildes im Text (sonst hat der Rahmen keine eigene).
- `_frei_stil(name, a)` — Rahmenvorlage (Familie „graphic“) für ein frei positioniertes Bild: ohne Textumfluss, vor oder hinter dem Text.
- `_bild_elemente(img, stamm, bilder)` — Die ``draw:image``-Elemente eines Bildes; die Bilddaten kommen nach ``bilder`` (Pictures/…). Original oder PNG; ein SVG wie bei LibreOffice
- `_frei_rahmen(a, img, nr, stil, bilder)` — Ein frei positioniertes Bild als draw:frame am Absatz; die Bilddaten kommen nach ``bilder`` (Pictures/…).
- `_frei_form(a, nr, stil)` — Einfache freie ODT-Form (Rechteck/Ellipse) ohne Rasterbild speichern.

### `dienste/odt_schreiber.py`

ODT (OpenDocument-Text) direkt schreiben — ohne Umwandlungsprogramm.

- `_manifest(namen)`
- `_text_zeichen(ch)` — Ein Zeichen des Dokumenttexts als ODF-Text (Sonderzeichen → Elemente, Steuerzeichen entfallen).
- `_leerzeichen_lauf(s, i)` — Mehrere Leerzeichen ab ``i`` → (ODF-Text, Länge des Laufs): ein echtes Leerzeichen plus ``text:s`` für den Rest.
- `_text_xml(s)`
- `_farbe(cf, eigenschaft, pinsel)` — Farbname des Pinsels, wenn das Format ihn gesetzt hat und er nicht leer ist, sonst ``""``.
- `_text_schluessel(cf)` — Alles am Zeichenformat, was ODF in eine Textvorlage schreibt (gleiche Schlüssel → gleiche Vorlage).
- `_text_eigenschaften(name, groesse, fett, kursiv, unter, durch, lage, farbe, hg)` — Die Attribute einer Textvorlage; nur gesetzte Eigenschaften erscheinen.
- `_absatz_vorlage_xml(name, schl)` — Eine Absatz- oder Spaltenvorlage (``schl`` wie in ``_Inhalt._absatz_stil`` bzw. ``("spalte", Prozent)``).
- `_listen_ebene_xml(stil, n)` — Eine Ebene (1–10) einer Listenvorlage: Aufzählungszeichen oder Zahlenart je nach Listenformat.
- **class `_Inhalt`** — Baut content.xml aus dem QTextDocument: Absätze, Überschriften, Zeichenformat, Listen, Tabellen, Bilder.
  - `__init__(doc, rep, meta)`
  - `_absatz_stil(bf)`
  - `_text_stil(cf)`
  - `_listen_stil(liste)`
  - `_bild(cf)`
  - `_freie_bilder(bf)`
  - `_note(text, cf)`
  - `absatz(block)`
  - `_spalten_xml(t)`
  - `_zelle_xml(t, r, c)`
  - `tabelle(t)`
  - `_listen_schliessen(listen, teile, bis)`
  - `_listenpunkt(blk, liste, listen, teile)` — Der Absatz ``blk`` als Listenpunkt von ``liste``: offene Listen auf die passende Tiefe bringen, dann Punkt öffnen.
  - `_rahmen_inhalt(it)`
  - `_vorlagen_xml()`
  - `_schriften_xml()`
  - `xml()`
- `_meta_xml(meta)`
- `odt_daten(doc, page, meta)` — Baut die ODT-Datei im Speicher. → (Inhalt, Bericht über nicht Übernommenes).
- `_verluste_melden(rep, page, meta, fmt)` — Was der direkte ODT-/RTF-Weg nicht mitnimmt — damit nichts still verloren geht.

### `dienste/odt_seite_lesen.py`

ODT lesen: Seitenvorlage (Größe, Ränder, Hintergrund, Seitenzahlart), Kopf- und Fußzeile samt Bildern → ``PageSettings``.

- `_mm(wert, standard)` — ODF-Länge → Millimeter; ohne Angabe ``standard``.
- `_hauptvorlage(wurzel)` — Die Seitenvorlage „Standard“ (sonst die erste) aus ``office:master-styles``.
- `_bereich_da(master, teil)` — Hat die Vorlage diesen Kopf bzw. Fuß (normal, erste Seite oder linke Seiten)?
- `_bereich_abstand(page, master, layout, art)` — ODF misst den Rand bis zur Kopfzeile; Lunivo bis zum Text: Höhe und Abstand der Kopf-/Fußzeile kommen zum Rand dazu.
- `_layout_anwenden(page, master, layout)`
- **class `_ODTSeite`**
  - `seite()`
  - `_linke_seiten(page, master)`
  - `_erste_seite(page, master)`
  - `_seiten_bilder(page, master)`
  - `_kopf_fuss(el)`

### `dienste/odt_seite_schreiben.py`

ODT schreiben: ``styles.xml`` — Standardschrift, Seitenvorlage (Größe, Ränder, Hintergrund), Kopf- und Fußzeile samt Bildern.

- `_absatz(hf, stil, rahmen)` — Kopf-/Fußzeilentext als ODF-Absätze; {PAGE} und {PAGES} werden zu Feldern. ``rahmen`` (frei positionierte Bilder) hängt am
- `_standard(doc)` — Standardschrift des Dokuments als Vorgabe für alle Absätze, dazu die Vorlage „Standard“.
- `_bilder_rahmen(page, bilder)` — Bilder in Kopf-/Fußzeile → (Rahmen-XML je Ort, Rahmenvorlagen); die Bilddaten kommen nach ``bilder``.
- `_hat_inhalt(hf, ort, rahmen)`
- `_aktiv(page, rahmen, art)` — Gibt es irgendwo (normal, erste Seite, gerade Seiten) einen Kopf bzw. Fuß?
- `_bereich_stil(page, art, aktiv, rand, seitenrand)` — ``style:header-style`` bzw. ``style:footer-style``: Mindesthöhe = Rest zwischen Rand und Text.
- `_ausrichtungs_stile(page)` — Absatzvorlagen der Kopf-/Fußzeilen. „außen“/„innen“: rechte (ungerade) Seiten in style:header, linke (gerade) in
- `_gespiegelt(hf)`
- `_master_teile(page, rahmen, art, aktiv)` — Die Elemente ``header``/``header-left``/``header-first`` (bzw. ``footer…``) der Seitenvorlage.
- `_seitenlayout(page, rand_oben, rand_unten, kopf_stil, fuss_stil)`
- `_styles_xml(page, doc, bilder)`

### `dienste/odt_stile.py`

ODT-Stilauflösung und Umsetzung von Zeichen- und Absatzformaten.

- **class `_Stile`** — Vorlagen und automatische Formate mit Vererbung (style:parent-style-name) und Standardformat je Familie.
  - `__init__()`
  - `lesen(wurzel)`
  - `_eintragen(s)` — Ein Kind von ``office:styles``/``office:automatic-styles`` in die passende Tabelle legen.
  - `eigenschaften(familie, name, art)` — Aufgelöste Eigenschaften (lokale Attributnamen mit Präfix, z. B. „fo:font-weight“) aus `style:<art>-properties`.
  - `liste_von(absatz_stil)`
- `_lage(pos)` — ``style:text-position`` (z. B. „super 58%“, „-33%“) → hoch-/tiefgestellt oder ``None``.
- `_farbe(wert, transparent_ok)` — Farbwert → Pinsel; ``None`` bei leerem, ungültigem (oder, wenn nicht erlaubt, „transparent“) Wert.
- `_schrift(cf, p, stile)`
- `_zeichenformat(p, stile)`
- `_absatzformat(p)`

### `dienste/odt_tabellen.py`

Tabellen aus ODT-Dokumenten in QTextDocument übernehmen.

- `_wiederholung(el, attribut)` — ``table:number-…-repeated`` (mindestens 1, höchstens ``MAX_WIEDERHOLUNG``).
- `_spannweite(zelle, attribut)`
- `_sammeln(e, breiten, zeilen)` — Spaltenbreiten (px) und Zeilen der Tabelle, auch aus Gruppen, mit aufgelösten Wiederholungen.
- `_zellen_der_zeile(zeile)`
- `_tabellenformat(breiten, spalten)`
- `_zelle_fuellen(t, r, c, zelle, ort, zeilen, spalten)` — Inhalt, Hintergrund und Verbund der Zelle (r, c) übernehmen; verdeckte Zellen bleiben leer.
- `tabelle(el, ort)`

### `dienste/odt_xml.py`

Gemeinsame XML-Namensräume und Hilfsfunktionen für ODT/FODT.

- `_kurz(attr)`
- `_q(name)`
- `_px(wert, standard)`
- `_pt(wert)`
- `_text_von(el)` — Reiner Text eines Elements samt Kindern (für Kopf- und Fußzeilen); Seitenzahl-Felder werden zu {PAGE}/{PAGES}.

### `dienste/pdf_export.py`

PDF exportieren nach der Wahl im Fenster „PDF-Datei exportieren“: Seitenbereich, Exportoptionen, Berechtigungen und Kennwörter.

- **class `PdfWahl`**
- `seiten(wahl, aktuelle)` — (erste, letzte) Seite für ``export_pdf``; ``None`` = bis zum Ende.
- `lesezeichen(wahl)`
- `nur_markierung(qdoc, anfang, ende)` — Eine Kopie des Dokuments, in der nur der markierte Teil steht (Bilder und Formate bleiben, das Original bleibt unberührt).
- `berechtigungen(wahl)` — Die Rechte als PDF-Bits (ISO 32000, Tabelle 22).
- `kennwort_fehler(wahl, bestaetigt_rechte, bestaetigt_oeffnen)` — Leer, wenn die Kennwörter passen; sonst der Hinweis für das Fenster.
- `verschluesseln(pfad, wahl)` — Die fertige PDF an Ort und Stelle verschlüsseln. Ohne Kennwort für die Berechtigungen gilt das Kennwort zum Öffnen auch dafür.

### `dienste/rtf_dokument_leser.py`

RTF direkt in das Dokumentmodell (``core.document.Dokument``) lesen — ohne das bisherige Modell als Zwischenschritt.

- `_hex(wert)`
- `_zeichenformat(z, roh)`
- `_absatzformat(roh)`
- **class `_Aufbau`**
  - `__init__(z)`
  - `liste(art)`
  - `absatz(a)`
  - `tabelle(t)`
  - `bloecke(ziel)`
- `_kopf_fuss(ziel)`
- `lese_rtf_dokument(path)` — RTF → ``(Dokument, PageSettings, meta, IOReport)``; ``None``, wenn der Zerleger etwas nicht ohne Qt auflösen kann.

### `dienste/rtf_modell_leser.py`

Qt-freier RTF-Leser für Text, Absätze, Listen und Tabellen.

- `_farbe(wert)`
- `_zeichenformat(z, roh)`
- `_absatzformat(z, roh, list_id)`
- `_absatz(z, a, listen, ids)`
- `_zelle(z, absatze, listen, ids)`
- `_ziel(z, ziel, listen, ids)`
- `_kopf_fuss(ziel)`
- `lese_rtf_modell(path)` — Lädt RTF ohne Qt; gibt bei nicht unterstützten Bildinhalten ``None`` für den bisherigen Qt-Leser zurück.

### `dienste/rtf_modell_schreiber.py`

RTF direkt aus dem Dokumentmodell (``core.document.Dokument``) schreiben, ohne ``QTextDocument`` und ohne Umwandlung ins bisherige Modell.

- **class `_RtfModell`**(_Rtf)
  - `__init__(dok, page)`
  - `farbe_hex(hexwert)`
  - `zeichen_modell(f)`
  - `bild_modell(x)`
  - `_listen_praefix_modell(a)`
  - `absatz_modell(a, in_tabelle)`
  - `_zeilenkopf_modell(t, r, breite)`
  - `_zelle_modell(z)`
  - `tabelle_modell(t)`
  - `run_modell()`
- `_absaetze(block)`
- `rtf_modell_daten(dok, page, meta)` — Baut die RTF-Datei im Speicher. → (Inhalt, Bericht über nicht Übernommenes).

### `dienste/rtf_schreiber.py`

RTF direkt schreiben — ohne Umwandlungsprogramm.

- `_bild_daten(img)` — Bildbytes und RTF-Bildart: JPEG-, EMF- und WMF-Originale bleiben es (\jpegblip, \emfblip, \wmetafile8), alles andere wird als PNG (\pngblip) geschrieben.
- `_mm(wert)`
- `_px(wert)`
- `_text(s)` — Text RTF-sicher: Steuerzeichen maskiert, alles außerhalb von ASCII als \uN? (UTF-16, mit Ersatzpaaren).
- **class `_Rtf`**
  - `__init__(doc, page)`
  - `_warn(text)`
  - `schrift(name)`
  - `farbe(c)`
  - `_zeichen_stile(cf)` — Fett, kursiv, unterstrichen, durchgestrichen, hoch-/tiefgestellt.
  - `_zeichen_farben(cf)`
  - `zeichen(cf)`
  - `bild(cf)`
  - `_ausrichtung(bf)`
  - `_listen_praefix(block, liste)` — (zusätzlicher linker Einzug, RTF-Präfix) für einen Listenpunkt.
  - `_absatz_abstaende(bf, links)` — Einzüge, Abstände, Seitenumbruch und Gliederungsebene.
  - `absatz(block, in_tabelle)`
  - `_zeilenkopf(t, r, breite)` — Zeilenanfang mit Spaltengrenzen und Zellverbindungen.
  - `_zelle(zelle)` — Inhalt einer Ursprungszelle als RTF (Absätze, verschachtelte Tabellen als Text).
  - `tabelle(t)`
  - `rahmen(frame)`
  - `kopf_fuss(art, hf, seite)` — ``seite`` 2 für die Kopf-/Fußzeile linker (gerader) Seiten: „außen“/„innen“ werden dort gespiegelt.
  - `_seite_rtf()` — Seitengröße, Ränder, Nummernformat und Startnummer.
  - `_kopf_rtf(seite)` — → (Seitenangaben, Kopf- und Fußzeilen); bei „außen/innen“ rechte (ungerade) und linke (gerade) Seiten getrennt.
  - `_tabellen_rtf()` — → (Schriftentabelle, Farbtabelle, Überschriftenstile).
  - `run()`
- `_bloecke(frame)`
- `rtf_daten(doc, page, meta)` — Baut die RTF-Datei im Speicher. → (Inhalt, Bericht über nicht Übernommenes).

### `dienste/sicher_schreiben.py`

Ein sicherer Schreibweg für alle Dokumentdateien (DOCX, ODT, DOC, RTF, TXT, PDF).

- `ziel(path)` — Tatsächliche Zieldatei: Verknüpfungen werden aufgelöst, damit die Verknüpfung erhalten bleibt.
- **class `SchreibKonflikt`**(DocumentIOError) — Die Zieldatei hat sich zwischen Öffnen (oder letztem Speichern) und jetzt verändert; es wurde nichts überschrieben.
- `stand(path)` — (Änderungszeit in ns, Größe) der Datei oder None — zum Erkennen fremder Änderungen.
- `fremd_geoeffnet(path)` — Beschreibung des Programms, das die Datei laut Sperrdatei offen hat (andere Programme legen „.~lock.<name>#“ an), sonst None.
- `fehlertext(e, path, vorhanden)` — Verständliche Meldung für einen Fehler beim Schreiben.
- `_umask()`
- `_fsync_datei(path)`
- `_fsync_ordner(ordner)`
- `_rest_muster(real)`
- `_reste_aufraeumen(real)` — Entfernt eigene Temp-Reste früherer, abgebrochener Speichervorgänge derselben Datei.
- `sperre(path)` — Verhindert, dass dieselbe Datei gleichzeitig zweimal gespeichert wird (im Programm und zwischen Lunivo-Fenstern).
- `sicherungs_ordner()`
- `_dokument_ordner(real)`
- `sicherungskopie(real)` — Kopiert die bisherige Fassung in den Sicherungsordner und räumt alte Kopien weg. → Pfad der Kopie.
- `sicherungen(path)` — Sicherungskopien einer Datei, neueste zuerst.
- `_ordner_aufraeumen(ordner, grenze)` — Zu viele oder zu alte Kopien eines Dokument-Ordners entfernen; ein leerer Ordner verschwindet.
- `sicherungen_aufraeumen(nur_ordner)` — Hält je Dokument höchstens SICHERUNGEN_JE_DOKUMENT Kopien und entfernt Kopien älter als SICHERUNG_TAGE.
- `_defekt(grund)`
- `_zip_pruefen(path, pflicht)`
- `_txt_pruefen(path)`
- `_odt_pruefen(path)`
- `_rtf_pruefen(path)`
- `_pdf_pruefen(kopf, ende)`
- `_docx_pruefen(path, kopf)`
- `_kopf_ende_lesen(path)` — (Größe, erste 8 Bytes, letztes KiB) der Datei.
- `pruefe_format(path, endung)` — Strukturprüfung der geschriebenen Datei. Wirft DocumentIOError, wenn sie nicht vollständig oder nicht gültig ist.
- `_ziel_pruefen(path)` — Vor dem Schreiben: (Zieldatei, Ordner, Endung-Vorgabe, vorhanden); wirft DocumentIOError bei ungültigem Ziel.
- `_stand_pruefen(real, erwartet)` — Zustand der Zieldatei in der Sperre; weicht er vom erwarteten Stand ab: SchreibKonflikt.
- `_tmp_entfernen(tmp)`
- `schreiben(path, erzeugen, *, endung, sicherung, erwartet)` — Schreibt eine Datei sicher: `erzeugen(temp_pfad)` legt die neue Fassung an, der Rest geschieht hier.
- `bytes_schreiben(path, daten, *, endung, sicherung, erwartet)`

### `dienste/textsatz.py`

Die Textsatz-Maschine der Anwendung: eine Stelle, die sagt, welche ``TextLayoutEngine`` Schriftmaße und Umbruch liefert.

- `standard_engine()` — Die Qt-freie HarfBuzz/FreeType-Engine für Kernlayout und Modellrendering.
- `engine_setzen(engine)` — Andere Engine einsetzen (Tests, Qt-freie Umsetzung); ``None`` = Standard.

### `dienste/txt_modell.py`

Qt-freie Ein- und Ausgabe einfacher Textdateien über das Dokumentmodell (``core.document.Dokument``).

- `textdatei_lesen(path)` — UTF-8 (mit BOM), Windows-1252 oder Latin-1 wie der bisherige Textleser dekodieren.
- `dokument_laden(path)` — Eine Textdatei als ``Dokument`` (ein Abschnitt, ein Absatz je Zeile) laden → (Dokument, Seiteneinrichtung).
- `dokument_als_text(dok, seite)` — Das Dokument als UTF-8-Text (ein Absatz je Zeile) und die Hinweise, was dabei verloren geht.

### `dienste/vektor_bilder.py`

Vektorbilder aus Textprogrammen lesen: EMF (Windows Enhanced Metafile). Das Format wird hier selbst ausgewertet — ohne fremde Programme.

- `ist_emf(blob)`
- `bild_lesen(blob)` — Ein eingebettetes Bild lesen: Pixelformate direkt, EMF/WMF über den eigenen Zeichner (auch gepackt als EMZ/WMZ). Leeres QImage, wenn es
- `_leer(img)` — Ist das Bild ganz durchsichtig? (zur Probe auf 16 × 16 verkleinert)
- `_rgb(farbe)`
- `_rechteck(b, off)`
- `_dib_bild(daten, bmi_off, bmi_len, bits_off, bits_len)` — Ein DIB (Bitmap-Kopf und Bildpunkte) als QImage; None, wenn es sich nicht lesen lässt.
- `_abbilden(p, z)` — Weltumwandlung, dann Fenster → Ansicht (Seitenumwandlung des Metafiles), dann das Zielrechteck.
- **class `_Zustand`** — Stifte, Pinsel, Schrift und Textfarbe des Zeichnens.
  - `__init__()`
- `_stock(handle)` — Vordefinierte Objekte (Bit 31 gesetzt): Pinsel 0 weiß, 4 leer; Stift 8 schwarz, 6 leer.
- `_begrenzt(breite, hoehe)`
- `_emf_kopf(blob)` — (Grenzen in Geräteeinheiten, Rahmen in 0,01 mm) aus dem Kopf; None, wenn die Datei kein brauchbares EMF ist.
- `masse_px(blob)` — Die Größe, die das Metafile auf dem Blatt haben soll (96 dpi), aus Rahmen (EMF) bzw. Platzhalterkopf (WMF); sonst None.
- `emf_zeichnen(blob, p, ziel)` — Das EMF als Vektorzeichnung in ``ziel`` malen (Maßstab folgt dem Rechteck, nichts außerhalb). False, wenn es kein lesbares EMF ist.
- `emf_bild(blob, hoehe_px, breite_px)` — Zeichnet die EMF-Datei in ein Bild. Größe: ``breite_px``/``hoehe_px`` oder aus dem Rahmen der Datei (0,01 mm), doppelt so fein wie 96 dpi,
- `_zeichnen(b, p, z)`
- `_umrissen(p, z, pfad, zeichnen)` — Form mit aktuellem Stift und Pinsel zeichnen — oder in den Pfad aufnehmen (das ist dann noch nicht gezeichnet).
- `_kurve(p, z, pfad, punkte)` — POLYBEZIER: ein Anfangspunkt, dann je drei Punkte (zwei Steuerpunkte und das Ende) als Kubikkurve.
- `_vielfach(p, z, pfad, b, d, geschlossen, breit)` — POLYPOLYGON/POLYPOLYLINE: Anzahl der Teile und Punkte, die Punktzahl je Teil, dann alle Punkte; Flächen nach Wechselregel (Löcher).
- `_mehrfach(p, z, pfad, geschlossen, punkte)`
- `_schrift(b, off)` — LOGFONTW ab ``off``: Höhe, Gewicht, Kursiv, Unterstrichen und Schriftname.
- `_text(p, b, d, z)` — EXTTEXTOUTW: Text an der Referenzposition, mit Schrift und Textfarbe des Zustands.
- `_bitmap(p, b, d, typ)` — BITBLT (76) und STRETCHDIBITS (81) mit eingebetteter Bitmap; ohne Bitmap bleibt es still.
- `ist_wmf(blob)`
- `_wmf_kopf(blob)` — (Logische Grenzen, Beginn der Datensätze, Größe in px bei 96 dpi, Spiegelung waagerecht/senkrecht); ohne Platzhalterkopf gilt ein Quadrat
- `_wmf_fenster(b, off)` — Das logische Fenster aus SETWINDOWORG/SETWINDOWEXT: die Koordinaten der Zeichenbefehle beziehen sich darauf, nicht auf den Platzhalterkopf.
- `wmf_zeichnen(blob, p, ziel)` — Das WMF als Vektorzeichnung in ``ziel`` malen. False, wenn es kein lesbares WMF ist.
- `wmf_bild(blob, breite_px, hoehe_px)` — Zeichnet die WMF-Datei in ein Bild (doppelt so fein wie 96 dpi, höchstens ``MAX_SEITE_PX``). → QImage oder None.
- `_wmf_zeichnen(b, off, p)`
- `_wmf_text(p, x, y, text, schrift, farbe, ausrichtung)`
- `_wmf_dib(p, b, d, ende)` — STRETCHDIB: Parameter (Rop, Farbe, Quellgröße, Quellausschnitt, Ziel) gefolgt von BITMAPINFO und Bildpunkten.

### `dienste/vorlesen.py`

Vorlesen: Piper (offline, gute Stimme) wenn eingerichtet, sonst der Sprachdienst des Systems (``plattform/sprachausgabe.py``).

- **class `VorlesenFehler`**(Exception)
- `piper_programm()`
- `piper_stimmen()`
- `_abspieler()`
- `piper_da()`
- `spd_da()`
- `verfuegbar()`
- `tempo_begrenzen(tempo)`
- `tempo_piper(tempo)`
- `stimmen()` — Alle wählbaren Stimmen: zuerst Piper, dann die deutschen des Sprachdienstes.
- `beenden()`
- `vorlesetext(dok, von, bis)` — Der Text des Dokuments (``Dokument``) von ``von`` bis ``bis`` (Stellen im Rohtext) zum Vorlesen. Bilder mit Beschreibung werden angesagt
- `lies_vor(text, stimme, tempo)`

### `dienste/wiederherstellung.py`

Automatische Wiederherstellung.

- `recovery_dir()`
- **class `RecoveryEntry`**
  - `meta_path()`
- `new_token()`
- `paths(token)`
- `write_meta(token, original, title)`
- `discard(token)`
- `pending(exclude)`
- `zwischenstand(token, title, tage)` — Legt eine Kopie der Sicherung unter staende/ ab und löscht Kopien, die älter als `tage` sind.

## `dienste/docx_teile`

### `dienste/docx_teile/__init__.py`


### `dienste/docx_teile/lesen_absatz.py`

DOCX lesen: Absatz – fachlich gekapselte Verarbeitung.

- `_listeneintraege(liste)` — Anzeigetexte der Einträge einer Auswahlliste (w:listItem), ersatzweise deren Werte.
- **class `LesenAbsatzMixin`** — Fachliche Teilverantwortung des DOCX-Readers.
  - `_sicher(fn, *a)`
  - `_para_attr(getter, pf, st)` — Absatzeigenschaft: direkt, aus Vorlage, Tabellenstil und zuletzt aus den Dokumentvorgaben.
  - `_para_doc_defaults()` — Die niedrig priorisierten Absatzvorgaben aus ``w:docDefaults/pPrDefault`` als python-docx-Format.
  - `_block_format(para)`
  - `_bf_einzuege(b, para, eff)` — Links-, Rechts- und Erstzeileneinzug (Listenabsätze: Qt rückt selbst ein).
  - `_bf_abstaende(b, para, ppr, eff)` — Abstand davor/danach (auch „Automatisch“ aus Webseiten), danach der Zeilenabstand.
  - `_bf_automatisch(b, para, ppr)` — „Automatisch“ (aus Webseiten): 14 pt davor/danach; leere Absätze behalten nur ihre Höhe.
  - `_bf_zeilenabstand(b, eff)`
  - `_bf_seitenumbruch(b)` — Seiten- (und ggf. Spalten-)Umbruch vor dem Absatz; ein vorgemerkter Umbruch ist damit verbraucht.
  - `_bf_schattierung(b, para)` — Absatzhintergrund aus w:shd: Muster über Füllfarbe oder einfache Füllfarbe.
  - `_bf_tabs(b, pf)` — Tabstopps mit Art und Füllzeichen.
  - `_bf_vorlage(b, para, st)` — Überschriftenebene, Standardvorlage (Titel, Zitat …) oder eigene Formatvorlage.
  - `_bf_abschnitt(b, para)` — Letzter Absatz eines Abschnitts: der folgende Abschnitt wird hier beschrieben.
  - `_list_info(para)` — → (numId, ilvl, 'bullet'\|'decimal'\|…) oder None.
  - `_numpr_direkt(para)` — (numId, ilvl) aus w:numPr des Absatzes, sonst (None, None).
  - `_numpr_aus_vorlage(stil)` — (numId, ilvl) aus der ersten Formatvorlage der Kette mit Nummerierung, sonst (None, None).
  - `_num_format(num_id, ilvl)`
  - `_block_format_setzen(block, vf)` — Das Format eines schon geschriebenen Absatzes ändern (der Modell-Leser überschreibt das: sein Absatz ist kein ``QTextBlock``).
  - `_start_block(bfmt, cfmt, cursor, reuse)`
  - `_kontext_abstand(para)` — w:contextualSpacing: kein Abstand zwischen Absätzen derselben Vorlage (Word-Regel, Listen typisch).
  - `add_paragraph(para, cursor, reuse, in_table)`
  - `_laufe(eltern, para, cursor, href)` — Kinder eines Absatzes der Reihe nach: Läufe, Links, nachverfolgte Änderungen, Kommentar- und Textmarkenbereiche.
  - `_lauf_run(el, para, cursor, href)`
  - `_lauf_hyperlink(el, para, cursor, href)`
  - `_lauf_aenderung(el, para, cursor, href)` — Nachverfolgte Änderung (w:ins / w:del): Art, Autor und Datum gelten für die enthaltenen Läufe.
  - `_lauf_kommentar_start(el, para, cursor, href)`
  - `_lauf_kommentar_ende(el, para, cursor, href)`
  - `_lauf_textmarke_start(el, para, cursor, href)`
  - `_lauf_textmarke_ende(el, para, cursor, href)`
  - `_lauf_steuerelement(el, para, cursor, href)`
  - `_lauf_feld_einfach(el, para, cursor, href)`
  - `_lauf_durchreichen(el, para, cursor, href)`
  - `_feld_ende()`
  - `_form_meta(sdt)` — Inhaltssteuerelement → Formularfeld-Daten (JSON); eigene Felder tragen sie im Tag, fremde (aus anderen Programmen) werden aus der Art abgeleitet.
  - `_form_meta_fremd(pr, name)` — Art des fremden Steuerelements (Auswahl, Datum, Kontrollkästchen, Text) → Formularfeld-Daten oder None.
  - `_zusatz_formate(cfmt)`
  - `_zusatz_aenderung(cfmt)` — Nachverfolgte Änderung: Art, Autor, Datum.
  - `_zusatz_feld(cfmt)` — Felder, die erhalten bleiben (SEQ, CITATION): Anweisung (und Zitatschlüssel) am Zeichenformat.
  - `_block_zusatz(bfmt, para)` — Verzeichnis- und Beschriftungsabsätze an ihrer Formatvorlage wiedererkennen; Absatzrahmen aus w:pBdr.
  - `_absatzrahmen_lesen(bfmt, para)` — Absatzrahmen aus w:pBdr: Linie der ersten sichtbaren Seite, alle sichtbaren Seiten, eigener Abstand zum Text.
  - `_rahmenlinie(da)` — Linie aus der ersten sichtbaren Rahmenseite; Seiten und eigener Abstand (w:space in pt) aus allen.
  - `_toc_art(name, para)` — Art des Verzeichnisses: toc, abb, tab, index, lit — bei Überschriften nach dem folgenden Absatz.
  - `_abb_oder_tab(para)`
  - `_toc_art_nach_kopf(para)` — Verzeichnisüberschrift: die Art ergibt sich aus der Formatvorlage des folgenden Absatzes.
  - `_flush_break(cursor)`

### `dienste/docx_teile/lesen_gemeinsam.py`

DOCX lesen — gemeinsame Bausteine (Importe, Konstanten, Hilfsfunktionen), von allen Teilen benutzt. Nichts hängt hier von den Teilen ab.

- `_xp(el, ausdruck)` — XPath mit den Namensräumen von python-docx — auch für Elemente, deren Klasse kein eigenes xpath mit Namensräumen hat.
- `_emu_to_px(v)`
- `_pt_to_px(v)`
- `_style_chain(style)`
- `_doc_defaults(document)`
- **class `_NoRun`** — Platzhalter, um Absatz-Standardwerte ohne Run aufzulösen.

### `dienste/docx_teile/lesen_metadaten.py`

DOCX lesen: Metadaten – fachlich gekapselte Verarbeitung.

- **class `LesenMetadatenMixin`** — Fachliche Teilverantwortung des DOCX-Readers.
  - `_laden_zusatz()` — Kommentare (python-docx) und Fuß-/Endnoten (Teile footnotes.xml / endnotes.xml) einlesen.
  - `_kommentare_lesen()`
  - `_noten_lesen(art, blob)` — Noten einer Art („f“ Fußnoten, „e“ Endnoten) aus dem Teil in ``zus["noten"]`` ablegen; Trenner und Hinweise entfallen.
  - `_kommentare_geloest_lesen()` — Welche Kommentare die DOCX-Datei als gelöst markiert hat (Teil commentsExtended: w15:done je Absatzkennung).
  - `_geloeste_kennungen()` — Absatzkennungen (w15:paraId) der Kommentare, die in commentsExtended als erledigt (done) stehen.
  - `_quellen_lesen()` — Literaturquellen aus dem DOCX-Bibliografieteil (customXml, Namensraum …/bibliography).
  - `_quelle_lesen(q, B)` — Eine Quelle (b:Source) → Angaben des Programms (Tag, Art, Autoren, Titel, Jahr, Verlag, Ort, URL).

### `dienste/docx_teile/lesen_objekte.py`

DOCX lesen: Bilder und schwebende Objekte (Textfelder: lesen_textfelder.py).

- `_fx_farbe(el)` — (Farbe, Transparenz in Prozent) eines Effekts.
- `_fx_leuchten(el)`
- `_fx_schatten(el)`
- `_fx_reflektion(el)`
- `_fx_weich(el)`
- **class `ObjekteMixin`** — DOCX lesen: Bilder und schwebende Objekte (Textfelder: lesen_textfelder.py).
  - `_effekte_lesen(drawing)` — ``a:effectLst`` am Bild → ``fx`` (Schatten, Leuchten, Spiegelung, weiche Kanten) in den Werten des Programms.
  - `_frei(drawing, teil, inline_ok, anchored_wrap_ok)` — Ein Bild, das frei auf dem Blatt liegt (wp:anchor ohne Textumbruch) → (Angabe, QImage); ``False``, wenn es nicht darstellbar ist
  - `_frei_anker(drawing, inline_ok, anchored_wrap_ok)` — Anker des Bildes ohne Textumbruch (sonst None: das Bild steht im Text oder wird umflossen).
  - `_frei_bild_laden(blip, teil)` — Bilddaten des Verweises laden; None (mit Hinweis im Bericht), wenn sie fehlen oder nicht lesbar sind (zum Beispiel Vektorbild).
  - `_bild_platzhalter(blip)` — Platzhalterbild in der Größe, die das Dokument für das Bild vorsieht (``wp:extent``), sonst 100 × 50.
  - `_svg_ergaenzen(blip, teil, img, png_blob)` — Wie Word: hat das Bild ``a:blip/a:extLst/asvg:svgBlip``, ist das SVG die Quelle und die PNG-Ersatzgrafik nur die Rasterfassung.
  - `_duoton_anwenden(drawing, img)` — Zweifarbig umgefärbt (zum Beispiel grau statt grün).
  - `_frei_groesse(anker, img)` — Breite und Höhe in Bildpunkten aus wp:extent, sonst aus dem Bild (oder 100 × 50).
  - `_frei_rand(drawing)` — Umrandung der Form (der weiße Ring um ein Foto) → {b, farbe, art} oder None.
  - `_frei_darstellung(angabe, drawing, tf_daten)` — Umrandung, Effekte, Beschreibung, Art (Textfeld, Form, Diagramm …) oder Zuschneideform ergänzen.
  - `_frei_zuschnitt(angabe, drawing)` — Zuschnitt (Tausendstel Prozent).
  - `_frei_helligkeit(angabe, drawing)` — Helligkeit/Kontrast (Tausendstel Prozent).
  - `_frei_fuellung(angabe, drawing)` — Füllung der Form hinter dem Bild.
  - `_frei_drehung(angabe, drawing)`
  - `_frei_lage(angabe, anker)` — Bezug und Ausrichtung/Versatz je Achse (wp:positionH / wp:positionV).
  - `_frei_maske(drawing)` — Die Zuschneideform eines Bildes (``{"maske": …}`` im Titel, „lunivo:“), sonst leer.
  - `_frei_objekt_daten(drawing)` — (Art, Daten) eines freien Objekts Form, Diagramm oder SmartArt aus dem Titel („lunivo:“) des Bildes, sonst None.
  - `_freiform_punkte(el)` — Der Pfad einer frei gezeichneten Form (a:custGeom) als Punkte der Freiform: [Typ, x, y] mit x, y als Anteil 0..1 der Pfadgröße.
  - `_form_aus_docx(drawing)` — Eine gezeichnete Form (wps:wsp mit Geometrie aus dem Formkatalog) als Form-Daten des Programms; None, wenn es keine solche
  - `_gruppe_einfuegen(drawing, cursor)` — Eine Gruppe (wpg) als einzelne freie Objekte: jedes Teil an seiner Lage in der Gruppe, mit der Größe der Gruppe skaliert.
  - `_gruppe_platz(inline, cursor)` — Eine Gruppe im Text (wp:inline) steht wie ein Bild in der Zeile und nimmt ihre Höhe ein. Ihre Teile sind frei am Absatz verankert und
  - `_gruppe_blaetter(xfrm, o_x, o_y, skala_x, skala_y)` — Alle Teile einer Gruppe als (Element, Lage x, Lage y, Breite, Höhe) in EMU, bezogen auf den Ursprung der obersten Gruppe.
  - `_gruppe_blatt(leaf, bw, bh_)` — Ein Teil einer Gruppe → (Angabe, Bild) wie ``_frei``; None, wenn es nicht darstellbar ist (mit Hinweis).
  - `_schwebend_setzen(cursor, imf, seite, versatz)` — Das umflossene Bild als Schwebeobjekt vor den Absatz des Cursors setzen; geschrieben wird danach am Ende dieses Absatzes weiter.
  - `_umbruch_form(drawing, cursor)` — Gezeichnete Form, die den Text umfließt (wrapSquare/Tight/Through): wie ein umflossenes Bild als Schwebeobjekt am Absatz.
  - `_add_image(drawing, cursor, cfmt)`
  - `_frei_einfuegen(frei, cursor)` — Frei positioniertes Bild als Ressource ablegen und am Absatz verankern.
  - `_bild_im_text_laden(drawing)` — Bild eines Verweises im Text; None (mit Hinweis im Bericht), wenn keines da, die Daten fehlen oder nicht lesbar sind.
  - `_dekorativ(drawing)` — Ist das Bild wie in Word als dekorativ markiert (``wp:docPr/a:extLst/a:ext/adec:decorative val="1"``)?
  - `_bildformat(drawing, name, w, h)` — Bildformat mit Größe, Beschreibung (Alternativtext) und den Daten eines eigenen Objekts („lunivo:“-Titel).

### `dienste/docx_teile/lesen_runs.py`

DOCX lesen: Runs – fachlich gekapselte Verarbeitung.

- **class `LesenRunsMixin`** — Fachliche Teilverantwortung des DOCX-Readers.
  - `_add_run(run, para, cursor, href)` — → True, wenn Text oder Bild eingefügt wurde.
  - `_im_feldcode()` — Steht das Lesen gerade in der Anweisung eines Felds (zwischen begin und separate)?
  - `_link_format(cfmt, href)` — Zeichenformat eines Hyperlinks: Ziel, QuickInfo, blaue Unterstreichung.
  - `_fldchar_lesen(child, run, para)` — Feldzeichen: begin öffnet ein Feld, separate wechselt zum Ergebnis (→ neues Zeichenformat), end schließt es.
  - `_run_text(child, cursor, cfmt)`
  - `_run_tab(child, cursor, cfmt)`
  - `_run_umbruch(child, cursor, cfmt)` — Seiten-/Spaltenumbruch wird für den Absatzwechsel vorgemerkt, sonst weicher Zeilenumbruch.
  - `_run_geschuetzter_bindestrich(child, cursor, cfmt)`
  - `_run_bild(child, cursor, cfmt)`
  - `_run_alternativer_inhalt(child, cursor, cfmt)` — Textprogramme legen Formen (Foto im Kreis) in „Alternativer Inhalt“: die Wahl nehmen.
  - `_run_notenverweis(child, cursor, cfmt)` — Fuß-/Endnotenverweis als hochgestellte Marke mit Verweis auf die Note.
  - `_note_marke(art, n)`
  - `_umbruch_versatz(drawing)` — Waagerechter Versatz vom Spaltenrand (wp:posOffset der Lage) in px; 0, wenn die Lage eine Ausrichtung ist oder fehlt.
  - `_umbruch_seite(drawing, breite_px)` — „links“/„rechts“, wenn das Bild den Text umfließt (wrapSquare/Tight/Through); sonst leer.
  - `_eigene_vorlage(st, b)` — Eine selbst angelegte Absatzvorlage des Dokuments: der Absatz behält ihren Namen; fehlt sie im Katalog, wird sie übernommen.
  - `_vorlage_uebernehmen(st)` — Schrift, Abstände, Ausrichtung und Einzug der DOCX-Vorlage in den Katalog der Formatvorlagen übernehmen.
  - `_vorlagenfarbe(f)`

### `dienste/docx_teile/lesen_seite.py`

DOCX lesen: Seitengröße, Ränder, Abschnitte, Kopf- und Fußzeilen.

- `_kante_sichtbar(x)` — Hat die Rahmenkante (w:top …) eine sichtbare Linie?
- **class `SeiteMixin`** — DOCX lesen: Seitengröße, Ränder, Abschnitte, Kopf- und Fußzeilen.
  - `read_page()` — Einrichtung des ERSTEN Abschnitts; weitere Abschnitte stehen als Umbrüche im Text (siehe editor/seite/abschnitte.py).
  - `_mass_roh(s, quelle)` — Ein Seitenmaß, das als Kommazahl in der Datei steht (im Format nicht erlaubt, kommt aber vor): gerundet lesen.
  - `_abschnitt_sichern()` — Ein Dokument ohne Abschnittsangabe (w:sectPr fehlt, im Dateiformat erlaubt) bekommt eine leere: alles Weitere liest dann die
  - `_section_page(s, erster, basis)`
  - `_hf_bilder(teil, ort, s, ps)` — Frei positionierte Bilder einer Kopf- oder Fußzeile (zum Beispiel ein Band über dem Briefkopf). „Am Absatz“ wird auf das Blatt
  - `_hf_abstand_mm(s, ort)` — Abstand der Kopf- bzw. Fußzeile vom Seitenrand in mm (ersatzweise 12,7).
  - `_hf_bild_im_text(angabe, dr, ort, s, ps)`
  - `_hf_bild_am_absatz(angabe, ort, s, ps)`
  - `_abschnitt_beginn(s)`
  - `_seitenschmuck(ps, sect)` — Seitenfarbe, Zeilennummern, Spalten, Standardtabstopp, Silbentrennung und Seitenrahmen.
  - `_spalten_lesen(ps, co)`
  - `_spaltenraster(co, n)` — Ungleich breite Spalten (``w:equalWidth="0"`` mit ``w:col`` je Spalte: Breite und Abstand danach in Zwanzigstelpunkt) → [[Breite, Abstand]] in mm,
  - `_standardtabstopp(dt)` — Standardtabstopps des Dokuments (Twips) in die Textoptionen übernehmen.
  - `_seitenrahmen_lesen(ps, pb)` — Seitenrahmen (w:pgBorders): Linie der ersten sichtbaren Kante, Seiten, Kunstrahmen, Abstände und Einstellungen des Dokuments.
  - `_seitenrahmen_linie(pb, e)` — Seiten mit Linie, Farbe, Stärke, Art und Abstand zum Seitenrand aus der ersten sichtbaren Kante ``e``.
  - `_seitenrahmen_zusatz(border, pb, wert)` — Kunstrahmen, Messung vom Text, Abstände je Seite, Vordergrund und die Einstellungen des Dokuments (Kopf-/Fußzeile, Ausrichtung).
  - `_aussen_innen(s, ps)` — Gerade Seiten mit gespiegelter Ausrichtung bei gleichem Text: das ist „außen“ (ungerade rechts) bzw. „innen“ (ungerade links).
  - `_gerade_zeile(ps, attr, teil)` — Kopf- bzw. Fußzeile der geraden Seiten: gespiegelt (außen/innen) oder eigene Zeilen.
  - `_seitenzahl_art(s, ps)` — w:pgNumType: Zahlenart, „Beginnen mit“, Kapitelnummer.
  - `_hf(part)`
  - `_hf_laeufe(part, text)` — Textstücke der Kopf-/Fußzeile mit ihrem eigenen Format (Zeilen durch „\n“ getrennt). Leer, wenn Felder im Spiel sind
  - `_hf_format(part)` — Zeichenformat der Kopf-/Fußzeile (Schrift, Größe, fett, kursiv, unterstrichen, Farbe) aus dem ersten Textlauf mit Text.
  - `_hf_zeichenformat(run, p)` — Zeichenformat eines Laufs als Schlüssel für ``HeaderFooter.fmt`` (Schrift, Größe, fett, kursiv, unterstrichen, Farbe).
  - `_hf_absatztext(p)` — Text eines Kopf-/Fußzeilenabsatzes; Seitenzahlfelder werden zu {PAGE} / {PAGES}, ihr zwischengespeicherter Wert entfällt.
  - `_hf_elementtext(el, ueberspringen)` — Beitrag eines Elements zum Text: Text, Tabulator oder Platzhalter für Seitenzahl bzw. Seitenanzahl.
  - `_hf_platzhalter(anweisung)` — Feldanweisung → {PAGES} (NUMPAGES), {PAGE} (PAGE) oder leer.

### `dienste/docx_teile/lesen_stile.py`

DOCX lesen: Formatvorlagen, Schrift und Zeichenformat (Vererbung, Standardwerte, Hervorhebung).

- **class `StilMixin`** — DOCX lesen: Formatvorlagen, Schrift und Zeichenformat (Vererbung, Standardwerte, Hervorhebung).
  - `_standard_stil(art)`
  - `_ps_name(para)` — Name der Absatzvorlage; leer, wenn das Dokument keine (auch keine Standardvorlage) hat.
  - `_ps(para)` — Absatzvorlage (mit Zwischenspeicher).
  - `_rs(run)`
  - `_kette(style)`
  - `_style_attr(style, getter)`
  - `_stil_font(style, attr)`
  - `_design_schriften()` — Schriften des Dokumentdesigns (word/theme): {"major": Überschriften, "minor": Fließtext}; leer, wenn es kein Design gibt.
  - `_schriftname_rpr(rpr)` — Schrift aus w:rFonts: der Name selbst oder, bei einem Verweis auf das Design (asciiTheme), dessen Schrift.
  - `_schriftname(font)`
  - `_font_name(run, para)`
  - `_standard_schrift()` — Schrift aus den Dokumentvorgaben (w:docDefaults), auch als Verweis auf das Design.
  - `_stil_farbe(style)` — Schriftfarbe (#rrggbb) aus der Vorlage oder ihren Basisvorlagen.
  - `_font_size_pt(run, para)`
  - `_font_size_gesetzt(run, para)` — Größe am Lauf, sonst aus dessen Zeichenvorlage, sonst aus der Absatzvorlage; sonst None.
  - `_font_size_ersatz(para)` — Standardgröße einer Überschrift oder benannten Vorlage, wenn nirgends eine Größe steht; sonst None.
  - `_flag(run, para, attr)`
  - `_heading_level(para)`
  - `_char_format(run, para)` — Zeichenformat eines Textlaufs. Es hängt nur von dessen Eigenschaften (rPr) und den Vorlagen von Lauf und Absatz ab; Läufe mit gleichem
  - `_char_format_roh(run, para)`
  - `_cf_stil(run, para, f)` — Fett, Kursiv (auch aus Überschrift und Standardvorlage) und das Unterstreichungs-Kennzeichen.
  - `_cf_unterstreichung(run, f)` — Besondere Unterstreichungsarten (doppelt, gestrichelt, wellig …) als eigenes Zeichenformat.
  - `_cf_kontur_abstand(run, f)` — Kontur, verborgener Text, Zeichenabstand.
  - `_cf_hochtief_farben(run, para, f)` — Durchgestrichen, Hoch-/Tiefstellung, Schriftfarbe, Hervorhebung, Versalien.
  - `_farbe_auto(run)` — Der Lauf verlangt ausdrücklich „automatisch“ (w:color w:val="auto"): die Farbe der Vorlage gilt dann nicht.
  - `_schrift_zusatz(rpr, f)` — Schrift für asiatische und komplexe Zeichen, Betonungszeichen und doppeltes Durchstreichen (Fenster „Schriftart“).
  - `_zs_schriften(rpr, f)` — Schrift für asiatische (eastAsia) und komplexe (cs) Zeichen; weitere Familien kommen hinter die Hauptschrift.
  - `_zs_komplex_schnitt(rpr)` — Schnitt („Fett Kursiv“) und Größe der komplexen Schrift → (Schnitt, Größe in pt als Text).
  - `_zs_skalieren_position(rpr, f)`
  - `_zs_raster_durchstreichung_betonung(rpr, f)`
  - `_highlight(run)`
  - `_ausrichtung(para, st)` — w:jc roh lesen — python-docx kennt „start“/„end“ nicht und bricht sonst ab.

### `dienste/docx_teile/lesen_tabellen.py`

DOCX lesen: Tabellen (verbundene Zellen, Rahmen, Maße, Zeilenhöhen).

- `_px(tw)` — Zwanzigstelpunkte → Bildpunkte.
- **class `TabellenMixin`** — DOCX lesen: Tabellen (verbundene Zellen, Rahmen, Maße, Zeilenhöhen).
  - `_zelle_format(qcell, cell)` — Zellenschattierung (w:shd) und senkrechte Ausrichtung (w:vAlign) aus der DOCX-Zelle.
  - `_zellrahmen(cf, tc)` — Rahmen je Seite der Zelle (w:tcBorders): Stärke aus w:sz (Achtelpunkt), Farbe, Art. Ein ausdrücklich fehlender Rahmen
  - `add_table(table, cursor)` — Tabelle an der Schreibmarke einfügen; mit ``cursor`` in eine Zelle (verschachtelte Tabelle).
  - `_cursor_ans_ende()` — Nach einer Tabelle weiterschreiben: am Ende des Dokuments (der Modell-Leser überschreibt das; seine Schreibmarke steht schon im Block nach der Tabelle).
  - `_zellbereiche(table, rows, cols)` — Zellen mit Rechteck: {id: [Zeile0, Spalte0, Zeile1, Spalte1, Zelle]}. Jede Zeile wird nach ihren eigenen Spannweiten (gridSpan)
  - `_zelle_fuellen(qt, r0, c0, cell)` — Absätze der Zelle in die Qt-Zelle schreiben; verschachtelte Tabellen werden gemeldet, nicht dargestellt.
  - `_zelle_ende(qt, r0, c0)` — Schreibmarke am Ende der Zelle.
  - `_innenabstand_oben_unten(qt, table, rows, cols)` — Oben und unten: der Innenabstand aus w:tblCellMar, sonst 0 — wie Word. Qt setzt sonst den seitlichen Wert auch oben und unten.
  - `_kopfzeilen(qt, table)` — Aufeinanderfolgende Kopfzeilen (w:tblHeader) ab der ersten Zeile.
  - `_tw(el)` — (Art, Wert) eines Maßelements (w:tblW, w:tcW, w:tblCellMar-Kante …); Art ``dxa``/``pct``/``auto``, Wert in Zwanzigstelpunkten bzw. Prozent.
  - `_tabellenformat(tf, table, cols)` — Tabellenbreite, Ausrichtung, Zellabstand, Rahmen (Stärke, Farbe, Stil), Innenabstand und Spaltenbreiten aus w:tblPr/w:tblGrid/w:tcW.
  - `_tf_schwebend(tf, pr)` — Schwebende Tabelle (w:tblpPr): Qt legt den Text um einen links oder rechts schwebenden Rahmen, wie Word es tut.
  - `_tw_von(pr, pfad)` — (Art, Wert) des ersten Elements am Pfad unter w:tblPr, sonst None.
  - `_tf_breite(tf, pr)`
  - `_tf_abstaende(tf, pr)` — Innenabstand der Zellen (aus den Kanten) und Zellabstand.
  - `_tf_rahmen(tf, pr, table)` — Rahmen: Stärke, Farbe und Stil der ersten sichtbaren Kante; ohne w:tblBorders nur bei Tabellenstilen mit „Grid“.
  - `_innenkanten(qt, table, placed, rows, cols)` — Innenlinien der Tabelle (w:insideH, w:insideV) und die Außenkanten (w:top …) als Rahmen je Zelle setzen, wenn die Zelle
  - `_kantenmasse(k)`
  - `_kantenformat(k, farbe)` — (Farbe, Stil, Stärke) einer Rahmenkante; ohne Farbangabe bleibt ``farbe``.
  - `_tf_spalten(tf, table, cols)` — Spaltenbreiten: je Spalte tcW der ersten ungeteilten Zelle; fehlt tcW in der Spalte ganz, gilt die Gitterbreite.
  - `_spalten_tcw(table, cols)` — Je Spalte das Breitenmaß (w:tcW) der ersten ungeteilten Zelle → (Maße, gefunden).
  - `_spaltenlaenge(a)` — Qt-Länge aus (Art, Wert): dxa → fest, pct → Prozent; sonst None.
  - `_zeilenhoehen(qt, table)` — w:trHeight je Zeile als Mindesthöhe übernehmen (wie der Befehl „Zeilenhöhe“: Eigenschaft plus Innenabstand).

### `dienste/docx_teile/lesen_textfelder.py`

DOCX lesen: Textfelder (``wps:wsp`` mit ``wps:txbx``/``wps:linkedTxbx``) und ihre Verknüpfungsketten.

- **class `TextfeldMixin`** — DOCX lesen: Parameter von Textfeldern, Läufe darin und Verknüpfungen.
  - `_textfeld_daten(drawing, wsp)` — Die Parameter eines Textfelds (``editor/objekte/frei_objekt.py``): genau die gespeicherten aus dem Titel („lunivo:“), sonst aus dem Text des
  - `_textfeld_innen(wsp, daten)` — Innenabstand des Textes (``wps:bodyPr`` lIns/tIns/rIns/bIns, EMU) als ``innen`` [links, oben, rechts, unten] in Bildpunkten; nur wenn er
  - `_textfeld_aus_titel(drawing)` — Die vom Programm gespeicherten Parameter aus dem Titel des Objekts, sonst None.
  - `_textfeld_laeufe(wsp)` — Läufe aller Absätze des Kastens; Absätze werden durch einen Lauf mit Zeilenumbruch getrennt.
  - `_textfeld_lauf(r, t)`
  - `_textfeld_zeichen(rp, lauf)` — Fett, Kursiv, Durchgestrichen, Unterstrichen, Hoch-/Tiefgestellt.
  - `_textfeld_farben_groesse(rp, lauf)` — Schriftfarbe, Hervorhebung (Hintergrund) und Größe.
  - `_textfeld_kette(wsp, daten)` — Verknüpfung (``wps:linkedTxbx`` mit Kette und Stelle): Kennung des Felds sowie Vorgänger und Nachfolger.
  - `_ketten_bereinigen()` — Nach dem Lesen: Verweise auf Folgefelder, die es nicht gibt, entfernen.
  - `_kette_bereinigen_absatz(b, ids)` — Entfernt in den Textfeldern des Absatzes Verweise (weiter, von) auf unbekannte Felder und schreibt den Absatz neu, wenn nötig.

### `dienste/docx_teile/lesen_vml.py`

DOCX lesen: ältere Zeichnungsobjekte in VML (``w:pict``) — Textfelder, Formen und Bilder aus Versionen vor 2010.

- `_stil(el)` — Das Attribut ``style`` als Verzeichnis, z. B. {"margin-left": "12pt", …}.
- `_pt(wert)` — „12.5pt“ → 12.5; Zahlen ohne Einheit gelten als Punkt; sonst None.
- `_hex(wert)` — Farbe als „#rrggbb“, wenn VML sie so angibt; benannte Farben bleiben ungelesen.
- **class `VmlMixin`** — DOCX lesen: VML-Textfelder, -Formen und -Bilder (``w:pict``).
  - `_run_vml(child, cursor, cfmt)` — Alle VML-Objekte eines ``w:pict`` als freie Objekte einfügen. → True, wenn etwas eingefügt wurde.
  - `_vml_frei(shape)` — (Angabe, Bild) eines VML-Objekts wie ``_frei`` in lesen_objekte; None, wenn es nicht darstellbar ist (mit Hinweis).
  - `_vml_lage(angabe, stil)` — Absolute Lage (``margin-left``/``margin-top``) und Bezug (``mso-position-…-relative``) oder Ausrichtung.
  - `_vml_farben(angabe, shape)` — Füllung (``fillcolor``) und Rahmen (``v:stroke``) des Objekts an die Angabe; → (Füllfarbe, Linienfarbe, Strichstärke) für Formen.
  - `_vml_textfeld(inhalt)` — Die Parameter eines Textfelds aus den Absätzen des VML-Kastens (wie ``_textfeld_daten``).

### `dienste/docx_teile/schreiben_absatz.py`

DOCX schreiben: Absatz – fachlich gekapselte Verarbeitung.

- **class `SchreibenAbsatzMixin`** — Fachliche Teilverantwortung des DOCX-Writers.
  - `write_frame(frame, container)`
  - `_unterrahmen_schreiben(fr, container)` — Tabelle, schwebendes Bild im Rahmen oder sonstiger Rahmen (als Fließtext). → True, wenn eine Tabelle geschrieben wurde.
  - `_eigener_stil(name)` — Selbst angelegte Formatvorlage als echte DOCX-Absatzvorlage (Schrift, Größe, Farbe, Abstände, Ausrichtung).
  - `_eigener_stil_schrift(st, d)`
  - `_eigener_stil_absatz(st, d)`
  - `write_block(blk, para)`
  - `_freie_bilder_des_absatzes(bf, para)` — Frei positionierte Bilder dieses Absatzes.
  - `_toc_stilname(bf)` — DOCX-Formatvorlage eines Verzeichnisabsatzes (Inhalt, Abbildungen, Index, Literatur).
  - `_absatz_vorlage(bf, para, style_name, lvl, lst)` — Formatvorlage des Absatzes: verzeichnis, Beschriftung, Überschrift, Standardvorlage, Liste, eigene Vorlage.
  - `_absatz_einzuege(bf, para, lst)` — Ausrichtung, Einzüge (bei Listen steckt der Listeneinzug in der Vorlage) und Schreibrichtung.
  - `_absatz_abstaende(bf, para)` — Abstand davor/danach und Zeilenabstand.
  - `_absatz_umbruch(bf, para)` — Manueller Seiten- oder Spaltenumbruch vor dem Absatz.
  - `_absatz_tabs(bf, pf)` — Tabstopps mit Art und Füllzeichen.
  - `_absatz_rahmen(bf, para)` — Absatzrahmen (w:pBdr) aus der Linie des Absatzes.
  - `_absatz_schattierung(bf, para)` — Hintergrund des Absatzes: Muster (Musterart + Farben) oder einfache Füllfarbe als w:shd.
  - `_absatz_laufe(blk, para, in_head)` — Fragmente des Absatzes schreiben; zusammengehörige Formularfelder und Felder werden gebündelt.
  - `_gruppe_ende(frags, i, prop, wert)` — Index hinter dem letzten aufeinanderfolgenden Fragment mit demselben Wert der Eigenschaft.
  - `_formularfeld_schreiben(para, form, gruppe, in_head)`
  - `_feld_schreiben(para, instr, gruppe, in_head)`
  - `_stil(name)`
  - `_fldchar(para, typ)`
  - `_instr(para, text)`
  - `_apply_list(para, lst)`
  - `_new_num_instance(para)` — Eigene Zählung je Liste, damit „1.“ neu beginnt.

### `dienste/docx_teile/schreiben_dokument.py`

DOCX schreiben: Dokument – fachlich gekapselte Verarbeitung.

- **class `SchreibenDokumentMixin`** — Fachliche Teilverantwortung des DOCX-Writers.
  - `_clear_body()`
  - `_standard_tabstopp()` — Die Standardtabstopps des Dokuments als w:defaultTabStop (Twips) in die Einstellungen schreiben.
  - `_dokument_ebene(p)`
  - `_text_with_fields(para, text)`
  - `_field(para, name)`
  - `_sprache()`
  - `write_defaults()`

### `dienste/docx_teile/schreiben_gemeinsam.py`

DOCX schreiben — gemeinsame Bausteine (Importe, Konstanten, Hilfsfunktionen), von allen Teilen benutzt. Nichts hängt hier von den Teilen ab.

- `_has(fmt, prop)`
- `_rpr_einfuegen(rpr, el)` — Ein Element an ``w:rPr`` in der Reihenfolge einfügen, die das Schema verlangt.
- `absatzopt_prop()`
- `_split(text)`
- `_rstyle_hyperlink(d)`
- **class `_Body`**
  - `__init__(d)`
  - `add_paragraph()`
  - `add_table(r, c)`
- **class `_CellBox`**
  - `__init__(cell)`
  - `first_paragraph()`
  - `add_paragraph()`
  - `add_table(r, c)`

### `dienste/docx_teile/schreiben_objekte.py`

DOCX schreiben: Bilder, schwebende Objekte und ihre Verankerung (Textfelder: schreiben_textfelder.py).

- `_eins(wert)` — Wahrheitswert als OOXML-Attribut „1“/„0“.
- **class `ObjekteSchreiber`** — DOCX schreiben: Bilder, schwebende Objekte und ihre Verankerung (Textfelder: schreiben_textfelder.py).
  - `_bild_laden(imf)` — Bild aus den Dokumentressourcen oder von der Platte; bei Misserfolg Hinweis im Bericht. Große Bilder je nach Option verkleinert.
  - `_image(imf, para, seite)`
  - `_bildquelle_beziehung(run, q, speicher, muster)` — Die Originalquelle eines Bildes im passenden DOCX-Part verknüpfen (Dokument, Kopf- oder Fußzeile).
  - `_metafile_anhaengen(run, img)` — EMF/WMF wie in Word: das Bild zeigt unmittelbar auf das Original (eigener Bildteil in word/media); die PNG-Rasterfassung, mit der
  - `_svg_anhaengen(run, img)` — Wie Word: das Bild zeigt auf die PNG-Ersatzgrafik, ``a:blip/a:extLst`` verweist auf das SVG (eigener Teil in word/media).
  - `_dekorativ_setzen(run)` — Wie Word: ``wp:docPr/a:extLst/a:ext/adec:decorative val="1"``; ein dekoratives Bild hat keine Beschreibung.
  - `_docpr_setzen(run, name, wert)` — Attribut (descr, title) an wp:docPr des Bildes setzen.
  - `_frei_bild(para, a, img)` — Ein frei positioniertes Bild (siehe editor/objekte/freie_bilder.py) als wp:anchor ohne Umbruch in den Absatz schreiben.
  - `_anker_lage(tag, bezug, ausr, versatz)` — wp:positionH / wp:positionV: Ausrichtung (wp:align) oder Versatz in EMU (wp:posOffset).
  - `_frei_verankern(inline, a)` — wp:inline → wp:anchor ohne Umbruch (wp:wrapNone), Lage nach Bezug und Ausrichtung/Versatz.
  - `_bild_ellipse(run, a)`
  - `_bild_zuschnitt(run, a)` — Zuschnitt als a:srcRect (Tausendstel Prozent).
  - `_bild_helligkeit(run, a)` — Helligkeit/Kontrast als a:lum (Tausendstel Prozent).
  - `_bild_maske_titel(run, a)` — Zuschneideform: nur in Lunivo, im Titel gemerkt.
  - `_bild_drehung(run, a)`
  - `_bild_fuellung(run, a)` — Füllung des Bildes (Farbe, Verlauf, Muster); Textur und Bild bleiben im Programm.
  - `_srgb(hexwert)`
  - `_fuell_farbe(f)`
  - `_fuell_muster(f)`
  - `_fuell_verlauf(f)` — Verlauf von hell nach dunkel, von oben nach unten.
  - `_bild_rand(run, a)` — Rahmenlinie des Bildes (a:ln) mit Breite, Farbe und Strichart.
  - `_bild_effekte(run, a)`
  - `_objekt_titel(run, a)` — Form, Diagramm, SmartArt, Piktogramm: Parameter im Titel („lunivo:“) und bei Diagrammen die Beschreibung.
  - `_effekte_element(fx)` — Schatten, Leuchten, Spiegelung und weiche Kanten als ``a:effectLst`` (Längen in Punkt → EMU, Winkel in 1/60000 Grad).
  - `_verankern(run, ausrichtung)` — Macht aus dem Bild im Text (wp:inline) ein umflossenes Bild (wp:anchor, Umbruch „Quadrat“, links/rechts).

### `dienste/docx_teile/schreiben_runs.py`

DOCX schreiben: Runs – fachlich gekapselte Verarbeitung.

- **class `SchreibenRunsMixin`** — Fachliche Teilverantwortung des DOCX-Writers.
  - `write_fragment(frag, para, in_head)`
  - `_fragment_ziel(para, cf)` — Textmarken und Hyperlink des Fragments anlegen → (Elternelement der Läufe, Linkziel).
  - `_lauf_inhalt(run, chunk, kind)` — Text, Tabulator oder Zeilenumbruch in den Lauf schreiben.
  - `_indexeintrag(para, cf)` — Indexeintrag (XE-Feld) hinter dem Fragment.
  - `_textmarken(para, namen)` — Offene Textmarken schließen, neue öffnen — je Name genau ein bookmarkStart/-End-Paar.
  - `_note_verweis(run, note)`
  - `_zusatz_anwenden(run, cf)` — Kommentarbereich merken, nachverfolgte Änderung als w:ins / w:del um den Lauf legen.
  - `_steuerelement(form, wert)` — w:sdt für ein Formularfeld: Art (Text, Liste, Datum, Kontrollkästchen), Name als Titel, unsere Daten im Tag.
  - `_sdt_text(pr, m, wert)`
  - `_sdt_auswahl(pr, m, wert)`
  - `_sdt_datum(pr, m, wert)`
  - `_sdt_kasten(pr, m, wert)`
  - `_make_run(parent, para)`
  - `_hyperlink(para, href, tipp)`
  - `_format_run(run, cf, in_head, is_link)` — Zeichenformat eines Fragments auf den Lauf übertragen; die Reihenfolge der Teilschritte bestimmt die Reihenfolge in w:rPr.
  - `_run_schrift(run, cf)` — Schriftfamilie, Größe, Fett, Kursiv.
  - `_run_familie(run, cf)` — Schriftfamilie, auch für asiatische und komplexe Zeichen.
  - `_run_unterstreichung(run, cf, is_link)`
  - `_run_durchstreichung(run, cf)`
  - `_run_komplexschrift(run, cf)` — Schnitt und Größe für komplexe Zeichen.
  - `_run_rpr_zusatz(run, cf)` — Skalieren, Position, Raster, Betonung — Elemente, die python-docx nicht kennt.
  - `_run_position(run, cf, rpr)` — Hoch-/Tiefstellung in Prozent der Schriftgröße (nur ohne Hoch-/Tiefgestellt-Attribut).
  - `_run_hochtief(run, cf)`
  - `_run_farben(run, cf, is_link)` — Vordergrundfarbe (nicht bei Links, nicht Schwarz) und Hintergrund als w:shd.
  - `_run_effekte(run, cf)` — Kontur, Texteffekte (Schatten, Transparenz u. a.) und verborgener Text.
  - `_run_abstand_und_versalien(run, cf)`

### `dienste/docx_teile/schreiben_seite.py`

DOCX schreiben: Seite, Abschnitte, Kopf- und Fußzeilen.

- `_zeichenformat_schreiben(run, fmt)` — Schlüssel aus ``HeaderFooter.fmt`` (Schrift, Größe, fett, kursiv, unterstrichen, Farbe) als Zeichenformat des Laufs.
- **class `SeiteSchreiber`** — DOCX schreiben: Seite, Abschnitte, Kopf- und Fußzeilen.
  - `write_page()` — Dokumentweite Einstellungen (Hintergrund, Silbentrennung) und der letzte Abschnitt in der Schlusseinrichtung des Textes.
  - `write_section(s, p, typ, nr)` — Einen Abschnitt (python-docx Section) nach Einrichtung p schreiben; nr = Nummer des Abschnitts (für verknüpfte Kopfzeilen).
  - `_kopf_fuss_paare(s, p)` — Alle Kopf-/Fußzeilen des Abschnitts als (Teil, Inhalt, verknüpft, Ort[, Seitenart]); Erstseite und gerade Seiten nur bei Bedarf.
  - `_gerade_seiten_getrennt()` — „außen“/„innen“ brauchen getrennte Kopf-/Fußzeilen für gerade Seiten (w:evenAndOddHeaders gilt für das ganze Dokument);
  - `_kopf_fuss_schreiben(part, hf, ort, seite, p, nr)` — Text (mit Feldern) und freie Bilder einer Kopf- oder Fußzeile; leere Zeilen im ersten Abschnitt bleiben ungeschrieben.
  - `_kopf_fuss_text(part, hf, seite)`
  - `_lauf_mit_format(para, text, fmt)` — Text mit Seitenzahlfeldern in den Absatz schreiben; die Textstücke bekommen das Zeichenformat ``fmt``.
  - `_seitenzahl_art(s, p)` — Zahlenart, „Beginnen mit“ und Kapitelnummer der Seitenzahl als w:pgNumType.
  - `_abschnitt_ende(para)` — Am Ende des Absatzes, der einen Abschnitt beschließt: dessen Einrichtung als w:sectPr in den Absatz schreiben.
  - `_seitenschmuck(sect, p)` — Seitenrahmen, Spalten, Zeilennummern (je als Element in w:sectPr) und Hinweis zum Wasserzeichen.
  - `_alte_entfernen(sp, tag)`
  - `_nach_anker_einfuegen(sp, el, *tags)` — Element hinter das erste vorhandene der Ankerelemente setzen, sonst ans Ende.
  - `_seitenrahmen(sp, p)` — Seitenrahmen als w:pgBorders und die zugehörigen Einstellungen des Dokuments.
  - `_rahmen_einstellungen(b)` — Kopf-/Fußzeile umgeben, am Seitenrand ausrichten (Einstellungen des Dokuments).
  - `_spalten(sp, p)`
  - `_zeilennummern(sp, p)`

### `dienste/docx_teile/schreiben_tabellen.py`

DOCX schreiben: Tabellen (Zellen, Rahmen, Maße).

- `_verschachtelte_in_zelle(qt, cell)` — Verschachtelte Tabellen, die in dieser Zelle der Tabelle ``qt`` stehen: [(Position, Tabelle)], in Dokumentreihenfolge.
- `_twips(px)` — Bildpunkte → Zwanzigstelpunkte.
- `_wel(tag, **attr)` — DOCX-Element mit Attributen im Namensraum w.
- **class `TabellenSchreiber`** — DOCX schreiben: Tabellen (Zellen, Rahmen, Maße).
  - `write_table(qt, container)`
  - `_zelle_schreiben(t, cell, r, c, qt)` — Eine Zelle (bei verbundenen Zellen den ganzen Bereich) mit Format und den Absätzen ihres Inhalts.
  - `_tabelle_eigenschaften(t, qt)` — Tabellenbreite, Ausrichtung, Zellabstand, Rahmen, Innenabstand (w:tblPr, in Schema-Reihenfolge), Spaltenbreiten
  - `_tabellenbreite(f, inhalt)` — Breite der Tabelle in Zwanzigstelpunkten → (Breite, Art pct/dxa/auto, Wert für w:tblW).
  - `_tblpr_elemente(f, art, wert)` — Neue Kindelemente von w:tblPr in Schema-Reihenfolge: Breite, Ausrichtung, Zellabstand, Rahmen, Innenabstand.
  - `_tabellenrahmen(f)`
  - `_spaltenbreiten(f, n, breite)` — Spalten: Fest -> dxa, Prozent -> pct, sonst auto (Gitterbreite aus dem Rest) → (Vorgaben, Gitterbreiten).
  - `_zellbreiten(t, lang, w, n)` — w:tcW jeder Zelle: eigene Vorgabe bei einfacher Zelle, Summe der Gitterbreiten bei verbundenen.
  - `_zeilenhoehe(drow, qt, r)` — Mindest- oder exakte Zeilenhöhe als w:trHeight in Zwanzigstelpunkten.
  - `_zelle_format(dcell, cf)` — Zellenschattierung (w:shd) und senkrechte Ausrichtung (w:vAlign) der Qt-Zelle übernehmen.

### `dienste/docx_teile/schreiben_textfelder.py`

DOCX schreiben: Textfelder (``wps:wsp`` mit ``wps:txbx``/``w:txbxContent``), ihre Verknüpfungsketten und der Text darin.

- `_w(eltern, name, **at)` — Kindelement im DOCX-Namensraum anlegen, Attribute ebenfalls in diesem Namensraum.
- **class `TextfeldSchreiber`** — Fachliche Teilverantwortung des DOCX-Writers: Textfelder und verknüpfte Textfeldketten.
  - `_textfeld_ketten()` — {id des Textfelds: (Kettennummer, Stelle in der Kette)} — die Verknüpfungen aller Textfelder des Dokuments (``wps:linkedTxbx``).
  - `_textfelder_sammeln()` — Daten aller Textfelder des Dokuments nach ihrer id.
  - `_ketten_nummerieren(felder)` — Jede Kette (erstes Feld ohne Vorgänger, mit Nachfolger) bekommt eine Nummer; jedes Feld seine Stelle darin.
  - `_textfeld_xml(run, a)` — Das Bild des Textfelds wird zur Form mit Text (``wps:wsp`` mit ``wps:txbx``/``w:txbxContent``), in „Alternativer Inhalt“.
  - `_textfeld_zeichnung(drawing, d)`
  - `_textfeld_text_oder_verknuepfung(wsp, d)` — Folgefelder einer Kette verweisen nur (``wps:linkedTxbx``); alle anderen tragen den Text (``wps:txbx``).
  - `_txbx_inhalt(inhalt, d)` — Absätze und Läufe des Textfelds (Text mit Zeichenformaten) als ``w:p``/``w:r`` in ``w:txbxContent``.
  - `_txbx_absatzformat(ppr, d)` — Ausrichtung, Einzug und Zeilenabstand des Textfeld-Absatzes.
  - `_txbx_lauf(p, r, d, schluessel)` — Ein Lauf mit Zeichenformat; fehlende Werte kommen aus den Daten des Textfelds.
  - `_txbx_schrift(rpr, e, d)` — Schriftart, Fett/Kursiv/Durchgestrichen, Farbe und Größe.
  - `_txbx_hervorhebung(rpr, e)` — Hervorhebung (Hintergrund), Unterstreichung, Hoch-/Tiefstellung.

### `dienste/docx_teile/schreiben_zusatz.py`

DOCX schreiben: Kommentare, Quellenverzeichnis, Fuß- und Endnoten.

- **class `ZusatzSchreiber`** — DOCX schreiben: Kommentare, Quellenverzeichnis, Fuß- und Endnoten.
  - `_kommentare_schreiben()`
  - `_kommentar_schreiben(runs, k, gelost)` — Einen Kommentar über dem Bereich von erstem bis letztem Lauf anlegen; gelöste bekommen eine Absatzkennung (→ ``gelost``).
  - `_komm_erweitert(kennungen)` — Teil word/commentsExtended.xml: Die Kommentare mit diesen Absatzkennungen sind gelöst (w15:done).
  - `_quellen_schreiben()`
  - `_quelle_schreiben(w, q)` — Eine Quelle als b:Source (Tag, Art, Autorenliste, Titel, Jahr, Ort, Verlag, URL) an b:Sources hängen.
  - `_noten_schreiben()`
  - `_notenstile(stil_t, stil_r)` — Absatzvorlage der Notentexte und Zeichenvorlage der Notenverweise anlegen, falls sie fehlen.
  - `_noten_xml(art, wurzel, tag, ref, stil_t, stil_r)` — Wurzel des Notenteils: zwei Trenner, danach jede Note mit Verweiszeichen in der ersten Zeile.
  - `_noten_absatz(note, i, zeile, ref, stil_t, stil_r)` — Eine Zeile der Note als Absatz; die erste beginnt mit dem Verweiszeichen (Zeichenvorlage ``stil_r``).

## `dienste/integrationen`

### `dienste/integrationen/__init__.py`

Optionale Anbindungen: LanguageTool.


### `dienste/integrationen/languagetool.py`

LanguageTool als zweite Meinung (eigener Java-Prozess, nur auf diesem Rechner, 127.0.0.1).

- **class `LanguageToolFehler`**(Exception)
- `ordner()`
- `laeuft(port)`
- `jar_finden()`
- `fremd_erlauben(port)` — Erlaubt (``port``) oder verbietet (None) die Nutzung eines bereits laufenden lokalen LanguageTool-Dienstes auf diesem Port.
- `eigener_prozess_laeuft()`
- `status()` — Wer bedient die Prüfung? Für Anzeige und Datenschutzhinweis: ``art`` ist „eigen“, „fremd“ oder „keiner“.
- `verfuegbar(port)` — Gibt es einen Weg, zu prüfen: eigener Prozess startbar (Jar und Java) oder ausdrücklich erlaubter lokaler Dienst?
- `_freier_port()`
- `starten(port, warte_s)` — Stellt sicher, dass ein vertrauenswürdiger Dienst läuft. → Portnummer. Ohne ``port`` wählt das System einen freien.
- `pruefe(text, sprache, port)` — → Funde im selben Format wie die eigene Prüfung (von, bis, alt, neu, grund, art).
- `beenden()` — Beendet den selbst gestarteten Prozess (nie einen fremden Dienst).

### `dienste/integrationen/verzeichnis.py`

Verzeichnis der Anbindungen an andere Programme und Dienste — eine Stelle, die für jede sagt, was sie ist, wohin Daten gehen und was erst

- **class `Integration`**
- `_languagetool(_k)`
- `_vorlesen(_k)`
- `_argos(_k)`
- `_ki(k)`
- `_mcp(k)`
- `uebersicht(kontext)` — Für die Datenschutzanzeige: je Integration Name, Art, Zustand, Datenweg und Zustimmung.

## `dienste/rtf`

### `dienste/rtf/__init__.py`

RTF direkt lesen — ohne Umwandlungsprogramm (Microsoft RTF 1.9).


### `dienste/rtf/aufbau.py`

RTF-Dokumentaufbau: Zwischenmodell (Absätze, Tabellen, Läufe) → QTextDocument; Kopf-/Fußzeilentext.

- `absatzformat(a)`
- `tabellenformat(t, spalten)`
- **class `Bauer`**
  - `__init__(z, doc)`
  - `zeichenformat(schl)`
  - `_stil(cf, z)`
  - `_farbe(i)`
  - `absatz(a, cur, frei, liste_vorher)`
  - `_liste(a, cur, liste_vorher)`
  - `_bild(lauf, cur)`
  - `teile(teile, cur)`
  - `_tabelle(t, cur, frei)`
- `kopf_fuss_text(ziel, report)`

### `dienste/rtf/bilder.py`

RTF-Bilder: Steuerwörter einer ``\pict``-Gruppe sammeln und die Bilddaten in ein QImage umsetzen.

- `neues_bild()`
- `bild_wort(b, w, z)`
- `_bilddaten(b)`
- `bild_lauf_modell(b)` — Qt-freier Bildlauf: Originalbytes und Zielgröße; die Rasterung gehört zum Renderadapter.
- `bild_lauf(b)` — → ("b", QImage, (Breite, Höhe)) oder None, wenn das Format nicht lesbar ist. Twip → px: 15 Twip = 1 px.

### `dienste/rtf/gruppen.py`

RTF-Gruppenziele: was eine ``{\wort …}``-Gruppe bedeutet (Tabellen, Info, Kopf-/Fußzeile, Bild, Feld) und wie sie endet.

- `ziel_beginnen(z, g, w, zahl)` — Wahr, wenn das Steuerwort am Gruppenanfang die Gruppe zu einem Ziel macht (es wird dann nicht weiter angewendet).
- `_tabellen_ziel(z, g, w)`
- `_info_ziel(z, g, w)`
- `_kopf_fuss_ziel(z, g, w)`
- `_inhalts_ziel(z, g, w)` — Bild und Listentext: die Gruppe sammelt Daten bzw. Text.
- `_feld_ziel(z, g, w)`
- `_verworfenes_ziel(z, g, w)`
- `gruppe_ende(z, g)`
- `gruppentext(z, g, s)` — Text innerhalb einer Gruppe: in den Haupttext, in einen Puffer, in die Farbtabelle oder in die Feldanweisung.

### `dienste/rtf/leser.py`

RTF-Import: ``read_rtf`` — Datei prüfen, zerlegen, QTextDocument, Seiteneinstellungen und Kopf-/Fußzeilen übernehmen.

- `_daten_lesen(path)`
- `_dokument_bauen(z)`
- `_seite_fertig(z)`
- `read_rtf(path)` — → (QTextDocument, PageSettings, meta-dict, IOReport). Wirft DocumentIOError.

### `dienste/rtf/modell.py`

RTF-Zwischenmodell: Absätze, Tabellen und das Sammelziel (Haupttext, Kopf- oder Fußzeile).

- **class `NichtImModell`**(Exception) — RTF-Konstrukt, das noch nicht verlustfrei ins Kernmodell überführt wird.
- **class `Absatz`**
  - `__init__(props, laeufe, liste)`
- **class `Tabelle`**
  - `__init__()`
- **class `Ziel`** — Sammelt Absätze und Tabellen — für den Haupttext und je Kopf-/Fußzeile.
  - `__init__(haupt)`
  - `text(s, zeichen)`
  - `absatz(absatz)`
  - `zelle_ende(absatz)`
  - `reihe_ende(cellx)`
  - `abschliessen(absatz)`

### `dienste/rtf/steuerwoerter.py`

RTF-Steuerwörter im Haupttext: Zeichen, Absatz, Zeichenformat, Seite und Farbtabelle (je eine kleine Stufe).

- `steuerwort(z, g, w, zahl)` — Ein Steuerwort im aktuellen Gruppenzustand ``g`` anwenden; ``z`` ist der Zerleger (Seite, Stile, Codepage).
- `_text_wort(z, g, w, zahl, an)`
- `_seite_umbruch(ab, ziel, w)` — \par, \page und \pard: Absatz abschließen bzw. das Format leeren; ein Seitenumbruch vor dem Absatz merkt sich der Absatz.
- `_absatz_format(z, ab, w, zahl, an)` — Ausrichtung, Abstände, Tabellenzeile, Seitenumbruch, Gliederungsebene und Absatzformatvorlage. → False, wenn ``w`` keiner davon ist.
- `_absatz_wort(z, g, w, zahl, an)`
- `_zeichen_wort(z, g, w, zahl, an)`
- `_dokument_wort(z, g, w, zahl, an)`

### `dienste/rtf/zerleger.py`

RTF-Zerleger: zerlegt den Bytestrom in Tokens und führt Gruppenstapel, Textzeichen und Tabellenzeilen nach.

- `_ersatzpaar(g, wert)` — Hälften eines UTF-16-Ersatzpaars (\u-Paar für Zeichen außerhalb der BMP) zusammensetzen.
- `_unicode_zeichen(g, zahl)`
- **class `Zerleger`**
  - `__init__(daten, modell)`
  - `run()`
  - `_token(wort, zahl, hexwert, symbol, klammer, text)` — Ein Token verarbeiten; wahr, wenn die äußerste Gruppe geschlossen wurde (Ende des Dokuments).
  - `_gruppe_auf()`
  - `_gruppe_zu()`
  - `_bild_fertig(b)`
  - `_textzeichen(hexwert, text)`
  - `_symbol(sym)`
  - `_wort(w, z)`
  - `_unicode_wort(g, w, z)`
  - `_tabellen_wort(g, w, z)`

## `editor`

### `editor/__init__.py`

Dokumentlogik rund um QTextDocument: Seiten, Umbruch, Fußnoten, Formeln, Stile, Formularfelder, Ausgabe.


## `editor/diagramme`

### `editor/diagramme/__init__.py`

Zeichnen, Geometrie und Formatierung von Diagrammen.


### `editor/diagramme/diagramm.py`

Diagramme als Bild (Einfügen ▸ Diagramm), gezeichnet mit QtCharts. Keine Oberfläche.

- `_filtern(kategorien, reihen, ausgeblendet)` — Diagrammfilter: → (Stellen der sichtbaren Reihen, Stellen der sichtbaren Rubriken, Rubriken, Reihen) ohne die ausgeblendeten.
- `_palette_und_daten(u, kategorien, reihen, ausgeblendet, kombi, kachel, tf, farben)` — Belegt die Palette der Zeichnung und liefert die gefilterten Daten: → (Stellen der Reihen, Rubriken, Reihen, Kombination).
- `bild(untertyp, titel, kategorien, reihen, b, h, legende, kombi, farben, kachel, titel_an, legende_pos, labels, stil, skala, elemente, ausgeblendet, teil_format, geo)` — ``skala``: Bild in dieser Auflösung (Maße ``b``/``h`` logisch, das Bild ist ``skala``-mal so groß, Schrift bleibt scharf).
- `_namen_aus_spalte_a(kategorien, reihen, aus)`
- `_namen_keine(kategorien, reihen, aus)`
- `namen_angewendet(kategorien, reihen, ausgeblendet, quelle)` — Namensquelle (Reiter „Name“ des Diagrammfilters) auf die Daten anwenden, ohne sie zu ändern: ``zeile1`` = wie gespeichert; ``spalte_a`` = die
- `bild_aus_daten(d, b, h, skala, geo)` — Das Diagramm aus den gespeicherten Daten (``a["daten"]``) in b × h Bildpunkten.
- **class `_Zeichnung`** — Was das Zeichnen eines fertig aufgebauten Diagramms braucht.
- `_ebene_malen(z, szene)` — Das Diagramm auf eine durchsichtige Ebene malen (ohne sichtbares Fenster: in einer eigenen Szene auf Bildgröße).
- `_geometrie(z)` — Lage der Teile (für Texte, Fehlerindikatoren, Pfeile und zum Anklicken); leer, wenn nichts davon gebraucht wird.
- `_zusaetze_malen(p, z, g)` — Was QtCharts nicht selbst zeichnet: Texte mit Effekten, Fehlerindikatoren, Linien, Pfeile, Rahmen, Datentabelle.
- `_bild_malen(z, ebene, g)` — Grund, Hintergründe der Teile, die Ebene mit dem Diagramm und die Zusätze zu einem Bild zusammensetzen.
- `_chart(u, titel)`
- `_legende_einstellen(ch, legende, legende_pos)`
- `_bild(untertyp, titel, kategorien, reihen, b, h, legende, kombi, kachel, legende_pos, labels, stil, skala, opt)`
- `_legenden_namen(u, namen, kategorien)`
- `_achsenteile(u, el)` — Achsen und Hauptrasterlinie der Wertachse (nur Arten mit Achsen).
- `teile(daten)` — Die wählbaren Teile des Diagramms (Schlüssel, Anzeigename), in der Reihenfolge des Feldes „Diagrammbereich“: Diagrammbereich,
- `teil_geo(daten, b, h)` — Wie ``teil_rechtecke``, aber mit allen Angaben der Geometrie (auch ``balken_<n>`` = Liste der einzelnen Balken einer Reihe).
- `teil_rechtecke(daten, b, h)` — Schlüssel (siehe ``teile``) → QRectF in Bildpunkten des gezeichneten Bildes (b × h, logische Maße) — zum Anklicken. Die Lage kommt

### `editor/diagramme/diagramm_elemente.py`

Diagrammelemente und Teilformate auf das QtCharts-Diagramm anwenden (vor dem Zeichnen): Achsen, Achsentitel, Trendlinien, Schrift und

- `_waagr_senkr(ch)`
- `_ist_wertachse(a)`
- `_achsen_schalten(ch, el)`
- `_achsentitel(ch, u, el)`
- `_trend_erlaubt(u)`
- `_trendlinien(ch, u, el, werte, namen)`
- `_titel_legende(ch, tf, schrift_hex)`
- `_hauptgitter(ch, u, tf)` — Linie der Hauptrasterlinien der Wertachse.
- `_achsen_format(ch, tf, schrift_hex)`
- `_datenbeschriftung(ch, tf, schrift_hex)`
- `_reihenformat(fmt, ziel, serie, farbe_name)` — Linie und Füllung einer Reihe (``linie``, ``fuell`` des Teilformats).
- `_luecke(ch, tf, nummern)` — Lückenbreite gilt für alle Säulen/Balken (QtCharts: eine Breite je Serie).
- `_reihen_format(ch, u, tf, namen, nummern)`
- `anwenden(ch, u, el, werte, namen, nummern, tf)` — Achsen, Achsentitel, Trendlinien und die Schrift-/Linienformate der Teile (``teil_format``).

### `editor/diagramme/diagramm_format.py`

Formate der Diagrammteile (``daten["teil_format"][teil]``): Füllung, Linie, Effekte, Text und Optionen von Achse und Reihe. Keine Oberfläche.

- `fuell_dict(f)` — Die Füllung als Wörterbuch; None bei Automatisch (nicht gesetzt) und bei „Keine Füllung“ (``""``).
- `ist_keine(f)`
- `hauptfarbe(f)` — Die Farbe, mit der eine Reihe (Legende, Linien, Kreisstücke) gezeichnet wird, wenn der Pinsel selbst nicht möglich ist.
- `bild_kodieren(img, laengste_seite)` — Ein Füllbild für die Daten des Diagramms: höchstens ``laengste_seite`` Bildpunkte, PNG, als Text (steckt im „lunivo:“-Titel der DOCX-Datei).
- `bild_dekodieren(text)`
- `pinsel(fuell, r)` — (Pinsel, Deckkraft 0…1) der Füllung; ``r`` ist das Rechteck, das gefüllt wird (ohne: der Pinsel gilt für das jeweils gezeichnete Objekt,
- `flaeche_zeichnen(p, r, fuell)`
- `flaeche_bild(fuell, w, h, aufl)` — Die Füllung als Bild (für die Effekte, die mit einem Bild arbeiten).
- `strich_schluessel(art)` — Der Schlüssel der Auswahl ``STRICHTYPEN`` zu einer gespeicherten Strichart (ältere Dokumente: ``gepunktet`` …).
- `_strichmuster(art)` — (Strichmuster in Linienbreiten, runde Enden) der neuen Strichtypen; None für die, die ``freie_bilder._stift`` kennt.
- `linie_keine(linie)`
- `stift(linie, standard_farbe, r)` — Der Stift einer ``linie`` (Breite in pt): Strichart über ``freie_bilder._stift``, dazu Transparenz, Abschluss, Verknüpfung und Farbverlauf.
- `_verlauf_pinsel(v, r, alpha)`
- `rahmen_zeichnen(p, r, linie)` — Die Linie um ein Rechteck; ``kombiniert`` (Doppelt, Dick–dünn) zeichnet die Konturformen von ``textfx``, ``rund`` rundet die Ecken.
- `fx_normal(fmt)` — Die Effekte eines Teils im Format von ``bildeffekte`` (``True`` und ältere Angaben ergänzt).
- `teil_zeichnen(p, r, fmt, grund, nur_hinter)` — Füllung und Effekte eines Teils unter dem Diagramm. Ohne Füllung brauchen die Effekte eine Fläche: dann dient ``grund`` (Hintergrund des Stils).
- `feld_von(t, teil)` — Das Textfeld eines Teils mit Vorgaben; ``teil="titel"`` belegt die Ränder vor (``RAENDER_TITEL``), alle anderen Teile bleiben bei 0.
- `textwinkel(t)` — Der Winkel des Textes in Grad (im Uhrzeigersinn): Textrichtung und benutzerdefinierter Winkel zusammen.
- `effekt_von(t)`
- `text_eigen(t)` — Muss der Text selbst gezeichnet werden (QtCharts kann Verläufe, Kontur, Schatten … nicht)? Gilt für Titel und Legende.
- `textfarbe(t, standard)` — Farbe des Textes mit Transparenz; „Keine Füllung“ ist ganz durchsichtig.
- `schrift_aus(basis, t)`
- `box_rect(teil, r, t, gesamt_breite)` — Das Feld des Teils um den Text: ohne „Größe der Form dem Text anpassen“ ist der Titel so breit wie das Diagramm; die Ränder liegen außen herum.
- `text_feld(box, t)` — Der Platz für den Text im Feld des Teils (``box_rect`` ohne die Ränder).
- `_umbrechen(text, fm, breite)`
- `_textzeilen(text, f, fm, breite, umbrechbar)` — Die Zeilen des Textes: gestapelt ein Zeichen je Zeile, sonst an den Zeilenenden und (wenn gewünscht) an der Feldbreite umbrochen.
- `_textkontur(e)` — (Farbe, Breite in px, Form, Art) der Textkontur oder None.
- `text_zeichnen(p, feld, text, font, t, standard, umbrechbar)` — Text mit Textfüllung, -kontur und Effekten (Schatten, Spiegelung, Leuchten, 3D) in ``feld``: waagerecht mittig, senkrecht nach ``vertikal``,
- `_pfad_zeichnen(p, pfad, gl, fx, kontur, face, px, standard)` — Eine Textzeile als Pfad: verformen (Bogen, 3D), füllen, dann Effekte und Kontur.
- `achse_anwenden(achse, opt, wert)` — Die Optionen einer Achse (``achse`` im Teilformat) auf die QtCharts-Achse. ``wert``: Wertachse (Minimum, Maximum, Hauptintervall).
- `_wertachse_anwenden(achse, opt)` — Bereich, Hauptintervall, Nebenintervall und Zahlenmuster der Wertachse.
- `luecke_zu_breite(prozent)` — Lückenbreite in Prozent der Säulenbreite → ``barWidth`` der Serie (Anteil der Kategorie, den die Säulen füllen).
- `pfeil_groessen(linie)` — (Größe des Anfangspfeils, Größe des Endpfeils); fehlt die eigene, gilt die gemeinsame ``pfeil_groesse`` älterer Dokumente.
- `pfeil_zeichnen(p, spitze, von, art, breite_pt, groesse, farbe)` — Ein Linienende an ``spitze``; ``von`` ist der benachbarte Punkt der Linie (gibt die Richtung).

### `editor/diagramme/diagramm_geo.py`

Lage der Diagrammteile im gezeichneten Bild (aus der QtCharts-Geometrie nach dem Layout). Keine Oberfläche.

- `_serie(ch, name)` — Die Serie zur Datenreihe ``name`` (bei Säulen/Balken der Satz in der Serie); → (Serie, Satz oder None).
- `punkte(ch, u, kategorien, werte, namen)` — Je Reihe die Punkte (x, y, Wert) in Bildpunkten, Säulen/Balken in der Mitte ihres Balkens. Gestapelte Typen: Oberkante des Stapels.
- `_balken(ch, u, punkte_, i, m, n)` — Die einzelnen Balken einer Reihe (nur Säulen/Balken).
- `legenden_items(ch)` — Je Eintrag der Legende (Rechteck des Eintrags, Rechteck des Beschriftungstextes) aus den Grafikelementen von QtCharts, in Bildpunkten;
- `titel_rect(ch)` — Das Rechteck des Titeltextes (QtCharts-Element), sonst None.
- `_legendeneintraege(ch, namen, r)` — Die Einträge der Legende: aus den Grafikelementen von QtCharts; ohne sie eine Näherung (nebeneinander oben/unten, untereinander links/rechts).
- `_geo_titel(ch, titel, b)`
- `_geo_legende(ch, legenden_namen)`
- `_geo_achsen(ch, u, pa, h)` — Achsen und Hauptrasterlinien eines Diagramms mit rechtwinkligen Achsen.
- `_geo_reihen(ch, u, kategorien, werte, namen, nummern, pa)` — Je Reihe ein Rechteck (bei Säulen und Balken dazu die einzelnen Balken); wo sich Reihen nicht trennen lassen, der Zeichnungsbereich.
- `geometrie(ch, u, kategorien, werte, namen, nummern, b, h, titel, legende_an, achsen_an, legenden_namen)` — Alle Teile → Rechteck (siehe Kopf); ``nummern`` = Stelle jeder sichtbaren Reihe in den gespeicherten Daten.
- `gitter_streifen(ch, u, pa, halb)` — Schmale Streifen um die Hauptrasterlinien der Wertachse (senkrechte Achse, bei Balken die waagerechte) — zum Anklicken.
- `_vereinigung(rects)`
- `_umhuellung(pts, pa)`

### `editor/diagramme/diagramm_kreis.py`

Kreisgrafiken des Diagrammzeichners (QPainter): 3D-Kreis, Kreis von Kreis, Balken von Kreis. Keine Oberfläche.

- `_scheiben(werte, start)` — (Anfang, Spanne) in Grad je Wert, im Uhrzeigersinn ab ``start``.
- `_text(p, mitte, text, farbe)`
- `_flach(p, c, r, werte, farben, beschriftung, schrift, start)`
- `_drei_d(p, pa, werte, farben, beschriftung)`
- `_kleine_indizes(werte)` — Die Rubriken mit den kleinsten Beträgen, die zum Rest („Weitere“) zusammengefasst werden.
- `_rest_ansatz(c1, r1, a0, span0)` — Die beiden Randpunkte des Rest-Kreisstücks (oben, unten), von denen die Verbindungslinien ausgehen.
- `_von_kreis(p, pa, balken, werte, farben, beschriftung, schrift)`
- `_rest_balken(p, pa, oben, unten, r1, klein, kl, farben, beschriftung)` — Gestapelter Balken für die zusammengefassten kleinen Werte, mit Verbindungslinien vom Hauptkreis.
- `_rest_kreis(p, pa, oben, unten, r1, klein, kl, farben, beschriftung, schrift)` — Zweiter Kreis für die zusammengefassten kleinen Werte, mit Verbindungslinien vom Hauptkreis.
- `zeichnen(p, pa, u, kategorien, werte, farben, beschriftung, schrift)` — Malt die Kreisgrafik ``u`` (``kreis_3d`` \| ``kreis_von_kreis`` \| ``kreis_balken``) in ``pa``.

### `editor/diagramme/diagramm_reihen.py`

Datenreihen des Diagramms: je Diagrammart die QtCharts-Serien und -Achsen aufbauen (Säulen, Linien, Flächen, Punkte, Blasen, Kreis, Kurs, Netz,

- `palette_setzen(liste)` — Belegt die Reihenfarben für die folgende Zeichnung; ``None`` stellt die Standardfarben wieder her.
- `farbe(i)`
- **class `Daten`** — Die Werte einer Zeichnung, wie sie die Serien brauchen.
- `_auf_hundert(werte)` — Jede Rubrik auf die Summe 100 bringen.
- `_hoechstwert(werte, gestapelt)` — Größter Wert; bei gestapelten Reihen die größte Rubriksumme.
- `werte_vorbereiten(u, reihen)` — (Namen, Werte, gestapelt, größter Wert). Bei „100 %“ (Linie, Fläche) wird jede Rubrik auf die Summe 100 gebracht.
- `achsen(ch, u, d, serie_liste, waagrecht, kategorie)` — Rubrik- (oder Wert-) und Wertachse anlegen, an die Serien hängen und die Wertachse einteilen. → (Achse 1, Wertachse).
- `_kreis(ch, u, d)`
- `_kurs_volumen(ch, ax, werte)` — Volumen: Säulen auf eigener Achse links, nur im unteren Teil; die Kurse stehen an der Achse rechts.
- `_kurs(ch, u, d)`
- `_kerzen(d, preise, ohlc)` — Die Kerzenserie: je Rubrik Eröffnung (nur bei Open-High-Low-Close), Hoch, Tief und Schluss aus den Reihen.
- `_saeulen(ch, u, d)`
- `_flaeche(ch, u, d)`
- `_blasen(ch, u, d)` — Blasen: ab drei Reihen X = 1., Y = 2., Größe = 3. Reihe; sonst X = Rubriknummer, Y = Wert, Größe = Wertebetrag. Je Blase eine Serie
- `_blase_faerben(s, u, nr)` — Farbe der Blase; „3D-Blase“ mit Kugelverlauf.
- `_achse_mit_luft(achse, wr, kategorien, erste_ohne_dreier)`
- `_blasen_achsen(ch, kategorien, werte)` — Achsen der Blasen mit Luft für die großen Punkte.
- `_punkte(ch, u, d)`
- `_netz(ch, u, d)`
- `_linien(ch, u, d)`
- `_kombi_saeulen(ch, kombi, d, sek, zuordnung, hoch)`
- `_kombi_flaechen(ch, kombi, d, sek, zuordnung, hoch)`
- `_kombi_linien(ch, kombi, d, sek, zuordnung, hoch)`
- `_kombination(ch, u, d)` — Jede Reihe mit eigenem Typ; Reihen mit Sekundärachse an einer zweiten Werteachse rechts.
- `aufbauen(ch, u, d)` — Stellt die Serien der Diagrammart ``u`` in das Diagramm.
- `kachel_ausstatten(ch)` — Kleines Bildchen (Untertypen im Fenster): schmale Ränder, keine Achsenschrift, Raster und Beschriftungen.
- `datenbeschriftung_ein(ch)`

### `editor/diagramme/diagramm_stile.py`

Gestaltung des Diagramms: Stile (Grund, Schrift, Raster), Farbschemen und ihre Anwendung auf ein QtCharts-Diagramm. Keine Oberfläche.

- `stile_liste()` — Alle Formatvorlagen (Diagrammstile) für die Galerie: {nr, name, grund, schrift, raster, **Zusätze}.
- `_monochrom(basis)` — Sechs Töne einer Farbe, vom dunklen zum hellen.
- `farbschemen_gruppen()` — Die Gruppen „Farbig“ und „Monochrom“ mit ihren Farbzeilen (Kopie von ``FARBSCHEMEN``).
- `farbschemen_flach()` — Alle Farbzeilen hintereinander (Nummer = Argument von ``diagrammFarben``).
- `stil_schrift(stil)` — Schriftfarbe des Stils (ungültige Nummer: Standardschrift).
- `stil_grund(stil, kachel)` — Grundfarbe des Stils; Kacheln und ungültige Nummern sind weiß.
- `stil_anwenden(ch, stil, kachel, gitter)` — Schrift- und Rasterfarben des Stils. Den Grund malt ``_bild`` selbst (das Diagramm liegt auf einer durchsichtigen Ebene).

### `editor/diagramme/diagramm_teile.py`

Diagrammteile am gewählten Diagramm (freies Objekt): Auswahl, Treffer beim Mausklick und Formate je Teil. Keine Oberfläche.

- `teil_gewaehlt(ed)` — Schlüssel des gewählten Diagrammteils des gewählten Diagramms oder None (auch wenn der Teil inzwischen fehlt).
- `teil_name(ed)` — Anzeigename des gewählten Teils (Feld „Diagrammbereich“ in den Diagrammtools); leer, wenn keiner gewählt ist.
- `teil_waehlen(ed, schluessel)` — Einen Teil wählen (None: Auswahl aufheben). Das Bild wird nicht neu gezeichnet.
- `_geo(ed, d, b, h)` — Geometrie der Teile, zwischengemerkt, bis sich Daten oder Größe ändern.
- `teil_bei(ed, pos)` — Der Diagrammteil unter ``pos`` (QPointF im Editor, dieselben Koordinaten wie die Rechtecke von ``ed._frei_liste()``) für das gewählte
- `_diagramm_punkt(pos, r, dreh, b, h)` — ``pos`` im Editor als Punkt im Diagramm (Breite ``b`` × Höhe ``h``); die Drehung um die Mitte von ``r`` wird zurückgenommen.
- `_treffer(geo, erlaubt, lp)` — (Rang, Teil) aller Teile, die ``lp`` enthalten; kleinster Rang gewinnt (Balken vor Gitterstreifen vor Flächen nach Größe).
- `diagramm_teil_format_lesen(ed, teil)` — Das Format des gewählten Teils (oder von ``teil``) als Kopie; leer, wenn nichts gesetzt ist oder kein Diagramm gewählt ist. Beim Diagrammbereich
- `_ohne_leer(w)`
- `_objekt_effekt_setzen(obj_fx, k, v)`
- `_format_wert_setzen(fmt, k, v)` — Einen Wert ins Teilformat: None/False entfernt, Wörterbücher der ``_ZUSAMMEN`` werden mit den vorhandenen zusammengeführt (leer = entfernt).
- `_objekt_effekte_lesen(ed)`
- `_werte_setzen(fmt, obj_fx, kw)` — Werte ins Teilformat bzw. (Effekte des Diagrammbereichs) ins Objekt; True, wenn Objekteffekte berührt wurden.
- `_text_drehung(ed, kw)` — „Text nicht drehen“: die Drehung des Objekts merkt sich das Diagramm für das Zeichnen.
- `diagramm_teil_format_setzen(ed, teil, **kw)` — Format des gewählten Teils (``teil`` nennt einen anderen) ändern und das Diagramm neu zeichnen. ``fuell`` (Farbe, Wörterbuch, ``""`` = keine

### `editor/diagramme/diagramm_typen.py`

Diagrammarten: Katalog der Untertypen (Gruppen der linken Liste im Fenster), Kombinationen, Vorlagen, Altnamen, Beispieldaten.

- `ist_kreis(u)` — Alle Kreisarten (Kreis, 3D-Kreis, Kreis/Balken von Kreis, Ring).
- `hat_linien(u)` — Arten mit Linienreihen (Pfeile, Linienformat).
- `beispiel(untertyp)` — Beispieldaten für die Vorschau im Fenster nach Art des Untertyps (wie die Vorlage): (Titel, Rubriken, Reihen).
- `kombi_vorgabe(untertyp, anzahl)` — Belegung der Kombinationstabelle für eine fertige Kombination (die letzte Reihe ist Linie bzw. Säule).
- `_art(daten)`

### `editor/diagramme/diagramm_zusatz.py`

Diagramm: Elemente (Diagrammelemente-Liste), Teilformate und Zusätze, die QtCharts nicht selbst zeichnet. Keine Oberfläche.

- `elemente_wirksam(d)` — Alle neun Elemente mit ihrem Wert: Wahrheitswerte, bei ``legende`` die Lage (``oben`` … ``rechts``) oder ``aus``.
- `trend(werte)` — Lineare Regression y = a + b·x über x = 0 … n-1 → (a, b).
- `stift(linie, standard_farbe)` — Stift aus {farbe, breite (Bildpunkte), art}; die Strichart kommt aus ``freie_bilder._stift`` (dieselbe wie bei Bildern und Formen).
- `schrift_aus(basis, text)`
- `hintergruende(p, geo, tf, grund)` — Füllung und Effekte von Diagrammbereich, Zeichnungsbereich, Titel, Legende und Reihen — unter dem Diagramm (``diagramm_format``).
- `_reihen_effekte(p, geo, tf, grund)` — Effekte, die hinter den Balken einer Reihe liegen (Schatten u. ä.).
- `linien(p, geo, tf)` — Die Linien (Rahmen) der Teile mit ``linie`` — über dem Diagramm.
- `fehlerindikatoren(p, ch, u, pts, hoechst, farbe)` — Feste Balken ± ``FEHLER_ANTEIL`` des Höchstwerts an jedem Punkt (nicht bei Balken, Kreis, Netz und gestapelten Typen).
- `tabelle(p, r, kategorien, namen, werte, farben, schrift)` — Datentabelle: Kopfzeile mit den Rubriken, darunter je Reihe ein Farbfeld, der Name und die Werte.
- `text_fuer(tf, teil)` — Das Textformat eines Teils: die Angaben des Diagrammbereichs gelten für alle, der Teil überschreibt sie.
- `eigene_texte(p, ch, g, tf, titel, standard, legende_an)` — Titel und Legende mit Textfüllung (Verlauf, Keine), Kontur und Effekten: QtCharts zeichnet sie durchsichtig, hier kommt der Text selbst darüber.
- `_pfeil_linie(tf, nr)`
- `pfeile(p, ch, u, kategorien, werte, namen, nummern, tf)` — Pfeile und Linienenden an Linien- und Kurvenreihen (``linie.pfeil_anfang`` / ``pfeil_ende``).

## `editor/dokument`

### `editor/dokument/__init__.py`

Unterpaket ``dokument`` von ``core.editor``.


### `editor/dokument/einfuegen.py`

Einfügen: Formen, WordArt, Diagramme, Piktogramme, Formeln, Schnelltabellen, Deckblätter, Text aus Datei.

- `qimage_einfuegen(ed, img, alt, art, daten)` — Bild an der Schreibmarke einfügen. art/daten (Form, WordArt, Diagramm, …) bleiben am Bild, damit es sich wieder bearbeiten
- `_leer(w, h)`
- `form_pinsel(fuell, art, r)` — Füllung einer Form: ``art`` leer = einfarbig, ``verlauf`` (hell nach Farbe), ``abgestuft`` (drei Stufen), ``glanz`` (obere Hälfte heller).
- `_form_dreieck(p, r)`
- `_form_raute(p, r)`
- `_form_pfeil(p, r)`
- `_form_stern(p, r)`
- `_form_sprechblase(p, r)`
- `_form_zeichnen(p, art, r, adj, punkte)` — Der Pfad der Form: Freiform-Punkte, Anpassungsgriffe, eingebaute Form oder Formenkatalog.
- `_form_pfad(art, r, adj, punkte)` — (Umriss als Qt-Pfad, offen?) für Freiformen, Anpassungsformen und Katalogformen; ``None`` für die eingebauten Grundformen, die direkt gezeichnet werden.
- `_form_ueber_backend(p, art, r, adj, punkte, fuell, fuell_art, linie, strich)` — Die Form als Vektorpfad (``ShapeObject``) über das Rendering-Backend zeichnen: Füllung einfarbig oder als Verlauf, Kontur mit runden Ecken.
- `_form_text(p, art, r, text, fuell)`
- `form_bild(art, breite, hoehe, fuell, linie, strich, text, skala, adj, fuell_art, punkte)` — ``skala``: Bild in dieser Auflösung (Maße und Strich bleiben logisch, das Bild ist ``skala``-mal so groß) — für scharfe freie Formen.
- `wordart_vorlage_bild(text, nr, schrift, pt)` — WordArt nach einem der 15 Stile der Galerie: Füllverlauf, Kontur und Schatten (gezeichnet über ``core/rendering/wordart.py``).
- `wordart_bild(text, stil, schrift, pt, farbe, vorlage)`
- `diagramm_bild(art, titel, kategorien, reihen, b, h)` — ``art``: Untertyp aus ``editor.diagramme.diagramm.TYPEN`` oder einer der früheren Namen (Säulen, Balken, Linie, Kreis).
- `piktogramm_bild(name, px, farbe)`
- `formel_teile(text)` — Einfache Schreibweise → [(Text, "normal"\|"hoch"\|"tief")]:  a^2  x_{12}  sqrt(x)  frac(a,b)  \alpha
- `formel_bild(text, pt, farbe)` — Die Formel als Bild (Vorschau im Fenster „Formel“ und in der Gleichungsgalerie).
- `formel_einfuegen(ed, text)` — Fügt die Formel als Text mit hoch- und tiefgestellten Teilen an der Schreibmarke ein.
- `_tabelle(ed, zeilen, kopf, breit)` — Fügt eine Tabelle mit Rahmen und dem Text je Zelle ein (erste Zeile als Kopfzeile, wenn ``kopf``).
- `schnelltabelle(ed, name)`
- `deckblatt_einfuegen(ed, vorlage, titel, untertitel, autor, datum)` — Setzt ein Deckblatt an den Anfang des Dokuments; danach beginnt der Text auf einer neuen Seite.
- `datei_symbol_bild(name, symbol, breite)` — Dateisymbol mit Namen darunter (Einfügen ▸ Objekt ▸ Als Symbol anzeigen).
- `_fremde_bloecke(s, fremd)` — Die Blöcke des Haupttextes eines geladenen Dokuments für die Sitzung ``s``: Listen werden angelegt, Bilddaten unter neuen Namen abgelegt.
- `text_aus_datei(ed, pfad)` — Fügt den Inhalt einer Datei (DOCX, ODT, RTF, TXT …) an der Schreibmarke ein; → Bericht über Nicht-Übernommenes.
- `datum_feldanweisung(fmt)` — Qt-Datumsformat → DOCX-Feld (DATE, bei reinen Uhrzeiten TIME) für „Automatisch aktualisieren“.
- `datum_text(fmt, sprache)`
- `initiale(ed, zeilen)` — Erster Buchstabe des Absatzes groß und fett (im Absatz, in der Zeile).
- `textfeld(ed, text, breite)` — Ein Textfeld als einzellige Tabelle mit Rahmen.
- `bild_ersetzen(ed, wandle)` — wandle(QImage) → QImage; das Bild im Text wird durch das Ergebnis ersetzt (Anzeigebreite bleibt, Seitenverhältnis folgt).
- `bild_original(ed)`
- `farbe_anwenden(img, modus)`
- `zuschneiden(img, links, oben, rechts, unten)`
- `drehen(img, art)`

### `editor/dokument/fassungen.py`

Fassungen eines Dokuments mit verfolgten Änderungen, für die Anzeige „Original“: eine Kopie, in der jede Einfügung fehlt und jede

- `_stuecke(dok)` — (Art, Autor, Datum) jedes Stücks mit Änderungsmarke.
- `original(dok)` — Die Kopie des Dokuments, in der alle verfolgten Änderungen abgelehnt sind (Einfügungen fehlen, Löschungen stehen wieder da).
- `bearbeiter(dok)`
- `zeiten(dok)`

### `editor/dokument/felder.py`

Felder einfügen (Einfügen ▸ Schnellbausteine ▸ Felder …) wie in Kays Vorlage: Feldnamen, Feldfunktionen und Assistent.

- `vorgabe(name)`
- `_schalter(anweisung, zeichen)`
- `_ohne_schalter(anweisung)`
- `schreibweise(n, art)`
- `zahl_formatieren(wert, muster)` — Zahl nach einem Muster wie ``#.##0,00``, ``0 %`` (deutsche Schreibweise); ohne Muster so kurz wie möglich.
- `_seitenzahl(wort, k, art)` — NUMPAGES / SECTIONPAGES.
- `_zeitfeld(wort, roh, k)` — TIME / DATE / PRINTDATE.
- `ergebnis(anweisung, kontext)` — Feldanweisung über den Qt-freien Kern auswerten.
- `formel(text, kontext)` — Ausdruck rechnen; ValueError bei Fehlern. Bereiche (ABOVE …) kommen aus ``kontext["bereiche"]``, Textmarken aus
- `_fehler(n)`
- `_funktion(n, w)`
- `_zahl(text)`
- `tabellen_bereiche(ed)` — Zahlen über, unter, links und rechts der Zelle an der Schreibmarke (leer außerhalb von Tabellen).
- `kontext_sammeln(ed, autor, pfad)`
- `feld_einfuegen(ed, anweisung, text, versteckt)` — ``versteckt``: ausgeblendeter Text (TC-Einträge stehen wie in Textprogrammen unsichtbar im Text).

### `editor/dokument/felder_ergebnis_kern.py`

Qt-freie Auswertung von Feldanweisungen.

- `feld_ergebnis(anweisung, kontext, *, _FELD_ERGEBNIS, _ohne_schalter, _schalter, formel, zahl_formatieren)` — Das Feldergebnis jetzt. ``kontext`` aus ``kontext_sammeln`` (alle Angaben freiwillig).

### `editor/dokument/felder_text_kern.py`

- `_ohne_schalter(anweisung)`

### `editor/dokument/formular.py`

Formularfelder (Inhaltssteuerelemente): Textfeld, Auswahlliste, Datum, Kontrollkästchen, Schaltfläche.

- **class `_Eingabe`** — Wer fragt den Benutzer nach Datum oder Text eines Formularfeldes? Die Oberfläche setzt ``eingabe_anbieter`` beim Start auf ihr
  - `getDatum(eltern, titel, frage, datum)`
  - `getText(eltern, titel, frage, text, kennwort)`
  - `zeigeAuswahl(eltern, optionen, global_pos, gewaehlt)` — Liste der Möglichkeiten an ``global_pos``; ein Eintrag ruft ``gewaehlt(eintrag)``.
- `meta(art, name, **kw)`
- `meta_text(m)`
- `meta_lesen(s)`
- `_format(m, leer)`
- `_anzeige(m, wert)` — (Text des Feldes, zeigt nur den Platzhalter) für ein neues Feld mit dem Wert ``wert``.
- `einfuegen(ed, m, wert)` — Feld an der Schreibmarke (oder anstelle der Markierung) einfügen.
- `_zeichenformat(m, leer)` — Das Zeichenformat eines Feldes im Dokumentmodell (``formular``: die Daten als Text).
- `bereiche(dok)` — [(von, bis, Feld-Daten)] aller Felder (Stellen im Rohtext); zusammenhängende Stücke mit gleichen Daten sind ein Feld.
- `feld_an(dok, pos)`
- `_auswahl(ed, v, e)`
- `_ersetzen(ed, v, e, m, text, leer)`
- `wert_von(ed, v, e)`
- `_klick_kasten(ed, v, e, m, fenster)`
- `_klick_auswahl(ed, v, e, m, fenster)`
- `_klick_datum(ed, v, e, m, fenster)`
- `_klick_text(ed, v, e, m, fenster)`
- `_klick_knopf(ed, v, e, m, fenster)`
- `klick(ed, pos, fenster)` — Klick in ein Feld: Kontrollkästchen wechselt, Auswahl zeigt die Liste, Text und Datum fragen nach dem Wert, die Schaltfläche löst
- `_ist_leer(ed, pos)`
- `_knopf_aktion(ed, m, fenster)`
- `alle_zuruecksetzen(ed)` — Alle Felder auf ihren Anfangswert (Platzhalter, leeres Kästchen) zurücksetzen.
- `daten(dok)` — [(Name, Wert)] aller Felder mit Wert (ohne Platzhalter und Schaltflächen).
- `nur_formulardaten(dok)` — „Nur Formulardaten drucken“ in der KOPIE ``dok``: Text außerhalb der Felder wird unsichtbar, Bilder entfallen. → Zahl der Felder.

### `editor/dokument/gehe_zu.py`

„Gehe zu“: Sprungziele im Dokument — Seite, Zeile (Absatz), Überschrift, Textmarke, Kommentar, Fußnote, Endnote, Tabelle, Bild,

- `_kurz(t, n)`
- `_stellen(dok)` — Absatz-Id → Stelle des Absatzanfangs im Rohtext.
- `_seitenzahl(ed)`
- `maximum(ed, art)` — Obergrenze für Seite und Zeile.
- `seitenstart(ed, n)` — Stelle des ersten Textes auf der Seite ``n`` (ab 1); hat die Seite keinen Text, der Anfang der nächsten mit Text.
- `zeilenstart(ed, n)`
- `_ziele_ueberschrift(ed)`
- `_ziele_textmarke(ed)`
- `_ziele_beschriftung(ed)`
- `_ziele_kommentar(ed)`
- `_ziele_note(art)`
- `_tabellen(bloecke, stellen)` — (Tabelle, Stelle des Tabellenanfangs) aller Tabellen in Dokumentreihenfolge (auch geschachtelte).
- `_ziele_tabelle(ed)`
- `_objekte(ed, nur_art)` — [(Stelle, Art)] aller Objekte (im Text und frei positioniert) in Dokumentreihenfolge.
- `_ziele_bild(ed)`
- `_ziele_abschnitt(ed)`
- `ziele(ed, art)` — [(Beschriftung, Position)] für die Listen-Arten.
- `springen(ed, pos)`
- `positionen(ed, element)` — Die Anfänge aller Elemente einer Art, der Reihe nach.
- `_ziel_index_leer(alle, element, i, hier, richtung)` — Index für „Weiter“/„Zurück“ ohne Eingabe.
- `ziel(ed, element, eingabe, richtung)` — Wohin „Weiter“ (``richtung`` 1) oder „Zurück“ (-1) springt. ``eingabe``: leer = nächstes/voriges Element, „4“ = das vierte,

### `editor/dokument/indexeintrag.py`

Indexeinträge wie das DOCX-Feld XE: Haupt- und Untereintrag, Lesung, „Siehe …“, Seitenbereich über eine Textmarke, fette oder

- **class `Eintrag`**
  - `text()`
  - `schalter()`
  - `sortierung()`
- `aus_text(text, schalter)` — Eintrag aus ``P_INDEX`` und ``P_INDEX_OPT``.
- `feld(e)`
- `aus_feld(anweisung)` — Eintrag aus einer Feldanweisung ``XE "…" …``; None, wenn es kein XE-Feld ist.

### `editor/dokument/je_stand.py`

Zwischenspeicher je Dokumentstand: Ergebnisse, die nur vom Inhalt des Dokuments abhängen, einmal je Änderung berechnen.

- `je_stand(doc, name, bauen)` — ``bauen(doc)``, gemerkt am Dokument unter ``name``, bis sich das Dokument ändert (Qt vergibt dann eine neue Revision).
- `im_blick(p, b)` — Liegt der Absatz ``b`` im Ausschnitt, den der Maler ``p`` gerade zeichnet? Ohne Ausschnitt (ganzes Dokument): immer.

### `editor/dokument/literatur.py`

Quellen und Zitierweisen (APA, Harvard, IEEE, Chicago, DIN ISO 690).

- `_nachname(autor)`
- `_autoren(autor)`
- `zitat(q, weise, nr)`
- `eintrag(q, weise, nr)`
- `literaturverzeichnis(quellen, weise)`

### `editor/dokument/sendungen.py`

Sendungen: Umschlag, Etiketten, Seriendruck (mit Feldern, Adressblock, Regeln), Formularfelder. Auf dem Dokumentmodell, ohne Qt-Dokument.

- `_einzeilig(text)`
- `umschlag_aufbauen(ed, format_name, absender, empfaenger)` — Ersetzt den Inhalt des Editors durch einen Umschlag (Absender klein oben links, Empfänger rechts darunter); → die Seiteneinrichtung.
- `etiketten_aufbauen(ed, bogen, text, gleich)` — Ersetzt den Inhalt des Editors durch einen Etikettenbogen (Tabelle ohne Rahmen, je Etikett eine Zelle); → die Seiteneinrichtung.
- `tabelle_lesen(roh)`
- `felder_im_text(dok)`
- `feld_einfuegen(ed, name)` — Fügt ``{{name}}`` mit Feldfarbe ein; dahinter geht es ohne Feldfarbe weiter.
- `adressblock_einfuegen(ed, was)`
- `regel_einfuegen(ed, feld, wert, dann, sonst)`
- `_satz_einsetzen(s, satz, von_bis)` — Felder und Regeln mit den Werten von ``satz`` füllen (``von_bis``: nur in diesem Bereich, Stellen im Rohtext).
- `brief_fuer(vorlage, satz)` — Ein Brief (Kopie der Vorlage). Steht „Nächster Datensatz“ im Text, gilt hinter jeder solchen Stelle der nächste Satz der Liste ``satz``.
- `saetze_je_brief(vorlage)` — Wie viele Datensätze ein Brief verbraucht (1 + Zahl der Felder „Nächster Datensatz“).
- `gruppen(vorlage, saetze)`
- `serienbrief_erzeugen(quelle, saetze)` — Alle Briefe in EIN Dokument, durch Seitenumbrüche getrennt. → (Dokument, Zahl der Briefe).
- `quelle_lesen(pfad)` — Empfängerliste aus einer Textdatei (CSV mit ; oder , oder Tabulator; erste Zeile = Spaltennamen). → (Spalten, Sätze) oder None.
- `zugeordnet(satz, zuordnung)` — Satz mit den Namen der Felder im Text: ``zuordnung`` {Feld im Text: Spalte der Quelle}; ohne Eintrag gilt der gleiche Name.
- `felder_hervorheben(ed, an)` — Hintergrund der Felder {{…}} an oder aus (ein Schritt).
- `naechster_einfuegen(ed)` — Feld „Nächster Datensatz“: dahinter füllt der nächste Satz die Felder (z. B. mehrere Etiketten auf einem Blatt).
- `form_textfeld(ed, text)`
- `form_kasten(ed, beschriftung)`
- `form_knopf(ed, aufschrift)`
- `kasten_umschalten(ed, pos)` — Klick auf ein Kontrollkästchen ☐/☒ wechselt den Zustand.

### `editor/dokument/vergleich.py`

Dokumente vergleichen und zusammenführen — das Ergebnis sind verfolgte Änderungen (einfügen/löschen, mit Autor und Datum). Ohne Qt.

- `ops_bestimmen(basis, andere, autor)` — Änderungen von ``basis`` nach ``andere`` als Operationen auf den Absätzen von ``basis`` (Nummer des Absatzes in Dokumentreihenfolge).
- `_bereich(op)`
- `zusammenlegen(listen)` — Operationen mehrerer Autoren vereinen; überschneidende Löschungen verschiedener Autoren → die erste gilt, die andere ist Konflikt.
- `_jetzt()`
- `_freie_strecken(a, von, bis)` — Die Strecken von ``von`` bis ``bis`` im Absatz ohne Änderungsmarke (bereits verfolgte Zeichen bleiben, wie sie sind).
- `anwenden(s, ops, datum)` — Operationen als verfolgte Änderungen in die Sitzung schreiben (von hinten nach vorn, damit die Stellen stimmen).
- `vergleichen(basis, andere, autor)`
- `zusammenfuehren(basis, fassungen)`

### `editor/dokument/vergleich_datum_kern.py`

- `_jetzt()`

### `editor/dokument/verweise.py`

Beschriftungen, Textmarken, Querverweise, Stichwörter und Zitate — Funktionen am Editor (``KernEditor``).

- `seq_format(anweisung)` — Zahlschreibweise aus einer Feldanweisung ``SEQ Abbildung \* ROMAN`` (Vorgabe arabisch).
- `_seq_lauf(a)` — (Versatz, Lauf) des SEQ-Feldes eines Absatzes, sonst ``None``.
- `beschriftungen_liste(ed)` — [{label, text, pos, block}] — die Beschriftungsabsätze in Dokumentreihenfolge (``pos``: Stelle im Rohtext, ``block``: Id des Absatzes).
- `naechste_nummer(ed, label, zahl)` — Nummer, die eine neue Beschriftung ``label`` an der Schreibmarke bekäme (für die Anzeige im Fenster).
- `beschriftung_einfuegen(ed, label, text, oben, *, nach, ohne_bezeichnung, zahl)` — Beschriftung „Abbildung 1: Text“ unter (``oben``: über) dem Objekt oder Absatz. ``nach`` ersetzt „: Text“ durch genau diesen
- `beschriftungen_nummerieren(ed)`
- `lesezeichen_liste(ed, versteckte)` — [{name, von, bis}] — Textmarken mit ihren Stellen im Rohtext. ``versteckte=False`` lässt die Marken weg, die mit „_“ beginnen
- `lesezeichen_name_gueltig(name)`
- `lesezeichen_setzen(ed, name)` — Setzt die Textmarke auf die Auswahl (ohne Auswahl: auf das Wort an der Schreibmarke); eine gleichnamige wird versetzt.
- `lesezeichen_loeschen(ed, name)`
- `lesezeichen_gehe(ed, name)`
- `intern_springen(ed, href)`
- `verweisen_auf(art)`
- `_ziele_absaetze(ed)` — Überschriften und nummerierte Absätze.
- `_bezeichnung_nummer(a)` — „Abbildung 2“ — der Text der Beschriftung bis einschließlich der Nummer.
- `_beschriftungstext(a)` — Der Text hinter der Nummer, ohne Doppelpunkt.
- `_ziele_beschriftungen(ed)`
- `_ziele_textmarken(ed)`
- `_ziele_noten(ed)` — Fußnoten (1, 2, …) und Endnoten (i, ii, …) in Textreihenfolge.
- `querverweis_ziele(ed)` — Mögliche Ziele: nummerierte Absätze, Überschriften, Textmarken, Fuß- und Endnoten, Beschriftungen.
- `marke_sichern(ed, ziel)` — Name der Textmarke am Ziel. Fehlt eine, bekommt der Bereich des Ziels eine verborgene Textmarke „_Ref…“.
- `querverweis_text(ed, ziel, wie, oben_unten)`
- `querverweis_einfuegen(ed, ziel, wie, *, link, oben_unten)` — Querverweis an der Schreibmarke (siehe ``querverweis_text``); ``link`` macht ihn zum internen Hyperlink (Strg+Klick).
- `index_eintragen(ed, e, alle)` — Indexeintrag ``e`` (``editor.dokument.indexeintrag.Eintrag``) an die Markierung setzen (ohne Markierung: das Wort an der
- `index_markieren(ed, term)`
- `zitat_einfuegen(ed, q)`
- `quelle_tag(quellen, q)`

### `editor/dokument/verweise_fach_kern.py`

Qt-freie Fachlogik für Querverweise und Quellenkürzel.

- `querverweis_text_bilden(ziel, wie, cursor_position, seitenzahl, oben_unten)`
- `quelle_tag_bilden(quellen, q)` — Eindeutiger Kurzname (Nachname + Jahr).

### `editor/dokument/verzeichnis.py`

Verzeichnisse: Inhalt, Abbildungen, Tabellen, Stichwörter, Literatur.

- `toc_opt_text(opt)`
- `toc_opt_lesen(text)`
- `_koepfe(dok)` — Die Kopfabsätze aller Verzeichnisse in Dokumentreihenfolge.
- `toc_optionen(doc)` — Einstellungen des ersten Inhaltsverzeichnisses im Dokument (None, wenn es keines gibt).
- `vorhanden(doc, art)`
- `_stellen(dok)` — Absatz-Id → Stelle des Absatzanfangs im Rohtext.
- `_ueberschriften(dok, ebenen)` — (Ebene, Text, Absatz-Id, Stelle) der Überschriften außerhalb von Verzeichnissen.
- `_beschriftungen(dok, label)`
- `_toc_marken(editor, ueberschriften)` — Absatz-Id → Name der verborgenen Textmarke „_Toc…“ an der Überschrift; fehlende werden gesetzt (in einem Schritt mit dem Verzeichnis).
- `_stichwoerter(editor)` — [(Eintrag, Stelle)] aus den markierten Textstellen (eine Stelle je zusammenhängender Markierung).
- `_index_zeilen(editor)` — Zeilen des Stichwortverzeichnisses: Haupteinträge, darunter eingerückt die Untereinträge; „Siehe …“ statt Seitenzahl,
- `zeilen_fuer(editor, art, opt)` — → [(Ebene, Text, Seitenangabe)]; beim Inhaltsverzeichnis mit Verknüpfungen (``opt["links"]``) als viertes die Textmarke.
- `_seite_text(seite)` — Die Seitenangabe als Text: ein Text oder Stücke (Text, fett, kursiv), wie sie das Stichwortverzeichnis liefert.
- `_schreiben(editor, s, art, zeilen, opt)` — Schreibt das Verzeichnis (ersetzt ein vorhandenes der Art) im Rahmen eines laufenden Schrittes.
- `verzeichnis_einfuegen(editor, art, opt)` — Verzeichnis an der Schreibmarke einfügen. Gibt es schon eines der Art, wird es mit ``opt`` neu geschrieben.
- `verzeichnis_aktualisieren(editor, nur)` — Alle Verzeichnisse (oder nur die der Art ``nur``) neu schreiben; gibt die Zahl der Zeilen zurück.

### `editor/dokument/verzeichnis_kern.py`

Qt-freie Indexverarbeitung.

- `index_zeilen_bilden(eintraege, seiten, marken)`

### `editor/dokument/vorlagen.py`

Die mitgelieferten Gerüste (Brief, Bewerbung, Lebenslauf …) und eigene Vorlagen.

- `muster()`
- `_benutzer_zeilen(b, mit_name)`
- `_ersetze(text, b)`
- `aufbauen(ed, zeilen, benutzer, heute)` — Schreibt das Gerüst in den (leeren) Editor und hebt die Lücken hervor.
- `naechste_luecke(doc, von)`
- `luecken_entfernen(doc)` — Für den Druck: Lücken « … » verschwinden samt Klammern.
- `vorlagenordner(settings)`
- `rubriken(ordner)` — Der Vorlagenordner nach Rubriken: jeder Unterordner ist eine Rubrik (Name → Dateien); lose Dateien liegen im Ordner selbst.
- `eigene_vorlagen(ordner)`

### `editor/dokument/zusatz.py`

Zusatzdaten am Text: Kommentare, Fuß-/Endnoten, nachverfolgte Änderungen.

- `roemisch(n)`
- `neue_id(vorhanden)`
- `leere_meta()`
- `abstand_davor_px(bf)` — Der Abstand vor dem Absatz, wie ihn der Benutzer eingestellt hat — auch wenn Lunivo ihn am Seitenanfang gerade unterdrückt.
- `kommentar_farbe(geloest)`

## `editor/layout`

### `editor/layout/__init__.py`

Die Layout-Schicht von Lunivo Writer (Seitenplan, später Layout-Baum, Seitenaufteilung, Display-Liste). Siehe dokumentation/architektur/layout-schicht.md.


### `editor/layout/seitenlauf.py`

Der Seitenlauf: die eigene Dokument-Layout-Klasse von Lunivo (``QAbstractTextDocumentLayout``).

- `unterstuetzt(doc)` — Kennt der Seitenlauf alles, was im Dokument steht? Absätze, Listen, Tabellen (auch verschachtelt), Bilder in der Zeile und schwebende Rahmen
- **class `Seitenlauf`**(QAbstractTextDocumentLayout) — Setzt ein ``QTextDocument`` nach dem Seitenplan. Der Plan wird bei jeder Änderung des Dokuments neu aus den Abschnittsumbrüchen gebildet;
  - `__init__(doc, basis, zoom, rand_oben, fluss, lazy)`
  - `_bild_handler_uebernehmen()` — Bilder in der Zeile: Qt erkennt ein Zeilenobjekt nur, wenn die Layout-Klasse einen Handler für seine Art kennt. Aus Python lässt sich keiner
  - `zoom_setzen(zoom, neu_setzen)` — Die Anzeigegröße: alle Maße und die Schrift des Laufs werden mit ``zoom`` gesetzt (Schrift über das Zeichengerät, wie bei Qt).
  - `endlos_setzen(breite_px, neu_setzen)` — Weblayout an (Breite) oder aus (None): ein endloses Blatt dieser Breite statt der Blätter der Seiteneinrichtung.
  - `_plan()`
  - `voll_setzen()` — Alles neu setzen (nach einer Änderung von Seite, Zoom oder Weblayout), nicht nur ab dem geänderten Absatz.
  - `anordnen()` — Das Dokument setzen; mit Fußnoten am Seitenfuß so oft, bis Text und Platz unten zueinander passen.
  - `_setzen()` — Das Dokument setzen. Bei reinem Text (keine Tabellen und Rahmen) nur ab dem ersten geänderten Absatz — und nur bis zu dem, an dem
  - `_bereich_von(block)` — Index des Bereichs, in dem der Block steht (über die Abschnittsumbrüche, je Dokumentstand einmal gelesen).
  - `_neues_blatt(erg, bereich)`
  - `_absatz(block, platz, erg)` — Einen Absatz setzen: Zeile für Zeile an den Platz (Seitenfluss oder Zelle), mit Rändern, Einzug, Ausrichtung und Zeilenabstand.
  - `_regeln_an(platz)` — Die Umbruchregeln gelten im Seitenfluss mit gleich breiten Spalten (nicht in Zellen, nicht im Fluss der Druckkopie, nicht im Weblayout).
  - `_raender(block, platz)` — (Rand links, Rand rechts, Einzug der ersten Zeile) eines Absatzes in Bildpunkten mit Zoom.
  - `_option_setzen(block)`
  - `_erste_zeilen(block, platz, anzahl)` — Höhen der ersten ``anzahl`` Zeilen eines Absatzes bei der Breite des Platzes (zum Vorausschauen) und seine Zeilenzahl.
  - `_umbruch_stelle(block, bf, platz, hs)` — Vor welcher Zeile (0 = vor dem ganzen Absatz) beginnt die nächste Spalte oder Seite, damit die Umbruchregeln gelten? None: kein Umbruch nötig. Die Regeln selbst stehen
  - `_absatz_mit_regeln(block, bf, tl, platz, erg, sig, rand_links, rand_rechts)` — Wie ``_absatz``, aber erst alle Zeilen bilden, dann nach den Umbruchregeln auf die Spalten und Blätter verteilen.
  - `_wiederverwenden(block, platz, erg, sig)` — Kann der Absatz seine Zeilen behalten? Ja, wenn sich weder er noch seine Breite geändert haben, er Zeilen hat, kein schwebender Rahmen
  - `_absatz_abschluss(block, tl, bf, platz, erg, gesetzt, x_min, y_min, x_max, y_max, erster_platz)`
  - `_zeilenhoehe(h, bf)` — Zeilenhöhe nach Zeilenabstand des Absatzes (Rechnung in ``core/textlayout/paragraph.zeilenhoehe``).
  - `_rahmen(rahmen, platz, erg)` — Ein Rahmen im Text. Schwebend (links oder rechts): am Rand der Spalte an der aktuellen Höhe, der folgende Text läuft darum herum.
  - `_rahmen_inhalt(rahmen, platz, erg)`
  - `_tabelle(tabelle, platz, erg)` — Eine Tabelle setzen: Spaltenbreiten aus den Vorgaben, Zeilenhöhen aus dem Inhalt der Zellen, Zeilen untereinander (im Seitenfluss auf
  - `_kopfzeilen_wiederholen(start, kopf_n, y_alt, y_neu, dx, gesetzt, erg)` — Die Kopfzeilen einer Tabelle noch einmal oben auf dem neuen Blatt: Zellen (Füllung, Rahmen) und die Absätze darin, nur verschoben.
  - `_tabellenbreite(tf, verfuegbar, z)`
  - `_spaltenbreiten(tabelle, tf, breite_tab, luecke, z)`
  - `_zellinhalt(zelle, x, y, breite, erg, messen)` — Den Inhalt einer Zelle (Absätze und verschachtelte Tabellen) von (x, y) an setzen. → Höhe des Inhalts.
  - `documentChanged(position, chars_removed, chars_added)`
  - `_sicher()` — Bei einer ``lazy`` gesetzten Kopie: jetzt setzen, wenn seit dem letzten Setzen etwas geändert wurde.
  - `draw(painter, ctx)` — Den Text zeichnen: alle Absätze, die im Zeichenbereich liegen, mit Auswahl und Schreibmarke.
  - `_listenzeichen(painter, block)` — Aufzählungszeichen oder Nummer links vor der ersten Zeile eines Listenabsatzes (wie ``QTextDocumentLayout``).
  - `_tabellen_zeichnen(painter, klipp)` — Füllung und Rahmen der Tabellenzellen (hinter dem Text), über das Rendering-Backend. Rahmen je Zelle und Seite, sonst der Rahmen der Tabelle.
  - `hitTest(punkt, genauigkeit)` — Die Textposition am Punkt (Blattraum): die nächste Zeile, dann das Zeichen in ihr.
  - `_kern_treffer(punkt, genauigkeit)` — Qt-Punkt → Kernabsatz und Zeichenstelle; gibt ``None`` zurück, wenn der Qt-Fallback gebraucht wird.
  - `pageCount()`
  - `documentSize()`
  - `frameBoundingRect(rahmen)`
  - `blockBoundingRect(block)`
  - `_kern_rechteck(block)` — Das Rechteck des ersten Zeilenstücks des Absatzes aus dem Qt-freien Seitenumbruch (``core/layout``); ``None``, wenn der Absatz dort nicht steht.
  - `_kern_aktualisieren()` — Das Kernlayout und alle Qt-zu-Modellpfade für den aktuellen Dokumentstand aufbauen.
  - `_kern_pfad(block)` — Modellpfad eines eindeutig zuordenbaren Absatzes; verschachtelte Blöcke bleiben beim Qt-Rechteck.
  - `_kern_pfade_bilden(modell)` — Qt-Blocknummer → Modellpfad für Absätze in Dokument, Tabelle und Rahmen; Rahmenpositionen werden nebenbei erfasst.
  - `_kern_rahmen_bilden()` — Tabellen- und Rahmenrechtecke nach ihrer QTextFrame-Position aus den Kern-Plätzen zusammensetzen.
  - `drawInlineObject(painter, rechteck, objekt, position, format)`
  - `_bild(f)`
  - `ort(y)` — (Blatt 1-basiert, y ab dem oberen Textrand des Blattes) zu einem y des Laufs — für Lesezeichen, Notizen, Verweise und Blasen.
  - `seitenwechsel()` — Zeichenstelle, an der jedes weitere Blatt beginnt (der erste Absatz, der dort anfängt) — für „Gehe zu Seite“.
  - `seitennummern(start)` — Die angezeigte Seitennummer je Blatt: ab ``start`` + 1 (Einrichtung des Dokuments), „Beginnen mit“ eines Abschnitts setzt neu an.
  - `zeilennummern(art)` — (Blattindex, y, Zeilenhöhe, Nummer) für jede nummerierte Zeile in Blattkoordinaten; ``art`` „seite“: auf jedem Blatt neu ab 1.
  - `frei_index()` — Die frei positionierten Bilder je Blatt (1-basiert) wie ``freie_bilder.koerper_index``, aber nach den Blättern des Laufs:
  - `blatt_von_block(blocknummer)` — Das Blatt, auf dem der Block beginnt (0-basiert).
  - `blaetter()`
  - `blatt_bei_y(y)` — Das Blatt, auf dem oder nach dem Punkt y (Blattraum) liegt; im Zwischenraum das davor.

### `editor/layout/seitenplan.py`

Seitenplan: die eine Quelle dafür, wie ein Dokument in Bereiche (Abschnitte), Seiten und Spalten gegliedert ist.

- **class `Spalte`** — Eine Textspalte: ``x`` vom linken Textrand und ``breite`` in Bildpunkten.
- **class `Bereich`** — Ein Stück des Dokuments mit einheitlicher Seiteneinrichtung (ein oder mehrere aufeinanderfolgende Abschnitte gleicher Geometrie).
  - `blatt_px()`
  - `text_links_px()`
  - `text_oben_px()`
- `spalten(ps)`
- `gleiche_geometrie(a, b)` — Haben zwei Einrichtungen dieselbe Seitengeometrie (Blatt, Ränder, Spaltenraster)? Dann bilden sie bei „fortlaufend“ einen Bereich.
- **class `Seitenplan`** — Die Bereiche eines Dokuments, in Reihenfolge.
  - `__init__(bereiche, hinweise)`
  - `aus_dokument(qdoc, basis)` — Der Plan für ``qdoc`` mit der Dokumenteinrichtung ``basis``. Ein „fortlaufender“ Umbruch zu gleicher Geometrie geht im vorigen
  - `bereich_von_abschnitt(abschnitt)`
  - `bereich_von_block(qdoc, blocknummer)` — Der Bereich, in dem der Block mit dieser Nummer steht.

### `editor/layout/seitenplatz.py`

Platz im Seitenfluss ohne Qt: Blätter, gesetzte Zellen, Stand und Ergebnis des Laufs sowie die Platzvergabe für Absätze, Tabellenzeilen und Zellen.

- **class `Blatt`** — Ein Blatt des Laufs (Maße mit Zoom).
  - `breite()`
  - `hoehe()`
  - `text_links()`
  - `text_oben()`
  - `text_hoehe()`
  - `fluss_hoehe()` — Höhe einer logischen Seite im Textfluss der Druckkopie (im Raster des Seitenumbruchs, wie ``PageSettings.content_height_px``).
  - `rechteck()`
- **class `Zelle`** — Eine gesetzte Tabellenzelle für das Zeichnen: Rechteck im Blattraum, ihr Format und das der Tabelle.
- **class `_Stand`**
- **class `_Ergebnis`**
- **class `_KoerperPlatz`** — Der Platz für Absätze und Tabellenzeilen im Seitenfluss: Spalten des Bereichs, Blätter, Seitenwechsel.
  - `__init__(lauf, bereich, stand, erg)`
  - `_spalte()`
  - `breite()`
  - `links()`
  - `_unten_y()` — y des oberen Randes der Spalte im Koordinatensystem des Laufs.
  - `_hoehe()`
  - `abstand(a, vor)`
  - `umbruch_vor()`
  - `_weiter()`
  - `vergeben(h)` — Platz für eine Zeile der Höhe ``h``; passt sie nicht mehr, beginnt die nächste Spalte oder Seite. → (linker Rand der Spalte, y, Breite).
  - `_ausschluss(y, h, w)` — Wie weit schwebende Rahmen die Zeile (y bis y + h) von links und rechts einengen; ``unter`` = Unterkante, falls zu wenig bleibt.
  - `zeile_vergeben(h)` — Platz für eine Tabellenzeile der Höhe ``h`` (eine zu hohe Zeile steht trotzdem). → y der Oberkante.
  - `stelle()`
  - `blatt_index()`
- **class `_FreiPlatz`** — Der Platz in einer Zelle: feste Breite, die Höhe wächst mit dem Inhalt.
  - `__init__(x, y, breite)`
  - `breite()`
  - `links()`
  - `abstand(a, vor)`
  - `umbruch_vor()`
  - `vergeben(h)`
  - `zeile_vergeben(h)`
  - `stelle()`
  - `blatt_index()`

## `editor/objekte`

### `editor/objekte/__init__.py`

Unterpaket ``objekte`` von ``core.editor``.


### `editor/objekte/bilddaten.py`

Originaldaten von Bildern: Bytes und Format der Datei, aus der ein Bild stammt.

- **class `BildQuelle`** — Originalbytes eines Bildes. ``ersatz_png``: Pixelersatz für Vektorformate (SVG, EMF, WMF).
  - `endung()`
  - `medientyp()`
- `entpacken(blob)` — gzip-gepackte Bilddaten (SVGZ, EMZ, WMZ) entpacken, höchstens ``MAX_ENTPACKT_BYTES``.
- `merken(img, blob, ersatz_png, nur_raster)` — Die Originalbytes zu diesem Bild ablegen. None, wenn das Bild leer oder das Format unbekannt ist.
- `quelle_zu(img)` — Das Original zu diesem Bild, solange seine Bildpunkte unverändert sind; sonst None (dann PNG schreiben).
- `uebernehmen(von, nach)` — Ein Bild mit gleichen Bildpunkten, aber eigenem Schlüssel (zum Beispiel nach einer verlustfreien Kopie) behält das Original.
- `png_bytes(img)`
- `fuer_schreiben(img, erlaubt)` — → (Bytes, Dateiendung, Medientyp) für das Speichern: das Original, wenn die Bildpunkte unverändert sind und der Schreiber das Format
- `mit_ausrichtung_lesen(blob)` — Bilddaten lesen und eine EXIF-Drehung/-Spiegelung (Fotos von Kameras und Telefonen) anwenden — so zeigt Word das Bild und so bleibt das
- `svg_bereinigen(svg)` — Verweise auf andere Dateien oder Adressen entfernen (nur ``data:`` und ``#``-Verweise im Bild bleiben).
- `_renderer(q)`
- `_svg_groesse(r)`
- `svg_raster(svg, seite)` — Rasterfassung eines SVG (transparent, längste Seite ``seite``); leeres QImage, wenn QtSvg es nicht lesen kann.
- `bild_aus_svg(svg, ersatz_png)` — Ein SVG als Bild mit Vektorquelle. ``ersatz_png``: vorhandene Ersatzgrafik (aus DOCX/ODT) als Rasterfassung; sonst wird gerastert.
- `ist_svg(img)`
- `anzeigegroesse(img)` — Startgröße auf dem Blatt in px: bei SVG das Maß aus ``width``/``height`` bzw. ``viewBox``, sonst die Bildgröße.
- `zeichnen(p, r, img)` — Das Bild in ``r`` zeichnen; ein unverändertes SVG als Vektor (scharf in jeder Zoomstufe, auch im PDF), sonst die Bildpunkte.
- `platzhalter(breite, hoehe)` — Ersatz für ein Bild, dessen Daten fehlen oder nicht lesbar sind: graue Fläche mit Rahmen und Kreuz in der Größe des Bildes (gezeichnet über das Rendering-Backend).
- `bild_aus_datei(pfad, still)` — Eine Bilddatei als QImage laden und ihr Original ablegen. Leeres QImage, wenn sie sich nicht lesen lässt;
- `_aus_datei(pfad)`

### `editor/objekte/bildeffekte.py`

Effekte für Bilder und Formen, die Lunivo selbst zeichnet: Schatten, Reflektion (Spiegelung), Leuchten, Weiche Kanten, 3D-Format (Tiefe)

- `gespiegelt(img, waagrecht, senkrecht)` — Das Bild gespiegelt (links ↔ rechts und/oder oben ↔ unten). Die eine Stelle dafür: ``QImage.flipped`` gibt es ab Qt 6.9,
- `_merken(schluessel, bauen)`
- `_maske(bild, groesse, ellipse)` — Die Form des Bildes (Alpha) in der gewünschten Größe: das Bild selbst, in einer Ellipse beschnitten, wenn ``ellipse``.
- `_getoent(maske, farbe)`
- `_weich(img, radius)` — Weichzeichnen durch Verkleinern und Vergrößern (billig und gleichmäßig); der Rand muss vorher frei sein.
- `weiche_kanten(bild, r, ellipse, radius_pt)` — Das Bild mit weich auslaufendem Rand (Alpha nimmt zum Rand hin ab), in der Größe ``r``.
- `_schatten_bild(bild, w, h, ellipse, farbe, weich_px, faktor)` — (Bild des Schattens mit Rand ringsum, Randbreite): die getönte Form, um ``faktor`` skaliert und weichgezeichnet.
- `unter_zeichnen(p, bild, r, ellipse, fx)` — Leuchten, Schatten und Reflektion hinter dem Bild (in der Reihenfolge der Schichten: Leuchten zuerst).
- `_stufenfarbe(basis, material, licht, t)` — Farbe der Tiefe in Stufe ``t`` (0 = vorn, 1 = hinten) nach Material und Beleuchtung (dieselben Namen wie bei den Texteffekten).
- `tiefe_richtung(dreh)` — Einheitsvektor, in dem die Tiefe nach hinten läuft: schräg nach rechts unten, bei gedrehtem Objekt (3D-Drehung X/Y) entsprechend verschoben.
- `extrusion_zeichnen(p, bild, r, ellipse, d3, dreh)` — 3D-Format: die Form des Bildes (Alpha) als Tiefe nach hinten gestapelt (``tiefe`` pt, Farbe, Material, Beleuchtung), dazu eine Kontur
- `_dreht(dreh)`
- `hat_drehung(fx)` — True, wenn ``fx["drehung"]`` das Bild dreht (``drehung_3d``).
- `hat_nachbearbeitung(fx)` — True, wenn das Bild vor dem Zeichnen mit ``bild_nachbearbeiten`` verändert werden muss (gedreht oder mit oberem Abschluss).
- `hat_abschluss(fx)`
- `bild_nachbearbeiten(bild, r, ellipse, fx)` — Das Bild für das Zeichnen vorbereiten: oberer Abschluss des 3D-Formats eingearbeitet, dann im Raum gedreht (3D-Drehung). Die Form ist danach
- `_projektion(w, h, dreh)` — (Zielviereck, Faktor) der gedrehten Bildfläche: Drehung um X, Y, Z und Perspektive (Sichtwinkel ``persp``, 0 = parallel), eingepasst in ``w`` × ``h``.
- `drehung_3d(bild, r, ellipse, dreh)` — Das Bild (Größe ``r``) im Raum gedreht (``x``, ``y``, ``z`` Grad, ``persp``); dieselbe Größe, die Fläche passt vollständig hinein.
- `_erodiert(m, rad)` — Die Form um ``rad`` px nach innen verkleinert (Schnitt der in acht Richtungen verschobenen Form).
- `_band(aussen, innen)`
- `_licht(band, art, st, umgekehrt)` — Das Band mit Licht von links oben: hell oben links, dunkel unten rechts (``st`` = Stärke 0…1).
- `abschluss_oben(bild, r, ellipse, ab)` — Oberer Abschluss: ein Rand der Breite ``breite`` pt rundum, von links oben beleuchtet; ``hoehe`` pt bestimmt die Stärke von Licht und Schatten.
- `abschluss_symbol(art, groesse)` — Bildchen für die Auswahl der Abschlussart: eine graue Fläche mit dem Abschluss.

### `editor/objekte/bildlayout.py`

Das Fenster „Layout“ (oberflaeche/baukasten/dokument/layout_dialog.py) mit einem Bild verbinden: Werte vom Bild lesen, die Wahl auf das Bild anwenden.

- `ziel(ed)` — („frei“, Schlüssel, Angabe, Bild) oder („text“, Objekt) für das markierte Bild; sonst None.
- `_achse_lesen(a, waagerecht)`
- `verschieben_wahl(a)` — Vorwahl der Radios „Mit Text verschieben“ / „Fester Text“ im Popup Layoutoptionen eines freien Objekts: ``"mit_text"``, ``"fest"`` oder
- `lesen(ed, z)`
- `_box(page, bezug, waagerecht)`
- `_achse_schreiben(a, w, page, waagerecht)`
- `_mass(w, page, waagerecht, alt)`
- `anwenden(ed, z, werte)` — Schreibt die Wahl des Fensters (oder eines Teils davon: nur die genannten Schlüssel) auf das Bild.
- `_speichern_frei(ed, key, neu)`
- `format_lesen(ed, z)` — Füllung, Kontur und Effekte des markierten freien Bildes im Format des Panels (``ObjektFormatPanel``); sonst None.
- `fx_alle(ed, fx)` — Seitenlayout ▸ Effekte: dieselben Effekte an alle frei liegenden Bilder und Formen des Dokuments (``{}`` nimmt sie weg). → Anzahl.
- `format_aus_panel(ed, z, werte)` — Wendet die Werte des Panels an: Füllung, Kontur und alle Effekte (fehlende Effekte sind ausgeschaltet).
- `format_setzen(ed, z, fuell, rand, rand_teil, fx)` — Füllung (``fuell``: Wörterbuch oder None) und/oder Kontur (``rand``: Wörterbuch oder None; ``rand_teil`` ändert nur einzelne Angaben der
- `fuellbild_setzen(ed, z, bild)` — „Füllung ▸ Bild“: das Bild als Füllung; es liegt als Ressource des Dokuments.
- `frei_aendern(ed, z, **teile)` — Einzelne Angaben des markierten freien Bildes ersetzen (Schlüssel der Angabe: ``dreh``, ``hinter`` …).
- `ausrichten(ed, z, wie)` — Das freie Bild am Blatt ausrichten (links/mitte/rechts, oben/mittig/unten).
- `drehen(ed, z, grad)`
- `ebene(ed, z, vorn)` — „Eine Ebene nach vorne/hinten“: das Bild liegt vor oder hinter dem Text (frei positioniert).
- `masse_lesen(ed, z)` — Breite und Höhe des markierten Bildes in mm.
- `masse_setzen(ed, z, breite_mm, hoehe_mm)`
- `format_merken(z)` — Füllung, Kontur und Effekte des markierten freien Bildes zum „Format übertragen“.
- `format_uebertragen(ed, z, merk)`
- `_hoehe_je_breite(img, a)` — Höhe je Breite des sichtbaren Ausschnitts von ``img`` (mit Zuschnitt ``zu`` der Angabe).
- `frei_bild_ersetzen(ed, z, wandle)` — ``wandle(QImage) → QImage``: das Bild des markierten freien Bildes wird durch das Ergebnis ersetzt (Anzeigebreite bleibt, die Höhe
- `frei_original(ed, z)` — Farbänderung und Zuschnitt zurücknehmen (das ursprüngliche Bild, gleiche Anzeigebreite).
- `frei_original_groesse(ed, z)` — Das Bild in seiner Pixelgröße.
- `frei_entfernen(ed)` — Das gewählte Bild löschen (wie die Entf-Taste).

### `editor/objekte/bildwerkzeuge.py`

Weitere Bildtools für frei positionierte Bilder (Datei, Bildschirmfoto, Piktogramm): Seitenverhältnis sperren, transparente Farbe,

- `frei_bild(ed)` — Das gewählte freie Bild (Datei, Bildschirmfoto, Piktogramm) als Ziel für ``bildlayout``, sonst None.
- `sperre(z)`
- `sperre_umschalten(ed, z, an)` — Seitenverhältnis sperren: Ziehen an den Kanten hält es dann auch, die Größen-Eingabe ebenfalls.
- `farbe_transparent(img, farbe, toleranz)` — Alle Bildpunkte, die ``farbe`` (innerhalb der Toleranz je Farbkanal) gleichen, werden durchsichtig.
- `transparent(ed, z, farbe, toleranz)`
- `aendern(ed, z, bild, alt)` — Bild ändern: ``bild`` ersetzt den Inhalt; Größe, Lage, Rahmen, Füllung und Effekte bleiben, Zuschnitt und Farbänderung entfallen.
- `aus_datei(ed, z, pfad)`
- `komprimieren(ed, z, beschnitt_loeschen)` — Bild komprimieren: weggeschnittene Bereiche löschen (wenn ``beschnitt_loeschen``) und auf ``KOMPRIMIEREN_FAKTOR`` × Anzeigegröße
- `werte(a)` — (Helligkeit, Kontrast) in Prozent aus der Angabe des Bildes.
- `korrigiert(bild, hell, kontrast)` — Das Bild mit Helligkeit und Kontrast (Prozent): Kontrast streckt die Werte um die Mitte, Helligkeit verschiebt sie; Alpha bleibt.
- `korrektur_setzen(ed, z, hell, kontrast)` — Helligkeit und/oder Kontrast (begrenzt auf -100 bis 100) des freien Bildes setzen; 0 entfernt die Angabe.
- `korrektur_schritt(ed, z, hell, kontrast)` — Helligkeit/Kontrast um die Schritte ``hell``/``kontrast`` (Prozent) ändern.
- `zuruecksetzen(ed, z)` — Bild zurücksetzen: ursprüngliches Bild (vor Farbänderungen), kein Zuschnitt, keine Maske, Rahmen, Füllung, Effekte und Drehung weg;

### `editor/objekte/bildzuschnitt.py`

Zuschneiden frei positionierter Bilder — nicht zerstörend (die Bilddaten bleiben unverändert).

- `formen_kategorien()` — Die Formen zum Zuschneiden: (Kategorie, [Formnamen]) aus dem Formenkatalog, ohne Linien — für die Galerie.
- `lesen(a)` — (links, oben, rechts, unten) als Anteile; ohne Zuschnitt (0, 0, 0, 0).
- `hat(a)`
- `anzeige(bild, a)` — Der sichtbare Ausschnitt von ``bild`` (mit Formmaske); ohne Zuschnitt und Maske das Bild selbst. Zwischengespeichert.
- `_quelle(ed, a)`
- `_skalen(a)` — Anzeigepunkte je Anteil des ganzen Bildes (waagerecht, senkrecht).
- `setzen(ed, z, zu, maske, b, h)` — Zuschnitt ``zu`` = (links, oben, rechts, unten) als Anteile (None: Zuschnitt entfernen) und/oder Formmaske (``""``: entfernen); was nicht
- `skala(ed, z, breite, hoehe)` — Nach Skala (Seitenverhältnis) zuschneiden: der größte mittige Ausschnitt mit diesem Verhältnis; die Breite des Rahmens bleibt.
- `skala_text(ed, z, text)` — ``"16:9"`` (oder ``(16, 9)``) → ``skala``. „Frei“ (kein festes Verhältnis) ändert nichts und gilt als gelungen.
- `form(ed, z, name)` — Nach Form zuschneiden: der Ausschnitt wird in die Form (Name aus dem Formenkatalog) eingepasst; Zuschnitt bleibt.
- `zuruecksetzen(ed, z)` — Form und Größe zurücksetzen: Maske und Zuschnitt weg, das ganze Bild in der bisherigen Breite im ursprünglichen Seitenverhältnis.
- `aus_ziehen(a0, neu, griff)` — Zuschneiden durch Ziehen an einem Griff: ``a0`` die Angabe vor dem Ziehen, ``neu`` die mit der gezogenen Größe (``b``, ``h``).

### `editor/objekte/formen.py`

Formen nachträglich ändern (Füllung, Kontur, Vorlage, Größe) und Formen zu einer Gruppe zusammenfassen.

- `form_daten(o, breite, hoehe)`
- `_zeichnen(d)`
- `_gruppe_zeichnen(kinder)`
- `frei_daten(ed)` — Die Parameter der gewählten Form als freies Objekt (Kopie) oder None.
- `aendern(ed, **felder)` — Parameter der markierten Form ändern (fuell, linie, strich, text, form, breite, hoehe) und neu zeichnen. Eine als freies Objekt
- `vorlage(ed, name)`
- `gruppieren(ed)` — → '' bei Erfolg, sonst die Begründung.
- `gruppe_aufheben(ed)`

### `editor/objekte/formen_anpassen.py`

Anpassungsgriffe der Formen (die gelbe Raute): welche Form welche Parameter hat, wie der Pfad daraus entsteht und wo der Griff liegt.

- `_poly_pfad(punkte, r)`
- `_pt(r, x, y)`
- `_anteil(r, p)`
- `_rund(standard)`
- `_stern(zacken, innen)`
- `_pfeil(richtung, schaft, kopf)` — [Schaft (Dicke als Anteil der Quermaße), Kopf (Länge des Kopfes als Anteil der Längsmaße)].
- `_doppelpfeil(waagrecht, schaft, kopf)` — [Schaft, Kopf (je Seite, Anteil der Längsmaße 0 … 0.5)].
- `_fuenfeckpfeil(kopf)`
- `_kreuz(arm)` — [Armdicke] als Anteil von Breite und Höhe.
- `_trapez(neigung)` — [Neigung] = Versatz der kurzen Seite als Anteil der Breite (0 … 0.5).
- `_parallelogramm(neigung)`
- `_dreieck(spitze)` — [Lage der Spitze] als Anteil der Breite (0 … 1).
- `_ring(dicke)` — [Dicke] des Rings als Anteil der kürzeren Seite (0.05 … 0.5).
- `anpassbar(name)`
- `standard(name)`
- `_voll(name, adj)` — Die Parameter mit Standardwerten für fehlende Stellen, auf die Grenzen begrenzt.
- `pfad(name, r, adj)`
- `griffe(name, r, adj)` — Die Lage der Anpassungsgriffe (je Parameter einer) im selben Koordinatensystem wie ``r``.
- `setzen(name, wert, adj, index)` — Neue Parameterliste: Parameter ``index`` = ``wert`` (auf die Grenzen begrenzt), die anderen bleiben.
- `wert_aus_punkt(name, r, punkt, index)` — Der Parameter ``index``, wenn der Griff an ``punkt`` gezogen wird (auf die Grenzen begrenzt).

### `editor/objekte/formen_katalog.py`

Die Formen der Galerie Einfügen ▸ Formen, nach Gruppen wie in der Vorlage: Linie, Rechteck, Standardformen, Blockpfeile, Formelformen,

- `_poly(*punkte)` — Vieleck aus Anteilen (0…1) der Breite und Höhe.
- `_vieleck(n, drehung)`
- `_stern(zacken, innen)`
- `_linie(*punkte, pfeil_ende, pfeil_anfang)`
- `_kurve(pfeil_ende, pfeil_anfang)` — S-förmige Kurvenverbindung von links oben nach rechts unten (waagerechte Enden), auf Wunsch mit Pfeilspitzen.
- `_bogen(start, spanne)`
- `_abgerundet(radius)`
- `_ellipse(r)`
- `_ring(r)`
- `_zylinder(r)`
- `_herz(r)`
- `_mond(r)`
- `_smiley(r)`
- `_wolke(r)`
- `_dokument(r)`
- `_welle(r)`
- `_fahne(r)` — Fahne: Mast links, wehendes Tuch rechts.
- `_legende(form)`
- `_tropfen(r)` — Kreis mit einer Ecke oben rechts (Tropfen).
- `_rechteck(r)`
- `namen()`
- `hat(name)`
- `ist_linie(name)`
- `anpassbar(name)` — Hat die Form Anpassungsgriffe (siehe ``formen_anpassen``)?
- `pfad(name, r, adj)` — Der Pfad der Form in ``r``; ``adj`` = Parameter der Anpassungsgriffe (fehlt er oder hat die Form keine, gilt die Standardform).

### `editor/objekte/formen_stile.py`

Formstil-Raster (Zeichentools ▸ Formstile „Abc“): sechs Zeilen (Umriss, Voll, Verlauf hell, Abgestuft, Glanz, 3D) zu sieben Farben

- `formstil(zeile, spalte)` — Die Werte des Stils: {"fuell": Farbe oder "" (keine), "fuell_art": "" \| verlauf \| abgestuft \| glanz, "linie": Farbe, "strich": pt,
- `formstile_raster()` — Das Raster für die Galerie: [Zeile][Spalte] = {"zeile", "spalte", "name" (z. B. „Voll – Blau“), **Werte von ``formstil``}.

### `editor/objekte/frei_objekt.py`

Freie Objekte mit Parametern (WordArt, Textfeld): EIN gemeinsamer Baustein.

- `_form_zeichnen(d, b, h)` — Eine Form (``editor/objekte/formen.py``/``einfuegen.py``) in b × h Bildpunkten, in doppelter Auflösung.
- `_diagramm_zeichnen(d, b, h)` — Ein Diagramm (``editor/diagramme/diagramm.py``) aus den gespeicherten Daten, in b × h Bildpunkten, in doppelter Auflösung.
- `_smartart_zeichnen(d, _b, _h)`
- `_piktogramm_zeichnen(d, _b, _h)`
- `_zeichenbereich_zeichnen(d, b, h)` — Zeichenbereich (``editor/objekte/formen.py``): gestrichelter Rand und die ``kinder`` (Formen mit Lage x/y), in doppelter Auflösung.
- `zeichnen(art, d, b, h)`
- `_anzeige_mass(art, img, b, h)` — Größe auf dem Blatt in Bildpunkten: WordArt aus dem Bild (ohne Überbreite), SmartArt wie das Bild (sofern keine Größe vorgegeben),
- `einfuegen(ed, art, daten, b, h)` — Fügt das Objekt als freies Objekt am Absatz der Schreibmarke ein und wählt es aus. → Id des Objekts.
- `bild_einfuegen(ed, img, bb, hh, art, daten, alt)` — Der gemeinsame Weg aller freien Bilder und Objekte: ``img`` als Darstellung, Größe auf die Inhaltsbreite begrenzt, danach ausgewählt.
- `ziel(ed)` — (Art, Daten, Id, Angabe, Bild) des gewählten Objekts (WordArt, Textfeld, Form, Diagramm, SmartArt) oder None.
- `art_gewaehlt(ed)`
- `daten_lesen(ed, art)`
- `aendern(ed, art, **kw)` — Parameter des gewählten Objekts ändern (siehe ``_aendern_innen``).
- `_daten_vorbereiten(d, kw)` — Vor dem Ändern: Vorlage und neuer Text setzen Altes zurück, ein Zeichenformat fürs ganze Objekt löscht gleiche Angaben der Läufe.
- `_form_daten_setzen(d, k, v)` — Bei einer Form: Farben der Form selbst, kein Kasten ums Bild.
- `_kasten_setzen(neu, a, k, v)` — Füllung, Strichstärke, Effekt und Linie des Kastens ums Objekt.
- `_eintrag_setzen(art, k, v, d, neu, a)` — Ein Schlüssel von ``kw`` (außer Größe) in ``daten`` oder in den Kasten schreiben.
- `_aendern_innen(ed, art, **kw)` — Parameter des gewählten Objekts ändern und neu zeichnen. ``breite``/``hoehe`` (px) ändern die Größe; ``form_fuell`` (Farbe oder ``""``)
- `daten_still(ed, art, **kw)` — Daten des gewählten Objekts ändern, ohne das Bild neu zu zeichnen (z. B. die Auswahl eines Diagrammteils); None entfernt den Schlüssel.
- `nach_groesse(ed, neu)` — Nach dem Ziehen der Griffe: Textfeld, Form und Diagramm werden in der neuen Größe frisch gezeichnet; SmartArt skaliert nur.
- `text_bereich(a, bild)` — Wo der Text im Objekt liegt, als Anteil (0..1) von Breite/Höhe — für die graue Textmarkierung wie in der Vorlage (nur WordArt).
- `_fmt_unter(cf, k, v)`
- `_fmt_hoch_tief(cf, k, v)`
- `_fmt_schrift(cf, k, v)`
- `_fmt_pt(cf, k, v)`
- `_format_aus_kw(kw)` — Zeichenformat für das Eingabefeld aus Schlüsseln der Texttools (nur die genannten).
- `_lauf_schnitt(cf, setze)` — Fett, kursiv, unterstrichen, durchgestrichen, hoch- und tiefgestellt.
- `_lauf_farben(cf, setze)` — Hervorhebung, Textfarbe (mit Deckkraft) und Kontur; leer = ausdrücklich keine.
- `_lauf_schrift(cf, setze)`
- `_lauf_aus_format(cf, basis)` — Die Zeichenschlüssel, die ein Format ausdrücklich setzt und die vom Objekt abweichen.
- `_basis(d, art)`
- `_widget_laeufe(w, d, art)` — Die Läufe aus dem Eingabefeld; ``None``, wenn der ganze Text ohne eigene Formate ist.
- `_edit_laden(ed)` — Das Eingabefeld mit den Läufen des Objekts füllen (Auswahl bleibt erhalten).
- `_edit_stil(ed)` — Schrift, Farbe und Ausrichtung des Eingabefeldes folgen den Parametern des Objekts (auch nach einem Knopf der Texttools).
- `edit_platzieren(ed)` — Das Eingabefeld deckt das Objekt (folgt dem Blatt beim Scrollen und Zoomen).
- `bearbeiten_starten(ed)` — Schreibt direkt im gewählten Objekt (WordArt oder Textfeld): ein Eingabefeld über dem Text. Eingabe, Markieren, Rückschritt und Enter
- `auswahl_daten(ed)` — Die Zeichenformate der Markierung (oder der Schreibmarke) im Eingabefeld — wirksame Werte, auch die des Objekts. Für den Zustand der
- `edit_uebernehmen(ed)` — Der eingegebene Text mit seinen Formaten kommt ins Objekt (ohne das Feld zu schließen).
- `bearbeiten_beenden(ed)`
- `text_werte_lesen(ed)` — Die Textoptionen (Format von ``texteffekt.py``) des gewählten Objekts.
- `text_werte_anwenden(ed, werte)` — Die Textoptionen der Seitenleiste wirken auf den Text im gewählten Objekt: Füllung (Farbe, Transparenz), Kontur (Farbe, Breite).
- `_textfelder(ed)` — Alle freien Textfelder des Dokuments: (Schlüssel, Angabe) — frisch aus dem Modell gelesen.
- `_speichern_angabe(ed, key, a)`
- `_neu_setzen(ed, key, a)` — Das Bild des Textfelds aus seinen Daten neu zeichnen und die Angabe sichern.
- `_kette_ohne(felder, da, verboten)` — Von ``da`` die Kette nach oben bis zum Kopf gehen. → False, wenn ein Vorgänger fehlt oder das Feld ``verboten`` darin steht (Kreis).
- `_verknuepfbar(felder, von_key, nach_key)` — (Daten von ``von``, Daten von ``nach``) als Kopien mit Kennung, wenn die Verknüpfung erlaubt ist; sonst None.
- `_text_uebernehmen(da, db)` — Den Text (und die Läufe) von ``db`` an ``da`` hängen; ``db`` wird leer.
- `verknuepfen(ed, von_key, nach_key)` — Textfeld ``von`` mit Textfeld ``nach`` verknüpfen: was in ``von`` nicht mehr passt, läuft in ``nach`` weiter (wie „Verknüpfung erstellen“).
- `loesen(ed, key)` — Die Verknüpfung des Textfelds zu seinem Nachfolger lösen (steht ``key`` am Ende einer Kette, die zu seinem Vorgänger): der Nachfolger
- `ist_verknuepft(ed, key)`
- `_kette_glieder(k, a, nach_id)` — Alle Felder einer Kette ab ``(k, a)`` in Reihenfolge.
- `_kette_verteilen(ed, kette, voll, hat_laeufe, gesehen)` — Den vollen Text auf die Felder der Kette verteilen; nur Felder mit geändertem Anteil neu setzen.
- `kette_aktualisieren(ed)` — Jede Kette neu verteilen: der Text des ersten Feldes (mit seinen Zeichenformaten) füllt ein Feld nach dem anderen; geändert werden nur

### `editor/objekte/frei_objekt_text.py`

Textdarstellung für frei positionierte Objekte.

- `listenmarken(liste, anzahl)` — Die Marke jeder Zeile (mit Leerzeichen dahinter): Aufzählungszeichen oder Nummer nach dem Listenwert aus ``editor/text/listen.py``
- `richtung_anwenden(img, richtung, zeilenbaender)` — Die Textrichtung am fertigen (waagerecht gesetzten) Bild: senkrecht_rl und dreh90 laufen von oben nach unten (Zeilen von rechts nach links),
- `_gedreht(richtung)`
- `effekte_auf_text(img, ef, text_hoehe, farbe)` — Leuchten und Spiegelung am fertig gezeichneten Text (durchsichtiges Bild in doppelter Auflösung).
- `anzeige_laeufe(d)` — Die Läufe, die das Objekt zeigt: ``[{"t": Text, <Zeichenschlüssel>…}]`` (Schlüssel, die fehlen, gelten für das ganze Objekt).
- `laeufe_text(laeufe)`
- `laeufe_ab(laeufe, von, bis)` — Der Ausschnitt ``[von, bis)`` des Gesamttextes mit seinen Formaten.
- `laeufe_zusammen(laeufe)` — Benachbarte Läufe mit gleichem Format zu einem verbinden (leere fallen weg).
- `_zeilen_laeufe(laeufe)` — Läufe in Zeilen (Absätze) teilen.
- `_wa_stil(d, pt)` — Füllung, Kontur, Konturbreite und Schatten aus Vorlage und Objektangaben.
- `_wa_format(d, r)` — Das Format eines Laufs: seine eigenen Angaben vor denen des Objekts.
- `_wa_schrift(e, pt)`
- `_wa_segmente(d, laeufe, pt)` — Je Zeile [(Text, Format, Schrift, Metrik)]; dazu die Listenmarken und das Grundformat.
- `_wa_masse(d, segmente, basis, pt)` — Zeilenhöhen, Grundlinien, Breiten und Bildgröße des WordArt-Bildes.
- `_wa_effekte(d)`
- `_wa_verteilt(sg, marke, ausr, letzte)`
- `_wa_text_pfad(t, e, f, fm, xx, y, luecke)` — Pfad eines Laufs (bei `luecke` wortweise verteilt) und die Endposition.
- `_wa_zeile(i, sg, ctx, aus)` — Fügt die Pfade einer Zeile zu (gesamt, gruppen, hervor, linien) hinzu.
- `_wa_dekoration(pf, e, f, fm, lage, f1, aus)` — Unterstreichung, Durchstreichung und Hervorhebung eines Laufs.
- `_wa_glut_schatten(p, gesamt, ef, stil, pt)`
- `_wa_fuellen(p, gruppen, stil, h, pt)`
- `_wa_spiegeln(img, b, h)` — Spiegelbild unter das Bild setzen, nach unten verblassend.
- `wordart_zeichnen(d)`
- `_zeichenformat(d, lauf, vorlage, farbe_ueber)` — Das Zeichenformat eines Laufs: seine eigenen Angaben, sonst die des Objekts.
- `_zeichen_unterstrich(cf, e)`
- `_zeichen_schrift(cf, e)` — Schriftart, Größe, Hoch-/Tiefstellung und Hervorhebung.
- `_zeichen_farbe(cf, lauf, farbe_ueber)`
- `_innen(d)` — Innenabstand links, oben, rechts, unten — aus ``d["innen"]`` (zum Beispiel aus bodyPr lIns/tIns/rIns/bIns einer DOCX), sonst ``TEXTRAND``.
- `_textdoc(d, laeufe, b, h, farbe_ueber)` — Das Textdokument eines Textfelds (Klartext mit Zeichenformaten) für die Läufe; → (Dokument, innere Breite, innere Höhe).
- `_text_passt(d, laeufe, b, h)` — Wie viele Zeichen der Läufe im Feld ``b`` x ``h`` stehen (Anfang der ersten Zeile, die nicht mehr passt) — für verknüpfte Textfelder.
- `_text_malen(img, d, doc, bi, hi, b, h)` — Den gesetzten Text ins Bild malen; mit dem Effekt „Schatten“ darunter derselbe Text in der Schattenfarbe, leicht versetzt.
- `_zeilenbaender(doc, hoehe)` — (oben, Höhe) jeder Textzeile in Bildpunkten des Bildes; dazu der Rand darüber und darunter als eigene Bänder, damit nichts verloren geht.
- `textfeld_zeichnen(d, b, h)` — Nur der Text (durchsichtig); Füllung und Rand legt die Angabe des Bildes darum (so wirken Füllung und Kontur der Schnellleiste).

### `editor/objekte/freie_bilder.py`

Frei positionierte Bilder: Bilder, die nicht im Text stehen, sondern an einer Stelle des Blattes (DOCX ``wp:anchor`` ohne Umbruch).

- `emu_zu_px(emu)`
- `aus_absatz(bf)`
- `an_absatz(cursor, angabe)` — Hängt die Angabe an den Absatz des Cursors (mehrere Bilder an einem Absatz sind möglich).
- `hat_bilder(doc)` — Gibt es im Text überhaupt einen Absatz mit frei positionierten Bildern? (billig genug für jeden Zeichenvorgang des Editors)
- `bild_im_dokument(doc, name)`
- `neuer_name(doc)`
- `_zu_gross(blob)` — Liest nur die Maße aus dem Bildkopf; Bilder über ``MAX_BILDPUNKTE`` werden abgelehnt, bevor Qt sie anlegt.
- `bild_aus_daten(blob)` — Ein Bild aus Dateidaten. Qt kennt kein EMF; viele DOCX-Bilder (eingescannte Unterschriften) sind aber EMF-Hüllen um ein Bitmap
- `farbe_aus_element(el, ns)` — Eine DrawingML-Farbe (srgbClr, prstClr, schemeClr) mit lumMod, lumOff, satMod, tint und shade. ``ns``: Namensräume für XPath.
- `duoton(img, dunkel, hell)` — Das Bild in zwei Farben: Schwarz wird ``dunkel``, Weiß wird ``hell``, dazwischen Verlauf (DrawingML ``a:duotone``). Durchsicht bleibt.
- `rechteck(a, blatt_b, blatt_h, ml, mt, inhalt_b, inhalt_h, absatz_y, spalte_x, seite)` — Das Rechteck des Bildes auf dem Blatt. ``absatz_y``: oberer Rand des Absatzes (Blattkoordinate), ``spalte_x``: linker Rand der Spalte.
- `fuell_pinsel(fuell, r, fuellbild)` — Der Pinsel für die Füllung eines Bildes (hinter durchsichtigen Stellen): ``farbe``, ``verlauf``, ``graduell`` (zwei Farben), ``muster``,
- `_stift(rand)` — Die Kontur eines Bildes als Stift (Stärke in Bildpunkten, Art wie bei den Linien).
- `_text_gerade(dreh, fx)` — „Text nicht drehen“: Form und Füllung gedreht, der Text bleibt aufrecht.
- `_png_daten(bild)` — Die Bildpunkte als PNG für das Backend (kleine Ablage nach ``cacheKey``, damit nicht bei jedem Zeichnen neu kodiert wird).
- `_ueber_backend(p, bild, r, ellipse, rand, dreh, fuell, fuellbild, fx)` — Bild mit Füllung, Kontur, Drehung und Effekten über ``core.rendering`` zeichnen. Vektorbilder (SVG, EMF/WMF) gehen mit ihren Originalbytes an das Backend.
- `bild_zeichnen(p, bild, r, ellipse, rand, dreh, fuell, fuellbild, fx)` — Bild in ``r``; ``ellipse``: in einer Ellipse beschnitten; ``rand``: {"b": px, "farbe": "#rrggbb", "art": Linienart} eine Linie um die Form;
- `koerper_index(d, ch, ncol)` — {Blatt (1-basiert): [(Angabe, y des Absatzes in der Spalte, Spalte)]} für die Bilder im Text. ``d`` ist der Textfluss
- `objekte_der_seite(page, d, n, index)` — Alle frei positionierten Bilder des Blattes ``n`` (1-basiert) mit ihrem Rechteck, in Blattkoordinaten (px).
- `versatz_fuer(a, r, page, n)` — Die Angaben ``xh``/``yv`` (ohne Ausrichtung), mit denen das Bild im Rechteck ``r`` steht — zum Verschieben und Verändern der Größe.
- `ohne_hilfsangaben(a)`
- `vorne_hinten(objekte, hinter)`

### `editor/objekte/freiform.py`

Freiform: die Punkte einer Form (Zeichentools ▸ Form bearbeiten ▸ Punkte bearbeiten). Keine Oberfläche.

- `innen(daten, b, h)` — Das Zeichenrechteck der Form im Bild von b × h Bildpunkten (wie in ``einfuegen.form_bild``).
- `aus_pfad(pfad, r)` — Die Elemente des Pfads, auf das Rechteck ``r`` bezogen (Anteil 0..1). Ein Teilpfad, der zum Anfang zurückkehrt, wird mit ``Z`` geschlossen.
- `aus_form(daten, b, h)` — Die Punktliste der gewählten Form in ihrer Größe (Pfeilspitzen der Linien werden zu eigenen Teilpfaden).
- `pfad(punkte, r)` — Der Pfad der Punktliste im Rechteck ``r``.
- `geschlossen(punkte)` — Gibt es einen geschlossenen Teilpfad (dann wird gefüllt, sonst nur die Linie gezeichnet)?
- `rollen(punkte)` — Je Element: ``"knoten"`` (Punkt), ``"steuer"`` (Kurven-Steuerpunkt) oder ``"zu"`` (Schließen).
- `knoten(punkte)`
- `_teil(punkte, i)` — Anfang und Ende (einschließlich) des Teilpfads, zu dem Element ``i`` gehört.
- `verschieben(punkte, i, x, y)` — Element ``i`` an (x, y) setzen; ein Punkt nimmt seine Steuerpunkte mit.
- `loeschen(punkte, i)` — Punkt ``i`` entfernen (die Nachbarn verbinden sich); None, wenn es kein Punkt ist oder der Teilpfad zu klein würde
- `_kubisch(p0, p1, p2, p3, t)`
- `_kanten(punkte)` — Alle Kanten als (Index des Elements, Art, Stützpunkte): Art ``"L"`` (p0, p1), ``"C"`` (p0, c1, c2, p1) oder ``"Z"`` (letzter Punkt → Anfang).
- `naechste_kante(punkte, x, y, b, h)` — Die Kante, die (x, y) (Anteile) am nächsten liegt: (Abstand in Bildpunkten b × h, Index, Art, Stützpunkte, t) oder None.
- `einfuegen(punkte, x, y, b, h, toleranz)` — Einen Punkt auf der nächsten Kante einfügen (bei einer Kurve wird sie dort geteilt, ihre Form bleibt). → (neue Liste, Index des

### `editor/objekte/linie.py`

Eine Linie als Wert: Farbe, Stärke, Art und (für Absatzrahmen) die Seiten, auf denen sie steht.

- `_bauen()` — Die Linienarten der Auswahl „Formatvorlage“: Schlüssel → (Name, Strichart, DOCX-Wert, Bahnen, wellig). Die Tabelle steht Qt-frei in ``core/rendering/linien.py``;
- `docx_wert(art)` — Wert von ``w:val`` für eine Linienart (unbekannt: einfach).
- `art_aus_docx(wert)`
- **class `Linie`**
  - `text()`
  - `polster()` — (oben, unten, links, rechts) in pt, wenn ein eigener Abstand gesetzt ist.
  - `aus_text(text)`
  - `mit_seiten(seiten)`
  - `stift(massstab)` — QPen der Linie (bei Mehrfachlinien die Gesamtbreite); ``massstab`` rechnet pt in Bildpunkte um (96/72 am Bildschirm, mal Zoom).
  - `_bahn_stift(w, dicke, strich)`
  - `zeichne(p, x1, y1, x2, y2, massstab)` — Eine einzelne Linie in ihrer Art: einfach, gestrichelt, mehrfach (Bahnen nebeneinander) oder wellig (gezeichnet über ``core/rendering/linien.py``).
  - `rahmen_zeichnen(p, r, massstab, innen_y)` — Zeichnet die gemeinten Seiten eines Rechtecks in der Linienart. ``innen_y``: Höhen der Linien zwischen Absätzen (nur wenn ``h`` gesetzt ist).

### `editor/objekte/smartart.py`

SmartArt: Listen, Prozesse, Hierarchien (Organigramm), Zyklen und Pyramiden aus einem Baum von Knoten.

- `punkte(text)` — [(Ebene, Text)] — die Ebene ergibt sich aus der Einrückung (je zwei Leerzeichen oder ein Tabulator).
- `knoten_aus_text(text)` — Der Knotenbaum (flach, in Reihenfolge) aus dem eingerückten Text; Zeilen mit „• “ werden Aufzählungspunkte des Knotens davor.
- `_glatt(kn)` — Ebenen so begrenzen, dass kein Knoten mehr als eine Ebene unter seinem Vorgänger steht (der erste steht auf Ebene 0).
- `knoten_von(daten)` — Die Knoten des SmartArt als Kopie: aus ``daten["knoten"]``, sonst aus ``daten["text"]``.
- `text_aus_knoten(kn)` — Der eingerückte Text zu den Knoten (Aufzählungspunkte als „• “-Zeilen eine Ebene tiefer).
- `_knotentext(k)`
- `_neue_id(kn)`
- `_index(kn, ident)`
- `_ende(kn, i)` — Index hinter dem letzten Nachkommen von Knoten ``i`` (Ende seines Teilbaums).
- `_geschwister(kn, i, richtung)` — Beginn des vorigen (-1) bzw. nächsten (+1) Geschwisters von ``i`` (gleiche Ebene, gleicher Elternknoten) oder None.
- `form_einfuegen(kn, ident, wie, text)` — Neuen Knoten einfügen relativ zu ``ident`` (ohne gültige Auswahl: hinter den letzten obersten Knoten): ``nach`` (Geschwister dahinter), ``vor``
- `kann_level(kn, ident, richtung)` — Ob ``level(..., "erhoehen")`` bzw. ``"reduzieren"`` für den Knoten geht (der erste Knoten und Knoten, die schon Kind ihres Vorgängers sind,
- `level(kn, ident, richtung)` — Knoten samt Teilbaum eine Ebene tiefer (``erhoehen``) oder höher (``reduzieren``); None, wenn es nicht geht.
- `kann_verschieben(kn, ident, richtung)`
- `verschieben(kn, ident, richtung)` — Knoten samt Teilbaum vor das vorige (``vor``) bzw. hinter das nächste (``zurueck``) Geschwister; None, wenn keins da ist.
- `aufzaehlung(kn, ident, text)` — Einen Aufzählungspunkt an den Knoten hängen.
- `zeichnen_mit_knoten(daten)` — Das SmartArt als Bild und dazu die Rechtecke aller Knoten (id → QRectF in Bildpunkten dieses Bildes).
- `zeichnen(daten)`
- `knoten_rechtecke(daten, b, h)` — id → QRectF der Knoten aus dem Zeichnen. Mit ``b``/``h`` (Größe des Objekts auf dem Blatt) umgerechnet in dessen Bildpunkte, sonst in
- `katalogeintrag(schluessel)`
- `neue_daten(eintrag, farben)` — Daten eines neuen SmartArt aus einem Katalogeintrag (oder dessen Schlüssel); ohne Angabe das Standard-Layout (Organigramm) mit Mustertext.
- `einfuegen(ed, daten)` — Fügt das SmartArt als freies Objekt ein (``editor/objekte/frei_objekt.py``): Rahmen, Griffe und Schnellleiste wie bei WordArt. ``daten`` = Daten
- `_inline_daten(ed)` — Daten eines SmartArt, das als Bild im Text sitzt.
- `daten_der_auswahl(ed)` — Daten des gewählten SmartArt: zuerst das freie Objekt, sonst ein älteres Bild im Text.
- `_text_gegen_knoten(ed, neu)` — Ein neuer ``text`` ohne neue Knoten: weicht er vom Text der vorhandenen Knoten ab, ersetzt er sie; sonst bleibt alles, wie es ist.
- `_inline_aendern(ed, neu)` — Ein SmartArt, das als Bild im Text steht: Daten ändern, neu zeichnen, Breite behalten.
- `aendern(ed, **felder)` — Daten des gewählten SmartArt ändern und neu zeichnen (Breite bleibt, Seitenverhältnis folgt). Ein neuer ``text`` (anders als der zu den
- `knoten_gewaehlt(ed)` — Id des gewählten Knotens des gewählten SmartArt (freies Objekt) oder None.
- `knoten_waehlen(ed, ident)` — Knoten wählen (None: Auswahl aufheben). Das Bild wird nicht neu gezeichnet.
- `_im_objekt(pos, r, a)` — ``pos`` (Editor) in den Koordinaten des ungedrehten Objekts der Größe ``a["b"]`` x ``a["h"]``; ``r`` ist sein Rechteck im Editor.
- `_knoten_rechtecke_gemerkt(ed, d, b, h)` — ``knoten_rechtecke``, gemerkt am Editor, solange Daten (ohne Auswahl) und Größe gleich bleiben.
- `knoten_bei(ed, pos)` — Die Id des Knotens unter ``pos`` (QPointF im Editor, dieselben Koordinaten wie die Rechtecke von ``ed._frei_liste()``) im gewählten SmartArt;
- `knoten_text(ed, ident)` — Der Text des Knotens (ohne Aufzählungspunkte) oder None.
- `knoten_text_setzen(ed, ident, text)` — Den Text eines Knotens setzen (Eintippen im Knoten) und neu zeichnen.
- `_knoten_schreiben(ed, kn, auswahl)`
- `_format_mischen(fmt, kw)` — Angaben in ein Format einarbeiten: None/False entfernt, ``linie``/``text`` werden mit den vorhandenen Angaben zusammengeführt.
- `format_lesen(ed)` — Werte für die Seitenleiste: ``{"format": …, "gewaehlt": Id \| None}`` — das Format des gewählten Knotens, ohne Auswahl das von allen Knoten.
- `format_setzen(ed, **kw)` — Format des gewählten Knotens (ohne Auswahl: aller Knoten) ändern; ``kw`` wie ``teil_format`` des Diagramms (``fuell``, ``linie``, ``schatten`` …, ``text``).
- `befehl_form(ed, wie)` — ``smartartFormEinfuegen``: neuen Knoten relativ zum gewählten (``wie`` siehe ``form_einfuegen``); der neue Knoten wird gewählt.
- `befehl_level(ed, richtung)`
- `befehl_verschieben(ed, richtung)`
- `befehl_aufzaehlung(ed)`
- `kann(ed, was, richtung)` — Ob ein Knotenbefehl gerade geht (zum Ausgrauen): ``level`` (erhoehen/reduzieren), ``verschieben`` (vor/zurueck), ``knoten`` (ein Knoten ist

### `editor/objekte/smartart_zeichnen.py`

Zeichenfunktionen und Layouts für SmartArt.

- `_format_von(nr)` — Das Format des Knotens Nummer ``nr`` (Format wie ``teil_format`` des Diagramms): das des Knotens über dem von allen Knoten (``daten["format"]``).
- `_spiegel(r)`
- `_merke(i, r)` — Rechteck des Knotens Nummer ``i`` (Stelle in der Knotenliste) für ``knoten_rechtecke`` merken.
- `_farbe(daten, ebene)`
- `_stilfarbe(c)` — Die Füllfarbe, die der Formenstil aus der Farbe macht (für den Textkontrast).
- `_text_farbe(c)`
- `_fuellen(p, c, r)` — Stift und Pinsel nach dem Formenstil: 0 flach (ohne Rand), 1 einfach, 2 hell (Farbrand), 3 kräftig (dicker dunkler Rand), 4 3D (Verlauf).
- `_text_zeichnen(p, r, flags, t)` — Text immer ungespiegelt (auch bei „von rechts nach links“, wo die Formen gespiegelt werden).
- `_schrift(p, text, groesse)`
- `_kasten(p, r, text, c, rund, nr)`
- `_kasten_format(p, r, c, fm)` — Füllung, Effekte und Linie des eigenen Formats auf Pinsel und Stift setzen.
- `_pinsel_setzen(p, r, fu)`
- `_pfeil(p, a, b, c)`
- `_bild(b, h)`
- `_text(p, r, t, c, groesse)`
- `_gruppen(pts)` — Oberste Ebene als Überschrift, alles Eingerückte darunter als Unterpunkte: [(Nr. der Überschrift, Text, [(Nr., Unterpunkt)])].
- `_bunt(daten, i)`
- `_spalten(daten, pts, b)`
- `_gruppenliste(daten, pts, b)`
- `_matrix(daten, pts, b)`
- `_chevron(daten, pts, b)`
- `_radial(daten, pts, b)`
- `_zielscheibe(daten, pts, b)`
- `_trichter(daten, pts, b)`
- `_zeitachse(daten, pts, b)`
- `_stufen(daten, pts, b)`
- `_baum(pts)` — Die Wurzeln des Knotenbaums; jeder Knoten {i (Nr.), t (Text), e (Ebene), k (Kinder), a (Assistent)}.
- `_alle(n)`
- `_standard_baum(daten, wurzeln, b)` — Blätter nebeneinander, Eltern mittig über ihren Kindern; Assistenten stehen eine Zeile unter dem Eltern, die übrigen Kinder darunter.
- `_haengend_baum(daten, wurzeln, b, variante)` — Hängende Layouts: die Kinder stehen untereinander neben einer senkrechten Linie unter dem Eltern (links, rechts oder abwechselnd beidseits).
- `_organigramm(daten, pts, b)`
- `_liste(daten, pts, b)`
- `_prozess(daten, pts, b)`
- `_zyklus(daten, pts, b)`
- `_pyramide(daten, pts, b)`
- `_eintraege(pts)` — Oberste Ebene als Eintrag: [(Nr., Überschrift, Textzeilen (Aufzählungspunkte und Unterpunkte), [Nr. der Unterpunkte])].
- `_merke_mehrere(nummern, r)`
- `_zeilen(p, r, zeilen, grund, kopf)` — Aufzählungszeilen linksbündig in ``r`` (Textfarbe nach dem Untergrund ``grund``); ``kopf`` steht vorweg, wenn gegeben.
- `_blockraster(daten, pts, b)`
- `_punktliste(daten, pts, b)`
- `_balkenliste(daten, pts, b)`
- `_beschreibungsliste(daten, pts, b)`
- `_spaltenrahmen(daten, pts, b)`
- `_bildliste(daten, pts, b)`
- `_perspektive(daten, pts, b)`
- `_konvergenz(daten, pts, b)`
- `_kartenprozess(daten, pts, b)`
- `_kreisbeziehung(daten, pts, b)`
- `_segmentzyklus(daten, pts, b)`

### `editor/objekte/sprechblasen.py`

Sprechblasen: Kommentare und verfolgte Änderungen als Blasen im Seitenrand, mit Verbindungslinien zum Text.

- `konfig_lesen(settings)`
- `breite_mm(k)`
- `aktiv(k)`
- **class `Blase`**
- `autor_farbe(autor)`
- `_kuerzen(t, n)`
- `sammeln(doc, kommentare, verwenden)` — Alle Blasen des Dokuments in Textreihenfolge.
- `sammeln_modell(sitzung, verwenden)` — Alle Blasen des Dokuments in Textreihenfolge (Stellen im Rohtext) aus dem Dokumentmodell.
- `_kopf(bl)`
- `blasen_px(key)`
- `karten_pt(key)`
- `messen(bl, breite, font)` — Höhe der Blase bei gegebener Breite (alles in Bildpunkten des Zeichengeräts).
- `stapeln(anker_y, hoehen, unten, abstand)` — Obere Kanten der Blasen: so nah wie möglich an ihrem Anker, ohne sich zu überlappen (und nicht unter `unten`).
- `_ortszeit(iso)` — „2026-10-22 12:11“ in der Ortszeit (die Datei speichert UTC; die Karte links zeigt auch Ortszeit).
- `menue_rect(r)` — Die Fläche des Menüzeichens „☰“ oben rechts in der Blase (für den Klick).
- `zeichnen(p, bl, r, font, druck)` — Eine Blase zeichnen wie eine Karte: Kreis mit Initial, Name fett, Datum, Menüzeichen, darunter der Text — Farben des Designs, Kreis in der Farbe des Kommentars.
- `verbindung(p, bl, x_text, y_text, r, rechts)` — Linie vom Text zur Blase: waagerecht aus dem Seitenrand, dann zur Mitte der Kopfzeile.

## `editor/seite`

### `editor/seite/__init__.py`

Unterpaket ``seite`` von ``core.editor``.


### `editor/seite/absatzopt.py`

Absatzoptionen des Absatz-Fensters (Reiter „Zeilen- und Seitenumbruch“ und die Raster-Haken): Vorgaben, Speichern am Absatz, DOCX.

- `lesen(bf)` — Alle Absatzoptionen eines Absatzformats (Vorgabe, wo nichts gesetzt ist).
- `setzen(bf, w)`
- `als_text(w)` — Die Abweichungen von der Vorgabe als ``Schlüssel=Wert;…`` (für eine Formatvorlage; leer = nur Vorgaben).
- `aus_text(text)`
- `in_ppr(ppr, w)` — Abweichungen von der Vorgabe als Elemente an ``w:pPr`` schreiben (in der Reihenfolge, die das Schema verlangt).
- `aus_ppr(ppr)` — Das Gegenstück zu ``in_ppr``: die Absatzoptionen aus ``w:pPr`` (nur, was gesetzt ist).

### `editor/seite/abschnitte.py`

Abschnitte: Seiteneinrichtung, die mitten im Dokument wechseln kann.

- `_bilder_zu_text(angabe)`
- `_bilder_aus_text(angabe)`
- `seite_zu_dict(ps)` — Die Einrichtung als JSON-fähiges Verzeichnis; die Bilder der Kopf-/Fußzeilen (``ps.bilder``) als Text.
- `seite_aus_dict(d)`
- `eintrag(typ, ps)`
- `lesen(blockformat)`
- `umbrueche(doc)` — [(Blocknummer, Beginn, Einrichtung des folgenden Abschnitts)] in Dokumentreihenfolge.
- `anzahl(doc)`
- `index_bei(doc, position)` — Nummer (0-basiert) des Abschnitts, in dem die Position liegt.
- `einrichtung(doc, basis, index)` — Einrichtung des Abschnitts `index` (0 = Dokumenteinrichtung); verknüpfte Kopf-/Fußzeilen werden vom Vorgänger übernommen.
- `alle_einrichtungen(doc, basis)` — [(Beginn, Einrichtung)] für jeden Abschnitt (der erste mit Beginn „naechste“).
- `beginn(doc, index)` — Zeichenposition, an der Abschnitt `index` beginnt.
- `ende(doc, index)`
- `_setze(cursor, wert)`
- `einfuegen(doc, cursor, typ, basis)` — Abschnittsumbruch an der Schreibmarke: der Absatz wird geteilt, der erste Teil beschließt den Abschnitt.
- `einfuegen_an(doc, position, typ, basis)` — Abschnitt ab ``position`` beginnen lassen (z. B. am Anfang der aktuellen Seite). Steht die Stelle am Anfang eines Absatzes, beschließt
- `entfernen(doc, index)` — Den Umbruch am Ende von Abschnitt `index` entfernen (ist es der letzte, den davor): die beiden Abschnitte werden einer
- `setzen(doc, index, ps, typ)` — Einrichtung (und Beginn) eines Abschnitts ab dem zweiten ändern; für den ersten gilt `ed.page`.
- `teile(qdoc, basis)` — Für Seitenansicht, Druck und PDF: [(Dokument, Einrichtung, Beginn)] je Abschnitt und Hinweise.

### `editor/seite/anzeige_extra.py`

Anzeige- und Druckhilfen: ausgeblendeter Text, Feldschattierung, Feldcodes, Zeichnungsobjekte, geänderte Zeilen, Objektanker.

- **class `VersteckterText`**(QSyntaxHighlighter) — Ausgeblendeter Text (Eigenschaft P_VERSTECKT) wird nur in der Anzeige unsichtbar gemacht (winzige, durchsichtige Schrift)
  - `__init__(doc, zeigen)`
  - `setze_zeigen(an)`
  - `highlightBlock(text)`
- `_bereiche(d, prop)` — [(von, bis, wert)] zusammenhängender Zeichenbereiche mit der Eigenschaft prop.
- `versteckte_entfernen(d)` — Löscht den ausgeblendeten Text aus der KOPIE (Druck, PDF, Seitenzählung). → Anzahl gelöschter Bereiche.
- `feldcodes_einsetzen(d)` — „Feldfunktionen drucken“: an die Stelle des Ergebnisses tritt der Feldcode in geschweiften Klammern.
- `feldbereiche(d)`
- `zeichnungen_entfernen(d)` — „Zeichnungsobjekte drucken“ aus: Formen, WordArt, Diagramme und SmartArt (Bilder mit P_OBJEKT) fehlen im Ausdruck.
- `aenderungszeilen(d)` — Senkrechte Bereiche (oben, unten) in Dokumentkoordinaten aller Zeilen, in denen verfolgte Änderungen stehen.

### `editor/seite/blasen_druck.py`

Sprechblasen beim Drucken und im PDF: Die Seite wird verkleinert, daneben stehen die Kommentar-Blasen

- `blasen_geometrie(page, opt)` — Platz für Sprechblasen beim Drucken: Die Seite wird verkleinert, daneben stehen die Blasen. → None ohne Blasen.
- `blasen_pro_seite(d, page, liste, bd, ort)` — {Blattseite (1-basiert): [(Blase, y in px auf der Textfläche)]} — die Blasen stammen aus der Kopie selbst.
- `blasen_zeichnen(p, eintraege, geo)`

### `editor/seite/deckblatt.py`

Deckblätter (Einfügen ▸ Deckblatt): 17 Gestaltungen in den Gruppen der Vorlage (Artikel, Firma, Lebenslauf, Abschlussarbeit), je im

- **class `Feld`** — Ein Platzhalter-Absatz: ``y`` = Oberkante als Anteil der Blatthöhe, ``x`` = linker Rand als Anteil der Blattbreite (bei links).
- **class `Gestaltung`**
- `_kontakt(y, farbe, x, ausrichtung, abstand)`
- `_arbeit(y, farbe)`
- `gestaltung(name)`
- `_stil(farbe, alpha)`
- `_verlauf(r, farben, senkrecht)`
- `_flaeche(b, r, fuellung)` — Rechteck füllen: Farbe (``#rrggbb``) oder Verlauf.
- `_wolken(b, r, y, farbe, n)`
- `_dreieck(x1, y1, x2, y2, x3, y3)`
- `_segelboot(b, x, y, s)`
- `_puzzle(b, x, y, s, farbe)`
- `_blume(b, cx, cy, s)`
- `_g_mosaik(b, r, w, h, x0, y0, R)`
- `_g_himmel(b, r, w, h, x0, y0, R)`
- `_g_sonne(b, r, w, h, x0, y0, R)`
- `_g_kopfbalken(b, r, w, h, x0, y0, R)`
- `_g_wellen(b, r, w, h, x0, y0, R)`
- `_g_blaurand(b, r, w, h, x0, y0, R)`
- `_g_stadt(b, r, w, h, x0, y0, R)`
- `_g_notizzettel(b, r, w, h, x0, y0, R)`
- `_g_sonnenblume(b, r, w, h, x0, y0, R)`
- `_g_gruen(b, r, w, h, x0, y0, R)`
- `_g_puzzle(b, r, w, h, x0, y0, R)`
- `_g_segel(b, r, w, h, x0, y0, R)`
- `_g_rahmen(b, r, w, h, x0, y0, R)`
- `_g_linien(b, r, w, h, x0, y0, R)`
- `_g_siegel(b, r, w, h, x0, y0, R)`
- `_grafik(b, name, r)` — Die Grafik einer Gestaltung (ohne Text) auf das Blatt ``r``.
- `_schrift(f, blatt_hoehe_px, quer)` — Schrift eines Feldes im Maßstab des Blattes (Original: A4 hoch = 1123 Bildpunkte; quer etwas kleiner).
- `zeichnen_mit(b, name, r, mit_text, engine)` — Gestaltung ``name`` auf das Blatt ``r`` (weißer Grund, Grafik, auf Wunsch die Platzhalter) über ein beliebiges Rendering-Backend.
- `zeichnen(p, name, r, mit_text)` — Gestaltung ``name`` auf das Blatt ``r`` (QPainter, QRectF): für die Galerie.
- `grafik_bild(name, breite_px, hoehe_px)`
- `hat_deckblatt(dok)` — Beginnt das Dokument mit einem Deckblatt (erster Absatz trägt die Angabe ``deckblatt``)?
- `entfernen(ed)` — Das Deckblatt (erster Abschnitt) herausnehmen; das Dokument bekommt die Einrichtung des zweiten Abschnitts.
- `einfuegen(ed, name, quer)` — Deckblatt ``name`` als ersten Abschnitt an den Anfang setzen (ersetzt ein vorhandenes).
- `_bild_text(img)`

### `editor/seite/druck.py`

Drucken nach den Einstellungen des Druckfensters: Seitenauswahl, Blattseiten, mehrere Seiten pro Blatt, anderes Papier.

- `papier_name(b_mm, h_mm)` — „A4“ für 210 × 297 (mit 2 mm Toleranz, in beiden Lagen), sonst „Benutzerdefiniert“.
- `bereich_lesen(text, gesamt)` — „1-3, 5“ → [1, 2, 3, 5]. Seiten außerhalb 1..gesamt fallen weg; ungültige Eingabe oder nichts Übriges → None.
- `seiten_nach_wahl(ein, gesamt)` — Welche Seiten das Druckfenster meint (aufsteigend); ohne gültigen Bereich alle.
- `blatt_zeichnen(p, rect, bilder, pro_blatt, rand)` — Setzt die Seitenbilder in einem Raster auf das Blatt; jedes wird ins eigene Feld eingepasst (Seitenverhältnis bleibt).
- `optionen_aus(opt, ein, noten)` — Die Ausgabeoptionen der Einstellungen, ergänzt um die Wahl im Druckfenster.
- `zwischen_pdf(qdoc, page, opt, noten, pfad)`
- `pdf_seiten_bilder(pfad, breite_px, nummern)` — Rastert Seiten (Nummern ab 1 in der Zwischen-PDF) auf die gewünschte Breite.
- `vorschau_bild(qdoc, page, opt, noten, nummern, breite_px)` — Die Seiten `nummern` (der Ausgabe, ab 1) so, wie die Optionen sie ausgeben — für die Vorschau.
- `drucken(printer, qdoc, page, opt, ein, noten)` — Druckt nach den Einstellungen `ein` (Ergebnis des Druckfensters). → Zahl der gedruckten Seiten.
- **class `Zwischenseiten`** — Das Dokument einmal als Zwischen-PDF ausgegeben und geladen; jede Seite lässt sich in beliebiger Größe rastern (Druckvorschau).
  - `__init__(qdoc, page, opt, noten)`
  - `anzahl()`
  - `groesse_px(n, zoom)` — Größe der Seite n bei 96 dpi mal Zoom.
  - `bild(n, zoom)`
  - `schliessen()`

### `editor/seite/fussnoten.py`

Fuß- und Endnoten in der Kopie für Seitenzählung, Seitenansicht, PDF und Druck: gesammelt am Textende, unten auf der Seite

- `fussnoten_am_fuss(page, noten)` — Fußnoten am Seitenfuß gibt es bei einer Spalte; bei mehreren Spalten stehen sie gesammelt am Textende.
- `_notenfragmente(d)` — (Absatz, Textstück, Art „f“/„e“, Id als Text) jeder Notenmarke in Textreihenfolge.
- `_notenabschnitt(c, art, titel, ids, noten)`
- `noten_anhaengen(d, noten, arten)` — Fuß- und Endnoten gesammelt am Textende (nur in der Kopie für Seitenzählung, PDF und Druck). Fußnoten stehen bei einer
- `_fussnoten_stellen(d)` — [(Zeichenstelle, Fußnoten-Id, Länge)] in Textreihenfolge.
- `zeilenbereiche(d)` — [(oben, unten, Zeichenstelle des Zeilenanfangs, Blocknummer)] aller Zeilen in Dokumentreihenfolge.
- `_notenschrift(d)`
- `_notendoc_fabrik(liste, schrift, breite)` — Liefert ``notendoc(nr, id)``: das gesetzte Textdokument einer Fußnote (je Id einmal).
- `_notenhoehe(eintraege, notendoc)`
- `_belegung(stellen, zeilen, ch)` — {Seite (1-basiert): [(laufende Nummer, Fußnoten-Id)]} nach der Zeile, in der die Marke steht.
- `_erste_zeile_ohne_platz(zeilen, seite, ch, grenze)` — Zeichenstelle der ersten Zeile der Seite, die unter die Grenze ragt (die erste Zeile der Seite bleibt immer).
- `_zu_hohe_zeile(belegung, zeilen, ch, notendoc)` — Stelle, an der ein Seitenwechsel nötig ist, damit die Fußnoten der Seite Platz haben; None, wenn alles passt.
- `_seitenwechsel_vor(d, pos)` — Seitenwechsel vor der Zeichenstelle: am Absatzanfang als Umbruchregel, sonst wird der Absatz geteilt.
- `_platzierung(belegung, notendoc, ch)` — {Seite: {"hoehe": px, "noten": [(y ab Textflächenanfang, Textdokument, Id)]}}.
- `fussnoten_am_seitenende(d, page, noten)` — Fußnoten unten auf der Seite, auf der ihre Marke steht (nur in der Kopie für Seitenzählung, Seitenansicht, PDF und Druck).
- `_notenmarken(d, ort, liste)` — {(Art, Id): Lage der Marke auf ihrer Seite}; nur Seiten aus ``liste``.
- `_notenziele(d, ort, liste)` — {(Art, Id): Lage der Note}: Fußnoten am Seitenfuß, Endnoten und gesammelte Noten am Textende.
- `notenlinks_sammeln(d, page, liste, ort)` — Sprungverweise für die PDF: Marke → Note und Note → Marke (Fußnoten am Seitenfuß, Endnoten und gesammelte Noten am Textende).

### `editor/seite/lese_zeilenluft.py`

Zeilenluft der Lesehilfe: mehr Platz zwischen den Zeilen — nur in der Anzeige beim Bearbeiten, nie im Dokument.

- `_markiert(bf)`
- `aktiv(doc)` — Trägt ein Absatz des Dokuments noch den Zusatzabstand der Lesehilfe?
- `_zuruecksetzen(bf)`
- `_durchlaufen(doc, aendern)`
- `zuruecknehmen(doc)` — Jedem Absatz den ursprünglichen Zeilenabstand zurückgeben (ohne Rückgängig-Schritt, wenn das Dokument sonst nichts mehr davon weiß).
- `bereinigte_kopie(doc)` — Eine Kopie ohne den Zusatzabstand zum Speichern oder Ausgeben; das bearbeitete Dokument bleibt unberührt.
- `anwenden(doc, faktor)` — Zeilenluft ``faktor`` (1,0 = normal) für alle Absätze setzen; vorherige Werte werden zuerst zurückgenommen. Ändert nichts, wenn nichts zu tun ist.

### `editor/seite/pdf_struktur.py`

Struktur der PDF-Ausgabe: Lesezeichen (Gliederung), Kommentar-Notizen und Sprungverweise. ``*_sammeln`` liest die Stellen aus der

- `fluss_ort(ch, spalten)` — Ort im Textfluss einer Druckkopie: y → (Seite 1-basiert, y in der Spalte); beim Blattweg liefert ``Seitenlauf.ort`` dasselbe.
- `_erste_kommentarstellen(d)` — {Kommentar-Id: erste Zeichenstelle} aus der Eigenschaft P_KOMMENTAR.
- `kommentarstellen(d, ch, liste, kommentare, spalten, ort)` — [(Seitenindex, y in px auf der Textfläche, Text)] für die PDF-Notizen. `kommentare` = {Kommentar-Id: Text}; die Stelle
- `_blockseite(lay, b, ort, spalten)` — Seite (1-basiert), auf der der Absatz beginnt; ``ort`` ist die Ortsfunktion oder die Höhe einer Seite im Textfluss.
- `_stilname(b)`
- `_ist_stileintrag(b, was)` — Titel, Untertitel, Zitat („andere“) oder eigene Formatvorlage („eigene“) als Lesezeichen.
- `_textmarken_anhaengen(b, idx, out)`
- `_block_eintraege(b, idx, was, out)` — Hängt die Lesezeichen des Absatzes (Überschrift, Stil, Textmarken) an ``out``: (Ebene, Titel, Seitenindex, Stelle).
- `lesezeichen_sammeln(d, ch, liste, was, spalten, ort)` — [(Ebene, Titel, Seitenindex 0-basiert)] für die PDF-Gliederung: Überschriften und/oder Textmarken.
- `_rand_pt(page)`
- `_notizen_anfuegen(w, kommentare, page)`
- `_verweis_anfuegen(w, k, ml, mt)`
- `_verweise_anfuegen(w, links, page)`
- `_gliederung_anfuegen(w, eintraege)`
- `gliederung_schreiben(pfad, eintraege, kommentare, page, links)` — Schreibt Lesezeichen und Kommentare in die fertige PDF (QPdfWriter kann das nicht selbst) — mit pypdf.

### `editor/seite/querblatt.py`

Blätter verschiedener Größe im Editor (z. B. ein Querformat-Blatt zwischen Hochformat-Blättern) — nur in der Anzeige beim Bearbeiten.

- `rechts_px(bf)` — Der rechte Einzug, wie ihn der Benutzer eingestellt hat (ohne den Zusatz der Anzeige).
- `rechts_setzen(bf, px)` — Rechten Einzug setzen; die Anzeige rechnet ihren Zusatz danach neu hinzu.
- `_geometrie(p)`
- `einrichtungen(doc, page)`
- `aktiv(doc, page)`
- `masse(doc, page)` — (größte Textbreite, größte Texthöhe) aller Abschnitte in Bildpunkten (ohne Zoom).
- `_abschnitt_je_block(doc, eins)` — (Block, Einrichtung) für jeden Absatz in Textreihenfolge.
- `_setzen(doc, aendern)`
- `breite_anwenden(doc, page, zoom, an)` — Den Absätzen und Tabellen schmalerer Abschnitte den Zusatz geben (``an=False``: überall wegnehmen). → True bei Änderung.
- `zuruecknehmen(doc)` — Den Zusatz überall wegnehmen (für Kopien zum Speichern, Drucken, PDF).
- `bereinigte_kopie(doc)`
- `hat_zusatz(doc)`
- `blattplan(doc, page, ch)` — Einrichtung jeder Seite des Textflusses (Seiten der Höhe ``ch`` im Layout): die des Abschnitts, dessen Text oben auf der Seite steht.
- `_am_seitenanfang(oben, ch, b)` — Der Absatz beginnt oben auf einer Seite. Rundung: knapp unter der Seitengrenze zählt als oben; der erste Absatz des Dokuments auch.
- `_zu_hoch_fuer_blatt(tl, oben, erste, plan, ch, zoom)` — Eine Zeile des Absatzes (Layout ``tl``, Oberkante ``oben``) reicht unter die Textfläche des Blattes ``erste``; nur die Zeilen auf dieser Seite zählen.
- `grenzen(doc, page, ch, zoom)` — Absätze, vor die ein eigener Seitenumbruch gehört: der erste Absatz eines Abschnitts mit anderer Blattgröße, wenn er nicht oben auf

### `editor/seite/seiten_aufteilung.py`

Seitenaufteilung, PDF-Ausgabe und Drucken mit Kopf-/Fußzeile und Seitenzahlen.

- `layout_device()` — Ein Gerät mit festen 96 dpi, an dem alle Dokumente gesetzt werden.
- `zoom_device(faktor)` — Ein Gerät mit 96 dpi × Zoom: Text, Ränder, Tabellen und Bilder werden beim Setzen mitskaliert.
- `bind_layout(qdoc, faktor)`
- `ausgabe_seiten(logisch, page)` — Seiten der Ausgabe: bei mehreren Spalten füllen je so viele „logische“ Spaltenseiten eine Blattseite.
- `paginated_copy(qdoc, page, noten, silben, einspaltig, versteckt, fussnoten, lese_luft, blaetter)` — ``blaetter``: das ganze Dokument in Blattkoordinaten setzen (Seitenlauf mit allen Abschnitten), statt im Textfluss eines Abschnitts.
- `_abschnittsbeginn_markieren(d)` — Nur in der Kopie: Der Absatz nach einem Abschnittsumbruch („nächste/gerade/ungerade Seite“) beginnt eine neue Seite.
- `page_count(qdoc, page)`
- `_start_nummer(page)` — Angezeigte Seitennummer vor der ersten Seite: „Beginnen mit“ der Einrichtung.
- `_kapitel_liste(d, page)` — Kapitelnummer je Seite für Kopf-/Fußzeile; leer ohne Kapitelebene.
- `_kapitel_von(kapitel, n, spalten)`
- `_nur_formular(page, opt)` — Nur die Feldinhalte (für vorgedruckte Formulare): kein Seitenschmuck, keine Kopf-/Fußzeile.
- `_inhalt_anpassen(d, opt)` — Inhalt der Ausgabekopie nach den Optionen: Formulardaten, Feldcodes, Zeichnungen, Lücken.
- `_darstellung_anpassen(d, opt)` — Darstellung der Ausgabekopie nach den Optionen: Hintergründe, Steuerelemente, Farben, Hervorhebungen, Verweise.
- `_ausgabekopie(qdoc, page, opt)` — Die gesetzte Kopie für Druck/PDF mit allen Optionen; → (Kopie, Silbenfarben). Die Silbenfarben müssen bis zum Zeichnen leben.
- `_seitenliste(d, page, total, first, last, opt)`
- **class `_Lauf`** — Was für jede Seite der Ausgabe gleich bleibt.
- `_lauf_vorbereiten(d, page, total, liste, base, skala, opt)`
- `_seite_ausgeben(p, lauf, n)`
- `_pdf_ergebnisse(opt, d, page, liste, spalten, ort)` — Stellen für Lesezeichen, Kommentar-Notizen und Sprungverweise der PDF (``export_pdf`` trägt sie danach ein).
- `render(qdoc, page, device, first, last, dpi, opt)` — Zeichnet die Seiten first..last auf device (QPdfWriter/QPrinter). → Anzahl Seiten.
- `_leerseite_davor(i, typ, gesamt)` — 1, wenn vor dem Abschnitt i eine Leerseite nötig ist („gerade/ungerade Seite“), sonst 0.
- `_leerseiten_plan(typen, zaehl)` — ([Seitenzahl vor dem Abschnitt einschließlich Leerseite], [Leerseite davor 0/1], Seiten insgesamt).
- `_erste_nummern(teile, zaehl, leer)` — Angezeigte Nummer vor dem ersten Blatt je Abschnitt: „Beginnen mit“ setzt neu an, sonst geht es nach dem vorigen Teil weiter.
- `_startteil(zaehl, offsets, leer, first, last)` — Erster Abschnitt, der wirklich gedruckt wird: sein Papier gilt schon beim Start.
- **class `_Folge`** — Stand beim Ausgeben mehrerer Abschnitte hintereinander.
- `_papier_wechseln(f, i, ps)` — Das Papier eines Abschnitts gilt erst ab seiner ersten gedruckten Seite (der erste Teil ist schon eingestellt).
- `_abschnitt_drucken(f, i, d, ps, o, z, nummer)` — Leerseite vor dem Abschnitt (falls nötig) und seine Seiten im gewünschten Bereich.
- `render_dokument(qdoc, page, device, first, last, dpi, opt, layout)` — Wie render(), aber mit mehreren Abschnitten: jeder Abschnitt wird mit seiner eigenen Seitengröße, seinen Rändern, Spalten und
- `_blattweise(qdoc, page, teile, opt)` — Druck, PDF, Seitenzahl und Seitenbilder gehen über den Seitenlauf (``render_blaetter``); der Weg je Abschnitt bleibt nur als Rückfall, wenn
- `_blatt_zeichnen(p, d, bl, n, total, nummer, base, frei_alle, opt)` — Ein Blatt des Seitenlaufs (Nummer n, 1-basiert; angezeigt als ``nummer``) mit Schmuck, Bildern, Kopf-/Fußzeile, Zeilennummern, Spaltenlinie
- `_gesetzt(qdoc, page, opt)` — Das ganze Dokument im Seitenlauf gesetzt: (Kopie, gedruckte Blätter, Index der freien Bilder).
- `_blatt_liste(d, blaetter, total, first, last, opt)` — Die Blätter, die ausgegeben werden: Bereich, Auswahl („nur_seiten“), Leerseiten weglassen.
- `render_blaetter(qdoc, page, device, first, last, dpi, opt, layout)` — Druck/PDF direkt nach den Blättern des Seitenlaufs: das ganze Dokument wird einmal gesetzt (Abschnitte können auf derselben Seite
- `_frei_index(d, page)` — Index der freien Bilder im Fluss (je Kopie einmal berechnet).
- `_kopf_fuss_zeichnen(p, page, n, nr_offset, total, gesamt, base, kapitel)`
- `_zeilennummern_zeichnen(p, d, page, n, base)`
- `_fussnoten_zeichnen(p, d, page, n)` — Fußnoten am Seitenfuß, mit kurzem Trennstrich.
- `_spalte_zeichnen(p, d, page, lp, x)` — Die logische Spaltenseite ``lp`` an Stelle ``x`` der Blattseite.
- `_fussnoten_trennlinie(backend, y0, breite)` — Kurzer Trennstrich über den Fußnoten.
- `_balken_stil()` — Stil der Änderungsbalken: Farbe aus dem Thema (Farbe.ROT), Strichstärke 1,4.
- `_aenderungsbalken(backend, balken, page, n, lp, x_spalte)` — Änderungsbalken neben den Zeilen mit verfolgten Änderungen.
- `_balken_blatt(backend, balken, bl, n)` — Änderungsbalken neben den Zeilen des Blattes, die verfolgte Änderungen tragen (Koordinaten des Laufs).
- `_spaltenlinien_zeichnen(backend, page, n_sp)`
- `zeichne_seite(p, d, page, n, total, base, hintergrund, balken, nr_offset, gesamt, kapitel)` — Eine Seite (Nummer n, 1-basiert) mit Seitenschmuck, Kopf-/Fußzeile und Text; Maßstab 96 dpi, Ursprung links oben.
- `seite_als_bild(qdoc, page, n, faktor, d, noten, nr_offset, gesamt)` — Seite n als Bild (für die Zwei-Seiten-Ansicht und „Als Bild exportieren“). Ohne ``nr_offset`` gilt „Beginnen mit“ der Einrichtung.
- `seitenzahl(qdoc, page, noten)` — Seiten der Ausgabe über alle Abschnitte (einschließlich Leerseiten vor „gerade/ungerade Seite“).
- `seiten_bilder(qdoc, page, noten, faktor)` — Alle Seiten der Ausgabe als (Nummer, Bild, Seiteneinrichtung) — mit mehreren Abschnitten je Abschnitt in der eigenen Größe.
- `_leere_seiten(d, page, total)`
- `_page_layout(page, quer)`
- `_quer(geo)`
- `_xmp_autor(author)`
- `_pdf_schreiber(path, page, geo, title, author)`
- `export_pdf(path, qdoc, page, title, author, noten, lesezeichen, silben, kommentare, extra, erste, letzte)` — Schreibt die Seiten ``erste`` bis ``letzte`` (``None``: bis zum Ende) als PDF. → Seitenzahl des Dokuments.
- `print_document(printer, qdoc, page, opt)`

### `editor/seite/seiten_aufteilung_deko.py`

Kopf- und Fußzeilen, Seitenschmuck und Druckseiten-Auswahl.

- `_expand(text, n, total, page, kapitel)`
- `_draw_hf(p, hf, rect, n, total, base, page, kapitel)` — Kopf- oder Fußzeile einer Seite; ``n`` ist die angezeigte Seitennummer (bestimmt auch „außen“/„innen“).
- `_hf_schrift(base, fmt)` — Schrift einer Kopf-/Fußzeile aus einem Zeichenformat (``HeaderFooter.fmt``).
- `_laeufe_eigen(hf)` — Hat die Zeile eigene Textstücke mit Format, die den Text ergeben? Texteffekte hängen an der ganzen Zeile: dann bleibt es beim alten Weg.
- `_zeichne_laeufe(p, hf, rect, n, total, base, page, kapitel)` — Kopf-/Fußzeile Stück für Stück: jedes Textstück in seiner Schrift und Farbe, Zeile für Zeile ausgerichtet.
- `_hf_effekt(p, fmt, f, rect, text, flag)` — Zeilen mit Texteffekt (Schatten, Spiegelung, Leuchten, Kontur …) zeichnen: dieselben Bausteine wie im Dokument (``editor/text/textfx.py``), über das Rendering-Backend.
- `_ohne_hintergruende(d)`
- `_text_schwarz(d)` — „Text schwarz drucken“ in der Kopie: jede Schriftfarbe wird schwarz (Verknüpfungen und Platzhalter eingeschlossen).
- `_formularteile_ausblenden(d, steuer, platzhalter)` — Steuerelemente (Felder mit Wert, Schaltflächen, Kästchen) und/oder Platzhaltertexte leerer Felder werden in der Kopie unsichtbar.
- `_ohne_hervorhebungen(d)` — Nur die Texthervorhebung (Marker) entfällt; Absatz- und Tabellenhintergründe bleiben.
- `_ohne_links(d)` — PDF ohne Hyperlinks: der Text bleibt, nur das Linkziel entfällt (Qt schreibt sonst für jedes Linkziel einen PDF-Link).
- `_textmarken_klammern(d)` — „Textmarken drucken“: jede Textmarke steht in eckigen Klammern im Ausdruck.
- `_bf_ohne(bf)`
- `seitenschmuck(p, page, hintergrund, flaeche, rahmen, wasserzeichen)` — Seitenfarbe, Seitenrahmen und Wasserzeichen. Koordinaten: Seite in 96-dpi-Bildpunkten, Ursprung links oben. ``flaeche`` (QRectF) überschreibt das Seitenrechteck — der Editor
- `seiten_liste(total, first, last, opt)` — Welche Seiten in welcher Reihenfolge gedruckt werden (Duplex, umgekehrte Reihenfolge).
- `frei_zeichnen(p, objekte, hinter)` — Freie Bilder der Seite hinter oder vor dem Text (zum Beispiel ein Band im Briefkopf, Foto, Unterschrift).
- `_druckmarken(p, page, grenzen, zuschnitt)` — Textbegrenzungen (gestrichelter Rahmen um die Textfläche) und Zuschnittsmarken (Ecken) auf der gedruckten Seite.
- `_inhalt_zeichnen(p, d, rect)` — Wie ``QTextDocument.drawContents``, aber mit schwarzer Grundschrift: Text ohne eigene Farbe nähme sonst die Textfarbe des
- `absatz_zusatz_zeichnen(p, d, faktor)` — Was an den Absätzen nicht von Qt kommt: Rahmen und die Nummern mehrstufiger Listen.
- `_rahmengruppen(d)` — [[Rahmenangabe, [Absätze], Nummer des letzten Absatzes]]: zusammenhängende sichtbare Absätze mit gleichem B_RAHMEN.
- `_rahmengruppen_bauen(d)`
- `_rahmenrechteck(r, linie, faktor, polster)` — Rechteck des Rahmens: Absatzfläche plus Abstand (eigener Abstand der Linie in pt, sonst ``polster``).
- `absatzrahmen_zeichnen(p, d, faktor, polster)` — Rahmen um zusammenhängende Absätze mit gleichem B_RAHMEN. Koordinaten: Dokument (Layoutgerät); faktor = Zoom.

### `editor/seite/seitenfluss.py`

Umbruchregeln am Seitenende: „Diesen Absatz zusammenhalten“, „Nicht vom nächsten Absatz trennen“ und die Absatzkontrolle

- `seitenraster(doc, ch)` — Die Höhe, in der Qt die Seiten dieses Dokuments umbricht: seine Seitenhöhe (sonst ``ch``), auf 1/64 Bildpunkt abgeschnitten.
- `_von_oben(zeile, ch)` — Abstand einer Zeile (aus ``_zeilen``) vom oberen Rand ihrer Seite.
- `fertig_setzen(doc)` — Setzt das ganze Dokument sofort. Qt setzt sonst in Etappen: Absätze dahinter haben noch keine Zeilen, die Regeln sähen sie nicht,
- **class `_Schritt`** — Der Bearbeitungsblock der Prüfung: hängt an den vorigen Rückgängig-Schritt und lässt zwischen den Durchgängen neu setzen.
  - `__init__(doc)`
  - `neu_setzen()`
  - `ende()`
- `ist_manuell(bf)` — Ein Seitenumbruch oberhalb, den der Benutzer gesetzt hat (kein von Lunivo eingefügter).
- `_zeilen(b, ch)` — (Seite, oben, unten) jeder Zeile des Absatzes.
- `_hoehe(z)`
- `_zeilen_auf(z, seite)`
- `_zerrissen(z, ch, w)` — Der Absatz läuft über ein Seitenende, obwohl „zusammenhalten“ oder die Absatzkontrolle das verbietet.
- `_vom_naechsten_getrennt(z, naechster, ch, w)` — „Nicht vom nächsten Absatz trennen“: der nächste Absatz beginnt auf einer anderen Seite, als dieser endet.
- `_verletzt(b, naechster, ch, w)`
- `_gesetzte(doc)` — Die sichtbaren Absätze, die schon gesetzt sind (mit Layout).
- `_oben_auf_seite(bf, z, ch, spiel)` — Die erste Zeile steht (bis auf ``spiel``) oben auf einer Folgeseite, die der Textfluss begonnen hat.
- `_vorabstand_pruefen(b, ch, zurueck)` — Abstand vor einem Absatz: am Seitenanfang wegnehmen (Wert in ``B_VORHER`` merken), sonst zurückgeben. → True, wenn geändert.
- `_seitenanfang(doc, ch, schritt)` — Am Anfang einer Seite, die durch den Textfluss entsteht, entfällt der Abstand vor dem Absatz. Nach einem
- `_hat_umbruch(b)`
- `_alte_umbrueche_entfernen(doc)`
- `_braucht_umbruch(b, ch)` — Der Absatz verletzt eine Umbruchregel und ein Umbruch davor hilft (er hat noch keinen und steht nicht schon ganz oben).
- `_umbruchstellen(doc, ch, weitere)` — Absätze, vor die jetzt ein eigener Umbruch gehört: Regelverletzungen und die von ``weitere()`` genannten.
- `_umbrueche_setzen(bloecke)`
- `anwenden(doc, ch, weitere)` — Umbruchregeln auf das Dokument anwenden (``ch`` = Höhe der Textfläche einer Seite in Bildpunkten; gilt nur, wenn das Dokument keine

### `editor/seite/seitenrahmen.py`

Der Rahmen um die Seite („Rahmen und Schattierung“ ▸ Seitenrand): Lage, Abstände, Kunstrahmen.

- `rechteck(b, page, seite)` — Das Rechteck des Rahmens in Bildpunkten, auf einer Seite mit dem Rechteck ``seite`` (Qt-Hülle um ``core.rendering.seitenrahmen.rechteck``).
- `zeichnen(p, b, page, seite)` — Den Seitenrahmen auf eine Seite zeichnen (Linie in ihrer Art oder Kunstrahmen), über das Rendering-Backend.

### `editor/seite/seitenzahl.py`

Seitenzahlen in Kopf- oder Fußzeile setzen und entfernen (Einfügen ▸ Seitenzahl). Arbeitet auf ``PageSettings``; keine Oberfläche.

- `_ohne_zahl(text)`
- `seitenzahl_setzen(page, ort, ausrichtung, muster, format, start, kapitel)` — Seitenzahl in Kopf- (``ort="kopf"``) oder Fußzeile setzen. Eine vorhandene Seitenzahl dort wird ersetzt, übriger Text bleibt;
- `seitenzahlen_entfernen(page)` — Seitenzahl (mit „Seite … von …“) aus Kopf- und Fußzeile entfernen. → ob es eine gab.
- `seitenzahl_loeschen_bereich(page, art, blatt)` — Seitenzahl nur auf einem Teil der Seiten eines Abschnitts entfernen (Seitenzahl löschen ▾ in der Kopf-/Fußzeilenleiste).
- `nummer(n, page, kapitel)` — Die Seitennummer ``n`` in der Zahlenart der Einrichtung, mit Kapitelnummer davor („2-1“).
- `text(vorlage, n, gesamt, page, kapitel)`
- `ausrichtung(align, n)` — „außen“: ungerade (rechte) Seiten rechts, gerade links; „innen“ umgekehrt. Andere Werte bleiben.
- `erste_nummer(page)` — Nummer der ersten Seite eines Abschnitts, wenn er nicht fortsetzt (sonst 1).
- `absatz_oben(lay, b)` — y der ersten Zeile des Absatzes im Textfluss — danach richtet sich, auf welcher Seite er beginnt. Nicht ``blockBoundingRect(b).top()``:
- `seitenwechsel(d, seitenhoehe)` — Zeichenstellen, an denen eine neue Seite beginnt (erste Zeile der Seiten 2, 3, …), nach der Höhe einer Seite im Layout.
- `_kapitel_nummer(b, mehr)`
- `kapitel_je_seite(d, ebene, wechsel)` — Kapitelnummer jeder Seite (Index 0 = Seite 1): die Nummer der letzten Überschrift der Ebene ``ebene``, die auf der Seite oder

### `editor/seite/silbentrennung.py`

Silbentrennung für Druck, PDF und Seitenzählung: weiche Trennstriche (U+00AD) in einer Kopie des Dokuments.

- `_trenner(sprache)` — pyphen-Wörterbuch (zwischengespeichert); None, wenn pyphen oder die Sprache fehlt.
- `_trennstellen(block, trenner)` — Zeichenstellen im Dokument, an denen im Absatz ein weicher Strich eingefügt wird.
- `_einfuegen(d, stellen)`
- `silben_einfuegen(d, sprache)` — Fügt in einer KOPIE des Dokuments weiche Trennstriche (U+00AD) in lange Wörter ein; Qt bricht dort um und zeigt „-“.

### `editor/seite/umbruch.py`

Textumbruch um Bilder: Bilder, die links oder rechts stehen und vom Text umflossen werden.

- `_rahmen(frame)`
- `schwebende_rahmen(doc)` — {Position des Bildzeichens: Rahmen} für alle schwebenden Bilder des Dokuments.
- `schwebend(doc, pos)` — „links“ / „rechts“, wenn das Bild an Position pos schwebt; sonst None (Bild steht in der Zeile).
- `bild_im_rahmen(rahmen)` — Das Bild, das in einem schwebenden Rahmen steht.
- `ist_anker(blk)`
- `schwebend_einfuegen(doc, blockpos, f, seite, versatz)` — Fügt das Bild f vor dem Absatz bei blockpos als schwebendes Bild ein (seite: „links“ \| „rechts“).
- `absatz_nach_rahmen(doc, bildpos)` — Der Absatz, zu dem das schwebende Bild bei bildpos gehört (er folgt dem Rahmen).
- `schwebend_entfernen(doc, pos)` — Nimmt das schwebende Bild bei pos samt Rahmen und Anker aus dem Dokument. Gibt die Stelle zurück, an der der Absatz
- `umbruch_setzen(ed, modus)` — Das markierte Bild: modus „zeile“ (mit Text in Zeile), „links“ oder „rechts“ (vom Text umflossen).

### `editor/seite/wasserzeichen.py`

Wasserzeichen einer Seite: Text oder Bild, mit Lage, Größe und Transparenz (Einfügen ▸ Wasserzeichen). Keine Oberfläche.

- `da(w)` — Ob das Wasserzeichen etwas zeigt (Text oder Bild).
- `bild_zu_text(img)`
- `bild_aus_text(text)`
- `ausgewaschen(img)` — „Auswaschen“ wie in Textverarbeitungen: hell und kontrastarm (85 % zum Weiß hin).
- `_deckkraft(w)`
- `_lage(w, r, b, h)` — Mittelpunkt des Wasserzeichens (Breite b, Höhe h) im Seitenrechteck r.
- `schrift(w, r)` — Schrift des Textwasserzeichens; „automatisch“ füllt die Seite (waagerecht 80 % der Breite, schräg 78 % der Diagonale).
- `zeichnen(p, w, r)` — Das Wasserzeichen ``w`` auf die Seite ``r`` (96-dpi-Bildpunkte) zeichnen: Lage, Größe und Deckkraft rechnet ``core/rendering/wasserzeichen.py``, gezeichnet wird über das Backend.

### `editor/seite/zeilennummern.py`

Zeilennummern (Seitenlayout ▸ Zeilennummern): welche Zeile welche Nummer trägt. Keine Oberfläche — Editor, Druck und PDF zeichnen damit.

- `unterdrueckt(block)`
- `nummern(doc, ch, art)` — (Absatz, Zeile, y im Textfluss, Nummer) für jede nummerierte Zeile; ``ch``: Höhe des Textbereichs einer Seite im Fluss.
- `zeichnen(p, d, n, ch, base, art)` — Zeilennummern am linken Rand der Seite n (Koordinaten: Textfläche, auf die Seite verschoben).

## `editor/tabelle`

### `editor/tabelle/__init__.py`

Unterpaket ``tabelle`` von ``core.editor``.


### `editor/tabelle/tabelle_text.py`

Text in Tabelle umwandeln und zurück (Einfügen ▸ Tabelle). Keine Oberfläche; jede Umwandlung ist ein Rückgängig-Schritt.

- `markierte_absaetze(ed)` — Die Absätze der Markierung (ganz, auch wenn die Markierung mitten im Absatz beginnt).
- `zellen(texte, trenner)` — Absätze in Zeilen und Zellen teilen. Bei „Absatzmarken“ wird jeder Absatz eine Zeile mit einer Zelle.
- `text_zu_tabelle(ed, trenner, spalten)`
- `_zelle_text(zelle, trenner, geschachtelt, bleiben)` — Text einer Zelle. Eine Tabelle darin wird mit umgewandelt (``geschachtelt``) oder als Kopie in ``bleiben`` gemerkt und
- `_tabelle_zeilen(t, trenner, geschachtelt, bleiben)`
- `tabelle_zu_text(ed, trenner, geschachtelt)` — Die Tabelle an der Schreibmarke zu Text. ``geschachtelt``: Tabellen in Zellen ebenfalls zu Text; sonst bleiben sie Tabellen

### `editor/tabelle/tabelleneigenschaften.py`

Eigenschaften einer Tabelle lesen und setzen (Fenster „Tabelleneigenschaften“). Keine Oberfläche; Maße in Millimetern.

- `lesen(t, c)`
- `anwenden(t, c, w)`
- `optionen_lesen(t)` — Formatoptionen dieser Tabelle: ``kopf`` (aus der Kopfzeilenzahl), ``streifen``, ``spalte``, ``vorlage`` (Name oder ``""``) und
- `optionen_setzen(t, *, kopf, streifen, spalte, vorlage)` — Formatoptionen an der Tabelle merken (nur die übergebenen); ``kopf`` setzt die Kopfzeilenzahl (0/1).
- `_loesch_bereich(t, c, z)` — (erste Zeile, Zeilenzahl, erste Spalte, Spaltenzahl) der markierten Zellen, sonst der einen Zelle.
- `_zeile_spalte_loeschen(t, c, art, r0, nr, s0, ns)`
- `_zellen_verschieben(t, c, waagrecht, linien, start, laenge, schritt)` — Inhalt der Zellen ab ``start`` um ``schritt`` nach vorn kopieren, die letzten Zellen leeren (ein Rückgängig-Schritt).
- `zellen_loeschen(t, c, art)` — „Zellen löschen“ für die Zelle bzw. die markierten Zellen: ``art`` = ``zeile``, ``spalte``, ``links`` (Zellen rechts davon rücken
- `_verbundene_teilen(t, z, spalten, zeilen)` — Eine verbundene Zelle innerhalb ihrer Spannweite in ``spalten`` x ``zeilen`` Stücke teilen. ``QTextTable.splitCell`` verkleinert nur
- `_spalten_dazu(t, zr, zc, spalten)` — Hinter der Spalte ``zc`` neue Spalten einfügen; alle anderen Zellen, die in dieser Spalte enden (auch von links herüberreichende
- `_zeilen_dazu(t, zr, zc, spalten, zeilen)` — Unter der Zeile ``zr`` neue Zeilen einfügen; alle Zellen außer den geteilten, die in dieser Zeile enden (auch von oben herabreichende
- `zelle_teilen(t, c, spalten, zeilen)` — Teilt die Zelle unter dem Cursor c in spalten x zeilen Zellen (wie „Zellen teilen“).
- `zeilenhoehe_setzen(t, r, px, zeile_px)` — Mindesthöhe ``px`` der Tabellenzeile ``r`` setzen: Zellformat-Eigenschaft ``Z_MINHOEHE`` plus Innenabstand oben/unten
- `zeilenhoehe_lesen(t, r)` — Mindesthöhe der Zeile in Bildpunkten; 0, wenn keine gesetzt ist.
- `an_inhalt_anpassen(t, c)` — Jede Spalte so schmal wie ihr breitester Zellentext (+ 2x Innenabstand + Rand); Tabellenbreite variabel. Ein Rückgängig-Schritt.
- `_zoom(t)` — Ansichtsfaktor des Layouts (Zeichengerät 96 dpi x Zoom): Layoutmaße / Faktor = Dokumentmaße.
- `_zellen_der_zeile(t, r)` — Zellen, die in Zeile ``r`` beginnen und nur eine Zeile hoch sind.
- `_textHoehe(t, r)` — Höhe des höchsten Zelleninhalts der Zeile (ohne Innenabstand), aus dem Layout.
- `_zeilen_oberkanten(t)` — y der Oberkante jeder Zeile (Dokumentkoordinaten), gemessen an Zelleninhalt minus oberem Innenabstand.
- `_unterkante(t)` — Layout-y der Unterkante der Tabelle: Ende des Inhalts der letzten Zeile plus unterer Innenabstand.
- `tabelle_basis(t)` — (Spaltenbreiten, Zeilenhöhen) der Tabelle in Bildpunkten des Dokuments (zoomunabhängig): Breiten aus festen
- `zeilengrenzen(t)` — y der inneren waagrechten Zeilenränder (n-1 Stück) in Layoutkoordinaten des Dokuments (wie ``_grenzen`` der Spalten,
- `zeilen_mindesthoehe(t, r)` — Kleinste zulässige Höhe der Zeile: Inhalt plus Innenabstand oben und unten.
- `_zeile_setzen(t, r, px)`
- `zeile_hoehe_ziehen(t, zeile, neue_hoehe_px)` — Mindesthöhe nur der Zeile ``zeile`` auf ``neue_hoehe_px`` setzen (nie unter dem Inhalt). Der Aufrufer öffnet den
- `_zeilen_setzen(t, ziele)` — Mindesthöhen mehrerer Zeilen setzen. Die Textmaße aller Zeilen werden zuerst gemessen (ein Layoutlauf); danach
- `_zellen_der_zeile_alle(t, r)` — Erste in Zeile ``r`` beginnende Zelle (Stellvertreter für den Ist-Zustand der Zeile).
- `skalierungs_kosten(t)` — Aufwand eines Skalierungsschritts: Anzahl der Zellen. Der Aufrufer kann bei großen Tabellen auf einen Vorschaurahmen wechseln.
- `tabelle_skalieren_spalten(t, basis_breiten, faktor_b)` — Nur die Spaltenbreiten = Basis x ``faktor_b`` (mind. ``MIN_SPALTE``, Tabellenbreite variabel); die Zeilenhöhen
- `tabelle_skalieren_zeilen(t, basis_hoehen, faktor_h)` — Nur die Zeilenhöhen = Basis x ``faktor_h`` (mind. Inhalt); unveränderte Zeilen bleiben unberührt.
- `tabelle_skalieren(t, basis_breiten, basis_hoehen, faktor_b, faktor_h)` — Spaltenbreiten = Basis x ``faktor_b`` (feste Längen, mind. ``MIN_SPALTE``, Tabellenbreite variabel), Zeilenhöhen =
- `spalten_gleich(t)` — Alle Spalten gleich breit bei unveränderter Gesamtbreite (Prozentbreite bleibt Prozentbreite). Ein Rückgängig-Schritt.
- `zeilen_gleich(t)` — Alle Zeilen auf die Höhe der höchsten Zeile bringen (aufrunden). Ein Rückgängig-Schritt je Aufruf über den Aufrufer.
- `spalten_festschreiben(t)` — Aktuelle Spaltenbreiten als feste Längen festschreiben; Tabellenbreite variabel.
- `linie_loeschen(t, zeile, spalte, seite)` — Löscht die Linie auf der Seite (links/rechts/oben/unten) der Zelle: verbindet die Zelle mit dem Nachbarn dahinter.

### `editor/tabelle/tabellenstil.py`

Tabellenformatvorlagen und Formatoptionen (Kopfzeile, gebänderte Zeilen, erste Spalte).

- `_zellen(t)`
- `_fett(cell, an, farbe)`
- `_zeilengrund(r, kopf, kopf_fill, streifen_fill)` — Hintergrundfarbe der Zeile ``r``: Kopfzeile, jede zweite Zeile darunter als Streifen, sonst keine (leer).
- `anwenden(t, name, kopf, streifen, spalte)`

### `editor/tabelle/tabellenzustand.py`

Der Zustand der Schreibmarke gegenüber einer Tabelle - an einer Stelle festgelegt (keine Oberfläche).

- `zustand(editor)`
- `tabellenmodus(editor, rechtsklick, per_griff)` — ``True``, wenn Tabellenfunktionen (Einfügen/Löschen, Rahmen, Schattierung …) angeboten werden.

## `editor/text`

### `editor/text/__init__.py`

Unterpaket ``text`` von ``core.editor``.


### `editor/text/designs.py`

Designs des Reiters Seitenlayout: Farbschemen, Schriftpaare, Effekte und die Designs, die alles drei bündeln. Keine Oberfläche.

- `ueberschrift_farbe(schema)` — Die Farbe der Überschriften eines Farbschemas: Akzent 1.
- `design(name)` — Was ein Design setzt: {"kopf", "text", "farbe", "farben"} (Schriften, Überschriftfarbe, das ganze Farbschema).

### `editor/text/fragmente.py`

Die Textstücke (``QTextFragment``) eines Absatzes oder des ganzen Dokuments der Reihe nach — die eine Stelle für diese Schleife.

- `absatz_fragmente(b)`
- `dokument_fragmente(doc)`

### `editor/text/ki_markdown.py`

KI-Antworten als Markdown: die eine Stelle, die Chat-Anzeige, Vorschau und Übernahme ins Dokument gemeinsam nutzen.

- `normalisieren(text)` — Einheitliche Vorbereitung: einzelne Zeilenumbrüche werden harte Umbrüche (außer vor Listen, Tabellen, Überschriften, Codeblöcken);
- `dokument(text)` — Der Text als gelesenes Dokument (mit Überschriftsebenen, Listen, Tabellen und Zeichenformaten).
- `_zeichen_besonders(f)`
- `hat_struktur(text)` — Wahr, wenn der Text Überschriften, Listen, Tabellen oder Hervorhebungen enthält. Sonst bleibt er einfacher Text (auch ohne Markdown-Deutung).
- `_tabellen(d)`
- `klartext(text)` — Der sichtbare Text ohne Markdown-Zeichen (z. B. für Zähler und Vergleiche).
- **class `_Zustand`**
  - `__init__()`
- `_basis_zeichen(f)` — Zeichenformat der Stelle ohne Hervorhebungen: Schrift, Größe, Farbe bleiben, Fett/Kursiv/Link kommen aus dem Text.
- `_inline(c, quelle, basis, ueberschrift)` — Text eines gelesenen Absatzes mit Fett, Kursiv, Durchgestrichen, Code und Links einfügen (die Überschrift bringt ihre Vorlage selbst mit).
- `_aus_liste(c)`
- `_fliesstext_format(basis)`
- `_block_bereit(c, st, bf, cf, mitte_ok)` — Der nächste Absatz: der erste darf den Absatz der Schreibmarke weiterbenutzen (leer, oder bei Fließtext auch mitten im Satz).
- `_listenart(quelle_liste)` — (Stil im Ziel, Ebene, Start) aus der gelesenen Liste.
- `_liste_zuordnen(c, st, quelle_liste)`
- `_tabelle(editor, c, st, quelle, bf, cf)` — Native Tabelle über ``editor.insert_table``; die Zellen bekommen den Text samt Hervorhebungen. → Schreibmarke hinter der Tabelle.
- `einfuegen(editor, cursor, text)` — Markdown-Text an ``cursor`` einfügen — Überschriften als Formatvorlagen, Listen als echte Listen, Tabellen als Tabellen,

### `editor/text/listen.py`

Aufzählungen und Nummerierungen: die Arten, die Lunivo zeichnet und in DOCX schreibt, und ihre Beschreibung als kleines Wörterbuch.

- `zeichen_filtern(w)` — Aus den Werten eines Schriftart-Fensters nur das, was für Nummern gilt und gesetzt ist.
- `liste(stil, praefix, suffix, start, zeichen, pos)` — ``pos``: eigene Position der Nummer (``ausr``, ``ausr_art``, ``tab``, ``einzug`` in mm) — dann zeichnet Lunivo die Nummer selbst.
- `marke(spec)` — Zeichenfolge für ``liste_zeichner`` (Vorschaubild) dieser Liste.
- `zu_format(spec, einzug)`
- `aus_format(f)`
- `als_text(spec)`
- `aus_text(text)`

### `editor/text/mehrstufig.py`

Mehrstufige Nummerierung („Gliederung nummeriert“: 1. / 1.1. / 1.1.1.), von Lunivo selbst gezeichnet.

- `nummer_text(stil, n)` — Die Zahl ``n`` in der Zahlenart ``stil`` (dezimal, klein, gross, roem_klein, roem_gross).
- `ebene(stil, format, start, ausr, einzug, zeichen, **mehr)`
- `ebene_aus(x)` — Eine Ebene aus einem Wörterbuch (JSON, Dialog) mit allen bekannten Feldern neu aufbauen.
- `aufzaehlung(zeichen)` — Aufzählung mit einem Zeichen (◆ ✤ ➤ ✓ ✧ …), das Lunivo selbst zeichnet; Ebenen wie bei einer Gliederung eingerückt.
- `ist_aufzaehlung(defn)` — Gliederung ohne einen einzigen Platzhalter für Nummern: eine Aufzählung mit eigenem Zeichen.
- `als_mehrstufig(spec)` — Eine einfache Liste (``editor.text.listen``) mit eigener Position als Gliederung: Ebene 1 ist die Liste, tiefere Ebenen zählen für sich.
- `gliederung(stile, formate)` — 9 Ebenen aus je einer Zahlenart und einem Zahlenformat; Ausrichtung und Einzug wachsen mit der Ebene.
- `_alle(zahlenart, formate)` — Ebene n zeigt die Nummern aller Ebenen davor (``①.②.``); ``formate`` bestimmt, ob Ebene 1, 2 und tiefer mit Punkt enden (``"."``) oder nicht (``""``).
- `als_text(defn)`
- `aus_text(text)`
- `block_wert(ebene_nr, defn)`
- `aus_block(text)`
- `nummer_der_ebene(defn, zaehler, ebene_nr)` — Die Nummer als Text für einen Absatz der Ebene ``ebene_nr`` (1…9) bei diesen Zählerständen.
- `zaehlen(zaehler, defn, ebene_nr)` — Zählerstand nach einem Absatz der Ebene ``ebene_nr``: diese Ebene weiter, tiefere neu.
- `nummern(d)` — [(Block, Nummerntext, Ebene, Beschreibung der Ebene)] aller Absätze mit ``B_MEHRSTUFIG`` in Dokumentreihenfolge.
- `_nummern_bauen(d)`
- `_marker_font(b, e)` — Schrift und Farbe der Nummer: die des Absatzes, mit den Änderungen der Ebene („Schriftart …“).
- `_text_breite(text, f, geraet)`
- `einrichten_alle(d)` — Einzug aller Absätze mehrstufiger Listen setzen: Text ab „Einzug bei“, erste Zeile ab „Tabstopp-Leerstelle“ — oder direkt nach der
- `nummern_zeichnen(p, d, faktor)` — Die Nummern der mehrstufigen Listen vor die Absätze zeichnen. Koordinaten: Dokument (wie ``absatzrahmen_zeichnen``).

### `editor/text/muster.py`

Schattierungsmuster (Rahmen und Schattierung ▸ Muster): Prozentraster und Linienmuster.

- `_pct_name(p)`
- `name_von(schluessel)`
- `ooxml_von(schluessel)`
- `schluessel_von_ooxml(wert)`
- `_an(schluessel, x, y)` — Ist das Bildelement (x, y) der 8 × 8-Kachel in der Musterfarbe?
- `kachel(schluessel, muster, fuell)` — Eine 8 × 8-Kachel des Musters; ohne Füllfarbe bleibt der Grund durchsichtig.
- `pinsel(schluessel, muster, fuell)` — Der Pinsel für den Hintergrund eines Absatzes (Muster über Füllfarbe).
- `als_text(schluessel, muster, fuell)`
- `aus_text(text)`

### `editor/text/schreibweise.py`

Groß-/Kleinschreibung und Sortierreihenfolge als reine Textfunktionen (ohne Oberfläche, einzeln testbar).

- `umwandeln(text, art)`
- `_zahl(t)` — Die erste Zahl im Text (Komma oder Punkt als Dezimalzeichen); ohne Zahl ganz vorn.
- `_datum(t)`
- `sortiert(texte, *, absteigend, typ, gross_klein)` — Die Texte in der gewünschten Reihenfolge. ``typ``: ``text``, ``zahl`` (erste Zahl im Text) oder ``datum`` (TT.MM.JJJJ).
- `felder(text, trenner)` — Die Felder eines Absatzes (getrennt durch Tab, Komma oder ein anderes Zeichen).
- `feldzahl(texte, trenner)`
- `reihenfolge(texte, schluessel, *, trenner, gross_klein, sprache, kopfzeile)` — Neue Reihenfolge der Absätze (Indizes). ``schluessel``: bis zu drei (Feld oder None für den ganzen Absatz, Typ, absteigend) — der erste
- `absaetze(doc, von, bis)` — Die Absätze zwischen ``von`` und ``bis`` (ohne Angabe: das ganze Dokument). → [] wenn eine Tabelle dazwischenliegt.
- `umstellen(doc, bloecke, ordnung)` — Stellt die (aufeinanderfolgenden) Absätze ``bloecke`` in die Reihenfolge ``ordnung`` — mit Absatz- und Zeichenformat, als ein Rückgängig-Schritt.

### `editor/text/silbenfarben.py`

Silben farbig: Lesehilfe für Menschen mit Legasthenie.

- `konfig_lesen(settings)` — Die Einstellungen (settings: Settings des Programms) als Wörterbuch mit allen Schlüsseln.
- `konfig_speichern(settings, k)`
- `farben(k)`
- `verfuegbar(sprache)` — Die Regeln brauchen nichts außer Python; pyphen verbessert nur die Wortgrenzen in Zusammensetzungen.
- `silben(wort, sprache)` — Das Wort in deutsche Sprechsilben (ein Eintrag, wenn es sich nicht teilen lässt).
- `_formate(k)`
- **class `SilbenFarben`**(QSyntaxHighlighter) — Färbt die Silben im Anzeige-Layout des Dokuments ein; verändert weder Text noch Formatierung.
  - `__init__(doc, konfig, aktueller_block)`
  - `highlightBlock(text)`
  - `neu_konfigurieren(konfig)`

### `editor/text/statistik.py`

Wörter zählen wie das Fenster der Vorlage: Seiten, Wörter, Zeichen mit und ohne Leerzeichen, Absätze, nicht-asiatische Wörter,

- `texte_des_dokuments(doc)`
- `zaehlen(texte, seiten)` — ``texte``: ein Eintrag je Absatz (auch Noten und Textfelder, wenn sie mitzählen sollen).

### `editor/text/stile.py`

Formatvorlagen des Katalogs (Start ▸ Stile) — Vorgaben und eigene Änderungen (Start ▸ Stile ▸ ↘ Formatvorlagen verwalten).

- `namen()`
- `ist_eigen(name)`
- `laden_neu(text)`
- `_meta(x)` — „basiert auf“, „folgender Absatz“ und die Abweichungen von der Basis (nur bei Vorlagen mit Basis).
- `als_json_neu()`
- `pruefe_name(name)` — Darf eine neue Vorlage so heißen? → None, sonst der Grund.
- `anlegen(name, *, basis, folge, **felder)` — Neue Vorlage anlegen. → None bei Erfolg, sonst der Grund (Name leer oder schon vergeben).
- `loeschen(name)`
- `laden(text)`
- `als_json()`
- `definition(name, _tiefe)`
- `aendern(name, **felder)`
- `zuruecksetzen(name)`
- `name_zu_key(name)`
- `key_zu_name(key)`

### `editor/text/tabfuell.py`

Füllzeichen vor Tabstopps (Punkte, Striche, Linie): Qt kennt sie nicht, Lunivo zeichnet sie selbst.

- `lesen(bf)` — Position (px) → Füllzeichen-Schlüssel eines Absatzformats.
- `setzen(bf, fuell)`
- `aus_docx(wert)`
- `_tabstrecken(b, bf)` — (Zeile, x0, x1, Füllzeichen) jedes Tabzeichens des Absatzes, dessen Tabstopp ein Füllzeichen hat. x in Koordinaten der Zeile.
- `_strecke_fuellen(p, fm, zeichen, x0, x1, y)` — Die Strecke x0…x1 auf der Grundlinie ``y`` füllen: durchgehende Linie oder Zeichen mit festem Abstand, rechtsbündig ans Tabziel.
- `_absatz_zeichnen(p, b, bf)`
- `zeichnen(p, d)` — Füllzeichen in die Tabstrecken der Absätze zeichnen. Koordinaten: Dokument.
- `_absaetze_mit_fuellung(d)`

### `editor/text/textdaten.py`

Formatierten Text als einfache Daten (Absätze aus Textstücken) ablegen und wieder einfügen — für Textbausteine und Ähnliches.

- `_stueck(f)`
- `fragment_zu_daten(fragment)`
- `daten_zu_fragment(absaetze)`

### `editor/text/texteffekt.py`

Texteffekte, die Lunivo zeichnet: Füllung des Textes (Farbe, Transparenz) und Kontur (Farbe, Breite, Linienart).

- `strich_setzen(pen, art)` — Strichart (Muster oder Qt-Stil) in einen Stift schreiben.
- `zu_format(w)` — Zeichenformat, das den Effekt zeichnet (zum Anwenden im Editor und für Vorschauen).
- `_fuellart_ableiten(w)` — Füllart und Kontur aus den gelesenen Effekten ableiten: ein Verlauf, ein Muster oder Bild als Füllung; eine Kontur mit Verlauf oder Form.
- `_kontur_aus_stift(p, w)` — Farbe, Breite (pt) und Strichart der Textkontur aus dem Stift des Zeichenformats.
- `aus_format(cf)`
- `als_text(w)` — Nur Transparenz und Kontur; ``""`` wenn weder noch.
- `aus_text(text, farbe)`
- `_q(name)`
- `_farbelement(eltern, hexwert, alpha_pct)`
- `_verlauf_element(eltern, v)`
- `_rpr_leuchten(rpr, g)`
- `_rpr_schatten(rpr, s)`
- `_rpr_reflektion(rpr, r)`
- `_rpr_kontur(rpr, w)`
- `_rpr_fuellung(rpr, w)` — Textfüllung: keine, Verlauf oder (bei Transparenz) einfarbig mit Deckkraft.
- `_rpr_3d(rpr, d)`
- `in_rpr(rpr, cf)` — Texteffekte des Zeichenformats als w14-Elemente an ``w:rPr`` schreiben, in der Reihenfolge des Schemas (nichts, wenn es keinen Effekt gibt).
- `_wert(e, name, vorgabe)`
- `_farbe_aus(e)` — (Farbe, Transparenz in %) eines Elements mit w14:srgbClr darunter.
- `_verlauf_aus(g)`
- `_kontur_aus(rpr, w)`
- `_fuellung_aus(rpr, w)`
- `_leuchten_schatten_aus(rpr, w)`
- `_reflektion_3d_aus(rpr, w)`
- `aus_rpr(rpr, cf)` — Das Gegenstück zu ``in_rpr``: die w14-Elemente von ``w:rPr`` ins Zeichenformat lesen.

### `editor/text/textfx.py`

Texteffekte, die Qt am Text nicht kennt und die Lunivo über den Umrissen der Buchstaben selbst zeichnet: Farbverlauf in Füllung und Kontur,

- `_farbe(hexwert, transparenz)`
- `hat_effekt(fx)`
- `als_text(fx)` — Nur die Teile, die Lunivo selbst zeichnet, als JSON für das Zeichenformat (leer = keiner).
- `aus_text(text)`
- `_verlauf(rect, v)`
- `fuell_pinsel_von(d, rect)` — Der Pinsel zu ``fuell_pinsel`` (Muster, Textur, Bild); ``rect``: Fläche, über die ein Bild gestreckt wird.
- `_warp_y(art, x, y, u, hoehe, mitte_y)` — Die Höhe eines Punktes nach der Textverformung ``art`` (``u``: Lage 0..1 in der Breite des Pfades).
- `_drehen_3d(x, y, m, rx, ry, rz, dist)` — Ein Punkt nach der Drehung um Z, X, Y (Bogenmaß) um die Mitte ``m`` mit Perspektive (``dist``: Augenabstand, 0 = keine).
- `_augenabstand(d3, breite, hoehe)` — Abstand des Auges für die Perspektive (0 = ohne) aus dem Blickwinkel ``perspektive``.
- `_polygon_verformen(poly, art, r, m, drehung, dist)` — Die Punkte eines feinen Linienzugs (in vierfacher Größe) nach Verformung und 3D-Drehung.
- `pfad_verformen(pfad, fx)` — Der Textpfad nach ``warp`` (Transformieren) und ``text_3d`` (3D-Drehung um X, Y, Z mit Perspektive); ohne beides unverändert.
- `_weich(p, pfad, farbe, radius)` — Pfad mit weichem Rand: gefüllt, dazu Striche in wachsender Breite und sinkender Deckkraft.
- `_richtung(winkel)`
- `_helligkeit(c, f)`
- `_normale(a, q, b)` — Die Einheitsnormale am Eckpunkt ``q`` zwischen Vorgänger ``a`` und Nachfolger ``b`` (fehlende Nachbarn zählen nicht).
- `_linienzug_versetzt(pts, zu, abstand)` — Die Eckpunkte eines Linienzugs entlang ihrer Normalen um ``abstand`` verschoben (``zu``: geschlossen).
- `_versetzt(pfad, abstand)` — Der Pfad seitlich um ``abstand`` verschoben (Eckpunkte entlang ihrer Normalen, mit begrenzter Spitze); für Linien und geschlossene Formen.
- `_kontur_pfade(pfad, breite, form, art)` — Die Flächen einer Konturlinie: einfach ein Strich, doppelt zwei Streifen mit Lücke, dick–dünn/dünn–dick zwei ungleiche, dreifach drei Streifen.
- `_basisname(basis_farbe)`
- `_fx_reflektion(p, pfad, aussen, r, grundlinie, schrift_px, basis_farbe)` — Spiegelung unter der Grundlinie, nur außerhalb der Buchstaben.
- `_tiefe_faktor(mat, licht, t)` — Helligkeitsfaktor einer Tiefenschicht ``t`` (0..1) nach Material und Beleuchtung.
- `_tiefe_farbe(basis, f, licht)`
- `_fx_3d(p, pfad, aussen, d3)` — 3D-Format: Tiefenschichten hinter dem Text, optional mit Kontur.
- `_fx_schatten_aussen(p, pfad, aussen, s, rect, grundlinie)` — Schatten hinter dem Text (``aussen`` oder ``persp``).
- `_fx_leuchten(p, pfad, aussen, g)`
- `_fx_fuellung(p, pfad, fx, rect)` — Verlauf- und Pinselfüllung (Muster, Textur, Bild) über den Buchstaben.
- `_fx_schatten_innen(p, pfad, s, rect)`
- `_fx_kontur(p, pfad, fx, rect, kontur)` — Konturlinie (einfach/mehrfach, Farbe oder Verlauf), wenn sie Lunivo zeichnet.
- `fx_zeichnen(p, pfad, fx, grundlinie, schrift_px, basis_farbe, kontur)` — Die Effekte zu einem Textstück zeichnen. ``pfad``: Umrisse in Zeichenkoordinaten, ``grundlinie``: y der Schriftlinie, ``schrift_px``: Schriftgröße.
- `_fx_hinter(p, pfad, aussen, fx, rect, grundlinie, schrift_px, basis_farbe)` — Die Effekte hinter dem Text: Spiegelung, 3D-Tiefe, Schatten außen, Leuchten.
- `_fx_ueber(p, pfad, fx, rect, kontur)` — Die Effekte über dem Text: Füllung, Schatten innen, Kontur.
- `text_pfad(text, font, ursprung)` — Umrisse eines Textes (für Vorschauen); → (Pfad, y der Grundlinie).
- `vorschau_zeichnen(p, rect, text, font, fx, farbe, kontur)` — Text mit Effekt zentriert in ein Rechteck zeichnen (Kacheln und Vorschau der Fenster); der Text selbst wird hier mitgezeichnet.

### `editor/text/textfx_vorgaben.py`

Voreinstellungen und Kachelbilder der Texteffekt-Auswahlen (Schatten, Spiegelung, Leuchten, WordArt) — gezeichnet mit ``textfx.vorschau_zeichnen``.

- `schatten_vorgaben()` — [(Abschnitt, Name, Schatten)] — Außen, Innen (je 9) und Perspektive (5).
- `reflektion_vorgaben()` — 9 Spiegelungen: drei Größen (eng, halb, voll) mal drei Abstände.
- `leuchten_vorgaben()` — 24 Leuchtvarianten: sechs Farben mal vier Größen.
- `voreinstellung_icon(fx, groesse, text, farbe, kontur)` — Kachelbild einer Voreinstellung: ein „A“ mit dem Effekt auf weißem Grund (``kontur``: (Farbe, Breite, Form) wie bei ``vorschau_zeichnen``).
- `text_kachel_icon(fx, groesse)` — Kachelbild der Effektmenüs im Text (Schatten, Spiegelung, Leuchten): ein hellblaues „A“ mit blauem Rand, plastisch, wie in der Vorlage.
- `form_kachel_icon(fx, groesse)` — Kachelbild des Schattenmenüs eines Objekts: ein abgerundetes Rechteck mit weichem Verlauf (hellblau, blauer Rand) und dem Effekt auf weißem Grund.
- `wordart_vorgaben()` — Die 15 Formatvorlagen im Menü „Texteffekte ▸ WordArt“: Füllung, Kontur, Schatten (vollständige Effekte, ersetzen die bisherigen).
- `wordart_icon(w, groesse)` — Kachelbild einer WordArt-Formatvorlage.

### `editor/text/textfx_zeichen.py`

Was Lunivo am Text selbst zeichnet, das Qt nicht kann und das nicht zu den Effekten von ``textfx`` gehört: Unterstreichungsarten,

- `_woerter(text)` — Die Wörter eines Textes als (Anfang, Ende); Leerzeichen bleiben frei („Nur Wörter“).
- `_unterstrich(p, strecken, art, grundlinie, groesse, farbe)` — Unterstreichungen, die Qt nicht kennt: doppelt, dick, lang gestrichelt, Wellen in zwei Stärken, nur Wörter.
- `unter_zeichnen(p, x0, y, x1, art, farbe, groesse)` — Eine Unterstreichungsart als Linie von ``x0`` bis ``x1`` in Höhe ``y`` (für Auswahllisten wie das Menü am Knopf „Unterstrichen“).
- `unter_symbol(art, groesse, farbe)` — Bildchen einer Unterstreichungsart für Auswahllisten (dieselbe Zeichnung wie im Text).
- `_doppelt_durch(p, rect, grundlinie, groesse, farbe)` — Die zweite Durchstreichlinie (die erste zeichnet Qt): zwei Linien in Höhe der Kleinbuchstaben.
- `_betonung(p, glyphen, art, grundlinie, groesse, farbe)` — Betonungszeichen: ein Punkt, Kreis oder Komma über (oder ein Punkt unter) jedem Buchstaben.
- `absaetze_zeichnen(p, d)` — Die Effekte aller Textstücke des Dokuments zeichnen (Textstücke mit ``P_EFFEKT``). Koordinaten: Dokument.
- `_absaetze_mit_effekt(d)` — Die Absätze, in denen mindestens ein Textstück etwas hat, das Lunivo selbst zeichnet.
- `_P(name)`
- `hat_zeichen_effekt(cf)` — Hat dieses Zeichenformat etwas, das Lunivo selbst zeichnet: Effekte, doppelt durchgestrichen oder Betonungszeichen?
- `_glyphlauf(z, a, e)` — (Glyphenpfad, Position) aller Glyphen der Zeile ``z`` von ``a`` bis ``e``.
- `_zeilenpfad(z, a, e, ursprung)` — Umrisse der Zeichen ``a``..``e`` der Zeile (in Dokumentkoordinaten) und je Buchstabe (Mitte, Ober-, Unterkante) für Betonungszeichen.
- `_textfarbe(cf)`
- `_kontur_von(fx)` — Die Kontur, die Lunivo selbst zeichnet (aus den Konturteilen des Effekts), sonst ``None``.
- `_unter_zeichnen_stueck(p, b, tl, z, a, e, cf, art, grundlinie, groesse, farbe)`
- `_zusaetze_zeichnen(p, tl, z, a, e, ursprung, cf, glyphen, grundlinie, groesse, farbe)` — Betonungszeichen, umschlossene Zeichen und Ruby einer Zeilenstrecke.
- `_zeile_zeichnen(p, b, tl, z, a, e, cf, fx)`
- `_stueck(p, b, tl, von, laenge, cf, fx)` — Ein Textstück (Zeichenformat ``cf``) zeilenweise mit Effekten und Zeichenzusätzen zeichnen.
- `_umschlossen(p, kasten, wie, farbe, groesse)` — Die Form um die Zeichen: „reduzieren“ legt sie eng an, „erweitern“ lässt dem Symbol Raum.
- `_ruby(p, x0, x1, grundlinie, groesse, ruby, farbe)` — Der Leittext über dem Basistext, in kleinerer Schrift, nach der gewählten Ausrichtung.

### `editor/text/textur.py`

Kleine, selbst gezeichnete Texturen für Vorschau und Füllung. Ohne Oberfläche.

- `textur(name, groesse)` — Eine kleine, selbst gezeichnete Textur (Vorschau und Füllung): ``papier``, ``granit``, ``holz``, ``stoff``, ``marmor``, ``sand``.

### `editor/text/unterstreichung.py`

Unterstreichungsarten als Zeichenformat: was Qt selbst zeichnet und was Lunivo zeichnet (``P_UNTER``). Ohne Oberfläche.

- `unter_format(art)` — Nur die Unterstreichung als Zeichenformat (zum Zusammenführen, ohne anderes anzufassen).

### `editor/text/wortextras.py`

Wort-Extras: Absätze aufräumen — über die Markierung, ohne Markierung über das ganze Dokument. Jede Handlung ist ein Schritt für Rückgängig.

- `_bloecke(ed, s)` — Die Absätze der Markierung (ohne Markierung: alle) außerhalb von Tabellen, in Dokumentreihenfolge.
- `_leer(a)` — Ein Absatz ohne Zeichen und ohne Bild.
- `_nachbar(s, a, schritt)` — Der Absatz davor oder dahinter im selben Textfluss (``None``, wenn dort keiner steht).
- `_schritt(ed, arbeit)` — Führt ``arbeit(sitzung, absaetze)`` als einen Rückgängig-Schritt aus. → Zahl der Änderungen.
- `_auswahl(a, von, bis)`
- `leere_loeschen(ed)`
- `leere_einfuegen(ed)`
- `zeilenumbruch_in_return(ed)`
- `absaetze_neu_anordnen(ed)` — Absätze, die mitten im Satz enden (hartes Return in einem Satz, etwa aus PDF-Text), werden zu einem Absatz.
- `leerzeichen_bereinigen(ed)` — Doppelte Leerzeichen und Leerzeichen am Anfang und Ende der Absätze entfernen.
- `_punkte(s, a)`
- `einzug_zwei_zeichen(ed)` — Erstzeileneinzug um zwei Zeichen der Schriftgröße des Absatzes.
- `smart_anordnen(ed)` — Leerzeichen bereinigen, leere Absätze löschen, Erstzeileneinzug um zwei Zeichen (zusammen ein Schritt für Rückgängig).
- `fuehrende_leerzeichen_loeschen(ed)` — Leerzeichen und Tabs am Anfang der Absätze entfernen.
- `zeilenumbrueche_loeschen(ed)` — Manuelle Zeilenumbrüche (Umschalt+Enter) entfernen; die Zeilen laufen zusammen, zwischen zwei Wörtern bleibt ein Leerzeichen.
- `leerabsatz_modus_wechseln(ed)` — Trennung durch leere Absätze umschalten: Stehen zwischen den Absätzen leere Absätze, verschwinden sie; sonst kommt zwischen
- `einzug_in_leerzeichen(ed)` — Den Erstzeileneinzug eines Absatzes in Leerzeichen am Absatzanfang umwandeln (gleich breit), der Einzug selbst wird 0.

### `editor/text/zahlformat.py`

Zahlen in anderer Schreibweise (Einfügen ▸ Zahl): 1,2,3 · A,B,C · I,II,III · eingekreist · Zahlwort. Keine Oberfläche.

- `_buchstaben(n)` — 1 → A, 26 → Z, 27 → AA .
- `_unter_tausend(n)`
- `zahlwort(n)` — Deutsches Zahlwort bis 999 999 („einundzwanzig“, „eintausend“).
- `grenzen(typ)` — Kleinste und größte Zahl, die der Typ darstellen kann.
- `zahl_text(n, typ)` — Die Zahl im gewählten Typ; liegt sie außerhalb der Grenzen, ``ValueError``.

### `editor/text/zeichenzusatz.py`

Zeichenzusätze der Gruppe „Schriftart“ ▸ Groß-/Kleinschreibung: Eingeschlossene Zeichen und Phonetisches Leitzeichen.

- `umschlossen_text(form, vorlage)`
- `umschlossen_lesen(text)`
- `ruby_text(ruby, ausrichtung, abstand, groesse)`
- `ruby_lesen(text)`

## `kern`

### `kern/__init__.py`

Anwendungskern: Befehle (commands), Pfade — ohne Oberflächenlogik.


### `kern/anwendung.py`

Anwendungsstart: QApplication einrichten, Einstellungen und Theme laden, Hauptfenster zeigen, sauber beenden.

- `programm_symbol()` — Lunivos Programmsymbol (ressourcen/symbole/varianten/Abstrakt) in allen vorhandenen Größen.
- **class `LunivoApplication`**
  - `__init__(argv)`
  - `start()`
  - `_abbauen()` — Fenster vor dem Interpreter-Ende abbauen: PySide räumt sonst in falscher Reihenfolge ab (Heap-Fehler beim Beenden).

### `kern/befehlsliste.py`

Befehle des Bandes: Aktionsname aus register.json → Funktion.

- **class `Befehle`**(AnsichtBefehle, BearbeitenBefehle, BildToolsBefehle, DateiBefehle, DiagrammToolsBefehle, EinfuegenBefehle, FormToolsBefehle, KIBefehle, KommentarBefehle, KopfFussBefehle, KontextBefehle, PruefenBefehle, SeiteBefehle, SerienBefehle, SmartArtKnotenZustand, SmartArtToolsBefehle, TextBefehle, TextToolsBefehle, UeberpruefenBefehle, VerweiseBefehle) — Alle Befehle des Bandes. Die Grundfunktionen (Aktion suchen, ausführen, Zustand) stehen hier, die Befehle selbst in ``kern/befehle/*``.
  - `__init__(win)`
  - `ed()`
  - `_teile(name)` — 'w.setzePapier:["a4"]' → ('w_setzePapier', ['a4'])
  - `hat(name)`
  - `tun(name, knopf)`
  - `zustand(name)`
  - `kann(name)` — Ob der Befehl gerade geht (Befehl ``kann_<name>``); ``None``: keine eigene Bedingung.
  - `band_feld(name)` — Ein Eingabefeld fürs Band (Befehl ``feld_<name>``), z. B. die Nummer des Datensatzes im Seriendruck.
  - `symbolname(name)` — Symbol, das ein Knopf nach seiner letzten Wahl zeigt (Befehl ``symbolname_<name>``); ``None``: der Knopf behält seins.
  - `haken_wert(item)` — Haken eines Menüpunkts: Zustandsfrage des Menüeintrags (z. B. w.randVorgabeJetzt) gegen sein Argument.
  - `klappe(name)`
  - `_popup(menue)` — Menü an der Mausposition zeigen (eigene Stelle, damit Tests es abfangen können).
  - `fehlende(namen)`
  - `_fmt()`

### `kern/dokument_verwaltung.py`

Dokumentverwaltung ohne Oberfläche: Laden, Speichern, automatische Sicherung, Wiederherstellung, zuletzt benutzte Dateien.

- **class `DocumentManager`**
  - `__init__(settings)`
  - `laden(path, kennwort)` — Liest eine Datei; Fehler (DocumentIOError, PasswortNoetig) gehen an den Aufrufer.
  - `meta_fuer_speichern(meta)` — Dokument-Metadaten plus Einstellungen: Verfasser (Benutzername oder gelöscht).
  - `speichern(path, dokument, seite, meta, erwartet)` — Schreibt das Dokument; gibt den Bericht über nicht Übernommenes zurück. ``erwartet``: der zuletzt gesehene ``stand`` der Zieldatei
  - `zuletzt()`
  - `gelesen(path)`
  - `vergessen(path)`
  - `sichern(tabs)` — Automatische Sicherung aller geänderten Dokumente. Fehler stören die Arbeit nie.
  - `wiederherstellbar(offene_token)`
  - `verwerfen(token)`

### `kern/farben.py`

Die Grundfarben des Programms mit Namen — der eine Ort, an dem ein Farbwert steht.

- **class `Farbe`**

### `kern/pfade.py`

Orte der Programmdaten: Ressourcen im Paket, Symbole/Bilder/Schriften unter ressourcen/.


### `kern/piktogramme.py`

Der Piktogramm-Katalog (Name → 24×24-Pfad) und das Bild eines Piktogramms — neutral, ohne Oberfläche.

- `katalog()` — Alle 1800 Lucide-Symbole (Name → 24×24-Pfad) — für Piktogramm einfügen und Symbol austauschen.
- `katalog_bild(name, px, farbe, strich)`

### `kern/tabellenaktionen.py`

Die Tabellenaktionen „Einfügen“ und „Löschen“ - eine gemeinsame Definition für Tabellentools, Mini-Leiste und Kontextmenü.

- **class `Tabellenaktion`**(NamedTuple)

## `kern/befehle`

### `kern/befehle/__init__.py`

Die Befehle des Bandes, nach Aufgaben in Bausteine (Mixins) geteilt; ``kern/befehlsliste.py`` setzt sie zu ``Befehle`` zusammen.


### `kern/befehle/hilfen.py`

Gemeinsame Kleinigkeiten der Befehls-Bausteine.

- **class `FreiMenue`** — Die Menüs des Reiters Zeichentools: dieselben Baukasten-Menüs wie neben dem Bild, wirken aber auf den Editor, der bei der Wahl aktuell ist.
  - `formstile(cmd)`
  - `fuell(cmd)`
  - `kontur(cmd)`

## `kern/befehle/hauptreiter`

### `kern/befehle/hauptreiter/__init__.py`

Unterpaket ``hauptreiter`` von ``lunivo_writer.kern.befehle``.


### `kern/befehle/hauptreiter/ansicht.py`

Befehle: Ansicht, Fenster, Zoom.

- **class `AnsichtBefehle`** — Befehle des Bandes: Ansicht, Fenster, Zoom. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``).
  - `handbuch(k)`
  - `tastenHilfe(k)`
  - `erweiterungen(k)`
  - `vorlagenWaehlen(k)`
  - `vorlagenOrdner(k)`
  - `menueleisteZeigen(k)`
  - `an_menueleisteZeigen()`
  - `registerAnpassen(k)`
  - `schnellzugriffAnpassen(k)`
  - `symbolTauschen(k, name)` — Symbol austauschen (Ansicht ▸ Oberfläche, Optionen — und Rechtsklick auf einen Knopf, dann mit dessen Symbol).
  - `benutzeroberflaeche(k)`
  - `leistenZeigen(k)`
  - `an_leistenZeigen()`
  - `vorlagenZurueck(k)`
  - `neuesFenster(k)`
  - `fensterNebeneinander(k)`
  - `fensterUntereinander(k)`
  - `fensterKacheln(k)`
  - `fensterListe(k)`
  - `w_setzeLayout(k, art)`
  - `w_layoutJetzt(k)`
  - `gliederung(k)`
  - `an_gliederung()`
  - `linealZeigen(k)`
  - `linealHochZeigen(k)`
  - `an_linealZeigen()`
  - `an_linealHochZeigen()`
  - `_zoom_um(faktor)`
  - `groesser(k)`
  - `kleiner(k)`
  - `normal(k)`
  - `zoomBreite(k)`
  - `zoomSeite(k)`
  - `zoomStufe(k)`
  - `lesehilfe(k)`
  - `ausblenden(k)` — Markierten Text als „ausgeblendet“ formatieren (Strg+Umschalt+H).
  - `an_ausblenden()`
  - `versteckteZeigen(k)`
  - `an_versteckteZeigen()`
  - `silbenfarben(k)`
  - `an_silbenfarben()`
  - `silbenEinstellen(k)`
  - `markenZeigen(k)`
  - `an_markenZeigen()`
  - `navigation(k)`
  - `an_navigation()`

### `kern/befehle/hauptreiter/bearbeiten.py`

Befehle: Zwischenablage und Bearbeiten.

- **class `BearbeitenBefehle`** — Befehle des Bandes: Zwischenablage und Bearbeiten. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``).
  - `einfuegen(k)`
  - `einfuegenOhne(k)`
  - `menue_einfuegenKlappe()` — Wie in der Vorlage: mit Formatierung, passend zum Ziel formatiert, als unformatierter Text, „Inhalte einfügen …“ und
  - `einfuegenUnformatiert(k)` — Nur der Text der Zwischenablage, ohne jede Formatierung (auch nicht die der Einfügestelle): Schrift und Größe des Dokuments.
  - `inhalteEinfuegen(k)` — „Inhalte einfügen …“: aus den Formaten der Zwischenablage eines wählen (mit Formatierung, nur Text, Bild).
  - `ausschneiden(k)`
  - `kopieren(k)`
  - `suchen(k, *_)`
  - `menue_suchenKlappe()` — „Suchen oder ersetzen“: Suchen, Ersetzen, Gehe zu — alle im Feld der linken Seitenleiste.
  - `ersetzen(k, *_)`
  - `allesMarkieren(k)`
  - `menue_auswaehlenKlappe()` — „Auswählen“ wie in der Vorlage.
  - `tabelleOhneRahmen(k)` — Die nächste Tabelle ohne sichtbaren Rahmen (im Text nur gestrichelt angedeutet) ganz markieren.
  - `aehnlicheFormatierung(k)` — Alle Stellen mit derselben Zeichenformatierung wie an der Schreibmarke farbig hinterlegen; die erste wird markiert.
  - `auswahlbereich(k)` — Der Bereich „Auswahl“: alle Bilder, Formen und Tabellen des Dokuments in einer Liste; ein Klick markiert das Objekt.

### `kern/befehle/hauptreiter/datei.py`

Befehle: Datei, Vorlagen, Schutz.

- **class `DateiBefehle`** — Befehle des Bandes: Datei, Vorlagen, Schutz. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``).
  - `zuletztOeffnen(pfad)`
  - `zuletztEntfernen(pfad)`
  - `optionen(k)`
  - `fensterWaehlen(tab)`
  - `neu(k)`
  - `oeffnen(k)`
  - `speichern(k)`
  - `speichernUnter(k)`
  - `w_speichernAls(k, ext)`
  - `speichernPdf(k)`
  - `drucken(k)`
  - `vorschau(k)`
  - `eigenschaften(k)`
  - `umbenennen(k)`
  - `schliessen(k)`
  - `beenden(k)`
  - `ueber(k)`
  - `rueckgaengig(k)`
  - `wiederholen(k)`
  - `neuAusVorlage(k)`
  - `vorlagenDurchsuchen(k)`
  - `dokumentSchuetzen(k)`
  - `exportierenPng(k)` — Öffnet den Bildexport in der rechten Spalte des Datei-Menüs.
  - `kopieSpeichern(k)`
  - `exportierenDocx(k)`
  - `exportierenOdt(k)`
  - `exportierenTxt(k)`
  - `druckerWaehlen(k)`
  - `menue_zuletzt()`

### `kern/befehle/hauptreiter/einfuegen.py`

Befehle: Einfügen.

- **class `EinfuegenBefehle`**(EinfuegenObjektBefehle) — Befehle des Bandes: Einfügen. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``).
  - `seitenumbruch(k)`
  - `tabelleRaster(k)`
  - `tabelleZeichnen(k)` — Stift: Rechteck aufziehen, die Tabelle kommt dorthin (``tabellen_bedienung.py`` der Zeichenfläche); Esc beendet.
  - `tabelleRadierer(k)` — Radiergummi: Klick auf eine Zellenlinie verbindet die Zellen daneben (``tabellen_bedienung.py``); Esc beendet.
  - `bild(k)`
  - `hyperlink(k)` — Fenster „Hyperlink“ (Datei oder Webseite, Aktuelles Dokument, E-Mail-Adresse).
  - `objekt(k, als_symbol)` — Fenster „Objekt einfügen“: Inhalt einer Datei (Text, Bild) oder ein Dateisymbol mit Link.
  - `_datei_einsetzen(pfad, art)` — Bild ins Dokument, Text (DOCX, ODT, RTF, TXT, MD) mit seinem Inhalt, alles andere als Dateisymbol mit Link.
  - `dateiObjekt(k)` — „Datei-Objekt“ wie in der Vorlage: gleich das Fenster „Dateiobjekt einfügen“ (Lunivos Dateifenster); die gewählte Datei kommt
  - `menue_objektKlappe()`
  - `kopfFussZeigen(k)`
  - `menue_seitenzahlKlappe()` — Seitenzahl wie in der Vorlage: zehn Vorgaben (Kopf-/Fußzeile links, Mitte, rechts, außen, innen), darunter Einfügen … und Entfernen.
  - `_seitenzahl_vorgabe(schl)`
  - `seitenzahlEinfuegen(k)` — Fenster „Seitenzahl einfügen“; „Übernehmen für“ entscheidet, welche Abschnitte es trifft. „Von aktueller Seite“ beginnt am
  - `seitenzahlenEntfernen(k)`
  - `_eigene_wasserzeichen()` — Eigene Wasserzeichen (Text oder Bild) aus den Einstellungen.
  - `menue_wasserzeichenKlappe()` — Wasserzeichen wie in der Vorlage: „Benutzerdefiniert“ (eigene + Hinzufügen), „Voreinstellung“, darunter Einfügen … und Entfernen.
  - `seitenzahlKlappe(k)`
  - `leereSeite(k, quer)` — Leere Seite: ein neues Blatt hinter der Seite der Schreibmarke (Vertikal/Horizontal; ohne Angabe wie die Seite davor).
  - `sonderzeichen(k)` — Fenster „Symbol“ (Weitere Symbole …) in der Seitenleiste; „Einfügen“ setzt das Zeichen an die Schreibmarke.
  - `_symbol_daten()` — Die eine Datenbasis von Klappe und Fenster „Symbol“: zuletzt verwendet, benutzerdefinierte Liste, Tastenkombinationen.
  - `symbol_tasten_anwenden()` — Tastenkombinationen der benutzerdefinierten Symbole als Kürzel des Hauptfensters setzen (alte werden ersetzt).
  - `_sym(name)`
  - `menue_umbruecheKlappe()` — Umbrüche wie in der Vorlage: Seite, Spalte, Textfluss, dann die vier Abschnittsumbrüche.
  - `menue_leereSeiteKlappe()`
  - `menue_tabelleKlappe()` — Tabelle wie in der Vorlage: 10 × 10 Zellen (fügt an der Schreibmarke ein), darunter Einfügen, Zeichnen, Text ↔ Tabelle;
  - `menue_bildKlappe()`
  - `menue_textfeldKlappe()`
  - `textfeldVertikal(k)` — Textfeld mit senkrecht laufendem Text: dasselbe freie Objekt wie das waagerechte (Rahmen, Griffe, Schnellleiste), Richtung vertikal.
  - `textfeldMehrzeilig(k)`
  - `menue_schnellbausteineKlappe()` — Schnellbausteine wie in der Vorlage: AutoText-Liste ▸ und Felder …
  - `_bausteine_fuellen(m)` — AutoText-Liste wie in der Vorlage: die vier Seitenzahl-Texte, dann die eigenen und mitgelieferten Bausteine, zuletzt
  - `_autotext_seite(teile)`
  - `autotextHinzufuegen(k)` — Die Markierung als AutoText (Textbaustein) speichern; der Name kommt aus dem Fenster „AutoText erstellen“.
  - `schnellbausteine(k)`
  - `felder(k)` — Fenster „Felder“ (Schnellbausteine ▸ Felder …). TOC fügt ein echtes Inhaltsverzeichnis ein, TC einen ausgeblendeten
  - `menue_symbolKlappe()` — Symbol wie in der Vorlage: zuletzt verwendete und benutzerdefinierte Symbole als Kacheln, darunter „Weitere Symbole …“.
  - `_symbole_zuletzt()`
  - `_symbol_merken(z)`
  - `_symbol_einfuegen(z)`
  - `symbol(k)`
  - `zahl(k)`
  - `textInTabelle(k)`
  - `tabelleInText(k)`
  - `inhaltsverzeichnis(k)` — Fenster „Inhaltsverzeichnis“ (Füllzeichen, Ebenen, Seitenzahlen, Verknüpfungen); OK fügt es ein oder schreibt das
  - `verzeichnisseAktualisieren(k)`

### `kern/befehle/hauptreiter/einfuegen_objekte.py`

Einfügen-Befehle für Illustrationen, Text, Symbole und Seiten.

- **class `EinfuegenObjektBefehle`**
  - `_bild_einfuegen(img, alt, art, daten)`
  - `formenGalerie(k)`
  - `menue_formenKlappe()` — Formen wie in der Vorlage: Gruppen (Linie, Rechteck, Standardformen, Blockpfeile, …) mit kleinen Umrissbildern.
  - `formEinfuegen(k, name)` — Die Form ``name`` (Katalog ``formen_katalog``, auch Linien und Pfeile) einfügen: im Zeichenbereich dort, sonst als freies Objekt.
  - `zeichenbereich(k)` — Einfügen ▸ Formen ▸ Neuer Zeichenbereich (siehe ``editor/objekte/formen.py``).
  - `zeichnen(k)`
  - `smartart(k)`
  - `smartartText(k)`
  - `menue_smartartLayout()`
  - `menue_smartartFarben()`
  - `wordart(k)`
  - `wordartVorgabe(k, nr)` — WordArt aus der Galerie: fügt sofort „Hier Text einfügen“ im gewählten Stil als freies Objekt ein — ausgewählt (Rahmen, acht Griffe,
  - `wordartBearbeiten(k)` — Text und Stil des gewählten WordArt-Objekts im Fenster „WordArt“ ändern.
  - `textfeldBearbeiten(k)` — Im gewählten Textfeld direkt schreiben (Doppelklick, Enter oder F2 auf das Textfeld).
  - `menue_wordartKlappe()` — Galerie „Formatvorlage“: 15 Stile als „A“ auf hellem Kachelgrund (wie in der Vorlage, auch im dunklen Thema gut zu erkennen).
  - `menue_gleichungKlappe()` — Gleichung wie in der Vorlage: eingebaute Gleichungen als große Kacheln mit Namen, darunter „Neue Gleichung einfügen …“.
  - `menue_deckblattKlappe()` — Deckblätter wie in der Vorlage: Kopf „Stil“ mit Hochformat/Querformat, darunter die Gestaltungen als Seitenbilder in vier Spalten
  - `deckblattVorlage(k, vorlage, quer)` — Aus der Galerie (``gewaehlt`` liefert den Namen als ``k``) oder als Befehl ``deckblattVorlage:["Sonne"]``.
  - `menue_diagrammKlappe()` — Klappe am Diagramm-Knopf: Diagramm … (Fenster) und Neuer Zeichenbereich.
  - `diagramm(k)`
  - `piktogramm(k)`
  - `screenshot(k)`
  - `_aufnehmen(nur_bereich)`
  - `_bereich_fertig(pm)`
  - `_foto_einfuegen(pm)`
  - `textfeld(k)`
  - `initiale(k)`
  - `textAusDatei(k)`
  - `formel(k)`
  - `schnelltabelle(k)`
  - `deckblatt(k)`
  - `datumUhrzeit(k)`
  - `textbaustein(k)`
  - `textbausteine(k)`
  - `schnellbaustein(k)` — F3: steht vor der Schreibmarke ein Kürzel, kommt der Baustein sofort; sonst die Liste aller Bausteine zum Auswählen.

### `kern/befehle/hauptreiter/ki.py`

Befehle: KI, Vorlesen.

- **class `KIBefehle`** — Befehle des Bandes: KI, Vorlesen. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``).
  - `w_schnelleAktionErstellen(k)` — „Schnelle KI-Aktion erstellen“: ein Eintrag (art „aktion“) in der Liste der Assistenten.
  - `w_kiAssistentErstellen(k)` — „Neuen Assistenten erstellen“: das Fenster ``KIAssistentDialog`` (oberflaeche/dialoge/ki/ki_dialoge.py); ``werte()`` liefert die Felder für
  - `menue_assistenten()` — Das Menü „KI-Aktionen“: Schnelle KI-Aktionen und fortlaufende Assistenten (mit Haken an/aus) getrennt, neu anlegen, entfernen, Ergebnisse.
  - `menue_silbenTrennungMenue()` — Zur Silbentrennung: wo man die Trennstriche sieht (die Bearbeitungsansicht zeigt sie nicht) und die Einstellungen.
  - `silbentrennungVorschau(k)`
  - `menue_silbenMenue()`
  - `vorlesen(k)`
  - `vorlesenAbSatz(k)`
  - `vorlesenStopp(k)`
  - `stimmeWaehlen(k)`
  - `kiKorrektur(k)`
  - `kiVorschlaege(k)`
  - `kiUmformulieren(k)`
  - `kiZusammenfassen(k)`
  - `w_kiUebersetzenErsetzen(k)`
  - `w_kiUebersetzenZeigen(k)`
  - `kiEntwerfen(k)`
  - `w_chatUmschalten(k)`
  - `_ki_einstellungen(reiter)`
  - `w_kiEinstellungen(k)`
  - `w_kiKonfiguration(k)`
  - `w_kiSprache(k)`
  - `w_eigenenAnbieterHinzufuegen(k)`
  - `w_kiVergleich(k, nr)` — Vorher/Nachher-Fenster einer KI-Antwort (Kennung ``nr`` der Chat-Nachricht) in der Seitenleiste.
  - `w_kiErgebnisse(k)`
  - `kiTextInBild(k)`
  - `kiTextAktion(k, aktion)`

### `kern/befehle/hauptreiter/kommentare.py`

Befehle: Kommentare, Noten, Änderungen.

- **class `KommentarBefehle`** — Befehle des Bandes: Kommentare, Noten, Änderungen. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``).
  - `_text_abfragen(titel, frage, vorgabe)`
  - `kommentar(k)` — Neuer Kommentar wie in der Vorlage: das Feld „Kommentare“ links öffnet sich mit dem Eingabefeld — Knopf und Seitenleiste
  - `kommentarWeiter(k)`
  - `kommentarZurueck(k)`
  - `kommentarWeg(k)`
  - `kommentareAlleWeg(k)`
  - `_note(art, titel)` — Neue Note: das Zeichen kommt in den Text, unten öffnet sich das Notenfeld mit dem Cursor darin.
  - `fussnote(k)`
  - `endnote(k)`
  - `noteWeiter(k)`
  - `noteZurueck(k)`
  - `notenZeigen(k)`
  - `note_bearbeiten(art, nid)`
  - `_geschuetzt(*arten)` — Steht ein Dokumentschutz dieser Art (Überprüfen ▸ Bearbeitung einschränken), Hinweis in der Statusleiste und True.
  - `verfolgen(k)`
  - `an_verfolgen()`
  - `markupUmschalten(k)`
  - `an_markupUmschalten()`
  - `ueberarbeitungsbereich(k)`
  - `aenderungAnnehmen(k)`
  - `aenderungAblehnen(k)`
  - `_aend_am_cursor(annehmen)`
  - `aenderungWeiter(k)`
  - `aenderungZurueck(k)`
  - `aenderungenUebernehmen(k)`
  - `aenderungenVerwerfen(k)`

### `kern/befehle/hauptreiter/pruefen.py`

Befehle: Überprüfen, Schreibhilfe, Vergleichen.

- **class `PruefenBefehle`** — Befehle des Bandes: Überprüfen, Schreibhilfe, Vergleichen. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``).
  - `woerterZaehlen(k)` — Wörter zählen wie in der Vorlage: Statistiken des Dokuments, auf Wunsch samt Fuß- und Endnoten.
  - `_jetzt_pruefen()` — Prüfen (F7): ohne Text eine deutliche Rückmeldung statt einer leeren Seitenleiste.
  - `rechtschreibung(k)`
  - `w_pruefen(k)`
  - `gruendlichPruefen(k)`
  - `wellen(k)` — Rote Wellenlinien beim Schreiben an/aus (derselbe Schalter wie „We“ in der Seitenleiste und in „Welche Hilfe wann“).
  - `an_wellen()`
  - `vorhersage(k)`
  - `an_vorhersage()`
  - `autokorrektur(k)`
  - `an_autokorrektur()`
  - `tafelZeigen(k)`
  - `welcheHilfe(k)`
  - `w_optionenOeffnen(k, seite)`
  - `zeilenfokus(k)`
  - `an_zeilenfokus()`
  - `bearbeitungSperren(k)`
  - `an_bearbeitungSperren()`
  - `lesemodus(k)`
  - `an_lesemodus()`
  - `_fassung_laden(pfad)`
  - `_ergebnis_blatt(titel, ziel, page)` — Öffnet das Ergebnis (ein ``Dokument``) in einem neuen Blatt.
  - `dokumenteVergleichen(k)`
  - `dokumenteZusammenfuehren(k)`
  - `_neues_blatt(titel)`
  - `umschlag(k)`
  - `etiketten(k)`
  - `seriendruckfeld(k)`
  - `adressblock(k)`
  - `seriendruckregel(k)`
  - `seriendruck(k)`
  - `_form_dialog(art)`
  - `formTextfeld(k)`
  - `formAuswahl(k)`
  - `tabstopps(k)`
  - `geheZu(k, art)` — „Gehe zu“ (Strg+G): der Reiter im Feld „Suchen und ersetzen“ der linken Seitenleiste.
  - `vollbild(k)`
  - `an_vollbild()`
  - `formDatum(k)`
  - `formKasten(k)`
  - `formKnopf(k)`
  - `formLeeren(k)`
  - `thesaurus(k)`
  - `_wie_geschrieben(alt, neu)`
  - `barrierefrei(k)`
  - `pruefsprache(k)`
  - `pruefsprache_aktuell()`
  - `pruefsprache_setzen(kennung)` — Die Sprache des Dokuments für die Korrekturhilfen (wird in der Datei vermerkt) — vom Band und vom Fenster „KI-Einstellungen“ benutzt.

### `kern/befehle/hauptreiter/seite.py`

Befehle: Seite, Abschnitte, Spalten.

- `_abschnitt_wasserzeichen(ps, i, nr, bereich, w, alt)` — Das Wasserzeichen, das der Abschnitt Nummer ``i`` nach „Übernehmen für“ bekommt; ``_UNVERAENDERT``, wenn er es behält.
- **class `SeiteBefehle`** — Befehle des Bandes: Seite, Abschnitte, Spalten. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``).
  - `w_setzeRandVorgabe(k, art)`
  - `galerie_randVorgaben()` — Die Randvorgaben der Galerie im Band: ``[(art, Beschriftung), ...]``.
  - `randVorgabeWaehlen(art)`
  - `setzeRaender(oben, unten, links, rechts)`
  - `w_randVorgabeJetzt()`
  - `seitenraender(k, *_)`
  - `spaltenSetzen(k, n)`
  - `w_spaltenJetzt()`
  - `spalten(k)`
  - `spaltenumbruch(k)` — Der Text danach beginnt in der nächsten Spalte (bei einer Spalte: auf der nächsten Seite).
  - `w_setzePapier(k, art)`
  - `w_papierJetzt()`
  - `w_querJetzt()`
  - `w_setzeQuer(k, quer)` — Hochformat (False) oder Querformat (True) für den Abschnitt am Zeiger.
  - `querformat(k)`
  - `w_setzeThema(k, wahl)`
  - `w_themaJetzt()`
  - `_haken_auffrischen(m, jetzt)` — Vor dem Aufklappen die aktuelle Kachel markieren (die Menüs werden nur einmal gebaut).
  - `menue_raenderKlappe()`
  - `menue_ausrichtungKlappe()`
  - `menue_groesseKlappe()`
  - `menue_spaltenKlappe()`
  - `menue_textrichtungKlappe()` — Textrichtung wie in der Vorlage. Lunivo setzt Text nur waagerecht; die senkrechten Richtungen bleiben grau.
  - `menue_zeilennummernKlappe()`
  - `zeilennummernArt(k, art)` — ``art``: None = keine, "" = fortlaufend, "seite" = jede Seite neu.
  - `_ohne_zeilennr()`
  - `zeilennummernUnterdruecken(k)` — Der Absatz an der Schreibmarke (oder die markierten) bekommt keine Zeilennummern — oder wieder welche.
  - `menue_ausrichtenKlappe()` — Ausrichten wie in der Vorlage: die Form oder das freie Bild am Blatt ausrichten; was eine Mehrfachauswahl braucht, bleibt grau.
  - `_seite_aendern(**felder)`
  - `menue_seitenfarbe()`
  - `menue_seitenfarbeKlappe()` — Seitenfarbe wie in der Vorlage: Palette, darunter Hintergrundbild und anderer Hintergrund (in Lunivo noch grau) und das
  - `seitenfarbe(k)`
  - `wasserzeichen(k)`
  - `_wasserzeichen_setzen(w, bereich)` — Wasserzeichen für das ganze Dokument oder nur den Abschnitt mit der Schreibmarke („Übernehmen für“).
  - `seitenrahmen(k)`
  - `netzlinien(k)`
  - `an_netzlinien()`
  - `absatzabstand(k)`
  - `_abstand_setzen(vor, nach)`
  - `zeilennummern(k)`
  - `an_zeilennummern()`
  - `silbentrennung(k)`
  - `an_silbentrennung()`
  - `textrichtung(k)`
  - `textrichtungLinks(k)`
  - `textrichtungRechts(k)`
  - `zeilenumbruch(k)` — Zeilenumbruch ohne neuen Absatz (Umschalt+Enter).
  - `an_textrichtung()`
  - `menue_designsKlappe()`
  - `designSetzen(k, name)` — Design: Schrift der Überschriften und des Textes, Farbe der Überschriften — für das ganze Dokument (ein Schritt).
  - `menue_farbenKlappe()`
  - `farbschemaSetzen(k, name)`
  - `_farbe_eigen()`
  - `menue_schriftartenKlappe()`
  - `schriftpaarSetzen(k, name)`
  - `menue_effekteKlappe()`
  - `effektSetzen(k, name)` — Effekt an die markierte Form bzw. das markierte freie Bild; ist nichts markiert, an alle im Dokument.
  - `designs(k)`
  - `farbschema(k)`
  - `designSchriften(k)`
  - `designEffekte(k)`
  - `abschnittsumbruch(k, art)`
  - `abschnittLoeschen(k)`
  - `abschnittVorher(k)`
  - `abschnittNaechster(k)`
  - `abschnittNavigation(k)`
  - `abschnittEinstellungen(k)`
  - `_kopf_link(was, an)`
  - `kopfVerknuepfen(k)`
  - `fussVerknuepfen(k)`
  - `an_kopfVerknuepfen()`
  - `an_fussVerknuepfen()`
  - `schriftartMehr(k)`
  - `papierformatFenster(k)`
  - `fusszeileBearbeiten(k)`
  - `ersteSeiteAnders(k)`
  - `geradeUngerade(k)` — „Gerade und ungerade Seiten sind unterschiedlich“: gerade Seiten bekommen eine eigene Kopf-/Fußzeile (zuerst eine Kopie der gewöhnlichen).
  - `an_geradeUngerade()`
  - `an_ersteSeiteAnders()`
  - `tabelleSortieren(k)`

### `kern/befehle/hauptreiter/serien.py`

Befehle: Seriendruck (Reiter „Mailings“ nach der Vorlage).

- **class `SerienBefehle`** — Befehle des Kontext-Reiters „Mailings“. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``).
  - `_serie()`
  - `_hat_quelle()`
  - `_gewaehlte()` — Die angehakten Sätze, mit den Namen der Felder im Text.
  - `an_serienVorschau()`
  - `an_serienHervorheben()`
  - `serienReiter(k)` — Verweise ▸ Seriendruck: den Reiter „Mailings“ zeigen und dorthin wechseln.
  - `serienSchliessen(k)`
  - `serienQuelle(k)` — Datenquelle öffnen: eine Empfängerliste als Text (CSV mit ; , oder Tabulator; erste Zeile = Spaltennamen).
  - `_quelle_setzen(pfad, spalten, saetze)`
  - `serienQuelleSchliessen(k)`
  - `menue_serienQuelleKlappe()`
  - `serienEmpfaenger(k)`
  - `serienFeld(k)`
  - `serienNaechster(k)`
  - `serienHervorheben(k)` — Seriendruckfelder hervorheben: der farbige Hintergrund der Felder an oder aus (nur Anzeige, ändert den Text nicht).
  - `serienZuordnen(k)`
  - `_briefe()`
  - `_vorschau_auffrischen()`
  - `serienVorschau(k)` — Seriendruck-Vorschau an/aus: zeigt den Brief des gewählten Datensatzes; die Vorlage bleibt unverändert.
  - `_gehe_satz(wohin)`
  - `serienErster(k)`
  - `serienVorheriger(k)`
  - `serienNaechsterSatz(k)`
  - `serienLetzter(k)`
  - `feld_datensatz()` — Das Feld zwischen „Vorheriger“ und „Nächster Datensatz“: Nummer des gezeigten Datensatzes (Eingabe springt dorthin).
  - `_datensatz_anzeigen()`
  - `serienNeuesDokument(k)` — In neuem Dokument zusammenführen: alle Briefe hintereinander, je Brief eine neue Seite.
  - `serienEinzeln(k)` — In anderem neuen Dokument zusammenführen: jeder Brief als eigene DOCX-Datei in einem Ordner.
  - `serienDrucker(k)` — An Drucker zusammenführen: die Briefe in ein neues Dokument und gleich das Druckfenster.

### `kern/befehle/hauptreiter/text.py`

Kompatible Fassade für Zeichen-, Absatz- und Formatvorlagenbefehle.

- **class `TextBefehle`**(TextZeichenBefehle, TextAbsatzBefehle, TextVorlagenBefehle) — Befehle des Bandes: Zeichen und Absatz; öffentliche Fassade.

### `kern/befehle/hauptreiter/text_absatz.py`

TextAbsatzBefehle: fachlich abgegrenzte Bandbefehle.

- **class `TextAbsatzBefehle`** — Teilbereich der Textbefehle; wird von TextBefehle zusammengesetzt.
  - `punkte(k)`
  - `an_punkte()`
  - `zahlen(k)`
  - `an_zahlen()`
  - `_listenraster(art, titel)` — Auswahl der Aufzählungs- bzw. Nummerierungsarten: dieselben Kacheln und Listen wie im Fenster „Nummerierung und Aufzählungszeichen“.
  - `_liste_setzen(spec)`
  - `listeDialog(seite)` — Fenster „Nummerierung und Aufzählungszeichen“ (Baukasten); das Ergebnis gilt für den Absatz an der Schreibmarke.
  - `menue_aufzaehlungKlappe()`
  - `menue_nummerierungKlappe()`
  - `einzugMehr(k)`
  - `einzugWeniger(k)`
  - `einzugGenau(k)`
  - `ebeneHoeher(k)`
  - `ebeneTiefer(k)`
  - `links(k)`
  - `an_links()`
  - `mitte(k)`
  - `an_mitte()`
  - `rechts(k)`
  - `an_rechts()`
  - `block(k)`
  - `an_block()`
  - `menue_zeilenabstandKlappe()`
  - `steuerzeichenZeigen(k)`
  - `an_steuerzeichenZeigen()`
  - `verteilt(k)`
  - `formatUebertragen(k)`
  - `an_formatUebertragen()`
  - `sortieren(k)` — Sortiert die markierten Absätze (ohne Markierung das ganze Dokument); „Text sortieren“ fragt Schlüssel, Typ und Richtung,
  - `menue_absatzSchattierung()`
  - `menue_absatzRahmen()`
  - `_rahmen_seite(schluessel)` — Eintrag des Rahmen-Menüs: einzelne Seiten ein-/ausschalten, alle, außen oder keine.
  - `absatzRahmen(k, seite)` — Fenster „Rahmen und Schattierung“ (Reiter Rahmen · Seitenrand · Schattierung); ``seite`` wählt den Reiter.

### `kern/befehle/hauptreiter/text_vorlagen.py`

TextVorlagenBefehle: fachlich abgegrenzte Bandbefehle.

- **class `TextVorlagenBefehle`** — Teilbereich der Textbefehle; wird von TextBefehle zusammengesetzt.
  - `_stile_fertig()` — Nach jeder Änderung an den Vorlagen: Galerie neu füllen, Tastenkombinationen der Vorlagen in allen Dokumenten neu setzen.
  - `_taste_belegt(taste, eigene)` — Name dessen, was die Tastenkombination schon hat (Befehl im Fenster oder andere Vorlage), sonst None.
  - `neueFormatvorlage(k)` — Fenster „Neue Formatvorlage“ (Baukasten); die Werte kommen vom Absatz an der Schreibmarke.
  - `formatvorlageAendern(name)` — Rechtsklick auf eine Vorlage in der Galerie ▸ Ändern …: dasselbe Fenster, der Name steht fest.
  - `formatvorlageLoeschen(name)`

### `kern/befehle/hauptreiter/text_zeichen.py`

TextZeichenBefehle: fachlich abgegrenzte Bandbefehle.

- **class `TextZeichenBefehle`** — Teilbereich der Textbefehle; wird von TextBefehle zusammengesetzt.
  - `stilAnwenden(name)`
  - `stilVorschau(name, ed)` — Stilvorschau (Überfahren der Galerie): „Fließtext“ gilt als „Standard“.
  - `schriftGroesser(k)`
  - `schriftKleiner(k)`
  - `schlicht(k)`
  - `fett(k)`
  - `an_fett()`
  - `kursiv(k)`
  - `an_kursiv()`
  - `unter(k)`
  - `an_unter()`
  - `menue_unterstrichKlappe()` — Wie in der Vorlage: die Linienarten als Bild, „Mehr Unterstreichungen …“ (Fenster Schriftart) und „Unterstreichungsfarbe“ mit der
  - `_unterfarbe(farbe)` — Farbe der Unterstreichung; ist der Text noch nicht unterstrichen, wird er es einfach (wie in der Vorlage).
  - `durchJetzt(k)`
  - `an_durchJetzt()`
  - `symbolname_durchJetzt()`
  - `menue_durchKlappe()`
  - `_durch_waehlen(art)`
  - `betonung(k)` — Betonungszeichen (Punkt über jedem Buchstaben) an- oder ausschalten; andere Zeichen wählt das Fenster „Schriftart“.
  - `an_betonung()`
  - `menue_einstellungenKlappe()` — Knopf „Einstellungen“ wie in der Vorlage: die Fenster des Reiters Start.
  - `formatvorlagenBereich(k)` — „Formatvorlagen und Formatierung“: die Liste aller Formatvorlagen in der rechten Seitenleiste (wie der Bereich der Vorlage).
  - `objekteWaehlen(k)` — Springt zum nächsten Bild im Text und markiert es (dann erscheinen die Bildtools).
  - `zeichenumriss(k)`
  - `an_zeichenumriss()`
  - `zeichenschattierung(k)`
  - `an_zeichenschattierung()`
  - `texteffekte(k)` — „Texteffekte formatieren“ in der rechten Seitenleiste: die Änderungen wirken sofort an der Markierung, solange der Bereich offen ist.
  - `_effekt_setzen(**teile)` — Einen Teil der Texteffekte der Markierung ersetzen (Wert ``None`` nimmt ihn weg); die übrigen Effekte bleiben.
  - `menue_texteffekteKlappe()` — Menü am Knopf „Texteffekte“ wie in der Vorlage: WordArt, Schatten, Spiegelung, Leuchteffekt (je mit Bildchen zum Anklicken), 3D-Drehung und
  - `texteffekteFenster(k)` — Dasselbe als eigenes Fenster (mit „OK“), wie es das Schriftart-Fenster und die Formatvorlage benutzen.
  - `effekt(k)`
  - `durch(k)`
  - `an_durch()`
  - `hoch(k)`
  - `an_hoch()`
  - `tief(k)`
  - `an_tief()`
  - `schreibweise(k)`
  - `symbolname_schreibweise()`
  - `_aa_waehlen(wahl)`
  - `menue_schreibweiseKlappe()`
  - `schreibweiseFenster(k)` — Das Fenster „Groß-/Kleinschreibung“ (Zusatzfenster in der Seitenleiste).
  - `zeichenSkalierung(k, prozent)` — Zeichenskalierung: Breite der Zeichen des gewählten Texts in Prozent (wie „Skalieren“ im Fenster Schriftart).
  - `zeichenSkalierungJetzt()` — Aktuelle Zeichenskalierung in Prozent am Cursor (für den Haken im Menü Zeichen-Layout).
  - `umschlosseneZeichen(k)` — Das Fenster „Eingeschlossene Zeichen“: der gewählte Text bekommt Kreis, Quadrat, Dreieck oder Raute.
  - `phonetischesLeitzeichen(k)` — Das Fenster „Phonetisches Leitzeichen“: Leittext über dem gewählten Text.
  - `_farbmenue(setzen, ohne_text, vorschau, **opt)` — Die gemeinsame Farbpalette; ``setzen`` bekommt eine QColor oder None („keine“).
  - `schriftfarbeJetzt(k)`
  - `menue_schriftfarbeKlappe()`
  - `hervorhebenJetzt(k)`
  - `menue_hervorhebenKlappe()`

### `kern/befehle/hauptreiter/ueberpruefen.py`

Befehle: Reiter „Überprüfen“ nach Kays Vorlagen (ueberpruefen/01–10) — Klappen, Anzeige der Fassung, Markup-Auswahl,

- **class `UeberpruefenBefehle`** — Befehle des Reiters „Überprüfen“. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``).
  - `_sym(name)`
  - `_hat_kommentare()`
  - `_hat_aenderungen()`
  - `_schutz()`
  - `_darf_aendern()` — Annehmen und Ablehnen: nicht, solange ein Dokumentschutz steht.
  - `an_bearbeitungEinschraenken()`
  - `menue_rechtschreibKlappe()`
  - `menue_kommentarLoeschenKlappe()`
  - `menue_verfolgenKlappe()`
  - `_anzeige_index()`
  - `ueberpruefenAnzeige(k, index)` — Was das Dokumentfenster zeigt: mit oder ohne Markup, oder das Original ohne die verfolgten Änderungen (schreibgeschützt).
  - `feld_anzeige()` — Die Auswahl über „Markup anzeigen“ wie in der Vorlage: die Fassung, darunter das Markup-Menü.
  - `_filter_setzen(**werte)`
  - `_bearbeiter_fuellen(m)`
  - `_zeiten_fuellen(m)`
  - `menue_markupKlappe()`
  - `menue_ueberpruefenKlappe()`
  - `_angezeigte(annehmen)`
  - `_entscheiden_menue(annehmen)`
  - `menue_annehmenKlappe()`
  - `menue_ablehnenKlappe()`
  - `menue_vergleichenKlappe()`
  - `bearbeitungEinschraenken(k)` — Seitenleiste „Bearbeitung einschränken“: Schreibgeschützt, nur nachverfolgte Änderungen oder nur Kommentare.
  - `schutz_setzen(t, art)`

### `kern/befehle/hauptreiter/verweise.py`

Befehle: Verweise.

- **class `VerweiseBefehle`** — Befehle des Bandes: Verweise. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``).
  - `beschriftung(k)` — Fenster „Beschriftung“: die Nummer steht schon im Feld („Tabelle 1“), dahinter schreibt man weiter. Eigene Bezeichnungen
  - `_verzeichnis(art, titel, leer)`
  - `abbildungsverzeichnis(k)`
  - `stichwortverzeichnis(k)`
  - `literaturverzeichnis(k)`
  - `textmarke(k)`
  - `querverweis(k)` — Fenster „Querverweis“: „Einfügen“ setzt den Verweis an die Schreibmarke, das Fenster bleibt offen.
  - `indexEintrag(k)` — Fenster „Indexeintrag festlegen“: „Markieren“ setzt den Eintrag an die Markierung, „Alles markieren“ an jede Stelle
  - `indexAktualisieren(k)`
  - `inhaltsverzeichnisAktualisieren(k)`
  - `menue_inhaltsverzeichnisKlappe()` — Ebene 1–9 und Textkörper wie in der Vorlage. In Lunivo trägt die Ebene die Formatvorlage „Überschrift N“
  - `inhaltsEbene(k, ebene)`
  - `_note_gehe(delta, art, titel)`
  - `fussnoteZurueck(k)`
  - `fussnoteWeiter(k)`
  - `endnoteZurueck(k)`
  - `endnoteWeiter(k)`
  - `quelleNeu(k)`
  - `quellenVerwalten(k)`
  - `zitat(k)`
  - `zitierweise(k)`

## `kern/befehle/kontextreiter`

### `kern/befehle/kontextreiter/__init__.py`

Unterpaket ``kontextreiter`` von ``lunivo_writer.kern.befehle``.


### `kern/befehle/kontextreiter/bildtools.py`

Befehle: Kontext-Reiter „Bildtools“ für frei positionierte Bilder (Datei, Bildschirmfoto, Piktogramm): Zuschneiden, Größe, Farbe.

- **class `BildToolsBefehle`**
  - `_bz()` — Das gewählte freie Bild (``bildlayout``-Ziel) oder None (dann Hinweis in der Statuszeile).
  - `bildZuschneidenModus(k)` — Zuschneiden ein/aus: schwarze Eckwinkel und Kantenstriche; Ziehen schneidet ab (der Zuschnitt wird als Anteil gespeichert).
  - `an_bildZuschneidenModus()`
  - `bildZuschneidenForm(k, name)` — Nach Form zuschneiden: ``name`` ist eine Form des Formenkatalogs (zum Beispiel „Ellipse“, „Herz“).
  - `bildZuschneidenSkala(k, verhaeltnis)` — Nach Skala zuschneiden: Seitenverhältnis wie ``"16:9"``, ``"4:3"``, ``"1:1"`` (mittiger Ausschnitt).
  - `bildDrehen(k, richtung)` — Das Bild um 90° drehen: ``richtung`` ist ``"rechts"`` oder ``"links"`` (nutzt ``zeichenDrehen``).
  - `bildZuschneidenZuruecksetzen(k)` — Form und Größe zurücksetzen: Maske und Zuschnitt entfernen, das ganze Bild im ursprünglichen Seitenverhältnis.
  - `bildGroesseZuruecksetzen(k)` — Größe zurücksetzen: Originalgröße des sichtbaren Ausschnitts in Bildpunkten.
  - `bildSeitenverhaeltnis(k)` — Seitenverhältnis sperren ein/aus (auch Ziehen an den Kanten hält es dann).
  - `an_bildSeitenverhaeltnis()`
  - `bildTransparent(k, toleranz)` — Transparente Farbe: eine Farbe des Bildes wählen (Farbfenster), alle gleichen Bildpunkte werden durchsichtig.
  - `bildVergroessern(k)` — Lupe der Schnellleiste: das Bild in seiner Auflösung in der Seitenleiste zeigen, Zoom per Regler oder Mausrad (nur ansehen).
  - `bildHelligkeit(k, schritt)` — Heller (+10) oder dunkler (-10): Helligkeit des Bildes um ``schritt`` Prozent ändern (-100 bis 100). Nicht zerstörend: der Wert steht als
  - `bildKontrast(k, schritt)` — Kontrast erhöhen (+10) oder verringern (-10) um ``schritt`` Prozent (Angabe ``kontrast``, nicht zerstörend).
  - `bildAendern(k, pfad)` — Bild ändern: eine andere Bilddatei an die Stelle des Bildes setzen (Größe, Lage und Rahmen bleiben).
  - `bildKomprimieren(k)` — Bilder komprimieren: weggeschnittene Bereiche löschen und auf 144 dpi (Anzeigegröße) verkleinern.
  - `bildZuruecksetzen(k)` — Bild zurücksetzen: Zuschnitt, Farbe, Rahmen, Füllung, Effekte und Drehung zurück (Lage und Alternativtext bleiben).
  - `_bild_frei()` — (Editor, Ziel) des gewählten frei positionierten Bildes (Datei, Bildschirmfoto, Piktogramm …) oder (Editor, None).
  - `bildFarbe(k)`
  - `bildZuschneiden(k)`
  - `objektDrehen(k)`
  - `objektAusrichten(k)`
  - `_bild()`
  - `bildGroesse(k)`
  - `bildBreite(k)`
  - `anordnen(k)` — Textumbruch / Position: Objekt mit Text in der Zeile oder frei, vom Text umflossen.
  - `bildOriginal(k)`
  - `bildAltText(k)` — Alternativtext und „Als dekorativ markieren“ in der Seitenleiste (``BildAlternativtextPanel``); Änderungen gelten sofort.
  - `bildEntfernen(k)`

### `kern/befehle/kontextreiter/diagrammtools.py`

Befehle: Kontext-Reiter „Diagrammtools“ für das Diagramm als freies Objekt (``editor/objekte/frei_objekt.py``, Art ``diagramm``).

- `_nummer(k, nr)` — Bandbefehle mit Angabe (``diagrammStil:[2]``) bekommen (Knopf, Nummer); direkte Aufrufe dürfen die Nummer als erstes Argument geben.
- **class `DiagrammToolsBefehle`**
  - `_dg()` — Die Daten des gewählten Diagramms (Kopie) oder None.
  - `_dg_set(**kw)` — Daten des gewählten Diagramms ändern (None entfernt die Angabe) und neu zeichnen; ohne Diagramm ein Hinweis in der Statuszeile.
  - `diagrammDatenBearbeiten(k)` — Titel, Rubriken und Datenreihen des gewählten Diagramms im vorhandenen Datenfenster bearbeiten.
  - `diagrammTypAendern(k, untertyp)` — Mit ``untertyp`` (``diagrammTypAendern:["linie"]``, Namen aus ``diagramm.TYPEN``) wird die Diagrammart direkt gesetzt; ohne Angabe öffnet
  - `menue_diagrammTyp(symbol)` — Klappe eines Typ-Knopfes: die Untertypen der Gruppe (``diagramm.TYPEN``) mit Haken beim aktuellen (beim Öffnen aufgefrischt);
  - `menue_diagrammSchnelllayout()`
  - `diagrammSchnelllayout(k, nr)` — Schnelllayout Nummer ``nr`` (0 bis 18, siehe ``SCHNELLLAYOUT_ANZEIGE`` für die Reihenfolge der Kacheln) anwenden — für Kacheln der Schnellleiste.
  - `menue_diagrammFarben()` — Die Farbreihen der Diagrammvorlagen (``diagramm.VORLAGEN``), je mit der ersten Farbe als Muster.
  - `diagrammFarben(k, nr)` — Farbzeile Nummer ``nr`` aus ``diagramm.farbschemen_flach()`` (Gruppen „Farbig“ dann „Monochrom“) anwenden — für Kacheln der Schnellleiste.
  - `menue_diagrammElement()` — Diagrammelemente an/aus: Titel, Legende (mit Lage), Datenbeschriftungen, Achsen, Achsentitel, Gitternetzlinien, Datentabelle,
  - `diagrammElement(k, name, wert)` — Ein Diagrammelement umschalten (``diagrammElement:["achsen"]``) oder setzen (``wert`` True/False, bei ``legende`` auch die Lage
  - `_element_an(name)`
  - `diagrammElementListe(k)` — Für die Liste „Diagrammelemente“: [(Name, Anzeigename, Haken)] in der Reihenfolge der Vorlage.
  - `diagrammTitel(k)`
  - `an_diagrammTitel()`
  - `diagrammLegende(k)`
  - `an_diagrammLegende()`
  - `diagrammBeschriftungen(k)`
  - `an_diagrammBeschriftungen()`
  - `diagrammStil(k, nr)` — Diagrammstil ``nr`` (Nummer in ``diagramm.STILE``, Liste: ``diagramm.stile_liste()``).
  - `diagrammZuruecksetzen(k)` — Farben, Titel/Legende/Beschriftungen, Elemente, Filter, Teilformate und Stil auf den Standard zurück; Daten, Diagrammart und Alternativtext bleiben.
  - `diagrammTeile(k)` — Die wählbaren Teile des gewählten Diagramms [(Schlüssel, Anzeigename)] für das Feld „Diagrammbereich“ (leer ohne Diagramm).
  - `diagrammTeilWaehlen(k, schluessel)` — Einen Diagrammteil wählen (``diagrammTeilWaehlen:["reihe_0"]``; ohne Schlüssel: Auswahl aufheben). Zeichnet nicht neu.
  - `feld_diagrammTeil()` — Anzeigename des gewählten Teils fürs Feld „Diagrammbereich“ (ohne Auswahl: „Diagrammbereich“).
  - `diagrammTeilFormat(k, angaben, **kw)` — Format des gewählten Teils ändern: ``fuell`` (Farbe oder Wörterbuch), ``linie``, ``schatten``, ``reflektion``, ``leuchten``, ``weich``, ``d3``, ``drehung``,
  - `diagrammFilterDaten(k)` — Für das Popup „Diagrammfilter“: {"reihen": [(Name, Haken)], "rubriken": [(Name, Haken)]} — Haken = sichtbar.
  - `diagrammFilterSetzen(k, ausgeblendet)` — „Übernehmen“: {"reihen": [Namen], "rubriken": [Namen]} = die ausgeblendeten Einträge (leer/None = alles zeigen).
  - `diagrammNamenQuelleLesen(k)` — Gewählte Namensquelle: ``"zeile1"`` (Standard), ``"spalte_a"`` oder ``"keine"`` (Radio im Reiter „Name“).
  - `diagrammNamenQuelle(k, quelle)` — Namensquelle wählen: ``"zeile1"`` (Standard: Reihennamen und Rubriken wie eingegeben), ``"spalte_a"`` (Reihen und Rubriken tauschen die
  - `diagrammNamenSetzen(k, namen)` — Reihen/Rubriken umbenennen: {"reihen": [(alt, neu)], "rubriken": [(alt, neu)]}. Leere oder doppelte neue Namen bleiben beim alten Namen;
  - `diagrammAltText(k, titel, beschreibung)` — Alternativtext des Diagramms (``alt_titel``, ``alt_beschreibung``; in DOCX steht die Beschreibung als ``descr``); ``""`` löscht.
- `_umbenennen(alte, paare)` — Alter Name → neuer Name. Leer oder doppelt: der alte Name bleibt.
- `_filter_umbenennen(aus, rn, kn)` — Die ausgeblendeten Reihen und Rubriken unter ihren neuen Namen; leere Gruppen fallen weg.
- `_element_befehle()` — Je Element ``an_diagrammElement_<name>`` (Haken) und ``diagrammElement_<name>`` (Umschalten) — für Knöpfe, die keine Angabe mitgeben.
- `_typ_klappen()` — Je Typ-Knopf des Reiters eine Klappe ``menue_diagrammTyp_<symbol>`` (Untertypen der Gruppe).

### `kern/befehle/kontextreiter/formtools.py`

Befehle zu Formen als freie Objekte (Zeichentools): Formstil-Raster, Füllungs-Palette, Anpassungsgriff, Form tauschen, Punkte bearbeiten.

- **class `FormToolsBefehle`**
  - `_form()`
  - `_form_hinweis()`
  - `formstileRaster(k)` — Daten der Galerie „Formstile“: 6 Zeilen × 7 Spalten (``editor/objekte/formen_stile.formstile_raster``).
  - `formStilRaster(k, zeile, spalte)` — Stil (Zeile, Spalte) des Rasters auf die gewählte Form: Füllung, Verlaufsart, Linie, Strichbreite und Effekt.
  - `zeichenFuellungDaten(k)` — Daten des Füllungs-Popups aus dem Baustein ``oberflaeche/baukasten/basis/farben.py``: {"thema": Zeilen × 10 Spalten, "standard": [Farben],
  - `formAnpassen(k, wert, index)` — Parameter ``index`` des Anpassungsgriffs der gewählten Form auf ``wert`` setzen (``formen.anpass_setzen``).
  - `kann_formAnpassen()`
  - `formAendern(k, name)` — „Form bearbeiten ▸ Form ändern“: die gewählte Form durch ``name`` (Katalogname) ersetzen; Größe, Füllung und Kontur bleiben.
  - `formPunkteBearbeiten(k)` — „Punkte bearbeiten“: die gewählte Form wird zur Freiform (``editor/objekte/freiform.py``, Punktliste in ``daten["punkte"]``) und zeigt ihre
  - `kann_formPunkteBearbeiten()`
  - `_form_farbe(feld, titel)`
  - `_form_aendern(**kw)`
  - `menue_formFuellung()`
  - `menue_formKontur()`
  - `menue_formVorlagen()`
  - `_form_vorlage(name)`
  - `formText(k)`
  - `gruppieren(k)`
  - `gruppeAufheben(k)`

### `kern/befehle/kontextreiter/kontext.py`

Befehle: Kontext-Reiter: Tabelle, Bild, Formen, Zeichnen.

- **class `KontextBefehle`**(TabellenBefehle, TabellenFormatBefehle, ZeichenToolsBefehle) — Befehle des Bandes: Kontext-Reiter: Tabelle, Bild, Formen, Zeichnen. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``).
  - `absatzFormatZuruecksetzen(k)` — Absatzformat (Blockformat) der Absätze an der Schreibmarke/Auswahl auf Standard; Zeichenformat bleibt. Ein Rückgängig-Schritt.
  - `wortExtras(k)` — Wort-Extras: Absätze aufräumen (Markierung, sonst das ganze Dokument).
  - `menue_wortExtrasKlappe()` — Das Menü „Wort-Extras“ wie in der Vorlage, mit dem Untermenü „Löschen“; jeder Eintrag ist ein Schritt für Rückgängig.
  - `_wort_extra(text, f)`
  - `exportierenRtf(k)`

### `kern/befehle/kontextreiter/kopffuss.py`

Befehle: Kontext-Reiter „Kopf- und Fußzeile“ (Bearbeiten direkt auf der Seite, siehe ``oberflaeche/dokument/kopffuss/kopffuss_bearbeiter.py``).

- **class `KopfFussBefehle`** — Befehle des Bandes: Kopf- und Fußzeile. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``).
  - `_kf()` — Der Bearbeiter des aktuellen Editors, nur wenn er gerade bearbeitet.
  - `_kf_start(zone)`
  - `menue_kfGruppeKlappe()`
  - `_hf_klappe(zone)`
  - `menue_kopfzeileKlappe()`
  - `menue_fusszeileKlappe()`
  - `menue_kopfLinieKlappe()`
  - `menue_kfEinstellungenKlappe()`
  - `_kf_ausrichten(zone, ausr)`
  - `_kf_leeren(felder)`
  - `kopfFussSchliessen(k)`
  - `kfWechseln(k)`
  - `kfVorige(k)`
  - `kfNaechste(k)`
  - `kfVerknuepfen(k)`
  - `kann_kfVerknuepfen()` — Grau auf der ersten Seite/im ersten Abschnitt: dort gibt es keinen Vorgänger.
  - `an_kfVerknuepfen()`
  - `kfTabstopp(k)`
  - `kfOptionen(k)` — Seitenleistenfenster: Erste Seite anders; Gerade und ungerade Seiten unterschiedlich.
  - `_kf_abstand(attr, name, symbol)`
  - `feld_kopfHoehe()`
  - `feld_fussHoehe()`

### `kern/befehle/kontextreiter/smartart_knoten_zustand.py`

Befehle: Zustand des gewählten SmartArt-Knotens – seine Maße fürs Band und ob „Aufzählungszeichen einfügen“ geht.

- **class `SmartArtKnotenZustand`**
  - `smartartKnotenMasse()` — (Breite, Höhe) des gewählten Knotens in mm; ohne gewählten Knoten None (dann gelten die Maße des Objekts).
  - `kann_smartartAufzaehlung()` — Ein Knoten ist gewählt und das Layout erlaubt Aufzählungspunkte (im Organigramm sind Unterpunkte eigene Knoten: im Foto grau).
  - `smartartAufzaehlung(k)` — Ohne Wirkung, solange der Knopf grau ist.

### `kern/befehle/kontextreiter/smartarttools.py`

Befehle: Kontext-Reiter „SmartArt-Design“ für das SmartArt als freies Objekt (``editor/objekte/frei_objekt.py``, Art ``smartart``).

- **class `SmartArtToolsBefehle`**
  - `_sa()`
  - `_sa_hinweis()`
  - `_sa_tun(f, *args)`
  - `smartartKnotenWaehlen(k, ident)` — Knoten wählen (``smartartKnotenWaehlen:["k2"]``; ohne Id: Auswahl aufheben). Zeichnet nicht neu.
  - `smartartKnotenText(k, ident, text)` — Den Text eines Knotens setzen (Eintippen im Knoten).
  - `smartartFormEinfuegen(k, wie)` — „Form einfügen“: ``nach`` \| ``vor`` \| ``unter`` \| ``ueber`` \| ``assistent`` relativ zum gewählten Knoten (ohne Auswahl: hinter den letzten);
  - `smartartLevel(k, richtung)` — „Level erhöhen“ (``erhoehen``) / „Level reduzieren“ (``reduzieren``): der gewählte Knoten samt Unterknoten.
  - `smartartLevelErhoehen(k)`
  - `smartartLevelReduzieren(k)`
  - `smartartVerschieben(k, richtung)` — „Vorwärts“ (``vor``) / „Rückwärts“ (``zurueck``): den Knoten unter seinen Geschwistern verschieben.
  - `smartartVorwaerts(k)`
  - `smartartRueckwaerts(k)`
  - `smartartAufzaehlung(k)` — „Aufzählungszeichen einfügen“: ein Aufzählungspunkt „Text“ unter dem gewählten Knoten.
  - `smartartRechtsLinks(k)` — „Layout von rechts nach links“ umschalten (``rtl``); Zustand: ``an_smartartRechtsLinks``.
  - `an_smartartRechtsLinks()`
  - `smartartHierarchie(k, art)` — Organigramm-Variante: ``standard`` \| ``beide`` \| ``haengend_links`` \| ``haengend_rechts`` (nur bei den Layouts Organigramm/Hierarchie).
  - `smartartStil(k, nr)` — Formenstil 0 bis 4 (``SA.STILE``: Flach, Einfach, Hell, Kräftig, 3D).
  - `smartartLayout(k, name)` — Layout wechseln (Schlüssel aus ``SA.LAYOUTS``); Knoten und Farben bleiben.
  - `_sa_kann(was, richtung)`
  - `kann_smartartKnotenWaehlen()`
  - `kann_smartartFormEinfuegen()`
  - `kann_smartartAufzaehlung()`
  - `kann_smartartLevelErhoehen()`
  - `kann_smartartLevelReduzieren()`
  - `kann_smartartVorwaerts()`
  - `kann_smartartRueckwaerts()`
  - `kann_smartartHierarchie()`
  - `kann_smartartRechtsLinks()`
  - `kann_smartartStil()`

### `kern/befehle/kontextreiter/tabellen.py`

Befehle: Kontext-Reiter „Tabellentools“, Aufbau: Zeilen/Spalten einfügen und löschen, Zellen verbinden/teilen, Tabelle teilen, Eigenschaften.

- **class `TabellenBefehle`**
  - `_tab()`
  - `tabelleZeileOben(k)`
  - `tabelleZeileUnten(k)`
  - `tabelleSpalteLinks(k)`
  - `tabelleSpalteRechts(k)`
  - `tabelleZeileLoeschen(k)`
  - `tabelleSpalteLoeschen(k)`
  - `tabelleLoeschen(k)`
  - `tabelleZellenLoeschen(k)` — Löschen ▸ Zellen löschen …: ganze Zeile oder Spalte der Zelle.
  - `tabelleVerbinden(k)`
  - `tabelleTeilen(k)`
  - `tabelleTabelleTeilen(k)` — Tabelle oberhalb der Zeile der Schreibmarke teilen: die Zeilen ab hier kommen in eine neue Tabelle darunter.
  - `tabelleEigenschaften(k)`
  - `_tabellen_aktionsmenue(name)` — Menü „Einfügen“ bzw. „Löschen“ aus der gemeinsamen Definition (``kern/tabellenaktionen.py``): Band, Mini-Leiste und Kontextmenü.
  - `menue_tabelleEinfuegenAktionen()`
  - `menue_tabelleLoeschenAktionen()`

### `kern/befehle/kontextreiter/tabellen_format.py`

Befehle: Kontext-Reiter „Tabellentools“, Gestaltung: Rahmen, Schattierung, Vorlagen, Optionen, Zellausrichtung, Maße, Gitternetz, Textrichtung.

- **class `TabellenFormatBefehle`**
  - `tabelleRahmen(k)`
  - `an_tabelleRahmen()`
  - `tabelleRahmenSchattierung(k)` — Rechtsklick ▸ Rahmen und Schattierung: der Baustein-Dialog (ohne Reiter Seitenrand), vorbelegt aus Tabelle und Zelle.
  - `_tabelle_rahmen_schattierung_anwenden(e, linie, fuell)` — Rahmen der Tabelle (Linie oder None = ohne) und Füllfarbe der markierten Zellen bzw. der Zelle der Schreibmarke.
  - `tabelleBeschriftung(k, oben)` — „Beschriftung …“ für die Tabelle der Schreibmarke: dasselbe Fenster wie Verweise ▸ Beschriftung (``BeschriftungDialog``),
  - `menue_tabelleSchattierung()`
  - `menue_tabelleVorlagen()`
  - `_tabelle_vorlage(name)` — Vorlage auf die Tabelle der Schreibmarke anwenden; Kopfzeile/Streifen/Erste Spalte stehen je Tabelle.
  - `_tabellen_option(key)` — Option (kopf/streifen/spalte) der Tabelle der Schreibmarke umschalten; ist eine Vorlage gesetzt, wird sie neu angewendet.
  - `tabelleKopfzeile(k)`
  - `tabelleStreifen(k)`
  - `tabelleErsteSpalte(k)`
  - `_an_tabellen_option(key)`
  - `an_tabelleKopfzeile()`
  - `an_tabelleStreifen()`
  - `an_tabelleErsteSpalte()`
  - `_zelle_ausrichten(wo)`
  - `zelleOben(k)`
  - `zelleMitte(k)`
  - `zelleUnten(k)`
  - `_zelle_waagrecht(wo)`
  - `zelleLinks(k)`
  - `zelleZentriert(k)`
  - `zelleRechts(k)`
  - `menue_tabelleAutoAnpassen()`
  - `_tabelle_anpassen(art)`
  - `tabelleBreite(k)` — Breite der Spalte der Schreibmarke in cm festlegen (Eingabe; gesetzt über ``tabelleMasse``).
  - `tabelleMasse(breite_mm, hoehe_mm)` — Band-Zahlenfelder der Tabellentools: Spaltenbreite der Schreibmarke und/oder Mindesthöhe ihrer Zeile in mm setzen.
  - `tabelleMasseLesen()` — (Breite der Spalte, Höhe der Zeile) der Schreibmarke in mm für die Zahlenfelder des Bandes; ``None`` außerhalb einer Tabelle.
  - `an_tabelleGitternetz()`
  - `tabelleGitternetz(k)` — Gitternetzlinien umschalten: hellgraue gestrichelte Zellränder; wirkt nur bei Tabellen ohne Rahmen.
  - `menue_tabelleTextrichtung()`
  - `tabelleTextrichtung(k)` — Auswahl der Textrichtung der Zelle (waagrecht / rechts nach links).
  - `_tabelle_richtung(richtung)` — Textrichtung der Zelle der Schreibmarke bzw. aller markierten Zellen setzen.

### `kern/befehle/kontextreiter/texttools.py`

Befehle: Kontext-Reiter „Texttools“ (und die Galerien von „Zeichentools“) für die freien Objekte WordArt und Textfeld.

- **class `TextToolsBefehle`**
  - `tt_art()` — Welches freie Textobjekt ist markiert? ``wordart`` \| ``textfeld`` \| None.
  - `_wa()`
  - `_wa_set(**kw)` — Angaben des markierten WordArt/Textfelds ändern; ohne Auswahl ein Hinweis in der Statuszeile.
  - `ttSchriftart(name)`
  - `ttGroesse(pt)`
  - `tabSchriftart(name)`
  - `tabGroesse(pt)`
  - `_tt_pt(delta)`
  - `ttGroesser(k)`
  - `ttKleiner(k)`
  - `ttSchlicht(k)` — Formatierung löschen: Schrift, Auszeichnungen, Hervorhebung, Effekte, Liste und Absatzwerte zurück auf die Vorgabe der Vorlage.
  - `_tt_umschalten(schl, standard)`
  - `ttFett(k)`
  - `an_ttFett()`
  - `ttKursiv(k)`
  - `an_ttKursiv()`
  - `ttUnter(k)`
  - `an_ttUnter()`
  - `ttDurch(k)`
  - `an_ttDurch()`
  - `ttHoch(k)`
  - `an_ttHoch()`
  - `ttTief(k)`
  - `an_ttTief()`
  - `menue_ttUnter()` — Wie bei Start: die Linienarten als Bild, „Mehr Unterstreichungen …“ und die Unterstreichungsfarbe; wirkt auf das Objekt.
  - `_tt_unter_dialog()` — Das Fenster „Schriftart“ mit der Unterstreichung des Objekts; übernommen werden Art und Farbe der Linie.
  - `menue_ttDurch()`
  - `ttHervorJetzt(k)`
  - `menue_ttHervor()`
  - `ttSchriftfarbeJetzt(k)`
  - `menue_ttSchriftfarbe()`
  - `_tt_liste_setzen(spec)` — Aufzählung/Nummerierung des Objekts: dieselben Angaben wie im Start-Reiter (``editor/text/listen``), ``None`` = keine Liste.
  - `_tt_liste_ist(aufzaehlung)`
  - `ttPunkte(k)`
  - `an_ttPunkte()`
  - `ttZahlen(k)`
  - `an_ttZahlen()`
  - `_tt_listenraster(art, titel)` — Dieselbe Auswahl wie bei Start (alle Aufzählungszeichen und Nummerierungen), gilt für den Text im Objekt.
  - `_tt_listendialog(seite)`
  - `menue_ttPunkte()`
  - `menue_ttZahlen()`
  - `ttEinzugMehr(k)`
  - `ttEinzugWeniger(k)`
  - `ttSortieren(k)` — Zeilen des WordArt-Textes sortieren (A–Z, beim nächsten Mal Z–A).
  - `menue_ttTextrichtung()` — Textrichtung wie in der Vorlage (dieselben sechs Einträge mit Bildchen wie bei Start), wirkt auf den Text im Objekt.
  - `_tt_ausr(wie)`
  - `ttLinks(k)`
  - `ttMitte(k)`
  - `ttRechts(k)`
  - `ttBlock(k)`
  - `ttVerteilt(k)`
  - `an_ttLinks()`
  - `an_ttMitte()`
  - `an_ttRechts()`
  - `an_ttBlock()`
  - `an_ttVerteilt()`
  - `menue_ttZeilenabstand()`
  - `ttStil(nr)` — WordArt-Formatvorlage (0–14) auf das markierte WordArt anwenden; die Textfüllung, Kontur und Effekte setzen sich neu.
  - `galerie_ttWordartStile()`
  - `_wa_kachel(i)`
  - `menue_ttStile()` — Alle 15 Stile als „A“ auf hellem Grund (wie das Menü neben Einfügen ▸ WordArt), wirkt auf das markierte WordArt.
  - `menue_ttTextfuellung()`
  - `menue_ttTextkontur()`
  - `menue_ttTexteffekte()`
  - `_wa_effekt(**teile)`
  - `_effekt_menue(setzen, _schl)` — Schatten, Spiegelung und Leuchteffekt mit Bildchen (wie bei Start ▸ Texteffekte); ``setzen(**teil)`` schreibt den Teil.
  - `ttFormstil(schl)`
  - `galerie_ttFormstile()` — Die drei Kacheln „Abc“ im Band (schwarzer, blauer, oranger Rand) und das Menü mit allen 42 Formstilen.
  - `menue_ttFormFuellung()`
  - `menue_ttFormKontur()`
  - `ttFormEffekte(k)` — Weitere Formeffekte: die Seitenleiste „Formatierung“ auf dem Reiter Effekte (Schatten, Reflektion, Leuchten, Weiche Kanten).
  - `menue_ttFormEffekte()` — Schatten, Spiegelung und Leuchteffekt der Form (wie die Voreinstellungen der Seitenleiste), darunter „Weitere Effekte …“.
  - `ttFormatUebertragen(k)` — Format des markierten WordArt/Textfelds (Schrift, Auszeichnungen, Farben, Effekte, Form) aufnehmen; beim nächsten markierten Objekt
  - `an_ttFormatUebertragen()`
  - `_tt_felder()` — Die Textfelder, mit denen das markierte verknüpft werden kann (Schlüssel, Anzeigename): nicht es selbst, keins mit Vorgänger.
  - `menue_ttVerknuepfung()` — Das markierte Textfeld mit einem anderen verknüpfen (der Text läuft weiter) oder die Verknüpfung lösen.
  - `ttVerknuepfen(k, ziel)` — Das markierte Textfeld mit ``ziel`` verknüpfen: was nicht mehr hineinpasst, läuft dort weiter.
  - `ttVerknuepfungLoesen(k)`
  - `menue_ttEinstellungen()` — Einstellungen wie in der Vorlage: die Fenster zum markierten Objekt (Seitenleiste „Formatierung“, Layout, Text).
  - `ttTextBearbeiten(k)`
  - `_tt_gehe(richtung)` — Das vorige/nächste WordArt oder Textfeld des Dokuments markieren (am Ende springt es an den Anfang).
  - `ttVoriges(k)`
  - `ttNaechstes(k)`

### `kern/befehle/kontextreiter/zeichentools.py`

Befehle: Kontext-Reiter „Zeichentools“ für frei positionierte Bilder und Formen: Ausrichten, Drehen, Ebene, Umbruch, Layout, Maße.

- **class `ZeichenToolsBefehle`**
  - `_zeichen()` — (Editor, Ziel) des markierten Bildes oder (Editor, None).
  - `_zeichen_edit()`
  - `menue_zeichenFormstile()`
  - `menue_zeichenFuellung()`
  - `menue_zeichenGliederung()`
  - `menue_zeichenAusrichten()`
  - `menue_zeichenDrehen()`
  - `menue_zeichenEbene()`
  - `zeichenEffekte(k)`
  - `zeichenFormatUebertragen(k)`
  - `zeichenAusrichten(k, wie)`
  - `zeichenDrehen(k, grad)`
  - `zeichenEbene(k, wo)`
  - `zeichenVorn(k)`
  - `zeichenHinten(k)`
  - `zeichenUmbruch(k)`
  - `zeichenLayout(k)`
  - `zeichenMasse(breite_mm, hoehe_mm)`

## `ki`

### `ki/__init__.py`

KI-Ebene: Anbieter, Aufgaben, Dienst.


### `ki/arbeitslauf.py`

Kleine Worker-Hüllen für asynchrone KI-Aufträge.

- **class `_Sig`**(QObject)
- **class `_Lauf`**(QRunnable)
  - `__init__(auftrag, arbeit, sig)`
  - `run()`

### `ki/argos.py`

Lokale Offline-Übersetzung mit argostranslate. Der Text verlässt den Rechner nie.

- `code_fuer(sprache)`
- `erkenne_sprache(text)` — Einfache Erkennung (Schrift, dann Stoppwörter). Bei Unklarheit Deutsch.
- `_fehler(text)`
- `_bibliothek()` — (package, translate) oder None, wenn argostranslate fehlt. Speicherort der Pakete vorher auf einen beschreibbaren Ordner legen.
- `_mitgelieferte_installieren(package)` — Beim ersten Bedarf einmalig alle .argosmodel-Dateien aus den Suchorten installieren (bereits Installierte überspringt Argos nicht,
- `_suche(translate, von, nach)` — Übersetzer von→nach, direkt oder über Englisch; sonst None.
- `uebersetze(text, sprache, quelle)` — {"text": …, "methode": "Lokal"} oder {"fehler": …}. ``sprache`` ist der deutsche Name (oder ISO-Code) der Zielsprache.
- `_name(code)`
- `installierte_richtungen()` — Bereits installierte Richtungen: [{"von", "nach", "name"}]. Leer, wenn Argos fehlt. Kein Netz.
- `verfuegbare_richtungen()` — Noch nicht installierte Richtungen aus dem Argos-Paketindex: {"richtungen": [{"von","nach","name","groesse_mb"}]} oder {"fehler"}.
- `richtung_installieren(von, nach)` — Lädt das Paket von→nach herunter und installiert es. Nur auf ausdrücklichen Wunsch, im Hintergrund; nie automatisch.
- `_netzfehler(e)`

### `ki/assistent_lauf.py`

Fortlaufende KI-Assistenten: reine Regeln ohne Qt — wann ein Absatz neu geschickt wird, wie gedrosselt wird, was ein Ergebnis wert ist.

- `verzoegerung_begrenzen(wert)`
- `absatz_geaendert(zuletzt, jetzt)` — Lohnt eine Anfrage? Nur wenn der Absatz lang genug ist und sich gegenüber dem zuletzt gesendeten Stand wirklich geändert hat.
- `eingabe_kuerzen(text)`
- `ergebnis_wirkt(alt, neu)` — Leer oder (bis auf Leerraum) gleich dem Eingang: keine Wirkung.
- `trenne_begruendung(text)` — (geänderter Text, Begründung); ohne Trenner ist die Begründung leer.
- **class `Drossel`** — Mindestabstand und Höchstzahl je Stunde; die Uhr ist austauschbar (Tests).
  - `__init__(abstand, je_stunde, uhr)`
  - `warten_noch()` — Sekunden bis zur nächsten erlaubten Anfrage (0 = jetzt); ``float('inf')`` heißt: Stundengrenze erreicht.
  - `erlaubt()`
  - `gesendet()`
  - `stundengrenze()`

### `ki/chat_antwort.py`

Chat-Antwort der KI in Einleitung, Kern (der eigentliche Text) und Erklärung teilen. Reine Logik, ohne Qt.

- `_ohne_marke(text)`
- `teilen(text)` — (einleitung, kern, erklaerung); alle drei zusammen ergeben bis auf Marker und Leerraum den Text.
- `strom_text(teil)` — Zwischentext einer laufenden Antwort ohne Marker, auch ohne halb eingetroffene Marker am Ende.
- `felder(text)` — Die Felder ``einleitung``, ``kern``, ``erklaerung`` für eine Nachricht.
- `kern_von(nachricht)` — Kern einer Nachricht; ältere Nachrichten ohne Felder: der ganze Text.

### `ki/chat_bezug.py`

Woran sich eine Chat-Antwort bezieht (Markierung/Schreibmarke zum Sendezeitpunkt) und ob sie noch passt. Reine Logik, ohne Qt.

- `bezug_bauen(von, bis, markiert, revision, alt, dokument, editor_obj, dokument_obj, ganz)` — ``ganz``: ohne Markierung der Dokumenttext zum Sendezeitpunkt (nur für den Vorher/Nachher-Vergleich, nie gesendet oder gespeichert).
- `bezug_angewendet()` — Marke für Aktionen, die ihr Ergebnis selbst schon ins Dokument geschrieben haben (Wirkung „ersetzen“/„anhängen“).
- `bezug_pruefen(bezug, revision_jetzt, editor_jetzt, dokument_jetzt, editor_obj_jetzt)` — (ok, Grund). Gleiche Revision, Editor-Kennung und – sofern erfasst – dieselben Objektidentitäten.
- `vorschau_stuecke(alt, neu)` — Alt → neu als Stücke (art, text); art: „gleich“, „entfernt“, „neu“. Ohne Farben und Markup.
- `_aehnlichkeit(alt, neu)` — Wortähnlichkeit 0..1 (Wörter und Zwischenräume wie in ``ki_diff``).
- `ersetz_schritte(alt, neu)` — Ersetzen als Wortänderungen [(von, bis, text)] in „alt“-Zeichenstellen, von hinten nach vorn — so bleibt die Formatierung des Dokuments
- `vorher_der_nachricht(nachricht, bezug)` — Text der Stelle zum Fragezeitpunkt, mit dem die Antwort verglichen wird: die Markierung (``alt``); ohne Markierung der ganze Dokumenttext (``ganz``),
- `vorschau_der_nachricht(nachricht, bezug)` — Stücke Kern gegen die Stelle aus ``vorher_der_nachricht``; None, wenn es keine gibt. Prüft nicht, ob der Bezug noch passt.
- `vorschau_einfuegen(neu)` — Einfache Vorschau fürs Einfügen: nur der neue Text.

### `ki/chat_modell.py`

Zustand des KI-Chats ohne Oberfläche: Nachrichten, Phase, Anfragekennung, Gesprächsliste. Schicht 1 — kennt weder Dienst noch Qt.

- `fehler_objekt(text)` — Aus einer Fehlermeldung des Dienstes {titel, art, text}; ``art`` steuert die Darstellung.
- `gespraechstitel(text)`
- **class `ChatModell`**
  - `__init__()`
  - `phase()`
  - `titel()`
  - `verlauf()` — Was an die KI geht: ohne Fehler, im Format des Dienstes.
  - `_neu(rolle, text, cent, fehler, bilder, bezug)`
  - `anfrage(text, bilder, bezug)` — Nutzernachricht (mit geprüften Bildanhängen {pfad, typ, bytes}) aufnehmen und eine Anfrage beginnen; liefert deren Kennung.
  - `beginnen(bezug)`
  - `teil_setzen(kennung, text)` — Zwischenstand der Antwort; veraltete Anfragen werden verworfen.
  - `antwort(kennung, text, cent, zusatz)`
  - `fehler(kennung, text)`
  - `aktion(name, text, cent, bezug)` — Ergebnis einer Schnellen KI-Aktion: Verlauf und Anzeige führen dieselben zwei Nachrichten.
  - `bezug_von(index)` — Bezug der KI-Nachricht ``index`` (None, wenn es keinen gibt).
  - `index_von_nr(nr)` — Aktueller Platz der Nachricht mit Kennung ``nr`` (None, wenn sie nicht mehr im Gespräch ist; Nachrichten ohne Feld haben keine).
  - `abbrechen()` — Die Antwort der laufenden Anfrage wird nicht mehr angenommen.
  - `wiederholen()` — Letzte Nutzernachricht erneut senden: davor liegende Antwort/Fehler fällt weg. Liefert den Text oder None; danach ``beginnen()``.
  - `neues_gespraech()`
  - `gespraech_laden(index)`

### `ki/chat_vorschlaege.py`

Welche Aufgaben der Chat vorschlägt — je Zustand (Markierung / Dokument / leeres Dokument). Schicht 1: nur Daten aus ``ki``, kein Qt.

- `_eintrag(id_, konfig)`
- `chat_vorschlaege(auswahl, leer, konfig)` — Immer die zehn Chips der Vorlage. Jeder Eintrag: {id, titel, anweisung, aktiv, hinweis}; ``aktiv`` ist False, wenn der Chip Text braucht und das Dokument leer

### `ki/dokument_abschnitte.py`

Dateien für die Dokumentensuche in Abschnitte zerlegen: ``lesen(pfad) → [(ort, titel, text)]``.

- `_aus_textdokument(doc)`
- `_aus_pdf(pfad)`
- `_aus_txt(pfad)`
- `lesen(pfad)`

### `ki/dokumentensuche.py`

Lokale Dokumentensuche: Dateien aus vom Benutzer freigegebenen Ordnern in Abschnitte zerlegen, mit SQLite FTS5 durchsuchbar machen

- `abschnitte_bilden(zeilen)` — Aus ``(ebene, text)`` je Absatz (ebene > 0 = Überschrift) die Abschnitte ``(titel, text)``: ein neuer Abschnitt beginnt bei jeder Überschrift
- `frage_zu_fts(frage)` — FTS5-Abfrage aus einer Frage in ganzen Sätzen: Füllwörter fallen weg, die übrigen Wörter gelten als Anfang (Wortstamm) und werden mit ODER
- `_ohne_versteckte(namen)`
- `dateien_in(ordner)` — (Pfad, Änderungszeit, Größe) aller lesbaren Dokumente unter ``ordner``; Links werden nicht verfolgt.
- `_bestand(ordner)` — {Pfad: (Änderungszeit, Größe)} aller lesbaren Dateien in den freigegebenen Ordnern.
- `_datei_aufnehmen(db, pfad, stand, lesen)` — Die Abschnitte einer Datei neu in den Index schreiben. → False, wenn sie nicht zu lesen war (sie steht dann ohne Abschnitte im Index:
- **class `Index`** — SQLite-Datei mit der Tabelle ``dateien`` (Stand je Datei) und der FTS5-Tabelle ``abschnitte``. Jede Methode öffnet die Verbindung selbst:
  - `__init__(pfad)`
  - `_db()`
  - `aktualisieren(ordner, lesen, zeitgrenze, abbruch)` — Neue und geänderte Dateien lesen, entfernte (und nicht mehr freigegebene) vergessen. ``lesen(pfad)`` liefert ``[(ort, titel, text)]``
  - `suchen(frage, ordner, anzahl)` — [{datei, pfad, ort, titel, text}] der besten Abschnitte, nur aus Dateien unterhalb der freigegebenen ``ordner``.
  - `anzahl()` — (Dateien, Abschnitte) im Index.
- `fundstelle(t)`
- `als_text(treffer)` — Die Auszüge als nummerierte Quellenliste für die Anweisung an die KI.
- `fundstellen_zeilen(treffer)` — Kurzliste für die Anzeige unter der Antwort.

### `ki/ki.py`

Die KI-Ebene: Korrigieren, Vorschläge, Übersetzen, Zusammenfassen, Text bearbeiten, Chat.

- `als_geld(cent)`
- **class `KI`**
  - `__init__(konfig, gelernt)`
  - `modell(aufgabe)`
  - `verfuegbar()`
  - `verfuegbar_fuer(aufgabe)` — Wie ``verfuegbar``, aber für das Modell der Aufgabe: argos: und auto: gehen auch ohne Standardmodell (lokal).
  - `schickt_nach_aussen(modell)` — Name des Empfängers, wenn der Text das Gerät verlässt — sonst None.
  - `_ollama_faehigkeiten(name, warten)` — Fähigkeiten laut Ollama (/api/show → capabilities), mit Zwischenspeicher. ``warten=False``: nur aus dem Speicher, sonst im
  - `_ollama_faehigkeiten_holen(name)`
  - `faehigkeit(modell, warten)` — (denken, bild) für die Modellkennung (claude-…, ollama:…, eigen:…). Mit ``warten=False`` nie blockierend.
  - `kann_bild(modell)` — Für die Oberfläche: nie blockierend; während die Abfrage bei Ollama läuft (oder scheitert) False.
  - `kann_denken(modell)`
  - `websuche_ziel()` — Wohin die Frage der Websuche geht, wenn das nicht dieser Rechner ist (Brave oder eine nicht lokale Adresse), sonst None.
  - `zustimmung_fehlt(modell, umfang)` — Sperre an der Sendestelle: Geht der Text an einen Dienst außerhalb dieses Rechners und liegt dafür keine Einwilligung vor, kommt eine
  - `anfrage(anweisung, text, bauplan, modell, optionen)`
  - `_claude(anweisung, text, bauplan, modell, optionen)`
  - `_ollama(anweisung, text, bauplan, modell, optionen)`
  - `_eigen(a, anweisung, text, bauplan, optionen)`
  - `_text(anweisung, text, aufgabe, optionen)`
  - `_kosten(cent)`
  - `korrigieren(text)`
  - `uebersetzen(text, sprache)` — Je nach Modell der Aufgabe: Argos (lokal), KI oder Automatisch (KI wenn eingeschaltet, erlaubt und erreichbar, sonst lokal;
  - `_uebersetzen_ki(text, sprache, modell)`
  - `zusammenfassen(text)`
  - `text_analyse(text)`
  - `eigener_assistent(text, prompt, kommentar, modell, nur_kommentar, optionen)` — ``kommentar``: die KI begründet ihre Änderung nach ``KOMMENTAR_ZUSATZ``; ``nur_kommentar``: sie antwortet nur mit einem Kommentar;
  - `satz_umschreiben(satz, grund)` — Ein zu langer oder verschachtelter Satz in kürzere Sätze — der Sinn bleibt, nichts kommt dazu.
  - `text_aktion(text, aktion)`
  - `chat(verlauf, dokumenttext, markiert, strom, abbruch)` — ``markiert``: ``dokumenttext`` ist nur die Markierung (Umfang „auszug“ genügt), sonst das ganze Dokument („dokument“).
  - `_chat_optionen(strom, abbruch)`
  - `_chat_ziel(modell)` — (Adresse, Modellname beim Anbieter, Kopfzeilen) für den Chat mit Werkzeugen; None, wenn der eigene Anbieter fehlt.
  - `_chat_werkzeuge(system, verlauf, server, modell, optionen)` — Chat mit MCP-Werkzeugen über die OpenAI-kompatible Schnittstelle (Ollama und eigene Anbieter), siehe ``ki_werkzeugschleife``.
  - `vorschlaege(text)`
  - `synonyme(wort, umgebung)` — Wörter, die statt `wort` an dieser Stelle stehen könnten (Thesaurus — geht nur mit KI).
  - `bild_erzeugen(beschreibung)` — Bild aus Text: nur eigene Anbieter mit „Bilder“, siehe ``ki_bildgenerierung``.
  - `ollama_modelle()`
- `anbieter_modelle(url, schluessel)` — GET <URL>/models — so fragen OpenAI und die meisten OpenAI-kompatiblen Dienste (auch Ollama unter /v1).

### `ki/ki_aktionen.py`

KIAktionen: fachlich abgegrenzte KI-Dienstlogik.

- **class `KIAktionenMixin`** — Teilverantwortung des KI-Dienstes; wird von KIDienst eingebunden.
  - `korrigieren()`
  - `uebersetzen(sprache, modus)` — Übersetzen in die gewählte Sprache. ``modus``: „ersetzen“ setzt die Übersetzung an die Stelle der Markierung, „zeigen“ zeigt sie in der Schreibhilfe
  - `_methode(r)`
  - `text_aktion(aktion)`
  - `assistent(a)` — Schnelle KI-Aktion (Eigener Assistent): ein Name und ein Prompt. Wirkung „ersetzen“ wie Korrigieren, „anhaengen“ hinter den Text, „hinweis“ wie
  - `zusammenfassen()`
  - `analyse()`
  - `vorschlaege_holen()`
  - `thesaurus(danach)` — Synonyme zum Wort am Zeiger; danach(wort, woerter, von, bis) im Hauptthread.
  - `satz_vorschlag(fund, danach)` — Zu einem Hinweis („Langer Satz …“) einen Umschreibe-Vorschlag holen; ``danach(vorschlag)`` bekommt {alt, neu, grund} im Hauptthread.
  - `vorschlag_aktuell(v)` — Prüft den Herkunftsbezug, auch wenn ein Vorschlag nur verworfen werden soll.
  - `vorschlag_einsetzen(v)`

### `ki/ki_anfragen.py`

KIAnfragen: fachlich abgegrenzte KI-Dienstlogik.

- **class `KIAnfragenMixin`** — Teilverantwortung des KI-Dienstes; wird von KIDienst eingebunden.
  - `_werkzeug_erlaubt(name, argumente, server, art)` — Aus dem Arbeitsfaden: fragt im Hauptfenster, ob die KI das Werkzeug aufrufen darf, und wartet auf die Antwort.
  - `_werkzeug_fragen(name, argumente, server_art)`
  - `_server_erlaubt(name, befehl)` — Aus dem Arbeitsfaden: zeigt den vollständigen Startbefehl des MCP-Servers und fragt vor dem Start (ein Programm auf diesem Rechner).
  - `_hinweis_fenster(titel, text)` — Ein Hinweis, den man nicht übersehen kann (statt nur einer Zeile in der Statusleiste).
  - `merke_ergebnis(titel, text, vorlage)`
  - `beschaeftigt()`
  - `chat_beschaeftigt()` — Für die Chat-Eingabe: ein fortlaufender Assistent im Hintergrund sperrt sie nicht (``dauer_verdraengen`` räumt ihn beim Senden weg).
  - `kontext_pruefen()` — Von Editor-Signalen gerufen: ``kontextGeaendert`` nur, wenn sich Markierung oder Leer-Sein wirklich geändert haben.
  - `_bezug_stand()` — Nur wenn eine Antwort mit Bezug im Chat steht: (Editor, Revision), damit die Oberfläche „Ersetzen/Einfügen“ neu bewertet.
  - `kontext()` — (Markierung da, Dokument leer, Modell für den Chat verbunden, Name des Chat-Modells) aus Editor und Konfiguration.
  - `verfuegbar()`
  - `zettel(text)`
  - `_einwilligung(modell, umfang, zeichen)` — Fragt vor dem ersten Senden an einen Dienst im Internet. Gespeichert wird je Anbieter und Umfang („auszug“ oder „dokument“), mit Datum;
  - `_eingabe()`
  - `starte(meldung, arbeit, danach, eing, aufgabe, modell)` — arbeit(text) → Ergebnisdict (im Hintergrund); danach(ergebnis, eingabe) im Hauptthread.
  - `_eingabe_binden(eing, meldung)` — Der Eingabe ihr Dokument (für die Prüfung beim Zurückkommen) und den Titel der Aufgabe mitgeben. → False, wenn der Editor schon weg ist.
  - `_fertig(auftrag, r)` — Ergebnis einer Hintergrundanfrage im Hauptthread: ``danach`` ist „bild“, „dauer“, „chat“ oder die Funktion der Textaufgabe.
  - `_fertig_bild(r, eing)` — Das erzeugte Bild nur einfügen, wenn Dokument und Schreibposition noch die vom Sendezeitpunkt sind.
  - `_fertig_chat(r, eing)`
  - `_fertig_text(danach, r, eing)`
  - `_eingabe_gueltig(eing)` — Nur Antworten für den aktiven Editor, das Dokument und die Revision vom Sendezeitpunkt dürfen weiterlaufen.
  - `bild_aus_text(beschreibung)` — Markierter Text (oder der übergebene) ist die Bildbeschreibung; das Bild tritt an die Stelle der Markierung.
  - `_bild_fertig(r, eing)`
  - `_preis(cent)`
  - `_einsetzen(r, eing, ganz_text, markiert_text)`
  - `_anhaengen(r, eing, name)` — Das Ergebnis hinter die Markierung (ohne Markierung: ans Ende des Textes) setzen — als ein Schritt für Rückgängig.

### `ki/ki_anweisungen.py`

Prompt-Vorlagen und Anweisungen für KI-Textaufgaben.

- `_zettel(z)`
- `steckbrief(gelernt)`
- `anweisung_korrektur(k, gelernt)`
- `anweisung_uebersetzung(sprache)`
- `anweisung_vorschlaege(k)`
- `anweisung_text_aktion(k, aktion)`

### `ki/ki_bildgenerierung.py`

Bild aus Text: nur eigene Anbieter mit „Bilder“, OpenAI-Schnittstelle POST <URL>/images/generations.

- `anbieter_pruefen(konfig, modell)` — (Anbieter, None) oder (None, Fehler).
- `_bild_aus(a, daten)`
- `_http_fehler(a, e)`
- `erzeugen(a, beschreibung)`

### `ki/ki_chat.py`

KIChat: fachlich abgegrenzte KI-Dienstlogik.

- **class `KIChatMixin`** — Teilverantwortung des KI-Dienstes; wird von KIDienst eingebunden.
  - `chat_senden(text, bild)` — Neue Nutzernachricht in ``chat_modell`` aufnehmen und senden. False, wenn nichts gesendet wurde (leer, beschäftigt, keine Zustimmung).
  - `denktiefe()`
  - `denktiefe_setzen(stufe)`
  - `werkzeugmodus()`
  - `werkzeugmodus_setzen(modus)` — „fragen“ oder „automatisch“. „automatisch“ gilt nur für diese Sitzung (``KIKonfig.speichern`` schreibt es nie) und nur für Lesen und
  - `kann_bild()`
  - `kann_denken()`
  - `werkzeuge_vorhanden()` — MCP-Server an UND ein Modell, das Werkzeuge im Chat nutzt (Ollama oder eigener Anbieter, nicht Claude).
  - `bild_hinweis()`
  - `denken_hinweis()`
  - `werkzeuge_hinweis()`
  - `chat_wiederholen()` — Die letzte Nutzernachricht erneut senden; die davorliegende Antwort/der Fehler fällt weg.
  - `chat_neu()`
  - `chat_abbrechen()` — Eine laufende Antwort wird nicht mehr angezeigt. Der Hintergrundfaden selbst lässt sich im Thread-Pool nicht unterbrechen und läuft aus.
  - `_aktion_bezug(eing)` — Bezug einer Aktion aus ihrer Eingabe (Editor, Text, Basis, Revision zum Start); ganzes Dokument: Einfügen am Ende, kein Ersetzen.
  - `aktion_in_chat(name, text, cent, bezug)`
  - `_chat_anfragen(aufnehmen)`
  - `chat_bezug()` — Stelle im Text zum SENDEZEITPUNKT: Markierung (markiert=True) oder Schreibmarke; None ohne Editor. Nur im Speicher.
  - `_bezug_lage(index)` — (Bezug, Editor, Grund). Editor nur, wenn Bezug und aktueller Editor noch zusammenpassen.
  - `bezug_gueltig(index, ersetzen)` — Für die Oberfläche: darf die Antwort ``index`` jetzt eingefügt (bzw. ersetzt) werden? (ok, Grund).
  - `rezension_gueltig(index)` — Für die Oberfläche: darf die Antwort ``index`` als nachverfolgte Änderungen eingetragen werden? (ok, Grund).
  - `antwort_vorschau(index, ersetzen)` — Vorschau als [(art, text)] (gleich/entfernt/neu); leer, wenn nichts anzuwenden ist.
  - `antwort_diff(index)` — Für die Oberfläche: Stücke [(art, text)] Kern gegen die beim Fragen markierte Stelle, ohne Klick; None, wenn der Bezug ungültig ist oder (ohne Markierung) die Antwort keine Überarbeitung des Dokuments ist.
  - `antwort_index(nr)` — Kennung (``nr``) einer Nachricht → aktueller Index im Chat; None, wenn sie nicht mehr da ist.
  - `antwort_lage(index)` — Alles für das Vergleichsfenster in einem Aufruf: {gueltig, nr, vorher, nachher, stuecke, einfuegen, ersetzen, rezension}.
  - `antwort_einfuegen(index)` — Antwort ``index`` hinter der gemerkten Stelle einfügen (ein Schritt für Rückgängig). → (ok, Meldung); bei Ablehnung wird nichts geändert.
  - `antwort_ersetzen(index)` — Die beim Fragen markierte Stelle durch die Antwort ersetzen (ein Schritt); ohne Markierung das ganze Dokument, wenn die Antwort es überarbeitet. Nur bei unverändertem Text. → (ok, Meldung).
  - `antwort_rezension(index)` — Die Überarbeitung als nachverfolgte Änderungen (Autor „KI“) eintragen: Altes bleibt durchgestrichen stehen, Neues ist markiert (ein Schritt für Rückgängig).
  - `_antwort_anwenden(index, ersetzen, rezension)`
  - `_chat_bereit()` — Modell da und Zustimmungen erteilt? Bei Markierung gilt der Umfang „auszug“, sonst „dokument“ (die Sperre an der Sendestelle bleibt).
  - `_chat_los(verlauf, kennung)` — Kontext des Chats: die Markierung, wenn es eine gibt (weniger Text verlässt den Rechner), sonst das Dokument.
  - `_chat_teil(kennung, text)`

### `ki/ki_chat_kontext.py`

Was dem Chat vor dem Senden mitgegeben wird: Systemtext mit Dokument, Websuche, Dokumentensuche, Bildanhänge; und die Nachbearbeitung der Antwort.

- `system_text(ki, dokumenttext)`
- `sperre(ki, modell, verlauf, dokumenttext, markiert)` — Fehlende Zustimmung (Text, dann Bildinhalt) als Wörterbuch, sonst None. ``markiert``: nur die Markierung geht raus.
- `bilder(ki, modell, verlauf)` — (Verlauf mit gelesenen Bildern, Fehler oder None). Lesen und Base64 erst hier, im Arbeitsfaden.
- `websuche(ki, verlauf)` — (Zusatz für den Systemtext, Notiz für den Benutzer).
- `dokumentensuche(ki, verlauf, modell)` — (Zusatz für den Systemtext, Notiz, Fundstellen).
- `abschliessen(r, quellen, notiz)` — Kürzungshinweis, Fundstellen und Notiz als eigene Felder (``kuerzung``, ``fundstellen``, ``notiz``) neben ``text`` legen.

### `ki/ki_claude.py`

Claude (Anthropic-API): Anfrage bauen, senden, Antwort und Fehler lesen. Die Adresse kommt vom Aufrufer (``ki.CLAUDE_URL``).

- `cent_fuer(modell, verbrauch)`
- `_ausgabe_einstellungen(modell, bauplan, optionen)`
- `bitte_bauen(anweisung, text, bauplan, modell, optionen)`
- `_meldung(e)`
- `fehler_http(e)`
- `antwort_lesen(daten, modell)`
- `anfrage(url, schluessel, anweisung, text, bauplan, modell, optionen)`

### `ki/ki_dauerbetrieb.py`

KIDauerbetrieb: fachlich abgegrenzte KI-Dienstlogik.

- **class `KIDauerbetriebMixin`** — Teilverantwortung des KI-Dienstes; wird von KIDienst eingebunden.
  - `dauerbetrieb()` — Hauptschalter: nur wenn er an ist, läuft irgendein fortlaufender Assistent.
  - `_dauer_einwilligung(modell)` — Klartext-Frage (nur bei Anbietern außerhalb dieses Rechners): „Sendet bei jeder Änderung den geänderten Absatz an <Anbieter>“.
  - `dauerbetrieb_setzen(an)` — Hauptschalter ein-/ausschalten; False, wenn das Einschalten abgelehnt wurde oder nicht möglich ist.
  - `assistent_an_setzen(id_, an)` — Einen fortlaufenden Assistenten an-/ausschalten (läuft erst, wenn auch ``dauerbetrieb()`` an ist); False bei Ablehnung.
  - `_dauer_aus(a, grund)` — Fehler oder fehlende Erlaubnis: den Assistenten ausschalten und es sagen — nie stumm wiederholen.
  - `dauer_geaendert(art)` — Von Dokument-/Markierungssignalen gerufen (oberflaeche/programmfenster.py): startet die Ruhezeit des Assistenten neu.
  - `_dauer_eingabe(a)`
  - `_dauer_editor_passt()` — Der Timer gehört zu dem Editor, dessen Änderung ihn ausgelöst hat; ein Tabwechsel darf keinen Assistenten im neuen Tab starten.
  - `_dauer_drossel_frei()` — False, wenn die Drossel noch wartet (Timer neu gestellt) oder die Stundengrenze erreicht ist (Pause gemeldet).
  - `_dauer_erlaubt(a, modell)` — Modell eingerichtet und Erlaubnis vorhanden? Sonst wird der Assistent mit Meldung ausgeschaltet.
  - `_dauer_starten(a, eing, schluessel, modell)`
  - `dauer_verdraengen()` — Interaktive Anfragen (Chat) haben Vorrang: einen laufenden fortlaufenden Assistenten abbrechen und sein Ergebnis verwerfen.
  - `_dauer_nach_vorrang()` — Nach der interaktiven Anfrage: den verdrängten Assistenten wieder einplanen.
  - `_dauer_los()` — Nach der Ruhezeit: den ersten fälligen Assistenten starten (die übrigen kommen nach seinem Ergebnis dran).
  - `_dauer_fertig(r, eing)`
  - `_dauer_kommentar(ed, eing, text, autor)`
  - `_dauer_ersetzen(a, eing, text, begruendung, r)` — Ersetzen nur nach Bestätigung; ein Undo-Schritt (``_einsetzen``).

### `ki/ki_dienst.py`

Öffentliche Fassade des KI-Dienstes; Fachlogik liegt in eigenen Mixins.

- **class `KIDienst`**(KIAnfragenMixin, KIAktionenMixin, KIDauerbetriebMixin, KIChatMixin, QObject)
  - `__init__(assistant, fenster, parent)`

### `ki/ki_diff.py`

Wortgenaue Änderungen zwischen KI-Ergebnis und Ausgangstext.

- `aenderungen(alt, neu)` — Welche Wörter haben sich geändert? → [{von, bis, text}] in „alt"-Zeichenstellen; None, wenn zu groß.
- `ersetze_ergebnis(alt, neu)` — → (liste_von_ersetzungen (von, bis, text) von hinten nach vorn, ganz: bool, absaetze).

### `ki/ki_eigen.py`

Eigener Anbieter (OpenAI-kompatible Schnittstelle): Anfrage bauen, senden, Antwort lesen.

- `_optionen_uebernehmen(bitte, o)`
- `bitte_bauen(a, anweisung, text, bauplan, optionen)`
- `antwort_lesen(daten)`
- `_senden(a, bitte)`
- `anfrage(a, anweisung, text, bauplan, optionen)`

### `ki/ki_konfiguration.py`

Konstanten, Assistentenvorlagen und persistente KI-Konfiguration.

- `assistent_normiert(a)` — Ein Assistenteneintrag mit allen Feldern und gültigen Werten; fehlende Felder (ältere Einträge) bekommen ihre Vorgabe.
- **class `KIKonfig`**
  - `__init__(pfad)`
  - `speichern()`
  - `__getitem__(k)`
  - `setze(k, v)`
  - `einwilligungen()` — [{anbieter, umfang, seit}]; ältere Einträge (nur der Name) gelten als Umfang „dokument“, wie damals gefragt wurde.
  - `hat_einwilligung(anbieter, umfang)` — „dokument“ schließt „auszug“ ein, nicht umgekehrt; „bild“ wird von keinem anderen Umfang abgedeckt.
  - `einwilligung_geben(anbieter, umfang)`
  - `einwilligung_widerrufen(anbieter, umfang)` — Ohne Angaben: alle. Mit ``anbieter`` (und ``umfang``): nur diese.
  - `anbieter_holen(id_)`
  - `anbieter_hinzufuegen(name, url, schluessel, modell, verwendung)`
  - `anbieter_aktualisieren(id_, name, url, schluessel, modell, verwendung)`
  - `chat_optionen()` — Die erweiterten Einstellungen des KI-Chats (Länge, Temperatur, Top P, Stoppfolgen, Antwort direkt einfügen) mit ihren Vorgaben.
  - `websuche_optionen()`
  - `dokumentsuche_optionen()` — Lokale Dokumentensuche: ``an``, freigegebene ``ordner`` (nur existierende, absolut), ``anzahl`` der Abschnitte je Frage.
  - `dokumentsuche_setzen(**teile)`
  - `dokumentindex_pfad()`
  - `websuche_setzen(**teile)`
  - `mcp_speichern(id_, name, befehl, an)` — MCP-Server anlegen (``id_`` None) oder ändern.
  - `suchdienst_eintragen()` — Die Dokumentensuche als KI-Werkzeug (MCP-Server ``ki/suchdienst.py``) eintragen oder aktualisieren — mit den jetzt freigegebenen Ordnern.
  - `mcp_entfernen(id_)`
  - `chat_setzen(**teile)`
  - `aufgabe_setzen(aufgabe, modell)`
  - `assistent_hinzufuegen(name, prompt, modus, zugriff, **mehr)` — Eine „Schnelle KI-Aktion“ (art „aktion“): ``modus`` = ersetzen \| anhaengen \| hinweis; ``zugriff`` = kontext (Rechtsklick-Menü) \| schnell
  - `assistent_holen(id_)`
  - `assistent_aendern(id_, **teile)` — Felder eines Assistenten ändern (der Eintrag bleibt dasselbe Objekt, Werte werden geprüft).
  - `assistenten(art)` — Alle Assistenten (``art`` None) oder nur die einer Art; ältere Einträge ohne Art gelten als „aktion“.
  - `assistent_entfernen(id_)`
  - `anbieter_entfernen(id_)`
  - `alle_modelle()` — Eine Liste für alle Felder „welches Modell?“: Claude, eigene Anbieter (mit Fähigkeiten und ‚lokal‘).
- `ist_lokale_url(url)` — Nur der Rechner selbst: der Rechnername wird aus der Adresse gelesen (nicht per Muster), damit „http://127.0.0.1:80@fremd.de“ nicht durchgeht.

### `ki/ki_ollama.py`

Ollama (läuft auf diesem Rechner): Tempo-Einstellungen, Anfrage bauen, senden, Antwort und Strom (NDJSON) lesen.

- `_leer()`
- `keep_alive_begrenzen(wert)`
- `num_thread_begrenzen(wert)` — 0 = automatisch; sonst 1 bis zur Zahl der logischen Kerne dieses Rechners.
- `num_ctx_begrenzen(wert)`
- `num_predict_fuer(eingang_zeichen, chat, denkt, gesetzt)` — Antwortgrenze: ausdrücklich gesetzt (Chat-Einstellung) gilt immer; sonst Chat 1024, Überarbeitung nach Länge des Eingangs
- `num_ctx_fuer(eingestellt, zeichen, vorhersage)` — Eingestellte Größe, aber nie kleiner als Gespräch plus Antwort brauchen — der Verlauf wird nie abgeschnitten.
- `_optionen_bauen(o, einst, zeichen, denkt)`
- `bitte_bauen(modell, anweisung, text, bauplan, o, einst, strom)`
- `_http_fehler(e, bitte, modell)` — Fehlertext als Wörterbuch; None = „think“ wurde entfernt, noch einmal senden.
- `antwort_lesen(daten)`
- `_senden(url, bitte, strom, abbruch, modell)`
- `anfrage(url, einst, anweisung, text, bauplan, modell, optionen)` — ``einst``: Chat-Einstellungen (keepAlive/numCtx/numThread/streaming gelten für alle Ollama-Aufgaben).
- `_abgebrochen(abbruch)`
- `_json_teil(zeile)` — Eine Zeile des Stroms als Wörterbuch; leere, kaputte und fremde Zeilen sind None.
- **class `_Strom`** — Sammelt den Text des Stroms; ``strom(text)`` bekommt den bisherigen Text (ohne Grübeln), gedrosselt.
  - `__init__(strom)`
  - `zeile(zeile)` — Fehler als Wörterbuch, sonst None.
  - `_inhalt(teil)`
  - `ergebnis()`
- `strom_lesen(r, strom, abbruch)` — Liest die Antwortzeilen (NDJSON) von Ollama; ``abbruch`` (threading.Event) beendet die Verbindung sofort.

### `ki/ki_textaktionen.py`

Auswertung der KI-Antworten für Vorschläge und Synonyme (Thesaurus): Antwort lesen, prüfen, bereinigen. Die Anfrage selbst stellt ``KI``.

- `anweisung_synonyme(wort)`
- `liste_lesen(roh, schluessel)` — Die Liste unter ``schluessel`` aus der Antwort, oder None, wenn die Form nicht stimmt.
- `_vorschlag_gueltig(v, text)` — Nur, was sich zeichengenau im Text wiederfindet, lässt sich einsetzen.
- `vorschlaege_bereinigen(lst, text)`
- `synonyme_bereinigen(lst, wort)`

### `ki/ki_transport.py`

Gemeinsames der Anbieter-Anfragen: HTTP-Aufruf, Antwort als Wörterbuch, Nachrichten- und Bildformat, Denkstufe, Stoppwörter.

- `json_dict(r)` — Antwort eines Anbieters als Wörterbuch. Alles andere (kein JSON, keine Zeichenfolge, Liste statt Objekt) ist ein ValueError und wird als
- `post(url, kopf, body, timeout)` — Sendet über ``ki._post`` (so bleibt der Transport für Tests und Anbindungen austauschbar).
- `post_roh(url, kopf, body, timeout)`
- `bearer_kopf(schluessel)` — Kopfzeile für OpenAI-kompatible Anbieter (leer, wenn kein Schlüssel eingetragen ist).
- `stufe(optionen)`
- `stopp_liste(optionen)`
- `erste_nachricht(daten)` — ``choices[0].message`` einer OpenAI-kompatiblen Antwort, sonst ein leeres Wörterbuch.
- `json_nach_marken(roh)` — JSON aus einer Modellantwort, auch wenn sie in ```-Marken steht.
- `ohne_gruebeln(roh)`
- `bild_block(b, anbieter)` — Ein Bildanhang im Format des Anbieters: „claude“, „ollama“ oder „openai“ (eigene Anbieter). ``b["b64"]`` ist beim Senden schon gelesen.
- `_bild_inhalt(text, bilder, anbieter)`
- `nachricht(z, anbieter, letzte)`
- `nachrichten(text, anbieter)`
- `bilder_lesen(verlauf)` — Liest und kodiert (Base64) nur die Bilder der LETZTEN Nachricht, erst beim Senden. Liefert (Kopie des Verlaufs, Fehlertext).

### `ki/ki_werkzeugschleife.py`

Chat mit MCP-Werkzeugen über die OpenAI-kompatible Schnittstelle (Ollama und eigene Anbieter): Das Modell darf Werkzeuge verlangen; jeder

- **class `_Sitzung`** — Die gestarteten Werkzeug-Server und ihre Werkzeuge (``wo``: Name -> (Client, Werkzeugname, Servername, Art)).
  - `__init__()`
  - `starten(ki, server)` — Startet jeden erlaubten Server. Fehler als Wörterbuch, sonst None.
  - `_erlaubnis(ki, sv)`
  - `_werkzeuge_aufnehmen(c, servername)`
  - `schliessen()`
- `_bitte(name, nachrichten, tools, optionen, effort)`
- `_senden(url, kopf, bitte, effort)` — (Antwort, Denktiefe). Kennt das Modell keine Denktiefe (400), geht es ohne sie noch einmal — dauerhaft für dieses Gespräch.
- `_aufrufe(msg)`
- `_argumente(f)`
- `_ausfuehren(ki, ziel, arg, modus)`
- `_tool_antwort(ki, wo, aufruf, modus)`
- `_runden(ki, sitzung, system, verlauf, ziel, optionen)`
- `_fehler_http(e, verlauf)`
- `chat(ki, system, verlauf, server, ziel, optionen)` — ``ziel``: (Adresse der Chat-Schnittstelle, Modellname beim Anbieter, Kopfzeilen).

### `ki/mcp.py`

MCP-Server (Model Context Protocol) über die Standard-Ein-/Ausgabe: Werkzeuge auflisten und aufrufen.

- **class `McpFehler`**(Exception)
- **class `McpClient`**
  - `__init__(befehl)`
  - `_starten()`
  - `_neu()`
  - `_lesen()`
  - `_senden(nachricht)`
  - `_antwort(nr)`
  - `werkzeuge()` — [{name, description, inputSchema}] des Servers.
  - `aufrufen(name, argumente)`
  - `schliessen()`
- `pruefen(befehl)` — Verbindung testen: die Werkzeuge des Servers (für „Testen“ im Fenster KI-Einstellungen).
- `art_des_werkzeugs(werkzeug)` — Grobe Einstufung eines Werkzeugs für die Rückfrage: „lesen“, „schreiben“, „löschen“, „netzwerk“ oder „unbekannt“.

### `ki/modellfaehigkeit.py`

Was ein KI-Modell kann und was erlaubt ist — reine Logik ohne Qt. Schicht 1: kennt weder Dienst noch Oberfläche.

- `denkstufe(schluessel)`
- `claude_faehig(modell)` — (denken, bild) für ein Claude-Modell.
- `bildtyp_aus_inhalt(kopf)` — Medientyp nach den ersten Bytes der Datei (nicht nach der Endung).
- `bild_pruefen(pfad)` — Prüft einen Bildanhang. Liefert {pfad, typ, bytes} oder {fehler}.
- `werkzeug_erlaubt(modus, art)` — Darf ein Werkzeug dieser Art ohne Rückfrage laufen? Nur im Modus „automatisch“ und nur für Lesen und Schreiben.

### `ki/suchdienst.py`

Die lokale Dokumentensuche als MCP-Server (Standard-Ein-/Ausgabe, JSON-RPC 2.0, eine Nachricht je Zeile).

- `_text(t, fehler)`
- `aufrufen(name, argumente, index, ordner)`
- `behandle(nachricht, index, ordner)` — Antwort auf eine Nachricht; ``None`` für Benachrichtigungen (ohne ``id``).
- `main(argv)`

### `ki/websuche.py`

Websuche für den KI-Chat: Treffer holen und als Quellenliste an die Frage hängen.

- `suche(einst, frage, zeit)` — [{titel, url, text}] zur Frage; Fehler werden als Ausnahme gemeldet (OSError, ValueError).
- `als_text(treffer)` — Die Treffer als Quellenliste für die Anweisung an die KI.

## `korrektur`

### `korrektur/__init__.py`

Schreibhilfe: Prüfregeln, Vorhersage, Autokorrektur, Barrierefreiheit, Silben.


### `korrektur/autokorrektur.py`

AutoKorrektur beim Tippen. Greift erst, wenn ein Wort abgeschlossen ist.

- `_ordnung(m)`
- `korrigiere(text, an)`
- `kleinste_aenderung(alt, neu)` — → (von, bis, ersatz): nur der Abschnitt, der sich wirklich ändert — Formatierung bleibt sonst unberührt.

### `korrektur/barrierefreiheit.py`

Barrierefreiheit prüfen — was Menschen mit Sehbehinderung den Text unlesbar macht.

- `_hell(c)`
- `kontrast(vorne, hinten)`
- `_bild_ohne_alt(o)` — Ein Objekt (``InlineObjekt`` oder ``FreiesObjekt``) ohne Alternativtext; dekorative brauchen keinen.
- `_text_durchsuchen(dok, seite)` — Durchläuft alle Absätze: (Zähler, Überschriftenebenen, Wortzahl).
- `_ueberschriften_funde(ebenen, woerter)`
- `_link_fund(n)`
- `pruefe(editor)`
- `_tabellen(dok)` — Alle Tabellen des Dokuments (auch geschachtelte) in Dokumentreihenfolge.

### `korrektur/fund.py`

Herkunft und Sicherheit eines Fundes; Auflösung, wenn mehrere Quellen dieselbe Stelle melden.

- `klemmen(wert, vorgabe)`
- `markieren(funde, quelle, text_laenge)` — Funde gegen den Datenvertrag ``ProofingIssue`` prüfen (ungültige fallen weg; Wörterbücher von außen werden umgewandelt), dann Quelle und
- `_rang(f)`
- `loesen(funde)` — Überschneidende Funde auflösen: der beste bleibt, die unterlegenen werden nicht angezeigt, aber als `verdraengt` vermerkt.
- `_bestaetigen(f)` — Punkt a): Quellen mit gleichem Vorschlag bestätigen den Fund und heben seine Konfidenz.
- `_konsens(f)` — Punkte a) und b): Bestätigung durch andere Quellen, ein abweichender Vorschlag macht aus „fehler“ einen „tipp“.
- `_gegenprobe_faellig(f, geprueft)` — Punkt c): unbestätigter, unsicherer Fehler, den eine andere Quelle im ganzen Bereich geprüft und nicht beanstandet hat.
- `abstimmen(funde, geprueft, in_ruhe, selbst, gegenprobe)` — Konsens zwischen den Quellen nach ``loesen`` (reine Funktion, idempotent).

### `korrektur/haeufig.py`

Häufige deutsche Wörter.


### `korrektur/inkrement.py`

Inkrementelle Prüfung: nur die geänderte Stelle (plus Sicherheitsbereich) neu prüfen, den Rest verschieben und behalten.

- `verschieben(funde, pos, entfernt, hinzu)` — Funde nach einer Änderung (pos, entfernt, hinzugefügt) umrechnen. Betroffene Funde entfallen.
- `schmutz_abbilden(bereich, pos, entfernt, hinzu)` — Den bisher ungeprüften Bereich in die neuen Positionen umrechnen und um die neue Änderung erweitern.
- `pruefbereich(text, a, b, absaetze)` — Den geänderten Bereich auf ganze Absätze samt Sicherheitsbereich erweitern.
- `lohnt(laenge, von, bis)`
- `einsetzen(alt, von, bis, neue_relativ)` — Funde im Bereich [von, bis) durch die neuen (Positionen relativ zum Bereich) ersetzen.

### `korrektur/klang.py`

Vorschläge für ein einzelnes Wort (Rechtsklick-Menü): Klangvergleich über die Kölner Phonetik und Rangfolge.

- `_pruefung()`
- `_klangtafel()`
- `_gewicht(w, k)`
- `klingt_wie(wort, hoechstens)`
- `_rang(w, k, eigen, klang_gleich)`
- `_treffer_sammeln(w, woerter, gelernt)` — Nachbarwörter, dann Klanggleiche, ein selbst Gelerntes zuvorderst. Liefert (Treffer, eigen).
- `vorschlaege_fuer(wort, hoechstens, gelernt)`

### `korrektur/korrektur_dienst.py`

Die Schreibhilfe: prüft im Hintergrund, hält den Stand, setzt Korrekturen ein.

- **class `_Signale`**(QObject)
- **class `_Lauf`**(QRunnable)
  - `__init__(rev, text, gelernt, signale, dokument, schalter)`
  - `run()`
- **class `WritingAssistant`**(QObject)
  - `__init__(settings, gelernt, parent)`
  - `an(name)`
  - `setze(name, wert)`
  - `setze_thema(name)`
  - `ak_an(name)`
  - `attach(editor)`
  - `_geaendert(pos, entfernt, hinzu)` — Bereichs-Invalidierung: Funde hinter der Änderung verschieben, Funde an der Änderung verwerfen, Bereich merken.
  - `dokument_geaendert()`
  - `pruefen(zaehlen, voll)` — zaehlen=True nur bei ausdrücklichem Prüfen (Knopf): dann zählt das Gedächtnis mit und es wird alles geprüft.
  - `pruef_schalter()` — Die Schalter für `pruefung.finde_probleme`: Optionen der Rechtschreibung und je Prüfer „schreibhilfe/pruefer_<name>“.
  - `_fertig_veraltet(rev, doc)` — Der Text (oder das Dokument) hat sich seit dem Start der Prüfung geändert.
  - `_eigene_funde_uebernehmen(roh)` — Eigene Funde (ganz oder nur die geprüfte Region) einsetzen; LanguageTool/KI gehen dabei nicht verloren.
  - `_fertig(rev, roh, doc)`
  - `_abstimmen(funde)` — Konsens zwischen den Quellen (``fund.abstimmen``) mit den gelernten Daten und dem Schalter der Gegenprobe.
  - `_text()` — Dokumenttext, je Dokumentrevision nur einmal gebildet (``toPlainText`` kopiert das ganze Dokument).
  - `_key(f)`
  - `_zeigen(meldung)`
  - `anzeigen(funde)`
  - `fund_aktuell(fund)` — Nur Karten/Funde der aktuellen Dokumentrevision dürfen Aktionen auslösen.
  - `funde_an(pos)`
  - `_menue_vorschlaege(gefunden, wort)` — (Text, Fund)-Paare: erst die Funde an der Stelle, dann Wörterbuch-/Klangvorschläge für ein unbekanntes Wort.
  - `_menue_aktionen(menu, gefunden, vorschlaege, wort)` — Kopf, fette Vorschläge und die Ignorieren-/Wörterbuch-Aktionen als QActions.
  - `erweitere_menue(menu, pos)` — Ein Kopf, ein Vorschlag je Möglichkeit, drei Aktionen — wie im Prüfbogen (Kontextmenü für Fehler-Aktionen).
  - `_wort_an(pos)` — (Wort, von, bis), wenn an der Stelle ein Wort steht, das das Wörterbuch nicht kennt.
  - `alle_ignorieren(wort)`
  - `zum_woerterbuch(wort)`
  - `ignorierte_wieder_pruefen()`
  - `gruendlich()`
  - `_lt_ignorieren(rev, funde, doc)` — Antwort verwerfen (True): anderes Dokument, Fehlermeldung (mit Status) oder geänderter Text.
  - `_lt_fertig(rev, funde, doc)`
  - `_ki_roh(text, vorschlaege)` — KI-Vorschläge als Fund-Dicts, der Reihe nach im Text verortet; nicht auffindbare entfallen.
  - `ki_fertig(rev, vorschlaege, dokument)` — KI-Vorschläge übernehmen; Antworten für ein gewechseltes oder geändertes Dokument verwerfen.
  - `aendern(fund)`
  - `lassen(fund)`
  - `alle_aendern()`
  - `vorschlaege(anfang)`
  - `autokorr(text_vor_cursor)`

### `korrektur/phonetik.py`

Lautvergleich für die Rechtschreibprüfung: Kölner Phonetik, Editierabstand, Wortvergleichs-Helfer.

- `de_schluessel(wort)`
- `ist_teilfolge(kurz, lang)`
- `gleicher_anfang(a, b)`
- `abstand(a, b)`
- `_in(zeichen, menge)`
- `_code_c(i, vor, nach)`
- `_koeln_code(c, i, vor, nach)` — Code eines Buchstabens; abhängig von Vorgänger und Nachfolger bei P, D, T, C, X.
- `koelner_phonetik(wort)`

### `korrektur/pruefung.py`

Die Prüfung ohne Internet: Regeln, Listen und Begründungen für Rechtschreibung, Grammatik und Zeichensetzung.

- `daten_ordner()` — Wo regeln.json und woerter.txt liegen.
- `_lies_regeln()` — Holt den gemeinsamen Wortschatz aus regeln.json.
- `uebernimm_schreibweise(original, verbesserung)`
- `mach_fund(von, bis, alt, neu, grund, art, wort_ebene)`
- `ist_abkuerzung(text, punkt)`
- `wort_um(text, stelle)`
- `ist_adresse(text, stelle)`
- `gross_dahinter(m, text)`
- `regel(muster, bau, grund, art, gruppe, pruefe, flags)`
- `wende_regeln_an(text, regeln, funde)`
- `pruefe_kongruenz(text, funde)`
- `lade_woerter(pfad)` — Liest die deutsche Wörterliste. Sie liegt neben dieser Datei; fehlt sie,
- `trenne_zusammen(wort)`
- `pruefe_zusammengeschrieben(text, funde)`
- `verwechslungen(wort)` — Wörter, bei denen genau ein Buchstabe gegen sein Spiegelbild getauscht ist (b/d, p/q). Eigene Hilfe, die
- `regel_varianten(wort)` — Wörter, die eine feste Hörregel ergibt: b/d, p/q, schp→sp, scht→st, verdoppelter oder einfacher Mitlaut.
- `_geruest(w)`
- `_ist_zusammensetzung(w)` — Zwei bekannte Wörter (mindestens vier Buchstaben), auch mit Fugen-s: „Wortabstand“.
- `_klang_kandidaten(w)`
- `_regel_vorschlag(w)` — Feste Hörregeln: ein einziges Wort (Umlaut-Paare zählen als eins) ist die Antwort, sonst None.
- `_klang_bewertet(w)` — Kandidaten mit Abstand (höchstens 3) als [(d, k)]; None, wenn w selbst eine Zusammensetzung ist.
- `_klang_reihe(bewertet)` — Nach Umlaut-Paaren zusammengefasst und gewichtet sortiert: [(Gewicht, Wort)].
- `_klang_eindeutig(reihe)`
- `klang_vorschlag(wort)` — Das eine Wort, das gemeint sein muss, oder None. Nur kleingeschrieben, ohne Rücksicht auf Satzstellung.
- `_klang_ausgeschlossen(text, m, gelernt, schalter)` — Wörter, bei denen der Klang-Prüfer nicht rät (Name, Adresse, schon bekannt, zusammengeschrieben ...).
- `_am_satzanfang(text, stelle)` — Steht davor nur Leerraum oder ein Satzzeichen (. ! ? :) mit Leerraum? Schaut nur rückwärts bis zum ersten Zeichen, das kein Leerraum
- `_klang_fund_wort(text, m, gelernt, schalter)` — Die Verbesserung für das Wort, falls der Klang-Prüfer sicher genug ist, sonst None.
- `pruefe_klang(text, funde, gelernt, schalter)`
- `nachbar_woerter(w)` — Alle Wörter, die genau einen Handgriff entfernt sind.
- `_tippfehler_treffer(w, woerter)`
- `tippfehler_vorschlag(wort)`
- `_tippfehler_berechnen(w, woerter)`
- `_tippfehler_fund(text, m, gelernt, schalter, klang_an)`
- `pruefe_tippfehler(text, funde, gelernt, schalter)`
- `wort_abstand(a, b)` — Wie viele Handgriffe liegen zwischen zwei Wörtern? Zwei vertauschte
- `ist_korrektur(falsch, richtig)` — Sieht die Verbesserung dem Wort überhaupt ähnlich? Ein Rechtschreib-
- `uebergehen(wort, text, stelle, schalter)`
- `_wort_fund(wort, stelle, eigene)` — Fund für ein Wort aus der mitgelieferten Liste oder aus selbst Gelerntem, sonst None.
- `pruefe_woerter(text, funde, gelernt, schalter)`
- `pruefe_satzende(text, funde)`
- `mach_hinweis(von, bis, grund, stelle)`
- `pruefe_satzbau(text, hinweise)`
- `ohne_ueberschneidung(funde)` — Zwei Funde an derselben Stelle gehen nicht — die erste Änderung ließe
- `pruefer_aktiv(name, schalter)` — Ist der Prüfer eingeschaltet? Ohne Angabe sind alle an.
- `finde_probleme(text, gelernt, schalter)` — Alle Stellen, die auffällig sind — in derselben Reihenfolge wie am Handy.

### `korrektur/silben_de.py`

Deutsche Sprechsilben — für „Silben farbig“ (Lesehilfe für Legasthenie).

- `_einheiten(w)` — Zerlegt in Buchstabeneinheiten: Vokalkerne (V…), Konsonanteneinheiten (K…). → Liste von (art, text).
- `_wortende(w)` — Zusätzliche Grenzen am Wortende für getrennt gesprochene Vokale: Ide-en, Mu-se-um, Fami-li-en, Fa-mi-li-e.
- `_stueck(w)` — Silbengrenzen (Indizes in w) innerhalb eines Wortstücks nach den Regeln der Sprechsilben.
- `_pyphen()`
- `_hat_kern(s)`
- `_hinweis_ok(w, p)` — Ist die von pyphen vorgeschlagene Stelle p ein Wortbaustein-Rand und keine bloße Zeilenumbruch-Stelle?
- `silben(wort)` — Das Wort in Sprechsilben. Wörter mit Ziffern/Sonderzeichen und ganz in Großbuchstaben bleiben ungeteilt.

### `korrektur/vorhersage.py`

Wortvorhersage und Themenwörter (daten/themenwoerter.json).

- `themenwoerter()` — Liest daten/themenwoerter.json: je Empfänger eine Liste von Wörtern.
- `thema_woerter(name)`
- `thema_aufnehmen(woerter)` — Themenwörter sind richtig geschrieben und bekommen keine Wellenlinie.
- `_liste()`
- `faengt_an_mit(anfang, hoechstens, gelernt, thema)`

## `modelle`

### `modelle/__init__.py`

Datenmodelle: Seiteneinrichtung, Berichte.


### `modelle/bericht.py`

Bericht über das, was beim Öffnen/Speichern nicht verlustfrei ging.

- **class `IOReport`**
  - `warn(text)`
  - `__bool__()`
- **class `DocumentIOError`**(Exception) — Datei nicht lesbar oder nicht schreibbar — Text ist für Anwender gedacht.
- **class `PasswortNoetig`**(DocumentIOError) — Das Dokument ist verschlüsselt; ohne (richtiges) Kennwort lässt es sich nicht öffnen.
  - `__init__(falsch)`

### `modelle/korrektur.py`

Gemeinsames Datenmodell eines Fundes der Schreibhilfe (Rechtschreibung, Grammatik, Stil, LanguageTool, KI).

- **class `FundFehler`**(ValueError) — Ein Fund entspricht nicht dem Datenvertrag von ``ProofingIssue``.
- **class `Verdraengt`** — Ein Fund einer anderen Quelle, der von einem besseren überlagert wurde (nur zur Nachvollziehbarkeit).
- `zeige_leer(s)` — Leerzeichen und Zeilenumbrüche in Worten statt in Symbolen: „2 Leerzeichen“, „Zeilenumbruch“ (auch gut vorlesbar).
- **class `ProofingIssue`**
  - `_pruefe_bereich(text_laenge)`
  - `_pruefe_texte()`
  - `_pruefe_herkunft()`
  - `pruefen(text_laenge)` — Wirft ``FundFehler``, wenn der Fund nicht dem Vertrag entspricht. → self.
  - `laenge()`
  - `zeige_alt()`
  - `zeige_neu()`
  - `hat_vorschlag()`
  - `ersetzt(**felder)` — Eine Kopie mit geänderten Feldern (der Fund selbst ist unveränderlich).
  - `verschoben(delta)`
  - `stellenschluessel()` — Sortierung nach Stelle: früher zuerst, bei gleichem Anfang der längere.
  - `von_dict(f)`
  - `als_dict()` — Wörterbuch wie bisher; Schlüssel ohne Wert (quelle, konfidenz, verdraengt) fehlen, wie bei den ursprünglichen Funden.
- `bereinigen(funde, text_laenge)` — Prüft jeden Fund gegen den Vertrag (``ProofingIssue`` oder Wörterbuch von außen, etwa aus LanguageTool); gültige kommen als

### `modelle/seite.py`

Seiteneinrichtung: Papier, Ränder, Ausrichtung, Kopf- und Fußzeile.

- **class `HeaderFooter`** — Text mit Platzhalter {PAGE} und {PAGES}. Ausrichtung: left\|center\|right, dazu aussen\|innen (ungerade Seiten rechts bzw. links,
  - `kopie(text, align)`
  - `laeufe()` — (Text, Zeichenformat)-Stücke in Reihenfolge. Ohne gültige eigene Läufe gilt ein Stück: der ganze Text mit ``fmt``.
  - `is_empty()`
- **class `PageSettings`**
  - `landscape()`
  - `set_orientation(landscape)`
  - `set_paper(name)`
  - `paper_name()`
  - `content_width_px()`
  - `content_height_px()` — Höhe der Textfläche einer Seite, im Raster des Seitenumbruchs (``umbruchraster``).
  - `kopf_fuss_art(blatt, nummer)` — Welche Kopf-/Fußzeile ein Blatt trägt: "first" (Blatt 1 bei „Erste Seite anders“), "even" (gerade angezeigte Seitenzahl bei
  - `kopf_fuss(blatt, nummer)` — (Kopfzeile, Fußzeile) für das Blatt, siehe ``kopf_fuss_art``.
  - `erste_seite_versatz_px()` — Wie weit der Text der ersten Seite nach unten rückt, weil die Kopfzeile länger ist als der obere Rand: Der Text beginnt erst unter der
  - `copy()`
  - `spaltenraster_px()` — Das Spaltenraster der Textfläche: [(x, Breite)] je Spalte in Bildpunkten, x vom linken Textrand. Gleich breit oder — mit
  - `spalten_breite_px()` — Breite einer Textspalte (bei einer Spalte: die ganze Textbreite).

## `oberflaeche`

### `oberflaeche/__init__.py`

Oberfläche (Qt-Widgets): Hauptfenster, Menüband, Dokumentbereich, Seitenleiste, Dialoge.


### `oberflaeche/backstage.py`

Backstage-Ansicht des Reiters „Datei“: links die Befehlsliste, rechts die Seite zum gewählten Befehl.

- `symbol(name, px)`
- **class `_Zeile`**(QStyledItemDelegate) — Zeichnet die Trennlinien quer über die Liste und den kleinen Pfeil rechts bei Einträgen mit eigener Seite.
  - `paint(p, opt, idx)`
- `stil()` — Stylesheet beim Aufruf formatiert, damit das Thema gilt.
- **class `Backstage`**(QWidget)
  - `__init__(fenster)`
  - `oeffnen(seite, unter)` — ``unter``: bei „optionen“ die Seite der Optionen, die gleich offen sein soll (z. B. „ki“).
  - `optionen_seite()` — Schlüssel der Optionenseite, die gerade offen ist (z. B. „ansicht“).
  - `_optionen()` — Platzhalter: die Optionen werden erst gebaut, wenn die Seite zum ersten Mal gezeigt wird.
  - `_optionen_zeigen()`
  - `_zeigen(schl)`
  - `_aktiviert(it)` — Eingabetaste in der Liste; ein Mausklick meldet sich zugleich über ``itemClicked`` und darf nicht doppelt wirken.
  - `_gewaehlt(it)`
  - `_speicherort()`
  - `_seite(titel)`
  - `_gruppe(v, text, hinweis)`
  - `_knopf(v, text, befehl, icon, schliessen, datei)`
  - `_zuletzt()` — Rechts neben dem Menü: die zuletzt verwendeten Dateien (Name, Ordner, Datum; ✕ nimmt sie aus der Liste).
  - `_speichern_als()`
  - `_vorlage()` — Platzhalter: die Galerie mit den Vorschauen wird erst gebaut, wenn die Seite gezeigt wird.
  - `_vorlage_zeigen()`
  - `_drucken()` — Platzhalter: das Druckfenster samt Vorschau wird erst gebaut, wenn die Seite gezeigt wird.
  - `_pdf()` — Platzhalter für den eingebetteten PDF-Export, frisch je Öffnen des Datei-Menüs.
  - `_pdf_zeigen()`
  - `_bild()` — Platzhalter für den Bildexport in der rechten Menüspalte.
  - `_bild_zeigen()`
  - `_drucken_zeigen()`
  - `_hilfe()`
  - `_schuetzen()`
  - `_info()`
  - `_info_allgemein(v, t)`
  - `_info_statistik(v, ed)`
  - `_info_eigenschaften(v, t)`
  - `_meta_setzen(t, schl, wert)`
  - `_zeile(v, name, feld)`
  - `_oeffnen_mit()`

### `oberflaeche/kuerzel.py`

Tastenkürzel — eine Tabelle für die Hilfe und für die Kürzel, die nicht an einer Aktion des Fensters hängen.

- `als_markdown()` — Die Tabelle als Markdown — das zeigt der Hilfe-Dialog über ``QTextBrowser.setMarkdown``.

### `oberflaeche/lesestufen.py`

Die drei Lesestufen der Lesehilfe — gemeinsam für die Optionen und die rechte Seitenleiste.

- `aktuell(s)` — Name der Stufe, auf der die Einstellungen gerade stehen, oder „“ (eigene Einstellung).
- `setze(s, name)` — Schreibt die Werte der Stufe in die Einstellungen (angewendet wird mit ``MainWindow.lesehilfe_anwenden``).

### `oberflaeche/programmfenster.py`

Hauptfenster: Menüleiste, Schnellzugriff, Ribbon, Dokumentreiter, Statusleiste.

- **class `MainWindow`**(ReiterZustandMixin, FensterVerwaltungMixin, DokumentSyncMixin, DateienBaustein, BearbeitenBaustein, OberflaecheBaustein, BackstageBaustein, QMainWindow)
  - `__init__(settings)`
  - `_act(text, slot, shortcut, checkable, tip, symbol)`
  - `_build_actions()`
  - `_build_menu()`
  - `_fill_recent()`
  - `_clear_recent()`
  - `_build_status()`
  - `word_count()` — Wörter zählen (Fenster wie Überprüfen ▸ Wörter zählen).
  - `show_info()`
  - `show_options(seite)` — Die Optionen stehen in der Datei-Ansicht („☰ Menü ▸ Optionen“); ohne Register-Band als Fenster.
  - `toggle_fullscreen(on)`
  - `about()`

### `oberflaeche/schreibhilfe_katalog.py`

Alle Funktionen der Schreibhilfe an einer Stelle: Wo sie in der Seitenleiste („Werkbank“) und im Band stehen und welcher Befehl dahinter hängt.

- **class `Funktion`**
- `fuer_reiter(reiter)`
- `fuer_gruppe(gruppe)`

### `oberflaeche/thema.py`

Hell/Dunkel über Qt-Paletten (Stil „Fusion“) — keine Stylesheets für das Grundlayout.

- `kopf_symbolfarbe()` — Symbolfarbe für den grünen Kopfbereich im Thema Mint (dunkel auf Hellgrün); sonst ``None`` = Farbe der Palette.
- **class `_RundFilter`**(QObject) — Rundet die Ecken eines Widgets (Maske), solange er installiert ist; Radius aus ``MINT_FARBEN``.
  - `eventFilter(obj, ev)`
  - `runden(w)`
- `karten_rand()` — Breite des Kartenrands der Seitenleisten-Panels im aktuellen Thema (Mint: ``luft``, sonst 0).
- `karte_einrichten(widget, layout, breite)` — Seitenleisten-Karte (Mint): gemeinsame Eigenschaft für das Stylesheet und der Innenrand = Breite des Kartenrands, sonst überdeckt der Rand die
- `_karten_rand_setzen(widget)`
- `mint_abstaende(fenster)` — Thema-Hook für das Hauptfenster: im Thema Mint Außenränder um Arbeitsbereich und Band, Band als Karte, Dokumentfläche mit runden Ecken;
- `apply_theme(app, mode)`
- `_ist_dunkel(app)`
- `_pfeile(farbe)` — Dropdown-Pfeile aus dem zentralen Lucide-Katalog für Qt-Stylesheets.
- `_kreuz(farbe)`
- `_stil(app)`
- `_setze(app, mode)`
- `_mint_palette()`
- `_helle_palette()` — Feste helle Grundpalette (wie Fusion hell), unabhängig von der Palette des Plattformdesigns.
- `_hell_feinschliff(app)` — Helle Palette: Fläche um das Blatt; mit „Weichem Kontrast“ warme Töne.
- `Qt_white()`

## `oberflaeche/band`

### `oberflaeche/band/__init__.py`

Menüband: Reiterleiste, Gruppen, Knöpfe, Symbol-/Menüleisten.


### `oberflaeche/band/band_bausteine.py`

Hilfswidgets und Kurztexte des Menübandes.

- **class `_GruppenTrenner`**(QWidget) — Dezenter Gruppentrenner im Band: genau ein physischer Bildpunkt breit, oben und unten eingerückt, Farbe aus der aktuellen Palette
  - `__init__()`
  - `paintEvent(_ev)`
- **class `_BandSeite`**(QScrollArea) — Eine Seite des Bandes. Ist sie breiter als das Fenster, erscheinen am Rand Pfeile zum Blättern (‹ und ›), wie in der Vorlage Writer;
  - `__init__()`
  - `blaettern(richtung)`
  - `_pfeile_zeigen(*_)`
  - `_pfeile_legen()`
  - `resizeEvent(ev)`
  - `wheelEvent(ev)`
- `_kurz(name)`
- `_mit_kuerzel(name)` — Hinweistext eines Knopfes; steht der Name in der Kürzel-Tabelle (``oberflaeche/kuerzel.py``), kommt das Tastenkürzel dahinter.
- `_zweizeilig(text)`
- **class `_ReiterLeiste`**(UeberlaufLeiste)
  - `mouseDoubleClickEvent(ev)`
  - `ist_kontext(i)`
  - `tabSizeHint(i)`
  - `_luecke()`
  - `paintEvent(ev)`
- **class `_SperrKasten`**(QCheckBox) — Kontrollkästchen „Seitenverhältnis sperren“: Klick ruft ``bildSeitenverhaeltnis``; ``auffrischen`` holt den Zustand vom Bild.
  - `__init__(text, befehle)`
  - `_klick(an)`
  - `auffrischen()`
- **class `_FelderDict`**(dict) — Felder des Bandes: Reiter werden schrittweise gebaut; expliziter Zugriff auf ein fehlendes Feld baut alle Reiter.
  - `__init__(band)`
  - `__missing__(key)`
  - `get(key, default)`
  - `__contains__(key)`

### `oberflaeche/band/band_gruppen.py`

Aufbau von Gruppen und Schaltflächen im Menüband.

- `_zeilen_teilen(eintraege)` — Die kleinen Einträge in Zeilen: ``//`` oder ein Zeilenumbruch beginnt eine neue (dann ``explizit``); sonst entscheidet das Gitter.
- **class `BandGruppenBaustein`** — Erzeugt die Gruppeninhalte und deren Schaltflächen-Anordnungen.
  - `_gruppe(g)`
  - `_knoepfe_geordnet(g, inhalt)` — Knöpfe in der Reihenfolge der Liste: große stehen allein, aufeinanderfolgende kleine bilden eine Spalte aus zwei Zeilen.
  - `_knoepfe_schrift(g, inhalt)` — Wie in der Vorlage: oben Schriftname und -größe, daneben die Größen-/Löschknöpfe; darunter die Zeichenformate.
  - `_knoepfe_tt_schrift(g, inhalt, art)` — Texttools: Schriftname und -größe oben (wirken auf das markierte WordArt/Textfeld), darunter die Zeichenformate — wie bei Start.
  - `_knoepfe_galerie(g, inhalt)` — Eine Galerie wie in der Vorlage: drei Kacheln zum Anklicken und daneben ein Pfeil mit der ganzen Auswahl (Befehl ``galerie_<name>``).
  - `_knoepfe_raender(g, inhalt)` — Der Rand-Knopf und daneben wie in der Vorlage die vier Maßfelder Oben/Unten/Links/Rechts (in der gewählten Maßeinheit).
  - `_knoepfe_masse(g, inhalt)` — Höhe und Breite des markierten Bildes (Zeichentools); „Seitenverhältnis sperren“ hält das Verhältnis beim Ändern.
  - `_knoepfe(g, inhalt)`
  - `_knoepfe_formatfelder(inhalt)` — Formatvorlage, Schriftart und Größe als Spalte vor den Knöpfen.
  - `_gitter_fuellen(gitter, explizit, zeilen, kleine)` — Die kleinen Knöpfe ins Gitter: explizit zeilenweise, sonst spaltenweise in zwei Zeilen.
  - `_knoepfe_gitter(eintraege, inhalt)` — Große Knöpfe nebeneinander, kleine im Gitter (zwei Zeilen oder explizite Zeilen).

### `oberflaeche/band/band_knoepfe.py`

Erzeugung der Menüband-Knöpfe und ihrer Menüs.

- **class `BandKnopfBaustein`** — Baut einzelne Menüband-Knöpfe, Klappen und Menüeinträge.
  - `_knopf(e, gross)`
  - `_knopf_aktion(k, akt, name, sym, gross)` — Text, Tipp, Symbol und Größe des Symbols.
  - `_knopf_buchstabe(k, sym)` — Knöpfe ohne Symbol zeigen den Buchstaben (F fett, K kursiv, U unterstrichen).
  - `_knopf_darstellung(k, akt, e, gross)` — Textstellung und Größenrolle je nach Art des Knopfes.
  - `_knopf_menue(k, akt, e, gross)` — Menü oder Klappe des Knopfes. → (vorhanden?, Menü).
  - `_knopf_zustand(k, akt, e)` — Wechselsymbol und Schaltzustand (Haken) des Befehls.
  - `_klappe(name)` — Das Menü einer Klappe: erst die Bausteine der Oberfläche (``KLAPPEN``), sonst ``menue_<name>`` des Befehlsbausteins.
  - `_menue_fuellen(menu, items)`

### `oberflaeche/band/band_leiste.py`

Das Band (Register): Reiter → Gruppen → Knöpfe, gebaut aus ressourcen/register.json.

- `lade_register()`
- **class `RegisterBand`**(BandSchnellzugriffBaustein, BandReiterBaustein, BandRaenderBaustein, BandZustandBaustein, BandStileBaustein, BandKnopfBaustein, BandGruppenBaustein, QWidget) — Kopfzeile (☰, Schnellzugriff, Reiter) und darunter das Band des gewählten Reiters.
  - `__init__(befehle, daten, cfg, schnell, kompakt)`
  - `bandfehler()`
  - `_trenner()`
  - `gruppe_widget(g)` — Eine Gruppe als eigenständiges Widget (für die Seitenleiste).

### `oberflaeche/band/band_raender.py`

Randvorgaben-Steuerung für das Menüband.

- **class `BandRaenderBaustein`** — Erzeugt die Auswahl der vordefinierten Seitenränder.
  - `_raender()`

### `oberflaeche/band/band_reiter.py`

Reiter-, Seiten- und Kontextnavigation des Menübands.

- **class `BandReiterBaustein`** — Verwaltet Menüband-Reiter, Seitenaufbau und Kontextregister.
  - `_reiter_gewaehlt(i)`
  - `_seite_bauen(i)`
  - `_alle_bauen()`
  - `_im_leerlauf_bauen()` — Nach dem Anzeigen: je Durchlauf einen Reiter bauen, damit die Oberfläche dazwischen bedienbar bleibt.
  - `_reiter_geklickt(_i)`
  - `einklappen_umschalten()`
  - `_plan_angepasst()` — Reiter in der Reihenfolge der Struktur — ausgeblendete weglassen, eigene Reihenfolge beachten (Register anpassen).
  - `_reiter(r)`
  - `kontext(name, sichtbar, aktivieren)` — Kontext-Register (Tabellentools, Bildtools …) ein- oder ausblenden; ``aktivieren``: gleich öffnen.
  - `_start_index()`

### `oberflaeche/band/band_schnellzugriff.py`

Schnellzugriffsleiste und schnelle KI-Aktionen des Menübands.

- **class `BandSchnellzugriffBaustein`** — Baut die Schnellzugriffsleiste und ihre KI-Aktionsknöpfe.
  - `_tausch_rechtsklick(k, sym)` — Rechtsklick auf einen Knopf: Fenster „Symbol austauschen“ mit der Zeichnung dieses Knopfes.
  - `_schnellzugriff()`
  - `ki_schnell(aktionen, ausfuehren)` — „Schnelle KI-Aktionen“ mit Zugriff „Schnellzugriff“: je ein Knopf hinter den übrigen der Schnellzugriffsleiste.

### `oberflaeche/band/band_stile.py`

Galerie und Vorschau der Formatvorlagen im Menüband.

- `_kacheln(m, aktuell, mehr)` — Je Formatvorlage eine Kachel: in ihrer Schrift und Farbe, mit Hinweis; „Weitere Stile“ aus blendet die selten gebrauchten aus.
- **class `BandStileBaustein`** — Stellt die Formatvorlagen-Galerie und ihre Ereignisbehandlung bereit.
  - `_stile(spalten)`
  - `_stile_popup(unter)` — Alle Formatvorlagen als Galerie (Pfeil rechts neben der Reihe): Probe in der Vorlage, Name darunter; Überfahren zeigt live.
  - `stile_aktualisieren()` — Die Galerie neu füllen — die eingebauten Vorlagen und die selbst angelegten (editor/text/stile.py).
  - `eventFilter(obj, ev)`

### `oberflaeche/band/band_zustand.py`

Zustandsaktualisierung für das Menüband.

- **class `BandZustandBaustein`** — Hält Knöpfe und Felder des Menübandes mit dem Dokumentzustand synchron.
  - `aktualisieren(hat_dokument)`
  - `_wechsler_auffrischen()` — Symbole der Wechsler (z. B. Ansicht) nach dem Zustand.
  - `_schalter_auffrischen()` — Angekreuzt, wenn der Zustand des Befehls gilt; ohne Signal, damit nichts ausgelöst wird.
  - `_knoepfe_auffrischen(hat_dokument)` — Knöpfe, die ein Dokument brauchen, und Knöpfe, deren Befehl im Augenblick nicht frei ist.
  - `_felder_auffrischen()`

### `oberflaeche/band/menueleiste.py`

Menüleiste, gebaut aus register.json („menues“).

- `_taste(t)`
- `baue_menueleiste(mb, menues, befehle)` — Füllt die Menüleiste. → Anzahl der Menüpunkte ohne nativen Befehl.
- `_fenster_menue(m, befehle)`

### `oberflaeche/band/plan.py`

Die Reiterleiste nach der Struktur „LUNIVO WRITER“: Datei, Start, Einfügen, Seitenlayout, Verweise, Überprüfen,

- `plan(register)` — Die Reiter in der Reihenfolge der Struktur; Kontext-Register stehen am Ende (zunächst verborgen).

### `oberflaeche/band/werkzeugleisten.py`

Oberfläche „Symbolleisten“: ☰ Menü + obere Leiste (Datei/Dokument) + untere Leiste (Text) + Zusammenhangsleiste.

- **class `Symbolleisten`**(QWidget)
  - `__init__(befehle)`
  - `_zeile(v)`
  - `_trenner(h)`
  - `_fuellen(h, liste)`
  - `_knopf(sym, tip, akt, haken)`
  - `_abstand(box)`
  - `kontext(name, sichtbar, aktivieren)`
  - `_kontext_fuellen(plan)` — Die Kontext-Leiste leeren und mit den Knöpfen des Plans neu aufbauen (je Gruppe ein Trenner).
  - `_kontext_knopf(e)` — Der Knopf zu einem Eintrag des Plans: Befehlsknopf (``tun``) oder Aufklappknopf (``klappe`` mit Menü des Bands); sonst None.
  - `aktualisieren(hat_dokument)`

## `oberflaeche/band/reiter`

### `oberflaeche/band/reiter/__init__.py`

Die Reiter des Menübands (Datei, Start, Einfügen, Seitenlayout, Verweise, Überprüfen, Schreibhilfe, Ansicht).


### `oberflaeche/band/reiter/abschnitt_reiter.py`

Reiter „Abschnitt“ in der Anordnung der Vorlage.

- `bauen(register)`

### `oberflaeche/band/reiter/ansicht_reiter.py`

Reiter „Ansicht“ in der Anordnung der Vorlage: Dokumentansichten (Vollbild, Lesemodus, Drucklayout, Weblayout), Navigationsbereich

- `bauen(register)`
- `_mit_weitere(tab, gruppen, rest_knoepfe)` — Die übrigen Befehle als Gruppe „Weitere“ am Ende (nur, wenn es welche gibt).

### `oberflaeche/band/reiter/baustein.py`

Baustein für die Reiterbeschreibungen: ein Knopf als Wörterbuch.

- `k(symbol, name, tun, gross, **kw)`
- `anordnen_knopf(art, name, **kw)` — Ein Knopf der Gruppe „Anordnen“ (``art``: drehen, gruppieren, ausrichten, umbruch, vorn, hinten, ebene, objekte, auswahlbereich); ``name`` und ``gross``/``text`` je Reiter.
- `anordnen_gruppe(*knoepfe)` — Die Gruppe „Anordnen“ der Kontext-Reiter.
- `alle(tab)` — Alle Knöpfe eines Reiters aus register.json nach Namen.
- `uebrige(tab, benutzt)` — Knöpfe des Reiters, die in der neuen Anordnung noch nicht vorkommen (damit keine Funktion verloren geht).

### `oberflaeche/band/reiter/datei_reiter.py`

Reiter „Datei“ (die Backstage-Ansicht ersetzt das Band; die Gruppen bleiben als Vorlage für Menüs und Symbolleisten).

- `bauen(register)`

### `oberflaeche/band/reiter/einfuegen_reiter.py`

Reiter „Einfügen“ in der Anordnung der Vorlagen (Ordner einfuegen/): Deckblatt, Leere Seite ▾, Umbrüche ▾, Tabelle ▾,

- `bauen(register)`

### `oberflaeche/band/reiter/ki_reiter.py`

Reiter „Schreibhilfe“: Lesen, Prüfen, Beim Schreiben, Vorlesen, Sprache, Bausteine, KI und Anzeigen — jede Funktion einmal, jede mit eigenem Symbol.

- `_knoepfe(gruppe)` — Die Band-Knöpfe einer Gruppe: erst die kleinen, dann die großen.
- `_ki_knoepfe()` — KI: die vier Textbefehle (entwerfen, umformulieren, zusammenfassen, Text in Bild) stehen in einem Menü „Text mit KI“; Chat und Aktionen
- `_pruefen_menue(e)` — Das eine Prüfmenü: wann geprüft wird (F7), gründlich, mit KI (F8), Hilfen.
- `bauen(register)`

### `oberflaeche/band/reiter/layout_reiter.py`

Reiter „Seitenlayout“ in der Anordnung der Vorlage: Designs, Ränder mit den vier Maßfeldern, Seite einrichten

- `bauen(register)`

### `oberflaeche/band/reiter/sendungen_reiter.py`

Reiter „Sendungen“ (nur nach „Register anpassen“ sichtbar): Serienbriefe. Die Formularfelder stehen nur im Reiter Einfügen (Gruppe Formulare).

- `bauen(register)`

### `oberflaeche/band/reiter/start_reiter.py`

Reiter „Start“ in der Anordnung der Vorlage.

- `bauen(start)` — Reiter Start in der Anordnung der Vorlage: Zwischenablage (Einfügen, Ausschneiden/Kopieren, Format übertragen), Schriftart mit

### `oberflaeche/band/reiter/ueberpruefen_reiter.py`

Reiter „Überprüfen“ nach Kays Vorlagen (ueberpruefen/01–10): Rechtschreibprüfung, Wörter zählen, Kommentare, Änderungen

- `bauen(register)`

### `oberflaeche/band/reiter/verweise_reiter.py`

Reiter „Verweise“ (in register.json „Referenzen“) in der Anordnung der Vorlage: TOC einfügen, Inhaltsverzeichnis

- `bauen(register)`

## `oberflaeche/baukasten`

### `oberflaeche/baukasten/__init__.py`

Wiederverwendbare Bausteine der Lunivo-Oberfläche, nach Zuständigkeit in Unterpaketen:


## `oberflaeche/baukasten/basis`

### `oberflaeche/baukasten/basis/__init__.py`

Grundlegende UI-Bausteine.


### `oberflaeche/baukasten/basis/beschriftung.py`

Beschriftungen ohne Auszeichnungssprache: Text mit Schrifteigenschaften oder Markdown (`Qt.MarkdownText`).

- `md_escape(text)` — Sonderzeichen eines Textes für Markdown unschädlich machen (z. B. wenn er in `**…**` eingebettet wird).
- `text_label(text, *, fett, pt, durchgestrichen, umbruch, auswaehlbar)` — Beschriftung aus reinem Text; Zeilenumbrüche des Textes bleiben erhalten.
- `md_label(markdown, *, umbruch)` — Beschriftung aus Markdown (fett, durchgestrichen, Absätze) — Qt zeigt es selbst an.

### `oberflaeche/baukasten/basis/dialog_rahmen.py`

Grundgerüst für kleine Dialoge: Formular, optionale Vorschau, OK/Abbrechen und Zusatzknöpfe wie „Entfernen“.

- **class `_KnopfLayout`**(QLayout) — Zusatzknöpfe links, „Abbrechen“ und „OK“ rechts — in einer Zeile, wenn sie nebeneinander passen; sonst stehen die Zusatzknöpfe (umbrechend) darüber.
  - `__init__()`
  - `extra(widget)`
  - `haupt(widget)`
  - `addItem(item)`
  - `count()`
  - `itemAt(i)`
  - `takeAt(i)`
  - `hasHeightForWidth()`
  - `sizeHint()`
  - `minimumSize()`
  - `heightForWidth(w)`
  - `setGeometry(r)`
  - `_plan(w)`
- **class `Knopfzeile`**(QWidget) — Die Knopfzeile unten in jedem Fenster — der einzige Ort, der sie baut: links Zusatzknöpfe, rechts „Abbrechen“ und „OK“ (gleich breit).
  - `__init__(dialog, *links, bei_ok, ok_text, abbrechen_text, nur_ok, schliessen)`
  - `zusatz_knopf(k)`
  - `zusatz(text, aktion, *, schliesst)` — Knopf neben OK/Abbrechen (z. B. „Entfernen“); ``schliesst`` beendet das Fenster mit OK.
- `knopfzeile(dialog, *links, **kw)` — Eine Knopfzeile für ``dialog`` (zum Einsetzen in ein Layout); Wahlmöglichkeiten wie bei ``Knopfzeile``.
- `fussleiste(dialog, layout, *links, bei_ok, ok_text, abbrechen_text, nur_ok)` — Knopfzeile unten ins ``layout`` setzen. Gibt den OK-Knopf zurück (``bei_ok`` ersetzt ``accept``, z. B. zum Prüfen vor dem Schließen).
- `_symbol(art)` — Lucide-Symbol für Abbrechen oder Bestätigen.
- **class `VorschauFlaeche`**(QWidget) — Weißes Blatt, auf das der Dialog mit ``zeichne(painter, rect)`` seine Vorschau malt.
  - `__init__(zeichne, hoehe, flaeche)` — ``flaeche=False``: kein weißes Feld mit Rand; ``zeichne`` malt direkt auf den Fensterhintergrund (z. B. ein einzelnes Blatt).
  - `paintEvent(e)`
- **class `DialogRahmen`**(QDialog) — Unterklassen füllen ``self.form`` (``zeile(...)``) und liefern ``ergebnis()``. Wer sich ändert, ruft ``aktualisieren()``.
  - `__init__(parent, titel, vorschau)`
  - `zeile(beschriftung, widget)`
  - `zusatzknopf(text, aktion, *, schliesst)` — Knopf neben OK/Abbrechen (z. B. „Entfernen“); ``schliesst`` beendet den Dialog mit OK.
  - `aktualisieren(*_)`
  - `ergebnis()`

### `oberflaeche/baukasten/basis/farben.py`

Farbdaten für jede Palette im Programm: Themenfarben mit Abstufungen, Standardfarben, zuletzt benutzte.

- `mische(a, b, anteil)` — Mischt Farbe a zum Anteil (0…1) mit Farbe b.
- `abstufungen(farbe)` — Fünf Abstufungen einer Themenfarbe, von hell nach dunkel (Weiß geht nur nach Grau, Schwarz nur nach Grau).
- `thema_raster()` — Zeilen der Themenfarben: erst die Grundfarben, darunter die fünf Abstufungen.
- `zuletzt_laden()`
- `zuletzt_merken(farbe)`

### `oberflaeche/baukasten/basis/karte.py`

Karte/Zeile: die eine Quelle für abgesetzte Flächen in den Seitenleisten (Kommentar, Fund, Funktionszeile, KI-Blase).

- `als_karte(widget, art)` — Kennzeichnet das Widget als Karte der Art ``art``: zeile (anklickbar, durchsichtig), karte (Fund), kompakt (Kommentar), ki/markiert (Blase mit Streifen links),
- `karte_regeln(fokus, ki, grau, fehler)` — QSS-Text aller Kartenarten; Farben ``fokus`` (Fokusrahmen, KI-Streifen), ``ki`` (Streifen KI-Blase), ``grau`` (Streifen sonst), ``fehler`` (Fehlerkarte) kommen vom Thema.

### `oberflaeche/baukasten/basis/linien.py`

Linien: Stärke, Art, Farbe — als Wert, als Auswahlzeile für Dialoge und als Rahmen-Menü (unten, oben, links, rechts …).

- `linien_symbol(art, groesse, farbe, breite_pt)`
- **class `LinienZeile`**(QWidget) — Eine Zeile in einem Menü: links ein Text (kann leer sein), rechts die Linie in ihrer Art und Stärke — wie die Auswahl „Linienart“ und
  - `__init__(text, art, breite_pt, farbe, parent, maler)` — ``maler(painter, x0, y, x1, farbe)`` zeichnet statt einer Rahmenlinie etwas anderes, zum Beispiel eine Unterstreichungsart.
  - `enterEvent(e)`
  - `leaveEvent(e)`
  - `mouseReleaseEvent(e)`
  - `paintEvent(e)`
- `linien_menue_zeile(menue, text, art, breite_pt, aktion, maler)` — Hängt eine ``LinienZeile`` als Eintrag in ein Menü; ein Klick ruft ``aktion`` und schließt das Menü.
- **class `LinienWahl`**(QWidget) — Eine Zeile aus Art, Stärke und Farbe. Meldet jede Änderung als ``Linie``.
  - `__init__(linie, *, arten, breiten, frei, parent)` — ``frei``: eine Stärke, die nicht in der Liste steht, kommt als eigener Eintrag dazu (statt auf die nächste zu runden).
  - `setLinie(linie)`
  - `linie()`
  - `_aend()`
- **class `RahmenSeiten`**(Flag)
- `rahmen_symbol(seiten, groesse)` — Kleines Quadrat, in dem nur die gemeinten Linien kräftig sind.

### `oberflaeche/baukasten/basis/mass.py`

Zentrale Maße der gemeinsamen Bausteine und Fenster — benannte Konstanten nach Rolle, damit gleiche Werte nur einmal stehen.


### `oberflaeche/baukasten/basis/texte.py`

Gedämpfte Texte und Trennlinien der Oberfläche — ein Baustein statt einzelner Stylesheets.

- `_stil(klein, zusatz)`
- `hinweis_label(text, *, umbruch, klein, zusatz)`
- `hinweis_stil(label, *, klein, zusatz)` — Macht ein vorhandenes Label zum gedämpften Hinweistext (für Labels, die anders gebaut werden, z. B. mit eigener Schrift oder Ausrichtung).
- `kleintext_label(text)` — Kleine gedämpfte Beschriftung (z. B. „Für wen“), ohne Zeilenumbruch.
- `trennlinie(*, senkrecht, tief)` — Feine Trennlinie: waagerecht (Standard) oder ``senkrecht``; ``tief`` = die vertiefte Linie des Stils, sonst eine Linie in ``midlight``.
- `auffrischen(widget)` — Setzt den Stil eines Hinweistexts nach einem Themenwechsel mit der neuen ``Farbe.HINWEIS`` neu.
- `marke_faerben(w, grund, schrift, rest)` — Farbige Marke (Chip-Label): ``grund``/``schrift`` sind Farben; ist ``grund`` die Akzentfarbe, kommen Fläche und Schrift aus dem Thema

### `oberflaeche/baukasten/basis/zwischenablage.py`

Zwischenablage: Text in die Zwischenablage legen — die eine Stelle dafür im Baukasten (Chat-Blasen u. a.).

- `in_zwischenablage(text)`

## `oberflaeche/baukasten/chat`

### `oberflaeche/baukasten/chat/__init__.py`

Chat-Oberflächenbausteine.


### `oberflaeche/baukasten/chat/chat_anhang.py`

Bild-Anhang im KI-Chat: ``AnhangChip`` (über dem Textfeld) und (Vorschau ``miniatur`` steht in ``chat_blase``).

- `groesse_text(n)`
- `name_gekuerzt(pfad, zeichen)` — Dateiname, in der Mitte gekürzt, die Endung bleibt sichtbar.
- **class `AnhangChip`**(QFrame) — Zeile „Vorschau, Dateiname (gekürzt), Größe, ×“. ``entfernt`` kommt beim Klick auf ×.
  - `__init__(pfad, groesse)`

### `oberflaeche/baukasten/chat/chat_blase.py`

Nachrichten des KI-Chats: Nutzerblase, KI-Antwort und Fehlerkarte — nur Darstellung, jede Aktion ruft den Dienst (``dienst``).

- **class `SymbolKnopf`**(DropdownKnopf) — Flacher Symbolknopf (Chat): Symbol in Palettenfarbe, folgt dem Themenwechsel.
  - `__init__(symbol, tipp, funktion)`
  - `symbol_setzen(symbol, tipp, farbe)`
  - `_zeichnen()`
  - `changeEvent(e)`
- `miniatur(pfad, seite)` — Kleine Bildvorschau als Widget. Fehlt die Datei oder lässt sie sich nicht lesen, steht dort der Platzhalter „[Bild]“.
- `_text(text)`
- `antwort_label(text)` — Antwort der KI: mit Überschriften, Listen, Tabellen oder Hervorhebungen als Markdown (dieselben Regeln wie bei der Übernahme ins Dokument,
- **class `NutzerBlase`**(QWidget) — Eigene Nachricht: rechts, grau, bei Anhang mit Bild-Miniatur; darunter Kopieren und Mehr (Text noch einmal ins Eingabefeld nehmen).
  - `__init__(text, bilder)`
- **class `KiBlase`**(QWidget) — Antwort der KI mit Symbolzeile: Wiederholen, Kopieren, Einfügen, Ersetzen; Kosten klein dahinter.
  - `__init__(dienst, text, cent, index, *, dokument, titel)`
  - `_auszug(text)` — Die ersten ``CHAT_AUSZUG_ZEILEN`` Zeilen des neuen Dokumenttexts; der Rest ist mit „…“ ausgelassen.
  - `vergleich_oeffnen()` — Das Vergleichsfenster für diese Antwort anfordern (Signal ``vergleichOeffnen`` mit der Kennung; ohne Kennung nichts).
  - `kontext_neu()` — Zustand der Symbole aus ``dienst.bezug_gueltig`` neu lesen (bei ``kontextGeaendert``/``chatGeaendert``).
- **class `FehlerKarte`**(QWidget) — Fehler der KI: Titel, Text, Knopf „Wiederholen“; bei ``art`` „konfiguration“ der Weg zu den KI-Einstellungen, bei „zustimmung“ ein Hinweis.
  - `__init__(dienst, fehler)`

### `oberflaeche/baukasten/chat/chat_eingabe.py`

Eingabekasten des KI-Chats: Textfeld, darunter + (Bild), Befehle (Meine Aktionen), Modellwahl und der runde Senden-/Stopp-Knopf; Fußzeile mit Hinweis.

- **class `ChatEingabe`**(QPlainTextEdit) — Mehrzeiliges Eingabefeld: Enter schickt ab, Umschalt+Enter macht eine neue Zeile; wächst mit dem Text bis ``CHAT_EINGABE_MAX``. ``text()``/``setText()`` wie beim Einzeiler.
  - `__init__()`
  - `_hoehe()`
  - `keyPressEvent(e)`
  - `text()`
  - `setText(t)`
- **class `ChatEingabeKasten`**(QWidget)
  - `__init__(dienst)`
  - `text()`
  - `setText(t)`
  - `leeren()`
  - `anhang()` — Pfad des angehängten Bildes (oder ``None``).
  - `anhang_setzen(pfad, groesse)`
  - `anhang_entfernen()`
  - `_bild_waehlen()`
  - `_bild_nachziehen()` — „Lokales Bild“ ist grau mit dem Hinweis des Dienstes, wenn das Modell keine Bilder kann; ein vorhandener Anhang fällt dann mit Hinweis weg.
  - `zustand_setzen(frei, beschaeftigt)` — ``frei``: Modell verbunden (sonst alles gesperrt); ``beschaeftigt``: die KI arbeitet (Knopf wird zum Stopp).
  - `_zustand()`
  - `_symbole()`
  - `changeEvent(e)`
  - `eventFilter(o, e)`
  - `modelle_neu()` — Modellfeld aus der KI-Konfiguration füllen; „Standard“ zeigt den Namen des tatsächlich genutzten Modells.
  - `_modell_gewaehlt()`
  - `_websuche_gewaehlt(an)`
  - `_websuche_nachziehen()` — Der Schalter zeigt immer den Zustand der Konfiguration (auch nach Änderungen in den Einstellungen).
  - `_modell_zusatz(menue)` — Zeilen unter der Modellliste: Denktiefe und Berechtigungen, je mit dem aktuellen Wert rechts und einem Untermenü. Grau mit Hinweis, wenn nicht möglich.
  - `_werkzeugmodus_waehlen(modus)`
  - `_vorlagen_fuellen(menue)` — Untermenü „Vorlagen“: dieselben Anweisungen wie die Chips (Datenquelle ``chat_vorschlaege``); Klick füllt das Eingabefeld.
  - `_aktionen_fuellen()`
  - `_abschicken()`
  - `_knopf()`

### `oberflaeche/baukasten/chat/chat_leerzustand.py`

Leerzustand des KI-Chats: Symbol, Text „Ihr KI-Assistent für Dokumente“ und darunter die Vorschläge (Chips) passend zu Markierung und Dokument.

- **class `ChatLeerzustand`**(QWidget)
  - `__init__(dienst)`
  - `_bild()`
  - `changeEvent(e)`
  - `neu_aufbauen()` — Chips aus Markierung, Dokumentstand und Konfiguration neu bilden.

### `oberflaeche/baukasten/chat/chat_regler.py`

Reglerblock für den KI-Chat: Länge, Temperatur, Top P, Stoppfolgen, „Antwort direkt einfügen“ — als zugeklappter Abschnitt in den KI-Einstellungen.

- **class `ChatReglerBlock`**(QWidget)
  - `__init__(konfig)`
  - `umschalten(an)`

## `oberflaeche/baukasten/diagramme`

### `oberflaeche/baukasten/diagramme/__init__.py`

Diagramm- und SmartArt-Bausteine.


### `oberflaeche/baukasten/diagramme/diagramm_format_bausteine.py`

Gemeinsame Kleinbausteine der Diagramm-Formatierung (Seitenleiste): Auswahllisten, Zeichner für Strichart und Kombinierten Typ, ``_AutoWert``.

- `_optionen_name(teil)`
- `_text_teil(teil)`
- `_combo(eintraege)`
- `_strich_zeichner(art)` — Zeichner für ``StrichAuswahl``: ein Strich der Strichart ``art`` über die Breite (schwarz).
- `_kombi_zeichner(form)` — Zeichner für ``StrichAuswahl``: eine Linie des kombinierten Typs ``form`` (Flächen aus ``textfx._kontur_pfade``).
- `_still(x, wert, setter)`
- **class `_AutoWert`**(QWidget) — Eine Zahl, die „Automatisch“ sein kann (Minimum, Maximum, Hauptintervall der Achse): Haken + Feld. ``wert()`` ist None bei Automatisch.
  - `__init__(vorgabe)`
  - `wert()`
  - `setze(w)`

### `oberflaeche/baukasten/diagramme/diagramm_format_panel.py`

„Formatierung“ für einen Teil des Diagramms in der rechten Seitenleiste (nach der Vorlage).

- **class `DiagrammFormatPanel`**(DiagrammFormatWerteMixin, KopfMenueMixin, NurDreiEffekteMixin, AutoFelderMixin, ObjektFormatPanel)
  - `__init__(parent, werte)`
  - `_reiter_kurz()` — Kurze Reitertexte, damit sie bei 300 px lesbar bleiben; der volle Name steht als Tooltip (nur Texte).
  - `_zusatz_radios(abschnitt)`
  - `_zusatz_felder(abschnitt, a)`
  - `_pfeile_freigeben(an)`
  - `_bild_waehlen()`
  - `fuellung_waehlen(art)`
  - `_farbe_waehlen()`
  - `_k_breite()`
  - `_k_breite_setzen(pt)`
  - `_linie_waehlen()`
  - `_seite_fuellung(w)`
  - `_seite_optionen()`
  - `_achse_melden()`
  - `_reihe_melden()`
  - `_seite_eigenschaften()` — Nach der Vorlage nur „Alternativtext“ (Größe und Drehung stellt das Fenster „Layout“ des Objekts ein).
  - `_melde(**kw)`
  - `_melden()`

### `oberflaeche/baukasten/diagramme/diagramm_format_werte.py`

Werte von ``DiagrammFormatPanel`` (Seitenleiste „Diagramm formatieren“): ``werte()`` lesen, ``setze()`` füllen, Teil einrichten.

- **class `DiagrammFormatWerteMixin`** — Werte des Panels lesen und setzen (Füllung, Linie, Optionen, Teil einrichten); ``DiagrammFormatPanel`` baut nur die Oberfläche.
  - `werte()` — Füllung, Linie und Effekte im Format des Teilformats (``None`` = entfernen).
  - `_fuell_wert()`
  - `_fuell_art(tr)` — Die Füllung der gewählten Art: Angaben, ``_OHNE`` (Bildfüllung ohne Bild) oder die Farbe (einfarbig ohne Transparenz).
  - `_bild_fuellung()`
  - `_linie_wert()`
  - `_pfeil_werte()` — Pfeile am Anfang und Ende der Linienreihe; die Vorgabe („keiner“, Größe 1) gilt als nicht gesetzt (None).
  - `_setze(w)`
  - `_setze_fuellung(w)`
  - `_setze_fuellfarben(art, d)`
  - `_setze_linienfelder(li)`
  - `setze(werte)` — Die Felder mit dem Format des Teils füllen; meldet nichts.
  - `_teile_zeigen(werte)` — Die Liste „Teil“ mit den Teilen des Diagramms (``werte["teile"]``, sonst nur der gewählte) und dem gewählten Eintrag.
  - `_hauptreiter_einrichten(teil)` — Die zwei Hauptreiter „<Teil>optionen“ und „Textoptionen“: Name, was wählbar ist, welcher offen steht.
  - `_teil_einrichten(werte)`
  - `_setze_optionen(werte, f)`

### `oberflaeche/baukasten/diagramme/diagramm_text_panel.py`

Textoptionen eines Diagramm-Teils in der Seitenleiste: Textfüllung und -kontur, Schrift, Effekte, „Textfeld“ (``DiagrammTextPanel``).

- **class `DiagrammTextPanel`**(TextFuellartenMixin, TextKopfMenueMixin, _TextPanel) — Textfüllung und -kontur, Effekte (wie bei den Texteffekten) und „Textfeld“. ``werte()`` ist das Textformat des Teils (``diagramm_format``: ``text``).
  - `__init__(parent, werte)`
  - `_dreh_warp_bauen()`
  - `_dreh_zuruecksetzen()`
  - `_warp_bild(art, groesse)` — „abcde“ so verformt, wie der Text gezeichnet wird (derselbe ``pfad_verformen``).
  - `_warp_menue(parent)`
  - `_warp_setzen(art, melden)`
  - `_verbinde()`
  - `_setze(w)`
  - `_setze_dreh(e)`
  - `_setze_schrift(t)`
  - `_setze_feld_alt(f)` — „Textfeld“ ohne ``TextfeldAbschnitt`` (alter Aufbau, SmartArt).
  - `werte()`
  - `_effekt_werte(w)`
  - `_effekt_oder_standard(eff)` — Die Effekte oder None, wenn sie der Standard sind (einfarbige Füllung ohne alles).
  - `_feld_alt_werte()`

### `oberflaeche/baukasten/diagramme/smartart_format_panel.py`

„Formatierung“ für SmartArt in der rechten Seitenleiste: Füllung und Linie, Effekte, Textoptionen — für den gewählten Knoten, ohne Auswahl für alle.

- **class `SmartArtTextPanel`**(DiagrammTextPanel)
- **class `SmartArtFormatPanel`**(DiagrammFormatPanel)
  - `__init__(parent, werte)`
  - `_nur_format()`
  - `_teil_einrichten(werte)`

### `oberflaeche/baukasten/diagramme/smartart_stil_kacheln.py`

Stilkacheln im Band „SmartArt-Design“ nach der Vorlage: Organigramm-Motiv (ein Kasten oben, zwei unten, Linien) in den fünf Stilen.

- `stil_bild_org(nr, groesse, blau)`
- `stile_menue_org(b)`
- `stile_galerie_org(b)`

## `oberflaeche/baukasten/dokument`

### `oberflaeche/baukasten/dokument/__init__.py`

Dokument-, Druck- und Exportbausteine.


### `oberflaeche/baukasten/dokument/aenderungs_fenster.py`

Vorher/Nachher-Fenster einer KI-Antwort in der Seitenleiste (Einfügen, Ersetzen, Kopieren).

- **class `AenderungsFenster`**(PanelFaehig, QDialog) — ``dienst``: der KI-Dienst; ``nr``: Kennung der Chat-Nachricht (nicht der Index). Aktueller Stand: ``self.lage()`` (= ``dienst.antwort_lage``),
  - `__init__(dienst, nr, parent)`
  - `_bereich(v, titel, *, kopieren)` — Überschrift (bei ``kopieren`` mit Kopier-Symbol rechts in derselben Zeile) und darunter das Feld, das den freien Platz teilt.
  - `passe_an(_breite, hoehe)` — Die Seite nimmt die ganze Höhe der Seitenleiste; die beiden Felder teilen sich, was Überschriften und Knöpfe übrig lassen.
  - `index()`
  - `lage()`
  - `neu_lesen()` — Zustand des Dienstes neu lesen: Texte, Knöpfe, Hinweis. Ist die Antwort nicht mehr im Gespräch, sind die Aktionen gesperrt.
  - `_hinweis(text)`
  - `_trennen(*_)`
  - `_einfuegen()`
  - `_ersetzen()`
  - `_rezension()`
  - `_anwenden(aktion)`

### `oberflaeche/baukasten/dokument/aenderungs_vorschau.py`

Änderungsvorschau: schreibgeschütztes Feld, das Stücke ``(art, text)`` zeigt — „entfernt“ durchgestrichen, „neu“ unterstrichen, „gleich“ normal.

- `_hinterlegt(farbe)`
- **class `AenderungsVorschau`**(QTextEdit)
  - `__init__(stuecke, *, frei)`
  - `stuecke_setzen(stuecke, markdown)` — ``markdown``: „neu“-Stücke sind Markdown und erscheinen so, wie sie ins Dokument kommen (Überschriften, Listen, Tabellen, Hervorhebungen).
  - `_format(art)`
  - `_zeichnen()`
  - `_hoehe()`
  - `resizeEvent(e)`
  - `changeEvent(e)`

### `oberflaeche/baukasten/dokument/druck_dialog.py`

Das Druckfenster: oben die Reiter „Standard“, „Lunivo-Office“ und „Drucker“, darunter die Vorschau des Blattes (eine Spalte).

- `_kopf(text)`
- `_drucker_liste()`
- `_combo(eintraege, aktuell)`
- **class `_Reiter`**(AngepassteReiter) — Reiter, deren Höhe mit der Breite mitgeht: schmal umbrechen die Beschriftungen, die Seite wird höher (sonst überlappen die Felder).
  - `hasHeightForWidth()`
  - `heightForWidth(w)`
- **class `DruckAnsicht`**(QWidget) — Reiter oben, Vorschau darunter. ``geaendert`` kommt bei jeder Änderung der Wahl.
  - `__init__(seiten, papier_mm, quer, start, *, auswahl, vorschau, parent)`
  - `_angeordnet(breit)`
  - `_standard(s, hoch, quer, auswahl)`
  - `_papier_combo(aktuell)`
  - `_programm(s)`
  - `_druckerseite(s)`
  - `_verdrahten()`
  - `_gleich(von, nach)`
  - `_drucker_gewaehlt(*_)`
  - `drucker_setzen(kopien, beidseitig)` — Nach den Einstellungen des Systems: Kopien und Beidseitig übernehmen.
  - `ergebnis()`
  - `gueltig()` — Ein eigener Seitenbereich muss mindestens eine Seite treffen.
  - `_blatt_mm()`
  - `_blaetter()`
  - `_aenderung()`
  - `_gehe(i)`
  - `_neu_laden()`
  - `_zeichnen(p, r)`
- **class `DruckDialog`**(PanelFaehig, QDialog) — Das Druckfenster mit Knopfzeile: Hilfe links, „Abbrechen“ und „Drucken“ rechts.
  - `__init__(parent, seiten, papier_mm, quer, start, *, auswahl, vorschau, hilfe)`
  - `_pruefen()`
  - `ergebnis()`

### `oberflaeche/baukasten/dokument/druckvorschau.py`

Die Druckvorschau als ganzes Fenster: oben Drucken…, Blattwechsel, Ansicht (Eine/Zwei/Alle Seiten), Zoom, Einpassen, Vorschau schließen.

- **class `DruckVorschau`**(QDialog)
  - `__init__(parent, quelle)`
  - `_zoomknopf(text, tip, faktor)`
  - `_schritt()`
  - `showEvent(e)`
  - `einpassen()` — Zoom, bei dem die Seiten der Ansicht ganz ins Fenster passen (bei „Alle Seiten“ die Breite einer Seite).
  - `_zoom_setzen(z)`
  - `_gehe(n)`
  - `_aufbauen()`

### `oberflaeche/baukasten/dokument/eingabe_fenster.py`

Kleine Abfrage in der Seitenleiste: eine Frage, darunter eine Auswahl oder ein Textfeld, unten „Abbrechen“ und „OK“.

- **class `EingabeFenster`**(PanelFaehig, QDialog) — Frage mit Auswahlliste (``eintraege``) oder, ohne Einträge, mit einem Textfeld.
  - `__init__(parent, titel, frage, eintraege, aktuell, text, kennwort, mehrzeilig, datum)`
  - `wert()` — Der gewählte Eintrag oder der getippte Text.
  - `getItem(parent, titel, frage, eintraege, aktuell, bearbeitbar)` — Wie ``QInputDialog.getItem``; (``bearbeitbar`` gibt es nicht — Auswahl nur aus der Liste).
  - `getText(parent, titel, frage, text, kennwort)` — Wie ``QInputDialog.getText``; ``kennwort=True`` zeigt Punkte statt der Zeichen.
  - `getMultiLineText(parent, titel, frage, text)` — Wie ``QInputDialog.getMultiLineText``.
  - `getDatum(parent, titel, frage, datum)` — Ein Datum aus dem Kalender wählen; Rückgabe ``(QDate, ok)``.
  - `zeigeAuswahl(parent, optionen, global_pos, gewaehlt)` — Auswahlfeld im Text: Liste der Möglichkeiten an ``global_pos``; ein Eintrag ruft ``gewaehlt(eintrag)``.
- `_beim_editor_anmelden()` — Der Editor fragt über ``formular.eingabe_anbieter``; er kennt die Oberfläche nicht, hier wird ihm dieses Fenster mitgegeben.

### `oberflaeche/baukasten/dokument/erstellen_fenster.py`

Basis der Erstellen-Fenster „Schnelle KI-Aktion“ und „Neuen Assistenten erstellen“: Hinweis, Vorlagen-Chips, Name, Prompt, Knopfzeile.

- **class `ErstellenFenster`**(PanelFaehig, QDialog)
  - `__init__(fenster, titel, hinweis, vorlagen_namen, *, meldung, ok_text)`
  - `name_zeile(beschriftung, platzhalter, symbol)` — Namensfeld; mit ``symbol`` (Symbolwahl) steht es links daneben, die Beschriftungen darüber.
  - `prompt_zeile(beschriftung, platzhalter)`
  - `abschliessen()`
  - `vorlage_gewaehlt(i)` — Hier füllt die Unterklasse die Felder aus der Vorlage Nr. ``i``.
  - `_ok()`

### `oberflaeche/baukasten/dokument/layout_dialog.py`

Das Fenster „Layout“ für Bilder und Formen: Position, Textumbruch, Größe — nach der Vorlage.

- `_combo(eintraege, aktuell)`
- `_zeile(g, _r, radio, *rest)` — Eine Wahlzeile: der Knopf mit seinem Feld, dahinter (falls da) „Beschriftung + Feld“ — nebeneinander oder untereinander, je nach Breite.
- **class `LayoutDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, werte)`
  - `_achse(titel, w, waagerecht)`
  - `_achse_ein(f)` — Nur die Felder der gewählten Zeile sind bedienbar (wie in der Vorlage).
  - `_position(w)`
  - `_umbruch(w)`
  - `_mass(titel, w)`
  - `_groesse(w)`
  - `_orig_anzeigen()`
  - `_skal_nachziehen()` — Die Skalierung in Prozent aus der aktuellen Größe im Verhältnis zur Originalgröße.
  - `_skal_bezug()` — Wovon die Prozente gelten: die Originalgröße des Bildes — oder die Größe beim Öffnen, wenn „Relativ zur Originalbildgröße“ aus ist.
  - `_groesse_geaendert(hoehe)` — Höhe oder Breite getippt: bei gesperrtem Seitenverhältnis zieht das andere Maß mit.
  - `_skal_geaendert(hoehe)`
  - `_zuruecksetzen()`
  - `_pruefen()` — Zeilenumbruch und Abstand zum Text gelten nur bei Quadrat, Passend und Transparent.
  - `_achse_lesen(f)`
  - `_mass_lesen(f)`
  - `werte()`

### `oberflaeche/baukasten/dokument/layout_dialog_objekt.py`

Das Fenster „Layout“ eines Bildes oder freien Objekts nach der Vorlage (Fotos „Im Textfluss“ und „SmartArt“).

- **class `LayoutDialogObjekt`**(LayoutDialog)
  - `__init__(parent, werte, art)`
  - `_pruefen()`
  - `_abstand_ordnen()`
  - `_relativ_sperren()`
  - `_ohne_original()`
  - `_orig_anzeigen()`
- `layout_dialog_fuer(art)` — Der Fensterbau für die Objektart: ``layout_dialog_fuer(art)(parent, werte)``.

### `oberflaeche/baukasten/dokument/liste_dialog.py`

Die Fenster „Nummerierung und Aufzählungszeichen“ und „Nummerierung anpassen“ als Bausteine.

- `benutzerlisten()`
- `_merke(listen)`
- `_rahmen(p, groesse)`
- `_bild(spec, groesse)`
- `_raster(eintraege, bild)`
- **class `_Zahlenformat`**(QWidget) — Zahlenformat, Zahlenart, Startzahl und „Schriftart …“ der Nummer — gemeinsam für „Nummerierung anpassen“ und „Gliederung anpassen“.
  - `__init__(tipp, breit)` — ``breit``: die Anordnung der Gliederung (Zahlenformat und Vorlage über die ganze Breite, „Beginnen mit“ in einer eigenen Zeile;
  - `setze(format, stil, start, zeichen)`
  - `_schriftart()`
- **class `_Positionen`**(QWidget) — Nummernposition (Ausrichtung der Nummer, Abstand) und Textposition (Tabstopp-Leerstelle nach, Einzug bei) — gemeinsam für
  - `__init__()`
  - `setze(ausr, art, tab, einzug)`
  - `werte()`
- **class `NummerierungAnpassenDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, spec)`
  - `_erweitern(an)`
  - `_pos_neu()`
  - `spec()`
  - `_zeichen()`
  - `_zeichen(w)`
  - `_neu()`
  - `_male(p, rect)` — Vorschau wie in der Vorlage: oben und unten graue Balken, dazwischen drei Nummern mit je zwei schwarzen Zeilen.
- `_gl_bild(defn, groesse)` — Kachel einer Gliederung: die Ebenen 1 bis 3 mit ihren Nummern.
- **class `GliederungAnpassenDialog`**(PanelFaehig, QDialog) — „Gliederung anpassen“ (auch „Aufzählungszeichen anpassen“): je Ebene Zahlenformat, Zahlenart, Startzahl, Schriftart, Position und Text,
  - `__init__(parent, defn, *, titel)`
  - `_erweitern(an)`
  - `_wechsel(i)`
  - `_lesen()`
  - `_vorher_gewaehlt(_i)`
  - `_pruefen()`
  - `defn()`
  - `_male(p, rect)` — Die neun Ebenen mit ihren Nummern; die gewählte Ebene hat schwarze Linien, die anderen graue (wie in der Vorlage).
- **class `_KachelFueller`**(QObject) — Ein Kachelraster füllt seine Breite mit drei Kacheln je Zeile (Größe folgt der Breite) und ist genau so hoch wie seine Zeilen.
  - `__init__(raster, spalten)`
  - `eventFilter(obj, ev)`
  - `_anpassen()`
- **class `ListenDialog`**(PanelFaehig, QDialog)
  - `kompakt_machen()` — Für die schmale Seitenleiste: kleinere Kacheln (drei je Zeile), Reiter mit Überlauf hinter „•••“, Fenster ohne feste Größe.
  - `passe_an(breite, hoehe)` — Je breiter die Seitenleiste, desto mehr Kacheln je Zeile (vier bis sechs), damit die Auswahl ohne Rollen auskommt.
  - `__init__(parent, aktuell, *, seite)`
  - `_anfangsauswahl(aktuell, seite)` — Die Auswahl beim Öffnen: das bisherige Format, sonst die Vorgabe des Aufrufs (Aufzählung oder Nummerierung).
  - `_raster_zu(aktuell)` — Das Raster, in dem ein bisheriges Format steht: Gliederung, Aufzählung oder Nummerierung.
  - `_fuelle_benutzer()`
  - `_male(p, rect)`
  - `_eintragen(s)` — Ein selbst angepasstes Format kommt in den Reiter „Nummerierung“ und in die Liste der eigenen Formate.
  - `_eintragen_gl(d, raster)`
  - `_aktuell()`
  - `_auswahl()`
  - `_knoepfe(*_)`
  - `_anpassen()`
  - `_loeschen()`
  - `ergebnis()` — Die gewählte Liste, oder None bei „Kein“.
- `kachel_bild(spec, groesse)` — Dieselbe Kachel wie im Fenster „Nummerierung und Aufzählungszeichen“, verkleinert für die Auswahl im Band.
- `aufzaehlungen()` — Die Aufzählungsarten der Auswahl: Punkt, Quadrat und die Zeichen ◆ ✤ ➤ ✓ ✧ (wie im Fenster).
- `nummerierungen()`

### `oberflaeche/baukasten/dokument/pdf_export.py`

Eingebettete, schrittweise PDF-Exportansicht für Lunivos Datei-Menü.

- `_abschnitt(titel, hilfe, layout)`
- `_einklappen(titel, beschreibung, inhalt, offen)`
- `_kennwort()`
- **class `PdfExportAnsicht`**(QWidget) — PDF-Export als dauerhaft sichtbare zweite Menüspalte, keine separates Dialogfenster.
  - `__init__(parent, start, seiten, aktuelle, markierung, exportieren, zurueck)`
  - `_schutz(s)`
  - `_seiten_schalten(an)`
  - `_durchsuchen()`
  - `ergebnis()`
  - `_ok()`
  - `wahl()`

### `oberflaeche/baukasten/dokument/sortieren_dialog.py`

Das Fenster „Text sortieren“ als Baustein (Start ▸ Absatz ▸ Sortieren): ein Hauptschlüssel und bis zu zwei weitere („Anschließend nach“),

- `_feld(w, breite)` — Feldhöhe wie überall; ``breite`` nur für kleine Felder (ein Zeichen), sonst richtet sich das Feld nach dem Gitter.
- **class `SortierOptionenDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, trenner, gross_klein, sprache, nur_spalte)`
  - `trenner()`
- **class `_Schluessel`** — Ein Schlüssel „nach … Typ … Aufsteigend/Absteigend“ im ``FormularGitter`` ``g``: Feld über die Breite, darunter Typ, dann die Richtung.
  - `__init__(g, eltern, mit_keine)`
  - `fuellen(felder)`
  - `_aktiv()`
  - `wert()`
- **class `SortierenDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, texte)`
  - `_aktualisieren()` — Felder gibt es erst, wenn die Absätze durch den Trenner geteilt sind; ohne Felder sind die weiteren Schlüssel und die
  - `_optionen()`
  - `werte()`

### `oberflaeche/baukasten/dokument/speichern_fenster.py`

Das eine Speichern-Fenster: Orte links, Ordnerinhalt rechts, unten Dateiname und Dateityp.

- `stil()` — Stylesheet beim Aufruf formatiert, damit das Thema gilt.
- `_symbol(name, px)`
- **class `_DateiModell`**(QFileSystemModel) — Dateimodell mit deutschen Spaltenköpfen (Qt liefert sie sonst englisch).
  - `headerData(section, orientation, role)`
- **class `_Symbole`**(QFileIconProvider) — Ordner und Dateien in der Liste mit denselben Liniensymbolen wie der Rest des Fensters.
  - `__init__()`
  - `icon(info)`
- `_ordner(art)`
- **class `SpeichernFenster`**(QDialog) — ``typen``: Liste (Endung, Filtertext) wie („.docx“, „DOCX-Dokument (*.docx)“). ``ergebnis()`` → (Pfad, Endung).
  - `__init__(parent, titel, startpfad, typen, vorwahl, oeffnen, mehrere)`
  - `_bauen_links(titel)` — Links: Titel und Orte.
  - `_bauen_leiste(rv)` — Rechts oben: Zurück/Vor/Hoch, Pfad, Neuer Ordner, Ansichten.
  - `_bauen_ansichten(rv)` — Dateiliste (Baum) und Kacheln im Stapel.
  - `_bauen_unten(rv, name, vorwahl, oeffnen)` — Name und Typ mit den Knöpfen; liefert die beiden Beschriftungen.
  - `_modus_anpassen(l1, l2, oeffnen, mehrere)` — Öffnen (auch mehrere) und Ordner wählen weichen von „Speichern“ ab.
  - `_ort(text, pfad, ic)`
  - `_knopf(ic, tipp, aktion, pruefbar)`
  - `endung()`
  - `gehe_zu(pfad, merken)`
  - `zurueck()`
  - `vor()`
  - `hoch()`
  - `_pfad_zeigen()`
  - `ansicht(nr)`
  - `neuer_ordner()`
  - `_filter_setzen()`
  - `_typ_gewechselt()`
  - `_angeklickt(idx)`
  - `_auswahl_geaendert(*_a)`
  - `_doppelklick(idx)`
  - `zielpfad()` — Pfad aus Ordner und Dateiname; die Endung des gewählten Dateityps gilt (eine andere bekannte wird ersetzt).
  - `speichern()` — Die Eingabe im Namensfeld bestätigen: je nach Art des Fensters Dateien öffnen, einen Ordner wählen oder den Speicherort festlegen.
  - `_warnen(text)`
  - `_hinein(ordner)` — Ein Ordnername wurde eingegeben: hineingehen statt bestätigen.
  - `_oeffnen_bestaetigen(text)`
  - `_ordner_bestaetigen(text)`
  - `_speicherort_bestaetigen(text)`
  - `_ersetzen_erlaubt(pfad)` — Fragt, ob die vorhandene Datei ersetzt werden darf (Vorgabe: Abbrechen).
  - `ergebnis()`
  - `dateien()`
- `speicherort_waehlen(parent, titel, startpfad, typen, vorwahl)` — Öffnet das Speichern-Fenster. → (Pfad mit Endung, Endung) oder None bei Abbruch.
- `ordner_waehlen(parent, titel, startordner)` — Dasselbe Fenster zum Wählen eines Ordners. → Ordner oder None bei Abbruch.
- `datei_waehlen(parent, titel, start, filter_text, mehrere)` — Dasselbe Fenster zum Öffnen. ``filter_text`` im Qt-Stil („Dokumente (*.docx *.odt);;Alle Dateien (*)“).
- `datei_speichern(parent, titel, startpfad, filter_text)` — Speichern mit einem Filter im Qt-Stil („JSON (*.json)“) — für Lunivos eigene Dateien (Sicherungen, Gelerntes …).
- **class `Dateifenster`** — Dieselben Aufrufe wie ``QFileDialog.get…`` (Rückgabe wie dort), aber mit Lunivos eigenem Fenster.
  - `getOpenFileName(parent, titel, start, filter_text, *_a, **_k)`
  - `getOpenFileNames(parent, titel, start, filter_text, *_a, **_k)`
  - `getSaveFileName(parent, titel, start, filter_text, *_a, **_k)`
  - `getExistingDirectory(parent, titel, start, *_a, **_k)`
- `_ordner_name_fragen(parent)` — Kleines Fenster „Neuer Ordner“ in der Größe der übrigen Felder (statt des winzigen Eingabefensters von Qt).

### `oberflaeche/baukasten/dokument/stimme_dialog.py`

Das Fenster „Stimme und Tempo“ als Baustein: Stimme aus einer ``AuswahlListe``, die den freien Platz füllt, Tempo mit Regler.

- **class `StimmeDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, stimmen, kennung, tempo, bereich)`
  - `passe_an(_breite, hoehe)` — Die Seite nimmt die ganze Höhe der Seitenleiste; die Stimmenliste füllt, was Tempo und Hinweis übrig lassen.
  - `stimme()`
  - `tempo()`

### `oberflaeche/baukasten/dokument/tabstopp_dialog.py`

Das Fenster „Tabstopps“ als Baustein: Position, Ausrichtung und Füllzeichen festlegen, löschen, alle löschen.

- `aus_block(bf)` — Die Tabstopps eines Absatzformats als Liste aus Millimetern, Ausrichtung und Füllzeichen.
- `zu_block(bf, stopps)` — Tabstopps (mm, Ausrichtung, Füllzeichen) in ein Absatzformat schreiben.
- `als_text(stopps)` — Tabstopps als Text für eine Formatvorlage: ``30.0:rechts:punkt;80.0:mitte:`` (leer = keine).
- `aus_text(text)`
- `_text(mm, art, fuell)`
- **class `TabstoppDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, stopps, standard_mm)` — ``standard_mm``: Standardabstand der Tabstopps des Dokuments (``None``: das Feld bleibt weg).
  - `_fuellen()`
  - `_knoepfe(*_)`
  - `_zeile(i)`
  - `festlegen()`
  - `loeschen()`
  - `alle()`
  - `stopps()`
  - `standard_abstand()` — Der Standardabstand in Millimetern (``None``, wenn das Fenster ohne dieses Feld aufgerufen wurde).

### `oberflaeche/baukasten/dokument/tasten_dialog.py`

Das Fenster „Tastenkombination“ als Baustein: eine Tastenkombination aufnehmen und zuweisen.

- **class `TastenDialog`**(QDialog)
  - `__init__(parent, aktuell, *, belegt)`
  - `taste()`
  - `_pruefen(*_)`

## `oberflaeche/baukasten/dropdown`

### `oberflaeche/baukasten/dropdown/__init__.py`

Dropdown- und Menübausteine.


### `oberflaeche/baukasten/dropdown/auswahlfeld.py`

Auswahlfeld: das eine Dropdown für ganz Lunivo.

- **class `_KuerzDelegate`**(QStyledItemDelegate) — Zeilenhöhe wie in den Menüs (Schrifthöhe + 2 × Abstand aus mass.py), Text mittig gekürzt.
  - `sizeHint(option, index)`
  - `paint(painter, option, index)`
- `popup_begrenzen(combo, popup_min)` — Nach ``showPopup()`` aufrufen: Größe der Liste (Breite, sichtbare Zeilen); die Lage in Fenster und Bildschirm bestimmt ``popup_klemmen``.
- **class `_Feldlaenge`** — Gemeinsam für ``Auswahlfeld`` und ``Schriftauswahl``: die Länge des Feldes in Zeichen (Rolle statt fester Zahl am Aufrufer).
  - `zeichen(n)`
  - `rolle(rolle, variante, *, mindest)` — Die Breite des Feldes aus der zentralen Tabelle ``DROPDOWN_BREITE`` (Rolle × Layoutvariante: band, leiste, mini, dialog, feld).
  - `an_inhalt()` — Das Feld ist so breit wie sein längster Eintrag (z. B. kurze feste Listen).
- **class `Auswahlfeld`**(_Feldlaenge, QComboBox)
  - `__init__(parent, *, min_zeichen, popup_min)`
  - `als_menue_nach_oben(an, zusatz)` — Statt der Liste öffnet das Feld eine ``MenueListe`` über sich (Häkchen rechts am gewählten Eintrag); Auswahl setzt wie gewohnt den Index.
  - `_menue_zeigen()`
  - `showPopup()`
  - `hidePopup()`
  - `paintEvent(event)`
- **class `Schriftauswahl`**(_Feldlaenge, QFontComboBox) — Schriftart-Auswahl; behält die Schriftvorschau der Einträge, begrenzt nur die Liste.
  - `__init__(parent, *, min_zeichen)`
  - `showPopup()`

### `oberflaeche/baukasten/dropdown/dropdown_knopf.py`

Dropdown-Knopf: der Knopf mit Pfeil, der ein Menü öffnet (Stufe 4 der Dropdown-Pyramide).

- **class `_DropdownBasis`**
  - `groesse_rolle(rolle, variante)` — Die Größe des Knopfes aus der zentralen Tabelle ``DROPDOWN_KNOPF`` (Rolle × Layoutvariante: band, mini, kopf, dokument).
  - `gross(textbreite, kompakt)` — Großer Bandknopf (Text unter dem Symbol): Breite folgt dem Text, Höhe je Dichte (kompakt oder normal) aus ``mass.py``.
  - `band_zeile()` — Knopf in einer Bandzeile: Mindesthöhe der Kopf-Dropdowns (eine Quelle in ``mass.py``), damit die Zeilen fluchten.
  - `menue_setzen(menue, *, geteilt, gross, fuellend, besitzen)` — ``geteilt``: True = Symbol und Pfeil getrennt (``MenuButtonPopup``), False = ein Klick öffnet das Menü (``InstantPopup``), None = Modus bleibt.
- **class `DropdownKnopf`**(_DropdownBasis, QToolButton) — Werkzeugknopf, der ein Menü öffnet.
- **class `DropdownTaste`**(_DropdownBasis, QPushButton) — Taste mit Text, die ein Menü öffnet.
  - `__init__(*args, **kw)`

### `oberflaeche/baukasten/dropdown/galerie_auswahl.py`

Galerie-Popup: Kacheln mit einer Textprobe in der jeweiligen Schrift und dem Namen darunter (Formatvorlagen, später Tabellen-

- **class `_Kachel`**(QWidget)
  - `__init__(schluessel, name, probe, schrift, farbe, groesse, aktuell, tipp)`
  - `enterEvent(e)`
  - `leaveEvent(e)`
  - `contextMenuEvent(e)`
  - `mouseReleaseEvent(e)`
  - `paintEvent(_e)`
- **class `GalerieAuswahl`**(MenueListe) — Meldet den Schlüssel der gewählten Kachel.
  - `__init__(parent, *, titel, spalten, kachel, zeilen_sichtbar)`
  - `kachel(schluessel, name, schrift, *, probe, farbe, aktuell, tipp)`
  - `aktion(text, fn, symbol, *, haken, aktiv)` — Zeile unter der Galerie (z. B. „Neue Formatvorlage …“); schließt das Popup und ruft ``fn``.
  - `_haken_symbol()`

### `oberflaeche/baukasten/dropdown/kopf_dropdown.py`

Dropdown im Kopf eines Abschnitts („FÜLLUNG ▾ [Feld ▾]“, „LINIE ▾ [Strich ▾]“ der Vorlage): ein weißes Feld mit dem aktuellen Ergebnis und kleinem

- `keine_symbol(groesse)` — Das Zeichen der Zeile „Keine …“: Quadrat mit rotem Schrägstrich.
- `keine_zeile(menue, text)` — Die klickbare Zeile „Keine …“ ganz oben im Popup (Zeichen + Text); sie meldet den Schlüssel ``""``.
- **class `KopfDropdown`**(QPushButton)
  - `__init__(fabrik, symbol, parent)`
  - `sizeHint()`
  - `setSymbol(symbol)`
  - `an(abschnitt)` — Rechts in den Kopf des ``Abschnitt`` setzen (hinter den Streckungsraum).
  - `_popup()`
  - `paintEvent(_e)` — Ein Feld wie die übrigen der Seitenleiste (Farbfeld „Automatisch“): Rahmen, Hintergrund und Rundung vom Thema, darin nur das Ergebnis und der Pfeil.

### `oberflaeche/baukasten/dropdown/kopf_menue_mixin.py`

Dropdowns in den Köpfen von „FÜLLUNG“ und „LINIE“ des Diagramm-Panels (Vorlage): Mixin vor ``ObjektFormatPanel``.

- `_hex(farbe)`
- **class `KopfMenueMixin`**
  - `_kopf_menues_bauen()`
  - `_fuell_voreinstellung(schluessel)`
  - `_linien_voreinstellung(schluessel)`
  - `_fuell_spec()`
  - `_fuell_schluessel()`
  - `_linien_spec()`
  - `_linien_schluessel()`
  - `_kopf_aktualisieren()`
  - `_felder_zeigen()`

### `oberflaeche/baukasten/dropdown/menue_liste.py`

Menü-Liste: Zeilen mit Symbol, Text, Tastenkürzel, Haken und Untermenü — überall dieselbe Gestalt.

- **class `MenueListe`**(PopupVerhalten, QMenu) — Ein Menü, das Zeilen einheitlich aufbaut. Nicht Mögliches bleibt grau sichtbar statt zu fehlen.
  - `eintrag(text, aktion, *, symbol, kuerzel, haken, aktiv, tip, daten, echt, gruppe)` — ``kuerzel`` (Text oder ``QKeySequence``) wird nur angezeigt; mit ``echt=True`` ist es ein wirkliches Tastenkürzel
  - `vorhanden(a)` — Eine schon bestehende Aktion (z. B. aus der Hauptfenster-Aktionstabelle) als Zeile übernehmen.
  - `einhaengen(text, menue, symbol)` — Ein fertiges Menü (z. B. ein Raster) als Untermenü-Zeile mit ``text`` einhängen.
  - `untermenue(text, symbol, aktiv, *, wert, tip)` — Untermenü-Zeile. ``wert``: aktueller Wert, rechts in der Zeile vor dem Pfeil (wie ein Kürzel). ``tip``: Hinweis, auch bei grauer Zeile.
  - `untermenue_einhaengen(sub, titel)` — Ein vorhandenes Menü (z. B. das Klappmenü eines anderen Knopfes) als Untermenü übernehmen; es gehört danach diesem Menü.
  - `widget(w)` — Ein eingebautes Bedienfeld (Raster, Reiter, Zeile) als einzige Zeile des Menüs oder zwischen anderen Zeilen.
  - `schalter(text, an, aktion, *, symbol)` — Zeile mit kleinem Kippschalter (z. B. „Websuche“). ``aktion(an)`` läuft beim Umschalten; zurückgegeben wird die ``SchalterZeile``
  - `kompakt()` — Layoutvariante „kompakt“ (schmalere Zeilen) — für das Tabellenmenü; die übrigen Menüs behalten das Standardmaß.
  - `standard(widget, parent)` — Das Standard-Kontextmenü eines Qt-Textfeldes (``createStandardContextMenu``) als Menüliste, mit deutschen Texten.
  - `in_leiste(leiste, titel)` — Ein Menü der Menüleiste (``QMenuBar``) mit dem Titel ``titel``.
  - `trenner()`
  - `aus_liste(zeilen, parent)` — Baut ein Menü aus einer Beschreibung: ``"-"`` = Trennlinie, sonst ein Wörterbuch mit text, aktion, symbol,
  - `_fuellen(zeilen)`

### `oberflaeche/baukasten/dropdown/menue_tafel.py`

Das ☰ Menü: links die Datei-Befehle, rechts der Inhalt (zuletzt verwendete Dateien oder die Punkte eines Untermenüs).

- `_menue_symbol(name)`
- `_datum(pfad)` — Änderungsdatum der Datei für die Liste „Zuletzt verwendet“ (leer, wenn es sie nicht mehr gibt).
- **class `MenueTafel`**(PopupVerhalten, QFrame)
  - `__init__(punkte, befehle, fenster)`
  - `eventFilter(obj, ev)`
  - `_leeren()`
  - `_zeige_zuletzt()`
  - `_zeige_unter(p)`
  - `_klick(p)`
  - `zeigen_unter(widget)`

### `oberflaeche/baukasten/dropdown/popup_lage.py`

Popup-Lage: das eine Öffnungsverhalten für alle aufklappenden Fenster (Menüs, Klapplisten, Popup-Fenster).

- `popup_bereich(anker, schirm_geometrie)` — Der Bereich, in dem ein von ``anker`` aufklappendes Fenster liegen darf: nächste Grenze oberhalb des Ankers (Eigenschaft
- `popup_klemmen(pop, anker)` — Die Öffnungsregeln für jedes aufklappende Fenster. True, wenn es verschoben wurde.
- **class `PopupVerhalten`** — Basis aller aufklappenden Fenster (Menüs, Galerien, Popup-Widgets): Wer von ihr erbt, öffnet sich nach denselben Regeln.
  - `showEvent(ev)`

### `oberflaeche/baukasten/dropdown/schalter_zeile.py`

Schalter-Zeile für Menüs: Symbol, Text und kleiner Kippschalter (``KippSchalter``). Ein Klick auf die ganze Zeile schaltet um; das Menü bleibt offen.

- **class `SchalterZeile`**(QWidget)
  - `__init__(text, an, symbol, parent)`
  - `an()`
  - `an_setzen(an)` — Zustand von außen nachziehen, ohne ``umgeschaltet`` zu senden.
  - `mousePressEvent(e)`

### `oberflaeche/baukasten/dropdown/teil_menue.py`

Der Pfeil am Hauptreiter („DIAGRAMM OPTIONEN ▾“): öffnet die Liste der Teile des Diagramms, der aktuelle Teil trägt einen Haken.

- **class `TeilMenueKnopf`**(QToolButton)
  - `__init__(parent)`
  - `setze(teile, aktuell)`
  - `aktuell()`
  - `_menue()`
  - `_waehlen(schluessel)`
  - `_oeffnen()`

### `oberflaeche/baukasten/dropdown/text_kopf_menue_mixin.py`

Dropdowns in den Köpfen von „TEXTFÜLLUNG“ und „TEXTKONTUR“ der Textoptionen des Diagramms (Vorlage): Mixin vor ``TexteffektPanel``/``_TextPanel``.

- `text_fuell_menue(parent, aktuell)` — „Keine Füllung“, die Farbpalette und graduelle Füllung (Muster und Struktur gibt es beim Text nicht).
- `_text_bild(text, groesse)`
- **class `TextKopfMenueMixin`**
  - `_text_kopf_bauen()`
  - `_text_fuell_wahl(schluessel)`
  - `_text_fuell_schluessel()`
  - `_text_linien_schluessel()`
  - `_text_kopf_aktualisieren()`
  - `_neu(*a)`
  - `_setze_fuellung(w)`

### `oberflaeche/baukasten/dropdown/voreinstellung_menue.py`

Auswahl von Voreinstellungen als Popup mit Bildchen in Abschnitten (Schatten: Kein, Außen, Innen, Perspektive; Leuchten; Spiegelung;

- **class `VoreinstellungMenue`**(MenueListe)
  - `__init__(parent, *, keine, kachel)`
  - `_kopf(text)`
  - `_gitter(eintraege, spalten)`
  - `abschnitt(titel, eintraege, spalten)`
  - `_waehle(schluessel)`

### `oberflaeche/baukasten/dropdown/zeile.py`

Dropdown-Zeile: die eine Gestalt jeder Zeilentaste in aufklappenden Fenstern (Menütafel, Raster, Galerie, Bildmenüs).

- `dropdown_zeile(taste, *, hinweis)` — Macht ``taste`` zur Dropdown-Zeile; ``hinweis``: kleinere Schrift (Hinweis-Zeilen wie „Zuletzt geöffnet“).

## `oberflaeche/baukasten/dropdown/auswahl`

### `oberflaeche/baukasten/dropdown/auswahl/__init__.py`

Unterpaket ``auswahl`` von ``writer.baukasten.dropdown``.


### `oberflaeche/baukasten/dropdown/auswahl/farbpalette.py`

Die eine Farbpalette des Programms: Popup, Farbfeld für Dialoge und geteilter Knopf fürs Band.

- `weitere_farben(parent, start, titel)` — „Weitere Farben …“: das Fenster „Farben“ (Standard · Benutzerdefiniert · Erweitert). Gibt die Farbe zurück oder ``None`` bei Abbruch.
- `weitere_farben_unter(parent, fertig, start, titel)` — Wie ``weitere_farben``, aber als Unterfenster: Liegt ``parent`` in einem ``FensterStapel``, öffnet sich „Farben“ als Seite im selben Fenster;
- `farb_symbol(farbe, groesse)`
- **class `_Kachel`**(QWidget) — Ein Farbfeld der Palette; meldet Überfahren und Klick an die Palette.
  - `__init__(palette, farbe, seite)`
  - `enterEvent(e)`
  - `leaveEvent(e)`
  - `mouseReleaseEvent(e)`
  - `paintEvent(e)`
- **class `_VerlaufKachel`**(_Kachel) — Kachel der Zeile „Graduelle Füllung“: ein Farbverlauf von hell nach dunkel in der Farbe; ein Klick meldet die Farbe als Verlauf.
  - `mouseReleaseEvent(e)`
  - `paintEvent(e)`
- **class `_BildKachel`**(_Kachel) — Kachel einer Bildreihe („Musterfüllung“, „Strukturfüllung“): zeigt ein Bild; ein Klick meldet ihren Schlüssel.
  - `__init__(palette, schluessel, bild, tipp, seite)`
  - `enterEvent(e)`
  - `leaveEvent(e)`
  - `mouseReleaseEvent(e)`
  - `paintEvent(e)`
- **class `FarbPalette`**(MenueListe) — Popup mit „Keine Farbe“, Themenfarben (Grundfarben + Abstufungen), Standardfarben, zuletzt Benutzten, „Weitere Farben …“.
  - `__init__(parent, *, keine_text, start, titel, zuletzt, weitere, verlauf, verlauf_titel, weitere_text, automatisch, pipette, standard, reihen)`
  - `zusatz_eintrag(text, aktion)` — Ein weiterer Eintrag unter „Weitere Farben …“ (z. B. „Rahmen und Schattierung …“); schließt die Palette und ruft ``aktion``.
  - `_titel_zeile(text)`
  - `_keine_symbol()`
  - `_raster(zeilen)`
  - `waehle(farbe)` — Farbe übernehmen: merken, melden, Popup schließen.
  - `_pipette()` — „Pipette“: eine Farbe vom Bildschirm aufnehmen.
  - `_weitere()`
- **class `FarbFeld`**(QPushButton) — Knopf für Dialoge, der seine Farbe zeigt; ein Klick öffnet die Palette. ``farbe`` ist ein Hex-Text ('' = keine).
  - `__init__(farbe, titel, keine_text, parent, verlauf)`
  - `setFarbe(farbe)`
  - `_waehle()`
  - `_zeige_popup(pal)`
  - `_uebernehmen(c)`
  - `_zeige()` — Ruhig und sachlich: ein kleines Farbfeld mit Rand und der Name daneben — kein Knopf, der selbst bunt wird.
- **class `FarbKnopf`**(QToolButton) — Geteilter Knopf fürs Band: Klick auf das Symbol wendet die letzte Farbe an, der Pfeil klappt die Palette auf.
  - `__init__(symbol, text, farbe, *, keine_text, titel, parent)`
  - `menu_neu()`
  - `_gewaehlt(c)`
  - `_balken()`

### `oberflaeche/baukasten/dropdown/auswahl/rahmen_menue.py`

Das Rahmen-Menü (Unten, Oben, Links, Rechts, Kein, Alle, Außen, Innen): ein Dropdown-Baustein, erbt alles von ``MenueListe``.

- **class `RahmenMenue`**(MenueListe) — Das Rahmen-Menü (Unten, Oben, Links, Rechts, Kein, Alle, Außen, Innen). Meldet die gewählten Seiten.
  - `__init__(parent, *, innen, mehr_text, mehr)` — ``innen``: True = beide inneren Linien (Tabelle), ``"h"`` = nur die waagerechte (Absätze), False = keine.

### `oberflaeche/baukasten/dropdown/auswahl/raster_auswahl.py`

Kachel-Auswahl: ein Popup mit Bildchen im Raster und einem „Mehr …“-Fuß (Aufzählung, Vorlagen, Ränder, Deckblätter …).

- `_symbol(bild, groesse, blass)` — Aus QIcon, QPixmap oder einer Zeichenfunktion ``f(QPainter, QRectF)`` ein Symbol machen; ``blass``: für Graues (nicht möglich).
- `textkachel(text, pixel)` — Zeichenfunktion für eine Kachel, die nur ein Zeichen oder kurzes Wort zeigt (Symbole, Einheiten).
- `zeilenkachel(bild, titel, angaben, spalten, bild_breite)` — Zeichenfunktion für eine Listenzeile: links ein Bildchen (Zeichner), daneben der Titel fett und darunter die Angaben,
- **class `RasterAuswahl`**(MenueListe) — Meldet den Schlüssel der gewählten Kachel.
  - `__init__(parent, *, titel, spalten, groesse, beschriftet, hoehe_max)` — ``beschriftet``: der Name steht unter dem Bild (Seitenzahl-, Wasserzeichen-, Gleichungsgalerie), sonst nur im Tipp.
  - `_rollen_masse()`
  - `kachel(schluessel, beschriftung, bild, *, aktuell, aktiv)` — ``aktiv=False``: die Kachel bleibt sichtbar, aber grau (blass gezeichnet) und nicht wählbar.
  - `bild_setzen(schluessel, bild, beschriftung)` — Bild und Tipp einer vorhandenen Kachel wechseln (z. B. „zuletzt verwendet“ vor dem Aufklappen).
  - `abschnitt(titel)` — Neuer Abschnitt mit eigener Überschrift und eigenem Raster darunter (z. B. „Benutzerdefinierte Symbole:“).
  - `kacheln(eintraege, aktuell)` — ``eintraege``: Liste aus (schluessel, beschriftung, bild).
  - `fuss(text, aktion)` — Zeile unter dem Raster, z. B. „Weitere Aufzählungszeichen …“.
  - `trenner()` — Dünne Linie im Fuß (vor „Benutzerdefinierte Seitenränder …“ u. ä.).
  - `kopf(widget)` — Eine Leiste über den Kacheln (z. B. „Stil \| Hochformat \| Querformat“ bei den Deckblättern).
  - `leeren(groesse)` — Alle Kacheln entfernen (auf Wunsch mit neuer Kachelgröße), um sie neu zu füllen; Kopf und Fuß bleiben.
  - `neu_messen()` — Nach ``leeren`` und neuem Füllen bei offenem Menü: Größe an die neuen Kacheln anpassen.
  - `_klick(schluessel)`

### `oberflaeche/baukasten/dropdown/auswahl/strich_auswahl.py`

Auswahlfeld, das einen Strich zeigt (Kombinierter Typ, Strichtyp): im Feld die schwarze Strichvorschau, im Popup eine Zeile je Eintrag.

- **class `StrichAuswahl`**(QPushButton)
  - `__init__(eintraege, parent)`
  - `aktuell()`
  - `setze(schluessel)`
  - `_namen()`
  - `_zeichner(schluessel)`
  - `_bild(zeichner, groesse)`
  - `paintEvent(_e)`
  - `_popup()`
  - `_waehle(schluessel)`

### `oberflaeche/baukasten/dropdown/auswahl/symbol_auswahl.py`

Symbolwahl: ein Knopf mit dem gewählten Symbol und Pfeil, der ein kleines Raster aus dem vorhandenen Symbolsystem aufklappt.

- **class `SymbolAuswahl`**(RasterAuswahl) — Das Raster der Symbole (meldet den Schlüssel).
  - `__init__(parent, symbole, aktuell, spalten)`
- **class `SymbolWahl`**(DropdownTaste) — Taste mit Symbol und Pfeil; ein Klick öffnet das Raster.
  - `__init__(wert, parent, symbole)`
  - `wert()`
  - `setzen(schluessel, melden)`

### `oberflaeche/baukasten/dropdown/auswahl/zellen_raster.py`

Zellenraster: wie in der Vorlage die Tabelle einfügen — mit der Maus über Zellen fahren, „3 × 4“ lesen, klicken.

- **class `_Gitter`**(QWidget)
  - `__init__(raster, zeilen, spalten, zelle)`
  - `_zelle_bei(pos)`
  - `setze(z, s)`
  - `mouseMoveEvent(e)`
  - `leaveEvent(e)`
  - `mouseReleaseEvent(e)`
  - `paintEvent(e)`
- **class `ZellenRaster`**(MenueListe) — Meldet ``gewaehlt(zeilen, spalten)``. Darunter lassen sich mit ``fuss(...)`` weitere Einträge anhängen.
  - `__init__(parent, zeilen, spalten, *, leer_text)`
  - `_beschriften(z, s)`
  - `waehle(zeilen, spalten)`
  - `fuss(text, aktion)`

## `oberflaeche/baukasten/dropdown/objektmenues`

### `oberflaeche/baukasten/dropdown/objektmenues/__init__.py`

Unterpaket ``objektmenues`` von ``writer.baukasten.dropdown``.


### `oberflaeche/baukasten/dropdown/objektmenues/bild_diagramm_menues.py`

Menüs und Galerien der Reiter „Bildtools“ und „Diagrammtools“ (nur Aussehen; jede Wahl ruft einen Befehl des Bandes).

- `_form_bild(name)`
- `_abschnittsleiste(text)`
- `zuschneiden_menue(b)` — Die Klappe „Zuschneiden“ nach der Vorlage; ``b`` ist der Befehlsbaustein (``bildZuschneidenForm/Skala/Zuruecksetzen``).
- `stil_bild(nr, groesse)` — Vorschau des Diagrammstils ``nr`` (``diagramm.STILE``): Grund, Raster und Schrift wie im fertigen Diagramm, mit drei Säulenreihen.
- `_stilname(nr)`
- `diagramm_stile_menue(b)` — Alle Diagrammstile als Kacheln (Name im Tipp); die Wahl ist ``diagrammStil``.
- `diagramm_stile_galerie(b)` — Die Galerie im Band: eine Kachel je Stil und das Menü mit allen (Aufbau wie ``galerie_ttFormstile``).

### `oberflaeche/baukasten/dropdown/objektmenues/diagramm_popups.py`

Popups der Schnellleiste am Diagramm und die Klappen der Diagrammtools — ein Baustein, damit Band und Schnellleiste dasselbe zeigen.

- `_dg(b)`
- `_kopfknopf(text, i, gruppe)`
- `_linie()`
- `_ueberschrift(text)`
- `_bild_titel_achsentitel(p, fl, kw, el, w, h, mittel)` — Titelbalken und Achsentitel; verkleinern die Zeichenfläche ``fl``.
- `_bild_legende(p, fl, pos, w, h, mittel)`
- `_bild_achsenmarken_gitter(p, fl, el, hell)`
- `_bild_saeulen(p, fl, kw, el, tab, n, farben)`
- `_bild_tabelle(p, tab, n, mittel)`
- `layout_bild(nr, groesse)` — Strichbild eines Schnelllayouts aus dessen Einstellungen (``SCHNELLLAYOUTS[nr]``): Titelbalken, Legende (Lage), Datenbeschriftungen,
- `_farbzeile(farben, gewaehlt, klick)`
- **class `DiagrammPopup`**(MenueListe) — Ein Popup mit Reitern; ``art``: ``elemente``, ``stile`` oder ``filter``; ``reiter``: der zuerst gezeigte Reiter.
  - `__init__(b, art, reiter, parent)`
  - `waehle(i)`
  - `neu_lesen()` — Beim Öffnen: den Reiter zeigen, den der Aufrufer wollte, mit frisch gelesenen Daten.
  - `_fuellen(i)`
  - `_seite_elemente()`
  - `_seite_schnelllayout()`
  - `_seite_vorlagen()`
  - `_seite_farben()`
  - `_seite_filter()`
  - `_seite_namen()` — Reiter „Name“: Reihen und Rubriken umbenennen; „Übernehmen“ schreibt über ``diagrammNamenSetzen`` in die Diagrammdaten.
  - `_namen_uebernehmen()`
  - `_hoehe()`
  - `_uebernehmen()`
- `elemente_popup(b)`
- `schnelllayout_popup(b)`
- `stile_popup(b)`
- `farben_popup(b)`
- `filter_popup(b)`
- `diagramm_bereich_feld(b)` — Auswahlfeld „Diagrammbereich“ der Diagrammtools: oben die Liste der Teile (zeigt den gewählten), darunter „Formatieren“ und

### `oberflaeche/baukasten/dropdown/objektmenues/form_menues.py`

Menüs und Galerie des Reiters „Zeichentools“ für Formen: „Form bearbeiten“ und die Stilgalerie „Abc“ (nur Aussehen; jede Wahl ruft einen Befehl).

- `form_bearbeiten_menue(b)`
- `formstile_galerie(b)`
- `linien_galerie(b)` — Linien und Pfeile als Kacheln im Band (zwei Reihen, ``zeilen`` der Gruppe); Klick fügt die Linie ein (``formEinfuegen``).

### `oberflaeche/baukasten/dropdown/objektmenues/fuell_voreinstellungen.py`

Popup der Füllung im Kopf (Vorlage): „Keine Füllung“, Designfarben (10 × 6), Graduelle Füllung (10), Musterfüllung (5), Strukturfüllung (5).

- `graduell_paar(farbe)` — (dunkel, hell) der graduellen Füllung einer Grundfarbe.
- `_feld(farbe, groesse)`
- `_gekachelt(kachel, groesse)`
- `_muster_kachel(key, farbe)`
- `fuell_bild(spec, groesse)` — Das Ergebnis der Füllung als Bild der Größe ``groesse`` (leer = durchsichtig).
- **class `FuellPalette`**(FarbPalette) — Die Farbpalette des Programms als Popup der Füllung im Kopf; meldet den Schlüssel statt einer Farbe.
  - `__init__(parent, aktuell, **kw)`
- `fuell_menue(parent, aktuell)`

### `oberflaeche/baukasten/dropdown/objektmenues/layout_optionen.py`

Das kleine Popup „Layoutoptionen“ neben einem markierten Bild: Umbruchart per Klick, „Mit Text verschieben“ oder „Fester Text“, „Mehr anzeigen“.

- **class `LayoutOptionen`**(PopupVerhalten, QFrame)
  - `__init__(parent, art, mit_text)`
  - `_titel(text)`
  - `_klick(art)`
  - `setze(art)`
  - `zeigen_bei(pos)`

### `oberflaeche/baukasten/dropdown/objektmenues/layout_optionen_objekt.py`

Das Popup „Layoutoptionen“ eines freien Objekts nach der Vorlage: ✕ im Kopf, größere Kacheln, beide Radios leer bei SmartArt.

- **class `LayoutOptionenObjekt`**(LayoutOptionen)
  - `__init__(parent, art, mit_text)`
  - `_kopf_mit_schliessen()`
  - `_kacheln_gross()`
  - `verschieben_wahl()`
  - `verschieben_wahl(wahl)`

### `oberflaeche/baukasten/dropdown/objektmenues/linien_voreinstellungen.py`

Popup der Linie im Kopf (Vorlage): „Keine Linie“ und „Voreingestellte Linie“ — 8 Strichtypen (Zeilen) × 4 Formen (Spalten).

- `linien_schluessel(art, form, breite)`
- `linien_bild(spec, groesse)` — Eine Linie der Strichart/Form/Breite (pt) in Farbe über die Breite, mittig; ``art`` "keine" gibt ein leeres Bild.
- `linien_menue(parent, aktuell, arten)`

### `oberflaeche/baukasten/dropdown/objektmenues/objekt_menues.py`

Die Popups für ein markiertes Bild oder eine Form: Formstile, Füllung, Kontur (wie in der Vorlage).

- `_linien_symbol(art, breite, groesse)`
- `graduell_pixmap(dunkel, hell, w, h)`
- **class `FuellMenue`**(FarbPalette) — Füllung wie in der Vorlage: Keine Farbe · Thema-Farben · Standard-Farben · Farbverlauf · Automatisch · Weitere Füllfarben · Pipette ·
  - `__init__(parent, start)`
  - `_raster_untermenue(text, art, weitere, kacheln, groesse, spalten, gewaehlt)` — Ein Untermenü mit Kacheln (Graduell, Textur, Muster) und darunter „Weitere …“, das die Seitenleiste „Formatierung“ öffnet.
  - `_untermenue(text, icon)`
  - `_einsetzen(menue, inhalt)` — Das Raster steht als Inhalt des Untermenüs.
- **class `KonturMenue`**(FarbPalette) — Kontur wie in der Vorlage: Keine Linie · Thema-Farben · Standard-Farben · Farbverlauf · Weitere Linienfarben · Pipette · Linienart ▸ · Strichart ▸ · Pfeilart ▸.
  - `__init__(parent, start)`
- `formstil_werte(schluessel)` — Füllung und Kontur des Stils ``z{Zeile}{Spalte}`` für Bilder und Textfelder: {"fuell": …, "rand": …} (``None`` = keine). Die Werte kommen aus
- `formstil_zeichner(schluessel)` — Zeichnet die Kachel „Abc“ des Stils: Füllung (auch Verlauf), Rand und Schrift in passender Farbe.
- `formstile(parent)` — Das Popup „Formstile“: sechs Zeilen zu sieben Stilen; ``gewaehlt`` meldet ``z{Zeile}{Spalte}`` (Namen im Tipp). Darunter steht „Weitere Effekte …“.

### `oberflaeche/baukasten/dropdown/objektmenues/smartart_menues.py`

Menüs, Galerie und Miniaturen für SmartArt (Reiter „SmartArt-Design“, Schnellleiste am Knoten, Dialog „SmartArt-Grafik auswählen“).

- `_sa(b)`
- `_sym(name)`
- **class `_Auffrischend`**(MenueListe) — Ein Menü, das seine Zeilen bei jedem Öffnen neu bewertet (grau, Haken) — das Band baut ein Menü nur einmal.
  - `__init__(bau, parent)`
  - `_neu()`
- `form_menue(b)`
- `level_menue(b)`
- `hierarchie_menue(b, mit_rechts_links)` — Die Layoutvarianten des Organigramms; ``mit_rechts_links``: oben noch „Layout von rechts nach links“ (Schnellleiste am Knoten).
- `layout_menue(b)` — „Layout ändern“: die 15 Layouts des Katalogs mit ihren Anzeigenamen; das gewählte trägt einen Haken.
- `stil_bild(nr, groesse, blau)` — Zwei übereinanderstehende Kästen im Formenstil ``nr`` (``SA.STILE``: Flach, Einfach, Hell, Kräftig, 3D).
- `stile_menue(b)`
- `stile_galerie(b)`
- `_farben(grau)` — (Fläche, Rand, Strich für Text) — grau im Raster des Dialogs, blau in der großen Vorschau.
- `_kasten(p, r, fl, rand, strich, text, rund)`
- `_pfeil(p, a, b, col)`
- `_m_organigramm(p, W, H, c)`
- `_m_liste(p, W, H, c)`
- `_m_prozess(p, W, H, c)`
- `_m_zyklus(p, W, H, c)`
- `_m_pyramide(p, W, H, c)`
- `_m_spalten(p, W, H, c)`
- `_m_gruppen(p, W, H, c)`
- `_m_matrix(p, W, H, c)`
- `_m_chevron(p, W, H, c)`
- `_m_radial(p, W, H, c)`
- `_m_zielscheibe(p, W, H, c)`
- `_m_trichter(p, W, H, c)`
- `_m_zeitachse(p, W, H, c)`
- `_m_stufen(p, W, H, c)`
- `_zeile(p, x, y, w, col, punkt)` — Eine Aufzählungszeile: Punkt und Strich.
- `_m_punktliste(p, W, H, c)`
- `_m_balkenliste(p, W, H, c)`
- `_m_beschreibungsliste(p, W, H, c)`
- `_m_spaltenrahmen(p, W, H, c)`
- `_m_bildliste(p, W, H, c)`
- `_m_perspektive(p, W, H, c)`
- `_m_konvergenz(p, W, H, c)`
- `_m_kartenprozess(p, W, H, c)`
- `_m_kreisbeziehung(p, W, H, c)`
- `_m_segmentzyklus(p, W, H, c)`
- `zeichne_miniatur(p, r, schluessel, grau)` — Zeichnet die Miniatur des Layouts in ``r``.
- `miniatur(schluessel, grau, groesse)`

## `oberflaeche/baukasten/felder`

### `oberflaeche/baukasten/felder/__init__.py`

Wiederverwendbare Bedienelemente.


### `oberflaeche/baukasten/felder/assistenten_liste.py`

Die Liste der Assistenten (Schnelle KI-Aktionen und fortlaufende Assistenten) mit Hauptschalter — EIN Baustein für KI-Einstellungen und Optionen.

- **class `AssistentenListe`**(QWidget)
  - `__init__(fenster, parent)`
  - `_haupt_geklickt(an)`
  - `neu_lesen()`

### `oberflaeche/baukasten/felder/auswahl_bereich.py`

Der Bereich „Auswahl“ (Start ▸ Auswählen ▸ Auswahlbereich) als Baustein: alle Bilder, Formen, Diagramme und Tabellen des Dokuments in einer

- `objekte(ed)` — [(Beschriftung, Ziel)] aller Objekte in Dokumentreihenfolge; Ziel ``("text", von, bis)``, ``("frei", Id)`` oder ``("tabelle", von, bis)``.
- **class `AuswahlBereich`**(PanelFaehig, QDialog)
  - `__init__(parent, ed)`
  - `fuellen()`
  - `_markieren(it)`

### `oberflaeche/baukasten/felder/auswahl_liste.py`

Auswahlliste mit Rahmen und hohen Zeilen — der eine Baustein für „Eintrag aus einer Liste wählen“ (Sprachen, Stimmen).

- **class `AuswahlListe`**(QListWidget)
  - `__init__(eintraege, mindesthoehe)`
  - `currentData()`
  - `currentText()`
  - `findData(daten)`
  - `setCurrentIndex(i)`
  - `setCurrentText(text)`

### `oberflaeche/baukasten/felder/farbwaehler.py`

„Weitere Farben …“: das Fenster „Farben“ mit den Karteireitern Standard, Benutzerdefiniert und Erweitert.

- **class `Modell`**(QObject) — Die gewählte Farbe, als Farbton/Sättigung/Wert gehalten (der Farbton geht bei Grau nicht verloren).
  - `__init__(start)`
  - `farbe()`
  - `setze(c, melden)`
  - `setze_deckkraft(prozent)`
  - `setze_hsv(h, s, v)`
- **class `_Kacheln`**(QWidget) — Rundes Kachelraster: Farbton quer, oben hell und blass, unten dunkel; ganz unten die Graustufen.
  - `__init__(modell)`
  - `skaliere(zelle)` — Die Kacheln in dieser Größe (Bildpunkte) neu legen: so groß, wie Breite und Höhe der Seitenleiste es zulassen.
  - `_feld(s, z)`
  - `_bei(pos)`
  - `paintEvent(_e)`
  - `mousePressEvent(e)`
  - `mouseDoubleClickEvent(e)`
- **class `_Flaeche`**(QWidget) — Farbton quer, Sättigung von oben (voll) nach unten (grau).
  - `__init__(modell)`
  - `setGroesse(b, h)` — Größe ändern und das Farbbild neu rechnen.
  - `paintEvent(_e)`
  - `_setze(pos)`
  - `mousePressEvent(e)`
  - `mouseMoveEvent(e)`
- **class `_Leiste`**(QWidget) — Helligkeit (Wert): oben hell, unten dunkel, mit Pfeil am rechten Rand.
  - `__init__(modell)`
  - `paintEvent(_e)`
  - `_setze(pos)`
  - `mousePressEvent(e)`
  - `mouseMoveEvent(e)`
- **class `_Ring`**(QWidget) — Farbring (Farbton) mit Dreieck (Sättigung und Wert). Das Dreieck dreht mit: Die reine Farbe zeigt auf ihren Farbton.
  - `__init__(modell)`
  - `skaliere(k)` — Ring und Dreieck im Maßstab ``k`` (1,0 = 270 × 250 Bildpunkte).
  - `_ecken()`
  - `paintEvent(_e)`
  - `_schwerpunkt(q, a, b, c)`
  - `_wirke(pos)`
  - `mousePressEvent(e)`
  - `mouseMoveEvent(e)`
  - `mouseReleaseEvent(_e)`
- **class `_Regler`**(QWidget) — Farbmodell (RGB, HSV, HSL), drei Zahlenfelder und die Schreibweise #rrggbb — gleich in allen Karteireitern.
  - `__init__(modell)`
  - `_modus(text)`
  - `_modus_zeigen()`
  - `werte()`
  - `auffrischen()`
  - `_tippen()`
  - `_hex()`
- **class `_Proben`**(QWidget) — Eine Fläche, oben „Neu“, unten „Aktuell“.
  - `__init__(modell, aktuell)`
  - `paintEvent(_e)`
- **class `_FlaechePaar`**(QWidget) — Farbfläche und Helligkeitsleiste als ein Bedienelement; die Größe folgt den beiden (``ordne`` nach jeder Änderung).
  - `__init__(flaeche, leiste)`
  - `ordne()`
- **class `_ProbeBlock`**(QWidget) — Die Probe mit „Neu“ oben und „Aktuell“ unten daneben.
  - `__init__(probe)`
- **class `FarbenDialog`**(PanelFaehig, QDialog) — Das Fenster „Farben“ (öffnet sich in der Seitenleiste). ``farbe()`` gibt nach OK die gewählte Farbe zurück.
  - `__init__(parent, start, titel)`
  - `_transparenz_zeile()` — „Transparenz“: Schieber und Zahlenfeld in Prozent (100 % = deckend) — beide halten dieselbe Zahl.
  - `_deckkraft_zeigen()`
  - `passe_an(breite, hoehe)` — Das Standard-Raster so groß machen, wie die Seitenleiste Platz hat (Breite für 17 Spalten, Höhe für 18 Zeilen samt Reitern und Probe).
  - `farbe()` — Die gewählte Farbe samt Transparenz (Alpha); ohne Änderung am Schieber ist sie deckend.
  - `deckkraft()`

### `oberflaeche/baukasten/felder/flache_reiter_leiste.py`

Flache Reiterleiste nach der Vorlage: Beschriftung in Großbuchstaben, kein Kasten, Linie unter dem aktiven Reiter.

- `_gross(text)`
- `_mische(a, b, anteil)` — Farbe a zum Anteil (0…1) mit b gemischt.
- **class `ReiterUeberlauf`** — Basis der Reiterleisten mit Knopf „•••“ (Band, Dokumente, Register: ``UeberlaufLeiste``) und Menü der Reiter, die nicht mehr in die Leiste passen.
  - `_mehr_einrichten()`
  - `_mehr_menue()`
- **class `ReiterDropdown`** — Die Leiste als ein Dropdown (statt vieler Reiter nebeneinander): Taste mit dem Namen des aktuellen Reiters, Liste aller sichtbaren Reiter mit Haken am aktuellen;
  - `_wahl_einrichten()`
  - `_wahl_zeigen(an)` — Dropdown ein/aus; Name und Lage nachziehen.
  - `_wahl_fuellen()`
- **class `FlacheReiterLeiste`**(ReiterDropdown, QTabBar)
  - `__init__(art, parent)`
  - `_sichtbar()`
  - `_knopf_breite(i)`
  - `_schrift(groesse)`
  - `_breiten()` — Breite je sichtbarem Reiter: Unterreiter gleich breit, Hauptreiter nach Länge der Beschriftung (der Pfeilknopf zählt mit).
  - `_soll()` — Natürliche Breite jedes sichtbaren Hauptreiters (Beschriftung gemessen, Pfeilknopf zählt mit).
  - `_als_dropdown()` — Passen die Hauptreiter in ihrer natürlichen Breite nicht nebeneinander? Dann zeigt das Dropdown die Wahl (Reiter mit Knopf bleiben Reiter: ihr Pfeil hätte im Dropdown keinen Platz).
  - `_neu_anordnen()` — Größe, aktiver Reiter, Texte oder Reiterzahl haben sich geändert: Dropdown oder Reiterleiste zeigen und neu auslegen.
  - `_text_flaeche(i, breite)`
  - `_groesse(breiten)` — Die Schriftgröße: so groß wie möglich, aber so, dass das längste Wort jedes Reiters ganz hineinpasst (nie „…“).
  - `_text_hoehe(fm, i, breite)`
  - `_hoehe(breiten, gr)`
  - `tabSizeHint(index)`
  - `minimumTabSizeHint(index)`
  - `sizeHint()`
  - `minimumSizeHint()`
  - `resizeEvent(e)`
  - `tabLayoutChange()`
  - `_pfeil_rect(i, gr)` — Die Fläche des Pfeils hinter dem Text des Reiters ``i`` (leer ohne Knopf).
  - `changeEvent(e)`
  - `mousePressEvent(e)`
  - `paintEvent(_e)`
- **class `UeberlaufLeiste`**(ReiterUeberlauf, QTabBar) — Gewöhnliche Reiterleiste (Band, Dokumente, Register) nach derselben Regel wie ``FlacheReiterLeiste``: keine Rollpfeile, kein angeschnittener Reiter.
  - `__init__(parent)`
  - `setTabVisible(index, sichtbar)`
  - `isTabVisible(index)`
  - `gezeigt(index)`
  - `tabInserted(index)`
  - `tabRemoved(index)`
  - `_verschoben(von, nach)`
  - `_verfuegbar()`
  - `_versteckte()`
  - `_sichtbare_waehlen(wollen, gesamt)` — Welche Reiter bei der verfügbaren Breite sichtbar bleiben (der aktive immer).
  - `_sichtbarkeit_setzen(zeige)`
  - `_mehr_knopf_setzen()`
  - `neu_verteilen()`
  - `sizeHint()`
  - `minimumSizeHint()`
  - `resizeEvent(e)`
  - `tabLayoutChange()`
- `flach_machen(reiter, art)` — Setzt eine ``FlacheReiterLeiste`` in das ``QTabWidget`` (``setTabBar`` gilt nur vor dem ersten Reiter, darum werden die Seiten neu eingesetzt).
- `alle_flach(wurzel, art)` — Alle Reiter unter ``wurzel`` (``QTabWidget``) bekommen dieselbe flache Leiste: EIN Aussehen für alle Reiter in den Seitenleisten-Fenstern.

### `oberflaeche/baukasten/felder/formular_gitter.py`

Formular, das sich der Breite anpasst — der Baustein für Felder in Zusatzfenstern (Seitenleiste) und in breiten Fenstern.

- `tabellen_gitter(eltern, *, rand, abstand, waagerecht, senkrecht, oben_links)` — DIE eine Stelle im Projekt, an der ein ``QGridLayout`` erzeugt wird. Für Zellen, deren Spalten feste Aufgaben haben (Kachelraster, Zwei-Listen-Gerüst,
- **class `UmbruchSchalter`**(QCheckBox) — Ankreuzfeld, dessen Text bei Platzmangel umbricht (``QCheckBox`` selbst kann das nicht).
  - `__init__(text, parent)`
  - `natuerliche_breite()` — Breite des Ankreuzfelds in einer Zeile, ohne Umbruch (damit kurz/lang richtig entschieden wird; ``sizeHint`` ist wegen des Umbruchs klein).
  - `_indikator()`
  - `hasHeightForWidth()`
  - `heightForWidth(breite)`
  - `sizeHint()`
  - `minimumSizeHint()`
  - `paintEvent(ev)`
- **class `FlussLayout`**(QLayout) — Zeile, die umbricht (wie Text): Beschriftung und das Feld dahinter bleiben beisammen.
  - `__init__(abstand, zentriert)` — ``zentriert``: jede Zeile steht für sich mittig (Standard: linksbündig).
  - `addItem(item)`
  - `count()`
  - `itemAt(i)`
  - `takeAt(i)`
  - `hasHeightForWidth()`
  - `heightForWidth(breite)`
  - `setGeometry(rect)`
  - `sizeHint()`
  - `minimumSize()`
  - `_gruppen()` — Beschriftung + nächstes Feld sind eine Einheit, alles andere steht für sich.
  - `_lege(rect, setzen)`
- `abschnittstitel(text)` — Die Überschrift eines Abschnitts: klein, gedämpft, Großbuchstaben — überall gleich (Gruppen, Spalten, Bereiche in Fenstern).
- `reiter_knopf_stil(knopf)` — Der Reiterknopf (``QToolButton``, ``checkable``) mit Unterstrich in der Hervorhebungsfarbe — für selbst gebaute Reiterleisten.
- `abschnittsband(text)` — Eine Überschrift als graues Band über einer Gruppe von Kacheln (Menüs mit mehreren Gruppen); Schriftgröße der Oberfläche.
- `mittig(widget)` — Ein Element fester Größe (Vorschau, Farbraster …) in der Mitte der Breite.
- **class `_Einheit`** — Ein Paar (Beschriftung + Feld) oder ein breites Element.
  - `__init__(beschriftung, feld, reihe, gewichte)`
- `_hoehe_bei(item, breite)`
- `_natuerlich(item)`
- `ist_dropdown(w)` — Ein Dropdown (Auswahlfeld, Schriftauswahl, Dropdown-Taste, Kopf-Dropdown, Strichart, Farbfeld; Knöpfe tragen die Eigenschaft ``dropdownFeld``):
- `einzeilig(item)`
- `felder_angleichen(wurzel)` — Alle einzeiligen Felder (Zahl, Text, Farbe) und beschriftete Knöpfe unter ``wurzel`` auf ``FELDHOEHE``; Dropdowns bleiben bei ``DROPDOWN_HOEHE``. Auch für
- **class `FormularGitter`**(QLayout)
  - `__init__(parent)`
  - `_nimm(objekt)`
  - `zeile(beschriftung, feld)` — Beschriftung (Text oder Widget) und das Feld (Widget oder Layout) dahinter.
  - `breit(objekt)`
  - `nebeneinander(*felder, spalten, abstand)` — Felder ohne Beschriftung gleich breit in einer Zeile; ``spalten`` größer als die Zahl der Felder lässt den Rest der Zeile frei (halbe Zeile).
  - `reihe(*paare, gewichte, vorn)` — Mehrere Felder nebeneinander, jedes mit der Beschriftung darüber: ``reihe(("Schriftart:", a), ("Größe:", b), gewichte=(3, 1))``.
  - `addItem(item)`
  - `count()`
  - `itemAt(i)`
  - `takeAt(i)`
  - `hasHeightForWidth()`
  - `sizeHint()`
  - `minimumSize()`
  - `heightForWidth(breite)`
  - `setGeometry(rect)`
  - `_beschriftungen_nachfuehren()` — Ein ausgeblendetes Feld nimmt seine Beschriftung mit (sonst bliebe sie als Waise am alten Platz stehen); wird das Feld wieder gezeigt, kommt sie zurück.
  - `_reihe_legen(e, breite, y, out)`
  - `_kurz(e, breite)` — Ein einzelnes Ankreuzfeld, Optionsfeld oder ein Knopf, der höchstens eine halbe Zeile braucht.
  - `_gleich_hoch()` — Alle einzeiligen Bedienelemente (Menü, Zahl, Text, Knopf) dieses Formulars gleich hoch: die Höhe des höchsten natürlichen Elements, ohne feste Pixelwerte.
  - `_plan(breite)` — → ([(Element, x, y, Breite, Höhe)], Gesamthöhe) bei dieser Breite.
  - `_spaltenmass(paare, breite)` — → (Breite der Beschriftungen, Spaltenzahl, Beschriftung darüber?).
  - `_breit_legen(einheiten, i, breite, y, out)` — Ein Element ohne Beschriftung; kurze Einzelelemente (Ankreuzfeld, Option, Knopf) stehen zu zweit/zu dritt nebeneinander. → (y, i).
  - `_paarzeile_legen(zeile, mass, y, out)` — Eine Zeile aus ein oder zwei Beschriftung/Feld-Paaren. → neues y.
  - `_paar_daneben(u, x0, sp, bw)` — Beschriftung links, Feld rechts. → ([Plätze], Zeilenhöhe).
- **class `AngepassteReiter`**(QTabWidget) — Reiter, deren Höhe dem gewählten Reiter folgt (ein ``QTabWidget`` richtet sich sonst nach dem höchsten und lässt kürzeren Reitern leeren Platz).
  - `__init__(parent)`
  - `_aktuelle_seite(_i)` — Nur die gewählte Seite bestimmt die Höhe: die anderen zählen für das Layout nicht mit (sonst bleibt unter kürzeren Reitern leerer Platz).
  - `tabInserted(index)`
  - `_mass(minimum)`
  - `hasHeightForWidth()`
  - `heightForWidth(breite)` — Die Höhe der gewählten Seite bei dieser Breite (Seiten aus ``FormularGitter`` brechen um): so bleibt unter kürzeren Reitern kein leerer Platz.
  - `sizeHint()`
  - `minimumSizeHint()`
- `gruppe(titel, *, karte)` — Eine Gruppe von Feldern mit Titel: flach wie die Abschnittstitel (Großbuchstaben, Linie darüber); ``karte=True`` = Gruppenkasten des Stils

### `oberflaeche/baukasten/felder/kachel_feld.py`

Beschriftete Kacheln zum Anklicken, immer genau eine gewählt (zum Beispiel die Umbruchart eines Bildes).

- **class `KachelFeld`**(QWidget)
  - `__init__(parent, *, spalten, groesse, mit_text, fliessend)`
  - `hinzu(schluessel, text, bild)`
  - `_neu_legen(spalten)` — Kacheln in ``spalten`` Spalten neu ins Raster setzen (nur Anordnung, Auswahl und Signale bleiben).
  - `minimumSizeHint()`
  - `resizeEvent(ev)` — Mit ``fliessend=True`` so viele Spalten, wie in die Breite passen (``spalten`` ist das Höchstmaß).
  - `_fokus_ziel()` — Nur eine Kachel ist per Tab erreichbar: die gewählte, sonst die erste.
  - `eventFilter(obj, ev)`
  - `setze(schluessel, melden)`
  - `aktuell()`

### `oberflaeche/baukasten/felder/karten_raster.py`

KartenRaster: ein Raster mit gemeinsamem Maßsystem für Karten, Schalter und Knöpfe.

- `spanne_von(name_oder_text)` — Spanne aus einem Namen der zentralen Tabelle (``"breit"``), aus ``"2x1"`` oder aus einem Paar.
- `_platzieren(spannen, n)` — Platzierung im Raster mit ``n`` Spalten → je Element (Zeile, Spalte, Spalten, Zeilen): der Reihe nach an die erste freie Stelle ab dem
- `_zeilenhoehen(stellen, noetig, a, gleich)` — Höhe jeder Rasterzeile; ``noetig[i]`` = Höhe, die Element i für seinen Inhalt braucht. ``gleich``: eine gemeinsame Zeileneinheit, so
- **class `KartenRaster`**(QLayout)
  - `__init__(parent, min_breite, abstand, spalten_fest, gleiche_hoehe)`
  - `addWidget(w, spanne)`
  - `addItem(item)`
  - `setSpanne(w, spanne)`
  - `count()`
  - `itemAt(i)`
  - `takeAt(i)`
  - `hasHeightForWidth()`
  - `expandingDirections()`
  - `spalten(breite)`
  - `_sichtbar()`
  - `_plan(breite)` — Plätze (Item, x, y, b, h) und Gesamthöhe bei der Breite ``breite``.
  - `heightForWidth(breite)`
  - `sizeHint()`
  - `minimumSize()`
  - `setGeometry(r)`
- `kacheln_legen(gitter, kacheln, spalten)` — Kacheln der Reihe nach in ``spalten`` Spalten ins Gitter setzen (zeilenweise, links oben beginnend).
- `kachel_gitter(kacheln, spalten, *, eltern, rand, abstand, waagerecht, senkrecht, oben_links, rest_dehnt)` — Kachelraster fester Kachelgröße (Farben, Formen, Seitenbildchen …): die Rasterlogik für alle Stellen, an denen das Gitter der Zweck ist.
- `_ist_kurz(it, max_breite)` — Ein sichtbares kurzes Ankreuzfeld, Optionsfeld oder ein kurzer Knopf, der ins Raster darf.
- `_alle_layouts(fenster)` — Jedes Layout des Fensters genau einmal, auch die verschachtelten.
- `_gruppe_ins_raster(l, von, bis)` — Die Elemente ``von`` bis ``bis`` (ausschließlich) des Layouts in ein ``KartenRaster`` an derselben Stelle legen.
- `_gruppen_buendeln(l, max_breite)` — Jede Folge von mindestens zwei kurzen Elementen im Layout bündeln. → Zahl der Gruppen.
- `kurze_gruppen_ins_raster(fenster, max_breite)` — Zentrale Automatik für jedes Fenster der Seitenleiste: aufeinanderfolgende kurze Ankreuzfelder, Optionsfelder und Knöpfe in einem senkrechten Layout

### `oberflaeche/baukasten/felder/listen_leiste.py`

Liste mit Knopfleiste: der EINE Baustein für jede Liste, die man hinzufügen, bearbeiten und entfernen kann (KI-Modelle, KI-Werkzeuge …).

- **class `ListenLeiste`**(QFrame)
  - `__init__(neu_tip, min_hoehe, parent)`
  - `_knopf(symbol, tip)`
  - `knoepfe_pruefen(*_)`

### `oberflaeche/baukasten/felder/mass_feld.py`

Zahlenfeld mit Maßeinheit: intern immer Millimeter, angezeigt in der gewählten Einheit (Optionen ▸ Speichern).

- `set_einheit(name)`
- `einheit()`
- **class `MassSpin`**(QDoubleSpinBox) — Wert in mm, Anzeige in der gewählten Maßeinheit; wer „mm“ eingibt oder „2 cm“ tippt, wird verstanden.
  - `textFromValue(v)`
  - `valueFromText(text)`
  - `validate(text, pos)`
- `spin(value, lo, hi, suffix, step, decimals)`
- **class `EinheitFeld`**(QWidget) — Zahlenfeld mit Einheiten-Auswahl daneben (wie „0 char ▾“ in der Vorlage): der Wert ist immer in Millimetern, angezeigt wird er in der
  - `__init__(wert_mm, lo, hi, einheiten, start, leer_bei_null)`
  - `_faktor()`
  - `_zeige()`
  - `_gelesen(v)`
  - `value()`
  - `setValue(mm)`
- `einheit_name()` — Kürzel der Maßeinheit der Oberfläche (Optionen ▸ Speichern) als Schlüssel von ``FELD_EINHEITEN``.

### `oberflaeche/baukasten/felder/pipette.py`

Die Pipette: eine Farbe vom Bildschirm aufnehmen.

- **class `_Pipette`**(QWidget)
  - `__init__(bild, geometrie)`
  - `_tick()`
  - `_fokus_pruefen()`
  - `_zustand(zustand)`
  - `focusOutEvent(e)`
  - `_ende(farbe)`
  - `_farbe_bei(p)`
  - `paintEvent(_e)`
  - `mouseMoveEvent(e)`
  - `mouseReleaseEvent(e)`
  - `keyPressEvent(e)`
- `farbe_vom_bildschirm(parent)` — Die Farbe unter dem nächsten Linksklick (blockiert höchstens ``ZEIT_S`` Sekunden); None bei Abbruch, Zeitablauf oder wenn der Bildschirm nicht aufnehmbar ist.

### `oberflaeche/baukasten/felder/schalter.py`

Chips und an/aus-Schalter der Oberfläche — ein Baustein statt einzelner Stylesheets.

- `chip_stil()` — Auswahl-Chip mit Rahmen; gewählt: Akzentfläche.
- `chip_gruen_stil()` — Grüner Schalter-Chip (gewählt = ``Farbe.AN``).
- `schalter_an_stil()` — Die Kapsel „an“ (gefüllt).
- `schalter_aus_stil()` — Die Kapsel „aus“ (nur Rahmen).
- **class `KippSchalter`**(QAbstractButton) — Kleiner Kippschalter (Schiene mit rundem Knopf), gezeichnet in Paletten­farben: an = Akzent, aus = Rand. Maße aus ``mass.py``; ``toggled(bool)`` wie beim Ankreuzfeld.
  - `__init__(an, parent)`
  - `sizeHint()`
  - `paintEvent(_e)`

### `oberflaeche/baukasten/felder/schiebe_feld.py`

Regler und Schrittfeld für Dialoge.

- `_knopf(text)`
- **class `SchrittFeld`**(QWidget)
  - `__init__(lo, hi, suffix, schritt, nachkomma, wert)`
  - `value()`
  - `setValue(v)`
- **class `SchiebeFeld`**(QWidget)
  - `__init__(lo, hi, suffix, schritt, nachkomma, wert)`
  - `_zeige(w, melden)`
  - `value()`
  - `setValue(v, melden)`

### `oberflaeche/baukasten/felder/winkel_feld.py`

Winkelfeld: Drehknopf (QDial) und Zähler „0,0°“ mit „−“ und „+“ (wie der Schattenwinkel der Vorlage).

- **class `WinkelFeld`**(QWidget)
  - `__init__(lo, hi, suffix, schritt, nachkomma, wert)`
  - `_vom_knopf(v)`
  - `_vom_zaehler(v)`
  - `value()`
  - `setValue(v)`

## `oberflaeche/baukasten/formatierung`

### `oberflaeche/baukasten/formatierung/__init__.py`

Text- und Objektformatierung.


### `oberflaeche/baukasten/formatierung/absatz_dialog.py`

Das Fenster „Absatz“ (Einzüge und Abstände, Zeilen- und Seitenumbruch) als Baustein.

- `aus_block(bf)` — Die Werte eines Absatzformats für das Fenster (Gegenstück zu ``werte()``): Einzüge in mm, Abstände in pt, Zeilenabstand.
- **class `AbsatzDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, werte, *, umfang)`
  - `setze(w)`
  - `_zeilenart(*_)`
  - `_neu()`
  - `werte()`
  - `_opt()`
  - `_tabstopps()`
  - `_male(p, rect)` — Vorhergehender Absatz (grau), der eigene mit Einzügen und Abständen, folgender Absatz (grau).

### `oberflaeche/baukasten/formatierung/auto_felder_mixin.py`

Bei „Automatische Füllung“ / „Automatische Linie“ die Felder zeigen, aber grau (nicht bedienbar), wie in der Vorlage.

- **class `AutoFelderMixin`**
  - `_felder_zeigen()`
  - `_auto_gruppe(gruppen, auto)`

### `oberflaeche/baukasten/formatierung/effekte_drei_mixin.py`

Effekte-Seite mit nur drei Abschnitten (Schatten, Leuchten, Weiche Kanten) — wie die Vorlage des Diagramms.

- **class `NurDreiEffekteMixin`**
  - `_seite_effekte(w)`
  - `alle_zu()`
  - `_teil_in_regler(name)`
  - `_fx_null_schatten()`
  - `_setze_effekte(w)`

### `oberflaeche/baukasten/formatierung/formatvorlage_dialog.py`

„Neue Formatvorlage“ als Baustein: Eigenschaften (Name, Typ, basiert auf, folgender Absatz), die Formatierungsleiste aus dem Band

- **class `FormatvorlageDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, *, start, vorlagen, name, basis, aendern, belegt, standard_tab_mm)` — ``aendern``: Name einer vorhandenen Vorlage — dann ist es das Fenster „Formatvorlage ändern“ (Name fest).
  - `_bauen_eigenschaften(v, name, namen)`
  - `_bauen_formatierung(v)` — Formatierung (dieselbe Leiste wie im Band) mit Vorschau.
  - `_bauen_fuss(v)` — Zur Vorlage hinzufügen, Format-Menü, Knöpfe.
  - `_anfangswerte(basis, start, namen)` — Beim Ändern einer vorhandenen Vorlage deren Werte übernehmen; liefert (Basis, Startwerte).
  - `_freier_name(wunsch)`
  - `_felder()`
  - `_neu(*_)`
  - `_male(p, rect)` — Vorhergehender Absatz (grau), Beispieltext in der Vorlage, folgender Absatz (grau).
  - `_basis_geaendert()` — Eine andere Basis: ihre Werte sind der neue Ausgangspunkt, was man vorher selbst geändert hat, bleibt dabei nicht stehen.
  - `_pruefen(*_)`
  - `_schriftart()` — Format ▸ Schriftart …: dasselbe Fenster wie im Band, mit allen Feldern; die Vorlage merkt sie sich.
  - `_absatz()` — Format ▸ Absatz …: dasselbe Fenster wie im Band, mit beiden Reitern; die Vorlage merkt sich alle Felder (auch Tabstopps und Umbruchregeln).
  - `_rahmen()` — Format ▸ Rahmen …: das Fenster „Rahmen und Schattierung“ ohne den Reiter Seitenrand (der gehört nicht zu einer Vorlage).
  - `_liste()` — Format ▸ Nummerierung …: dasselbe Fenster wie im Band; die Vorlage merkt sich die gewählte Liste.
  - `_effekte()` — Format ▸ Texteffekte …: Füllung (Farbe der Vorlage, Transparenz) und Kontur.
  - `_tabs()` — Format ▸ Tabstopps …: dasselbe Fenster wie im Absatz; die Vorlage merkt sich die Tabstopps.
  - `_verknuepfung()` — Format ▸ Verknüpfung …: die Tastenkombination, die die Vorlage auf den Absatz anwendet.
  - `_ok()`
  - `ergebnis()` — Name, Basis, folgender Absatz und alle Felder der Vorlage.

### `oberflaeche/baukasten/formatierung/objektformat_panel.py`

„Formatierung“ für ein Bild, eine Form, ein Textfeld oder WordArt in der rechten Seitenleiste (nach der Vorlage).

- **class `_Felder`**(QWidget) — Eine Gruppe von Feldern im ``FormularGitter`` (Beschriftung über dem Feld), die nur bei passender Füllungs- oder Linienart zu sehen ist.
  - `__init__()`
  - `zeile(text, widget)`
  - `breit(widget)`
- **class `_DreiDUntereinander`** — Für beide Seiten der Effekte (Objekt und Text): Zahlenfelder als Regler mit Wert darüber (ein Schrittfeld zeigt seine Zahl im dunklen Thema nicht)
  - `_schritt_feld(lo, hi, suffix, schritt, nk)`
  - `_seite_effekte(w)`
  - `_abschluss_menue(k)`
  - `_abschluss_setzen(k, art)`
  - `_abschluss_regler(k)` — Wer Breite oder Höhe bewegt, schaltet den Abschluss ein (Rund), wenn er aus war.
  - `_setze_effekte(w)`
  - `_werte_effekte()`
- **class `_TextPanel`**(_DreiDUntereinander, TexteffektPanel) — Die Textoptionen: das Panel der Texteffekte mit dem schmalen 3D-Format.
- **class `ObjektFormatPanel`**(_DreiDUntereinander, TexteffektPanel)
  - `__init__(parent, werte)`
  - `optionen_waehlen(i)` — 0 = Formoptionen (Füllung und Linie, Effekte des Objekts), 1 = Textoptionen (Text im Objekt).
  - `setze_text(werte)` — Die Textoptionen mit den Werten des Textes im Objekt füllen (meldet nichts).
  - `text_werte()`
  - `_tab_icon(t, unterstrichen)` — Die Reiter-Symbole aus dem Katalog (gut sichtbar in beiden Designs): Farbeimer (Füllung und Linie) und Funken (Effekte).
  - `_zusatz_radios(abschnitt)` — Weitere Auswahlpunkte am Ende der Liste („fuell“ oder „linie“).
  - `_zusatz_felder(abschnitt, a)` — Weitere Felder am Ende des Abschnitts („fuell“ oder „linie“).
  - `_seite_fuellung(w)`
  - `_farbe_gewaehlt(c)` — „Keine Farbe“ in der Palette wählt die Füllungsart ohne Farbe (Keine bzw. Automatische Füllung).
  - `_k_breite()`
  - `_k_breite_setzen(pt)`
  - `fuellung_waehlen(art)` — Die Füllungsart wählen („verlauf“, „textur“, „muster“, „bild“ …); die Füllung gilt sofort, die Felder dazu sind bedienbar.
  - `_neu(*_)`
  - `_felder_zeigen()` — Nur die Felder zur gewählten Füllungs- und Linienart zeigen (Keine und Automatisch haben keine weiteren Felder).
  - `_setze_fuellung(w)`
  - `_werte_fuellung()`
  - `_seite_effekte(w)`
  - `_drehung_zuruecksetzen()`
  - `_weich_einschalten()`
  - `_weich_symbol(radius)` — Das Bildchen der Liste: ein Quadrat, dessen Rand mit der Größe weicher wird.
  - `_weich_menue()` — Voreinstellungen als Liste mit Bild und Text: Keine weichen Kanten · 1 · 2,5 · 5 · 10 · 25 · 50 Punkt.
  - `_setze_effekte(w)`
  - `_werte_effekte()`

### `oberflaeche/baukasten/formatierung/rahmen_schattierung.py`

„Rahmen und Schattierung“ als Baustein: das Fenster mit den Karteireitern Rahmen, Seitenrand und Schattierung.

- `_kopf(text)` — Kleine Überschrift über einem Feld — der Baustein ``abschnittstitel``.
- `_einstellung_symbol(art, px)` — Kleines Blatt mit Textzeilen und dem Rahmen, den die Einstellung setzt.
- `_stil_symbol(art, groesse)` — Probe einer Linienart für die Liste „Formatvorlage“.
- `_breite_symbol(pt, groesse)`
- `_muster_symbol(schluessel, px)`
- **class `_Vorschau`**(QWidget) — Blatt mit zwei Absätzen aus grauen Zeilen; zeigt Rahmen und Füllung und schaltet Kanten per Klick.
  - `__init__(kanten_klick)`
  - `sizeHint()`
  - `minimumSizeHint()`
  - `_feld()`
  - `paintEvent(_e)`
  - `_luecke(f)`
  - `mousePressEvent(e)`
- **class `_KantenFlaeche`**(QWidget) — Die Vorschau mit den Kantenknöpfen um sich (oben, Mitte, unten links daneben; links und rechts darunter). Die Vorschau wächst mit
  - `__init__(vorschau, links, unten_l, unten_r)`
  - `_rand()`
  - `_vorschau_breite(breite)`
  - `_vorschau_hoehe(w)`
  - `hasHeightForWidth()`
  - `heightForWidth(breite)`
  - `sizeHint()`
  - `minimumSizeHint()`
  - `setMaximal(maximal)`
  - `resizeEvent(ev)`
  - `_lege()`
- **class `_RahmenSeite`**(QWidget) — Einstellung · Linienart · Farbe · Breite · Vorschau mit Kantenknöpfen · Übernehmen für.
  - `__init__(linie, *, seitenrand, innen_h, fuer, abstand_mm)`
  - `_bauen_einstellung(g)` — Einstellung: eine Reihe Symbole (der Name steht im Tipp), bei Platzmangel in der nächsten Zeile weiter.
  - `_bauen_vorschau(g)` — Vorschau mit Kantenknöpfen (wächst mit der Breite).
  - `_bauen_farbe_breite_art(g, basis)`
  - `_bauen_linienart(g)`
  - `_bauen_fuer(g, fuer, linie)` — Übernehmen für, Optionen.
  - `_anfangswerte(basis)` — Anfangswerte, Verkabelung.
  - `linie_wert()`
  - `_setze_einstellung(art)`
  - `_kante(k, an)`
  - `_zeige_seiten()`
  - `_neu()`
  - `_abstand_vorschau()` — Der Abstand, den die Vorschau des Seitenrahmens zeigt (in mm).
  - `_optionen()`
- `_blatt_vorschau(p, rect)` — Das Blatt der Optionen-Fenster: oben weiß, nach unten vom Feld abgeschnitten, darauf ein Textblock (die erste Zeile eingerückt).
- **class `_PolsterDialog`**(QDialog) — „Optionen …“ am Absatzrahmen: Abstand des Rahmens vom Text, oben, unten, links und rechts (mit Einheit), dazu eine Vorschau.
  - `__init__(parent, werte, linie)`
  - `werte()`
  - `_male(p, rect)` — Ein Blatt mit Textzeilen; der Rahmen um den Absatz hat die eingestellten Abstände zum Text.
- **class `_SeitenOptionenDialog`**(QDialog) — „Optionen …“ am Seitenrand: Abstand (vom Text oder vom Seitenrand), „Gemessen von“, die vier Optionen und eine Vorschau der Seite.
  - `__init__(parent, w, linie)`
  - `_messen(*_)`
  - `werte()`
  - `_male(p, rect)` — Ein Blatt mit Text; der Rahmen liegt je nach „Gemessen von“ um den Text oder am Blattrand.
- **class `_AbstandDialog`**(QDialog) — „Optionen …“ am Seitenrand: Abstand des Rahmens vom Seitenrand.
  - `__init__(parent, mm)`
  - `wert()`
- **class `_SchattierungSeite`**(QWidget) — Ausfüllen (Farbe) · Muster (Art, Farbe) · Vorschau · Übernehmen für.
  - `__init__(fuell, muster, fuer)`
  - `werte()`
  - `_neu()`
- **class `RahmenSchattierungDialog`**(PanelFaehig, QDialog) — Das Fenster „Rahmen und Schattierung“. Die Reiter und ihre Werte stehen oben in der Beschreibung des Bausteins.
  - `__init__(parent, *, rahmen, fuell, muster, seitenrand, mit_seitenrand, fuer, innen_h, seite)`
  - `passe_an(breite, hoehe)` — Vorschau so groß, wie die Seitenleiste Platz hat (neben ihr stehen Farbe und Breite).
  - `rahmen()`
  - `schattierung()` — (Füllfarbe oder None, (Musterschlüssel, Musterfarbe) oder None).
  - `seitenrand()`

### `oberflaeche/baukasten/formatierung/ruby_dialog.py`

Das Fenster „Phonetisches Leitzeichen“ als Baustein: der Text in Teilen (je eine Zeile), zu jedem Teil sein Leittext, dazu Ausrichtung, Abstand, Schrift und Größe.

- **class `RubyDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, teile, schrift)`
  - `_zeile_anhaengen(basis, ruby, wie, an)`
  - `_gewaehlt()`
  - `_gruppieren()`
  - `_mono()`
  - `_alle_weg()`
  - `_standard()`
  - `_alles()`
  - `_zeile_gewaehlt(r, _c, _vr, _vc)`
  - `_feld_geaendert(*_)`
  - `_malen(p, rect)`
  - `zeilen()`

### `oberflaeche/baukasten/formatierung/schreibweise_dialog.py`

Das Fenster „Groß-/Kleinschreibung“ als Baustein: eine der fünf Arten wählen.

- **class `SchreibweiseDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, art)`
  - `art()`

### `oberflaeche/baukasten/formatierung/schriftart_dialog.py`

Das Fenster „Schriftart“ (Karteireiter Schriftart und Zeichenabstand) als Baustein.

- `zeichen_waehlen(parent, zeichen)` — Das Schriftart-Fenster für Nummern und Vorlagen. → die gewählten Werte (alle Felder von ``ZEICHEN``) oder None bei „Abbrechen“.
- `_schrift_combo(thema)` — Schriftauswahl; ``thema``: Einträge wie „+Textkörper“ davor (die Vorgabe des Dokuments, hier: keine bestimmte Schrift).
- `_schnitt_combo()`
- `_ueberschrift(text)`
- **class `SchriftartDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, werte, *, umfang)`
  - `_schnitt_setzen(c, fett, kursiv)`
  - `_schnitt_lesen(t)`
  - `_groesse_lesen(t)`
  - `_groesse_setzen(c, g)`
  - `setze(w)`
  - `werte()`
  - `_texteffekte()`
  - `_standard()` — „Standard …“: diese Schrift gilt künftig für neue Dokumente (der Aufrufer speichert sie).
  - `_neu()`
  - `_male(p, rect)`

### `oberflaeche/baukasten/formatierung/text_format.py`

Textformat-Bausteine: Schriftname, Größe, Fett, Kursiv, Ausrichtung, Zeilenabstand — so wie im Band (Start ▸ Schriftart, Absatz).

- `schrift_feld(combo, variante)` — Das Feld für den Schriftnamen (im Band mit Live-Vorschau, im Fenster ohne).
- `groesse_feld(combo, variante)` — Das Feld für die Schriftgröße: zum Tippen und mit der Liste der üblichen Größen.
- `text_knopf(symbol, tipp)` — F, K oder U als Knopf zum Ein-/Ausschalten, in dem Schnitt, den er bedeutet (wie im Band).
- `ausrichtung_knoepfe()` — Linksbündig, Zentriert, Rechtsbündig, Blocksatz — gleiche Symbole und Namen wie im Band; immer höchstens einer gewählt.
- `_zeilen_symbol(abstand)`
- `_abstand_symbol(mehr)`
- `_einzug_symbol(mehr)`
- **class `TextFormatLeiste`**(QWidget) — Zwei Zeilen wie im Band: Schrift, Größe, Fett, Kursiv · Ausrichtung (und mit ``absatz=True`` Zeilenabstand, Absatzabstand und
  - `__init__(parent, *, absatz)`
  - `_trenner()`
  - `_aktion(name, symbol, fn)`
  - `_ausrichtung(schl, an)`
  - `_zeilenabstand(f, an)`
  - `_zeige_zeilen()`
  - `_abstand(delta)`
  - `_einzug(delta)`
  - `werte()`
  - `setze(d)` — Alle Felder auf die Werte einer Vorlage stellen (ohne ``geaendert`` zu melden).
- `_zu_format_schrift(f, w)` — Schriftfamilien (lateinisch, asiatisch, komplex), Betonung, Doppeltes, Fett/Kursiv, Größe, Farbe.
- `_zu_format_linien(f, w)` — Unterstreichung, Durchstreichung, Hoch/Tief, Kapitälchen/Großbuchstaben.
- `_zu_format_abstand(f, w)` — Zeichenabstand, Unterschneidung, Skalierung, Position, Raster.
- `zu_format(w)` — Die Werte eines Zeichenfensters als Zeichenformat (zum Anwenden im Editor und für Vorschauen).
- `_aus_format_unter(cf, w)`
- `_aus_format_schriften(cf, w)` — Doppelt durchgestrichen, Betonung, asiatische und komplexe Schrift.
- `_aus_format_abstand(cf, w, standard_groesse)`
- `aus_format(cf, standard_schrift, standard_groesse)` — Die Werte eines Zeichenformats (zum Vorbelegen eines Zeichenfensters).
- `zeichne_absaetze(p, rect, absaetze, mittig)` — Absätze (Absatzformat, Zeichenformat, Text) in ein Rechteck zeichnen — die Vorschau der Formatierungsfenster.

### `oberflaeche/baukasten/formatierung/text_fuellarten_mixin.py`

Textfüllung der Diagramm-Textoptionen mit fünf Arten wie in der Vorlage: Keine Füllung · Einfarbige Füllung · Farbverlauf · Bild- oder Texturfüllung · Musterfüllung.

- **class `TextFuellartenMixin`**
  - `_text_fuellarten_bauen()`
  - `_pinsel_wahl(art)` — Ein Feld einer neuen Art wurde bedient: damit ist diese Art gewählt.
  - `_bild_waehlen()`
  - `_sichtbar()`
  - `_setze_fuellung(w)`
  - `werte()`

### `oberflaeche/baukasten/formatierung/texteffekt_dialog.py`

Das Fenster „Texteffekte formatieren“ als Baustein: Reiter „Textfüllung und -kontur“ und „Effekte“ (Schatten, Reflektion, Leuchten, 3D-Format).

- `seitengitter(widget)` — Das ``FormularGitter`` der Seitenleiste „Formatierung“: Beschriftungen links, alle Felder in einer gleich breiten Spalte rechts.
- **class `_Pfeil`**(QToolButton) — Der Pfeil vor einer Abschnittsüberschrift: schaltet um wie ein Umschaltknopf (``setChecked``, ``toggled``), zeigt aber keinen Knopfrahmen.
  - `__init__()`
  - `isChecked()`
  - `setChecked(an)`
  - `toggle()`
- **class `Abschnitt`**(QWidget) — Aufklappbarer Abschnitt: Pfeil und Überschrift in Großbuchstaben links, optional ein Bedienelement rechts (z. B. die Voreinstellung).
  - `__init__(titel, rechts)`
  - `_umschalten(an)`
  - `kopffeld(widget, text)` — Das Menü des Abschnitts (Voreinstellung, Farbe) rechts im Kopf, in der Breite der Feldspalte darunter.
  - `zeile(text, widget)`
  - `auswahl(*radios)` — Auswahlpunkte (Füllungsart, Linienart) ordentlich untereinander, eine je Zeile.
  - `breit(widget)`
- `_linien_icon(art, form, groesse)` — Kachel der Linienauswahl: eine Linie in Strichart und Form.
- **class `TexteffektPanel`**(QWidget)
  - `__init__(parent, werte)`
  - `_scroll(seite)`
  - `_tab_icon(t, unterstrichen)`
  - `_seite_fuellung(w)`
  - `_kopffarbe(c)` — Die Farbe im Kopf der Textfüllung: „Keine Füllung“ oder eine einfarbige Füllung.
  - `_kopf_verlauf(farbe)` — „Graduelle Füllung“ im Farbmenü: Farbverlauf von hell nach dunkel in dieser Farbe.
  - `_linien_auswahl()`
  - `_linie_gewaehlt(schluessel)`
  - `_voreinstellungs_knopf(text)`
  - `_seite_effekte(w)`
  - `_schritt_feld(lo, hi, suffix, schritt, nk)` — Zahlenfeld mit Minus und Plus an den Seiten (wie die Größenfelder im 3D-Format der Vorlage).
  - `_zweier(*teile)`
  - `_d3_zuruecksetzen()`
  - `_menue_zeigen(m, knopf)`
  - `_schatten_auswahl()`
  - `_refl_auswahl()`
  - `_leucht_auswahl()`
  - `_material_auswahl()`
  - `_licht_auswahl()`
  - `_setze_material(material, licht)`
  - `_setze_teil(name, wert, text)` — Eine Voreinstellung übernehmen: die Regler zeigen ihre Werte.
  - `_teil_in_regler(name)`
  - `setze(w)` — Werte ins Panel schreiben (ohne ``geaendert`` zu melden).
  - `_setze(w)`
  - `_setze_fuellung(w)`
  - `_setze_effekte(w)`
  - `werte()`
  - `_werte_fuellung()` — (Werte der Füllung und Kontur, zusätzliche Schlüssel dazu: Verlauf, Konturverlauf, Konturform).
  - `_werte_effekte()` — Schatten, Reflektion, Leuchten und 3D mit den Werten der Regler (gemeinsam für Text und Objekte).
  - `_einschalten(name)` — Ein Regler eines Effekts wurde bewegt: der Effekt ist damit an (mit den Werten, die die Regler zeigen).
  - `_sichtbar()` — Nur die Felder zeigen, die zur gewählten Füllung und Linie gehören (spart Höhe in der Seitenleiste). Das Objekt-Panel baut die Seite selbst und hat sie nicht.
  - `_neu(*_)`
  - `_melden()`
  - `_male(p, rect)`
- **class `TexteffektDialog`**(PanelFaehig, QDialog) — Das Fenster „Texteffekte formatieren“: das Panel mit „OK“ (wie in der Vorlage; das Schließen-Kreuz bricht ab). Felder des Panels sind hier erreichbar.
  - `__init__(parent, werte)`
  - `passe_an(breite, hoehe)` — Die Seite nimmt die ganze Höhe der Seitenleiste: die Abschnitte rollen sonst in einem winzigen Streifen.
  - `__getattr__(name)`

### `oberflaeche/baukasten/formatierung/textfeld_abschnitt.py`

Abschnitt „AUSRICHTUNG“ der Seite „Textfeld“ (Textoptionen eines Diagrammteils) — nach der Vorlage.

- `_still(x, wert, setter)`
- **class `TextfeldAbschnitt`**(Abschnitt)
  - `__init__(parent)`
  - `freigeben(raender, gerade)`
  - `setze(feld)` — Ohne Meldung.
  - `werte()`

### `oberflaeche/baukasten/formatierung/umschlossen_dialog.py`

Das Fenster „Eingeschlossene Zeichen“ als Baustein: Vorlage (Ohne, Text reduzieren, Symbol erweitern), Text und Form (Kreis, Quadrat, Dreieck, Raute).

- `form_bild(form, px, gross, text)` — Die Form als kleines Bild (für die Liste) oder, mit ``text``, als Beispiel für die Vorlage.
- `_vorlagenbild(vorlage)`
- **class `UmschlosseneZeichenDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, text, form, vorlage)`
  - `werte()`

## `oberflaeche/baukasten/geruest`

### `oberflaeche/baukasten/geruest/__init__.py`

Unterpaket ``geruest`` von ``oberflaeche.baukasten``.


### `oberflaeche/baukasten/geruest/abschnitt_gruppe.py`

Aufklappbare Abschnitte als Gruppe: höchstens einer ist offen.

- **class `EinzelOffen`**
  - `__init__(*abschnitte)`
  - `_geoeffnet(offen)`
  - `schliesse_alle()`

### `oberflaeche/baukasten/geruest/aktionen_leiste.py`

„Meine Aktionen“: die Schnellen KI-Aktionen (Eigene Assistenten) als Knöpfe — in der Seitenleiste der Schreibhilfe und im KI-Chat dieselbe Leiste.

- **class `AktionenLeiste`**(QWidget)
  - `__init__()`
  - `verbinde(dienst, fenster)`
  - `fuellen()` — Die Knöpfe neu aufbauen: je Aktion einer, dazu „＋ Neue Aktion“.
  - `zustand()` — Die Aktionen laufen nur mit verbundenem Modell und nicht, solange die KI schon arbeitet; „Neue Aktion“ geht immer.

### `oberflaeche/baukasten/geruest/einklappgruppe.py`

Eingeklappte Gruppe („Weitere Einstellungen“): ein Knopf mit Pfeil, darunter der Inhalt, der erst auf Wunsch aufgeht.

- **class `EinklappGruppe`**(QWidget) — Knopf plus Inhalt. Der Inhalt kommt in ``innen`` (ein ``QVBoxLayout``).
  - `__init__(titel, parent)`
  - `_zeigen(offen)`
  - `ausklappen(offen)`
  - `ist_offen()`

### `oberflaeche/baukasten/geruest/fenster_stapel.py`

Fenster in einem Fenster: Unterfenster öffnen sich als Seite im selben Fenster statt als neues Fenster darüber.

- **class `FensterStapel`**(QDialog)
  - `__init__(wurzel, parent)`
  - `oeffne(d, fertig)` — Ein Fenster als oberste Seite einlegen; ``fertig()`` wird nach „OK“ gerufen.
  - `_beendet(d, ergebnis)`
  - `_zurueck()`
  - `_kopf_neu()`
- `ausfuehren(d)` — ``d`` als oberstes Fenster eines Stapels zeigen und warten (wie ``d.exec()``): seine Unterfenster öffnen sich als Seiten im selben Fenster.
- `stapel_von(w)`
- `zeige_unter(elter, d, fertig)` — ``d`` als Unterfenster von ``elter`` zeigen; ``fertig()`` läuft nach „OK“. Im ``FensterStapel`` als Seite, sonst als Fenster mit ``exec``.

### `oberflaeche/baukasten/geruest/panel_rahmen.py`

Rahmen eines Feldes in einer Seitenleiste: Titel, davor/dahinter Knöpfe, ein Menü (⋯ oder ⚙) und ✕ zum Schließen; darunter der Inhalt.

- `panel_kopf(*teile, dehnen)` — Die Kopfzeile aller Seitenleistenfenster samt Trennlinie darunter: ``teile`` von links nach rechts.
- `_knopf(symbol, tipp)`
- **class `PanelRahmen`**(QWidget)
  - `__init__(titel, menue_zeichen, menue, knoepfe, schliessbar, titel_teile)` — ``knoepfe``: Folge von (Lucide-Name oder Text, Tooltip, Funktion) — stehen vor dem Menü.
- `rollflaeche(inhalt, *, immer)` — Der Rollbereich in Seitenleisten-Panels: ohne Rahmen, nie seitlich rollend, Rollbalken nach Bedarf — mit ``immer=True`` steht er immer

### `oberflaeche/baukasten/geruest/schmal.py`

Ein Fenster auf eine schmale Breite bringen (Seitenleiste), ohne dass etwas abgeschnitten wird oder seitlich gerollt werden muss.

- `_alle_layouts(w)`
- `_breite(l)`
- `_zeile_zu_fluss(l)`
- `_abstand(g)`
- `_tabelle_umbrechen(g, avail)`
- `_spalten_umbrechen(g, zeilen, avail)` — So viele Spalten nebeneinander, wie hineinpassen; der Rest darunter.
- `_zeile_einheiten(items)` — Beschriftung und das folgende Feld bleiben zusammen (eine Einheit).
- `_zeilen_umbrechen(g, zeilen, avail)` — Jede Zeile läuft über mehrere Gitterzeilen, wenn sie nicht passt.
- **class `_Umbruchtext`**(QLabel) — Der Text neben einem Ankreuzfeld, mit Zeilenumbruch; ein Klick darauf schaltet das Feld wie sonst der Text.
  - `__init__(knopf, text)`
  - `eventFilter(obj, ev)`
  - `mouseReleaseEvent(ev)`
- `_knopf_umbrechen(l, k)`
- `_nein(l)` — Ein Layout (oder eines darüber), das nicht umbrechen soll: ``layout.setProperty("schmal_nein", True)``.
- `_beschriftungen_umbrechen(d, breite)` — Lange Texte laufen in die nächste Zeile statt über den Rand.
- `_kontrollfelder_umbrechen(l, breite)`
- `_layout_umbrechen(l, breite)`
- `schmal_machen(d, breite)` — Alles in ``d``, was breiter als ``breite`` Pixel ist, umbrechen.
- `_breite_gitter(g)`

### `oberflaeche/baukasten/geruest/schnellleiste_zustand.py`

Zustand der Schnellleiste neben dem gewählten SmartArt-Knoten: ob ⊖ fehlt und welche Knöpfe grau sind. Reine Funktionen, zeichnen nichts.

- `ohne_minus(leiste, knoten)` — Bei gewähltem SmartArt-Knoten (Knopfsatz mit ``sa_form`` und ein Knotenrechteck) steht kein ⊖ (wie in der Vorlage).
- `knopf_aktiv(b, name)` — Ob der Knopf bedienbar ist (sonst grau). Unbekannte Knöpfe und fehlende Befehle gelten als aktiv; ``sa_level`` genügt eine Richtung.

### `oberflaeche/baukasten/geruest/spalten.py`

Zweispalter: links Navigation/Blatt/Liste, rechts Inhalt — der eine Baustein für alle zweispaltigen Seiten.

- **class `ZweiSpalter`**(QWidget) — ``links``/``rechts``: beliebige Widgets. ``breit_ab``: Breite, ab der sie nebeneinander stehen (``0`` = immer nebeneinander,
  - `__init__(links, rechts, *, breit_ab, links_breite, oben, breit_stretch, gestapelt_stretch, raender_breit, raender_gestapelt, abstand, parent)`
  - `anordnen(breit)` — Setzt Richtung, Reihenfolge, Ränder und Breite neu; bei gleichem Zustand geschieht nichts.
  - `resizeEvent(e)`

### `oberflaeche/baukasten/geruest/werkbank.py`

Werkbank: die Funktionen eines Reiters der Schreibhilfe als große, selbsterklärende Zeilen (Symbol, Name, Hinweis, Tastenkürzel, bei Schaltern „an/aus“).

- **class `FunktionsZeile`**(QFrame) — Eine große, anklickbare Zeile; mit Tastatur bedienbar (Tab, Leertaste oder Eingabe) und mit Fokusrahmen.
  - `__init__(f, fenster)`
  - `mouseReleaseEvent(e)`
  - `keyPressEvent(e)`
  - `_los()`
  - `_in_navigation()`
  - `_beschreibung(an)` — Was ein Bildschirmleser zusätzlich zum Namen hört: Art, Zustand, Hinweis, Kürzel.
  - `aktualisieren()`
- **class `Werkbank`**(QScrollArea) — Die Zeilen eines Reiters; ``oben`` (optional) ist ein Widget über den Zeilen, etwa ein Hinweis.
  - `__init__(fenster, reiter, oben, nur, ohne)`
  - `aktualisieren()`

### `oberflaeche/baukasten/geruest/zugaenglichkeit.py`

Zugängliche Namen für Knöpfe ohne eigenen Namen (Screenreader, Sprachsteuerung).

- `name_fuer(knopf)` — Der Name, den ein Screenreader für diesen Knopf lesen soll: Text, sonst Tooltip, ohne Tastenkombination und Erklärung.
- **class `NamenFilter`**(QObject) — Setzt beim ersten Anzeigen eines Knopfes den zugänglichen Namen, wenn noch keiner gesetzt ist.
  - `eventFilter(obj, ev)`
  - `einhaengen(app)`

### `oberflaeche/baukasten/geruest/zusatz_panel.py`

Zusatzfenster in der Seitenleiste: ein Fenster (zum Beispiel „Nummerierung und Aufzählungszeichen“) öffnet sich nicht über dem Text, sondern als Seite

- **class `_Seite`**(QWidget) — Eine Seite des Panels: oben der Inhalt des Fensters (rollt bei Bedarf, nie seitlich, steht oben in seiner natürlichen Höhe),
  - `__init__(d)`
  - `_anheften(d)` — Die Knopfzeile des Fensters aus seinem Layout nehmen (sie bleibt mit dem Fenster verbunden).
  - `freigeben()` — Fenster wieder aus der Seite lösen (der Aufrufer liest danach noch Werte aus ihm).
- `zusatz_knopf(symbol, tipp, aktion, name)` — Ein Knopf der Titelzeile (Zurück, Schließen, Anheften): flach, mit Symbol aus ``icons``.
- `zusatz_kopf(*teile)` — Die Titelzeile der Seitenleistenfenster samt Linie darunter: ``teile`` von links nach rechts; das erste QLabel/der Titel nimmt den freien Platz.
- **class `ZusatzPanel`**(QWidget) — Die Seite in der Seitenleiste. Unterfenster (``zeige_unter``) legen sich als weitere Seite darüber, mit „← Zurück“.
  - `__init__()`
  - `oeffne(d, fertig)`
  - `_beendet(d, ergebnis)`
  - `unter_ausfuehren(d)` — Ein weiteres Fenster als Seite über die offene legen und warten (wie ``exec``): zum Beispiel „Farben“ aus „Rahmen und Schattierung“.
  - `_zurueck()`
  - `_schliessen()`
  - `_kopf_neu()`
  - `raeumen()`
- `ausfuehren_in(seite, d, vorher, nachher)` — ``d`` als unterste Seite von ``seite`` zeigen und warten (wie ``d.exec()``). ``vorher()`` zeigt die Seitenleiste, ``nachher()`` stellt sie zurück.
- `ausfuehren_im_stapel(stapel, d, breite, hoehe)` — ``d`` als Seite in einem anderen Stapel zeigen und warten (wie ``d.exec()``) — zum Beispiel in der linken Seitenleiste, damit ein
- `leiste_fuer(d)` — Die Seitenleiste, in der ``d`` sich zeigen soll — oder None (dann wie bisher als Fenster): Panels aus, kein Hauptfenster, oder ein anderes Fenster hält schon den Fokus.
- **class `PanelFaehig`** — Zusatzfenster (Einstellungen, die man selten braucht): ``exec()`` zeigt sie in der Seitenleiste statt über dem Text.
  - `exec()`

## `oberflaeche/baukasten/medien`

### `oberflaeche/baukasten/medien/__init__.py`

Medien- und Bildbausteine.


### `oberflaeche/baukasten/medien/alternativtext_abschnitt.py`

Abschnitt „ALTERNATIVTEXT“ (Titel und Beschreibung) für die Seite „Größe und Eigenschaften“ — nach der Vorlage.

- **class `AlternativtextAbschnitt`**(Abschnitt)
  - `__init__(parent, mit_titel, mit_dekorativ)`
  - `_start(*_)`
  - `setze(titel, text)` — Ohne Meldung; ein Feld mit dem Fokus (Eingabe läuft) bleibt unberührt.
  - `_dekorativ(an)`
  - `_felder_sperren(an)`
  - `setze_dekorativ(an)` — Ohne Meldung.

### `oberflaeche/baukasten/medien/bild_alternativtext_panel.py`

Seitenleiste „Alternativtext“ für ein Bild: Beschreibung und „Als dekorativ markieren“ (der Abschnitt ``AlternativtextAbschnitt``).

- **class `BildAlternativtextPanel`**(QWidget)
  - `__init__(parent, werte)`
  - `werte()`
  - `_melde()`
  - `setze(werte)`

### `oberflaeche/baukasten/medien/bild_export.py`

„Als Bild exportieren“: die Bildlayoutkarten und Einstellungen in der rechten Spalte des Datei-Menüs.

- **class `_Karte`**(QAbstractButton) — Eine wählbare Karte mit Bildchen und Beschriftung; gewählt mit blauem Rand und Haken in der Ecke.
  - `__init__(text, lang)`
  - `sizeHint()`
  - `paintEvent(_e)`
  - `_bildchen(p, dunkel)`
- **class `BildExportAnsicht`**(QWidget) — Bildexport als Seite in der zweiten Spalte des Datei-Menüs.
  - `__init__(parent, startordner, dpi, exportieren, zurueck)`
  - `_ordner_waehlen()`
  - `_exportieren()`
  - `_erstes_bild_oeffnen()`
  - `_zielordner_oeffnen()`
- `_abschnitt(titel, hilfe, layout)`
- `_bilder_ordner()`

### `oberflaeche/baukasten/medien/bild_zoom.py`

Das Fenster „Vergrößern“ (Lupe in der Schnellleiste am Bild): das Bild in seiner Auflösung ansehen, mit Regler und Mausrad zoomen.

- **class `_Ansicht`**(QScrollArea) — Rollbereich, dessen Mausrad (mit oder ohne Strg) den Zoom ändert.
  - `__init__(bei_zoom)`
  - `wheelEvent(e)`
- **class `BildZoomFenster`**(PanelFaehig, QDialog)
  - `__init__(parent, bild, titel)`
  - `aktualisieren(_w)` — Das Bild im gewählten Maßstab zeigen.

### `oberflaeche/baukasten/medien/bildformate.py`

Die gemeinsame Dateiliste aller Bild-Fenster (Einfügen, Bild ändern, Füllung, Wasserzeichen). Der Chat hat seine eigene (PNG, JPEG, WebP).


### `oberflaeche/baukasten/medien/datei_symbole.py`

Lokale, vollständige Dateityp-Symbole aus der zentralen Iconsammlung.

- `icon_namen(name)` — Liefert den passenden lokalen Dateityp und den generischen Rückfall.
- `datei_symbol(name)` — Rendert ein vollständiges farbiges Dateiblatt aus einem gebündelten SVG.

### `oberflaeche/baukasten/medien/design_bildchen.py`

Bildchen für die Galerien Designs, Farben, Schriftarten und Effekte (Reiter Seitenlayout). Jede Funktion gibt einen Zeichner

- `_text(p, r, text, familie, px, ausr, fett, farbe)`
- `design_zeichner(farben, kopf)` — Weiße Karte mit „Aa“ in der Überschriftschrift und den sechs Akzentfarben als Band.
- `farbreihe_zeichner(farben, name)` — Eine Zeile der Liste „Farben“: acht Farbfelder, rechts daneben der Name.
- `schriftpaar_zeichner(name, kopf, text)` — Eine Zeile der Liste „Schriftarten“: Kästchen „Aa“, darüber der Name, dann die Überschrift- und die Textschrift in sich selbst.
- `effekt_zeichner(fx)` — Blauer Blockpfeil auf hellem Feld, mit dem Effekt gezeichnet (wie er an Formen erscheint).

### `oberflaeche/baukasten/medien/listen_symbole.py`

Kleine Vorschaubilder für Aufzählungs- und Nummerierungsarten (drei Zeilen mit Zeichen davor).

- `liste_zeichner(marke)` — ``marke``: 'disc', 'circle', 'square' oder die Zeichenfolge der ersten drei Nummern (z. B. '1.\|2.\|3.'); None = Keine.

### `oberflaeche/baukasten/medien/seiten_bildchen.py`

Kleine Seitenbilder für Galerien (Einfügen ▸ Seitenzahl, Wasserzeichen, Deckblatt). Jede Funktion gibt einen Zeichner

- `_blatt(p, r, verhaeltnis)` — Ein weißes Hochformat-Blatt mittig in ``r``; gibt das Blattrechteck zurück.
- `_zeilen(p, r, n)`
- `seitenzahl_zeichner(ort, ausrichtung)` — ``ort``: "kopf" \| "fuss"; ``ausrichtung``: "left" \| "center" \| "right" \| "aussen" \| "innen" (zwei Seiten nebeneinander).
- `wasserzeichen_vorschau(w)` — Blatt mit einem beliebigen Wasserzeichen (Text oder Bild, Lage, Transparenz) wie in der Ausgabe (``editor/seite/wasserzeichen.py``).
- `wasserzeichen_zeichner(text, winkel, farbe)`
- `plus_zeichner(beschriftung)` — Kachel „Hinzufügen“: großes graues Plus auf hellem Feld.
- `deckblatt_zeichner(vorlage)` — Die Deckblätter aus ``editor.dokument.einfuegen.DECKBLATT_VORLAGEN`` im Kleinen: Titel als dicker Balken, Angaben als dünne Zeilen.
- `raender_zeichner(oben, unten, links, rechts)` — Blatt mit dem Satzspiegel als Rahmen (Seitenlayout ▸ Ränder); die Maße in mm, Blatt A4.
- `format_zeichner(quer)` — Hoch- oder Querformat: ein Blatt mit gestrichelter Mittellinie.
- `papier_zeichner()` — Blatt mit Eselsohr (Seitenlayout ▸ Größe).
- `textrichtung_zeichner(art)` — Kästchen mit „ABC“ in der jeweiligen Richtung: "waagerecht", "senkrecht_rl", "senkrecht_lr", "dreh90", "dreh270", "asiatisch270".

### `oberflaeche/baukasten/medien/umbruch_symbole.py`

Die Bildchen für den Textumbruch um ein Bild (wie in der Vorlage): Textzeilen in Grau, das Bild als blaues Feld.

- `umbruch_zeichner(art)`

## `oberflaeche/baukasten/vorlagen`

### `oberflaeche/baukasten/vorlagen/__init__.py`

Vorlagenbausteine.


### `oberflaeche/baukasten/vorlagen/formatvorlagen_bereich.py`

Der Bereich „Formatvorlagen und Formatierung“ (Start ▸ Einstellungen) als Baustein — wie der Bereich der Vorlage in der rechten Seitenleiste:

- `vorlagen_namen(art, ed)` — Die Namen für die Liste: gültige (Katalog und eigene), verwendete (im Dokument) oder alle.
- `vorlagen_schrift(name, vorschau)` — Die Schrift, in der eine Vorlage in Listen erscheint (Größe gedämpft, damit die Liste ruhig bleibt).
- **class `_Absatzmarke`**(QStyledItemDelegate) — Zeile der Liste mit dem Zeichen ↵ rechts (Absatzvorlage), wie in der Vorlage; etwas Luft über und unter dem Namen.
  - `sizeHint(option, index)`
  - `paint(p, option, index)`
- **class `FormatvorlagenBereich`**(PanelFaehig, QDialog)
  - `__init__(parent, get_editor, anwenden, neu)`
  - `_stil_jetzt()`
  - `fuellen()`
  - `waehle(name)`
  - `_neu_vorlage()`
  - `_formatierung_loeschen()`

### `oberflaeche/baukasten/vorlagen/vorlagen_chips.py`

Zwei kleine Bausteine für Erstellen-Fenster (Schnelle KI-Aktion, KI-Assistent): Vorlagen-Chips und ein aufklappbarer Bereich.

- `_link(text)`
- **class `VorlagenChips`**(QWidget) — Chips zum Antippen; zuerst ``zuerst`` Stück, mit „Alle anzeigen“ alle. Meldet den Index des gewählten Chips.
  - `__init__(namen, zuerst, parent)`
  - `umschalten()`
- **class `AufklappBereich`**(QWidget) — Ein Link-Knopf „<Titel> anzeigen/ausblenden“ und darunter ein Bereich, der aufklappt (``layout_innen``).
  - `__init__(titel, parent)`
  - `umschalten(an)`

### `oberflaeche/baukasten/vorlagen/vorlagen_galerie.py`

Die Seite „Neu“: leeres Dokument direkt starten oder Standard- und eigene Vorlagen getrennt durchsuchen.

- `_blatt_bild(doc, page)` — Erste Seite eines Dokuments, auf Kachelbreite verkleinert.
- `_geruest_bild(muster, benutzer)`
- `_datei_bild(pfad)`
- **class `_Kachel`**(QToolButton) — Ein Blatt mit Name darunter; eine Rubrik zeigt zusätzlich ein Ordnerzeichen mit der Zahl ihrer Vorlagen.
  - `__init__(name, art, wert, schluessel, anzahl)`
  - `_platzhalter(symbol)`
  - `bild_setzen(pm)`
  - `_mit_ordnerzeichen(pm)` — Eine Rubrik: das erste Blatt, dahinter angedeutet weitere, vorn ein Schild mit der Zahl.
- **class `VorlagenGalerie`**(QWidget)
  - `__init__(settings, kann_speichern, benutzer, parent)`
  - `_daten_lesen()`
  - `_ziel()` — Wohin „Dieses Dokument als Vorlage behalten“ ablegt: in die geöffnete Rubrik, sonst in den Vorlagenordner.
  - `_stempel(p)`
  - `_datei_kachel(p, gruppe)`
  - `_geruest_kachel(m)`
  - `_bauen()`
  - `_naechstes_bild()`
  - `_bild_fuer(k)`
  - `rubrik_oeffnen(name)`
  - `_reiter_setzen(schl)`
  - `_sichtbar()`
  - `_anordnen(*_a)`
  - `resizeEvent(e)`
  - `_rubrik_anlegen()`
  - `_ordner_waehlen()`
  - `_ordner_oeffnen()`
  - `neu_lesen()` — Der Ordner wird bei jedem Öffnen der Seite neu gelesen.

## `oberflaeche/bauteile`

### `oberflaeche/bauteile/__init__.py`

Wiederverwendbare Widgets (Symbole, Fließlayout, Live-Vorschau, Minisymbolleiste).


### `oberflaeche/bauteile/fluss_layout.py`

Umbrechendes Layout für die Auswahlknöpfe (nach dem Qt-Beispiel „Flow Layout“).

- **class `FlowLayout`**(QLayout)
  - `__init__(parent, spacing)`
  - `addItem(item)`
  - `count()`
  - `itemAt(i)`
  - `takeAt(i)`
  - `expandingDirections()`
  - `hasHeightForWidth()`
  - `heightForWidth(w)`
  - `setGeometry(r)`
  - `sizeHint()`
  - `minimumSize()`
  - `_lay(rect, test)`

### `oberflaeche/bauteile/kontextmenue.py`

Das Rechtsklick-Menü des Textes, deutsch und in der Reihenfolge der Vorlage: Zwischenablage, Format übertragen, Schriftart, Absatz,

- `_symbole()`
- `menue_bauen(editor, fenster)` — Das Menü für den Editor ``editor`` des Fensters ``fenster``; der Aufrufer zeigt es und löscht es danach.
- `_symbol(name)`
- `_tabellenmenue(m, punkt, b, editor, lesen, auswahl)` — Das Menü in einer Tabelle (Reihenfolge der Vorlage): Zwischenablage · Zeilen/Spalten/Zellen · Rahmen, Anpassen, Ausrichtung, Eigenschaften.
- `objektmenue_bauen(editor, fenster)` — Das Rechtsklick-Menü eines gewählten Objekts (Bild, Form, Textfeld, Diagramm, SmartArt …): Zwischenablage, Layout, Anordnen, Größe, Alternativtext,

### `oberflaeche/bauteile/lese_ende_knopf.py`

Großer Knopf „Lesemodus beenden“, der im Lesemodus oben mittig über dem Fenster schwebt (Band und Seitenleiste sind dann ausgeblendet).

- **class `LeseEndeKnopf`**(QPushButton)
  - `__init__(fenster, aktion)`
  - `zeigen(sichtbar)`
  - `platzieren()`
  - `eventFilter(obj, e)`

### `oberflaeche/bauteile/live_vorschau.py`

Live-Vorschau: Beim Überfahren einer Formatvorlage, Schrift, Größe oder Farbe zeigt das Dokument das Ergebnis schon — ohne dass etwas

- **class `LiveVorschau`**
  - `__init__(fenster)`
  - `aktiv()`
  - `zeigen(anwenden)` — anwenden(editor) wendet das Format an; es wird beim nächsten `ende()` zurückgenommen.
  - `ende()`
- **class `Ueberfahren`**(QObject) — Event-Filter: Zeiger über dem Knopf → Vorschau, Zeiger weg oder Klick → Vorschau beenden.
  - `__init__(vorschau, anwenden)`
  - `eventFilter(o, e)`
- **class `VorschauCombo`**(Auswahlfeld) — Auswahlfeld, dessen Einträge beim Überfahren (highlighted) als Vorschau gezeigt werden.
  - `__init__(vorschau_fn, ende_fn, parent)`
  - `hidePopup()`
- **class `VorschauFontCombo`**(Schriftauswahl)
  - `__init__(vorschau_fn, ende_fn, parent)`
  - `hidePopup()`

### `oberflaeche/bauteile/mini_leiste.py`

Minisymbolleiste: schwebende Leiste mit den häufigsten Formaten über der Auswahl oder am Rechtsklick.

- `_symbole()`
- **class `MiniLeiste`**(QFrame)
  - `__init__(fenster)`
  - `_stil_setzen()` — Bei Themenwechsel Symbole und Menüs in der neuen Schriftfarbe neu zeichnen (Aussehen der Leiste: ``oberflaeche/thema.py``).
  - `_anordnen(tabelle)` — Die beiden Zeilen für den Text- oder den Tabellenmodus füllen (die Knöpfe sind dieselben, nur Auswahl und Reihenfolge wechseln).
  - `_tabellenzeile()` — „Einfügen ▾“ und „Löschen ▾“ als große Symbolknöpfe mit Beschriftung darunter (wie in der Vorlage); Menüs aus ``kern/tabellenaktionen.py``.
  - `_aktionsmenue(b, aktionen)`
  - `tabellenmodus()` — Tabellenmodus (siehe ``editor/tabelle/tabellenzustand.py``): mehrere Zellen oder die ganze Tabelle markiert, über den Verschiebegriff gewählt oder
  - `_modus_anwenden()` — Knöpfe des Modus anordnen; ``True``, wenn sich der Modus geändert hat (Größe und Platz müssen neu gesetzt werden).
  - `_ausrichtung_menue()`
  - `_rahmen_menue()`
  - `_menue_setzen(b, tun)` — Das Menü ist dasselbe wie im Band (Einfügen, Farbpaletten mit „Zuletzt benutzt“ und Vorschau, Zeilenabstand); es entsteht nach jeder Wahl neu.
  - `_nach_farbe(b, tun)`
  - `_schrift(name)`
  - `_groesse(text)`
  - `_tun(tun)`
  - `aktualisieren()`
  - `zeigen(editor, global_pos, rechtsklick, menue)` — Über global_pos zeigen; am Rechtsklick richtet sich die Leiste nach dem Menü (menue = dessen Größe) und überlappt es nie.
  - `_platzieren()` — Größe neu messen und die Leiste über (bzw. am Rechtsklick neben) ``_pos`` setzen; überlappt das Menü nie.
  - `_neben_menue(p, menue, g)` — Platz für die Leiste um das Kontextmenü: über dem Klickpunkt, sonst unter, sonst neben dem Menü; nie überlappend.
  - `_pruefen(editor)`
- **class `_Zu`**(QObject) — Schließt die Leiste bei Tastendruck, Mausrad und Fokusverlust des Editors.
  - `__init__(leiste, editor)`
  - `eventFilter(o, e)`

### `oberflaeche/bauteile/schweb_knopf.py`

Ein runder Knopf, der unten rechts über dem Blatt schwebt.

- **class `SchwebKnopf`**(QToolButton)
  - `__init__(editor, symbol, tipp, aktion)`
  - `platzieren()`
  - `eventFilter(obj, e)`

### `oberflaeche/bauteile/symbole.py`

Einheitliche Symbole: 24×24-Strichzeichnungen aus Lucide, mit Qt gerendert.

- `pfade_original()` — Die mitgelieferten Symbole, ohne Austausch.
- `pfade()`
- `uebersteuern(tausch)` — Austausch {Symbolname: Katalogname} anwenden (Ansicht ▸ Symbol austauschen); leere Zuordnung stellt alles zurück.
- `katalog_bild(name, px, farbe, strich)`
- `pfad_bild(pfad, px, farbe)` — Eine Zeichnung (Katalogpfad oder eigene) als Bild — für Vorschau und Auswahlfenster.
- `hat(name)`
- `_symbolpfad(name)` — Gibt zuerst das semantische Standardsymbol, sonst das Lucide-Katalogsymbol zurück.
- `eigene_zeichnung(text, gefuellt)` — SVG oder Pfaddaten → Zeichnung, auf 24 × 24 gebracht und mittig eingepasst (Zeichenkette für den Austausch).
- `_svg(pfad, farbe)`
- `svg_datei(name, farbe)` — Lucide-SVG als Datei für Qt-Stylesheets, die SVG-Daten nicht direkt annehmen.
- `_pixmap(name, farbe, px)`
- `icon(name, px, farbe)`
- `icon_aus_pfad(pfad, px)` — Ein Liniensymbol aus einem Pfad (24er-Raster, Strichstil wie die übrigen Symbole) in den Farben der Palette.
- `leeren()`
- `setze(knopf, name, px)` — Symbol auf einen Knopf setzen und den Namen merken: beim Wechsel zwischen hell und dunkel bekommt er sein Symbol in der neuen Farbe zurück.
- `alle_neu()` — Nach einem Farbwechsel: alle Knöpfe mit gemerktem Symbol neu beziehen (der Zwischenspeicher ist dann schon geleert).

## `oberflaeche/dialoge`

### `oberflaeche/dialoge/__init__.py`

Dialoge und Optionen.


### `oberflaeche/dialoge/dokument_dialoge.py`

Kleine Dialoge: Seite einrichten, Absatz, Kopf-/Fußzeile, Tabelle, Suchen/Ersetzen.

- `_titel(text, feld)`
- **class `PageSetupDialog`**(PanelFaehig, QDialog)
  - `__init__(page, parent)`
  - `result_page()`
  - `accept()`
- **class `HeaderFooterDialog`**(PanelFaehig, QDialog)
  - `__init__(title, hf, parent)`
  - `value()`
- **class `TableDialog`**(PanelFaehig, QDialog) — „Tabelle einfügen“ wie in der Vorlage: Tabellengröße, Einstellung für optimale Breite, Abmessungen für neue Tabellen speichern.
  - `__init__(parent, vorgabe)`
  - `spaltenbreite_px()` — Feste Breite jeder Spalte in Bildpunkten; None: automatisch (Seitenbreite).
- **class `BildGroesseDialog`**(PanelFaehig, QDialog)
  - `__init__(breite_px, hoehe_px, parent)`
  - `_b(v)`
  - `_h(v)`
  - `breite_px()`
  - `hoehe_px()`
- **class `ZoomDialog`**(PanelFaehig, QDialog) — Ansicht ▸ Zoom: feste Stufen, Seitenbreite, ganze Seite oder eigener Wert.
  - `__init__(parent, aktuell)`
  - `ergebnis()`
- **class `TabellenEigenschaftenDialog`**(PanelFaehig, QDialog) — „Tabelleneigenschaften“ (Reiter „Tabelle“ und „Spalte und Zelle“). Ändert die Tabelle nicht selbst; der Aufrufer liest ``werte()``
  - `__init__(parent, breite_prozent, ausrichtung, rand, abstand, kopfzeile, *, werte)`
  - `setze(w)`
  - `_sichtbar(*_)`
  - `werte()`
- **class `BildZuschneidenDialog`**(PanelFaehig, QDialog) — „Bild zuschneiden“: wie viele Bildpunkte links, oben, rechts und unten abgeschnitten werden.
  - `__init__(parent)`
  - `werte()` — (links, oben, rechts, unten) in Bildpunkten.

### `oberflaeche/dialoge/oberflaeche_dialoge.py`

Oberfläche anpassen: Register (Reiter) auswählen und ordnen, Schnellzugriff, Symbole austauschen, Oberfläche wählen.

- `lade_json(settings, key, standard)`
- `_satz(text, gedaempft)` — Erklärung über den Feldern: bricht um.
- **class `RegisterAnpassenDialog`**(PanelFaehig, QDialog) — Reiter ein-/ausblenden und umordnen — wie „Menüband anpassen“.
  - `__init__(parent, settings, daten)`
  - `_schieben(d)`
  - `_speichern()`
- **class `SchnellzugriffDialog`**(PanelFaehig, QDialog) — Welche Knöpfe in der Schnellzugriffsleiste neben dem ☰-Menü stehen.
  - `__init__(parent, settings, alle, aktuell)`
  - `_speichern()`
- **class `EigeneZeichnungDialog`**(PanelFaehig, QDialog) — „Eigene Zeichnung …“: eine SVG-Datei oder nur Pfaddaten hineinkopieren; die Vorschau zeichnet beim Tippen mit.
  - `__init__(parent)`
  - `_schau()`
  - `_ok()`
- **class `SymbolTauschenDialog`**(PanelFaehig, QDialog) — Ein Symbol austauschen — wie in der ersten Fassung: Getauscht wird die Zeichnung, nicht der Knopf; sie ändert sich überall,
  - `__init__(parent, settings, name)`
  - `_befehle()`
  - `_kopf_zeigen()`
  - `_gitter_zeigen()`
  - `_anwenden(meldung)`
  - `_waehle(katalogname)`
  - `_eigene()`
  - `_dieses_zurueck()`
  - `_alle_zurueck()`
  - `reject()` — Abbrechen (auch Esc und ✕) nimmt zurück, was in diesem Fenster getauscht wurde.
- **class `OberflaecheDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, settings)`
  - `wahl()`

### `oberflaeche/dialoge/optionen.py`

Optionen — das Fenster hinter „☰ Menü ▸ Optionen“ (F9): sechs Seiten in einer flachen Liste, oben eine Suche.

- `stil()` — Stylesheet beim Aufruf formatiert, damit das Thema gilt.
- **class `OptionenAnsicht`**(LesenSeiten, AnsichtSeiten, DateiSeiten, BefehleSeiten, LunivoSeiten, NameKiSeiten, QWidget) — Alle Optionen als Ansicht (Liste und Suche links, Seite rechts) — sie steht in der Datei-Ansicht („☰ Menü ▸ Erweiterte
  - `__init__(fenster, seite)`
  - `eventFilter(obj, ev)`
  - `_erklaere(name)`
  - `gehe_zu(key)` — Eine Seite zeigen; frühere Seitennamen führen auf die neue Seite und klappen dort den passenden Bereich auf.
  - `_index_bauen()`
  - `_suchen(q)`
  - `_springe(it)`
  - `_band_merken()` — Die Änderung steht in den Einstellungen; das Band wird beim Verlassen der Seite neu gebaut (nicht bei jedem Klick).
  - `_band_jetzt(*_a)`
  - `hideEvent(ev)`
- **class `OptionenDialog`**(QDialog) — Die Optionen als eigenes Fenster (für Aufrufe außerhalb der Datei-Ansicht); gleicher Inhalt wie `OptionenAnsicht`.
  - `__init__(fenster, seite)`

### `oberflaeche/dialoge/ueberpruefen_fenster.py`

Fenster des Reiters „Überprüfen“ nach Kays Vorlagen (ueberpruefen/02, 10).

- **class `WoerterDialog`**(PanelFaehig, QDialog) — „Wörter zählen“: die Statistiken untereinander, Werte rechtsbündig; der Haken nimmt Fuß- und Endnoten dazu.
  - `__init__(parent, ohne, mit)`
  - `_zeigen(*_)`
- **class `SchutzDialog`**(PanelFaehig, QDialog) — „Bearbeitung einschränken“ in der Seitenleiste: Dokumentschutz einstellen und „Schutz starten …“; steht ein Schutz,
  - `__init__(parent, art)`
  - `_zustand(*_)`
  - `ergebnis()` — Die gewählte Art des Schutzes; None: kein Schutz (auch nach „Schutz beenden“).

### `oberflaeche/dialoge/vorlagen_dialog.py`

Neu aus Vorlage: die mitgelieferten Gerüste und die Dateien aus dem Vorlagenordner.

- **class `VorlagenDialog`**(QDialog)
  - `__init__(parent, settings, kann_speichern)`
  - `_fuellen()`
  - `_ordner_waehlen()`
  - `_ordner_oeffnen()`
  - `_als_vorlage()`
  - `_ok()`

## `oberflaeche/dialoge/einfuegen`

### `oberflaeche/dialoge/einfuegen/__init__.py`

Unterpaket ``einfuegen`` von ``writer.dialoge``.


### `oberflaeche/dialoge/einfuegen/bildschirmfoto.py`

Bildschirmfoto: ganzer Bildschirm oder aufgezogener Bereich.

- **class `BereichWahl`**(QWidget) — Vollbild mit eingefrorenem Bildschirm; mit der Maus einen Bereich aufziehen (Esc bricht ab).
  - `__init__(bild)`
  - `paintEvent(ev)`
  - `_quelle(r)`
  - `mousePressEvent(e)`
  - `mouseMoveEvent(e)`
  - `mouseReleaseEvent(e)`
  - `keyPressEvent(e)`

### `oberflaeche/dialoge/einfuegen/diagramm_fenster.py`

„Diagramm einfügen“ nach Kays Vorlage (einfuegen/07 und Prüfkatalog): links die Diagrammarten mit eigenen Bildchen, oben die

- `art_symbol(sym, px)` — Diagrammart-Symbol aus dem zentralen Lucide-Katalog.
- **class `DiagrammDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, vorhanden)` — ``vorhanden``: Daten eines vorhandenen Diagramms (Diagrammart, Titel, Rubriken, Reihen, Kombination) — dann öffnet das Fenster damit.
  - `_kombi_tabelle()`
  - `_kombi_fuellen()` — Eine Zeile je Datenreihe; Werte aus ``self.kombi``.
  - `_kombi_geaendert(*_)`
  - `kompakt_machen()` — In der Seitenleiste: die Diagrammarten wie in der Vorlage in einer Spalte über der Vorschau (alle sichtbar, ohne Rollbalken),
  - `passe_an(breite, _hoehe)` — Auf die echte Breite der Seitenleiste: zwei Spalten Diagrammarten, Vorschau so breit wie der Platz.
  - `_gruppe(zeile)`
  - `_beispiel_laden(untertyp)`
  - `_vorlagen_hinweis()`
  - `_waehle(untertyp)`
  - `_daten()`
  - `_ist_kombi()`
  - `bild(breite, hoehe)`
  - `daten()`
  - `aktualisieren(*_)`

### `oberflaeche/dialoge/einfuegen/einfuegen_dialoge.py`

Dialoge zum Einfügen: Formen, WordArt, Diagramm, Piktogramm, Formel, Deckblatt, Datum, Textbausteine.

- `_ok(dlg)`
- **class `_Vorschau`**(QLabel) — Vorschaubild, das sich der Breite anpasst (in der Seitenleiste kleiner, nie breiter als 460 px).
  - `__init__()`
  - `setze(img)`
  - `_neu()`
  - `resizeEvent(ev)`
- **class `VorschauMixin`**
  - `_vorschau_bauen(layout)`
  - `_zeige(img)`
- **class `FormDialog`**(PanelFaehig, QDialog, VorschauMixin)
  - `__init__(parent, form)`
  - `bild()`
  - `daten()`
  - `aktualisieren(*_)`
- **class `_LayoutGalerie`**(QWidget) — Galerie der SmartArt-Layouts: Bildchen (selbst gezeichnet) in einem KachelFeld, die Spaltenzahl folgt der Breite.
  - `__init__(namen, zeichner, aktuell)`
  - `_bauen(spalten)`
  - `_klick(name)`
  - `setze(name)`
  - `aktuell()`
  - `resizeEvent(ev)`
- `_layout_bildchen(p, r, name)` — Graue Miniatur eines SmartArt-Layouts (selbst gezeichnet, ``oberflaeche/baukasten/dropdown/objektmenues/smartart_menues.py``).
- **class `SmartArtDialog`**(PanelFaehig, QDialog, VorschauMixin) — SmartArt auswählen (wie in der Vorlage „Grafik auswählen“): Galerie der Layouts, darunter Name, Beschreibung und Vorschau, OK.
  - `__init__(parent, daten)`
  - `layout_()`
  - `_layout(name)`
  - `daten()`
  - `aktualisieren(*_)`
- **class `WordArtDialog`**(PanelFaehig, QDialog, VorschauMixin)
  - `__init__(parent, text, stil, farbe, vorlage)` — ``vorlage``: Nummer eines Galerie-Stils (``E.WORDART_VORLAGEN``); ohne sie gelten ``stil`` und ``farbe``.
  - `vorlage_nr()`
  - `bild()`
  - `aktualisieren(*_)`
- **class `DiagrammDatenDialog`**(PanelFaehig, QDialog) — Titel und Daten des Diagramms (Unterfenster von „Diagramm einfügen“): erste Spalte Rubriken, weitere Spalten Datenreihen.
  - `__init__(parent, titel, kategorien, reihen)`
  - `_reihe_dazu()`
  - `daten()`
- **class `PiktogrammDialog`**(PanelFaehig, QDialog)
  - `__init__(parent)`
  - `_fuellen(q)`
  - `ergebnis()`
- **class `FormelDialog`**(PanelFaehig, QDialog)
  - `__init__(parent)`
  - `_zeige(*_)`
- **class `DeckblattDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, autor)`
- **class `DatumDialog`**(PanelFaehig, QDialog) — Wie die Vorlage: links „Verfügbare Formate“, rechts „Sprache“, darunter „Automatisch aktualisieren“ (dann als Datumsfeld).
  - `__init__(parent, sprache)`
  - `_loc()`
  - `_fuellen(*_)`
  - `ergebnis()`
  - `feldanweisung()` — Bei „Automatisch aktualisieren“ die Feldanweisung (DATE/TIME), sonst None.
- **class `BausteinDialog`**(PanelFaehig, QDialog) — Textbausteine: links die Liste (mitgelieferte und eigene), rechts die Vorschau; Name und Kürzel oben. „Aus Markierung …“ merkt den markierten Text
  - `__init__(parent, ed)`
  - `_fuellen(wahl)`
  - `_aktuell()`
  - `_zeigen()`
  - `_neu()`
  - `resizeEvent(ev)`
- **class `VorschauMixin`**
  - `_vorschau_bauen(layout)`
  - `_zeige(img)`
- **class `FormDialog`**(PanelFaehig, QDialog, VorschauMixin)
  - `__init__(parent, form)`
  - `bild()`
  - `daten()`
  - `aktualisieren(*_)`
- **class `_LayoutGalerie`**(QWidget) — Galerie der SmartArt-Layouts: Bildchen (selbst gezeichnet) in einem KachelFeld, die Spaltenzahl folgt der Breite.
  - `__init__(namen, zeichner, aktuell)`
  - `_bauen(spalten)`
  - `_klick(name)`
  - `setze(name)`
  - `aktuell()`
  - `resizeEvent(ev)`
- `_layout_bildchen(p, r, name)` — Graue Miniatur eines SmartArt-Layouts (selbst gezeichnet, ``oberflaeche/baukasten/dropdown/objektmenues/smartart_menues.py``).
- **class `SmartArtDialog`**(PanelFaehig, QDialog, VorschauMixin) — SmartArt auswählen (wie in der Vorlage „Grafik auswählen“): Galerie der Layouts, darunter Name, Beschreibung und Vorschau, OK.
  - `__init__(parent, daten)`
  - `layout_()`
  - `_layout(name)`
  - `daten()`
  - `aktualisieren(*_)`
- **class `WordArtDialog`**(PanelFaehig, QDialog, VorschauMixin)
  - `__init__(parent, text, stil, farbe, vorlage)` — ``vorlage``: Nummer eines Galerie-Stils (``E.WORDART_VORLAGEN``); ohne sie gelten ``stil`` und ``farbe``.
  - `vorlage_nr()`
  - `bild()`
  - `aktualisieren(*_)`
- **class `DiagrammDatenDialog`**(PanelFaehig, QDialog) — Titel und Daten des Diagramms (Unterfenster von „Diagramm einfügen“): erste Spalte Rubriken, weitere Spalten Datenreihen.
  - `__init__(parent, titel, kategorien, reihen)`
  - `_reihe_dazu()`
  - `daten()`
- **class `PiktogrammDialog`**(PanelFaehig, QDialog)
  - `__init__(parent)`
  - `_fuellen(q)`
  - `ergebnis()`
- **class `FormelDialog`**(PanelFaehig, QDialog)
  - `__init__(parent)`
  - `_zeige(*_)`
- **class `DeckblattDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, autor)`
- **class `DatumDialog`**(PanelFaehig, QDialog) — Wie die Vorlage: links „Verfügbare Formate“, rechts „Sprache“, darunter „Automatisch aktualisieren“ (dann als Datumsfeld).
  - `__init__(parent, sprache)`
  - `_loc()`
  - `_fuellen(*_)`
  - `ergebnis()`
  - `feldanweisung()` — Bei „Automatisch aktualisieren“ die Feldanweisung (DATE/TIME), sonst None.
- **class `BausteinDialog`**(PanelFaehig, QDialog) — Textbausteine: links die Liste (mitgelieferte und eigene), rechts die Vorschau; Name und Kürzel oben. „Aus Markierung …“ merkt den markierten Text
  - `__init__(parent, ed)`
  - `_fuellen(wahl)`
  - `_aktuell()`
  - `_zeigen()`
  - `_neu()`
  - `_weg()`
  - `_einfuegen()`

### `oberflaeche/dialoge/einfuegen/einfuegen_fenster.py`

Kleine Fenster des Reiters Einfügen nach den Vorlagen: „Zahl“, „Felder“, „Text in Tabelle umwandeln“, „Tabelle in Text konvertieren“.

- `_titel(text, feld)`
- **class `ZahlDialog`**(PanelFaehig, QDialog) — Feld „Zahl“, darunter die Liste „Zahlentyp“ (wie die Vorlage „Zahl“).
  - `__init__(parent)`
  - `ergebnis()` — Die Zahl im gewählten Typ; ``ValueError`` bei falscher Eingabe.
  - `_pruefen()`
- **class `FelderDialog`**(PanelFaehig, QDialog) — „Felder“ wie in der Vorlage: links „Feld auswählen“ mit den Feldnamen, rechts „Feldeigenschaften“ mit Feldfunktionen,
  - `__init__(parent, kontext)`
  - `kompakt_machen()` — In der Seitenleiste: die Feldnamen als Liste von begrenzter Höhe.
  - `_zeile(schl, text, w, aktiv)`
  - `_box(eintraege, bearbeitbar, daten)`
  - `_assistent_formel(name)`
  - `_assistent_adresse(name)`
  - `_assistent_zahlenformat(name)`
  - `_assistent_seitenverweis(name)`
  - `_assistent_seq(name)`
  - `_assistent_tc(name)`
  - `_assistent_datum(name)`
  - `_assistent_toc(name)`
  - `_assistent_variable(name)`
  - `_assistent_serienfeld(name)`
  - `_assistent_formatvorlage(name)`
  - `_zeigen(name)`
  - `_wert(schl)`
  - `_bauen(*_)` — Feldfunktion aus dem Assistenten (außer bei Formel, die man selbst schreibt).
  - `_formel_format(muster)`
  - `_formel_einsetzen(box)`
  - `_gueltig()`
  - `_pruefen(*_)`
  - `feld()` — (Feldanweisung, Ergebnis); mit „Formatierung beibehalten“ trägt die Anweisung ``\* MERGEFORMAT``.
- **class `AutoTextDialog`**(PanelFaehig, QDialog) — „AutoText erstellen“: Name für die Markierung (Vorschlag: ihre ersten Wörter).
  - `__init__(parent, markierung)`
  - `name()`
- **class `TrennerDialog`**(PanelFaehig, QDialog) — „Text in Tabelle umwandeln“ (mit Spaltenzahl) oder „Tabelle in Text konvertieren“: woran getrennt wird.
  - `__init__(parent, *, zu_tabelle, texte)`
  - `trenner()`
  - `spalten()`
  - `_zaehlen()`
- **class `SeitenzahlDialog`**(PanelFaehig, QDialog) — „Seitenzahl einfügen“ wie in der Vorlage: Format und Position, Kapitelnummer einbeziehen (Formatvorlage, Trennzeichen, Beispiele),
  - `__init__(parent, page)`
  - `_zustand(*_a)`
  - `werte()`
- **class `HyperlinkDialog`**(PanelFaehig, QDialog) — „Hyperlink“ wie in der Vorlage: links „Link zu“ (Datei oder Webseite, Aktuelles Dokument, E-Mail-Adresse), oben „Anzuzeigender Text“
  - `__init__(parent, *, text, ziele, ordner, adressen)`
  - `_ordner_setzen(pfad)`
  - `_ordner_zeigen(pfad)`
  - `_doppelklick(i)`
  - `_quickinfo()`
  - `art_waehlen(i)`
  - `_pruefen()`
  - `adresse_zu_href(adresse)` — Eingabe → Linkziel: Dateipfad → file://…, „www.…“ → https://…, sonst unverändert.
  - `ergebnis()`
- **class `ObjektDialog`**(PanelFaehig, QDialog) — „Objekt einfügen“ wie in der Vorlage. „Neu“ (ein eingebettetes Objekt eines anderen Programms anlegen) kann Lunivo nicht und bleibt grau;
  - `__init__(parent, *, als_symbol, ordner)`
  - `_suchen()`
  - `art()` — "symbol" \| "bild" \| "text" \| "" (keine Datei).
  - `_beschreiben()`

### `oberflaeche/dialoge/einfuegen/formular_dialog.py`

Dialog zum Anlegen eines Formularfelds (Textfeld, Auswahlliste, Datum, Kontrollkästchen, Schaltfläche).

- **class `FormFeldDialog`**(PanelFaehig, QDialog)
  - `__init__(fenster, art, bestehend)`
  - `_ok()`
  - `meta()`

### `oberflaeche/dialoge/einfuegen/smartart_dialog_foto.py`

SmartArt-Auswahl nach der Vorlage (Foto „Grafik auswählen“): Reiter „Alle“, große Kacheln, darunter Vorschau mit Name und Beschreibung, ein blauer OK-Knopf.

- `_weg(w)`
- **class `_GrosseGalerie`**(_LayoutGalerie) — Die Layout-Galerie mit Kacheln im Seitenverhältnis des Fotos.
  - `__init__(namen, zeichner, aktuell)`
  - `_bauen(spalten)`
  - `resizeEvent(ev)`
- **class `SmartArtDialogFoto`**(SmartArtDialog)
  - `__init__(parent, daten)`

### `oberflaeche/dialoge/einfuegen/sonderzeichen.py`

Das Fenster „Symbol“ (Einfügen › Symbol › Weitere Symbole …) in der Seitenleiste, nach der Vorlage mit drei Reitern:

- **class `SymbolDaten`** — Zuletzt verwendet, benutzerdefinierte Symbole (Zeichen, Haken) und Tastenkombinationen — in den Einstellungen (``get``/``set``).
  - `__init__(einstellungen, standard, anzahl)`
  - `_lesen(key, leer)`
  - `zuletzt()`
  - `merken(z)`
  - `benutzer()` — Die Liste „Benutzerdefinierte Symbole“ in ihrer Reihenfolge, je Zeichen mit Haken (``True``: in der Klappe zu sehen).
  - `setze_benutzer(liste)`
  - `sichtbar()`
  - `zuruecksetzen()`
  - `tasten()`
  - `setze_tasten(tasten)`
- **class `_Speicher`**
  - `__init__()`
  - `get(key, default)`
  - `set(key, wert)`
- **class `Zeichenraster`**(QWidget) — Zeichen in Zellen, die sich der Breite anpassen: Spaltenzahl = Breite / Zelle, Höhe folgt der Zahl der Zeilen (``heightForWidth``).
  - `__init__(parent)`
  - `setze(zeichen, schrift)`
  - `zeichen()`
  - `waehle(code)`
  - `spalten()`
  - `hasHeightForWidth()`
  - `heightForWidth(breite)`
  - `sizeHint()`
  - `minimumSizeHint()`
  - `zelle_von(i)`
  - `paintEvent(_ev)`
  - `_index_bei(pos)`
  - `mousePressEvent(ev)`
  - `mouseDoubleClickEvent(ev)`
  - `_setze_index(i)`
  - `keyPressEvent(ev)`
  - `focusInEvent(ev)`
  - `focusOutEvent(ev)`
- **class `_TastenFenster`**(PanelFaehig, TastenDialog) — „Tastenkombination“ als Seite über dem Fenster „Symbol“.
- **class `SonderzeichenDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, einfuegen, daten, *, bei_tasten)`
  - `_symbole()`
  - `_schrift_neu(*_)`
  - `_gewaehlt(cp)`
  - `_code_zeigen()`
  - `_code_getippt(text)`
  - `_sonderzeichen()`
  - `_benutzer()`
  - `_breiten()`
  - `resizeEvent(ev)`
  - `showEvent(ev)`
  - `_benutzer_fuellen(wahl)`
  - `_liste_aus_widget()`
  - `_liste_knoepfe()`
  - `_haken(*_)`
  - `_verschieben(schritt)`
  - `_entfernen()`
  - `_zuruecksetzen()`
  - `_taste_festlegen()`
  - `_tasten_melden()`
  - `zeichen_jetzt()` — Das Zeichen, das „Einfügen“ gerade einfügt: je nach Reiter aus Raster, Sonderzeichen oder benutzerdefinierter Liste.
  - `_reiter(i)`
  - `_knoepfe()`
  - `_einfuegen()`
  - `_zu_benutzer()`

### `oberflaeche/dialoge/einfuegen/wasserzeichen_fenster.py`

Fenster „Wasserzeichen“ nach der Vorlage: oben Bildwasserzeichen, darunter Textwasserzeichen, Transparenz, rechts die Vorschau

- `_titel(text, feld)`
- `_feld(w, breite)`
- `_lage_vorbelegen(fmt, hz, hm, vt, vm, a, winkel_vorgabe)` — Drehung, waagerechte und senkrechte Lage (Auswahl und mm) eines Bildes oder Textes aus den gespeicherten Angaben.
- **class `WasserzeichenDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, aktuell, page, ordner)`
  - `_lage_felder(g, kuerzel, partner)` — Format, Horizontal und Vertikal (je Liste und Abstand vom Rand).
  - `_vorbelegen(a)`
  - `_art(an, andere)`
  - `_bild_waehlen()`
  - `bild_laden(pfad)`
  - `_zustand(*_a)`
  - `_male(p, r)`
  - `ergebnis()` — Das eingestellte Wasserzeichen; None, wenn keine Art angekreuzt ist (oder kein Bild bzw. kein Text da ist).
  - `bereich()`

## `oberflaeche/dialoge/ki`

### `oberflaeche/dialoge/ki/__init__.py`

Unterpaket ``ki`` von ``writer.dialoge``.


### `oberflaeche/dialoge/ki/ki_aktions_dialoge.py`

KI-Aktionsfenster: Schnelle KI-Aktion, Neuer Assistent, Alle Ergebnisse (Erstellen-Fenster nach dem Baukasten).

- **class `SchnelleAktionDialog`**(ErstellenFenster) — „Schnelle KI-Aktion erstellen“: eine einmalige KI-Aufgabe mit Name, Anweisung, Ergebnisart und Zugriff.
  - `__init__(fenster)`
  - `vorlage_gewaehlt(i)`
  - `werte()`
- **class `KIAssistentDialog`**(ErstellenFenster) — „Neuen Assistenten erstellen“: ein KI-Assistent, der fortlaufend arbeitet und auf Änderungen im Dokument reagiert.
  - `__init__(fenster)`
  - `vorlage_gewaehlt(i)`
  - `werte()`
- **class `ErgebnisseDialog`**(PanelFaehig, QDialog) — „Alle Ergebnisse anzeigen“: die KI-Antworten dieser Sitzung; Kopieren oder an der Schreibmarke einfügen.
  - `__init__(fenster)`
  - `_zeigen(i)`
  - `_einfuegen()`

### `oberflaeche/dialoge/ki/ki_dialoge.py`

KI-Konfiguration: Aufgaben-Modellzuweisung, Liste der KI-Modelle, „Eigenen Anbieter hinzufügen“.

- **class `KIEinstellungenDialog`**(PanelFaehig, QDialog) — Das eine Fenster für alles zur KI: verbundene Modelle, Modellzuweisung, MCP-Server und Websuche.
  - `__init__(fenster, start)`
  - `kompakt_machen()` — In der Seitenleiste: kurze Reiternamen (die langen stehen im Tipp), damit alle fünf nebeneinander passen.
  - `freischalten()` — Alle Reiter sind immer anklickbar; Sprache, MCP und Websuche brauchen kein Modell, die Zuweisung zeigt ohne Modell eine leere Auswahl.
  - `neues_modell()`
  - `_ok()`

### `oberflaeche/dialoge/ki/ki_einstellungen_panels.py`

KI-Einstellungen, Seiten (Panels): Offline-Sprachen, Sprache, MCP-Werkzeuge, Datenschutz, Websuche, Dokumentensuche.

- **class `_NetzLauf`**(QRunnable) — Ein Netzaufruf der Sprachpakete im Hintergrund; das Ergebnis kommt als Signal zurück.
  - `__init__(sender, funktion, *args)`
  - `run()`
- **class `_NetzSender`**(QObject)
- **class `OfflineSprachen`**(QWidget) — „Offline-Sprachen“: installierte Richtungen der lokalen Übersetzung und das Nachladen weiterer Sprachpakete (nur auf Klick, im Hintergrund).
  - `__init__()`
  - `aktualisieren()`
  - `_sperren(an)`
  - `_verfuegbare_holen()`
  - `_herunterladen(von, nach, name, mb)`
  - `_ergebnis(erg)`
- **class `SprachePanel`**(QWidget) — Die Sprachen der Schreibhilfe, nebeneinander: „Sprache für die Überprüfung“ (Sprache des Dokuments) und „Übersetzen nach“ (Ziel der KI-Übersetzung).
  - `__init__(fenster)`
  - `kompakt_machen()` — Die zwei Listen stehen schon untereinander (je sechs sichtbare Zeilen, der Rest rollt); nichts mehr umzubauen.
  - `uebernehmen()`
- **class `McpDialog`**(QDialog) — Ein MCP-Server: Name, Startbefehl, ein/aus; „Testen“ startet ihn kurz und zeigt seine Werkzeuge.
  - `__init__(fenster, e)`
  - `_testen()`
  - `_ok()`
  - `werte()`
- **class `McpListe`**(QWidget) — Die eingetragenen MCP-Server: hinzufügen, bearbeiten, entfernen.
  - `__init__(fenster, konfig)`
  - `fuellen()`
  - `_aktuell()`
  - `_neu()`
  - `_bearbeiten()`
  - `_entfernen()`
- **class `EinwilligungenPanel`**(QWidget) — Wer darf welchen Text bekommen: die gespeicherten Einwilligungen, einzeln oder alle widerrufbar. Ohne Einwilligung wird nichts gesendet.
  - `__init__(konfig)`
  - `fuellen()`
  - `_knoepfe(*_)`
  - `_widerrufen()`
  - `_alle()`
- **class `WebsuchePanel`**(QWidget) — Websuche für den KI-Chat: Anbieter, Adresse oder Schlüssel, Zahl der Treffer. Ein: die Frage geht an den Suchanbieter.
  - `__init__(konfig)`
  - `werte()`
  - `_testen()`
  - `uebernehmen()`
- **class `DokumentePanel`**(QWidget)
  - `__init__(konfig)`
  - `ordner()`
  - `_stand_zeigen()`
  - `_neu()`
  - `_weg()`
  - `_indexieren()`
  - `_fertig(b)`
  - `_werkzeug_eintragen()`
  - `uebernehmen()`

### `oberflaeche/dialoge/ki/ki_modelle_dialoge.py`

KI-Konfiguration: Aufgaben-Modellzuweisung, Liste der KI-Modelle, „Eigenen Anbieter hinzufügen“.

- `_tags_text(a)`
- **class `_Antwort`**(QObject)
- **class `AnbieterDialog`**(QDialog) — Neuer oder zu bearbeitender Anbieter: Name, Vorlage, URL, Schlüssel, Modell (Liste vom Anbieter), Fähigkeiten.
  - `__init__(fenster, konfig, bestehend)`
  - `kompakt_machen()` — In der Seitenleiste: der Titel steht schon im Kopf der Seite; die Fähigkeiten laufen als Fluss in die Breite.
  - `_vorlage_gewaehlt(i)`
  - `_modell_abfrage_ungueltig(*_args)` — Antworten für eine alte URL oder einen alten Schlüssel dürfen die aktuelle Modellliste nicht überschreiben.
  - `_holen(still)`
  - `_geholt(r)`
  - `_ok()`
- **class `ModellListe`**(QWidget) — Die Liste der verbundenen KI-Modelle: hinzufügen, bearbeiten, entfernen (im Fenster „KI-Einstellungen“ und als eigenes Fenster).
  - `__init__(fenster, konfig)`
  - `_fuellen()`
  - `_aktuell()`
  - `_neu()`
  - `_bearbeiten()`
  - `_entfernen()`
- **class `ModellListeDialog`**(QDialog) — „Liste der KI-Modelle“ als eigenes Fenster (Optionen).
  - `__init__(fenster, konfig)`
- `modell_passt(m, aufgabe)` — Lokale Übersetzung („argos:“) und „Automatisch“ („auto:“) gelten nur für ihre Aufgabe (``verwendungFuer``); Bildgenerierung hat ihre eigene Regel.
- `modell_felder_fuellen(combo, konfig, aufgabe, gewaehlt, standard)` — Die eine Stelle, die ein Modell-Auswahlfeld füllt (Modellzuweisung, Optionen, Chat): Eintrag „Standard“, dann alle passenden Modelle; Signale ruhen dabei.
- `modell_combo(konfig, aufgabe, gewaehlt)` — Die Auswahl „welches Modell für diese Aufgabe?“ — dieselbe in der Modellzuweisung und in den erweiterten Einstellungen des Chats.
- **class `ModellZuweisung`**(QWidget) — Je Aufgabe ein Modell: Chatbot, Zusammenfassen, Übersetzung, Textanalyse, Bildgenerierung.
  - `__init__(fenster)`
  - `aufbauen()`
  - `uebernehmen()`
- **class `KIKonfigurationDialog`**(QDialog) — Die Modellzuweisung als eigenes Fenster (nur noch für Altaufrufe; im Alltag öffnet „KI-Einstellungen“).
  - `__init__(fenster)`
  - `_ok()`

## `oberflaeche/dialoge/lesen_hilfe`

### `oberflaeche/dialoge/lesen_hilfe/__init__.py`

Unterpaket ``lesen_hilfe`` von ``writer.dialoge``.


### `oberflaeche/dialoge/lesen_hilfe/hilfe_dialoge.py`

Hilfe: Handbuch, Tastenkürzel, Erweiterungen.

- `_browser(parent, titel, breite, hoehe)`
- **class `HilfeFenster`**(PanelFaehig, QDialog) — Hilfefenster (Handbuch, Tastenkürzel, Erweiterungen, Über): öffnet mit ``exec()`` in der Seitenleiste.
- **class `_Lesefeld`**(QTextBrowser) — Der Text des Handbuchs in einer ruhigen Spalte: nicht breiter als ~780 px, die Spalte steht in der Mitte (schmal: kleiner Rand).
  - `resizeEvent(e)`
- `_hb_bloecke(d, grund2)` — Absätze und Überschriften: Abstände, Zeilenhöhe, Merkkästen.
- `_hb_tastenchips(d, grund2)` — Tastenchips und Wege (Schrift mit fester Breite).
- `_hb_tabellen(d, linie)` — Tabellen: kein Gitter, nur feine Linien zwischen den Zeilen; leere Kopfzeile fällt weg.
- `_handbuch_gestalten(b)` — Gibt dem Markdown-Text die Gestalt der Vorlage: Antiqua mit Luft, Überschriften, Tabellen ohne Gitter, Merkkästen, Tastenchips.
- `handbuch(parent)` — Das Handbuch: oben die Gliederung (Gruppen, Abschnitte), darunter der Text. Er liegt als Markdown in ressourcen/handbuch.md.
- `_fuss(d, v)` — Knopfzeile unten („Schließen“); in der Seitenleiste bleibt sie angeheftet.
- `_titel(text)`
- `_dialog(parent, titel, breite)`
- `tastenkuerzel(parent)` — „Tastenkombinationen“: je Gruppe eine Überschrift, darunter zwei Kürzel mit Wirkung nebeneinander.
- `_erweiterungen_liste()`
- `erweiterungen(parent)` — „Erweiterungen“: jede Karte zeigt mit „DA“, ob der Teil schon geholt ist.
- `ueber(parent, version)`

### `oberflaeche/dialoge/lesen_hilfe/lesehilfe_dialog.py`

Lesehilfe: Papierton, Abstände, Zeilenfokus und Absatzfokus — wirkt nur auf die Anzeige, nicht auf das gespeicherte Dokument.

- **class `LesehilfeDialog`**(PanelFaehig, QDialog)
  - `__init__(fenster)`
  - `zeige(knopf)` — In der Seitenleiste öffnen (Standard); ohne Seitenleiste unter dem Knopf aufklappen.
  - `zeige_unter(knopf)` — Unter dem Knopf „Lesehilfe“ aufklappen (ohne ihn: wie ein gewöhnliches Fenster).
  - `anwenden()`
  - `reject()` — „Abbrechen“ stellt den Stand von vorher wieder her.

### `oberflaeche/dialoge/lesen_hilfe/silben_dialog.py`

Einstellungen für „Silben farbig“: alles, was jemand mit Legasthenie braucht, um es für sich passend zu machen.

- **class `SilbenDialog`**(PanelFaehig, QDialog)
  - `__init__(fenster)`
  - `_farbe_waehlen(i)`
  - `_knoepfe_faerben()`
  - `_zustand()`
  - `konfig()`
  - `anwenden()` — Wirkt sofort auf Vorschau und alle offenen Dokumente (Abbrechen stellt den alten Stand wieder her).
  - `_standard()`
  - `reject()`

### `oberflaeche/dialoge/lesen_hilfe/welche_hilfe.py`

„Welche Hilfe wann“: die Stufen der Schreibhilfe von der Wellenlinie bis zur KI, die Etiketten der Funde und ein Weg durch einen Brief.

- `_etiketten()`
- **class `_Umbruch`**(QLabel) — Text, der umbricht und dabei immer die Höhe bekommt, die er braucht (verschachtelte Layouts reichen „Höhe bei Breite“ nicht sicher weiter).
  - `resizeEvent(ev)`
- `_text(text)`
- **class `HilfeWannDialog`**(PanelFaehig, QDialog)
  - `__init__(fenster)`
  - `_mit_trenner(z, trenner)`
  - `_zeile(stufe, titel, kuerzel, frage, rechts, aktion, trenner)` — Stufenzeile in drei festen Spalten: Nummer \| Text (Titel, Frage, Hinweis) \| Schalter rechts, immer oben bündig.
  - `_nachziehen(name, an)`

## `oberflaeche/dialoge/optionen_seiten`

### `oberflaeche/dialoge/optionen_seiten/__init__.py`

Die Seiten des Optionen-Fensters, je Thema ein Baustein (``oberflaeche/dialoge/optionen.py`` setzt sie zusammen).


### `oberflaeche/dialoge/optionen_seiten/ansicht.py`

Optionen: Ansicht und Darstellung.

- **class `AnsichtSeiten`** — Optionen: Ansicht und Darstellung. Baustein von ``OptionenAnsicht`` (siehe ``vcl/qt/widgets/dialoge/optionen.py``).
  - `_ansicht(titel)`
  - `_aussehen(p)` — Hell, Dunkel, Mint oder wie das System: vier große Schaltflächen, genau eine ist gewählt (kein ausgegrauter Zusatzschalter).
  - `_oberflaeche_wahl(p, f)`
  - `_darstellung(p, f)` — Schrift größer/kleiner, Weicher Kontrast, Größe der Symbole, Schrift der Bedienung.

### `oberflaeche/dialoge/optionen_seiten/befehle.py`

Optionen: Menüband, Schnellzugriff, Sicherheit.

- **class `BefehleSeiten`** — Optionen: Menüband, Schnellzugriff, Sicherheit. Baustein von ``OptionenAnsicht`` (siehe ``vcl/qt/widgets/dialoge/optionen.py``).
  - `_zwei_listen(p, links_kopf, rechts_kopf, hinzu, weg, kategorie)` — Gerüst der Vorlage: links „Befehle auswählen“ (Auswahl, Suche, Liste), in der Mitte Hinzufügen/Entfernen, rechts die Liste
  - `_schieben(liste, d)`
  - `_menueband(titel)`
  - `_schnellzugriff(titel)`
  - `_sicherheit(titel)`
  - `_verfolgen(titel)`

### `oberflaeche/dialoge/optionen_seiten/datei.py`

Optionen: Schreiben, Speichern, Drucken und PDF.

- **class `DateiSeiten`** — Optionen: Schreiben, Speichern, Drucken und PDF. Baustein von ``OptionenAnsicht`` (siehe ``vcl/qt/widgets/dialoge/optionen.py``).
  - `_schreiben(titel)` — Schrift für neuen Text, Prüfung, AutoKorrektur; im Einzelnen eingeklappt (alle AutoKorrektur-Fälle bleiben erhalten).
  - `_speichern(titel)`
  - `_zwischenstaende_loeschen()`
  - `_sicherungskopien_oeffnen()`
  - `_daten_sichern()`
  - `_daten_zurueckholen()`
  - `_drucken(titel)` — Drucken und PDF auf einer Seite: das Häufige sichtbar, der Rest eingeklappt.

### `oberflaeche/dialoge/optionen_seiten/gemeinsam.py`

Gemeinsame Werte der Bausteine.

- `erklaerung(name)` — Der Satz zu einer Einstellung (aus ressourcen/daten/optionen_erklaerungen.json); leer, wenn es keinen gibt.
- **class `_Seite`**(QWidget) — Eine Optionenseite: Gruppen mit Zeilen; Werte stehen sofort in den Einstellungen.
  - `__init__(fenster, titel, offen)`
  - `gruppe(name)`
  - `mehr(name)` — Eingeklappter Bereich am Ende einer Seite; ``unter`` legt Gruppen hinein.
  - `unter(e, name)`
  - `haken(f, key, text, std, wirkt)`
  - `_zeile(f, c, text)` — Haken in die Gruppe setzen; gibt es einen Erklärsatz, steht er immer sichtbar darunter (nicht nur als QuickInfo).
  - `auswahl(f, key, label, werte, std, wirkt)`
  - `wahl(f, key, label, eintraege, std, wirkt)` — Auswahl mit Anzeigetext und gespeichertem Wert (Text oder Ja/Nein).
  - `schalter(f, text, ist, umschalten)` — Haken, der den Zustand eines anderen Teils des Programms zeigt und schaltet (Navigationsbereich, Gitternetzlinien …).
  - `eingabe(key, platzhalter)`
  - `felder(f, eintraege, spalten)` — Eingabefelder im Raster, jedes mit seinem Platzhalter als Beschriftung.
  - `pfad(f, key, text, platzhalter, wirkt)` — Ordner-Zeile: Beschriftung, darunter Feld und „Wählen …“.
  - `stufen(f, key, label, eintraege, std, wirkt)` — Auswahl aus benannten Stufen („normal“, „weit“ …), die als Zahl gespeichert werden.
  - `zahl(f, key, label, lo, hi, std, einheit, dezimal, wirkt)`
  - `zeile(f, text)`
  - `hinweis(text)`
  - `aktion(text, knopf, aktion, name)` — Zeile mit Text und Knopf in der Gruppe, die zuletzt begonnen wurde.
  - `haken_aus(f, text, grund, an)` — Ein Haken, den es in der ersten Fassung gab und der hier noch nichts bewirkt: grau, mit Grund.
  - `abschluss()`
- **class `_Karte`**(FormularGitter) — Zeilen einer Gruppe (ein ``FormularGitter``). Haken stehen wie in der ersten Fassung zu zweit nebeneinander, mit Linie zwischen den Zeilen;
  - `__init__(eltern)`
  - `addRow(*args)`
  - `aktion(text, knopf, aktion, name)` — Zeile aus Text und darunter einem Knopf („Den Text hören“ / „Stimme und Tempo …“).
  - `ende()` — Unterste Linie der letzten Haken-Zeile weg (die Karte hat selbst einen Rand); halbe Zeile mit Platz auffüllen.

### `oberflaeche/dialoge/optionen_seiten/lesen.py`

Optionen: Leichter lesen, Sprache.

- **class `LesenSeiten`** — Optionen: Leichter lesen, Sprache. Baustein von ``OptionenAnsicht`` (siehe ``vcl/qt/widgets/dialoge/optionen.py``).
  - `_lesehilfe(titel)`
  - `_silbentrennung_haken(p, f)` — Haken „Silbentrennung“: gilt für das Dokument, das gerade offen ist (derselbe Schalter wie im Reiter Schreibhilfe).
  - `_lese_schriften(p, e)` — Die drei Schriften zum leichteren Lesen mit Probe; sagt, ob sie da sind.
  - `_uebersetzung_oeffnen()`

### `oberflaeche/dialoge/optionen_seiten/lunivo.py`

Optionen: KI, Gedächtnis, Erweitert.

- **class `LunivoSeiten`** — Optionen: KI, Gedächtnis, Erweitert. Baustein von ``OptionenAnsicht`` (siehe ``vcl/qt/widgets/dialoge/optionen.py``).
  - `_ki(titel)`
  - `_gedaechtnis(titel)`
  - `_erweitert(titel)`

### `oberflaeche/dialoge/optionen_seiten/name_ki.py`

Optionen: Name und KI, dazu die Werkzeug-Fenster (Menüband, Schnellzugriff, Kennwort, Änderungen verfolgen).

- **class `NameKiSeiten`** — Optionen: Name und KI. Baustein von ``OptionenAnsicht`` (siehe ``vcl/qt/widgets/dialoge/optionen.py``).
  - `_name_ki(titel)`
  - `_anpassen(key)` — Eines der Werkzeuge als Fenster zeigen; das Band wird danach neu gebaut, wenn es sich geändert hat.

## `oberflaeche/dialoge/sendungen`

### `oberflaeche/dialoge/sendungen/__init__.py`

Unterpaket ``sendungen`` von ``writer.dialoge``.


### `oberflaeche/dialoge/sendungen/sendungen_dialoge.py`

Dialoge zu Sendungen: Umschlag, Etiketten, Seriendruck, Regeln, Vorschau.

- `_hinweis(text)`
- `_ok(dlg, text_ok)`
- **class `UmschlagDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, absender)`
- **class `EtikettenDialog`**(PanelFaehig, QDialog)
  - `__init__(parent)`
- **class `SeriendruckDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, felder, gespeichert)`
  - `_laden()`
- **class `RegelDialog`**(PanelFaehig, QDialog)
  - `__init__(parent)`

### `oberflaeche/dialoge/sendungen/serien_fenster.py`

Fenster des Reiters „Mailings“ (Seriendruck): Empfänger auswählen, Seriendruckfeld einfügen, übereinstimmende Felder festlegen.

- **class `EmpfaengerDialog`**(PanelFaehig, QDialog) — „Seriendruckempfänger“: alle Sätze der Datenquelle als Tabelle, je Zeile ein Haken; „Alle“ und „Keine“.
  - `__init__(parent, spalten, saetze, aktiv)`
  - `_alle(an)`
  - `ergebnis()`
- **class `FeldDialog`**(PanelFaehig, QDialog) — „Seriendruckfeld einfügen“: die Spalten der Datenquelle; ohne Datenquelle ein Name zum Eintippen. „Einfügen“ meldet
  - `__init__(parent, spalten)`
  - `_melden()`
- **class `ZuordnenDialog`**(PanelFaehig, QDialog) — „Übereinstimmende Felder festlegen“: zu jedem Feld im Text die Spalte der Datenquelle, aus der es seinen Wert bekommt.
  - `__init__(parent, felder, spalten, zuordnung)`
  - `ergebnis()`

## `oberflaeche/dialoge/verweise`

### `oberflaeche/dialoge/verweise/__init__.py`

Unterpaket ``verweise`` von ``writer.dialoge``.


### `oberflaeche/dialoge/verweise/verweise_dialoge.py`

Dialoge zu Verweisen: Textmarken, Quellen. (Beschriftung und Querverweis: ``verweise_fenster.py``.)

- `_knoepfe(dlg)`
- **class `TextmarkeDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, ed)`
  - `_fuellen()`
  - `_add()`
  - `_del()`
  - `_gehe()`
- **class `QuelleDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, q)`
  - `ergebnis()`
- **class `QuellenDialog`**(PanelFaehig, QDialog)
  - `__init__(parent, ed)`
  - `_fuellen()`
  - `_akt()`
  - `_neu()`
  - `_bearb()`
  - `_weg()`
  - `_zitat()`

### `oberflaeche/dialoge/verweise/verweise_fenster.py`

Fenster des Reiters Verweise nach den Vorlagen: „Inhaltsverzeichnis“, „Indexeintrag festlegen“, „Beschriftung“ (mit

- `_titel(text, feld)`
- **class `InhaltsverzeichnisDialog`**(PanelFaehig, QDialog) — Links Füllzeichen, Ebenen anzeigen, Seitenzahlen anzeigen/rechtsbündig, Hyperlinks verwenden; rechts die Seitenansicht.
  - `__init__(parent, opt)`
  - `kompakt_machen()` — In der Seitenleiste: die Seitenansicht unter den Einstellungen.
  - `ergebnis()`
  - `_auffrischen(*_)`
  - `_male(p, r)`
- **class `IndexeintragDialog`**(PanelFaehig, QDialog) — Haupt- und Untereintrag mit Sortierung, Optionen (Querverweis „Siehe“, aktuelle Seite, Seitenbereich über eine Textmarke),
  - `__init__(parent, vorschlag, marken, auswahl)`
  - `eintrag()`
  - `_melden(alle)`
  - `_auffrischen()`
- **class `NummerierungDialog`**(PanelFaehig, QDialog) — „Beschriftungsnummerierung“: Schreibweise der Nummer. Kapitelnummern kennt Lunivo noch nicht (grau).
  - `__init__(parent, zahl)`
  - `zahl()`
- **class `BeschriftungDialog`**(PanelFaehig, QDialog) — „Beschriftung“ wie die Vorlage: Feld mit „Tabelle 1“ zum Weiterschreiben, Bezeichnung, Position (nur bei markiertem Objekt),
  - `__init__(parent, eigene, naechste, objekt, label)`
  - `_vorspann()` — Den Anfang „Tabelle 1“ im Feld erneuern, Geschriebenes dahinter behalten.
  - `_neu()`
  - `_loeschen()`
  - `_nummerierung()`
  - `ergebnis()`
- **class `QuerverweisDialog`**(PanelFaehig, QDialog) — „Querverweis“ wie die Vorlage: Verweistyp, Verweisen auf, „Als Hyperlink einfügen“, „Oben/unten einschließen“, die Liste
  - `__init__(parent, ziele)`
  - `_art_gewaehlt(art)`
  - `_auffrischen()`
  - `ergebnis()`
  - `_melden()`

## `oberflaeche/dokument`

### `oberflaeche/dokument/__init__.py`

Dokumentbereich: Editor, Seitenfläche, Dokumentreiter, Lineal, Navigation.


## `oberflaeche/dokument/ansicht`

### `oberflaeche/dokument/ansicht/__init__.py`

Unterpaket ``ansicht`` von ``writer.dokumentansicht``.


### `oberflaeche/dokument/ansicht/absatz_symbol.py`

Absatz-Layout-Symbol: ein kleiner Knopf links neben dem Absatz der Schreibmarke (Absatzzeichen mit Pfeil). Sein Menü bietet

- `dunkel(symbol, px)` — Symbol in dunkler Tinte für die hellen Knöpfe auf dem Papier.
- **class `AbsatzSymbol`**(QObject)
  - `__init__(ed)`
  - `sichtbar_soll()`
  - `aktualisieren()`
  - `_zuruecksetzen()`
  - `_ausblenden()`

### `oberflaeche/dokument/ansicht/blasen_bedienung.py`

Sprechblasen im Seitenrand (Kommentare, verfolgte Änderungen) auf der Zeichenfläche: Lage, Zeichnen und Bedienung.

- **class `BlasenBedienung`**
  - `_blasen_init()`
  - `blasen_breite()`
  - `blasen_aktiv()`
  - `_blasen_schrift()`
  - `blasen_layout()` — [(Blase, Rechteck in der Ansicht, y der Textstelle)] aller Blasen, je Blatt gestapelt.
  - `blasen_zeichnen(p)`
  - `_blatt_kante(r, rechts)`
  - `blase_bei(pos)`
  - `blasen_maus_druecken(ev)`
  - `blasen_doppelklick(ev)`

### `oberflaeche/dokument/ansicht/dokument_ansicht.py`

Die Dokument-Zeichenfläche: zeigt ein ``Dokument`` über die neue Layout-Engine und den Dokument-Renderer, mit Schreibmarke, Auswahl, Maus, Tastatur,

- **class `DokumentAnsicht`**(EingabeTeil, ObjektBedienung, TabellenBedienung, BlasenBedienung, QWidget)
  - `__init__(sitzung, parent, engine)`
  - `ergebnis()` — Das Layout zum jetzigen Stand des Dokuments (bei Änderung neu berechnet).
  - `_modell_geaendert(_aenderung)`
  - `nach_aenderung()` — Nach einer Änderung über die Eingabe: Layout neu, Schreibmarke zeigen, Blinken zurücksetzen.
  - `nach_bewegung()`
  - `_markup_flaechen()` — Seitenindex → [(Art, Rechteck, Farbe)] für Kommentare (Hintergrund) und nachverfolgte Änderungen (unterstrichen/durchgestrichen), je Layout einmal.
  - `set_ansicht(**werte)` — Ansichtseinstellungen: ``textgrenzen``, ``gitter``, ``zeilenfokus``, ``papier`` (Farbe) sowie für das Layout ``buchstaben``, ``wort``,
  - `set_markup(an)`
  - `set_wellen(funde)`
  - `set_suchtreffer(treffer)`
  - `set_formatzeichen(absatz, leer)`
  - `setReadOnly(an)`
  - `isReadOnly()`
  - `seitenzahl()`
  - `set_zoom(faktor)`
  - `_blattmass(i)`
  - `set_seitenansicht(art)` — ``einzeln`` (Drucklayout), ``doppelt`` (zwei Seiten nebeneinander) oder ``web`` (eine endlose Seite in der Breite des Fensters).
  - `_web_breite()`
  - `_anordnung()` — (x, y, Breite, Höhe) jedes Blatts bei Zoom 1 im Blattraum: untereinander, bei zwei Seiten paarweise nebeneinander (x ab dem linken Rand des Blattraums).
  - `_groesse_setzen()`
  - `blatt(i)` — Das Blatt ``i`` in den Koordinaten der Ansicht (waagerecht in der Mitte).
  - `_naechstes_blatt(pos)`
  - `stelle(pos)` — Die Textstelle unter einem Punkt der Ansicht (auf dem nächstgelegenen Blatt).
  - `objekt_bei(pos)` — Das frei positionierte Objekt unter einem Punkt der Ansicht.
  - `cursor_flaeche()` — Die Schreibmarke in den Koordinaten der Ansicht.
  - `_sichtbar_machen()`
  - `paintEvent(ev)`
  - `_hilfen_zeichnen(b, erg, i, marke)` — Gitter, Textgrenzen und Zeilenfokus über dem Blatt.
  - `_blinken()`
  - `focusInEvent(ev)`
  - `focusOutEvent(ev)`

### `oberflaeche/dokument/ansicht/eingabe.py`

Eingabe der Dokument-Ansicht: Tastatur, Maus, Eingabemethoden und Zwischenablage. Jede Änderung geht über die Bearbeitungssitzung;

- **class `EingabeTeil`**
  - `_aendern(fn)` — Eine Änderung über die Sitzung ausführen; was die Sitzung ablehnt, lässt das Dokument unverändert.
  - `einfuegen(text)`
  - `entfernen(rueckwaerts, wort)` — Die Auswahl löschen, sonst das Zeichen (oder Wort) vor bzw. hinter der Schreibmarke.
  - `rueckgaengig()`
  - `wiederholen()`
  - `zeichenformat_umschalten(name)` — Ein Ja/Nein-Zeichenmerkmal (fett, kursiv, unterstrichen …) an der Auswahl umschalten; bei gemischter Auswahl gilt das Format am Anfang.
  - `kopieren()`
  - `ausschneiden()`
  - `einsetzen()`
  - `alles_auswaehlen()`
  - `_gehen(ziel, auswaehlen)`
  - `bewegen(art, auswaehlen)` — Die Schreibmarke bewegen (``schreibmarke.BEWEGUNGEN``); mit ``auswaehlen`` bleibt der Anker stehen.
  - `tabelle_weiter(rueckwaerts)` — Tabulator in einer Tabelle: zur nächsten (vorigen) Zelle; hinter der letzten entsteht eine neue Zeile. ``False`` außerhalb von Tabellen.
  - `keyPressEvent(ev)`
  - `inputMethodEvent(ev)`
  - `inputMethodQuery(frage)`
  - `focusNextPrevChild(_weiter)`
  - `mousePressEvent(ev)`
  - `_klick_ziel(ziel, ev)` — Klick auf das Zeichen einer Note (öffnet sie), auf ein Formularfeld oder Strg+Klick auf eine Verknüpfung (folgt ihr); ``True``, wenn der Klick
  - `contextMenuEvent(ev)` — Rechtsklick: Auswahl an die Stelle setzen (außerhalb der Auswahl) bzw. das Objekt wählen, dann das Menü anfordern.
  - `mouseMoveEvent(ev)`
  - `mouseReleaseEvent(ev)`
  - `mouseDoubleClickEvent(ev)`
  - `wheelEvent(ev)`

### `oberflaeche/dokument/ansicht/lineal.py`

Waagerechtes und senkrechtes Lineal am Rand des Dokumentfensters.

- **class `_Lineal`**(QWidget)
  - `__init__(tab)`
  - `_versatz()` — Wo der Editor (das Blatt) im Fenster steht — ändert sich beim Rollen.
  - `px(mm)`
  - `farben()`
  - `_schrift(p)`
- **class `LinealH`**(_Lineal)
  - `_einzuege()`
  - `_x0()` — x des linken Blattrandes im Lineal.
  - `_marken()` — Name → x-Position (Bildpunkte) der ziehbaren Marken.
  - `paintEvent(ev)`
  - `_treffer(x, y)`
  - `mouseMoveEvent(ev)`
  - `_mm(x, name)`
  - `mousePressEvent(ev)`
  - `mouseReleaseEvent(ev)`
- **class `LinealV`**(_Lineal)
  - `_blatt()` — Nummer des Blattes, in dem die Schreibmarke steht — das Lineal richtet sich nach diesem Blatt.
  - `_o()` — y des oberen Blattrandes des aktuellen Blattes im Lineal.
  - `paintEvent(ev)`
  - `_treffer(y)`
  - `mouseMoveEvent(ev)`
  - `mousePressEvent(ev)`
  - `mouseReleaseEvent(ev)`

### `oberflaeche/dokument/ansicht/objekt_bedienung.py`

Objekte auf dem Blatt bedienen: auswählen, verschieben, in der Größe ändern, drehen und die Schaltflächen neben dem Objekt.

- **class `ObjektBedienung`**
  - `_objekt_init()`
  - `sitzung_objekt_rechteck(objekt_id)` — (Seitenindex, Rechteck in Seitenkoordinaten) eines frei positionierten Objekts.
  - `_auswahl_objekt()` — (Art, Id, Seite, Rechteck) des gewählten Objekts; Art ``frei`` oder ``inline``; ``None``, wenn keines gewählt ist.
  - `_rahmen(sel)`
  - `_ansicht_punkt(seite, x, y)`
  - `_seiten_punkt(pos)` — Ein Punkt der Ansicht in den Koordinaten des nächsten Blattes.
  - `_griffe(r)`
  - `_griffe_ansicht(sel)`
  - `griff_bei(pos, sel)` — Der Griff („nw“ … „se“ oder „rot“) des gewählten Objekts unter dem Punkt der Ansicht, sonst ``None``.
  - `knopf_liste(sel)` — [(Name, Zeichen, Hinweis, Rechteck in der Ansicht)] der Schaltflächen neben dem gewählten Objekt.
  - `knopf_bei(pos, sel)`
  - `objekt_zeichnen(b, seite)` — Auswahlrahmen, Griffe und Drehgriff auf der Seite ``seite`` (Seitenkoordinaten, ``b`` ist auf das Blatt skaliert).
  - `knoepfe_zeichnen(p)` — Die Schaltflächen neben dem gewählten Objekt (in den Koordinaten der Ansicht).
  - `objekt_maus_druecken(ev)` — ``True``, wenn der Mausdruck ein Objekt, einen Griff oder eine Schaltfläche betraf.
  - `objekt_maus_bewegen(ev)`
  - `objekt_maus_loslassen(ev)`

### `oberflaeche/dokument/ansicht/tabellen_bedienung.py`

Tabellen auf dem Blatt bedienen: Griffe an der Tabelle, Spalten- und Zeilenränder ziehen, Tabelle zeichnen (Stift) und Linien löschen (Radiergummi).

- **class `TabellenBedienung`**
  - `_tabelle_init()`
  - `_zellplaetze(tid)` — [(Seite, Platz)] der Zellen der Tabelle (ohne wiederholte Kopfzeilen).
  - `_tabellen_rahmen(tid)` — (Seite, Rechteck der Tabelle in Seitenkoordinaten) auf der ersten Seite, auf der sie steht; sonst ``None``.
  - `_v(seite, x, y)`
  - `_ansicht_rect(seite, r)`
  - `tabellen_griffe()` — {Name: QRectF} der Griffe der Tabelle an der Schreibmarke in Koordinaten der Ansicht; leer ohne Tabelle.
  - `_spanne(zelle, breit)`
  - `_rand_bei(pos)` — (Art, Tabelle, Index) des Zellenrands unter dem Punkt der Ansicht; Art ``spalte`` oder ``zeile``; ``Index``: letzte Spalte links bzw. letzte Zeile
  - `tabellen_zeichnen(p)` — Griffe der Tabelle, die Vorschau beim Ziehen und die Stift-Vorschau (in Koordinaten der Ansicht).
  - `tabellen_maus_druecken(ev)`
  - `tabellen_maus_bewegen(ev)`
  - `tabellen_maus_loslassen(ev)`
  - `tabellen_modus_setzen(modus)` — ``"stift"``, ``"radierer"`` oder ``None`` (aus).
  - `_radieren(pos)` — Eine Zellenlinie unter dem Punkt löschen: die beiden Zellen daneben werden zu einer.

### `oberflaeche/dokument/ansicht/vorschau_ansicht.py`

Vorschau im Dokumentfenster: statt des Dokuments steht eine schreibgeschützte Zeichenfläche mit einer abgeleiteten Fassung da — der Brief eines

- `aktiv(tab, art)`
- `zeigen(tab, dokument, art)`
- `beenden(tab)`

## `oberflaeche/dokument/bearbeitung`

### `oberflaeche/dokument/bearbeitung/__init__.py`

Unterpaket ``bearbeitung`` von ``writer.dokumentansicht``.


### `oberflaeche/dokument/bearbeitung/freie_bilder_geometrie.py`

Maße und reine Geometrie der frei positionierten Bilder im Editor (Griffe, Rahmen, Anpassungsgriffe) — kein Zeichnen, keine Maus, kein Zustand.

- `griff_mitte(r, name)` — Mitte des Griffs ``name`` (acht Größengriffe oder ``rot``) am Rahmen ``r``.
- `abbilden(r, a, rr)` — Ein Rechteck in logischen Bildpunkten des Objekts (Breite ``b`` × Höhe ``h``) in Editor-Koordinaten (Zoom, Lage) umrechnen.
- `um_mitte_drehen(punkt, r, grad)` — Ein Punkt um die Mitte von ``r`` um ``grad`` Grad gedreht.
- `adj_lagen(r, a, vorlaeufig)` — Lage der Anpassungsgriffe (gelbe Raute) einer Form in Editor-Koordinaten: {"adj0": Punkt, …}; leer bei anderen Objekten.
- `drehwinkel(mitte, pos, raster)` — Der Winkel (Grad, 0 = oben) von der Mitte zur Maus; ``raster``: auf 15 Grad gerundet.
- `_kanten_verschieben(r, griff, dx, dy)`
- `groesse_rechteck(r, griff, dx, dy, frei)` — Das Rechteck ``r`` nach dem Ziehen am Griff ``griff`` um (``dx``, ``dy``); ohne ``frei`` bleibt das Seitenverhältnis erhalten.

### `oberflaeche/dokument/bearbeitung/freie_bilder_knoepfe.py`

Frei positionierte Bilder im Editor: die Schaltflächen neben dem gewählten Objekt und ihre Menüs — Layoutoptionen, Formstile, Füllung, Kontur,

- **class `FreieBilderKnoepfeMixin`**
  - `_frei_knopf(name, pos)`
  - `_frei_befehl_knopf(name, pos)` — Bild: Vergrößern (Ansicht mit Zoom) und Zuschneiden; Diagramm: Elemente, Stile, Einstellungen (Datenfenster) — jeweils der Befehl des Bandes.
  - `_frei_anker_menue(pos)` — Menü des Absatz-Symbols links vom Rahmen: Absatzformat zurücksetzen, Symbol ausblenden.
  - `_frei_anker_ausblenden()`
  - `_frei_absatz_zuruecksetzen()` — Der Absatz, an dem das Objekt hängt, bekommt Ausrichtung, Einzüge und Abstände zurück (das Objekt bleibt).
  - `_frei_wirken(**teile)`
  - `_frei_formstile(pos)`
  - `frei_formstile_menue(parent, ed)`
  - `_frei_formatierung(reiter)` — Zahnrad am Diagramm und Rechtsklick „Formatieren“: die Seitenleiste „Formatierung“ für das gewählte Objekt (Diagramm, SmartArt, Form, Bild …).
  - `_frei_effekte()` — „Weitere Effekte …“: die Seitenleiste „Formatierung“ mit den Effekten.
  - `_frei_fuell(pos)`
  - `frei_fuell_menue(parent, ed)`
  - `_frei_fuell_fenster(art)` — „Fülleffekte“, „Weitere Farbverläufe/Texturen/Muster“: die Seitenleiste „Formatierung“ auf „Füllung und Linie“ mit dieser Füllungsart.
  - `_frei_kontur(pos)`
  - `frei_kontur_menue(parent, ed)`
  - `_frei_linien_fenster()` — „Weitere Linien …“: die Seitenleiste „Formatierung“ auf dem Reiter „Füllung und Linie“ (Farbe, Breite, Strichart).
  - `bild_layout_popup(global_pos)`
  - `_frei_layout_popup(global_pos)`
  - `bild_layout_dialog()` — Das Fenster „Layout“ für das markierte Bild (frei oder im Text).

### `oberflaeche/dokument/bearbeitung/freie_bilder_knoten.py`

Frei positionierte Bilder im Editor: Teile eines Diagramms und Knoten eines SmartArt — Lage der Knoten, Teil bzw. Knoten per Klick wählen,

- **class `FreieBilderKnotenMixin`**
  - `_frei_sa_geo(a)` — Rechtecke der SmartArt-Knoten (logisch), zwischengemerkt, bis sich Knoten oder Größe ändern.
  - `_frei_knoten_rect(r)` — Der gewählte SmartArt-Knoten in Editor-Koordinaten (ohne Drehung) oder None.
  - `_frei_teil_klick(pos, a)` — Ein Klick in das markierte Diagramm wählt den Teil darunter, in das markierte SmartArt den Knoten darunter.
  - `_frei_teilwahl_aufheben()` — Vor dem Abwählen des Objekts: den gewählten Diagrammteil bzw. SmartArt-Knoten wieder abwählen.
  - `_frei_teil_tipp(e, pos, griff)` — Beim Überfahren des markierten Diagramms steht der Name des Teils unter der Maus im Tooltip.
  - `_frei_knoten_feld(kn, ident, text)` — Das Eingabefeld über dem Knoten ``ident``: Knotentext, dahinter (oder statt seiner, mit „Tippen ersetzt die Auswahl“) die getippten Zeichen.
  - `frei_knoten_edit_starten(text)` — Ein Eingabefeld über dem gewählten SmartArt-Knoten (Doppelklick, Enter oder Tippen). ``text``: bereits getippte Zeichen werden hinter den
  - `_frei_knoten_edit_ende(verwerfen)` — Das Eingabefeld schließen und den Text in den Knoten übernehmen (``verwerfen``: nicht übernehmen).

### `oberflaeche/dokument/bearbeitung/freiform_bedienung.py`

Punkte einer Form bearbeiten mit der Maus (Zeichentools ▸ Form bearbeiten ▸ Punkte bearbeiten); Rechnen in ``editor/objekte/freiform.py``.

- `aktiv(ed)`
- `starten(ed)` — Die gewählte Form in eine Freiform umwandeln (falls nötig; ein Schritt für Rückgängig) und den Modus einschalten.
- `beenden(ed)`
- `_eintrag(ed)`
- `_punkte(ed, a)`
- **class `_Abb`** — Anteil (0..1) im Zeichenrechteck der Form ↔ Bildschirm (Editorkoordinaten) für ein Objekt (Zoom, Lage, Drehung).
  - `__init__(a, r)`
  - `zu_schirm(x, y)`
  - `zu_anteil(pos)`
- `_punkt_bei(punkte, abb, pos)` — Index des Punkts (oder Steuerpunkts) unter der Maus; Punkte gehen vor Steuerpunkten.
- `zeichnen(ed, p, r, a)` — Punkte (Quadrate), Steuerpunkte (Kreise mit Haltelinie) und den gewählten Punkt (gefüllt) der Form.
- `_speichern(ed, punkte)`
- `_vorschau(ed, key, a, punkte)` — Das Bild der Form mit den vorläufigen Punkten neu zeichnen — ohne Dokumentschritt.
- `_maus_press(ed, e, punkte, abb, pos)`
- `_maus_move(ed, e, key, a, abb, pos)`
- `_maus_release(ed, a)`
- `_maus_doppel(ed, punkte, abb, pos)`
- `maus(ed, e, art)` — True, wenn das Ereignis zum Bearbeiten der Punkte gehört (art: press, move, release, doppel).
- `taste(ed, e)` — Esc beendet den Modus, Entf/Rücktaste löscht den gewählten Punkt (nie die ganze Form).

### `oberflaeche/dokument/bearbeitung/kern_befehle.py`

Bandbefehle des Editors für Absatz, Liste, Rahmen, Tabulator, Formatvorlage, Abschnitt, Verknüpfung und Ersetzen im Text.

- `spec_zu_ebenen(spec)` — Die 9 Ebenen einer Liste des Modells für die Beschreibung, die die Listenfenster liefern (einfache Liste oder Gliederung).
- `ebenen_zu_spec(ebenen)` — Das Gegenstück: die Beschreibung der Liste für die Listenfenster (einfach, wenn sie genau so entstanden sein kann, sonst Gliederung).
- `katalog_zu_vorlage(name, d)` — Eine Formatvorlage des Katalogs (``editor/text/stile.py``) als Vorlage des Dokumentmodells.
- `vorlage_zu_katalog(v)` — Die Felder einer Katalogvorlage (``stile.VORLAGE``), soweit das Modell sie führt — für das Fenster „Formatvorlage“.
- `_inline(zeile)` — Fett (**…**), kursiv (*…*), Code (`…`) aus einer Zeile: (reiner Text, [(von, bis, Zeichenformat)]).
- `markdown_bloecke(text)` — Einfaches Markdown (Überschriften, Aufzählungen, Nummerierungen, Fett, Kursiv, Code) als Absatzliste:
- **class `KernBefehle`** — Gemischt in ``KernEditor``: nutzt ``self.sitzung`` und ``self.ansicht`` des Editors.
  - `currentCharFormat()`
  - `set_outline(an)`
  - `ist_versteckt()`
  - `set_versteckt(an)`
  - `format_aufnehmen()` — Zeichen- und Absatzformat an der Schreibmarke für „Format übertragen“.
  - `format_uebertragen(probe)` — Das aufgenommene Format auf die Auswahl legen (Zeichen) — bei leerer Auswahl auf den Absatz.
  - `_merge(cf)` — Legt die Eigenschaften eines Qt-Zeichenformats (aus Dialogen und Menüs der Schriftart und Effekte) auf die Auswahl; was das Format nicht
  - `set_indents(links_mm, rechts_mm, erste_mm)`
  - `absatz_option(name)` — Eine Absatzoption (``editor/seite/absatzopt.py``) des Absatzes an der Schreibmarke.
  - `absatz_option_setzen(name, wert)`
  - `set_absatzopt(opt)`
  - `set_tabstopps(stopps)` — Tabstopps als Liste aus (Millimeter, Ausrichtung, Füllzeichen).
  - `standard_tab_mm()`
  - `set_standard_tab_mm(mm)`
  - `toggle_rtl()`
  - `absatzrahmen()`
  - `set_absatzrahmen(text)`
  - `absatzschatten()`
  - `set_absatzschatten(fuell, muster, musterfarbe)`
  - `liste_spec()` — Beschreibung der Liste am Absatz der Schreibmarke (für die Listenfenster), ``None`` ohne Liste.
  - `set_liste(spec)` — Wendet die Liste auf die Absätze der Auswahl an (``None``: Liste entfernen). Folgt sie unmittelbar auf eine gleiche Liste, zählt sie weiter.
  - `liste_neu_beginnen(start)`
  - `stil_aus_auswahl()` — Die Werte des Absatzes an der Schreibmarke als Vorgabe für „Neue Formatvorlage“.
  - `_vorlage_abgleichen(name)` — Legt die Vorlage des Katalogs im Dokument an oder aktualisiert sie, wenn sie dort anders steht.
  - `stil_neu_anwenden(name)` — Nach dem Ändern einer Vorlage im Katalog: das Dokument übernimmt die neue Definition.
  - `stil_entfernen(name)`
  - `stil_tasten()` — Tastenkombinationen der Formatvorlagen (``taste`` im Katalog) auf der Zeichenfläche setzen.
  - `apply_design(text_schrift, kopf_schrift, farbe)` — Dokumentdesign (Entwurf ▸ Design): Schrift des Fließtextes, Schrift und Farbe der Überschriften — über die Formatvorlagen des Dokuments.
  - `abschnitt_einfuegen(art)`
  - `abschnitt_entfernen()`
  - `abschnitt_gehe(n)`
  - `seite_letzter_block()` — Der letzte Absatz des Haupttextes (für Seiten, die am Ende des Dokuments eingefügt werden).
  - `insert_link(href, text, tipp)` — Verknüpfung auf die Auswahl; ohne Auswahl und mit ``text`` wird der Text eingefügt, sonst gilt sie für das Wort an der Schreibmarke.
  - `note_loeschen(art, note_id)`
  - `rohtext()` — Der Text des Dokuments mit U+2029 zwischen den Absätzen (Stellen wie bei ``textCursor().position()``).
  - `replace_range(von, bis, neu, erwartet, markdown)` — Ersetzt [von, bis) des Rohtextes durch ``neu``; mit ``erwartet`` nur, wenn dort noch dieser Text steht. ``markdown``: Auszeichnungen
  - `_markdown_ersetzen(von, bis, neu)`
  - `ersetze_verfolgt(von, bis, neu, autor)` — Wie ``replace_range``, aber als nachverfolgte Änderung des Bearbeiters ``autor``.
  - `_zellen_der_auswahl()` — (Tabelle, [(Zeile, Spalte)]) der Zellen der Auswahl (sonst der Zelle der Schreibmarke); ``None`` außerhalb einer Tabelle.
  - `_absaetze_der_zelle(zelle)`
  - `tabelle_rahmen_umschalten()`
  - `tabelle_rahmen_an()`
  - `tabelle_rahmen_linie(linie)` — Rahmen der Tabelle aus einer ``Linie`` (``None`` = ohne Rahmen).
  - `tabelle_rahmen_lesen()`
  - `zell_fuellung()`
  - `tabelle_optionen()` — Kopfzeile, Streifen, erste Spalte und Vorlage der Tabelle an der Schreibmarke.
  - `tabelle_vorlage_anwenden(name, kopf, streifen, spalte)` — Wendet eine Tabellenvorlage (Füllungen, Fettdruck, Rahmen) auf die Zellen an; die Optionen bleiben an der Tabelle gespeichert.
  - `tabelle_option_umschalten(schluessel)`
  - `zell_senkrecht(wo)`
  - `zell_waagrecht(ausrichtung)`
  - `zell_richtung(richtung)`
  - `tabelle_gitternetz_an()`
  - `tabelle_gitternetz()`
  - `zellmasse()` — (Breite, Höhe) der Zelle an der Schreibmarke in Bildpunkten, wie sie das Layout setzt; ``None`` außerhalb einer Tabelle.
  - `spalte_breite_setzen(mm)`
  - `zeile_hoehe_setzen(mm)`
  - `_spaltenbreiten_gemessen(t)` — Breiten aller Spalten: die gesetzten, sonst die vom Layout gemessenen.
  - `tabelle_anpassen(art)` — ``inhalt``, ``fenster``, ``spalten_gleich``, ``zeilen_gleich``, ``fest``.
  - `installEventFilter(filter_)` — Ereignisfilter (Minileiste) gehören an die Zeichenfläche, auf der Tasten und Maus ankommen.
  - `canPaste()`
  - `mini_zeigen(pos)` — Minileiste über der Auswahl (nach dem Auswählen mit der Maus).
  - `kontextmenue_zeigen(pos)` — Das Rechtsklickmenü an der Stelle zeigen (Text, Tabelle oder gewähltes Objekt); die Schreibhilfe ergänzt Vorschläge, die Minileiste steht daneben.
  - `verknuepfung_folgen(ziel)` — Strg+Klick auf eine Verknüpfung: ``#Name`` springt zur Textmarke, sonst öffnet das System die Adresse.
  - `tabellen_verbinden()` — Belegt die Rückrufe der Zeichenfläche für die Tabellenbedienung.
  - `tabelle_ganz_waehlen(tid)` — Wählt die ganze Tabelle (von der ersten bis zur letzten Zelle) und zeigt die Minileiste.
  - `tabelle_maus_aendern(art, tid, wert)`
  - `_zeilenhoehe_gemessen(tid, zeile)`
  - `tabelle_zeichnen_an(stelle, zeilen, spalten)` — Tabelle mit dem Stift gezeichnet: sie entsteht an der Stelle, an der das Ziehen begann.
  - `tabelle_zellen_vereinen(tid, a, b)` — Radiergummi: die Zellen ``a`` und ``b`` (Anker) werden zu einer Zelle verbunden, wenn sie ein Rechteck bilden.
  - `quellen()` — Die Literaturquellen des Dokuments (Kopie; ändern über ``quelle_hinzufuegen`` und ``quelle_entfernen``).
  - `zitierweise()`
  - `zitierweise(name)`
  - `quelle_hinzufuegen(q)`
  - `quelle_entfernen(tag)`
  - `seiten_von(offsets)` — Die angezeigten Seitenzahlen der Stellen im Rohtext (``"?"``, wenn eine Stelle nirgends steht).
  - `_formular_klick(pos)` — Klick auf ein Formularfeld (Kontrollkästchen, Auswahl, Datum, Text, Schaltfläche).
  - `abschnitt_seite(nr)` — Die Seiteneinrichtung des Abschnitts ``nr`` (ohne Angabe: an der Schreibmarke) als Kopie zum Ändern.
  - `abschnitt_seite_setzen(nr, seite)`
  - `abschnitte_anzahl()`
  - `abschnitt_beginn(nr)`
  - `abschnitt_beginn_setzen(nr, art)`
  - `seitenzahl_anwenden(w)` — Seitenzahl nach den Werten des Fensters: für das ganze Dokument, ab der aktuellen Seite (neuer Abschnitt) oder den aktuellen Abschnitt.
  - `seite_letzter_block()` — Der letzte Absatz des Haupttextes, der auf der Seite der Schreibmarke beginnt.
  - `leere_seite(quer)` — Ein neues, leeres Blatt hinter der Seite der Schreibmarke; der Text wird nicht geteilt. Hat das Blatt eine andere Ausrichtung als der
  - `note_text_setzen(art, note_id, text)` — Ändert den Text einer Fuß- oder Endnote (tippt das Feld „Noten“, ein Rückgängig-Schritt je Pause).
  - `_blatt(i)` — Lage des Blattes ``i`` in der Ansicht: ``x`` links, ``H`` Höhe, ``ml`` linker Rand und ``cw`` Textbreite (Bildpunkte der Ansicht).
  - `blatt_oben(i)`
  - `_blatt_bei_y(y)`
  - `cursorRect()`
  - `seitenzahl_zone(bereich, zone, ausr, muster, zahl)` — Seitenzahl in Kopf- oder Fußzeile (``zone``) für das Dokument, ab der aktuellen Seite (neuer Abschnitt) oder den aktuellen Abschnitt.
  - `gliederung_ebene(delta)` — Gliederungsansicht: Überschrift des Absatzes um ``delta`` Ebenen herauf- (−1) oder herabstufen (+1); Ebene 0 ist Fließtext.
  - `blasen_setzen(konfig, schrift)` — Einstellungen der Sprechblasen im Seitenrand (``sprechblasen.konfig_lesen``) übernehmen und neu setzen.
  - `_blase_aktion(art, kid, pos)`
  - `kommentar_bearbeiten(kid)` — Fragt den neuen Text des Kommentars und setzt ihn.
  - `tabelle_ohne_rahmen_waehlen()` — Markiert die nächste Tabelle ohne Rahmen hinter der Schreibmarke (am Ende geht es vorn weiter). → ``False``, wenn es keine gibt.
  - `aehnlich_formatiert()` — Alle Strecken (Stellen im Rohtext) mit derselben Zeichenformatierung wie das Zeichen an der Schreibmarke.
  - `naechstes_objekt_waehlen()` — Springt zum nächsten Objekt (im Text oder frei positioniert) hinter der Schreibmarke und wählt es (am Ende geht es vorn weiter).
- **class `_TabellenRef`** — Wie ``KernTabelle``, wenn die Tabelle nicht an der Schreibmarke steht (nur Id und Tabelle).
  - `__init__(tabelle)`

### `oberflaeche/dokument/bearbeitung/kern_editor.py`

Die Schnittstelle der Oberfläche zum Dokumentenkern: Der Editor des Dokument-Tabs.

- `_hex(farbe)` — ``QColor`` oder Farbtext als ``#rrggbb``; ungültig oder ``None``: ``None`` (Eigenschaft entfernen).
- **class `KernDokument`**(QObject) — Der Teil der Dokumentschnittstelle, den Fenster und Statusleiste abfragen (Änderungsstatus, Zeichenzahl, Signal bei Änderung).
  - `__init__(editor)`
  - `isModified()`
  - `setModified(an)`
  - `melde_status()` — Meldet ``modificationChanged``, wenn sich der Änderungsstatus seit der letzten Meldung geändert hat.
  - `revision()` — Zählt jede Änderung des Dokuments (auch Rückgängig und Wiederholen); gleiche Zahl heißt gleicher Inhalt.
  - `defaultFont()`
  - `toPlainText()`
  - `resource(_art, url)` — Das Bild einer Ressource (für die Bildfunktionen); ``None`` ohne eine solche.
  - `addResource(_art, url, bild)`
  - `blockCount()`
  - `characterCount()`
- **class `KernTabelle`** — Die Tabelle an der Schreibmarke: Id, Zeile und Spalte; Maße über Zeilen- und Spaltenzahl.
  - `__init__(tabelle, zeile, spalte)`
  - `rows()`
  - `columns()`
- **class `KernListe`** — Die Liste des Absatzes an der Schreibmarke; ``format().style()`` ist die Aufzählungs- oder Zahlenart als Qt-Wert.
  - `__init__(definition, ebene)`
  - `format()`
- **class `KernCursor`** — Ein Textzeiger mit den gebräuchlichen Aufrufen eines Qt-Textcursors, aber auf dem Dokumentmodell: Stellen sind Zeichenstellen im Rohtext
  - `__init__(editor)`
  - `_text()`
  - `_ende()`
  - `position()`
  - `anchor()`
  - `hasSelection()`
  - `selectionStart()`
  - `selectionEnd()`
  - `selectedText()`
  - `setPosition(pos, mode)`
  - `clearSelection()`
  - `atBlockEnd()`
  - `atBlockStart()`
  - `atStart()`
  - `atEnd()`
  - `_absatz_grenzen(pos)` — (Anfang, Ende) des Absatzes, in dem die Stelle liegt (Stellen im Rohtext).
  - `movePosition(op, mode, n)`
  - `select(art)`
  - `_uebernehmen()`
  - `insertText(text, _format)` — Fügt Text an dieser Stelle ein (eine Auswahl wird ersetzt); ein übergebenes Qt-Format bedeutet: ohne Zeichenformat des Umfelds.
  - `removeSelectedText()`
  - `beginEditBlock()`
  - `endEditBlock()`
  - `currentTable()` — Die Tabelle, in der die Schreibmarke steht (sonst ``None``).
  - `currentList()` — Die Liste des Absatzes an der Schreibmarke (sonst ``None``).
  - `charFormat()`
  - `blockFormat()`
- **class `KernEditor`**(KernBefehle, KernObjekte, FreieBilderKnoepfeMixin, FreieBilderKnotenMixin, QObject)
  - `__init__(dokument, parent)`
  - `_geaendert()`
  - `_bewegt()`
  - `_seite_melden()`
  - `document()`
  - `textCursor()`
  - `setTextCursor(c)` — Setzt Anker und Kopf der Auswahl auf die Stellen des Zeigers.
  - `widget()`
  - `setFocus()`
  - `viewport()`
  - `setReadOnly(an)`
  - `isReadOnly()`
  - `set_formatzeichen(absatz, leer)`
  - `__getattr__(name)`
  - `zoom()`
  - `set_zoom(faktor)`
  - `current_page()`
  - `page_count()`
  - `word_count()`
  - `tabelle_an_marke()` — ``KernTabelle`` der Tabelle, in der die Schreibmarke steht (sonst ``None``).
  - `liste_an_marke()`
  - `_recount()`
  - `_kf()`
  - `position_im_text(pos)` — Die Zeichenstelle im Gesamttext (Absätze durch je ein Zeichen getrennt).
  - `noten()`
  - `kommentare()`
  - `_absatz_an_marke()`
  - `_zeichen()` — Das wirksame Zeichenformat an der Schreibmarke (am Anfang einer Auswahl: das erste Zeichen).
  - `qt_zeichenformat()`
  - `qt_absatzformat()`
  - `alignment()`
  - `current_style()`
  - `_zf(aenderung)`
  - `toggle_bold(an)`
  - `toggle_italic(an)`
  - `toggle_underline(an)`
  - `toggle_strike(an)`
  - `set_script(art)`
  - `set_font_family(familie)`
  - `set_font_size(pt)`
  - `grow_font(delta)`
  - `set_text_color(farbe)`
  - `set_highlight(farbe)`
  - `set_capitalization(art)`
  - `set_letter_spacing(px)`
  - `clear_formatting()`
  - `change_case(art)` — Groß-/Kleinschreibung des markierten Textes ändern (``art``: „gross“, „klein“, „wortanfang“, „satzanfang“).
  - `_af(aenderung)`
  - `set_alignment(al)`
  - `change_indent(delta_mm)`
  - `_absatz_formatwert(name)`
  - `set_line_spacing(faktor)`
  - `set_line_height(art, wert)` — Zeilenabstand: ``faktor`` (Vielfaches), ``mindestens`` oder ``genau`` (Punkt).
  - `set_paragraph_spacing(davor_pt, danach_pt)`
  - `set_page_break_before(an)`
  - `apply_style(name)`
  - `toggle_list(art, stil)`
  - `list_level(schritte)`
  - `insert_table(zeilen, spalten)`
  - `insert_page_break()`
  - `insert_column_break()`
  - `insertPlainText(text)`
  - `undo()`
  - `redo()`
  - `cut()`
  - `copy()`
  - `paste()`
  - `selectAll()`
  - `toPlainText()`
  - `abschnitt_nr()`
  - `abschnitt_seite()` — Die Seiteneinrichtung des Abschnitts an der Schreibmarke (eine Kopie zum Ändern).
  - `page()`
  - `page_settings_changed(seite)`
  - `apply_page(seite)`
  - `set_zeilennummern(an, neu)`
  - `geruest_aufbauen(zeilen, benutzer, heute)` — Schreibt das Gerüst einer Dokumentvorlage in das (leere) Dokument: Absätze, Auszeichnungen und die Lücken « … » zum Ausfüllen.
  - `select_range(von, bis)` — Wählt die Stellen [von, bis) des Rohtextes (Absätze durch ein Zeichen getrennt) aus.
  - `ensureCursorVisible()`
  - `set_wellen(funde)` — Zeigt die Funde der Schreibhilfe als Wellenlinien unter dem Text.
  - `set_suchtreffer(treffer)` — Hebt die Fundstellen (Rohtext-Stellen) in der Zeichenfläche hervor; eine leere Liste nimmt sie weg.
  - `ersetze_roh(von, bis, neu, zeichen, absatz, vorlage)` — Ersetzt eine Fundstelle; die Schreibmarke steht danach hinter dem eingesetzten Text.
  - `alle_ersetzen_roh(auftrag, ersatz, von, bis, zeichen, absatz, vorlage, zwischenablage)`
  - `qt_zeichenformat_aus(fmt)` — Das Zeichenformat eines Textstücks (Wörterbuch) als Qt-Wert; Vorlagen und Grundschrift sind aufgelöst.
  - `qt_absatzformat_aus(absatz)` — Das wirksame Absatzformat eines Absatzes als Qt-Wert (für Dialoge, die Qt-Formate lesen).
  - `zeichenformat_aus_qt(cf)` — Die Eigenschaften eines Qt-Zeichenformats, die das Dokumentenmodell kennt, als Zeichenformat (Wörterbuch).
  - `absatzformat_aus_qt(bf)` — Die Eigenschaften eines Qt-Absatzformats, die das Dokumentenmodell kennt, als Absatzformat (Wörterbuch).
  - `_bereiche_offsets(trifft, wert)` — Die Bereiche, deren Format ``trifft``: Liste von {"von", "bis", "wert"} mit Stellen im Rohtext (Absätze durch ein Zeichen getrennt).
  - `_format_bei(pos)`
  - `_springe(bereiche, delta)` — Wählt den nächsten (``delta`` 1) oder vorigen (-1) Bereich hinter bzw. vor der Schreibmarke (mit Umlauf); ``None``, wenn es keinen gibt.
  - `_markup_vorgabe()`
  - `markup()`
  - `set_markup(an)`
  - `markup_filter_setzen(**werte)`
  - `verfolgen()`
  - `set_verfolgen(an)`
  - `vor_aenderung(s)` — Vor jeder Änderung: Bearbeiter und Zeit für nachverfolgte Änderungen und Kommentare setzen.
  - `kommentar_bereiche()`
  - `kommentar_neu(text)` — Kommentiert die Auswahl (ohne Auswahl das Wort an der Schreibmarke); gibt die Kommentar-Id zurück, ``None`` wenn es nicht geht.
  - `kommentar_text_setzen(kid, text)`
  - `kommentar_geloest(kid, geloest)`
  - `kommentar_loeschen(kid)`
  - `kommentare_alle_loeschen()`
  - `kommentar_springen(delta)`
  - `kommentar_am_cursor()`
  - `aenderungen()` — Die nachverfolgten Änderungen: {"von", "bis", "wert" ("ins"/"del"), "autor", "datum"}.
  - `aenderung_am_cursor()`
  - `aenderung_springen(delta)`
  - `aenderung_annehmen(b, annehmen)`
  - `alle_aenderungen(annehmen)`
  - `aenderung_sichtbar(b)` — Ob eine Änderung zum gewählten Markup gehört (Bearbeiter, Tag).
  - `angezeigte_aenderungen(annehmen)`
  - `noten_stellen()`
  - `note_neu(art, text)`
  - `note_springen(delta, art)`
  - `kopffuss()`
  - `felder_aktualisieren()` — Rechnet die Felder neu, deren Ergebnis das Dokument selbst bestimmt (Nummern der Beschriftungen).
  - `tabelle_aktion(art)` — Zeilen und Spalten einfügen und löschen, ganze Tabelle löschen — an der Zelle der Schreibmarke. ``False``, wenn keine Tabelle gewählt ist.
  - `zellen_im_bereich()` — (Tabelle, [(Zeile, Spalte)]) der Zellen, die die Auswahl überstreicht; ohne Auswahl die Zelle der Schreibmarke.
  - `zellen_verbinden()` — Verbindet die überstrichenen Zellen zu einer; ``False``, wenn nichts zu verbinden ist.
  - `zelle_teilen(spalten, zeilen)`
  - `tabelle_teilen()` — Teilt die Tabelle oberhalb der Zeile der Schreibmarke: Die Zeilen ab hier bilden eine neue Tabelle darunter.
  - `zellformat(aenderung)` — Wendet ein Zellformat auf die überstrichenen Zellen (sonst die der Schreibmarke) an.
  - `tabellenformat(aenderung)`
  - `_png(img)` — Die Bytes des Bildes fürs Dokument: ein Rasterbild aus einer Datei (JPEG, GIF …) bleibt im Original, sonst PNG.
  - `objekt_frei_einfuegen(art, daten, breite, hoehe, bild, alt)` — Legt ein frei positioniertes Objekt am Absatz der Schreibmarke an (ein Bild als Darstellung) und wählt es aus; → Id des Objekts.
  - `insert_image(pfad)` — Fügt ein Bild aus einer Datei wie ein Zeichen in den Text ein, auf die Inhaltsbreite begrenzt.
  - `objekt_gewaehlt()` — Das gewählte frei positionierte Objekt (``FreiesObjekt``) oder ``None``.
  - `objekt_bild(objekt)` — Das Darstellungsbild eines Objekts (Ressource) als ``QImage``; ``None`` ohne Bilddaten.
  - `objekt_setzen(objekt_id, **felder)` — Ändert Felder eines frei positionierten Objekts (``daten``, ``breite``, ``hoehe``, ``bilddaten`` …) in einem Schritt.
  - `web()`
  - `set_web(an)`
  - `set_gliederung(an)` — Gliederungsansicht: nur die Überschriften des Dokuments.
  - `set_marken(an)`
  - `set_gitter(an)`
  - `set_zeilenfokus(an)`
  - `set_lesehilfe(papier, buchstaben, wort)` — Lesehilfe: Blattfarbe sowie zusätzlicher Buchstaben- und Wortabstand (Bildpunkte).
  - `set_zeilenluft(faktor)`
  - `set_versteckt_zeigen(an)`
  - `setAcceptDrops(an)`
  - `set_silbenfarben(k)` — Lesehilfe „Silbenfarben“ (Einstellungen aus ``editor/text/silbenfarben.konfig_lesen``): reine Anzeige, das Dokument bleibt unverändert.
  - `set_lesefokus(groesser, zurueck)` — Lesehilfe: Alles außer dem Absatz der Schreibmarke tritt zurück (``zurueck`` kleiner als 1 = blasser).
  - `objekt_verschieben(objekt_id, seite, rect)` — Setzt ein frei positioniertes Objekt an das Rechteck ``rect`` (Seitenkoordinaten der Seite ``seite``): Es hängt danach am Absatz, der dort
  - `objekt_ebene(wohin)` — Stapelreihenfolge des gewählten Objekts: ``vorn``, ``hinten``, ``vor``, ``zurueck``.
  - `objekt_loeschen()`
- **class `KopfFussBearbeiter`**(QObject) — Bearbeiter für Kopf- und Fußzeilen: bearbeitet wird im Fenster „Kopf- und Fußzeile“ (``edit_header_footer``), nicht direkt auf der Seite.
  - `__init__(editor)`
  - `starte(zone)`
  - `beende()`
  - `wechseln()`
  - `abschnitt_springen(delta)`

### `oberflaeche/dokument/bearbeitung/kern_objekte.py`

Objekte im Editor: Auswahl, Angaben und Ändern von Bildern, Formen, Textfeldern, Diagrammen und SmartArt — frei positioniert oder im Text.

- `angabe_von(o)` — Die Angabe eines frei positionierten Objekts (``FreiesObjekt``).
- `felder_aus_angabe(a)` — Die Felder des ``FreiesObjekt``, die eine (geänderte) Angabe beschreibt, für ``objekt_aendern``.
- **class `_BildFormat`** — Maße eines Bildes im Text (die Fenster fragen ``width()``, ``height()`` und ``name()``).
  - `__init__(o)`
  - `width()`
  - `height()`
  - `name()`
- **class `KernObjekte`** — Gemischt in ``KernEditor``.
  - `_frei_sel()`
  - `_frei_sel(wert)`
  - `inline_gewaehlt()` — Das Objekt im Text, das die Auswahl genau umfasst (ein Zeichen), sonst ``None``.
  - `objekt_ziel()` — Das Ziel der Bildbefehle: gewähltes freies Objekt oder gewähltes Objekt im Text; sonst ``None``.
  - `objekt_art()`
  - `bild_format()` — Maße des gewählten Bildes im Text (``None``, wenn die Auswahl kein solches Objekt ist).
  - `_bild_cursor()`
  - `_frei_liste()` — [(Schlüssel, Angabe, Bild, Rechteck in Koordinaten der Ansicht, hinten, Seite)] der frei positionierten Objekte in Dokumentreihenfolge.
  - `angabe_speichern(objekt_id, angabe)` — Schreibt die Angabe eines freien Objekts zurück (mit den Bildern, die ``addResource`` des Dokuments gesammelt hat) in einem Schritt.
  - `inline_aendern(objekt_id, **felder)` — Ändert ein Objekt im Text (Größe, Daten, Bild …); neue Bilder aus ``bild_ressource_neu`` kommen im selben Schritt ins Dokument.
  - `bild_setzen(width, height, alt, dekor)` — Größe, Alternativtext und „dekorativ“ des gewählten Bildes im Text.
  - `bild_im_text_einfuegen(img, alt, art, daten)` — Fügt ein Bild (Form, WordArt, Diagramm, Datei …) wie ein Zeichen an der Schreibmarke ein, auf die Inhaltsbreite begrenzt.
  - `inline_daten(art)` — Die Parameter des gewählten Objekts im Text (Kopie); mit ``art`` nur, wenn es von dieser Art ist.
  - `inline_neu_zeichnen(img, daten, breite, hoehe, alt)` — Das gewählte Objekt im Text bekommt ein neues Bild und neue Parameter (Breite bleibt, Höhe folgt dem Seitenverhältnis, wenn nichts angegeben ist).
  - `inline_objekte_der_auswahl()` — Die Objekte im Text, wenn die Auswahl nur aus Objekten (und Leerraum) besteht; sonst ``None``.
  - `bild_ressource(name)` — Das Bild einer Ressource (auch eines, das noch nicht gespeichert ist) oder ``None``.
  - `bild_ressource_neu(img, name)` — Legt ein Bild für die nächste Angabe bereit; → sein Name (er gehört dann in ``n`` bzw. ``fuell['n']`` der Angabe).
  - `objekt_inline_rechteck(objekt_id)` — (Seite, Rechteck) eines Objekts im Text in Seitenkoordinaten oder ``None``.
  - `inline_bei(ziel, punkt)` — Id des Objekts im Text, das an der Stelle ``ziel`` getroffen ist (Klick auf das Zeichen), sonst ``None``.
  - `inline_waehlen(objekt_id)`
  - `objekt_drehen(grad)`
  - `objekt_spiegeln(waagerecht)`
  - `objekt_umbruch(art)` — Textumbruch des gewählten Objekts: ``textfluss`` (im Text), ``quadrat``, ``eng``, ``durch``, ``oben_unten``, ``hinter``, ``vor``.
  - `objekte_verbinden()` — Belegt die Rückrufe der Zeichenfläche (Auswahl, Ziehen, Drehen, Schaltflächen, Doppelklick) mit den Operationen des Editors.
  - `_frei_treffer()` — [(Schlüssel, Angabe, Rechteck in der Ansicht, hinten, Seite)] — wie ``_frei_liste`` ohne Bild (für Diagramm-, SmartArt- und Freiformbedienung).
  - `_frei_angabe()` — Die Angabe des gewählten freien Objekts oder ``None``.
  - `_frei_abbilden(r, a, rr)`
  - `window()`
  - `teil_klick(pos)` — Klick in das gewählte Diagramm oder SmartArt: wählt den Teil bzw. Knoten darunter.
  - `freiform_ereignis(art, ev)` — Maus im Punktebearbeitungsmodus der Freiform (Zeichentools ▸ Form bearbeiten); ``True``, wenn das Ereignis dazu gehört.
  - `freiform_taste(ev)`
  - `freiform_zeichnen(p)`
  - `objekt_gedreht(objekt_id, winkel)`
  - `inline_groesse(objekt_id, breite, hoehe)`
  - `objekt_art_von(art, objekt_id)`
  - `objekt_doppelklick(objekt_id)` — Doppelklick auf ein freies Objekt: Text in Form, Textfeld und WordArt bearbeiten, sonst das Layoutfenster.
  - `zuschnitt_lesen(objekt_id)` — Der Zuschnitt (links, oben, rechts, unten) als Anteile des freien Objekts.
  - `objekt_zuschneiden(objekt_id, seite, rect, zu)` — Zuschneiden-Modus: die Kanten sind gezogen; das Objekt bekommt den neuen sichtbaren Ausschnitt und seine Lage (ein Schritt).

## `oberflaeche/dokument/dokumentfenster`

### `oberflaeche/dokument/dokumentfenster/__init__.py`

Unterpaket ``dokumentfenster`` von ``writer.dokumentansicht``.


### `oberflaeche/dokument/dokumentfenster/dokument_bereich.py`

Ein geöffnetes Dokument: Zeichenfläche auf grauem Arbeitsgrund, Pfad, Meta, Wiederherstellungs-Kennung.

- **class `DocumentTab`**(QScrollArea)
  - `__init__(loaded, path, title, grundschrift)`
  - `set_layout(art)` — blatt/kern (Drucklayout) \| web (Weblayout, eine endlose Seite) \| doppelt (zwei Seiten nebeneinander).
  - `resizeEvent(ev)`
  - `_rand(seite, mm)`
  - `zeige_lineale(waagerecht, senkrecht)`
  - `_lineale_anordnen()` — Lineale in den Rand des Viewports legen; nur im Drucklayout.
  - `_lineale_neu_zeichnen(*_)`
  - `zoom_breite()` — Seitenbreite: die Seite füllt die Breite des Fensters.
  - `zoom_seite()` — Eine Seite: die ganze Seite ist sichtbar.
  - `page()`
  - `modell_fuer_speichern()` — Das Dokument des Tabs.
  - `is_modified()`
  - `set_path(path)`

### `oberflaeche/dokument/dokumentfenster/dokument_reiter.py`

Dokumentreiter ganz oben (mit „+“) und der Stapel der Dokumente darunter.

- **class `DocTabs`**(QObject) — Wie ein QTabWidget, nur dass Reiterleiste und Inhalt getrennt eingebaut werden.
  - `__init__()`
  - `eventFilter(obj, ev)`
  - `_moved(von, nach)`
  - `_bar_changed(i)`
  - `addTab(w, title)`
  - `count()`
  - `widget(i)`
  - `currentIndex()`
  - `currentWidget()`
  - `setCurrentIndex(i)`
  - `setCurrentWidget(w)`
  - `setTabText(i, t)`
  - `setTabIcon(i, icon)`
  - `tabText(i)`
  - `setTabToolTip(i, t)`
  - `removeTab(i)`

### `oberflaeche/dokument/dokumentfenster/navigation.py`

Die linke Seitenleiste: Suchen und ersetzen, Kommentare, Überschriften, Änderungen, Noten und Vorlesen — jedes als Feld mit Titel, Menü und ✕.

- `_datum(iso)`
- **class `KommentarKarte`**(QFrame) — Ein Kommentar: Verfasser, Datum, Text und Zeigen / Bearbeiten / Gelöst / Löschen; beim Bearbeiten steht der Text in einem Eingabefeld.
  - `__init__(b, k, ed, aktualisieren, pt, bearbeiten, speichern, abbrechen, bearbeite_los)`
- **class `NavigationPanel`**(QWidget)
  - `__init__(get_editor, fenster)`
  - `zeige_tab(key)`
  - `aktuelle_seite()`
  - `showEvent(e)`
  - `hideEvent(e)`
  - `spaeter()`
  - `aktualisieren()`
  - `anzahl(key)` — Wie viele Einträge ein Feld gerade zeigt (für Tests und die Zähler).
  - `_bau_suche()`
  - `zusatz_ausfuehren(d)` — Ein Zusatzfenster (Stimme und Tempo …) in dieser Leiste zeigen: dieselbe Schnittstelle wie die rechte Seitenleiste.
  - `unterfenster(d)` — Ein Unterfenster (Schriftart, Absatz … für „Format“) als Seite hier in der linken Leiste zeigen — die rechte Seitenleiste bleibt zu.
  - `suche_zeigen(text, reiter, element)` — Das Feld öffnen, die Markierung (oder ``text``) einsetzen und in das Suchfeld springen; ``reiter``: Suchen, Ersetzen oder Gehe zu.
  - `_zaehlen()`
  - `_weiter(rueckwaerts)`
  - `_ersetzen_eins()`
  - `_ersetzen_alle()`
  - `_bau_kommentare()`
  - `_kommentar_schrift(key)` — Schriftgröße der Kommentare: in den Karten hier und in den Blasen am Seitenrand.
  - `kommentar_bearbeiten(kid)` — Den Kommentar in seiner Karte bearbeiten (Doppelklick auf die Blase oder „Bearbeiten“).
  - `_bearbeiten_speichern(kid, text)`
  - `_bearbeiten_abbrechen()`
  - `_sortieren(key)`
  - `_anzeigen(key)`
  - `_neu_zeigen()`
  - `_neu_schliessen()`
  - `_neu_speichern()`
  - `_kommentare()`
  - `_bau_ueberschriften()`
  - `_einstellung(key, std)`
  - `_merke(key, wert)`
  - `_schrift(key, speichern)`
  - `_umbrechen(an, speichern)`
  - `_ebene(n)` — Alles bis zur Ebene ``n`` aufklappen, tiefere Ebenen zuklappen.
  - `_ueberschriften()`
  - `_klick(item, _col)`
  - `_kartenfeld(r, leer_text)` — Ein Feld mit Karten in einer Rolle (ohne seitliches Rollen) und einem Hinweis für den leeren Zustand. → (Layout, Hinweis)
  - `_bau_aenderungen()`
  - `_befehl(name)`
  - `_verfolgen_zeigen()`
  - `_bau_noten()`
  - `_karte(titel, text, farbe, kopf_rechts)`
  - `_aenderungen_und_noten()`
  - `_aend_aktion(name, daten)`
  - `_bau_vorlesen()`

### `oberflaeche/dokument/dokumentfenster/suchen_feld.py`

„Suchen und Ersetzen“ in der linken Seitenleiste — aufgebaut wie das Fenster der Vorlage, aber als Feld neben dem Text:

- `_gleich(a, b)`
- `_format_text(f)` — „Format: Fett, Schriftart: Arial, Hervorgehoben“ — was als Bedingung an einem Feld hängt.
- `_linie()`
- **class `FormatvorlageWahl`**(QDialog) — Eine Formatvorlage aus der Liste wählen (für „Format ▸ Formatvorlage …“ beim Suchen und Ersetzen).
  - `__init__(parent, aktuell)`
  - `name()`
- **class `SuchenFeld`**(QWidget) — Inhalt des Feldes „Suchen und ersetzen“. ``unterfenster(dialog) -> bool`` zeigt ein Unterfenster in der linken Leiste (wie ``exec``).
  - `__init__(get_editor, unterfenster)`
  - `_feld()`
  - `_knopf(text, menue)`
  - `_sprung(symbol, tipp)` — Pfeilknopf neben dem Suchfeld (vorheriger/nächster Treffer) — quadratisch, so hoch wie das Feld.
  - `_titel(text, feld)`
  - `_bau_suchen()` — Aufbau von oben nach unten: was man sucht (Feld, Pfeile, Trefferzahl), was man einsetzt (nur Reiter Ersetzen), dann zwei
  - `eventFilter(obj, e)`
  - `keyPressEvent(e)`
  - `_bau_gehe_zu()`
  - `_element_gewaehlt(t)`
  - `gehe(richtung)`
  - `zeige(reiter, element)` — Reiter „Suchen“, „Ersetzen“ oder „Gehe zu“ zeigen; bei „Gehe zu“ optional das Element (Seite, Abschnitt …) wählen.
  - `_reiter(i)`
  - `_optionen_neu()`
  - `_format_zeilen_neu()`
  - `auftrag()`
  - `_bedingungen(a, f)`
  - `_zeichen_bedingungen(a, f, ed)`
  - `_absatz_bedingungen(a, f, ed)`
  - `_ersatz_formate()` — Zeichenformat und Absatzformat (Wörterbücher des Dokumentenmodells) für „Ersetzen durch“ (aus „Format“ am Ersetzen-Feld).
  - `_bereich()`
  - `zaehlen()`
  - `weitersuchen(vorherige)` — „Weitersuchen“ (in der eingestellten Richtung) oder „Vorherige suchen“ (entgegen). Abwärts und Aufwärts halten am Ende an,
  - `_waehle(ed, t)`
  - `_merken(combo)`
  - `ersetzen_eins()`
  - `ersetzen_alle()`
  - `_hervorheben(an)`
  - `_suchen_in_fuellen()`
  - `_suchen_in(auswahl)` — Wie in der Vorlage: alle Treffer im gewählten Teil finden und zeigen; „Aktuelle Auswahl“ begrenzt auch die weitere Suche.
  - `_format_menue_fuellen()`
  - `_spezial_menue_fuellen()`
  - `_spezial(code)`
  - `_geaendert()`
  - `_format_schrift()`
  - `_format_absatz()`
  - `_format_tabs()`
  - `_format_stil()`
  - `_format_hervor()` — Wie in der Vorlage: erster Klick „Hervorgehoben“, zweiter „Nicht hervorgehoben“, dritter ohne Bedingung.
  - `_format_loeschen()`
- `_absatz_format(w)` — Die geänderten Absatzwerte als Absatzformat (für „Ersetzen durch“): nur, was im Fenster geändert wurde.

## `oberflaeche/dokument/kopffuss`

### `oberflaeche/dokument/kopffuss/__init__.py`

Unterpaket ``kopffuss`` von ``writer.dokumentansicht``.


### `oberflaeche/dokument/kopffuss/kopffuss_bearbeiter.py`

Kopf- und Fußzeile direkt auf der Seite bearbeiten (Einfügen ▸ Kopf- und Fußzeile, Doppelklick in den Seitenrand).

- `_schrift_aus_format(f)` — Schrift, Größe, Fett, Kursiv, Unterstrichen, Durchgestrichen, Hoch/Tief: was das Zeichenformat ausdrücklich setzt, als Schlüssel von ``HeaderFooter.fmt``.
- `_auszeichnung_aus_format(f)` — Farbe, Hervorhebung, Texteffekt und Kontur, die das Zeichenformat ausdrücklich setzt (None oder leer = ausdrücklich keine).
- `_fmt_zusammen(alt, neu, farbe_weg)` — Das Format der Zeile mit den neuen Werten; abgeschaltete Auszeichnungen (leer) stehen nicht mehr darin.
- **class `KopfFussBearbeiter`**(QObject)
  - `__init__(editor)`
  - `feld()` — Das Feld des aktiven Bereichs (``zone``); None, solange noch nie gestartet.
  - `_teile()`
  - `starte(zone, blatt)`
  - `beende()`
  - `wechseln()` — Zwischen Kopf- und Fußzeile springen: Schreibmarke ins andere Feld, die Leiste zieht mit.
  - `abschnitt_springen(schritt)` — Zur Kopfzeile des vorigen/nächsten Abschnitts; → False, wenn es keinen gibt.
  - `_fokus(zone)` — Klick/Schreibmarke in den anderen Bereich: die Leiste und das Absatz-Symbol ziehen dorthin.
  - `_cursor_blatt()`
  - `_art(page)` — "first", "even" oder "": welche Kopf-/Fußzeile das Blatt trägt (siehe ``PageSettings.kopf_fuss_art``).
  - `_name(page, zone)`
  - `_etikett(page, zone)`
  - `hf(page, zone)`
  - `_laden()` — Beide Felder (Kopf und Fuß) des aktuellen Blatts füllen.
  - `_leiste_laden(page)`
  - `_ausrichten(zone, align)`
  - `_geaendert()`
  - `speichern()` — Den Text des Feldes in die Seiteneinrichtung des Abschnitts schreiben (sofort; sonst nach kurzer Pause beim Tippen).
  - `aendern(aendere, neu_laden)` — ``aendere(page)`` auf die Einrichtung des aktuellen Abschnitts anwenden und speichern; → danach das Feld neu füllen.
  - `ausrichtung_setzen(align)`
  - `_stand()`
  - `_merken(vorher)`
  - `_text_gemerkt(zone)`
  - `_stand_setzen(stand)`
  - `_text_schritt(feld, rueck)` — Rückgängig/Wiederholen im Feld, bis sich der Text ändert (Schriftschritte, die Qt dazwischen merkt, zählen nicht).
  - `rueckgaengig()`
  - `wiederholen()`
  - `basis_format(fmt, zoom)` — Das Zeichenformat für ein Format aus ``HeaderFooter.fmt``; die Größe wird mit dem Zoom des Editors skaliert.
  - `_basis_anwenden(zone, hf)`
  - `format_anwenden(f, farbe_weg)` — Ein Zeichenformat der Start-Werkzeuge (Schrift, Größe, Fett, Kursiv, Unterstrichen, Farbe) auf die aktive Zeile anwenden.
  - `format_loeschen()` — „Formatierung löschen“: Schrift, Größe, F/K/U, Farbe und Effekte der aktiven Zeile zurück auf die Vorgabe (die Seitenzahl-Felder bleiben).
  - `format_lesen()` — Das Zeichenformat der aktiven Zeile (für die Schalterstellung der Start-Werkzeuge).
  - `ausrichtung_vom_werkzeug(al)`
  - `tabstopp_einfuegen()`
  - `_rect(zone)`
  - `_platzieren()`
  - `eventFilter(o, e)`
  - `_menues()`
  - `_menue_neu(m)`
  - `seitenzahl_einfuegen(ausr, muster, zahl, bereich)` — Seitenzahl in die Zeile setzen, die gerade bearbeitet wird („Seitenzahl einfügen ▾“); ``bereich``: dokument \| seite \| abschnitt.
  - `_start_setzen(n)`
  - `_menue_format(m)`
  - `_menue_loeschen(m)`
  - `seitenzahl_loeschen(art)` — Seitenzahl entfernen: "dokument" (alle Abschnitte), "abschnitt", "aktuelle", "auf", "von" (siehe ``seitenzahl_loeschen_bereich``).
  - `_hinweis(text)`

### `oberflaeche/dokument/kopffuss/kopffuss_felder.py`

Bausteine des Kopf-/Fußzeilen-Bearbeiters: Konstanten, Stile und die vier Qt-Elemente (Linie, Einfügen-Panel, Textfeld, Leiste).

- `_stil(vorlage)` — Stylesheet zur Laufzeit aus den Farbe-Tokens bilden (Farbe.* setzt apply_theme erst nach dem Import).
- `etikett_stil()`
- `panel_stil()`
- `_symbol(art)` — Aktionssymbol aus dem zentralen Lucide-Katalog.
- **class `_Linie`**(QWidget) — Gestrichelte graue Linie über die ganze Blattbreite, an der der Kopf-/Fußbereich endet.
  - `__init__(eltern)`
  - `paintEvent(e)`
- **class `_EinfuegenPanel`**(MenueListe) — Aufklappfeld „Seitenzahl einfügen“: Format, Position (fünf Kacheln mit Seitenbildchen), Übernehmen für, OK.
  - `__init__(eltern)`
  - `ort_setzen(ort)`
  - `_ok()`
- **class `_Feld`**(QPlainTextEdit) — Das Textfeld über dem Kopf- bzw. Fußbereich: randlos, gestrichelter Rahmen, Esc beendet.
  - `__init__(eltern, zone)`
  - `_feld_format(art)`
  - `felder_setzen(text, zahlen)` — Den Text mit {PAGE}/{PAGES} ins Feld schreiben; die Felder erscheinen als ``zahlen["PAGE"]`` bzw. ``zahlen["PAGES"]``.
  - `text_lesen()` — Der Text, in dem jedes Feld wieder als {PAGE}/{PAGES} steht.
  - `_feld_bei(pos)` — (Anfang, Ende) des Feldes, das die Zeichen vor/hinter ``pos`` berührt, sonst None — getrennt nach 'davor' und 'dahinter'.
  - `focusInEvent(e)`
  - `keyPressEvent(e)`
  - `_effekte_zeichnen(p)` — Schatten, Spiegelung, Leuchten usw. (``editor/text/textfx.py``) an der Stelle, an der das Feld den Text zeichnet. Das Feld setzt seine Blöcke
  - `paintEvent(e)`
- **class `_Leiste`**(QWidget) — Die schwebende Leiste neben dem Etikett des aktiven Bereichs: mit Seitenzahl drei Knöpfe, ohne nur „Seitenzahl einfügen“.
  - `__init__(eltern)`
  - `zahl_zeigen(mit)` — Mit Seitenzahl: drei Knöpfe; ohne: nur „Seitenzahl einfügen“ (beides linksbündig, direkt neben dem Etikett).
  - `natuerliche_breite()`

### `oberflaeche/dokument/kopffuss/noten_feld.py`

Notenfeld unten im Fenster: hier schreibt man den Text einer Fuß- oder Endnote, direkt nach dem Einfügen oder nach einem Klick auf das Zeichen im Text.

- **class `_Eingabe`**(QPlainTextEdit)
  - `keyPressEvent(e)`
- **class `NotenFeld`**(PanelRahmen) — ``get_editor``: liefert den aktuellen Editor. Zeigt sich mit `oeffnen(art, id)`, schließt mit ✕, Esc oder `zumachen()`.
  - `__init__(get_editor)`
  - `oeffnen(art, nid)`
  - `_getippt()`
  - `zumachen()`

## `oberflaeche/dokument/tabelle`

### `oberflaeche/dokument/tabelle/__init__.py`

Unterpaket ``tabelle`` von ``writer.dokumentansicht``.


## `oberflaeche/hauptfenster`

### `oberflaeche/hauptfenster/__init__.py`

Bausteine des Hauptfensters (``oberflaeche/programmfenster.py``), nach Aufgaben geteilt.


### `oberflaeche/hauptfenster/backstage_dokument.py`

Dokumentaktionen aus der Backstage-Ansicht.

- **class `BackstageDokumentBaustein`** — Umbenennen, Einfügen, Sperren und Kopf-/Fußzeilen eines Dokuments.
  - `rename_document()`
  - `toggle_sperre()` — Überprüfen ▸ Bearbeitung einschränken: Dokument schreibgeschützt (nur in dieser Sitzung).
  - `toggle_marks(on)`
  - `insert_table()`
  - `insert_image()`
  - `insert_link()`
  - `insert_date()`
  - `edit_header_footer(header)`
  - `kopffuss_starten(editor, header)` — Kopf- oder Fußzeile des Abschnitts an der Schreibmarke im Fenster „Kopf- und Fußzeile“ bearbeiten.
  - `_kopffuss_aus()`
  - `insert_page_number()`

### `oberflaeche/hauptfenster/backstage_fenster.py`

Weitere Fenster- und Seitenleistenaktionen der Backstage-Ansicht.

- **class `BackstageFensterBaustein`** — Baustein für Texteffekte und allgemeine Fensteraktionen.
  - `texteffekte_seitenleiste()` — Den Bereich „Texteffekte formatieren“ in der Seitenleiste öffnen; Änderungen gelten sofort für die Markierung.
  - `_effekt_sync()` — Folgt die Markierung einer anderen Formatierung, zeigt der offene Bereich „Texteffekte“ deren Werte.
  - `toggle_sidebar()`
  - `zum_band_springen()` — F10: aus dem Text zu den Reitern des Bandes (dann mit Tab und Pfeiltasten weiter), noch einmal F10: zurück in den Text.
  - `toggle_menubar()`
  - `find_dialog_show(reiter, element)` — Strg+F, Strg+H, Strg+G: „Suchen und ersetzen“ als Feld in der linken Seitenleiste (Reiter Suchen, Ersetzen oder Gehe zu).

### `oberflaeche/hauptfenster/backstage_navigation.py`

Navigation und Öffnen/Schließen der Backstage-Dateiansicht.

- **class `BackstageNavigationBaustein`** — Baustein für die Navigation der Backstage-Dateiansicht.
  - `_backstage_verbinden()`
  - `_menue_geklickt()` — ☰ Menü: öffnet die Datei-Ansicht, ein zweiter Klick schließt sie wieder.
  - `_ist_datei(i)`
  - `_reiter_gewechselt(i)`
  - `_reiter_angeklickt(i)`
  - `backstage_oeffnen(seite, unter)`
  - `backstage_zu()`
  - `backstage_schliessen()`
  - `show_main_menu()`

### `oberflaeche/hauptfenster/backstage_objektformat.py`

Objektformatierung in der Backstage-Seitenleiste.

- **class `BackstageObjektformatBaustein`** — Formatierungsseitenleisten für Bilder, SmartArt, Diagramme und weitere Objekte.
  - `_seitenleiste_oeffnen()` — Gemeinsam für alle Bereiche „Formatierung“: die Seitenleiste einblenden, falls sie zu ist.
  - `objektformat_seitenleiste(reiter, fuellung)` — Den Bereich „Formatierung“ für das markierte Bild in der Seitenleiste öffnen (Füllung und Linie, Effekte); Änderungen gelten sofort.
  - `formatierung_seitenleiste(reiter)` — Zahnrad am Diagramm und „Formatieren“ im Rechtsklick-Menü: die Seitenleiste „Formatierung“ passend zum gewählten Objekt.
  - `_smartart_werte(e)`
  - `smartartformat_seitenleiste()` — Seitenleiste „Formatierung“ für SmartArt (Rechtsklick): die Seitenleiste „Formatierung“ für den gewählten Knoten (ohne Auswahl: alle Knoten); Änderungen gelten sofort.
  - `smartartformat_folgen()` — Wählt der Benutzer einen anderen Knoten, zeigt der offene Bereich dessen Format.
  - `_diagramm_werte(e)` — Die Werte für die Seitenleiste „Formatierung“ des gewählten Diagrammteils (None ohne markiertes Diagramm).
  - `diagrammformat_seitenleiste()` — „Formatieren“ in den Diagrammtools: die Seitenleiste „Formatierung“ für den gewählten Diagrammteil öffnen; Änderungen gelten sofort.
  - `_format_folgen(schluessel, lesen)` — Gemeinsam für alle Bereiche „Formatierung“: ist er offen, zeigt er die Werte des neu gewählten Objekts (``lesen(editor)`` -> Werte oder None).
  - `diagrammformat_folgen()` — Wählt der Benutzer einen anderen Diagrammteil, zeigt der offene Bereich dessen Format.
  - `_objekt_text_verbinden()` — Die Textoptionen der Seitenleiste wirken auf den Text im gewählten WordArt oder Textfeld (``editor/objekte/frei_objekt.py``).
  - `_zeichen_masse(e)` — Höhe und Breite im Reiter Zeichentools (``bild_…``) und Bildtools (``bt_…``) mit dem markierten Bild abgleichen.
  - `_tabelle_masse(e)` — Zahlenfelder Höhe/Breite im Reiter Tabellentools (``tab_…``) mit der Zeile und Spalte der Schreibmarke abgleichen.
  - `objektformat_folgen()` — Wechsler der Seitenleiste „Formatierung“ bei neuer Auswahl: Ist ein Format-Bereich (Objekt, SmartArt, Diagramm) offen, zeigt der zur

### `oberflaeche/hauptfenster/backstage_seitenleisten.py`

Steuerung der linken und rechten Backstage-Seitenleisten.

- **class `BackstageSeitenleistenBaustein`** — Baustein für die linken und rechten Backstage-Seitenleisten.
  - `_leiste_links()` — Schmale Leiste links: Suchen, Kommentare, Überschriften, Änderungen, Noten, Vorlesen. Ein Klick öffnet das Feld, ein zweiter schließt es.
  - `leisten_beschriften()` — Option „Seitenleisten mit Text“: unter jedem Symbol der beiden Randleisten steht sein Name (breitere Leiste, kleinere Schrift).
  - `_links_klick(key)`
  - `_links_sync()`
  - `_leiste_rechts()` — Schmale Leiste rechts: Die vier Reiter der Schreibhilfe (Prüfen, Lesen, Schreiben, KI) und der KI-Chat schalten die Seitenleiste um.
  - `_rechts_klick(name)` — Ein Knopf der Leiste: öffnet die Seitenleiste auf dem Reiter; ein zweiter Klick auf denselben Reiter schließt sie wieder.
  - `_rechts_sync()`

### `oberflaeche/hauptfenster/backstage_steuerung.py`

Zusammensetzung der Backstage-Bausteine.

- **class `BackstageBaustein`**(BackstageObjektformatBaustein, BackstageDokumentBaustein, BackstageSeitenleistenBaustein, BackstageNavigationBaustein, BackstageFensterBaustein) — Datei-Ansicht (Backstage). Baustein von MainWindow.

### `oberflaeche/hauptfenster/bearbeiten.py`

Bearbeiten, Einfügen, Seite.

- **class `BearbeitenBaustein`** — Bearbeiten, Einfügen, Seite. Baustein von ``MainWindow`` (siehe ``lunivo_writer/oberflaeche/programmfenster.py``).
  - `paste_plain()`
  - `choose_color()`
  - `choose_highlight()`
  - `paragraph_dialog()`
  - `tabstopp_dialog()`
  - `_lesehilfe_auf(e)`
  - `mini_zeigen(ed, pos, rechtsklick, menue)`
  - `markup_neu()` — Markup- und Sprechblasen-Einstellungen haben sich geändert: Seitenrand für Blasen und Auszeichnung neu aufbauen.
  - `versteckt_anwenden(e)`
  - `silbenfarben_anwenden(e)`
  - `lineale_anwenden(tab)`
  - `formatzeichen_anwenden(e)` — Formatierungszeichen für Reiter: Absatzmarken und Leerzeichen/Tabstopps getrennt (Optionen ▸ Ansicht).
  - `marken_setzen(absatz, leer)` — Absatzmarken und/oder Leerzeichen und Tabstopps ein- oder ausschalten (None = unverändert).
  - `ansicht_optionen_anwenden()` — Statusleiste, QuickInfo, Bedienschrift, Symbolgröße — aus den Optionen.
  - `lesehilfe_anwenden()`
  - `set_marken(an)`
  - `chat_oeffnen(vorlage)`
  - `vorlesen(ab_hier)`
  - `stimme_waehlen()`
  - `_nav_aktion(name, b)`
  - `zeige_navigation(tab)`
  - `autor_angaben()`
  - `toggle_navigation()`
  - `toggle_lesemodus()`
  - `set_theme(wahl)`
  - `thema_ist_dunkel()`
  - `thema_wechseln()` — Schneller Zugang zu Hell und Dunkel (Strg+Umschalt+D, Statusleiste, Ansicht-Menü): wechselt zum jeweils anderen.
  - `thema_anzeigen()`
  - `_bereiche_bauen()`
  - `_chat_knopf_pruefen()` — Der schwebende KI-Chat-Knopf ist weg, solange der Chat in der Seitenleiste offen ist.
  - `ki_schnell_zeigen()` — Die Schnellen KI-Aktionen mit Zugriff „Schnellzugriff“ in der Schnellzugriffsleiste zeigen.
  - `_page_change(fn)`
  - `set_margins(top, bottom, left, right)`
  - `set_orientation(landscape)`
  - `set_paper(name)`
  - `page_setup()`

### `oberflaeche/hauptfenster/dateien.py`

Dateien, Vorlagen, Wiederherstellung.

- **class `DateienBaustein`**(DateienOeffnenBaustein, DateienVorlagenBaustein, DateienSpeichernBaustein, DateienExportBaustein, DateienDruckenBaustein, DateienReiterBaustein) — Dateien, Vorlagen, Wiederherstellung. Baustein von ``MainWindow`` (siehe ``lunivo_writer/oberflaeche/programmfenster.py``).

### `oberflaeche/hauptfenster/dateien_drucken.py`

Druckfunktionen des Hauptfensters.

- **class `DateienDruckenBaustein`**
  - `druck_start()` — Letzte Wahl im Druckfenster; Hintergrund, Grafik und Leerseiten teilen sich die Schalter mit den Optionen.
  - `druck_merken(e)`
  - `druck_vorschau(t)`
  - `_druck_args(t)`
  - `druck_ansicht(t, parent)` — Das Druckfenster ohne Knopfzeile (Menü ▸ Drucken, zweite Spalte).
  - `print_dialog()` — Drucken (Strg+P, Schnellzugriff, Druckvorschau): die Seite „Drucken“ im Menü, kein eigenes Fenster.
  - `druckfenster()` — Dasselbe als eigenes Fenster (für Aufrufer ohne Menü).
  - `druck_hilfe()`
  - `drucke_nach_wahl(t, e)` — Druckt das Blatt `t` nach der Wahl `e` (Druckfenster oder Menü ▸ Drucken).
  - `_drucker_eigenschaften(dlg, name)`
  - `print_preview()`
  - `ausgabe_ppi()` — Standard-Ausgabeziel: Auflösung für „Als Bild exportieren“.
  - `druckoptionen()`
  - `_blasen_fuer_druck()`
  - `_silben_fuer_druck()`
  - `_neuer_drucker()`
  - `_vor_dem_drucken(tab)` — „Felder vor dem Drucken aktualisieren“: Verzeichnisse neu rechnen.

### `oberflaeche/hauptfenster/dateien_export.py`

PDF- und Bildexport für das Hauptfenster.

- **class `DateienExportBaustein`** — PDF- und Bildexportfunktionen des Hauptfensters.
  - `pdf_wahl_start(t)` — Die Vorgaben für das PDF-Fenster und den PDF-Weg über „Speichern unter“ (Kennwörter werden nie gemerkt).
  - `export_pdf_dialog()` — Öffnet den PDF-Export als Seite in der zweiten Spalte des Datei-Menüs.
  - `pdf_export_widget()` — Baut die PDF-Exportseite des Datei-Menüs; alle Exportwahloptionen bleiben erhalten.
  - `bild_export_widget()` — Baut die Bildexportseite des Datei-Menüs; schreibt Bilder ohne ein separates Exportfenster.
  - `_pdf_schreiben(t, path, wahl)` — Schreibt die PDF. Ohne ``wahl`` (Weg über „Speichern unter“) gelten die gemerkten Exportoptionen, ganzes Dokument, ohne Kennwort.

### `oberflaeche/hauptfenster/dateien_oeffnen.py`

Öffnen und Anlegen von Dokumenten im Hauptfenster.

- **class `DateienOeffnenBaustein`** — Methoden zum Erstellen und Öffnen von Dokumenten.
  - `new_document()`
  - `_add_tab(tab)`
  - `open_dialog()`
  - `open_path(path)`
  - `_show_report(rep, title, when)`

### `oberflaeche/hauptfenster/dateien_reiter.py`

Reiterverwaltung und zusätzliche Tastenkürzel für das Hauptfenster.

- **class `DateienReiterBaustein`** — Kontextmenüs, Schließen von Dokumentreitern und Reiter-Tastenkürzel.
  - `reiter_menue(index, pos)` — Kontextmenü am Dokumentreiter.
  - `_reiter_schliessen(behalten, nur_andere)`
  - `close_tab(index)`
  - `_zusatz_kuerzel()` — Kürzel ohne eigene Aktion (Tabelle in windows/kuerzel.py zeigt sie in der Hilfe).
  - `_tab_weiter(d)`

### `oberflaeche/hauptfenster/dateien_speichern.py`

Speicherfunktionen für das Hauptfenster.

- **class `DateienSpeichernBaustein`** — Speichern und Exportieren von Dokumentdateien.
  - `save()`
  - `_save_tab(tab)`
  - `save_as()`
  - `save_as_format(ext)` — Speichern unter mit vorgewähltem Dateiformat (Untermenü „Speichern unter ▸“) — dasselbe Fenster wie „Speichern unter“.
  - `_ask_path(tab, title, only)` — Das eine Speichern-Fenster: Dateiname und Dateityp. `only` wählt den Dateityp vor, alle anderen bleiben wählbar.
  - `_save_tab_as(tab, only)`
  - `_darf_ueberschreiben(tab, path)` — Fragt nach, bevor eine Datei überschrieben wird, die außerhalb von Lunivo geändert wurde oder offen ist.
  - `_write(tab, path, mark_saved)`
  - `save_copy()`
  - `export_as(ext, title)`

### `oberflaeche/hauptfenster/dateien_vorlagen.py`

Vorlagen und Wiederherstellung des Hauptfensters.

- **class `DateienVorlagenBaustein`** — Methoden für Dokumentvorlagen und Wiederherstellung.
  - `benutzerdaten()`
  - `neu_aus_vorlage()` — Die Seite „Neu“ im Menü: alle Vorlagen als Blätter mit Vorschau.
  - `neu_aus_wahl(art, wert)` — Legt ein neues Dokument nach der Wahl auf der Seite „Neu“ an: leer, ein Gerüst oder eine Abschrift einer Vorlagendatei.
  - `als_vorlage_speichern(ordner)` — Legt das Blatt als Vorlage ab: im Vorlagenordner oder (``ordner``) in einer seiner Rubriken.
  - `autosave_now()`
  - `offer_recovery()`

### `oberflaeche/hauptfenster/dokument_sync.py`

Synchronisierung zwischen aktivem Dokument, Ribbon und Statusleiste.

- `_feld_setzen(feld, setter, wert)` — Setzt den Wert eines Feldes, ohne dessen Signale auszulösen.
- **class `DokumentSyncMixin`** — Hält UI-Felder und Statusanzeige mit dem aktiven Dokument synchron.
  - `_regler_bewegt(v)`
  - `_zoom_anzeigen(f)`
  - `_sync_later()`
  - `_sync_format()`
  - `_sync_kontexte(e)` — Schaltet die Kontext-Reiter nach dem gewählten Objekt. → Art des Textobjekts (WordArt, Textfeld) oder None.
  - `_sync_seitenmasse(f)` — Maßfelder im Reiter Seitenlayout.
  - `_sync_status()`

### `oberflaeche/hauptfenster/fenster_verwaltung.py`

Mehrere Hauptfenster: Liste, Neues Fenster, Anordnen, Fensterliste, Schließen.

- **class `FensterVerwaltungMixin`** — Baustein von ``MainWindow`` (siehe ``lunivo_writer/oberflaeche/programmfenster.py``).
  - `alle_fenster()`
  - `neues_fenster()` — Das aktuelle Dokument in einem zweiten Fenster öffnen (eigene Kopie, keine Synchronisation).
  - `fenster_anordnen(art)`
  - `fensterliste_menue()`
  - `closeEvent(ev)`

### `oberflaeche/hauptfenster/gemeinsam.py`

Gemeinsame Werte der Bausteine.

- **class `_QuickInfo`**(QObject) — Schluckt die Hinweistexte (QuickInfo) an Knöpfen und Feldern, wenn sie ausgeschaltet sind (Optionen ▸ Ansicht).
  - `__init__()`
  - `eventFilter(obj, ev)`

### `oberflaeche/hauptfenster/oberflaeche.py`

Oberfläche: Register oder Symbolleisten.

- **class `OberflaecheBaustein`** — Oberfläche: Register oder Symbolleisten. Baustein von ``MainWindow`` (siehe ``lunivo_writer/oberflaeche/programmfenster.py``).
  - `_symbole_anwenden()`
  - `_band_erzeugen()`
  - `oberflaeche_aendern(art, menueleiste)`
  - `neu_bauen_band()`
  - `_band_neu_bauen()`

### `oberflaeche/hauptfenster/reiter_zustand.py`

Aktives Dokument und Reiter des Hauptfensters: Zugriff, Titel, Umschalten, Verdrahtung neuer Reiter.

- **class `ReiterZustandMixin`** — Baustein von ``MainWindow`` (siehe ``lunivo_writer/oberflaeche/programmfenster.py``).
  - `current_tab()`
  - `current_editor()`
  - `_ed(fn)`
  - `_doc_tabs()`
  - `_tab_title(tab)`
  - `_update_tab_titles()`
  - `_update_window_title()`
  - `_tab_changed(_i)`
  - `_refresh_ui()`
  - `_connect_tab(tab)`
  - `_verbinde_felder()`
  - `stil_anwenden(name)`
  - `_size_chosen(*_)`

## `oberflaeche/kontext`

### `oberflaeche/kontext/__init__.py`

Kontextabhängige Reiter: Tabellen, Bilder/Formen, Kopf-/Fußzeile, Formulare.


### `oberflaeche/kontext/bild_werkzeuge.py`

Kontext-Reiter „Bildtools“ und „Zeichentools“ (für Formen im Text: ``form``; für freie Objekte inkl. WordArt/Textfeld: ``zeichen``).

- `_gruppieren_menue()` — Gruppieren ▾ wie in der Vorlage: beide Befehle im Menü (der Knopf selbst löst nichts aus).

### `oberflaeche/kontext/diagramm_werkzeuge.py`

Kontext-Reiter „Diagrammtools“ nach der Vorlage (erscheint bei markiertem Diagramm, Kontext ``diagramm``).


### `oberflaeche/kontext/kopf_fuss_werkzeuge.py`

Kontext-Reiter „Kopf- und Fußzeile“ nach der Vorlage: Gruppen ohne Namen, Klappen für Kopfzeile, Fußzeile, Seitenzahl,


### `oberflaeche/kontext/serien_werkzeuge.py`

Kontext-Reiter „Mailings“ (Seriendruck) nach der Vorlage: erscheint über Verweise ▸ Seriendruck und bleibt, bis


### `oberflaeche/kontext/tabellen_werkzeuge.py`

Kontext-Reiter „Tabellentools“ (erscheint, wenn die Schreibmarke in einer Tabelle steht).


### `oberflaeche/kontext/text_werkzeuge.py`

Kontext-Reiter „Texttools“ nach der Vorlage (erscheint bei markiertem WordArt oder Textfeld, zusammen mit „Zeichentools“).


## `oberflaeche/seitenleiste`

### `oberflaeche/seitenleiste/__init__.py`

Rechte Seitenleiste: Schreibhilfe und KI-Chat.


### `oberflaeche/seitenleiste/seitenleiste.py`

Die Schreibhilfe-Seitenleiste: Prüfen, Wellen/Vorhersage/AutoKorr, Funde, „Für wen?“, KI-Knöpfe.

- `werk_reiter_stil()` — Stylesheet beim Aufruf formatiert, damit das Thema gilt.
- **class `SchreibhilfePanel`**(QWidget)
  - `sizeHint()`
  - `__init__(assistent, parent)`
  - `verbinde_ki(dienst, fenster)`
  - `_schalter_nachziehen(name, an)`
  - `_thema_nachziehen(name)`
  - `ki_aktualisieren(laeuft)` — Ohne Modell steht oben auf dem Reiter KI der Weg dorthin; die Zeilen selbst bleiben bedienbar (ein Klick führt in die KI-Einstellungen).
  - `_werk_bauen()` — Die Reiter Lesen, Schreiben und KI aus dem Katalog; der Reiter Prüfen sind die Funde plus die Wege dahin.
  - `werkbank_aktualisieren()`
  - `aktueller_reiter()`
  - `zeige_reiter(name)` — Einen Reiter der Werkbank öffnen (und die Seitenleiste auf die Schreibhilfe stellen).
  - `_ollama_pruefen()`
  - `_ollama_da(modelle)`
  - `zeige_vorschlaege(lst)`
  - `_funde_zeigen()` — Ergebnisse (Hinweise, Vorschläge, Übersetzung) erscheinen auf dem Reiter Prüfen — die Seitenleiste wird dafür geöffnet und umgestellt.
  - `zeige_hinweis(titel, text, cent)`
  - `_karten_leeren()`
  - `_leer(text)`
  - `_format_zustand()`
  - `format_panel(schluessel)`
  - `_bereiche_menue(eltern, menue_text)` — Das Menü am Titel „Formatierung ▾“: die Bereiche der Seitenleiste wie in der Vorlage (der eigene Bereich trägt den Haken).
  - `_sicherungen_zeigen()` — Der Ordner mit den Sicherungskopien (derselbe wie in den Optionen).
  - `_formatierung_host(panel_klasse, menue_text, werte)` — Der gemeinsame Rahmen der Bereiche „Formatierung“: Kopf mit „Formatierung ▾“, Anheften und Schließen, darunter das Panel.
  - `zeige_format(schluessel, werte, **verbindungen)` — Den Bereich „Formatierung“ für ``schluessel`` zeigen. ``verbindungen``: Signalname des Panels -> Empfänger (``None`` wird übergangen).
  - `format_sichtbar(schluessel)`
  - `aktualisiere_format(schluessel, werte)` — Die Werte des Panels an die Markierung anpassen (wenn der Benutzer gerade nicht darin bedient).
  - `zeige_texteffekte(werte, anwenden)`
  - `texteffekte_sichtbar()`
  - `aktualisiere_texteffekte(werte)`
  - `zeige_objektformat(werte, anwenden, reiter, bild_wunsch)` — ``reiter``: 0 = Füllung und Linie, 1 = Effekte.
  - `zeige_bildalternativtext(werte, anwenden)` — Alternativtext und „Als dekorativ markieren“ des gewählten Bildes (``werte``: {"alt", "dekor"}); Änderungen gelten sofort.
  - `objektformat_sichtbar()`
  - `aktualisiere_objektformat(werte)`
  - `zeige_diagrammformat(werte, anwenden, alt_anwenden, bild_wunsch, teil_wunsch, dekor_anwenden)`
  - `diagrammformat_sichtbar()`
  - `aktualisiere_diagrammformat(werte)`
  - `zeige_smartartformat(werte, anwenden, bild_wunsch)`
  - `zusatz_ausfuehren(d)` — Ein Zusatzfenster als Seite hier in der Seitenleiste zeigen, solange man es bearbeitet (wie ``d.exec()``). Die Breite bleibt.
  - `zeige_bereich(i)` — 0 = Schreibhilfe, 1 = KI-Chat.
  - `setze_bereiche()` — Den KI-Bereich bauen: nur der Chat (Verlauf, Eingabe) — alles andere steht im Reiter Schreibhilfe und im Fenster „KI-Einstellungen“.
  - `zeige(funde)`
  - `_alle()`
  - `welche_hilfe()`

## `oberflaeche/seitenleiste/panels`

### `oberflaeche/seitenleiste/panels/__init__.py`

Bereiche der Seitenleiste.


### `oberflaeche/seitenleiste/panels/ki_panel.py`

KI-Chat in der Seitenleiste (Bereich „KI“): nur Verdrahtung — Zustand und Logik liegen im Dienst (``dienst.chat_modell``), die Bausteine in ``oberflaeche/baukasten/chat_*.py``.

- **class `ChatPanel`**(QWidget) — KI-Chat: Kopf (Neues Gespräch, Verlauf, KI-Einstellungen, Schließen), darunter je nach Phase Leerzustand mit Chips oder Nachrichten, Eingabekasten (mit Befehlen, Modell, Fußzeile). Ohne verbundenes Modell steht der Hinweis „KI-Modell verbinden“ mit dem Weg zu den KI-Einstellungen, die Eingabe ist gesperrt.
  - `__init__(dienst, fenster)`
  - `_geaendert()` — KI-Einstellungen oder Modell geändert: Modellfeld, Chips und Zustand neu lesen.
  - `_kontext()` — Markierung oder Dokumentinhalt haben sich geändert: Chips neu, Ersetzen-Knöpfe nachziehen.
  - `zustand()` — Verbunden ja/nein, Phase und Beschäftigung bestimmen, was sichtbar und bedienbar ist.
  - `anzeige()` — Nachrichten aus ``dienst.chat_modell`` neu aufbauen.
  - `_ki_blasen(i, n)` — Eine KI-Antwort als getrennte Blasen: Notiz, Einleitung, Dokumenttext, Erklärung, Fundstellen/Kürzung. Ohne Trennung genau eine Blase.
  - `_zum_ende_scrollen()` — Scrollt nach dem Neuaufbau nach unten, sofern das Panel noch existiert.
  - `_teil_label_format(teil)` — Streaming-Text wie die fertige Antwort: mit Struktur als Markdown (Qt, ``ki_markdown``), sonst einfacher Text — nie Markup.
  - `_teil_zeigen()` — Streaming: nur das Textfeld der laufenden Antwort nachziehen — kein Neuaufbau aller Blasen.
  - `_verlauf_fuellen()`
  - `_gespraech(index)`
  - `_neu()`
  - `_einstellungen()`
  - `_melden(text)`
  - `_senden(text)`
  - `_bild(text)`

### `oberflaeche/seitenleiste/panels/schreib_panel.py`

Bereich „Schreibhilfe“ der Seitenleiste: die Karten für Funde, Vorschläge und Hinweise.

- `kurz(text)` — Lange gleiche Zeichenfolgen (viele Leerzeichen hintereinander) kurz zeigen: „␣×34“ — sonst wird die Karte breiter als die Seitenleiste.
- `farbe_je_art()`
- `_marken()`
- `marke(art, quelle)`
- **class `FundKarte`**(QFrame)
  - `__init__(fund, assistent, parent, dienst)`
  - `_vorschlag_holen()`
  - `_vorschlag_da(v)`
  - `_annehmen()`
  - `_verwerfen()`
  - `_zeigen()`
  - `_hoeren()`
  - `mousePressEvent(e)`
- **class `VorschlagKarte`**(QFrame)
  - `__init__(v, dienst, panel)`
  - `_lassen()`
  - `_einsetzen()`
  - `_weg()`
- **class `HinweisKarte`**(QFrame) — Antworten, die den Text nicht ersetzen sollen (Zusammenfassung, Analyse).
  - `__init__(titel, text, cent, fenster, panel)`
  - `_kopieren()`
  - `_ende()`
  - `_weg()`

## `oberflaeche/statusleiste`

### `oberflaeche/statusleiste/__init__.py`

Statusleiste.


### `oberflaeche/statusleiste/statusleiste.py`

Statusleiste: Meldung, Wörter/Zeichen, Seite, Zoom (− Regler + Anzeige).

- **class `StatusBar`**(QStatusBar)
  - `__init__(parent)`
  - `thema_zeigen(dunkel)`
  - `meldung(text)`
  - `zaehler(woerter, zeichen)`
  - `seite(aktuell, gesamt)`
  - `zoom_zeigen(faktor)`

## `plattform`

### `plattform/__init__.py`

Alles, was vom Betriebssystem abhängt, an einer Stelle.


### `plattform/dateisystem.py`

Dateisystem-Besonderheiten der Betriebssysteme an einer Stelle (heute: wie eine Datei für ``fsync`` geöffnet werden muss).

- `fsync_oeffnen(path)` — Dateikennung für ``os.fsync``. Windows braucht dafür einen schreibenden Zugriff, Linux und macOS genügt Lesen.
- `ordner_oeffnen(ordner)` — Kennung eines Ordners zum ``fsync`` (sichert das Umbenennen); wirft OSError, wo das Betriebssystem es nicht kann (Windows).

### `plattform/pfade.py`

Orte für Programmdaten, Zwischenspeicher, nachgeladene Schriften/Stimmen und Vorlagen (über QStandardPaths).

- `_ort(art)`
- `data_dir()` — Programmdaten des Benutzers (gelernte Wörter, Sicherungen, KI-Einstellungen …); wird bei Bedarf angelegt.
- `cache_dir()` — Wiederherstellbares Zwischengelagertes.
- `schriften_dir()` — Nachgeladene Lese-Schriften (schrift-holen.sh); Linux: ~/.local/share/fonts/lunivo-office.
- `piper_dirs()` — Suchorte für Piper und seine Stimmen (stimme-holen.sh), der erste ist der aktuelle.
- `argos_dirs()` — Suchorte für Argos-Sprachpakete (.argosmodel): Benutzerordner zuerst, dann der mitgelieferte Ordner beim Programm.
- `argos_pakete_dir()` — Beschreibbarer Ort, an dem Argos die installierten Sprachpakete ablegt (der mitgelieferte Ordner ist schreibgeschützt).
- `vorlagen_dir()` — Vorgabeordner eigener Vorlagen, wenn der Benutzer keinen eigenen gewählt hat.

### `plattform/protokoll.py`

Protokoll: eine Logdatei im Zwischenspeicher-Ordner, damit Fehler beim Laden, Speichern und Prüfen nicht still verschwinden.

- `schwaerzen(text)` — Schlüssel, Tokens und Kennwörter in einem Text durch „***“ ersetzen.
- **class `SchutzFilter`**(logging.Filter) — Schwärzt Meldung und Ablaufspur, bevor sie in die Logdatei geschrieben werden.
  - `filter(record)`
- `umgebung()`
- `benutzerfehler(log, fehler)` — Erwartet und für den Benutzer bestimmt: eine Zeile ohne Ablaufspur.
- `technischer_fehler(log, kontext, fehler)` — Die Umgebung versagt (Platte, Netz, Dienst): Art des Fehlers und Systemcode, ohne Ablaufspur.
- `unerwartet(log, kontext, fehler)` — Ein Programmfehler: vollständige Ablaufspur und Umgebung, damit er sich nachstellen lässt.
- `logdatei()`
- `einrichten(stufe)` — Logdatei einrichten und nicht abgefangene Fehler protokollieren; liefert den Pfad (oder None, wenn nicht schreibbar).

### `plattform/prozess.py`

Fremde Programme starten und sicher beenden — die einzige Stelle, die dabei auf das Betriebssystem Rücksicht nimmt.

- `bereinigte_umgebung(basis)` — Die Umgebung ohne Variablen, die nach Zugangsdaten aussehen (API-Schlüssel, Tokens, Kennwörter).
- `starten(args, **kw)` — ``subprocess.Popen`` mit eigener Prozessgruppe und bereinigter Umgebung (``env`` überschreibt).
- `_signal(p, hart)`
- `beenden(p, warte)` — Beendet den Prozess (und bei POSIX seine Gruppe) und wartet auf ihn, damit kein Zombie bleibt.

### `plattform/schriften.py`

Schriftordner des Betriebssystems (Qt-frei). Die Textsatz-Schicht fragt hier, statt selbst nach dem System zu unterscheiden.

- `schrift_ordner()` — Übliche Schriftordner des Systems; weitere über die Umgebungsvariable ``LUNIVO_SCHRIFTEN`` (liest die Schriftdatenbank).

### `plattform/sperre.py`

Sperre auf eine Sperrdatei, die auch zwischen Lunivo-Fenstern (Prozessen) gilt: fcntl unter Linux/macOS, msvcrt unter Windows.

- **class `SperreBelegt`**(Exception) — Ein anderer Prozess hält die Sperre.
- `sperr_ordner()` — Ordner für die Sperrdateien (nur für den Benutzer); wird bei Bedarf angelegt.
- `sperre_oeffnen(datei)` — Sperrdatei öffnen und sofort sperren; gibt den Dateideskriptor zurück. Belegt → SperreBelegt, sonst OSError.
- `sperre_freigeben(fd)`

### `plattform/sprachausgabe.py`

Plattformanbindung der Sprachausgabe: Audio-Abspieler für Piper und der Sprachdienst des Systems.

- `programmname(name)` — Dateiname einer ausführbaren Datei auf diesem System (Windows: mit ``.exe``).
- `abspieler()` — Befehl, der rohe 16-Bit-Töne (22,05 kHz, mono) von stdin abspielt; ``None``, wenn dieses System keinen eingerichtet hat.
- `system_da()`
- `system_stimmen()` — Deutsche Stimmen des Sprachdienstes: ``[{"kennung", "name"}]``.
- `system_stoppen()`
- `system_sprechen(text, stimme, tempo)`
- `hinweis_fehlt()` — Verständliche Meldung, wenn keine Sprachausgabe eingerichtet ist.

