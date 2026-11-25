"""Formel einfuegen: aus ``core.bearbeitung.einfuegen`` herausgelöst."""
from __future__ import annotations
from PySide6.QtGui import QImage
from core.formatierung.farben.farben import Farbe


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
    from vcl.qt.rendering.formen.anzeige import kern_bild
    from core.geometrie import Point
    from core.layout.drucklayout.ausgabe.backend import Style, rgba
    from core.textsatz import FontSpec
    from framework.dokumentverwaltung.ausgabe.textsatz import standard_engine
    engine = standard_engine()
    basis, klein = FontSpec("DejaVu Serif", float(pt), 400, True), FontSpec("DejaVu Serif", pt * 2 / 3, 400, True)
    stuecke, x = [], 0.0
    for t, a in formel_teile(text):
        f = klein if a in ("hoch", "tief") else basis
        stuecke.append((t, a, f, x))
        x += engine.measure_text(t, f)
    m = engine.font_metrics(basis)
    grund = 2 + pt * 0.45 + m.ascent
    b, h = int(x) + 8, int(grund + m.descent + pt * 0.3) + 4

    def zeichnen(z) -> None:
        for t, a, f, x0 in stuecke:
            z.draw_text(t, Point(4 + x0, grund - pt * 0.4 if a == "hoch" else grund + pt * 0.2 if a == "tief" else grund), f, Style(color=rgba(farbe)))
    return kern_bild(b, h, zeichnen)


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
