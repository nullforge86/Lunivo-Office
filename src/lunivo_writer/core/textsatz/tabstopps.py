"""Tabstopps: Breite jedes Tabulators (links, rechts, zentriert, Dezimalstopp, Standardabstand, hängender Einzug). Ohne Qt."""
from __future__ import annotations

import math

TAB = "\t"
TAB_LINKS, TAB_RECHTS, TAB_MITTE, TAB_TRENNZEICHEN = 0, 1, 2, 3          # Art eines Tabstopps (Zählung wie ``core.document.values.TabStop``)


def naechster_stopp(x: float, tabs: tuple, abstand: float, haengend: float | None) -> tuple:
    """Der nächste Tabstopp rechts von ``x`` (vom linken Rand der Spalte): ein gesetzter Stopp, der linke Einzug bei hängendem Einzug, sonst das nächste Vielfache des Standardabstands."""
    kandidaten = [(t[0], t[1], t[2] if len(t) > 2 else "") for t in tabs if t[0] > x + 0.01]
    if haengend is not None and haengend > x + 0.01:
        kandidaten.append((haengend, TAB_LINKS, ""))
    if kandidaten:
        return min(kandidaten)
    return (math.floor((x + 0.01) / abstand) + 1) * abstand, TAB_LINKS, ""


def tab_vorschuebe(text: str, adv: list[float], plan: list, tabs: tuple, abstand: float, einzug_links: float, einzug_erste: float) -> tuple[dict[int, float], dict[int, float]]:
    """(Breite, Stopp) jedes Tabulators bei diesem Zeilenplan: bis zum nächsten Stopp; bei rechtsbündigem oder zentriertem Stopp rückt das folgende Stück an bzw. um den Stopp,
    beim Stopp mit Trennzeichen (Dezimalstopp) steht das Trennzeichen am Stopp."""
    neu: dict[int, float] = {}
    stopps: dict[int, float] = {}
    for nr, (b, dl, _raum, _luecke) in enumerate(plan):
        x = einzug_links + (einzug_erste if nr == 0 else 0.0) + dl
        ende, i = b.start + b.length, b.start
        while i < ende:
            if text[i] != TAB:
                x += adv[i]
                i += 1
                continue
            stopp, art, trenner = naechster_stopp(x, tabs, abstand, einzug_links if nr == 0 and einzug_erste < 0 else None)
            w = stopp - x
            if art in (TAB_RECHTS, TAB_MITTE, TAB_TRENNZEICHEN):
                j, stueck = i + 1, 0.0
                while j < ende and text[j] not in "\t\n\u2028" and not (art == TAB_TRENNZEICHEN and text[j] in (trenner or ",.")):
                    stueck += adv[j]
                    j += 1
                w = max(0.0, w - (stueck / 2 if art == TAB_MITTE else stueck))
            neu[i] = w
            stopps[i] = stopp
            x += w
            i += 1
    return neu, stopps
