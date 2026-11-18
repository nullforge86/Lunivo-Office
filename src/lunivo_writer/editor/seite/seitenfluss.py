"""Umbruchregeln am Seitenende: „Diesen Absatz zusammenhalten“, „Nicht vom nächsten Absatz trennen“ und die Absatzkontrolle
(keine Schusterjungen und Hurenkinder).

Qt bricht Seiten Zeile für Zeile um und kennt diese Regeln nicht. Darum prüft ``anwenden`` nach dem Setzen des Textes, welche Absätze eine
Regel verletzen, und setzt vor ihnen einen eigenen Seitenumbruch (``PageBreak_AlwaysBefore`` mit der Kennung ``B_AUTOUMBRUCH``). Diese
Umbrüche kommen bei jeder Prüfung neu: erst werden alle alten entfernt, dann die nötigen gesetzt. Sie werden nicht in DOCX geschrieben,
zählen nicht als „Seitenumbruch oberhalb“ des Absatz-Fensters und verändern weder die Änderungsmarke noch den Rückgängig-Verlauf.

Zwei Dinge, auf die sich jede Prüfung hier verlässt:
- Das Layout ist frisch. Innerhalb eines Bearbeitungsblocks setzt Qt den Text nicht neu; darum schließt ``_Schritt.neu_setzen`` den Block
  nach jeder Änderung, lässt setzen und öffnet ihn wieder (weiter als Teil des vorigen Rückgängig-Schritts).
- Die Seitenhöhe ist die, mit der Qt umbricht: die Seitenhöhe des Dokuments (im Editor mit Zoom) im ``umbruchraster``
  (``modelle/seite.py``), siehe ``seitenraster``.
"""
from __future__ import annotations

from PySide6.QtGui import QTextBlockFormat, QTextCursor, QTextFormat

MAX_DURCHGAENGE = 4
OBEN_SPIEL = 1.0                                         # so nah am oberen Rand gilt eine Zeile als „steht ganz oben auf der Seite“


def seitenraster(doc, ch: float) -> float:
    """Die Höhe, in der Qt die Seiten dieses Dokuments umbricht: seine Seitenhöhe (sonst ``ch``), auf 1/64 Bildpunkt abgeschnitten."""
    from lunivo_writer.modelle.seite import umbruchraster
    h = doc.pageSize().height()
    return umbruchraster(h if h > 0 else ch)


def _von_oben(zeile, ch: float) -> float:
    """Abstand einer Zeile (aus ``_zeilen``) vom oberen Rand ihrer Seite."""
    return zeile[1] - zeile[0] * ch


def fertig_setzen(doc) -> None:
    """Setzt das ganze Dokument sofort. Qt setzt sonst in Etappen: Absätze dahinter haben noch keine Zeilen, die Regeln sähen sie nicht,
    und Seitenzahl und Ausgabe brächen dort ab."""
    doc.pageCount()
    doc.documentLayout().documentSize()


class _Schritt:
    """Der Bearbeitungsblock der Prüfung: hängt an den vorigen Rückgängig-Schritt und lässt zwischen den Durchgängen neu setzen."""

    def __init__(self, doc):
        self.doc, self.c = doc, QTextCursor(doc)
        fertig_setzen(doc)                               # vor dem Bearbeitungsblock: darin setzt Qt nur noch den geänderten Teil
        self.c.joinPreviousEditBlock()

    def neu_setzen(self) -> None:
        self.c.endEditBlock()
        fertig_setzen(self.doc)
        self.c.joinPreviousEditBlock()

    def ende(self) -> None:
        self.c.endEditBlock()


def ist_manuell(bf) -> bool:
    """Ein Seitenumbruch oberhalb, den der Benutzer gesetzt hat (kein von Lunivo eingefügter)."""
    from lunivo_writer.editor.dokument.zusatz import B_AUTOUMBRUCH
    return bool(bf.pageBreakPolicy() & QTextFormat.PageBreak_AlwaysBefore) and not bf.hasProperty(B_AUTOUMBRUCH)


def _zeilen(b, ch: float) -> list[tuple[int, float, float]]:
    """(Seite, oben, unten) jeder Zeile des Absatzes."""
    tl = b.layout()
    aus = []
    if tl is None:
        return aus
    for i in range(tl.lineCount()):
        z = tl.lineAt(i)
        y = tl.position().y() + z.y()
        aus.append((int((y + 0.5) // ch), y, y + z.height()))
    return aus


def _hoehe(z) -> float:
    return z[-1][2] - z[0][1]


def _zeilen_auf(z, seite: int) -> int:
    return sum(1 for s, _a, _b in z if s == seite)


def _zerrissen(z, ch: float, w: dict) -> bool:
    """Der Absatz läuft über ein Seitenende, obwohl „zusammenhalten“ oder die Absatzkontrolle das verbietet."""
    erste, letzte = z[0][0], z[-1][0]
    if erste == letzte or _hoehe(z) > ch:                # länger als eine Seite: nicht zu retten
        return False
    if w["zusammen"]:
        return True
    return bool(w["kontrolle"]) and len(z) >= 2 and min(_zeilen_auf(z, erste), _zeilen_auf(z, letzte)) < 2


def _vom_naechsten_getrennt(z, naechster, ch: float, w: dict) -> bool:
    """„Nicht vom nächsten Absatz trennen“: der nächste Absatz beginnt auf einer anderen Seite, als dieser endet."""
    if not w["nicht_trennen"] or naechster is None or not naechster.isValid() or _hoehe(z) > ch:
        return False
    zn = _zeilen(naechster, ch)
    return bool(zn) and zn[0][0] != z[-1][0]


def _verletzt(b, naechster, ch: float, w: dict) -> bool:
    z = _zeilen(b, ch)
    return bool(z) and (_zerrissen(z, ch, w) or _vom_naechsten_getrennt(z, naechster, ch, w))


def _gesetzte(doc):
    """Die sichtbaren Absätze, die schon gesetzt sind (mit Layout)."""
    b = doc.firstBlock()
    while b.isValid():
        if b.isVisible() and b.layout() is not None:
            yield b
        b = b.next()


def _oben_auf_seite(bf, z, ch: float, spiel: float) -> bool:
    """Die erste Zeile steht (bis auf ``spiel``) oben auf einer Folgeseite, die der Textfluss begonnen hat."""
    return z[0][0] >= 1 and _von_oben(z[0], ch) <= spiel and not ist_manuell(bf)


def _vorabstand_pruefen(b, ch: float, zurueck: set) -> bool:
    """Abstand vor einem Absatz: am Seitenanfang wegnehmen (Wert in ``B_VORHER`` merken), sonst zurückgeben. → True, wenn geändert.
    ``zurueck``: Absätze, die ihren Abstand in dieser Prüfung schon zurückbekommen haben. Sie behalten ihn — sonst nähme der nächste Durchgang
    ihn wieder weg (ohne Abstand passt so ein Absatz noch auf die vorige Seite, mit Abstand beginnt er die nächste)."""
    from lunivo_writer.editor.dokument.zusatz import B_VORHER
    bf = b.blockFormat()
    geaendert = False
    hat = bf.hasProperty(B_VORHER)
    if hat and bf.topMargin() > 0.01:                               # der Benutzer hat den Abstand inzwischen selbst geändert: vergessen
        bf.clearProperty(B_VORHER); QTextCursor(b).setBlockFormat(bf); hat, geaendert = False, True
        bf = b.blockFormat()
    soll = bf.doubleProperty(B_VORHER) if hat else bf.topMargin()
    z = _zeilen(b, ch)
    if not z or soll <= 0.01:
        return geaendert
    if not hat and b.blockNumber() not in zurueck and _oben_auf_seite(bf, z, ch, bf.topMargin() + OBEN_SPIEL):
        bf.setProperty(B_VORHER, float(bf.topMargin())); bf.setTopMargin(0.0)
    elif hat and not _oben_auf_seite(bf, z, ch, OBEN_SPIEL):
        bf.setTopMargin(float(bf.doubleProperty(B_VORHER))); bf.clearProperty(B_VORHER)
        zurueck.add(b.blockNumber())
    else:
        return geaendert
    QTextCursor(b).setBlockFormat(bf)
    return True


def _seitenanfang(doc, ch: float, schritt: _Schritt) -> bool:
    """Am Anfang einer Seite, die durch den Textfluss entsteht, entfällt der Abstand vor dem Absatz. Nach einem
    Seitenumbruch, den der Benutzer gesetzt hat, und am Dokumentanfang bleibt er. Der eingestellte Wert steht in ``B_VORHER``."""
    geaendert = False
    zurueck: set[int] = set()
    for _ in range(MAX_DURCHGAENGE + 2):
        if not any([_vorabstand_pruefen(b, ch, zurueck) for b in _gesetzte(doc)]):
            break
        geaendert = True
        schritt.neu_setzen()                                        # der nächste Durchgang prüft, wo die Absätze jetzt stehen
    return geaendert


def _hat_umbruch(b) -> bool:
    return bool(b.blockFormat().pageBreakPolicy() & QTextFormat.PageBreak_AlwaysBefore)


def _alte_umbrueche_entfernen(doc) -> bool:
    from lunivo_writer.editor.dokument.zusatz import B_AUTOUMBRUCH
    entfernt = False
    b = doc.firstBlock()
    while b.isValid():
        if b.blockFormat().hasProperty(B_AUTOUMBRUCH):
            bf = b.blockFormat(); bf.clearProperty(B_AUTOUMBRUCH); bf.setPageBreakPolicy(QTextBlockFormat.PageBreak_Auto)
            QTextCursor(b).setBlockFormat(bf); entfernt = True
        b = b.next()
    return entfernt


def _braucht_umbruch(b, ch: float) -> bool:
    """Der Absatz verletzt eine Umbruchregel und ein Umbruch davor hilft (er hat noch keinen und steht nicht schon ganz oben)."""
    from lunivo_writer.editor.seite import absatzopt
    if not _verletzt(b, b.next(), ch, absatzopt.lesen(b.blockFormat())) or _hat_umbruch(b):
        return False
    z = _zeilen(b, ch)
    return bool(z) and _von_oben(z[0], ch) > OBEN_SPIEL          # steht schon ganz oben auf der Seite: nichts zu gewinnen


def _umbruchstellen(doc, ch: float, weitere) -> list:
    """Absätze, vor die jetzt ein eigener Umbruch gehört: Regelverletzungen und die von ``weitere()`` genannten."""
    neue = [b for b in _gesetzte(doc) if _braucht_umbruch(b, ch)]
    if weitere is None:
        return neue
    schon = {x.blockNumber() for x in neue}
    for x in weitere():
        if x.blockNumber() not in schon and not _hat_umbruch(x):
            neue.append(x); schon.add(x.blockNumber())
    return neue


def _umbrueche_setzen(bloecke) -> None:
    from lunivo_writer.editor.dokument.zusatz import B_AUTOUMBRUCH
    for b in bloecke:
        bf = b.blockFormat(); bf.setPageBreakPolicy(QTextBlockFormat.PageBreak_AlwaysBefore); bf.setProperty(B_AUTOUMBRUCH, 1)
        QTextCursor(b).setBlockFormat(bf)


def anwenden(doc, ch: float, weitere=None) -> bool:
    """Umbruchregeln auf das Dokument anwenden (``ch`` = Höhe der Textfläche einer Seite in Bildpunkten; gilt nur, wenn das Dokument keine
    Seitenhöhe hat, siehe ``seitenraster``). → True, wenn sich etwas geändert hat.
    ``weitere()`` nennt zusätzlich Absätze, vor die ein eigener Umbruch gehört (z. B. ``querblatt.grenzen`` für Blätter anderer Größe)."""
    if ch <= 0:
        return False
    ch = seitenraster(doc, ch)
    war_geaendert = doc.isModified()
    schritt = _Schritt(doc)
    try:
        aenderung = _alte_umbrueche_entfernen(doc)
        if aenderung:
            schritt.neu_setzen()                                    # die Regeln prüfen den Text ohne die alten Umbrüche
        for _ in range(MAX_DURCHGAENGE if weitere is None else 3 * MAX_DURCHGAENGE):
            neue = _umbruchstellen(doc, ch, weitere)
            if not neue:
                break
            _umbrueche_setzen(neue)
            schritt.neu_setzen()
            aenderung = True
        aenderung |= _seitenanfang(doc, ch, schritt)
    finally:
        schritt.ende()
        doc.setModified(war_geaendert)
    return aenderung
