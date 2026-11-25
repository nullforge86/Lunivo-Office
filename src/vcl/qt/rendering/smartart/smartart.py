from __future__ import annotations
import json
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QImage
from writer.funktionen.objekte import smartart as SM
from writer.funktionen.objekte.smartart import aufzaehlung, form_einfuegen, knoten_von, level, text_aus_knoten, verschieben
from writer.funktionen.objekte.smartart import format_mischen as _format_mischen, knoten_index as _index, knotentext as _knotentext


# ---- Daten des gewählten SmartArt (aus dem Editor gelesen, an den Editor zurückgeschrieben) -------------------------------------------------
def _inline_daten(ed) -> dict | None:
    """Daten eines SmartArt, das als Bild im Text sitzt."""
    return ed.inline_daten("smartart")


def daten_der_auswahl(ed) -> dict | None:
    """Daten des gewählten SmartArt: zuerst das freie Objekt, sonst ein älteres Bild im Text."""
    d = ed.frei_daten_lesen("smartart")
    return d if d is not None else _inline_daten(ed)


def einfuegen(ed, daten) -> None:
    """Fügt das SmartArt als freies Objekt ein: Rahmen, Griffe und Schnellleiste wie bei WordArt. ``daten`` = Daten, ein Katalogeintrag oder dessen Schlüssel."""
    ed.frei_einfuegen("smartart", SM.einfuegen_daten(daten))


def knoten_gewaehlt(ed) -> str | None:
    """Id des gewählten Knotens des gewählten SmartArt (freies Objekt) oder None."""
    return SM.knoten_gewaehlt(ed.frei_daten_lesen("smartart"))


def knoten_waehlen(ed, ident) -> bool:
    """Knoten wählen (None: Auswahl aufheben). Das Bild wird nicht neu gezeichnet."""
    if not SM.knoten_waehlbar(ed.frei_daten_lesen("smartart"), ident):
        return False
    return ed.frei_daten_still("smartart", auswahl=ident or None)


def knoten_text(ed, ident) -> str | None:
    """Der Text des Knotens (ohne Aufzählungspunkte) oder None."""
    return SM.knoten_text(daten_der_auswahl(ed), ident)


def format_lesen(ed) -> dict | None:
    """Werte für die Seitenleiste (siehe Framework): Format des gewählten Knotens, ohne Auswahl das von allen Knoten."""
    d = daten_der_auswahl(ed)
    if d is None:
        return None
    return SM.format_lesen({**d, "auswahl": knoten_gewaehlt(ed)})


def kann(ed, was: str, richtung: str = "") -> bool:
    """Ob ein Knotenbefehl gerade geht (zum Ausgrauen); siehe Framework."""
    return SM.kann(daten_der_auswahl(ed), was, richtung)


# ---- Zeichnen: gemeinsamer Zustand, Hilfen ---------------------------------------------------------------------------------------------
def zeichnen_mit_knoten(daten: dict) -> tuple[QImage, dict[str, QRectF]]:
    """Das SmartArt als Bild und dazu die Rechtecke aller Knoten (id → QRectF in Bildpunkten dieses Bildes)."""
    from vcl.qt.rendering.smartart import smartart_zeichnen as zeichner

    kn = knoten_von(daten)
    pts = [(k["ebene"], _knotentext(k)) for k in kn] or [(0, "…")]
    zeichner._ZU.update(schrift=None, stil=int(daten.get("stil", 1)), rtl=bool(daten.get("rtl")), b=520, reg={}, ids=[k["id"] for k in kn], knoten=kn,
               hier=daten.get("hierarchie", "standard"), fmt=[k.get("format") for k in kn], fmt_alle=daten.get("format") or {})
    img = zeichner._ZEICHNER.get(daten.get("layout", "Liste"), zeichner._pyramide)(daten, pts, 520)
    reg, letzt = dict(zeichner._ZU["reg"]), QRectF(0, 0, img.width(), img.height())
    for ident in zeichner._ZU["ids"]:                                                 # jeder Knoten hat ein Rechteck: sonst das des Knotens davor
        letzt = reg.setdefault(ident, letzt)
    return img, reg


def zeichnen(daten: dict) -> QImage:
    return zeichnen_mit_knoten(daten)[0]


def knoten_rechtecke(daten: dict, b: float = 0, h: float = 0) -> dict[str, QRectF]:
    """id → QRectF der Knoten aus dem Zeichnen. Mit ``b``/``h`` (Größe des Objekts auf dem Blatt) umgerechnet in dessen Bildpunkte, sonst in
    Bildpunkten des gezeichneten Bildes."""
    img, reg = zeichnen_mit_knoten(daten)
    if not (b and h):
        return reg
    sx, sy = b / img.width(), h / img.height()
    return {k: QRectF(r.x() * sx, r.y() * sy, r.width() * sx, r.height() * sy) for k, r in reg.items()}


def _inline_aendern(ed, neu: dict) -> bool:
    """Ein SmartArt, das als Bild im Text steht: Daten ändern, neu zeichnen, Breite behalten."""
    d = _inline_daten(ed)
    if d is None:
        return False
    for k, v in neu.items():
        if v is None:
            d.pop(k, None)
        else:
            d[k] = v
    return ed.inline_neu_zeichnen(zeichnen(d), d, alt="SmartArt: " + d.get("layout", "Liste") + " mit " + str(len(knoten_von(d))) + " Punkten")


def aendern(ed, **felder) -> bool:
    """Daten des gewählten SmartArt ändern und neu zeichnen (Breite bleibt, Seitenverhältnis folgt). Ein neuer ``text`` (anders als der zu den
    Knoten gehörende) ersetzt die Knoten; ``knoten=None``, ``auswahl=None``, ``hierarchie=None`` und ``rtl=None`` entfernen die Angabe."""
    from vcl.qt.rendering import formen as FO
    neu = {k: v for k, v in felder.items() if v is not None or k in ("knoten", "auswahl", "hierarchie", "rtl", "format")}
    neu = SM.text_gegen_knoten(daten_der_auswahl(ed), neu)
    if FO.art_gewaehlt(ed) == "smartart":
        return FO.frei_objekt_aendern(ed, "smartart", **neu) if neu else True
    return _inline_aendern(ed, neu)


def _im_objekt(pos, r, a: dict) -> QPointF:
    """``pos`` (Editor) in den Koordinaten des ungedrehten Objekts der Größe ``a["b"]`` x ``a["h"]``; ``r`` ist sein Rechteck im Editor."""
    from PySide6.QtGui import QTransform
    p = QPointF(pos)
    dreh = float(a.get("dreh", 0.0) or 0.0)
    if dreh:
        p = QTransform().translate(r.center().x(), r.center().y()).rotate(-dreh).translate(-r.center().x(), -r.center().y()).map(p)
    return QPointF((p.x() - r.x()) * float(a["b"]) / r.width(), (p.y() - r.y()) * float(a["h"]) / r.height())


def _knoten_rechtecke_gemerkt(ed, d: dict, b: float, h: float) -> dict:
    """``knoten_rechtecke``, gemerkt am Editor, solange Daten (ohne Auswahl) und Größe gleich bleiben."""
    schl = (json.dumps({k: v for k, v in d.items() if k != "auswahl"}, sort_keys=True, default=str), round(b), round(h))
    c = getattr(ed, "_sa_knoten_cache", None)
    if c is None or c[0] != schl:
        c = (schl, knoten_rechtecke(d, b, h)); ed._sa_knoten_cache = c
    return c[1]


def knoten_bei(ed, pos) -> str | None:
    """Die Id des Knotens unter ``pos`` (QPointF im Editor, dieselben Koordinaten wie die Rechtecke von ``ed._frei_liste()``) im gewählten SmartArt;
    Drehung und Zoom sind berücksichtigt. Kein Treffer: None."""
    from vcl.qt.rendering import formen as FO
    z = FO.frei_objekt_ziel(ed)
    if z is None or z[0] != "smartart":
        return None
    _art, d, key, a, _bild_ = z
    r = next((x[3] for x in ed._frei_liste() if x[0] == key), None)
    if r is None or r.width() <= 0 or r.height() <= 0:
        return None
    lp = _im_objekt(pos, r, a)
    rechtecke = _knoten_rechtecke_gemerkt(ed, d, float(a["b"]), float(a["h"]))
    treffer = sorted((rr.width() * rr.height(), k) for k, rr in rechtecke.items() if rr.contains(lp))     # der kleinste Knoten unter dem Punkt
    return treffer[0][1] if treffer else None


def knoten_text_setzen(ed, ident, text: str) -> bool:
    """Den Text eines Knotens setzen (Eintippen im Knoten) und neu zeichnen."""
    d = daten_der_auswahl(ed)
    kn = knoten_von(d) if d else []
    i = _index(kn, ident)
    if i is None:
        return False
    kn[i]["text"] = text.replace("\n", " ")
    return _knoten_schreiben(ed, kn, ident)


def _knoten_schreiben(ed, kn: list[dict], auswahl) -> bool:
    return aendern(ed, knoten=kn, text=text_aus_knoten(kn), auswahl=auswahl)


def format_setzen(ed, **kw) -> bool:
    """Format des gewählten Knotens (ohne Auswahl: aller Knoten) ändern; ``kw`` wie ``teil_format`` des Diagramms (``fuell``, ``linie``, ``schatten`` …, ``text``)."""
    d = daten_der_auswahl(ed)
    if d is None or not (set(kw) & set(SM.format_schluessel())):
        return False
    ident = knoten_gewaehlt(ed)
    kn = knoten_von(d)
    if ident:
        k = kn[_index(kn, ident)]
        fmt = _format_mischen(dict(k.get("format") or {}), kw)
        k.pop("format", None)
        if fmt:
            k["format"] = fmt
        return _knoten_schreiben(ed, kn, ident)
    fmt = _format_mischen(dict(d.get("format") or {}), kw)
    for k in kn:                                                             # „alle Knoten“ gilt: gleiche Angaben einzelner Knoten fallen weg
        eigen = {a: b for a, b in (k.get("format") or {}).items() if a not in kw}
        k.pop("format", None)
        if eigen:
            k["format"] = eigen
    return aendern(ed, format=fmt or None, knoten=kn, text=text_aus_knoten(kn), auswahl=d.get("auswahl"))


def befehl_form(ed, wie: str) -> bool:
    """``smartartFormEinfuegen``: neuen Knoten relativ zum gewählten (``wie`` siehe ``form_einfuegen``); der neue Knoten wird gewählt."""
    d = daten_der_auswahl(ed)
    if d is None:
        return False
    r = form_einfuegen(knoten_von(d), d.get("auswahl"), wie)
    return bool(r) and _knoten_schreiben(ed, r[0], r[1])


def befehl_level(ed, richtung: str) -> bool:
    d = daten_der_auswahl(ed)
    neu = level(knoten_von(d), d.get("auswahl"), richtung) if d else None
    return neu is not None and _knoten_schreiben(ed, neu, d.get("auswahl"))


def befehl_verschieben(ed, richtung: str) -> bool:
    d = daten_der_auswahl(ed)
    neu = verschieben(knoten_von(d), d.get("auswahl"), richtung) if d else None
    return neu is not None and _knoten_schreiben(ed, neu, d.get("auswahl"))


def befehl_aufzaehlung(ed) -> bool:
    d = daten_der_auswahl(ed)
    neu = aufzaehlung(knoten_von(d), d.get("auswahl")) if d else None
    return neu is not None and _knoten_schreiben(ed, neu, d.get("auswahl"))
