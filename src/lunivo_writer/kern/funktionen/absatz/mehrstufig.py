"""Mehrstufige Nummerierung („Gliederung nummeriert“: 1. / 1.1. / 1.1.1.): Definitionen, Zählung und Nummerntexte. Qt-frei.

Die Nummern setzt und zeichnet die Layoutberechnung des Kerns (``core/document/listen.py``, ``core/layout``); hier stehen die Vorlagen und der Zähler für die
Fenster. Der Text steht mit Einzug „Einzug bei“ ab dieser Ebene, die Nummer beginnt bei „Ausrichtung“.

Eine Gliederung ist ``{"ebenen": [9 × {"stil", "format", "start", "ausr", "einzug", "zeichen"?}]}``. ``format`` ist das Zahlenformat mit
den Platzhaltern ①…⑨ für die Nummern der Ebenen 1…9 („①.②.“ = 1.1.). ``ausr`` und ``einzug`` sind Millimeter.
"""
from __future__ import annotations

import json

from lunivo_writer.kern.funktionen.absatz.listen import STILE, zeichen_filtern

PLATZHALTER = "①②③④⑤⑥⑦⑧⑨"
EBENEN = 9


def nummer_text(stil: str, n: int) -> str:
    """Die Zahl ``n`` in der Zahlenart ``stil`` (dezimal, klein, gross, roem_klein, roem_gross)."""
    if stil == "dezimal" or stil not in STILE:
        return str(n)
    if stil in ("klein", "gross"):
        s = ""
        while n > 0:
            n, r = divmod(n - 1, 26)
            s = chr(97 + r) + s
        return s if stil == "klein" else s.upper()
    zahlen = ((1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"), (50, "l"), (40, "xl"), (10, "x"),
              (9, "ix"), (5, "v"), (4, "iv"), (1, "i"))
    s = ""
    for w, z in zahlen:
        while n >= w:
            s += z; n -= w
    return s if stil == "roem_klein" else s.upper()


# Weitere Felder einer Ebene (nur gesetzt, wenn sie von der Vorgabe abweichen):
#   tab (Tabstopp-Leerstelle nach, mm; Vorgabe = einzug), ausr_art ("links" | "mitte" | "rechts": woran die Nummer an ``ausr`` hängt),
#   danach ("tab" | "leer" | "nichts": was zwischen Nummer und Text steht), neu (Ebene, nach der neu gezählt wird; None = nach jeder höheren),
#   norm (Nummern höherer Ebenen als Dezimalzahlen), vorlage (Formatvorlage, die Absätze auf diese Ebene setzt)
EXTRA = {"tab": None, "ausr_art": "links", "danach": "tab", "neu": None, "norm": False, "vorlage": ""}


def ebene(stil: str = "dezimal", format: str = "①.", start: int = 1, ausr: float = 0.0, einzug: float = 8.0, zeichen: dict | None = None,
          **mehr) -> dict:
    d = {"stil": stil, "format": format, "start": max(1, int(start)), "ausr": float(ausr), "einzug": float(einzug)}
    z = zeichen_filtern(zeichen)
    if z:
        d["zeichen"] = z
    for k, v in mehr.items():
        if k in EXTRA and v not in (None, EXTRA[k], False, ""):
            d[k] = v
    return d


def ebene_aus(x: dict) -> dict:
    """Eine Ebene aus einem Wörterbuch (JSON, Dialog) mit allen bekannten Feldern neu aufbauen."""
    return ebene(x["stil"], x["format"], x["start"], x["ausr"], x["einzug"], x.get("zeichen"), **{k: x.get(k) for k in EXTRA})


def aufzaehlung(zeichen: str) -> dict:
    """Aufzählung mit einem Zeichen (◆ ✤ ➤ ✓ ✧ …), das Lunivo selbst zeichnet; Ebenen wie bei einer Gliederung eingerückt."""
    return {"ebenen": [ebene("dezimal", zeichen, 1, i * 7.0, i * 7.0 + 7.0) for i in range(EBENEN)]}


GLYPHEN = ("◆", "✤", "➤", "✓", "✧")                  # die Aufzählungszeichen des Reiters „Aufzählungszeichen“ neben Punkt und Quadrat


def ist_aufzaehlung(defn: dict) -> bool:
    """Gliederung ohne einen einzigen Platzhalter für Nummern: eine Aufzählung mit eigenem Zeichen."""
    return not any(ch in e["format"] for e in defn["ebenen"] for ch in PLATZHALTER)


def als_mehrstufig(spec: dict) -> dict:
    """Eine einfache Liste (``kern.funktionen.absatz.listen``) mit eigener Position als Gliederung: Ebene 1 ist die Liste, tiefere Ebenen zählen für sich."""
    pos = spec.get("pos") or {}
    e = []
    for i in range(EBENEN):
        f = (spec["praefix"] + PLATZHALTER[i] + spec["suffix"]) if i else (spec["praefix"] + PLATZHALTER[0] + spec["suffix"])
        e.append(ebene(spec["stil"], f, spec["start"] if not i else 1, pos.get("ausr", 0.0) + i * 7.0, pos.get("einzug", 8.0) + i * 7.0,
                       spec.get("zeichen"), tab=(pos.get("tab", pos.get("einzug", 8.0)) + i * 7.0), ausr_art=pos.get("ausr_art", "links"),
                       danach=pos.get("danach", "tab")))
    return {"ebenen": e}


def gliederung(stile: list[str], formate: list[str]) -> dict:
    """9 Ebenen aus je einer Zahlenart und einem Zahlenformat; Ausrichtung und Einzug wachsen mit der Ebene."""
    return {"ebenen": [ebene(stile[min(i, len(stile) - 1)], formate[min(i, len(formate) - 1)], 1, i * 7.0, i * 7.0 + 9.0)
                       for i in range(EBENEN)]}


def _alle(zahlenart: str, formate: tuple[str, str, str]) -> dict:
    """Ebene n zeigt die Nummern aller Ebenen davor (``①.②.``); ``formate`` bestimmt, ob Ebene 1, 2 und tiefer mit Punkt enden (``"."``) oder nicht (``""``)."""
    def fmt(i: int) -> str:
        ende = formate[min(i, 2)]
        return ".".join(PLATZHALTER[k] for k in range(i + 1)) + ende
    return gliederung([zahlenart], [fmt(i) for i in range(EBENEN)])


 # Die Vorlagen des Reiters „Gliederung nummeriert“ (ohne „Kein“): erst die sieben wie in der Vorlage, dann zwei klassische; Name für die Kachel
VORLAGEN = (
    ("1. / 1.1. / 1.1.1.", _alle("dezimal", (".", ".", "."))),
    ("I. / I.I / I.I.I", _alle("roem_gross", (".", "", ""))),
    ("i. / i.i. / i.i.i.", _alle("roem_klein", (".", ".", "."))),
    ("i. / i.i / i.i.i", _alle("roem_klein", (".", "", ""))),
    ("1 / 1.1. / 1.1.1.", _alle("dezimal", ("", ".", "."))),
    ("1. / 1.1 / 1.1.1", _alle("dezimal", (".", "", ""))),
    ("A. / A.A. / A.A.A.", _alle("gross", (".", ".", "."))),
    ("I. / A. / 1. / a) / i)", gliederung(["roem_gross", "gross", "dezimal", "klein", "roem_klein"],
                                         ["①.", "②.", "③.", "④)", "⑤)", "⑥.", "⑦.", "⑧)", "⑨)"])),
    ("1) / a) / i)", gliederung(["dezimal", "klein", "roem_klein"], ["①)", "②)", "③)", "④)", "⑤)", "⑥)", "⑦)", "⑧)", "⑨)"])),
)


def als_text(defn: dict) -> str:
    return "g:" + json.dumps(defn, ensure_ascii=False, separators=(",", ":"))


def aus_text(text: str | None) -> dict | None:
    if not text or not text.startswith("g:"):
        return None
    try:
        d = json.loads(text[2:])
        e = d["ebenen"]
        if len(e) != EBENEN:
            return None
        return {"ebenen": [ebene_aus(x) for x in e]}
    except (ValueError, KeyError, TypeError):
        return None


def block_wert(ebene_nr: int, defn: dict) -> str:
    return f"{ebene_nr}|{json.dumps(defn, ensure_ascii=False, separators=(',', ':'))}"


def aus_block(text: str) -> tuple[int, dict] | None:
    try:
        n, rest = text.split("|", 1)
        d = aus_text("g:" + rest)
        return (max(1, min(EBENEN, int(n))), d) if d else None
    except ValueError:
        return None


def nummer_der_ebene(defn: dict, zaehler: list[int], ebene_nr: int) -> str:
    """Die Nummer als Text für einen Absatz der Ebene ``ebene_nr`` (1…9) bei diesen Zählerständen."""
    e = defn["ebenen"][ebene_nr - 1]
    f = e["format"]
    for i, ch in enumerate(PLATZHALTER):
        if ch in f:
            stil = "dezimal" if e.get("norm") and i != ebene_nr - 1 else defn["ebenen"][i]["stil"]       # „Nummerieren nach Norm“
            f = f.replace(ch, nummer_text(stil, zaehler[i]) if i < ebene_nr else "")
    return f


def zaehlen(zaehler: list[int], defn: dict, ebene_nr: int) -> None:
    """Zählerstand nach einem Absatz der Ebene ``ebene_nr``: diese Ebene weiter, tiefere neu."""
    i = ebene_nr - 1
    zaehler[i] = defn["ebenen"][i]["start"] if zaehler[i] == 0 else zaehler[i] + 1
    for k in range(i + 1, EBENEN):
        neu = defn["ebenen"][k].get("neu")                  # „Neu nummerieren nach Ebene …“: sonst nach jeder höheren Ebene
        if neu is None or ebene_nr <= neu:
            zaehler[k] = 0
