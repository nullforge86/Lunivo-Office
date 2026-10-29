"""Dialoge zum Einfügen: Formen, WordArt, Diagramm, Piktogramm, Formel, Deckblatt, Datum, Textbausteine."""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPalette, QPixmap, QPolygonF
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMessageBox, QPlainTextEdit, QPushButton, QSpinBox, QTableWidget, QTableWidgetItem,
    QSizePolicy, QVBoxLayout, QApplication, QWidget,
)

from lunivo_writer.editor import einfuegen as E
from lunivo_writer.ui.baukasten import FarbFeld
from lunivo_writer.ui.baukasten.formular_gitter import FormularGitter, abschnittstitel
from lunivo_writer.services import bausteine


from lunivo_writer.core.farben import Farbe
def _ok(dlg):
    return knopfzeile(dlg)


_Farbknopf = FarbFeld


from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig
from lunivo_writer.ui.baukasten.dialog_rahmen import knopfzeile
class _Vorschau(QLabel):
    """Vorschaubild, das sich der Breite anpasst (in der Seitenleiste kleiner, nie breiter als 460 px)."""

    def __init__(self):
        super().__init__()
        self._bild = None
        self.setMinimumHeight(120); self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.setStyleSheet(('background: white; border: 1px solid ' + Farbe.GRAU_HELL + ';'))

    def setze(self, img) -> None:
        self._bild = img
        self._neu()

    def _neu(self) -> None:
        if self._bild is None:
            return
        pm = QPixmap.fromImage(self._bild)
        b = min(460, max(40, self.width() - 8))
        if pm.width() > b:
            pm = pm.scaledToWidth(b, Qt.SmoothTransformation)
        self.setPixmap(pm)

    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        self._neu()


class VorschauMixin:
    def _vorschau_bauen(self, layout):
        self.vorschau = _Vorschau()
        layout.addWidget(self.vorschau) if not isinstance(layout, FormularGitter) else layout.breit(self.vorschau)

    def _zeige(self, img):
        self.vorschau.setze(img)


class FormDialog(PanelFaehig, QDialog, VorschauMixin):
    def __init__(self, parent, form: str | None = None):
        super().__init__(parent)
        self.setWindowTitle("Form einfügen")
        v = QVBoxLayout(self); f = FormularGitter(); v.addLayout(f)
        self.art = QComboBox(); self.art.addItems(E.FORMEN)
        if form:
            self.art.setCurrentText(form)
        self.fuell = _Farbknopf(Farbe.AKZENT_DUNKEL, "Füllfarbe"); self.linie = _Farbknopf("#1f3864", "Linienfarbe")
        self.breite = QSpinBox(); self.breite.setRange(20, 1200); self.breite.setValue(240)
        self.hoehe = QSpinBox(); self.hoehe.setRange(10, 1200); self.hoehe.setValue(140)
        self.strich = QDoubleSpinBox(); self.strich.setRange(0.5, 12); self.strich.setValue(2.0)
        self.text = QLineEdit()
        for lab, w in (("Form", self.art), ("Füllfarbe", self.fuell), ("Linienfarbe", self.linie), ("Breite (px)", self.breite),
                       ("Höhe (px)", self.hoehe), ("Linienstärke", self.strich), ("Text in der Form", self.text)):
            f.zeile(lab, w)
        self._vorschau_bauen(v)
        v.addWidget(_ok(self))
        for w in (self.art, self.breite, self.hoehe, self.strich, self.text):
            (w.currentTextChanged if isinstance(w, QComboBox) else w.textChanged if isinstance(w, QLineEdit) else w.valueChanged).connect(self.aktualisieren)
        self.fuell.clicked.connect(self.aktualisieren); self.linie.clicked.connect(self.aktualisieren)
        self.aktualisieren()

    def bild(self):
        return E.form_bild(self.art.currentText(), self.breite.value(), self.hoehe.value(), self.fuell.farbe, self.linie.farbe,
                           self.strich.value(), self.text.text())

    def daten(self):
        return {"form": self.art.currentText(), "fuell": self.fuell.farbe, "linie": self.linie.farbe,
                "strich": self.strich.value(), "text": self.text.text()}

    def aktualisieren(self, *_):
        self._zeige(self.bild())


class _LayoutGalerie(QWidget):
    """Galerie der SmartArt-Layouts: Bildchen (selbst gezeichnet) in einem KachelFeld, die Spaltenzahl folgt der Breite."""
    gewaehlt = Signal(str)
    KACHEL = 52

    def __init__(self, namen, zeichner, aktuell):
        super().__init__()
        self._namen, self._zeichner, self._aktuell, self._spalten = list(namen), zeichner, aktuell, 0
        self._v = QVBoxLayout(self); self._v.setContentsMargins(0, 0, 0, 0)
        self.feld = None
        self._bauen(3)

    def _bauen(self, spalten: int) -> None:
        from lunivo_writer.ui.baukasten.kachel_feld import KachelFeld
        if self.feld is not None:
            self._v.removeWidget(self.feld); self.feld.deleteLater()
        self._spalten = spalten
        self.feld = KachelFeld(spalten=spalten, groesse=QSize(self.KACHEL, self.KACHEL * 3 // 4), mit_text=False)
        for n in self._namen:
            self.feld.hinzu(n, n, lambda p, r, n=n: self._zeichner(p, r, n))
            self.feld.knoepfe[n].setAccessibleName(n)
        self.feld.gewaehlt.connect(self._klick)
        self.feld.setze(self._aktuell)
        self._v.addWidget(self.feld)
        self.updateGeometry()

    def _klick(self, name: str) -> None:
        self._aktuell = name
        self.gewaehlt.emit(name)

    def setze(self, name: str) -> None:
        self._aktuell = name; self.feld.setze(name)

    def aktuell(self) -> str:
        return self._aktuell

    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        s = max(1, min(len(self._namen), (self.width() + 4) // (self.KACHEL + 14)))
        if s != self._spalten:
            self._bauen(s)


def _layout_bildchen(p, r, name: str) -> None:
    """Kleines Bild eines SmartArt-Layouts (nur Umrisse in Palettenfarben)."""
    from PySide6.QtGui import QBrush, QPen
    pal = QApplication.palette()
    f = pal.color(QPalette.Highlight); f.setAlpha(170)
    p.setPen(QPen(pal.color(QPalette.Mid), 1)); p.setBrush(QBrush(f))
    r = r.adjusted(3, 3, -3, -3)
    w, h = r.width(), r.height()

    def kasten(x, y, bw, bh):
        p.drawRoundedRect(QRectF(r.left() + x * w, r.top() + y * h, bw * w, bh * h), 2, 2)
    if name == "Liste":
        for i in range(3):
            kasten(0.0 + i * 0.08, i * 0.36, 1 - i * 0.08, 0.26)
    elif name == "Prozess":
        for i in range(3):
            kasten(i * 0.37, 0.3, 0.26, 0.4)
            if i < 2:
                p.drawLine(QPointF(r.left() + (i * 0.37 + 0.27) * w, r.center().y()), QPointF(r.left() + (i * 0.37 + 0.36) * w, r.center().y()))
    elif name == "Hierarchie":
        kasten(0.33, 0.0, 0.34, 0.26)
        p.drawLine(QPointF(r.center().x(), r.top() + 0.26 * h), QPointF(r.center().x(), r.top() + 0.5 * h))
        p.drawLine(QPointF(r.left() + 0.15 * w, r.top() + 0.5 * h), QPointF(r.left() + 0.85 * w, r.top() + 0.5 * h))
        for x in (0.0, 0.35, 0.7):
            p.drawLine(QPointF(r.left() + (x + 0.15) * w, r.top() + 0.5 * h), QPointF(r.left() + (x + 0.15) * w, r.top() + 0.64 * h))
            kasten(x, 0.64, 0.3, 0.26)
    elif name == "Zyklus":
        for i in range(4):
            a = math.radians(i * 90 - 90)
            c = QPointF(r.center().x() + math.cos(a) * w * 0.3, r.center().y() + math.sin(a) * h * 0.32)
            p.drawEllipse(c, w * 0.12, w * 0.12)
    elif name == "Pyramide":
        for i in range(3):
            y0, y1 = i / 3 + 0.02, (i + 1) / 3 - 0.02
            b0, b1 = y0 * 0.5, y1 * 0.5
            p.drawPolygon(QPolygonF([QPointF(r.center().x() - b0 * w, r.top() + y0 * h), QPointF(r.center().x() + b0 * w, r.top() + y0 * h),
                                     QPointF(r.center().x() + b1 * w, r.top() + y1 * h), QPointF(r.center().x() - b1 * w, r.top() + y1 * h)]))
    else:
        kasten(0.1, 0.1, 0.8, 0.8)


class SmartArtDialog(PanelFaehig, QDialog, VorschauMixin):
    """SmartArt auswählen (wie WPS „Grafik auswählen“): Galerie der Layouts, darunter Name, Beschreibung und Vorschau, OK.
    Beim Bearbeiten (``daten`` gegeben) kommen Farben und der eingerückte Text (zwei Leerzeichen = eine Ebene tiefer) dazu."""
    BESCHREIBUNG = {
        "Liste": "Zeigt nicht aufeinanderfolgende Informationen oder Gruppen von Informationen untereinander. Eingerückte Zeilen bilden Unterpunkte.",
        "Prozess": "Zeigt die Schritte eines Ablaufs oder einer Zeitachse nacheinander, durch Pfeile verbunden.",
        "Hierarchie": "Stellt hierarchische Informationen oder Berichtsbeziehungen dar, etwa den Aufbau einer Organisation. Eingerückte Zeilen sind untergeordnet.",
        "Zyklus": "Zeigt einen fortlaufenden Prozess, dessen Schritte im Kreis wieder von vorn beginnen.",
        "Pyramide": "Zeigt Beziehungen, die nach oben schmaler werden, etwa Grundlagen unten und Spitze oben.",
    }

    def __init__(self, parent, daten: dict | None = None):
        super().__init__(parent)
        from lunivo_writer.editor import smartart as SA
        self.SA = SA
        self.setWindowTitle("SmartArt-Grafik auswählen")
        v = QVBoxLayout(self)
        bearbeiten = bool(daten)
        daten = daten or {}
        start = daten.get("layout", "Prozess")
        self.galerie = _LayoutGalerie(SA.LAYOUTS, _layout_bildchen, start)
        v.addWidget(abschnittstitel("Layout")); v.addWidget(self.galerie)
        self.name = QLabel(); self.name.setStyleSheet("font-weight: 600;")
        self.beschreibung = QLabel(); self.beschreibung.setWordWrap(True)
        self.beschreibung.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        v.addWidget(self.name); v.addWidget(self.beschreibung)
        self._vorschau_bauen(v)
        self.farben = QComboBox(); self.farben.addItems(list(SA.FARBEN))
        self.farben.setCurrentText(daten.get("farben", "Blau"))
        self.text = QPlainTextEdit(daten.get("text") or SA.MUSTER[start])
        self.text.setMinimumHeight(110)
        self.bearbeiten = QWidget()
        f = FormularGitter(); b = QVBoxLayout(self.bearbeiten); b.setContentsMargins(0, 0, 0, 0); b.addLayout(f)
        f.zeile("Farben", self.farben)
        f.breit(QLabel("Text (eine Zeile je Punkt)")); f.breit(self.text)
        v.addWidget(self.bearbeiten); self.bearbeiten.setVisible(bearbeiten)
        v.addStretch(1)
        v.addWidget(_ok(self))
        self.galerie.gewaehlt.connect(self._layout)
        self.farben.currentTextChanged.connect(self.aktualisieren)
        self.text.textChanged.connect(self.aktualisieren)
        self._eigener_text = bool(daten.get("text"))
        self.aktualisieren()

    @property
    def layout_(self):
        return self.galerie

    def _layout(self, name):
        if not self._eigener_text or self.text.toPlainText() in self.SA.MUSTER.values():
            self.text.blockSignals(True); self.text.setPlainText(self.SA.MUSTER.get(name, "")); self.text.blockSignals(False)
        self.aktualisieren()

    def daten(self):
        return {"layout": self.galerie.aktuell(), "farben": self.farben.currentText(), "text": self.text.toPlainText()}

    def aktualisieren(self, *_):
        d = self.daten()
        self.name.setText(d["layout"]); self.beschreibung.setText(self.BESCHREIBUNG.get(d["layout"], ""))
        self._zeige(self.SA.zeichnen(d))


class WordArtDialog(PanelFaehig, QDialog, VorschauMixin):
    def __init__(self, parent, text: str = "Ihr Text", stil: str = "Verlauf", farbe: str = Farbe.AKZENT, vorlage: int | None = None):
        """``vorlage``: Nummer eines Galerie-Stils (``E.WORDART_VORLAGEN``); ohne sie gelten ``stil`` und ``farbe``."""
        super().__init__(parent)
        self.setWindowTitle("WordArt")
        v = QVBoxLayout(self); f = FormularGitter(); v.addLayout(f)
        self.text = QLineEdit(text or "Ihr Text"); self.stil = QComboBox(); self.stil.addItems(E.WORDART_STILE)
        self.stil.setCurrentText(stil)
        self.vorlage = QComboBox(); self.vorlage.addItem("(eigener Stil)")
        self.vorlage.addItems([n for n, *_r in E.WORDART_VORLAGEN])
        self.vorlage.setCurrentIndex(0 if vorlage is None else vorlage + 1)
        self.schrift = QLineEdit("Liberation Sans"); self.pt = QSpinBox(); self.pt.setRange(12, 200); self.pt.setValue(48)
        self.farbe = _Farbknopf(farbe)
        for lab, w in (("Text", self.text), ("Formatvorlage", self.vorlage), ("Stil", self.stil), ("Schriftart", self.schrift), ("Größe (pt)", self.pt), ("Farbe", self.farbe)):
            f.zeile(lab, w)
        self._vorschau_bauen(v); v.addWidget(_ok(self))
        self.text.textChanged.connect(self.aktualisieren); self.stil.currentTextChanged.connect(self.aktualisieren)
        self.vorlage.currentIndexChanged.connect(self.aktualisieren)
        self.schrift.textChanged.connect(self.aktualisieren); self.pt.valueChanged.connect(self.aktualisieren)
        self.farbe.clicked.connect(self.aktualisieren)
        self.aktualisieren()

    def vorlage_nr(self) -> int | None:
        i = self.vorlage.currentIndex() - 1
        return i if i >= 0 else None

    def bild(self):
        return E.wordart_bild(self.text.text() or " ", self.stil.currentText(), self.schrift.text() or "Liberation Sans",
                              self.pt.value(), self.farbe.farbe, self.vorlage_nr())

    def aktualisieren(self, *_):
        self._zeige(self.bild())


class DiagrammDatenDialog(PanelFaehig, QDialog):
    """Titel und Daten des Diagramms (Unterfenster von „Diagramm einfügen“): erste Spalte Rubriken, weitere Spalten Datenreihen."""

    def __init__(self, parent, titel: str, kategorien: list[str], reihen: dict[str, list[float]]):
        super().__init__(parent)
        from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
        from PySide6.QtWidgets import QWidget
        from lunivo_writer.ui.baukasten.formular_gitter import FlussLayout, FormularGitter
        self.setWindowTitle("Daten bearbeiten")
        v = QVBoxLayout(self)
        kopf = QWidget(); g = FormularGitter(kopf)
        self.titel = QLineEdit(titel); self.titel.setMinimumHeight(34); g.zeile("&Titel:", self.titel)
        v.addWidget(kopf)
        self.tab = QTableWidget(len(kategorien), len(reihen) + 1)
        self.tab.setHorizontalHeaderLabels(["Rubrik"] + list(reihen))
        self.tab.setMinimumHeight(180)
        for r, k in enumerate(kategorien):
            self.tab.setItem(r, 0, QTableWidgetItem(k))
            for c, werte in enumerate(reihen.values(), 1):
                self.tab.setItem(r, c, QTableWidgetItem(f"{werte[r]:g}" if r < len(werte) else "0"))
        v.addWidget(self.tab)
        z = FlussLayout(6)
        for text, fn in (("Zeile hinzufügen", lambda: self.tab.setRowCount(self.tab.rowCount() + 1)),
                         ("Zeile entfernen", lambda: self.tab.setRowCount(max(1, self.tab.rowCount() - 1))),
                         ("Reihe hinzufügen", self._reihe_dazu),
                         ("Reihe entfernen", lambda: self.tab.setColumnCount(max(2, self.tab.columnCount() - 1)))):
            b = QPushButton(text); b.setMinimumHeight(34); b.clicked.connect(fn); z.addWidget(b)
        v.addLayout(z)
        fussleiste(self, v)
        self.resize(520, 360)

    def _reihe_dazu(self) -> None:
        n = self.tab.columnCount()
        self.tab.setColumnCount(n + 1); self.tab.setHorizontalHeaderItem(n, QTableWidgetItem(f"Datenreihe {n}"))

    def daten(self) -> tuple[str, list[str], dict[str, list[float]]]:
        kat, reihen = [], {}
        for c in range(1, self.tab.columnCount()):
            kopf = self.tab.horizontalHeaderItem(c)
            reihen[kopf.text() if kopf else f"Datenreihe {c}"] = []
        for r in range(self.tab.rowCount()):
            k = self.tab.item(r, 0)
            kat.append(k.text() if k else "")
            for c, name in enumerate(reihen, 1):
                it = self.tab.item(r, c)
                try:
                    reihen[name].append(float((it.text() if it else "0").replace(",", ".")))
                except ValueError:
                    reihen[name].append(0.0)
        return self.titel.text(), kat, reihen


class PiktogrammDialog(PanelFaehig, QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Piktogramm einfügen")
        self.resize(520, 520)
        from lunivo_writer.ui.widgets import icons
        v = QVBoxLayout(self)
        self.suche = QLineEdit(); self.suche.setPlaceholderText("Suchen (englische Symbolnamen, z. B. heart, home, star)")
        v.addWidget(self.suche)
        self.liste = QListWidget(); self.liste.setViewMode(QListWidget.IconMode); self.liste.setIconSize(__import__("PySide6.QtCore", fromlist=["QSize"]).QSize(40, 40))
        self.liste.setResizeMode(QListWidget.Adjust); self.liste.setGridSize(__import__("PySide6.QtCore", fromlist=["QSize"]).QSize(90, 70))
        self.liste.setUniformItemSizes(True); self.liste.itemDoubleClicked.connect(lambda _: self.accept())
        v.addWidget(self.liste)
        z = QHBoxLayout(); self.farbe = _Farbknopf("#1f2328"); z.addWidget(QLabel("Farbe:")); z.addWidget(self.farbe); z.addStretch(1); v.addLayout(z)
        v.addWidget(_ok(self))
        self.namen = sorted(icons.katalog())
        self.suche.textChanged.connect(self._fuellen)
        self.farbe.clicked.connect(lambda: self._fuellen(self.suche.text()))
        self._fuellen("")

    def _fuellen(self, q):
        from lunivo_writer.ui.widgets import icons
        self.liste.clear()
        q = (q or "").lower().strip()
        for n in self.namen:
            if q and q not in n.lower():
                continue
            if self.liste.count() >= 240:
                break
            from PySide6.QtGui import QIcon
            it = QListWidgetItem(QIcon(QPixmap.fromImage(icons.katalog_bild(n, 40, self.farbe.farbe))), n)
            it.setData(Qt.UserRole, n)
            self.liste.addItem(it)

    def ergebnis(self):
        it = self.liste.currentItem()
        return (it.data(Qt.UserRole), self.farbe.farbe) if it else (None, None)


class FormelDialog(PanelFaehig, QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Formel")
        v = QVBoxLayout(self)
        hilfe = QLabel("Schreibweise: hoch  a^2 oder a^{n+1}  · tief  x_1  · Wurzel  sqrt(x)  · Bruch  frac(a,b)  · Griechisch  \\alpha \\pi \\Sigma  ·  \\infty \\leq \\geq \\neq \\pm \\times")
        hilfe.setWordWrap(True); v.addWidget(hilfe)
        self.eingabe = QLineEdit("E = m c^2"); v.addWidget(self.eingabe)
        self.vorschau = _Vorschau()                                            # verkleinert lange Formeln auf die Breite
        v.addWidget(self.vorschau); v.addWidget(_ok(self))
        self.eingabe.textChanged.connect(self._zeige); self._zeige()

    def _zeige(self, *_):
        from PySide6.QtGui import QColor, QPainter, QPixmap
        img = E.formel_bild(self.eingabe.text())
        pm = QPixmap(img.width() + 16, img.height() + 12); pm.fill(QColor("white"))
        p = QPainter(pm); p.drawImage(8, 6, img); p.end()
        self.vorschau.setze(pm.toImage())


class DeckblattDialog(PanelFaehig, QDialog):
    def __init__(self, parent, autor: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Deckblatt")
        f = QFormLayout(self)
        self.vorlage = QComboBox(); self.vorlage.addItems(E.DECKBLATT_VORLAGEN)
        self.titel = QLineEdit("Titel des Dokuments"); self.unter = QLineEdit(); self.autor = QLineEdit(autor)
        self.datum = QLineEdit(E.datum_text("d. MMMM yyyy"))
        for lab, w in (("Vorlage", self.vorlage), ("Titel", self.titel), ("Untertitel", self.unter), ("Autor", self.autor), ("Datum", self.datum)):
            f.addRow(lab, w)
        f.addRow(_ok(self))


class DatumDialog(PanelFaehig, QDialog):
    """Wie die Vorlage: links „Verfügbare Formate“, rechts „Sprache“, darunter „Automatisch aktualisieren“ (dann als Datumsfeld)."""

    def __init__(self, parent, sprache: str = "de_DE"):
        super().__init__(parent)
        from PySide6.QtWidgets import QCheckBox, QGridLayout
        from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
        self.setWindowTitle("Datum und Uhrzeit")
        v = QVBoxLayout(self)
        g = QGridLayout(); g.setHorizontalSpacing(12)
        self.liste = QListWidget(); self.liste.setAccessibleName("Verfügbare Formate"); self.liste.setMinimumWidth(220)
        self.sprache = QComboBox(); self.sprache.setMinimumHeight(34); self.sprache.setAccessibleName("Sprache")
        for k, (t, _f) in E.DATUM_SPRACHEN.items():
            self.sprache.addItem(t, k)
        self.sprache.setCurrentIndex(max(0, self.sprache.findData(sprache)))
        self.auto = QCheckBox("&Automatisch aktualisieren")
        self.auto.setToolTip("Das Datum wird als Feld gespeichert; Textprogramme rechnen es beim Öffnen neu (in DOCX).")
        t1 = QLabel("&Verfügbare Formate:"); t1.setBuddy(self.liste)
        t2 = QLabel("&Sprache:"); t2.setBuddy(self.sprache)
        g.addWidget(t1, 0, 0); g.addWidget(self.liste, 1, 0, 2, 1)
        g.addWidget(t2, 0, 1); g.addWidget(self.sprache, 1, 1, Qt.AlignTop); g.addWidget(self.auto, 2, 1, Qt.AlignBottom)
        g.setRowStretch(2, 1)
        v.addLayout(g)
        fussleiste(self, v)
        self.sprache.currentIndexChanged.connect(self._fuellen)
        self.liste.itemDoubleClicked.connect(lambda _: self.accept())
        self._fuellen()

    def _loc(self) -> str:
        return self.sprache.currentData()

    def _fuellen(self, *_):
        self.liste.clear()
        for fmt in E.DATUM_SPRACHEN[self._loc()][1]:
            it = QListWidgetItem(E.datum_text(fmt, self._loc())); it.setData(Qt.UserRole, fmt); self.liste.addItem(it)
        self.liste.setCurrentRow(0)

    def ergebnis(self) -> str:
        it = self.liste.currentItem()
        return it.text() if it else ""

    def feldanweisung(self) -> str | None:
        """Bei „Automatisch aktualisieren“ die Feldanweisung (DATE/TIME), sonst None."""
        it = self.liste.currentItem()
        return E.datum_feldanweisung(it.data(Qt.UserRole)) if it and self.auto.isChecked() else None


class BausteinDialog(PanelFaehig, QDialog):
    """Textbausteine: links die Liste (mitgelieferte und eigene), rechts die Vorschau; Name und Kürzel oben. „Aus Markierung …“ merkt den markierten Text
    samt Formatierung, „Einfügen“ setzt den Baustein an die Schreibmarke. Das Kürzel plus F3 setzt ihn direkt ein."""

    def __init__(self, parent, ed):
        super().__init__(parent)
        from PySide6.QtWidgets import QLineEdit, QTextBrowser
        self.ed = ed
        self.setWindowTitle("Textbausteine")
        self.resize(840, 600)
        v = QVBoxLayout(self)
        from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
        from lunivo_writer.ui.baukasten.formular_gitter import FormularGitter, abschnittstitel
        felder = FormularGitter(); v.addLayout(felder)
        self.name = QLineEdit(); self.kuerzel = QLineEdit()
        felder.zeile("Name:", self.name)
        felder.zeile("Kürzel:", self.kuerzel)
        v.addWidget(abschnittstitel("Bausteine"))
        self.liste = QListWidget(); self.liste.itemDoubleClicked.connect(lambda _: self._einfuegen())
        self.liste.currentItemChanged.connect(lambda *_: self._zeigen())
        self.liste.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.liste.setWordWrap(True)
        self.liste.setTextElideMode(Qt.ElideNone); self.liste.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.liste.setMinimumHeight(150)
        v.addWidget(self.liste, 3)
        v.addWidget(abschnittstitel("Vorschau"))
        self.vorschau = QTextBrowser(); self.vorschau.setFont(QFont("Liberation Serif", 12))
        self.vorschau.document().setDocumentMargin(12); self.vorschau.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.vorschau.setMinimumHeight(150)
        v.addWidget(self.vorschau, 4)
        h = QLabel("Eigene kommen aus dem Markierten, die übrigen sind mitgeliefert. «So gesetzte Stellen» sind Lücken: Tab springt von einer zur nächsten, Tippen ersetzt sie.")
        h.setWordWrap(True); h.setStyleSheet("color: palette(mid); font-size: 9pt;"); h.setContentsMargins(0, 4, 0, 4)
        v.addWidget(h)
        self.aus_markierung = QPushButton("Aus Markierung …"); self.aus_markierung.clicked.connect(self._neu)
        self.loeschen = QPushButton("Löschen"); self.loeschen.clicked.connect(self._weg)
        self.einfuegen_knopf = fussleiste(self, v, self.aus_markierung, self.loeschen, nur_ok=True, ok_text="Einfügen", bei_ok=self._einfuegen)
        self._fuellen()

    def _fuellen(self, wahl: str | None = None) -> None:
        self.liste.clear()
        gruppen = (("Standard", bausteine.standard()), ("Eigene", bausteine.laden()))
        for titel, eintraege in gruppen:
            if not eintraege:
                continue
            kopf = QListWidgetItem(titel.upper()); kopf.setFlags(Qt.NoItemFlags)
            f = kopf.font(); f.setPointSizeF(f.pointSizeF() * 0.85); kopf.setFont(f); self.liste.addItem(kopf)
            for b in eintraege:
                it = QListWidgetItem(b["name"]); it.setData(Qt.UserRole, b); self.liste.addItem(it)
                if wahl and b["name"] == wahl:
                    self.liste.setCurrentItem(it)
        if self.liste.currentItem() is None:
            for i in range(self.liste.count()):
                if self.liste.item(i).data(Qt.UserRole):
                    self.liste.setCurrentRow(i); break
        self._zeigen()

    def _aktuell(self) -> dict | None:
        it = self.liste.currentItem()
        return it.data(Qt.UserRole) if it else None

    def _zeigen(self) -> None:
        b = self._aktuell()
        self.einfuegen_knopf.setEnabled(b is not None)
        self.loeschen.setEnabled(bool(b) and not b.get("standard"))
        if b is None:
            self.vorschau.clear()
            return
        self.name.setText(b["name"]); self.kuerzel.setText(b.get("kuerzel", ""))
        if b.get("absaetze"):
            from lunivo_writer.editor.textdaten import daten_zu_fragment
            from PySide6.QtGui import QTextCursor
            self.vorschau.clear()
            c = QTextCursor(self.vorschau.document()); c.insertFragment(daten_zu_fragment(b["absaetze"]))
        else:
            self.vorschau.setPlainText(b.get("text", ""))

    def _neu(self) -> None:
        from PySide6.QtGui import QTextDocumentFragment
        from PySide6.QtWidgets import QInputDialog
        c = self.ed.textCursor()
        if not c.hasSelection():
            QMessageBox.information(self, "Textbaustein", "Bitte zuerst den Text markieren, der gemerkt werden soll.")
            return
        n = self.name.text().strip()
        if not n:
            n, ok = QInputDialog.getText(self, "Textbaustein", "Name des Bausteins:")
            if not ok or not n.strip():
                return
            n = n.strip()
        if any(b["name"] == n for b in bausteine.standard()):
            QMessageBox.information(self, "Textbaustein", "Dieser Name gehört zu einem mitgelieferten Baustein. Bitte einen anderen wählen.")
            return
        bausteine.hinzufuegen(n, QTextDocumentFragment(c), self.kuerzel.text())
        self._fuellen(n)

    def _weg(self) -> None:
        b = self._aktuell()
        if b and not b.get("standard"):
            bausteine.entfernen(b["name"]); self._fuellen()

    def _einfuegen(self) -> None:
        b = self._aktuell()
        if b:
            bausteine.einfuegen(self.ed.textCursor(), b); self.ed.document().setModified(True); self.accept()


from lunivo_writer.ui.dialogs.diagramm_fenster import DiagrammDialog  # noqa: E402,F401  eigenes Modul, hier für ältere Aufrufer
