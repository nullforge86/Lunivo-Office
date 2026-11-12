"""Fachliche Zugriffe auf die benannten Eigenschaften des Dokumentenmodells (Namen wie die Eigenschaften von Qt-Formaten, siehe ``core/document/model.py``).
Alle Zahlen sind Bildpunkte, Schriftgrößen Punkt; fehlt eine Eigenschaft, gilt der Standard."""
from __future__ import annotations

from lunivo_writer.core.document.model import CharacterFormat, Document, ParagraphFormat
from lunivo_writer.core.document.values import Color, Length, LineSpacing, TabStop
from lunivo_writer.core.textlayout.engine import FontSpec

STANDARD_FAMILIE = "Liberation Sans"
STANDARD_GROESSE_PT = 11.0
PX_JE_PT = 96.0 / 72.0
# Qt-Ausrichtungsbits
LINKS, RECHTS, MITTE, BLOCK = 0x1, 0x2, 0x4, 0x8
# Qt-Seitenumbruchmarken
UMBRUCH_VOR, UMBRUCH_NACH = 0x1, 0x10
ZEILEN_ART = {0: "single", 1: "proportional", 2: "fixed", 3: "min", 4: "single"}
TAB_ABSTAND = 80.0                                                          # Standardabstand der Tabstopps, wenn das Dokument keinen nennt
HOCH, TIEF, SENKRECHT_MITTE, SENKRECHT_UNTEN = 1, 2, 3, 5                   # senkrechte Ausrichtung (Zeichenformat; Mitte/unten gelten für Tabellenzellen)
GROSS, KLEIN, KAPITAELCHEN, WORTANFANG_GROSS = 1, 2, 3, 4                    # Schreibweise (``FontCapitalization``)
KAPITAELCHEN_GROESSE = 0.8                                                  # Kapitälchen: Kleinbuchstaben als Großbuchstaben in diesem Anteil der Schriftgröße
P_ABSATZRAHMEN = "user:1048581"                                             # Absatzrahmen (``B_RAHMEN``)
P_TABFUELL = "user:1048613"                                                 # Füllzeichen der Tabstopps (``B_TABFUELL``)
FUELLZEICHEN = {"punkt": ".", "strich": "-", "linie": "_", "mitte": "·"}
SPERRUNG_PROZENT, SPERRUNG_FEST = 0, 1                                      # Art der Laufweite (``FontLetterSpacingType``)
STRICHART = {2: "dash", 3: "dot", 4: "dashdot", 5: "dashdotdot"}                     # Unterstreichungsarten mit unterbrochener Linie (``TextUnderlineStyle``)
HOCH_VERSATZ, TIEF_VERSATZ = -0.5, 0.16                                     # Grundlinie hoch-/tiefgestellter Zeichen, Anteil der (verkleinerten) Schriftgröße in Bildpunkten


def _zahl(v, standard: float = 0.0) -> float:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else standard


def schrift(cf: CharacterFormat | None, grund: CharacterFormat | None = None) -> FontSpec:
    """Die Schrift eines Textstücks; was es nicht setzt, kommt aus der Grundschrift des Dokuments, dann aus den Standards."""
    def holen(name: str | tuple[str, ...], semantik: str | None = None):
        for f in (cf, grund):
            if f is None:
                continue
            wert = getattr(f, semantik, None) if semantik else None
            if wert is not None:
                return wert
            for key in (name,) if isinstance(name, str) else name:
                if key in f.properties:
                    return f.properties[key]
        return None
    fam = holen(("FontFamilies", "FontFamily"), "family")
    if isinstance(fam, (tuple, list)):
        fam = fam[0] if fam else None
    pt = holen("FontPointSize", "size_pt")
    if not isinstance(pt, (int, float)) or pt <= 0:
        px = holen("FontPixelSize")
        pt = px / PX_JE_PT if isinstance(px, (int, float)) and px > 0 else STANDARD_GROESSE_PT
    gewicht = holen("FontWeight", "weight")
    kursiv = holen("FontItalic", "italic")
    sub = holen("TextVerticalAlignment")
    if sub in (1, 2):                                                       # Hoch-/Tiefgestellt: verkleinert (wie Qt)
        pt = pt * 2 / 3
    return FontSpec(str(fam) if fam else STANDARD_FAMILIE, float(pt), int(gewicht) if isinstance(gewicht, (int, float)) and gewicht else 400, bool(kursiv))


def ausrichtung(pf: ParagraphFormat, standard: str = "left") -> str:
    if pf.alignment in ("left", "right", "center", "justify"):
        return pf.alignment
    a = int(_zahl(pf.properties.get("BlockAlignment"), 0)) & 0xF
    return "justify" if a & BLOCK else "center" if a & MITTE else "right" if a & RECHTS else "left" if a & LINKS else standard


def abstaende(pf: ParagraphFormat) -> tuple[float, float]:
    davor = pf.space_before_px if pf.space_before_px is not None else pf.properties.get("BlockTopMargin")
    danach = pf.space_after_px if pf.space_after_px is not None else pf.properties.get("BlockBottomMargin")
    return _zahl(davor), _zahl(danach)


def einzuege(pf: ParagraphFormat, einrueck_breite: float) -> tuple[float, float, float]:
    """(links, rechts, erste Zeile zusätzlich): Rand plus Einrückungsstufe mal Stufenbreite."""
    stufe = _zahl(pf.properties.get("BlockIndent")) * einrueck_breite
    links = pf.left_indent_px if pf.left_indent_px is not None else pf.properties.get("BlockLeftMargin")
    rechts = pf.right_indent_px if pf.right_indent_px is not None else pf.properties.get("BlockRightMargin")
    erste = pf.first_line_indent_px if pf.first_line_indent_px is not None else pf.properties.get("TextIndent")
    return (_zahl(links) + stufe, _zahl(rechts), _zahl(erste))


def zeilenabstand(pf: ParagraphFormat) -> tuple[str, float]:
    spacing = pf.line_spacing
    if isinstance(spacing, LineSpacing):
        if spacing.kind == "multiple":
            return "proportional", spacing.value * 100.0
        art = {"single": "single", "proportional": "proportional", "fixed": "fixed", "minimum": "min"}.get(spacing.kind)
        if art is not None:
            return art, spacing.value
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


def tabstopps(pf: ParagraphFormat, dok: Document) -> tuple[tuple, float]:
    """((Position, Art, Trennzeichen), …) der Tabstopps des Absatzes (sonst die des Dokuments), aufsteigend, und der Standardabstand."""
    eigene = pf.properties.get("TabPositions") or dok.text_option.get("tabs") or ()
    stopps = tuple(sorted((float(t.position), int(t.kind), str(t.delimiter or "")) for t in eigene if isinstance(t, TabStop)))
    return stopps, _zahl(dok.text_option.get("tab_stop_distance"), TAB_ABSTAND) or TAB_ABSTAND


def tabfuellung(pf: ParagraphFormat) -> dict[float, str]:
    """Position (Bildpunkte) → Füllzeichen der Tabstopps des Absatzes (``P_TABFUELL``: „Position:Schlüssel;…“)."""
    aus: dict[float, str] = {}
    text = pf.properties.get(P_TABFUELL)
    for teil in (text.split(";") if isinstance(text, str) else []):
        pos, _s, schluessel = teil.partition(":")
        try:
            if FUELLZEICHEN.get(schluessel):
                aus[float(pos)] = FUELLZEICHEN[schluessel]
        except ValueError:
            continue
    return aus


def absatzrahmen(pf: ParagraphFormat) -> str | None:
    """Die Rahmenangabe des Absatzes („Farbe|Breite pt|Art|Seiten|Abstände“, siehe ``core/rendering/linien.rahmen_aus_text``) oder ``None``."""
    text = pf.properties.get(P_ABSATZRAHMEN)
    return text if isinstance(text, str) and text else None


def kapitaelchen(cf: CharacterFormat | None, grund: CharacterFormat | None = None) -> bool:
    for f in (cf, grund):
        if f is not None and "FontCapitalization" in f.properties:
            return int(_zahl(f.properties["FontCapitalization"])) == KAPITAELCHEN
    return False


def kapitaelchen_stuecke(text: str, font: FontSpec) -> list[tuple[str, FontSpec]]:
    """Der Text als Kapitälchen: Kleinbuchstaben werden zu verkleinerten Großbuchstaben, alles andere bleibt; → [(Text, Schrift)] mit gleicher Zeichenzahl."""
    klein = FontSpec(font.family, font.size_pt * KAPITAELCHEN_GROESSE, font.weight, font.italic)
    aus: list[tuple[str, FontSpec]] = []
    for c in text:
        gross = c.upper()
        ist_klein = c.islower() and len(gross) == 1
        z, f = (gross, klein) if ist_klein else (c, font)
        if aus and aus[-1][1] is f:
            aus[-1] = (aus[-1][0] + z, f)
        else:
            aus.append((z, f))
    return aus


def hintergrund(pf: ParagraphFormat) -> tuple[int, int, int, int] | None:
    """Füllfarbe des Absatzes (Schattierung) oder ``None``."""
    return _brush_farbe(pf.properties.get("BackgroundBrush"))


def grundschrift(dok: Document) -> CharacterFormat:
    return dok.default_format


def _brush_farbe(b) -> tuple[int, int, int, int] | None:
    from lunivo_writer.core.document.values import Brush
    if isinstance(b, Brush) and b.style != 0:
        return b.color.r, b.color.g, b.color.b, b.color.a
    return None


def stil(cf: CharacterFormat | None, grund: CharacterFormat | None = None) -> dict:
    """Stil eines Textstücks für Satz und Zeichnen: Farbe, Unterstreichen (Art, Farbe), Überstreichen, Durchstreichen, Hervorheben, Versatz der Grundlinie (hoch-/tiefgestellt), Laufweite und Wortabstand; was fehlt, kommt aus der Grundschrift."""
    def holen(name: str):
        for f in (cf, grund):
            if f is None:
                continue
            semantik = {"ForegroundBrush": "foreground_color", "FontUnderline": "underline"}.get(name)
            wert = getattr(f, semantik, None) if semantik else None
            if wert is not None:
                return wert
            if name in f.properties:
                return f.properties[name]
        return None
    hoch = int(_zahl(holen("TextVerticalAlignment")))
    unter = int(_zahl(holen("TextUnderlineStyle")))
    weite = _zahl(holen("FontLetterSpacing"))
    fest = int(_zahl(holen("FontLetterSpacingType"))) == SPERRUNG_FEST
    farbe = holen("ForegroundBrush")
    if not isinstance(farbe, Color):
        farbe = _brush_farbe(farbe)
    unter_semantik = next((f.underline for f in (cf, grund) if f is not None and f.underline is not None), None)
    aus = {"color": _farbwert(farbe) or (0, 0, 0, 255), "underline": unter_semantik if unter_semantik is not None else unter > 0 or bool(holen("FontUnderline")),
           "strike": bool(holen("FontStrikeOut")), "highlight": _brush_farbe(holen("BackgroundBrush")),
           "versatz": HOCH_VERSATZ if hoch == HOCH else TIEF_VERSATZ if hoch == TIEF else 0.0}
    if aus["underline"] and unter in STRICHART:
        aus["underline_dash"] = STRICHART[unter]
    farbe = _farbwert(holen("TextUnderlineColor"))
    if farbe is not None:
        aus["underline_color"] = farbe
    if holen("FontOverline"):
        aus["overline"] = True
    if fest and weite:
        aus["sperrung"] = weite                                             # Bildpunkte zusätzlich nach jedem Zeichen
    elif not fest and weite and weite != 100.0:
        aus["sperrung_prozent"] = weite                                     # Vorschub in Prozent
    if _zahl(holen("FontWordSpacing")):
        aus["wortabstand"] = _zahl(holen("FontWordSpacing"))
    return aus


def _farbwert(v) -> tuple[int, int, int, int] | None:
    from lunivo_writer.core.document.values import Color
    return (v.r, v.g, v.b, v.a) if isinstance(v, Color) else _brush_farbe(v)


def schreibweise(text: str, cf: CharacterFormat | None, grund: CharacterFormat | None = None) -> str:
    """Der Text in der Schreibweise des Formats (Großbuchstaben, Kleinbuchstaben, Wortanfänge groß); die Zeichenzahl bleibt gleich (ein Zeichen, das dabei mehrere würde, bleibt stehen)."""
    art = None
    for f in (cf, grund):
        if f is not None and "FontCapitalization" in f.properties:
            art = int(_zahl(f.properties["FontCapitalization"]))
            break
    if art not in (GROSS, KLEIN, WORTANFANG_GROSS):
        return text

    def eins(c: str, gross: bool) -> str:
        n = c.upper() if gross else c.lower()
        return n if len(n) == 1 else c
    if art == WORTANFANG_GROSS:
        return "".join(eins(c, True) if i == 0 or not text[i - 1].isalnum() else c for i, c in enumerate(text))
    return "".join(eins(c, art == GROSS) for c in text)


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
