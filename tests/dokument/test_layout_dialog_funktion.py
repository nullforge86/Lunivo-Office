"""Fenster „Layout“, Reiter Größe: Skalieren, Seitenverhältnis, Originalgröße, Zurücksetzen wirken wirklich auf die Werte."""
from lunivo_writer.ui.baukasten.dokument.layout_dialog import LayoutDialog


def _d(**kw):
    w = {"original": (60.0, 40.0), "breite": {"mm": 60.0}, "hoehe": {"mm": 40.0}}
    w.update(kw)
    return LayoutDialog(None, w)


def test_skalieren_sperren_original_und_zuruecksetzen(app):
    d = _d()
    d.skal_h.setValue(200)
    assert abs(d.werte()["hoehe"]["mm"] - 80.0) < 0.01 and abs(d.werte()["breite"]["mm"] - 60.0) < 0.01
    d.sperren.setChecked(True)
    d.skal_b.setValue(50)                                              # gesperrt: Höhe zieht mit
    assert abs(d.skal_h.value() - 50) < 0.01 and abs(d.werte()["hoehe"]["mm"] - 20.0) < 0.01
    d.breite["mm"].setValue(120.0)                                     # Breite getippt: Höhe folgt im Verhältnis 3:2
    assert abs(d.werte()["hoehe"]["mm"] - 80.0) < 0.05 and abs(d.skal_b.value() - 200) < 0.1
    d.drehung.setValue(30)
    d._zuruecksetzen()
    w = d.werte()
    assert (w["breite"]["mm"], w["hoehe"]["mm"], w["drehung"]) == (60.0, 40.0, 0.0) and d.skal_h.value() == 100 == d.skal_b.value()


def test_ohne_original_bezug_gilt_die_groesse_beim_oeffnen(app):
    d = _d(breite={"mm": 30.0}, hoehe={"mm": 20.0})
    d.skal_original.setChecked(False)
    assert d.skal_h.value() == 100
    d.skal_h.setValue(150)
    assert abs(d.werte()["hoehe"]["mm"] - 30.0) < 0.01


def test_objekt_fenster_textfluss_grau_smartart_gesperrt_abstand_reihenfolge(app):
    from lunivo_writer.ui.baukasten.dokument.layout_dialog_objekt import layout_dialog_fuer
    w = {"umbruch": "textfluss", "original": (60.0, 40.0), "breite": {"mm": 60.0}, "hoehe": {"mm": 40.0}}
    d = layout_dialog_fuer("smartart")(None, w)
    assert not d.h["box"].isEnabled() and not d.v["box"].isEnabled() and not d.ueberlappen.isEnabled()
    d.kacheln.setze("quadrat", True)
    assert d.h["box"].isEnabled() and d.ueberlappen.isEnabled()
    assert not d.drehung.isEnabled() and not d.skal_original.isEnabled() and not d.skal_original.isChecked() and d.orig_text.text() == ""
    assert not d.hoehe["r_rel"].isEnabled() and d.werte()["hoehe"]["modus"] == "abs"
    zeilen = [d._abstand_box.layout().itemAt(i).widget() for i in range(d._abstand_box.layout().count())]
    assert [d.abstand[k] for k in ("oben", "unten", "links", "rechts")] == [f for f in zeilen if f in d.abstand.values()]
    b = layout_dialog_fuer("bild")(None, w)
    assert b.drehung.isEnabled() and b.skal_original.isChecked() and "Höhe" in b.orig_text.text()


def test_objekt_popup_schliessen_und_leere_radios(app):
    from lunivo_writer.ui.baukasten.dropdown.layout_optionen_objekt import LayoutOptionenObjekt
    p = LayoutOptionenObjekt(None, "vor", False)
    gemeldet = []
    p.verschieben.connect(gemeldet.append)
    p.verschieben_wahl = None
    assert not p.r_mit.isChecked() and not p.r_fest.isChecked() and gemeldet == []
    p.r_mit.click()
    assert gemeldet == [True] and p.verschieben_wahl == "mit_text"
    p.r_fest.click()
    assert p.verschieben_wahl == "fest" and not p.r_mit.isChecked()
    p.verschieben_wahl = "mit_text"
    assert p.r_mit.isChecked() and p.zeile.knoepfe["textfluss"].iconSize().width() == 50
