"""Tür des Pakets ``writer.funktionen.bearbeiten``. Aufrufer außerhalb des Pakets importieren nur von hier."""
from __future__ import annotations

from writer.funktionen.bearbeiten.gehe_zu import gehe_zu_eingabe_titel, gehe_zu_element, gehe_zu_elemente, gehe_zu_hat_elemente
from writer.funktionen.bearbeiten.wortextras import wortextra_ausfuehren, wortextras_menue

__all__ = ["gehe_zu_eingabe_titel", "gehe_zu_element", "gehe_zu_elemente", "gehe_zu_hat_elemente", "wortextra_ausfuehren", "wortextras_menue"]
