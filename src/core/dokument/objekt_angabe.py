"""Die „Angabe“ eines frei positionierten Objekts: Wörterbuch mit den Schlüsseln ``b``, ``h``, ``bh``, ``xh``, ``ah``, ``bv``, ``yv``, ``av``, ``hinter``, ``n``,
``dreh``, ``fuell``, ``rand``, ``fx`` …, mit der die Bild-, Form- und Layoutfunktionen arbeiten – gebildet aus dem Objekt des Dokumentmodells und zurück."""
from __future__ import annotations

from core.dokument.dokument import UMBRUCH_ARTEN

ANGABE_FELDER = {"b", "h", "bh", "xh", "ah", "bv", "yv", "av", "hinter", "art", "n", "alt", "umbruch"}


def angabe_von(o) -> dict:
    """Die Angabe eines frei positionierten Objekts (``FreiesObjekt``)."""
    d = {k: v for k, v in o.daten.items() if k != "daten"}
    d.update(art=o.art, b=o.breite, h=o.hoehe, bh=o.bezug_h, xh=o.x, ah=o.ausr_h, bv=o.bezug_v, yv=o.y, av=o.ausr_v, hinter=o.umbruch == "hinter",
             n=o.ressource, alt=o.alt_text, umbruch=o.umbruch)
    if isinstance(o.daten.get("daten"), dict):
        d["daten"] = dict(o.daten["daten"])
    return d


def felder_aus_angabe(a: dict) -> dict:
    """Die Felder des ``FreiesObjekt``, die eine (geänderte) Angabe beschreibt, für ``objekt_aendern``."""
    umbruch = a.get("umbruch") if a.get("umbruch") in UMBRUCH_ARTEN and a.get("umbruch") not in ("hinter", "vor") else ("hinter" if a.get("hinter") else "vor")
    daten = {k: v for k, v in a.items() if k not in ANGABE_FELDER and k != "daten" and not k.startswith("_")}
    if a.get("daten"):
        daten["daten"] = dict(a["daten"])
    return {"breite": float(a.get("b", 0.0)), "hoehe": float(a.get("h", 0.0)), "bezug_h": a.get("bh", "spalte"), "x": float(a.get("xh", 0.0)),
            "ausr_h": a.get("ah") or "", "bezug_v": a.get("bv", "absatz"), "y": float(a.get("yv", 0.0)), "ausr_v": a.get("av") or "", "umbruch": umbruch,
            "ressource": a.get("n", ""), "alt_text": a.get("alt", ""), "daten": daten}
