"""Reiter „Mailings“ (Seriendruck) nach Kays Vorlage verweise/08-seriendruck.png: Datenquelle, Empfänger, Felder, Vorschau mit
Datensatz-Blättern, Zusammenführen."""
from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog

from lunivo_writer.editor.dokument import sendungen as S


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


@pytest.fixture
def liste(tmp_path):
    p = tmp_path / "empfaenger.csv"
    p.write_text("Vorname;Stadt\nAnna;Kiel\nBernd;Bonn\nCarla;Ulm\n", encoding="utf-8")
    return str(p)


def _knoepfe(w):
    from PySide6.QtWidgets import QToolButton
    return {k.toolTip().split("\n")[0]: k for k in w.band.findChildren(QToolButton)}


def test_band_mailings_wie_vorlage(fenster):
    from lunivo_writer.oberflaeche.band.plan import plan
    from lunivo_writer.oberflaeche.band.band_leiste import lade_register
    tab = next(t for t in plan(lade_register()) if t["name"] == "Mailings")
    namen = [e["name"] for g in tab["gruppen"] for e in g["knoepfe"]]
    assert namen == ["Datenquelle öffnen", "Seriendruckempfänger", "Seriendruckfeld einfügen", "Nächstes Feld einfügen",
                     "Seriendruckfelder hervorheben", "Übereinstimmende Felder festlegen", "Seriendruck-Vorschau", "Erster Datensatz",
                     "Vorheriger Datensatz", "Datensatz", "Nächster Datensatz", "Letzter Datensatz", "In neuem Dokument zusammenführen",
                     "In anderem neuen Dokument zusammenführen", "An Drucker zusammenführen", "Seriendruck schließen"]
    for e in (e for g in tab["gruppen"] for e in g["knoepfe"] if e.get("tun")):
        assert fenster.befehle.hat(e["tun"]), e["name"]
    band = fenster.band
    i = band.kontext_index["serien"]
    assert not band.reiter.isTabVisible(i)
    fenster.befehle.serienReiter()                                                      # Verweise ▸ Seriendruck
    assert band.reiter.isTabVisible(i) and band.reiter.currentIndex() == i
    band.aktualisieren(True)
    kn = _knoepfe(fenster)
    assert kn["Seriendruckfeld einfügen"].isEnabled() and kn["Datenquelle öffnen"].isEnabled()
    for n in ("Seriendruckempfänger", "Seriendruck-Vorschau", "Erster Datensatz", "In neuem Dokument zusammenführen"):
        assert not kn[n].isEnabled(), n                                                  # ohne Datenquelle grau, wie in der Vorlage
    assert not band.felder["datensatz"].isEnabled()
    fenster.befehle.serienSchliessen()
    assert not band.reiter.isTabVisible(i)






def test_feld_dialog_meldet_und_bleibt_offen(app):
    from lunivo_writer.oberflaeche.dialoge.sendungen.serien_fenster import FeldDialog
    d = FeldDialog(None, ["Vorname", "Stadt"])
    gemeldet = []
    d.einfuegen.connect(gemeldet.append)
    d.liste.setCurrentRow(1); d.zeile.ok.click()
    d.name.setText("{{Eigenes}}"); d.zeile.ok.click()
    assert gemeldet == ["Stadt", "Eigenes"] and d.zeile.abbrechen.text() == "Schließen"
    leer = FeldDialog(None, [])
    assert not leer.zeile.ok.isEnabled()
