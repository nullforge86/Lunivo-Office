# Interne Funktionen — Inventar

Vollständiges Inventar der Module, Klassen, Funktionen und Methoden von `src/lunivo_writer`. Erzeugt mit `werkzeuge/erstellung/inventar_bauen.py` aus dem Quelltext (`ast`, ohne Import); nicht von Hand ändern, sondern neu erzeugen. Die Beschreibung stammt aus der ersten Docstring-Zeile.

Stand: 524 Module, 487 Klassen, 6325 Funktionen und Methoden.

## Inhalt

- `(Wurzel)` — 3 Module
- `dienste` — 25 Module
- `dienste/docx_teile` — 19 Module
- `dienste/integrationen` — 3 Module
- `dienste/rtf` — 8 Module
- `editor` — 1 Module
- `editor/diagramme` — 11 Module
- `editor/dokument` — 14 Module
- `editor/objekte` — 17 Module
- `editor/seite` — 21 Module
- `editor/tabelle` — 5 Module
- `editor/text` — 24 Module
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
- `oberflaeche/baukasten/medien` — 9 Module
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
- `oberflaeche/dokument/ansicht` — 6 Module
- `oberflaeche/dokument/bearbeitung` — 23 Module
- `oberflaeche/dokument/dokumentfenster` — 5 Module
- `oberflaeche/dokument/kopffuss` — 4 Module
- `oberflaeche/dokument/tabelle` — 4 Module
- `oberflaeche/hauptfenster` — 20 Module
- `oberflaeche/kontext` — 7 Module
- `oberflaeche/seitenleiste` — 2 Module
- `oberflaeche/seitenleiste/panels` — 3 Module
- `oberflaeche/statusleiste` — 2 Module
- `plattform` — 6 Module

## `(Wurzel)`

### `__init__.py`

Lunivo Writer — native Textverarbeitung (Python 3, PySide6/Qt Widgets).


### `__main__.py`


### `app.py`

Einstieg: python -m lunivo_writer [Datei …]

- `main(argv)`

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
- `hinzufuegen(name, fragment, kuerzel)`
- `entfernen(name)`
- `einfuegen(cursor, baustein)` — Fügt den Baustein mit seiner Formatierung ein; ein alter Eintrag ohne Absatzdaten kommt als einfacher Text.

### `dienste/bild_export.py`

Das Dokument als Bild schreiben: jede Seite als eigene Datei oder alle Seiten untereinander als ein langes Bild.

- **class `BildWahl`**
- `_frei(pfad)` — Ein Dateiname, den es noch nicht gibt (nichts Vorhandenes wird überschrieben): „Brief (2).png“.
- `wasserzeichen(img, text)` — Den Text schräg und blass über das ganze Bild legen.
- `_speichern(img, pfad, fmt)`
- `bilder_schreiben(doc, page, noten, name, wahl)` — Schreibt die Bilder nach ``wahl.ordner``. → die geschriebenen Dateien.
- `_seitenbilder_schreiben(doc, page, noten, stamm, endung, faktor, wahl)`
- `_langes_bild_schreiben(doc, page, noten, stamm, endung, faktor, wahl)` — Langes Bild: zuerst die Höhe abschätzen, damit es nicht zu groß für das Bildformat wird.

### `dienste/datei_dienst.py`

Eine Stelle für alle Dateiformate: laden und speichern nach Endung.

- `endung_zum_filter(filter_text)` — Filtertext aus dem Speichern-Fenster → Endung (z. B. „OpenDocument-Text (*.odt)“ → „.odt“).
- **class `Loaded`**
- `ext(path)`
- `_verschluesselt(path)`
- `_entschluesseln(path, kennwort, ziel)`
- `_docx_laden(path, kennwort)`
- `_txt_laden(path)`
- `load(path, kennwort)`
- `_kopf_pruefen(path, e)` — Ein falsch benanntes oder kaputtes Dokument wird als solches gemeldet, nicht „irgendwie“ geöffnet.
- `_has_rich_content(doc)`
- `save(path, doc, page, meta, sicherung, erwartet)` — Speichert nach Endung über den sicheren Schreibweg (``sicher_schreiben``): Temp-Datei, Prüfung, Sicherungskopie der
- `_als_docx(path, ziel)` — DOTX (Vorlage) und DOCM (mit Makros) sind DOCX-Pakete mit anderem Inhaltstyp des Hauptteils; für den DOCX-Leser wird nur
- `_verschluesseln(data, kennwort)`

### `dienste/docx_leser.py`

DOCX → QTextDocument (python-docx).

- **class `_Reader`**(LesenMetadatenMixin, LesenAbsatzMixin, LesenRunsMixin, StilMixin, TabellenMixin, SeiteMixin, ObjekteMixin, TextfeldMixin)
  - `__init__(path)`
  - `run()`
  - `_nicht_unterstuetztes_melden(body)`
  - `_koerper_lesen(body)`
  - `_meta_lesen()`
- `_kinder(eltern)` — Die Blockelemente eines Körpers; Inhaltssteuerelemente (``w:sdt``) werden aufgelöst.
- `_schriften_ersatz()` — DOCX-Schriften ohne Entsprechung im System ersetzt Qt sonst durch irgendeine breite Schrift (so wurde aus „Calibri Light“ Noto Sans).
- `read_docx(path)` — → (QTextDocument, PageSettings, meta-dict, IOReport). Wirft DocumentIOError.

### `dienste/docx_schreiber.py`

QTextDocument → DOCX (python-docx).

- **class `_Writer`**(SchreibenDokumentMixin, SchreibenAbsatzMixin, SchreibenRunsMixin, SeiteSchreiber, TabellenSchreiber, ObjekteSchreiber, TextfeldSchreiber, ZusatzSchreiber)
  - `__init__(qdoc, page, meta)`
  - `_kompatibilitaet()`
  - `run()`
  - `_trim_trailing_empty()`
- `docx_daten(qdoc, page, meta)` — Baut die DOCX-Datei im Speicher. → (Inhalt, Bericht). Wirft DocumentIOError.
- `write_docx(path, qdoc, page, meta, sicherung)` — Schreibt über den sicheren Schreibweg (Temp-Datei, Prüfung, Umbenennen). Wirft DocumentIOError.

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
- `_entpacken_zaehlen(z, info, art, grenze, rest)` — Entpackt einen Eintrag nur zum Zählen. Prüft Größe, Gesamtgröße, Verhältnis und (bei XML) DTD/Entitäten.
- `_tiefe_pruefen(daten)`
- `sicheres_xml(daten)` — XML lesen wie ``ET.fromstring``, aber ohne DTD und Entitäten und mit Tiefengrenze. Wirft DocumentIOError.
- `lxml_parser()` — lxml-Parser für selbst gelesene Teile: keine Entitäten, kein Netz, keine DTD, keine Riesenknoten.

### `dienste/odt_bilder.py`

Bildimport und Rahmenbehandlung für den ODT-Reader.

- **class `_ODTBilder`**
  - `_bild_laden(bild)`
  - `_frei_angabe(frame)` — Ein Rahmen am Absatz oder an der Seite, den kein Text umfließt → Angabe wie in editor/objekte/freie_bilder.py, sonst None.
  - `rahmen(frame, cur)`

### `dienste/odt_leser.py`

ODT und FODT (OpenDocument-Text) direkt lesen — ohne Umwandlungsprogramm.

- **class `_Ort`** — Wohin der nächste Absatz kommt: ein Cursor und ob dessen Block noch leer und frei ist.
  - `__init__(cur, frei)`
- `_leerzeichen_anzahl(el)` — ``text:s``: Anzahl der Leerzeichen (1 bis 1000, bei ungültigem Wert 1).
- **class `_Leser`**(_ODTBilder, _ODTSeite, _ODTListen)
  - `__init__(inhalt, stil_wurzel, meta, bilder)`
  - `absatz(el, ort, liste)`
  - `inline(el, cur, eltern)`
  - `_inline_kind(k, cur, eltern, cf)`
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

### `dienste/odt_schreiben_basis.py`

Gemeinsame Bausteine zum Schreiben von ODT: Namensräume, Maße, Tabellen-Elemente, Bilder und frei positionierte Rahmen.

- `_mm(wert)`
- `bild_aus_format(doc, cf)` — Das Bild hinter einem Bildformat (Ressource im Dokument oder Datei), sonst None.
- `spannweite(t, r, c)` — Wie viele Spalten und Zeilen die Zelle mit Ursprung (r, c) überdeckt (gezählt, nicht columnSpan(): das liefert für
- `_png(img)`
- `_odf(element, attr, inhalt)` — Ein Element des ODF-Tabellenmodells (Namensraum ``table:``) als XML-Text.
- `_laenge(px)`
- `_frei_stil(name, a)` — Rahmenvorlage (Familie „graphic“) für ein frei positioniertes Bild: ohne Textumfluss, vor oder hinter dem Text.
- `_frei_rahmen(a, img, nr, stil, bilder)` — Ein frei positioniertes Bild als draw:frame am Absatz; die Bilddaten kommen nach ``bilder`` (Pictures/…).

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
  - `__init__(doc, rep)`
  - `_absatz_stil(bf)`
  - `_text_stil(cf)`
  - `_listen_stil(liste)`
  - `_bild(cf)`
  - `_freie_bilder(bf)`
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

### `dienste/rtf_schreiber.py`

RTF direkt schreiben — ohne Umwandlungsprogramm.

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

### `dienste/vorlesen.py`

Vorlesen: Piper (offline, gute Stimme) wenn eingerichtet, sonst speech-dispatcher (spd-say).

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
  - `_para_attr(getter, pf, st)` — Absatzeigenschaft: direkt am Absatz, sonst aus der Formatvorlage (samt Vorlagenkette).
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
  - `_start_block(bfmt, cfmt, cursor, reuse)`
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
  - `_frei(drawing, teil, inline_ok)` — Ein Bild, das frei auf dem Blatt liegt (wp:anchor ohne Textumbruch) → (Angabe, QImage); ``False``, wenn es nicht darstellbar ist
  - `_frei_anker(drawing, inline_ok)` — Anker des Bildes ohne Textumbruch (sonst None: das Bild steht im Text oder wird umflossen).
  - `_frei_bild_laden(blip, teil)` — Bilddaten des Verweises laden; None (mit Hinweis im Bericht), wenn sie fehlen oder nicht lesbar sind (zum Beispiel Vektorbild).
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
  - `_add_image(drawing, cursor, cfmt)`
  - `_frei_einfuegen(frei, cursor)` — Frei positioniertes Bild als Ressource ablegen und am Absatz verankern.
  - `_bild_im_text_laden(drawing)` — Bild eines Verweises im Text; None (mit Hinweis im Bericht), wenn keines da, die Daten fehlen oder nicht lesbar sind.
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
  - `_umbruch_seite(drawing, breite_px)` — „links“/„rechts“, wenn das Bild den Text umfließt (wrapSquare/Tight/Through); sonst leer.
  - `_eigene_vorlage(st, b)` — Eine selbst angelegte Absatzvorlage des Dokuments: der Absatz behält ihren Namen; fehlt sie im Katalog, wird sie übernommen.
  - `_vorlage_uebernehmen(st)` — Schrift, Abstände, Ausrichtung und Einzug der DOCX-Vorlage in den Katalog der Formatvorlagen übernehmen.
  - `_vorlagenfarbe(f)`

### `dienste/docx_teile/lesen_seite.py`

DOCX lesen: Seitengröße, Ränder, Abschnitte, Kopf- und Fußzeilen.

- `_kante_sichtbar(x)` — Hat die Rahmenkante (w:top …) eine sichtbare Linie?
- **class `SeiteMixin`** — DOCX lesen: Seitengröße, Ränder, Abschnitte, Kopf- und Fußzeilen.
  - `read_page()` — Einrichtung des ERSTEN Abschnitts; weitere Abschnitte stehen als Umbrüche im Text (siehe editor/seite/abschnitte.py).
  - `_section_page(s, erster, basis)`
  - `_hf_bilder(teil, ort, s, ps)` — Frei positionierte Bilder einer Kopf- oder Fußzeile (zum Beispiel ein Band über dem Briefkopf). „Am Absatz“ wird auf das Blatt
  - `_hf_abstand_mm(s, ort)` — Abstand der Kopf- bzw. Fußzeile vom Seitenrand in mm (ersatzweise 12,7).
  - `_hf_bild_im_text(angabe, dr, ort, s, ps)`
  - `_hf_bild_am_absatz(angabe, ort, s, ps)`
  - `_abschnitt_beginn(s)`
  - `_seitenschmuck(ps, sect)` — Seitenfarbe, Zeilennummern, Spalten, Standardtabstopp, Silbentrennung und Seitenrahmen.
  - `_spalten_lesen(ps, co)`
  - `_standardtabstopp(dt)` — Standardtabstopps des Dokuments (Twips) in die Textoptionen übernehmen.
  - `_seitenrahmen_lesen(ps, pb)` — Seitenrahmen (w:pgBorders): Linie der ersten sichtbaren Kante, Seiten, Kunstrahmen, Abstände und Einstellungen des Dokuments.
  - `_seitenrahmen_linie(pb, e)` — Seiten mit Linie, Farbe, Stärke, Art und Abstand zum Seitenrand aus der ersten sichtbaren Kante ``e``.
  - `_seitenrahmen_zusatz(border, pb, wert)` — Kunstrahmen, Messung vom Text, Abstände je Seite, Vordergrund und die Einstellungen des Dokuments (Kopf-/Fußzeile, Ausrichtung).
  - `_aussen_innen(s, ps)` — Gerade Seiten mit gespiegelter Ausrichtung bei gleichem Text: das ist „außen“ (ungerade rechts) bzw. „innen“ (ungerade links).
  - `_gerade_zeile(ps, attr, teil)` — Kopf- bzw. Fußzeile der geraden Seiten: gespiegelt (außen/innen) oder eigene Zeilen.
  - `_seitenzahl_art(s, ps)` — w:pgNumType: Zahlenart, „Beginnen mit“, Kapitelnummer.
  - `_hf(part)`
  - `_hf_absatztext(p)` — Text eines Kopf-/Fußzeilenabsatzes; Seitenzahlfelder werden zu {PAGE} / {PAGES}, ihr zwischengespeicherter Wert entfällt.
  - `_hf_elementtext(el, ueberspringen)` — Beitrag eines Elements zum Text: Text, Tabulator oder Platzhalter für Seitenzahl bzw. Seitenanzahl.
  - `_hf_platzhalter(anweisung)` — Feldanweisung → {PAGES} (NUMPAGES), {PAGE} (PAGE) oder leer.

### `dienste/docx_teile/lesen_stile.py`

DOCX lesen: Formatvorlagen, Schrift und Zeichenformat (Vererbung, Standardwerte, Hervorhebung).

- **class `StilMixin`** — DOCX lesen: Formatvorlagen, Schrift und Zeichenformat (Vererbung, Standardwerte, Hervorhebung).
  - `_standard_stil(art)`
  - `_ps(para)` — Absatzvorlage (mit Zwischenspeicher).
  - `_rs(run)`
  - `_kette(style)`
  - `_style_attr(style, getter)`
  - `_stil_font(style, attr)`
  - `_font_name(run, para)`
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
  - `add_table(table)`
  - `_zellbereiche(table, rows, cols)` — Zellen mit Rechteck: gleiche tc → eine Zelle → {id: [Zeile0, Spalte0, Zeile1, Spalte1, Zelle]}.
  - `_zelle_fuellen(qt, r0, c0, cell)` — Absätze der Zelle in die Qt-Zelle schreiben; verschachtelte Tabellen werden gemeldet, nicht dargestellt.
  - `_kopfzeilen(qt, table)` — Aufeinanderfolgende Kopfzeilen (w:tblHeader) ab der ersten Zeile.
  - `_tw(el)` — (Art, Wert) eines Maßelements (w:tblW, w:tcW, w:tblCellMar-Kante …); Art ``dxa``/``pct``/``auto``, Wert in Zwanzigstelpunkten bzw. Prozent.
  - `_tabellenformat(tf, table, cols)` — Tabellenbreite, Ausrichtung, Zellabstand, Rahmen (Stärke, Farbe, Stil), Innenabstand und Spaltenbreiten aus w:tblPr/w:tblGrid/w:tcW.
  - `_tw_von(pr, pfad)` — (Art, Wert) des ersten Elements am Pfad unter w:tblPr, sonst None.
  - `_tf_breite(tf, pr)`
  - `_tf_abstaende(tf, pr)` — Innenabstand der Zellen (aus den Kanten) und Zellabstand.
  - `_tf_rahmen(tf, pr, table)` — Rahmen: Stärke, Farbe und Stil der ersten sichtbaren Kante; ohne w:tblBorders nur bei Tabellenstilen mit „Grid“.
  - `_kantenformat(k, farbe)` — (Farbe, Stil, Stärke) einer Rahmenkante; ohne Farbangabe bleibt ``farbe``.
  - `_tf_spalten(tf, table, cols)` — Spaltenbreiten: je Spalte tcW der ersten ungeteilten Zelle; fehlt tcW in der Spalte ganz, gilt die Gitterbreite.
  - `_spalten_tcw(table, cols)` — Je Spalte das Breitenmaß (w:tcW) der ersten ungeteilten Zelle → (Maße, gefunden).
  - `_spaltenlaenge(a)` — Qt-Länge aus (Art, Wert): dxa → fest, pct → Prozent; sonst None.
  - `_zeilenhoehen(qt, table)` — w:trHeight je Zeile als Mindesthöhe übernehmen (wie der Befehl „Zeilenhöhe“: Eigenschaft plus Innenabstand).

### `dienste/docx_teile/lesen_textfelder.py`

DOCX lesen: Textfelder (``wps:wsp`` mit ``wps:txbx``/``wps:linkedTxbx``) und ihre Verknüpfungsketten.

- **class `TextfeldMixin`** — DOCX lesen: Parameter von Textfeldern, Läufe darin und Verknüpfungen.
  - `_textfeld_daten(drawing, wsp)` — Die Parameter eines Textfelds (``editor/objekte/frei_objekt.py``): genau die gespeicherten aus dem Titel („lunivo:“), sonst aus dem Text des
  - `_textfeld_aus_titel(drawing)` — Die vom Programm gespeicherten Parameter aus dem Titel des Objekts, sonst None.
  - `_textfeld_laeufe(wsp)` — Läufe aller Absätze des Kastens; Absätze werden durch einen Lauf mit Zeilenumbruch getrennt.
  - `_textfeld_lauf(r, t)`
  - `_textfeld_zeichen(rp, lauf)` — Fett, Kursiv, Durchgestrichen, Unterstrichen, Hoch-/Tiefgestellt.
  - `_textfeld_farben_groesse(rp, lauf)` — Schriftfarbe, Hervorhebung (Hintergrund) und Größe.
  - `_textfeld_kette(wsp, daten)` — Verknüpfung (``wps:linkedTxbx`` mit Kette und Stelle): Kennung des Felds sowie Vorgänger und Nachfolger.
  - `_ketten_bereinigen()` — Nach dem Lesen: Verweise auf Folgefelder, die es nicht gibt, entfernen.
  - `_kette_bereinigen_absatz(b, ids)` — Entfernt in den Textfeldern des Absatzes Verweise (weiter, von) auf unbekannte Felder und schreibt den Absatz neu, wenn nötig.

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
  - `_png_bytes(img)`
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

- **class `SeiteSchreiber`** — DOCX schreiben: Seite, Abschnitte, Kopf- und Fußzeilen.
  - `write_page()` — Dokumentweite Einstellungen (Hintergrund, Silbentrennung) und der letzte Abschnitt in der Schlusseinrichtung des Textes.
  - `write_section(s, p, typ, nr)` — Einen Abschnitt (python-docx Section) nach Einrichtung p schreiben; nr = Nummer des Abschnitts (für verknüpfte Kopfzeilen).
  - `_kopf_fuss_paare(s, p)` — Alle Kopf-/Fußzeilen des Abschnitts als (Teil, Inhalt, verknüpft, Ort[, Seitenart]); Erstseite und gerade Seiten nur bei Bedarf.
  - `_gerade_seiten_getrennt()` — „außen“/„innen“ brauchen getrennte Kopf-/Fußzeilen für gerade Seiten (w:evenAndOddHeaders gilt für das ganze Dokument);
  - `_kopf_fuss_schreiben(part, hf, ort, seite, p, nr)` — Text (mit Feldern) und freie Bilder einer Kopf- oder Fußzeile; leere Zeilen im ersten Abschnitt bleiben ungeschrieben.
  - `_kopf_fuss_text(part, hf, seite)`
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

- `_twips(px)` — Bildpunkte → Zwanzigstelpunkte.
- `_wel(tag, **attr)` — DOCX-Element mit Attributen im Namensraum w.
- **class `TabellenSchreiber`** — DOCX schreiben: Tabellen (Zellen, Rahmen, Maße).
  - `write_table(qt, container)`
  - `_zelle_schreiben(t, cell, r, c)` — Eine Zelle (bei verbundenen Zellen den ganzen Bereich) mit Format und den Absätzen ihres Inhalts.
  - `_tabelle_eigenschaften(t, qt)` — Tabellenbreite, Ausrichtung, Zellabstand, Rahmen, Innenabstand (w:tblPr, in Schema-Reihenfolge), Spaltenbreiten
  - `_tabellenbreite(f, inhalt)` — Breite der Tabelle in Zwanzigstelpunkten → (Breite, Art pct/dxa/auto, Wert für w:tblW).
  - `_tblpr_elemente(f, art, wert)` — Neue Kindelemente von w:tblPr in Schema-Reihenfolge: Breite, Ausrichtung, Zellabstand, Rahmen, Innenabstand.
  - `_tabellenrahmen(f)`
  - `_spaltenbreiten(f, n, breite)` — Spalten: Fest -> dxa, Prozent -> pct, sonst auto (Gitterbreite aus dem Rest) → (Vorgaben, Gitterbreiten).
  - `_zellbreiten(t, lang, w, n)` — w:tcW jeder Zelle: eigene Vorgabe bei einfacher Zelle, Summe der Gitterbreiten bei verbundenen.
  - `_zeilenhoehe(drow, qt, r)` — Mindesthöhe der Zeile (Z_MINHOEHE, Bildpunkte) als w:trHeight mit hRule=atLeast, in Zwanzigstelpunkten.
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
  - `__init__(daten)`
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

Unterpaket ``dokument`` von ``lunivo_writer.editor``.


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
- `_form_text(p, art, r, text, fuell)`
- `form_bild(art, breite, hoehe, fuell, linie, strich, text, skala, adj, fuell_art, punkte)` — ``skala``: Bild in dieser Auflösung (Maße und Strich bleiben logisch, das Bild ist ``skala``-mal so groß) — für scharfe freie Formen.
- `wordart_vorlage_bild(text, nr, schrift, pt)` — WordArt nach einem der 15 Stile der Galerie: Füllverlauf, Kontur und Schatten.
- `wordart_bild(text, stil, schrift, pt, farbe, vorlage)`
- `diagramm_bild(art, titel, kategorien, reihen, b, h)` — ``art``: Untertyp aus ``editor.diagramme.diagramm.TYPEN`` oder einer der früheren Namen (Säulen, Balken, Linie, Kreis).
- `piktogramm_bild(name, px, farbe)`
- `formel_teile(text)` — Einfache Schreibweise → [(Text, "normal"\|"hoch"\|"tief")]:  a^2  x_{12}  sqrt(x)  frac(a,b)  \alpha
- `formel_bild(text, pt, farbe)` — Die Formel als Bild (Vorschau im Fenster „Formel“ und in der Gleichungsgalerie).
- `formel_einfuegen(ed, text)`
- `_tabelle(ed, zeilen, kopf, breit)`
- `schnelltabelle(ed, name)`
- `deckblatt_einfuegen(ed, vorlage, titel, untertitel, autor, datum)`
- `datei_symbol_bild(name, symbol, breite)` — Dateisymbol mit Namen darunter (Einfügen ▸ Objekt ▸ Als Symbol anzeigen).
- `text_aus_datei(ed, pfad)`
- `datum_feldanweisung(fmt)` — Qt-Datumsformat → DOCX-Feld (DATE, bei reinen Uhrzeiten TIME) für „Automatisch aktualisieren“.
- `datum_text(fmt, sprache)`
- `initiale(ed, zeilen)` — Erster Buchstabe des Absatzes groß (Hängende Initiale ist mit Qt nicht möglich — er steht in der Zeile).
- `textfeld(ed, text, breite)` — Ein Textfeld als einzellige Tabelle mit Rahmen (frei schwebende Textfelder kennt Qt nicht).
- `_bild_cursor(ed)`
- `bild_ersetzen(ed, wandle)` — wandle(QImage) → QImage; das Bild im Text wird durch das Ergebnis ersetzt (Anzeigebreite bleibt, Seitenverhältnis folgt).
- `bild_original(ed)`
- `farbe_anwenden(img, modus)`
- `zuschneiden(img, links, oben, rechts, unten)`
- `drehen(img, art)`

### `editor/dokument/fassungen.py`

Fassungen eines Dokuments mit verfolgten Änderungen, für die Anzeige „Original“: eine Kopie, in der jede Einfügung fehlt und jede

- `_stuecke(doc)`
- `original(doc)`
- `bearbeiter(doc)`
- `zeiten(doc)`

### `editor/dokument/felder.py`

Felder einfügen (Einfügen ▸ Schnellbausteine ▸ Felder …) wie in Kays Vorlage: Feldnamen, Feldfunktionen und Assistent.

- `vorgabe(name)`
- `_schalter(anweisung, zeichen)`
- `_ohne_schalter(anweisung)`
- `schreibweise(n, art)`
- `zahl_formatieren(wert, muster)` — Zahl nach einem Muster wie ``#.##0,00``, ``0 %`` (deutsche Schreibweise); ohne Muster so kurz wie möglich.
- `_seitenzahl(wort, k, art)` — NUMPAGES / SECTIONPAGES.
- `_zeitfeld(wort, roh, k)` — TIME / DATE / PRINTDATE.
- `ergebnis(anweisung, kontext)` — Das Feldergebnis jetzt. ``kontext`` aus ``kontext_sammeln`` (alle Angaben freiwillig).
- `formel(text, kontext)` — Ausdruck rechnen; ValueError bei Fehlern. Bereiche (ABOVE …) kommen aus ``kontext["bereiche"]``, Textmarken aus
- `_fehler(n)`
- `_funktion(n, w)`
- `_zahl(text)`
- `tabellen_bereiche(ed)` — Zahlen über, unter, links und rechts der Zelle an der Schreibmarke (leer außerhalb von Tabellen).
- `kontext_sammeln(ed, autor, pfad)`
- `feld_einfuegen(ed, anweisung, text, versteckt)` — ``versteckt``: ausgeblendeter Text (TC-Einträge stehen wie in Textprogrammen unsichtbar im Text).

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
- `bereiche(doc)` — [(von, bis, Feld-Daten)] aller Felder; zusammenhängende Stücke mit gleichen Daten sind ein Feld.
- `feld_an(doc, pos)`
- `_ersetzen(ed, v, e, m, text, leer)`
- `wert_von(doc, v, e)`
- `_klick_kasten(ed, v, e, m, fenster)`
- `_klick_auswahl(ed, v, e, m, fenster)`
- `_klick_datum(ed, v, e, m, fenster)`
- `_klick_text(ed, v, e, m, fenster)`
- `_klick_knopf(ed, v, e, m, fenster)`
- `klick(ed, pos, fenster)` — Klick in ein Feld: Kontrollkästchen wechselt, Auswahl zeigt die Liste, Text und Datum fragen nach dem Wert, die Schaltfläche löst
- `_c(ed, pos)`
- `_ist_leer(doc, pos)`
- `_knopf_aktion(ed, m, fenster)`
- `alle_zuruecksetzen(ed)` — Alle Felder auf ihren Anfangswert (Platzhalter, leeres Kästchen) zurücksetzen.
- `daten(doc)` — [(Name, Wert)] aller Felder mit Wert (ohne Platzhalter und Schaltflächen).
- `nur_formulardaten(d)` — „Nur Formulardaten drucken“ in der KOPIE: Text außerhalb der Felder wird unsichtbar, Bilder und Hintergründe entfallen.

### `editor/dokument/gehe_zu.py`

„Gehe zu“: Sprungziele im Dokument — Seite, Zeile (Absatz), Überschrift, Textmarke, Kommentar, Fußnote, Endnote, Tabelle, Bild,

- `_kurz(t, n)`
- `_tabellen(rahmen)`
- `maximum(ed, art)` — Obergrenze für Seite und Zeile.
- `seitenstart(ed, n)`
- `zeilenstart(ed, n)`
- `_ziele_ueberschrift(ed, doc)`
- `_ziele_textmarke(ed, doc)`
- `_ziele_beschriftung(ed, doc)`
- `_ziele_kommentar(ed, doc)`
- `_ziele_note(art)`
- `_ziele_tabelle(ed, doc)`
- `_ziele_bild(ed, doc)`
- `_ziele_abschnitt(ed, doc)`
- `ziele(ed, art)` — [(Beschriftung, Position)] für die Listen-Arten.
- `springen(ed, pos)`
- `_objekte(doc, nur_art)`
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

### `editor/dokument/literatur.py`

Quellen und Zitierweisen (APA, Harvard, IEEE, Chicago, DIN ISO 690).

- `_nachname(autor)`
- `_autoren(autor)`
- `zitat(q, weise, nr)`
- `eintrag(q, weise, nr)`
- `literaturverzeichnis(quellen, weise)`

### `editor/dokument/sendungen.py`

Sendungen: Umschlag, Etiketten, Seriendruck (mit Feldern, Adressblock, Regeln), Formularfelder.

- `umschlag_aufbauen(ed, format_name, absender, empfaenger)`
- `etiketten_aufbauen(ed, bogen, text, gleich)`
- `tabelle_lesen(roh)`
- `felder_im_text(doc)`
- `feld_einfuegen(ed, name)`
- `adressblock_einfuegen(ed, was)`
- `regel_einfuegen(ed, feld, wert, dann, sonst)`
- `_satz_einsetzen(doc, satz, von_bis)` — Felder und Regeln mit den Werten von ``satz`` füllen (``von_bis``: nur in diesem Bereich).
- `brief_fuer(vorlage, satz)` — Ein Brief. Steht „Nächster Datensatz“ im Text, gilt hinter jeder solchen Stelle der nächste Satz der Liste ``satz``.
- `saetze_je_brief(vorlage)` — Wie viele Datensätze ein Brief verbraucht (1 + Zahl der Felder „Nächster Datensatz“).
- `gruppen(vorlage, saetze)`
- `serienbrief_erzeugen(quelle, saetze, ziel)` — Alle Briefe in EIN Dokument, durch Seitenumbrüche getrennt. → Zahl der Briefe.
- `quelle_lesen(pfad)` — Empfängerliste aus einer Textdatei (CSV mit ; oder , oder Tabulator; erste Zeile = Spaltennamen). → (Spalten, Sätze) oder None.
- `zugeordnet(satz, zuordnung)` — Satz mit den Namen der Felder im Text: ``zuordnung`` {Feld im Text: Spalte der Quelle}; ohne Eintrag gilt der gleiche Name.
- `felder_hervorheben(doc, an)` — Hintergrund der Felder {{…}} an oder aus. Gehört zum letzten Bearbeitungsschritt und lässt „geändert“ wie es war.
- `naechster_einfuegen(ed)` — Feld „Nächster Datensatz“: dahinter füllt der nächste Satz die Felder (z. B. mehrere Etiketten auf einem Blatt).
- `_ressourcen(quelle, ziel)`
- `form_textfeld(ed, text)`
- `form_kasten(ed, beschriftung)`
- `form_knopf(ed, aufschrift)`
- `kasten_umschalten(ed, pos)` — Klick auf ein Kontrollkästchen ☐/☒ wechselt den Zustand.

### `editor/dokument/vergleich.py`

Dokumente vergleichen und zusammenführen — das Ergebnis sind verfolgte Änderungen (einfügen/löschen, mit Autor und Datum).

- `_absaetze(doc)`
- `ops_bestimmen(basis, andere, autor)` — Änderungen von `basis` nach `andere` als Operationen auf den Absätzen von `basis`.
- `_bereich(op)`
- `zusammenlegen(listen)` — Operationen mehrerer Autoren vereinen; überschneidende Löschungen verschiedener Autoren → die erste gilt, die andere ist Konflikt.
- `_jetzt()`
- `_markieren(doc, von, bis, art, autor, datum)`
- `_op_loeschen(ziel, blk, op, datum)` — Die Zeichen ``von``…``bis`` des Absatzes als gelöscht markieren; bereits verfolgte Zeichen bleiben, wie sie sind. → Zahl der Zeichen.
- `_op_einfuegen(ziel, blk, op, datum)` — Text im Absatz als verfolgte Einfügung. → Zahl der Zeichen.
- `_op_absatz_einfuegen(ziel, blk, op, datum)` — Einen ganzen Absatz der Quelle als verfolgte Einfügung vor ``blk`` (ohne ``blk``: hinter dem letzten Absatz). → Zahl der Zeichen.
- `anwenden(ziel, ops, datum)` — Operationen als verfolgte Änderungen in `ziel` schreiben (von hinten nach vorn, damit die Stellen stimmen).
- `vergleichen(basis, andere, autor)`
- `zusammenfuehren(basis, fassungen)`

### `editor/dokument/verweise.py`

Beschriftungen, Textmarken, Querverweise, Stichwörter und Zitate — Funktionen am Editor.

- `seq_format(anweisung)` — Zahlschreibweise aus einer Feldanweisung ``SEQ Abbildung \* ROMAN`` (Vorgabe arabisch).
- `naechste_nummer(ed, label, zahl)` — Nummer, die eine neue Beschriftung ``label`` an der Schreibmarke bekäme (für die Anzeige im Fenster).
- `beschriftung_einfuegen(ed, label, text, oben, *, nach, ohne_bezeichnung, zahl)` — Beschriftung „Abbildung 1: Text“ unter (``oben``: über) dem Objekt oder Absatz. ``nach`` ersetzt „: Text“ durch genau diesen
- `beschriftungen_nummerieren(ed)`
- `beschriftungen_liste(ed)`
- `lesezeichen_liste(ed, versteckte)` — [{name, von, bis}] — zusammenhängende Textstücke mit demselben Namen. ``versteckte=False`` lässt die Marken weg, die mit
- `lesezeichen_name_gueltig(name)`
- `lesezeichen_setzen(ed, name)`
- `lesezeichen_loeschen(ed, name)`
- `lesezeichen_gehe(ed, name)`
- `intern_springen(ed, href)`
- `verweisen_auf(art)`
- `_ziele_absaetze(ed)` — Überschriften und nummerierte Absätze.
- `_ziele_beschriftungen(ed)`
- `_ziele_textmarken(ed)`
- `_ziele_noten(ed)` — Fußnoten (1, 2, …) und Endnoten (i, ii, …) in Textreihenfolge.
- `querverweis_ziele(ed)` — Mögliche Ziele: nummerierte Absätze, Überschriften, Textmarken, Fuß- und Endnoten, Beschriftungen.
- `_seq_fragment(blk)`
- `_bezeichnung_nummer(blk)` — „Abbildung 2“ — der Text der Beschriftung bis einschließlich der Nummer.
- `_beschriftungstext(blk)` — Der Text hinter der Nummer, ohne Doppelpunkt.
- `marke_sichern(ed, ziel)` — Name der Textmarke am Ziel. Fehlt eine, bekommt der Bereich des Ziels eine verborgene Textmarke „_Ref…“.
- `querverweis_text(ed, ziel, wie, oben_unten)` — Der Text, den der Querverweis zeigt. wie: "text", "nummer", "nur_text", "seite" oder "obenunten".
- `querverweis_einfuegen(ed, ziel, wie, *, link, oben_unten)` — Querverweis an der Schreibmarke (siehe ``querverweis_text``); ``link`` macht ihn zum internen Hyperlink (Strg+Klick).
- `index_eintragen(ed, e, alle)` — Indexeintrag ``e`` (``editor.dokument.indexeintrag.Eintrag``) an die Markierung setzen (ohne Markierung: das Wort an der
- `index_markieren(ed, term)`
- `zitat_einfuegen(ed, q)`
- `quelle_tag(quellen, q)` — Eindeutiger Kurzname (Nachname + Jahr).

### `editor/dokument/verzeichnis.py`

Verzeichnisse: Inhalt, Abbildungen, Tabellen, Stichwörter, Literatur.

- `toc_opt_text(opt)`
- `toc_opt_lesen(text)`
- `toc_optionen(doc)` — Einstellungen des ersten Inhaltsverzeichnisses im Dokument (None, wenn es keines gibt).
- `_ueberschriften(doc, ebenen)`
- `_toc_marke(doc, pos, vergeben)` — Name der verborgenen Textmarke an der Überschrift bei ``pos``; fehlt sie, wird sie gesetzt.
- `_alle_toc_marken(doc)`
- `_beschriftungen(doc, label)`
- `_stichwoerter(doc)` — [(Eintrag, Position)] aus den markierten Textstellen (eine Stelle je zusammenhängender Markierung).
- `_index_zeilen(editor)` — Zeilen des Stichwortverzeichnisses: Haupteinträge, darunter eingerückt die Untereinträge; „Siehe …“ statt Seitenzahl,
- `_seiten(editor, positionen)`
- `zeilen_fuer(editor, art, opt)` — → [(Ebene, Text, Seitenangabe)]; beim Inhaltsverzeichnis mit Verknüpfungen (``opt["links"]``) als viertes die Textmarke.
- `_kopf_schreiben(cur, art, o, neuer_block)` — Die Überschrift des Verzeichnisses; am Absatz stehen Art und (beim Inhaltsverzeichnis) die Optionen.
- `_zeilenformat(art, lvl, o, rechts, breite)` — Absatzformat einer Verzeichniszeile: Einzug nach Ebene; ``rechts``: Seitenzahl am rechten Rand, davor das Füllzeichen.
- `_seite_schreiben(cur, seite, zf, rechts)` — Die Seitenangabe hinter den Text: ein Text oder Stücke (Text, fett, kursiv), wie sie das Stichwortverzeichnis liefert.
- `_schreibe(cur, editor, art, zeilen, neuer_block, opt)`
- `verzeichnis_einfuegen(editor, art, opt)` — Verzeichnis an der Schreibmarke einfügen. Gibt es schon ein Inhaltsverzeichnis, wird es mit ``opt`` neu geschrieben.
- `_bereiche(doc)` — [(Art, erste Blockposition, letzte Blockposition)] zusammenhängender Verzeichnisblöcke.
- `verzeichnis_aktualisieren(editor, nur)` — Alle Verzeichnisse (oder nur die der Art ``nur``) neu schreiben; gibt die Zahl der Zeilen zurück.
- `vorhanden(doc, art)`
- `_neu_schreiben(editor, nur, opt_neu)`

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

## `editor/objekte`

### `editor/objekte/__init__.py`

Unterpaket ``objekte`` von ``lunivo_writer.editor``.


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

- `ziel(ed)` — („frei“, Schlüssel, Angabe, Bild) oder („text“, Cursor) für das markierte Bild; sonst None.
- `_achse_lesen(a, waagerecht)`
- `verschieben_wahl(a)` — Vorwahl der Radios „Mit Text verschieben“ / „Fester Text“ im Popup Layoutoptionen eines freien Objekts: ``"mit_text"``, ``"fest"`` oder
- `lesen(ed, z)`
- `_box(page, bezug, waagerecht)`
- `_achse_schreiben(a, w, page, waagerecht)`
- `_mass(w, page, waagerecht, alt)`
- `anwenden(ed, z, werte)` — Schreibt die Wahl des Fensters (oder eines Teils davon: nur die genannten Schlüssel) auf das Bild.
- `_abstand_setzen(ed, abstand)` — „Abstand zum Text“ (oben/unten/links/rechts, mm): die Ränder des Rahmens, in dem das umflossene Bild schwebt.
- `_speichern_frei(ed, key, neu)`
- `_text_zu_frei(ed, c, w, hinter)` — Ein Bild im Text wird frei: es verlässt die Zeile und liegt, wo der Absatz beginnt (dort lässt es sich ziehen).
- `_frei_zu_text(ed, key, a, bild, w)` — Ein freies Bild kommt in den Text: es steht am Anfang seines Absatzes (in der Zeile, links/rechts umflossen oder allein).
- `format_lesen(ed, z)` — Füllung, Kontur und Effekte des markierten freien Bildes im Format des Panels (``ObjektFormatPanel``); sonst None.
- `fx_alle(ed, fx)` — Seitenlayout ▸ Effekte: dieselben Effekte an alle frei liegenden Bilder und Formen des Dokuments (``{}`` nimmt sie weg). → Anzahl.
- `format_aus_panel(ed, z, werte)` — Wendet die Werte des Panels an: Füllung, Kontur und alle Effekte (fehlende Effekte sind ausgeschaltet).
- `format_setzen(ed, z, fuell, rand, rand_teil, fx)` — Füllung (``fuell``: Wörterbuch oder None) und/oder Kontur (``rand``: Wörterbuch oder None; ``rand_teil`` ändert nur einzelne Angaben der
- `fuellbild_setzen(ed, z, bild)` — „Füllung ▸ Bild“: das Bild als Füllung; im Text liegt es als Ressource des Dokuments, in der Kopfzeile am Bild selbst.
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
- `frei_entfernen(ed)` — Das gewählte freie Bild löschen (wie die Entf-Taste).

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

- `objekt(f)`
- `ist_form(f)`
- `form_daten(o, breite, hoehe)`
- `_zeichnen(d)`
- `_gruppe_zeichnen(kinder)`
- `_ersetzen(ed, c, img, o, f, breite, hoehe)`
- `frei_daten(ed)` — Die Parameter der gewählten Form als freies Objekt (Kopie) oder None.
- `aendern(ed, **felder)` — Parameter der markierten Form ändern (fuell, linie, strich, text, form, breite, hoehe) und neu zeichnen. Eine als freies Objekt
- `vorlage(ed, name)`
- `_auswahl_formen(ed)` — Alle Formbilder der Markierung (Position, Format); nur wenn die Markierung sonst leer ist.
- `gruppieren(ed)` — → '' bei Erfolg, sonst die Begründung.
- `gruppe_aufheben(ed)`
- `zeichenbereich_bild(d, skala)`
- `zeichenbereich_einfuegen(ed)` — Als freies Objekt (``frei_objekt.py``): Rahmen mit Griffen zum Skalieren und Schnellleiste rechts daneben.
- `in_zeichenbereich(ed, form)` — Form in den gewählten Zeichenbereich setzen; False, wenn keiner gewählt ist (dann kommt die Form in den Text).
- `E_ist_linie(form)`
- `wordart_daten(ed)` — Die Parameter des gewählten WordArt (Kopie) oder None.
- `wordart_aendern(ed, **kw)` — Parameter des gewählten WordArt ändern (None entfernt den Schlüssel) und neu zeichnen; ``form_fuell``/``form_linie``/``form_strich``/
- `anpass_griffe(form, rect, adj)` — Lage aller Anpassungsgriffe der Form im Rechteck ``rect`` (QRectF, beliebiges Koordinatensystem; Ergebnis im selben) — leer, wenn die Form
- `anpass_griff(form, rect, adj, index)` — Lage des Griffs ``index`` (QPointF) oder None, wenn die Form keinen hat.
- `anpassen(form, wert, adj, index)` — Neue Parameterliste für ``daten["adj"]``: Parameter ``index`` = ``wert`` (begrenzt), die übrigen bleiben; leer bei einer Form ohne Griff.
- `anpass_wert(form, rect, punkt, index)` — Der Parameter, den der gezogene Griff ``index`` an ``punkt`` ergibt (für das Ziehen mit der Maus; mit ``anpassen`` speichern).
- `anpass_setzen(ed, wert, index)` — Parameter ``index`` der gewählten freien Form setzen und neu zeichnen.
- `form_wechseln(ed, name)` — Die gewählte freie Form durch ``name`` ersetzen; Größe, Füllung und Kontur bleiben, die Anpassung (``adj``) fällt weg.

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
- `einfuegen(ed, art, daten, b, h)` — Fügt das Objekt als freies Bild am Absatz der Schreibmarke ein (steht dort Text, in einem neuen Absatz darunter), wählt es aus —
- `bild_einfuegen(ed, img, bb, hh, art, daten, alt)` — Der gemeinsame Weg aller freien Bilder: ``img`` als Ressource, die Angabe am Absatz der Schreibmarke (steht dort Text, in einem neuen
- `ziel(ed)` — (Art, Daten, Schlüssel, Angabe, Bild) des gewählten Objekts (WordArt, Textfeld, Form, Diagramm, SmartArt) oder None.
- `art_gewaehlt(ed)`
- `daten_lesen(ed, art)`
- `aendern(ed, art, **kw)` — Parameter des gewählten Objekts ändern (siehe ``_aendern_innen``). Schreibt der Benutzer gerade im Objekt und hat Text markiert, gelten
- `_daten_vorbereiten(d, kw)` — Vor dem Ändern: Vorlage und neuer Text setzen Altes zurück, ein Zeichenformat fürs ganze Objekt löscht gleiche Angaben der Läufe.
- `_form_daten_setzen(d, k, v)` — Bei einer Form: Farben der Form selbst, kein Kasten ums Bild.
- `_kasten_setzen(neu, a, k, v)` — Füllung, Strichstärke, Effekt und Linie des Kastens ums Objekt.
- `_eintrag_setzen(art, k, v, d, neu, a)` — Ein Schlüssel von ``kw`` (außer Größe) in ``daten`` oder in den Kasten schreiben.
- `_bild_erneuern(ed, art, d, a, bild, b, h)` — Neues Bild des Objekts zeichnen und als Dokument-Ressource anlegen: (Name, Breite, Höhe).
- `_aendern_innen(ed, art, **kw)` — Parameter des gewählten Objekts ändern und neu zeichnen. ``breite``/``hoehe`` (px) ändern die Größe; ``form_fuell`` (Farbe oder ``""``)
- `daten_still(ed, art, **kw)` — Daten des gewählten Objekts ändern, ohne das Bild neu zu zeichnen (z. B. die Auswahl eines Diagrammteils); None entfernt den Schlüssel.
- `nach_groesse(ed, neu)` — Nach dem Ziehen der Griffe: Textfeld, Form und Diagramm werden in der neuen Größe frisch gezeichnet (Zeilenumbruch folgt der Breite,
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
- `_textfelder(ed)` — Alle Textfelder des Textes: (Schlüssel, Angabe) — frisch aus den Absätzen gelesen.
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
- `_effekte(p, bild, r, ellipse, fx)` — Leuchten, Schatten, Reflektion hinter das Bild zeichnen; Weiche Kanten, 3D-Format und 3D-Drehung am Bild selbst. → (Bild, noch Ellipse).
- `_flaeche_zeichnen(p, bild, r, ellipse, fuell, fuellbild)` — Füllung und Bild, bei ``ellipse`` in einer Ellipse beschnitten.
- `_rand_zeichnen(p, r, ellipse, rand)` — Die Linie um die Form, ganz innerhalb von ``r``.
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

- `_bauen()` — Die Linienarten der Auswahl „Formatvorlage“: Schlüssel → (Name, Strichart, DOCX-Wert, Bahnen, wellig).
- `docx_wert(art)` — Wert von ``w:val`` für eine Linienart (unbekannt: einfach).
- `art_aus_docx(wert)`
- **class `Linie`**
  - `text()`
  - `polster()` — (oben, unten, links, rechts) in pt, wenn ein eigener Abstand gesetzt ist.
  - `aus_text(text)`
  - `mit_seiten(seiten)`
  - `stift(massstab)` — QPen der Linie (bei Mehrfachlinien die Gesamtbreite); ``massstab`` rechnet pt in Bildpunkte um (96/72 am Bildschirm, mal Zoom).
  - `_bahn_stift(w, dicke, strich)`
  - `zeichne(p, x1, y1, x2, y2, massstab)` — Eine einzelne Linie in ihrer Art: einfach, gestrichelt, mehrfach (Bahnen nebeneinander) oder wellig.
  - `rahmen_zeichnen(p, r, massstab, innen_y)` — Zeichnet die gemeinten Seiten eines Rechtecks in der Linienart. ``innen_y``: Höhen der Linien zwischen Absätzen

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
- `_inline_daten(ed)` — Daten eines älteren, im Text sitzenden SmartArt-Bildes (aus vorhandenen Dokumenten).
- `daten_der_auswahl(ed)` — Daten des gewählten SmartArt: zuerst das freie Objekt, sonst ein älteres Bild im Text.
- `_text_gegen_knoten(ed, neu)` — Ein neuer ``text`` ohne neue Knoten: weicht er vom Text der vorhandenen Knoten ab, ersetzt er sie; sonst bleibt alles, wie es ist.
- `_inline_aendern(ed, neu)` — Ein älteres SmartArt, das als Bild im Text steht: Daten ändern, neu zeichnen, Breite behalten.
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

Unterpaket ``seite`` von ``lunivo_writer.editor``.


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

- `seite_zu_dict(ps)`
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
- `_gleiche_geometrie(a, b)`
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
- `blasen_pro_seite(d, page, liste, bd)` — {Blattseite (1-basiert): [(Blase, y in px auf der Textfläche)]} — die Blasen stammen aus der Kopie selbst.
- `blasen_zeichnen(p, eintraege, geo)`

### `editor/seite/deckblatt.py`

Deckblätter (Einfügen ▸ Deckblatt): 17 Gestaltungen in den Gruppen der Vorlage (Artikel, Firma, Lebenslauf, Abschlussarbeit), je im

- **class `Feld`** — Ein Platzhalter-Absatz: ``y`` = Oberkante als Anteil der Blatthöhe, ``x`` = linker Rand als Anteil der Blattbreite (bei links).
- **class `Gestaltung`**
- `_kontakt(y, farbe, x, ausrichtung, abstand)`
- `_arbeit(y, farbe)`
- `gestaltung(name)`
- `_verlauf(r, farben, senkrecht)`
- `_wolken(p, r, y, farbe, n)`
- `_segelboot(p, x, y, s)`
- `_puzzle(p, x, y, s, farbe)`
- `_blume(p, cx, cy, s)`
- `_g_mosaik(p, r, w, h, x0, y0, R)`
- `_g_himmel(p, r, w, h, x0, y0, R)`
- `_g_sonne(p, r, w, h, x0, y0, R)`
- `_g_kopfbalken(p, r, w, h, x0, y0, R)`
- `_g_wellen(p, r, w, h, x0, y0, R)`
- `_g_blaurand(p, r, w, h, x0, y0, R)`
- `_g_stadt(p, r, w, h, x0, y0, R)`
- `_g_notizzettel(p, r, w, h, x0, y0, R)`
- `_g_sonnenblume(p, r, w, h, x0, y0, R)`
- `_g_gruen(p, r, w, h, x0, y0, R)`
- `_g_puzzle(p, r, w, h, x0, y0, R)`
- `_g_segel(p, r, w, h, x0, y0, R)`
- `_g_rahmen(p, r, w, h, x0, y0, R)`
- `_g_linien(p, r, w, h, x0, y0, R)`
- `_g_siegel(p, r, w, h, x0, y0, R)`
- `_grafik(p, name, r)` — Die Grafik einer Gestaltung (ohne Text) auf das Blatt ``r``.
- `_schrift(f, blatt_hoehe_px, quer)` — Schrift eines Feldes im Maßstab des Blattes (Original: A4 hoch = 1123 Bildpunkte; quer etwas kleiner).
- `zeichnen(p, name, r, mit_text)` — Gestaltung ``name`` auf das Blatt ``r`` (weißer Grund, Grafik, auf Wunsch die Platzhalter): für die Galerie.
- `grafik_bild(name, breite_px, hoehe_px)`
- `hat_deckblatt(doc)`
- `entfernen(ed)` — Das Deckblatt (erster Abschnitt mit ``B_DECKBLATT``) herausnehmen; das Dokument bekommt die Einrichtung des zweiten Abschnitts.
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
- `_notenmarken(d, ch, liste)` — {(Art, Id): Lage der Marke auf ihrer Seite}; nur Seiten aus ``liste``.
- `_notenziele(d, ch, liste)` — {(Art, Id): Lage der Note}: Fußnoten am Seitenfuß, Endnoten und gesammelte Noten am Textende.
- `notenlinks_sammeln(d, page, liste)` — Sprungverweise für die PDF: Marke → Note und Note → Marke (Fußnoten am Seitenfuß, Endnoten und gesammelte Noten am Textende).

### `editor/seite/leere_seite.py`

Einfügen ▸ Leere Seite: ein neues, leeres Blatt HINTER der Seite der Schreibmarke. Der vorhandene Text wird nicht geteilt.

- `_umbruch_davor(block)`
- `leere_seite(doc, letzter, einrichtung, quer)`

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

- `_erste_kommentarstellen(d)` — {Kommentar-Id: erste Zeichenstelle} aus der Eigenschaft P_KOMMENTAR.
- `kommentarstellen(d, ch, liste, kommentare, spalten)` — [(Seitenindex, y in px auf der Textfläche, Text)] für die PDF-Notizen. `kommentare` = {Kommentar-Id: Text}; die Stelle
- `_blockseite(lay, b, ch, spalten)`
- `_stilname(b)`
- `_ist_stileintrag(b, was)` — Titel, Untertitel, Zitat („andere“) oder eigene Formatvorlage („eigene“) als Lesezeichen.
- `_textmarken_anhaengen(b, idx, out)`
- `_block_eintraege(b, idx, was, out)` — Hängt die Lesezeichen des Absatzes (Überschrift, Stil, Textmarken) an ``out``: (Ebene, Titel, Seitenindex, Stelle).
- `lesezeichen_sammeln(d, ch, liste, was, spalten)` — [(Ebene, Titel, Seitenindex 0-basiert)] für die PDF-Gliederung: Überschriften und/oder Textmarken.
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
- `paginated_copy(qdoc, page, noten, silben, einspaltig, versteckt, fussnoten, lese_luft)`
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
- `_pdf_ergebnisse(opt, d, page, liste, spalten)` — Stellen für Lesezeichen, Kommentar-Notizen und Sprungverweise der PDF (``export_pdf`` trägt sie danach ein).
- `render(qdoc, page, device, first, last, dpi, opt)` — Zeichnet die Seiten first..last auf device (QPdfWriter/QPrinter). → Anzahl Seiten.
- `_leerseite_davor(i, typ, gesamt)` — 1, wenn vor dem Abschnitt i eine Leerseite nötig ist („gerade/ungerade Seite“), sonst 0.
- `_leerseiten_plan(typen, zaehl)` — ([Seitenzahl vor dem Abschnitt einschließlich Leerseite], [Leerseite davor 0/1], Seiten insgesamt).
- `_erste_nummern(teile, zaehl, leer)` — Angezeigte Nummer vor dem ersten Blatt je Abschnitt: „Beginnen mit“ setzt neu an, sonst geht es nach dem vorigen Teil weiter.
- `_startteil(zaehl, offsets, leer, first, last)` — Erster Abschnitt, der wirklich gedruckt wird: sein Papier gilt schon beim Start.
- **class `_Folge`** — Stand beim Ausgeben mehrerer Abschnitte hintereinander.
- `_papier_wechseln(f, i, ps)` — Das Papier eines Abschnitts gilt erst ab seiner ersten gedruckten Seite (der erste Teil ist schon eingestellt).
- `_abschnitt_drucken(f, i, d, ps, o, z, nummer)` — Leerseite vor dem Abschnitt (falls nötig) und seine Seiten im gewünschten Bereich.
- `render_dokument(qdoc, page, device, first, last, dpi, opt, layout)` — Wie render(), aber mit mehreren Abschnitten: jeder Abschnitt wird mit seiner eigenen Seitengröße, seinen Rändern, Spalten und
- `_frei_index(d, page)` — Index der freien Bilder im Fluss (je Kopie einmal berechnet).
- `_kopf_fuss_zeichnen(p, page, n, nr_offset, total, gesamt, base, kapitel)`
- `_zeilennummern_zeichnen(p, d, page, n, base)`
- `_fussnoten_zeichnen(p, d, page, n)` — Fußnoten am Seitenfuß, mit kurzem Trennstrich.
- `_spalte_zeichnen(p, d, page, lp, x)` — Die logische Spaltenseite ``lp`` an Stelle ``x`` der Blattseite.
- `_aenderungsbalken(p, balken, page, n, lp, x_spalte)` — Änderungsbalken neben den Zeilen mit verfolgten Änderungen.
- `_spaltenlinien_zeichnen(p, page, n_sp)`
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
- `_hf_effekt(p, fmt, f, rect, text, flag)` — Zeilen mit Texteffekt (Schatten, Spiegelung, Leuchten, Kontur …) zeichnen: dieselben Bausteine wie im Dokument (``editor/text/textfx.py``).
- `_ohne_hintergruende(d)`
- `_text_schwarz(d)` — „Text schwarz drucken“ in der Kopie: jede Schriftfarbe wird schwarz (Verknüpfungen und Platzhalter eingeschlossen).
- `_formularteile_ausblenden(d, steuer, platzhalter)` — Steuerelemente (Felder mit Wert, Schaltflächen, Kästchen) und/oder Platzhaltertexte leerer Felder werden in der Kopie unsichtbar.
- `_ohne_hervorhebungen(d)` — Nur die Texthervorhebung (Marker) entfällt; Absatz- und Tabellenhintergründe bleiben.
- `_ohne_links(d)` — PDF ohne Hyperlinks: der Text bleibt, nur das Linkziel entfällt (Qt schreibt sonst für jedes Linkziel einen PDF-Link).
- `_textmarken_klammern(d)` — „Textmarken drucken“: jede Textmarke steht in eckigen Klammern im Ausdruck.
- `_bf_ohne(bf)`
- `seitenschmuck(p, page, hintergrund, flaeche, rahmen, wasserzeichen)` — Seitenfarbe, Seitenrahmen und Wasserzeichen. Koordinaten: Seite in 96-dpi-Bildpunkten, Ursprung links oben.
- `seiten_liste(total, first, last, opt)` — Welche Seiten in welcher Reihenfolge gedruckt werden (Duplex, umgekehrte Reihenfolge).
- `frei_zeichnen(p, objekte, hinter)` — Freie Bilder der Seite hinter oder vor dem Text (zum Beispiel ein Band im Briefkopf, Foto, Unterschrift).
- `_druckmarken(p, page, grenzen, zuschnitt)` — Textbegrenzungen (gestrichelter Rahmen um die Textfläche) und Zuschnittsmarken (Ecken) auf der gedruckten Seite.
- `_inhalt_zeichnen(p, d, rect)` — Wie ``QTextDocument.drawContents``, aber mit schwarzer Grundschrift: Text ohne eigene Farbe nähme sonst die Textfarbe des
- `absatz_zusatz_zeichnen(p, d, faktor)` — Was an den Absätzen nicht von Qt kommt: Rahmen und die Nummern mehrstufiger Listen.
- `_rahmengruppen(d)` — [[Rahmenangabe, [Absätze], Nummer des letzten Absatzes]]: zusammenhängende sichtbare Absätze mit gleichem B_RAHMEN.
- `_rahmenrechteck(r, linie, faktor, polster)` — Rechteck des Rahmens: Absatzfläche plus Abstand (eigener Abstand der Linie in pt, sonst ``polster``).
- `absatzrahmen_zeichnen(p, d, faktor, polster)` — Rahmen um zusammenhängende Absätze mit gleichem B_RAHMEN. Koordinaten: Dokument (Layoutgerät); faktor = Zoom.

### `editor/seite/seitenfluss.py`

Umbruchregeln am Seitenende: „Diesen Absatz zusammenhalten“, „Nicht vom nächsten Absatz trennen“ und die Absatzkontrolle

- `seitenraster(doc, ch)` — Die Höhe, in der Qt die Seiten dieses Dokuments umbricht: seine Seitenhöhe (sonst ``ch``), auf 1/64 Bildpunkt abgeschnitten.
- `_von_oben(zeile, ch)` — Abstand einer Zeile (aus ``_zeilen``) vom oberen Rand ihrer Seite.
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

- `abstaende_pt(b)` — (oben, unten, links, rechts) in pt.
- `rechteck(b, page, seite)` — Das Rechteck des Rahmens in Bildpunkten, auf einer Seite mit dem Rechteck ``seite``.
- `_figur(art, mitte, groesse)`
- `kunst_zeichnen(p, rect, art, breite_px, farbe)` — Einen Kunstrahmen entlang der Kanten: Figuren in regelmäßigem Abstand (Zickzack als Linienzug).
- `zeichnen(p, b, page, seite)` — Den Seitenrahmen auf eine Seite zeichnen (Linie in ihrer Art oder Kunstrahmen).

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
- `schwebend_einfuegen(doc, blockpos, f, seite)` — Fügt das Bild f vor dem Absatz bei blockpos als schwebendes Bild ein (seite: „links“ \| „rechts“).
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
- `zeichnen(p, w, r)` — Das Wasserzeichen ``w`` auf die Seite ``r`` (96-dpi-Bildpunkte) zeichnen.

### `editor/seite/zeilennummern.py`

Zeilennummern (Seitenlayout ▸ Zeilennummern): welche Zeile welche Nummer trägt. Keine Oberfläche — Editor, Druck und PDF zeichnen damit.

- `unterdrueckt(block)`
- `nummern(doc, ch, art)` — (Absatz, Zeile, y im Textfluss, Nummer) für jede nummerierte Zeile; ``ch``: Höhe des Textbereichs einer Seite im Fluss.
- `zeichnen(p, d, n, ch, base, art)` — Zeilennummern am linken Rand der Seite n (Koordinaten: Textfläche, auf die Seite verschoben).

## `editor/tabelle`

### `editor/tabelle/__init__.py`

Unterpaket ``tabelle`` von ``lunivo_writer.editor``.


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

Unterpaket ``text`` von ``lunivo_writer.editor``.


### `editor/text/auswahl.py`

Auswählen (Start ▸ Auswählen): Tabellen ohne sichtbaren Rahmen finden und Stellen mit gleicher Zeichenformatierung sammeln — ohne Oberfläche.

- `_tabellen(rahmen)`
- `ohne_rahmen(t)`
- `tabelle_ohne_rahmen(ed)` — Markiert die nächste Tabelle ohne Rahmen hinter der Schreibmarke (am Ende geht es vorn weiter). → False, wenn es keine gibt.
- `_merkmale(cf)`
- `aehnlich_formatiert(ed)` — Alle Strecken mit derselben Zeichenformatierung wie das Zeichen an der Schreibmarke (je Absatz zusammengefasst).

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

### `editor/text/suche.py`

Suchen und Ersetzen wie im Fenster der Vorlage: Sonderzeichen (^p, ^t, ^? …), Platzhalter, Präfix/Suffix, Satzzeichen und Leerzeichen

- **class `Suchauftrag`**
  - `hat_format()`
  - `leer()`
- `_zeichen_kennzeichen(cf)` — Kennzeichen für Grafik, Fuß- oder Endnotenzeichen und Feld; leer für gewöhnlichen Text.
- `_umbruch_kennzeichen(b)` — Kennzeichen für das Ende des Absatzes ``b``: Abschnitts-, Spalten- oder (vom Benutzer gesetzter) Seitenumbruch; sonst leer.
- `roh_text(doc)` — Der Text des Dokuments, eine Stelle je Position, mit Kennzeichen für Noten, Felder, Grafiken und Umbrüche.
- `_woertlich(text)` — Suchtext ohne Platzhalter → Liste von Regex-Stücken (ein Stück je Zeichen oder Sonderzeichen).
- `_klammer(text, i)` — ``{n,m}`` (Wiederholung) oder ``[abc]``/``[!x]`` (Zeichenklasse) ab Stelle ``i`` → (Regex-Stück, Stelle des letzten verbrauchten Zeichens).
- `_platzhalter(text)` — Platzhalter: ? ein Zeichen, * beliebig viele, [abc] [a-z] [!x] eines davon/keines, {n,m} Wiederholung, @ eins oder mehr,
- `_ignoriert(a)` — Die Zeichen, über die die Suche hinweggeht (Satzzeichen, Leerzeichen); mit Platzhaltern gilt das nicht.
- `muster(a)` — Der reguläre Ausdruck des Auftrags; ``None`` bei leerem Text (dann sucht nur die Formatierung) oder ungültigen Platzhaltern.
- `gueltig(a)`
- `_zeichen_passen(doc, von, bis, a)`
- `_nur_format(doc, a, von, bis)` — Ohne Suchtext: jede zusammenhängende Strecke mit der gesuchten Formatierung (je Absatz).
- `treffer(doc, a, von, bis, grenze)` — Alle Treffer im Bereich [von, bis) als (von, bis).
- `naechster(doc, a, ab, rueckwaerts, von, bis, umlauf)` — Der nächste Treffer hinter (oder vor) ``ab``; mit ``umlauf`` geht es am Ende vorn weiter (und umgekehrt).
- `ersatz_text(a, ersatz, gefunden, zwischenablage)` — Der Ersatztext mit seinen Sonderzeichen: ^p Absatz, ^t Tab, ^l Zeilenumbruch, ^m Seiten-, ^n Spaltenumbruch, ^& der gefundene Text,
- `ersetzen(doc, von, bis, neu, format_, absatz_format)` — Den Bereich durch ``neu`` ersetzen (Text mit Kennzeichen aus ``ersatz_text``). Die Formatierung des ersetzten Textes bleibt,
- `_umbruch_weg(doc, pos, art)`
- `alle_ersetzen(doc, a, ersatz, von, bis, format_, absatz_format, zwischenablage)` — Alle Treffer im Bereich ersetzen, als ein Schritt für Rückgängig. → Zahl der Ersetzungen.

### `editor/text/tabfuell.py`

Füllzeichen vor Tabstopps (Punkte, Striche, Linie): Qt kennt sie nicht, Lunivo zeichnet sie selbst.

- `lesen(bf)` — Position (px) → Füllzeichen-Schlüssel eines Absatzformats.
- `setzen(bf, fuell)`
- `aus_docx(wert)`
- `_tabstrecken(b, bf)` — (Zeile, x0, x1, Füllzeichen) jedes Tabzeichens des Absatzes, dessen Tabstopp ein Füllzeichen hat. x in Koordinaten der Zeile.
- `_strecke_fuellen(p, fm, zeichen, x0, x1, y)` — Die Strecke x0…x1 auf der Grundlinie ``y`` füllen: durchgehende Linie oder Zeichen mit festem Abstand, rechtsbündig ans Tabziel.
- `_absatz_zeichnen(p, b, bf)`
- `zeichnen(p, d)` — Füllzeichen in die Tabstrecken der Absätze zeichnen. Koordinaten: Dokument.

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

- `_bloecke(ed)` — Die Absätze der Markierung (ohne Markierung: alle) außerhalb von Tabellen, in Dokumentreihenfolge.
- `_leer(b)` — Ein Absatz ohne Zeichen und ohne Bild.
- `_schritt(ed, arbeit)` — Führt ``arbeit(doc, bloecke)`` als einen Rückgängig-Schritt aus. → Zahl der Änderungen.
- `leere_loeschen(ed)`
- `leere_einfuegen(ed)`
- `zeilenumbruch_in_return(ed)`
- `absaetze_neu_anordnen(ed)` — Absätze, die mitten im Satz enden (hartes Return in einem Satz, etwa aus PDF-Text), werden zu einem Absatz.
- `leerzeichen_bereinigen(ed)` — Doppelte Leerzeichen und Leerzeichen am Anfang und Ende der Absätze entfernen.
- `einzug_zwei_zeichen(ed)` — Erstzeileneinzug um zwei Zeichen der Schriftgröße des Absatzes.
- `smart_anordnen(ed)` — Leerzeichen bereinigen, leere Absätze löschen, Erstzeileneinzug um zwei Zeichen.
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
  - `tabelleZeichnen(k)` — Stift: Rechteck aufziehen, die Tabelle kommt dorthin (siehe ``oberflaeche/dokument/tabelle/tabelle_stift.py``).
  - `tabelleRadierer(k)` — Radiergummi: Klick auf eine Zellenlinie löscht sie (siehe ``oberflaeche/dokument/tabelle/tabelle_radierer.py``).
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
  - `_ergebnis_blatt(titel, ziel, page)`
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
  - `anordnen(k)` — Textumbruch / Position: Bild mit Text in der Zeile oder links/rechts vom Text umflossen.
  - `bildOriginal(k)`
  - `bildAltText(k)`
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
  - `tabelleZellenLoeschen(k)` — Löschen ▸ Zellen löschen …: Auswahl, wie die Lücke geschlossen wird (Logik: ``editor/tabelle/tabelleneigenschaften.zellen_loeschen``).
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
  - `_tabelle_rahmen_schattierung_anwenden(t, c, linie, fuell)` — Rahmen der Tabelle (Linie oder None = ohne) und Füllfarbe der markierten Zellen bzw. der Zelle der Schreibmarke.
  - `tabelleBeschriftung(k, oben)` — „Beschriftung …“ für die Tabelle der Schreibmarke: dasselbe Fenster wie Verweise ▸ Beschriftung (``BeschriftungDialog``),
  - `menue_tabelleSchattierung()`
  - `menue_tabelleVorlagen()`
  - `_tabelle_vorlage(name)` — Vorlage auf die Tabelle der Schreibmarke anwenden; Kopfzeile/Streifen/Erste Spalte stehen je Tabelle (editor/tabelle/tabelleneigenschaften.py).
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
  - `_tabelle_fenster()`
  - `_tabelle_inhalt()`
  - `_tabelle_aendern(funktion)`
  - `_tabelle_gleich()`
  - `_tabelle_zeilen_gleich()`
  - `_tabelle_fest()`
  - `tabelleBreite(k)` — Breite der Spalte der Schreibmarke in cm festlegen (Eingabe; gesetzt über ``tabelleMasse``).
  - `tabelleMasse(breite_mm, hoehe_mm)` — Band-Zahlenfelder der Tabellentools: Spaltenbreite der Schreibmarke und/oder Mindesthöhe ihrer Zeile in mm setzen (ein Rückgängig-Schritt).
  - `tabelleMasseLesen()` — (Breite der Spalte, Höhe der Zeile) der Schreibmarke in mm für die Zahlenfelder des Bandes; ``None`` außerhalb einer Tabelle.
  - `an_tabelleGitternetz()`
  - `tabelleGitternetz(k)` — Gitternetzlinien umschalten: hellgraue gestrichelte Zellränder; wirkt nur bei Tabellen ohne Rahmen.
  - `menue_tabelleTextrichtung()`
  - `tabelleTextrichtung(k)` — Auswahl der Textrichtung der Zelle (waagrecht / rechts nach links); Qt zeichnet nur diese beiden.
  - `_tabelle_richtung(richtung)` — Textrichtung der Zelle der Schreibmarke bzw. aller markierten Zellen setzen (Blockformat setLayoutDirection).

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
- `_bild_ohne_alt(cf)`
- `_fragment_pruefen(f, seite, z)` — Ein Textstück: Bild ohne Beschreibung, zu blasse Schrift, nichtssagender Verweis (Zähler in ``z``).
- `_text_durchsuchen(doc, seite)` — Durchläuft alle Blöcke: (Zähler, Überschriftenebenen, Wortzahl).
- `_ueberschriften_funde(ebenen, woerter)`
- `_link_fund(n)`
- `pruefe(editor)`
- `_tabellen(doc)`

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

- `mm_to_px(mm)`
- `px_to_mm(px)`
- `umbruchraster(px)` — Eine Seitenhöhe so, wie Qt mit ihr umbricht: auf 1/64 Bildpunkt abgeschnitten. Jede Rechnung „y → Seite“ muss diese Höhe nehmen;
- **class `HeaderFooter`** — Text mit Platzhalter {PAGE} und {PAGES}. Ausrichtung: left\|center\|right, dazu aussen\|innen (ungerade Seiten rechts bzw. links,
  - `kopie(text, align)`
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
- **class `_FelderDict`**(dict) — Felder des Bandes: Reiter werden erst nach dem Anzeigen fertig gebaut; wer ein noch fehlendes Feld braucht, bekommt zuerst alle Reiter.
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

Unterpaket ``auswahl`` von ``lunivo_writer.oberflaeche.baukasten.dropdown``.


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

Unterpaket ``objektmenues`` von ``lunivo_writer.oberflaeche.baukasten.dropdown``.


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

- `objekte(ed)` — [(Beschriftung, von, bis)] aller Objekte in Dokumentreihenfolge.
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
  - `__init__(parent)`
  - `_start(*_)`
  - `setze(titel, text)` — Ohne Meldung; ein Feld mit dem Fokus (Eingabe läuft) bleibt unberührt.

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

Unterpaket ``einfuegen`` von ``lunivo_writer.oberflaeche.dialoge``.


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

Unterpaket ``ki`` von ``lunivo_writer.oberflaeche.dialoge``.


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

Unterpaket ``lesen_hilfe`` von ``lunivo_writer.oberflaeche.dialoge``.


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

- **class `AnsichtSeiten`** — Optionen: Ansicht und Darstellung. Baustein von ``OptionenAnsicht`` (siehe ``lunivo_writer/oberflaeche/dialoge/optionen.py``).
  - `_ansicht(titel)`
  - `_aussehen(p)` — Hell, Dunkel, Mint oder wie das System: vier große Schaltflächen, genau eine ist gewählt (kein ausgegrauter Zusatzschalter).
  - `_oberflaeche_wahl(p, f)`
  - `_darstellung(p, f)` — Schrift größer/kleiner, Weicher Kontrast, Größe der Symbole, Schrift der Bedienung.

### `oberflaeche/dialoge/optionen_seiten/befehle.py`

Optionen: Menüband, Schnellzugriff, Sicherheit.

- **class `BefehleSeiten`** — Optionen: Menüband, Schnellzugriff, Sicherheit. Baustein von ``OptionenAnsicht`` (siehe ``lunivo_writer/oberflaeche/dialoge/optionen.py``).
  - `_zwei_listen(p, links_kopf, rechts_kopf, hinzu, weg, kategorie)` — Gerüst der Vorlage: links „Befehle auswählen“ (Auswahl, Suche, Liste), in der Mitte Hinzufügen/Entfernen, rechts die Liste
  - `_schieben(liste, d)`
  - `_menueband(titel)`
  - `_schnellzugriff(titel)`
  - `_sicherheit(titel)`
  - `_verfolgen(titel)`

### `oberflaeche/dialoge/optionen_seiten/datei.py`

Optionen: Schreiben, Speichern, Drucken und PDF.

- **class `DateiSeiten`** — Optionen: Schreiben, Speichern, Drucken und PDF. Baustein von ``OptionenAnsicht`` (siehe ``lunivo_writer/oberflaeche/dialoge/optionen.py``).
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

- **class `LesenSeiten`** — Optionen: Leichter lesen, Sprache. Baustein von ``OptionenAnsicht`` (siehe ``lunivo_writer/oberflaeche/dialoge/optionen.py``).
  - `_lesehilfe(titel)`
  - `_silbentrennung_haken(p, f)` — Haken „Silbentrennung“: gilt für das Dokument, das gerade offen ist (derselbe Schalter wie im Reiter Schreibhilfe).
  - `_lese_schriften(p, e)` — Die drei Schriften zum leichteren Lesen mit Probe; sagt, ob sie da sind.
  - `_uebersetzung_oeffnen()`

### `oberflaeche/dialoge/optionen_seiten/lunivo.py`

Optionen: KI, Gedächtnis, Erweitert.

- **class `LunivoSeiten`** — Optionen: KI, Gedächtnis, Erweitert. Baustein von ``OptionenAnsicht`` (siehe ``lunivo_writer/oberflaeche/dialoge/optionen.py``).
  - `_ki(titel)`
  - `_gedaechtnis(titel)`
  - `_erweitert(titel)`

### `oberflaeche/dialoge/optionen_seiten/name_ki.py`

Optionen: Name und KI, dazu die Werkzeug-Fenster (Menüband, Schnellzugriff, Kennwort, Änderungen verfolgen).

- **class `NameKiSeiten`** — Optionen: Name und KI. Baustein von ``OptionenAnsicht`` (siehe ``lunivo_writer/oberflaeche/dialoge/optionen.py``).
  - `_name_ki(titel)`
  - `_anpassen(key)` — Eines der Werkzeuge als Fenster zeigen; das Band wird danach neu gebaut, wenn es sich geändert hat.

## `oberflaeche/dialoge/sendungen`

### `oberflaeche/dialoge/sendungen/__init__.py`

Unterpaket ``sendungen`` von ``lunivo_writer.oberflaeche.dialoge``.


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

Unterpaket ``verweise`` von ``lunivo_writer.oberflaeche.dialoge``.


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

Unterpaket ``ansicht`` von ``lunivo_writer.oberflaeche.dokument``.


### `oberflaeche/dokument/ansicht/absatz_symbol.py`

Absatz-Layout-Symbol: ein kleiner Knopf links neben dem Absatz der Schreibmarke (Absatzzeichen mit Pfeil). Sein Menü bietet

- **class `AbsatzSymbol`**(QObject)
  - `__init__(ed)`
  - `sichtbar_soll()`
  - `aktualisieren()`
  - `_zuruecksetzen()`
  - `_ausblenden()`

### `oberflaeche/dokument/ansicht/blasen_flaeche.py`

Die Fläche neben der Seite, auf der die Sprechblasen des Editors stehen (Kommentare, verfolgte Änderungen).

- **class `BlasenFlaeche`**(QWidget)
  - `__init__(editor)`
  - `grundfarbe()` — Der Grund der Fläche ist derselbe wie rund um das Blatt (der Hintergrund des Dokumentfensters) — der Streifen ist also nicht zu sehen, nur die Blasen darauf.
  - `paintEvent(e)`
  - `_blase_bei(pos)`
  - `mousePressEvent(e)`
  - `_menue(bl, pos)`
  - `mouseDoubleClickEvent(e)`

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

### `oberflaeche/dokument/ansicht/seiten_ansicht.py`

Zwei-Seiten-Ansicht: die Seiten des Dokuments nebeneinander, so wie sie gedruckt werden (nur zum Ansehen).

- **class `SeitenAnsicht`**(QWidget)
  - `__init__(editor, breite)`

### `oberflaeche/dokument/ansicht/vorschau_ansicht.py`

Vorschau im Dokumentfenster: statt des Dokuments steht ein schreibgeschützter Editor mit einer abgeleiteten Fassung da — der

- `aktiv(tab, art)`
- `zeigen(tab, doc, art)`
- `beenden(tab)`

## `oberflaeche/dokument/bearbeitung`

### `oberflaeche/dokument/bearbeitung/__init__.py`

Unterpaket ``bearbeitung`` von ``lunivo_writer.oberflaeche.dokument``.


### `oberflaeche/dokument/bearbeitung/basis.py`

- `_ziel_fragment(html, standard)` — HTML einfügen, aber Schriftart, -größe, Farben und Hintergründe des Ziels behalten.

### `oberflaeche/dokument/bearbeitung/dokument_editor.py`

Der Editor: QTextEdit mit Seitenbreite, Formatierungsbefehlen und Seitenzählung.

- **class `DocumentEditor`**(AnzeigeBaustein, SpaltenBaustein, SeitenBaustein, FormatierungBaustein, BilderBaustein, SchreibhilfeBaustein, FreieBilderMixin, ZusatzMixin, EinfuegenMixin, QTextEdit)
  - `setReadOnly(ro)`
  - `__init__(parent)`
  - `_verbinde_groesse()`
  - `_passe_hoehe_an(*_)`
  - `_blatt_anzahl()` — Anzahl der Blätter: so viele, wie der Textfluss des Editors Seiten braucht (plus Noten-Seiten, die nur der Druck anhängt).
  - `_aussen()`
  - `_scroll_outer()`
  - `set_document_and_page(doc, page)`
  - `apply_page(page)`
  - `focusInEvent(e)`
  - `mousePressEvent(e)`
  - `dragMoveEvent(e)`
  - `dropEvent(e)`
  - `mouseMoveEvent(e)`
  - `mouseDoubleClickEvent(e)`
  - `_doppelklick_kopffuss(zone)` — Doppelklick in die Kopf-/Fußzone öffnet sie; Doppelklick in den Text beendet das Bearbeiten der Kopfzeile.
  - `_doppelklick_objekt(e)` — Doppelklick auf einen SmartArt-Knoten oder ein WordArt/Textfeld: direkt im Objekt schreiben.
  - `resizeEvent(e)`
  - `wheelEvent(e)`
  - `contextMenuEvent(e)`
  - `_kontext_objekt_eintraege(m)` — Layout und Textumbruch für ein gewähltes Objekt oder Bild.
  - `_kontext_text_eintraege(m)` — Ausgeblendeter Text und KI-Aktionen für markierten Text (nicht in Tabellen: das Tabellenmenü bleibt wie in der Vorlage).
  - `mouseReleaseEvent(e)`
  - `_mini_nach_auswahl(e)`
  - `_strg_klick_link(e)` — Strg+Klick auf einen Verweis springt dorthin bzw. öffnet die Adresse. → behandelt?
  - `_klick_auf_marke(e)` — Klick auf ein Formularfeld, einen Kasten oder eine Notiz-Marke. → behandelt?
  - `_bild_vor_klick_waehlen(e)`
  - `paintEvent(e)`
  - `_dekoration_zeichnen(p, vp, sp)` — Alles, was über dem Text liegt: Schmuck, Gitter, Absatzzusatz, Zeilennummern, Eckmarken, Spaltenlinien, Zeilenfokus.
  - `_deko_flaechen(p, sp)` — Schmuck, Gitter, Absatzzusatz und Zeilennummern.
  - `_deko_marken(p, vp, sp)` — Eckmarken, Zusätze, Spaltenlinien und Zeilenfokus.
  - `_hat_absatzzusatz()` — Rahmen, Mehrstufiges oder Tabfüllung an irgendeinem Absatz (je Dokumentrevision nur einmal gesucht, nicht bei jedem Zeichnen) oder ein Texteffekt.
  - `_absatzzusatz_zeichnen(p, sp)` — Rahmen, Mehrstufiges, Tabfüllung und Effekte der Absätze (je Blatt oder fortlaufend).
  - `_eckmarken_zeichnen(p, line_color)` — Eckmarken liegen außerhalb der Textfläche und zeigen von ihrer Ecke nach außen.
  - `_spaltenlinien_zeichnen(p, line_color)`
  - `_zeilenfokus_zeichnen(p, vp)` — Alles außer der Zeile mit der Schreibmarke wird abgedunkelt.
  - `keyPressEvent(e)`
  - `_teilen_vorher(e)` — Enter teilt einen Absatz: Absatznummer, wenn der Absatz einen Seiten-/Spaltenumbruch davor oder ein Abschnittsende trägt.
  - `_teilen_danach(nr)` — Qt kopiert das Absatzformat in den neuen Absatz. Der Umbruch davor gilt nur für den ersten Teil (sonst macht jedes Enter ein
  - `focusOutEvent(e)`

### `oberflaeche/dokument/bearbeitung/editor_absatzformat.py`

Absatzformat: fachlich abgegrenzte Editor-Funktionen.

- **class `AbsatzformatMixin`** — Teilbereich der Formatierungs- und Bearbeitungsfunktionen.
  - `_block_merge(fn)`
  - `set_alignment(al)`
  - `change_indent(delta_mm)`
  - `set_page_break_before(an)`
  - `set_indents(left_mm, right_mm, first_mm)`
  - `standard_tab_mm()` — Standardtabstopps des Dokuments (Abstand in mm).
  - `set_standard_tab_mm(mm)`
  - `set_absatzopt(w)` — Absatzoptionen (Umbruchregeln, Zeilenumbruch, Zeichenabstand, Raster) der markierten Absätze setzen.
  - `set_tabstopps(stopps)` — Tabstopps als Liste aus (Millimeter, Ausrichtung, Füllzeichen) setzen.
  - `set_line_spacing(factor)`
  - `set_line_height(art, wert)` — Zeilenabstand: ``faktor`` (Vielfaches), ``mindestens`` oder ``genau`` (Punkt).
  - `set_paragraph_spacing(before_pt, after_pt)`
  - `toggle_list(kind, style)`
  - `list_remove(nur_qt)` — Aufzählung/Nummerierung vom Absatz an der Schreibmarke (bzw. der Auswahl) nehmen.
  - `list_level(delta)`
  - `set_mehrstufig(defn, ebene_nr)` — Die markierten Absätze in eine mehrstufige Liste setzen (``defn=None``: herausnehmen). Der Text rückt ein, die Nummer steht davor.
  - `set_liste(spec)` — Liste setzen: ändert die Liste des Absatzes (alle ihre Absätze) oder legt für die Auswahl eine neue an; None nimmt sie weg.
  - `_nummern_zeichen(lst, zeichen)` — Schrift der Nummern: Qt zeichnet sie mit dem Zeichenformat des Absatzes.

### `oberflaeche/dokument/bearbeitung/editor_anzeige.py`

Anzeige: Sprechblasen, ausgeblendeter Text, Lesehilfe.

- **class `AnzeigeBaustein`** — Anzeige: Sprechblasen, ausgeblendeter Text, Lesehilfe. Baustein von ``DocumentEditor`` (siehe ``lunivo_writer/oberflaeche/dokument/bearbeitung/dokument_editor.py``).
  - `blasen_konfig()`
  - `blasen_rand()`
  - `blasen_linien()`
  - `_blasen_da()`
  - `_blasen_einrichten()` — Seitenrand für die Blasen: Fläche neben der Seite (setViewportMargins), nur wenn es Blasen gibt.
  - `_blasen_geometrie()`
  - `blasen_layout(breite)` — [(Blase, Rechteck in der Blasenfläche, y der Textzeile)] — gestapelt, ohne sich zu überlappen.
  - `kommentar_bearbeiten(kid)` — Doppelklick auf eine Blase: den Kommentar in der Karte links bearbeiten.
  - `set_versteckt_zeigen(an)`
  - `ist_versteckt()`
  - `_fragmente_in(von, bis)`
  - `set_versteckt(an)` — Markierung (oder Wort am Zeiger) als ausgeblendeten Text formatieren / zurücknehmen.
  - `set_zeilenfokus(an)`
  - `set_marken(an)`
  - `set_lesehilfe(papier, buchstaben, wort)`
  - `set_zeilenluft(faktor)` — Lesehilfe „Zeilenluft“: nur in dieser Anzeige; gespeichert und gedruckt wird ohne (editor/seite/lese_zeilenluft.py).
  - `set_lesefokus(wachstum, blasse)` — wachstum: 1,0 / 1,05 / 1,10 für den Absatz, in dem die Schreibmarke steht; blasse: 1,0 / 0,62 / 0,38 für den übrigen Text.
  - `_lese_aktiv()`
  - `_lese_neu(*_, erzwingen)`
  - `_lese_blasse_auswahl()` — Zusatzauswahl, die den Text außerhalb des aktuellen Absatzes in die Farbe des Papiers mischt (nur der sichtbare Bereich).
  - `_lese_wachstum_zeichnen()` — Der Absatz an der Schreibmarke wird ein wenig größer gezeichnet (aus der Mitte, ohne den Umbruch zu ändern): sein
  - `_aenderungszeilen_gecacht()`
  - `_kapitel_je_blatt(pg)` — Kapitelnummer je Blatt für die Seitenzahl („2-1“), nur wenn die Einrichtung sie verlangt; gemerkt je Textstand.
  - `_extras_zeichnen(p, sp)` — Objektanker, Änderungsbalken, Kopf- und Fußzeile im Rand der Seite.
  - `_objektanker_zeichnen(p, accent_color)` — Objektanker neben Bildern, die vom Text umflossen werden (bei sichtbaren Formatierungszeichen).
  - `_abschnittsumbrueche_zeichnen(p, accent_color)` — Abschnittsumbrüche: gestrichelte Linie mit Beschriftung unter dem letzten Absatz des Abschnitts.
  - `_aenderungsbalken_zeichnen(p, is_dark)` — Balken neben geänderten Zeilen.
  - `_blasenlinien_zeichnen(p)` — Linien von den Sprechblasen zum Text: Textende bis zum Seitenrand (der Rest steht in der Blasenfläche).
  - `_kopf_fuss_zeichnen(p, line_color)` — Kopf- und Fußzeile auf jedem Blatt (Lage wie im Druck: 8 mm unter dem oberen, 18 mm über dem unteren Blattrand).

### `oberflaeche/dokument/bearbeitung/editor_bilder.py`

Bilder im Text.

- **class `BilderBaustein`** — Bilder im Text. Baustein von ``DocumentEditor`` (siehe ``lunivo_writer/oberflaeche/dokument/bearbeitung/dokument_editor.py``).
  - `_bild_cursor()`
  - `bild_format()`
  - `bild_setzen(width, height, alt)`
  - `_wortweise()` — Wortweise markieren: eine mit der Maus gezogene Auswahl wird an Wortgrenzen erweitert.
  - `_cursor_at(pos)`

### `oberflaeche/dokument/bearbeitung/editor_einfuegen.py`

Einfügen aus Zwischenablage und nachträgliche Einfügeoptionen.

- `_ziel_fragment(html, standard)` — HTML einfügen, aber Schriftart, -größe, Farben und Hintergründe des Ziels behalten (Fett, Kursiv, Verweise bleiben).
- **class `EinfuegenMixin`** — Kapselt Einfügen, Formatvarianten und die kleine Einfüge-Schaltfläche.
  - `insertFromMimeData(source)`
  - `_einfuegen_mit(source, modus, neu)` — Einfügen als EIN Rückgängig-Schritt; danach bietet die kleine Schaltfläche die anderen Formen an (Optionen ▸ Bearbeiten).
  - `_einfuegen_schaltflaeche(quelle, start, ende, modus)`
  - `_einfuegen_neu(quelle, start, modus)`
  - `_paste_btn_pruefen()`

### `oberflaeche/dokument/bearbeitung/editor_formatierung.py`

Formatierungsfunktionen des Dokumenteditors, zusammengesetzt aus Fach-Mixins.

- **class `FormatierungBaustein`**(ZeichenformatMixin, AbsatzformatMixin, StilformatMixin, EditorWerkzeugeMixin) — Kompatible Fassade für die bisherigen Formatierungsfunktionen.

### `oberflaeche/dokument/bearbeitung/editor_gemeinsam.py`

Gemeinsame Werte der Bausteine.


### `oberflaeche/dokument/bearbeitung/editor_schreibhilfe.py`

Schreibhilfe im Text.

- **class `SchreibhilfeBaustein`** — Schreibhilfe im Text. Baustein von ``DocumentEditor`` (siehe ``lunivo_writer/oberflaeche/dokument/bearbeitung/dokument_editor.py``).
  - `cut()`
  - `set_wellen(funde)`
  - `replace_range(von, bis, neu, erwartet, markdown)` — Text ersetzen. ``markdown``: ``neu`` ist Markdown — die Struktur geht mit den Werkzeugen des Editors ins Dokument (``editor.text.ki_markdown``).
  - `select_range(von, bis)`
  - `_wort_vor_cursor()`
  - `_vorschlaege_zeigen()`
  - `_vorschlag_nehmen(wort)`
  - `_autokorr_anwenden()`
  - `_folge_vorher(e)` — Return am Ende eines Absatzes, dessen Vorlage einen „folgenden Absatz“ kennt → (Name der Folgevorlage, Absatznummer).
  - `_folge_danach(folge, nr)`
  - `_taste(e)`
  - `_gliederung_taste(e)` — Alt+Umschalt+Links/Rechts ändert die Gliederungsebene.
  - `_rechts_enter(c0, e)` — Eingabetaste in einem rechtsbündigen Absatz, wenn die Option „Leerzeichen am Ende entfernen“ gilt.
  - `_tab_luecke(e)` — Tab springt zur nächsten Lücke «…» der Vorlage.
  - `_popup_taste(e)` — Tasten bei offener Vorschlagsliste; True, wenn die Taste verbraucht wurde.
  - `_einzug_taste(c0, k, e)` — Tab/Rücktaste setzen den Einzug (nur am Absatzanfang).
  - `_auswahl_ans_ende(c0, e)` — Tippen ersetzt die Auswahl nur, wenn die Option an ist (Standard: aus, Markieren löscht nichts) — sonst wird hinter die Auswahl
  - `_nach_taste(e)` — AutoKorrektur und Vorschläge nach dem Einfügen des Zeichens.
  - `_rechts_leerzeichen_weg(c)` — AutoKorrektur: Leerzeichen am Ende einer rechtsbündigen Zeile würden den Text nach links schieben — sie werden entfernt.
  - `_kreiszahl()` — AutoKorrektur: „(1)“ … „(20)“ werden zu ① … ⑳ (Optionen ▸ Bearbeiten ▸ AutoKorrektur).
  - `_autoformat_liste()` — „1. “ / „1) “ am Absatzanfang → Nummerierung, „* “ / „- “ / „• “ → Aufzählung.
  - `_autokorr_extras()` — Netzadressen → Hyperlinks; Leerzeichen am Absatzanfang → Erstzeileneinzug.

### `oberflaeche/dokument/bearbeitung/editor_seiten.py`

Abschnitte, Seitenzählung, Paginierung.

- **class `SeitenBaustein`** — Abschnitte, Seitenzählung, Paginierung. Baustein von ``DocumentEditor`` (siehe ``lunivo_writer/oberflaeche/dokument/bearbeitung/dokument_editor.py``).
  - `seite_letzter_block()` — Der letzte Absatz, der auf dem Blatt der Schreibmarke beginnt (für „Leere Seite“: das neue Blatt kommt dahinter).
  - `abschnitt_nr()`
  - `abschnitt_seite(nr)` — Kopie der Einrichtung des Abschnitts `nr` (Vorgabe: des aktuellen).
  - `kopffuss()` — Der Bearbeiter für Kopf- und Fußzeile direkt auf der Seite (siehe ``kopffuss_bearbeiter``).
  - `abschnitt_einfuegen(typ)`
  - `abschnitt_entfernen()`
  - `abschnitt_gehe(nr)`
  - `_recount()` — Seitenzahl und Seitenwechsel neu bestimmen. Die Blätter selbst entstehen aus dem Textfluss des Editors; die
  - `_seitenwechsel(d)` — Zeichenstellen, an denen eine neue Seite beginnt (erste Zeile der Seiten 2, 3, …).
  - `seitenwechsel()`
  - `page_count()`
  - `current_page()` — Blatt, auf dem die Schreibmarke steht (so, wie es im Editor angezeigt wird).
  - `_cursor_moved()`
  - `set_silbenfarben(konfig)` — Silben farbig (reine Anzeige, ändert das Dokument nicht); konfig None oder an=False schaltet ab.
  - `word_count()`

### `oberflaeche/dokument/bearbeitung/editor_spalten.py`

Spalten im Editor.

- **class `SpaltenBaustein`** — Spalten im Editor. Baustein von ``DocumentEditor`` (siehe ``lunivo_writer/oberflaeche/dokument/bearbeitung/dokument_editor.py``).
  - `_blatt_aktiv()` — Blattmodus (Drucklayout): echte Blätter mit Rand und Zwischenraum; nur das Weblayout ist ein Endlosfluss.
  - `_mehrspaltig()`
  - `_sp_geo()` — Maße des Textflusses und (bei gleich großen Blättern) jedes Blattes. Bei verschieden großen Blättern (``_qplan``) sind
  - `blatt_oben(nr)` — y des oberen Randes von Blatt `nr` (0-basiert) im Editor — die Lineale richten sich danach.
  - `_blatt(k)` — Maße von Blatt `k` im Editor (mit Zoom): x (linker Blattrand), W, H, ml, mt, mb, cw (Textbreite), ch (Texthöhe), pg.
  - `_q_oben()` — Obere Blattränder bei verschieden großen Blättern (zwischengespeichert je Plan und Zoom).
  - `_quer_auffrischen()` — Plan der Blattgrößen neu bestimmen (nur einspaltig, nicht im Weblayout). → True, wenn sich Breite oder Fluss geändert haben.
  - `_blatt_bei_y(vy)`
  - `_sp_ursprung(lp)` — Ecke links oben der Textspalte, in der die logische Seite `lp` des Textflusses steht (Editorkoordinaten).
  - `_sp_einrichten()` — Dokument in Spaltenbreite und -höhe legen: feste Zeilenbreite, damit QTextEdit die Seitenhöhe nicht wieder auf „endlos“ setzt.
  - `_sp_view(dx, dy)` — Dokumentkoordinate (fortlaufender Fluss der Spaltenseiten) → Punkt auf dem Blatt.
  - `_sp_doc(vx, vy)` — Punkt auf dem Blatt → Dokumentkoordinate; Punkte in Rändern und Lücken landen in der nächsten Spalte.
  - `_sp_neu_zeichnen(*_)`
  - `_sp_blinken()`
  - `cursorRect(*args)`
  - `cursorForPosition(pos)`
  - `anchorAt(pos)`
  - `_maus_abgebildet(e)` — Mausereignis mit Dokumentkoordinaten (nur bei Spalten); QTextEdit selbst rechnet in Dokumentkoordinaten.
  - `_ziehen_abgebildet(e)` — Ziehen/Ablegen: QTextEdit rechnet in Dokumentkoordinaten, der Editor zeigt aber Blätter → Position abbilden.
  - `_kopffuss_zone(y)` — „kopf“ im oberen, „fuss“ im unteren Rand der Seite (nur Seitenansicht, nicht im Weblayout).
  - `_blatt_bereich(y0, y1)` — Blätter, die den senkrechten Bereich y0…y1 (Editorkoordinaten) berühren können, mit je einem Blatt Rand — damit das Zeichnen
  - `_arbeitsflaeche()` — Grauer Arbeitsbereich zwischen und um die Blätter (gleich dem Grund hinter dem Editor).
  - `_blaetter_zeichnen(p, g, sicht, papier, quer)` — Blätter mit Schatten und Papier; die Grafik eines Deckblatts liegt hinter dem Text.
  - `_rahmen_hinter_text(p, g, sicht, quer)` — Seitenrahmen hinter dem Text.
  - `_text_kontext()` — Zeichenkontext des Textes: Farben, Auswahl (auch Zusatzauswahlen), Schreibmarke.
  - `_text_seiten_zeichnen(p, g, sicht, quer, ctx)` — Jede Seite des Textflusses in ihre Spalte auf ihrem Blatt.
  - `_blatt_zeichnen(e)` — Arbeitsfläche, Blätter mit Schatten, dann Text, Auswahl, Schreibmarke und Wellenlinien: jede Seite des Textflusses
  - `set_web(an)`
  - `set_web_breite(px)`
  - `set_gliederung(an)` — Gliederungsansicht: nur Überschriften sind sichtbar; der Text dazwischen ist ausgeblendet (nicht gelöscht).
  - `gliederung_ebene(delta)` — Überschrift hoch-/herabstufen (Gliederung): Ebene 1..6, darüber/darunter wird sie zu Text/Titel.
  - `set_zeilennummern(an)`
  - `_zeilennummern_zeichnen(p)`
  - `apply_design(fliess, kopf, farbe)` — Design: Schriftart für Text und Überschriften, Farbe der Überschriften — für das ganze Dokument.
  - `set_absatzrahmen(wert)`
  - `absatzrahmen()` — Der Rahmen des Absatzes an der Schreibmarke (bei Auswahl: des ersten Absatzes) als ``Linie``, sonst None.
  - `set_absatzschatten(fuell, muster)` — Füllung (und Muster darüber) der markierten Absätze; ``None`` und kein Muster nehmen sie weg.
  - `absatzschatten()` — (Füllfarbe oder None, (Musterschlüssel, Musterfarbe) oder None) des Absatzes an der Schreibmarke.
  - `toggle_rtl()`
  - `_fluss_planen()`
  - `_seitenfluss()` — Umbruchregeln (Zusammenhalten, nicht vom nächsten Absatz trennen, Absatzkontrolle) auf die Seiten anwenden.
  - `_effekt_in(von, bis)`
  - `_effekt_geaendert(pos, entfernt, neu)` — Änderung im Text: war bisher kein Effekt da, genügt es, die geänderte Stelle zu prüfen (statt das ganze Dokument bei jedem Tastendruck).
  - `_hat_effekt()` — Gibt es Textstücke mit Effekten, die Lunivo selbst zeichnet (Verlauf, Schatten, Spiegelung, Leuchten, 3D)? Das Ergebnis gilt bis zur nächsten Änderung.
  - `_hat_blockzusatz()` — Rahmen, Mehrstufiges oder Tabfüllung an irgendeinem Absatz — ein Durchgang statt dreier (``_hat_rahmen``/``_hat_mehrstufig``/``_hat_tabfuell``).
  - `_hat_tabfuell()`
  - `_hat_mehrstufig()`
  - `_hat_rahmen()`
  - `set_gitter(an)`
  - `seitenspannen()` — Senkrechte Bereiche (von, bis) jedes Blattes im Editor.
  - `_wasserzeichen_je_blatt()` — Wasserzeichen je Blatt, wenn ein Abschnitt ein eigenes hat („Übernehmen für: Aktueller Abschnitt“); sonst None.
  - `_deckblatt_grafik(p, k, blatt)` — Ganzseitiges Bild (Deckblatt, ``editor/seite/deckblatt.py``) des Blattes ``k`` auf die Blattfläche, vor dem Text.
  - `_schmuck_zeichnen(p)`
  - `_gitter_zeichnen(p)`
  - `seitenfarbe_anwenden()`
  - `set_zoom(faktor)` — Ansicht vergrößern/verkleinern. Das Dokument selbst (Schriftgrößen, Maße) bleibt unverändert.
  - `page_settings_changed(page)` — Seiteneinrichtung ändern — für den Abschnitt, in dem die Schreibmarke steht (der erste Abschnitt ist das Dokument).

### `oberflaeche/dokument/bearbeitung/editor_stilformat.py`

Stilformat: fachlich abgegrenzte Editor-Funktionen.

- **class `StilformatMixin`** — Teilbereich der Formatierungs- und Bearbeitungsfunktionen.
  - `apply_style(name)`
  - `_bf_grundlagen(bf, d)` — Überschriftsebene, Vorlagenschlüssel, Abstände, Zeilenhöhe.
  - `_bf_einzuege(bf, d)` — Einzüge, Schreibrichtung, Umbruch, Gliederung, Absatzoptionen, Ausrichtung.
  - `_bf_rahmen_fuellung(bf, d)` — Rahmen, Muster und Füllung.
  - `_stil_auf_block(blk, name)`
  - `_zeichen_auf_block(blk, d)`
  - `_zeichen_der_vorlage(d)` — Das Zeichenformat einer Vorlage (alle Felder des Fensters „Schriftart“). Was die Vorlage nicht setzt, bleibt in der Auswahl, wie es ist.
  - `_ebene_der_vorlage(blk, name)` — „Verbinden mit Formatvorlage“ (Gliederung anpassen): ein Absatz mit dieser Vorlage gehört zur verbundenen Ebene der Gliederung.
  - `stil_tasten()` — Die Tastenkombinationen der Formatvorlagen (nur gültig, solange der Editor den Fokus hat).
  - `_liste_auf_block(blk, text)` — Absatz einer Formatvorlage mit Liste: aufeinanderfolgende Absätze mit derselben Liste zählen gemeinsam.
  - `liste_spec()` — Die Liste des Absatzes an der Schreibmarke (siehe ``editor.text.listen``) oder None.
  - `_mehrstufig_am_zeiger()` — (Ebene, Gliederung) des Absatzes an der Schreibmarke, wenn er zu einer mehrstufigen Liste gehört.
  - `stil_neu_anwenden(name)` — Nach „Formatvorlagen verwalten“: alle Absätze dieser Vorlage im Dokument neu formatieren.
  - `_stil_name(bf)`
  - `stil_aus_auswahl()` — Definition für eine neue Formatvorlage nach dem Absatz, in dem die Schreibmarke steht.
  - `_absatz_felder(bf)` — Die Felder des Fensters „Absatz“ (außer Ausrichtung, Einzug links, Abstände), als Felder einer Formatvorlage.
  - `_zeichen_felder(cf)` — Die Felder des Fensters „Schriftart“ (ohne Schrift, Größe, Schnitt, Farbe) eines Zeichenformats, als Felder einer Formatvorlage.
  - `_rahmen_felder()` — Rahmen und Schattierung des Absatzes an der Schreibmarke als Felder einer Formatvorlage.
  - `stil_entfernen(name)` — Eine gelöschte eigene Vorlage: die Absätze behalten ihr Aussehen, verlieren aber die Zuordnung.
  - `current_style()`

### `oberflaeche/dokument/bearbeitung/editor_werkzeuge.py`

EditorWerkzeuge: fachlich abgegrenzte Editor-Funktionen.

- **class `EditorWerkzeugeMixin`** — Teilbereich der Formatierungs- und Bearbeitungsfunktionen.
  - `insert_page_break()`
  - `insert_column_break()`
  - `insert_table(rows, cols, borders, spaltenbreite)` — Tabelle an der Schreibmarke; ``spaltenbreite`` (Bildpunkte): feste Spalten, sonst passt sie sich der Seitenbreite an.
  - `insert_image(path)`
  - `insert_link(url, text, tipp)` — Link an der Schreibmarke; mit Markierung wird sie zum Link. ``tipp``: QuickInfo beim Überfahren.
  - `find_text(text, backwards, case, whole)`
  - `replace_current(find, repl, case)`
  - `_format_am_anfang(cur)` — Das Zeichenformat des ersten Zeichens der Markierung (``charFormat()`` eines Cursors mit Markierung wäre das davor).
  - `replace_all(find, repl, case, whole)`

### `oberflaeche/dokument/bearbeitung/editor_zeichenformat.py`

Zeichenformat: fachlich abgegrenzte Editor-Funktionen.

- **class `ZeichenformatMixin`** — Teilbereich der Formatierungs- und Bearbeitungsfunktionen.
  - `_kf()` — Der Kopf-/Fußzeilen-Bearbeiter, solange die Schreibmarke dort steht (dann wirken die Start-Werkzeuge auf die Zeile), sonst None.
  - `_kf_fertig(kf)`
  - `_merge(fmt)`
  - `toggle_bold(on)`
  - `toggle_italic(on)`
  - `toggle_underline(on)`
  - `set_underline_style(stil)`
  - `set_outline(an)`
  - `set_letter_spacing(px)`
  - `set_capitalization(cap)`
  - `toggle_strike(on)`
  - `set_script(kind)`
  - `set_font_family(family)`
  - `set_font_size(pt)`
  - `grow_font(delta)`
  - `set_text_color(color)`
  - `set_highlight(color)`
  - `change_case(mode)`
  - `clear_formatting()`

### `oberflaeche/dokument/bearbeitung/freie_bilder_bedienung.py`

Frei positionierte Bilder im Editor: zeichnen, anklicken, verschieben, in der Größe ändern, löschen (siehe editor/objekte/freie_bilder.py).

- **class `FreieBilderMixin`**(FreieBilderZeichnenMixin, FreieBilderInteraktionMixin, FreieBilderKnotenMixin, FreieBilderKnoepfeMixin)
  - `_frei_sel()`
  - `_frei_sel(wert)`
  - `_frei_init()`
  - `_frei_schluessel(a)`
  - `_frei_index_pruefen(doc, g, z, schl)` — Den Index der Körperbilder (Absatz → Angaben) neu bauen, wenn sich Dokument, Zoom, Seite oder Bildzahl geändert haben.
  - `_frei_vorlaeufig_anwenden(key, bild, k)` — Das Objekt, das gerade gezogen wird: vorläufige Angabe, Rechteck und (bei Live-Vorschau) das Vorschaubild.
  - `_frei_liste_bauen(doc, z)`
  - `_frei_liste()` — Alle frei positionierten Bilder aller Blätter: (Schlüssel, Angabe, Bild, Rechteck im Editor, hinter, Blatt-Nr.). Unabhängig davon, was
  - `_frei_rechteck(a, n)`
  - `_frei_angabe()` — Die Angabe des gewählten freien Objekts (oder None).
  - `_frei_abbilden(r, a, rr)`
  - `_frei_griff_mitte(r, name)`
  - `_frei_adj_lagen(r, a)` — Lage der Anpassungsgriffe (gelbe Raute) der gewählten Form in Editor-Koordinaten: {"adj0": Punkt, …}; leer bei anderen Objekten.
  - `_frei_absatz_aendern(blk, idx, neu)` — Ändert (oder, mit ``neu=None``, entfernt) die Angabe ``idx`` am Absatz ``blk`` — als ein Schritt, den Rückgängig zurücknimmt.

### `oberflaeche/dokument/bearbeitung/freie_bilder_geometrie.py`

Maße und reine Geometrie der frei positionierten Bilder im Editor (Griffe, Rahmen, Anpassungsgriffe) — kein Zeichnen, keine Maus, kein Zustand.

- `griff_mitte(r, name)` — Mitte des Griffs ``name`` (acht Größengriffe oder ``rot``) am Rahmen ``r``.
- `abbilden(r, a, rr)` — Ein Rechteck in logischen Bildpunkten des Objekts (Breite ``b`` × Höhe ``h``) in Editor-Koordinaten (Zoom, Lage) umrechnen.
- `um_mitte_drehen(punkt, r, grad)` — Ein Punkt um die Mitte von ``r`` um ``grad`` Grad gedreht.
- `adj_lagen(r, a, vorlaeufig)` — Lage der Anpassungsgriffe (gelbe Raute) einer Form in Editor-Koordinaten: {"adj0": Punkt, …}; leer bei anderen Objekten.
- `drehwinkel(mitte, pos, raster)` — Der Winkel (Grad, 0 = oben) von der Mitte zur Maus; ``raster``: auf 15 Grad gerundet.
- `_kanten_verschieben(r, griff, dx, dy)`
- `groesse_rechteck(r, griff, dx, dy, frei)` — Das Rechteck ``r`` nach dem Ziehen am Griff ``griff`` um (``dx``, ``dy``); ohne ``frei`` bleibt das Seitenverhältnis erhalten.

### `oberflaeche/dokument/bearbeitung/freie_bilder_interaktion.py`

Frei positionierte Bilder im Editor: Bedienung mit Maus und Tastatur — anklicken, Griffe, ziehen, ablegen, Entf/Esc/Enter.

- **class `FreieBilderInteraktionMixin`**
  - `_frei_griff_bei(pos)`
  - `_frei_griff_name(pos, a, r)` — Der Griff unter ``pos``: erst die Anpassungsgriffe der Form, dann die acht Größengriffe und der Drehgriff.
  - `_frei_text_bei(pos)` — Liegt an dieser Stelle Text? Dann gehört der Klick dem Text, nicht einem Bild dahinter.
  - `_frei_bild_bei(pos, auch_hinten)`
  - `_frei_gewaehlt_rect()` — (Schlüssel, Rechteck im Editor) des gewählten Objekts oder None.
  - `_frei_maus(e, art)` — True, wenn das Ereignis ein Bild betrifft und der Editor es nicht weiter behandeln soll.
  - `_frei_maus_leer(art)` — Keine Bilder oder schreibgeschützt: ein Klick hebt eine alte Auswahl auf; der Editor behandelt das Ereignis.
  - `_frei_punkte_maus(e, art)` — Punkte einer Form bearbeiten: die Maus gehört zuerst der Punktbearbeitung.
  - `_frei_knopf_klick(e, pos)` — Klick auf eine Schaltfläche neben dem gewählten Objekt.
  - `_frei_treffer_bei(e, pos)` — (Griff, Treffer) unter der Maus: erst Griffe und Rahmen des gewählten Objekts, sonst ein Bild — hinter dem Text mit Strg+Alt, oder wenn an der
  - `_frei_abwaehlen()` — Klick ins Leere: Teil, Knoten und Objekt abwählen; ein offener Formatbereich geht zu.
  - `_frei_format_uebertragen(key, merk)` — „Format übertragen“ wartet auf das Zielbild: das Format auf das angeklickte Objekt anwenden.
  - `_frei_maus_druecken(e, pos)`
  - `_frei_auswaehlen(key, a, pos, griff)` — Das Objekt ``key`` wählen: Teil und Knoten eines vorher gewählten anderen Objekts werden abgewählt, ein Klick in das schon markierte
  - `_frei_knopf_tipp_zeigen(e, pos)` — Tooltip der Schaltfläche unter der Maus; True, wenn die Maus über einer Schaltfläche des gewählten Objekts steht.
  - `_frei_cursor_setzen(cursor)`
  - `_frei_maus_bewegen(e, pos)`
  - `_frei_ziehen_anpassen(e, griff, a0, r0)` — Gelbe Raute: der Parameter folgt der Maus, gespeichert wird beim Loslassen.
  - `_frei_ziehen_drehen(e, a0, r0)` — Drehgriff: der Winkel zeigt von der Mitte zur Maus (mit Umschalt in 15-Grad-Schritten).
  - `_frei_ziehen_rahmen(e, art, griff, start, a0, r0, n)` — Verschieben und Größe ändern: der vorläufige Rahmen in Blattkoordinaten.
  - `_frei_ziehen(e)`
  - `_frei_adj_vorschau(a0, i, wert)` — Die Form beim Ziehen der gelben Raute laufend neu zeichnen (nur das Bild, kein Dokumentschritt).
  - `_frei_ablegen()`
  - `_frei_ablage_speichern(neu)` — Die neue Lage/Größe in das Objekt schreiben: frei an der Seite oder am Absatz (dann als ein Rückgängig-Schritt).
  - `_frei_taste_esc()`
  - `_frei_taste_loeschen()`
  - `_frei_taste_knoten(e)` — SmartArt-Knoten: Enter/F2 oder Tippen schreibt im Knoten; None, wenn die Taste nicht dafür ist.
  - `_frei_taste(e)`

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

### `oberflaeche/dokument/bearbeitung/freie_bilder_zeichnen.py`

Frei positionierte Bilder im Editor: Darstellung — die Bilder selbst, der Auswahlrahmen mit Griffen, die Schaltflächen neben dem Objekt und die Rahmen

- **class `FreieBilderZeichnenMixin`**
  - `_frei_edit_nachfuehren()` — Das Eingabefeld im SmartArt-Knoten bzw. im Objekt folgt dem Blatt.
  - `_frei_bild_zeichnen(p, r, a, bild)`
  - `_frei_zeichnen(p, sicht, hinter)` — Bilder der sichtbaren Blätter, hinter (``hinter``) oder vor dem Text; die vorderen zeichnen auch die Auswahl.
  - `_frei_auswahl_ueber(p, sicht)` — Die Auswahl des gewählten Objekts (Textmarkierung, Rahmen, Griffe, Knöpfe) über den Bildern.
  - `_frei_text_markieren(p, r, a, bild)` — WordArt wie in der Vorlage: der Text im gewählten Objekt ist grau hinterlegt (nur der Text, kein Kasten über dem Objekt).
  - `_frei_leiste()` — Die Schaltflächen neben dem markierten Objekt: für Bilder und Diagramme eigene, sonst die der Formen und WordArt.
  - `_frei_anker_rect(r)` — Das Absatz-Symbol links vom Rahmen; beim Textfeld neben dem Drehgriff (wie in der Vorlage).
  - `_frei_leisten_rects(r, x, leiste)` — Die Knöpfe der Leiste: rechts neben dem Bild, am SmartArt-Knoten senkrecht daneben (wie in der Vorlage); dazu der Knoten.
  - `_frei_knopf_rects(r)` — Die Schaltflächen rechts neben dem Bild: oben der Minus-Knopf (klappt sie ein), darunter Layoutoptionen, Formstile, Füllung, Kontur.
  - `_frei_anker_zeichnen(p, k)` — Seite mit Pfeil nach unten (Menü).
  - `_frei_minus_zeichnen(p, k, offen)`
  - `_frei_knopf_zeichnen(p, name, k, offen)` — Eine Schaltfläche: weißer Grund, grau, wenn der Befehl nicht möglich ist, darauf das Sinnbild.
  - `_frei_dunkel(name)` — Das Symbol dunkel gefärbt: die Knöpfe am Bild sind immer weiß, auch im dunklen Design (dort wären die Symbole sonst hell auf weiß).
  - `_frei_zuschnitt_griffe(p, r)` — Zuschneiden: schwarze Eckwinkel und Kantenstriche statt der runden Griffe.
  - `_frei_drehgriff_zeichnen(p, r, a)` — Der Drehgriff über der Mitte der Oberkante (nicht beim Zeichenbereich, wie in der Vorlage).
  - `_frei_rund_griffe(p, r, a)` — Runde Griffe wie in der Vorlage (weiße Kreise, grauer Rand), Drehgriff und die gelbe Raute der Anpassungsgriffe.
  - `_frei_auswahl_zeichnen(p, r, a)`
  - `_frei_diagramm_teil_rects(r, a)` — Rechtecke (Editor-Koordinaten) des gewählten Diagrammteils und die Achse, an der Griffe an den Enden sitzen (``h``, ``v``, ``kein`` oder None).
  - `_frei_teil_punkte(x, achse)` — Die Griffpunkte um ein Teilrechteck: an den Enden einer Achse, sonst alle acht.
  - `_frei_teil_rects(r, a)` — Rechtecke des gewählten Diagrammteils bzw. SmartArt-Knotens (Editor-Koordinaten) und die Achsenart.
  - `_frei_teile_zeichnen(p, r, a)` — Rahmen mit kleinen runden Griffen um den gewählten Diagrammteil bzw. SmartArt-Knoten (dünner als der Rahmen des Objekts).

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

### `oberflaeche/dokument/bearbeitung/zusatz_editor.py`

Editor-Seite von Kommentaren, Fuß-/Endnoten und Änderungsverfolgung (Mixin für DocumentEditor).

- `autor_farbe(autor)`
- **class `ZusatzMixin`**
  - `_zusatz_init()`
  - `zusatz_binden(meta)` — Meta-Daten des Dokuments (Kommentartexte, Noten) mit dem Editor teilen.
  - `_fragmente()`
  - `_bereiche(prop, schluessel)` — Zusammenhängende Textstücke mit gleicher Eigenschaft: [{von, bis, wert, cf}].
  - `kommentar_bereiche()`
  - `aenderungen()`
  - `noten_stellen()`
  - `_bereich_format(von, bis, props)`
  - `_eigenschaft_weg(prop, pred, von, bis)`
  - `kommentar_neu(text, autor)`
  - `set_suchtreffer(bereiche)` — Alle Treffer der Suche farbig hinterlegen (leere Liste nimmt die Markierung weg).
  - `kommentar_text_setzen(kid, text)` — Den Text eines Kommentars ändern; Blase und Karte zeigen ihn sofort neu.
  - `kommentar_geloest(kid, geloest)` — Einen Kommentar als gelöst markieren (oder wieder öffnen); er bleibt im Dokument.
  - `kommentar_loeschen(kid)`
  - `kommentare_alle_loeschen()`
  - `_springe(bereiche, delta)`
  - `kommentar_springen(delta)`
  - `kommentar_am_cursor()`
  - `note_neu(art, text)`
  - `noten_neu_nummerieren()`
  - `note_loeschen(art, nid)`
  - `note_an(pos)` — (Art, Id) der Note, deren Zeichen an Stelle `pos` liegt (oder direkt davor), sonst None.
  - `notentext_geaendert()` — Der Text einer Note wurde im Notenfeld geändert: Seitenansicht und Karten links ziehen nach (gebündelt, nicht bei jedem Zeichen).
  - `note_springen(delta, art)` — Zur nächsten (delta 1) oder vorigen (-1) Note springen; ``art`` "f" oder "e" nur Fuß- bzw. Endnoten.
  - `set_verfolgen(an)`
  - `_markiere_geloescht(von, bis, autor)` — Statt zu löschen als gelöscht kennzeichnen — eigener, noch nicht angenommener Einfügetext verschwindet wirklich. ``autor``: Name statt des Nutzers (z. B. KI).
  - `ersetze_verfolgt(von, bis, neu, autor)` — Als nachverfolgte Änderung ersetzen: das Alte bleibt als „del“ stehen, ``neu`` kommt direkt dahinter als „ins“ (Autor ``autor`` oder der Nutzer).
  - `_loesche_verfolgt(von, bis, ende)`
  - `_verfolgte_taste(e)`
  - `_jetzt()`
  - `_inhalt_geaendert(pos, entfernt, hinzu)`
  - `aenderung_annehmen(b, annehmen)`
  - `alle_aenderungen(annehmen)`
  - `aenderung_sichtbar(b)` — Ob eine Änderung zum gewählten Markup gehört (Bearbeiter, Tag).
  - `angezeigte_aenderungen(annehmen)` — Nur die Änderungen annehmen oder ablehnen, die das Markup gerade zeigt.
  - `markup_filter_setzen(**werte)`
  - `aenderung_springen(delta)`
  - `aenderung_am_cursor()`
  - `_zus_geaendert()`
  - `set_markup(an)`
  - `_zusatzauswahl(doc, von, bis, fmt)` — Eine Zusatzauswahl (nur Anzeige) von ``von`` bis ``bis``.
  - `_hintergrund(farbe)`
  - `_overlays_neu()` — Wellenlinien der Schreibhilfe plus Markup (Kommentare, Änderungen) als Zusatzauswahl — nichts davon landet im Format.
  - `_overlay_wellen(doc)`
  - `_overlay_luecken(doc)` — Lücken «…» der Vorlagen und Textbausteine: gelb nur in der Ansicht, nie in der Datei.
  - `_overlay_felder(doc)`
  - `_overlay_formular(doc)`
  - `_overlay_kommentare(doc)`
  - `_aenderung_format(stil, farbe)` — Darstellung einer verfolgten Änderung nach der gewählten Stilart.
  - `_overlay_aenderungen(doc)`

## `oberflaeche/dokument/dokumentfenster`

### `oberflaeche/dokument/dokumentfenster/__init__.py`

Unterpaket ``dokumentfenster`` von ``lunivo_writer.oberflaeche.dokument``.


### `oberflaeche/dokument/dokumentfenster/dokument_bereich.py`

Ein geöffnetes Dokument: Editor auf grauem Arbeitsgrund, Pfad, Meta, Wiederherstellungs-Kennung.

- **class `DocumentTab`**(QScrollArea)
  - `__init__(loaded, path, title)`
  - `set_layout(art)` — blatt (Drucklayout) \| web (Weblayout) \| doppelt (Zwei Seiten, nur Ansicht).
  - `resizeEvent(ev)`
  - `_rand(seite, mm)`
  - `zeige_lineale(waagerecht, senkrecht)`
  - `_lineale_anordnen()` — Lineale in den Rand des Viewports legen; nur im Drucklayout (Weblayout und Zwei Seiten haben keine Blattkanten).
  - `_lineale_neu_zeichnen(*_)`
  - `zoom_breite()` — Seitenbreite: die Seite füllt die Breite des Fensters.
  - `zoom_seite()` — Eine Seite: die ganze Seite ist sichtbar.
  - `page()`
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
  - `_ersatz_formate()` — Zeichenformat und Absatz-Änderung für „Ersetzen durch“ (aus „Format“ am Ersetzen-Feld).
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

Unterpaket ``kopffuss`` von ``lunivo_writer.oberflaeche.dokument``.


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

Unterpaket ``tabelle`` von ``lunivo_writer.oberflaeche.dokument``.


### `oberflaeche/dokument/tabelle/tabelle_griffe.py`

Bedienelemente direkt an der Tabelle im Dokument (wie in gewohnten Textprogrammen): Verschiebegriff oben links, „+“ rechts und unten, Aufziehgriff unten rechts

- `dunkel(symbol, px)` — Symbol in dunkler Tinte für die hellen Knöpfe (``icons.icon`` richtet sich nach der Fensterpalette und wäre auf Hellgrau weiß).
- **class `_Vorschau`**(QWidget) — Gestrichelter Rahmen (Aufziehen) oder Linie (Rand) in der Zielgeometrie; durchsichtig für die Maus.
  - `__init__(vp)`
  - `paintEvent(e)`
- **class `_Grau`**(QWidget) — Graue, durchscheinende Fläche über der markierten Tabelle (Qt füllt leere Zellen einer Auswahl nicht); durchsichtig für die Maus.
  - `__init__(vp)`
  - `paintEvent(e)`
- **class `_Rand`**(QWidget) — Durchsichtiger Streifen über einem Spalten- (senkrecht) oder Zeilenrand (waagrecht); Ziehen meldet die Bildpunkte seit dem Start
  - `__init__(vp, bei_start, bei_ziehen, bei_ende, waagrecht)`
  - `mousePressEvent(e)`
  - `mouseMoveEvent(e)`
  - `mouseReleaseEvent(e)`
- **class `_Griff`**(QToolButton) — Ein kleiner Knopf auf dem Sichtbereich; Ziehen meldet die Mausbewegung an ``bei_ziehen`` (Bildpunkte seit dem Start).
  - `__init__(vp, symbol, tipp, bei_klick, bei_ziehen, bei_ende, bei_start, cursor, ende_immer)`
  - `paintEvent(e)`
  - `mousePressEvent(e)`
  - `mouseMoveEvent(e)`
  - `mouseReleaseEvent(e)`
- **class `TabellenGriffe`**(QObject)
  - `__init__(ed)`
  - `eventFilter(obj, ev)`
  - `_bloecke_schliessen()` — Offene Ziehvorgänge (Esc, Fokusverlust) ohne Änderung verwerfen.
  - `tabelle()`
  - `_gezeichnet(t)` — Der wirklich gezeichnete Rahmen in Layoutkoordinaten: aus den Zellen (Inhalt plus Innenabstand), nicht aus ``frameBoundingRect``
  - `rechteck(t)` — Die Tabelle (erste Seite, wenn sie über mehrere läuft) in Bildpunkten des Sichtbereichs.
  - `_verstecken()`
  - `aktualisieren()`
  - `_ausblenden(halter)` — Alle Tabellensymbole außer dem gezogenen verstecken; dieses bleibt sichtbar, zeichnet aber nichts (behält die Maus).
  - `_einblenden()`
  - `_ziehen_start(t, halter)` — Merkt Rechteck und Zoom beim Start; ab jetzt ruht ``aktualisieren`` (auch das Absatz-Symbol).
  - `_ziehen_ende(anwenden)` — Loslassen (``anwenden``) oder Verwerfen: die vorgemerkte Änderung genau einmal und als ein Rückgängig-Schritt ausführen.
  - `_ziehen_frei(geaendert)` — Ruhe aufheben und einmal vollständig aktualisieren.
  - `_markieren()` — Die ganze Tabelle grau zeigen (wie in gewohnten Textprogrammen beim Aufziehen); die Textauswahl bleibt unberührt, ``_ziehen_ende`` blendet die Fläche aus.
  - `_auswahl_alle(t)`
  - `_griffe_setzen(r)`
  - `_vorschau_zeigen(geo, linie)`
  - `_grenzen(t)` — x-Abstand jeder Spaltengrenze (0 = linker Tabellenrand, n = rechter) vom linken Tabellenrand, in Bildpunkten.
  - `_raender_setzen(t, r)`
  - `_rand_start(spalte)`
  - `_rand_ziehen(dx)`
  - `_spalten_anwenden(w)`
  - `_rand_ende(geaendert)`
  - `_zeilenraender_setzen(t, r)`
  - `_zeile_start(zeile)`
  - `_zeile_ziehen(dy)`
  - `_zeile_ende(geaendert)`
  - `_waehlen()`
  - `_anhaengen(spalte)` — Symbole kurz ausblenden, Spalte/Zeile anhängen, nach dem Layout am neuen Rand wieder einblenden (kein zweiter Klick dazwischen).
  - `_verschieben_zeigen(d, gp)`
  - `_verschieben_frei()`
  - `_verschieben_ende(gp)` — Tabelle an die Stelle unter der Maus verschieben (vor den Absatz, auf dem losgelassen wird).
  - `_verschieben_ende_tun(gp)`
  - `_aufziehen_start()`
  - `_aufziehen(d, gp)` — Nur der gestrichelte Rahmen von der oberen linken Ecke bis zum Ziel; die Tabelle bleibt (grau markiert) unverändert.
  - `_aufziehen_ende(gp, geaendert)` — Loslassen: einmal skalieren (auch bei Klick ohne Ziehen wird der Vorgang geschlossen).

### `oberflaeche/dokument/tabelle/tabelle_radierer.py`

„Radiergummi“ (Tabellentools): ein Klick auf eine Zellenlinie löscht sie; die beiden Zellen daneben werden zu einer verbunden.

- `_pad(zelle, name, tabelle)` — Innenabstand der Zelle (links/oben); ohne eigenen Wert gilt der der Tabelle.
- `gitter(ed, t)` — (x der Spaltengrenzen, y der Zeilengrenzen) der Tabelle in Dokumentkoordinaten, je ``columns+1`` bzw. ``rows+1`` Werte.
- `kante_finden(ed, t, dx, dy, toleranz)` — Nächste Zellenlinie zum Punkt (Dokumentkoordinaten): ``(zeile, spalte, seite, (x1, y1, x2, y2))`` oder ``None``.
- `_radierer_cursor()` — Radiergummi in Dunkel mit weißem Rand (wie der Stift): auf weißem Blatt wie auf dunklem Grund gut zu sehen; heißer Punkt unten links.
- **class `TabellenRadierer`**(QWidget)
  - `__init__(ed)`
  - `_doc(pt)`
  - `_view(x, y)`
  - `treffer(pt)` — Die Linie unter dem Punkt des Sichtbereichs: ``(tabelle, (zeile, spalte, seite, linie))`` oder ``None``.
  - `_im_dokument(global_pos)`
  - `eventFilter(obj, ev)`
  - `loeschen(pt)` — Die Linie unter ``pt`` löschen (ein Rückgängig-Schritt); sonst kurze Meldung in der Statusleiste.
  - `_hervorheben(pt)`
  - `beenden()`
  - `paintEvent(_e)`

### `oberflaeche/dokument/tabelle/tabelle_stift.py`

„Tabelle zeichnen“ (Einfügen ▸ Tabelle): mit dem Stift ein Rechteck auf die Seite ziehen; gestrichelt erscheinen die Zellen und

- `groesse(breite, hoehe, zoom)` — (Zeilen, Spalten) für ein gezogenes Rechteck; mindestens 1 × 1.
- `_stift_cursor()` — Stift in Dunkel mit weißem Rand: auf weißem Blatt wie auf dunklem Grund gut zu sehen (Spitze oben links).
- `andere_beenden(ed)` — Stift und Radiergummi schließen sich gegenseitig (und ein früherer derselben Art); der Mauszeiger wird dabei zurückgesetzt.
- `ueberwachen(w, ed, bei_tabellenverlust)` — Beendet das Werkzeug ``w`` (mit ``beenden()``), wenn der Reiter des Bandes wechselt, die Anwendung endet oder der Editor zerstört wird;
- `cursor_zurueck(w)`
- **class `TabellenStift`**(QWidget)
  - `__init__(ed)`
  - `_im_dokument(global_pos)`
  - `eventFilter(obj, ev)`
  - `_druecken(ev)` — Mausklick: links setzt den Anfang der Linie, sonst (auch außerhalb des Dokuments) endet der Stift; der Klick außerhalb geht weiter.
  - `_ziehen(ev)` — Bewegung mit dem Stift: die Linie folgt der Maus.
  - `_einfuegen()`
  - `_rechteck()`
  - `zellen()`
  - `beenden()`
  - `paintEvent(_e)`

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
  - `kopffuss_starten(editor, header)` — Kopf- oder Fußzeile auf der Seite bearbeiten: Textfeld über dem Rand, Kontext-Reiter „Kopf- und Fußzeile“ eingeblendet und aktiv.
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
  - `objektformat_sichtbar()`
  - `aktualisiere_objektformat(werte)`
  - `zeige_diagrammformat(werte, anwenden, alt_anwenden, bild_wunsch, teil_wunsch)`
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

### `plattform/sperre.py`

Sperre auf eine Sperrdatei, die auch zwischen Lunivo-Fenstern (Prozessen) gilt: fcntl unter Linux/macOS, msvcrt unter Windows.

- **class `SperreBelegt`**(Exception) — Ein anderer Prozess hält die Sperre.
- `sperr_ordner()` — Ordner für die Sperrdateien (nur für den Benutzer); wird bei Bedarf angelegt.
- `sperre_oeffnen(datei)` — Sperrdatei öffnen und sofort sperren; gibt den Dateideskriptor zurück. Belegt → SperreBelegt, sonst OSError.
- `sperre_freigeben(fd)`

