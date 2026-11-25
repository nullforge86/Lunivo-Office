"""Das einheitliche Layout des Dashboards (Dokumente · Prüfung · Ergebnisse · Fehlerbericht) — die Schicht des Prüfers in der Modulhierarchie von Lunivo:

    ``lunivo_writer.oberflaeche.baukasten.farben.Farbe``  und  ``oberflaeche.baukasten.basis.mass``   (Farben, Maße, Abstände, Ränder, Radien, Schriftstufen der Anwendung)
        └─ diese Datei: bezieht ALLE Werte von dort und benennt sie für die Rollen des Prüfers (Karte, Navigation, Hilfsband …); sie führt keine eigenen Zahlen
            └─ Seiten, Panels, Dialoge: schreiben keine Zahl, keine Farbe und kein Stylesheet selbst, sondern importieren aus dieser Datei.

So sieht der Prüfer aus wie die Anwendung, und eine Änderung an ``mass`` oder ``Farbe`` wirkt überall."""
from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget

from lunivo_writer.oberflaeche.baukasten.basis.raster import RasterLayout, RasterSpalte, RasterZeile          # noqa: F401  (Layouts der Panels: das Raster der Anwendung)
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FlussLayout, FormularGitter          # noqa: F401  (FlussLayout: umbrechende Zeilen der Panels)
from lunivo_writer.oberflaeche.baukasten.felder.karten_raster import KartenRaster

from lunivo_writer.farmwork.datentypen.farben import Farbe
from lunivo_writer.oberflaeche.baukasten.basis import mass as M
from lunivo_writer.oberflaeche.baukasten.basis.mass import ABSTAND_BLOCK, ABSTAND_ENG, ABSTAND_GROSS, ABSTAND_KEIN, ABSTAND_KLEIN, ABSTAND_MITTEL, ABSTAND_NORMAL, ABSTAND_SPALTE, RAND_KEIN

# ---- Ränder (links, oben, rechts, unten) ---------------------------------------------------------------------------------------------------------------
RAND_SEITE = M.RAND_SEITE_TITEL                                        # Seite mit Titel
RAND_PRUEFUNG = M.RAND_BACKSTAGE_SEITE                                 # die ruhige Fortschrittsseite: großzügiger Rand wie die Seiten der Datei-Ansicht
RAND_BAND = M.RAND_SEITE_TITEL[:3] + (0,)                              # Hilfsband über den Seiten
RAND_KENNZAHL = M.RAND_ZEILE_KARTE                                     # Karte mit Zahl und Beschriftung
RAND_NAVIGATION = M.RAND_KOPF_LINKS                                    # Navigationsleiste
RAND_EINRICHTEN = M.RAND_ERWEITERUNG_KARTE                             # Einrichtungskarte (Prüfarten, Referenz)

# ---- Höhen und Breiten --------------------------------------------------------------------------------------------------------------------------------
HOEHE_NAV_KNOPF = M.HOEHE_KNOPF_HOCH
HOEHE_START = M.HOEHE_KNOPF_HOCH
HOEHE_START_ZWEITER = M.HOEHE_KNOPF_GROSS
HOEHE_NEUE_PRUEFUNG = M.HOEHE_KNOPF_GROSS
HOEHE_BALKEN = M.HOEHE_FELD
HOEHE_AKTIVITAET_MIN = M.HOEHE_BEREICH_MITTEL
HOEHE_DATEIEN_MIN = M.HOEHE_LISTE_ANBIETER
HOEHE_ARTEN_MIN = M.HOEHE_LISTE_ANBIETER
HOEHE_ARTEN_MAX = M.HOEHE_LISTE_REITER
HOEHE_REFERENZ_MAX = M.HOEHE_VORSCHAU_DIAGRAMM
HOEHE_DETAIL_KOPF_MAX = M.HOEHE_LISTE_ZIEL
HOEHE_DETAILPANEL_KOPF_MAX = M.HOEHE_LISTE_REITER
HOEHE_DETAILPANEL_TEXT_MAX = M.HOEHE_VORSCHAU_KLEIN
HOEHE_ERWARTET_MAX = M.HOEHE_EINGABE_TEXT
HOEHE_LISTE_KLEIN_MAX = M.HOEHE_TEXT_MITTEL
HOEHE_AUFSCHLUESSELUNG_MAX = M.HOEHE_LISTE_MITTEL
HOEHE_ZEILE_ERGEBNIS = M.HOEHE_ZEILE_SONDER
HOEHE_ZEILE_DATEI = M.HOEHE_ZEILE_SONDER
HOEHE_ZEILE_ERGEBNISLISTE = M.HOEHE_ZELLE_SONDER

BREITE_NAVIGATION = M.BREITE_NAVIGATION_OPTIONEN
BREITE_SYMBOLKNOPF = M.BREITE_KNOPF_KLEIN
BREITE_ZOOMKNOPF = M.BREITE_KNOPF_KLEIN
BREITE_ZOOM_MAX = M.BREITE_LISTE_ARTEN
BREITE_DECKKRAFT_MAX = M.BREITE_LISTE_ARTEN
BREITE_SPALTE_NAME = M.BREITE_NAVIGATION_BACKSTAGE
BREITEN_SPALTEN_ERGEBNISLISTE = (M.BREITE_NAVIGATION_OPTIONEN, M.BREITE_SCHIENE_BESCHRIFTET, M.BREITE_LISTE_ARTEN)     # die letzte Spalte nimmt den Rest der Breite
BREITE_FEHLERPANEL_MIN = M.BREITE_SEITE_MIN
BREITE_KENNZAHL_MIN = M.BREITE_LISTE_ARTEN                             # schmalste Karte: wie viele nebeneinander passen, folgt aus der Fensterbreite

# ---- Fenstergrößen (Breite, Höhe) aus ``mass``; die Anteile begrenzen sie auf den Bildschirm -----------------------------------------------------------------
FENSTER_HAUPT = M.GROESSE_FENSTER_DRUCKVORSCHAU
ANTEIL_HAUPT = (0.92, 0.85)
FENSTER_HAUPT_MIN = M.GROESSE_FENSTER_EINFUEGEN_GROSS
ANTEIL_HAUPT_MIN = (0.8, 0.7)
FENSTER_LISTE = M.GROESSE_FENSTER_SERIENBRIEF
ANTEIL_LISTE_BREITE = 0.9
FENSTER_FEHLERPANEL = M.GROESSE_FENSTER_TABELLE
FENSTER_FEHLERDETAIL = M.GROESSE_FENSTER_EINFUEGEN_GROSS
FENSTER_KONFIG = M.GROESSE_FENSTER_KI
ANTEIL_KONFIG = (0.9, 0.85)
TEILER_GLEICH = (M.BREITE_SEITE_MIN, M.BREITE_SEITE_MIN)               # Vergleichsansicht: beide Hälften gleich breit
STRECKUNG_FEHLER_LISTE = (3, 2)                                        # Fehlerbericht: Liste zu Detail
STRECKUNG_GLEICH = (1, 1)

# ---- Schriftstufen: Punkte über der Grundschrift, aus den Stufen von ``mass`` ---------------------------------------------------------------------------
SCHRIFT_PLUS_NAVIGATION = M.SCHRIFT_HINWEIS - M.SCHRIFT_KLEIN
SCHRIFT_PLUS_PRUEFZEILE = M.SCHRIFT_UEBERSCHRIFT_KLEIN - M.SCHRIFT_HINWEIS
SCHRIFT_PLUS_ERGEBNIS = M.SCHRIFT_UEBERSCHRIFT - M.SCHRIFT_HINWEIS
SCHRIFT_PLUS_SEITENTITEL = M.SCHRIFT_UEBERSCHRIFT - M.SCHRIFT_KLEIN
SCHRIFT_PLUS_KENNZAHL = SCHRIFT_PLUS_SEITENTITEL + 2
SCHRIFT_PLUS_PRUEFTITEL = SCHRIFT_PLUS_SEITENTITEL + 3
SCHRIFT_KLEIN_PX = M.SCHRIFT_GRUPPENTITEL_PX
STIL_HTML_GROSS = "font-size:large"                                    # große Zeile in Rich-Text-Meldungen

# ---- Radien ---------------------------------------------------------------------------------------------------------------------------------------------
RADIUS_KARTE = M.RADIUS_KARTE
RADIUS_KNOPF = M.RADIUS_FELD
RADIUS_BAND = M.RADIUS_KLEIN

# ---- Farben, aus ``Farbe`` --------------------------------------------------------------------------------------------------------------------------------
FARBE_GRUND_ANSICHT = Farbe.GRAU                                       # Fläche hinter den Seitenbildern der Vergleichsansicht
FARBE_PAPIER = Farbe.WEISS
FARBE_AKZENT = Farbe.AKZENT
FARBE_AKZENT_HOVER = Farbe.AKZENT_HELL
FARBE_AKZENT_SCHRIFT = Farbe.AUF_AKZENT
FARBE_NEUTRAL = Farbe.GRAU
FARBEN = {"bestanden": Farbe.GRUEN, "teilweise": Farbe.WARNUNG, "auffaellig": Farbe.ORANGE, "fehlgeschlagen": Farbe.ROT, "nicht_pruefbar": FARBE_NEUTRAL,
          "abgebrochen": FARBE_NEUTRAL, "offen": FARBE_NEUTRAL, "kritisch": Farbe.ROT, "schwer": Farbe.ORANGE, "mittel": Farbe.WARNUNG, "gering": Farbe.AKZENT_HELL,
          "hinweis": FARBE_NEUTRAL}
KLASSEN_FARBEN = {"behoben": Farbe.GRUEN, "verbessert": Farbe.GRUEN, "unveraendert": FARBE_NEUTRAL, "verschlechtert": Farbe.ORANGE, "neu": Farbe.ROT,
                  "nicht_vergleichbar": FARBE_NEUTRAL, "nicht_durchgefuehrt": FARBE_NEUTRAL}
MARKENFARBE = {"fehlt in Lunivo": Farbe.ROT, "zusätzlich in Lunivo": Farbe.AKZENT, "anders gesetzt": Farbe.ORANGE}
MARKENFARBE_STANDARD = Farbe.ORANGE


def _mischen(farbe: str, mit: str, anteil: float) -> str:
    """``farbe`` zu ``anteil`` (0…1) mit ``mit`` gemischt."""
    a, b = (tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in (farbe, mit))
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * anteil) for x, y in zip(a, b))


def _band(farbe: str) -> tuple:
    """(Grund, Schrift, Rand) des Hilfsbands aus einer Farbe: heller Grund, dunkle Schrift, mittlerer Rand."""
    return _mischen(farbe, Farbe.WEISS, 0.88), _mischen(farbe, "#000000", 0.72), _mischen(farbe, Farbe.WEISS, 0.55)


BAND_FARBEN = {"bereit": _band(Farbe.AKZENT), "laeuft": _band(Farbe.WARNUNG), "abbrechend": _band(Farbe.WARNUNG), "abgebrochen": _band(Farbe.GRAU),
               "erfolgreich": _band(Farbe.GRUEN), "fehler": _band(Farbe.ROT)}

# ---- Stile (Stylesheet-Texte) ---------------------------------------------------------------------------------------------------------------------------
STIL_HINWEIS = "color: palette(placeholder-text)"
STIL_FETT = "font-weight: bold"
STIL_KLEIN = f"font-size: {SCHRIFT_KLEIN_PX}px"
STIL_KLEIN_HINWEIS = f"color: palette(placeholder-text); font-size: {SCHRIFT_KLEIN_PX}px; margin-left: {M.BREITE_NUMMER + 2}px"
STIL_SYMBOLKNOPF = f"padding: {ABSTAND_KLEIN}px"
STIL_KNOPF_BREIT = f"padding: {ABSTAND_KLEIN}px {ABSTAND_GROSS}px"


def stil_farbe(farbe: str) -> str:
    """Schriftfarbe als Stylesheet-Text."""
    return f"color: {farbe}"


def stil_band(zustand: str) -> str:
    """Stylesheet des Hilfsbands im Zustand ``zustand`` (Grund, Schrift und Rand aus ``BAND_FARBEN``)."""
    grund, schrift, rand = BAND_FARBEN[zustand]
    return f"background: {grund}; color: {schrift}; border: 1px solid {rand}; border-radius: {RADIUS_BAND}px; padding: {ABSTAND_NORMAL}px {ABSTAND_GROSS}px"


def stil() -> str:
    """Das Stylesheet des ganzen Dashboards, aus den Werten oben gebaut."""
    knopf = f"{ABSTAND_NORMAL}px {ABSTAND_SPALTE}px"
    gross = f"{ABSTAND_MITTEL}px {ABSTAND_SPALTE + ABSTAND_MITTEL}px"
    return f"""
QFrame#navigation {{ background: palette(window); border-right: 1px solid palette(mid); }}
QPushButton#nav {{ text-align: left; padding: {gross}; border: none; border-radius: {RADIUS_KNOPF}px; background: transparent; }}
QPushButton#nav:hover:!checked {{ background: palette(midlight); }}
QPushButton#nav:checked {{ background: palette(highlight); color: palette(highlighted-text); font-weight: bold; }}
QPushButton#haupt {{ font-weight: bold; padding: {gross}; border-radius: {RADIUS_KNOPF}px; background: {FARBE_AKZENT}; color: {FARBE_AKZENT_SCHRIFT}; border: none; }}
QPushButton#haupt:hover {{ background: {FARBE_AKZENT_HOVER}; }}
QPushButton#haupt:disabled {{ background: palette(mid); color: palette(midlight); }}
QPushButton#haupt2 {{ padding: {gross}; border-radius: {RADIUS_KNOPF}px; }}
QPushButton#segment {{ padding: {knopf}; border: 1px solid palette(mid); }}
QPushButton#segment:checked {{ background: palette(highlight); color: palette(highlighted-text); }}
QFrame#karte {{ border: 1px solid palette(mid); border-radius: {RADIUS_KARTE}px; }}
QPushButton {{ padding: {knopf}; }}
QToolButton {{ padding: {knopf}; }}
"""


# ---- Hilfen: die Werte anwenden -------------------------------------------------------------------------------------------------------------------------
def schrift_stufe(widget, plus: int, fett: bool = False) -> None:
    """Die Schrift des Widgets um ``plus`` Punkte größer (und auf Wunsch fett) setzen."""
    f = widget.font()
    f.setPointSize(f.pointSize() + plus)
    if fett:
        f.setBold(True)
    widget.setFont(f)


def textzeile(text: str = "") -> QLabel:
    """Ein Text, der sich der Breite anpasst: er bricht um, statt das Fenster breiter zu zwingen oder abgeschnitten zu werden."""
    l = QLabel(text)
    l.setWordWrap(True)
    return l


def groesse_aus_anteil(verfuegbar, groesse: tuple, anteil: tuple) -> tuple:
    """Fenstergröße: ``groesse``, aber höchstens ``anteil`` des verfügbaren Bildschirms."""
    return min(groesse[0], int(verfuegbar.width() * anteil[0])), min(groesse[1], int(verfuegbar.height() * anteil[1]))


class Kachelzeile(QWidget):
    """Eine Reihe gleich breiter Karten, die die ganze Breite nutzt und sich dem Fenster anpasst: bei schmalem Fenster rücken Karten in die nächste Zeile
    (so viele nebeneinander, wie ``BREITE_KENNZAHL_MIN`` erlaubt), bei breitem verteilen sie sich gleichmäßig auf die ganze Breite. Das Raster ist das
    ``KartenRaster`` der Anwendung."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._gitter = KartenRaster(self, min_breite=BREITE_KENNZAHL_MIN, abstand=ABSTAND_GROSS, gleiche_hoehe=False, hoechstens_anzahl=True)

    def hinzu(self, karte) -> None:
        self._gitter.addWidget(karte)


class Formular(FormularGitter):
    """Formular des Prüfers: je Zeile eine Beschriftung und ihr Feld (wie zuvor), auf dem Formularraster der Anwendung. Direkt in einer Gruppe
    bekommt es den Innenrand der Rolle „gruppe“ — wie jede andere Gruppe des Prüfers."""
    einspaltig = True

    def __init__(self, eltern: QWidget | None = None):
        super().__init__(eltern)
        if eltern is not None:
            from lunivo_writer.oberflaeche.baukasten.geruest.rollen import raender
            raender(self, "gruppe")
