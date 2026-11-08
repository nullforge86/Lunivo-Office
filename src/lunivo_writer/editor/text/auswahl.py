"""Auswählen (Start ▸ Auswählen): Tabellen ohne sichtbaren Rahmen finden und Stellen mit gleicher Zeichenformatierung sammeln — ohne Oberfläche."""
from __future__ import annotations

from PySide6.QtGui import QTextCharFormat, QTextCursor, QTextFormat, QTextFrameFormat, QTextTable

# Eigenschaften, an denen „ähnliche Formatierung“ gemessen wird (Schrift, Größe, Schnitt, Unterstreichung, Durchstreichung, Farbe, Hervorhebung)
_MERKMALE = (QTextFormat.FontFamilies, QTextFormat.FontPointSize, QTextFormat.FontWeight, QTextFormat.FontItalic, QTextFormat.TextUnderlineStyle,
             QTextFormat.FontStrikeOut, QTextFormat.ForegroundBrush, QTextFormat.BackgroundBrush, QTextFormat.TextVerticalAlignment)


def _tabellen(rahmen):
    for k in rahmen.childFrames():
        if isinstance(k, QTextTable):
            yield k
        yield from _tabellen(k)


def ohne_rahmen(t: QTextTable) -> bool:
    f = t.format()
    return f.border() <= 0 or f.borderStyle() == QTextFrameFormat.BorderStyle_None


def tabelle_ohne_rahmen(ed) -> bool:
    """Markiert die nächste Tabelle ohne Rahmen hinter der Schreibmarke (am Ende geht es vorn weiter). → False, wenn es keine gibt."""
    doc = ed.document()
    alle = sorted((t for t in _tabellen(doc.rootFrame()) if ohne_rahmen(t)), key=lambda t: t.firstPosition())
    if not alle:
        return False
    hier = ed.textCursor().selectionEnd()
    t = next((t for t in alle if t.firstPosition() >= hier), alle[0])
    c = QTextCursor(doc)
    c.setPosition(t.firstPosition()); c.setPosition(t.lastPosition(), QTextCursor.KeepAnchor)
    ed.setTextCursor(c); ed.ensureCursorVisible()
    return True


def _merkmale(cf: QTextCharFormat) -> tuple:
    return tuple(str(cf.property(p)) if cf.hasProperty(p) else "" for p in _MERKMALE)


def aehnlich_formatiert(ed) -> list[tuple[int, int]]:
    """Alle Strecken mit derselben Zeichenformatierung wie das Zeichen an der Schreibmarke (je Absatz zusammengefasst)."""
    doc = ed.document()
    c = QTextCursor(ed.textCursor())
    if c.hasSelection():
        c.setPosition(c.selectionStart()); c.movePosition(QTextCursor.NextCharacter)
    soll = _merkmale(c.charFormat())
    out: list[tuple[int, int]] = []
    b = doc.firstBlock()
    while b.isValid():
        it = b.begin()
        while not it.atEnd():
            f = it.fragment()
            if f.isValid() and f.text().strip() and _merkmale(f.charFormat()) == soll:
                s, e = f.position(), f.position() + f.length()
                if out and out[-1][1] == s:
                    out[-1] = (out[-1][0], e)
                else:
                    out.append((s, e))
            it += 1
        b = b.next()
    return out
