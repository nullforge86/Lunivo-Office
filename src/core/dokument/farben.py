"""Die Grundfarben des Programms mit Namen — der eine Ort, an dem ein Farbwert steht.

Wer eine Farbe braucht, schreibt ``Farbe.AKZENT`` statt ``"#2f6fb5"``. Ändert sich ein Farbton, ändert er sich hier und überall zugleich.
Die Namen sagen, wofür die Farbe da ist, nicht, wie sie aussieht. Die Farbtafeln des Designs (hell/dunkel) stehen in ``oberflaeche/thema.py``.
"""
from __future__ import annotations


class Farbe:
    SCHWARZ = "#000000"
    WEISS = "#ffffff"
    TINTE = "#343a40"               # dunkle Schrift und Striche auf hellem Grund
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
