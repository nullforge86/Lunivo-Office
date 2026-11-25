"""Befehle der Funktion „Verweise“: Beschriftungen, Verzeichnisse, Textmarken, Querverweise, Index, Fuß-/Endnoten und Quellen.

Der Editor kommt über den ``EditorPort`` herein; die Fachlogik steht in ``editor/dokument`` (Programmkern). Nach außen gehen nur Grundtypen, einfache
Datenwörterbücher und die Datentypen aus ``typen.py``; Meldungen für die Statusleiste gehen als Ereignis an den ``Melder``."""
from __future__ import annotations

from core.funktionen.verweise.beschriftungen import beschriftung
from core.funktionen.verweise.querverweise import querverweis
from core.funktionen.verweise.quellen import quelle_tag, zitat
from core.funktionen.verweise.stichwoerter import stichwort
from core.funktionen.verweise.textmarken import textmarke
from core.funktionen.verweise.verzeichnisse import verzeichnis
from core.funktionen.verweise.stichwoerter.indexeintrag import Eintrag
from core.funktionen.verweise.quellen.literatur import eintrag as literatur_eintrag
from framework.datentypen.ereignisdaten import Art, Ereignis
from framework.funktionen.verweise import einstellungen as verweise_einstellungen
from framework.funktionen.verweise.typen import BeschriftungsStart, IndexEintrag, IndexStart
from framework.schnittstellen.dokument import EditorPort
from framework.schnittstellen.einstellungen import Einstellungen
from framework.steuerung.ereignissteuerung import Melder


class VerweiseBefehle:
    def __init__(self, editor: EditorPort, einstellungen: Einstellungen, melder: Melder):
        self._editor = editor
        self._einstellungen = einstellungen
        self._melder = melder

    def _melden(self, text: str, dauer_ms: int = 4000) -> None:
        self._melder.melden(Ereignis(Art.MELDUNG, text, {"dauer_ms": dauer_ms}))

    # ---- Beschriftung -------------------------------------------------------------------------------------------------------------
    def beschriftung_vorbereiten(self) -> BeschriftungsStart:
        c = self._editor.textCursor()
        tabelle = c.currentTable() is not None
        objekt = tabelle or (c.hasSelection() and "￼" in c.selectedText())
        return BeschriftungsStart(verweise_einstellungen.eigene_beschriftungen(self._einstellungen), bool(objekt), "Tabelle" if tabelle else "Abbildung")

    def naechste_nummer(self, label: str, zahl: str) -> str:
        return beschriftung.naechste_nummer(self._editor, label, zahl)

    def eigene_beschriftungen_speichern(self, eigene: list[str]) -> None:
        verweise_einstellungen.eigene_beschriftungen_setzen(self._einstellungen, eigene)

    def beschriftung_einfuegen(self, label: str, oben: bool, nach: str | None, ohne: bool, zahl: str) -> None:
        beschriftung.beschriftung_einfuegen(self._editor, label, "", oben, nach=nach, ohne_bezeichnung=ohne, zahl=zahl)

    # ---- Verzeichnisse ------------------------------------------------------------------------------------------------------------
    def verzeichnis_einfuegen(self, art: str) -> int:
        """Fügt ein Verzeichnis ein (``abb``, ``index``, ``lit``, ``toc``); gibt die Zahl der Einträge zurück (0: es gab nichts aufzunehmen)."""
        return verzeichnis.verzeichnis_einfuegen(self._editor, art)

    def verzeichnis_aktualisieren(self, art: str, fehlt_meldung: str) -> None:
        if not verzeichnis.vorhanden(self._editor.sitzung.dokument, art):
            self._melden(fehlt_meldung)
            return
        verzeichnis.verzeichnis_aktualisieren(self._editor, art)

    # ---- Textmarken ---------------------------------------------------------------------------------------------------------------
    def lesezeichen_namen(self, versteckte: bool = False) -> tuple[str, ...]:
        return tuple(m["name"] for m in textmarke.lesezeichen_liste(self._editor, versteckte=versteckte))

    @staticmethod
    def lesezeichen_name_gueltig(name: str) -> bool:
        return textmarke.lesezeichen_name_gueltig(name)

    def lesezeichen_setzen(self, name: str) -> bool:
        return textmarke.lesezeichen_setzen(self._editor, name)

    def lesezeichen_loeschen(self, name: str) -> None:
        textmarke.lesezeichen_loeschen(self._editor, name)

    def lesezeichen_gehe(self, name: str) -> bool:
        return textmarke.lesezeichen_gehe(self._editor, name)

    # ---- Querverweis --------------------------------------------------------------------------------------------------------------
    def querverweis_ziele(self) -> list[dict]:
        return querverweis.querverweis_ziele(self._editor)

    def querverweis_einfuegen(self, ziel: dict, wie: str, link: bool, oben_unten: bool) -> None:
        querverweis.querverweis_einfuegen(self._editor, ziel, wie, link=link, oben_unten=oben_unten)

    # ---- Index --------------------------------------------------------------------------------------------------------------------
    def index_vorbereiten(self) -> IndexStart:
        c = self._editor.textCursor()
        return IndexStart(c.selectedText().strip() if c.hasSelection() else "", self.lesezeichen_namen(), bool(c.hasSelection()))

    def index_markieren(self, eintrag: IndexEintrag, alle: bool) -> int:
        n = stichwort.index_eintragen(self._editor, Eintrag(**{f: getattr(eintrag, f) for f in ("haupt", "unter", "lesung", "lesung_unter", "siehe", "marke", "fett", "kursiv")}), alle)
        self._melden(f"{n} Indexeintrag markiert." if n == 1 else f"{n} Indexeinträge markiert." if n else "Bitte Text markieren oder in ein Wort klicken.")
        return n

    # ---- Gliederung und Noten -------------------------------------------------------------------------------------------------------
    def gliederungsebene(self) -> int:
        return int(self._editor.absatzformat().get("gliederungsebene") or 0)

    def ebene_setzen(self, ebene: int) -> None:
        self._editor.apply_style(f"Überschrift {ebene}" if ebene else "Standard")

    def note_springen(self, delta: int, art: str, titel: str) -> None:
        if self._editor.note_springen(delta, art) is None:
            self._melden(f"Im Dokument gibt es keine {titel}.", 3000)

    # ---- Quellen und Zitate -----------------------------------------------------------------------------------------------------------
    def quellen(self) -> list[dict]:
        return [dict(q) for q in self._editor.quellen]

    def quelle_beschreibung(self, quelle: dict) -> str:
        return literatur_eintrag(quelle, self._editor.zitierweise)

    def zitierweise(self) -> str:
        return self._editor.zitierweise

    def zitierweise_setzen(self, name: str) -> None:
        self._editor.zitierweise = name
        self._editor.document().setModified(True)

    def quelle_neu(self, quelle: dict) -> None:
        quelle = dict(quelle)
        quelle["tag"] = quelle_tag.quelle_tag(self._editor.quellen, quelle)
        self._editor.quelle_hinzufuegen(quelle)

    def quelle_aendern(self, tag: str, werte: dict) -> None:
        q = next((q for q in self._editor.quellen if q["tag"] == tag), None)
        if q is not None:
            q.update(werte)
            self._editor.document().setModified(True)

    def quelle_entfernen(self, tag: str) -> None:
        self._editor.quelle_entfernen(tag)

    def zitat_einfuegen(self, tag: str) -> None:
        q = next((q for q in self._editor.quellen if q["tag"] == tag), None)
        if q is not None:
            zitat.zitat_einfuegen(self._editor, q)
