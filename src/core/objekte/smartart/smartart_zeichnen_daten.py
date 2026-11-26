"""Smartart zeichnen daten: aus ``vcl.qt.rendering.smartart.smartart_zeichnen`` herausgelöst."""
from __future__ import annotations

from core.diagramme.formatierung import schrift_aus

_ZU: dict = {"schrift": None, "knoten": [], "fmt": [], "fmt_alle": {}}


def beginnen(knoten: list, fmt: list, fmt_alle: dict) -> None:
    """Ein neues SmartArt wird gezeichnet: Knoten, ihre Formate und das Format aller Knoten merken, die Schrift zurücksetzen."""
    _ZU.update(schrift=None, knoten=knoten, fmt=fmt, fmt_alle=fmt_alle)


def grundschrift_setzen(pt: float) -> None:
    """Die Schrift des nächsten Textes: die Grundschrift in der Größe ``pt``."""
    _ZU["schrift"] = _grundschrift(pt)


def schrift():
    """Die aktuelle Schrift (ohne Angabe die Grundschrift in 11 pt)."""
    return _ZU["schrift"] or _grundschrift(11.0)


def format_von(nr) -> dict | None:
    """Das Format des Knotens Nummer ``nr`` (Format wie ``teil_format`` des Diagramms): das des Knotens über dem von allen Knoten (``daten["format"]``)."""
    alle = _ZU.get("fmt_alle") or {}
    eigen = _ZU["fmt"][nr] if nr is not None and 0 <= nr < len(_ZU["fmt"]) else None
    if not alle and not eigen:
        return None
    f = {**alle, **(eigen or {})}
    for k in ("linie", "text"):
        if alle.get(k) and (eigen or {}).get(k):
            f[k] = {**alle[k], **eigen[k]}
    return f


def schrift_uebernehmen(t: dict | None) -> None:
    """Die Schrift des Kastens bekommt die Angaben des Textformats ``t`` (Name, Größe, fett, kursiv) über der aktuellen Schrift."""
    _ZU["schrift"] = schrift_aus(_ZU["schrift"] or _grundschrift(11.0), t)


def _grundschrift(pt: float):
    """Grundschrift des Dokuments als Beschreibung des Kerns; gesetzt und gezeichnet wird der Text vom Kern, nicht von Qt."""
    from core.layout.drucklayout.formatwerte import STANDARD_FAMILIE
    from core.textsatz import FontSpec
    return FontSpec(STANDARD_FAMILIE, pt, 400, False)


def gruppen(pts: list[tuple[int, str]]) -> list[tuple[int, str, list[tuple[int, str]]]]:
    """Oberste Ebene als Überschrift, alles Eingerückte darunter als Unterpunkte: [(Nr. der Überschrift, Text, [(Nr., Unterpunkt)])]."""
    out: list[tuple[int, str, list[tuple[int, str]]]] = []
    for i, (e, t) in enumerate(pts):
        if e == 0 or not out:
            out.append((i, t, []))
        else:
            out[-1][2].append((i, t))
    return out


# ---- Organigramm / Hierarchie ---------------------------------------------------------------------------------------------------------
def baum(pts) -> list[dict]:
    """Die Wurzeln des Knotenbaums; jeder Knoten {i (Nr.), t (Text), e (Ebene), k (Kinder), a (Assistent)}."""
    kn = _ZU["knoten"]
    wurzeln: list[dict] = []
    stapel: list[dict] = []
    for i, (e, t) in enumerate(pts):
        n = {"i": i, "t": t, "e": e, "k": [], "a": bool(kn[i].get("assistent")) if i < len(kn) else False}
        while stapel and stapel[-1]["e"] >= e:
            stapel.pop()
        (stapel[-1]["k"] if stapel else wurzeln).append(n)
        stapel.append(n)
    return wurzeln
