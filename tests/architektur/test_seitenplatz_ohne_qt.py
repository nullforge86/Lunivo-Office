"""Wächter: ``editor/layout/seitenplatz.py`` und ``seitenplan.py`` (Platz im Seitenfluss) importieren kein Qt."""
import ast
import os

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src", "lunivo_writer", "editor", "layout")


def test_platzklassen_ohne_qt():
    for name in ("seitenplatz.py", "seitenplan.py"):
        for n in ast.walk(ast.parse(open(os.path.join(DIR, name), encoding="utf-8").read())):
            namen = [a.name for a in n.names] if isinstance(n, ast.Import) else [n.module or ""] if isinstance(n, ast.ImportFrom) else []
            assert not [m for m in namen if m.startswith(("PySide6", "shiboken6"))], name
