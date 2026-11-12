"""Abschnitte: Seiteneinrichtung, die mitten im Dokument wechseln kann.

Modell wie in DOCX, nur umgekehrt notiert: Ein Absatz mit B_ABSCHNITT ist der LETZTE Absatz eines Abschnitts; sein Wert (JSON) beschreibt
den Abschnitt, der danach beginnt — Beginn („naechste“, „fortlaufend“, „gerade“, „ungerade“) und Seiteneinrichtung. Der erste
Abschnitt hat keinen eigenen Eintrag, seine Einrichtung ist die des Dokuments (`ed.page`).

Grenze: Die Bearbeitungsansicht zeigt alle Abschnitte in der Seitengeometrie des ersten (Qt-Dokumente haben genau eine Seitengröße);
Seitenansicht, Druck, PDF und DOCX kennen die Maße jedes Abschnitts."""
from __future__ import annotations

import dataclasses
import json

from PySide6.QtGui import QImage, QTextCursor, QTextFormat

from lunivo_writer.modelle.seite import HeaderFooter, PageSettings

B_ABSCHNITT = QTextFormat.UserProperty + 35

TYPEN = {"naechste": "Nächste Seite", "fortlaufend": "Fortlaufend", "gerade": "Gerade Seite", "ungerade": "Ungerade Seite"}
DOCX_TYP = {"naechste": "nextPage", "fortlaufend": "continuous", "gerade": "evenPage", "ungerade": "oddPage"}
VOM_DOCX = {v: k for k, v in DOCX_TYP.items()}


# ---- Seiteneinrichtung <-> JSON ----------------------------------------------------------------------------------
_BILD_MARKE = "__bild__"                             # ein Bild einer Kopf-/Fußzeile steht im JSON als {_BILD_MARKE: Text}


def _bilder_zu_text(angabe: dict) -> dict:
    from lunivo_writer.editor.seite.wasserzeichen import bild_zu_text
    return {k: ({_BILD_MARKE: bild_zu_text(v)} if isinstance(v, QImage) else v) for k, v in angabe.items()}


def _bilder_aus_text(angabe: dict) -> dict:
    from lunivo_writer.editor.seite.wasserzeichen import bild_aus_text
    return {k: (bild_aus_text(v[_BILD_MARKE]) if isinstance(v, dict) and _BILD_MARKE in v else v) for k, v in angabe.items()}


def seite_zu_dict(ps: PageSettings) -> dict:
    """Die Einrichtung als JSON-fähiges Verzeichnis; die Bilder der Kopf-/Fußzeilen (``ps.bilder``) als Text."""
    d = dataclasses.asdict(dataclasses.replace(ps, bilder=[]))
    d["bilder"] = [_bilder_zu_text(a) for a in ps.bilder]
    return d


def seite_aus_dict(d: dict) -> PageSettings:
    ps = PageSettings()
    for f in dataclasses.fields(PageSettings):
        if f.name not in d:
            continue
        v = d[f.name]
        if f.name in ("header", "footer", "first_header", "first_footer", "even_header", "even_footer") and isinstance(v, dict):
            v = HeaderFooter(v.get("text", ""), v.get("align", "center"), dict(v.get("fmt") or {}),
                             [dict(r) for r in v.get("runs") or [] if isinstance(r, dict)])
        if f.name == "bilder":
            v = [_bilder_aus_text(a) for a in v or [] if isinstance(a, dict)]
        setattr(ps, f.name, v)
    return ps


def eintrag(typ: str, ps: PageSettings) -> str:
    return json.dumps({"typ": typ, "seite": seite_zu_dict(ps)}, ensure_ascii=False, separators=(",", ":"))


def lesen(blockformat) -> tuple[str, PageSettings] | None:
    if not blockformat.hasProperty(B_ABSCHNITT):
        return None
    try:
        d = json.loads(blockformat.property(B_ABSCHNITT))
        return d.get("typ", "naechste"), seite_aus_dict(d.get("seite", {}))
    except (ValueError, TypeError):
        return None


# ---- Abfragen ----------------------------------------------------------------------------------------------------
def umbrueche(doc) -> list[tuple[int, str, PageSettings]]:
    """[(Blocknummer, Beginn, Einrichtung des folgenden Abschnitts)] in Dokumentreihenfolge."""
    rev = doc.revision()                                 # Qt vergibt auch nach Undo/Redo neue Revisionen: der Stand gilt genau für diese
    zw = getattr(doc, "_umbrueche_zw", None)
    if zw is not None and zw[0] == rev:
        return list(zw[1])
    out = []
    b = doc.firstBlock()
    while b.isValid():
        e = lesen(b.blockFormat())
        if e:
            out.append((b.blockNumber(), e[0], e[1]))
        b = b.next()
    doc._umbrueche_zw = (rev, out)
    return list(out)


def anzahl(doc) -> int:
    return len(umbrueche(doc)) + 1


def index_bei(doc, position: int) -> int:
    """Nummer (0-basiert) des Abschnitts, in dem die Position liegt."""
    nr = doc.findBlock(position).blockNumber()
    return sum(1 for n, _t, _p in umbrueche(doc) if n < nr)


def einrichtung(doc, basis: PageSettings, index: int) -> PageSettings:
    """Einrichtung des Abschnitts `index` (0 = Dokumenteinrichtung); verknüpfte Kopf-/Fußzeilen werden vom Vorgänger übernommen."""
    ab = umbrueche(doc)
    ps = basis.copy()
    for k in range(min(index, len(ab))):
        neu = ab[k][2].copy()
        if neu.kopf_verknuepft:
            neu.header, neu.first_header, neu.diff_first = ps.header.kopie(), \
                ps.first_header.kopie(), ps.diff_first
            neu.even_header, neu.diff_even = ps.even_header.kopie(), ps.diff_even
        if neu.fuss_verknuepft:
            neu.footer, neu.first_footer = ps.footer.kopie(), ps.first_footer.kopie()
            neu.even_footer = ps.even_footer.kopie()
        ps = neu
    return ps


def alle_einrichtungen(doc, basis: PageSettings) -> list[tuple[str, PageSettings]]:
    """[(Beginn, Einrichtung)] für jeden Abschnitt (der erste mit Beginn „naechste“)."""
    ab = umbrueche(doc)
    out = [("naechste", basis.copy())]
    for k in range(len(ab)):
        out.append((ab[k][1], einrichtung(doc, basis, k + 1)))
    return out


def beginn(doc, index: int) -> int:
    """Zeichenposition, an der Abschnitt `index` beginnt."""
    if index <= 0:
        return 0
    ab = umbrueche(doc)
    b = doc.findBlockByNumber(ab[min(index, len(ab)) - 1][0]).next()
    return b.position() if b.isValid() else doc.characterCount() - 1


def ende(doc, index: int) -> int:
    ab = umbrueche(doc)
    if index >= len(ab):
        return doc.characterCount() - 1
    b = doc.findBlockByNumber(ab[index][0])
    return b.position() + b.length() - 1


# ---- Ändern ------------------------------------------------------------------------------------------------------
def _setze(cursor: QTextCursor, wert: str | None) -> None:
    bf = cursor.blockFormat()
    if wert is None:
        bf.clearProperty(B_ABSCHNITT)
    else:
        bf.setProperty(B_ABSCHNITT, wert)
    cursor.setBlockFormat(bf)
    cursor.document()._umbrueche_zw = None               # eine reine Formatänderung erhöht die Revision nicht zuverlässig: Zwischenspeicher verwerfen


def einfuegen(doc, cursor: QTextCursor, typ: str, basis: PageSettings) -> int:
    """Abschnittsumbruch an der Schreibmarke: der Absatz wird geteilt, der erste Teil beschließt den Abschnitt.
    Der neue Abschnitt übernimmt die Einrichtung des aktuellen. → Nummer des neuen Abschnitts."""
    index = index_bei(doc, cursor.position())
    aktuell = einrichtung(doc, basis, index)
    c = QTextCursor(cursor)
    c.beginEditBlock()
    vorher = c.blockFormat().property(B_ABSCHNITT) if c.blockFormat().hasProperty(B_ABSCHNITT) else None
    c.insertBlock()
    zweiter = QTextCursor(c)
    erster = QTextCursor(c)
    erster.movePosition(QTextCursor.PreviousBlock)
    _setze(erster, eintrag(typ, aktuell))
    _setze(zweiter, vorher)                              # der alte Umbruch beschließt jetzt den (neuen) zweiten Teil
    c.endEditBlock()
    cursor.setPosition(zweiter.position())
    return index + 1


def einfuegen_an(doc, position: int, typ: str, basis: PageSettings) -> int:
    """Abschnitt ab ``position`` beginnen lassen (z. B. am Anfang der aktuellen Seite). Steht die Stelle am Anfang eines Absatzes, beschließt
    der Absatz davor den alten Abschnitt (kein leerer Absatz dazwischen); beginnt dort schon ein Abschnitt, bleibt alles. → Nummer des
    Abschnitts, der an ``position`` beginnt."""
    b = doc.findBlock(position)
    if position == b.position():
        vor = b.previous()
        if not vor.isValid():
            return 0
        index = index_bei(doc, position)
        if lesen(vor.blockFormat()):
            return index
        c = QTextCursor(vor)
        c.beginEditBlock()
        _setze(c, eintrag(typ, einrichtung(doc, basis, index)))
        c.endEditBlock()
        return index + 1
    c = QTextCursor(doc)
    c.setPosition(position)
    return einfuegen(doc, c, typ, basis)


def entfernen(doc, index: int) -> bool:
    """Den Umbruch am Ende von Abschnitt `index` entfernen (ist es der letzte, den davor): die beiden Abschnitte werden einer
    und behalten die Einrichtung des früheren."""
    ab = umbrueche(doc)
    if not ab:
        return False
    k = index if index < len(ab) else len(ab) - 1
    c = QTextCursor(doc.findBlockByNumber(ab[k][0]))
    c.beginEditBlock()
    _setze(c, None)
    c.endEditBlock()
    return True


def setzen(doc, index: int, ps: PageSettings, typ: str | None = None) -> bool:
    """Einrichtung (und Beginn) eines Abschnitts ab dem zweiten ändern; für den ersten gilt `ed.page`."""
    ab = umbrueche(doc)
    if index < 1 or index > len(ab):
        return False
    nr, alt_typ, _alt = ab[index - 1]
    c = QTextCursor(doc.findBlockByNumber(nr))
    _setze(c, eintrag(typ or alt_typ, ps))
    return True


# ---- Ausgabe: das Dokument in Teile mit je eigener Seitengeometrie zerlegen ----------------------------------------------
def teile(qdoc, basis: PageSettings) -> tuple[list[tuple[object, PageSettings, str]], list[str]]:
    """Für Seitenansicht, Druck und PDF: [(Dokument, Einrichtung, Beginn)] je Abschnitt und Hinweise.

    Ein „fortlaufender“ Umbruch zu einem Abschnitt mit gleicher Geometrie wird mit dem vorigen zu einem Teil (kein Seitenwechsel).
    Wechselt bei „fortlaufend“ die Geometrie (z. B. die Spaltenzahl), beginnt der Abschnitt in der Ausgabe auf einer neuen Seite —
    ein Seitenteil mit zwei Spaltenzahlen gibt es hier nicht. Die Gliederung kommt aus ``editor/layout/seitenplan.py``."""
    if not umbrueche(qdoc):
        return [(qdoc, basis, "naechste")], []
    from lunivo_writer.editor.layout.seitenplan import Seitenplan
    plan = Seitenplan.aus_dokument(qdoc, basis)             # die eine Quelle für die Gliederung in Bereiche
    hinweise = plan.hinweise
    ranges = [(br.beginn, br.seite, br.von_abschnitt, br.bis_abschnitt) for br in plan.bereiche]
    out = []
    for typ, ps, a, b in ranges:
        d = qdoc.clone()
        von, bis = beginn(qdoc, a), ende(qdoc, b)
        c = QTextCursor(d)
        c.setPosition(bis); c.movePosition(QTextCursor.End, QTextCursor.KeepAnchor); c.removeSelectedText()
        if von:
            c.setPosition(0); c.setPosition(von, QTextCursor.KeepAnchor); c.removeSelectedText()
        blk = d.firstBlock()                             # die Umbruchmarken gehören zur Zerlegung, nicht zum Teil
        while blk.isValid():
            if blk.blockFormat().hasProperty(B_ABSCHNITT):
                cc = QTextCursor(blk); _setze(cc, None)
            blk = blk.next()
        erster = QTextCursor(d.firstBlock())                 # ein Teil beginnt ohnehin auf einer neuen Seite; ein Umbruch davor gäbe ein leeres Blatt
        bf = erster.blockFormat()
        if bf.pageBreakPolicy() & QTextFormat.PageBreak_AlwaysBefore:
            bf.setPageBreakPolicy(bf.pageBreakPolicy() & ~QTextFormat.PageBreak_AlwaysBefore); erster.setBlockFormat(bf)
        out.append((d, ps, typ))
    return out, hinweise
