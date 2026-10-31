"""SmartArt-Fenster: Galerie der Layouts, Beschreibung, nichts ragt in der Seitenleiste heraus."""
import pytest
from PySide6.QtWidgets import QWidget

from lunivo_writer.editor import smartart as SA
from lunivo_writer.ui.baukasten.zusatz_panel import ZusatzPanel
from lunivo_writer.ui.dialogs.einfuegen_dialoge import SmartArtDialog


@pytest.mark.parametrize("breite", [300, 444])
def test_nichts_ragt_heraus(app, breite):
    p = ZusatzPanel(); p.verfuegbar, p.verfuegbar_hoehe = breite, 587; p.resize(breite + 36, 727)
    d = SmartArtDialog(None); p.oeffne(d); p.show(); app.processEvents(); app.processEvents()
    for w in d.findChildren(QWidget):
        if w.isVisible():
            r = w.mapTo(d, w.rect().bottomRight())
            assert r.x() <= d.width() + 1, (type(w).__name__, r.x(), d.width())
    assert list(d.galerie.feld.knoepfe) == SA.KATALOG_LAYOUTS and len(d.galerie.feld.knoepfe) == 15
    p.close()


def test_auswahl_liefert_layout(app):
    d = SmartArtDialog(None)
    d.galerie.feld.knoepfe["Segmentzyklus"].click()
    assert d.daten()["layout"] == "Segmentzyklus" and d.name.text() == SA.ANZEIGENAMEN["Segmentzyklus"] and d.beschreibung.text()
    assert d.daten()["text"] == SA.MUSTER["Segmentzyklus"]
    assert not d.bearbeiten.isVisibleTo(d)
    e = SmartArtDialog(None, {"layout": "Pyramide", "farben": "Grün", "text": "A\nB"})
    assert e.bearbeiten.isVisibleTo(e) and e.daten() == {"layout": "Pyramide", "farben": "Grün", "text": "A\nB"}
