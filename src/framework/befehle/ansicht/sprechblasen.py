"""Sprechblasen (Kommentare und Änderungen im Seitenrand): Abfragen. Einstellungen, Blasen, Maße und Stapelung berechnet der Kern; die Oberfläche
erhält unveränderliche Beschreibungen und Kopien."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict

from core.objekte.formen import sprechblasen_modell as modell
from framework.dokumentverwaltung.ausgabe.textsatz import standard_engine
from framework.schnittstellen.aenderungs_port import AenderungsPort
from framework.schnittstellen.einstellungen import Einstellungen
from framework.schnittstellen.sprechblasen import BlasenEinstellung, BlasenKatalog, BlasenSchrift, Sprechblase


def _einstellung(k: dict) -> BlasenEinstellung:
    return BlasenEinstellung(verwenden=k["verwenden"], breite_mm=float(k["breite_mm"]), empfohlen=bool(k["empfohlen"]), rand=k["rand"],
                             linien=bool(k["linien"]), ausrichtung=k["ausrichtung"])


def katalog() -> BlasenKatalog:
    """Auswahlmöglichkeiten, Standardwerte und Maße."""
    return BlasenKatalog(verwenden=tuple(modell.VERWENDEN), rand=tuple(modell.RAND), ausrichtung=tuple(modell.AUSRICHTUNG),
                         standard=_einstellung(modell.STANDARD), luecke_mm=modell.LUECKE_MM, kopf_hoehe=modell.KOPF_HOEHE,
                         blase_rand=modell.BLASE_RAND, blase_ueberabtastung=modell.BLASE_UEBERABTASTUNG)


def konfig_lesen(e: Einstellungen) -> BlasenEinstellung:
    """Die Einstellungen der Sprechblasen (fehlende oder ungültige Werte bekommen den Standard)."""
    return _einstellung(modell.konfig_lesen(e))


def breite_mm(konfig: BlasenEinstellung) -> float:
    return modell.breite_mm(asdict(konfig))


def aktiv(konfig: BlasenEinstellung) -> bool:
    return modell.aktiv(asdict(konfig))


def blasen_px(schluessel: str) -> int:
    """Schriftgröße der Blasen im Editor (Bildpunkte bei 100 % Zoom) zu „klein“, „mittel“, „gross“."""
    return modell.blasen_px(schluessel)


def karten_pt(schluessel: str) -> float:
    """Schriftgröße der Kommentarkarten in Punkt zu „klein“, „mittel“, „gross“."""
    return modell.karten_pt(schluessel)


def blasen_schrift(px: float) -> BlasenSchrift:
    """Die Schrift der Blasen: Grundschrift des Dokuments, Größe aus Bildpunkten (96 dpi) in Punkt."""
    f = modell.blasen_schrift(px)
    return BlasenSchrift(f.family, f.size_pt, f.weight, f.italic)


def sammeln(editor: AenderungsPort, verwenden: str = "Nur für Kommentare") -> tuple[Sprechblase, ...]:
    """Alle Blasen des Dokuments in Textreihenfolge als unveränderliche Beschreibungen; gelesen über den Anschluss des Editors."""
    gefunden = editor.lesen(lambda sitzung: modell.sammeln_modell(sitzung, verwenden))
    return tuple(Sprechblase(b.von, b.bis, b.autor, b.datum, b.art, b.text, b.farbe, b.kid) for b in gefunden)


def messen(blase: Sprechblase, breite: float, schrift: BlasenSchrift) -> float:
    """Höhe der Blase bei gegebener Breite (Bildpunkte des Zeichengeräts)."""
    return modell.messen(standard_engine(), blase, breite, schrift)


def stapeln(anker_y: Sequence[float], hoehen: Sequence[float], unten: float, abstand: float = 6.0) -> tuple[float, ...]:
    """Obere Kanten der Blasen: so nah wie möglich am Anker, ohne Überlappung."""
    return tuple(modell.stapeln(list(anker_y), list(hoehen), unten, abstand))


def ortszeit(iso: str) -> str:
    """Zeitangabe der Blase in der Ortszeit."""
    return modell._ortszeit(iso)
