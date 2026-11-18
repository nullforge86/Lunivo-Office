"""KI-Antworten als Markdown: die eine Stelle, die Chat-Anzeige, Vorschau und Übernahme ins Dokument gemeinsam nutzen.

Der Text wird von Qt selbst gelesen (``QTextDocument.setMarkdown``, GitHub-Dialekt); eine eigene Syntax gibt es nicht. Davor sorgt
``normalisieren`` für die Regeln, die für alle gelten: einzelne Zeilenumbrüche bleiben Zeilenumbrüche, rohe Auszeichnungen im Text werden nicht gedeutet.

* ``dokument(text)`` — der gelesene Text als ``QTextDocument`` (Chat und Vorschau zeigen genau das).
* ``hat_struktur(text)`` — gibt es Überschriften, Listen, Tabellen oder Hervorhebungen? Wenn nicht, bleibt der Text einfacher Text.
* ``einfuegen(editor, cursor, text)`` — überträgt die Struktur mit den Werkzeugen des Editors: Formatvorlagen „Überschrift n“, echte Listen
  (``editor.text.listen``) mit Ebenen, ``insert_table``, Fett/Kursiv als Zeichenformat. Das Dokumentdesign (Schrift, Absatzformat der Stelle) bleibt.
Kein HTML, nur ``QTextDocument``, ``QTextCursor``, ``QTextCharFormat``, ``QTextBlockFormat``."""
from __future__ import annotations

import re

from PySide6.QtGui import QFont, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument
from PySide6.QtGui import QTextTable

from lunivo_writer.editor.text.fragmente import absatz_fragmente
from lunivo_writer.editor.text import listen, stile

DIALEKT = QTextDocument.MarkdownDialectGitHub
AUFZAEHLUNG_EBENEN = ("disc", "circle", "square")            # Aufzählungszeichen je Ebene
_BLOCKANFANG = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s|#{1,6}\s|>|\||```|~~~|-{3,}\s*$|\*{3,}\s*$|={3,}\s*$)")
_ROHE_MARKE = re.compile(r"<(?=[A-Za-z/!?])")


def normalisieren(text: str) -> str:
    """Einheitliche Vorbereitung: einzelne Zeilenumbrüche werden harte Umbrüche (außer vor Listen, Tabellen, Überschriften, Codeblöcken);
    ``<`` vor Buchstaben wird maskiert, damit nichts als Auszeichnung gedeutet wird."""
    zeilen = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    aus: list[str] = []
    im_code = False
    for i, z in enumerate(zeilen):
        if z.lstrip().startswith(("```", "~~~")):
            im_code = not im_code
            aus.append(z)
            continue
        if im_code:
            aus.append(z)
            continue
        z = _ROHE_MARKE.sub("\\<", z)
        weiter = zeilen[i + 1] if i + 1 < len(zeilen) else ""
        if z.strip() and weiter.strip() and not z.endswith("  ") and not _BLOCKANFANG.match(z) and not _BLOCKANFANG.match(weiter):
            z += "  "
        aus.append(z)
    return "\n".join(aus)


def dokument(text: str) -> QTextDocument:
    """Der Text als gelesenes Dokument (mit Überschriftsebenen, Listen, Tabellen und Zeichenformaten)."""
    d = QTextDocument()
    d.setMarkdown(normalisieren(text), DIALEKT)
    return d


def _zeichen_besonders(f: QTextCharFormat) -> bool:
    return f.fontWeight() > QFont.Normal or f.fontItalic() or f.fontStrikeOut() or f.isAnchor() or f.fontFixedPitch()


def hat_struktur(text: str) -> bool:
    """Wahr, wenn der Text Überschriften, Listen, Tabellen oder Hervorhebungen enthält. Sonst bleibt er einfacher Text (auch ohne Markdown-Deutung)."""
    if not text or not text.strip():
        return False
    d = dokument(text)
    b = d.begin()
    while b.isValid():
        if b.blockFormat().headingLevel() or b.textList() is not None or b.blockFormat().hasProperty(QTextBlockFormat.ObjectIndex):
            return True
        if any(_zeichen_besonders(f.charFormat()) for f in absatz_fragmente(b)):
            return True
        b = b.next()
    return _tabellen(d) != []


def _tabellen(d: QTextDocument) -> list:
    return [f for f in d.rootFrame().childFrames() if isinstance(f, QTextTable)]


def klartext(text: str) -> str:
    """Der sichtbare Text ohne Markdown-Zeichen (z. B. für Zähler und Vergleiche)."""
    return dokument(text).toPlainText()


# ---- Übernahme ins Dokument --------------------------------------------------------------

class _Zustand:
    def __init__(self) -> None:
        self.frisch = True                    # der Absatz an der Schreibmarke darf noch benutzt werden
        self.listen: dict[int, tuple] = {}    # Ebene → (Liste im Ziel, Beschreibung)
        self.tabelle = False


def _basis_zeichen(f: QTextCharFormat) -> QTextCharFormat:
    """Zeichenformat der Stelle ohne Hervorhebungen: Schrift, Größe, Farbe bleiben, Fett/Kursiv/Link kommen aus dem Text."""
    g = QTextCharFormat(f)
    g.setFontWeight(QFont.Normal); g.setFontItalic(False); g.setFontStrikeOut(False)
    g.setAnchor(False); g.setAnchorHref(""); g.setAnchorNames([])
    g.setFontFixedPitch(False)
    return g


def _inline(c: QTextCursor, quelle, basis: QTextCharFormat, ueberschrift: bool) -> None:
    """Text eines gelesenen Absatzes mit Fett, Kursiv, Durchgestrichen, Code und Links einfügen (die Überschrift bringt ihre Vorlage selbst mit)."""
    for fr in absatz_fragmente(quelle):
        q = fr.charFormat()
        f = QTextCharFormat(basis)
        if q.fontWeight() > QFont.Normal and not ueberschrift:
            f.setFontWeight(QFont.Bold)
        if q.fontItalic():
            f.setFontItalic(True)
        if q.fontStrikeOut():
            f.setFontStrikeOut(True)
        if q.fontFixedPitch() and not ueberschrift:
            f.setFontFixedPitch(True)
            if q.fontFamilies():
                f.setFontFamilies(q.fontFamilies())
        if q.isAnchor():
            f.setAnchor(True); f.setAnchorHref(q.anchorHref())
        c.insertText(fr.text(), f)


def _aus_liste(c: QTextCursor) -> None:
    lst = c.currentList()
    if lst is not None:
        lst.remove(c.block())


def _fliesstext_format(basis: QTextBlockFormat) -> QTextBlockFormat:
    bf = QTextBlockFormat(basis)
    bf.setObjectIndex(-1)                 # nicht in der Liste der Ausgangsstelle bleiben
    bf.setHeadingLevel(0)
    return bf


def _block_bereit(c: QTextCursor, st: _Zustand, bf: QTextBlockFormat, cf: QTextCharFormat, mitte_ok: bool = False) -> None:
    """Der nächste Absatz: der erste darf den Absatz der Schreibmarke weiterbenutzen (leer, oder bei Fließtext auch mitten im Satz)."""
    leer = c.block().length() <= 1
    if st.frisch and (leer or mitte_ok):
        if leer:
            c.setBlockFormat(bf); c.setBlockCharFormat(cf)
    else:
        c.insertBlock(bf, cf)
    st.frisch = False


def _listenart(quelle_liste) -> tuple[str, int, int]:
    """(Stil im Ziel, Ebene, Start) aus der gelesenen Liste."""
    fmt = quelle_liste.format()
    ebene = max(1, fmt.indent())
    if listen.STILE.get(next((k for k, v in listen.STILE.items() if v[2] == fmt.style()), "disc"), ("", True))[1]:
        return AUFZAEHLUNG_EBENEN[min(ebene, len(AUFZAEHLUNG_EBENEN)) - 1], ebene, 1
    return "dezimal", ebene, fmt.start() or 1


def _liste_zuordnen(c: QTextCursor, st: _Zustand, quelle_liste) -> None:
    stil, ebene, start = _listenart(quelle_liste)
    spec = listen.liste(stil, "", ".", start)
    for tiefer in [e for e in st.listen if e > ebene]:
        del st.listen[tiefer]
    vorhanden = st.listen.get(ebene)
    if vorhanden is not None and vorhanden[1] == spec:
        vorhanden[0].add(c.block())
        return
    st.listen[ebene] = (c.createList(listen.zu_format(spec, ebene)), spec)


def _tabelle(editor, c: QTextCursor, st: _Zustand, quelle: QTextTable, bf: QTextBlockFormat, cf: QTextCharFormat) -> QTextCursor:
    """Native Tabelle über ``editor.insert_table``; die Zellen bekommen den Text samt Hervorhebungen. → Schreibmarke hinter der Tabelle."""
    _block_bereit(c, st, _fliesstext_format(bf), cf)
    _aus_liste(c)
    editor.setTextCursor(c)
    editor.insert_table(quelle.rows(), quelle.columns())
    ziel = editor.textCursor().currentTable()
    for r in range(quelle.rows()):
        for k in range(quelle.columns()):
            zc = ziel.cellAt(r, k).firstCursorPosition()
            b = quelle.cellAt(r, k).begin()
            erster = True
            while not b.atEnd():
                blk = b.currentBlock()
                b += 1
                if not blk.isValid():
                    continue
                if not erster:
                    zc.insertBlock()
                _inline(zc, blk, cf, False)
                erster = False
    ende = ziel.lastCursorPosition()
    ende.movePosition(QTextCursor.NextCharacter)          # hinter die Tabelle (dort liegt immer ein Absatz)
    st.frisch = True
    st.listen.clear()
    st.tabelle = True
    return ende


def einfuegen(editor, cursor: QTextCursor, text: str) -> None:
    """Markdown-Text an ``cursor`` einfügen — Überschriften als Formatvorlagen, Listen als echte Listen, Tabellen als Tabellen,
    Fett/Kursiv als Zeichenformat. Format und Schrift der Stelle bleiben für den Fließtext. Ein Schritt für Rückgängig, wenn der Aufrufer ihn bündelt."""
    quelle = dokument(text)
    merk = QTextCursor(editor.textCursor())
    basis_bf = _fliesstext_format(cursor.blockFormat())
    stelle_ist_vorlage = cursor.blockFormat().headingLevel() > 0
    basis_cf = _basis_zeichen(cursor.charFormat())
    c = QTextCursor(cursor)
    st = _Zustand()
    it = quelle.rootFrame().begin()
    while not it.atEnd():
        rahmen, blk = it.currentFrame(), it.currentBlock()
        it += 1
        if isinstance(rahmen, QTextTable):
            c = _tabelle(editor, c, st, rahmen, basis_bf, basis_cf)
            continue
        if not blk.isValid():
            continue
        ebene = blk.blockFormat().headingLevel()
        liste = blk.textList()
        if ebene:
            _block_bereit(c, st, basis_bf, basis_cf)
            _aus_liste(c); st.listen.clear()
            _inline(c, blk, basis_cf, True)
            name = f"Überschrift {ebene}"
            editor._stil_auf_block(c.block(), name if name in stile.namen() else "Überschrift 1")
        elif liste is not None:
            _block_bereit(c, st, basis_bf, basis_cf)
            _liste_zuordnen(c, st, liste)
            _inline(c, blk, basis_cf, False)
        else:
            st.listen.clear()
            _block_bereit(c, st, basis_bf, basis_cf, mitte_ok=quelle.blockCount() == 1)      # nur eine einzelne Zeile läuft im Satz weiter
            _inline(c, blk, basis_cf, False)
            if stelle_ist_vorlage and c.block().blockFormat().headingLevel() > 0:
                editor._stil_auf_block(c.block(), "Standard")
    if st.tabelle:
        editor.setTextCursor(merk)
