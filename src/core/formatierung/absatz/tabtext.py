"""Tabstopps als Text, wie Formatvorlagen des Katalogs sie speichern: ``30.0:rechts:punkt;80.0:mitte:`` (Millimeter, Ausrichtung, Füllzeichen;
leer = keine)."""
from __future__ import annotations

from core.formatierung.absatz.tabfuell import FUELL

TAB_ARTEN: tuple[str, ...] = ("links", "mitte", "rechts", "dezimal")


def tabs_als_text(stopps) -> str:
    return ";".join(f"{m:g}:{a}:{f}" for m, a, f in stopps)


def tabs_aus_text(text: str | None) -> list[tuple[float, str, str]]:
    aus = []
    for teil in (text or "").split(";"):
        try:
            m, a, *f = teil.split(":")
            if a in TAB_ARTEN:
                aus.append((float(m), a, f[0] if f and f[0] in FUELL else ""))
        except ValueError:
            continue
    return aus
