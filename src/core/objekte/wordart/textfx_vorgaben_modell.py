"""Textfx vorgaben modell: aus ``vcl.qt.rendering.wordart.textfx_vorgaben`` herausgelöst."""
from __future__ import annotations
from core.formatierung.farben.farben import Farbe


# ---- Voreinstellungen der Auswahlen im Fenster „Texteffekte formatieren“ ---------------------------------------------------
_RICHTUNGEN = (("Unten rechts", 45), ("Unten", 90), ("Unten links", 135), ("Rechts", 0), ("Zentriert", 0), ("Links", 180),
               ("Oben rechts", 315), ("Oben", 270), ("Oben links", 225))


def schatten_vorgaben() -> list[tuple[str, str, dict]]:
    """[(Abschnitt, Name, Schatten)] — Außen, Innen (je 9) und Perspektive (5)."""
    aus = []
    for art, abschnitt in (("aussen", "Außen"), ("innen", "Innen")):
        for name, w in _RICHTUNGEN:
            zentral = name == "Zentriert"
            aus.append((abschnitt, name, {"art": art, "farbe": Farbe.SCHWARZ, "transparenz": 50 if art == "aussen" else 40, "groesse": 100,
                                          "weich": 6 if zentral else 3, "abstand": 0 if zentral else 4, "winkel": w}))
    for i, (name, w) in enumerate((("Perspektive diagonal unten rechts", 45), ("Perspektive diagonal unten links", 135), ("Perspektive unten", 90),
                                   ("Perspektive rechts", 0), ("Perspektive links", 180))):
        aus.append(("Perspektive", name, {"art": "persp", "farbe": Farbe.SCHWARZ, "transparenz": 55, "groesse": 100, "weich": 2, "abstand": 8, "winkel": w}))
    return aus


def reflektion_vorgaben() -> list[tuple[str, dict]]:
    """9 Spiegelungen: drei Größen (eng, halb, voll) mal drei Abstände."""
    aus = []
    for groesse, gname in ((35, "enge"), (50, "halbe"), (90, "volle")):
        for abstand in (0, 4, 8):
            aus.append((f"{gname.capitalize()} Spiegelung, Abstand {abstand} pt", {"groesse": groesse, "transparenz": 55 if groesse < 90 else 65, "weich": 0, "abstand": abstand}))
    return aus


def leuchten_vorgaben() -> list[tuple[str, dict]]:
    """24 Leuchtvarianten: sechs Farben mal vier Größen."""
    aus = []
    for groesse in (5, 8, 11, 18):
        for name, farbe in (("Blau", Farbe.BLAU), ("Rot", "#fa5252"), ("Grau", Farbe.GRAU), ("Gelb", "#fab005"), ("Hellblau", "#339af0"), ("Grün", "#40c057")):
            aus.append((f"{name}, {groesse} pt", {"farbe": farbe, "groesse": groesse, "transparenz": 60}))
    return aus


def wordart_vorgaben() -> list[tuple[str, dict]]:
    """Die 15 Formatvorlagen im Menü „Texteffekte ▸ WordArt“: Füllung, Kontur, Schatten (vollständige Effekte, ersetzen die bisherigen)."""
    def e(**k):
        return {"fuell": "farbe", "farbe": "#111417", "transparenz": 0, "kontur": False, "kontur_farbe": Farbe.SCHWARZ, "kontur_breite": 0.75, "kontur_art": "einfach", **k}
    sch = {"art": "aussen", "farbe": Farbe.SCHWARZ, "transparenz": 55, "groesse": 100, "weich": 2, "abstand": 3, "winkel": 45}
    return [("Schwarz", e()), ("Blau", e(farbe="#4a90d9")), ("Orange", e(farbe="#f08c2e")),
            ("Blaue Kontur", e(fuell="keine", kontur=True, kontur_farbe="#4a90d9", kontur_breite=1.25)), ("Gelb", e(farbe="#ffc61a")), ("Grau", e(farbe="#7f8790")),
            ("Blau mit Schatten", e(farbe=Farbe.AKZENT, schatten=sch)), ("Gelbe Kontur", e(fuell="keine", kontur=True, kontur_farbe="#ffc61a", kontur_breite=1.25)),
            ("Hellblaue Kontur", e(fuell="keine", kontur=True, kontur_farbe="#8fb8ea", kontur_breite=1.0)), ("Dunkelgrau", e(farbe="#495057")),
            ("Schwarz mit Schatten", e(schatten=sch)), ("Schwarz mit blauer Kontur", e(kontur=True, kontur_farbe="#4a90d9", kontur_breite=1.0)),
            ("Blauer Verlauf", e(fuell="verlauf", farbe="", verlauf={"farbe1": "#5b9be0", "farbe2": "#1c4fa3", "winkel": 90}, schatten=sch)),
            ("Orange Kontur", e(fuell="keine", kontur=True, kontur_farbe="#f08c2e", kontur_breite=1.25)), ("Graue Kontur", e(fuell="keine", kontur=True, kontur_farbe=Farbe.GRAU, kontur_breite=1.25))]
