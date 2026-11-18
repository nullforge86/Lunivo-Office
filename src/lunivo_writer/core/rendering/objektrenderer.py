"""Objekte des Dokumentmodells (``InlineObjekt``, ``FreiesObjekt``) über das Rendering-Backend zeichnen, ohne Qt.

``daten`` eines Objekts hat je Art das Wörterbuch-Format, das schon die Bild- und Formwerkzeuge schreiben: die Angabe eines frei
positionierten Bildes (Kasten, Lage: ``zu`` Zuschnitt, ``ellipse``, ``maske``, ``fuell``, ``rand``, ``fx``, ``dreh``, ``flipH``, ``flipV``), ``form`` wie die
Formparameter (``form``, ``fuell``, ``linie``, ``strich``, ``text``, ``adj``, ``punkte``), ``textfeld`` wie der Text des Textfelds (``text``, ``schrift``,
``pt`` …) mit denselben ``fuell``/``rand`` des Bildes. Alle anderen Arten (Diagramm, SmartArt, Formel, Piktogramm, WordArt, Zeichenbereich)
liegen als Bild in ``ressource`` vor.
"""
from __future__ import annotations

from ..document.dokument import Dokument
from ..document.objekte import ImageObject, ShapeObject
from ..geometry import Point, Rect
from .backend import RenderTarget
from .objekte import zeichne_bild, zeichne_form, zeichne_platzhalter
from .backend import Style, rgba
from ..textlayout.engine import FontSpec


def zeichne_objekt(b: RenderTarget, dok: Dokument, art: str, breite: float, hoehe: float, ressource: str, daten: dict, rect: Rect) -> None:
    """Ein Objekt in ``rect`` zeichnen."""
    if art == "diagramm" and isinstance(daten.get("diagramm"), dict):            # gelesenes Word-Diagramm: im Kern gezeichnet, ohne Qt
        from .diagrammzeichner import zeichne_diagramm
        zeichne_diagramm(b, rect, daten["diagramm"])
        return
    bilddaten = dok.ressourcen.get(ressource) if ressource else None
    innen = daten.get("daten") if isinstance(daten.get("daten"), dict) else {}
    angabe = {**{k: v for k, v in daten.items() if k != "daten"}, "b": breite, "h": hoehe}
    fuell_name = (daten.get("fuell") or {}).get("n", "") if isinstance(daten.get("fuell"), dict) else ""
    fuellbild = dok.ressourcen.get(fuell_name) if fuell_name else None
    if art == "form" and innen:
        form = ShapeObject.aus_parametern({**innen, "breite": breite, "hoehe": hoehe})
        form.kind = form.kind.casefold()
        if zeichne_form(b, form, rect):
            return
    elif art == "textfeld" and innen:
        obj = ImageObject.aus_angabe(angabe, None)
        if zeichne_textfeld(b, obj, rect, innen):
            return
    if bilddaten is not None or art in ("bild", "textfeld", "form"):
        zeichne_bild(b, ImageObject.aus_angabe(angabe, bilddaten), rect, None, fuellbild)
    else:
        zeichne_platzhalter(b, rect)


def zeichne_textfeld(b: RenderTarget, obj: ImageObject, rect: Rect, daten: dict) -> bool:
    """Ein Klartextfeld mit einem Format nativ zeichnen; für Runs, Ketten und Effekte bleibt das Bild der Rückfall."""
    if not isinstance(daten.get("text", ""), str) or daten.get("laeufe") or daten.get("von") or daten.get("weiter"):
        return False
    if any(daten.get(k) for k in ("effekt", "kontur", "vorlage", "liste", "einzug", "zeilenabstand", "hervor", "hoch", "tief", "durch")):
        return False
    if daten.get("richtung") not in (None, "", "waagerecht"):
        return False
    from .objekte import fuellstil, kontur_stil
    font = FontSpec(str(daten.get("schrift") or "Liberation Sans"), float(daten.get("pt") or 11.0), 700 if daten.get("fett") else 400, bool(daten.get("kursiv")))
    style = Style(color=rgba(str(daten.get("farbe") or "#1f1f1f")))
    ausrichtung = {"mitte": "center", "rechts": "right", "block": "justify", "verteilt": "justify"}.get(str(daten.get("ausr") or "links"), "left")
    innen = daten.get("innen")
    try:
        li, ob, re, un = (max(0.0, float(v)) for v in innen) if isinstance(innen, (list, tuple)) and len(innen) == 4 else (0.0, 0.0, 0.0, 0.0)
    except (TypeError, ValueError):
        li = ob = re = un = 0.0

    transform = obj.transform
    veraendert = bool(transform.rotation or transform.flip_h or transform.flip_v)
    b.push_state(opacity=obj.opacity, translate=Point(rect.x + rect.width / 2, rect.y + rect.height / 2) if veraendert else None,
                 rotate=transform.rotation, antialias=True, flip_h=transform.flip_h, flip_v=transform.flip_v)
    ziel = Rect(-rect.width / 2, -rect.height / 2, rect.width, rect.height) if veraendert else rect
    if obj.fill:
        fuellung = fuellstil(obj.fill, ziel)
        if fuellung is not None:
            b.draw_rect(ziel, fuellung)
    if obj.stroke:
        b.draw_rect(ziel, kontur_stil(obj.stroke))
    text_rect = Rect(ziel.x + li, ziel.y + ob, max(0.0, ziel.width - li - re), max(0.0, ziel.height - ob - un))
    b.draw_text_box(daten.get("text", ""), text_rect, font, style, align=ausrichtung, wrap=True, valign="top")
    b.pop_state()
    return True
