"""Das Dokumentmodell als einfache Daten (JSON-tauglich, ohne Markup) und zurück. Ohne Qt.

Für Zwischenablage, Wiederherstellung und Textbausteine. Bilddaten stehen als Base64-Text.
"""
from __future__ import annotations

import base64
import dataclasses

from core.dokument.abschnitte.seite import HeaderFooter, PageSettings

from core.dokument.dokument import Absatz, Abschnitt, Dokument, Formatvorlage, FreiesObjekt, InlineObjekt, Kommentar, Lauf, ListenDefinition, ListenEbene, Note, Rahmen, Tabelle, Zelle

FASSUNG = 1
_KOPF_FUSS = ("header", "footer", "first_header", "first_footer", "even_header", "even_footer")


def seite_zu_daten(seite: PageSettings) -> dict:
    return dataclasses.asdict(seite)


def seite_aus_daten(daten: dict) -> PageSettings:
    seite = PageSettings()
    for f in dataclasses.fields(PageSettings):
        if f.name not in daten:
            continue
        wert = daten[f.name]
        if f.name in _KOPF_FUSS and isinstance(wert, dict):
            wert = HeaderFooter(wert.get("text", ""), wert.get("align", "center"), dict(wert.get("fmt") or {}),
                                [dict(r) for r in wert.get("runs") or []])
        setattr(seite, f.name, wert)
    return seite


def _fmt(fmt: dict) -> dict:
    return {k: (list(v) if isinstance(v, tuple) else v) for k, v in fmt.items()}


def bloecke_zu_daten(bloecke: list) -> list:
    daten = []
    for b in bloecke:
        if isinstance(b, Absatz):
            inhalte = []
            for x in b.inhalte:
                if isinstance(x, Lauf):
                    inhalte.append({"t": x.text, "f": _fmt(x.format)} if x.format else {"t": x.text})
                else:
                    inhalte.append({"objekt": dataclasses.asdict(x)})
            eintrag: dict = {"art": "absatz", "id": b.id, "inhalte": inhalte}
            if b.format_aufgeloest:
                eintrag["format_aufgeloest"] = True
            if b.format:
                eintrag["format"] = _fmt(b.format)
            if b.zeichenformat:
                eintrag["zeichenformat"] = _fmt(b.zeichenformat)
            if b.liste_id is not None:
                eintrag["liste"] = b.liste_id; eintrag["ebene"] = b.ebene
            daten.append(eintrag)
        elif isinstance(b, Rahmen):
            daten.append({"art": "rahmen", "id": b.id, "bloecke": bloecke_zu_daten(b.bloecke), "format": _fmt(b.format)})
        else:
            zellen = []
            for zeile in b.zellen:
                reihe = []
                for c in zeile:
                    if c.verdeckt_von is not None:
                        reihe.append({"verdeckt_von": list(c.verdeckt_von)})
                    else:
                        reihe.append({"bloecke": bloecke_zu_daten(c.bloecke), "format": _fmt(c.format), "zeilenspanne": c.zeilenspanne,
                                      "spaltenspanne": c.spaltenspanne})
                zellen.append(reihe)
            daten.append({"art": "tabelle", "id": b.id, "zellen": zellen, "spaltenbreiten": list(b.spaltenbreiten),
                          "zeilenhoehen": list(b.zeilenhoehen), "format": _fmt(b.format)})
    return daten


def bloecke_aus_daten(daten: list) -> list:
    bloecke = []
    for e in daten:
        if e.get("art") == "rahmen":
            bloecke.append(Rahmen(int(e["id"]), bloecke_aus_daten(e["bloecke"]), _fmt(e.get("format") or {})))
        elif e.get("art") == "tabelle":
            zellen = []
            for reihe in e["zellen"]:
                zeile = []
                for c in reihe:
                    if "verdeckt_von" in c:
                        zeile.append(Zelle([], {}, 1, 1, tuple(c["verdeckt_von"])))
                    else:
                        zeile.append(Zelle(bloecke_aus_daten(c["bloecke"]), _fmt(c.get("format") or {}), int(c.get("zeilenspanne", 1)),
                                           int(c.get("spaltenspanne", 1))))
                zellen.append(zeile)
            bloecke.append(Tabelle(int(e["id"]), zellen, list(e.get("spaltenbreiten") or []), list(e.get("zeilenhoehen") or []),
                                   _fmt(e.get("format") or {})))
        else:
            inhalte = []
            for x in e.get("inhalte", []):
                if "objekt" in x:
                    inhalte.append(InlineObjekt(**x["objekt"]))
                else:
                    inhalte.append(Lauf(x["t"], _fmt(x.get("f") or {})))
            bloecke.append(Absatz(int(e["id"]), inhalte, _fmt(e.get("format") or {}), _fmt(e.get("zeichenformat") or {}), e.get("liste"),
                                  int(e.get("ebene", 0)), bool(e.get("format_aufgeloest", False))))
    return bloecke


def dokument_zu_daten(d: Dokument) -> dict:
    return {
        "fassung": FASSUNG,
        "naechste_id": d.naechste_id,
        "abschnitte": [{"id": a.id, "beginn": a.beginn, "seite": seite_zu_daten(a.seite), "bloecke": bloecke_zu_daten(a.bloecke)}
                       for a in d.abschnitte],
        "vorlagen": {name: dataclasses.asdict(v) for name, v in d.vorlagen.items()},
        "listen": {str(i): dataclasses.asdict(liste) for i, liste in d.listen.items()},
        "kommentare": {str(i): dataclasses.asdict(k) for i, k in d.kommentare.items()},
        "noten": {art: {str(i): dataclasses.asdict(n) for i, n in noten.items()} for art, noten in d.noten.items()},
        "objekte": {str(i): dataclasses.asdict(o) for i, o in d.objekte.items()},
        "ressourcen": {k: base64.b64encode(v).decode("ascii") for k, v in d.ressourcen.items()},
        "quellen": [dict(q) for q in d.quellen],
        "eigenschaften": dict(d.eigenschaften),
        "standardformat": dict(d.standardformat),
    }


def dokument_aus_daten(daten: dict) -> Dokument:
    if int(daten.get("fassung", 0)) > FASSUNG:
        raise ValueError("Die Dokumentdaten stammen aus einer neueren Formatversion")
    d = Dokument()
    for a in daten.get("abschnitte", []):
        d.abschnitte.append(Abschnitt(int(a["id"]), bloecke_aus_daten(a["bloecke"]), seite_aus_daten(a.get("seite") or {}),
                                      a.get("beginn", "naechste")))
    d.vorlagen = {name: Formatvorlage(**v) for name, v in (daten.get("vorlagen") or {}).items()}
    for i, liste in (daten.get("listen") or {}).items():
        d.listen[int(i)] = ListenDefinition(int(liste["id"]), [ListenEbene(**e) for e in liste.get("ebenen", [])], liste.get("name", ""))
    d.kommentare = {int(i): Kommentar(**k) for i, k in (daten.get("kommentare") or {}).items()}
    d.noten = {"f": {}, "e": {}}
    for art, noten in (daten.get("noten") or {}).items():
        d.noten[art] = {int(i): Note(**n) for i, n in noten.items()}
    d.objekte = {int(i): FreiesObjekt(**o) for i, o in (daten.get("objekte") or {}).items()}
    d.ressourcen = {k: base64.b64decode(v) for k, v in (daten.get("ressourcen") or {}).items()}
    d.quellen = [dict(q) for q in daten.get("quellen") or []]
    d.eigenschaften = dict(daten.get("eigenschaften") or {})
    d.standardformat = dict(daten.get("standardformat") or {})
    d.naechste_id = int(daten.get("naechste_id", 1))
    return d
