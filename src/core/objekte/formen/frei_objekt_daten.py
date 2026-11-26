"""Frei objekt daten: aus ``vcl.qt.rendering.formen.frei_objekt`` herausgelöst."""
from __future__ import annotations

from core.dokument import angabe_von

NEU_ZEICHNEN = ("textfeld", "form", "diagramm", "zeichenbereich")                      # Arten, die nach einer Größenänderung in der neuen Größe frisch gezeichnet werden


def form_daten_setzen(d: dict, k: str, v) -> None:
    """Bei einer Form: Farben der Form selbst, kein Kasten ums Bild."""
    if k == "form_fuell":
        d["fuell"] = v or ""
    elif k == "form_linie":
        d["linie"] = v or ""
    else:
        d["strich"] = float(v)


def nach_groesse(neu: dict) -> dict:
    """Nach dem Ziehen der Griffe: Textfeld, Form und Diagramm werden in der neuen Größe frisch gezeichnet; SmartArt skaliert nur."""
    return neu


# ---- Verknüpfte Textfelder -----------------------------------------------------------------------------------------------------
def textfelder(dok) -> list[tuple[tuple, dict]]:
    """Alle freien Textfelder des Dokuments ``dok``: (Schlüssel, Angabe) in Dokumentreihenfolge — frisch aus dem Modell gelesen."""
    return [(("o", oid), angabe_von(o)) for oid, o in dok.objekte.items() if o.art == "textfeld"]


def _kette_ohne(felder: dict, da: dict, verboten: str) -> bool:
    """Von ``da`` die Kette nach oben bis zum Kopf gehen. → False, wenn ein Vorgänger fehlt oder das Feld ``verboten`` darin steht (Kreis)."""
    kopf = da
    while kopf.get("von"):
        nxt = next((x["daten"] for x in felder.values() if x.get("daten", {}).get("id") == kopf["von"]), None)
        if nxt is None or nxt.get("id") == verboten:
            return False
        kopf = nxt
    return True


def verknuepfbar(felder: dict, von_key: tuple, nach_key: tuple):
    """(Daten von ``von``, Daten von ``nach``) als Kopien mit Kennung, wenn die Verknüpfung erlaubt ist; sonst None."""
    import uuid
    if von_key == nach_key or von_key not in felder or nach_key not in felder:
        return None
    da, db = dict(felder[von_key].get("daten", {})), dict(felder[nach_key].get("daten", {}))
    if da.get("weiter") or db.get("von"):
        return None
    if da.get("von") and da["von"] == db.get("id"):                 # b ist der Vorgänger von a: Kreis
        return None
    da.setdefault("id", uuid.uuid4().hex[:8]); db.setdefault("id", uuid.uuid4().hex[:8])
    return (da, db) if _kette_ohne(felder, da, db["id"]) else None  # a mitten in einer Kette: Kreis ausschließen


def ist_verknuepft(dok, key: tuple) -> bool:
    d = dict(textfelder(dok)).get(key, {}).get("daten", {})
    return bool(d.get("weiter") or d.get("von"))


def hat_nachfolger(dok, key: tuple) -> bool:
    """Fließt der Text des Textfelds ``key`` in ein nächstes Feld weiter?"""
    return bool(dict(textfelder(dok)).get(key, {}).get("daten", {}).get("weiter"))


def kette_glieder(k, a, nach_id: dict) -> list:
    """Alle Felder einer Kette ab ``(k, a)`` in Reihenfolge."""
    kette = [(k, a)]
    nxt = a.get("daten", {})
    while nxt.get("weiter") and nxt["weiter"] in nach_id:
        kette.append(nach_id[nxt["weiter"]]); nxt = kette[-1][1].get("daten", {})
    return kette
