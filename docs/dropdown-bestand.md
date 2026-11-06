# Dropdown-Bestand

Erzeugt mit `werkzeug/dropdown-bestand.py` (nicht von Hand ändern). Alle Dropdown-Bausteine liegen im Paket `ui/baukasten/dropdown/`; Regeln und Pyramide stehen in `docs/baukasten.md`.

## Klassen (Baustein → Basis → Datei)

| Klasse | Basis | Datei |
|---|---|---|
| `Auswahlfeld` | QComboBox, _Feldlaenge | `ui/baukasten/dropdown/auswahlfeld.py` |
| `Schriftauswahl` | QFontComboBox, _Feldlaenge | `ui/baukasten/dropdown/auswahlfeld.py` |
| `DiagrammPopup` | MenueListe | `ui/baukasten/dropdown/diagramm_popups.py` |
| `DropdownKnopf` | QToolButton, _DropdownBasis | `ui/baukasten/dropdown/dropdown_knopf.py` |
| `DropdownTaste` | QPushButton, _DropdownBasis | `ui/baukasten/dropdown/dropdown_knopf.py` |
| `FarbPalette` | MenueListe | `ui/baukasten/dropdown/farbpalette.py` |
| `GalerieAuswahl` | MenueListe | `ui/baukasten/dropdown/galerie_auswahl.py` |
| `LayoutOptionen` | PopupVerhalten, QFrame | `ui/baukasten/dropdown/layout_optionen.py` |
| `MenueListe` | PopupVerhalten, QMenu | `ui/baukasten/dropdown/menue_liste.py` |
| `MenueTafel` | PopupVerhalten, QFrame | `ui/baukasten/dropdown/menue_tafel.py` |
| `PopupVerhalten` |  | `ui/baukasten/dropdown/popup_lage.py` |
| `RahmenMenue` | MenueListe | `ui/baukasten/dropdown/rahmen_menue.py` |
| `RasterAuswahl` | MenueListe | `ui/baukasten/dropdown/raster_auswahl.py` |
| `_Auffrischend` | MenueListe | `ui/baukasten/dropdown/smartart_menues.py` |
| `VoreinstellungMenue` | MenueListe | `ui/baukasten/dropdown/voreinstellung_menue.py` |
| `ZellenRaster` | MenueListe | `ui/baukasten/dropdown/zellen_raster.py` |
| `FlacheReiterLeiste` | QTabBar, ReiterUeberlauf | `ui/baukasten/flache_reiter_leiste.py` |
| `UeberlaufLeiste` | QTabBar, ReiterUeberlauf | `ui/baukasten/flache_reiter_leiste.py` |
| `_EinfuegenPanel` | MenueListe | `ui/document/kopffuss_bearbeiter.py` |
| `_ReiterLeiste` | UeberlaufLeiste | `ui/ribbon/ribbon_bar.py` |

## Verwendung von `MenueListe(…` außerhalb des Pakets (91 Stellen in 31 Dateien)

- `core/befehle/bearbeiten.py`: 3
- `core/befehle/datei.py`: 1
- `core/befehle/diagrammtools.py`: 4
- `core/befehle/einfuegen.py`: 11
- `core/befehle/ki.py`: 3
- `core/befehle/kontext.py`: 10
- `core/befehle/kopffuss.py`: 4
- `core/befehle/seite.py`: 4
- `core/befehle/serien.py`: 1
- `core/befehle/text.py`: 7
- `core/befehle/texttools.py`: 6
- `core/befehle/ueberpruefen.py`: 7
- `core/befehle/verweise.py`: 1
- `editor/formular.py`: 1
- `ui/baukasten/flache_reiter_leiste.py`: 1
- `ui/baukasten/formatvorlage_dialog.py`: 1
- `ui/baukasten/objektformat_panel.py`: 1
- `ui/dialogs/optionen_seiten/befehle.py`: 1
- `ui/document/absatz_symbol.py`: 1
- `ui/document/blasen_flaeche.py`: 1
- `ui/document/document_editor.py`: 1
- `ui/document/freie_bilder_bedienung.py`: 1
- `ui/document/kopffuss_bearbeiter.py`: 4
- `ui/document/navigation.py`: 3
- `ui/document/suchen_feld.py`: 4
- `ui/hauptfenster/dateien.py`: 1
- `ui/main_window.py`: 1
- `ui/ribbon/ribbon_bar.py`: 2
- `ui/sidebar/sidebar.py`: 1
- `ui/widgets/kontextmenue.py`: 1
- `ui/widgets/mini_leiste.py`: 3

## Verwendung von `Auswahlfeld(…` außerhalb des Pakets (122 Stellen in 47 Dateien)

- `core/befehle/ueberpruefen.py`: 1
- `ui/baukasten/absatz_dialog.py`: 5
- `ui/baukasten/bild_export.py`: 2
- `ui/baukasten/diagramm_format_panel.py`: 1
- `ui/baukasten/druck_dialog.py`: 3
- `ui/baukasten/druckvorschau.py`: 1
- `ui/baukasten/farbwaehler.py`: 1
- `ui/baukasten/formatvorlage_dialog.py`: 3
- `ui/baukasten/formatvorlagen_bereich.py`: 2
- `ui/baukasten/layout_dialog.py`: 1
- `ui/baukasten/linien.py`: 2
- `ui/baukasten/liste_dialog.py`: 6
- `ui/baukasten/mass_feld.py`: 1
- `ui/baukasten/objektformat_panel.py`: 2
- `ui/baukasten/pdf_export.py`: 1
- `ui/baukasten/rahmen_schattierung.py`: 6
- `ui/baukasten/ruby_dialog.py`: 1
- `ui/baukasten/schriftart_dialog.py`: 6
- `ui/baukasten/sortieren_dialog.py`: 3
- `ui/baukasten/speichern_fenster.py`: 2
- `ui/baukasten/text_format.py`: 1
- `ui/baukasten/text_fuellarten_mixin.py`: 2
- `ui/baukasten/texteffekt_dialog.py`: 2
- `ui/baukasten/textfeld_abschnitt.py`: 2
- `ui/dialogs/diagramm_fenster.py`: 1
- `ui/dialogs/dokument_dialoge.py`: 6
- `ui/dialogs/einfuegen_dialoge.py`: 6
- `ui/dialogs/einfuegen_fenster.py`: 6
- `ui/dialogs/formular_dialog.py`: 1
- `ui/dialogs/ki_dialoge.py`: 5
- `ui/dialogs/lesehilfe_dialog.py`: 1
- `ui/dialogs/optionen_seiten/befehle.py`: 1
- `ui/dialogs/optionen_seiten/datei.py`: 1
- `ui/dialogs/optionen_seiten/gemeinsam.py`: 3
- `ui/dialogs/optionen_seiten/lunivo.py`: 3
- `ui/dialogs/sendungen_dialoge.py`: 3
- `ui/dialogs/serien_fenster.py`: 1
- `ui/dialogs/silben_dialog.py`: 2
- `ui/dialogs/sonderzeichen.py`: 2
- `ui/dialogs/verweise_dialoge.py`: 1
- `ui/dialogs/verweise_fenster.py`: 7
- `ui/dialogs/wasserzeichen_fenster.py`: 6
- `ui/document/kopffuss_bearbeiter.py`: 1
- `ui/document/suchen_feld.py`: 2
- `ui/ribbon/toolbars.py`: 3
- `ui/sidebar/sidebar.py`: 1
- `ui/widgets/mini_leiste.py`: 2

## Verwendung von `Schriftauswahl(…` außerhalb des Pakets (7 Stellen in 7 Dateien)

- `ui/baukasten/diagramm_format_panel.py`: 1
- `ui/baukasten/ruby_dialog.py`: 1
- `ui/baukasten/schriftart_dialog.py`: 1
- `ui/baukasten/text_format.py`: 1
- `ui/dialogs/wasserzeichen_fenster.py`: 1
- `ui/ribbon/ribbon_bar.py`: 1
- `ui/ribbon/toolbars.py`: 1

## Verwendung von `DropdownKnopf(…` außerhalb des Pakets (12 Stellen in 9 Dateien)

- `core/befehle/ueberpruefen.py`: 1
- `ui/baukasten/panel_rahmen.py`: 1
- `ui/document/absatz_symbol.py`: 1
- `ui/document/document_editor.py`: 1
- `ui/document/kopffuss_bearbeiter.py`: 2
- `ui/ribbon/ribbon_bar.py`: 2
- `ui/ribbon/toolbars.py`: 1
- `ui/sidebar/sidebar.py`: 1
- `ui/widgets/mini_leiste.py`: 2

## Verwendung von `DropdownTaste(…` außerhalb des Pakets (3 Stellen in 3 Dateien)

- `ui/baukasten/formatvorlage_dialog.py`: 1
- `ui/dialogs/optionen_seiten/befehle.py`: 1
- `ui/document/suchen_feld.py`: 1

## Verwendung von `menue_setzen(…` außerhalb des Pakets (19 Stellen in 13 Dateien)

- `core/befehle/ueberpruefen.py`: 1
- `ui/baukasten/dropdown/dropdown_knopf.py`: 1
- `ui/baukasten/formatvorlage_dialog.py`: 1
- `ui/baukasten/panel_rahmen.py`: 1
- `ui/dialogs/optionen_seiten/befehle.py`: 1
- `ui/document/absatz_symbol.py`: 1
- `ui/document/document_editor.py`: 1
- `ui/document/kopffuss_bearbeiter.py`: 5
- `ui/document/suchen_feld.py`: 1
- `ui/ribbon/ribbon_bar.py`: 2
- `ui/ribbon/toolbars.py`: 1
- `ui/sidebar/sidebar.py`: 1
- `ui/widgets/mini_leiste.py`: 2
