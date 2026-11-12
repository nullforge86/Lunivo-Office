"""Auswahlfeld: Popup begrenzt, Zeilenhöhe, Kürzung, API wie QComboBox."""
import pytest
from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QApplication, QComboBox, QVBoxLayout, QWidget

from lunivo_writer.oberflaeche.baukasten.basis.mass import DROPDOWN_ZEILE_PAD_V
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld import Auswahlfeld, Schriftauswahl, _KuerzDelegate

LANG = "Sehr langer Eintrag " * 12 + "ENDE"


def _schmal(app, feld):
    w = QWidget(); w.setFixedWidth(300)
    l = QVBoxLayout(w); l.addWidget(feld)
    return w


def test_popup_nicht_breiter_als_eltern(app):
    f = Auswahlfeld(); f.addItems(["kurz", LANG])
    w = _schmal(app, f); w.show(); QCoreApplication.processEvents()
    f.showPopup(); QCoreApplication.processEvents()
    assert f.view().window().width() <= 300
    f.hidePopup()
    assert f.width() <= 300


def test_zeilenhoehe_und_kuerzung(app):
    f = Auswahlfeld(); f.addItem(LANG)
    h = f.view().sizeHintForRow(0)
    assert h == f.fontMetrics().height() + 2 * DROPDOWN_ZEILE_PAD_V      # so kompakt wie die Menüzeilen
    assert isinstance(f.itemDelegate(), _KuerzDelegate)
    t = f.fontMetrics().elidedText(LANG, Qt.TextElideMode.ElideMiddle, 150)
    assert t.startswith("Sehr") and t.endswith("ENDE") and "…" in t


def test_api_gleich(app):
    f = Auswahlfeld(); assert isinstance(f, QComboBox)
    f.addItem("A", 1); f.addItem("B", 2)
    seen = []; f.currentIndexChanged.connect(seen.append)
    f.setCurrentIndex(1)
    assert f.currentData() == 2 and f.findData(1) == 0 and f.currentText() == "B" and seen == [1]


def test_editierbar_bleibt_eingabefaehig(app):
    f = Auswahlfeld(); f.setEditable(True); f.addItem("x")
    w = _schmal(app, f); w.show()
    f.lineEdit().setText("eigener Text")
    assert f.currentText() == "eigener Text"
    f.grab()


def test_feste_breite_bleibt(app):
    f = Auswahlfeld(); f.addItem(LANG); f.setFixedWidth(120); f.show()
    assert f.width() == 120


def test_schriftauswahl_popup(app):
    f = Schriftauswahl()
    w = _schmal(app, f); w.show(); QCoreApplication.processEvents()
    f.showPopup(); QCoreApplication.processEvents()
    assert f.view().window().width() <= 300
    f.hidePopup()


@pytest.mark.parametrize("name,ort,anzahl", [
    ("mitte", "mitte", 3), ("rechts", "rechts", 3), ("unten", "unten", 3), ("ecke", "ecke", 3),
    ("ragt_raus", "ragt_raus", 3), ("viele_unten", "unten", 40), ("links_aussen", "links", 3),
])
def test_popup_bleibt_im_bildschirm(app, name, ort, anzahl):
    """Auch an Bildschirmrändern (rechts, unten, Ecke, Fenster ragt hinaus, sehr viele Einträge) liegt die Liste ganz im Bildschirm."""
    bs = app.primaryScreen().availableGeometry()
    lage = {"mitte": (200, 100), "rechts": (bs.right() - 300, 100), "unten": (200, bs.bottom() - 60),
            "ecke": (bs.right() - 300, bs.bottom() - 60), "ragt_raus": (bs.right() - 150, 100), "links": (bs.left() - 100, 100)}[ort]
    c = Auswahlfeld()
    for i in range(anzahl):
        c.addItem(LANG + str(i))
    w = QWidget(); QVBoxLayout(w).addWidget(c)
    w.setGeometry(lage[0], lage[1], 300, 60 if ort in ("unten", "ecke") else 200)
    w.show(); app.processEvents()
    c.showPopup(); app.processEvents()
    assert bs.contains(c.view().window().geometry())
    c.hidePopup(); w.close()
