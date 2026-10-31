"""Vorschau im Dokumentfenster: statt des Dokuments steht ein schreibgeschützter Editor mit einer abgeleiteten Fassung da — der
Brief eines Datensatzes (Seriendruck-Vorschau) oder das Original ohne die verfolgten Änderungen (Überprüfen ▸ Anzeige „Original“).
Das Dokument selbst bleibt unverändert (und ist der Editor, an dem alle Befehle arbeiten).

    zeigen(tab, doc, art)  → Vorschau mit diesem Dokument zeigen (oder ersetzen); art "serien" oder "original"
    beenden(tab)           → wieder das Dokument zeigen
    aktiv(tab, art=None)   → True, solange eine Vorschau (dieser Art) steht
"""
from __future__ import annotations


def aktiv(tab, art: str | None = None) -> bool:
    return getattr(tab, "_vorschau_ansicht", None) is not None and art in (None, getattr(tab, "_vorschau_art", None))


def zeigen(tab, doc, art: str = "serien") -> None:
    from PySide6.QtCore import Qt
    from lunivo_writer.ui.document.document_editor import DocumentEditor
    v = getattr(tab, "_vorschau_ansicht", None)
    if v is None:
        v = DocumentEditor()
        lay = tab._holder.layout()
        lay.insertWidget(lay.indexOf(tab.editor) + 1, v, 0, Qt.AlignTop)
        tab._vorschau_ansicht = v
    tab._vorschau_art = art
    v.set_document_and_page(doc, tab.editor.page.copy())
    v.zusatz_binden(dict(tab.meta))
    v.setReadOnly(True)
    v.set_zoom(tab.editor.zoom)
    v._recount()
    tab.editor.hide(); v.show()


def beenden(tab) -> None:
    v = getattr(tab, "_vorschau_ansicht", None)
    if v is None:
        return
    tab._vorschau_ansicht = None
    v.hide(); v.setParent(None); v.deleteLater()
    tab.editor.show(); tab.editor.setFocus()
