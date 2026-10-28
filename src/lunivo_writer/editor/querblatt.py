"""Blätter verschiedener Größe im Editor (z. B. ein Querformat-Blatt zwischen Hochformat-Blättern) — nur in der Anzeige beim Bearbeiten.

Qt setzt ein Dokument in einer einzigen Breite und teilt es in gleich hohe Seiten. Hat ein Abschnitt eine andere Blattgröße oder andere
Ränder, setzt der Editor das Dokument in der größten Textbreite und Texthöhe aller Abschnitte und

* gibt den Absätzen (und Tabellen) der schmaleren Abschnitte einen zusätzlichen rechten Einzug (``B_QUERBREITE`` merkt sich, wie viel),
* lässt den Text eines Blattes nicht unter dessen Textfläche laufen und beginnt jeden Abschnitt mit eigener Blattgröße auf einem neuen
  Blatt (``grenzen`` nennt die Absätze, vor die ``seitenfluss`` dafür einen eigenen Seitenumbruch setzt).

Grenze: Qt teilt einen Absatz nur an den (gleich hohen) Seiten des Flusses. Ein einzelner Absatz, der höher ist als die Textfläche eines
niedrigeren Blattes (gut 30 Zeilen auf einem Querformat-Blatt A4), läuft dort über den unteren Rand hinaus.

Gespeichert, gedruckt und als PDF ausgegeben wird immer ohne den Zusatz: ``zuruecknehmen`` und ``bereinigte_kopie``. Wer den rechten
Einzug eines Absatzes liest oder setzt, nimmt ``rechts_px`` und ``rechts_setzen``.

    einrichtungen(doc, page)        → [(erster Absatz, PageSettings)] je Abschnitt
    aktiv(doc, page)                → True, wenn Abschnitte verschieden große Blätter haben (nur einspaltig)
    blattplan(doc, page, ch)        → PageSettings je Seite des Textflusses (ch = Seitenhöhe des Flusses)
"""
from __future__ import annotations

from PySide6.QtGui import QTextCursor, QTextDocument, QTextFormat

from lunivo_writer.models.page import PageSettings

B_QUERBREITE = QTextFormat.UserProperty + 54     # am Absatz/an der Tabelle: zusätzlicher rechter Einzug der Anzeige (Bildpunkte des Layouts; nie gespeichert)


def rechts_px(bf) -> float:
    """Der rechte Einzug, wie ihn der Benutzer eingestellt hat (ohne den Zusatz der Anzeige)."""
    return bf.rightMargin() - (bf.doubleProperty(B_QUERBREITE) if bf.hasProperty(B_QUERBREITE) else 0.0)


def rechts_setzen(bf, px: float) -> None:
    """Rechten Einzug setzen; die Anzeige rechnet ihren Zusatz danach neu hinzu."""
    bf.setRightMargin(px)
    bf.clearProperty(B_QUERBREITE)


def _geometrie(p: PageSettings) -> tuple:
    return (round(p.width_mm, 2), round(p.height_mm, 2), round(p.margin_left_mm, 2), round(p.margin_right_mm, 2),
            round(p.margin_top_mm, 2), round(p.margin_bottom_mm, 2))


def einrichtungen(doc: QTextDocument, page: PageSettings) -> list[tuple[int, PageSettings]]:
    from lunivo_writer.editor import abschnitte as AB
    ab = AB.umbrueche(doc)
    return [(0 if k == 0 else ab[k - 1][0] + 1, AB.einrichtung(doc, page, k)) for k in range(len(ab) + 1)]


def aktiv(doc: QTextDocument, page: PageSettings) -> bool:
    if int(page.spalten) > 1:
        return False
    eins = einrichtungen(doc, page)
    return len(eins) > 1 and all(int(p.spalten) <= 1 for _n, p in eins) and len({_geometrie(p) for _n, p in eins}) > 1


def masse(doc: QTextDocument, page: PageSettings) -> tuple[float, float]:
    """(größte Textbreite, größte Texthöhe) aller Abschnitte in Bildpunkten (ohne Zoom)."""
    eins = einrichtungen(doc, page)
    return max(p.content_width_px for _n, p in eins), max(p.content_height_px for _n, p in eins)


def _abschnitt_je_block(doc, eins):
    """(Block, Einrichtung) für jeden Absatz in Textreihenfolge."""
    k = 0
    b = doc.firstBlock()
    while b.isValid():
        while k + 1 < len(eins) and b.blockNumber() >= eins[k + 1][0]:
            k += 1
        yield b, eins[k][1], k
        b = b.next()


def _setzen(doc, aendern) -> bool:
    war = doc.isModified()
    c = QTextCursor(doc)
    c.joinPreviousEditBlock()
    try:
        geaendert = aendern()
    finally:
        c.endEditBlock()
        doc.setModified(war)
    return geaendert


def breite_anwenden(doc: QTextDocument, page: PageSettings, zoom: float = 1.0, an: bool = True) -> bool:
    """Den Absätzen und Tabellen schmalerer Abschnitte den Zusatz geben (``an=False``: überall wegnehmen). → True bei Änderung."""
    eins = einrichtungen(doc, page) if an else [(0, page)]
    breit = max(p.content_width_px for _n, p in eins)

    def tun() -> bool:
        geaendert = False
        tabellen = {}
        for b, p, _k in _abschnitt_je_block(doc, eins):
            soll = (breit - p.content_width_px) * zoom if an else 0.0
            c = QTextCursor(b)
            t = c.currentTable()
            if t is not None:
                tabellen.setdefault(t.firstPosition(), (t, soll))
                continue
            bf = b.blockFormat()
            ist = bf.doubleProperty(B_QUERBREITE) if bf.hasProperty(B_QUERBREITE) else 0.0
            if abs(soll - ist) > 0.01:
                bf.setRightMargin(bf.rightMargin() - ist + soll)
                if soll > 0.01:
                    bf.setProperty(B_QUERBREITE, float(soll))
                else:
                    bf.clearProperty(B_QUERBREITE)
                c.setBlockFormat(bf)
                geaendert = True
        for t, soll in tabellen.values():
            tf = t.format()
            ist = tf.doubleProperty(B_QUERBREITE) if tf.hasProperty(B_QUERBREITE) else 0.0
            if abs(soll - ist) > 0.01:
                tf.setRightMargin(tf.rightMargin() - ist + soll)
                if soll > 0.01:
                    tf.setProperty(B_QUERBREITE, float(soll))
                else:
                    tf.clearProperty(B_QUERBREITE)
                t.setFormat(tf)
                geaendert = True
        return geaendert
    return _setzen(doc, tun)


def zuruecknehmen(doc: QTextDocument) -> bool:
    """Den Zusatz überall wegnehmen (für Kopien zum Speichern, Drucken, PDF)."""
    from PySide6.QtGui import QTextTable
    b = doc.firstBlock()
    hat = False
    while b.isValid() and not hat:
        hat = b.blockFormat().hasProperty(B_QUERBREITE)
        b = b.next()
    for f in doc.rootFrame().childFrames():
        hat = hat or (isinstance(f, QTextTable) and f.format().hasProperty(B_QUERBREITE))
    if not hat:
        return False

    def tun() -> bool:
        b = doc.firstBlock()
        while b.isValid():
            bf = b.blockFormat()
            if bf.hasProperty(B_QUERBREITE):
                bf.setRightMargin(rechts_px(bf)); bf.clearProperty(B_QUERBREITE)
                QTextCursor(b).setBlockFormat(bf)
            b = b.next()
        for f in doc.rootFrame().childFrames():
            if isinstance(f, QTextTable) and f.format().hasProperty(B_QUERBREITE):
                tf = f.format()
                tf.setRightMargin(tf.rightMargin() - tf.doubleProperty(B_QUERBREITE)); tf.clearProperty(B_QUERBREITE)
                f.setFormat(tf)
        return True
    return _setzen(doc, tun)


def bereinigte_kopie(doc: QTextDocument) -> QTextDocument:
    d = doc.clone()
    zuruecknehmen(d)
    return d


def hat_zusatz(doc: QTextDocument) -> bool:
    b = doc.firstBlock()
    while b.isValid():
        if b.blockFormat().hasProperty(B_QUERBREITE):
            return True
        b = b.next()
    return False


def blattplan(doc: QTextDocument, page: PageSettings, ch: float) -> list[PageSettings]:
    """Einrichtung jeder Seite des Textflusses (Seiten der Höhe ``ch`` im Layout): die des Abschnitts, dessen Text oben auf der Seite steht."""
    eins = einrichtungen(doc, page)
    n = max(1, doc.pageCount())
    plan: list[PageSettings | None] = [None] * n
    lay = doc.documentLayout()
    for b, p, _k in _abschnitt_je_block(doc, eins):
        if not b.isVisible():
            continue
        r = lay.blockBoundingRect(b)
        von, bis = int((r.top() + 1.0) // ch), int((max(r.top(), r.bottom() - 1.0)) // ch)
        for s in range(max(0, von), min(n - 1, bis) + 1):
            if plan[s] is None:
                plan[s] = p
    letzte = eins[0][1]
    for s in range(n):
        plan[s] = plan[s] or letzte
        letzte = plan[s]
    return plan


def grenzen(doc: QTextDocument, page: PageSettings, ch: float, zoom: float = 1.0) -> list:
    """Absätze, vor die ein eigener Seitenumbruch gehört: der erste Absatz eines Abschnitts mit anderer Blattgröße, wenn er nicht oben auf
    einer Seite steht, und ein Absatz, der unter die Textfläche seines Blattes reichen würde (z. B. auf einem Querformat-Blatt)."""
    if ch <= 0:
        return []
    eins = einrichtungen(doc, page)
    plan = blattplan(doc, page, ch)
    lay = doc.documentLayout()
    aus = []
    vorher = None
    for b, p, k in _abschnitt_je_block(doc, eins):
        if not b.isVisible() or b.layout() is None or QTextCursor(b).currentTable() is not None:
            vorher = k
            continue
        tl = b.layout()
        oben = lay.blockBoundingRect(b).top()
        rest = oben % ch
        am_anfang = rest <= 1.0 or ch - rest <= 1.0 or b.blockNumber() == 0       # Rundung: knapp unter der Seitengrenze zählt als oben
        if vorher is not None and k != vorher and _geometrie(p) != _geometrie(eins[vorher][1]) and not am_anfang:
            aus.append(b)
        elif tl.lineCount() and not am_anfang:
            erste = int((oben + tl.lineAt(0).y() + 0.5) // ch)
            if 0 <= erste < len(plan):
                nutz = plan[erste].content_height_px * zoom
                for i in range(tl.lineCount()):
                    z = tl.lineAt(i)
                    y = oben + z.y()
                    if int((y + 0.5) // ch) != erste:
                        break
                    if (y + z.height()) - erste * ch > nutz + 0.5:
                        aus.append(b)
                        break
        vorher = k
    return aus
