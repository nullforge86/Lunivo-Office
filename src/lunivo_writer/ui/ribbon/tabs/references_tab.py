"""Reiter „Verweise“ (in register.json „Referenzen“) in der Anordnung von WPS Office: TOC einfügen, Inhaltsverzeichnis
aktualisieren, Klappe „Inhaltsverzeichnis“ (Ebene 1–9, Textkörper); Fußnote und Endnote je mit Vorherige/Nächste und der
Trennlinie; Beschriftung mit Abbildungsverzeichnis und Querverweis; Eintrag festlegen, Index einfügen und aktualisieren;
Seriendruck. Lunivos Zitate und Literatur stehen dahinter."""
from __future__ import annotations

from lunivo_writer.ui.ribbon.tabs.baustein import alle, k as _k, uebrige


def bauen(register: dict) -> dict:
    tab = dict(next(t for t in register["register"] if t["name"] == "Referenzen"), name="Verweise")
    kn = alle(tab)
    benutzt: set = set()

    def nimm(_name, **kw):
        benutzt.add(_name)
        return {s: w for s, w in dict(kn[_name], **kw).items() if w is not None}         # None nimmt einen Schlüssel weg

    zitate = next(g for g in tab["gruppen"] if g["name"] == "Zitate und Literatur")
    for e in zitate["knoepfe"]:
        benutzt.add(e["name"])
    gruppen = [
        {"name": "Inhaltsverzeichnis", "reihenfolge": True, "knoepfe": [
            nimm("Inhaltsverzeichnis", name="TOC einfügen", gross=True),
            nimm("Verzeichnisse aktualisieren", name="Inhaltsverzeichnis aktualisieren", symbol="aktualisieren", gross=True,
                 tun="inhaltsverzeichnisAktualisieren"),
            _k("ebenen", "Inhaltsverzeichnis", None, True, klappe="inhaltsverzeichnisKlappe")]},
        {"name": "Fußnoten", "reihenfolge": True, "knoepfe": [
            nimm("Fußnote", name="Fußnote einfügen", gross=True),
            _k("voriges", "Vorherige Fußnote", "fussnoteZurueck", text=True), _k("naechstes", "Nächste Fußnote", "fussnoteWeiter", text=True),
            nimm("Endnote", name="Endnote einfügen", gross=True),
            _k("voriges", "Vorherige Endnote", "endnoteZurueck", text=True), _k("naechstes", "Nächste Endnote", "endnoteWeiter", text=True),
            _k("notentrenner", "Fußnote/Endnotentrennlinie", "notenTrennlinie", True),     # gibt es nur im Notenbereich: grau
            nimm("Notenbereich", text=True)]},
        {"name": "Beschriftungen", "reihenfolge": True, "knoepfe": [
            nimm("Beschriftung", gross=True), nimm("Abbildungsverzeichnis", name="Abbildungsverzeichnis einfügen", text=True),
            nimm("Querverweis", text=True)]},
        {"name": "Index", "reihenfolge": True, "knoepfe": [
            nimm("Indexeintrag", name="Eintrag festlegen", gross=True),
            nimm("Stichwortverzeichnis", name="Index einfügen", symbol="indexbuch", text=True),
            _k("aktualisieren", "Index aktualisieren", "indexAktualisieren", text=True)]},
        {"name": "Seriendruck", "reihenfolge": True, "knoepfe": [
            _k("serie", "Seriendruck", "serienReiter", True)]},
        dict(zitate, reihenfolge=True, knoepfe=[dict(e, gross=(i == 0), text=(i > 0)) for i, e in enumerate(zitate["knoepfe"])]),
    ]
    benutzt.update(("Nächste Note", "Vorige Note"))         # ersetzt durch Vorherige/Nächste Fußnote und Endnote
    rest = [dict(e, gross=False, text=True) for e in uebrige(tab, benutzt)]
    if rest:
        gruppen.append({"name": "Weitere", "reihenfolge": True, "knoepfe": rest})
    return dict(tab, gruppen=gruppen)
