"""Fachliche Zugriffe auf die Formate des Dokumentmodells (``core/document/formate.py``) für Textsatz und Layout. Ohne Qt.

Alle Zahlen sind Bildpunkte (96 dpi), Schriftgrößen Punkt. Was ein Format nicht setzt, kommt aus der Formatvorlage (``formatvorlagen.py``),
dann aus der Grundschrift des Dokuments (``Dokument.standardformat``), dann aus den Standards hier.
"""
from __future__ import annotations

from ..document.dokument import Absatz, Dokument
from ..document.formatvorlagen import wirksames_absatzformat, wirksames_zeichenformat
from ..geometry import mm_to_px
from ..textlayout.engine import FontSpec

STANDARD_FAMILIE = "Liberation Sans"
STANDARD_GROESSE_PT = 11.0
PX_JE_PT = 96.0 / 72.0
TAB_ABSTAND = 80.0                                  # Standardabstand der Tabstopps, wenn das Dokument keinen nennt
TAB_ARTEN = {"links": 0, "rechts": 1, "mitte": 2, "dezimal": 3}
FUELLZEICHEN = {"punkt": ".", "strich": "-", "linie": "_", "mitte": "·"}
KAPITAELCHEN_GROESSE = 0.8                          # Kapitälchen: Kleinbuchstaben als Großbuchstaben in diesem Anteil der Schriftgröße
HOCH_VERSATZ, TIEF_VERSATZ = -0.5, 0.16            # Grundlinie hoch-/tiefgestellter Zeichen, Anteil der (verkleinerten) Schriftgröße
STRICHART = {"gestrichelt": "dash", "gepunktet": "dot", "strichpunkt": "dashdot", "strichpunktpunkt": "dashdotdot"}
AUSRICHTUNG = {"links": "left", "mitte": "center", "rechts": "right", "block": "justify"}
ZEILENABSTAND = {"einfach": "single", "vielfach": "proportional", "genau": "fixed", "mindestens": "min"}


def _zahl(v, standard: float = 0.0) -> float:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else standard


def farbwert(text) -> tuple[int, int, int, int] | None:
    """``#rrggbb`` oder ``#rrggbbaa`` als (r, g, b, a); sonst ``None``."""
    if not isinstance(text, str) or not text.startswith("#") or len(text) not in (7, 9):
        return None
    try:
        r, g, b = (int(text[i:i + 2], 16) for i in (1, 3, 5))
        a = int(text[7:9], 16) if len(text) == 9 else 255
    except ValueError:
        return None
    return r, g, b, a


def zeichenformat(dok: Dokument, absatz: Absatz, fmt: dict) -> dict:
    """Das wirksame Zeichenformat eines Textstücks (Vorlagen aufgelöst); die Grundschrift des Dokuments steht darunter."""
    grund = {k: v for k, v in dok.standardformat.items() if k in ("schrift", "groesse_pt")}
    if absatz.format_aufgeloest:
        return {**grund, **fmt}
    return {**grund, **wirksames_zeichenformat(dok, absatz, fmt)}


def absatzformat(dok: Dokument, absatz: Absatz) -> dict:
    return dict(absatz.format) if absatz.format_aufgeloest else wirksames_absatzformat(dok, absatz)


def schrift(z: dict) -> FontSpec:
    """Die Schrift eines Textstücks aus dem wirksamen Zeichenformat."""
    fam = z.get("schrift")
    if isinstance(fam, (list, tuple)):
        fam = fam[0] if fam else None
    pt = _zahl(z.get("groesse_pt"), STANDARD_GROESSE_PT)
    if pt <= 0:
        pt = STANDARD_GROESSE_PT
    if z.get("hoch_tief") in ("hoch", "tief"):
        pt = pt * 2 / 3
    gewicht = z.get("gewicht")
    if not isinstance(gewicht, int) or isinstance(gewicht, bool) or gewicht <= 0:
        gewicht = 700 if z.get("fett") else 400
    return FontSpec(str(fam) if fam else STANDARD_FAMILIE, float(pt), gewicht, bool(z.get("kursiv")))


def kapitaelchen(z: dict) -> bool:
    return bool(z.get("kapitaelchen"))


def kapitaelchen_stuecke(text: str, font: FontSpec) -> list[tuple[str, FontSpec]]:
    """Der Text als Kapitälchen: Kleinbuchstaben werden zu verkleinerten Großbuchstaben; → [(Text, Schrift)] mit gleicher Zeichenzahl."""
    klein = FontSpec(font.family, font.size_pt * KAPITAELCHEN_GROESSE, font.weight, font.italic)
    aus: list[tuple[str, FontSpec]] = []
    for c in text:
        gross = c.upper()
        ist_klein = c.islower() and len(gross) == 1
        zeichen, f = (gross, klein) if ist_klein else (c, font)
        if aus and aus[-1][1] is f:
            aus[-1] = (aus[-1][0] + zeichen, f)
        else:
            aus.append((zeichen, f))
    return aus


def schreibweise(text: str, z: dict) -> str:
    """Der Text in Großbuchstaben, wenn das Format es verlangt; die Zeichenzahl bleibt gleich (ein Zeichen, das dabei mehrere würde, bleibt stehen)."""
    if not z.get("grossbuchstaben"):
        return text
    return "".join(c.upper() if len(c.upper()) == 1 else c for c in text)


def stil(z: dict) -> dict:
    """Stil eines Textstücks für Satz und Zeichnen: Farbe, Unterstreichen, Überstreichen, Durchstreichen, Hervorheben, Versatz der Grundlinie,
    Laufweite und Wortabstand."""
    hoch = z.get("hoch_tief")
    aus = {"color": farbwert(z.get("farbe")) or (0, 0, 0, 255),
           "underline": bool(z.get("unterstrichen")) or bool(_zahl(z.get("unter_stil"))),
           "strike": bool(z.get("durchgestrichen") or z.get("doppelt_durch")),
           "highlight": farbwert(z.get("marker")),
           "versatz": HOCH_VERSATZ if hoch == "hoch" else TIEF_VERSATZ if hoch == "tief" else 0.0}
    if z.get("doppelt_durch"):
        aus["strike_double"] = True
    if aus["underline"] and z.get("unter_art") in STRICHART:
        aus["underline_dash"] = STRICHART[z["unter_art"]]
    farbe = farbwert(z.get("unter_farbe"))
    if farbe is not None:
        aus["underline_color"] = farbe
    if z.get("ueberstrichen"):
        aus["overline"] = True
    weite = _zahl(z.get("zeichenabstand"))
    if weite:
        if int(_zahl(z.get("zeichenabstand_art"))) == 1:
            aus["sperrung"] = weite                             # Bildpunkte zusätzlich nach jedem Zeichen
        elif weite != 100.0:
            aus["sperrung_prozent"] = weite                     # Vorschub in Prozent
    return aus


# ---- Absatz --------------------------------------------------------------------------------------------------------
def ausrichtung(a: dict) -> str:
    return AUSRICHTUNG.get(a.get("ausrichtung", "links"), "left")


def abstaende(a: dict) -> tuple[float, float]:
    return _zahl(a.get("abstand_vor")), _zahl(a.get("abstand_nach"))


def einzuege(a: dict) -> tuple[float, float, float]:
    """(links, rechts, erste Zeile zusätzlich)."""
    return _zahl(a.get("einzug_links")), _zahl(a.get("einzug_rechts")), _zahl(a.get("einzug_erste"))


def zeilenabstand(a: dict) -> tuple[str, float]:
    art = ZEILENABSTAND.get(a.get("zeilenabstand_art", "einfach"), "single")
    wert = _zahl(a.get("zeilenabstand"), 100.0 if art == "proportional" else 0.0)
    if art == "proportional" and wert <= 10.0:                  # Faktor (1,5) statt Prozent (150)
        wert *= 100.0
    return art, wert


def richtung(a: dict) -> str | None:
    """„rtl“ oder „ltr“, wenn der Absatz die Schreibrichtung festlegt; sonst ``None`` (das erste starke Zeichen entscheidet)."""
    r = a.get("richtung")
    return "rtl" if r in ("rtl", 1) else "ltr" if r in ("ltr", 0) else None


def umbruch_vor(a: dict) -> bool:
    return bool(a.get("seitenumbruch_vor"))


def umbruch_nach(a: dict) -> bool:
    return bool(a.get("seitenumbruch_nach"))


def spaltenumbruch_vor(a: dict) -> bool:
    return bool(a.get("spaltenumbruch_vor"))


def regeln(a: dict) -> dict:
    """Die Umbruchregeln eines Absatzes: ``kontrolle`` (Witwen/Waisen, Vorgabe an), ``nicht_trennen`` (mit dem nächsten zusammen),
    ``zusammen`` (Absatz nicht teilen)."""
    w = {"kontrolle": True, "nicht_trennen": False, "zusammen": False}
    opt = a.get("optionen")
    if isinstance(opt, dict):
        for k in w:
            if k in opt:
                w[k] = bool(opt[k])
    elif isinstance(opt, str):
        for teil in opt.split(";"):
            k, _s, v = teil.partition("=")
            if k in w:
                w[k] = v == "1"
    return w


def option(a: dict, name: str) -> bool:
    opt = a.get("optionen")
    if isinstance(opt, dict):
        return bool(opt.get(name))
    return isinstance(opt, str) and f"{name}=1" in opt.split(";")


def tabstopps(a: dict, dok: Dokument) -> tuple[tuple, float]:
    """((Position, Art, Trennzeichen), …) der Tabstopps des Absatzes, aufsteigend, und der Standardabstand."""
    stopps = []
    for t in a.get("tabstopps") or ():
        if not isinstance(t, (list, tuple)) or not t:
            continue
        art = t[1] if len(t) > 1 else 0
        art = TAB_ARTEN.get(art, 0) if isinstance(art, str) else int(art)
        stopps.append((float(t[0]), art, str(t[2]) if len(t) > 2 and t[2] else ""))
    return tuple(sorted(stopps)), _zahl(dok.eigenschaften.get("tab_abstand"), TAB_ABSTAND) or TAB_ABSTAND


def tabfuellung(a: dict) -> dict[float, str]:
    """Position (Bildpunkte) → Füllzeichen der Tabstopps („Position:Schlüssel;…“)."""
    aus: dict[float, str] = {}
    text = a.get("tabfuell")
    for teil in (text.split(";") if isinstance(text, str) else []):
        pos, _s, schluessel = teil.partition(":")
        try:
            if FUELLZEICHEN.get(schluessel):
                aus[float(pos)] = FUELLZEICHEN[schluessel]
        except ValueError:
            continue
    return aus


def hintergrund(a: dict) -> tuple[int, int, int, int] | None:
    return farbwert(a.get("hintergrund"))


def absatzrahmen(a: dict) -> str | None:
    text = a.get("rahmen")
    return text if isinstance(text, str) and text else None


def listen_einzug(ebene) -> tuple[float, float]:
    """(Beginn der Nummer, Beginn des Textes) einer Listenebene in Bildpunkten vom linken Rand."""
    return mm_to_px(ebene.ausr), mm_to_px(ebene.einzug)
