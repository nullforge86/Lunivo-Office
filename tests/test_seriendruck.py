"""Reiter „Mailings“ (Seriendruck) nach Kays Vorlage verweise/08-seriendruck.png: Datenquelle, Empfänger, Felder, Vorschau mit
Datensatz-Blättern, Zusammenführen."""
from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog

from lunivo_writer.editor import sendungen as S


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


@pytest.fixture
def liste(tmp_path):
    p = tmp_path / "empfaenger.csv"
    p.write_text("Vorname;Stadt\nAnna;Kiel\nBernd;Bonn\nCarla;Ulm\n", encoding="utf-8")
    return str(p)


def _knoepfe(w):
    from PySide6.QtWidgets import QToolButton
    return {k.toolTip().split("\n")[0]: k for k in w.band.findChildren(QToolButton)}


def test_band_mailings_wie_vorlage(fenster):
    from lunivo_writer.ui.ribbon.plan import plan
    from lunivo_writer.ui.ribbon.ribbon_bar import lade_register
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


def test_naechster_datensatz_und_zuordnung(app):
    from lunivo_writer.ui.document.document_editor import DocumentEditor
    e = DocumentEditor()
    S.feld_einfuegen(e, "Name"); e.insertPlainText(" | "); S.naechster_einfuegen(e); S.feld_einfuegen(e, "Name")
    saetze = [S.zugeordnet(s, {"Name": "Vorname"}) for s in S.tabelle_lesen("Vorname;Stadt\nAnna;Kiel\nBernd;Bonn\nCarla;Ulm")[1]]
    assert S.saetze_je_brief(e.document()) == 2
    briefe = S.gruppen(e.document(), saetze)
    assert [S.brief_fuer(e.document(), g).toPlainText() for g in briefe] == ["Anna | Bernd", "Carla | {{Name}}"]


def test_quelle_empfaenger_vorschau_und_zusammenfuehren(fenster, liste, monkeypatch, tmp_path):
    from lunivo_writer.ui.baukasten import speichern_fenster
    from lunivo_writer.ui.dialogs import serien_fenster as SF
    from lunivo_writer.ui.document import serien_vorschau
    b, e = fenster.befehle, fenster.current_editor()
    e.insertPlainText("Hallo "); S.feld_einfuegen(e, "Name"); e.insertPlainText(" aus "); S.feld_einfuegen(e, "Stadt")
    monkeypatch.setattr(speichern_fenster, "datei_waehlen", lambda *a, **k: [liste])
    b.serienReiter(); b.serienQuelle(); fenster.band.aktualisieren(True)
    assert _knoepfe(fenster)["Seriendruck-Vorschau"].isEnabled()
    # Übereinstimmende Felder: „Name“ im Text bekommt die Spalte „Vorname“
    monkeypatch.setattr(SF.ZuordnenDialog, "exec", lambda self: (self.wahl["Name"].setCurrentIndex(self.wahl["Name"].findData("Vorname")),
                                                                  QDialog.Accepted)[1])
    b.serienZuordnen()
    # Empfänger: Bernd auslassen
    monkeypatch.setattr(SF.EmpfaengerDialog, "exec", lambda self: (self.tabelle.item(1, 0).setCheckState(Qt.Unchecked), QDialog.Accepted)[1])
    b.serienEmpfaenger()
    t = fenster.current_tab()
    b.serienVorschau()
    assert serien_vorschau.aktiv(t) and t._serien_vorschau.toPlainText() == "Hallo Anna aus Kiel" and t._serien_vorschau.isReadOnly()
    assert fenster.band.felder["datensatz"].text() == "1"
    b.serienLetzter()
    assert t._serien_vorschau.toPlainText() == "Hallo Carla aus Ulm" and fenster.band.felder["datensatz"].text() == "2"
    b.serienVorheriger(); b.serienVorheriger()                                          # bleibt beim ersten
    assert t._serien_vorschau.toPlainText().startswith("Hallo Anna")
    assert "{{Name}}" in e.toPlainText()                                                 # die Vorlage bleibt unverändert
    b.serienVorschau()
    assert not serien_vorschau.aktiv(t) and not e.isHidden()
    # In neuem Dokument zusammenführen
    neu = b.serienNeuesDokument()
    assert neu.editor.toPlainText().splitlines() == ["Hallo Anna aus Kiel", "Hallo Carla aus Ulm"]
    # In anderem neuen Dokument: je Brief eine Datei
    fenster.tabs.setCurrentWidget(t)
    monkeypatch.setattr(speichern_fenster, "ordner_waehlen", lambda *a, **k: str(tmp_path))
    b.serienEinzeln()
    assert len(list(tmp_path.glob("*.docx"))) == 2


def test_feld_dialog_meldet_und_bleibt_offen(app):
    from lunivo_writer.ui.dialogs.serien_fenster import FeldDialog
    d = FeldDialog(None, ["Vorname", "Stadt"])
    gemeldet = []
    d.einfuegen.connect(gemeldet.append)
    d.liste.setCurrentRow(1); d.zeile.ok.click()
    d.name.setText("{{Eigenes}}"); d.zeile.ok.click()
    assert gemeldet == ["Stadt", "Eigenes"] and d.zeile.abbrechen.text() == "Schließen"
    leer = FeldDialog(None, [])
    assert not leer.zeile.ok.isEnabled()
