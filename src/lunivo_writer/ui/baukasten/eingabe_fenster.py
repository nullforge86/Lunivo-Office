"""Kleine Abfrage in der Seitenleiste: eine Frage, darunter eine Auswahl oder ein Textfeld, unten „Abbrechen“ und „OK“.

Ersatz für ``QInputDialog.getItem`` / ``getText``, die als freies Fenster über dem Text aufgingen. Gleiche Aufrufe, gleiche Rückgabe ``(Text, ok)``:

    n, ok = EingabeFenster.getItem(parent, "Zitierweise", "Zitierweise:", ["APA", "MLA"], aktuell=0)
    t, ok = EingabeFenster.getText(parent, "Seriendruckfeld", "Feldname:", text="Name")

Das Fenster ändert nichts selbst; der Aufrufer wertet das Ergebnis aus. Als ``PanelFaehig`` geht es in der rechten Seitenleiste auf (sonst als Fenster).
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
from lunivo_writer.ui.baukasten.formular_gitter import FormularGitter
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig


class EingabeFenster(PanelFaehig, QDialog):
    """Frage mit Auswahlliste (``eintraege``) oder, ohne Einträge, mit einem Textfeld."""

    def __init__(self, parent, titel: str, frage: str, eintraege: list[str] | None = None, aktuell: int = 0, text: str = ""):
        super().__init__(parent)
        self.setWindowTitle(titel)
        self._ist_liste = eintraege is not None
        v = QVBoxLayout(self)
        inhalt = QWidget(); g = FormularGitter(inhalt)
        f = QLabel(frage); f.setWordWrap(True)
        g.breit(f)
        if self._ist_liste:
            self.liste = QListWidget(); self.liste.setAccessibleName(titel)
            self.liste.setWordWrap(True); self.liste.setTextElideMode(Qt.ElideNone)
            self.liste.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            for e in eintraege:
                self.liste.addItem(QListWidgetItem(e))
            self.liste.setCurrentRow(max(0, min(aktuell, self.liste.count() - 1)))
            zeilen = max(1, min(self.liste.count(), 8))
            self.liste.setMinimumHeight(self.liste.sizeHintForRow(0) * zeilen + 8 if self.liste.count() else 40)
            self.liste.itemDoubleClicked.connect(lambda _i: self.accept())
            f.setBuddy(self.liste)
            g.breit(self.liste)
            self.feld = None
        else:
            self.feld = QLineEdit(text); self.feld.setMinimumHeight(30); self.feld.setAccessibleName(titel); self.feld.selectAll()
            self.feld.returnPressed.connect(self.accept)
            f.setBuddy(self.feld)
            g.breit(self.feld)
            self.liste = None
        v.addWidget(inhalt)
        fussleiste(self, v)
        self.resize(300, 0)

    def wert(self) -> str:
        """Der gewählte Eintrag oder der getippte Text."""
        if self._ist_liste:
            it = self.liste.currentItem()
            return it.text() if it is not None else ""
        return self.feld.text()

    @staticmethod
    def getItem(parent, titel: str, frage: str, eintraege: list[str], aktuell: int = 0, bearbeitbar: bool = False) -> tuple[str, bool]:
        """Wie ``QInputDialog.getItem``; (``bearbeitbar`` gibt es nicht — Auswahl nur aus der Liste)."""
        d = EingabeFenster(parent, titel, frage, list(eintraege), aktuell)
        ok = bool(d.exec()) and d.liste.currentItem() is not None
        return (d.wert() if ok else ""), ok

    @staticmethod
    def getText(parent, titel: str, frage: str, text: str = "") -> tuple[str, bool]:
        """Wie ``QInputDialog.getText``."""
        d = EingabeFenster(parent, titel, frage, None, text=text)
        ok = bool(d.exec())
        return (d.wert() if ok else ""), ok
