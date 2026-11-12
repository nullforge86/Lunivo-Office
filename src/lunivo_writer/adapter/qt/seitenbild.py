"""Seiten aus dem Dokumentenmodell als Bild: Modell → Qt-freier Seitenumbruch → Rendering-Backend (Qt) — ohne ``QTextDocument`` dazwischen."""
from __future__ import annotations

from PySide6.QtGui import QColor, QImage, QPainter, QTextCharFormat

from lunivo_writer.adapter.qt.rendering import QtRenderBackend
from lunivo_writer.core.document import Document
from lunivo_writer.core.layout import umbrechen
from lunivo_writer.core.rendering.seite import zeichne_seite, zeichne_zeilennummern
from lunivo_writer.core.rendering.seitenschmuck import zeichne_seitenschmuck
from lunivo_writer.dienste.textsatz import standard_engine


def _kopf_fuss(p: QPainter, einr, n: int, nr_offset: int, total: int, grund, engine) -> None:
    """Kopf- und Fußzeile: Qt-frei über ``core.rendering.kopffuss``; Zeilen mit Texteffekten zeichnet der Editor."""
    from lunivo_writer.adapter.qt.textlayout import _fontspec_aus
    from lunivo_writer.core.geometry import Rect
    from lunivo_writer.core.rendering.kopffuss import zeichne_zeile
    from lunivo_writer.editor.seite import seitenzahl as SZ
    from lunivo_writer.editor.seite.seiten_aufteilung import KOPF_HOEHE_MM, _kopf_fuss_zeichnen
    from lunivo_writer.modelle.seite import mm_to_px
    angezeigt = n + nr_offset
    kopf, fuss = einr.kopf_fuss(n, angezeigt)
    backend = QtRenderBackend(p)
    spec = _fontspec_aus(grund)
    ml, cw, ph = mm_to_px(einr.margin_left_mm), einr.content_width_px, mm_to_px(einr.height_mm)
    for hf, y in ((kopf, mm_to_px(einr.kopf_abstand_mm)), (fuss, ph - mm_to_px(einr.fuss_abstand_mm))):
        ok = zeichne_zeile(backend, engine, hf, Rect(ml, y, cw, mm_to_px(KOPF_HOEHE_MM)), lambda t: SZ.text(t, angezeigt, total, einr, ""),
                           SZ.ausrichtung(hf.align, angezeigt), spec)
        if not ok:                                                                  # Texteffekte: der Editor zeichnet beide Zeilen
            _kopf_fuss_zeichnen(p, einr, n, nr_offset, total, None, grund, "")
            return


def seiten_aus_modell(modell: Document, faktor: float = 1.0, engine=None) -> list[QImage]:
    """Alle Seiten des Modells als Bilder (``faktor`` 1.0 = 96 dpi)."""
    from lunivo_writer.adapter.qt.dokument import _setzen
    from lunivo_writer.adapter.qt.textlayout import _fontspec_aus
    from lunivo_writer.editor.seite.seiten_aufteilung import _start_nummer
    engine = engine or standard_engine()
    erg = umbrechen(modell, engine)
    cf = QTextCharFormat()
    _setzen(cf, modell.default_format.properties)
    grund = cf.font()
    bilder = []
    for i, s in enumerate(erg.seiten):
        einr = s.einrichtung
        w = round((einr.width_mm if einr is not None else 210.0) * 96 / 25.4 * faktor)
        h = round((einr.height_mm if einr is not None else 297.0) * 96 / 25.4 * faktor)
        img = QImage(w, h, QImage.Format_RGB32)
        img.fill(QColor("white"))
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        p.scale(faktor, faktor)
        if einr is not None and hasattr(einr, "kopf_fuss"):                              # Seitenschmuck und Kopf-/Fußzeile: die Bausteine des Editors (Seitenfarbe, Rahmen, Wasserzeichen)
            zeichne_seitenschmuck(QtRenderBackend(p), engine, einr, True, None, "hinten")
            _kopf_fuss(p, einr, i + 1, _start_nummer(einr), len(erg.seiten), grund, engine)
        zeichne_seite(QtRenderBackend(p), erg, i, engine, False, modell)
        zeichne_zeilennummern(QtRenderBackend(p), erg, i, _fontspec_aus(grund))
        if einr is not None and hasattr(einr, "kopf_fuss"):
            zeichne_seitenschmuck(QtRenderBackend(p), engine, einr, False, None, "vorn", False)
        p.end()
        bilder.append(img)
    return bilder
