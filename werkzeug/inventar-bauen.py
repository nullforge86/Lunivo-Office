#!/usr/bin/env python3
"""Schreibt docs/interne-funktionen.md: Inventar aller Module, Klassen, Funktionen und Methoden von ``src/lunivo_writer``.

    .venv/bin/python werkzeug/inventar-bauen.py

Liest den Quelltext nur über ``ast`` (nichts wird importiert oder ausgeführt) und schreibt Markdown. Die Beschreibung ist
die erste Zeile des Docstrings; fehlt er, bleibt sie leer.
"""
from __future__ import annotations

import ast
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
QUELLE = WURZEL / "src" / "lunivo_writer"
ZIEL = WURZEL / "docs" / "interne-funktionen.md"


def _kurz(knoten) -> str:
    text = ast.get_docstring(knoten) or ""
    zeile = text.strip().splitlines()[0].strip() if text.strip() else ""
    return zeile.replace("|", "\\|")


def _signatur(f) -> str:
    a = f.args
    teile = [x.arg for x in a.posonlyargs + a.args]
    if a.vararg:
        teile.append("*" + a.vararg.arg)
    elif a.kwonlyargs:
        teile.append("*")
    teile += [x.arg for x in a.kwonlyargs]
    if a.kwarg:
        teile.append("**" + a.kwarg.arg)
    return ", ".join(t for t in teile if t not in ("self", "cls"))


def _eintrag(f, einzug: str = "") -> str:
    art = "async " if isinstance(f, ast.AsyncFunctionDef) else ""
    text = _kurz(f)
    return f"{einzug}- `{art}{f.name}({_signatur(f)})`" + (f" — {text}" if text else "")


def _modul(pfad: Path) -> list[str]:
    try:
        baum = ast.parse(pfad.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError) as fehler:
        return [f"_nicht lesbar: {fehler}_"]
    zeilen: list[str] = []
    kopf = _kurz(baum)
    if kopf:
        zeilen.append(f"{kopf}\n")
    for k in baum.body:
        if isinstance(k, (ast.FunctionDef, ast.AsyncFunctionDef)):
            zeilen.append(_eintrag(k))
        elif isinstance(k, ast.ClassDef):
            basen = ", ".join(ast.unparse(b) for b in k.bases)
            text = _kurz(k)
            zeilen.append(f"- **class `{k.name}`**" + (f"({basen})" if basen else "") + (f" — {text}" if text else ""))
            for m in k.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    zeilen.append(_eintrag(m, "  "))
    return zeilen


def main() -> None:
    ausgabe = [
        "# Interne Funktionen — Inventar",
        "",
        "Vollständiges Inventar der Module, Klassen, Funktionen und Methoden von `src/lunivo_writer`. "
        "Erzeugt mit `werkzeug/inventar-bauen.py` aus dem Quelltext (`ast`, ohne Import); nicht von Hand ändern, sondern neu erzeugen. "
        "Die Beschreibung stammt aus der ersten Docstring-Zeile.",
        "",
    ]
    ordner: dict[str, list[Path]] = {}
    for p in sorted(QUELLE.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        rel = p.relative_to(QUELLE)
        ordner.setdefault(str(rel.parent) if rel.parent != Path(".") else "(Wurzel)", []).append(p)
    ausgabe.append("## Inhalt\n")
    for name, dateien in ordner.items():
        ausgabe.append(f"- `{name}` — {len(dateien)} Module")
    ausgabe.append("")
    zaehler = [0, 0, 0]
    for name, dateien in ordner.items():
        ausgabe += [f"## `{name}`", ""]
        for p in dateien:
            rel = p.relative_to(QUELLE).as_posix()
            zeilen = _modul(p)
            ausgabe += [f"### `{rel}`", ""] + zeilen + [""]
            zaehler[0] += 1
            zaehler[1] += sum(1 for z in zeilen if z.startswith("- **class"))
            zaehler[2] += sum(1 for z in zeilen if z.lstrip().startswith("- `"))
    ausgabe.insert(4, f"Stand: {zaehler[0]} Module, {zaehler[1]} Klassen, {zaehler[2]} Funktionen und Methoden.\n")
    ZIEL.write_text("\n".join(ausgabe) + "\n", encoding="utf-8")
    print(f"{ZIEL.relative_to(WURZEL)}: {zaehler[0]} Module, {zaehler[1]} Klassen, {zaehler[2]} Funktionen/Methoden")


if __name__ == "__main__":
    main()
