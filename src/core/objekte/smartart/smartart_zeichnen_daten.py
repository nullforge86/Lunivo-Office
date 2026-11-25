"""Smartart zeichnen daten: aus ``vcl.qt.rendering.smartart.smartart_zeichnen`` herausgelöst."""
from __future__ import annotations


_ZU: dict = {"schrift": None, "stil": 1, "rtl": False, "b": 520, "reg": {}, "ids": [], "knoten": [], "hier": "standard", "fmt": [], "fmt_alle": {}}


def _format_von(nr) -> dict | None:
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


def _grundschrift(pt: float):
    """Grundschrift des Dokuments als Beschreibung des Kerns; gesetzt und gezeichnet wird der Text vom Kern, nicht von Qt."""
    from core.layout.drucklayout.formatwerte import STANDARD_FAMILIE
    from core.textsatz import FontSpec
    return FontSpec(STANDARD_FAMILIE, pt, 400, False)


def _gruppen(pts: list[tuple[int, str]]) -> list[tuple[int, str, list[tuple[int, str]]]]:
    """Oberste Ebene als Überschrift, alles Eingerückte darunter als Unterpunkte: [(Nr. der Überschrift, Text, [(Nr., Unterpunkt)])]."""
    out: list[tuple[int, str, list[tuple[int, str]]]] = []
    for i, (e, t) in enumerate(pts):
        if e == 0 or not out:
            out.append((i, t, []))
        else:
            out[-1][2].append((i, t))
    return out


# ---- Organigramm / Hierarchie ---------------------------------------------------------------------------------------------------------
def _baum(pts) -> list[dict]:
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


def _alle(n: dict):
    yield n
    for k in n["k"]:
        yield from _alle(k)
