"""Diagramm: Elemente (Diagrammelemente-Liste) und die Daten-Schlüssel der Teilformate; gezeichnet wird im Kern. Keine Oberfläche.

Die Daten des Diagramms (``a["daten"]``) kennen zusätzlich zu den Angaben aus ``editor/diagramme/diagramm.py``:
``elemente``      {achsen, achsentitel, datentabelle, fehlerindikatoren, gitter, trendlinie: bool} — fehlt ein Schlüssel, gilt ``STANDARD_ELEMENTE``;
                  Titel, Legende (mit Lage) und Datenbeschriftungen liegen weiter in ``titel_an``, ``legende``/``legende_pos``, ``labels``;
``ausgeblendet``  {"reihen": [Namen], "rubriken": [Namen]} (Diagrammfilter);
``teil_format``   Teil-Schlüssel → {fuell, linie, schatten, reflektion, leuchten, weich, d3, drehung, text, achse, reihe} (jeder Schlüssel darf fehlen,
                  Aufbau in ``diagramm_format``);
``teil``          der gewählte Diagrammteil (Schlüssel wie in ``diagramm.teile``); ``alt_titel``/``alt_beschreibung``: Alternativtext."""
from __future__ import annotations

ELEMENTE = ("achsen", "achsentitel", "titel", "datenbeschriftung", "datentabelle", "fehlerindikatoren", "gitter", "legende", "trendlinie")
ELEMENT_NAMEN = {"achsen": "Achsen", "achsentitel": "Achsentitel", "titel": "Diagrammtitel", "datenbeschriftung": "Datenbeschriftungen",
                 "datentabelle": "Datentabelle", "fehlerindikatoren": "Fehlerindikatoren", "gitter": "Gitternetzlinien", "legende": "Legende",
                 "trendlinie": "Trendlinie"}
STANDARD_ELEMENTE = {"achsen": True, "achsentitel": False, "datentabelle": False, "fehlerindikatoren": False, "gitter": True, "trendlinie": False}
LEGENDEN_LAGEN = ("oben", "unten", "links", "rechts")


def elemente_wirksam(d: dict) -> dict:
    """Alle neun Elemente mit ihrem Wert: Wahrheitswerte, bei ``legende`` die Lage (``oben`` … ``rechts``) oder ``aus``."""
    el = {**STANDARD_ELEMENTE, **(d.get("elemente") or {})}
    el["titel"] = bool(d.get("titel_an", True))
    el["datenbeschriftung"] = bool(d.get("labels", False))
    el["legende"] = d.get("legende_pos", "unten") if d.get("legende", True) else "aus"
    return el
