"""„Formatierung“ für einen Teil des Diagramms in der rechten Seitenleiste (nach der Vorlage).

Der Baustein baut auf dem Panel für Bilder und Formen auf (``ObjektFormatPanel``): Füllung (Keine, Einfarbig, Farbverlauf, Textur, Muster, Bild, Automatisch, mit
Transparenz), Linie (Keine, Durchgezogen, Farbverlaufslinie, Automatisch; Transparenz, Breite, Strichart, Kombinierter Typ, Abschlusstyp, Verknüpfungstyp,
abgerundete Ecke, bei Linienreihen Pfeile) und die Effekte (Schatten, Reflektion, Leuchten, Weiche Kanten, 3D-Format, 3D-Drehung) sind dieselben Regler wie dort — nur
die Auswahlpunkte „Automatisch“ und die Felder der Linie kommen über die Erweiterungspunkte ``_zusatz_radios`` und ``_zusatz_felder`` dazu. Die Textoptionen sind das
Panel der Texteffekte (Textfüllung und -kontur, Effekte), ergänzt um Schrift und „Textfeld“.

Oben die zwei Hauptreiter „<TEIL> OPTIONEN“ (der Name folgt dem gewählten Teil) und „TEXTOPTIONEN“; darunter die Reiter mit Symbol: „Füllung und Linie“, „Effekte“ und —
je nach Teil — „Größe und Eigenschaften“ (Diagrammbereich), „Legendenoptionen“, „Achsenoptionen“ oder „Reihenoptionen“.

``setze(werte)`` füllt das Panel (meldet nichts); ``werte`` = {"teil", "name", "format" (``diagramm_teile.diagramm_teil_format_lesen``), "linienreihe" (bool),
"saeulen" (bool), "wertachse" (bool), "objekt" {"legende_pos", "breite_mm", "hoehe_mm", "dreh"}, "alt_titel", "alt_beschreibung"}. Die Änderungen kommen als
``geaendert(angaben)`` — die Schlüssel von ``diagramm_teile.FORMAT_SCHLUESSEL`` (``None`` entfernt = Automatisch) und die Sonderschlüssel ``objekt`` (Angaben des
Diagramms, z. B. ``legende_pos``), ``groesse`` ({"breite_mm", "hoehe_mm"}) und ``dreh`` (Grad); ``alt_geaendert(titel, beschreibung)`` beim Alternativtext;
``bild_gewuenscht`` bei „Bild wählen …“ (der Aufrufer kodiert das Bild mit ``diagramm_format.bild_kodieren`` und sendet ``fuell``).
"""
from __future__ import annotations

from PySide6.QtCore import QPoint, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (QCheckBox, QGridLayout, QLabel, QMenu, QToolButton, QComboBox, QDoubleSpinBox, QFontComboBox, QHBoxLayout, QLineEdit, QPlainTextEdit, QRadioButton, QVBoxLayout, QWidget)

from lunivo_writer.core.farben import Farbe
from lunivo_writer.editor import diagramm_format as F
from lunivo_writer.editor import texteffekt as T
from lunivo_writer.editor import muster as M
from lunivo_writer.ui.baukasten.farbpalette import FarbFeld, FarbPalette
from lunivo_writer.ui.baukasten.objekt_menues import TEXTUREN, _textur
from lunivo_writer.ui.baukasten.formular_gitter import UmbruchSchalter
from lunivo_writer.ui.baukasten.mass_feld import EinheitFeld
from lunivo_writer.ui.baukasten.objektformat_panel import ObjektFormatPanel, _TextPanel
from lunivo_writer.ui.baukasten.schiebe_feld import SchiebeFeld, SchrittFeld
from lunivo_writer.ui.baukasten.texteffekt_dialog import Abschnitt
from lunivo_writer.ui.widgets import icons

# Teile, deren Text sich formatieren lässt (Titel, Legende, Achsen, Legendeneinträge, Datenbeschriftungen)
TEXT_TEILE = ("diagrammbereich", "titel", "legende", "achse_horizontal", "achse_vertikal", "datenbeschriftung")
LEGENDEN_LAGEN = (("oben", "Oben"), ("unten", "Unten"), ("links", "Links"), ("rechts", "Rechts"))
RICHTUNGEN = (("waagerecht", "Waagerecht"), ("dreh90", "Um 90° drehen"), ("dreh270", "Um 270° drehen"), ("gestapelt", "Gestapelt"))
VERTIKAL = (("oben", "Oben"), ("mitte", "Mittig"), ("unten", "Unten"))
ABSCHLUSS = (("flach", "Flach"), ("rund", "Rund"), ("quadrat", "Quadratisch"))
VERKNUEPFUNG = (("rund", "Rund"), ("schraeg", "Abgeschrägt"), ("spitz", "Spitz"))
_OHNE = object()                                       # „Bildfüllung ohne Bild“: die Füllung bleibt, wie sie ist


def _optionen_name(teil: str) -> str:
    if teil.startswith("reihe_"):
        return "REIHE OPTIONEN"
    if teil.startswith("legendeneintrag_"):
        return "LEGENDENEINTRAG OPTIONEN"
    return {"titel": "TITEL OPTIONEN", "legende": "LEGENDE OPTIONEN", "achse_horizontal": "ACHSE OPTIONEN", "achse_vertikal": "ACHSE OPTIONEN",
            "zeichnungsbereich": "ZEICHNUNGSBEREICH OPTIONEN", "datenbeschriftung": "DATENBESCHRIFTUNG OPTIONEN"}.get(teil, "DIAGRAMM OPTIONEN")


def _text_teil(teil: str) -> bool:
    return teil in TEXT_TEILE or teil.startswith("legendeneintrag_")


def _combo(eintraege) -> QComboBox:
    c = QComboBox(); c.setMinimumHeight(36)
    for k, n in eintraege:
        c.addItem(n, k)
    return c


def _still(x, wert, setter: str = "setValue") -> None:
    x.blockSignals(True); getattr(x, setter)(wert); x.blockSignals(False)


class _FuellKopf(FarbFeld):
    """Der Farbknopf im Kopf von „Füllung“: Keine Füllung · Designfarben · Graduelle Füllung · Musterfüllung (6 Kacheln) · Strukturfüllung (5 Kacheln),
    ohne Standardfarben (so die Vorlage). Dieselben Kacheln wie ``objekt_menues.FuellMenue``."""
    musterGewaehlt = Signal(str)
    texturGewaehlt = Signal(str)

    def _waehle(self) -> None:
        pal = FarbPalette(self, keine_text="Keine Füllung", start=self.farbe or None, titel=self.titel, verlauf=True, weitere=False, zuletzt=False, standard=False)
        pal.gewaehlt.connect(self._uebernehmen)
        pal.verlauf_gewaehlt.connect(lambda c: self.verlaufGewaehlt.emit(c.name()))
        muster = [(k, QIcon(M.kachel(k, Farbe.TINTE, Farbe.WEISS).scaled(28, 28))) for k, _n, _o in M.MUSTER if k != "loeschen"][:6]
        textur = [(k, QIcon(_textur(k, 28))) for k, _n in TEXTUREN][:5]
        for titel, kacheln, sig in (("Musterfüllung", muster, self.musterGewaehlt), ("Strukturfüllung", textur, self.texturGewaehlt)):
            pal._spalte.addWidget(pal._titel_zeile(titel))
            g = QGridLayout(); g.setSpacing(2); g.setContentsMargins(0, 0, 0, 0)
            for i, (k, ic) in enumerate(kacheln):
                b = QToolButton(); b.setIcon(ic); b.setIconSize(QSize(28, 28)); b.setAutoRaise(True); b.setToolTip(k)
                b.clicked.connect(lambda _=False, k=k, sig=sig: (pal.close(), sig.emit(k)))
                g.addWidget(b, 0, i)
            g.setAlignment(Qt.AlignLeft)
            pal._spalte.addLayout(g)
        self._zeige_popup(pal)


class _AutoWert(QWidget):
    """Eine Zahl, die „Automatisch“ sein kann (Minimum, Maximum, Hauptintervall der Achse): Haken + Feld. ``wert()`` ist None bei Automatisch."""
    geaendert = Signal()

    def __init__(self, vorgabe: float = 0.0):
        super().__init__()
        h = QHBoxLayout(self); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(6)
        self.auto = QCheckBox("Auto"); self.auto.setChecked(True)
        self.feld = QDoubleSpinBox(); self.feld.setRange(-1e9, 1e9); self.feld.setDecimals(2); self.feld.setValue(vorgabe); self.feld.setEnabled(False)
        self.feld.setMinimumHeight(36); self.feld.setMinimumWidth(70)
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
class DiagrammTextPanel(_TextPanel):
    """Textfüllung und -kontur, Effekte (wie bei den Texteffekten) und „Textfeld“. ``werte()`` ist das Textformat des Teils (``diagramm_format``: ``text``)."""

    def __init__(self, parent=None, werte: dict | None = None):
        super().__init__(parent, werte)
        self._stumm = True
        # Schrift vor der Textfüllung
        self.a_schrift = Abschnitt("Schrift")
        self.s_name = QFontComboBox(); self.s_name.setMinimumHeight(36)
        self.s_groesse = SchrittFeld(6, 96, " pt", 1, 0, 10)
        self.s_fett, self.s_kursiv, self.s_unter = UmbruchSchalter("Fett"), UmbruchSchalter("Kursiv"), UmbruchSchalter("Unterstrichen")
        self.s_gesetzt = {"name": False, "groesse": False}
        self.a_schrift.zeile("Schriftart:", self.s_name); self.a_schrift.zeile("Größe:", self.s_groesse)
        for x in (self.s_fett, self.s_kursiv, self.s_unter):
            self.a_schrift.breit(x)
        self.reiter.widget(0).widget().layout().insertWidget(0, self.a_schrift)
        # Textfeld
        self.a_feld = Abschnitt("Textfeld")
        self.f_vertikal, self.f_richtung = _combo(VERTIKAL), _combo(RICHTUNGEN)
        self.f_winkel = SchrittFeld(-180, 180, "°", 5, 0, 0)
        self.f_rand = {k: SchrittFeld(0, 60, " pt", 1, 0, 0) for k in "lrou"}
        self.f_anpassen = UmbruchSchalter("Größe der Form dem Text anpassen"); self.f_anpassen.setChecked(True)
        self.f_umbruch = UmbruchSchalter("Text in Form umbrechen"); self.f_umbruch.setChecked(True)
        for t, f in (("Vertikale Ausrichtung:", self.f_vertikal), ("Textrichtung:", self.f_richtung), ("Benutzerdefinierter Winkel:", self.f_winkel),
                     ("Linker Rand:", self.f_rand["l"]), ("Rechter Rand:", self.f_rand["r"]), ("Oberer Rand:", self.f_rand["o"]), ("Unterer Rand:", self.f_rand["u"])):
            self.a_feld.zeile(t, f)
        self.a_feld.breit(self.f_anpassen); self.a_feld.breit(self.f_umbruch)
        feldseite = QWidget(); v = QVBoxLayout(feldseite); v.setSpacing(10); v.addWidget(self.a_feld); v.addStretch(1)
        self.reiter.addTab(self._scroll(feldseite), icons.icon("square-text", 22), "TEXTFELD")
        for a in (self.a_schrift, self.a_feld, self.a_fuell, self.a_kontur):
            a.knopf.setChecked(True)
        self.s_name.currentFontChanged.connect(lambda *_: (self.s_gesetzt.update(name=True), self._neu()))
        self.s_groesse.valueChanged.connect(lambda *_: (self.s_gesetzt.update(groesse=True), self._neu()))
        for x in (self.s_fett, self.s_kursiv, self.s_unter, self.f_anpassen, self.f_umbruch):
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
        if not hasattr(self, "f_rand"):
            return
        f = F.feld_von(t)
        _still(self.s_name, QFont(t.get("name") or self.font().family()), "setCurrentFont")
        self.s_gesetzt = {"name": bool(t.get("name")), "groesse": bool(t.get("groesse"))}
        _still(self.s_groesse, float(t.get("groesse") or 10)); _still(self.f_winkel, float(f["winkel"]))
        for x, wert in ((self.s_fett, bool(t.get("fett"))), (self.s_kursiv, bool(t.get("kursiv"))), (self.s_unter, bool(t.get("unter"))),
                        (self.f_anpassen, f["anpassen"] is not False), (self.f_umbruch, f["umbruch"] is not False)):
            _still(x, wert, "setChecked")
        for x, d in ((self.f_vertikal, f["vertikal"]), (self.f_richtung, f["richtung"])):
            _still(x, max(0, x.findData(d)), "setCurrentIndex")
        for k, x in self.f_rand.items():
            _still(x, float(f["raender"][k]))

    def werte(self) -> dict:
        w = super().werte()
        eff = {k: v for k, v in w.items() if v is not None}
        standard = eff.get("fuell") == "farbe" and not eff.get("transparenz") and not eff.get("kontur") and not any(
            eff.get(k) for k in ("verlauf", "kontur_verlauf", "schatten", "reflektion", "leuchten", "d3")) and eff.get("kontur_form", "einfach") == "einfach"
        t = {"farbe": eff.get("farbe") or None, "effekt": None if standard else eff,
             "groesse": self.s_groesse.value() if self.s_gesetzt["groesse"] else None,
             "name": self.s_name.currentFont().family() if self.s_gesetzt["name"] else None,
             "fett": True if self.s_fett.isChecked() else None, "kursiv": True if self.s_kursiv.isChecked() else None,
             "unter": True if self.s_unter.isChecked() else None}
        t["feld"] = {"vertikal": self.f_vertikal.currentData(), "richtung": self.f_richtung.currentData(), "winkel": self.f_winkel.value(),
                     "anpassen": self.f_anpassen.isChecked(), "umbruch": self.f_umbruch.isChecked(),
                     "raender": {k: x.value() for k, x in self.f_rand.items()}}
        return t


# ---- das Panel ------------------------------------------------------------------------------------------------------------------------
class DiagrammFormatPanel(ObjektFormatPanel):
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
        self.hauptreiter = [self.umschalter.button(0), self.umschalter.button(1)]
        self.teil_pfeil = QToolButton(); self.teil_pfeil.setArrowType(Qt.DownArrow); self.teil_pfeil.setAutoRaise(True)
        self.teil_pfeil.setToolTip("Diagrammteil wählen"); self.teil_pfeil.setPopupMode(QToolButton.InstantPopup)
        self.teil_menue = QMenu(self.teil_pfeil); self.teil_pfeil.setMenu(self.teil_menue)
        self.kopf_zeile.insertWidget(1, self.teil_pfeil)
        self.fuell_farbe_kopf.musterGewaehlt.connect(lambda k: (self.fuellung_waehlen("muster"), self.muster.setCurrentIndex(max(0, self.muster.findData(k))), self._neu()))
        self.fuell_farbe_kopf.texturGewaehlt.connect(lambda k: (self.fuellung_waehlen("textur"), self.textur.setCurrentIndex(max(0, self.textur.findData(k))), self._neu()))
        self.text_panel.geaendert.connect(lambda t: self._melde(text=t))
        self.optionen_seite = self._seite_optionen()
        self.reiter.addTab(self._scroll(self.optionen_seite), icons.icon("sliders-horizontal", 22), "OPTIONEN")
        self.eigenschaften_seite = self._seite_eigenschaften()
        self.reiter.addTab(self._scroll(self.eigenschaften_seite), icons.icon("scaling", 22), "GRÖSSE UND\nEIGENSCHAFTEN")
        for i, name in enumerate(("FÜLLUNG\nUND LINIE", "EFFEKTE")):
            self.reiter.tabKnopf(i).setText(name)
        self.text_panel.reiter.tabKnopf(0).setText("TEXTFÜLLUNG\nUND -KONTUR")
        for k in self.reiter._gruppe.buttons() + self.text_panel.reiter._gruppe.buttons():        # vier Reiter müssen in 300 Bildpunkte passen
            k.setStyleSheet("QToolButton { border: none; border-bottom: 2px solid transparent; padding: 4px 6px; color: palette(window-text); }"
                            "QToolButton:checked { color: palette(highlight); border-bottom: 2px solid palette(highlight); }")
        for a in (self.a_fuell, self.a_kontur, self.a_schatten):         # wie in der Vorlage: die wichtigsten Abschnitte stehen offen
            a.knopf.setChecked(True)
        self._alt_timer = QTimer(self); self._alt_timer.setSingleShot(True); self._alt_timer.setInterval(400)
        self._alt_timer.timeout.connect(lambda: self.alt_geaendert.emit(self.alt_titel.text(), self.alt_text.toPlainText()))
        self._fertig = True
        self._stumm = False
        self.setze(werte or {})

    def _kopf_klasse(self):
        return _FuellKopf

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
            a.zeile("Transparenz:", self.f_trans); a.zeile("Winkel des Verlaufs:", self.v_winkel)
            self.f_trans.valueChanged.connect(lambda *_: (self._farbe_waehlen(), self._neu()))
            self.v_winkel.valueChanged.connect(lambda *_: (self.r_verlauf.setChecked(True), self._neu()))
            return
        self.kv1, self.kv2 = FarbFeld("#c92a2a", "Farbe 1"), FarbFeld("#1864ab", "Farbe 2")
        self.kv_winkel = SchiebeFeld(0, 360, "°", 5)
        self.k_trans = SchiebeFeld(0, 100, " %")
        self.l_kombi = _combo(T.KONTUR_FORMEN)
        self.l_abschluss, self.l_verknuepfung = _combo(ABSCHLUSS), _combo(VERKNUEPFUNG)
        self.l_rund = UmbruchSchalter("Abgerundete Ecke")
        a.zeile("Farbe 1:", self.kv1); a.zeile("Farbe 2:", self.kv2); a.zeile("Winkel:", self.kv_winkel)
        a.zeile("Transparenz:", self.k_trans); a.zeile("Kombinierter Typ:", self.l_kombi); a.zeile("Abschlusstyp:", self.l_abschluss)
        a.zeile("Verknüpfungstyp:", self.l_verknuepfung); a.breit(self.l_rund)
        for sig in (self.kv1.farbeGeaendert, self.kv2.farbeGeaendert, self.kv_winkel.valueChanged):
            sig.connect(lambda *_: (self.k_verlauf.setChecked(True), self._neu()))
        for sig in (self.k_trans.valueChanged, self.l_kombi.currentIndexChanged, self.l_abschluss.currentIndexChanged, self.l_verknuepfung.currentIndexChanged,
                    self.l_rund.toggled):
            sig.connect(lambda *_: (self._linie_waehlen(), self._neu()))
        # Pfeile (nur Linienreihen): eigener Abschnitt unter der Linie
        self.a_pfeile = Abschnitt("Pfeile")
        self.p_anfang, self.p_ende = _combo(F.PFEILE), _combo(F.PFEILE)
        self.p_groesse = SchiebeFeld(1, 3, "", 0.5, 1, 1.0)
        self.a_pfeile.zeile("Anfang:", self.p_anfang); self.a_pfeile.zeile("Ende:", self.p_ende); self.a_pfeile.zeile("Größe:", self.p_groesse)
        for sig in (self.p_anfang.currentIndexChanged, self.p_ende.currentIndexChanged, self.p_groesse.valueChanged):
            sig.connect(lambda *_: (self._linie_waehlen(), self._neu()))

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

    def _linie_waehlen(self) -> None:
        if self.k_auto.isChecked() or self.k_keine.isChecked():
            self.k_linie.setChecked(True)

    def _seite_fuellung(self, w: dict) -> QWidget:
        seite = super()._seite_fuellung(w)
        self.r_textur.setText("Bild- oder Texturfüllung"); self.r_bild.setVisible(False)       # ein Feld mit Unterwahl (Struktur oder Bild)
        self._bild_modus = False
        self.bild_knopf.clicked.connect(self._bild_waehlen)
        v = seite.layout()
        v.insertWidget(v.count() - 1, self.a_pfeile)
        for sig in (self.k_farbe.farbeGeaendert, self.k_breite.valueChanged, self.k_art.currentIndexChanged):
            sig.connect(lambda *_: self._linie_waehlen())
        return seite

    # ---- Seite „Optionen“ (Legende, Achse, Reihe) ---------------------------------------------------------------------------------
    def _seite_optionen(self) -> QWidget:
        seite = QWidget(); v = QVBoxLayout(seite); v.setSpacing(10); v.setContentsMargins(0, 0, 0, 0)
        self.a_legende = Abschnitt("Legendenoptionen")
        self.o_lage = _combo(LEGENDEN_LAGEN)
        self.a_legende.zeile("Legendenposition:", self.o_lage)
        self.o_lage.currentIndexChanged.connect(lambda *_: self._melde(objekt={"legende_pos": self.o_lage.currentData()}))
        self.a_achse = Abschnitt("Achsenoptionen")
        self.o_min, self.o_max, self.o_intervall = _AutoWert(0.0), _AutoWert(10.0), _AutoWert(1.0)
        self.o_umkehren = UmbruchSchalter("Werte in umgekehrter Reihenfolge")
        self.o_beschr = _combo((("neben", "Neben der Achse"), ("keine", "Keine")))
        self.a_achse.zeile("Minimum:", self.o_min); self.a_achse.zeile("Maximum:", self.o_max); self.a_achse.zeile("Hauptintervall:", self.o_intervall)
        self._wert_zeilen = (self.o_min, self.o_max, self.o_intervall)
        self.a_achse.breit(self.o_umkehren); self.a_achse.zeile("Beschriftungsposition:", self.o_beschr)
        for sig in (self.o_min.geaendert, self.o_max.geaendert, self.o_intervall.geaendert, self.o_umkehren.toggled, self.o_beschr.currentIndexChanged):
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
                           "umkehren": True if self.o_umkehren.isChecked() else None,
                           "beschriftung": self.o_beschr.currentData() if self.o_beschr.currentData() != "neben" else None})

    def _reihe_melden(self) -> None:
        self._melde(reihe={"luecke": self.o_luecke.value() if self._luecke_an else None, "glatt": True if self.o_glatt.isChecked() else None,
                           "punkte": True if self.o_punkte.isChecked() else None})

    # ---- Seite „Größe und Eigenschaften“ ------------------------------------------------------------------------------------------
    def _seite_eigenschaften(self) -> QWidget:
        seite = QWidget(); v = QVBoxLayout(seite); v.setSpacing(10); v.setContentsMargins(0, 0, 0, 0)
        self.a_groesse = Abschnitt("Größe")
        self.g_hoehe = EinheitFeld(80.0, 10.0, 1000.0, ("mm", "cm", "in", "pt")); self.g_breite = EinheitFeld(120.0, 10.0, 1000.0, ("mm", "cm", "in", "pt"))
        self.g_sperren = UmbruchSchalter("Seitenverhältnis sperren")
        self.g_dreh = SchrittFeld(-360, 360, "°", 5, 0, 0)
        self.a_groesse.zeile("Höhe:", self.g_hoehe); self.a_groesse.zeile("Breite:", self.g_breite); self.a_groesse.breit(self.g_sperren)
        self.a_groesse.zeile("Drehung:", self.g_dreh)
        self._verhaeltnis = 1.5
        self.g_hoehe.valueChanged.connect(lambda *_: self._groesse_melden(True)); self.g_breite.valueChanged.connect(lambda *_: self._groesse_melden(False))
        self.g_dreh.valueChanged.connect(lambda *_: self._melde(dreh=self.g_dreh.value()))
        self.a_alt = Abschnitt("Alternativtext")
        self.alt_titel = QLineEdit(); self.alt_titel.setMinimumHeight(36)
        self.alt_text = QPlainTextEdit(); self.alt_text.setMinimumHeight(110)
        self.a_alt.zeile("Titel:", self.alt_titel); self.a_alt.zeile("Beschreibung:", self.alt_text)
        self.alt_titel.textChanged.connect(lambda *_: self._alt_start()); self.alt_text.textChanged.connect(self._alt_start)
        v.addWidget(self.a_groesse); v.addWidget(self.a_alt); v.addStretch(1)
        for a in (self.a_groesse, self.a_alt):
            a.knopf.setChecked(True)
        return seite

    def _groesse_melden(self, hoehe: bool) -> None:
        if self._stumm or not self._fertig:
            return
        if self.g_sperren.isChecked():
            ziel, wert = (self.g_breite, self.g_hoehe.value() * self._verhaeltnis) if hoehe else (self.g_hoehe, self.g_breite.value() / max(0.01, self._verhaeltnis))
            ziel.blockSignals(True); ziel.setValue(wert); ziel.blockSignals(False)
        self._verhaeltnis = self.g_breite.value() / max(0.01, self.g_hoehe.value())
        self._melde(groesse={"breite_mm": self.g_breite.value(), "hoehe_mm": self.g_hoehe.value()})

    def _alt_start(self) -> None:
        if not self._stumm and self._fertig:
            self._alt_timer.start()

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
            d = {"art": "graduell", "dunkel": self.v1.farbe or "#1864ab", "hell": self.v2.farbe or "#ffffff", "winkel": self.v_winkel.value()}
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
                "rund": None, "verlauf": None, "pfeil_anfang": None, "pfeil_ende": None, "pfeil_groesse": None}
        if self.k_keine.isChecked():
            return {**voll, "keine": True}
        voll.update(farbe=self.k_farbe.farbe or Farbe.GRAU, breite=self.k_breite.value(), art=self.k_art.currentData() or "einfach",
                    transparenz=int(self.k_trans.value()) or None, kombiniert=self.l_kombi.currentData() if self.l_kombi.currentData() != "einfach" else None,
                    abschluss=self.l_abschluss.currentData() if self.l_abschluss.currentData() != "flach" else None,
                    verknuepfung=self.l_verknuepfung.currentData() if self.l_verknuepfung.currentData() != "rund" else None,
                    rund=True if self.l_rund.isChecked() else None)
        if self.k_verlauf.isChecked():
            voll["verlauf"] = {"farbe1": self.kv1.farbe or "#c92a2a", "farbe2": self.kv2.farbe or "#1864ab", "winkel": self.kv_winkel.value()}
        if not self.a_pfeile.isHidden():
            voll.update(pfeil_anfang=self.p_anfang.currentData() if self.p_anfang.currentData() != "keiner" else None,
                        pfeil_ende=self.p_ende.currentData() if self.p_ende.currentData() != "keiner" else None,
                        pfeil_groesse=self.p_groesse.value() if self.p_groesse.value() != 1.0 else None)
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
        if art == "farbe":
            self.farbe.setFarbe(d.get("farbe", Farbe.BLAU))
        elif art in ("graduell", "verlauf"):
            self.v1.setFarbe(d.get("dunkel", d.get("farbe", "#1864ab"))); self.v2.setFarbe(d.get("hell", "#d0ebff"))
        elif art == "textur":
            self.textur.setCurrentIndex(max(0, self.textur.findData(d.get("key"))))
        elif art == "muster":
            self.muster.setCurrentIndex(max(0, self.muster.findData(d.get("key")))); self.m_farbe.setFarbe(d.get("farbe", Farbe.TINTE))
        self.f_trans.setValue(float(d.get("transparenz", 0))); self.v_winkel.setValue(float(d.get("winkel", 90)))
        self.fuell_farbe_kopf.setFarbe(d.get("farbe", "") if art == "farbe" else "")
        li = li or {}
        self.k_farbe.setFarbe(li.get("farbe", Farbe.GRAU)); self.k_breite.setValue(float(li.get("breite", 1.0)))
        self.k_art.setCurrentIndex(max(0, self.k_art.findData(li.get("art", "einfach"))))
        self.k_trans.setValue(float(li.get("transparenz", 0)))
        for c, k, vorgabe in ((self.l_kombi, "kombiniert", "einfach"), (self.l_abschluss, "abschluss", "flach"), (self.l_verknuepfung, "verknuepfung", "rund"),
                              (self.p_anfang, "pfeil_anfang", "keiner"), (self.p_ende, "pfeil_ende", "keiner")):
            _still(c, max(0, c.findData(li.get(k, vorgabe))), "setCurrentIndex")
        _still(self.l_rund, bool(li.get("rund")), "setChecked")
        self.p_groesse.setValue(float(li.get("pfeil_groesse", 1.0)))
        v = li.get("verlauf") or {}
        self.kv1.setFarbe(v.get("farbe1", "#c92a2a")); self.kv2.setFarbe(v.get("farbe2", "#1864ab")); self.kv_winkel.setValue(float(v.get("winkel", 0)))

    def _neu(self, *_) -> None:
        super()._neu()
        if hasattr(self, "k_auto"):
            self.linie_knopf.setText("Keine" if self.k_keine.isChecked() else "Automatisch" if self.k_auto.isChecked() else self.linie_knopf.text())

    def setze(self, werte: dict) -> None:
        """Die Felder mit dem Format des Teils füllen; meldet nichts."""
        if not self._fertig:
            super().setze(werte)
            return
        alt, self._stumm = self._stumm, True
        try:
            self._teil = werte.get("teil") or "diagrammbereich"
            self._teil_einrichten(werte)
            super().setze(werte)
            f = werte.get("format") or {}
            self.text_panel.setze({"text": f.get("text") or {}})
            self._setze_optionen(werte, f)
        finally:
            self._stumm = alt

    def _teil_einrichten(self, werte: dict) -> None:
        teil = self._teil
        self.hauptreiter[0].setText(_optionen_name(teil))
        text_ok = _text_teil(teil)
        self.hauptreiter[1].setEnabled(text_ok)
        self.hauptreiter[0].setEnabled(teil != "datenbeschriftung")
        if (not text_ok and self.optionen.currentIndex() == 1) or (teil == "datenbeschriftung" and self.optionen.currentIndex() == 0):
            self.optionen_waehlen(1 if teil == "datenbeschriftung" else 0)
        legende, achse, reihe, bereich = teil == "legende", teil.startswith("achse_"), teil.startswith("reihe_"), teil == "diagrammbereich"
        self.reiter.setTabVisible(2, legende or achse or reihe)
        self.reiter.tabKnopf(2).setText("LEGENDEN-\nOPTIONEN" if legende else "ACHSEN-\nOPTIONEN" if achse else "REIHEN-\nOPTIONEN")
        self.reiter.setTabVisible(3, bereich)
        self._luecke_an = reihe and bool(werte.get("saeulen"))
        for a, an in ((self.a_legende, legende), (self.a_achse, achse), (self.a_reihe, self._luecke_an),
                      (self.a_reihe_linie, reihe and bool(werte.get("linienreihe"))), (self.a_pfeile, reihe and bool(werte.get("linienreihe")))):
            a.setVisible(an)
        for x in self._wert_zeilen:                                         # Minimum, Maximum, Hauptintervall: nur die Wertachse
            x.setEnabled(bool(werte.get("wertachse", True)))

    def _setze_optionen(self, werte: dict, f: dict) -> None:
        o = werte.get("objekt") or {}
        _still(self.o_lage, max(0, self.o_lage.findData(o.get("legende_pos", "unten"))), "setCurrentIndex")
        a = f.get("achse") or {}
        self.o_min.setze(a.get("min")); self.o_max.setze(a.get("max")); self.o_intervall.setze(a.get("intervall"))
        _still(self.o_umkehren, bool(a.get("umkehren")), "setChecked")
        _still(self.o_beschr, max(0, self.o_beschr.findData(a.get("beschriftung", "neben"))), "setCurrentIndex")
        r = f.get("reihe") or {}
        _still(self.o_luecke, float(r.get("luecke", 100))); _still(self.o_glatt, bool(r.get("glatt")), "setChecked"); _still(self.o_punkte, bool(r.get("punkte")), "setChecked")
        if o.get("breite_mm"):
            for x, wert in ((self.g_breite, float(o["breite_mm"])), (self.g_hoehe, float(o["hoehe_mm"]))):
                _still(x, wert)
            self._verhaeltnis = float(o["breite_mm"]) / max(0.01, float(o["hoehe_mm"]))
        _still(self.g_dreh, float(o.get("dreh", 0.0)))
        if not self.alt_titel.hasFocus():
            self.alt_titel.setText(werte.get("alt_titel") or "")
        if not self.alt_text.hasFocus():
            self.alt_text.setPlainText(werte.get("alt_beschreibung") or "")
