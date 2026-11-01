# Werkzeuge

Entwicklungs- und Prüfhilfen. Sie gehören nicht zur ausgelieferten Anwendung; Aufruf aus dem Projektverzeichnis mit `.venv/bin/python werkzeug/<name>`.

| Skript | Zweck |
|---|---|
| `arbeitsplan-bauen.py` | Aus seinem Prüfbogen einen Arbeitsplan machen. |
| `bildschirmfotos.py` | Nimmt die Bilder der Qt-Oberfläche für das README auf (ohne Bildschirm, QT_QPA_PLATFORM=offscreen). |
| `deb_bauen.py` | Baut genau eine .deb:  python3 werkzeug/deb_bauen.py [--ausgabe VERZEICHNIS] |
| `funktionspruefung.py` | Probiert jeden Knopf und jeden Menüpunkt des Bandes aus und schreibt auf, was wirklich passiert. |
| `haken-an.sh` | (ohne Beschreibung) |
| `icon-zeichner.py` | Icon-Zeichner — ein kleines Programm, um eigene Symbole für Lunivo zu zeichnen (24 × 24, Strichzeichnung wie die Lucide-Symbole). |
| `icon-zeichner.sh` | Startet den Icon-Zeichner (Doppelklick im Dateimanager: „Im Terminal ausführen“ oder „Ausführen“ wählen). |
| `inventar-bauen.py` | Schreibt docs/entwicklung/interne-funktionen.md: Inventar aller Module, Klassen, Funktionen und Methoden von ``src/lunivo_writer``. |
| `menuestruktur-abgleich.py` | Schreibt docs/MENUESTRUKTUR.md: die vorgegebene Menüstruktur (12 Bereiche) Punkt für Punkt gegen das Programm. |
| `pruefbogen-abgleich.py` | Gleicht den Prüfbogen (415 Punkte) mit der nativen Fassung ab → docs/PRUEFBOGEN.md. |
| `pruefbogen-zuordnung-bauen.py` | Schreibt docs/pruefbogen/zuordnung.json — die von Hand begründete Zuordnung Prüfpunkt → native Fassung. |
| `pruefhilfen.py` | Gemeinsame Hilfen der Prüfwerkzeuge in ``werkzeug/`` (``funktionspruefung.py``, ``seitenleistenpruefung.py``): Umgebung ohne Bildschirm, ein Fenster |
| `seitenleistenpruefung.py` | Klickt die Seitenleiste „Formatierung“ automatisch durch, wie ein Tester es von Hand täte, und schreibt auf, was wirklich passiert. |
| `speicherpruefung.py` | Prüft den Speicherweg für alle Formate und schreibt ein Prüfprotokoll in eine SQLite-Datenbank. |
| `stapel-demo.py` | Vorführung: „Neue Formatvorlage“ mit allen Unterfenstern in EINEM Fenster (Fenster-Stapel), ohne die Anwendung. |
| `svg-zu-pfad.py` | Rechnet ein Lucide-SVG in einen einzigen Pfad um. |
| `symbol-uebersicht.py` | Kontaktübersicht der Funktionssymbole als PNG:  python3 werkzeug/symbol-uebersicht.py [Ziel.png] [--dunkel] |
| `symbol-waehlen.sh` | (ohne Beschreibung) |
| `wps-befehle-lesen.py` | Die Befehle des WPS Writer auslesen. |
