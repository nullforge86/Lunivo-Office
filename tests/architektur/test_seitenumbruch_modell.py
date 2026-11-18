"""Seitenumbruch ohne Qt über dem Dokumentenmodell (``LayoutEngine``): Seiten, Spalten, Abschnitte, Tabellen, Bilder, Cursor und Treffertest."""
import pytest

from lunivo_writer.core.document.dokument import Tabelle
from lunivo_writer.core.geometry import Point
from lunivo_writer.core.layout import LayoutEngine
from lunivo_writer.core.textlayout.hb_engine import HarfBuzzEngine
from lunivo_writer.modelle.seite import PageSettings
from tests.hilfen_dokument import sitzung

NULL = {"abstand_vor": 0.0, "abstand_nach": 0.0}


def bauen(texte, seite=None, **format):
    """Ein Dokument mit einem Absatz je Text; ``format`` gilt für alle Absätze (Abstände sind standardmäßig null)."""
    s = sitzung("\n".join(texte), seite)
    s.absatzformat_anwenden({**NULL, **format}, absatz_ids=[a.id for a in s.dokument.absaetze()])
    return s


def setzen(dok, eng):
    return LayoutEngine(eng).berechnen(dok)


@pytest.fixture(scope="module")
def eng():
    return HarfBuzzEngine()


def test_seiten_und_zeilen(eng):
    seite = PageSettings()
    erg = setzen(bauen(["Wort " * 60] * 40, seite).dokument, eng)
    assert len(erg.seiten) >= 3
    for s in erg.seiten:
        unten = max(p.rect.bottom for p in s.plaetze if p.art == "zeile")
        assert unten <= (seite.margin_top_mm * 96 / 25.4) + seite.content_height_px + 1             # nichts unter dem Textrand
    erste = next(p for p in erg.seiten[0].plaetze if p.art == "zeile").rect
    assert erste.x == pytest.approx(seite.margin_left_mm * 96 / 25.4)


def test_spalten_und_abschnitt(eng):
    zwei = PageSettings(); zwei.spalten = 2
    s = bauen(["Wort " * 400], zwei)
    s.abschnitt_einfuegen(beginn="naechste", seite=PageSettings())
    s.text_einfuegen("Danach")
    erg = setzen(s.dokument, eng)
    xs = {round(p.rect.x) for p in erg.seiten[0].plaetze if p.art == "zeile"}
    assert len(xs) == 2                                                                         # zwei Spalten auf der Seite
    assert erg.seiten[-1].abschnitt == 1 and len(erg.seiten) >= 2


def test_umbruch_abstaende_und_bild(eng):
    s = bauen(["Eins", "Zwei"])
    a, b = list(s.dokument.absaetze())
    s.absatzformat_anwenden({"abstand_nach": 20.0}, absatz_ids=[a.id])
    s.absatzformat_anwenden({"abstand_vor": 30.0}, absatz_ids=[b.id])
    erg = setzen(s.dokument, eng)
    r1, r2 = erg.absaetze[a.id].zeilen[0][2], erg.absaetze[b.id].zeilen[0][2]
    assert r2.y - r1.bottom == pytest.approx(30)                                                # Abstände fallen zusammen: der größere gilt
    s2 = bauen(["Davor", "Danach"])
    d, n = list(s2.dokument.absaetze())
    s2.absatzformat_anwenden({"abstand_nach": 40.0}, absatz_ids=[d.id])
    s2.absatzformat_anwenden({"abstand_vor": 50.0}, absatz_ids=[n.id])
    geom = setzen(s2.dokument, eng)
    assert geom.absaetze[n.id].zeilen[0][2].y - geom.absaetze[d.id].zeilen[0][2].bottom == pytest.approx(50)
    s3 = bauen(["Text"])
    s3.setze_auswahl(s3.dokument.ende())
    s3.objekt_einfuegen("bild", 100.0, 200.0, bilddaten=b"\x89PNG-daten")
    s3.text_einfuegen("\nNach dem Bild")
    nach = list(s3.dokument.absaetze())[-1]
    s3.absatzformat_anwenden({"seitenumbruch_vor": True}, absatz_ids=[nach.id])
    erg3 = setzen(s3.dokument, eng)
    assert len(erg3.seiten) == 2 and any(p.rect.height >= 200 for p in erg3.seiten[0].plaetze if p.art == "zeile")


def test_absatzausrichtung_ist_in_der_seitengeometrie_sichtbar(eng):
    lang = "Viele Wörter bilden eine lange Zeile und füllen den Absatz mit genug Inhalt damit er in mehrere Zeilen umbricht und verteilt wird " * 2
    s = bauen(["Kurzer Absatz", "Kurzer Absatz", "Kurzer Absatz", lang])
    a = list(s.dokument.absaetze())
    for absatz, art in zip(a, ("links", "mitte", "rechts", "block")):
        s.absatzformat_anwenden({"ausrichtung": art}, absatz_ids=[absatz.id])
    erg = setzen(s.dokument, eng)
    x_links, x_mitte, x_rechts = (erg.absaetze[a[i].id].satz.zeilen[0].x for i in range(3))
    justify = erg.absaetze[a[3].id].satz.zeilen
    assert x_links == pytest.approx(0)
    assert 0 < x_mitte < x_rechts
    assert len(justify) > 1 and justify[0].wort_zuschlag > 0


def test_absatzeinzuege_sind_in_der_geometrie_sichtbar(eng):
    text = "Ein langer Absatz mit genügend Wörtern für mehrere Zeilen " * 20
    s = bauen([text, text])
    a, b = list(s.dokument.absaetze())
    s.absatzformat_anwenden({"einzug_links": 10.0, "einzug_rechts": 100.0, "einzug_erste": 5.0}, absatz_ids=[a.id])
    erg = setzen(s.dokument, eng)
    s_sem, s_basis = erg.absaetze[a.id].satz, erg.absaetze[b.id].satz
    assert s_sem.zeilen[0].x == pytest.approx(15)
    assert len(s_sem.zeilen) > len(s_basis.zeilen)


def test_zeilenabstaende(eng):
    s = bauen(["Zeile mit normaler Schrift"] * 5)
    a = list(s.dokument.absaetze())
    for absatz, fmt in zip(a, ({}, {"zeilenabstand_art": "vielfach", "zeilenabstand": 150.0}, {"zeilenabstand_art": "vielfach", "zeilenabstand": 1.5},
                               {"zeilenabstand_art": "genau", "zeilenabstand": 42.0}, {"zeilenabstand_art": "mindestens", "zeilenabstand": 42.0})):
        if fmt:
            s.absatzformat_anwenden(fmt, absatz_ids=[absatz.id])
    erg = setzen(s.dokument, eng)
    h = [erg.absaetze[x.id].satz.zeilen[0].hoehe for x in a]
    assert h[0] == pytest.approx(h[1] / 1.5)
    assert h[1] == pytest.approx(h[2])                                                          # 150 (Prozent) und 1,5 (Faktor) sind dasselbe
    assert h[3] == pytest.approx(42) and h[4] == pytest.approx(42)


def test_tabelle_cursor_treffer(eng):
    s = bauen(["Davor"])
    s.setze_auswahl(s.dokument.ende())
    s.tabelle_einfuegen(1, 2)
    tab = next(b for ab in s.dokument.abschnitte for b in ab.bloecke if isinstance(b, Tabelle))
    s.text_einfuegen("Links", pos=s.zelle_anfang(tab.id, 0, 0))
    s.text_einfuegen("Rechts " * 30, pos=s.zelle_anfang(tab.id, 0, 1))
    erg = setzen(s.dokument, eng)
    rechts = tab.zellen[0][1].bloecke[0]
    assert len(erg.absaetze[rechts.id].satz.zeilen) > 1                                            # lange Zelle bricht um
    seite, pt = erg.cursor(rechts.id, 7)
    absatz_id, i = erg.treffer(seite, Point(pt.x + 0.5, pt.y + 2))
    assert absatz_id == rechts.id and i == 7
    erster = next(a for a in s.dokument.absaetze())
    zeile = next(p for p in erg.seiten[0].plaetze if p.art == "zeile")
    absatz_id, i = erg.treffer(0, Point(zeile.rect.x + 1, zeile.rect.y + 1))
    assert absatz_id == erster.id and i == 0


def test_absatzregeln_zusammenhalten(eng):
    seite = PageSettings()
    h = setzen(bauen(["x"], seite).dokument, eng)
    hoehe = next(iter(h.absaetze.values())).satz.zeilen[0].hoehe
    zeilen_je_seite = int(seite.content_height_px // hoehe)

    def lauf(optionen: str | None):
        s = bauen(["Fuell"] * (zeilen_je_seite - 2) + ["Wort " * 120], seite)
        lang = list(s.dokument.absaetze())[-1]
        if optionen:
            s.absatzformat_anwenden({"optionen": optionen}, absatz_ids=[lang.id])
        return setzen(s.dokument, eng).absaetze[lang.id].zeilen
    ohne = lauf("kontrolle=0")
    zusammen = lauf("zusammen=1;kontrolle=0")
    assert ohne[0][0] == 0
    assert zusammen[0][0] == 1 or len({z[0] for z in zusammen}) == 1                            # der Absatz wird nicht geteilt: er beginnt auf der nächsten Seite


def test_zeilennummern(eng):
    s = bauen(["Eins", "Nicht gezählt", "Zwei", "Drei"])
    a = list(s.dokument.absaetze())
    s.absatzformat_anwenden({"optionen": "ohne_zeilennr=1"}, absatz_ids=[a[1].id])
    s.absatzformat_anwenden({"seitenumbruch_vor": True}, absatz_ids=[a[3].id])
    erg = setzen(s.dokument, eng)
    assert [n for *_r, n in erg.zeilennummern()] == [1, 2, 3]
    assert [n for *_r, n in erg.zeilennummern("seite")] == [1, 2, 1]


def test_tabstopps_links_rechts_und_standard(eng):
    s = bauen(["a\tb\tc", "a\tb"])
    a, b = list(s.dokument.absaetze())
    s.absatzformat_anwenden({"tabstopps": [[100.0, 0, ""], [300.0, 1, ""]]}, absatz_ids=[a.id])
    s.eigenschaft_setzen("tab_abstand", 50.0)
    erg = setzen(s.dokument, eng)
    satz = erg.absaetze[a.id].satz
    assert satz.cursor_x(2) == pytest.approx(100.0)                                             # „b“ beginnt am linken Stopp
    assert satz.cursor_x(5) == pytest.approx(300.0, abs=0.5)                                     # „c“ endet am rechtsbündigen Stopp
    assert erg.absaetze[b.id].satz.cursor_x(2) == pytest.approx(50.0)                           # ohne eigene Stopps: Standardabstand des Dokuments


def _tabelle(zeilen, kopfzeilen=0):
    s = bauen(["Davor"])
    s.setze_auswahl(s.dokument.ende())
    s.tabelle_einfuegen(zeilen, 2, format={"kopfzeilen": kopfzeilen} if kopfzeilen else None)
    tab = next(b for ab in s.dokument.abschnitte for b in ab.bloecke if isinstance(b, Tabelle))
    for r in range(zeilen):
        s.text_einfuegen(f"Zeile {r}", pos=s.zelle_anfang(tab.id, r, 0))
    return s, tab


def test_tabelle_kopfzeile_wiederholt(eng):
    s, tab = _tabelle(80, kopfzeilen=1)
    erg = setzen(s.dokument, eng)
    assert len(erg.seiten) >= 2
    kopien = [p for p in erg.seiten[1].plaetze if p.kopie]
    assert {p.art for p in kopien} >= {"zelle", "zeile"}                                         # die Kopfzeile steht oben auf Seite 2 noch einmal
    kopf_absatz = tab.zellen[0][0].bloecke[0]
    assert len(erg.absaetze[kopf_absatz.id].zeilen) == 1                                         # der Cursor kennt nur das Original


def test_tabellenzeile_hoeher_als_die_seite_wird_geteilt(eng):
    s = bauen(["Davor"])
    s.setze_auswahl(s.dokument.ende())
    s.tabelle_einfuegen(1, 2)
    tab = next(b for ab in s.dokument.abschnitte for b in ab.bloecke if isinstance(b, Tabelle))
    s.text_einfuegen("Wort " * 3000, pos=s.zelle_anfang(tab.id, 0, 0))
    erg = setzen(s.dokument, eng)
    zellabsatz = tab.zellen[0][0].bloecke[0]
    seiten = sorted({sx for sx, _z, _r in erg.absaetze[zellabsatz.id].zeilen})
    assert len(seiten) >= 2 and seiten[0] == 0                                                   # die Zelle beginnt auf Seite 1 und läuft weiter
    unten = PageSettings().margin_top_mm * 96 / 25.4 + PageSettings().content_height_px
    assert all(r.bottom <= unten + 1 for _s, _z, r in erg.absaetze[zellabsatz.id].zeilen)


def test_zeichenformat_schreibweise_laufweite(eng):
    s = bauen(["Maß und Zahl"] * 3)
    a = list(s.dokument.absaetze())

    def fmt(absatz, **f):
        from lunivo_writer.core.document.dokument import Auswahl, Position
        s.zeichenformat_anwenden(f, Auswahl(Position(absatz.id, 0), Position(absatz.id, absatz.laenge)))
    fmt(a[1], grossbuchstaben=True)
    fmt(a[2], zeichenabstand=3.0, zeichenabstand_art=1)                                      # 3 Bildpunkte nach jedem Zeichen (Art 1; ohne Art gilt Prozent)
    erg = setzen(s.dokument, eng)
    normal, gross, gesperrt = (erg.absaetze[x.id].satz for x in a)
    assert gross.text.startswith("MAß") or gross.text.startswith("MASS")
    assert gesperrt.cursor_x(12) > normal.cursor_x(12)


def test_dezimalstopp_fuellzeichen_und_absatzrahmen(eng):
    from lunivo_writer.core.rendering import DokumentRenderer
    from lunivo_writer.core.rendering.backend import RenderBackend
    s = bauen(["x\t12,50", "Abc"])
    a, b = list(s.dokument.absaetze())
    s.absatzformat_anwenden({"tabstopps": [[200.0, 3, ","]], "tabfuell": "200.00:punkt", "rahmen": "#ff0000|1|einfach"}, absatz_ids=[a.id])
    s.absatzformat_anwenden({"rahmen": "#ff0000|1|einfach"}, absatz_ids=[b.id])
    erg = setzen(s.dokument, eng)
    satz = erg.absaetze[a.id].satz
    assert satz.cursor_x(4) == pytest.approx(200.0, abs=0.5) and satz.tab_fuell                  # das Komma steht am Stopp, die Strecke davor ist gefüllt

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
    DokumentRenderer(eng).zeichne_seite(m, s.dokument, erg, 0, None)
    rot = [li for li in m.linien if li[2].color[:3] == (255, 0, 0)]
    assert len(rot) == 4                                                                       # ein gemeinsamer Rahmen um beide Absätze
    assert "12,50" in "".join(m.texte)


def test_silbentrennung_trennt_lange_woerter_am_zeilenende(eng):
    """Mit eingeschalteter Silbentrennung brechen lange Wörter an Silbengrenzen um; der Trennstrich gehört zur Zeile, der Text bleibt unverändert."""
    pytest.importorskip("pyphen")
    seite = PageSettings(); seite.silbentrennung = True
    text = "Donaudampfschifffahrtsgesellschaft Kaffeemaschinenbedienungsanleitung " * 12
    s = bauen([text], seite)
    erg = setzen(s.dokument, eng)
    satz = next(iter(erg.absaetze.values())).satz
    assert satz.text == text and any(z.box.trennstrich for z in satz.zeilen)
