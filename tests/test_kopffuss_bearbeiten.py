"""Kopf- und Fußzeile direkt auf der Seite bearbeiten: Start, Tippen, Seitenzahl löschen, Schließen."""
from PySide6.QtTest import QTest

from lunivo_writer.models.page import HeaderFooter


def _fenster(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document()
    w.show()
    app.processEvents()
    return w


def _kontext_sichtbar(w):
    i = w.band.kontext_index["kopffuss"]
    return w.band.reiter.isTabVisible(i), w.band.reiter.currentIndex() == i


def test_start_zeigt_feld_und_kontextreiter(app, tmp_path):
    w = _fenster(app, tmp_path)
    w.befehle.tun("kopfFussZeigen")
    b = w.current_editor().kopffuss()
    assert b.aktiv and b.feld.isVisible() and b.leiste.isVisible()
    assert _kontext_sichtbar(w) == (True, True)
    w.befehle.tun("kopfFussSchliessen")
    assert not b.aktiv and not b.feld.isVisible() and _kontext_sichtbar(w)[0] is False


def test_tippen_wird_in_kopfzeile_gespeichert(app, tmp_path):
    w = _fenster(app, tmp_path)
    w.befehle.tun("kopfFussZeigen")
    e = w.current_editor(); b = e.kopffuss()
    QTest.keyClicks(b.feld, "Mein Kopf")
    QTest.qWait(400)
    assert e.abschnitt_seite().header.text == "Mein Kopf"
    b.beende()


def test_seitenzahl_loeschen_gesamtes_dokument(app, tmp_path):
    w = _fenster(app, tmp_path)
    e = w.current_editor()
    pg = e.abschnitt_seite(); pg.footer = HeaderFooter("Seite {PAGE}", "center"); pg.header = HeaderFooter("Kopf {PAGE}", "left")
    e.page_settings_changed(pg)
    w.befehle.tun("fusszeileBearbeiten")
    b = e.kopffuss()
    assert b.seitenzahl_loeschen("dokument") is True
    pg = e.abschnitt_seite()
    assert "{PAGE" not in pg.footer.text and "{PAGE" not in pg.header.text and pg.header.text == "Kopf"
    assert b.seitenzahl_loeschen("dokument") is False
    b.beende()


def test_esc_beendet(app, tmp_path):
    w = _fenster(app, tmp_path)
    w.befehle.tun("kopfFussZeigen")
    b = w.current_editor().kopffuss()
    QTest.keyClick(b.feld, __import__("PySide6.QtCore", fromlist=["Qt"]).Qt.Key_Escape)
    assert not b.aktiv
