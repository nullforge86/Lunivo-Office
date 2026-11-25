"""Absatzsatz über eine beliebige ``TextLayoutEngine``: Läufe in verschiedenen Schriften und Bilder in der Zeile, Zeilen mit Einzug und Ausrichtung
(links, rechts, zentriert, Blocksatz), Tabstopps (links, rechts, zentriert, Standardabstand, hängender Einzug), Zeilenhöhen, Cursorstelle zu einem Zeichen
und Treffertest (Punkt → Zeichen).
Rechnet nur mit Zahlen; die Engine liefert Maße und Vorschübe."""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from lunivo_writer.kern.textsatz import bidi
from .engine import FontSpec, LineBox, TextLayoutEngine
from .wortumbruch import LEERZEICHEN
from .zeilenumbruch import zeilen_umbrechen
from .textpositionen import TextPositionen
from .tabstopps import (TAB, TAB_LINKS, TAB_MITTE, TAB_RECHTS, TAB_TRENNZEICHEN, naechster_stopp as _naechster_stopp,  # noqa: F401
                        tab_vorschuebe as _tab_vorschuebe)
from .textmessung import zeilenhoehe, zeilenmasse  # noqa: F401

AUSRICHTUNGEN = ("left", "right", "center", "justify")
OBJEKT = "￼"
MIN_ZEILENBREITE = 40.0                 # schmaler als das darf neben einem schwebenden Rahmen keine Zeile werden
TAB_DURCHLAEUFE = 4                     # so oft werden Tabbreiten und Zeilenumbruch höchstens gegeneinander abgeglichen


@dataclass(frozen=True)
class Objekt:
    """Ein Bild (oder anderes Stück fester Größe) in der Zeile; steht im Text als U+FFFC. Es steht auf der Grundlinie."""
    breite: float
    hoehe: float


@dataclass(frozen=True)
class SatzZeile:
    """Eine gesetzte Zeile: ``box`` (Zeichenbereich, Breite, Höhe), Versatz ``x`` vom linken Rand der Spalte, ``y`` vom Absatzanfang, Zeilenhöhe ``hoehe`` (nach Zeilenabstand)
    und ``wort_zuschlag`` (Blocksatz: so viel kommt zu jedem Leerzeichen der Zeile hinzu)."""
    box: LineBox
    x: float
    y: float
    hoehe: float
    wort_zuschlag: float = 0.0

    @property
    def ende(self) -> int:
        return self.box.start + self.box.length


@dataclass(frozen=True)
class Lauf:
    """Ein Stück des Absatztextes in einer Schrift (oder ein Objekt) mit seinem Stil (Farbe, Unterstreichen … für das Zeichnen)."""
    start: int
    ende: int
    schrift: FontSpec | Objekt
    stil: dict[str, object]


@dataclass
class Absatzsatz(TextPositionen):
    text: str
    zeilen: list[SatzZeile]
    vorschuebe: list[float]
    laeufe: list[Lauf] = field(default_factory=list)
    tab_fuell: dict[int, str] = field(default_factory=dict)  # Zeichenstelle eines Tabulators → Füllzeichen seiner Strecke (".", "-", "_", "·")
    ebenen: list[int] | None = None                          # bidirektionale Ebene je Zeichen; ``None``: nur links nach rechts
    basis: int = 0                                           # Grundrichtung des Absatzes: 0 links nach rechts, 1 rechts nach links
    _zeilenpos: dict = field(default_factory=dict, repr=False, compare=False)

    @property
    def hoehe(self) -> float:
        return self.zeilen[-1].y + self.zeilen[-1].hoehe if self.zeilen else 0.0


def _lauf_maße(engine: TextLayoutEngine, laeufe: list, richtung: str | None = None) -> tuple[str, list[float], list[tuple[float, float]], list[Lauf], list[int] | None, int]:
    """Text, Vorschub je Zeichen, (Oberlänge, Zeilenhöhe) je Zeichen, die Läufe aus ``(text, FontSpec | Objekt[, Stil])``, die bidirektionalen Ebenen
    (``None`` ohne Zeichen rechts nach links) und die Grundrichtung."""
    gesamt = "".join(eintrag[0] if not isinstance(eintrag[1], Objekt) else OBJEKT * len(eintrag[0]) for eintrag in laeufe)
    bd = bidi.ebenen(gesamt, richtung)
    ebenen, basis = (bd if bd is not None else (None, bidi.basis_ebene(gesamt, richtung)))
    text, adv, hoehen, info = [], [], [], []
    pos = 0
    for eintrag in laeufe:
        t, f = eintrag[0], eintrag[1]
        stil = eintrag[2] if len(eintrag) > 2 else {}
        info.append(Lauf(pos, pos + len(t), f, stil))
        if isinstance(f, Objekt):
            for _ in t:
                text.append(OBJEKT); adv.append(f.breite); hoehen.append((f.hoehe, f.hoehe))
            pos += len(t)
            continue
        steig, tief = zeilenmasse(engine, f)
        text.append(t)
        if ebenen is None:
            breiten = [g.advance for g in engine.shape_text(t, f)]
        else:                                                                    # je Abschnitt gleicher Ebene formen, damit jede Schrift ihre Richtung bekommt
            breiten = []
            i = 0
            while i < len(t):
                j = i + 1
                while j < len(t) and ebenen[pos + j] % 2 == ebenen[pos + i] % 2:
                    j += 1
                breiten.extend(g.advance for g in engine.shape_text(t[i:j], f))
                i = j
        if stil.get("sperrung_prozent"):                                         # Laufweite in Prozent des Vorschubs
            breiten = [a * stil["sperrung_prozent"] / 100.0 for a in breiten]
        if stil.get("sperrung") or stil.get("wortabstand"):                      # feste Laufweite nach jedem Zeichen, Wortabstand nach jedem Leerzeichen
            breiten = [a + stil.get("sperrung", 0.0) + (stil.get("wortabstand", 0.0) if c in LEERZEICHEN else 0.0) for a, c in zip(breiten, t)]
        adv.extend(breiten)
        hoehen.extend([(steig, steig + tief)] * len(t))
        pos += len(t)
    return "".join(text), adv, hoehen, info, ebenen, basis


def absatz_setzen(engine: TextLayoutEngine, laeufe: list, breite: float, ausrichtung: str = "left", einzug_erste: float = 0.0,
                  einzug_links: float = 0.0, einzug_rechts: float = 0.0, zeilen_art: str = "single", zeilen_wert: float = 100.0,
                  leer_schrift: FontSpec | None = None, ausschluss=None, tabs: tuple = (), tab_abstand: float = 0.0,
                  tab_fuell: dict | None = None, richtung: str | None = None, trennstellen=None) -> Absatzsatz:
    """Den Absatz in Zeilen setzen. ``laeufe`` = [(Text, FontSpec)] (ein Bild: (U+FFFC, Objekt)). ``einzug_erste`` gilt zusätzlich in der ersten Zeile
    (negativ: hängender Einzug). Ein leerer Absatz hat eine Zeile in ``leer_schrift``.
    ``ausschluss(y, h)`` → (Einengung links, Einengung rechts, Unterkante oder None): schwebende Rahmen, um die der Text läuft (y relativ zum Absatzanfang).
    ``tabs`` = ((Position vom linken Rand der Spalte, Art[, Trennzeichen]), …), ``tab_fuell`` = {Position: Füllzeichen} und ``tab_abstand`` (Standardabstand; 0: Tabulatoren behalten die Breite ihres Zeichens).
    ``richtung``: „ltr“/„rtl“ erzwingt die Grundrichtung, sonst bestimmt das erste starke Zeichen sie; in einem Absatz rechts nach links gelten „links“ und „rechts“ als Anfang und Ende."""
    text, adv, hoehen, info, ebenen, basis = _lauf_maße(engine, laeufe, richtung)
    if basis == 1 and ausrichtung in ("left", "right"):
        ausrichtung = "right" if ausrichtung == "left" else "left"
    if not text:
        steig, tief = zeilenmasse(engine, leer_schrift or FontSpec("Liberation Sans", 11))
        box = LineBox(0, 0, 0.0, steig + tief, steig)
        return Absatzsatz("", [SatzZeile(box, einzug_links + einzug_erste, 0.0, zeilenhoehe(steig + tief, zeilen_art, zeilen_wert))], [], [], basis=basis)
    silben, strich = frozenset(), 0.0
    if trennstellen is not None:                                              # Silbentrennung: Stellen im Text, Breite des Trennstrichs aus der ersten Schrift
        silben = frozenset(trennstellen(text))
        erste_schrift = next((l[1] for l in laeufe if isinstance(l[1], FontSpec)), leer_schrift)
        strich = engine.measure_text("-", erste_schrift) if silben and erste_schrift is not None else 0.0
    verf = max(1.0, breite - einzug_links - einzug_rechts)
    erste_b = max(1.0, verf - einzug_erste)

    def zeilen_ab(start: int, b: float) -> list[LineBox]:
        res = zeilen_umbrechen(text[start:], adv[start:], b, 0.0, 0.0, frozenset(s - start for s in silben if s > start), strich)
        return [LineBox(z.start + start, z.length, z.width, 0.0, 0.0, z.trennstrich) for z in res]

    def hoehe_von(b: LineBox) -> tuple[float, float]:
        stuecke = hoehen[b.start:b.start + b.length] or hoehen[-1:]
        steig = max(s[0] for s in stuecke)
        return steig, max(max(s[1] - s[0] for s in stuecke) + steig, max(s[1] for s in stuecke))

    def planen() -> list[tuple[LineBox, float, float, float]]:
        """Zeilen als (Zeichenbereich, Versatz links, verfügbare Breite, Lücke davor); ohne ``ausschluss`` mit gleichbleibender Breite."""
        plan: list[tuple[LineBox, float, float, float]] = []
        if ausschluss is None:
            boxen = zeilen_ab(0, erste_b)
            if len(boxen) > 1 and abs(erste_b - verf) > 0.01:
                boxen = boxen[:1] + zeilen_ab(boxen[0].length, verf)
            plan = [(b, 0.0, erste_b if i == 0 else verf, 0.0) for i, b in enumerate(boxen)]
        else:
            start, y = 0, 0.0
            while start < len(text):
                raum = erste_b if start == 0 else verf
                luecke = 0.0
                h_est = max(h[1] for h in hoehen[start:start + 40] or hoehen[-1:])
                for _ in range(40):
                    dl, dr, unter = ausschluss(y + luecke, h_est)
                    if raum - dl - dr >= MIN_ZEILENBREITE or unter is None:
                        break
                    luecke += max(unter - y - luecke, 1.0)                           # zu schmal neben dem Rahmen: die Zeile beginnt darunter
                breite_zeile = max(1.0, raum - dl - dr)
                box = zeilen_ab(start, breite_zeile)[0]
                plan.append((box, dl, breite_zeile, luecke))
                y += luecke + zeilenhoehe(hoehe_von(box)[1], zeilen_art, zeilen_wert)
                if box.length == 0:
                    break
                start = box.start + box.length
        return plan

    tab_stellen = [i for i, c in enumerate(text) if c == TAB] if tab_abstand > 0 else []
    for i in tab_stellen:
        adv[i] = 0.0
    plan = planen()
    tab_stopp: dict[int, float] = {}
    for _ in range(TAB_DURCHLAEUFE if tab_stellen else 0):                       # Tabbreiten hängen von der Stelle in der Zeile ab, der Umbruch von den Breiten
        neu, tab_stopp = _tab_vorschuebe(text, adv, plan, tabs, tab_abstand, einzug_links, einzug_erste)
        if all(abs(neu.get(i, 0.0) - adv[i]) < 0.01 for i in tab_stellen):
            break
        for i in tab_stellen:
            adv[i] = neu.get(i, 0.0)
        plan = planen()
    res, y = [], 0.0
    for i, (b, dl, raum, luecke) in enumerate(plan):
        y += luecke
        steig, natuerlich = hoehe_von(b)
        links = einzug_links + (einzug_erste if i == 0 else 0.0) + dl
        letzte = i == len(plan) - 1
        x, extra = links, 0.0
        zeilentext = text[b.start:b.start + b.length]
        if ausrichtung == "right":
            x = links + raum - b.width
        elif ausrichtung == "center":
            x = links + (raum - b.width) / 2
        elif ausrichtung == "justify" and not letzte and not zeilentext.endswith(("\n", "\u2028")) and not (tab_stellen and TAB in zeilentext):
            luecken = sum(1 for c in zeilentext.rstrip(" \t") if c in LEERZEICHEN)
            if luecken:
                extra = max(0.0, (raum - b.width) / luecken)
        h = natuerlich if (zeilen_art == "proportional" and OBJEKT in zeilentext) else zeilenhoehe(natuerlich, zeilen_art, zeilen_wert)   # Zeile mit Bild/Diagramm: Vielfaches wird nicht auf die Objekthöhe angewendet (wie in Word)
        res.append(SatzZeile(LineBox(b.start, b.length, b.width, natuerlich, steig, b.trennstrich), x, y, h, extra))
        y += h
    if text.endswith(("\n", " ")):                                             # Zeilenumbruch am Ende: eine leere Zeile folgt
        m = hoehen[-1]
        res.append(SatzZeile(LineBox(len(text), 0, 0.0, m[1], m[0]), einzug_links, y, zeilenhoehe(m[1], zeilen_art, zeilen_wert)))
    fuell = {i: z for i, stopp in tab_stopp.items() for pos, z in (tab_fuell or {}).items() if z and abs(pos - stopp) < 0.5}
    return Absatzsatz(text, res, adv, info, fuell, ebenen, basis)
