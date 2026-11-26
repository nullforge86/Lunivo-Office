"""Frei objekt text daten: aus ``vcl.qt.rendering.textfelder.frei_objekt_text`` herausgelöst."""
from core.layout.drucklayout.ausgabe.text.wordartobjekt import ZEICHEN_SCHLUESSEL


ARTEN = ("wordart", "textfeld", "form", "diagramm", "smartart", "piktogramm", "zeichenbereich")


TEXT_ARTEN = ("wordart", "textfeld")                                 # Arten mit Text zum Schreiben (Texttools, Eingabefeld im Objekt)


STANDARD_MASS = {"form": (160, 120), "diagramm": (480, 300), "zeichenbereich": (567, 302)}         # Größe in Bildpunkten, wenn beim Einfügen keine angegeben ist


FORM_STANDARD = {"form": "Rechteck", "fuell": "#4a8fd8", "linie": "#1f3864", "strich": 2.0, "text": ""}


TEXTFELD_STANDARD = {"text": "", "schrift": "Liberation Sans", "pt": 11, "farbe": "#1f1f1f"}


TEXTFELD_FUELL = {"art": "farbe", "farbe": "#ffffff"}


TEXTFELD_RAND = {"b": 1.5, "farbe": "#1f3864", "art": "einfach"}


WORDART_STANDARD = {"text": "Hier Text einfügen", "vorlage": 0, "pt": 36, "schrift": "Liberation Sans"}


SS = 2                                                              # Zeichnen in doppelter Auflösung (scharf auch bei Zoom)


# ---- Gemeinsame Hilfen: Listenmarken, Textrichtung, Effekte ---------------------------------------------------------------
RICHTUNGEN = ("waagerecht", "senkrecht_rl", "senkrecht_lr", "dreh90", "dreh270", "asiatisch270")


def gedreht(richtung: str | None) -> bool:
    return richtung not in (None, "", "waagerecht")


def laeufe_ab(laeufe: list[dict], von: int, bis: int | None = None) -> list[dict]:
    """Der Ausschnitt ``[von, bis)`` des Gesamttextes mit seinen Formaten."""
    out, pos = [], 0
    for r in laeufe:
        n = len(r["t"]); a, e = max(von, pos), min(pos + n if bis is None else bis, pos + n)
        if e > a:
            out.append({**r, "t": r["t"][a - pos:e - pos]})
        pos += n
    return out


def laeufe_zusammen(laeufe: list[dict]) -> list[dict]:
    """Benachbarte Läufe mit gleichem Format zu einem verbinden (leere fallen weg)."""
    out: list[dict] = []
    for r in laeufe:
        if not r["t"]:
            continue
        if out and {k: v for k, v in out[-1].items() if k != "t"} == {k: v for k, v in r.items() if k != "t"}:
            out[-1] = {**out[-1], "t": out[-1]["t"] + r["t"]}
        else:
            out.append(dict(r))
    return out


# ---- Textfeld zeichnen --------------------------------------------------------------------------------------------------
def zeichen_dict(d: dict, lauf: dict, vorlage, farbe_ueber: str | None, standard_farbe: str) -> dict:
    """Das Zeichenformat eines Laufs im Dokumentenmodell: seine eigenen Angaben, sonst die des Objekts."""
    e = {k: lauf.get(k, d.get(k)) for k in ZEICHEN_SCHLUESSEL}
    z: dict = {"schrift": e["schrift"] or d.get("schrift", "Liberation Sans"), "groesse_pt": float(e["pt"] or d.get("pt", 11))}
    if e["fett"]:
        z["fett"] = True
    if e["kursiv"]:
        z["kursiv"] = True
    if e["unter"]:
        z["unterstrichen"] = True
        if isinstance(e["unter"], str) and e["unter"] != "einfach":
            z["unter_art"] = e["unter"]
        if e["unterfarbe"]:
            z["unter_farbe"] = e["unterfarbe"]
    if e["durch"]:
        z["durchgestrichen"] = True
    if e["hoch"]:
        z["hoch_tief"] = "hoch"
    elif e["tief"]:
        z["hoch_tief"] = "tief"
    if e["hervor"]:
        z["marker"] = e["hervor"]
    kontur = e["kontur"] if e["kontur"] is not None else (vorlage[3] if vorlage and "kontur" not in d else None)
    if kontur:
        z["effekt"] = {"kontur": True, "kontur_farbe": kontur, "kontur_breite": float(d.get("kontur_breite", 0.75))}
    if farbe_ueber:
        z["farbe"] = farbe_ueber
    elif "fuell" in lauf:
        z["farbe"] = lauf["fuell"] or "#00000000"                       # leer = ausdrücklich keine Füllung
    else:
        z["farbe"] = standard_farbe
    return z


TEXTRAND = 8.0                                                 # Standard-Innenabstand des Textes im Feld (Bildpunkte); ``d["innen"]`` = [links, oben, rechts, unten] überschreibt ihn


def innen(d: dict) -> tuple[float, float, float, float]:
    """Innenabstand links, oben, rechts, unten — aus ``d["innen"]`` (zum Beispiel aus bodyPr lIns/tIns/rIns/bIns einer DOCX), sonst ``TEXTRAND``."""
    w = d.get("innen")
    if isinstance(w, (list, tuple)) and len(w) == 4:
        try:
            return tuple(max(0.0, float(x)) for x in w)
        except (TypeError, ValueError):
            pass
    return (TEXTRAND,) * 4
