"""Absatzsatz über eine beliebige ``TextLayoutEngine``: Läufe in verschiedenen Schriften und Bilder in der Zeile, Zeilen mit Einzug und Ausrichtung
(links, rechts, zentriert, Blocksatz), Zeilenhöhen, Cursorstelle zu einem Zeichen und Treffertest (Punkt → Zeichen).
Rechnet nur mit Zahlen; die Engine liefert Maße und Vorschübe."""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from lunivo_writer.core.textlayout.engine import FontSpec, LineBox, TextLayoutEngine
from lunivo_writer.core.textlayout.hb_engine import LEERZEICHEN, zeilen_umbrechen

AUSRICHTUNGEN = ("left", "right", "center", "justify")
OBJEKT = "￼"
MIN_ZEILENBREITE = 40.0                 # schmaler als das darf neben einem schwebenden Rahmen keine Zeile werden


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
    schrift: object                      # FontSpec oder Objekt
    stil: dict


@dataclass
class Absatzsatz:
    text: str
    zeilen: list[SatzZeile]
    vorschuebe: list[float]
    laeufe: list = field(default_factory=list)

    @property
    def hoehe(self) -> float:
        return self.zeilen[-1].y + self.zeilen[-1].hoehe if self.zeilen else 0.0

    def zeile_von(self, index: int) -> int:
        for i, z in enumerate(self.zeilen):
            if index < z.ende or i == len(self.zeilen) - 1:
                return i
        return 0

    def cursor_x(self, index: int, zeile: int | None = None) -> float:
        """Stelle des Cursors vor dem Zeichen ``index`` vom linken Rand der Spalte (in der Zeile, die ``index`` enthält, oder in ``zeile``)."""
        z = self.zeilen[self.zeile_von(index) if zeile is None else zeile]
        index = max(z.box.start, min(index, z.ende))
        breite = sum(self.vorschuebe[z.box.start:index])
        luecken = sum(1 for c in self.text[z.box.start:index] if c in LEERZEICHEN) if z.wort_zuschlag else 0
        return z.x + breite + luecken * z.wort_zuschlag

    def zeile_bei_y(self, y: float) -> int:
        for i, z in enumerate(self.zeilen):
            if y < z.y + z.hoehe:
                return i
        return len(self.zeilen) - 1

    def treffer(self, x: float, y: float) -> int:
        """Zeichenstelle des Cursors für den Punkt (x, y) im Absatz: die Zeile nach y, darin die nächste Zeichengrenze."""
        if not self.zeilen:
            return 0
        zi = self.zeile_bei_y(y)
        z = self.zeilen[zi]
        ende = z.ende - (1 if self.text[z.box.start:z.ende].endswith(("\n", " ")) else 0)
        best, abstand = z.box.start, float("inf")
        for i in range(z.box.start, ende + 1):
            d = abs(self.cursor_x(i, zi) - x)
            if d < abstand:
                best, abstand = i, d
        return best


def zeilenhoehe(natuerlich: float, art: str = "single", wert: float = 100.0) -> float:
    """Zeilenhöhe nach Zeilenabstand: ``single`` (wert ignoriert), ``proportional`` (Prozent), ``fixed`` (Bildpunkte), ``min`` (mindestens Bildpunkte)."""
    if art == "proportional":
        return natuerlich * wert / 100.0
    if art == "fixed":
        return float(wert)
    if art == "min":
        return max(natuerlich, float(wert))
    return natuerlich


def zeilenmasse(engine: TextLayoutEngine, font: FontSpec) -> tuple[float, float]:
    """(Oberlänge, Unterlänge) einer Zeile in dieser Schrift: wie bei Qt auf ganze Bildpunkte aufgerundet (die Zeilenhöhe von ``QTextLine`` ist ganzzahlig)."""
    m = engine.font_metrics(font)
    return float(math.ceil(m.ascent - 1e-6)), float(math.ceil(m.descent - 1e-6))


def _lauf_maße(engine: TextLayoutEngine, laeufe: list) -> tuple[str, list[float], list[tuple[float, float]], list[Lauf]]:
    """Text, Vorschub je Zeichen, (Oberlänge, Zeilenhöhe) je Zeichen und die Läufe aus ``(text, FontSpec | Objekt[, Stil])``."""
    text, adv, hoehen, info = [], [], [], []
    pos = 0
    for eintrag in laeufe:
        t, f = eintrag[0], eintrag[1]
        stil = eintrag[2] if len(eintrag) > 2 else {}
        info.append(Lauf(pos, pos + len(t), f, stil))
        pos += len(t)
        if isinstance(f, Objekt):
            for _ in t:
                text.append(OBJEKT); adv.append(f.breite); hoehen.append((f.hoehe, f.hoehe))
            continue
        steig, tief = zeilenmasse(engine, f)
        text.append(t)
        adv.extend(g.advance for g in engine.shape_text(t, f))
        hoehen.extend([(steig, steig + tief)] * len(t))
    return "".join(text), adv, hoehen, info


def absatz_setzen(engine: TextLayoutEngine, laeufe: list, breite: float, ausrichtung: str = "left", einzug_erste: float = 0.0,
                  einzug_links: float = 0.0, einzug_rechts: float = 0.0, zeilen_art: str = "single", zeilen_wert: float = 100.0,
                  leer_schrift: FontSpec | None = None, ausschluss=None) -> Absatzsatz:
    """Den Absatz in Zeilen setzen. ``laeufe`` = [(Text, FontSpec)] (ein Bild: (U+FFFC, Objekt)). ``einzug_erste`` gilt zusätzlich in der ersten Zeile
    (negativ: hängender Einzug). Ein leerer Absatz hat eine Zeile in ``leer_schrift``.
    ``ausschluss(y, h)`` → (Einengung links, Einengung rechts, Unterkante oder None): schwebende Rahmen, um die der Text läuft (y relativ zum Absatzanfang)."""
    text, adv, hoehen, info = _lauf_maße(engine, laeufe)
    if not text:
        steig, tief = zeilenmasse(engine, leer_schrift or FontSpec("Liberation Sans", 11))
        box = LineBox(0, 0, 0.0, steig + tief, steig)
        return Absatzsatz("", [SatzZeile(box, einzug_links + einzug_erste, 0.0, zeilenhoehe(steig + tief, zeilen_art, zeilen_wert))], [], [])
    verf = max(1.0, breite - einzug_links - einzug_rechts)
    erste_b = max(1.0, verf - einzug_erste)

    def zeilen_ab(start: int, b: float) -> list[LineBox]:
        res = zeilen_umbrechen(text[start:], adv[start:], b, 0.0, 0.0)
        return [LineBox(z.start + start, z.length, z.width, 0.0, 0.0) for z in res]

    def hoehe_von(b: LineBox) -> tuple[float, float]:
        stuecke = hoehen[b.start:b.start + b.length] or hoehen[-1:]
        steig = max(s[0] for s in stuecke)
        return steig, max(max(s[1] - s[0] for s in stuecke) + steig, max(s[1] for s in stuecke))

    # Zeilen als (Zeichenbereich, Versatz links, verfügbare Breite, Lücke davor); ohne ``ausschluss`` mit gleichbleibender Breite
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
        elif ausrichtung == "justify" and not letzte and not zeilentext.endswith(("\n", "\u2028")):
            luecken = sum(1 for c in zeilentext.rstrip(" \t") if c in LEERZEICHEN)
            if luecken:
                extra = max(0.0, (raum - b.width) / luecken)
        h = zeilenhoehe(natuerlich, zeilen_art, zeilen_wert)
        res.append(SatzZeile(LineBox(b.start, b.length, b.width, natuerlich, steig), x, y, h, extra))
        y += h
    if text.endswith(("\n", " ")):                                             # Zeilenumbruch am Ende: eine leere Zeile folgt
        m = hoehen[-1]
        res.append(SatzZeile(LineBox(len(text), 0, 0.0, m[1], m[0]), einzug_links, y, zeilenhoehe(m[1], zeilen_art, zeilen_wert)))
    return Absatzsatz(text, res, adv, info)
