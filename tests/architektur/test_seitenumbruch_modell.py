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


def test_tabstopps_links_rechts_und_standard(eng):
    from lunivo_writer.core.document.values import TabStop
    dok = Document([Section("naechste", PageSettings(), [absatz("a\tb\tc", TabPositions=(TabStop(100.0, 0), TabStop(300.0, 1))), absatz("a\tb")])], text_option={"tab_stop_distance": 50.0})
    erg = umbrechen(dok, eng)
    satz = erg.absaetze[(0, 0)].satz
    assert satz.cursor_x(2) == pytest.approx(100.0)                                             # „b“ beginnt am linken Stopp
    assert satz.cursor_x(5) == pytest.approx(300.0, abs=0.5)                                     # „c“ endet am rechtsbündigen Stopp
    assert erg.absaetze[(0, 1)].satz.cursor_x(2) == pytest.approx(50.0)                         # ohne eigene Stopps: Standardabstand des Dokuments


def _tabelle(zeilen, eig=None, text=lambda r: f"Zeile {r}"):
    return Table(zeilen, 2, eig or {}, [TableRow([TableCell(r, 0, content=[absatz(text(r))]), TableCell(r, 1, content=[absatz("x")])]) for r in range(zeilen)])


def test_tabelle_kopfzeile_wiederholt_und_ausgerichtet(eng):
    from lunivo_writer.core.document.values import Length
    tab = _tabelle(80, {"TableHeaderRowCount": 1, "FrameWidth": Length("fixed", 300.0), "BlockAlignment": 0x4})
    erg = umbrechen(Document([Section("naechste", PageSettings(), [tab])]), eng)
    assert len(erg.seiten) >= 2
    kopien = [p for p in erg.seiten[1].plaetze if p.kopie]
    assert {p.art for p in kopien} == {"zelle", "zeile"} and kopien[0].pfad[-2:] == (0, 0)       # die Kopfzeile steht oben auf Seite 2 noch einmal
    assert len(erg.absaetze[(0, 0, 0, 0, 0)].zeilen) == 1                                       # der Cursor kennt nur das Original
    zellen = [p for p in erg.seiten[0].plaetze if p.art == "zelle"]
    seite = PageSettings()
    mitte = seite.margin_left_mm * 96 / 25.4 + seite.content_width_px / 2
    assert (min(z.rect.x for z in zellen) + max(z.rect.right for z in zellen)) / 2 == pytest.approx(mitte, abs=3)


def test_tabellenzeile_hoeher_als_die_seite_wird_geteilt(eng):
    tab = _tabelle(1, text=lambda r: "Wort " * 3000)
    erg = umbrechen(Document([Section("naechste", PageSettings(), [absatz("Davor"), tab])]), eng)
    seiten = sorted({s for s, _z, _r in erg.absaetze[(0, 1, 0, 0, 0)].zeilen})
    assert len(seiten) >= 2 and seiten[0] == 0                                                   # die Zelle beginnt auf Seite 1 und läuft weiter
    unten = PageSettings().margin_top_mm * 96 / 25.4 + PageSettings().content_height_px
    assert all(r.bottom <= unten + 1 for _s, _z, r in erg.absaetze[(0, 1, 0, 0, 0)].zeilen)


def test_endnoten_am_ende_und_rahmen_als_block(eng):
    from lunivo_writer.core.document.model import Footnote, Frame
    marke = TextRun("i", CharacterFormat({"user:21": "e:4", "FontPointSize": 12.0}))
    rahmen = Frame({"FrameBorder": 2.0, "FramePadding": 10.0, "FrameMargin": 5.0}, [absatz("Im Rahmen")])
    dok = Document([Section("naechste", PageSettings(), [Paragraph(ParagraphFormat({}), [TextRun("Text", CharacterFormat({"FontPointSize": 12.0})), marke]), rahmen, absatz("Danach")])],
                   notes=[Footnote(4, "e", "Eine Endnote")])
    erg = umbrechen(dok, eng)
    plaetze = erg.seiten[-1].plaetze
    note = next(p for p in plaetze if p.art == "endnote")
    assert note.daten.text.startswith("i  Eine Endnote") and note.rect.y > erg.absaetze[(0, 2)].zeilen[0][2].bottom
    assert any(p.art == "notenlinie" for p in plaetze)
    r = next(p for p in plaetze if p.art == "rahmen")
    innen = erg.absaetze[(0, 1, 0)].zeilen[0][2]
    assert innen.x == pytest.approx(r.rect.x + 12.0) and innen.y == pytest.approx(r.rect.y + 12.0)   # Rahmenstrich und Innenabstand
    assert erg.absaetze[(0, 2)].zeilen[0][2].y >= r.rect.bottom + 5.0                                 # Rand unter dem Rahmen


def test_zeichenformat_schreibweise_laufweite_unterstreichung(eng):
    from lunivo_writer.core.layout import eigenschaften as E
    def lauf(**eig):
        return Paragraph(ParagraphFormat({}), [TextRun("Maß und Zahl", CharacterFormat({"FontPointSize": 12.0, **eig}))])
    dok = Document([Section("naechste", PageSettings(), [lauf(), lauf(FontCapitalization=1), lauf(FontLetterSpacing=3.0, FontLetterSpacingType=1), lauf(FontWordSpacing=10.0)])])
    erg = umbrechen(dok, eng)
    normal, gross, gesperrt, weit = (erg.absaetze[(0, i)].satz for i in range(4))
    assert gross.text == "MAß UND ZAHL"                                                          # „ß“ bliebe als „SS“ nicht ein Zeichen: es bleibt stehen
    assert gesperrt.cursor_x(12) == pytest.approx(normal.cursor_x(12) + 12 * 3.0)
    assert weit.cursor_x(12) == pytest.approx(normal.cursor_x(12) + 2 * 10.0)
    stil = E.stil(CharacterFormat({"TextUnderlineStyle": 3, "FontOverline": True}))
    assert stil["underline"] and stil["underline_dash"] == "dot" and stil["overline"]


def test_dezimalstopp_fuellzeichen_kapitaelchen_absatzrahmen(eng):
    from lunivo_writer.core.document.values import TabStop
    from lunivo_writer.core.rendering.backend import RenderBackend
    from lunivo_writer.core.rendering.seite import zeichne_seite
    dezimal = absatz("x\t12,50", **{"TabPositions": (TabStop(200.0, 3, ","),), "user:1048613": "200.00:punkt", "user:1048581": "#ff0000|1|einfach"})
    kap = Paragraph(ParagraphFormat({"user:1048581": "#ff0000|1|einfach"}), [TextRun("Abc", CharacterFormat({"FontPointSize": 12.0, "FontCapitalization": 3}))])
    erg = umbrechen(Document([Section("naechste", PageSettings(), [dezimal, kap])]), eng)
    satz = erg.absaetze[(0, 0)].satz
    assert satz.cursor_x(4) == pytest.approx(200.0, abs=0.5) and satz.tab_fuell == {1: "."}     # das Komma steht am Stopp, die Strecke davor ist gepunktet
    k = erg.absaetze[(0, 1)].satz
    assert k.text == "ABC" and k.laeufe[1].schrift.size_pt == pytest.approx(12.0 * 0.8)

    class Mitschnitt(RenderBackend):
        def __init__(self):
            self.linien, self.texte = [], []
        def draw_line(self, start, end, style):
            self.linien.append((start, end, style))
        def draw_text(self, text, position, font, style):
            self.texte.append(text)
        def draw_rect(self, rect, style):
            pass
    m = Mitschnitt()
    zeichne_seite(m, erg, 0, eng, False)
    rot = [li for li in m.linien if li[2].color[:3] == (255, 0, 0)]
    assert len(rot) == 4                                                                       # ein gemeinsamer Rahmen um beide Absätze
    assert any(li[2].dash == "dot" for li in m.linien) and "12,50" in "".join(m.texte)


def test_navigation_cursor_auswahl_bewegung(eng):
    from lunivo_writer.core.editing import Caret
    from lunivo_writer.core.layout import navigation as NAV
    dok = Document([Section("naechste", PageSettings(), [absatz("Erste Zeile hier"), absatz("Wort " * 60), absatz("Ende")])])
    erg = umbrechen(dok, eng)
    seite, r = NAV.cursor_rechteck(erg, Caret((0, 0), 6))
    assert seite == 0 and r.x == pytest.approx(erg.absaetze[(0, 0)].zeilen[0][2].x + erg.absaetze[(0, 0)].satz.cursor_x(6))
    fl = NAV.auswahl_rechtecke(erg, Caret((0, 0), 6), Caret((0, 1), 3))[0]
    assert len(fl) == 2 and fl[0].y < fl[1].y                                                   # Rest des ersten Absatzes (mit Absatzende) und Anfang des zweiten
    assert NAV.bewegen(erg, Caret((0, 0), 16), "rechts")[0] == Caret((0, 1), 0)                 # über das Absatzende
    assert NAV.bewegen(erg, Caret((0, 1), 0), "links")[0] == Caret((0, 0), 16)
    assert NAV.bewegen(erg, Caret((0, 0), 8), "wort_rechts")[0] == Caret((0, 0), 11)
    assert NAV.bewegen(erg, Caret((0, 0), 8), "wort_links")[0] == Caret((0, 0), 6)
    unten, x = NAV.bewegen(erg, Caret((0, 0), 6), "runter")
    assert unten.pfad == (0, 1) and abs(erg.absaetze[(0, 1)].satz.cursor_x(unten.versatz) - erg.absaetze[(0, 0)].satz.cursor_x(6)) < 6
    zweite, _x = NAV.bewegen(erg, unten, "runter", x)
    assert erg.absaetze[(0, 1)].satz.zeile_von(zweite.versatz) == 1
    assert NAV.bewegen(erg, zweite, "hoch", x)[0] == unten
    ende = NAV.bewegen(erg, unten, "zeilenende")[0]
    assert erg.absaetze[(0, 1)].satz.zeile_von(ende.versatz) == 0 and ende.versatz > unten.versatz
    assert NAV.bewegen(erg, ende, "zeilenanfang")[0] == Caret((0, 1), 0)
    assert NAV.bewegen(erg, unten, "ende")[0] == Caret((0, 2), 4) and NAV.bewegen(erg, unten, "anfang")[0] == Caret((0, 0), 0)
    assert NAV.wort_bei(erg, Caret((0, 0), 8)) == (Caret((0, 0), 6), Caret((0, 0), 11))
