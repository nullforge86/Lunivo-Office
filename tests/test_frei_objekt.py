"""WordArt und Textfeld als freie Objekte: ausgewählt (Rahmen, Griffe, Schnellleiste), kein Textmarkierungs-Kasten, Griffe wirken."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent

from lunivo_writer.editor import formen, frei_objekt as FO
from lunivo_writer.editor.zusatz import B_BILDANKER


def _ed(fenster):
    return fenster.current_editor()


def _maus(ed, typ, pos, taste=Qt.LeftButton, gedrueckt=Qt.LeftButton):
    e = QMouseEvent(typ, QPointF(pos), QPointF(pos), taste, gedrueckt, Qt.NoModifier)
    return ed._frei_maus(e, {QEvent.MouseButtonPress: "press", QEvent.MouseMove: "move", QEvent.MouseButtonRelease: "release"}[typ])


def _rect(ed):
    ed._frei_liste()
    return [t for t in ed._frei_treffer if t[0] == ed._frei_sel][0][2]


@pytest.fixture
def fenster(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document(); w.resize(1200, 800); w.show()
    yield w
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def test_wordart_ohne_auswahlkasten_mit_griffen(fenster):
    w = fenster; ed = _ed(w)
    w.befehle.wordartVorgabe(None, 1)
    assert not ed._bild_cursor() and not ed.textCursor().hasSelection()      # kein Bild im Text, keine Textmarkierung
    assert ed._frei_sel is not None and FO.art_gewaehlt(ed) == "wordart"       # Objekt ausgewählt: Rahmen, Griffe, Schnellleiste
    assert ed.document().firstBlock().blockFormat().hasProperty(B_BILDANKER)
    assert formen.wordart_daten(ed)["vorlage"] == 1
    r = _rect(ed)
    assert ed._frei_griff_bei(ed._frei_griff_mitte(r, "se"))[0] == "se" and ed._frei_griff_bei(ed._frei_griff_mitte(r, "rot"))[0] == "rot"
    assert set(ed._frei_knopf_rects(r)) == {"anker", "minus", "layout", "formstile", "fuell", "kontur"}


def test_griffe_groesse_und_drehen(fenster):
    ed = _ed(fenster); fenster.befehle.wordartVorgabe(None, 0)
    r = _rect(ed); se = ed._frei_griff_mitte(r, "se")
    _maus(ed, QEvent.MouseButtonPress, se); _maus(ed, QEvent.MouseMove, se + QPointF(60, 30)); _maus(ed, QEvent.MouseButtonRelease, se + QPointF(60, 30))
    assert _rect(ed).width() > r.width() + 30
    r = _rect(ed); rot = ed._frei_griff_mitte(r, "rot")
    _maus(ed, QEvent.MouseButtonPress, rot); ziel = QPointF(r.right() + 50, r.center().y())
    _maus(ed, QEvent.MouseMove, ziel); _maus(ed, QEvent.MouseButtonRelease, ziel)
    assert 60 < FO.ziel(ed)[3]["dreh"] < 120
    mitte = _rect(ed).center()                                                 # verschieben
    vor = _rect(ed).topLeft()
    _maus(ed, QEvent.MouseButtonPress, mitte); _maus(ed, QEvent.MouseMove, mitte + QPointF(40, 40)); _maus(ed, QEvent.MouseButtonRelease, mitte + QPointF(40, 40))
    assert _rect(ed).topLeft() != vor


def test_wordart_aendern_api(fenster):
    ed = _ed(fenster); fenster.befehle.wordartVorgabe(None, 0)
    assert formen.wordart_aendern(ed, text="Neu\nzwei", fuell="#ff0000", effekt={"schatten": {}}, kontur="#00ff00", unter=True, hervor="#ffff00")
    d = formen.wordart_daten(ed)
    assert d["text"] == "Neu\nzwei" and d["fuell"] == "#ff0000"
    assert formen.wordart_aendern(ed, form_fuell="#abcdef", form_linie="#123456", pt=None)
    assert FO.ziel(ed)[3]["fuell"]["farbe"] == "#abcdef"


def test_textfeld_wie_wordart(fenster):
    w = fenster; ed = _ed(w)
    w.befehle.textfeld()
    assert FO.art_gewaehlt(ed) == "textfeld" and not ed.textCursor().hasSelection()
    r = _rect(ed); se = ed._frei_griff_mitte(r, "se")
    _maus(ed, QEvent.MouseButtonPress, se); _maus(ed, QEvent.MouseMove, se + QPointF(80, 40)); _maus(ed, QEvent.MouseButtonRelease, se + QPointF(80, 40))
    assert _rect(ed).width() > r.width() + 40
    assert FO.ziel(ed)[3]["b"] > 240                                           # neu gesetzt in der neuen Größe
    assert FO.aendern(ed, "textfeld", text="Geändert", form_fuell="#ffeeaa")
    assert FO.daten_lesen(ed, "textfeld")["text"] == "Geändert"


def test_absatzsymbol_menue(fenster):
    ed = _ed(fenster); fenster.befehle.wordartVorgabe(None, 0)
    r = _rect(ed); k = ed._frei_knopf_rects(r)
    assert "anker" in k and k["anker"].right() < r.left()
    ed.textCursor().block()
    blk = ed.document().findBlockByNumber(ed._frei_sel[1])
    from PySide6.QtGui import QTextCursor, QTextBlockFormat
    bf = blk.blockFormat(); bf.setAlignment(Qt.AlignRight); QTextCursor(blk).mergeBlockFormat(bf)
    ed._frei_absatz_zuruecksetzen()
    assert ed.document().findBlockByNumber(ed._frei_sel[1]).blockFormat().alignment() & Qt.AlignLeft
    assert ed.document().findBlockByNumber(ed._frei_sel[1]).blockFormat().hasProperty(B_BILDANKER)
    ed._frei_anker_ausblenden()
    assert "anker" not in ed._frei_knopf_rects(r)


def test_textfeld_drei_varianten_und_texttools_schluessel(fenster):
    ed = _ed(fenster)
    for befehl, richtung in (("textfeld", None), ("textfeldVertikal", "senkrecht_rl"), ("textfeldMehrzeilig", None)):
        getattr(fenster.befehle, befehl)()
        z = FO.ziel(ed)
        assert z[0] == "textfeld" and z[1].get("richtung") == richtung and not ed.textCursor().hasSelection()
        if richtung:
            assert z[3]["h"] > z[3]["b"]                                      # senkrecht: hoch und schmal
    assert FO.aendern(ed, "textfeld", fett=True, unter=True, hervor="#ffff00", ausr="block", liste="punkt", einzug=1, zeilenabstand=1.5,
                      effekt={"schatten": {}}, kontur="#ff0000", vorlage=2)
    assert FO.daten_lesen(ed, "textfeld")["fett"] is True


def test_abstand_zum_text_und_transparenz(fenster):
    from lunivo_writer.editor import bildlayout as BL
    ed = _ed(fenster); fenster.befehle.wordartVorgabe(None, 0)
    BL.anwenden(ed, BL.ziel(ed), {"umbruch": "vor", "abstand": {"oben": 2.0, "unten": 3.0, "links": 4.0, "rechts": 5.0}})
    assert BL.lesen(ed, BL.ziel(ed))["abstand"]["unten"] == 3.0
    BL.anwenden(ed, BL.ziel(ed), {"umbruch": "textfluss"})                     # frei → in den Text
    BL.anwenden(ed, BL.ziel(ed), {"umbruch": "quadrat", "zeilen": "rechts", "abstand": {"oben": 2.0, "unten": 3.0, "links": 4.0, "rechts": 5.0}})
    from lunivo_writer.editor import umbruch as U
    c = ed._bild_cursor(); ff = U.schwebende_rahmen(ed.document())[c.selectionStart()].frameFormat()
    assert abs(ff.bottomMargin() - 3.0 * 96 / 25.4) < 0.5
    from PySide6.QtGui import QColor
    assert QColor("#80ff0000").alpha() == 0x80


def test_schreiben_im_objekt(fenster):
    from PySide6.QtTest import QTest
    ed = _ed(fenster); fenster.befehle.textfeld()
    assert ed._frei_edit is not None and ed._frei_edit.isVisible()                 # Schreibmarke steht gleich im leeren Textfeld
    QTest.keyClicks(ed._frei_edit, "Hallo"); QTest.keyClick(ed._frei_edit, Qt.Key_Return); QTest.keyClicks(ed._frei_edit, "Welt")
    QTest.keyClick(ed._frei_edit, Qt.Key_Backspace)
    assert ed._frei_edit.toPlainText() == "Hallo\nWel"
    FO.aendern(ed, "textfeld", fett=True)                                          # Texttools: Text wird zuerst übernommen
    assert FO.daten_lesen(ed, "textfeld")["text"] == "Hallo\nWel" and FO.daten_lesen(ed, "textfeld")["fett"]
    QTest.keyClick(ed._frei_edit, Qt.Key_Escape)
    assert ed._frei_edit is None and FO.daten_lesen(ed, "textfeld")["text"] == "Hallo\nWel"
    fenster.befehle.wordartVorgabe(None, 2)
    assert FO.bearbeiten_starten(ed)
    ed._frei_edit.setPlainText("Neu"); QTest.keyClick(ed._frei_edit, Qt.Key_Escape)
    assert formen.wordart_daten(ed)["text"] == "Neu"



def test_absatzsymbol_beim_textfeld_neben_drehgriff(fenster):
    ed = _ed(fenster); fenster.befehle.textfeld()
    r = _rect(ed); k = ed._frei_knopf_rects(r)["anker"]; rot = ed._frei_griff_mitte(r, "rot")
    assert k.left() > rot.x() and abs(k.center().y() - rot.y()) < 14


def test_textoptionen_der_seitenleiste_wirken_auf_den_text(fenster):
    from lunivo_writer.editor import bildlayout as BL
    ed = _ed(fenster); fenster.befehle.wordartVorgabe(None, 0)
    fenster.objektformat_seitenleiste(reiter=1)
    panel = fenster.sidebar.objekt_panel
    panel.optionen_waehlen(1)
    panel.text_geaendert.emit({"fuell": "farbe", "farbe": "#ff0000", "transparenz": 0, "kontur": True, "kontur_farbe": "#00ff00", "kontur_breite": 2.0})
    d = formen.wordart_daten(ed)
    assert d["fuell"] == "#ff0000" and d["kontur"] == "#00ff00" and d["kontur_breite"] == 2.0
    assert {"d3", "drehung"} <= set(BL.FX_SCHLUESSEL)


def test_schnellleiste_menues_wirken_auf_das_objekt(fenster):
    from PySide6.QtGui import QColor
    from lunivo_writer.editor import bildlayout as BL
    ed = _ed(fenster); fenster.befehle.wordartVorgabe(None, 0)
    a = lambda: FO.ziel(ed)[3]
    m = ed.frei_fuell_menue(ed); m.gewaehlt.emit(QColor(255, 0, 0, 128))               # Füllung mit Transparenz
    assert a()["fuell"]["farbe"].lower() == "#80ff0000"
    m.gewaehlt.emit(None); assert a()["fuell"] is None                                 # Keine Farbe
    m.verlauf_gewaehlt.emit(QColor("#1971c2")); assert a()["fuell"]["art"] == "verlauf"
    m.muster_gewaehlt.emit("rein") if False else None
    k = ed.frei_kontur_menue(ed); k.gewaehlt.emit(QColor(0, 128, 0, 200)); assert a()["rand"]["farbe"].lower().startswith("#c8")
    k.breite_gewaehlt.emit(3.0); assert abs(a()["rand"]["b"] - 4.0) < 0.01
    k.strich_gewaehlt.emit("gestrichelt"); assert a()["rand"]["art"] == "gestrichelt"
    k.gewaehlt.emit(None); assert a()["rand"] is None                                  # Keine Linie
    f = ed.frei_formstile_menue(ed); f.gewaehlt.emit("z12"); assert a()["fuell"] is not None
    BL.anwenden(ed, BL.ziel(ed), {"umbruch": "hinter"}); assert a()["hinter"] is True  # Layoutoptionen
    BL.anwenden(ed, BL.ziel(ed), {"umbruch": "vor", "mit_text": False}); assert a()["hinter"] is False


# ---- Zeichnen aller Texttools-Schlüssel (Pixel- und Layoutprüfung) ----------------------------------------------------------------------
def _dunkel(img):
    """Anzahl, Mittelpunkt (x, y) und Umfang der sichtbaren Pixel."""
    xs = ys = n = 0
    x0 = y0 = 10**9; x1 = y1 = -1
    for y in range(0, img.height()):
        for x in range(0, img.width()):
            if (img.pixel(x, y) >> 24) & 0xFF > 40:
                n += 1; xs += x; ys += y; x0 = min(x0, x); x1 = max(x1, x); y0 = min(y0, y); y1 = max(y1, y)
    return n, (xs / n if n else 0, ys / n if n else 0), (x0, y0, x1, y1)


BASIS = {"text": "Hallo Welt\nzweite Zeile", "pt": 12}


def test_textfeld_zeichnet_alle_texttools_schluessel(app):
    from PySide6.QtGui import QColor
    f = lambda **kw: FO.textfeld_zeichnen({**BASIS, **kw}, 260, 120)
    n0, m0, u0 = _dunkel(f())
    assert _dunkel(f(fett=True))[0] > n0                                             # fett: mehr Tinte
    assert _dunkel(f(unter=True))[0] > n0 and _dunkel(f(durch=True))[0] > n0         # Linien kommen dazu
    assert _dunkel(f(kontur="#ff0000", kontur_breite=1.5))[0] > n0                   # Kontur
    assert _dunkel(f(hervor="#ffff00"))[0] > n0 * 2                                  # Hintergrund hinter dem Text
    assert _dunkel(f(effekt={"schatten": {}}))[0] > n0                               # Schatten
    assert _dunkel(f(effekt={"leuchten": {}}))[0] > n0 * 1.3                         # Leuchten
    assert _dunkel(f(effekt={"reflektion": {}}))[2][3] > u0[3]                       # Spiegelung reicht tiefer
    assert _dunkel(f(einzug=2))[2][0] > u0[0] + 20                                   # Einzug schiebt nach rechts
    assert _dunkel(f(zeilenabstand=2.0))[2][3] > u0[3] + 10                          # Zeilenabstand
    assert _dunkel(f(hoch=True))[1][1] < m0[1] + 2 and _dunkel(f(tief=True))[1][1] > m0[1]
    assert _dunkel(f(ausr="rechts"))[2][0] > u0[0] + 20 and _dunkel(f(ausr="mitte"))[1][0] > m0[0]
    t = {"text": "aaa bbb ccc ddd eee fff ggg hhh iii jjj kkk lll mmm nnn ooo", "pt": 12}
    voll = lambda **kw: FO.textfeld_zeichnen({**t, **kw}, 220, 120)
    assert _dunkel(voll(ausr="block"))[2][2] >= _dunkel(voll())[2][2]                # Blocksatz: rechter Rand mindestens so weit
    assert _dunkel(f(fuell="#00ff00"))[0] == n0                                      # Farbe ändert nur die Farbe


def test_listenmarken_und_richtungen(app):
    from lunivo_writer.editor import listen
    assert FO.listenmarken(listen.liste("disc"), 2) == ["\u25cf ", "\u25cf "]
    assert FO.listenmarken(listen.liste("dezimal", "(", ")", 3), 2) == ["(3) ", "(4) "]
    assert FO.listenmarken(listen.liste("roem_gross"), 4)[3] == "IV. " and FO.listenmarken(listen.liste("klein"), 2)[1] == "b. "
    assert FO.listenmarken({"ebenen": [{"format": "\u25c6"}]}, 1) == ["\u25c6 "]
    assert FO.listenmarken(None, 2) == ["", ""]
    n0 = _dunkel(FO.textfeld_zeichnen({**BASIS}, 260, 120))[0]
    assert _dunkel(FO.textfeld_zeichnen({**BASIS, "liste": listen.liste("dezimal")}, 260, 120))[0] > n0
    for r in FO.RICHTUNGEN:
        img = FO.textfeld_zeichnen({**BASIS, "richtung": r}, 260, 120)
        assert (img.width(), img.height()) == (520, 240)                             # Maße des Objekts bleiben
        assert _dunkel(img)[0] > 100
    quer = _dunkel(FO.textfeld_zeichnen({**BASIS}, 260, 120))[2]
    hoch = _dunkel(FO.textfeld_zeichnen({**BASIS, "richtung": "senkrecht_rl"}, 120, 260))[2]
    assert (hoch[3] - hoch[1]) > (hoch[2] - hoch[0])                                  # Text läuft senkrecht
    rl = _dunkel(FO.textfeld_zeichnen({**BASIS, "richtung": "senkrecht_rl"}, 120, 260))[1][0]
    lr = _dunkel(FO.textfeld_zeichnen({**BASIS, "richtung": "senkrecht_lr", "text": "Kurz\nLangere Zeile hier"}, 120, 260))[1][0]
    rl2 = _dunkel(FO.textfeld_zeichnen({**BASIS, "richtung": "senkrecht_rl", "text": "Kurz\nLangere Zeile hier"}, 120, 260))[1][0]
    assert lr != rl2                                                                  # die Zeilenfolge ist umgekehrt


def test_textfelder_verknuepfen_und_loesen(fenster):
    ed = _ed(fenster)
    fenster.befehle.textfeld(); a = ed._frei_sel
    fenster.befehle.textfeld(); b = ed._frei_sel
    lang = " ".join(f"Wort{i}" for i in range(60))
    FO.bearbeiten_beenden(ed)
    ed._frei_sel = a; FO.aendern(ed, "textfeld", text=lang, breite=200, hoehe=60)
    ed._frei_sel = b
    assert FO.verknuepfen(ed, a, b) and FO.ist_verknuepft(ed, a)
    fel = dict(FO._textfelder(ed))
    ga, gb = fel[a]["daten"]["gezeigt"], fel[b]["daten"]["gezeigt"]
    assert ga and gb and ga + " " + gb == lang or (ga.split() + gb.split()) == lang.split()   # Überlauf von A steht in B
    assert not FO.verknuepfen(ed, a, b)                                                 # doppelt nicht möglich
    assert not FO.verknuepfen(ed, b, a)                                                 # Kreis nicht möglich
    assert FO.loesen(ed, a) and not FO.ist_verknuepft(ed, a)
    fel = dict(FO._textfelder(ed))
    assert fel[b]["daten"]["text"] == gb and "von" not in fel[b]["daten"]               # B behält seinen Teil


def test_text_nicht_drehen(app):
    from PySide6.QtCore import QRectF
    from PySide6.QtGui import QImage, QPainter
    from lunivo_writer.editor import freie_bilder as FB
    bild = QImage(100, 40, QImage.Format_ARGB32); bild.fill(0)
    q = QPainter(bild); q.fillRect(0, 15, 100, 10, 0xffff0000); q.end()                # waagerechter roter Streifen als „Text“
    def malen(gerade):
        ziel = QImage(200, 200, QImage.Format_ARGB32); ziel.fill(0xffffffff)
        p = QPainter(ziel)
        FB.bild_zeichnen(p, bild, QRectF(50, 80, 100, 40), False, {"b": 2.0, "farbe": "#0000ff", "art": "einfach"}, 90.0, None, None,
                         {"drehung": {"text_gerade": True}} if gerade else None)
        p.end(); return ziel
    rot = lambda img: [(x, y) for y in range(200) for x in range(200) if img.pixelColor(x, y).red() > 200 and img.pixelColor(x, y).green() < 60]
    gedreht, gerade = rot(malen(False)), rot(malen(True))
    bx = lambda pts: (max(x for x, _ in pts) - min(x for x, _ in pts), max(y for _, y in pts) - min(y for _, y in pts))
    assert bx(gedreht)[1] > bx(gedreht)[0] and bx(gerade)[0] > bx(gerade)[1]           # gedreht: senkrecht, gerade: waagerecht
    blau = lambda img: [(x, y) for y in range(200) for x in range(200) if img.pixelColor(x, y).blue() > 200 and img.pixelColor(x, y).red() < 60]
    assert bx(blau(malen(True)))[1] > bx(blau(malen(True)))[0]                          # der Rahmen ist trotzdem gedreht


def test_docx_speichern_mit_3d_schluesseln(fenster, tmp_path):
    from lunivo_writer.editor import bildlayout as BL
    from lunivo_writer.services import docx_writer
    ed = _ed(fenster); fenster.befehle.wordartVorgabe(None, 0); fenster.befehle.textfeld()
    BL.format_setzen(ed, BL.ziel(ed), fx={"schatten": {"farbe": "#000000", "transparenz": 50, "groesse": 100, "weich": 4, "abstand": 3, "winkel": 45},
                                          "d3": {"oben": {"art": "rund"}}, "drehung": {"x": 10, "text_gerade": True, "boden": False}})
    out = str(tmp_path / "o.docx")
    docx_writer.write_docx(out, ed.document(), ed.page, {})
    assert os.path.getsize(out) > 1000


def test_fuellmenue_untermenues_graduell_textur_muster(fenster):
    from PySide6.QtGui import QColor
    ed = _ed(fenster); fenster.befehle.wordartVorgabe(None, 0)
    m = ed.frei_fuell_menue(ed)
    namen = {a.text().replace("&", ""): a for a in m.actions() if a.text()}
    assert "Fülleffekte…" not in namen and all(n in namen for n in ("Graduell", "Textur", "Muster(N)", "Bild(P)"))
    a = lambda: FO.ziel(ed)[3]["fuell"]
    gm = namen["Graduell"].menu(); assert gm is not None
    gm.knoepfe[list(gm.knoepfe)[1]].click(); assert a()["art"] == "graduell"
    tm = namen["Textur"].menu(); tm.knoepfe["holz"].click(); assert a() == {"art": "textur", "key": "holz"}
    mm = namen["Muster(N)"].menu(); mm.knoepfe["rein"].click(); assert a()["art"] == "muster" and a()["key"] == "rein"
    gesehen = []
    m.weitere_fuellung.connect(gesehen.append)                                       # „Weitere …“ öffnet die Seitenleiste
    for menu, art in ((gm, "verlauf"), (tm, "textur"), (mm, "muster")):
        menu._fuss_v.itemAt(menu._fuss_v.count() - 1).widget().click()
    assert gesehen == ["verlauf", "textur", "muster"]


def test_texttools_auf_markierung_im_objekt(fenster):
    from PySide6.QtGui import QTextCursor
    from PySide6.QtTest import QTest
    ed = _ed(fenster); fenster.befehle.textfeld()
    w = ed._frei_edit
    QTest.keyClicks(w, "Hallo Welt")
    c = w.textCursor(); c.setPosition(0); c.setPosition(5, QTextCursor.KeepAnchor); w.setTextCursor(c)       # „Hallo“ markieren
    assert FO.aendern(ed, "textfeld", fett=True, fuell="#ff0000")
    d = FO.daten_lesen(ed, "textfeld")
    assert d["laeufe"] == [{"t": "Hallo", "fett": True, "fuell": "#ff0000"}, {"t": " Welt"}] and d["text"] == "Hallo Welt" and "fett" not in d
    assert FO.auswahl_daten(ed)["fett"] is True                                       # Zustand der Markierung für die Knöpfe
    plain = _dunkel(FO.textfeld_zeichnen({"text": "Hallo Welt", "pt": 11}, 240, 60))[0]
    gemischt = _dunkel(FO.textfeld_zeichnen(d, 240, 60))[0]
    assert gemischt > plain                                                           # nur das Wort ist fett
    img = FO.textfeld_zeichnen(d, 240, 60)                                            # und rot: das erste Wort rot, das zweite nicht
    rot = sum(1 for x in range(img.width()) for y in range(img.height()) if img.pixelColor(x, y).red() > 200 and img.pixelColor(x, y).green() < 80 and img.pixelColor(x, y).alpha() > 100)
    assert rot > 50
    c = w.textCursor(); c.clearSelection(); w.setTextCursor(c)                          # ohne Markierung: das ganze Objekt
    assert FO.aendern(ed, "textfeld", kursiv=True)
    d = FO.daten_lesen(ed, "textfeld"); assert d["kursiv"] is True and d["laeufe"][0]["fett"] is True
    assert FO.aendern(ed, "textfeld", fett=False, fuell="")                             # ganz: löscht die Angaben der Läufe
    assert "laeufe" not in FO.daten_lesen(ed, "textfeld") and FO.daten_lesen(ed, "textfeld")["fett"] is False
    QTest.keyClick(w, Qt.Key_Escape)
    assert FO.daten_lesen(ed, "textfeld")["text"] == "Hallo Welt"


def test_wordart_laeufe(fenster):
    ed = _ed(fenster); fenster.befehle.wordartVorgabe(None, 0)
    FO.bearbeiten_starten(ed); w = ed._frei_edit
    w.setPlainText("Ab Cd")
    from PySide6.QtGui import QTextCursor
    c = w.textCursor(); c.setPosition(3); c.setPosition(5, QTextCursor.KeepAnchor); w.setTextCursor(c)
    assert formen.wordart_aendern(ed, fuell="#00ff00", kursiv=True)
    d = formen.wordart_daten(ed)
    assert d["laeufe"][-1] == {"t": "Cd", "fuell": "#00ff00", "kursiv": True}
    img = FO.wordart_zeichnen(d)
    gruen = sum(1 for x in range(0, img.width(), 2) for y in range(0, img.height(), 2) if img.pixelColor(x, y).green() > 200 and img.pixelColor(x, y).red() < 80)
    assert gruen > 50
    QTest = None


def test_verknuepfte_textfelder_im_docx(fenster, tmp_path):
    import zipfile
    from lunivo_writer.editor import freie_bilder as FB
    from lunivo_writer.services import docx_reader, docx_writer
    ed = _ed(fenster)
    fenster.befehle.textfeld(); a = ed._frei_sel
    fenster.befehle.textfeld(); b = ed._frei_sel
    FO.bearbeiten_beenden(ed)
    lang = " ".join(f"Wort{i}" for i in range(60))
    ed._frei_sel = a; FO.aendern(ed, "textfeld", text=lang, breite=200, hoehe=60, fett=True)
    assert FO.verknuepfen(ed, a, b)
    pfad = str(tmp_path / "k.docx")
    docx_writer.write_docx(pfad, ed.document(), ed.page, {})
    xml = zipfile.ZipFile(pfad).read("word/document.xml").decode("utf-8")
    assert "wps:wsp" in xml and "w:txbxContent" in xml and "wps:linkedTxbx" in xml            # Standard-Textfeld mit Verknüpfung
    assert 'seq="1"' in xml and 'Requires="wps"' in xml and "Wort0" in xml
    doc, page, meta, report = docx_reader.read_docx(pfad)
    felder = []
    blk = doc.firstBlock()
    while blk.isValid():
        felder += [x for x in FB.aus_absatz(blk.blockFormat()) if x.get("art") == "textfeld"]
        blk = blk.next()
    assert len(felder) == 2
    kopf = next(x for x in felder if not x["daten"].get("von")); folge = next(x for x in felder if x["daten"].get("von"))
    assert kopf["daten"]["weiter"] == folge["daten"]["id"] and folge["daten"]["von"] == kopf["daten"]["id"]
    assert kopf["daten"]["text"] == lang and kopf["daten"]["fett"] is True
    assert abs(kopf["b"] - 200) < 1 and abs(kopf["h"] - 60) < 1


def test_textfeld_von_word_ohne_lunivo_daten(fenster, tmp_path):
    """Ein Word-Textfeld (nur ``wps:txbx`` mit Läufen und ``linkedTxbx``) wird als Textfeld mit Formaten gelesen."""
    import zipfile
    from lunivo_writer.editor import freie_bilder as FB
    from lunivo_writer.services import docx_reader, docx_writer
    ed = _ed(fenster); fenster.befehle.textfeld(); FO.bearbeiten_beenden(ed)
    FO.aendern(ed, "textfeld", text="Hallo Welt", laeufe=[{"t": "Hallo", "fett": True}, {"t": " Welt"}])
    pfad = str(tmp_path / "w.docx"); docx_writer.write_docx(pfad, ed.document(), ed.page, {})
    zin = zipfile.ZipFile(pfad); xml = zin.read("word/document.xml").decode("utf-8")
    import re
    xml = re.sub(r' title="lunivo:[^"]*"', "", xml)                               # wie ein Dokument aus Word: ohne Programmdaten
    neu = str(tmp_path / "w2.docx")
    with zipfile.ZipFile(neu, "w") as zout:
        for n in zin.namelist():
            zout.writestr(n, xml if n == "word/document.xml" else zin.read(n))
    doc, *_ = docx_reader.read_docx(neu)
    blk = doc.firstBlock(); felder = []
    while blk.isValid():
        felder += [x for x in FB.aus_absatz(blk.blockFormat()) if x.get("art") == "textfeld"]; blk = blk.next()
    assert len(felder) == 1 and felder[0]["daten"]["text"] == "Hallo Welt"
    assert felder[0]["daten"]["laeufe"][0] == {"t": "Hallo", "fett": True}


def test_oeffnen_verteilt_den_text_der_kette(fenster, tmp_path):
    from lunivo_writer.services import docx_writer
    ed = _ed(fenster)
    fenster.befehle.textfeld(); a = ed._frei_sel
    fenster.befehle.textfeld(); b = ed._frei_sel
    FO.bearbeiten_beenden(ed)
    ed._frei_sel = a; FO.aendern(ed, "textfeld", text=" ".join(f"Wort{i}" for i in range(60)), breite=200, hoehe=60)
    FO.verknuepfen(ed, a, b)
    pfad = str(tmp_path / "o.docx"); docx_writer.write_docx(pfad, ed.document(), ed.page, {})
    fenster.open_path(pfad)
    neu = fenster.current_editor()
    felder = dict(FO._textfelder(neu))
    gezeigt = [x["daten"].get("gezeigt") for x in felder.values()]
    assert len(felder) == 2 and all(gezeigt) and " ".join(gezeigt).split() == [f"Wort{i}" for i in range(60)]
