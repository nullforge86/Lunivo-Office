"""Der Bereich „Auswahl“ (Start ▸ Auswählen ▸ Auswahlbereich) als Baustein: alle Bilder, Formen, Diagramme und Tabellen des Dokuments in einer
Liste; ein Klick markiert das Objekt im Text (dann erscheinen seine Werkzeuge). Der Bereich ändert nichts am Dokument.

    ausfuehren(AuswahlBereich(parent, editor))       # Zusatzfenster in der Seitenleiste, offen bis „Schließen“
"""
from __future__ import annotations

from lunivo_writer.oberflaeche.baukasten.geruest.rollen import reihe as _reihe, spalte as _spalte

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QListWidget, QListWidgetItem

from lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen import knopfzeile
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import PanelFaehig
from lunivo_writer.oberflaeche.baukasten.basis.mass import ABSTAND_NORMAL, HOEHE_LISTE_REITER, RAND_PANEL_KLEIN


def objekte(ed) -> list[tuple]:
    """[(Beschriftung, Ziel)] aller Objekte in Dokumentreihenfolge; Ziel ``("text", von, bis)``, ``("frei", Id)`` oder ``("tabelle", von, bis)``."""
    from lunivo_writer.core.dokument.dokument import InlineObjekt
    from lunivo_writer.editor.dokument import gehe_zu as G
    namen = {"form": "Form", "zeichenbereich": "Zeichenbereich", "wordart": "WordArt", "diagramm": "Diagramm", "smartart": "SmartArt", "formel": "Formel",
             "piktogramm": "Piktogramm", "textfeld": "Textfeld", "gruppe": "Gruppe", "bild": "Bild"}
    dok = ed.sitzung.dokument
    stellen = G._stellen(dok)
    gefunden, zaehler = [], {}

    def benennen(art: str) -> str:
        n = namen.get(art, "Objekt")
        zaehler[n] = zaehler.get(n, 0) + 1
        return f"{n} {zaehler[n]}"
    for a in dok.absaetze():
        versatz = 0
        for x in a.inhalte:
            if isinstance(x, InlineObjekt):
                gefunden.append((stellen[a.id] + versatz, ("text", stellen[a.id] + versatz, stellen[a.id] + versatz + 1), x.art))
                versatz += 1
            else:
                versatz += len(x.text)
    gefunden += [(stellen.get(o.anker, 0), ("frei", o.id), o.art) for o in dok.objekte.values()]
    out = [(benennen(art), ziel, p) for p, ziel, art in sorted(gefunden, key=lambda x: x[0])]
    tabellen = sorted((p, t) for a in dok.abschnitte for t, p in G._tabellen(a.bloecke, stellen))
    out += [(f"Tabelle {i}", ("tabelle", p, p), p) for i, (p, _t) in enumerate(tabellen, start=1)]
    return [(n, z) for n, z, _p in sorted(out, key=lambda x: x[2])]


class AuswahlBereich(PanelFaehig, QDialog):
    def __init__(self, parent=None, ed=None):
        super().__init__(parent)
        self.setWindowTitle("Auswahl")
        self.ed = ed
        v = _spalte("panel", self)
        kopf = QLabel("Objekte im Dokument:"); kopf.setWordWrap(True)
        v.addWidget(kopf)
        self.liste = QListWidget(); self.liste.setMinimumHeight(HOEHE_LISTE_REITER)
        v.addWidget(self.liste, 1)
        self.leer = QLabel("Das Dokument enthält keine Bilder, Formen oder Tabellen."); self.leer.setWordWrap(True)
        v.addWidget(self.leer)
        v.addWidget(knopfzeile(self, schliessen=True))
        self.liste.itemClicked.connect(self._markieren)
        self.fuellen()

    def fuellen(self) -> None:
        self.liste.clear()
        for name, ziel in objekte(self.ed) if self.ed is not None else []:
            it = QListWidgetItem(name); it.setData(Qt.UserRole, ziel); self.liste.addItem(it)
        self.leer.setVisible(self.liste.count() == 0)

    def _markieren(self, it: QListWidgetItem) -> None:
        ziel = it.data(Qt.UserRole)
        if ziel[0] == "frei":
            self.ed.ansicht.gewaehltes_objekt = ziel[1]
            self.ed.freiAuswahlGeaendert.emit()
            self.ed.ansicht.update()
        else:
            self.ed.select_range(ziel[1], ziel[2])
        self.ed.ensureCursorVisible()
