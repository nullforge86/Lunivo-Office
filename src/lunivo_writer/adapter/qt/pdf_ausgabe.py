"""PDF-Ausgabe des Dokuments über Qt (``QPdfWriter``): Ausgabeschnittstelle der Oberfläche, kein Teil der Dokumentverarbeitung.

Das Dokument wird vom Kern berechnet (Layout) und gezeichnet (Rendering); Qt stellt hier nur das Ausgabegerät."""
from __future__ import annotations

from lunivo_writer.core.document import Dokument


def dokument_als_pdf(dokument: Dokument, ziel: str, titel: str = "", autor: str = "", engine=None, erste: int = 1, letzte: int | None = None, struktur: dict | None = None) -> int:
    """Das Dokument als PDF schreiben: dieselbe Layoutberechnung und derselbe Renderer wie die Zeichenfläche, ein Blatt je Seite. ``erste`` und
    ``letzte``: Seitenbereich (1-basiert, einschließlich). ``struktur``: Lesezeichen, Kommentarnotizen, Hyperlinks und Notenverweise
    (siehe ``dienste.pdf_struktur.struktur_sammeln``); sie werden nach dem Zeichnen in die Datei eingetragen. Gibt die Zahl der geschriebenen Seiten zurück."""
    from PySide6.QtCore import QMarginsF, QSizeF
    from PySide6.QtGui import QPageLayout, QPageSize, QPainter, QPdfWriter

    from lunivo_writer.adapter.qt.rendering import QtRenderBackend
    from lunivo_writer.core.layout import LayoutEngine
    from lunivo_writer.core.layout import formatwerte as F
    from lunivo_writer.core.rendering import DokumentRenderer

    layout = LayoutEngine(engine)
    erg = layout.berechnen(dokument)
    renderer = DokumentRenderer(layout.engine)
    schreiber = QPdfWriter(ziel)
    schreiber.setResolution(96)
    schreiber.setTitle(titel or str(dokument.eigenschaften.get("title", "")))
    schreiber.setCreator(autor or str(dokument.eigenschaften.get("author", "")))
    grund = F.schrift(dict(dokument.standardformat))
    maler = None
    geschrieben = 0
    for seite in erg.seiten:
        if seite.index + 1 < max(1, erste) or (letzte is not None and seite.index + 1 > letzte):
            continue
        geschrieben += 1
        einr = seite.einrichtung
        layout_seite = QPageLayout(QPageSize(QSizeF(einr.width_mm, einr.height_mm), QPageSize.Millimeter), QPageLayout.Portrait, QMarginsF(0, 0, 0, 0))
        if maler is None:
            schreiber.setPageLayout(layout_seite)
            maler = QPainter(schreiber)
        else:
            schreiber.setPageLayout(layout_seite)
            schreiber.newPage()
        maler.setRenderHint(QPainter.Antialiasing)
        maler.setRenderHint(QPainter.TextAntialiasing)
        renderer.zeichne_seite(QtRenderBackend(maler), dokument, erg, seite.index, grund)
    if maler is not None:
        maler.end()
    if struktur and geschrieben:
        from lunivo_writer.dienste import pdf_struktur as PS
        PS.struktur_schreiben(ziel, PS.struktur_sammeln(dokument, erg, struktur, erste, letzte))
    return geschrieben
