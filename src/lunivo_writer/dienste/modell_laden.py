"""Dateien als ``core.document.Dokument`` laden — ausschließlich über die Qt-freien Leser (DOCX, ODT, RTF, TXT).

Es gibt keinen Rückfallweg: Enthält eine Datei etwas, das der Leser noch nicht abbildet, wird das mit einer klaren Meldung gesagt und die Datei nicht
geöffnet (``DocumentIOError``). Fehlende Fähigkeiten gehören in den jeweiligen Qt-freien Leser, nicht in einen zweiten Weg."""
from __future__ import annotations

import os
from dataclasses import dataclass

from lunivo_writer.core.document import Dokument
from lunivo_writer.dienste import dateiformate as D
from lunivo_writer.modelle.bericht import DocumentIOError, IOReport


@dataclass
class ModellGeladen:
    document: Dokument
    page: object            # ``PageSettings`` des ersten Abschnitts
    meta: dict
    report: object          # ``IOReport``: was nicht übernommen wurde


def lade_modell(path: str, kennwort: str | None = None) -> ModellGeladen:
    """Datei laden und als Dokument liefern. Wirft ``DocumentIOError``."""
    if not os.path.isfile(path):
        raise DocumentIOError(f"Die Datei „{path}“ existiert nicht.")
    endung = D.ext(path)
    if endung in (".txt", ".text", ""):
        from lunivo_writer.dienste.txt_modell import dokument_laden
        dok, seite = dokument_laden(path)
        return ModellGeladen(dok, seite, {}, IOReport())
    if endung in (".docx", ".dotx", ".docm"):
        return _docx(path, endung, kennwort)
    if endung in (".odt", ".fodt"):
        from lunivo_writer.dienste.odt_dokument_leser import lese_odt_dokument
        D._kopf_pruefen(path, endung)
        dok, page, meta, rep = lese_odt_dokument(path, flach=endung == ".fodt")
        return ModellGeladen(dok, page, meta, rep)
    if endung == ".rtf":
        from lunivo_writer.dienste.rtf_dokument_leser import lese_rtf_dokument
        D._kopf_pruefen(path, ".rtf")
        gelesen = lese_rtf_dokument(path)
        if gelesen is None:
            raise DocumentIOError("Die RTF-Datei enthält Inhalt, den Lunivo noch nicht abbilden kann (zum Beispiel Bilder in Kopf- oder Fußzeilen).")
        dok, page, meta, rep = gelesen
        return ModellGeladen(dok, page, meta, rep)
    if endung in D.NICHT_UNTERSTUETZT:
        raise DocumentIOError(f"Das alte Format {D.NICHT_UNTERSTUETZT[endung]} wird nicht mehr unterstützt. Bitte die Datei im "
                              "ursprünglichen Programm als DOCX speichern und dann in Lunivo öffnen.")
    raise DocumentIOError(f"Das Format „{endung or 'ohne Endung'}“ kann nicht geöffnet werden. Unterstützt: DOCX, ODT, RTF, TXT.")


def _docx(path: str, endung: str, kennwort: str | None) -> ModellGeladen:
    """DOCX (auch DOTX, DOCM und kennwortgeschützt) mit dem Qt-freien Leser; ohne Rückfall."""
    import tempfile
    from lunivo_writer.dienste.docx_dokument_leser import lese_docx_dokument
    with tempfile.TemporaryDirectory(prefix="lunivo-") as tmp:
        quelle = path
        if endung in (".dotx", ".docm"):
            D._kopf_pruefen(path, endung)
            quelle = D._als_docx(path, os.path.join(tmp, "dokument.docx"))
        verschluesselt = D._verschluesselt(quelle)
        if verschluesselt:
            klar = os.path.join(tmp, "klar.docx")
            D._entschluesseln(quelle, kennwort, klar)
            quelle = klar
        dok, page, meta, rep = lese_docx_dokument(quelle)
    if verschluesselt:
        meta["kennwort"] = kennwort
    if endung == ".docm":
        rep.warn("Makros aus der DOCM-Datei werden nicht ausgeführt und beim Speichern nicht übernommen.")
    return ModellGeladen(dok, page, meta, rep)
