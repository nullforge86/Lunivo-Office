# Dropdown-Architektur: Übersicht und Maßnahmen

Stand: 2026-11-06. Grundlage ist die Verfolgung der Aufrufketten im Code, nicht nur Suchtreffer. Die Stellenzahlen stehen in `docs/dropdown-bestand.md` (erzeugt mit `werkzeug/dropdown-bestand.py`).

## 1. Die vier Stufen (jede baut auf der darunter auf)

| Stufe | Quelle | Datei |
|---|---|---|
| 1 Öffnungsverhalten (Lage in Fenster und Bildschirm) | `PopupVerhalten`, `popup_klemmen` | `ui/baukasten/dropdown/popup_lage.py` |
| 2 Maße (Zeilenhöhe, Feldhöhe, Breiten, Kacheln) | Konstanten `DROPDOWN_*`, `PADDING_MENUE*` | `ui/baukasten/mass.py` |
| 3 Aussehen (Farbe, Rand, Radius, Pfeil, Auswahl, Zeilen, Kacheln, Popup-Rahmen) | Themenregeln, Eigenschaften `variante`, `dropdownZeile`, `dropdownKachel`, `dropdownFenster`, `dropdownTitel`, `dropdownKopf`, `dropdownLink` | `ui/theme.py` |
| 4 Bausteine | siehe Abschnitt 2 | `ui/baukasten/dropdown/` |

## 2. Komponenten, Basis, Quelle von Design und Konfiguration

| Baustein | Basis | Design aus | Maße aus |
|---|---|---|---|
| `MenueListe` (und alle Menüs, Untermenüs, Kontextmenüs) | `PopupVerhalten`, `QMenu` | Thema `QMenu…` | `PADDING_MENUE_GLOBAL`, `PADDING_MENUEEINTRAG_GLOBAL` |
| `MenueListe.kompakt()` | wie oben, Eigenschaft `variante="kompakt"` | Thema `QMenu[variante="kompakt"]` | `PADDING_MENUE_KOMPAKT`, `PADDING_MENUEEINTRAG_KOMPAKT` |
| `RasterAuswahl`, `GalerieAuswahl`, `FarbPalette`, `ZellenRaster`, `VoreinstellungMenue`, `RahmenMenue`, `DiagrammPopup`, `_Auffrischend` (SmartArt) | `MenueListe` | Thema (Zeilen: `dropdownZeile`, Kacheln: `dropdownKachel`) | `mass.py` |
| `MenueTafel`, `LayoutOptionen` | `PopupVerhalten`, `QFrame` | Thema `QFrame[dropdownFenster]` | `mass.py` |
| `Auswahlfeld`, `Schriftauswahl` (und `VorschauCombo`, `VorschauFontCombo` im Band) | `QComboBox`, `QFontComboBox` | Thema `QComboBox…` | `DROPDOWN_HOEHE`, Feldlänge per Rolle |
| `DropdownKnopf`, `DropdownTaste` | `QToolButton`, `QPushButton` | Thema `QToolButton::menu-*` | `DROPDOWN_HOEHE`, `DROPDOWN_PFEIL_ZONE` |
| `KopfDropdown` | `QToolButton` | eigenes Zeichnen mit `HOEHE_KOPFDROPDOWN` | `mass.py` |
| Überlaufmenü „•••“ (`FlacheReiterLeiste`, `_ReiterLeiste`) | `MenueListe` | Thema | `mass.py` |

Aufrufstellen: 91 × `MenueListe(`, 122 × `Auswahlfeld(`, 7 × `Schriftauswahl(`, 12 × `DropdownKnopf(`, 3 × `DropdownTaste(` außerhalb des Pakets (Band, Seitenleiste, Mini-Leiste, Dokument, Dialoge, Befehle). Außerhalb des Pakets entsteht kein rohes `QMenu`, `QComboBox` oder `addMenu("Text")`; die Wächtertests in `tests/test_main_window.py` und `tests/test_popup_lage.py` sichern das.

## 3. Abweichungen und Stand

| Abweichung | Stand |
|---|---|
| Lokale Stylesheets im Paket (Zeilentasten, Kacheln, Popup-Rahmen, Titel, Links, `kompakt()`) | behoben, Themenregeln mit Eigenschaften; Wächter: kein `setStyleSheet` im Paket |
| Eigener Menü-Pfeil und Menü-Knopf der Mini-Leiste | behoben, Rahmen und Knopfabstand im Thema |
| Doppeltes `menu-indicator` in Seitenleiste, Kopf-/Fußzeile, Absatz-Symbol | behoben |
| Feste Zahlen für Kacheln, Raster, Farbfelder im Paket | behoben, in `mass.py` |
| Zwei Menü-Paddings ohne Erklärung (`PADDING_MENUE` / `_GLOBAL`) | geklärt: Standard und Variante „kompakt“, umbenannt |
| Liste des Auswahlfelds ohne Ecken- und Eintragsradius wie `QMenu` | behoben im Thema; Innenabstand bewusst offen (Listenhöhe in `popup_begrenzen` ist fest gerechnet) |
| Dokument-Leisten (Kopf-/Fußzeile, Tabellengriffe, Absatz-Symbol) mit eigenen Stylesheets | behoben: Eigenschaft `papierKnopf` und Regel `#kfLeiste QToolButton` im Thema (Papierfarben als Tokens) |
| Zeichenmaße in Zeichenroutinen (`galerie_auswahl.py`, Vorschaubild der Diagramme) | bewusst offen: keine Gestaltungsregeln, sondern Geometrie |
| Unterschiedliches Aussehen der Auswahlfelder (Bildschirmfotos) | im aktuellen Stand gemessen: alle `Auswahlfeld` im Fenster haben Höhe 36 und gleiche Pixel (dunkel, Mint). Wächter `test_auswahlfelder_sehen_ueberall_gleich_aus` prüft das in drei Themen und drei Zusammenhängen. Die Fotos stammen vermutlich von einem älteren Stand. |

## 4. Offen

- Innenabstand der Auswahlfeld-Liste (hängt an der Listenhöhenrechnung in `popup_begrenzen`).
- Zeichenmaße in Zeichenroutinen (Geometrie, keine Gestaltungsregeln).
