#!/usr/bin/env python3
"""Architekturgrenze nach der verbindlichen Migrations-README (Framework-Grenze, höchste Priorität).

Prüft den Quellbaum ``src/`` statisch über den Syntaxbaum (``ast``), auch transitiv:

    richtung:A->B           verbotene Verbindung zwischen Schichten (je Datei und Zielmodul einmal gezählt)
    qt_ausserhalb_vcl_qt    Qt-Import außerhalb von ``vcl/qt``
    qt_transitiv            Modul außerhalb von ``vcl/qt``, das über andere Module Qt lädt
    kern_durchgereicht      writer/vcl importiert über ``framework`` einen Namen, den das Framework aus ``core`` holt (Re-Export)
    offene_schnittstelle    öffentliche Framework-Funktion mit ``object``/``Any`` oder einem core-Typ in der Signatur
    schnittstelle_veraenderbar  ``dict``/``list``/``set`` in der Signatur einer öffentlichen Framework-Funktion (statt unveränderlicher Typen)
    schnittstelle_auftrag   Framework-Funktion gibt ``Callable``/``lambda`` zurück, den die Oberfläche mit eigener Sitzung ausführt (leere Fassade)
    kern_ruft_oberflaeche   core-Funktion mit Parameter ``ed``/``editor`` (Rückruf an ein Objekt der Oberfläche)
    altlast_sitzungszugang  Nutzung des einen freigegebenen Übergangszugangs ``framework.sitzungen.altlast`` (nur kern_editor, bis Schritt 5)
    zerbrochener_zugriff    ``Modul.Name`` oder ``from modul import Name``, wobei es ``Name`` in diesem Modul nicht gibt (AttributeError/ImportError zur Laufzeit)
    weiterleitung           Weiterleitungsname in vcl/writer (``name = modul.name``), der alte Zugriffe am Leben hält (Legacy-Wrapper)
    dynamischer_import      ``importlib.import_module`` / ``__import__``
    platzhalter             ``.gitkeep`` und Reste unter ``src/lunivo_writer``
    zyklen                  Importzyklen (Anzahl und beteiligte Module)

Der festgehaltene Stand (``architektur_grenze_stand.json``) darf nur sinken. Jede Zahl über dem Stand und jede neue Fundstelle ist ein Verstoß.

    python3 werkzeuge/pruefungen/architektur_grenze.py                 Bericht; Rückgabe 1 bei neuen Verstößen
    python3 werkzeuge/pruefungen/architektur_grenze.py --stand-senken  übernimmt nur Verbesserungen in den Stand (erhöht nie)
    --haken-vorher / --haken-nachher / --haken-stopp                   Claude-Code-Haken (siehe .claude/settings.json)
    --git                                                              für .githooks/pre-commit

Statische Prüfung: Laufzeitwege (Rückgaben, Ereignisse, Rückrufe mit Kern-Objekten) erkennt sie nur teilweise.
"""
from __future__ import annotations

import ast
import collections
import json
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
PROJEKT = os.path.dirname(os.path.dirname(HIER))
SRC = os.path.join(PROJEKT, "src")
STAND = os.path.join(HIER, "architektur_grenze_stand.json")
QT = ("PySide6", "PyQt5", "PyQt6", "shiboken6")
SCHICHTEN = ("core", "framework", "filter", "system", "writer", "vcl")

# Erlaubte Richtungen laut README. vcl ist geteilt: vcl_qt (vcl/qt) und vcl_basis (übriges vcl, Qt-frei).
ERLAUBT = {
    "core": {"core"},
    "framework": {"framework", "core", "filter", "system"},
    "filter": {"filter", "core", "system"},
    "system": {"system"},
    "writer": {"writer", "framework", "system", "vcl_basis"},
    "vcl_basis": {"vcl_basis", "system"},
    "vcl_qt": {"vcl_qt", "vcl_basis", "writer", "system"},
}

# Der eine vom Eigentümer freigegebene Übergangszugang (Weg 1, 2026-11-25): Das Framework besitzt die einzige Sitzung; bis Schritt 5 des Pakets
# „Sitzung gehört dem Framework“ erreicht KernEditor sie nur über dieses Modul. Eigene Regel ``altlast_sitzungszugang``, Stand darf nur sinken.
ALTLAST_ZUGANG = "framework.sitzungen.altlast"
ALTLAST_ERLAUBT_AUS = "vcl.qt.widgets.dokumentansicht.bearbeitung.kern_editor"

GESCHUETZT = ("werkzeuge/pruefungen/architektur_grenze.py", "werkzeuge/pruefungen/startpruefung.py", "werkzeuge/pruefungen/architektur_grenze_stand.json",
              ".claude/settings.json", ".claude/settings.local.json", ".githooks/", "CLAUDE.md", "AGENTS.md")


def schicht(modul: str) -> str | None:
    teile = modul.split(".")
    if teile[0] == "vcl":
        return "vcl_qt" if len(teile) > 1 and teile[1] == "qt" else "vcl_basis"
    return teile[0] if teile[0] in SCHICHTEN else None


# ---- Einlesen --------------------------------------------------------------------------------------------------------------------

def module_einlesen() -> dict[str, str]:
    mods = {}
    for top in SCHICHTEN:
        for d, unter, dateien in os.walk(os.path.join(SRC, top)):
            unter[:] = [u for u in unter if u != "__pycache__"]
            for f in dateien:
                if f.endswith(".py"):
                    pfad = os.path.join(d, f)
                    m = os.path.relpath(pfad, SRC)[:-3].replace(os.sep, ".")
                    mods[m[:-9] if m.endswith(".__init__") else m] = pfad
    return mods


def aufloesen(name: str, mods: dict[str, str]) -> str | None:
    while name and name not in mods:
        name = name.rpartition(".")[0]
    return name or None


def analysieren():
    mods = module_einlesen()
    funde: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    kanten: dict[str, set[str]] = collections.defaultdict(set)
    qt_direkt: set[str] = set()
    aus_core: dict[str, set[str]] = collections.defaultdict(set)      # framework-Modul -> Namen, die es aus core holt
    nutzungen = []                                                      # (modul, framework-modul, name, rel)
    rel = lambda m: os.path.relpath(mods[m], PROJEKT)
    baeume = {}
    gezaehlt: set[tuple[str, str]] = set()
    for m, pfad in mods.items():
        try:
            baeume[m] = ast.parse(open(pfad, encoding="utf-8").read())
        except SyntaxError as e:
            funde["syntaxfehler"][rel(m)] += 1
            print(f"Syntaxfehler {rel(m)}: {e}", file=sys.stderr)
    for m, baum in baeume.items():
        paket = m.split(".") if mods[m].endswith("__init__.py") else m.split(".")[:-1]
        quelle = schicht(m)
        for n in ast.walk(baum):
            ziele = []
            if isinstance(n, ast.Import):
                ziele = [(a.name, None) for a in n.names]
            elif isinstance(n, ast.ImportFrom):
                basis = ".".join(paket[:len(paket) - n.level + 1] + ([n.module] if n.module else [])) if n.level else (n.module or "")
                ziele = [(basis, a.name) for a in n.names]
            elif isinstance(n, ast.Call):
                fn = n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id if isinstance(n.func, ast.Name) else ""
                if fn in ("import_module", "__import__"):
                    funde["dynamischer_import"][rel(m)] += 1
            for basis, name in ziele:
                if basis.startswith(QT):
                    qt_direkt.add(m)
                    if quelle != "vcl_qt":
                        funde["qt_ausserhalb_vcl_qt"][rel(m)] += 1
                    continue
                ziel = aufloesen(f"{basis}.{name}" if name else basis, mods) or aufloesen(basis, mods)
                if not ziel or ziel == m:
                    continue
                kanten[m].add(ziel)
                zs = schicht(ziel)
                if ziel == ALTLAST_ZUGANG or ziel.startswith(ALTLAST_ZUGANG + "."):
                    if (m, ziel) not in gezaehlt:
                        gezaehlt.add((m, ziel))
                        funde["altlast_sitzungszugang"][rel(m)] += 1          # jede Nutzung zählt; erlaubt laut Stand nur aus kern_editor
                    continue
                if quelle and zs and zs not in ERLAUBT[quelle] and (m, ziel) not in gezaehlt:
                    gezaehlt.add((m, ziel))                                          # je Datei und Zielmodul einmal, nicht je Name
                    funde[f"richtung:{quelle}->{zs}"][rel(m)] += 1
                if quelle == "framework" and zs == "core" and name:
                    aus_core[m].add(name)
                if quelle in ("writer", "vcl_qt", "vcl_basis") and zs == "framework" and name:
                    nutzungen.append((m, aufloesen(basis, mods), name))
    for m, fw, name in nutzungen:
        if fw and name in aus_core.get(fw, ()):
            funde["kern_durchgereicht"][rel(m)] += 1
    # offene Schnittstellen im Framework
    for m, baum in baeume.items():
        if schicht(m) != "framework" or m == ALTLAST_ZUGANG:
            continue
        kern_namen = aus_core.get(m, set())
        for n in ast.walk(baum):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not n.name.startswith("_"):
                anm = [a.annotation for a in n.args.args + n.args.kwonlyargs + n.args.posonlyargs if a.annotation is not None]
                if n.returns is not None:
                    anm.append(n.returns)
                for a in anm:
                    namen = {x.id for x in ast.walk(a) if isinstance(x, ast.Name)} | {x.attr for x in ast.walk(a) if isinstance(x, ast.Attribute)}
                    texte = {x.value for x in ast.walk(a) if isinstance(x, ast.Constant) and isinstance(x.value, str)}
                    if namen & ({"object", "Any"} | kern_namen) or any(re.search(r"\b(object|Any)\b", t) for t in texte):
                        funde["offene_schnittstelle"][rel(m)] += 1
    # veränderbare Daten und Aufträge an Framework-Schnittstellen; Rückrufe des Kerns; Weiterleitungsnamen
    VERAENDERBAR = {"dict", "list", "set", "Dict", "List", "Set", "MutableMapping", "MutableSequence"}
    for m, baum in baeume.items():
        s_m = schicht(m)
        if s_m == "framework" and not m.startswith("framework.pruefung") and m != ALTLAST_ZUGANG:
            for n in ast.walk(baum):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not n.name.startswith("_"):
                    anm = [a.annotation for a in n.args.args + n.args.kwonlyargs + n.args.posonlyargs if a.annotation is not None]
                    if n.returns is not None:
                        anm.append(n.returns)
                    for a in anm:
                        namen = {x.id for x in ast.walk(a) if isinstance(x, ast.Name)} | {x.attr for x in ast.walk(a) if isinstance(x, ast.Attribute)}
                        texte = " ".join(x.value for x in ast.walk(a) if isinstance(x, ast.Constant) and isinstance(x.value, str))
                        if namen & VERAENDERBAR or re.search(r"\b(dict|list|set)\b", texte):
                            funde["schnittstelle_veraenderbar"][rel(m)] += 1
                    rueck = {x.id for x in ast.walk(n.returns) if isinstance(x, ast.Name)} | {x.attr for x in ast.walk(n.returns) if isinstance(x, ast.Attribute)} if n.returns is not None else set()
                    gibt_lambda = any(isinstance(r, ast.Return) and isinstance(r.value, ast.Lambda) for r in ast.walk(n))
                    if "Callable" in rueck or gibt_lambda:
                        funde["schnittstelle_auftrag"][rel(m)] += 1
        if s_m == "core":
            for n in ast.walk(baum):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and {a.arg for a in n.args.args + n.args.kwonlyargs + n.args.posonlyargs} & {"ed", "editor"}:
                    funde["kern_ruft_oberflaeche"][rel(m)] += 1
        if s_m in ("vcl_qt", "vcl_basis", "writer"):
            importiert = {(a.asname or a.name).split(".")[0] for x in baum.body if isinstance(x, (ast.Import, ast.ImportFrom)) for a in x.names}
            for x in baum.body:
                if isinstance(x, ast.Assign) and all(isinstance(t, ast.Name) for t in x.targets):
                    w = x.value.args[0] if isinstance(x.value, ast.Call) and isinstance(x.value.func, ast.Name) and x.value.func.id in ("list", "tuple") and x.value.args else x.value
                    if isinstance(w, ast.Attribute) and isinstance(w.value, ast.Name) and (w.value.id in importiert or w.value.id.startswith("_")):
                        funde["weiterleitung"][rel(m)] += 1
    # zerbrochene Zugriffe: Name existiert im angesprochenen Projektmodul nicht
    def _namen(mod: str) -> set[str]:
        t = baeume.get(mod)
        if t is None:
            return {"*"}
        s_ = set()
        for x in ast.walk(t):
            if isinstance(x, ast.FunctionDef) and x.name == "__getattr__" and x in t.body:
                s_.add("*")
        for x in t.body:
            for y in ast.walk(x):
                if isinstance(y, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and (y in t.body or not isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))):
                    s_.add(y.name)
                elif isinstance(y, ast.Name) and isinstance(y.ctx, ast.Store) and not isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    s_.add(y.id)
                elif isinstance(y, (ast.Import, ast.ImportFrom)) and not isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    for a in y.names:
                        s_.add("*" if a.name == "*" else (a.asname or a.name).split(".")[0])
        if mods[mod].endswith("__init__.py"):
            s_ |= {k[len(mod) + 1:].split(".")[0] for k in mods if k.startswith(mod + ".")}
        return s_
    namen_cache: dict[str, set[str]] = {}

    def namen_von(mod: str) -> set[str]:
        if mod not in namen_cache:
            namen_cache[mod] = _namen(mod)
        return namen_cache[mod]
    for m, baum in baeume.items():
        paket = m.split(".") if mods[m].endswith("__init__.py") else m.split(".")[:-1]
        alias: dict[str, str] = {}
        for n in ast.walk(baum):
            if isinstance(n, ast.Import):
                for a in n.names:
                    if a.asname and a.name in mods:
                        alias[a.asname] = a.name
            elif isinstance(n, ast.ImportFrom):
                basis = ".".join(paket[:len(paket) - n.level + 1] + ([n.module] if n.module else [])) if n.level else (n.module or "")
                for a in n.names:
                    if f"{basis}.{a.name}" in mods:
                        alias[a.asname or a.name] = f"{basis}.{a.name}"
                    elif basis in mods and a.name != "*" and not (namen_von(basis) & {a.name, "*"}):
                        funde["zerbrochener_zugriff"][rel(m)] += 1
        for n in ast.walk(baum):
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in alias and isinstance(n.ctx, ast.Load):
                ziel = alias[n.value.id]
                if not n.attr.startswith("__") and not (namen_von(ziel) & {n.attr, "*"}) and f"{ziel}.{n.attr}" not in mods:
                    funde["zerbrochener_zugriff"][rel(m)] += 1
    # transitiv Qt (auch über übergeordnete Pakete, die beim Import mitgeladen werden)
    voll = {m: set(z) | {".".join(z_.split(".")[:i]) for z_ in z for i in range(1, len(z_.split("."))) if ".".join(z_.split(".")[:i]) in mods}
            for m, z in kanten.items()}
    qt = set(qt_direkt)
    geaendert = True
    while geaendert:
        geaendert = False
        for m, z in voll.items():
            if m not in qt and z & qt:
                qt.add(m)
                geaendert = True
    for m in qt - qt_direkt:
        if schicht(m) != "vcl_qt":
            funde["qt_transitiv"][rel(m)] += 1
    # Platzhalter
    for d, unter, dateien in os.walk(SRC):
        unter[:] = [u for u in unter if u != "__pycache__"]
        for f in dateien:
            if f == ".gitkeep":
                funde["platzhalter"][os.path.relpath(os.path.join(d, f), PROJEKT)] += 1
    if os.path.isdir(os.path.join(SRC, "lunivo_writer")):
        funde["platzhalter"]["src/lunivo_writer"] += 1
    # Zyklen (Tarjan, nur direkte Importkanten)
    index, tief, stapel, auf, zaehler, sccs = {}, {}, [], set(), [0], []
    sys.setrecursionlimit(10000)

    def stark(v):
        index[v] = tief[v] = zaehler[0]
        zaehler[0] += 1
        stapel.append(v)
        auf.add(v)
        for w in kanten.get(v, ()):
            if w not in index:
                stark(w)
                tief[v] = min(tief[v], tief[w])
            elif w in auf:
                tief[v] = min(tief[v], index[w])
        if tief[v] == index[v]:
            teil = []
            while True:
                w = stapel.pop()
                auf.discard(w)
                teil.append(w)
                if w == v:
                    break
            if len(teil) > 1:
                sccs.append(teil)
    for v in list(mods):
        if v not in index:
            stark(v)
    if sccs:
        funde["zyklen"]["anzahl"] = len(sccs)
        funde["zyklen"]["module_in_zyklen"] = sum(len(s) for s in sccs)
    return {k: dict(v) for k, v in funde.items()}


# ---- Stand -----------------------------------------------------------------------------------------------------------------------

def stand_lesen() -> dict:
    with open(STAND, encoding="utf-8") as f:
        return json.load(f)


def stand_schreiben(stand: dict) -> None:
    with open(STAND, "w", encoding="utf-8") as f:
        json.dump({k: dict(sorted(v.items())) for k, v in sorted(stand.items()) if v}, f, ensure_ascii=False, indent=1)
        f.write("\n")


def neue_verstoesse(ist: dict, stand: dict) -> list[str]:
    neu = []
    for regel, dateien in ist.items():
        for datei, zahl in dateien.items():
            alt = stand.get(regel, {}).get(datei, 0)
            if zahl > alt:
                neu.append(f"{regel}: {datei}  {alt} → {zahl}")
    return sorted(neu)


def summen(d: dict) -> dict:
    return {k: sum(v.values()) if k != "zyklen" else v.get("anzahl", 0) for k, v in sorted(d.items())}


def bericht(ist: dict, stand: dict) -> str:
    zeilen = ["Architekturgrenze (README): Regel  Stand → jetzt"]
    s_alt, s_neu = summen(stand), summen(ist)
    for k in sorted(set(s_alt) | set(s_neu)):
        zeilen.append(f"  {k:32} {s_alt.get(k, 0):5} → {s_neu.get(k, 0):5}")
    return "\n".join(zeilen)


MELDUNG = ("ARCHITEKTURSPERRE: Diese Arbeit verstößt gegen die verbindliche Framework-Grenze der README "
           "(Qt → writer → framework → core; Qt nur in vcl/qt; core importiert nichts außer core). "
           "Mache die genannten Stellen rückgängig oder korrigiere sie im Sinne der README. "
           "Die Sperre und ihr Stand dürfen nicht verändert, umgangen oder abgeschaltet werden.")


# ---- Haken -----------------------------------------------------------------------------------------------------------------------

def _eingabe() -> dict:
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def _geschuetzt(pfad: str) -> bool:
    p = os.path.relpath(os.path.abspath(pfad), PROJEKT).replace(os.sep, "/") if pfad else ""
    return any(p == g or p.startswith(g) for g in GESCHUETZT)


def haken_vorher() -> int:
    e = _eingabe()
    werkzeug, eingabe = e.get("tool_name", ""), e.get("tool_input", {}) or {}
    if werkzeug in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        pfad = eingabe.get("file_path") or eingabe.get("notebook_path") or ""
        if _geschuetzt(pfad):
            print("ARCHITEKTURSPERRE: Die Sperre, ihr Stand, die Haken-Einstellungen sowie CLAUDE.md und AGENTS.md sind geschützt (nur der Eigentümer ändert sie) und dürfen nicht geändert werden.", file=sys.stderr)
            return 2
        rel = os.path.relpath(os.path.abspath(pfad), PROJEKT).replace(os.sep, "/") if pfad else ""
        if rel.endswith(".gitkeep") or rel.startswith("src/lunivo_writer/"):
            print("ARCHITEKTURSPERRE: Keine Platzhalterdateien (.gitkeep) und nichts unter src/lunivo_writer (README).", file=sys.stderr)
            return 2
        inhalt = eingabe.get("content") or eingabe.get("new_string") or "".join(x.get("new_string", "") for x in eingabe.get("edits", []) or [])
        if rel.startswith("src/") and not rel.startswith("src/vcl/qt/") and re.search(r"^\s*(from|import)\s+(PySide6|PyQt[56]|shiboken6)", inhalt, re.M):
            print(f"ARCHITEKTURSPERRE: Qt-Import in {rel} – Qt gehört ausschließlich nach src/vcl/qt (README).", file=sys.stderr)
            return 2
    elif werkzeug == "Bash":
        befehl = eingabe.get("command", "")
        if re.search(r"--no-verify|\bcommit\s+-[a-zA-Z]*n|core\.hooksPath|githooks|\.claude/settings|architektur_grenze_stand|>\s*\S*(CLAUDE|AGENTS)\.md|(sed|tee|cp|mv|rm|truncate)\b[^|;&]*(CLAUDE|AGENTS)\.md", befehl):
            print("ARCHITEKTURSPERRE: Befehl berührt die Sperre, ihre Haken oder den Stand – nicht erlaubt.", file=sys.stderr)
            return 2
        if "architektur_grenze.py" in befehl and re.search(r">|\bsed\b|\btee\b|\bcp\b|\bmv\b|\brm\b|truncate|git\s+(checkout|restore|rm)|open\(", befehl):
            print("ARCHITEKTURSPERRE: Die Sperre darf nur ausgeführt, nicht verändert werden.", file=sys.stderr)
            return 2
        if re.search(r"\.gitkeep", befehl) and re.search(r"touch|>|cp|mv|install|tee", befehl):
            print("ARCHITEKTURSPERRE: Keine Platzhalterdateien (.gitkeep) anlegen (README).", file=sys.stderr)
            return 2
    return 0


def pruefen_und_melden(blockieren_mit: int) -> int:
    neu = neue_verstoesse(analysieren(), stand_lesen())
    if not neu:
        return 0
    print(MELDUNG + "\nNeue Verstöße gegenüber dem festgehaltenen Stand:\n  " + "\n  ".join(neu[:60])
          + (f"\n  … und {len(neu) - 60} weitere" if len(neu) > 60 else ""), file=sys.stderr)
    return blockieren_mit


def main(argv: list[str]) -> int:
    if "--haken-vorher" in argv:
        return haken_vorher()
    if "--haken-nachher" in argv:
        e = _eingabe()
        if e.get("tool_name") in ("Edit", "Write", "MultiEdit", "NotebookEdit", "Bash"):
            return pruefen_und_melden(2)
        return 0
    if "--haken-stopp" in argv:
        _eingabe()
        return pruefen_und_melden(2)
    ist = analysieren()
    if "--stand-anlegen" in argv:
        if os.path.exists(STAND):
            print("Stand existiert schon; er darf nur mit --stand-senken verringert werden.", file=sys.stderr)
            return 1
        stand_schreiben(ist)
        print(bericht(ist, ist))
        return 0
    stand = stand_lesen()
    if "--stand-senken" in argv:
        neu = {r: {d: min(z, ist.get(r, {}).get(d, 0)) for d, z in dateien.items()} for r, dateien in stand.items()}
        neu = {r: {d: z for d, z in v.items() if z > 0} for r, v in neu.items()}
        editor = os.path.join(SRC, *ALTLAST_ERLAUBT_AUS.split(".")) + ".py"
        schritt5_offen = os.path.exists(os.path.join(SRC, *ALTLAST_ZUGANG.split(".")) + ".py") or (
            os.path.exists(editor) and "Bearbeitungssitzung(" in open(editor, encoding="utf-8").read())
        if "altlast_sitzungszugang" in stand and schritt5_offen:
            neu["altlast_sitzungszugang"] = stand["altlast_sitzungszugang"]     # Freigabe bleibt bis Schritt 5: Altlast-Modul weg UND kern_editor erzeugt keine Sitzung mehr
        stand_schreiben(neu)
        print(bericht(ist, neu))
        return 0
    print(bericht(ist, stand))
    neu = neue_verstoesse(ist, stand)
    if neu:
        print("\nNEUE VERSTÖSSE:\n  " + "\n  ".join(neu))
        return 1
    print("\nKeine neuen Verstöße. (Bestehende Altlast laut Stand; Ziel: alle Zahlen 0.)")
    return 0


if __name__ == "__main__":
    code = main(sys.argv[1:])
    if "--git" in sys.argv and code:
        print("Architektursperre: Commit abgebrochen.", file=sys.stderr)
    sys.exit(code)
