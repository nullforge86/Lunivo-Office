#!/usr/bin/env python3
"""Architekturprüfung: der Dokumentenkern bleibt frei von Qt (``Unbenannter Ordner/CLAUDE.md``, Abschnitt „Architektursperre“).

Rein statisch (``ast``, kein Import der geprüften Module, keine Ausführung von Projektcode):

    python3 werkzeuge/pruefungen/architekturpruefung.py [--projekt PROJEKTORDNER]

Ergebnis: Ausgabe jedes Verstoßes mit Datei, Stelle, Regel, Erklärung und zulässiger Korrekturrichtung; Rückgabewert 1 bei mindestens einem Verstoß
(blockierend), sonst 0. Es gibt bewusst keine Ausnahmenliste: Neue Ausnahmen braucht die ausdrückliche Genehmigung des Projektinhabers.

Schichten (Pfade unter ``src/lunivo_writer``):

* GESCHÜTZT: ``core/``, ``modelle/`` und die Qt-freien Dokument-Adapter (Import/Export) aus ``GESCHUETZT_DATEIEN``. Hier ist jede Qt-Abhängigkeit,
  auch eine indirekte über eigene Module, verboten.
* GUI-SCHICHT (Qt erlaubt): ``oberflaeche/``, ``adapter/qt/``, ``kern/``, ``plattform/``, ``app.py``, ``__main__.py``.
* Alles übrige (``editor/``, ``ki/``, ``korrektur/``, übrige ``dienste/``): darf Qt für Darstellung nutzen, aber keine Qt-Dokumentklassen verwenden.

Herkunft der geschützten Bereiche (nicht geraten): ``writing-block.md`` §4 „Verantwortlichkeiten der Pakete“ (``core/document``, ``core/editing``, ``core/textlayout``,
``core/layout``, ``core/rendering``) und die tatsächlichen Verzeichnisse; ``modelle/`` (Seiteneinrichtung, schon ohne Qt) und die Dokument-Adapter aus ``dienste/``,
die Dokumentmodelle lesen oder erzeugen (§4 „dienste/“, Hauptprompt „Import und Export“). Der Qt-Renderer liegt in ``adapter/qt`` (GUI-Schicht), nicht in ``core/rendering``.

GRENZEN DER ERKENNUNG (keine Behauptung vollständiger Abdeckung): Erkannt werden Importe (auch in Funktionen, mit Aliasen und relativen Pfaden), Verwendung von
Qt-Dokumentklassen als Namen/Attribute, die Importkette zwischen Projektmodulen und Importe über ``importlib.import_module``/``__import__`` mit Zeichenkettenliteral.
NICHT statisch prüfbar sind Importe mit berechnetem Modulnamen, ``getattr``/``exec``/``eval``, Plugins und Qt-Objekte, die als Parameter hereinkommen; solche Stellen
werden als „nicht vollständig statisch prüfbar“ ausgegeben. Zweite Dokument-Engine, zweiter Bearbeitungsweg und Qt-Rückfallweg sind nur über ihre Spuren erkennbar
(Qt-Dokumentklassen, Importkette, auffällige Klassennamen: AQ-5 als Prüfhinweis); den Rest sichern die Schichtgrenzen (öffentliche ``__init__``-Schnittstellen,
``core`` kennt keine GUI) und die manuelle Prüfung nach ``CLAUDE.md``.

Regeln:  AQ-1 Qt-Import im geschützten Modul · AQ-2 Qt-Dokumentklasse außerhalb der GUI-Schicht · AQ-3 indirekte Qt-Abhängigkeit eines geschützten Moduls ·
AQ-4 Abhängigkeitsrichtung (geschützt → GUI-Schicht oder Qt-Dokumenteditor) ·
AQ-6 Qt-Dokumentklasse in der GUI-Schicht ohne eigenes Qt-Textfeld (``kern/``, ``adapter/qt``, Dialoge, Bandbefehle: dort darf Qt nur anzeigen und Ereignisse
entgegennehmen; ``QPlainTextEdit``/``QTextEdit``/``QTextBrowser`` als eigenständiges Eingabe- oder Anzeigefeld bleiben erlaubt, und in einer Datei, die ein solches
Feld selbst benutzt, sind die Klassen des Feldes (Cursor, Format, Fragment) zulässig und werden nur als Prüfhinweis gemeldet) ·
AQ-7 bekannte alte Qt-Dokumentspiegelung (``document_to_qt``, ``document_from_qt`` und gleichwertige Namen als Definition, Import oder Aufruf, überall)."""
from __future__ import annotations

import argparse
import ast
import os
import sys

PAKET = "lunivo_writer"
QT_PAKETE = ("PySide6", "PyQt5", "PyQt6", "shiboken6", "shiboken2", "PySide2")

# Qt-Klassen, die ein Dokument, seine Bearbeitung oder sein Layout tragen: außerhalb der GUI-Schicht verboten.
QT_DOKUMENTKLASSEN = frozenset({
    "QTextDocument", "QTextCursor", "QTextEdit", "QPlainTextEdit", "QTextBrowser", "QTextBlock", "QTextBlockFormat", "QTextCharFormat",
    "QTextFrame", "QTextFrameFormat", "QTextTable", "QTextTableFormat", "QTextTableCell", "QTextList", "QTextListFormat", "QTextFormat",
    "QTextImageFormat", "QTextFragment", "QTextLayout", "QTextDocumentFragment", "QTextDocumentWriter", "QAbstractTextDocumentLayout",
    "QTextDocumentLayout"})

# Eigenständige Qt-Textfelder (Eingabe-/Anzeigeelemente): erlaubt, solange sie nicht als Dokument-Engine dienen. Alle übrigen QT_DOKUMENTKLASSEN sind in der GUI-Schicht
# nur zulässig, wenn dieselbe Datei ein solches Feld verwendet (AQ-6).
QT_TEXTFELDER = frozenset({"QPlainTextEdit", "QTextEdit", "QTextBrowser"})
# Namen der alten Dokumentspiegelung zwischen Dokumentmodell und Qt-Textdokument (AQ-7).
QT_SPIEGELUNG = frozenset({"document_to_qt", "document_from_qt", "dokument_zu_qt", "dokument_aus_qt", "modell_zu_qt", "modell_aus_qt"})

# GUI-Schicht: hier ist Qt erlaubt (Oberfläche, Interaktion, Darstellung fertig berechneter Seiten).
GUI_PRAEFIXE = ("oberflaeche", "adapter.qt", "kern", "plattform", "app", "__main__")
# Geschützt: der Kern und alles, was nur das Dokumentmodell kennt.
GESCHUETZT_PRAEFIXE = ("core", "modelle")
# Qt-freie Dokument-Adapter (Import/Export), die nie eine zweite Dokumentrepräsentation führen dürfen.
GESCHUETZT_DATEIEN = (
    "dienste.docx_dokument_leser", "dienste.docx_modell_schreiber", "dienste.docx_erhalt", "dienste.docx_formen", "dienste.docx_diagramm",
    "dienste.odt_dokument_leser", "dienste.odt_modell_leser", "dienste.odt_modell_schreiber", "dienste.odt_seite_schreiben", "dienste.odt_basis", "dienste.odt_xml",
    "dienste.rtf_dokument_leser", "dienste.rtf_modell_schreiber", "dienste.rtf_basis", "dienste.rtf", "dienste.rtf.modell", "dienste.rtf.zerleger", "dienste.rtf.gruppen",
    "dienste.rtf.steuerwoerter", "dienste.rtf.bilder", "dienste.txt_modell", "dienste.modell_laden", "dienste.modell_speichern",
    "dienste.docx_effekte", "dienste.docx_bildeffekte", "dienste.pdf_struktur", "dienste.pdf_export", "dienste.dateiformate", "dienste.import_grenzen", "dienste.sicher_schreiben", "dienste.formate", "dienste.textsatz",
    "plattform", "plattform.dateisystem", "plattform.sperre", "plattform.schriften",    # Qt-freie Plattformmodule (Paketkopf ohne Importe, Dateisystem, Sperrdatei, Schriftordner): Infrastruktur des Kerns
    "kern.farben")                                                    # die Farbnamen: reine Zeichenketten, ohne Importe; Modell und Kern dürfen sie nutzen
# Der Qt-Dokumenteditor (alte Schicht): nie Abhängigkeit eines geschützten Moduls.
QT_EDITOR_PRAEFIXE = ("editor", "adapter", "oberflaeche", "kern")

import re  # noqa: E402

# Auffällige Klassennamen außerhalb von ``core``: möglicher Hinweis auf eine zweite Engine (Heuristik, nur Prüfhinweis).
ZWEITE_ENGINE = re.compile(r"(Layout|Textsatz|Satz|Dokument|Document|Bearbeitung|Editing|Sitzung)(Engine|Modell|Model|Kern|Core)$|^(DokumentEngine|LayoutEngine|TextLayoutEngine)$")

REGELTEXT = {
    "AQ-1": ("Qt-Import in einem geschützten Modul",
             "Dokumentkern und Qt-freie Dokument-Adapter dürfen weder PySide6 noch PyQt importieren.",
             "Die Logik ohne Qt im Kern lösen; Qt-Typen (Bilder, Schriften) gehören in die Rendering-Adapter unter adapter/qt oder in die Oberfläche."),
    "AQ-2": ("Qt-Dokumentklasse außerhalb der GUI-Schicht",
             "QTextDocument, QTextCursor & Co. dürfen weder das Dokument noch Import, Export, Textsatz oder Layout tragen (zweite Dokument-Engine).",
             "Das Dokumentmodell (core/document) und die zentrale Bearbeitung (core/editing) verwenden; Dateiformate direkt ins Modell lesen und aus ihm schreiben."),
    "AQ-3": ("Indirekte Qt-Abhängigkeit eines geschützten Moduls",
             "Das Modul importiert (auch erst innerhalb einer Funktion) ein eigenes Modul, das seinerseits Qt benutzt.",
             "Die benötigte Funktion Qt-frei im Kern oder in einem Qt-freien Adapter bereitstellen und die Abhängigkeit auf diese umstellen."),
    "AQ-6": ("Qt-Dokumentklasse in der GUI-Schicht außerhalb eines eigenen Qt-Textfelds",
             "Die Oberfläche darf Qt-Textdokument-, Cursor- und Formatklassen nur für eigenständige Eingabe-/Anzeigefelder (QPlainTextEdit, QTextEdit, QTextBrowser) "
             "in derselben Datei verwenden; als Bearbeitungsweg, Formatträger oder Dokumentkopie sind sie eine zweite Dokumentverarbeitung.",
             "Die Dokumentänderung über die zentrale Bearbeitung (core/editing) als Wörterbücher und Modellklassen auslösen; Formate als Wörterbücher übergeben."),
    "AQ-7": ("Alte Qt-Dokumentspiegelung",
             "Funktionen wie document_to_qt/document_from_qt übertragen das maßgebliche Dokument in ein Qt-Textdokument oder zurück (zweite Dokumentrepräsentation).",
             "Den Aufrufer auf das Dokumentmodell (core/document), die Bearbeitung (core/editing), das Layout (core/layout) und das Rendering (core/rendering) umstellen."),
    "AQ-4": ("Falsche Abhängigkeitsrichtung",
             "Geschützte Module dürfen weder die GUI-Schicht noch den Qt-Dokumenteditor oder die Rendering-Adapter importieren (erlaubt: GUI → Kern).",
             "Die Abhängigkeit umkehren: die Oberfläche ruft den Kern, nie umgekehrt; gemeinsame Typen in den Kern verlegen."),
}


class Verstoss:
    def __init__(self, regel: str, datei: str, zeile: int, stelle: str, detail: str = ""):
        self.regel, self.datei, self.zeile, self.stelle, self.detail = regel, datei, zeile, stelle, detail

    def text(self) -> str:
        titel, erklaerung, korrektur = REGELTEXT[self.regel]
        zeilen = [f"{self.regel}  {titel}", f"  Datei:      {self.datei}:{self.zeile}", f"  Stelle:     {self.stelle}"]
        if self.detail:
            zeilen.append(f"  Kette:      {self.detail}")
        zeilen += [f"  Warum:      {erklaerung}", f"  Korrektur:  {korrektur}"]
        return "\n".join(zeilen)


def _beginnt(name: str, praefixe) -> bool:
    return any(name == p or name.startswith(p + ".") for p in praefixe)


class Quellbaum:
    """Alle Python-Module unter ``src/lunivo_writer``: Name → (Pfad, AST)."""

    def __init__(self, projekt: str, ueberschreibe: dict[str, str] | None = None):
        """``ueberschreibe``: absoluter Dateipfad → Quelltext, der statt des Dateiinhalts geprüft wird (Vorabprüfung einer geplanten Änderung)."""
        self.wurzel = os.path.join(projekt, "src", PAKET)
        ueberschreibe = {os.path.abspath(k): v for k, v in (ueberschreibe or {}).items()}
        self.module: dict[str, tuple[str, ast.AST]] = {}
        self.fehler: list[str] = []
        for ordner, dirs, dateien in os.walk(self.wurzel):
            dirs[:] = sorted(d for d in dirs if d != "__pycache__")
            for datei in sorted(dateien):
                if not datei.endswith(".py"):
                    continue
                pfad = os.path.join(ordner, datei)
                rel = os.path.relpath(pfad, self.wurzel)[:-3].replace(os.sep, ".")
                name = rel[:-len(".__init__")] if rel.endswith(".__init__") else rel
                if rel == "__init__":
                    name = ""
                try:
                    if os.path.abspath(pfad) in ueberschreibe:
                        self.module[name] = (pfad, ast.parse(ueberschreibe[os.path.abspath(pfad)], pfad))
                        continue
                    with open(pfad, encoding="utf-8") as f:
                        self.module[name] = (pfad, ast.parse(f.read(), pfad))
                except (SyntaxError, UnicodeDecodeError, OSError) as e:
                    self.fehler.append(f"{os.path.relpath(pfad, self.wurzel)}: nicht lesbar ({e})")

    def ist_paket(self, name: str) -> bool:
        pfad = self.module.get(name, ("", None))[0]
        return os.path.basename(pfad) == "__init__.py"

    def aufloesen(self, kandidat: str) -> str | None:
        """Der längste vorhandene Modulname, der ``kandidat`` (mit Paketnamen ohne Präfix) entspricht."""
        teile = kandidat.split(".") if kandidat else []
        while teile:
            n = ".".join(teile)
            if n in self.module:
                return n
            teile.pop()
        return None


def importe_von(baum: Quellbaum, name: str) -> list[tuple[int, str, str | None, str | None]]:
    """Alle Importe (auch in Funktionen): (Zeile, Text, Qt-Paket oder None, Projektmodul oder None)."""
    _pfad, kopf = baum.module[name]
    paket = name if baum.ist_paket(name) else name.rpartition(".")[0]
    erg = []
    for n in ast.walk(kopf):
        if isinstance(n, ast.Call) and _importaufruf(n) and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
            modul = n.args[0].value
            qt = modul.split(".")[0] if modul.split(".")[0] in QT_PAKETE else None
            ziel = baum.aufloesen(modul[len(PAKET) + 1:]) if modul.startswith(PAKET + ".") else None
            erg.append((n.lineno, f"import_module('{modul}')", qt, ziel))
        elif isinstance(n, ast.Import):
            for a in n.names:
                qt = a.name.split(".")[0] if a.name.split(".")[0] in QT_PAKETE else None
                ziel = None
                if a.name == PAKET or a.name.startswith(PAKET + "."):
                    ziel = baum.aufloesen(a.name[len(PAKET) + 1:])
                erg.append((n.lineno, f"import {a.name}", qt, ziel))
        elif isinstance(n, ast.ImportFrom):
            modul = n.module or ""
            if n.level == 0:
                qt = modul.split(".")[0] if modul.split(".")[0] in QT_PAKETE else None
                basis = modul[len(PAKET) + 1:] if modul.startswith(PAKET + ".") else ("" if modul == PAKET else None)
                if qt:
                    erg.append((n.lineno, f"from {modul} import ...", qt, None))
                elif basis is not None:
                    ziele = _ziele(baum, basis, n)
                    erg += [(n.lineno, f"from {modul} import {', '.join(a.name for a in n.names)}", None, z) for z in ziele] or \
                           [(n.lineno, f"from {modul} import ...", None, None)]
            else:
                teile = paket.split(".") if paket else []
                hoch = n.level - 1
                if hoch > len(teile):
                    continue
                basis_teile = teile[:len(teile) - hoch] if hoch else teile
                basis = ".".join(basis_teile + ([modul] if modul else []))
                ziele = _ziele(baum, basis, n)
                erg += [(n.lineno, f"from {'.' * n.level}{modul} import {', '.join(a.name for a in n.names)}", None, z) for z in ziele]
    return erg


def _importaufruf(n: ast.Call) -> bool:
    f = n.func
    return (isinstance(f, ast.Name) and f.id in ("__import__", "import_module")) or (isinstance(f, ast.Attribute) and f.attr in ("import_module", "__import__"))


def dynamische_importe(kopf: ast.AST) -> list[tuple[int, str]]:
    """Importe mit berechnetem Modulnamen (nicht statisch auflösbar) und ``exec``/``eval``: (Zeile, Text)."""
    funde = []
    for n in ast.walk(kopf):
        if isinstance(n, ast.Call):
            if _importaufruf(n) and not (n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str)):
                funde.append((n.lineno, "Import mit berechnetem Modulnamen"))
            elif isinstance(n.func, ast.Name) and n.func.id in ("exec", "eval"):
                funde.append((n.lineno, f"{n.func.id}(...)"))
    return funde


def _ziele(baum: Quellbaum, basis: str, n: ast.ImportFrom) -> list[str]:
    """Projektmodule, die ``from basis import namen`` anspricht: ``basis`` selbst und jedes ``basis.name``, das ein Modul ist."""
    ziele = []
    b = baum.aufloesen(basis) if basis else ("" if "" in baum.module else None)
    if b is not None:
        ziele.append(b)
    for a in n.names:
        voll = f"{basis}.{a.name}" if basis else a.name
        if voll in baum.module:
            ziele.append(voll)
    return list(dict.fromkeys(ziele))


def verwendete_dokumentklassen(kopf: ast.AST) -> list[tuple[int, str]]:
    funde = []
    for n in ast.walk(kopf):
        if isinstance(n, ast.ImportFrom):
            funde += [(n.lineno, a.name) for a in n.names if a.name in QT_DOKUMENTKLASSEN]
        elif isinstance(n, ast.Name) and n.id in QT_DOKUMENTKLASSEN:
            funde.append((n.lineno, n.id))
        elif isinstance(n, ast.Attribute) and n.attr in QT_DOKUMENTKLASSEN:
            funde.append((n.lineno, n.attr))
    return sorted(set(funde))


def spiegelungsnamen(kopf: ast.AST) -> list[tuple[int, str]]:
    """AQ-7: Definitionen, Importe und Verwendungen der bekannten Namen der alten Qt-Dokumentspiegelung."""
    funde = []
    for n in ast.walk(kopf):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in QT_SPIEGELUNG:
            funde.append((n.lineno, n.name))
        elif isinstance(n, ast.ImportFrom):
            funde += [(n.lineno, a.name) for a in n.names if a.name in QT_SPIEGELUNG]
        elif isinstance(n, ast.Name) and n.id in QT_SPIEGELUNG:
            funde.append((n.lineno, n.id))
        elif isinstance(n, ast.Attribute) and n.attr in QT_SPIEGELUNG:
            funde.append((n.lineno, n.attr))
    return sorted(set(funde))


def pruefen(projekt: str, ueberschreibe: dict[str, str] | None = None) -> tuple[list[Verstoss], list[str]]:
    baum = Quellbaum(projekt, ueberschreibe)
    verstoesse: list[Verstoss] = []
    rel = lambda n: os.path.relpath(baum.module[n][0], projekt)          # noqa: E731
    importe = {n: importe_von(baum, n) for n in baum.module}
    qt_direkt = {n for n, liste in importe.items() if any(qt for _z, _t, qt, _m in liste)}

    def geschuetzt(n: str) -> bool:
        return _beginnt(n, GESCHUETZT_PRAEFIXE) or n in GESCHUETZT_DATEIEN

    def gui(n: str) -> bool:
        return _beginnt(n, GUI_PRAEFIXE) and n not in GESCHUETZT_DATEIEN

    def kette(start: str) -> list[str] | None:
        """Kürzester Importweg von ``start`` zu einem Modul mit direktem Qt-Import (ohne ``start`` selbst), sonst None."""
        gesehen, warteschlange = {start}, [[start]]
        while warteschlange:
            pfad = warteschlange.pop(0)
            for _z, _t, _qt, ziel in importe.get(pfad[-1], []):
                if ziel is None or ziel in gesehen:
                    continue
                gesehen.add(ziel)
                if ziel in qt_direkt:
                    return pfad + [ziel]
                warteschlange.append(pfad + [ziel])
        return None

    for name in sorted(baum.module):
        datei = rel(name)
        for zeile, klasse in spiegelungsnamen(baum.module[name][1]):                                    # AQ-7 gilt überall
            verstoesse.append(Verstoss("AQ-7", datei, zeile, klasse))
        if gui(name):
            funde = verwendete_dokumentklassen(baum.module[name][1])
            if not any(k in QT_TEXTFELDER for _z, k in funde):                                           # AQ-6: ohne eigenes Textfeld gibt es keinen zulässigen Grund
                verstoesse += [Verstoss("AQ-6", datei, zeile, klasse) for zeile, klasse in funde]
            continue
        if not geschuetzt(name):
            for zeile, klasse in verwendete_dokumentklassen(baum.module[name][1]):                        # AQ-2 gilt überall außerhalb der GUI-Schicht
                verstoesse.append(Verstoss("AQ-2", datei, zeile, klasse))
            continue
        for zeile, klasse in verwendete_dokumentklassen(baum.module[name][1]):
            verstoesse.append(Verstoss("AQ-2", datei, zeile, klasse))
        gemeldet: set[tuple[int, str]] = set()
        for zeile, text, qt, ziel in importe[name]:
            if qt:
                verstoesse.append(Verstoss("AQ-1", datei, zeile, text))
                continue
            if ziel is None or (zeile, ziel) in gemeldet:
                continue
            if geschuetzt(ziel):
                continue                                                  # das Zielmodul wird selbst geprüft und dort gemeldet
            if _beginnt(ziel, QT_EDITOR_PRAEFIXE) or gui(ziel):
                gemeldet.add((zeile, ziel))
                verstoesse.append(Verstoss("AQ-4", datei, zeile, text, f"{name} → {ziel}"))
                continue
            if geschuetzt(ziel) and ziel not in qt_direkt and not kette(ziel):
                continue
            if geschuetzt(ziel):
                continue                                                  # das Zielmodul wird selbst geprüft und dort gemeldet
            weg = [name] + ([ziel] if ziel in qt_direkt else (kette(ziel) or []))
            if len(weg) > 1 and (ziel in qt_direkt or kette(ziel)):
                gemeldet.add((zeile, ziel))
                verstoesse.append(Verstoss("AQ-3", datei, zeile, text, " → ".join(weg)))
    hinweise = list(baum.fehler)
    for name in sorted(baum.module):
        datei = rel(name)
        for zeile, text in dynamische_importe(baum.module[name][1]):
            hinweise.append(f"NICHT VOLLSTAENDIG STATISCH PRUEFBAR  {datei}:{zeile}  {text}" + ("  (geschütztes Modul!)" if geschuetzt(name) else ""))
        if _beginnt(name, ("core",)):
            continue
        for n in ast.walk(baum.module[name][1]):                                                   # AQ-5: Spuren einer zweiten Engine (nur Hinweis, nicht blockierend)
            if isinstance(n, ast.ClassDef) and ZWEITE_ENGINE.search(n.name):
                hinweise.append(f"PRUEFHINWEIS AQ-5  {datei}:{n.lineno}  Klasse {n.name} außerhalb von core: zweite Dokument-/Layout-/Bearbeitungs-Engine? Zuständigkeit klären.")
        if gui(name):
            klassen = sorted({k for _z, k in verwendete_dokumentklassen(baum.module[name][1])})
            if klassen:
                hinweise.append(f"PRUEFHINWEIS GUI  {datei}  nutzt Qt-Dokumentklassen ({', '.join(klassen)}): nur als Eingabe-/Darstellungselement zulässig, "
                                "kein maßgeblicher Dokumentzustand; manuell prüfen.")
    return sorted(verstoesse, key=lambda v: (v.datei, v.zeile, v.regel)), hinweise


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Architekturprüfung: Qt-freier Dokumentenkern")
    ap.add_argument("--projekt", default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), help="Projektordner (mit src/lunivo_writer)")
    args = ap.parse_args(argv)
    verstoesse, fehler = pruefen(args.projekt)
    for v in verstoesse:
        print(v.text() + "\n")
    for f in fehler:
        print(f)
    if fehler:
        print()
    print("Abdeckung: statisch geprüft werden Importe (auch lokale, mit Aliasen, relativ), Qt-Dokumentklassen und die Importkette zwischen Projektmodulen. "
          "Dynamische Importe, getattr/exec/eval und zweite Engines ohne Qt-Spur sind NICHT vollständig automatisch erkennbar (siehe Meldungen oben und Kopf der Datei).\n")
    if verstoesse:
        je_regel = {r: sum(1 for v in verstoesse if v.regel == r) for r in REGELTEXT}
        print("ARCHITEKTURVERSTOSS — BLOCKIEREND: " + ", ".join(f"{r}: {n}" for r, n in je_regel.items() if n) + f" ({len(verstoesse)} gesamt)")
        return 1
    print("Architekturprüfung: keine Verstöße gefunden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
