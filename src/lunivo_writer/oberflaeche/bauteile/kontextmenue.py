"""Das Rechtsklick-Menü des Textes, deutsch und in der Reihenfolge der Vorlage: Zwischenablage, Format übertragen, Schriftart, Absatz,
Aufzählung, Hyperlink, Kommentar. Darunter stehen die Punkte, die nur dort etwas bewirken (Bild, markierter Text, KI).

Die Befehle sind dieselben wie im Band (``fenster.befehle``); das Menü hat keine eigene Logik, es ruft sie nur.
"""
from __future__ import annotations

from PySide6.QtGui import QKeySequence
from lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste import MenueListe

from lunivo_writer.oberflaeche.bauteile import symbole
from lunivo_writer.oberflaeche.baukasten.basis.mass import ICON_NORMAL


def _symbole() -> dict[str, str]:
    from lunivo_writer.oberflaeche.bauteile.mini_leiste import _symbole as lade
    return lade()


def menue_bauen(editor, fenster) -> MenueListe:
    """Das Menü für den Editor ``editor`` des Fensters ``fenster``; der Aufrufer zeigt es und löscht es danach."""
    b = fenster.befehle
    sym = _symbole()
    m = MenueListe(editor)
    lesen = editor.isReadOnly()
    auswahl = editor.textCursor().hasSelection()

    def punkt(text: str, tun=None, taste: str = "", icon: str = "", an: bool = True, aktion=None):
        name = icon or (sym.get(tun, "") if isinstance(tun, str) else "")      # icon="-": bewusst ohne Symbol
        return m.eintrag(text, aktion if aktion is not None else (lambda t=tun: b.tun(t)),
                         symbol=symbole.icon(name, ICON_NORMAL) if name and symbole.hat(name) else None,
                         kuerzel=QKeySequence(taste) if taste else "", echt=True, aktiv=an)

    if editor.textCursor().currentTable() is not None:
        _tabellenmenue(m, punkt, b, editor, lesen, auswahl)
        return m

    punkt("Kopieren", "kopieren", "Ctrl+C", "kopie", auswahl)
    punkt("Ausschneiden", "ausschneiden", "Ctrl+X", "schere", auswahl and not lesen)
    punkt("Einfügen", "einfuegen", "Ctrl+V", "kleben", editor.canPaste() and not lesen)
    punkt("Einfügen ohne Formatierung", "einfuegenOhne", "", "", editor.canPaste() and not lesen)
    punkt("Inhalte einfügen …", "inhalteEinfuegen", "Ctrl+Alt+V", "", editor.canPaste() and not lesen)
    m.trenner()
    punkt("Format übertragen", "formatUebertragen", "", "pinsel", not lesen)
    m.trenner()
    punkt("Schriftart …", "schriftartMehr", "Ctrl+D", "", not lesen)
    punkt("Absatz …", None, "", "absatzlayout", not lesen, aktion=fenster.paragraph_dialog)
    punkt("Aufzählungszeichen und Nummerierung …", None, "", "", not lesen, aktion=lambda: b.listeDialog())
    m.trenner()
    punkt("Hyperlink …", "hyperlink", "Ctrl+K", "kette", not lesen)
    punkt("Neuer Kommentar", "kommentar", "", "notiz", not lesen)
    m.trenner()
    punkt("Alles auswählen", None, "Ctrl+A", "", True, aktion=editor.selectAll)
    return m


def _symbol(name: str):
    return symbole.icon(name, ICON_NORMAL) if name and symbole.hat(name) else None


def _tabellenmenue(m: MenueListe, punkt, b, editor, lesen: bool, auswahl: bool) -> None:
    """Das Menü in einer Tabelle (Reihenfolge der Vorlage): Zwischenablage · Zeilen/Spalten/Zellen · Rahmen, Anpassen, Ausrichtung, Eigenschaften.
    Ohne Symbol (wie in der Vorlage): Tabelle teilen, Rahmen und Schattierung, Automatisch anpassen, Tabelleneigenschaften."""
    m.kompakt()
    frei = editor.canPaste() and not lesen
    punkt("Kopieren", "kopieren", "Ctrl+C", "kopie", auswahl)
    punkt("Ausschneiden", "ausschneiden", "Ctrl+X", "schere", auswahl and not lesen)
    punkt("Einfügen", "einfuegen", "Ctrl+V", "kleben", frei)
    punkt("Inhalte einfügen …", "inhalteEinfuegen", "Ctrl+Alt+V", "inhalteEinfuegen", frei)
    m.trenner()
    from lunivo_writer.kern.tabellenaktionen import EINFUEGEN, LOESCHEN       # dieselbe Definition wie Band und Mini-Leiste
    for titel, symbol, gruppe in (("Einfügen", "tabelleEinfuegen", EINFUEGEN), ("Löschen", "tabelleLoeschen", LOESCHEN)):
        sub = m.untermenue(titel, _symbol(symbol), not lesen)
        for a in gruppe:
            sub.eintrag(a.name, lambda t=a.befehl: b.tun(t), symbol=_symbol(a.symbol))
    punkt("Tabelle teilen", "tabelleTabelleTeilen", "", "-", not lesen)
    punkt("Zellen zusammenführen", "tabelleVerbinden", "", "tabelleVerbinden", not lesen)
    punkt("Zellen teilen …", "tabelleTeilen", "", "tabelleTeilen", not lesen)
    m.trenner()
    punkt("Rahmen und Schattierung …", "tabelleRahmenSchattierung", "", "-", not lesen)
    quelle = b.menue_tabelleAutoAnpassen()                    # dieselben Einträge wie im Band
    auto = m.untermenue("Automatisch anpassen", aktiv=not lesen)
    for a in quelle.actions():
        auto.vorhanden(a)
    m._auto_quelle = quelle                                   # hält die Aktionen am Leben
    zelle = m.untermenue("Zellausrichtung", _symbol("tabelleZellAusrichtung"), not lesen)
    for eintrag in (("Oben", "zelleOben", "zelleOben"), ("Mittig", "zelleMitte", "zelleMitte"), ("Unten", "zelleUnten", "zelleUnten"), None,
                      ("Links", "zelleLinks", "links"), ("Zentriert", "zelleZentriert", "mitte"), ("Rechts", "zelleRechts", "rechts")):
        if eintrag is None:
            zelle.trenner()
        else:
            zelle.eintrag(eintrag[0], lambda t=eintrag[1]: b.tun(t), symbol=_symbol(eintrag[2]))
    punkt("Textausrichtung …", "tabelleTextrichtung", "", "tabelleTextrichtung", not lesen)
    punkt("Beschriftung …", "tabelleBeschriftung", "", "tabelleBeschriftung", not lesen)
    punkt("Tabelleneigenschaften …", "tabelleEigenschaften", "", "-", not lesen)
