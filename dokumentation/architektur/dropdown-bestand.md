# Dropdown-Bestand

Erzeugt mit `werkzeuge/pruefungen/dropdown_bestand.py` (nicht von Hand ändern). Alle Dropdown-Bausteine liegen im Paket `oberflaeche/baukasten/dropdown/`; Regeln und Pyramide stehen in `dokumentation/entwicklung/baukasten.md`.

## Klassen (Baustein → Basis → Datei)

| Klasse | Basis | Datei |
|---|---|---|
| `_ReiterLeiste` | UeberlaufLeiste | `oberflaeche/band/band_bausteine.py` |
| `SymbolKnopf` | DropdownKnopf | `oberflaeche/baukasten/chat/chat_blase.py` |
| `FarbPalette` | MenueListe | `oberflaeche/baukasten/dropdown/auswahl/farbpalette.py` |
| `RahmenMenue` | MenueListe | `oberflaeche/baukasten/dropdown/auswahl/rahmen_menue.py` |
| `RasterAuswahl` | MenueListe | `oberflaeche/baukasten/dropdown/auswahl/raster_auswahl.py` |
| `SymbolWahl` | DropdownTaste | `oberflaeche/baukasten/dropdown/auswahl/symbol_auswahl.py` |
| `ZellenRaster` | MenueListe | `oberflaeche/baukasten/dropdown/auswahl/zellen_raster.py` |
| `Auswahlfeld` | QComboBox, _Feldlaenge | `oberflaeche/baukasten/dropdown/auswahlfeld.py` |
| `Schriftauswahl` | QFontComboBox, _Feldlaenge | `oberflaeche/baukasten/dropdown/auswahlfeld.py` |
| `DropdownKnopf` | QToolButton, _DropdownBasis | `oberflaeche/baukasten/dropdown/dropdown_knopf.py` |
| `DropdownTaste` | QPushButton, _DropdownBasis | `oberflaeche/baukasten/dropdown/dropdown_knopf.py` |
| `GalerieAuswahl` | MenueListe | `oberflaeche/baukasten/dropdown/galerie_auswahl.py` |
| `MenueListe` | PopupVerhalten, QMenu | `oberflaeche/baukasten/dropdown/menue_liste.py` |
| `MenueTafel` | PopupVerhalten, QFrame | `oberflaeche/baukasten/dropdown/menue_tafel.py` |
| `DiagrammPopup` | MenueListe | `oberflaeche/baukasten/dropdown/objektmenues/diagramm_popups.py` |
| `LayoutOptionen` | PopupVerhalten, QFrame | `oberflaeche/baukasten/dropdown/objektmenues/layout_optionen.py` |
| `_Auffrischend` | MenueListe | `oberflaeche/baukasten/dropdown/objektmenues/smartart_menues.py` |
| `PopupVerhalten` |  | `oberflaeche/baukasten/dropdown/popup_lage.py` |
| `VoreinstellungMenue` | MenueListe | `oberflaeche/baukasten/dropdown/voreinstellung_menue.py` |
| `FlacheReiterLeiste` | QTabBar, ReiterDropdown | `oberflaeche/baukasten/felder/flache_reiter_leiste.py` |
| `UeberlaufLeiste` | QTabBar, ReiterUeberlauf | `oberflaeche/baukasten/felder/flache_reiter_leiste.py` |
| `VorschauCombo` | Auswahlfeld | `oberflaeche/bauteile/live_vorschau.py` |
| `VorschauFontCombo` | Schriftauswahl | `oberflaeche/bauteile/live_vorschau.py` |
| `_EinfuegenPanel` | MenueListe | `oberflaeche/dokument/kopffuss/kopffuss_felder.py` |

## Verwendung von `MenueListe(…` außerhalb des Pakets (96 Stellen in 42 Dateien)

- `kern/befehle/hauptreiter/bearbeiten.py`: 3
- `kern/befehle/hauptreiter/datei.py`: 1
- `kern/befehle/hauptreiter/einfuegen.py`: 6
- `kern/befehle/hauptreiter/einfuegen_objekte.py`: 5
- `kern/befehle/hauptreiter/ki.py`: 3
- `kern/befehle/hauptreiter/seite.py`: 4
- `kern/befehle/hauptreiter/serien.py`: 1
- `kern/befehle/hauptreiter/text_absatz.py`: 1
- `kern/befehle/hauptreiter/text_zeichen.py`: 6
- `kern/befehle/hauptreiter/ueberpruefen.py`: 7
- `kern/befehle/hauptreiter/verweise.py`: 1
- `kern/befehle/kontextreiter/bildtools.py`: 1
- `kern/befehle/kontextreiter/diagrammtools.py`: 4
- `kern/befehle/kontextreiter/formtools.py`: 1
- `kern/befehle/kontextreiter/kontext.py`: 1
- `kern/befehle/kontextreiter/kopffuss.py`: 4
- `kern/befehle/kontextreiter/tabellen.py`: 1
- `kern/befehle/kontextreiter/tabellen_format.py`: 3
- `kern/befehle/kontextreiter/texttools.py`: 6
- `kern/befehle/kontextreiter/zeichentools.py`: 3
- `oberflaeche/band/band_knoepfe.py`: 1
- `oberflaeche/band/band_stile.py`: 1
- `oberflaeche/baukasten/chat/chat_blase.py`: 1
- `oberflaeche/baukasten/chat/chat_eingabe.py`: 2
- `oberflaeche/baukasten/dokument/eingabe_fenster.py`: 1
- `oberflaeche/baukasten/felder/flache_reiter_leiste.py`: 2
- `oberflaeche/baukasten/formatierung/formatvorlage_dialog.py`: 1
- `oberflaeche/baukasten/formatierung/objektformat_panel.py`: 1
- `oberflaeche/bauteile/kontextmenue.py`: 1
- `oberflaeche/bauteile/mini_leiste.py`: 3
- `oberflaeche/dialoge/optionen_seiten/befehle.py`: 1
- `oberflaeche/dokument/ansicht/absatz_symbol.py`: 1
- `oberflaeche/dokument/ansicht/blasen_flaeche.py`: 1
- `oberflaeche/dokument/bearbeitung/editor_einfuegen.py`: 1
- `oberflaeche/dokument/bearbeitung/freie_bilder_knoepfe.py`: 1
- `oberflaeche/dokument/dokumentfenster/navigation.py`: 3
- `oberflaeche/dokument/dokumentfenster/suchen_feld.py`: 4
- `oberflaeche/dokument/kopffuss/kopffuss_bearbeiter.py`: 4
- `oberflaeche/hauptfenster/dateien_reiter.py`: 1
- `oberflaeche/hauptfenster/fenster_verwaltung.py`: 1
- `oberflaeche/seitenleiste/panels/ki_panel.py`: 1
- `oberflaeche/seitenleiste/seitenleiste.py`: 1

## Verwendung von `Auswahlfeld(…` außerhalb des Pakets (127 Stellen in 50 Dateien)

- `kern/befehle/hauptreiter/ueberpruefen.py`: 1
- `oberflaeche/band/werkzeugleisten.py`: 3
- `oberflaeche/baukasten/basis/linien.py`: 2
- `oberflaeche/baukasten/chat/chat_eingabe.py`: 1
- `oberflaeche/baukasten/diagramme/diagramm_format_bausteine.py`: 1
- `oberflaeche/baukasten/dokument/druck_dialog.py`: 3
- `oberflaeche/baukasten/dokument/druckvorschau.py`: 1
- `oberflaeche/baukasten/dokument/layout_dialog.py`: 1
- `oberflaeche/baukasten/dokument/liste_dialog.py`: 6
- `oberflaeche/baukasten/dokument/pdf_export.py`: 1
- `oberflaeche/baukasten/dokument/sortieren_dialog.py`: 3
- `oberflaeche/baukasten/dokument/speichern_fenster.py`: 2
- `oberflaeche/baukasten/felder/farbwaehler.py`: 1
- `oberflaeche/baukasten/felder/mass_feld.py`: 1
- `oberflaeche/baukasten/formatierung/absatz_dialog.py`: 5
- `oberflaeche/baukasten/formatierung/formatvorlage_dialog.py`: 3
- `oberflaeche/baukasten/formatierung/objektformat_panel.py`: 2
- `oberflaeche/baukasten/formatierung/rahmen_schattierung.py`: 6
- `oberflaeche/baukasten/formatierung/ruby_dialog.py`: 1
- `oberflaeche/baukasten/formatierung/schriftart_dialog.py`: 6
- `oberflaeche/baukasten/formatierung/text_format.py`: 1
- `oberflaeche/baukasten/formatierung/text_fuellarten_mixin.py`: 2
- `oberflaeche/baukasten/formatierung/texteffekt_dialog.py`: 2
- `oberflaeche/baukasten/formatierung/textfeld_abschnitt.py`: 2
- `oberflaeche/baukasten/medien/bild_export.py`: 2
- `oberflaeche/baukasten/vorlagen/formatvorlagen_bereich.py`: 2
- `oberflaeche/bauteile/mini_leiste.py`: 2
- `oberflaeche/dialoge/dokument_dialoge.py`: 6
- `oberflaeche/dialoge/einfuegen/diagramm_fenster.py`: 1
- `oberflaeche/dialoge/einfuegen/einfuegen_dialoge.py`: 6
- `oberflaeche/dialoge/einfuegen/einfuegen_fenster.py`: 6
- `oberflaeche/dialoge/einfuegen/formular_dialog.py`: 1
- `oberflaeche/dialoge/einfuegen/sonderzeichen.py`: 2
- `oberflaeche/dialoge/einfuegen/wasserzeichen_fenster.py`: 6
- `oberflaeche/dialoge/ki/ki_aktions_dialoge.py`: 5
- `oberflaeche/dialoge/ki/ki_einstellungen_panels.py`: 1
- `oberflaeche/dialoge/ki/ki_modelle_dialoge.py`: 3
- `oberflaeche/dialoge/lesen_hilfe/lesehilfe_dialog.py`: 1
- `oberflaeche/dialoge/lesen_hilfe/silben_dialog.py`: 2
- `oberflaeche/dialoge/optionen_seiten/befehle.py`: 1
- `oberflaeche/dialoge/optionen_seiten/datei.py`: 1
- `oberflaeche/dialoge/optionen_seiten/gemeinsam.py`: 3
- `oberflaeche/dialoge/optionen_seiten/lunivo.py`: 3
- `oberflaeche/dialoge/sendungen/sendungen_dialoge.py`: 3
- `oberflaeche/dialoge/sendungen/serien_fenster.py`: 1
- `oberflaeche/dialoge/verweise/verweise_dialoge.py`: 1
- `oberflaeche/dialoge/verweise/verweise_fenster.py`: 7
- `oberflaeche/dokument/dokumentfenster/suchen_feld.py`: 2
- `oberflaeche/dokument/kopffuss/kopffuss_felder.py`: 1
- `oberflaeche/seitenleiste/seitenleiste.py`: 1

## Verwendung von `Schriftauswahl(…` außerhalb des Pakets (7 Stellen in 7 Dateien)

- `oberflaeche/band/band_gruppen.py`: 1
- `oberflaeche/band/werkzeugleisten.py`: 1
- `oberflaeche/baukasten/diagramme/diagramm_text_panel.py`: 1
- `oberflaeche/baukasten/formatierung/ruby_dialog.py`: 1
- `oberflaeche/baukasten/formatierung/schriftart_dialog.py`: 1
- `oberflaeche/baukasten/formatierung/text_format.py`: 1
- `oberflaeche/dialoge/einfuegen/wasserzeichen_fenster.py`: 1

## Verwendung von `DropdownKnopf(…` außerhalb des Pakets (12 Stellen in 11 Dateien)

- `kern/befehle/hauptreiter/ueberpruefen.py`: 1
- `oberflaeche/band/band_gruppen.py`: 1
- `oberflaeche/band/band_knoepfe.py`: 1
- `oberflaeche/band/werkzeugleisten.py`: 1
- `oberflaeche/baukasten/geruest/panel_rahmen.py`: 1
- `oberflaeche/bauteile/mini_leiste.py`: 2
- `oberflaeche/dokument/ansicht/absatz_symbol.py`: 1
- `oberflaeche/dokument/bearbeitung/editor_einfuegen.py`: 1
- `oberflaeche/dokument/kopffuss/kopffuss_bearbeiter.py`: 1
- `oberflaeche/dokument/kopffuss/kopffuss_felder.py`: 1
- `oberflaeche/seitenleiste/seitenleiste.py`: 1

## Verwendung von `DropdownTaste(…` außerhalb des Pakets (4 Stellen in 4 Dateien)

- `oberflaeche/baukasten/felder/flache_reiter_leiste.py`: 1
- `oberflaeche/baukasten/formatierung/formatvorlage_dialog.py`: 1
- `oberflaeche/dialoge/optionen_seiten/befehle.py`: 1
- `oberflaeche/dokument/dokumentfenster/suchen_feld.py`: 1

## Verwendung von `menue_setzen(…` außerhalb des Pakets (25 Stellen in 19 Dateien)

- `kern/befehle/hauptreiter/ueberpruefen.py`: 1
- `oberflaeche/band/band_gruppen.py`: 1
- `oberflaeche/band/band_knoepfe.py`: 1
- `oberflaeche/band/werkzeugleisten.py`: 1
- `oberflaeche/baukasten/chat/chat_blase.py`: 1
- `oberflaeche/baukasten/chat/chat_eingabe.py`: 2
- `oberflaeche/baukasten/dropdown/auswahl/symbol_auswahl.py`: 1
- `oberflaeche/baukasten/dropdown/dropdown_knopf.py`: 1
- `oberflaeche/baukasten/felder/flache_reiter_leiste.py`: 1
- `oberflaeche/baukasten/formatierung/formatvorlage_dialog.py`: 1
- `oberflaeche/baukasten/geruest/panel_rahmen.py`: 1
- `oberflaeche/bauteile/mini_leiste.py`: 2
- `oberflaeche/dialoge/optionen_seiten/befehle.py`: 1
- `oberflaeche/dokument/ansicht/absatz_symbol.py`: 1
- `oberflaeche/dokument/bearbeitung/editor_einfuegen.py`: 1
- `oberflaeche/dokument/dokumentfenster/suchen_feld.py`: 1
- `oberflaeche/dokument/kopffuss/kopffuss_bearbeiter.py`: 5
- `oberflaeche/seitenleiste/panels/ki_panel.py`: 1
- `oberflaeche/seitenleiste/seitenleiste.py`: 1
