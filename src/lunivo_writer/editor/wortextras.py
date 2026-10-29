"""Wort-Extras: Absätze aufräumen — über die Markierung, ohne Markierung über das ganze Dokument. Jede Handlung ist ein Schritt für Rückgängig.

Texte in Tabellen bleiben unberührt; leere Absätze, Bilder und Zeilenumbrüche werden dort gesucht, wo sie im Fließtext stehen."""
from __future__ import annotations

from PySide6.QtGui import QTextCursor

ZEILENUMBRUCH = " "
SATZENDE = tuple(".!?:;…\"“”»«)")


def _bloecke(ed) -> list:
    """Die Absätze der Markierung (ohne Markierung: alle) außerhalb von Tabellen, in Dokumentreihenfolge."""
    doc = ed.document()
    c = ed.textCursor()
    if c.hasSelection():
        b, ende = doc.findBlock(c.selectionStart()), doc.findBlock(c.selectionEnd()).blockNumber()
    else:
        b, ende = doc.firstBlock(), doc.blockCount()
    out = []
    while b.isValid() and b.blockNumber() <= ende:
        if QTextCursor(b).currentTable() is None:
            out.append(b)
        b = b.next()
    return out


def _leer(b) -> bool:
    """Ein Absatz ohne Zeichen und ohne Bild."""
    return b.length() <= 1


def _schritt(ed, arbeit) -> int:
    """Führt ``arbeit(doc, bloecke)`` als einen Rückgängig-Schritt aus. → Zahl der Änderungen."""
    c = QTextCursor(ed.document())
    c.beginEditBlock()
    try:
        return arbeit(ed.document(), _bloecke(ed)) or 0
    finally:
        c.endEditBlock()


def leere_loeschen(ed) -> int:
    def arbeit(doc, bloecke):
        n = 0
        for b in reversed(bloecke):
            if _leer(b) and b.next().isValid():
                c = QTextCursor(b); c.movePosition(QTextCursor.NextBlock, QTextCursor.KeepAnchor); c.removeSelectedText(); n += 1
        return n
    return _schritt(ed, arbeit)


def leere_einfuegen(ed) -> int:
    def arbeit(doc, bloecke):
        n = 0
        for b in reversed(bloecke):
            nxt = b.next()
            if not _leer(b) and nxt.isValid() and not _leer(nxt) and QTextCursor(nxt).currentTable() is None:
                c = QTextCursor(b); c.movePosition(QTextCursor.EndOfBlock); c.insertBlock(); n += 1
        return n
    return _schritt(ed, arbeit)


def zeilenumbruch_in_return(ed) -> int:
    def arbeit(doc, bloecke):
        n = 0
        for b in reversed(bloecke):
            while (i := b.text().rfind(ZEILENUMBRUCH)) >= 0:
                c = QTextCursor(doc); c.setPosition(b.position() + i); c.setPosition(b.position() + i + 1, QTextCursor.KeepAnchor)
                c.removeSelectedText(); c.insertBlock(); n += 1
                b = doc.findBlock(b.position())
        return n
    return _schritt(ed, arbeit)


def absaetze_neu_anordnen(ed) -> int:
    """Absätze, die mitten im Satz enden (hartes Return in einem Satz, etwa aus PDF-Text), werden zu einem Absatz."""
    def arbeit(doc, bloecke):
        n = 0
        for b in reversed(bloecke):
            nxt = b.next()
            t = b.text().rstrip()
            if t and not t.endswith(SATZENDE) and nxt.isValid() and nxt.text().strip() and QTextCursor(nxt).currentTable() is None \
                    and not b.textList() and not nxt.textList() and b.blockFormat().headingLevel() == 0:
                c = QTextCursor(b); c.movePosition(QTextCursor.EndOfBlock); c.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
                c.insertText(" "); n += 1
        return n
    return _schritt(ed, arbeit)


def leerzeichen_bereinigen(ed) -> int:
    """Doppelte Leerzeichen und Leerzeichen am Anfang und Ende der Absätze entfernen."""
    import re

    def arbeit(doc, bloecke):
        n = 0
        for b in reversed(bloecke):
            t = b.text()
            for m in reversed(list(re.finditer(r"^[ \t]+|[ \t]+$|(?<=\S)[ ]{2,}", t))):
                a, e = m.start(), m.end()
                c = QTextCursor(doc); c.setPosition(b.position() + a); c.setPosition(b.position() + e, QTextCursor.KeepAnchor)
                if m.group().strip() == "" and a > 0 and e < len(t):          # mitten im Satz bleibt ein Leerzeichen
                    c.setPosition(b.position() + a + 1)
                    c.setPosition(b.position() + e, QTextCursor.KeepAnchor)
                c.removeSelectedText(); n += 1
        return n
    return _schritt(ed, arbeit)


def einzug_zwei_zeichen(ed) -> int:
    """Erstzeileneinzug um zwei Zeichen der Schriftgröße des Absatzes."""
    def arbeit(doc, bloecke):
        n = 0
        for b in bloecke:
            if _leer(b) or b.textList():
                continue
            pt = b.charFormat().fontPointSize() or doc.defaultFont().pointSizeF() or 11.0
            bf = b.blockFormat(); bf.setTextIndent(2 * pt * 96 / 72)
            QTextCursor(b).setBlockFormat(bf); n += 1
        return n
    return _schritt(ed, arbeit)


def smart_anordnen(ed) -> int:
    """Leerzeichen bereinigen, leere Absätze löschen, Erstzeileneinzug um zwei Zeichen."""
    c = QTextCursor(ed.document())
    c.beginEditBlock()                                               # die drei Schritte sind zusammen ein Schritt für Rückgängig
    try:
        return leerzeichen_bereinigen(ed) + leere_loeschen(ed) + einzug_zwei_zeichen(ed)
    finally:
        c.endEditBlock()


def fuehrende_leerzeichen_loeschen(ed) -> int:
    """Leerzeichen und Tabs am Anfang der Absätze entfernen."""
    def arbeit(doc, bloecke):
        n = 0
        for b in reversed(bloecke):
            t = b.text()
            k = len(t) - len(t.lstrip(" \t\u00a0\u3000"))
            if k and t.strip():
                c = QTextCursor(doc); c.setPosition(b.position()); c.setPosition(b.position() + k, QTextCursor.KeepAnchor)
                c.removeSelectedText(); n += 1
        return n
    return _schritt(ed, arbeit)


def zeilenumbrueche_loeschen(ed) -> int:
    """Manuelle Zeilenumbrüche (Umschalt+Enter) entfernen; die Zeilen laufen zusammen, zwischen zwei Wörtern bleibt ein Leerzeichen."""
    def arbeit(doc, bloecke):
        n = 0
        for b in reversed(bloecke):
            while (i := b.text().rfind(ZEILENUMBRUCH)) >= 0:
                t = b.text()
                luecke = 0 < i < len(t) - 1 and not t[i - 1].isspace() and not t[i + 1].isspace()
                c = QTextCursor(doc); c.setPosition(b.position() + i); c.setPosition(b.position() + i + 1, QTextCursor.KeepAnchor)
                c.insertText(" " if luecke else ""); n += 1
                b = doc.findBlock(b.position())
        return n
    return _schritt(ed, arbeit)


def leerabsatz_modus_wechseln(ed) -> int:
    """Trennung durch leere Absätze umschalten: Stehen zwischen den Absätzen leere Absätze, verschwinden sie; sonst kommt zwischen
    je zwei Absätze einer."""
    bloecke = _bloecke(ed)
    zwischen = any(_leer(b) and b.previous().isValid() and not _leer(b.previous()) and b.next().isValid() and not _leer(b.next())
                   for b in bloecke)
    return leere_loeschen(ed) if zwischen else leere_einfuegen(ed)


def einzug_in_leerzeichen(ed) -> int:
    """Den Erstzeileneinzug eines Absatzes in Leerzeichen am Absatzanfang umwandeln (gleich breit), der Einzug selbst wird 0."""
    from PySide6.QtGui import QFontMetricsF

    def arbeit(doc, bloecke):
        n = 0
        for b in bloecke:
            bf = b.blockFormat()
            if bf.textIndent() <= 0 or _leer(b):
                continue
            c = QTextCursor(b)
            c.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
            breite = QFontMetricsF(c.charFormat().font()).horizontalAdvance(" ") or 4.0
            anzahl = max(1, round(bf.textIndent() / breite))
            bf.setTextIndent(0); QTextCursor(b).setBlockFormat(bf)
            c = QTextCursor(b); c.insertText(" " * anzahl); n += 1
        return n
    return _schritt(ed, arbeit)


# Das Menü am Knopf „Wort-Extras“ in der Anordnung der Vorlage: (Text, Symbol, Funktion), "-" = Trennlinie,
# („Löschen“, Symbol, [Untereinträge]) = Untermenü
MENUE = [("Absätze neu anordnen", "weNeu", absaetze_neu_anordnen),
         ("Smart-Anordnen", "weSmart", smart_anordnen),
         ("Leerabsatz-Trennung umschalten", "weLeerModus", leerabsatz_modus_wechseln),
         "-",
         ("Löschen", "weLoeschen", [("Leere Absätze löschen", "weLeerWeg", leere_loeschen),
                                    ("Führende Leerzeichen löschen", "weFuehrend", fuehrende_leerzeichen_loeschen),
                                    ("Leerzeichen löschen", "weLeerz", leerzeichen_bereinigen),
                                    ("Zeilenumbrüche löschen", "weZeilenWeg", zeilenumbrueche_loeschen)]),
         ("Zeilenumbruch in Absatzmarke umwandeln", "weReturn", zeilenumbruch_in_return),
         "-",
         ("Absatzeinzug um 2 Zeichen", "weEinzug", einzug_zwei_zeichen),
         ("Absatzeinzug in Leerzeichen umwandeln", "weEinzugLeer", einzug_in_leerzeichen),
         ("Leere Absätze einfügen", "weLeerEin", leere_einfuegen)]
