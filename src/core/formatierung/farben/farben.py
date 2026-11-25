"""Die Grundfarben des Programms mit Namen — der eine Ort, an dem ein Farbwert steht.

Wer eine Farbe braucht, schreibt ``Farbe.AKZENT`` statt ``"#2f6fb5"``. Ändert sich ein Farbton, ändert er sich hier und überall zugleich.
Die Namen sagen, wofür die Farbe da ist, nicht, wie sie aussieht. Die Farbtafeln des Designs (hell/dunkel) stehen in ``oberflaeche/thema.py``.
"""
from __future__ import annotations


class Farbe:
    SCHWARZ = "#000000"
    WEISS = "#ffffff"
    PIKTOGRAMM = "#1f2328"          # Standardfarbe eines eingefügten Piktogramms
    HOLZ = "#d9b98a"                # Holzton der Bildvorlagen (Rahmen „Holz“)
    FORM_LINIE = "#1f3864"          # Standardlinie eingefügter Formen
    REGENBOGEN = ("#e03131", "#f08c00", "#ffd43b", "#2f9e44", "#1971c2", "#7048a8")   # Farbfolge der WordArt-Vorlage „Regenbogen“
    # Diagramme
    DIAGRAMM_LINIE = "#3c4043"          # Standardfarbe von Linien und Text im Diagramm
    DIAGRAMM_BLAU_DUNKEL = "#1864ab"    # dunkler Ton der Standardfüllung (Verlauf, Verlauf-Endfarbe)
    DIAGRAMM_ROT = "#c0392b"            # Anfangsfarbe der Verlaufsvorgabe
    LEUCHTEN_GELB = "#ffc000"           # Standardfarbe des Leuchtens
    DIAGRAMM_FARBIG = (("Farbig 1", ("#4a8fd8", "#ef8a3c", "#9aa0a6", "#f2b705", "#2f6fb5", "#5aa454")),
                       ("Farbig 2", ("#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6", "#e67e22")),
                       ("Farbig 3", ("#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51", "#8ab17d")),
                       ("Farbig 4", ("#6a4c93", "#1982c4", "#8ac926", "#ffca3a", "#ff595e", "#52a9a1")))   # Farbschemen der Diagrammstile
    DIAGRAMM_MONOCHROM = ("#4a8fd8", "#ef8a3c", "#868e96", "#f2b705", "#2f6fb5", "#5aa454", "#c0392b", "#7e57c2")   # Grundfarben der einfarbigen Schemen
    # Zeichnen, Objekte, WordArt
    DURCHSICHTIG_HEX = "#00000000"      # keine Farbe, als Farbtext
    GRAU_MITTEL = "#808080"             # mittleres Grau (Platzhalter, Tiefe von WordArt)
    GRAU_DUNKEL = "#404040"             # Kontur der WordArt-Tiefe
    SCHATTEN_GRAU = "#8a8a8a"           # Standardfarbe eines Schattens
    TEXT_STANDARD = "#1f1f1f"           # Standardfarbe eines Textfeldes
    WORDART_BLAU = "#2f78bd"            # Standardfarbe der WordArt
    WORDART_TINTE = "#111417"           # Gesicht des WordArt-Kachelbildes ohne eigene Farbe
    SYMBOL_HELL = "#e6e9ec"             # helles Unterstreichungssymbol
    BILDEFFEKT_GRUND = "#9aa3ad"        # Grundton des Rauschbildes
    VORGABE_GRUND = "#dbe4ff"           # „A“ im Kachelbild der Texteffekte
    VORGABE_RAND = "#8fa8e8"            # Rand des „A“ im Kachelbild
    VORGABE_VERLAUF = ("#f3f6ff", "#dfe7ff", "#c9d6fb")   # Verlauf der Formkachel (oben, Mitte, unten)
    VORGABE_FORMRAND = "#a9bcef"        # Rand der Formkachel
    TEXTUR = {"papier": "#f1ead8", "granit": "#9a9a9a", "holz": "#c8955a", "stoff": "#8aa4c8", "marmor": "#e6e6ea", "sand": "#e3cf9f"}   # Grundtöne der Texturen
    TINTE = "#343a40"               # dunkle Schrift und Striche auf hellem Grund
    FORMFARBEN = ("#4a8fd8", "#6bbf59", "#f4a259", "#e5645f", "#ffd43b", "#ced4da", "#495057", "#ffffff", "#000000")   # Farbfelder für Formen (Füllung, Linie)
    TINTE_DUNKEL = "#212529"
    GRAU = "#868e96"                # gedämpft: Rahmen, Hinweise, Platzhalter
    GRAU_HELL = "#adb5bd"
    AKZENT = "#2f6fb5"              # die Hauptfarbe (Knöpfe, Auswahl) auf hellem Grund
    AKZENT_DUNKEL = "#4a8fd8"       # dieselbe Hauptfarbe auf dunklem Grund
    BLAU = "#4c6ef5"                # Bilder, Füllungen im Objektformat
    ROT = "#c92a2a"
    ROT_HELL = "#ff6b6b"            # Rot auf dunklem Grund (Änderungsbalken)
    ORANGE = "#e8590c"
    GRUEN = "#2f9e44"
    ENTFERNT = ROT                  # Änderungsvorschau: entfernter Text (durchgestrichen); das Thema setzt sie je Thema um (dunkel: ROT_HELL)
    NEU = GRUEN                     # Änderungsvorschau: neuer Text (unterstrichen); das Thema setzt sie je Thema um (dunkel: GRUEN_HELL)
    GRUEN_HELL = "#69db7c"          # Grün auf dunklem Grund
    AN = "#2f9e75"                  # „an“-Marke und eingeschaltete Schalter der Seitenleisten (Thema „Mint“ setzt sie um)
    AN_SCHRIFT = "#ffffff"
    HINWEIS = "#a0a0a0"             # gedämpfte Hinweis-/Leertexte = Palette-Rolle Mid (hell: #a0a0a0); das Thema setzt sie je Thema — nur zur Laufzeit lesen
    AUF_AKZENT = "#ffffff"          # Schrift und Symbole auf eingeschalteten Flächen; das Thema setzt sie um (Mint: dunkel auf Hellgrün)
    KONTEXT = None                  # Farbe der Kontext-Reiter im Band (Zeichentools …); None = Akzentfarbe des Themas, Mint setzt sie
    KONTEXT_SCHRIFT = "#ffffff"     # Schrift des gewählten Kontext-Reiters
    KONTEXT_TEXT = "#9cc4f0"        # Schrift nicht gewählter Kontext-Reiter auf dunklem Grund; das Thema setzt sie um
    BLAU_DUNKEL = "#1864ab"         # Standardfarbe 2 von Verläufen
    BLAU_HELL = "#d0ebff"
    AUSWAHL = "#1c7ed6"             # Auswahlrahmen und Drehgriff freier Objekte
    GRIFF_RAND = "#8c8c8c"          # Rand der weißen Griffe
    PAPIER = "#ffffff"              # Seitenpapier und Weiß hinter Vorschauen (bleibt in allen Themen weiß)
    GITTER = "#e6e9ec"              # Hilfs- und Rahmenlinien, leichte Hover-Flächen auf hellem Grund
    LEISTE = "#f5f5f5"              # Werkzeugleisten auf dem Papier (Kopf-/Fußbearbeiter)
    LEISTE_RAND = "#c8c8c8"         # Rand dieser Leisten
    SYMBOL = "#1f2328"              # Standard-Symbolfarbe auf hellem Grund
    SYMBOL_HELL = "#f4f6f8"         # Symbolfarbe auf dunklem Grund
    SYMBOL_AUS_AKZENT = "#5d7a45"   # ausgegraute Symbole auf dem hellen Akzent; das Thema setzt sie um (Mint: gedämpftes Grün)
    AKZENT_HELL = "#748ffc"         # helle Akzentvariante
    WARNUNG = "#c77d2e"             # „sicher falsch“-Marke und gestrichelte Linie der Schreibhilfe (warmes Orange)
    WARNUNG_HELL = "#d9a03a"        # dieselbe Marke als Fläche mit dunkler Schrift
    AUSWAHL_HELL = "#e8f0fe"        # helle Auswahl-/Hover-Fläche in Menüs auf dem Papier
    # Farben der Dropdown-Vorschauen (Sinnbilder, Voreinstellungen): feste Farben, unabhängig vom Thema
    SINNBILD_HELL = "#d4d4d4"       # Diagramm-Sinnbilder: Grautöne
    SINNBILD_MITTEL = "#9a9a9a"
    SINNBILD_DUNKEL = "#6e6e6e"
    VORSCHAU_RAND = "#3c000000"     # feiner Rand um Farbfelder in Vorschauen (ARGB, 24 % Schwarz)
    GRADUELL = (("#e03131", "#ffc9c9"), ("#f08c00", "#ffe8cc"), ("#f2c200", "#fff3bf"), (GRUEN, "#d3f9d8"), ("#1971c2", "#d0ebff"), ("#7048e8", "#e5dbff"),
                (TINTE_DUNKEL, "#dee2e6"), (GRAU, "#f8f9fa"))     # (dunkel, hell) der graduellen Füllungen
