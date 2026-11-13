"""Das Qt-freie Dokumentenmodell als Datei speichern; nur Formate ohne fertigen Modellschreiber nutzen den Qt-Adapter."""
from __future__ import annotations

from lunivo_writer.core.document import Document
from lunivo_writer.dienste import sicher_schreiben


def speichere_modell(path: str, modell: Document, page, meta: dict | None = None, sicherung: bool = True,
                     erwartet=sicher_schreiben.UNGEPRUEFT):
    """Wirft ``DocumentIOError`` wie ``datei_dienst.save``; liefert den ``IOReport`` des Schreibens."""
    from lunivo_writer.modelle.bericht import IOReport

    endung = path.lower().rsplit(".", 1)[-1] if "." in path else ""
    if endung == "txt":
        from lunivo_writer.dienste.txt_modell import text_aus_modell
        direkt = text_aus_modell(modell)
        if direkt is not None:
            daten, reich = direkt
            bericht = IOReport()
            if reich:
                bericht.warn("Als Textdatei gehen Formatierung, Listen, Tabellen und Bilder verloren.")
            if not page.header.is_empty() or not page.footer.is_empty():
                bericht.warn("Kopf- und Fußzeile werden in der Textdatei nicht gespeichert.")
            sicher_schreiben.bytes_schreiben(path, daten, endung=".txt", sicherung=sicherung, erwartet=erwartet)
            return bericht
    if path.lower().endswith(".pdf"):
        from lunivo_writer.adapter.qt.pdf_modell import modell_als_pdf
        angaben = meta or {}
        sicher_schreiben.schreiben(
            path,
            lambda temp: modell_als_pdf(modell, temp, angaben.get("title", ""), autor=angaben.get("author", "")),
            endung="pdf",
            sicherung=sicherung,
            erwartet=erwartet,
        )
        return IOReport()
    if path.lower().endswith(".docx"):
        from lunivo_writer.dienste import docx_schreiber, datei_dienst
        direkt = docx_schreiber.docx_modell_daten(modell, page, meta or {})
        if direkt is not None:
            daten, bericht = direkt
            return datei_dienst.save_docx_daten(path, daten, bericht, meta or {}, sicherung, erwartet)
    from lunivo_writer.adapter.qt.dokument import document_to_qt
    from lunivo_writer.dienste import datei_dienst
    return datei_dienst.save(path, document_to_qt(modell), page, meta or {}, sicherung, erwartet)
