"""Abschnitte mit eigener Blattgröße (Quer- und Hochformat) stehen untereinander; jede Seite hat die Größe ihres Abschnitts, die Datei merkt sich beide Größen.

Früher zeigte ein Zusatz der Anzeige (``editor/seite/querblatt.py``) die Blätter; jetzt gibt die Layout-Engine jeder Seite ihre Einrichtung mit."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest

from lunivo_writer.core.layout import LayoutEngine
from lunivo_writer.modelle.seite import PageSettings
from tests.hilfen_dokument import docx_rundlauf, sitzung


def _quer_dokument():
    s = sitzung("Hochformat")
    quer = PageSettings(); quer.set_orientation(True)
    s.abschnitt_einfuegen(beginn="naechste", seite=quer)
    s.text_einfuegen("Querformat")
    return s.dokument


def test_jede_seite_hat_die_groesse_ihres_abschnitts():
    erg = LayoutEngine().berechnen(_quer_dokument())
    assert len(erg.seiten) == 2
    hoch, quer = erg.seiten[0].einrichtung, erg.seiten[1].einrichtung
    assert hoch.height_mm > hoch.width_mm and quer.width_mm > quer.height_mm


def test_docx_merkt_sich_beide_blattgroessen(app, tmp_path):
    gelesen, _schreib, _lese, _pfad = docx_rundlauf(_quer_dokument(), tmp_path)
    erste, zweite = gelesen.abschnitte[0].seite, gelesen.abschnitte[1].seite
    assert erste.height_mm == pytest.approx(297, abs=1) and zweite.width_mm == pytest.approx(297, abs=1) and zweite.height_mm == pytest.approx(210, abs=1)
