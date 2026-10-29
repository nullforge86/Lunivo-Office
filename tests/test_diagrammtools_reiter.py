"""Kontext-Reiter „Diagrammtools“ und „Bildtools“: erscheinen bei markiertem Diagramm bzw. Bild, jeder Knopf hat einen Befehl."""
from __future__ import annotations

from PySide6.QtWidgets import QToolButton

from lunivo_writer.ui.contextual.diagramm_tools import DIAGRAMMTOOLS
from lunivo_writer.ui.contextual.image_tools import BILDTOOLS


def _fenster(tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document()
    return w


def _zu(w):
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def _knoepfe(plan):
    for g in plan["gruppen"]:
        for e in g.get("knoepfe", []):
            if e.get("name") and not e.get("zeilenumbruch"):
                yield e


def test_diagramm_zeigt_diagrammtools_mit_allen_befehlen(app, tmp_path):
    from lunivo_writer.editor import diagramm as D, frei_objekt as FO
    w = _fenster(tmp_path); w.show()
    i = w.band.kontext_index["diagramm"]
    assert w.band.reiter.tabText(i) == "Diagrammtools" and not w.band.reiter.isTabVisible(i)
    ed = w.current_editor()
    FO.einfuegen(ed, "diagramm", {"art": "saeule_gruppiert", "titel": "T", "kategorien": list(D.BEISPIEL_KATEGORIEN),
                                  "reihen": dict(D.BEISPIEL_REIHEN)}, 480, 300)
    w._sync_format()
    assert w.band.reiter.isTabVisible(i) and w.band.reiter.currentIndex() == i
    b = w.band.b
    for e in _knoepfe(DIAGRAMMTOOLS):
        assert (e.get("tun") and b.hat(e["tun"])) or (e.get("klappe") and b.klappe(e["klappe"]) is not None), e["name"]
    galerie = next(g for g in DIAGRAMMTOOLS["gruppen"] if g.get("galerie"))
    from lunivo_writer.ui.baukasten.bild_diagramm_menues import GALERIEN
    spec = GALERIEN[galerie["galerie"]](b)
    assert len(spec["kacheln"]) == 4 and len(D.STILE) >= 12 and spec["menue"] is not None
    spec["kacheln"][3][2]()                                                  # Kachel „Dunkel“ wirkt auf das Diagramm
    assert FO.daten_lesen(ed, "diagramm")["stil"] == 3
    for k in w.band.stapel.widget(i).findChildren(QToolButton):
        assert not k.property("fehlt"), k.toolTip()
    ed._frei_sel = None
    w._sync_format()
    assert not w.band.reiter.isTabVisible(i)
    _zu(w)


def test_bildtools_jeder_knopf_hat_einen_befehl(app, tmp_path):
    w = _fenster(tmp_path); w.show()
    b = w.band.b
    for e in _knoepfe(BILDTOOLS):
        assert (e.get("tun") and b.hat(e["tun"].partition(":")[0])) or (e.get("klappe") and w.band._klappe(e["klappe"]) is not None), e["name"]
    seite = w.band.stapel.widget(w.band.kontext_index["bild"])
    for k in seite.findChildren(QToolButton):
        assert not k.property("fehlt"), k.toolTip()
    _zu(w)
