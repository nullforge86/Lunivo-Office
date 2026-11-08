"""Diagramm einfügen: Fenster in der Seitenleiste (Arten in einer Spalte, Kombinationstabelle) und Klappe am Band-Knopf."""
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QWidget

from lunivo_writer.editor import diagramm as D
from lunivo_writer.ui.baukasten.controls.zusatz_panel import ZusatzPanel
from lunivo_writer.ui.dialogs.diagramm_fenster import DiagrammDialog

@pytest.fixture
def fenster(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document()
    yield w
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


GRUPPEN = [g for g, _s, _u in D.TYPEN]


def _panel(app, breite):
    p = ZusatzPanel(); p.verfuegbar, p.verfuegbar_hoehe = breite, 587; p.resize(breite + 36, 727)
    d = DiagrammDialog(None)
    p.oeffne(d); p.show(); app.processEvents(); app.processEvents()
    return p, d


def _ragt(p, d):
    vp = p.stapel.currentWidget().sa.viewport()
    return [type(c).__name__ for c in d.findChildren(QWidget) if c.isVisible() and c.width() > 0
            and (c.mapTo(vp, c.rect().topLeft()).x() < -1 or c.mapTo(vp, c.rect().topRight()).x() > vp.width())]


def test_diagramm_fenster_passt_bei_300_und_444(app):
    for breite in (300, 444):
        p, d = _panel(app, breite)
        for zeile in (0, GRUPPEN.index("Kombination")):
            d.arten.setCurrentRow(zeile); app.processEvents(); app.processEvents()
            assert not _ragt(p, d), (breite, zeile)
            assert d.arten.flow() == d.arten.Flow.TopToBottom and not d.arten.isWrapping()      # eine Spalte
            assert d.vorschau.height() >= d.vorschau.pixmap().height()                            # Vorschau nicht abgeschnitten
        p.close()


def test_kombination_tabelle_wirkt_auf_werte(app):
    p, d = _panel(app, 300)
    d.arten.setCurrentRow(GRUPPEN.index("Kombination")); app.processEvents()
    assert not d.kombi_teil.isHidden() and len(d._kombi_felder) == 3
    texte = {l.text() for l in d.kombi_teil.findChildren(type(d.name)) if l.isVisible()}
    assert {"Datenreihenname", "Diagrammtyp", "Sekundärachse", "Kombinationsdiagramme erstellen."} <= texte
    _l, box, kasten = d._kombi_felder[0]
    box.setCurrentIndex(box.findData("linie")); kasten.setChecked(True)
    assert d.daten()["art"] == "kombi_eigen" and d.daten()["kombi"][0] == ["linie", True]
    p.close()


def test_diagramm_klappe_hat_die_eintraege(fenster):
    m = fenster.befehle.klappe("diagrammKlappe")
    assert [a.text().replace("&", "") for a in m.actions() if a.text()] == ["Diagramm …", "Neuer Zeichenbereich"]


def test_jeder_untertyp_zeichnet_und_alte_namen_gelten(app):
    from PySide6.QtGui import QColor
    erwartet = {"Linie": 6, "Kreis": 5, "Fläche": 3, "X Y (Punkt)": 7, "Kurs": 4}
    assert {g: len(u) for g, _s, u in D.TYPEN if g in erwartet} == erwartet and "Vorlagen" not in GRUPPEN
    for _g, _s, unter in D.TYPEN:
        for u, _n in unter:
            t, k, r = D.beispiel(u)
            for kachel in (False, True):
                img = D.bild(u, t, k, r, 220, 160, kachel=kachel)
                assert not img.isNull() and any(img.pixelColor(x, y) != QColor("white") for x in range(0, img.width(), 7) for y in range(0, img.height(), 7)), u
    t, k, r = D.beispiel("kreis_3d")
    a, b = (D.bild(x, "", k, r, 220, 160).convertToFormat(D.QImage.Format_RGB32) for x in ("kreis", "kreis_3d"))
    assert a != b                                              # 3D-Kreis sieht wirklich anders aus
    for alt, neu in (("punkte_linien", "punkte_gerade_punkte"), ("Säulen", "saeule_gruppiert")):
        assert D.ALT[alt] == neu
    assert "linie_glatt" in D.NAMEN and not D.bild("linie_glatt", "T", D.BEISPIEL_KATEGORIEN, D.BEISPIEL_REIHEN, 200, 140).isNull()
    assert not D.bild("punkte_linien", "T", D.BEISPIEL_KATEGORIEN, D.BEISPIEL_REIHEN, 200, 140).isNull()
    assert D._art({"art": "vorlage_klar"}) == "saeule_gruppiert"        # feste Vorlagen für alte Dokumente bleiben
