# Grid-Umstellung der Oberfläche — Abschlussbericht (2026-11-24)

## Ergebnis
Die gesamte selbst entwickelte Qt-Oberfläche unter `src/lunivo_writer/` ordnet ihre Bedienelemente ausschließlich mit `QGridLayout`.
Im Quelltext gibt es kein `QVBoxLayout`, `QHBoxLayout`, `QBoxLayout`, `QFormLayout` oder `QStackedLayout` mehr (auch nicht als Import);
`QGridLayout` wird nur im Raster-Kern erzeugt bzw. abgeleitet; keine Layoutklasse setzt Elementpositionen selbst (`item.setGeometry`).
Das sichert `tests/oberflaeche/test_raster_architektur.py` dauerhaft ab.

## Zentrale Grid-Architektur (eine Stelle)
* **`baukasten/basis/raster.py`** (neu) — der Raster-Kern:
  * `RasterLayout(QGridLayout)` — Basis aller Layouts.
  * `RasterLinie` / `RasterSpalte` / `RasterZeile` — Elemente der Reihe nach in Zellen `(i, 0)` bzw. `(0, i)`; Dehnung = Zeilen-/Spaltendehnung
    (wirkt nur, solange die Zelle belegt und sichtbar ist), Abstand = Zellenabstand, `addStretch`/`addSpacing` = Platzhalterzellen,
    `insertWidget`/`insertLayout` ordnen die Zellen neu, `senkrecht_stellen()`/`waagerecht_stellen()` drehen die Linie.
  * `PlanRaster` — responsives Gitter: bei jeder Breite neue Zellenbelegung, Spalten-/Zeilenmaße; Anordnung macht das `QGridLayout`.
  * `kanten_anordnung` — Gitterlinien an den Kanten der Elemente (für das Formular und die Knopfzeile).
* **`baukasten/geruest/rollen.py`** — die eine Stelle der Rasterregeln (Außenränder, Abstände); `spalte()`/`reihe()` erzeugen jetzt Gitterlinien.
  Neue Rollen: `formatseite`, `bandhalter`, `menuekopf`, `bandgruppe` (Werte in `mass.py`: `RAND_BANDHALTER`, `RAND_MENUEKOPF`).

### Überarbeitete Baukastenklassen
| Baustein | vorher | jetzt |
|---|---|---|
| `spalte()` / `reihe()` (rollen.py, ~470 Aufrufe in 90+ Dateien) | QVBoxLayout / QHBoxLayout | RasterSpalte / RasterZeile (QGridLayout) |
| `tabellen_gitter()` | QGridLayout direkt | RasterLayout |
| `KartenRaster` | eigenes QLayout mit `setGeometry` | PlanRaster: n gleich breite Spalten, Spannen als Zellenbereiche |
| `FlussLayout` | eigenes QLayout mit `setGeometry` (natürliche Breiten, versetzt) | PlanRaster: gleich breite Spalten, die umbrechen; Beschriftung+Feld als Einheit |
| `FormularGitter` | eigenes QLayout mit `setGeometry` | PlanRaster mit Kantenraster (Paare, zwei Paare je Zeile, gestapelt, `reihe`) |
| `_KnopfLayout` (Knopfzeile aller Dialoge) | eigenes QLayout mit `setGeometry` | PlanRaster; Rand aus dem Fenster, Mindestgröße mit Rändern (Überlappung behoben) |
| `kachel_gitter()` / `KachelFeld` | QGridLayout mit ungleichen Spalten | gleich breite, gleich dehnbare Kachelspalten |
| `Kachelraster` (Dashboard) | tabellen_gitter | unverändert, jetzt RasterLayout |
| `ZweiSpalter` | QBoxLayout mit setDirection | RasterSpalte mit senkrecht/waagerecht_stellen |
| `kurze_gruppen_ins_raster` | erkannte QVBoxLayout | erkennt senkrechte RasterLinie; verankert in `DialogRahmen`, `PanelRahmen` (showEvent) und wie bisher `ZusatzPanel` |
| `schmal_machen` | QHBoxLayout/QGridLayout-Logik | RasterLinie/RasterLayout; PlanRaster bleibt unberührt |
| `FlowLayout` (bauteile/fluss_layout.py) | zweites Fließ-Layout | **gelöscht** (konkurrierend, unbenutzt) |

## Ersetzte Layouttypen
QVBoxLayout, QHBoxLayout, QBoxLayout (inkl. setDirection), vier eigene QLayout-Klassen mit manueller Positionierung, ein zweites Fließ-Layout.
QFormLayout/QStackedLayout kamen nicht vor.

## Geänderte Dateien

Neu: `src/vcl/qt/widgets/bausteine/basis/raster.py`, `tests/oberflaeche/test_raster_architektur.py`  
Gelöscht: `src/lunivo_writer/oberflaeche/bauteile/fluss_layout.py`

* `kern/befehle/hauptreiter/einfuegen_objekte.py`
* `kern/befehle/hauptreiter/ueberpruefen.py`
* `kern/befehle/kontextreiter/kopffuss.py`
* `oberflaeche/backstage.py`
* `oberflaeche/band/band_gruppen.py`
* `oberflaeche/band/band_leiste.py`
* `oberflaeche/band/band_raender.py`
* `oberflaeche/band/band_reiter.py`
* `oberflaeche/band/band_stile.py`
* `oberflaeche/band/werkzeugleisten.py`
* `oberflaeche/baukasten/basis/dialog_rahmen.py`
* `oberflaeche/baukasten/basis/linien.py`
* `oberflaeche/baukasten/basis/mass.py`
* `oberflaeche/baukasten/chat/chat_anhang.py`
* `oberflaeche/baukasten/chat/chat_blase.py`
* `oberflaeche/baukasten/chat/chat_eingabe.py`
* `oberflaeche/baukasten/chat/chat_leerzustand.py`
* `oberflaeche/baukasten/chat/chat_regler.py`
* `oberflaeche/baukasten/diagramme/diagramm_format_bausteine.py`
* `oberflaeche/baukasten/diagramme/diagramm_format_panel.py`
* `oberflaeche/baukasten/diagramme/diagramm_text_panel.py`
* `oberflaeche/baukasten/dokument/aenderungs_fenster.py`
* `oberflaeche/baukasten/dokument/druck_dialog.py`
* `oberflaeche/baukasten/dokument/druckvorschau.py`
* `oberflaeche/baukasten/dokument/eingabe_fenster.py`
* `oberflaeche/baukasten/dokument/erstellen_fenster.py`
* `oberflaeche/baukasten/dokument/layout_dialog.py`
* `oberflaeche/baukasten/dokument/liste_dialog.py`
* `oberflaeche/baukasten/dokument/pdf_export.py`
* `oberflaeche/baukasten/dokument/sortieren_dialog.py`
* `oberflaeche/baukasten/dokument/speichern_fenster.py`
* `oberflaeche/baukasten/dokument/stimme_dialog.py`
* `oberflaeche/baukasten/dokument/tabstopp_dialog.py`
* `oberflaeche/baukasten/dokument/tasten_dialog.py`
* `oberflaeche/baukasten/dropdown/auswahl/farbpalette.py`
* `oberflaeche/baukasten/dropdown/auswahl/raster_auswahl.py`
* `oberflaeche/baukasten/dropdown/auswahl/zellen_raster.py`
* `oberflaeche/baukasten/dropdown/galerie_auswahl.py`
* `oberflaeche/baukasten/dropdown/menue_tafel.py`
* `oberflaeche/baukasten/dropdown/objektmenues/bild_diagramm_menues.py`
* `oberflaeche/baukasten/dropdown/objektmenues/diagramm_popups.py`
* `oberflaeche/baukasten/dropdown/objektmenues/layout_optionen.py`
* `oberflaeche/baukasten/dropdown/objektmenues/layout_optionen_objekt.py`
* `oberflaeche/baukasten/dropdown/schalter_zeile.py`
* `oberflaeche/baukasten/dropdown/voreinstellung_menue.py`
* `oberflaeche/baukasten/felder/assistenten_liste.py`
* `oberflaeche/baukasten/felder/auswahl_bereich.py`
* `oberflaeche/baukasten/felder/farbwaehler.py`
* `oberflaeche/baukasten/felder/formular_gitter.py`
* `oberflaeche/baukasten/felder/kachel_feld.py`
* `oberflaeche/baukasten/felder/karten_raster.py`
* `oberflaeche/baukasten/felder/listen_leiste.py`
* `oberflaeche/baukasten/felder/mass_feld.py`
* `oberflaeche/baukasten/felder/schiebe_feld.py`
* `oberflaeche/baukasten/felder/winkel_feld.py`
* `oberflaeche/baukasten/formatierung/absatz_dialog.py`
* `oberflaeche/baukasten/formatierung/formatvorlage_dialog.py`
* `oberflaeche/baukasten/formatierung/objektformat_panel.py`
* `oberflaeche/baukasten/formatierung/rahmen_schattierung.py`
* `oberflaeche/baukasten/formatierung/ruby_dialog.py`
* `oberflaeche/baukasten/formatierung/schreibweise_dialog.py`
* `oberflaeche/baukasten/formatierung/schriftart_dialog.py`
* `oberflaeche/baukasten/formatierung/text_format.py`
* `oberflaeche/baukasten/formatierung/texteffekt_dialog.py`
* `oberflaeche/baukasten/formatierung/umschlossen_dialog.py`
* `oberflaeche/baukasten/geruest/befehlsseite.py`
* `oberflaeche/baukasten/geruest/einklappgruppe.py`
* `oberflaeche/baukasten/geruest/fenster_stapel.py`
* `oberflaeche/baukasten/geruest/panel_rahmen.py`
* `oberflaeche/baukasten/geruest/rollen.py`
* `oberflaeche/baukasten/geruest/schmal.py`
* `oberflaeche/baukasten/geruest/spalten.py`
* `oberflaeche/baukasten/geruest/werkbank.py`
* `oberflaeche/baukasten/geruest/zusatz_panel.py`
* `oberflaeche/baukasten/medien/bild_alternativtext_panel.py`
* `oberflaeche/baukasten/medien/bild_export.py`
* `oberflaeche/baukasten/medien/bild_zoom.py`
* `oberflaeche/baukasten/vorlagen/formatvorlagen_bereich.py`
* `oberflaeche/baukasten/vorlagen/vorlagen_chips.py`
* `oberflaeche/baukasten/vorlagen/vorlagen_galerie.py`
* `oberflaeche/bauteile/fluss_layout.py`
* `oberflaeche/bauteile/mini_leiste.py`
* `oberflaeche/dialoge/dokument_dialoge.py`
* `oberflaeche/dialoge/einfuegen/diagramm_fenster.py`
* `oberflaeche/dialoge/einfuegen/einfuegen_dialoge.py`
* `oberflaeche/dialoge/einfuegen/einfuegen_fenster.py`
* `oberflaeche/dialoge/einfuegen/formular_dialog.py`
* `oberflaeche/dialoge/einfuegen/smartart_dialog_foto.py`
* `oberflaeche/dialoge/einfuegen/sonderzeichen.py`
* `oberflaeche/dialoge/einfuegen/wasserzeichen_fenster.py`
* `oberflaeche/dialoge/ki/ki_aktions_dialoge.py`
* `oberflaeche/dialoge/ki/ki_dialoge.py`
* `oberflaeche/dialoge/ki/ki_einstellungen_panels.py`
* `oberflaeche/dialoge/ki/ki_modelle_dialoge.py`
* `oberflaeche/dialoge/lesen_hilfe/hilfe_dialoge.py`
* `oberflaeche/dialoge/lesen_hilfe/lesehilfe_dialog.py`
* `oberflaeche/dialoge/lesen_hilfe/silben_dialog.py`
* `oberflaeche/dialoge/lesen_hilfe/welche_hilfe.py`
* `oberflaeche/dialoge/oberflaeche_dialoge.py`
* `oberflaeche/dialoge/optionen.py`
* `oberflaeche/dialoge/optionen_seiten/ansicht.py`
* `oberflaeche/dialoge/optionen_seiten/befehle.py`
* `oberflaeche/dialoge/optionen_seiten/gemeinsam.py`
* `oberflaeche/dialoge/optionen_seiten/lesen.py`
* `oberflaeche/dialoge/optionen_seiten/lunivo.py`
* `oberflaeche/dialoge/optionen_seiten/name_ki.py`
* `oberflaeche/dialoge/sendungen/sendungen_dialoge.py`
* `oberflaeche/dialoge/sendungen/serien_fenster.py`
* `oberflaeche/dialoge/ueberpruefen_fenster.py`
* `oberflaeche/dialoge/verweise/verweise_dialoge.py`
* `oberflaeche/dialoge/verweise/verweise_fenster.py`
* `oberflaeche/dokument/dokumentfenster/dokument_reiter.py`
* `oberflaeche/dokument/dokumentfenster/navigation.py`
* `oberflaeche/dokument/dokumentfenster/suchen_feld.py`
* `oberflaeche/hauptfenster/backstage_seitenleisten.py`
* `oberflaeche/programmfenster.py`
* `oberflaeche/seitenleiste/panels/ki_panel.py`
* `oberflaeche/seitenleiste/panels/schreib_panel.py`
* `oberflaeche/seitenleiste/seitenleiste.py`

Art der Änderung: zentrale Bausteine umgebaut (siehe Tabelle); direkte Box-Layouts in `kern/befehle` (3), Band (`band_gruppen.py`,
`werkzeugleisten.py`), Dialogen (Schriftart, Ruby, Wasserzeichen, Verweise, Diagramm, Einfügen, DialogRahmen), Panels (`panel_rahmen.py`,
`diagramm_text_panel.py`, `diagramm_popups.py`, `text_format.py`, `chat_blase.py`, `linien.py`) auf Rollen-Gitter umgestellt; übrige Dateien:
ungenutzte Box-Importe entfernt bzw. Typangaben auf `RasterSpalte`/`RasterZeile` (AST-gestützt, nur Importanweisungen und Annotationen).
Signale, Slots, Objektnamen, Tab-Reihenfolge, Texte und Fachlogik sind unverändert.

## Tests (gezielt)
* `tests/oberflaeche/test_raster_architektur.py` (neu, 16 Prüfungen): Architekturregeln (keine abweichenden Layouts, QGridLayout nur im Kern,
  keine manuelle Positionierung, kein globaler Hook); Verhalten: Zellenfolge/Dehnung/Ausblenden/Drehen der Gitterlinie; FlussLayout in
  gleichen Spalten bei 180/320/900 px inkl. Signal; KartenRaster bei 200→420→800→300 px; FormularGitter 200/320/700 px ohne Überlappung;
  Dialog-Knopfzeile; Schriftart-Effekte in der Seitenleiste (300/444 px) in Spalten; Regression „Dehnung ausgeblendeter Elemente“. **16/16 grün.**
* Bestehende, betroffene Tests: `test_baukasten`, `test_fenster_seitenleiste`, `test_fenster_seitenleiste_weitere`, `test_objektformat_panel`,
  `test_optionen`, `test_dashboard_architektur`, `test_backstage`: alle grün bis auf Fälle, die **schon vor der Umstellung** rot waren
  (siehe unten). `test_direkte_layouts_wachsen_nicht` war vorher rot und ist jetzt grün.
* Hauptfenster 1920×1040 nachgestellt: Arbeitsbereich füllt bis zur Statusleiste, Datei-Ansicht beginnt oben.
* Importtest aller 608 Module: 605 laden; 3 Fehler bestanden schon vorher (siehe unten).

## Ausnahmen (technisch begründet)
* `raster.py` benutzt die Richtungskonstanten von `QBoxLayout` (`TopToBottom` …), damit `direction()`/`setDirection()` die gewohnten Werte
  liefern/annehmen. Es wird kein Box-Layout erzeugt.
* Von Qt intern verwaltete Layouts (`QTabWidget`, `QScrollArea`, `QStackedWidget`, `QMenu`, `QListView` usw.) bleiben Qt-intern.
* Widget-Geometrie außerhalb von Layouts (Schwebeleisten, Popups, Lineale, Dokumentfläche) ist Zeichen-/Platzierungslogik, kein Layout.

## Stand 2026-11-24 (Abschluss)
Keine offenen Punkte.
* **Werkzeuge umgestellt:** Kompatibilitätsprüfer (11 Dateien, dazu sein eigenes `FlussLayout` und die `Kachelzeile`) und Symbolzeichner nutzen
  dasselbe Raster (`RasterSpalte`/`RasterZeile`, `FormularGitter`, `FlussLayout`, `KartenRaster`). Die Architekturprüfung deckt `werkzeuge/` mit ab.
* **Alle sieben vorher roten Tests behoben:** Auswahlfeld-Popup im Bildschirm (`popup_klemmen` kürzt zu hohe Popups), Seriendruck-Hinweis bricht um,
  Objektformat-Panel passt in 300 px (Abschnittstitel bricht um), Bandgruppen-Starter mit Lucide-Symbol statt Stylesheet; drei Tests an bewusste
  Änderungen angepasst (Bildcache-Schlüssel mit Pixeldichte, Datei-Ansicht baut Seiten erst beim Zeigen).
* **Formen einfügen repariert:** drei Zeichenbereich-Funktionen fehlten seit der Kern-Umstellung; neu auf der Objekt-Schnittstelle, mit Test.
* **Knöpfe neben Objekten und Tabellengriffe:** Lucide-Symbole statt Schriftzeichen.
* **Weitere Rasterkorrekturen:** Diagramm-Popups (Größe nach Reiterwechsel), Kachelfeld (Kacheln füllen ihre Zelle), Chips (Spanne nach Inhalt),
  einheitlicher Abstand unter Reiterleisten, `FormularGitter` meldet Breite/Mindesthöhe passend zur Spaltenregel.
* **Gezielte Abschlussprüfung:** alle ehemals roten Tests, Raster-Architektur, Formen: 363/363 grün.
* Hinweis (vorbestehend, keine Folge der Umstellung): Der Prüfer braucht mindestens 845 px Fensterbreite (vorher 893 px); schmaler erscheint ein
  waagerechter Rollbalken.
