"""Serienbrief: Briefe entstehen als Kopien des Dokuments, die über eine eigene Bearbeitungssitzung gefüllt werden; die Vorlage bleibt unverändert."""
from __future__ import annotations

import copy
import re

from lunivo_writer.core.editing import Bearbeitungssitzung
from lunivo_writer.core.editing.suche import position_zu_offset
from lunivo_writer.core.document.dokument import Dokument, Position
from lunivo_writer.editor.dokument.sendungen.konstanten import NAECHSTER


def _satz_einsetzen(s: Bearbeitungssitzung, satz: dict, von_bis: tuple[int, int] | None = None) -> None:
    """Felder und Regeln mit den Werten von ``satz`` füllen (``von_bis``: nur in diesem Bereich, Stellen im Rohtext)."""
    dok = s.dokument
    lo, hi = von_bis if von_bis else (0, 1 << 30)
    # Regeln zuerst: sie entscheiden anhand eines Feldes, welcher Text stehen bleibt
    regeln = [(f, f.anker) for f in s.bereiche(lambda f: "regel" in f, lambda f: f["regel"])]
    for fund, _a in reversed(regeln):
        von = position_zu_offset(dok, fund.anker)
        if not lo <= von < hi:
            continue
        a = s._absatz(fund.anker.absatz_id)
        regel = next((x.format["regel"] for x in a.inhalte if hasattr(x, "text") and x.format.get("regel")), "")
        feld, wert, dann, sonst = (regel.split("|") + ["", "", "", ""])[:4]
        text = dann if (satz.get(feld, "").strip() == wert.strip()) else sonst
        laenge = fund.kopf.versatz - fund.anker.versatz
        s.ersetzen(text, fund, format={})
        hi += len(text) - laenge
    for name, wert in satz.items():
        for fund in reversed(s.suche(r"\{\{\s*" + re.escape(name) + r"\s*\}\}", regex=True, gross_klein=True)):
            von = position_zu_offset(dok, fund.anker)
            if not lo <= von < hi:
                continue
            laenge = fund.kopf.versatz - fund.anker.versatz
            ende = s.ersetzen(str(wert), fund, format={})
            hi += len(str(wert)) - laenge


def brief_fuer(vorlage: Dokument, satz: dict | list[dict]) -> Dokument:
    """Ein Brief (Kopie der Vorlage). Steht „Nächster Datensatz“ im Text, gilt hinter jeder solchen Stelle der nächste Satz der Liste ``satz``."""
    saetze = satz if isinstance(satz, list) else [satz]
    d = copy.deepcopy(vorlage)
    s = Bearbeitungssitzung(d)
    stellen = [(position_zu_offset(d, f.anker), f) for f in s.suche(r"\{\{\s*" + re.escape(NAECHSTER) + r"\s*\}\}", regex=True, gross_klein=True)]
    anfang = [0] + [position_zu_offset(d, f.kopf) for _o, f in stellen]     # Stück k: hinter dem (k-1)-ten bis vor das k-te Feld „Nächster Datensatz“
    ende = [o for o, _f in stellen] + [1 << 30]
    for k in range(len(anfang) - 1, -1, -1):                 # von hinten: vordere Stellen verschieben sich nicht
        if k < len(saetze):
            _satz_einsetzen(s, saetze[k], (anfang[k], ende[k]))
        if k:                                                  # das Feld „Nächster Datensatz“ vor diesem Stück selbst verschwindet
            s.loeschen(stellen[k - 1][1])
    return d


def saetze_je_brief(vorlage: Dokument) -> int:
    """Wie viele Datensätze ein Brief verbraucht (1 + Zahl der Felder „Nächster Datensatz“)."""
    return 1 + len(re.findall(r"\{\{\s*" + re.escape(NAECHSTER) + r"\s*\}\}", vorlage.text()))


def gruppen(vorlage: Dokument, saetze: list[dict]) -> list[list[dict]]:
    n = saetze_je_brief(vorlage)
    return [saetze[i:i + n] for i in range(0, len(saetze), n)]


def serienbrief_erzeugen(quelle: Dokument, saetze: list[dict]) -> tuple[Dokument | None, int]:
    """Alle Briefe in EIN Dokument, durch Seitenumbrüche getrennt. → (Dokument, Zahl der Briefe)."""
    briefe = gruppen(quelle, saetze)
    if not briefe:
        return None, 0
    ziel = brief_fuer(quelle, briefe[0])
    s = Bearbeitungssitzung(ziel)
    for gruppe in briefe[1:]:
        brief = brief_fuer(quelle, gruppe)
        bloecke = copy.deepcopy([b for a in brief.abschnitte for b in a.bloecke])
        letzter = list(ziel.absaetze())[-1]
        ende = s.text_einfuegen("\n", Position(letzter.id, letzter.laenge), format={})
        s.ausschnitt_einfuegen(bloecke, ende)
        s.absatzformat_anwenden({"seitenumbruch_vor": True}, absatz_ids=[ende.absatz_id])
        # ressourcen und listen der Kopie stammen aus derselben Vorlage und sind schon im Ziel
    return ziel, len(briefe)
