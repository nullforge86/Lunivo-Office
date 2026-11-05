"""Gemeinsames Datenmodell eines Fundes der Schreibhilfe (Rechtschreibung, Grammatik, Stil, LanguageTool, KI).

``ProofingIssue`` ist der einzige Typ eines Fundes in der ganzen Schreibhilfe: Prüfer, Auflösung (``proofing/fund.py``), inkrementelle Prüfung,
Service, Seitenleiste und Editor-Wellenlinien arbeiten mit Attributen; ein Fund ist unveränderlich (``ersetzt``, ``verschoben`` liefern Kopien).
``von_dict`` / ``als_dict`` sind nur noch die Brücke zu Daten von außen (LanguageTool, gespeicherte Daten); unbekannte Schlüssel bleiben
in ``weitere`` erhalten.
Ohne Qt, ohne Logik der Prüfung.

**Verbindlicher Datenvertrag:** Jeder Fund, der in die Schreibhilfe (Seitenleiste, Editor) gelangt, läuft durch ``bereinigen`` (aufgerufen von
``proofing.fund.markieren``): Pflichtfelder, Typen, Wertebereiche und Textbereich werden geprüft, ungültige Funde werden verworfen und gezählt
(ohne Textinhalt zu protokollieren). Nach dieser Stelle dürfen nachgelagerte Teile von gültigen Werten ausgehen.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field, replace

_log = logging.getLogger("lunivo.schreibhilfe")

ARTEN = ("fehler", "tipp", "hinweis")      # Schweregrad, von schwer nach leicht
QUELLEN = ("eigen", "languagetool", "ki")  # Herkunft

_BEKANNT = {"von", "bis", "alt", "neu", "grund", "art", "wortEbene", "quelle", "konfidenz", "verdraengt", "stelle", "bestaetigtVon"}


class FundFehler(ValueError):
    """Ein Fund entspricht nicht dem Datenvertrag von ``ProofingIssue``."""


@dataclass(frozen=True)
class Verdraengt:
    """Ein Fund einer anderen Quelle, der von einem besseren überlagert wurde (nur zur Nachvollziehbarkeit)."""
    quelle: str | None = None
    neu: str | None = None
    grund: str | None = None
    konfidenz: float | None = None


def zeige_leer(s: str) -> str:
    """Leerzeichen und Zeilenumbrüche in Worten statt in Symbolen: „2 Leerzeichen“, „Zeilenumbruch“ (auch gut vorlesbar)."""
    def wort(m):
        t = m.group(0)
        if t.startswith("\n"):
            return "Zeilenumbruch" if len(t) == 1 else f"{len(t)} Zeilenumbrüche"
        return "1 Leerzeichen" if len(t) == 1 else f"{len(t)} Leerzeichen"
    ganz = not s.strip(" \n")
    return re.sub(r" +|\n+", lambda m: wort(m) if ganz else f"[{wort(m)}]", s)


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
    verdraengt: tuple[Verdraengt, ...] = ()    # von diesem Fund überlagerte Funde anderer Quellen
    stelle: str = ""                           # bei Hinweisen auf einen Satz: der ganze Satz
    bestaetigt_von: tuple[str, ...] = ()       # andere Quellen (QUELLEN), die denselben Vorschlag melden (Konsens, siehe fund.abstimmen)
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
        if not isinstance(self.bestaetigt_von, tuple) or any(q not in QUELLEN for q in self.bestaetigt_von):
            raise FundFehler("bestaetigt_von enthält unbekannte Quellen")
        return self

    @property
    def laenge(self) -> int:
        return self.bis - self.von

    @property
    def zeige_alt(self) -> str:
        return zeige_leer(self.alt)

    @property
    def zeige_neu(self) -> str:
        return zeige_leer(self.neu or "")

    @property
    def hat_vorschlag(self) -> bool:
        return bool(self.neu)

    def ersetzt(self, **felder) -> "ProofingIssue":
        """Eine Kopie mit geänderten Feldern (der Fund selbst ist unveränderlich)."""
        return replace(self, **felder)

    def verschoben(self, delta: int) -> "ProofingIssue":
        return replace(self, von=self.von + delta, bis=self.bis + delta)

    @property
    def stellenschluessel(self) -> tuple:
        """Sortierung nach Stelle: früher zuerst, bei gleichem Anfang der längere."""
        return (self.von, -(self.bis - self.von))

    @classmethod
    def von_dict(cls, f: dict) -> "ProofingIssue":
        return cls(
            von=f["von"], bis=f["bis"], alt=f.get("alt", ""), neu=f.get("neu"), grund=f.get("grund", ""),
            art=f.get("art", "fehler"), wort_ebene=bool(f.get("wortEbene", False)),
            quelle=f.get("quelle"), konfidenz=f.get("konfidenz"),
            verdraengt=tuple(v if isinstance(v, Verdraengt) else Verdraengt(**{k: v.get(k) for k in ("quelle", "neu", "grund", "konfidenz")})
                             for v in f.get("verdraengt", ())),
            stelle=f.get("stelle") or "",
            bestaetigt_von=tuple(q for q in (f.get("bestaetigtVon") or ()) if q in QUELLEN),
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
            d["verdraengt"] = [{"quelle": v.quelle, "neu": v.neu, "grund": v.grund, "konfidenz": v.konfidenz} for v in self.verdraengt]
        if self.stelle:
            d["stelle"] = self.stelle
        if self.bestaetigt_von:
            d["bestaetigtVon"] = list(self.bestaetigt_von)
        d.update(self.weitere)
        return d


def bereinigen(funde: list, text_laenge: int | None = None) -> list[ProofingIssue]:
    """Prüft jeden Fund gegen den Vertrag (``ProofingIssue`` oder Wörterbuch von außen, etwa aus LanguageTool); gültige kommen als
    ``ProofingIssue`` zurück, ungültige werden verworfen.

    Protokolliert nur die Anzahl und die Gründe, nie den Text."""
    gut, verworfen = [], {}
    for f in funde:
        try:
            if isinstance(f, dict):
                f = ProofingIssue.von_dict(f)
            if not isinstance(f, ProofingIssue):
                raise FundFehler("weder Fund noch Wörterbuch")
            gut.append(f.pruefen(text_laenge))
        except (FundFehler, KeyError, TypeError) as e:
            grund = str(e) if isinstance(e, FundFehler) else f"Pflichtfeld fehlt oder falscher Typ ({type(e).__name__})"
            verworfen[grund] = verworfen.get(grund, 0) + 1
    if verworfen:
        _log.warning("Ungültige Funde der Schreibhilfe verworfen: %s", "; ".join(f"{n}× {g}" for g, n in verworfen.items()))
    return gut
