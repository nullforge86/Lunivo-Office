"""Flache Reiterleiste: zu schmal heißt Überlaufmenü „…“, nie Rollpfeile oder angeschnittene Reiter."""
from PySide6.QtWidgets import QApplication, QTabWidget, QWidget

from lunivo_writer.ui.baukasten.flache_reiter_leiste import HAUPT, FlacheReiterLeiste, flach_machen

NAMEN = ["KI-Modelle", "Modellzuweisung", "Sprache", "KI-Werkzeuge", "Websuche", "Datenschutz"]


def test_zu_schmal_zeigt_dropdown_ohne_rollpfeile(app):
    """Passen die Hauptreiter nicht nebeneinander, zeigt die flache Leiste ein Dropdown — nie Rollpfeile oder angeschnittene Reiter."""
    tw = QTabWidget()
    for n in NAMEN:
        tw.addTab(QWidget(), n)
    leiste = flach_machen(tw, HAUPT)
    tw.resize(300, 200); tw.show(); QApplication.processEvents()
    assert not leiste.usesScrollButtons()
    assert leiste._als_dropdown() and leiste._wahl.isVisible()
    for ziel in range(len(NAMEN)):                     # jeder Reiter ist erreichbar; die Taste nennt den aktiven
        tw.setCurrentIndex(ziel); QApplication.processEvents()
        assert leiste._wahl.isVisible() and leiste._wahl.toolTip() == NAMEN[ziel]
    frei = FlacheReiterLeiste(HAUPT)                    # genug Platz: alle Reiter nebeneinander, kein Dropdown
    for n in NAMEN:
        frei.addTab(n)
    frei.resize(900, 44); frei.show(); QApplication.processEvents()
    assert not frei._als_dropdown() and not frei._wahl.isVisible()


def test_dropdown_listet_alle_reiter_und_loest_aus(app):
    """Die Liste des Dropdowns enthält alle sichtbaren Reiter; ein Eintrag macht den Reiter aktiv."""
    tw = QTabWidget()
    for n in NAMEN:
        tw.addTab(QWidget(), n)
    leiste = flach_machen(tw, HAUPT)
    tw.resize(300, 200); tw.show(); QApplication.processEvents()
    assert leiste._als_dropdown()
    leiste._wahl_fuellen()
    akt = [a for a in leiste._wahl_liste.actions() if not a.isSeparator()]
    assert [a.text() for a in akt] == NAMEN
    akt[-1].trigger(); QApplication.processEvents()
    assert leiste.currentIndex() == len(NAMEN) - 1 and leiste._wahl.toolTip() == NAMEN[-1]


def test_ueberlauf_leiste_gewoehnliche_reiter(app):
    """Band-/Dokumentreiter: keine Rollpfeile, nichts angeschnitten, Rest hinter „•••“; gewollte Unsichtbarkeit (Kontext-Reiter) bleibt."""
    from lunivo_writer.ui.baukasten.flache_reiter_leiste import UeberlaufLeiste
    b = UeberlaufLeiste()
    for i in range(8):
        b.addTab(f"Dokument Nummer {i} lang")
    b.setTabVisible(3, False)                             # gewollt unsichtbar
    b.resize(500, 32); b.show(); QApplication.processEvents()
    assert not b.usesScrollButtons() and b._mehr.isVisible()
    assert b.isTabVisible(3) is False and 3 not in b._versteckte()
    for i in range(b.count()):
        if b.gezeigt(i):
            assert 0 <= b.tabRect(i).left() and b.tabRect(i).right() <= b.width() - 36
    b.setCurrentIndex(7); QApplication.processEvents()
    assert b.gezeigt(7) and b.tabRect(7).left() >= 0 and b.tabRect(7).right() <= b.width()
    b.resize(2000, 32); QApplication.processEvents()
    assert not b._versteckte() and not b._mehr.isVisible() and not b.gezeigt(3)


def test_groesse_vor_dem_eintragen_des_reiters_wirft_nicht(app):
    """Wächter: Fragt Qt die Größe, bevor ``tabInserted`` den Reiter in ``_will`` eingetragen hat (Liste kürzer als ``count()``), gibt es keinen IndexError
    (Absturz beim Öffnen der Silben-Einstellungen in der Seitenleiste)."""
    from lunivo_writer.ui.baukasten.flache_reiter_leiste import UeberlaufLeiste
    leiste = UeberlaufLeiste()
    for n in ("Eins", "Zwei", "Drei"):
        leiste.addTab(n)
    leiste._will = leiste._will[:1]                      # Zustand mitten im Einfügen
    leiste.sizeHint(); leiste.minimumSizeHint()
    assert leiste._versteckte() == []
