"""Reiter „Überprüfen“ nach Kays Vorlagen ueberpruefen/01–10: Anordnung, Wörter zählen, Markup-Auswahl, Original-Ansicht,
Annehmen der angezeigten Änderungen, Bearbeitung einschränken."""
from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from lunivo_writer.oberflaeche.dokument.bearbeitung.kern_editor import KernCursor

from lunivo_writer.editor.dokument import fassungen

from lunivo_writer.editor.text import statistik


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


def _mit_aenderungen(e, autoren=("Anna", "Bernd")):
    """Text „Alt bleibt.“ und je Autor eine Einfügung; Anna löscht dazu „Alt “."""
    e.insertPlainText("Alt bleibt.")
    e.set_verfolgen(True)
    for a in autoren:
        e.autor = lambda a=a: (a, "")
        c = e.textCursor(); c.movePosition(KernCursor.End); e.setTextCursor(c)
        e.insertPlainText(f" {a}")
    e.autor = lambda: ("Anna", "")
    c = e.textCursor(); c.setPosition(0); c.setPosition(4, KernCursor.KeepAnchor); e.setTextCursor(c)
    QTest.keyClick(e, Qt.Key_Delete)                                                     # verfolgt gelöscht: bleibt als Löschung stehen
    e.set_verfolgen(False)


def test_band_ueberpruefen_wie_vorlage(fenster):
    from lunivo_writer.oberflaeche.band.plan import plan
    from lunivo_writer.oberflaeche.band.band_leiste import lade_register
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






