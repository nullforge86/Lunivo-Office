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
    assert set(ed._frei_knopf_rects(r)) == {"anker", "minus", "layout", "formstile", "fuell", "kontur", "zahnrad"}


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


# ---- Form, Diagramm und SmartArt als freie Objekte --------------------------------------------------------------------------------
def _docx_rundweg(ed, tmp_path):
    """Speichert als DOCX, liest wieder und gibt die freien Angaben (art == Form/Diagramm/SmartArt) in Lesereihenfolge zurück."""
    from lunivo_writer.editor import freie_bilder as FB
    from lunivo_writer.services import docx_reader, docx_writer
    pfad = str(tmp_path / "f.docx")
    docx_writer.write_docx(pfad, ed.document(), ed.page, {})
    doc = docx_reader.read_docx(pfad)[0]
    out, blk = [], doc.firstBlock()
    while blk.isValid():
        out += [x for x in FB.aus_absatz(blk.blockFormat()) if x.get("art") in ("form", "diagramm", "smartart")]
        blk = blk.next()
    return out


def test_form_als_freies_objekt_aendern_und_docx(fenster, tmp_path):
    ed = _ed(fenster)
    FO.einfuegen(ed, "form", {**FO.FORM_STANDARD, "form": "Ellipse"}, 200, 100)
    assert FO.art_gewaehlt(ed) == "form" and fenster.befehle.tt_art() is None            # keine Texttools für Formen
    assert formen.aendern(ed, fuell="#ff0000", linie="#00ff00", strich=3.0, text="Hallo")
    d = FO.daten_lesen(ed, "form")
    assert d["fuell"] == "#ff0000" and d["linie"] == "#00ff00" and d["strich"] == 3.0 and d["text"] == "Hallo"
    assert formen.vorlage(ed, "Grün") and FO.daten_lesen(ed, "form")["fuell"] == "#6bbf59"
    assert FO.aendern(ed, "form", form_fuell="#0000ff") and FO.daten_lesen(ed, "form")["fuell"] == "#0000ff"
    z = FO.ziel(ed)
    assert z[3].get("fuell") is None                                                       # kein Kasten ums Bild
    neu = FO.nach_groesse(ed, dict(z[3], b=300, h=150))                                    # neue Größe: frisch gezeichnet, scharf (doppelt)
    bild = ed.document().resource(3, __import__("PySide6.QtCore", fromlist=["QUrl"]).QUrl(neu["n"]))
    assert bild.width() == 300 * FO._SS and bild.height() == 150 * FO._SS
    (a,) = _docx_rundweg(ed, tmp_path)
    assert a["art"] == "form" and a["daten"]["fuell"] == "#0000ff" and a["daten"]["form"] == "Ellipse"


def test_diagramm_als_freies_objekt_und_diagrammtools(fenster, tmp_path):
    from lunivo_writer.editor import diagramm as D
    ed = _ed(fenster); b = fenster.befehle
    daten = {"art": "saeule_gruppiert", "titel": "Umsatz", "kategorien": list(D.BEISPIEL_KATEGORIEN), "reihen": dict(D.BEISPIEL_REIHEN)}
    FO.einfuegen(ed, "diagramm", daten, 480, 300)
    assert FO.art_gewaehlt(ed) == "diagramm" and b.tt_art() is None
    fenster._sync_format()                                                                 # Kontext „diagramm“ ohne vorhandenen Reiter: kein Absturz
    b.diagrammStil(3); assert FO.daten_lesen(ed, "diagramm")["stil"] == 3
    b.diagrammSchnelllayout(3); d = FO.daten_lesen(ed, "diagramm")
    assert d["labels"] is True and d["legende"] is False
    mf = b.menue_diagrammFarben(); mf.actions()[1].trigger()
    assert FO.daten_lesen(ed, "diagramm")["farben"][0] == D.VORLAGEN["vorlage_blau"][1][0]
    m = b.menue_diagrammElement(); assert [a.text() for a in m.actions()][:2] == ["Diagrammtitel", "Legende"]
    b.diagrammTitel(); assert FO.daten_lesen(ed, "diagramm")["titel_an"] is False and not b.an_diagrammTitel()
    ms = b.menue_diagrammSchnelllayout(); assert len(ms.actions()) >= 4
    FO.aendern(ed, "diagramm", untertyp="kreis", reihen={"A": [1.0, 2.0, 3.0, 4.0]})
    assert FO.daten_lesen(ed, "diagramm")["art"] == "kreis"
    b.diagrammZuruecksetzen(); d = FO.daten_lesen(ed, "diagramm")
    assert not ({"farben", "labels", "stil", "legende", "titel_an"} & set(d)) and d["titel"] == "Umsatz"
    (a,) = _docx_rundweg(ed, tmp_path)
    assert a["art"] == "diagramm" and a["daten"] == d


def test_smartart_und_form_ohne_auswahl_aendern_nichts(fenster):
    ed = _ed(fenster); b = fenster.befehle
    b.diagrammStil(1)                                                                      # kein Diagramm gewählt: Hinweis, kein Absturz
    assert "Diagramm" in fenster.lbl_msg.text() and not formen.aendern(ed, fuell="#fff")


def test_smartart_als_freies_objekt_menues(fenster, tmp_path):
    from lunivo_writer.editor import smartart as SA
    ed = _ed(fenster); b = fenster.befehle
    FO.einfuegen(ed, "smartart", {"layout": "Prozess", "farben": "Blau", "text": "A\nB\nC"})
    assert FO.art_gewaehlt(ed) == "smartart"
    ml = b.menue_smartartLayout(); ml.actions()[2].trigger(); mc = b.menue_smartartFarben(); mc.actions()[1].trigger()
    d = SA.daten_der_auswahl(ed)
    assert d["layout"] == SA.LAYOUT_KATALOG[2]["schluessel"] == "Punktliste" and d["farben"] == list(SA.FARBEN)[1]
    (a,) = _docx_rundweg(ed, tmp_path)
    assert a["art"] == "smartart" and a["daten"] == d


def test_bild_und_piktogramm_als_freies_bild(fenster, tmp_path):
    from PySide6.QtGui import QColor, QImage
    from lunivo_writer.editor import bildlayout as BL, freie_bilder as FB
    from lunivo_writer.services import docx_reader, docx_writer
    ed = _ed(fenster); b = fenster.befehle
    img = QImage(400, 200, QImage.Format_RGB32); img.fill(QColor("red")); pfad = str(tmp_path / "r.png"); img.save(pfad)
    assert ed.insert_image(pfad)
    assert ed._frei_sel is not None and FO.art_gewaehlt(ed) is None and ed.bild_format() is None      # freies Bild ohne Parameter
    z = BL.ziel(ed); assert z[0] == "frei" and z[2]["b"] == 400
    BL.frei_aendern(ed, z, alt="Rotes Feld")
    z = BL.ziel(ed)
    assert BL.frei_bild_ersetzen(ed, z, lambda i: i.copy(0, 0, 100, 100)); z = BL.ziel(ed)
    assert z[2]["h"] == 400 and z[2].get("orig")                                                         # Breite bleibt, Höhe folgt dem Zuschnitt
    assert BL.frei_original(ed, z); z = BL.ziel(ed); assert z[2]["h"] == 200
    assert BL.frei_original_groesse(ed, BL.ziel(ed))
    FO.einfuegen(ed, "piktogramm", {"name": "heart", "farbe": "#ff0000"}, 96, 96)
    assert FO.art_gewaehlt(ed) == "piktogramm" and b.tt_art() is None
    fenster._sync_format()
    pfad2 = str(tmp_path / "p.docx")
    docx_writer.write_docx(pfad2, ed.document(), ed.page, {})
    doc = docx_reader.read_docx(pfad2)[0]
    angaben, blk = [], doc.firstBlock()
    while blk.isValid():
        angaben += FB.aus_absatz(blk.blockFormat()); blk = blk.next()
    assert [x.get("art") for x in angaben] == [None, "piktogramm"] and angaben[0].get("alt") == "Rotes Feld"
    assert BL.frei_entfernen(ed) and ed._frei_sel is None


def test_bild_zuschneiden_nicht_zerstoerend_masken_docx(fenster, tmp_path):
    from PySide6.QtGui import QColor, QImage
    from lunivo_writer.editor import bildlayout as BL, bildwerkzeuge as BW, bildzuschnitt as BZ, freie_bilder as FB
    from lunivo_writer.services import docx_reader, docx_writer
    ed = _ed(fenster); b = fenster.befehle
    b.bildZuschneidenModus(); assert not b.an_bildZuschneidenModus()                                      # ohne Bild: nur Hinweis
    img = QImage(400, 200, QImage.Format_RGB32); img.fill(QColor("red")); pfad = str(tmp_path / "r.png"); img.save(pfad)
    assert ed.insert_image(pfad)
    b.bildZuschneidenModus(); assert b.an_bildZuschneidenModus()
    # Ziehen am rechten Mittelgriff im Zuschneiden-Modus schneidet ab, das Bild selbst bleibt unverändert
    r = _rect(ed); start = QPointF(r.right(), r.center().y())
    _maus(ed, QEvent.MouseButtonPress, start); _maus(ed, QEvent.MouseMove, start - QPointF(r.width() / 4, 0)); _maus(ed, QEvent.MouseButtonRelease, start - QPointF(r.width() / 4, 0))
    z = BL.ziel(ed); l, o, rr, u = BZ.lesen(z[2])
    assert abs(rr - 0.25) < 0.02 and l == o == u == 0 and abs(z[2]["b"] - 300) < 8
    assert FB.bild_im_dokument(ed.document(), z[2]["n"]).width() == 400 and z[3].width() == 300
    # Nach Skala 1:1: mittiger Ausschnitt 200 x 200 der Quelle, Breite des Rahmens bleibt
    b.bildZuschneidenSkala(None, "1:1"); z = BL.ziel(ed)
    assert abs(z[2]["h"] - z[2]["b"]) < 0.5 and z[3].width() == z[3].height() == 200
    b.bildZuschneidenForm(None, "Ellipse"); z = BL.ziel(ed)
    assert z[2]["maske"] == "Ellipse" and z[3].pixelColor(0, 0).alpha() == 0 and z[3].pixelColor(100, 100).alpha() == 255
    assert any(n == "Herz" for _k, ns in BZ.formen_kategorien() for n in ns) and not any(BZ.formen_kategorien()[0][0] == "Linie" for _ in [0])
    m = b.menue_bildZuschneiden(); assert m is not None
    pfad2 = str(tmp_path / "z.docx")
    docx_writer.write_docx(pfad2, ed.document(), ed.page, {})
    doc = docx_reader.read_docx(pfad2)[0]
    angaben, blk = [], doc.firstBlock()
    while blk.isValid():
        angaben += FB.aus_absatz(blk.blockFormat()); blk = blk.next()
    assert angaben and abs(BZ.lesen(angaben[0])[0] - BZ.lesen(z[2])[0]) < 0.001 and angaben[0].get("maske") == "Ellipse"
    b.bildZuschneidenZuruecksetzen(); z = BL.ziel(ed)
    assert not BZ.hat(z[2]) and abs(z[2]["h"] / z[2]["b"] - 0.5) < 0.01 and not b.an_bildZuschneidenModus()
    # Bildtools am freien Bild
    b.bildSeitenverhaeltnis(); assert b.an_bildSeitenverhaeltnis()
    BW.transparent(ed, BL.ziel(ed), QColor("red")); assert BL.ziel(ed)[3].pixelColor(5, 5).alpha() == 0
    BW.zuruecksetzen(ed, BL.ziel(ed)); z = BL.ziel(ed); assert z[3].pixelColor(5, 5).alpha() == 255 and "sperre" not in z[2]
    img2 = QImage(100, 100, QImage.Format_RGB32); img2.fill(QColor("blue")); p2 = str(tmp_path / "b.png"); img2.save(p2)
    b.bildAendern(None, p2); z = BL.ziel(ed); assert z[3].width() == 100 and abs(z[2]["h"] - z[2]["b"]) < 0.5
    BZ.skala(ed, z, 2, 1); z = BL.ziel(ed)
    assert BW.komprimieren(ed, z) is not None and not BL.ziel(ed)[2].get("zu")
    b.bildGroesseZuruecksetzen(); assert BL.ziel(ed)[2]["b"] > 0
    b.bildZuruecksetzen()


def test_diagrammbefehle_mit_bandangabe(fenster):
    ed = _ed(fenster); b = fenster.befehle
    FO.einfuegen(ed, "diagramm", {"art": "saeule_gruppiert", "titel": "T", "kategorien": ["a", "b"], "reihen": {"R": [1, 2]}}, 300, 200)
    b.tun("diagrammStil:[2]"); assert FO.daten_lesen(ed, "diagramm")["stil"] == 2                  # (Knopf, Nummer) wie vom Band
    b.tun("diagrammSchnelllayout:[5]"); assert FO.daten_lesen(ed, "diagramm")["legende"] is False
    b.tun("diagrammZuruecksetzen"); assert "stil" not in FO.daten_lesen(ed, "diagramm")
    fenster.band.kontext("diagramm", True)                                                        # ohne Reiter kein Absturz


# ---- Diagramm: Teile, Elemente, Filter, Teilformate; Formstil-Raster und Anpassungsgriff ------------------------------------------------
def _dg(fenster, **zusatz):
    ed = _ed(fenster)
    FO.einfuegen(ed, "diagramm", {"art": "saeule_gruppiert", "titel": "Umsatz", "kategorien": ["A", "B", "C"],
                                  "reihen": {"X": [1, 2, 3], "Y": [3, 1, 2]}, **zusatz}, 400, 260)
    return ed, fenster.befehle


def test_diagramm_teile_rechtecke_und_treffer(fenster):
    from lunivo_writer.editor import diagramm as D, diagramm_teile as T
    ed, b = _dg(fenster)
    d = FO.daten_lesen(ed, "diagramm")
    schl = [k for k, _n in D.teile(d)]
    assert schl[:4] == ["diagrammbereich", "zeichnungsbereich", "titel", "legende"] and "reihe_1" in schl and "legendeneintrag_0" in schl
    r = D.teil_rechtecke(d, 400, 260)
    assert set(r) == set(schl) and all(0 <= v.x() and v.right() <= 401 and v.bottom() <= 261 for v in r.values())
    b.tun('diagrammTeilWaehlen:["reihe_0"]')
    assert T.teil_gewaehlt(ed) == "reihe_0" and b.feld_diagrammTeil() == "Reihe „X“"
    bal = D.teil_geo(d, 400, 260)["balken_1"][0]
    ed._frei_liste(); rr = _rect(ed)
    mitte = QPointF(rr.x() + bal.center().x() * rr.width() / 400, rr.y() + bal.center().y() * rr.height() / 260)
    assert T.teil_bei(ed, mitte) == "reihe_1"
    assert T.teil_bei(ed, QPointF(rr.x() + 3, rr.y() + 3)) == "diagrammbereich"
    assert T.teil_bei(ed, QPointF(rr.x() - 50, rr.y() - 50)) is None


def test_diagramm_elemente_filter_format_und_zuruecksetzen(fenster):
    from lunivo_writer.editor import diagramm as D, diagramm_teile as T
    ed, b = _dg(fenster)
    glatt = D.bild_aus_daten(FO.daten_lesen(ed, "diagramm"), 400, 260)
    for name in ("achsentitel", "datentabelle", "fehlerindikatoren", "trendlinie", "gitter"):
        b.tun(f'diagrammElement:["{name}"]')
        erwartet = name != "gitter"                                                                  # Gitternetzlinien sind von Haus aus an
        assert FO.daten_lesen(ed, "diagramm")["elemente"][name] is erwartet and getattr(b, "an_diagrammElement_" + name)() is erwartet
    assert D.bild_aus_daten(FO.daten_lesen(ed, "diagramm"), 400, 260) != glatt
    b.tun('diagrammElement:["legende", "rechts"]'); d = FO.daten_lesen(ed, "diagramm")
    assert d["legende"] is True and d["legende_pos"] == "rechts"
    b.tun('diagrammElement:["titel"]'); assert not b.an_diagrammElement_titel() and "titel" not in dict(D.teile(FO.daten_lesen(ed, "diagramm")))
    b.diagrammTitel(); assert b.an_diagrammElement_titel()                                       # alter Umschalter wirkt weiter
    # Filter
    assert b.diagrammFilterDaten()["reihen"] == [("X", True), ("Y", True)]
    b.tun('diagrammFilterSetzen:[{"reihen": ["Y"], "rubriken": ["B"]}]')
    assert b.diagrammFilterDaten() == {"reihen": [("X", True), ("Y", False)], "rubriken": [("A", True), ("B", False), ("C", True)]}
    assert [k for k, _n in D.teile(FO.daten_lesen(ed, "diagramm")) if k.startswith("reihe_")] == ["reihe_0"]
    # Teilformat
    b.diagrammTeilWaehlen(None, "titel")
    assert T.diagramm_teil_format_setzen(ed, text={"groesse": 18, "fett": True}, fuell="#ffeeee") and T.diagramm_teil_format_setzen(ed, text={"farbe": "#aa0000"})
    assert T.diagramm_teil_format_lesen(ed) == {"text": {"groesse": 18, "fett": True, "farbe": "#aa0000"}, "fuell": "#ffeeee"}
    b.tun('diagrammTeilFormat:[{"teil": "reihe_0", "fuell": "#ff0000", "schatten": true}]')
    assert FO.daten_lesen(ed, "diagramm")["teil_format"]["reihe_0"]["fuell"] == "#ff0000"
    img = D.bild_aus_daten(FO.daten_lesen(ed, "diagramm"), 400, 260)
    assert not img.isNull()
    b.diagrammAltText(None, "T", "Beschreibung"); assert FO.daten_lesen(ed, "diagramm")["alt_beschreibung"] == "Beschreibung"
    b.diagrammZuruecksetzen(); d = FO.daten_lesen(ed, "diagramm")
    assert not ({"elemente", "ausgeblendet", "teil_format", "teil", "stil"} & set(d)) and d["alt_titel"] == "T" and d["reihen"]


def test_diagramm_stile_und_farbschemen():
    from lunivo_writer.editor import diagramm as D
    assert len(D.STILE) >= 12 and D.STILE[0][0] == "Standard" and D.STILE[3][0] == "Dunkel" and len(D.stile_liste()) == len(D.STILE)
    assert len({(s[1], s[2], s[3]) for s in D.STILE}) >= 10                                            # gut unterscheidbar
    g = dict(D.farbschemen_gruppen())
    assert set(g) == {"Farbig", "Monochrom"} and len(g["Farbig"]) >= 3 and all(len(f) == 6 for _n, f in g["Farbig"] + g["Monochrom"])
    for i in range(len(D.STILE)):
        assert not D.bild("saeule_gruppiert", "T", ["a", "b"], {"R": [1, 2]}, 200, 140, stil=i).isNull()


def test_diagramm_docx_rundweg_mit_elementen_und_filter(fenster, tmp_path):
    ed, b = _dg(fenster)
    b.tun('diagrammElement:["datentabelle"]'); b.tun('diagrammFilterSetzen:[{"rubriken": ["B"]}]')
    b.tun('diagrammTeilFormat:[{"fuell": "#ddeeff"}]'); b.diagrammTeilWaehlen(None, "legende"); b.diagrammAltText(None, "", "Alt")
    d = FO.daten_lesen(ed, "diagramm")
    (a,) = _docx_rundweg(ed, tmp_path)
    assert a["daten"] == {k: v for k, v in d.items() if k != "teil"}


def test_formstil_raster_und_anpassungsgriff(fenster):
    from PySide6.QtCore import QRectF
    from lunivo_writer.editor import formen_anpassen as A, formen_katalog as K, formen_stile as S
    ed = _ed(fenster); b = fenster.befehle
    raster = b.formstileRaster(); assert len(raster) == 6 and all(len(z) == 7 for z in raster)
    FO.einfuegen(ed, "form", {**FO.FORM_STANDARD, "form": "Stern mit 5 Zacken"}, 160, 120)
    for zeile in range(6):
        b.tun(f"formStilRaster:[{zeile}, 1]")
        d = FO.daten_lesen(ed, "form"); w = S.formstil(zeile, 1)
        assert d["fuell"] == w["fuell"] and d["linie"] == w["linie"] and (d.get("fuell_art") or "") == w["fuell_art"]
    assert FO.ziel(ed)[3].get("fx") and not b.zeichenFuellungDaten()["thema"][0][0] == ""
    r = QRectF(0, 0, 160, 120)
    g = A.griffe("Stern mit 5 Zacken", r)[0]
    assert formen.anpass_griff("Stern mit 5 Zacken", r, [0.5]) is not None and formen.anpass_griff("Linie", r) is None
    assert abs(formen.anpass_wert("Stern mit 5 Zacken", r, g) - 0.42) < 1e-6
    assert formen.anpassen("Stern mit 5 Zacken", 2.0) == [0.95]                                         # begrenzt
    standard = K.pfad("Pfeil nach rechts", r).boundingRect(); schmal = K.pfad("Pfeil nach rechts", r, [0.2, 0.2])
    assert schmal != K.pfad("Pfeil nach rechts", r) and abs(schmal.boundingRect().width() - standard.width()) < 1e-6
    assert b.kann_formAnpassen() and b.formAnpassen(None, 0.8, 0) and FO.daten_lesen(ed, "form")["adj"] == [0.8]
    before = FO.ziel(ed)[3]["b"]
    b.tun('formAendern:["Pfeil nach rechts"]'); d = FO.daten_lesen(ed, "form")
    assert d["form"] == "Pfeil nach rechts" and "adj" not in d and FO.ziel(ed)[3]["b"] == before and d["fuell"]
    b.formAnpassen(None, 0.3, 1); assert FO.daten_lesen(ed, "form")["adj"] == [0.5, 0.3]
    assert b.formPunkteBearbeiten() and ed.__dict__.get("_fp_key") is not None and FO.daten_lesen(ed, "form")["form"] == "Freiform"      # Punkte bearbeiten: Freiform
