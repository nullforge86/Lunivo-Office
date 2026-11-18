"""Dateien als ``core.document.Dokument`` laden. Die vorhandenen Leser (DOCX, ODT, RTF, TXT) liefern noch das bisherige Modell; ``modell_umwandlung`` übersetzt es
einmal beim Laden (siehe dort)."""
from __future__ import annotations

import os
from dataclasses import dataclass

from lunivo_writer.core.document import Dokument
from lunivo_writer.dienste.modell_umwandlung import alt_zu_neu


@dataclass
class ModellGeladen:
    document: Dokument
    page: object            # ``PageSettings`` des ersten Abschnitts
    meta: dict
    report: object          # ``IOReport``: was nicht übernommen wurde


def lade_modell(path: str, kennwort: str | None = None) -> ModellGeladen:
    """Datei laden und als Dokument liefern. Wirft ``DocumentIOError`` wie ``datei_dienst.load``."""
    if os.path.splitext(path)[1].lower() in (".txt", ".text", ""):
        from lunivo_writer.dienste.txt_modell import dokument_laden
        from lunivo_writer.modelle.bericht import IOReport
        dok, seite = dokument_laden(path)
        return ModellGeladen(dok, seite, {}, IOReport())
    endung = os.path.splitext(path)[1].lower()
    if endung == ".docx" and os.path.isfile(path):
        direkt = _docx_direkt(path, kennwort)
        if direkt is not None:
            return direkt
    if endung in (".odt", ".fodt") and os.path.isfile(path):
        from lunivo_writer.dienste.datei_dienst import _kopf_pruefen
        from lunivo_writer.dienste.odt_dokument_leser import lese_odt_dokument
        _kopf_pruefen(path, endung)
        dok, page, meta, rep = lese_odt_dokument(path, flach=endung == ".fodt")
        return ModellGeladen(dok, page, meta, rep)
    if os.path.splitext(path)[1].lower() == ".rtf" and os.path.isfile(path):
        from lunivo_writer.dienste.datei_dienst import _kopf_pruefen
        from lunivo_writer.dienste.rtf_dokument_leser import lese_rtf_dokument
        _kopf_pruefen(path, ".rtf")
        direkt = lese_rtf_dokument(path)
        if direkt is not None:
            dok, page, meta, rep = direkt
            return ModellGeladen(dok, page, meta, rep)
    from lunivo_writer.dienste.datei_dienst import load
    geladen = load(path, kennwort)
    if geladen.modell is not None:
        modell = geladen.modell
    else:
        from lunivo_writer.adapter.qt.dokument import document_from_qt
        modell = document_from_qt(geladen.doc, geladen.page)
        from lunivo_writer.core.document import Footnote
        noten = geladen.meta.get("noten", {})
        modell.notes = [Footnote(int(nid), art, str(text))
                        for art, eintraege in noten.items() if art in ("f", "e")
                        for nid, text in eintraege.items()]
    return ModellGeladen(alt_zu_neu(modell, geladen.meta), geladen.page, geladen.meta, geladen.report)


def _docx_direkt(path: str, kennwort: str | None):
    """DOCX direkt ins Dokumentmodell lesen; ``None``, wenn die Datei etwas enthält, das der direkte Leser nicht abbildet (dann der bisherige Weg).
    Fehler beim direkten Lesen führen ebenfalls zum bisherigen Weg."""
    import logging
    import tempfile
    from lunivo_writer.dienste import datei_dienst as _dd
    from lunivo_writer.dienste.docx_dokument_leser import lese_docx_dokument
    from lunivo_writer.modelle.bericht import DocumentIOError, PasswortNoetig
    try:
        if _dd._verschluesselt(path):
            with tempfile.TemporaryDirectory(prefix="lunivo-") as tmp:
                klar = os.path.join(tmp, "klar.docx")
                _dd._entschluesseln(path, kennwort, klar)
                gelesen = lese_docx_dokument(klar)
            if gelesen is not None:
                gelesen[2]["kennwort"] = kennwort
        else:
            gelesen = lese_docx_dokument(path)
    except (DocumentIOError, PasswortNoetig):
        raise
    except Exception:                                                               # noqa: BLE001 — der bisherige Weg bleibt als Rückfall
        logging.getLogger("lunivo.dateien").exception("Direktes Lesen der DOCX-Datei fehlgeschlagen, nehme den bisherigen Weg")
        return None
    if gelesen is None:
        return None
    dok, page, meta, rep = gelesen
    return ModellGeladen(dok, page, meta, rep)
