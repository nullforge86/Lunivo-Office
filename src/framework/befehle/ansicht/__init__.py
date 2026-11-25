"""Tür des Pakets ``framework.befehle.ansicht``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "AnsichtBefehle": ("befehle", "AnsichtBefehle"),
    "GLIEDERUNG_AN": ("befehle", "GLIEDERUNG_AN"),
    "GLIEDERUNG_AUS": ("befehle", "GLIEDERUNG_AUS"),
    "LINEAL": ("einstellungen", "LINEAL"),
    "LINEAL_HOCH": ("einstellungen", "LINEAL_HOCH"),
    "OBERFLAECHE": ("einstellungen", "OBERFLAECHE"),
    "OBERFLAECHE_SCHLUESSEL": ("einstellungen", "OBERFLAECHE_SCHLUESSEL"),
    "SILBEN_AN": ("lesehilfe", "SILBEN_AN"),
    "THEMA": ("einstellungen", "THEMA"),
    "VERSTECKT_ZEIGEN": ("einstellungen", "VERSTECKT_ZEIGEN"),
    "VORGABEN": ("einstellungen", "VORGABEN"),
    "WEICH": ("einstellungen", "WEICH"),
    "aktiv": ("sprechblasen", "aktiv"),
    "blasen_px": ("sprechblasen", "blasen_px"),
    "blasen_schrift": ("sprechblasen", "blasen_schrift"),
    "breite_mm": ("sprechblasen", "breite_mm"),
    "einstellung_lesen": ("silbenfarben", "einstellung_lesen"),
    "einstellung_speichern": ("silbenfarben", "einstellung_speichern"),
    "farben": ("silbenfarben", "farben"),
    "fuer_den_druck": ("silbenfarben", "fuer_den_druck"),
    "karten_pt": ("sprechblasen", "karten_pt"),
    "konfig_lesen": ("sprechblasen", "konfig_lesen"),
    "lineal_hoch_umschalten": ("einstellungen", "lineal_hoch_umschalten"),
    "lineal_hoch_zeigen": ("einstellungen", "lineal_hoch_zeigen"),
    "lineal_umschalten": ("einstellungen", "lineal_umschalten"),
    "lineal_zeigen": ("einstellungen", "lineal_zeigen"),
    "messen": ("sprechblasen", "messen"),
    "neue_einstellung": ("silbenfarben", "neue_einstellung"),
    "oberflaeche_umschalten": ("einstellungen", "oberflaeche_umschalten"),
    "oberflaeche_zuruecksetzen": ("einstellungen", "oberflaeche_zuruecksetzen"),
    "ortszeit": ("sprechblasen", "ortszeit"),
    "sammeln": ("sprechblasen", "sammeln"),
    "silben": ("silbenfarben", "silben"),
    "silben_an": ("lesehilfe", "silben_an"),
    "silben_umschalten": ("lesehilfe", "silben_umschalten"),
    "silbenfarben_katalog": ("silbenfarben", "katalog"),
    "sprechblasen_katalog": ("sprechblasen", "katalog"),
    "stapeln": ("sprechblasen", "stapeln"),
    "symbolleisten_statt_register": ("einstellungen", "symbolleisten_statt_register"),
    "thema": ("einstellungen", "thema"),
    "verstecktes_umschalten": ("einstellungen", "verstecktes_umschalten"),
    "verstecktes_zeigen": ("einstellungen", "verstecktes_zeigen"),
    "vorlagen_ordner": ("vorlagen", "vorlagen_ordner"),
    "weich": ("einstellungen", "weich"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "befehle":
        from . import befehle as _datei
    elif datei == "einstellungen":
        from . import einstellungen as _datei
    elif datei == "lesehilfe":
        from . import lesehilfe as _datei
    elif datei == "silbenfarben":
        from . import silbenfarben as _datei
    elif datei == "sprechblasen":
        from . import sprechblasen as _datei
    elif datei == "vorlagen":
        from . import vorlagen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
