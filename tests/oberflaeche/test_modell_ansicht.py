"""Ansicht aus dem Kern (``ModellAnsicht``): zeigt das Dokument über Modell, Qt-freien Seitenumbruch und Backend; Tippen, Löschen und Rückgängig laufen über die Sitzung
und stehen danach auch im Textdokument des Editors."""
import importlib
import os

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor
from PySide6.QtTest import QTest

from lunivo_writer.core.editing import Caret
from lunivo_writer.oberflaeche.dokument.ansicht import modell_ansicht
from lunivo_writer.oberflaeche.dokument.dokumentfenster.dokument_bereich import DocumentTab


def _tab(text: str):
    tab = DocumentTab()
    tab.editor.setPlainText(text)
    tab.resize(900, 700)
    tab.set_layout("kern")
    ansicht = tab.widget()
    assert isinstance(ansicht, modell_ansicht.ModellAnsicht)
    return tab, ansicht


def test_document_tab_standardansicht_und_umgebungsrueckfall(app, monkeypatch):
    """Neue Dokumente nutzen standardmäßig die Modellansicht; 0/false erzwingen das Blattlayout."""
    vorher = os.environ.get("LUNIVO_KERN_ANSICHT")
    try:
        monkeypatch.delenv("LUNIVO_KERN_ANSICHT", raising=False)
        importlib.reload(modell_ansicht)
        tab = DocumentTab()
        assert tab.layout_art == "kern"
        assert isinstance(tab.widget(), modell_ansicht.ModellAnsicht)

        for wert in ("0", "false"):
            monkeypatch.setenv("LUNIVO_KERN_ANSICHT", wert)
            importlib.reload(modell_ansicht)
            fallback = DocumentTab()
            assert fallback.layout_art == "blatt"
            assert fallback.widget() is fallback._holder
    finally:
        if vorher is None:
            monkeypatch.delenv("LUNIVO_KERN_ANSICHT", raising=False)
        else:
            monkeypatch.setenv("LUNIVO_KERN_ANSICHT", vorher)
        importlib.reload(modell_ansicht)


def test_tippen_loeschen_rueckgaengig_stehen_im_editor(app):
    tab, a = _tab("Hallo Welt\nZweiter Absatz")
    a.sitzung().setzen(Caret((0, 0), 5))
    QTest.keyClicks(a, " sch")
    a.einfuegen("öne")                                                                          # QTest kann nur ASCII tippen
    assert tab.editor.document().firstBlock().text() == "Hallo schöne Welt"
    QTest.keyClick(a, Qt.Key_Backspace)
    assert tab.editor.document().firstBlock().text() == "Hallo schön Welt"
    QTest.keyClick(a, Qt.Key_Return)
    assert tab.editor.document().blockCount() == 3 and a.sitzung().cursor == Caret((0, 1), 0)
    a.rueckgaengig()
    assert tab.editor.document().blockCount() == 2
    QTest.keyClick(a, Qt.Key_End, Qt.ControlModifier)
    QTest.keyClick(a, Qt.Key_Home, Qt.ShiftModifier)
    assert a.sitzung().text(*a.sitzung().auswahl()) == "Zweiter Absatz"
    QTest.keyClick(a, Qt.Key_Delete)
    assert tab.editor.document().lastBlock().text() == ""


def test_document_tab_liefert_aktuelles_kernmodell_zum_speichern(app):
    tab, ansicht = _tab("Vorher")
    ansicht.einfuegen("Nachher")
    modell = tab.modell_fuer_speichern()
    assert modell.sections[0].content[0].text == "NachherVorher"


def test_klick_setzt_die_schreibmarke_und_die_seite_wird_gezeichnet(app):
    tab, a = _tab("Erster Absatz\nZweiter Absatz")
    tab.show()
    erg = a.ergebnis()
    r = erg.absaetze[(0, 1)].zeilen[0][2]
    blatt = a.blatt(0)
    x = erg.absaetze[(0, 1)].satz.cursor_x(8)
    QTest.mouseClick(a, Qt.LeftButton, Qt.NoModifier, QPointF(blatt.left() + r.x + x + 0.5, blatt.top() + r.y + r.height / 2).toPoint())
    assert a.sitzung().cursor == Caret((0, 1), 8)
    bild = a.grab().toImage()
    mitte = QPointF(blatt.left() + r.x + 2, blatt.top() + r.y + r.height / 2).toPoint()
    farben = {bild.pixelColor(mitte.x() + dx, mitte.y() + dy).name() for dx in range(0, 60) for dy in range(-6, 7)}
    assert QColor("#ffffff").name() in farben and len(farben) > 1                               # Papier und Text darauf
    a.set_zoom(2.0)
    assert a.blatt(0).width() == blatt.width() * 2
    tab.set_layout("blatt")
    assert tab.widget() is tab._holder
