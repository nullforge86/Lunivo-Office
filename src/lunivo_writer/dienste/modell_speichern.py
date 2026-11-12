"""Das Dokumentenmodell als Datei speichern (Gegenstück zu ``modell_laden``): DOCX, ODT, RTF, TXT oder PDF, je nach Endung. PDF kommt ohne Textdokument aus (``adapter/qt/pdf_modell.py``).

``speichere_modell`` baut aus dem Modell über die Brücke ``adapter/qt/dokument.py`` das Textdokument, das die Schreiber (``docx_schreiber``, ``odt_schreiber`` …) lesen; die Bilder, auf die nur ein Name verweist
(``Document.media``), kommen dabei mit. Bearbeitet man ein Modell mit ``core.editing.Sitzung``, lässt es sich so ohne Editor speichern."""
from __future__ import annotations

from lunivo_writer.adapter.qt.dokument import document_to_qt
from lunivo_writer.core.document import Document
from lunivo_writer.dienste import datei_dienst


def speichere_modell(path: str, modell: Document, page, meta: dict | None = None, sicherung: bool = True):
    """Wirft ``DocumentIOError`` wie ``datei_dienst.save``; liefert den ``IOReport`` des Schreibens."""
    if path.lower().endswith(".pdf"):
        from lunivo_writer.adapter.qt.pdf_modell import modell_als_pdf
        from lunivo_writer.modelle.bericht import IOReport
        modell_als_pdf(modell, path, (meta or {}).get("title", ""))
        return IOReport()
    return datei_dienst.save(path, document_to_qt(modell), page, meta or {}, sicherung)
