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
    return [a.text() for a in m.actions() if a.text()]


def test_klappmenues_wie_vorlage(fenster):
    b = fenster.befehle
    assert _texte(b.klappe("leereSeiteKlappe")) == ["Vertikal", "Horizontal"]
    assert _texte(b.klappe("umbruecheKlappe")) == [
        "Seitenumbruch\tStrg+Enter", "Spaltenumbruch", "Textflussumbruch\tUmschalt+Enter", "Abschnittsumbruch auf nächster Seite",
        "Fortlaufender Abschnittsumbruch", "Abschnittsumbruch auf gerader Seite", "Abschnittsumbruch auf ungerader Seite"]
    assert _texte(b.klappe("bildKlappe")) == ["Bild aus Datei einfügen …", "Bildschirmfoto …", "Piktogramm …"]
    tf = b.klappe("textfeldKlappe")
    assert _texte(tf) == ["Horizontal", "Vertikal", "Mehrzeiliger Text"]
    assert not tf.actions()[1].isEnabled()                  # grau sichtbar statt versteckt
    assert _texte(b.klappe("schnellbausteineKlappe")) == ["AutoText-Liste", "Felder …"]
    assert b.hat("textflussumbruch")                        # auch im Seitenlayout-Menü nicht mehr grau


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
    d = FelderDialog(fenster, {"autor": "Kay"})
    d.liste.setCurrentRow(list(F.FELDER).index("Autor"))
    assert d.feld() == ("AUTHOR", "Kay")
    F.feld_einfuegen(e, *d.feld()); e.insertPlainText(" danach")
    c = QTextCursor(e.document()); c.setPosition(2)
    assert c.charFormat().stringProperty(P_FELD) == "AUTHOR"
    c.movePosition(QTextCursor.End)
    assert not c.charFormat().hasProperty(P_FELD)


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


def test_tabelle_in_text_fenster_wie_vorlage():
    from lunivo_writer.ui.dialogs.einfuegen_fenster import TrennerDialog
    from PySide6.QtWidgets import QRadioButton
    d = TrennerDialog(None, zu_tabelle=False)
    assert [r.text().replace("&", "") for r in d.findChildren(QRadioButton)] == ["Absätze", "Tabstopps", "Kommata", "Andere:"]
    assert d.trenner() == "\t" and d.geschachtelt.isChecked() and not d.geschachtelt.isEnabled()


def test_tabelle_einfuegen_fenster_und_stift(fenster):
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtGui import QTextLength
    from PySide6.QtTest import QTest
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
    QTest.mousePress(stift, Qt.LeftButton, pos=a); QTest.mouseMove(stift, b); QTest.mouseRelease(stift, Qt.LeftButton, pos=b)
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
    assert len(m.knoepfe) == 10 and not m.knoepfe["kopf_aussen"].isEnabled() and m.knoepfe["fuss_rechts"].isEnabled()
    m.gewaehlt.emit("fuss_rechts")
    s = fenster.current_editor().abschnitt_seite()
    assert (s.footer.text, s.footer.align) == ("{PAGE}", "right")


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
    assert set(b.klappe("deckblattKlappe").knoepfe) == set(E.DECKBLATT_VORLAGEN)
    b.deckblattVorlage("Farbband")
    assert e.document().firstBlock().next().text() == "[Titel des Dokuments]"
    assert len(b.klappe("wordartKlappe").knoepfe) == len(E.WORDART_VORGABEN)


def test_diagramm_alle_arten_und_fenster(app):
    from lunivo_writer.editor import diagramm as D
    from lunivo_writer.ui.dialogs.einfuegen_dialoge import DiagrammDialog
    for _g, _s, unter in D.TYPEN:
        for u, _n in unter:
            img = D.bild(u, "T", D.BEISPIEL_KATEGORIEN, D.BEISPIEL_REIHEN, 200, 140)
            assert not img.isNull() and img.pixelColor(100, 70).name() != "#000000"
    d = DiagrammDialog(None)
    kurs = d.arten.item([g for g, _s, _u in D.TYPEN].index("Kurs"))
    assert not kurs.flags() & __import__("PySide6.QtCore", fromlist=["Qt"]).Qt.ItemIsEnabled      # grau, nicht versteckt
    d.arten.setCurrentRow(1)                                               # Linie
    assert d.untertyp == "linie" and d.name.text() == "Linie" and len(d._knoepfe.buttons()) == 3
    assert d.daten()["kategorien"] == D.BEISPIEL_KATEGORIEN


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
    fenster.befehle.dateiObjekt()
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
