#!/usr/bin/env python3
"""Prüft die Symbole in der laufenden Oberfläche (ohne Bildschirm):  .venv/bin/python werkzeug/icon-oberflaeche.py

Baut das Hauptfenster in hell und dunkel, nimmt je Register ein Bild des Fensters auf (assets/icons/oberflaeche/) und listet alle
Knöpfe mit Symbol: Beschriftung, Tooltip, Accessible Name, aktiv/deaktiviert, Symbol sichtbar. Ergebnis: docs/entwicklung/icon-oberflaeche.md. Kein HTML."""
import os
import sys
import tempfile

W = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(W, "src"))
sys.path.insert(0, os.path.join(W, "werkzeug"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QSettings, QSize  # noqa: E402
from PySide6.QtWidgets import QApplication, QToolButton, QAbstractButton  # noqa: E402

from lunivo_writer.services.settings_service import Settings  # noqa: E402
from lunivo_writer.ui.main_window import MainWindow  # noqa: E402
from lunivo_writer.ui.theme import apply_theme  # noqa: E402
from lunivo_writer.ui.widgets import icons  # noqa: E402

ZIEL = os.path.join(W, "assets", "icons", "oberflaeche")


def main():
    app = QApplication([])
    os.makedirs(ZIEL, exist_ok=True)
    zeilen, summe = [], {}
    for theme in ("light", "dark"):
        apply_theme(app, theme)
        icons.leeren()
        ini = os.path.join(tempfile.mkdtemp(), "s.ini")
        w = MainWindow(Settings(QSettings(ini, QSettings.IniFormat)))
        w.resize(1500, 900)
        w.show()
        w.new_document()
        app.processEvents()
        r = w.band.reiter
        mit = ohne_tip = leer_icon = gesehen = 0
        for i in range(r.count()):
            name = r.tabText(i)
            r.setCurrentIndex(i)
            for _ in range(5):
                app.processEvents()
            w.grab().save(os.path.join(ZIEL, f"{theme}-{i:02d}-{name}.png"))
            seite = w.band.stapel.currentWidget()
            for b in seite.findChildren(QAbstractButton):
                if b.icon().isNull() or not b.isVisible():
                    continue
                gesehen += 1
                px = b.iconSize() if b.iconSize().isValid() else QSize(16, 16)
                pm = b.icon().pixmap(px)
                sichtbar = (not pm.isNull()) and any(pm.toImage().pixelColor(x, y).alpha() > 40 for x in range(0, pm.width(), 2) for y in range(0, pm.height(), 2))
                tip, acc, txt = b.toolTip().strip(), b.accessibleName().strip(), b.text().strip()
                if theme == "light":
                    sym = b.property("symbolName") or ""
                    zeilen.append((name, txt, tip, acc, b.isEnabled(), f"{px.width()}", sichtbar, sym))
                if not (tip or acc or txt):
                    ohne_tip += 1
                if not sichtbar:
                    leer_icon += 1
        summe[theme] = (gesehen, ohne_tip, leer_icon)
        w.close()
    kopf = ["# Symbole in der laufenden Oberfläche (Phase 10, Laufzeitprüfung)", "",
            "Erzeugt mit `werkzeug/icon-oberflaeche.py` (Qt offscreen). Bilder je Register: `assets/icons/oberflaeche/`.", "",
            "| Thema | Knöpfe mit Symbol | ohne Beschriftung, Tooltip und Accessible Name | Symbol unsichtbar |", "|---|---|---|---|"]
    kopf += [f"| {t} | {a} | {b} | {c} |" for t, (a, b, c) in summe.items()]
    kopf += ["", "Hinweis: Accessible Names setzt Qt aus Beschriftung/Tooltip, soweit nicht gesetzt (hier wird nur das ausdrücklich Gesetzte gezählt).", "",
             "## Knöpfe ohne jede Beschriftung (Hell)", "| Register | Symbol | Größe | aktiv |", "|---|---|---|---|"]
    kopf += [f"| {a} | {h or '?'} | {f} | {e} |" for a, b, c, d, e, f, g, h in zeilen if not (b or c or d)]
    kopf += ["", "## Alle Knöpfe (Hell)", "| Register | Text | Tooltip | Accessible Name | aktiv | Größe | sichtbar | Symbol |", "|---|---|---|---|---|---|---|---|"]
    kopf += [f"| {a} | {b} | {c} | {d} | {e} | {f} | {g} | {h} |" for a, b, c, d, e, f, g, h in zeilen]
    open(os.path.join(W, "docs", "entwicklung", "icon-oberflaeche.md"), "w", encoding="utf-8").write("\n".join(kopf) + "\n")
    print(summe)


if __name__ == "__main__":
    main()
