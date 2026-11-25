"""Kartesisch: aus ``core.layout.drucklayout.ausgabe.diagramm.diagrammzeichner`` herausgelöst."""
from __future__ import annotations
import math
from core.geometrie import Point, Rect
from core.layout.drucklayout.ausgabe.backend import Style
from core.layout.drucklayout.ausgabe.diagramm import diagrammformat as DF
from core.diagramme.achsen.skala import _printf, _skala, _zahl
from core.layout.drucklayout.ausgabe.diagramm.diagrammzeichner_hilfen import _Z, _farbe, _hell, _reihenfarbe


TABELLE_ZEILE = 20.0


FEHLER_ANTEIL = 0.1


def trend(werte: list) -> tuple[float, float]:
    """Lineare Regression y = a + b·x über x = 0 … n-1 → (a, b)."""
    n = len(werte)
    if n < 2:
        return (werte[0] if werte else 0.0), 0.0
    mx, my = (n - 1) / 2, sum(werte) / n
    s = sum((x - mx) ** 2 for x in range(n))
    b = sum((x - mx) * (v - my) for x, v in enumerate(werte)) / s
    return my - b * mx, b


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
