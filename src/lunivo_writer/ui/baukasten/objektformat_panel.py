"""„Formatierung“ für ein Bild, eine Form, ein Textfeld oder WordArt in der rechten Seitenleiste (nach der Vorlage).

Oben der Umschalter FORMOPTIONEN / TEXTOPTIONEN. Formoptionen: Reiter „Füllung und Linie“ und „Effekte“ (Schatten, Reflektion, Leuchten, Weiche Kanten,
3D-Format, 3D-Drehung). Textoptionen: derselbe Aufbau für den Text im Objekt (``text_panel``, ein ``TexteffektPanel``).

Der Baustein erbt vom Panel der Texteffekte: Schatten, Reflektion, Leuchten und 3D-Format sind dieselben Regler und Voreinstellungen,
nur Füllung und Linie gehören dem Objekt, und es kommen „Weiche Kanten“ und „3D-Drehung“ dazu. ``werte()`` liefert

    {"fuell": {…} | None, "rand": {…} | None, "schatten": {…}, "reflektion": {…}, "leuchten": {…}, "weich": {"radius": pt},
     "d3": {"tiefe", "tiefe_farbe", "kontur", "kontur_farbe", "material", "beleuchtung", "winkel"}, "drehung": {"x", "y", "z", "persp"}}

— die Angaben, die ``editor/freie_bilder.py`` am Objekt kennt (gezeichnet von ``editor/bildeffekte.py``); wer das Panel einsetzt
(``editor/bildlayout.py``), schreibt sie zurück. Die Textoptionen melden über ``text_geaendert(werte)`` (Format wie ``editor/texteffekt.py``);
``setze_text(werte)`` füllt sie.
"""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QButtonGroup, QComboBox, QHBoxLayout, QPushButton, QRadioButton, QStackedWidget, QToolButton, QVBoxLayout, QWidget

from lunivo_writer.editor import muster as M
from lunivo_writer.editor import texteffekt as T
from lunivo_writer.editor.linie import LINIENARTEN
from lunivo_writer.editor import bildeffekte as BE
from lunivo_writer.ui.baukasten.farbpalette import FarbFeld
from lunivo_writer.ui.baukasten.formular_gitter import UmbruchSchalter
from lunivo_writer.ui.baukasten.linien import linien_symbol
from lunivo_writer.ui.baukasten.objekt_menues import TEXTUREN
from lunivo_writer.ui.baukasten.schiebe_feld import SchiebeFeld
from lunivo_writer.ui.baukasten.texteffekt_dialog import Abschnitt, TexteffektPanel
from lunivo_writer.ui.baukasten.voreinstellung_menue import VoreinstellungMenue

from lunivo_writer.editor.linie import OBJEKT_STRICHE
from lunivo_writer.core.farben import Farbe
STRICHE = [k for k, _name in OBJEKT_STRICHE]                                    # die eine Liste der Strichlinien (editor/linie.py)
WEICH_STUFEN = (1, 2.5, 5, 10, 25, 50)
LEER = {"fuell": None, "rand": None}


class _DreiDUntereinander:
    """Für beide Seiten der Effekte (Objekt und Text): Zahlenfelder als Regler mit Wert darüber (ein Schrittfeld zeigt seine Zahl im dunklen Thema nicht)
    und das 3D-Format mit den Feldern untereinander im ``FormularGitter`` — die Zweierreihen des Text-Panels sind für 300 px zu breit."""

    @staticmethod
    def _schritt_feld(lo: float, hi: float, suffix: str, schritt: float, nk: int) -> QWidget:
        return SchiebeFeld(lo, hi, suffix, schritt, nk)

    MIT_ABSCHLUSS = False                      # Oberer/Unterer Abschluss gibt es nur für Objekte (der Text-Effekt kennt sie nicht)

    def _seite_effekte(self, w: dict) -> QWidget:
        seite = super()._seite_effekte(w)
        # 3D-Format neu ordnen: die Felder untereinander im FormularGitter (die Zweierreihen des Text-Panels sind für 300 px zu breit)
        alt = self.a_3d
        self.a_3d = Abschnitt("3D-Format")
        zr3 = QPushButton("Zurücksetzen"); zr3.clicked.connect(self._d3_zuruecksetzen)
        self._ab_stumm = True
        self.ab_art, self.ab_knopf, self.ab_breite, self.ab_hoehe = {}, {}, {}, {}
        if self.MIT_ABSCHLUSS:
            for k, titel in (("oben", "Oberer Abschluss"), ("unten", "Unterer Abschluss")):
                self.ab_art[k] = "keine"
                self.ab_knopf[k] = QPushButton("Keine"); self.ab_knopf[k].setMinimumWidth(110)
                self.ab_breite[k], self.ab_hoehe[k] = SchiebeFeld(0, 20, " pt", 0.5, 1, 4.0), SchiebeFeld(0, 20, " pt", 0.5, 1, 6.0)
                self.a_3d.zeile(titel + ":", self.ab_knopf[k]); self.a_3d.zeile("Breite:", self.ab_breite[k]); self.a_3d.zeile("Höhe:", self.ab_hoehe[k])
                self.ab_knopf[k].clicked.connect(lambda _=False, k=k: self._abschluss_menue(k))
                for f in (self.ab_breite[k], self.ab_hoehe[k]):
                    f.valueChanged.connect(lambda *_, k=k: self._abschluss_regler(k))
        for t, f in (("Tiefe:", self.d_tiefe_f), ("Größe der Tiefe:", self.d_tiefe), ("Kontur:", self.d_kontur_f), ("Größe der Kontur:", self.d_kontur),
                     ("Material:", self.d_material), ("Beleuchtung:", self.d_licht), ("Winkel:", self.d_winkel)):
            self.a_3d.zeile(t, f)
        self.a_3d.breit(zr3)
        seite.layout().replaceWidget(alt, self.a_3d); alt.hide(); alt.setParent(None); alt.deleteLater()
        self._ab_stumm = False
        return seite

    # ---- Oberer / Unterer Abschluss: Auswahl der Art (Bildchen), Breite und Höhe
    def _abschluss_menue(self, k: str) -> None:
        m = VoreinstellungMenue(self, keine=("Kein Abschluss", QIcon(BE.abschluss_symbol("keine"))), kachel=QSize(40, 40))
        m.abschnitt("Abschluss", [(a, QIcon(BE.abschluss_symbol(a)), n) for a, n in BE.ABSCHLUSS], 3)
        m.gewaehlt.connect(lambda a: self._abschluss_setzen(k, a or "keine"))
        m.exec(self.ab_knopf[k].mapToGlobal(self.ab_knopf[k].rect().bottomLeft()))

    def _abschluss_setzen(self, k: str, art: str) -> None:
        self.ab_art[k] = art
        self.ab_knopf[k].setText("Keine" if art == "keine" else dict(BE.ABSCHLUSS)[art])
        self._neu()

    def _abschluss_regler(self, k: str) -> None:
        """Wer Breite oder Höhe bewegt, schaltet den Abschluss ein (Rund), wenn er aus war."""
        if getattr(self, "_ab_stumm", True):
            return
        if self.ab_art[k] == "keine":
            self._abschluss_setzen(k, "rund")
        else:
            self._neu()

    def _setze_effekte(self, w: dict) -> None:
        super()._setze_effekte(w)
        if self.MIT_ABSCHLUSS:
            self._ab_stumm = True
            d3 = w.get("d3") or {}
            for k in ("oben", "unten"):
                ab = d3.get(k) or {}
                self.ab_art[k] = ab.get("art", "keine")
                self.ab_knopf[k].setText("Keine" if self.ab_art[k] == "keine" else dict(BE.ABSCHLUSS).get(self.ab_art[k], "Eigene"))
                self.ab_breite[k].setValue(ab.get("breite", 4.0)); self.ab_hoehe[k].setValue(ab.get("hoehe", 6.0))
            self._ab_stumm = False

    def _werte_effekte(self) -> dict:
        fx = super()._werte_effekte()
        if self.MIT_ABSCHLUSS and any(a != "keine" for a in self.ab_art.values()):
            d3 = fx.get("d3") or {"tiefe": 0.0, "tiefe_farbe": self.d_tiefe_f.farbe or Farbe.GRAU, "kontur": 0.0, "kontur_farbe": self.d_kontur_f.farbe or Farbe.TINTE,
                                  "material": self._material, "beleuchtung": self._licht, "winkel": self.d_winkel.value()}
            for k, a in self.ab_art.items():
                if a != "keine":
                    d3[k] = {"art": a, "breite": self.ab_breite[k].value(), "hoehe": self.ab_hoehe[k].value()}
            fx["d3"] = d3
        return fx


class _TextPanel(_DreiDUntereinander, TexteffektPanel):
    """Die Textoptionen: das Panel der Texteffekte mit dem schmalen 3D-Format."""


class ObjektFormatPanel(_DreiDUntereinander, TexteffektPanel):
    MIT_ABSCHLUSS = True
    TITEL = ("FÜLLUNG UND LINIE", "EFFEKTE")
    bild_gewuenscht = Signal()                    # „Bild …“ als Füllung: der Aufrufer fragt nach der Datei
    text_geaendert = Signal(dict)                 # Änderung in den Textoptionen (Format von ``editor/texteffekt.py``)

    def __init__(self, parent=None, werte: dict | None = None):
        super().__init__(parent, werte)
        v = self.layout()
        v.removeWidget(self.reiter)
        self.optionen = QStackedWidget()
        self.text_panel = _TextPanel(self)                                 # TEXTOPTIONEN: derselbe Aufbau, wirkt auf den Text im Objekt
        self.optionen.addWidget(self.reiter); self.optionen.addWidget(self.text_panel)
        kopf = QHBoxLayout(); kopf.setContentsMargins(0, 0, 0, 0); kopf.setSpacing(0)
        self.umschalter = QButtonGroup(self); self.umschalter.setExclusive(True)
        for i, titel in enumerate(("FORMOPTIONEN", "TEXTOPTIONEN")):
            k = QToolButton(); k.setText(titel); k.setCheckable(True); k.setAutoRaise(True); k.setToolButtonStyle(Qt.ToolButtonTextOnly)
            k.setStyleSheet("QToolButton { border: none; border-bottom: 2px solid transparent; padding: 5px 6px; color: palette(window-text); font-weight: 600; }"
                            "QToolButton:checked { color: palette(highlight); border-bottom: 2px solid palette(highlight); }")
            self.umschalter.addButton(k, i); kopf.addWidget(k, 1)
            k.setObjectName(f"optionen_{i}")
        self.umschalter.button(0).setChecked(True)
        self.umschalter.idClicked.connect(self.optionen_waehlen)
        v.addLayout(kopf); v.addWidget(self.optionen, 1)
        self.text_panel.geaendert.connect(self.text_geaendert)

    def optionen_waehlen(self, i: int) -> None:
        """0 = Formoptionen (Füllung und Linie, Effekte des Objekts), 1 = Textoptionen (Text im Objekt)."""
        self.optionen.setCurrentIndex(i)
        self.umschalter.button(i).setChecked(True)

    def setze_text(self, werte: dict) -> None:
        """Die Textoptionen mit den Werten des Textes im Objekt füllen (meldet nichts)."""
        self.text_panel.setze({**T.EFFEKT, **werte})

    def text_werte(self) -> dict:
        return self.text_panel.werte()

    @staticmethod
    def _tab_icon(t: str, unterstrichen: bool):
        """Die Reiter-Bildchen: Farbeimer (Füllung und Linie) und ein Quadrat mit Funken (Effekte)."""
        from PySide6.QtCore import QRectF, Qt
        from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
        from lunivo_writer.ui.widgets import icons
        pm = QPixmap(26, 26); pm.fill(Qt.transparent)
        p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
        if unterstrichen:
            p.drawPixmap(2, 0, icons.icon("farbe", 22).pixmap(22, 22))
            p.setPen(QColor(Farbe.BLAU)); p.drawLine(5, 24, 21, 24)
        else:
            p.setPen(QPen(QColor(Farbe.GRAU), 1.6)); p.drawRect(QRectF(4, 6, 14, 14))
            p.setPen(QPen(QColor(Farbe.BLAU), 1.6)); p.drawLine(18, 2, 18, 8); p.drawLine(15, 5, 21, 5)
        p.end()
        return QIcon(pm)

    # ---- Seite 1: Füllung und Linie ------------------------------------------------------------------------------------------
    def _seite_fuellung(self, w: dict) -> QWidget:
        seite = QWidget(); v = QVBoxLayout(seite); v.setSpacing(10)
        self.fuell_farbe_kopf = FarbFeld(Farbe.BLAU, "Füllfarbe", keine_text="Keine Füllung", verlauf=True)
        self.fuell_farbe_kopf.setMinimumWidth(110)
        self.a_fuell = Abschnitt("Füllung", self.fuell_farbe_kopf)
        self.r_keine, self.r_farbe, self.r_verlauf = QRadioButton("Keine Füllung"), QRadioButton("Einfarbige Füllung"), QRadioButton("Farbverlauf")
        self.r_textur, self.r_muster = QRadioButton("Strukturfüllung"), QRadioButton("Musterfüllung")
        self.r_bild = QRadioButton("Bildfüllung")
        for r in (self.r_keine, self.r_farbe, self.r_verlauf, self.r_textur, self.r_muster, self.r_bild):
            self.a_fuell.breit(r)
        self.farbe = FarbFeld(Farbe.BLAU, "Füllfarbe", keine_text="Automatisch")
        self.a_fuell.zeile("Farbe:", self.farbe)
        self.v1, self.v2 = FarbFeld("#1864ab", "Dunkle Farbe"), FarbFeld("#d0ebff", "Helle Farbe")
        self.a_fuell.zeile("Farbe 1:", self.v1); self.a_fuell.zeile("Farbe 2:", self.v2)
        self.textur = QComboBox()
        for schl, name in TEXTUREN:
            self.textur.addItem(name, schl)
        self.a_fuell.zeile("Struktur:", self.textur)
        self.muster = QComboBox()
        for schl, name, _o in M.MUSTER:
            if schl != "loeschen":
                self.muster.addItem(M.name_von(schl), schl)
        self.m_farbe = FarbFeld(Farbe.TINTE, "Musterfarbe")
        self.a_fuell.zeile("Muster:", self.muster); self.a_fuell.zeile("Musterfarbe:", self.m_farbe)
        self.bild_knopf = QPushButton("Bild wählen …"); self.bild_knopf.clicked.connect(self.bild_gewuenscht)
        self.a_fuell.zeile("Bild:", self.bild_knopf)
        v.addWidget(self.a_fuell)
        # Linie
        self.linie_knopf = QPushButton("Keine"); self.linie_knopf.setMinimumWidth(110)
        self.a_kontur = Abschnitt("Linie", self.linie_knopf)
        self.k_keine, self.k_linie = QRadioButton("Keine Linie"), QRadioButton("Durchgezogene Linie")
        for r in (self.k_keine, self.k_linie):
            self.a_kontur.breit(r)
        self.k_farbe = FarbFeld(Farbe.SCHWARZ, "Linienfarbe")
        self.k_breite = SchiebeFeld(0.25, 20, " pt", 0.25, 2)
        self.k_art = QComboBox(); self.k_art.setIconSize(QSize(86, 14))
        for k in STRICHE:                                          # die Strichlinien des Bausteins „Linie“ als Bildchen, nicht als Text
            self.k_art.addItem(linien_symbol(k, QSize(86, 14)), "", k)
        self.a_kontur.zeile("Farbe:", self.k_farbe); self.a_kontur.zeile("Breite:", self.k_breite); self.a_kontur.zeile("Strichart:", self.k_art)
        v.addWidget(self.a_kontur)
        v.addStretch(1)
        self.linie_knopf.clicked.connect(self._linien_menue)
        self.fuell_farbe_kopf.farbeGeaendert.connect(self._kopffarbe)
        self.fuell_farbe_kopf.verlaufGewaehlt.connect(self._kopf_verlauf)
        for r in (self.r_keine, self.r_farbe, self.r_verlauf, self.r_textur, self.r_muster, self.r_bild, self.k_keine, self.k_linie):
            r.toggled.connect(self._neu)
        # Jedes Feld ist bedienbar: wer es ändert, wählt damit die dazugehörige Füllung bzw. Linie
        for sig, radio in ((self.farbe.farbeGeaendert, self.r_farbe), (self.v1.farbeGeaendert, self.r_verlauf), (self.v2.farbeGeaendert, self.r_verlauf),
                           (self.textur.currentIndexChanged, self.r_textur), (self.muster.currentIndexChanged, self.r_muster),
                           (self.m_farbe.farbeGeaendert, self.r_muster)):
            sig.connect(lambda *_, r=radio: (r.setChecked(True), self._neu()))
        for sig in (self.k_farbe.farbeGeaendert, self.k_breite.valueChanged, self.k_art.currentIndexChanged):
            sig.connect(lambda *_: (self.k_linie.setChecked(True), self._neu()))
        return seite

    def _kopffarbe(self, c: str) -> None:
        if not c:
            self.r_keine.setChecked(True)
        else:
            self.r_farbe.setChecked(True); self.farbe.setFarbe(c)
        self._neu()

    def _kopf_verlauf(self, farbe: str) -> None:
        from PySide6.QtGui import QColor
        c = QColor(farbe)
        self.v1.setFarbe(c.name()); self.v2.setFarbe(c.lighter(170).name()); self.r_verlauf.setChecked(True)
        self._neu()

    def _linien_menue(self) -> None:
        m = VoreinstellungMenue(self, keine=("Keine Linie", None), kachel=QSize(86, 14))
        m._kopf("Keine Linie")
        m.abschnitt("Strichart", [(k, linien_symbol(k, QSize(86, 14)), LINIENARTEN[k][0]) for k in STRICHE], 2)
        m.gewaehlt.connect(lambda k: self.k_keine.setChecked(True) if not k else (self.k_linie.setChecked(True), self.k_art.setCurrentIndex(self.k_art.findData(k))))
        m.exec(self.linie_knopf.mapToGlobal(self.linie_knopf.rect().bottomLeft()))

    def fuellung_waehlen(self, art: str) -> None:
        """Die Füllungsart wählen („verlauf“, „textur“, „muster“, „bild“ …); die Füllung gilt sofort, die Felder dazu sind bedienbar."""
        radio = {"keine": self.r_keine, "farbe": self.r_farbe, "verlauf": self.r_verlauf, "graduell": self.r_verlauf, "textur": self.r_textur,
                 "muster": self.r_muster, "bild": self.r_bild}.get(art)
        if radio is not None and not radio.isChecked():
            radio.setChecked(True)

    def _neu(self, *_) -> None:
        super()._neu()
        self.linie_knopf.setText("Keine" if self.k_keine.isChecked() else LINIENARTEN[self.k_art.currentData() or "einfach"][0])

    def _setze_fuellung(self, w: dict) -> None:
        f, r = w.get("fuell"), w.get("rand")
        art = (f or {}).get("art")
        radios = (self.r_keine, self.r_farbe, self.r_verlauf, self.r_textur, self.r_muster, self.r_bild, self.k_keine, self.k_linie)
        for x in radios:
            x.blockSignals(True)
        self.r_keine.setChecked(f is None); self.r_farbe.setChecked(art == "farbe"); self.r_verlauf.setChecked(art in ("verlauf", "graduell"))
        self.r_textur.setChecked(art == "textur"); self.r_muster.setChecked(art == "muster"); self.r_bild.setChecked(art == "bild")
        self.k_keine.setChecked(not r); self.k_linie.setChecked(bool(r))
        for x in radios:
            x.blockSignals(False)
        if f:
            if art == "farbe":
                self.farbe.setFarbe(f["farbe"])
            elif art in ("verlauf", "graduell"):
                self.v1.setFarbe(f.get("dunkel", f.get("farbe", "#1864ab"))); self.v2.setFarbe(f.get("hell", "#d0ebff"))
            elif art == "textur":
                self.textur.setCurrentIndex(max(0, self.textur.findData(f.get("key"))))
            elif art == "muster":
                self.muster.setCurrentIndex(max(0, self.muster.findData(f.get("key")))); self.m_farbe.setFarbe(f.get("farbe", Farbe.TINTE))
        self.fuell_farbe_kopf.setFarbe(f.get("farbe", "") if art == "farbe" else "")
        if r:
            self.k_farbe.setFarbe(r.get("farbe", Farbe.SCHWARZ)); self.k_breite.setValue(r.get("b", 2.0) * 72 / 96)
            self.k_art.setCurrentIndex(max(0, self.k_art.findData(r.get("art", "einfach"))))

    def _werte_fuellung(self) -> tuple[dict, dict]:
        if self.r_keine.isChecked():
            fuell = None
        elif self.r_verlauf.isChecked():
            fuell = {"art": "graduell", "dunkel": self.v1.farbe or "#1864ab", "hell": self.v2.farbe or Farbe.WEISS, "farbe": self.v1.farbe or "#1864ab"}
        elif self.r_textur.isChecked():
            fuell = {"art": "textur", "key": self.textur.currentData()}
        elif self.r_muster.isChecked():
            fuell = {"art": "muster", "key": self.muster.currentData(), "farbe": self.m_farbe.farbe or Farbe.TINTE, "grund": Farbe.WEISS}
        elif self.r_bild.isChecked():
            fuell = {"art": "bild", "unveraendert": True}                       # das Bild bleibt, wie es ist (der Aufrufer behält es)
        else:
            fuell = {"art": "farbe", "farbe": self.farbe.farbe or Farbe.BLAU}
        rand = None if self.k_keine.isChecked() else {"b": self.k_breite.value() * 96 / 72, "farbe": self.k_farbe.farbe or Farbe.SCHWARZ,
                                                         "art": self.k_art.currentData() or "einfach"}
        return {"fuell": fuell, "rand": rand}, {}

    # ---- Seite 2: Effekte (dieselben wie beim Text, dazu Weiche Kanten und 3D-Drehung) ------------------------------------------------
    def _seite_effekte(self, w: dict) -> QWidget:
        seite = super()._seite_effekte(w)
        self.weich_knopf = self._voreinstellungs_knopf()
        self.a_weich = Abschnitt("Weiche Kanten", self.weich_knopf)
        self.w_radius = SchiebeFeld(0, 50, " pt", 0.5, 1)
        self.a_weich.zeile("Größe", self.w_radius)
        seite.layout().insertWidget(3, self.a_weich)                           # nach Schatten, Reflektion, Leuchten
        self._weich_an = False
        self.w_radius.valueChanged.connect(lambda *_: self._weich_einschalten())
        self.weich_knopf.clicked.connect(self._weich_menue)
        # 3D-Drehung (nach dem 3D-Format): Drehung um X, Y, Z, Perspektive, Zurücksetzen
        self.a_dreh = Abschnitt("3D-Drehung")
        self.dr_x, self.dr_y, self.dr_z = (self._schritt_feld(-180, 180, "°", 5, 1) for _ in range(3))
        self.dr_pers = self._schritt_feld(0, 120, "°", 5, 1)
        for t, f in (("X-Drehung", self.dr_x), ("Y-Drehung", self.dr_y), ("Z-Drehung", self.dr_z), ("Perspektive", self.dr_pers)):
            self.a_dreh.zeile(t, f)
        self.dr_boden = self._schritt_feld(0, 100, " pt", 1, 1)
        self.dr_text = UmbruchSchalter("Text nicht drehen")
        self.a_dreh.breit(self.dr_text); self.a_dreh.zeile("Abstand vom Boden", self.dr_boden)
        zr = QPushButton("Zurücksetzen"); zr.clicked.connect(self._drehung_zuruecksetzen); self.a_dreh.breit(zr)
        self.dr_pers.setValue(45)
        seite.layout().insertWidget(seite.layout().indexOf(self.a_3d) + 1, self.a_dreh)
        for f in (self.dr_x, self.dr_y, self.dr_z, self.dr_pers, self.dr_boden):
            f.valueChanged.connect(lambda *_: self._neu())
        self.dr_text.toggled.connect(lambda *_: self._neu())
        return seite

    def _drehung_zuruecksetzen(self) -> None:
        for f in (self.dr_x, self.dr_y, self.dr_z):
            f.setValue(0)
        self.dr_pers.setValue(45); self.dr_boden.setValue(0); self.dr_text.setChecked(False)

    def _weich_einschalten(self) -> None:
        if not self._weich_an:
            self._weich_an = True; self.weich_knopf.setText("Eigene")
        self._neu()

    def _weich_menue(self) -> None:
        from PySide6.QtGui import QIcon
        m = VoreinstellungMenue(self, keine=("Keine weichen Kanten", None))
        m._kopf("Keine weichen Kanten")
        m.abschnitt("Weiche Kanten", [(f"{s:g}", QIcon(), f"{s:g} pt") for s in WEICH_STUFEN], 3)

        def waehle(k: str) -> None:
            self._weich_an = bool(k)
            self.weich_knopf.setText(f"{k} pt" if k else "Keine")
            if k:
                self.w_radius.setValue(float(k))
            self._neu()
        m.gewaehlt.connect(waehle)
        m.exec(self.weich_knopf.mapToGlobal(self.weich_knopf.rect().bottomLeft()))

    def _setze_effekte(self, w: dict) -> None:
        super()._setze_effekte(w)
        wk = w.get("weich")
        self._weich_an = bool(wk)
        self.weich_knopf.setText("Keine" if not wk else "Eigene")
        self.w_radius.setValue((wk or {}).get("radius", 6.0))
        dr = w.get("drehung") or {}
        self.dr_x.setValue(dr.get("x", 0.0)); self.dr_y.setValue(dr.get("y", 0.0)); self.dr_z.setValue(dr.get("z", 0.0)); self.dr_pers.setValue(dr.get("persp", 45.0))
        self.dr_boden.setValue(dr.get("boden", 0.0)); self.dr_text.blockSignals(True); self.dr_text.setChecked(bool(dr.get("text_gerade"))); self.dr_text.blockSignals(False)

    def _werte_effekte(self) -> dict:
        fx = super()._werte_effekte()
        if getattr(self, "_weich_an", False):
            fx["weich"] = {"radius": self.w_radius.value()}
        if any(abs(f.value()) > 0.01 for f in (self.dr_x, self.dr_y, self.dr_z, self.dr_boden)):
            fx["drehung"] = {"x": self.dr_x.value(), "y": self.dr_y.value(), "z": self.dr_z.value(), "persp": self.dr_pers.value(),
                             "text_gerade": self.dr_text.isChecked(), "boden": self.dr_boden.value()}
        return fx
