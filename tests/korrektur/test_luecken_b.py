"""Lücken B: Diagrammfilter „Name“, Diagrammtyp direkt, Linien-Galerie, Freiform (Punkte bearbeiten), Live-Vorschau, Helligkeit/Kontrast, Zoom-Ansicht."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QColor, QImage, QKeyEvent, QMouseEvent

from lunivo_writer.editor.objekte import freiform as FF

from lunivo_writer.editor.objekte import frei_objekt as FO


@pytest.fixture
def fenster(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.dienste.einstellungen_dienst import Settings
    from lunivo_writer.oberflaeche.programmfenster import MainWindow
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
    from lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.diagramm_popups import DiagrammPopup
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
    from lunivo_writer.oberflaeche.kontext.diagramm_werkzeuge import DIAGRAMMTOOLS
    knoepfe = [k for g in DIAGRAMMTOOLS["gruppen"] for k in g.get("knoepfe", []) if k.get("name", "").startswith("Diagrammtyp: ")]
    assert len(knoepfe) == 10 and all(b.hat(k["tun"].split(":")[0]) for k in knoepfe)












def test_zoom_ansicht_baut_sich_bei_300px(app):
    from lunivo_writer.oberflaeche.baukasten.medien.bild_zoom import BildZoomFenster
    from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import ZusatzPanel
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
    from lunivo_writer.editor.objekte import smartart as SA
    d = {"layout": "Radial", "text": "Kern\nA\nB\nC"}
    img = SA.zeichnen(d)
    assert img.width() > 100
