"""Seitenumbruch ohne Qt über dem Dokumentenmodell: Seiten, Spalten, Abschnitte, Tabellen, Bilder, Cursor und Treffertest."""
import pytest

from lunivo_writer.core.document.model import (CharacterFormat, Document, Image, Paragraph, ParagraphFormat, Section, Table, TableCell, TableRow, TextRun)
from lunivo_writer.core.geometry import Point
from lunivo_writer.core.layout import umbrechen
from lunivo_writer.core.textlayout.hb_engine import HarfBuzzEngine
from lunivo_writer.modelle.seite import PageSettings


def absatz(text, **eig):
    return Paragraph(ParagraphFormat({"BlockTopMargin": 0, "BlockBottomMargin": 0, **eig}), [TextRun(text, CharacterFormat({"FontFamilies": ("Liberation Sans",), "FontPointSize": 12.0}))])


@pytest.fixture(scope="module")
def eng():
    return HarfBuzzEngine()


def test_seiten_und_zeilen(eng):
    seite = PageSettings()
    dok = Document([Section("naechste", seite, [absatz("Wort " * 60) for _ in range(40)])])
    erg = umbrechen(dok, eng)
    assert len(erg.seiten) >= 3
    hoehe = seite.content_height_px
    for s in erg.seiten:
        unten = max(p.rect.bottom for p in s.plaetze)
        assert unten <= (25 * 96 / 25.4) + hoehe + 1                                           # nichts unter dem Textrand
    erste = erg.seiten[0].plaetze[0].rect
    assert erste.x == pytest.approx(seite.margin_left_mm * 96 / 25.4)


def test_spalten_und_abschnitt(eng):
    zwei = PageSettings(); zwei.spalten = 2
    dok = Document([Section("naechste", zwei, [absatz("Wort " * 400)]), Section("naechste", PageSettings(), [absatz("Danach")])])
    erg = umbrechen(dok, eng)
    xs = {round(p.rect.x) for s in erg.seiten[:1] for p in s.plaetze}
    assert len(xs) == 2                                                                         # zwei Spalten auf der Seite
    assert erg.seiten[-1].abschnitt == 1 and len(erg.seiten) >= 2


def test_umbruch_abstaende_und_bild(eng):
    dok = Document([Section("naechste", PageSettings(), [
        absatz("Eins", BlockBottomMargin=20), absatz("Zwei", BlockTopMargin=30),
        Paragraph(ParagraphFormat({"PageBreakPolicy": 1}), [Image(b"", CharacterFormat({"ImageWidth": 100.0, "ImageHeight": 200.0}))])])])
    erg = umbrechen(dok, eng)
    r1, r2 = erg.absaetze[(0, 0)].zeilen[0][2], erg.absaetze[(0, 1)].zeilen[0][2]
    assert r2.y - r1.bottom == pytest.approx(30)                                                # Abstände fallen zusammen: der größere gilt
    assert len(erg.seiten) == 2 and erg.absaetze[(0, 2)].zeilen[0][2].height >= 200


def test_tabelle_cursor_treffer(eng):
    zellen = [TableCell(0, 0, content=[absatz("Links")]), TableCell(0, 1, content=[absatz("Rechts " * 30)])]
    tab = Table(1, 2, {}, [TableRow(zellen)])
    dok = Document([Section("naechste", PageSettings(), [absatz("Davor"), tab])])
    erg = umbrechen(dok, eng)
    assert erg.absaetze[(0, 1, 0, 1, 0)].satz.zeilen.__len__() > 1                                  # lange Zelle bricht um
    seite, pt = erg.cursor((0, 1, 0, 1, 0), 7)
    pfad, i = erg.treffer(seite, Point(pt.x + 0.5, pt.y + 2))
    assert pfad == (0, 1, 0, 1, 0) and i == 7
    pfad, i = erg.treffer(0, Point(erg.seiten[0].plaetze[0].rect.x + 1, erg.seiten[0].plaetze[0].rect.y + 1))
    assert pfad == (0, 0) and i == 0


def test_fussnoten_nehmen_platz_unten(eng):
    from lunivo_writer.core.document.model import Footnote
    marke = TextRun("1", CharacterFormat({"user:21": "f:7", "FontFamilies": ("Liberation Sans",), "FontPointSize": 12.0}))
    mit = Paragraph(ParagraphFormat({"BlockTopMargin": 0, "BlockBottomMargin": 0}), [TextRun("Text", CharacterFormat({"FontPointSize": 12.0})), marke])
    dok = Document([Section("naechste", PageSettings(), [absatz("Zeile") for _ in range(10)] + [mit])], notes=[Footnote(7, "f", "Eine Fußnote " * 10)])
    erg = umbrechen(dok, eng)
    noten = [p for s in erg.seiten for p in s.plaetze if p.art == "fussnote"]
    assert len(noten) == 1 and noten[0].pfad == ("note", 7)
    zeile = erg.absaetze[(0, 10)].zeilen[0][2]
    assert noten[0].rect.y >= zeile.bottom                                                          # die Note steht unter der Zeile mit der Marke
    PageSettingsHoch = PageSettings()
    voll = Document([Section("naechste", PageSettingsHoch, [absatz("Zeile") for _ in range(46)] + [mit])], notes=[Footnote(7, "f", "Eine Fußnote " * 10)])
    ohne = Document([Section("naechste", PageSettingsHoch, [absatz("Zeile") for _ in range(46)] + [absatz("Text")])])
    assert len(umbrechen(voll, eng).seiten) >= len(umbrechen(ohne, eng).seiten)


def test_textumfluss_um_schwebenden_rahmen(eng):
    from lunivo_writer.core.document.model import Frame
    from lunivo_writer.core.document.values import Length
    bild = Paragraph(ParagraphFormat({}), [Image(b"", CharacterFormat({"ImageWidth": 200.0, "ImageHeight": 150.0}))])
    rahmen = Frame({"CssFloat": 1, "FrameWidth": Length("fixed", 200.0), "FrameMargin": 8.0}, [bild])
    dok = Document([Section("naechste", PageSettings(), [rahmen, absatz("Wort " * 200)])])
    erg = umbrechen(dok, eng)
    zeilen = erg.absaetze[(0, 1)].zeilen
    erste, spaeter = zeilen[0][2], zeilen[-1][2]
    r = next(p for p in erg.seiten[0].plaetze if p.art == "rahmen")
    ort = erg.absaetze[(0, 1)].satz.zeilen
    assert ort[0].x >= 200                                                                    # die erste Zeile beginnt rechts vom Rahmen
    assert ort[-1].x == 0 and r.rect.width >= 200                                             # unterhalb des Rahmens läuft der Text über die volle Breite


def test_absatzregeln_schusterjunge_hurenkind_zusammen(eng):
    seite = PageSettings()
    hoehe = umbrechen(Document([Section("naechste", seite, [absatz("x")])]), HarfBuzzEngine()).absaetze[(0, 0)].satz.zeilen[0].hoehe
    zeilen_je_seite = int(seite.content_height_px // hoehe)

    def lauf(opt: str | None, laenge: int):
        fuell = [absatz("Fuell") for _ in range(zeilen_je_seite - 2)]                          # lässt genau Platz für ca. zwei Zeilen
        eig = {"user:1048614": opt} if opt else {}
        lang = absatz("Wort " * laenge, **eig)
        return umbrechen(Document([Section("naechste", seite, fuell + [lang])]), eng).absaetze[(0, zeilen_je_seite - 2)].zeilen
    ohne = lauf("kontrolle=0", 120)
    mit = lauf(None, 120)
    assert ohne[0][0] == 0 and mit[0][0] <= ohne[0][0] + 1
    zusammen = lauf("zusammen=1,kontrolle=0".replace(",", ";"), 120)
    assert zusammen[0][0] == 1 or len({z[0] for z in zusammen}) == 1                            # der Absatz wird nicht geteilt: er beginnt auf der nächsten Seite


def test_zeilennummern(eng):
    ohne = Paragraph(ParagraphFormat({"user:1048614": "ohne_zeilennr=1"}), [TextRun("Nicht gezählt", CharacterFormat({"FontPointSize": 12.0}))])
    dok = Document([Section("naechste", PageSettings(), [absatz("Eins"), ohne, absatz("Zwei"), Paragraph(ParagraphFormat({"PageBreakPolicy": 1}), [TextRun("Drei", CharacterFormat())])])])
    erg = umbrechen(dok, eng)
    assert [n for *_r, n in erg.zeilennummern()] == [1, 2, 3]
    assert [n for *_r, n in erg.zeilennummern("seite")] == [1, 2, 1]
