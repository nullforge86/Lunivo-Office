"""Fachliche Zugriffe auf die benannten Eigenschaften des Dokumentenmodells (Namen wie die Eigenschaften von Qt-Formaten, siehe ``core/document/model.py``).
Alle Zahlen sind Bildpunkte, Schriftgrößen Punkt; fehlt eine Eigenschaft, gilt der Standard."""
from __future__ import annotations

from lunivo_writer.core.document.model import CharacterFormat, Document, ParagraphFormat
from lunivo_writer.core.document.values import Length
from lunivo_writer.core.textlayout.engine import FontSpec

STANDARD_FAMILIE = "Liberation Sans"
STANDARD_GROESSE_PT = 11.0
PX_JE_PT = 96.0 / 72.0
# Qt-Ausrichtungsbits
LINKS, RECHTS, MITTE, BLOCK = 0x1, 0x2, 0x4, 0x8
# Qt-Seitenumbruchmarken
UMBRUCH_VOR, UMBRUCH_NACH = 0x1, 0x10
ZEILEN_ART = {0: "single", 1: "proportional", 2: "fixed", 3: "min", 4: "single"}


def _zahl(v, standard: float = 0.0) -> float:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else standard


def schrift(cf: CharacterFormat | None, grund: CharacterFormat | None = None) -> FontSpec:
    """Die Schrift eines Textstücks; was es nicht setzt, kommt aus der Grundschrift des Dokuments, dann aus den Standards."""
    def holen(name: str):
        for f in (cf, grund):
            if f is not None and name in f.properties:
                return f.properties[name]
        return None
    fam = holen("FontFamilies") or holen("FontFamily")
    if isinstance(fam, (tuple, list)):
        fam = fam[0] if fam else None
    pt = holen("FontPointSize")
    if not isinstance(pt, (int, float)) or pt <= 0:
        px = holen("FontPixelSize")
        pt = px / PX_JE_PT if isinstance(px, (int, float)) and px > 0 else STANDARD_GROESSE_PT
    gewicht = holen("FontWeight")
    kursiv = holen("FontItalic")
    sub = holen("TextVerticalAlignment")
    if sub in (1, 2):                                                       # Hoch-/Tiefgestellt: verkleinert (wie Qt)
        pt = pt * 2 / 3
    return FontSpec(str(fam) if fam else STANDARD_FAMILIE, float(pt), int(gewicht) if isinstance(gewicht, (int, float)) and gewicht else 400, bool(kursiv))


def ausrichtung(pf: ParagraphFormat, standard: str = "left") -> str:
    a = int(_zahl(pf.properties.get("BlockAlignment"), 0)) & 0xF
    return "justify" if a & BLOCK else "center" if a & MITTE else "right" if a & RECHTS else "left" if a & LINKS else standard


def abstaende(pf: ParagraphFormat) -> tuple[float, float]:
    return _zahl(pf.properties.get("BlockTopMargin")), _zahl(pf.properties.get("BlockBottomMargin"))


def einzuege(pf: ParagraphFormat, einrueck_breite: float) -> tuple[float, float, float]:
    """(links, rechts, erste Zeile zusätzlich): Rand plus Einrückungsstufe mal Stufenbreite."""
    stufe = _zahl(pf.properties.get("BlockIndent")) * einrueck_breite
    return (_zahl(pf.properties.get("BlockLeftMargin")) + stufe, _zahl(pf.properties.get("BlockRightMargin")), _zahl(pf.properties.get("TextIndent")))


def zeilenabstand(pf: ParagraphFormat) -> tuple[str, float]:
    art = ZEILEN_ART.get(int(_zahl(pf.properties.get("LineHeightType"), 0)), "single")
    return art, _zahl(pf.properties.get("LineHeight"), 100.0 if art == "proportional" else 0.0)


def umbruch_vor(pf: ParagraphFormat) -> bool:
    return bool(int(_zahl(pf.properties.get("PageBreakPolicy"))) & UMBRUCH_VOR)


def umbruch_nach(pf: ParagraphFormat) -> bool:
    return bool(int(_zahl(pf.properties.get("PageBreakPolicy"))) & UMBRUCH_NACH)


def laenge(v, gesamt: float) -> float | None:
    """Eine Längenangabe in Bildpunkten; ``None`` bei variabler Länge."""
    if isinstance(v, Length):
        return v.value if v.kind == "fixed" else gesamt * v.value / 100.0 if v.kind == "percentage" else None
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def grundschrift(dok: Document) -> CharacterFormat:
    return dok.default_format


def _brush_farbe(b) -> tuple[int, int, int, int] | None:
    from lunivo_writer.core.document.values import Brush
    if isinstance(b, Brush) and b.style != 0:
        return b.color.r, b.color.g, b.color.b, b.color.a
    return None


def stil(cf: CharacterFormat | None, grund: CharacterFormat | None = None) -> dict:
    """Stil eines Textstücks für das Zeichnen: Farbe, Unterstreichen, Durchstreichen, Hervorheben; was fehlt, kommt aus der Grundschrift."""
    def holen(name: str):
        for f in (cf, grund):
            if f is not None and name in f.properties:
                return f.properties[name]
        return None
    return {"color": _brush_farbe(holen("ForegroundBrush")) or (0, 0, 0, 255), "underline": _zahl(holen("TextUnderlineStyle")) > 0,
            "strike": bool(holen("FontStrikeOut")), "highlight": _brush_farbe(holen("BackgroundBrush"))}


def _roemisch(n: int) -> str:
    teile = ((1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"), (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i"))
    aus = ""
    for wert, z in teile:
        while n >= wert:
            aus += z
            n -= wert
    return aus


def _buchstaben(n: int) -> str:
    aus = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        aus = chr(ord("a") + r) + aus
    return aus


def listenzeichen(stil_nr: int, n: int, vor: str = "", nach: str = ".") -> str:
    """Aufzählungszeichen oder Nummer des ``n``-ten Absatzes einer Liste; ``stil_nr`` wie ``QTextListFormat.Style`` (Punkt -1, Kreis -2, Quadrat -3, Zahl -4, a -5, A -6, i -7, I -8)."""
    if stil_nr in (-1, -2, -3):
        return {-1: "•", -2: "◦", -3: "▪"}[stil_nr]
    zahl = {-4: str(n), -5: _buchstaben(n), -6: _buchstaben(n).upper(), -7: _roemisch(n), -8: _roemisch(n).upper()}.get(stil_nr, str(n))
    return f"{vor}{zahl}{nach}"
