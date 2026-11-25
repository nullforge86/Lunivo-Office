"""Sprechblasen: die Steuerung der Oberfläche. Reicht Abfragen an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.ansicht import sprechblasen as befehle
from framework.schnittstellen.aenderungs_port import AenderungsPort
from framework.schnittstellen.einstellungen import Einstellungen
from framework.schnittstellen.sprechblasen import BlasenEinstellung, BlasenKatalog, BlasenSchrift, Sprechblase


def katalog() -> BlasenKatalog:
    return befehle.katalog()


def konfig_lesen(e: Einstellungen) -> BlasenEinstellung:
    return befehle.konfig_lesen(e)


def breite_mm(konfig: BlasenEinstellung) -> float:
    return befehle.breite_mm(konfig)


def aktiv(konfig: BlasenEinstellung) -> bool:
    return befehle.aktiv(konfig)


def blasen_px(schluessel: str) -> int:
    return befehle.blasen_px(schluessel)


def karten_pt(schluessel: str) -> float:
    return befehle.karten_pt(schluessel)


def blasen_schrift(px: float) -> BlasenSchrift:
    return befehle.blasen_schrift(px)


def sammeln(editor: AenderungsPort, verwenden: str = "Nur für Kommentare") -> tuple[Sprechblase, ...]:
    return befehle.sammeln(editor, verwenden)


def messen(blase: Sprechblase, breite: float, schrift: BlasenSchrift) -> float:
    return befehle.messen(blase, breite, schrift)


def stapeln(anker_y: list[float], hoehen: list[float], unten: float, abstand: float = 6.0) -> list[float]:
    return befehle.stapeln(anker_y, hoehen, unten, abstand)


def ortszeit(iso: str) -> str:
    return befehle.ortszeit(iso)
