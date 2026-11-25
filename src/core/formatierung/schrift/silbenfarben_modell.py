"""Silbenfarben modell: aus ``vcl.qt.schrift.silbenfarben`` herausgelöst."""
from __future__ import annotations
import re
from core.formatierung.farben.farben import Farbe


PALETTEN = {
    "Blau / Rot": ["#1f5fbf", Farbe.ROT],
    "Blau / Orange": ["#1f5fbf", "#d9480f"],
    "Grün / Violett": ["#2b8a3e", "#862e9c"],
    "Dunkelblau / Braun": ["#1b3a6b", "#8a4b14"],
    "Drei Farben (Blau, Rot, Grün)": ["#1f5fbf", Farbe.ROT, "#2b8a3e"],
    "Eigene Farben": None,
}


DARSTELLUNGEN = ["Schriftfarbe", "Hintergrund (Marker)", "Schriftfarbe und Hintergrund"]


BEISPIEL = ("Die Silbenfarben helfen beim Lesen: Wörter wie Schmetterling, Wanderung und Computertastatur "
            "werden in ihre Teile zerlegt.")


STANDARD = {"an": False, "palette": "Blau / Rot", "eigene": ["#1f5fbf", Farbe.ROT, "#2b8a3e"], "anzahl_eigene": 2,
            "darstellung": "Schriftfarbe", "fett": False, "einsilbig": True, "neu_pro_wort": True, "mindestens": 4,
            "nur_absatz": False, "drucken": False, "sprache": "de_DE"}


_WORT = re.compile(r"[^\W\d_]{2,}", re.UNICODE)


def konfig_speichern(settings, k: dict) -> None:
    for n, v in k.items():
        if n == "eigene":
            v = ",".join(v)
        settings.set("lesehilfe/silben/" + n, v)


def farben(k: dict) -> list[str]:
    pal = PALETTEN.get(k["palette"])
    return list(pal) if pal else list(k["eigene"][:k["anzahl_eigene"]])


def verfuegbar(sprache: str = "de_DE") -> bool:
    """Die Regeln brauchen nichts außer Python; pyphen verbessert nur die Wortgrenzen in Zusammensetzungen."""
    return True


def silben_an(settings) -> bool:
    """Ist die Lesehilfe „Silben farbig“ eingeschaltet? (Nur dieser eine Schlüssel; alle Werte liest ``konfig_lesen`` in der Anzeige.)"""
    return bool(settings.get_bool("lesehilfe/silben/an", STANDARD["an"]))


def silben(wort: str, sprache: str = "de_DE") -> tuple[str, ...]:
    """Das Wort in deutsche Sprechsilben (ein Eintrag, wenn es sich nicht teilen lässt)."""
    from core.korrektur.silbentrennung.silben_de import silben as _silben
    return _silben(wort)
