"""Fenster „Layout“, Reiter Größe: Skalieren, Seitenverhältnis, Originalgröße, Zurücksetzen wirken wirklich auf die Werte."""
from lunivo_writer.ui.baukasten.layout_dialog import LayoutDialog


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
