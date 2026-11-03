"""Eigenschaften einer Tabelle lesen und setzen (Fenster „Tabelleneigenschaften“). Keine Oberfläche; Maße in Millimetern.

    w = lesen(tabelle, cursor)          # dict, siehe ``VORGABE``
    anwenden(tabelle, cursor, w)        # ein Rückgängig-Schritt
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCharFormat, QTextFormat, QTextFrameFormat, QTextLength, QTextTableFormat

from lunivo_writer.models.page import mm_to_px, px_to_mm

Z_MINHOEHE = QTextFormat.UserProperty + 62     # an jeder Zelle einer Zeile: Mindesthöhe der Zeile in Bildpunkten (DOCX: w:trHeight, atLeast)
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


def zelle_teilen(t, c, spalten: int, zeilen: int) -> bool:
    """Teilt die Zelle unter dem Cursor c in spalten x zeilen Zellen (wie „Zellen teilen“).

    Verbundene Zelle: t.splitCell. Unverbundene Zelle: Qt kann nur verbundene Zellen teilen. Gewählte Lösung:
    Tabelle um (spalten-1) Spalten bzw. (zeilen-1) Zeilen direkt hinter der Zelle erweitern und alle anderen
    Zellen derselben Spalte bzw. Zeile über die neuen Spalten/Zeilen verbinden. So bleibt das Gitter der übrigen
    Zellen samt Inhalt unverändert, nur die Ursprungszelle zerfällt. Alles ein Rückgängig-Schritt."""
    spalten, zeilen = max(1, int(spalten)), max(1, int(zeilen))
    if spalten == 1 and zeilen == 1:
        return False
    z = t.cellAt(c)
    if not z.isValid():
        return False
    zr, zc = z.row(), z.column()
    c.beginEditBlock()
    try:
        if z.rowSpan() > 1 or z.columnSpan() > 1:
            # Qt teilt nur innerhalb der vorhandenen Spannweite
            t.splitCell(zr, zc, min(zeilen, z.rowSpan()), min(spalten, z.columnSpan()))
            return True
        if spalten > 1:
            t.insertColumns(zc + 1, spalten - 1)
            r = 0
            while r < t.rows():
                x = t.cellAt(r, zc)
                if r != zr and x.row() == r and x.column() == zc and x.columnSpan() == 1:
                    t.mergeCells(r, zc, x.rowSpan(), spalten)
                r += max(1, t.cellAt(r, zc).rowSpan() if t.cellAt(r, zc).row() == r else 1)
        if zeilen > 1:
            t.insertRows(zr + 1, zeilen - 1)
            j = 0
            while j < t.columns():
                x = t.cellAt(zr, j)
                dazu = zc <= j < zc + spalten
                if not dazu and x.row() == zr and x.column() == j and x.rowSpan() == 1:
                    t.mergeCells(zr, j, zeilen, x.columnSpan())
                j += max(1, x.columnSpan() if x.column() == j else 1)
    finally:
        c.endEditBlock()
    return True


def zeilenhoehe_setzen(t, r: int, px: float, zeile_px: float) -> None:
    """Mindesthöhe ``px`` der Tabellenzeile ``r`` setzen: Zellformat-Eigenschaft ``Z_MINHOEHE`` plus Innenabstand oben/unten
    (Qt kennt keine Zeilenhöhe): Abstand = (Höhe - Zeilenhöhe der Schrift) / 2."""
    pad = max(0.0, (px - zeile_px) / 2)
    for sp in range(t.columns()):
        cell = t.cellAt(r, sp)
        if cell.row() != r:
            continue
        f = cell.format().toTableCellFormat()
        f.setTopPadding(pad); f.setBottomPadding(pad)
        f.setProperty(Z_MINHOEHE, float(px))
        cell.setFormat(f)


def zeilenhoehe_lesen(t, r: int) -> float:
    """Mindesthöhe der Zeile in Bildpunkten; 0, wenn keine gesetzt ist."""
    for sp in range(t.columns()):
        cell = t.cellAt(r, sp)
        f = cell.format()
        if cell.row() == r and f.hasProperty(Z_MINHOEHE):
            return float(f.property(Z_MINHOEHE))
    return 0.0
