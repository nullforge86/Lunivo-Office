"""Skala: aus ``core.layout.drucklayout.ausgabe.diagramm.diagrammzeichner`` herausgelöst."""
from __future__ import annotations
import math


# ---- Wertachse ----------------------------------------------------------------------------------------------------------------
def _schritt(spanne: float) -> float:
    roh = spanne / 10.0 if spanne > 0 else 1.0
    exp = math.floor(math.log10(roh))
    for faktor in (1, 2, 5, 10):
        if faktor * 10 ** exp >= roh:
            return faktor * 10 ** exp
    return 10 ** (exp + 1)


def _skala(w: dict, werte: list, prozent: bool) -> tuple[float, float, float]:
    """(Minimum, Maximum, Intervall) der Wertachse: Angaben der Datei, sonst wie Word."""
    if prozent:
        return 0.0, 1.0, w.get("intervall") or 0.1
    lo = w.get("min") if w.get("min") is not None else min(0.0, min(werte, default=0.0))
    spitze = max(werte, default=1.0)
    spanne = spitze * 1.05 - lo
    schritt = w.get("intervall") or _schritt(spanne if spanne > 1e-9 else 1.0)           # nur Nullwerte: Spanne 1, nicht unendlich viele Teilstriche
    hi = w.get("max") if w.get("max") is not None else (math.ceil((spitze * 1.05 if spitze > 0 else 1.0) / schritt - 1e-9) * schritt)
    if hi <= lo:
        hi = lo + schritt
    return lo, hi, schritt


def _zahl(wert: float, stellen: int = 0) -> str:
    if stellen:
        return f"{wert:.{stellen}f}".replace(".", ",")
    return str(int(round(wert))) if abs(wert - round(wert)) < 1e-9 else f"{wert:g}".replace(".", ",")


def _printf(muster: str, wert: float) -> str:
    try:
        return (muster % wert).replace(".", ",")
    except (TypeError, ValueError):
        return _zahl(wert)
