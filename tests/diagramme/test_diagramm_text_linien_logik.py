"""Logik hinter den Fotos 28/29, 37/38, 39, 43, 54: Linientypen, Hauptrasterlinie, Textfüllung, 3D-Drehung/Transformieren, Textfeld."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QFont, QImage, QPainter, QPainterPath

from lunivo_writer.editor import diagramm as D, diagramm_format as F, texteffekt as TE, textfx as X

DATEN = {"art": "saeule_gruppiert", "titel": "Umsatz", "kategorien": ["A", "B", "C"], "reihen": {"X": [1, 2, 3], "Y": [3, 1, 2]}}


def _bild(tf, **z):
    return D.bild_aus_daten({**DATEN, "teil_format": tf, **z}, 400, 260, 1.0)


def _dunkel(img: QImage, r: QRectF) -> int:
    return sum(1 for y in range(int(r.top()), int(r.bottom())) for x in range(int(r.left()), int(r.right())) if img.pixelColor(x, y).lightness() < 128)


def test_kombinierte_typen_und_strichtypen_nach_foto(app):
    assert [k for k, _n in F.KOMBI_TYPEN] == ["einfach", "doppelt", "dick_duenn", "duenn_dick", "dreifach"]
    assert len(F.STRICHTYPEN) == 8 and F.strich_schluessel("gepunktet") == "quadratpunkt" and F.strich_schluessel("fein_gestrichelt") == "gestrichelt"
    assert F.stift({"art": "rundpunkt", "breite": 2}).dashPattern()[0] < 0.1
    assert len(F.stift({"art": "lang_strichpunktpunkt"}).dashPattern()) == 6
    flaechen = {k: sum(f.boundingRect().height() for f in X._kontur_pfade(_pfad(), 2.0, k)) for k, _n in F.KOMBI_TYPEN}
    assert len(X._kontur_pfade(_pfad(), 2.0, "dreifach")) == 3 and len(X._kontur_pfade(_pfad(), 2.0, "duenn_dick")) == 2
    assert flaechen["dreifach"] > flaechen["einfach"]
    e = _bild({"diagrammbereich": {"linie": {"breite": 3, "farbe": "#000000"}}})
    d = _bild({"diagrammbereich": {"linie": {"breite": 3, "farbe": "#000000", "kombiniert": "dreifach"}}})
    assert e != d


def _pfad() -> QPainterPath:
    p = QPainterPath(); p.moveTo(0, 20); p.lineTo(100, 20)
    return p


def test_hauptrasterlinie_teil_format_und_klickstreifen(app):
    namen = [n for _k, n in D.teile(DATEN)]
    assert namen.index("Vertikal (Wert) Achse Hauptrasterlinie") == namen.index("Vertikal (Wert) Achse") + 1
    assert namen[-2:] == ['Reihe"X"', 'Reihe"Y"'][-2:] or 'Reihe"X"' in namen
    geo = D.teil_geo(DATEN, 400, 260)
    assert geo.get("gitter_linien") and len(geo["gitter_linien"]) >= 3
    ohne = _bild({}); rot = _bild({"gitter_haupt": {"linie": {"farbe": "#ff0000", "breite": 3}}})
    r = geo["gitter_linien"][1]
    y = int(r.center().y()); x = int(r.right() - 4)
    assert rot.pixelColor(x, y).red() > 200 and rot.pixelColor(x, y).green() < 80
    assert ohne.pixelColor(x, y).red() < 230 or ohne.pixelColor(x, y).green() > 100
    aus = _bild({"gitter_haupt": {"linie": {"keine": True}}})
    assert aus.pixelColor(x, y) != rot.pixelColor(x, y)


def test_textfuellung_muster_und_bild_wirken_und_bleiben_gespeichert(app):
    w = {**TE.EFFEKT, "fuell": "muster", "fuell_pinsel": {"art": "muster", "key": "rein", "farbe": "#ff0000", "grund": "#ffffff"}}
    cf = TE.zu_format(w)
    back = TE.aus_format(cf)
    assert back["fuell"] == "muster" and back["fuell_pinsel"]["farbe"] == "#ff0000"
    assert TE.aus_text(TE.als_text(w))["fuell_pinsel"]["key"] == "rein"
    f = QFont(); f.setPixelSize(40); f.setBold(True)
    pfad, _g = X.text_pfad("MMM", f, QPointF(5, 45))
    img = QImage(150, 60, QImage.Format_ARGB32); img.fill(0xFFFFFFFF)
    p = QPainter(img); X.fx_zeichnen(p, pfad, {"fuell_pinsel": w["fuell_pinsel"]}, 45, 40, None, None); p.end()
    c = img.pixelColor(int(pfad.boundingRect().center().x()), int(pfad.boundingRect().center().y()))
    assert any(img.pixelColor(x, 30).red() > 200 and img.pixelColor(x, 30).green() < 60 for x in range(5, 140))
    ti = _bild({"titel": {"text": {"effekt": {"fuell": "muster", "farbe": "#000000", "fuell_pinsel": w["fuell_pinsel"]}}}})
    assert ti != _bild({})


def test_text_3d_drehung_und_warp_verformen_den_text(app):
    f = QFont(); f.setPixelSize(30)
    pfad, _g = X.text_pfad("abcde", f, QPointF(0, 30))
    r0 = pfad.boundingRect()
    assert X.pfad_verformen(pfad, {}) is pfad
    for art in ("bogen", "welle", "trichter", "kaskade_auf"):
        assert X.pfad_verformen(pfad, {"warp": {"art": art}}).boundingRect() != r0
    d = X.pfad_verformen(pfad, {"text_3d": {"x": 0, "y": 50, "z": 0, "perspektive": 45}}).boundingRect()
    assert d.width() < r0.width()
    z = X.pfad_verformen(pfad, {"text_3d": {"x": 0, "y": 0, "z": 90, "perspektive": 0}}).boundingRect()
    assert z.height() > z.width() * 0.8 and z.height() > r0.height() * 2
    glatt = _bild({"titel": {"text": {"effekt": {"warp": {"art": "bogen"}}}}})
    assert glatt != _bild({})


def test_textfeld_ausrichtung_raender_und_nicht_drehen(app):
    assert [n for _k, n in F.VERTIKAL] == ["Oben", "Oben zentriert", "Mitte", "Mitte zentriert", "Unten", "Unten zentriert"]
    assert F.feld_von(None)["vertikal"] == "mitte"
    assert F.feld_von(None)["raender"] == {"l": 0.0, "o": 0.0, "r": 0.0, "u": 0.0}
    assert F.feld_von(None, "legende")["raender"]["l"] == 0.0
    t = F.feld_von(None, "titel")["raender"]
    assert (t["l"], t["r"], t["o"], t["u"]) == (7.2, 7.2, 3.6, 3.6)                      # 0,10 / 0,05 Inch in pt
    assert F.feld_von({"feld": {"raender": {"l": 1.0}}}, "titel")["raender"]["l"] == 1.0
    ein = _bild({"titel": {"text": {"feld": {"vertikal": "oben_links"}}}})
    assert ein != _bild({})
    dreh = _bild({"titel": {"text": {"feld": {"gerade": True}}}}, objekt_dreh=0.0)
    assert D.bild_aus_daten({**DATEN, "teil_format": {"titel": {"text": {"feld": {"gerade": True, "winkel": 0}}}}, "objekt_dreh": 30}, 400, 260, 1.0) != dreh
    F.OBJEKT_DREH = 0.0


def test_mehrfachlinien_folgen_der_strichart_und_standard_bleibt():
    from PySide6.QtGui import QPainterPath
    from lunivo_writer.editor import textfx as X
    pf = QPainterPath(); pf.moveTo(0, 0); pf.lineTo(200, 0)
    for form in ("doppelt", "dick_duenn", "duenn_dick", "dreifach"):
        voll, gestr = X._kontur_pfade(pf, 3.0, form), X._kontur_pfade(pf, 3.0, form, "gestrichelt")
        n = lambda fl: sum(len(f.toSubpathPolygons()) for f in fl)
        assert n(gestr) > n(voll), form
    assert len(X._kontur_pfade(pf, 3.0, "doppelt", "gestrichelt")) == 2 and len(X._kontur_pfade(pf, 3.0, "doppelt")) == 1


def test_text_kopf_dropdowns_setzen_vorhandene_felder(app):
    from lunivo_writer.ui.baukasten.diagramme.diagramm_format_panel import DiagrammFormatPanel
    from lunivo_writer.ui.baukasten.diagramme.smartart_format_panel import SmartArtFormatPanel
    t = DiagrammFormatPanel().text_panel
    assert t.fuell_farbe_kopf.isHidden() and t.linie_knopf.isHidden()
    t._text_fuell_wahl("farbe:#1971c2")
    assert t.r_farbe.isChecked() and t.farbe.farbe == "#1971c2" and t._text_fuell_schluessel() == "farbe:#1971c2"
    t._text_fuell_wahl("")
    assert t.r_keine.isChecked()
    t._linie_gewaehlt("gestrichelt|doppelt|2.25")
    assert t.k_linie.isChecked() and t._text_linien_schluessel() == "gestrichelt|doppelt|2.25" and t.werte()["effekt"]["kontur_art"] == "gestrichelt"
    t._linie_gewaehlt("")
    assert t.k_keine.isChecked()
    assert not hasattr(SmartArtFormatPanel().text_panel, "kopf_fuell")


def test_textfuellung_fuenf_arten_und_fuell_pinsel(app):
    from lunivo_writer.ui.baukasten.diagramme.diagramm_format_panel import DiagrammFormatPanel
    from lunivo_writer.ui.baukasten.diagramme.smartart_format_panel import SmartArtFormatPanel
    t = DiagrammFormatPanel().text_panel
    assert t.r_farbe.isChecked() and t.werte()["effekt"] is None                      # Standard unverändert: Einfarbig
    t.r_muster.setChecked(True); t.p_muster.setCurrentIndex(2); t.p_vorn.setFarbe("#ff0000")
    e = t.werte()["effekt"]
    assert e["fuell"] == "muster" and e["fuell_pinsel"]["art"] == "muster" and e["fuell_pinsel"]["farbe"] == "#ff0000" and e["fuell_pinsel"]["key"] == t.p_muster.currentData()
    t2 = DiagrammFormatPanel().text_panel
    t2.setze({"teil": "titel", "text": {"effekt": e}})                                # zurücklesen
    assert t2.r_muster.isChecked() and t2.p_vorn.farbe == "#ff0000" and t2.werte()["effekt"]["fuell_pinsel"] == e["fuell_pinsel"]
    t2.r_bild.setChecked(True); t2.p_textur.setCurrentIndex(3)
    assert t2.werte()["effekt"]["fuell_pinsel"] == {"art": "textur", "key": t2.p_textur.currentData()}
    t2.r_farbe.setChecked(True)
    assert "fuell_pinsel" not in (t2.werte()["effekt"] or {})
    assert not hasattr(SmartArtFormatPanel().text_panel, "r_muster")




def test_kopfmenues_sind_kompakt_wie_die_vorlage(app):
    from lunivo_writer.ui.baukasten.dropdown.fuell_voreinstellungen import fuell_menue
    from lunivo_writer.ui.baukasten.dropdown.linien_voreinstellungen import linien_menue
    f = fuell_menue(None, ""); f.adjustSize()
    assert f.sizeHint().width() <= 230                       # Vorlage: ~222 px (vorher ~370)
    l = linien_menue(None, ""); l.adjustSize()
    assert l.sizeHint().width() <= 480                       # Standardmenü des Baukastens (VoreinstellungMenue)
