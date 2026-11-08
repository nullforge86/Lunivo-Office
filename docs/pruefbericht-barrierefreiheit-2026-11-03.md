# Prüfbericht Oberfläche: Barrierefreiheit und Tastaturbedienung (Phase A + B)

Stand: 2026-11-03. Grundlage: statische Untersuchung des Quellcodes (grep und Lesen der Fundstellen) im Arbeitsbaum, Zweig `mint-thema`.
**Nicht geprüft:** Laufzeitverhalten, Screenreader (Orca/NVDA), Kontrastmessung, Skalierung 125–200 %. Alles Folgende ist Code-Befund, keine Praxisprüfung.

## 1. Bestandsaufnahme (Zahlen)

| Merkmal | Anzahl | Anmerkung |
|---|---:|---|
| `Qt.NoFocus` (`setFocusPolicy`) | 14 Fundstellen in 11 Dateien | siehe Abschnitt 2 |
| `setAccessibleName` | 114 | gute Basis |
| `setAccessibleDescription` | 5 | kaum genutzt |
| `setBuddy` | 26 | Beschriftungen an Feldern verknüpft |
| `setTabOrder` | 1 | Tab-Reihenfolge fast überall implizit (Layout-Reihenfolge) |
| `QAccessible` / `accessibleInterface` | 0 | keine eigenen Rollen für selbstgebaute Widgets |
| Tastenkürzel-Tabelle | `ui/kuerzel.py` + `hauptfenster/dateien.py:541` | F3–F10, Strg-Kürzel; F10 springt zum Band (`backstage_steuerung.py:480`) |
| Widgets mit eigenem `mousePressEvent` | 9 Dateien | Kandidaten für Tastatur-/Rollenprüfung |
| Widgets mit eigenem `keyPressEvent` | 10 Dateien | Tastatur grundsätzlich bedacht |
| A11y-Tests (Programm) | `tests/oberflaeche/test_optionen.py::test_optionen_barrierefrei_namen_und_fokus` | deckt nur Optionsfenster ab |
| A11y-Prüfung (Dokument) | `proofing/barrierefreiheit.py`, `tests/proofing/test_pruefen_tools.py::test_barrierefreiheit_findet_alle_vier_klassen` | betrifft erzeugte Dokumente, nicht die Oberfläche |

## 2. Bestätigte Befunde (`Qt.NoFocus`)

Bewertung: **Lücke** = per Tab/Pfeiltaste nicht erreichbar und kein Ersatzweg gefunden; **vertretbar** = Kontext rechtfertigt es, sofern Tastaturweg anderswo besteht.

| ID | Datei:Zeile | Element | Befund | Einstufung |
|---|---|---|---|---|
| A11Y-01 | `ui/backstage.py:110` | `QListWidget` Dateinavigation | Bestätigt. Liste nicht fokussierbar, Auswahl per Maus. | **Lücke, P1** |
| A11Y-02 | `ui/dialogs/lesen_hilfe/hilfe_dialoge.py:120` | Handbuch-Navigation (`nav`) | Bestätigt, ebenfalls `NoFocus`. (Auswahlsignal `itemClicked` noch zu prüfen: Pfeiltasten lösen es nicht aus, `currentItemChanged` nötig.) | **Lücke, P1** |
| A11Y-03 | `ui/baukasten/controls/kachel_feld.py:27` | `KachelFeld`-Schaltflächen | Bestätigt. Genutzt in `layout_dialog.py:130`, `layout_optionen.py:31/35`, `einfuegen_dialoge.py:119`. Sieben Fenster betroffen, daher größter Hebel. | **Lücke, P1** |
| A11Y-04 | `ui/baukasten/vorlagen/vorlagen_galerie.py:119` | `QTabBar` Vorlagenregister | Bestätigt. | **Lücke, P2** |
| A11Y-05 | `ui/ribbon/ribbon_bar.py:75` | Blätterpfeile des Bandes | Bestätigt. Abmilderung: `F10` und Tab/Pfeile auf Reitern existieren; ob alle Register ohne Pfeile erreichbar sind, ist ungeprüft. | **P2, Teilweise gedeckt** |
| A11Y-06 | `ui/widgets/mini_leiste.py:105,108,129,183` | schwebende Mini-Leiste (Schriftart, Größe, Knöpfe) | Neu gefunden (nicht im Auftrag). Schwebende Leiste, die den Fokus nicht aus dem Text ziehen soll; Tastaturersatz sind die Kürzel (Strg+B/I/U, Fenster Schriftart Strg+D). | vertretbar, dokumentieren |
| A11Y-07 | `ui/document/tabelle/tabelle_griffe.py:72,97` | Tabellen-Ziehgriffe | Neu. Reine Maus-Griffe; Tastaturweg über Tabellen-Fenster/Band prüfen. | P3, prüfen |
| A11Y-08 | `ui/document/ansicht/absatz_symbol.py:28` | Absatz-Layout-Symbol | Neu. Menü nur per Maus; Funktionen („Absatzformat zurücksetzen“) sollten auch im Band/Menü stehen. | P3, prüfen |
| A11Y-09 | `ui/document/bearbeitung/document_editor.py:100` | Vorschlags-Popup | Üblich (Fokus bleibt im Editor). Auswahl per Strg+1…6 vorhanden. | vertretbar |
| A11Y-10 | `ui/dialogs/optionen.py:192` | nur Lesezugriff auf Policy | Kein Befund. | – |

`FunktionsZeile` (`ui/baukasten/geruest/werkbank.py:23`) ist **StrongFocus**, hat `setAccessibleName` und Tastenbedienung. Positiv. Offen: es ist ein `QFrame` ohne Rolle (kein `QAccessible`-Interface), Screenreader meldet vermutlich nur „Rahmen“ statt „Schaltfläche/Schalter“; Zustand (an/aus) steht nur im Label `zustand`, nicht im Accessible-Namen/Description. Praxisprüfung nötig.

## 3. Weitere Risiken (Code-Hinweise, nicht verifiziert)

- **R1 Rollen/Zustände:** Keine Spuren eigener Accessibility-Schnittstellen. Selbstgebaute Widgets (`farbwaehler`, `rahmen_schattierung`, `lineal`, `blasen_flaeche`, `sonderzeichen`) sind vermutlich für Screenreader stumm.
- **R2 Beschreibungen:** Nur 5 Accessible Descriptions; Symbolknöpfe haben meist nur Tooltip. Tooltip ist nicht in jeder Konfiguration als Name sichtbar.
- **R3 Tab-Reihenfolge:** Ein einziges `setTabOrder`; Reihenfolge hängt am Layout. Fenster mit `FormularGitter`/`FlussLayout` können bei Umbruch eine andere visuelle als Tab-Reihenfolge ergeben.
- **R4 Fokusrahmen:** Teilweise eigene Stylesheets (z. B. Blätterpfeile, Tabs `bandReiter`) setzen `border: none`. Ob `:focus` sichtbar gestaltet ist, ist ungeprüft; wichtig, sobald NoFocus entfernt wird.
- **R5 Kontrast/Skalierung:** Kleine Schrift (8–9 pt, `palette(mid)`) in Kürzel/Untertiteln; Kontrast `mid` auf `window` nicht gemessen.
- **R6 Testabdeckung:** Ein Programm-A11y-Test, nur Optionen. Backstage, Handbuch, Kacheln, Galerie, Band ohne Fokus-/Namenstest.

## 4. Maßnahmenplan (Phase B)

Reihenfolge nach Hebel und Risiko; jedes Paket klein und einzeln prüfbar. Pro Paket gilt der Test laut CLAUDE.md (gezielt, keine Vollsuite).

| ID | Prio | Aufgabe | Dateien | Lösung | Nebenwirkungen | Test | Abnahme |
|---|---|---|---|---|---|---|---|
| M1 | P1 | `KachelFeld` tastaturbedienbar | `ui/baukasten/controls/kachel_feld.py` | `Qt.TabFocus`/`StrongFocus` nur für den gewählten Knopf (Roving Tabindex), Pfeiltasten wechseln und wählen, Leertaste/Enter aktiviert; `setAccessibleName(text)`, Auswahl „ausgewählt“ via Checked + Description; sichtbarer Fokusrahmen | Tab-Reihenfolge in 4 Fenstern ändert sich; Optik unverändert halten | neuer Test in `tests/oberflaeche/test_baukasten.py` (Fokus, Pfeile, Name) | Tab erreicht das Feld genau einmal; Pfeile wählen; Name nicht leer; Mausverhalten unverändert |
| M2 | P1 | Backstage-Liste fokussierbar | `ui/backstage.py` | `StrongFocus`, Auswahl über `currentItemChanged`/Enter, Fokus beim Öffnen auf Liste, bei Rückkehr auf auslösendes Element; Zeilendelegat `_Zeile` Fokusrahmen | Delegat zeichnet evtl. keinen Fokus | `tests/oberflaeche/test_backstage.py` ergänzen | Pfeiltasten wechseln Seite, Enter öffnet, Esc zurück; Fokus sichtbar |
| M3 | P1 | Handbuch-Navigation | `ui/dialogs/lesen_hilfe/hilfe_dialoge.py` | `StrongFocus`, `currentRowChanged` statt nur `itemClicked`, Accessible Name | Wechsel beim bloßen Pfeil-Scrollen springt Text (gewollt) | kleiner Test (Fokus + Pfeil wechselt Abschnitt) | Tastatur erreicht und steuert die Liste |
| M4 | P2 | Vorlagenregister | `ui/baukasten/vorlagen/vorlagen_galerie.py` | `NoFocus` entfernen, Pfeiltasten (QTabBar-Standard), Name | Stylesheet `bandReiter` Fokusdarstellung | Test in Galerie-Testdatei | Tab erreicht, Pfeil wechselt Register |
| M5 | P2 | Blätterpfeile des Bandes | `ui/ribbon/ribbon_bar.py` | zunächst prüfen, ob Reiter ohne Pfeile erreichbar sind (F10 + Pfeile). Wenn ja: Accessible Names „Band nach links/rechts blättern“, Fokus per `TabFocus` nur wenn nötig | Autorepeat bei Fokus | `werkzeug/funktionspruefung.py` (Band) | Alle Reiter ohne Maus erreichbar |
| M6 | P2 | Rollen/Zustände eigener Widgets | `werkbank.py` und weitere | erst Praxisprüfung mit Orca; dann je nach Befund Accessible Description (Zustand) oder `QAccessibleWidget`-Unterklasse | Plattformabhängig (Orca/NVDA) | manuelle Prüfung, dokumentiert | Screenreader nennt Rolle + Zustand |
| M7 | P2 | Allgemeiner Programm-A11y-Test | neu `tests/oberflaeche/test_bedienung_a11y.py` | generalisiert den Optionstest: Hauptfenster, Backstage, Handbuch, Kachel-Fenster auf Name + Fokus; Ausnahmenliste (A11Y-06/07/09) mit Begründung | Test kann anfangs rot sein, bis M1–M4 fertig | selbst | Liste der Ausnahmen darf nur kleiner werden |
| M8 | P3 | Mini-Leiste, Tabellengriffe, Absatzsymbol | siehe A11Y-06..08 | Tastaturersatz dokumentieren/ergänzen (Menüeintrag im Band) | gering | gezielt | jede Funktion hat einen Tastaturweg |
| M9 | P3 | Kontrast/Skalierung | `ui/theme.py` | Messung (rechnerisch, WCAG-Verhältnis der Palette), dann Tokens anpassen; Test bei 125/150/200 % und 300 px Seitenleiste | Optikänderung | Messwerkzeug in `werkzeug/` (Markdown-Ausgabe) | Text ≥ 4,5:1, Symbole/Rahmen ≥ 3:1, Fokus ≥ 3:1 |
| M10 | P3 | Funktionsübersicht (Auffindbarkeit) | `docs/` | Tabelle Funktion/Bereich/Weg/Schritte/Kürzel aus `interne-funktionen.md` und `kuerzel.py` ableiten | keine | – | Übersicht vollständig, Lücken bei Kürzeln benannt |

Abhängigkeiten: M7 nach M1–M4; M6 braucht Praxisprüfung (Orca unter Linux verfügbar prüfen); M1 vor M8.

## 5. Offene Fragen an den Eigentümer

1. Reihenfolge einverstanden (M1 → M2 → M3 → M4 …)?
2. Soll die Mini-Leiste bewusst fokusfrei bleiben (Empfehlung: ja, mit dokumentierter Ausnahme)?
3. Ist Orca auf diesem Rechner installiert, damit M6 praktisch geprüft werden kann?

## 6. Nicht Bestandteil dieses Berichts

Der zweite Auftrag (Sicherheit/Import/MCP/LanguageTool/Datenmodelle) ist noch nicht untersucht und braucht eine eigene Bestandsaufnahme.
