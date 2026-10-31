"""Baustein für die Reiterbeschreibungen: ein Knopf als Wörterbuch."""
from __future__ import annotations


def k(symbol, name, tun=None, gross=False, **kw):
    e = {"symbol": symbol, "name": name, "gross": gross}
    if tun:
        e["tun"] = tun
    e.update(kw)
    return e


# Die gemeinsamen Knöpfe der Gruppe „Anordnen“ (Bild-, Zeichen- und SmartArt-Tools): einmal beschrieben (Symbol, Standardname, Befehl, feste Angaben).
_ANORDNEN = {
    "drehen": ("objektdrehen", "Drehen", None, {"klappe": "zeichenDrehen"}),
    "gruppieren": ("gruppieren", "Gruppieren", "gruppieren", {}),
    "ausrichten": ("ausrichten", "Ausrichten", None, {"klappe": "zeichenAusrichten"}),
    "umbruch": ("textflussumbruch", "Textumbruch Stil", "zeichenUmbruch", {}),
    "vorn": ("ebeneHoch", "Eine Ebene nach vorne", "zeichenVorn", {}),
    "hinten": ("ebeneTief", "Eine Ebene nach hinten", "zeichenHinten", {}),
    "auswahlbereich": ("auswahlbereich", "Auswahlbereich", "auswahlbereich", {}),
}


def anordnen_knopf(art: str, name: str | None = None, **kw) -> dict:
    """Ein Knopf der Gruppe „Anordnen“ (``art``: drehen, gruppieren, ausrichten, umbruch, vorn, hinten, auswahlbereich); ``name`` und ``gross``/``text`` je Reiter."""
    symbol, standard, tun, fest = _ANORDNEN[art]
    return k(symbol, name or standard, tun, **{**fest, **kw})


def anordnen_gruppe(*knoepfe: dict) -> dict:
    """Die Gruppe „Anordnen“ der Kontext-Reiter."""
    return {"name": "Anordnen", "reihenfolge": True, "ohne_titel": True, "knoepfe": list(knoepfe)}


def alle(tab: dict) -> dict:
    """Alle Knöpfe eines Reiters aus register.json nach Namen."""
    return {e["name"]: e for g in tab["gruppen"] for e in g.get("knoepfe", []) if e.get("name")}


def uebrige(tab: dict, benutzt: set) -> list:
    """Knöpfe des Reiters, die in der neuen Anordnung noch nicht vorkommen (damit keine Funktion verloren geht)."""
    return [e for g in tab["gruppen"] for e in g.get("knoepfe", [])
            if e.get("name") and e["name"] not in benutzt and not e.get("zeilenumbruch")]
