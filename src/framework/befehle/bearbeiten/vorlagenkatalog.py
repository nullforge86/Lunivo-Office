"""Der Katalog der Formatvorlagen (eingebaute und eigene) und die Designs (Farbschemen, Schriftpaare, Effekte) für die Oberfläche.

Die Daten liegen im Kern (``core.formatvorlagen.zeichen``); hier gehen nur Kopien hinaus und Kopien hinein – die Oberfläche hält nie ein
Objekt des Kerns in der Hand."""
from __future__ import annotations

import copy
from collections.abc import Mapping
from types import MappingProxyType

import core.formatvorlagen.zeichen as _katalog

Angabe = str | int | float | bool | None | tuple | Mapping


def _kopie(d: dict) -> Mapping[str, Angabe]:
    return MappingProxyType(copy.deepcopy(dict(d)))


# ---- Formatvorlagen ------------------------------------------------------------------------------------------------------------------
def namen() -> tuple[str, ...]:
    """Alle Vorlagen (eingebaute und eigene) in der Reihenfolge des Katalogs."""
    return tuple(_katalog.namen())


def eingebaute_namen() -> tuple[str, ...]:
    return tuple(_katalog.NAMEN)


def vorlage() -> Mapping[str, Angabe]:
    """Die Felder einer Vorlage mit ihren Vorgaben (``stile.VORLAGE``)."""
    return _kopie(_katalog.VORLAGE)


def definition(name: str) -> Mapping[str, Angabe]:
    """Die wirksamen Felder der Vorlage ``name`` (mit Basis aufgelöst)."""
    return _kopie(_katalog.definition(name))


def ist_eigen(name: str) -> bool:
    return bool(_katalog.ist_eigen(name))


def eigene_angaben(name: str) -> Mapping[str, Angabe]:
    """Die selbst gesetzten Felder einer eigenen Vorlage (leer bei eingebauten)."""
    return _kopie(_katalog.eigene_angaben(name))


def pruefe_name(name: str) -> str | None:
    return _katalog.pruefe_name(name)


def anlegen(name: str, basis: str = "", folge: str = "", felder: Mapping[str, Angabe] | None = None) -> str | None:
    return _katalog.anlegen(name, basis=basis, folge=folge, **copy.deepcopy(dict(felder or {})))


def aendern(name: str, felder: Mapping[str, Angabe]) -> None:
    _katalog.aendern(name, **copy.deepcopy(dict(felder)))


def loeschen(name: str) -> bool:
    return bool(_katalog.loeschen(name))


def laden(text: str) -> None:
    _katalog.laden(text)


def laden_neu(text: str) -> None:
    _katalog.laden_neu(text)


def als_json() -> str:
    return _katalog.als_json()


def als_json_neu() -> str:
    return _katalog.als_json_neu()


# ---- Designs -------------------------------------------------------------------------------------------------------------------------
def design_namen() -> Mapping[str, tuple[str, str]]:
    """Design → (Farbschema, Schriftpaar)."""
    return MappingProxyType({k: tuple(v) for k, v in _katalog.DESIGNS.items()})


def farbschemen() -> Mapping[str, tuple[str, ...]]:
    return MappingProxyType({k: tuple(v) for k, v in _katalog.FARBSCHEMEN.items()})


def schriftpaare() -> Mapping[str, tuple[str, str]]:
    return MappingProxyType({k: tuple(v) for k, v in _katalog.SCHRIFTPAARE.items()})


def effekte() -> Mapping[str, Mapping[str, Angabe]]:
    return MappingProxyType({k: _kopie(v) for k, v in _katalog.EFFEKTE.items()})


def ueberschrift_farbe(schema: str) -> str:
    return str(_katalog.ueberschrift_farbe(schema))


def design(name: str) -> Mapping[str, Angabe]:
    """Was ein Design setzt: Schriften, Überschriftfarbe, das ganze Farbschema."""
    d = _katalog.design(name)
    return MappingProxyType({**d, "farben": tuple(d["farben"])})
