"""Gemeinsame Hilfen der Prüfwerkzeuge in ``werkzeug/`` (``funktionspruefung.py``, ``seitenleistenpruefung.py``): Umgebung ohne Bildschirm, ein Fenster
aufbauen und sauber schließen, ein Wächter, der aufgehende Dialoge und Menüs schließt, und kleine Bausteine für Markdown-Berichte.

Keine Oberfläche, kein HTML; nur Qt-Widgets ohne Bildschirm (``QT_QPA_PLATFORM=offscreen``).
"""
from __future__ import annotations

import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.dirname(HIER)
sys.path.insert(0, os.path.join(WURZEL, "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSettings, QStandardPaths, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication, QDialog, QMenu, QMessageBox  # noqa: E402


def app_starten(name: str = "lunivo-writer-pruefung") -> QApplication:
    """Die Qt-Anwendung (einmalig) mit Testpfaden für die Einstellungen."""
    app = QApplication.instance() or QApplication([])
    QStandardPaths.setTestModeEnabled(True)
    app.setApplicationName(name); app.setOrganizationName("lunivo-pruefung")
    return app


def fenster_bauen(tmp: str, breite: int = 1500, hoehe: int = 900):
    """Ein Hauptfenster mit leerem Dokument und eigener Einstellungsdatei in ``tmp``, sichtbar (ohne Bildschirm)."""
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(os.path.join(tmp, "s.ini"), QSettings.IniFormat)))
    w.new_document(); w.resize(breite, hoehe); w.show()
    QApplication.instance().processEvents()
    return w


def fenster_schliessen(w) -> None:
    """Ohne Änderungsmarke schließen, sonst fragt das Fenster nach dem Speichern."""
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def menue_eintraege(m: QMenu, tiefe: int = 0) -> list[str]:
    """Die Texte aller Einträge eines Menüs (Untermenüs eingerückt)."""
    out = []
    for a in m.actions():
        if a.isSeparator() or not a.text().strip():
            continue
        out.append(a.text().replace("&", "").split("\t")[0])
        if a.menu() is not None and tiefe < 3:
            out += ["  " + t for t in menue_eintraege(a.menu(), tiefe + 1)]
    return out


class DialogWaechter:
    """Schließt Fenster, die auf Eingaben warten (Dialoge, Meldungen, Dateifenster, aufgeklappte Menüs). ``takt()`` regelmäßig aufrufen (QTimer).
    ``modus_ok``: Lunivos eigene Dialoge mit OK (True) oder Abbrechen (False) schließen; Meldungs- und Dateifenster werden immer abgebrochen.
    Was aufging, steht in ``fenster_log``."""

    def __init__(self) -> None:
        self.fenster_log: list[str] = []
        self.modus_ok = False

    def starten(self, ms: int = 30) -> QTimer:
        self.uhr = QTimer(); self.uhr.setInterval(ms); self.uhr.timeout.connect(self.takt); self.uhr.start()
        return self.uhr

    def takt(self) -> None:
        # Dialoge, die nach OK noch offen sind (etwa weil sie eine Warnung zeigten), werden nach einigen Takten abgebrochen
        for x in QApplication.topLevelWidgets():
            if isinstance(x, QDialog) and x.isVisible() and x.property("geprueft"):
                n = int(x.property("takte") or 0) + 1
                x.setProperty("takte", n)
                if n == 5:
                    self.fenster_log.append(f"{type(x).__name__}: {x.windowTitle()} (blieb nach OK offen)")
                    QTimer.singleShot(0, x.reject)
        sichtbar = [x for x in QApplication.topLevelWidgets() if isinstance(x, QDialog) and x.isVisible() and not x.property("geprueft")]
        fremd = [x for x in sichtbar if not type(x).__module__.startswith("lunivo_writer")]
        for x in (fremd or sichtbar):                              # zuerst Meldungs- und Dateifenster, erst dann Lunivos eigene Dialoge
            x.setProperty("geprueft", True)
            self.fenster_log.append(f"{type(x).__name__}: {x.windowTitle()}" + (f" — {x.text()[:80]}" if isinstance(x, QMessageBox) else ""))
            if self.modus_ok and x in sichtbar and x not in fremd:
                QTimer.singleShot(0, x.accept)                     # nicht im Wächter selbst: eine Warnung dabei muss er schließen können
            else:
                QTimer.singleShot(0, x.reject)
        for x in QApplication.topLevelWidgets():
            if isinstance(x, QMenu) and x.isVisible() and x.parent() is None:
                x.close()
        pop = QApplication.activePopupWidget()                      # auch aufgeklappte Menüs, die einem Knopf gehören
        if pop is not None:
            pop.close()


def md_zelle(text) -> str:
    """Text für eine Tabellenzelle in Markdown (kein senkrechter Strich, keine Zeilenumbrüche)."""
    return str(text).replace("|", "/").replace("\n", " ").strip()


def md_tabelle(kopf: list[str], zeilen: list[list]) -> list[str]:
    """Zeilen einer Markdown-Tabelle."""
    out = ["| " + " | ".join(kopf) + " |", "|" + "---|" * len(kopf)]
    out += ["| " + " | ".join(md_zelle(z) for z in zeile) + " |" for zeile in zeilen]
    return out
