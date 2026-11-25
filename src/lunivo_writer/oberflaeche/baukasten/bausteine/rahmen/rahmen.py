"""Rahmen als Baustein aus Form, Inhalt und Verhalten.

    rahmen("flach", karte="nutzer")                 # Karte der Art „nutzer“ ohne eigenen Rahmenstrich
    rahmen("panel", name="sfPfad")                  # Kasten mit Rahmen des Themas
    rahmen("linie_waagerecht")                      # Trennlinie"""
from __future__ import annotations

from PySide6.QtWidgets import QFrame, QWidget

from lunivo_writer.oberflaeche.baukasten.bausteine.rahmen.form import formen
from lunivo_writer.oberflaeche.baukasten.bausteine.rahmen.inhalt import beschriften
from lunivo_writer.oberflaeche.baukasten.bausteine.rahmen.verhalten import verbinden


def rahmen(form: str = "flach", *, karte: str = "", name: str = "", sichtbar: bool = True, eigenschaften: dict[str, object] | None = None,
           eltern: QWidget | None = None) -> QFrame:
    r = QFrame(eltern)
    formen(r, form)
    beschriften(r, name, karte)
    verbinden(r, sichtbar, eigenschaften)
    return r
