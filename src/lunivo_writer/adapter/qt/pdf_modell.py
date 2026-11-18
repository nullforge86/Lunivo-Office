"""Das Dokumentenmodell als PDF: Modell → Qt-freier Seitenumbruch → Rendering-Backend auf einem ``QPdfWriter`` (Text bleibt Text, Vektoren bleiben Vektoren), ohne ``QTextDocument``."""
from __future__ import annotations

from PySide6.QtGui import QPainter, QPdfWriter, QTextCharFormat

from lunivo_writer.adapter.qt.dokument import _setzen
from lunivo_writer.adapter.qt.seitenbild import seite_malen
from lunivo_writer.core.document import Document
from lunivo_writer.core.layout import umbrechen
from lunivo_writer.dienste.textsatz import standard_engine
from lunivo_writer.modelle.seite import PageSettings

AUFLOESUNG = 600                                    # dpi des PDF-Zeichenraums


def modell_als_pdf(modell: Document, pfad: str, titel: str = "", engine=None, *, autor: str = "", erste: int = 1, letzte: int | None = None) -> int:
    """Das Modell als PDF schreiben (jede Seite in der Größe ihrer Seiteneinrichtung), optional auf einen Seitenbereich begrenzt. → Zahl geschriebener Seiten."""
    from lunivo_writer.editor.seite.seiten_aufteilung import _page_layout
    engine = engine or standard_engine()
    erg = umbrechen(modell, engine)
    cf = QTextCharFormat()
    _setzen(cf, modell.default_format.properties)
    grund = cf.font()
    w = QPdfWriter(pfad)
    w.setResolution(AUFLOESUNG)
    if titel:
        w.setTitle(titel)
    w.setCreator("Lunivo Writer")
    if autor:
        from lunivo_writer.editor.seite.seiten_aufteilung import _xmp_autor
        w.setDocumentXmpMetadata(_xmp_autor(autor))
    p = QPainter()
    anfang = max(1, int(erste))
    ende = len(erg.seiten) if letzte is None else min(len(erg.seiten), int(letzte))
    ausgewaehlt = list(enumerate(erg.seiten[anfang - 1:ende], start=anfang - 1)) if anfang <= ende else []
    for nummer, s in ausgewaehlt:
        einr = s.einrichtung
        if einr is not None:
            w.setPageLayout(_page_layout(einr))
        else:
            w.setPageLayout(_page_layout(PageSettings()))
        if nummer == ausgewaehlt[0][0]:
            p.begin(w)
        else:
            w.newPage()
        p.save()
        p.scale(AUFLOESUNG / 96.0, AUFLOESUNG / 96.0)                  # Bildpunkte bei 96 dpi → Gerätepunkte
        seite_malen(p, modell, erg, nummer, engine, grund)
        p.restore()
    p.end()
    return len(ausgewaehlt)
