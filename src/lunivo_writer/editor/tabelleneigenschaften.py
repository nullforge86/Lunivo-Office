"""Eigenschaften einer Tabelle lesen und setzen (Fenster „Tabelleneigenschaften“). Keine Oberfläche; Maße in Millimetern.

    w = lesen(tabelle, cursor)          # dict, siehe ``VORGABE``
    anwenden(tabelle, cursor, w)        # ein Rückgängig-Schritt
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetricsF, QTextCharFormat, QTextCursor, QTextFormat, QTextFrameFormat, QTextLength, QTextTableFormat

from lunivo_writer.models.page import mm_to_px, px_to_mm

T_OPTIONEN = QTextFormat.UserProperty + 63     # an der Tabelle: Bit 1 = gebänderte Zeilen, Bit 2 = erste Spalte (Formatoptionen der Tabellentools)
T_VORLAGE = QTextFormat.UserProperty + 64      # an der Tabelle: Name der zuletzt angewendeten Tabellenformatvorlage
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
    w = {**VORGABE, **w}                  # optional: "rahmen_stil" (QTextFrameFormat.BorderStyle_*) - fehlt er, bleibt der Rahmenstil
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
    if f.border() and "rahmen_stil" in w:                       # nur wenn der Aufrufer einen Stil mitgibt; sonst bleibt der bestehende
        f.setBorderStyle(w["rahmen_stil"])
    lang = f.columnWidthConstraints() or [QTextLength() for _ in range(t.columns())]
    lang = list(lang) + [QTextLength()] * (t.columns() - len(lang))
    lang[spalte] = QTextLength(QTextLength.FixedLength, mm_to_px(w["spalte"])) if w["spalte_fest"] and w["spalte"] > 0 else QTextLength()
    f.setColumnWidthConstraints(lang)
    t.setFormat(f)
    zf = zelle.format().toTableCellFormat()
    zf.setVerticalAlignment(_SENKRECHT[w["senkrecht"]])
    zelle.setFormat(zf)
    c.endEditBlock()


def optionen_lesen(t) -> dict:
    """Formatoptionen dieser Tabelle: ``kopf`` (aus der Kopfzeilenzahl), ``streifen``, ``spalte``, ``vorlage`` (Name oder ``""``) und
    ``gesetzt`` (False, wenn noch nie eine Vorlage/Option gesetzt wurde)."""
    f = t.format()
    bits = int(f.property(T_OPTIONEN)) if f.hasProperty(T_OPTIONEN) else 0
    return {"kopf": f.headerRowCount() > 0, "streifen": bool(bits & 1), "spalte": bool(bits & 2),
            "vorlage": str(f.property(T_VORLAGE) or "") if f.hasProperty(T_VORLAGE) else "", "gesetzt": f.hasProperty(T_OPTIONEN)}


def optionen_setzen(t, *, kopf=None, streifen=None, spalte=None, vorlage=None) -> None:
    """Formatoptionen an der Tabelle merken (nur die übergebenen); ``kopf`` setzt die Kopfzeilenzahl (0/1)."""
    o = optionen_lesen(t)
    f = t.format()
    if kopf is not None:
        f.setHeaderRowCount(1 if kopf else 0)
    s = o["streifen"] if streifen is None else streifen
    sp = o["spalte"] if spalte is None else spalte
    f.setProperty(T_OPTIONEN, (1 if s else 0) | (2 if sp else 0))
    if vorlage is not None:
        f.setProperty(T_VORLAGE, vorlage)
    t.setFormat(f)


def zellen_loeschen(t, c, art: str) -> str | None:
    """„Zellen löschen“ für die Zelle bzw. die markierten Zellen: ``art`` = ``zeile``, ``spalte``, ``links`` (Zellen rechts davon rücken
    nach links) oder ``oben`` (Zellen darunter rücken nach oben). Bei „links“/„oben“ wird der Inhalt (QTextDocumentFragment je Zelle)
    nach vorn kopiert und die letzten Zellen werden geleert. Ein Rückgängig-Schritt.

    Rückgabe: ``None`` bei Erfolg, sonst ein Meldetext (verbundene Zellen im Weg, letzte Zeile/Spalte, unbekannte Art)."""
    z = t.cellAt(c)
    if not z.isValid():
        return "Die Schreibmarke steht in keiner Tabellenzelle."
    if c.hasSelection():
        r0, nr, s0, ns = c.selectedTableCells()
        if nr <= 0 or ns <= 0:
            r0, nr, s0, ns = z.row(), 1, z.column(), 1
    else:
        r0, nr, s0, ns = z.row(), 1, z.column(), 1
    if art in ("zeile", "spalte"):
        if art == "zeile" and t.rows() > nr:
            c.beginEditBlock(); t.removeRows(r0, nr); c.endEditBlock(); return None
        if art == "spalte" and t.columns() > ns:
            c.beginEditBlock(); t.removeColumns(s0, ns); c.endEditBlock(); return None
        return "Die letzte Zeile bzw. Spalte kann so nicht gelöscht werden; verwenden Sie „Tabelle löschen“."
    if art not in ("links", "oben"):
        return "Unbekannte Art des Löschens."
    waagrecht = art == "links"
    # Alle Zellen der betroffenen Zeilen (links) bzw. Spalten (oben) ab dem Löschbereich müssen einfache Zellen sein
    linien = range(r0, r0 + nr) if waagrecht else range(s0, s0 + ns)
    laenge = t.columns() if waagrecht else t.rows()
    start = s0 if waagrecht else r0
    schritt = ns if waagrecht else nr
    for ln in linien:
        for j in range(start, laenge):
            x = t.cellAt(ln, j) if waagrecht else t.cellAt(j, ln)
            if x.rowSpan() > 1 or x.columnSpan() > 1:
                return "Verbundene Zellen sind im Weg; die Zellen können nicht verschoben werden."

    def zelle(ln, j):
        return t.cellAt(ln, j) if waagrecht else t.cellAt(j, ln)

    def auswahl(x):
        cur = x.firstCursorPosition()
        cur.setPosition(x.lastCursorPosition().position(), QTextCursor.KeepAnchor)
        return cur
    c.beginEditBlock()
    try:
        for ln in linien:
            teile = [auswahl(zelle(ln, j)).selection() for j in range(start, laenge)]
            for k, j in enumerate(range(start, laenge)):
                cur = auswahl(zelle(ln, j))
                quelle = k + schritt
                if quelle < len(teile):
                    cur.insertFragment(teile[quelle])
                else:
                    cur.removeSelectedText()
    finally:
        c.endEditBlock()
    return None


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


MIN_SPALTE_PX = 24.0


def an_inhalt_anpassen(t, c) -> None:
    """Jede Spalte so schmal wie ihr breitester Zellentext (+ 2x Innenabstand + Rand); Tabellenbreite variabel. Ein Rückgängig-Schritt.

    Verbundene Zellen über mehrere Spalten werden nicht berücksichtigt."""
    f = t.format()
    rand = float(f.border())
    pad = f.cellPadding()
    breiten = [MIN_SPALTE_PX] * t.columns()
    for r in range(t.rows()):
        for s in range(t.columns()):
            z = t.cellAt(r, s)
            if z.row() != r or z.column() != s or z.columnSpan() > 1:
                continue
            fm = QFontMetricsF(z.format().font())
            cur = z.firstCursorPosition()
            blk = cur.block()
            w = 0.0
            while blk.isValid() and blk.position() <= z.lastPosition():
                bf = QFontMetricsF(blk.charFormat().font() if blk.text() else z.format().font())
                w = max(w, bf.horizontalAdvance(blk.text()))
                blk = blk.next()
            breiten[s] = max(breiten[s], w + 2 * pad + 2 * rand)
    c.beginEditBlock()
    f.setColumnWidthConstraints([QTextLength(QTextLength.FixedLength, b) for b in breiten])
    f.setWidth(QTextLength())
    t.setFormat(f)
    c.endEditBlock()


MIN_SPALTE = 12.0            # kleinste Spaltenbreite beim Skalieren/Ziehen (Bildpunkte)


def _zoom(t) -> float:
    """Ansichtsfaktor des Layouts (Zeichengerät 96 dpi x Zoom): Layoutmaße / Faktor = Dokumentmaße."""
    dev = t.document().documentLayout().paintDevice()
    return dev.logicalDpiX() / 96.0 if dev is not None else 1.0


def _zellen_der_zeile(t, r: int):
    """Zellen, die in Zeile ``r`` beginnen und nur eine Zeile hoch sind."""
    for sp in range(t.columns()):
        z = t.cellAt(r, sp)
        if z.row() == r and z.column() == sp and z.rowSpan() == 1:
            yield z


def _textHoehe(t, r: int) -> float:
    """Höhe des höchsten Zelleninhalts der Zeile (ohne Innenabstand), aus dem Layout."""
    lay = t.document().documentLayout()
    h = 0.0
    for z in _zellen_der_zeile(t, r):
        a = z.firstCursorPosition().block(); b = z.lastCursorPosition().block()
        if a.isValid() and b.isValid():
            h = max(h, lay.blockBoundingRect(b).bottom() - lay.blockBoundingRect(a).top())
    return h / _zoom(t)


def _zeilen_oberkanten(t) -> list[float]:
    """y der Oberkante jeder Zeile (Dokumentkoordinaten), gemessen an Zelleninhalt minus oberem Innenabstand."""
    lay = t.document().documentLayout()
    pad_t = t.format().cellPadding()
    ys = []
    for r in range(t.rows()):
        y = None
        for z in _zellen_der_zeile(t, r):
            f = z.format().toTableCellFormat()
            pad = f.topPadding() if f.topPadding() > 0 else pad_t
            v = lay.blockBoundingRect(z.firstCursorPosition().block()).top() - pad
            y = v if y is None else min(y, v)
        ys.append(y if y is not None else (ys[-1] if ys else lay.frameBoundingRect(t).top()))
    return ys


def _unterkante(t) -> float:
    """Layout-y der Unterkante der Tabelle: Ende des Inhalts der letzten Zeile plus unterer Innenabstand."""
    lay = t.document().documentLayout()
    pad_t = t.format().cellPadding(); y = None
    for z in _zellen_der_zeile(t, t.rows() - 1):
        f = z.format().toTableCellFormat()
        pad = f.bottomPadding() if f.bottomPadding() > 0 else pad_t
        v = lay.blockBoundingRect(z.lastCursorPosition().block()).bottom() + pad
        y = v if y is None else max(y, v)
    return y if y is not None else lay.frameBoundingRect(t).bottom()


def tabelle_basis(t) -> tuple[list[float], list[float]]:
    """(Spaltenbreiten, Zeilenhöhen) der Tabelle in Bildpunkten des Dokuments (zoomunabhängig): Breiten aus festen
    Constraints, sonst aus dem Layout; Höhen aus dem Layout (Abstand der Zeilenoberkanten, letzte bis Tabellenunterkante)."""
    lay = t.document().documentLayout()
    rect = lay.frameBoundingRect(t)
    n = t.columns()
    lang = t.format().columnWidthConstraints()
    if len(lang) == n and all(x.type() == QTextLength.FixedLength for x in lang):
        breiten = [float(x.rawValue()) for x in lang]            # feste Längen sind Dokumentmaße
    else:
        f = t.format(); halb = f.cellPadding() + f.cellSpacing() / 2
        xs = [0.0]
        for i in range(1, n):
            xs.append(lay.blockBoundingRect(t.cellAt(0, i).firstCursorPosition().block()).left() - rect.left() - halb)
        xs.append(rect.width())
        z = _zoom(t)
        breiten = [(xs[i + 1] - xs[i]) / z for i in range(n)]
    ys = _zeilen_oberkanten(t)
    ys.append(_unterkante(t))
    z = _zoom(t)
    return breiten, [max(1.0, (ys[i + 1] - ys[i]) / z) for i in range(t.rows())]


def zeilengrenzen(t) -> list[float]:
    """y der inneren waagrechten Zeilenränder (n-1 Stück) in Layoutkoordinaten des Dokuments (wie ``_grenzen`` der Spalten,
    also mit Zoom; für die Lage der Griffe). Dokumentmaße: Wert / Zoom, oder ``tabelle_basis``."""
    ys = _zeilen_oberkanten(t)
    return [float(y) for y in ys[1:]]


def zeilen_mindesthoehe(t, r: int) -> float:
    """Kleinste zulässige Höhe der Zeile: Inhalt plus Innenabstand oben und unten."""
    return max(_textHoehe(t, r), 1.0) + 2 * t.format().cellPadding()


def _zeile_setzen(t, r: int, px: float) -> None:
    px = max(px, zeilen_mindesthoehe(t, r))
    zeilenhoehe_setzen(t, r, px, _textHoehe(t, r) or 1.0)


def zeile_hoehe_ziehen(t, zeile: int, neue_hoehe_px: float) -> None:
    """Mindesthöhe nur der Zeile ``zeile`` auf ``neue_hoehe_px`` setzen (nie unter dem Inhalt). Der Aufrufer öffnet den
    Rückgängig-Block (ein Schritt je Ziehvorgang)."""
    if 0 <= zeile < t.rows():
        _zeile_setzen(t, zeile, float(neue_hoehe_px))


def _zeilen_setzen(t, ziele: list[tuple[int, float]]) -> None:
    """Mindesthöhen mehrerer Zeilen setzen. Die Textmaße aller Zeilen werden zuerst gemessen (ein Layoutlauf); danach
    werden nur Zeilen angefasst, deren Höhe oder Innenabstand sich um mehr als 0,5 Bildpunkte ändert."""
    mess = [(r, px, _textHoehe(t, r)) for r, px in ziele]
    pad_t = t.format().cellPadding()
    for r, px, th in mess:
        px = max(px, max(th, 1.0) + 2 * pad_t)
        zeile_px = th or 1.0
        pad = max(0.0, (px - zeile_px) / 2)
        for z in _zellen_der_zeile_alle(t, r):
            f = z.format()
            if (f.hasProperty(Z_MINHOEHE) and abs(float(f.property(Z_MINHOEHE)) - px) <= 0.5
                    and abs(f.toTableCellFormat().topPadding() - pad) <= 0.5):
                break                                           # Zeile unverändert: nichts anfassen
            zeilenhoehe_setzen(t, r, px, zeile_px)
            break


def _zellen_der_zeile_alle(t, r: int):
    """Erste in Zeile ``r`` beginnende Zelle (Stellvertreter für den Ist-Zustand der Zeile)."""
    for sp in range(t.columns()):
        z = t.cellAt(r, sp)
        if z.row() == r:
            yield z
            return


def skalierungs_kosten(t) -> int:
    """Aufwand eines Skalierungsschritts: Anzahl der Zellen. Der Aufrufer kann bei großen Tabellen auf einen Vorschaurahmen wechseln."""
    return t.rows() * t.columns()


def tabelle_skalieren_spalten(t, basis_breiten, faktor_b: float) -> None:
    """Nur die Spaltenbreiten = Basis x ``faktor_b`` (mind. ``MIN_SPALTE``, Tabellenbreite variabel); die Zeilenhöhen
    folgen dem Umbruch (Zeilen, deren Höhe sich nicht ändert, bleiben unberührt). Der Aufrufer öffnet den Rückgängig-Block."""
    f = t.format()
    f.setColumnWidthConstraints([QTextLength(QTextLength.FixedLength, max(MIN_SPALTE, b * faktor_b)) for b in basis_breiten])
    f.setWidth(QTextLength())
    t.setFormat(f)


def tabelle_skalieren_zeilen(t, basis_hoehen, faktor_h: float) -> None:
    """Nur die Zeilenhöhen = Basis x ``faktor_h`` (mind. Inhalt); unveränderte Zeilen bleiben unberührt."""
    _zeilen_setzen(t, [(r, h * faktor_h) for r, h in enumerate(basis_hoehen[:t.rows()])])


def tabelle_skalieren(t, basis_breiten, basis_hoehen, faktor_b: float, faktor_h: float) -> None:
    """Spaltenbreiten = Basis x ``faktor_b`` (feste Längen, mind. ``MIN_SPALTE``, Tabellenbreite variabel), Zeilenhöhen =
    Basis x ``faktor_h`` (mind. Inhalt). Der Aufrufer öffnet den Rückgängig-Block."""
    tabelle_skalieren_spalten(t, basis_breiten, faktor_b)
    tabelle_skalieren_zeilen(t, basis_hoehen, faktor_h)


def spalten_gleich(t) -> None:
    """Alle Spalten gleich breit bei unveränderter Gesamtbreite (Prozentbreite bleibt Prozentbreite). Ein Rückgängig-Schritt."""
    n = t.columns()
    f = t.format()
    if f.width().type() == QTextLength.PercentageLength:
        f.setColumnWidthConstraints([QTextLength(QTextLength.PercentageLength, 100.0 / n)] * n)
    else:
        gesamt = sum(tabelle_basis(t)[0])
        f.setColumnWidthConstraints([QTextLength(QTextLength.FixedLength, gesamt / n)] * n)
    t.setFormat(f)


def zeilen_gleich(t) -> None:
    """Alle Zeilen auf die Höhe der höchsten Zeile bringen (aufrunden). Ein Rückgängig-Schritt je Aufruf über den Aufrufer."""
    hoehen = tabelle_basis(t)[1]
    if hoehen:
        ziel = max(hoehen)
        for r in range(t.rows()):
            _zeile_setzen(t, r, ziel)


def spalten_festschreiben(t) -> None:
    """Aktuelle Spaltenbreiten als feste Längen festschreiben; Tabellenbreite variabel."""
    f = t.format()
    f.setColumnWidthConstraints([QTextLength(QTextLength.FixedLength, b) for b in tabelle_basis(t)[0]])
    f.setWidth(QTextLength())
    t.setFormat(f)


_RICHTUNG = {"links": (0, -1), "rechts": (0, 1), "oben": (-1, 0), "unten": (1, 0)}


def linie_loeschen(t, zeile: int, spalte: int, seite: str) -> bool:
    """Löscht die Linie auf der Seite (links/rechts/oben/unten) der Zelle: verbindet die Zelle mit dem Nachbarn dahinter.

    Der Bereich aus beiden Zellen (samt bereits verbundener) muss ein Rechteck ergeben, sonst passiert nichts (False)."""
    if seite not in _RICHTUNG:
        return False
    z = t.cellAt(zeile, spalte)
    if not z.isValid():
        return False
    dr, ds = _RICHTUNG[seite]
    if dr > 0: nr, ns = z.row() + z.rowSpan(), spalte
    elif dr < 0: nr, ns = z.row() - 1, spalte
    elif ds > 0: nr, ns = zeile, z.column() + z.columnSpan()
    else: nr, ns = zeile, z.column() - 1
    if not (0 <= nr < t.rows() and 0 <= ns < t.columns()):
        return False
    n = t.cellAt(nr, ns)
    if not n.isValid() or n.firstPosition() == z.firstPosition():
        return False
    r0 = min(z.row(), n.row()); r1 = max(z.row() + z.rowSpan(), n.row() + n.rowSpan())
    c0 = min(z.column(), n.column()); c1 = max(z.column() + z.columnSpan(), n.column() + n.columnSpan())
    # Rechteck-Prüfung: keine Zelle im Bereich darf über ihn hinausragen
    for r in range(r0, r1):
        for s in range(c0, c1):
            x = t.cellAt(r, s)
            if x.row() < r0 or x.column() < c0 or x.row() + x.rowSpan() > r1 or x.column() + x.columnSpan() > c1:
                return False
    t.mergeCells(r0, c0, r1 - r0, c1 - c0)
    return True
