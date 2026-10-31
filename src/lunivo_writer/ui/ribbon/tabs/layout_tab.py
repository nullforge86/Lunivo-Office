"""Reiter „Seitenlayout“ in der Anordnung von WPS Office: Designs, Ränder mit den vier Maßfeldern, Seite einrichten
(Orientierung, Größe, Spalten, Textrichtung, Umbrüche, Zeilennummern), Seitenhintergrund und Anordnen.
Dazu die kleine Gruppe Absatz (Einzug, Absatzabstand) aus dem Prüfbogen; die Silbentrennung steht unter Schreibhilfe."""
from __future__ import annotations

from lunivo_writer.ui.ribbon.tabs.baustein import k as _k


def bauen(register: dict) -> dict:
    tab = next(t for t in register["register"] if t["name"] == "Seitenlayout")
    alt = {g["name"]: g for g in tab["gruppen"]}
    knopf = {k["name"]: k for g in tab["gruppen"] for k in g.get("knoepfe", [])}

    def mit(_name, **kw):
        return {s: w for s, w in dict(knopf[_name], **kw).items() if w is not None}         # None nimmt einen Schlüssel weg

    designs = {"name": "Designs", "reihenfolge": True, "knoepfe": [
        mit("Designs", gross=True, tun=None, klappe="designsKlappe"), mit("Farben", text=True, tun=None, klappe="farbenKlappe"),
        mit("Schriftarten", symbol="Stil", text=True, tun=None, klappe="schriftartenKlappe"),
        mit("Effekte", gross=True, tun=None, klappe="effekteKlappe")]}
    raender = {"name": "Ränder", "felder": "raender", "reihenfolge": True, "knoepfe": [mit("Ränder", gross=True, menue=None, klappe="raenderKlappe")]}
    einrichten = {"name": "Seite einrichten", "pfeil": alt["Seite einrichten"].get("pfeil"), "reihenfolge": True, "knoepfe": [
        mit("Ausrichtung", name="Orientierung", gross=True, menue=None, klappe="ausrichtungKlappe"),
        mit("Größe", gross=True, menue=None, klappe="groesseKlappe"), mit("Spalten", gross=True, menue=None, klappe="spaltenKlappe"),
        mit("Textrichtung", gross=True, tun=None, klappe="textrichtungKlappe"),
        mit("Umbrüche", text=True, menue=None, klappe="umbruecheKlappe"), mit("Zeilennummern", text=True, tun=None, klappe="zeilennummernKlappe")]}
    hintergrund = {"name": "Seitenhintergrund", "reihenfolge": True, "knoepfe": [
        mit("Seitenfarbe", gross=True, tun=None, klappe="seitenfarbeKlappe"), mit("Seitenränder", gross=True, tun="seitenrahmen"),
        _k("netz", "Genko-Einstellung", "genkoEinstellung", True)]}         # Wasserzeichen: im Menü Seitenfarbe; Genko (japanisches Manuskriptraster) fehlt Lunivo noch und bleibt grau
    anordnen = {"name": "Anordnen", "reihenfolge": True, "knoepfe": [
        mit("Textfluss", gross=True), mit("Ausrichten", gross=True, tun=None, klappe="ausrichtenKlappe"), mit("Gruppieren", text=True), mit("Drehen", text=True),
        _k("objekte", "Auswahlbereich", "objekteWaehlen", True)]}
    absatz = {"name": "Absatz", "pfeil": alt["Absatz"].get("pfeil"), "reihenfolge": True, "knoepfe": [
        mit("Einzug", text=True), mit("Absatzabstand", text=True)]}                 # die Silbentrennung steht unter Schreibhilfe
    return dict(tab, gruppen=[designs, raender, einrichten, hintergrund, anordnen, absatz])
