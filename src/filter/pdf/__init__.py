"""Tür des Pakets ``filter.pdf``: öffentliche Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "DRUCK": ("pdf_export", "DRUCK"),
    "PdfWahl": ("pdf_export", "PdfWahl"),
    "dokument_als_pdf": ("pdf_ausgabe", "dokument_als_pdf"),
    "kennwort_fehler": ("pdf_export", "kennwort_fehler"),
    "lesezeichen": ("pdf_export", "lesezeichen"),
    "nur_markierung": ("pdf_export", "nur_markierung"),
    "seiten": ("pdf_export", "seiten"),
    "verschluesseln": ("pdf_export", "verschluesseln"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "pdf_ausgabe":
        from . import pdf_ausgabe as _datei
    elif datei == "pdf_export":
        from . import pdf_export as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
