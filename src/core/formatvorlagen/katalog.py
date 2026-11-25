"""Formatvorlagen des Katalogs (``core.formatvorlagen.zeichen.stile``) und des Dokumentmodells ineinander umrechnen; eine Katalogvorlage im
Dokument anlegen oder angleichen und anwenden."""
from __future__ import annotations

from core.dokument import Formatvorlage, Position
from core.formatierung.absatz import tabs_als_text, tabs_aus_text
from core.layout.drucklayout import FUELLZEICHEN, absatzformat, tabfuellung, tabstopps, zeichenformat
from core.formatvorlagen.zeichen import definition as _definition, namen as _namen
from core.geometrie import mm_to_px, px_to_mm


def katalog_zu_vorlage(name: str, d: dict) -> Formatvorlage:
    """Eine Formatvorlage des Katalogs (``editor/text/stile.py``) als Vorlage des Dokumentmodells."""
    zeichen = {}
    for k, v in (("groesse_pt", float(d["groesse"]) if d.get("groesse") else None), ("fett", True if d.get("fett") else None),
                 ("kursiv", True if d.get("kursiv") else None), ("farbe", d.get("farbe") or None), ("schrift", d.get("schrift") or None),
                 ("durchgestrichen", True if d.get("durch") else None), ("doppelt_durch", True if d.get("doppelt") else None),
                 ("hoch_tief", "hoch" if d.get("hoch") else "tief" if d.get("tief") else None),
                 ("kapitaelchen", True if d.get("kapital") else None), ("grossbuchstaben", True if d.get("gross") else None),
                 ("versteckt", True if d.get("versteckt") else None), ("zeichenabstand", float(d["abstand"]) if d.get("abstand") else None),
                 ("skalierung", float(d["skala"]) if d.get("skala") and float(d["skala"]) != 100.0 else None),
                 ("versatz_pt", float(d["position"]) if d.get("position") else None), ("unterstrichen", True if d.get("unter") else None),
                 ("unter_farbe", d.get("unterfarbe") or None), ("betonung", d.get("betonung") or None), ("effekt", d.get("effekt") or None)):
        if v is not None:
            zeichen[k] = v
    absatz = {}
    zeilen_art = d.get("zeilen_art", "faktor")
    for k, v in (("abstand_vor", d["vor"] / 0.75 if d.get("vor") else None), ("abstand_nach", d["nach"] / 0.75 if d.get("nach") else None),
                 ("ausrichtung", d.get("ausr") or None),
                 ("zeilenabstand_art", ("vielfach" if zeilen_art == "faktor" else zeilen_art) if (d.get("zeilen") or zeilen_art != "faktor") else None),
                 ("zeilenabstand", d["zeilen"] * 100.0 if zeilen_art == "faktor" and d.get("zeilen") else d["zeilen_pt"] / 0.75 if zeilen_art != "faktor" and d.get("zeilen_pt") else None),
                 ("einzug_links", mm_to_px(d["einzug"]) if d.get("einzug") else None), ("einzug_rechts", mm_to_px(d["rechts"]) if d.get("rechts") else None),
                 ("einzug_erste", mm_to_px(d["erste"]) if d.get("erste") else None), ("seitenumbruch_vor", True if d.get("umbruch") else None),
                 ("gliederungsebene", int(d["gliederung"]) if d.get("gliederung") else None), ("richtung", "rtl" if d.get("rtl") else None),
                 ("rahmen", d.get("rahmen") or None), ("hintergrund", d.get("fuell") or None),
                 ("muster", (d["muster"] + ("|" + d["musterfarbe"] if d.get("musterfarbe") else "")) if d.get("muster") else None),
                 ("optionen", d.get("opt") or None)):
        if v is not None:
            absatz[k] = v
    if d.get("tabs"):
        stopps = tabs_aus_text(d["tabs"])
        absatz["tabstopps"] = [[mm_to_px(m), art, ""] for m, art, _f in stopps]
        fuell = ";".join(f"{mm_to_px(m):.2f}:{f}" for m, _a, f in stopps if f)
        if fuell:
            absatz["tabfuell"] = fuell
    zusatz = {k: d[k] for k in ("taste", "key", "liste") if d.get(k)}
    return Formatvorlage(name, "absatz", d.get("basis") or ("" if name == "Standard" else "Standard"), d.get("folge") or ("Standard" if d.get("ebene") else ""),
                         int(d.get("ebene") or 0), zeichen, absatz, zusatz)


def vorlage_zu_katalog(v: Formatvorlage) -> dict:
    """Die Felder einer Katalogvorlage (``stile.VORLAGE``), soweit das Modell sie führt — für das Fenster „Formatvorlage“."""
    z, a = v.zeichen, v.absatz
    d = {"ebene": v.ebene, "groesse": z.get("groesse_pt") or 0, "fett": bool(z.get("fett")), "kursiv": bool(z.get("kursiv")), "farbe": z.get("farbe", ""),
         "schrift": z.get("schrift", "") if isinstance(z.get("schrift", ""), str) else "", "vor": round(a.get("abstand_vor", 0) * 0.75, 1),
         "nach": round(a.get("abstand_nach", 0) * 0.75, 1), "ausr": a.get("ausrichtung", ""), "einzug": round(px_to_mm(a.get("einzug_links", 0)), 1),
         "rechts": round(px_to_mm(a.get("einzug_rechts", 0)), 1), "erste": round(px_to_mm(a.get("einzug_erste", 0)), 1),
         "rtl": a.get("richtung") in ("rtl", 1), "umbruch": bool(a.get("seitenumbruch_vor")), "gliederung": a.get("gliederungsebene", 0),
         "rahmen": a.get("rahmen", ""), "fuell": a.get("hintergrund", ""), "durch": bool(z.get("durchgestrichen")), "versteckt": bool(z.get("versteckt")),
         "hoch": z.get("hoch_tief") == "hoch", "tief": z.get("hoch_tief") == "tief", "kapital": bool(z.get("kapitaelchen")), "gross": bool(z.get("grossbuchstaben"))}
    art = a.get("zeilenabstand_art")
    if art == "vielfach":
        d["zeilen"] = a.get("zeilenabstand", 100.0) / 100.0
    elif art in ("genau", "mindestens"):
        d.update(zeilen_art=art, zeilen_pt=a.get("zeilenabstand", 0.0) * 0.75)
    if isinstance(a.get("optionen"), str):
        d["opt"] = a["optionen"]
    return d


def vorlage_abgleichen(s, name: str) -> int:
    """Legt die Katalogvorlage ``name`` in der Bearbeitungssitzung ``s`` an oder aktualisiert sie, wenn sie dort anders steht. → 1 bei Änderung."""
    if name not in _namen():
        return 0
    neu = katalog_zu_vorlage(name, _definition(name))
    if s.dokument.vorlagen.get(name) == neu:
        return 0
    s.vorlage_setzen(neu)
    return 1


def vorlage_anwenden(s, name: str) -> int:
    """Wendet die Vorlage ``name`` auf die Auswahl an („Fließtext“ heißt im Dokument „Standard“); vorher aus dem Katalog angleichen.
    → 1, wenn es die Vorlage gibt."""
    name = "Standard" if name == "Fließtext" else name
    vorlage_abgleichen(s, name)
    if name not in s.dokument.vorlagen:
        return 0
    s.vorlage_anwenden(name)
    return 1


_TAB_NAME = {0: "links", 1: "rechts", 2: "mitte", 3: "dezimal"}


def werte_aus_auswahl(s) -> dict:
    """Die Werte des Absatzes an der Schreibmarke als Vorgabe für „Neue Formatvorlage“ (Felder des Katalogs; ohne Liste)."""
    d = s.dokument
    start, _ende = s._bereich()
    a = s._absatz(start.absatz_id)
    z = zeichenformat(d, a, s.zeichenformat_bei(start if s.auswahl.leer else Position(start.absatz_id, min(start.versatz + 1, a.laenge))))
    af = absatzformat(d, s._absatz(s.auswahl.kopf.absatz_id))
    probe = Formatvorlage("", "absatz", "", "", 0, {k: v for k, v in z.items() if k != "vorlage"}, {k: v for k, v in af.items() if k != "vorlage"})
    werte = vorlage_zu_katalog(probe)
    werte["basis"] = s._absatz(s.auswahl.kopf.absatz_id).format.get("vorlage") or "Standard"
    if af.get("tabstopps"):
        fuell = tabfuellung(af)
        werte["tabs"] = tabs_als_text([(round(px_to_mm(t[0]), 1), _TAB_NAME.get(t[1], "links"),
                                        next((k for k, v in FUELLZEICHEN.items() for p, zz in fuell.items() if abs(p - t[0]) < 0.05 and zz == v), ""))
                                       for t in tabstopps(af, d)[0]])
    return werte
