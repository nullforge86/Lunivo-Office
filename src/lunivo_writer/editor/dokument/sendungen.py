"""Sendungen: Umschlag, Etiketten, Seriendruck (mit Feldern, Adressblock, Regeln), Formularfelder. Auf dem Dokumentmodell, ohne Qt-Dokument.

Seriendruckfelder stehen als ``{{Name}}`` mit farbigem Hintergrund (``marker``) im Text, Regeln als Text mit dem Zeichenformat ``regel`` („Feld|Wert|dann|sonst“).
Briefe entstehen als Kopien des Dokuments (``Dokument``), die über eine eigene Bearbeitungssitzung gefüllt werden; die Vorlage bleibt unverändert.
"""
from __future__ import annotations

import copy
import re

from lunivo_writer.core.document.dokument import Auswahl, Dokument, Position, neues_dokument
from lunivo_writer.core.editing import Bearbeitungssitzung
from lunivo_writer.core.editing.suche import position_zu_offset
from lunivo_writer.core.geometry import mm_to_px
from lunivo_writer.modelle.seite import PageSettings

FELD_FARBE = "#d0ebff"
REGEL_FARBE = "#ffe8cc"
NAECHSTER = "Nächster Datensatz"

UMSCHLAEGE = {"DIN lang (220 × 110 mm)": (220, 110), "C6 (162 × 114 mm)": (162, 114), "C5 (229 × 162 mm)": (229, 162),
              "C4 (324 × 229 mm)": (324, 229)}
ETIKETTEN = {"70 × 37 mm — 24 Stück (3 × 8)": (3, 8, 70, 37), "70 × 42,3 mm — 21 Stück (3 × 7)": (3, 7, 70, 42.3),
             "70 × 50,8 mm — 15 Stück (3 × 5)": (3, 5, 70, 50.8), "105 × 42,3 mm — 14 Stück (2 × 7)": (2, 7, 105, 42.3),
             "105 × 148 mm — 4 Stück (2 × 2)": (2, 2, 105, 148)}


def _einzeilig(text: str) -> str:
    return " ".join(z.strip() for z in text.splitlines() if z.strip())


# ---- Umschlag und Etiketten -----------------------------------------------------------------------------------
def umschlag_aufbauen(ed, format_name: str, absender: str, empfaenger: str) -> PageSettings:
    """Ersetzt den Inhalt des Editors durch einen Umschlag (Absender klein oben links, Empfänger rechts darunter); → die Seiteneinrichtung."""
    b, h = UMSCHLAEGE[format_name]
    pg = PageSettings(width_mm=b, height_mm=h, margin_top_mm=12, margin_bottom_mm=10, margin_left_mm=15, margin_right_mm=12)
    neu = neues_dokument()
    s = Bearbeitungssitzung(neu)
    a = next(neu.absaetze())
    s.text_einfuegen(_einzeilig(absender) + "\n" + _einzeilig(empfaenger), Position(a.id, 0), format={})
    erster, zweiter = list(neu.absaetze())[:2]
    s.zeichenformat_anwenden({"groesse_pt": 8.0}, Auswahl(Position(erster.id, 0), Position(erster.id, erster.laenge)))
    s.zeichenformat_anwenden({"groesse_pt": 12.0}, Auswahl(Position(zweiter.id, 0), Position(zweiter.id, zweiter.laenge)))
    s.absatzformat_anwenden({"abstand_vor": mm_to_px(max(10, h * 0.2)), "einzug_links": mm_to_px(b * 0.42)}, absatz_ids=[zweiter.id])
    neu.abschnitte[0].seite = pg
    ed.ansicht._aendern(lambda sitz: sitz.dokument_ersetzen(neu))
    return pg


def etiketten_aufbauen(ed, bogen: str, text: str, gleich: bool) -> PageSettings:
    """Ersetzt den Inhalt des Editors durch einen Etikettenbogen (Tabelle ohne Rahmen, je Etikett eine Zelle); → die Seiteneinrichtung."""
    sp, ze, b, h = ETIKETTEN[bogen]
    pg = PageSettings(margin_top_mm=8, margin_bottom_mm=8, margin_left_mm=5, margin_right_mm=5)
    zeilen = [z.strip() for z in text.splitlines() if z.strip()]
    neu = neues_dokument()
    s = Bearbeitungssitzung(neu)
    tid = s.tabelle_einfuegen(ze, sp, format={"zellpolster": mm_to_px(2)}, spaltenbreiten=[mm_to_px(b)] * sp)
    s.zeilenhoehen_setzen(tid, [mm_to_px(h)] * ze)
    n = 0
    for r in range(ze):
        for k in range(sp):
            inhalt = " ".join(zeilen) if gleich else (zeilen[n] if n < len(zeilen) else "")
            if inhalt:
                s.text_einfuegen(inhalt, s.zelle_anfang(tid, r, k), format={"groesse_pt": 10.0})
            n += 1
    neu.abschnitte[0].seite = pg
    ed.ansicht._aendern(lambda sitz: sitz.dokument_ersetzen(neu))
    return pg


# ---- Serienbrief -------------------------------------------------------------------------------------------------------------
def tabelle_lesen(roh: str):
    zeilen = [z for z in re.split(r"\r?\n", roh) if z.strip()]
    if len(zeilen) < 2:
        return None
    tr = "\t" if "\t" in zeilen[0] else (";" if ";" in zeilen[0] else ",")
    spalten = [s.strip() for s in zeilen[0].split(tr)]
    saetze = []
    for z in zeilen[1:]:
        w = [x.strip() for x in z.split(tr)]
        saetze.append({n: (w[i] if i < len(w) else "") for i, n in enumerate(spalten)})
    return spalten, saetze


FELD = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")


def felder_im_text(dok: Dokument) -> list[str]:
    return sorted(set(m.group(1) for m in FELD.finditer(dok.text())))


def feld_einfuegen(ed, name: str) -> None:
    """Fügt ``{{name}}`` mit Feldfarbe ein; dahinter geht es ohne Feldfarbe weiter."""
    def f(s):
        with s.gruppe("Seriendruckfeld"):
            s.text_einfuegen("{{" + name + "}}", format={"marker": FELD_FARBE})
            s.tippformat = {}
    ed.ansicht._aendern(f)


def adressblock_einfuegen(ed, was: str) -> None:
    def f(s):
        with s.gruppe("Adressblock"):
            def feld(n):
                s.text_einfuegen("{{" + n + "}}", format={"marker": FELD_FARBE})

            def text(t):
                s.text_einfuegen(t, format={})
            if was in ("adresse", "beides"):
                feld("Name"); text(" "); feld("Straße"); text(" "); feld("PLZ"); text(" "); feld("Ort")
            if was == "beides":
                text("\n\n")
            if was in ("gruss", "beides"):
                text("Sehr geehrte"); feld("Anrede"); text(" "); feld("Name"); text(",")
    ed.ansicht._aendern(f)


def regel_einfuegen(ed, feld: str, wert: str, dann: str, sonst: str) -> None:
    regel = "|".join(x.replace("|", "/") for x in (feld, wert, dann, sonst))
    ed.ansicht._aendern(lambda s: s.text_einfuegen(dann, format={"marker": REGEL_FARBE, "regel": regel}))


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


# ---- Datenquelle des Seriendrucks -------------------------------------------------------------------------------------
def quelle_lesen(pfad: str):
    """Empfängerliste aus einer Textdatei (CSV mit ; oder , oder Tabulator; erste Zeile = Spaltennamen). → (Spalten, Sätze) oder None."""
    for enc in ("utf-8-sig", "cp1252"):
        try:
            with open(pfad, encoding=enc) as fh:
                return tabelle_lesen(fh.read())
        except UnicodeDecodeError:
            continue
    return None


def zugeordnet(satz: dict, zuordnung: dict) -> dict:
    """Satz mit den Namen der Felder im Text: ``zuordnung`` {Feld im Text: Spalte der Quelle}; ohne Eintrag gilt der gleiche Name."""
    aus = dict(satz)
    for feld, spalte in zuordnung.items():
        if spalte in satz:
            aus[feld] = satz[spalte]
    return aus


def felder_hervorheben(ed, an: bool) -> None:
    """Hintergrund der Felder {{…}} an oder aus (ein Schritt)."""
    def f(s):
        with s.gruppe("Seriendruckfelder hervorheben"):
            for fund in s.suche(r"\{\{\s*[^{}]+?\s*\}\}", regex=True, gross_klein=True):
                s.zeichenformat_anwenden({"marker": FELD_FARBE if an else None}, fund)
    ed.ansicht._aendern(f)


def naechster_einfuegen(ed) -> None:
    """Feld „Nächster Datensatz“: dahinter füllt der nächste Satz die Felder (z. B. mehrere Etiketten auf einem Blatt)."""
    feld_einfuegen(ed, NAECHSTER)


# ---- Formular ------------------------------------------------------------------------------------------------------------------
KASTEN_LEER, KASTEN_VOLL = "☐", "☒"


def form_textfeld(ed, text: str = "Text eingeben") -> None:
    ed.ansicht._aendern(lambda s: s.text_einfuegen(f"[ {text} ]", format={"marker": "#f1f3f5", "unterstrichen": True, "unter_art": "gepunktet"}))


def form_kasten(ed, beschriftung: str = "Auswahl") -> None:
    def f(s):
        with s.gruppe("Kontrollkästchen"):
            s.text_einfuegen(KASTEN_LEER, format={"groesse_pt": 14.0})
            s.text_einfuegen(" " + beschriftung, format={})
    ed.ansicht._aendern(f)


def form_knopf(ed, aufschrift: str) -> None:
    ed.ansicht._aendern(lambda s: s.text_einfuegen(f"  {aufschrift or 'Schaltfläche'}  ", format={"marker": "#dee2e6", "fett": True}))


def kasten_umschalten(ed, pos: int) -> bool:
    """Klick auf ein Kontrollkästchen ☐/☒ wechselt den Zustand."""
    from lunivo_writer.core.editing.suche import offset_zu_position
    dok = ed.sitzung.dokument
    for p in (pos, pos - 1):
        if p < 0:
            continue
        von, bis = offset_zu_position(dok, p), offset_zu_position(dok, p + 1)
        if von.absatz_id != bis.absatz_id:
            continue
        auswahl = Auswahl(von, bis)
        t = ed.sitzung.text(auswahl)
        if t in (KASTEN_LEER, KASTEN_VOLL):
            return ed.ansicht._aendern(lambda s: s.ersetzen(KASTEN_VOLL if t == KASTEN_LEER else KASTEN_LEER, auswahl))
    return False
