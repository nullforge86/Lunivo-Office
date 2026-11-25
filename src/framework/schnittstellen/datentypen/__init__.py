"""Tür des Pakets ``framework.schnittstellen.datentypen``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "Art": ("ereignisdaten", "Art"),
    "Auswahlansicht": ("dokumentdaten", "Auswahlansicht"),
    "Befehl": ("befehlsdaten", "Befehl"),
    "EffektDaten": ("effektdaten", "EffektDaten"),
    "EffektVorgabe": ("effektdaten", "EffektVorgabe"),
    "EffektWert": ("effektdaten", "EffektWert"),
    "Ereignis": ("ereignisdaten", "Ereignis"),
    "Ergebnis": ("befehlsdaten", "Ergebnis"),
    "FeldTreffer": ("formulardaten", "FeldTreffer"),
    "Feldbeschreibung": ("formulardaten", "Feldbeschreibung"),
    "Geoeffnet": ("geoeffnet", "Geoeffnet"),
    "Menueeintrag": ("menuedaten", "Menueeintrag"),
    "Rechteck": ("dokumentdaten", "Rechteck"),
    "Schreibmarke": ("cursordaten", "Schreibmarke"),
    "Seitenansicht": ("layoutdaten", "Seitenansicht"),
    "Seitenuebersicht": ("layoutdaten", "Seitenuebersicht"),
    "TextfeldVorgabe": ("objektdaten", "TextfeldVorgabe"),
    "Wasserzeichenangabe": ("wasserzeichendaten", "Wasserzeichenangabe"),
    "Wert": ("einstellungsdaten", "Wert"),
    "WordartVorgabe": ("objektdaten", "WordartVorgabe"),
    "Zeichenbefehl": ("zeichenliste", "Zeichenbefehl"),
    "Zeichenliste": ("zeichenliste", "Zeichenliste"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "befehlsdaten":
        from . import befehlsdaten as _datei
    elif datei == "cursordaten":
        from . import cursordaten as _datei
    elif datei == "dokumentdaten":
        from . import dokumentdaten as _datei
    elif datei == "effektdaten":
        from . import effektdaten as _datei
    elif datei == "einstellungsdaten":
        from . import einstellungsdaten as _datei
    elif datei == "ereignisdaten":
        from . import ereignisdaten as _datei
    elif datei == "formulardaten":
        from . import formulardaten as _datei
    elif datei == "geoeffnet":
        from . import geoeffnet as _datei
    elif datei == "layoutdaten":
        from . import layoutdaten as _datei
    elif datei == "menuedaten":
        from . import menuedaten as _datei
    elif datei == "objektdaten":
        from . import objektdaten as _datei
    elif datei == "wasserzeichendaten":
        from . import wasserzeichendaten as _datei
    elif datei == "zeichenliste":
        from . import zeichenliste as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
