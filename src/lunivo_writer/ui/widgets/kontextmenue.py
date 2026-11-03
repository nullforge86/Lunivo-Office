"""Das Rechtsklick-Menü des Textes, deutsch und in der Reihenfolge der Vorlage: Zwischenablage, Format übertragen, Schriftart, Absatz,
Aufzählung, Hyperlink, Kommentar. Darunter stehen die Punkte, die nur dort etwas bewirken (Bild, markierter Text, KI).

Die Befehle sind dieselben wie im Band (``fenster.befehle``); das Menü hat keine eigene Logik, es ruft sie nur.
"""
from __future__ import annotations

from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QMenu

from lunivo_writer.ui.widgets import icons


def _symbole() -> dict[str, str]:
    from lunivo_writer.ui.widgets.mini_leiste import _symbole as lade
    return lade()


def menue_bauen(editor, fenster) -> QMenu:
    """Das Menü für den Editor ``editor`` des Fensters ``fenster``; der Aufrufer zeigt es und löscht es danach."""
    b = fenster.befehle
    sym = _symbole()
    m = QMenu(editor)
    lesen = editor.isReadOnly()
    auswahl = editor.textCursor().hasSelection()

    def punkt(text: str, tun=None, taste: str = "", icon: str = "", an: bool = True, aktion=None):
        a = m.addAction(text)
        name = icon or (sym.get(tun, "") if isinstance(tun, str) else "")      # icon="-": bewusst ohne Symbol
        if name and icons.hat(name):
            a.setIcon(icons.icon(name, 16))
        if taste:
            a.setShortcut(QKeySequence(taste)); a.setShortcutVisibleInContextMenu(True)
        a.setEnabled(an)
        a.triggered.connect(aktion if aktion is not None else (lambda _=False, t=tun: b.tun(t)))
        return a

    if editor.textCursor().currentTable() is not None:
        _tabellenmenue(m, punkt, b, editor, lesen, auswahl)
        return m

    punkt("Kopieren", "kopieren", "Ctrl+C", "kopie", auswahl)
    punkt("Ausschneiden", "ausschneiden", "Ctrl+X", "schere", auswahl and not lesen)
    punkt("Einfügen", "einfuegen", "Ctrl+V", "kleben", editor.canPaste() and not lesen)
    punkt("Einfügen ohne Formatierung", "einfuegenOhne", "", "", editor.canPaste() and not lesen)
    punkt("Inhalte einfügen …", "inhalteEinfuegen", "Ctrl+Alt+V", "", editor.canPaste() and not lesen)
    m.addSeparator()
    punkt("Format übertragen", "formatUebertragen", "", "pinsel", not lesen)
    m.addSeparator()
    punkt("Schriftart …", "schriftartMehr", "Ctrl+D", "", not lesen)
    punkt("Absatz …", None, "", "absatzlayout", not lesen, aktion=fenster.paragraph_dialog)
    punkt("Aufzählungszeichen und Nummerierung …", None, "", "", not lesen, aktion=lambda: b.listeDialog())
    m.addSeparator()
    punkt("Hyperlink …", "hyperlink", "Ctrl+K", "kette", not lesen)
    punkt("Neuer Kommentar", "kommentar", "", "notiz", not lesen)
    m.addSeparator()
    punkt("Alles auswählen", None, "Ctrl+A", "", True, aktion=editor.selectAll)
    return m


# Nur für das Tabellenmenü: schmalere Zeilen (Symbolspalte, Text, Kürzel dicht); die übrigen Menüs behalten das Standardmaß aus dem Thema.
_TABELLENMENUE_STIL = "QMenu { padding: 3px; } QMenu::item { padding: 5px 14px 5px 6px; } QMenu::icon { padding-left: 2px; }"


def _mit_symbol(aktion, name: str) -> None:
    if name and icons.hat(name):
        aktion.setIcon(icons.icon(name, 16))


def _tabellenmenue(m: QMenu, punkt, b, editor, lesen: bool, auswahl: bool) -> None:
    """Das Menü in einer Tabelle (Reihenfolge der Vorlage): Zwischenablage · Zeilen/Spalten/Zellen · Rahmen, Anpassen, Ausrichtung, Eigenschaften.
    Ohne Symbol (wie in der Vorlage): Tabelle teilen, Rahmen und Schattierung, Automatisch anpassen, Tabelleneigenschaften."""
    m.setStyleSheet(_TABELLENMENUE_STIL)
    frei = editor.canPaste() and not lesen
    punkt("Kopieren", "kopieren", "Ctrl+C", "kopie", auswahl)
    punkt("Ausschneiden", "ausschneiden", "Ctrl+X", "schere", auswahl and not lesen)
    punkt("Einfügen", "einfuegen", "Ctrl+V", "kleben", frei)
    punkt("Inhalte einfügen …", "inhalteEinfuegen", "Ctrl+Alt+V", "inhalteEinfuegen", frei)
    m.addSeparator()
    from lunivo_writer.core.tabellenaktionen import EINFUEGEN, LOESCHEN       # dieselbe Definition wie Band und Mini-Leiste
    for titel, symbol, gruppe in (("Einfügen", "tabelleEinfuegen", EINFUEGEN), ("Löschen", "tabelleLoeschen", LOESCHEN)):
        sub = m.addMenu(titel)
        sub.setEnabled(not lesen)
        _mit_symbol(sub.menuAction(), symbol)
        for a in gruppe:
            _mit_symbol(sub.addAction(a.name, lambda _=False, t=a.befehl: b.tun(t)), a.symbol)
    punkt("Tabelle teilen", "tabelleTabelleTeilen", "", "-", not lesen)
    punkt("Zellen zusammenführen", "tabelleVerbinden", "", "tabelleVerbinden", not lesen)
    punkt("Zellen teilen …", "tabelleTeilen", "", "tabelleTeilen", not lesen)
    m.addSeparator()
    punkt("Rahmen und Schattierung …", "tabelleRahmenSchattierung", "", "-", not lesen)
    quelle = b.menue_tabelleAutoAnpassen()                    # dieselben Einträge wie im Band
    auto = m.addMenu("Automatisch anpassen")
    auto.setEnabled(not lesen)
    auto.addActions(quelle.actions())
    m._auto_quelle = quelle                                   # hält die Aktionen am Leben
    zelle = m.addMenu("Zellausrichtung")
    zelle.setEnabled(not lesen)
    _mit_symbol(zelle.menuAction(), "tabelleZellAusrichtung")
    for eintrag in (("Oben", "zelleOben", "zelleOben"), ("Mittig", "zelleMitte", "zelleMitte"), ("Unten", "zelleUnten", "zelleUnten"), None,
                      ("Links", "zelleLinks", "links"), ("Zentriert", "zelleZentriert", "mitte"), ("Rechts", "zelleRechts", "rechts")):
        if eintrag is None:
            zelle.addSeparator()
        else:
            _mit_symbol(zelle.addAction(eintrag[0], lambda _=False, t=eintrag[1]: b.tun(t)), eintrag[2])
    punkt("Textausrichtung …", "tabelleTextrichtung", "", "tabelleTextrichtung", not lesen)
    punkt("Beschriftung …", "tabelleBeschriftung", "", "tabelleBeschriftung", not lesen)
    punkt("Tabelleneigenschaften …", "tabelleEigenschaften", "", "-", not lesen)
