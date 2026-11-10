"""Der Neubau des Registerbands darf den unabhängigen Seitenleisten-Zustand nicht zurücksetzen."""
from PySide6.QtCore import QSettings

from lunivo_writer.services.settings_service import Settings
from lunivo_writer.ui.main_window import MainWindow


def test_band_neubau_erhaelt_seitenleiste_und_chat(app, tmp_path):
    settings = Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat))
    fenster = MainWindow(settings)
    fenster.show()
    app.processEvents()

    seitenleiste = fenster.sidebar
    chat = seitenleiste.chat
    seitenleiste.zeige_reiter("Schreiben")
    seitenleiste.zeige_bereich(1)
    app.processEvents()

    fenster.neu_bauen_band()
    app.processEvents()

    assert fenster.sidebar is seitenleiste
    assert seitenleiste.chat is chat
    assert seitenleiste.stapel.currentIndex() == 1
    assert seitenleiste.aktueller_reiter == "Schreiben"
