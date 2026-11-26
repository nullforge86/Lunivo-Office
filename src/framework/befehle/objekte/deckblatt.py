"""Deckblätter: die Namen der Gestaltungen in der Reihenfolge der Galerie. Die Fachdaten liegen im Kern; die Oberfläche erhält unveränderliche Werte."""
from __future__ import annotations

from collections.abc import Mapping

from core.dokument.abschnitte import deckblatt_vorlagen as modell
from framework.anbindung import Daten, fest
from framework.befehle import ausfuehren

NAMEN: tuple[str, ...] = tuple(modell.NAMEN)


def entfernen(kennung: int) -> bool:
    """Nimmt das Deckblatt des Dokuments heraus (ein Rückgängig-Schritt). → ``False``, wenn es keines gab oder das Dokument schreibgeschützt ist."""
    return bool(ausfuehren(kennung, modell.entfernen))


def felder_formate(name: str, blatt_b: float, blatt_h: float, quer: bool, oben_px: float, links_px: float, rechts_px: float) -> tuple[tuple[str, Mapping[str, Daten], Mapping[str, Daten]], ...]:
    """Die Textfelder der Gestaltung ``name`` für ein Blatt ``blatt_b`` × ``blatt_h`` (Bildpunkte): je Feld (Text, Absatzformat, Zeichenformat), so dass
    jedes Feld an seiner Stelle der Gestaltung steht. ``oben_px``, ``links_px``, ``rechts_px``: Seitenränder des Blattes."""
    from framework.dokumentverwaltung.ausgabe import standard_engine
    g = modell.gestaltung(name)
    y = oben_px
    aus = []
    for feld in g.felder:
        spec = modell._schrift(feld, blatt_h if not quer else blatt_b, quer)
        ziel = feld.y * blatt_h
        af = {"abstand_vor": max(0.0, ziel - y) or None, "deckblatt": name,
              "ausrichtung": {"links": "links", "mitte": "mitte", "rechts": "rechts"}[feld.ausrichtung]}
        if feld.ausrichtung == "links":
            af["einzug_links"] = max(0.0, feld.x * blatt_b - links_px) or None
        else:
            af["einzug_links"] = max(0.0, 0.1 * blatt_b - links_px) or None
            af["einzug_rechts"] = max(0.0, 0.1 * blatt_b - rechts_px) or None
        zf = {"schrift": feld.schrift, "groesse_pt": feld.pt * (0.85 if quer else 1.0), "farbe": feld.farbe, "fett": True if feld.fett else None}
        aus.append((feld.text, fest(af), fest(zf)))
        m = standard_engine().font_metrics(spec)
        y = max(y, ziel) + (m.ascent + m.descent) * 1.15
    return tuple(aus)


def gruppe(name: str) -> str:
    """Die Gruppe der Galerie, zu der die Gestaltung ``name`` gehört."""
    return modell.gestaltung(name).gruppe
