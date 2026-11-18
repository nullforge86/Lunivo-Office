"""Das Fenster „Layout“ (oberflaeche/baukasten/dokument/layout_dialog.py) mit einem Bild verbinden: Werte vom Bild lesen, die Wahl auf das Bild anwenden.

Zwei Arten von Bildern gibt es im Dokument:

* **frei** — ein frei positioniertes Objekt (``FreiesObjekt``): liegt an einer Stelle des Blattes, hinter oder vor dem Text oder vom Text umflossen.
  Sein Layout sind Lage, Größe, Drehung, Umbruchart und Schicht.
* **im Text** — ein Objekt im Text (``InlineObjekt``), das wie ein Zeichen in der Zeile steht.

Die Umbruchart wechselt zwischen beiden: „In Zeile mit Text“ setzt ein Bild in den Text, jede andere Art macht es frei. Der Baustein selbst kennt davon nichts;
diese Datei ist die einzige Stelle, die Werte und Bild kennt. Gelesen und geschrieben wird über den ``KernEditor`` (``kern_objekte.py``); das Ziel ``z``
liefert ``ed.objekt_ziel()``: ``("frei", ("o", Id), Angabe, Bild)`` oder ``("text", InlineObjekt)``.
"""
from __future__ import annotations

from PySide6.QtGui import QImage

from lunivo_writer.core.geometry import mm_to_px, px_to_mm
from lunivo_writer.editor.objekte import freie_bilder as FB
from lunivo_writer.kern.farben import Farbe

# Vorgabewerte des Fensters „Layout“ (oberflaeche/baukasten/dokument/layout_dialog.py) – hier, damit der Editor nichts aus der Oberfläche braucht
STANDARD = {
    "umbruch": "textfluss", "zeilen": "beide", "abstand": {"oben": 0.0, "unten": 0.0, "links": 3.4, "rechts": 3.4},
    "h": {"modus": "abs", "ausr": "links", "buch": "innen", "bezug_ausr": "spalte", "bezug_buch": "rand", "mm": 0.0, "bezug_abs": "spalte",
          "proz": 0.0, "bezug_rel": "seite"},
    "v": {"modus": "abs", "ausr": "oben", "bezug_ausr": "seite", "mm": 0.0, "bezug_abs": "absatz", "proz": 0.0, "bezug_rel": "seite"},
    "mit_text": False, "ueberlappen": True, "verankern": False,
    "breite": {"modus": "abs", "mm": 40.0, "proz": 0.0, "bezug": "seite"}, "hoehe": {"modus": "abs", "mm": 40.0, "proz": 0.0, "bezug": "seite"},
    "drehung": 0.0, "sperren": False, "skal_original": True, "original": (40.0, 40.0),
}

AUSR_H = {"left": "links", "center": "zentriert", "right": "rechts"}
AUSR_V = {"top": "oben", "center": "zentriert", "bottom": "unten"}
UMGEKEHRT_H = {v: k for k, v in AUSR_H.items()}
UMGEKEHRT_V = {v: k for k, v in AUSR_V.items()}
# Umbruchart des Fensters ↔ Umbruchart des Modells
UMBRUCH_MODELL = {"quadrat": "quadrat", "passend": "eng", "transparent": "durch", "obenunten": "oben_unten", "hinter": "hinter", "vor": "vor"}
UMBRUCH_FENSTER = {v: k for k, v in UMBRUCH_MODELL.items()}


# ---- Ziel: das markierte Bild ---------------------------------------------------------------------------------------------
def ziel(ed):
    """(„frei“, Schlüssel, Angabe, Bild) oder („text“, Objekt) für das markierte Bild; sonst None."""
    return ed.objekt_ziel()


# ---- Lesen -----------------------------------------------------------------------------------------------------------------
def _achse_lesen(a: dict, waagerecht: bool) -> dict:
    ausr, off = a.get("ah" if waagerecht else "av") or "", float(a.get("xh" if waagerecht else "yv", 0.0))
    bezug = a.get("bh" if waagerecht else "bv", "spalte" if waagerecht else "absatz")
    w = {"modus": "abs", "mm": px_to_mm(off), "bezug_abs": bezug}
    if waagerecht and ausr in ("inside", "outside"):
        w.update(modus="buch", buch="innen" if ausr == "inside" else "aussen", bezug_buch="rand" if bezug == "rand" else "seite")
    elif ausr:
        w.update(modus="ausr", ausr=(AUSR_H if waagerecht else AUSR_V).get(ausr, "links"), bezug_ausr=bezug)
    return w


def verschieben_wahl(a: dict) -> str | None:
    """Vorwahl der Radios „Mit Text verschieben“ / „Fester Text“ im Popup Layoutoptionen eines freien Objekts: ``"mit_text"``, ``"fest"`` oder
    None (keins gewählt: SmartArt). Eine Form ohne gespeicherte Angabe steht auf „Mit Text verschieben“ (wie in der Vorlage)."""
    if a.get("art") == "smartart":
        return None
    if a.get("art") in ("form", "gruppe") and "mit_text" not in a:
        return "mit_text"
    return "mit_text" if a.get("mit_text") else "fest"


def lesen(ed, z) -> dict:
    import copy
    w = copy.deepcopy(STANDARD)
    if z[0] == "frei":
        _k, key, a, bild = z
        w["umbruch"] = UMBRUCH_FENSTER.get(a.get("umbruch") or ("hinter" if a.get("hinter") else "vor"), "vor")
        if w["umbruch"] in ("quadrat", "passend", "transparent"):
            w["zeilen"] = "links" if a.get("ah") == "right" else "rechts" if a.get("ah") == "left" else "beide"
        w["h"].update(_achse_lesen(a, True)); w["v"].update(_achse_lesen(a, False))
        w["breite"].update(modus="abs", mm=px_to_mm(a["b"])); w["hoehe"].update(modus="abs", mm=px_to_mm(a["h"]))
        w["drehung"] = float(a.get("dreh", 0.0))
        if a.get("abstand"):
            w["abstand"] = dict(a["abstand"])
        w["mit_text"], w["ueberlappen"], w["verankern"] = bool(a.get("mit_text", False)), bool(a.get("ueberlappen", True)), bool(a.get("verankern", False))
        w["verschieben_wahl"] = verschieben_wahl(a)
        if bild is not None and not bild.isNull():
            w["original"] = (px_to_mm(bild.width()), px_to_mm(bild.height()))
        return w
    o = z[1]
    img = ed.bild_ressource(o.ressource)
    ob, oh = (img.width(), img.height()) if img is not None and not img.isNull() else (o.breite or 100, o.hoehe or 100)
    w["breite"].update(mm=px_to_mm(o.breite or ob)); w["hoehe"].update(mm=px_to_mm(o.hoehe or oh)); w["original"] = (px_to_mm(ob), px_to_mm(oh))
    return w


# ---- Anwenden --------------------------------------------------------------------------------------------------------------
def _box(page, bezug: str, waagerecht: bool) -> float:
    if bezug == "seite":
        return mm_to_px(page.width_mm if waagerecht else page.height_mm)
    return page.content_width_px if waagerecht else page.content_height_px


def _achse_schreiben(a: dict, w: dict, page, waagerecht: bool) -> None:
    ak, ok_ = ("ah", "xh") if waagerecht else ("av", "yv")
    bk = "bh" if waagerecht else "bv"
    if w["modus"] == "ausr":
        a[ak] = (UMGEKEHRT_H if waagerecht else UMGEKEHRT_V).get(w["ausr"], ""); a[ok_] = 0.0; a[bk] = w["bezug_ausr"]
    elif w["modus"] == "buch":
        a[ak] = "inside" if w.get("buch") == "innen" else "outside"; a[ok_] = 0.0; a[bk] = w.get("bezug_buch", "rand")
    elif w["modus"] == "rel":
        a[ak] = ""; a[bk] = w["bezug_rel"]; a[ok_] = _box(page, w["bezug_rel"], waagerecht) * w["proz"] / 100.0
    else:
        a[ak] = ""; a[ok_] = mm_to_px(w["mm"]); a[bk] = w["bezug_abs"]


def _mass(w: dict, page, waagerecht: bool, alt: float) -> float:
    if w["modus"] == "rel":
        return _box(page, w["bezug"], waagerecht) * w["proz"] / 100.0
    return mm_to_px(w["mm"]) if w["mm"] > 0 else alt


def anwenden(ed, z, werte: dict) -> None:
    """Schreibt die Wahl des Fensters (oder eines Teils davon: nur die genannten Schlüssel) auf das Bild."""
    alt = lesen(ed, z)
    w = dict(alt)
    for k, v in werte.items():
        w[k] = {**alt[k], **v} if isinstance(v, dict) and isinstance(alt.get(k), dict) else v
    art = w["umbruch"]
    if z[0] == "frei":
        _k, key, a, bild = z
        if art == "textfluss":                                    # frei → in den Text zurück (am Anfang seines Absatzes)
            ed.objekt_umbruch("textfluss")
            return
        neu = dict(a)
        neu["umbruch"] = UMBRUCH_MODELL.get(art, "vor")
        neu["hinter"] = art == "hinter"
        _achse_schreiben(neu, w["h"], ed.page, True); _achse_schreiben(neu, w["v"], ed.page, False)
        if art in ("quadrat", "passend", "transparent") and w["zeilen"] in ("links", "rechts"):      # der Text läuft auf der anderen Seite des Bildes
            neu["ah"], neu["bh"] = ("right" if w["zeilen"] == "links" else "left"), "spalte"
        neu["b"] = _mass(w["breite"], ed.page, True, a["b"]); neu["h"] = _mass(w["hoehe"], ed.page, False, a["h"])
        neu["dreh"] = float(w["drehung"])
        neu["abstand"] = dict(w["abstand"])                        # Abstand zum Text (mm), gilt beim Umbruch im Text
        neu["mit_text"], neu["ueberlappen"], neu["verankern"] = bool(w["mit_text"]), bool(w["ueberlappen"]), bool(w["verankern"])
        _speichern_frei(ed, key, neu)
        return
    o = z[1]
    if art == "textfluss":
        ed.inline_aendern(o.id, breite=mm_to_px(w["breite"]["mm"]), hoehe=mm_to_px(w["hoehe"]["mm"]))
        return
    # im Text → frei: das Objekt verlässt die Zeile und liegt, wo der Absatz beginnt
    if not ed.objekt_umbruch(UMBRUCH_MODELL.get(art, "vor")):
        return
    neu_z = ed.objekt_ziel()
    if neu_z is None or neu_z[0] != "frei":
        return
    a = dict(neu_z[2])
    a["hinter"] = art == "hinter"
    a["b"], a["h"] = mm_to_px(w["breite"]["mm"]), mm_to_px(w["hoehe"]["mm"])
    a["bh"], a["xh"], a["bv"], a["yv"], a["ah"], a["av"] = "spalte", 0.0, "absatz", 0.0, "", ""
    _achse_schreiben(a, w["h"], ed.page, True); _achse_schreiben(a, w["v"], ed.page, False)
    if art in ("quadrat", "passend", "transparent"):
        a["ah"], a["bh"] = ("right" if w["zeilen"] == "links" else "left"), "spalte"
    a["dreh"] = float(w["drehung"])
    a["abstand"] = dict(w["abstand"])
    _speichern_frei(ed, ("o", o.id), a)


def _speichern_frei(ed, key, neu: dict) -> None:
    ed.angabe_speichern(key[1], FB.ohne_hilfsangaben(neu))


# ---- Füllung und Kontur ---------------------------------------------------------------------------------------------------
FX_SCHLUESSEL = ("schatten", "reflektion", "leuchten", "weich", "d3", "drehung")


def format_lesen(ed, z) -> dict | None:
    """Füllung, Kontur und Effekte des markierten freien Bildes im Format des Panels (``ObjektFormatPanel``); sonst None."""
    if z is None or z[0] != "frei":
        return None
    a = z[2]
    w = {"fuell": a.get("fuell"), "rand": a.get("rand")}
    w.update({k: dict(v) for k, v in (a.get("fx") or {}).items() if k in FX_SCHLUESSEL})
    return w


def fx_alle(ed, fx: dict) -> int:
    """Seitenlayout ▸ Effekte: dieselben Effekte an alle frei liegenden Bilder und Formen des Dokuments (``{}`` nimmt sie weg). → Anzahl."""
    n = 0
    with ed.sitzung.gruppe("Effekte"):
        for key, a, bild, _r, _hinten, _blatt in list(ed._frei_liste()):
            n += format_setzen(ed, ("frei", key, a, bild), fx=dict(fx))
    return n


def format_aus_panel(ed, z, werte: dict) -> bool:
    """Wendet die Werte des Panels an: Füllung, Kontur und alle Effekte (fehlende Effekte sind ausgeschaltet)."""
    if z is None or z[0] != "frei":
        return False
    fuell = werte.get("fuell")
    if fuell and fuell.get("art") == "bild" and fuell.get("unveraendert"):
        fuell = (z[2].get("fuell") if (z[2].get("fuell") or {}).get("art") == "bild" else "__nicht__")       # das vorhandene Bild behalten
    return format_setzen(ed, z, fuell=fuell, rand=werte.get("rand"), fx={k: v for k, v in werte.items() if k in FX_SCHLUESSEL})


def format_setzen(ed, z, fuell="__nicht__", rand="__nicht__", rand_teil: dict | None = None, fx="__nicht__") -> bool:
    """Füllung (``fuell``: Wörterbuch oder None) und/oder Kontur (``rand``: Wörterbuch oder None; ``rand_teil`` ändert nur einzelne Angaben der
    vorhandenen Kontur) des markierten freien Bildes. → True, wenn etwas gesetzt wurde."""
    if z is None or z[0] != "frei":
        return False
    _k, key, a, _bild = z
    neu = dict(a)
    if fuell != "__nicht__":
        neu["fuell"] = fuell
    if rand != "__nicht__":
        neu["rand"] = rand
    if fx != "__nicht__":
        if fx:
            neu["fx"] = fx
        else:
            neu.pop("fx", None)
    if rand_teil:
        alt = dict(neu.get("rand") or {"b": 2.0, "farbe": Farbe.SCHWARZ, "art": "einfach"})
        alt.update(rand_teil)
        neu["rand"] = alt
    _speichern_frei(ed, key, neu)
    return True


def fuellbild_setzen(ed, z, bild: QImage) -> bool:
    """„Füllung ▸ Bild“: das Bild als Füllung; es liegt als Ressource des Dokuments."""
    if z is None or z[0] != "frei" or bild.isNull():
        return False
    return format_setzen(ed, z, fuell={"art": "bild", "n": ed.bild_ressource_neu(bild)})


# ---- Zeichentools: Ausrichten, Drehen, Ebene, Maße, Format übertragen -------------------------------------------------------------
AUSRICHTEN = {"links": ("ah", "left"), "mitte": ("ah", "center"), "rechts": ("ah", "right"),
              "oben": ("av", "top"), "mittig": ("av", "center"), "unten": ("av", "bottom")}


def frei_aendern(ed, z, **teile) -> bool:
    """Einzelne Angaben des markierten freien Bildes ersetzen (Schlüssel der Angabe: ``dreh``, ``hinter`` …)."""
    if z is None or z[0] != "frei":
        return False
    if "hinter" in teile and "umbruch" not in teile:
        teile["umbruch"] = "hinter" if teile["hinter"] else "vor"
    _speichern_frei(ed, z[1], {**z[2], **teile})
    return True


def ausrichten(ed, z, wie: str) -> bool:
    """Das freie Bild am Blatt ausrichten (links/mitte/rechts, oben/mittig/unten)."""
    if wie not in AUSRICHTEN or z is None or z[0] != "frei":
        return False
    achse, wert = AUSRICHTEN[wie]
    bezug = ("bh", "xh") if achse == "ah" else ("bv", "yv")
    return frei_aendern(ed, z, **{achse: wert, bezug[0]: "seite", bezug[1]: 0.0})


def drehen(ed, z, grad: float) -> bool:
    if z is None or z[0] != "frei":
        return False
    return frei_aendern(ed, z, dreh=(float(z[2].get("dreh", 0.0)) + grad) % 360.0)


def ebene(ed, z, vorn: bool) -> bool:
    """„Eine Ebene nach vorne/hinten“: das Bild liegt vor oder hinter dem Text (frei positioniert)."""
    if z is None:
        return False
    if z[0] == "frei":
        return frei_aendern(ed, z, hinter=not vorn)
    anwenden(ed, z, {"umbruch": "vor" if vorn else "hinter"})
    return True


def masse_lesen(ed, z) -> tuple[float, float] | None:
    """Breite und Höhe des markierten Bildes in mm."""
    if z is None:
        return None
    if z[0] == "frei":
        return px_to_mm(float(z[2]["b"])), px_to_mm(float(z[2]["h"]))
    return px_to_mm(z[1].breite), px_to_mm(z[1].hoehe)


def masse_setzen(ed, z, breite_mm: float | None = None, hoehe_mm: float | None = None) -> bool:
    if z is None:
        return False
    if z[0] == "frei":
        return frei_aendern(ed, z, **({"b": mm_to_px(breite_mm)} if breite_mm else {}), **({"h": mm_to_px(hoehe_mm)} if hoehe_mm else {}))
    return ed.inline_aendern(z[1].id, **({"breite": mm_to_px(breite_mm)} if breite_mm else {}), **({"hoehe": mm_to_px(hoehe_mm)} if hoehe_mm else {}))


def format_merken(z) -> dict | None:
    """Füllung, Kontur und Effekte des markierten freien Bildes zum „Format übertragen“."""
    if z is None or z[0] != "frei":
        return None
    a = z[2]
    return {k: a[k] for k in ("fuell", "rand", "fx") if a.get(k)} | {"_leer": [k for k in ("fuell", "rand", "fx") if not a.get(k)]}


def format_uebertragen(ed, z, merk: dict) -> bool:
    if z is None or z[0] != "frei" or not merk:
        return False
    neu = dict(z[2])
    for k in merk.get("_leer", ()):
        neu.pop(k, None)
    neu.update({k: v for k, v in merk.items() if k != "_leer"})
    _speichern_frei(ed, z[1], neu)
    return True


# ---- Bildtools für frei positionierte Bilder (Zuschneiden, Farbe, Originalgröße, Alternativtext, Entfernen) ----------------------------
def _hoehe_je_breite(img: QImage, a: dict) -> float:
    """Höhe je Breite des sichtbaren Ausschnitts von ``img`` (mit Zuschnitt ``zu`` der Angabe)."""
    from lunivo_writer.editor.objekte import bildzuschnitt as BZ
    l, o, r, u = BZ.lesen(a)
    return img.height() * (1 - o - u) / max(1.0, img.width() * (1 - l - r))


def frei_bild_ersetzen(ed, z, wandle) -> bool:
    """``wandle(QImage) → QImage``: das Bild des markierten freien Bildes wird durch das Ergebnis ersetzt (Anzeigebreite bleibt, die Höhe
    folgt dem Seitenverhältnis); das Original bleibt für „Original“ erhalten."""
    if z is None or z[0] != "frei":
        return False
    a = z[2]
    img = ed.bild_ressource(a.get("n", ""))
    if img is None:
        return False
    neu = wandle(QImage(img))
    if neu is None or neu.isNull():
        return False
    name = ed.bild_ressource_neu(neu)
    b = float(a["b"])
    return frei_aendern(ed, z, n=name, h=b * _hoehe_je_breite(neu, a), orig=a.get("orig") or a.get("n"))


def frei_original(ed, z) -> bool:
    """Farbänderung und Zuschnitt zurücknehmen (das ursprüngliche Bild, gleiche Anzeigebreite)."""
    if z is None or z[0] != "frei" or not z[2].get("orig"):
        return False
    img = ed.bild_ressource(z[2]["orig"])
    if img is None:
        return False
    b = float(z[2]["b"])
    return frei_aendern(ed, z, n=z[2]["orig"], h=b * _hoehe_je_breite(img, z[2]))


def frei_original_groesse(ed, z) -> bool:
    """Das Bild in seiner Pixelgröße."""
    img = ed.bild_ressource(z[2].get("n", "")) if z is not None and z[0] == "frei" else None
    if img is None:
        return False
    from lunivo_writer.editor.objekte import bildzuschnitt as BZ
    l, o, r, u = BZ.lesen(z[2])                                      # der sichtbare Ausschnitt in Bildpunkten
    return frei_aendern(ed, z, b=float(img.width()) * (1 - l - r), h=float(img.height()) * (1 - o - u))


def frei_entfernen(ed) -> bool:
    """Das gewählte Bild löschen (wie die Entf-Taste)."""
    return ed.objekt_loeschen()
