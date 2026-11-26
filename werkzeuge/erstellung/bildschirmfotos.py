#!/usr/bin/env python3
"""Nimmt die Bilder der Qt-Oberfläche für das README auf (ohne Bildschirm, QT_QPA_PLATFORM=offscreen).

    python3 werkzeuge/erstellung/bildschirmfotos.py            schreibt ressourcen/bilder/qt-*.png und rechtsklick.png
    python3 werkzeuge/erstellung/bildschirmfotos.py --zusatz   nur Abschnitte, SmartArt, Formen, Tabellen, Überprüfen, Rechtsklick
"""
import os
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.dirname(os.path.dirname(HIER))
sys.path.insert(0, os.path.join(WURZEL, "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ZIEL = os.path.join(WURZEL, "ressourcen", "bilder")

# Eigene, leere Einstellungs- und Datenordner: Die Aufnahmen zeigen den Auslieferungszustand und berühren die echten Benutzerdaten nicht.
# Das Programm liest seine Orte aus den XDG-Variablen; sie müssen vor dem ersten Import gesetzt sein.
_ORT = tempfile.mkdtemp(prefix="lunivo-bilder-")
for _variable, _ordner in (("XDG_CONFIG_HOME", "config"), ("XDG_DATA_HOME", "daten"), ("XDG_CACHE_HOME", "cache"), ("XDG_STATE_HOME", "state")):
    os.environ[_variable] = os.path.join(_ORT, _ordner)
    os.makedirs(os.environ[_variable], exist_ok=True)

import framework  # noqa: F401,E402  (meldet dem Kern seine Orte an)
from PySide6.QtCore import QEventLoop, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from vcl.qt.widgets.dialoge.optionen import OptionenDialog  # noqa: E402
from vcl.qt.fenster.fenster.programmfenster import MainWindow  # noqa: E402
from vcl.qt.widgets.bausteine.farben.thema.thema import apply_theme  # noqa: E402
from vcl.qt.widgets.bausteine.symbole.bauteile import symbole  # noqa: E402

BRIEF = """Anna Meyer
Bahnhofstraße 12
50667 Köln

Stadt Köln
Amt für Soziales
Amtsplatz 1
50667 Köln

Köln, 18. Oktober 2026

Widerspruch gegen den Bescheid vom 2. Oktober 2026

Sehr geehrte Damen und Herren,

hiermit wiederspreche ich dem oben genannten Bescheid. Ich bin der Meinung, dass die Berechnung nicht stimmt, weil mein Einkommen falsch angesetzt wurde. Ich bitte Sie deshalb, den Bescheid noch einmal zu prüfen.

Die Unterlagen lege ich bei. Über eine kurze Bestätigung würde ich mich freuen.

Mit freundlichen Grüßen

Anna Meyer
"""

LANG = ("Die Schreibhilfe sitzt fest an der Seite und sucht die Fehler, die ein Rechtschreibprüfer nicht finden kann. "
        "Sie arbeitet ohne Internet, und sie meldet sich nur dort, wo sie sich sicher ist. ") * 14


def warte(ms):
    schleife = QEventLoop()
    QTimer.singleShot(ms, schleife.quit)
    schleife.exec()


def fenster(app, theme, text=BRIEF, groesse=(1500, 900)):
    apply_theme(app, theme)                   # zuerst das Thema, dann das Fenster: Die Symbole übernehmen die Farben beim Bauen
    symbole.leeren()
    w = MainWindow()
    w.resize(*groesse)
    w.show()
    w.new_document()
    ed = w.current_editor()
    ed.insertPlainText(text)                  # über den Bearbeitungsweg des Programms: die Seitenränder bleiben erhalten
    app.processEvents()
    return w


def marke(ed, stelle):
    """Die Schreibmarke an die Zeichenstelle ``stelle`` setzen (ohne Auswahl)."""
    ed.select_range(stelle, stelle)


def schliessen(w):
    """Ohne Änderungsmarke schließen, sonst fragt das Fenster nach dem Speichern."""
    for t in w._doc_tabs():
        t.editor.document().setModified(False)
    w.close()


def foto(w, name):
    app = QApplication.instance()
    app.processEvents()
    pfad = os.path.join(ZIEL, name)
    w.grab().save(pfad)
    print("geschrieben:", pfad)


def reiter(w, name):
    r = w.band.reiter
    r.setCurrentIndex(next(i for i in range(r.count()) if r.tabText(i) == name and r.isTabVisible(i)))


def main():
    app = QApplication.instance() or QApplication([])
    os.makedirs(ZIEL, exist_ok=True)
    for theme, suffix in (("light", ""), ("dark", "-dunkel")):
        w = fenster(app, theme)
        reiter(w, "Start")
        w.sidebar.setVisible(True)
        warte(1500)
        foto(w, f"qt-uebersicht{suffix}.png")
        reiter(w, "Schreibhilfe")
        warte(200)
        foto(w, f"qt-schreibhilfe{suffix}.png")
        w.backstage_oeffnen("info")
        warte(200)
        foto(w, f"qt-datei{suffix}.png")
        w.backstage_zu()
        schliessen(w)
    w = fenster(app, "light", LANG)
    w.befehle.tun("spaltenSetzen:[2]") if w.befehle.hat("spaltenSetzen") else None
    reiter(w, "Seitenlayout")
    warte(600)
    foto(w, "qt-spalten.png")
    schliessen(w)
    for seite, name in (("lesehilfe", "qt-optionen-lesehilfe.png"), ("schriften", "qt-optionen-schriften.png")):
        w = fenster(app, "light")
        d = OptionenDialog(w, seite)
        d.resize(1100, 760)
        d.show()
        warte(300)
        d.grab().save(os.path.join(ZIEL, name))
        print("geschrieben:", os.path.join(ZIEL, name))
        d.close()
        schliessen(w)


def zusatzbilder(app):
    """Abschnitte, SmartArt, Form- und Tabellenwerkzeuge, Überprüfen (Vergleichen)."""
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent
    from vcl.qt.rendering.formen import frei_objekt_aendern
    from vcl.qt.rendering.smartart import smartart as SA

    w = fenster(app, "light")
    w.sidebar.setVisible(False)                                                   # Platz für das Querformat des zweiten Abschnitts
    ed = w.current_editor()
    marke(ed, ed.toPlainText().index("Sehr geehrte"))
    w.befehle.tun('abschnittsumbruch:["NextPage"]')
    ps = ed.abschnitt_seite(); ps.set_orientation(True); ed.page_settings_changed(ps)
    reiter(w, "Abschnitt")
    warte(400)
    foto(w, "qt-abschnitte.png")
    schliessen(w)

    w = fenster(app, "light", "Unser Vorgehen in vier Schritten:\n")
    ed = w.current_editor()
    SA.einfuegen(ed, {"layout": "Prozess", "farben": "Blau", "text": "Planen\nUmsetzen\nPrüfen\nAbschließen"})   # freies Objekt, gleich gewählt
    w._sync_format()
    reiter(w, "SmartArt-Design")
    warte(400)
    foto(w, "qt-smartart.png")
    schliessen(w)

    w = fenster(app, "light", "Formen im Text:\n")
    ed = w.current_editor()
    w.befehle.tun('formEinfuegen:["Raute"]')                                      # freies Objekt, gleich gewählt
    frei_objekt_aendern(ed, "form", form_fuell="#f4a259", form_linie="#9c4f0a")
    w._sync_format()
    reiter(w, "Zeichentools")
    warte(400)
    foto(w, "qt-formtools.png")
    schliessen(w)

    w = fenster(app, "light", "Quartalszahlen:\n")
    ed = w.current_editor()
    ed.insert_table(4, 3)                                                         # die Schreibmarke steht danach in der ersten Zelle
    zellen = [x for zeile in (("Quartal", "Umsatz", "Kosten"), ("Q1", "120", "80"), ("Q2", "150", "90"), ("Q3", "170", "110")) for x in zeile]
    for nr, x in enumerate(zellen):
        if nr:                                                                    # mit der Tabulatortaste in die nächste Zelle, wie am Bildschirm
            app.sendEvent(ed.ansicht, QKeyEvent(QEvent.KeyPress, Qt.Key_Tab, Qt.NoModifier))
        ed.insertPlainText(x)
    ed.tabelle_vorlage_anwenden("Blau", True, True, False)
    w._sync_format()
    reiter(w, "Tabellentools")
    warte(400)
    foto(w, "qt-tabellentools.png")
    schliessen(w)

    w = fenster(app, "light")
    reiter(w, "Überprüfen")
    warte(300)
    foto(w, "qt-ueberpruefen.png")
    schliessen(w)


def rechtsklick(app):
    """Rechtsklick auf „garnicht“: Menü samt schwebender Formatleiste, in das Fenster hineingemalt."""
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtGui import QContextMenuEvent, QPainter
    from PySide6.QtWidgets import QMenu

    w = fenster(app, "light", "Das Ergebnis ist garnicht schlimm, wenn man es kurz prüft.\n", groesse=(1100, 1050))
    w.sidebar.setVisible(False)
    ed = w.current_editor()
    marke(ed, ed.toPlainText().index("garnicht") + 8)
    warte(1500)                                   # erst die Prüfung beim Schreiben auslaufen lassen: solange sie läuft, wird „Prüfen“ nur vorgemerkt
    w.assistant.pruefen(zaehlen=True)
    warte(2500)                                   # die Prüfung läuft im Hintergrund; erst danach kennt das Menü den Fund
    pos = ed.cursorRect().center()

    def aufnehmen():
        bild = w.grab()
        maler = QPainter(bild)
        for top in sorted(app.topLevelWidgets(), key=lambda t: isinstance(t, QMenu)):      # das Menü zuletzt: es liegt über der Formatleiste
            if top is not w and top.isVisible() and top.windowFlags() & (Qt.Popup | Qt.ToolTip | Qt.Tool | Qt.FramelessWindowHint):
                maler.drawPixmap(w.mapFromGlobal(top.pos()), top.grab())
        maler.end()
        pfad = os.path.join(ZIEL, "rechtsklick.png")
        bild.save(pfad)
        print("geschrieben:", pfad)
        for m in app.allWidgets():
            if isinstance(m, QMenu) and m.isVisible():
                m.close()

    QTimer.singleShot(800, aufnehmen)
    ed.ansicht.contextMenuEvent(QContextMenuEvent(QContextMenuEvent.Mouse, pos, ed.ansicht.mapToGlobal(pos)))
    schliessen(w)


if __name__ == "__main__":
    app = QApplication.instance() or QApplication([])
    if "--zusatz" in sys.argv:                    # nur die Bilder der Zusatzfunktionen und des Rechtsklicks (ohne die Übersichten)
        zusatzbilder(app)
        rechtsklick(app)
    else:
        main()
        zusatzbilder(QApplication.instance())
        rechtsklick(QApplication.instance())
