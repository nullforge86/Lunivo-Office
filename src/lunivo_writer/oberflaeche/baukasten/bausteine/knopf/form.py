"""Form des Knopfes: Größe und Gewicht je Rolle – die EINE Stelle dafür. Ändert sich eine Form hier (aus den Maßen in ``basis/mass``), ändern sich alle Knöpfe dieser Form
in der ganzen Oberfläche; eine Funktionsdatei nennt nur den Namen der Form."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractButton, QToolButton

from lunivo_writer.oberflaeche.baukasten.basis import mass as m

# Form → (Mindesthöhe, feste Breite); ``None``: das Thema bestimmt
FORMEN: dict[str, tuple[int | None, int | None]] = {
    "standard": (None, None),                           # der Knopf, wie das Thema ihn zeichnet
    "klein": (m.HOEHE_KNOPF, None),                     # Knopf in Zeilen mit Feldern
    "gross": (m.HOEHE_KNOPF_GROSS, None),               # Knopf neben Feldern in Fenstern und Panels
    "hoch": (m.HOEHE_KNOPF_HOCH, None),                 # betonter Knopf (Fußleiste)
    "symbol": (m.HOEHE_KNOPF, m.HOEHE_KNOPF),           # quadratischer Knopf nur mit Symbol
    "leseende": (m.HOEHE_LESEENDE_KNOPF, None),         # „Lesemodus beenden“ in der Statusleiste
    "thema": (m.HOEHE_THEMAKNOPF, None),                # „Hell / Dunkel“ in der Statusleiste
    "zoomanzeige": (None, None),                        # Zoomanzeige der Statusleiste (Mindestbreite siehe ``MIN_BREITEN``)
    "band_menue": (None, None),                         # „Menü“ im Band: Text neben dem Symbol
    "band_menue_kopf": (None, None),                    # „Menü“ im Kopf: Symbol rechts vom Text
    "band_stil": (None, None),                          # Formatvorlage im Band: Text unter dem Symbol
    "fest": (None, None),                               # feste Größe, die der Aufrufer aus dem Inhalt ableitet (``groesse=``)
}

# Form → (Stil des Werkzeugknopfes, Symbol rechts vom Text); nur Werkzeugknöpfe
WERKZEUG_STILE: dict[str, tuple[Qt.ToolButtonStyle, bool]] = {
    "band_menue": (Qt.ToolButtonTextBesideIcon, False),
    "band_menue_kopf": (Qt.ToolButtonTextBesideIcon, True),
    "band_stil": (Qt.ToolButtonTextUnderIcon, False),
}

# Form → Mindestbreite (nur Formen, die eine brauchen)
MIN_BREITEN: dict[str, int] = {"zoomanzeige": m.BREITE_ZOOMANZEIGE}


def formen(knopf: QAbstractButton, form: str, groesse: tuple[int, int] | None = None, ohne_rand: bool = False) -> QAbstractButton:
    """Wendet die Form auf den Knopf an; ``groesse`` (Breite, Höhe) legt eine feste Größe fest, die der Aufrufer aus dem Inhalt ableitet; ``ohne_rand``: flacher Druckknopf."""
    if groesse is not None:
        knopf.setFixedSize(*groesse)
    if ohne_rand and hasattr(knopf, "setFlat"):
        knopf.setFlat(True)
    if form in WERKZEUG_STILE and isinstance(knopf, QToolButton):
        stil, rechts_nach_links = WERKZEUG_STILE[form]
        knopf.setToolButtonStyle(stil)
        if rechts_nach_links:
            knopf.setLayoutDirection(Qt.RightToLeft)
    hoehe, breite = FORMEN[form]
    if hoehe is not None:
        knopf.setMinimumHeight(hoehe)
    if breite is not None:
        knopf.setFixedWidth(breite)
    if form in MIN_BREITEN:
        knopf.setMinimumWidth(MIN_BREITEN[form])
    return knopf
