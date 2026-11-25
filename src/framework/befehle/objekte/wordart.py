"""WordArt und Texteffekte: Vorgaben, Auswahllisten und die Umwandlung der Effekte in den Text des Zeichenformats. Die Fachdaten liegen im Kern; die
Oberfläche erhält unveränderliche Beschreibungen."""
from __future__ import annotations

from core.objekte.wordart import textfx_daten as daten
from core.objekte.wordart import textfx_vorgaben_modell as vorgaben
from framework.schnittstellen.datentypen.effektdaten import EffektDaten, EffektVorgabe, EffektWert

PX: float = daten.PX
MATERIAL: tuple[tuple[str, str], ...] = tuple(daten.MATERIAL)
BELEUCHTUNG: tuple[tuple[str, str], ...] = tuple(daten.BELEUCHTUNG)
WARP_FORMEN: tuple[tuple[str, str], ...] = tuple(daten.WARP_FORMEN)


def _wert_aus_kern(w: object) -> EffektWert:
    if isinstance(w, dict):
        return _aus_kern(w)
    if isinstance(w, (list, tuple)):
        return tuple(_wert_aus_kern(x) for x in w)
    return w                                               # type: ignore[return-value]  (Zahl, Text, Wahrheitswert, None)


def _aus_kern(fx: dict) -> EffektDaten:
    """Entkoppelte, unveränderliche Kopie eines Effekts des Kerns."""
    return EffektDaten(tuple((str(k), _wert_aus_kern(v)) for k, v in fx.items()))


def _wert_zum_kern(w: EffektWert) -> object:
    if isinstance(w, EffektDaten):
        return _zum_kern(w)
    if isinstance(w, tuple):
        return [_wert_zum_kern(x) for x in w]
    return w


def _zum_kern(e: EffektDaten | None) -> dict:
    """Der Effekt im Format des Kerns (neue Kopie)."""
    return {k: _wert_zum_kern(v) for k, v in e.werte} if e is not None else {}


def schatten_vorgaben() -> tuple[EffektVorgabe, ...]:
    """Außen, Innen und Perspektive: Name, Schatten und Abschnitt."""
    return tuple(EffektVorgabe(name, _aus_kern(s), abschnitt) for abschnitt, name, s in vorgaben.schatten_vorgaben())


def reflektion_vorgaben() -> tuple[EffektVorgabe, ...]:
    """Name und Spiegelung."""
    return tuple(EffektVorgabe(name, _aus_kern(s)) for name, s in vorgaben.reflektion_vorgaben())


def leuchten_vorgaben() -> tuple[EffektVorgabe, ...]:
    """Name und Leuchteffekt."""
    return tuple(EffektVorgabe(name, _aus_kern(s)) for name, s in vorgaben.leuchten_vorgaben())


def wordart_vorgaben() -> tuple[EffektVorgabe, ...]:
    """Name und vollständiger Effekt — die Formatvorlagen des WordArt-Menüs."""
    return tuple(EffektVorgabe(name, _aus_kern(s)) for name, s in vorgaben.wordart_vorgaben())


def hat_effekt(fx: EffektDaten | None) -> bool:
    return daten.hat_effekt(_zum_kern(fx) if fx is not None else None)


def als_text(fx: EffektDaten | None) -> str:
    """Die Effekte, die der Kern zeichnet, als Text für das Zeichenformat (leer: keine)."""
    return daten.als_text(_zum_kern(fx) if fx is not None else None)


def aus_text(text: str | None) -> EffektDaten:
    """Die Effekte aus dem Text des Zeichenformats."""
    return _aus_kern(daten.aus_text(text))
