"""Eigenschaften einer Tabelle lesen und setzen (Fenster „Tabelleneigenschaften“). Keine Oberfläche; Maße in Millimetern.

    w = lesen(tabelle, cursor)          # dict, siehe ``VORGABE``
    anwenden(tabelle, cursor, w)        # ein Rückgängig-Schritt
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCharFormat, QTextFrameFormat, QTextLength, QTextTableFormat

from lunivo_writer.models.page import mm_to_px, px_to_mm

VORGABE = {"breite_art": "prozent", "breite": 100.0, "ausr": "links", "innen": 1.0, "abstand": 0.0, "rahmen": 1.0,
           "spalte": 0.0, "spalte_fest": False, "senkrecht": "oben"}
_AUSR = {"links": Qt.AlignLeft, "mitte": Qt.AlignHCenter, "rechts": Qt.AlignRight}
_SENKRECHT = {"oben": QTextCharFormat.AlignTop, "mitte": QTextCharFormat.AlignMiddle, "unten": QTextCharFormat.AlignBottom}


def lesen(t, c) -> dict:
    f = t.format()
    b = f.width()
    zelle = t.cellAt(c)
    sp = f.columnWidthConstraints()
    s = sp[zelle.column()] if zelle.column() < len(sp) else QTextLength()
    al = f.alignment()
    sk = {v: k for k, v in _SENKRECHT.items()}.get(zelle.format().toTableCellFormat().verticalAlignment(), "oben")
    return {"breite_art": "prozent" if b.type() == QTextLength.PercentageLength else "fest" if b.type() == QTextLength.FixedLength else "auto",
            "breite": b.rawValue() if b.type() == QTextLength.PercentageLength else px_to_mm(b.rawValue()),
            "ausr": "mitte" if al & Qt.AlignHCenter else "rechts" if al & Qt.AlignRight else "links",
            "innen": px_to_mm(f.cellPadding()), "abstand": px_to_mm(f.cellSpacing()), "rahmen": f.border() * 0.2646,
            "spalte": px_to_mm(s.rawValue()) if s.type() == QTextLength.FixedLength else 0.0,
            "spalte_fest": s.type() == QTextLength.FixedLength, "senkrecht": sk}


def anwenden(t, c, w: dict) -> None:
    w = {**VORGABE, **w}
    spalte = t.cellAt(c).column()
    zelle = t.cellAt(c)
    c.beginEditBlock()
    f = t.format()
    if w["breite_art"] == "prozent":
        f.setWidth(QTextLength(QTextLength.PercentageLength, w["breite"]))
    elif w["breite_art"] == "fest":
        f.setWidth(QTextLength(QTextLength.FixedLength, mm_to_px(w["breite"])))
    else:
        f.setWidth(QTextLength())
    f.setAlignment(_AUSR[w["ausr"]])
    f.setCellPadding(mm_to_px(w["innen"])); f.setCellSpacing(mm_to_px(w["abstand"]))
    f.setBorder(round(w["rahmen"] / 0.2646))
    if f.border():
        f.setBorderStyle(QTextFrameFormat.BorderStyle_Solid)
    lang = f.columnWidthConstraints() or [QTextLength() for _ in range(t.columns())]
    lang = list(lang) + [QTextLength()] * (t.columns() - len(lang))
    lang[spalte] = QTextLength(QTextLength.FixedLength, mm_to_px(w["spalte"])) if w["spalte_fest"] and w["spalte"] > 0 else QTextLength()
    f.setColumnWidthConstraints(lang)
    t.setFormat(f)
    zf = zelle.format().toTableCellFormat()
    zf.setVerticalAlignment(_SENKRECHT[w["senkrecht"]])
    zelle.setFormat(zf)
    c.endEditBlock()
