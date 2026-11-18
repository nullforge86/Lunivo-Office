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

from PySide6.QtCore import QEventLoop, QSettings, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from lunivo_writer.dienste.einstellungen_dienst import Settings  # noqa: E402
from lunivo_writer.oberflaeche.dialoge.optionen import OptionenDialog  # noqa: E402
from lunivo_writer.oberflaeche.programmfenster import MainWindow  # noqa: E402
from lunivo_writer.oberflaeche.thema import apply_theme  # noqa: E402
from lunivo_writer.oberflaeche.bauteile import symbole  # noqa: E402

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
    ini = os.path.join(tempfile.mkdtemp(), "s.ini")
    apply_theme(app, theme)                   # zuerst das Thema, dann das Fenster: Die Symbole übernehmen die Farben beim Bauen
    symbole.leeren()
    w = MainWindow(Settings(QSettings(ini, QSettings.IniFormat)))
    w.resize(*groesse)
    w.show()
    w.new_document()
    ed = w.current_editor()
    ed.textCursor().insertText(text)          # Einfügen statt setPlainText: die Seitenränder bleiben erhalten
    app.processEvents()
    return w


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
    from PySide6.QtGui import QTextCursor
    from lunivo_writer.editor.objekte import frei_objekt as FO
    from lunivo_writer.editor.objekte import smartart as SA
    from lunivo_writer.editor.tabelle import tabellenstil as TS
    from PySide6.QtGui import QTextTableFormat

    w = fenster(app, "light")
    ed = w.current_editor()
    c = QTextCursor(ed.document()); c.setPosition(ed.document().toPlainText().index("Sehr geehrte")); ed.setTextCursor(c)
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
    FO.einfuegen(ed, "form", {**FO.FORM_STANDARD, "form": "Raute"}, 160, 120)      # freies Objekt, gleich gewählt
    FO.aendern(ed, "form", form_fuell="#f4a259", form_linie="#9c4f0a")
    w._sync_format()
    reiter(w, "Zeichentools")
    warte(400)
    foto(w, "qt-formtools.png")
    schliessen(w)

    w = fenster(app, "light", "Quartalszahlen:\n")
    ed = w.current_editor()
    c = ed.textCursor(); c.movePosition(QTextCursor.End)
    ed.setTextCursor(c)
    t = c.insertTable(4, 3, QTextTableFormat())
    for r, zeile in enumerate((("Quartal", "Umsatz", "Kosten"), ("Q1", "120", "80"), ("Q2", "150", "90"), ("Q3", "170", "110"))):
        for k, x in enumerate(zeile):
            t.cellAt(r, k).firstCursorPosition().insertText(x)
    TS.anwenden(t, "Blau")
    ed.setTextCursor(t.cellAt(1, 1).firstCursorPosition())
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
    from PySide6.QtGui import QContextMenuEvent, QPainter, QTextCursor
    from PySide6.QtWidgets import QMenu

    w = fenster(app, "light", "Das Ergebnis ist garnicht schlimm, wenn man es kurz prüft.\n", groesse=(1100, 1050))
    w.sidebar.setVisible(False)
    ed = w.current_editor()
    c = QTextCursor(ed.document())
    c.setPosition(ed.document().toPlainText().index("garnicht") + 8)
    ed.setTextCursor(c)
    w.assistant.pruefen(zaehlen=True)
    warte(1500)                                   # die Prüfung läuft im Hintergrund; erst danach kennt das Menü den Fund
    pos = ed.cursorRect(c).center()

    def aufnehmen():
        bild = w.grab()
        maler = QPainter(bild)
        for top in app.topLevelWidgets():
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
    ed.contextMenuEvent(QContextMenuEvent(QContextMenuEvent.Mouse, pos, ed.mapToGlobal(pos)))
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
