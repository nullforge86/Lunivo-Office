"""Das ``core.document.Dokument`` als Datei speichern (DOCX, ODT, RTF, TXT) über die Qt-freien Schreiber. Es gibt keinen Rückfallweg.

PDF entsteht nicht hier, sondern über die Ausgabeschnittstelle der Oberfläche (``adapter/qt/pdf_ausgabe``)."""
from __future__ import annotations

from lunivo_writer.kern.dokument import Dokument
from lunivo_writer.dienste import dateiformate as D
from lunivo_writer.dienste import sicher_schreiben
from lunivo_writer.kern.dokument.bericht import DocumentIOError


def meta_aus_dokument(neu: Dokument, meta: dict | None = None) -> dict:
    """Das Meta-Wörterbuch der Schreiber aus den Zusatzdaten des Dokuments; Einträge, die das Dokument nicht kennt, bleiben aus ``meta`` erhalten."""
    aus = dict(meta or {})
    aus["kommentare"] = {k.id: {"autor": k.autor, "initialen": k.initialen, "datum": k.datum, "text": k.text, "geloest": k.geloest,
                                **({"antwort_auf": k.antwort_auf} if k.antwort_auf is not None else {})} for k in neu.kommentare.values()}
    aus["noten"] = {art: {n.id: n.text for n in noten.values()} for art, noten in neu.noten.items()}
    aus["quellen"] = [dict(q) for q in neu.quellen]
    aus.update(neu.eigenschaften)
    return aus


def speichere_modell(path: str, modell: Dokument, page, meta: dict | None = None, sicherung: bool = True,
                     erwartet=sicher_schreiben.UNGEPRUEFT):
    """Wirft ``DocumentIOError``; liefert den ``IOReport`` des Schreibens."""
    from lunivo_writer.kern.dokument.bericht import IOReport

    angaben = meta_aus_dokument(modell, meta)
    endung = path.lower().rsplit(".", 1)[-1] if "." in path else ""
    if endung == "pdf":
        raise DocumentIOError("PDF wird über die PDF-Ausgabe der Oberfläche geschrieben, nicht über das Speichern des Dokuments.")
    if endung == "txt":
        from lunivo_writer.dienste.txt_modell import dokument_als_text
        daten, hinweise = dokument_als_text(modell, page)
        bericht = IOReport()
        for h in hinweise:
            bericht.warn(h)
        sicher_schreiben.bytes_schreiben(path, daten, endung=".txt", sicherung=sicherung, erwartet=erwartet)
        return bericht
    if endung == "odt":
        from lunivo_writer.dienste import odt_modell_schreiber
        daten, bericht = odt_modell_schreiber.odt_modell_daten(modell, page, angaben)
        sicher_schreiben.bytes_schreiben(path, daten, endung=".odt", sicherung=sicherung, erwartet=erwartet)
        return bericht
    if endung == "rtf":
        from lunivo_writer.dienste import rtf_modell_schreiber
        daten, bericht = rtf_modell_schreiber.rtf_modell_daten(modell, page, angaben)
        sicher_schreiben.bytes_schreiben(path, daten, endung=".rtf", sicherung=sicherung, erwartet=erwartet)
        return bericht
    if endung == "docx":
        from lunivo_writer.dienste import docx_modell_schreiber
        daten, bericht = docx_modell_schreiber.docx_dokument_daten(modell, page, angaben)
        return D.save_docx_daten(path, daten, bericht, angaben, sicherung, erwartet)
    raise DocumentIOError(f"Das Format „{endung}“ kann nicht gespeichert werden.")
