"""Wächter der Darstellung: findet in den Dateien der Oberfläche alles, was sein Aussehen selbst festlegt, statt es aus dem Baukasten zu beziehen.

Gemeldet wird (über den Syntaxbaum, ``ast``):

* direkt erzeugtes ``QPushButton``, ``QToolButton``, ``QCheckBox``, ``QRadioButton``, ``QLineEdit`` und ``QFrame``  → Bausteine ``knopf``, ``werkzeugknopf``, ``haken``,
  ``option``, ``zeilenfeld``, ``rahmen`` aus ``baukasten/bausteine/``
* ``QGridLayout``  → ``RasterLayout`` / ``FormularGitter``
* ``setStyleSheet``  → eine Rolle (``darstellung.rolle``), das Aussehen steht in ``oberflaeche_regeln.py``
* Farbtexte (``#…``, ``rgb(``, ``rgba(``) und ``QColor`` mit festen Zahlen  → ``basis/farben.py``
* Zahlen außer 0, 1 und -1 in ``setFixed*``, ``setMinimum*``, ``setMaximum*``, ``resize``, ``setContentsMargins``, ``setSpacing*``, ``setPointSize*``, ``setPixelSize``,
  ``QPen``, ``drawRoundedRect``, ``QFont``  → ``basis/mass.py``  (Halbieren mit ``/ 2`` ist erlaubt)
* feste Schriftartnamen in ``QFont``, ``setFamily``, ``setFontFamilies``  → ``basis/schriftarten.py``

Ausgenommen sind ``baukasten/basis/``, ``baukasten/bausteine/``, ``baukasten/thema/`` und dieser Ordner; Docstrings zählen nicht.

``DARSTELLUNG_NOCH_NICHT_UMGESTELLT`` (Datei → Anzahl der Stellen) nennt, was noch offen ist. Die Liste darf nur kleiner werden: Neue Dateien kommen nie darauf, und die
Zahl einer Datei darf nicht steigen."""
from __future__ import annotations

import ast
import os
import re

BAUSTEIN_FUER = {"QPushButton": "knopf", "QToolButton": "werkzeugknopf", "QCheckBox": "haken", "QRadioButton": "option", "QLineEdit": "zeilenfeld", "QFrame": "rahmen"}
ZAHLEN_AUFRUFE = {"setFixedSize", "setFixedHeight", "setFixedWidth", "setMinimumHeight", "setMinimumWidth", "setMinimumSize", "setMaximumHeight", "setMaximumWidth",
                  "setMaximumSize", "setContentsMargins", "setSpacing", "setHorizontalSpacing", "setVerticalSpacing", "addSpacing", "resize", "setPixelSize",
                  "setPointSize", "setPointSizeF", "QPen", "drawRoundedRect", "QFont"}
SCHRIFTART_AUFRUFE = {"QFont", "setFamily", "setFontFamilies"}
FARBTEXT = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(")
ERLAUBTE_ZAHLEN = (0, 1, -1)

QUELLE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))))   # …/src
OBERFLAECHEN = tuple(os.path.join(QUELLE, n) for n in ("vcl", "writer"))                                  # die Oberfläche: Qt-Darstellung und Steuerung
BAUKASTEN = os.path.join(QUELLE, "vcl", "qt", "widgets", "bausteine")
# Das Fundament des Baukastens (Maße, Farben, Schriften, Rahmen, Bausteine, Thema, dieser Wächter) legt das Aussehen fest und ist von der Prüfung ausgenommen.
AUSGENOMMEN = tuple(os.path.join(BAUKASTEN, n) + os.sep for n in (
    "abstaende", "farben", "schrift", "rahmen", "skalierung", "drag_drop", os.path.join("interaktion", "knopf"), os.path.join("interaktion", "haken"),
    os.path.join("interaktion", "option"), os.path.join("interaktion", "feld"), os.path.join("zustaende", "pruefung")))

# Datei (Pfad ab ``src/``, mit ``/``) → Anzahl der Stellen. Zu Beginn mit dem Ist-Stand gefüllt; darf nur kleiner werden.
DARSTELLUNG_NOCH_NICHT_UMGESTELLT: dict[str, int] = {
    "vcl/qt/fenster/fenster/bearbeiten.py": 1, "vcl/qt/fenster/fenster/programmfenster.py": 1,
    "vcl/qt/widgets/bausteine/interaktion/felder/kacheln.py": 1, "vcl/qt/widgets/bausteine/interaktion/felder/ring.py": 1,
    "vcl/qt/widgets/bausteine/symbole/medien/listen_symbole.py": 1, "vcl/qt/widgets/bausteine/symbole/medien/seiten_bildchen.py": 6,
    "vcl/qt/widgets/bausteine/symbole/medien/umbruch_symbole.py": 1,
    "vcl/qt/widgets/dialoge/dokument/aenderungs_vorschau.py": 1, "vcl/qt/widgets/dialoge/dokument/eingabe_fenster.py": 1,
    "vcl/qt/widgets/dialoge/dokument/gliederung_anpassen_dialog.py": 2,
    "vcl/qt/widgets/dialoge/formatierung/rahmen_seite.py": 2, "vcl/qt/widgets/dialoge/formatierung/ruby_dialog.py": 1,
    "vcl/qt/widgets/dialoge/formatierung/texteffekt_dialog.py": 1, "vcl/qt/widgets/dialoge/formatierung/umschlossen_dialog.py": 1,
    "vcl/qt/widgets/dialoge/lesen_hilfe/hilfe_dialoge.py": 1,
    "vcl/qt/widgets/dokumentansicht/bearbeitung/freie_bilder_knoten.py": 1, "vcl/qt/widgets/dokumentansicht/bearbeitung/objekt_texteingabe.py": 1,
    "vcl/qt/widgets/dokumentansicht/dokumentfenster/navigation_hilfen.py": 1,
    "vcl/qt/widgets/menues/backstage/backstage_seitenleisten.py": 1,
    "vcl/qt/widgets/menues/dropdown/auswahl/farbpalette_hilfen.py": 3, "vcl/qt/widgets/menues/dropdown/auswahl/raster_auswahl.py": 2,
    "vcl/qt/widgets/menues/dropdown/galerie_auswahl.py": 1,
    "vcl/qt/widgets/menues/dropdown/objektmenues/diagramm_popups.py": 4, "vcl/qt/widgets/menues/dropdown/objektmenues/objekt_menues.py": 1,
    "vcl/qt/widgets/ribbon/band_stile.py": 1, "vcl/qt/widgets/seitenleisten/vorlagen/formatvorlagen_bereich.py": 1,
}


def _name(n: ast.Call) -> str:
    return n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id if isinstance(n.func, ast.Name) else ""


def _zahlen(n: ast.AST) -> bool:
    """Enthält der Ausdruck eine Zahl außer 0, 1, -1? Halbieren (``/ 2``, ``// 2``) zählt nicht."""
    if isinstance(n, ast.Constant):
        return isinstance(n.value, (int, float)) and not isinstance(n.value, bool) and n.value not in ERLAUBTE_ZAHLEN
    if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Div, ast.FloorDiv)) and isinstance(n.right, ast.Constant) and n.right.value == 2:
        return _zahlen(n.left)
    return any(_zahlen(k) for k in ast.iter_child_nodes(n))


def _ist_text(n: ast.AST) -> bool:
    return isinstance(n, ast.Constant) and isinstance(n.value, str) and bool(n.value)


def _mass_argumente(name: str, n: ast.Call) -> list[ast.AST]:
    """Die Argumente, die ein Maß tragen: bei ``QPen`` die Breite, bei ``drawRoundedRect`` die Radien, bei ``QFont`` die Größe, sonst alle."""
    args = [*n.args, *(k.value for k in n.keywords)]
    if name == "QPen":
        return args[1:2]
    if name == "drawRoundedRect":
        return args[-2:]
    if name == "QFont":
        return args[1:2]
    return args


def _text_konstanten(baum: ast.AST) -> list[ast.Constant]:
    doc = set()
    for n in ast.walk(baum):
        if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and n.body and isinstance(n.body[0], ast.Expr) \
                and isinstance(n.body[0].value, ast.Constant) and isinstance(n.body[0].value.value, str):
            doc.add(id(n.body[0].value))
    return [n for n in ast.walk(baum) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in doc]


def stellen(baum: ast.AST) -> list[tuple[int, str]]:
    """Alle Stellen einer Datei, die ihre Darstellung selbst festlegen: (Zeile, Art)."""
    funde: list[tuple[int, str]] = []
    for n in ast.walk(baum):
        if not isinstance(n, ast.Call):
            continue
        name = _name(n)
        args = [*n.args, *(k.value for k in n.keywords)]
        if name in BAUSTEIN_FUER:
            funde.append((n.lineno, f"{name}() direkt → {BAUSTEIN_FUER[name]}()"))
        elif name == "QGridLayout":
            funde.append((n.lineno, "QGridLayout() direkt → RasterLayout"))
        elif name == "setStyleSheet":
            funde.append((n.lineno, "setStyleSheet → Rolle"))
        elif name == "QColor" and len([a for a in n.args if isinstance(a, ast.Constant) and isinstance(a.value, (int, float))]) >= 3:
            funde.append((n.lineno, "QColor mit festen Zahlen → basis/farben"))
        if name in ZAHLEN_AUFRUFE and any(_zahlen(a) for a in _mass_argumente(name, n)):
            funde.append((n.lineno, f"Zahl in {name} → basis/mass"))
        if name in SCHRIFTART_AUFRUFE and any(_ist_text(a) or isinstance(a, (ast.List, ast.Tuple)) and any(_ist_text(e) for e in a.elts) for a in args):
            funde.append((n.lineno, f"Schriftartname in {name} → basis/schriftarten"))
    for k in _text_konstanten(baum):
        if FARBTEXT.search(k.value):
            funde.append((k.lineno, "Farbtext → basis/farben"))
    return sorted(funde)


def pruefe_alles() -> dict[str, list[tuple[int, str]]]:
    """Datei (relativ zu ``src/``) → ihre Stellen; nur Dateien mit mindestens einer Stelle."""
    ergebnis: dict[str, list[tuple[int, str]]] = {}
    for wurzel in OBERFLAECHEN:
        for ordner, dirs, dateien in os.walk(wurzel):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for datei in dateien:
                pfad = os.path.join(ordner, datei)
                if not datei.endswith(".py") or any(pfad.startswith(a) for a in AUSGENOMMEN):
                    continue
                with open(pfad, encoding="utf-8") as f:
                    s = stellen(ast.parse(f.read()))
                if s:
                    ergebnis[os.path.relpath(pfad, QUELLE).replace(os.sep, "/")] = s
    return ergebnis
