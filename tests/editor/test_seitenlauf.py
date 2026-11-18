"""Seitenlauf über die Layout-Engine des Kerns (``core.layout.LayoutEngine``): Ränder, Abschnitte, Spalten, Tabellen, Trefferprüfung.

Der frühere ``Seitenlauf`` (ein Qt-Dokumentlayout) gibt es nicht mehr; diese Tests prüfen dieselben Eigenschaften an der einen maßgeblichen Layout-Engine."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest

from lunivo_writer.core.geometry import Point
from lunivo_writer.core.layout import LayoutEngine
from lunivo_writer.modelle.seite import PageSettings, mm_to_px
from tests.hilfen_dokument import seitenzahl, sitzung


def _layout(dok):
    return LayoutEngine().berechnen(dok)


def _zeilen(seite):
    return [p for p in seite.plaetze if p.art == "zeile" and not p.kopie]


def test_ein_abschnitt_ein_blatt_raender_wie_eingestellt():
    seite = PageSettings(margin_left_mm=30, margin_top_mm=20)
    erg = _layout(sitzung("Text", seite).dokument)
    assert len(erg.seiten) == 1
    z = _zeilen(erg.seiten[0])[0]
    assert z.rect.x == pytest.approx(mm_to_px(30), abs=1.0) and z.rect.y == pytest.approx(mm_to_px(20), abs=1.0)


def test_abschnitt_beginnt_neues_blatt_mit_eigenen_raendern():
    s = sitzung("Eins", PageSettings(margin_left_mm=30))
    s.abschnitt_einfuegen(beginn="naechste", seite=PageSettings(margin_left_mm=50))
    s.text_einfuegen("Zwei")
    erg = _layout(s.dokument)
    assert len(erg.seiten) == 2
    assert _zeilen(erg.seiten[1])[0].rect.x == pytest.approx(mm_to_px(50), abs=1.0)


def test_fortlaufend_gleiche_geometrie_bleibt_auf_dem_blatt():
    s = sitzung("Eins")
    s.abschnitt_einfuegen(beginn="fortlaufend", seite=PageSettings())
    s.text_einfuegen("Zwei")
    assert seitenzahl(s.dokument) == 1


def test_absatz_laeuft_ueber_die_seite_und_nichts_geht_verloren():
    text = " ".join(f"Wort{i}" for i in range(4000))
    d = sitzung(text).dokument
    erg = _layout(d)
    assert len(erg.seiten) > 1
    a = next(iter(d.absaetze()))
    ort = erg.absaetze[a.id]
    assert {z[0] for z in ort.zeilen} == set(range(len(erg.seiten)))             # der Absatz steht auf allen Seiten
    assert sum(s.zeilen[zi].box.length for _sx, zi, _r in ort.zeilen for s in [ort.satz]) >= len(text) - 1


def test_ungleiche_spalten_setzen_text_in_zwei_spalten():
    seite = PageSettings(spalten=2, spalten_raster_mm=[[80.0, 10.0], [80.0, 0.0]], margin_left_mm=20, margin_right_mm=30)
    erg = _layout(sitzung(" ".join(f"Wort{i}" for i in range(600)), seite).dokument)
    xs = {round(p.rect.x) for p in _zeilen(erg.seiten[0])}
    assert len(xs) == 2


def test_treffer_findet_zeile_und_zeichen():
    s = sitzung("Hallo Welt")
    erg = _layout(s.dokument)
    z = _zeilen(erg.seiten[0])[0]
    aid, index = erg.treffer(0, Point(z.rect.x + 1, z.rect.y + 2))
    assert aid == next(iter(s.dokument.absaetze())).id and index == 0


def test_tabelle_zellen_nebeneinander_untereinander():
    s = sitzung("Vor")
    s.tabelle_einfuegen(2, 2)
    erg = _layout(s.dokument)
    zellen = [p for p in erg.seiten[0].plaetze if p.art == "zelle"]
    assert len(zellen) == 4
    assert len({round(p.rect.y) for p in zellen}) == 2 and len({round(p.rect.x) for p in zellen}) == 2


def test_tabellenzeilen_laufen_auf_das_naechste_blatt():
    s = sitzung("Vor")
    s.tabelle_einfuegen(120, 2)
    erg = _layout(s.dokument)
    assert len(erg.seiten) > 1 and any(p.art == "zelle" for p in erg.seiten[1].plaetze)
