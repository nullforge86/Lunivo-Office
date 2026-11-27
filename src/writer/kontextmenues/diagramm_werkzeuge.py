"""Kontext-Reiter „Diagrammtools“ nach der Vorlage (erscheint bei markiertem Diagramm, Kontext ``diagramm``).

Gruppen von links nach rechts: Diagrammelement hinzufügen ▾ · Schnelllayout ▾ · Farbe ändern ▾ · Galerie der vier Diagrammstile ·
Diagrammtyp ändern (Fenster, aktuelle Art vorgewählt) mit zehn kleinen Typ-Knöpfen (Klick ändert die Art direkt, Pfeil: Untertypen) · Daten auswählen · Daten bearbeiten · Formatieren und Formatvorlage zurücksetzen.
Jeder Knopf ist ein ``diagramm…``-Befehl (kern/befehle/kontextreiter/diagrammtools.py) oder ein Popup des Bandes (oberflaeche/baukasten/dropdown/objektmenues/diagramm_popups.py, dieselben wie
in der Schnellleiste am Diagramm); die Stilkacheln zeichnet oberflaeche/baukasten/dropdown/objektmenues/bild_diagramm_menues.py. Ganz rechts steht das Auswahlfeld „Diagrammbereich“ mit
„Formatieren“ und „Formatvorlage zurücksetzen“ darunter (``diagramm_bereich_feld``)."""
from __future__ import annotations

from writer.werkzeugleisten.reiter.baustein import k as _k

# (Symbol, Name) der kleinen Typ-Knöpfe; zeilenweise gelesen wie in der Vorlage: obere Reihe Säule, Balken, Linie, Netz, Kurs — untere Reihe
# Fläche, Kombination, Kreis, Ring, Punkt. Ein Klick öffnet nur die Untertypen der Gruppe; geändert wird die Diagrammart erst mit der Wahl darin.
_TYPEN = (("saeule", "Säule"), ("flaeche", "Fläche"), ("balkenquer", "Balken"), ("kombination", "Kombination"), ("linie", "Linie"),
          ("kreis", "Kreis"), ("netz", "Netz"), ("donut", "Ring"), ("kurs", "Kurs"), ("punktwolke", "Punkt (XY)"))


def _typ_knopf(sym: str, name: str) -> dict:
    """Ein Typ-Knopf: die Klappe seiner Gruppe. „Ring“ hat keine Untertypen und setzt die Diagrammart deshalb selbst."""
    if sym == "donut":
        return _k(sym, "Diagrammtyp: " + name, 'diagrammTypAendern:["ring"]')
    return _k(sym, "Diagrammtyp: " + name, None, klappe="diagrammTyp_" + sym)

DIAGRAMMTOOLS = {"name": "Diagrammtools", "kontext": "diagramm", "gruppen": [
    {"name": "Elemente", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("diagrammteil", "Diagrammelement hinzufügen", None, True, klappe="diagrammElement"),
        _k("layout-template", "Schnelllayout", None, True, klappe="diagrammSchnelllayout"),
        _k("palette", "Farbe ändern", None, True, klappe="diagrammFarben")]},
    {"name": "Diagrammstile", "ohne_titel": True, "galerie": "diagrammStile", "knoepfe": []},
    {"name": "Diagrammtyp", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("chart-no-axes-combined", "Diagrammtyp ändern", "diagrammTypAendern", True)]
        + [_typ_knopf(sym, name) for sym, name in _TYPEN]},
    {"name": "Daten", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("tabelleWahl", "Daten auswählen", None, True, klappe="diagrammFilter"),      # welche Reihen und Rubriken das Diagramm zeigt, und ihre Namen
        _k("square-pen", "Daten bearbeiten", "diagrammDatenBearbeiten", True)]},
    {"name": "Bereich", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        {"feld": "diagrammBereich"}]},
]}
