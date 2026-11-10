"""Textoptionen eines Diagramm-Teils in der Seitenleiste: Textfüllung und -kontur, Schrift, Effekte, „Textfeld“ (``DiagrammTextPanel``).

Gebraucht von ``diagramm_format_panel.DiagrammFormatPanel`` (Reiter „Textoptionen“) und dem SmartArt-Panel."""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QIcon, QPainter, QPainterPath, QPalette, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from lunivo_writer.editor.diagramme import diagramm_format as F
from lunivo_writer.editor.text import texteffekt as T
from lunivo_writer.editor.text.textfx import WARP_FORMEN, pfad_verformen
from lunivo_writer.ui.baukasten.dropdown.voreinstellung_menue import VoreinstellungMenue
from lunivo_writer.ui.baukasten.dropdown.kopf_dropdown import KopfDropdown, keine_zeile
from lunivo_writer.ui.baukasten.formatierung.textfeld_abschnitt import TextfeldAbschnitt
from lunivo_writer.ui.baukasten.controls.formular_gitter import UmbruchSchalter
from lunivo_writer.ui.baukasten.dropdown.text_kopf_menue_mixin import TextKopfMenueMixin
from lunivo_writer.ui.baukasten.formatierung.objektformat_panel import _TextPanel
from lunivo_writer.ui.baukasten.controls.schiebe_feld import SchrittFeld
from lunivo_writer.ui.baukasten.formatierung.text_fuellarten_mixin import TextFuellartenMixin
from lunivo_writer.ui.baukasten.formatierung.texteffekt_dialog import Abschnitt
from lunivo_writer.ui.widgets import icons
from lunivo_writer.ui.baukasten.basis.mass import ABSTAND_SPALTE, GROESSE_TEXTVERFORMUNG_KACHEL, ICON_MITTEL, RAND_FORMATSEITE
from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Schriftauswahl
from lunivo_writer.ui.baukasten.diagramme.diagramm_format_bausteine import RICHTUNGEN, _combo, _still


# ---- Textoptionen --------------------------------------------------------------------------------------------------------------------
class DiagrammTextPanel(TextFuellartenMixin, TextKopfMenueMixin, _TextPanel):
    """Textfüllung und -kontur, Effekte (wie bei den Texteffekten) und „Textfeld“. ``werte()`` ist das Textformat des Teils (``diagramm_format``: ``text``)."""

    FOTO = True                                     # Vorlage: „Ausrichtung“ als Baustein, Schrift hinter Textkontur (SmartArt behält den alten Aufbau)

    def __init__(self, parent=None, werte: dict | None = None):
        super().__init__(parent, werte)
        self._stumm = True
        # Schrift (die Vorlage zeigt sie nicht; sie ist sonst nirgends erreichbar und steht darum hinter der Textkontur)
        self.a_schrift = Abschnitt("Schrift")
        self.s_name = Schriftauswahl()
        self.s_groesse = SchrittFeld(6, 96, " pt", 1, 0, 10)
        self.s_fett, self.s_kursiv, self.s_unter = UmbruchSchalter("Fett"), UmbruchSchalter("Kursiv"), UmbruchSchalter("Unterstrichen")
        self.s_gesetzt = {"name": False, "groesse": False}
        self.a_schrift.zeile("Schriftart:", self.s_name); self.a_schrift.zeile("Größe:", self.s_groesse)
        for x in (self.s_fett, self.s_kursiv, self.s_unter):
            self.a_schrift.breit(x)
        seite0 = self.reiter.widget(0).widget().layout()
        seite0.insertWidget(seite0.indexOf(self.a_kontur) + 1 if self.FOTO and seite0.indexOf(self.a_kontur) >= 0 else 0, self.a_schrift)
        self._dreh_warp_bauen()
        # Textfeld
        if self.FOTO:
            self._text_kopf_bauen()                 # Köpfe von Textfüllung und -kontur wie in der Vorlage (Mixin, Basis unverändert)
            self._text_fuellarten_bauen()           # Bild-/Texturfüllung und Musterfüllung als Textfüllung (Mixin)
            self.a_feld = TextfeldAbschnitt()
            self.f_winkel, self.f_rand = self.a_feld.winkel, self.a_feld.raender
            feldseite = QWidget(); v = QVBoxLayout(feldseite); v.setSpacing(ABSTAND_SPALTE); v.setContentsMargins(*RAND_FORMATSEITE); v.addWidget(self.a_feld); v.addStretch(1)
            self.reiter.addTab(self._scroll(feldseite), icons.icon("square-text", ICON_MITTEL), "Textfeld")
            self._verbinde()
            return
        self.a_feld = Abschnitt("Textfeld")
        self.f_vertikal, self.f_richtung = _combo(F.VERTIKAL), _combo(RICHTUNGEN)
        self.f_winkel = SchrittFeld(-180, 180, "°", 5, 0, 0)
        self.f_rand = {k: SchrittFeld(0, 60, " pt", 1, 0, 0) for k in "lrou"}
        self.f_anpassen = UmbruchSchalter("Größe der Form dem Text anpassen"); self.f_anpassen.setChecked(True)
        self.f_umbruch = UmbruchSchalter("Text in Form umbrechen"); self.f_umbruch.setChecked(True)
        for t, f in (("Vertikale Ausrichtung:", self.f_vertikal), ("Textrichtung:", self.f_richtung), ("Benutzerdefinierter Winkel:", self.f_winkel),
                     ("Linker Rand:", self.f_rand["l"]), ("Rechter Rand:", self.f_rand["r"]), ("Oberer Rand:", self.f_rand["o"]), ("Unterer Rand:", self.f_rand["u"])):
            self.a_feld.zeile(t, f)
        self.a_feld.breit(self.f_anpassen); self.a_feld.breit(self.f_umbruch)
        feldseite = QWidget(); v = QVBoxLayout(feldseite); v.setSpacing(ABSTAND_SPALTE); v.setContentsMargins(*RAND_FORMATSEITE); v.addWidget(self.a_feld); v.addStretch(1)
        self.reiter.addTab(self._scroll(feldseite), icons.icon("square-text", ICON_MITTEL), "Textfeld")
        self._verbinde()

    # ---- 3D-Drehung und Transformieren (Effekte, hinter dem 3D-Format): Datenmodell ``text_3d`` und ``warp`` (``editor/text/textfx.py``)
    def _dreh_warp_bauen(self) -> None:
        seite = self.reiter.widget(1).widget().layout()
        self.a_dreh = Abschnitt("3D-Drehung")
        self.dr_x, self.dr_y, self.dr_z = (self._schritt_feld(-180, 180, "°", 5, 1) for _ in range(3))
        self.dr_pers = self._schritt_feld(0, 120, "°", 5, 1); self.dr_pers.setValue(45)
        for t, f in (("X-Drehung", self.dr_x), ("Y-Drehung", self.dr_y), ("Z-Drehung", self.dr_z), ("Perspektive", self.dr_pers)):
            self.a_dreh.zeile(t, f)
            f.valueChanged.connect(lambda *_: self._neu())
        zr = QPushButton("Zurücksetzen"); zr.clicked.connect(self._dreh_zuruecksetzen); self.a_dreh.breit(zr)
        self.a_warp = Abschnitt("Transformieren")
        self._warp_art = "keine"
        self.warp_knopf = KopfDropdown(self._warp_menue)
        self.warp_knopf.gewaehlt.connect(lambda k: self._warp_setzen(k or "keine"))
        self.warp_knopf.setAccessibleName("Transformieren wählen"); self.warp_knopf.setToolTip("Textverformung wählen")
        self.warp_knopf.an(self.a_warp)
        self._warp_zeige = QLabel(); self._warp_zeige.setWordWrap(True); self.a_warp.breit(self._warp_zeige)
        self._warp_setzen("keine", melden=False)
        i = seite.indexOf(self.a_3d)
        seite.insertWidget(i + 1, self.a_dreh); seite.insertWidget(i + 2, self.a_warp)

    def _dreh_zuruecksetzen(self) -> None:
        for f in (self.dr_x, self.dr_y, self.dr_z):
            f.setValue(0)
        self.dr_pers.setValue(45)

    @staticmethod
    def _warp_bild(art: str, groesse: QSize) -> QPixmap:
        """„abcde“ so verformt, wie der Text gezeichnet wird (derselbe ``pfad_verformen``)."""
        pm = QPixmap(groesse); pm.fill(Qt.transparent)
        pfad = QPainterPath(); pfad.addText(0, 0, QFont("sans-serif", 40), "abcde")
        pfad = pfad_verformen(pfad, {"warp": {"art": art}})
        r = pfad.boundingRect()
        if r.isEmpty():
            return pm
        k = min((groesse.width() - 6) / r.width(), (groesse.height() - 6) / r.height())
        p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
        p.translate(groesse.width() / 2, groesse.height() / 2); p.scale(k, k); p.translate(-r.center())
        p.fillPath(pfad, QApplication.palette().color(QPalette.WindowText)); p.end()
        return pm

    def _warp_menue(self, parent) -> VoreinstellungMenue:
        m = VoreinstellungMenue(parent, keine=None, kachel=QSize(*GROESSE_TEXTVERFORMUNG_KACHEL))
        m.aktuell = "" if self._warp_art == "keine" else self._warp_art
        keine_zeile(m, "Keine Transformation")
        m.abschnitt("Verbiegen", [(k, QIcon(self._warp_bild(k, QSize(*GROESSE_TEXTVERFORMUNG_KACHEL))), n) for k, n in WARP_FORMEN if k != "keine"], 4)
        return m

    def _warp_setzen(self, art: str, melden: bool = True) -> None:
        self._warp_art = art if art in dict(WARP_FORMEN) else "keine"
        self.warp_knopf.setSymbol(QIcon(self._warp_bild(self._warp_art, KopfDropdown.SYMBOL)))
        self._warp_zeige.setText(dict(WARP_FORMEN)[self._warp_art])
        if melden:
            self._neu()

    def _verbinde(self) -> None:
        for a in (self.a_schrift, self.a_feld, self.a_fuell, self.a_kontur):
            a.knopf.setChecked(True)
        self.s_name.currentFontChanged.connect(lambda *_: (self.s_gesetzt.update(name=True), self._neu()))
        self.s_groesse.valueChanged.connect(lambda *_: (self.s_gesetzt.update(groesse=True), self._neu()))
        for x in (self.s_fett, self.s_kursiv, self.s_unter):
            x.toggled.connect(lambda *_: self._neu())
        if self.FOTO:
            self.a_feld.geaendert.connect(self._neu)
        else:
            for x in (self.f_anpassen, self.f_umbruch):
                x.toggled.connect(lambda *_: self._neu())
            for x in (self.f_vertikal, self.f_richtung):
                x.currentIndexChanged.connect(lambda *_: self._neu())
            for x in (self.f_winkel, *self.f_rand.values()):
                x.valueChanged.connect(lambda *_: self._neu())
        self._stumm = False

    # ---- Werte: das Textformat des Teils
    def _setze(self, w: dict) -> None:
        t = w.get("text") or {}
        e = t.get("effekt") or {}
        basis = {**T.EFFEKT, **e}
        if not e and t.get("farbe"):
            basis["farbe"] = t["farbe"]
        super()._setze(basis)
        if hasattr(self, "a_dreh"):
            self._setze_dreh(e)
        if not hasattr(self, "f_rand"):
            return
        self._setze_schrift(t)
        f = F.feld_von(t, w.get("teil"))
        if self.FOTO:
            self.a_feld.setze(f)
            return
        self._setze_feld_alt(f)

    def _setze_dreh(self, e: dict) -> None:
        d3 = e.get("text_3d") or {}
        for f, k, v in ((self.dr_x, "x", 0), (self.dr_y, "y", 0), (self.dr_z, "z", 0), (self.dr_pers, "perspektive", 45)):
            _still(f, float(d3[k]) if d3.get(k) is not None else float(v))
        self._warp_setzen((e.get("warp") or {}).get("art", "keine"), melden=False)

    def _setze_schrift(self, t: dict) -> None:
        _still(self.s_name, QFont(t.get("name") or self.font().family()), "setCurrentFont")
        self.s_gesetzt = {"name": bool(t.get("name")), "groesse": bool(t.get("groesse"))}
        _still(self.s_groesse, float(t.get("groesse") or 10))
        for x, wert in ((self.s_fett, bool(t.get("fett"))), (self.s_kursiv, bool(t.get("kursiv"))), (self.s_unter, bool(t.get("unter")))):
            _still(x, wert, "setChecked")

    def _setze_feld_alt(self, f: dict) -> None:
        """„Textfeld“ ohne ``TextfeldAbschnitt`` (alter Aufbau, SmartArt)."""
        _still(self.f_winkel, float(f["winkel"]))
        for x, wert in ((self.f_anpassen, f["anpassen"] is not False), (self.f_umbruch, f["umbruch"] is not False)):
            _still(x, wert, "setChecked")
        for x, d in ((self.f_vertikal, f["vertikal"]), (self.f_richtung, f["richtung"])):
            _still(x, max(0, x.findData(d)), "setCurrentIndex")
        for k, x in self.f_rand.items():
            _still(x, float(f["raender"][k]))

    def werte(self) -> dict:
        w = super().werte()
        eff = self._effekt_werte(w)
        t = {"farbe": eff.get("farbe") or None, "effekt": self._effekt_oder_standard(eff),
             "groesse": self.s_groesse.value() if self.s_gesetzt["groesse"] else None,
             "name": self.s_name.currentFont().family() if self.s_gesetzt["name"] else None,
             "fett": True if self.s_fett.isChecked() else None, "kursiv": True if self.s_kursiv.isChecked() else None,
             "unter": True if self.s_unter.isChecked() else None}
        t["feld"] = self.a_feld.werte() if self.FOTO else self._feld_alt_werte()
        return t

    def _effekt_werte(self, w: dict) -> dict:
        eff = {k: v for k, v in w.items() if v is not None}
        if any(abs(f.value()) > 0.01 for f in (self.dr_x, self.dr_y, self.dr_z)):
            eff["text_3d"] = {"x": self.dr_x.value(), "y": self.dr_y.value(), "z": self.dr_z.value(), "perspektive": self.dr_pers.value()}
        if self._warp_art != "keine":
            eff["warp"] = {"art": self._warp_art}
        return eff

    @staticmethod
    def _effekt_oder_standard(eff: dict):
        """Die Effekte oder None, wenn sie der Standard sind (einfarbige Füllung ohne alles)."""
        standard = eff.get("fuell") == "farbe" and not eff.get("transparenz") and not eff.get("kontur") and not any(
            eff.get(k) for k in ("verlauf", "kontur_verlauf", "schatten", "reflektion", "leuchten", "d3", "text_3d", "warp")) and eff.get("kontur_form", "einfach") == "einfach"
        return None if standard else eff

    def _feld_alt_werte(self) -> dict:
        return {"vertikal": self.f_vertikal.currentData(), "richtung": self.f_richtung.currentData(), "winkel": self.f_winkel.value(),
                "anpassen": self.f_anpassen.isChecked(), "umbruch": self.f_umbruch.isChecked(),
                "raender": {k: x.value() for k, x in self.f_rand.items()}}

