"""Seitenplan (Layout-Schicht, Phase 1): Spaltenraster, ungleich breite Spalten in DOCX, Bereiche aus den Abschnitten."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import io
import zipfile

import pytest
from PySide6.QtGui import QTextDocument

from lunivo_writer.dienste import docx_leser, docx_schreiber
from lunivo_writer.editor.layout.seitenplan import Seitenplan, gleiche_geometrie, spalten
from lunivo_writer.modelle.seite import PageSettings, mm_to_px


def _seite(**kw) -> PageSettings:
    return PageSettings(width_mm=210, height_mm=297, margin_left_mm=20, margin_right_mm=20, **kw)      # Textbreite 170 mm


def test_raster_gleich_breit():
    r = spalten(_seite(spalten=2, spalten_abstand_mm=10))
    assert len(r) == 2 and r[0].x == 0 and r[0].breite == pytest.approx(mm_to_px(80)) and r[1].x == pytest.approx(mm_to_px(90))


def test_raster_ungleich_breit_und_rueckfall():
    p = _seite(spalten=2, spalten_raster_mm=[[100.0, 50.0], [20.0, 0.0]])
    a, b = spalten(p)
    assert a.breite == pytest.approx(mm_to_px(100)) and b.x == pytest.approx(mm_to_px(150)) and b.breite == pytest.approx(mm_to_px(20))
    falsch = _seite(spalten=2, spalten_raster_mm=[[100.0, 50.0], [90.0, 0.0]])          # Summe passt nicht zur Textbreite
    assert [round(s.breite) for s in spalten(falsch)] == [round(mm_to_px(80))] * 2
    assert not gleiche_geometrie(p, _seite(spalten=2, spalten_abstand_mm=50.0))           # anderes Raster: andere Geometrie


def test_docx_ungleiche_spalten_hin_und_zurueck(app, tmp_path):
    p = _seite(spalten=2, spalten_raster_mm=[[100.0, 50.0], [20.0, 0.0]])
    pfad = str(tmp_path / "s.docx")
    docx_schreiber.write_docx(pfad, QTextDocument(), p, {})
    xml = zipfile.ZipFile(pfad).read("word/document.xml").decode()
    assert 'w:equalWidth="0"' in xml and xml.count("<w:col ") == 2
    gelesen = docx_leser.read_docx(pfad)[1]
    assert gelesen.spalten == 2 and [round(b) for b, _a in gelesen.spalten_raster_mm] == [100, 20] and round(gelesen.spalten_raster_mm[0][1]) == 50


def test_gleich_breite_spalten_schreiben_kein_raster(app, tmp_path):
    pfad = str(tmp_path / "g.docx")
    docx_schreiber.write_docx(pfad, QTextDocument(), _seite(spalten=2, spalten_abstand_mm=10), {})
    assert "<w:col " not in zipfile.ZipFile(pfad).read("word/document.xml").decode()
    assert docx_leser.read_docx(pfad)[1].spalten_raster_mm is None


def test_plan_ohne_abschnitte_ist_ein_bereich(app):
    pl = Seitenplan.aus_dokument(QTextDocument(), _seite())
    assert len(pl.bereiche) == 1 and pl.bereiche[0].neue_seite and pl.bereiche[0].spalten[0].breite == pytest.approx(mm_to_px(170))


@pytest.mark.skipif(not os.path.isfile(os.path.expanduser("~/Schreibtisch/00467262742bd3b5eac2de95ac748cb1d50990fc479bac8b44a68c550fd8b98f.docx")), reason="Beispieldatei nicht vorhanden")
def test_plan_der_formular_docx():
    """Vier Abschnitte; der letzte beginnt fortlaufend mit zwei ungleichen Spalten (5220 + 3424 Lücke + 1466 Zwanzigstelpunkt)."""
    pfad = os.path.expanduser("~/Schreibtisch/00467262742bd3b5eac2de95ac748cb1d50990fc479bac8b44a68c550fd8b98f.docx")
    doc, page = docx_leser.read_docx(pfad)[:2]
    pl = Seitenplan.aus_dokument(doc, page)
    assert len(pl.bereiche) == 4 and pl.bereiche[3].beginn == "fortlaufend"
    a, b = pl.bereiche[3].spalten
    assert round(a.breite) == round(mm_to_px(5220 / 1440 * 25.4)) and round(b.breite) == round(mm_to_px(1466 / 1440 * 25.4)) and b.x > a.breite + 200


def test_editor_beginnt_abschnitt_auf_neuem_blatt(app):
    """Ein Abschnitt „nächste Seite“ beginnt im Editor auf einem neuen Blatt — wie in Druck, PDF und Word (vorher floss der Text weiter)."""
    from PySide6.QtGui import QTextCursor
    from lunivo_writer.editor.seite import abschnitte as AB
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("Eins\nZwei\nDrei")
    doc = ed.document()
    c = QTextCursor(doc); c.setPosition(4)
    AB.einfuegen(doc, c, "naechste", ed.page)
    ed._recount()
    erster = doc.findBlock(AB.beginn(doc, 1))
    lauf = ed._lauf
    blatt = lauf.blaetter[lauf.blatt_von_block(erster.blockNumber())]
    assert blatt.index == 1 and lauf.blockBoundingRect(erster).y() == pytest.approx(blatt.oben + blatt.text_oben, abs=1)    # oben auf dem zweiten Blatt
    assert ed._blatt_anzahl() >= 2


def test_editor_fortlaufender_abschnitt_gleicher_geometrie_bleibt_auf_der_seite(app):
    from PySide6.QtGui import QTextCursor
    from lunivo_writer.editor.seite import abschnitte as AB
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("Eins\nZwei\nDrei")
    doc = ed.document()
    c = QTextCursor(doc); c.setPosition(4)
    AB.einfuegen(doc, c, "fortlaufend", ed.page)
    ed._recount()
    assert ed._lauf.blatt_von_block(doc.findBlock(AB.beginn(doc, 1)).blockNumber()) == 0                # noch auf dem ersten Blatt
