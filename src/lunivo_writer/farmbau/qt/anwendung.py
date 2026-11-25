"""Qt-Komposition: QApplication, Übersetzung, Theme und Hauptfenster."""
from __future__ import annotations
import os
from PySide6.QtCore import QEvent, QLibraryInfo, QSize, QTranslator
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from lunivo_writer.dienste.einstellungen_dienst import APP_NAME, APP_ORG, Settings
from lunivo_writer.oberflaeche.programmfenster import MainWindow
from lunivo_writer.oberflaeche.thema import apply_theme
from lunivo_writer.plattform import protokoll

def programm_symbol() -> QIcon:
    from lunivo_writer.kern.pfade import ASSETS
    ordner = os.path.join(ASSETS, "symbole", "varianten", "Abstrakt")
    symbol = QIcon()
    for px in (16, 24, 32, 48, 128, 256):
        datei = os.path.join(ordner, f"icon-{px}.png")
        if os.path.exists(datei):
            symbol.addFile(datei, QSize(px, px))
    return symbol

class LunivoQtApplication:
    """Qt-Lebenszyklus; bewusst nicht im fachlichen core."""
    def __init__(self, argv: list[str]):
        self.argv = argv
        self.app = QApplication(argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setOrganizationName(APP_ORG)
        self.app.setDesktopFileName("lunivo-writer")
        protokoll.einrichten()
        self.app.setWindowIcon(programm_symbol())
        self._uebersetzer: list[QTranslator] = []
        for name in ("qtbase_de", "qt_de"):
            translator = QTranslator()
            if translator.load(name, QLibraryInfo.path(QLibraryInfo.TranslationsPath)):
                self.app.installTranslator(translator)
                self._uebersetzer.append(translator)
        self.settings = Settings()
        from lunivo_writer.oberflaeche import thema
        thema.WEICH = self.settings.get_bool("ui/weich", False)
        apply_theme(self.app, self.settings.get("theme", "system"))
        from lunivo_writer.oberflaeche.baukasten.geruest.zugaenglichkeit import NamenFilter
        NamenFilter.einhaengen(self.app)
        self.fenster = MainWindow(self.settings)

    def start(self) -> int:
        win = self.fenster
        win.show()
        dateien = [a for a in self.argv[1:] if not a.startswith("-")]
        for datei in dateien:
            win.open_path(datei)
        if not dateien:
            win.offer_recovery()
        if not dateien and win.tabs.count() == 0 and self.settings.get_bool("start/letztes_oeffnen", False):
            letztes = next((pfad for pfad in self.settings.recent() if os.path.exists(pfad)), None)
            if letztes:
                win.open_path(letztes)
        if win.tabs.count() == 0:
            win.new_document()
        rc = self.app.exec()
        self._abbauen()
        return rc

    def _abbauen(self) -> None:
        self.fenster.deleteLater()
        self.app.sendPostedEvents(None, QEvent.DeferredDelete)
        self.app.processEvents()
        self.fenster = None
