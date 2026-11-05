"""Flache Reiterleiste: zu schmal heißt Überlaufmenü „…“, nie Rollpfeile oder angeschnittene Reiter."""
from PySide6.QtWidgets import QApplication, QTabWidget, QWidget

from lunivo_writer.ui.baukasten.flache_reiter_leiste import HAUPT, FlacheReiterLeiste, flach_machen

NAMEN = ["KI-Modelle", "Modellzuweisung", "Sprache", "KI-Werkzeuge", "Websuche", "Datenschutz"]


def test_ueberlauf_geht_ins_menue_ohne_rollpfeile(app):
    tw = QTabWidget()
    for n in NAMEN:
        tw.addTab(QWidget(), n)
    leiste = flach_machen(tw, HAUPT)
    tw.resize(300, 200); tw.show(); QApplication.processEvents()
    assert not leiste.usesScrollButtons()
    versteckt = leiste._versteckte()
    assert versteckt and leiste._mehr.isVisible()
    for i in range(leiste.count()):
        if i not in versteckt:
            assert 0 < leiste.tabRect(i).right() <= leiste.width() - 36
    for ziel in range(len(NAMEN)):                     # jeder Reiter ist erreichbar; der aktive ist immer sichtbar
        tw.setCurrentIndex(ziel); QApplication.processEvents()
        assert ziel not in leiste._versteckte()
        assert leiste.tabRect(ziel).right() <= leiste.width()
    frei = FlacheReiterLeiste(HAUPT)                    # genug Platz: alles sichtbar, kein Knopf
    for n in NAMEN:
        frei.addTab(n)
    frei.resize(900, 44); frei.show(); QApplication.processEvents()
    assert not frei._versteckte() and not frei._mehr.isVisible()


def test_mehr_menue_listet_versteckte_und_loest_aus(app, monkeypatch):
    """Die Einträge hinter „•••“ sind genau die versteckten Reiter; ein Eintrag macht den Reiter aktiv und sichtbar."""
    from lunivo_writer.ui.baukasten.menue_liste import MenueListe
    tw = QTabWidget()
    for n in NAMEN:
        tw.addTab(QWidget(), n)
    leiste = flach_machen(tw, HAUPT)
    tw.resize(300, 200); tw.show(); QApplication.processEvents()
    versteckt = leiste._versteckte()
    assert versteckt
    gesehen = {}

    def falsch_exec(self, *_a, **_k):                    # kein echtes Popup: Einträge lesen und den letzten auslösen
        akt = [a for a in self.actions() if not a.isSeparator()]
        gesehen["texte"] = [a.text() for a in akt]
        akt[-1].trigger()
    monkeypatch.setattr(MenueListe, "exec", falsch_exec)
    leiste._mehr_menue(); QApplication.processEvents()
    assert gesehen["texte"] == [NAMEN[i] for i in versteckt]
    ziel = versteckt[-1]
    assert leiste.currentIndex() == ziel and ziel not in leiste._versteckte()
    assert 0 < leiste.tabRect(ziel).right() <= leiste.width()


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
