"""Das Dokumentenmodell als PDF: Modell → Qt-freier Seitenumbruch → Rendering-Backend auf einem ``QPdfWriter`` (Text bleibt Text, Vektoren bleiben Vektoren), ohne ``QTextDocument``."""
from __future__ import annotations

from PySide6.QtCore import QMarginsF, QSizeF
from PySide6.QtGui import QPageLayout, QPageSize, QPainter, QPdfWriter, QTextCharFormat

from lunivo_writer.adapter.qt.dokument import _setzen
from lunivo_writer.adapter.qt.rendering import QtRenderBackend
from lunivo_writer.adapter.qt.textlayout import _fontspec_aus
from lunivo_writer.core.document import Document
from lunivo_writer.core.layout import umbrechen
from lunivo_writer.core.rendering.seite import zeichne_seite, zeichne_zeilennummern
from lunivo_writer.core.rendering.seitenschmuck import zeichne_seitenschmuck
from lunivo_writer.dienste.textsatz import standard_engine

AUFLOESUNG = 600                                    # dpi des PDF-Zeichenraums


def modell_als_pdf(modell: Document, pfad: str, titel: str = "", engine=None) -> int:
    """Das Modell als PDF schreiben (jede Seite in der Größe ihrer Seiteneinrichtung). → Seitenzahl."""
    from lunivo_writer.editor.seite.seiten_aufteilung import _start_nummer
    from lunivo_writer.adapter.qt.seitenbild import _kopf_fuss
    engine = engine or standard_engine()
    erg = umbrechen(modell, engine)
    cf = QTextCharFormat()
    _setzen(cf, modell.default_format.properties)
    grund = cf.font()
    w = QPdfWriter(pfad)
    w.setResolution(AUFLOESUNG)
    if titel:
        w.setTitle(titel)
    p = QPainter()
    for i, s in enumerate(erg.seiten):
        einr = s.einrichtung
        breite_mm, hoehe_mm = (einr.width_mm, einr.height_mm) if einr is not None else (210.0, 297.0)
        w.setPageLayout(QPageLayout(QPageSize(QSizeF(breite_mm, hoehe_mm), QPageSize.Millimeter), QPageLayout.Portrait, QMarginsF(0, 0, 0, 0)))
        if i == 0:
            p.begin(w)
        else:
            w.newPage()
        p.save()
        p.scale(AUFLOESUNG / 96.0, AUFLOESUNG / 96.0)                  # Bildpunkte bei 96 dpi → Gerätepunkte
        b = QtRenderBackend(p)
        if einr is not None and hasattr(einr, "kopf_fuss"):
            zeichne_seitenschmuck(b, engine, einr, True, None, "hinten")
            _kopf_fuss(p, einr, i + 1, _start_nummer(einr), len(erg.seiten), grund, engine)
        zeichne_seite(b, erg, i, engine, False, modell)
        zeichne_zeilennummern(b, erg, i, _fontspec_aus(grund))
        if einr is not None and hasattr(einr, "kopf_fuss"):
            zeichne_seitenschmuck(b, engine, einr, False, None, "vorn", False)
        p.restore()
    p.end()
    return len(erg.seiten)
