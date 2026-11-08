# Dropdown-Bestand

Erzeugt mit `werkzeug/pruefen/dropdown-bestand.py` (nicht von Hand ändern). Alle Dropdown-Bausteine liegen im Paket `ui/baukasten/dropdown/`; Regeln und Pyramide stehen in `docs/baukasten.md`.

## Klassen (Baustein → Basis → Datei)

| Klasse | Basis | Datei |
|---|---|---|
| `SymbolKnopf` | DropdownKnopf | `ui/baukasten/chat/chat_blase.py` |
| `FlacheReiterLeiste` | QTabBar, ReiterDropdown | `ui/baukasten/controls/flache_reiter_leiste.py` |
| `UeberlaufLeiste` | QTabBar, ReiterUeberlauf | `ui/baukasten/controls/flache_reiter_leiste.py` |
| `FarbPalette` | MenueListe | `ui/baukasten/dropdown/auswahl/farbpalette.py` |
| `RahmenMenue` | MenueListe | `ui/baukasten/dropdown/auswahl/rahmen_menue.py` |
| `RasterAuswahl` | MenueListe | `ui/baukasten/dropdown/auswahl/raster_auswahl.py` |
| `SymbolWahl` | DropdownTaste | `ui/baukasten/dropdown/auswahl/symbol_auswahl.py` |
| `ZellenRaster` | MenueListe | `ui/baukasten/dropdown/auswahl/zellen_raster.py` |
| `Auswahlfeld` | QComboBox, _Feldlaenge | `ui/baukasten/dropdown/auswahlfeld.py` |
| `Schriftauswahl` | QFontComboBox, _Feldlaenge | `ui/baukasten/dropdown/auswahlfeld.py` |
| `DropdownKnopf` | QToolButton, _DropdownBasis | `ui/baukasten/dropdown/dropdown_knopf.py` |
| `DropdownTaste` | QPushButton, _DropdownBasis | `ui/baukasten/dropdown/dropdown_knopf.py` |
| `GalerieAuswahl` | MenueListe | `ui/baukasten/dropdown/galerie_auswahl.py` |
| `MenueListe` | PopupVerhalten, QMenu | `ui/baukasten/dropdown/menue_liste.py` |
| `MenueTafel` | PopupVerhalten, QFrame | `ui/baukasten/dropdown/menue_tafel.py` |
| `DiagrammPopup` | MenueListe | `ui/baukasten/dropdown/objektmenues/diagramm_popups.py` |
| `LayoutOptionen` | PopupVerhalten, QFrame | `ui/baukasten/dropdown/objektmenues/layout_optionen.py` |
| `_Auffrischend` | MenueListe | `ui/baukasten/dropdown/objektmenues/smartart_menues.py` |
| `PopupVerhalten` |  | `ui/baukasten/dropdown/popup_lage.py` |
| `VoreinstellungMenue` | MenueListe | `ui/baukasten/dropdown/voreinstellung_menue.py` |
| `_EinfuegenPanel` | MenueListe | `ui/document/kopffuss/kopffuss_felder.py` |
| `_ReiterLeiste` | UeberlaufLeiste | `ui/ribbon/ribbon_bausteine.py` |
| `VorschauCombo` | Auswahlfeld | `ui/widgets/live_vorschau.py` |
| `VorschauFontCombo` | Schriftauswahl | `ui/widgets/live_vorschau.py` |

## Verwendung von `MenueListe(…` außerhalb des Pakets (96 Stellen in 37 Dateien)

- `core/befehle/hauptreiter/bearbeiten.py`: 3
- `core/befehle/hauptreiter/datei.py`: 1
- `core/befehle/hauptreiter/einfuegen.py`: 6
- `core/befehle/hauptreiter/einfuegen_objekte.py`: 5
- `core/befehle/hauptreiter/ki.py`: 3
- `core/befehle/hauptreiter/seite.py`: 4
- `core/befehle/hauptreiter/serien.py`: 1
- `core/befehle/hauptreiter/text_absatz.py`: 1
- `core/befehle/hauptreiter/text_zeichen.py`: 6
- `core/befehle/hauptreiter/ueberpruefen.py`: 7
- `core/befehle/hauptreiter/verweise.py`: 1
- `core/befehle/kontextreiter/diagrammtools.py`: 4
- `core/befehle/kontextreiter/kontext.py`: 10
- `core/befehle/kontextreiter/kopffuss.py`: 4
- `core/befehle/kontextreiter/texttools.py`: 6
- `ui/baukasten/chat/chat_blase.py`: 1
- `ui/baukasten/chat/chat_eingabe.py`: 2
- `ui/baukasten/controls/flache_reiter_leiste.py`: 2
- `ui/baukasten/dokument/eingabe_fenster.py`: 1
- `ui/baukasten/formatierung/formatvorlage_dialog.py`: 1
- `ui/baukasten/formatierung/objektformat_panel.py`: 1
- `ui/dialogs/optionen_seiten/befehle.py`: 1
- `ui/document/ansicht/absatz_symbol.py`: 1
- `ui/document/ansicht/blasen_flaeche.py`: 1
- `ui/document/bearbeitung/editor_einfuegen.py`: 1
- `ui/document/bearbeitung/freie_bilder_bedienung.py`: 1
- `ui/document/dokumentfenster/navigation.py`: 3
- `ui/document/dokumentfenster/suchen_feld.py`: 4
- `ui/document/kopffuss/kopffuss_bearbeiter.py`: 4
- `ui/hauptfenster/dateien_reiter.py`: 1
- `ui/main_window.py`: 1
- `ui/ribbon/ribbon_knoepfe.py`: 1
- `ui/ribbon/ribbon_stile.py`: 1
- `ui/sidebar/panels/ai_panel.py`: 1
- `ui/sidebar/sidebar.py`: 1
- `ui/widgets/kontextmenue.py`: 1
- `ui/widgets/mini_leiste.py`: 3

## Verwendung von `Auswahlfeld(…` außerhalb des Pakets (127 Stellen in 49 Dateien)

- `core/befehle/hauptreiter/ueberpruefen.py`: 1
- `ui/baukasten/basis/linien.py`: 2
- `ui/baukasten/chat/chat_eingabe.py`: 1
- `ui/baukasten/controls/farbwaehler.py`: 1
- `ui/baukasten/controls/mass_feld.py`: 1
- `ui/baukasten/diagramme/diagramm_format_panel.py`: 1
- `ui/baukasten/dokument/druck_dialog.py`: 3
- `ui/baukasten/dokument/druckvorschau.py`: 1
- `ui/baukasten/dokument/layout_dialog.py`: 1
- `ui/baukasten/dokument/liste_dialog.py`: 6
- `ui/baukasten/dokument/pdf_export.py`: 1
- `ui/baukasten/dokument/sortieren_dialog.py`: 3
- `ui/baukasten/dokument/speichern_fenster.py`: 2
- `ui/baukasten/formatierung/absatz_dialog.py`: 5
- `ui/baukasten/formatierung/formatvorlage_dialog.py`: 3
- `ui/baukasten/formatierung/objektformat_panel.py`: 2
- `ui/baukasten/formatierung/rahmen_schattierung.py`: 6
- `ui/baukasten/formatierung/ruby_dialog.py`: 1
- `ui/baukasten/formatierung/schriftart_dialog.py`: 6
- `ui/baukasten/formatierung/text_format.py`: 1
- `ui/baukasten/formatierung/text_fuellarten_mixin.py`: 2
- `ui/baukasten/formatierung/texteffekt_dialog.py`: 2
- `ui/baukasten/formatierung/textfeld_abschnitt.py`: 2
- `ui/baukasten/medien/bild_export.py`: 2
- `ui/baukasten/vorlagen/formatvorlagen_bereich.py`: 2
- `ui/dialogs/dokument_dialoge.py`: 6
- `ui/dialogs/einfuegen/diagramm_fenster.py`: 1
- `ui/dialogs/einfuegen/einfuegen_dialoge.py`: 6
- `ui/dialogs/einfuegen/einfuegen_fenster.py`: 6
- `ui/dialogs/einfuegen/formular_dialog.py`: 1
- `ui/dialogs/einfuegen/sonderzeichen.py`: 2
- `ui/dialogs/einfuegen/wasserzeichen_fenster.py`: 6
- `ui/dialogs/ki/ki_dialoge.py`: 6
- `ui/dialogs/ki/ki_modelle_dialoge.py`: 3
- `ui/dialogs/lesen_hilfe/lesehilfe_dialog.py`: 1
- `ui/dialogs/lesen_hilfe/silben_dialog.py`: 2
- `ui/dialogs/optionen_seiten/befehle.py`: 1
- `ui/dialogs/optionen_seiten/datei.py`: 1
- `ui/dialogs/optionen_seiten/gemeinsam.py`: 3
- `ui/dialogs/optionen_seiten/lunivo.py`: 3
- `ui/dialogs/sendungen/sendungen_dialoge.py`: 3
- `ui/dialogs/sendungen/serien_fenster.py`: 1
- `ui/dialogs/verweise/verweise_dialoge.py`: 1
- `ui/dialogs/verweise/verweise_fenster.py`: 7
- `ui/document/dokumentfenster/suchen_feld.py`: 2
- `ui/document/kopffuss/kopffuss_felder.py`: 1
- `ui/ribbon/toolbars.py`: 3
- `ui/sidebar/sidebar.py`: 1
- `ui/widgets/mini_leiste.py`: 2

## Verwendung von `Schriftauswahl(…` außerhalb des Pakets (7 Stellen in 7 Dateien)

- `ui/baukasten/diagramme/diagramm_format_panel.py`: 1
- `ui/baukasten/formatierung/ruby_dialog.py`: 1
- `ui/baukasten/formatierung/schriftart_dialog.py`: 1
- `ui/baukasten/formatierung/text_format.py`: 1
- `ui/dialogs/einfuegen/wasserzeichen_fenster.py`: 1
- `ui/ribbon/ribbon_gruppen.py`: 1
- `ui/ribbon/toolbars.py`: 1

## Verwendung von `DropdownKnopf(…` außerhalb des Pakets (12 Stellen in 11 Dateien)

- `core/befehle/hauptreiter/ueberpruefen.py`: 1
- `ui/baukasten/geruest/panel_rahmen.py`: 1
- `ui/document/ansicht/absatz_symbol.py`: 1
- `ui/document/bearbeitung/editor_einfuegen.py`: 1
- `ui/document/kopffuss/kopffuss_bearbeiter.py`: 1
- `ui/document/kopffuss/kopffuss_felder.py`: 1
- `ui/ribbon/ribbon_gruppen.py`: 1
- `ui/ribbon/ribbon_knoepfe.py`: 1
- `ui/ribbon/toolbars.py`: 1
- `ui/sidebar/sidebar.py`: 1
- `ui/widgets/mini_leiste.py`: 2

## Verwendung von `DropdownTaste(…` außerhalb des Pakets (4 Stellen in 4 Dateien)

- `ui/baukasten/controls/flache_reiter_leiste.py`: 1
- `ui/baukasten/formatierung/formatvorlage_dialog.py`: 1
- `ui/dialogs/optionen_seiten/befehle.py`: 1
- `ui/document/dokumentfenster/suchen_feld.py`: 1

## Verwendung von `menue_setzen(…` außerhalb des Pakets (25 Stellen in 19 Dateien)

- `core/befehle/hauptreiter/ueberpruefen.py`: 1
- `ui/baukasten/chat/chat_blase.py`: 1
- `ui/baukasten/chat/chat_eingabe.py`: 2
- `ui/baukasten/controls/flache_reiter_leiste.py`: 1
- `ui/baukasten/dropdown/auswahl/symbol_auswahl.py`: 1
- `ui/baukasten/dropdown/dropdown_knopf.py`: 1
- `ui/baukasten/formatierung/formatvorlage_dialog.py`: 1
- `ui/baukasten/geruest/panel_rahmen.py`: 1
- `ui/dialogs/optionen_seiten/befehle.py`: 1
- `ui/document/ansicht/absatz_symbol.py`: 1
- `ui/document/bearbeitung/editor_einfuegen.py`: 1
- `ui/document/dokumentfenster/suchen_feld.py`: 1
- `ui/document/kopffuss/kopffuss_bearbeiter.py`: 5
- `ui/ribbon/ribbon_gruppen.py`: 1
- `ui/ribbon/ribbon_knoepfe.py`: 1
- `ui/ribbon/toolbars.py`: 1
- `ui/sidebar/panels/ai_panel.py`: 1
- `ui/sidebar/sidebar.py`: 1
- `ui/widgets/mini_leiste.py`: 2
