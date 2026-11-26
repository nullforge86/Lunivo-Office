"""Textformat-Bausteine: Schriftname, Größe, Fett, Kursiv, Ausrichtung, Zeilenabstand — so wie im Band (Start ▸ Schriftart, Absatz).

Das Band und jedes Fenster, das Text formatiert (Neue Formatvorlage, später Zeichen- und Absatzfenster), bauen ihre Felder hier;
niemand baut sie nach. Die Bausteine kennen den Editor nicht: ``TextFormatLeiste`` meldet Werte, der Aufrufer tut damit, was er will.
"""
from __future__ import annotations

from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import werkzeugknopf

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPainter
from PySide6.QtWidgets import QButtonGroup, QComboBox, QFontComboBox, QFrame, QToolButton, QWidget

from vcl.qt.widgets.bausteine.schrift.texte import trennlinie
from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_KLEIN, BREITE_KNOPF_KLEIN, ICON_GROSS, ICON_TEXTFORMATLEISTE, RAND_KEIN
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.menues.dropdown.schriftauswahl import Schriftauswahl

GROESSEN = (8, 9, 10, 10.5, 11, 12, 14, 16, 18, 20, 24, 28, 36, 48, 72)
AUSRICHTUNG = (("links", "Linksbündig"), ("mitte", "Zentriert"), ("rechts", "Rechtsbündig"), ("block", "Blocksatz"))
ZEILENABSTAND = ((1.0, "Einfach"), (1.5, "1,5 Zeilen"), (2.0, "Doppelt"))


def schrift_feld(combo: QComboBox | None = None, variante: str = "band") -> QComboBox:
    """Das Feld für den Schriftnamen (im Band mit Live-Vorschau, im Fenster ohne)."""
    c = combo if combo is not None else Schriftauswahl()
    c.rolle("schrift", variante)
    return c


def groesse_feld(combo: QComboBox | None = None, variante: str = "band") -> QComboBox:
    """Das Feld für die Schriftgröße: zum Tippen und mit der Liste der üblichen Größen."""
    c = combo if combo is not None else Auswahlfeld()
    c.setEditable(True)
    c.rolle("groesse", variante)
    c.addItems([f"{g:g}" for g in GROESSEN])
    return c


def text_knopf(symbol: str, tipp: str) -> QToolButton:
    """F, K oder U als Knopf zum Ein-/Ausschalten, in dem Schnitt, den er bedeutet (wie im Band)."""
    k = werkzeugknopf("standard", umschaltbar=True); k.setText(symbol); k.setToolTip(tipp); k.setMinimumWidth(BREITE_KNOPF_KLEIN)
    f = k.font()
    f.setBold(symbol == "F"); f.setItalic(symbol == "K"); f.setUnderline(symbol == "U")
    k.setFont(f)
    return k


def ausrichtung_knoepfe() -> dict[str, QToolButton]:
    """Linksbündig, Zentriert, Rechtsbündig, Blocksatz — gleiche Symbole und Namen wie im Band; immer höchstens einer gewählt."""
    gruppe = {}
    for schl, name in AUSRICHTUNG:
        k = werkzeugknopf("standard", umschaltbar=True); k.setToolTip(name)
        k.setIcon(symbole.icon(schl, ICON_GROSS)); k.setIconSize(QSize(ICON_GROSS, ICON_GROSS))
        gruppe[schl] = k
    return gruppe


def _zeilen_symbol(abstand: float) -> QIcon:
    return symbole.icon({1.0: "list-start", 1.5: "list", 2.0: "list-chevrons-up-down"}.get(abstand, "list"), ICON_TEXTFORMATLEISTE)


def _abstand_symbol(mehr: bool) -> QIcon:
    return symbole.icon("list-plus" if mehr else "list-minus", ICON_TEXTFORMATLEISTE)


def _einzug_symbol(mehr: bool) -> QIcon:
    return symbole.icon("list-indent-increase" if mehr else "list-indent-decrease", ICON_TEXTFORMATLEISTE)


class TextFormatLeiste(QWidget):
    """Zwei Zeilen wie im Band: Schrift, Größe, Fett, Kursiv · Ausrichtung (und mit ``absatz=True`` Zeilenabstand, Absatzabstand und
    Einzug). Meldet jede Änderung mit ``geaendert``; ``werte()`` und ``setze()`` lesen und schreiben alles auf einmal."""

    geaendert = Signal()
    SCHRITT_ABSTAND = 6.0        # pt je Klick auf „Absatzabstand“
    SCHRITT_EINZUG = 10.0        # mm je Klick auf „Einzug“

    def __init__(self, parent=None, *, absatz: bool = True):
        super().__init__(parent)
        from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte
        self.vor = self.nach = self.einzug = 0.0
        self.zeilen = 0.0
        v = spalte("eng", self)
        from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
        z1 = FlussLayout(4); v.addLayout(z1)
        self.schrift = schrift_feld(); self.groesse = groesse_feld()
        self.groesse.setCurrentIndex(-1)
        self.fett, self.kursiv = text_knopf("F", "Fett"), text_knopf("K", "Kursiv")
        for w in (self.schrift, self.groesse):
            z1.addWidget(w)
        z1.addWidget(self.fett); z1.addWidget(self.kursiv)
        z2 = FlussLayout(4); v.addLayout(z2)
        self.ausr = ausrichtung_knoepfe()
        self._gruppe = QButtonGroup(self); self._gruppe.setExclusive(False)
        for schl, k in self.ausr.items():
            z2.addWidget(k)
            k.clicked.connect(lambda an, s=schl: self._ausrichtung(s, an))
        self.zeilen_knoepfe: dict[float, QToolButton] = {}
        self.knoepfe_absatz: list[QToolButton] = []
        if absatz:
            for f, name in ZEILENABSTAND:
                k = werkzeugknopf("standard", umschaltbar=True); k.setToolTip(name); k.setIcon(_zeilen_symbol(f)); k.setIconSize(QSize(ICON_TEXTFORMATLEISTE, ICON_TEXTFORMATLEISTE))
                k.clicked.connect(lambda an, f=f: self._zeilenabstand(f, an))
                self.zeilen_knoepfe[f] = k; z2.addWidget(k)
            for name, mehr, fn in (("Absatzabstand vergrößern", True, lambda: self._abstand(+self.SCHRITT_ABSTAND)),
                                   ("Absatzabstand verkleinern", False, lambda: self._abstand(-self.SCHRITT_ABSTAND))):
                k = self._aktion(name, _abstand_symbol(mehr), fn); z2.addWidget(k)
            for name, mehr, fn in (("Einzug verkleinern", False, lambda: self._einzug(-self.SCHRITT_EINZUG)),
                                   ("Einzug vergrößern", True, lambda: self._einzug(+self.SCHRITT_EINZUG))):
                k = self._aktion(name, _einzug_symbol(mehr), fn); z2.addWidget(k)
        for w in self.findChildren(QToolButton) + [self.schrift, self.groesse]:       # Bedienelemente mindestens 36 px (Eigentümer-Vorgabe Seitenleiste)
            if isinstance(w, QToolButton):
                w.setMinimumWidth(BREITE_KNOPF_KLEIN)
        self.schrift.currentFontChanged.connect(lambda _f: self.geaendert.emit())
        self.groesse.editTextChanged.connect(lambda _t: self.geaendert.emit())
        self.fett.toggled.connect(lambda _a: self.geaendert.emit()); self.kursiv.toggled.connect(lambda _a: self.geaendert.emit())

    @staticmethod
    def _trenner() -> QFrame:
        t = trennlinie(senkrecht=True, tief=True)
        return t

    @staticmethod
    def _aktion(name: str, symbol: QIcon, fn) -> QToolButton:
        k = werkzeugknopf("standard"); k.setToolTip(name); k.setIcon(symbol); k.setIconSize(QSize(ICON_TEXTFORMATLEISTE, ICON_TEXTFORMATLEISTE))
        k.clicked.connect(lambda _c=False: fn())
        return k

    # ---- Bedienung
    def _ausrichtung(self, schl: str, an: bool) -> None:
        for s, k in self.ausr.items():
            k.setChecked(s == schl and an)
        self.geaendert.emit()

    def _zeilenabstand(self, f: float, an: bool) -> None:
        self.zeilen = f if an else 0.0
        self._zeige_zeilen()
        self.geaendert.emit()

    def _zeige_zeilen(self) -> None:
        for f, k in self.zeilen_knoepfe.items():
            k.setChecked(abs(f - self.zeilen) < 0.01)

    def _abstand(self, delta: float) -> None:
        self.vor, self.nach = max(0.0, self.vor + delta), max(0.0, self.nach + delta)
        self.geaendert.emit()

    def _einzug(self, delta: float) -> None:
        self.einzug = max(0.0, self.einzug + delta)
        self.geaendert.emit()

    # ---- Werte
    def werte(self) -> dict:
        try:
            gr = float(self.groesse.currentText().replace(",", "."))
        except ValueError:
            gr = 0.0
        return {"schrift": self.schrift.currentFont().family() if self._schrift_gesetzt else "", "groesse": gr,
                "fett": self.fett.isChecked(), "kursiv": self.kursiv.isChecked(),
                "ausr": next((s for s, k in self.ausr.items() if k.isChecked()), ""),
                "vor": self.vor, "nach": self.nach, "einzug": self.einzug, "zeilen": self.zeilen}

    _schrift_gesetzt = False

    def setze(self, d: dict) -> None:
        """Alle Felder auf die Werte einer Vorlage stellen (ohne ``geaendert`` zu melden)."""
        for w in (self.schrift, self.groesse, self.fett, self.kursiv):
            w.blockSignals(True)
        self._schrift_gesetzt = bool(d.get("schrift"))
        if d.get("schrift"):
            self.schrift.setCurrentFont(QFont(d["schrift"]))
        g = d.get("groesse") or 0
        self.groesse.setCurrentText(f"{g:g}" if g else "")
        self.fett.setChecked(bool(d.get("fett"))); self.kursiv.setChecked(bool(d.get("kursiv")))
        for s, k in self.ausr.items():
            k.setChecked(d.get("ausr") == s)
        self.vor, self.nach = float(d.get("vor") or 0), float(d.get("nach") or 0)
        self.einzug, self.zeilen = float(d.get("einzug") or 0), float(d.get("zeilen") or 0)
        self._zeige_zeilen()
        for w in (self.schrift, self.groesse, self.fett, self.kursiv):
            w.blockSignals(False)


# ---- Zeichenformat <-> Werte, gemeinsam für das Fenster „Schriftart“ und den Editor --------------------------------------------
UNTERSTREICHUNG = (("", "(Keine)"), ("woerter", "Nur Wörter"), ("einfach", "Einfach"), ("doppelt", "Doppelt"), ("dick", "Dick"),
                   ("gepunktet", "Gepunktet"), ("dick_gepunktet", "Dick gepunktet"), ("gestrichelt", "Gestrichelt"), ("dick_gestrichelt", "Dick gestrichelt"),
                   ("lang", "Lang gestrichelt"), ("dick_lang", "Dick lang gestrichelt"), ("strichpunkt", "Strich-Punkt"), ("dick_strichpunkt", "Dick Strich-Punkt"),
                   ("strichpunktpunkt", "Strich-Punkt-Punkt"), ("dick_strichpunktpunkt", "Dick Strich-Punkt-Punkt"), ("wellig", "Wellenlinie"),
                   ("dick_wellig", "Dicke Wellenlinie"), ("doppelwellig", "Doppelte Wellenlinie"))
ZEICHEN = {"schrift": "", "fett": False, "kursiv": False, "groesse": 0.0, "farbe": "", "unter": "", "unterfarbe": "",
           "durch": False, "hoch": False, "tief": False, "kapital": False, "gross": False, "versteckt": False,
           "abstand": 0.0, "kerning": True, "doppelt": False, "betonung": "", "skala": 100.0, "position": 0.0, "kern_ab": 0.0, "raster": True,
           "schrift_asien": "", "schnitt_asien": "", "groesse_asien": 0.0, "schrift_komplex": "", "schnitt_komplex": "", "groesse_komplex": 0.0}
BETONUNG = (("", "(Keine)"), ("punkt", "Punkt oberhalb"), ("kreis", "Kreis oberhalb"), ("komma", "Komma oberhalb"), ("unten", "Punkt unterhalb"))


def zu_zeichen(w: dict) -> dict:
    """Die Werte eines Zeichenfensters als Änderung des Zeichenformats im Dokumentenmodell (Wörterbuch; ``None`` nimmt ein Merkmal weg)."""
    d: dict = {"fett": True if w.get("fett") else None, "kursiv": True if w.get("kursiv") else None}
    familien = [x for x in (w.get("schrift"), w.get("schrift_asien"), w.get("schrift_komplex")) if x]
    if w.get("schrift"):
        d["schrift"] = w["schrift"]
    for art in ("asien", "komplex"):
        d[f"font_{art}"] = f'{w.get(f"schrift_{art}", "")}|{w.get(f"schnitt_{art}", "")}|{w.get(f"groesse_{art}", 0.0):g}' if w.get(f"schrift_{art}") else None
    d["betonung"] = w.get("betonung") or None
    if w.get("groesse"):
        d["groesse_pt"] = float(w["groesse"])
    if w.get("farbe"):
        d["farbe"] = w["farbe"]
    unter = w.get("unter") or ""
    d["unterstrichen"] = True if unter else None
    d["unter_art"] = unter if unter and unter != "einfach" else None
    d["unter_farbe"] = w.get("unterfarbe") or None if unter else None
    d["durchgestrichen"] = True if w.get("durch") else None
    d["doppelt_durch"] = True if w.get("doppelt") else None
    d["hoch_tief"] = "hoch" if w.get("hoch") else "tief" if w.get("tief") else None
    d["kapitaelchen"] = True if w.get("kapital") and not w.get("gross") else None
    d["grossbuchstaben"] = True if w.get("gross") else None
    d["zeichenabstand"] = float(w.get("abstand") or 0) or None
    kern_ab = float(w.get("kern_ab") or 0)                    # „Unterschneidung ab … Punkte“: erst ab dieser Größe
    an = bool(w.get("kerning", True)) and (kern_ab <= 0 or float(w.get("groesse") or 11) >= kern_ab)
    d["unterschneidung"] = None if an else False
    skala = float(w.get("skala") or 100)
    d["skalierung"] = skala if round(skala) != 100 else None
    d["versatz_pt"] = float(w.get("position") or 0) or None
    d["raster"] = None if w.get("raster", True) else False
    d["versteckt"] = True if w.get("versteckt") else None
    del familien
    return d


def aus_zeichen(z: dict, standard_schrift: str = "", standard_groesse: float = 0.0) -> dict:
    """Die Werte eines Zeichenformats des Dokumentenmodells (zum Vorbelegen eines Zeichenfensters)."""
    from writer.anbindung import formatwerte as F
    w = dict(ZEICHEN)
    fam = z.get("schrift")
    fam = fam[0] if isinstance(fam, (list, tuple)) and fam else fam
    w["schrift"] = (fam if isinstance(fam, str) else "") or standard_schrift
    w["fett"], w["kursiv"] = F.schrift(z).weight >= 600, bool(z.get("kursiv"))
    w["groesse"] = z.get("groesse_pt") or standard_groesse
    w["farbe"] = str(z.get("farbe") or "")[:7]
    w["unter"] = z.get("unter_art") or ("einfach" if z.get("unterstrichen") else "")
    w["unterfarbe"] = str(z.get("unter_farbe") or "") if w["unter"] else ""
    w["doppelt"] = bool(z.get("doppelt_durch"))
    w["durch"] = bool(z.get("durchgestrichen")) and not w["doppelt"]
    w["betonung"] = str(z.get("betonung") or "")
    for art in ("asien", "komplex"):
        roh = z.get(f"font_{art}")
        if roh:
            f_, sn, gr = (str(roh).split("|") + ["", "", ""])[:3]
            w[f"schrift_{art}"] = f_; w[f"schnitt_{art}"] = sn
            try:
                w[f"groesse_{art}"] = float(gr or 0)
            except ValueError:
                pass
    w["hoch"], w["tief"] = z.get("hoch_tief") == "hoch", z.get("hoch_tief") == "tief"
    w["kapital"], w["gross"] = bool(z.get("kapitaelchen")), bool(z.get("grossbuchstaben"))
    w["abstand"] = round(float(z.get("zeichenabstand") or 0), 1)
    w["kerning"] = z.get("unterschneidung") is not False                                     # ohne Angabe gilt: an
    w["skala"] = float(z.get("skalierung") or 100.0)
    w["position"] = float(z.get("versatz_pt") or 0.0)
    w["raster"] = z.get("raster") is not False
    w["versteckt"] = bool(z.get("versteckt"))
    return w


def zeichne_absaetze(p: QPainter, rect, absaetze: list[tuple[dict, dict, str]], mittig: bool = False) -> None:
    """Absätze (Absatzformat, Zeichenformat — beides Wörterbücher des Dokumentenmodells —, Text) in ein Rechteck zeichnen: die Vorschau der
    Formatierungsfenster. Gesetzt und gezeichnet wird vom Kern (über ``writer.anbindung.zeichnen``), nicht von Qt."""
    from PySide6.QtCore import QRectF
    from vcl.qt.rendering.formen import raster_malen
    from writer.anbindung import zeichnen as ZW
    feld = (float(rect.left()), float(rect.top()), float(rect.width()), float(rect.height()))
    p.save()
    p.setClipRect(rect)
    raster_malen(p, QRectF(rect), lambda f: ZW.absaetze(f, feld, absaetze, mittig), rand=0.0)
    p.restore()
