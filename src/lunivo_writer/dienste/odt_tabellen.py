"""Tabellen aus ODT-Dokumenten in QTextDocument übernehmen."""
from __future__ import annotations

import xml.etree.ElementTree as ET

from PySide6.QtGui import QBrush, QColor, QTextCursor, QTextFrameFormat, QTextLength, QTextTableFormat

from lunivo_writer.dienste.odt_xml import MAX_WIEDERHOLUNG, _q, _px

QTextFrameFormatBorder = QTextFrameFormat.BorderStyle_Solid

_SPALTEN_GRUPPEN = frozenset(_q(t) for t in ("table:table-columns", "table:table-header-columns", "table:table-rows",
                                             "table:table-header-rows", "table:table-column-group", "table:table-row-group"))
_ZELLEN = (_q("table:table-cell"), _q("table:covered-table-cell"))


def _wiederholung(el: ET.Element, attribut: str) -> int:
    """``table:number-…-repeated`` (mindestens 1, höchstens ``MAX_WIEDERHOLUNG``)."""
    return min(MAX_WIEDERHOLUNG, int(el.get(_q(attribut), "1") or 1))


def _spannweite(zelle: ET.Element, attribut: str) -> int:
    return int(zelle.get(_q(attribut), "1") or 1)


def _sammeln(self, e: ET.Element, breiten: list[float], zeilen: list[ET.Element]) -> None:
    """Spaltenbreiten (px) und Zeilen der Tabelle, auch aus Gruppen, mit aufgelösten Wiederholungen."""
    for k in e:
        if k.tag == _q("table:table-column"):
            b = _px(self.stile.eigenschaften("table-column", k.get(_q("table:style-name")), "table-column").get("style:column-width"))
            breiten.extend([b] * _wiederholung(k, "table:number-columns-repeated"))
        elif k.tag == _q("table:table-row"):
            zeilen.extend([k] * _wiederholung(k, "table:number-rows-repeated"))
        elif k.tag in _SPALTEN_GRUPPEN:
            _sammeln(self, k, breiten, zeilen)


def _zellen_der_zeile(zeile: ET.Element) -> list[ET.Element]:
    reihe: list[ET.Element] = []
    for c in zeile:
        if c.tag in _ZELLEN:
            reihe.extend([c] * _wiederholung(c, "table:number-columns-repeated"))
    return reihe


def _tabellenformat(breiten: list[float], spalten: int) -> QTextTableFormat:
    tf = QTextTableFormat()
    tf.setCellPadding(4)
    tf.setCellSpacing(0)
    tf.setBorder(1)
    tf.setBorderBrush(QBrush(QColor("#000000")))
    tf.setBorderStyle(QTextFrameFormatBorder)
    if breiten and len(breiten) == spalten and sum(breiten) > 0:
        tf.setColumnWidthConstraints([QTextLength(QTextLength.PercentageLength, 100 * b / sum(breiten)) for b in breiten])
    return tf


def _zelle_fuellen(self, t, r: int, c: int, zelle: ET.Element, ort, zeilen: int, spalten: int) -> None:
    """Inhalt, Hintergrund und Verbund der Zelle (r, c) übernehmen; verdeckte Zellen bleiben leer."""
    if zelle.tag != _q("table:table-cell"):
        return
    zelle_ort = type(ort)(t.cellAt(r, c).firstCursorPosition())
    hg = self.stile.eigenschaften("table-cell", zelle.get(_q("table:style-name")), "table-cell").get("fo:background-color")
    if hg and hg != "transparent" and QColor(hg).isValid():
        zf = t.cellAt(r, c).format()
        zf.setBackground(QBrush(QColor(hg)))
        t.cellAt(r, c).setFormat(zf)
    self.bereich(list(zelle), zelle_ort)
    zs = _spannweite(zelle, "table:number-rows-spanned")
    ss = _spannweite(zelle, "table:number-columns-spanned")
    if zs > 1 or ss > 1:
        t.mergeCells(r, c, min(zs, zeilen - r), min(ss, spalten - c))


def tabelle(self, el: ET.Element, ort) -> None:
    breiten: list[float] = []
    zeilen: list[ET.Element] = []
    _sammeln(self, el, breiten, zeilen)
    zellen = [_zellen_der_zeile(z) for z in zeilen]
    spalten = max([len(r) for r in zellen] + [len(breiten), 1])
    if not zeilen:
        return
    if not ort.frei:
        ort.cur.insertBlock()
    t = ort.cur.insertTable(len(zeilen), spalten, _tabellenformat(breiten, spalten))
    for r, reihe in enumerate(zellen):
        for c, zelle in enumerate(reihe):
            _zelle_fuellen(self, t, r, c, zelle, ort, len(zeilen), spalten)
    ort.cur = QTextCursor(self.doc)
    ort.cur.setPosition(t.lastPosition() + 1)
    ort.frei = True
