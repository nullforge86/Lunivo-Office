from PySide6.QtGui import QTextCursor, QTextDocument

from lunivo_writer.editor.dokument import vergleich as V
from lunivo_writer.editor.dokument.zusatz import P_AENDERUNG, P_AUTOR


def _doc(text):
    d = QTextDocument(); d.setPlainText(text); return d


def _spuren(d):
    """[(art, autor, text)] zusammenhängender verfolgter Stücke."""
    out = []
    b = d.firstBlock()
    while b.isValid():
        it = b.begin()
        while not it.atEnd():
            f = it.fragment()
            cf = f.charFormat()
            if cf.hasProperty(P_AENDERUNG):
                out.append((cf.stringProperty(P_AENDERUNG), cf.stringProperty(P_AUTOR), f.text()))
            it += 1
        b = b.next()
    return out


def _angenommen(d):
    return "\n".join("".join(f.text() for f in _frags(b) if f.charFormat().stringProperty(P_AENDERUNG) != "del") for b in _blocks(d))


def _blocks(d):
    b = d.firstBlock()
    while b.isValid():
        yield b; b = b.next()


def _frags(b):
    it = b.begin()
    while not it.atEnd():
        yield it.fragment(); it += 1










