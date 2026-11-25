# Bericht: Umstrukturierung auf deutsche Namen (2026-11-11)

Branch `aufgeraeumt`. Sicherung vor dem Umbau: Commit `5b9cd9a`, Marke `sicherung-vor-umstrukturierung`.
Es wurde nichts gelöscht: vorher 941 Dateien, nachher 941 Dateien (plus dieser Bericht). 731 Dateien haben einen neuen Ort oder Namen.

Leitlinie für die Namen: kurze, gebräuchliche deutsche Wörter, keine Abkürzungen, keine zum Verwechseln ähnlichen Namen,
keine Umlaute in Pfaden (ae, oe, ue, ss). Python-Dateien in `snake_case`.

## Neue Verzeichnisstruktur

```text
Lunivo-Office/
├── .claude/                  Agentenprofile
├── ressourcen/               (vorher assets/)
│   ├── bilder/               Bildschirmfotos, Titelbild (vorher images/)
│   ├── icons/                Symbole des Programms; dateitypen/ (vorher filetypes/), entwurf/
│   ├── schriftarten/         (vorher fonts/)
│   └── symbole/              Programmsymbol in Varianten
├── dokumentation/            (vorher docs/)
│   ├── README.md             Projektaufbau
│   ├── benutzerhandbuch/     Installation, Bedienung, Speichern, Einstellungen
│   ├── entwicklung/          Baukasten, Inventar, Erweiterungen, Plattformen
│   ├── architektur/          Aufbau von Band und Optionen, Dropdown, UI-Technologie
│   ├── konzepte/             Richtung, Konzept Optionen, Optimierung, symbolsystem/
│   └── berichte/             Prüf-, Test- und Abschlussberichte
├── src/lunivo_writer/
│   ├── ki/                   (vorher ai/)
│   ├── kern/                 (vorher core/)
│   ├── editor/
│   ├── modelle/              (vorher models/)
│   ├── plattform/
│   ├── korrektur/            (vorher proofing/)
│   ├── ressourcen/           (vorher resources/)
│   ├── dienste/              (vorher services/); integrationen/
│   └── oberflaeche/          (vorher ui/)
│       ├── band/             (vorher ribbon/); reiter/ (vorher tabs/)
│       ├── baukasten/        felder/ (vorher controls/), sonst unverändert
│       ├── bauteile/         (vorher widgets/)
│       ├── dialoge/          (vorher dialogs/)
│       ├── dokument/         (vorher document/)
│       ├── hauptfenster/
│       ├── kontext/          (vorher contextual/)
│       ├── seitenleiste/     (vorher sidebar/)
│       └── statusleiste/     (vorher statusbar/)
├── tests/                    korrektur/ (vorher proofing/), sonst unverändert
├── werkzeuge/                (vorher werkzeug/)
│   ├── erstellung/           (vorher bauen/)
│   ├── pruefungen/           (vorher pruefen/)
│   ├── symbole/
│   └── git_haken/            (vorher git-haken/)
├── skripte/                  starten-qt.sh, schrift-holen.sh, stimme-holen.sh (vorher im Hauptordner)
├── main.py, README.md, CLAUDE.md, CLOUD-KI-ANWEISUNGEN.md, LICENSE
└── pyproject.toml, requirements.txt, requirements-dev.txt, uv.lock
```

## Bewusst nicht umbenannt

- Paketname `lunivo_writer`, Startbefehl `lunivo-writer`, `main.py`, `src/`, `tests/`, `conftest.py`, `README.md`, `LICENSE`, `CLAUDE.md`, `pyproject.toml`, `requirements*.txt`, `uv.lock`: feste Namen von Python, pytest, Git und GitHub.
- Einstellungsschlüssel wie `ui/weich` oder `ui/seitenleiste`: Sie stehen in den gespeicherten Einstellungen der Benutzer. Ein neuer Name würde vorhandene Einstellungen verlieren.
- Benutzerordner außerhalb des Projekts (`~/.local/share/fonts/lunivo-office`), Paketziel `/opt/stevie-empire/lunivo-office/`.
- Eigennamen und Formatnamen: docx, odt, rtf, pdf, mcp, argos, ollama, claude, languagetool, smartart, backstage, dropdown.
- Klassen-, Funktions- und Variablennamen im Code (z. B. `MainWindow`, `ASSETS`, `write_docx`): nicht Teil dieses Auftrags.
- Dateinamen der fremden Dateityp-Symbole (`archive.svg`, `photo.svg` …) samt ihrer `LICENSE.txt` und `README.md`.
- Shell-Skripte behalten ihren Namen mit Bindestrich (`deb-bauen.sh`, `haken-an.sh`).

## Umbenannte Dateien (neuer Dateiname)

| Bisher | Neu |
|---|---|
| `assets/images/diagram.png` | `ressourcen/bilder/diagramm.png` |
| `docs/ENTSTEHUNG.md` | `dokumentation/entwicklung/entstehung.md` |
| `docs/INSTALLATION.md` | `dokumentation/benutzerhandbuch/installation.md` |
| `docs/LIESMICH.md` | `dokumentation/benutzerhandbuch/liesmich.md` |
| `docs/RICHTUNG.md` | `dokumentation/konzepte/richtung.md` |
| `docs/SPEICHERN.md` | `dokumentation/benutzerhandbuch/speichern.md` |
| `src/lunivo_writer/ai/ai_service.py` | `src/lunivo_writer/ki/ki_dienst.py` |
| `src/lunivo_writer/core/application.py` | `src/lunivo_writer/kern/anwendung.py` |
| `src/lunivo_writer/core/commands.py` | `src/lunivo_writer/kern/befehlsliste.py` |
| `src/lunivo_writer/core/document_manager.py` | `src/lunivo_writer/kern/dokument_verwaltung.py` |
| `src/lunivo_writer/core/paths.py` | `src/lunivo_writer/kern/pfade.py` |
| `src/lunivo_writer/editor/seite/pagination.py` | `src/lunivo_writer/editor/seite/seiten_aufteilung.py` |
| `src/lunivo_writer/editor/seite/pagination_deko.py` | `src/lunivo_writer/editor/seite/seiten_aufteilung_deko.py` |
| `src/lunivo_writer/models/page.py` | `src/lunivo_writer/modelle/seite.py` |
| `src/lunivo_writer/models/proofing.py` | `src/lunivo_writer/modelle/korrektur.py` |
| `src/lunivo_writer/models/report.py` | `src/lunivo_writer/modelle/bericht.py` |
| `src/lunivo_writer/proofing/proofing_service.py` | `src/lunivo_writer/korrektur/korrektur_dienst.py` |
| `src/lunivo_writer/services/docx_reader.py` | `src/lunivo_writer/dienste/docx_leser.py` |
| `src/lunivo_writer/services/docx_writer.py` | `src/lunivo_writer/dienste/docx_schreiber.py` |
| `src/lunivo_writer/services/file_service.py` | `src/lunivo_writer/dienste/datei_dienst.py` |
| `src/lunivo_writer/services/odt_reader.py` | `src/lunivo_writer/dienste/odt_leser.py` |
| `src/lunivo_writer/services/odt_writer.py` | `src/lunivo_writer/dienste/odt_schreiber.py` |
| `src/lunivo_writer/services/recovery.py` | `src/lunivo_writer/dienste/wiederherstellung.py` |
| `src/lunivo_writer/services/rtf_writer.py` | `src/lunivo_writer/dienste/rtf_schreiber.py` |
| `src/lunivo_writer/services/settings_service.py` | `src/lunivo_writer/dienste/einstellungen_dienst.py` |
| `src/lunivo_writer/ui/contextual/diagramm_tools.py` | `src/lunivo_writer/oberflaeche/kontext/diagramm_werkzeuge.py` |
| `src/lunivo_writer/ui/contextual/header_footer_tools.py` | `src/lunivo_writer/oberflaeche/kontext/kopf_fuss_werkzeuge.py` |
| `src/lunivo_writer/ui/contextual/image_tools.py` | `src/lunivo_writer/oberflaeche/kontext/bild_werkzeuge.py` |
| `src/lunivo_writer/ui/contextual/serien_tools.py` | `src/lunivo_writer/oberflaeche/kontext/serien_werkzeuge.py` |
| `src/lunivo_writer/ui/contextual/table_tools.py` | `src/lunivo_writer/oberflaeche/kontext/tabellen_werkzeuge.py` |
| `src/lunivo_writer/ui/contextual/text_tools.py` | `src/lunivo_writer/oberflaeche/kontext/text_werkzeuge.py` |
| `src/lunivo_writer/ui/document/bearbeitung/base.py` | `src/lunivo_writer/oberflaeche/dokument/bearbeitung/basis.py` |
| `src/lunivo_writer/ui/document/bearbeitung/document_editor.py` | `src/lunivo_writer/oberflaeche/dokument/bearbeitung/dokument_editor.py` |
| `src/lunivo_writer/ui/document/dokumentfenster/document_area.py` | `src/lunivo_writer/oberflaeche/dokument/dokumentfenster/dokument_bereich.py` |
| `src/lunivo_writer/ui/document/dokumentfenster/document_tabs.py` | `src/lunivo_writer/oberflaeche/dokument/dokumentfenster/dokument_reiter.py` |
| `src/lunivo_writer/ui/main_window.py` | `src/lunivo_writer/oberflaeche/programmfenster.py` |
| `src/lunivo_writer/ui/ribbon/menubar.py` | `src/lunivo_writer/oberflaeche/band/menueleiste.py` |
| `src/lunivo_writer/ui/ribbon/ribbon_bar.py` | `src/lunivo_writer/oberflaeche/band/band_leiste.py` |
| `src/lunivo_writer/ui/ribbon/ribbon_bausteine.py` | `src/lunivo_writer/oberflaeche/band/band_bausteine.py` |
| `src/lunivo_writer/ui/ribbon/ribbon_gruppen.py` | `src/lunivo_writer/oberflaeche/band/band_gruppen.py` |
| `src/lunivo_writer/ui/ribbon/ribbon_knoepfe.py` | `src/lunivo_writer/oberflaeche/band/band_knoepfe.py` |
| `src/lunivo_writer/ui/ribbon/ribbon_raender.py` | `src/lunivo_writer/oberflaeche/band/band_raender.py` |
| `src/lunivo_writer/ui/ribbon/ribbon_reiter.py` | `src/lunivo_writer/oberflaeche/band/band_reiter.py` |
| `src/lunivo_writer/ui/ribbon/ribbon_schnellzugriff.py` | `src/lunivo_writer/oberflaeche/band/band_schnellzugriff.py` |
| `src/lunivo_writer/ui/ribbon/ribbon_stile.py` | `src/lunivo_writer/oberflaeche/band/band_stile.py` |
| `src/lunivo_writer/ui/ribbon/ribbon_zustand.py` | `src/lunivo_writer/oberflaeche/band/band_zustand.py` |
| `src/lunivo_writer/ui/ribbon/tabs/ai_tab.py` | `src/lunivo_writer/oberflaeche/band/reiter/ki_reiter.py` |
| `src/lunivo_writer/ui/ribbon/tabs/file_tab.py` | `src/lunivo_writer/oberflaeche/band/reiter/datei_reiter.py` |
| `src/lunivo_writer/ui/ribbon/tabs/home_tab.py` | `src/lunivo_writer/oberflaeche/band/reiter/start_reiter.py` |
| `src/lunivo_writer/ui/ribbon/tabs/insert_tab.py` | `src/lunivo_writer/oberflaeche/band/reiter/einfuegen_reiter.py` |
| `src/lunivo_writer/ui/ribbon/tabs/layout_tab.py` | `src/lunivo_writer/oberflaeche/band/reiter/layout_reiter.py` |
| `src/lunivo_writer/ui/ribbon/tabs/mailings_tab.py` | `src/lunivo_writer/oberflaeche/band/reiter/sendungen_reiter.py` |
| `src/lunivo_writer/ui/ribbon/tabs/references_tab.py` | `src/lunivo_writer/oberflaeche/band/reiter/verweise_reiter.py` |
| `src/lunivo_writer/ui/ribbon/tabs/review_tab.py` | `src/lunivo_writer/oberflaeche/band/reiter/ueberpruefen_reiter.py` |
| `src/lunivo_writer/ui/ribbon/tabs/section_tab.py` | `src/lunivo_writer/oberflaeche/band/reiter/abschnitt_reiter.py` |
| `src/lunivo_writer/ui/ribbon/tabs/view_tab.py` | `src/lunivo_writer/oberflaeche/band/reiter/ansicht_reiter.py` |
| `src/lunivo_writer/ui/ribbon/toolbars.py` | `src/lunivo_writer/oberflaeche/band/werkzeugleisten.py` |
| `src/lunivo_writer/ui/sidebar/panels/ai_panel.py` | `src/lunivo_writer/oberflaeche/seitenleiste/panels/ki_panel.py` |
| `src/lunivo_writer/ui/sidebar/panels/writing_panel.py` | `src/lunivo_writer/oberflaeche/seitenleiste/panels/schreib_panel.py` |
| `src/lunivo_writer/ui/sidebar/sidebar.py` | `src/lunivo_writer/oberflaeche/seitenleiste/seitenleiste.py` |
| `src/lunivo_writer/ui/statusbar/status_bar.py` | `src/lunivo_writer/oberflaeche/statusleiste/statusleiste.py` |
| `src/lunivo_writer/ui/theme.py` | `src/lunivo_writer/oberflaeche/thema.py` |
| `src/lunivo_writer/ui/widgets/flow_layout.py` | `src/lunivo_writer/oberflaeche/bauteile/fluss_layout.py` |
| `src/lunivo_writer/ui/widgets/icons.py` | `src/lunivo_writer/oberflaeche/bauteile/symbole.py` |
| `tests/dokument/formate/test_docx_roundtrip.py` | `tests/dokument/formate/test_docx_hin_und_zurueck.py` |
| `tests/dokument/formate/test_formats.py` | `tests/dokument/formate/test_formate.py` |
| `tests/dokument/seite/test_layout_tab.py` | `tests/dokument/seite/test_layout_reiter.py` |
| `tests/integration/test_main_window.py` | `tests/integration/test_programmfenster.py` |
| `tests/integration/test_smoke_befehle.py` | `tests/integration/test_schnelltest_befehle.py` |
| `tests/ki/fake_mcp_server.py` | `tests/ki/mcp_test_server.py` |
| `tests/oberflaeche/test_bedienung_a11y.py` | `tests/oberflaeche/test_bedienung_barrierefreiheit.py` |
| `tests/plattform/test_storage.py` | `tests/plattform/test_wiederherstellung.py` |
| `tests/proofing/test_issue.py` | `tests/korrektur/test_fund.py` |
| `tests/proofing/test_proofing_positionen.py` | `tests/korrektur/test_korrektur_positionen.py` |
| `tests/proofing/test_proofing_pruefer.py` | `tests/korrektur/test_korrektur_pruefer.py` |
| `tests/proofing/test_pruefen_tools.py` | `tests/korrektur/test_pruefen_werkzeuge.py` |
| `werkzeug/bauen/arbeitsplan-bauen.py` | `werkzeuge/erstellung/arbeitsplan_bauen.py` |
| `werkzeug/bauen/inventar-bauen.py` | `werkzeuge/erstellung/inventar_bauen.py` |
| `werkzeug/pruefen/dropdown-bestand.py` | `werkzeuge/pruefungen/dropdown_bestand.py` |
| `werkzeug/pruefen/menuestruktur-abgleich.py` | `werkzeuge/pruefungen/menuestruktur_abgleich.py` |
| `werkzeug/pruefen/pruefbogen-abgleich.py` | `werkzeuge/pruefungen/pruefbogen_abgleich.py` |
| `werkzeug/pruefen/pruefbogen-zuordnung-bauen.py` | `werkzeuge/pruefungen/pruefbogen_zuordnung_bauen.py` |
| `werkzeug/pruefen/stapel-demo.py` | `werkzeuge/pruefungen/stapel_demo.py` |
| `werkzeug/symbole/icon-zeichner.py` | `werkzeuge/symbole/icon_zeichner.py` |
| `werkzeug/symbole/svg-zu-pfad.py` | `werkzeuge/symbole/svg_zu_pfad.py` |
| `werkzeug/symbole/symbol-kontaktbogen.py` | `werkzeuge/symbole/symbol_kontaktbogen.py` |

## Verschobene Ordner (alle Dateien darin, Dateiname unverändert oder siehe oben)

| Bisher | Neu | Dateien |
|---|---|---|
| `assets/fonts/` | `ressourcen/schriftarten/` | 1 |
| `assets/icons/` | `dokumentation/` | 1 |
| `assets/icons/entwurf/` | `ressourcen/icons/entwurf/` | 129 |
| `assets/icons/filetypes/` | `ressourcen/icons/dateitypen/` | 19 |
| `assets/icons/` | `ressourcen/icons/` | 2 |
| `assets/images/` | `ressourcen/bilder/` | 23 |
| `assets/symbole/varianten/Abstrakt/` | `ressourcen/symbole/varianten/Abstrakt/` | 11 |
| `assets/symbole/varianten/icon-SVG/` | `ressourcen/symbole/varianten/icon-SVG/` | 10 |
| `assets/symbole/varianten/klassisch-3d/` | `ressourcen/symbole/varianten/klassisch-3d/` | 10 |
| `assets/symbole/varianten/klassisch-dunkel/` | `ressourcen/symbole/varianten/klassisch-dunkel/` | 10 |
| `docs/` | `dokumentation/entwicklung/` | 6 |
| `docs/` | `dokumentation/benutzerhandbuch/` | 10 |
| `docs/` | `ressourcen/icons/` | 1 |
| `docs/` | `dokumentation/` | 1 |
| `docs/` | `dokumentation/konzepte/` | 3 |
| `docs/` | `dokumentation/architektur/` | 6 |
| `docs/berichte/` | `dokumentation/berichte/` | 6 |
| `docs/symbolsystem/` | `dokumentation/konzepte/symbolsystem/` | 3 |
| `./` | `skripte/` | 3 |
| `src/lunivo_writer/ai/` | `src/lunivo_writer/ki/` | 31 |
| `src/lunivo_writer/core/` | `src/lunivo_writer/kern/` | 8 |
| `src/lunivo_writer/core/befehle/` | `src/lunivo_writer/kern/befehle/` | 2 |
| `src/lunivo_writer/core/befehle/hauptreiter/` | `src/lunivo_writer/kern/befehle/hauptreiter/` | 17 |
| `src/lunivo_writer/core/befehle/kontextreiter/` | `src/lunivo_writer/kern/befehle/kontextreiter/` | 12 |
| `src/lunivo_writer/models/` | `src/lunivo_writer/modelle/` | 4 |
| `src/lunivo_writer/proofing/` | `src/lunivo_writer/korrektur/` | 12 |
| `src/lunivo_writer/resources/` | `src/lunivo_writer/ressourcen/` | 4 |
| `src/lunivo_writer/resources/daten/` | `src/lunivo_writer/ressourcen/daten/` | 4 |
| `src/lunivo_writer/services/` | `src/lunivo_writer/dienste/` | 25 |
| `src/lunivo_writer/services/docx_teile/` | `src/lunivo_writer/dienste/docx_teile/` | 19 |
| `src/lunivo_writer/services/integrations/` | `src/lunivo_writer/dienste/integrationen/` | 3 |
| `src/lunivo_writer/services/rtf/` | `src/lunivo_writer/dienste/rtf/` | 8 |
| `src/lunivo_writer/ui/` | `src/lunivo_writer/oberflaeche/` | 7 |
| `src/lunivo_writer/ui/baukasten/` | `src/lunivo_writer/oberflaeche/baukasten/` | 1 |
| `src/lunivo_writer/ui/baukasten/basis/` | `src/lunivo_writer/oberflaeche/baukasten/basis/` | 9 |
| `src/lunivo_writer/ui/baukasten/chat/` | `src/lunivo_writer/oberflaeche/baukasten/chat/` | 6 |
| `src/lunivo_writer/ui/baukasten/controls/` | `src/lunivo_writer/oberflaeche/baukasten/felder/` | 15 |
| `src/lunivo_writer/ui/baukasten/diagramme/` | `src/lunivo_writer/oberflaeche/baukasten/diagramme/` | 7 |
| `src/lunivo_writer/ui/baukasten/dokument/` | `src/lunivo_writer/oberflaeche/baukasten/dokument/` | 16 |
| `src/lunivo_writer/ui/baukasten/dropdown/` | `src/lunivo_writer/oberflaeche/baukasten/dropdown/` | 14 |
| `src/lunivo_writer/ui/baukasten/dropdown/auswahl/` | `src/lunivo_writer/oberflaeche/baukasten/dropdown/auswahl/` | 6 |
| `src/lunivo_writer/ui/baukasten/dropdown/objektmenues/` | `src/lunivo_writer/oberflaeche/baukasten/dropdown/objektmenues/` | 9 |
| `src/lunivo_writer/ui/baukasten/formatierung/` | `src/lunivo_writer/oberflaeche/baukasten/formatierung/` | 15 |
| `src/lunivo_writer/ui/baukasten/geruest/` | `src/lunivo_writer/oberflaeche/baukasten/geruest/` | 11 |
| `src/lunivo_writer/ui/baukasten/medien/` | `src/lunivo_writer/oberflaeche/baukasten/medien/` | 9 |
| `src/lunivo_writer/ui/baukasten/vorlagen/` | `src/lunivo_writer/oberflaeche/baukasten/vorlagen/` | 4 |
| `src/lunivo_writer/ui/contextual/` | `src/lunivo_writer/oberflaeche/kontext/` | 7 |
| `src/lunivo_writer/ui/dialogs/` | `src/lunivo_writer/oberflaeche/dialoge/` | 6 |
| `src/lunivo_writer/ui/dialogs/einfuegen/` | `src/lunivo_writer/oberflaeche/dialoge/einfuegen/` | 8 |
| `src/lunivo_writer/ui/dialogs/ki/` | `src/lunivo_writer/oberflaeche/dialoge/ki/` | 4 |
| `src/lunivo_writer/ui/dialogs/lesen_hilfe/` | `src/lunivo_writer/oberflaeche/dialoge/lesen_hilfe/` | 4 |
| `src/lunivo_writer/ui/dialogs/optionen_seiten/` | `src/lunivo_writer/oberflaeche/dialoge/optionen_seiten/` | 7 |
| `src/lunivo_writer/ui/dialogs/sendungen/` | `src/lunivo_writer/oberflaeche/dialoge/sendungen/` | 2 |
| `src/lunivo_writer/ui/dialogs/verweise/` | `src/lunivo_writer/oberflaeche/dialoge/verweise/` | 2 |
| `src/lunivo_writer/ui/document/` | `src/lunivo_writer/oberflaeche/dokument/` | 1 |
| `src/lunivo_writer/ui/document/ansicht/` | `src/lunivo_writer/oberflaeche/dokument/ansicht/` | 5 |
| `src/lunivo_writer/ui/document/bearbeitung/` | `src/lunivo_writer/oberflaeche/dokument/bearbeitung/` | 22 |
| `src/lunivo_writer/ui/document/dokumentfenster/` | `src/lunivo_writer/oberflaeche/dokument/dokumentfenster/` | 4 |
| `src/lunivo_writer/ui/document/kopffuss/` | `src/lunivo_writer/oberflaeche/dokument/kopffuss/` | 3 |
| `src/lunivo_writer/ui/document/tabelle/` | `src/lunivo_writer/oberflaeche/dokument/tabelle/` | 3 |
| `src/lunivo_writer/ui/hauptfenster/` | `src/lunivo_writer/oberflaeche/hauptfenster/` | 19 |
| `src/lunivo_writer/ui/ribbon/` | `src/lunivo_writer/oberflaeche/band/` | 13 |
| `src/lunivo_writer/ui/ribbon/tabs/` | `src/lunivo_writer/oberflaeche/band/reiter/` | 12 |
| `src/lunivo_writer/ui/sidebar/` | `src/lunivo_writer/oberflaeche/seitenleiste/` | 2 |
| `src/lunivo_writer/ui/sidebar/panels/` | `src/lunivo_writer/oberflaeche/seitenleiste/panels/` | 3 |
| `src/lunivo_writer/ui/statusbar/` | `src/lunivo_writer/oberflaeche/statusleiste/` | 2 |
| `src/lunivo_writer/ui/widgets/` | `src/lunivo_writer/oberflaeche/bauteile/` | 8 |
| `tests/proofing/` | `tests/korrektur/` | 10 |
| `werkzeug/bauen/` | `werkzeuge/erstellung/` | 7 |
| `werkzeug/git-haken/` | `werkzeuge/git_haken/` | 1 |
| `werkzeug/` | `werkzeuge/` | 1 |
| `werkzeug/pruefen/` | `werkzeuge/pruefungen/` | 12 |
| `werkzeug/symbole/` | `werkzeuge/symbole/` | 5 |

## Angepasste Verweise

- **Python-Importe:** rund 3800 Importzeilen in `src/`, `tests/` und `werkzeuge/` auf die neuen Modulnamen umgestellt, ebenso Modulnamen in Zeichenketten (`__import__`, `importlib`, `monkeypatch`). Wo ein Modul unter seinem Namen importiert wird (`from … import theme`), heißt es jetzt auch im Code deutsch (`thema`, `symbole`, `pfade`, `datei_dienst` …). In acht Dateien blieb der alte Kurzname als Alias stehen (`symbole as icons`, `pfade as paths`, `thema as theme`), weil der neue Name dort schon für etwas anderes vergeben ist.
- **Ressourcenpfade:** `kern/pfade.py` (Ordner `ressourcen`), `baukasten/medien/datei_symbole.py` (`dateitypen`), `pyproject.toml` (Paketdaten `ressourcen/*`).
- **Skripte:** `skripte/starten-qt.sh` findet den Projektordner jetzt eine Ebene höher; Menüeintrag und Symbolpfad angepasst. `werkzeuge/erstellung/deb-bauen.sh` kopiert `ressourcen/` und schreibt das Paket nach `erstellung/` (vorher `build/`, steht in `.gitignore`). `werkzeuge/haken-an.sh` zeigt auf `werkzeuge/git_haken`.
- **Werkzeuge:** Ausgabeziele auf `dokumentation/…` umgestellt (Inventar, Dropdown-Bestand, Funktionsstand, Seitenleistenstand, Menüstruktur, Kontaktbogen, Bildschirmfotos, Titelbild).
- **Tests:** Pfadangaben in `test_schichten.py`, `test_programmfenster.py`, `test_importpfade.py`, `test_werkzeuge.py`, `test_speichern_sicher.py`, `test_docx_korpus.py`, `test_silben_de.py`.
- **Dokumentation:** alle Pfadangaben und Verweise in `README.md`, `CLAUDE.md`, `.claude/agents/`, `dokumentation/` und im eingebauten Handbuch. `interne-funktionen.md` und `dropdown-bestand.md` wurden mit ihren Werkzeugen neu erzeugt.

## Prüfergebnisse

| Prüfung | Ergebnis |
|---|---|
| Alle Python-Dateien übersetzen (`compileall`) | ohne Fehler |
| Alle 521 Module von `lunivo_writer` einzeln importieren | 0 Fehler |
| `werkzeuge/pruefungen/importpruefung.py` | 0 Importfehler, 0 unbekannte Pfade |
| pytest: alle Testdateien einsammeln (ohne Ausführung) | 1203 Tests gefunden, 0 Fehler |
| Gezielte Tests (Plattform, Schichten, Wächtertest „kein HTML“, Dropdown-Paket, Werkzeuge, Dateisymbole, DOCX-Korpus, Silben, Seitenleisten-Fenster, Start-Reiter, Schnelltest Befehle) | 205 bestanden, 1 übersprungen |
| Programmstart ohne Bildschirm über `skripte/starten-qt.sh` und `main.py` | läuft, kein Absturz |
| Ressourcen (Register, Handbuch, Wörter, Symbole, Programmsymbol, Dateitypen) | gefunden |
| Verweise in allen Markdown-Dateien | 113 geprüft, 110 gültig; 3 sind GitHub-Verweise (Fehler melden, Wunsch, Diskussionen), die nur auf der GitHub-Seite gelten |
| Suche nach alten Pfaden im ganzen Projekt | keine Treffer |
| Shell-Skripte (Syntax), `pre-commit` direkt ausgeführt | in Ordnung |

Nicht geprüft: die vollständige Testsuite (laut Projektregel kein lokaler Volltest; es liefen 205 von 1203 Tests) und der echte Bau der `.deb` (braucht Internet und lädt mehrere hundert MB; nur Syntax geprüft).

## Nachbereinigung (2026-11-11)

- **CI wieder da:** `.github/` (Workflow `pruefen.yml`, Mitmach-Regeln, Vorlagen für Fehler und Wünsche) aus `main` übernommen und auf die neuen Pfade umgestellt. `ruff check .` läuft lokal ohne Fehler.
- **Fehlender Import behoben:** `kern/befehle/kontextreiter/bildtools.py` benutzte `QUrl` ohne Import; die CI wäre daran gescheitert.
- **Git-Haken entfernt:** `werkzeuge/haken-an.sh` und `werkzeuge/git_haken/pre-commit`. Der Haken prüfte nur JavaScript-Dateien und rief `namen-pruefen.py` auf; beides gibt es im Projekt nicht, er endete immer ohne Prüfung.
- **`werkzeuge/symbole/symbol-waehlen.sh` entfernt:** Es kopierte nach `symbole/` im Hauptordner und rief `starten.sh --nur-eintrag` auf; beides gibt es nicht, und das Programm liest sein Symbol fest aus `ressourcen/symbole/varianten/Abstrakt`.
- **Menüeintrag:** `~/.local/share/applications/lunivo-office-alt.desktop` zeigt jetzt auf `skripte/starten-qt.sh` und das Symbol unter `ressourcen/`.
- **`analyse/`:** steht in `.gitignore` (Ausgaben von radon, ruff, vulture); die Dateien selbst sind unberührt.

Die drei entfernten Dateien liegen weiter im Verlauf (Commit `f02438d`).

## Offene Punkte

1. **Vollständige Testsuite:** lokal nicht gelaufen (Projektregel). Sie läuft in der CI, sobald der Branch gepusht wird.
2. **Bau der `.deb`:** nicht ausgeführt (braucht Internet und lädt mehrere hundert MB); nur die Syntax des Skripts ist geprüft.
3. **`werkzeuge/pruefungen/pruefbogen_zuordnung_bauen.py`:** enthält alte Herkunftsangaben wie `widgets/register_band.py` als Textdaten; unverändert gelassen.
4. **`CLAUDE.md`:** Der Satz „Das Projekt liegt nicht unter Git“ stimmt nicht mehr; nicht geändert, weil es eine Eigentümer-Regel ist.
