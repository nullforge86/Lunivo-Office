"""„Diagramm einfügen“ nach Kays Vorlage (einfuegen/07 und Prüfkatalog): links die Diagrammarten mit eigenen Bildchen, oben die
Untertypen als Bildchen, darunter Name und Vorschau. Bei „Kombination …“ steht unter der Vorschau die Tabelle Datenreihenname /
Diagrammtyp / Sekundärachse; wer dort etwas ändert, wählt „Benutzerdefinierte Kombination“.

    d = DiagrammDialog(parent)      # if d.exec(): d.bild() → QImage, d.daten() → dict (art, titel, kategorien, reihen, kombi, farben)

Das Fenster ändert das Dokument nicht. „Daten bearbeiten …“ öffnet Titel und Werte als Unterfenster im selben Stapel.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap, QPolygonF
from PySide6.QtWidgets import (
    QBoxLayout, QButtonGroup, QCheckBox, QComboBox, QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QListView, QListWidget,
    QListWidgetItem, QPushButton, QToolButton, QVBoxLayout, QWidget,
)

from lunivo_writer.core.farben import Farbe
from lunivo_writer.editor import diagramm as D
from lunivo_writer.ui.baukasten.formular_gitter import FlussLayout
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig

_BLAU, _ORANGE, _GRAU = QColor("#4a8fd8"), QColor("#ef8a3c"), QColor("#7a8086")


def art_symbol(sym: str, px: int = 22) -> QIcon:
    """Eigenes, gut erkennbares Bildchen je Diagrammart (Säulen, Linienzug, Torte, Balken, Fläche, Punkte, Kurs, Netz,
    Säulen mit Linie, Vorlagenblatt)."""
    pm = QPixmap(px, px); pm.fill(Qt.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    s = px / 22.0
    p.scale(s, s)
    linie = QPen(QColor("#3c4043"), 1.4)
    p.setPen(linie)
    p.drawLine(3, 19, 20, 19)
    if sym in ("saeule", "kombination"):
        for x, h, c in ((5, 9, _BLAU), (10, 13, _ORANGE), (15, 7, _BLAU)):
            p.fillRect(QRectF(x, 19 - h, 3.5, h), c)
        if sym == "kombination":
            p.setPen(QPen(_GRAU.darker(130), 1.6)); p.drawPolyline(QPolygonF([QPointF(4, 12), QPointF(10, 9), QPointF(18, 3)]))
    elif sym == "linie":
        p.setPen(QPen(_BLAU, 1.8)); p.drawPolyline(QPolygonF([QPointF(3, 15), QPointF(8, 9), QPointF(13, 12), QPointF(19, 4)]))
    elif sym == "kreis":
        r = QRectF(3, 2, 16, 16)
        p.setPen(QPen(Qt.white, 1)); p.setBrush(_BLAU); p.drawPie(r, 90 * 16, 220 * 16)
        p.setBrush(_ORANGE); p.drawPie(r, 310 * 16, 80 * 16); p.setBrush(_GRAU); p.drawPie(r, 30 * 16, 60 * 16)
    elif sym == "balkenquer":
        p.drawLine(3, 2, 3, 19)
        for y, w, c in ((4, 12, _BLAU), (9, 16, _ORANGE), (14, 8, _BLAU)):
            p.fillRect(QRectF(4, y, w, 3.5), c)
    elif sym == "flaeche":
        pfad = QPainterPath(QPointF(3, 19)); pfad.lineTo(3, 12); pfad.lineTo(9, 7); pfad.lineTo(14, 11); pfad.lineTo(20, 4)
        pfad.lineTo(20, 19); pfad.closeSubpath()
        p.setPen(QPen(_BLAU.darker(120), 1)); p.setBrush(QColor(74, 143, 216, 160)); p.drawPath(pfad)
    elif sym == "punktwolke":
        p.drawLine(3, 2, 3, 19)
        p.setPen(Qt.NoPen)
        for x, y, c in ((6, 14, _BLAU), (9, 9, _ORANGE), (12, 12, _BLAU), (15, 6, _ORANGE), (18, 9, _BLAU)):
            p.setBrush(c); p.drawEllipse(QPointF(x, y), 1.8, 1.8)
    elif sym == "kurs":
        for x, hoch, tief, a, b in ((6, 4, 16, 7, 12), (11, 3, 14, 5, 10), (16, 6, 17, 9, 14)):
            p.setPen(QPen(QColor("#3c4043"), 1.2)); p.drawLine(QPointF(x, hoch), QPointF(x, tief))
            p.setBrush(_BLAU); p.drawRect(QRectF(x - 2, a, 4, b - a))
    elif sym == "netz":
        p.eraseRect(0, 18, 22, 4)
        mitte, punkte = QPointF(11, 11), []
        import math
        for i in range(5):
            w = -math.pi / 2 + i * 2 * math.pi / 5
            punkte.append(QPointF(11 + 8.5 * math.cos(w), 11 + 8.5 * math.sin(w)))
        p.setPen(QPen(_GRAU, 1)); p.setBrush(Qt.NoBrush); p.drawPolygon(QPolygonF(punkte))
        for q in punkte:
            p.drawLine(mitte, q)
        innen = [mitte + (q - mitte) * f for q, f in zip(punkte, (0.8, 0.5, 0.7, 0.4, 0.6))]
        p.setPen(QPen(_BLAU, 1.6)); p.setBrush(QColor(74, 143, 216, 90)); p.drawPolygon(QPolygonF(innen))
    elif sym == "vorlagen":
        p.eraseRect(0, 18, 22, 4)
        p.setPen(QPen(QColor("#3c4043"), 1.2)); p.setBrush(Qt.white); p.drawRoundedRect(QRectF(3, 2, 16, 18), 2, 2)
        for x, h, c in ((6, 6, _BLAU), (10, 10, _ORANGE), (14, 4, _BLAU)):
            p.fillRect(QRectF(x, 17 - h, 3, h), c)
        p.drawLine(5, 5, 17, 5)
    p.end()
    return QIcon(pm)


class DiagrammDialog(PanelFaehig, QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
        self.setWindowTitle("Diagramm einfügen")
        self.titel_text, self.kategorien, self.reihen = "Diagrammtitel", list(D.BEISPIEL_KATEGORIEN), dict(D.BEISPIEL_REIHEN)
        self.kombi: list[tuple[str, bool]] = []
        v = QVBoxLayout(self)
        rahmen = QFrame(); rahmen.setFrameShape(QFrame.StyledPanel); h = QHBoxLayout(rahmen); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(0)
        self.arten = QListWidget(); self.arten.setIconSize(QSize(22, 22)); self.arten.setFixedWidth(180)
        self.arten.setAccessibleName("Diagrammart"); self.arten.setSpacing(2)
        for gruppe, sym, _unter in D.TYPEN:
            self.arten.addItem(QListWidgetItem(art_symbol(sym), gruppe if gruppe != "Kombination" else "Kombination …"))
        h.addWidget(self.arten)
        rechts = QVBoxLayout(); rechts.setContentsMargins(12, 10, 12, 10)
        self.unter_zeile = FlussLayout(6)                                   # Untertypen: brechen um, wenn der Platz nicht reicht
        rechts.addLayout(self.unter_zeile)
        linie = QFrame(); linie.setFrameShape(QFrame.HLine); linie.setStyleSheet("color: palette(midlight);"); rechts.addWidget(linie)
        self.name = QLabel(); f = self.name.font(); f.setBold(True); f.setPointSizeF(f.pointSizeF() * 1.35); self.name.setFont(f)
        self.name.setWordWrap(True)
        rechts.addWidget(self.name)
        self.vorschau = QLabel(); self.vorschau.setAlignment(Qt.AlignCenter); self.vorschau.setMinimumSize(560, 330)
        self.vorschau.setStyleSheet("background: white; border: 1px solid " + Farbe.GRAU_HELL + ";")
        rechts.addWidget(self.vorschau, 1)
        self.kombi_teil = self._kombi_tabelle()
        rechts.addWidget(self.kombi_teil)
        h.addLayout(rechts, 1)
        v.addWidget(rahmen, 1)
        self._teile = h
        daten = QPushButton("&Daten bearbeiten …"); daten.setMinimumHeight(36); daten.clicked.connect(self._daten)
        fussleiste(self, v, daten)
        self._knoepfe = QButtonGroup(self); self._knoepfe.setExclusive(True)
        self.untertyp = "saeule_gruppiert"
        self._vorschau_breite, self._bild_groesse = 620, QSize(84, 64)
        self.arten.currentRowChanged.connect(self._gruppe)
        self.arten.setCurrentRow(0)

    # ---- Kombinationstabelle ----------------------------------------------------------------------------------------------
    def _kombi_tabelle(self) -> QWidget:
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 8, 0, 0)
        v.addWidget(QLabel("Kombinationsdiagramme erstellen."))
        rahmen = QFrame(); rahmen.setFrameShape(QFrame.StyledPanel)
        self._kombi_gitter = QGridLayout(rahmen); self._kombi_gitter.setHorizontalSpacing(12); self._kombi_gitter.setVerticalSpacing(6)
        self._kombi_gitter.setProperty("schmal_nein", True)               # Tabelle wie in der Vorlage, Zeilen werden neu gefüllt
        for s, text in enumerate(("Datenreihenname", "Diagrammtyp", "Sekundärachse")):
            t = QLabel(text); t.setAlignment(Qt.AlignCenter); self._kombi_gitter.addWidget(t, 0, s)
        self._kombi_gitter.setColumnStretch(0, 1); self._kombi_gitter.setColumnStretch(1, 2)
        v.addWidget(rahmen)
        self._kombi_felder: list[tuple[QLabel, QComboBox, QCheckBox]] = []
        return w

    def _kombi_fuellen(self) -> None:
        """Eine Zeile je Datenreihe; Werte aus ``self.kombi``."""
        for lab, box, kasten in self._kombi_felder:
            for x in (lab, box, kasten):
                self._kombi_gitter.removeWidget(x); x.deleteLater()
        self._kombi_felder = []
        for i, name in enumerate(self.reihen):
            typ, sek = self.kombi[i] if i < len(self.kombi) else ("saeule", False)
            box = QComboBox(); box.setMinimumHeight(36); box.setAccessibleName(f"Diagrammtyp {name}")
            box.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon); box.setMinimumContentsLength(8)
            for schl, text in D.KOMBI_TYPEN:
                box.addItem(text, schl)
            box.setCurrentIndex(max(0, box.findData(typ)))
            kasten = QCheckBox(); kasten.setChecked(sek); kasten.setAccessibleName(f"Sekundärachse {name}")
            box.currentIndexChanged.connect(self._kombi_geaendert); kasten.toggled.connect(self._kombi_geaendert)
            lab = QLabel(name)
            self._kombi_gitter.addWidget(lab, i + 1, 0); self._kombi_gitter.addWidget(box, i + 1, 1)
            self._kombi_gitter.addWidget(kasten, i + 1, 2, Qt.AlignCenter)
            self._kombi_felder.append((lab, box, kasten))

    def _kombi_geaendert(self, *_):
        self.kombi = [(box.currentData(), kasten.isChecked()) for _l, box, kasten in self._kombi_felder]
        if self.untertyp != "kombi_eigen":
            self.untertyp = "kombi_eigen"
            for b in self._knoepfe.buttons():
                b.setChecked(b.property("untertyp") == "kombi_eigen")
            self.name.setText(D.NAMEN["kombi_eigen"])
        self.aktualisieren()

    # ---- Seitenleiste ---------------------------------------------------------------------------------------------------
    def kompakt_machen(self) -> None:
        """In der Seitenleiste: die Diagrammarten in zwei Spalten über der Vorschau (alle sichtbar, ohne Rollbalken), Untertypen
        als Raster, die Vorschau so breit wie die Seitenleiste."""
        self._teile.setDirection(QBoxLayout.TopToBottom)
        a = self.arten
        a.setFlow(QListView.LeftToRight); a.setWrapping(True); a.setResizeMode(QListView.Adjust); a.setSpacing(0)
        a.setGridSize(QSize(196, 34)); a.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        a.setMinimumWidth(0); a.setMaximumWidth(16777215); a.setFixedHeight(34 * ((a.count() + 1) // 2) + 6)
        self.vorschau.setMinimumSize(0, 230)
        self._vorschau_breite, self._bild_groesse = 390, QSize(70, 54)
        self._gruppe(self.arten.currentRow())

    def passe_an(self, breite: int, _hoehe: int) -> None:
        """Auf die echte Breite der Seitenleiste: zwei Spalten Diagrammarten, Vorschau so breit wie der Platz."""
        innen = max(200, breite - 30)
        self.arten.setGridSize(QSize(innen // 2, 34))
        self._vorschau_breite = innen - 24
        self.aktualisieren()

    # ---- Auswahl --------------------------------------------------------------------------------------------------------
    def _gruppe(self, zeile: int) -> None:
        while self.unter_zeile.count():
            w = self.unter_zeile.takeAt(0).widget()
            if w is not None:
                self._knoepfe.removeButton(w); w.hide(); w.deleteLater()
        unter = D.TYPEN[zeile][2] if 0 <= zeile < len(D.TYPEN) else []
        g = self._bild_groesse
        for i, (schl, name) in enumerate(unter):
            img = D.bild(schl, "", self.kategorien, self.reihen, g.width() * 2, g.height() * 2, kachel=True)
            b = QToolButton(); b.setCheckable(True); b.setToolTip(name); b.setAccessibleName(name); b.setProperty("untertyp", schl)
            b.setIcon(QIcon(QPixmap.fromImage(img))); b.setIconSize(g); b.setFixedSize(g.width() + 12, g.height() + 12)
            b.clicked.connect(lambda _c=False, s=schl: self._waehle(s))
            self._knoepfe.addButton(b); self.unter_zeile.addWidget(b)
        ist_kombi = D.TYPEN[zeile][0] == "Kombination" if 0 <= zeile < len(D.TYPEN) else False
        self.kombi_teil.setVisible(ist_kombi)
        if unter:
            vorher = self.untertyp if any(s == self.untertyp for s, _n in unter) else unter[0][0]
            for b in self._knoepfe.buttons():
                b.setChecked(b.property("untertyp") == vorher)
            self._waehle(vorher)

    def _waehle(self, untertyp: str) -> None:
        self.untertyp = untertyp
        self.name.setText(D.NAMEN.get(untertyp, ""))
        if untertyp == "kombination" or untertyp.startswith("kombi_"):
            if untertyp != "kombi_eigen" or not self.kombi:
                self.kombi = D.kombi_vorgabe("kombination" if untertyp == "kombi_eigen" else untertyp, len(self.reihen))
            self._kombi_fuellen()
        self.aktualisieren()

    def _daten(self) -> None:
        from lunivo_writer.ui.baukasten.fenster_stapel import zeige_unter
        from lunivo_writer.ui.dialogs.einfuegen_dialoge import DiagrammDatenDialog
        d = DiagrammDatenDialog(self, self.titel_text, self.kategorien, self.reihen)

        def fertig():
            self.titel_text, self.kategorien, self.reihen = d.daten()
            self.kombi = self.kombi[:len(self.reihen)]
            self._gruppe(self.arten.currentRow())
        zeige_unter(self, d, fertig)

    # ---- Ergebnis -------------------------------------------------------------------------------------------------------
    def _ist_kombi(self) -> bool:
        return self.untertyp == "kombination" or self.untertyp.startswith("kombi_")

    def bild(self, breite: int = 640, hoehe: int = 400):
        return D.bild(self.untertyp, self.titel_text, self.kategorien, self.reihen, breite, hoehe,
                      kombi=self.kombi if self._ist_kombi() else None)

    def daten(self) -> dict:
        d = {"art": self.untertyp, "titel": self.titel_text, "kategorien": self.kategorien, "reihen": self.reihen}
        if self._ist_kombi():
            d["kombi"] = [list(k) for k in self.kombi]
        if self.untertyp in D.VORLAGEN:
            d["farben"] = list(D.VORLAGEN[self.untertyp][1])
        return d

    def aktualisieren(self, *_):
        b = self._vorschau_breite
        r = max(b, 420)                                                      # schmal: groß zeichnen und verkleinern, damit Beschriftungen lesbar bleiben
        pm = QPixmap.fromImage(self.bild(r, int(r * 0.58)))
        self.vorschau.setPixmap(pm if r == b else pm.scaledToWidth(b, Qt.SmoothTransformation))
