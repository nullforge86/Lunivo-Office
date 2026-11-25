"""Der Katalog der Formatvorlagen und die Designs für die Oberfläche: ordnet die Fenster und Bandbefehle dem Framework zu.

Was hinausgeht, ist eine Kopie (Wörterbücher als neue ``dict``, Listen als Tupel); was hineingeht, kopiert das Framework, bevor der Kern es sieht."""
from __future__ import annotations

from framework.befehle import bearbeiten as _fw


# ---- Formatvorlagen ------------------------------------------------------------------------------------------------------------------
def namen() -> tuple[str, ...]:
    return _fw.namen()


def eingebaute_namen() -> tuple[str, ...]:
    return _fw.eingebaute_namen()


def vorlage() -> dict:
    """Die Felder einer Vorlage mit ihren Vorgaben (eine Kopie)."""
    return dict(_fw.vorlage())


def definition(name: str) -> dict:
    """Die wirksamen Felder der Vorlage ``name`` (eine Kopie)."""
    return dict(_fw.definition(name))


def ist_eigen(name: str) -> bool:
    return _fw.ist_eigen(name)


def eigene_angaben(name: str) -> dict:
    """Die selbst gesetzten Felder einer eigenen Vorlage (leer bei eingebauten; eine Kopie)."""
    return dict(_fw.eigene_angaben(name))


def pruefe_name(name: str) -> str | None:
    return _fw.pruefe_name(name)


def anlegen(name: str, *, basis: str = "", folge: str = "", **felder) -> str | None:
    """Legt eine eigene Vorlage an; → Grund, wenn es nicht geht."""
    return _fw.anlegen(name, basis, folge, felder)


def aendern(name: str, **felder) -> None:
    _fw.aendern(name, felder)


def loeschen(name: str) -> bool:
    return _fw.loeschen(name)


def laden(text: str) -> None:
    _fw.laden(text)


def laden_neu(text: str) -> None:
    _fw.laden_neu(text)


def als_json() -> str:
    return _fw.als_json()


def als_json_neu() -> str:
    return _fw.als_json_neu()


# ---- Designs -------------------------------------------------------------------------------------------------------------------------
def designs() -> dict:
    """Design → (Farbschema, Schriftpaar)."""
    return dict(_fw.design_namen())


def farbschemen() -> dict:
    return dict(_fw.farbschemen())


def schriftpaare() -> dict:
    return dict(_fw.schriftpaare())


def effekte() -> dict:
    return {k: dict(v) for k, v in _fw.effekte().items()}


def ueberschrift_farbe(schema: str) -> str:
    return _fw.ueberschrift_farbe(schema)


def design(name: str) -> dict:
    return dict(_fw.design(name))
