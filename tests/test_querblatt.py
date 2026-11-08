"""Querformat-Blatt zwischen Hochformat-Blättern (Einfügen ▸ Leere Seite ▸ Horizontal): der Editor zeigt jedes Blatt in seiner
eigenen Größe untereinander, gespeichert wird ohne den Zusatz der Anzeige (``editor/querblatt.py``)."""
from __future__ import annotations

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication

from lunivo_writer.editor import querblatt
from lunivo_writer.models.page import mm_to_px
from lunivo_writer.services import docx_reader


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


def _warte(ms=400):
    from PySide6.QtCore import QElapsedTimer
    t = QElapsedTimer(); t.start()
    while t.elapsed() < ms:
        QApplication.processEvents()


def _hoch_quer_hoch(w, quertext="Querblatt. " * 40):
    e = w.current_editor()
    e.selectAll(); e.textCursor().removeSelectedText()
    e.insertPlainText("Hochformat oben. " * 10)
    w.befehle.leereSeite(None, True); _warte(200)
    e.insertPlainText(quertext); _warte(300)
    w.befehle.leereSeite(None, False); _warte(200)
    e.insertPlainText("Wieder hoch. " * 5)
    e._recount(); _warte(600)
    return e


def test_querblatt_breit_und_mittig(fenster):
    e = _hoch_quer_hoch(fenster)
    plan = [(round(p.width_mm), round(p.height_mm)) for p in e._qplan]
    assert plan == [(210, 297), (297, 210), (210, 297)]
    assert e.width() >= int(mm_to_px(297) * e.zoom)
    hoch, quer = e._blatt(0), e._blatt(1)
    assert quer["W"] > hoch["W"] and quer["x"] == 0 and hoch["x"] > 0                    # Hochformat steht mittig
    assert e.blatt_oben(1) > e.blatt_oben(0) + hoch["H"] - 1 and e.blatt_oben(2) > e.blatt_oben(1) + quer["H"] - 1
    # ein Klick auf das Querblatt trifft dessen Text, auch rechts außerhalb der Breite eines Hochformat-Blattes
    x = int(quer["x"] + quer["ml"] + quer["cw"] - 20)
    y = int(e.blatt_oben(1) + quer["mt"] + 5)
    c = e.cursorForPosition(QPoint(x, y))
    assert c.block().text().startswith("Querblatt")
    # der Text des Querblattes ist breiter umbrochen als der eines Hochformat-Blattes
    lay = c.block().layout()
    assert lay.lineAt(0).naturalTextWidth() > hoch["cw"]


def test_speichern_ohne_zusatz(fenster, tmp_path):
    e = _hoch_quer_hoch(fenster)
    doc = e.document()
    assert querblatt.hat_zusatz(doc)                                                      # die Hochformat-Absätze haben ihn
    rein = querblatt.bereinigte_kopie(doc)
    assert not querblatt.hat_zusatz(rein)
    b = rein.firstBlock()
    while b.isValid():
        assert b.blockFormat().rightMargin() == 0
        b = b.next()
    out = tmp_path / "q.docx"
    from lunivo_writer.services import file_service
    file_service.save(str(out), doc, e.page, dict(e._meta), sicherung=False)
    d2, _p, _m, _r = docx_reader.read_docx(str(out))
    assert not querblatt.hat_zusatz(d2)
    assert querblatt.rechts_px(doc.firstBlock().blockFormat()) == 0                     # der Benutzer sieht seinen Einzug


def test_langer_text_auf_zwei_querblaettern(fenster):
    e = _hoch_quer_hoch(fenster, ("Viel Text auf dem Querblatt. " * 20 + "\n") * 25)
    plan = [(round(p.width_mm), round(p.height_mm)) for p in e._qplan]
    assert plan.count((297, 210)) >= 2 and plan[0] == (210, 297) and plan[-1] == (210, 297)
    # keine Zeile eines Querblattes reicht unter dessen Textfläche
    assert querblatt.grenzen(e.document(), e.page, e._sp_geo()["ch"], e.zoom) == []
