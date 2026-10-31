"""Gemeinsames Datenmodell eines Fundes der Schreibhilfe (Rechtschreibung, Grammatik, Stil, LanguageTool, KI).

Die Schreibhilfe arbeitet bisher mit Wörterbüchern (``{'von', 'bis', 'alt', 'neu', 'grund', 'art', 'wortEbene', …}``).
``ProofingIssue`` ist die typisierte Fassung davon; ``von_dict`` / ``als_dict`` wandeln verlustfrei hin und her
(unbekannte Schlüssel bleiben in ``weitere`` erhalten), damit Prüfer einzeln umgestellt werden können.
Ohne Qt, ohne Logik der Prüfung.
"""
from __future__ import annotations

from dataclasses import dataclass, field

ARTEN = ("fehler", "tipp", "hinweis")      # Schweregrad, von schwer nach leicht
QUELLEN = ("eigen", "languagetool", "ki")  # Herkunft

_BEKANNT = {"von", "bis", "alt", "neu", "grund", "art", "wortEbene", "quelle", "konfidenz", "verdraengt"}


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
