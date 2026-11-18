"""Die gemeinsamen Bausteine der Oberfläche: Farbpalette, Linien, Menü-Liste, Kachel-Auswahl, Maßfeld, Dialoggerüst."""
from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtWidgets import QColorDialog, QDialog, QLabel

from lunivo_writer.oberflaeche.baukasten import (
    DialogRahmen, FarbFeld, FarbKnopf, FarbPalette, Linie, LinienWahl, MassSpin, MenueListe, RahmenMenue, RahmenSeiten,
    RasterAuswahl, set_einheit,
)
from lunivo_writer.oberflaeche.baukasten.basis import farben as F


def _sauber():
    from PySide6.QtCore import QSettings
    QSettings().remove(F.ZULETZT_SCHLUESSEL)


def test_abstufungen_und_raster(app):
    raster = F.thema_raster()
    assert len(raster) == 6 and all(len(z) == 10 for z in raster)
    assert raster[0] == list(F.THEMA_FARBEN)
    blau = F.abstufungen("#1971c2")
    assert len(blau) == 5 and QColor(blau[0]).lightness() > QColor("#1971c2").lightness() > QColor(blau[4]).lightness()
    assert all(QColor(f).isValid() for z in raster for f in z)


def test_palette_meldet_farbe_keine_und_merkt_zuletzt(app):
    _sauber()
    pal = FarbPalette(keine_text="Keine Farbe")
    erhalten = []
    pal.gewaehlt.connect(erhalten.append)
    pal.waehle(QColor("#c92a2a"))
    pal.waehle(None)
    assert [e.name() if e is not None else None for e in erhalten] == ["#c92a2a", None]
    assert F.zuletzt_laden() == ["#c92a2a"]
    # beim nächsten Öffnen steht „Zuletzt benutzt“ da
    assert any(l.text() == "Zuletzt benutzt" for l in FarbPalette().findChildren(QLabel))
    _sauber()


def test_palette_ueberfahren_meldet_vorschau(app):
    pal = FarbPalette()
    geseh, ende = [], []
    pal.ueberfahren.connect(lambda c: geseh.append(c.name())); pal.verlassen.connect(lambda: ende.append(1))
    from lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.farbpalette import _Kachel
    k = pal.findChildren(_Kachel)[0]
    k.enterEvent(None); k.leaveEvent(None)
    assert geseh == [k.farbe] and ende == [1]


def test_weitere_farben_ueber_das_farbenfenster(app, monkeypatch):
    from lunivo_writer.oberflaeche.baukasten.felder.farbwaehler import FarbenDialog
    _sauber()
    monkeypatch.setattr(FarbenDialog, "exec", lambda self: 1)
    monkeypatch.setattr(FarbenDialog, "farbe", lambda self: QColor("#123456"))
    pal = FarbPalette(); erhalten = []
    pal.gewaehlt.connect(erhalten.append)
    pal._weitere()
    assert erhalten[0].name() == "#123456" and F.zuletzt_laden()[0] == "#123456"
    monkeypatch.setattr(FarbenDialog, "exec", lambda self: 0)                    # Abbrechen
    pal._weitere()
    assert len(erhalten) == 1
    _sauber()


def test_farbfeld_uebernimmt_farbe_aus_der_palette(app, monkeypatch):
    feld = FarbFeld("#000000", "Test", keine_text="Keine")
    monkeypatch.setattr(FarbFeld, "_zeige_popup", lambda self, pal: pal.waehle(QColor("#2f9e44")))
    gemeldet = []
    feld.farbeGeaendert.connect(gemeldet.append)
    feld.click()
    assert feld.farbe == "#2f9e44" and gemeldet == ["#2f9e44"] and feld.text() == "#2F9E44" and feld.icon().pixmap(14, 14).toImage().pixelColor(7, 7).name() == "#2f9e44"
    monkeypatch.setattr(FarbFeld, "_zeige_popup", lambda self, pal: pal.waehle(None))
    feld.click()
    assert feld.farbe == "" and feld.text() == "Keine"


def test_farbknopf_klick_wendet_letzte_farbe_an(app):
    from PySide6.QtGui import QIcon, QPixmap
    pm = QPixmap(22, 22); pm.fill(QColor("white"))
    k = FarbKnopf(QIcon(pm), "Schriftfarbe", "#c92a2a")
    erhalten = []
    k.angewendet.connect(erhalten.append)
    k.click()
    assert erhalten[-1].name() == "#c92a2a"
    k.menu().waehle(QColor("#1971c2"))
    assert k.farbe == "#1971c2" and erhalten[-1].name() == "#1971c2"
    k.click()
    assert erhalten[-1].name() == "#1971c2"
    _sauber()


def test_linie_text_stift_und_zeichnen(app):
    li = Linie("#c92a2a", 1.5, "gestrichelt")
    assert li.text() == "#c92a2a|1.5|gestrichelt"
    assert Linie.aus_text(li.text()) == li
    assert Linie.aus_text("") is None and Linie.aus_text("x|y") is None
    assert li.stift(96 / 72).widthF() == 1.5 * 96 / 72
    bild = QImage(60, 20, QImage.Format_ARGB32); bild.fill(QColor("white"))
    p = QPainter(bild)
    Linie("#000000", 3.0, "doppelt").zeichne(p, 2, 10, 58, 10)
    p.end()
    zeilen = [bild.pixelColor(30, y).lightness() < 128 for y in range(20)]
    assert sum(zeilen) >= 2                            # doppelt: zwei getrennte Striche


def test_linienwahl_meldet_aenderungen(app):
    w = LinienWahl(Linie("#000000", 1.0, "einfach"))
    gemeldet = []
    w.geaendert.connect(gemeldet.append)
    w.art.setCurrentIndex(w.art.findData("gepunktet"))
    w.breite.setCurrentIndex(w.breite.findData(3.0))
    w.farbe._uebernehmen(QColor("#1971c2"))
    assert w.linie() == Linie("#1971c2", 3.0, "gepunktet") and gemeldet[-1] == w.linie()
    w.setLinie(Linie("#c92a2a", 0.75, "doppelt"))
    assert w.linie() == Linie("#c92a2a", 0.75, "doppelt")


def test_rahmenmenue_meldet_seiten(app):
    m = RahmenMenue()
    gemeldet = []
    m.gewaehlt.connect(lambda s, k: gemeldet.append((k, s)))
    namen = {a.text(): a for a in m.actions() if a.text()}
    namen["Rahmenlinie unten"].trigger(); namen["Rahmenlinien außen"].trigger(); namen["Kein Rahmen"].trigger()
    assert gemeldet[0] == ("unten", RahmenSeiten.UNTEN)
    assert gemeldet[1][1] == RahmenSeiten.AUSSEN and RahmenSeiten.OBEN in gemeldet[1][1] and RahmenSeiten.INNEN_H not in gemeldet[1][1]
    assert gemeldet[2] == ("kein", RahmenSeiten.KEINE)
    assert "Innere horizontale Rahmenlinie" not in [a.text() for a in RahmenMenue(innen=False).actions()]


def test_menueliste_aus_beschreibung(app):
    ausgeloest = []
    m = MenueListe.aus_liste([
        {"text": "Öffnen", "kuerzel": "Strg+O", "aktion": lambda: ausgeloest.append("auf")},
        {"text": "Fett", "haken": True, "aktion": lambda: ausgeloest.append("fett")},
        "-",
        {"text": "Mehr", "untermenue": [{"text": "Innen", "aktion": lambda: ausgeloest.append("innen")}]},
        {"text": "Grau", "aktiv": False},
    ])
    a = m.actions()
    assert a[0].text() == "Öffnen\tStrg+O" and a[1].isCheckable() and a[1].isChecked() and a[2].isSeparator()
    a[0].trigger(); a[3].menu().actions()[0].trigger()
    assert ausgeloest == ["auf", "innen"] and not a[4].isEnabled()


def test_rasterauswahl_meldet_schluessel(app):
    r = RasterAuswahl(spalten=2)
    r.kacheln([("a", "Eins", None), ("b", "Zwei", lambda p, rc: p.drawRect(rc)), ("c", "Drei", None)], aktuell="b")
    gemeldet, fuss = [], []
    r.gewaehlt.connect(gemeldet.append)
    r.fuss("Mehr …", lambda: fuss.append(1))
    assert r.knoepfe["b"].isChecked() and not r.knoepfe["a"].isChecked()
    r.knoepfe["c"].click()
    assert gemeldet == ["c"]


def test_massfeld_versteht_einheiten(app):
    try:
        set_einheit("Zentimeter")
        s = MassSpin(); s.setRange(0, 500)
        s.setValue(25.0)
        assert s.text() == "2,50 cm"
        assert abs(s.valueFromText("30 mm") - 30.0) < 1e-6 and abs(s.valueFromText("2 cm") - 20.0) < 1e-6
    finally:
        set_einheit("Millimeter")


def test_dialograhmen_vorschau_und_zusatzknopf(app):
    gemalt = []
    class D(DialogRahmen):
        def ergebnis(self): return 42
    d = D(None, "Titel", lambda p, r: gemalt.append(r))
    d.zeile("Name", QLabel("x"))
    kn = d.zusatzknopf("Entfernen")
    d.resize(300, 300); d.show(); d.aktualisieren(); app.processEvents()
    assert d.windowTitle() == "Titel" and gemalt and d.ergebnis() == 42 and kn.text() == "Entfernen"
    kn.click()
    assert d.result() == QDialog.Accepted


# ---- Absatzrahmen: einzelne Seiten ---------------------------------------------------------------------------------------

def test_linie_seiten_im_text_und_alt_kompatibel(app):
    assert Linie.aus_text("#ff0000|1.5|doppelt").seiten == "tblr"                      # alter Text: alle vier Seiten
    assert Linie("#ff0000", 1.5, "doppelt").text() == "#ff0000|1.5|doppelt"
    li = Linie("#000000", 1.0, "einfach", "bh")
    assert li.text() == "#000000|1|einfach|bh" and Linie.aus_text(li.text()) == li
    assert li.mit_seiten("hbt").seiten == "tbh"                                         # feste Reihenfolge


def test_rahmenmenue_schaltet_seiten_im_absatz(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.dienste.einstellungen_dienst import Settings
    from lunivo_writer.oberflaeche.programmfenster import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document()
    e = w.current_editor(); e.insertPlainText("Ein Absatz")
    b = w.befehle
    b._rahmen_seite("unten");  assert e.absatzrahmen().seiten == "b"
    b._rahmen_seite("oben");   assert e.absatzrahmen().seiten == "tb"
    b._rahmen_seite("unten");  assert e.absatzrahmen().seiten == "t"
    b._rahmen_seite("alle");   assert e.absatzrahmen().seiten == "tblrh"
    b._rahmen_seite("aussen"); assert e.absatzrahmen().seiten == "tblr"
    b._rahmen_seite("kein");   assert e.absatzrahmen() is None
    m = b.menue_absatzRahmen()
    assert "Innere vertikale Rahmenlinie" not in [a.text() for a in m.actions()]
    assert "Innere horizontale Rahmenlinie" in [a.text() for a in m.actions()]
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def test_rahmenfenster_liefert_linie_schattierung_und_seitenrand(app):
    from lunivo_writer.oberflaeche.baukasten.formatierung.rahmen_schattierung import RahmenSchattierungDialog
    d = RahmenSchattierungDialog(None)
    assert d.rahmen() is None and d.schattierung() == (None, None) and d.seitenrand() is None
    d.p_rahmen.einstellung["kontur"].click()
    assert d.rahmen().seiten == "tblr"
    d.p_rahmen.kantenknoepfe["l"].toggle(); d.p_rahmen.kantenknoepfe["r"].toggle()
    assert d.rahmen().seiten == "tb" and d.p_rahmen.einstellung["anpassen"].isChecked()
    d.p_rahmen.einstellung["alle"].click()
    assert d.rahmen().seiten == "tblrh"
    d.p_schatt.fuell._uebernehmen(QColor("#fff3bf"))
    d.p_schatt.art.setCurrentIndex(d.p_schatt.art.findData("pct25"))
    assert d.schattierung() == ("#fff3bf", ("pct25", "#000000"))
    d.p_rand.einstellung["kontur"].click()
    assert d.seitenrand()["art"] == "einfach" and d.seitenrand()["messen"] == "text" and d.seitenrand()["abstand"] == "1,1,4,4"      # Vorgabe wie in der Vorlage
    d2 = RahmenSchattierungDialog(None, rahmen=Linie("#000000", 1.0, "einfach", "lr"), fuell="#d0ebff", seite="schattierung")
    assert d2.rahmen().seiten == "lr" and d2.schattierung() == ("#d0ebff", None) and d2.reiter.currentIndex() == 2
    d.show(); app.processEvents()


def test_muster_kacheln_und_ooxml(app):
    from lunivo_writer.editor.text import muster as M
    assert len(M.MUSTER) == 37 and M.ooxml_von("pct12_5") == "pct12" and M.schluessel_von_ooxml("diagCross") == "dunkel_karo"
    assert M.aus_text(M.als_text("pct50", "#ff0000", None)) == ("pct50", "#ff0000", None)
    k = M.kachel("pct50", "#000000", "#ffffff").toImage()
    schwarz = sum(1 for y in range(8) for x in range(8) if k.pixelColor(x, y).name() == "#000000")
    assert schwarz == 32                                                           # 50 % von 64


# ---- Aufzählung, Nummerierung, Tabellenraster ----------------------------------------------------------------------------

def _fenster(tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.dienste.einstellungen_dienst import Settings
    from lunivo_writer.oberflaeche.programmfenster import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document()
    return w


def _zu(w):
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def test_listenraster_setzt_und_entfernt_listen(app, tmp_path):
    from PySide6.QtGui import QTextListFormat
    w = _fenster(tmp_path)
    e = w.current_editor(); e.insertPlainText("Eins\nZwei")
    r = w.befehle.menue_aufzaehlungKlappe()
    assert set(r.knoepfe) == {"keine"} | {str(i) for i in range(7)} and r.knoepfe["keine"].isChecked()      # Punkt, Quadrat und fünf Zeichen
    r.knoepfe["1"].click()                                  # Quadrat
    assert e.textCursor().currentList().format().style() == QTextListFormat.ListSquare
    n = w.befehle.menue_nummerierungKlappe()
    assert set(n.knoepfe) == {"keine"} | {str(i) for i in range(7)}
    n.knoepfe["2"].click()                                  # I. II. III.
    assert e.textCursor().currentList().format().style() == QTextListFormat.ListUpperRoman
    n2 = w.befehle.menue_nummerierungKlappe()
    assert n2.knoepfe["2"].isChecked() and not n2.knoepfe["0"].isChecked()
    n2.knoepfe["2"].click()                                # gleiche Art nochmal: bleibt
    assert e.textCursor().currentList() is not None
    n2.knoepfe["keine"].click()
    assert e.textCursor().currentList() is None
    _zu(w)


def test_zellenraster_meldet_zeilen_und_spalten(app, tmp_path):
    from PySide6.QtCore import QPointF
    from lunivo_writer.oberflaeche.baukasten import ZellenRaster
    gemeldet = []
    z = ZellenRaster(); z.gewaehlt.connect(lambda a, b: gemeldet.append((a, b)))
    g = z.gitter
    g.setze(*g._zelle_bei(QPointF(3 * g.zelle + 5, 2 * g.zelle + 5)))
    assert g.an == (3, 4) and z.beschriftung.text() == "3 × 4 Tabelle"
    g.setze(0, 0); assert z.beschriftung.text() == "Tabelle einfügen"
    z.waehle(3, 4)
    assert gemeldet == [(3, 4)] and g._zelle_bei(QPointF(-5, 5)) == (0, 0)


def test_tabellenmenue_fuegt_tabelle_ein(app, tmp_path):
    w = _fenster(tmp_path)
    e = w.current_editor(); e.insertPlainText("x")
    m = w.befehle.menue_tabelleKlappe()
    m.waehle(2, 3)
    t = e.textCursor().currentTable()
    assert t is not None and t.rows() == 2 and t.columns() == 3
    assert [a.text().replace("&", "") for a in m.actions() if a.text()] == [
        "Tabelle einfügen", "Tabelle zeichnen(W)", "Text in Tabelle umwandeln...", "Tabelle in Text konvertieren..."]
    m.aboutToShow.emit()                                     # in der Tabelle: nur „Tabelle in Text“ wählbar, wie in der Vorlage
    assert [a.isEnabled() for a in m.actions() if a.text()][2:] == [False, True]
    assert (m.gitter.zeilen, m.gitter.spalten) == (10, 10)
    _zu(w)


def test_beschriftungen_ohne_html(app):
    from PySide6.QtCore import Qt
    from lunivo_writer.oberflaeche.baukasten import md_escape, md_label, text_label
    t = text_label("<b>kein Markup</b>\nzweite Zeile", fett=True, pt=13)
    assert t.textFormat() == Qt.PlainText and t.text().startswith("<b>") and t.font().bold() and t.font().pointSizeF() == 13
    m = md_label(f"~~{md_escape('a <b> *x*')}~~ → **{md_escape('neu_1')}**")
    assert m.textFormat() == Qt.MarkdownText
    d = __import__("PySide6.QtGui", fromlist=["QTextDocument"]).QTextDocument()
    d.setMarkdown("~~alt~~ → **neu**")
    assert d.toPlainText().strip() == "alt → neu"
    f = d.begin().begin().fragment().charFormat()
    assert f.fontStrikeOut()
    assert md_escape("a*b_c") == "a\\*b\\_c"


def test_ausrichtung_menue_setzt_hoch_und_querformat(app, tmp_path):
    from lunivo_writer.oberflaeche.band.band_leiste import lade_register
    w = _fenster(tmp_path)
    ed = w.current_editor()
    b = w.befehle
    b.tun("w.setzeQuer:[true]");  assert ed.abschnitt_seite().landscape
    b.tun("w.setzeQuer:[false]"); assert not ed.abschnitt_seite().landscape
    assert "w.setzeQuer:[true]" in str(lade_register()) and "w.setzeQuer:[false]" in str(lade_register())
    _zu(w)


def test_dunkles_system_nutzt_die_lunivo_palette(app, monkeypatch):
    """Bei „Wie das System“ und dunklem System muss der Nebentext (palette(mid)) lesbar bleiben."""
    from PySide6.QtGui import QPalette
    from lunivo_writer.oberflaeche import thema
    alt = app.palette()
    try:
        monkeypatch.setattr(thema, "_ist_dunkel", lambda a: a.palette().color(QPalette.Window).lightness() < 128)
        thema._setze(app, "dark")
        assert app.palette().color(QPalette.Mid).name() == "#7c858e" and app.palette().color(QPalette.Window).name() == "#2a2e32"
        # System meldet dunkel: die Standardpalette wird durch die Lunivo-Palette ersetzt
        monkeypatch.setattr(app.style().__class__, "standardPalette", lambda self: app.palette(), raising=False)
        thema._setze(app, "system")
        assert app.palette().color(QPalette.Mid).lightness() > 100
    finally:
        app.setPalette(alt)


def test_dateisymbole_aus_mitgelieferten_svgs(app):
    """Die Dateisymbole kommen aus den mitgelieferten SVGs (ressourcen/icons/dateitypen), nicht aus dem Icon-Theme des Systems."""
    from lunivo_writer.oberflaeche.baukasten.medien import datei_symbole as D
    assert D.icon_namen(".pdf") == ["pdf", "genericfile"]                          # Dateityp zuerst, dann der allgemeine Rückfall
    assert D.icon_namen("/home/x/brief.txt")[0] == "txt" and D.icon_namen(".odt")[0] == "rtf"
    assert D.icon_namen("unbekannt.xyz") == ["genericfile", "genericfile"]
    for name in ("a.pdf", "b.docx", "c.txt", "d.unbekannt"):
        assert not D.datei_symbol(name).isNull(), name




def test_farbenfenster_wege_zur_selben_farbe(app):
    from PySide6.QtCore import QPointF
    from PySide6.QtGui import QColor
    from lunivo_writer.oberflaeche.baukasten.felder.farbwaehler import FarbenDialog, _Flaeche, _Leiste, _Regler, _Ring
    d = FarbenDialog(None, QColor("#2f6fb5"), "Schriftfarbe")
    assert d.farbe().name() == "#2f6fb5"
    reg = d.findChildren(_Regler)[0]
    reg.hex.setText("#ff8800"); reg._hex()
    assert d.farbe().name() == "#ff8800" and reg.werte() == (255, 136, 0)
    ring = d.findChildren(_Ring)[0]
    ring._ziehen = "ring"; ring._wirke(QPointF(ring.mitte.x() + 100, ring.mitte.y()))      # drei Uhr = Farbton 90°
    assert abs(d.m.h - 0.25) < 0.01
    d.findChildren(_Leiste)[0]._setze(QPointF(5, 214))                                      # ganz unten = schwarz
    assert d.farbe().name() == "#000000"
    d.findChildren(_Flaeche)[0]._setze(QPointF(0, 0))                                       # links oben = Rot, voll
    d.findChildren(_Leiste)[0]._setze(QPointF(5, 0))
    assert d.farbe().name() == "#ff0000"


def test_seitenrand_einzelne_kanten_und_docx(app, tmp_path):
    from PySide6.QtCore import QPoint, QSettings, Qt
    from PySide6.QtTest import QTest
    from lunivo_writer.oberflaeche.baukasten.formatierung.rahmen_schattierung import RahmenSchattierungDialog
    d = RahmenSchattierungDialog(None, seite="seitenrand"); d.show()
    r = d.p_rand
    assert all(b.isEnabled() for b in r.kantenknoepfe.values())                    # alle vier Kanten sind anklickbar
    r.kantenknoepfe["l"].click(); r.kantenknoepfe["b"].click()
    assert d.seitenrand()["seiten"] == "bl"
    v = r.vorschau; a = max(4.0, r.abstand_mm * 1.2)
    QTest.mouseClick(v, Qt.LeftButton, Qt.NoModifier, QPoint(int(v.width() - a), v.height() // 2))   # Klick auf die rechte Kante
    assert d.seitenrand()["seiten"] == "blr"
    from lunivo_writer.dienste.einstellungen_dienst import Settings
    from lunivo_writer.oberflaeche.programmfenster import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document(); e = w.current_editor()
    w.befehle._seite_aendern(border=d.seitenrand())
    pfad = str(tmp_path / "r.docx"); w.current_tab().path = pfad; w.save()
    geladen = w.dokumente.laden(pfad)
    assert geladen.page.border["seiten"] == "blr"
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def test_galerie_meldet_gewaehlt_und_ueberfahren(app):
    from PySide6.QtGui import QFont
    from lunivo_writer.oberflaeche.baukasten import GalerieAuswahl
    g = GalerieAuswahl(None, titel="Stile")
    f = QFont("Liberation Sans"); f.setPointSizeF(20)
    g.kachel("a", "Eins", f, probe="AaBbCcD"); g.kachel("b", "Zwei", QFont("Liberation Sans"))
    seen, gewaehlt, weg = [], [], []
    g.ueberfahren.connect(seen.append); g.gewaehlt.connect(gewaehlt.append); g.verlassen.connect(lambda: weg.append(1))
    k = g.kacheln["a"]
    assert k.schrift.pointSizeF() < 20                                        # große Probe wird in die Kachel eingepasst
    k.darueber.emit("a"); k.weg.emit(); k.klick.emit("b")
    assert seen == ["a"] and weg == [1] and gewaehlt == ["b"]


def test_schriftart_fenster_werte_und_format(app):
    from lunivo_writer.oberflaeche.baukasten.formatierung.schriftart_dialog import SchriftartDialog
    from lunivo_writer.oberflaeche.baukasten.formatierung.text_format import aus_format, zu_format
    d = SchriftartDialog(None, {"schrift": "Liberation Sans", "groesse": 12.0})
    d.schnitt.setCurrentText("Fett Kursiv"); d.groesse.setCurrentText("18")
    d.asien.setCurrentText("Noto Sans CJK JP"); d.betonung.setCurrentIndex(d.betonung.findData("kreis")); d.cb["doppelt"].setChecked(True)
    d.cb["doppelt"].setChecked(False)
    d.unter.setCurrentIndex(d.unter.findData("gepunktet")); d.cb["durch"].setChecked(True); d.cb["hoch"].setChecked(True)
    d.cb["tief"].setChecked(True)                                                   # Hoch- und Tiefgestellt schließen sich aus
    w = d.werte()
    assert w["fett"] and w["kursiv"] and w["groesse"] == 18 and w["unter"] == "gepunktet" and w["tief"] and not w["hoch"]
    f = zu_format(w)
    assert f.fontWeight() >= 600 and f.fontItalic() and f.fontStrikeOut() and f.fontPointSize() == 18
    assert f.fontFamilies() == ["Liberation Sans", "Noto Sans CJK JP"]              # asiatische Schrift hinter der westlichen
    w2 = aus_format(f)
    assert w2["unter"] == "gepunktet" and w2["durch"] and w2["tief"] and w2["kerning"]
    assert w2["schrift_asien"] == "Noto Sans CJK JP" and w2["betonung"] == "kreis" and not w2["doppelt"]
    v = SchriftartDialog(None, {"schrift": "Liberation Sans"}, umfang="vorlage")
    assert v.reiter.count() == 2 and v.effekte.isVisibleTo(v) and not v.effekt_knopf.isVisibleTo(v)    # in der Vorlage dasselbe Fenster, ohne Texteffekte und Standard










































def test_texteffekte_alle_regler_bedienbar(app):
    from lunivo_writer.oberflaeche.baukasten.formatierung.texteffekt_dialog import TexteffektDialog
    d = TexteffektDialog(None, {})
    alle = [d.s_farbe, d.s_trans, d.s_gross, d.s_weich, d.s_abst, d.s_winkel, d.r_gross, d.r_trans, d.r_weich, d.r_abst, d.l_farbe, d.l_gross, d.l_trans,
            d.farbe, d.trans, d.v1, d.v2, d.v_winkel, d.k_farbe, d.k_breite, d.k_art, d.k_form, d.kv1, d.kv2, d.kv_winkel, d.d_tiefe, d.d_kontur,
            d.d_tiefe_f, d.d_kontur_f, d.d_licht, d.d_winkel]
    assert all(x.isEnabled() for x in alle)                                   # nichts ist ausgegraut

    def zieh(x, v):                                                            # wie mit der Maus am Regler ziehen
        x.regler.setValue(int(round(v * x._f)))
    d.s_abst.regler.setValue(120)                                              # ein Regler schaltet seinen Effekt ein
    assert d.werte()["schatten"]["abstand"] == 12.0
    zieh(d.r_gross, 70.0); assert d.werte()["reflektion"]["groesse"] == 70.0
    zieh(d.l_gross, 9.0); assert d.werte()["leuchten"]["groesse"] == 9.0
    zieh(d.v_winkel, 30); assert d.r_verlauf.isChecked() and d.werte()["verlauf"]["winkel"] == 30
    zieh(d.k_breite, 2.0); assert d.k_linie.isChecked() and d.werte()["kontur"]
    zieh(d.kv_winkel, 45); assert d.k_verlauf.isChecked() and d.werte()["kontur_verlauf"]["winkel"] == 45
    d.d_tiefe.setValue(5.0); d.d_winkel.setValue(40.0)
    assert d.werte()["d3"]["tiefe"] == 5.0 and d.werte()["d3"]["winkel"] == 40.0
    zieh(d.trans, 30); assert d.r_farbe.isChecked() and d.werte()["transparenz"] == 30




def test_seitenrahmen_vorn_und_hinten(app):
    from PySide6.QtCore import QRectF
    from PySide6.QtGui import QColor, QImage, QPainter
    from lunivo_writer.editor.seite.seiten_aufteilung import seitenschmuck
    from lunivo_writer.modelle.seite import PageSettings

    def bild(vorn: bool, rahmen: str) -> QImage:
        pg = PageSettings(); pg.border = {"art": "einfach", "farbe": "#c92a2a", "breite_pt": 6.0, "abstand_mm": 10.0, "seiten": "tblr", "vordergrund": vorn}
        img = QImage(300, 300, QImage.Format_RGB32); img.fill(QColor("white"))
        p = QPainter(img); seitenschmuck(p, pg, False, QRectF(0, 0, 300, 300), rahmen, False); p.end()
        return img
    rot = lambda img: img.pixelColor(150, 38).red() > 150 and img.pixelColor(150, 38).green() < 100            # liegt der Rahmen an der Kante?
    assert rot(bild(True, "vorn")) and not rot(bild(True, "hinten"))              # Vordergrund: nur beim Zeichnen „vorn“
    assert rot(bild(False, "hinten")) and not rot(bild(False, "vorn"))            # Hintergrund: nur beim Zeichnen „hinten“
    assert rot(bild(False, "immer"))




def test_texteffekte_knopf_im_band_oeffnet_die_seitenleiste(app, tmp_path):
    from PySide6.QtCore import QSettings
    from PySide6.QtWidgets import QToolButton
    from lunivo_writer.dienste.einstellungen_dienst import Settings
    from lunivo_writer.oberflaeche.programmfenster import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.show(); w.new_document(); w.current_editor().setPlainText("Text")
    # Es gibt zwei Knöpfe mit diesem Namen; der unsichtbare öffnet nur sein Menü (das blockiert im Test). Gemeint ist der sichtbare im Band.
    knoepfe = [b for b in w.findChildren(QToolButton) if b.toolTip() in ("Texteffekte", "Texteffekte formatieren") and b.isVisible()]
    assert knoepfe, "der Knopf „Texteffekte“ fehlt im Band"
    w.sidebar.hide()
    knoepfe[0].click()
    assert w.sidebar.texteffekte_sichtbar()




def test_fenster_stapel_unterfenster_als_seiten(app):
    from PySide6.QtWidgets import QDialog
    from lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel import FensterStapel, stapel_von
    from lunivo_writer.oberflaeche.baukasten.formatierung.formatvorlage_dialog import FormatvorlageDialog
    fv = FormatvorlageDialog(None, start={"groesse": 12}, vorlagen=["Standard"])
    host = FensterStapel(fv)
    host.show()
    assert len(host._seiten) == 1 and not host.zurueck.isVisible()
    gr0 = host.size(); assert gr0 == host.GROESSE or gr0.width() <= host.GROESSE.width()
    fv._absatz()                                                              # Format ▸ Absatz: eine Seite im selben Fenster
    assert len(host._seiten) == 2 and host.zurueck.isVisibleTo(host) and "Absatz" in host.pfad.text() and stapel_von(host._seiten[1][0]) is host
    absatz = host._seiten[1][0]
    absatz.vor.setValue(10.0)
    absatz._tabstopps()                                                       # zweite Ebene: Tabstopps aus dem Absatz
    assert len(host._seiten) == 3 and "Tabstopps" in host.pfad.text()
    host._seiten[2][0].accept()                                               # OK im Tabstoppfenster: zurück zum Absatz
    assert len(host._seiten) == 2
    absatz.accept()                                                           # OK im Absatz: fertig() setzt die Werte der Vorlage, zurück zur Vorlage
    assert len(host._seiten) == 1 and host.width() >= gr0.width() and host.height() >= gr0.height()      # das Fenster schrumpft nicht
    assert fv.leiste.werte()["vor"] > 0
    fv._effekte(); assert len(host._seiten) == 2
    host._zurueck()                                                           # „← Zurück“ bricht ab
    assert len(host._seiten) == 1
    fv.accept()                                                               # OK der Vorlage beendet das ganze Fenster
    assert host.result() == QDialog.Accepted


def test_weitere_farben_als_seite_im_stapel(app):
    from PySide6.QtGui import QColor
    from lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel import FensterStapel
    from lunivo_writer.oberflaeche.baukasten.formatierung.formatvorlage_dialog import FormatvorlageDialog
    from lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.farbpalette import FarbPalette
    fv = FormatvorlageDialog(None, start={"groesse": 12}, vorlagen=["Standard"])
    host = FensterStapel(fv); host.show()
    pal = FarbPalette(fv.leiste, keine_text=None)                  # eine Palette in der Formatvorlage
    gewaehlt = []
    pal.gewaehlt.connect(gewaehlt.append)
    pal._weitere()                                                  # „Weitere Farben …“: Seite „Farben“ im selben Fenster
    assert len(host._seiten) == 2 and "Farben" in host.pfad.text()
    seite = host._seiten[1][0]
    seite.accept()
    assert len(host._seiten) == 1 and gewaehlt and isinstance(gewaehlt[0], QColor)


def test_pipette_hat_sicherungen(app, monkeypatch):
    from PySide6.QtCore import QEventLoop, QPoint, QTimer
    from PySide6.QtGui import QColor, QGuiApplication, QKeyEvent
    from PySide6.QtCore import Qt, QEvent
    from lunivo_writer.oberflaeche.baukasten.felder import pipette
    # Zeitablauf: ohne Eingabe endet die Pipette von selbst (hier in einer Sekunde)
    monkeypatch.setattr(pipette, "ZEIT_S", 1)
    monkeypatch.setattr(QGuiApplication, "platformName", staticmethod(lambda: "xcb"))
    import time
    t = time.time()
    assert pipette.farbe_vom_bildschirm() is None
    assert time.time() - t < 4
    # Taste bricht ab
    monkeypatch.setattr(pipette, "ZEIT_S", 30)
    def taste():
        w = [x for x in QGuiApplication.topLevelWidgets() if isinstance(x, pipette._Pipette)] if hasattr(QGuiApplication, "topLevelWidgets") else []
        from PySide6.QtWidgets import QApplication
        w = [x for x in QApplication.topLevelWidgets() if isinstance(x, pipette._Pipette) and x._offen]
        if w:
            w[0].keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_A, Qt.NoModifier))
    QTimer.singleShot(200, taste)
    t = time.time()
    assert pipette.farbe_vom_bildschirm() is None and time.time() - t < 3
    # Wayland: nichts aufnehmen, nichts blockieren
    monkeypatch.setattr(QGuiApplication, "platformName", staticmethod(lambda: "wayland"))
    assert pipette.farbe_vom_bildschirm() is None


def test_druck_bereich_und_blattseiten():
    from lunivo_writer.editor.seite.druck import bereich_lesen, papier_name, seiten_nach_wahl
    assert bereich_lesen("1-3, 5", 10) == [1, 2, 3, 5]
    assert bereich_lesen("8-12", 10) == [8, 9, 10] and bereich_lesen("x", 10) is None and bereich_lesen("20", 10) is None
    assert seiten_nach_wahl({"bereich": "alle", "blattseiten": "vorder"}, 5) == [1, 3, 5]
    assert seiten_nach_wahl({"bereich": "seiten", "seiten_text": "2-4", "blattseiten": "rueck"}, 5) == [2, 4]
    assert papier_name(210, 297) == "A4" and papier_name(297, 210) == "A4" and papier_name(100, 100) == "Benutzerdefiniert"


def test_druckfenster_wahl_und_pruefung(app):
    from lunivo_writer.oberflaeche.baukasten.dokument.druck_dialog import DruckDialog
    d = DruckDialog(None, 4, (210, 297), False, {"schwarz": True})
    e = d.ergebnis()
    assert e["bereich"] == "alle" and e["papier"] == "A4" and e["schwarz"] and e["steuerelemente"] and not e["platzhalter"]
    d.ansicht.text.setText("9")                                   # Seite außerhalb → Drucken nicht möglich
    assert not d.ok.isEnabled() and d.ergebnis()["bereich"] == "seiten"
    d.ansicht.text.setText("2-3"); d.ansicht.pro_blatt.setCurrentIndex(d.ansicht.pro_blatt.findData(2))
    assert d.ok.isEnabled() and d.ansicht.von.text() == "/ 1"
    d.ansicht.papier2.setCurrentIndex(d.ansicht.papier2.findData("A5"))   # Reiter „Drucker“ und „Standard“ teilen die Wahl
    assert d.ergebnis()["papier"] == "A5"




def test_druckvorschau_ansichten_und_zoom(app):
    from PySide6.QtGui import QTextDocument
    from lunivo_writer.editor.seite.druck import Zwischenseiten
    from lunivo_writer.modelle.seite import PageSettings
    from lunivo_writer.oberflaeche.baukasten.dokument.druckvorschau import DruckVorschau
    d = QTextDocument(); d.setPlainText("Zeile\n" * 140)
    v = DruckVorschau(None, Zwischenseiten(d, PageSettings(), {}))
    v.resize(1000, 700); v.show()
    assert v._gesamt >= 3 and len(v._seiten) == 1
    v.ansicht.setCurrentIndex(1); assert len(v._seiten) == 2
    v.ansicht.setCurrentIndex(2); assert len(v._seiten) == v._gesamt
    z = v._zoom; v._zoom_setzen(z * 1.25); assert abs(v._zoom - z * 1.25) < 1e-6
    v._gehe(2); assert v.nr.value() == 2
    assert v._q.bild(1).pixelColor(2, 2).name() == "#ffffff"
    v.close()




def test_vorlagen_galerie_zeigt_eigene_vorlagen(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.dienste.einstellungen_dienst import Settings
    from lunivo_writer.oberflaeche.baukasten.vorlagen.vorlagen_galerie import VorlagenGalerie
    s = Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)); s.set("vorlagen/ordner", str(tmp_path))
    (tmp_path / "Mein Brief.txt").write_text("Hallo\nVorlage\n", encoding="utf-8")
    g = VorlagenGalerie(s, True); g.resize(1200, 800); g.show()
    namen = [k.name for k in g._kacheln]
    assert "Mein Brief" in namen and "Brief" in namen        # „Leeres Dokument“ ist keine Kachel der Vorlagen mehr (eigene Auswahl auf der Seite „Neu“)
    assert g.reiter_w.tabText(1).endswith("1")                # Reiter „Meine Vorlagen  1“ (es gibt zwei Reiter)
    g._reiter_setzen("eigene"); app.processEvents(); assert [k.name for k in g._kacheln if k.isVisible()] == ["Mein Brief"]
    g.suche.setText("xyz"); assert not [k for k in g._kacheln if k.isVisible()]
    g.suche.setText(""); g._reiter_setzen("eigene")                # es gibt nur noch „Standardvorlagen“ und „Meine Vorlagen“
    gewaehlt = []
    g.gewaehlt.connect(lambda a, w: gewaehlt.append((a, w)))
    next(k for k in g._kacheln if k.name == "Mein Brief").click()
    assert gewaehlt == [("datei", str(tmp_path / "Mein Brief.txt"))]
    g._timer.stop()


def test_vorlagen_rubriken_aus_unterordnern(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.dienste.einstellungen_dienst import Settings
    from lunivo_writer.oberflaeche.baukasten.vorlagen.vorlagen_galerie import VorlagenGalerie
    s = Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)); s.set("vorlagen/ordner", str(tmp_path))
    (tmp_path / "Lebenslauf").mkdir()
    for n in ("Kay 2024", "Kay Technik"):
        (tmp_path / "Lebenslauf" / f"{n}.txt").write_text("Lebenslauf\n", encoding="utf-8")
    g = VorlagenGalerie(s, True); g.resize(1200, 800); g.show()
    sicht = [k.name for k in g._sichtbar()]
    assert "Lebenslauf" in sicht and "Brief" in sicht and "Kay 2024" not in sicht          # oben nur die Rubriken
    g.rubrik_oeffnen("Lebenslauf")
    assert [k.name for k in g._sichtbar()] == ["Lebenslauf", "Kay 2024", "Kay Technik"]     # Gerüst und eigene Dokumente der Rubrik
    assert g._ziel() == str(tmp_path / "Lebenslauf") and g.zurueck.isVisible() is True
    g.rubrik_oeffnen("Brief")
    assert "Brief an eine Behörde" in [k.name for k in g._sichtbar()]
    g.rubrik_oeffnen(None); g.suche.setText("technik")
    assert [k.name for k in g._sichtbar()] == ["Kay Technik"]                               # die Suche findet auch in Rubriken
    g._timer.stop()


def test_pdf_schrift_bleibt_schwarz_im_dunklen_thema(app, tmp_path):
    """Text ohne eigene Farbe darf im PDF nicht die helle Textfarbe des dunklen Themas bekommen (blasse, fast weiße Schrift)."""
    from PySide6.QtCore import QSize, Qt
    from PySide6.QtGui import QColor, QImage, QPainter, QPalette, QTextDocument
    from PySide6.QtPdf import QPdfDocument
    from lunivo_writer.editor.seite.seiten_aufteilung import export_pdf
    from lunivo_writer.modelle.seite import PageSettings
    alt = app.palette()
    dunkel = QPalette(alt)
    for rolle in (QPalette.Text, QPalette.WindowText, QPalette.ButtonText):
        dunkel.setColor(rolle, QColor("#e8eaed"))
    app.setPalette(dunkel)
    try:
        d = QTextDocument(); d.setPlainText("Hallo dunkles Thema\nZweite Zeile")
        pdf = str(tmp_path / "d.pdf"); export_pdf(pdf, d, PageSettings())
        q = QPdfDocument(); q.load(pdf); gr = QSize(700, 990)
        img = QImage(gr, QImage.Format_RGB32); img.fill(Qt.white)
        p = QPainter(img); p.drawImage(0, 0, q.render(0, gr)); p.end()
        assert min(img.pixelColor(x, y).lightness() for x in range(60, 400) for y in range(60, 200)) < 80
    finally:
        app.setPalette(alt)


def test_docx_schreibt_dokumentsprache_statt_englisch(app, tmp_path):
    """Ohne eigene Angabe steht die Sprache des Dokuments (de-DE) in der DOCX, nicht die Vorgabe en-US der Vorlage."""
    import zipfile
    from PySide6.QtGui import QTextDocument
    from lunivo_writer.modelle.seite import PageSettings
    from lunivo_writer.dienste import docx_schreiber
    d = QTextDocument(); d.setPlainText("Sehr geehrte Damen und Herren")
    pfad = str(tmp_path / "s.docx"); docx_schreiber.write_docx(pfad, d, PageSettings(), {})
    xml = zipfile.ZipFile(pfad).read("word/styles.xml").decode("utf-8")
    assert 'w:lang w:val="de-DE"' in xml and 'w:lang w:val="en-US"' not in xml




def _rot(b=40, h=30):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QImage
    img = QImage(b, h, QImage.Format_RGB32); img.fill(Qt.red)
    return img


def test_frei_positionierte_bilder_ueberleben_docx_und_werden_gezeichnet(app, tmp_path):
    """Kopfzeilenbild und Bild am Absatz (ohne Textumbruch): schreiben, lesen, zeichnen — Lage und Schichtfolge bleiben."""
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QTextCursor, QTextDocument
    from lunivo_writer.editor.objekte import freie_bilder as FB
    from lunivo_writer.editor.seite.seiten_aufteilung import seite_als_bild
    from lunivo_writer.modelle.seite import PageSettings, mm_to_px
    from lunivo_writer.dienste import docx_schreiber, datei_dienst
    d = QTextDocument(); d.setPlainText("Hallo\nZweiter Absatz")
    name = FB.neuer_name(d); d.addResource(QTextDocument.ImageResource, QUrl(name), _rot())
    FB.an_absatz(QTextCursor(d.firstBlock()), {"n": name, "b": 40.0, "h": 30.0, "bh": "seite", "xh": 100.0, "bv": "seite", "yv": 400.0,
                                                "hinter": False, "ellipse": False, "ah": "", "av": ""})
    ps = PageSettings()
    ps.bilder = [{"ort": "kopf", "bild": _rot(80, 50), "b": 80.0, "h": 50.0, "bh": "seite", "xh": 10.0, "bv": "seite", "yv": 10.0,
                  "hinter": True, "ellipse": False, "ah": "", "av": ""}]
    pfad = str(tmp_path / "f.docx"); docx_schreiber.write_docx(pfad, d, ps, {})
    g = datei_dienst.load(pfad)
    assert len(g.page.bilder) == 1 and g.page.bilder[0]["ort"] == "kopf" and g.page.bilder[0]["hinter"]
    angaben = [a for b in [g.doc.firstBlock()] for a in FB.aus_absatz(b.blockFormat())]
    assert len(angaben) == 1 and abs(angaben[0]["yv"] - 400.0) < 1 and angaben[0]["bv"] == "seite"
    img = seite_als_bild(g.doc, g.page, 1, 1.0)
    assert img.pixelColor(50, 30).red() > 200 and img.pixelColor(50, 30).green() < 60          # Bild in der Kopfzeile, oben links
    assert img.pixelColor(120, 410).red() > 200 and img.pixelColor(120, 410).green() < 60      # Bild am Absatz, weiter unten
    assert img.pixelColor(300, 300).green() > 200                                                # sonst weißes Blatt


def test_frei_bild_ausrichtung_und_ellipse(app):
    from lunivo_writer.editor.objekte import freie_bilder as FB
    r = FB.rechteck({"b": 100.0, "h": 50.0, "bh": "seite", "ah": "center", "bv": "seite", "av": "bottom"}, 800, 1000, 100, 100, 600, 800)
    assert (r.x(), r.y()) == (350.0, 950.0)
    r = FB.rechteck({"b": 10.0, "h": 10.0, "bh": "rand", "xh": 5.0, "bv": "absatz", "yv": -20.0}, 800, 1000, 100, 100, 600, 800, absatz_y=300.0)
    assert (r.x(), r.y()) == (105.0, 280.0)






def test_rechtsklickmenue_deutsch_und_mini_leiste_zwei_zeilen(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.dienste.einstellungen_dienst import Settings
    from lunivo_writer.oberflaeche.programmfenster import MainWindow
    from lunivo_writer.oberflaeche.bauteile.kontextmenue import menue_bauen
    from lunivo_writer.oberflaeche.bauteile.mini_leiste import MiniLeiste
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document(); e = w.current_editor(); e.insertPlainText("Text")
    texte = [a.text() for a in menue_bauen(e, w).actions() if not a.isSeparator()]
    assert texte[:3] == ["Kopieren", "Ausschneiden", "Einfügen"] and "Schriftart …" in texte and "Neuer Kommentar" in texte
    assert not any(t in ("Undo", "Redo", "Cut", "Copy", "Paste", "Select All") for t in texte)           # keine englischen Standardtexte
    m = MiniLeiste(w)
    assert {"kopieren", "einfuegen", "ausschneiden", "formatUebertragen", "fett", "hervorhebenJetzt", "schriftfarbeJetzt", "ausrichtung", "zeilenabstand"} <= set(m.knoepfe)
    assert m.schriftart.count() > 5 and m.groesse.count() >= 10
    assert m.knoepfe["schriftfarbeJetzt"].menu() is not None and m.knoepfe["zeilenabstand"].menu() is not None
    for x in w._doc_tabs():
        x.editor.document().setModified(False)                         # sonst fragt das Schließen nach und der Test hängt
    w.close()














def test_bildeffekte_ueberleben_docx(app, tmp_path):
    """Schatten, Leuchten, Spiegelung und weiche Kanten eines freien Bildes werden als effectLst geschrieben und wieder gelesen."""
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QTextCursor, QTextDocument
    from lunivo_writer.editor.objekte import freie_bilder as FB
    from lunivo_writer.modelle.seite import PageSettings
    from lunivo_writer.dienste import docx_schreiber, datei_dienst
    d = QTextDocument(); d.setPlainText("Hallo")
    name = FB.neuer_name(d); d.addResource(QTextDocument.ImageResource, QUrl(name), _rot())
    fx = {"schatten": {"farbe": "#112233", "transparenz": 40, "groesse": 100, "weich": 5.0, "abstand": 6.0, "winkel": 90},
          "leuchten": {"farbe": "#ff0000", "groesse": 9.0, "transparenz": 30},
          "reflektion": {"groesse": 40, "transparenz": 60, "weich": 1.0, "abstand": 2.0}, "weich": {"radius": 7.0}}
    FB.an_absatz(QTextCursor(d.firstBlock()), {"n": name, "b": 40.0, "h": 30.0, "bh": "seite", "xh": 100.0, "bv": "seite", "yv": 400.0,
                                                "hinter": False, "ellipse": False, "ah": "", "av": "", "fx": fx})
    pfad = str(tmp_path / "e.docx"); docx_schreiber.write_docx(pfad, d, PageSettings(), {})
    g = datei_dienst.load(pfad)
    a = FB.aus_absatz(g.doc.firstBlock().blockFormat())[0]
    got = a["fx"]
    assert got["schatten"]["farbe"] == "#112233" and abs(got["schatten"]["abstand"] - 6.0) < 0.1 and abs(got["schatten"]["winkel"] - 90) < 0.1
    assert abs(got["schatten"]["transparenz"] - 40) < 0.2 and abs(got["leuchten"]["groesse"] - 9.0) < 0.1 and got["leuchten"]["farbe"] == "#ff0000"
    assert abs(got["reflektion"]["groesse"] - 40) < 0.1 and abs(got["weich"]["radius"] - 7.0) < 0.1


def test_zusatzfenster_oeffnet_in_der_seitenleiste_ohne_breite_zu_aendern(app, tmp_path):
    """„Nummerierung und Aufzählungszeichen“ erscheint als Seite in der Seitenleiste (Breite bleibt), gilt nur solange man es bearbeitet und setzt die Liste."""
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QDialog
    w = _fenster(tmp_path)
    w.show()                                                # nur ein sichtbares Hauptfenster hat eine Seitenleiste, in der sich das Fenster zeigen kann
    e = w.current_editor(); e.insertPlainText("Eins\nZwei")
    breite = w.sidebar.width()
    seen = {}

    def waehle_und_ok():
        seen["breite"] = w.sidebar.width(); seen["sichtbar"] = not w.sidebar.isHidden()
        seen["seite"] = w.sidebar.stapel.currentIndex()
        d = w.sidebar.findChildren(QDialog)[0]
        d.r_punkte.setCurrentRow(1)                         # Punkt
        d.accept()
    QTimer.singleShot(300, waehle_und_ok)
    w.befehle.listeDialog()
    assert seen["breite"] == breite and seen["sichtbar"] and seen["seite"] == 2
    assert w.sidebar.stapel.currentIndex() == 0 and getattr(w.sidebar, "_zusatz", None) is None      # danach wie vorher
    assert e.textCursor().currentList() is not None
    _zu(w)


def test_seitenleisten_seiten_passen_in_echte_groesse(app):
    """Jede Seite der Seitenleiste passt in die Größe auf einem 1080er Bildschirm (etwa 480 × 727), ohne zu rollen und ohne seitlich überzulaufen."""
    from PySide6.QtWidgets import QWidget
    from lunivo_writer.oberflaeche.baukasten.formatierung.absatz_dialog import AbsatzDialog
    from lunivo_writer.oberflaeche.baukasten.felder.farbwaehler import FarbenDialog
    from lunivo_writer.oberflaeche.baukasten.formatierung.formatvorlage_dialog import FormatvorlageDialog
    from lunivo_writer.oberflaeche.baukasten.dokument.liste_dialog import ListenDialog
    from lunivo_writer.oberflaeche.baukasten.formatierung.rahmen_schattierung import RahmenSchattierungDialog
    from lunivo_writer.oberflaeche.baukasten.formatierung.schriftart_dialog import SchriftartDialog
    from lunivo_writer.oberflaeche.baukasten.dokument.tabstopp_dialog import TabstoppDialog
    from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import ZusatzPanel
    bauen = (lambda: AbsatzDialog(None, {}), lambda: SchriftartDialog(None, {"schrift": "Liberation Sans", "groesse": 12.0}), lambda: TabstoppDialog(None, [], 12.7),
             lambda: ListenDialog(None), lambda: RahmenSchattierungDialog(None), lambda: FarbenDialog(None), lambda: FormatvorlageDialog(None, vorlagen=["Standard"]))
    for f in bauen:
        p = ZusatzPanel(); p.verfuegbar, p.verfuegbar_hoehe = 444, 587; p.resize(480, 727)
        d = f(); p.oeffne(d); p.show()
        for i in range(d.reiter.count() if hasattr(d, "reiter") else 1):
            if hasattr(d, "reiter"):
                d.reiter.setCurrentIndex(i)
            app.processEvents(); app.processEvents()
            sa = p.stapel.currentWidget().sa
            h = sa.widget()
            unten = max((c.mapTo(h, c.rect().bottomLeft()).y() for c in d.findChildren(QWidget) if c.isVisible() and c.height() < 600), default=0)
            rechts = max((c.mapTo(h, c.rect().topRight()).x() for c in d.findChildren(QWidget) if c.isVisible()), default=0)
            assert unten <= sa.viewport().height(), (type(d).__name__, i, unten, sa.viewport().height())
            assert rechts <= sa.viewport().width(), (type(d).__name__, i, rechts)
        p.close()




def test_farbpalette_pipette_abschaltbar(app):
    from PySide6.QtWidgets import QPushButton
    namen = lambda p: [b.text() for b in p.findChildren(QPushButton)]          # noqa: E731
    assert "Pipette" in namen(FarbPalette())
    assert "Pipette" not in namen(FarbPalette(pipette=False))


def test_namenfilter_gibt_symbolknoepfen_einen_namen(app):
    from PySide6.QtWidgets import QToolButton
    from lunivo_writer.oberflaeche.baukasten.geruest.zugaenglichkeit import NamenFilter, name_fuer
    f = NamenFilter.einhaengen(app)
    k = QToolButton(); k.setText("↘"); k.setToolTip("Schriftart — Einstellungen")
    assert name_fuer(k) == "Schriftart"
    o = QToolButton(); o.setToolTip("Öffnen (Strg+O)"); o.setAccessibleName("Datei öffnen")
    k.show(); o.show(); app.processEvents()
    assert k.accessibleName() == "Schriftart" and o.accessibleName() == "Datei öffnen"
    app.removeEventFilter(f); k.close(); o.close()


def test_kachelfeld_tastatur_und_namen(app):
    """Tab erreicht genau eine Kachel; Pfeile bewegen den Fokus, Eingabe wählt; jede Kachel hat einen Namen."""
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtWidgets import QApplication
    from lunivo_writer.oberflaeche.baukasten.felder.kachel_feld import KachelFeld
    k = KachelFeld(spalten=2)
    for s, t in (("a", "Eins"), ("b", "Zwei"), ("c", "Drei")):
        k.hinzu(s, t)
    k.show(); k.activateWindow(); app.processEvents(); gemeldet = []; k.gewaehlt.connect(gemeldet.append)
    assert [b.accessibleName() for b in k.knoepfe.values()] == ["Eins", "Zwei", "Drei"]
    assert [b.focusPolicy() for b in k.knoepfe.values()].count(Qt.StrongFocus) == 1 and k.knoepfe["a"].focusPolicy() == Qt.StrongFocus
    k.knoepfe["a"].setFocus()
    QApplication.sendEvent(k.knoepfe["a"], QKeyEvent(QEvent.KeyPress, Qt.Key_Right, Qt.NoModifier))
    assert k.knoepfe["b"].hasFocus()
    QApplication.sendEvent(k.knoepfe["b"], QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.NoModifier))
    assert gemeldet == ["b"] and k.knoepfe["b"].isChecked() and k.knoepfe["b"].focusPolicy() == Qt.StrongFocus
    assert k.knoepfe["a"].focusPolicy() == Qt.ClickFocus


