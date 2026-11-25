"""RTF-Steuerwörter im Haupttext: Zeichen, Absatz, Zeichenformat, Seite und Farbtabelle (je eine kleine Stufe)."""
from __future__ import annotations

TWIP_PRO_MM = 1440 / 25.4
ZEICHEN = {"emdash": "—", "endash": "–", "bullet": "•", "lquote": "‘", "rquote": "’",
           "ldblquote": "“", "rdblquote": "”", "emspace": " ", "enspace": " ", "qmspace": " ",
           "tab": "\t", "line": " ", "lbr": " "}
_UNTERSTREICHUNG = {"ul", "uld", "uldb", "uldash", "uldashd", "uldashdd", "ulth", "ulw", "ulwave", "ulhwave", "ulldash",
                    "ulthd", "ulthdash", "ulthdashd", "ulthdashdd", "ulthldash", "ululdbwave"}
_ABSATZ_MASSE = ("li", "ri", "fi", "sb", "sa")
_SEITE_MASSE = {"paperw": "width_mm", "paperh": "height_mm"}                              # gelten für das ganze Dokument (Vorgabe aller Abschnitte)
_SEITE_RAND = {"margl": "margin_left_mm", "margr": "margin_right_mm", "margt": "margin_top_mm", "margb": "margin_bottom_mm",
               "headery": "kopf_abstand_mm", "footery": "fuss_abstand_mm"}
# Abschnittseigenschaften (nach \sectd): überschreiben die Vorgabe des Dokuments nur für ihren Abschnitt
_SEKTION = {"pgwsxn": "width_mm", "pghsxn": "height_mm", "marglsxn": "margin_left_mm", "margrsxn": "margin_right_mm", "margtsxn": "margin_top_mm", "margbsxn": "margin_bottom_mm"}
_SBK = {"sbknone": "fortlaufend", "sbkpage": "naechste", "sbkcol": "fortlaufend", "sbkeven": "gerade", "sbkodd": "ungerade"}
_FARBKANAL = ("red", "green", "blue")


def sek_fertig(sek: dict) -> dict:
    """Die Eigenschaften eines Abschnitts für das Modell: einzelne Spaltenbreiten (``\\colw``, ``\\colsr``) werden zu ``spalten_raster_mm``, wenn sie ungleich sind."""
    aus = {k: v for k, v in sek.items() if not k.startswith("_")}
    cols = sek.get("_cols")
    if cols and aus.get("spalten") and len(cols) == aus["spalten"]:
        raster = [[c.get("colw", 0) / TWIP_PRO_MM, c.get("colsr", 0) / TWIP_PRO_MM] for _n, c in sorted(cols.items())]
        if len({round(r[0]) for r in raster}) > 1:
            aus["spalten_raster_mm"] = raster
    return aus


def steuerwort(z, g: dict, w: str, zahl: int | None) -> None:
    """Ein Steuerwort im aktuellen Gruppenzustand ``g`` anwenden; ``z`` ist der Zerleger (Seite, Stile, Codepage)."""
    if g["dest"] == "colortbl":
        if w in _FARBKANAL and zahl is not None:
            g["farbe"][_FARBKANAL.index(w)] = max(0, min(255, zahl))
        return
    if g["dest"] is not None:
        return
    an = zahl is None or zahl != 0
    for stufe in (_text_wort, _absatz_wort, _zeichen_wort, _dokument_wort):
        if stufe(z, g, w, zahl, an):
            return


def _text_wort(z, g, w, zahl, an) -> bool:
    if w in ZEICHEN:
        g["ziel"].text(ZEICHEN[w], g["z"])
    elif w == "chpgn" and not g["ziel"].haupt:
        g["ziel"].text("{PAGE}", g["z"])
    elif w in ("cell", "nestcell"):
        ziel = g["ziel"]
        ziel.zelle_ende(g["a"]) if ziel.haupt else ziel.text("\t", g["z"])
    else:
        return False
    return True


def _seite_umbruch(ab: dict, ziel, w: str) -> None:
    """\\par, \\page und \\pard: Absatz abschließen bzw. das Format leeren; ein Seitenumbruch vor dem Absatz merkt sich der Absatz."""
    if w == "par":
        ziel.absatz(ab)
        ab.pop("pagebb_einmal", None)
    elif w == "page":
        if ziel.laeufe:
            ziel.absatz(ab)
        ab["pagebb_einmal"] = True
    else:                                                    # pard: alles zurück, der Seitenumbruch vor dem Absatz bleibt
        einmal = ab.get("pagebb_einmal")
        ab.clear()
        if einmal:
            ab["pagebb_einmal"] = True


def _absatz_format(z, ab: dict, w: str, zahl, an) -> bool:
    """Ausrichtung, Abstände, Tabellenzeile, Seitenumbruch, Gliederungsebene und Absatzformatvorlage. → False, wenn ``w`` keiner davon ist."""
    if w in ("ql", "qc", "qr", "qj"):
        ab["q"] = w
    elif w in _ABSATZ_MASSE and zahl is not None:
        ab[w] = zahl
    elif w == "intbl":
        ab["intbl"] = True
    elif w in ("sl", "slmult", "ls", "ilvl", "cbpat") and zahl is not None:   # Zeilenabstand, Listenverweis, Absatzschattierung
        ab[w] = zahl
    elif w in ("tqr", "tqc", "tqdec"):                                    # Art des nächsten Tabulators (\tx folgt)
        ab["_tq"] = {"tqr": 1, "tqc": 2, "tqdec": 3}[w]
    elif w in ("tldot", "tlhyph", "tlul", "tlth", "tleq", "tlmdot"):      # Füllzeichen des nächsten Tabulators
        ab["_tl"] = {"tldot": ".", "tlhyph": "-", "tlul": "_", "tlth": "_", "tleq": "-", "tlmdot": "·"}[w]
    elif w == "tx" and zahl is not None:
        ab.setdefault("tabs", []).append((zahl, ab.pop("_tq", 0), ab.pop("_tl", "")))
    elif w in ("box", "brdrt", "brdrb", "brdrl", "brdrr") and not ab.get("in_tabelle_rand"):
        ab["rahmen"] = True
    elif w == "pagebb":
        ab["pagebb"] = an
    elif w == "s" and zahl is not None:
        if zahl in z.stile:
            ab["h"] = z.stile[zahl]
    elif w == "outlinelevel" and zahl is not None and 0 <= zahl <= 8:
        ab["h"] = zahl + 1
    else:
        return False
    return True


def _absatz_wort(z, g, w, zahl, an) -> bool:
    ab, ziel = g["a"], g["ziel"]
    if w == "sect" and z.modell and ziel.haupt:                       # Abschnittsende: schließt den Absatz ab, danach beginnt ein neuer Abschnitt
        _seite_umbruch(ab, ziel, "par")
        from filter.rtf.modell import Abschnittswechsel
        z.sek_liste.append(sek_fertig(z.sek))                                   # die Eigenschaften des Abschnitts, der hier endet (bleiben bis \sectd gültig)
        ziel.teile.append(Abschnittswechsel())
        return True
    if w in ("page", "column"):                                        # Umbruch mitten im Absatz: an seiner Stelle als Zeilenwechsel-Zeichen mit dem Zeichenformat ``umbruch``
        ziel.text("\u2028", {**g["z"], "umbruch": "seite" if w == "page" else "spalte"})
        return True
    if w in ("par", "pard"):
        _seite_umbruch(ab, ziel, w)
        return True
    return _absatz_format(z, ab, w, zahl, an)


def _zeichen_wort(z, g, w, zahl, an) -> bool:
    zf = g["z"]
    if w == "plain":
        zf.clear()
        zf.update({"f": None, "fs": 24})
    elif w in ("b", "i", "strike", "striked"):
        zf["strike" if w == "striked" else w] = an
    elif w in _UNTERSTREICHUNG:
        zf["ul"] = an
    elif w == "ulnone":
        zf["ul"] = False
    elif w in ("super", "sub"):
        zf["va"] = w
    elif w == "nosupersub":
        zf.pop("va", None)
    elif w in ("caps", "scaps", "v"):
        zf[w] = an
    elif w == "expnd" and zahl is not None:                              # Zeichenabstand: Viertelpunkte → Bildpunkte
        zf["expnd"] = zahl / 3.0
    elif w == "expndtw" and zahl is not None:                            # … oder Twips
        zf["expnd"] = zahl / 15.0
    elif w == "charscalex" and zahl:
        zf["scalex"] = zahl
    elif w in ("up", "dn"):                                              # Höhe der Grundlinie: Halbpunkte (ohne Zahl 6) → Punkt
        halb = 6 if zahl is None else zahl
        zf["up"] = halb / 2.0 if w == "up" else -halb / 2.0
    elif w == "fs" and zahl:
        zf["fs"] = zahl
    elif w in ("f", "cf") and zahl is not None:
        zf[w] = zahl
    elif w in ("cb", "chcbpat") and zahl is not None:
        zf["cb"] = zahl
    elif w == "highlight" and zahl is not None:
        zf["hl"] = zahl
    else:
        return False
    return True


def _dokument_wort(z, g, w, zahl, an) -> bool:
    if w == "ansicpg" and zahl:
        try:
            "".encode(f"cp{zahl}")
            z.codepage = f"cp{zahl}"
        except LookupError:
            pass
    elif w == "deff" and zahl is not None:
        z.standard_schrift = zahl
    elif w in _SEITE_MASSE and zahl:
        setattr(z.seite, _SEITE_MASSE[w], zahl / TWIP_PRO_MM)
    elif w in _SEITE_RAND and zahl is not None:
        setattr(z.seite, _SEITE_RAND[w], zahl / TWIP_PRO_MM)
    elif w == "sectd":                                                     # neuer Abschnitt: Eigenschaften zurück auf die Vorgabe des Dokuments
        z.sek = {}
    elif w in _SBK:
        z.sek["beginn"] = _SBK[w]
    elif w == "cols" and zahl:                                             # Spalten des Abschnitts: Zahl, Abstand, Trennlinie, einzelne Breiten (\\colno/\\colw/\\colsr)
        z.sek["spalten"] = zahl
    elif w == "colsx" and zahl is not None:
        z.sek["spalten_abstand_mm"] = zahl / TWIP_PRO_MM
    elif w == "linebetcol":
        z.sek["spalten_linie"] = an
    elif w == "colno" and zahl:
        z.sek["_colno"] = zahl
    elif w in ("colw", "colsr") and zahl is not None and z.sek.get("_colno"):
        z.sek.setdefault("_cols", {}).setdefault(z.sek["_colno"], {})[w] = zahl
    elif w in _SEKTION and zahl is not None:
        z.sek[_SEKTION[w]] = zahl / TWIP_PRO_MM
    elif w == "titlepg":
        z.titel_erste = True
    else:
        return False
    return True
