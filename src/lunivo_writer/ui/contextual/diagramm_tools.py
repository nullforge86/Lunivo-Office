"""Kontext-Reiter „Diagrammtools“ nach der WPS-Vorlage (erscheint bei markiertem Diagramm, Kontext ``diagramm``).

Gruppen von links nach rechts: Diagrammelement hinzufügen ▾ · Schnelllayout ▾ · Farbe ändern ▾ · Galerie der vier Diagrammstile ·
Diagrammtyp ändern (Fenster, aktuelle Art vorgewählt) mit zehn kleinen Typ-Knöpfen (Klick ändert die Art direkt, Pfeil: Untertypen) · Daten auswählen · Daten bearbeiten · Formatieren und Formatvorlage zurücksetzen.
Jeder Knopf ist ein ``diagramm…``-Befehl (core/befehle/diagrammtools.py) oder ein Popup des Bandes (ui/baukasten/diagramm_popups.py, dieselben wie
in der Schnellleiste am Diagramm); die Stilkacheln zeichnet ui/baukasten/bild_diagramm_menues.py. Ganz rechts steht das Auswahlfeld „Diagrammbereich“ mit
„Formatieren“ und „Formatvorlage zurücksetzen“ darunter (``diagramm_bereich_feld``)."""
from __future__ import annotations

from lunivo_writer.ui.ribbon.tabs.baustein import k as _k

# (Symbol, Name) der kleinen Typ-Knöpfe; zeilenweise gelesen: obere Reihe Säule, Balken, Linie, Netz, Kurs — untere Reihe Kombination, Fläche, Kreis, Ring, Punkt
_TYPEN = (("saeule", "Säule"), ("kombination", "Kombination"), ("balkenquer", "Balken"), ("flaeche", "Fläche"), ("linie", "Linie"),
          ("kreis", "Kreis"), ("netz", "Netz"), ("donut", "Ring"), ("kurs", "Kurs"), ("punktwolke", "Punkt (XY)"))

# Untertyp, den der Klick auf den Knopf selbst setzt (der Pfeil daneben öffnet die Untertypen der Gruppe)
_STANDARD = {"saeule": "saeule_gruppiert", "kombination": "kombination", "balkenquer": "balken_gruppiert", "flaeche": "flaeche", "linie": "linie",
             "kreis": "kreis", "netz": "netz", "donut": "ring", "kurs": "kurs_hts", "punktwolke": "punkte"}

DIAGRAMMTOOLS = {"name": "Diagrammtools", "kontext": "diagramm", "gruppen": [
    {"name": "Elemente", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("diagrammteil", "Diagrammelement hinzufügen", None, True, klappe="diagrammElement"),
        _k("layout-template", "Schnelllayout", None, True, klappe="diagrammSchnelllayout"),
        _k("palette", "Farbe ändern", None, True, klappe="diagrammFarben")]},
    {"name": "Diagrammstile", "ohne_titel": True, "galerie": "diagrammStile", "knoepfe": []},
    {"name": "Diagrammtyp", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("chart-no-axes-combined", "Diagrammtyp ändern", "diagrammTypAendern", True)]
        + [_k(sym, "Diagrammtyp: " + name, 'diagrammTypAendern:["%s"]' % _STANDARD[sym],
              klappe=None if sym == "donut" else "diagrammTyp_" + sym) for sym, name in _TYPEN]},
    {"name": "Daten", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("table-2", "Daten auswählen", "diagrammDatenBearbeiten", True),
        _k("square-pen", "Daten bearbeiten", "diagrammDatenBearbeiten", True)]},
    {"name": "Bereich", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        {"feld": "diagrammBereich"}]},
]}
