"""Vorschau im Dokumentfenster: statt des Dokuments steht eine schreibgeschützte Zeichenfläche mit einer abgeleiteten Fassung da — der Brief eines
Datensatzes (Seriendruck-Vorschau) oder das Original ohne die verfolgten Änderungen. Das Dokument selbst bleibt unverändert.

    zeigen(tab, dokument, art)  → Vorschau mit diesem ``Dokument`` zeigen (oder ersetzen); art "serien" oder "original"
    beenden(tab)                → wieder das Dokument zeigen
    aktiv(tab, art=None)        → True, solange eine Vorschau (dieser Art) steht
"""
from __future__ import annotations


def aktiv(tab, art: str | None = None) -> bool:
    return getattr(tab, "_vorschau_ansicht", None) is not None and art in (None, getattr(tab, "_vorschau_art", None))


def zeigen(tab, dokument, art: str = "serien") -> None:
    from lunivo_writer.core.bearbeitung import Bearbeitungssitzung
    from lunivo_writer.oberflaeche.dokument.ansicht.dokument_ansicht import DokumentAnsicht
    beenden(tab)
    v = DokumentAnsicht(Bearbeitungssitzung(dokument))
    v.setReadOnly(True)
    v.set_zoom(tab.editor.zoom)
    tab._vorschau_ansicht, tab._vorschau_art = v, art
    tab.takeWidget()
    tab.setWidget(v)


def beenden(tab) -> None:
    v = getattr(tab, "_vorschau_ansicht", None)
    if v is None:
        return
    tab._vorschau_ansicht = None
    tab.takeWidget()
    v.deleteLater()
    tab.setWidget(tab.editor.ansicht)
    tab.editor.ansicht.show()
    tab.editor.setFocus()
