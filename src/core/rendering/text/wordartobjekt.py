"""WordArt-Objekte mit Text ohne Qt: mehrere Zeilen und Läufe mit eigenem Format (Fett, Kursiv, hoch/tief, Unterstreichung, Hervorhebung, Füllung, Kontur, Schrift, Größe), Listen,
Ausrichtung (auch Block und verteilt), Zeilenabstand, Einzug, Leuchten, Schatten und Spiegelung; gesetzt mit der Textsatz-Engine, gezeichnet über Glyphenpfade.

``wordart_rgba`` liefert das fertige Bild (RGBA); die Textrichtung (senkrecht, gedreht) wendet der Aufrufer am Bild an."""
from __future__ import annotations

import math

from core.geometrie import Point, Rect
from core.textsatz.engine import FontSpec
from core.rendering.text import zeichenzusatz as Z
from core.rendering.ausgabe.backend import LinearGradient, Style, rgba

SS = 2                                                                # Zeichnen in doppelter Auflösung (scharf auch bei Zoom)
PX = 96.0 / 72.0
ZEICHEN_SCHLUESSEL = ("fett", "kursiv", "unter", "unterfarbe", "durch", "hoch", "tief", "hervor", "fuell", "kontur", "schrift", "pt")
_PUNKTE = {"disc": "●", "circle": "○", "square": "■"}


# ---- Läufe und Listen (reine Datenhilfen) -----------------------------------------------------------------------------------
def nummer_text(stil: str, n: int) -> str:
    """Die Zahl ``n`` in der Zahlenart ``stil`` (dezimal, klein, gross, roem_klein, roem_gross)."""
    if stil in ("klein", "gross"):
        s = ""
        while n > 0:
            n, r = divmod(n - 1, 26)
            s = chr(97 + r) + s
        return s if stil == "klein" else s.upper()
    if stil in ("roem_klein", "roem_gross"):
        s = ""
        for w, z in ((1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"), (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")):
            while n >= w:
                s += z
                n -= w
        return s if stil == "roem_klein" else s.upper()
    return str(n)


def listenmarken(liste, anzahl: int) -> list[str]:
    """Die Marke jeder Zeile (mit Leerzeichen dahinter): Aufzählungszeichen oder Nummer; leer: keine Liste."""
    if not liste:
        return [""] * anzahl
    if isinstance(liste, str):                                       # alte Schreibweise
        liste = {"stil": "disc"} if liste == "punkt" else {"stil": "dezimal", "praefix": "", "suffix": ".", "start": 1}
    if liste.get("ebenen"):
        z = liste["ebenen"][0].get("format") or "•"
        return [f"{z} "] * anzahl
    stil = liste.get("stil", "disc")
    if stil in _PUNKTE:
        return [_PUNKTE[stil] + " "] * anzahl
    start = int(liste.get("start", 1))
    return [f"{liste.get('praefix', '')}{nummer_text(stil, start + i)}{liste.get('suffix', '')} " for i in range(anzahl)]


def anzeige_laeufe(d: dict) -> list[dict]:
    """Die Läufe, die das Objekt zeigt: ``[{"t": Text, <Zeichenschlüssel>…}]`` (Schlüssel, die fehlen, gelten für das ganze Objekt)."""
    if "gezeigt" in d:
        return d.get("gezeigt_laeufe") or [{"t": d["gezeigt"]}]
    return d.get("laeufe") or [{"t": d.get("text", "")}]


def laeufe_text(laeufe: list[dict]) -> str:
    return "".join(r["t"] for r in laeufe)


def zeilen_laeufe(laeufe: list[dict]) -> list[list[dict]]:
    """Läufe in Zeilen (Absätze) teilen."""
    zeilen: list[list[dict]] = [[]]
    for r in laeufe:
        for i, t in enumerate(r["t"].split("\n")):
            if i:
                zeilen.append([])
            if t:
                zeilen[-1].append({**r, "t": t})
    return zeilen


# ---- Satz ---------------------------------------------------------------------------------------------------------------------
def _stil(d: dict, pt: float, vorlagen) -> tuple:
    """Füllung, Kontur, Konturbreite und Schatten aus Vorlage und Objektangaben."""
    _n, f1, f2, kontur, kb, schatten = vorlagen[int(d["vorlage"])]
    if "fuell" in d:
        f1 = f2 = d["fuell"] or None
    if "kontur" in d:
        kontur = d["kontur"] or None
        kb = float(d.get("kontur_breite", 1.5)) * 96 / 72 / max(1.0, pt / 36) if kontur else 0
    elif "kontur_breite" in d and kontur:
        kb = float(d["kontur_breite"]) * 96 / 72 / max(1.0, pt / 36)
    return f1, f2, kontur, kb, schatten


def _format(d: dict, r: dict) -> dict:
    return {k: r.get(k, d.get(k)) for k in ZEICHEN_SCHLUESSEL}


def _schrift(e: dict, pt: float) -> FontSpec:
    gr = float(e["pt"] or pt)
    if e["hoch"] or e["tief"]:
        gr *= 0.6
    return FontSpec(e["schrift"] or "Liberation Sans", gr, 700 if (e["fett"] is None or e["fett"]) else 400, bool(e["kursiv"]))


class _Satz:
    def __init__(self, engine, d: dict, laeufe: list, pt: float):
        self.engine = engine
        zeilen = zeilen_laeufe(laeufe) or [[]]
        self.marken = listenmarken(d.get("liste"), len(zeilen))
        self.basis = _format(d, {})
        self.segmente = []
        for m_, zl in zip(self.marken, zeilen):
            seg = ([(m_, self.basis)] if m_ else []) + [(r["t"], _format(d, r)) for r in zl]
            self.segmente.append([(t, e, _schrift(e, pt)) for t, e in seg])
        f0 = _schrift(self.basis, pt)
        self.einzug = 24.0 * int(d.get("einzug") or 0)
        self.hoehen = [max([engine.font_metrics(f).line_spacing for _t, _e, f in sg] or [engine.font_metrics(f0).line_spacing]) for sg in self.segmente]
        self.asz = [max([engine.font_metrics(f).ascent for _t, _e, f in sg] or [engine.font_metrics(f0).ascent]) for sg in self.segmente]
        self.faktor = float(d.get("zeilenabstand") or 1.0)
        self.breiten = [sum(engine.measure_text(t, f) for t, _e, f in sg) + self.einzug for sg in self.segmente]
        self.ys, y_ = [], 20.0
        for hh, aa in zip(self.hoehen, self.asz):
            self.ys.append(y_ + aa)
            y_ += hh * self.faktor
        self.b = int(max(self.breiten)) + 40
        self.h = int(y_ - (self.hoehen[-1] * self.faktor - self.hoehen[-1])) + 20


def _effekte(d: dict) -> dict:
    ef = d.get("effekt") or {}
    if isinstance(ef, str):                                            # alte Schreibweise: Name
        ef = {({"schatten": "schatten", "spiegelung": "reflektion", "leuchten": "leuchten"}.get(ef.lower(), ef.lower())): {}}
    return ef


def _verteilt(sg: list, marke, ausr: str, letzte: bool) -> bool:
    einzeln = len(sg) <= 1 or (len(sg) == 2 and bool(marke))
    woerter = (sg[-1][0].split(" ") if sg else [])
    return ausr in ("block", "verteilt") and einzeln and len(woerter) > 1 and (ausr == "verteilt" or not letzte)


def _rechteck(x: float, y: float, w: float, h: float) -> list:
    return [("M", x, y), ("L", x + w, y), ("L", x + w, y + h), ("L", x, y + h), ("Z",)]


def _zeile(s: _Satz, i: int, ctx: dict, aus: tuple) -> None:
    """Fügt die Pfade einer Zeile zu (gesamt, gruppen, hervor, linien) hinzu."""
    gesamt, gruppen, hervor, linien = aus
    eng, sg, marke, ausr = s.engine, s.segmente[i], s.marken[i], ctx["ausr"]
    x = {"mitte": (max(s.breiten) - s.breiten[i]) / 2, "rechts": max(s.breiten) - s.breiten[i]}.get(ausr, 0) + s.einzug
    woerter = (sg[-1][0].split(" ") if sg else [])
    verteilen = _verteilt(sg, marke, ausr, i >= len(s.marken) - 1)
    xx = 20 + x
    for t, e, f in sg:
        hoehe = eng.font_metrics(f).line_spacing
        y = s.ys[i] + (-hoehe * 0.35 if e["hoch"] else hoehe * 0.2 if e["tief"] else 0)
        luecke = None
        if verteilen and t is sg[-1][0]:
            summe = sum(eng.measure_text(w_, f) for w_ in woerter)
            luecke = (max(s.breiten) - s.einzug - summe - (eng.measure_text(sg[0][0], f) if marke else 0)) / (len(woerter) - 1)
        x0 = xx
        pf: list = []
        for w_ in (t.split(" ") if luecke is not None else [t]):
            pf += eng.glyphen_pfad(w_, f, xx, y)
            xx += eng.measure_text(w_, f) + (luecke or 0)
        breite_t, px = xx - x0, f.size_pt * PX
        # Dekoration: Unterstreichung, Durchstreichung, Hervorhebung
        if e["unter"]:
            art_u = e["unter"] if isinstance(e["unter"], str) else "einfach"
            if art_u == "einfach" and not e["unterfarbe"]:
                pf += _rechteck(x0, y + px * 0.08 + 1, breite_t, max(1.0, px * 0.05))
            else:
                linien.append((x0, x0 + breite_t, y, art_u, e["unterfarbe"] or e["fuell"] or ctx["f1"] or "#000000", px))
        if e["durch"]:
            pf += _rechteck(x0, y - px * 0.27, breite_t, max(1.0, px * 0.05))
        if e["hervor"]:
            m = eng.font_metrics(f)
            hervor.append((e["hervor"], _rechteck(x0, y - m.ascent, breite_t, m.line_spacing)))
        gesamt.extend(pf)
        kl = e["kontur"] if e["kontur"] is not None else ctx["kontur"]
        gruppen.setdefault((e["fuell"], kl or None), []).extend(pf)


def _farbe(text, standard=(0, 0, 0, 255)) -> tuple:
    try:
        return rgba(text)
    except (ValueError, IndexError, TypeError, AttributeError):
        return standard


def _glut_schatten(z, gesamt: list, ef: dict, stil: tuple, pt: float) -> None:
    f1, f2, kontur, schatten = stil
    if "leuchten" in ef:
        c = _farbe((ef["leuchten"] or {}).get("farbe") or f2 or kontur or "#4f93d1")
        for br in (14, 9, 5):
            z.draw_path(gesamt, Style(color=(c[0], c[1], c[2], 60), width=br, join="round"), True, True)
    if "schatten" in ef:
        schatten = (ef["schatten"] or {}).get("farbe") or schatten or "#6b6b6b"
    if schatten:
        dd = max(2.0, pt / 14)
        z.push_state(translate=Point(dd, dd))
        z.draw_path(gesamt, Style(color=_farbe(schatten), width=0, filled=True), True, True)
        z.pop_state()


def _fuellen(z, gruppen: dict, stil: tuple, h: int, pt: float) -> None:
    f1, f2, kb = stil
    for (fl, kl), pf in gruppen.items():
        if not pf:
            continue
        fuell = None
        if fl is not None:
            if fl:
                z.draw_path(pf, Style(color=_farbe(fl), width=0, filled=True), True, True)
        elif f1:
            fuell = LinearGradient(Point(0, 20), Point(0, h - 20), ((0.0, _farbe(f1)), (1.0, _farbe(f2 or f1))))
            z.draw_path(pf, Style(color=_farbe(f1), width=0, filled=True, fill=fuell), True, True)
        if kl:
            z.draw_path(pf, Style(color=_farbe(kl), width=(kb or 1.5 * 96 / 72 / max(1.0, pt / 36)) * max(1.0, pt / 36), join="round"), True, True)


def _spiegeln(rgba_, b: int, h: int, hoehe_gesamt: int) -> None:
    """Spiegelbild unter das Bild setzen (Zeilen ``h``…``2h``), nach unten verblassend (Deckkraft 110/255 bis 0 bei 60 % der Höhe)."""
    for y in range(h):
        quelle = (h - 1 - y)
        nach = h + y
        if nach >= hoehe_gesamt:
            break
        f = max(0.0, (110 / 255) * (1.0 - (y / h) / 0.6)) if h else 0.0
        a = quelle * b * 4
        n = nach * b * 4
        zeile = bytearray(rgba_[a:a + b * 4])
        zeile[3::4] = bytes(int(v * f) for v in zeile[3::4])
        rgba_[n:n + b * 4] = zeile


def wordart_rgba(d: dict, engine, vorlagen, ss: int = SS) -> dict:
    """Das WordArt-Objekt ``d`` als Bild in ``ss``-facher Auflösung. → ``{"rgba", "w", "h", "b", "hoehe", "ys", "asz", "hoehen", "faktor", "zeilen"}``: ``w``/``h`` Pixel des Bildes,
    ``b``/``hoehe`` logische Maße (ohne Spiegelung), ``ys``/``asz``/``hoehen`` je Zeile (logisch), ``faktor`` Zeilenabstand."""
    from core.rendering.ausgabe.rasterziel import RasterZiel
    laeufe = anzeige_laeufe(d)
    pt = float(d.get("pt", 36))
    f1, f2, kontur, kb, schatten = _stil(d, pt, vorlagen)
    s = _Satz(engine, d, laeufe, pt)
    ef = _effekte(d)
    spiegel = "reflektion" in ef
    gesamt_h = s.h * 2 if spiegel else s.h
    z = RasterZiel(engine, s.b, gesamt_h, float(ss), (255, 255, 255, 0))
    aus = ([], {}, [], [])                                             # gesamt; Gruppen nach Füllung/Kontur; Hervorhebungen; eigene Linien
    ctx = {"ausr": d.get("ausr", "links"), "kontur": kontur, "f1": f1}
    for i in range(len(s.segmente)):
        _zeile(s, i, ctx, aus)
    gesamt, gruppen, hervor, linien = aus
    _glut_schatten(z, gesamt, ef, (f1, f2, kontur, schatten), pt)
    for farbe_h, hp in hervor:                                        # Texthervorhebung: Hintergrund hinter dem Text
        z.draw_path(hp, Style(color=_farbe(farbe_h), width=0, filled=True), True, True)
    _fuellen(z, gruppen, (f1, f2, kb), s.h, pt)
    for x0_, x1_, y_u, art_u, farbe_u, px in linien:
        Z.unterstrich(z, [(x0_, x1_)], art_u, y_u, float(px), _farbe(farbe_u))
    w, h, roh = z.als_rgba()
    puffer = bytearray(roh)
    if spiegel:
        _spiegeln(puffer, w, s.h * ss, h)
    return {"rgba": puffer, "w": w, "h": h, "b": s.b, "hoehe": s.h, "ys": s.ys, "asz": s.asz, "hoehen": s.hoehen, "faktor": s.faktor, "zeilen": len(s.segmente)}
