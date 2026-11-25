"""Objekte des Dokumentmodells (``InlineObjekt``, ``FreiesObjekt``) über das Rendering-Backend zeichnen, ohne Qt.

``daten`` eines Objekts hat je Art das Wörterbuch-Format, das schon die Bild- und Formwerkzeuge schreiben: die Angabe eines frei
positionierten Bildes (Kasten, Lage: ``zu`` Zuschnitt, ``ellipse``, ``maske``, ``fuell``, ``rand``, ``fx``, ``dreh``, ``flipH``, ``flipV``), ``form`` wie die
Formparameter (``form``, ``fuell``, ``linie``, ``strich``, ``text``, ``adj``, ``punkte``), ``textfeld`` wie der Text des Textfelds (``text``, ``schrift``,
``pt`` …) mit denselben ``fuell``/``rand`` des Bildes. Alle anderen Arten (Diagramm, SmartArt, Formel, Piktogramm, WordArt, Zeichenbereich)
liegen als Bild in ``ressource`` vor.
"""
from __future__ import annotations

import dataclasses
import math

from core.dokument.dokument import Dokument
from core.objekte.anordnung.objekte_hilfen import FillStyle, Shadow, StrokeStyle
from core.objekte.anordnung.image_object import ImageObject
from core.objekte.anordnung.shape_object import ShapeObject
from core.geometrie import Point, Rect
from core.layout.drucklayout.ausgabe.backend import RenderTarget
from core.layout.drucklayout.ausgabe.objekte.objekte import zeichne_bild, zeichne_form, zeichne_platzhalter
from core.layout.drucklayout.ausgabe.backend import Style, rgba
from core.layout.drucklayout.ausgabe.text.textpfad import zeichne_text_kontur
from core.textsatz.engine import FontSpec


def zeichne_objekt(b: RenderTarget, dok: Dokument, art: str, breite: float, hoehe: float, ressource: str, daten: dict, rect: Rect, engine=None) -> None:
    """Ein Objekt in ``rect`` zeichnen. ``engine``: die Textsatz-Engine für den Text in Formen, Textfeldern und WordArt (ohne sie setzt das Backend den Text)."""
    if art == "diagramm" and isinstance(daten.get("diagramm"), dict):            # gelesenes Word-Diagramm: im Kern gezeichnet, ohne Qt
        from core.layout.drucklayout.ausgabe.diagramm.diagrammzeichner import zeichne_diagramm
        zeichne_diagramm(b, rect, daten["diagramm"])
        return
    if art == "gruppe" and daten.get("elemente"):                                  # Gruppe: ihre Teile an ihren Stellen zeichnen (Maßstab der Gruppe auf ``rect``)
        fx = rect.width / breite if breite else 1.0
        fy = rect.height / hoehe if hoehe else 1.0
        eigen = ImageObject.aus_angabe({**daten, "b": breite, "h": hoehe}, None).transform         # Drehung und Spiegelung der ganzen Gruppe
        veraendert = bool(eigen.rotation or eigen.flip_h or eigen.flip_v)
        flaeche = rect
        if veraendert:
            b.push_state(translate=Point(rect.x + rect.width / 2, rect.y + rect.height / 2), rotate=eigen.rotation, flip_h=eigen.flip_h, flip_v=eigen.flip_v)
            flaeche = Rect(-rect.width / 2, -rect.height / 2, rect.width, rect.height)
        for e in daten["elemente"]:
            teil = Rect(flaeche.x + e["x"] * fx, flaeche.y + e["y"] * fy, e["b"] * fx, e["h"] * fy)
            zeichne_objekt(b, dok, e["art"], e["b"], e["h"], e.get("ressource", ""), e.get("angabe") or {}, teil, engine)
        if veraendert:
            b.pop_state()
        return
    bilddaten = dok.ressourcen.get(ressource) if ressource else None
    innen = daten.get("daten") if isinstance(daten.get("daten"), dict) else {}
    angabe = {**{k: v for k, v in daten.items() if k != "daten"}, "b": breite, "h": hoehe}
    fuell_name = (daten.get("fuell") or {}).get("n", "") if isinstance(daten.get("fuell"), dict) else ""
    fuellbild = dok.ressourcen.get(fuell_name) if fuell_name else None
    if art == "form" and innen:
        form = ShapeObject.aus_parametern({**innen, "breite": breite, "hoehe": hoehe})
        form.kind = form.kind.casefold()
        voll = daten.get("fuell")
        if isinstance(voll, dict) and voll:                                          # die volle Füllung (Verlauf, Muster, Bild …) geht der einfachen Farbe vor
            form = dataclasses.replace(form, fill=FillStyle.aus_dict(voll))
        elif isinstance(voll, dict) and "fuell" not in innen:                         # ausdrücklich keine Füllung
            form = dataclasses.replace(form, fill=None)
        rand = daten.get("rand")
        if isinstance(rand, dict) and rand.get("farbe"):                               # Kontur mit Strichart aus der Angabe (Datei); ohne sie gilt die einfache Linie der Form
            form = dataclasses.replace(form, stroke=StrokeStyle(str(rand["farbe"]), float(rand.get("b", 1.0)), str(rand.get("art") or "einfach")))
        eigen = ImageObject.aus_angabe(angabe, None)                                   # Drehung, Spiegelung und Deckkraft stehen in der Angabe des Objekts
        form = dataclasses.replace(form, transform=eigen.transform, opacity=eigen.opacity)
        sch = daten.get("schatten")
        if isinstance(sch, dict):
            form = dataclasses.replace(form, shadow=Shadow(str(sch.get("farbe") or "#000000"), float(sch.get("blur", 4.0)), float(sch.get("dx", 3.0)), float(sch.get("dy", 3.0)),
                                                           float(sch.get("deckkraft", 0.4))))
        text = str(innen.get("text") or "")
        if zeichne_form(b, form, rect, fuellbild, (lambda r: _form_text(b, r, innen, form, engine)) if text.strip() else None):
            return
    elif art == "textfeld" and innen:
        obj = ImageObject.aus_angabe(angabe, None)
        if zeichne_textfeld(b, obj, rect, innen, engine):
            return
    elif art == "wordart" and bilddaten is None and (innen.get("text") or daten.get("text")):
        if zeichne_wordart(b, engine, rect, {**daten, **innen}):
            return
    if bilddaten is not None or art in ("bild", "textfeld", "form"):
        zeichne_bild(b, ImageObject.aus_angabe(angabe, bilddaten), rect, None, fuellbild)
    else:
        zeichne_platzhalter(b, rect)


def _text_setzen(b: RenderTarget, engine, text: str, font, farbe, ausr: str, rect: Rect, valign: str = "top") -> None:
    """Text in ``rect``: Zeilenumbruch und Ausrichtung über die Textsatz-Engine (die Zeilen zeichnet der Textrenderer wie im Fließtext); ohne Engine setzt ihn das Backend."""
    if engine is None:
        b.draw_text_box(text, rect, font, Style(color=farbe), align=ausr, wrap=True, valign=valign)
        return
    from core.textsatz.paragraph import absatz_setzen
    from core.layout.drucklayout.ausgabe.text.textrenderer import zeichne_zeile
    saetze = [absatz_setzen(engine, [(zeile, font, {"color": farbe})] if zeile else [], max(1.0, rect.width), ausr, leer_schrift=font) for zeile in text.split("\n")]
    gesamt = sum(s.hoehe for s in saetze)
    y = rect.y + (0.0 if valign == "top" else max(0.0, (rect.height - gesamt) / 2))
    b.push_state(clip=rect)
    for s in saetze:
        for i, z in enumerate(s.zeilen):
            zeichne_zeile(b, s, i, Rect(rect.x, y + z.y, rect.width, z.hoehe))
        y += s.hoehe
    b.pop_state()


def _absaetze_setzen(b: RenderTarget, engine, absaetze: list, standard, farbe, rect: Rect) -> None:
    """Die Absätze eines Textfelds mit ihren eigenen Schriften, Einzügen, Ausrichtungen und Zeilenabständen setzen und zeichnen."""
    from core.textsatz.paragraph import absatz_setzen
    from core.layout.drucklayout.ausgabe.text.textrenderer import zeichne_zeile
    y = rect.y
    b.push_state(clip=rect)
    for a in absaetze:
        laeufe = []
        for text, f in a["laeufe"]:
            fs = FontSpec(str(f.get("schrift") or standard.family), float(f.get("pt") or standard.size_pt), 700 if f.get("fett") else 400, bool(f.get("kursiv")))
            stil = {"color": rgba(str(f["farbe"])) if f.get("farbe") else farbe}
            if f.get("abstand"):
                stil["sperrung"] = float(f["abstand"])
            laeufe.append((text, fs, stil))
        leer = laeufe[0][1] if laeufe else standard
        art, wert = a.get("zeile") or ("single", 100.0)
        ausr = {"mitte": "center", "rechts": "right", "block": "justify"}.get(a.get("ausr", "links"), "left")
        y += a.get("vor", 0.0)
        s = absatz_setzen(engine, laeufe, max(1.0, rect.width), ausr, a.get("erste", 0.0), a.get("links", 0.0), a.get("rechts", 0.0), art, wert, leer_schrift=leer)
        for i, z in enumerate(s.zeilen):
            zeichne_zeile(b, s, i, Rect(rect.x, y + z.y, rect.width, z.hoehe))
        y += s.hoehe + a.get("nach", 0.0)
    b.pop_state()


_WARP_BOGEN = {"textArchUp": 1, "textArchUpPour": 1, "textCircle": 1, "textCirclePour": 1, "textArcUp": 1, "textArchDown": -1, "textArchDownPour": -1}
_WARP_WELLE = ("textWave1", "textWave2", "textWave4", "textDoubleWave1")


def _wordart_stil(d: dict, breite: float, hoehe: float):
    from core.layout.drucklayout.ausgabe.objekte.objekte import fuellstil
    from core.objekte.anordnung.objekte_hilfen import FillStyle
    voll = FillStyle.aus_dict(d["fuell"]) if isinstance(d.get("fuell"), dict) and d.get("fuell") else FillStyle("farbe", str(d.get("farbe") or "#000000"))
    stil = fuellstil(voll, Rect(0.0, 0.0, breite, hoehe))
    kontur = d.get("kontur") if isinstance(d.get("kontur"), dict) else None
    return Style(color=rgba(str(kontur["farbe"])) if kontur else (0, 0, 0, 255), width=float(kontur.get("b", 1.0)) if kontur else 0, filled=True,
                 fill=stil.fill if stil is not None else None, join="round")


def _zeichne_verformt(b: RenderTarget, engine, rect: Rect, text: str, font, d: dict, warp: str) -> bool:
    """WordArt auf einem Bogen oder einer Welle: jedes Zeichen sitzt an seiner Stelle der Bahn und folgt ihrer Richtung; die Schrift wird so verkleinert, dass alles in ``rect`` passt."""
    import math
    for _ in range(2):
        xs = [engine.measure_text(text[:i], font) for i in range(len(text) + 1)]
        breite = xs[-1] or 1.0
        m = engine.font_metrics(font)
        hoch = m.ascent + m.descent
        pos = []
        if warp in _WARP_BOGEN:
            vorz = _WARP_BOGEN[warp]
            winkel = 5.4 if "ircle" in warp else 2.4
            radius = breite / winkel
            for i in range(len(text)):
                s = (xs[i] + xs[i + 1]) / 2 - breite / 2
                phi = s / radius
                pos.append((radius * math.sin(phi), -vorz * radius * math.cos(phi), math.degrees(phi) * vorz))
        else:
            zyklen = 2.0 if warp in ("textWave4", "textDoubleWave1") else 1.0
            amp = max(0.0, (rect.height - hoch) / 2)
            for i in range(len(text)):
                xm = (xs[i] + xs[i + 1]) / 2
                pos.append((xm - breite / 2, amp * math.sin(2 * math.pi * zyklen * xm / breite), 0.0))
        oben = min(p[1] for p in pos) - m.ascent
        unten = max(p[1] for p in pos) + m.descent
        links = min(p[0] for p in pos) - breite / max(1, len(text))
        rechts = max(p[0] for p in pos) + breite / max(1, len(text))
        faktor = min(1.0, rect.width / max(1.0, rechts - links), rect.height / max(1.0, unten - oben))
        if faktor >= 0.99:
            break
        font = FontSpec(font.family, font.size_pt * faktor, font.weight, font.italic)
    cx, oy = rect.x + rect.width / 2, rect.y - oben + (rect.height - (unten - oben)) / 2
    stil = _wordart_stil(d, breite, hoch)
    for pass_, versatz in ((0, d.get("schatten")), (1, None)):
        if pass_ == 0 and not versatz:
            continue
        sd = max(2.0, font.size_pt / 14) if pass_ == 0 else 0.0
        for i, ch in enumerate(text):
            if not ch.strip():
                continue
            w = xs[i + 1] - xs[i]
            x, y, grad = pos[i]
            b.push_state(translate=Point(cx + x + sd, oy + y + sd), rotate=grad)
            zeichne_text_kontur(b, ch, font, Point(-w / 2, 0.0), Style(color=rgba(str(versatz)), width=0, filled=True) if pass_ == 0 else stil)
            b.pop_state()
    return True


def zeichne_wordart(b: RenderTarget, engine, rect: Rect, d: dict) -> bool:
    """WordArt ohne Bild: der Text als Pfad mit Füllung (Farbe oder Verlauf), Kontur und Schatten, eingepasst in ``rect``. ``d``: ``text``, ``schrift``, ``pt``, ``fett``, ``kursiv``,
    ``fuell`` (Wörterbuch wie bei Formen), ``kontur`` ({"farbe", "b"}), ``schatten`` (Farbe)."""
    if engine is None:
        return False
    from core.layout.drucklayout.ausgabe.objekte.objekte import fuellstil
    from core.objekte.anordnung.objekte_hilfen import FillStyle
    text = str(d.get("text") or "")
    font = FontSpec(str(d.get("schrift") or "Liberation Sans"), float(d.get("pt") or 36.0), 700 if d.get("fett", True) else 400, bool(d.get("kursiv")))
    m = engine.font_metrics(font)
    breite = engine.measure_text(text, font)
    hoehe = m.ascent + m.descent
    faktor = min(rect.width / breite if breite else 1.0, rect.height / hoehe if hoehe else 1.0)           # in die Fläche einpassen (WordArt wird mit dem Rahmen gestreckt)
    if abs(faktor - 1.0) > 0.01:
        font = FontSpec(font.family, font.size_pt * faktor, font.weight, font.italic)
        m = engine.font_metrics(font)
        breite, hoehe = engine.measure_text(text, font), m.ascent + m.descent
    warp = str(d.get("warp") or "")
    if warp in _WARP_BOGEN or warp in _WARP_WELLE:
        return _zeichne_verformt(b, engine, rect, text, font, d, warp)
    b.push_state(translate=Point(rect.x + (rect.width - breite) / 2, rect.y + (rect.height - hoehe) / 2))
    ursprung = Point(0.0, m.ascent)
    if d.get("schatten"):
        versatz = max(2.0, font.size_pt / 14)
        b.push_state(translate=Point(versatz, versatz))
        zeichne_text_kontur(b, text, font, ursprung, Style(color=rgba(str(d["schatten"])), width=0, filled=True))
        b.pop_state()
    voll = FillStyle.aus_dict(d["fuell"]) if isinstance(d.get("fuell"), dict) and d.get("fuell") else FillStyle("farbe", str(d.get("farbe") or "#000000"))
    stil = fuellstil(voll, Rect(0.0, 0.0, breite, hoehe))
    kontur = d.get("kontur") if isinstance(d.get("kontur"), dict) else None
    zeichne_text_kontur(b, text, font, ursprung, Style(color=rgba(str(kontur["farbe"])) if kontur else (0, 0, 0, 255), width=float(kontur.get("b", 1.0)) if kontur else 0, filled=True,
                                                 fill=stil.fill if stil is not None else None, join="round"))
    b.pop_state()
    return True


def _form_text(b: RenderTarget, rect: Rect, innen: dict, form, engine=None) -> None:
    """Der Text einer Form, mittig in ihr; ohne eigene Farbe weiß auf dunkler und schwarz auf heller Füllung."""
    farbe = str(innen.get("farbe") or "")
    if not farbe:
        fl = form.fill
        f = ""
        if fl is not None:                                       # Hintergrund hinter dem Text: bei Mustern der Grund, bei Verläufen die Mitte, sonst die Farbe
            if fl.kind == "muster":
                f = str(fl.params.get("grund") or "#ffffff")
            elif fl.kind in ("graduell", "verlauf"):
                f = "#808080"
            elif fl.kind in ("textur", "bild"):
                f = "#ffffff"
            else:
                f = fl.color or ""
        r, g, bl = (int(f[i:i + 2], 16) for i in (1, 3, 5)) if len(f) == 7 and f.startswith("#") else (255, 255, 255)
        farbe = "#ffffff" if 0.299 * r + 0.587 * g + 0.114 * bl < 140 else "#1f1f1f"
    font = FontSpec(str(innen.get("schrift") or "Liberation Sans"), float(innen.get("pt") or 11.0), 700 if innen.get("fett") else 400, bool(innen.get("kursiv")))
    ziel = Rect(rect.x + 4, rect.y + 2, max(0.0, rect.width - 8), max(0.0, rect.height - 4))
    _text_setzen(b, engine, str(innen["text"]), font, rgba(farbe), "center", ziel, "center")


def zeichne_textfeld(b: RenderTarget, obj: ImageObject, rect: Rect, daten: dict, engine=None) -> bool:
    """Ein Klartextfeld mit einem Format nativ zeichnen; für Runs, Ketten und Effekte bleibt das Bild der Rückfall."""
    if not isinstance(daten.get("text", ""), str) or daten.get("laeufe") or daten.get("von") or daten.get("weiter"):
        return False
    if any(daten.get(k) for k in ("effekt", "kontur", "vorlage", "liste", "einzug", "zeilenabstand", "hervor", "hoch", "tief", "durch")):
        return False
    if daten.get("richtung") not in (None, "", "waagerecht"):
        return False
    from core.layout.drucklayout.ausgabe.objekte.objekte import fuellstil, kontur_stil
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
    reich = daten.get("absaetze")
    if engine is not None and isinstance(reich, list) and reich and "\n".join("".join(t for t, _f in a_["laeufe"]) for a_ in reich) == str(daten.get("text", "")):
        _absaetze_setzen(b, engine, reich, font, style.color, text_rect)
    else:
        _text_setzen(b, engine, daten.get("text", ""), font, style.color, ausrichtung, text_rect, "top")
    b.pop_state()
    return True
