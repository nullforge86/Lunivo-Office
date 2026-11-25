"""Sonderzeichen hilfen: aus ``vcl.qt.widgets.dialoge.einfuegen.sonderzeichen`` herausgelöst."""
from __future__ import annotations
import json
from vcl.qt.widgets.dialoge.dokument.tasten_dialog import TastenDialog
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.abstaende.mass import HOEHE_ZELLE_SONDER


KEY_ZULETZT = "einfuegen/symbole_zuletzt"


KEY_BENUTZER = "einfuegen/symbole_benutzer"


KEY_TASTEN = "einfuegen/symbole_tasten"


ZELLE = HOEHE_ZELLE_SONDER


class SymbolDaten:
    """Zuletzt verwendet, benutzerdefinierte Symbole (Zeichen, Haken) und Tastenkombinationen — in den Einstellungen (``get``/``set``)."""

    def __init__(self, einstellungen=None, standard: tuple = (), anzahl: int = 24):
        self.e = einstellungen if einstellungen is not None else _Speicher()
        self.standard, self.anzahl = tuple(standard), anzahl

    def _lesen(self, key: str, leer):
        try:
            wert = json.loads(str(self.e.get(key, "") or ""))
        except ValueError:
            return leer
        return wert if isinstance(wert, type(leer)) else leer

    def zuletzt(self) -> list[str]:
        return [z for z in self._lesen(KEY_ZULETZT, []) if isinstance(z, str) and z]

    def merken(self, z: str) -> None:
        liste = [z] + [x for x in self.zuletzt() if x != z]
        self.e.set(KEY_ZULETZT, json.dumps(liste[:self.anzahl], ensure_ascii=False))

    def benutzer(self) -> list[tuple[str, bool]]:
        """Die Liste „Benutzerdefinierte Symbole“ in ihrer Reihenfolge, je Zeichen mit Haken (``True``: in der Klappe zu sehen)."""
        if not str(self.e.get(KEY_BENUTZER, "") or ""):
            return [(z, True) for z in self.standard]
        return [(p[0], bool(p[1])) for p in self._lesen(KEY_BENUTZER, []) if isinstance(p, list) and len(p) == 2 and isinstance(p[0], str) and p[0]]

    def setze_benutzer(self, liste: list[tuple[str, bool]]) -> None:
        self.e.set(KEY_BENUTZER, json.dumps([[z, an] for z, an in liste], ensure_ascii=False) if liste else "[]")

    def sichtbar(self) -> list[str]:
        return [z for z, an in self.benutzer() if an]

    def zuruecksetzen(self) -> None:
        self.e.set(KEY_BENUTZER, ""); self.e.set(KEY_TASTEN, "")

    def tasten(self) -> dict[str, str]:
        return {z: t for z, t in self._lesen(KEY_TASTEN, {}).items() if isinstance(z, str) and isinstance(t, str) and t}

    def setze_tasten(self, tasten: dict[str, str]) -> None:
        self.e.set(KEY_TASTEN, json.dumps({z: t for z, t in tasten.items() if t}, ensure_ascii=False))


class _Speicher:
    def __init__(self):
        self.d: dict = {}

    def get(self, key, default=None):
        return self.d.get(key, default)

    def set(self, key, wert) -> None:
        self.d[key] = wert


class _TastenFenster(PanelFaehig, TastenDialog):
    """„Tastenkombination“ als Seite über dem Fenster „Symbol“."""
