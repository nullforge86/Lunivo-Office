"""Gemeinsames Datenmodell eines Fundes der Schreibhilfe (Rechtschreibung, Grammatik, Stil, LanguageTool, KI).

Die Schreibhilfe arbeitet bisher mit Wörterbüchern (``{'von', 'bis', 'alt', 'neu', 'grund', 'art', 'wortEbene', …}``).
``ProofingIssue`` ist die typisierte Fassung davon; ``von_dict`` / ``als_dict`` wandeln verlustfrei hin und her
(unbekannte Schlüssel bleiben in ``weitere`` erhalten), damit Prüfer einzeln umgestellt werden können.
Ohne Qt, ohne Logik der Prüfung.

**Verbindlicher Datenvertrag:** Jeder Fund, der in die Schreibhilfe (Seitenleiste, Editor) gelangt, läuft durch ``bereinigen`` (aufgerufen von
``proofing.fund.markieren``): Pflichtfelder, Typen, Wertebereiche und Textbereich werden geprüft, ungültige Funde werden verworfen und gezählt
(ohne Textinhalt zu protokollieren). Nach dieser Stelle dürfen nachgelagerte Teile von gültigen Werten ausgehen.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

_log = logging.getLogger("lunivo.schreibhilfe")

ARTEN = ("fehler", "tipp", "hinweis")      # Schweregrad, von schwer nach leicht
QUELLEN = ("eigen", "languagetool", "ki")  # Herkunft

_BEKANNT = {"von", "bis", "alt", "neu", "grund", "art", "wortEbene", "quelle", "konfidenz", "verdraengt"}


class FundFehler(ValueError):
    """Ein Fund entspricht nicht dem Datenvertrag von ``ProofingIssue``."""


@dataclass(frozen=True)
class ProofingIssue:
    von: int                                   # Textposition (Zeichen), Anfang
    bis: int                                   # Ende (exklusiv)
    alt: str                                   # ursprünglicher Text
    neu: str | None = None                     # Verbesserungsvorschlag
    grund: str = ""                            # Beschreibung
    art: str = "fehler"                        # Fehlerart / Schweregrad, siehe ARTEN
    wort_ebene: bool = False
    quelle: str | None = None                  # Herkunft, siehe QUELLEN; None = noch nicht markiert
    konfidenz: float | None = None
    verdraengt: tuple = ()                     # von diesem Fund überlagerte Funde anderer Quellen
    weitere: tuple = field(default_factory=tuple)  # unbekannte Schlüssel als (Name, Wert)-Paare

    def pruefen(self, text_laenge: int | None = None) -> "ProofingIssue":
        """Wirft ``FundFehler``, wenn der Fund nicht dem Vertrag entspricht. → self."""
        if not (isinstance(self.von, int) and isinstance(self.bis, int)) or isinstance(self.von, bool) or isinstance(self.bis, bool):
            raise FundFehler("von/bis sind keine ganzen Zahlen")
        if self.von < 0 or self.bis <= self.von:
            raise FundFehler("leerer oder verkehrter Textbereich")
        if text_laenge is not None and self.bis > text_laenge:
            raise FundFehler("Textbereich liegt außerhalb des Textes")
        if not isinstance(self.alt, str) or not isinstance(self.grund, str) or not (self.neu is None or isinstance(self.neu, str)):
            raise FundFehler("alt, neu oder grund haben den falschen Typ")
        if self.art not in ARTEN:
            raise FundFehler(f"unbekannte Art „{self.art}“")
        if self.quelle is not None and self.quelle not in QUELLEN:
            raise FundFehler(f"unbekannte Quelle „{self.quelle}“")
        if self.konfidenz is not None and not (isinstance(self.konfidenz, (int, float)) and 0.0 <= self.konfidenz <= 1.0):
            raise FundFehler("Konfidenz außerhalb von 0 bis 1")
        return self

    @property
    def laenge(self) -> int:
        return self.bis - self.von

    @classmethod
    def von_dict(cls, f: dict) -> "ProofingIssue":
        return cls(
            von=f["von"], bis=f["bis"], alt=f.get("alt", ""), neu=f.get("neu"), grund=f.get("grund", ""),
            art=f.get("art", "fehler"), wort_ebene=bool(f.get("wortEbene", False)),
            quelle=f.get("quelle"), konfidenz=f.get("konfidenz"),
            verdraengt=tuple(f.get("verdraengt", ())),
            weitere=tuple((k, v) for k, v in f.items() if k not in _BEKANNT))

    def als_dict(self) -> dict:
        """Wörterbuch wie bisher; Schlüssel ohne Wert (quelle, konfidenz, verdraengt) fehlen, wie bei den ursprünglichen Funden."""
        d = {"von": self.von, "bis": self.bis, "alt": self.alt, "neu": self.neu, "grund": self.grund,
             "art": self.art, "wortEbene": self.wort_ebene}
        if self.quelle is not None:
            d["quelle"] = self.quelle
        if self.konfidenz is not None:
            d["konfidenz"] = self.konfidenz
        if self.verdraengt:
            d["verdraengt"] = list(self.verdraengt)
        d.update(self.weitere)
        return d


def bereinigen(funde: list[dict], text_laenge: int | None = None) -> list[dict]:
    """Prüft jeden Fund gegen den Vertrag; gültige kommen als Wörterbuch (``als_dict``) zurück, ungültige werden verworfen.

    Protokolliert nur die Anzahl und die Gründe, nie den Text."""
    gut, verworfen = [], {}
    for f in funde:
        try:
            if not isinstance(f, dict):
                raise FundFehler("kein Wörterbuch")
            gut.append(ProofingIssue.von_dict(f).pruefen(text_laenge).als_dict())
        except (FundFehler, KeyError, TypeError) as e:
            grund = str(e) if isinstance(e, FundFehler) else f"Pflichtfeld fehlt oder falscher Typ ({type(e).__name__})"
            verworfen[grund] = verworfen.get(grund, 0) + 1
    if verworfen:
        _log.warning("Ungültige Funde der Schreibhilfe verworfen: %s", "; ".join(f"{n}× {g}" for g, n in verworfen.items()))
    return gut
