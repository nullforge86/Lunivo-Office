"""RTF-Dokumentaufbau: Zwischenmodell (Absätze, Tabellen, Läufe) → QTextDocument; Kopf-/Fußzeilentext."""
from __future__ import annotations

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import (QBrush, QColor, QFont, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument, QTextFormat,
                           QTextFrameFormat, QTextImageFormat, QTextLength, QTextListFormat, QTextTableFormat)

from lunivo_writer.models.page import HeaderFooter
from lunivo_writer.services.rtf.modell import Absatz, Tabelle, Ziel

# feste Farben von \highlightN (RTF-Spezifikation)
_MARKER = {1: "#000000", 2: "#0000ff", 3: "#00ffff", 4: "#00ff00", 5: "#ff00ff", 6: "#ff0000", 7: "#ffff00", 8: "#ffffff",
           9: "#000080", 10: "#008080", 11: "#008000", 12: "#800080", 13: "#800000", 14: "#808000", 15: "#808080", 16: "#c0c0c0"}
_AUSRICHTUNG = {"qc": Qt.AlignHCenter, "qr": Qt.AlignRight, "qj": Qt.AlignJustify}
_AUSRICHTUNG_TEXT = {"qc": "center", "qr": "right", "qj": "justify"}
_STANDARD_ZEICHEN = tuple(sorted({"fs": 24}.items()))


def absatzformat(a: dict) -> QTextBlockFormat:
    bf = QTextBlockFormat()
    bf.setAlignment(_AUSRICHTUNG.get(a.get("q", ""), Qt.AlignLeft))
    for k, setzen in (("li", bf.setLeftMargin), ("ri", bf.setRightMargin), ("sb", bf.setTopMargin), ("sa", bf.setBottomMargin)):
        if a.get(k):
            setzen(max(0, a[k]) / 15)
    if a.get("fi"):
        bf.setTextIndent(a["fi"] / 15)
    if a.get("pagebb") or a.get("pagebb_einmal"):
        bf.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore)
    if a.get("h"):
        bf.setHeadingLevel(a["h"])
    return bf


def tabellenformat(t: Tabelle, spalten: int) -> QTextTableFormat:
    tf = QTextTableFormat()
    tf.setCellPadding(4)
    tf.setCellSpacing(0)
    tf.setBorder(1)
    tf.setBorderBrush(QBrush(QColor("#000000")))
    tf.setBorderStyle(QTextFrameFormat.BorderStyle_Solid)
    grenzen = next((c for r, c in t.zeilen if len(c) == spalten), None)
    if grenzen and grenzen[-1] > 0:
        breiten = [b - a for a, b in zip([0] + grenzen[:-1], grenzen)]
        if all(b > 0 for b in breiten):
            tf.setColumnWidthConstraints([QTextLength(QTextLength.PercentageLength, 100 * b / sum(breiten)) for b in breiten])
    return tf


class Bauer:
    def __init__(self, z, doc: QTextDocument):
        self.z, self.doc = z, doc
        self.bild_n = 0

    # ---- Zeichenformat --------------------------------------------------------------------------------------------------
    def zeichenformat(self, schl: tuple) -> QTextCharFormat:
        z = dict(schl)
        cf = QTextCharFormat()
        f = z.get("f")
        name = self.z.schriften.get(f if f is not None else self.z.standard_schrift)
        if name:
            cf.setFontFamilies([name])
        cf.setFontPointSize(max(1, z.get("fs", 24)) / 2)
        self._stil(cf, z)
        farbe = self._farbe(z.get("cf"))
        if farbe:
            cf.setForeground(QBrush(QColor(farbe)))
        hg = _MARKER.get(z["hl"]) if z.get("hl") else self._farbe(z.get("cb"))
        if hg:
            cf.setBackground(QBrush(QColor(hg)))
        return cf

    @staticmethod
    def _stil(cf: QTextCharFormat, z: dict) -> None:
        if z.get("b"):
            cf.setFontWeight(QFont.Bold)
        if z.get("i"):
            cf.setFontItalic(True)
        if z.get("ul"):
            cf.setFontUnderline(True)
        if z.get("strike"):
            cf.setFontStrikeOut(True)
        if z.get("va") == "super":
            cf.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        elif z.get("va") == "sub":
            cf.setVerticalAlignment(QTextCharFormat.AlignSubScript)

    def _farbe(self, i: int | None) -> str | None:
        if i is None or i <= 0 or i >= len(self.z.farben):
            return None
        return self.z.farben[i]

    # ---- Absätze --------------------------------------------------------------------------------------------------------
    def absatz(self, a: Absatz, cur: QTextCursor, frei: bool, liste_vorher: dict) -> None:
        bf = absatzformat(a.props)
        if a.liste:
            bf.setTextIndent(0)
            bf.setLeftMargin(0)
        erstes = next((lf for lf in a.laeufe if lf[0] == "t"), None)
        grund = self.zeichenformat(erstes[2] if erstes else _STANDARD_ZEICHEN)
        if frei:
            cur.setBlockFormat(bf)
            cur.setBlockCharFormat(grund)
        else:
            cur.insertBlock(bf, grund)
        if a.liste:
            self._liste(a, cur, liste_vorher)
        else:
            liste_vorher.clear()
        for lauf in a.laeufe:
            if lauf[0] == "t":
                cur.insertText(lauf[1], self.zeichenformat(lauf[2]))
            else:
                self._bild(lauf, cur)

    @staticmethod
    def _liste(a: Absatz, cur: QTextCursor, liste_vorher: dict) -> None:
        ebene = max(1, round(a.props.get("li", 0) / 360)) if a.props.get("li") else 1
        vorher = liste_vorher.get("l")
        if vorher is not None and liste_vorher.get("art") == a.liste and liste_vorher.get("ebene") == ebene:
            vorher.add(cur.block())
            return
        lf = QTextListFormat()
        lf.setStyle(QTextListFormat.ListDecimal if a.liste == "zahl" else QTextListFormat.ListDisc)
        lf.setIndent(ebene)
        liste_vorher.update(l=cur.createList(lf), art=a.liste, ebene=ebene)

    def _bild(self, lauf: tuple, cur: QTextCursor) -> None:
        self.bild_n += 1
        name = f"rtf-bild-{self.bild_n}"
        self.doc.addResource(QTextDocument.ImageResource, QUrl(name), lauf[1])
        f = QTextImageFormat()
        f.setName(name)
        f.setWidth(lauf[2][0])
        f.setHeight(lauf[2][1])
        cur.insertImage(f)

    # ---- Dokument und Tabellen ------------------------------------------------------------------------------------------
    def teile(self, teile: list, cur: QTextCursor) -> None:
        frei = True
        liste: dict = {}
        for t in teile:
            if isinstance(t, Absatz):
                self.absatz(t, cur, frei, liste)
                frei = False
                continue
            liste.clear()
            self._tabelle(t, cur, frei)
            frei = True

    def _tabelle(self, t: Tabelle, cur: QTextCursor, frei: bool) -> None:
        spalten = max(max((len(r) for r, _c in t.zeilen), default=1), 1)
        if not frei:
            cur.insertBlock()
        tab = cur.insertTable(len(t.zeilen), spalten, tabellenformat(t, spalten))
        for r, (reihe, _c) in enumerate(t.zeilen):
            for c, zelle in enumerate(reihe):
                zc = tab.cellAt(r, c).firstCursorPosition()
                zfrei, zliste = True, {}
                for a in zelle:
                    self.absatz(a, zc, zfrei, zliste)
                    zfrei = False
        cur.setPosition(tab.lastPosition() + 1)


def kopf_fuss_text(ziel: Ziel, report) -> HeaderFooter:
    absaetze = [a for a in ziel.teile if isinstance(a, Absatz)]
    if ziel.laeufe:
        absaetze.append(Absatz({}, ziel.laeufe, None))
    zeilen = ["".join(lf[1] for lf in a.laeufe if lf[0] == "t").replace(" ", "\n") for a in absaetze]
    text = "\n".join(zeilen).strip("\n")
    ausr = _AUSRICHTUNG_TEXT.get(absaetze[0].props.get("q", ""), "left") if absaetze else "left"
    if any(lf[0] == "b" for a in absaetze for lf in a.laeufe):
        report.warn("Bilder in Kopf- und Fußzeile aus der RTF-Datei wurden nicht übernommen.")
    return HeaderFooter(text, ausr)
