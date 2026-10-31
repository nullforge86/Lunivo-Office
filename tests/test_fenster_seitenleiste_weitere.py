"""Weitere Fenster öffnen in der rechten Seitenleiste (``PanelFaehig``) und passen dort in die Breite: Oberfläche (Register, Symbole,
Benutzeroberfläche), Lesehilfe, „Welche Hilfe wann“, die kleinen Abfragen (``EingabeFenster``), Diagrammdaten, Tabelleneigenschaften,
Bild zuschneiden (Kay, 2026-10-28: Fenster nicht mehr frei, sondern in der Seitenleiste, nach Funktion im Reiter)."""
from __future__ import annotations

import pytest
from PySide6.QtCore import QSettings, QTimer
from PySide6.QtWidgets import QApplication, QDialog, QTabWidget, QWidget

from lunivo_writer.services.settings_service import Settings
from lunivo_writer.ui.baukasten.eingabe_fenster import EingabeFenster
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig, ZusatzPanel
from lunivo_writer.ui.main_window import MainWindow


def _settings(tmp_path):
    return Settings(QSettings(str(tmp_path / "s.ini"), QSettings.IniFormat))


def _hauptfenster(tmp_path):
    w = MainWindow(_settings(tmp_path)); w.new_document()
    return w


def _daten():
    from lunivo_writer.ui.ribbon.ribbon_bar import lade_register
    return lade_register()


def _o():
    from lunivo_writer.ui.dialogs import oberflaeche_dialoge as O
    return O


FENSTER = {
    # Reiter Ansicht
    "Register anpassen": lambda tp: _o().RegisterAnpassenDialog(None, _settings(tp), _daten()),
    "Schnellzugriff": lambda tp: _o().SchnellzugriffDialog(None, _settings(tp), __import__("lunivo_writer.ui.ribbon.ribbon_bar", fromlist=["x"]).RegisterBand.SCHNELL_ALLE, []),
    "Symbol austauschen": lambda tp: _o().SymbolTauschenDialog(None, _settings(tp)),
    "Eigene Zeichnung": lambda tp: _o().EigeneZeichnungDialog(None),
    "Benutzeroberfläche": lambda tp: _o().OberflaecheDialog(None, _settings(tp)),
    # Reiter Schreibhilfe
    "Lesehilfe": lambda tp: __import__("lunivo_writer.ui.dialogs.lesehilfe_dialog", fromlist=["x"]).LesehilfeDialog(_hauptfenster(tp)),
    "Welche Hilfe wann": lambda tp: __import__("lunivo_writer.ui.dialogs.welche_hilfe", fromlist=["x"]).HilfeWannDialog(_hauptfenster(tp)),
    # kleine Abfragen (Sprache, Seriendruckfeld, Adressblock, Zitierweise, Zitat, Inhalte einfügen)
    "Abfrage Auswahl": lambda tp: EingabeFenster(None, "Sprache für die Korrekturhilfen", "Sprache des Dokuments (wird in der Datei vermerkt).\n"
                                                 "Die Schreibhilfe selbst prüft weiter auf Deutsch.",
                                                 ["Deutsch", "Deutsch (Österreich)", "Deutsch (Schweiz)", "Englisch", "Englisch (UK)", "Französisch"], 0),
    "Abfrage Text": lambda tp: EingabeFenster(None, "Seriendruckfeld", "Feldname (muss in der Kopfzeile der Empfängerliste stehen):", None, text="Name"),
    # Einfügen, Tabelle, Bild
    "Diagrammdaten": lambda tp: __import__("lunivo_writer.ui.dialogs.einfuegen_dialoge", fromlist=["x"]).DiagrammDatenDialog(
        None, "Titel", ["A", "B", "C"], {"Reihe 1": [1.0, 2.0, 3.0], "Reihe 2": [2.0, 1.0, 4.0]}),
    "Tabelleneigenschaften": lambda tp: __import__("lunivo_writer.ui.dialogs.dokument_dialoge", fromlist=["x"]).TabellenEigenschaftenDialog(None, 100, 0, 1.0, 4.0, True),
    "Bild zuschneiden": lambda tp: __import__("lunivo_writer.ui.dialogs.dokument_dialoge", fromlist=["x"]).BildZuschneidenDialog(None),
}


@pytest.mark.parametrize("breite", [444, 300])
@pytest.mark.parametrize("name", list(FENSTER))
def test_weitere_fenster_in_der_seitenleiste_und_passen(app, tmp_path, name, breite):
    """Jedes Fenster ist ``PanelFaehig`` und ragt auch bei 300 px (schmalste Seitenleiste) nirgends links oder rechts hinaus."""
    p = ZusatzPanel(); p.verfuegbar, p.verfuegbar_hoehe = breite, 587; p.resize(breite + 36, 727)
    d = FENSTER[name](tmp_path)
    assert isinstance(d, PanelFaehig), name
    p.oeffne(d); p.show(); app.processEvents(); app.processEvents()
    reiter = [w for w in d.findChildren(QTabWidget)]
    seiten = max([r.count() for r in reiter], default=1)
    for i in range(seiten):
        for r in reiter:
            if i < r.count():
                r.setCurrentIndex(i)
        app.processEvents(); app.processEvents()
        vp = p.stapel.currentWidget().sa.viewport()
        zu = [type(c).__name__ for c in d.findChildren(QWidget) if c.isVisible() and c.width() > 0
              and (c.mapTo(vp, c.rect().topLeft()).x() < -1 or c.mapTo(vp, c.rect().topRight()).x() > vp.width())]
        assert not zu, (name, breite, i, zu)
    p.close()


def _in_der_seitenleiste_bestaetigen(app, w, aktion):
    """Wartet, bis ein Fenster als Seite in der Seitenleiste steht (nicht frei), und ruft ``aktion(dialog)``; danach „OK“."""
    gesehen = {}

    def lauf():
        z = getattr(w.sidebar, "_zusatz", None)
        if z is None or not z._seiten:
            return
        d = z._seiten[-1][0]
        gesehen["titel"] = d.windowTitle()
        gesehen["frei"] = any(t is d for t in QApplication.topLevelWidgets() if t.isVisible())
        aktion(d)
        d.accept()
    uhr = QTimer(); uhr.setSingleShot(True); uhr.setInterval(80); uhr.timeout.connect(lauf); uhr.start()
    return gesehen, uhr


def test_zitierweise_oeffnet_in_der_seitenleiste_und_wirkt(app, tmp_path):
    from lunivo_writer.editor.literatur import ZITIERWEISEN
    w = _hauptfenster(tmp_path); w.resize(1380, 860); w.show()
    ziel = [z for z in ZITIERWEISEN if z != w.current_editor().zitierweise][0]
    gesehen, _uhr = _in_der_seitenleiste_bestaetigen(app, w, lambda d: d.liste.setCurrentRow(ZITIERWEISEN.index(ziel)))
    w.befehle.zitierweise()
    assert gesehen == {"titel": "Zitierweise", "frei": False}
    assert w.current_editor().zitierweise == ziel
    w.current_editor().document().setModified(False); w.close()


def test_seriendruckfeld_abfrage_in_der_seitenleiste(app, tmp_path):
    w = _hauptfenster(tmp_path); w.resize(1380, 860); w.show()
    gesehen, _uhr = _in_der_seitenleiste_bestaetigen(app, w, lambda d: d.feld.setText("Ort"))
    w.befehle.seriendruckfeld()
    assert gesehen == {"titel": "Seriendruckfeld", "frei": False}
    assert "Ort" in w.current_editor().toPlainText()
    w.current_editor().document().setModified(False); w.close()


def test_abbrechen_gibt_nichts_zurueck(app, tmp_path):
    w = _hauptfenster(tmp_path); w.resize(1380, 860); w.show()
    uhr = QTimer(); uhr.setSingleShot(True); uhr.setInterval(80)
    uhr.timeout.connect(lambda: w.sidebar._zusatz._seiten[-1][0].reject()); uhr.start()
    assert EingabeFenster.getItem(w, "Test", "Frage:", ["a", "b"], 1) == ("", False)
    w.close()


def test_tabelle_eigenschaften_und_bild_zuschneiden_werte(app):
    from lunivo_writer.ui.dialogs.dokument_dialoge import BildZuschneidenDialog, TabellenEigenschaftenDialog
    t = TabellenEigenschaftenDialog(None, 80, 1, 0.5, 3.0, False)
    assert (t.breite.value(), t.ausr.currentIndex(), t.rand.value(), t.pad.value(), t.kopf.isChecked()) == (80, 1, 0.5, 3.0, False)
    b = BildZuschneidenDialog(None)
    b.felder["Oben"].setValue(7); b.felder["Unten"].setValue(2)
    assert b.werte() == (0, 7, 0, 2)
    assert isinstance(b, QDialog)
