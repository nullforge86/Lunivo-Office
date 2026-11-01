#!/usr/bin/env python3
"""Bestandsinventar der Funktionssymbole (Auftrag Phase 2):  python3 werkzeug/icon-inventar.py

Liest assets/icons/symbole.json (so wie im Programm), durchsucht src/ nach Verwendungen und schreibt docs/entwicklung/icon-inventar.md.
Verwendung = Textstelle mit dem Symbolnamen als Zeichenkette (Näherung: kann auch Nicht-Symbol-Treffer enthalten, daher „Treffer“).
Funktionsname = Beschriftung aus den Registerdefinitionen (`_k("symbol", "Beschriftung"`/`k(...)`) oder der Schnellzugriffsliste. Kein HTML."""
import itertools
import json
import os
import re
import sys
from collections import defaultdict

W = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(W, "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QByteArray, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QImage, QPainter  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from lunivo_writer.ui.widgets import icons  # noqa: E402


def maske(pfad):
    img = QImage(16, 16, QImage.Format_ARGB32_Premultiplied)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    QSvgRenderer(QByteArray(icons._svg(pfad, "#000000"))).render(p, QRectF(0, 0, 16, 16))
    p.end()
    return tuple(img.pixelColor(x, y).alpha() > 90 for y in range(16) for x in range(16))


def main():
    sym = json.load(open(os.path.join(W, "assets", "icons", "symbole.json"), encoding="utf-8"))
    kat = json.load(open(os.path.join(W, "assets", "icons", "symbolkatalog.json"), encoding="utf-8"))
    katpfade = set(kat.values())
    orte, label, alle_k = defaultdict(set), {}, {}
    quell = []
    for r, _, fs in os.walk(os.path.join(W, "src")):
        for f in fs:
            if f.endswith(".py") and f != "icons.py":
                quell.append(os.path.join(r, f))
    for pf in quell:
        t = open(pf, encoding="utf-8").read()
        rel = os.path.relpath(pf, os.path.join(W, "src", "lunivo_writer"))
        for m in re.finditer(r'\b_?k\(\s*"([A-Za-z0-9_]+)"\s*,\s*"([^"]+)"', t):
            alle_k.setdefault(m.group(1), m.group(2))
            if m.group(1) in sym:
                label.setdefault(m.group(1), m.group(2))
        for m in re.finditer(r'\(\s*"([A-Za-z0-9_]+)"\s*,\s*"([^"]{2,40})"\s*,\s*"[A-Za-z0-9_]+"\s*\)', t):
            if m.group(1) in sym and "ribbon_bar" in pf:
                label.setdefault(m.group(1), m.group(2))
        for n in set(re.findall(r'["\']([A-Za-z0-9_]+)["\']', t)):
            if n in sym:
                orte[n].add(rel)
    namen = sorted(sym, key=str.lower)
    m = {n: maske(sym[n]) for n in namen}
    nah = {}
    for n in namen:
        b = (0.0, "")
        for o in namen:
            if o != n:
                u = sum(1 for a, c in zip(m[n], m[o]) if a or c)
                v = sum(1 for a, c in zip(m[n], m[o]) if a and c) / u if u else 0
                if v > b[0]:
                    b = (v, o)
        nah[n] = b
    gleich = defaultdict(list)
    for n in namen:
        gleich[sym[n]].append(n)
    zeilen, ungenutzt = [], []
    for n in namen:
        o = sorted(orte.get(n, []))
        herk = "Lucide-Katalog (unverändert)" if sym[n] in katpfade else "aus Lucide abgeleitet/eigene Zeichnung (Pfad nicht im Katalog)"
        probleme = []
        if len(gleich[sym[n]]) > 1:
            probleme.append("Mehrfachbelegung: " + ", ".join(x for x in gleich[sym[n]] if x != n))
        elif nah[n][0] >= 0.8:
            probleme.append(f"Verwechslung mit {nah[n][1]} ({nah[n][0]:.2f})")
        if not o:
            ungenutzt.append(n)
        gr = []
        if n in label:
            gr.append("Band 28 oder 18")
        if o:
            gr.append("Menü/Dialog 16–20 (nach Code)")
        zeilen.append(f"| {n} | `assets/icons/symbole.json` › `{n}` (kein Einzel-SVG) | {label.get(n, 'nicht ermittelbar')} | "
                      f"{', '.join(o[:3])}{' …(' + str(len(o)) + ')' if len(o) > 3 else ''} | {'; '.join(gr) or '—'} | {herk} | {'; '.join(probleme) or '—'} |")
    ft = sorted(os.listdir(os.path.join(W, "assets", "icons", "filetypes")))
    var = os.path.join(W, "assets", "symbole", "varianten")
    kopf = ["# Icon-Inventar (Bestand vor Überarbeitung)", "",
            "Erzeugt mit `werkzeug/icon-inventar.py` aus `assets/icons/symbole.json` (Stand HEAD) und `src/`. **Status: ABGESCHLOSSEN (Erfassung), Bewertung siehe Bericht.**", "",
            "## Speicherorte (tatsächlich geprüft)",
            "- Funktionssymbole: `assets/icons/symbole.json` — Name → ein 24×24-Pfad (kein SVG je Symbol). Rendering `src/lunivo_writer/ui/widgets/icons.py` (QSvgRenderer, Strich 1,5, Palettenfarbe).",
            f"- Allgemeine Bibliothek: `assets/icons/symbolkatalog.json` — {len(kat)} Lucide-Pfade (Symbol austauschen, Piktogramm einfügen).",
            f"- Dateitypsymbole: `assets/icons/filetypes/` — {len([f for f in ft if f.endswith('.svg')])} SVG ({', '.join(f[:-4] for f in ft if f.endswith('.svg'))}).",
            f"- Programm-/App-Symbole (dekorativ, nicht Teil des Funktionssatzes): `assets/symbole/varianten/` — {sum(len(fs) for _, _, fs in os.walk(var))} Dateien (PNG/SVG).",
            "- Lizenz: `assets/icons/LIZENZ-LUCIDE.txt` (ISC).", "",
            "## Zusammenfassung",
            f"- Funktionssymbole: {len(namen)}; davon ohne Textfundstelle im Code (Zuordnung über `nimm(…)`/dynamische Namen nicht erfasst – „nicht verwendet“ also NICHT PRÜFBAR ohne Laufzeitprüfung): {len(ungenutzt)}: {', '.join(ungenutzt)}.",
            f"- Gleiche Zeichnung unter mehreren Namen (Mehrfachbelegung): {sum(1 for v in gleich.values() if len(v) > 1)} Gruppen.",
            "- Darstellungsgrößen im Code: Band groß 28 px, Band klein/Menüs/Schnellzugriff 18 px, Menüknopf 16 px, Auswahlpfeil 14 px, Dialoge 16–24 px (`setIconSize`-Auswertung); Rendering immer mit Faktor 2 (HiDPI).",
            "- Tooltips/Accessible Names: im Code 241 Stellen mit `setToolTip`/`setAccessibleName`; die Schnellzugriffsleiste setzt Tooltips (`ribbon_bar.py`). Vollständigkeit je Knopf **NICHT PRÜFBAR ohne Laufzeitprüfung** (Oberfläche nicht gestartet).", "",
            "## Funktionen im Band ohne eigenes Funktionssymbol (Symbolname weder in symbole.json noch im Katalog)",
            ", ".join(f"{k} („{v}“)" for k, v in sorted(alle_k.items()) if k not in sym and k not in kat) or "keine gefunden (Erfassung nur über `_k(\"symbol\", \"Beschriftung\")`; `nimm(…)`-Einträge nicht erfasst)", "",
            "## Matrix", "",
            "| Name | Speicherort | Funktion (Beschriftung) | Einsatzorte (Dateien, Treffer) | Größen | Herkunft | Probleme / Mehrfachbelegung / Verwechslung |", "|---|---|---|---|---|---|---|"]
    open(os.path.join(W, "docs", "entwicklung", "icon-inventar.md"), "w", encoding="utf-8").write("\n".join(kopf + zeilen) + "\n")
    print(len(namen), "Symbole;", len(ungenutzt), "ohne Fundstelle;", len(label), "mit Beschriftung")


if __name__ == "__main__":
    QApplication([])
    main()
