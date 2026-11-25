"""Bildeffekte (Schatten, Spiegelung, Leuchten, weiche Kanten, 3D-Format, 3D-Drehung): Vorgabewerte und Auswahllisten. Die Fachdaten liegen im Kern; die
Oberfläche erhält unveränderliche Beschreibungen."""
from __future__ import annotations

from core.objekte.formen import bildeffekte_daten as modell
from framework.schnittstellen.datentypen.effektdaten import EffektDaten, EffektWert

ABSCHLUSS: tuple[tuple[str, str], ...] = tuple((art, name) for art, name in modell.ABSCHLUSS)       # die Abschlussarten des 3D-Formats


def _wert_aus_kern(w: object) -> EffektWert:
    if isinstance(w, dict):
        return _aus_kern(w)
    if isinstance(w, (list, tuple)):
        return tuple(_wert_aus_kern(x) for x in w)
    return w                                               # type: ignore[return-value]  (Zahl, Text, Wahrheitswert, None)


def _aus_kern(fx: dict) -> EffektDaten:
    """Entkoppelte, unveränderliche Kopie der Effektdaten des Kerns."""
    return EffektDaten(tuple((str(k), _wert_aus_kern(v)) for k, v in fx.items()))


def vorgabe() -> EffektDaten:
    """Die Vorgabewerte je Effekt (``schatten``, ``reflektion``, ``leuchten``, ``weich``, ``d3``, ``drehung``)."""
    return _aus_kern(modell.VORGABE)
