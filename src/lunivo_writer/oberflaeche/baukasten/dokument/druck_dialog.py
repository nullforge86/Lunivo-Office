"""Das Druckfenster: oben die Reiter „Standard“, „Lunivo-Office“ und „Drucker“, darunter die Vorschau des Blattes (eine Spalte).

    d = DruckDialog(parent, seiten=5, papier_mm=(210, 297), quer=False, start={...}, vorschau=lambda nummern, ein: [QImage, ...])
    if d.exec(): d.ergebnis()

``DruckAnsicht`` ist derselbe Inhalt ohne Knopfzeile (so liegt er auch im Menü unter „Drucken“). Der Baustein druckt nichts selbst;
``ergebnis()`` liefert die Wahl als Wörterbuch, der Aufrufer druckt (siehe ``dienste/drucken.py``).
"""
from __future__ import annotations

from lunivo_writer.oberflaeche.baukasten.basis.darstellung import rolle as _rolle

from lunivo_writer.oberflaeche.baukasten.geruest.rollen import reihe as _reihe, spalte as _spalte

from lunivo_writer.oberflaeche.baukasten.basis.daten import text as _t

import math
from typing import Callable

from PySide6.QtCore import QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QImage, QPainter, QPalette
from PySide6.QtWidgets import QButtonGroup, QCheckBox, QComboBox, QDialog, QLabel, QLineEdit, QPushButton, QRadioButton, QSpinBox, QTabWidget, QWidget

from lunivo_writer.dienste.ausgabe.drucken import PAPIER, PRO_BLATT, blatt_zeichnen, papier_name, seiten_nach_wahl
from lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen import VorschauFlaeche, fussleiste
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import AngepassteReiter
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FlussLayout, FormularGitter, abschnittstitel
from lunivo_writer.oberflaeche.baukasten.geruest.spalten import ZweiSpalter
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import PanelFaehig
from lunivo_writer.oberflaeche.bauteile import symbole
from lunivo_writer.farmwork.datentypen.farben import Farbe
from lunivo_writer.oberflaeche.baukasten.basis.mass import ABSTAND_MITTEL, BREITE_AB_ZWEISPALTER, BREITE_KNOPF_KLEIN, GROESSE_FENSTER_DRUCKEN, HOEHE_KNOPF_GROSS, ICON_GROSS, RAND_DRUCK_FUSS, RAND_DRUCK_SEITE, RAND_DRUCK_SPALTEN, RAND_FENSTER_DRUCKEN, RAND_FUSS_BACKSTAGE, RAND_KEIN, RAND_OBEN_SEITE
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld import Auswahlfeld
from lunivo_writer.oberflaeche.baukasten.basis.farben import SCHATTEN_BLATT
from lunivo_writer.oberflaeche.baukasten.bausteine.feld.feld import zeilenfeld
from lunivo_writer.oberflaeche.baukasten.bausteine.haken.haken import haken as haken_baustein
from lunivo_writer.oberflaeche.baukasten.bausteine.knopf.knopf import knopf
from lunivo_writer.oberflaeche.baukasten.bausteine.option.option import option

KEIN_DRUCKER = _t("druck.kein_drucker_eingerichtet")
KEIN_DRUCKER_HINWEIS = _t("druck.kein_drucker_eingerichtet_es_wird_das_fe")
KOMMENTARE = [(_t("druck.keine_nur_das_dokument"), "keine"), (_t("druck.als_sprechblasen_am_rand"), "blasen")]
BLATTSEITEN = [(_t("druck.alle_seiten"), "alle"), (_t("druck.nur_vorderseiten_ungerade"), "vorder"), (_t("druck.nur_rueckseiten_gerade"), "rueck")]
BEIDSEITIG = [(_t("druck.aus"), "aus"), (_t("druck.lange_kante"), "lang"), (_t("druck.kurze_kante"), "kurz")]
ZUSTAND = {0: _t("druck.bereit"), 1: _t("druck.druckt"), 2: _t("druck.fehler"), 3: _t("druck.angehalten")}


def _kopf(text: str) -> QLabel:
    return abschnittstitel(text)


def _drucker_liste() -> list:
    try:
        from PySide6.QtPrintSupport import QPrinterInfo
        return list(QPrinterInfo.availablePrinters())
    except Exception:
        return []


def _combo(eintraege, aktuell) -> QComboBox:
    c = Auswahlfeld()
    for text, wert in eintraege:
        c.addItem(text, wert)
    i = c.findData(aktuell)
    c.setCurrentIndex(max(0, i))
    return c


class _Reiter(AngepassteReiter):
    """Reiter, deren Höhe mit der Breite mitgeht: schmal umbrechen die Beschriftungen, die Seite wird höher (sonst überlappen die Felder)."""

    gestapelt = True                                          # nur gestapelt (schmal) geht die Höhe mit der Breite mit; nebeneinander bestimmt das Fenster die Höhe

    def hasHeightForWidth(self) -> bool:
        return self.gestapelt

    def heightForWidth(self, w: int) -> int:
        kopf = self.tabBar().sizeHint().height() + 4
        hoehen = []
        for i in range(self.count()):
            lay = self.widget(i).layout()
            wunsch = self.widget(i).sizeHint().height()                    # natürliche Höhe: nie darunter, sonst überlappen die Zeilen
            hoehen.append(max(wunsch, lay.totalHeightForWidth(w)) if lay is not None and lay.hasHeightForWidth() else wunsch)
        return kopf + max(hoehen or [0])


class DruckAnsicht(QWidget):
    """Reiter oben, Vorschau darunter. ``geaendert`` kommt bei jeder Änderung der Wahl."""
    geaendert = Signal()
    eigenschaften = Signal(str)                                   # Name des Druckers → der Aufrufer öffnet dessen Einstellungen

    def __init__(self, seiten: int, papier_mm: tuple[float, float] = (210, 297), quer: bool = False, start: dict | None = None, *,
                 auswahl: bool = False, vorschau: Callable[[list[int], dict], list[QImage]] | None = None, parent=None):
        super().__init__(parent)
        s = start or {}
        self._seiten, self._vorschau, self._blatt = max(1, seiten), vorschau, 0
        self._cache: dict = {}
        self._sync = False
        self._drucker = _drucker_liste()
        hoch = (min(papier_mm), max(papier_mm))

        # ---- Reiter: breit (Datei-Ansicht) rechts neben dem Blatt wie in der Vorlage, schmal (Seitenleiste) oben ----------------
        self.reiter = _Reiter(); self.reiter.setDocumentMode(True)
        self.reiter.setUsesScrollButtons(False)                   # die flache Leiste (Basis) zeigt, was ganz passt; der Rest steht hinter „•••“

        # ---- darunter: Vorschau des Blattes, in voller Breite ------------------------------------------------------------------
        unter = _spalte("fuss")
        self.flaeche = VorschauFlaeche(self._zeichnen, 300, flaeche=False)
        unter.addWidget(self.flaeche, 1)
        nav_zeile = FlussLayout()
        self.zeigen = haken_baustein("standard", _t("druck.vorschau"), an=bool(s.get("vorschau", True)))
        nav_zeile.addWidget(self.zeigen)
        self.nav = []
        for sym, tip, f in (("chevron-first", _t("druck.erstes_blatt"), lambda: self._gehe(0)),
                            ("chevron-left", _t("druck.voriges_blatt"), lambda: self._gehe(self._blatt - 1))):
            k = knopf("standard", symbol=sym, symbolgroesse="gross", tooltip=tip, aktion=f); self.nav.append(k); nav_zeile.addWidget(k)
        self.nr = QSpinBox(); self.nr.setMinimum(1); self.nr.valueChanged.connect(lambda n: self._gehe(n - 1))
        self.von = QLabel("/ 1")
        nav_zeile.addWidget(self.nr); nav_zeile.addWidget(self.von)
        for sym, tip, f in (("chevron-right", _t("druck.naechstes_blatt"), lambda: self._gehe(self._blatt + 1)),
                            ("chevron-last", _t("druck.letztes_blatt"), lambda: self._gehe(10 ** 6))):
            k = knopf("standard", symbol=sym, symbolgroesse="gross", tooltip=tip, aktion=f); self.nav.append(k); nav_zeile.addWidget(k)
        for k in self.nav:
            k.setFlat(True); _rolle(k, "symbol")
        unter.addLayout(nav_zeile)
        self._blatt_box = QWidget(); self._blatt_box.setLayout(unter)
        # ---- beide in den ZweiSpalter: breit links das Blatt, rechts die Auswahl; schmal die Auswahl oben, das Blatt darunter -------
        self.spalten = ZweiSpalter(self._blatt_box, self.reiter, oben="rechts", gestapelt_stretch=(0, 1),
                                   raender_breit=RAND_DRUCK_SPALTEN, raender_gestapelt=RAND_OBEN_SEITE)
        self.spalten.angeordnet.connect(self._angeordnet)
        self._angeordnet(False)
        _h = _spalte("kein", self); _h.addWidget(self.spalten)
        self._standard(s, hoch, quer, auswahl)
        self._programm(s)
        self._druckerseite(s)
        self.reiter.setCurrentIndex(max(0, min(2, int(s.get("reiter", 0)))))
        self._verdrahten()
        self._timer = QTimer(self); self._timer.setSingleShot(True); self._timer.setInterval(250); self._timer.timeout.connect(self._neu_laden)
        self._aenderung()

    # ---- Anordnung nach Breite (macht der ZweiSpalter) -----------------------------------------------------------------------
    BREIT_AB = BREITE_AB_ZWEISPALTER                              # ab dieser Breite stehen Blatt und Auswahl nebeneinander (Datei-Ansicht)

    def _angeordnet(self, breit: bool) -> None:
        self.reiter.gestapelt = not breit
        self.reiter.updateGeometry()

    # ---- Reiter „Standard“ ----------------------------------------------------------------------------------------------
    def _standard(self, s, hoch, quer, auswahl):
        w = QWidget(); f = _spalte("fenster", w)
        f.addWidget(_kopf(_t("druck.drucker")))
        g = FormularGitter(); f.addLayout(g)
        self.name = Auswahlfeld()
        if self._drucker:
            for p in self._drucker:
                self.name.addItem(p.printerName(), p.printerName())
            i = self.name.findData(s.get("drucker", ""))
            self.name.setCurrentIndex(i if i >= 0 else max(0, next((j for j, p in enumerate(self._drucker) if p.isDefault()), 0)))
        else:
            self.name.addItem(KEIN_DRUCKER, "")
        g.zeile(_t("druck.name"), self.name)
        self.eig = knopf("standard", _t("druck.eigenschaften"), aktiv=bool(self._drucker))
        g.breit(self.eig)
        self.status = QLabel(); self.status.setWordWrap(True)
        g.zeile(_t("druck.status"), self.status)

        f.addWidget(_kopf(_t("druck.bereich_und_kopien")))
        g = FormularGitter(); f.addLayout(g)
        self.alle = option("standard", _t("druck.alle_seiten")); self.auswahl = option("standard", _t("druck.auswahl")); self.seiten = option("standard", _t("druck.seiten"))
        self.auswahl.setEnabled(auswahl)
        gruppe = QButtonGroup(self); [gruppe.addButton(b) for b in (self.alle, self.auswahl, self.seiten)]
        self.text = zeilenfeld("frei", s.get("seiten_text", ""), platzhalter="1-3, 5")
        (self.seiten if s.get("bereich") == "seiten" else self.alle).setChecked(True)
        g.breit(self.alle); g.breit(self.auswahl); g.zeile(self.seiten, self.text)
        self.kopien = QSpinBox(); self.kopien.setRange(1, 999); self.kopien.setValue(int(s.get("kopien", 1)))
        g.zeile(_t("druck.anzahl_der_kopien"), self.kopien)
        self.sortieren = haken_baustein("standard", _t("druck.sortieren"), an=bool(s.get("sortieren", True))); g.breit(self.sortieren)
        self.blattseiten = _combo(BLATTSEITEN, s.get("blattseiten", "alle")); g.zeile(_t("druck.blattseiten"), self.blattseiten)

        f.addWidget(_kopf(_t("druck.seitenlayout")))
        g = FormularGitter(); f.addLayout(g)
        self.papier = self._papier_combo(s.get("papier") or papier_name(*hoch))
        self.lage = _combo([(_t("druck.hochformat"), False), (_t("druck.querformat"), True)], bool(s.get("quer", quer)))
        self.pro_blatt = _combo([(str(n), n) for n in PRO_BLATT], int(s.get("pro_blatt", 1)))
        for text, c in ((_t("druck.papiergroesse"), self.papier), (_t("druck.ausrichtung"), self.lage), (_t("druck.seiten_pro_blatt"), self.pro_blatt)):
            g.zeile(text, c)
        f.addStretch(1)
        self.reiter.addTab(w, _t("druck.standard"))

    @staticmethod
    def _papier_combo(aktuell: str) -> QComboBox:
        c = Auswahlfeld()
        for n in PAPIER:
            c.addItem(n, n)
        if aktuell not in PAPIER:
            c.addItem(aktuell, aktuell)
        c.setCurrentIndex(c.findData(aktuell))
        return c

    # ---- Reiter „Lunivo-Office“ ------------------------------------------------------------------------------------------
    def _programm(self, s):
        w = QWidget(); f = _spalte("fenster", w)
        f.addWidget(_kopf(_t("druck.inhalt")))

        def haken(text, schl, vorgabe):
            c = haken_baustein("standard", text, an=bool(s.get(schl, vorgabe))); f.addWidget(c); return c
        self.hintergrund = haken(_t("druck.seitenhintergrund"), "hintergrund", True)
        self.zeichnungen = haken(_t("druck.bilder_und_andere_grafikobjekte"), "zeichnungen", True)
        self.platzhalter = haken(_t("druck.textplatzhalter"), "platzhalter", False)
        self.steuer = haken(_t("druck.steuerelemente"), "steuerelemente", True)
        g = FormularGitter(); f.addLayout(g)
        self.kommentare = _combo(KOMMENTARE, s.get("kommentare", "keine")); g.zeile(_t("druck.kommentare"), self.kommentare)
        f.addWidget(_kopf(_t("druck.farbe")))
        self.schwarz = haken(_t("druck.text_schwarz_drucken"), "schwarz", False)
        f.addWidget(_kopf(_t("druck.seiten_2")))
        self.leere = haken(_t("druck.leere_seiten_mitdrucken"), "leere", True)
        f.addStretch(1)
        self.reiter.addTab(w, _t("druck.lunivo_writer"))

    # ---- Reiter „Drucker“ ------------------------------------------------------------------------------------------------
    def _druckerseite(self, s):
        w = QWidget(); f = _spalte("fenster", w)
        f.addWidget(_kopf(_t("druck.drucker")))
        g = FormularGitter(); f.addLayout(g)
        self.info = {}
        for i, k in enumerate((_t("druck.name"), _t("druck.status_2"), _t("druck.typ"), _t("druck.ort"), _t("druck.kommentar"))):
            self.info[k] = QLabel("—"); self.info[k].setWordWrap(True); g.zeile(k + ":", self.info[k])
        f.addWidget(_kopf(_t("druck.papier")))
        self.papier2 = self._papier_combo(self.papier.currentData())
        self.lage2 = _combo([(_t("druck.hochformat"), False), (_t("druck.querformat"), True)], self.lage.currentData())
        self.beidseitig = _combo(BEIDSEITIG, s.get("beidseitig", "aus"))
        g = FormularGitter(); f.addLayout(g)
        for text, c in ((_t("druck.papiergroesse"), self.papier2), (_t("druck.ausrichtung"), self.lage2), (_t("druck.beidseitig"), self.beidseitig)):
            g.zeile(text, c)
        f.addWidget(_kopf(_t("druck.geraet")))
        self.geraet = QLabel(); self.geraet.setWordWrap(True); f.addWidget(self.geraet)
        f.addStretch(1)
        self.reiter.addTab(w, _t("druck.drucker"))

    # ---- Verdrahtung ---------------------------------------------------------------------------------------------------
    def _verdrahten(self):
        for a, b in ((self.papier, self.papier2), (self.lage, self.lage2)):      # dieselbe Wahl auf beiden Reitern
            a.currentIndexChanged.connect(lambda _=0, a=a, b=b: self._gleich(a, b))
            b.currentIndexChanged.connect(lambda _=0, a=a, b=b: self._gleich(b, a))
        self.name.currentIndexChanged.connect(self._drucker_gewaehlt)
        self.eig.clicked.connect(lambda: self.eigenschaften.emit(self.name.currentData() or ""))
        self.text.textChanged.connect(lambda _t: (self.seiten.setChecked(True), self._aenderung()))
        for c in (self.alle, self.auswahl, self.seiten):
            c.toggled.connect(lambda _=False: self._aenderung())
        for c in (self.blattseiten, self.pro_blatt, self.kommentare, self.beidseitig):
            c.currentIndexChanged.connect(lambda _=0: self._aenderung())
        for c in (self.hintergrund, self.zeichnungen, self.platzhalter, self.steuer, self.schwarz, self.leere, self.sortieren, self.zeigen):
            c.toggled.connect(lambda _=False: self._aenderung())
        self.kopien.valueChanged.connect(lambda _=0: self._aenderung())
        self.reiter.currentChanged.connect(lambda _=0: self.geaendert.emit())
        self._drucker_gewaehlt()

    def _gleich(self, von: QComboBox, nach: QComboBox):
        if self._sync:
            return
        self._sync = True
        nach.setCurrentIndex(nach.findData(von.currentData()))
        self._sync = False
        self._aenderung()

    def _drucker_gewaehlt(self, *_):
        p = next((p for p in self._drucker if p.printerName() == self.name.currentData()), None)
        if p is None:
            self.status.setText(KEIN_DRUCKER_HINWEIS)
            for k in self.info:
                self.info[k].setText("—")
            self.geraet.setText(_t("druck.erst_einen_drucker_waehlen"))
            return
        zustand = ZUSTAND.get(int(getattr(p.state(), "value", p.state())), _t("druck.bereit"))
        self.status.setText(zustand)
        for k, t in ((_t("druck.name"), p.printerName()), (_t("druck.status_2"), zustand), (_t("druck.typ"), p.makeAndModel()), (_t("druck.ort"), p.location()), (_t("druck.kommentar"), p.description())):
            self.info[k].setText(t or "—")
        farbe = _t("druck.farbe") if getattr(p, "supportedColorModes", None) and len(p.supportedColorModes()) > 1 else _t("druck.schwarzweiss_oder_farbe")
        duplex = _t("druck.beidseitiger_druck_moeglich") if len(p.supportedDuplexModes()) > 1 else _t("druck.nur_einseitiger_druck")
        self.geraet.setText(f"{farbe} · {duplex}")
        self.beidseitig.setEnabled(len(p.supportedDuplexModes()) > 1)
        self._aenderung()

    def drucker_setzen(self, kopien: int, beidseitig: str) -> None:
        """Nach den Einstellungen des Systems: Kopien und Beidseitig übernehmen."""
        self.kopien.setValue(max(1, kopien))
        self.beidseitig.setCurrentIndex(max(0, self.beidseitig.findData(beidseitig)))

    # ---- Wahl lesen ------------------------------------------------------------------------------------------------------
    def ergebnis(self) -> dict:
        b = PAPIER.get(self.papier.currentData())
        return {"drucker": self.name.currentData() or "", "bereich": "seiten" if self.seiten.isChecked() else ("auswahl" if self.auswahl.isChecked() else "alle"),
                "seiten_text": self.text.text().strip(), "kopien": self.kopien.value(), "sortieren": self.sortieren.isChecked(),
                "blattseiten": self.blattseiten.currentData(), "papier": self.papier.currentData(), "papier_mm": b, "quer": bool(self.lage.currentData()),
                "pro_blatt": self.pro_blatt.currentData(), "hintergrund": self.hintergrund.isChecked(), "zeichnungen": self.zeichnungen.isChecked(),
                "platzhalter": self.platzhalter.isChecked(), "steuerelemente": self.steuer.isChecked(), "kommentare": self.kommentare.currentData(),
                "schwarz": self.schwarz.isChecked(), "leere": self.leere.isChecked(), "beidseitig": self.beidseitig.currentData(),
                "vorschau": self.zeigen.isChecked(), "reiter": self.reiter.currentIndex()}

    def gueltig(self) -> bool:
        """Ein eigener Seitenbereich muss mindestens eine Seite treffen."""
        return bool(seiten_nach_wahl(self.ergebnis(), self._seiten))

    # ---- Vorschau --------------------------------------------------------------------------------------------------------
    def _blatt_mm(self) -> tuple[float, float]:
        b, h = PAPIER.get(self.papier.currentData(), (210, 297))
        return (h, b) if self.lage.currentData() else (b, h)

    def _blaetter(self) -> list[list[int]]:
        e = self.ergebnis()
        nummern = seiten_nach_wahl(e, self._seiten)
        k = int(e["pro_blatt"])
        return [nummern[i:i + k] for i in range(0, len(nummern), k)] or [[]]

    def _aenderung(self):
        n = len(self._blaetter())
        self._blatt = min(self._blatt, n - 1)
        self.nr.blockSignals(True); self.nr.setMaximum(n); self.nr.setValue(self._blatt + 1); self.nr.blockSignals(False)
        self.von.setText(f"/ {n}")
        self.flaeche.setVisible(self.zeigen.isChecked())
        self.flaeche.update()
        self._timer.start()
        self.geaendert.emit()

    def _gehe(self, i: int):
        self._blatt = max(0, min(i, len(self._blaetter()) - 1))
        self.nr.blockSignals(True); self.nr.setValue(self._blatt + 1); self.nr.blockSignals(False)
        self._neu_laden()

    def _neu_laden(self):
        if not (self._vorschau and self.zeigen.isChecked()):
            return
        nummern = self._blaetter()[self._blatt]
        e = self.ergebnis()
        schl = (tuple(nummern), e["hintergrund"], e["zeichnungen"], e["platzhalter"], e["steuerelemente"], e["schwarz"], e["leere"], e["kommentare"])
        if schl not in self._cache:
            self._cache[schl] = self._vorschau(nummern, e) if nummern else []
            if len(self._cache) > 24:
                self._cache.pop(next(iter(self._cache)))
        self._bilder = self._cache[schl]
        self.flaeche.update()

    def _zeichnen(self, p: QPainter, r) -> None:
        b, h = self._blatt_mm()
        rand_oben, rand_links = 24, 30                                  # Platz für die Maße über und links vom Blatt
        f = min((r.width() - rand_links - 10) / b, (r.height() - rand_oben - 10) / h)
        blatt = QRectF(rand_links + (r.width() - rand_links - b * f) / 2, rand_oben + (r.height() - rand_oben - h * f) / 2, b * f, h * f)
        p.setPen(self.palette().color(QPalette.Mid))
        p.drawText(QRectF(blatt.left(), 0, blatt.width(), rand_oben - 4), Qt.AlignCenter, _t("druck.0_g_mm_1").format(b, self.papier.currentData()))
        p.save(); p.translate(rand_links - 8, blatt.center().y()); p.rotate(-90)
        p.drawText(QRectF(-60, -10, 120, 20), Qt.AlignCenter, f"{h:g} mm"); p.restore()
        p.fillRect(blatt.translated(2, 3), QColor(*SCHATTEN_BLATT))
        p.fillRect(blatt, QColor(Farbe.PAPIER))
        bilder = getattr(self, "_bilder", [])
        if bilder and self.zeigen.isChecked():
            blatt_zeichnen(p, blatt, bilder, int(self.pro_blatt.currentData()), rand=1.0 if self.pro_blatt.currentData() > 1 else 0.0)


class DruckDialog(PanelFaehig, QDialog):
    """Das Druckfenster mit Knopfzeile: Hilfe links, „Abbrechen“ und „Drucken“ rechts."""

    def __init__(self, parent, seiten: int, papier_mm: tuple[float, float] = (210, 297), quer: bool = False, start: dict | None = None, *,
                 auswahl: bool = False, vorschau=None, hilfe: Callable | None = None):
        super().__init__(parent)
        self.setWindowTitle(_t("druck.drucken")); self.setModal(True); self.resize(*GROESSE_FENSTER_DRUCKEN)
        v = _spalte("aussen", self)
        self.ansicht = DruckAnsicht(seiten, papier_mm, quer, start, auswahl=auswahl, vorschau=vorschau)
        v.addWidget(self.ansicht, 1)
        h = knopf("standard", _t("druck.hilfe"))
        if hilfe:
            h.clicked.connect(hilfe)
        fuss = _spalte("fuss")
        self.ok = fussleiste(self, fuss, h, ok_text=_t("druck.drucken"))
        v.addLayout(fuss)
        self.ansicht.geaendert.connect(self._pruefen)
        self._pruefen()

    def _pruefen(self):
        self.ok.setEnabled(self.ansicht.gueltig())

    def ergebnis(self) -> dict:
        return self.ansicht.ergebnis()
