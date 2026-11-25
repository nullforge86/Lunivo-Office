"""Diagramme ohne Qt: Säulen, Balken, Linien, Flächen (gruppiert, gestapelt, 100 %), Kombinationen mit Sekundärachse, Kreis, Ring, 3D-Kreis, Kreis/Balken von Kreis,
Punkt (XY), Blase, Netz, Kurs — mit Titel, Legende (vier Lagen), Achsen, Achsentiteln, Gitter, Datenbeschriftungen, Trendlinien, Fehlerindikatoren, Datentabelle und Stilen.
Gezeichnet über das Rendering-Backend.

``d`` = {"art", "titel", "titel_an", "kategorien", "reihen" {Name: [Werte]}, "farben", "legende", "legende_pos", "labels", "stil", "elemente", "ausgeblendet", "kombi",
"namen_quelle", "wert" {min, max, intervall, stellen}, "luecke", "teil_format"}. Maße in Bildpunkten (96 dpi). ``geo`` (Wörterbuch, optional) füllt sich mit den Rechtecken der Teile."""
from __future__ import annotations

import math

from lunivo_writer.core.geometry import Point, Rect
from lunivo_writer.core.textlayout.engine import FontSpec
from .backend import RenderTarget, Style, rgba
from lunivo_writer.core.rendering import diagrammformat as DF
from .diagrammtypen import ALT, BEISPIEL_KATEGORIEN, BEISPIEL_REIHEN, FARBEN, VORLAGEN, ist_kreis

_SCHRIFT = "Liberation Sans"
STILE = [("Standard", "#ffffff", "#3c4043", True), ("Ohne Raster", "#ffffff", "#3c4043", False), ("Hellgrau", "#f1f3f5", "#343a40", True), ("Dunkel", "#2b2d42", "#f1f3f5", True),
         ("Fetter Titel", "#ffffff", "#212529", True), ("Mit Datenbeschriftung", "#ffffff", "#3c4043", False), ("Mit Rahmen", "#ffffff", "#1f3864", True),
         ("Hellblau", "#e7f1fb", "#1c4f8c", True), ("Warm", "#fff4e6", "#7a3e00", True), ("Hellgrün", "#ebf7ee", "#1d4f28", False), ("Nachtblau", "#14213d", "#e5e5e5", True),
         ("Schwarz", "#000000", "#ffffff", False), ("Papier", "#fdf6e3", "#586e75", True), ("Hoher Kontrast", "#ffffff", "#000000", True)]
STIL_EXTRA = {4: {"titel_pt": 16, "titel_fett": True}, 5: {"labels": True}, 6: {"rahmen": "#1f3864"}, 7: {"raster_farbe": "#b9d4f5"}, 8: {"raster_farbe": "#ffd8a8"},
              10: {"raster_farbe": "#3a4a6b"}, 11: {"labels": True}, 12: {"rahmen": "#93a1a1", "raster_farbe": "#eee8d5"},
              13: {"titel_pt": 14, "titel_fett": True, "rahmen": "#000000", "raster_farbe": "#868e96"}}
STANDARD_ELEMENTE = {"achsen": True, "achsentitel": False, "datentabelle": False, "fehlerindikatoren": False, "gitter": True, "trendlinie": False}
TABELLE_ZEILE = 20.0
FEHLER_ANTEIL = 0.1
_KOMBI_SAEULE = ("saeule", "saeule_gestapelt")


# ---- Daten vorbereiten ------------------------------------------------------------------------------------------------------
def _hell(c: tuple, f: float) -> tuple:
    return tuple(int(c[i] + (255 - c[i]) * f) for i in range(3)) + (c[3],)


def _dunkel(c: tuple, f: float) -> tuple:
    return tuple(int(c[i] * (1 - f)) for i in range(3)) + (c[3],)


def _farbe(text, standard=(0, 0, 0, 255)) -> tuple:
    try:
        return rgba(text)
    except (ValueError, IndexError, TypeError, AttributeError):
        return standard


def trend(werte: list) -> tuple[float, float]:
    """Lineare Regression y = a + b·x über x = 0 … n-1 → (a, b)."""
    n = len(werte)
    if n < 2:
        return (werte[0] if werte else 0.0), 0.0
    mx, my = (n - 1) / 2, sum(werte) / n
    s = sum((x - mx) ** 2 for x in range(n))
    b = sum((x - mx) * (v - my) for x, v in enumerate(werte)) / s
    return my - b * mx, b


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


def _reihenfarbe(v: dict, i: int, nr: int) -> tuple:
    fmt = (v["tf"].get(f"reihe_{nr}") or {}).get("fuell")
    if isinstance(fmt, dict) and fmt.get("farbe"):
        return _farbe(fmt["farbe"])
    return v["palette"][i % len(v["palette"])]


# ---- Wertachse ----------------------------------------------------------------------------------------------------------------
def _schritt(spanne: float) -> float:
    roh = spanne / 10.0 if spanne > 0 else 1.0
    exp = math.floor(math.log10(roh))
    for faktor in (1, 2, 5, 10):
        if faktor * 10 ** exp >= roh:
            return faktor * 10 ** exp
    return 10 ** (exp + 1)


def _skala(w: dict, werte: list, prozent: bool) -> tuple[float, float, float]:
    """(Minimum, Maximum, Intervall) der Wertachse: Angaben der Datei, sonst wie Word."""
    if prozent:
        return 0.0, 1.0, w.get("intervall") or 0.1
    lo = w.get("min") if w.get("min") is not None else min(0.0, min(werte, default=0.0))
    spitze = max(werte, default=1.0)
    spanne = spitze * 1.05 - lo
    schritt = w.get("intervall") or _schritt(spanne if spanne > 1e-9 else 1.0)           # nur Nullwerte: Spanne 1, nicht unendlich viele Teilstriche
    hi = w.get("max") if w.get("max") is not None else (math.ceil((spitze * 1.05 if spitze > 0 else 1.0) / schritt - 1e-9) * schritt)
    if hi <= lo:
        hi = lo + schritt
    return lo, hi, schritt


def _zahl(wert: float, stellen: int = 0) -> str:
    if stellen:
        return f"{wert:.{stellen}f}".replace(".", ",")
    return str(int(round(wert))) if abs(wert - round(wert)) < 1e-9 else f"{wert:g}".replace(".", ",")


# ---- Zeichenkontext ------------------------------------------------------------------------------------------------------------
class _Z:
    def __init__(self, b: RenderTarget, v: dict, r: Rect, geo):
        self.b, self.v, self.r, self.geo = b, v, r, geo
        stil = STILE[v["stil"]]
        self.grund, self.text, self.raster_an = _farbe(stil[1]), _farbe(stil[2]), stil[3]
        self.raster = _farbe(v["ex"].get("raster_farbe") or ("#3a4a6b" if v["stil"] in (3, 10) else "#d9d9d9"))
        self.achse = _hell(self.text, 0.45) if sum(self.text[:3]) < 400 else _dunkel(self.text, 0.35)
        self.schrift = FontSpec(_SCHRIFT, 9.5)
        self.ts = Style(color=self.text)
        self.tf = v["tf"]
        self.engine = getattr(b, "engine", None)
        if self.engine is None:
            from .textpfad import gemeinsame_engine
            self.engine = gemeinsame_engine()
        self.hinweise: list = []

    def textformat(self, schluessel: str):
        return (self.tf.get(schluessel) or {}).get("text")

    def tx(self, schluessel: str, t: str, rect: Rect, ausr: str = "center", valign: str = "center", box=None, raender=None) -> Rect:
        """Text nach dem Textformat des Teils ``schluessel`` (Größe, Winkel, Ränder, Effekte); → das Feld um den Text."""
        return DF.text_zeichnen(self.b, self.engine, t, rect, self.textformat(schluessel), self.schrift, self.text, ausr, valign, raender, box, self.v.get("objekt_dreh", 0.0))

    def melden(self, text: str) -> None:
        if text not in self.hinweise:
            self.hinweise.append(text)
        if hasattr(self.b, "hinweise") and text not in self.b.hinweise:
            self.b.hinweise.append(text)

    def breite(self, t: str, f=None) -> float:
        return self.b.text_bounds(t, Rect(0, 0, 3000, 200), f or self.schrift, "left", False).width

    def text_(self, t: str, rect: Rect, ausr="center", valign="center", f=None, farbe=None) -> None:
        self.b.draw_text_box(t, rect, f or self.schrift, Style(color=farbe or self.text), ausr, False, valign)

    def teil(self, schluessel: str, rect: Rect) -> None:
        if self.geo is not None:
            self.geo[schluessel] = rect


def _marke(z: _Z, x: float, y: float, farbe: tuple, r: float = 3.5) -> None:
    z.b.draw_ellipse(Point(x, y), r, r, Style(color=farbe, width=1, filled=True, outline=(255, 255, 255, 255)))


def _glatt(pts: list) -> list:
    """Geglättete Linie (Catmull-Rom) als Pfadanweisungen durch die Punkte."""
    if len(pts) < 3:
        return [("M", pts[0][0], pts[0][1])] + [("L", q[0], q[1]) for q in pts[1:]]
    ops = [("M", pts[0][0], pts[0][1])]
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(0, i - 1)], pts[i], pts[i + 1], pts[min(len(pts) - 1, i + 2)]
        ops.append(("C", p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6, p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, p2[0], p2[1]))
    return ops


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


# ---- Legende ------------------------------------------------------------------------------------------------------------------
def _eintraege(z: _Z) -> list:
    v = z.v
    if ist_kreis(v["art"]):
        return [(str(k), z.v["palette"][i % len(z.v["palette"])]) for i, k in enumerate(v["kat"])]
    if v["art"].startswith("kurs"):
        return []
    return [(str(n), _reihenfarbe(v, i, v["nummern"][i] if i < len(v["nummern"]) else i)) for i, n in enumerate(v["reihen"])]


def _legende(z: _Z, flaeche: Rect) -> Rect:
    v = z.v
    eintraege = _eintraege(z)
    if not v["legende"] or not eintraege:
        return flaeche
    pos = v["legende_pos"] if v["legende_pos"] in ("oben", "unten", "links", "rechts") else "unten"
    lfmt = z.tf.get("legende") or {}
    lf, lfarbe, _fx = DF.schrift(lfmt.get("text"), z.schrift, z.text)
    breiten = [z.engine.measure_text(n, lf) + 22 for n, _c in eintraege]
    zeile = max(20.0, z.engine.font_metrics(lf).line_spacing + 4)

    def box(rect: Rect) -> Rect:
        if any(lfmt.get(k) for k in ("fuell", "linie")) or DF.hat_effekte(lfmt):
            DF.teil_zeichnen(z.b, z.engine, rect, {k: x for k, x in lfmt.items() if k in ("fuell", "linie") or k in DF.FX_SCHLUESSEL}, z.grund)
        return rect

    def eintrag(n: str, c: tuple, x: float, y: float, w: float, h: float) -> None:
        z.b.draw_rect(Rect(x, y + h / 2 - 4, 8, 8), Style(color=c, width=0, filled=True))
        z.b.draw_text_box(n, Rect(x + 12, y, w - 12, h), lf, Style(color=lfarbe), "left", False, "center")
    if pos in ("oben", "unten"):
        h = zeile + 2
        y = flaeche.y + 2 if pos == "oben" else flaeche.bottom - h
        x = flaeche.x + (flaeche.width - sum(breiten)) / 2
        z.teil("legende", box(Rect(x, y, sum(breiten), h)))
        for i, (n, c) in enumerate(eintraege):
            eintrag(n, c, x, y, breiten[i], h)
            z.teil(f"legendeneintrag_{i}", Rect(x, y, breiten[i], h))
            x += breiten[i]
        return Rect(flaeche.x, flaeche.y + (h + 4 if pos == "oben" else 0), flaeche.width, flaeche.height - h - 4)
    br = max(breiten) + 8
    x = flaeche.x + 4 if pos == "links" else flaeche.right - br
    y0 = flaeche.y + (flaeche.height - len(eintraege) * zeile) / 2
    z.teil("legende", box(Rect(x, y0, br, len(eintraege) * zeile)))
    for i, (n, c) in enumerate(eintraege):
        eintrag(n, c, x, y0 + i * zeile, br, zeile)
        z.teil(f"legendeneintrag_{i}", Rect(x, y0 + i * zeile, br, zeile))
    return Rect(flaeche.x + (br + 6 if pos == "links" else 0), flaeche.y, flaeche.width - br - 6, flaeche.height)


# ---- Kartesisch (Säulen, Balken, Linien, Flächen, Punkt, Blase, Kombination) --------------------------------------------------
def _spezifikation(v: dict) -> list:
    """Je Reihe: (Art ``saeule``/``linie``/``flaeche``, gestapelt, Sekundärachse, Punkte, Linie, glatt, Blase)."""
    art, namen = v["art"], list(v["reihen"])
    kombi = v["kombi"]
    if art.startswith("kombi"):
        kombi = kombi or [("saeule", False)] * max(1, len(namen) - 1) + [("linie", art == "kombi_sekundaer")] * (len(namen) > 1)
        aus = []
        for i, _n in enumerate(namen):
            k, sek = kombi[i] if i < len(kombi) else ("saeule", False)
            grund = k.split("_")[0]
            aus.append((grund, k.endswith("gestapelt"), sek, k == "linie_punkte", True, False, False))
        return aus
    prozent = art.endswith("_100")
    gest = art.endswith("_gestapelt") or prozent
    if art.startswith(("saeule", "balken")):
        return [("saeule", gest, False, False, False, False, False)] * len(namen)
    if art.startswith("linie"):
        return [("linie", gest, False, "punkte" in art, True, art == "linie_glatt", False)] * len(namen)
    if art.startswith("flaeche"):
        return [("flaeche", gest, False, False, True, False, False)] * len(namen)
    if art.startswith("punkte"):
        gerade, glatt = "gerade" in art or "glatt" in art, "glatt" in art
        return [("linie", False, False, "blase" not in art, gerade, glatt, "blase" in art)] * len(namen)
    return [("saeule", False, False, False, False, False, False)] * len(namen)


def _printf(muster: str, wert: float) -> str:
    try:
        return (muster % wert).replace(".", ",")
    except (TypeError, ValueError):
        return _zahl(wert)


def _kartesisch(z: _Z, flaeche: Rect) -> None:
    v, b = z.v, z.b
    art, kat, reihen = v["art"], v["kat"], v["reihen"]
    namen = list(reihen)
    spez = _spezifikation(v)
    waagrecht = art.startswith("balken")
    prozent = art.endswith("_100") and not art.startswith("kombi")
    el, wert = v["el"], dict(v["wert"])
    n = len(kat)
    wk, kk = ("achse_horizontal", "achse_vertikal") if waagrecht else ("achse_vertikal", "achse_horizontal")          # Wert- und Rubrikenachse
    wo, ko = (z.tf.get(wk) or {}).get("achse") or {}, (z.tf.get(kk) or {}).get("achse") or {}
    for schl in ("min", "max", "intervall"):                                                                           # Optionen der Wertachse
        if wo.get(schl) is not None:
            wert[schl] = wo[schl]
    w_umkehr, k_umkehr = bool(wo.get("umkehren")), bool(ko.get("umkehren"))
    w_labels, k_labels = wo.get("beschriftung") != "keine", ko.get("beschriftung") != "keine"

    def nr(i: int) -> int:
        return v["nummern"][i] if i < len(v["nummern"]) else i

    def rf(i: int) -> dict:
        return z.tf.get(f"reihe_{nr(i)}") or {}

    def reihe(i: int) -> list:
        w = reihen[namen[i]]
        return [(w[j] if j < len(w) else 0.0) for j in range(n)]
    werte = [reihe(i) for i in range(len(namen))]
    stapel = {}
    for i, s in enumerate(spez):                                                    # gestapelte Reihen: je (Art, Achse) ein Stapel
        if s[1]:
            stapel.setdefault((s[0], s[2]), []).append(i)
    unten, oben = {}, {}
    for schl, idx in stapel.items():
        lauf = [0.0] * n
        for i in idx:
            summen = [sum(werte[k][j] for k in idx) or 1.0 for j in range(n)]
            w = [werte[i][j] / summen[j] for j in range(n)] if prozent else werte[i]
            unten[i] = list(lauf)
            lauf = [lauf[j] + w[j] for j in range(n)]
            oben[i] = list(lauf)
    for i, s in enumerate(spez):
        if i not in oben:
            oben[i] = list(werte[i])
            unten[i] = [0.0] * n
    sek = any(s[2] for s in spez)
    prim_w = [x for i, s in enumerate(spez) if not s[2] for x in oben[i] + unten[i]] or [1.0]
    sek_w = [x for i, s in enumerate(spez) if s[2] for x in oben[i] + unten[i]] or [1.0]
    skalen = [_skala(wert, prim_w, prozent), _skala({}, sek_w, False)]
    stellen = int(wert.get("stellen") or 0)
    muster = wo.get("format")

    def beschr(m: float, k: int) -> str:
        if muster and k == 0 and not prozent:
            return _printf(muster, m)
        return (_zahl(m * 100) + " %") if prozent else _zahl(m, stellen if k == 0 else 0)
    lo, hi, schritt = skalen[0]
    marken = [lo + i * schritt for i in range(max(1, int(round((hi - lo) / schritt))) + 1)]
    texte = [beschr(m, 0) for m in marken]
    kat_breit = max((z.breite(str(k)) for k in kat), default=10.0)
    wb = max((z.breite(t) for t in texte), default=10.0)
    sek_b = max((z.breite(beschr(m, 1)) for m in [skalen[1][0] + i * skalen[1][2] for i in range(int(round((skalen[1][1] - skalen[1][0]) / skalen[1][2])) + 1)]), default=0.0) + 10 if sek else 0.0
    achsen = bool(el.get("achsen"))
    waagr_winkel = abs(DF.textwinkel(z.textformat("achse_horizontal")))
    links = (8.0 + ((kat_breit if k_labels else 0.0) if waagrecht else (wb if w_labels else 0.0)) + 6) if achsen else 10.0
    if el.get("achsentitel"):
        links += 18
    unten_h = (8.0 + 14 + 4 + (16 if waagr_winkel > 20 else 0)) if achsen else 8.0
    if el.get("achsentitel"):
        unten_h += 16
    tabelle = TABELLE_ZEILE * (len(namen) + 1) if el.get("datentabelle") and not waagrecht else 0.0
    p = Rect(flaeche.x + links, flaeche.y + 8, flaeche.width - links - 14 - sek_b, flaeche.height - unten_h - tabelle - 8)
    if p.width < 20 or p.height < 20:
        return
    z.teil("zeichnungsbereich", p)
    zf = z.tf.get("zeichnungsbereich") or {}
    if any(zf.get(k) for k in ("fuell", "linie")) or DF.hat_effekte(zf):
        DF.teil_zeichnen(b, z.engine, p, {k: x for k, x in zf.items() if k in ("fuell", "linie") or k in DF.FX_SCHLUESSEL}, z.grund)

    def pos(w: float, k: int = 0) -> float:
        l_, h_, _s = skalen[k]
        a = (w - l_) / (h_ - l_)
        return 1.0 - a if (w_umkehr and k == 0) else a

    def y_von(w: float, k: int = 0) -> float:
        return p.bottom - pos(w, k) * p.height

    def idx(j: int) -> int:
        return n - 1 - j if k_umkehr else j

    gruppe = (p.height if waagrecht else p.width) / max(1, n)
    # Gitter (Haupt- und Nebenlinien) und Wertachse
    gitter_rects = []
    gf = z.tf.get("gitter_haupt") or {}
    gstile = DF.linie_stile(gf.get("linie"), z.raster, 1.0) if z.raster_an else []
    neben = wo.get("neben")
    if el.get("gitter") and z.raster_an and neben and float(neben) > 0 and (hi - lo) / float(neben) < 200:
        m = lo + float(neben)
        while m < hi - 1e-9:
            a = pos(m)
            if waagrecht:
                b.draw_line(Point(p.x + a * p.width, p.y), Point(p.x + a * p.width, p.bottom), Style(color=_hell(z.raster, 0.5), width=0.75))
            else:
                b.draw_line(Point(p.x, p.bottom - a * p.height), Point(p.right, p.bottom - a * p.height), Style(color=_hell(z.raster, 0.5), width=0.75))
            m += float(neben)
    for m, t in zip(marken, texte):
        a = pos(m)
        if waagrecht:
            x = p.x + a * p.width
            if el.get("gitter"):
                for st in gstile:
                    b.draw_line(Point(x, p.y), Point(x, p.bottom), st)
            gitter_rects.append(Rect(x - 3, p.y, 6, p.height))
            if achsen and w_labels:
                z.tx(wk, t, Rect(x - 25, p.bottom + 4, 50, 14), "center", "top")
        else:
            y = p.bottom - a * p.height
            if el.get("gitter"):
                for st in gstile:
                    b.draw_line(Point(p.x, y), Point(p.right, y), st)
            gitter_rects.append(Rect(p.x, y - 3, p.width, 6))
            if achsen and w_labels:
                z.tx(wk, t, Rect(flaeche.x + (22 if el.get("achsentitel") else 4), y - 7, wb + 4, 14), "right")
    z.teil("gitter_haupt", p)
    z.teil("gitter_linien", gitter_rects)
    if sek:
        s0, s1, ss = skalen[1]
        for i in range(int(round((s1 - s0) / ss)) + 1):
            m = s0 + i * ss
            z.text_(beschr(m, 1), Rect(p.right + 4, y_von(m, 1) - 7, sek_b, 14), "left")
        b.draw_line(Point(p.right, p.y), Point(p.right, p.bottom), Style(color=z.achse, width=1))
    for j, k in enumerate(kat):                                                    # Rubrikenachse
        mitte = (p.bottom - (idx(j) + 0.5) * gruppe) if waagrecht else (p.x + (idx(j) + 0.5) * gruppe)
        if not achsen or not k_labels:
            continue
        if waagrecht:
            z.tx(kk, str(k), Rect(flaeche.x + 4, mitte - 7, kat_breit + 4, 14), "right")
        else:
            z.tx(kk, str(k), Rect(mitte - gruppe / 2, p.bottom + 4, gruppe, 14), "center", "top")
    z.teil("achse_horizontal", Rect(p.x, p.bottom, p.width, unten_h))
    z.teil("achse_vertikal", Rect(p.x - links, p.y, links, p.height))
    if el.get("achsentitel"):
        z.text_("Werte" if waagrecht else "Rubriken", Rect(p.x, p.bottom + unten_h - 16, p.width, 16), "center", "top")
        b.push_state(translate=Point(flaeche.x + 10, p.y + p.height / 2), rotate=-90)
        z.text_("Rubriken" if waagrecht else "Werte", Rect(-p.height / 2, -8, p.height, 16), "center")
        b.pop_state()
    # luecke: Angabe der ersten Reihe mit eigener Lücke, sonst des Diagramms
    luecke_pro = next((float((rf(i).get("reihe") or {}).get("luecke")) for i in range(len(namen)) if (rf(i).get("reihe") or {}).get("luecke") is not None), None)
    luecke = float(luecke_pro if luecke_pro is not None else (v["luecke"] if v["luecke"] is not None else 150.0)) / 100.0
    saeulen = [i for i, s in enumerate(spez) if s[0] == "saeule"]
    gruppierte = [i for i in saeulen if not spez[i][1]]
    stapel_achsen = sorted({spez[i][2] for i in saeulen if spez[i][1]})
    spalten = (len(gruppierte) + len(stapel_achsen)) or 1
    breite = gruppe / (spalten + luecke)
    # Flächen und Säulen zuerst, dann Linien und Marken (wie in Office)
    reihenfolge = sorted(range(len(namen)), key=lambda i: {"flaeche": 0, "saeule": 1, "linie": 2}[spez[i][0]])
    gemerkt = {}
    for i in reihenfolge:
        art_i, gest, sk, punkte, linie, glatt, blase = spez[i]
        k = 1 if sk else 0
        fmt = rf(i)
        opt = fmt.get("reihe") or {}
        glatt = bool(opt["glatt"]) if "glatt" in opt else glatt
        punkte = bool(opt["punkte"]) if "punkte" in opt else punkte
        farbe = _reihenfarbe(v, i, nr(i))
        gemerkt[i] = []
        if art_i == "saeule":
            spalte = gruppierte.index(i) if not gest else len(gruppierte) + stapel_achsen.index(sk)
            versatz = (gruppe - breite * spalten) / 2 + spalte * breite
            balken = []
            for j in range(n):
                a0, a1 = pos(min(unten[i][j], oben[i][j]), k), pos(max(unten[i][j], oben[i][j]), k)
                if not gest and lo > 0:
                    a0 = 0.0
                if w_umkehr and k == 0:
                    a0, a1 = min(a0, a1), max(a0, a1)
                jj = idx(j)
                if waagrecht:
                    rect = Rect(p.x + a0 * p.width, p.bottom - jj * gruppe - versatz - breite, (a1 - a0) * p.width, breite)
                else:
                    rect = Rect(p.x + jj * gruppe + versatz, p.bottom - a1 * p.height, breite, (a1 - a0) * p.height)
                if DF.hat_effekte(fmt):
                    DF.effekte_hinter(b, rect, fmt, farbe)
                st = DF.fuell_style(fmt.get("fuell"), rect) if "fuell" in fmt else Style(color=farbe, width=0, filled=True)
                if st is not None:
                    b.draw_rect(rect, st)
                if "linie" in fmt:
                    DF.rahmen_zeichnen(b, rect, fmt["linie"])
                balken.append(rect)
                gemerkt[i].append((rect.x + rect.width / 2, rect.y, werte[i][j]) if not waagrecht else (rect.right, rect.y + rect.height / 2, werte[i][j]))
            z.teil(f"balken_{nr(i)}", balken)
            z.teil(f"reihe_{nr(i)}", Rect(p.x, min((r_.y for r_ in balken), default=p.y), p.width, p.height) if balken else p)
            if fmt.get("weich"):
                z.melden("Weiche Kanten an Diagrammreihen werden in dieser Ausgabe nicht dargestellt.")
        else:
            pts = [(p.x + (idx(j) + 0.5) * gruppe, y_von(oben[i][j], k)) for j in range(n)]
            pts_sortiert = sorted(pts)
            gemerkt[i] = [(pts[j][0], pts[j][1], werte[i][j]) for j in range(n)]
            lf = fmt.get("linie")
            lstil = DF.linie_stile(lf, farbe, 2.5)
            lfarbe = lstil[0].color if lstil else farbe
            lbreite = lstil[0].width if lstil else 2.5
            if art_i == "flaeche":
                ops = [("M", pts_sortiert[0][0], y_von(unten[i][0] if gest else max(lo, 0.0), k))] + [("L", q[0], q[1]) for q in pts_sortiert]
                ops += [("L", pts_sortiert[-1][0], y_von(unten[i][-1] if gest else max(lo, 0.0), k)), ("Z",)]
                bb = Rect(p.x, min(q[1] for q in pts), p.width, max(1.0, p.bottom - min(q[1] for q in pts)))
                fst = DF.fuell_style(fmt.get("fuell"), bb) if "fuell" in fmt else Style(color=(farbe[0], farbe[1], farbe[2], 190), width=0, filled=True)
                if fst is not None:
                    b.draw_path(ops, fst, True, True)
                if len(pts) > 1:
                    b.draw_path([("M", pts_sortiert[0][0], pts_sortiert[0][1])] + [("L", q[0], q[1]) for q in pts_sortiert[1:]], Style(color=lfarbe, width=1.5 if not lf else lbreite, join="round"), True, True)
            elif linie and len(pts) > 1:
                ops = _glatt(pts_sortiert) if glatt else [("M", pts_sortiert[0][0], pts_sortiert[0][1])] + [("L", q[0], q[1]) for q in pts_sortiert[1:]]
                if DF.hat_effekte(fmt) and not blase:
                    bbox = Rect(p.x, min(q[1] for q in pts), p.width, max(1.0, max(q[1] for q in pts) - min(q[1] for q in pts)))
                    if fmt.get("schatten") or fmt.get("leuchten"):
                        sch = DF.effekt(fmt, "schatten")
                        gl = DF.effekt(fmt, "leuchten")
                        if sch:
                            a_ = math.radians(float(sch.get("winkel", 45)))
                            b.draw_shadow(ops, DF._mit_deckkraft(_farbe(sch.get("farbe")), sch.get("transparenz", 60)), float(sch.get("weich", 4)) * DF.PX * 0.6,
                                          math.cos(a_) * float(sch.get("abstand", 4)) * DF.PX, math.sin(a_) * float(sch.get("abstand", 4)) * DF.PX)
                        if gl:
                            b.draw_shadow(ops, DF._mit_deckkraft(_farbe(gl.get("farbe")), gl.get("transparenz", 60)), float(gl.get("groesse", 8)) * DF.PX, 0.0, 0.0)
                    if fmt.get("reflektion") or fmt.get("d3") or fmt.get("weich"):
                        z.melden("Spiegelung, 3D-Format und weiche Kanten an Linienreihen werden in dieser Ausgabe nicht dargestellt.")
                stile = lstil or [Style(color=farbe, width=2.5)]
                gesamt_b = float((lf or {}).get("breite", 0.75)) * DF.PX
                for st, off in zip(stile, DF._versatz(lf)):
                    b.draw_path(ops, dataclasses_ersetzen(st, cap="round" if st.cap == "flat" and not lf else st.cap, join="round" if not lf else st.join), True, True)
                if lf:                                                                  # Pfeile am Anfang und am Ende der Linie
                    gr_a = lf.get("pfeil_groesse_anfang", lf.get("pfeil_groesse", 1.0))
                    gr_e = lf.get("pfeil_groesse_ende", lf.get("pfeil_groesse", 1.0))
                    if len(pts_sortiert) > 1:
                        DF.pfeil_zeichnen(b, pts_sortiert[-1], pts_sortiert[-2], str(lf.get("pfeil_ende") or ""), gr_e, lfarbe, lbreite)
                        DF.pfeil_zeichnen(b, pts_sortiert[0], pts_sortiert[1], str(lf.get("pfeil_anfang") or ""), gr_a, lfarbe, lbreite)
            if blase:
                maxw = max((abs(x) for x in werte[i]), default=1.0) or 1.0
                for (x, y), w in zip(pts, werte[i]):
                    rr = 4 + 14 * math.sqrt(abs(w) / maxw)
                    b.draw_ellipse(Point(x, y), rr, rr, Style(color=(farbe[0], farbe[1], farbe[2], 170), width=1, filled=True, outline=farbe))
            elif punkte or (not linie and art_i == "linie"):
                for x, y in pts:
                    _marke(z, x, y, farbe)
            z.teil(f"reihe_{nr(i)}", Rect(p.x, min(q[1] for q in pts), p.width, max(1.0, max(q[1] for q in pts) - min(q[1] for q in pts))))
    # Trendlinien, Fehlerindikatoren, Datenbeschriftungen
    if el.get("trendlinie") and not waagrecht:
        for i in range(len(namen)):
            a, s_ = trend(werte[i])
            farbe = _reihenfarbe(v, i, nr(i))
            k = 1 if spez[i][2] else 0
            x0, x1 = p.x + 0.5 * gruppe, p.x + (n - 0.5) * gruppe
            b.draw_line(Point(x0, y_von(a, k)), Point(x1, y_von(a + s_ * (n - 1), k)), Style(color=farbe, width=1.5, dash="dash"))
    if el.get("fehlerindikatoren"):
        for i in range(len(namen)):
            peak = max((abs(x) for x in werte[i]), default=1.0) * FEHLER_ANTEIL
            for x, y, w in gemerkt.get(i, []):
                if waagrecht:
                    continue
                k = 1 if spez[i][2] else 0
                d_ = abs(y_von(w + peak, k) - y_von(w, k))
                st = Style(color=z.text, width=1.4)
                b.draw_line(Point(x, y - d_), Point(x, y + d_), st)
                b.draw_line(Point(x - 4, y - d_), Point(x + 4, y - d_), st)
                b.draw_line(Point(x - 4, y + d_), Point(x + 4, y + d_), st)
    if v["labels"]:
        felder = []
        for i in range(len(namen)):
            for x, y, w in gemerkt.get(i, []):
                if waagrecht:
                    felder.append(z.tx("datenbeschriftung", _zahl(w, stellen), Rect(x + 2, y - 7, 40, 14), "left"))
                else:
                    felder.append(z.tx("datenbeschriftung", _zahl(w, stellen), Rect(x - 25, y - 17, 50, 14), "center", "top"))
        if felder:
            z.teil("datenbeschriftung", Rect(min(f.x for f in felder), min(f.y for f in felder), max(f.right for f in felder) - min(f.x for f in felder), max(f.bottom for f in felder) - min(f.y for f in felder)))
    # Achsenlinien (Format der Achsenteile)
    for schl, (a_, b_) in ((wk, ((p.x, p.y), (p.x, p.bottom))), (kk, ((p.x, p.bottom), (p.right, p.bottom)))):
        stile = DF.linie_stile((z.tf.get(schl) or {}).get("linie"), z.achse, 1.0)
        for st in stile:
            b.draw_line(Point(*a_), Point(*b_), st)
    if tabelle:                                                                    # Datentabelle unter der Rubrikenachse
        ty = p.bottom + unten_h - 4
        namens_b = min(p.width * 0.3, max([z.breite(nm) for nm in namen] + [30.0]) + 26)
        sb = (p.width + links - namens_b - 8) / max(1, n)
        x0 = flaeche.x + 4
        for j, k in enumerate(kat):
            z.text_(str(k), Rect(x0 + namens_b + j * sb, ty, sb, TABELLE_ZEILE), "center")
        for i, nm in enumerate(namen):
            y = ty + (i + 1) * TABELLE_ZEILE
            b.draw_line(Point(x0, y), Point(x0 + namens_b + n * sb, y), Style(color=z.raster, width=1))
            b.draw_rect(Rect(x0 + 4, y + 6, 8, 8), Style(color=_reihenfarbe(v, i, nr(i)), width=0, filled=True))
            z.text_(nm, Rect(x0 + 17, y, namens_b - 19, TABELLE_ZEILE), "left")
            for j in range(n):
                z.text_(_zahl(werte[i][j]), Rect(x0 + namens_b + j * sb, y, sb, TABELLE_ZEILE), "center")


def dataclasses_ersetzen(st: Style, **kw) -> Style:
    import dataclasses
    return dataclasses.replace(st, **kw)


# ---- Kreis ----------------------------------------------------------------------------------------------------------------------
def _sektor(b, mx, my, rx, ry, w0, w1, farbe, innen: float = 0.0, tiefe: float = 0.0) -> None:
    n = max(2, int(abs(w1 - w0) / math.radians(3)) + 1)
    aussen = [(mx + rx * math.cos(w0 + (w1 - w0) * k / n), my + ry * math.sin(w0 + (w1 - w0) * k / n)) for k in range(n + 1)]
    if innen > 0:
        ein = [(mx + rx * innen * math.cos(w1 - (w1 - w0) * k / n), my + ry * innen * math.sin(w1 - (w1 - w0) * k / n)) for k in range(n + 1)]
        ops = [("M", *aussen[0])] + [("L", *q) for q in aussen[1:]] + [("L", *q) for q in ein] + [("Z",)]
    else:
        ops = [("M", mx, my)] + [("L", *q) for q in aussen] + [("Z",)]
    b.draw_path(ops, Style(color=farbe, width=1, filled=True, outline=(255, 255, 255, 255)), True, True)


def _kreis(z: _Z, f: Rect) -> None:
    v, b = z.v, z.b
    art, kat = v["art"], v["kat"]
    werte = [max(0.0, w) for w in v["reihen"][list(v["reihen"])[0]]]
    werte += [0.0] * (len(kat) - len(werte))
    farben = v["palette"]
    von_kreis = art in ("kreis_von_kreis", "kreis_balken")
    haupt = f
    if von_kreis:
        haupt = Rect(f.x, f.y, f.width * 0.58, f.height)
    plus = (len(kat) > 3) if von_kreis else False
    rest = werte[-min(3, max(2, len(werte) // 3)):] if von_kreis and len(werte) > 2 else []
    hauptwerte = (werte[:len(werte) - len(rest)] + [sum(rest)]) if von_kreis else werte
    summe = sum(hauptwerte) or 1.0
    schief = 0.62 if art == "kreis_3d" else 1.0
    radius = min(haupt.width, haupt.height / schief) / 2 - 6
    mx, my = haupt.x + haupt.width / 2, haupt.y + haupt.height / 2 - (8 if schief < 1 else 0)
    if art == "kreis_3d":
        for t in range(14, 0, -1):                                                      # Tiefe: abgedunkelte Scheiben unter dem Kreis
            w0 = -math.pi / 2
            for i, w in enumerate(hauptwerte):
                if w <= 0:
                    continue
                s = 2 * math.pi * w / summe
                _sektor(b, mx, my + t, radius, radius * schief, w0, w0 + s, _dunkel(farben[i % len(farben)], 0.35))
                w0 += s
    w0 = -math.pi / 2
    mitten = []
    for i, w in enumerate(hauptwerte):
        if w <= 0:
            mitten.append(None)
            continue
        s = 2 * math.pi * w / summe
        farbe = farben[i % len(farben)] if not (von_kreis and i == len(hauptwerte) - 1) else _hell(farben[(len(farben) - 1)], 0.3)
        _sektor(b, mx, my, radius, radius * schief, w0, w0 + s, farbe, 0.5 if art == "ring" else 0.0)
        mitten.append((w0 + s / 2, w / summe))
        w0 += s
    z.teil("zeichnungsbereich", Rect(mx - radius, my - radius * schief, 2 * radius, 2 * radius * schief))
    if v["labels"]:
        for m in mitten:
            if m is not None:
                w, anteil = m
                z.text_(f"{anteil * 100:.0f} %".replace(".", ","), Rect(mx + math.cos(w) * radius * 0.7 - 25, my + math.sin(w) * radius * schief * 0.7 - 7, 50, 14), "center")
    if von_kreis and rest:
        sub = Rect(f.x + f.width * 0.62, f.y, f.width * 0.38, f.height)
        sm = sum(rest) or 1.0
        if art == "kreis_balken":
            h = min(sub.height * 0.7, 160.0)
            y = sub.y + (sub.height - h) / 2
            lauf = 0.0
            for i, w in enumerate(rest):
                hh = h * w / sm
                b.draw_rect(Rect(sub.x + 10, y + lauf, 26, hh), Style(color=farben[(len(werte) - len(rest) + i) % len(farben)], width=1, filled=True, outline=(255, 255, 255, 255)))
                lauf += hh
        else:
            rr = min(sub.width, sub.height) / 2 - 6
            w0 = -math.pi / 2
            for i, w in enumerate(rest):
                s = 2 * math.pi * w / sm
                _sektor(b, sub.x + sub.width / 2, sub.y + sub.height / 2, rr, rr, w0, w0 + s, farben[(len(werte) - len(rest) + i) % len(farben)])
                w0 += s


# ---- Netz (Radar) -------------------------------------------------------------------------------------------------------------
def _netz(z: _Z, f: Rect) -> None:
    v, b = z.v, z.b
    kat, reihen = v["kat"], v["reihen"]
    namen = list(reihen)
    n = len(kat)
    alle = [w for nm in namen for w in reihen[nm]]
    lo, hi, schritt = _skala(v["wert"], alle, False)
    radius = min(f.width, f.height) / 2 - 24
    mx, my = f.x + f.width / 2, f.y + f.height / 2
    z.teil("zeichnungsbereich", Rect(mx - radius, my - radius, 2 * radius, 2 * radius))
    ringe = max(1, int(round((hi - lo) / schritt)))
    for g in range(1, ringe + 1):
        rr = radius * g / ringe
        ops = [("M", mx + rr * math.cos(-math.pi / 2), my + rr * math.sin(-math.pi / 2))] + [("L", mx + rr * math.cos(-math.pi / 2 + 2 * math.pi * k / n), my + rr * math.sin(-math.pi / 2 + 2 * math.pi * k / n)) for k in range(1, n)] + [("Z",)]
        b.draw_path(ops, Style(color=z.raster, width=1), True, True)
    for k in range(n):
        w = -math.pi / 2 + 2 * math.pi * k / n
        b.draw_line(Point(mx, my), Point(mx + radius * math.cos(w), my + radius * math.sin(w)), Style(color=z.raster, width=1))
        z.text_(str(kat[k]), Rect(mx + (radius + 14) * math.cos(w) - 30, my + (radius + 10) * math.sin(w) - 7, 60, 14), "center")
    for i, nm in enumerate(namen):
        farbe = _reihenfarbe(v, i, v["nummern"][i] if i < len(v["nummern"]) else i)
        pts = [(mx + radius * (reihen[nm][k] - lo) / (hi - lo) * math.cos(-math.pi / 2 + 2 * math.pi * k / n),
                my + radius * (reihen[nm][k] - lo) / (hi - lo) * math.sin(-math.pi / 2 + 2 * math.pi * k / n)) for k in range(n) if k < len(reihen[nm])]
        if len(pts) < 2:
            continue
        ops = [("M", *pts[0])] + [("L", *q) for q in pts[1:]] + [("Z",)]
        if v["art"] == "netz_gefuellt":
            b.draw_path(ops, Style(color=(farbe[0], farbe[1], farbe[2], 120), width=2, filled=True, outline=farbe), True, True)
        else:
            b.draw_path(ops, Style(color=farbe, width=2.5, join="round"), True, True)
        if v["art"] == "netz_punkte":
            for x, y in pts:
                _marke(z, x, y, farbe)


# ---- Kurs ---------------------------------------------------------------------------------------------------------------------
def _kurs(z: _Z, f: Rect) -> None:
    v, b = z.v, z.b
    kat, reihen = v["kat"], v["reihen"]
    art = v["art"]

    def holen(name: str) -> list:
        return reihen.get(name) or [0.0] * len(kat)
    hoch, tief, schluss = holen("Höchst"), holen("Tiefst"), holen("Schluss")
    eroeff = holen("Eröffnung") if art in ("kurs_ohts", "kurs_vohts") else None
    volumen = holen("Volumen") if art in ("kurs_vhts", "kurs_vohts") else None
    n = len(kat)
    lo, hi, schritt = _skala({}, hoch + tief + schluss, False)
    lo = min(lo, min(tief + schluss) if tief else lo)
    unten_h = 24.0
    vol_h = f.height * 0.22 if volumen else 0.0
    p = Rect(f.x + 40, f.y + 8, f.width - 54, f.height - unten_h - vol_h - 12)
    z.teil("zeichnungsbereich", p)
    ringe = max(1, min(100, int(round((hi - lo) / schritt))))
    for g in range(ringe + 1):
        y = p.bottom - p.height * g / ringe
        b.draw_line(Point(p.x, y), Point(p.right, y), Style(color=z.raster, width=1))
        z.text_(_zahl(lo + g * (hi - lo) / ringe), Rect(f.x + 2, y - 7, 34, 14), "right")
    gruppe = p.width / max(1, n)
    for j in range(n):
        x = p.x + (j + 0.5) * gruppe
        y_h, y_t = p.bottom - (hoch[j] - lo) / (hi - lo) * p.height, p.bottom - (tief[j] - lo) / (hi - lo) * p.height
        y_s = p.bottom - (schluss[j] - lo) / (hi - lo) * p.height
        b.draw_line(Point(x, y_h), Point(x, y_t), Style(color=z.text, width=1.5))
        if eroeff is not None:
            y_e = p.bottom - (eroeff[j] - lo) / (hi - lo) * p.height
            steigt = schluss[j] >= eroeff[j]
            b.draw_rect(Rect(x - gruppe * 0.22, min(y_e, y_s), gruppe * 0.44, max(1.0, abs(y_s - y_e))), Style(color=(255, 255, 255, 255) if steigt else z.text, width=1, filled=True, outline=z.text))
        else:
            b.draw_line(Point(x, y_s), Point(x + gruppe * 0.2, y_s), Style(color=z.text, width=1.5))
        z.text_(str(kat[j]), Rect(x - gruppe / 2, p.bottom + 4, gruppe, 14), "center", "top")
    if volumen:
        top = p.bottom + unten_h
        vmax = max(volumen) or 1.0
        for j in range(n):
            hh = vol_h * volumen[j] / vmax
            b.draw_rect(Rect(p.x + (j + 0.5) * gruppe - gruppe * 0.3, top + vol_h - hh, gruppe * 0.6, hh), Style(color=v["palette"][0], width=0, filled=True))
    b.draw_line(Point(p.x, p.bottom), Point(p.right, p.bottom), Style(color=z.achse, width=1))
