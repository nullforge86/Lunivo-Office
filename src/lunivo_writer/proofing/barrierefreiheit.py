"""Barrierefreiheit prüfen — was Menschen mit Sehbehinderung den Text unlesbar macht."""
from __future__ import annotations

import re

from PySide6.QtGui import QColor

from lunivo_writer.services.docx_reader import STYLE_PROP


from lunivo_writer.core.farben import Farbe
def _hell(c: QColor) -> float:
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(c.red()) + 0.7152 * lin(c.green()) + 0.0722 * lin(c.blue())


def kontrast(vorne: QColor, hinten: QColor) -> float:
    a, b = _hell(vorne) + 0.05, _hell(hinten) + 0.05
    return max(a, b) / min(a, b)


_LINK_SCHLECHT = re.compile(r"^(hier|klick|mehr|link|weiter)", re.I)


def _bild_ohne_alt(cf) -> bool:
    bf = cf.toImageFormat()
    alt = bf.property(STYLE_PROP + 1) if bf.hasProperty(STYLE_PROP + 1) else ""
    return not (alt or "").strip()


def _fragment_pruefen(f, seite: QColor, z: dict) -> None:
    """Ein Textstück: Bild ohne Beschreibung, zu blasse Schrift, nichtssagender Verweis (Zähler in ``z``)."""
    cf = f.charFormat()
    if cf.isImageFormat():
        if _bild_ohne_alt(cf):
            z["bilder"] += 1
    elif f.text().strip():
        fg = cf.foreground().color() if cf.foreground().style() != 0 else QColor(Farbe.SCHWARZ)
        hg = cf.background().color() if cf.background().style() != 0 else seite
        if kontrast(fg, hg) < 4.5:
            z["farben"] += 1
        if cf.isAnchor() and cf.anchorHref() and _LINK_SCHLECHT.match(f.text().strip()):
            z["links"] += 1


def _text_durchsuchen(doc, seite: QColor) -> tuple[dict, list, int]:
    """Durchläuft alle Blöcke: (Zähler, Überschriftenebenen, Wortzahl)."""
    z = {"bilder": 0, "farben": 0, "links": 0}
    ebenen: list = []
    woerter = 0
    b = doc.firstBlock()
    while b.isValid():
        lv = b.blockFormat().headingLevel()
        if lv and b.text().strip():
            ebenen.append(lv)
        woerter += len(b.text().split())
        it = b.begin()
        while not it.atEnd():
            f = it.fragment()
            if f.isValid():
                _fragment_pruefen(f, seite, z)
            it += 1
        b = b.next()
    return z, ebenen, woerter


def _ueberschriften_funde(ebenen: list, woerter: int) -> list[str]:
    funde: list[str] = []
    sprung = sum(1 for i in range(1, len(ebenen)) if ebenen[i] - ebenen[i - 1] > 1)
    if sprung:
        funde.append(f"{sprung} {'übersprungene Ebene' if sprung == 1 else 'übersprungene Ebenen'} bei den Überschriften — "
                     "etwa Überschrift 1 direkt gefolgt von Überschrift 3.")
    if not ebenen and woerter > 150:
        funde.append("Der Text hat keine Überschriften. Ab etwa einer Seite fällt das Zurechtfinden schwer.")
    return funde


def _link_fund(n: int) -> str:
    if n == 1:
        return "Ein Verweis heißt nur „hier“ oder „mehr“. Wer sich Verweise vorlesen lässt, hört das ohne Zusammenhang."
    return f"{n} Verweise heißen nur „hier“ oder „mehr“. Wer sich Verweise vorlesen lässt, hört das ohne Zusammenhang."


def pruefe(editor) -> list[str]:
    doc = editor.document()
    seite = QColor(editor.page.color or Farbe.WEISS)
    z, ebenen, woerter = _text_durchsuchen(doc, seite)
    funde: list[str] = []
    bilder_ohne = z["bilder"]
    if bilder_ohne:
        funde.append(f"{bilder_ohne} {'Bild hat' if bilder_ohne == 1 else 'Bilder haben'} keine Beschreibung (Alternativtext). "
                     "Wer nicht sieht, erfährt nicht, was darauf ist.")
    funde += _ueberschriften_funde(ebenen, woerter)
    ohne_kopf = sum(1 for t in _tabellen(doc) if t.format().headerRowCount() < 1)
    if ohne_kopf:
        funde.append(f"{ohne_kopf} {'Tabelle hat' if ohne_kopf == 1 else 'Tabellen haben'} keine Kopfzeile. "
                     "Ohne sie ist unklar, wofür eine Spalte steht.")
    n = z["farben"]
    if n:
        funde.append(f"{n} {'Stelle ist' if n == 1 else 'Stellen sind'} zu blass — unter dem Verhältnis 4,5 zu 1, "
                     "das für Fließtext empfohlen wird.")
    if z["links"]:
        funde.append(_link_fund(z["links"]))
    return funde


def _tabellen(doc):
    from PySide6.QtGui import QTextCursor, QTextTable
    gesehen = set()
    c = QTextCursor(doc)
    b = doc.firstBlock()
    while b.isValid():
        c.setPosition(b.position())
        t = c.currentTable()
        if t is not None and id(t) not in gesehen and t.firstPosition() >= 0:
            key = t.firstPosition()
            if key not in gesehen:
                gesehen.add(key)
                yield t
        b = b.next()
