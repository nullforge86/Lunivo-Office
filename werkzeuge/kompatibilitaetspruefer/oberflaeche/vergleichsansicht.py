"""Grafischer Dokumentvergleich: links die Referenzdarstellung (PDF/Seitenbilder aus dem Ursprungsprogramm), rechts die Darstellung von Lunivo (Layout- und Rendering-Architektur der
Anwendung, erzeugt vom Prüfprozess). Dazu Überlagerung und Differenzansicht, Abweichungsmarkierungen aus den Messwerten der Layoutprüfung, Seitennavigation, Zoom und gemeinsames Scrollen.
Die Ansicht zeigt nur Bilder an, die der Prüfprozess aus Referenz und Lunivo erzeugt hat; sie baut kein Dokument nach."""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QImage, QPainter, QPen, QPixmap, QTransform
from PySide6.QtWidgets import (QCheckBox, QComboBox, QGraphicsScene, QGraphicsView, QHBoxLayout, QLabel, QPushButton, QSlider, QSpinBox, QSplitter, QVBoxLayout, QWidget)

MARKENFARBE = {"fehlt in Lunivo": "#e53935", "zusätzlich in Lunivo": "#1e88e5", "anders gesetzt": "#fb8c00"}


class SeitenAnsicht(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setBackgroundBrush(QBrush(QColor("#6b6f76")))
        self.setAlignment(Qt.AlignCenter)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def zeige(self, bild: QImage | None, marken: list[dict]) -> None:
        sc = self.scene()
        sc.clear()
        if bild is None or bild.isNull():
            sc.addText("Keine Darstellung")
            sc.setSceneRect(sc.itemsBoundingRect())
            return
        sc.addPixmap(QPixmap.fromImage(bild))
        for m in marken:
            farbe = QColor(MARKENFARBE.get(m.get("art"), "#fb8c00"))
            fill = QColor(farbe)
            fill.setAlpha(45)
            r = sc.addRect(QRectF(m["x"], m["y"], m["w"], m["h"]), QPen(farbe, 1.5), QBrush(fill))
            r.setToolTip(f"{m.get('art', '')} ({m.get('zellen', '?')} Rasterzellen)")
        sc.setSceneRect(QRectF(0, 0, bild.width(), bild.height()))


class Vergleichsansicht(QWidget):
    darstellung_gewuenscht = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ref: list[str] = []
        self.lun: list[str] = []
        self.seitenwerte: list[dict] = []
        self._sync = False
        self.titel = QLabel("Kein Ergebnis gewählt")
        self.titel.setWordWrap(True)
        self.seite = QSpinBox()
        self.seite.setRange(1, 1)
        self.seite.valueChanged.connect(self.aktualisieren)
        self.von = QLabel("von 0")
        zurueck, vor = QPushButton("◀"), QPushButton("▶")
        zurueck.clicked.connect(lambda: self.seite.setValue(self.seite.value() - 1))
        vor.clicked.connect(lambda: self.seite.setValue(self.seite.value() + 1))
        self.zoom = QSlider(Qt.Horizontal)
        self.zoom.setRange(20, 400)
        self.zoom.setValue(70)
        self.zoom.setMaximumWidth(160)
        self.zoom.valueChanged.connect(self._zoom)
        self.zoom_text = QLabel("70 %")
        anpassen = QPushButton("Anpassen")
        anpassen.clicked.connect(self._anpassen)
        self.modus = QComboBox()
        self.modus.addItems(["Nebeneinander", "Überlagerung", "Differenz"])
        self.modus.currentIndexChanged.connect(self.aktualisieren)
        self.deckkraft = QSlider(Qt.Horizontal)
        self.deckkraft.setRange(0, 100)
        self.deckkraft.setValue(50)
        self.deckkraft.setMaximumWidth(110)
        self.deckkraft.setToolTip("Überlagerung: Anteil der Referenz")
        self.deckkraft.valueChanged.connect(self.aktualisieren)
        self.marken = QCheckBox("Abweichungsmarkierungen")
        self.marken.setChecked(True)
        self.marken.toggled.connect(self.aktualisieren)
        self.gemeinsam = QCheckBox("Gemeinsam scrollen")
        self.gemeinsam.setChecked(True)
        self.erzeugen = QPushButton("Darstellung erzeugen")
        self.erzeugen.setToolTip("Rendert die Lunivo-Seiten (und die Referenz) im Prüfprozess, ohne Beurteilung")
        self.erzeugen.clicked.connect(self.darstellung_gewuenscht)
        leiste, leiste2 = QHBoxLayout(), QHBoxLayout()
        for w in (QLabel("Seite"), zurueck, self.seite, self.von, vor, QLabel("Zoom"), self.zoom, self.zoom_text, anpassen):
            leiste.addWidget(w)
        leiste.addStretch(1)
        for w in (self.modus, self.deckkraft, self.marken, self.gemeinsam, self.erzeugen):
            leiste2.addWidget(w)
        leiste2.addStretch(1)
        self.v_ref, self.v_lun = SeitenAnsicht(), SeitenAnsicht()
        self.kopf_ref, self.kopf_lun = QLabel("Referenz (Ursprungsprogramm)"), QLabel("Lunivo Office")
        links, rechts = QWidget(), QWidget()
        for w, k, v in ((links, self.kopf_ref, self.v_ref), (rechts, self.kopf_lun, self.v_lun)):
            l = QVBoxLayout(w)
            l.setContentsMargins(0, 0, 0, 0)
            k.setAlignment(Qt.AlignCenter)
            l.addWidget(k)
            l.addWidget(v, 1)
        self.teiler = QSplitter(Qt.Horizontal)
        self.teiler.addWidget(links)
        self.teiler.addWidget(rechts)
        self._rechts = rechts
        self.info = QLabel("")
        lay = QVBoxLayout(self)
        lay.addWidget(self.titel)
        lay.addLayout(leiste)
        lay.addLayout(leiste2)
        lay.addWidget(self.teiler, 1)
        lay.addWidget(self.info)
        for a, b in ((self.v_ref, self.v_lun), (self.v_lun, self.v_ref)):
            a.horizontalScrollBar().valueChanged.connect(lambda v, b=b: self._scroll(b.horizontalScrollBar(), v))
            a.verticalScrollBar().valueChanged.connect(lambda v, b=b: self._scroll(b.verticalScrollBar(), v))
        self._zoom(70)

    # ---- Daten -----------------------------------------------------------------------------------------------------
    def setze(self, titel: str, referenz: list[str], lunivo: list[str], seitenwerte: list[dict], seite: int | None = None, hinweis: str = "") -> None:
        self.titel.setText(titel)
        self.ref, self.lun, self.seitenwerte = referenz or [], lunivo or [], seitenwerte or []
        n = max(len(self.ref), len(self.lun), 1)
        self.seite.blockSignals(True)
        self.seite.setRange(1, n)
        self.seite.setValue(min(max(1, seite or 1), n))
        self.seite.blockSignals(False)
        self.von.setText(f"von {n}  (Referenz {len(self.ref)}, Lunivo {len(self.lun)})")
        self.info.setText(hinweis)
        self.aktualisieren()

    def leeren(self, text: str) -> None:
        self.setze(text, [], [], [])
        self.info.setText("")

    def _bild(self, pfade: list[str], i: int) -> QImage | None:
        if 0 <= i < len(pfade):
            b = QImage(pfade[i])
            return None if b.isNull() else b
        return None

    def aktualisieren(self, *_) -> None:
        i = self.seite.value() - 1
        ref, lun = self._bild(self.ref, i), self._bild(self.lun, i)
        marken = []
        if self.marken.isChecked():
            for sw in self.seitenwerte:
                if sw.get("seite") == i + 1:
                    marken = sw.get("bereiche", [])
        modus = self.modus.currentIndex()
        self._rechts.setVisible(modus == 0)
        self.kopf_ref.setText("Referenz (Ursprungsprogramm)" if modus == 0 else ("Überlagerung: Referenz über Lunivo" if modus == 1 else "Differenz (dunkel = Unterschied)"))
        if ref is not None and lun is not None and ref.size() != lun.size():
            ref = ref.scaled(lun.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)      # gleiche Seitenfläche, damit die Ansichten deckungsgleich sind
        if modus == 0:
            self.v_ref.zeige(ref, marken if ref is not None else [])
            self.v_lun.zeige(lun, marken)
        elif ref is None or lun is None:
            self.v_ref.zeige(None, [])
        elif modus == 1:
            out = QImage(lun.size(), QImage.Format_RGB32)
            out.fill(QColor("white"))
            p = QPainter(out)
            p.drawImage(0, 0, lun)
            p.setOpacity(self.deckkraft.value() / 100.0)
            p.drawImage(0, 0, ref)
            p.end()
            self.v_ref.zeige(out, marken)
        else:
            out = QImage(lun.size(), QImage.Format_RGB32)
            out.fill(QColor("white"))
            p = QPainter(out)
            p.drawImage(0, 0, lun)
            p.setCompositionMode(QPainter.CompositionMode_Difference)
            p.drawImage(0, 0, ref)
            p.end()
            out.invertPixels()
            self.v_ref.zeige(out, marken)
        fehlt = [n for n, b in (("Referenz", ref), ("Lunivo", lun)) if b is None]
        self.info.setText(("Für diese Seite fehlt: " + ", ".join(fehlt)) if fehlt and (self.ref or self.lun) else self.info.text())
        self._zoom(self.zoom.value())

    def _zoom(self, wert: int) -> None:
        self.zoom_text.setText(f"{wert} %")
        t = QTransform.fromScale(wert / 100.0, wert / 100.0)
        self.v_ref.setTransform(t)
        self.v_lun.setTransform(t)

    def _anpassen(self) -> None:
        if self.v_ref.scene().sceneRect().width() > 1:
            r = self.v_ref.scene().sceneRect()
            ansicht = self.v_ref.viewport().size()
            self.zoom.setValue(int(max(20, min(400, 100 * min(ansicht.width() / r.width(), ansicht.height() / r.height())))))

    def _scroll(self, leiste, wert: int) -> None:
        if self.gemeinsam.isChecked() and not self._sync:
            self._sync = True
            leiste.setValue(wert)
            self._sync = False
