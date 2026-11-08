"""Sendungen: Umschlag, Etiketten, Seriendruck (mit Feldern, Adressblock, Regeln), Formularfelder."""
from __future__ import annotations

import re

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import (
    QBrush, QColor, QFont, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument, QTextDocumentFragment, QTextFormat,
    QTextLength, QTextTableFormat,
)

from lunivo_writer.models.page import PageSettings, mm_to_px

P_REGEL = QTextFormat.UserProperty + 30          # "Feld|Wert|dann|sonst" — Regel im Serienbrief
FELD_FARBE = "#d0ebff"
REGEL_FARBE = "#ffe8cc"

UMSCHLAEGE = {"DIN lang (220 × 110 mm)": (220, 110), "C6 (162 × 114 mm)": (162, 114), "C5 (229 × 162 mm)": (229, 162),
              "C4 (324 × 229 mm)": (324, 229)}
ETIKETTEN = {"70 × 37 mm — 24 Stück (3 × 8)": (3, 8, 70, 37), "70 × 42,3 mm — 21 Stück (3 × 7)": (3, 7, 70, 42.3),
             "70 × 50,8 mm — 15 Stück (3 × 5)": (3, 5, 70, 50.8), "105 × 42,3 mm — 14 Stück (2 × 7)": (2, 7, 105, 42.3),
             "105 × 148 mm — 4 Stück (2 × 2)": (2, 2, 105, 148)}


# ---- Umschlag und Etiketten -----------------------------------------------------------------------------------
def umschlag_aufbauen(ed, format_name: str, absender: str, empfaenger: str) -> PageSettings:
    b, h = UMSCHLAEGE[format_name]
    pg = PageSettings(width_mm=b, height_mm=h, margin_top_mm=12, margin_bottom_mm=10, margin_left_mm=15, margin_right_mm=12)
    doc = ed.document()
    doc.clear()
    c = QTextCursor(doc)
    f = QTextCharFormat(); f.setFontPointSize(8)
    bf = QTextBlockFormat()
    c.setBlockFormat(bf); c.setBlockCharFormat(f)
    c.insertText(" ".join(z.strip() for z in absender.splitlines() if z.strip()), f)
    bf2 = QTextBlockFormat()
    bf2.setTopMargin(mm_to_px(max(10, h * 0.2))); bf2.setLeftMargin(mm_to_px(b * 0.42))
    f2 = QTextCharFormat(); f2.setFontPointSize(12)
    c.insertBlock(bf2, f2)
    c.insertText(" ".join(z.strip() for z in empfaenger.splitlines() if z.strip()), f2)
    return pg


def etiketten_aufbauen(ed, bogen: str, text: str, gleich: bool) -> PageSettings:
    sp, ze, b, h = ETIKETTEN[bogen]
    pg = PageSettings(margin_top_mm=8, margin_bottom_mm=8, margin_left_mm=5, margin_right_mm=5)
    doc = ed.document()
    doc.clear()
    zeilen = [z.strip() for z in text.splitlines() if z.strip()]
    tf = QTextTableFormat()
    tf.setCellPadding(mm_to_px(2)); tf.setCellSpacing(0); tf.setBorder(0)
    tf.setColumnWidthConstraints([QTextLength(QTextLength.FixedLength, mm_to_px(b))] * sp)
    c = QTextCursor(doc)
    t = c.insertTable(ze, sp, tf)
    n = 0
    for r in range(ze):
        for k in range(sp):
            cell = t.cellAt(r, k)
            cc = cell.firstCursorPosition()
            inhalt = " ".join(zeilen) if gleich else (zeilen[n] if n < len(zeilen) else "")
            f = QTextCharFormat(); f.setFontPointSize(10)
            cc.insertText(inhalt, f)
            n += 1
    # feste Zeilenhöhe: je Zelle ein Absatz mit Mindesthöhe wird mit Qt nicht garantiert — Abstand setzt die Höhe
    for r in range(ze):
        for k in range(sp):
            cc = t.cellAt(r, k).firstCursorPosition()
            bf = cc.blockFormat()
            bf.setBottomMargin(max(0.0, mm_to_px(h) - mm_to_px(2) * 2 - 14 * (len(zeilen) if gleich else 1)))
            cc.setBlockFormat(bf)
    return pg


# ---- Serienbrief -------------------------------------------------------------------------------------------------------------
def tabelle_lesen(roh: str):
    zeilen = [z for z in re.split(r"\r?\n", roh) if z.strip()]
    if len(zeilen) < 2:
        return None
    tr = "\t" if "\t" in zeilen[0] else (";" if ";" in zeilen[0] else ",")
    spalten = [s.strip() for s in zeilen[0].split(tr)]
    saetze = []
    for z in zeilen[1:]:
        w = [x.strip() for x in z.split(tr)]
        saetze.append({n: (w[i] if i < len(w) else "") for i, n in enumerate(spalten)})
    return spalten, saetze


FELD = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")


def felder_im_text(doc: QTextDocument) -> list[str]:
    return sorted(set(m.group(1) for m in FELD.finditer(doc.toPlainText())))


def feld_einfuegen(ed, name: str) -> None:
    c = ed.textCursor()
    vorher = QTextCharFormat(c.charFormat())
    vorher.clearBackground()
    f = QTextCharFormat(vorher); f.setBackground(QBrush(QColor(FELD_FARBE)))
    c.insertText("{{" + name + "}}", f)
    ed.setTextCursor(c)
    ed.setCurrentCharFormat(vorher)                      # dahinter geht es ohne Feldfarbe weiter
    ed.document().setModified(True)


def adressblock_einfuegen(ed, was: str) -> None:
    c = ed.textCursor()
    c.beginEditBlock()

    def feld(n):
        f = QTextCharFormat(); f.setBackground(QBrush(QColor(FELD_FARBE))); c.insertText("{{" + n + "}}", f)

    def text(t):
        c.insertText(t, QTextCharFormat())
    if was in ("adresse", "beides"):
        feld("Name"); c.insertText(" ", QTextCharFormat()); feld("Straße"); c.insertText(" ", QTextCharFormat())
        feld("PLZ"); text(" "); feld("Ort")
    if was == "beides":
        c.insertBlock(); c.insertBlock()
    if was in ("gruss", "beides"):
        text("Sehr geehrte"); feld("Anrede"); text(" "); feld("Name"); text(",")
    c.endEditBlock()
    ed.setTextCursor(c)
    ed.document().setModified(True)


def regel_einfuegen(ed, feld: str, wert: str, dann: str, sonst: str) -> None:
    f = QTextCharFormat(); f.setBackground(QBrush(QColor(REGEL_FARBE)))
    f.setProperty(P_REGEL, "|".join(x.replace("|", "/") for x in (feld, wert, dann, sonst)))
    ed.textCursor().insertText(dann, f)
    ed.document().setModified(True)


def _satz_einsetzen(doc: QTextDocument, satz: dict, von_bis: tuple[int, int] | None = None) -> None:
    """Felder und Regeln mit den Werten von ``satz`` füllen (``von_bis``: nur in diesem Bereich)."""
    lo, hi = von_bis if von_bis else (0, 1 << 30)
    # Regeln zuerst: sie entscheiden anhand eines Feldes, welcher Text stehen bleibt
    stuecke = []
    b = doc.firstBlock()
    while b.isValid():
        it = b.begin()
        while not it.atEnd():
            f = it.fragment()
            if f.isValid() and f.charFormat().hasProperty(P_REGEL) and lo <= f.position() < hi:
                stuecke.append((f.position(), f.position() + f.length(), f.charFormat().stringProperty(P_REGEL), f.charFormat()))
            it += 1
        b = b.next()
    for von, bis, regel, cf in reversed(stuecke):
        feld, wert, dann, sonst = (regel.split("|") + ["", "", "", ""])[:4]
        text = dann if (satz.get(feld, "").strip() == wert.strip()) else sonst
        c = QTextCursor(doc)
        c.setPosition(von); c.setPosition(bis, QTextCursor.KeepAnchor)
        nf = QTextCharFormat(cf)
        nf.setBackground(QBrush(Qt.NoBrush)); nf.clearProperty(P_REGEL)
        c.insertText(text, nf)
        hi += len(text) - (bis - von)
    for name, wert in satz.items():
        c = QTextCursor(doc)
        muster = re.compile(r"\{\{\s*" + re.escape(name) + r"\s*\}\}")
        text = doc.toPlainText()
        for m in reversed(list(muster.finditer(text))):
            if not (lo <= m.start() < hi):
                continue
            hi += len(str(wert)) - (m.end() - m.start())
            c.setPosition(m.start()); c.setPosition(m.end(), QTextCursor.KeepAnchor)
            nf = c.charFormat(); nf.setBackground(QBrush(Qt.NoBrush))
            c.insertText(str(wert), nf)


def brief_fuer(vorlage: QTextDocument, satz: dict | list[dict]) -> QTextDocument:
    """Ein Brief. Steht „Nächster Datensatz“ im Text, gilt hinter jeder solchen Stelle der nächste Satz der Liste ``satz``."""
    saetze = satz if isinstance(satz, list) else [satz]
    d = vorlage.clone()
    muster = re.compile(r"\{\{\s*" + re.escape(NAECHSTER) + r"\s*\}\}")
    stellen = [(m.start(), m.end()) for m in muster.finditer(d.toPlainText())]
    anfang = [0] + [e for _a, e in stellen]                 # Stück k: hinter dem (k-1)-ten bis vor das k-te Feld „Nächster Datensatz“
    ende = [a for a, _e in stellen] + [1 << 30]
    for k in range(len(anfang) - 1, -1, -1):               # von hinten: vordere Stellen verschieben sich nicht
        if k < len(saetze):
            _satz_einsetzen(d, saetze[k], (anfang[k], ende[k]))
        if k:                                               # das Feld „Nächster Datensatz“ vor diesem Stück selbst verschwindet
            c = QTextCursor(d); c.setPosition(stellen[k - 1][0]); c.setPosition(stellen[k - 1][1], QTextCursor.KeepAnchor)
            c.removeSelectedText()
    return d


def saetze_je_brief(vorlage: QTextDocument) -> int:
    """Wie viele Datensätze ein Brief verbraucht (1 + Zahl der Felder „Nächster Datensatz“)."""
    return 1 + len(re.findall(r"\{\{\s*" + re.escape(NAECHSTER) + r"\s*\}\}", vorlage.toPlainText()))


def gruppen(vorlage: QTextDocument, saetze: list[dict]) -> list[list[dict]]:
    n = saetze_je_brief(vorlage)
    return [saetze[i:i + n] for i in range(0, len(saetze), n)]


def serienbrief_erzeugen(quelle: QTextDocument, saetze: list[dict], ziel: QTextDocument) -> int:
    """Alle Briefe in EIN Dokument, durch Seitenumbrüche getrennt. → Zahl der Briefe."""
    ziel.clear()
    c = QTextCursor(ziel)
    briefe = gruppen(quelle, saetze)
    for i, gruppe in enumerate(briefe):
        d = brief_fuer(quelle, gruppe)
        _ressourcen(d, ziel)
        if i:
            bf = QTextBlockFormat(); bf.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore)
            c.insertBlock(bf, QTextCharFormat())
        c.insertFragment(QTextDocumentFragment(d))
    return len(briefe)


# ---- Datenquelle des Seriendrucks -------------------------------------------------------------------------------------
NAECHSTER = "Nächster Datensatz"


def quelle_lesen(pfad: str):
    """Empfängerliste aus einer Textdatei (CSV mit ; oder , oder Tabulator; erste Zeile = Spaltennamen). → (Spalten, Sätze) oder None."""
    for enc in ("utf-8-sig", "cp1252"):
        try:
            with open(pfad, encoding=enc) as fh:
                return tabelle_lesen(fh.read())
        except UnicodeDecodeError:
            continue
    return None


def zugeordnet(satz: dict, zuordnung: dict) -> dict:
    """Satz mit den Namen der Felder im Text: ``zuordnung`` {Feld im Text: Spalte der Quelle}; ohne Eintrag gilt der gleiche Name."""
    aus = dict(satz)
    for feld, spalte in zuordnung.items():
        if spalte in satz:
            aus[feld] = satz[spalte]
    return aus


def felder_hervorheben(doc: QTextDocument, an: bool) -> None:
    """Hintergrund der Felder {{…}} an oder aus. Gehört zum letzten Bearbeitungsschritt und lässt „geändert“ wie es war."""
    war = doc.isModified()
    c = QTextCursor(doc)
    c.joinPreviousEditBlock()
    for m in FELD.finditer(doc.toPlainText()):
        c.setPosition(m.start()); c.setPosition(m.end(), QTextCursor.KeepAnchor)
        f = QTextCharFormat()
        f.setBackground(QBrush(QColor(FELD_FARBE)) if an else QBrush(Qt.NoBrush))
        c.mergeCharFormat(f)
    c.endEditBlock()
    doc.setModified(war)


def naechster_einfuegen(ed) -> None:
    """Feld „Nächster Datensatz“: dahinter füllt der nächste Satz die Felder (z. B. mehrere Etiketten auf einem Blatt)."""
    feld_einfuegen(ed, NAECHSTER)


def _ressourcen(quelle: QTextDocument, ziel: QTextDocument) -> None:
    b = quelle.firstBlock()
    while b.isValid():
        it = b.begin()
        while not it.atEnd():
            f = it.fragment()
            if f.isValid() and f.charFormat().isImageFormat():
                n = f.charFormat().toImageFormat().name()
                r = quelle.resource(QTextDocument.ImageResource, QUrl(n))
                if r is not None:
                    ziel.addResource(QTextDocument.ImageResource, QUrl(n), r)
            it += 1
        b = b.next()


# ---- Formular ------------------------------------------------------------------------------------------------------------------
KASTEN_LEER, KASTEN_VOLL = "☐", "☒"


def form_textfeld(ed, text: str = "Text eingeben") -> None:
    f = QTextCharFormat()
    f.setBackground(QBrush(QColor("#f1f3f5"))); f.setUnderlineStyle(QTextCharFormat.DotLine)
    ed.textCursor().insertText(f"[ {text} ]", f)
    ed.document().setModified(True)


def form_kasten(ed, beschriftung: str = "Auswahl") -> None:
    c = ed.textCursor()
    f = QTextCharFormat(); f.setFontPointSize((ed.document().defaultFont().pointSizeF() or 11) * 1.3)
    c.insertText(KASTEN_LEER, f)
    c.insertText(" " + beschriftung, QTextCharFormat())
    ed.document().setModified(True)


def form_knopf(ed, aufschrift: str) -> None:
    f = QTextCharFormat()
    f.setBackground(QBrush(QColor("#dee2e6"))); f.setFontWeight(QFont.Bold)
    ed.textCursor().insertText(f"  {aufschrift or 'Schaltfläche'}  ", f)
    ed.document().setModified(True)


def kasten_umschalten(ed, pos: int) -> bool:
    """Klick auf ein Kontrollkästchen ☐/☒ wechselt den Zustand."""
    for p in (pos, pos - 1):
        if p < 0:
            continue
        c = QTextCursor(ed.document())
        c.setPosition(p); c.setPosition(p + 1, QTextCursor.KeepAnchor)
        t = c.selectedText()
        if t in (KASTEN_LEER, KASTEN_VOLL):
            c.insertText(KASTEN_VOLL if t == KASTEN_LEER else KASTEN_LEER, c.charFormat())
            return True
    return False
