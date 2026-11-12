"""Wächter für die Qt-Entkopplung (``dokumentation/architektur/qt-entkopplung.md``): ``core`` importiert weder Qt noch Oberfläche, Adapter oder die
alten Schichten, und die Geometrie rechnet ohne Qt."""
import ast
import os

from lunivo_writer.core.geometry import Margins, Point, Rect, Size

KERN = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src", "lunivo_writer", "core")
VERBOTEN = ("PySide6", "PyQt5", "PyQt6", "shiboken6", "lunivo_writer.adapter", "lunivo_writer.oberflaeche", "lunivo_writer.editor",
            "lunivo_writer.dienste", "lunivo_writer.kern", "lunivo_writer.ki", "lunivo_writer.korrektur")


def test_core_importiert_kein_qt_und_keine_oberflaeche():
    funde = []
    for d, _u, dateien in os.walk(KERN):
        for f in dateien:
            if not f.endswith(".py"):
                continue
            pfad = os.path.join(d, f)
            for n in ast.walk(ast.parse(open(pfad, encoding="utf-8").read())):
                namen = [a.name for a in n.names] if isinstance(n, ast.Import) else [n.module or ""] if isinstance(n, ast.ImportFrom) else []
                funde += [f"{os.path.relpath(pfad, KERN)}: {m}" for m in namen if m.startswith(VERBOTEN)]
    assert funde == []


def test_geometrie_rechnet_ohne_qt():
    r = Rect(10, 20, 100, 50)
    assert (r.right, r.bottom, r.center) == (110, 70, Point(60, 45))
    assert r.contains(Point(10, 20)) and not r.contains(Point(110, 70))                      # rechts/unten gehören nicht dazu
    assert r.intersected(Rect(100, 60, 50, 50)) == Rect(100, 60, 10, 10)
    assert r.intersected(Rect(110, 20, 5, 5)) is None                                         # nur Berührung: keine Fläche
    assert r.united(Rect(0, 0, 5, 5)) == Rect(0, 0, 110, 70) and r.united(Rect()) == r
    assert r.translated(5, -5) == Rect(15, 15, 100, 50) and r.adjusted(1, 2, -3, -4) == Rect(11, 22, 96, 44)
    assert r.shrunk(Margins(10, 5, 20, 5)) == Rect(20, 25, 70, 40) and r.shrunk(Margins(10, 5, 20, 5)).grown(Margins(10, 5, 20, 5)) == r
    assert Size(3, 4).scaled(2) == Size(6, 8) and Size(0, 4).is_empty() and Point(1, 2).translated(1, 1) == Point(2, 3)
