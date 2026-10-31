"""Reiter „Überprüfen“ nach Kays Vorlagen ueberpruefen/01–10: Anordnung, Wörter zählen, Markup-Auswahl, Original-Ansicht,
Annehmen der angezeigten Änderungen, Bearbeitung einschränken."""
from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtGui import QTextCursor

from lunivo_writer.editor import fassungen, statistik


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


def _mit_aenderungen(e, autoren=("Anna", "Bernd")):
    """Text „Alt bleibt.“ und je Autor eine Einfügung; Anna löscht dazu „Alt “."""
    e.insertPlainText("Alt bleibt.")
    e.set_verfolgen(True)
    for a in autoren:
        e.autor = lambda a=a: (a, "")
        c = e.textCursor(); c.movePosition(QTextCursor.End); e.setTextCursor(c)
        e.insertPlainText(f" {a}")
    e.autor = lambda: ("Anna", "")
    c = e.textCursor(); c.setPosition(0); c.setPosition(4, QTextCursor.KeepAnchor); e.setTextCursor(c)
    QTest.keyClick(e, Qt.Key_Delete)                                                     # verfolgt gelöscht: bleibt als Löschung stehen
    e.set_verfolgen(False)


def test_band_ueberpruefen_wie_vorlage(fenster):
    from lunivo_writer.ui.ribbon.plan import plan
    from lunivo_writer.ui.ribbon.ribbon_bar import lade_register
    tab = next(t for t in plan(lade_register()) if t["name"] == "Überprüfen")
    namen = [e["name"] for g in tab["gruppen"] for e in g["knoepfe"]]
    assert namen == ["Rechtschreibprüfung", "Wörter zählen", "Kommentar einfügen", "Löschen", "Vorherige", "Weiter",
                     "Änderungen nachverfolgen", "Anzeige zur Überprüfung", "Überprüfen", "Annehmen", "Ablehnen", "Vorherige", "Weiter",
                     "Vergleichen", "Freihand", "Bearbeitung einschränken"]
    b = fenster.befehle
    for e in (e for g in tab["gruppen"] for e in g["knoepfe"]):
        for n in (e.get("tun"), e.get("klappe")):
            if n:
                assert b.hat(n) or b.klappe(n) is not None, n
    fenster.band.aktualisieren(True)
    feld = fenster.band.felder["anzeige"]
    assert feld.anzeige.currentText() == "Endgültige Version enthält Markups" and feld.markup.menu() is not None
    assert not b.kann("kommentarWeg")                                                  # ohne Kommentar grau, wie in der Vorlage


def test_woerter_zaehlen():
    w = statistik.zaehlen(["Ein kleiner Satz.", "", "日本 und mehr"], seiten=2)
    assert w == {"seiten": 2, "woerter": 7, "zeichen_ohne": 24, "zeichen_mit": 28, "absaetze": 2, "nicht_asiatisch": 5, "asiatisch": 2}


def test_woerter_dialog_mit_noten(fenster, monkeypatch):
    from lunivo_writer.ui.dialogs import ueberpruefen_fenster as UF
    e = fenster.current_editor()
    e.insertPlainText("Drei Wörter hier")
    e.note_neu("f", "zwei mehr")
    gesehen = []
    monkeypatch.setattr(UF.WoerterDialog, "exec", lambda self: gesehen.append(self) or 0)
    fenster.befehle.woerterZaehlen()
    d = gesehen[0]
    assert d.werte["woerter"].text() == "3"
    d.noten.setChecked(True)
    assert d.werte["woerter"].text() == "5"


def test_markup_filter_original_und_angezeigte_annehmen(fenster):
    from lunivo_writer.ui.document import vorschau_ansicht
    b, e, t = fenster.befehle, fenster.current_editor(), fenster.current_tab()
    _mit_aenderungen(e)
    assert fassungen.bearbeiter(e.document()) == ["Anna", "Bernd"]
    assert fassungen.original(e.document()).toPlainText() == "Alt bleibt."
    # Original: schreibgeschützte Ansicht ohne die Änderungen, das Dokument bleibt
    b.ueberpruefenAnzeige(None, 3)
    assert vorschau_ansicht.aktiv(t, "original") and t._vorschau_ansicht.toPlainText() == "Alt bleibt."
    b.ueberpruefenAnzeige(None, 1)
    assert not vorschau_ansicht.aktiv(t) and not e.markup
    b.ueberpruefenAnzeige(None, 0)
    assert e.markup
    # nur Bernd zeigen und dessen Änderungen annehmen
    e.markup_filter_setzen(bearbeiter={"Bernd"})
    assert [e.aenderung_sichtbar(x) for x in e.aenderungen()].count(True) == 1
    b._angezeigte(True)
    rest = e.aenderungen()
    assert {x["cf"].stringProperty(fassungen.P_AUTOR) for x in rest} == {"Anna"} and "Bernd" in e.toPlainText()


def test_bearbeitung_einschraenken(fenster, monkeypatch):
    from lunivo_writer.ui.dialogs.ueberpruefen_fenster import SchutzDialog
    b, e, t = fenster.befehle, fenster.current_editor(), fenster.current_tab()
    d = SchutzDialog(None, None)
    assert not d.ok.isEnabled() and not d.wahl["lesen"].isEnabled()
    d.schutz.setChecked(True); d.wahl["aenderungen"].setChecked(True)
    assert d.ok.isEnabled() and not d.wahl["formulare"].isEnabled() and d.ergebnis() == "aenderungen"
    _mit_aenderungen(e, ("Anna",))
    b.schutz_setzen(t, "aenderungen")
    assert e.verfolgen and not e.isReadOnly() and b.an_bearbeitungEinschraenken()
    b.verfolgen()                                                                          # lässt sich nicht abschalten
    vorher = len(e.aenderungen())
    b.aenderungenUebernehmen()                                                             # und nicht annehmen
    assert e.verfolgen and len(e.aenderungen()) == vorher and not b.kann("aenderungAnnehmen")
    b.schutz_setzen(t, "lesen")
    assert e.isReadOnly() and t.gesperrt
    b.schutz_setzen(t, None)
    assert not e.isReadOnly() and not b.an_bearbeitungEinschraenken()
    # das Fenster beendet einen stehenden Schutz
    d2 = SchutzDialog(None, "lesen")
    assert d2.ok.text().startswith("Schutz beenden") and d2.ergebnis() is None
