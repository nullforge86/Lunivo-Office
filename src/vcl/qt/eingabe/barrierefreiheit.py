"""Barrierefreiheit prüfen — was Menschen mit Sehbehinderung den Text unlesbar macht."""
from __future__ import annotations

from PySide6.QtGui import QColor



from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
def _hell(c: QColor) -> float:
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(c.red()) + 0.7152 * lin(c.green()) + 0.0722 * lin(c.blue())


def kontrast(vorne: QColor, hinten: QColor) -> float:
    a, b = _hell(vorne) + 0.05, _hell(hinten) + 0.05
    return max(a, b) / min(a, b)


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
    from writer.funktionen import bearbeiten as _bearbeiten
    seite = QColor(editor.page.color or Farbe.WEISS)
    b = _bearbeiten.barrierefreiheit_befund(editor.kennung)                # das Dokument durchläuft das Framework; hier wird nur der Farbkontrast bewertet
    blass = sum(1 for farbe, marker in b.textfarben
                if kontrast(QColor(str(farbe or Farbe.SCHWARZ)[:7]), QColor(str(marker)[:7]) if marker else seite) < 4.5)
    funde: list[str] = []
    bilder_ohne = b.bilder_ohne_text
    if bilder_ohne:
        funde.append(f"{bilder_ohne} {'Bild hat' if bilder_ohne == 1 else 'Bilder haben'} keine Beschreibung (Alternativtext). "
                     "Wer nicht sieht, erfährt nicht, was darauf ist.")
    funde += _ueberschriften_funde(list(b.ebenen), b.woerter)
    ohne_kopf = b.tabellen_ohne_kopf
    if ohne_kopf:
        funde.append(f"{ohne_kopf} {'Tabelle hat' if ohne_kopf == 1 else 'Tabellen haben'} keine Kopfzeile. "
                     "Ohne sie ist unklar, wofür eine Spalte steht.")
    n = blass
    if n:
        funde.append(f"{n} {'Stelle ist' if n == 1 else 'Stellen sind'} zu blass — unter dem Verhältnis 4,5 zu 1, "
                     "das für Fließtext empfohlen wird.")
    if b.schlechte_links:
        funde.append(_link_fund(b.schlechte_links))
    return funde
