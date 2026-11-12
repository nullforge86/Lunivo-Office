"""Seitenlauf (Layout-Schicht): Abschnitte mit eigenen Rändern und Spalten, Seitenumbruch, Absatz über Seiten, Hit-Test."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
from PySide6.QtCore import QPointF
from PySide6.QtGui import QFont, QTextBlockFormat, QTextCursor, QTextDocument

from lunivo_writer.editor.layout.seitenlauf import Seitenlauf, unterstuetzt
from lunivo_writer.editor.seite import abschnitte as AB
from lunivo_writer.modelle.seite import PageSettings, mm_to_px


def _doc(absaetze=6, woerter=60):
    d = QTextDocument()
    d.setDefaultFont(QFont("Liberation Sans", 11))
    d.setPlainText("\n".join(f"Absatz {i} " + "Text " * woerter for i in range(absaetze)))
    return d


def _basis(**kw):
    return PageSettings(width_mm=210, height_mm=297, margin_left_mm=20, margin_right_mm=20, margin_top_mm=20, margin_bottom_mm=20, **kw)


def _abschnitt(doc, nach_block, basis, typ="naechste", **aendern):
    c = QTextCursor(doc)
    c.setPosition(doc.findBlockByNumber(nach_block).position() + 2)
    AB.einfuegen(doc, c, typ, basis)
    ps = AB.einrichtung(doc, basis, 1)
    for k, v in aendern.items():
        setattr(ps, k, v)
    AB.setzen(doc, 1, ps, typ)


def _lauf(doc, basis):
    lay = Seitenlauf(doc, basis)
    doc.setDocumentLayout(lay)
    lay.anordnen()
    return lay


def test_ein_abschnitt_ein_blatt_ränder_wie_eingestellt(app):
    d = _doc(2, 10)
    lay = _lauf(d, _basis())
    r = lay.blockBoundingRect(d.firstBlock())
    assert lay.pageCount() == 1 and r.x() == pytest.approx(mm_to_px(20), abs=1) and r.y() == pytest.approx(mm_to_px(20), abs=1)
    assert unterstuetzt(d)


def test_abschnitt_beginnt_neues_blatt_mit_eigenen_raendern(app):
    d = _doc(6, 60)
    basis = _basis()
    _abschnitt(d, 2, basis, margin_left_mm=50.0, margin_right_mm=10.0)
    lay = _lauf(d, basis)
    assert lay.pageCount() == 2
    nach = AB.beginn(d, 1)
    erster = d.findBlock(nach)
    r = lay.blockBoundingRect(erster)
    assert lay.blatt_von_block(erster.blockNumber()) == 1 and r.x() == pytest.approx(mm_to_px(50), abs=1)
    assert r.y() == pytest.approx(lay.erg.blaetter[1].oben + mm_to_px(20), abs=1)                # oben auf dem zweiten Blatt
    assert r.width() <= mm_to_px(210 - 50 - 10) + 1                                             # nicht breiter als die Textfläche


def test_fortlaufend_gleiche_geometrie_bleibt_auf_dem_blatt(app):
    d = _doc(4, 10)
    basis = _basis()
    _abschnitt(d, 1, basis, typ="fortlaufend")
    assert _lauf(d, basis).pageCount() == 1


def test_absatz_laeuft_ueber_die_seite(app):
    d = _doc(1, 4000)                                                                           # ein sehr langer Absatz
    lay = _lauf(d, _basis())
    assert lay.pageCount() >= 2
    tl = d.firstBlock().layout()
    blaetter = {int(tl.lineAt(i).y() // (mm_to_px(297) + 16)) for i in range(tl.lineCount())}
    assert len(blaetter) >= 2                                                                    # Zeilen auf mehreren Blättern


def test_ungleiche_spalten(app):
    d = _doc(1, 1500)
    basis = _basis(spalten=2, spalten_raster_mm=[[100.0, 40.0], [30.0, 0.0]])                    # Textbreite 170 mm
    lay = _lauf(d, basis)
    tl = d.firstBlock().layout()
    xs = sorted({round(tl.lineAt(i).x()) for i in range(tl.lineCount())})
    assert len(xs) == 2 and xs[1] - xs[0] == round(mm_to_px(140))                                # zweite Spalte 140 mm rechts der ersten
    breiten = {round(tl.lineAt(i).width()) for i in range(tl.lineCount())}
    assert round(mm_to_px(100)) in breiten and round(mm_to_px(30)) in breiten


def test_hit_test_findet_zeile_und_zeichen(app):
    d = _doc(3, 30)
    lay = _lauf(d, _basis())
    r = lay.blockBoundingRect(d.findBlockByNumber(1))
    pos = lay.hitTest(QPointF(r.x() + 5, r.y() + 3), 0)
    assert d.findBlock(pos).blockNumber() == 1 and pos - d.findBlockByNumber(1).position() <= 3


def test_zoom_skaliert_blatt_und_raender(app):
    d = _doc(3, 20)
    lay = Seitenlauf(d, _basis(), zoom=2.0)
    d.setDocumentLayout(lay)
    lay.anordnen()
    r = lay.blockBoundingRect(d.firstBlock())
    assert r.x() == pytest.approx(mm_to_px(20) * 2, abs=1.5) and lay.erg.blaetter[0].breite == pytest.approx(mm_to_px(210) * 2)
    lay.zoom_setzen(1.0)
    assert lay.blockBoundingRect(d.firstBlock()).x() == pytest.approx(mm_to_px(20), abs=1.5)


def test_bild_in_der_zeile_nimmt_hoehe_ein_und_wird_gezeichnet(app):
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QColor, QImage, QPainter, QTextImageFormat
    d = _doc(1, 3)
    bild = QImage(40, 120, QImage.Format_RGB32)
    bild.fill(QColor("red"))
    d.addResource(QTextDocument.ImageResource, QUrl("b"), bild)
    f = QTextImageFormat(); f.setName("b"); f.setWidth(40); f.setHeight(120)
    QTextCursor(d).insertImage(f)
    lay = _lauf(d, _basis())
    assert lay.blockBoundingRect(d.firstBlock()).height() >= 120
    ziel = QImage(900, 1200, QImage.Format_RGB32)
    ziel.fill(QColor("white"))
    p = QPainter(ziel)
    from PySide6.QtGui import QAbstractTextDocumentLayout
    lay.draw(p, QAbstractTextDocumentLayout.PaintContext())
    p.end()
    rot = sum(1 for x in range(0, 900, 3) for y in range(0, 400, 3) if ziel.pixelColor(x, y).red() > 200 and ziel.pixelColor(x, y).green() < 60)
    assert rot > 100                                                                              # das Bild steht im Text


def test_editor_mit_seitenlauf_klick_cursor_und_blaetter(app):
    """Der Editor zeigt ein Dokument mit Abschnitten über den Seitenlauf: Blätter mit eigenen Rändern, Klick und Cursor in Blattkoordinaten."""
    from PySide6.QtCore import QPoint
    from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
    ed = DocumentEditor()
    ed.setPlainText("\n".join(f"Absatz {i} " + "Text " * 50 for i in range(6)))
    doc = ed.document()
    c = QTextCursor(doc); c.setPosition(doc.findBlockByNumber(2).position() + 5)
    AB.einfuegen(doc, c, "naechste", ed.page)
    ps = AB.einrichtung(doc, ed.page, 1); ps.margin_left_mm = 50.0
    AB.setzen(doc, 1, ps, "naechste")
    assert ed.lauf_einschalten() and ed.lauf_aktiv()
    ed.resize(ed.width(), 1500)
    assert ed._blatt_anzahl() == 2 and ed._blatt(1)["ml"] == pytest.approx(mm_to_px(50) * ed.zoom, abs=1)
    zweites = doc.findBlock(AB.beginn(doc, 1))
    r = ed.cursorRect(QTextCursor(zweites))
    assert r.y() >= ed.blatt_oben(1) and r.x() >= mm_to_px(50) * ed.zoom - 2                    # liegt auf dem zweiten Blatt am eigenen linken Rand
    gefunden = ed.cursorForPosition(QPoint(r.x() + 3, r.y() + 3))
    assert doc.findBlock(gefunden.position()).blockNumber() == zweites.blockNumber()
    ed.set_zoom(2.0)
    assert ed._blatt(1)["W"] == pytest.approx(mm_to_px(210) * 2.0)


def test_fortlaufender_abschnitt_mit_anderen_raendern_und_spalten_bleibt_auf_dem_blatt(app):
    d = _doc(4, 12)
    basis = _basis()
    _abschnitt(d, 1, basis, typ="fortlaufend", margin_left_mm=40.0, spalten=2, spalten_abstand_mm=10.0)
    lay = _lauf(d, basis)
    assert lay.pageCount() == 1
    erster = d.findBlock(AB.beginn(d, 1))
    r = lay.blockBoundingRect(erster)
    assert r.x() == pytest.approx(mm_to_px(40), abs=1)                              # eigener linker Rand
    vorher = lay.blockBoundingRect(d.firstBlock())
    assert r.y() > vorher.y()                                                       # weiter unten auf demselben Blatt, nicht oben


# ---- Tabellen im Seitenlauf ---------------------------------------------------------------------------------------------------
def _tabellen_doc(zeilen=2, spalten=2, text="Zelle"):
    from PySide6.QtGui import QTextTableFormat, QTextLength, QColor, QBrush, QTextFrameFormat
    d = QTextDocument()
    d.setDefaultFont(QFont("Liberation Sans", 11))
    c = QTextCursor(d)
    c.insertText("Vor der Tabelle")
    c.insertBlock()
    tf = QTextTableFormat()
    tf.setBorder(1); tf.setBorderBrush(QBrush(QColor("black"))); tf.setBorderStyle(QTextFrameFormat.BorderStyle_Solid)
    tf.setCellPadding(4); tf.setCellSpacing(0)
    tf.setWidth(QTextLength(QTextLength.PercentageLength, 100))
    t = c.insertTable(zeilen, spalten, tf)
    for r in range(zeilen):
        for k in range(spalten):
            t.cellAt(r, k).firstCursorPosition().insertText(f"{text} {r}{k}")
    c.movePosition(QTextCursor.End)
    c.insertBlock()
    c.insertText("Nach der Tabelle")
    return d, t


def test_tabelle_wird_gesetzt_zellen_nebeneinander_untereinander(app):
    d, t = _tabellen_doc(2, 2)
    assert unterstuetzt(d)
    lay = _lauf(d, _basis())
    z00, z01, z10 = (lay.blockBoundingRect(t.cellAt(r, k).firstCursorPosition().block()) for r, k in ((0, 0), (0, 1), (1, 0)))
    assert z01.x() > z00.x() + 50 and abs(z01.y() - z00.y()) < 2                                   # nebeneinander
    assert z10.y() > z00.y() + 10 and abs(z10.x() - z00.x()) < 2                                   # untereinander
    vor = lay.blockBoundingRect(d.firstBlock())
    nach = lay.blockBoundingRect(d.lastBlock())
    assert z00.y() > vor.bottom() and nach.y() > z10.bottom()                                      # Text davor, Tabelle, Text danach
    assert len(lay.erg.zellen) == 4 and lay.frameBoundingRect(t).width() == pytest.approx(mm_to_px(170), abs=2)


def test_tabelle_rahmen_und_fuellung_werden_gezeichnet(app):
    from PySide6.QtGui import QAbstractTextDocumentLayout, QBrush, QColor, QImage, QPainter, QTextTableCellFormat
    d, t = _tabellen_doc(1, 2)
    cf = QTextTableCellFormat(); cf.setBackground(QBrush(QColor("#ff0000")))
    t.cellAt(0, 0).setFormat(cf)
    lay = _lauf(d, _basis())
    ziel = QImage(900, 400, QImage.Format_RGB32); ziel.fill(QColor("white"))
    p = QPainter(ziel); lay.draw(p, QAbstractTextDocumentLayout.PaintContext()); p.end()
    r = lay.erg.zellen[0].rechteck
    assert ziel.pixelColor(int(r.x) + 4, int(r.bottom) - 3).red() > 200 and ziel.pixelColor(int(r.x) + 4, int(r.bottom) - 3).green() < 60   # rote Füllung
    assert ziel.pixelColor(int(r.x), int(r.y + r.height / 2)).red() < 100                                                                    # schwarzer Rand links


def test_tabellenzeilen_laufen_auf_das_naechste_blatt(app):
    d, t = _tabellen_doc(60, 1)
    lay = _lauf(d, _basis())
    assert lay.pageCount() >= 2
    erste = lay.blockBoundingRect(t.cellAt(0, 0).firstCursorPosition().block())
    letzte = lay.blockBoundingRect(t.cellAt(59, 0).firstCursorPosition().block())
    assert letzte.y() > lay.erg.blaetter[1].oben and erste.y() < lay.erg.blaetter[1].oben          # Zeile 59 steht auf Blatt 2, Zeile 0 auf Blatt 1


def test_verbundene_zellen_und_verschachtelte_tabelle(app):
    d, t = _tabellen_doc(2, 2)
    t.mergeCells(0, 0, 1, 2)                                                                         # erste Zeile über beide Spalten
    inner = t.cellAt(1, 1).firstCursorPosition().insertTable(1, 2)
    inner.cellAt(0, 0).firstCursorPosition().insertText("innen")
    lay = _lauf(d, _basis())
    breit = lay.blockBoundingRect(t.cellAt(0, 0).firstCursorPosition().block())
    assert t.cellAt(0, 0).columnSpan() == 2
    assert len(lay.erg.zellen) >= 3 + 2                                                              # drei äußere Zellen und zwei innere
    i = lay.blockBoundingRect(inner.cellAt(0, 0).firstCursorPosition().block())
    z11 = lay.erg.zellen[[z.rechteck for z in lay.erg.zellen].index(max((z.rechteck for z in lay.erg.zellen if z.rechteck.height > 5), key=lambda r: r.x))]
    assert i.x() > lay.blockBoundingRect(t.cellAt(1, 0).firstCursorPosition().block()).x() + 50    # steht in der rechten Zelle der zweiten Zeile
    assert breit.y() < i.y()


def test_schwebendes_bild_text_laeuft_darum_herum(app):
    """Ein schwebendes Bild links (Rahmen mit Bild, wie ``umbruch.schwebend_einfuegen``): die Zeilen daneben sind eingerückt, darunter wieder volle Breite."""
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QColor, QImage, QTextImageFormat
    from lunivo_writer.editor.seite import umbruch
    d = QTextDocument()
    d.setDefaultFont(QFont("Liberation Sans", 11))
    d.setPlainText("Text " * 400)
    bild = QImage(150, 100, QImage.Format_RGB32); bild.fill(QColor("blue"))
    d.addResource(QTextDocument.ImageResource, QUrl("sb"), bild)
    f = QTextImageFormat(); f.setName("sb"); f.setWidth(150); f.setHeight(100)
    umbruch.schwebend_einfuegen(d, 0, f, "links")
    assert unterstuetzt(d)
    lay = _lauf(d, _basis())
    text = d.lastBlock()
    tl = text.layout()
    xs = [round(tl.lineAt(i).x() + tl.position().x()) for i in range(tl.lineCount())]
    assert xs[0] > mm_to_px(20) + 140                                                              # erste Zeilen neben dem Bild
    assert xs[-1] == round(mm_to_px(20))                                                           # weiter unten wieder am Rand
    assert lay.erg.ausschluesse and lay.erg.ausschluesse[0][3] == "links"


def test_zelle_mitte_und_unten_ausgerichtet(app):
    from PySide6.QtGui import QTextCharFormat
    d, t = _tabellen_doc(1, 3)
    t.cellAt(0, 0).firstCursorPosition().insertText("\nzwei\ndrei\nvier")                      # hohe Zelle bestimmt die Zeilenhöhe
    for k, va in ((1, QTextCharFormat.AlignMiddle), (2, QTextCharFormat.AlignBottom)):
        z = t.cellAt(0, k)
        f = z.format().toTableCellFormat(); f.setVerticalAlignment(va); z.setFormat(f)
    lay = _lauf(d, _basis())
    y = [lay.blockBoundingRect(t.cellAt(0, k).firstCursorPosition().block()).y() for k in range(3)]
    assert y[0] < y[1] < y[2]


def test_pdf_und_seitenzahl_folgen_dem_seitenlauf_bei_fortlaufendem_abschnitt(app, tmp_path):
    from lunivo_writer.editor.seite import seiten_aufteilung as SA
    d = _doc(4, 12)
    basis = _basis()
    _abschnitt(d, 1, basis, typ="fortlaufend", margin_left_mm=40.0, spalten=2, spalten_abstand_mm=10.0)
    assert SA.seitenzahl(d, basis) == 1                                             # ein Blatt, nicht je Abschnitt eines
    pdf = tmp_path / "a.pdf"
    assert SA.export_pdf(str(pdf), d, basis) == 1
    assert pdf.read_bytes().count(b"/Type /Page\n") + pdf.read_bytes().count(b"/Type /Page ") >= 1
    bilder = list(SA.seiten_bilder(d, basis, faktor=0.3))
    assert len(bilder) == 1 and not bilder[0][1].isNull()


def test_tabellenkopfzeile_wird_auf_dem_naechsten_blatt_wiederholt(app):
    d, t = _tabellen_doc(80, 2)
    f = t.format(); f.setHeaderRowCount(1); t.setFormat(f)
    lay = _lauf(d, _basis())
    assert lay.pageCount() >= 2 and len(lay.erg.kopien) >= 2                                       # zwei Kopfzellen je Folgeblatt
    zelle, blocke = lay.erg.kopien[0]
    nr, dx, dy = blocke[0]
    orig = lay.blockBoundingRect(d.findBlockByNumber(nr))
    assert dy > 100 and zelle.rechteck.top == pytest.approx(lay.erg.zellen[0].rechteck.top + dy, abs=1)
    zweites_blatt_zeile = [z for z in lay.erg.zellen if z.rechteck.top > zelle.rechteck.bottom - 1 and z.rechteck.top < zelle.rechteck.bottom + 5]
    assert zweites_blatt_zeile                                                                      # die erste Datenzeile folgt unter der Kopie


def _ausgabe(d, basis, tmp_path, **opt):
    from PySide6.QtGui import QPdfWriter
    from lunivo_writer.editor.seite import seiten_aufteilung as SA
    w = QPdfWriter(str(tmp_path / "o.pdf"))
    n = SA.render_dokument(d, basis, w, opt=opt)
    return n, opt


def test_blattweg_fussnote_unten_lesezeichen_und_verweise(app, tmp_path):
    from PySide6.QtGui import QTextBlockFormat, QTextCharFormat
    from lunivo_writer.editor.dokument.zusatz import P_NOTE
    d = _doc(3, 10)
    c = QTextCursor(d)
    c.movePosition(QTextCursor.Start)
    bf = QTextBlockFormat(); bf.setHeadingLevel(1)
    c.setBlockFormat(bf)
    c.movePosition(QTextCursor.EndOfBlock)
    f = QTextCharFormat(); f.setProperty(P_NOTE, "f:1")
    c.insertText("1", f)
    n, opt = _ausgabe(d, _basis(), tmp_path, noten={"f": {1: "Text der Fußnote"}}, lesezeichen={"ueberschriften": True}, notenlinks=True)
    assert n >= 1
    assert opt["lesezeichen_ergebnis"] and opt["lesezeichen_ergebnis"][0][2] == 0
    assert opt["notenlinks_ergebnis"] and {k["seite"] for k in opt["notenlinks_ergebnis"]} == {0}      # Marke und Fußnote auf Blatt 1
    from lunivo_writer.editor.seite import seiten_aufteilung as SA
    kopie, blaetter, _f = SA._gesetzt(d, _basis(), {"noten": {"f": {1: "Text der Fußnote"}}})
    info = kopie.documentLayout().erg.fussnoten[0]
    bl = blaetter[0]
    assert info["hoehe"] > 10 and info["noten"][0][0] < bl.text_hoehe                                    # unten auf dem Blatt
    letzte = max(r.bottom for k, r in kopie.documentLayout().erg.rechtecke.items() if kopie.documentLayout().erg.block_blatt[k] == 0)
    assert letzte <= bl.oben + bl.text_oben + bl.text_hoehe - info["hoehe"] + 1                         # der Text endet über den Fußnoten


def test_blattweg_leerseite_nummern_und_auswahl(app, tmp_path):
    d = _doc(2, 6)
    basis = _basis()
    _abschnitt(d, 1, basis, typ="ungerade")                                                            # Abschnitt 2 auf einer ungeraden Seite
    lay = _lauf(d, basis)
    assert [b.leer for b in lay.erg.blaetter] == [False, True, False]                                  # Blatt 2 bleibt leer, Abschnitt 2 steht auf Blatt 3
    assert lay.seitennummern() == [1, 2, 3]
    n, opt = _ausgabe(d, basis, tmp_path)
    assert n == 3
    n2, opt2 = _ausgabe(d, basis, tmp_path, nur_seiten={1, 3})
    assert opt2["_gedruckt"] == 2


@pytest.mark.parametrize("nr", [0, 40, 119])
def test_setzen_ab_geaendertem_absatz_gleicht_dem_vollen_setzen(app, nr):
    d = _doc(120, 25)
    lay = _lauf(d, _basis())
    c = QTextCursor(d.findBlockByNumber(nr))
    c.movePosition(QTextCursor.EndOfBlock)
    c.insertText(" Wort" * 140)                                                  # der Absatz wird länger: spätere Absätze rücken auf andere Blätter
    c.insertText("!")
    neu = QTextDocument(); neu.setDefaultFont(d.defaultFont()); neu.setPlainText(d.toPlainText())
    voll = _lauf(neu, _basis())
    assert len(lay.blaetter) == len(voll.blaetter) and lay.erg.block_blatt == voll.erg.block_blatt
    for k in (0, 1, nr, 119):
        a, b = lay.blockBoundingRect(d.findBlockByNumber(k)), voll.blockBoundingRect(neu.findBlockByNumber(k))
        assert (round(a.x(), 1), round(a.y(), 1), round(a.height(), 1)) == (round(b.x(), 1), round(b.y(), 1), round(b.height(), 1))
    c = QTextCursor(d.findBlockByNumber(nr)); c.select(QTextCursor.LineUnderCursor)
    c.insertText("kurz")                                                          # wieder kürzer
    neu2 = QTextDocument(); neu2.setDefaultFont(d.defaultFont()); neu2.setPlainText(d.toPlainText())
    assert lay.erg.block_blatt == _lauf(neu2, _basis()).erg.block_blatt


def test_seitennummern_beginnen_neu_im_abschnitt(app):
    d = _doc(2, 60)
    basis = _basis()
    _abschnitt(d, 1, basis, typ="naechste", seiten_start=10)
    lay = _lauf(d, basis)
    nummern = lay.seitennummern()
    erster = lay.erg.bereich_start[1]
    assert nummern[erster] == 10 and nummern[0] == 1


def _regel_doc(k, optionen, naechster_zeilen=3, auf="kopf"):
    """k einzeilige Füllabsätze, dann ein Absatz („kopf“) und ein Folgeabsatz („text“) mit mehreren Zeilen; ``optionen`` gelten für den gewählten."""
    from lunivo_writer.editor.seite import absatzopt

    def format_mit(opt):
        bf = QTextBlockFormat(); w = absatzopt.lesen(bf); w.update(opt); absatzopt.setzen(bf, w)
        return bf
    d = QTextDocument(); d.setDefaultFont(QFont("Liberation Sans", 11))
    c = QTextCursor(d)
    for i in range(k):
        c.insertText(f"Fülle {i}"); c.insertBlock()
    c.setBlockFormat(format_mit(optionen if auf == "kopf" else {}))
    c.insertText("Überschrift")
    c.insertBlock(format_mit(optionen if auf == "text" else {}))
    c.insertText("Folgetext " * (14 * naechster_zeilen))
    return d


def _stellen_ohne_regel(**kw):
    for k in range(30, 80):
        lay = _lauf(_regel_doc(k, {"kontrolle": False}, **kw), _basis())
        if lay.erg.block_blatt[k] == 0 and lay.erg.anfang[k + 1][0] == 0 and lay.erg.block_blatt[k + 1] == 0 and lay.blockBoundingRect(d_letzter(lay)).bottom() > 0:
            ende = lay.erg.rechtecke[k + 1]
            if ende.bottom() > lay.erg.blaetter[1].oben:                       # der Folgeabsatz läuft auf das zweite Blatt
                return k
    return None


def d_letzter(lay):
    return lay.document().lastBlock()


def test_nicht_vom_naechsten_trennen_zieht_die_ueberschrift_mit(app):
    for k in range(30, 80):
        ohne = _lauf(_regel_doc(k, {"kontrolle": False}), _basis())
        mit = _lauf(_regel_doc(k, {"kontrolle": False, "nicht_trennen": True}), _basis())
        if ohne.erg.block_blatt[k] == 0 and ohne.erg.anfang[k + 1][0] == 1:                 # Überschrift ganz unten, Folgetext erst auf dem nächsten Blatt
            assert mit.erg.block_blatt[k] == 1 and mit.erg.block_blatt[k + 1] == 1
            return
    pytest.fail("keine Stelle gefunden")


@pytest.mark.parametrize("opt", [{"zusammen": True, "kontrolle": False}, {"kontrolle": True}])
def test_zusammenhalten_und_absatzkontrolle(app, opt):
    for k in range(30, 80):
        ohne = _lauf(_regel_doc(k, {"kontrolle": False}, 2, "text"), _basis())
        mit = _lauf(_regel_doc(k, opt, 2, "text"), _basis())
        if len(ohne.blaetter) < 2:
            continue
        zeilen = ohne.document().findBlockByNumber(k + 1).layout().lineCount()
        r = ohne.erg.rechtecke[k + 1]
        if ohne.erg.anfang[k + 1][0] == 0 and r.bottom > ohne.erg.blaetter[1].oben and zeilen >= 2:    # ohne Regel über zwei Blätter geteilt
            tl = ohne.document().findBlockByNumber(k + 1).layout()
            auf0 = sum(1 for i in range(tl.lineCount()) if ohne.blatt_bei_y(tl.position().y() + tl.lineAt(i).y() + 1) == 0)
            if opt.get("zusammen") or auf0 < 2 or zeilen - auf0 < 2:                          # Regel greift: ganz auf Blatt 2, oder 2 Zeilen auf jedem
                assert mit.erg.anfang[k + 1][0] == 1 or _zeilen_je_blatt(mit, k + 1)[0] >= 2
                return
    pytest.fail("keine Stelle gefunden")


def _zeilen_je_blatt(lay, nr):
    tl = lay.document().findBlockByNumber(nr).layout()
    je = [0, 0]
    for i in range(tl.lineCount()):
        je[min(1, lay.blatt_bei_y(tl.position().y() + tl.lineAt(i).y() + 1))] += 1
    return je
