"""Reiter „Start“ in der Anordnung der Vorlage."""
from __future__ import annotations

from lunivo_writer.ui.ribbon.tabs.baustein import k as _k


def bauen(start: dict) -> dict:
    """Reiter Start in der Anordnung der Vorlage: Zwischenablage (Einfügen, Ausschneiden/Kopieren, Format übertragen), Schriftart mit
    Name und Größe in einer Zeile, Absatz, Stile, dann die Gruppe Bearbeiten (Suchen, Auswählen, Wort-Extras, Einstellungen als Knöpfe mit Text neben dem Symbol); die Stile zeigen zwei Spalten, der Rest steht im Pfeil."""
    alt = {g["name"]: g for g in start["gruppen"]}
    ablage = {"name": "Zwischenablage", "reihenfolge": True, "knoepfe": [
        _k("kleben", "Einfügen", "einfuegen", True, klappe="einfuegenKlappe"),
        _k("schere", "Ausschneiden", "ausschneiden", text=True),
        _k("kopie", "Kopieren", "kopieren", text=True),
        _k("pinsel", "Format übertragen", "formatUebertragen", True)]}
    schrift = dict(alt["Schriftart"], felder="zeile", knoepfe=[
        dict(e, tun="durchJetzt", klappe="durchKlappe") if e.get("name") == "Durchgestrichen" else e for e in alt["Schriftart"]["knoepfe"]])
    absatz = dict(alt["Absatz"])
    bearbeiten = {"name": "Bearbeiten", "reihenfolge": True, "knoepfe": [                 # vier Knöpfe in zwei Spalten statt vier großen Gruppen
        _k("lupe", "Suchen oder ersetzen", text=True, klappe="suchenKlappe"),
        _k("objekte", "Auswählen", text=True, klappe="auswaehlenKlappe"),
        _k("wortextras", "Wort-Extras", text=True, klappe="wortExtrasKlappe"),
        _k("zahnrad", "Einstellungen", text=True, klappe="einstellungenKlappe")]}
    return dict(start, gruppen=[ablage, schrift, absatz, dict(alt["Stile"], spalten=2), bearbeiten])

