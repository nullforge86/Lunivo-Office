"""Textsatz ohne Qt: HarfBuzz/FreeType-Engine (Maße gegen die Qt-Umsetzung), Zeilenumbruch, Ausrichtung, Cursor und Treffertest."""
import pytest

from lunivo_writer.core.textlayout import FontSpec
from lunivo_writer.core.textlayout.hb_engine import HarfBuzzEngine
from lunivo_writer.core.textlayout.paragraph import Objekt, absatz_setzen, zeilenhoehe

TEXT = "Dies ist ein längerer Absatz mit vielen Wörtern, der umbrochen werden muss, weil die Zeile schmal ist. Donaudampfschifffahrtsgesellschaft!"
F = FontSpec("Liberation Sans", 11)


@pytest.fixture(scope="module")
def eng():
    return HarfBuzzEngine()


def test_masse_und_umbruch(eng):
    m = eng.font_metrics(F)
    assert m.ascent > 0 and m.descent > 0 and m.line_spacing == pytest.approx(m.ascent + m.descent)
    assert eng.measure_text("", F) == 0 and eng.measure_text("ab", F) < eng.measure_text("abc", F)
    zeilen = eng.layout_paragraph(TEXT, F, 200)
    assert "".join(TEXT[z.start:z.start + z.length] for z in zeilen) == TEXT                  # nichts geht verloren
    assert all(z.width <= 200.5 for z in zeilen) and len(zeilen) >= 4
    assert TEXT[zeilen[0].start:zeilen[0].start + zeilen[0].length].endswith(" ")             # Umbruch nach dem Wort


def test_masse_wie_qt(eng, app):
    from lunivo_writer.adapter.qt.textlayout import QtTextLayoutEngine
    q = QtTextLayoutEngine()
    for fam in ("Liberation Sans", "Carlito", "DejaVu Serif"):
        for pt in (9, 11, 14):
            f = FontSpec(fam, pt)
            a, b = eng.font_metrics(f), q.font_metrics(f)
            assert abs(a.ascent - b.ascent) < 0.1 and abs(a.line_spacing - b.line_spacing) < 0.1
            assert abs(eng.measure_text(TEXT, f) - q.measure_text(TEXT, f)) < 0.005 * q.measure_text(TEXT, f)
            assert [(z.start, z.length) for z in eng.layout_paragraph(TEXT, f, 250)] == [(z.start, z.length) for z in q.layout_paragraph(TEXT, f, 250)]


def test_ausrichtung_und_einzug(eng):
    links = absatz_setzen(eng, [(TEXT, F)], 300).zeilen
    rechts = absatz_setzen(eng, [(TEXT, F)], 300, "right").zeilen
    mitte = absatz_setzen(eng, [(TEXT, F)], 300, "center").zeilen
    block = absatz_setzen(eng, [(TEXT, F)], 300, "justify").zeilen
    assert links[0].x == 0 and rechts[0].x == pytest.approx(300 - links[0].box.width) and mitte[0].x == pytest.approx((300 - links[0].box.width) / 2)
    assert block[0].wort_zuschlag > 0 and block[-1].wort_zuschlag == 0                         # letzte Zeile bleibt linksbündig
    erste = absatz_setzen(eng, [(TEXT, F)], 300, einzug_erste=40, einzug_links=10).zeilen
    assert erste[0].x == 50 and erste[1].x == 10 and erste[0].box.width <= 300 - 50 + 0.5
    assert zeilenhoehe(17.0, "proportional", 150) == 25.5 and zeilenhoehe(17.0, "fixed", 20) == 20 and zeilenhoehe(17.0, "min", 12) == 17.0


def test_cursor_und_treffer(eng):
    satz = absatz_setzen(eng, [(TEXT, F)], 220, "justify")
    for i in (0, 5, 40, len(TEXT) - 1):
        x = satz.cursor_x(i)
        z = satz.zeilen[satz.zeile_von(i)]
        assert satz.treffer(x, z.y + 1) == i
    assert satz.treffer(-50, 0) == 0
    assert satz.treffer(1000, satz.zeilen[-1].y + 1) == len(TEXT)


def test_gemischte_laeufe_und_bild(eng):
    gross = FontSpec("Liberation Sans", 24, 700)
    satz = absatz_setzen(eng, [("Klein ", F), ("GROSS", gross), ("\ufffc", Objekt(50, 80)), (" Ende", F)], 400)
    z = satz.zeilen[0]
    assert z.box.height >= 80 and z.box.ascent >= 80                                           # das Bild bestimmt die Zeilenhöhe
    assert satz.vorschuebe[satz.text.index("\ufffc")] == 50
    leer = absatz_setzen(eng, [], 300, leer_schrift=gross)
    m = eng.font_metrics(gross)
    import math
    assert len(leer.zeilen) == 1 and leer.zeilen[0].box.height == math.ceil(m.ascent) + math.ceil(m.descent)               # ganze Bildpunkte wie QTextLine
