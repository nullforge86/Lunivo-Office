"""Befehle der Funktion „Verweise“: Beschriftungen, Verzeichnisse, Textmarken, Querverweise, Index, Fuß-/Endnoten, Quellen und Zitate.

Arbeitet mit der Kennung des Dokuments, nie mit dem Editor der Oberfläche. Lesen, Ändern und Springen laufen über den Änderungsrahmen
(``framework.befehle.aenderung``); die Fachlogik liegt im Kern und bekommt einen ``Kontext`` der Sitzung."""
from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from core.bearbeitung import Kontext
from core.verzeichnisse.abbildungsverzeichnis import beschriftung
from core.referenzen.querverweise import querverweis
from core.referenzen.literaturverzeichnis import quelle_tag, zitat
from core.referenzen.querverweise import stichwort
from core.referenzen.querverweise import textmarke
from core.verzeichnisse.inhaltsverzeichnis import verzeichnis
from core.referenzen.querverweise.indexeintrag import Eintrag
from core.referenzen.literaturverzeichnis.literatur import eintrag as literatur_eintrag
from framework.schnittstellen.datentypen.ereignisdaten import Art, Ereignis
from framework.befehle.aenderung import ausfuehren, bewegen, lesen
from framework.befehle.verweise import einstellungen as verweise_einstellungen
from framework.befehle.verweise.typen import BeschriftungsStart, IndexEintrag, IndexStart
from framework.schnittstellen.einstellungen import Einstellungen
from framework.ereignisse.ereignissteuerung import Melder

_OBJEKT = "\ufffc"                                             # Platzhalterzeichen eines Objekts im Rohtext


def _frei(d) -> Mapping[str, str | int]:
    return MappingProxyType(dict(d))


class VerweiseBefehle:
    def __init__(self, kennung: int, einstellungen: Einstellungen | None = None, melder: Melder | None = None):
        self._kennung = kennung
        self._einstellungen = einstellungen
        self._melder = melder

    def _melden(self, text: str, dauer_ms: int = 4000) -> None:
        if self._melder is not None:
            self._melder.melden(Ereignis(Art.MELDUNG, text, {"dauer_ms": dauer_ms}))

    def _lesen(self, arbeit):
        return lesen(self._kennung, lambda s: arbeit(Kontext(s)))

    def _aendern(self, arbeit):
        return ausfuehren(self._kennung, lambda s: arbeit(Kontext(s)))

    def _bewegen(self, arbeit):
        return bewegen(self._kennung, lambda s: arbeit(Kontext(s)))

    # ---- Beschriftung -------------------------------------------------------------------------------------------------------------
    def beschriftung_vorbereiten(self) -> BeschriftungsStart:
        tabelle, auswahl = self._lesen(lambda k: (k.tabelle_an_marke() is not None, k.auswahl_text())) or (False, "")
        objekt = tabelle or _OBJEKT in auswahl
        eigene = verweise_einstellungen.eigene_beschriftungen(self._einstellungen) if self._einstellungen is not None else []
        return BeschriftungsStart(eigene, bool(objekt), "Tabelle" if tabelle else "Abbildung")

    def naechste_nummer(self, label: str, zahl: str) -> str:
        return self._lesen(lambda k: beschriftung.naechste_nummer(k, label, zahl)) or ""

    def eigene_beschriftungen_speichern(self, eigene: list[str]) -> None:
        if self._einstellungen is not None:
            verweise_einstellungen.eigene_beschriftungen_setzen(self._einstellungen, eigene)

    def beschriftung_einfuegen(self, label: str, oben: bool, nach: str | None, ohne: bool, zahl: str) -> None:
        self._aendern(lambda k: beschriftung.beschriftung_einfuegen(k, label, "", oben, nach=nach, ohne_bezeichnung=ohne, zahl=zahl))

    def beschriftungen_liste(self) -> tuple[Mapping[str, str | int], ...]:
        return tuple(_frei(x) for x in self._lesen(beschriftung.beschriftungen_liste) or ())

    # ---- Verzeichnisse ------------------------------------------------------------------------------------------------------------
    def verzeichnis_einfuegen(self, art: str, opt: Mapping[str, str | int | bool] | None = None) -> int:
        """Fügt ein Verzeichnis ein (``abb``, ``index``, ``lit``, ``toc``); gibt die Zahl der Einträge zurück (0: es gab nichts aufzunehmen)."""
        return self._aendern(lambda k: verzeichnis.verzeichnis_einfuegen(k, art, dict(opt) if opt is not None else None)) or 0

    def verzeichnis_aktualisieren(self, art: str, fehlt_meldung: str) -> None:
        if not self._lesen(lambda k: verzeichnis.vorhanden(k.sitzung.dokument, art)):
            self._melden(fehlt_meldung)
            return
        self._aendern(lambda k: verzeichnis.verzeichnis_aktualisieren(k, art))

    def verzeichnis_alle_aktualisieren(self) -> int:
        """Alle Verzeichnisse des Dokuments neu schreiben; → Zahl der Zeilen."""
        return self._aendern(lambda k: verzeichnis.verzeichnis_aktualisieren(k)) or 0

    # ---- Textmarken ---------------------------------------------------------------------------------------------------------------
    def textmarken_liste(self, versteckte: bool = True) -> tuple[Mapping[str, str | int], ...]:
        return tuple(_frei(x) for x in self._lesen(lambda k: textmarke.lesezeichen_liste(k, versteckte=versteckte)) or ())

    def lesezeichen_namen(self, versteckte: bool = False) -> tuple[str, ...]:
        return tuple(m["name"] for m in self.textmarken_liste(versteckte))

    @staticmethod
    def lesezeichen_name_gueltig(name: str) -> bool:
        return textmarke.lesezeichen_name_gueltig(name)

    def lesezeichen_setzen(self, name: str) -> bool:
        return bool(self._aendern(lambda k: textmarke.lesezeichen_setzen(k, name)))

    def lesezeichen_loeschen(self, name: str) -> None:
        self._aendern(lambda k: textmarke.lesezeichen_loeschen(k, name))

    def lesezeichen_gehe(self, name: str) -> bool:
        return bool(self._bewegen(lambda k: textmarke.lesezeichen_gehe(k, name)))

    # ---- Querverweis --------------------------------------------------------------------------------------------------------------
    def querverweis_ziele(self) -> list[dict]:
        return self._lesen(querverweis.querverweis_ziele) or []

    def marke_sichern(self, ziel: Mapping[str, str | int]) -> str:
        """Name der Textmarke am Ziel (legt bei Bedarf eine verborgene an)."""
        return self._aendern(lambda k: querverweis.marke_sichern(k, dict(ziel))) or ""

    def querverweis_einfuegen(self, ziel: dict, wie: str, link: bool, oben_unten: bool) -> None:
        self._aendern(lambda k: querverweis.querverweis_einfuegen(k, ziel, wie, link=link, oben_unten=oben_unten))

    # ---- Index --------------------------------------------------------------------------------------------------------------------
    def index_vorbereiten(self) -> IndexStart:
        text = (self._lesen(lambda k: k.auswahl_text()) or "").strip()
        return IndexStart(text, self.lesezeichen_namen(), bool(text))

    def index_markieren(self, eintrag: IndexEintrag, alle: bool) -> int:
        e = Eintrag(**{f: getattr(eintrag, f) for f in ("haupt", "unter", "lesung", "lesung_unter", "siehe", "marke", "fett", "kursiv")})
        n = self._aendern(lambda k: stichwort.index_eintragen(k, e, alle)) or 0
        self._melden(f"{n} Indexeintrag markiert." if n == 1 else f"{n} Indexeinträge markiert." if n else "Bitte Text markieren oder in ein Wort klicken.")
        return n

    # ---- Gliederung und Noten -------------------------------------------------------------------------------------------------------
    def gliederungsebene(self) -> int:
        return int(self._lesen(lambda k: k.absatzformat().get("gliederungsebene") or 0) or 0)

    def note_springen(self, delta: int, art: str, titel: str) -> None:
        ziel = self._bewegen(lambda k: k.springe([n for n in k.noten_stellen() if art is None or n["art"] == art], delta))
        if ziel is None:
            self._melden(f"Im Dokument gibt es keine {titel}.", 3000)

    # ---- Quellen und Zitate -----------------------------------------------------------------------------------------------------------
    def quellen(self) -> list[dict]:
        return self._lesen(lambda k: k.quellen) or []

    def quelle_beschreibung(self, quelle: dict) -> str:
        return literatur_eintrag(quelle, self.zitierweise())

    def zitierweise(self) -> str:
        return self._lesen(lambda k: k.zitierweise) or "APA"

    def zitierweise_setzen(self, name: str) -> None:
        self._aendern(lambda k: k.sitzung.eigenschaft_setzen("zitierweise", name))

    def quelle_neu(self, quelle: dict) -> None:
        q = dict(quelle)
        q["tag"] = quelle_tag.quelle_tag(self.quellen(), q)
        self._aendern(lambda k: k.sitzung.quelle_setzen(q))

    def quelle_aendern(self, tag: str, werte: dict) -> None:
        q = next((q for q in self.quellen() if q["tag"] == tag), None)
        if q is not None:
            self._aendern(lambda k: k.sitzung.quelle_setzen({**q, **werte}))

    def quelle_entfernen(self, tag: str) -> None:
        self._aendern(lambda k: k.sitzung.quelle_loeschen(tag))

    def zitat_einfuegen(self, tag: str) -> None:
        q = next((q for q in self.quellen() if q["tag"] == tag), None)
        if q is not None:
            self._aendern(lambda k: zitat.zitat_einfuegen(k, q))
