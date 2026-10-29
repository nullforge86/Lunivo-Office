"""Reiter Einfügen nach Kays WPS-Vorlagen (Ordner einfuegen/): Klappmenüs, Zahl, Felder, Text ↔ Tabelle, Leere Seite quer."""
from __future__ import annotations

import pytest
from PySide6.QtGui import QTextCursor


@pytest.fixture
def fenster(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document()
    yield w
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def _texte(m):
    return [a.text().replace("&", "") for a in m.actions() if a.text()]


def test_klappmenues_wie_vorlage(fenster):
    b = fenster.befehle
    assert _texte(b.klappe("leereSeiteKlappe")) == ["Vertikal", "Horizontal"]
    assert _texte(b.klappe("umbruecheKlappe")) == [
        "Seitenumbruch(P)\tStrg+Enter", "Spaltenumbruch", "Textflussumbruch(W)\tUmschalt+Enter",
        "Abschnittsumbruch von nächster Seite", "Fortlaufenden Abschnittsumbruch", "Abschnittsumbruch von gerader Seite",
        "Abschnittsumbruch von ungerader Seite"]
    assert _texte(b.klappe("bildKlappe")) == ["Bild aus Datei einfügen …", "Bildschirmfoto …", "Piktogramm …"]
    tf = b.klappe("textfeldKlappe")
    assert _texte(tf) == ["Horizontal", "Vertikal", "Mehrzeiliger Text"]
    assert all(a.isEnabled() for a in tf.actions() if a.text())          # wie in WPS: alle drei wählbar
    assert _texte(b.klappe("schnellbausteineKlappe")) == ["AutoText-Liste", "Felder …"]
    assert b.hat("textflussumbruch")                        # auch im Seitenlayout-Menü nicht mehr grau


def test_textfeld_vertikal_ist_form_mit_text(fenster):
    from lunivo_writer.editor import formen as F
    ed = fenster.current_editor()
    fenster.befehle.textfeldVertikal()
    b = ed.document().firstBlock()
    it = b.begin()
    f = None
    while not it.atEnd():
        cf = it.fragment().charFormat()
        if cf.isImageFormat():
            f = cf.toImageFormat()
        it += 1
    o = F.objekt(f)
    assert o["art"] == "form" and o["daten"]["form"] == "Textfeld vertikal" and o["daten"]["text"] == "Text hier eingeben"
    assert f.height() > f.width()                                          # hochkant wie in der Vorlage


def test_band_einfuegen_reihenfolge(fenster):
    from lunivo_writer.ui.ribbon.plan import plan
    from lunivo_writer.ui.ribbon.ribbon_bar import lade_register
    tab = next(t for t in plan(lade_register()) if t["name"] == "Einfügen")
    namen = [e["name"] for g in tab["gruppen"] if g["name"] != "Weitere" for e in g["knoepfe"]]
    for a, z in (("Deckblatt", "Leere Seite"), ("Leere Seite", "Umbrüche"), ("Umbrüche", "Tabelle"), ("Tabelle", "Bild"),
                 ("Textfeld", "WordArt"), ("Symbol", "Gleichung"), ("Gleichung", "Zahl"), ("Zahl", "Hyperlink")):
        assert namen.index(a) < namen.index(z)
    assert all(g["name"] != "Weitere" for g in tab["gruppen"])     # nicht länger als die WPS-Vorlage (Kay, 2026-10-28)
    # nichts geht verloren: was WPS nicht im Band hat, steht in den Klappen
    assert "Text aus Datei …" in _texte(fenster.befehle.klappe("objektKlappe"))


def test_symbol_zuletzt_verwendet(fenster):
    b = fenster.befehle
    e = fenster.current_editor()
    m = b.klappe("symbolKlappe")
    assert m.knoepfe["zuletzt0"].isHidden() and "kg" in m.knoepfe
    m.gewaehlt.emit("§")
    assert e.toPlainText().endswith("§")
    m.aboutToShow.emit()
    assert not m.knoepfe["zuletzt0"].isHidden() and m.knoepfe["zuletzt0"].toolTip() == "„§“ einfügen"
    m.gewaehlt.emit("zuletzt0")
    assert e.toPlainText().endswith("§§")


def test_symbol_fenster_einfuegen_und_benutzerdefiniert(fenster):
    """Fenster „Symbol“: Einfügen setzt das Zeichen und merkt es; die benutzerdefinierte Liste (gleiche Daten wie die Klappe) lässt sich
    verschieben, abhaken, entfernen und zurücksetzen."""
    from PySide6.QtCore import Qt
    from lunivo_writer.ui.dialogs.sonderzeichen import SonderzeichenDialog
    b = fenster.befehle
    e = fenster.current_editor()
    d = SonderzeichenDialog(None, e.insertPlainText, b._symbol_daten())
    d.zeichencode.setText("167"); d._code_getippt("167")                     # Reiter Symbole: Zeichencode 167 = §
    d.ok.click()
    assert e.toPlainText().endswith("§") and b._symbole_zuletzt()[0] == "§"
    d.reiter.setCurrentIndex(1); d.sonder.setCurrentItem(d.sonder.topLevelItem(0)); d.ok.click()   # Reiter Sonderzeichen: Geviertstrich
    assert e.toPlainText().endswith("—") and d.abbrechen.text() == "Abbrechen"
    d.reiter.setCurrentIndex(2)
    assert d.abbrechen.text() == "Schließen" and not d.bei_benutzer.isEnabled()
    erste = [z for z, _ in b._symbol_daten().benutzer()]
    assert d.liste.topLevelItemCount() == len(erste) and not d.hoch.isEnabled()
    d.liste.setCurrentItem(d.liste.topLevelItem(0)); d.runter.click()
    assert [z for z, _ in b._symbol_daten().benutzer()][:2] == [erste[1], erste[0]]
    d.liste.topLevelItem(0).setCheckState(0, Qt.Unchecked)
    assert erste[1] not in b._symbol_daten().sichtbar() and erste[1] not in b.klappe("symbolKlappe").knoepfe
    d.liste.setCurrentItem(d.liste.topLevelItem(1)); d.entfernen.click()
    assert erste[0] not in [z for z, _ in b._symbol_daten().benutzer()]
    d.reiter.setCurrentIndex(0); d.zeichencode.setText("A"); d.von.setCurrentIndex(1); d._code_getippt("21"); d.bei_benutzer.click()
    assert b._symbol_daten().benutzer()[-1] == ("!", True)
    d.reiter.setCurrentIndex(2); d.zurueck.click()
    assert [z for z, _ in b._symbol_daten().benutzer()] == list(b.BENUTZER_SYMBOLE)


def test_zahl_typen():
    from lunivo_writer.editor.zahlformat import zahl_text
    assert [zahl_text(14, "roemisch"), zahl_text(28, "gross"), zahl_text(3, "klein"), zahl_text(5, "kreis"), zahl_text(7, "null")] == \
        ["XIV", "AB", "c", "⑤", "07"]
    assert [zahl_text(n, "wort") for n in (1, 21, 101, 1000, 2026)] == ["eins", "einundzwanzig", "einhunderteins", "eintausend",
                                                                        "zweitausendsechsundzwanzig"]
    with pytest.raises(ValueError):
        zahl_text(0, "roemisch")


def test_zahl_fenster_prueft_eingabe(app):
    from lunivo_writer.ui.dialogs.einfuegen_fenster import ZahlDialog
    d = ZahlDialog()
    d.zahl.setText("abc"); d._pruefen()
    assert d.result() == 0 and d.hinweis.text()
    d.zahl.setText("12"); d.typ.setCurrentRow(3); d._pruefen()
    assert d.result() == 1 and d.ergebnis() == "XII"


def test_felder_einfuegen(fenster):
    from lunivo_writer.editor import felder as F
    from lunivo_writer.editor.zusatz import P_FELD
    from lunivo_writer.ui.dialogs.einfuegen_fenster import FelderDialog
    e = fenster.current_editor()
    d = FelderDialog(fenster, {"seite": 2, "seiten": 5})
    assert [d.liste.item(i).text() for i in range(d.liste.count())] == [
        "Formel", "Hyperlink", "Seite", "PageRef", "SectionPages", "Seq", "TC", "Uhrzeit", "PrintDate", "TOC", "NumPages",
        "Dokumentvariable", "Seriendruckfeld", "StyleRef"]
    # Formel wie in der Vorlage: „=“, Assistent mit Zahlenformat, Funktion, Tabellenbereich (grau außerhalb), Textmarke
    assert d.anweisung.text() == "=" and not d.ok.isEnabled() and not d._felder["bereich"].isEnabled()
    assert d.formatierung.isChecked()
    d.anweisung.setText("=")
    d._felder["funktion"].setCurrentText("SUM"); d._formel_einsetzen(d._felder["funktion"])
    assert d.anweisung.text() == "=SUM()"
    d.anweisung.setText("=SUM(2;3)*2"); d._felder["format"].setCurrentText("0,00")
    assert d.ok.isEnabled() and d.feld() == ('=SUM(2;3)*2 \\# "0,00" \\* MERGEFORMAT', "10,00")
    d.liste.setCurrentRow(2)                                            # Seite, römisch
    d._felder["art"].setCurrentIndex(1)
    assert d.feld() == ("PAGE \\* ROMAN \\* MERGEFORMAT", "II")
    d.formatierung.setChecked(False)
    F.feld_einfuegen(e, *d.feld()); e.insertPlainText(" danach")
    c = QTextCursor(e.document()); c.setPosition(1)
    assert c.charFormat().stringProperty(P_FELD) == "PAGE \\* ROMAN"
    c.movePosition(QTextCursor.End)
    assert not c.charFormat().hasProperty(P_FELD)


def test_formel_und_tabellenbereiche(fenster):
    from lunivo_writer.editor import felder as F
    assert F.formel("2+3*4", {}) == 14 and F.formel("ROUND(10/3;2)", {}) == 3.33 and F.formel("IF(1>2;5;7)", {}) == 7
    assert F.formel("AVERAGE(ABOVE)", {"bereiche": {"ABOVE": [2, 4]}}) == 3
    assert F.zahl_formatieren(1234.5, "#.##0,00") == "1.234,50" and F.zahl_formatieren(0.25, "0 %") == "25 %"
    with pytest.raises(ValueError):
        F.formel("2+", {})
    e = fenster.current_editor()
    e.insert_table(3, 1)
    t = e.textCursor().currentTable()
    t.cellAt(0, 0).firstCursorPosition().insertText("4")
    t.cellAt(1, 0).firstCursorPosition().insertText("1,5")
    e.setTextCursor(t.cellAt(2, 0).firstCursorPosition())
    k = F.kontext_sammeln(e)
    assert k["in_tabelle"] and k["bereiche"]["ABOVE"] == [4.0, 1.5]
    assert F.ergebnis("=SUM(ABOVE)", k) == "5,5"


def test_autotext_liste_wie_vorlage(fenster):
    from lunivo_writer.editor.zusatz import P_FELD
    from lunivo_writer.ui.dialogs.einfuegen_fenster import AutoTextDialog
    b, e = fenster.befehle, fenster.current_editor()
    m = b.klappe("schnellbausteineKlappe")
    assert _texte(m) == ["AutoText-Liste", "Felder …"]
    liste = m.actions()[0].menu(); liste.aboutToShow.emit()
    texte = _texte(liste)
    assert texte[:4] == ["- Seite -", "Seite X", "Gesamtmenge von Y Seite", "Seite X von Y"] and "AutoText hinzufügen …" in texte
    assert not next(a for a in liste.actions() if a.text() == "AutoText hinzufügen …").isEnabled()     # ohne Markierung grau
    next(a for a in liste.actions() if a.text() == "Seite X von Y").trigger()
    assert e.toPlainText() == "Seite 1 von 1"
    c = QTextCursor(e.document()); c.setPosition(7)
    assert c.charFormat().stringProperty(P_FELD) == "PAGE"
    d = AutoTextDialog(None, "Mit freundlichen Grüßen und so weiter")
    assert d.name() == "Mit freundlichen Grüßen und" and d.ok.isEnabled()


def test_text_in_tabelle_und_zurueck(fenster):
    from lunivo_writer.editor import tabelle_text as TT
    from lunivo_writer.ui.dialogs.einfuegen_fenster import TrennerDialog
    e = fenster.current_editor()
    e.setPlainText("vorher\na\tb\tc\nd\te\nnachher")
    c = e.textCursor(); d = e.document()
    c.setPosition(d.findBlockByNumber(1).position() + 1); c.setPosition(d.findBlockByNumber(2).position() + 1, QTextCursor.KeepAnchor)
    e.setTextCursor(c)
    dlg = TrennerDialog(fenster, zu_tabelle=True, texte=TT.markierte_absaetze(e))
    assert dlg.trenner() == "\t" and dlg.spalten() == 3 and dlg._zeilen.text() == "2"
    assert TT.text_zu_tabelle(e, dlg.trenner(), dlg.spalten())
    t = e.textCursor().currentTable()
    assert (t.rows(), t.columns()) == (2, 3)
    assert d.findBlock(t.firstPosition() - 2).text() == "vorher" and d.findBlock(t.lastPosition() + 1).text() == "nachher"
    assert TT.tabelle_zu_text(e, ";")
    assert e.toPlainText() == "vorher\na;b;c\nd;e;\nnachher"


def test_datei_objekt_wie_vorlage(fenster, tmp_path, monkeypatch):
    from lunivo_writer.ui.baukasten import speichern_fenster as SF
    datei = tmp_path / "notiz.txt"; datei.write_text("Aus der Datei", encoding="utf-8")
    gefragt = []
    monkeypatch.setattr(SF, "datei_waehlen", lambda p, titel, start, filt, mehrere=False: gefragt.append((titel, filt)) or [str(datei)])
    fenster.befehle.dateiObjekt()
    assert gefragt[0][0] == "Dateiobjekt einfügen" and "PDF (*.pdf)" in gefragt[0][1]
    assert "Aus der Datei" in fenster.current_editor().toPlainText()


def test_kommentar_knopf_und_seitenleiste_gleiche_daten(fenster):
    """Prüfkatalog: Kommentar aus dem Band (auch im leeren Dokument) erscheint in der Kommentar-Seitenleiste und umgekehrt."""
    b, e, nav = fenster.befehle, fenster.current_editor(), fenster.navigation
    e.clear()
    b.kommentar()
    assert not nav.isHidden() and not nav.neu_feld.isHidden()
    nav.neu_text.setPlainText("Erster Gedanke"); nav._neu_speichern()
    assert [k["text"] for k in e.kommentare.values()] == ["Erster Gedanke"] and len(nav._karten) == 1
    assert e.kommentar_bereiche()


def test_zeichenbereich_nimmt_formen_auf(fenster):
    import json
    from lunivo_writer.editor import formen as F
    from lunivo_writer.editor.zusatz import P_OBJEKT
    b, e = fenster.befehle, fenster.current_editor()
    m = b.menue_formenKlappe()
    assert any(x.text().replace("&", "") == "Neuer Zeichenbereich" for x in m.findChildren(__import__("PySide6.QtWidgets", fromlist=["QPushButton"]).QPushButton))
    b.zeichenbereich()
    assert F.in_zeichenbereich(e, "Rechteck") and F.in_zeichenbereich(e, "Ellipse")
    o = json.loads(e.bild_format().property(P_OBJEKT))
    assert o["art"] == "zeichenbereich" and [k["form"] for k in o["daten"]["kinder"]] == ["Rechteck", "Ellipse"]
    assert (e.bild_format().width(), e.bild_format().height()) == (o["daten"]["breite"], F.ZEICHENBEREICH[1])


def test_tabelle_in_text_fenster_wie_vorlage():
    from lunivo_writer.ui.dialogs.einfuegen_fenster import TrennerDialog
    from PySide6.QtWidgets import QRadioButton
    d = TrennerDialog(None, zu_tabelle=False)
    assert [r.text().replace("&", "") for r in d.findChildren(QRadioButton)] == ["Absätze", "Tabstopps", "Kommata", "Andere:"]
    assert d.trenner() == "\t" and d.geschachtelt.isChecked() and d.geschachtelt.isEnabled()


@pytest.mark.parametrize("geschachtelt", [True, False])
def test_tabelle_in_text_mit_innerer_tabelle(fenster, geschachtelt):
    from lunivo_writer.editor import tabelle_text as TT
    e = fenster.current_editor()
    e.insert_table(1, 2)
    e.insertPlainText("a")
    c = e.textCursor(); c.movePosition(QTextCursor.NextCell); e.setTextCursor(c)
    e.insert_table(1, 2); e.insertPlainText("x")
    c = e.textCursor(); c.movePosition(QTextCursor.NextCell); c.insertText("y")
    aussen = e.document().rootFrame().childFrames()[0]
    c.setPosition(aussen.firstPosition()); e.setTextCursor(c)
    assert TT.tabelle_zu_text(e, ";", geschachtelt)
    if geschachtelt:
        assert e.toPlainText().strip() == "a;x;y"
    else:
        tabellen = [f for f in e.document().rootFrame().childFrames()]
        assert e.document().findBlockByNumber(0).text() == "a;" and len(tabellen) == 1
        assert tabellen[0].rows() == 1 and tabellen[0].columns() == 2


def test_tabelle_einfuegen_fenster_und_stift(fenster):
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtGui import QTextLength
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    from lunivo_writer.ui.dialogs.dokument_dialoge import TableDialog
    from lunivo_writer.ui.document import tabelle_stift as TS
    d = TableDialog(None, (5, 2))
    assert (d.cols.value(), d.rows.value()) == (5, 2) and d.spaltenbreite_px() is None and not d.breite.isEnabled()
    d.fest.setChecked(True)
    assert d.breite.isEnabled() and d.spaltenbreite_px() > 0
    # Stift: Rechteck aufziehen → Tabelle mit Zeilen × Spalten nach Größe, feste Spaltenbreite
    assert TS.groesse(3 * TS.ZELLE_B, 6 * TS.ZELLE_H) == (6, 3)
    e = fenster.current_editor(); e.insertPlainText("x")
    e.set_zoom(1.0)
    stift = TS.TabellenStift(e)
    a = QPoint(40, 40); b = a + QPoint(2 * TS.ZELLE_B, 6 * TS.ZELLE_H)
    vp = e.viewport()                                   # die Maus geht an den Sichtbereich; der Stift fängt sie programmweit ab
    assert QApplication.overrideCursor() is not None                            # Stift-Mauszeiger überall sichtbar
    QTest.mousePress(vp, Qt.LeftButton, pos=a); QTest.mouseMove(vp, b); QTest.mouseRelease(vp, Qt.LeftButton, pos=b)
    assert QApplication.overrideCursor() is None                                # nach dem Zeichnen wieder normal
    t = e.textCursor().currentTable()
    assert t is not None and (t.rows(), t.columns()) == (6, 2)
    assert t.format().columnWidthConstraints()[0].type() == QTextLength.FixedLength


def _seitentext(e, n):
    """n Seiten Text, jede mit eigenem Seitenumbruch davor; die Schreibmarke steht mitten auf Seite 1."""
    from PySide6.QtGui import QTextBlockFormat
    for i in range(n):
        if i:
            e.insert_page_break()
        for j, t in enumerate(("Anfang", "Mitte", "Ende")):
            c = e.textCursor()
            if j:
                c.insertBlock(QTextBlockFormat())
            c.insertText(f"Seite {i + 1} {t}"); e.setTextCursor(c)
    c = e.textCursor(); c.setPosition(10); e.setTextCursor(c)


def test_leere_seite_kommt_als_ganzes_blatt_hinter_die_seite(fenster):
    """Kay: kein Blatt im Blatt — das neue Blatt steht hinter der Seite, der Text wird nicht geteilt."""
    from PySide6.QtGui import QTextFormat
    from PySide6.QtWidgets import QApplication
    e = fenster.current_editor(); _seitentext(e, 2)
    texte = [e.document().findBlockByNumber(i).text() for i in range(e.document().blockCount())]
    fenster.befehle.leereSeite(None, None)
    QApplication.processEvents()
    nachher = [e.document().findBlockByNumber(i).text() for i in range(e.document().blockCount())]
    assert nachher == texte[:3] + [""] + texte[3:]                     # nichts geteilt, das leere Blatt nach „Seite 1 Ende“
    assert e.textCursor().block().text() == "" and e.textCursor().blockNumber() == 3
    assert e._blatt_anzahl() == 3
    assert e.document().findBlockByNumber(4).blockFormat().pageBreakPolicy() & QTextFormat.PageBreak_AlwaysBefore          # Seite 2 beginnt weiter auf eigenem Blatt


def test_enter_auf_neuem_blatt_macht_kein_weiteres_blatt(fenster):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    e = fenster.current_editor(); e.insertPlainText("x")
    fenster.befehle.leereSeite(None, None)
    for t in ("a", None, "b", None, "c"):
        QTest.keyClick(e, Qt.Key_Return) if t is None else QTest.keyClicks(e, t)
    assert e._blatt_anzahl() == 2
    assert [e.document().findBlockByNumber(i).text() for i in range(e.document().blockCount())] == ["x", "a", "b", "c"]


def test_leere_seite_horizontal_eigener_abschnitt(fenster):
    from lunivo_writer.editor import abschnitte as AB
    e = fenster.current_editor(); _seitentext(e, 2)
    fenster.befehle.leereSeite(None, True)
    n = AB.anzahl(e.document())
    assert [e.abschnitt_seite(i).landscape for i in range(n)] == [False, True, False]
    assert e.textCursor().block().text() == "" and e.abschnitt_seite().landscape
    assert e.document().findBlockByNumber(2).text() == "Seite 1 Ende"


def test_leere_seite_am_ende_ohne_extra_abschnitt(fenster):
    from lunivo_writer.editor import abschnitte as AB
    e = fenster.current_editor(); e.insertPlainText("x")
    fenster.befehle.leereSeite(None, True)
    assert [e.abschnitt_seite(i).landscape for i in range(AB.anzahl(e.document()))] == [False, True]
    assert [e.document().findBlockByNumber(i).text() for i in range(e.document().blockCount())] == ["x", ""]


def test_seitenzahl_vorgaben_und_entfernen(fenster):
    from lunivo_writer.editor import seitenzahl as SZ
    from lunivo_writer.models.page import HeaderFooter, PageSettings
    p = PageSettings(); p.header = HeaderFooter("Bericht", "left")
    SZ.seitenzahl_setzen(p, "kopf", "right", "Seite {PAGE} von {PAGES}")
    assert (p.header.text, p.header.align) == ("Bericht Seite {PAGE} von {PAGES}", "right")
    SZ.seitenzahl_setzen(p, "fuss", "center")
    assert p.footer.text == "{PAGE}" and p.header.text == "Bericht"          # nicht doppelt
    assert SZ.seitenzahlen_entfernen(p) and p.footer.text == "" and not SZ.seitenzahlen_entfernen(p)
    m = fenster.befehle.klappe("seitenzahlKlappe")
    assert len(m.knoepfe) == 10 and all(k.isEnabled() for k in m.knoepfe.values())        # außen/innen wie in WPS wählbar
    m.gewaehlt.emit("fuss_rechts")
    s = fenster.current_editor().abschnitt_seite()
    assert (s.footer.text, s.footer.align) == ("{PAGE}", "right")


def test_seitenzahl_zahlenart_aussen_kapitel():
    from lunivo_writer.editor import seitenzahl as SZ
    from lunivo_writer.models.page import PageSettings
    p = PageSettings(); p.seiten_format = "roem_gross"
    assert SZ.text("Seite {PAGE} von {PAGES}", 4, 9, p) == "Seite IV von 9"
    p.kapitel_ebene, p.kapitel_trenner, p.seiten_format = 1, ".", "dezimal"
    assert SZ.nummer(3, p, "2") == "2.3" and SZ.nummer(3, p, "") == "3"
    assert [SZ.ausrichtung("aussen", n) for n in (1, 2)] == ["right", "left"]
    assert [SZ.ausrichtung("innen", n) for n in (1, 2)] == ["left", "right"] and SZ.ausrichtung("center", 2) == "center"


def test_kapitel_je_seite(app):
    from PySide6.QtGui import QTextBlockFormat, QTextListFormat
    from lunivo_writer.editor import seitenzahl as SZ
    from lunivo_writer.ui.document.document_editor import DocumentEditor
    ed = DocumentEditor(); ed.setPlainText("Einleitung\nText\nMethode\nMehr")
    doc = ed.document()
    lf = QTextListFormat(); lf.setStyle(QTextListFormat.ListDecimal)
    liste = None
    for nr in (0, 2):
        c = QTextCursor(doc.findBlockByNumber(nr))
        bf = QTextBlockFormat(c.blockFormat()); bf.setHeadingLevel(1); c.setBlockFormat(bf)
        if liste is None:
            liste = c.createList(lf)
        else:
            liste.add(c.block())
    wechsel = [doc.findBlockByNumber(2).position(), doc.findBlockByNumber(3).position()]       # drei Seiten
    assert SZ.kapitel_je_seite(doc, 1, wechsel) == ["1", "2", "2"]


def test_seitenzahl_fenster_wie_vorlage(app):
    from lunivo_writer.models.page import PageSettings
    from lunivo_writer.ui.dialogs.einfuegen_fenster import SeitenzahlDialog
    d = SeitenzahlDialog(None, PageSettings())
    assert d.muster.count() == 9 and d.position.count() == 10 and d.position.currentText() == "Unten zentriert"
    assert [d.ebene.itemText(i) for i in (0, 8)] == ["Überschrift 1", "Überschrift 9"]
    assert not d.ebene.isEnabled() and not d.start.isEnabled() and d.fortsetzen.isChecked()       # grau wie in der Vorlage
    assert [b.text() for b in d.bereich.buttons()] == ["Gesamtes &Dokument", "Von aktueller Seite (&p)", "Aktueller Abschnit&t"]
    d.kapitel.setChecked(True); d.trenner.setCurrentIndex(1); d.beginnen.setChecked(True); d.start.setValue(5)
    d.muster.setCurrentIndex(5); d.position.setCurrentIndex(3)
    assert d.ebene.isEnabled() and d.beispiel.text() == "1.1, 1.A"
    assert d.werte() == {"ort": "kopf", "ausrichtung": "aussen", "muster": "{PAGE}", "format": "roem_gross", "start": 5,
                         "kapitel": (1, "."), "bereich": "dokument"}


def test_seitenzahl_von_aktueller_seite(fenster, monkeypatch):
    from lunivo_writer.editor import abschnitte as AB
    from lunivo_writer.ui.dialogs import einfuegen_fenster as EF
    ed = fenster.current_editor()
    ed.setPlainText("\n".join(f"Zeile {i}" for i in range(120)))
    ed._recount()
    assert ed.seitenwechsel
    c = ed.textCursor(); c.setPosition(ed.seitenwechsel[0] + 3); ed.setTextCursor(c)

    def exec_(self):
        self.bereich.button(1).setChecked(True); self.beginnen.setChecked(True); self.start.setValue(7)
        return 1
    monkeypatch.setattr(EF.SeitenzahlDialog, "exec", exec_)
    fenster.befehle.seitenzahlEinfuegen()
    doc = ed.document()
    assert AB.anzahl(doc) == 2 and AB.beginn(doc, 1) == ed.seitenwechsel[0]
    assert ed.abschnitt_seite(0).footer.is_empty() and ed.abschnitt_seite(1).footer.text == "{PAGE}"
    assert ed.abschnitt_seite(1).seiten_start == 7


def test_seitenzahl_ausgabe_und_docx(app, tmp_path, monkeypatch):
    from lunivo_writer.editor import pagination as PG
    from lunivo_writer.models.page import HeaderFooter, PageSettings
    from lunivo_writer.services.docx_reader import read_docx
    from lunivo_writer.services.docx_writer import write_docx
    from lunivo_writer.services.odt_reader import read_odt
    from lunivo_writer.services.odt_writer import odt_daten
    from lunivo_writer.ui.document.document_editor import DocumentEditor
    ed = DocumentEditor(); ed.setPlainText("\n".join(f"Zeile {i}" for i in range(120)))
    p = PageSettings(); p.footer = HeaderFooter("{PAGE}", "aussen"); p.seiten_format = "roem_klein"; p.seiten_start = 3
    gezeichnet = []
    echt = PG._draw_hf
    monkeypatch.setattr(PG, "_draw_hf", lambda pa, hf, r, n, t, b, page=None, kapitel="":
                        (gezeichnet.append((PG._expand(hf.text, n, t, page, kapitel), n)) if not hf.is_empty() else None, echt(pa, hf, r, n, t, b, page, kapitel)))
    PG.export_pdf(str(tmp_path / "a.pdf"), ed.document(), p)
    assert gezeichnet[:2] == [("iii", 3), ("iv", 4)]
    p.kapitel_ebene, p.kapitel_trenner = 2, ":"
    write_docx(str(tmp_path / "a.docx"), ed.document(), p)
    _d, q, _m, _r = read_docx(str(tmp_path / "a.docx"))
    assert (q.footer.align, q.seiten_format, q.seiten_start, q.kapitel_ebene, q.kapitel_trenner) == ("aussen", "roem_klein", 3, 2, ":")
    (tmp_path / "a.odt").write_bytes(odt_daten(ed.document(), p)[0])
    _d, q, _m, _r = read_odt(str(tmp_path / "a.odt"))
    assert (q.footer.align, q.seiten_format) == ("aussen", "roem_klein")


def test_wasserzeichen_galerie(fenster):
    import json
    m = fenster.befehle.klappe("wasserzeichenKlappe")
    assert {"VERTRAULICH", "EILT", "neu"} <= set(m.knoepfe) and m.knoepfe["eigen0"].isHidden()
    m.gewaehlt.emit("EILT")
    assert fenster.current_editor().abschnitt_seite().watermark["text"] == "EILT"
    fenster.settings.set(fenster.befehle.EIGENE_WASSERZEICHEN, json.dumps([{"text": "ENTWURF", "winkel": 0}]))
    m.aboutToShow.emit()
    assert not m.knoepfe["eigen0"].isHidden() and m.knoepfe["eigen0"].toolTip() == "ENTWURF"
    m.gewaehlt.emit("eigen0")
    assert fenster.current_editor().abschnitt_seite().watermark["text"] == "ENTWURF"


def test_wasserzeichen_fenster_wie_vorlage(app, tmp_path):
    from PySide6.QtGui import QColor, QImage
    from lunivo_writer.ui.dialogs.wasserzeichen_fenster import WasserzeichenDialog
    d = WasserzeichenDialog(None, None)
    assert not d.mit_bild.isChecked() and not d.mit_text.isChecked() and d.ergebnis() is None
    assert not d.zoom.isEnabled() and not d.inhalt.isEnabled() and not d.transparenz.isEnabled()      # grau wie in der Vorlage
    assert d.inhalt.itemText(1) == "NICHT KOPIEREN" and d.groesse.itemText(0) == "Automatisch" and d.transparenz.value() == 50
    assert [d.bereich_wahl.itemText(i) for i in range(2)] == ["Gesamtes Dokument", "Aktueller Abschnitt"]
    d.mit_text.setChecked(True); d.inhalt.setCurrentText("MUSTER"); d.text_format.setCurrentIndex(1); d.text_v.setCurrentIndex(1)
    assert d.inhalt.isEnabled() and d.text_v_mm.isEnabled() and not d.text_h_mm.isEnabled()
    w = d.ergebnis()
    assert (w["text"], w["winkel"], w["v"], w["groesse_pt"], w["transparenz"]) == ("MUSTER", -45, "oben", 0, 50)
    img = QImage(40, 20, QImage.Format_RGB32); img.fill(QColor("red")); img.save(str(tmp_path / "b.png"))
    d.mit_bild.setChecked(True)
    assert not d.mit_text.isChecked()                                                      # nur eine Art
    assert d.bild_laden(str(tmp_path / "b.png")) and d.bild_name.text() == "b.png"
    d.bereich_wahl.setCurrentIndex(1)
    w = d.ergebnis()
    assert w["bild"] and w["auswaschen"] and w["zoom"] == 0 and w["abschnitt"] and d.bereich() == "abschnitt"
    d2 = WasserzeichenDialog(None, w)                                                       # Vorbelegung
    assert d2.mit_bild.isChecked() and d2.bereich() == "abschnitt" and d2.ergebnis()["bild"] == w["bild"]


def test_wasserzeichen_zeichnen_und_abschnitt(fenster):
    from PySide6.QtCore import QRectF
    from PySide6.QtGui import QColor, QImage, QPainter
    from lunivo_writer.editor import abschnitte as AB
    from lunivo_writer.editor import wasserzeichen as WZ

    def bild(w):
        img = QImage(200, 280, QImage.Format_RGB32); img.fill(QColor("white"))
        p = QPainter(img); WZ.zeichnen(p, w, QRectF(0, 0, 200, 280)); p.end()
        return img
    rot = QImage(10, 10, QImage.Format_RGB32); rot.fill(QColor("red"))
    img = bild({"bild": WZ.bild_zu_text(rot), "auswaschen": False, "transparenz": 0})
    assert img.pixelColor(100, 140) == QColor("red")
    oben = bild({"text": "X", "winkel": 0, "v": "oben", "groesse_pt": 40, "farbe": "#000000", "transparenz": 0})
    assert any(oben.pixelColor(x, y) != QColor("white") for x in range(80, 120) for y in range(0, 50))
    assert all(oben.pixelColor(x, 240) == QColor("white") for x in range(200))
    ed = fenster.current_editor()
    ed.setPlainText("eins\nzwei")
    c = ed.textCursor(); c.setPosition(4); ed.setTextCursor(c); ed.abschnitt_einfuegen("naechste")
    b = fenster.befehle
    b._wasserzeichen_setzen({"text": "EILT"})
    c = ed.textCursor(); c.setPosition(ed.document().characterCount() - 1); ed.setTextCursor(c)
    b._wasserzeichen_setzen({"text": "MUSTER"}, "abschnitt")
    teile, _h = AB.teile(ed.document(), ed.page)
    assert [ps.watermark["text"] for _d, ps, _t in teile] == ["EILT", "MUSTER"]
    b._wasserzeichen_setzen(None)
    teile, _h = AB.teile(ed.document(), ed.page)
    assert [ps.watermark for _d, ps, _t in teile] == [None, None]


def test_gleichungen_formen_deckblatt(fenster):
    from lunivo_writer.editor import einfuegen as E
    from lunivo_writer.editor import formen_katalog as K
    b = fenster.befehle
    e = fenster.current_editor()
    assert len(b.klappe("gleichungKlappe").knoepfe) == len(E.GLEICHUNGEN)
    b.klappe("gleichungKlappe").gewaehlt.emit("4")                        # Satz des Pythagoras
    assert "a2 + b2 = c2" in e.toPlainText()
    for n in K.namen():                                                    # jede Form lässt sich zeichnen
        assert not E.form_bild(n, 60, 40).isNull()
    m = b.klappe("formenKlappe")
    assert set(K.namen()) <= set(m.knoepfe)
    vorher = e.document().characterCount()
    m.gewaehlt.emit("Fünfeck")
    assert e.document().characterCount() == vorher + 1
    assert len(b.klappe("wordartKlappe").knoepfe) == len(E.WORDART_VORGABEN)


def test_wordart_galerie_fuegt_sofort_ein(fenster):
    from lunivo_writer.editor import einfuegen as E, formen
    b = fenster.befehle
    e = fenster.current_editor()
    m = b.klappe("wordartKlappe")
    assert len(m.knoepfe) == 15 == len(E.WORDART_VORLAGEN)
    m.gewaehlt.emit("3")                                                   # Klick auf Stil 4: ohne Fenster, sofort im Dokument
    f = e.bild_format()
    o = formen.objekt(f)
    assert o["art"] == "wordart" and o["daten"] == {"text": "Hier Text einfügen", "vorlage": 3, "pt": 36}
    band = fenster.band
    assert band.reiter.isTabVisible(band.kontext_index["form"]) and not band.reiter.isTabVisible(band.kontext_index["bild"])


def test_diagramm_alle_arten_und_fenster(app):
    from lunivo_writer.editor import diagramm as D
    from lunivo_writer.ui.dialogs.einfuegen_dialoge import DiagrammDialog
    for _g, _s, unter in D.TYPEN:
        for u, _n in unter:
            img = D.bild(u, "T", D.BEISPIEL_KATEGORIEN, D.BEISPIEL_REIHEN, 200, 140)
            assert not img.isNull() and img.pixelColor(100, 70).name() != "#000000"
    d = DiagrammDialog(None)
    gruppen = [g for g, _s, _u in D.TYPEN]
    assert gruppen == ["Säule", "Linie", "Kreis", "Balken", "Fläche", "X Y (Punkt)", "Kurs", "Netz", "Kombination", "Vorlagen"]
    d.arten.setCurrentRow(1)                                               # Linie
    assert d.untertyp == "linie" and d.name.text() == "Linie" and len(d._knoepfe.buttons()) == 3
    assert d.daten()["kategorien"] == D.BEISPIEL_KATEGORIEN and d.kombi_teil.isHidden()
    d.arten.setCurrentRow(gruppen.index("Kurs"))
    assert d.untertyp == "kurs_hts" and len(d._knoepfe.buttons()) == 2
    # Kombination wie in der Vorlage: vier Untertypen und die Tabelle Datenreihen / Diagrammtyp / Sekundärachse
    d.arten.setCurrentRow(gruppen.index("Kombination"))
    assert len(d._knoepfe.buttons()) == 4 and not d.kombi_teil.isHidden() and len(d._kombi_felder) == 3
    assert d.kombi == [("saeule", False), ("saeule", False), ("linie", False)]
    _l, box, kasten = d._kombi_felder[2]
    kasten.setChecked(True)
    assert d.untertyp == "kombi_eigen" and d.daten()["kombi"][2] == ["linie", True]
    d.arten.setCurrentRow(gruppen.index("Vorlagen"))
    assert d.daten()["farben"] == D.VORLAGEN[d.untertyp][1] and not d.bild().isNull()


def test_datum_fenster_mit_feld(app):
    from lunivo_writer.ui.dialogs.einfuegen_dialoge import DatumDialog
    d = DatumDialog(None, "en_US")
    assert d.sprache.currentData() == "en_US" and "/" in d.ergebnis()
    assert d.feldanweisung() is None
    d.auto.setChecked(True)
    assert d.feldanweisung() == 'DATE \\@ "M/d/yyyy"'
    d.sprache.setCurrentIndex(0); d.liste.setCurrentRow(d.liste.count() - 3)          # HH:mm
    assert d.feldanweisung().startswith("TIME")


def test_hyperlink_fenster(app, tmp_path):
    from lunivo_writer.ui.dialogs.einfuegen_fenster import HyperlinkDialog
    H = HyperlinkDialog
    assert H.adresse_zu_href("www.beispiel.de") == "https://www.beispiel.de"
    assert H.adresse_zu_href("/tmp/a b.pdf") == "file:///tmp/a b.pdf"
    d = H(None, text="hier", ziele=[{"art": "Überschrift", "text": "Kapitel 1", "pos": 0, "block": 3}], ordner=str(tmp_path))
    assert not d.ok.isEnabled()
    d.adresse.setText("www.beispiel.de"); d.tipp = "Zur Seite"
    assert d.ok.isEnabled() and d.ergebnis() == {"art": "datei", "href": "https://www.beispiel.de", "text": "hier", "tipp": "Zur Seite"}
    d.art_waehlen(2); assert not d.ok.isEnabled()
    d.mail.setText("kay@example.org"); d.betreff.setText("Hallo Welt")
    r = d.ergebnis()
    assert r["href"].startswith("mailto:kay@example.org?subject=Hallo") and d.ok.isEnabled()
    d.art_waehlen(1)
    kapitel = d.stellen.topLevelItem(1).child(0)
    d.stellen.setCurrentItem(kapitel)
    assert d.ergebnis()["ziel"]["block"] == 3


def test_link_quickinfo_bleibt_im_docx(app, tmp_path):
    from PySide6.QtGui import QTextDocument
    from lunivo_writer.models.page import PageSettings
    from lunivo_writer.services.docx_reader import read_docx
    from lunivo_writer.services.docx_writer import write_docx
    from lunivo_writer.ui.document.document_editor import DocumentEditor
    e = DocumentEditor()
    e.insert_link("https://example.org", "Beispiel", "Mehr dazu")
    out = str(tmp_path / "l.docx")
    write_docx(out, e.document(), PageSettings(), {})
    qd, _p, _m, _r = read_docx(out)
    c = QTextCursor(qd); c.setPosition(3)
    assert c.charFormat().anchorHref() == "https://example.org" and c.charFormat().toolTip() == "Mehr dazu"
    assert isinstance(qd, QTextDocument)


def test_objekt_fenster(app, tmp_path):
    from lunivo_writer.ui.dialogs.einfuegen_fenster import ObjektDialog
    txt = tmp_path / "notiz.txt"; txt.write_text("Hallo")
    zip_ = tmp_path / "paket.zip"; zip_.write_bytes(b"PK")
    d = ObjektDialog(None)
    assert not d.neu.isEnabled() and not d.ok.isEnabled()
    d.datei.setText(str(txt)); assert d.art() == "text" and d.ok.isEnabled()
    d.datei.setText(str(zip_)); assert d.art() == "symbol"
    d.datei.setText(str(txt)); d.symbol.setChecked(True); assert d.art() == "symbol"


def test_objekt_und_hyperlink_befehle(fenster, tmp_path, monkeypatch):
    from lunivo_writer.editor import verweise
    from lunivo_writer.ui.dialogs import einfuegen_fenster as EF
    e = fenster.current_editor()
    zip_ = tmp_path / "paket.zip"; zip_.write_bytes(b"PK")

    def objekt_ok(self):
        self.datei.setText(str(zip_))
        return True
    monkeypatch.setattr(EF.ObjektDialog, "exec", objekt_ok)
    fenster.befehle.objekt(als_symbol=True)
    c = e.textCursor(); c.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
    assert c.charFormat().isImageFormat() and c.charFormat().anchorHref().endswith("paket.zip")
    e.insertPlainText("\nKapitel")
    def link_ok(self):
        self.art_waehlen(2); self.mail.setText("a@b.de")
        return True
    monkeypatch.setattr(EF.HyperlinkDialog, "exec", link_ok)
    fenster.befehle.hyperlink()
    assert "a@b.de" in e.toPlainText()
    assert "a@b.de" in fenster.settings.get("einfuegen/mail_zuletzt", "")
    assert verweise.lesezeichen_liste(e) == []


def test_deckblatt_wie_vorlage(fenster):
    """Einfügen ▸ Deckblatt wie die Vorlage: „Stil“ mit Hoch-/Querformat, 17 Gestaltungen; das Deckblatt ist ein eigener erster Abschnitt mit
    ganzseitiger Grafik, ersetzt ein vorhandenes und lässt sich entfernen; das Dokument danach behält Einrichtung und Text."""
    from PySide6.QtWidgets import QToolButton
    from lunivo_writer.editor import abschnitte as AB
    from lunivo_writer.editor import deckblatt as DB
    b, e = fenster.befehle, fenster.current_editor()
    e.setPlainText("Mein Text.")
    e.page.header.text = "Kopf {PAGE}"
    m = b.menue_deckblattKlappe()
    assert list(m.knoepfe) == DB.NAMEN and len(DB.NAMEN) == 17
    quer = [k for k in m.findChildren(QToolButton) if k.text() == "Querformat"][0]
    quer.click()
    assert m.quer and m.knoepfe["Segel"].iconSize().width() > m.knoepfe["Segel"].iconSize().height()
    m.gewaehlt.emit("Segel")                                               # Querformat-Deckblatt
    doc = e.document()
    assert e.page.landscape and e.page.watermark["ganzseitig"] and not e.page.header.text
    assert AB.anzahl(doc) == 2 and not AB.einrichtung(doc, e.page, 1).landscape
    assert AB.einrichtung(doc, e.page, 1).header.text == "Kopf {PAGE}"
    assert "LEBENSLAUF" in doc.toPlainText() and doc.findBlock(AB.beginn(doc, 1)).text() == "Mein Text."
    b.deckblattVorlage("Sonne")                                            # ersetzt das vorhandene
    assert AB.anzahl(doc) == 2 and "LEBENSLAUF" not in doc.toPlainText() and not e.page.landscape
    assert doc.toPlainText().count("Mein Text.") == 1
    assert DB.entfernen(e)
    assert doc.toPlainText().strip() == "Mein Text." and AB.anzahl(doc) == 1
    assert e.page.header.text == "Kopf {PAGE}" and e.page.watermark is None


def test_deckblatt_ausgabe_mit_grafik(fenster, tmp_path):
    """Im PDF steht die Grafik hinter dem Text, der Titel unten (Gestaltung „Sonne“), danach der Text auf Seite 2."""
    from PySide6.QtCore import QSizeF
    from PySide6.QtGui import QPageSize, QPdfWriter
    from lunivo_writer.editor import deckblatt as DB
    from lunivo_writer.editor.pagination import render_dokument
    e = fenster.current_editor()
    e.setPlainText("Mein Text.")
    DB.einfuegen(e, "Sonne")
    pw = QPdfWriter(str(tmp_path / "d.pdf")); pw.setResolution(96)
    pw.setPageSize(QPageSize(QSizeF(210, 297), QPageSize.Millimeter))
    assert render_dokument(e.document(), e.page, pw) == 2
    del pw
    lay = e.document().documentLayout()
    titel = e.document().firstBlock().next()
    assert titel.text() == "[Titel des Artikels]"
    assert lay.blockBoundingRect(titel).top() > e.page.content_height_px * 0.6     # unten auf dem Blatt wie in der Vorlage
    for n in DB.NAMEN:                                                     # jede Gestaltung lässt sich zeichnen, hoch und quer
        assert not DB.grafik_bild(n, 60, 85).isNull() and not DB.grafik_bild(n, 85, 60).isNull()


def test_umbrueche_wirken(fenster):
    """Alle sieben Einträge der Umbrüche-Klappe wirken im Dokument (WPS-Vorlage ``einfuegen/03-umbrueche.png``)."""
    from PySide6.QtGui import QTextFormat
    from lunivo_writer.editor import abschnitte as AB
    from lunivo_writer.editor.zusatz import B_SPALTE
    for i in range(7):
        fenster.new_document()
        ed = fenster.current_tab().editor
        ed.insertPlainText("Vorher")
        menue = fenster.befehle.klappe("umbruecheKlappe")              # Verweis halten, sonst räumt Python das Menü weg
        aktionen = [a for a in menue.actions() if a.text()]
        assert len(aktionen) == 7
        aktionen[i].trigger()
        doc = ed.document()
        if i < 2:                                                    # Seiten- und Spaltenumbruch
            b = doc.lastBlock()
            assert doc.blockCount() == 2
            assert b.blockFormat().pageBreakPolicy() & QTextFormat.PageBreak_AlwaysBefore
            assert bool(b.blockFormat().property(B_SPALTE)) == (i == 1)
        elif i == 2:                                                 # Textflussumbruch = Zeilenumbruch im Absatz
            assert doc.blockCount() == 1 and "\u2028" in doc.toRawText()
        else:
            assert [u[1] for u in AB.umbrueche(doc)] == [["naechste", "fortlaufend", "gerade", "ungerade"][i - 3]]
