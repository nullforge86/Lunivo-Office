"""Seitenleiste „Formatierung“ für Diagrammteile: vollständige Formate (Verlauf, Transparenz, Textwinkel, Effekte …) wirken im Bild, überleben den DOCX-Rundweg,
das Panel baut für jeden Teil bei 300 und 444 Bildpunkten ohne Überstand."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget

from lunivo_writer.editor import diagramm as D, diagramm_format as F, diagramm_teile as T, frei_objekt as FO

DATEN = {"art": "saeule_gruppiert", "titel": "Umsatz", "kategorien": ["A", "B", "C"], "reihen": {"X": [1, 2, 3], "Y": [3, 1, 2]}}


@pytest.fixture
def fenster(app, tmp_path):
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document(); w.resize(1300, 800); w.show()
    yield w
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def _bild(tf, **zusatz):
    return D.bild_aus_daten({**DATEN, "teil_format": tf, **zusatz}, 400, 260, 1.0)


def _farbe(img, x, y) -> QColor:
    return img.pixelColor(x, y)


def test_fuellung_verlauf_transparenz_und_linie_wirken(app):
    ohne = _bild({})
    einfach = _bild({"diagrammbereich": {"fuell": "#ff0000"}})
    halb = _bild({"diagrammbereich": {"fuell": {"art": "farbe", "farbe": "#ff0000", "transparenz": 60}}})
    verlauf = _bild({"diagrammbereich": {"fuell": {"art": "graduell", "dunkel": "#000080", "hell": "#ffff00", "winkel": 90}}})
    assert _farbe(einfach, 5, 5).red() > 240 and _farbe(einfach, 5, 5).green() < 20
    assert 20 < _farbe(halb, 5, 5).green() < 235 and _farbe(halb, 5, 5).red() > 240                      # durchscheinend: Weiß schimmert durch
    oben, unten = _farbe(verlauf, 5, 3), _farbe(verlauf, 5, 256)
    assert oben.red() > 200 and unten.blue() > 100 and unten.red() < 100                               # hell oben, dunkel unten
    assert _farbe(ohne, 5, 5).red() > 240 and _farbe(ohne, 5, 5).green() > 240
    from PySide6.QtGui import QImage
    rot = QImage(8, 8, QImage.Format_ARGB32); rot.fill(QColor("#ff0000"))
    bild = _bild({"diagrammbereich": {"fuell": {"art": "bild", "bild_b64": F.bild_kodieren(rot)}}})
    assert _farbe(bild, 5, 5).red() > 240 and _farbe(bild, 5, 5).green() < 20                          # Bildfüllung (als Text in den Daten)
    textur = _bild({"zeichnungsbereich": {"fuell": {"art": "textur", "key": "holz"}}})
    muster = _bild({"zeichnungsbereich": {"fuell": {"art": "muster", "key": "pct50", "farbe": "#000000", "grund": "#ffffff"}}})
    assert textur != ohne and muster != ohne
    rahmen = _bild({"diagrammbereich": {"linie": {"farbe": "#00aa00", "breite": 4, "kombiniert": "doppelt", "rund": True, "transparenz": 20}}})
    assert rahmen != ohne and any(_farbe(rahmen, 200, y).green() > _farbe(rahmen, 200, y).red() for y in range(0, 14))      # grüne Doppellinie am Rand


def test_effekte_weiche_kanten_spiegelung_und_leuchten_je_teil(app):
    ohne = _bild({"legende": {"fuell": "#eeeeee"}})
    for fx in ({"schatten": True}, {"leuchten": {"farbe": "#ff8800", "groesse": 8, "transparenz": 30}}, {"reflektion": True}, {"weich": {"radius": 6}},
               {"d3": {"tiefe": 6, "tiefe_farbe": "#808080", "kontur": 0, "kontur_farbe": "#404040", "material": "matt", "beleuchtung": "neutral", "winkel": 0}}):
        assert _bild({"legende": {"fuell": "#eeeeee", **fx}}) != ohne, fx
    assert _bild({"reihe_0": {"schatten": {"farbe": "#000000", "transparenz": 40, "groesse": 100, "weich": 2, "abstand": 6, "winkel": 45}}}) != _bild({})


def test_textwinkel_effekte_und_achse_wirken(app):
    ohne = _bild({})
    achse = _bild({"achse_horizontal": {"text": {"feld": {"winkel": -45}}}})
    assert achse != ohne and F.textwinkel({"feld": {"winkel": -45}}) == -45 and F.textwinkel({"feld": {"richtung": "dreh270", "winkel": 10}}) == -80
    titel = _bild({"titel": {"text": {"groesse": 20, "effekt": {"fuell": "verlauf", "verlauf": {"farbe1": "#ff0000", "farbe2": "#0000ff", "winkel": 0},
                                                              "schatten": {"farbe": "#000000", "transparenz": 50, "groesse": 100, "weich": 2, "abstand": 4, "winkel": 45}}}}})
    assert titel != ohne
    gedreht = _bild({"titel": {"text": {"feld": {"richtung": "dreh90"}}}})
    assert gedreht != ohne
    raender = _bild({"titel": {"fuell": "#ffff00", "text": {"feld": {"raender": {"l": 12, "o": 6, "r": 12, "u": 6}}}}})
    assert raender != _bild({"titel": {"fuell": "#ffff00"}})
    skala = _bild({"achse_vertikal": {"achse": {"min": 0, "max": 20, "intervall": 5, "umkehren": True}}})
    assert skala != ohne
    assert _bild({"reihe_0": {"reihe": {"luecke": 400}}}) != ohne
    assert _bild({"reihe_0": {"linie": {"farbe": "#ff0000", "breite": 2, "pfeil_ende": "pfeil"}, "reihe": {"glatt": True}}}, art="linie") != _bild({}, art="linie")
    assert _bild({"datenbeschriftung": {"text": {"farbe": "#ff0000", "groesse": 14}}}, labels=True) != _bild({}, labels=True)


def test_teil_format_setzen_zusammenfuehren_und_diagrammbereich_effekt_am_objekt(fenster):
    ed = fenster.current_editor()
    FO.einfuegen(ed, "diagramm", dict(DATEN), 400, 260)
    assert T.diagramm_teil_format_setzen(ed, "legende", linie={"farbe": "#ff0000", "breite": 2, "keine": True})
    assert T.diagramm_teil_format_setzen(ed, "legende", linie={"keine": None, "breite": 3})
    assert T.diagramm_teil_format_lesen(ed, "legende")["linie"] == {"farbe": "#ff0000", "breite": 3}
    assert T.diagramm_teil_format_setzen(ed, "legende", linie=None, fuell={"art": "graduell", "dunkel": "#000", "hell": "#fff"}, schatten=True)
    assert "linie" not in T.diagramm_teil_format_lesen(ed, "legende")
    # Effekte des Diagrammbereichs liegen am Objekt (außerhalb des Bildes)
    assert T.diagramm_teil_format_setzen(ed, "diagrammbereich", schatten={"farbe": "#000000", "transparenz": 50, "groesse": 100, "weich": 3, "abstand": 5, "winkel": 45},
                                         fuell="#eeeeee")
    assert FO.ziel(ed)[3]["fx"]["schatten"]["abstand"] == 5 and "schatten" not in (FO.daten_lesen(ed, "diagramm")["teil_format"]["diagrammbereich"])
    assert T.diagramm_teil_format_lesen(ed, "diagrammbereich")["schatten"]["abstand"] == 5
    assert T.diagramm_teil_format_setzen(ed, "diagrammbereich", schatten=None) and not FO.ziel(ed)[3].get("fx")


def test_docx_rundweg_teilformate(fenster, tmp_path):
    from lunivo_writer.editor import freie_bilder as FB
    from lunivo_writer.services import docx_reader, docx_writer
    ed = fenster.current_editor()
    FO.einfuegen(ed, "diagramm", dict(DATEN), 400, 260)
    T.diagramm_teil_format_setzen(ed, "titel", fuell={"art": "graduell", "dunkel": "#000080", "hell": "#ffff00", "winkel": 45, "transparenz": 30},
                                  linie={"farbe": "#ff0000", "breite": 2, "kombiniert": "doppelt", "abschluss": "rund", "verknuepfung": "spitz", "rund": True},
                                  text={"effekt": {"fuell": "verlauf", "verlauf": {"farbe1": "#ff0000", "farbe2": "#0000ff", "winkel": 0}},
                                        "feld": {"winkel": -30, "raender": {"l": 5, "o": 2, "r": 5, "u": 2}}, "kursiv": True})
    T.diagramm_teil_format_setzen(ed, "achse_vertikal", achse={"min": 0, "max": 20, "intervall": 5, "umkehren": True})
    T.diagramm_teil_format_setzen(ed, "reihe_1", fuell={"art": "textur", "key": "holz"}, reihe={"luecke": 80})
    T.diagramm_teil_format_setzen(ed, "diagrammbereich", schatten={"farbe": "#000000", "transparenz": 50, "groesse": 100, "weich": 3, "abstand": 5, "winkel": 45})
    d = FO.daten_lesen(ed, "diagramm")
    pfad = str(tmp_path / "f.docx")
    docx_writer.write_docx(pfad, ed.document(), ed.page, {})
    doc = docx_reader.read_docx(pfad)[0]
    gelesen, blk = [], doc.firstBlock()
    while blk.isValid():
        gelesen += [x for x in FB.aus_absatz(blk.blockFormat()) if x.get("art") == "diagramm"]
        blk = blk.next()
    assert len(gelesen) == 1
    assert gelesen[0]["daten"]["teil_format"] == d["teil_format"]
    assert gelesen[0].get("fx", {}).get("schatten")                                   # Effekte des Diagrammbereichs: wie bei jedem freien Bild als DOCX-Effekt
    assert D.bild_aus_daten(gelesen[0]["daten"], 400, 260) == D.bild_aus_daten(d, 400, 260)


def _teile_werte(teil: str, art: str = "saeule_gruppiert") -> dict:
    reihe = teil.startswith("reihe_")
    return {"teil": teil, "format": {}, "linienreihe": reihe and art.startswith("linie"), "saeulen": reihe and art.startswith("saeule"), "wertachse": True,
            "objekt": {"legende_pos": "unten", "breite_mm": 120.0, "hoehe_mm": 80.0, "dreh": 0.0}}


@pytest.mark.parametrize("breite", [300, 444])
@pytest.mark.parametrize("teil", ["diagrammbereich", "zeichnungsbereich", "titel", "legende", "achse_vertikal", "reihe_0", "legendeneintrag_0", "datenbeschriftung"])
def test_panel_ragt_bei_jedem_teil_nicht_heraus(app, breite, teil):
    from lunivo_writer.ui.baukasten.diagramm_format_panel import DiagrammFormatPanel
    p = DiagrammFormatPanel(None, _teile_werte(teil, "linie" if teil == "reihe_0" else "saeule_gruppiert")); p.resize(breite, 700); p.show(); app.processEvents()
    for haupt in (0, 1):
        if not p.optionen.isTabEnabled(haupt):
            continue
        p.optionen_waehlen(haupt); app.processEvents()
        reiter = p.reiter if haupt == 0 else p.text_panel.reiter
        for i in range(reiter.count()):
            if not reiter.isTabVisible(i):
                continue
            reiter.setCurrentIndex(i); app.processEvents()
            for wdg in p.findChildren(QWidget):
                if wdg.isVisible():
                    x = wdg.mapTo(p, wdg.rect().bottomRight()).x()
                    assert x <= p.width() + 1, (teil, haupt, i, type(wdg).__name__, x, p.width())
    p.close()


def test_reiter_und_abschnitte_folgen_dem_teil(app):
    from lunivo_writer.ui.baukasten.diagramm_format_panel import DiagrammFormatPanel
    p = DiagrammFormatPanel(None, _teile_werte("diagrammbereich")); p.show(); app.processEvents()
    sichtbar = lambda: [p.reiter.isTabVisible(i) for i in range(4)]       # noqa: E731
    assert sichtbar() == [True, True, False, True]
    for teil, namen, haupt in (("titel", [True, True, False, False], "Titeloptionen"), ("legende", [True, True, True, False], "Legendenoptionen"),
                               ("achse_horizontal", [True, True, True, False], "Achsenoptionen"), ("reihe_1", [True, True, True, False], "Reihenoptionen")):
        p.setze(_teile_werte(teil)); app.processEvents()
        assert sichtbar() == namen and p.optionen.tabText(0) == haupt, teil
    p.setze({**_teile_werte("reihe_0", "linie"), "linienreihe": True}); assert not p.a_pfeile.isHidden() and not p.a_reihe_linie.isHidden() and p.a_reihe.isHidden()
    p.setze({**_teile_werte("reihe_0"), "saeulen": True}); assert p.a_pfeile.isHidden() and not p.a_reihe.isHidden()
    p.setze(_teile_werte("zeichnungsbereich")); assert not p.optionen.isTabEnabled(1)
    p.setze(_teile_werte("datenbeschriftung")); assert p.optionen.isTabEnabled(1) and not p.optionen.isTabEnabled(0) and p.optionen.currentIndex() == 1


def test_panel_meldet_verlauf_linie_effekte_text_und_optionen(fenster, app):
    ed = fenster.current_editor()
    FO.einfuegen(ed, "diagramm", dict(DATEN), 400, 260)
    fenster._sync_format()
    T.teil_waehlen(ed, "titel")
    fenster.diagrammformat_seitenleiste()
    p = fenster.sidebar.diagramm_panel
    p.r_verlauf.setChecked(True); app.processEvents()
    fu = T.diagramm_teil_format_lesen(ed)["fuell"]
    assert fu["art"] == "graduell" and fu["winkel"] == 90
    p.f_trans.setValue(40, melden=True); app.processEvents()
    assert T.diagramm_teil_format_lesen(ed)["fuell"]["transparenz"] == 40
    p.k_verlauf.setChecked(True); p.l_kombi.setCurrentIndex(p.l_kombi.findData("doppelt")); p.l_rund.setChecked(True); app.processEvents()
    li = T.diagramm_teil_format_lesen(ed)["linie"]
    assert li["verlauf"]["farbe1"] and li["kombiniert"] == "doppelt" and li["rund"] is True and "keine" not in li
    p.k_keine.setChecked(True); app.processEvents()
    assert T.diagramm_teil_format_lesen(ed)["linie"] == {"keine": True}
    p.k_auto.setChecked(True); app.processEvents()
    assert "linie" not in T.diagramm_teil_format_lesen(ed)
    p.r_auto.setChecked(True); app.processEvents()
    assert "fuell" not in T.diagramm_teil_format_lesen(ed)
    # Effekte
    p.s_farbe.setFarbe("#336699"); p.s_farbe.farbeGeaendert.emit("#336699"); p.l_gross.setValue(7, melden=True); app.processEvents()
    f = T.diagramm_teil_format_lesen(ed)
    assert f["schatten"]["farbe"] == "#336699" and f["leuchten"]["groesse"] == 7
    # Textoptionen: Winkel, Ränder, Schrift, Textfüllung
    p.optionen_waehlen(1)
    tp = p.text_panel
    tp.f_winkel.setValue(-30); tp.f_rand["l"].setValue(8); tp.s_fett.setChecked(True); tp.s_groesse.setValue(20); app.processEvents()
    t = T.diagramm_teil_format_lesen(ed)["text"]
    assert t["feld"]["winkel"] == -30 and t["feld"]["raender"]["l"] == 8 and t["fett"] is True and t["groesse"] == 20
    tp.r_verlauf.setChecked(True); app.processEvents()
    assert T.diagramm_teil_format_lesen(ed)["text"]["effekt"]["fuell"] == "verlauf"
    # Legende: Position; Achse: Skala; Reihe: Lückenbreite
    T.teil_waehlen(ed, "legende"); fenster.diagrammformat_folgen()
    p.o_lage.setCurrentIndex(p.o_lage.findData("rechts")); app.processEvents()
    assert FO.daten_lesen(ed, "diagramm")["legende_pos"] == "rechts"
    T.teil_waehlen(ed, "achse_vertikal"); fenster.diagrammformat_folgen()
    p.o_max.auto.setChecked(False); p.o_max.feld.setValue(12); p.o_umkehren.setChecked(True); app.processEvents()
    a = T.diagramm_teil_format_lesen(ed)["achse"]
    assert a["max"] == 12 and a["umkehren"] is True and "min" not in a
    T.teil_waehlen(ed, "reihe_0"); fenster.diagrammformat_folgen()
    p.o_luecke.setValue(50, melden=True); app.processEvents()
    assert T.diagramm_teil_format_lesen(ed)["reihe"]["luecke"] == 50
    # Diagrammbereich: Größe, Drehung, Effekt am Objekt
    T.teil_waehlen(ed, "diagrammbereich"); fenster.diagrammformat_folgen()
    p.g_breite.zahl.setValue(p.g_breite.zahl.value() / 2); app.processEvents()
    assert FO.ziel(ed)[3]["b"] < 400
    p.g_dreh.setValue(15); app.processEvents()
    assert FO.ziel(ed)[3]["dreh"] == 15
    p.reiter.setCurrentIndex(1); p.s_farbe.setFarbe("#112233"); p.s_farbe.farbeGeaendert.emit("#112233"); app.processEvents()
    assert FO.ziel(ed)[3]["fx"]["schatten"]["farbe"] == "#112233"
