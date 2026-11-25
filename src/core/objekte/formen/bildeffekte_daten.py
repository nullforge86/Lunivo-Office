"""Bildeffekte daten: aus ``vcl.qt.rendering.formen.bildeffekte`` herausgelöst."""
from __future__ import annotations
import math
from core.formatierung.farben.farben import Farbe


PX_PT = 96.0 / 72.0


# Dieselben Schlüssel wie bei den Texteffekten (editor/text/textfx.py), damit Voreinstellungen und Regler gemeinsam genutzt werden
VORGABE = {"schatten": {"farbe": Farbe.SCHWARZ, "transparenz": 60, "groesse": 100, "weich": 4.0, "abstand": 4.0, "winkel": 45},
           "reflektion": {"groesse": 50, "transparenz": 50, "weich": 0.5, "abstand": 0.0},
           "leuchten": {"farbe": Farbe.BLAU, "groesse": 8.0, "transparenz": 60},
           "weich": {"radius": 6.0},
           "d3": {"tiefe": 6.0, "tiefe_farbe": Farbe.GRAU, "kontur": 0.0, "kontur_farbe": Farbe.TINTE, "material": "matt", "beleuchtung": "neutral", "winkel": 0,
                  "oben": {"art": "rund", "breite": 4.0, "hoehe": 6.0}, "unten": {"art": "rund", "breite": 4.0, "hoehe": 6.0}},
           "drehung": {"x": 0.0, "y": 0.0, "z": 0.0, "persp": 45.0, "text_gerade": False, "boden": 0.0}}


ABSCHLUSS = (("rund", "Rund"), ("winkel", "Winkel"), ("weich", "Weich"), ("kreuz", "Kreuz"), ("rahmen", "Rahmen"))      # die Abschlussarten des 3D-Formats


_MERK: dict = {}


def _merken(schluessel, bauen):
    if schluessel not in _MERK:
        if len(_MERK) > 48:
            _MERK.pop(next(iter(_MERK)))
        _MERK[schluessel] = bauen()
    return _MERK[schluessel]


def tiefe_richtung(dreh: dict | None) -> tuple[float, float]:
    """Einheitsvektor, in dem die Tiefe nach hinten läuft: schräg nach rechts unten, bei gedrehtem Objekt (3D-Drehung X/Y) entsprechend verschoben."""
    dx, dy = 0.7, 0.7
    if dreh:
        dx += math.sin(math.radians(float(dreh.get("y", 0.0)))) * 0.8
        dy -= math.sin(math.radians(float(dreh.get("x", 0.0)))) * 0.8
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


# ---- 3D-Drehung: das Bild im Raum gedreht (Perspektive) ------------------------------------------------------------------------
def _dreht(dreh: dict | None) -> bool:
    return bool(dreh) and any(abs(float(dreh.get(k, 0.0))) > 0.01 for k in ("x", "y", "z"))


def hat_drehung(fx: dict | None) -> bool:
    """True, wenn ``fx["drehung"]`` das Bild dreht (``drehung_3d``)."""
    return _dreht((fx or {}).get("drehung"))


def hat_nachbearbeitung(fx: dict | None) -> bool:
    """True, wenn das Bild vor dem Zeichnen mit ``bild_nachbearbeiten`` verändert werden muss (gedreht oder mit oberem Abschluss)."""
    return hat_drehung(fx) or hat_abschluss(fx)


def hat_abschluss(fx: dict | None) -> bool:
    return ((((fx or {}).get("d3") or {}).get("oben") or {}).get("art", "keine")) != "keine"
