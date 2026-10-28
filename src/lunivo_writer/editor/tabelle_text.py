"""Text in Tabelle umwandeln und zurück (Einfügen ▸ Tabelle). Keine Oberfläche; jede Umwandlung ist ein Rückgängig-Schritt.

    text_zu_tabelle(ed, "\t")       # die markierten Absätze werden Zeilen, der Trenner teilt sie in Zellen
    tabelle_zu_text(ed, "\t")       # die Tabelle an der Schreibmarke wird zu Absätzen, Zellen getrennt durch den Trenner
"""
from __future__ import annotations

from PySide6.QtGui import QTextCursor, QTextLength, QTextTableFormat

# Schlüssel → Beschriftung im Fenster („Andere“ gibt der Benutzer selbst ein)
TRENNER = [("\n", "Absatzmarken"), ("\t", "Tabstopps"), (";", "Semikolons"), (",", "Kommata"), (" ", "Leerzeichen")]


def markierte_absaetze(ed) -> list[str]:
    """Die Absätze der Markierung (ganz, auch wenn die Markierung mitten im Absatz beginnt)."""
    c = ed.textCursor()
    if not c.hasSelection():
        return []
    doc = ed.document()
    erster, letzter = doc.findBlock(c.selectionStart()), doc.findBlock(c.selectionEnd())
    if c.selectionEnd() == letzter.position() and letzter != erster:
        letzter = letzter.previous()                       # Markierung endet am Anfang eines Absatzes: der zählt nicht mit
    texte, b = [], erster
    while b.isValid():
        texte.append(b.text())
        if b == letzter:
            break
        b = b.next()
    return texte


def zellen(texte: list[str], trenner: str) -> list[list[str]]:
    """Absätze in Zeilen und Zellen teilen. Bei „Absatzmarken“ wird jeder Absatz eine Zeile mit einer Zelle."""
    if trenner == "\n" or not trenner:
        return [[t] for t in texte]
    return [t.split(trenner) for t in texte]


def text_zu_tabelle(ed, trenner: str = "\t", spalten: int | None = None) -> bool:
    texte = markierte_absaetze(ed)
    if not texte:
        return False
    zeilen = zellen(texte, trenner)
    n = spalten or max(len(z) for z in zeilen)
    c = ed.textCursor()
    doc = ed.document()
    erster = doc.findBlock(c.selectionStart())
    letzter = doc.findBlockByNumber(erster.blockNumber() + len(texte) - 1)
    c.beginEditBlock()
    c.setPosition(erster.position())
    c.setPosition(letzter.position() + letzter.length(), QTextCursor.KeepAnchor)   # mit Absatzende: kein leerer Absatz bleibt zurück
    c.removeSelectedText()
    tf = QTextTableFormat()
    tf.setCellPadding(4); tf.setCellSpacing(0); tf.setBorder(1); tf.setBorderCollapse(True)
    tf.setWidth(QTextLength(QTextLength.PercentageLength, 100))
    t = c.insertTable(len(zeilen), n, tf)
    for r, z in enumerate(zeilen):
        for s, text in enumerate(z[:n]):
            t.cellAt(r, s).firstCursorPosition().insertText(text)
    c.endEditBlock()
    ed.setTextCursor(t.cellAt(0, 0).firstCursorPosition())
    ed.document().setModified(True)
    return True


def tabelle_zu_text(ed, trenner: str = "\t") -> bool:
    c = ed.textCursor()
    t = c.currentTable()
    if t is None:
        return False
    zeilen = []
    for r in range(t.rows()):
        teile = []
        for s in range(t.columns()):
            z = t.cellAt(r, s)
            if z.column() != s or z.row() != r:            # verbundene Zelle: nur einmal
                continue
            a, e = QTextCursor(z.firstCursorPosition()), z.lastCursorPosition()
            a.setPosition(e.position(), QTextCursor.KeepAnchor)
            teile.append(a.selectedText().replace(" ", " ").replace(" ", " "))
        zeilen.append(trenner.join(teile) if trenner != "\n" else "\n".join(teile))
    c.beginEditBlock()
    c.setPosition(t.firstPosition() - 1)
    c.setPosition(t.lastPosition() + 1, QTextCursor.KeepAnchor)
    c.removeSelectedText()
    c.insertText("\n".join(zeilen))
    if not c.atBlockEnd():                                  # stand direkt ein Absatz hinter der Tabelle, bleibt er ein eigener
        c.insertBlock(); c.movePosition(QTextCursor.PreviousBlock); c.movePosition(QTextCursor.EndOfBlock)
    c.endEditBlock()
    ed.setTextCursor(c)
    ed.document().setModified(True)
    return True
