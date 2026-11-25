"""Befehlsseite — eine Seite aus Titel, Gruppen und Befehlsknöpfen, vollständig aus einer Beschreibung gebaut.

Texte stehen in der Beschreibung nur als Stichwörter (``texte.json``). Die Beschreibung (aus ``baukasten.basis.daten``) lautet: ``{"titel", "gruppen": [{"name", "hinweis", "knoepfe": [...]}]}``; ein Knopf hat
``text``, ``symbol`` und genau eines von ``befehl`` / ``seite`` / ``aktion`` (sowie auf Wunsch ``datei`` für ein Dateiformatsymbol). Was ein
Knopf tut, entscheidet der Aufrufer über ``ausloeser(knopf)``; ob er bedienbar ist, über ``aktiv(knopf)``. Maße kommen aus ``mass``."""
from __future__ import annotations

from lunivo_writer.oberflaeche.baukasten.basis.raster import RasterSpalte
from lunivo_writer.oberflaeche.baukasten.geruest.rollen import reihe as _reihe, spalte as _spalte

from typing import Callable

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QScrollArea, QWidget

from lunivo_writer.oberflaeche.baukasten.basis.mass import ABSTAND_MITTEL, ABSTAND_SPALTE, ICON_GROSS, ICON_KNOPF_GROSS, RAND_BACKSTAGE_SEITE
from lunivo_writer.oberflaeche.baukasten.basis.daten import text as _t
from lunivo_writer.oberflaeche.baukasten.medien.datei_symbole import datei_symbol
from lunivo_writer.oberflaeche.bauteile import symbole


def seitenrahmen(titel: str = "") -> tuple[QScrollArea, RasterSpalte]:
    """Leere, scrollbare Seite mit Titelzeile — der Boden für jede Seite der Datei-Ansicht."""
    sa = QScrollArea(); sa.setObjectName("bsSeite"); sa.setWidgetResizable(True); sa.setFrameShape(QFrame.NoFrame)
    inh = QWidget(); v = _spalte("seite", inh)
    if titel:
        t = QLabel(titel); t.setObjectName("bsTitel"); v.addWidget(t); v.addSpacing(ABSTAND_SPALTE)
    sa.setWidget(inh)
    return sa, v


def gruppenkopf(v: RasterSpalte, name: str, hinweis: str = "") -> None:
    v.addSpacing(ABSTAND_MITTEL)
    if name:
        g = QLabel(name); g.setObjectName("bsGruppe"); v.addWidget(g)
    if hinweis:
        h = QLabel(hinweis); h.setObjectName("bsHinweis"); h.setWordWrap(True); v.addWidget(h)


def befehlsknopf(v: RasterSpalte, spec: dict, ausloeser: Callable[[dict], None], aktiv: Callable[[dict], bool] = lambda _k: True) -> QPushButton:
    k = QPushButton(_t(spec["text"])); k.setObjectName("bsKnopf"); k.setCursor(Qt.PointingHandCursor)
    sym = datei_symbol(spec["datei"]) if spec.get("datei") else None
    if sym is not None and not sym.isNull():                       # eigenes, vollständiges Dateiformatblatt
        k.setIcon(sym); k.setIconSize(QSize(ICON_KNOPF_GROSS, ICON_KNOPF_GROSS))
    elif spec.get("symbol") and symbole.hat(spec["symbol"]):
        symbole.setze(k, spec["symbol"], ICON_GROSS)
    k.setEnabled(aktiv(spec))
    k.clicked.connect(lambda _=False, s=spec: ausloeser(s))
    v.addWidget(k)
    return k


def befehlsseite(beschreibung: dict, ausloeser: Callable[[dict], None], aktiv: Callable[[dict], bool] = lambda _k: True) -> QScrollArea:
    sa, v = seitenrahmen(_t(beschreibung["titel"]) if beschreibung.get("titel") else "")
    for gruppe in beschreibung.get("gruppen", []):
        if gruppe.get("name") or gruppe.get("hinweis"):
            gruppenkopf(v, _t(gruppe["name"]) if gruppe.get("name") else "", _t(gruppe["hinweis"]) if gruppe.get("hinweis") else "")
        for k in gruppe.get("knoepfe", []):
            befehlsknopf(v, k, ausloeser, aktiv)
    v.addStretch(1)
    return sa


def inhaltsseite(titel: str, inhalt: QWidget, scrollen: bool = True) -> QWidget:
    """Seite mit Titel, deren Inhalt ein fertiges Widget aus einem Fachmodul ist (z. B. das Handbuch). ``scrollen=False``: der Inhalt scrollt selbst."""
    if scrollen:
        sa, v = seitenrahmen(titel)
        v.addWidget(inhalt, 1)
        return sa
    w = QWidget(); w.setObjectName("bsInhalt")
    v = _spalte("seite", w)
    t = QLabel(titel); t.setObjectName("bsTitel"); v.addWidget(t); v.addWidget(inhalt, 1)
    return w
