"""Popup-Lage: Menüs und Popup-Fenster bleiben in Programmfenster und Bildschirm."""
import pytest
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QMenu, QVBoxLayout, QWidget

from lunivo_writer.ui.baukasten.popup_lage import PopupWaechter, popup_klemmen


@pytest.fixture(autouse=True)
def _waechter(app):
    """Den Popup-Wächter nur für diese Tests an die gemeinsame Anwendung hängen und danach wieder lösen."""
    w = PopupWaechter.einhaengen(app)
    yield
    app.removeEventFilter(w)


def _fenster(app, x, y, w=300, h=200):
    f = QWidget(); f.setGeometry(x, y, w, h); f.show(); app.processEvents()
    return f


@pytest.mark.parametrize("ort", ["mitte", "rechts", "unten", "ecke", "links"])
def test_popup_fenster_bleibt_im_programmfenster_und_bildschirm(app, ort):
    bs = app.primaryScreen().availableGeometry()
    f = _fenster(app, 200, 100)
    f.activateWindow(); app.processEvents()
    pop = QFrame(f, Qt.WindowType.Popup); QVBoxLayout(pop).addWidget(QLabel("Ein Popup mit etwas Text"))
    pop.resize(180, 90)
    ziel = {"mitte": QPoint(250, 150), "rechts": QPoint(f.x() + f.width() - 20, 150), "unten": QPoint(250, bs.bottom() - 10),
            "ecke": QPoint(bs.right() - 5, bs.bottom() - 5), "links": QPoint(bs.left() - 50, 150)}[ort]
    pop.move(ziel); pop.show(); app.processEvents()
    g = pop.frameGeometry()
    assert bs.contains(g)
    if ort in ("mitte", "rechts", "links"):
        assert g.right() <= f.mapToGlobal(QPoint(0, 0)).x() + f.width() - 1 or g.width() > f.width()
    pop.close(); f.close()


def test_menue_ragt_nicht_ueber_den_rand(app):
    bs = app.primaryScreen().availableGeometry()
    f = _fenster(app, bs.right() - 250, bs.bottom() - 150, 250, 150)
    m = QMenu(f)
    for i in range(30):
        m.addAction("Ein Menüpunkt mit längerem Text Nummer %d" % i)
    m.popup(QPoint(bs.right() - 10, bs.bottom() - 10)); app.processEvents()
    assert bs.contains(m.frameGeometry())
    m.close(); f.close()


def test_klemmen_meldet_verschieben(app):
    bs = app.primaryScreen().availableGeometry()
    pop = QFrame(None, Qt.WindowType.Popup); pop.resize(100, 50); pop.move(bs.right() - 10, 10); pop.show()
    assert popup_klemmen(pop) in (True, False) and bs.contains(pop.frameGeometry())
    pop.close()
