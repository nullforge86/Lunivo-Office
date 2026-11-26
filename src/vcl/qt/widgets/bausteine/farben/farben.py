"""Farbdaten für jede Palette im Programm: Themenfarben mit Abstufungen, Standardfarben, zuletzt benutzte."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from writer.hauptfenster import einstellungen as _einstellungen
from PySide6.QtGui import QColor

# Eigene Grundfarben (Weiß, Schwarz, zwei Grautöne, dann die Farben der Oberfläche) — jede Spalte bekommt fünf Abstufungen.
THEMA_FARBEN = ("#ffffff", "#000000", "#e9ecef", "#343a40", "#1971c2", "#e8590c", "#868e96", "#f08c00", "#1098ad", "#2f9e44")
STANDARD_FARBEN = ("#c92a2a", "#f03e3e", "#f08c00", "#ffd43b", "#82c91e", "#2f9e44", "#1098ad", "#1971c2", "#364fc7", "#6741d9")
# Voreinstellungsfarben für Benutzerobjekte und Dokumentdaten (werden bewusst nicht thematisiert).
VORGABE_WASSERZEICHEN = "#c0c0c0"      # Standardfarbe der Wasserzeichen
VORGABE_WORDART = "#2f78bd"            # Standardfarbe eines WordArt-Objekts im Dialog
VORGABE_MARKER = "#ffec99"             # Standardfarbe des Textmarkers
VORGABE_SCHATTIERUNG = "#d9d9d9"       # Zeichenschattierung
VORGABE_LINIE = "#1f3864"             # Standard-Linienfarbe einer neuen Form im Dialog
VORGABE_SCHRIFT = "#1f2328"            # Standard-Schriftfarbe eines neuen Textobjekts im Dialog
VORGABE_TABELLENRAND = "#333333"       # Rand einer per Befehl umrandeten Tabelle
# Heller Kachelgrund für Vorschauen mit dunkler Schrift (in allen Themen gleich hell, damit auch das schwarze „A“ zu sehen ist).
KACHEL_GRUND = "#f3f4f6"
KACHEL_RAND = "#d0d4d9"

# Fachliche Farben der Dokumentansicht und der Symbole – eine Stelle, sprechende Namen (Werte exakt wie bisher in den Funktionsdateien).
WELLEN_FEHLER, WELLEN_TIPP, WELLEN_HINWEIS = "#e03131", "#1971c2", "#f08c00"                       # Wellenlinien der Korrektur je Art
WELLEN_STANDARD = WELLEN_FEHLER
WELLEN_FARBE = {"fehler": WELLEN_FEHLER, "tipp": WELLEN_TIPP, "hinweis": WELLEN_HINWEIS}           # Wellenlinie je Art des Fundes
AUTOR_FARBEN = ("#c92a2a", "#1971c2", "#2f9e44", "#e8590c", "#7048a8", "#0b7285", "#a61e4d", "#5c940d")   # Farben der Autoren (Änderungen, Kommentare)
SYMBOL_AKZENT_SCHRIFTFARBE, SYMBOL_AKZENT_MARKER, SYMBOL_AKZENT_TOENUNG = "#e03131", "#fcc419", "#74c0fc"   # Farbstreifen unter den Symbolen
SYMBOL_AKZENT = {"schriftfarbe": SYMBOL_AKZENT_SCHRIFTFARBE, "marker": SYMBOL_AKZENT_MARKER, "absatztoenung": SYMBOL_AKZENT_TOENUNG,
                 "toenung": SYMBOL_AKZENT_TOENUNG}                                                 # Farbstrich unter dem Symbol je Name
SYMBOL_STRICH_DUNKEL, SYMBOL_STRICH_HELL = "#243062", "#F3F6FF"                                    # Strichsymbole ohne Hybrid-Entsprechung (heller/dunkler Grund)
KNOPF_SYMBOLFARBE = "#283c5a"                                                                      # Symbole auf dem hellen Knopfgrund (in jedem Thema gleich)
GITTER_FARBE = "#c8c8c8"                                                                           # Tabellengitter in der Ansicht
FUSSNOTE_VIOLETT = "#7048a8"                                                                       # Kennfarbe der Endnoten-Karten
HERVORHEBUNG_GELB = "#ffec99"                                                                      # Textmarker beim Hervorheben der Suche
SINNBILD_GELB, SINNBILD_GELB_HELL, SINNBILD_KONTUR = "#f2c200", "#ffe45c", "#1c3faa"              # Sinnbilder der freien Bilder
BILDCHEN_BLATT_DUNKEL, BILDCHEN_AKZENT_DUNKEL = "#3a3f45", "#6b5442"                              # Bildchen im dunklen Thema
BILDCHEN_LINIE, BILDCHEN_RAND, BILDCHEN_STRICH_HELL, BILDCHEN_FLAECHE_HELL = "#5c636a", "#495057", "#ced4da", "#f1f3f5"   # Papier-Sinnbilder
DESIGN_BILDCHEN_RAND = "#adb5bd"
AUSWAHL_OBJEKTTEXT = "#8a9ab0"                                                                    # Auswahlgrund beim Schreiben im Objekt
ABSATZ_VORSCHAU_GRAU = "#808080"                                                                   # vorhergehender/folgender Absatz in der Absatzvorschau
WASSERZEICHEN_VORSCHAU = "#b4b9be"                                                                 # Vorschaufarbe des Wasserzeichens
PAPIERTOENE = {"Weiß": Farbe.WEISS, "Creme": "#fbf4e2", "Gelblich": "#fff7cc", "Hellblau": "#e6f0fa", "Hellgrün": "#e8f5e9", "Hellgrau": "#eceff1"}   # Lesehilfe
AUGENSCHUTZ_PAPIER = "#cce8cf"                                                                     # Blattfarbe im Augenschutzmodus (Statusleiste)
NACHVERFOLGT_BLAU, NACHVERFOLGT_SCHWARZ, NACHVERFOLGT_VIOLETT ="#1971c2", "#222222", "#7048a8"    # feste Farben nachverfolgter Änderungen
FESTE_FARBEN = {"Rot": Farbe.ROT, "Blau": NACHVERFOLGT_BLAU, "Grün": Farbe.GRUEN, "Schwarz": NACHVERFOLGT_SCHWARZ, "Violett": NACHVERFOLGT_VIOLETT}   # Autorenfarbe wählbar
WORDART_FUELLUNG, TEXTOBJEKT_FUELLUNG = "#2f78bd", "#1f1f1f"                                       # Vorgaben im Textobjekt
TABELLENRAND_STANDARD, TABELLENRAND_SCHWARZ = "#333333", "#000000"                                 # Rand einer neuen Tabelle
LINIE_VORLAGE_GRAU, FUELLUNG_VORLAGE_BLAU = "#868e96", "#1971c2"                                  # Beispiele der Voreinstellungsmenüs
# Zeichenfarben als (R, G, B, A) – gebraucht mit ``QColor(*NAME)``; Werte exakt wie bisher an den Stellen.
DURCHSICHTIG = (0, 0, 0, 0)                                      # keine Farbe (Hintergrund/Vordergrund zurücksetzen)
SCHATTEN_KACHEL = (0, 0, 0, 190)                                 # Beschriftungsband über der Kachel
SCHATTEN_BLATT = (0, 0, 0, 60)                                   # Schatten unter dem Blatt in der Druckvorschau
SCHWARZ_RGB = (0, 0, 0)                                           # Schwarz ohne Deckkraft: ``QColor(*SCHWARZ_RGB, alpha)``
WEISS_RGB = (255, 255, 255)                                       # Weiß ohne Deckkraft
GRAU_RGB = (128, 128, 128)                                        # mittleres Grau ohne Deckkraft
ALPHA_VOLL = 255                                                  # volle Deckkraft
WEISS_GLANZ = (255, 255, 255, 55)                                 # Glanz auf Smartart-Knoten
SCHATTENANSATZ = (0, 0, 0, 110)                                   # Beginn des Schattens unter einem Textfeld
BILDVORLAGE_HELL = (255, 255, 255, 70)                           # Aufhellung des Bildes bei der Vorlage „Heller“
BILDVORLAGE_DUNKEL = (0, 0, 0, 70)                                # Abdunklung des Bildes bei der Vorlage „Dunkler“
ABDUNKELUNG = (0, 0, 0, 90)                                     # Abdunklung außerhalb des Ausschnitts / Lineal-Rand
WEISS_FLAECHE = (255, 255, 255)                                  # weiße Fläche (Deckkraft getrennt)
TABELLE_AKZENT = (47, 111, 181)                                  # Griffe und Rahmen der Tabellenbedienung
TABELLE_AKZENT_FLAECHE = (47, 111, 181, 30)                      # Füllung dazu
TABELLE_GRIFF_RAND = (120, 130, 150)                             # Rand der Minileiste
GRIFF_FLAECHE = (255, 255, 255, 235)                             # Grund der Minileiste
OBJEKT_KNOPF_RAND = (150, 160, 175)                              # Rand der Schaltflächen neben Objekten
OBJEKT_KNOPF_FLAECHE = (255, 255, 255, 240)                      # Grund der Schaltflächen neben Objekten
UMBRUCH_LINIE, UMBRUCH_LINIE_HINTER, UMBRUCH_FLAECHE = (110, 118, 130), (90, 96, 108), (76, 110, 245, 140)   # Sinnbilder der Textumbrüche
ZULETZT_SCHLUESSEL = "baukasten/zuletzt_farben"
ZULETZT_MAX = 10


def mische(a: str, b: str, anteil: float) -> str:
    """Mischt Farbe a zum Anteil (0…1) mit Farbe b."""
    x, y = QColor(a), QColor(b)
    return QColor(round(x.red() + (y.red() - x.red()) * anteil), round(x.green() + (y.green() - x.green()) * anteil),
                  round(x.blue() + (y.blue() - x.blue()) * anteil)).name()


def abstufungen(farbe: str) -> list[str]:
    """Fünf Abstufungen einer Themenfarbe, von hell nach dunkel (Weiß geht nur nach Grau, Schwarz nur nach Grau)."""
    f = QColor(farbe).name()
    if f == "#ffffff":
        return [mische(f, "#000000", t) for t in (0.05, 0.15, 0.25, 0.35, 0.5)]
    if f == "#000000":
        return [mische(f, "#ffffff", t) for t in (0.5, 0.35, 0.25, 0.15, 0.05)]
    return [mische(f, "#ffffff", 0.8), mische(f, "#ffffff", 0.6), mische(f, "#ffffff", 0.4),
            mische(f, "#000000", 0.25), mische(f, "#000000", 0.5)]


def thema_raster() -> list[list[str]]:
    """Zeilen der Themenfarben: erst die Grundfarben, darunter die fünf Abstufungen."""
    spalten = [[f] + abstufungen(f) for f in THEMA_FARBEN]
    return [[s[z] for s in spalten] for z in range(6)]


def zuletzt_laden() -> list[str]:
    try:
        wert = _einstellungen().get(ZULETZT_SCHLUESSEL, [])
    except Exception:
        return []
    if isinstance(wert, str):
        wert = [wert] if wert else []
    return [QColor(w).name() for w in (wert or []) if QColor(w).isValid()][:ZULETZT_MAX]


def zuletzt_merken(farbe: str) -> None:
    f = QColor(farbe).name()
    liste = [f] + [x for x in zuletzt_laden() if x != f]
    try:
        _einstellungen().set(ZULETZT_SCHLUESSEL, liste[:ZULETZT_MAX])
    except Exception:
        pass
