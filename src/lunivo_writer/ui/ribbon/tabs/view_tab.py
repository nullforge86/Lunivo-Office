"""Reiter „Ansicht“ in der Anordnung der Vorlage: Dokumentansichten (Vollbild, Lesemodus, Drucklayout, Weblayout), Navigationsbereich
mit den Anzeige-Schaltern, Zoom, Fenster; dazu Helligkeit und Oberfläche."""
from __future__ import annotations

from lunivo_writer.ui.ribbon.tabs.baustein import alle, k as _k, uebrige


def bauen(register: dict) -> dict:
    tab = dict(next(t for t in register["register"] if t["name"] == "Ansicht"))
    tab["gruppen"] = [dict(g) for g in tab["gruppen"]]
    anz = next(g for g in tab["gruppen"] if g["name"] == "Anzeigen")
    if not any(e.get("tun") == "versteckteZeigen" for e in anz["knoepfe"]):
        anz["knoepfe"] = anz["knoepfe"] + [_k("vorschau", "Ausgeblendeter Text", "versteckteZeigen", haken=True)]
    kn = alle(tab)
    benutzt: set = set()

    def nimm(name, **kw):
        benutzt.add(name)
        return dict(kn[name], **kw)

    helligkeit = next(g for g in tab["gruppen"] if g["name"] == "Helligkeit")
    oberflaeche = next(g for g in tab["gruppen"] if g["name"] == "Oberfläche")
    for g in (helligkeit, oberflaeche):
        for e in g["knoepfe"]:
            benutzt.add(e["name"])
    def eintraege(*namen):
        """Befehle als Menüeinträge (Haken bleiben Haken) — aus Einzelknöpfen wird ein Menü."""
        return [{"name": n, "tun": kn[n]["tun"], **({"haken": True} if kn[n].get("haken") else {})} for n in namen]

    def klein(name):                                                  # nur Symbol; der Hinweistext nennt die Funktion
        return nimm(name, gross=False, text=False)

    fenster_menue = list(kn["Anordnen"]["menue"]) + [{"trenner": True}] + eintraege("Fensterliste")
    for n in ("Nebeneinander", "Untereinander", "Kacheln", "Fensterliste", "Anordnen", "Steuerzeichen", "Weblayout", "Gliederung", "Vertikales Lineal", "Textbegrenzungen", "Ausgeblendeter Text"):
        benutzt.add(n)
    gruppen = [
        {"name": "Dokumentansichten", "reihenfolge": True, "knoepfe": [
            nimm("Drucklayout", gross=True), nimm("Lesemodus", gross=True),
            {"symbol": "fortlaufend", "name": "Weitere Ansichten", "gross": True,
             "menue": [{"name": "Vollbild", "tun": "vollbild", "haken": True}] + eintraege("Weblayout", "Gliederung")}]},
        {"name": "Anzeigen", "pfeil": anz.get("pfeil"), "reihenfolge": True, "knoepfe": [
            nimm("Navigationsbereich", gross=True), nimm("Lineal", text=True), nimm("Gitternetzlinien", text=True),
            {"symbol": "ecken", "name": "Weitere Anzeigen", "text": True,
             "menue": eintraege("Vertikales Lineal", "Textbegrenzungen", "Steuerzeichen", "Ausgeblendeter Text")}]},
        {"name": "Zoom", "pfeil": "zoomStufe", "reihenfolge": True, "knoepfe": [
            nimm("Zoom", gross=True), klein("100 %"), klein("Seitenbreite"), klein("Eine Seite"),
            klein("Zwei Seiten"), klein("Vergrößern"), klein("Verkleinern")]},
        dict(helligkeit, reihenfolge=True, knoepfe=[dict(e, text=False) for e in helligkeit["knoepfe"]]),
        {"name": "Fenster", "reihenfolge": True, "knoepfe": [
            nimm("Neues Fenster", gross=True), dict(kn["Anordnen"], menue=fenster_menue, gross=True)]},
        dict(oberflaeche, reihenfolge=True),
    ]
    rest = [dict(e, gross=False, text=True) for e in uebrige(tab, benutzt)]
    if rest:
        gruppen.append({"name": "Weitere", "reihenfolge": True, "knoepfe": rest})
    return dict(tab, gruppen=gruppen)
