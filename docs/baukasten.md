# Der Baukasten der Oberfläche

`src/lunivo_writer/ui/baukasten/` — Bausteine, die an vielen Stellen wiederkehren. **Ein Baustein, viele Aufrufer:**
Er kennt nur seinen eigenen Wert und meldet ihn (Signal oder Rückgabewert). Was damit geschieht — Schriftfarbe,
Schattierung, Seitenfarbe, Rahmen, Füllung —, entscheidet der Aufrufer.

| Datei | Baustein | Meldet |
|---|---|---|
| `farben.py` | Daten: 10 Themenfarben mit je 5 Abstufungen, 10 Standardfarben, „zuletzt benutzt“ (QSettings) | — |
| `farbpalette.py` | `FarbPalette` (Popup), `FarbFeld` (Knopf für Dialoge), `FarbKnopf` (geteilter Knopf fürs Band), `weitere_farben()` (Fenster „Farben“, siehe `farbwaehler.py`: Standard · Benutzerdefiniert · Erweitert, Farbmodell RGB/HSV/HSL, Hex, Neu/Aktuell) | `gewaehlt(QColor \| None)`, `ueberfahren`, `verlassen` |
| `linien.py` | `Linie` (Farbe, pt, Art), `LinienWahl` (Zeile aus Art, Stärke, Farbe), `RahmenMenue` (unten, oben, links, rechts, kein, alle, außen, innen) | `geaendert(Linie)`, `gewaehlt(RahmenSeiten, schluessel)` |
| `menue_liste.py` | `MenueListe`: der EINE Baustein für alle Menüs (außerhalb davon wird kein `QMenu(` erzeugt; Wächter: `grep -rn "QMenu(" src`). `eintrag` (Symbol, Haken, `aktiv=`, `kuerzel=` nur Anzeige oder `echt=True` = wirkliches Tastenkürzel), `untermenue(text, …, wert=, tip=)` (aktueller Wert rechts vor dem Pfeil, graue Zeile mit Hinweis), `trenner`, `schalter(text, an, aktion, symbol=)` (Zeile mit kleinem `KippSchalter` aus `schalter.py`, `SchalterZeile` in `dropdown/schalter_zeile.py`, `an_setzen` zieht den Zustand nach), `widget(w)` (eingebettetes Bedienfeld, z. B. Raster/Zuschneiden), `kompakt()` (Tabellenmenü-Stil), `standard(editor)` (Standard-Kontextmenü deutsch), `in_leiste(menueleiste, titel)`, `aus_liste`. Raster-, Farb-, Galerie-, Voreinstellungs-Menüs erben davon | `triggered` je Zeile |
| `raster_auswahl.py` | `RasterAuswahl`: Kacheln mit „Mehr …“-Fuß (Aufzählung, Vorlagen, Ränder, Deckblätter, Symbole); `abschnitt(titel)` beginnt ein zweites Raster, `bild_setzen` wechselt eine Kachel vor dem Aufklappen, `kopf(widget)` setzt eine Leiste über die Kacheln, `leeren(groesse)` + `neu_messen()` füllen neu (Deckblatt: Hoch-/Querformat), `textkachel(text)` zeichnet ein Zeichen als Kachel | `gewaehlt(schluessel)` |
| `bild_diagramm_menues.py` | `zuschneiden_menue(b)` (Klappe „Zuschneiden“: Reiter Nach Form / Nach Skala, Formen nach Gruppen, „Form und Größe zurücksetzen“), `diagramm_stile_galerie(b)` / `diagramm_stile_menue(b)` (vier Stilkacheln, mit QPainter gezeichnet); `KLAPPEN` / `GALERIEN` melden sie dem Band | der Aufruf der Befehle `bildZuschneiden…`, `diagrammStil` |
| `zellen_raster.py` | `ZellenRaster`: Zellen überfahren, „3 × 4 Tabelle“ lesen, klicken; mit `fuss()` weitere Einträge darunter | `gewaehlt(zeilen, spalten)` |
| `spalten.py` | `ZweiSpalter(links, rechts, breit_ab=760, links_breite=None, oben="links"|"rechts", breit_stretch, gestapelt_stretch, raender_breit, raender_gestapelt, abstand)`: der eine Baustein für alle zweispaltigen Seiten (links Navigation/Blatt/Liste, rechts Inhalt). Ab `breit_ab` nebeneinander, schmal untereinander (`oben` = welches Widget oben steht); `breit_ab=0` = nie umbrechen. Genutzt von Druck, Optionen, Datei öffnen/speichern, Handbuch, Datei-Ansicht | `angeordnet(breit)` |
| `listen_symbole.py` | `liste_zeichner()`: Vorschaubild einer Aufzählungs- oder Nummerierungsart für die Kachel-Auswahl | — |
| `mass_feld.py` | `MassSpin`: Zahl mit Maßeinheit (intern mm), `set_einheit()` | `valueChanged` |
| `auswahl_liste.py` | `AuswahlListe([(wert, text)])`: Liste mit Rahmen und hohen Zeilen, bedienbar wie eine Auswahl (`currentData`, `findData`, `setCurrentIndex` …); genutzt für Sprachen (KI-Einstellungen) und Stimmen | `currentData()` |
| `stimme_dialog.py` | `StimmeDialog`: „Stimme und Tempo“ — Stimme aus der `AuswahlListe` (füllt den freien Platz der Seitenleiste), Tempo mit `SchiebeFeld`. Kennt weder Einstellungen noch Sprachausgabe: Tempobereich und Schritt (`TEMPO_MIN/MAX/SCHRITT`) und die Schlüssel (`EINSTELLUNG_*`) kommen aus `services/vorlesen.py` über den Aufrufer | `stimme()`, `tempo()` |
| `dialog_rahmen.py` | `DialogRahmen`: Formular, optionale Vorschau, OK/Abbrechen, Zusatzknöpfe („Entfernen“) | `ergebnis()` |
| `speichern_fenster.py` | `SpeichernFenster` / `speicherort_waehlen()` / `Dateifenster` (gleiche Aufrufe wie `QFileDialog.get…`, das ein Test im Code verbietet): das eine Datei-Fenster — Orte links, Ordner mit Pfadleiste, Liste/Kacheln, unten Dateiname + Speichern, Dateityp + Abbrechen; fragt vor dem Ersetzen. Dasselbe Fenster öffnet (`datei_waehlen()`, Filter im Qt-Stil, auch mehrere Dateien) und wählt Ordner (`ordner_waehlen()`) | `(Pfad, Endung)` · Liste der Dateien · Ordner · `None` |
| `bild_export.py` | `BildExportFenster`: „Als Bild exportieren“ — Karten „Jede Seite“ / „Langes Bild“, Wasserzeichen, Qualität, Format, Zielordner; `ErfolgFenster` danach mit Öffnen / Ordner öffnen. Geschrieben wird in `services/bild_export.py` | `BildWahl` oder `None` |
| `pdf_export.py` | `PdfExportFenster`: „PDF-Datei exportieren“ — Reiter Allgemein (Speichern unter, Seitenbereich, Exportoptionen) und Berechtigungseinstellungen (Verschlüsseln, Kennwörter, Rechte, Druck); unten „Nach Abschluss des Exports schließen“. Schreibt nichts selbst: der Aufrufer gibt `exportieren(PdfWahl) -> bool` mit, Seitenbereich, Markierung und Verschlüsselung stecken in `services/pdf_export.py` | `PdfWahl` oder `None` |

## Dropdown-Pyramide (jede Stufe baut auf der darunter auf; alle Dropdown-Bausteine liegen im Paket `ui/baukasten/dropdown/`)

| Stufe | Zuständig | Datei | Stand |
|---|---|---|---|
| 1 Öffnungsverhalten (Lage in Fenster und Bildschirm) | `PopupVerhalten` (Basisklasse), `popup_klemmen` | `ui/baukasten/dropdown/popup_lage.py`, eingehängt in `core/application.py` | gilt für jedes `Qt.Popup`-Fenster |
| 2 Größe und Skalierung (Zeilenhöhe so kompakt wie möglich, sichtbare Zeilen, Breite, Kürzung) | `DROPDOWN_ZEILE_PAD_V`, `DROPDOWN_MAX_ZEILEN` in `mass.py`; `popup_begrenzen`, Kürz-Delegate | `ui/baukasten/basis/mass.py`, `auswahlfeld.py` | Auswahlfeld und Menüs (Stylesheet `PADDING_MENUEEINTRAG_GLOBAL`) nutzen dieselbe Quelle |
| 3 Aussehen (Farbe, Rand, Radius, Pfeil, Auswahlfarbe) | Stylesheet-Regeln `QComboBox`, `QMenu` | `ui/theme.py` | zentral; keine Farben in Widget-Stylesheets |
| 4 Bausteine | `Auswahlfeld`, `Schriftauswahl`, `MenueListe` (und `RasterAuswahl`, `GalerieAuswahl`, Kopf-Dropdowns), Reiter-Dropdown der `FlacheReiterLeiste` (`ReiterDropdown`), Überlaufmenü „•••“ der `UeberlaufLeiste` | `ui/baukasten/` | bauen auf 1–3 auf |

**Verbindlich (Eigentümer):** Jedes Dropdown-Menü, jedes aufklappende Fenster, jeder Menüknopf und jedes Auswahlfeld gehört in dieses Paket; der Aufrufort entscheidet nie. Die aufrufende Funktion legt nur fest, *was* ein Menü enthält und *welche Aktion* läuft; *wie* es aufgebaut ist und sich öffnet, steht im Paket. Neue Menüs entstehen nur aus `MenueListe`, neue Auswahlfelder nur aus `Auswahlfeld`/`Schriftauswahl`, Knöpfe mit Menü nur aus `DropdownKnopf`/`DropdownTaste` (`menue_setzen`). Wächter in `tests/integration/test_main_window.py`: kein rohes `QMenu(`, kein `addMenu("Text")`, kein `QComboBox(`, kein `setMenu(`/`setPopupMode(`/`setParent(…, Qt.Popup)` außerhalb des Pakets (Besitz über `menue_setzen(…, besitzen=True)`, Untermenü eines anderen Knopfes über `MenueListe.untermenue_einhaengen`), keine Dropdown-Größe und keine Dropdown-Farben außerhalb von Paket und Thema. Alle Stellen auf einen Blick: `docs/dropdown-bestand.md` (erzeugt mit `werkzeug/pruefen/dropdown-bestand.py`).

**Layoutvarianten statt eigener Stile:** Zeilentasten in Popups sind `dropdown_zeile(taste)` (`dropdown/zeile.py`; Regel `QPushButton[dropdownZeile]` in `ui/theme.py`), die schmale Menüzeile ist `MenueListe.kompakt()` (Regel `QMenu[variante="kompakt"]` im Thema). Weitere Eigenschaften im Thema: `dropdownFenster` (QFrame-Popups), `dropdownTitel` (Kopf, Abschnitt, Kopfzeile), `dropdownKachel` (Kachel, Stil), `dropdownKopf`, `dropdownLink`; Menü-Knopf und -Pfeil gestaltet nur das Thema, die Mini-Leiste hat dort keinen eigenen Stil mehr. Maße der Raster/Galerien/Paletten stehen in `mass.py` (`DROPDOWN_KACHEL`, `DROPDOWN_RASTERZELLE`, `DROPDOWN_FARBKACHEL` …). Neue Varianten entstehen als Eigenschaft + Themenregel, nie als `setStyleSheet` am Aufrufort (Wächter `test_dropdown_zeilen_und_menuemasse_nur_im_thema`).

**Verbindlich (Eigentümer):** Jedes Dropdown-Menü, jedes aufklappende Fenster, jeder Menüknopf und jedes Auswahlfeld gehört in dieses Paket; der Aufrufort entscheidet nie. Die aufrufende Funktion legt nur fest, *was* ein Menü enthält und *welche Aktion* läuft; *wie* es aufgebaut ist und sich öffnet, steht im Paket. Neue Menüs entstehen nur aus `MenueListe`, neue Auswahlfelder nur aus `Auswahlfeld`/`Schriftauswahl`, Knöpfe mit Menü nur aus `DropdownKnopf`/`DropdownTaste` (`menue_setzen`). Wächter in `tests/integration/test_main_window.py`: kein rohes `QMenu(`, kein `addMenu("Text")`, kein `QComboBox(`, kein `setMenu(`/`setPopupMode(`/`setParent(…, Qt.Popup)` außerhalb des Pakets (Besitz über `menue_setzen(…, besitzen=True)`, Untermenü eines anderen Knopfes über `MenueListe.untermenue_einhaengen`), keine Dropdown-Größe und keine Dropdown-Farben außerhalb von Paket und Thema. Alle Stellen auf einen Blick: `docs/dropdown-bestand.md` (erzeugt mit `werkzeug/pruefen/dropdown-bestand.py`).

**Layoutvarianten statt eigener Stile:** Zeilentasten in Popups sind `dropdown_zeile(taste)` (`dropdown/zeile.py`; Regel `QPushButton[dropdownZeile]` in `ui/theme.py`), die schmale Menüzeile ist `MenueListe.kompakt()` (Regel `QMenu[variante="kompakt"]` im Thema). Weitere Eigenschaften im Thema: `dropdownFenster` (QFrame-Popups), `dropdownTitel` (Kopf, Abschnitt, Kopfzeile), `dropdownKachel` (Kachel, Stil), `dropdownKopf`, `dropdownLink`; Menü-Knopf und -Pfeil gestaltet nur das Thema, die Mini-Leiste hat dort keinen eigenen Stil mehr. Maße der Raster/Galerien/Paletten stehen in `mass.py` (`DROPDOWN_KACHEL`, `DROPDOWN_RASTERZELLE`, `DROPDOWN_FARBKACHEL` …). Neue Varianten entstehen als Eigenschaft + Themenregel, nie als `setStyleSheet` am Aufrufort (Wächter `test_dropdown_zeilen_und_menuemasse_nur_im_thema`).

Eine Änderung gehört in die tiefste Stufe, die sie betrifft: Lage → Stufe 1, Maße → Stufe 2, Farbe → Stufe 3; Bausteine ändern daran nichts.

## Regeln

1. **Ein Popup liefert einen Wert** — `QColor` oder `None` („Keine Farbe“). Es kennt den Aufrufer nicht.
2. **Popups wirken sofort, Dialoge haben Vorschau und OK/Abbrechen.**
3. **„Keine“ und „Zuletzt benutzt“ stehen immer an derselben Stelle.**
4. **Nicht Mögliches bleibt grau sichtbar**, statt zu fehlen.
5. **Nichts nachbauen:** Wer eine Farbe braucht, nimmt `FarbPalette`/`FarbFeld`/`weitere_farben`, wer eine Linie braucht,
   `LinienWahl`/`Linie`, wer ein Maß braucht, `MassSpin`.

6. **Farben nur im Thema:** Ein Widget-Stylesheet trägt keine Akzentfarbe (`Farbe.AKZENT*`, `AUSWAHL`, Hex). Es setzt die Eigenschaft `akzentSchrift`, `akzentRand` oder `akzentFlaeche` (Chip-Marken: `texte.marke_faerben`), die Knöpfe `optFertig`/`sfSpeichern` bekommen ihre Farbe aus `ui/theme.py`, sonst gilt `palette(highlight)`/`palette(highlighted-text)`. Die Mint-Ersetzung von Blautönen in Widget-Stylesheets gibt es nicht mehr.
7. **Kein `QComboBox(` außerhalb von `auswahlfeld.py`:** Dropdowns sind `Auswahlfeld`/`Schriftauswahl` (Wächter: `tests/integration/test_main_window.py::test_kein_combobox_ausser_auswahlfeld`, Liste `COMBO_NOCH_ERLAUBT` darf nur kleiner werden).
## Wer den Baukasten benutzt

- **Band** (`core/commands.py`): Schriftfarbe, Hervorheben, Seitenfarbe, Absatz- und Tabellenschattierung, Formfüllung,
  Formkontur — alle über `_farbmenue()` bzw. `FarbPalette`. Die Live-Vorschau hängt an `ueberfahren`/`verlassen`.
- **Dialoge:** Wasserzeichen und Seitenrahmen (`DialogRahmen`, `FarbFeld`, `LinienWahl`, mit Vorschau), Formen/WordArt
  (`FarbFeld`), Silben farbig, Seite einrichten und Absatz (`MassSpin`).

## Neues Fenster oder neue Farbstelle

```python
from lunivo_writer.ui.baukasten import DialogRahmen, FarbFeld, LinienWahl, Linie

class MeinDialog(DialogRahmen):
    def __init__(self, parent):
        super().__init__(parent, "Mein Dialog", vorschau=self._male)
        self.farbe = FarbFeld("#1971c2", "Füllfarbe", keine_text="Keine Füllung")
        self.linie = LinienWahl(Linie("#000000", 1.0, "einfach"))
        self.zeile("Füllung", self.farbe); self.zeile("Linie", self.linie)
        self.farbe.farbeGeaendert.connect(self.aktualisieren); self.linie.geaendert.connect(self.aktualisieren)

    def _male(self, painter, rect): ...
    def ergebnis(self): return {"fuell": self.farbe.farbe, "linie": self.linie.linie().text()}
```

## Absatzrahmen

Der Rahmen eines Absatzes steht als Text `farbe|pt|art` am Absatz (`B_RAHMEN`); ein vierter Teil nennt die Seiten, wenn nicht alle
vier gemeint sind: `t` oben, `b` unten, `l` links, `r` rechts, `h` zwischen zwei Absätzen (`editor/objekte/linie.py`, Klasse `Linie`).
Ohne vierten Teil gelten alle Seiten, ältere Dateien bleiben also gültig. Gezeichnet wird in `editor/seite/pagination.py`, im DOCX gespeichert und gelesen als `w:pBdr` (`top`, `left`, `bottom`, `right`, `between`; Linienarten einfach, doppelt, gestrichelt,
gepunktet, Strich-Punkt).

- **Menü** (`RahmenMenue`): schaltet einzelne Seiten ein/aus, „Alle“, „Außen“, „Kein“; neue Rahmen übernehmen die zuletzt
  eingestellte Linie.
- **Fenster „Rahmen und Schattierung“** (`ui/baukasten/formatierung/rahmen_schattierung.py`, Muster in `editor/text/muster.py`): Reiter Rahmen (Einstellung, Linienart, Farbe, Breite, Vorschau mit Kantenknöpfen), Seitenrand und Schattierung (Füllfarbe, 37 Muster, Musterfarbe). Gespeichert wird das Muster am Absatz (`B_MUSTER`) und in DOCX als `w:shd`.

## Fenster für Absatz, Schrift, Listen, Tasten und Effekte

Alle Fenster liefern Werte und formatieren selbst nichts; der Aufrufer (Band, Editor, Formatvorlage) setzt das Ergebnis. Die Knopfzeile
unten kommt überall von `fussleiste` (`dialog_rahmen.py`), Maße von `EinheitFeld` / `MassSpin` (`mass_feld.py`).

| Baustein | Datei | Was dahinter steckt |
|---|---|---|
| Absatz | `absatz_dialog.py` | Einzüge, Abstände, Zeilenabstand (Faktor, Mindestens, Genau), Gliederungsebene, Seitenumbruch, Absatzoptionen (`editor/seite/absatzopt.py`); Umbruchregeln wirkt `editor/seite/seitenfluss.py` |
| Tabstopps | `tabstopp_dialog.py` | Position, Ausrichtung, Füllzeichen (`editor/text/tabfuell.py`, gezeichnet), Standardtabstopps (`w:defaultTabStop`) |
| Schriftart | `schriftart_dialog.py` | alle Felder: asiatisch/westlich/komplex, Unterstreichungsarten, Betonungszeichen, Effekte, Zeichenabstand; Zeichnen der Extras in `editor/text/textfx.py` |
| Texteffekte | `texteffekt_dialog.py` | Füllung (Farbe, Verlauf), Kontur, Schatten, Reflektion, Leuchten, 3D; Zeichnen in `editor/text/textfx.py`, DOCX als `w14:*` in `editor/text/texteffekt.py` |
| Nummerierung | `liste_dialog.py` | Aufzählung, Nummerierung, mehrstufige Gliederung (`editor/text/mehrstufig.py`, selbst gezeichnet), Anpassen-Fenster |
| Tastenkombination | `tasten_dialog.py` | eine Tastenkombination aufnehmen, Belegung prüfen |
| Formatvorlage | `formatvorlage_dialog.py` | Name, Basis, Folgevorlage, Leiste, Format ▾ mit Schriftart, Absatz, Tabstopps, Rahmen, Nummerierung, Texteffekte, Verknüpfung |
| Hilfen | `schiebe_feld.py`, `voreinstellung_menue.py`, `pipette.py` | Regler mit Feld, Popup mit Bildchen in Abschnitten, Farbe vom Bildschirm |

- **Gedämpfte Texte und Trennlinie** (`ui/baukasten/basis/texte.py`): `hinweis_label` (Hinweis-/Leertext, Farbe `Farbe.HINWEIS` = Palette-Rolle Mid je Thema, klein/Umbruch/`zusatz`), `kleintext_label` (kleine Beschriftung), `trennlinie()` (HLine in midlight); Themenwechsel frischt die Texte über `auffrischen` auf.
- **Chips und an/aus-Schalter** (`ui/baukasten/controls/schalter.py`): `chip_stil` (Auswahl-Chip, gewählt = Akzent), `chip_gruen_stil`, `schalter_an_stil`/`schalter_aus_stil` (Kapseln der Werkbank), `CHIP_B`/`CHIP_H`; Farben zur Laufzeit aus `Farbe`.
- **Zugängliche Namen** (`ui/baukasten/geruest/zugaenglichkeit.py`): `NamenFilter` gibt jedem Knopf ohne Namen beim Anzeigen seinen Tooltip als Namen (ohne Tastenkombination); wird einmal in `core/application.py` eingehängt.

Tests: `tests/oberflaeche/test_baukasten.py`.

## Zusatzfenster in der Seitenleiste

Seltene Einstellungen (Absatz, Schriftart, Rahmen, Listen, Seite einrichten …) öffnen sich nicht über dem Text, sondern als Seite in der
Seitenleiste — nur solange man sie bearbeitet. Die Breite der Seitenleiste ändert sich nie; der Inhalt passt sich an.
Jeder Baustein macht genau eine Sache:

| Baustein | Datei | Aufgabe |
|---|---|---|
| `PanelFaehig` | `zusatz_panel.py` | Markierung für ein Fenster: `exec()` zeigt es in der Seitenleiste (sonst wie bisher als Fenster) |
| `ZusatzPanel` | `zusatz_panel.py` | die Seite in der Seitenleiste: Kopf mit Titel und ✕, Rollbereich ohne seitliche Leiste, Unterfenster mit „←“; Kopfzeile = `panel_kopf` aus `panel_rahmen.py` (dieselbe wie `PanelRahmen` und „Formatierung“), Ränder `PANEL_KOPF_RAND`/`PANEL_INHALT_RAND` |
| `FormularGitter` | `formular_gitter.py` | Felder, die sich der Breite anpassen: `zeile(Beschriftung, Feld)`, `breit(Feld)`, `reihe((Beschr., Feld), …)`. Breit: zwei Paare nebeneinander; schmal: eines je Zeile; sehr schmal: Beschriftung über dem Feld |
| `Auswahlfeld` / `Schriftauswahl` | `auswahlfeld.py` | Das eine Dropdown (`Auswahlfeld.als_menue_nach_oben(zusatz=)`: öffnet stattdessen eine `MenueListe` über dem Feld, Häkchen rechts, `zusatz(menue)` füllt bei jedem Öffnen Zeilen unter einer Trennlinie (Chat: Denktiefe, Berechtigungen), z. B. Modellwahl im Chat; Drop-in für `QComboBox`/`QFontComboBox`): Feldbreite folgt dem Layout, Aufklappliste nie breiter als das Fenster/die Seitenleiste, Zeilen so kompakt wie Menüzeilen (Schrifthöhe + 2 × `DROPDOWN_ZEILE_PAD_V`), lange Texte mittig gekürzt. `popup_begrenzen(combo)` ist der geteilte Teil |
| `PopupVerhalten` / `popup_klemmen` | `popup_lage.py` | Die Basisklasse aller aufklappenden Fenster: `MenueListe` (und damit alle Menüs, Galerien, Paletten) und die Popup-Widgets (`MenueTafel`, `LayoutOptionen`) erben sie und öffnen sich nach denselben Regeln: im Bereich ihres Ankers (Seitenleiste mit Eigenschaft `popupGrenze`, sonst Fenster) ∩ Bildschirm, mit Randabstand `POPUP_RAND`, mindestens `DROPDOWN_BREITE_MIN` breit (`mass.py`). Kein Anwendungsfilter. Reihenfolge: `class X(PopupVerhalten, QMenu)` |
| Symbolwahl | `dropdown/auswahl/symbol_auswahl.py` | `SymbolWahl` (Taste mit Symbol + Pfeil, `wert()`, `geaendert(str)`) öffnet `SymbolAuswahl` (erbt `RasterAuswahl`); Symbole aus `ASSISTENT_SYMBOLE` (Schlüssel des Symbolkatalogs `ui/widgets/icons`) | Schlüssel |
| Erstellen-Fenster | `erstellen_fenster.py`, `vorlagen_chips.py` | `ErstellenFenster(PanelFaehig, QDialog)`: Hinweis, `VorlagenChips` (sechs Chips, „Alle anzeigen“), Name, Prompt, Knopfzeile; Basis von `SchnelleAktionDialog` und `KIAssistentDialog` (`ui/dialogs/ki/ki_dialoge.py`). `AufklappBereich` = „… anzeigen/ausblenden“ | `werte()` |
| Assistentenliste | `assistenten_liste.py` | `AssistentenListe(fenster)`: Hauptschalter „Fortlaufende Assistenten“, Liste mit Art (Aktion / Fortlaufend), Haken „an“, Entfernen, „Neuen Assistenten erstellen …“, „Schnelle KI-Aktion erstellen …“; im Reiter „Assistenten“ der KI-Einstellungen und in den Optionen ▸ Lunivo | folgt `ki.geaendert` |
| `AngepassteReiter` | `formular_gitter.py` | Reiter, deren Höhe dem gewählten Reiter folgt (kein leerer Platz unter kurzen Reitern) |
| `UmbruchSchalter` | `formular_gitter.py` | Ankreuzfeld, dessen langer Text umbricht |
| `FlussLayout` | `formular_gitter.py` | Reihe von Feldern, die wie Text umbricht (Beschriftung und Feld bleiben beisammen) |
| `KartenRaster` | `karten_raster.py` | Raster mit gemeinsamem Maßsystem: gleich große Zellen, Spaltenzahl nach Breite; jedes Element belegt eine Rasterspanne `Spalten×Zeilen` (`1×1`, `2×1`, `2×2`, `3×1`), die zentral in `SPANNEN` benannt ist (`addWidget(w, "breit")` oder Eigenschaft `raster_spanne`). Gleiche Spanne = gleiche Außenmaße; zu breite Spannen werden auf die vorhandenen Spalten gekürzt (ganze Zeile), nichts wird abgeschnitten. `spalten_fest=1` = untereinander (Funktionszeilen der Schreibhilfe in `werkbank.py`); `kurze_gruppen_ins_raster` setzt in jedem Seitenleisten-Fenster kurze Ankreuzfelder/Knöpfe nebeneinander |
| `EingabeFenster` | `eingabe_fenster.py` | kleine Abfrage in der Seitenleiste (Frage + Auswahlliste oder Textfeld): `getItem(parent, titel, frage, eintraege, aktuell)` / `getText(...)` wie `QInputDialog`, Rückgabe `(Text, ok)` |
| `ausfuehren_im_stapel` | `zusatz_panel.py` | ein `PanelFaehig`-Fenster in einem beliebigen `QStackedWidget` zeigen (z. B. die Fenster der Suche in der **linken** Seitenleiste, ohne dass sich die rechte öffnet) |
| `schmal_machen` | `schmal.py` | **Notbehelf** für Fenster, die noch nicht aus Bausteinen gebaut sind: bricht zu breite Zeilen nachträglich um. Neue Fenster bauen mit `FormularGitter`, nicht darauf verlassen |

Ein Fenster, das aus einem offenen Zusatzfenster heraus aufgerufen wird (zum Beispiel „Farben“ aus „Rahmen und Schattierung“), legt sich als weitere Seite darüber (mit „←“); das darunter bleibt offen.

Neues Fenster: `class MeinDialog(PanelFaehig, QDialog)`, Felder in `FormularGitter`-Gruppen. Fertig umgebaut (alle Fenster der Seitenleiste außer Rahmen und Schattierung): Farben, Absatz, Schriftart, Tabstopps, Layout, Nummerierung, Gliederung, Texteffekte, Formatvorlage. Dazu KI-Einstellungen (`KIEinstellungenDialog`, `kompakt_machen()` kürzt die Reiternamen, die Sprachlisten stehen untereinander).
Ebenso die Fenster der Reiter Einfügen, Verweise, Sendungen und Überprüfen (Zahl, Felder, Umbruch, Seitenzahl, Hyperlink, Objekt,
Form, SmartArt, WordArt, Diagramm, Piktogramm, Formel, Deckblatt, Baustein, Inhaltsverzeichnis, Indexeintrag, Nummerierung,
Beschriftung, Querverweis, Empfänger, Seriendruckfeld, Felder zuordnen, Wörter zählen, Wasserzeichen). Breite Fenster (Hyperlink,
Inhaltsverzeichnis, Diagramm) stellen ihre Spalten in `kompakt_machen()` untereinander (ein so senkrecht gestelltes `QHBoxLayout` lässt
`schmal_machen` in Ruhe). Was in der Vorlage rechts daneben steht (Vorschau, „Übernehmen für“), steht in der Seitenleiste darunter;
Vorschaubilder verkleinern sich mit der Breite. Ebenfalls auf `FormularGitter`/`FlussLayout` umgebaut: Umschlag, Etiketten, Seriendruck, Regel, Quelle, Textmarke, Quellen verwalten, Formularfeld, Silben farbig (Test in `test_fenster_seitenleiste_weitere.py`). Weitere Fenster (Register anpassen, Symbole, Benutzeroberfläche, Lesehilfe, Welche Hilfe wann, Abfragen, Diagrammdaten, Tabelleneigenschaften, Bild zuschneiden): `tests/oberflaeche/test_fenster_seitenleiste_weitere.py`. Prüfung: `tests/oberflaeche/test_fenster_seitenleiste.py` — jedes Fenster bei 444 und bei 300 px,
nichts darf links oder rechts herausragen. Neue Seitenleisten-Fenster dort in `FENSTER` eintragen.
Unterfenster eines Seitenleisten-Fensters (z. B. Diagrammdaten) öffnen über `zeige_unter` im selben Stapel.

Platz in der Seitenleiste: Wer Größen der Seitenleiste braucht, bietet `passe_an(breite, hoehe)` an (`ZusatzPanel` ruft es mit `verfuegbar` und `verfuegbar_hoehe` auf, die die Seitenleiste aus ihrer echten Größe setzt); Beispiele: Farbraster, Rahmenvorschau, Kachelzahl der Nummerierung, Texteffekte. `AngepassteReiter` und der Stapel der KI-Einstellungen richten die Höhe nach der gewählten Seite. Prüfung: `test_seitenleisten_seiten_passen_in_echte_groesse`.
Auf dem Notbehelf nur noch: Rahmen und Schattierung (bewusst: Spalten mit Vorschau, `schmal_nein` schützt die Kantenknöpfe) und die kleinen Fenster mit `QFormLayout`.
Tests, die Fenster per Zeitgeber schließen, müssen auch die Fenster in der Seitenleiste finden (`tests/integration/test_smoke_befehle.py`).

## Bausteine des Reiters Start

| Baustein | Datei | Aufgabe |
|---|---|---|
| Suchmaschine | `editor/text/suche.py` | `Suchauftrag` (Groß/klein, ganzes Wort, Platzhalter, Präfix, Suffix, Satz- und Leerzeichen übergehen, Zeichen- und Absatzformat), Sonderzeichen-Codes (`SPEZIAL`, `^p ^t ^l …`), `naechster`, `treffer`, `ersatz_text`, `alle_ersetzen` (ein Rückgängig-Schritt). Keine Oberfläche |
| Gehe zu | `editor/dokument/gehe_zu.py` | `ELEMENTE` (Seite, Abschnitt, Zeile, Textmarke, …), `positionen`, `ziel(ed, element, eingabe, richtung)` |
| Suchen-Feld | `ui/document/dokumentfenster/suchen_feld.py` | `SuchenFeld`: Reiter Suchen/Ersetzen/Gehe zu, Erweitern/Reduzieren, Format ▾ (Schriftart, Absatz, Tabstopps, Formatvorlage, Hervorheben), Spezial ▾, Lesehervorhebung, Suchen in. Sitzt in der linken Seitenleiste (`navigation.py`), Unterfenster über `ausfuehren_im_stapel` |
| Auswählen | `editor/text/auswahl.py`, `ui/baukasten/controls/auswahl_bereich.py` | Tabelle ohne Rahmen, ähnliche Formatierung (hervorgehoben, da Qt nur eine Markierung kennt); `AuswahlBereich` listet alle Objekte |
| Formatvorlagen und Formatierung | `ui/baukasten/vorlagen/formatvorlagen_bereich.py` | `FormatvorlagenBereich`, `vorlagen_namen`, `vorlagen_schrift` |
| Text sortieren | `ui/baukasten/dokument/sortieren_dialog.py`, `editor/text/schreibweise.py` | `SortierenDialog` (drei Schlüssel, Überschriftenzeile) mit `SortierOptionenDialog` (Feldtrenner, Groß/klein, Sortiersprache); `reihenfolge` (QCollator), `absaetze`, `umstellen` (behält Formate) |
| Wort-Extras | `editor/text/wortextras.py` | `MENUE`: verschachtelte Liste (Text, Symbol, Funktion) für das Menü; jede Funktion ein Rückgängig-Schritt |
| Unterstreichungen | `ui/baukasten/basis/linien.py`, `editor/text/textfx.py` | `LinienZeile(…, maler=)` / `linien_menue_zeile(…, maler=unter_zeichnen)`: Menüzeilen mit gezeichneter Unterstreichung |
| Absatzwerte | `ui/baukasten/formatierung/absatz_dialog.py` | `aus_block(bf)`: die Werte des Absatz-Fensters aus einem `QTextBlockFormat` |

## Bausteine des Reiters Einfügen

| Baustein | Datei | Aufgabe |
|---|---|---|
| Klappmenüs | `core/befehle/hauptreiter/einfuegen.py` | `menue_…Klappe` für Leere Seite, Umbrüche, Tabelle (10 × 10, Text ↔ Tabelle), Bild, Textfeld, Schnellbausteine, Symbol (zuletzt verwendet + eigene Symbole) — aus `MenueListe`, `ZellenRaster`, `RasterAuswahl` |
| Zahlschreibweisen | `editor/text/zahlformat.py` | `TYPEN`, `zahl_text(n, typ)` (1,2,3 · A,B,C · I,II,III · ①②③ · Zahlwort), `zahlwort`. Keine Oberfläche |
| Text ↔ Tabelle | `editor/tabelle/tabelle_text.py` | `markierte_absaetze`, `zellen`, `text_zu_tabelle`, `tabelle_zu_text` (je ein Rückgängig-Schritt), `TRENNER` |
| Felder | `editor/dokument/felder.py` | `FELDER` (Name → Beschreibung, Feldanweisung), `ergebnis`, `feld_einfuegen` (Text mit `P_FELD`, im DOCX ein echtes Feld) |
| Deckblatt | `editor/seite/deckblatt.py` | 17 Gestaltungen (Artikel, Firma, Lebenslauf, Abschlussarbeit), hoch und quer; eigener erster Abschnitt, Grafik als ganzseitiges Abschnitts-Wasserzeichen hinter dem Text (`"ganzseitig"` in `editor/seite/wasserzeichen.py`), `einfuegen`, `entfernen` |
| Galerien | `core/befehle/hauptreiter/einfuegen.py` | `menue_…Klappe` für Deckblatt, Formen, Seitenzahl, Wasserzeichen (eigene + Voreinstellung), WordArt, Gleichung — alle aus `RasterAuswahl` |
| Seitenbildchen | `ui/baukasten/medien/seiten_bildchen.py` | `seitenzahl_zeichner`, `wasserzeichen_zeichner`, `deckblatt_zeichner`, `plus_zeichner` — Zeichner `f(QPainter, QRectF)` für Kacheln und Vorschauen |
| Seitenzahlen | `editor/seite/seitenzahl.py` | `VORGABEN`, `MUSTER`, `seitenzahl_setzen(page, ort, ausrichtung, muster)`, `seitenzahlen_entfernen` (arbeiten auf `PageSettings`) |
| Formenkatalog | `editor/objekte/formen_katalog.py` | `KATEGORIEN` (Linie … Legenden), `pfad(name, r)`, `ist_linie`, `namen`; `editor.dokument.einfuegen.form_bild` zeichnet damit |
| Gleichungen, WordArt | `editor/dokument/einfuegen.py` | `GLEICHUNGEN`, `formel_bild`, `WORDART_VORGABEN`, `DECKBLATT_VORLAGEN` |
| Diagramme | `editor/diagramme/diagramm.py`, `editor/diagramme/diagramm_kreis.py` | `TYPEN` (Säule, Linie ×6, Kreis ×5, Balken, Fläche ×3, X Y ×7 mit Blase, Kurs ×4 mit Volumen, Netz, Kombination; „Vorlagen“ ist im Fenster eine leere Seite, `VORLAGEN` nur für alte Dokumente), `bild(untertyp, titel, kategorien, reihen)` → `QImage` über QtCharts in einer eigenen `QGraphicsScene`; `beispiel(untertyp)` liefert die Beispieldaten des Fensters; `namen_angewendet` setzt die Namensquelle (`zeile1`/`spalte_a`/`keine`, Befehl `diagrammNamenQuelle`); 3D-Kreis, Kreis von Kreis und Balken von Kreis zeichnet `diagramm_kreis.py` mit QPainter; `ALT` für frühere Namen |
| Diagramm formatieren | `ui/baukasten/diagramme/diagramm_format_panel.py`, `editor/diagramme/diagramm_format.py` | Seitenleiste „Formatierung“ je Diagrammteil: baut auf `ObjektFormatPanel` (Füllung, Linie, Effekte; Erweiterungspunkte `_zusatz_radios`/`_zusatz_felder`) und `TexteffektPanel` (Textoptionen + Schrift + Textfeld) auf; Optionen von Legende, Achse (Skala), Reihe (Lückenbreite, Glättung, Pfeile); Größe/Drehung/Alternativtext beim Diagrammbereich. Gezeichnet mit `freie_bilder` (Pinsel, Stift), `bildeffekte`, `textfx`; Datenmodell `daten["teil_format"][teil]` siehe Kopf von `diagramm_format.py` |
| Fenster | `ui/dialogs/einfuegen/einfuegen_fenster.py` | `ZahlDialog`, `FelderDialog`, `TrennerDialog` (Text in Tabelle / Tabelle in Text), `SeitenzahlDialog`, `HyperlinkDialog` (Datei/Webseite, Stelle im Dokument, E-Mail; `ergebnis()`), `ObjektDialog` (aus Datei, als Symbol; `art()`) — ändern das Dokument nicht selbst |
| Fenster (Daten) | `ui/dialogs/einfuegen/einfuegen_dialoge.py` | `DiagrammDialog` mit `DiagrammDatenDialog`, `DatumDialog` (Formate, Sprache, „Automatisch aktualisieren“ → Feld), `WordArtDialog`, `FormelDialog` |

## Bausteine des Reiters Seitenlayout

| Baustein | Datei | Aufgabe |
|---|---|---|
| Designs | `editor/text/designs.py` | `FARBSCHEMEN` (8 Farben: dunkel, hell, Akzent 1–6), `SCHRIFTPAARE` (Überschrift, Text), `EFFEKTE` (fx wie `bildeffekte`), `DESIGNS` (Farbschema + Schriftpaar), `design(name)`. Alles eigene Namen und Farben |
| Designbildchen | `ui/baukasten/medien/design_bildchen.py` | `design_zeichner`, `farbreihe_zeichner`, `schriftpaar_zeichner`, `effekt_zeichner` für die Galerien |
| Seitenbildchen | `ui/baukasten/medien/seiten_bildchen.py` | dazu `raender_zeichner`, `format_zeichner` (hoch/quer), `papier_zeichner`, `textrichtung_zeichner` |
| Listenzeile | `ui/baukasten/dropdown/auswahl/raster_auswahl.py` | `zeilenkachel(bild, titel, angaben, spalten)`: Bildchen + fetter Titel + Angaben (Ränder, Größe, Orientierung, Textrichtung); `RasterAuswahl(hoehe_max=…)` rollt lange Galerien, `trenner()` im Fuß, `kachel(aktiv=False)` bleibt blass sichtbar |
| Klappmenüs | `core/befehle/hauptreiter/seite.py` | `menue_…Klappe` für Designs, Farben, Schriftarten, Effekte, Ränder, Orientierung, Größe, Spalten, Textrichtung, Zeilennummern, Seitenfarbe (mit Wasserzeichen), Ausrichten; Haken werden in `aboutToShow` aufgefrischt |
| Effekte für alle | `editor/objekte/bildlayout.py` | `fx_alle(ed, fx)`: Effekt an alle freien Bilder und Formen (sonst nur an das markierte) |
| Zeilennummern | `editor/seite/zeilennummern.py` | `nummern(doc, ch, art)`: fortlaufend oder je Seite neu; Absätze mit `absatzopt` „ohne_zeilennr“ (DOCX `w:suppressLineNumbers`) zählen nicht. `PageSettings.zeilennummern_neu`, DOCX `w:lnNumType w:restart` |
| Leere Seite | `editor/seite/leere_seite.py` | `leere_seite(doc, letzter_block, einrichtung, quer)`: neues Blatt hinter der Seite (`DocumentEditor.seite_letzter_block`), quer als eigener Abschnitt |

## Bausteine des Reiters Verweise

| Baustein | Datei | Aufgabe |
|---|---|---|
| Inhaltsverzeichnis | `editor/dokument/verzeichnis.py` | `TOC_VORGABE`, `toc_optionen(doc)`: Füllzeichen, Ebenen 1–9, Seitenzahlen anzeigen/rechtsbündig, Verknüpfungen (verborgene Textmarken „_Toc…“) — am Kopf als `B_TOC_OPT`; `verzeichnis_aktualisieren(ed, nur)`, `vorhanden(doc, art)` |
| Indexeinträge | `editor/dokument/indexeintrag.py` | `Eintrag` (Haupt/Unter, Sortierung, „Siehe“, Seitenbereich über Textmarke, fett/kursiv), `feld`/`aus_feld` (Word-Feld XE); am Text `P_INDEX` + `P_INDEX_OPT`; `verweise.index_eintragen(ed, e, alle)` |
| Fenster | `ui/dialogs/verweise/verweise_fenster.py` | `InhaltsverzeichnisDialog` (mit Seitenansicht; `ergebnis()`), `IndexeintragDialog` (Signal `markieren(Eintrag, alle)`), `BeschriftungDialog` (Nummer steht im Feld; eigene Bezeichnungen in `verweise/beschriftungen`; `NummerierungDialog`), `QuerverweisDialog` (Signal `einfuegen(ziel, wie, link, oben_unten)`, bleibt offen) — ändern das Dokument nicht selbst |

| Beschriftung, Querverweis | `editor/dokument/verweise.py` | `beschriftung_einfuegen(…, nach, ohne_bezeichnung, zahl)` mit SEQ-Schreibweise (`SEQ_FORMAT`), `naechste_nummer`; `VERWEISTYPEN`, `verweisen_auf(art)`, `querverweis_ziele`, `querverweis_einfuegen(ed, ziel, wie, link, oben_unten)` — Ziel bekommt eine verborgene Textmarke „_Ref…“ |
| Klappe | `core/befehle/hauptreiter/verweise.py` | `menue_inhaltsverzeichnisKlappe`: Ebene 1–9 und Textkörper (Formatvorlage „Überschrift N“ / „Standard“); Fuß- und Endnoten einzeln mit `note_springen(delta, art)` |

## Bausteine des Reiters Mailings (Seriendruck)

| Baustein | Datei | Aufgabe |
|---|---|---|
| Reiter | `ui/contextual/serien_tools.py` | Kontext-Reiter `SERIENDRUCK` („Mailings“), erscheint über Verweise ▸ Seriendruck (`serienReiter`), weg mit `serienSchliessen` |
| Befehle | `core/befehle/hauptreiter/serien.py` | Datenquelle je Dokumentfenster (`tab.serie`, nicht gespeichert); `kann_<Befehl>` macht Knöpfe ohne Datenquelle grau; `feld_datensatz` ist das Nummernfeld im Band |
| Datenquelle, Felder | `editor/dokument/sendungen.py` | `quelle_lesen` (CSV/TSV/TXT), `zugeordnet`, `NAECHSTER`/`naechster_einfuegen`, `gruppen`, `brief_fuer(vorlage, [Sätze])`, `felder_hervorheben` |
| Vorschau | `ui/document/ansicht/vorschau_ansicht.py` | schreibgeschützter Editor mit dem Brief eines Datensatzes statt der Vorlage (`art="serien"`); die Vorlage bleibt unverändert |
| Fenster | `ui/dialogs/sendungen/serien_fenster.py` | `EmpfaengerDialog`, `FeldDialog` (Signal `einfuegen`, bleibt offen), `ZuordnenDialog` |
| Band | `ui/ribbon/ribbon_bar.py` | allgemein: `kann_<Befehl>` (Knopf frei/grau) und Einträge `{"feld": name}` (Eingabefeld aus `feld_<name>`; hat es `auffrischen()`, ruft `aktualisieren` es auf) |

## Bausteine des Reiters Überprüfen

| Baustein | Datei | Aufgabe |
|---|---|---|
| Reiter | `ui/ribbon/tabs/review_tab.py` | Anordnung nach den Vorlagen ueberpruefen/01–10 |
| Befehle | `core/befehle/hauptreiter/ueberpruefen.py` | Klappen (Rechtschreibprüfung, Löschen, Nachverfolgen, Markup, Überprüfen, Annehmen, Ablehnen, Vergleichen), `feld_anzeige` (Fassung + „Markup anzeigen“), `bearbeitungEinschraenken`/`schutz_setzen` (`tab.schutz`, nur für die Sitzung) |
| Zählen | `editor/text/statistik.py` | `zaehlen(texte, seiten)`: Wörter, Zeichen mit/ohne Leerzeichen, Absätze, asiatische Zeichen |
| Fassungen | `editor/dokument/fassungen.py` | `original(doc)` (Kopie ohne Einfügungen, Löschungen als Text), `bearbeiter(doc)`, `zeiten(doc)` |
| Markup-Auswahl | `ui/document/bearbeitung/zusatz_editor.py` | `markup_filter` (Kommentare, Einfügungen, Bearbeiter, Tag), `aenderung_sichtbar`, `angezeigte_aenderungen`; Sprechblasen folgen der Auswahl |
| Original | `ui/document/ansicht/vorschau_ansicht.py` | dieselbe Vorschau mit `art="original"` |
| Fenster | `ui/dialogs/ueberpruefen_fenster.py` | `WoerterDialog`, `SchutzDialog` (Seitenleiste) |

## Weitere Bausteine in `ui/baukasten/`

| Baustein | Datei | Aufgabe |
|---|---|---|
| Aktionsleiste | `aktionen_leiste.py` | „Meine Aktionen“: die schnellen KI-Aktionen (eigene Assistenten) als Knöpfe, in der Seitenleiste der Schreibhilfe und im KI-Chat dieselbe Leiste |
| Beschriftung | `beschriftung.py` | Beschriftungen mit Schrifteigenschaften oder Markdown (`Qt.MarkdownText`) |
| Bild vergrößern | `bild_zoom.py` | Fenster „Vergrößern“ (Lupe in der Schnellleiste am Bild): Bild in seiner Auflösung, Zoom mit Regler und Mausrad |
| Dateisymbole | `datei_symbole.py` | lokale Dateityp-Symbole aus der zentralen Symbolsammlung |
| Diagramm-Popups | `diagramm_popups.py` | Popups der Schnellleiste am Diagramm und Klappen der Diagrammtools — Band und Schnellleiste zeigen dasselbe; Schnelllayout: 11 Kacheln in der Reihenfolge des Fotos (`SCHNELLLAYOUT_ANZEIGE` → Nummer in `SCHNELLLAYOUTS`, `core/befehle/kontextreiter/diagrammtools.py`; Nummern bleiben stabil); Filter, Reiter „Name“: Radiogruppen für die Namensquelle |
| Druckfenster | `druck_dialog.py` | eine Spalte: oben die Reiter „Standard“, „Lunivo-Office“ und „Drucker“, darunter die Vorschau; öffnet in der Seitenleiste (`PanelFaehig`) |
| Druckvorschau | `druckvorschau.py` | Druckvorschau als ganzes Fenster: Blattwechsel, Ansicht (eine, zwei, alle Seiten), Zoom, Einpassen |
| Einklappgruppe | `einklappgruppe.py` | eingeklappte Gruppe („Weitere Einstellungen“): Knopf mit Pfeil, darunter der Inhalt auf Wunsch |
| Fensterstapel | `fenster_stapel.py` | Unterfenster öffnen als Seite im selben Fenster statt als neues Fenster darüber |
| Formmenüs | `form_menues.py` | Menüs und Galerie der Zeichentools für Formen („Form bearbeiten“, Stilgalerie) |
| Galerieauswahl | `galerie_auswahl.py` | Galerie-Popup: Kacheln mit Textprobe und Namen, in Spalten, mit Aktionen darunter |
| Kachelfeld | `kachel_feld.py` | beschriftete Kacheln zum Anklicken, immer genau eine gewählt (zum Beispiel die Umbruchart eines Bildes) |
| Layoutfenster | `layout_dialog.py` | Fenster „Layout“ für Bilder und Formen: Position, Textumbruch, Größe |
| Layoutoptionen | `layout_optionen.py` | Popup „Layoutoptionen“ neben einem markierten Bild: Umbruchart, „Mit Text verschieben“, „Fester Text“ |
| Objektformat | `objektformat_panel.py` | Seitenleiste „Formatierung“ für Bild, Form, Textfeld oder WordArt |
| Objektmenüs | `objekt_menues.py` | Popups für markierte Bilder oder Formen: Formstile, Füllung, Kontur |
| Panelrahmen | `panel_rahmen.py` | Rahmen eines Feldes in einer Seitenleiste: Titel (auch mehrfarbig: `titel_teile`), Knöpfe (Symbol oder Text), Menü und Schließen (abschaltbar: `schliessbar=False`); Styling der Seitenfelder über `seitenKarte` in `theme.py` |
| Karte/Zeile | `karte.py` | `als_karte(widget, art)` setzt die Eigenschaft `karte` (zeile, karte, kompakt, ki, markiert, nutzer, fehler, eingabe, chip (checkbar: gewählt = Akzent), senden, anhang, miniatur, liste, liste_eng); die Regeln stehen einmal dort und im Thema (`theme.py`), kein Widget-Stylesheet |
| KI-Chat: Eingabe | `chat_eingabe.py` | `ChatEingabeKasten`: Textfeld (Enter sendet, Umschalt+Enter neue Zeile) mit Rahmen (Fokus aus dem Thema), + (Lokales Bild hinzufügen, Bild aus Text, Websuche), Anhang-Chip über dem Textfeld (`chat_anhang.py`: `AnhangChip`; Karten-Arten `anhang`/`miniatur`), Befehle (Meine Aktionen, zuletzt „Neue Aktion …“), Modellfeld mit Denktiefe/Berechtigungen, runder Senden-/Stopp-Knopf, Fußzeile; meldet `senden` (Anhang über `anhang()`), `bild`, `stopp`, `meldung`, `neue_aktion` |
| Änderungsvorschau | `aenderungs_vorschau.py` | `AenderungsVorschau`: schreibgeschütztes Feld (Karten-Art `karte`) für Stücke `(art, text)` — „entfernt“ durchgestrichen, „neu“ unterstrichen, „gleich“ normal; Farben aus den Thema-Rollen `Farbe.ENTFERNT`/`Farbe.NEU`, Deckkraft/Höchsthöhe aus `mass.py` (`AENDERUNG_DECKKRAFT`, `CHAT_VORSCHAU_MAX`); wächst mit dem Text, dann Scrollen; folgt dem Themenwechsel (`stuecke_setzen`) |
| KI-Chat: Nachrichten | `chat_blase.py` | `NutzerBlase` (mit Bild-Miniatur, `miniatur()`; fehlt die Datei: „[Bild]“), `KiBlase(dienst, text, cent, index)` (Wiederholen, Kopieren, Einfügen, Ersetzen; beide klappen eine Vorschau-Karte mit Übernehmen/Verwerfen auf; Zustand nur aus `dienst.bezug_gueltig`, ungültig = grau + Grund als Tooltip und Hinweiszeile), `FehlerKarte` (Wiederholen, KI-Einstellungen), `SymbolKnopf`; rufen den Dienst, melden über Signale |
| KI-Chat: Regler | `chat_regler.py` | `ChatReglerBlock`: Länge, Temperatur, Top P, Stoppfolgen, „Antwort direkt einfügen“ (zugeklappt) in den KI-Einstellungen; liest/schreibt `chat_optionen`/`chat_setzen`. Der Chat zeigt keine Aktionsleiste, keine Reglers und keine Token-Anzeige |
| KI-Chat: Leerzustand | `chat_leerzustand.py` | `ChatLeerzustand`: Symbol, Text und Vorschlags-Chips aus `ai/chat_vorschlaege.py`; Klick füllt das Eingabefeld |
| Maße | `mass.py` | EINE Quelle aller UI-Maße, benannt nach Rolle: `RADIUS_*`, `ICON_*`, `HOEHE_*`, `BREITE_*`, `GROESSE_*` (Tupel, `setFixedSize(*…)`), `RAND_*` (Tupel, `setContentsMargins(*…)`), `ABSTAND_*`, `SCHRIFT_*` (pt), `ZUGABE_*`, `PADDING_*`/`MARGIN_*` (Textbausteine wie `"4px 10px"` für Stylesheets, per f-String eingesetzt), Kachelgrößen als `GROESSE_*_KACHEL` bzw. `GROESSE_*_BILD` (`QSize(*…)`). Seit 2026-11-05 stehen in ganz `ui/` keine nackten Maße mehr (rund 500 Konstanten); neue Maße zuerst hier benennen. Fenster (`dialogs/`, `hauptfenster/`, `backstage.py`) und Bausteine nutzen sie; keine nackten Zahlen für Maße (nur Werte, kein Verhalten) |
| Leitzeichen | `ruby_dialog.py` | Fenster „Phonetisches Leitzeichen“: Text in Teilen mit Leittext, Ausrichtung, Abstand, Schrift |
| Schreibweise | `schreibweise_dialog.py` | Fenster „Groß-/Kleinschreibung“: eine der fünf Arten wählen |
| SmartArt-Format | `smartart_format_panel.py` | Seitenleiste „Formatierung“ für SmartArt: Füllung und Linie, Effekte, Textoptionen |
| SmartArt-Menüs | `smartart_menues.py` | Menüs, Galerie und Miniaturen für SmartArt (Reiter „SmartArt-Design“, Schnellleiste, Dialog „SmartArt-Grafik auswählen“) |
| Textformat | `text_format.py` | Schriftname, Größe, Fett, Kursiv, Ausrichtung, Zeilenabstand wie im Band |
| Umbruchsymbole | `umbruch_symbole.py` | Bildchen für den Textumbruch um ein Bild: Textzeilen in Grau, das Bild als blaues Feld |
| Eingeschlossene Zeichen | `umschlossen_dialog.py` | Fenster „Eingeschlossene Zeichen“: Vorlage, Text und Form (Kreis, Quadrat, Dreieck, Raute) |
| Vorlagengalerie | `vorlagen_galerie.py` | Seite „Neu“: leeres Dokument starten oder Standard- und eigene Vorlagen durchsuchen |
| Werkbank | `werkbank.py` | die Funktionen eines Reiters der Schreibhilfe als große Zeilen (Symbol, Name, Hinweis, Tastenkürzel, „an/aus“) |

## Befehle nach Aufgaben

`core/commands.py` enthält nur noch die Grundfunktionen von `Befehle` (Aktion suchen, ausführen, Zustand). Die Befehle selbst stehen in
`core/befehle/`, je Aufgabe ein Baustein: `text` (Zeichen und Absatz), `bearbeiten`, `einfuegen`, `seite` (Seite, Abschnitte, Spalten),
`pruefen` (Schreibhilfe, Vergleichen), `ueberpruefen` (Reiter Überprüfen), `serien` (Mailings), `ansicht`, `datei`, `verweise`, `kommentare`, `kontext` (Tabelle, Bild, Formen), `kopffuss`, `bildtools`, `formtools`, `texttools`, `smartarttools`, `diagrammtools`, `hilfen`, `ki`.
Ein neuer Befehl kommt in den Baustein seiner Aufgabe; `Befehle` setzt sie zusammen. Kein Baustein importiert `commands.py`.

## Aufbau der großen Klassen

Die drei großen Klassen sind nach Aufgaben in Bausteine (Mixins) geteilt. Die Hauptdatei behält Aufbau, Signale und Qt-Ereignisse
(`…Event`), die Bausteine die Aufgaben:

| Klasse | Hauptdatei | Bausteine |
|---|---|---|
| `Befehle` | `core/commands.py` (Grundfunktionen) | `core/befehle/*.py` |
| `MainWindow` | `ui/main_window.py` | `ui/hauptfenster/`: `dateien`, `bearbeiten`, `oberflaeche`, `backstage_steuerung` |
| `DocumentEditor` | `ui/document/bearbeitung/document_editor.py` | `ui/document/editor_*.py`: `anzeige`, `spalten`, `seiten`, `formatierung`, `bilder`, `schreibhilfe` |
| `OptionenAnsicht` | `ui/dialogs/optionen.py` | `ui/dialogs/optionen_seiten/`: `lesen`, `ansicht`, `datei`, `befehle`, `lunivo`, `name_ki` |

Regel: Ein neuer Befehl, eine neue Editor-Funktion oder eine neue Optionen-Seite kommt in den Baustein ihrer Aufgabe, nicht in die Hauptdatei.
Bausteine kennen die Hauptdatei nicht (kein Import zurück); Werte, die mehrere brauchen, stehen in `gemeinsam.py` des jeweiligen Ordners.

## Bausteine der Seitenleiste „Formatierung“ für Diagramme

Jeder Baustein liegt in einer eigenen Datei unter `ui/baukasten/` und hat eine Aufgabe. Eingebunden werden sie nur im Diagramm-Panel
(`diagramm_format_panel.py`) durch Mixins und Komposition. Die Basis (`objektformat_panel.py`, `texteffekt_dialog.py`, `formular_gitter.py`,
`farbpalette.py`, `schiebe_feld.py`, `linien.py`) bleibt unverändert; Form-Panel, SmartArt-Panel und das Fenster „Texteffekte“ sehen aus wie zuvor
(Schalter `NUR_DREI_EFFEKTE`, `AUTO_FELDER`, `KOPF_MENUES`, `FOTO` im SmartArt-Panel auf `False`).
Vorlage: die Fotos in `~/Schreibtisch/Illustrationen/Diagram/`; Abgleich Foto für Foto in `docs/pruefung-illustrationen.md`.

| Baustein | Datei | Aufgabe | Meldet |
|---|---|---|---|
| Flache Reiterleiste | `flache_reiter_leiste.py` | `FlacheReiterLeiste(QTabBar)` in zwei Arten: Hauptreiter (Großbuchstaben, aktiver fett mit Linie) und Unterreiter (Symbol oben, Beschriftung darunter, bricht um, aktiv blau); `flach_machen(reiter, art)` setzt sie in ein `QTabWidget`; zeichnet den Teil-Pfeil „▾“ hinter dem Reitertext. Passen die Hauptreiter (Beschriftung gemessen) nicht nebeneinander, ersetzt EIN Dropdown (`ReiterDropdown`: `DropdownTaste` + `MenueListe`, Name des aktuellen Reiters, Haken am aktuellen, nicht wählbare grau) die Leiste und wählt über `setCurrentIndex`/`currentChanged`; Reiter mit Knopf bleiben Reiter. Maß `REITER_DROPDOWN_RAND` in `mass.py`. Die `UeberlaufLeiste` (Band, Dokumente) behält „•••“ | Klick auf den Pfeil, Wahl im Dropdown |
| Teilmenü | `teil_menue.py` | `TeilMenueKnopf`: Liste der Diagrammteile als Popup mit Haken beim aktuellen | `gewaehlt(str)` |
| Auto-Felder | `auto_felder_mixin.py` | Bei „Automatisch“ stehen Füll- und Linienfelder sichtbar, aber grau | – |
| Strichauswahl | `strich_auswahl.py` | Dropdown mit Strichvorschau (Kombinierter Typ 5, Strichtyp 8 Zeilen) | `gewaehlt(str)` |
| Effekte (3) | `effekte_drei_mixin.py`, `abschnitt_gruppe.py`, `winkel_feld.py` | Nur Schatten, Leuchten, Weiche Kanten, zugeklappt, höchstens einer offen (`EinzelOffen`), Nullwerte, Schatten-Winkel mit Drehknopf (`WinkelFeld`) | – |
| Kopfmenüs | `kopf_dropdown.py`, `fuell_voreinstellungen.py`, `linien_voreinstellungen.py`, `kopf_menue_mixin.py` | Dropdown im Kopf von FÜLLUNG und LINIE (Keine, Designfarben, Graduelle, Muster, Struktur; Voreingestellte Linie 8×4) | `gewaehlt(str)` |
| Text-Kopfmenüs | `text_kopf_menue_mixin.py` | dasselbe für TEXTFÜLLUNG und TEXTKONTUR, ohne die Basis zu ändern | – |
| Textfüllarten | `text_fuellarten_mixin.py` | Fünf Radios der Textfüllung (Bild/Textur, Muster) mit `fuell_pinsel` | – |
| Alternativtext | `alternativtext_abschnitt.py` | Titel und Beschreibung mit 400 ms Verzögerung | `geaendert(titel, text)` |
| Textfeld | `textfeld_abschnitt.py` | Ausrichtung, Textrichtung, Textwinkel, Ränder in Inch (intern pt), „Text nicht drehen“ | `geaendert()` |

| `ui/dialogs/einfuegen/smartart_dialog_foto.py` | `SmartArtDialogFoto(SmartArtDialog)`: SmartArt einfügen nach der Vorlage (Reiter „Alle“, Kacheln 126 x 76 px, Vorschau darunter mit Name und Beschreibung, blauer OK-Knopf); `SmartArtDialog` bleibt für das Bearbeiten |
| `ui/baukasten/diagramme/smartart_stil_kacheln.py` | `stil_bild_org(nr, groesse)`, `stile_galerie_org(b)`: Stilkacheln im Band „SmartArt-Design“ mit Organigramm-Motiv, Galerie `smartartStile` |
| `ui/baukasten/dokument/layout_dialog_objekt.py` | `LayoutDialogObjekt(LayoutDialog)`, Fabrik `layout_dialog_fuer(art)`: Fenster „Layout“ nach der Vorlage — Position bei „Im Textfluss“ grau, „Relativ“ immer grau, Abstand Oben/Unten/Links/Rechts, bei SmartArt Drehung, Original-Skalierung und Zurücksetzen gesperrt, Originalgröße leer; `LayoutDialog` bleibt für Absatz/Tabelle |
| `ui/baukasten/dropdown/objektmenues/layout_optionen_objekt.py` | `LayoutOptionenObjekt(LayoutOptionen)`: Popup „Layoutoptionen“ mit ✕ im Kopf, Kacheln 50 px, Eigenschaft `verschieben_wahl` (`"mit_text"`, `"fest"`, None = beide Radios leer) |

**Eingabefelder im Thema (eine Regelgruppe in `ui/theme.py`, Block „EINGABEFELD“):** `QLineEdit`, `QSpinBox`, `QDoubleSpinBox`, `QComboBox`, `QPlainTextEdit` und `QTextEdit[eingabefeld="true"]` teilen Rahmen (`rand`), Radius, Fläche (`feld`), Innenabstand, `:focus` (Akzent) und `:disabled`. Die Regel für Seitenleisten-Karten (`*[seitenKarte="true"]`) trifft nur Listen, Rollbereiche und `QTextBrowser`, nicht Eingabefelder (sie hatte `QPlainTextEdit` rahmenlos gemacht). Ausnahme nur per Eigenschaft: Chat-Eingabekasten `karte="eingabe"`. Ein rohes `QTextEdit` (Dokument, Vorschau) bleibt ohne Rahmen.
