"""Kontext-Reiter „Zeichentools“ und „Texttools“ bei markiertem WordArt oder Textfeld: beide erscheinen, jeder Knopf hat einen Befehl und wirkt."""
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QToolButton

from lunivo_writer.ui.contextual.image_tools import ZEICHENTOOLS
from lunivo_writer.ui.contextual.text_tools import TEXTTOOLS


def _fenster(tmp_path):
    from PySide6.QtCore import QSettings
    from lunivo_writer.services.settings_service import Settings
    from lunivo_writer.ui.main_window import MainWindow
    w = MainWindow(Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat)))
    w.new_document()
    return w


def _zu(w):
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def _sichtbar(w, kontext):
    return w.band.reiter.isTabVisible(w.band.kontext_index[kontext])


def _knoepfe(plan):
    for g in plan["gruppen"]:
        for e in g.get("knoepfe", []):
            if e.get("name") and not e.get("zeilenumbruch") and e.get("symbol") != "//":
                yield g, e


def test_wordart_zeigt_zeichentools_und_texttools(app, tmp_path):
    w = _fenster(tmp_path); w.show()
    assert not _sichtbar(w, "zeichen") and not _sichtbar(w, "text")
    w.band.b.wordartVorgabe(None, 1)
    w._sync_format()
    assert _sichtbar(w, "zeichen") and _sichtbar(w, "text")
    r = w.band.reiter
    assert r.tabText(w.band.kontext_index["zeichen"]) == "Zeichentools" and r.tabText(w.band.kontext_index["text"]) == "Texttools"
    assert r.currentIndex() == w.band.kontext_index["text"]                  # WordArt: Texttools ist aktiv
    w.current_editor()._frei_sel = None
    w._sync_format()
    assert not _sichtbar(w, "zeichen") and not _sichtbar(w, "text")
    _zu(w)


def test_textfeld_zeigt_beide_reiter_zeichentools_aktiv(app, tmp_path):
    w = _fenster(tmp_path); w.show()
    w.band.b.textfeld()
    w._sync_format()
    assert _sichtbar(w, "zeichen") and _sichtbar(w, "text")
    assert w.band.reiter.currentIndex() == w.band.kontext_index["zeichen"]   # Textfeld: Zeichentools ist aktiv
    _zu(w)


def test_jeder_knopf_hat_einen_befehl(app, tmp_path):
    w = _fenster(tmp_path); w.show()
    b = w.band.b
    for plan in (TEXTTOOLS, ZEICHENTOOLS):
        for g, e in _knoepfe(plan):
            tun, klappe = e.get("tun"), e.get("klappe")
            assert (tun and b.hat(tun)) or (klappe and w.band._klappe(klappe) is not None), (plan["name"], e["name"])
        for g in plan["gruppen"]:
            if g.get("galerie"):
                from lunivo_writer.ui.baukasten.bild_diagramm_menues import GALERIEN
                spec = GALERIEN[g["galerie"]](b) if g["galerie"] in GALERIEN else getattr(b, "galerie_" + g["galerie"])()
                assert len(spec["kacheln"]) in (3, 6, 10) and spec["menue"] is not None
            if g.get("pfeil"):
                assert b.hat(g["pfeil"])
    # im gebauten Band ist keiner dieser Knöpfe ausgegraut und kein Befehl fehlt
    namen = {e.get("tun") for plan in (TEXTTOOLS, ZEICHENTOOLS) for _g, e in _knoepfe(plan)} | {e.get("klappe") for plan in (TEXTTOOLS, ZEICHENTOOLS) for _g, e in _knoepfe(plan)}
    assert not (namen & set(w.band.bandfehler))
    for i in (w.band.kontext_index["text"], w.band.kontext_index["zeichen"]):
        seite = w.band.stapel.widget(i)
        for k in seite.findChildren(QToolButton):
            assert not k.property("fehlt"), k.toolTip()
    _zu(w)


def _wordart(w):
    from lunivo_writer.editor import frei_objekt as FO
    w.band.b.wordartVorgabe(None, 0)
    w._sync_format()
    return w.current_editor(), FO


def test_texttools_wirken_auf_wordart(app, tmp_path):
    w = _fenster(tmp_path); w.show()
    b = w.band.b
    ed, FO = _wordart(w)
    d = lambda: FO.daten_lesen(ed, "wordart")
    b.ttKursiv(); assert d()["kursiv"] is True and b.an_ttKursiv()
    b.ttFett(); assert d()["fett"] is False
    b.ttUnter(); assert d()["unter"] == "einfach"
    b.ttDurch(); assert d()["durch"] is True
    b.ttHoch(); assert d()["hoch"] is True
    b.ttTief(); assert d()["tief"] is True and not d().get("hoch")
    b.ttSchriftart("DejaVu Sans"); assert d()["schrift"] == "DejaVu Sans"
    b.ttGroesse("48"); assert d()["pt"] == 48.0
    b.ttGroesser(); assert d()["pt"] == 50.0
    b.ttKleiner(); assert d()["pt"] == 48.0
    b.ttPunkte(); assert d()["liste"]["stil"] == "disc" and b.an_ttPunkte()
    b.ttZahlen(); assert d()["liste"]["stil"] == "dezimal" and b.an_ttZahlen() and not b.an_ttPunkte()
    from lunivo_writer.ui.baukasten.liste_dialog import aufzaehlungen, nummerierungen
    r = b.menue_ttPunkte(); r.gewaehlt.emit("1"); assert d()["liste"] == aufzaehlungen()[1]     # dieselbe Auswahl wie bei Start
    r = b.menue_ttZahlen(); r.gewaehlt.emit("2"); assert d()["liste"] == nummerierungen()[2]
    r.gewaehlt.emit("keine"); assert "liste" not in d()
    b.ttEinzugMehr(); assert d()["einzug"] == 1
    b.ttEinzugWeniger(); assert "einzug" not in d()
    for n, w_ in (("ttMitte", "mitte"), ("ttRechts", "rechts"), ("ttBlock", "block"), ("ttVerteilt", "verteilt"), ("ttLinks", "links")):
        getattr(b, n)(); assert d()["ausr"] == w_
    m = b.menue_ttZeilenabstand(); m.actions()[2].trigger(); assert d()["zeilenabstand"] == 2.0
    m = b.menue_ttTextrichtung()
    for art, _t in b.TEXTRICHTUNGEN[1:]:
        m.gewaehlt.emit(art); assert d()["richtung"] == art
    m.gewaehlt.emit("waagerecht"); assert "richtung" not in d()
    ed2 = ed
    FO.aendern(ed2, "wordart", text="b\na")
    b.ttSortieren(); assert d()["text"] == "a\nb"
    b.ttStil(3); assert d()["vorlage"] == 3
    b._wa_set(fuell="#ff0000", kontur="#00ff00", hervor="#ffff00"); assert d()["fuell"] == "#ff0000"
    b.ttSchlicht()
    assert not ({"kursiv", "unter", "durch", "hoch", "tief", "liste", "fuell", "kontur", "hervor", "schrift", "pt"} & set(d()))
    b.ttFormstil("z10")
    z = FO.ziel(ed)
    assert z[3]["fuell"]["art"] == "farbe"
    m = b.menue_ttFormEffekte()
    sub = next(a.menu() for a in m.actions() if a.menu() and a.text() == "Schatten")
    sub.gewaehlt.emit("0")
    assert "schatten" in (FO.ziel(ed)[3].get("fx") or {})
    m2 = b.menue_ttTexteffekte()
    sub = next(a.menu() for a in m2.actions() if a.menu() and a.text() == "Leuchteffekt")
    sub.gewaehlt.emit("0")
    assert "leuchten" in d()["effekt"]
    b.ttFormatUebertragen(); assert b.an_ttFormatUebertragen()
    b.ttFormatUebertragen(); assert not b.an_ttFormatUebertragen()
    _zu(w)


def test_texttools_wirken_auf_textfeld_und_navigation(app, tmp_path):
    from lunivo_writer.editor import frei_objekt as FO
    w = _fenster(tmp_path); w.show()
    b = w.band.b
    b.textfeld(); ed = w.current_editor()
    b.ttKursiv(); assert FO.daten_lesen(ed, "textfeld")["kursiv"] is True
    b.ttGroesse("20"); assert FO.daten_lesen(ed, "textfeld")["pt"] == 20.0
    b.ttMitte(); assert FO.daten_lesen(ed, "textfeld")["ausr"] == "mitte"
    b.wordartVorgabe(None, 0)
    assert FO.art_gewaehlt(ed) == "wordart"
    b.ttVoriges()
    assert FO.art_gewaehlt(ed) == "textfeld"
    b.ttNaechstes()
    assert FO.art_gewaehlt(ed) == "wordart"
    _zu(w)


def test_verknuepfung_erstellen_ueber_die_knoepfe(app, tmp_path):
    from lunivo_writer.editor import frei_objekt as FO
    w = _fenster(tmp_path); w.show()
    b = w.band.b; ed = w.current_editor()
    b.textfeld(); a = ed._frei_sel
    b.textfeld(); bb = ed._frei_sel
    lang = " ".join(f"Wort{i}" for i in range(60))
    FO.bearbeiten_beenden(ed)
    ed._frei_sel = a; FO.aendern(ed, "textfeld", text=lang, breite=200, hoehe=60)
    m = b.menue_ttVerknuepfung()
    verknuepfen = [x for x in m.actions() if x.text().startswith("Verknüpfen mit")]
    assert verknuepfen and not [x for x in m.actions() if x.text() == "Verknüpfung aufheben"][0].isEnabled()
    b.ttVerknuepfen(None, bb)
    fel = dict(FO._textfelder(ed))
    assert FO.ist_verknuepft(ed, a) and fel[a]["daten"]["gezeigt"] and fel[bb]["daten"]["gezeigt"]         # Überlauf steht in B
    assert (fel[a]["daten"]["gezeigt"] + " " + fel[bb]["daten"]["gezeigt"]).split() == lang.split()
    m.aboutToHide.emit(); m.aboutToShow.emit()
    assert [x for x in m.actions() if x.text() == "Verknüpfung aufheben"][0].isEnabled()
    b.ttVerknuepfungLoesen()
    assert not FO.ist_verknuepft(ed, a)
    assert "von" not in dict(FO._textfelder(ed))[bb]["daten"]
    _zu(w)
