"""Barrierefreiheit prüfen — was Menschen mit Sehbehinderung den Text unlesbar macht."""
from __future__ import annotations

import re

from PySide6.QtGui import QColor



from core.formatierung.farben.farben import Farbe
def _hell(c: QColor) -> float:
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(c.red()) + 0.7152 * lin(c.green()) + 0.0722 * lin(c.blue())


def kontrast(vorne: QColor, hinten: QColor) -> float:
    a, b = _hell(vorne) + 0.05, _hell(hinten) + 0.05
    return max(a, b) / min(a, b)


_LINK_SCHLECHT = re.compile(r"^(hier|klick|mehr|link|weiter)", re.I)


def _bild_ohne_alt(o) -> bool:
    """Ein Objekt (``InlineObjekt`` oder ``FreiesObjekt``) ohne Alternativtext; dekorative brauchen keinen."""
    if o.daten.get("dekor"):
        return False
    return not (o.alt_text or "").strip()


def _text_durchsuchen(dok, seite: QColor) -> tuple[dict, list, int]:
    """Durchläuft alle Absätze: (Zähler, Überschriftenebenen, Wortzahl)."""
    from core.dokument.dokument import InlineObjekt, Lauf
    from core.formatvorlagen.formatvorlagen import ueberschriftsebene
    from core.layout.drucklayout import formatwerte as F
    z = {"bilder": 0, "farben": 0, "links": 0}
    ebenen: list = []
    woerter = 0
    for a in dok.absaetze():
        lv = ueberschriftsebene(dok, a)
        if lv and a.text().strip():
            ebenen.append(lv)
        woerter += len(a.text().split())
        for x in a.inhalte:
            if isinstance(x, InlineObjekt):
                if x.art in ("bild", "piktogramm", "diagramm", "smartart", "formel", "zeichenbereich", "wordart") and _bild_ohne_alt(x):
                    z["bilder"] += 1
            elif isinstance(x, Lauf) and x.text.strip():
                fmt = F.zeichenformat(dok, a, x.format)
                fg = QColor(str(fmt.get("farbe") or Farbe.SCHWARZ)[:7])
                hg = QColor(str(fmt.get("marker"))[:7]) if fmt.get("marker") else seite
                if kontrast(fg, hg) < 4.5:
                    z["farben"] += 1
                if x.format.get("link") and _LINK_SCHLECHT.match(x.text.strip()):
                    z["links"] += 1
    z["bilder"] += sum(1 for o in dok.objekte.values() if o.art in ("bild", "piktogramm", "diagramm", "smartart", "zeichenbereich") and _bild_ohne_alt(o))
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
    dok = editor.sitzung.dokument
    seite = QColor(editor.page.color or Farbe.WEISS)
    z, ebenen, woerter = _text_durchsuchen(dok, seite)
    funde: list[str] = []
    bilder_ohne = z["bilder"]
    if bilder_ohne:
        funde.append(f"{bilder_ohne} {'Bild hat' if bilder_ohne == 1 else 'Bilder haben'} keine Beschreibung (Alternativtext). "
                     "Wer nicht sieht, erfährt nicht, was darauf ist.")
    funde += _ueberschriften_funde(ebenen, woerter)
    ohne_kopf = sum(1 for t in _tabellen(dok) if not t.format.get("kopfzeilen"))
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


def _tabellen(dok):
    """Alle Tabellen des Dokuments (auch geschachtelte) in Dokumentreihenfolge."""
    from core.dokument.dokument import Tabelle

    def lauf(bloecke):
        for b in bloecke:
            if isinstance(b, Tabelle):
                yield b
                for zeile in b.zellen:
                    for zelle in zeile:
                        yield from lauf(zelle.bloecke)
    for ab in dok.abschnitte:
        yield from lauf(ab.bloecke)
