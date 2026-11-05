"""Karte/Zeile: die eine Quelle für abgesetzte Flächen in den Seitenleisten (Kommentar, Fund, Funktionszeile, KI-Blase).

Ein Widget wird nur mit ``als_karte(widget, art)`` gekennzeichnet (Eigenschaft ``karte``); die Regeln dazu stehen genau einmal hier und werden vom Thema
(``ui/theme.py``) in das Programm-Stylesheet aufgenommen. Kein Widget setzt dafür ein eigenes Stylesheet."""
from __future__ import annotations

from lunivo_writer.ui.baukasten.mass import RADIUS_KARTE, RADIUS_MITTEL

ARTEN = ("zeile", "karte", "kompakt", "ki", "markiert")


def als_karte(widget, art: str = "karte"):
    """Kennzeichnet das Widget als Karte der Art ``art``: zeile (anklickbar, durchsichtig), karte (Fund), kompakt (Kommentar), ki/markiert (Blase mit Streifen links)."""
    widget.setProperty("karte", art)
    return widget


def karte_regeln(fokus: str, ki: str, grau: str) -> str:
    """QSS-Text aller Kartenarten; Farben ``fokus`` (Fokusrahmen, KI-Streifen), ``ki`` (Streifen KI-Blase), ``grau`` (Streifen sonst) kommen vom Thema."""
    flaeche = "border: 1px solid palette(midlight); "
    return (
        'QFrame[karte="zeile"] { ' + flaeche + 'border-radius: ' + str(RADIUS_MITTEL) + 'px; background: transparent; }'
        'QFrame[karte="zeile"]:hover { background: palette(alternate-base); border-color: palette(mid); }'
        'QFrame[karte="zeile"]:focus { border: 2px solid ' + fokus + '; }'
        'QFrame[karte="karte"] { ' + flaeche + 'border-radius: ' + str(RADIUS_KARTE) + 'px; background: rgba(128, 128, 128, 0.07); }'
        'QFrame[karte="kompakt"] { ' + flaeche + 'border-radius: ' + str(RADIUS_MITTEL) + 'px; background: rgba(128, 128, 128, 0.06); }'
        'QFrame[karte="karte"] QLabel, QFrame[karte="kompakt"] QLabel { border: none; background: transparent; }'
        'QFrame[karte="ki"], QFrame[karte="ki"] QFrame { border-left: 4px solid ' + ki + '; }'
        'QFrame[karte="markiert"], QFrame[karte="markiert"] QFrame { border-left: 4px solid ' + grau + '; }'
    )
