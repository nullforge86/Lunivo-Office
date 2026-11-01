"""Reiter „Start“ in der Anordnung von WPS Office."""
from __future__ import annotations

from lunivo_writer.ui.ribbon.tabs.baustein import k as _k


def bauen(start: dict) -> dict:
    """Reiter Start in kompakter Layout-Anordnung: Einfügen, Schrift, Absatz, Stile, Extras, Suchen, Auswählen und Einstellungen."""
    alt = {g["name"]: g for g in start["gruppen"]}
    ablage = {"name": "Einfügen", "reihenfolge": True, "knoepfe": [
        _k("kleben", "Einfügen", "einfuegen", True, klappe="einfuegenKlappe"),
        _k("schere", "Ausschneiden", "ausschneiden", text=True),
        _k("kopie", "Kopieren", "kopieren", text=True),
        _k("pinsel", "Format", "formatUebertragen", True)]}
    schrift = dict(alt["Schriftart"], felder="zeile", knoepfe=[
        dict(e, tun="durchJetzt", klappe="durchKlappe") if e.get("name") == "Durchgestrichen" else e for e in alt["Schriftart"]["knoepfe"]])
    absatz = dict(alt["Absatz"])
    extras = {"name": "Extras", "reihenfolge": True, "knoepfe": [
        _k("wortextras", "Extras", gross=True, klappe="wortExtrasKlappe")]}
    suchen = {"name": "Suchen", "reihenfolge": True, "knoepfe": [
        _k("lupe", "Suchen", gross=True, klappe="suchenKlappe")]}
    waehlen = {"name": "Auswählen", "reihenfolge": True, "knoepfe": [
        _k("objekte", "Auswählen", gross=True, klappe="auswaehlenKlappe")]}
    einst = {"name": "Einst.", "reihenfolge": True, "knoepfe": [
        _k("zahnrad", "Einst.", gross=True, klappe="einstellungenKlappe")]}
    return dict(start, gruppen=[ablage, schrift, absatz, alt["Stile"], extras, suchen, waehlen, einst])
