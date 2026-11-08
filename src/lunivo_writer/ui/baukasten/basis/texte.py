"""Gedämpfte Texte und Trennlinien der Oberfläche — ein Baustein statt einzelner Stylesheets.

``hinweis_label`` (Hinweis-/Leertext), ``kleintext_label`` (kleine Beschriftung), ``trennlinie`` (feine waagerechte Linie).
Die Farbe wird bei jedem Aufruf aus ``Farbe.HINWEIS`` gelesen; bei Themenwechsel setzt ``theme.apply_theme`` die Stile neu (``auffrischen``).
"""
from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.basis.mass import PADDING_HINWEIS, SCHRIFT_HINWEIS

_EIGENSCHAFT = "hinweisKlein"          # 0 = normale Größe, 1 = klein; fehlt = kein Hinweistext


def _stil(klein: bool, zusatz: str = "") -> str:
    return f"color: {Farbe.HINWEIS};" + (" font-size: " f"{SCHRIFT_HINWEIS}" "pt;" if klein else "") + (" " + zusatz if zusatz else "")


def hinweis_label(text: str = "", *, umbruch: bool = True, klein: bool = False, zusatz: str = "") -> QLabel:
    """Gedämpfter Hinweis-/Leertext (Farbe ``Farbe.HINWEIS``), auf Wunsch klein (9 pt) und mit Zeilenumbruch; ``zusatz`` hängt weitere Stilangaben an (z. B. ``padding: """ f"{PADDING_HINWEIS}" """;``)."""
    t = QLabel(text)
    t.setWordWrap(umbruch)
    t.setProperty(_EIGENSCHAFT, 1 if klein else 0)
    t.setProperty("hinweisZusatz", zusatz)
    t.setStyleSheet(_stil(klein, zusatz))
    return t


def hinweis_stil(label: QLabel, *, klein: bool = False, zusatz: str = "") -> QLabel:
    """Macht ein vorhandenes Label zum gedämpften Hinweistext (für Labels, die anders gebaut werden, z. B. mit eigener Schrift oder Ausrichtung)."""
    label.setProperty(_EIGENSCHAFT, 1 if klein else 0)
    label.setProperty("hinweisZusatz", zusatz)
    label.setStyleSheet(_stil(klein, zusatz))
    return label


def kleintext_label(text: str = "") -> QLabel:
    """Kleine gedämpfte Beschriftung (z. B. „Für wen“), ohne Zeilenumbruch."""
    return hinweis_label(text, umbruch=False, klein=True)


def trennlinie(*, senkrecht: bool = False, tief: bool = False) -> QFrame:
    """Feine Trennlinie: waagerecht (Standard) oder ``senkrecht``; ``tief`` = die vertiefte Linie des Stils, sonst eine Linie in ``midlight``."""
    linie = QFrame()
    linie.setFrameShape(QFrame.VLine if senkrecht else QFrame.HLine)
    if tief:
        linie.setFrameShadow(QFrame.Sunken)
    else:
        linie.setFrameShadow(QFrame.Plain)
        linie.setStyleSheet("color: palette(midlight);")
    return linie


def auffrischen(widget) -> None:
    """Setzt den Stil eines Hinweistexts nach einem Themenwechsel mit der neuen ``Farbe.HINWEIS`` neu."""
    klein = widget.property(_EIGENSCHAFT)
    if klein is not None and isinstance(widget, QLabel):
        widget.setStyleSheet(_stil(bool(klein), widget.property("hinweisZusatz") or ""))


def marke_faerben(w, grund: str, schrift: str, rest: str) -> None:
    """Farbige Marke (Chip-Label): ``grund``/``schrift`` sind Farben; ist ``grund`` die Akzentfarbe, kommen Fläche und Schrift aus dem Thema
    (Eigenschaft ``akzentFlaeche``, Regel in ui/theme.py), das Widget-Stylesheet trägt dann nur ``rest`` (Nicht-Farbwerte)."""
    from lunivo_writer.core.farben import Farbe
    if grund == Farbe.AKZENT:
        w.setProperty("akzentFlaeche", True)
        w.setStyleSheet(rest)
    else:
        w.setStyleSheet(f"background: {grund}; color: {schrift}; {rest}")
