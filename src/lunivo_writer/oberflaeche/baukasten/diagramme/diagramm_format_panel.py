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

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QTabBar, QLineEdit, QRadioButton, QVBoxLayout, QWidget
from lunivo_writer.kern.farben import Farbe
from lunivo_writer.editor.diagramme import diagramm_format as F
from lunivo_writer.editor.text import texteffekt as T
from lunivo_writer.oberflaeche.baukasten.medien.alternativtext_abschnitt import AlternativtextAbschnitt
from lunivo_writer.oberflaeche.baukasten.formatierung.auto_felder_mixin import AutoFelderMixin
from lunivo_writer.oberflaeche.baukasten.formatierung.effekte_drei_mixin import NurDreiEffekteMixin
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.farbpalette import FarbFeld
from lunivo_writer.oberflaeche.baukasten.dropdown.kopf_menue_mixin import KopfMenueMixin
from lunivo_writer.oberflaeche.baukasten.dropdown.teil_menue import TeilMenueKnopf
from lunivo_writer.oberflaeche.baukasten.basis.linien import Linie
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import UmbruchSchalter
from lunivo_writer.oberflaeche.baukasten.formatierung.objektformat_panel import ObjektFormatPanel
from lunivo_writer.oberflaeche.baukasten.felder.schiebe_feld import SchiebeFeld, SchrittFeld
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahl.strich_auswahl import StrichAuswahl
from lunivo_writer.oberflaeche.baukasten.formatierung.texteffekt_dialog import Abschnitt
from lunivo_writer.oberflaeche.bauteile import symbole
from lunivo_writer.oberflaeche.baukasten.basis.mass import ABSTAND_SPALTE, ICON_MITTEL, RAND_FORMATSEITE
from lunivo_writer.oberflaeche.baukasten.diagramme.diagramm_format_bausteine import LEGENDEN_LAGEN, ABSCHLUSS, VERKNUEPFUNG, _combo, _strich_zeichner, _kombi_zeichner, _still, _AutoWert
from lunivo_writer.oberflaeche.baukasten.diagramme.diagramm_format_werte import DiagrammFormatWerteMixin
from lunivo_writer.oberflaeche.baukasten.diagramme.diagramm_text_panel import DiagrammTextPanel


# ---- das Panel ------------------------------------------------------------------------------------------------------------------------
class DiagrammFormatPanel(DiagrammFormatWerteMixin, KopfMenueMixin, NurDreiEffekteMixin, AutoFelderMixin, ObjektFormatPanel):
    TEXT_KLASSE = DiagrammTextPanel
    _bild_modus = False
    alt_geaendert = Signal(str, str)
    dekorativ_geaendert = Signal(bool)                                  # „Als dekorativ markieren“ des Diagramms
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
        self.reiter.addTab(self._scroll(self.optionen_seite), symbole.icon("sliders-horizontal", ICON_MITTEL), "Optionen")
        self.eigenschaften_seite = self._seite_eigenschaften()
        self.reiter.addTab(self._scroll(self.eigenschaften_seite), symbole.icon("scaling", ICON_MITTEL), "Größe und Eigenschaften")
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
        self.a_alt = AlternativtextAbschnitt(mit_dekorativ=True)
        self.a_alt.dekorativ_geaendert.connect(lambda an: None if self._stumm or not self._fertig else self.dekorativ_geaendert.emit(an))
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
