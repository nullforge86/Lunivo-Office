"""Formel einfuegen: aus ``vcl.qt.rendering.formen.einfuegen`` herausgelöst."""
from __future__ import annotations
from PySide6.QtGui import QImage
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe


# ---- Formel -----------------------------------------------------------------------------------------------------------------
_GRIECH = {"alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε", "theta": "θ", "lambda": "λ", "mu": "μ",
           "pi": "π", "rho": "ρ", "sigma": "σ", "phi": "φ", "omega": "ω", "Delta": "Δ", "Sigma": "Σ", "Omega": "Ω",
           "infty": "∞", "sum": "∑", "int": "∫", "partial": "∂", "pm": "±", "leq": "≤", "geq": "≥", "neq": "≠", "approx": "≈",
           "times": "×", "cdot": "·", "to": "→", "in": "∈", "forall": "∀", "exists": "∃"}


def formel_teile(text: str) -> list[tuple[str, str]]:
    """Einfache Schreibweise → [(Text, "normal"|"hoch"|"tief")]:  a^2  x_{12}  sqrt(x)  frac(a,b)  \\alpha"""
    import re
    t = re.sub(r"\\([A-Za-z]+)", lambda m: _GRIECH.get(m.group(1), m.group(0)), text)
    t = re.sub(r"sqrt\(([^()]*)\)", r"√(\1)", t)
    t = re.sub(r"frac\(([^(),]*),([^()]*)\)", r"(\1)⁄(\2)", t)
    teile: list[tuple[str, str]] = []
    i = 0
    puffer = ""
    while i < len(t):
        ch = t[i]
        if ch in "^_" and i + 1 < len(t):
            if t[i + 1] == "{":
                j = t.find("}", i + 2)
                j = len(t) if j < 0 else j
                inhalt, naechst = t[i + 2:j], j + 1
            else:
                inhalt, naechst = t[i + 1], i + 2
            if puffer:
                teile.append((puffer, "normal")); puffer = ""
            teile.append((inhalt, "hoch" if ch == "^" else "tief"))
            i = naechst
        else:
            puffer += ch; i += 1
    if puffer:
        teile.append((puffer, "normal"))
    return teile


def formel_bild(text: str, pt: int = 16, farbe: str = Farbe.SCHWARZ) -> QImage:
    """Die Formel als Bild (Vorschau im Fenster „Formel“ und in der Gleichungsgalerie): kursive Stücke, Hoch- und Tiefgestelltes verkleinert und versetzt; gezeichnet vom Kern."""
    from writer.anbindung import zeichnen as ZW
    breite, hoehe, roh = ZW.formel(tuple(formel_teile(text)), pt, farbe)
    return QImage(roh, breite, hoehe, breite * 4, QImage.Format_RGBA8888).copy()


def formel_einfuegen(ed, text: str) -> None:
    """Fügt die Formel als Text mit hoch- und tiefgestellten Teilen an der Schreibmarke ein."""
    with ed.sitzung.gruppe("Formel"):
        for stueck, art in formel_teile(text):
            fmt = {"schrift": "DejaVu Serif", "kursiv": True}
            if art in ("hoch", "tief"):
                fmt["hoch_tief"] = art
            ed.sitzung.text_einfuegen(stueck, format=fmt)
        ed.sitzung.text_einfuegen(" ", format={})
    ed.ansicht.nach_aenderung()
