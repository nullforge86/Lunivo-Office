from __future__ import annotations
from PySide6.QtGui import QColor
from core.formatierung.schrift.silbenfarben_modell import DARSTELLUNGEN, PALETTEN, STANDARD


def konfig_lesen(settings) -> dict:
    """Die Einstellungen (settings: Settings des Programms) als Wörterbuch mit allen Schlüsseln."""
    k = dict(STANDARD)
    g = lambda n: "lesehilfe/silben/" + n                                          # noqa: E731
    k["an"] = settings.get_bool(g("an"), STANDARD["an"])
    pal = settings.get(g("palette"), STANDARD["palette"])
    k["palette"] = pal if pal in PALETTEN else STANDARD["palette"]
    eig = [c for c in str(settings.get(g("eigene"), ",".join(STANDARD["eigene"]))).split(",") if QColor(c).isValid()]
    k["eigene"] = (eig + STANDARD["eigene"])[:3]
    k["anzahl_eigene"] = min(3, max(2, int(settings.get(g("anzahl_eigene"), 2))))
    d = settings.get(g("darstellung"), STANDARD["darstellung"])
    k["darstellung"] = d if d in DARSTELLUNGEN else STANDARD["darstellung"]
    for n in ("fett", "einsilbig", "neu_pro_wort", "nur_absatz", "drucken"):
        k[n] = settings.get_bool(g(n), STANDARD[n])
    k["mindestens"] = min(10, max(2, int(settings.get(g("mindestens"), STANDARD["mindestens"]))))
    k["sprache"] = settings.get(g("sprache"), settings.get("silben/sprache", "de_DE"))
    return k
