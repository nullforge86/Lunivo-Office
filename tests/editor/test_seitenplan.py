"""Seitenplan (Layout-Schicht): Spaltenraster und ungleich breite Spalten in DOCX (über das Dokumentenmodell)."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import zipfile

import pytest

from lunivo_writer.editor.layout.seitenplan import gleiche_geometrie, spalten
from lunivo_writer.modelle.seite import PageSettings, mm_to_px
from tests.hilfen_dokument import dokument, docx_rundlauf


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
    gelesen, _schreib, _lese, pfad = docx_rundlauf(dokument("", p), tmp_path, "s.docx")
    xml = zipfile.ZipFile(pfad).read("word/document.xml").decode()
    assert 'w:equalWidth="0"' in xml and xml.count("<w:col ") == 2
    seite = gelesen.abschnitte[0].seite
    assert seite.spalten == 2 and [round(b) for b, _a in seite.spalten_raster_mm] == [100, 20] and round(seite.spalten_raster_mm[0][1]) == 50


def test_gleich_breite_spalten_schreiben_kein_raster(app, tmp_path):
    gelesen, _schreib, _lese, pfad = docx_rundlauf(dokument("", _seite(spalten=2, spalten_abstand_mm=10)), tmp_path, "g.docx")
    assert "<w:col " not in zipfile.ZipFile(pfad).read("word/document.xml").decode()
    assert gelesen.abschnitte[0].seite.spalten_raster_mm is None
