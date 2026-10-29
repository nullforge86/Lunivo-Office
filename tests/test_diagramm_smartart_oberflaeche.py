"""Oberfläche für Diagramm, Formen und SmartArt: Reiter-Befehle, Popups, Diagrammbereich-Feld, Teilwahl per Maus, Anpassungsgriff, Knotenklick,
Seitenleiste „Formatierung“ für Diagrammteile (nichts ragt bei 300 px heraus)."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
from PySide6.QtCore import QEvent, QPointF, QRectF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QToolButton, QWidget

from lunivo_writer.editor import diagramm as D, formen as F, frei_objekt as FO, smartart as SA
from lunivo_writer.editor import diagramm_teile as T
from lunivo_writer.ui.contextual.image_tools import SMARTARTTOOLS, ZEICHENTOOLS


def _maus(ed, typ, pos):
    e = QMouseEvent(typ, QPointF(pos), QPointF(pos), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    return ed._frei_maus(e, {QEvent.MouseButtonPress: "press", QEvent.MouseMove: "move", QEvent.MouseButtonRelease: "release"}[typ])


def _rect(ed):
    ed._frei_liste()
    return [t for t in ed._frei_treffer if t[0] == ed._frei_sel][0][2]


@pytest.fixture
def fenster(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document(); w.resize(1300, 800); w.show()
    yield w
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def _diagramm(w):
    ed = w.current_editor()
    FO.einfuegen(ed, "diagramm", {"art": "saeule_gruppiert", "titel": "T", "kategorien": list(D.BEISPIEL_KATEGORIEN), "reihen": dict(D.BEISPIEL_REIHEN)}, 480, 300)
    w._sync_format()
    return ed


def test_smartarttools_alle_knoepfe_da(fenster):
    w = fenster; ed = w.current_editor()
    SA.einfuegen(ed, "Organigramm"); w._sync_format()
    i = w.band.kontext_index["smartart"]
    assert w.band.reiter.tabText(i) == "SmartArt-Design" and w.band.reiter.isTabVisible(i)
    seite = w.band.stapel.widget(i)
    for k in seite.findChildren(QToolButton):
        assert not k.property("fehlt"), k.toolTip()
    namen = {k.toolTip() for k in seite.findChildren(QToolButton)}
    assert {"Form einfügen", "Aufzählungszeichen einfügen", "Level erhöhen", "Level reduzieren", "Vorwärts", "Rückwärts", "Layout von rechts nach links",
            "Layout", "Farben ändern"} <= namen
    for e in (e for g in SMARTARTTOOLS["gruppen"] for e in g.get("knoepfe", [])):
        if e.get("tun"):
            assert w.befehle.hat(e["tun"].partition(":")[0])
    assert w.befehle.kann("smartartLevelErhoehen") is not None


def test_popups_bauen_sich(fenster):
    from lunivo_writer.ui.baukasten import diagramm_popups as DP, form_menues as FM, smartart_menues as SM
    w = fenster; b = w.befehle
    _diagramm(w)
    for bau in (DP.elemente_popup, DP.schnelllayout_popup, DP.stile_popup, DP.farben_popup, DP.filter_popup):
        m = bau(b); m.neu_lesen(); assert m.stapel.count() >= 1
    p = DP.stile_popup(b); p.waehle(1)
    assert p.stapel.currentIndex() == 1
    assert len(DP.elemente_popup(b)._seite_elemente().findChildren(type(DP.QCheckBox()))) == 9
    ed = w.current_editor(); SA.einfuegen(ed, "Organigramm")
    for bau in (SM.form_menue, SM.level_menue, SM.hierarchie_menue, SM.layout_menue, SM.stile_menue):
        assert bau(b) is not None
    assert len(SM.stile_galerie(b)["kacheln"]) == 5
    assert len(FM.formstile_galerie(b)["kacheln"]) == 6 and FM.form_bearbeiten_menue(b) is not None
    assert len(SM.layout_menue(b).actions()) == 15
    for k in SA.LAYOUTS:
        assert not SM.miniatur(k, True).isNull() and not SM.miniatur(k, False).isNull()


def test_diagrammbereich_feld_und_teilwahl(fenster):
    w = fenster; ed = _diagramm(w)
    feld = w.band.felder["diagrammBereich"]
    assert feld.feld.count() >= 4 and feld.feld.currentText() == "Diagrammbereich"
    i = feld.feld.findText("Diagrammtitel")
    feld.feld.setCurrentIndex(i); feld.feld.activated.emit(i)
    assert T.teil_name(ed) == "Diagrammtitel"
    w.band.aktualisieren(); assert feld.feld.currentText() == "Diagrammtitel"


def test_klick_ins_diagramm_waehlt_teil_und_aussen_hebt_auf(fenster):
    w = fenster; ed = _diagramm(w)
    r = _rect(ed); a = FO.ziel(ed)[3]
    titel = T.teil_bei  # noqa: F841
    geo = D.teil_rechtecke(FO.daten_lesen(ed, "diagramm"), a["b"], a["h"])
    t = geo["titel"]
    pos = QPointF(r.x() + t.center().x() * r.width() / a["b"], r.y() + t.center().y() * r.height() / a["h"])
    _maus(ed, QEvent.MouseButtonPress, pos); _maus(ed, QEvent.MouseButtonRelease, pos)
    assert T.teil_gewaehlt(ed) == "titel"
    ed.viewport().grab()                                                       # Zeichnen mit Teilrahmen ohne Fehler
    aussen = QPointF(r.right() + 300, r.bottom() + 200)
    _maus(ed, QEvent.MouseButtonPress, aussen)
    assert ed._frei_sel is None


def test_formatierung_diagrammteil_wirkt(fenster, app):
    w = fenster; ed = _diagramm(w)
    T.teil_waehlen(ed, "legende")
    w.diagrammformat_seitenleiste()
    p = w.sidebar.diagramm_panel
    assert p.hauptreiter[0].text() == "LEGENDE OPTIONEN"
    p.farbe.setFarbe("#ff0000"); p.farbe.farbeGeaendert.emit("#ff0000"); app.processEvents()
    assert T.diagramm_teil_format_lesen(ed)["fuell"] == "#ff0000"
    p.s_farbe.farbeGeaendert.emit("#112233"); app.processEvents()                 # ein Regler des Schattens schaltet ihn ein
    assert T.diagramm_teil_format_lesen(ed).get("schatten")
    p.reiter.setCurrentIndex(2); p.o_lage.setCurrentIndex(p.o_lage.findData("links")); app.processEvents()
    assert FO.daten_lesen(ed, "diagramm")["legende_pos"] == "links"
    T.teil_waehlen(ed, "diagrammbereich"); w.diagrammformat_folgen()
    p.alt_titel.setText("Umsatz"); p._alt_timer.timeout.emit()
    assert FO.daten_lesen(ed, "diagramm")["alt_titel"] == "Umsatz"


@pytest.mark.parametrize("breite", [300, 444])
def test_formatpanel_ragt_nicht_heraus(app, breite):
    from lunivo_writer.ui.baukasten.diagramm_format_panel import DiagrammFormatPanel
    from lunivo_writer.ui.baukasten.zusatz_panel import ZusatzPanel
    p = DiagrammFormatPanel(None, {"teil": "titel"}); p.resize(breite, 700); p.show(); app.processEvents()
    for i in range(3):
        p.reiter.setCurrentIndex(i); app.processEvents()
        for wdg in p.findChildren(QWidget):
            if wdg.isVisible():
                x = wdg.mapTo(p, wdg.rect().bottomRight()).x()
                assert x <= p.width() + 1, (type(wdg).__name__, x, p.width())
    p.close()


def test_anpassungsgriff_ziehen_aendert_adj(fenster):
    w = fenster; ed = w.current_editor()
    FO.einfuegen(ed, "form", {"form": "Abgerundetes Rechteck", "fuell": "#4a8fd8", "linie": "#1f3864", "strich": 2.0, "text": ""}, 240, 140)
    d = FO.daten_lesen(ed, "form")
    assert F.anpass_griffe(d["form"], QRectF(0, 0, 1, 1)), "Testform braucht einen Anpassungsgriff"
    r = _rect(ed)
    lagen = ed._frei_adj_lagen(r, FO.ziel(ed)[3])
    assert "adj0" in lagen
    start = lagen["adj0"]; ziel = start + QPointF(25, 0)
    _maus(ed, QEvent.MouseButtonPress, start); _maus(ed, QEvent.MouseMove, ziel); _maus(ed, QEvent.MouseButtonRelease, ziel)
    adj = FO.daten_lesen(ed, "form").get("adj")
    assert adj and abs(adj[0] - F.anpass_wert(d["form"], r, start)) > 0.001
    ed.viewport().grab()


def test_knotenklick_waehlt_knoten_und_tippen_schreibt(fenster):
    w = fenster; ed = w.current_editor()
    SA.einfuegen(ed, "Matrix"); ed._frei_liste()
    ed._frei_sel = [t[0] for t in ed._frei_treffer][-1]
    r = _rect(ed); a = FO.ziel(ed)[3]
    rects = SA.knoten_rechtecke(FO.daten_lesen(ed, "smartart"), a["b"], a["h"])
    ident, rr = next(iter(rects.items()))
    pos = QPointF(r.x() + rr.center().x() * r.width() / a["b"], r.y() + rr.center().y() * r.height() / a["h"])
    _maus(ed, QEvent.MouseButtonPress, pos); _maus(ed, QEvent.MouseButtonRelease, pos)
    assert SA.knoten_gewaehlt(ed) == ident
    assert "sa_form" in ed._frei_knopf_rects(_rect(ed))
    assert ed.frei_knoten_edit_starten("Neu")
    ed._sa_edit[0].editingFinished.emit()
    assert SA.knoten_text(ed, ident) == "Neu"
    ed.viewport().grab()


def test_formstile_raster_ist_eines(fenster):
    from lunivo_writer.ui.baukasten.objekt_menues import formstile, formstil_werte
    assert len(formstile().knoepfe) == 42 and formstil_werte("z12")["fuell"]["art"] == "farbe"
    w = fenster; ed = w.current_editor()
    FO.einfuegen(ed, "form", {"form": "Rechteck", "fuell": "#ffffff", "linie": "#000000", "strich": 1.0, "text": ""}, 200, 120)
    m = ed.frei_formstile_menue(ed); m.gewaehlt.emit("z12")
    assert FO.daten_lesen(ed, "form")["fuell"].lower() == "#f08c00"


def test_zahnrad_oeffnet_formatierung_je_objektart(fenster):
    w = fenster; ed = w.current_editor()
    FO.einfuegen(ed, "form", {"form": "Rechteck", "fuell": "#ffffff", "linie": "#000000", "strich": 1.0, "text": ""}, 200, 120)
    ed._frei_liste(); ed._frei_sel = [t[0] for t in ed._frei_treffer][-1]
    assert "zahnrad" in ed._frei_knopf_rects(_rect(ed))
    ed._frei_knopf("zahnrad", QPointF(0, 0))
    assert w.sidebar.objektformat_sichtbar()
    w.sidebar.zeige_bereich(0)
    ed = _diagramm(w); ed._frei_liste(); ed._frei_sel = [t[0] for t in ed._frei_treffer][-1]
    assert "zahnrad" in ed._frei_knopf_rects(_rect(ed)) and "dg_einst" not in ed._frei_knopf_rects(_rect(ed))
    ed._frei_knopf("zahnrad", QPointF(0, 0))
    assert w.sidebar.diagrammformat_sichtbar()
