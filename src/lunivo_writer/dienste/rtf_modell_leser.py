"""Qt-freier RTF-Leser für Text, Absätze, Listen und Tabellen."""
from __future__ import annotations

from lunivo_writer.core.document import CharacterFormat, Document, Image, ListFormat, Paragraph, ParagraphFormat, Section, Table, TableCell, TableRow, TextRun
from lunivo_writer.core.document.values import Brush, Color
from lunivo_writer.dienste.rtf.leser import _daten_lesen
from lunivo_writer.dienste.rtf.modell import Absatz, NichtImModell, Tabelle as RtfTabelle, Ziel
from lunivo_writer.dienste.rtf.zerleger import Zerleger
from lunivo_writer.modelle.seite import HeaderFooter


def _farbe(wert: str | None) -> Color | None:
    if not isinstance(wert, str) or len(wert) != 7 or wert[0] != "#":
        return None
    try:
        return Color(int(wert[1:3], 16), int(wert[3:5], 16), int(wert[5:7], 16))
    except ValueError:
        return None


def _zeichenformat(z: Zerleger, roh: tuple) -> CharacterFormat:
    p = dict(roh)
    familie = z.schriften.get(p.get("f"), z.schriften.get(z.standard_schrift, "Liberation Serif"))
    groesse = max(1.0, float(p.get("fs", 24)) / 2)
    gewicht = 700 if p.get("b") else 400
    fg = _farbe(z.farben[p["cf"]]) if isinstance(p.get("cf"), int) and 0 <= p["cf"] < len(z.farben) else None
    hintergrund = _farbe(z.farben[p["cb"]]) if isinstance(p.get("cb"), int) and 0 <= p["cb"] < len(z.farben) else None
    props = {"FontFamilies": (familie,), "FontPointSize": groesse, "FontWeight": gewicht,
             "FontItalic": bool(p.get("i")), "FontUnderline": bool(p.get("ul")),
             "FontStrikeOut": bool(p.get("strike"))}
    if hintergrund is not None:
        props["BackgroundBrush"] = Brush(1, hintergrund)
    if p.get("va") == "super":
        props["TextVerticalAlignment"] = 1
    elif p.get("va") == "sub":
        props["TextVerticalAlignment"] = 2
    return CharacterFormat(props, familie, groesse, gewicht, bool(p.get("i")), fg, bool(p.get("ul")))


def _absatzformat(z: Zerleger, roh: dict, list_id: int | None) -> ParagraphFormat:
    ausrichtung = {"ql": "left", "qc": "center", "qr": "right", "qj": "justify"}.get(roh.get("q"), "left")
    props = {}
    if roh.get("pagebb") or roh.get("pagebb_einmal"):
        props["PageBreakPolicy"] = 0x1
    if roh.get("h"):
        props["HeadingLevel"] = int(roh["h"])
    return ParagraphFormat(
        properties=props,
        list_id=list_id,
        alignment=ausrichtung,
        space_before_px=float(roh["sb"]) / 15 if roh.get("sb") else None,
        space_after_px=float(roh["sa"]) / 15 if roh.get("sa") else None,
        left_indent_px=float(roh["li"]) / 15 if roh.get("li") else None,
        right_indent_px=float(roh["ri"]) / 15 if roh.get("ri") else None,
        first_line_indent_px=float(roh["fi"]) / 15 if roh.get("fi") else None,
    )


def _absatz(z: Zerleger, a: Absatz, listen: dict[int, ListFormat], ids: dict[str, int]) -> Paragraph:
    lid = None
    if a.liste:
        lid = ids.setdefault(a.liste, len(ids) + 1)
        if lid not in listen:
            listen[lid] = ListFormat({"ListStyle": -4 if a.liste == "zahl" else -1})
    laeufe = []
    for lauf in a.laeufe:
        if lauf[0] == "t" and lauf[1]:
            laeufe.append(TextRun(lauf[1], _zeichenformat(z, lauf[2])))
        elif lauf[0] == "b_raw":
            daten, (breite, hoehe), art = lauf[1], lauf[2], lauf[3]
            laeufe.append(Image(daten, CharacterFormat({"ImageWidth": breite, "ImageHeight": hoehe}), daten, art))
    format = _absatzformat(z, a.props, lid)
    if laeufe:
        format.char_format = laeufe[0].format
    return Paragraph(format, laeufe)


def _zelle(z: Zerleger, absatze: list[Absatz], listen: dict[int, ListFormat], ids: dict[str, int]) -> list:
    return [_absatz(z, a, listen, ids) for a in absatze] or [Paragraph()]


def _ziel(z: Zerleger, ziel: Ziel, listen: dict[int, ListFormat], ids: dict[str, int]) -> list:
    bloecke = []
    for teil in ziel.teile:
        if isinstance(teil, Absatz):
            bloecke.append(_absatz(z, teil, listen, ids))
            continue
        if not isinstance(teil, RtfTabelle):
            raise NichtImModell(f"Unbekannter RTF-Block: {type(teil).__name__}")
        zeilen = []
        for r, (zellen, _grenzen) in enumerate(teil.zeilen):
            zeile = TableRow()
            for c, absatze in enumerate(zellen):
                zeile.cells.append(TableCell(r, c, content=_zelle(z, absatze, listen, ids)))
            zeilen.append(zeile)
        bloecke.append(Table(max(1, len(zeilen)), max((len(r.cells) for r in zeilen), default=1), table_rows=zeilen))
    return bloecke


def _kopf_fuss(ziel: Ziel) -> HeaderFooter:
    if any(lauf[0] != "t" for absatz in ziel.teile if isinstance(absatz, Absatz) for lauf in absatz.laeufe):
        raise NichtImModell("Bilder in RTF-Kopf- oder Fußzeilen")
    if any(lauf[0] != "t" for lauf in ziel.laeufe):
        raise NichtImModell("Bilder in RTF-Kopf- oder Fußzeilen")
    absatzteile = [t for t in ziel.teile if isinstance(t, Absatz)]
    if ziel.laeufe:
        absatzteile.append(Absatz({}, ziel.laeufe, None))
    text = "\n".join("".join(lauf[1] for lauf in a.laeufe if lauf[0] == "t").replace("\u2028", "\n") for a in absatzteile).strip("\n")
    ausrichtung = {"qc": "center", "qr": "right", "qj": "justify"}.get(absatzteile[0].props.get("q", "") if absatzteile else "", "left")
    return HeaderFooter(text, ausrichtung)


def lese_rtf_modell(path: str):
    """Lädt RTF ohne Qt; gibt bei nicht unterstützten Bildinhalten ``None`` für den bisherigen Qt-Leser zurück."""
    from lunivo_writer.core.document import Section
    from lunivo_writer.core.document import Document as KernDokument
    from lunivo_writer.dienste.rtf.modell import NichtImModell
    from lunivo_writer.modelle.bericht import IOReport

    z = Zerleger(_daten_lesen(path), modell=True)
    try:
        z.run()
    except NichtImModell:
        return None
    listen: dict[int, ListFormat] = {}
    ids: dict[str, int] = {}
    bloecke = _ziel(z, z.haupt, listen, ids)
    page = z.seite
    try:
        for key, (ziel, _props) in z.kopf_fuss.items():
            if "?" in key:
                basis = key.split("?", 1)[0]
                if basis in z.kopf_fuss:
                    continue
                key = basis
            setattr(page, key, _kopf_fuss(ziel))
    except NichtImModell:
        return None
    page.diff_first = z.titel_erste
    if not z.titel_erste:
        page.first_header, page.first_footer = HeaderFooter(), HeaderFooter()
    familie = z.schriften.get(z.standard_schrift, "Liberation Serif")
    grund = CharacterFormat({"FontFamilies": (familie,), "FontPointSize": 12.0}, family=familie, size_pt=12.0)
    modell = KernDokument([Section("naechste", page, bloecke)], default_format=grund, document_margin=0.0, lists=listen)
    meta = dict(z.meta)
    return modell, page, meta, z.report if z.report is not None else IOReport()
