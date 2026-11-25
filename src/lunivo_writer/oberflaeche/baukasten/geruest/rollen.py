"""Layout-Rollen — die EINE Stelle, an der Ränder und Abstände festgelegt werden.

Eine Seite, ein Fenster oder eine Zeile bestimmt ihr Layout nicht selbst, sondern nennt nur ihre Rolle: ``spalte("abschnitt", eltern)`` /
``reihe("zeile", eltern)``. Welche Ränder und Abstände eine Rolle hat, steht ausschließlich in ``ROLLEN`` — ändert sich dort ein Wert,
ändern sich alle Seiten gleichzeitig, und keine Datei kann abweichen. Die Zahlen selbst kommen aus ``mass``.

Jedes Layout, das hier entsteht, ist ein ``QGridLayout`` aus ``baukasten/basis/raster.py``: ``spalte`` legt die Elemente in die Zellen
``(0, 0), (1, 0) …``, ``reihe`` in ``(0, 0), (0, 1) …``. Diese Datei ist damit die eine Stelle, an der die Rasterregeln (Außenrand,
waagerechter und senkrechter Zellenabstand) der ganzen Oberfläche festgelegt werden."""
from __future__ import annotations

from PySide6.QtWidgets import QWidget

from lunivo_writer.oberflaeche.baukasten.basis import mass as m
from lunivo_writer.oberflaeche.baukasten.basis.raster import RasterSpalte, RasterZeile

ROLLEN: dict[str, tuple[tuple, int]] = {
    # --- Stufen ohne eigenen Rand: nur der Abstand zwischen den Elementen (Stufen aus mass.ABSTAND_*) ---
    "kein":     (m.RAND_KEIN, m.ABSTAND_KEIN),
    "eng":      (m.RAND_KEIN, m.ABSTAND_KLEIN),                 # dicht gepackte Elemente (Zeile aus Symbol und Text)
    "standard": (m.RAND_KEIN, m.ABSTAND_NORMAL),                # verschachteltes Layout, der Normalfall
    "inhalt":   (m.RAND_KEIN, m.ABSTAND_MITTEL),                # Elemente nebeneinander/untereinander mit Luft (Bedienelemente, Blöcke)
    # --- Funktionen: jede Rolle beschreibt, WOFÜR der Bereich da ist ---
    "seite":    (m.RAND_SEITE_TITEL, m.ABSTAND_MITTEL),         # eine Seite einer Ansicht (Optionen, Datei-Ansicht)
    "fenster":  (m.RAND_EXPORT_FENSTER, m.ABSTAND_MITTEL),      # Inhalt eines Fensters oder Dialogs
    "aussen":   (m.RAND_FENSTER_DRUCKEN, m.ABSTAND_KEIN),       # Hülle um Inhalt und Fußzeile
    "kopf":     (m.RAND_KOPF_LINKS, m.ABSTAND_NORMAL),          # Kopfbereich einer Fläche
    "fuss":     (m.RAND_FUSS_BACKSTAGE, m.ABSTAND_MITTEL),      # Fußleiste mit Aktionsknöpfen
    "panel":    (m.RAND_PANEL_KLEIN, m.ABSTAND_NORMAL),         # Inhalt eines Panels, einer Navigation oder einer kompakten Box
    "panel_inhalt": (m.RAND_PANEL_INHALT, m.ABSTAND_MITTEL),    # Inhalt eines Seitenleistenfensters, bündig zwischen Kopfzeile und Knopfzeile
    "panel_kopf": (m.RAND_PANEL_KOPF, m.ABSTAND_ENG),           # Kopfzeile eines Seitenleistenfensters
    "popup":    (m.RAND_POPUP_SEITE, m.ABSTAND_KLEIN),          # Dropdown-Fenster und Menüs (Kopf, Seite, Fuß)
    "leiste":   (m.RAND_SYMBOLLEISTE, m.ABSTAND_ENG),           # Werkzeug-, Reiter- und Symbolleisten
    "karte":    (m.RAND_KARTE_ZEILE, m.ABSTAND_NORMAL),         # abgesetzte Karte (Fund, Vorschlag, Info)
    "gruppe":   (m.RAND_OPTIONEN_GRUPPE, m.ABSTAND_NORMAL),     # Kachel einer Optionen-Seite
    "abschnitt": (m.RAND_ABSCHNITT, m.ABSTAND_MITTEL),          # Abschnitt innerhalb einer Kachel oder Seite
    "zeile":    (m.RAND_ZEILE, m.ABSTAND_GROSS),                # Zeile mit Luft oben und unten
    "paar":     (m.RAND_ZEILE_PAAR, m.ABSTAND_KEIN),            # Einstellung mit Erklärsatz direkt darunter
    "oben":     (m.RAND_OBEN_SEITE, m.ABSTAND_NORMAL),          # Abstand über einem Block
    "einzug":   (m.RAND_EXPORT_SEITENZEILE, m.ABSTAND_NORMAL),  # eingerückte Zeile oder Gruppe
    # --- Besonderheiten einzelner Seiten, die fachlich begründet lokal bleiben ---
    "listenkopf":      (m.RAND_LISTENKOPF, m.ABSTAND_NORMAL),   # Navigationsliste der Datei-Ansicht
    "zuletzt":         (m.RAND_ZULETZT_ZEILE, m.ABSTAND_NORMAL),   # Zeile der Zuletzt-Liste (Platz für das Dateisymbol)
    "zuletzt_liste":   (m.RAND_ZEILE_BACKSTAGE, m.ABSTAND_ENG),
    "pfadleiste":      (m.RAND_SPEICHERN_PFAD, m.ABSTAND_KEIN),    # Pfadleiste im Speichern-Fenster
    "pfadtrenner":     (m.RAND_PFADTRENNER, m.ABSTAND_KEIN),
    "vorschau_seiten": (m.RAND_DRUCKVORSCHAU_SEITEN, m.ABSTAND_DRUCKVORSCHAU_SEITEN),   # Ablagefläche der Druckvorschau
    "rand_seitlich":   (m.RAND_HILFE_SEITE, m.ABSTAND_NORMAL),
    "formatseite":     (m.RAND_FORMATSEITE, m.ABSTAND_SPALTE),     # Seite eines Formatpanels (Diagramm, Texteffekt, Füllung)
    "bandhalter":      (m.RAND_BANDHALTER, m.ABSTAND_KLEIN),       # mehrere Felder übereinander in einer Bandgruppe
    "menuekopf":       (m.RAND_MENUEKOPF, m.ABSTAND_NORMAL),       # Kopfzeile über den Kacheln eines Auswahlmenüs
    "bandgruppe":      (m.RAND_KEIN, m.ABSTAND_DICHT),             # Knöpfe einer Bandgruppe, dicht gepackt
}


def anwenden(lay, rolle: str):
    """Ränder UND Abstand der Rolle auf ein vorhandenes Layout anwenden."""
    rand, abstand = ROLLEN[rolle]
    lay.setContentsMargins(*rand)
    lay.setSpacing(abstand)
    return lay


def spalte(rolle: str = "standard", eltern: QWidget | None = None) -> RasterSpalte:
    """Gitterspalte (Elemente untereinander) mit den Rändern und Abständen der Rolle."""
    return anwenden(RasterSpalte(eltern), rolle)


def reihe(rolle: str = "standard", eltern: QWidget | None = None) -> RasterZeile:
    """Gitterzeile (Elemente nebeneinander) mit den Rändern und Abständen der Rolle."""
    return anwenden(RasterZeile(eltern), rolle)


def raender(layout, rolle: str):
    """Nur die Ränder der Rolle auf ein vorhandenes Layout (z. B. ``widget.layout()``) anwenden."""
    layout.setContentsMargins(*ROLLEN[rolle][0])
    return layout


def rand(rolle: str) -> tuple:
    return ROLLEN[rolle][0]
