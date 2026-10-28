"""Der Bereich „Auswahl“ (Start ▸ Auswählen ▸ Auswahlbereich) als Baustein: alle Bilder, Formen, Diagramme und Tabellen des Dokuments in einer
Liste; ein Klick markiert das Objekt im Text (dann erscheinen seine Werkzeuge). Der Bereich ändert nichts am Dokument.

    ausfuehren(AuswahlBereich(parent, editor))       # Zusatzfenster in der Seitenleiste, offen bis „Schließen“
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QDialog, QLabel, QListWidget, QListWidgetItem, QVBoxLayout

from lunivo_writer.ui.baukasten.dialog_rahmen import knopfzeile
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig


def objekte(ed) -> list[tuple[str, int, int]]:
    """[(Beschriftung, von, bis)] aller Objekte in Dokumentreihenfolge."""
    import json
    from lunivo_writer.editor import gehe_zu as G
    from lunivo_writer.editor.zusatz import P_OBJEKT
    namen = {"form": "Form", "zeichenbereich": "Zeichenbereich", "wordart": "WordArt", "diagramm": "Diagramm", "smartart": "SmartArt", "formel": "Formel", "piktogramm": "Piktogramm"}
    out, zaehler = [], {}
    for f in G._fragmente(ed.document()):
        cf = f.charFormat()
        if not cf.isImageFormat():
            continue
        art = "Bild"
        if cf.hasProperty(P_OBJEKT):
            try:
                art = namen.get(json.loads(cf.stringProperty(P_OBJEKT)).get("art", ""), "Objekt")
            except ValueError:
                art = "Objekt"
        for i in range(f.length()):
            zaehler[art] = zaehler.get(art, 0) + 1
            out.append((f"{art} {zaehler[art]}", f.position() + i, f.position() + i + 1))
    for i, t in enumerate(sorted(G._tabellen(ed.document().rootFrame()), key=lambda t: t.firstPosition()), start=1):
        out.append((f"Tabelle {i}", t.firstPosition(), t.lastPosition()))
    return sorted(out, key=lambda x: x[1])


class AuswahlBereich(PanelFaehig, QDialog):
    def __init__(self, parent=None, ed=None):
        super().__init__(parent)
        self.setWindowTitle("Auswahl")
        self.ed = ed
        v = QVBoxLayout(self)
        v.addWidget(QLabel("Objekte im Dokument:"))
        self.liste = QListWidget(); self.liste.setMinimumHeight(260)
        v.addWidget(self.liste, 1)
        self.leer = QLabel("Das Dokument enthält keine Bilder, Formen oder Tabellen."); self.leer.setWordWrap(True)
        v.addWidget(self.leer)
        v.addWidget(knopfzeile(self, schliessen=True))
        self.liste.itemClicked.connect(self._markieren)
        self.fuellen()

    def fuellen(self) -> None:
        self.liste.clear()
        for name, von, bis in objekte(self.ed) if self.ed is not None else []:
            it = QListWidgetItem(name); it.setData(Qt.UserRole, (von, bis)); self.liste.addItem(it)
        self.leer.setVisible(self.liste.count() == 0)

    def _markieren(self, it: QListWidgetItem) -> None:
        von, bis = it.data(Qt.UserRole)
        c = QTextCursor(self.ed.document()); c.setPosition(von); c.setPosition(bis, QTextCursor.KeepAnchor)
        self.ed.setTextCursor(c); self.ed.ensureCursorVisible()
