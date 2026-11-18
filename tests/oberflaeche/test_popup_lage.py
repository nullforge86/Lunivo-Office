"""Popup-Lage: Menüs und Popup-Fenster bleiben in Programmfenster und Bildschirm."""
import pytest
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QMenu, QVBoxLayout, QWidget

from lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste import MenueListe
from lunivo_writer.oberflaeche.baukasten.dropdown.popup_lage import PopupVerhalten, popup_klemmen


class _Popup(PopupVerhalten, QFrame):
    """Ein Popup-Fenster, das die Öffnungsregeln erbt."""
    def __init__(self, parent):
        super().__init__(parent, Qt.WindowType.Popup)


def _fenster(app, x, y, w=300, h=200):
    f = QWidget(); f.setGeometry(x, y, w, h); f.show(); app.processEvents()
    return f


@pytest.mark.parametrize("ort", ["mitte", "rechts", "unten", "ecke", "links"])
def test_popup_fenster_bleibt_im_programmfenster_und_bildschirm(app, ort):
    bs = app.primaryScreen().availableGeometry()
    f = _fenster(app, 200, 100)
    f.activateWindow(); app.processEvents()
    pop = _Popup(f); QVBoxLayout(pop).addWidget(QLabel("Ein Popup mit etwas Text"))
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
    m = MenueListe(f)
    for i in range(30):
        m.addAction("Ein Menüpunkt mit längerem Text Nummer %d" % i)
    m.popup(QPoint(bs.right() - 10, bs.bottom() - 10)); app.processEvents()
    assert bs.contains(m.frameGeometry())
    m.close(); f.close()


def test_klemmen_meldet_verschieben(app):
    bs = app.primaryScreen().availableGeometry()
    pop = _Popup(None); pop.resize(100, 50); pop.move(bs.right() - 10, 10); pop.show()
    assert popup_klemmen(pop) in (True, False) and bs.contains(pop.frameGeometry())
    pop.close()


def test_popup_bleibt_in_der_seitenleiste_mit_randabstand(app):
    """Ein Popup, das aus einem Bereich mit der Eigenschaft popupGrenze aufklappt, liegt ganz in diesem Bereich, mit POPUP_RAND Abstand."""
    from lunivo_writer.oberflaeche.baukasten.basis.mass import POPUP_RAND
    bs = app.primaryScreen().availableGeometry()
    f = _fenster(app, 100, 100, 700, 300)
    panel = QWidget(f); panel.setProperty("popupGrenze", True); panel.setGeometry(400, 0, 300, 300); panel.show()
    pop = _Popup(panel); QVBoxLayout(pop).addWidget(QLabel("Ein Popup mit etwas längerem Text darin"))
    pop.resize(200, 60); pop.move(f.mapToGlobal(QPoint(400, 50))); pop.show(); app.processEvents()
    g = pop.frameGeometry(); pg = QRect(panel.mapToGlobal(QPoint(0, 0)), panel.size())
    assert pg.adjusted(POPUP_RAND, 0, -POPUP_RAND, 0).contains(g.left(), g.top()) and g.right() <= pg.right() - POPUP_RAND
    assert bs.contains(g)
    pop.close(); f.close()


def test_alle_aufklappenden_fenster_erben_popup_verhalten():
    """Wächter: Kein rohes ``QMenu(``/``(QMenu)`` außerhalb von menue_liste.py und kein Popup-Fenster (``Qt.Popup`` im Konstruktor) ohne ``PopupVerhalten``."""
    import pathlib, re
    wurzel = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "lunivo_writer"
    roh, ohne = [], []
    for p in wurzel.rglob("*.py"):
        n = p.relative_to(wurzel).as_posix()
        s = p.read_text(encoding="utf-8", errors="replace")
        if n not in ("oberflaeche/baukasten/dropdown/menue_liste.py", "oberflaeche/baukasten/dropdown/popup_lage.py") and re.search(r"\bQMenu\(|class \w+\((?:\w+, )*QMenu\)", s):
            roh.append(n)
        if n != "oberflaeche/baukasten/dropdown/popup_lage.py" and re.search(r"__init__\([^)]*Qt\.Popup", s) and "PopupVerhalten" not in s:
            ohne.append(n)
    assert not roh, "rohes QMenu außerhalb von MenueListe: " + ", ".join(roh)
    assert not ohne, "Popup-Fenster ohne PopupVerhalten: " + ", ".join(ohne)


def test_alle_menues_sind_mindestens_gleich_breit(app):
    """Die Basisklasse gibt jedem Menü dieselbe Mindestbreite (aus mass.py); kurze Menüs sind nicht schmaler."""
    from lunivo_writer.oberflaeche.baukasten.basis.mass import DROPDOWN_BREITE_MIN
    for text in ("Ja", "Ein deutlich längerer Menüpunkt"):
        m = MenueListe(); m.eintrag(text); m.popup(QPoint(50, 50)); app.processEvents()
        assert m.width() >= DROPDOWN_BREITE_MIN
        m.close()


def test_menue_liste_behaelt_symbole_kuerzel_zustaende_und_untermenues(app):
    """Der zentrale Menübaustein: Symbol, Tastenkürzel (nur angezeigt oder echt), Haken, Aktivierung und Untermenü bleiben erhalten."""
    from PySide6.QtGui import QIcon, QPixmap
    pm = QPixmap(8, 8); pm.fill(Qt.GlobalColor.red)
    m = MenueListe()
    a = m.eintrag("Einfügen", symbol=QIcon(pm), kuerzel="Strg+V")
    b = m.eintrag("Haken", haken=True, aktiv=False, tip="grau")
    echt = m.eintrag("Echt", kuerzel="Ctrl+E", echt=True)
    u = m.untermenue("Mehr")
    u.eintrag("Innen")
    assert "Strg+V" in a.text() and not a.icon().isNull()
    assert b.isCheckable() and b.isChecked() and not b.isEnabled() and b.toolTip() == "grau"
    assert echt.shortcut().toString() == "Ctrl+E"
    assert isinstance(u, MenueListe) and [x.text() for x in u.actions()] == ["Innen"]
    assert any(x.menu() is u for x in m.actions())
