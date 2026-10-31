"""Designs des Reiters Seitenlayout: Farbschemen, Schriftpaare, Effekte und die Designs, die alles drei bündeln. Keine Oberfläche.

    FARBSCHEMEN["Ostsee"]          # 8 Farben: Text dunkel, Hintergrund hell, Akzent 1 … 6
    SCHRIFTPAARE["Klar"]           # (Überschriften, Fließtext)
    EFFEKTE["Weicher Schatten"]    # fx für Formen und freie Bilder (Schlüssel wie editor/bildeffekte.py)
    DESIGNS["Ostsee"]              # (Farbschema, Schriftpaar)

Alle Namen und Farben sind Lunivos eigene. Die Schriften sind solche, die unter Linux Mint üblich sind; fehlt eine, ersetzt Qt sie.
"""
from __future__ import annotations

# Name → [Text dunkel, Hintergrund hell, Akzent 1 … 6]
FARBSCHEMEN: dict[str, list[str]] = {
    "Lunivo": ["#212529", "#f1f3f5", "#1971c2", "#e8590c", "#868e96", "#f08c00", "#1098ad", "#2f9e44"],
    "Ostsee": ["#1b2a3a", "#e7f0f7", "#1d5f8a", "#3c9bd6", "#79b8e0", "#2a9d8f", "#e9c46a", "#f4a261"],
    "Heide": ["#3a2e39", "#f4eef3", "#7b4f8e", "#b07cc6", "#d6a2c8", "#8f6e4f", "#c9a66b", "#6f8f72"],
    "Wald": ["#1f2a1f", "#eef3ec", "#2d6a4f", "#40916c", "#74c69d", "#95794b", "#d4a373", "#6c757d"],
    "Sandstein": ["#3b3024", "#f6f0e6", "#a0703c", "#c9935a", "#e3c08d", "#6b705c", "#a5a58d", "#cb997e"],
    "Ziegel": ["#2f1f1a", "#f7ece8", "#a23e2a", "#d1603d", "#e9a178", "#5c6b73", "#9db4c0", "#c2a878"],
    "Schiefer": ["#1e2329", "#e9ecef", "#495057", "#6c757d", "#adb5bd", "#3d5a80", "#98c1d9", "#ee6c4d"],
    "Morgenrot": ["#2b1d2a", "#fbf0ee", "#d1495b", "#edae49", "#f79256", "#00798c", "#30638e", "#003d5b"],
    "Lagune": ["#10292e", "#e6f4f1", "#00838f", "#26a69a", "#80cbc4", "#0277bd", "#ffb300", "#8d6e63"],
    "Kupfer": ["#2a211b", "#f5ede6", "#b5651d", "#d08c60", "#e8b996", "#5f6f52", "#a9b388", "#7f5539"],
    "Gletscher": ["#14213d", "#eef4fa", "#4a6fa5", "#7aa5d2", "#b8d4ea", "#6c8ead", "#9fb1bc", "#d8a48f"],
    "Mohn": ["#26181a", "#fdf0ef", "#c1121f", "#e85d75", "#f4a6b3", "#3a5a40", "#a3b18a", "#dda15e"],
    "Olive": ["#262b1c", "#f2f3ea", "#606c38", "#8a9a5b", "#c5d1a1", "#bc6c25", "#dda15e", "#283618"],
    "Nacht": ["#0b132b", "#e8eaf2", "#1c2541", "#3a506b", "#5bc0be", "#6fffe9", "#f2a541", "#e85d04"],
    "Pastell": ["#3d3d4e", "#fafafa", "#8ecae6", "#ffb5a7", "#bde0fe", "#cdb4db", "#b5e48c", "#ffd6a5"],
    "Signal": ["#111111", "#ffffff", "#e63946", "#f1c40f", "#2a9d8f", "#264653", "#e76f51", "#457b9d"],
    "Herbst": ["#2e1f14", "#f8efe4", "#9c4a1a", "#d97b29", "#e9b44c", "#7a8450", "#4f6d7a", "#8c5e58"],
    "Flieder": ["#2a2438", "#f3f0f9", "#6d597a", "#9d79bc", "#c3a6d8", "#b56576", "#e56b6f", "#eaac8b"],
    "Meer": ["#0d1b2a", "#e0ecf5", "#1b4965", "#5fa8d3", "#62b6cb", "#bee9e8", "#cae9ff", "#ef8354"],
    "Graustufen": ["#000000", "#ffffff", "#343a40", "#495057", "#6c757d", "#868e96", "#adb5bd", "#ced4da"],
}

# Name → (Schrift der Überschriften, Schrift des Fließtextes)
SCHRIFTPAARE: dict[str, tuple[str, str]] = {
    "Lunivo": ("Liberation Sans", "Liberation Sans"),
    "Klassisch": ("Liberation Serif", "Liberation Serif"),
    "Brief": ("Liberation Serif", "Liberation Sans"),
    "Bericht": ("Liberation Sans", "Liberation Serif"),
    "Klar": ("DejaVu Sans", "DejaVu Sans"),
    "Buch": ("DejaVu Serif", "DejaVu Serif"),
    "Noto": ("Noto Sans", "Noto Serif"),
    "Noto Serif": ("Noto Serif", "Noto Sans"),
    "Mint": ("Ubuntu", "Noto Sans"),
    "Büro": ("Carlito", "Carlito"),
    "Büro Serif": ("Caladea", "Carlito"),
    "Frei": ("FreeSans", "FreeSerif"),
    "Schreibmaschine": ("Liberation Mono", "Liberation Mono"),
}

# Name → fx (siehe editor/bildeffekte.py: schatten, reflektion, leuchten, weich); {} = ohne Effekt
EFFEKTE: dict[str, dict] = {
    "Schlicht": {},
    "Weicher Schatten": {"schatten": {"farbe": "#000000", "transparenz": 70, "groesse": 100, "weich": 6.0, "abstand": 3.0, "winkel": 45}},
    "Harter Schatten": {"schatten": {"farbe": "#000000", "transparenz": 45, "groesse": 100, "weich": 0.5, "abstand": 4.0, "winkel": 45}},
    "Schatten unten": {"schatten": {"farbe": "#000000", "transparenz": 65, "groesse": 100, "weich": 5.0, "abstand": 5.0, "winkel": 90}},
    "Leuchten": {"leuchten": {"farbe": "#4dabf7", "groesse": 6.0, "transparenz": 55}},
    "Leuchten warm": {"leuchten": {"farbe": "#ffa94d", "groesse": 6.0, "transparenz": 55}},
    "Spiegelung": {"reflektion": {"groesse": 40, "transparenz": 55, "weich": 0.5, "abstand": 1.0}},
    "Weiche Kanten": {"weich": {"radius": 4.0}},
    "Schatten, Spiegel": {"schatten": {"farbe": "#000000", "transparenz": 70, "groesse": 100, "weich": 5.0, "abstand": 3.0, "winkel": 45},
                          "reflektion": {"groesse": 35, "transparenz": 60, "weich": 0.5, "abstand": 1.0}},
    "Leuchten, Schatten": {"leuchten": {"farbe": "#74c0fc", "groesse": 4.0, "transparenz": 60},
                           "schatten": {"farbe": "#000000", "transparenz": 70, "groesse": 100, "weich": 5.0, "abstand": 3.0, "winkel": 45}},
}

# Name → (Farbschema, Schriftpaar). Effekte wählt man eigens (Seitenlayout ▸ Effekte), damit ein Design keine Schatten an Formen überschreibt.
DESIGNS: dict[str, tuple[str, str]] = {
    "Lunivo": ("Lunivo", "Lunivo"),
    "Ostsee": ("Ostsee", "Klar"),
    "Heide": ("Heide", "Brief"),
    "Wald": ("Wald", "Noto"),
    "Sandstein": ("Sandstein", "Buch"),
    "Ziegel": ("Ziegel", "Bericht"),
    "Schiefer": ("Schiefer", "Mint"),
    "Morgenrot": ("Morgenrot", "Klar"),
    "Lagune": ("Lagune", "Noto Serif"),
    "Kupfer": ("Kupfer", "Klassisch"),
    "Gletscher": ("Gletscher", "Büro"),
    "Mohn": ("Mohn", "Büro Serif"),
    "Olive": ("Olive", "Frei"),
    "Nacht": ("Nacht", "Mint"),
    "Pastell": ("Pastell", "Klar"),
    "Signal": ("Signal", "Lunivo"),
    "Herbst": ("Herbst", "Buch"),
    "Flieder": ("Flieder", "Brief"),
    "Meer": ("Meer", "Noto"),
    "Graustufen": ("Graustufen", "Schreibmaschine"),
}


def ueberschrift_farbe(schema: str) -> str:
    """Die Farbe der Überschriften eines Farbschemas: Akzent 1."""
    return FARBSCHEMEN[schema][2]


def design(name: str) -> dict:
    """Was ein Design setzt: {"kopf", "text", "farbe", "farben"} (Schriften, Überschriftfarbe, das ganze Farbschema)."""
    schema, paar = DESIGNS[name]
    kopf, text = SCHRIFTPAARE[paar]
    return {"kopf": kopf, "text": text, "farbe": ueberschrift_farbe(schema), "farben": list(FARBSCHEMEN[schema])}
