"""Fassungen eines Dokuments mit verfolgten Änderungen, für die Anzeige „Original“: eine Kopie, in der jede Einfügung fehlt und jede
Löschung wieder normaler Text ist. Das Dokument selbst bleibt unverändert. Keine Oberfläche.

    original(doc)      → Kopie wie vor den Änderungen
    bearbeiter(doc)    → Namen aller Bearbeiter mit Änderungen (sortiert)
    zeiten(doc)        → Tage (JJJJ-MM-TT) mit Änderungen (sortiert)
"""
from __future__ import annotations

from PySide6.QtGui import QTextCharFormat, QTextCursor, QTextDocument

from lunivo_writer.editor.zusatz import P_AENDERUNG, P_AUTOR, P_DATUM


def _stuecke(doc: QTextDocument) -> list[tuple[int, int, str, str, str]]:
    out = []
    b = doc.firstBlock()
    while b.isValid():
        it = b.begin()
        while not it.atEnd():
            f = it.fragment()
            if f.isValid() and f.charFormat().hasProperty(P_AENDERUNG):
                cf = f.charFormat()
                out.append((f.position(), f.position() + f.length(), cf.stringProperty(P_AENDERUNG), cf.stringProperty(P_AUTOR),
                            cf.stringProperty(P_DATUM)))
            it += 1
        b = b.next()
    return out


def original(doc: QTextDocument) -> QTextDocument:
    d = doc.clone()
    c = QTextCursor(d)
    c.beginEditBlock()
    for von, bis, art, _a, _z in reversed(_stuecke(d)):
        c.setPosition(von); c.setPosition(bis, QTextCursor.KeepAnchor)
        if art == "ins":
            c.removeSelectedText()
        else:
            f = QTextCharFormat(c.charFormat())
            for p in (P_AENDERUNG, P_AUTOR, P_DATUM):
                f.clearProperty(p)
            c.setCharFormat(f)
    c.endEditBlock()
    return d


def bearbeiter(doc: QTextDocument) -> list[str]:
    return sorted({a for _v, _b, _art, a, _z in _stuecke(doc) if a})


def zeiten(doc: QTextDocument) -> list[str]:
    return sorted({z[:10] for _v, _b, _art, _a, z in _stuecke(doc) if z})
