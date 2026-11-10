"""RTF-Steuerwörter im Haupttext: Zeichen, Absatz, Zeichenformat, Seite und Farbtabelle (je eine kleine Stufe)."""
from __future__ import annotations

TWIP_PRO_MM = 1440 / 25.4
ZEICHEN = {"emdash": "—", "endash": "–", "bullet": "•", "lquote": "‘", "rquote": "’",
           "ldblquote": "“", "rdblquote": "”", "emspace": " ", "enspace": " ", "qmspace": " ",
           "tab": "\t", "line": " ", "lbr": " "}
_UNTERSTREICHUNG = {"ul", "uld", "uldb", "uldash", "uldashd", "uldashdd", "ulth", "ulw", "ulwave", "ulhwave", "ulldash",
                    "ulthd", "ulthdash", "ulthdashd", "ulthdashdd", "ulthldash", "ululdbwave"}
_ABSATZ_MASSE = ("li", "ri", "fi", "sb", "sa")
_SEITE_MASSE = {"paperw": "width_mm", "pgwsxn": "width_mm", "paperh": "height_mm", "pghsxn": "height_mm"}
_SEITE_RAND = {"margl": "margin_left_mm", "marglsxn": "margin_left_mm", "margr": "margin_right_mm",
               "margrsxn": "margin_right_mm", "margt": "margin_top_mm", "margtsxn": "margin_top_mm",
               "margb": "margin_bottom_mm", "margbsxn": "margin_bottom_mm", "headery": "kopf_abstand_mm",
               "footery": "fuss_abstand_mm"}
_FARBKANAL = ("red", "green", "blue")


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


def _absatz_wort(z, g, w, zahl, an) -> bool:
    ab, ziel = g["a"], g["ziel"]
    if w == "par":
        ziel.absatz(ab)
        ab.pop("pagebb_einmal", None)
    elif w == "page":
        if ziel.laeufe:
            ziel.absatz(ab)
        ab["pagebb_einmal"] = True
    elif w == "pard":
        einmal = ab.get("pagebb_einmal")
        ab.clear()
        if einmal:
            ab["pagebb_einmal"] = True
    elif w in ("ql", "qc", "qr", "qj"):
        ab["q"] = w
    elif w in _ABSATZ_MASSE and zahl is not None:
        ab[w] = zahl
    elif w == "intbl":
        ab["intbl"] = True
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
    elif w == "titlepg":
        z.titel_erste = True
    else:
        return False
    return True
