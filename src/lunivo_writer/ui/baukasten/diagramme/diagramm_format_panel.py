"""„Formatierung“ für einen Teil des Diagramms in der rechten Seitenleiste (nach der Vorlage).

Der Baustein baut auf dem Panel für Bilder und Formen auf (``ObjektFormatPanel``): Füllung (Keine, Einfarbig, Farbverlauf, Textur, Muster, Bild, Automatisch, mit
Transparenz), Linie (Keine, Durchgezogen, Farbverlaufslinie, Automatisch; Transparenz, Breite, Strichart, Kombinierter Typ, Abschlusstyp, Verknüpfungstyp,
abgerundete Ecke, bei Linienreihen Pfeile) und die Effekte (Schatten, Reflektion, Leuchten, Weiche Kanten, 3D-Format, 3D-Drehung) sind dieselben Regler wie dort — nur
die Auswahlpunkte „Automatisch“ und die Felder der Linie kommen über die Erweiterungspunkte ``_zusatz_radios`` und ``_zusatz_felder`` dazu. Die Textoptionen sind das
Panel der Texteffekte (Textfüllung und -kontur, Effekte), ergänzt um Schrift und „Textfeld“.

Oben die zwei Hauptreiter „<Teil>optionen“ (der Name folgt dem gewählten Teil) und „Textoptionen“ als Reiter; darunter die Reiter mit Symbol: „Füllung und Linie“, „Effekte“ und —
je nach Teil — „Größe und Eigenschaften“ (Diagrammbereich), „Legendenoptionen“, „Achsenoptionen“ oder „Reihenoptionen“.

``setze(werte)`` füllt das Panel (meldet nichts); ``werte`` = {"teil", "name", "format" (``diagramm_teile.diagramm_teil_format_lesen``), "linienreihe" (bool),
"saeulen" (bool), "wertachse" (bool), "objekt" {"legende_pos", "breite_mm", "hoehe_mm", "dreh"}, "alt_titel", "alt_beschreibung"}. Die Änderungen kommen als
``geaendert(angaben)`` — die Schlüssel von ``diagramm_teile.FORMAT_SCHLUESSEL`` (``None`` entfernt = Automatisch) und die Sonderschlüssel ``objekt`` (Angaben des
Diagramms, z. B. ``legende_pos``), ``groesse`` ({"breite_mm", "hoehe_mm"}) und ``dreh`` (Grad); ``alt_geaendert(titel, beschreibung)`` beim Alternativtext;
``bild_gewuenscht`` bei „Bild wählen …“ (der Aufrufer kodiert das Bild mit ``diagramm_format.bild_kodieren`` und sendet ``fuell``).
"""
from __future__ import annotations


from PySide6.QtCore import QPointF, QSize, Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPainter, QPainterPath, QPalette, QPixmap
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QLabel, QTabBar, QComboBox, QDoubleSpinBox, QFontComboBox, QHBoxLayout, QLineEdit, QPushButton, QRadioButton,
    QVBoxLayout, QWidget,
)

from lunivo_writer.core.farben import Farbe
from lunivo_writer.editor.diagramme import diagramm_format as F
from lunivo_writer.editor.text import texteffekt as T
from lunivo_writer.editor.text.textfx import WARP_FORMEN, pfad_verformen
from lunivo_writer.ui.baukasten.dropdown.voreinstellung_menue import VoreinstellungMenue
from lunivo_writer.ui.baukasten.dropdown.kopf_dropdown import KopfDropdown, keine_zeile
from lunivo_writer.ui.baukasten.medien.alternativtext_abschnitt import AlternativtextAbschnitt
from lunivo_writer.ui.baukasten.formatierung.auto_felder_mixin import AutoFelderMixin
from lunivo_writer.ui.baukasten.formatierung.effekte_drei_mixin import NurDreiEffekteMixin
from lunivo_writer.ui.baukasten.dropdown.auswahl.farbpalette import FarbFeld
from lunivo_writer.ui.baukasten.dropdown.kopf_menue_mixin import KopfMenueMixin
from lunivo_writer.ui.baukasten.formatierung.textfeld_abschnitt import TextfeldAbschnitt
from lunivo_writer.ui.baukasten.dropdown.teil_menue import TeilMenueKnopf
from lunivo_writer.ui.baukasten.basis.linien import Linie
from lunivo_writer.ui.baukasten.controls.formular_gitter import UmbruchSchalter
from lunivo_writer.ui.baukasten.dropdown.text_kopf_menue_mixin import TextKopfMenueMixin
from lunivo_writer.ui.baukasten.formatierung.objektformat_panel import ObjektFormatPanel, _TextPanel
from lunivo_writer.ui.baukasten.controls.schiebe_feld import SchiebeFeld, SchrittFeld
from lunivo_writer.ui.baukasten.formatierung.text_fuellarten_mixin import TextFuellartenMixin
from lunivo_writer.ui.baukasten.dropdown.auswahl.strich_auswahl import StrichAuswahl
from lunivo_writer.ui.baukasten.formatierung.texteffekt_dialog import Abschnitt
from lunivo_writer.ui.widgets import icons
from lunivo_writer.ui.baukasten.basis.mass import (
    ABSTAND_NORMAL,
    ABSTAND_SPALTE,
    GROESSE_TEXTVERFORMUNG_KACHEL,
    ICON_MITTEL,
    RAND_FORMATSEITE,
    RAND_KEIN,
)
from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Auswahlfeld, Schriftauswahl

# Teile, deren Text sich formatieren lässt (Titel, Legende, Achsen, Legendeneinträge, Datenbeschriftungen)
TEXT_TEILE = ("diagrammbereich", "titel", "legende", "achse_horizontal", "achse_vertikal", "datenbeschriftung")
LEGENDEN_LAGEN = (("oben", "Oben"), ("unten", "Unten"), ("links", "Links"), ("rechts", "Rechts"))
RICHTUNGEN = (("waagerecht", "Waagerecht"), ("dreh90", "Um 90° drehen"), ("dreh270", "Um 270° drehen"), ("gestapelt", "Gestapelt"))
ABSCHLUSS = (("flach", "Flach"), ("rund", "Rund"), ("quadrat", "Quadratisch"))
VERKNUEPFUNG = (("rund", "Rund"), ("schraeg", "Abgeschrägt"), ("spitz", "Spitz"))
_OHNE = object()                                       # „Bildfüllung ohne Bild“: die Füllung bleibt, wie sie ist


def _optionen_name(teil: str) -> str:
    if teil.startswith("reihe_"):
        return "Reihe Optionen"
    if teil.startswith("legendeneintrag_"):
        return "Legendeneintrag Optionen"
    return {"titel": "Titel Optionen", "legende": "Legende Optionen", "achse_horizontal": "Achse Optionen", "achse_vertikal": "Achse Optionen",
            "zeichnungsbereich": "Zeichnungsbereich Optionen", "datenbeschriftung": "Datenbeschriftung Optionen"}.get(teil, "Diagramm Optionen")


def _text_teil(teil: str) -> bool:
    return teil in TEXT_TEILE or teil.startswith("legendeneintrag_")


def _combo(eintraege) -> QComboBox:
    c = Auswahlfeld()
    for k, n in eintraege:
        c.addItem(n, k)
    return c


def _strich_zeichner(art: str):
    """Zeichner für ``StrichAuswahl``: ein Strich der Strichart ``art`` über die Breite (schwarz)."""
    def z(p, r, farbe):
        pen = F.stift({"art": art, "breite": 1.6, "farbe": farbe.name()}); pen.setColor(farbe); p.setPen(pen)
        p.drawLine(QPointF(r.left(), r.center().y()), QPointF(r.right(), r.center().y()))
    return z


def _kombi_zeichner(form: str):
    """Zeichner für ``StrichAuswahl``: eine Linie des kombinierten Typs ``form`` (Flächen aus ``textfx._kontur_pfade``)."""
    def z(p, r, farbe):
        from lunivo_writer.editor.text import textfx as X
        pf = QPainterPath(); pf.moveTo(r.left(), r.center().y()); pf.lineTo(r.right(), r.center().y())
        p.setPen(Qt.NoPen); p.setBrush(farbe)
        for fl in X._kontur_pfade(pf, 3.0, form):
            p.drawPath(fl)
    return z


def _still(x, wert, setter: str = "setValue") -> None:
    x.blockSignals(True); getattr(x, setter)(wert); x.blockSignals(False)


class _AutoWert(QWidget):
    """Eine Zahl, die „Automatisch“ sein kann (Minimum, Maximum, Hauptintervall der Achse): Haken + Feld. ``wert()`` ist None bei Automatisch."""
    geaendert = Signal()

    def __init__(self, vorgabe: float = 0.0):
        super().__init__()
        h = QHBoxLayout(self); h.setContentsMargins(*RAND_KEIN); h.setSpacing(ABSTAND_NORMAL)
        self.auto = QCheckBox("Auto"); self.auto.setChecked(True)
        self.feld = QDoubleSpinBox(); self.feld.setRange(-1e9, 1e9); self.feld.setDecimals(2); self.feld.setValue(vorgabe); self.feld.setEnabled(False)
        self.feld.setMinimumWidth(0)
        h.addWidget(self.auto); h.addWidget(self.feld, 1)
        self.auto.toggled.connect(lambda an: (self.feld.setEnabled(not an), self.geaendert.emit()))
        self.feld.valueChanged.connect(lambda *_: self.geaendert.emit())

    def wert(self) -> float | None:
        return None if self.auto.isChecked() else self.feld.value()

    def setze(self, w: float | None) -> None:
        for x in (self.auto, self.feld):
            x.blockSignals(True)
        self.auto.setChecked(w is None); self.feld.setEnabled(w is not None)
        if w is not None:
            self.feld.setValue(float(w))
        for x in (self.auto, self.feld):
            x.blockSignals(False)


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
            d3 = e.get("text_3d") or {}
            for f, k, v in ((self.dr_x, "x", 0), (self.dr_y, "y", 0), (self.dr_z, "z", 0), (self.dr_pers, "perspektive", 45)):
                _still(f, float(d3[k]) if d3.get(k) is not None else float(v))
            self._warp_setzen((e.get("warp") or {}).get("art", "keine"), melden=False)
        if not hasattr(self, "f_rand"):
            return
        f = F.feld_von(t, w.get("teil"))
        _still(self.s_name, QFont(t.get("name") or self.font().family()), "setCurrentFont")
        self.s_gesetzt = {"name": bool(t.get("name")), "groesse": bool(t.get("groesse"))}
        _still(self.s_groesse, float(t.get("groesse") or 10))
        for x, wert in ((self.s_fett, bool(t.get("fett"))), (self.s_kursiv, bool(t.get("kursiv"))), (self.s_unter, bool(t.get("unter")))):
            _still(x, wert, "setChecked")
        if self.FOTO:
            self.a_feld.setze(f)
            return
        _still(self.f_winkel, float(f["winkel"]))
        for x, wert in ((self.f_anpassen, f["anpassen"] is not False), (self.f_umbruch, f["umbruch"] is not False)):
            _still(x, wert, "setChecked")
        for x, d in ((self.f_vertikal, f["vertikal"]), (self.f_richtung, f["richtung"])):
            _still(x, max(0, x.findData(d)), "setCurrentIndex")
        for k, x in self.f_rand.items():
            _still(x, float(f["raender"][k]))

    def werte(self) -> dict:
        w = super().werte()
        eff = {k: v for k, v in w.items() if v is not None}
        if any(abs(f.value()) > 0.01 for f in (self.dr_x, self.dr_y, self.dr_z)):
            eff["text_3d"] = {"x": self.dr_x.value(), "y": self.dr_y.value(), "z": self.dr_z.value(), "perspektive": self.dr_pers.value()}
        if self._warp_art != "keine":
            eff["warp"] = {"art": self._warp_art}
        standard = eff.get("fuell") == "farbe" and not eff.get("transparenz") and not eff.get("kontur") and not any(
            eff.get(k) for k in ("verlauf", "kontur_verlauf", "schatten", "reflektion", "leuchten", "d3", "text_3d", "warp")) and eff.get("kontur_form", "einfach") == "einfach"
        t = {"farbe": eff.get("farbe") or None, "effekt": None if standard else eff,
             "groesse": self.s_groesse.value() if self.s_gesetzt["groesse"] else None,
             "name": self.s_name.currentFont().family() if self.s_gesetzt["name"] else None,
             "fett": True if self.s_fett.isChecked() else None, "kursiv": True if self.s_kursiv.isChecked() else None,
             "unter": True if self.s_unter.isChecked() else None}
        t["feld"] = self.a_feld.werte() if self.FOTO else {"vertikal": self.f_vertikal.currentData(), "richtung": self.f_richtung.currentData(), "winkel": self.f_winkel.value(),
                     "anpassen": self.f_anpassen.isChecked(), "umbruch": self.f_umbruch.isChecked(),
                     "raender": {k: x.value() for k, x in self.f_rand.items()}}
        return t


# ---- das Panel ------------------------------------------------------------------------------------------------------------------------
class DiagrammFormatPanel(KopfMenueMixin, NurDreiEffekteMixin, AutoFelderMixin, ObjektFormatPanel):
    TEXT_KLASSE = DiagrammTextPanel
    _bild_modus = False
    alt_geaendert = Signal(str, str)
    teil_gewaehlt = Signal(str)                     # Wahl in der Teilliste am Hauptreiter (Pfeil neben „DIAGRAMM OPTIONEN“)

    def __init__(self, parent=None, werte: dict | None = None):
        self._teil = "diagrammbereich"
        self._bild_b64 = ""
        self._fertig = False
        self._luecke_an = False
        super().__init__(parent, werte)
        self._stumm = True
        self.teil_wahl = TeilMenueKnopf()                                                      # der Pfeil am Hauptreiter „DIAGRAMM OPTIONEN ▾“ (Liste der Teile)
        self.teil_wahl.gewaehlt.connect(self.teil_gewaehlt)
        self._kopf_menues_bauen()                                                               # Dropdowns in den Köpfen von Füllung und Linie
        self.optionen.tabBar().setTabButton(0, QTabBar.RightSide, self.teil_wahl)      # die Teilliste „▾“ am ersten Hauptreiter, mit gewöhnlicher wie flacher Leiste
        self.text_panel.geaendert.connect(lambda t: self._melde(text=t))
        self.optionen_seite = self._seite_optionen()
        self.reiter.addTab(self._scroll(self.optionen_seite), icons.icon("sliders-horizontal", ICON_MITTEL), "Optionen")
        self.eigenschaften_seite = self._seite_eigenschaften()
        self.reiter.addTab(self._scroll(self.eigenschaften_seite), icons.icon("scaling", ICON_MITTEL), "Größe und Eigenschaften")
        self._reiter_kurz()
        for a in (self.a_fuell, self.a_kontur) + (() if self.NUR_DREI_EFFEKTE else (self.a_schatten,)):         # wie in der Vorlage: Füllung und Linie offen, die Effekte zu
            a.knopf.setChecked(True)
        self._fertig = True
        self._stumm = False
        self.setze(werte or {})

    def _reiter_kurz(self) -> None:
        """Kurze Reitertexte, damit sie bei 300 px lesbar bleiben; der volle Name steht als Tooltip (nur Texte)."""
        kurz = {"Füllung und Linie": "Füllung", "Textfüllung und -kontur": "Füllung", "Größe und Eigenschaften": "Größe",
                "Legendenoptionen": "Legende", "Achsenoptionen": "Achse", "Reihenoptionen": "Reihe"}
        for rw in (self.reiter, self.text_panel.reiter):
            for i in range(rw.count()):
                voll = rw.tabText(i)
                if voll in kurz:
                    rw.setTabToolTip(i, voll); rw.setTabText(i, kurz[voll])

    # ---- Erweiterungen der Seite „Füllung und Linie“ ----------------------------------------------------------------------------
    def _zusatz_radios(self, abschnitt: str) -> list:
        if abschnitt == "fuell":
            self.r_auto = QRadioButton("Automatische Füllung")
            r = [self.r_auto]
        else:
            self.k_verlauf, self.k_auto = QRadioButton("Farbverlaufslinie"), QRadioButton("Automatische Linie")
            r = [self.k_verlauf, self.k_auto]
        for x in r:
            x.toggled.connect(self._neu)
        return r

    def _zusatz_felder(self, abschnitt: str, a: Abschnitt) -> None:
        if abschnitt == "fuell":
            self.textur.currentIndexChanged.connect(lambda *_: setattr(self, "_bild_modus", False))      # vor dem Verbinden der Basis: die Struktur gilt dann
            self.f_trans = SchiebeFeld(0, 100, " %")
            self.v_winkel = SchiebeFeld(0, 360, "°", 5, 0, 90)
            self.g_farbe.zeile("Transparenz:", self.f_trans); self.g_verlauf.zeile("Winkel des Verlaufs:", self.v_winkel)
            self.f_trans.valueChanged.connect(lambda *_: (self._farbe_waehlen(), self._neu()))
            self.v_winkel.valueChanged.connect(lambda *_: (self.r_verlauf.setChecked(True), self._neu()))
            return
        self.kv1, self.kv2 = FarbFeld(Farbe.ROT, "Farbe 1"), FarbFeld(Farbe.BLAU_DUNKEL, "Farbe 2")
        self.kv_winkel = SchiebeFeld(0, 360, "°", 5)
        self.k_trans = SchiebeFeld(0, 100, " %")
        self.l_kombi = StrichAuswahl([(k, _kombi_zeichner(k), n) for k, n in T.KONTUR_FORMEN])
        self.l_kombi.gewaehlt.connect(lambda *_: (self._linie_waehlen(), self._neu()))
        self.k_wahl.breite.hide(); self.k_wahl.art.hide()                  # sie bleiben die Datenhalter der Basis; sichtbar sind Zähler und Strichauswahl
        self.k_art.clear()
        for k, n in F.STRICHTYPEN:
            self.k_art.addItem(n, k)
        self.s_art = StrichAuswahl([(k, _strich_zeichner(k), n) for k, n in F.STRICHTYPEN])
        self.s_art.gewaehlt.connect(lambda k: self.k_art.setCurrentIndex(max(0, self.k_art.findData(k))))
        self.k_art.currentIndexChanged.connect(lambda *_: self.s_art.setze(str(self.k_art.currentData())))
        self.s_breite = SchrittFeld(0, 1584, "pt", 0.25, 2, 0.75)
        self.s_breite.valueChanged.connect(lambda *_: (self._linie_waehlen(), self._neu()))
        self.l_abschluss, self.l_verknuepfung = _combo(ABSCHLUSS), _combo(VERKNUEPFUNG)
        self.l_rund = UmbruchSchalter("Abgerundete Ecke")
        g, f = self.g_lin_verlauf, self.g_lin_form
        g.zeile("Farbe 1:", self.kv1); g.zeile("Farbe 2:", self.kv2); g.zeile("Winkel:", self.kv_winkel)
        # Reihenfolge der Vorlage: Farbe, Transparenz, Breite, Kombinierter Typ, Strichtyp, Abschluss, Verknüpfung (die Teile der Zeile von ``k_wahl`` einzeln)
        self.l_farbe_text = QLabel("Farbe:")
        f.zeile(self.l_farbe_text, self.k_farbe); f.zeile("Transparenz:", self.k_trans); f.zeile("Breite:", self.s_breite)
        f.zeile("Kombinierter Typ:", self.l_kombi); f.zeile("Strichtyp:", self.s_art); f.zeile("Abschlusstyp:", self.l_abschluss)
        f.zeile("Verknüpfungstyp:", self.l_verknuepfung)
        # Pfeile (wie in der Vorlage in der Linie, immer zu sehen, grau außer bei Linienreihen): je Pfeil Art und Größe
        self._linienreihe = False
        self.p_anfang, self.p_ende = _combo(F.PFEILE), _combo(F.PFEILE)
        self.p_groesse_anfang, self.p_groesse_ende = _combo(F.PFEIL_GROESSEN), _combo(F.PFEIL_GROESSEN)
        self.l_pfeil_anfang, self.l_pfeil_ende = QLabel("Anfangspfeil:"), QLabel("Endpfeil:")
        for l, a, g in ((self.l_pfeil_anfang, self.p_anfang, self.p_groesse_anfang), (self.l_pfeil_ende, self.p_ende, self.p_groesse_ende)):
            f.zeile(l, a); f.zeile("Größe:", g)
        f.breit(self.l_rund)
        for sig in (self.kv1.farbeGeaendert, self.kv2.farbeGeaendert, self.kv_winkel.valueChanged):
            sig.connect(lambda *_: (self.k_verlauf.setChecked(True), self._neu()))
        for sig in (self.k_trans.valueChanged, self.l_abschluss.currentIndexChanged, self.l_verknuepfung.currentIndexChanged,
                    self.l_rund.toggled):
            sig.connect(lambda *_: (self._linie_waehlen(), self._neu()))
        for sig in (self.p_anfang.currentIndexChanged, self.p_ende.currentIndexChanged, self.p_groesse_anfang.currentIndexChanged,
                    self.p_groesse_ende.currentIndexChanged):
            sig.connect(lambda *_: (self._linie_waehlen(), self._neu()))
        self._pfeile_freigeben(False)

    def _pfeile_freigeben(self, an: bool) -> None:
        self._linienreihe = an
        for x in (self.p_anfang, self.p_ende, self.p_groesse_anfang, self.p_groesse_ende, self.l_pfeil_anfang, self.l_pfeil_ende):
            x.setEnabled(an)

    def _bild_waehlen(self) -> None:
        self._bild_modus = True
        self.r_textur.setChecked(True)

    def fuellung_waehlen(self, art: str) -> None:
        if art == "bild":
            self._bild_modus = True; art = "textur"
        elif art == "textur":
            self._bild_modus = False
        super().fuellung_waehlen(art)

    def _farbe_waehlen(self) -> None:
        if self.r_auto.isChecked() or self.r_keine.isChecked():
            self.r_farbe.setChecked(True)

    def _k_breite(self) -> float:
        return float(self.s_breite.value())

    def _k_breite_setzen(self, pt: float) -> None:
        _still(self.s_breite, float(pt))

    def _linie_waehlen(self) -> None:
        if self.k_auto.isChecked() or self.k_keine.isChecked():
            self.k_linie.setChecked(True)

    def _seite_fuellung(self, w: dict) -> QWidget:
        seite = super()._seite_fuellung(w)
        self.r_textur.setText("Bild- oder Texturfüllung"); self.r_bild.setVisible(False)       # ein Feld mit Unterwahl (Struktur oder Bild)
        self._bild_modus = False
        self.bild_knopf.clicked.connect(self._bild_waehlen)
        self.k_wahl.geaendert.connect(lambda *_: self._linie_waehlen())
        return seite

    # ---- Seite „Optionen“ (Legende, Achse, Reihe) ---------------------------------------------------------------------------------
    def _seite_optionen(self) -> QWidget:
        seite = QWidget(); v = QVBoxLayout(seite); v.setSpacing(ABSTAND_SPALTE); v.setContentsMargins(*RAND_FORMATSEITE)
        self.a_legende = Abschnitt("Legendenoptionen")
        self.o_lage = _combo(LEGENDEN_LAGEN)
        self.a_legende.zeile("Legendenposition:", self.o_lage)
        self.o_lage.currentIndexChanged.connect(lambda *_: self._melde(objekt={"legende_pos": self.o_lage.currentData()}))
        self.a_achse = Abschnitt("Achsenoptionen")
        self.o_min, self.o_max, self.o_intervall = _AutoWert(0.0), _AutoWert(10.0), _AutoWert(1.0)
        self.o_umkehren = UmbruchSchalter("Werte in umgekehrter Reihenfolge")
        self.o_beschr = _combo((("neben", "Neben der Achse"), ("keine", "Keine")))
        self.o_neben = _AutoWert(0.5)
        self.o_format = QLineEdit(); self.o_format.setPlaceholderText("Automatisch, z. B. %.1f oder %d"); self.o_format.setToolTip("Muster der Zahlen an der Achse (printf: %.2f, %d, %.0f %%)")
        self.a_achse.zeile("Minimum:", self.o_min); self.a_achse.zeile("Maximum:", self.o_max); self.a_achse.zeile("Hauptintervall:", self.o_intervall)
        self.a_achse.zeile("Nebenintervall:", self.o_neben); self.a_achse.zeile("Zahlenformat (Muster):", self.o_format)
        self._wert_zeilen = (self.o_min, self.o_max, self.o_intervall, self.o_neben, self.o_format)
        self.a_achse.breit(self.o_umkehren); self.a_achse.zeile("Beschriftungsposition:", self.o_beschr)
        for sig in (self.o_min.geaendert, self.o_max.geaendert, self.o_intervall.geaendert, self.o_neben.geaendert, self.o_format.editingFinished,
                    self.o_umkehren.toggled, self.o_beschr.currentIndexChanged):
            sig.connect(lambda *_: self._achse_melden())
        self.a_reihe = Abschnitt("Reihenoptionen")
        self.o_luecke = SchiebeFeld(0, 500, " %", 5, 0, 100)
        self.a_reihe.zeile("Lückenbreite:", self.o_luecke)
        self.a_reihe_linie = Abschnitt("Linienreihe")
        self.o_glatt, self.o_punkte = UmbruchSchalter("Linie glätten"), UmbruchSchalter("Datenpunkte anzeigen")
        self.a_reihe_linie.breit(self.o_glatt); self.a_reihe_linie.breit(self.o_punkte)
        self.o_luecke.valueChanged.connect(lambda *_: self._reihe_melden())
        for x in (self.o_glatt, self.o_punkte):
            x.toggled.connect(lambda *_: self._reihe_melden())
        for a in (self.a_legende, self.a_achse, self.a_reihe, self.a_reihe_linie):
            v.addWidget(a); a.knopf.setChecked(True)
        v.addStretch(1)
        return seite

    def _achse_melden(self) -> None:
        self._melde(achse={"min": self.o_min.wert(), "max": self.o_max.wert(), "intervall": self.o_intervall.wert(),
                           "neben": self.o_neben.wert(), "format": self.o_format.text().strip() or None,
                           "umkehren": True if self.o_umkehren.isChecked() else None,
                           "beschriftung": self.o_beschr.currentData() if self.o_beschr.currentData() != "neben" else None})

    def _reihe_melden(self) -> None:
        self._melde(reihe={"luecke": self.o_luecke.value() if self._luecke_an else None, "glatt": True if self.o_glatt.isChecked() else None,
                           "punkte": True if self.o_punkte.isChecked() else None})

    # ---- Seite „Größe und Eigenschaften“ ------------------------------------------------------------------------------------------
    def _seite_eigenschaften(self) -> QWidget:
        """Nach der Vorlage nur „Alternativtext“ (Größe und Drehung stellt das Fenster „Layout“ des Objekts ein)."""
        seite = QWidget(); v = QVBoxLayout(seite); v.setSpacing(ABSTAND_SPALTE); v.setContentsMargins(*RAND_FORMATSEITE)
        self.a_alt = AlternativtextAbschnitt()
        self.a_alt.geaendert.connect(lambda t, b: None if self._stumm or not self._fertig else self.alt_geaendert.emit(t, b))
        self.alt_titel, self.alt_text = self.a_alt.titel_feld, self.a_alt.text_feld
        self._alt_timer = self.a_alt._timer
        v.addWidget(self.a_alt); v.addStretch(1)
        return seite

    # ---- Melden --------------------------------------------------------------------------------------------------------------------------
    def _melde(self, **kw) -> None:
        if not self._stumm and self._fertig:
            self.geaendert.emit(kw)

    def _melden(self) -> None:                                              # Füllung, Linie und Effekte (Seiten 1 und 2): alles, was dort steht
        try:
            if not self._stumm and self._fertig:
                self.geaendert.emit(self.werte())
        except RuntimeError:                       # das Fenster wurde schon abgebaut, bevor die verzögerte Meldung kam
            pass

    def werte(self) -> dict:
        """Füllung, Linie und Effekte im Format des Teilformats (``None`` = entfernen)."""
        out: dict = {}
        fu = self._fuell_wert()
        if fu is not _OHNE:
            out["fuell"] = fu
        out["linie"] = self._linie_wert()
        fx = self._werte_effekte()
        for k in F.FX_SCHLUESSEL:
            out[k] = fx.get(k)
        return out

    def _fuell_wert(self):
        if self.r_auto.isChecked():
            return None
        if self.r_keine.isChecked():
            return ""
        tr = int(self.f_trans.value())
        if self.r_verlauf.isChecked():
            d = {"art": "graduell", "dunkel": self.v1.farbe or Farbe.BLAU_DUNKEL, "hell": self.v2.farbe or Farbe.WEISS, "winkel": self.v_winkel.value()}
            d["farbe"] = d["dunkel"]
        elif self.r_textur.isChecked() and self._bild_modus:
            if not self._bild_b64:
                return _OHNE
            d = {"art": "bild", "bild_b64": self._bild_b64}
        elif self.r_textur.isChecked():
            d = {"art": "textur", "key": self.textur.currentData()}
        elif self.r_muster.isChecked():
            d = {"art": "muster", "key": self.muster.currentData(), "farbe": self.m_farbe.farbe or Farbe.TINTE, "grund": Farbe.WEISS}
        elif self.r_bild.isChecked():
            if not self._bild_b64:
                return _OHNE
            d = {"art": "bild", "bild_b64": self._bild_b64}
        else:
            c = self.farbe.farbe or Farbe.BLAU
            if not tr:
                return c
            d = {"art": "farbe", "farbe": c}
        if tr:
            d["transparenz"] = tr
        return d

    def _linie_wert(self) -> dict | None:
        if self.k_auto.isChecked():
            return None
        voll = {"keine": None, "farbe": None, "breite": None, "art": None, "transparenz": None, "kombiniert": None, "abschluss": None, "verknuepfung": None,
                "rund": None, "verlauf": None, "pfeil_anfang": None, "pfeil_ende": None, "pfeil_groesse": None,
                "pfeil_groesse_anfang": None, "pfeil_groesse_ende": None}
        if self.k_keine.isChecked():
            return {**voll, "keine": True}
        voll.update(farbe=self.k_farbe.farbe or Farbe.GRAU, breite=self._k_breite(), art=self.k_art.currentData() or "einfach",
                    transparenz=int(self.k_trans.value()) or None, kombiniert=self.l_kombi.aktuell() if self.l_kombi.aktuell() != "einfach" else None,
                    abschluss=self.l_abschluss.currentData() if self.l_abschluss.currentData() != "flach" else None,
                    verknuepfung=self.l_verknuepfung.currentData() if self.l_verknuepfung.currentData() != "rund" else None,
                    rund=True if self.l_rund.isChecked() else None)
        if self.k_verlauf.isChecked():
            voll["verlauf"] = {"farbe1": self.kv1.farbe or Farbe.ROT, "farbe2": self.kv2.farbe or Farbe.BLAU_DUNKEL, "winkel": self.kv_winkel.value()}
        if self._linienreihe:
            voll.update(pfeil_anfang=self.p_anfang.currentData() if self.p_anfang.currentData() != "keiner" else None,
                        pfeil_ende=self.p_ende.currentData() if self.p_ende.currentData() != "keiner" else None,
                        pfeil_groesse_anfang=self.p_groesse_anfang.currentData() if self.p_groesse_anfang.currentData() != 1.0 else None,
                        pfeil_groesse_ende=self.p_groesse_ende.currentData() if self.p_groesse_ende.currentData() != 1.0 else None)
        return voll

    # ---- Füllen ----------------------------------------------------------------------------------------------------------------------
    def _setze(self, w: dict) -> None:
        fmt = w.get("format") or {}
        super()._setze({**F.fx_normal(fmt), "_fmt": fmt})

    def _setze_fuellung(self, w: dict) -> None:
        fmt = w.get("_fmt") or {}
        fu, li = fmt.get("fuell"), fmt.get("linie")
        d = F.fuell_dict(fu)
        art = d.get("art", "farbe") if d else None
        radios = (self.r_keine, self.r_farbe, self.r_verlauf, self.r_textur, self.r_muster, self.r_bild, self.r_auto, self.k_keine, self.k_linie, self.k_verlauf, self.k_auto)
        for x in radios:
            x.blockSignals(True)
        self.r_auto.setChecked(fu is None); self.r_keine.setChecked(fu == "" or art == "keine"); self.r_farbe.setChecked(art == "farbe")
        self.r_verlauf.setChecked(art in ("graduell", "verlauf")); self.r_textur.setChecked(art in ("textur", "bild")); self.r_muster.setChecked(art == "muster")
        self.r_bild.setChecked(False); self._bild_modus = art == "bild"
        verlauf = bool(li and li.get("verlauf"))
        keine = F.linie_keine(li)
        self.k_auto.setChecked(not li); self.k_keine.setChecked(keine); self.k_verlauf.setChecked(bool(li) and not keine and verlauf)
        self.k_linie.setChecked(bool(li) and not keine and not verlauf)
        for x in radios:
            x.blockSignals(False)
        self._bild_b64 = (d or {}).get("bild_b64", "") if art == "bild" else ""
        d = d or {}
        self.farbe.setFarbe("")                                             # leere Farbe = „Automatisch“ (wie überall: gesetzte Farben zeigen ihre Hex-Zahl)
        if art == "farbe":
            self.farbe.setFarbe(d.get("farbe", Farbe.BLAU))
        elif art in ("graduell", "verlauf"):
            self.v1.setFarbe(d.get("dunkel", d.get("farbe", Farbe.BLAU_DUNKEL))); self.v2.setFarbe(d.get("hell", Farbe.BLAU_HELL))
        elif art == "textur":
            self.textur.setCurrentIndex(max(0, self.textur.findData(d.get("key"))))
        elif art == "muster":
            self.muster.setCurrentIndex(max(0, self.muster.findData(d.get("key")))); self.m_farbe.setFarbe(d.get("farbe", Farbe.TINTE))
        self.f_trans.setValue(float(d.get("transparenz", 0))); self.v_winkel.setValue(float(d.get("winkel", 90)))
        li = li or {}
        self.k_farbe.keine_text = "Automatisch"
        _still(self.k_wahl, Linie(li.get("farbe", ""), float(li.get("breite", 1.0)), F.strich_schluessel(li.get("art"))), "setLinie")
        self.s_art.setze(F.strich_schluessel(li.get("art"))); _still(self.s_breite, float(li.get("breite", 1.0 if li else 0.75)))      # still: sonst wählt die Änderung „Durchgezogene Linie“
        self.k_trans.setValue(float(li.get("transparenz", 0)))
        self.l_kombi.setze(li.get("kombiniert", "einfach"))
        for c, k, vorgabe in ((self.l_abschluss, "abschluss", "flach"), (self.l_verknuepfung, "verknuepfung", "rund"),
                              (self.p_anfang, "pfeil_anfang", "keiner"), (self.p_ende, "pfeil_ende", "keiner")):
            _still(c, max(0, c.findData(li.get(k, vorgabe))), "setCurrentIndex")
        _still(self.l_rund, bool(li.get("rund")), "setChecked")
        for c, k in ((self.p_groesse_anfang, "pfeil_groesse_anfang"), (self.p_groesse_ende, "pfeil_groesse_ende")):
            _still(c, max(0, c.findData(float(li.get(k, li.get("pfeil_groesse", 1.0))))), "setCurrentIndex")
        v = li.get("verlauf") or {}
        self.kv1.setFarbe(v.get("farbe1", Farbe.ROT)); self.kv2.setFarbe(v.get("farbe2", Farbe.BLAU_DUNKEL)); self.kv_winkel.setValue(float(v.get("winkel", 0)))
        self._felder_zeigen()

    def setze(self, werte: dict) -> None:
        """Die Felder mit dem Format des Teils füllen; meldet nichts."""
        if not self._fertig:
            super().setze(werte)
            return
        alt, self._stumm = self._stumm, True
        try:
            self._teil = werte.get("teil") or "diagrammbereich"
            self._teile_zeigen(werte)
            self._teil_einrichten(werte)
            super().setze(werte)
            f = werte.get("format") or {}
            self.text_panel.setze({"text": f.get("text") or {}, "teil": self._teil})
            if getattr(self.text_panel, "FOTO", False):               # Ränder usw. nur außer beim Titel (Vorlage: dort grau); „Text nicht drehen“ nur beim gedrehten Diagramm
                self.text_panel.a_feld.freigeben(self._teil != "titel", bool((werte.get("objekt") or {}).get("dreh")))
            self._setze_optionen(werte, f)
        finally:
            self._stumm = alt

    def _teile_zeigen(self, werte: dict) -> None:
        """Die Liste „Teil“ mit den Teilen des Diagramms (``werte["teile"]``, sonst nur der gewählte) und dem gewählten Eintrag."""
        teile = list(werte.get("teile") or [(self._teil, werte.get("name") or "Diagrammbereich")])
        self.teil_wahl.setze(teile, self._teil)

    def _teil_einrichten(self, werte: dict) -> None:
        teil = self._teil
        self.optionen.setTabText(0, _optionen_name(teil))
        text_ok = _text_teil(teil)
        self.optionen.setTabEnabled(1, text_ok)
        self.optionen.setTabEnabled(0, teil != "datenbeschriftung")
        if (not text_ok and self.optionen.currentIndex() == 1) or (teil == "datenbeschriftung" and self.optionen.currentIndex() == 0):
            self.optionen_waehlen(1 if teil == "datenbeschriftung" else 0)
        legende, achse, reihe, bereich = teil == "legende", teil.startswith("achse_"), teil.startswith("reihe_"), teil == "diagrammbereich"
        self.reiter.setTabVisible(2, legende or achse or reihe)
        self.reiter.setTabText(2, "Legendenoptionen" if legende else "Achsenoptionen" if achse else "Reihenoptionen")
        self._reiter_kurz()
        self.reiter.setTabVisible(3, bereich)
        self._luecke_an = reihe and bool(werte.get("saeulen"))
        for a, an in ((self.a_legende, legende), (self.a_achse, achse), (self.a_reihe, self._luecke_an),
                      (self.a_reihe_linie, reihe and bool(werte.get("linienreihe")))):
            a.setVisible(an)
        self._pfeile_freigeben(reihe and bool(werte.get("linienreihe")))
        for x in self._wert_zeilen:                                         # Minimum, Maximum, Hauptintervall: nur die Wertachse
            x.setEnabled(bool(werte.get("wertachse", True)))

    def _setze_optionen(self, werte: dict, f: dict) -> None:
        o = werte.get("objekt") or {}
        _still(self.o_lage, max(0, self.o_lage.findData(o.get("legende_pos", "unten"))), "setCurrentIndex")
        a = f.get("achse") or {}
        self.o_min.setze(a.get("min")); self.o_max.setze(a.get("max")); self.o_intervall.setze(a.get("intervall"))
        self.o_neben.setze(a.get("neben")); _still(self.o_format, a.get("format") or "", "setText")
        _still(self.o_umkehren, bool(a.get("umkehren")), "setChecked")
        _still(self.o_beschr, max(0, self.o_beschr.findData(a.get("beschriftung", "neben"))), "setCurrentIndex")
        r = f.get("reihe") or {}
        _still(self.o_luecke, float(r.get("luecke", 100))); _still(self.o_glatt, bool(r.get("glatt")), "setChecked"); _still(self.o_punkte, bool(r.get("punkte")), "setChecked")
        self.a_alt.setze(werte.get("alt_titel") or "", werte.get("alt_beschreibung") or "")
