# Aufbau und aktueller Quellcode

Diese Seite verweist auf die aktuellen Quellen statt eine zweite, manuell gepflegte Kopie der Register- und Optionsstruktur zu führen.

## Oberfläche

- [Aufbau des Bandes](aufbau-band.md) beschreibt die zehn Reiter, die Kontext-Reiter und ihre Befehle (standardmäßig sind acht Reiter sichtbar).
- [Aufbau der Optionen](aufbau-optionen.md) beschreibt die sechs Optionsseiten.
- [Baukasten der Oberfläche](../entwicklung/baukasten.md) dokumentiert wiederverwendete Qt-Widgets.

## Quellcode

- Registerdefinitionen: `src/lunivo_writer/ressourcen/register.json`
- Registermodule: `src/lunivo_writer/oberflaeche/band/reiter/`; Kontext-Reiter: `src/lunivo_writer/oberflaeche/kontext/`; Zusammenbau: `src/lunivo_writer/oberflaeche/band/plan.py`
- Optionen: `src/lunivo_writer/oberflaeche/dialoge/optionen.py` und `optionen_seiten/`
- Dokumentoperationen: `src/lunivo_writer/editor/`.
- Der Qt-Editor liegt in `src/lunivo_writer/oberflaeche/dokument/bearbeitung/dokument_editor.py`; Einfügen aus der Zwischenablage und Einfügevarianten sind in `editor_einfuegen.py` gekapselt.
- Zeichenformatierung, Absatz-/Listenformatierung, Formatvorlagen sowie Einfüge-/Suchwerkzeuge des Editors sind in `editor_zeichenformat.py`, `editor_absatzformat.py`, `editor_stilformat.py` und `editor_werkzeuge.py` getrennt; `editor_formatierung.py` bleibt als kompatible Fassade bestehen.
- Synchronisierung von Dokument, Ribbon und Statusleiste liegt in `src/lunivo_writer/oberflaeche/hauptfenster/dokument_sync.py`; `oberflaeche/programmfenster.py` bindet diese Verantwortlichkeit über einen Mixin ein.
- Der KI-Dienst ist in `src/lunivo_writer/ki/` fachlich getrennt: `ki_anfragen.py` (Kontext, Einwilligung und Hintergrundaufträge), `ki_aktionen.py` (Textaktionen), `ki_dauerbetrieb.py` (laufende Assistenz), `ki_chat.py` (Chat und Antwortbezug) sowie `arbeitslauf.py` (Worker). `ki_dienst.py` bleibt die öffentliche `KIDienst`-Fassade.
- Bandbefehle für Zeichen, Absatz und Formatvorlagen sind in `kern/befehle/hauptreiter/text_zeichen.py`, `text_absatz.py` und `text_vorlagen.py` getrennt; `kern/befehle/hauptreiter/text.py` bleibt als kompatible Fassade bestehen.
- Dateiformate und Einstellungen: `src/lunivo_writer/dienste/`

Die übergeordneten Modulgrenzen sind in [Projektaufbau](../README.md) erklärt.
