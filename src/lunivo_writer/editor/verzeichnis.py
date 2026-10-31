"""Verzeichnisse: Inhalt, Abbildungen, Tabellen, Stichwörter, Literatur.

Die Zeilen sind gewöhnliche Absätze mit rechtem Tabstopp und einer Markierung (B_TOC/B_ART), an der „Verzeichnisse
aktualisieren“ sie wiederfindet. In DOCX tragen sie die Word-Formatvorlagen „TOC Heading“, „TOC 1–3“, „Table of Figures“,
„Index 1“ und „Bibliography“ — beim Öffnen werden sie daran wiedererkannt (kein Word-Feld, aber aktualisierbar).

Das Inhaltsverzeichnis merkt sich am Kopf seine Einstellungen (``B_TOC_OPT``, Fenster „Inhaltsverzeichnis“): Füllzeichen,
Ebenen 1–9, Seitenzahlen anzeigen, rechtsbündig, Verknüpfungen. Mit Verknüpfungen bekommt jede Überschrift eine verborgene
Textmarke „_Toc…“, die Zeile verweist darauf (Strg+Klick springt hin, im DOCX ein interner Hyperlink).
"""
from __future__ import annotations

from PySide6.QtGui import QFont, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextOption

from lunivo_writer.models.page import mm_to_px
from lunivo_writer.editor.pagination import paginated_copy
from lunivo_writer.editor.zusatz import B_ART, B_CAP, B_TOC, B_TOC_OPT, P_INDEX, P_INDEX_OPT

TOC_VORGABE = {"fuell": "punkt", "ebenen": 3, "seitenzahlen": True, "rechts": True, "links": True}
TOC_FUELL = ("", "punkt", "strich", "linie")           # Auswahl im Fenster (Schlüssel aus editor/tabfuell.py)

ARTEN = {
    "toc": "Inhaltsverzeichnis",
    "abb": "Abbildungsverzeichnis",
    "tab": "Tabellenverzeichnis",
    "index": "Stichwortverzeichnis",
    "lit": "Literaturverzeichnis",
}


def toc_opt_text(opt: dict) -> str:
    o = {**TOC_VORGABE, **opt}
    return f"{o['fuell']}|{int(o['ebenen'])}|{int(bool(o['seitenzahlen']))}|{int(bool(o['rechts']))}|{int(bool(o['links']))}"


def toc_opt_lesen(text: str | None) -> dict:
    o = dict(TOC_VORGABE)
    teile = (text or "").split("|")
    if len(teile) == 5:
        try:
            o.update(fuell=teile[0] if teile[0] in TOC_FUELL else "", ebenen=max(1, min(9, int(teile[1]))),
                     seitenzahlen=teile[2] == "1", rechts=teile[3] == "1", links=teile[4] == "1")
        except ValueError:
            pass
    return o


def toc_optionen(doc) -> dict | None:
    """Einstellungen des ersten Inhaltsverzeichnisses im Dokument (None, wenn es keines gibt)."""
    b = doc.firstBlock()
    while b.isValid():
        bf = b.blockFormat()
        if bf.property(B_TOC) == "kopf" and (bf.property(B_ART) or "toc") == "toc":
            return toc_opt_lesen(bf.stringProperty(B_TOC_OPT) if bf.hasProperty(B_TOC_OPT) else None)
        b = b.next()
    return None


def _ueberschriften(doc, ebenen: int = 3):
    b = doc.firstBlock()
    while b.isValid():
        lvl = b.blockFormat().headingLevel()
        if 1 <= lvl <= ebenen and b.text().strip() and b.blockFormat().property(B_TOC) is None:
            yield lvl, b.text().strip(), b.position()
        b = b.next()


def _toc_marke(doc, pos: int, vergeben: set) -> str:
    """Name der verborgenen Textmarke an der Überschrift bei ``pos``; fehlt sie, wird sie gesetzt."""
    blk = doc.findBlock(pos)
    it = blk.begin()
    while not it.atEnd():
        f = it.fragment()
        if f.isValid() and f.charFormat().isAnchor():
            for n in f.charFormat().anchorNames():
                if n.startswith("_Toc"):
                    vergeben.add(n)
                    return n
        it += 1
    n = len(vergeben) + 1
    while f"_Toc{n:06d}" in vergeben:
        n += 1
    name = f"_Toc{n:06d}"
    vergeben.add(name)
    stuecke = []
    it = blk.begin()
    while not it.atEnd():
        f = it.fragment()
        if f.isValid():
            stuecke.append((f.position(), f.position() + f.length(), f.charFormat()))
        it += 1
    for a, z, cf in stuecke:
        neu = QTextCharFormat(cf)
        neu.setAnchor(True)
        neu.setAnchorNames((list(cf.anchorNames()) if cf.isAnchor() else []) + [name])
        c = QTextCursor(doc); c.setPosition(a); c.setPosition(z, QTextCursor.KeepAnchor)
        c.setCharFormat(neu)
    return name


def _alle_toc_marken(doc) -> set:
    out = set()
    b = doc.firstBlock()
    while b.isValid():
        it = b.begin()
        while not it.atEnd():
            f = it.fragment()
            if f.isValid() and f.charFormat().isAnchor():
                out.update(n for n in f.charFormat().anchorNames() if n.startswith("_Toc"))
            it += 1
        b = b.next()
    return out


def _beschriftungen(doc, label: str):
    b = doc.firstBlock()
    while b.isValid():
        if b.blockFormat().hasProperty(B_CAP) and b.blockFormat().property(B_CAP) == label and b.text().strip():
            yield 1, b.text().strip(), b.position()
        b = b.next()


def _stichwoerter(doc):
    """[(Eintrag, Position)] aus den markierten Textstellen (eine Stelle je zusammenhängender Markierung)."""
    from lunivo_writer.editor.indexeintrag import aus_text
    out = []
    vorher = None
    b = doc.firstBlock()
    while b.isValid():
        it = b.begin()
        while not it.atEnd():
            f = it.fragment()
            if f.isValid() and f.charFormat().hasProperty(P_INDEX):
                cf = f.charFormat()
                schl = (cf.stringProperty(P_INDEX), cf.stringProperty(P_INDEX_OPT) if cf.hasProperty(P_INDEX_OPT) else "")
                if vorher is None or vorher[0] != schl or vorher[1] != f.position():
                    out.append((aus_text(*schl), f.position()))
                vorher = (schl, f.position() + f.length())
            it += 1
        b = b.next()
    return out


def _index_zeilen(editor) -> list:
    """Zeilen des Stichwortverzeichnisses: Haupteinträge, darunter eingerückt die Untereinträge; „Siehe …“ statt Seitenzahl,
    Seitenbereiche aus Textmarken, fette/kursive Seitenzahlen als Stücke (Text, fett, kursiv)."""
    from lunivo_writer.editor.verweise import lesezeichen_liste
    eintraege = _stichwoerter(editor.document())
    marken = {d["name"]: d for d in lesezeichen_liste(editor)}
    pos = []
    for e, p in eintraege:
        pos.append(p)
        if e.marke in marken:
            pos += [marken[e.marke]["von"], max(marken[e.marke]["von"], marken[e.marke]["bis"] - 1)]
    seiten = iter(_seiten(editor, pos)) if pos else iter(())
    baum: dict[tuple, dict] = {}
    for e, _p in eintraege:
        s = next(seiten)
        if e.marke in marken:
            a, z = next(seiten), next(seiten)
            s = (a, z) if z > a else a
        h = baum.setdefault((e.sortierung()[0], e.haupt), {"text": e.haupt, "seiten": {}, "siehe": [], "unter": {}})
        ziel = h if not e.unter else h["unter"].setdefault((e.sortierung()[1], e.unter), {"text": e.unter, "seiten": {}, "siehe": []})
        if e.siehe:
            if e.siehe not in ziel["siehe"]:
                ziel["siehe"].append(e.siehe)
        else:
            fk = ziel["seiten"].setdefault(s, [False, False])
            fk[0] |= e.fett; fk[1] |= e.kursiv

    def angabe(knoten) -> list:
        stuecke = []
        for s in sorted(knoten["seiten"], key=lambda x: x if isinstance(x, tuple) else (x, x)):
            if stuecke:
                stuecke.append((", ", False, False))
            text = f"{s[0]}–{s[1]}" if isinstance(s, tuple) else str(s)
            stuecke.append((text, *knoten["seiten"][s]))
        for x in knoten["siehe"]:
            stuecke.append(((". " if stuecke else "") + "Siehe " + x, False, True))
        return stuecke

    out = []
    for k in sorted(baum):
        h = baum[k]
        out.append((1, h["text"], angabe(h)))
        for u in sorted(h["unter"]):
            out.append((2, h["unter"][u]["text"], angabe(h["unter"][u])))
    return out


def _seiten(editor, positionen):
    kopie = paginated_copy(editor.document(), editor.page, editor.noten)
    ch = editor.page.content_height_px
    out = []
    for pos in positionen:
        blk = kopie.findBlock(pos)
        r = kopie.documentLayout().blockBoundingRect(blk)
        out.append(int((r.top() + 0.5) // ch) // max(1, int(editor.page.spalten)) + 1)
    return out


def zeilen_fuer(editor, art: str, opt: dict | None = None) -> list[tuple]:
    """→ [(Ebene, Text, Seitenangabe)]; beim Inhaltsverzeichnis mit Verknüpfungen (``opt["links"]``) als viertes die Textmarke.
    Die Seitenangabe ist Text oder eine Liste von Stücken (Text, fett, kursiv)."""
    doc = editor.document()
    if art == "toc":
        o = {**TOC_VORGABE, **(opt or {})}
        ue = list(_ueberschriften(doc, int(o["ebenen"])))
        s = _seiten(editor, [p for _l, _t, p in ue]) if ue else []
        if o["links"]:
            vergeben = _alle_toc_marken(doc)
            return [(l, t, str(n), _toc_marke(doc, p, vergeben)) for (l, t, p), n in zip(ue, s)]
        return [(l, t, str(n)) for (l, t, _p), n in zip(ue, s)]
    if art in ("abb", "tab"):
        ue = list(_beschriftungen(doc, "Abbildung" if art == "abb" else "Tabelle"))
        s = _seiten(editor, [p for _l, _t, p in ue]) if ue else []
        return [(l, t, str(n)) for (l, t, _p), n in zip(ue, s)]
    if art == "index":
        return _index_zeilen(editor)
    if art == "lit":
        from lunivo_writer.editor.literatur import literaturverzeichnis
        return [(1, z, "") for z in literaturverzeichnis(editor.quellen, getattr(editor, "zitierweise", "APA"))]
    return []


def _schreibe(cur: QTextCursor, editor, art: str, zeilen, neuer_block: bool, opt: dict | None = None) -> None:
    from lunivo_writer.editor import tabfuell
    breite = editor.page.content_width_px
    o = {**TOC_VORGABE, **(opt or {})} if art == "toc" else {**TOC_VORGABE, "fuell": "", "links": False}
    kopf = QTextBlockFormat()
    kopf.setProperty(B_TOC, "kopf")
    kopf.setProperty(B_ART, art)
    if art == "toc":
        kopf.setProperty(B_TOC_OPT, toc_opt_text(o))
    kopf.setBottomMargin(6)
    cf = QTextCharFormat()
    cf.setFontWeight(QFont.Bold)
    cf.setFontPointSize(14)
    if neuer_block:
        cur.insertBlock(kopf, cf)
    else:
        cur.setBlockFormat(kopf)
    cur.insertText(ARTEN[art], cf)
    for lvl, text, seite, *marke in zeilen:
        bf = QTextBlockFormat()
        bf.setProperty(B_TOC, f"zeile{lvl}")
        bf.setProperty(B_ART, art)
        if art in ("toc", "index"):
            bf.setLeftMargin(mm_to_px(6) * (lvl - 1))
        if not o["seitenzahlen"]:
            seite = ""
        rechts = bool(seite) and o["rechts"]
        if rechts:
            bf.setTabPositions([QTextOption.Tab(breite, QTextOption.RightTab)])
            if o["fuell"]:
                tabfuell.setzen(bf, {round(float(breite), 2): o["fuell"]})
        zf = QTextCharFormat()
        if marke and marke[0]:
            zf.setAnchor(True); zf.setAnchorHref("#" + marke[0])
        cur.insertBlock(bf, QTextCharFormat())
        cur.insertText(text, zf)
        if seite:
            cur.insertText("\t" if rechts else " ", zf)
            for teil, fett, kursiv in ([(seite, False, False)] if isinstance(seite, str) else seite):
                sf = QTextCharFormat(zf)
                if fett:
                    sf.setFontWeight(QFont.Bold)
                if kursiv:
                    sf.setFontItalic(True)
                cur.insertText(teil, sf)


def verzeichnis_einfuegen(editor, art: str = "toc", opt: dict | None = None) -> int:
    """Verzeichnis an der Schreibmarke einfügen. Gibt es schon ein Inhaltsverzeichnis, wird es mit ``opt`` neu geschrieben."""
    cur = editor.textCursor()
    cur.beginEditBlock()
    zeilen = zeilen_fuer(editor, art, opt)
    if not zeilen:
        cur.endEditBlock()
        return 0
    if art == "toc" and opt is not None and toc_optionen(editor.document()) is not None:
        cur.endEditBlock()
        _neu_schreiben(editor, "toc", opt)
        return len(zeilen)
    if cur.block().text():
        cur.movePosition(QTextCursor.EndOfBlock)
    _schreibe(cur, editor, art, zeilen, True, opt)
    cur.endEditBlock()
    verzeichnis_aktualisieren(editor)      # Seitenzahlen nach dem Einfügen (das Verzeichnis schiebt den Text)
    return len(zeilen)


def _bereiche(doc) -> list[tuple[str, int, int]]:
    """[(Art, erste Blockposition, letzte Blockposition)] zusammenhängender Verzeichnisblöcke."""
    out: list[list] = []
    b = doc.firstBlock()
    while b.isValid():
        if b.blockFormat().hasProperty(B_TOC):
            art = b.blockFormat().property(B_ART) or "toc"
            neu = b.blockFormat().property(B_TOC) == "kopf"
            if out and out[-1][0] == art and not neu and out[-1][3] == b.blockNumber() - 1:
                out[-1][2] = b.position(); out[-1][3] = b.blockNumber()
            else:
                out.append([art, b.position(), b.position(), b.blockNumber()])
        b = b.next()
    return [(a, p, q) for a, p, q, _n in out]


def verzeichnis_aktualisieren(editor, nur: str | None = None) -> int:
    """Alle Verzeichnisse (oder nur die der Art ``nur``) neu schreiben; gibt die Zahl der Zeilen zurück."""
    return _neu_schreiben(editor, nur)


def vorhanden(doc, art: str) -> bool:
    return any(a == art for a, _v, _b in _bereiche(doc))


def _neu_schreiben(editor, nur: str | None = None, opt_neu: dict | None = None) -> int:
    doc = editor.document()
    n = 0
    for art, von, bis in reversed(_bereiche(doc)):
        if nur and art != nur:
            continue
        kf = doc.findBlock(von).blockFormat()
        opt = opt_neu if opt_neu is not None else (toc_opt_lesen(kf.stringProperty(B_TOC_OPT) if kf.hasProperty(B_TOC_OPT) else None)
                                                   if art == "toc" else None)
        zeilen = zeilen_fuer(editor, art, opt)
        cur = QTextCursor(doc)
        cur.beginEditBlock()
        cur.setPosition(von)
        letzter = doc.findBlock(bis)
        cur.setPosition(letzter.position() + letzter.length() - 1, QTextCursor.KeepAnchor)
        cur.removeSelectedText()
        cur.setBlockFormat(QTextBlockFormat())
        cur.setBlockCharFormat(QTextCharFormat())
        _schreibe(cur, editor, art, zeilen, False, opt)
        cur.endEditBlock()
        n += len(zeilen)
    return n
