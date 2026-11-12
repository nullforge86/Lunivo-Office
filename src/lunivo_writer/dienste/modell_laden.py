"""Dateien als Qt-freies Dokumentenmodell laden (Phase 5 der Qt-Entkopplung, siehe ``dokumentation/architektur/qt-entkopplung.md``).

``lade_modell`` ist die Schnittstelle für Code, der den Inhalt einer DOCX-, DOTX-, DOCM-, ODT-, FODT-, RTF- oder TXT-Datei als ``core.document.Document`` braucht und kein
``QTextDocument``. Gelesen wird noch von den bestehenden Lesern (sie schreiben in ein ``QTextDocument``); die Umwandlung ins Modell übernimmt die verlustfreie Brücke
``adapter/qt/dokument.py``. Dadurch bleibt jeder Leser unverändert und meldet wie bisher alles Nichtübernommene im ``IOReport``."""
from __future__ import annotations

from dataclasses import dataclass

from lunivo_writer.adapter.qt.dokument import document_from_qt
from lunivo_writer.core.document import Document
from lunivo_writer.dienste.datei_dienst import load


@dataclass
class ModellGeladen:
    document: Document
    page: object            # ``PageSettings`` des ersten Abschnitts
    meta: dict
    report: object          # ``IOReport``: was nicht übernommen wurde


def lade_modell(path: str, kennwort: str | None = None) -> ModellGeladen:
    """Datei laden und als Modell liefern. Wirft ``DocumentIOError`` wie ``datei_dienst.load``."""
    geladen = load(path, kennwort)
    if geladen.modell is not None:
        modell = geladen.modell
    else:
        modell = document_from_qt(geladen.doc, geladen.page)
        from lunivo_writer.core.document import Footnote
        noten = geladen.meta.get("noten", {})
        modell.notes = [Footnote(int(nid), art, str(text))
                        for art, eintraege in noten.items() if art in ("f", "e")
                        for nid, text in eintraege.items()]
    return ModellGeladen(modell, geladen.page, geladen.meta, geladen.report)
