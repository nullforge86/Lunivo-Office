"""Qt-freie Indexverarbeitung."""

def index_zeilen_bilden(eintraege, seiten, marken) -> list:
    baum: dict[tuple, dict] = {}
    for e, _p in eintraege:
        s = next(seiten)
        if e.marke in marken:
            a, z = next(seiten), next(seiten)
            s = (a, z) if z > a else a
        h = baum.setdefault((e.sortierung()[0], e.haupt), {"text": e.haupt, "seiten": {}, "siehe": [], "unter": {}})
        ziel = h if not e.unter else h["unter"].setdefault((e.sortierung()[1], e.unter), {"text": e.unter, "seiten": {}, "siehe": []})
        if e.siehe:
            if e.siehe not in ziel["siehe"]:
                ziel["siehe"].append(e.siehe)
        else:
            fk = ziel["seiten"].setdefault(s, [False, False])
            fk[0] |= e.fett; fk[1] |= e.kursiv

    def angabe(knoten) -> list:
        stuecke = []
        for s in sorted(knoten["seiten"], key=lambda x: x if isinstance(x, tuple) else (x, x)):
            if stuecke:
                stuecke.append((", ", False, False))
            text = f"{s[0]}–{s[1]}" if isinstance(s, tuple) else str(s)
            stuecke.append((text, *knoten["seiten"][s]))
        for x in knoten["siehe"]:
            stuecke.append(((". " if stuecke else "") + "Siehe " + x, False, True))
        return stuecke

    out = []
    for k in sorted(baum):
        h = baum[k]
        out.append((1, h["text"], angabe(h)))
        for u in sorted(h["unter"]):
            out.append((2, h["unter"][u]["text"], angabe(h["unter"][u])))
    return out
