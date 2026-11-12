"""SmartArt-Fenster: Galerie der Layouts, Beschreibung, nichts ragt in der Seitenleiste heraus."""
import pytest
from PySide6.QtWidgets import QWidget

from lunivo_writer.editor.objekte import smartart as SA
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import ZusatzPanel
from lunivo_writer.oberflaeche.dialoge.einfuegen.einfuegen_dialoge import SmartArtDialog


@pytest.mark.parametrize("breite", [300, 444])
def test_nichts_ragt_heraus(app, breite):
    p = ZusatzPanel(); p.verfuegbar, p.verfuegbar_hoehe = breite, 587; p.resize(breite + 36, 727)
    d = SmartArtDialog(None); p.oeffne(d); p.show(); app.processEvents(); app.processEvents()
    for w in d.findChildren(QWidget):
        if w.isVisible():
            r = w.mapTo(d, w.rect().bottomRight())
            assert r.x() <= d.width() + 1, (type(w).__name__, r.x(), d.width())
    assert list(d.galerie.feld.knoepfe) == SA.KATALOG_LAYOUTS and len(d.galerie.feld.knoepfe) == 15
    p.close()


def test_auswahl_liefert_layout(app):
    d = SmartArtDialog(None)
    d.galerie.feld.knoepfe["Segmentzyklus"].click()
    assert d.daten()["layout"] == "Segmentzyklus" and d.name.text() == SA.ANZEIGENAMEN["Segmentzyklus"] and d.beschreibung.text()
    assert d.daten()["text"] == SA.MUSTER["Segmentzyklus"]
    assert not d.bearbeiten.isVisibleTo(d)
    e = SmartArtDialog(None, {"layout": "Pyramide", "farben": "Grün", "text": "A\nB"})
    assert e.bearbeiten.isVisibleTo(e) and e.daten() == {"layout": "Pyramide", "farben": "Grün", "text": "A\nB"}


@pytest.fixture
def fenster_kn(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.dienste.einstellungen_dienst import Settings
    from lunivo_writer.oberflaeche.programmfenster import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document(); w.resize(1200, 800); w.show()
    yield w.current_editor(), w.befehle
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def test_knotenmasse_aufzaehlung_und_schnellleiste(fenster_kn):
    from lunivo_writer.editor.objekte import bildlayout as BL
    from lunivo_writer.oberflaeche.baukasten.geruest import schnellleiste_zustand as SZ
    ed, b = fenster_kn
    SA.einfuegen(ed, SA.LAYOUT_KATALOG[0])                                       # Organigramm
    assert b.smartartKnotenMasse() is None and not b.kann_smartartAufzaehlung()
    b.tun('smartartKnotenWaehlen:["k2"]')
    km, om = b.smartartKnotenMasse(), BL.masse_lesen(ed, BL.ziel(ed))
    assert km and 0 < km[0] < om[0] and 0 < km[1] < om[1]                         # Knoten kleiner als das Objekt
    assert not b.kann_smartartAufzaehlung() and b.smartartAufzaehlung() is False  # Organigramm: grau und ohne Wirkung
    assert not SZ.knopf_aktiv(b, "sa_bullet") and SZ.knopf_aktiv(b, "sa_form") and SZ.knopf_aktiv(b, "layout")
    assert SZ.ohne_minus(ed.KNOEPFE_SMARTART, object()) and not SZ.ohne_minus(ed.KNOEPFE_SMARTART_LEER, object())
    assert "minus" not in ed._frei_knopf_rects(ed._frei_knoten_rect() or __import__("PySide6.QtCore").QtCore.QRectF(0, 0, 50, 50))
    SA.aendern(ed, layout="Punktliste")
    assert b.kann_smartartAufzaehlung() and SZ.knopf_aktiv(b, "sa_bullet")
    b.tun('smartartKnotenWaehlen')                                               # Auswahl aufheben: Objektmaße, ⊖ wieder da
    assert b.smartartKnotenMasse() is None and "minus" in ed._frei_knopf_rects(__import__("PySide6.QtCore").QtCore.QRectF(0, 0, 50, 50))


def test_layoutoptionen_vorwahl_smartart_und_form(fenster_kn):
    from lunivo_writer.editor.objekte import bildlayout as BL
    ed, _b = fenster_kn
    SA.einfuegen(ed, SA.LAYOUT_KATALOG[0])
    assert BL.lesen(ed, BL.ziel(ed))["verschieben_wahl"] is None                  # beide Radios leer
    assert BL.verschieben_wahl({"art": "form"}) == "mit_text" and BL.verschieben_wahl({"art": "form", "mit_text": False}) == "fest"


@pytest.mark.parametrize("breite", [300, 444])
def test_foto_dialog_nichts_ragt_heraus(app, breite):
    from lunivo_writer.oberflaeche.dialoge.einfuegen.smartart_dialog_foto import SmartArtDialogFoto
    p = ZusatzPanel(); p.verfuegbar, p.verfuegbar_hoehe = breite, 587; p.resize(breite + 36, 727)
    d = SmartArtDialogFoto(None); p.oeffne(d); p.show(); app.processEvents(); app.processEvents()
    for w in d.findChildren(QWidget):
        if w.isVisible():
            r = w.mapTo(d, w.rect().bottomRight())
            assert r.x() <= d.width() + 1, (type(w).__name__, r.x(), d.width())
    assert d.reiter.tabText(0) == "Alle" and list(d.galerie.feld.knoepfe) == SA.KATALOG_LAYOUTS
    d.galerie.feld.knoepfe["Segmentzyklus"].click()
    assert d.daten()["layout"] == "Segmentzyklus"
    p.close()
