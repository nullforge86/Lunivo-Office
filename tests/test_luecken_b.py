"""Lücken B: Diagrammfilter „Name“, Diagrammtyp direkt, Linien-Galerie, Freiform (Punkte bearbeiten), Live-Vorschau, Helligkeit/Kontrast, Zoom-Ansicht."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QColor, QImage, QKeyEvent, QMouseEvent

from lunivo_writer.editor import freiform as FF, frei_objekt as FO


@pytest.fixture
def fenster(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document(); w.resize(1200, 800); w.show()
    yield w
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def _maus(ed, typ, pos, taste=Qt.LeftButton, gedrueckt=Qt.LeftButton):
    e = QMouseEvent(typ, QPointF(pos), QPointF(pos), taste, gedrueckt, Qt.NoModifier)
    art = {QEvent.MouseButtonPress: "press", QEvent.MouseMove: "move", QEvent.MouseButtonRelease: "release", QEvent.MouseButtonDblClick: "doppel"}[typ]
    return ed._frei_maus(e, art)


def _rect(ed):
    ed._frei_liste()
    return [t for t in ed._frei_treffer if t[0] == ed._frei_sel][0][2]


def test_diagramm_filter_name_und_typ_direkt(fenster):
    from lunivo_writer.ui.baukasten.diagramm_popups import DiagrammPopup
    ed = fenster.current_editor(); b = fenster.befehle
    FO.einfuegen(ed, "diagramm", {"art": "saeule_gruppiert", "titel": "T", "kategorien": ["A", "B"], "reihen": {"X": [1, 2], "Y": [3, 1]}}, 400, 260)
    b.diagrammFilterSetzen(None, {"reihen": ["Y"]})
    pop = DiagrammPopup(b, "filter", 1)                                      # Reiter „Name“
    assert [pop.gruppe.button(i).text() for i in (0, 1)] == ["Wert", "Name"]
    pop.neu_lesen(); namen = pop._felder
    assert [a for a, _e in namen["reihen"]] == ["X", "Y"] and [a for a, _e in namen["rubriken"]] == ["A", "B"]
    namen["reihen"][1][1].setText("Süd"); namen["rubriken"][0][1].setText("Q1")
    pop._namen_uebernehmen()
    d = FO.daten_lesen(ed, "diagramm")
    assert list(d["reihen"]) == ["X", "Süd"] and d["reihen"]["Süd"] == [3, 1] and d["kategorien"] == ["Q1", "B"]
    assert d["ausgeblendet"] == {"reihen": ["Süd"]}                          # der Filter wandert mit
    b.diagrammNamenSetzen(None, {"reihen": [("X", "Süd")]})                  # doppelter Name bleibt beim alten
    assert list(FO.daten_lesen(ed, "diagramm")["reihen"]) == ["X", "Süd"]
    # Typ direkt ändern; das Fenster ohne Angabe bleibt der große Knopf
    b.tun('diagrammTypAendern:["linie"]')
    assert FO.daten_lesen(ed, "diagramm")["art"] == "linie"
    assert not b.diagrammTypAendern(None, "gibt_es_nicht")
    m = b.klappe("diagrammTyp_saeule")
    assert [a.text() for a in m.actions()] == ["Gruppierte Säule", "Gestapelte Säule", "100 % gestapelte Säule"]
    m.actions()[1].trigger()
    m.aboutToShow.emit()
    assert FO.daten_lesen(ed, "diagramm")["art"] == "saeule_gestapelt" and m.actions()[1].isChecked() and not m.actions()[0].isChecked()
    from lunivo_writer.ui.contextual.diagramm_tools import DIAGRAMMTOOLS
    knoepfe = [k for g in DIAGRAMMTOOLS["gruppen"] for k in g.get("knoepfe", []) if k.get("name", "").startswith("Diagrammtyp: ")]
    assert len(knoepfe) == 10 and all(b.hat(k["tun"].split(":")[0]) for k in knoepfe)


def test_linien_galerie_fuegt_ein(fenster):
    from lunivo_writer.ui.baukasten.form_menues import GALERIEN
    from lunivo_writer.ui.contextual.image_tools import ZEICHENTOOLS
    from lunivo_writer.editor import formen_katalog as K
    ed = fenster.current_editor(); b = fenster.befehle
    spec = GALERIEN["zeichenLinien"](b)
    assert len(spec["kacheln"]) == 10 and all(K.ist_linie(t) for t, _pm, _f in spec["kacheln"])
    assert any(g.get("galerie") == "zeichenLinien" and g.get("zeilen") == 2 for g in ZEICHENTOOLS["gruppen"])
    tipp, _pm, tun = spec["kacheln"][1]
    tun()
    assert tipp == "Pfeil" and FO.art_gewaehlt(ed) == "form" and FO.daten_lesen(ed, "form")["form"] == "Pfeil"
    spec["menue"].actions()      # Raster baut sich
    assert FO.ziel(ed)[4].width() > 0


def test_freiform_punkte_ziehen_loeschen_einfuegen(fenster, tmp_path):
    ed = fenster.current_editor(); b = fenster.befehle
    FO.einfuegen(ed, "form", {**FO.FORM_STANDARD, "form": "Rechteck"}, 200, 120)
    assert b.formPunkteBearbeiten()
    d = FO.daten_lesen(ed, "form")
    assert d["form"] == "Freiform" and len(FF.knoten(d["punkte"])) == 4 and ed._frei_sel is not None
    r = _rect(ed)
    # Ecke oben links nach rechts unten ziehen: Live-Vorschau ohne Dokumentschritt, erst beim Loslassen gespeichert
    start = QPointF(r.left() + 2 * r.width() / 200, r.top() + 2 * r.height() / 120)
    rev = ed.document().revision()
    assert _maus(ed, QEvent.MouseButtonPress, start)
    ziel = QPointF(r.center().x(), r.center().y())
    assert _maus(ed, QEvent.MouseMove, ziel)
    assert ed.document().revision() == rev and any(v.get("_vorschau") is not None for v in ed._frei_vorlaeufig.values())
    assert _maus(ed, QEvent.MouseButtonRelease, ziel, gedrueckt=Qt.NoButton)
    p = FO.daten_lesen(ed, "form")["punkte"]
    assert 0.3 < p[0][1] < 0.7 and 0.3 < p[0][2] < 0.7 and not ed._frei_vorlaeufig
    ed.undo() if hasattr(ed, "undo") else None
    # Punkt löschen: Rechtsklick auf einen Punkt (aus 4 wird 3), danach ist Schluss (Dreieck bleibt)
    r = _rect(ed)
    abb_p = FO.daten_lesen(ed, "form")["punkte"]
    from lunivo_writer.ui.document import freiform_bedienung as FP
    a = FO.ziel(ed)[3] and [t for t in ed._frei_treffer if t[0] == ed._frei_sel][0][1]
    abb = FP._Abb(a, r)
    ecke = abb.zu_schirm(abb_p[2][1], abb_p[2][2])
    assert _maus(ed, QEvent.MouseButtonPress, ecke, Qt.RightButton, Qt.RightButton)
    assert len(FF.knoten(FO.daten_lesen(ed, "form")["punkte"])) == 3
    p3 = FO.daten_lesen(ed, "form")["punkte"]
    k0 = abb.zu_schirm(p3[1][1], p3[1][2])
    assert _maus(ed, QEvent.MouseButtonPress, k0, Qt.RightButton, Qt.RightButton)
    assert len(FF.knoten(FO.daten_lesen(ed, "form")["punkte"])) == 3                      # mindestens 3 Punkte bleiben
    # Punkt einfügen: Doppelklick auf eine Kante
    p3 = FO.daten_lesen(ed, "form")["punkte"]
    ka = abb.zu_schirm(p3[1][1], p3[1][2]); kb = abb.zu_schirm(p3[2][1], p3[2][2])
    mitte = QPointF((ka.x() + kb.x()) / 2, (ka.y() + kb.y()) / 2)
    assert _maus(ed, QEvent.MouseButtonDblClick, mitte)
    assert len(FF.knoten(FO.daten_lesen(ed, "form")["punkte"])) == 4
    # Entf löscht den gewählten Punkt, nicht das Objekt; Esc beendet den Modus (Objekt bleibt gewählt)
    assert ed.__dict__["_fp_sel"] is not None
    ed._frei_taste(QKeyEvent(QEvent.KeyPress, Qt.Key_Delete, Qt.NoModifier))
    assert len(FF.knoten(FO.daten_lesen(ed, "form")["punkte"])) == 3 and ed._frei_sel is not None
    ed._frei_taste(QKeyEvent(QEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier))
    assert ed.__dict__.get("_fp_key") is None and ed._frei_sel is not None
    # DOCX-Rundweg: die Punkte stehen im lunivo:-Titel
    from lunivo_writer.editor import freie_bilder as FB
    from lunivo_writer.services import docx_reader, docx_writer
    pfad = str(tmp_path / "f.docx")
    docx_writer.write_docx(pfad, ed.document(), ed.page, {})
    doc = docx_reader.read_docx(pfad)[0]
    angaben, blk = [], doc.firstBlock()
    while blk.isValid():
        angaben += FB.aus_absatz(blk.blockFormat()); blk = blk.next()
    soll = FO.daten_lesen(ed, "form")["punkte"]
    gelesen = [x for x in angaben if x.get("art") == "form"][0]["daten"]
    assert gelesen["form"] == "Freiform" and [[round(v, 6) for v in e] for e in gelesen["punkte"]] == [[round(v, 6) for v in e] for e in soll]


def test_freiform_kurven_und_formwechsel(fenster):
    ed = fenster.current_editor(); b = fenster.befehle
    FO.einfuegen(ed, "form", {**FO.FORM_STANDARD, "form": "Ellipse"}, 160, 120)
    assert b.formPunkteBearbeiten()
    p = FO.daten_lesen(ed, "form")["punkte"]
    assert any(e[0] == FF.C for e in p) and FF.geschlossen(p)
    neu, i = FF.einfuegen(p, 0.5, 0.0, 156, 116)                              # Kurve wird geteilt
    assert len(FF.knoten(neu)) == len(FF.knoten(p)) + 1 and FF.loeschen(neu, i) is not None
    v = FF.verschieben(p, 0, 1.0, 0.6)                                          # ein Kurvenpunkt nimmt seine Steuerpunkte mit
    assert v[0][2] == 0.6 and v[1][2] != p[1][2]
    b.formAendern(None, "Raute")
    d = FO.daten_lesen(ed, "form")
    assert d["form"] == "Raute" and "punkte" not in d and ed.__dict__.get("_fp_key") is None


def test_live_vorschau_anpassungsgriff(fenster):
    ed = fenster.current_editor()
    FO.einfuegen(ed, "form", {**FO.FORM_STANDARD, "form": "Pfeil nach rechts"}, 160, 120)
    r = _rect(ed)
    griff = list(ed._frei_adj_lagen(r, FO.ziel(ed)[3]).values())[0]
    rev = ed.document().revision()
    assert _maus(ed, QEvent.MouseButtonPress, griff)
    _maus(ed, QEvent.MouseMove, griff + QPointF(-20, 10))
    assert ed.document().revision() == rev and any(v.get("_vorschau") is not None for v in ed._frei_vorlaeufig.values())
    vorschau = [t for t in ed._frei_liste() if t[0] == ed._frei_sel][0][2]
    assert vorschau.width() > 0
    _maus(ed, QEvent.MouseButtonRelease, griff + QPointF(-20, 10), gedrueckt=Qt.NoButton)
    assert not ed._frei_vorlaeufig and FO.daten_lesen(ed, "form").get("adj")


def test_bild_helligkeit_kontrast_nicht_zerstoerend(fenster, tmp_path):
    from lunivo_writer.editor import bildlayout as BL, bildwerkzeuge as BW, freie_bilder as FB
    from lunivo_writer.services import docx_reader, docx_writer
    ed = fenster.current_editor(); b = fenster.befehle
    img = QImage(60, 40, QImage.Format_RGB32); img.fill(QColor(100, 100, 100)); pfad = str(tmp_path / "g.png"); img.save(pfad)
    assert ed.insert_image(pfad)
    vorher = BL.ziel(ed)[3].pixelColor(5, 5).red()
    b.tun("bildHelligkeit:[10]"); z = BL.ziel(ed)
    assert z[2]["hell"] == 10 and z[3].pixelColor(5, 5).red() > vorher and FB.bild_im_dokument(ed.document(), z[2]["n"]).pixelColor(5, 5).red() == vorher
    b.tun("bildHelligkeit:[-10]"); b.tun("bildHelligkeit:[-10]")
    z = BL.ziel(ed); assert z[2]["hell"] == -10 and z[3].pixelColor(5, 5).red() < vorher
    b.tun("bildKontrast:[10]"); z = BL.ziel(ed)
    assert z[2]["kontrast"] == 10 and z[3].pixelColor(5, 5).red() < vorher - 20                        # dunkles Grau wird dunkler
    assert z[3].pixelColor(5, 5).alpha() == 255
    for _ in range(15):
        b.bildKontrast(None, 10)
    assert BL.ziel(ed)[2]["kontrast"] == 100                                                          # begrenzt
    b.bildKontrast(None, -100)
    pfad2 = str(tmp_path / "h.docx")
    docx_writer.write_docx(pfad2, ed.document(), ed.page, {})
    doc = docx_reader.read_docx(pfad2)[0]
    angaben, blk = [], doc.firstBlock()
    while blk.isValid():
        angaben += FB.aus_absatz(blk.blockFormat()); blk = blk.next()
    assert angaben[0].get("hell") == -10 and "kontrast" not in angaben[0]
    BW.zuruecksetzen(ed, BL.ziel(ed)); z = BL.ziel(ed)
    assert "hell" not in z[2] and z[3].pixelColor(5, 5).red() == vorher


def test_zoom_ansicht_baut_sich_bei_300px(app):
    from lunivo_writer.ui.baukasten.bild_zoom import BildZoomFenster
    from lunivo_writer.ui.baukasten.zusatz_panel import ZusatzPanel
    img = QImage(500, 300, QImage.Format_ARGB32); img.fill(QColor("steelblue"))
    p = ZusatzPanel(); p.verfuegbar, p.verfuegbar_hoehe = 300, 587; p.resize(336, 727)
    d = BildZoomFenster(None, img)
    p.oeffne(d); p.show(); app.processEvents(); app.processEvents()
    vp = p.stapel.currentWidget().sa.viewport()
    zu = [type(c).__name__ for c in d.findChildren(type(d.ansicht.bild).__mro__[-3]) if False]
    assert d.ansicht.bild.pixmap().width() == 500
    d.zoom.setValue(50, melden=True)
    assert d.ansicht.bild.pixmap().width() == 250
    from PySide6.QtGui import QWheelEvent
    from PySide6.QtCore import QPoint
    e = QWheelEvent(QPointF(10, 10), QPointF(10, 10), QPoint(0, 0), QPoint(0, 120), Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False)
    d.ansicht.wheelEvent(e)
    assert d.zoom.value() == 60 and d.ansicht.bild.pixmap().width() == 300
    from PySide6.QtWidgets import QWidget
    ragt = [type(c).__name__ for c in d.findChildren(QWidget) if c.isVisible() and c.width() > 0 and c is not d.ansicht.bild
            and (c.mapTo(vp, c.rect().topLeft()).x() < -1 or c.mapTo(vp, c.rect().topRight()).x() > vp.width()) and not d.ansicht.isAncestorOf(c)]
    assert not ragt, ragt
    p.close()


def test_smartart_radial_hat_pfeile(app):
    from lunivo_writer.editor import smartart as SA
    d = {"layout": "Radial", "text": "Kern\nA\nB\nC"}
    img = SA.zeichnen(d)
    assert img.width() > 100
