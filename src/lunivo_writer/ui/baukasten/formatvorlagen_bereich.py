"""Der Bereich „Formatvorlagen und Formatierung“ (Start ▸ Einstellungen) als Baustein — wie der Bereich der Vorlage in der rechten Seitenleiste:
oben die Vorlage des Absatzes an der Schreibmarke, „Neue Formatvorlage …“ und „Formatierung löschen“, darunter alle Vorlagen als Liste
(in ihrer eigenen Schrift), unten „Anzeigen“ und „Vorschau anzeigen“.

    d = FormatvorlagenBereich(parent, get_editor, anwenden, neu)     # anwenden(name), neu() öffnet „Neue Formatvorlage“
    ausfuehren(d)                                                    # bleibt offen, bis man „Schließen“ drückt

Ein Klick auf eine Vorlage wirkt sofort; der Bereich selbst formatiert nichts, er ruft ``anwenden``.
"""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QStyledItemDelegate, QVBoxLayout,
)

from lunivo_writer.ui.baukasten.dialog_rahmen import knopfzeile
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig

ANZEIGEN = (("gueltig", "Gültige Formatvorlagen"), ("verwendet", "Verwendete Formatvorlagen"), ("alle", "Alle Formatvorlagen"))


def vorlagen_namen(art: str = "gueltig", ed=None) -> list[str]:
    """Die Namen für die Liste: gültige (Katalog und eigene), verwendete (im Dokument) oder alle."""
    from lunivo_writer.editor import stile
    from lunivo_writer.ui.ribbon.ribbon_bar import STILE_KATALOG
    alle = STILE_KATALOG + [n for n in stile.namen() if n not in STILE_KATALOG]
    if art != "verwendet" or ed is None:
        return alle
    b, da = ed.document().firstBlock(), set()
    while b.isValid():
        da.add(ed._stil_name(b.blockFormat())); b = b.next()
    return [n for n in alle if n in da or (n == "Standard" and "Fließtext" in da)]


def vorlagen_schrift(name: str, vorschau: bool = True) -> QFont:
    """Die Schrift, in der eine Vorlage in Listen erscheint (Größe gedämpft, damit die Liste ruhig bleibt)."""
    from lunivo_writer.editor import stile
    f = QFont()
    if not vorschau:
        return f
    d = stile.definition(name)
    if d.get("schrift"):
        f.setFamily(d["schrift"])
    f.setPointSizeF(min(15.0, max(9.0, float(d.get("groesse") or 10) * 0.8)))
    f.setBold(name.startswith("Überschrift") or name == "Titel" or bool(d.get("fett")))
    f.setItalic(name in ("Untertitel", "Zitat") or bool(d.get("kursiv")))
    return f


class _Absatzmarke(QStyledItemDelegate):
    """Zeile der Liste mit dem Zeichen ↵ rechts (Absatzvorlage), wie in der Vorlage; etwas Luft über und unter dem Namen."""

    def sizeHint(self, option, index):
        s = super().sizeHint(option, index)
        return s.expandedTo(QSize(0, s.height() + 12))

    def paint(self, p, option, index):
        super().paint(p, option, index)
        p.save(); p.setPen(option.palette.color(QPalette.Mid))
        p.drawText(option.rect.adjusted(0, 0, -8, 0), Qt.AlignRight | Qt.AlignVCenter, "↵")
        p.restore()


class FormatvorlagenBereich(PanelFaehig, QDialog):
    def __init__(self, parent=None, get_editor: Callable | None = None, anwenden: Callable[[str], None] | None = None,
                 neu: Callable[[], None] | None = None):
        super().__init__(parent)
        self.setWindowTitle("Formatvorlagen und Formatierung")
        self.get_editor = get_editor or (lambda: None)
        self._anwenden, self._neu = anwenden, neu
        v = QVBoxLayout(self); v.setSpacing(8)
        self.aktuell = QComboBox(); self.aktuell.setMinimumHeight(34)
        v.addWidget(self.aktuell)
        z = QHBoxLayout()
        self.neu_knopf = QPushButton("Neue Formatvorlage …"); self.loeschen = QPushButton("Formatierung löschen")
        for k in (self.neu_knopf, self.loeschen):
            k.setMinimumHeight(34); z.addWidget(k)
        v.addLayout(z)
        titel = QLabel("Formatierung auswählen"); titel.setStyleSheet("color: palette(highlight);")
        v.addWidget(titel)
        self.liste = QListWidget(); self.liste.setMinimumHeight(260); self.liste.setItemDelegate(_Absatzmarke(self.liste))
        v.addWidget(self.liste, 1)
        az = QHBoxLayout(); az.addWidget(QLabel("Anzeigen:"))
        self.anzeigen = QComboBox(); self.anzeigen.setMinimumHeight(34)
        for k, t in ANZEIGEN:
            self.anzeigen.addItem(t, k)
        az.addWidget(self.anzeigen, 1); v.addLayout(az)
        self.vorschau = QCheckBox("Vorschau anzeigen"); self.vorschau.setChecked(True); v.addWidget(self.vorschau)
        v.addWidget(knopfzeile(self, schliessen=True))
        self.liste.itemClicked.connect(lambda it: self.waehle(it.data(Qt.UserRole)))
        self.aktuell.activated.connect(lambda _i: self.waehle(self.aktuell.currentText()))
        self.anzeigen.currentIndexChanged.connect(lambda _i: self.fuellen())
        self.vorschau.toggled.connect(lambda _a: self.fuellen())
        self.neu_knopf.clicked.connect(self._neu_vorlage)
        self.loeschen.clicked.connect(self._formatierung_loeschen)
        self.fuellen()

    def _stil_jetzt(self) -> str:
        ed = self.get_editor()
        n = ed.current_style() if ed is not None else "Standard"
        return "Standard" if n in ("Fließtext", "") else n

    def fuellen(self) -> None:
        from lunivo_writer.editor import stile
        jetzt = self._stil_jetzt()
        namen = vorlagen_namen(self.anzeigen.currentData(), self.get_editor())
        self.liste.clear(); self.aktuell.clear()
        for n in namen:
            it = QListWidgetItem(n); it.setData(Qt.UserRole, n); it.setFont(vorlagen_schrift(n, self.vorschau.isChecked()))
            it.setToolTip(n)
            farbe = stile.definition(n).get("farbe")
            if farbe and self.vorschau.isChecked():
                it.setForeground(QColor(farbe))
            self.liste.addItem(it)
            self.aktuell.addItem(n)
            if n == jetzt:
                self.liste.setCurrentItem(it)
        self.aktuell.setCurrentText(jetzt)

    def waehle(self, name: str) -> None:
        if name and self._anwenden is not None:
            self._anwenden(name)
        self.aktuell.setCurrentText(name)

    def _neu_vorlage(self) -> None:
        if self._neu is not None:
            self._neu()
        self.fuellen()

    def _formatierung_loeschen(self) -> None:
        ed = self.get_editor()
        if ed is not None:
            ed.clear_formatting()
            if self._anwenden is not None:
                self._anwenden("Standard")
        self.fuellen()
