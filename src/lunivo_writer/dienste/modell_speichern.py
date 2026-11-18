"""Das ``core.document.Dokument`` als Datei speichern. PDF entsteht aus derselben Layout- und Renderarchitektur wie die Anzeige; für DOCX, ODT, RTF und TXT
übersetzt ``modell_umwandlung`` das Dokument für die vorhandenen Schreiber (siehe dort)."""
from __future__ import annotations

from lunivo_writer.core.document import Dokument
from lunivo_writer.dienste import sicher_schreiben
from lunivo_writer.dienste.modell_umwandlung import meta_aus_dokument, neu_zu_alt


def dokument_als_pdf(dokument: Dokument, ziel: str, titel: str = "", autor: str = "", engine=None, erste: int = 1, letzte: int | None = None) -> int:
    """Das Dokument als PDF schreiben: dieselbe Layoutberechnung und derselbe Renderer wie die Zeichenfläche, ein Blatt je Seite. ``erste`` und
    ``letzte``: Seitenbereich (1-basiert, einschließlich). Gibt die Zahl der geschriebenen Seiten zurück."""
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
    return geschrieben


def speichere_modell(path: str, modell: Dokument, page, meta: dict | None = None, sicherung: bool = True,
                     erwartet=sicher_schreiben.UNGEPRUEFT):
    """Wirft ``DocumentIOError`` wie ``datei_dienst.save``; liefert den ``IOReport`` des Schreibens."""
    from lunivo_writer.modelle.bericht import IOReport

    angaben = meta_aus_dokument(modell, meta)
    if path.lower().endswith(".pdf"):
        sicher_schreiben.schreiben(
            path,
            lambda temp: dokument_als_pdf(modell, temp, angaben.get("title", ""), autor=angaben.get("author", "")),
            endung="pdf",
            sicherung=sicherung,
            erwartet=erwartet,
        )
        return IOReport()
    endung = path.lower().rsplit(".", 1)[-1] if "." in path else ""
    if endung == "txt":
        from lunivo_writer.dienste.txt_modell import dokument_als_text
        daten, hinweise = dokument_als_text(modell, page)
        bericht = IOReport()
        for h in hinweise:
            bericht.warn(h)
        sicher_schreiben.bytes_schreiben(path, daten, endung=".txt", sicherung=sicherung, erwartet=erwartet)
        return bericht
    if endung == "odt":
        from lunivo_writer.dienste import odt_modell_schreiber, sicher_schreiben as _s
        daten, bericht = odt_modell_schreiber.odt_modell_daten(modell, page, angaben)
        _s.bytes_schreiben(path, daten, endung=".odt", sicherung=sicherung, erwartet=erwartet)
        return bericht
    if endung == "rtf":
        from lunivo_writer.dienste import rtf_modell_schreiber, sicher_schreiben as _s
        daten, bericht = rtf_modell_schreiber.rtf_modell_daten(modell, page, angaben)
        _s.bytes_schreiben(path, daten, endung=".rtf", sicherung=sicherung, erwartet=erwartet)
        return bericht
    if endung == "docx":
        import logging
        from lunivo_writer.dienste import datei_dienst as _dd, docx_modell_schreiber
        try:
            neu = docx_modell_schreiber.docx_dokument_daten(modell, page, angaben)
        except Exception:                                                            # noqa: BLE001 — der bisherige Weg bleibt als Rückfall
            logging.getLogger("lunivo.dateien").exception("Direkter DOCX-Weg fehlgeschlagen, nehme den bisherigen")
            neu = None
        if neu is not None:
            daten, bericht = neu
            return _dd.save_docx_daten(path, daten, bericht, angaben, sicherung, erwartet)
    alt = neu_zu_alt(modell)
    if endung == "docx":
        from lunivo_writer.dienste import docx_schreiber, datei_dienst
        direkt = docx_schreiber.docx_modell_daten(alt, page, angaben)
        if direkt is not None:
            daten, bericht = direkt
            return datei_dienst.save_docx_daten(path, daten, bericht, angaben, sicherung, erwartet)
    from lunivo_writer.adapter.qt.dokument import document_to_qt
    from lunivo_writer.dienste import datei_dienst
    return datei_dienst.save(path, document_to_qt(alt), page, angaben, sicherung, erwartet)
