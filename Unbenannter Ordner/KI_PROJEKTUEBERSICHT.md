# Lunivo Office – Automatische Projektübersicht

## Einordnung und Projektverzeichnis

Statische Bestandsaufnahme, kein Arbeitsauftrag. Anweisungsrangfolge, Projektpfade und Arbeitsgrenzen stehen zentral in `CLAUDE.md`. Die folgenden Angaben beschreiben den Stand bei Erstellung dieser Übersicht, nicht zwingend den aktuellen Quellcode.

Diese Übersicht wurde statisch aus dem Quellcode erstellt.
Es wurde kein Programmcode ausgeführt.

## Gesamtumfang

- Python-Dateien: 594
- Dateien mit direkt erkannten Qt-Imports: 366

Ein fehlender Qt-Import beweist keine vollständige Qt-Unabhängigkeit, da indirekte Abhängigkeiten möglich sind.

## Projektbereiche

- `(Hauptpaket)`: 3 Python-Dateien
- `adapter`: 10 Python-Dateien
- `core`: 41 Python-Dateien
- `dienste`: 64 Python-Dateien
- `editor`: 99 Python-Dateien
- `kern`: 39 Python-Dateien
- `ki`: 31 Python-Dateien
- `korrektur`: 12 Python-Dateien
- `modelle`: 4 Python-Dateien
- `oberflaeche`: 285 Python-Dateien
- `plattform`: 6 Python-Dateien

## Module, Klassen und Funktionen

### `__init__.py`
- Direkter Qt-Import: nein

### `__main__.py`
- Direkter Qt-Import: nein
- Interne Imports: `lunivo_writer.app`

### `adapter/__init__.py`
- Direkter Qt-Import: nein

### `adapter/qt/__init__.py`
- Direkter Qt-Import: nein

### `adapter/qt/bearbeitung.py`
- Direkter Qt-Import: ja
- Klassen: `ModellSpiegel`
- Interne Imports: `lunivo_writer.adapter.qt.dokument`, `lunivo_writer.core.document.model`, `lunivo_writer.core.document.objekte`, `lunivo_writer.core.editing`, `lunivo_writer.core.editing.sitzung`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.tabelle.tabelleneigenschaften`

### `adapter/qt/dokument.py`
- Direkter Qt-Import: ja
- Klassen: `NichtUebertragbar`, `_Lesen`, `_Schreiben`
- Funktionen: `_name`, `_id`, `_wert`, `_verlauf`, `_verlauf_zurueck`, `_farbe`, `_zurueck`, `eigenschaften`, `_setzen`, `absatzformat_aus_qt`, `absatzformat_zu_qt_properties`, `zeichenformat_aus_qt`, `zeichenformat_zu_qt_properties`, `_bild_daten`, `_png`, `_bild`, `_bild_aus_modell`, `bild_aus_qimage`, `seite_bilder_zu_qt`, `bild_aus_format`, `_absatz`, `_inhalt`, `_tabelle`, `_enum`, `textoption_lesen`, `textoption_setzen`, `schnitte_bilden`, `medien_sammeln`, `document_from_qt`, `_runs_schreiben`, `_absatz_schreiben`, `_inhalt_schreiben`, `document_to_qt`, `_signatur`, `vergleichen`
- Interne Imports: `lunivo_writer.core.document`, `lunivo_writer.core.layout.seitenumbruch`, `lunivo_writer.dienste.vektor_bilder`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.seite`

### `adapter/qt/geometrie.py`
- Direkter Qt-Import: ja
- Funktionen: `point_from_qt`, `point_to_qt`, `size_from_qt`, `size_to_qt`, `rect_from_qt`, `rect_to_qt`, `margins_from_qt`, `margins_to_qt`
- Interne Imports: `lunivo_writer.core.geometry`

### `adapter/qt/pdf_modell.py`
- Direkter Qt-Import: ja
- Funktionen: `modell_als_pdf`
- Interne Imports: `lunivo_writer.adapter.qt.dokument`, `lunivo_writer.adapter.qt.seitenbild`, `lunivo_writer.core.document`, `lunivo_writer.core.layout`, `lunivo_writer.dienste.textsatz`, `lunivo_writer.editor.seite.seiten_aufteilung`, `lunivo_writer.modelle.seite`

### `adapter/qt/pfad.py`
- Direkter Qt-Import: ja
- Funktionen: `pfad_zu_vektor`, `vektor_zu_pfad`
- Interne Imports: `lunivo_writer.adapter.qt.rendering`, `lunivo_writer.core.document.objekte`

### `adapter/qt/rendering.py`
- Direkter Qt-Import: ja
- Klassen: `QtRenderBackend`
- Funktionen: `_farbe`, `_stufen`, `_bild`, `_png`, `_pinsel`, `_qfont`, `_ausgewaschen`, `_qrect`, `_flags`
- Interne Imports: `lunivo_writer.adapter.qt.textlayout`, `lunivo_writer.core.document.bildformat`, `lunivo_writer.core.geometry`, `lunivo_writer.core.rendering`, `lunivo_writer.core.textlayout`, `lunivo_writer.dienste`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.text`, `lunivo_writer.editor.text.textur`

### `adapter/qt/seitenbild.py`
- Direkter Qt-Import: ja
- Funktionen: `_kopf_fuss`, `grundschrift`, `seite_malen`, `seiten_bilder_modell`, `seiten_aus_modell`
- Interne Imports: `lunivo_writer.adapter.qt.dokument`, `lunivo_writer.adapter.qt.rendering`, `lunivo_writer.adapter.qt.textlayout`, `lunivo_writer.core.document`, `lunivo_writer.core.geometry`, `lunivo_writer.core.layout`, `lunivo_writer.core.rendering`, `lunivo_writer.core.rendering.kopffuss`, `lunivo_writer.dienste.textsatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.seiten_aufteilung`, `lunivo_writer.editor.seite.seiten_aufteilung_deko`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`

### `adapter/qt/textlayout.py`
- Direkter Qt-Import: ja
- Klassen: `QtTextLayoutEngine`
- Funktionen: `_schrift`, `_fontspec_aus`
- Interne Imports: `lunivo_writer.core.textlayout`

### `app.py`
- Direkter Qt-Import: ja
- Funktionen: `main`
- Interne Imports: `lunivo_writer.kern.anwendung`

### `core/__init__.py`
- Direkter Qt-Import: nein

### `core/document/__init__.py`
- Direkter Qt-Import: nein

### `core/document/bildformat.py`
- Direkter Qt-Import: nein
- Klassen: `BildFehler`
- Funktionen: `format_erkennen`, `entpacken`, `_jpeg`, `_tiff`, `_webp`, `_zahl`, `_svg`, `masse`, `seitenverhaeltnis`

### `core/document/model.py`
- Direkter Qt-Import: nein
- Klassen: `CharacterFormat`, `ParagraphFormat`, `ListFormat`, `TextRun`, `Image`, `Paragraph`, `TableCell`, `TableRow`, `Table`, `Frame`, `PageLayout`, `Footnote`, `Section`, `Document`

### `core/document/objekte.py`
- Direkter Qt-Import: nein
- Klassen: `Transform`, `Anchor`, `WrapSettings`, `FillStyle`, `StrokeStyle`, `Shadow`, `VectorPath`, `ImageObject`, `ShapeObject`
- Funktionen: `_rest`

### `core/document/position.py`
- Direkter Qt-Import: nein
- Klassen: `Caret`

### `core/document/values.py`
- Direkter Qt-Import: nein
- Klassen: `Color`, `Brush`, `GradientBrush`, `TextureBrush`, `Pen`, `Length`, `LineSpacing`, `RowHeight`, `TabStop`

### `core/document/zugriff.py`
- Direkter Qt-Import: nein
- Funktionen: `behaelter`, `absatz_bei`

### `core/editing/__init__.py`
- Direkter Qt-Import: nein

### `core/editing/sitzung.py`
- Direkter Qt-Import: nein
- Klassen: `Ersetzung`, `Aenderung`, `Sitzung`
- Funktionen: `_zeichenfelder_aktualisieren`, `innerste_tabelle`, `absaetze`, `laenge`, `_teilen`, `_verschmelzen`, `_neuer`

### `core/editing/tabelle.py`
- Direkter Qt-Import: nein
- Funktionen: `_leere_zelle`, `_zellen`, `_aufbauen`, `_zelle_an`, `zeilen_einfuegen`, `zeilen_loeschen`, `spalten_einfuegen`, `spalten_loeschen`, `zellen_verbinden`, `zelle_teilen`, `_neue_aufnehmen`

### `core/geometry/__init__.py`
- Direkter Qt-Import: nein

### `core/geometry/margins.py`
- Direkter Qt-Import: nein
- Klassen: `Margins`

### `core/geometry/point.py`
- Direkter Qt-Import: nein
- Klassen: `Point`

### `core/geometry/rect.py`
- Direkter Qt-Import: nein
- Klassen: `Rect`

### `core/geometry/size.py`
- Direkter Qt-Import: nein
- Klassen: `Size`

### `core/geometry/units.py`
- Direkter Qt-Import: nein
- Funktionen: `mm_to_px`, `px_to_mm`, `umbruchraster`

### `core/layout/__init__.py`
- Direkter Qt-Import: nein

### `core/layout/eigenschaften.py`
- Direkter Qt-Import: nein
- Funktionen: `_zahl`, `schrift`, `ausrichtung`, `abstaende`, `einzuege`, `zeilenabstand`, `umbruch_vor`, `umbruch_nach`, `laenge`, `tabstopps`, `tabfuellung`, `absatzrahmen`, `kapitaelchen`, `kapitaelchen_stuecke`, `hintergrund`, `grundschrift`, `_brush_farbe`, `stil`, `_farbwert`, `schreibweise`, `_roemisch`, `_buchstaben`, `listenzeichen`

### `core/layout/navigation.py`
- Direkter Qt-Import: nein
- Funktionen: `pfade`, `_zeile`, `cursor_rechteck`, `auswahl_rechtecke`, `_zeilen_der_seite`, `_stelle_in`, `_senkrecht`, `_wortgrenze`, `wort_bei`, `bewegen`

### `core/layout/objekte.py`
- Direkter Qt-Import: nein
- Funktionen: `objekt_rechteck`

### `core/layout/regeln.py`
- Direkter Qt-Import: nein
- Funktionen: `umbruch_stelle`

### `core/layout/seitenumbruch.py`
- Direkter Qt-Import: nein
- Klassen: `AbsatzOrt`, `Platz`, `Seite`, `Ergebnis`, `_Fluss`
- Funktionen: `_noten_platzieren`, `hoehe_von_bloecken`, `umbrechen`

### `core/rendering/__init__.py`
- Direkter Qt-Import: nein

### `core/rendering/backend.py`
- Direkter Qt-Import: nein
- Klassen: `LinearGradient`, `RadialGradient`, `PatternFill`, `TextureFill`, `ImageFill`, `Style`, `RenderTarget`, `RenderBackend`
- Funktionen: `rgba`

### `core/rendering/dokument.py`
- Direkter Qt-Import: nein
- Funktionen: `zeichne_dokumentseite`

### `core/rendering/kopffuss.py`
- Direkter Qt-Import: nein
- Funktionen: `schrift`, `_mit_effekt`, `zeichne_zeile`

### `core/rendering/linien.py`
- Direkter Qt-Import: nein
- Funktionen: `_bauen`, `zeichne_linie`, `zeichne_rahmen`, `rahmen_aus_text`, `zeichne_absatzrahmen`

### `core/rendering/objekte.py`
- Direkter Qt-Import: nein
- Funktionen: `heller`, `fuellstil`, `kontur_stil`, `zeichne_bild`, `zeichne_platzhalter`, `form_pfad`, `zeichne_form`

### `core/rendering/seite.py`
- Direkter Qt-Import: nein
- Funktionen: `zeichne_zeile`, `zeichne_tabfuellung`, `zeichne_absatzrahmen_der_seite`, `_woerter`, `zeichne_marke`, `zeichne_freie_bilder`, `_textfeld_einfach_zeichnen`, `zeichne_seite`, `zeichne_auswahl`, `zeichne_cursor`, `zeichne_zeilennummern`

### `core/rendering/seitenrahmen.py`
- Direkter Qt-Import: nein
- Funktionen: `abstaende_pt`, `rechteck`, `_vieleck`, `_figur`, `kunst_zeichnen`, `zeichnen`

### `core/rendering/seitenschmuck.py`
- Direkter Qt-Import: nein
- Funktionen: `zeichne_seitenschmuck`

### `core/rendering/tabelle.py`
- Direkter Qt-Import: nein
- Funktionen: `_farbe`, `_kante`, `zelle_anweisungen`, `rahmen_anweisungen`, `ausfuehren`

### `core/rendering/wasserzeichen.py`
- Direkter Qt-Import: nein
- Funktionen: `da`, `bild_bytes`, `deckkraft`, `lage`, `schrift`, `zeichne`

### `core/rendering/wordart.py`
- Direkter Qt-Import: nein
- Funktionen: `masse`, `zeichne`

### `core/textlayout/__init__.py`
- Direkter Qt-Import: nein

### `core/textlayout/engine.py`
- Direkter Qt-Import: nein
- Klassen: `FontSpec`, `FontMetrics`, `GlyphPosition`, `LineBox`, `TextLayoutEngine`

### `core/textlayout/fontconfig.py`
- Direkter Qt-Import: nein
- Funktionen: `_texte`, `_lesen_datei`, `regeln`, `familien_liste`

### `core/textlayout/fontdb.py`
- Direkter Qt-Import: nein
- Klassen: `Schnitt`, `SchriftDatenbank`
- Funktionen: `ersatz_von_qt`

### `core/textlayout/hb_engine.py`
- Direkter Qt-Import: nein
- Klassen: `_Schrift`, `HarfBuzzEngine`
- Funktionen: `umbruch_stellen`, `zeilen_umbrechen`

### `core/textlayout/paragraph.py`
- Direkter Qt-Import: nein
- Klassen: `Objekt`, `SatzZeile`, `Lauf`, `Absatzsatz`
- Funktionen: `zeilenhoehe`, `zeilenmasse`, `_naechster_stopp`, `_tab_vorschuebe`, `_lauf_maße`, `absatz_setzen`

### `dienste/__init__.py`
- Direkter Qt-Import: nein

### `dienste/bausteine.py`
- Direkter Qt-Import: ja
- Funktionen: `_pfad`, `laden`, `speichern`, `standard`, `alle`, `finde_kuerzel`, `hinzufuegen`, `entfernen`, `einfuegen`
- Interne Imports: `lunivo_writer.dienste.einstellungen_dienst`, `lunivo_writer.editor.text.textdaten`, `lunivo_writer.kern`

### `dienste/bild_export.py`
- Direkter Qt-Import: ja
- Klassen: `BildWahl`
- Funktionen: `_frei`, `wasserzeichen`, `_speichern`, `bilder_schreiben`, `_seitenbilder_schreiben`, `_langes_bild_schreiben`, `_langes_modellbild_schreiben`
- Interne Imports: `lunivo_writer.adapter.qt.seitenbild`, `lunivo_writer.core.document`, `lunivo_writer.core.layout`, `lunivo_writer.dienste.textsatz`, `lunivo_writer.editor.seite.seiten_aufteilung`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`

### `dienste/datei_dienst.py`
- Direkter Qt-Import: ja
- Klassen: `Loaded`
- Funktionen: `endung_zum_filter`, `ext`, `_verschluesselt`, `_entschluesseln`, `_docx_lesen`, `_docx_laden`, `_txt_laden`, `load`, `_kopf_pruefen`, `_has_rich_content`, `save`, `save_docx_daten`, `_als_docx`, `_verschluesseln`
- Interne Imports: `lunivo_writer.adapter.qt.dokument`, `lunivo_writer.core.document`, `lunivo_writer.dienste`, `lunivo_writer.dienste.odt_modell_leser`, `lunivo_writer.dienste.odt_schreiber`, `lunivo_writer.dienste.rtf`, `lunivo_writer.dienste.rtf_modell_leser`, `lunivo_writer.dienste.rtf_schreiber`, `lunivo_writer.dienste.txt_modell`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.modelle.bericht`, `lunivo_writer.modelle.seite`

### `dienste/docx_leser.py`
- Direkter Qt-Import: ja
- Klassen: `_Reader`
- Funktionen: `_kinder`, `_schriften_ersatz`, `read_docx`
- Interne Imports: `lunivo_writer.dienste.docx_teile.lesen_absatz`, `lunivo_writer.dienste.docx_teile.lesen_gemeinsam`, `lunivo_writer.dienste.docx_teile.lesen_metadaten`, `lunivo_writer.dienste.docx_teile.lesen_objekte`, `lunivo_writer.dienste.docx_teile.lesen_runs`, `lunivo_writer.dienste.docx_teile.lesen_seite`, `lunivo_writer.dienste.docx_teile.lesen_stile`, `lunivo_writer.dienste.docx_teile.lesen_tabellen`, `lunivo_writer.dienste.docx_teile.lesen_textfelder`, `lunivo_writer.dienste.docx_teile.lesen_vml`, `lunivo_writer.dienste.import_grenzen`, `lunivo_writer.plattform`

### `dienste/docx_modell_leser.py`
- Direkter Qt-Import: ja
- Klassen: `NichtImModell`, `_Absatz`, `_Fertig`, `_BlockRef`, `_ListRef`, `_ZelleRef`, `_TabelleRef`, `ModellCursor`, `_ModellReader`
- Funktionen: `lese_docx_modell`
- Interne Imports: `lunivo_writer.adapter.qt.dokument`, `lunivo_writer.core.document`, `lunivo_writer.core.layout`, `lunivo_writer.core.layout.seitenumbruch`, `lunivo_writer.core.textlayout`, `lunivo_writer.dienste`, `lunivo_writer.dienste.import_grenzen`, `lunivo_writer.dienste.textsatz`, `lunivo_writer.editor.dokument.indexeintrag`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.umbruch`, `lunivo_writer.editor.tabelle.tabelleneigenschaften`, `lunivo_writer.modelle.seite`

### `dienste/docx_schreiber.py`
- Direkter Qt-Import: nein
- Klassen: `_Writer`
- Funktionen: `docx_daten`, `docx_modell_daten`, `write_docx`
- Interne Imports: `lunivo_writer.core.document`, `lunivo_writer.core.document.values`, `lunivo_writer.dienste`, `lunivo_writer.dienste.docx_teile.schreiben_absatz`, `lunivo_writer.dienste.docx_teile.schreiben_dokument`, `lunivo_writer.dienste.docx_teile.schreiben_gemeinsam`, `lunivo_writer.dienste.docx_teile.schreiben_objekte`, `lunivo_writer.dienste.docx_teile.schreiben_runs`, `lunivo_writer.dienste.docx_teile.schreiben_seite`, `lunivo_writer.dienste.docx_teile.schreiben_tabellen`, `lunivo_writer.dienste.docx_teile.schreiben_textfelder`, `lunivo_writer.dienste.docx_teile.schreiben_zusatz`, `lunivo_writer.modelle.seite`

### `dienste/docx_teile/__init__.py`
- Direkter Qt-Import: nein

### `dienste/docx_teile/lesen_absatz.py`
- Direkter Qt-Import: ja
- Klassen: `LesenAbsatzMixin`
- Funktionen: `_listeneintraege`
- Interne Imports: `lunivo_writer.dienste.docx_teile.lesen_gemeinsam`, `lunivo_writer.editor.dokument`, `lunivo_writer.editor.dokument.indexeintrag`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.text`

### `dienste/docx_teile/lesen_gemeinsam.py`
- Direkter Qt-Import: ja
- Klassen: `_NoRun`
- Funktionen: `_xp`, `_emu_to_px`, `_pt_to_px`, `_style_chain`, `_doc_defaults`
- Interne Imports: `lunivo_writer.dienste.import_grenzen`, `lunivo_writer.editor.dokument.formular`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte.linie`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.bericht`, `lunivo_writer.modelle.seite`

### `dienste/docx_teile/lesen_metadaten.py`
- Direkter Qt-Import: nein
- Klassen: `LesenMetadatenMixin`
- Interne Imports: `lunivo_writer.dienste.docx_teile.lesen_gemeinsam`

### `dienste/docx_teile/lesen_objekte.py`
- Direkter Qt-Import: nein
- Klassen: `ObjekteMixin`
- Funktionen: `_fx_farbe`, `_fx_leuchten`, `_fx_schatten`, `_fx_reflektion`, `_fx_weich`
- Interne Imports: `lunivo_writer.dienste.docx_teile.lesen_gemeinsam`, `lunivo_writer.dienste.vektor_bilder`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.freie_bilder`, `lunivo_writer.editor.seite.umbruch`

### `dienste/docx_teile/lesen_runs.py`
- Direkter Qt-Import: nein
- Klassen: `LesenRunsMixin`
- Interne Imports: `lunivo_writer.dienste.docx_teile.lesen_gemeinsam`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text`

### `dienste/docx_teile/lesen_seite.py`
- Direkter Qt-Import: nein
- Klassen: `SeiteMixin`
- Funktionen: `_kante_sichtbar`
- Interne Imports: `lunivo_writer.dienste.docx_teile.lesen_gemeinsam`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.abschnitte`, `lunivo_writer.editor.seite.seitenrahmen`

### `dienste/docx_teile/lesen_stile.py`
- Direkter Qt-Import: ja
- Klassen: `StilMixin`
- Interne Imports: `lunivo_writer.dienste.docx_teile.lesen_gemeinsam`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text`, `lunivo_writer.editor.text.unterstreichung`

### `dienste/docx_teile/lesen_tabellen.py`
- Direkter Qt-Import: ja
- Klassen: `TabellenMixin`
- Funktionen: `_px`
- Interne Imports: `lunivo_writer.core.layout.seitenumbruch`, `lunivo_writer.dienste.docx_teile.lesen_gemeinsam`, `lunivo_writer.editor.tabelle.tabelleneigenschaften`, `lunivo_writer.modelle.seite`

### `dienste/docx_teile/lesen_textfelder.py`
- Direkter Qt-Import: nein
- Klassen: `TextfeldMixin`
- Interne Imports: `lunivo_writer.dienste.docx_teile.lesen_gemeinsam`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.frei_objekt_text`, `lunivo_writer.editor.objekte.freie_bilder`

### `dienste/docx_teile/lesen_vml.py`
- Direkter Qt-Import: nein
- Klassen: `VmlMixin`
- Funktionen: `_stil`, `_pt`, `_hex`
- Interne Imports: `lunivo_writer.dienste.docx_teile.lesen_gemeinsam`, `lunivo_writer.dienste.docx_teile.lesen_textfelder`, `lunivo_writer.dienste.vektor_bilder`, `lunivo_writer.editor.objekte`

### `dienste/docx_teile/schreiben_absatz.py`
- Direkter Qt-Import: ja
- Klassen: `SchreibenAbsatzMixin`
- Interne Imports: `lunivo_writer.dienste.docx_teile.schreiben_gemeinsam`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.seitenfluss`, `lunivo_writer.editor.text`, `lunivo_writer.editor.text.fragmente`

### `dienste/docx_teile/schreiben_dokument.py`
- Direkter Qt-Import: nein
- Klassen: `SchreibenDokumentMixin`
- Interne Imports: `lunivo_writer.dienste.docx_teile.schreiben_gemeinsam`, `lunivo_writer.modelle.seite`

### `dienste/docx_teile/schreiben_gemeinsam.py`
- Direkter Qt-Import: ja
- Klassen: `_Body`, `_CellBox`
- Funktionen: `_has`, `_rpr_einfuegen`, `absatzopt_prop`, `_split`, `_rstyle_hyperlink`
- Interne Imports: `lunivo_writer.dienste.docx_leser`, `lunivo_writer.editor.dokument.formular`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte.linie`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.abschnitte`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.bericht`, `lunivo_writer.modelle.seite`

### `dienste/docx_teile/schreiben_objekte.py`
- Direkter Qt-Import: nein
- Klassen: `ObjekteSchreiber`
- Funktionen: `_eins`
- Interne Imports: `lunivo_writer.core.document.objekte`, `lunivo_writer.dienste.docx_teile.schreiben_gemeinsam`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.text`

### `dienste/docx_teile/schreiben_runs.py`
- Direkter Qt-Import: nein
- Klassen: `SchreibenRunsMixin`
- Interne Imports: `lunivo_writer.dienste.docx_teile.schreiben_gemeinsam`, `lunivo_writer.editor.dokument`, `lunivo_writer.editor.dokument.indexeintrag`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text`

### `dienste/docx_teile/schreiben_seite.py`
- Direkter Qt-Import: nein
- Klassen: `SeiteSchreiber`
- Funktionen: `_zeichenformat_schreiben`
- Interne Imports: `lunivo_writer.dienste.docx_teile.schreiben_gemeinsam`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.seitenrahmen`

### `dienste/docx_teile/schreiben_tabellen.py`
- Direkter Qt-Import: ja
- Klassen: `TabellenSchreiber`
- Funktionen: `_verschachtelte_in_zelle`, `_twips`, `_wel`
- Interne Imports: `lunivo_writer.core.layout.seitenumbruch`, `lunivo_writer.dienste.docx_teile.schreiben_gemeinsam`, `lunivo_writer.editor.tabelle.tabelleneigenschaften`, `lunivo_writer.modelle.seite`

### `dienste/docx_teile/schreiben_textfelder.py`
- Direkter Qt-Import: nein
- Klassen: `TextfeldSchreiber`
- Funktionen: `_w`
- Interne Imports: `lunivo_writer.editor.objekte`

### `dienste/docx_teile/schreiben_zusatz.py`
- Direkter Qt-Import: nein
- Klassen: `ZusatzSchreiber`
- Interne Imports: `lunivo_writer.dienste.docx_teile.schreiben_gemeinsam`

### `dienste/einstellungen_dienst.py`
- Direkter Qt-Import: ja
- Klassen: `Settings`
- Interne Imports: `lunivo_writer.plattform.pfade`

### `dienste/formate.py`
- Direkter Qt-Import: nein
- Klassen: `FormatInfo`
- Funktionen: `finde`, `lesbar`, `speicherbar`, `als_markdown`

### `dienste/gelernt.py`
- Direkter Qt-Import: nein
- Klassen: `Gelernt`
- Interne Imports: `lunivo_writer.dienste.einstellungen_dienst`, `lunivo_writer.modelle.korrektur`

### `dienste/import_grenzen.py`
- Direkter Qt-Import: nein
- Klassen: `Grenzen`
- Funktionen: `_mb`, `pruefe_dateigroesse`, `_zu_gross`, `pruefe_paket`, `_entpacken_zaehlen`, `_tiefe_pruefen`, `sicheres_xml`, `lxml_parser`
- Interne Imports: `lunivo_writer.modelle.bericht`

### `dienste/integrationen/__init__.py`
- Direkter Qt-Import: nein

### `dienste/integrationen/languagetool.py`
- Direkter Qt-Import: nein
- Klassen: `LanguageToolFehler`
- Funktionen: `ordner`, `laeuft`, `jar_finden`, `fremd_erlauben`, `eigener_prozess_laeuft`, `status`, `verfuegbar`, `_freier_port`, `starten`, `pruefe`, `beenden`
- Interne Imports: `lunivo_writer.dienste.einstellungen_dienst`, `lunivo_writer.plattform`

### `dienste/integrationen/verzeichnis.py`
- Direkter Qt-Import: nein
- Klassen: `Integration`
- Funktionen: `_languagetool`, `_ki`, `_mcp`, `uebersicht`
- Interne Imports: `lunivo_writer.dienste.integrationen`

### `dienste/modell_laden.py`
- Direkter Qt-Import: nein
- Klassen: `ModellGeladen`
- Funktionen: `lade_modell`
- Interne Imports: `lunivo_writer.adapter.qt.dokument`, `lunivo_writer.core.document`, `lunivo_writer.dienste.datei_dienst`, `lunivo_writer.dienste.txt_modell`, `lunivo_writer.modelle.bericht`

### `dienste/modell_speichern.py`
- Direkter Qt-Import: nein
- Funktionen: `speichere_modell`
- Interne Imports: `lunivo_writer.adapter.qt.dokument`, `lunivo_writer.adapter.qt.pdf_modell`, `lunivo_writer.core.document`, `lunivo_writer.dienste`, `lunivo_writer.dienste.txt_modell`, `lunivo_writer.modelle.bericht`

### `dienste/odt_bilder.py`
- Direkter Qt-Import: ja
- Klassen: `_ODTBilder`
- Interne Imports: `lunivo_writer.dienste.odt_schreiben_basis`, `lunivo_writer.dienste.odt_xml`, `lunivo_writer.dienste.vektor_bilder`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`

### `dienste/odt_leser.py`
- Direkter Qt-Import: ja
- Klassen: `_Ort`, `_Leser`
- Funktionen: `_leerzeichen_anzahl`, `_xml`, `read_odt`, `read_fodt`
- Interne Imports: `lunivo_writer.dienste.import_grenzen`, `lunivo_writer.dienste.odt_bilder`, `lunivo_writer.dienste.odt_listen_lesen`, `lunivo_writer.dienste.odt_seite_lesen`, `lunivo_writer.dienste.odt_stile`, `lunivo_writer.dienste.odt_tabellen`, `lunivo_writer.dienste.odt_xml`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.modelle.bericht`, `lunivo_writer.modelle.seite`

### `dienste/odt_listen_lesen.py`
- Direkter Qt-Import: ja
- Klassen: `_ODTListen`
- Interne Imports: `lunivo_writer.dienste.odt_xml`

### `dienste/odt_modell_leser.py`
- Direkter Qt-Import: nein
- Klassen: `NichtImModell`, `_Stile`, `_Leser`
- Funktionen: `_farbe`, `_format`, `_absatzformat`, `_xml`, `lese_odt_modell`
- Interne Imports: `lunivo_writer.core.document`, `lunivo_writer.core.document.bildformat`, `lunivo_writer.core.document.values`, `lunivo_writer.dienste.import_grenzen`, `lunivo_writer.dienste.odt_xml`, `lunivo_writer.modelle.bericht`, `lunivo_writer.modelle.seite`

### `dienste/odt_schreiben_basis.py`
- Direkter Qt-Import: ja
- Funktionen: `_mm`, `bild_aus_format`, `spannweite`, `_odf`, `_laenge`, `_dekorativ`, `_bild_stil`, `_frei_stil`, `_bild_elemente`, `_frei_rahmen`, `_frei_form`
- Interne Imports: `lunivo_writer.editor.objekte`

### `dienste/odt_schreiber.py`
- Direkter Qt-Import: ja
- Klassen: `_Inhalt`
- Funktionen: `_manifest`, `_text_zeichen`, `_leerzeichen_lauf`, `_text_xml`, `_farbe`, `_text_schluessel`, `_text_eigenschaften`, `_absatz_vorlage_xml`, `_listen_ebene_xml`, `_meta_xml`, `odt_daten`, `_verluste_melden`
- Interne Imports: `lunivo_writer.dienste.odt_schreiben_basis`, `lunivo_writer.dienste.odt_seite_schreiben`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.modelle.bericht`, `lunivo_writer.modelle.seite`

### `dienste/odt_seite_lesen.py`
- Direkter Qt-Import: ja
- Klassen: `_ODTSeite`
- Funktionen: `_mm`, `_hauptvorlage`, `_bereich_da`, `_bereich_abstand`, `_layout_anwenden`
- Interne Imports: `lunivo_writer.dienste.odt_xml`, `lunivo_writer.modelle.seite`

### `dienste/odt_seite_schreiben.py`
- Direkter Qt-Import: ja
- Funktionen: `_absatz`, `_standard`, `_bilder_rahmen`, `_hat_inhalt`, `_aktiv`, `_bereich_stil`, `_ausrichtungs_stile`, `_gespiegelt`, `_master_teile`, `_seitenlayout`, `_styles_xml`
- Interne Imports: `lunivo_writer.dienste.odt_schreiben_basis`, `lunivo_writer.editor.seite`, `lunivo_writer.modelle.seite`

### `dienste/odt_stile.py`
- Direkter Qt-Import: ja
- Klassen: `_Stile`
- Funktionen: `_lage`, `_farbe`, `_schrift`, `_zeichenformat`, `_absatzformat`
- Interne Imports: `lunivo_writer.dienste.odt_xml`

### `dienste/odt_tabellen.py`
- Direkter Qt-Import: ja
- Funktionen: `_wiederholung`, `_spannweite`, `_sammeln`, `_zellen_der_zeile`, `_tabellenformat`, `_zelle_fuellen`, `tabelle`
- Interne Imports: `lunivo_writer.dienste.odt_xml`

### `dienste/odt_xml.py`
- Direkter Qt-Import: nein
- Funktionen: `_kurz`, `_q`, `_px`, `_pt`, `_text_von`

### `dienste/pdf_export.py`
- Direkter Qt-Import: ja
- Klassen: `PdfWahl`
- Funktionen: `seiten`, `lesezeichen`, `nur_markierung`, `berechtigungen`, `kennwort_fehler`, `verschluesseln`

### `dienste/rtf/__init__.py`
- Direkter Qt-Import: nein
- Interne Imports: `lunivo_writer.dienste.rtf.leser`

### `dienste/rtf/aufbau.py`
- Direkter Qt-Import: ja
- Klassen: `Bauer`
- Funktionen: `absatzformat`, `tabellenformat`, `kopf_fuss_text`
- Interne Imports: `lunivo_writer.dienste.rtf.modell`, `lunivo_writer.modelle.seite`

### `dienste/rtf/bilder.py`
- Direkter Qt-Import: ja
- Funktionen: `neues_bild`, `bild_wort`, `_bilddaten`, `bild_lauf_modell`, `bild_lauf`
- Interne Imports: `lunivo_writer.core.document.bildformat`, `lunivo_writer.dienste.vektor_bilder`

### `dienste/rtf/gruppen.py`
- Direkter Qt-Import: nein
- Funktionen: `ziel_beginnen`, `_tabellen_ziel`, `_info_ziel`, `_kopf_fuss_ziel`, `_inhalts_ziel`, `_feld_ziel`, `_verworfenes_ziel`, `gruppe_ende`, `gruppentext`
- Interne Imports: `lunivo_writer.dienste.rtf.bilder`, `lunivo_writer.dienste.rtf.modell`

### `dienste/rtf/leser.py`
- Direkter Qt-Import: ja
- Funktionen: `_daten_lesen`, `_dokument_bauen`, `_seite_fertig`, `read_rtf`
- Interne Imports: `lunivo_writer.dienste.rtf.aufbau`, `lunivo_writer.dienste.rtf.zerleger`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.modelle.bericht`, `lunivo_writer.modelle.seite`

### `dienste/rtf/modell.py`
- Direkter Qt-Import: nein
- Klassen: `NichtImModell`, `Absatz`, `Tabelle`, `Ziel`

### `dienste/rtf/steuerwoerter.py`
- Direkter Qt-Import: nein
- Funktionen: `steuerwort`, `_text_wort`, `_seite_umbruch`, `_absatz_format`, `_absatz_wort`, `_zeichen_wort`, `_dokument_wort`

### `dienste/rtf/zerleger.py`
- Direkter Qt-Import: nein
- Klassen: `Zerleger`
- Funktionen: `_ersatzpaar`, `_unicode_zeichen`
- Interne Imports: `lunivo_writer.dienste.rtf`, `lunivo_writer.dienste.rtf.gruppen`, `lunivo_writer.dienste.rtf.modell`, `lunivo_writer.dienste.rtf.steuerwoerter`, `lunivo_writer.modelle.bericht`, `lunivo_writer.modelle.seite`

### `dienste/rtf_modell_leser.py`
- Direkter Qt-Import: nein
- Funktionen: `_farbe`, `_zeichenformat`, `_absatzformat`, `_absatz`, `_zelle`, `_ziel`, `_kopf_fuss`, `lese_rtf_modell`
- Interne Imports: `lunivo_writer.core.document`, `lunivo_writer.core.document.values`, `lunivo_writer.dienste.rtf.leser`, `lunivo_writer.dienste.rtf.modell`, `lunivo_writer.dienste.rtf.zerleger`, `lunivo_writer.modelle.bericht`, `lunivo_writer.modelle.seite`

### `dienste/rtf_schreiber.py`
- Direkter Qt-Import: ja
- Klassen: `_Rtf`
- Funktionen: `_bild_daten`, `_mm`, `_px`, `_text`, `_bloecke`, `rtf_daten`
- Interne Imports: `lunivo_writer.dienste.odt_schreiber`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.freie_bilder`, `lunivo_writer.editor.seite.seitenzahl`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.modelle.bericht`, `lunivo_writer.modelle.seite`

### `dienste/sicher_schreiben.py`
- Direkter Qt-Import: nein
- Klassen: `SchreibKonflikt`
- Funktionen: `ziel`, `stand`, `fremd_geoeffnet`, `fehlertext`, `_umask`, `_fsync_datei`, `_fsync_ordner`, `_rest_muster`, `_reste_aufraeumen`, `sperre`, `sicherungs_ordner`, `_dokument_ordner`, `sicherungskopie`, `sicherungen`, `_ordner_aufraeumen`, `sicherungen_aufraeumen`, `_defekt`, `_zip_pruefen`, `_txt_pruefen`, `_odt_pruefen`, `_rtf_pruefen`, `_pdf_pruefen`, `_docx_pruefen`, `_kopf_ende_lesen`, `pruefe_format`, `_ziel_pruefen`, `_stand_pruefen`, `_tmp_entfernen`, `schreiben`, `bytes_schreiben`
- Interne Imports: `lunivo_writer.modelle.bericht`, `lunivo_writer.plattform`, `lunivo_writer.plattform.pfade`

### `dienste/textsatz.py`
- Direkter Qt-Import: nein
- Funktionen: `standard_engine`, `engine_setzen`
- Interne Imports: `lunivo_writer.core.textlayout`, `lunivo_writer.core.textlayout.hb_engine`

### `dienste/txt_modell.py`
- Direkter Qt-Import: nein
- Funktionen: `textdatei_lesen`, `modell_laden`, `text_aus_modell`
- Interne Imports: `lunivo_writer.core.document`, `lunivo_writer.dienste.import_grenzen`, `lunivo_writer.modelle.bericht`, `lunivo_writer.modelle.seite`

### `dienste/vektor_bilder.py`
- Direkter Qt-Import: ja
- Klassen: `_Zustand`
- Funktionen: `ist_emf`, `bild_lesen`, `_leer`, `_rgb`, `_rechteck`, `_dib_bild`, `_abbilden`, `_stock`, `_begrenzt`, `_emf_kopf`, `masse_px`, `emf_zeichnen`, `emf_bild`, `_zeichnen`, `_umrissen`, `_kurve`, `_vielfach`, `_mehrfach`, `_schrift`, `_text`, `_bitmap`, `ist_wmf`, `_wmf_kopf`, `_wmf_fenster`, `wmf_zeichnen`, `wmf_bild`, `_wmf_zeichnen`, `_wmf_text`, `_wmf_dib`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.freie_bilder`

### `dienste/vorlesen.py`
- Direkter Qt-Import: nein
- Klassen: `VorlesenFehler`
- Funktionen: `piper_programm`, `piper_stimmen`, `_abspieler`, `piper_da`, `spd_da`, `verfuegbar`, `tempo_begrenzen`, `tempo_piper`, `stimmen`, `beenden`, `vorlesetext`, `lies_vor`
- Interne Imports: `lunivo_writer.dienste.docx_teile.lesen_gemeinsam`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.plattform`

### `dienste/wiederherstellung.py`
- Direkter Qt-Import: nein
- Klassen: `RecoveryEntry`
- Funktionen: `recovery_dir`, `new_token`, `paths`, `write_meta`, `discard`, `pending`, `zwischenstand`
- Interne Imports: `lunivo_writer.plattform.pfade`

### `editor/__init__.py`
- Direkter Qt-Import: nein

### `editor/diagramme/__init__.py`
- Direkter Qt-Import: nein

### `editor/diagramme/diagramm.py`
- Direkter Qt-Import: ja
- Klassen: `_Zeichnung`
- Funktionen: `_filtern`, `_palette_und_daten`, `bild`, `_namen_aus_spalte_a`, `_namen_keine`, `namen_angewendet`, `bild_aus_daten`, `_ebene_malen`, `_geometrie`, `_zusaetze_malen`, `_bild_malen`, `_chart`, `_legende_einstellen`, `_bild`, `_legenden_namen`, `_achsenteile`, `teile`, `teil_geo`, `teil_rechtecke`

### `editor/diagramme/diagramm_elemente.py`
- Direkter Qt-Import: ja
- Funktionen: `_waagr_senkr`, `_ist_wertachse`, `_achsen_schalten`, `_achsentitel`, `_trend_erlaubt`, `_trendlinien`, `_titel_legende`, `_hauptgitter`, `_achsen_format`, `_datenbeschriftung`, `_reihenformat`, `_luecke`, `_reihen_format`, `anwenden`

### `editor/diagramme/diagramm_format.py`
- Direkter Qt-Import: ja
- Funktionen: `fuell_dict`, `ist_keine`, `hauptfarbe`, `bild_kodieren`, `bild_dekodieren`, `pinsel`, `flaeche_zeichnen`, `flaeche_bild`, `strich_schluessel`, `_strichmuster`, `linie_keine`, `stift`, `_verlauf_pinsel`, `rahmen_zeichnen`, `fx_normal`, `teil_zeichnen`, `feld_von`, `textwinkel`, `effekt_von`, `text_eigen`, `textfarbe`, `schrift_aus`, `box_rect`, `text_feld`, `_umbrechen`, `_textzeilen`, `_textkontur`, `text_zeichnen`, `_pfad_zeichnen`, `achse_anwenden`, `_wertachse_anwenden`, `luecke_zu_breite`, `pfeil_groessen`, `pfeil_zeichnen`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.editor.text`

### `editor/diagramme/diagramm_geo.py`
- Direkter Qt-Import: ja
- Funktionen: `_serie`, `punkte`, `_balken`, `legenden_items`, `titel_rect`, `_legendeneintraege`, `_geo_titel`, `_geo_legende`, `_geo_achsen`, `_geo_reihen`, `geometrie`, `gitter_streifen`, `_vereinigung`, `_umhuellung`

### `editor/diagramme/diagramm_kreis.py`
- Direkter Qt-Import: ja
- Funktionen: `_scheiben`, `_text`, `_flach`, `_drei_d`, `_kleine_indizes`, `_rest_ansatz`, `_von_kreis`, `_rest_balken`, `_rest_kreis`, `zeichnen`

### `editor/diagramme/diagramm_reihen.py`
- Direkter Qt-Import: ja
- Klassen: `Daten`
- Funktionen: `palette_setzen`, `farbe`, `_auf_hundert`, `_hoechstwert`, `werte_vorbereiten`, `achsen`, `_kreis`, `_kurs_volumen`, `_kurs`, `_kerzen`, `_saeulen`, `_flaeche`, `_blasen`, `_blase_faerben`, `_achse_mit_luft`, `_blasen_achsen`, `_punkte`, `_netz`, `_linien`, `_kombi_saeulen`, `_kombi_flaechen`, `_kombi_linien`, `_kombination`, `aufbauen`, `kachel_ausstatten`, `datenbeschriftung_ein`

### `editor/diagramme/diagramm_stile.py`
- Direkter Qt-Import: ja
- Funktionen: `stile_liste`, `_monochrom`, `farbschemen_gruppen`, `farbschemen_flach`, `stil_schrift`, `stil_grund`, `stil_anwenden`

### `editor/diagramme/diagramm_teile.py`
- Direkter Qt-Import: ja
- Funktionen: `teil_gewaehlt`, `teil_name`, `teil_waehlen`, `_geo`, `teil_bei`, `_diagramm_punkt`, `_treffer`, `diagramm_teil_format_lesen`, `_ohne_leer`, `_objekt_effekt_setzen`, `_format_wert_setzen`, `_objekt_effekte_lesen`, `_werte_setzen`, `_text_drehung`, `diagramm_teil_format_setzen`
- Interne Imports: `lunivo_writer.editor.objekte`

### `editor/diagramme/diagramm_typen.py`
- Direkter Qt-Import: nein
- Funktionen: `ist_kreis`, `hat_linien`, `beispiel`, `kombi_vorgabe`, `_art`

### `editor/diagramme/diagramm_zusatz.py`
- Direkter Qt-Import: ja
- Funktionen: `elemente_wirksam`, `trend`, `stift`, `schrift_aus`, `hintergruende`, `_reihen_effekte`, `linien`, `fehlerindikatoren`, `tabelle`, `text_fuer`, `eigene_texte`, `_pfeil_linie`, `pfeile`
- Interne Imports: `lunivo_writer.editor.objekte`

### `editor/dokument/__init__.py`
- Direkter Qt-Import: nein

### `editor/dokument/einfuegen.py`
- Direkter Qt-Import: ja
- Funktionen: `qimage_einfuegen`, `_leer`, `form_pinsel`, `_form_dreieck`, `_form_raute`, `_form_pfeil`, `_form_stern`, `_form_sprechblase`, `_form_zeichnen`, `_form_pfad`, `_form_ueber_backend`, `_form_text`, `form_bild`, `wordart_vorlage_bild`, `wordart_bild`, `diagramm_bild`, `piktogramm_bild`, `formel_teile`, `formel_bild`, `formel_einfuegen`, `_tabelle`, `schnelltabelle`, `deckblatt_einfuegen`, `datei_symbol_bild`, `text_aus_datei`, `datum_feldanweisung`, `datum_text`, `initiale`, `textfeld`, `_bild_cursor`, `bild_ersetzen`, `bild_original`, `farbe_anwenden`, `zuschneiden`, `drehen`
- Interne Imports: `lunivo_writer.adapter.qt.pfad`, `lunivo_writer.adapter.qt.rendering`, `lunivo_writer.core.document.objekte`, `lunivo_writer.core.geometry`, `lunivo_writer.core.rendering`, `lunivo_writer.core.rendering.backend`, `lunivo_writer.core.rendering.objekte`, `lunivo_writer.dienste`, `lunivo_writer.dienste.docx_leser`, `lunivo_writer.dienste.textsatz`, `lunivo_writer.editor.diagramme`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.bildeffekte`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.kern`, `lunivo_writer.kern.farben`

### `editor/dokument/fassungen.py`
- Direkter Qt-Import: ja
- Funktionen: `_stuecke`, `original`, `bearbeiter`, `zeiten`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text.fragmente`

### `editor/dokument/felder.py`
- Direkter Qt-Import: ja
- Funktionen: `vorgabe`, `_schalter`, `_ohne_schalter`, `schreibweise`, `zahl_formatieren`, `_seitenzahl`, `_zeitfeld`, `ergebnis`, `formel`, `_fehler`, `_funktion`, `_zahl`, `tabellen_bereiche`, `kontext_sammeln`, `feld_einfuegen`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.dokument.verzeichnis`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text.zahlformat`

### `editor/dokument/formular.py`
- Direkter Qt-Import: ja
- Klassen: `_Eingabe`
- Funktionen: `meta`, `meta_text`, `meta_lesen`, `_format`, `_anzeige`, `einfuegen`, `bereiche`, `feld_an`, `_ersetzen`, `wert_von`, `_klick_kasten`, `_klick_auswahl`, `_klick_datum`, `_klick_text`, `_klick_knopf`, `klick`, `_c`, `_ist_leer`, `_knopf_aktion`, `alle_zuruecksetzen`, `daten`, `nur_formulardaten`
- Interne Imports: `lunivo_writer.editor.text.fragmente`, `lunivo_writer.kern.farben`

### `editor/dokument/gehe_zu.py`
- Direkter Qt-Import: ja
- Funktionen: `_kurz`, `_tabellen`, `maximum`, `seitenstart`, `zeilenstart`, `_ziele_ueberschrift`, `_ziele_textmarke`, `_ziele_beschriftung`, `_ziele_kommentar`, `_ziele_note`, `_ziele_tabelle`, `_ziele_bild`, `_ziele_abschnitt`, `ziele`, `springen`, `_objekte`, `positionen`, `_ziel_index_leer`, `ziel`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.text.fragmente`

### `editor/dokument/indexeintrag.py`
- Direkter Qt-Import: nein
- Klassen: `Eintrag`
- Funktionen: `aus_text`, `feld`, `aus_feld`

### `editor/dokument/je_stand.py`
- Direkter Qt-Import: nein
- Funktionen: `je_stand`, `im_blick`

### `editor/dokument/literatur.py`
- Direkter Qt-Import: nein
- Funktionen: `_nachname`, `_autoren`, `zitat`, `eintrag`, `literaturverzeichnis`

### `editor/dokument/sendungen.py`
- Direkter Qt-Import: ja
- Funktionen: `umschlag_aufbauen`, `etiketten_aufbauen`, `tabelle_lesen`, `felder_im_text`, `feld_einfuegen`, `adressblock_einfuegen`, `regel_einfuegen`, `_satz_einsetzen`, `brief_fuer`, `saetze_je_brief`, `gruppen`, `serienbrief_erzeugen`, `quelle_lesen`, `zugeordnet`, `felder_hervorheben`, `naechster_einfuegen`, `_ressourcen`, `form_textfeld`, `form_kasten`, `form_knopf`, `kasten_umschalten`
- Interne Imports: `lunivo_writer.editor.text.fragmente`, `lunivo_writer.modelle.seite`

### `editor/dokument/vergleich.py`
- Direkter Qt-Import: ja
- Funktionen: `_absaetze`, `ops_bestimmen`, `_bereich`, `zusammenlegen`, `_jetzt`, `_markieren`, `_op_loeschen`, `_op_einfuegen`, `_op_absatz_einfuegen`, `anwenden`, `vergleichen`, `zusammenfuehren`
- Interne Imports: `lunivo_writer.editor.dokument.sendungen`, `lunivo_writer.editor.dokument.zusatz`

### `editor/dokument/verweise.py`
- Direkter Qt-Import: ja
- Funktionen: `seq_format`, `naechste_nummer`, `beschriftung_einfuegen`, `beschriftungen_nummerieren`, `beschriftungen_liste`, `lesezeichen_liste`, `lesezeichen_name_gueltig`, `lesezeichen_setzen`, `lesezeichen_loeschen`, `lesezeichen_gehe`, `intern_springen`, `verweisen_auf`, `_ziele_absaetze`, `_ziele_beschriftungen`, `_ziele_textmarken`, `_ziele_noten`, `querverweis_ziele`, `_seq_fragment`, `_bezeichnung_nummer`, `_beschriftungstext`, `marke_sichern`, `querverweis_text`, `querverweis_einfuegen`, `index_eintragen`, `index_markieren`, `zitat_einfuegen`, `quelle_tag`
- Interne Imports: `lunivo_writer.editor.dokument.literatur`, `lunivo_writer.editor.dokument.verzeichnis`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.editor.text.zahlformat`

### `editor/dokument/verzeichnis.py`
- Direkter Qt-Import: ja
- Funktionen: `toc_opt_text`, `toc_opt_lesen`, `toc_optionen`, `_ueberschriften`, `_toc_marke`, `_alle_toc_marken`, `_beschriftungen`, `_stichwoerter`, `_index_zeilen`, `_seiten`, `zeilen_fuer`, `_kopf_schreiben`, `_zeilenformat`, `_seite_schreiben`, `_schreibe`, `verzeichnis_einfuegen`, `_bereiche`, `verzeichnis_aktualisieren`, `vorhanden`, `_neu_schreiben`
- Interne Imports: `lunivo_writer.editor.dokument.indexeintrag`, `lunivo_writer.editor.dokument.literatur`, `lunivo_writer.editor.dokument.verweise`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.seite.seiten_aufteilung`, `lunivo_writer.editor.seite.seitenzahl`, `lunivo_writer.editor.text`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.modelle.seite`

### `editor/dokument/vorlagen.py`
- Direkter Qt-Import: ja
- Funktionen: `muster`, `_benutzer_zeilen`, `_ersetze`, `aufbauen`, `naechste_luecke`, `luecken_entfernen`, `vorlagenordner`, `rubriken`, `eigene_vorlagen`
- Interne Imports: `lunivo_writer.kern`, `lunivo_writer.plattform`

### `editor/dokument/zusatz.py`
- Direkter Qt-Import: ja
- Funktionen: `roemisch`, `neue_id`, `leere_meta`, `abstand_davor_px`, `kommentar_farbe`
- Interne Imports: `lunivo_writer.kern.farben`

### `editor/layout/__init__.py`
- Direkter Qt-Import: nein

### `editor/layout/seitenlauf.py`
- Direkter Qt-Import: ja
- Klassen: `Seitenlauf`
- Funktionen: `unterstuetzt`
- Interne Imports: `lunivo_writer.adapter.qt.dokument`, `lunivo_writer.adapter.qt.geometrie`, `lunivo_writer.adapter.qt.rendering`, `lunivo_writer.core.document.model`, `lunivo_writer.core.geometry`, `lunivo_writer.core.layout`, `lunivo_writer.core.layout.regeln`, `lunivo_writer.core.rendering`, `lunivo_writer.core.rendering.tabelle`, `lunivo_writer.core.textlayout.paragraph`, `lunivo_writer.dienste.textsatz`, `lunivo_writer.editor.layout.seitenplan`, `lunivo_writer.editor.layout.seitenplatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.seiten_aufteilung`, `lunivo_writer.editor.tabelle.tabelleneigenschaften`, `lunivo_writer.modelle.seite`

### `editor/layout/seitenplan.py`
- Direkter Qt-Import: nein
- Klassen: `Spalte`, `Bereich`, `Seitenplan`
- Funktionen: `spalten`, `gleiche_geometrie`
- Interne Imports: `lunivo_writer.editor.seite`, `lunivo_writer.modelle.seite`

### `editor/layout/seitenplatz.py`
- Direkter Qt-Import: nein
- Klassen: `Blatt`, `Zelle`, `_Stand`, `_Ergebnis`, `_KoerperPlatz`, `_FreiPlatz`
- Interne Imports: `lunivo_writer.core.geometry`, `lunivo_writer.core.textlayout.paragraph`, `lunivo_writer.editor.layout.seitenplan`, `lunivo_writer.modelle.seite`

### `editor/objekte/__init__.py`
- Direkter Qt-Import: nein

### `editor/objekte/bilddaten.py`
- Direkter Qt-Import: ja
- Klassen: `BildQuelle`
- Funktionen: `entpacken`, `merken`, `quelle_zu`, `uebernehmen`, `png_bytes`, `fuer_schreiben`, `mit_ausrichtung_lesen`, `svg_bereinigen`, `_renderer`, `_svg_groesse`, `svg_raster`, `bild_aus_svg`, `ist_svg`, `anzeigegroesse`, `zeichnen`, `platzhalter`, `bild_aus_datei`, `_aus_datei`
- Interne Imports: `lunivo_writer.adapter.qt.rendering`, `lunivo_writer.core.document.bildformat`, `lunivo_writer.core.geometry`, `lunivo_writer.core.rendering.objekte`, `lunivo_writer.dienste`, `lunivo_writer.dienste.vektor_bilder`

### `editor/objekte/bildeffekte.py`
- Direkter Qt-Import: ja
- Funktionen: `gespiegelt`, `_merken`, `_maske`, `_getoent`, `_weich`, `weiche_kanten`, `_schatten_bild`, `unter_zeichnen`, `_stufenfarbe`, `tiefe_richtung`, `extrusion_zeichnen`, `_dreht`, `hat_drehung`, `hat_nachbearbeitung`, `hat_abschluss`, `bild_nachbearbeiten`, `_projektion`, `drehung_3d`, `_erodiert`, `_band`, `_licht`, `abschluss_oben`, `abschluss_symbol`
- Interne Imports: `lunivo_writer.kern.farben`

### `editor/objekte/bildlayout.py`
- Direkter Qt-Import: ja
- Funktionen: `ziel`, `_achse_lesen`, `verschieben_wahl`, `lesen`, `_box`, `_achse_schreiben`, `_mass`, `anwenden`, `_abstand_setzen`, `_speichern_frei`, `_text_zu_frei`, `_frei_zu_text`, `format_lesen`, `fx_alle`, `format_aus_panel`, `format_setzen`, `fuellbild_setzen`, `frei_aendern`, `ausrichten`, `drehen`, `ebene`, `masse_lesen`, `masse_setzen`, `format_merken`, `format_uebertragen`, `_hoehe_je_breite`, `frei_bild_ersetzen`, `frei_original`, `frei_original_groesse`, `frei_entfernen`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.editor.seite`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`

### `editor/objekte/bildwerkzeuge.py`
- Direkter Qt-Import: ja
- Funktionen: `frei_bild`, `sperre`, `sperre_umschalten`, `farbe_transparent`, `transparent`, `aendern`, `aus_datei`, `komprimieren`, `werte`, `korrigiert`, `korrektur_setzen`, `korrektur_schritt`, `zuruecksetzen`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.bilddaten`

### `editor/objekte/bildzuschnitt.py`
- Direkter Qt-Import: ja
- Funktionen: `formen_kategorien`, `lesen`, `hat`, `anzeige`, `_quelle`, `_skalen`, `setzen`, `skala`, `skala_text`, `form`, `zuruecksetzen`, `aus_ziehen`
- Interne Imports: `lunivo_writer.editor.objekte`

### `editor/objekte/formen.py`
- Direkter Qt-Import: ja
- Funktionen: `objekt`, `ist_form`, `form_daten`, `_zeichnen`, `_gruppe_zeichnen`, `_ersetzen`, `frei_daten`, `aendern`, `vorlage`, `_auswahl_formen`, `gruppieren`, `gruppe_aufheben`, `zeichenbereich_bild`, `zeichenbereich_einfuegen`, `in_zeichenbereich`, `E_ist_linie`, `wordart_daten`, `wordart_aendern`, `anpass_griffe`, `anpass_griff`, `anpassen`, `anpass_wert`, `anpass_setzen`, `form_wechseln`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.kern.farben`

### `editor/objekte/formen_anpassen.py`
- Direkter Qt-Import: ja
- Funktionen: `_poly_pfad`, `_pt`, `_anteil`, `_rund`, `_stern`, `_pfeil`, `_doppelpfeil`, `_fuenfeckpfeil`, `_kreuz`, `_trapez`, `_parallelogramm`, `_dreieck`, `_ring`, `anpassbar`, `standard`, `_voll`, `pfad`, `griffe`, `setzen`, `wert_aus_punkt`

### `editor/objekte/formen_katalog.py`
- Direkter Qt-Import: ja
- Funktionen: `_poly`, `_vieleck`, `_stern`, `_linie`, `_kurve`, `_bogen`, `_abgerundet`, `_ellipse`, `_ring`, `_zylinder`, `_herz`, `_mond`, `_smiley`, `_wolke`, `_dokument`, `_welle`, `_fahne`, `_legende`, `_tropfen`, `_rechteck`, `namen`, `hat`, `ist_linie`, `anpassbar`, `pfad`
- Interne Imports: `lunivo_writer.editor.objekte`

### `editor/objekte/formen_stile.py`
- Direkter Qt-Import: ja
- Funktionen: `formstil`, `formstile_raster`
- Interne Imports: `lunivo_writer.editor.objekte`

### `editor/objekte/frei_objekt.py`
- Direkter Qt-Import: ja
- Funktionen: `_form_zeichnen`, `_diagramm_zeichnen`, `_smartart_zeichnen`, `_piktogramm_zeichnen`, `_zeichenbereich_zeichnen`, `zeichnen`, `_anzeige_mass`, `einfuegen`, `bild_einfuegen`, `ziel`, `art_gewaehlt`, `daten_lesen`, `aendern`, `_daten_vorbereiten`, `_form_daten_setzen`, `_kasten_setzen`, `_eintrag_setzen`, `_bild_erneuern`, `_aendern_innen`, `daten_still`, `nach_groesse`, `text_bereich`, `_fmt_unter`, `_fmt_hoch_tief`, `_fmt_schrift`, `_fmt_pt`, `_format_aus_kw`, `_lauf_schnitt`, `_lauf_farben`, `_lauf_schrift`, `_lauf_aus_format`, `_basis`, `_widget_laeufe`, `_edit_laden`, `_edit_stil`, `edit_platzieren`, `bearbeiten_starten`, `auswahl_daten`, `edit_uebernehmen`, `bearbeiten_beenden`, `text_werte_lesen`, `text_werte_anwenden`, `_textfelder`, `_speichern_angabe`, `_neu_setzen`, `_kette_ohne`, `_verknuepfbar`, `_text_uebernehmen`, `verknuepfen`, `loesen`, `ist_verknuepft`, `_kette_glieder`, `_kette_verteilen`, `kette_aktualisieren`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.editor.dokument`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.frei_objekt_text`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.editor.text.mehrstufig`, `lunivo_writer.editor.text.unterstreichung`

### `editor/objekte/frei_objekt_text.py`
- Direkter Qt-Import: ja
- Funktionen: `listenmarken`, `richtung_anwenden`, `_gedreht`, `effekte_auf_text`, `anzeige_laeufe`, `laeufe_text`, `laeufe_ab`, `laeufe_zusammen`, `_zeilen_laeufe`, `_wa_stil`, `_wa_format`, `_wa_schrift`, `_wa_segmente`, `_wa_masse`, `_wa_effekte`, `_wa_verteilt`, `_wa_text_pfad`, `_wa_zeile`, `_wa_dekoration`, `_wa_glut_schatten`, `_wa_fuellen`, `_wa_spiegeln`, `wordart_zeichnen`, `_zeichenformat`, `_zeichen_unterstrich`, `_zeichen_schrift`, `_zeichen_farbe`, `_innen`, `_textdoc`, `_text_passt`, `_text_malen`, `_zeilenbaender`, `textfeld_zeichnen`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.bildeffekte`, `lunivo_writer.editor.text.mehrstufig`, `lunivo_writer.editor.text.textfx`, `lunivo_writer.editor.text.unterstreichung`

### `editor/objekte/freie_bilder.py`
- Direkter Qt-Import: ja
- Funktionen: `emu_zu_px`, `aus_absatz`, `an_absatz`, `hat_bilder`, `bild_im_dokument`, `neuer_name`, `_zu_gross`, `bild_aus_daten`, `farbe_aus_element`, `duoton`, `rechteck`, `fuell_pinsel`, `_stift`, `_text_gerade`, `_png_daten`, `_ueber_backend`, `bild_zeichnen`, `koerper_index`, `objekte_der_seite`, `versatz_fuer`, `ohne_hilfsangaben`, `vorne_hinten`
- Interne Imports: `lunivo_writer.adapter.qt.geometrie`, `lunivo_writer.adapter.qt.rendering`, `lunivo_writer.core.document.objekte`, `lunivo_writer.core.geometry`, `lunivo_writer.core.layout.objekte`, `lunivo_writer.core.rendering.objekte`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.linie`, `lunivo_writer.editor.text`, `lunivo_writer.editor.text.textur`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`

### `editor/objekte/freiform.py`
- Direkter Qt-Import: ja
- Funktionen: `innen`, `aus_pfad`, `aus_form`, `pfad`, `geschlossen`, `rollen`, `knoten`, `_teil`, `verschieben`, `loeschen`, `_kubisch`, `_kanten`, `naechste_kante`, `einfuegen`
- Interne Imports: `lunivo_writer.editor.objekte`

### `editor/objekte/linie.py`
- Direkter Qt-Import: ja
- Klassen: `Linie`
- Funktionen: `_bauen`, `docx_wert`, `art_aus_docx`
- Interne Imports: `lunivo_writer.adapter.qt.rendering`, `lunivo_writer.core.geometry`, `lunivo_writer.core.rendering.linien`, `lunivo_writer.kern.farben`

### `editor/objekte/smartart.py`
- Direkter Qt-Import: ja
- Funktionen: `punkte`, `knoten_aus_text`, `_glatt`, `knoten_von`, `text_aus_knoten`, `_knotentext`, `_neue_id`, `_index`, `_ende`, `_geschwister`, `form_einfuegen`, `kann_level`, `level`, `kann_verschieben`, `verschieben`, `aufzaehlung`, `zeichnen_mit_knoten`, `zeichnen`, `knoten_rechtecke`, `katalogeintrag`, `neue_daten`, `einfuegen`, `_inline_daten`, `daten_der_auswahl`, `_text_gegen_knoten`, `_inline_aendern`, `aendern`, `knoten_gewaehlt`, `knoten_waehlen`, `_im_objekt`, `_knoten_rechtecke_gemerkt`, `knoten_bei`, `knoten_text`, `knoten_text_setzen`, `_knoten_schreiben`, `_format_mischen`, `format_lesen`, `format_setzen`, `befehl_form`, `befehl_level`, `befehl_verschieben`, `befehl_aufzaehlung`, `kann`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.kern.farben`

### `editor/objekte/smartart_zeichnen.py`
- Direkter Qt-Import: ja
- Funktionen: `_format_von`, `_spiegel`, `_merke`, `_farbe`, `_stilfarbe`, `_text_farbe`, `_fuellen`, `_text_zeichnen`, `_schrift`, `_kasten`, `_kasten_format`, `_pinsel_setzen`, `_pfeil`, `_bild`, `_text`, `_gruppen`, `_bunt`, `_spalten`, `_gruppenliste`, `_matrix`, `_chevron`, `_radial`, `_zielscheibe`, `_trichter`, `_zeitachse`, `_stufen`, `_baum`, `_alle`, `_standard_baum`, `_haengend_baum`, `_organigramm`, `_liste`, `_prozess`, `_zyklus`, `_pyramide`, `_eintraege`, `_merke_mehrere`, `_zeilen`, `_blockraster`, `_punktliste`, `_balkenliste`, `_beschreibungsliste`, `_spaltenrahmen`, `_bildliste`, `_perspektive`, `_konvergenz`, `_kartenprozess`, `_kreisbeziehung`, `_segmentzyklus`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.editor.objekte.smartart`, `lunivo_writer.kern.farben`

### `editor/objekte/sprechblasen.py`
- Direkter Qt-Import: ja
- Klassen: `Blase`
- Funktionen: `konfig_lesen`, `breite_mm`, `aktiv`, `autor_farbe`, `_kuerzen`, `sammeln`, `_kopf`, `blasen_px`, `karten_pt`, `messen`, `stapeln`, `_ortszeit`, `menue_rect`, `zeichnen`, `verbindung`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text.fragmente`

### `editor/seite/__init__.py`
- Direkter Qt-Import: nein

### `editor/seite/absatzopt.py`
- Direkter Qt-Import: nein
- Funktionen: `lesen`, `setzen`, `als_text`, `aus_text`, `in_ppr`, `aus_ppr`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`

### `editor/seite/abschnitte.py`
- Direkter Qt-Import: ja
- Funktionen: `_bilder_zu_text`, `_bilder_aus_text`, `seite_zu_dict`, `seite_aus_dict`, `eintrag`, `lesen`, `umbrueche`, `anzahl`, `index_bei`, `einrichtung`, `alle_einrichtungen`, `beginn`, `ende`, `_setze`, `einfuegen`, `einfuegen_an`, `entfernen`, `setzen`, `teile`
- Interne Imports: `lunivo_writer.editor.layout.seitenplan`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.seite.wasserzeichen`, `lunivo_writer.modelle.seite`

### `editor/seite/anzeige_extra.py`
- Direkter Qt-Import: ja
- Klassen: `VersteckterText`
- Funktionen: `_bereiche`, `versteckte_entfernen`, `feldcodes_einsetzen`, `feldbereiche`, `zeichnungen_entfernen`, `aenderungszeilen`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.kern.farben`

### `editor/seite/blasen_druck.py`
- Direkter Qt-Import: ja
- Funktionen: `blasen_geometrie`, `blasen_pro_seite`, `blasen_zeichnen`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.editor.seite.pdf_struktur`, `lunivo_writer.modelle.seite`

### `editor/seite/deckblatt.py`
- Direkter Qt-Import: ja
- Klassen: `Feld`, `Gestaltung`
- Funktionen: `_kontakt`, `_arbeit`, `gestaltung`, `_stil`, `_verlauf`, `_flaeche`, `_wolken`, `_dreieck`, `_segelboot`, `_puzzle`, `_blume`, `_g_mosaik`, `_g_himmel`, `_g_sonne`, `_g_kopfbalken`, `_g_wellen`, `_g_blaurand`, `_g_stadt`, `_g_notizzettel`, `_g_sonnenblume`, `_g_gruen`, `_g_puzzle`, `_g_segel`, `_g_rahmen`, `_g_linien`, `_g_siegel`, `_grafik`, `_schrift`, `zeichnen_mit`, `zeichnen`, `grafik_bild`, `hat_deckblatt`, `entfernen`, `einfuegen`, `_bild_text`
- Interne Imports: `lunivo_writer.adapter.qt.geometrie`, `lunivo_writer.adapter.qt.rendering`, `lunivo_writer.core.geometry`, `lunivo_writer.core.rendering`, `lunivo_writer.core.textlayout`, `lunivo_writer.dienste.textsatz`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.wasserzeichen`, `lunivo_writer.modelle.seite`

### `editor/seite/druck.py`
- Direkter Qt-Import: ja
- Klassen: `Zwischenseiten`
- Funktionen: `papier_name`, `bereich_lesen`, `seiten_nach_wahl`, `blatt_zeichnen`, `optionen_aus`, `zwischen_pdf`, `pdf_seiten_bilder`, `vorschau_bild`, `drucken`
- Interne Imports: `lunivo_writer.editor.seite.seiten_aufteilung`

### `editor/seite/fussnoten.py`
- Direkter Qt-Import: ja
- Funktionen: `fussnoten_am_fuss`, `_notenfragmente`, `_notenabschnitt`, `noten_anhaengen`, `_fussnoten_stellen`, `zeilenbereiche`, `_notenschrift`, `_notendoc_fabrik`, `_notenhoehe`, `_belegung`, `_erste_zeile_ohne_platz`, `_zu_hohe_zeile`, `_seitenwechsel_vor`, `_platzierung`, `fussnoten_am_seitenende`, `_notenmarken`, `_notenziele`, `notenlinks_sammeln`
- Interne Imports: `lunivo_writer.core.layout.seitenumbruch`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.seite.pdf_struktur`, `lunivo_writer.editor.seite.seitenzahl`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.modelle.seite`

### `editor/seite/leere_seite.py`
- Direkter Qt-Import: ja
- Funktionen: `_umbruch_davor`, `leere_seite`
- Interne Imports: `lunivo_writer.editor.seite`, `lunivo_writer.modelle.seite`

### `editor/seite/lese_zeilenluft.py`
- Direkter Qt-Import: ja
- Funktionen: `_markiert`, `aktiv`, `_zuruecksetzen`, `_durchlaufen`, `zuruecknehmen`, `bereinigte_kopie`, `anwenden`

### `editor/seite/pdf_struktur.py`
- Direkter Qt-Import: ja
- Funktionen: `fluss_ort`, `_erste_kommentarstellen`, `kommentarstellen`, `_blockseite`, `_stilname`, `_ist_stileintrag`, `_textmarken_anhaengen`, `_block_eintraege`, `lesezeichen_sammeln`, `_rand_pt`, `_notizen_anfuegen`, `_verweis_anfuegen`, `_verweise_anfuegen`, `_gliederung_anfuegen`, `gliederung_schreiben`
- Interne Imports: `lunivo_writer.dienste.docx_leser`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.seite.seitenzahl`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.modelle.seite`

### `editor/seite/querblatt.py`
- Direkter Qt-Import: ja
- Funktionen: `rechts_px`, `rechts_setzen`, `_geometrie`, `einrichtungen`, `aktiv`, `masse`, `_abschnitt_je_block`, `_setzen`, `breite_anwenden`, `zuruecknehmen`, `bereinigte_kopie`, `hat_zusatz`, `blattplan`, `_am_seitenanfang`, `_zu_hoch_fuer_blatt`, `grenzen`
- Interne Imports: `lunivo_writer.editor.seite`, `lunivo_writer.modelle.seite`

### `editor/seite/seiten_aufteilung.py`
- Direkter Qt-Import: ja
- Klassen: `_Lauf`, `_Folge`
- Funktionen: `layout_device`, `zoom_device`, `bind_layout`, `ausgabe_seiten`, `paginated_copy`, `_abschnittsbeginn_markieren`, `page_count`, `_start_nummer`, `_kapitel_liste`, `_kapitel_von`, `_nur_formular`, `_inhalt_anpassen`, `_darstellung_anpassen`, `_ausgabekopie`, `_seitenliste`, `_lauf_vorbereiten`, `_seite_ausgeben`, `_pdf_ergebnisse`, `render`, `_leerseite_davor`, `_leerseiten_plan`, `_erste_nummern`, `_startteil`, `_papier_wechseln`, `_abschnitt_drucken`, `render_dokument`, `_blattweise`, `_blatt_zeichnen`, `_gesetzt`, `_blatt_liste`, `render_blaetter`, `_frei_index`, `_kopf_fuss_zeichnen`, `_zeilennummern_zeichnen`, `_fussnoten_zeichnen`, `_spalte_zeichnen`, `_fussnoten_trennlinie`, `_balken_stil`, `_aenderungsbalken`, `_balken_blatt`, `_spaltenlinien_zeichnen`, `zeichne_seite`, `seite_als_bild`, `seitenzahl`, `seiten_bilder`, `_leere_seiten`, `_page_layout`, `_quer`, `_xmp_autor`, `_pdf_schreiber`, `export_pdf`, `print_document`
- Interne Imports: `lunivo_writer.adapter.qt.dokument`, `lunivo_writer.adapter.qt.pdf_modell`, `lunivo_writer.adapter.qt.rendering`, `lunivo_writer.adapter.qt.seitenbild`, `lunivo_writer.core.document`, `lunivo_writer.core.geometry`, `lunivo_writer.core.layout`, `lunivo_writer.core.rendering`, `lunivo_writer.dienste.textsatz`, `lunivo_writer.editor.dokument.formular`, `lunivo_writer.editor.dokument.vorlagen`, `lunivo_writer.editor.layout.seitenlauf`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.anzeige_extra`, `lunivo_writer.editor.seite.blasen_druck`, `lunivo_writer.editor.seite.fussnoten`, `lunivo_writer.editor.seite.pdf_struktur`, `lunivo_writer.editor.seite.seiten_aufteilung_deko`, `lunivo_writer.editor.seite.seitenzahl`, `lunivo_writer.editor.seite.silbentrennung`, `lunivo_writer.editor.text.silbenfarben`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`

### `editor/seite/seiten_aufteilung_deko.py`
- Direkter Qt-Import: ja
- Funktionen: `_expand`, `_draw_hf`, `_hf_schrift`, `_laeufe_eigen`, `_zeichne_laeufe`, `_hf_effekt`, `_ohne_hintergruende`, `_text_schwarz`, `_formularteile_ausblenden`, `_ohne_hervorhebungen`, `_ohne_links`, `_textmarken_klammern`, `_bf_ohne`, `seitenschmuck`, `seiten_liste`, `frei_zeichnen`, `_druckmarken`, `_inhalt_zeichnen`, `absatz_zusatz_zeichnen`, `_rahmengruppen`, `_rahmengruppen_bauen`, `_rahmenrechteck`, `absatzrahmen_zeichnen`
- Interne Imports: `lunivo_writer.adapter.qt.rendering`, `lunivo_writer.core.geometry`, `lunivo_writer.core.rendering`, `lunivo_writer.core.rendering.seitenschmuck`, `lunivo_writer.dienste.textsatz`, `lunivo_writer.editor.dokument`, `lunivo_writer.editor.dokument.je_stand`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.linie`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.text`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.editor.text.mehrstufig`, `lunivo_writer.editor.text.tabfuell`, `lunivo_writer.editor.text.textfx`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`

### `editor/seite/seitenfluss.py`
- Direkter Qt-Import: ja
- Klassen: `_Schritt`
- Funktionen: `seitenraster`, `_von_oben`, `fertig_setzen`, `ist_manuell`, `_zeilen`, `_hoehe`, `_zeilen_auf`, `_zerrissen`, `_vom_naechsten_getrennt`, `_verletzt`, `_gesetzte`, `_oben_auf_seite`, `_vorabstand_pruefen`, `_seitenanfang`, `_hat_umbruch`, `_alte_umbrueche_entfernen`, `_braucht_umbruch`, `_umbruchstellen`, `_umbrueche_setzen`, `anwenden`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.seite`, `lunivo_writer.modelle.seite`

### `editor/seite/seitenrahmen.py`
- Direkter Qt-Import: ja
- Funktionen: `rechteck`, `zeichnen`
- Interne Imports: `lunivo_writer.adapter.qt.rendering`, `lunivo_writer.core.geometry`, `lunivo_writer.core.rendering.seitenrahmen`

### `editor/seite/seitenzahl.py`
- Direkter Qt-Import: nein
- Funktionen: `_ohne_zahl`, `seitenzahl_setzen`, `seitenzahlen_entfernen`, `seitenzahl_loeschen_bereich`, `nummer`, `text`, `ausrichtung`, `erste_nummer`, `absatz_oben`, `seitenwechsel`, `_kapitel_nummer`, `kapitel_je_seite`
- Interne Imports: `lunivo_writer.editor.text.mehrstufig`, `lunivo_writer.modelle.seite`

### `editor/seite/silbentrennung.py`
- Direkter Qt-Import: ja
- Funktionen: `_trenner`, `_trennstellen`, `_einfuegen`, `silben_einfuegen`

### `editor/seite/umbruch.py`
- Direkter Qt-Import: ja
- Funktionen: `_rahmen`, `schwebende_rahmen`, `schwebend`, `bild_im_rahmen`, `ist_anker`, `schwebend_einfuegen`, `absatz_nach_rahmen`, `schwebend_entfernen`, `umbruch_setzen`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text.fragmente`

### `editor/seite/wasserzeichen.py`
- Direkter Qt-Import: ja
- Funktionen: `da`, `bild_zu_text`, `bild_aus_text`, `ausgewaschen`, `_deckkraft`, `_lage`, `schrift`, `zeichnen`
- Interne Imports: `lunivo_writer.adapter.qt.rendering`, `lunivo_writer.core.geometry`, `lunivo_writer.core.rendering.wasserzeichen`, `lunivo_writer.dienste.textsatz`, `lunivo_writer.modelle.seite`

### `editor/seite/zeilennummern.py`
- Direkter Qt-Import: ja
- Funktionen: `unterdrueckt`, `nummern`, `zeichnen`
- Interne Imports: `lunivo_writer.editor.seite`

### `editor/tabelle/__init__.py`
- Direkter Qt-Import: nein

### `editor/tabelle/tabelle_text.py`
- Direkter Qt-Import: ja
- Funktionen: `markierte_absaetze`, `zellen`, `text_zu_tabelle`, `_zelle_text`, `_tabelle_zeilen`, `tabelle_zu_text`

### `editor/tabelle/tabelleneigenschaften.py`
- Direkter Qt-Import: ja
- Funktionen: `lesen`, `anwenden`, `optionen_lesen`, `optionen_setzen`, `_loesch_bereich`, `_zeile_spalte_loeschen`, `_zellen_verschieben`, `zellen_loeschen`, `_verbundene_teilen`, `_spalten_dazu`, `_zeilen_dazu`, `zelle_teilen`, `zeilenhoehe_setzen`, `zeilenhoehe_lesen`, `an_inhalt_anpassen`, `_zoom`, `_zellen_der_zeile`, `_textHoehe`, `_zeilen_oberkanten`, `_unterkante`, `tabelle_basis`, `zeilengrenzen`, `zeilen_mindesthoehe`, `_zeile_setzen`, `zeile_hoehe_ziehen`, `_zeilen_setzen`, `_zellen_der_zeile_alle`, `skalierungs_kosten`, `tabelle_skalieren_spalten`, `tabelle_skalieren_zeilen`, `tabelle_skalieren`, `spalten_gleich`, `zeilen_gleich`, `spalten_festschreiben`, `linie_loeschen`
- Interne Imports: `lunivo_writer.modelle.seite`

### `editor/tabelle/tabellenstil.py`
- Direkter Qt-Import: ja
- Funktionen: `_zellen`, `_fett`, `_zeilengrund`, `anwenden`
- Interne Imports: `lunivo_writer.kern.farben`

### `editor/tabelle/tabellenzustand.py`
- Direkter Qt-Import: nein
- Funktionen: `zustand`, `tabellenmodus`

### `editor/text/__init__.py`
- Direkter Qt-Import: nein

### `editor/text/auswahl.py`
- Direkter Qt-Import: ja
- Funktionen: `_tabellen`, `ohne_rahmen`, `tabelle_ohne_rahmen`, `_merkmale`, `aehnlich_formatiert`
- Interne Imports: `lunivo_writer.editor.text.fragmente`

### `editor/text/designs.py`
- Direkter Qt-Import: nein
- Funktionen: `ueberschrift_farbe`, `design`

### `editor/text/fragmente.py`
- Direkter Qt-Import: ja
- Funktionen: `absatz_fragmente`, `dokument_fragmente`

### `editor/text/ki_markdown.py`
- Direkter Qt-Import: ja
- Klassen: `_Zustand`
- Funktionen: `normalisieren`, `dokument`, `_zeichen_besonders`, `hat_struktur`, `_tabellen`, `klartext`, `_basis_zeichen`, `_inline`, `_aus_liste`, `_fliesstext_format`, `_block_bereit`, `_listenart`, `_liste_zuordnen`, `_tabelle`, `einfuegen`
- Interne Imports: `lunivo_writer.editor.text`, `lunivo_writer.editor.text.fragmente`

### `editor/text/listen.py`
- Direkter Qt-Import: ja
- Funktionen: `zeichen_filtern`, `liste`, `marke`, `zu_format`, `aus_format`, `als_text`, `aus_text`
- Interne Imports: `lunivo_writer.editor.text.mehrstufig`

### `editor/text/mehrstufig.py`
- Direkter Qt-Import: ja
- Funktionen: `nummer_text`, `ebene`, `ebene_aus`, `aufzaehlung`, `ist_aufzaehlung`, `als_mehrstufig`, `gliederung`, `_alle`, `als_text`, `aus_text`, `block_wert`, `aus_block`, `nummer_der_ebene`, `zaehlen`, `nummern`, `_nummern_bauen`, `_marker_font`, `_text_breite`, `einrichten_alle`, `nummern_zeichnen`
- Interne Imports: `lunivo_writer.editor.dokument.je_stand`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text.listen`, `lunivo_writer.modelle.seite`

### `editor/text/muster.py`
- Direkter Qt-Import: ja
- Funktionen: `_pct_name`, `name_von`, `ooxml_von`, `schluessel_von_ooxml`, `_an`, `kachel`, `pinsel`, `als_text`, `aus_text`
- Interne Imports: `lunivo_writer.kern.farben`

### `editor/text/schreibweise.py`
- Direkter Qt-Import: ja
- Funktionen: `umwandeln`, `_zahl`, `_datum`, `sortiert`, `felder`, `feldzahl`, `reihenfolge`, `absaetze`, `umstellen`

### `editor/text/silbenfarben.py`
- Direkter Qt-Import: ja
- Klassen: `SilbenFarben`
- Funktionen: `konfig_lesen`, `konfig_speichern`, `farben`, `verfuegbar`, `silben`, `_formate`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.korrektur.silben_de`

### `editor/text/statistik.py`
- Direkter Qt-Import: nein
- Funktionen: `texte_des_dokuments`, `zaehlen`

### `editor/text/stile.py`
- Direkter Qt-Import: nein
- Funktionen: `namen`, `ist_eigen`, `laden_neu`, `_meta`, `als_json_neu`, `pruefe_name`, `anlegen`, `loeschen`, `laden`, `als_json`, `definition`, `aendern`, `zuruecksetzen`, `name_zu_key`, `key_zu_name`

### `editor/text/suche.py`
- Direkter Qt-Import: ja
- Klassen: `Suchauftrag`
- Funktionen: `_zeichen_kennzeichen`, `_umbruch_kennzeichen`, `roh_text`, `_woertlich`, `_klammer`, `_platzhalter`, `_ignoriert`, `muster`, `gueltig`, `_zeichen_passen`, `_nur_format`, `treffer`, `naechster`, `ersatz_text`, `ersetzen`, `_umbruch_weg`, `alle_ersetzen`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.seite.abschnitte`, `lunivo_writer.editor.text.fragmente`

### `editor/text/tabfuell.py`
- Direkter Qt-Import: ja
- Funktionen: `lesen`, `setzen`, `aus_docx`, `_tabstrecken`, `_strecke_fuellen`, `_absatz_zeichnen`, `zeichnen`, `_absaetze_mit_fuellung`
- Interne Imports: `lunivo_writer.editor.dokument.je_stand`, `lunivo_writer.editor.dokument.zusatz`

### `editor/text/textdaten.py`
- Direkter Qt-Import: ja
- Funktionen: `_stueck`, `fragment_zu_daten`, `daten_zu_fragment`
- Interne Imports: `lunivo_writer.editor.text.fragmente`

### `editor/text/texteffekt.py`
- Direkter Qt-Import: ja
- Funktionen: `strich_setzen`, `zu_format`, `_fuellart_ableiten`, `_kontur_aus_stift`, `aus_format`, `als_text`, `aus_text`, `_q`, `_farbelement`, `_verlauf_element`, `_rpr_leuchten`, `_rpr_schatten`, `_rpr_reflektion`, `_rpr_kontur`, `_rpr_fuellung`, `_rpr_3d`, `in_rpr`, `_wert`, `_farbe_aus`, `_verlauf_aus`, `_kontur_aus`, `_fuellung_aus`, `_leuchten_schatten_aus`, `_reflektion_3d_aus`, `aus_rpr`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`

### `editor/text/textfx.py`
- Direkter Qt-Import: ja
- Funktionen: `_farbe`, `hat_effekt`, `als_text`, `aus_text`, `_verlauf`, `fuell_pinsel_von`, `_warp_y`, `_drehen_3d`, `_augenabstand`, `_polygon_verformen`, `pfad_verformen`, `_weich`, `_richtung`, `_helligkeit`, `_normale`, `_linienzug_versetzt`, `_versetzt`, `_kontur_pfade`, `_basisname`, `_fx_reflektion`, `_tiefe_faktor`, `_tiefe_farbe`, `_fx_3d`, `_fx_schatten_aussen`, `_fx_leuchten`, `_fx_fuellung`, `_fx_schatten_innen`, `_fx_kontur`, `fx_zeichnen`, `_fx_hinter`, `_fx_ueber`, `text_pfad`, `vorschau_zeichnen`
- Interne Imports: `lunivo_writer.editor.diagramme.diagramm_format`, `lunivo_writer.editor.text`, `lunivo_writer.editor.text.texteffekt`, `lunivo_writer.editor.text.textfx_vorgaben`, `lunivo_writer.editor.text.textfx_zeichen`, `lunivo_writer.editor.text.textur`, `lunivo_writer.kern.farben`

### `editor/text/textfx_vorgaben.py`
- Direkter Qt-Import: ja
- Funktionen: `schatten_vorgaben`, `reflektion_vorgaben`, `leuchten_vorgaben`, `voreinstellung_icon`, `text_kachel_icon`, `form_kachel_icon`, `wordart_vorgaben`, `wordart_icon`
- Interne Imports: `lunivo_writer.editor.text.textfx`, `lunivo_writer.kern.farben`

### `editor/text/textfx_zeichen.py`
- Direkter Qt-Import: ja
- Funktionen: `_woerter`, `_unterstrich`, `unter_zeichnen`, `unter_symbol`, `_doppelt_durch`, `_betonung`, `absaetze_zeichnen`, `_absaetze_mit_effekt`, `_P`, `hat_zeichen_effekt`, `_glyphlauf`, `_zeilenpfad`, `_textfarbe`, `_kontur_von`, `_unter_zeichnen_stueck`, `_zusaetze_zeichnen`, `_zeile_zeichnen`, `_stueck`, `_umschlossen`, `_ruby`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.dokument.je_stand`, `lunivo_writer.editor.text`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.editor.text.textfx`, `lunivo_writer.kern.farben`

### `editor/text/textur.py`
- Direkter Qt-Import: ja
- Funktionen: `textur`

### `editor/text/unterstreichung.py`
- Direkter Qt-Import: ja
- Funktionen: `unter_format`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`

### `editor/text/wortextras.py`
- Direkter Qt-Import: ja
- Funktionen: `_bloecke`, `_leer`, `_schritt`, `leere_loeschen`, `leere_einfuegen`, `zeilenumbruch_in_return`, `absaetze_neu_anordnen`, `leerzeichen_bereinigen`, `einzug_zwei_zeichen`, `smart_anordnen`, `fuehrende_leerzeichen_loeschen`, `zeilenumbrueche_loeschen`, `leerabsatz_modus_wechseln`, `einzug_in_leerzeichen`

### `editor/text/zahlformat.py`
- Direkter Qt-Import: nein
- Funktionen: `_buchstaben`, `_unter_tausend`, `zahlwort`, `grenzen`, `zahl_text`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`

### `editor/text/zeichenzusatz.py`
- Direkter Qt-Import: nein
- Funktionen: `umschlossen_text`, `umschlossen_lesen`, `ruby_text`, `ruby_lesen`

### `kern/__init__.py`
- Direkter Qt-Import: nein

### `kern/anwendung.py`
- Direkter Qt-Import: ja
- Klassen: `LunivoApplication`
- Funktionen: `programm_symbol`
- Interne Imports: `lunivo_writer.dienste.einstellungen_dienst`, `lunivo_writer.kern.pfade`, `lunivo_writer.oberflaeche`, `lunivo_writer.oberflaeche.baukasten.geruest.zugaenglichkeit`, `lunivo_writer.oberflaeche.programmfenster`, `lunivo_writer.oberflaeche.thema`, `lunivo_writer.plattform`

### `kern/befehle/__init__.py`
- Direkter Qt-Import: nein

### `kern/befehle/hauptreiter/__init__.py`
- Direkter Qt-Import: nein

### `kern/befehle/hauptreiter/ansicht.py`
- Direkter Qt-Import: ja
- Klassen: `AnsichtBefehle`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.text`, `lunivo_writer.oberflaeche.band.band_leiste`, `lunivo_writer.oberflaeche.dialoge.dokument_dialoge`, `lunivo_writer.oberflaeche.dialoge.lesen_hilfe`, `lunivo_writer.oberflaeche.dialoge.lesen_hilfe.lesehilfe_dialog`, `lunivo_writer.oberflaeche.dialoge.lesen_hilfe.silben_dialog`, `lunivo_writer.oberflaeche.dialoge.oberflaeche_dialoge`

### `kern/befehle/hauptreiter/bearbeiten.py`
- Direkter Qt-Import: ja
- Klassen: `BearbeitenBefehle`
- Interne Imports: `lunivo_writer.editor.text`, `lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.felder.auswahl_bereich`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.bauteile`

### `kern/befehle/hauptreiter/datei.py`
- Direkter Qt-Import: ja
- Klassen: `DateiBefehle`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`

### `kern/befehle/hauptreiter/einfuegen.py`
- Direkter Qt-Import: ja
- Klassen: `EinfuegenBefehle`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.editor.dokument`, `lunivo_writer.editor.dokument.verzeichnis`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.bilddaten`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.leere_seite`, `lunivo_writer.editor.tabelle`, `lunivo_writer.kern.befehle.hauptreiter.einfuegen_objekte`, `lunivo_writer.kern.befehle.hilfen`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.bericht`, `lunivo_writer.oberflaeche.baukasten.basis`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.raster_auswahl`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.zellen_raster`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.medien.bildformate`, `lunivo_writer.oberflaeche.baukasten.medien.datei_symbole`, `lunivo_writer.oberflaeche.baukasten.medien.seiten_bildchen`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dialoge.einfuegen.einfuegen_fenster`, `lunivo_writer.oberflaeche.dialoge.einfuegen.sonderzeichen`, `lunivo_writer.oberflaeche.dialoge.einfuegen.wasserzeichen_fenster`, `lunivo_writer.oberflaeche.dialoge.verweise.verweise_fenster`, `lunivo_writer.oberflaeche.dokument.tabelle.tabelle_radierer`, `lunivo_writer.oberflaeche.dokument.tabelle.tabelle_stift`

### `kern/befehle/hauptreiter/einfuegen_objekte.py`
- Direkter Qt-Import: ja
- Klassen: `EinfuegenObjektBefehle`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.editor.dokument`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.seite`, `lunivo_writer.kern.befehle.hilfen`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.bericht`, `lunivo_writer.oberflaeche.baukasten.basis`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.raster_auswahl`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.dialoge.einfuegen.bildschirmfoto`, `lunivo_writer.oberflaeche.dialoge.einfuegen.einfuegen_dialoge`, `lunivo_writer.oberflaeche.dialoge.einfuegen.smartart_dialog_foto`

### `kern/befehle/hauptreiter/ki.py`
- Direkter Qt-Import: ja
- Klassen: `KIBefehle`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.oberflaeche.baukasten.dokument.aenderungs_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.dialoge.ki.ki_dialoge`

### `kern/befehle/hauptreiter/kommentare.py`
- Direkter Qt-Import: ja
- Klassen: `KommentarBefehle`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster`

### `kern/befehle/hauptreiter/pruefen.py`
- Direkter Qt-Import: ja
- Klassen: `PruefenBefehle`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.editor.dokument`, `lunivo_writer.editor.dokument.sendungen`, `lunivo_writer.editor.text`, `lunivo_writer.korrektur.barrierefreiheit`, `lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.dialoge.einfuegen.formular_dialog`, `lunivo_writer.oberflaeche.dialoge.sendungen.sendungen_dialoge`, `lunivo_writer.oberflaeche.dialoge.ueberpruefen_fenster`

### `kern/befehle/hauptreiter/seite.py`
- Direkter Qt-Import: ja
- Klassen: `SeiteBefehle`
- Funktionen: `_abschnitt_wasserzeichen`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.silbentrennung`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.farbpalette`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.raster_auswahl`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.formatierung.schriftart_dialog`, `lunivo_writer.oberflaeche.baukasten.formatierung.text_format`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.baukasten.medien.design_bildchen`, `lunivo_writer.oberflaeche.baukasten.medien.seiten_bildchen`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dialoge.dokument_dialoge`, `lunivo_writer.oberflaeche.dialoge.einfuegen.wasserzeichen_fenster`

### `kern/befehle/hauptreiter/serien.py`
- Direkter Qt-Import: ja
- Klassen: `SerienBefehle`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.editor.dokument`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.dialoge.sendungen.serien_fenster`, `lunivo_writer.oberflaeche.dokument.ansicht`

### `kern/befehle/hauptreiter/text.py`
- Direkter Qt-Import: nein
- Klassen: `TextBefehle`
- Interne Imports: `lunivo_writer.kern.befehle.hauptreiter.text_absatz`, `lunivo_writer.kern.befehle.hauptreiter.text_vorlagen`, `lunivo_writer.kern.befehle.hauptreiter.text_zeichen`

### `kern/befehle/hauptreiter/text_absatz.py`
- Direkter Qt-Import: ja
- Klassen: `TextAbsatzBefehle`
- Interne Imports: `lunivo_writer.editor.objekte.linie`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten`, `lunivo_writer.oberflaeche.baukasten.basis`, `lunivo_writer.oberflaeche.baukasten.dokument.liste_dialog`, `lunivo_writer.oberflaeche.baukasten.dokument.sortieren_dialog`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.formatierung.rahmen_schattierung`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`

### `kern/befehle/hauptreiter/text_vorlagen.py`
- Direkter Qt-Import: ja
- Klassen: `TextVorlagenBefehle`
- Interne Imports: `lunivo_writer.editor.objekte.linie`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten`, `lunivo_writer.oberflaeche.baukasten.basis`, `lunivo_writer.oberflaeche.baukasten.formatierung.formatvorlage_dialog`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`

### `kern/befehle/hauptreiter/text_zeichen.py`
- Direkter Qt-Import: ja
- Klassen: `TextZeichenBefehle`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte.linie`, `lunivo_writer.editor.text`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.editor.text.textfx`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten`, `lunivo_writer.oberflaeche.baukasten.basis`, `lunivo_writer.oberflaeche.baukasten.basis.linien`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.dropdown.voreinstellung_menue`, `lunivo_writer.oberflaeche.baukasten.formatierung.ruby_dialog`, `lunivo_writer.oberflaeche.baukasten.formatierung.schreibweise_dialog`, `lunivo_writer.oberflaeche.baukasten.formatierung.text_format`, `lunivo_writer.oberflaeche.baukasten.formatierung.texteffekt_dialog`, `lunivo_writer.oberflaeche.baukasten.formatierung.umschlossen_dialog`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.baukasten.vorlagen.formatvorlagen_bereich`, `lunivo_writer.oberflaeche.bauteile`

### `kern/befehle/hauptreiter/ueberpruefen.py`
- Direkter Qt-Import: ja
- Klassen: `UeberpruefenBefehle`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.objekte`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dialoge.ueberpruefen_fenster`, `lunivo_writer.oberflaeche.dokument.ansicht`

### `kern/befehle/hauptreiter/verweise.py`
- Direkter Qt-Import: ja
- Klassen: `VerweiseBefehle`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.dokument.literatur`, `lunivo_writer.editor.dokument.verzeichnis`, `lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.dialoge.verweise.verweise_dialoge`, `lunivo_writer.oberflaeche.dialoge.verweise.verweise_fenster`

### `kern/befehle/hilfen.py`
- Direkter Qt-Import: nein
- Klassen: `FreiMenue`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten`, `lunivo_writer.oberflaeche.dokument.bearbeitung.freie_bilder_bedienung`

### `kern/befehle/kontextreiter/__init__.py`
- Direkter Qt-Import: nein

### `kern/befehle/kontextreiter/bildtools.py`
- Direkter Qt-Import: ja
- Klassen: `BildToolsBefehle`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.bilddaten`, `lunivo_writer.editor.seite`, `lunivo_writer.oberflaeche.baukasten`, `lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.medien.bild_zoom`, `lunivo_writer.oberflaeche.baukasten.medien.bildformate`, `lunivo_writer.oberflaeche.dialoge.dokument_dialoge`

### `kern/befehle/kontextreiter/diagrammtools.py`
- Direkter Qt-Import: ja
- Klassen: `DiagrammToolsBefehle`
- Funktionen: `_nummer`, `_umbenennen`, `_filter_umbenennen`, `_element_befehle`, `_typ_klappen`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.editor.objekte`, `lunivo_writer.kern.befehle.hilfen`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.dialoge.einfuegen.diagramm_fenster`, `lunivo_writer.oberflaeche.dialoge.einfuegen.einfuegen_dialoge`

### `kern/befehle/kontextreiter/formtools.py`
- Direkter Qt-Import: ja
- Klassen: `FormToolsBefehle`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.kern.befehle.hilfen`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten`, `lunivo_writer.oberflaeche.baukasten.basis`, `lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.dokument.bearbeitung`

### `kern/befehle/kontextreiter/kontext.py`
- Direkter Qt-Import: ja
- Klassen: `KontextBefehle`
- Interne Imports: `lunivo_writer.editor.text`, `lunivo_writer.kern.befehle.kontextreiter.tabellen`, `lunivo_writer.kern.befehle.kontextreiter.tabellen_format`, `lunivo_writer.kern.befehle.kontextreiter.zeichentools`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.bauteile`

### `kern/befehle/kontextreiter/kopffuss.py`
- Direkter Qt-Import: ja
- Klassen: `KopfFussBefehle`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.schiebe_feld`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.bauteile`

### `kern/befehle/kontextreiter/smartart_knoten_zustand.py`
- Direkter Qt-Import: nein
- Klassen: `SmartArtKnotenZustand`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.modelle.seite`

### `kern/befehle/kontextreiter/smartarttools.py`
- Direkter Qt-Import: nein
- Klassen: `SmartArtToolsBefehle`
- Interne Imports: `lunivo_writer.editor.objekte`

### `kern/befehle/kontextreiter/tabellen.py`
- Direkter Qt-Import: ja
- Klassen: `TabellenBefehle`
- Interne Imports: `lunivo_writer.editor.tabelle`, `lunivo_writer.editor.tabelle.tabelleneigenschaften`, `lunivo_writer.kern.tabellenaktionen`, `lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dialoge.dokument_dialoge`

### `kern/befehle/kontextreiter/tabellen_format.py`
- Direkter Qt-Import: ja
- Klassen: `TabellenFormatBefehle`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.objekte.linie`, `lunivo_writer.editor.tabelle`, `lunivo_writer.kern.befehle.hilfen`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.baukasten.basis`, `lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.formatierung.rahmen_schattierung`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.dialoge.verweise.verweise_fenster`

### `kern/befehle/kontextreiter/texttools.py`
- Direkter Qt-Import: ja
- Klassen: `TextToolsBefehle`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.text`, `lunivo_writer.editor.text.textfx`, `lunivo_writer.kern.befehle.hauptreiter.text`, `lunivo_writer.kern.befehle.hilfen`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten`, `lunivo_writer.oberflaeche.baukasten.basis`, `lunivo_writer.oberflaeche.baukasten.basis.linien`, `lunivo_writer.oberflaeche.baukasten.dokument.liste_dialog`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.raster_auswahl`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.objekt_menues`, `lunivo_writer.oberflaeche.baukasten.dropdown.voreinstellung_menue`, `lunivo_writer.oberflaeche.baukasten.formatierung.schriftart_dialog`, `lunivo_writer.oberflaeche.baukasten.formatierung.text_format`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.baukasten.medien.seiten_bildchen`

### `kern/befehle/kontextreiter/zeichentools.py`
- Direkter Qt-Import: ja
- Klassen: `ZeichenToolsBefehle`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.kern.befehle.hilfen`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`

### `kern/befehlsliste.py`
- Direkter Qt-Import: ja
- Klassen: `Befehle`
- Interne Imports: `lunivo_writer.kern.befehle.hauptreiter.ansicht`, `lunivo_writer.kern.befehle.hauptreiter.bearbeiten`, `lunivo_writer.kern.befehle.hauptreiter.datei`, `lunivo_writer.kern.befehle.hauptreiter.einfuegen`, `lunivo_writer.kern.befehle.hauptreiter.ki`, `lunivo_writer.kern.befehle.hauptreiter.kommentare`, `lunivo_writer.kern.befehle.hauptreiter.pruefen`, `lunivo_writer.kern.befehle.hauptreiter.seite`, `lunivo_writer.kern.befehle.hauptreiter.serien`, `lunivo_writer.kern.befehle.hauptreiter.text`, `lunivo_writer.kern.befehle.hauptreiter.ueberpruefen`, `lunivo_writer.kern.befehle.hauptreiter.verweise`, `lunivo_writer.kern.befehle.hilfen`, `lunivo_writer.kern.befehle.kontextreiter.bildtools`, `lunivo_writer.kern.befehle.kontextreiter.diagrammtools`, `lunivo_writer.kern.befehle.kontextreiter.formtools`, `lunivo_writer.kern.befehle.kontextreiter.kontext`, `lunivo_writer.kern.befehle.kontextreiter.kopffuss`, `lunivo_writer.kern.befehle.kontextreiter.smartart_knoten_zustand`, `lunivo_writer.kern.befehle.kontextreiter.smartarttools`, `lunivo_writer.kern.befehle.kontextreiter.texttools`

### `kern/dokument_verwaltung.py`
- Direkter Qt-Import: nein
- Klassen: `DocumentManager`
- Interne Imports: `lunivo_writer.core.document`, `lunivo_writer.dienste`, `lunivo_writer.dienste.einstellungen_dienst`, `lunivo_writer.dienste.modell_speichern`

### `kern/farben.py`
- Direkter Qt-Import: nein
- Klassen: `Farbe`

### `kern/pfade.py`
- Direkter Qt-Import: nein

### `kern/piktogramme.py`
- Direkter Qt-Import: ja
- Funktionen: `katalog`, `katalog_bild`
- Interne Imports: `lunivo_writer.kern`, `lunivo_writer.kern.farben`

### `kern/tabellenaktionen.py`
- Direkter Qt-Import: nein
- Klassen: `Tabellenaktion`

### `ki/__init__.py`
- Direkter Qt-Import: nein

### `ki/arbeitslauf.py`
- Direkter Qt-Import: ja
- Klassen: `_Sig`, `_Lauf`

### `ki/argos.py`
- Direkter Qt-Import: nein
- Funktionen: `code_fuer`, `erkenne_sprache`, `_fehler`, `_bibliothek`, `_mitgelieferte_installieren`, `_suche`, `uebersetze`, `_name`, `installierte_richtungen`, `verfuegbare_richtungen`, `richtung_installieren`, `_netzfehler`
- Interne Imports: `lunivo_writer.plattform`

### `ki/assistent_lauf.py`
- Direkter Qt-Import: nein
- Klassen: `Drossel`
- Funktionen: `verzoegerung_begrenzen`, `absatz_geaendert`, `eingabe_kuerzen`, `ergebnis_wirkt`, `trenne_begruendung`

### `ki/chat_antwort.py`
- Direkter Qt-Import: nein
- Funktionen: `_ohne_marke`, `teilen`, `strom_text`, `felder`, `kern_von`

### `ki/chat_bezug.py`
- Direkter Qt-Import: nein
- Funktionen: `bezug_bauen`, `bezug_angewendet`, `bezug_pruefen`, `vorschau_stuecke`, `_aehnlichkeit`, `ersetz_schritte`, `vorher_der_nachricht`, `vorschau_der_nachricht`, `vorschau_einfuegen`
- Interne Imports: `lunivo_writer.editor.text`, `lunivo_writer.ki`

### `ki/chat_modell.py`
- Direkter Qt-Import: nein
- Klassen: `ChatModell`
- Funktionen: `fehler_objekt`, `gespraechstitel`
- Interne Imports: `lunivo_writer.ki`

### `ki/chat_vorschlaege.py`
- Direkter Qt-Import: nein
- Funktionen: `_eintrag`, `chat_vorschlaege`
- Interne Imports: `lunivo_writer.ki`

### `ki/dokument_abschnitte.py`
- Direkter Qt-Import: nein
- Funktionen: `_aus_textdokument`, `_aus_pdf`, `_aus_txt`, `lesen`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.ki.dokumentensuche`

### `ki/dokumentensuche.py`
- Direkter Qt-Import: nein
- Klassen: `Index`
- Funktionen: `abschnitte_bilden`, `frage_zu_fts`, `_ohne_versteckte`, `dateien_in`, `_bestand`, `_datei_aufnehmen`, `fundstelle`, `als_text`, `fundstellen_zeilen`
- Interne Imports: `lunivo_writer.ki.dokument_abschnitte`

### `ki/ki.py`
- Direkter Qt-Import: nein
- Klassen: `KI`
- Funktionen: `als_geld`, `anbieter_modelle`
- Interne Imports: `lunivo_writer.ki`, `lunivo_writer.ki.ki_anweisungen`, `lunivo_writer.ki.ki_claude`, `lunivo_writer.ki.ki_diff`, `lunivo_writer.ki.ki_konfiguration`, `lunivo_writer.ki.ki_ollama`, `lunivo_writer.ki.ki_transport`

### `ki/ki_aktionen.py`
- Direkter Qt-Import: ja
- Klassen: `KIAktionenMixin`
- Interne Imports: `lunivo_writer.dienste.einstellungen_dienst`, `lunivo_writer.ki`, `lunivo_writer.ki.chat_modell`

### `ki/ki_anfragen.py`
- Direkter Qt-Import: ja
- Klassen: `KIAnfragenMixin`
- Interne Imports: `lunivo_writer.dienste.einstellungen_dienst`, `lunivo_writer.editor.dokument`, `lunivo_writer.ki`, `lunivo_writer.ki.arbeitslauf`, `lunivo_writer.ki.chat_modell`

### `ki/ki_anweisungen.py`
- Direkter Qt-Import: nein
- Funktionen: `_zettel`, `steckbrief`, `anweisung_korrektur`, `anweisung_uebersetzung`, `anweisung_vorschlaege`, `anweisung_text_aktion`
- Interne Imports: `lunivo_writer.ki.ki_konfiguration`

### `ki/ki_bildgenerierung.py`
- Direkter Qt-Import: nein
- Funktionen: `anbieter_pruefen`, `_bild_aus`, `_http_fehler`, `erzeugen`
- Interne Imports: `lunivo_writer.ki`, `lunivo_writer.ki.ki_konfiguration`

### `ki/ki_chat.py`
- Direkter Qt-Import: ja
- Klassen: `KIChatMixin`
- Interne Imports: `lunivo_writer.dienste.einstellungen_dienst`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text`, `lunivo_writer.ki`, `lunivo_writer.ki.arbeitslauf`, `lunivo_writer.ki.chat_modell`

### `ki/ki_chat_kontext.py`
- Direkter Qt-Import: nein
- Funktionen: `system_text`, `sperre`, `bilder`, `websuche`, `dokumentensuche`, `abschliessen`
- Interne Imports: `lunivo_writer.ki`, `lunivo_writer.ki.ki_konfiguration`

### `ki/ki_claude.py`
- Direkter Qt-Import: nein
- Funktionen: `cent_fuer`, `_ausgabe_einstellungen`, `bitte_bauen`, `_meldung`, `fehler_http`, `antwort_lesen`, `anfrage`
- Interne Imports: `lunivo_writer.ki`, `lunivo_writer.ki.ki_konfiguration`

### `ki/ki_dauerbetrieb.py`
- Direkter Qt-Import: ja
- Klassen: `KIDauerbetriebMixin`
- Interne Imports: `lunivo_writer.dienste.einstellungen_dienst`, `lunivo_writer.ki`, `lunivo_writer.ki.chat_modell`

### `ki/ki_dienst.py`
- Direkter Qt-Import: ja
- Klassen: `KIDienst`
- Interne Imports: `lunivo_writer.dienste.einstellungen_dienst`, `lunivo_writer.ki`, `lunivo_writer.ki.arbeitslauf`, `lunivo_writer.ki.chat_modell`, `lunivo_writer.ki.ki_aktionen`, `lunivo_writer.ki.ki_anfragen`, `lunivo_writer.ki.ki_chat`, `lunivo_writer.ki.ki_dauerbetrieb`

### `ki/ki_diff.py`
- Direkter Qt-Import: nein
- Funktionen: `aenderungen`, `ersetze_ergebnis`

### `ki/ki_eigen.py`
- Direkter Qt-Import: nein
- Funktionen: `_optionen_uebernehmen`, `bitte_bauen`, `antwort_lesen`, `_senden`, `anfrage`
- Interne Imports: `lunivo_writer.ki`

### `ki/ki_konfiguration.py`
- Direkter Qt-Import: nein
- Klassen: `KIKonfig`
- Funktionen: `assistent_normiert`, `ist_lokale_url`
- Interne Imports: `lunivo_writer.ki`, `lunivo_writer.ki.assistent_lauf`

### `ki/ki_ollama.py`
- Direkter Qt-Import: nein
- Klassen: `_Strom`
- Funktionen: `_leer`, `keep_alive_begrenzen`, `num_thread_begrenzen`, `num_ctx_begrenzen`, `num_predict_fuer`, `num_ctx_fuer`, `_optionen_bauen`, `bitte_bauen`, `_http_fehler`, `antwort_lesen`, `_senden`, `anfrage`, `_abgebrochen`, `_json_teil`, `strom_lesen`
- Interne Imports: `lunivo_writer.ki`, `lunivo_writer.ki.ki_konfiguration`

### `ki/ki_textaktionen.py`
- Direkter Qt-Import: nein
- Funktionen: `anweisung_synonyme`, `liste_lesen`, `_vorschlag_gueltig`, `vorschlaege_bereinigen`, `synonyme_bereinigen`
- Interne Imports: `lunivo_writer.ki`, `lunivo_writer.korrektur.fund`

### `ki/ki_transport.py`
- Direkter Qt-Import: nein
- Funktionen: `json_dict`, `post`, `post_roh`, `bearer_kopf`, `stufe`, `stopp_liste`, `erste_nachricht`, `json_nach_marken`, `ohne_gruebeln`, `bild_block`, `_bild_inhalt`, `nachricht`, `nachrichten`, `bilder_lesen`
- Interne Imports: `lunivo_writer.ki`

### `ki/ki_werkzeugschleife.py`
- Direkter Qt-Import: nein
- Klassen: `_Sitzung`
- Funktionen: `_bitte`, `_senden`, `_aufrufe`, `_argumente`, `_ausfuehren`, `_tool_antwort`, `_runden`, `_fehler_http`, `chat`
- Interne Imports: `lunivo_writer.ki`

### `ki/mcp.py`
- Direkter Qt-Import: nein
- Klassen: `McpFehler`, `McpClient`
- Funktionen: `pruefen`, `art_des_werkzeugs`
- Interne Imports: `lunivo_writer.plattform`

### `ki/modellfaehigkeit.py`
- Direkter Qt-Import: nein
- Funktionen: `denkstufe`, `claude_faehig`, `bildtyp_aus_inhalt`, `bild_pruefen`, `werkzeug_erlaubt`

### `ki/suchdienst.py`
- Direkter Qt-Import: nein
- Funktionen: `_text`, `aufrufen`, `behandle`, `main`
- Interne Imports: `lunivo_writer.ki`

### `ki/websuche.py`
- Direkter Qt-Import: nein
- Funktionen: `suche`, `als_text`

### `korrektur/__init__.py`
- Direkter Qt-Import: nein

### `korrektur/autokorrektur.py`
- Direkter Qt-Import: nein
- Funktionen: `_ordnung`, `korrigiere`, `kleinste_aenderung`

### `korrektur/barrierefreiheit.py`
- Direkter Qt-Import: ja
- Funktionen: `_hell`, `kontrast`, `_bild_ohne_alt`, `_fragment_pruefen`, `_text_durchsuchen`, `_ueberschriften_funde`, `_link_fund`, `pruefe`, `_tabellen`
- Interne Imports: `lunivo_writer.dienste.docx_leser`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.kern.farben`

### `korrektur/fund.py`
- Direkter Qt-Import: nein
- Funktionen: `klemmen`, `markieren`, `_rang`, `loesen`, `_bestaetigen`, `_konsens`, `_gegenprobe_faellig`, `abstimmen`
- Interne Imports: `lunivo_writer.modelle.korrektur`

### `korrektur/haeufig.py`
- Direkter Qt-Import: nein

### `korrektur/inkrement.py`
- Direkter Qt-Import: nein
- Funktionen: `verschieben`, `schmutz_abbilden`, `pruefbereich`, `lohnt`, `einsetzen`
- Interne Imports: `lunivo_writer.modelle.korrektur`

### `korrektur/klang.py`
- Direkter Qt-Import: nein
- Funktionen: `_pruefung`, `_klangtafel`, `_gewicht`, `klingt_wie`, `_rang`, `_treffer_sammeln`, `vorschlaege_fuer`
- Interne Imports: `lunivo_writer.korrektur`, `lunivo_writer.korrektur.haeufig`, `lunivo_writer.korrektur.phonetik`

### `korrektur/korrektur_dienst.py`
- Direkter Qt-Import: ja
- Klassen: `_Signale`, `_Lauf`, `WritingAssistant`
- Interne Imports: `lunivo_writer.dienste.gelernt`, `lunivo_writer.dienste.integrationen`, `lunivo_writer.korrektur`, `lunivo_writer.modelle.korrektur`

### `korrektur/phonetik.py`
- Direkter Qt-Import: nein
- Funktionen: `de_schluessel`, `ist_teilfolge`, `gleicher_anfang`, `abstand`, `_in`, `_code_c`, `_koeln_code`, `koelner_phonetik`

### `korrektur/pruefung.py`
- Direkter Qt-Import: nein
- Funktionen: `daten_ordner`, `_lies_regeln`, `uebernimm_schreibweise`, `mach_fund`, `ist_abkuerzung`, `wort_um`, `ist_adresse`, `gross_dahinter`, `regel`, `wende_regeln_an`, `pruefe_kongruenz`, `lade_woerter`, `trenne_zusammen`, `pruefe_zusammengeschrieben`, `verwechslungen`, `regel_varianten`, `_geruest`, `_ist_zusammensetzung`, `_klang_kandidaten`, `_regel_vorschlag`, `_klang_bewertet`, `_klang_reihe`, `_klang_eindeutig`, `klang_vorschlag`, `_klang_ausgeschlossen`, `_am_satzanfang`, `_klang_fund_wort`, `pruefe_klang`, `nachbar_woerter`, `_tippfehler_treffer`, `tippfehler_vorschlag`, `_tippfehler_berechnen`, `_tippfehler_fund`, `pruefe_tippfehler`, `wort_abstand`, `ist_korrektur`, `uebergehen`, `_wort_fund`, `pruefe_woerter`, `pruefe_satzende`, `mach_hinweis`, `pruefe_satzbau`, `ohne_ueberschneidung`, `pruefer_aktiv`, `finde_probleme`
- Interne Imports: `lunivo_writer.kern`, `lunivo_writer.korrektur.haeufig`, `lunivo_writer.korrektur.klang`, `lunivo_writer.korrektur.phonetik`, `lunivo_writer.modelle.korrektur`

### `korrektur/silben_de.py`
- Direkter Qt-Import: nein
- Funktionen: `_einheiten`, `_wortende`, `_stueck`, `_pyphen`, `_hat_kern`, `_hinweis_ok`, `silben`

### `korrektur/vorhersage.py`
- Direkter Qt-Import: nein
- Funktionen: `themenwoerter`, `thema_woerter`, `thema_aufnehmen`, `_liste`, `faengt_an_mit`
- Interne Imports: `lunivo_writer.korrektur.haeufig`, `lunivo_writer.korrektur.pruefung`

### `modelle/__init__.py`
- Direkter Qt-Import: nein

### `modelle/bericht.py`
- Direkter Qt-Import: nein
- Klassen: `IOReport`, `DocumentIOError`, `PasswortNoetig`

### `modelle/korrektur.py`
- Direkter Qt-Import: nein
- Klassen: `FundFehler`, `Verdraengt`, `ProofingIssue`
- Funktionen: `zeige_leer`, `bereinigen`

### `modelle/seite.py`
- Direkter Qt-Import: nein
- Klassen: `HeaderFooter`, `PageSettings`
- Interne Imports: `lunivo_writer.core.geometry.units`, `lunivo_writer.kern.farben`

### `oberflaeche/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/backstage.py`
- Direkter Qt-Import: ja
- Klassen: `_Zeile`, `Backstage`
- Funktionen: `symbol`, `stil`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.spalten`, `lunivo_writer.oberflaeche.baukasten.medien.datei_symbole`, `lunivo_writer.oberflaeche.baukasten.vorlagen.vorlagen_galerie`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dialoge.optionen`

### `oberflaeche/band/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/band/band_bausteine.py`
- Direkter Qt-Import: ja
- Klassen: `_GruppenTrenner`, `_BandSeite`, `_ReiterLeiste`, `_SperrKasten`, `_FelderDict`
- Funktionen: `_kurz`, `_mit_kuerzel`, `_zweizeilig`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste`, `lunivo_writer.oberflaeche.kuerzel`

### `oberflaeche/band/band_gruppen.py`
- Direkter Qt-Import: ja
- Klassen: `BandGruppenBaustein`
- Funktionen: `_zeilen_teilen`
- Interne Imports: `lunivo_writer.kern`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.band.band_bausteine`, `lunivo_writer.oberflaeche.band.plan`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.bild_diagramm_menues`, `lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.karten_raster`, `lunivo_writer.oberflaeche.baukasten.formatierung.text_format`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.bauteile.live_vorschau`, `lunivo_writer.oberflaeche.dialoge.dokument_dialoge`, `lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor`, `lunivo_writer.oberflaeche.thema`

### `oberflaeche/band/band_knoepfe.py`
- Direkter Qt-Import: ja
- Klassen: `BandKnopfBaustein`
- Interne Imports: `lunivo_writer.oberflaeche.band.band_bausteine`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.bild_diagramm_menues`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/band/band_leiste.py`
- Direkter Qt-Import: ja
- Klassen: `RegisterBand`
- Funktionen: `lade_register`
- Interne Imports: `lunivo_writer.kern`, `lunivo_writer.oberflaeche.band.band_bausteine`, `lunivo_writer.oberflaeche.band.band_gruppen`, `lunivo_writer.oberflaeche.band.band_knoepfe`, `lunivo_writer.oberflaeche.band.band_raender`, `lunivo_writer.oberflaeche.band.band_reiter`, `lunivo_writer.oberflaeche.band.band_schnellzugriff`, `lunivo_writer.oberflaeche.band.band_stile`, `lunivo_writer.oberflaeche.band.band_zustand`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.thema`

### `oberflaeche/band/band_raender.py`
- Direkter Qt-Import: ja
- Klassen: `BandRaenderBaustein`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`

### `oberflaeche/band/band_reiter.py`
- Direkter Qt-Import: ja
- Klassen: `BandReiterBaustein`
- Interne Imports: `lunivo_writer.oberflaeche.band.band_bausteine`, `lunivo_writer.oberflaeche.band.plan`, `lunivo_writer.oberflaeche.baukasten.basis.mass`

### `oberflaeche/band/band_schnellzugriff.py`
- Direkter Qt-Import: ja
- Klassen: `BandSchnellzugriffBaustein`
- Interne Imports: `lunivo_writer.oberflaeche.band.band_bausteine`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.thema`

### `oberflaeche/band/band_stile.py`
- Direkter Qt-Import: ja
- Klassen: `BandStileBaustein`
- Funktionen: `_kacheln`
- Interne Imports: `lunivo_writer.editor.text`, `lunivo_writer.kern`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.band.plan`, `lunivo_writer.oberflaeche.baukasten`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.bild_diagramm_menues`, `lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.karten_raster`, `lunivo_writer.oberflaeche.baukasten.formatierung.text_format`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.bauteile.live_vorschau`, `lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor`, `lunivo_writer.oberflaeche.thema`

### `oberflaeche/band/band_zustand.py`
- Direkter Qt-Import: nein
- Klassen: `BandZustandBaustein`
- Interne Imports: `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/band/menueleiste.py`
- Direkter Qt-Import: ja
- Funktionen: `_taste`, `baue_menueleiste`, `_fenster_menue`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`

### `oberflaeche/band/plan.py`
- Direkter Qt-Import: nein
- Funktionen: `plan`
- Interne Imports: `lunivo_writer.oberflaeche.band.reiter`, `lunivo_writer.oberflaeche.kontext.bild_werkzeuge`, `lunivo_writer.oberflaeche.kontext.diagramm_werkzeuge`, `lunivo_writer.oberflaeche.kontext.kopf_fuss_werkzeuge`, `lunivo_writer.oberflaeche.kontext.serien_werkzeuge`, `lunivo_writer.oberflaeche.kontext.tabellen_werkzeuge`, `lunivo_writer.oberflaeche.kontext.text_werkzeuge`

### `oberflaeche/band/reiter/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/band/reiter/abschnitt_reiter.py`
- Direkter Qt-Import: nein
- Funktionen: `bauen`
- Interne Imports: `lunivo_writer.oberflaeche.band.reiter.baustein`

### `oberflaeche/band/reiter/ansicht_reiter.py`
- Direkter Qt-Import: nein
- Funktionen: `bauen`, `_mit_weitere`
- Interne Imports: `lunivo_writer.oberflaeche.band.reiter.baustein`

### `oberflaeche/band/reiter/baustein.py`
- Direkter Qt-Import: nein
- Funktionen: `k`, `anordnen_knopf`, `anordnen_gruppe`, `alle`, `uebrige`

### `oberflaeche/band/reiter/datei_reiter.py`
- Direkter Qt-Import: nein
- Funktionen: `bauen`
- Interne Imports: `lunivo_writer.oberflaeche.band.reiter.baustein`

### `oberflaeche/band/reiter/einfuegen_reiter.py`
- Direkter Qt-Import: nein
- Funktionen: `bauen`
- Interne Imports: `lunivo_writer.oberflaeche.band.reiter.baustein`

### `oberflaeche/band/reiter/ki_reiter.py`
- Direkter Qt-Import: nein
- Funktionen: `_knoepfe`, `_ki_knoepfe`, `_pruefen_menue`, `bauen`
- Interne Imports: `lunivo_writer.oberflaeche.band.reiter.baustein`, `lunivo_writer.oberflaeche.schreibhilfe_katalog`

### `oberflaeche/band/reiter/layout_reiter.py`
- Direkter Qt-Import: nein
- Funktionen: `bauen`
- Interne Imports: `lunivo_writer.oberflaeche.band.reiter.baustein`

### `oberflaeche/band/reiter/sendungen_reiter.py`
- Direkter Qt-Import: nein
- Funktionen: `bauen`

### `oberflaeche/band/reiter/start_reiter.py`
- Direkter Qt-Import: nein
- Funktionen: `bauen`
- Interne Imports: `lunivo_writer.oberflaeche.band.reiter.baustein`

### `oberflaeche/band/reiter/ueberpruefen_reiter.py`
- Direkter Qt-Import: nein
- Funktionen: `bauen`
- Interne Imports: `lunivo_writer.oberflaeche.band.reiter.baustein`

### `oberflaeche/band/reiter/verweise_reiter.py`
- Direkter Qt-Import: nein
- Funktionen: `bauen`
- Interne Imports: `lunivo_writer.oberflaeche.band.reiter.baustein`

### `oberflaeche/band/werkzeugleisten.py`
- Direkter Qt-Import: ja
- Klassen: `Symbolleisten`
- Interne Imports: `lunivo_writer.oberflaeche.band.band_leiste`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.kontext.bild_werkzeuge`, `lunivo_writer.oberflaeche.kontext.tabellen_werkzeuge`, `lunivo_writer.oberflaeche.kontext.text_werkzeuge`, `lunivo_writer.oberflaeche.thema`

### `oberflaeche/baukasten/__init__.py`
- Direkter Qt-Import: nein
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.beschriftung`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.linien`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.farbpalette`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.rahmen_menue`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.raster_auswahl`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.zellen_raster`, `lunivo_writer.oberflaeche.baukasten.dropdown.galerie_auswahl`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.felder.mass_feld`, `lunivo_writer.oberflaeche.baukasten.formatierung.text_format`, `lunivo_writer.oberflaeche.baukasten.medien.datei_symbole`, `lunivo_writer.oberflaeche.baukasten.medien.listen_symbole`

### `oberflaeche/baukasten/basis/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/baukasten/basis/beschriftung.py`
- Direkter Qt-Import: ja
- Funktionen: `md_escape`, `text_label`, `md_label`

### `oberflaeche/baukasten/basis/dialog_rahmen.py`
- Direkter Qt-Import: ja
- Klassen: `_KnopfLayout`, `Knopfzeile`, `VorschauFlaeche`, `DialogRahmen`
- Funktionen: `knopfzeile`, `fussleiste`, `_symbol`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/basis/farben.py`
- Direkter Qt-Import: ja
- Funktionen: `mische`, `abstufungen`, `thema_raster`, `zuletzt_laden`, `zuletzt_merken`

### `oberflaeche/baukasten/basis/karte.py`
- Direkter Qt-Import: nein
- Funktionen: `als_karte`, `karte_regeln`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`

### `oberflaeche/baukasten/basis/linien.py`
- Direkter Qt-Import: ja
- Klassen: `LinienZeile`, `LinienWahl`, `RahmenSeiten`
- Funktionen: `linien_symbol`, `linien_menue_zeile`, `rahmen_symbol`
- Interne Imports: `lunivo_writer.editor.objekte.linie`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.farbpalette`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`

### `oberflaeche/baukasten/basis/mass.py`
- Direkter Qt-Import: nein

### `oberflaeche/baukasten/basis/texte.py`
- Direkter Qt-Import: ja
- Funktionen: `_stil`, `hinweis_label`, `hinweis_stil`, `kleintext_label`, `trennlinie`, `auffrischen`, `marke_faerben`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`

### `oberflaeche/baukasten/basis/zwischenablage.py`
- Direkter Qt-Import: ja
- Funktionen: `in_zwischenablage`

### `oberflaeche/baukasten/chat/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/baukasten/chat/chat_anhang.py`
- Direkter Qt-Import: ja
- Klassen: `AnhangChip`
- Funktionen: `groesse_text`, `name_gekuerzt`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.beschriftung`, `lunivo_writer.oberflaeche.baukasten.basis.karte`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.chat.chat_blase`

### `oberflaeche/baukasten/chat/chat_blase.py`
- Direkter Qt-Import: ja
- Klassen: `SymbolKnopf`, `NutzerBlase`, `KiBlase`, `FehlerKarte`
- Funktionen: `miniatur`, `_text`, `antwort_label`
- Interne Imports: `lunivo_writer.editor.text`, `lunivo_writer.ki`, `lunivo_writer.oberflaeche.baukasten.basis.beschriftung`, `lunivo_writer.oberflaeche.baukasten.basis.karte`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.basis.zwischenablage`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/chat/chat_eingabe.py`
- Direkter Qt-Import: ja
- Klassen: `ChatEingabe`, `ChatEingabeKasten`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.ki`, `lunivo_writer.ki.chat_vorschlaege`, `lunivo_writer.oberflaeche.baukasten.basis.karte`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.chat.chat_anhang`, `lunivo_writer.oberflaeche.baukasten.chat.chat_blase`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dialoge.ki.ki_dialoge`

### `oberflaeche/baukasten/chat/chat_leerzustand.py`
- Direkter Qt-Import: ja
- Klassen: `ChatLeerzustand`
- Interne Imports: `lunivo_writer.ki.chat_vorschlaege`, `lunivo_writer.oberflaeche.baukasten.basis.karte`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/chat/chat_regler.py`
- Direkter Qt-Import: ja
- Klassen: `ChatReglerBlock`
- Interne Imports: `lunivo_writer.ki`, `lunivo_writer.oberflaeche.baukasten.basis.beschriftung`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/diagramme/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/baukasten/diagramme/diagramm_format_bausteine.py`
- Direkter Qt-Import: ja
- Klassen: `_AutoWert`
- Funktionen: `_optionen_name`, `_text_teil`, `_combo`, `_strich_zeichner`, `_kombi_zeichner`, `_still`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.editor.text`, `lunivo_writer.oberflaeche.baukasten.basis.linien`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.strich_auswahl`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`

### `oberflaeche/baukasten/diagramme/diagramm_format_panel.py`
- Direkter Qt-Import: ja
- Klassen: `DiagrammFormatPanel`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.linien`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.diagramme.diagramm_format_bausteine`, `lunivo_writer.oberflaeche.baukasten.diagramme.diagramm_format_werte`, `lunivo_writer.oberflaeche.baukasten.diagramme.diagramm_text_panel`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.farbpalette`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.strich_auswahl`, `lunivo_writer.oberflaeche.baukasten.dropdown.kopf_menue_mixin`, `lunivo_writer.oberflaeche.baukasten.dropdown.teil_menue`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.schiebe_feld`, `lunivo_writer.oberflaeche.baukasten.formatierung.auto_felder_mixin`, `lunivo_writer.oberflaeche.baukasten.formatierung.effekte_drei_mixin`, `lunivo_writer.oberflaeche.baukasten.formatierung.objektformat_panel`, `lunivo_writer.oberflaeche.baukasten.formatierung.texteffekt_dialog`, `lunivo_writer.oberflaeche.baukasten.medien.alternativtext_abschnitt`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/diagramme/diagramm_format_werte.py`
- Direkter Qt-Import: nein
- Klassen: `DiagrammFormatWerteMixin`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.linien`, `lunivo_writer.oberflaeche.baukasten.diagramme.diagramm_format_bausteine`

### `oberflaeche/baukasten/diagramme/diagramm_text_panel.py`
- Direkter Qt-Import: ja
- Klassen: `DiagrammTextPanel`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.editor.text`, `lunivo_writer.editor.text.textfx`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.diagramme.diagramm_format_bausteine`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.kopf_dropdown`, `lunivo_writer.oberflaeche.baukasten.dropdown.text_kopf_menue_mixin`, `lunivo_writer.oberflaeche.baukasten.dropdown.voreinstellung_menue`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.schiebe_feld`, `lunivo_writer.oberflaeche.baukasten.formatierung.objektformat_panel`, `lunivo_writer.oberflaeche.baukasten.formatierung.text_fuellarten_mixin`, `lunivo_writer.oberflaeche.baukasten.formatierung.texteffekt_dialog`, `lunivo_writer.oberflaeche.baukasten.formatierung.textfeld_abschnitt`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/diagramme/smartart_format_panel.py`
- Direkter Qt-Import: nein
- Klassen: `SmartArtTextPanel`, `SmartArtFormatPanel`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.diagramme.diagramm_format_panel`, `lunivo_writer.oberflaeche.baukasten.diagramme.diagramm_text_panel`

### `oberflaeche/baukasten/diagramme/smartart_stil_kacheln.py`
- Direkter Qt-Import: ja
- Funktionen: `stil_bild_org`, `stile_menue_org`, `stile_galerie_org`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.raster_auswahl`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.smartart_menues`

### `oberflaeche/baukasten/dokument/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/baukasten/dokument/aenderungs_fenster.py`
- Direkter Qt-Import: ja
- Klassen: `AenderungsFenster`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.beschriftung`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.basis.zwischenablage`, `lunivo_writer.oberflaeche.baukasten.chat.chat_blase`, `lunivo_writer.oberflaeche.baukasten.dokument.aenderungs_vorschau`, `lunivo_writer.oberflaeche.baukasten.geruest.panel_rahmen`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/baukasten/dokument/aenderungs_vorschau.py`
- Direkter Qt-Import: ja
- Klassen: `AenderungsVorschau`
- Funktionen: `_hinterlegt`
- Interne Imports: `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.karte`, `lunivo_writer.oberflaeche.baukasten.basis.mass`

### `oberflaeche/baukasten/dokument/druck_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `_Reiter`, `DruckAnsicht`, `DruckDialog`
- Funktionen: `_kopf`, `_drucker_liste`, `_combo`
- Interne Imports: `lunivo_writer.editor.seite.druck`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.spalten`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/dokument/druckvorschau.py`
- Direkter Qt-Import: ja
- Klassen: `DruckVorschau`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/dokument/eingabe_fenster.py`
- Direkter Qt-Import: ja
- Klassen: `EingabeFenster`
- Funktionen: `_beim_editor_anmelden`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/baukasten/dokument/erstellen_fenster.py`
- Direkter Qt-Import: ja
- Klassen: `ErstellenFenster`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.baukasten.vorlagen.vorlagen_chips`

### `oberflaeche/baukasten/dokument/layout_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `LayoutDialog`
- Funktionen: `_combo`, `_zeile`
- Interne Imports: `lunivo_writer.editor.objekte.bildlayout`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.kachel_feld`, `lunivo_writer.oberflaeche.baukasten.felder.mass_feld`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.baukasten.medien.umbruch_symbole`

### `oberflaeche/baukasten/dokument/layout_dialog_objekt.py`
- Direkter Qt-Import: ja
- Klassen: `LayoutDialogObjekt`
- Funktionen: `layout_dialog_fuer`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dokument.layout_dialog`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`

### `oberflaeche/baukasten/dokument/liste_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `_Zahlenformat`, `_Positionen`, `NummerierungAnpassenDialog`, `GliederungAnpassenDialog`, `_KachelFueller`, `ListenDialog`
- Funktionen: `benutzerlisten`, `_merke`, `_rahmen`, `_bild`, `_raster`, `_gl_bild`, `kachel_bild`, `aufzaehlungen`, `nummerierungen`
- Interne Imports: `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.mass_feld`, `lunivo_writer.oberflaeche.baukasten.formatierung.schriftart_dialog`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.baukasten.medien.listen_symbole`

### `oberflaeche/baukasten/dokument/pdf_export.py`
- Direkter Qt-Import: ja
- Klassen: `PdfExportAnsicht`
- Funktionen: `_abschnitt`, `_einklappen`, `_kennwort`
- Interne Imports: `lunivo_writer.dienste.pdf_export`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`

### `oberflaeche/baukasten/dokument/sortieren_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `SortierOptionenDialog`, `_Schluessel`, `SortierenDialog`
- Funktionen: `_feld`
- Interne Imports: `lunivo_writer.editor.text.schreibweise`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/baukasten/dokument/speichern_fenster.py`
- Direkter Qt-Import: ja
- Klassen: `_DateiModell`, `_Symbole`, `SpeichernFenster`, `Dateifenster`
- Funktionen: `stil`, `_symbol`, `_ordner`, `speicherort_waehlen`, `ordner_waehlen`, `datei_waehlen`, `datei_speichern`, `_ordner_name_fragen`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.spalten`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/dokument/stimme_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `StimmeDialog`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.felder.auswahl_liste`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.schiebe_feld`, `lunivo_writer.oberflaeche.baukasten.geruest.panel_rahmen`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/baukasten/dokument/tabstopp_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `TabstoppDialog`
- Funktionen: `aus_block`, `zu_block`, `als_text`, `aus_text`, `_text`
- Interne Imports: `lunivo_writer.editor.text`, `lunivo_writer.editor.text.tabfuell`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.mass_feld`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/baukasten/dokument/tasten_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `TastenDialog`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`

### `oberflaeche/baukasten/dropdown/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/baukasten/dropdown/auswahl/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/baukasten/dropdown/auswahl/farbpalette.py`
- Direkter Qt-Import: ja
- Klassen: `_Kachel`, `_VerlaufKachel`, `_BildKachel`, `FarbPalette`, `FarbFeld`, `FarbKnopf`
- Funktionen: `weitere_farben`, `weitere_farben_unter`, `farb_symbol`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.felder`, `lunivo_writer.oberflaeche.baukasten.felder.farbwaehler`, `lunivo_writer.oberflaeche.baukasten.felder.karten_raster`, `lunivo_writer.oberflaeche.baukasten.felder.pipette`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/dropdown/auswahl/rahmen_menue.py`
- Direkter Qt-Import: ja
- Klassen: `RahmenMenue`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.linien`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`

### `oberflaeche/baukasten/dropdown/auswahl/raster_auswahl.py`
- Direkter Qt-Import: ja
- Klassen: `RasterAuswahl`
- Funktionen: `_symbol`, `textkachel`, `zeilenkachel`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.dropdown.zeile`, `lunivo_writer.oberflaeche.baukasten.felder.karten_raster`

### `oberflaeche/baukasten/dropdown/auswahl/strich_auswahl.py`
- Direkter Qt-Import: ja
- Klassen: `StrichAuswahl`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.voreinstellung_menue`

### `oberflaeche/baukasten/dropdown/auswahl/symbol_auswahl.py`
- Direkter Qt-Import: ja
- Klassen: `SymbolAuswahl`, `SymbolWahl`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.raster_auswahl`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/dropdown/auswahl/zellen_raster.py`
- Direkter Qt-Import: ja
- Klassen: `_Gitter`, `ZellenRaster`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`

### `oberflaeche/baukasten/dropdown/auswahlfeld.py`
- Direkter Qt-Import: ja
- Klassen: `_KuerzDelegate`, `_Feldlaenge`, `Auswahlfeld`, `Schriftauswahl`
- Funktionen: `popup_begrenzen`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.dropdown.popup_lage`

### `oberflaeche/baukasten/dropdown/dropdown_knopf.py`
- Direkter Qt-Import: ja
- Klassen: `_DropdownBasis`, `DropdownKnopf`, `DropdownTaste`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`

### `oberflaeche/baukasten/dropdown/galerie_auswahl.py`
- Direkter Qt-Import: ja
- Klassen: `_Kachel`, `GalerieAuswahl`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.dropdown.zeile`, `lunivo_writer.oberflaeche.baukasten.felder.karten_raster`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/dropdown/kopf_dropdown.py`
- Direkter Qt-Import: ja
- Klassen: `KopfDropdown`
- Funktionen: `keine_symbol`, `keine_zeile`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.voreinstellung_menue`

### `oberflaeche/baukasten/dropdown/kopf_menue_mixin.py`
- Direkter Qt-Import: ja
- Klassen: `KopfMenueMixin`
- Funktionen: `_hex`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.dropdown.kopf_dropdown`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.fuell_voreinstellungen`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.linien_voreinstellungen`

### `oberflaeche/baukasten/dropdown/menue_liste.py`
- Direkter Qt-Import: ja
- Klassen: `MenueListe`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.dropdown.popup_lage`, `lunivo_writer.oberflaeche.baukasten.dropdown.schalter_zeile`

### `oberflaeche/baukasten/dropdown/menue_tafel.py`
- Direkter Qt-Import: ja
- Klassen: `MenueTafel`
- Funktionen: `_menue_symbol`, `_datum`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.beschriftung`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.popup_lage`, `lunivo_writer.oberflaeche.baukasten.dropdown.zeile`, `lunivo_writer.oberflaeche.baukasten.medien.datei_symbole`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/dropdown/objektmenues/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/baukasten/dropdown/objektmenues/bild_diagramm_menues.py`
- Direkter Qt-Import: ja
- Funktionen: `_form_bild`, `_abschnittsleiste`, `zuschneiden_menue`, `stil_bild`, `_stilname`, `diagramm_stile_menue`, `diagramm_stile_galerie`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.editor.objekte`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.diagramme.smartart_stil_kacheln`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.raster_auswahl`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.diagramm_popups`, `lunivo_writer.oberflaeche.baukasten.dropdown.zeile`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.karten_raster`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/dropdown/objektmenues/diagramm_popups.py`
- Direkter Qt-Import: ja
- Klassen: `DiagrammPopup`
- Funktionen: `_dg`, `_kopfknopf`, `_linie`, `_ueberschrift`, `_bild_titel_achsentitel`, `_bild_legende`, `_bild_achsenmarken_gitter`, `_bild_saeulen`, `_bild_tabelle`, `layout_bild`, `_farbzeile`, `elemente_popup`, `schnelllayout_popup`, `stile_popup`, `farben_popup`, `filter_popup`, `diagramm_bereich_feld`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.editor.objekte`, `lunivo_writer.kern.befehle.kontextreiter.diagrammtools`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.bild_diagramm_menues`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.karten_raster`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/dropdown/objektmenues/form_menues.py`
- Direkter Qt-Import: ja
- Funktionen: `form_bearbeiten_menue`, `formstile_galerie`, `linien_galerie`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.raster_auswahl`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.bild_diagramm_menues`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.objekt_menues`, `lunivo_writer.oberflaeche.dokument.bearbeitung.freie_bilder_bedienung`

### `oberflaeche/baukasten/dropdown/objektmenues/fuell_voreinstellungen.py`
- Direkter Qt-Import: ja
- Klassen: `FuellPalette`
- Funktionen: `graduell_paar`, `_feld`, `_gekachelt`, `_muster_kachel`, `fuell_bild`, `fuell_menue`
- Interne Imports: `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.farbpalette`, `lunivo_writer.oberflaeche.baukasten.dropdown.kopf_dropdown`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.objekt_menues`

### `oberflaeche/baukasten/dropdown/objektmenues/layout_optionen.py`
- Direkter Qt-Import: ja
- Klassen: `LayoutOptionen`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.popup_lage`, `lunivo_writer.oberflaeche.baukasten.felder.kachel_feld`, `lunivo_writer.oberflaeche.baukasten.medien.umbruch_symbole`

### `oberflaeche/baukasten/dropdown/objektmenues/layout_optionen_objekt.py`
- Direkter Qt-Import: ja
- Klassen: `LayoutOptionenObjekt`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.layout_optionen`, `lunivo_writer.oberflaeche.baukasten.felder.kachel_feld`, `lunivo_writer.oberflaeche.baukasten.medien.umbruch_symbole`

### `oberflaeche/baukasten/dropdown/objektmenues/linien_voreinstellungen.py`
- Direkter Qt-Import: ja
- Funktionen: `linien_schluessel`, `linien_bild`, `linien_menue`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.kopf_dropdown`, `lunivo_writer.oberflaeche.baukasten.dropdown.voreinstellung_menue`

### `oberflaeche/baukasten/dropdown/objektmenues/objekt_menues.py`
- Direkter Qt-Import: ja
- Klassen: `FuellMenue`, `KonturMenue`
- Funktionen: `_linien_symbol`, `graduell_pixmap`, `formstil_werte`, `formstil_zeichner`, `formstile`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.linie`, `lunivo_writer.editor.text`, `lunivo_writer.editor.text.textur`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.linien`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.farbpalette`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.raster_auswahl`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/dropdown/objektmenues/smartart_menues.py`
- Direkter Qt-Import: ja
- Klassen: `_Auffrischend`
- Funktionen: `_sa`, `_sym`, `form_menue`, `level_menue`, `hierarchie_menue`, `layout_menue`, `stil_bild`, `stile_menue`, `stile_galerie`, `_farben`, `_kasten`, `_pfeil`, `_m_organigramm`, `_m_liste`, `_m_prozess`, `_m_zyklus`, `_m_pyramide`, `_m_spalten`, `_m_gruppen`, `_m_matrix`, `_m_chevron`, `_m_radial`, `_m_zielscheibe`, `_m_trichter`, `_m_zeitachse`, `_m_stufen`, `_zeile`, `_m_punktliste`, `_m_balkenliste`, `_m_beschreibungsliste`, `_m_spaltenrahmen`, `_m_bildliste`, `_m_perspektive`, `_m_konvergenz`, `_m_kartenprozess`, `_m_kreisbeziehung`, `_m_segmentzyklus`, `zeichne_miniatur`, `miniatur`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.raster_auswahl`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/dropdown/popup_lage.py`
- Direkter Qt-Import: ja
- Klassen: `PopupVerhalten`
- Funktionen: `popup_bereich`, `popup_klemmen`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`

### `oberflaeche/baukasten/dropdown/schalter_zeile.py`
- Direkter Qt-Import: ja
- Klassen: `SchalterZeile`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.schalter`

### `oberflaeche/baukasten/dropdown/teil_menue.py`
- Direkter Qt-Import: ja
- Klassen: `TeilMenueKnopf`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`

### `oberflaeche/baukasten/dropdown/text_kopf_menue_mixin.py`
- Direkter Qt-Import: ja
- Klassen: `TextKopfMenueMixin`
- Funktionen: `text_fuell_menue`, `_text_bild`
- Interne Imports: `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.farbpalette`, `lunivo_writer.oberflaeche.baukasten.dropdown.kopf_dropdown`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.fuell_voreinstellungen`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.linien_voreinstellungen`

### `oberflaeche/baukasten/dropdown/voreinstellung_menue.py`
- Direkter Qt-Import: ja
- Klassen: `VoreinstellungMenue`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.felder.karten_raster`

### `oberflaeche/baukasten/dropdown/zeile.py`
- Direkter Qt-Import: ja
- Funktionen: `dropdown_zeile`

### `oberflaeche/baukasten/felder/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/baukasten/felder/assistenten_liste.py`
- Direkter Qt-Import: ja
- Klassen: `AssistentenListe`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`

### `oberflaeche/baukasten/felder/auswahl_bereich.py`
- Direkter Qt-Import: ja
- Klassen: `AuswahlBereich`
- Funktionen: `objekte`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/baukasten/felder/auswahl_liste.py`
- Direkter Qt-Import: ja
- Klassen: `AuswahlListe`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.karte`, `lunivo_writer.oberflaeche.baukasten.basis.mass`

### `oberflaeche/baukasten/felder/farbwaehler.py`
- Direkter Qt-Import: ja
- Klassen: `Modell`, `_Kacheln`, `_Flaeche`, `_Leiste`, `_Ring`, `_Regler`, `_Proben`, `_FlaechePaar`, `_ProbeBlock`, `FarbenDialog`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/baukasten/felder/flache_reiter_leiste.py`
- Direkter Qt-Import: ja
- Klassen: `ReiterUeberlauf`, `ReiterDropdown`, `FlacheReiterLeiste`, `UeberlaufLeiste`
- Funktionen: `_gross`, `_mische`, `flach_machen`, `alle_flach`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`

### `oberflaeche/baukasten/felder/formular_gitter.py`
- Direkter Qt-Import: ja
- Klassen: `UmbruchSchalter`, `FlussLayout`, `_Einheit`, `FormularGitter`, `AngepassteReiter`
- Funktionen: `tabellen_gitter`, `abschnittstitel`, `reiter_knopf_stil`, `abschnittsband`, `mittig`, `_hoehe_bei`, `_natuerlich`, `ist_dropdown`, `einzeilig`, `felder_angleichen`, `gruppe`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste`

### `oberflaeche/baukasten/felder/kachel_feld.py`
- Direkter Qt-Import: ja
- Klassen: `KachelFeld`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.raster_auswahl`, `lunivo_writer.oberflaeche.baukasten.felder.karten_raster`

### `oberflaeche/baukasten/felder/karten_raster.py`
- Direkter Qt-Import: ja
- Klassen: `KartenRaster`
- Funktionen: `spanne_von`, `_platzieren`, `_zeilenhoehen`, `kacheln_legen`, `kachel_gitter`, `_ist_kurz`, `_alle_layouts`, `_gruppe_ins_raster`, `_gruppen_buendeln`, `kurze_gruppen_ins_raster`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`

### `oberflaeche/baukasten/felder/listen_leiste.py`
- Direkter Qt-Import: ja
- Klassen: `ListenLeiste`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.karte`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/felder/mass_feld.py`
- Direkter Qt-Import: ja
- Klassen: `MassSpin`, `EinheitFeld`
- Funktionen: `set_einheit`, `einheit`, `spin`, `einheit_name`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`

### `oberflaeche/baukasten/felder/pipette.py`
- Direkter Qt-Import: ja
- Klassen: `_Pipette`
- Funktionen: `farbe_vom_bildschirm`
- Interne Imports: `lunivo_writer.kern.farben`

### `oberflaeche/baukasten/felder/schalter.py`
- Direkter Qt-Import: ja
- Klassen: `KippSchalter`
- Funktionen: `chip_stil`, `chip_gruen_stil`, `schalter_an_stil`, `schalter_aus_stil`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`

### `oberflaeche/baukasten/felder/schiebe_feld.py`
- Direkter Qt-Import: ja
- Klassen: `SchrittFeld`, `SchiebeFeld`
- Funktionen: `_knopf`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`

### `oberflaeche/baukasten/felder/winkel_feld.py`
- Direkter Qt-Import: ja
- Klassen: `WinkelFeld`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.schiebe_feld`

### `oberflaeche/baukasten/formatierung/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/baukasten/formatierung/absatz_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `AbsatzDialog`
- Funktionen: `aus_block`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.querblatt`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dokument.tabstopp_dialog`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.mass_feld`, `lunivo_writer.oberflaeche.baukasten.formatierung.text_format`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/baukasten/formatierung/auto_felder_mixin.py`
- Direkter Qt-Import: nein
- Klassen: `AutoFelderMixin`

### `oberflaeche/baukasten/formatierung/effekte_drei_mixin.py`
- Direkter Qt-Import: ja
- Klassen: `NurDreiEffekteMixin`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.felder.winkel_feld`, `lunivo_writer.oberflaeche.baukasten.geruest.abschnitt_gruppe`

### `oberflaeche/baukasten/formatierung/formatvorlage_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `FormatvorlageDialog`
- Interne Imports: `lunivo_writer.editor.objekte.linie`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dokument.liste_dialog`, `lunivo_writer.oberflaeche.baukasten.dokument.tabstopp_dialog`, `lunivo_writer.oberflaeche.baukasten.dokument.tasten_dialog`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.formatierung.absatz_dialog`, `lunivo_writer.oberflaeche.baukasten.formatierung.rahmen_schattierung`, `lunivo_writer.oberflaeche.baukasten.formatierung.schriftart_dialog`, `lunivo_writer.oberflaeche.baukasten.formatierung.text_format`, `lunivo_writer.oberflaeche.baukasten.formatierung.texteffekt_dialog`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/baukasten/formatierung/objektformat_panel.py`
- Direkter Qt-Import: ja
- Klassen: `_Felder`, `_DreiDUntereinander`, `_TextPanel`, `ObjektFormatPanel`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.linie`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.linien`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.farbpalette`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.objekt_menues`, `lunivo_writer.oberflaeche.baukasten.dropdown.voreinstellung_menue`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.schiebe_feld`, `lunivo_writer.oberflaeche.baukasten.formatierung.texteffekt_dialog`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/formatierung/rahmen_schattierung.py`
- Direkter Qt-Import: ja
- Klassen: `_Vorschau`, `_KantenFlaeche`, `_RahmenSeite`, `_PolsterDialog`, `_SeitenOptionenDialog`, `_AbstandDialog`, `_SchattierungSeite`, `RahmenSchattierungDialog`
- Funktionen: `_kopf`, `_einstellung_symbol`, `_stil_symbol`, `_breite_symbol`, `_muster_symbol`, `_blatt_vorschau`
- Interne Imports: `lunivo_writer.editor.objekte.linie`, `lunivo_writer.editor.seite.seitenrahmen`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.linien`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.farbpalette`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.mass_feld`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/baukasten/formatierung/ruby_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `RubyDialog`
- Interne Imports: `lunivo_writer.editor.text.zeichenzusatz`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.mass_feld`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/baukasten/formatierung/schreibweise_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `SchreibweiseDialog`
- Interne Imports: `lunivo_writer.editor.text.schreibweise`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/baukasten/formatierung/schriftart_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `SchriftartDialog`
- Funktionen: `zeichen_waehlen`, `_schrift_combo`, `_schnitt_combo`, `_ueberschrift`
- Interne Imports: `lunivo_writer.editor.text.textfx`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.farbpalette`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.mass_feld`, `lunivo_writer.oberflaeche.baukasten.formatierung.text_format`, `lunivo_writer.oberflaeche.baukasten.formatierung.texteffekt_dialog`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/baukasten/formatierung/text_format.py`
- Direkter Qt-Import: ja
- Klassen: `TextFormatLeiste`
- Funktionen: `schrift_feld`, `groesse_feld`, `text_knopf`, `ausrichtung_knoepfe`, `_zeilen_symbol`, `_abstand_symbol`, `_einzug_symbol`, `_zu_format_schrift`, `_zu_format_linien`, `_zu_format_abstand`, `zu_format`, `_aus_format_unter`, `_aus_format_schriften`, `_aus_format_abstand`, `aus_format`, `zeichne_absaetze`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text.unterstreichung`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/formatierung/text_fuellarten_mixin.py`
- Direkter Qt-Import: ja
- Klassen: `TextFuellartenMixin`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.editor.objekte.bilddaten`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.farbpalette`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.objekt_menues`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.medien.bildformate`

### `oberflaeche/baukasten/formatierung/texteffekt_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `_Pfeil`, `Abschnitt`, `TexteffektPanel`, `TexteffektDialog`
- Funktionen: `seitengitter`, `_linien_icon`
- Interne Imports: `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.farbpalette`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.voreinstellung_menue`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.schiebe_feld`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/formatierung/textfeld_abschnitt.py`
- Direkter Qt-Import: ja
- Klassen: `TextfeldAbschnitt`
- Funktionen: `_still`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.schiebe_feld`, `lunivo_writer.oberflaeche.baukasten.formatierung.texteffekt_dialog`

### `oberflaeche/baukasten/formatierung/umschlossen_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `UmschlosseneZeichenDialog`
- Funktionen: `form_bild`, `_vorlagenbild`
- Interne Imports: `lunivo_writer.editor.text.zeichenzusatz`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/baukasten/geruest/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/baukasten/geruest/abschnitt_gruppe.py`
- Direkter Qt-Import: nein
- Klassen: `EinzelOffen`

### `oberflaeche/baukasten/geruest/aktionen_leiste.py`
- Direkter Qt-Import: ja
- Klassen: `AktionenLeiste`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.bauteile.fluss_layout`

### `oberflaeche/baukasten/geruest/einklappgruppe.py`
- Direkter Qt-Import: ja
- Klassen: `EinklappGruppe`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`

### `oberflaeche/baukasten/geruest/fenster_stapel.py`
- Direkter Qt-Import: ja
- Klassen: `FensterStapel`
- Funktionen: `ausfuehren`, `stapel_von`, `zeige_unter`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/geruest/panel_rahmen.py`
- Direkter Qt-Import: ja
- Klassen: `PanelRahmen`
- Funktionen: `panel_kopf`, `_knopf`, `rollflaeche`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/geruest/schmal.py`
- Direkter Qt-Import: ja
- Klassen: `_Umbruchtext`
- Funktionen: `_alle_layouts`, `_breite`, `_zeile_zu_fluss`, `_abstand`, `_tabelle_umbrechen`, `_spalten_umbrechen`, `_zeile_einheiten`, `_zeilen_umbrechen`, `_knopf_umbrechen`, `_nein`, `_beschriftungen_umbrechen`, `_kontrollfelder_umbrechen`, `_layout_umbrechen`, `schmal_machen`, `_breite_gitter`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`

### `oberflaeche/baukasten/geruest/schnellleiste_zustand.py`
- Direkter Qt-Import: nein
- Funktionen: `ohne_minus`, `knopf_aktiv`

### `oberflaeche/baukasten/geruest/spalten.py`
- Direkter Qt-Import: ja
- Klassen: `ZweiSpalter`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`

### `oberflaeche/baukasten/geruest/werkbank.py`
- Direkter Qt-Import: ja
- Klassen: `FunktionsZeile`, `Werkbank`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.karte`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.felder.karten_raster`, `lunivo_writer.oberflaeche.baukasten.felder.schalter`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.schreibhilfe_katalog`

### `oberflaeche/baukasten/geruest/zugaenglichkeit.py`
- Direkter Qt-Import: ja
- Klassen: `NamenFilter`
- Funktionen: `name_fuer`

### `oberflaeche/baukasten/geruest/zusatz_panel.py`
- Direkter Qt-Import: ja
- Klassen: `_Seite`, `ZusatzPanel`, `PanelFaehig`
- Funktionen: `zusatz_knopf`, `zusatz_kopf`, `ausfuehren_in`, `ausfuehren_im_stapel`, `leiste_fuer`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.karten_raster`, `lunivo_writer.oberflaeche.baukasten.geruest.panel_rahmen`, `lunivo_writer.oberflaeche.baukasten.geruest.schmal`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/medien/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/baukasten/medien/alternativtext_abschnitt.py`
- Direkter Qt-Import: ja
- Klassen: `AlternativtextAbschnitt`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.formatierung.texteffekt_dialog`

### `oberflaeche/baukasten/medien/bild_alternativtext_panel.py`
- Direkter Qt-Import: ja
- Klassen: `BildAlternativtextPanel`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.medien.alternativtext_abschnitt`

### `oberflaeche/baukasten/medien/bild_export.py`
- Direkter Qt-Import: ja
- Klassen: `_Karte`, `BildExportAnsicht`
- Funktionen: `_abschnitt`, `_bilder_ordner`
- Interne Imports: `lunivo_writer.dienste.bild_export`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/baukasten/medien/bild_zoom.py`
- Direkter Qt-Import: ja
- Klassen: `_Ansicht`, `BildZoomFenster`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.schiebe_feld`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/baukasten/medien/bildformate.py`
- Direkter Qt-Import: nein

### `oberflaeche/baukasten/medien/datei_symbole.py`
- Direkter Qt-Import: ja
- Funktionen: `icon_namen`, `datei_symbol`
- Interne Imports: `lunivo_writer.kern`

### `oberflaeche/baukasten/medien/design_bildchen.py`
- Direkter Qt-Import: ja
- Funktionen: `_text`, `design_zeichner`, `farbreihe_zeichner`, `schriftpaar_zeichner`, `effekt_zeichner`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.objekte`, `lunivo_writer.kern.farben`

### `oberflaeche/baukasten/medien/listen_symbole.py`
- Direkter Qt-Import: ja
- Funktionen: `liste_zeichner`
- Interne Imports: `lunivo_writer.kern.farben`

### `oberflaeche/baukasten/medien/seiten_bildchen.py`
- Direkter Qt-Import: ja
- Funktionen: `_blatt`, `_zeilen`, `seitenzahl_zeichner`, `wasserzeichen_vorschau`, `wasserzeichen_zeichner`, `plus_zeichner`, `deckblatt_zeichner`, `raender_zeichner`, `format_zeichner`, `papier_zeichner`, `textrichtung_zeichner`
- Interne Imports: `lunivo_writer.editor.seite`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`

### `oberflaeche/baukasten/medien/umbruch_symbole.py`
- Direkter Qt-Import: ja
- Funktionen: `umbruch_zeichner`
- Interne Imports: `lunivo_writer.kern.farben`

### `oberflaeche/baukasten/vorlagen/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/baukasten/vorlagen/formatvorlagen_bereich.py`
- Direkter Qt-Import: ja
- Klassen: `_Absatzmarke`, `FormatvorlagenBereich`
- Funktionen: `vorlagen_namen`, `vorlagen_schrift`
- Interne Imports: `lunivo_writer.editor.text`, `lunivo_writer.oberflaeche.band.band_leiste`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/baukasten/vorlagen/vorlagen_chips.py`
- Direkter Qt-Import: ja
- Klassen: `VorlagenChips`, `AufklappBereich`
- Funktionen: `_link`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.karte`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`

### `oberflaeche/baukasten/vorlagen/vorlagen_galerie.py`
- Direkter Qt-Import: ja
- Klassen: `_Kachel`, `VorlagenGalerie`
- Funktionen: `_blatt_bild`, `_geruest_bild`, `_datei_bild`
- Interne Imports: `lunivo_writer.adapter.qt.dokument`, `lunivo_writer.adapter.qt.seitenbild`, `lunivo_writer.dienste`, `lunivo_writer.editor.dokument`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste`, `lunivo_writer.oberflaeche.baukasten.felder.karten_raster`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/bauteile/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/bauteile/fluss_layout.py`
- Direkter Qt-Import: ja
- Klassen: `FlowLayout`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`

### `oberflaeche/bauteile/kontextmenue.py`
- Direkter Qt-Import: ja
- Funktionen: `_symbole`, `menue_bauen`, `_symbol`, `_tabellenmenue`
- Interne Imports: `lunivo_writer.kern.tabellenaktionen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.bauteile.mini_leiste`

### `oberflaeche/bauteile/lese_ende_knopf.py`
- Direkter Qt-Import: ja
- Klassen: `LeseEndeKnopf`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`

### `oberflaeche/bauteile/live_vorschau.py`
- Direkter Qt-Import: ja
- Klassen: `LiveVorschau`, `Ueberfahren`, `VorschauCombo`, `VorschauFontCombo`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`

### `oberflaeche/bauteile/mini_leiste.py`
- Direkter Qt-Import: ja
- Klassen: `MiniLeiste`, `_Zu`
- Funktionen: `_symbole`
- Interne Imports: `lunivo_writer.editor.tabelle.tabellenzustand`, `lunivo_writer.kern.tabellenaktionen`, `lunivo_writer.oberflaeche.band.band_leiste`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/bauteile/schweb_knopf.py`
- Direkter Qt-Import: ja
- Klassen: `SchwebKnopf`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/bauteile/symbole.py`
- Direkter Qt-Import: ja
- Funktionen: `pfade_original`, `pfade`, `uebersteuern`, `katalog_bild`, `pfad_bild`, `hat`, `_symbolpfad`, `eigene_zeichnung`, `_svg`, `svg_datei`, `_pixmap`, `icon`, `icon_aus_pfad`, `leeren`, `setze`, `alle_neu`
- Interne Imports: `lunivo_writer.kern`, `lunivo_writer.kern.farben`, `lunivo_writer.kern.piktogramme`, `lunivo_writer.oberflaeche`

### `oberflaeche/dialoge/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/dialoge/dokument_dialoge.py`
- Direkter Qt-Import: ja
- Klassen: `PageSetupDialog`, `HeaderFooterDialog`, `TableDialog`, `BildGroesseDialog`, `ZoomDialog`, `TabellenEigenschaftenDialog`, `BildZuschneidenDialog`
- Funktionen: `_titel`
- Interne Imports: `lunivo_writer.editor.tabelle.tabelleneigenschaften`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.mass_feld`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.dialoge.einfuegen.wasserzeichen_fenster`

### `oberflaeche/dialoge/einfuegen/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/dialoge/einfuegen/bildschirmfoto.py`
- Direkter Qt-Import: ja
- Klassen: `BereichWahl`
- Interne Imports: `lunivo_writer.kern.farben`

### `oberflaeche/dialoge/einfuegen/diagramm_fenster.py`
- Direkter Qt-Import: ja
- Klassen: `DiagrammDialog`
- Funktionen: `art_symbol`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dialoge.einfuegen.einfuegen_dialoge`

### `oberflaeche/dialoge/einfuegen/einfuegen_dialoge.py`
- Direkter Qt-Import: ja
- Klassen: `_Vorschau`, `VorschauMixin`, `FormDialog`, `_LayoutGalerie`, `SmartArtDialog`, `WordArtDialog`, `DiagrammDatenDialog`, `PiktogrammDialog`, `FormelDialog`, `DeckblattDialog`, `DatumDialog`, `BausteinDialog`
- Funktionen: `_ok`, `_layout_bildchen`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.editor.dokument`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.text.textdaten`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.smartart_menues`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.kachel_feld`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dialoge.einfuegen.diagramm_fenster`

### `oberflaeche/dialoge/einfuegen/einfuegen_fenster.py`
- Direkter Qt-Import: ja
- Klassen: `ZahlDialog`, `FelderDialog`, `AutoTextDialog`, `TrennerDialog`, `SeitenzahlDialog`, `HyperlinkDialog`, `ObjektDialog`
- Funktionen: `_titel`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.tabelle`, `lunivo_writer.editor.text`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/dialoge/einfuegen/formular_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `FormFeldDialog`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/dialoge/einfuegen/smartart_dialog_foto.py`
- Direkter Qt-Import: ja
- Klassen: `_GrosseGalerie`, `SmartArtDialogFoto`
- Funktionen: `_weg`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste`, `lunivo_writer.oberflaeche.baukasten.felder.kachel_feld`, `lunivo_writer.oberflaeche.dialoge.einfuegen.einfuegen_dialoge`

### `oberflaeche/dialoge/einfuegen/sonderzeichen.py`
- Direkter Qt-Import: ja
- Klassen: `SymbolDaten`, `_Speicher`, `Zeichenraster`, `_TastenFenster`, `SonderzeichenDialog`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dokument.tasten_dialog`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/dialoge/einfuegen/wasserzeichen_fenster.py`
- Direkter Qt-Import: ja
- Klassen: `WasserzeichenDialog`
- Funktionen: `_titel`, `_feld`, `_lage_vorbelegen`
- Interne Imports: `lunivo_writer.editor.objekte.bilddaten`, `lunivo_writer.editor.seite`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.farbpalette`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.mass_feld`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.baukasten.medien.bildformate`

### `oberflaeche/dialoge/ki/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/dialoge/ki/ki_aktions_dialoge.py`
- Direkter Qt-Import: ja
- Klassen: `SchnelleAktionDialog`, `KIAssistentDialog`, `ErgebnisseDialog`
- Interne Imports: `lunivo_writer.ki`, `lunivo_writer.ki.assistent_lauf`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dokument.erstellen_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.symbol_auswahl`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.mass_feld`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.baukasten.vorlagen.vorlagen_chips`, `lunivo_writer.oberflaeche.dialoge.ki.ki_modelle_dialoge`

### `oberflaeche/dialoge/ki/ki_dialoge.py`
- Direkter Qt-Import: ja
- Klassen: `KIEinstellungenDialog`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.chat.chat_regler`, `lunivo_writer.oberflaeche.baukasten.felder.assistenten_liste`, `lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.dialoge.ki.ki_aktions_dialoge`, `lunivo_writer.oberflaeche.dialoge.ki.ki_einstellungen_panels`, `lunivo_writer.oberflaeche.dialoge.ki.ki_modelle_dialoge`

### `oberflaeche/dialoge/ki/ki_einstellungen_panels.py`
- Direkter Qt-Import: ja
- Klassen: `_NetzLauf`, `_NetzSender`, `OfflineSprachen`, `SprachePanel`, `McpDialog`, `McpListe`, `EinwilligungenPanel`, `WebsuchePanel`, `DokumentePanel`
- Interne Imports: `lunivo_writer.ki`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.karte`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.auswahl_liste`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.listen_leiste`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`

### `oberflaeche/dialoge/ki/ki_modelle_dialoge.py`
- Direkter Qt-Import: ja
- Klassen: `_Antwort`, `AnbieterDialog`, `ModellListe`, `ModellListeDialog`, `ModellZuweisung`, `KIKonfigurationDialog`
- Funktionen: `_tags_text`, `modell_passt`, `modell_felder_fuellen`, `modell_combo`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.ki`, `lunivo_writer.oberflaeche.baukasten.basis.beschriftung`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.karte`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.auswahl_liste`, `lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.listen_leiste`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/dialoge/lesen_hilfe/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/dialoge/lesen_hilfe/hilfe_dialoge.py`
- Direkter Qt-Import: ja
- Klassen: `HilfeFenster`, `_Lesefeld`
- Funktionen: `_browser`, `_hb_bloecke`, `_hb_tastenchips`, `_hb_tabellen`, `_handbuch_gestalten`, `handbuch`, `_fuss`, `_titel`, `_dialog`, `tastenkuerzel`, `_erweiterungen_liste`, `erweiterungen`, `ueber`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.dienste.integrationen`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.kern`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.einklappgruppe`, `lunivo_writer.oberflaeche.baukasten.geruest.spalten`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/dialoge/lesen_hilfe/lesehilfe_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `LesehilfeDialog`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/dialoge/lesen_hilfe/silben_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `SilbenDialog`
- Interne Imports: `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/dialoge/lesen_hilfe/welche_hilfe.py`
- Direkter Qt-Import: ja
- Klassen: `_Umbruch`, `HilfeWannDialog`
- Funktionen: `_etiketten`, `_text`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/dialoge/oberflaeche_dialoge.py`
- Direkter Qt-Import: ja
- Klassen: `RegisterAnpassenDialog`, `SchnellzugriffDialog`, `EigeneZeichnungDialog`, `SymbolTauschenDialog`, `OberflaecheDialog`
- Funktionen: `lade_json`, `_satz`
- Interne Imports: `lunivo_writer.oberflaeche.band.band_leiste`, `lunivo_writer.oberflaeche.band.plan`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/dialoge/optionen.py`
- Direkter Qt-Import: ja
- Klassen: `OptionenAnsicht`, `OptionenDialog`
- Funktionen: `stil`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.beschriftung`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.geruest.einklappgruppe`, `lunivo_writer.oberflaeche.baukasten.geruest.spalten`, `lunivo_writer.oberflaeche.dialoge.optionen_seiten.ansicht`, `lunivo_writer.oberflaeche.dialoge.optionen_seiten.befehle`, `lunivo_writer.oberflaeche.dialoge.optionen_seiten.datei`, `lunivo_writer.oberflaeche.dialoge.optionen_seiten.gemeinsam`, `lunivo_writer.oberflaeche.dialoge.optionen_seiten.lesen`, `lunivo_writer.oberflaeche.dialoge.optionen_seiten.lunivo`, `lunivo_writer.oberflaeche.dialoge.optionen_seiten.name_ki`

### `oberflaeche/dialoge/optionen_seiten/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/dialoge/optionen_seiten/ansicht.py`
- Direkter Qt-Import: ja
- Klassen: `AnsichtSeiten`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.beschriftung`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dialoge.optionen_seiten.gemeinsam`

### `oberflaeche/dialoge/optionen_seiten/befehle.py`
- Direkter Qt-Import: ja
- Klassen: `BefehleSeiten`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.oberflaeche.band.band_leiste`, `lunivo_writer.oberflaeche.band.plan`, `lunivo_writer.oberflaeche.baukasten.basis.beschriftung`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dialoge.oberflaeche_dialoge`, `lunivo_writer.oberflaeche.dialoge.optionen_seiten.gemeinsam`, `lunivo_writer.oberflaeche.dokument.bearbeitung.zusatz_editor`

### `oberflaeche/dialoge/optionen_seiten/datei.py`
- Direkter Qt-Import: ja
- Klassen: `DateiSeiten`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.dienste.einstellungen_dienst`, `lunivo_writer.korrektur`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.dialoge`, `lunivo_writer.oberflaeche.dialoge.optionen_seiten.gemeinsam`, `lunivo_writer.oberflaeche.dokument.bearbeitung.editor_einfuegen`

### `oberflaeche/dialoge/optionen_seiten/gemeinsam.py`
- Direkter Qt-Import: ja
- Klassen: `_Seite`, `_Karte`
- Funktionen: `erklaerung`
- Interne Imports: `lunivo_writer.kern`, `lunivo_writer.oberflaeche.baukasten.basis.beschriftung`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.einklappgruppe`

### `oberflaeche/dialoge/optionen_seiten/lesen.py`
- Direkter Qt-Import: ja
- Klassen: `LesenSeiten`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche`, `lunivo_writer.oberflaeche.baukasten.basis.beschriftung`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.dialoge.ki.ki_dialoge`, `lunivo_writer.oberflaeche.dialoge.lesen_hilfe.lesehilfe_dialog`, `lunivo_writer.oberflaeche.dialoge.optionen_seiten.gemeinsam`

### `oberflaeche/dialoge/optionen_seiten/lunivo.py`
- Direkter Qt-Import: ja
- Klassen: `LunivoSeiten`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.dienste.einstellungen_dienst`, `lunivo_writer.dienste.integrationen`, `lunivo_writer.kern.farben`, `lunivo_writer.ki`, `lunivo_writer.korrektur.vorhersage`, `lunivo_writer.oberflaeche.baukasten.basis.beschriftung`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.assistenten_liste`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.dialoge.ki.ki_dialoge`, `lunivo_writer.oberflaeche.dialoge.optionen_seiten.gemeinsam`, `lunivo_writer.plattform`

### `oberflaeche/dialoge/optionen_seiten/name_ki.py`
- Direkter Qt-Import: ja
- Klassen: `NameKiSeiten`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.dialoge.optionen_seiten.gemeinsam`

### `oberflaeche/dialoge/sendungen/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/dialoge/sendungen/sendungen_dialoge.py`
- Direkter Qt-Import: ja
- Klassen: `UmschlagDialog`, `EtikettenDialog`, `SeriendruckDialog`, `RegelDialog`
- Funktionen: `_hinweis`, `_ok`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/dialoge/sendungen/serien_fenster.py`
- Direkter Qt-Import: ja
- Klassen: `EmpfaengerDialog`, `FeldDialog`, `ZuordnenDialog`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/dialoge/ueberpruefen_fenster.py`
- Direkter Qt-Import: ja
- Klassen: `WoerterDialog`, `SchutzDialog`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/dialoge/verweise/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/dialoge/verweise/verweise_dialoge.py`
- Direkter Qt-Import: ja
- Klassen: `TextmarkeDialog`, `QuelleDialog`, `QuellenDialog`
- Funktionen: `_knoepfe`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.dokument.literatur`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/dialoge/verweise/verweise_fenster.py`
- Direkter Qt-Import: ja
- Klassen: `InhaltsverzeichnisDialog`, `IndexeintragDialog`, `NummerierungDialog`, `BeschriftungDialog`, `QuerverweisDialog`
- Funktionen: `_titel`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.dokument.indexeintrag`, `lunivo_writer.editor.dokument.verweise`, `lunivo_writer.editor.dokument.verzeichnis`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`

### `oberflaeche/dialoge/vorlagen_dialog.py`
- Direkter Qt-Import: ja
- Klassen: `VorlagenDialog`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`

### `oberflaeche/dokument/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/dokument/ansicht/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/dokument/ansicht/absatz_symbol.py`
- Direkter Qt-Import: ja
- Klassen: `AbsatzSymbol`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.dokument.tabelle.tabelle_griffe`

### `oberflaeche/dokument/ansicht/blasen_flaeche.py`
- Direkter Qt-Import: ja
- Klassen: `BlasenFlaeche`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`

### `oberflaeche/dokument/ansicht/lineal.py`
- Direkter Qt-Import: ja
- Klassen: `_Lineal`, `LinealH`, `LinealV`
- Interne Imports: `lunivo_writer.editor.seite.querblatt`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`

### `oberflaeche/dokument/ansicht/modell_ansicht.py`
- Direkter Qt-Import: ja
- Klassen: `ModellAnsicht`
- Interne Imports: `lunivo_writer.adapter.qt.rendering`, `lunivo_writer.adapter.qt.seitenbild`, `lunivo_writer.core.editing`, `lunivo_writer.core.geometry`, `lunivo_writer.core.layout`, `lunivo_writer.core.layout.seitenumbruch`, `lunivo_writer.core.rendering.backend`, `lunivo_writer.core.rendering.seite`, `lunivo_writer.dienste.textsatz`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`

### `oberflaeche/dokument/ansicht/seiten_ansicht.py`
- Direkter Qt-Import: ja
- Klassen: `SeitenAnsicht`
- Interne Imports: `lunivo_writer.editor.seite.seiten_aufteilung`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`

### `oberflaeche/dokument/ansicht/vorschau_ansicht.py`
- Direkter Qt-Import: ja
- Funktionen: `aktiv`, `zeigen`, `beenden`
- Interne Imports: `lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor`

### `oberflaeche/dokument/bearbeitung/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/dokument/bearbeitung/basis.py`
- Direkter Qt-Import: ja
- Funktionen: `_ziel_fragment`
- Interne Imports: `lunivo_writer.editor.text`, `lunivo_writer.editor.text.fragmente`

### `oberflaeche/dokument/bearbeitung/dokument_editor.py`
- Direkter Qt-Import: ja
- Klassen: `DocumentEditor`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.dokument.sendungen`, `lunivo_writer.editor.dokument.verweise`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.abschnitte`, `lunivo_writer.editor.seite.anzeige_extra`, `lunivo_writer.editor.seite.seiten_aufteilung`, `lunivo_writer.editor.seite.seiten_aufteilung_deko`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.bauteile.kontextmenue`, `lunivo_writer.oberflaeche.dokument.ansicht.absatz_symbol`, `lunivo_writer.oberflaeche.dokument.bearbeitung.editor_anzeige`, `lunivo_writer.oberflaeche.dokument.bearbeitung.editor_bilder`, `lunivo_writer.oberflaeche.dokument.bearbeitung.editor_einfuegen`, `lunivo_writer.oberflaeche.dokument.bearbeitung.editor_formatierung`, `lunivo_writer.oberflaeche.dokument.bearbeitung.editor_lauf`, `lunivo_writer.oberflaeche.dokument.bearbeitung.editor_schreibhilfe`, `lunivo_writer.oberflaeche.dokument.bearbeitung.editor_seiten`, `lunivo_writer.oberflaeche.dokument.bearbeitung.editor_spalten`, `lunivo_writer.oberflaeche.dokument.bearbeitung.freie_bilder_bedienung`, `lunivo_writer.oberflaeche.dokument.bearbeitung.zusatz_editor`, `lunivo_writer.oberflaeche.dokument.tabelle.tabelle_griffe`

### `oberflaeche/dokument/bearbeitung/editor_absatzformat.py`
- Direkter Qt-Import: ja
- Klassen: `AbsatzformatMixin`
- Interne Imports: `lunivo_writer.dienste.docx_leser`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.querblatt`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.baukasten.dokument.tabstopp_dialog`, `lunivo_writer.oberflaeche.baukasten.formatierung.text_format`

### `oberflaeche/dokument/bearbeitung/editor_anzeige.py`
- Direkter Qt-Import: ja
- Klassen: `AnzeigeBaustein`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.anzeige_extra`, `lunivo_writer.editor.seite.seiten_aufteilung`, `lunivo_writer.editor.seite.umbruch`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dokument.ansicht.blasen_flaeche`

### `oberflaeche/dokument/bearbeitung/editor_bilder.py`
- Direkter Qt-Import: ja
- Klassen: `BilderBaustein`
- Interne Imports: `lunivo_writer.dienste.docx_leser`, `lunivo_writer.editor.dokument.zusatz`

### `oberflaeche/dokument/bearbeitung/editor_einfuegen.py`
- Direkter Qt-Import: ja
- Klassen: `EinfuegenMixin`
- Funktionen: `_ziel_fragment`
- Interne Imports: `lunivo_writer.editor.text.fragmente`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/dokument/bearbeitung/editor_formatierung.py`
- Direkter Qt-Import: nein
- Klassen: `FormatierungBaustein`
- Interne Imports: `lunivo_writer.oberflaeche.dokument.bearbeitung.editor_absatzformat`, `lunivo_writer.oberflaeche.dokument.bearbeitung.editor_stilformat`, `lunivo_writer.oberflaeche.dokument.bearbeitung.editor_werkzeuge`, `lunivo_writer.oberflaeche.dokument.bearbeitung.editor_zeichenformat`

### `oberflaeche/dokument/bearbeitung/editor_gemeinsam.py`
- Direkter Qt-Import: nein
- Interne Imports: `lunivo_writer.editor.layout.seitenlauf`

### `oberflaeche/dokument/bearbeitung/editor_lauf.py`
- Direkter Qt-Import: ja
- Klassen: `LaufBaustein`
- Interne Imports: `lunivo_writer.adapter.qt.geometrie`, `lunivo_writer.editor.layout.seitenlauf`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.dokument.bearbeitung.editor_gemeinsam`

### `oberflaeche/dokument/bearbeitung/editor_schreibhilfe.py`
- Direkter Qt-Import: ja
- Klassen: `SchreibhilfeBaustein`
- Interne Imports: `lunivo_writer.editor.dokument.vorlagen`, `lunivo_writer.editor.text`, `lunivo_writer.korrektur.autokorrektur`, `lunivo_writer.modelle.seite`

### `oberflaeche/dokument/bearbeitung/editor_seiten.py`
- Direkter Qt-Import: ja
- Klassen: `SeitenBaustein`
- Interne Imports: `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.seiten_aufteilung`, `lunivo_writer.editor.seite.seitenzahl`, `lunivo_writer.editor.text.silbenfarben`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.dokument.kopffuss.kopffuss_bearbeiter`

### `oberflaeche/dokument/bearbeitung/editor_spalten.py`
- Direkter Qt-Import: ja
- Klassen: `SpaltenBaustein`
- Interne Imports: `lunivo_writer.dienste.docx_leser`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte.linie`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.seiten_aufteilung`, `lunivo_writer.editor.seite.zeilennummern`, `lunivo_writer.editor.text`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.editor.text.textfx`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.dokument.bearbeitung.editor_gemeinsam`

### `oberflaeche/dokument/bearbeitung/editor_stilformat.py`
- Direkter Qt-Import: ja
- Klassen: `StilformatMixin`
- Interne Imports: `lunivo_writer.dienste.docx_leser`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.seite.querblatt`, `lunivo_writer.editor.text`, `lunivo_writer.editor.text.listen`, `lunivo_writer.editor.text.mehrstufig`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.baukasten.dokument.tabstopp_dialog`, `lunivo_writer.oberflaeche.baukasten.formatierung.text_format`

### `oberflaeche/dokument/bearbeitung/editor_werkzeuge.py`
- Direkter Qt-Import: ja
- Klassen: `EditorWerkzeugeMixin`
- Interne Imports: `lunivo_writer.dienste.docx_leser`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.bilddaten`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`

### `oberflaeche/dokument/bearbeitung/editor_zeichenformat.py`
- Direkter Qt-Import: ja
- Klassen: `ZeichenformatMixin`
- Interne Imports: `lunivo_writer.adapter.qt.bearbeitung`, `lunivo_writer.dienste.docx_leser`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.text`, `lunivo_writer.editor.text.schreibweise`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`

### `oberflaeche/dokument/bearbeitung/freie_bilder_bedienung.py`
- Direkter Qt-Import: ja
- Klassen: `FreieBilderMixin`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.dokument.bearbeitung`, `lunivo_writer.oberflaeche.dokument.bearbeitung.freie_bilder_interaktion`, `lunivo_writer.oberflaeche.dokument.bearbeitung.freie_bilder_knoepfe`, `lunivo_writer.oberflaeche.dokument.bearbeitung.freie_bilder_knoten`, `lunivo_writer.oberflaeche.dokument.bearbeitung.freie_bilder_zeichnen`

### `oberflaeche/dokument/bearbeitung/freie_bilder_geometrie.py`
- Direkter Qt-Import: ja
- Funktionen: `griff_mitte`, `abbilden`, `um_mitte_drehen`, `adj_lagen`, `drehwinkel`, `_kanten_verschieben`, `groesse_rechteck`
- Interne Imports: `lunivo_writer.editor.objekte`

### `oberflaeche/dokument/bearbeitung/freie_bilder_interaktion.py`
- Direkter Qt-Import: ja
- Klassen: `FreieBilderInteraktionMixin`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.oberflaeche.dokument.bearbeitung`, `lunivo_writer.oberflaeche.dokument.bearbeitung.freie_bilder_geometrie`

### `oberflaeche/dokument/bearbeitung/freie_bilder_knoepfe.py`
- Direkter Qt-Import: ja
- Klassen: `FreieBilderKnoepfeMixin`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.bilddaten`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.dokument.layout_dialog_objekt`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.bild_diagramm_menues`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.layout_optionen_objekt`, `lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.objekt_menues`, `lunivo_writer.oberflaeche.baukasten.medien.bildformate`

### `oberflaeche/dokument/bearbeitung/freie_bilder_knoten.py`
- Direkter Qt-Import: ja
- Klassen: `FreieBilderKnotenMixin`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.editor.objekte`, `lunivo_writer.kern.farben`

### `oberflaeche/dokument/bearbeitung/freie_bilder_zeichnen.py`
- Direkter Qt-Import: ja
- Klassen: `FreieBilderZeichnenMixin`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.editor.objekte`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.geruest`, `lunivo_writer.oberflaeche.baukasten.medien.umbruch_symbole`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dokument.bearbeitung`, `lunivo_writer.oberflaeche.dokument.bearbeitung.freie_bilder_geometrie`

### `oberflaeche/dokument/bearbeitung/freiform_bedienung.py`
- Direkter Qt-Import: ja
- Klassen: `_Abb`
- Funktionen: `aktiv`, `starten`, `beenden`, `_eintrag`, `_punkte`, `_punkt_bei`, `zeichnen`, `_speichern`, `_vorschau`, `_maus_press`, `_maus_move`, `_maus_release`, `_maus_doppel`, `maus`, `taste`
- Interne Imports: `lunivo_writer.editor.objekte`, `lunivo_writer.kern.farben`

### `oberflaeche/dokument/bearbeitung/zusatz_editor.py`
- Direkter Qt-Import: ja
- Klassen: `ZusatzMixin`
- Funktionen: `autor_farbe`
- Interne Imports: `lunivo_writer.editor.dokument.formular`, `lunivo_writer.editor.dokument.vorlagen`, `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.seite.anzeige_extra`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.kern.farben`

### `oberflaeche/dokument/dokumentfenster/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/dokument/dokumentfenster/dokument_bereich.py`
- Direkter Qt-Import: ja
- Klassen: `DocumentTab`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.dienste.datei_dienst`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.dokument.ansicht.lineal`, `lunivo_writer.oberflaeche.dokument.ansicht.modell_ansicht`, `lunivo_writer.oberflaeche.dokument.ansicht.seiten_ansicht`, `lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor`

### `oberflaeche/dokument/dokumentfenster/dokument_reiter.py`
- Direkter Qt-Import: ja
- Klassen: `DocTabs`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.thema`

### `oberflaeche/dokument/dokumentfenster/navigation.py`
- Direkter Qt-Import: ja
- Klassen: `KommentarKarte`, `NavigationPanel`
- Funktionen: `_datum`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.objekte.sprechblasen`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.karte`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.geruest.panel_rahmen`, `lunivo_writer.oberflaeche.baukasten.geruest.werkbank`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.bauteile.fluss_layout`, `lunivo_writer.oberflaeche.dokument.dokumentfenster.suchen_feld`, `lunivo_writer.oberflaeche.schreibhilfe_katalog`, `lunivo_writer.oberflaeche.thema`

### `oberflaeche/dokument/dokumentfenster/suchen_feld.py`
- Direkter Qt-Import: ja
- Klassen: `FormatvorlageWahl`, `SuchenFeld`
- Funktionen: `_gleich`, `_format_text`, `_linie`, `_absatz_format`
- Interne Imports: `lunivo_writer.editor.dokument`, `lunivo_writer.editor.seite.querblatt`, `lunivo_writer.editor.text`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.band.band_leiste`, `lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dokument.tabstopp_dialog`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.formatierung.absatz_dialog`, `lunivo_writer.oberflaeche.baukasten.formatierung.schriftart_dialog`, `lunivo_writer.oberflaeche.baukasten.formatierung.text_format`, `lunivo_writer.oberflaeche.baukasten.geruest.einklappgruppe`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/dokument/kopffuss/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/dokument/kopffuss/kopffuss_bearbeiter.py`
- Direkter Qt-Import: ja
- Klassen: `KopfFussBearbeiter`
- Funktionen: `_schrift_aus_format`, `_auszeichnung_aus_format`, `_fmt_zusammen`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.editor.seite`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dokument.kopffuss.kopffuss_felder`

### `oberflaeche/dokument/kopffuss/kopffuss_felder.py`
- Direkter Qt-Import: ja
- Klassen: `_Linie`, `_EinfuegenPanel`, `_Feld`, `_Leiste`
- Funktionen: `_stil`, `etikett_stil`, `panel_stil`, `_symbol`
- Interne Imports: `lunivo_writer.editor.seite`, `lunivo_writer.editor.text`, `lunivo_writer.editor.text.fragmente`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.karten_raster`, `lunivo_writer.oberflaeche.baukasten.medien.seiten_bildchen`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/dokument/kopffuss/noten_feld.py`
- Direkter Qt-Import: ja
- Klassen: `_Eingabe`, `NotenFeld`
- Interne Imports: `lunivo_writer.editor.dokument.zusatz`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.geruest.panel_rahmen`

### `oberflaeche/dokument/tabelle/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/dokument/tabelle/tabelle_griffe.py`
- Direkter Qt-Import: ja
- Klassen: `_Vorschau`, `_Grau`, `_Rand`, `_Griff`, `TabellenGriffe`
- Funktionen: `dunkel`
- Interne Imports: `lunivo_writer.editor.tabelle`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/dokument/tabelle/tabelle_radierer.py`
- Direkter Qt-Import: ja
- Klassen: `TabellenRadierer`
- Funktionen: `_pad`, `gitter`, `kante_finden`, `_radierer_cursor`
- Interne Imports: `lunivo_writer.editor.tabelle`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dokument.tabelle.tabelle_stift`

### `oberflaeche/dokument/tabelle/tabelle_stift.py`
- Direkter Qt-Import: ja
- Klassen: `TabellenStift`
- Funktionen: `groesse`, `_stift_cursor`, `andere_beenden`, `ueberwachen`, `cursor_zurueck`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dokument.tabelle.tabelle_radierer`

### `oberflaeche/hauptfenster/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/hauptfenster/backstage_dokument.py`
- Direkter Qt-Import: ja
- Klassen: `BackstageDokumentBaustein`
- Interne Imports: `lunivo_writer.editor.objekte.bilddaten`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.medien.bildformate`, `lunivo_writer.oberflaeche.dialoge.dokument_dialoge`

### `oberflaeche/hauptfenster/backstage_fenster.py`
- Direkter Qt-Import: ja
- Klassen: `BackstageFensterBaustein`
- Interne Imports: `lunivo_writer.editor.text`

### `oberflaeche/hauptfenster/backstage_navigation.py`
- Direkter Qt-Import: ja
- Klassen: `BackstageNavigationBaustein`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_tafel`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.thema`

### `oberflaeche/hauptfenster/backstage_objektformat.py`
- Direkter Qt-Import: ja
- Klassen: `BackstageObjektformatBaustein`
- Interne Imports: `lunivo_writer.editor.diagramme`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.objekte.bilddaten`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.baukasten.medien.bildformate`

### `oberflaeche/hauptfenster/backstage_seitenleisten.py`
- Direkter Qt-Import: ja
- Klassen: `BackstageSeitenleistenBaustein`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dokument.dokumentfenster.navigation`

### `oberflaeche/hauptfenster/backstage_steuerung.py`
- Direkter Qt-Import: nein
- Klassen: `BackstageBaustein`
- Interne Imports: `lunivo_writer.oberflaeche.hauptfenster.backstage_dokument`, `lunivo_writer.oberflaeche.hauptfenster.backstage_fenster`, `lunivo_writer.oberflaeche.hauptfenster.backstage_navigation`, `lunivo_writer.oberflaeche.hauptfenster.backstage_objektformat`, `lunivo_writer.oberflaeche.hauptfenster.backstage_seitenleisten`

### `oberflaeche/hauptfenster/bearbeiten.py`
- Direkter Qt-Import: ja
- Klassen: `BearbeitenBaustein`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.editor.text`, `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche`, `lunivo_writer.oberflaeche.baukasten`, `lunivo_writer.oberflaeche.baukasten.basis.farben`, `lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster`, `lunivo_writer.oberflaeche.baukasten.dokument.stimme_dialog`, `lunivo_writer.oberflaeche.baukasten.dokument.tabstopp_dialog`, `lunivo_writer.oberflaeche.baukasten.formatierung.absatz_dialog`, `lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.bauteile.lese_ende_knopf`, `lunivo_writer.oberflaeche.bauteile.mini_leiste`, `lunivo_writer.oberflaeche.dialoge.dokument_dialoge`, `lunivo_writer.oberflaeche.dialoge.lesen_hilfe.lesehilfe_dialog`, `lunivo_writer.oberflaeche.hauptfenster.gemeinsam`, `lunivo_writer.oberflaeche.thema`

### `oberflaeche/hauptfenster/dateien.py`
- Direkter Qt-Import: nein
- Klassen: `DateienBaustein`
- Interne Imports: `lunivo_writer.oberflaeche.hauptfenster.dateien_drucken`, `lunivo_writer.oberflaeche.hauptfenster.dateien_export`, `lunivo_writer.oberflaeche.hauptfenster.dateien_oeffnen`, `lunivo_writer.oberflaeche.hauptfenster.dateien_reiter`, `lunivo_writer.oberflaeche.hauptfenster.dateien_speichern`, `lunivo_writer.oberflaeche.hauptfenster.dateien_vorlagen`

### `oberflaeche/hauptfenster/dateien_drucken.py`
- Direkter Qt-Import: ja
- Klassen: `DateienDruckenBaustein`
- Interne Imports: `lunivo_writer.editor.dokument.verzeichnis`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.seite.druck`, `lunivo_writer.editor.seite.seiten_aufteilung`, `lunivo_writer.editor.text`, `lunivo_writer.oberflaeche.baukasten.dokument.druck_dialog`, `lunivo_writer.oberflaeche.baukasten.dokument.druckvorschau`

### `oberflaeche/hauptfenster/dateien_export.py`
- Direkter Qt-Import: ja
- Klassen: `DateienExportBaustein`
- Interne Imports: `lunivo_writer.adapter.qt.pdf_modell`, `lunivo_writer.dienste`, `lunivo_writer.dienste.bild_export`, `lunivo_writer.dienste.pdf_export`, `lunivo_writer.editor.seite.seiten_aufteilung`, `lunivo_writer.oberflaeche.baukasten.dokument.pdf_export`, `lunivo_writer.oberflaeche.baukasten.medien.bild_export`, `lunivo_writer.oberflaeche.dokument.dokumentfenster.dokument_bereich`

### `oberflaeche/hauptfenster/dateien_oeffnen.py`
- Direkter Qt-Import: ja
- Klassen: `DateienOeffnenBaustein`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.editor.objekte`, `lunivo_writer.editor.text`, `lunivo_writer.modelle.bericht`, `lunivo_writer.modelle.seite`, `lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.dokument.dokumentfenster.dokument_bereich`

### `oberflaeche/hauptfenster/dateien_reiter.py`
- Direkter Qt-Import: ja
- Klassen: `DateienReiterBaustein`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.dokument.dokumentfenster.dokument_bereich`

### `oberflaeche/hauptfenster/dateien_speichern.py`
- Direkter Qt-Import: ja
- Klassen: `DateienSpeichernBaustein`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.modelle.bericht`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.dokument.dokumentfenster.dokument_bereich`

### `oberflaeche/hauptfenster/dateien_vorlagen.py`
- Direkter Qt-Import: ja
- Klassen: `DateienVorlagenBaustein`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.editor.dokument`, `lunivo_writer.modelle.bericht`, `lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster`, `lunivo_writer.oberflaeche.dokument.dokumentfenster.dokument_bereich`

### `oberflaeche/hauptfenster/dokument_sync.py`
- Direkter Qt-Import: ja
- Klassen: `DokumentSyncMixin`
- Funktionen: `_feld_setzen`
- Interne Imports: `lunivo_writer.editor.objekte`

### `oberflaeche/hauptfenster/fenster_verwaltung.py`
- Direkter Qt-Import: ja
- Klassen: `FensterVerwaltungMixin`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.dokument.dokumentfenster.dokument_bereich`, `lunivo_writer.oberflaeche.programmfenster`

### `oberflaeche/hauptfenster/gemeinsam.py`
- Direkter Qt-Import: ja
- Klassen: `_QuickInfo`

### `oberflaeche/hauptfenster/oberflaeche.py`
- Direkter Qt-Import: nein
- Klassen: `OberflaecheBaustein`
- Interne Imports: `lunivo_writer.oberflaeche.band.band_leiste`, `lunivo_writer.oberflaeche.band.werkzeugleisten`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dialoge.oberflaeche_dialoge`

### `oberflaeche/hauptfenster/reiter_zustand.py`
- Direkter Qt-Import: ja
- Klassen: `ReiterZustandMixin`
- Interne Imports: `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.bauteile.schweb_knopf`, `lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor`, `lunivo_writer.oberflaeche.dokument.dokumentfenster.dokument_bereich`

### `oberflaeche/kontext/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/kontext/bild_werkzeuge.py`
- Direkter Qt-Import: nein
- Funktionen: `_gruppieren_menue`
- Interne Imports: `lunivo_writer.oberflaeche.band.reiter.baustein`

### `oberflaeche/kontext/diagramm_werkzeuge.py`
- Direkter Qt-Import: nein
- Interne Imports: `lunivo_writer.oberflaeche.band.reiter.baustein`

### `oberflaeche/kontext/kopf_fuss_werkzeuge.py`
- Direkter Qt-Import: nein
- Interne Imports: `lunivo_writer.oberflaeche.band.reiter.baustein`

### `oberflaeche/kontext/serien_werkzeuge.py`
- Direkter Qt-Import: nein
- Interne Imports: `lunivo_writer.oberflaeche.band.reiter.baustein`

### `oberflaeche/kontext/tabellen_werkzeuge.py`
- Direkter Qt-Import: nein
- Interne Imports: `lunivo_writer.oberflaeche.band.reiter.baustein`

### `oberflaeche/kontext/text_werkzeuge.py`
- Direkter Qt-Import: nein
- Interne Imports: `lunivo_writer.oberflaeche.band.reiter.baustein`

### `oberflaeche/kuerzel.py`
- Direkter Qt-Import: nein
- Funktionen: `als_markdown`

### `oberflaeche/lesestufen.py`
- Direkter Qt-Import: nein
- Funktionen: `aktuell`, `setze`

### `oberflaeche/programmfenster.py`
- Direkter Qt-Import: ja
- Klassen: `MainWindow`
- Interne Imports: `lunivo_writer`, `lunivo_writer.dienste.einstellungen_dienst`, `lunivo_writer.editor.text`, `lunivo_writer.kern.befehlsliste`, `lunivo_writer.kern.dokument_verwaltung`, `lunivo_writer.ki.ki_dienst`, `lunivo_writer.korrektur.korrektur_dienst`, `lunivo_writer.oberflaeche.backstage`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.bauteile.live_vorschau`, `lunivo_writer.oberflaeche.dialoge`, `lunivo_writer.oberflaeche.dialoge.lesen_hilfe`, `lunivo_writer.oberflaeche.dialoge.optionen`, `lunivo_writer.oberflaeche.dokument.dokumentfenster.dokument_reiter`, `lunivo_writer.oberflaeche.dokument.dokumentfenster.navigation`, `lunivo_writer.oberflaeche.dokument.kopffuss.noten_feld`, `lunivo_writer.oberflaeche.hauptfenster.backstage_steuerung`, `lunivo_writer.oberflaeche.hauptfenster.bearbeiten`, `lunivo_writer.oberflaeche.hauptfenster.dateien`, `lunivo_writer.oberflaeche.hauptfenster.dokument_sync`, `lunivo_writer.oberflaeche.hauptfenster.fenster_verwaltung`, `lunivo_writer.oberflaeche.hauptfenster.oberflaeche`, `lunivo_writer.oberflaeche.hauptfenster.reiter_zustand`, `lunivo_writer.oberflaeche.seitenleiste.seitenleiste`, `lunivo_writer.oberflaeche.statusleiste.statusleiste`, `lunivo_writer.oberflaeche.thema`

### `oberflaeche/schreibhilfe_katalog.py`
- Direkter Qt-Import: nein
- Klassen: `Funktion`
- Funktionen: `fuer_reiter`, `fuer_gruppe`

### `oberflaeche/seitenleiste/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/seitenleiste/panels/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/seitenleiste/panels/ki_panel.py`
- Direkter Qt-Import: ja
- Klassen: `ChatPanel`
- Interne Imports: `lunivo_writer.editor.text`, `lunivo_writer.ki.chat_antwort`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.chat.chat_blase`, `lunivo_writer.oberflaeche.baukasten.chat.chat_eingabe`, `lunivo_writer.oberflaeche.baukasten.chat.chat_leerzustand`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.geruest.panel_rahmen`

### `oberflaeche/seitenleiste/panels/schreib_panel.py`
- Direkter Qt-Import: ja
- Klassen: `FundKarte`, `VorschlagKarte`, `HinweisKarte`
- Funktionen: `kurz`, `farbe_je_art`, `_marken`, `marke`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.kern.farben`, `lunivo_writer.modelle.korrektur`, `lunivo_writer.oberflaeche.baukasten.basis.beschriftung`, `lunivo_writer.oberflaeche.baukasten.basis.karte`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/seitenleiste/seitenleiste.py`
- Direkter Qt-Import: ja
- Klassen: `SchreibhilfePanel`
- Funktionen: `werk_reiter_stil`
- Interne Imports: `lunivo_writer.dienste`, `lunivo_writer.kern.farben`, `lunivo_writer.korrektur.vorhersage`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld`, `lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf`, `lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste`, `lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste`, `lunivo_writer.oberflaeche.baukasten.felder.formular_gitter`, `lunivo_writer.oberflaeche.baukasten.felder.karten_raster`, `lunivo_writer.oberflaeche.baukasten.geruest.panel_rahmen`, `lunivo_writer.oberflaeche.baukasten.geruest.werkbank`, `lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel`, `lunivo_writer.oberflaeche.bauteile`, `lunivo_writer.oberflaeche.dialoge.lesen_hilfe.welche_hilfe`, `lunivo_writer.oberflaeche.schreibhilfe_katalog`, `lunivo_writer.oberflaeche.seitenleiste.panels.ki_panel`, `lunivo_writer.oberflaeche.seitenleiste.panels.schreib_panel`, `lunivo_writer.oberflaeche.thema`

### `oberflaeche/statusleiste/__init__.py`
- Direkter Qt-Import: nein

### `oberflaeche/statusleiste/statusleiste.py`
- Direkter Qt-Import: ja
- Klassen: `StatusBar`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.bauteile`

### `oberflaeche/thema.py`
- Direkter Qt-Import: ja
- Klassen: `_RundFilter`
- Funktionen: `kopf_symbolfarbe`, `karten_rand`, `karte_einrichten`, `_karten_rand_setzen`, `mint_abstaende`, `apply_theme`, `_ist_dunkel`, `_pfeile`, `_kreuz`, `_stil`, `_setze`, `_mint_palette`, `_helle_palette`, `_hell_feinschliff`, `Qt_white`
- Interne Imports: `lunivo_writer.kern.farben`, `lunivo_writer.oberflaeche.baukasten.basis.karte`, `lunivo_writer.oberflaeche.baukasten.basis.mass`, `lunivo_writer.oberflaeche.baukasten.basis.texte`, `lunivo_writer.oberflaeche.bauteile`

### `plattform/__init__.py`
- Direkter Qt-Import: nein

### `plattform/dateisystem.py`
- Direkter Qt-Import: nein
- Funktionen: `fsync_oeffnen`, `ordner_oeffnen`

### `plattform/pfade.py`
- Direkter Qt-Import: ja
- Funktionen: `_ort`, `data_dir`, `cache_dir`, `schriften_dir`, `piper_dirs`, `argos_dirs`, `argos_pakete_dir`, `vorlagen_dir`

### `plattform/protokoll.py`
- Direkter Qt-Import: ja
- Klassen: `SchutzFilter`
- Funktionen: `schwaerzen`, `umgebung`, `benutzerfehler`, `technischer_fehler`, `unerwartet`, `logdatei`, `einrichten`
- Interne Imports: `lunivo_writer.plattform`

### `plattform/prozess.py`
- Direkter Qt-Import: nein
- Funktionen: `bereinigte_umgebung`, `starten`, `_signal`, `beenden`

### `plattform/sperre.py`
- Direkter Qt-Import: nein
- Klassen: `SperreBelegt`
- Funktionen: `sperr_ordner`, `sperre_oeffnen`, `sperre_freigeben`

## Befehlsmodule

Diese Module enthalten bestehende Funktionen, die beim Neuaufbau berücksichtigt werden sollen.

- `kern/befehle/__init__.py`
- `kern/befehle/hauptreiter/__init__.py`
- `kern/befehle/hauptreiter/ansicht.py`
- `kern/befehle/hauptreiter/bearbeiten.py`
- `kern/befehle/hauptreiter/datei.py`
- `kern/befehle/hauptreiter/einfuegen.py`
- `kern/befehle/hauptreiter/einfuegen_objekte.py`
- `kern/befehle/hauptreiter/ki.py`
- `kern/befehle/hauptreiter/kommentare.py`
- `kern/befehle/hauptreiter/pruefen.py`
- `kern/befehle/hauptreiter/seite.py`
- `kern/befehle/hauptreiter/serien.py`
- `kern/befehle/hauptreiter/text.py`
- `kern/befehle/hauptreiter/text_absatz.py`
- `kern/befehle/hauptreiter/text_vorlagen.py`
- `kern/befehle/hauptreiter/text_zeichen.py`
- `kern/befehle/hauptreiter/ueberpruefen.py`
- `kern/befehle/hauptreiter/verweise.py`
- `kern/befehle/hilfen.py`
- `kern/befehle/kontextreiter/__init__.py`
- `kern/befehle/kontextreiter/bildtools.py`
- `kern/befehle/kontextreiter/diagrammtools.py`
- `kern/befehle/kontextreiter/formtools.py`
- `kern/befehle/kontextreiter/kontext.py`
- `kern/befehle/kontextreiter/kopffuss.py`
- `kern/befehle/kontextreiter/smartart_knoten_zustand.py`
- `kern/befehle/kontextreiter/smartarttools.py`
- `kern/befehle/kontextreiter/tabellen.py`
- `kern/befehle/kontextreiter/tabellen_format.py`
- `kern/befehle/kontextreiter/texttools.py`
- `kern/befehle/kontextreiter/zeichentools.py`


## Hinweis zur neuen Modularchitektur (keine neue Bestandsaufnahme)

Diese Datei bleibt ein historisches, statisch erstelltes Nachschlagewerk. Die oben aufgeführten Dateilisten, Importangaben und Zahlen wurden **nicht** neu erhoben und nicht als aktueller Stand bestätigt. Die neue verbindliche Zielvorgabe aus dem ersten Hauptprompt, Abschnitt 13.3, sieht einen zentralen Moduleingang für optionale Zusatzdienste vor. Daraus folgt **nicht**, dass die hier aufgelisteten Dateien bereits eine solche Modulverwaltung enthalten. Vor konkreten Änderungen sind nur die unmittelbar betroffenen Dateien zu lesen; die bestehende Pfad- und Dienstlogik ist möglichst wiederzuverwenden. Keine neue Projektanalyse oder automatische Prüfung wird durch diesen Hinweis autorisiert.
