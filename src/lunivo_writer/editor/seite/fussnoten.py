"""Fuß- und Endnoten in der Kopie für Seitenzählung, Seitenansicht, PDF und Druck: gesammelt am Textende, unten auf der Seite
und als Sprungverweise im PDF. Die Marken im Text tragen ``P_NOTE`` („f:<Id>“ oder „e:<Id>“)."""
from __future__ import annotations

import bisect
from typing import Callable, Iterator

from PySide6.QtCore import QSizeF
from PySide6.QtGui import QFont, QTextBlock, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument, QTextFormat, QTextFragment

from lunivo_writer.editor.dokument.zusatz import B_NOTENZIEL, P_NOTE, roemisch
from lunivo_writer.editor.text.fragmente import absatz_fragmente
from lunivo_writer.modelle.seite import PageSettings

from lunivo_writer.core.layout.seitenumbruch import NOTEN_ABSTAND, NOTEN_SCHRIFT, NOTEN_SEITENANTEIL, NOTEN_TRENNER   # noqa: E402,F401  (die Maße der Fußnoten stehen einmal, im Kern)
NOTEN_RUNDEN = 60              # höchstens so viele Umbruchrunden


def fussnoten_am_fuss(page: PageSettings, noten: dict | None) -> bool:
    """Fußnoten am Seitenfuß gibt es bei einer Spalte; bei mehreren Spalten stehen sie gesammelt am Textende."""
    return bool(noten and noten.get("f")) and int(page.spalten) <= 1


def _notenfragmente(d: QTextDocument) -> Iterator[tuple[QTextBlock, QTextFragment, str, str]]:
    """(Absatz, Textstück, Art „f“/„e“, Id als Text) jeder Notenmarke in Textreihenfolge."""
    b = d.firstBlock()
    while b.isValid():
        for f in absatz_fragmente(b):
            if f.charFormat().hasProperty(P_NOTE):
                art, _, nid = f.charFormat().stringProperty(P_NOTE).partition(":")
                yield b, f, art, nid
        b = b.next()


def _notenabschnitt(c: QTextCursor, art: str, titel: str, ids: list[int], noten: dict) -> None:
    c.insertBlock()
    kopf = QTextCharFormat(); kopf.setFontWeight(QFont.Bold); kopf.setFontPointSize(10)
    c.insertText("—" * 10 + " " + titel, kopf)
    for n, nid in enumerate(ids, start=1):
        bf = QTextBlockFormat(); bf.setProperty(B_NOTENZIEL, f"{art}:{nid}")        # Sprungziel für die PDF-Verknüpfung
        c.insertBlock(bf)
        f = QTextCharFormat(); f.setFontPointSize(9)
        c.insertText(f"{n if art == 'f' else roemisch(n)}  {(noten.get(art, {}) or {}).get(nid, '')}", f)


def noten_anhaengen(d: QTextDocument, noten: dict | None, arten: tuple = ("f", "e")) -> None:
    """Fuß- und Endnoten gesammelt am Textende (nur in der Kopie für Seitenzählung, PDF und Druck). Fußnoten stehen bei einer
    Spalte am Seitenfuß (fussnoten_am_seitenende) und werden dann hier nicht angehängt (arten=(„e“,))."""
    if not noten or not (noten.get("f") or noten.get("e")):
        return
    stellen = {"f": [], "e": []}
    for _b, _f, art, nid in _notenfragmente(d):
        stellen[art].append(int(nid))
    c = QTextCursor(d)
    c.movePosition(QTextCursor.End)
    for art, titel in (("f", "Fußnoten"), ("e", "Endnoten")):
        if stellen[art] and art in arten:
            _notenabschnitt(c, art, titel, stellen[art], noten)


def _fussnoten_stellen(d: QTextDocument) -> list[tuple[int, int, int]]:
    """[(Zeichenstelle, Fußnoten-Id, Länge)] in Textreihenfolge."""
    return [(f.position(), int(nid), f.length()) for _b, f, art, nid in _notenfragmente(d) if art == "f"]


def zeilenbereiche(d: QTextDocument) -> list[tuple[float, float, int, int]]:
    """[(oben, unten, Zeichenstelle des Zeilenanfangs, Blocknummer)] aller Zeilen in Dokumentreihenfolge."""
    lay = d.documentLayout()
    out = []
    b = d.firstBlock()
    while b.isValid():
        tl = b.layout()
        if tl is not None and b.isVisible():
            top = lay.blockBoundingRect(b).top()
            for i in range(tl.lineCount()):
                ln = tl.lineAt(i)
                out.append((top + ln.y(), top + ln.y() + ln.height(), b.position() + ln.textStart(), b.blockNumber()))
        b = b.next()
    return out


def _notenschrift(d: QTextDocument) -> QFont:
    basis = d.defaultFont()
    kl = QFont(basis)
    kl.setPointSizeF(max(6.0, (basis.pointSizeF() if basis.pointSizeF() > 0 else 11.0) * NOTEN_SCHRIFT))
    return kl


def _notendoc_fabrik(liste: dict, schrift: QFont, breite: float) -> Callable[[int, int], QTextDocument]:
    """Liefert ``notendoc(nr, id)``: das gesetzte Textdokument einer Fußnote (je Id einmal)."""
    fertig: dict[int, QTextDocument] = {}

    def notendoc(nr: int, nid: int) -> QTextDocument:
        if nid not in fertig:
            nd = QTextDocument()
            nd.setDefaultFont(schrift)
            nd.setDocumentMargin(0)
            nd.setPlainText(f"{nr}  {liste.get(nid, '')}")
            nd.setTextWidth(breite)
            nd.setPageSize(QSizeF(breite, -1))
            fertig[nid] = nd
        return fertig[nid]
    return notendoc


def _notenhoehe(eintraege: list, notendoc: Callable[[int, int], QTextDocument]) -> float:
    return NOTEN_TRENNER + sum(notendoc(nr, nid).size().height() + NOTEN_ABSTAND for nr, nid in eintraege)


def _belegung(stellen: list, zeilen: list, ch: float) -> dict[int, list]:
    """{Seite (1-basiert): [(laufende Nummer, Fußnoten-Id)]} nach der Zeile, in der die Marke steht."""
    starts = [z[2] for z in zeilen]
    belegung: dict[int, list] = {}
    for nr, (pos, nid, _l) in enumerate(stellen, start=1):
        i = max(0, bisect.bisect_right(starts, pos) - 1)
        seite = int((zeilen[i][0] + 0.5) // ch) + 1
        belegung.setdefault(seite, []).append((nr, nid))
    return belegung


def _erste_zeile_ohne_platz(zeilen: list, seite: int, ch: float, grenze: float) -> int | None:
    """Zeichenstelle der ersten Zeile der Seite, die unter die Grenze ragt (die erste Zeile der Seite bleibt immer)."""
    erste = None
    for (o, u, pos, _bn) in zeilen:
        if (o + 0.5) // ch == seite - 1:
            if erste is None:
                erste = o
            if u > grenze + 0.5 and o > erste + 0.5:
                return pos
    return None


def _zu_hohe_zeile(belegung: dict, zeilen: list, ch: float, notendoc: Callable[[int, int], QTextDocument]) -> int | None:
    """Stelle, an der ein Seitenwechsel nötig ist, damit die Fußnoten der Seite Platz haben; None, wenn alles passt."""
    for seite, eintraege in sorted(belegung.items()):
        h = _notenhoehe(eintraege, notendoc)
        if h >= ch * NOTEN_SEITENANTEIL:
            continue                                           # eine Seite voller Fußnoten: Überlauf in Kauf nehmen
        pos = _erste_zeile_ohne_platz(zeilen, seite, ch, seite * ch - h)
        if pos is not None:
            return pos
    return None


def _seitenwechsel_vor(d: QTextDocument, pos: int) -> None:
    """Seitenwechsel vor der Zeichenstelle: am Absatzanfang als Umbruchregel, sonst wird der Absatz geteilt."""
    b = d.findBlock(pos)
    if pos == b.position():
        bf = b.blockFormat(); bf.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore)
        QTextCursor(b).setBlockFormat(bf)
        return
    c = QTextCursor(d)
    c.setPosition(pos)
    neu = QTextBlockFormat(c.blockFormat())
    neu.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore); neu.setTopMargin(0); neu.setTextIndent(0)
    vorher = QTextBlockFormat(c.blockFormat()); vorher.setBottomMargin(0)
    QTextCursor(b).setBlockFormat(vorher)
    c.insertBlock(neu, c.charFormat())


def _platzierung(belegung: dict, notendoc: Callable[[int, int], QTextDocument], ch: float) -> dict[int, dict]:
    """{Seite: {"hoehe": px, "noten": [(y ab Textflächenanfang, Textdokument, Id)]}}."""
    ergebnis: dict[int, dict] = {}
    for seite, eintraege in belegung.items():
        docs = [(nr, nid, notendoc(nr, nid)) for nr, nid in eintraege]
        h = _notenhoehe(eintraege, notendoc)
        y = seite * ch - h + NOTEN_TRENNER - (seite - 1) * ch
        platz = []
        for nr, nid, nd in docs:
            platz.append((y, nd, nid))
            y += nd.size().height() + NOTEN_ABSTAND
        ergebnis[seite] = {"hoehe": h, "noten": platz}
    return ergebnis


def fussnoten_am_seitenende(d: QTextDocument, page: PageSettings, noten: dict) -> None:
    """Fußnoten unten auf der Seite, auf der ihre Marke steht (nur in der Kopie für Seitenzählung, Seitenansicht, PDF und Druck).

    Die Kopie wird so umbrochen, dass unter dem Text Platz für die Fußnoten der Seite bleibt: Reicht er nicht, wird vor der ersten
    Zeile, die nicht mehr passt, ein Seitenwechsel eingefügt (Absätze werden dabei geteilt). Das Ergebnis steht in
    `d._fussnoten` = {Seite (1-basiert): {"hoehe": px, "noten": [(y in px ab Textflächenanfang, QTextDocument)]}}."""
    ch = page.content_height_px
    notendoc = _notendoc_fabrik((noten or {}).get("f", {}) or {}, _notenschrift(d), page.content_width_px)
    belegung: dict[int, list] = {}
    for _runde in range(NOTEN_RUNDEN):
        d.documentLayout().documentSize()
        stellen = _fussnoten_stellen(d)
        zeilen = zeilenbereiche(d)
        if not stellen or not zeilen:
            belegung = {}
            break
        belegung = _belegung(stellen, zeilen, ch)
        zu_hoch = _zu_hohe_zeile(belegung, zeilen, ch, notendoc)
        if zu_hoch is None:
            break
        _seitenwechsel_vor(d, zu_hoch)
    d._fussnoten = _platzierung(belegung, notendoc, ch)


def _notenmarken(d: QTextDocument, ort, liste: list[int]) -> dict:
    """{(Art, Id): Lage der Marke auf ihrer Seite}; nur Seiten aus ``liste``."""
    lay = d.documentLayout()
    marken = {}
    for b, f, art, nid in _notenfragmente(d):
        if b.layout() is None or not b.layout().lineCount():
            continue
        rel = f.position() - b.position()
        ln = b.layout().lineForTextPosition(rel)
        if not ln.isValid():
            continue
        x1 = ln.cursorToX(rel)[0]
        x2 = ln.cursorToX(rel + f.length())[0]
        y = lay.blockBoundingRect(b).top() + ln.y()
        seite, yr = ort(y)
        if seite in liste:
            marken[(art, int(nid))] = {"seite": liste.index(seite), "x": min(x1, x2), "y": yr,
                                       "w": abs(x2 - x1) + 2, "h": ln.height()}
    return marken


def _notenziele(d: QTextDocument, ort, liste: list[int]) -> dict:
    """{(Art, Id): Lage der Note}: Fußnoten am Seitenfuß, Endnoten und gesammelte Noten am Textende."""
    from lunivo_writer.editor.seite.seitenzahl import absatz_oben
    lay = d.documentLayout()
    ziele = {}
    fussnoten = dict(getattr(d, "_fussnoten", None) or {})
    for k, info in (getattr(lay, "erg", None) and getattr(lay.erg, "fussnoten", None) or {}).items():     # Blattweg: je Blatt, y ab dem Textrand
        fussnoten[k + 1] = info
    for seite, info in fussnoten.items():
        for y, nd, nid in info["noten"]:
            if seite in liste:
                ziele[("f", nid)] = {"seite": liste.index(seite), "y": y, "h": nd.size().height()}
    b = d.firstBlock()
    while b.isValid():
        bf = b.blockFormat()
        if bf.hasProperty(B_NOTENZIEL):
            art, _, nid = str(bf.property(B_NOTENZIEL)).partition(":")
            seite, yr = ort(absatz_oben(lay, b))
            if seite in liste:
                ziele[(art, int(nid))] = {"seite": liste.index(seite), "y": yr, "h": lay.blockBoundingRect(b).height()}
        b = b.next()
    return ziele


def notenlinks_sammeln(d: QTextDocument, page: PageSettings, liste: list[int], ort=None) -> list[dict]:
    """Sprungverweise für die PDF: Marke → Note und Note → Marke (Fußnoten am Seitenfuß, Endnoten und gesammelte Noten am Textende).
    Jeder Eintrag: {seite, x, y, w, h} (Quelle, in px auf der Textfläche) und {ziel_seite, ziel_y}."""
    if int(page.spalten) > 1:
        return []
    from lunivo_writer.editor.seite.pdf_struktur import fluss_ort
    ort = ort or fluss_ort(page.content_height_px)
    ziele = _notenziele(d, ort, liste)
    out = []
    for key, m in _notenmarken(d, ort, liste).items():
        z = ziele.get(key)
        if z is None:
            continue
        out.append({"seite": m["seite"], "x": m["x"], "y": m["y"], "w": m["w"], "h": m["h"], "ziel_seite": z["seite"], "ziel_y": z["y"]})
        out.append({"seite": z["seite"], "x": 0, "y": z["y"], "w": page.content_width_px, "h": z["h"],
                    "ziel_seite": m["seite"], "ziel_y": m["y"]})
    return out
