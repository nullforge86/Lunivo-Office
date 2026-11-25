"""Tür des Pakets ``framework.befehle.bearbeiten``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "Angabe": ("vorlagenkatalog", "Angabe"),
    "BearbeitenBefehle": ("befehle", "BearbeitenBefehle"),
    "ELEMENTE": ("gehe_zu", "ELEMENTE"),
    "Katalogwert": ("formatvorlagen", "Katalogwert"),
    "MENUE": ("wortextras", "MENUE"),
    "Tabstopp": ("formatvorlagen", "Tabstopp"),
    "aendern": ("vorlagenkatalog", "aendern"),
    "als_json": ("vorlagenkatalog", "als_json"),
    "als_json_neu": ("vorlagenkatalog", "als_json_neu"),
    "anlegen": ("vorlagenkatalog", "anlegen"),
    "definition": ("vorlagenkatalog", "definition"),
    "design": ("vorlagenkatalog", "design"),
    "design_namen": ("vorlagenkatalog", "design_namen"),
    "effekte": ("vorlagenkatalog", "effekte"),
    "eigene_angaben": ("vorlagenkatalog", "eigene_angaben"),
    "eingabe_titel": ("gehe_zu", "eingabe_titel"),
    "eingebaute_namen": ("vorlagenkatalog", "eingebaute_namen"),
    "farbschemen": ("vorlagenkatalog", "farbschemen"),
    "formatvorlage_abgleichen": ("formatvorlagen", "formatvorlage_abgleichen"),
    "formatvorlage_anwenden": ("formatvorlagen", "formatvorlage_anwenden"),
    "formatvorlage_aus_auswahl": ("formatvorlagen", "formatvorlage_aus_auswahl"),
    "gehe_zu_element": ("gehe_zu", "gehe_zu_element"),
    "hat_elemente": ("gehe_zu", "hat_elemente"),
    "ist_eigen": ("vorlagenkatalog", "ist_eigen"),
    "laden": ("vorlagenkatalog", "laden"),
    "laden_neu": ("vorlagenkatalog", "laden_neu"),
    "loeschen": ("vorlagenkatalog", "loeschen"),
    "namen": ("vorlagenkatalog", "namen"),
    "pruefe_name": ("vorlagenkatalog", "pruefe_name"),
    "schriftpaare": ("vorlagenkatalog", "schriftpaare"),
    "tabs_als_text": ("formatvorlagen", "tabs_als_text"),
    "tabs_aus_text": ("formatvorlagen", "tabs_aus_text"),
    "ueberschrift_farbe": ("vorlagenkatalog", "ueberschrift_farbe"),
    "vorlage": ("vorlagenkatalog", "vorlage"),
    "wortextra_ausfuehren": ("wortextras", "wortextra_ausfuehren"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "befehle":
        from . import befehle as _datei
    elif datei == "formatvorlagen":
        from . import formatvorlagen as _datei
    elif datei == "gehe_zu":
        from . import gehe_zu as _datei
    elif datei == "vorlagenkatalog":
        from . import vorlagenkatalog as _datei
    elif datei == "wortextras":
        from . import wortextras as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
