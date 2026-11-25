"""Freie Objekte mit Parametern (WordArt, Textfeld): EIN gemeinsamer Baustein.

Ein solches Objekt ist ein frei positioniertes Bild (siehe ``freie_bilder``): Auswahlrahmen, acht Griffe, Drehgriff, Verschieben und die
Schnellleiste daneben (Layout, Formstil, Füllung, Kontur) kommen aus ``oberflaeche/dokument/bearbeitung/freie_bilder_bedienung.py``. Dieser Baustein ergänzt nur,
was die beiden Arten unterscheidet: ihre Parameter (``art`` und ``daten`` an der Angabe des Bildes) und das Zeichnen daraus.
Neue Art = ein Eintrag in ``ZEICHNER``. Kein HTML: gezeichnet wird mit QPainter; Text setzt der Kern (LayoutEngine).
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, QUrl, Qt
from PySide6.QtGui import QColor, QImage, QPainter

from lunivo_writer.editor.objekte.bild import freie_bilder as FB
from lunivo_writer.core.funktionen.absatz.mehrstufig import nummer_text

from lunivo_writer.editor.objekte.frei.frei_objekt_text import ARTEN, TEXT_ARTEN, STANDARD_MASS, FORM_STANDARD, TEXTFELD_STANDARD, TEXTFELD_FUELL, TEXTFELD_RAND, WORDART_STANDARD, _SS, RICHTUNGEN, _PUNKTE, ZEICHEN_SCHLUESSEL, listenmarken, richtung_anwenden, _gedreht, effekte_auf_text, anzeige_laeufe, laeufe_text, laeufe_ab, laeufe_zusammen, _zeilen_laeufe, wordart_zeichnen, _text_passt, textfeld_zeichnen


def _pfad_festhalten(d: dict, k: dict) -> None:
    """Eine Katalogform behält ihren Umriss als Vektorpfad (0…1) in den Parametern des Modells; der Kern zeichnet sie damit selbst (scharf in jeder Größe, im Editor und im PDF
    gleich), das Qt-Bild bleibt die Vorschau beim Bearbeiten. Grundformen und Freiformen kennt der Kern ohne Pfad."""
    from lunivo_writer.core.geometrie.grundformen import FORMEN
    from lunivo_writer.editor.objekte.formen import formen_katalog as K
    name = str(k["form"])
    if name.casefold() in {"rechteck", "abgerundet", "ellipse", "kreis", "linie", "pfeil", "freiform"} | set(FORMEN) or k.get("punkte") or not K.hat(name):
        d.pop("pfad_norm", None)
        d.pop("offen", None)
        return
    from PySide6.QtCore import QRectF
    from lunivo_writer.oberflaeche.zeichnen.pfad import pfad_zu_vektor
    try:
        pfad = K.pfad(name, QRectF(0, 0, 100, 100), k.get("adj") if K.anpassbar(name) else None)
        ops = [[o[0]] + [round(v / 100.0, 5) for v in o[1:]] for o in pfad_zu_vektor(pfad).ops]
    except Exception:                                                              # noqa: BLE001 — ohne Pfad bleibt das Qt-Bild die Darstellung
        d.pop("pfad_norm", None)
        return
    d["pfad_norm"] = ops
    if K.ist_linie(name):
        d["offen"] = True
    else:
        d.pop("offen", None)


def _form_zeichnen(d: dict, b: float, h: float) -> QImage:
    """Eine Form (``editor/objekte/formen.py``/``einfuegen.py``) in b × h Bildpunkten, in doppelter Auflösung."""
    from lunivo_writer.editor.dokument import einfuegen as E
    k = {**FORM_STANDARD, **d}
    b, h = (b, h) if b and h else STANDARD_MASS["form"]
    _pfad_festhalten(d, k)
    return E.form_bild(k["form"], max(2, round(b)), max(2, round(h)), k["fuell"] or "", k["linie"] or "#00000000",
                       float(k["strich"]), k["text"], skala=_SS, adj=k.get("adj"), fuell_art=k.get("fuell_art") or "",
                       punkte=k.get("punkte"))


def _diagramm_zeichnen(d: dict, b: float, h: float) -> QImage:
    """Ein Diagramm (``editor/diagramme/diagramm.py``) aus den gespeicherten Daten, in b × h Bildpunkten, in doppelter Auflösung."""
    from lunivo_writer.editor.diagramme import diagramm as D
    b, h = (b, h) if b and h else STANDARD_MASS["diagramm"]
    return D.bild_aus_daten(d, b, h, _SS)


def _smartart_zeichnen(d: dict, _b: float, _h: float) -> QImage:
    from lunivo_writer.editor.objekte.smartart import smartart as SA
    return SA.zeichnen(d)


def _piktogramm_zeichnen(d: dict, _b: float, _h: float) -> QImage:
    from lunivo_writer.editor.dokument import einfuegen as E
    return E.piktogramm_bild(d.get("name", "star"), 96, d.get("farbe", "#1f2328"))


def _zeichenbereich_zeichnen(d: dict, b: float, h: float) -> QImage:
    """Zeichenbereich (``editor/objekte/formen.py``): gestrichelter Rand und die ``kinder`` (Formen mit Lage x/y), in doppelter Auflösung."""
    from lunivo_writer.editor.objekte.formen import formen as F
    b, h = (b, h) if b and h else STANDARD_MASS["zeichenbereich"]
    return F.zeichenbereich_bild(dict(d, breite=round(b), hoehe=round(h)), _SS)


# Art → Funktion(daten, breite, höhe) → Bild. Neue Art = ein Eintrag hier (und in ARTEN).
ZEICHNER = {"wordart": lambda d, b, h: wordart_zeichnen(d), "textfeld": textfeld_zeichnen, "form": _form_zeichnen,
            "diagramm": _diagramm_zeichnen, "smartart": _smartart_zeichnen, "piktogramm": _piktogramm_zeichnen,
            "zeichenbereich": _zeichenbereich_zeichnen}
NEU_ZEICHNEN = ("textfeld", "form", "diagramm", "zeichenbereich")                      # Arten, die nach einer Größenänderung in der neuen Größe frisch gezeichnet werden


def zeichnen(art: str, d: dict, b: float = 0, h: float = 0) -> QImage:
    return ZEICHNER[art](d, b, h)


def _anzeige_mass(art: str, img: QImage, b: float, h: float) -> tuple[float, float]:
    """Größe auf dem Blatt in Bildpunkten: WordArt aus dem Bild (ohne Überbreite), SmartArt wie das Bild (sofern keine Größe vorgegeben),
    Textfeld, Form und Diagramm wie vorgegeben (sonst die Standardgröße)."""
    if art == "wordart":
        return img.width() / _SS, img.height() / _SS
    if art in ("smartart", "piktogramm"):
        return (b, h) if b and h else (float(img.width()), float(img.height()))
    return (b, h) if b and h else STANDARD_MASS.get(art, (b, h))


# ---- Einfügen ---------------------------------------------------------------------------------------------------------------
def einfuegen(ed, art: str, daten: dict, b: float = 0, h: float = 0) -> int | None:
    """Fügt das Objekt als freies Objekt am Absatz der Schreibmarke ein und wählt es aus. → Id des Objekts."""
    if art in STANDARD_MASS and not (b and h):
        b, h = STANDARD_MASS[art]
    img = zeichnen(art, daten, b, h)
    bb, hh = _anzeige_mass(art, img, b, h)
    return bild_einfuegen(ed, img, bb, hh, art, daten)


def bild_einfuegen(ed, img: QImage, bb: float, hh: float, art: str | None = None, daten: dict | None = None, alt: str = "") -> int | None:
    """Der gemeinsame Weg aller freien Bilder und Objekte: ``img`` als Darstellung, Größe auf die Inhaltsbreite begrenzt, danach ausgewählt.
    ``art``/``daten`` nur bei Objekten mit Parametern (siehe ``ZEICHNER``); ein gewöhnliches Bild (Datei, Bildschirmfoto) hat keine. → Id des Objekts."""
    d = {"daten": dict(daten)} if daten else {}
    if art == "textfeld":
        d.setdefault("fuell", dict(TEXTFELD_FUELL))
        d.setdefault("rand", dict(TEXTFELD_RAND))
    return ed.objekt_frei_einfuegen(art or "bild", d, bb, hh, img, alt)


# ---- Lesen und Ändern ---------------------------------------------------------------------------------------------------------
def ziel(ed):
    """(Art, Daten, Id, Angabe, Bild) des gewählten Objekts (WordArt, Textfeld, Form, Diagramm, SmartArt) oder None."""
    o = ed.objekt_gewaehlt() if hasattr(ed, "objekt_gewaehlt") else None
    if o is None or o.art not in ARTEN:
        return None
    angabe = {**{k: v for k, v in o.daten.items() if k != "daten"}, "art": o.art, "b": o.breite, "h": o.hoehe, "daten": dict(o.daten.get("daten") or {}),
              "n": o.ressource}
    return (o.art, dict(o.daten.get("daten") or {}), o.id, angabe, ed.objekt_bild(o))


def art_gewaehlt(ed) -> str | None:
    z = ziel(ed)
    return z[0] if z else None


def daten_lesen(ed, art: str) -> dict | None:
    z = ziel(ed)
    return z[1] if z and z[0] == art else None


def aendern(ed, art: str, **kw) -> bool:
    """Parameter des gewählten Objekts ändern (siehe ``_aendern_innen``)."""
    return _aendern_innen(ed, art, **kw)


def _daten_vorbereiten(d: dict, kw: dict) -> None:
    """Vor dem Ändern: Vorlage und neuer Text setzen Altes zurück, ein Zeichenformat fürs ganze Objekt löscht gleiche Angaben der Läufe."""
    if kw.get("vorlage") is not None:                                # eine Vorlage setzt Füllung, Kontur und Effekt neu
        for k in ("fuell", "kontur", "kontur_breite", "effekt"):
            if k not in kw:
                d.pop(k, None)
    if "text" in kw and "laeufe" not in kw:                          # neuer Text ohne Formate (Dialog, Vorlage): die Läufe gelten nicht mehr
        d.pop("laeufe", None)
    for k in kw:                                                     # ein Zeichenformat für das ganze Objekt löscht gleiche Angaben der Läufe
        if k in ZEICHEN_SCHLUESSEL and d.get("laeufe"):
            d["laeufe"] = laeufe_zusammen([{x: y for x, y in r.items() if x != k} for r in d["laeufe"]])
            if all(len(r) == 1 for r in d["laeufe"]):
                d.pop("laeufe")


def _form_daten_setzen(d: dict, k: str, v) -> None:
    """Bei einer Form: Farben der Form selbst, kein Kasten ums Bild."""
    if k == "form_fuell":
        d["fuell"] = v or ""
    elif k == "form_linie":
        d["linie"] = v or ""
    else:
        d["strich"] = float(v)


def _kasten_setzen(neu: dict, a: dict, k: str, v) -> None:
    """Füllung, Strichstärke, Effekt und Linie des Kastens ums Objekt."""
    if k == "form_fuell":
        neu["fuell"] = {"art": "farbe", "farbe": v} if v else None
    elif k == "form_strich":
        neu["rand"] = {**(a.get("rand") or TEXTFELD_RAND), "b": float(v) * 96 / 72}
    elif k == "form_effekt":
        if v:
            neu["fx"] = v
        else:
            neu.pop("fx", None)
    else:                                                            # form_linie
        neu["rand"] = {**(a.get("rand") or TEXTFELD_RAND), "farbe": v} if v else None


def _eintrag_setzen(art: str, k: str, v, d: dict, neu: dict, a: dict) -> None:
    """Ein Schlüssel von ``kw`` (außer Größe) in ``daten`` oder in den Kasten schreiben."""
    if k == "laeufe":
        if v:
            d["laeufe"] = v
        else:
            d.pop("laeufe", None)
    elif art == "form" and k in ("form_fuell", "form_linie", "form_strich"):
        _form_daten_setzen(d, k, v)
    elif k == "untertyp":                                          # Diagramm: Diagrammart (in den Daten unter „art“)
        d["art"] = v
    elif k in ("form_fuell", "form_strich", "form_effekt", "form_linie"):
        _kasten_setzen(neu, a, k, v)
    elif v is None:
        d.pop(k, None)
    else:
        d[k] = v


def _aendern_innen(ed, art: str, **kw) -> bool:
    """Parameter des gewählten Objekts ändern und neu zeichnen. ``breite``/``hoehe`` (px) ändern die Größe; ``form_fuell`` (Farbe oder ``""``)
    und ``form_linie`` (Farbe oder ``""``) die Füllung und den Rand des Objekts; alle anderen Schlüssel gehören zu ``daten``."""
    z = ziel(ed)
    if z is None or z[0] != art:
        return False
    _art, d, oid, a, bild = z
    kasten: dict = {}
    aussen = {k: v for k, v in a.items() if k not in ("art", "b", "h", "daten", "n")}
    b, h = float(a["b"]), float(a["h"])
    _daten_vorbereiten(d, kw)
    for k, v in kw.items():
        if k == "breite":
            b = float(v)
        elif k == "hoehe":
            h = float(v)
        else:
            _eintrag_setzen(art, k, v, d, kasten, a)
    for k, v in kasten.items():
        if v is None:
            aussen.pop(k, None)
        else:
            aussen[k] = v
    if art == "form":                                                # Farbe und Rand der Form selbst gelten über der vollen Füllung/Kontur aus einer Datei (Verlauf, Muster, Strichart)
        if "form_fuell" in kw:
            aussen.pop("fuell", None)
        if "form_linie" in kw or "form_strich" in kw:
            aussen.pop("rand", None)
    neu_zeichnen = set(kw) - {"form_fuell", "form_linie", "form_strich", "form_effekt"} or (
        art == "form" and set(kw) & {"form_fuell", "form_linie", "form_strich"})
    felder = {"daten": {**aussen, "daten": d}, "breite": b, "hoehe": h}
    if neu_zeichnen:
        img = zeichnen(art, d, b, h)
        if art == "smartart":                                        # Breite bleibt, die Höhe folgt dem neuen Bild
            felder["hoehe"] = b * img.height() / max(1, img.width())
        elif art == "wordart":                                       # die Größe folgt dem Bild: gleicher Maßstab wie vorher
            faktor = a["b"] / max(1.0, (bild.width() if bild is not None else _SS * a["b"]) / _SS)
            felder["breite"], felder["hoehe"] = img.width() / _SS * faktor, img.height() / _SS * faktor
        felder["bilddaten"] = ed._png(img)
    return ed.objekt_setzen(oid, **felder)


def daten_still(ed, art: str, **kw) -> bool:
    """Daten des gewählten Objekts ändern, ohne das Bild neu zu zeichnen (z. B. die Auswahl eines Diagrammteils); None entfernt den Schlüssel."""
    z = ziel(ed)
    if z is None or z[0] != art:
        return False
    _art, d, oid, a, _bild = z
    for k, v in kw.items():
        if v is None:
            d.pop(k, None)
        else:
            d[k] = v
    return ed.objekt_setzen(oid, daten={**{k: v for k, v in a.items() if k not in ("art", "b", "h", "daten", "n")}, "daten": d})


def nach_groesse(ed, neu: dict) -> dict:
    """Nach dem Ziehen der Griffe: Textfeld, Form und Diagramm werden in der neuen Größe frisch gezeichnet; SmartArt skaliert nur."""
    return neu


def text_bereich(a: dict, bild: QImage) -> QRectF | None:
    """Wo der Text im Objekt liegt, als Anteil (0..1) von Breite/Höhe — für die graue Textmarkierung wie in der Vorlage (nur WordArt)."""
    if a.get("art") != "wordart" or bild is None or bild.isNull():
        return None
    w, h = bild.width() / _SS, bild.height() / _SS
    if "reflektion" in (a.get("daten", {}).get("effekt") or {}):
        h /= 2
        return QRectF(20 / w, 20 / (h * 2), (w - 40) / w, (h - 40) / (h * 2))
    return QRectF(20 / w, 20 / h, (w - 40) / w, (h - 40) / h)


# ---- Textoptionen der Seitenleiste „Formatierung“ -----------------------------------------------------------------------------
def text_werte_lesen(ed) -> dict | None:
    """Die Textoptionen (Format von ``texteffekt.py``) des gewählten Objekts."""
    z = ziel(ed)
    if z is None or z[0] not in TEXT_ARTEN:
        return None
    d = z[1]
    w = {"fuell": "farbe", "farbe": d.get("fuell") or d.get("farbe") or "", "transparenz": 0, "kontur": bool(d.get("kontur")),
         "kontur_farbe": d.get("kontur") or "#000000", "kontur_breite": float(d.get("kontur_breite", 0.75)), "kontur_art": "einfach"}
    if "fuell" in d and not d["fuell"]:
        w["fuell"] = "keine"
    return w


def text_werte_anwenden(ed, werte: dict) -> bool:
    """Die Textoptionen der Seitenleiste wirken auf den Text im gewählten Objekt: Füllung (Farbe, Transparenz), Kontur (Farbe, Breite)."""
    art = art_gewaehlt(ed)
    if art not in TEXT_ARTEN:
        return False
    kw: dict = {}
    if werte.get("fuell") == "keine":
        kw["fuell"] = ""
    elif werte.get("farbe") or werte.get("transparenz"):
        c = QColor(werte.get("farbe") or "#000000"); c.setAlphaF(1.0 - float(werte.get("transparenz", 0)) / 100)
        kw["fuell"] = c.name(QColor.HexArgb) if c.alpha() < 255 else c.name()
    if werte.get("kontur"):
        kw["kontur"] = werte.get("kontur_farbe", "#000000"); kw["kontur_breite"] = float(werte.get("kontur_breite", 0.75))
    elif "kontur" in werte:
        kw["kontur"] = ""
    return aendern(ed, art, **kw) if kw else False


# ---- Verknüpfte Textfelder -----------------------------------------------------------------------------------------------------
def _textfelder(ed) -> list[tuple[tuple, dict]]:
    """Alle freien Textfelder des Dokuments: (Schlüssel, Angabe) — frisch aus dem Modell gelesen."""
    return [(key, a) for key, a, _bild, _r, _hinten, _seite in ed._frei_liste() if a.get("art") == "textfeld"]


def _speichern_angabe(ed, key: tuple, a: dict) -> None:
    ed.angabe_speichern(key[1], FB.ohne_hilfsangaben(a))


def _neu_setzen(ed, key: tuple, a: dict) -> dict:
    """Das Bild des Textfelds aus seinen Daten neu zeichnen und die Angabe sichern."""
    n = ed.bild_ressource_neu(textfeld_zeichnen(a.get("daten", {}), a["b"], a["h"]))
    a = dict(a, n=n)
    _speichern_angabe(ed, key, a)
    return a


def _kette_ohne(felder: dict, da: dict, verboten: str) -> bool:
    """Von ``da`` die Kette nach oben bis zum Kopf gehen. → False, wenn ein Vorgänger fehlt oder das Feld ``verboten`` darin steht (Kreis)."""
    kopf = da
    while kopf.get("von"):
        nxt = next((x["daten"] for x in felder.values() if x.get("daten", {}).get("id") == kopf["von"]), None)
        if nxt is None or nxt.get("id") == verboten:
            return False
        kopf = nxt
    return True


def _verknuepfbar(felder: dict, von_key: tuple, nach_key: tuple):
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


def _text_uebernehmen(da: dict, db: dict) -> None:
    """Den Text (und die Läufe) von ``db`` an ``da`` hängen; ``db`` wird leer."""
    if not db.get("text"):
        return
    trenner = "\n" if da.get("text") else ""
    if da.get("laeufe") or db.get("laeufe"):
        la = da.get("laeufe") or [{"t": da.get("text", "")}]; lb = db.get("laeufe") or [{"t": db["text"]}]
        da["laeufe"] = laeufe_zusammen(la + ([{"t": trenner}] if trenner else []) + lb)
    da["text"] = da.get("text", "") + trenner + db["text"]
    db["text"] = ""; db.pop("laeufe", None)


def verknuepfen(ed, von_key: tuple, nach_key: tuple) -> bool:
    """Textfeld ``von`` mit Textfeld ``nach`` verknüpfen: was in ``von`` nicht mehr passt, läuft in ``nach`` weiter (wie „Verknüpfung erstellen“).
    Der Text von ``nach`` wird an den von ``von`` gehängt. Nicht möglich: gleiche Felder, ``von`` hat schon einen Nachfolger, ``nach`` einen
    Vorgänger, Kreisverknüpfung. → True bei Erfolg."""
    felder = dict(_textfelder(ed))
    paar = _verknuepfbar(felder, von_key, nach_key)
    if paar is None:
        return False
    da, db = paar
    _text_uebernehmen(da, db)
    da["weiter"], db["von"] = db["id"], da["id"]
    _speichern_angabe(ed, von_key, dict(felder[von_key], daten=da)); _speichern_angabe(ed, nach_key, dict(felder[nach_key], daten=db))
    kette_aktualisieren(ed)
    return True


def loesen(ed, key: tuple) -> bool:
    """Die Verknüpfung des Textfelds zu seinem Nachfolger lösen (steht ``key`` am Ende einer Kette, die zu seinem Vorgänger): der Nachfolger
    behält den Text, der in ihm stand; das Feld davor zeigt weiter seinen Text, der Rest wird abgeschnitten. → True, wenn etwas gelöst wurde."""
    felder = dict(_textfelder(ed))
    if key not in felder:
        return False
    d = felder[key].get("daten", {})
    if not d.get("weiter") and d.get("von"):                         # ``key`` ist ein Nachfolger: die Verknüpfung davor lösen
        key = next((k for k, x in felder.items() if x.get("daten", {}).get("weiter") == d.get("id")), None)
        if key is None:
            return False
        d = felder[key].get("daten", {})
    if not d.get("weiter"):
        return False
    nach = next((k for k, x in felder.items() if x.get("daten", {}).get("id") == d["weiter"]), None)
    da = dict(d); da.pop("weiter", None); da.pop("gezeigt_rest", None)
    _speichern_angabe(ed, key, dict(felder[key], daten=da))
    if nach is not None:
        db = dict(felder[nach].get("daten", {})); db.pop("von", None)
        db["text"] = db.pop("gezeigt", db.get("text", ""))           # behält, was in ihm stand
        gl = db.pop("gezeigt_laeufe", None)
        if gl:
            db["laeufe"] = gl
        else:
            db.pop("laeufe", None)
        _speichern_angabe(ed, nach, dict(felder[nach], daten=db))
    kette_aktualisieren(ed)
    return True


def ist_verknuepft(ed, key: tuple) -> bool:
    d = dict(_textfelder(ed)).get(key, {}).get("daten", {})
    return bool(d.get("weiter") or d.get("von"))


def _kette_glieder(k, a, nach_id: dict) -> list:
    """Alle Felder einer Kette ab ``(k, a)`` in Reihenfolge."""
    kette = [(k, a)]
    nxt = a.get("daten", {})
    while nxt.get("weiter") and nxt["weiter"] in nach_id:
        kette.append(nach_id[nxt["weiter"]]); nxt = kette[-1][1].get("daten", {})
    return kette


def _kette_verteilen(ed, kette: list, voll: list, hat_laeufe: bool, gesehen: set) -> None:
    """Den vollen Text auf die Felder der Kette verteilen; nur Felder mit geändertem Anteil neu setzen."""
    frisch = {kk: aa for kk, aa in _textfelder(ed)}               # aktuelle Angaben (Schlüssel bleiben)
    off = 0
    for kk, aa in kette:
        aa = frisch.get(kk, aa); dd = dict(aa.get("daten", {}))
        gesehen.add(kk)
        rest = laeufe_ab(voll, off)
        cut = _text_passt(dd, rest, aa["b"], aa["h"]) if dd.get("weiter") else len(laeufe_text(rest))
        zeigt = laeufe_ab(rest, 0, cut)
        skip = len(laeufe_text(rest)[cut:]) - len(laeufe_text(rest)[cut:].lstrip("\n "))
        off += cut + skip
        text = laeufe_text(zeigt).rstrip("\n")
        neu_l = laeufe_zusammen(laeufe_ab(zeigt, 0, len(text))) if hat_laeufe else None
        if dd.get("gezeigt") != text or dd.get("gezeigt_laeufe") != neu_l or "gezeigt" not in dd:
            dd["gezeigt"] = text
            if neu_l is not None:
                dd["gezeigt_laeufe"] = neu_l
            else:
                dd.pop("gezeigt_laeufe", None)
            _neu_setzen(ed, kk, dict(aa, daten=dd))


def kette_aktualisieren(ed) -> None:
    """Jede Kette neu verteilen: der Text des ersten Feldes (mit seinen Zeichenformaten) füllt ein Feld nach dem anderen; geändert werden nur
    Felder, deren Anteil sich ändert."""
    felder = _textfelder(ed)
    nach_id = {a.get("daten", {}).get("id"): (k, a) for k, a in felder if a.get("daten", {}).get("id")}
    gesehen: set = set()
    for k, a in felder:
        d = a.get("daten", {})
        if d.get("von") or k in gesehen:
            continue
        if not d.get("weiter"):
            if "gezeigt" in d:                                       # nicht (mehr) verknüpft
                d2 = {x: y for x, y in d.items() if x not in ("gezeigt", "gezeigt_laeufe")}; _neu_setzen(ed, k, dict(a, daten=d2))
            continue
        voll = d.get("laeufe") or [{"t": d.get("text", "")}]
        _kette_verteilen(ed, _kette_glieder(k, a, nach_id), voll, bool(d.get("laeufe")), gesehen)
