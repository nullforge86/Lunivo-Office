"""Reiter Seitenlayout nach Kays Vorlagen (Ordner seitenlayout/): Galerien, Klappmenüs, Zeilennummern."""
from __future__ import annotations

import pytest
from PySide6.QtGui import QTextBlockFormat


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


def _absaetze(e, *texte):
    c = e.textCursor()
    for i, t in enumerate(texte):
        if i:
            c.insertBlock(QTextBlockFormat())
        c.insertText(t)
    e.setTextCursor(c)


def test_band_seitenlayout_wie_vorlage(fenster):
    from lunivo_writer.ui.ribbon.plan import plan
    from lunivo_writer.ui.ribbon.ribbon_bar import lade_register
    tab = next(t for t in plan(lade_register()) if t["name"] == "Seitenlayout")
    knoepfe = {e["name"]: e for g in tab["gruppen"] for e in g["knoepfe"]}
    for name, klappe in (("Designs", "designsKlappe"), ("Farben", "farbenKlappe"), ("Schriftarten", "schriftartenKlappe"),
                         ("Effekte", "effekteKlappe"), ("Ränder", "raenderKlappe"), ("Orientierung", "ausrichtungKlappe"),
                         ("Größe", "groesseKlappe"), ("Spalten", "spaltenKlappe"), ("Textrichtung", "textrichtungKlappe"),
                         ("Umbrüche", "umbruecheKlappe"), ("Zeilennummern", "zeilennummernKlappe"), ("Seitenfarbe", "seitenfarbeKlappe"),
                         ("Ausrichten", "ausrichtenKlappe")):
        assert knoepfe[name].get("klappe") == klappe and "tun" not in knoepfe[name] and "menue" not in knoepfe[name], name
    assert knoepfe["Seitenränder"]["tun"] == "seitenrahmen"
    assert not fenster.befehle.hat("genkoEinstellung")                   # Genko bleibt grau sichtbar
    namen = [e["name"] for g in tab["gruppen"] for e in g["knoepfe"]]
    assert namen.index("Seitenfarbe") < namen.index("Seitenränder") < namen.index("Genko-Einstellung") < namen.index("Textfluss")


def test_designs_farben_schriften(fenster):
    from lunivo_writer.editor import designs as D
    e = fenster.current_editor()
    e.insertPlainText("Titel"); e.apply_style("Überschrift 1")
    c = e.textCursor(); c.insertBlock(QTextBlockFormat()); c.insertText("Text"); e.setTextCursor(c)
    m = fenster.befehle.klappe("designsKlappe")
    assert len(m.knoepfe) == len(D.DESIGNS)
    m.gewaehlt.emit("Ostsee")
    kopf, text = D.SCHRIFTPAARE[D.DESIGNS["Ostsee"][1]]
    assert e.document().defaultFont().family() == text

    def fmt():
        from PySide6.QtGui import QTextCursor
        c = QTextCursor(e.document().firstBlock()); c.movePosition(QTextCursor.NextCharacter)
        return c.charFormat()
    assert kopf in fmt().fontFamilies() and fmt().foreground().color().name() == D.ueberschrift_farbe("Ostsee")
    fenster.befehle.klappe("farbenKlappe").gewaehlt.emit("Mohn")
    assert fmt().foreground().color().name() == D.ueberschrift_farbe("Mohn")
    fenster.befehle.klappe("schriftartenKlappe").gewaehlt.emit("Klassisch")
    assert e.document().defaultFont().family() == "Liberation Serif"


def test_effekte_galerie(fenster):
    from lunivo_writer.editor import designs as D
    m = fenster.befehle.klappe("effekteKlappe")
    assert list(m.knoepfe) == list(D.EFFEKTE)
    m.gewaehlt.emit("Weicher Schatten")                                   # ohne Formen: nur ein Hinweis in der Statuszeile
    assert "Formen" in fenster.statusBar().currentMessage()


def test_raender_groesse_orientierung(fenster):
    b = fenster.befehle
    r = b.klappe("raenderKlappe"); r.aboutToShow.emit()
    assert r.knoepfe["normal"].isChecked()
    r.gewaehlt.emit("schmal")
    p = fenster.current_editor().abschnitt_seite()
    assert (round(p.margin_top_mm), round(p.margin_left_mm)) == (13, 13)
    b.klappe("groesseKlappe").gewaehlt.emit("a5")
    assert b.w_papierJetzt() == "a5"
    o = b.klappe("ausrichtungKlappe"); o.gewaehlt.emit("quer"); o.aboutToShow.emit()
    assert b.w_querJetzt() and o.knoepfe["quer"].isChecked()


def test_spalten_textrichtung_ausrichten(fenster):
    b = fenster.befehle
    s = b.klappe("spaltenKlappe")
    assert [a.text() for a in s.actions()] == ["Eins", "Zwei", "Drei", "Mehr Spalten …"]
    s.actions()[1].trigger(); s.aboutToShow.emit()
    assert b.w_spaltenJetzt() == 2 and s.actions()[1].isChecked()
    t = b.klappe("textrichtungKlappe")
    assert [k for k, w in t.knoepfe.items() if w.isEnabled()] == ["waagerecht"]       # die senkrechten bleiben grau
    a = b.klappe("ausrichtenKlappe"); a.aboutToShow.emit()
    texte = {x.text(): x for x in a.actions() if x.text()}
    assert not texte["Linksbündig"].isEnabled() and not texte["Gleiche Größe"].isEnabled() and texte["Gitternetzlinien"].isEnabled()


def test_seitenfarbe_mit_wasserzeichen(fenster):
    m = fenster.befehle.klappe("seitenfarbeKlappe")
    unter = {a.text(): a for a in m.actions() if a.text()}
    assert unter["Wasserzeichen"].menu() is not None and not unter["Hintergrundbild …"].isEnabled()


def test_zeilennummern_arten_und_unterdruecken(fenster, tmp_path):
    from lunivo_writer.editor.zeilennummern import nummern
    from lunivo_writer.services.docx_reader import read_docx
    from lunivo_writer.services.docx_writer import write_docx
    b = fenster.befehle; e = fenster.current_editor()
    _absaetze(e, "eins", "zwei", "drei")
    m = b.klappe("zeilennummernKlappe"); m.aboutToShow.emit()
    texte = {a.text(): a for a in m.actions() if a.text()}
    assert texte["Keine"].isChecked() and not texte["Für aktuellen Absatz unterdrücken"].isEnabled()
    b.zeilennummernArt(None, "seite")
    m.aboutToShow.emit()
    assert e.page.zeilennummern and e.page.zeilennummern_neu == "seite" and texte["Jede Seite neu beginnen"].isChecked()
    c = e.textCursor(); c.setPosition(e.document().findBlockByNumber(1).position()); e.setTextCursor(c)
    b.zeilennummernUnterdruecken()
    assert [(bl.text(), nr) for bl, _z, _y, nr in nummern(e.document(), 10_000, "seite")] == [("eins", 1), ("drei", 2)]
    out = tmp_path / "z.docx"
    write_docx(out, e.document(), e.page, {})
    qd, ps, _m, _r = read_docx(out)
    assert ps.zeilennummern and ps.zeilennummern_neu == "seite"
    assert [bl.text() for bl, _z, _y, _n in nummern(qd, 10_000)] == ["eins", "drei"]
    b.zeilennummernArt(None, None)
    assert not e.page.zeilennummern


def test_zeilennummern_jede_seite_neu():
    from PySide6.QtGui import QTextDocument
    from lunivo_writer.editor.zeilennummern import nummern
    d = QTextDocument(); d.setPlainText("\n".join(f"Zeile {i}" for i in range(6)))
    d.setTextWidth(400)
    h = d.documentLayout().blockBoundingRect(d.firstBlock()).height()
    nr = [n for _b, _z, _y, n in nummern(d, h * 3, "seite")]
    assert nr == [1, 2, 3, 1, 2, 3] and [n for *_r, n in nummern(d, h * 3)] == [1, 2, 3, 4, 5, 6]
