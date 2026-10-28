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
    assert _texte(b.klappe("bildKlappe")) == ["Bild aus Datei einfügen …"]
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
    weitere = [e["name"] for g in tab["gruppen"] if g["name"] == "Weitere" for e in g["knoepfe"]]
    assert {"Schnelltabelle", "Text aus Datei"} <= set(weitere)   # nichts geht verloren


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


def test_leere_seite_horizontal_eigener_abschnitt(fenster):
    from lunivo_writer.editor import abschnitte as AB
    e = fenster.current_editor(); e.insertPlainText("x")
    fenster.befehle.leereSeite(None, True)
    n = AB.anzahl(e.document())
    assert [e.abschnitt_seite(i).landscape for i in range(n)] == [False, True, False]


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
