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


def test_gerade_seite_zeigt_eigene_kopfzeile(app, tmp_path):
    w = _fenster(app, tmp_path)
    e = w.current_editor()
    pg = e.abschnitt_seite(); pg.header = HeaderFooter("Ungerade", "center")
    e.page_settings_changed(pg)
    w.befehle.tun("geradeUngerade")
    pg = e.abschnitt_seite()
    assert pg.diff_even and pg.even_header.text == "Ungerade"              # zuerst eine Kopie
    pg.even_header = HeaderFooter("Gerade", "center"); e.page_settings_changed(pg)
    b = e.kopffuss()
    b.starte("kopf", 1)                                                     # Blatt 2 = gerade Seite
    assert b.feld.text_lesen() == "Gerade" and b.leiste.etikett.text() == "Kopfzeile gerader Seiten"
    b.starte("kopf", 0)
    assert b.feld.text_lesen() == "Ungerade" and b.leiste.etikett.text() == "Kopfzeile ungerader Seiten"
    b.starte("kopf", 1)
    b.feld.felder_setzen("Neu gerade", {}); b.speichern()
    assert e.abschnitt_seite().even_header.text == "Neu gerade" and e.abschnitt_seite().header.text == "Ungerade"
    b.beende()


def test_feld_zeigt_zahl_und_speichert_platzhalter(app, tmp_path):
    from PySide6.QtCore import Qt
    w = _fenster(app, tmp_path)
    e = w.current_editor()
    pg = e.abschnitt_seite(); pg.footer = HeaderFooter("Seite {PAGE} von {PAGES}", "center")
    e.page_settings_changed(pg)
    w.befehle.tun("fusszeileBearbeiten")
    b = e.kopffuss()
    assert b.feld.toPlainText() == "Seite 1 von 1"
    assert b.feld.text_lesen() == "Seite {PAGE} von {PAGES}"
    # Tippen direkt hinter dem Feld erbt den Feld-Hintergrund nicht
    c = b.feld.textCursor(); c.movePosition(c.MoveOperation.End); b.feld.setTextCursor(c)
    QTest.keyClicks(b.feld, "x")
    assert b.feld.text_lesen() == "Seite {PAGE} von {PAGES}x"
    QTest.keyClick(b.feld, Qt.Key_Backspace)
    QTest.keyClick(b.feld, Qt.Key_Backspace)                                # löscht das Feld {PAGES} als Ganzes
    assert b.feld.text_lesen() == "Seite {PAGE} von "
    b.speichern()
    assert e.abschnitt_seite().footer.text == "Seite {PAGE} von"  or e.abschnitt_seite().footer.text == "Seite {PAGE} von "
    b.beende()
