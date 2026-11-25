"""Klappen (Pfeilmenüs) des Kontext-Reiters „Kopf- und Fußzeile“ als Datenbeschreibung. Die Oberfläche baut daraus die Menüs."""
from __future__ import annotations

from lunivo_writer.farmwork.funktionen.kopffuss.typen import TRENNER, MenueEintrag

AUSRICHTUNGEN = (("Links", "left"), ("Zentriert", "center"), ("Rechts", "right"), ("Außen", "aussen"), ("Innen", "innen"))
ALLE_FELDER = "header,footer,first_header,first_footer,even_header,even_footer"


def gruppe(bearbeitung_aktiv: bool) -> tuple[MenueEintrag, ...]:
    return (MenueEintrag("Kopfzeile bearbeiten", "bearbeiten:kopf"), MenueEintrag("Fußzeile bearbeiten", "bearbeiten:fuss"),
            MenueEintrag("Zwischen Kopf- und Fußzeile wechseln", "wechseln", aktiv=bearbeitung_aktiv))


def zone(zone_name: str) -> tuple[MenueEintrag, ...]:
    feld = "header" if zone_name == "kopf" else "footer"
    name = "Kopfzeile" if zone_name == "kopf" else "Fußzeile"
    return ((MenueEintrag(name + " bearbeiten", f"bearbeiten:{zone_name}"), TRENNER)
            + tuple(MenueEintrag(text, f"ausrichten:{zone_name}:{ausr}") for text, ausr in AUSRICHTUNGEN)
            + (TRENNER, MenueEintrag(name + " entfernen", f"leeren:{feld}")))


def linie() -> tuple[MenueEintrag, ...]:
    return (MenueEintrag("Kopfzeile entfernen", "leeren:header"), MenueEintrag("Fußzeile entfernen", "leeren:footer"),
            MenueEintrag("Kopf- und Fußzeile entfernen", f"leeren:{ALLE_FELDER}"))


def einstellungen() -> tuple[MenueEintrag, ...]:
    return (MenueEintrag("Optionen für Kopf- und Fußzeile …", "optionen_dialog"), MenueEintrag("Seite einrichten …", "seite_einrichten"), TRENNER,
            MenueEintrag("Kopf- und Fußzeile schließen", "schliessen"))
