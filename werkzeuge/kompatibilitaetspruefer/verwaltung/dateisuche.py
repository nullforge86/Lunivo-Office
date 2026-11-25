"""Dateien einlesen, Formate bewerten und Referenzvorschläge finden. Es werden nur Dateien gelesen/aufgelistet, nie verändert."""
from __future__ import annotations

import os

BILDENDUNGEN = (".png", ".jpg", ".jpeg", ".bmp", ".webp")


def lesbare_endungen() -> set[str]:
    """Alle Endungen, die Lunivo laut ``dienste.formate`` öffnen kann."""
    from framework.dokumentverwaltung.dateizugriff import formate
    return set(formate.lesbar())


def speicherbare_endungen() -> list[str]:
    from framework.dokumentverwaltung.dateizugriff import formate
    return formate.speicherbar()


def format_info(endung: str):
    from framework.dokumentverwaltung.dateizugriff import formate
    return formate.finde(endung)


def format_zustand(endung: str) -> str:
    """``unterstuetzt`` · ``nur_referenz`` (PDF: wird nur als Referenz/Ausgabe benutzt) · ``nicht_unterstuetzt``."""
    endung = endung.lower()
    if endung in lesbare_endungen():
        return "unterstuetzt"
    if endung == ".pdf":
        return "nur_referenz"
    return "nicht_unterstuetzt"


def ordner_lesen(ordner: str, unterordner: bool, nur_unterstuetzt: bool = True) -> list[str]:
    ordner = os.path.expanduser(ordner)
    lesbar = lesbare_endungen()
    treffer: list[str] = []
    if unterordner:
        for wurzel, dirs, namen in os.walk(ordner, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not d.startswith("."))
            for n in sorted(namen):
                if n.startswith(".~lock") or n.startswith("~$"):                    # Sperrdateien von Office-Programmen
                    continue
                if not nur_unterstuetzt or os.path.splitext(n)[1].lower() in lesbar:
                    treffer.append(os.path.join(wurzel, n))
    else:
        try:
            for n in sorted(os.listdir(ordner)):
                p = os.path.join(ordner, n)
                if os.path.isfile(p) and not n.startswith(".~lock") and not n.startswith("~$") and (not nur_unterstuetzt or os.path.splitext(n)[1].lower() in lesbar):
                    treffer.append(p)
        except OSError:
            pass
    return treffer


def referenzvorschlaege(datei: str, referenzordner: str, index: dict | None = None) -> dict:
    """Findet Referenzkandidaten mit **identischem Namensstamm** (neben der Datei und im Referenzordner). Das ist nur ein Vorschlag:
    angewendet wird er erst, wenn der Benutzer ihn bestätigt. Mehr als ein Kandidat → ``mehrdeutig``."""
    stamm = os.path.splitext(os.path.basename(datei))[0]
    pdfs: set[str] = set()
    bilder: set[str] = set()
    suchorte = [os.path.dirname(datei)]
    if referenzordner:
        suchorte.append(os.path.expanduser(referenzordner))
    for ort in suchorte:
        if index is not None and ort in index:
            namen = index[ort]
        else:
            namen = _index_ordner(ort)
            if index is not None:
                index[ort] = namen
        for pfad in namen.get(stamm, []):
            (pdfs if pfad.lower().endswith(".pdf") else bilder).add(pfad)
    kandidaten = sorted(pdfs) + sorted(bilder)
    zustand = "fehlt" if not kandidaten else "vorschlag" if len(kandidaten) == 1 else "mehrdeutig"
    return {"zustand": zustand, "pdf": sorted(pdfs), "bilder": sorted(bilder), "kandidaten": kandidaten}


_REFERENZ_WOERTER = ("pdf", "referenz", "reference")


def _pdfs_unter(ort: str, tiefe: int = 4) -> list[str]:
    grund = ort.rstrip(os.sep).count(os.sep)
    aus: list[str] = []
    for wurzel, dirs, namen in os.walk(ort):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        if wurzel.count(os.sep) - grund >= tiefe:
            dirs[:] = []
        aus += [os.path.join(wurzel, n) for n in sorted(namen) if n.lower().endswith(".pdf")]
    return aus


def ordner_pdfs(ordner: str) -> list[str]:
    """Alle PDFs unter dem gewählten Ordner (bis Tiefe 4): Liegen Dokumente und PDFs in verschiedenen Unterordnern desselben Ordners, werden sie so gefunden."""
    ordner = os.path.abspath(os.path.expanduser(ordner))
    return _pdfs_unter(ordner) if os.path.isdir(ordner) else []


def nachbar_pdfs(ordner: str) -> list[str]:
    """PDFs aus Nachbarordnern des gewählten Ordners, deren Name auf Referenzen hindeutet (enthält „pdf“, „referenz“ oder „reference“) —
    typisch: ``dateien/`` mit den Dokumenten und ``pdf/`` mit den Referenz-PDFs im selben Elternordner. Andere Nachbarordner werden nicht durchsucht."""
    ordner = os.path.abspath(os.path.expanduser(ordner))
    eltern = os.path.dirname(ordner)
    try:
        nachbarn = sorted(os.listdir(eltern))
    except OSError:
        return []
    aus: list[str] = []
    for n in nachbarn:
        p = os.path.join(eltern, n)
        if p == ordner or n.startswith(".") or not os.path.isdir(p) or not any(w in n.lower() for w in _REFERENZ_WOERTER):
            continue
        aus += _pdfs_unter(p)
    return aus


def _index_ordner(ort: str) -> dict:
    """Name ohne Endung → Pfade (PDFs und Ordner mit Seitenbildern), rekursiv bis Tiefe 4."""
    aus: dict[str, list[str]] = {}
    grund = ort.rstrip(os.sep).count(os.sep)
    for wurzel, dirs, namen in os.walk(ort):
        if wurzel.count(os.sep) - grund >= 4:
            dirs[:] = []
        for n in namen:
            if n.lower().endswith(".pdf"):
                aus.setdefault(os.path.splitext(n)[0], []).append(os.path.join(wurzel, n))
        for d in dirs:
            p = os.path.join(wurzel, d)
            try:
                if any(f.lower().endswith(BILDENDUNGEN) for f in os.listdir(p)):
                    aus.setdefault(d, []).append(p)
            except OSError:
                pass
    return aus


def referenzzustand(datei: str, ref: dict | None, vorschlag: dict | None) -> str:
    """Anzeige: ``zugeordnet`` · ``unvollstaendig`` (Zuordnung ohne PDF/Bilder, nur erwartete Werte) · ``vorschlag`` · ``mehrdeutig`` · ``fehlt`` ·
    ``defekt`` (verknüpfte Datei existiert nicht mehr)."""
    if ref:
        if (ref.get("pdf") and not os.path.isfile(ref["pdf"])) or (ref.get("bilder") and not os.path.isdir(ref["bilder"])):
            return "defekt"
        if ref.get("pdf") or ref.get("bilder"):
            return "zugeordnet"
        if ref.get("erwartet") or ref.get("seiten_erwartet"):
            return "unvollstaendig"
    if vorschlag:
        return vorschlag["zustand"]
    return "fehlt"


def bilddateien(ordner: str) -> list[str]:
    try:
        return [os.path.join(ordner, n) for n in sorted(os.listdir(ordner), key=_natuerlich) if n.lower().endswith(BILDENDUNGEN)]
    except OSError:
        return []


def _natuerlich(s: str):
    import re
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def automatisch_zuordnen(dateien: list[dict], referenzordner: str, zusatz_pdfs: list[str] | None = None) -> dict:
    """Ordnet Referenzen zu, soweit das **sicher** ist: genau ein Kandidat mit identischem Namensstamm (neben der Datei, im Referenzordner oder unter den ausdrücklich hinzugefügten PDFs),
    und dieser Kandidat gehört zu keiner anderen Testdatei. Alles andere wird nicht zugeordnet, sondern als ``mehrdeutig`` zur Bestätigung geliefert.
    → ``{"eindeutig": [(datei_id, pfad)], "mehrdeutig": [(datei_id, [kandidaten])], "fehlt": [datei_id]}``"""
    index: dict = {}
    extra: dict[str, list[str]] = {}
    for p in zusatz_pdfs or []:
        extra.setdefault(os.path.splitext(os.path.basename(p))[0], []).append(p)
    kandidaten: dict[int, list[str]] = {}
    for d in dateien:
        v = referenzvorschlaege(d["pfad"], referenzordner, index)["kandidaten"]
        stamm = os.path.splitext(d["name"])[0]
        kandidaten[d["id"]] = sorted(set(v) | set(extra.get(stamm, [])))
    nutzung: dict[str, int] = {}
    for liste in kandidaten.values():
        for k in liste:
            nutzung[k] = nutzung.get(k, 0) + 1
    aus: dict = {"eindeutig": [], "mehrdeutig": [], "fehlt": []}
    for d in dateien:
        k = kandidaten[d["id"]]
        if not k:
            aus["fehlt"].append(d["id"])
        elif len(k) == 1 and nutzung[k[0]] == 1:
            aus["eindeutig"].append((d["id"], k[0]))
        else:
            aus["mehrdeutig"].append((d["id"], k))
    return aus
