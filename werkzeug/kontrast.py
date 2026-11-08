"""Kontrast der Oberflächenfarben nach WCAG 2.1 (Verhältnis der relativen Helligkeiten) — rechnerisch aus den Farbtafeln in ``ui/theme.py``.

    python werkzeug/kontrast.py [Ausgabe.md]      → Markdown-Tabelle aller Paare in allen Themen

Grenzen: Text normal ≥ 4,5 : 1, Text ab 18 pt oder 14 pt fett und Bedienelemente/Rahmen/Fokus ≥ 3 : 1.
Das prüft nur die Tafeln, nicht jede einzelne Stelle mit eigenem Stylesheet — dafür bleibt die Sichtprüfung nötig.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def hell(hexfarbe: str) -> float:
    r, g, b = (int(hexfarbe[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4          # noqa: E731
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def verhaeltnis(a: str, b: str) -> float:
    la, lb = sorted((hell(a), hell(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# (Vordergrund, Hintergrund, Mindestwert, Beschreibung)
PAARE = [
    ("text", "bg", 4.5, "Text auf Grund"), ("text", "flaeche", 4.5, "Text auf Fläche"), ("text", "karte", 4.5, "Text auf Karte"),
    ("text", "feld", 4.5, "Text im Eingabefeld"), ("text", "hover", 4.5, "Text beim Überfahren"), ("text", "weich", 4.5, "Text auf Auswahl"),
    ("text2", "bg", 4.5, "Nebentext auf Grund"), ("text2", "flaeche", 4.5, "Nebentext auf Fläche"), ("text2", "karte", 4.5, "Nebentext auf Karte"),
    ("akzent", "bg", 3.0, "Akzent (Markierung, Fokus) auf Grund"), ("akzent", "feld", 3.0, "Fokusrahmen im Eingabefeld"),
    ("akzent", "karte", 3.0, "Akzent auf Karte"),
    ("grau", "bg", 3.0, "Deaktiviertes/Platzhalter auf Grund (Hinweis, kein Pflichttext)"),     # reine Zierlinien (Rand) sind nach WCAG ausgenommen
]


def tafeln() -> dict[str, dict]:
    from lunivo_writer.ui import theme
    return {"hell": theme.FARBEN[False], "dunkel": theme.FARBEN[True], "hell weich": theme.WEICHE_FARBEN[False],
            "dunkel weich": theme.WEICHE_FARBEN[True], "mint": theme.MINT_FARBEN}


def pruefen() -> list[tuple[str, str, float, float, str, bool]]:
    r = []
    for thema, t in tafeln().items():
        for vor, hin, soll, was in PAARE:
            v = verhaeltnis(t[vor], t[hin])
            r.append((thema, was, round(v, 2), soll, f"{t[vor]} auf {t[hin]}", v >= soll))
    return r


def bericht() -> str:
    z = ["# Kontrast der Oberflächenfarben (WCAG 2.1, rechnerisch)", "", "| Thema | Paar | Verhältnis | Soll | Farben | Ergebnis |", "|---|---|---|---|---|---|"]
    for thema, was, v, soll, farben, ok in pruefen():
        z.append(f"| {thema} | {was} | {v:.2f} | {soll:.1f} | `{farben}` | {'ok' if ok else '**zu niedrig**'} |")
    return "\n".join(z) + "\n"


if __name__ == "__main__":
    t = bericht()
    if len(sys.argv) > 1:
        open(sys.argv[1], "w", encoding="utf-8").write(t)
    else:
        print(t)
