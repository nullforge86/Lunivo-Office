"""Gemeinsame Hilfen der Tests, die mit dem Dokumentenmodell arbeiten (``core.document.Dokument``): Dokumente bauen, als PDF oder DOCX schreiben und wieder lesen.
Alles läuft über die Qt-freie Architektur; ein Qt-Textdokument kommt nicht vor."""
from __future__ import annotations

from lunivo_writer.core.document import Dokument, neues_dokument
from lunivo_writer.core.editing import Bearbeitungssitzung
from lunivo_writer.modelle.seite import PageSettings


def sitzung(text: str = "", seite: PageSettings | None = None) -> Bearbeitungssitzung:
    """Eine Sitzung über einem neuen Dokument; ``text`` steht darin (``\\n`` beginnt einen neuen Absatz)."""
    s = Bearbeitungssitzung(neues_dokument(seite))
    if text:
        s.text_einfuegen(text)
    return s


def dokument(text: str = "", seite: PageSettings | None = None) -> Dokument:
    return sitzung(text, seite).dokument


def seiten_dokument(anzahl: int, vorlage: str = "Seite {n}", seite: PageSettings | None = None) -> Dokument:
    """Ein Dokument mit ``anzahl`` Absätzen, jeder ab dem zweiten mit Seitenumbruch davor (also ``anzahl`` Seiten)."""
    s = sitzung("\n".join(vorlage.format(n=i + 1) for i in range(anzahl)), seite)
    for i, a in enumerate(s.dokument.absaetze()):
        if i:
            s.absatzformat_anwenden({"seitenumbruch_vor": True}, absatz_ids=[a.id])
    return s.dokument


def seitenzahl(dok: Dokument) -> int:
    from lunivo_writer.core.layout import LayoutEngine
    return len(LayoutEngine().berechnen(dok).seiten)


def als_pdf(dok: Dokument, pfad, titel: str = "", autor: str = "", **kw) -> int:
    """Das Dokument über die Ausgabeschnittstelle als PDF schreiben (``erste``/``letzte``: Seitenbereich); → Zahl der Seiten."""
    from lunivo_writer.adapter.qt.pdf_ausgabe import dokument_als_pdf
    return dokument_als_pdf(dok, str(pfad), titel, autor, **kw)


def docx_rundlauf(dok: Dokument, tmp_path, name: str = "rundlauf.docx", seite: PageSettings | None = None, meta: dict | None = None):
    """Das Dokument als DOCX schreiben und wieder lesen: → (gelesenes ``Dokument``, Bericht des Schreibens, Bericht des Lesens, Pfad)."""
    from lunivo_writer.dienste.docx_modell_schreiber import docx_dokument_daten
    from lunivo_writer.dienste.modell_laden import lade_modell
    daten, schreib_bericht = docx_dokument_daten(dok, seite or dok.abschnitte[0].seite, meta or {})
    pfad = tmp_path / name
    pfad.write_bytes(daten)
    geladen = lade_modell(str(pfad))
    return geladen.document, schreib_bericht, geladen.report, pfad
