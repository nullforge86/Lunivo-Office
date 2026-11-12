"""Struktur der PDF-Ausgabe: Lesezeichen (Gliederung), Kommentar-Notizen und Sprungverweise. ``*_sammeln`` liest die Stellen aus der
gesetzten Kopie, ``gliederung_schreiben`` trägt sie in die fertige Datei ein (QPdfWriter kann das nicht selbst)."""
from __future__ import annotations

import os

from PySide6.QtGui import QTextBlock, QTextDocument

from lunivo_writer.editor.text.fragmente import absatz_fragmente
from lunivo_writer.editor.dokument.zusatz import P_KOMMENTAR
from lunivo_writer.modelle.seite import PageSettings, mm_to_px
from lunivo_writer.dienste.docx_leser import STYLE_PROP

PT_JE_PX = 0.75                                            # PDF-Punkte je Bildpunkt (96 dpi)
STILE_ANDERE = ("title", "subtitle", "quote", "Title", "Subtitle", "Quote")
LESEZEICHEN_TITEL_MAX = 120


def fluss_ort(ch: float, spalten: int = 1):
    """Ort im Textfluss einer Druckkopie: y → (Seite 1-basiert, y in der Spalte); beim Blattweg liefert ``Seitenlauf.ort`` dasselbe."""
    def ort(y: float) -> tuple[int, float]:
        logisch = int((y + 0.5) // ch) if ch else 0
        return logisch // spalten + 1, y - logisch * ch
    return ort


def _erste_kommentarstellen(d: QTextDocument) -> dict[int, int]:
    """{Kommentar-Id: erste Zeichenstelle} aus der Eigenschaft P_KOMMENTAR."""
    erste: dict[int, int] = {}
    b = d.firstBlock()
    while b.isValid():
        for f in absatz_fragmente(b):
            if f.charFormat().hasProperty(P_KOMMENTAR):
                erste.setdefault(int(f.charFormat().property(P_KOMMENTAR)), f.position())
        b = b.next()
    return erste


def kommentarstellen(d: QTextDocument, ch: float, liste: list[int], kommentare: dict, spalten: int = 1, ort=None) -> list[tuple[int, float, str]]:
    """[(Seitenindex, y in px auf der Textfläche, Text)] für die PDF-Notizen. `kommentare` = {Kommentar-Id: Text}; die Stelle
    wird über die Eigenschaft P_KOMMENTAR in der Kopie gefunden (Zeichenstellen des Originals passen dort nicht mehr)."""
    erste = _erste_kommentarstellen(d)
    ort = ort or fluss_ort(ch, spalten)
    out = []
    for kid, text in kommentare.items():
        von = erste.get(int(kid))
        if von is None:
            continue
        b = d.findBlock(von)
        if not b.isValid() or b.layout() is None:
            continue
        zeile = b.layout().lineForTextPosition(von - b.position())
        y = d.documentLayout().blockBoundingRect(b).top() + (zeile.y() if zeile.isValid() else 0)
        seite, yr = ort(y)
        if seite in liste:
            out.append((liste.index(seite), yr, text))
    return out


def _blockseite(lay, b: QTextBlock, ort, spalten: int = 1) -> int:
    """Seite (1-basiert), auf der der Absatz beginnt; ``ort`` ist die Ortsfunktion oder die Höhe einer Seite im Textfluss."""
    from lunivo_writer.editor.seite.seitenzahl import absatz_oben
    if not callable(ort):
        ort = fluss_ort(ort, spalten)
    return ort(absatz_oben(lay, b))[0]


def _stilname(b: QTextBlock) -> str:
    bf = b.blockFormat()
    return str(bf.property(STYLE_PROP)) if bf.hasProperty(STYLE_PROP) else ""


def _ist_stileintrag(b: QTextBlock, was: dict) -> bool:
    """Titel, Untertitel, Zitat („andere“) oder eigene Formatvorlage („eigene“) als Lesezeichen."""
    stil = _stilname(b)
    return bool(b.text().strip() and stil and ((was.get("andere") and stil in STILE_ANDERE)
                                               or (was.get("eigene") and stil.startswith("x:"))))


def _textmarken_anhaengen(b: QTextBlock, idx: int, out: list) -> None:
    for f in absatz_fragmente(b):
        if f.charFormat().isAnchor() and not f.charFormat().anchorHref():
            for n in f.charFormat().anchorNames():
                if not any(o[1] == n and o[0] == 0 for o in out):
                    out.append((0, n, idx, f.position()))


def _block_eintraege(b: QTextBlock, idx: int, was: dict, out: list) -> None:
    """Hängt die Lesezeichen des Absatzes (Überschrift, Stil, Textmarken) an ``out``: (Ebene, Titel, Seitenindex, Stelle)."""
    lv = b.blockFormat().headingLevel()
    if was.get("ueberschriften", True) and lv and b.text().strip():
        out.append((lv, b.text().strip(), idx, b.position()))
    if _ist_stileintrag(b, was):
        out.append((1, b.text().strip()[:LESEZEICHEN_TITEL_MAX], idx, b.position()))
    if was.get("textmarken"):
        _textmarken_anhaengen(b, idx, out)


def lesezeichen_sammeln(d: QTextDocument, ch: float, liste: list[int], was: dict, spalten: int = 1, ort=None) -> list[tuple[int, str, int]]:
    """[(Ebene, Titel, Seitenindex 0-basiert)] für die PDF-Gliederung: Überschriften und/oder Textmarken."""
    lay = d.documentLayout()
    ort = ort or fluss_ort(ch, spalten)
    out = []
    b = d.firstBlock()
    while b.isValid():
        seite = _blockseite(lay, b, ort)
        if seite in liste and b.isVisible():
            _block_eintraege(b, liste.index(seite), was, out)
        b = b.next()
    out.sort(key=lambda o: o[3])
    return [(lv, t, i) for lv, t, i, _p in out]


def _rand_pt(page: PageSettings) -> tuple[float, float]:
    return mm_to_px(page.margin_left_mm) * PT_JE_PX, mm_to_px(page.margin_top_mm) * PT_JE_PX


def _notizen_anfuegen(w, kommentare: list, page: PageSettings) -> None:
    from pypdf.annotations import Text
    ml, mt = _rand_pt(page)
    for seite, y, text in kommentare:
        if seite >= len(w.pages):
            continue
        hoehe = float(w.pages[seite].mediabox.height)
        oben = hoehe - mt - y * PT_JE_PX
        w.add_annotation(page_number=seite, annotation=Text(text=text, rect=(max(0, ml - 24), oben - 18, ml - 6, oben), open=False))


def _verweis_anfuegen(w, k: dict, ml: float, mt: float) -> None:
    from pypdf.annotations import Link
    from pypdf.generic import Fit
    if k["seite"] >= len(w.pages) or k["ziel_seite"] >= len(w.pages):
        return
    hoehe = float(w.pages[k["seite"]].mediabox.height)
    x1 = ml + k["x"] * PT_JE_PX
    y2 = hoehe - mt - k["y"] * PT_JE_PX
    ziel_h = float(w.pages[k["ziel_seite"]].mediabox.height)
    w.add_annotation(page_number=k["seite"], annotation=Link(
        rect=(x1, y2 - k["h"] * PT_JE_PX, x1 + max(4.0, k["w"] * PT_JE_PX), y2), target_page_index=k["ziel_seite"],
        fit=Fit.xyz(left=ml, top=ziel_h - mt - max(0.0, k["ziel_y"] - 4) * PT_JE_PX, zoom=0)))
    ann = w.pages[k["seite"]]["/Annots"][-1].get_object()
    ziel = ann.get("/Dest")
    if ziel is not None and isinstance(ziel[0], int):
        ziel[0] = w.pages[int(ziel[0])].indirect_reference        # Verweise im Dokument zeigen auf die Seite selbst, nicht auf ihre Nummer


def _verweise_anfuegen(w, links: list, page: PageSettings) -> None:
    ml, mt = _rand_pt(page)
    for k in links:
        _verweis_anfuegen(w, k, ml, mt)


def _gliederung_anfuegen(w, eintraege: list[tuple[int, str, int]]) -> None:
    eltern: dict[int, object] = {}
    for lv, titel, seite in eintraege:
        stufe = max(1, lv)                    # Textmarken (Ebene 0) stehen auf oberster Ebene
        vater = next((eltern[k] for k in range(stufe - 1, 0, -1) if k in eltern), None)
        eltern[stufe] = w.add_outline_item(titel, min(seite, len(w.pages) - 1), parent=vater)
        for k in [k for k in eltern if k > stufe]:
            del eltern[k]


def gliederung_schreiben(pfad: str, eintraege: list[tuple[int, str, int]], kommentare=None, page: PageSettings | None = None,
                         links: list | None = None) -> None:
    """Schreibt Lesezeichen und Kommentare in die fertige PDF (QPdfWriter kann das nicht selbst) — mit pypdf."""
    from pypdf import PdfReader, PdfWriter
    w = PdfWriter(clone_from=PdfReader(pfad))
    if kommentare and page is not None:
        _notizen_anfuegen(w, kommentare, page)
    if links and page is not None:
        _verweise_anfuegen(w, links, page)
    _gliederung_anfuegen(w, eintraege)
    tmp = pfad + ".tmp"
    with open(tmp, "wb") as fh:
        w.write(fh)
    os.replace(tmp, pfad)
