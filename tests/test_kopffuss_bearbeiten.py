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
    for z, text in (("kopf", "Kopfzeile"), ("fuss", "Fußzeile")):                 # wie in der Vorlage: beide Bereiche zugleich
        assert b.felder[z].isVisible() and b.linien[z].isVisible() and b.etiketten[z].isVisible() and b.etiketten[z].text() == text
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
    assert b.feld.text_lesen() == "Gerade" and b.etiketten["kopf"].text() == "Kopfzeile gerader Seiten"
    b.starte("kopf", 0)
    assert b.feld.text_lesen() == "Ungerade" and b.etiketten["kopf"].text() == "Kopfzeile ungerader Seiten"
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


def test_feld_hintergrund_ist_im_dunklen_thema_hell(app, tmp_path):
    """Das Feld sitzt auf dem weißen Papier: Palette hell/schwarz, auch wenn das Programm dunkel ist."""
    from PySide6.QtGui import QPalette
    w = _fenster(app, tmp_path)
    w.befehle.tun("kopfFussZeigen")
    f = w.current_editor().kopffuss().feld
    assert f.palette().color(QPalette.Base).lightness() > 200
    assert f.palette().color(QPalette.Text).lightness() < 60
    w.befehle.tun("kopfFussSchliessen")


def test_ohne_seitenzahl_nur_einfuegen_knopf_und_einfuegen_setzt_zahl(app, tmp_path):
    w = _fenster(app, tmp_path)
    w.befehle.tun("kopfFussZeigen")
    b = w.current_editor().kopffuss()
    assert b.leiste.knopf["einfuegen"].isVisibleTo(b.leiste) and not b.leiste.knopf["neu"].isVisibleTo(b.leiste)
    b.seitenzahl_einfuegen("center", "{PAGE}", "dezimal", "abschnitt")
    assert "{PAGE}" in b.hf().text and b.hf().align == "center"
    assert b.leiste.knopf["neu"].isVisibleTo(b.leiste) and not b.leiste.knopf["einfuegen"].isVisibleTo(b.leiste)
    w.befehle.tun("kopfFussSchliessen")


def test_fussfeld_tippen_wechseln_und_leiste_zieht_mit(app, tmp_path):
    w = _fenster(app, tmp_path)
    w.befehle.tun("kopfFussZeigen")
    e = w.current_editor(); b = e.kopffuss()
    kopf, fuss = b.felder["kopf"], b.felder["fuss"]
    assert b.zone == "kopf" and kopf.geometry().bottom() < fuss.geometry().top()
    assert b.leiste.y() > kopf.geometry().bottom() and b.leiste.x() > b.etiketten["kopf"].geometry().right()
    # Klick ins Fußfeld: Leiste und Zone wechseln dorthin (Leiste neben dem Etikett über der Fußlinie)
    QTest.mouseClick(fuss, __import__("PySide6.QtCore", fromlist=["Qt"]).Qt.LeftButton)
    app.processEvents()
    assert b.zone == "fuss" and b.feld is fuss
    assert b.leiste.y() < fuss.geometry().top() and b.etiketten["fuss"].geometry().bottom() < fuss.geometry().top()
    QTest.keyClicks(fuss, "Mein Fuß")
    QTest.keyClicks(kopf, "Mein Kopf")
    QTest.qWait(400)
    pg = e.abschnitt_seite()
    assert pg.footer.text == "Mein Fuß" and pg.header.text == "Mein Kopf"
    b.wechseln()
    assert b.zone == "kopf" and b.leiste.y() > kopf.geometry().bottom()
    b.wechseln()
    assert b.zone == "fuss" and fuss.hasFocus() and b.leiste.y() < fuss.geometry().top()
    b.beende()
    assert not fuss.isVisible() and not b.etiketten["fuss"].isVisible()
