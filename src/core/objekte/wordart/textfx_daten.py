"""Textfx daten: aus ``vcl.qt.rendering.wordart.textfx`` herausgelöst."""
from __future__ import annotations
import json
import math


PX = 96 / 72                                    # Punkt → Bildpunkt


MATERIAL = (("matt", "Matt"), ("plastik", "Plastik"), ("metall", "Metall"), ("dunkel", "Dunkle Kanten"), ("weich", "Weicher Rand"), ("hell", "Hell"))


BELEUCHTUNG = (("neutral", "Neutral"), ("weich", "Weich"), ("hart", "Hart"), ("warm", "Warm"), ("kalt", "Kalt"), ("kontrast", "Kontrast"))


SCHLUESSEL = ("verlauf", "kontur_verlauf", "kontur_form", "schatten", "reflektion", "leuchten", "d3", "fuell_pinsel", "text_3d", "warp")


def hat_effekt(fx: dict | None) -> bool:
    return bool(fx) and any(k in fx for k in SCHLUESSEL)


def als_text(fx: dict | None) -> str:
    """Nur die Teile, die Lunivo selbst zeichnet, als JSON für das Zeichenformat (leer = keiner)."""
    if not hat_effekt(fx):
        return ""
    erlaubt = list(SCHLUESSEL)
    if "kontur_verlauf" in fx or fx.get("kontur_form"):                  # die Kontur zeichnet dann Lunivo: Farbe, Breite und Strichart gehören dazu
        erlaubt += ["kontur_art", "kontur_breite", "kontur_farbe"]
    return json.dumps({k: v for k, v in fx.items() if k in erlaubt}, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def aus_text(text: str | None) -> dict:
    try:
        d = json.loads(text) if text else {}
        return d if isinstance(d, dict) else {}
    except ValueError:
        return {}


WARP_FORMEN = (("keine", "Keine Transformation"), ("bogen", "Bogen nach oben"), ("bogen_unten", "Bogen nach unten"), ("welle", "Welle"),
               ("trichter", "Trichter"), ("kaskade_auf", "Kaskade aufwärts"), ("kaskade_ab", "Kaskade abwärts"))


# Bahnen der Mehrfachlinien: (Abstand von der Mitte, Dicke) in Linienbreiten (negativ = links der Laufrichtung)
_BAHNEN = {"dick_duenn": ((-0.9, 1.2), (0.9, 0.6)), "duenn_dick": ((-0.9, 0.6), (0.9, 1.2)), "dreifach": ((-1.4, 0.6), (0.0, 0.6), (1.4, 0.6))}


def _tiefe_faktor(mat: str, licht: str, t: float) -> float:
    """Helligkeitsfaktor einer Tiefenschicht ``t`` (0..1) nach Material und Beleuchtung."""
    f = {"plastik": 1.25 - 0.5 * t, "metall": 1.0 + 0.45 * math.sin(t * math.pi * 2), "dunkel": 0.6 + 0.4 * (1 - t), "weich": 1.15 - 0.25 * t,
         "hell": 1.3}.get(mat, 1.0)
    return f * {"neutral": 1.0, "weich": 1.08, "hart": 0.8 + 0.5 * (1 - t), "warm": 1.0, "kalt": 1.0, "kontrast": 0.7 + 0.7 * t}.get(licht, 1.0)
