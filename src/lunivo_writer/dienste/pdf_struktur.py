"""Struktur der PDF-Ausgabe, Qt-frei: Lesezeichen (Gliederung), Kommentar-Notizen, Hyperlinks und Sprungverweise zu Fuß- und Endnoten.

``struktur_sammeln`` liest die Stellen aus dem maßgeblichen ``Dokument`` und dem Ergebnis der Layoutberechnung (``core.layout.Ergebnis``);
``struktur_schreiben`` trägt sie mit pypdf in die fertige Datei ein (``QPdfWriter`` kann das nicht selbst). Es gibt keine zweite Dokumentkopie:
Seiten und Orte stammen aus demselben Layout, das auch Zeichenfläche, Druck und PDF zeichnet."""
from __future__ import annotations

import os

from lunivo_writer.core.document.dokument import InlineObjekt
from lunivo_writer.core.document.formatvorlagen import ueberschriftsebene

PT_JE_PX = 0.75                                             # PDF-Punkte je Bildpunkt (96 dpi)
STILE_ANDERE = ("title", "subtitle", "quote", "Title", "Subtitle", "Quote", "Titel", "Untertitel", "Zitat")
LESEZEICHEN_TITEL_MAX = 120
EXTERN = ("://", "mailto:", "tel:")


class PdfStruktur:
    """Die gesammelten Stellen, alle Seitenangaben 0-basiert in der geschriebenen PDF, y und x in Bildpunkten auf dem Blatt."""

    def __init__(self) -> None:
        self.lesezeichen: list = []        # (Ebene, Titel, Seite, y)
        self.notizen: list = []            # (Seite, x, y, Text)
        self.verweise: list = []           # (Seite, Rechteck (x, y, b, h), Ziel) — Ziel: ("uri", Adresse) | ("seite", Seite, y)

    def leer(self) -> bool:
        return not (self.lesezeichen or self.notizen or self.verweise)


def _laeufe(absatz):
    """(Anfang, Ende, Lauf) der Textläufe mit Zeichenformat; Objekte zählen als ein Zeichen."""
    stelle = 0
    for x in absatz.inhalte:
        n = 1 if isinstance(x, InlineObjekt) else len(x.text)
        yield stelle, stelle + n, x
        stelle += n


def _zeilen_rechtecke(ort, von: int, bis: int):
    """Je Zeile, die den Bereich [von, bis) berührt: (Seite, x, y, Breite, Höhe) auf dem Blatt."""
    satz = ort.satz
    for seite, zi, r in ort.zeilen:
        z = satz.zeilen[zi]
        a, b = max(von, z.box.start), min(bis, z.ende)
        if a >= b and not (von == bis and z.box.start <= von <= z.ende):
            continue
        x1, x2 = r.x + satz.cursor_x(a, zi), r.x + satz.cursor_x(b, zi)
        yield seite, min(x1, x2), r.y, max(abs(x2 - x1), 4.0), r.height


def struktur_sammeln(dokument, erg, optionen: dict, erste: int = 1, letzte: int | None = None) -> PdfStruktur:
    """Sammelt, was ``optionen`` verlangt: ``lesezeichen`` (``{"ueberschriften", "textmarken", "andere", "eigene"}`` oder ``None``), ``kommentare``,
    ``hyperlinks``, ``notenlinks``. ``erste``/``letzte``: der geschriebene Seitenbereich (1-basiert); Stellen außerhalb entfallen."""
    st = PdfStruktur()
    letzte = len(erg.seiten) if letzte is None else min(len(erg.seiten), letzte)

    def pdf_seite(index: int) -> int | None:
        return index - (max(1, erste) - 1) if max(1, erste) - 1 <= index < letzte else None

    was = optionen.get("lesezeichen") or {}
    noten_ziel: dict = {}
    for s in erg.seiten:
        for p in s.plaetze:
            if p.art in ("fussnote", "endnote") and (p.art[0], p.block_id) not in noten_ziel:
                noten_ziel[(("f" if p.art == "fussnote" else "e"), p.block_id)] = (s.index, p.rect.y)
    marken: dict = {}                                    # Name der Textmarke → (Seite, y)
    erste_notiz: set = set()
    verweise: list = []
    for absatz in dokument.absaetze():
        ort = erg.absaetze.get(absatz.id)
        if ort is None or not ort.zeilen:
            continue
        seite0, _zi, r0 = ort.zeilen[0]
        ps = pdf_seite(seite0)
        text = absatz.text().replace("￼", "").strip()
        if ps is not None and was:
            ebene = ueberschriftsebene(dokument, absatz)
            stil = str(absatz.format.get("vorlage", ""))
            if was.get("ueberschriften", True) and ebene and text:
                st.lesezeichen.append((ebene, text[:LESEZEICHEN_TITEL_MAX], ps, r0.y))
            elif text and ((was.get("andere") and stil in STILE_ANDERE) or (was.get("eigene") and stil.startswith("x:"))):
                st.lesezeichen.append((1, text[:LESEZEICHEN_TITEL_MAX], ps, r0.y))
        for von, bis, x in _laeufe(absatz):
            fmt = x.format
            for name in fmt.get("anker") or ():
                marken.setdefault(name, (seite0, r0.y))
                if was.get("textmarken") and ps is not None and not any(e[0] == 0 and e[1] == name for e in st.lesezeichen):
                    st.lesezeichen.append((0, str(name), ps, r0.y))
            kid = fmt.get("kommentar")
            if optionen.get("kommentare") and kid is not None and kid not in erste_notiz and int(kid) in dokument.kommentare and ps is not None:
                erste_notiz.add(kid)
                k = dokument.kommentare[int(kid)]
                st.notizen.append((ps, 0.0, r0.y, (f"{k.autor}: " if k.autor else "") + k.text))
            ziel_text = fmt.get("link")
            if optionen.get("hyperlinks", True) and ziel_text:
                for sx, x0, y0, b, h in _zeilen_rechtecke(ort, von, bis):
                    if pdf_seite(sx) is not None:
                        verweise.append((pdf_seite(sx), (x0, y0, b, h), ("link", str(ziel_text))))
            note = fmt.get("note")
            if optionen.get("notenlinks", True) and note:
                art, _, nid = str(note).partition(":")
                ziel = noten_ziel.get((art, int(nid))) if nid.isdigit() else None
                if ziel is not None and pdf_seite(ziel[0]) is not None:
                    for sx, x0, y0, b, h in _zeilen_rechtecke(ort, von, bis):
                        if pdf_seite(sx) is not None:
                            verweise.append((pdf_seite(sx), (x0, y0, b, h), ("seite", pdf_seite(ziel[0]), ziel[1])))
    for seite, rechteck, ziel in verweise:               # Textmarken sind erst nach dem ganzen Durchlauf bekannt
        if ziel[0] == "link":
            adresse = ziel[1]
            if adresse.startswith("#") or not any(m in adresse for m in EXTERN):
                name = adresse.lstrip("#")
                if name in marken and pdf_seite(marken[name][0]) is not None:
                    st.verweise.append((seite, rechteck, ("seite", pdf_seite(marken[name][0]), marken[name][1])))
            else:
                st.verweise.append((seite, rechteck, ("uri", adresse)))
        else:
            st.verweise.append((seite, rechteck, ziel))
    st.lesezeichen.sort(key=lambda e: (e[2], e[3]))
    return st


def _gliederung_anfuegen(w, eintraege: list) -> None:
    eltern: dict = {}
    for ebene, titel, seite, _y in eintraege:
        stufe = max(1, ebene)                             # Textmarken (Ebene 0) stehen auf oberster Ebene
        vater = next((eltern[k] for k in range(stufe - 1, 0, -1) if k in eltern), None)
        eltern[stufe] = w.add_outline_item(titel, min(seite, len(w.pages) - 1), parent=vater)
        for k in [k for k in eltern if k > stufe]:
            del eltern[k]


def _verweise_anfuegen(w, verweise: list) -> None:
    from pypdf.annotations import Link
    from pypdf.generic import Fit
    for seite, (x, y, b, h), ziel in verweise:
        if seite >= len(w.pages):
            continue
        hoehe = float(w.pages[seite].mediabox.height)
        rect = (x * PT_JE_PX, hoehe - (y + h) * PT_JE_PX, (x + b) * PT_JE_PX, hoehe - y * PT_JE_PX)
        if ziel[0] == "uri":
            w.add_annotation(page_number=seite, annotation=Link(rect=rect, url=ziel[1]))
            continue
        if ziel[1] >= len(w.pages):
            continue
        ziel_h = float(w.pages[ziel[1]].mediabox.height)
        w.add_annotation(page_number=seite, annotation=Link(rect=rect, target_page_index=ziel[1],
                                                           fit=Fit.xyz(left=0, top=ziel_h - max(0.0, ziel[2] - 4) * PT_JE_PX, zoom=0)))
        ann = w.pages[seite]["/Annots"][-1].get_object()
        d = ann.get("/Dest")
        if d is not None and isinstance(d[0], int):
            d[0] = w.pages[int(d[0])].indirect_reference  # Verweise im Dokument zeigen auf die Seite selbst, nicht auf ihre Nummer


def _notizen_anfuegen(w, notizen: list) -> None:
    from pypdf.annotations import Text
    for seite, _x, y, text in notizen:
        if seite >= len(w.pages):
            continue
        oben = float(w.pages[seite].mediabox.height) - y * PT_JE_PX
        w.add_annotation(page_number=seite, annotation=Text(text=text, rect=(6.0, oben - 18, 24.0, oben), open=False))


def struktur_schreiben(pfad: str, st: PdfStruktur) -> None:
    """Schreibt Lesezeichen, Notizen und Verweise in die fertige PDF (mit pypdf, an Ort und Stelle)."""
    if st.leer():
        return
    from pypdf import PdfReader, PdfWriter
    w = PdfWriter(clone_from=PdfReader(pfad))
    _notizen_anfuegen(w, st.notizen)
    _verweise_anfuegen(w, st.verweise)
    _gliederung_anfuegen(w, st.lesezeichen)
    tmp = pfad + ".tmp"
    with open(tmp, "wb") as fh:
        w.write(fh)
    os.replace(tmp, pfad)
