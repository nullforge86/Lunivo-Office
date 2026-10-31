"""Beschriftungen, Textmarken, Querverweise, Stichwörter und Zitate — Funktionen am Editor."""
from __future__ import annotations

import re

from PySide6.QtGui import QBrush, QColor, QFont, QTextBlockFormat, QTextCharFormat, QTextCursor

from lunivo_writer.editor.literatur import zitat
from lunivo_writer.editor.zusatz import B_CAP, P_FELD, P_INDEX, P_ZITAT


# ---- Beschriftungen ---------------------------------------------------------------------------------------
# Zahlschreibweise der Beschriftung (editor/zahlformat.py) ↔ Schalter des Word-Felds SEQ
SEQ_FORMAT = {"arabisch": "ARABIC", "gross": "ALPHABETIC", "klein": "alphabetic", "roemisch": "ROMAN", "roemisch_klein": "roman"}


def seq_format(anweisung: str) -> str:
    """Zahlschreibweise aus einer Feldanweisung ``SEQ Abbildung \\* ROMAN`` (Vorgabe arabisch)."""
    m = re.search(r"\\\*\s*(\w+)", anweisung)
    if m:
        for k, v in SEQ_FORMAT.items():
            if v == m.group(1):
                return k
    return "arabisch"


def naechste_nummer(ed, label: str, zahl: str = "arabisch") -> str:
    """Nummer, die eine neue Beschriftung ``label`` an der Schreibmarke bekäme (für die Anzeige im Fenster)."""
    from lunivo_writer.editor.zahlformat import zahl_text
    pos = ed.textCursor().position()
    n = 1 + sum(1 for k in beschriftungen_liste(ed) if k["label"] == label and k["pos"] < pos)
    return zahl_text(n, zahl)


def beschriftung_einfuegen(ed, label: str, text: str, oben: bool = False, *, nach: str | None = None,
                           ohne_bezeichnung: bool = False, zahl: str = "arabisch") -> None:
    """Beschriftung „Abbildung 1: Text“ unter (``oben``: über) dem Objekt oder Absatz. ``nach`` ersetzt „: Text“ durch genau diesen
    Text hinter der Nummer, ``ohne_bezeichnung`` lässt „Abbildung “ weg, ``zahl`` ist die Schreibweise der Nummer."""
    c = ed.textCursor()
    c.beginEditBlock()
    tab = c.currentTable()
    if tab is not None:
        if oben and tab.firstPosition() > 0:
            c.setPosition(tab.firstPosition() - 1)
            c.movePosition(QTextCursor.EndOfBlock)
        else:
            c.setPosition(tab.lastPosition() + 1)
            c.movePosition(QTextCursor.EndOfBlock)
            if c.block().text():
                c.insertBlock()
    else:
        c.movePosition(QTextCursor.EndOfBlock)
    bf = QTextBlockFormat()
    bf.setProperty(B_CAP, label)
    bf.setTopMargin(4); bf.setBottomMargin(8)
    cf = QTextCharFormat()
    cf.setFontItalic(True); cf.setFontPointSize(9); cf.setForeground(QBrush(QColor("#44546a")))
    if c.block().text() or tab is None:
        c.insertBlock(bf, cf)
    else:
        c.setBlockFormat(bf); c.setBlockCharFormat(cf)
    if not ohne_bezeichnung:
        c.insertText(label + " ", cf)
    nf = QTextCharFormat(cf)
    nf.setProperty(P_FELD, f"SEQ {label.replace(' ', '_')} \\* {SEQ_FORMAT.get(zahl, 'ARABIC')}")
    c.insertText("0", nf)
    if nach is not None:
        if nach:
            c.insertText(nach, cf)
    elif text:
        c.insertText(": " + text, cf)
    c.endEditBlock()
    ed.setTextCursor(c)
    beschriftungen_nummerieren(ed)
    ed.document().setModified(True)


def beschriftungen_nummerieren(ed) -> None:
    from lunivo_writer.editor.zahlformat import zahl_text
    zaehler: dict[str, int] = {}
    doc = ed.document()
    arbeit = []
    b = doc.firstBlock()
    while b.isValid():
        if b.blockFormat().hasProperty(B_CAP):
            label = b.blockFormat().property(B_CAP)
            zaehler[label] = zaehler.get(label, 0) + 1
            it = b.begin()
            while not it.atEnd():
                f = it.fragment()
                if f.isValid() and f.charFormat().hasProperty(P_FELD) and f.charFormat().stringProperty(P_FELD).upper().startswith("SEQ"):
                    try:
                        soll = zahl_text(zaehler[label], seq_format(f.charFormat().stringProperty(P_FELD)))
                    except ValueError:
                        soll = str(zaehler[label])
                    if f.text() != soll:
                        arbeit.append((f.position(), f.position() + f.length(), soll, f.charFormat()))
                    break
                it += 1
        b = b.next()
    if arbeit:
        c = QTextCursor(doc)
        c.beginEditBlock()
        for von, bis, neu, fmt in reversed(arbeit):
            c.setPosition(von); c.setPosition(bis, QTextCursor.KeepAnchor)
            c.insertText(neu, fmt)
        c.endEditBlock()


def beschriftungen_liste(ed) -> list[dict]:
    out = []
    b = ed.document().firstBlock()
    while b.isValid():
        if b.blockFormat().hasProperty(B_CAP) and b.text().strip():
            out.append({"label": b.blockFormat().property(B_CAP), "text": b.text().strip(), "pos": b.position(), "block": b})
        b = b.next()
    return out


# ---- Textmarken ------------------------------------------------------------------------------------------------
def lesezeichen_liste(ed, versteckte: bool = True) -> list[dict]:
    """[{name, von, bis}] — zusammenhängende Textstücke mit demselben Namen. ``versteckte=False`` lässt die Marken weg, die mit
    „_“ beginnen (z. B. „_Toc…“ des Inhaltsverzeichnisses; Word blendet sie ebenso aus)."""
    out: dict[str, dict] = {}
    b = ed.document().firstBlock()
    while b.isValid():
        it = b.begin()
        while not it.atEnd():
            f = it.fragment()
            if f.isValid() and f.charFormat().isAnchor() and not f.charFormat().anchorHref():
                for n in f.charFormat().anchorNames():
                    d = out.setdefault(n, {"name": n, "von": f.position(), "bis": f.position() + f.length()})
                    d["bis"] = max(d["bis"], f.position() + f.length())
                    d["von"] = min(d["von"], f.position())
            it += 1
        b = b.next()
    return sorted((d for d in out.values() if versteckte or not d["name"].startswith("_")), key=lambda d: d["von"])


_NAME = re.compile(r"^[A-Za-zÄÖÜäöüß][A-Za-z0-9ÄÖÜäöüß_]{0,39}$")


def lesezeichen_name_gueltig(name: str) -> bool:
    return bool(_NAME.match(name))


def lesezeichen_setzen(ed, name: str) -> bool:
    c = ed.textCursor()
    if not c.hasSelection():
        c.select(QTextCursor.WordUnderCursor)
        if not c.hasSelection():
            return False
    if any(d["name"] == name for d in lesezeichen_liste(ed)):
        lesezeichen_loeschen(ed, name)
    von, bis = c.selectionStart(), c.selectionEnd()
    c.beginEditBlock()
    stuecke = []
    b = ed.document().findBlock(von)
    while b.isValid() and b.position() < bis:
        it = b.begin()
        while not it.atEnd():
            f = it.fragment()
            if f.isValid() and f.position() < bis and f.position() + f.length() > von:
                stuecke.append((max(f.position(), von), min(f.position() + f.length(), bis), f.charFormat()))
            it += 1
        b = b.next()
    for a, z, cf in stuecke:
        neu = QTextCharFormat(cf)
        neu.setAnchor(True)
        neu.setAnchorNames(list(cf.anchorNames()) + [name] if cf.isAnchor() else [name])
        cc = QTextCursor(ed.document()); cc.setPosition(a); cc.setPosition(z, QTextCursor.KeepAnchor)
        cc.setCharFormat(neu)
    c.endEditBlock()
    ed.document().setModified(True)
    return True


def lesezeichen_loeschen(ed, name: str) -> None:
    doc = ed.document()
    c = QTextCursor(doc)
    c.beginEditBlock()
    stuecke = []
    b = doc.firstBlock()
    while b.isValid():
        it = b.begin()
        while not it.atEnd():
            f = it.fragment()
            if f.isValid() and f.charFormat().isAnchor() and name in f.charFormat().anchorNames():
                stuecke.append((f.position(), f.position() + f.length(), f.charFormat()))
            it += 1
        b = b.next()
    for a, z, cf in reversed(stuecke):
        neu = QTextCharFormat(cf)
        rest = [n for n in cf.anchorNames() if n != name]
        if rest:
            neu.setAnchorNames(rest)
        else:
            neu.setAnchor(False); neu.setAnchorNames([])
        cc = QTextCursor(doc); cc.setPosition(a); cc.setPosition(z, QTextCursor.KeepAnchor)
        cc.setCharFormat(neu)
    c.endEditBlock()
    doc.setModified(True)


def lesezeichen_gehe(ed, name: str) -> bool:
    for d in lesezeichen_liste(ed):
        if d["name"] == name:
            ed.select_range(d["von"], d["bis"])
            ed.ensureCursorVisible()
            return True
    return False


def intern_springen(ed, href: str) -> bool:
    return href.startswith("#") and lesezeichen_gehe(ed, href[1:])


# ---- Querverweise -----------------------------------------------------------------------------------------------
# Verweistyp → was eingefügt werden kann („Verweisen auf“), in der Reihenfolge des Fensters
VERWEISTYPEN = ["Nummeriertes Element", "Überschrift", "Textmarke", "Fußnote", "Endnote", "Abbildung", "Tabelle", "Gleichung"]
VERWEISEN_AUF = {
    "Nummeriertes Element": [("seite", "Seitenzahl"), ("nummer", "Absatznummer"), ("text", "Absatztext"), ("obenunten", "Oben/unten")],
    "Überschrift": [("text", "Überschriftentext"), ("seite", "Seitenzahl"), ("nummer", "Überschriftennummer"), ("obenunten", "Oben/unten")],
    "Textmarke": [("text", "Textmarkeninhalt"), ("seite", "Seitenzahl"), ("obenunten", "Oben/unten")],
    "Fußnote": [("nummer", "Fußnotennummer"), ("seite", "Seitenzahl"), ("obenunten", "Oben/unten")],
    "Endnote": [("nummer", "Endnotennummer"), ("seite", "Seitenzahl"), ("obenunten", "Oben/unten")],
}
_BESCHRIFTUNG_AUF = [("text", "Vollständige Beschriftung"), ("nummer", "Nur Bezeichnung und Nummer"), ("nur_text", "Nur Beschriftungstext"),
                     ("seite", "Seitenzahl"), ("obenunten", "Oben/unten")]


def verweisen_auf(art: str) -> list[tuple[str, str]]:
    return VERWEISEN_AUF.get(art, _BESCHRIFTUNG_AUF)


def querverweis_ziele(ed) -> list[dict]:
    """Mögliche Ziele: nummerierte Absätze, Überschriften, Textmarken, Fuß- und Endnoten, Beschriftungen.
    Jedes Ziel: art, text (Anzeige), pos, von/bis (Bereich für die Textmarke), nummer (wenn es eine hat)."""
    from lunivo_writer.editor.zusatz import roemisch
    z = []
    b = ed.document().firstBlock()
    while b.isValid():
        lv = b.blockFormat().headingLevel()
        lst = b.textList()
        nummer = lst.itemText(b).strip() if lst is not None else ""
        if lv and b.text().strip():
            z.append({"art": "Überschrift", "text": b.text().strip(), "pos": b.position(), "block": b.blockNumber(),
                      "von": b.position(), "bis": b.position() + len(b.text()), "nummer": nummer})
        elif lst is not None and nummer and not nummer.startswith(("•", "◦", "▪", "–", "-")) and b.text().strip():
            z.append({"art": "Nummeriertes Element", "text": f"{nummer} {b.text().strip()}", "pos": b.position(), "block": b.blockNumber(),
                      "von": b.position(), "bis": b.position() + len(b.text()), "nummer": nummer, "inhalt": b.text().strip()})
        b = b.next()
    for k in beschriftungen_liste(ed):
        blk = k["block"]
        z.append({"art": k["label"], "text": k["text"], "pos": k["pos"], "block": blk.blockNumber(), "von": blk.position(),
                  "bis": blk.position() + len(blk.text()), "nummer": _bezeichnung_nummer(blk) or k["text"],
                  "inhalt": _beschriftungstext(blk)})
    for d in lesezeichen_liste(ed, versteckte=False):
        doc_text = ed.document().toPlainText()
        z.append({"art": "Textmarke", "text": d["name"], "pos": d["von"], "name": d["name"],
                  "inhalt": doc_text[d["von"]:d["bis"]].replace("\u2029", " ")})
    zaehler = {"f": 0, "e": 0}
    for n in ed.noten_stellen() if hasattr(ed, "noten_stellen") else []:
        zaehler[n["art"]] += 1
        nr = str(zaehler[n["art"]]) if n["art"] == "f" else roemisch(zaehler[n["art"]])
        text = ((getattr(ed, "noten", {}) or {}).get(n["art"], {}) or {}).get(n["id"], "")
        z.append({"art": "Fußnote" if n["art"] == "f" else "Endnote", "text": f"{nr} {text}".strip(), "pos": n["von"],
                  "von": n["von"], "bis": n["bis"], "nummer": nr})
    return z


def _seq_fragment(blk):
    it = blk.begin()
    while not it.atEnd():
        f = it.fragment()
        if f.isValid() and f.charFormat().hasProperty(P_FELD) and f.charFormat().stringProperty(P_FELD).upper().startswith("SEQ"):
            return f
        it += 1
    return None


def _bezeichnung_nummer(blk) -> str:
    """„Abbildung 2“ — der Text der Beschriftung bis einschließlich der Nummer."""
    f = _seq_fragment(blk)
    return blk.text()[:f.position() + f.length() - blk.position()].strip() if f else ""


def _beschriftungstext(blk) -> str:
    """Der Text hinter der Nummer, ohne Doppelpunkt."""
    f = _seq_fragment(blk)
    rest = blk.text()[f.position() + f.length() - blk.position():] if f else blk.text()
    return re.sub(r"^\s*[:.–-]?\s*", "", rest).strip()


def marke_sichern(ed, ziel: dict) -> str:
    """Name der Textmarke am Ziel. Fehlt eine, bekommt der Bereich des Ziels eine verborgene Textmarke „_Ref…“ (wie in Word)."""
    if "name" in ziel:
        return ziel["name"]
    doc = ed.document()
    if "von" in ziel:
        von, bis = ziel["von"], ziel["bis"]
    else:
        blk = doc.findBlockByNumber(ziel["block"]) if "block" in ziel else doc.findBlock(ziel["pos"])
        von, bis = blk.position(), blk.position() + len(blk.text())
    if bis <= von:
        bis = von + 1
    vorhanden = set()
    for d in lesezeichen_liste(ed):
        vorhanden.add(d["name"])
        if d["von"] == von and d["bis"] == bis and d["name"].startswith(("_Ref", "Ziel_")):
            return d["name"]
    n = 1
    while f"_Ref{n:06d}" in vorhanden:
        n += 1
    name = f"_Ref{n:06d}"
    keep = QTextCursor(ed.textCursor())
    c = QTextCursor(doc); c.setPosition(von); c.setPosition(bis, QTextCursor.KeepAnchor)
    ed.setTextCursor(c)
    lesezeichen_setzen(ed, name)
    ed.setTextCursor(keep)
    return name


def querverweis_text(ed, ziel: dict, wie: str, oben_unten: bool = False) -> str:
    """Der Text, den der Querverweis zeigt. wie: "text", "nummer", "nur_text", "seite" oder "obenunten"."""
    richtung = "oben" if ziel["pos"] < ed.textCursor().position() else "unten"
    if wie == "obenunten":
        return richtung
    if wie == "seite":
        from lunivo_writer.editor.verzeichnis import _seiten
        text = str(_seiten(ed, [ziel["pos"]])[0])
    elif wie == "nummer":
        text = ziel.get("nummer") or ziel["text"]
    elif wie == "nur_text":
        text = ziel.get("inhalt", ziel["text"])
    else:
        text = ziel.get("inhalt", ziel["text"]) if ziel["art"] in ("Textmarke", "Nummeriertes Element") else ziel["text"]
    if oben_unten and wie in ("seite", "nummer"):
        text += " " + richtung
    return text


def querverweis_einfuegen(ed, ziel: dict, wie: str, *, link: bool = True, oben_unten: bool = False) -> None:
    """Querverweis an der Schreibmarke (siehe ``querverweis_text``); ``link`` macht ihn zum internen Hyperlink (Strg+Klick)."""
    text = querverweis_text(ed, ziel, wie, oben_unten)
    name = marke_sichern(ed, ziel) if link else ""
    c = ed.textCursor()
    schlicht = QTextCharFormat(c.charFormat())          # Schrift an der Schreibmarke behalten, nur ohne Verknüpfung
    schlicht.setAnchor(False); schlicht.setAnchorHref("")
    cf = QTextCharFormat(schlicht)
    if name:
        cf.setAnchor(True); cf.setAnchorHref("#" + name)
    c.insertText(text, cf)
    c.insertText(" ", schlicht)
    ed.setTextCursor(c)
    ed.document().setModified(True)


# ---- Stichwörter -------------------------------------------------------------------------------------------------------
def index_eintragen(ed, e, alle: bool = False) -> int:
    """Indexeintrag ``e`` (``editor.indexeintrag.Eintrag``) an die Markierung setzen (ohne Markierung: das Wort an der
    Schreibmarke); ``alle`` markiert jede Stelle im Dokument mit demselben Text. Gibt die Zahl der markierten Stellen zurück."""
    from lunivo_writer.editor.zusatz import P_INDEX_OPT
    c = ed.textCursor()
    if not c.hasSelection():
        c.select(QTextCursor.WordUnderCursor)
    if not c.hasSelection() or not e.haupt:
        return 0
    f = QTextCharFormat()
    f.setProperty(P_INDEX, e.text())
    f.setProperty(P_INDEX_OPT, e.schalter())
    stellen = [(c.selectionStart(), c.selectionEnd())]
    if alle:
        from PySide6.QtGui import QTextDocument
        such, stellen = c.selectedText(), []
        t = ed.document().find(such, 0, QTextDocument.FindCaseSensitively)
        while not t.isNull():
            stellen.append((t.selectionStart(), t.selectionEnd()))
            t = ed.document().find(such, t.selectionEnd(), QTextDocument.FindCaseSensitively)
    k = QTextCursor(ed.document())
    k.beginEditBlock()
    for von, bis in stellen:
        k.setPosition(von); k.setPosition(bis, QTextCursor.KeepAnchor)
        k.mergeCharFormat(f)
    k.endEditBlock()
    ed.document().setModified(True)
    return len(stellen)


def index_markieren(ed, term: str) -> bool:
    c = ed.textCursor()
    if not c.hasSelection():
        c.select(QTextCursor.WordUnderCursor)
    if not c.hasSelection():
        return False
    f = QTextCharFormat()
    f.setProperty(P_INDEX, term or c.selectedText())
    c.mergeCharFormat(f)
    ed.document().setModified(True)
    return True


# ---- Zitate ----------------------------------------------------------------------------------------------------------------
def zitat_einfuegen(ed, q: dict) -> None:
    nr = 1 + [x["tag"] for x in ed.quellen].index(q["tag"]) if q in ed.quellen else 1
    f = QTextCharFormat()
    f.setProperty(P_FELD, f"CITATION {q['tag']} \\l 1031")
    f.setProperty(P_ZITAT, q["tag"])
    c = ed.textCursor()
    c.insertText(zitat(q, ed.zitierweise, nr), f)
    c.insertText(" ", QTextCharFormat())
    ed.setTextCursor(c)
    ed.document().setModified(True)


def quelle_tag(quellen: list[dict], q: dict) -> str:
    """Eindeutiger Kurzname wie in Word (Nachname + Jahr)."""
    basis = re.sub(r"\W+", "", (q.get("autor", "").split(",")[0].split(";")[0] or q.get("titel", "Quelle")))[:20] or "Quelle"
    basis += re.sub(r"\D", "", q.get("jahr", ""))[:4]
    tag, i = basis, 2
    vorhanden = {x["tag"] for x in quellen}
    while tag in vorhanden:
        tag = f"{basis}{i}"; i += 1
    return tag
