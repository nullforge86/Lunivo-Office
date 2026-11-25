"""Silbenfarben (Lesehilfe): Abfragen und Befehle. Die Einstellungen liegen im JSON-Speicher, die Silben und Farben berechnet der Kern."""
from __future__ import annotations

import re
from dataclasses import replace

from core.formatierung.schrift import silbenfarben_modell as modell
from framework.schnittstellen.einstellungen import Einstellungen
from framework.schnittstellen.silbenfarben import SilbenEinstellung, SilbenKatalog

_SCHLUESSEL = "lesehilfe/silben/"
_FARBE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def _einstellung(k: dict) -> SilbenEinstellung:
    return SilbenEinstellung(an=bool(k["an"]), palette=k["palette"], eigene=tuple(k["eigene"]), anzahl_eigene=int(k["anzahl_eigene"]),
                             darstellung=k["darstellung"], fett=bool(k["fett"]), einsilbig=bool(k["einsilbig"]), neu_pro_wort=bool(k["neu_pro_wort"]),
                             mindestens=int(k["mindestens"]), nur_absatz=bool(k["nur_absatz"]), drucken=bool(k["drucken"]), sprache=k["sprache"])


def katalog() -> SilbenKatalog:
    """Paletten, Darstellungen, Beispieltext, Wortmuster und Standardwerte."""
    return SilbenKatalog(paletten=tuple(modell.PALETTEN), darstellungen=tuple(modell.DARSTELLUNGEN), beispiel=modell.BEISPIEL,
                         wortmuster=modell._WORT.pattern, standard=_einstellung(modell.STANDARD))


def einstellung_lesen(e: Einstellungen) -> SilbenEinstellung:
    """Die Einstellungen als eine Beschreibung mit allen Feldern (fehlende oder ungültige Werte bekommen den Standard)."""
    st = modell.STANDARD
    k = dict(st)
    k["an"] = e.get_bool(_SCHLUESSEL + "an", st["an"])
    pal = e.get(_SCHLUESSEL + "palette", st["palette"])
    k["palette"] = pal if pal in modell.PALETTEN else st["palette"]
    eig = [c for c in str(e.get(_SCHLUESSEL + "eigene", ",".join(st["eigene"]))).split(",") if _FARBE.match(c)]
    k["eigene"] = (eig + list(st["eigene"]))[:3]
    k["anzahl_eigene"] = min(3, max(2, int(e.get(_SCHLUESSEL + "anzahl_eigene", 2))))
    d = e.get(_SCHLUESSEL + "darstellung", st["darstellung"])
    k["darstellung"] = d if d in modell.DARSTELLUNGEN else st["darstellung"]
    for n in ("fett", "einsilbig", "neu_pro_wort", "nur_absatz", "drucken"):
        k[n] = e.get_bool(_SCHLUESSEL + n, st[n])
    k["mindestens"] = min(10, max(2, int(e.get(_SCHLUESSEL + "mindestens", st["mindestens"]))))
    k["sprache"] = e.get(_SCHLUESSEL + "sprache", e.get("silben/sprache", "de_DE"))
    return _einstellung(k)


def einstellung_speichern(e: Einstellungen, k: SilbenEinstellung) -> None:
    for n, v in vars(k).items():
        e.set(_SCHLUESSEL + n, ",".join(v) if n == "eigene" else v)


def neue_einstellung(**felder: object) -> SilbenEinstellung:
    """Eine Einstellung aus den Standardwerten, mit den angegebenen Feldern überschrieben."""
    return replace(katalog().standard, **felder)


def farben(k: SilbenEinstellung) -> tuple[str, ...]:
    """Die Farben der Silben (Palette oder eigene) als Farbtexte."""
    pal = modell.PALETTEN.get(k.palette)
    return tuple(pal) if pal else tuple(k.eigene[:k.anzahl_eigene])


def silben(wort: str, sprache: str = "de_DE") -> tuple[str, ...]:
    """Das Wort in deutsche Sprechsilben (ein Eintrag, wenn es sich nicht teilen lässt)."""
    return modell.silben(wort, sprache)


def fuer_den_druck(k: SilbenEinstellung) -> SilbenEinstellung | None:
    """Die Einstellung für Druck und PDF (immer im ganzen Text) oder ``None``, wenn die Silbenfarben dort nicht erscheinen sollen."""
    return replace(k, nur_absatz=False) if k.an and k.drucken else None
