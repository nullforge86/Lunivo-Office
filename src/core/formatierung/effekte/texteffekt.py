"""Texteffekte, die Lunivo zeichnet: Füllung des Textes (Farbe, Transparenz) und Kontur (Farbe, Breite, Linienart).

Ein Effekt ist ``{"fuell": "farbe"|"keine", "farbe": "#rrggbb"|"", "transparenz": 0…100, "kontur": bool, "kontur_farbe": "#rrggbb",
"kontur_breite": pt, "kontur_art": Schlüssel aus ``KONTUR_ARTEN``}``. Als Text (für eine Formatvorlage): ``transparenz|kontur_farbe|breite|art``
(leer = kein Effekt; die Füllfarbe steht bei der Vorlage in ihrem Feld „farbe“). Schatten, Spiegelung, Leuchten und 3D gibt es nicht,
weil Qt sie am Text nicht zeichnet.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen

from core.objekte.wordart import textfx

# Schlüssel → (Name, Qt-Strichart oder Strichmuster in Linienbreiten, DOCX-Wert ``a:prstDash``)
from core.formatierung.farben.farben import Farbe
KONTUR_ARTEN = {"einfach": ("Durchgezogen", Qt.SolidLine, "solid"), "gepunktet": ("Gepunktet", Qt.DotLine, "sysDot"),
                "fein": ("Fein gestrichelt", [3.0, 1.0], "sysDash"), "gestrichelt": ("Gestrichelt", Qt.DashLine, "dash"),
                "lang": ("Lang gestrichelt", [8.0, 3.0], "lgDash"), "strichpunkt": ("Strich-Punkt", Qt.DashDotLine, "dashDot"),
                "lang_strichpunkt": ("Lang Strich-Punkt", [8.0, 3.0, 1.0, 3.0], "lgDashDot"),
                "strichpunktpunkt": ("Strich-Punkt-Punkt", Qt.DashDotDotLine, "lgDashDotDot")}
# Formen der Konturlinie (zusammen mit der Breite die Spalten der Linienauswahl): einfach, doppelt, dick–dünn
KONTUR_FORMEN = (("einfach", "Einfach"), ("doppelt", "Doppelt"), ("dick_duenn", "Dick–dünn"), ("duenn_dick", "Dünn–dick"), ("dreifach", "Dreifach"))
# Zusätzliche Strichtypen des Diagramms (nicht in der Voreinstellungsliste ``KONTUR_ARTEN``): Schlüssel → (Strichmuster in Linienbreiten, runde Enden)
KONTUR_ARTEN_PLUS = {"rundpunkt": ([0.01, 2.0], True), "quadratpunkt": ([1.0, 1.0], False), "lang_strichpunktpunkt": ([8.0, 3.0, 1.0, 3.0, 1.0, 3.0], False)}


def strich_setzen(pen: QPen, art: str) -> None:
    """Strichart (Muster oder Qt-Stil) in einen Stift schreiben."""
    st = KONTUR_ARTEN.get(art, KONTUR_ARTEN["einfach"])[1]
    if isinstance(st, list):
        pen.setDashPattern(st)
    else:
        pen.setStyle(st)


EFFEKT = {"fuell": "farbe", "farbe": "", "transparenz": 0, "kontur": False, "kontur_farbe": Farbe.SCHWARZ, "kontur_breite": 0.75, "kontur_art": "einfach"}


def aus_zeichen(z: dict) -> dict:
    """Der Effekt eines Zeichenformats des Dokumentenmodells (Schlüssel ``effekt``: Wörterbuch oder JSON-Text) mit den Vorgaben von ``EFFEKT``."""
    w = dict(EFFEKT)
    e = z.get("effekt")
    if isinstance(e, str):
        e = textfx.aus_text(e)
    if isinstance(e, dict):
        w.update(e)
    return w


def zu_zeichen(w: dict) -> dict:
    """Die Änderung des Zeichenformats, die den Effekt setzt (nur was von der Vorgabe abweicht; kein Effekt: ``effekt`` wird entfernt)."""
    w = {**EFFEKT, **w}
    abweichend = {k: v for k, v in w.items() if k not in EFFEKT or EFFEKT[k] != v}
    return {"effekt": abweichend or None}


def _fuellart_ableiten(w: dict) -> None:
    """Füllart und Kontur aus den gelesenen Effekten ableiten: ein Verlauf, ein Muster oder Bild als Füllung; eine Kontur mit Verlauf oder Form."""
    if "verlauf" in w:
        w["fuell"] = "verlauf"
    if w.get("fuell_pinsel"):
        w["fuell"] = "muster" if w["fuell_pinsel"].get("art") == "muster" else "bild"
    if "kontur_verlauf" in w or w.get("kontur_form"):
        w["kontur"] = True


def _kontur_aus_stift(p, w: dict) -> None:
    """Farbe, Breite (pt) und Strichart der Textkontur aus dem Stift des Zeichenformats."""
    if p.style() == Qt.NoPen:
        return
    w["kontur"] = True; w["kontur_farbe"] = p.color().name(); w["kontur_breite"] = round(p.widthF() * 0.75, 2)
    if p.style() == Qt.CustomDashLine:
        w["kontur_art"] = next((k for k, v in KONTUR_ARTEN.items() if isinstance(v[1], list) and v[1] == list(p.dashPattern())), "einfach")
    else:
        w["kontur_art"] = next((k for k, v in KONTUR_ARTEN.items() if not isinstance(v[1], list) and v[1] == p.style()), "einfach")


def als_text(w: dict | None) -> str:
    """Nur Transparenz und Kontur; ``""`` wenn weder noch."""
    if not w or not (w.get("kontur") or w.get("transparenz") or textfx.hat_effekt(w)):
        return ""
    basis = f"{int(w.get('transparenz', 0))}|{w['kontur_farbe'] if w.get('kontur') else ''}|{w.get('kontur_breite', 0.75):g}|{w.get('kontur_art', 'einfach')}"
    extra = textfx.als_text(w)
    return basis + "|" + extra if extra else basis


def aus_text(text: str | None, farbe: str = "") -> dict | None:
    t = (text or "").split("|", 4)
    if len(t) not in (4, 5):
        return None
    try:
        w = {**EFFEKT, "farbe": farbe, "transparenz": int(t[0]), "kontur": bool(t[1]), "kontur_farbe": t[1] or Farbe.SCHWARZ,
             "kontur_breite": float(t[2]), "kontur_art": t[3] if t[3] in KONTUR_ARTEN else "einfach"}
        if len(t) == 5:
            w.update(textfx.aus_text(t[4]))
            _fuellart_ableiten(w)
        return w
    except ValueError:
        return None


# DOCX-Erweiterung w14: Qt-frei in ``dienste/docx_effekte``; hier weiter erreichbar
from filter.docx.docx_effekte import aus_rpr, in_rpr  # noqa: E402,F401
