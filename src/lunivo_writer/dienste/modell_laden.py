"""Dateien als Qt-freies Dokumentenmodell laden. TXT läuft direkt im Modell; andere Formate behalten bis zur Ablösung ihrer Leser den Qt-Rückfall."""
from __future__ import annotations

import os
from dataclasses import dataclass

from lunivo_writer.core.document import Document


@dataclass
class ModellGeladen:
    document: Document
    page: object            # ``PageSettings`` des ersten Abschnitts
    meta: dict
    report: object          # ``IOReport``: was nicht übernommen wurde


def lade_modell(path: str, kennwort: str | None = None) -> ModellGeladen:
    """Datei laden und als Modell liefern. Wirft ``DocumentIOError`` wie ``datei_dienst.load``."""
    if os.path.splitext(path)[1].lower() in (".txt", ".text", ""):
        from lunivo_writer.dienste.txt_modell import modell_laden
        from lunivo_writer.modelle.bericht import IOReport
        modell, seite = modell_laden(path)
        return ModellGeladen(modell, seite, {}, IOReport())
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
    return ModellGeladen(modell, geladen.page, geladen.meta, geladen.report)
