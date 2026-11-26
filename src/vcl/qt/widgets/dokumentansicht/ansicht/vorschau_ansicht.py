"""Vorschau im Dokumentfenster: statt des Dokuments steht eine schreibgeschützte Zeichenfläche mit einer abgeleiteten Fassung da — der Brief eines
Datensatzes (Seriendruck-Vorschau) oder das Original ohne die verfolgten Änderungen. Das Dokument selbst bleibt unverändert.

    zeigen(tab, kennung, art)   → Vorschau mit dem Nebendokument ``kennung`` zeigen (oder ersetzen); art "serien" oder "original"
    beenden(tab)                → wieder das Dokument zeigen
    aktiv(tab, art=None)        → True, solange eine Vorschau (dieser Art) steht
"""
from __future__ import annotations


def aktiv(tab, art: str | None = None) -> bool:
    return getattr(tab, "_vorschau_ansicht", None) is not None and art in (None, getattr(tab, "_vorschau_art", None))


def zeigen(tab, kennung: int, art: str = "serien") -> None:
    """``kennung``: ein Nebendokument des Frameworks; die Vorschau gibt es beim Beenden wieder frei."""
    from vcl.qt.widgets.dokumentansicht.ansicht.dokument_ansicht import DokumentAnsicht
    beenden(tab)
    v = DokumentAnsicht(kennung)
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
    v._blink.stop()                                    # die Ansicht fragt nichts mehr ab, bevor ihr Nebendokument freigegeben wird
    v.deleteLater()
    from writer.funktionen import ansicht as AN
    AN.vorschau_schliessen(v.kennung)
    tab.setWidget(tab.editor.ansicht)
    tab.editor.ansicht.show()
    tab.editor.setFocus()
