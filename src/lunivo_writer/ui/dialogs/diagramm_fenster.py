"""„Diagramm einfügen“ nach der Vorlage (einfuegen/07 und Prüfkatalog): links die Diagrammarten mit eigenen Bildchen, oben die
Untertypen als Bildchen, darunter Name und Vorschau. Bei „Kombination …“ steht unter der Vorschau die Tabelle Datenreihenname /
Diagrammtyp / Sekundärachse; wer dort etwas ändert, wählt „Benutzerdefinierte Kombination“.

    d = DiagrammDialog(parent)      # if d.exec(): d.bild() → QImage, d.daten() → dict (art, titel, kategorien, reihen, kombi, farben)

Das Fenster ändert das Dokument nicht. „Daten bearbeiten …“ öffnet Titel und Werte als Unterfenster im selben Stapel.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QBoxLayout, QButtonGroup, QCheckBox, QComboBox, QDialog, QFrame, QHBoxLayout, QLabel, QListView, QListWidget,
    QListWidgetItem, QPushButton, QToolButton, QVBoxLayout, QWidget,
)

from lunivo_writer.core.farben import Farbe
from lunivo_writer.editor import diagramm as D
from lunivo_writer.ui.baukasten.formular_gitter import FlussLayout, FormularGitter
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig

def art_symbol(sym: str, px: int = 22) -> QIcon:
    """Diagrammart-Symbol aus dem zentralen Lucide-Katalog."""
    namen = {
        "saeule": "chart-column", "linie": "chart-line", "kreis": "chart-pie",
        "balkenquer": "chart-bar", "flaeche": "chart-area", "punktwolke": "chart-scatter",
        "kurs": "chart-candlestick", "netz": "radar", "kombination": "chart-no-axes-combined",
        "vorlagen": "palette",
    }
    from lunivo_writer.ui.widgets import icons
    return icons.icon(namen.get(sym, "chart-column"), px)

class DiagrammDialog(PanelFaehig, QDialog):
    def __init__(self, parent, vorhanden: dict | None = None):
        """``vorhanden``: Daten eines vorhandenen Diagramms (Diagrammart, Titel, Rubriken, Reihen, Kombination) — dann öffnet das Fenster damit."""
        super().__init__(parent)
        from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
        self.setWindowTitle("Diagramm einfügen")
        self.titel_text, self.kategorien, self.reihen = "Diagrammtitel", list(D.BEISPIEL_KATEGORIEN), dict(D.BEISPIEL_REIHEN)
        self.kombi: list[tuple[str, bool]] = []
        v = QVBoxLayout(self)
        rahmen = QFrame(); rahmen.setFrameShape(QFrame.StyledPanel); h = QHBoxLayout(rahmen); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(0)
        self._kompakt = False
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
        zeile = 0
        if vorhanden:
            self.titel_text = vorhanden.get("titel", self.titel_text)
            self.kategorien = list(vorhanden.get("kategorien") or self.kategorien)
            self.reihen = {k: list(v) for k, v in (vorhanden.get("reihen") or self.reihen).items()}
            self.kombi = [(k[0], bool(k[1])) for k in vorhanden.get("kombi") or []]
            u = D.ALT.get(vorhanden.get("art"), vorhanden.get("art"))
            for i, (_g, _s, unter) in enumerate(D.TYPEN):
                if any(schl == u for schl, _n in unter):
                    self.untertyp, zeile = u, i
        self.arten.currentRowChanged.connect(self._gruppe)
        self.arten.setCurrentRow(zeile)

    # ---- Kombinationstabelle ----------------------------------------------------------------------------------------------
    def _kombi_tabelle(self) -> QWidget:
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 8, 0, 0)
        v.addWidget(QLabel("Kombinationsdiagramme erstellen."))
        self._kombi_rahmen = QFrame(); self._kombi_rahmen.setFrameShape(QFrame.StyledPanel)
        self._kombi_box = QVBoxLayout(self._kombi_rahmen); self._kombi_box.setContentsMargins(8, 6, 8, 6)
        self._kombi_gitter = None
        v.addWidget(self._kombi_rahmen)
        self._kombi_felder: list[tuple[QLabel, QComboBox, QCheckBox]] = []
        return w

    def _kombi_fuellen(self) -> None:
        """Eine Zeile je Datenreihe; Werte aus ``self.kombi``."""
        if self._kombi_gitter is not None:                                   # altes Gitter samt Feldern abbauen
            alt = self._kombi_box.takeAt(0)
            for lab, box, kasten in self._kombi_felder:
                for x in (lab, box, kasten):
                    x.hide(); x.deleteLater()
            if alt is not None and alt.widget() is not None:
                alt.widget().deleteLater()
        self._kombi_felder = []
        gitterteil = QWidget(); self._kombi_gitter = FormularGitter(gitterteil)
        self._kombi_box.addWidget(gitterteil)
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
            self._kombi_gitter.reihe(("Datenreihenname", lab), ("Diagrammtyp", box), ("Sekundärachse", kasten), gewichte=(3, 4, 2))
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
        """In der Seitenleiste: die Diagrammarten wie in WPS in einer Spalte über der Vorschau (alle sichtbar, ohne Rollbalken),
        Untertypen als Raster, die Vorschau so breit wie die Seitenleiste und nie abgeschnitten."""
        self._kompakt = True
        self._teile.setDirection(QBoxLayout.TopToBottom)
        a = self.arten
        a.setFlow(QListView.TopToBottom); a.setWrapping(False); a.setResizeMode(QListView.Adjust); a.setSpacing(0)
        a.setUniformItemSizes(True); a.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff); a.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        a.setMinimumWidth(0); a.setMaximumWidth(16777215); a.setFixedHeight(32 * a.count() + 6)
        for i in range(a.count()):
            a.item(i).setSizeHint(QSize(0, 32))
        self.vorschau.setMinimumSize(0, 0)
        self._vorschau_breite, self._bild_groesse = 390, QSize(70, 54)
        self._gruppe(self.arten.currentRow())

    def passe_an(self, breite: int, _hoehe: int) -> None:
        """Auf die echte Breite der Seitenleiste: zwei Spalten Diagrammarten, Vorschau so breit wie der Platz."""
        innen = max(200, breite - 30)
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
        pm = pm if r == b else pm.scaledToWidth(b, Qt.SmoothTransformation)
        self.vorschau.setPixmap(pm)
        if self._kompakt:
            self.vorschau.setFixedHeight(pm.height() + 2)                    # genau so hoch wie das Bild: nichts abgeschnitten
