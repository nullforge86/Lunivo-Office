"""Reiter Seitenlayout nach Kays Vorlagen (Ordner seitenlayout/): Galerien, Klappmenüs, Zeilennummern."""
from __future__ import annotations

import pytest
from PySide6.QtGui import QTextBlockFormat


@pytest.fixture
def fenster(app, tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.dienste.einstellungen_dienst import Settings
    from lunivo_writer.oberflaeche.programmfenster import MainWindow
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
    from lunivo_writer.oberflaeche.band.plan import plan
    from lunivo_writer.oberflaeche.band.band_leiste import lade_register
    tab = next(t for t in plan(lade_register()) if t["name"] == "Seitenlayout")
    knoepfe = {e["name"]: e for g in tab["gruppen"] for e in g["knoepfe"]}
    for name, klappe in (("Designs", "designsKlappe"), ("Farben", "farbenKlappe"), ("Schriftarten", "schriftartenKlappe"),
                         ("Effekte", "effekteKlappe"), ("Ränder", "raenderKlappe"), ("Orientierung", "ausrichtungKlappe"),
                         ("Größe", "groesseKlappe"), ("Spalten", "spaltenKlappe"), ("Textrichtung", "textrichtungKlappe"),
                         ("Seitenfarbe", "seitenfarbeKlappe")):
        assert knoepfe[name].get("klappe") == klappe and "tun" not in knoepfe[name] and "menue" not in knoepfe[name], name
    # Umbrüche + Zeilennummern und Ausrichten + Drehen + Gruppieren stehen je hinter einem Knopf (Platz im Band bei 1366 px)
    assert [i.get("klappe") for i in knoepfe["Umbrüche"]["menue"]] == ["umbruecheKlappe", "zeilennummernKlappe"]
    assert [i.get("klappe") or i.get("tun") for i in knoepfe["Objekte"]["menue"]] == ["ausrichtenKlappe", "objektDrehen", "gruppieren"]
    assert knoepfe["Seitenränder"]["tun"] == "seitenrahmen"
    assert not fenster.befehle.hat("genkoEinstellung")                   # Genko bleibt grau sichtbar
    namen = [e["name"] for g in tab["gruppen"] for e in g["knoepfe"]]
    assert namen.index("Seitenfarbe") < namen.index("Seitenränder") < namen.index("Genko-Einstellung") < namen.index("Textfluss")




def test_effekte_galerie(fenster):
    from lunivo_writer.editor.text import designs as D
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




def test_zeilennummern_jede_seite_neu():
    from lunivo_writer.core.layout import LayoutEngine
    from tests.hilfen_dokument import sitzung
    erg = LayoutEngine().berechnen(sitzung("\n".join(f"Zeile {i}" for i in range(120))).dokument)
    assert len(erg.seiten) >= 2
    je_seite = [n for _s, _y, _h, n in erg.zeilennummern("seite")]
    fortlaufend = [n for _s, _y, _h, n in erg.zeilennummern()]
    assert len(je_seite) == len(fortlaufend) == 120
    assert fortlaufend == list(range(1, 121))                                  # fortlaufend durch das ganze Dokument
    erste_der_zweiten = next(n for s, _y, _h, n in erg.zeilennummern("seite") if s == 1)
    assert erste_der_zweiten == 1 and max(je_seite) < 120                      # auf jeder Seite neu ab 1