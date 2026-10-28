"""Seriendruck-Vorschau im Dokumentfenster: statt der Vorlage steht ein schreibgeschützter Editor mit dem Brief eines Datensatzes da.
Die Vorlage selbst bleibt unverändert (und ist der Editor, an dem alle Befehle arbeiten).

    zeigen(tab, doc)   → Vorschau mit diesem Dokument zeigen (oder ersetzen)
    beenden(tab)       → wieder die Vorlage zeigen
    aktiv(tab)         → True, solange die Vorschau steht
"""
from __future__ import annotations


def aktiv(tab) -> bool:
    return getattr(tab, "_serien_vorschau", None) is not None


def zeigen(tab, doc) -> None:
    from PySide6.QtCore import Qt
    from lunivo_writer.ui.document.document_editor import DocumentEditor
    v = getattr(tab, "_serien_vorschau", None)
    if v is None:
        v = DocumentEditor()
        lay = tab._holder.layout()
        lay.insertWidget(lay.indexOf(tab.editor) + 1, v, 0, Qt.AlignTop)
        tab._serien_vorschau = v
    v.set_document_and_page(doc, tab.editor.page.copy())
    v.zusatz_binden(dict(tab.meta))
    v.setReadOnly(True)
    v.set_zoom(tab.editor.zoom)
    v._recount()
    tab.editor.hide(); v.show()


def beenden(tab) -> None:
    v = getattr(tab, "_serien_vorschau", None)
    if v is None:
        return
    tab._serien_vorschau = None
    v.hide(); v.setParent(None); v.deleteLater()
    tab.editor.show(); tab.editor.setFocus()
