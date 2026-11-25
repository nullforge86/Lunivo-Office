"""Vektorbilder aus Textprogrammen (EMF und WMF, Windows-Metafiles): erkennen, Größe bestimmen und vom Kern rastern lassen – ohne Qt.

Ausgewertet und gezeichnet wird vom Kern (``core.layout.drucklayout.ausgabe.bild.metafile``); die Oberfläche legt das fertige Rasterbild nur
auf ihre Zeichenfläche (``vcl.qt.rendering.formen.vektor_bilder``)."""
from __future__ import annotations

from core.layout.drucklayout.ausgabe.bild import metafile as _mf


def ist_emf(blob: bytes) -> bool:
    return bool(_mf.ist_emf(blob))


def ist_wmf(blob: bytes) -> bool:
    return bool(_mf.ist_wmf(blob))


def masse_px(blob: bytes) -> tuple[float, float] | None:
    """Die Größe, die das Metafile auf dem Blatt haben soll (96 dpi); ``None``, wenn sie sich nicht bestimmen lässt."""
    m = _mf.masse_px(blob)
    return None if m is None else (float(m[0]), float(m[1]))


def metafile_rgba(blob: bytes, breite_px: int = 0, hoehe_px: int = 0) -> tuple[int, int, bytes] | None:
    """Das EMF oder WMF gerastert: ``(breite, hoehe, RGBA)`` – in der angegebenen Größe oder aus dem Rahmen (doppelt so fein wie 96 dpi,
    höchstens ``MAX_SEITE_PX``); ``None``, wenn es kein lesbares Metafile ist."""
    erg = _mf.metafile_rgba(blob, breite_px, hoehe_px)
    if erg is None:
        return None
    b, h, roh = erg
    return int(b), int(h), bytes(roh)
