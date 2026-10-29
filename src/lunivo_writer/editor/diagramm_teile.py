"""Diagrammteile am gewählten Diagramm (freies Objekt): Auswahl, Treffer beim Mausklick und Formate je Teil. Keine Oberfläche.

Die Auswahl steht in ``a["daten"]["teil"]`` (Schlüssel aus ``diagramm.teile``), die Formate in ``a["daten"]["teil_format"][teil]``:
``{"fuell": "#rrggbb", "linie": {"farbe", "breite", "art"}, "schatten": {"farbe", "abstand"}, "leuchten": {"farbe", "radius"},
"text": {"farbe", "groesse", "fett"}}`` — jeder Schlüssel darf fehlen. Die Mausbedienung (``freie_bilder_bedienung.py``) ruft ``teil_bei`` und
``teil_waehlen`` auf."""
from __future__ import annotations

import json

from PySide6.QtCore import QPointF, QRectF

from lunivo_writer.editor import diagramm as D
from lunivo_writer.editor import diagramm_format as F
from lunivo_writer.editor import frei_objekt as FO

# Angaben, die ``diagramm_teil_format_setzen`` kennt (Aufbau: ``diagramm_format``); die Wörterbücher in ``_ZUSAMMEN`` werden mit den vorhandenen
# Angaben zusammengeführt (Angaben mit dem Wert None fallen dabei heraus). Die Effekte des Diagrammbereichs gehören dem Objekt (``a["fx"]``):
# Schatten und Leuchten außerhalb des Bildes gibt es nur dort.
FORMAT_SCHLUESSEL = ("fuell", "linie", "schatten", "leuchten", "reflektion", "weich", "d3", "drehung", "text", "achse", "reihe")
_ZUSAMMEN = ("linie", "text", "achse", "reihe")
EFFEKTE = ("schatten", "leuchten", "reflektion", "weich", "d3", "drehung")


def teil_gewaehlt(ed) -> str | None:
    """Schlüssel des gewählten Diagrammteils des gewählten Diagramms oder None (auch wenn der Teil inzwischen fehlt)."""
    d = FO.daten_lesen(ed, "diagramm")
    t = d.get("teil") if d else None
    return t if t and t in {k for k, _n in D.teile(d)} else None


def teil_name(ed) -> str:
    """Anzeigename des gewählten Teils (Feld „Diagrammbereich“ in den Diagrammtools); leer, wenn keiner gewählt ist."""
    d = FO.daten_lesen(ed, "diagramm")
    t = teil_gewaehlt(ed)
    return dict(D.teile(d)).get(t, "") if d and t else ""


def teil_waehlen(ed, schluessel: str | None) -> bool:
    """Einen Teil wählen (None: Auswahl aufheben). Das Bild wird nicht neu gezeichnet."""
    d = FO.daten_lesen(ed, "diagramm")
    if d is None:
        return False
    if schluessel and schluessel not in {k for k, _n in D.teile(d)}:
        return False
    return FO.daten_still(ed, "diagramm", teil=schluessel or None)


def _geo(ed, d: dict, b: float, h: float) -> dict:
    """Geometrie der Teile, zwischengemerkt, bis sich Daten oder Größe ändern."""
    schl = (json.dumps({k: v for k, v in d.items() if k != "teil"}, sort_keys=True, default=str), round(b), round(h))
    c = getattr(ed, "_dg_teile_cache", None)
    if c is None or c[0] != schl:
        c = (schl, D.teil_geo(d, b, h))
        ed._dg_teile_cache = c
    return c[1]


def teil_bei(ed, pos) -> str | None:
    """Der Diagrammteil unter ``pos`` (QPointF im Editor, dieselben Koordinaten wie die Rechtecke von ``ed._frei_liste()``) für das gewählte
    Diagramm; Drehung und Zoom sind berücksichtigt. Innerhalb des Diagramms ohne anderen Treffer: ``diagrammbereich``; außerhalb: None."""
    z = FO.ziel(ed)
    if z is None or z[0] != "diagramm":
        return None
    _art, d, key, a, _bild = z
    r = next((x[3] for x in ed._frei_liste() if x[0] == key), None)
    if r is None or r.width() <= 0 or r.height() <= 0:
        return None
    from PySide6.QtGui import QTransform
    p = QPointF(pos)
    dreh = float(a.get("dreh", 0.0) or 0.0)
    if dreh:
        p = QTransform().translate(r.center().x(), r.center().y()).rotate(-dreh).translate(-r.center().x(), -r.center().y()).map(p)
    b, h = float(a["b"]), float(a["h"])
    lp = QPointF((p.x() - r.x()) * b / r.width(), (p.y() - r.y()) * h / r.height())
    if not QRectF(0, 0, b, h).contains(lp):
        return None
    geo = _geo(ed, d, b, h)
    erlaubt = {k for k, _n in D.teile(d)}
    treffer = []
    for k in erlaubt:
        rr = geo.get(k)
        if not isinstance(rr, QRectF):
            continue
        if k.startswith("reihe_") and geo.get("balken_" + k[6:]):                      # Säulen/Balken: nur die einzelnen Balken zählen
            if any(x.contains(lp) for x in geo["balken_" + k[6:]]):
                treffer.append((0.0, k))
        elif rr.contains(lp):
            treffer.append((rr.width() * rr.height(), k))
    return min(treffer)[1] if treffer else "diagrammbereich"


# ---- Formate je Teil -------------------------------------------------------------------------------------------------------------
def diagramm_teil_format_lesen(ed, teil: str | None = None) -> dict:
    """Das Format des gewählten Teils (oder von ``teil``) als Kopie; leer, wenn nichts gesetzt ist oder kein Diagramm gewählt ist. Beim Diagrammbereich
    kommen die Effekte des Objekts (``a["fx"]``) dazu."""
    z = FO.ziel(ed)
    d = FO.daten_lesen(ed, "diagramm")
    if d is None:
        return {}
    t = teil or teil_gewaehlt(ed) or "diagrammbereich"
    fmt = json.loads(json.dumps((d.get("teil_format") or {}).get(t) or {}))
    if t == "diagrammbereich" and z is not None:
        fmt.update({k: v for k, v in json.loads(json.dumps(z[3].get("fx") or {})).items() if k in EFFEKTE})
    return fmt


def _ohne_leer(w: dict) -> dict:
    return {k: v for k, v in w.items() if v is not None}


def diagramm_teil_format_setzen(ed, teil: str | None = None, **kw) -> bool:
    """Format des gewählten Teils (``teil`` nennt einen anderen) ändern und das Diagramm neu zeichnen. ``fuell`` (Farbe, Wörterbuch, ``""`` = keine
    Füllung, None entfernt = Automatisch), ``linie``/``text``/``achse``/``reihe`` (Wörterbuch, wird mit den vorhandenen Angaben zusammengeführt; None
    entfernt alles), ``schatten``/``reflektion``/``leuchten``/``weich``/``d3``/``drehung`` (Wörterbuch, True für die Vorgabe, None/False entfernt).
    Ohne Teil: ``diagrammbereich``; dessen Effekte werden am Objekt gespeichert."""
    d = FO.daten_lesen(ed, "diagramm")
    if d is None or set(kw) - set(FORMAT_SCHLUESSEL):
        return False
    t = teil or teil_gewaehlt(ed) or "diagrammbereich"
    alle = {k: dict(v) for k, v in (d.get("teil_format") or {}).items()}
    fmt = alle.get(t, {})
    obj_fx = None
    if t == "diagrammbereich":                                       # Effekte außerhalb des Bildes: am Objekt
        z = FO.ziel(ed)
        obj_fx = dict(z[3].get("fx") or {}) if z else {}
    geaendert_fx = False
    for k, v in kw.items():
        if obj_fx is not None and k in EFFEKTE:
            geaendert_fx = True
            if v is None or v is False:
                obj_fx.pop(k, None)
            else:
                obj_fx[k] = dict(v) if isinstance(v, dict) else dict(F.fx_normal({k: True})[k])
            continue
        if v is None or v is False:
            fmt.pop(k, None)
        elif k in _ZUSAMMEN and isinstance(v, dict):
            neu = _ohne_leer({**(fmt.get(k) or {}), **v})
            if neu:
                fmt[k] = neu
            else:
                fmt.pop(k, None)
        else:
            fmt[k] = v
    if fmt:
        alle[t] = fmt
    else:
        alle.pop(t, None)
    ok = FO.aendern(ed, "diagramm", teil_format=alle or None)
    if ok and geaendert_fx:
        ok = FO.aendern(ed, "diagramm", form_effekt=obj_fx or None)
    return ok
