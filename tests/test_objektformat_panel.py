"""Seitenleiste „Formatierung“ für Objekte (``objektformat_panel.py``): Umschalter Form-/Textoptionen, Reiter, alle Effekt-Abschnitte mit Feldern,
3D-Format und 3D-Drehung wirken am Objekt (``editor/bildeffekte.py``), bei 300 px ragt nichts heraus."""
from __future__ import annotations

import pytest
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtWidgets import QScrollArea, QWidget

from lunivo_writer.editor import bildeffekte as E
from lunivo_writer.ui.baukasten.objektformat_panel import ObjektFormatPanel
from lunivo_writer.ui.baukasten.texteffekt_dialog import Abschnitt


def _bild(w=80, h=60) -> QImage:
    b = QImage(w, h, QImage.Format_ARGB32_Premultiplied); b.fill(QColor("#c92a2a"))
    return b


def _leer(w=240, h=200) -> QImage:
    b = QImage(w, h, QImage.Format_ARGB32_Premultiplied); b.fill(Qt.transparent)
    return b


def test_aufbau_nach_der_vorlage(app):
    p = ObjektFormatPanel(None, {"fuell": None, "rand": None})
    assert [p.optionen.tabText(i) for i in (0, 1)] == ["Formoptionen", "Textoptionen"]
    assert p.reiter.count() == 2
    p.reiter.setCurrentIndex(1)
    seite = p.reiter.currentWidget()
    lay = seite.widget().layout()
    namen = [lay.itemAt(i).widget().titel.text() for i in range(lay.count()) if isinstance(lay.itemAt(i).widget(), Abschnitt)]
    assert namen == ["SCHATTEN", "REFLEKTION", "LEUCHTEN", "WEICHE KANTEN", "3D-FORMAT", "3D-DREHUNG"], namen
    p.optionen_waehlen(1)
    assert p.optionen.currentWidget() is p.text_panel and p.optionen.currentIndex() == 1


def test_werte_mit_3d_und_drehung(app):
    p = ObjektFormatPanel(None, {"fuell": None, "rand": None})
    assert "d3" not in p.werte() and "drehung" not in p.werte()
    gemeldet = []
    p.geaendert.connect(gemeldet.append)
    p._stumm = False
    p.d_tiefe.setValue(12); p.dr_y.setValue(40); p.dr_pers.setValue(60)
    w = p.werte()
    assert w["d3"]["tiefe"] == 12 and w["drehung"] == {"x": 0.0, "y": 40.0, "z": 0.0, "persp": 60.0, "text_gerade": False, "boden": 0.0}
    p2 = ObjektFormatPanel(None, w)                                  # zurück ins Panel und wieder heraus
    assert p2.werte()["d3"]["tiefe"] == 12 and p2.werte()["drehung"]["y"] == 40.0
    p2._drehung_zuruecksetzen(); p2._d3_zuruecksetzen()
    assert "d3" not in p2.werte() and "drehung" not in p2.werte()


def test_textoptionen_melden_und_nehmen_werte(app):
    p = ObjektFormatPanel(None, {"fuell": None, "rand": None})
    p.setze_text({"fuell": "keine", "farbe": "#112233"})
    assert p.text_werte()["fuell"] == "keine"
    got = []
    p.text_geaendert.connect(got.append)
    p.text_panel._stumm = False
    p.text_panel.r_farbe.setChecked(True)
    app.processEvents()
    assert got and got[-1]["fuell"] == "farbe"


@pytest.mark.parametrize("breite", [300, 444])
def test_passt_in_die_seitenleiste(app, breite):
    from lunivo_writer.ui.baukasten.zusatz_panel import FLACHE_REITER
    p = ObjektFormatPanel(None, {"fuell": None, "rand": None}); p.setStyleSheet(FLACHE_REITER)       # wie im Rahmen der Seitenleiste
    p.resize(breite - 24, 800); p.show()
    for optionen in (0, 1):
        p.optionen_waehlen(optionen)
        reiter = p.reiter if optionen == 0 else p.text_panel.reiter
        for i in range(reiter.count()):
            reiter.setCurrentIndex(i)
            for a in reiter.currentWidget().findChildren(Abschnitt):
                a.knopf.setChecked(True)
            app.processEvents(); app.processEvents()
            sa = reiter.currentWidget()
            assert isinstance(sa, QScrollArea)
            vp = sa.viewport()
            zu = [type(c).__name__ for c in sa.widget().findChildren(QWidget) if c.isVisible() and c.width() > 0
                  and (c.mapTo(vp, c.rect().topLeft()).x() < -1 or c.mapTo(vp, c.rect().topRight()).x() > vp.width())]
            assert not zu, (breite, optionen, i, zu)
            assert not sa.horizontalScrollBar().isVisible()
    p.close()


def _beschriftet(bild: QImage) -> int:
    n = 0
    for y in range(bild.height()):
        for x in range(bild.width()):
            if QColor(bild.pixelColor(x, y)).alpha() > 0:
                n += 1
    return n


def test_3d_format_malt_tiefe_hinter_das_bild(app):
    """Mit Tiefe liegt hinter dem Bild (rechts unten) eine gestapelte Form in der Tiefenfarbe; ohne Tiefe bleibt die Fläche leer."""
    r = QRectF(40, 40, 80, 60)
    out = _leer(); p = QPainter(out)
    E.unter_zeichnen(p, _bild(), r, False, {}); p.end()
    assert _beschriftet(out) == 0
    out = _leer(); p = QPainter(out)
    E.unter_zeichnen(p, _bild(), r, False, {"d3": {"tiefe": 12, "tiefe_farbe": "#2f9e44", "material": "matt", "beleuchtung": "neutral"}}); p.end()
    assert QColor(out.pixelColor(125, 105)).alpha() > 0              # rechts unten über das Bild hinaus
    assert QColor(out.pixelColor(30, 30)).alpha() == 0               # links oben nichts
    assert QColor(out.pixelColor(120, 100)).green() > QColor(out.pixelColor(120, 100)).red()      # Tiefenfarbe, nicht die des Bildes


def test_3d_kontur_zeichnet_rand(app):
    r = QRectF(40, 40, 80, 60)
    out = _leer(); p = QPainter(out)
    E.unter_zeichnen(p, _bild(), r, False, {"d3": {"tiefe": 0, "kontur": 3, "kontur_farbe": "#0000ff"}}); p.end()
    assert QColor(out.pixelColor(38, 70)).alpha() > 0                # Kontur links neben dem Bild


def test_3d_drehung_verkleinert_und_bleibt_im_rahmen(app):
    r = QRectF(0, 0, 100, 60)
    b = _bild(100, 60)
    assert not E.hat_drehung({}) and E.hat_drehung({"drehung": {"x": 0, "y": 50, "z": 0}})
    g = E.drehung_3d(b, r, False, {"x": 0, "y": 60, "z": 0, "persp": 0})
    assert g.size() == b.size()
    breite = [x for x in range(g.width()) if QColor(g.pixelColor(x, 30)).alpha() > 128]
    assert 40 <= len(breite) <= 60                                   # um Y gedreht: etwa cos(60°) · 100
    z = E.drehung_3d(b, r, False, {"x": 0, "y": 0, "z": 90, "persp": 0})
    assert _beschriftet(z) > 0
    pers = E.drehung_3d(b, r, False, {"x": 40, "y": 0, "z": 0, "persp": 70})
    oben = sum(1 for x in range(100) if QColor(pers.pixelColor(x, 20)).alpha() > 128)
    unten = sum(1 for x in range(100) if QColor(pers.pixelColor(x, 40)).alpha() > 128)
    assert oben != unten                                             # Perspektive: eine Kante ist breiter als die andere


def test_abschluss_boden_und_text_gerade_in_den_werten(app):
    p = ObjektFormatPanel(None, {"fuell": None, "rand": None})
    p._abschluss_setzen("oben", "winkel"); p._abschluss_setzen("unten", "rund")
    p.ab_breite["oben"].setValue(7); p.dr_boden.setValue(12); p.dr_text.setChecked(True)
    w = p.werte()
    assert w["d3"]["oben"] == {"art": "winkel", "breite": 7.0, "hoehe": 6.0} and w["d3"]["unten"]["art"] == "rund" and w["d3"]["tiefe"] == 0.0
    assert w["drehung"]["boden"] == 12.0 and w["drehung"]["text_gerade"] is True
    p2 = ObjektFormatPanel(None, w)
    assert p2.werte()["d3"]["oben"]["breite"] == 7.0 and p2.ab_knopf["oben"].text() == "Winkel" and p2.dr_text.isChecked()
    p.ab_breite["unten"].regler.setValue(20); assert p.ab_art["unten"] == "rund"
    p3 = ObjektFormatPanel(None, {"fuell": None, "rand": None})
    p3.ab_hoehe["oben"].regler.setValue(90)                                  # ein Regler schaltet den Abschluss ein
    assert p3.ab_art["oben"] == "rund"
    assert not hasattr(p.text_panel, "ab_knopf") or not p.text_panel.ab_knopf     # der Text-Effekt kennt keine Abschlüsse


def test_oberer_abschluss_beleuchtet_den_rand(app):
    b = _bild(80, 60)
    g = E.abschluss_oben(b, QRectF(0, 0, 80, 60), False, {"art": "winkel", "breite": 6, "hoehe": 12})
    links_oben, rechts_unten, mitte = QColor(g.pixelColor(2, 30)), QColor(g.pixelColor(77, 30)), QColor(g.pixelColor(40, 30))
    assert links_oben.lightness() > mitte.lightness() > rechts_unten.lightness()     # hell links oben, dunkel rechts unten, Mitte unberührt
    ohne = E.abschluss_oben(b, QRectF(0, 0, 80, 60), False, {"art": "keine"})
    assert QColor(ohne.pixelColor(2, 30)) == QColor(b.pixelColor(2, 30))
    for art, _n in E.ABSCHLUSS:                                      # jede Art läuft und lässt die Mitte stehen
        x = E.abschluss_oben(b, QRectF(0, 0, 80, 60), False, {"art": art, "breite": 5, "hoehe": 8})
        assert QColor(x.pixelColor(40, 30)) == QColor(b.pixelColor(40, 30)), art
        assert not E.abschluss_symbol(art).isNull()
    fx = {"d3": {"tiefe": 0, "oben": {"art": "rund", "breite": 4, "hoehe": 6}}}
    assert E.hat_abschluss(fx) and E.hat_nachbearbeitung(fx) and E.bild_nachbearbeiten(b, QRectF(0, 0, 80, 60), False, fx).size() == b.size()


def test_unterer_abschluss_vertieft_die_rueckseite(app):
    r = QRectF(40, 40, 80, 60)
    def tiefe(unten):
        out = _leer(); p = QPainter(out)
        d3 = {"tiefe": 10, "tiefe_farbe": "#2f9e44"}
        if unten:
            d3["unten"] = {"art": "rund", "breite": 4, "hoehe": 12}
        E.unter_zeichnen(p, _bild(), r, False, {"d3": d3}); p.end()
        return _beschriftet(out)
    assert tiefe(True) > tiefe(False)


def test_abstand_vom_boden_senkt_schatten_und_spiegelung(app):
    r = QRectF(40, 40, 80, 60)
    def unten(boden):
        out = _leer(240, 300); p = QPainter(out)
        E.unter_zeichnen(p, _bild(), r, False, {"reflektion": {"groesse": 50, "transparenz": 20, "weich": 0, "abstand": 0}, "drehung": {"boden": boden}}); p.end()
        return max(y for y in range(out.height()) for x in range(0, out.width(), 4) if QColor(out.pixelColor(x, y)).alpha() > 0)
    assert unten(20) > unten(0) + 15


def test_text_nicht_drehen_haelt_den_inhalt_aufrecht(app):
    r = QRectF(0, 0, 100, 60)
    b = QImage(100, 60, QImage.Format_ARGB32_Premultiplied); b.fill(Qt.transparent)
    q = QPainter(b); q.fillRect(30, 20, 40, 20, QColor("#000000")); q.end()              # „Text“: ein Balken in der Mitte
    dreh = {"x": 0, "y": 0, "z": 90, "persp": 0}
    gedreht = E.drehung_3d(b, r, False, dreh)
    gerade = E.drehung_3d(b, r, False, {**dreh, "text_gerade": True})
    def waagrecht(g):
        xs = [x for x in range(100) if QColor(g.pixelColor(x, 30)).alpha() > 128]; ys = [y for y in range(60) if QColor(g.pixelColor(50, y)).alpha() > 128]
        return len(xs) > len(ys)
    assert not waagrecht(gedreht) and waagrecht(gerade)


def test_schrittfeld_zeigt_die_zahl_im_dunklen_thema(app):
    """Die Zahl steht im Textfeld (nicht leer) und das Feld hat Breite für den Text — Fehler war „NoButtons“ unter dem Stylesheet des Themas."""
    from lunivo_writer.ui.baukasten.schiebe_feld import SchrittFeld
    f = SchrittFeld(0, 60, " pt", 0.5, 1, wert=5); f.resize(150, 28); f.show(); app.processEvents()
    assert f.feld.text() == "5.0 pt" or f.feld.text() == "5,0 pt"
    img = f.feld.grab().toImage()
    mitte = {img.pixelColor(x, y).name() for x in range(img.width() // 2 - 20, img.width() // 2 + 20) for y in range(img.height())}
    assert len(mitte) > 2                                            # die Mitte zeigt Schrift, nicht nur die Fläche
