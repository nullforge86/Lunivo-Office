from __future__ import annotations
from core.geometrie import Rect
from core.textsatz.engine import FontSpec
from core.layout.drucklayout.ausgabe.backend import RenderTarget, Style
from core.layout.drucklayout.ausgabe.diagramm import diagrammformat as DF
from core.layout.drucklayout.ausgabe.diagramm.diagrammtypen import ALT, BEISPIEL_KATEGORIEN, BEISPIEL_REIHEN, FARBEN, VORLAGEN, ist_kreis
from core.diagramme.legenden.legende import _legende
from core.diagramme.typen.kartesisch import _kartesisch
from core.diagramme.typen.kreisdiagramm import _kreis
from core.diagramme.typen.kursdiagramm import _kurs
from core.diagramme.typen.netzdiagramm import _netz
from core.layout.drucklayout.ausgabe.diagramm.diagrammzeichner_hilfen import STILE, _SCHRIFT, _Z, _farbe


STIL_EXTRA = {4: {"titel_pt": 16, "titel_fett": True}, 5: {"labels": True}, 6: {"rahmen": "#1f3864"}, 7: {"raster_farbe": "#b9d4f5"}, 8: {"raster_farbe": "#ffd8a8"},
              10: {"raster_farbe": "#3a4a6b"}, 11: {"labels": True}, 12: {"rahmen": "#93a1a1", "raster_farbe": "#eee8d5"},
              13: {"titel_pt": 14, "titel_fett": True, "rahmen": "#000000", "raster_farbe": "#868e96"}}


STANDARD_ELEMENTE = {"achsen": True, "achsentitel": False, "datentabelle": False, "fehlerindikatoren": False, "gitter": True, "trendlinie": False}


_KOMBI_SAEULE = ("saeule", "saeule_gestapelt")


def namen_angewendet(kategorien: list, reihen: dict, ausgeblendet: dict | None, quelle: str | None):
    """Namensquelle des Diagrammfilters anwenden, ohne die Daten zu ändern (``zeile1``, ``spalte_a``, ``keine``)."""
    aus = {k: list(v) for k, v in (ausgeblendet or {}).items()}
    namen = list(reihen)
    if quelle == "spalte_a" and reihen:
        neu = {k: [(reihen[n][j] if j < len(reihen[n]) else 0.0) for n in namen] for j, k in enumerate(kategorien)}
        return namen, neu, ({"reihen": aus.get("rubriken", []), "rubriken": aus.get("reihen", [])} if aus else None)
    if quelle == "keine":
        rn = {n: f"Reihe {i + 1}" for i, n in enumerate(reihen)}
        kn = {k: str(j + 1) for j, k in enumerate(kategorien)}
        return (list(kn.values()), {rn[n]: v for n, v in reihen.items()},
                {"reihen": [rn[x] for x in aus.get("reihen", []) if x in rn], "rubriken": [kn[x] for x in aus.get("rubriken", []) if x in kn]} if aus else None)
    return kategorien, reihen, ausgeblendet or None


def _vorbereiten(d: dict) -> dict:
    art = str(d.get("art") or "saeule_gruppiert")
    farben = d.get("farben")
    if art in VORLAGEN:
        art, farben = VORLAGEN[art][0], farben or VORLAGEN[art][1]
    art = ALT.get(art, art)
    kat = list(d.get("kategorien") or BEISPIEL_KATEGORIEN)
    reihen = {k: list(v) for k, v in (d.get("reihen") or BEISPIEL_REIHEN).items()}
    kombi = [(k[0], bool(k[1])) for k in d.get("kombi") or []] or None
    kat, reihen, aus = namen_angewendet(kat, reihen, d.get("ausgeblendet"), d.get("namen_quelle"))
    if d.get("namen_quelle") == "spalte_a":
        kombi = None
    nummern = list(range(len(reihen)))
    if aus:                                                                   # Diagrammfilter: ausgeblendete Reihen und Rubriken fallen weg
        namen = list(reihen)
        nummern = [i for i, n in enumerate(namen) if n not in set(aus.get("reihen") or [])]
        keep = [j for j, k in enumerate(kat) if k not in set(aus.get("rubriken") or [])]
        reihen = {namen[i]: [reihen[namen[i]][j] for j in keep if j < len(reihen[namen[i]])] for i in nummern}
        if kombi:
            kombi = [kombi[i] for i in nummern if i < len(kombi)]
        kat = [kat[j] for j in keep]
    kachel = bool(d.get("kachel"))
    stil = int(d.get("stil") or 0)
    stil = stil if 0 <= stil < len(STILE) else 0
    ex = STIL_EXTRA.get(stil, {})
    el = {**STANDARD_ELEMENTE, **(d.get("elemente") or {})}
    if kachel:                                                                # Kachel: kleines Bildchen ohne Beschriftung, Titel und Legende
        el = {"achsen": False, "achsentitel": False, "datentabelle": False, "fehlerindikatoren": False, "gitter": True, "trendlinie": False}
    palette = [_farbe(f) for f in (farben or FARBEN)] or [_farbe(f) for f in FARBEN]
    tf = d.get("teil_format") or {}
    return {"art": art, "kat": kat, "reihen": reihen, "kombi": kombi, "nummern": nummern, "stil": stil, "ex": ex, "el": el, "palette": palette, "tf": tf,
            "titel": str(d.get("titel") or ""), "titel_an": bool(d.get("titel_an", True)) and bool(d.get("titel")) and not kachel, "legende": bool(d.get("legende", True)) and not kachel,
            "legende_pos": d.get("legende_pos", "unten"), "labels": (bool(d.get("labels")) or bool(ex.get("labels"))) and not kachel, "kachel": kachel, "wert": d.get("wert") or {}, "luecke": d.get("luecke"),
            "rand": "stil" not in d and not d.get("elemente"), "objekt_dreh": float(d.get("objekt_dreh") or 0.0)}


# ---- Einstieg ------------------------------------------------------------------------------------------------------------------
def zeichne_diagramm(b: RenderTarget, r: Rect, d: dict, geo: dict | None = None) -> list:
    """Das Diagramm in ``r`` zeichnen. ``geo`` (optional) füllt sich mit den Rechtecken der Teile; → Hinweise zu dem, was nicht dargestellt wird."""
    v = _vorbereiten(d)
    z = _Z(b, v, r, geo)
    b.draw_rect(r, Style(color=(255, 255, 255, 255) if v["kachel"] else z.grund, width=0, filled=True))
    bf = z.tf.get("diagrammbereich") or {}
    if bf.get("fuell") is not None or bf.get("linie") is not None:
        DF.teil_zeichnen(b, z.engine, r, {k: x for k, x in bf.items() if k in ("fuell", "linie")}, z.grund)
    elif v["rand"] and not v["kachel"]:
        b.draw_rect(Rect(r.x + 0.5, r.y + 0.5, r.width - 1, r.height - 1), Style(color=_farbe("#d9d9d9"), width=1))
    if v["ex"].get("rahmen") and not v["kachel"]:
        b.draw_rect(Rect(r.x + 1, r.y + 1, r.width - 2, r.height - 2), Style(color=_farbe(v["ex"]["rahmen"]), width=2))
    z.teil("diagrammbereich", r)
    if any((f or {}).get("drehung") for f in z.tf.values()):
        z.melden("Die 3D-Drehung von Diagrammteilen wird in dieser Ausgabe nicht dargestellt.")
    if not v["reihen"] or not v["kat"]:
        return z.hinweise
    kopf = 8.0
    if v["titel_an"]:
        pt = v["ex"].get("titel_pt", 12)
        tfs = FontSpec(_SCHRIFT, float(pt), 700 if v["ex"].get("titel_fett") else 400)
        tr = Rect(r.x, r.y + 4, r.width, pt * 96 / 72 + 8)
        tfmt = z.tf.get("titel") or {}
        sichtbar = any(tfmt.get(k) for k in ("fuell", "linie")) or DF.hat_effekte(tfmt)
        feld = DF.text_zeichnen(b, z.engine, v["titel"], tr, tfmt.get("text"), tfs, z.text, "center", "top", {"l": 7.2, "o": 3.6, "r": 7.2, "u": 3.6} if sichtbar else None,
                                {k: x for k, x in tfmt.items() if k in ("fuell", "linie") or k in DF.FX_SCHLUESSEL} if sichtbar else None, v["objekt_dreh"])
        z.teil("titel", feld)
        kopf = max(tr.bottom, feld.bottom) + 4 - r.y
    inhalt = Rect(r.x, r.y + kopf, r.width, r.height - kopf)
    inhalt = _legende(z, inhalt)
    art = v["art"]
    if ist_kreis(art):
        _kreis(z, inhalt)
    elif art.startswith("netz"):
        _netz(z, inhalt)
    elif art.startswith("kurs"):
        _kurs(z, inhalt)
    else:
        _kartesisch(z, inhalt)
    return z.hinweise
