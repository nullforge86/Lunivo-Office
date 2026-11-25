"""Tür des Pakets ``core.layout.drucklayout``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ABSATZENDE_BREITE": ("schreibmarke", "ABSATZENDE_BREITE"),
    "AbsatzLayout": ("absatzlayout", "AbsatzLayout"),
    "AbsatzOrt": ("ergebnis", "AbsatzOrt"),
    "BEWEGUNGEN": ("navigation", "BEWEGUNGEN"),
    "BLATT_ABSTAND_PX": ("geometrie", "BLATT_ABSTAND_PX"),
    "CURSOR_BREITE": ("schreibmarke", "CURSOR_BREITE"),
    "Ergebnis": ("ergebnis", "Ergebnis"),
    "FORTLAUFEND": ("geometrie", "FORTLAUFEND"),
    "FUELLZEICHEN": ("formatwerte", "FUELLZEICHEN"),
    "FussnotenLayout": ("fussnotenlayout", "FussnotenLayout"),
    "GERADE": ("geometrie", "GERADE"),
    "HOCH_VERSATZ": ("formatwerte", "HOCH_VERSATZ"),
    "KAPITAELCHEN_GROESSE": ("formatwerte", "KAPITAELCHEN_GROESSE"),
    "LayoutEngine": ("engine", "LayoutEngine"),
    "MIN_SPALTENBREITE": ("geometrie", "MIN_SPALTENBREITE"),
    "MIN_TABELLENBREITE": ("geometrie", "MIN_TABELLENBREITE"),
    "MIN_TEILHOEHE": ("geometrie", "MIN_TEILHOEHE"),
    "NOTEN_ABSTAND": ("geometrie", "NOTEN_ABSTAND"),
    "NOTEN_LINIE_ANTEIL": ("geometrie", "NOTEN_LINIE_ANTEIL"),
    "NOTEN_SCHRIFT": ("geometrie", "NOTEN_SCHRIFT"),
    "NOTEN_SEITENANTEIL": ("geometrie", "NOTEN_SEITENANTEIL"),
    "NOTEN_TRENNER": ("geometrie", "NOTEN_TRENNER"),
    "OBJEKT_ABSTAND": ("objektlayout", "OBJEKT_ABSTAND"),
    "PX_JE_PT": ("formatwerte", "PX_JE_PT"),
    "Platz": ("ergebnis", "Platz"),
    "STANDARD_FAMILIE": ("formatwerte", "STANDARD_FAMILIE"),
    "STANDARD_GROESSE_PT": ("formatwerte", "STANDARD_GROESSE_PT"),
    "STANDARD_OBJEKT": ("geometrie", "STANDARD_OBJEKT"),
    "STRICHART": ("formatwerte", "STRICHART"),
    "Seite": ("ergebnis", "Seite"),
    "TAB_ABSTAND": ("formatwerte", "TAB_ABSTAND"),
    "TAB_ARTEN": ("formatwerte", "TAB_ARTEN"),
    "TIEF_VERSATZ": ("formatwerte", "TIEF_VERSATZ"),
    "TabellenLayout": ("tabellenlayout", "TabellenLayout"),
    "TextUmfluss": ("textumfluss", "TextUmfluss"),
    "UMBRUCH_MIT_UMFLUSS": ("objektlayout", "UMBRUCH_MIT_UMFLUSS"),
    "UNGERADE": ("geometrie", "UNGERADE"),
    "WEB_RAND": ("geometrie", "WEB_RAND"),
    "ZEILENABSTAND": ("formatwerte", "ZEILENABSTAND"),
    "ZEILENENDE": ("navigation", "ZEILENENDE"),
    "ZELLEN_POLSTER": ("geometrie", "ZELLEN_POLSTER"),
    "ZELLEN_ZWISCHENRAUM": ("geometrie", "ZELLEN_ZWISCHENRAUM"),
    "absatzformat": ("formatwerte", "absatzformat"),
    "absatzrahmen": ("formatwerte", "absatzrahmen"),
    "abstaende": ("formatwerte", "abstaende"),
    "ausrichtung": ("formatwerte", "ausrichtung"),
    "auswahl_rechtecke": ("schreibmarke", "auswahl_rechtecke"),
    "bewegen": ("navigation", "bewegen"),
    "cursor_rechteck": ("schreibmarke", "cursor_rechteck"),
    "einzuege": ("formatwerte", "einzuege"),
    "farbwert": ("formatwerte", "farbwert"),
    "formatwerte_AUSRICHTUNG": ("formatwerte", "AUSRICHTUNG"),
    "formatwerte_regeln": ("formatwerte", "regeln"),
    "hintergrund": ("formatwerte", "hintergrund"),
    "kapitaelchen": ("formatwerte", "kapitaelchen"),
    "kapitaelchen_stuecke": ("formatwerte", "kapitaelchen_stuecke"),
    "kopf_fuss_setzen": ("kopf_fusslayout", "kopf_fuss_setzen"),
    "kopf_fusslayout_AUSRICHTUNG": ("kopf_fusslayout", "AUSRICHTUNG"),
    "listen_einzug": ("formatwerte", "listen_einzug"),
    "objekte_objekt_rechteck": ("objekte", "objekt_rechteck"),
    "objektlayout_objekt_rechteck": ("objektlayout", "objekt_rechteck"),
    "option": ("formatwerte", "option"),
    "richtung": ("formatwerte", "richtung"),
    "schreibweise": ("formatwerte", "schreibweise"),
    "schrift": ("formatwerte", "schrift"),
    "spaltenumbruch_vor": ("formatwerte", "spaltenumbruch_vor"),
    "stil": ("formatwerte", "stil"),
    "tabfuellung": ("formatwerte", "tabfuellung"),
    "tabstopps": ("formatwerte", "tabstopps"),
    "umbruch_art": ("absatzlayout", "umbruch_art"),
    "umbruch_nach": ("formatwerte", "umbruch_nach"),
    "umbruch_stelle": ("regeln", "umbruch_stelle"),
    "umbruch_vor": ("formatwerte", "umbruch_vor"),
    "wort_bei": ("navigation", "wort_bei"),
    "zeichenformat": ("formatwerte", "zeichenformat"),
    "zeilenabstand": ("formatwerte", "zeilenabstand"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "absatzlayout":
        from . import absatzlayout as _datei
    elif datei == "engine":
        from . import engine as _datei
    elif datei == "ergebnis":
        from . import ergebnis as _datei
    elif datei == "formatwerte":
        from . import formatwerte as _datei
    elif datei == "fussnotenlayout":
        from . import fussnotenlayout as _datei
    elif datei == "geometrie":
        from . import geometrie as _datei
    elif datei == "kopf_fusslayout":
        from . import kopf_fusslayout as _datei
    elif datei == "navigation":
        from . import navigation as _datei
    elif datei == "objekte":
        from . import objekte as _datei
    elif datei == "objektlayout":
        from . import objektlayout as _datei
    elif datei == "regeln":
        from . import regeln as _datei
    elif datei == "schreibmarke":
        from . import schreibmarke as _datei
    elif datei == "tabellenlayout":
        from . import tabellenlayout as _datei
    elif datei == "textumfluss":
        from . import textumfluss as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
