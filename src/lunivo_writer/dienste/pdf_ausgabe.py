"""PDF-Ausgabe des Dokuments ohne Qt: dieselbe Layoutberechnung und derselbe Renderer des Kerns wie die Zeichenfläche, geschrieben von ``core.rendering.pdfziel``."""
from __future__ import annotations

from lunivo_writer.core.document import Dokument
from lunivo_writer.core.layout import LayoutEngine
from lunivo_writer.core.layout import formatwerte as F
from lunivo_writer.core.rendering import DokumentRenderer
from lunivo_writer.core.rendering.pdfziel import PdfZiel


def dokument_als_pdf(dokument: Dokument, ziel: str, titel: str = "", autor: str = "", engine=None, erste: int = 1, letzte: int | None = None, struktur: dict | None = None,
                     hinweise: list | None = None, seiten: list | None = None, layout_optionen: dict | None = None) -> int:
    """Das Dokument als PDF schreiben, ein Blatt je Seite. ``erste`` und ``letzte``: Seitenbereich (1-basiert, einschließlich). ``struktur``: Lesezeichen, Kommentarnotizen,
    Hyperlinks und Notenverweise (siehe ``dienste.pdf_struktur.struktur_sammeln``); sie werden nach dem Schreiben in die Datei eingetragen. ``hinweise`` nimmt auf, was die
    PDF-Ausgabe nicht wiedergibt. ``seiten``: bestimmte Seiten (1-basiert) in dieser Reihenfolge statt eines Bereichs (Druck); ``layout_optionen``: Ansichtsoptionen des Layouts
    (zum Beispiel ``{"versteckt": True}``). Gibt die Zahl der geschriebenen Seiten zurück."""
    layout = LayoutEngine(engine, layout_optionen)
    erg = layout.berechnen(dokument)
    renderer = DokumentRenderer(layout.engine)
    pdf = PdfZiel(layout.engine, titel or str(dokument.eigenschaften.get("title", "")), autor or str(dokument.eigenschaften.get("author", "")))
    grund = F.schrift(dict(dokument.standardformat))
    geschrieben = 0
    if seiten is not None:
        auswahl = [erg.seiten[n - 1] for n in seiten if 1 <= n <= len(erg.seiten)]
    else:
        auswahl = [x for x in erg.seiten if not (x.index + 1 < max(1, erste) or (letzte is not None and x.index + 1 > letzte))]
    for seite in auswahl:
        geschrieben += 1
        einr = seite.einrichtung
        pdf.neue_seite(einr.width_mm * 96 / 25.4, einr.height_mm * 96 / 25.4)
        renderer.zeichne_seite(pdf, dokument, erg, seite.index, grund)
    if geschrieben:
        pdf.speichern(ziel)
    if hinweise is not None:
        hinweise.extend(dict.fromkeys(pdf.hinweise))
    if struktur and geschrieben:
        from lunivo_writer.dienste import pdf_struktur as PS
        PS.struktur_schreiben(ziel, PS.struktur_sammeln(dokument, erg, struktur, erste, letzte))
    return geschrieben
