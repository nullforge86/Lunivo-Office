"""Freiform: die Punkte einer Form (Zeichentools ▸ Form bearbeiten ▸ Punkte bearbeiten). Keine Oberfläche.

Eine Form bleibt ein freies Objekt der Art ``form`` (``editor/frei_objekt.py``); bei der Freiform trägt ihre Angabe ``daten["punkte"]`` den
Pfad als Liste von Elementen ``[typ, x, y]`` (x, y als Anteil 0..1 des Zeichenrechtecks der Form, also unabhängig von der Größe):

    0 ``M`` Anfang eines Teilpfads · 1 ``L`` Gerade bis hierher · 2 ``C`` erster Kurven-Steuerpunkt · 3 ``D`` zweiter Steuerpunkt, danach der
    Endpunkt der Kurve (wie die Elemente eines ``QPainterPath``) · 4 ``Z`` Teilpfad schließen (x, y ohne Bedeutung).

``daten["form"]`` heißt dann ``"Freiform"``. Gezeichnet wird im selben Zeichner wie alle Formen (``einfuegen.form_bild(…, punkte=)``).
Punkte (Knoten) sind M, L und das Kurvenende; Steuerpunkte liegen davor. Alle Funktionen liefern neue Listen und ändern nichts."""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPainterPath

M, L, C, D, Z = 0, 1, 2, 3, 4
NAME = "Freiform"


def innen(daten: dict, b: float, h: float) -> QRectF:
    """Das Zeichenrechteck der Form im Bild von b × h Bildpunkten (wie in ``einfuegen.form_bild``)."""
    s = float(daten.get("strich", 2.0) or 0.0)
    return QRectF(s, s, max(1.0, b - 2 * s), max(1.0, h - 2 * s))


# ---- Umwandeln -------------------------------------------------------------------------------------------------------------------
def aus_pfad(pfad: QPainterPath, r: QRectF) -> list[list]:
    """Die Elemente des Pfads, auf das Rechteck ``r`` bezogen (Anteil 0..1). Ein Teilpfad, der zum Anfang zurückkehrt, wird mit ``Z`` geschlossen."""
    w, h = max(1e-9, r.width()), max(1e-9, r.height())
    roh = []
    for i in range(pfad.elementCount()):
        e = pfad.elementAt(i)
        roh.append([int(e.type.value) if hasattr(e.type, "value") else int(e.type), (e.x - r.left()) / w, (e.y - r.top()) / h])
    out: list[list] = []
    teil: list[list] = []

    def abschliessen():
        if len(teil) >= 3:
            a, z = teil[0], teil[-1]
            if z[0] in (L, D) and abs(z[1] - a[1]) < 1e-6 and abs(z[2] - a[2]) < 1e-6:
                if z[0] == L:
                    teil[-1] = [Z, 0.0, 0.0]
                else:
                    teil.append([Z, 0.0, 0.0])
        out.extend(teil)
        teil.clear()
    for e in roh:
        if e[0] == M:
            abschliessen()
        teil.append(e)
    abschliessen()
    return out


def aus_form(daten: dict, b: float, h: float) -> list[list]:
    """Die Punktliste der gewählten Form in ihrer Größe (Pfeilspitzen der Linien werden zu eigenen Teilpfaden)."""
    from lunivo_writer.editor import formen_katalog as K
    r = innen(daten, b, h)
    name = daten.get("form", "Rechteck")
    if daten.get("punkte"):
        return [list(e) for e in daten["punkte"]]
    if K.hat(name):
        p = K.pfad(name, r, daten.get("adj"))
    else:
        p = QPainterPath(); p.addRect(r)
    return aus_pfad(p, r)


def pfad(punkte: list, r: QRectF) -> QPainterPath:
    """Der Pfad der Punktliste im Rechteck ``r``."""
    p = QPainterPath()

    def pt(e):
        return QPointF(r.left() + e[1] * r.width(), r.top() + e[2] * r.height())
    i = 0
    while i < len(punkte):
        e = punkte[i]
        if e[0] == M:
            p.moveTo(pt(e))
        elif e[0] == L:
            p.lineTo(pt(e))
        elif e[0] == C and i + 2 < len(punkte):
            p.cubicTo(pt(punkte[i]), pt(punkte[i + 1]), pt(punkte[i + 2])); i += 2
        elif e[0] == Z:
            p.closeSubpath()
        i += 1
    return p


def geschlossen(punkte: list) -> bool:
    """Gibt es einen geschlossenen Teilpfad (dann wird gefüllt, sonst nur die Linie gezeichnet)?"""
    return any(e[0] == Z for e in punkte)


# ---- Rollen der Elemente ---------------------------------------------------------------------------------------------------------
def rollen(punkte: list) -> list[str]:
    """Je Element: ``"knoten"`` (Punkt), ``"steuer"`` (Kurven-Steuerpunkt) oder ``"zu"`` (Schließen)."""
    out, i = [], 0
    while i < len(punkte):
        t = punkte[i][0]
        if t == C and i + 2 < len(punkte):
            out += ["steuer", "steuer", "knoten"]; i += 3
            continue
        out.append("zu" if t == Z else "knoten")
        i += 1
    return out


def knoten(punkte: list) -> list[int]:
    return [i for i, r in enumerate(rollen(punkte)) if r == "knoten"]


def _teil(punkte: list, i: int) -> tuple[int, int]:
    """Anfang und Ende (einschließlich) des Teilpfads, zu dem Element ``i`` gehört."""
    a = i
    while a > 0 and punkte[a][0] != M:
        a -= 1
    z = i
    while z + 1 < len(punkte) and punkte[z + 1][0] != M:
        z += 1
    return a, z


# ---- Bearbeiten ------------------------------------------------------------------------------------------------------------------
def verschieben(punkte: list, i: int, x: float, y: float) -> list[list]:
    """Element ``i`` an (x, y) setzen; ein Punkt nimmt seine Steuerpunkte mit."""
    neu = [list(e) for e in punkte]
    rl = rollen(neu)
    if not (0 <= i < len(neu)) or rl[i] == "zu":
        return neu
    dx, dy = x - neu[i][1], y - neu[i][2]
    neu[i][1], neu[i][2] = x, y
    if rl[i] == "knoten":
        if i >= 1 and rl[i - 1] == "steuer" and neu[i][0] == D:                    # Kurvenende: der zweite Steuerpunkt davor
            neu[i - 1][1] += dx; neu[i - 1][2] += dy
        if i + 1 < len(neu) and neu[i + 1][0] == C:                                   # der erste Steuerpunkt der folgenden Kurve
            neu[i + 1][1] += dx; neu[i + 1][2] += dy
    return neu


def loeschen(punkte: list, i: int) -> list[list] | None:
    """Punkt ``i`` entfernen (die Nachbarn verbinden sich); None, wenn es kein Punkt ist oder der Teilpfad zu klein würde
    (mindestens 2 Punkte offen, 3 geschlossen)."""
    rl = rollen(punkte)
    if not (0 <= i < len(punkte)) or rl[i] != "knoten":
        return None
    a, z = _teil(punkte, i)
    zu = punkte[z][0] == Z
    anzahl = sum(1 for k in range(a, z + 1) if rl[k] == "knoten")
    if anzahl <= (3 if zu else 2):
        return None
    neu = [list(e) for e in punkte]
    if punkte[i][0] == M:                                                                # der Anfang: der nächste Punkt wird Anfang
        n = i + 1
        if neu[n][0] == C:
            neu[i:n + 3] = [[M, neu[n + 2][1], neu[n + 2][2]]]
        else:
            neu[i:n + 1] = [[M, neu[n][1], neu[n][2]]]
    elif punkte[i][0] == D:                                                              # Kurvenende samt Steuerpunkten
        del neu[i - 2:i + 1]
    else:
        del neu[i]
    return neu


def _kubisch(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def _kanten(punkte: list):
    """Alle Kanten als (Index des Elements, Art, Stützpunkte): Art ``"L"`` (p0, p1), ``"C"`` (p0, c1, c2, p1) oder ``"Z"`` (letzter Punkt → Anfang)."""
    start = akt = None
    i = 0
    while i < len(punkte):
        e = punkte[i]
        if e[0] == M:
            start = akt = (e[1], e[2])
        elif e[0] == L and akt is not None:
            yield i, "L", (akt, (e[1], e[2])); akt = (e[1], e[2])
        elif e[0] == C and i + 2 < len(punkte):
            p1 = (punkte[i + 2][1], punkte[i + 2][2])
            yield i, "C", (akt, (e[1], e[2]), (punkte[i + 1][1], punkte[i + 1][2]), p1); akt = p1; i += 2
        elif e[0] == Z and akt is not None and start is not None and akt != start:
            yield i, "Z", (akt, start); akt = start
        i += 1


def naechste_kante(punkte: list, x: float, y: float, b: float, h: float):
    """Die Kante, die (x, y) (Anteile) am nächsten liegt: (Abstand in Bildpunkten b × h, Index, Art, Stützpunkte, t) oder None."""
    best = None
    for i, art, pts in _kanten(punkte):
        for s in range(41):
            t = s / 40
            if art == "C":
                q = _kubisch(*pts, t)
            else:
                q = (pts[0][0] + (pts[1][0] - pts[0][0]) * t, pts[0][1] + (pts[1][1] - pts[0][1]) * t)
            d = math.hypot((q[0] - x) * b, (q[1] - y) * h)
            if best is None or d < best[0]:
                best = (d, i, art, pts, t)
    return best


def einfuegen(punkte: list, x: float, y: float, b: float, h: float, toleranz: float = 6.0) -> tuple[list[list], int] | None:
    """Einen Punkt auf der nächsten Kante einfügen (bei einer Kurve wird sie dort geteilt, ihre Form bleibt). → (neue Liste, Index des
    neuen Punkts) oder None, wenn keine Kante näher als ``toleranz`` Bildpunkte liegt."""
    k = naechste_kante(punkte, x, y, b, h)
    if k is None or k[0] > toleranz:
        return None
    _d, i, art, pts, t = k
    neu = [list(e) for e in punkte]
    if art == "C":
        p0, c1, c2, p1 = pts
        a = [(p0[j] + (c1[j] - p0[j]) * t) for j in (0, 1)]
        bb = [(c1[j] + (c2[j] - c1[j]) * t) for j in (0, 1)]
        cc = [(c2[j] + (p1[j] - c2[j]) * t) for j in (0, 1)]
        ab = [(a[j] + (bb[j] - a[j]) * t) for j in (0, 1)]
        bc = [(bb[j] + (cc[j] - bb[j]) * t) for j in (0, 1)]
        m = [(ab[j] + (bc[j] - ab[j]) * t) for j in (0, 1)]
        neu[i:i + 3] = [[C, a[0], a[1]], [D, ab[0], ab[1]], [D, m[0], m[1]], [C, bc[0], bc[1]], [D, cc[0], cc[1]], [D, p1[0], p1[1]]]
        return neu, i + 2
    px = pts[0][0] + (pts[1][0] - pts[0][0]) * t
    py = pts[0][1] + (pts[1][1] - pts[0][1]) * t
    neu.insert(i, [L, px, py])
    return neu, i
