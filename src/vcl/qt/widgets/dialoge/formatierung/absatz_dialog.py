"""Das Fenster „Absatz“ (Einzüge und Abstände, Zeilen- und Seitenumbruch) als Baustein.

    d = AbsatzDialog(parent, werte)                      # alle Felder; ``umfang`` ist nur ein Name für den Aufrufer (Absatz oder Formatvorlage)
    if d.exec(): d.werte()                               # dict, siehe ``ABSATZ``

Das Fenster formatiert nichts selbst. Die Tabstopps stehen unter ``werte()["tabs"]`` (Liste aus mm und Ausrichtung) und kommen aus
dem Baustein ``TabstoppDialog``. Nur, was Lunivo wirklich zeichnen und speichern kann, steht darin: Qt kennt keine Regeln wie
„Absatz nicht trennen“, darum fehlen sie.
"""
from __future__ import annotations

from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QDialog, QGridLayout, QGroupBox, QLabel, QPushButton, QRadioButton, QTabWidget,
    QToolButton, QWidget,
)

from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import VorschauFlaeche, fussleiste
from writer.anbindung import absatzoptionen as _absatzoptionen
from vcl.qt.widgets.bausteine.interaktion.felder.mass_feld import _PT_MM, EinheitFeld, spin
from vcl.qt.widgets.dialoge.dokument.tabstopp_dialog import TabstoppDialog
from vcl.qt.widgets.dialoge.formatierung.text_format import AUSRICHTUNG, zeichne_absaetze
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FENSTER_ABSATZ, RAND_KEIN
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld

ABSATZ = {"ausr": "links", "rtl": False, "einzug": 0.0, "rechts": 0.0, "erste": 0.0, "vor": 0.0, "nach": 0.0, "zeilen": 1.0,
          "zeilen_art": "faktor", "zeilen_pt": 12.0, "ebene": 0, "umbruch": False, "tabs": [], "opt": {}}
_MM = 2.2                                        # Bildpunkte je Millimeter in der Vorschau
_SONDER = (("keiner", "(Kein)"), ("erste", "Erste Zeile"), ("haengend", "Hängend"))
_ZEILEN = (("faktor", 1.0, "Einfach"), ("faktor", 1.5, "1,5 Zeilen"), ("faktor", 2.0, "Doppelt"), ("mindestens", 0.0, "Mindestens"),
           ("genau", 0.0, "Genau"), ("faktor", 0.0, "Mehrfach"))


from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.interaktion.felder.angepasste_reiter import AngepassteReiter
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, UmbruchSchalter, abschnittstitel
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.farben.farben import ABSATZ_VORSCHAU_GRAU
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf, werkzeugknopf
from vcl.qt.widgets.bausteine.interaktion.option.option import option


def aus_absatz(af: dict, dokument) -> dict:
    """Die Werte eines wirksamen Absatzformats (Wörterbuch des Dokumentenmodells, siehe ``formatwerte.absatzformat``) für das Fenster (Gegenstück zu
    ``werte()``): Einzüge in mm, Abstände in pt, Zeilenabstand."""
    from writer.anbindung import formatwerte as _formatwerte
    from core.formatierung.absatz import absatzopt
    from writer.anbindung import absatzoptionen as _absatzoptionen
    from writer.werte import px_zu_mm as px_to_mm
    from vcl.qt.widgets.dialoge.dokument.tabstopp_dialog import aus_absatz as tabs_aus_absatz
    art, wert = _formatwerte.zeilenabstand(af)
    links, rechts, erste = _formatwerte.einzuege(af)
    vor, nach = _formatwerte.abstaende(af)
    roh = af.get("optionen")
    return {"ausr": af.get("ausrichtung") if af.get("ausrichtung") in ("mitte", "rechts", "block") else "links", "rtl": _formatwerte.richtung(af) == "rtl",
            "einzug": px_to_mm(links), "rechts": px_to_mm(rechts), "erste": px_to_mm(erste), "vor": vor * 0.75, "nach": nach * 0.75,
            "zeilen": wert / 100 if art == "proportional" and wert else 1.0, "zeilen_art": {"fixed": "genau", "min": "mindestens"}.get(art, "faktor"),
            "zeilen_pt": round(wert * 0.75, 1) if art in ("fixed", "min") else 12.0, "ebene": int(af.get("gliederungsebene") or 0),
            "opt": {**_absatzoptionen.vorgabe(), **(absatzopt.aus_text(roh) if isinstance(roh, str) else {})}, "umbruch": bool(af.get("seitenumbruch_vor")),
            "tabs": tabs_aus_absatz(af, dokument)}


def werte_von(editor, absatz) -> dict:
    """Die Fensterwerte des Absatzes ``absatz`` im Dokument des Editors."""
    from core.layout.drucklayout import formatwerte as F
    d = editor.sitzung.dokument
    return aus_absatz(F.absatzformat(d, absatz), d)


def werte_an_marke(editor) -> dict:
    """Die Fensterwerte des Absatzes an der Schreibmarke."""
    return werte_von(editor, editor._absatz_an_marke())


class AbsatzDialog(PanelFaehig, QDialog):
    def __init__(self, parent=None, werte: dict | None = None, *, umfang: str = "text"):
        super().__init__(parent)
        self.setWindowTitle("Absatz")
        self.resize(*GROESSE_FENSTER_ABSATZ)
        self.umfang = umfang
        w = {**ABSATZ, **(werte or {})}
        self._tabs = list(w["tabs"])
        v = _spalte("standard", self)
        self.reiter = AngepassteReiter(); v.addWidget(self.reiter, 1)
        # ---- Einzüge und Abstände: flach, Felder als Reihen (je nach Breite 2 bis 4 nebeneinander), keine Gruppenrahmen
        s = QWidget(); g = FormularGitter(s)
        self.ausr = Auswahlfeld()
        for k, name in AUSRICHTUNG:
            self.ausr.addItem(name, k)
        self.ebene = Auswahlfeld(); self.ebene.addItem("Textkörper", 0)
        for i in range(1, 10):
            self.ebene.addItem(f"Ebene {i}", i)
        self.r_rtl, self.r_ltr = option("standard", "Rechts nach links"), option("standard", "Links nach rechts")
        self.richtung = QButtonGroup(self); self.richtung.addButton(self.r_rtl); self.richtung.addButton(self.r_ltr)
        rz = FlussLayout(10); rz.addWidget(self.r_rtl); rz.addWidget(self.r_ltr)
        g.reihe(("Ausrichtung:", self.ausr), ("Gliederungsebene:", self.ebene))
        g.zeile("Richtung:", rz)
        g.breit(abschnittstitel("Einzug"))
        self.links = EinheitFeld(0.0, 0.0, 300.0); self.rechts = EinheitFeld(0.0, 0.0, 300.0); self.sonder = Auswahlfeld()
        for k, name in _SONDER:
            self.sonder.addItem(name, k)
        self.sonder_mass = EinheitFeld(0.0, 0.0, 300.0)
        g.reihe(("Vor Text:", self.links), ("Nach Text:", self.rechts), ("Sondereinzug:", self.sonder), ("Von:", self.sonder_mass))
        g.breit(abschnittstitel("Abstand"))
        self.vor = EinheitFeld(0.0, 0.0, 200 * _PT_MM, ("pt", "Zeile", "mm", "cm", "in"), "pt")
        self.nach = EinheitFeld(0.0, 0.0, 200 * _PT_MM, ("pt", "Zeile", "mm", "cm", "in"), "pt")
        self.zeilen_art = Auswahlfeld()
        for art, f, name in _ZEILEN:
            self.zeilen_art.addItem(name, (art, f))
        self.zeilen = spin(1.0, 0.1, 10.0, " ×", 0.05, 2)
        self.zeilen_pt = spin(12.0, 1.0, 1000.0, " pt", 0.5, 1)
        zf = _spalte("standard"); zf.addWidget(self.zeilen); zf.addWidget(self.zeilen_pt)      # je nach Art ist eines davon zu sehen
        g.reihe(("Vor:", self.vor), ("Nach:", self.nach), ("Zeilenabstand:", self.zeilen_art), ("Von:", zf))
        self.reiter.addTab(s, "Einzüge und Abstände")
        # ---- Zeilen- und Seitenumbruch: das Gebräuchliche sichtbar, asiatische Regeln und Raster eingeklappt
        u = QWidget(); ul = FormularGitter(u)
        self.cb = {k: UmbruchSchalter(t) for k, t in (
            ("kontrolle", "Absatzkontrolle"), ("nicht_trennen", "Nicht vom nächsten Absatz trennen"), ("zusammen", "Diesen Absatz zusammenhalten"),
            ("asiat", "Asiatische Regeln zum Steuern von Anfangs- und Endzeichen verwenden"),
            ("mitten", "Textumbruch in der Mitte eines Wortes für westlichen Text zulassen"), ("haengend", "Hängende Interpunktion zulassen"),
            ("kompr", "Interpunktion am Zeilenbeginn zum Komprimieren zulassen"),
            ("ade", "Abstand zwischen asiatischem und westlichem Text automatisch anpassen"),
            ("adn", "Abstand zwischen asiatischem Text und Zahlen automatisch anpassen"))}
        self.umbruch = UmbruchSchalter("Seitenumbruch oberhalb")
        self.rest_einzug = UmbruchSchalter("Bei Dokumentrasterdefinition rechten Einzug automatisch ausrichten")
        self.raster = UmbruchSchalter("Bei Dokumentrasterdefinition am Raster ausrichten")
        self.textausr = Auswahlfeld()
        for k, name in (("auto", "Automatisch"), ("top", "Oben"), ("center", "Zentriert"), ("baseline", "Basislinie"), ("bottom", "Unten")):
            self.textausr.addItem(name, k)
        ul.breit(abschnittstitel("Seitenumbruch"))
        for w_ in (self.cb["kontrolle"], self.cb["nicht_trennen"], self.cb["zusammen"], self.umbruch, self.cb["mitten"], self.cb["haengend"]):
            ul.breit(w_)
        ul.zeile("Textausrichtung:", self.textausr)
        erweitert = QWidget(); el = FormularGitter(erweitert)
        for w_ in (self.cb["asiat"], self.cb["kompr"], self.cb["ade"], self.cb["adn"], self.rest_einzug, self.raster):
            el.breit(w_)
        erweitert.setVisible(False)
        self.erweitert_knopf = werkzeugknopf("standard", "Asiatische Typografie und Raster", flach=False); self.erweitert_knopf.setArrowType(Qt.RightArrow)
        self.erweitert_knopf.setToolButtonStyle(Qt.ToolButtonTextBesideIcon); self.erweitert_knopf.setAutoRaise(True); self.erweitert_knopf.setCheckable(True)
        self.erweitert_knopf.toggled.connect(lambda an: (erweitert.setVisible(an), self.erweitert_knopf.setArrowType(Qt.DownArrow if an else Qt.RightArrow)))
        ul.breit(self.erweitert_knopf); ul.breit(erweitert)
        self.reiter.addTab(u, "Zeilen- und Seitenumbruch")
        # ---- Vorschau und Knöpfe
        v.addWidget(QLabel("Vorschau"))
        self.vorschau = VorschauFlaeche(self._male, 120); v.addWidget(self.vorschau)
        self.tabs_knopf = knopf("standard", "Tabstopps …", aktion=self._tabstopps)
        fussleiste(self, v, self.tabs_knopf)
        self.setze(w)
        for sig in (self.ausr.currentIndexChanged, self.r_rtl.toggled, self.links.valueChanged, self.rechts.valueChanged,
                    self.sonder.currentIndexChanged, self.sonder_mass.valueChanged, self.vor.valueChanged, self.nach.valueChanged,
                    self.zeilen.valueChanged):
            sig.connect(lambda *_: self._neu())
        self.zeilen_art.currentIndexChanged.connect(self._zeilenart)
        self.sonder.currentIndexChanged.connect(lambda *_: self._neu())
        self._neu()

    def setze(self, w: dict) -> None:
        self.ausr.setCurrentIndex(max(0, self.ausr.findData(w["ausr"])))
        (self.r_rtl if w["rtl"] else self.r_ltr).setChecked(True)
        self.ebene.setCurrentIndex(max(0, self.ebene.findData(w["ebene"])))
        self.links.setValue(w["einzug"]); self.rechts.setValue(w["rechts"])
        e = w["erste"]
        self.sonder.setCurrentIndex(1 if e > 0 else 2 if e < 0 else 0)
        self.sonder_mass.setValue(abs(e))
        self.vor.setValue(w["vor"] * _PT_MM); self.nach.setValue(w["nach"] * _PT_MM)      # Werte in pt, Felder in mm
        z = w["zeilen"] or 1.0
        self.zeilen_pt.setValue(w["zeilen_pt"])
        daten = [tuple(self.zeilen_art.itemData(k)) for k in range(self.zeilen_art.count())]
        wunsch = (w["zeilen_art"], 0.0) if w["zeilen_art"] != "faktor" else ("faktor", z)
        i = daten.index(wunsch) if wunsch in daten else daten.index(("faktor", 0.0)) if ("faktor", 0.0) in daten else 0
        self.zeilen_art.setCurrentIndex(max(0, i))
        self.zeilen.setValue(z)
        self.umbruch.setChecked(bool(w["umbruch"]))
        o = {**_absatzoptionen.vorgabe(), **w["opt"]}
        self._opt_alt = dict(o)                              # Optionen ohne Feld im Fenster (z. B. Zeilennummern unterdrücken) bleiben erhalten
        for k, c in self.cb.items():
            c.setChecked(o[k])
        self.rest_einzug.setChecked(o["rest_einzug"]); self.raster.setChecked(o["raster"])
        self.textausr.setCurrentIndex(max(0, self.textausr.findData(o["textausr"])))
        self._zeilenart()

    def _zeilenart(self, *_) -> None:
        art, f = tuple(self.zeilen_art.currentData())
        if art == "faktor" and f:
            self.zeilen.setValue(f)
        self.zeilen.setVisible(art == "faktor" and self.umfang != "x"); self.zeilen_pt.setVisible(art != "faktor" and self.umfang == "text")
        self.zeilen.setEnabled(art == "faktor" and not f)
        self._neu()

    def _neu(self) -> None:
        self.sonder_mass.setEnabled(self.sonder.currentData() != "keiner")
        self.vorschau.update()

    def werte(self) -> dict:
        s = self.sonder.currentData()
        m = self.sonder_mass.value()
        art = tuple(self.zeilen_art.currentData())[0]
        return {"ausr": self.ausr.currentData(), "rtl": self.r_rtl.isChecked(), "ebene": self.ebene.currentData(), "einzug": self.links.value(),
                "rechts": self.rechts.value(), "erste": m if s == "erste" else -m if s == "haengend" else 0.0,
                "vor": self.vor.value() / _PT_MM, "nach": self.nach.value() / _PT_MM, "zeilen": self.zeilen.value(), "zeilen_art": art,
                "zeilen_pt": self.zeilen_pt.value(), "opt": self._opt(), "umbruch": self.umbruch.isChecked(), "tabs": list(self._tabs)}

    def _opt(self) -> dict:
        o = dict(getattr(self, "_opt_alt", {}))
        o.update({k: c.isChecked() for k, c in self.cb.items()})
        o.update(rest_einzug=self.rest_einzug.isChecked(), raster=self.raster.isChecked(), textausr=self.textausr.currentData())
        return o

    def _tabstopps(self) -> None:
        from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import zeige_unter
        d = TabstoppDialog(self, self._tabs)
        zeige_unter(self, d, lambda: setattr(self, "_tabs", d.stopps()))

    def _male(self, p, rect) -> None:
        """Vorhergehender Absatz (grau), der eigene mit Einzügen und Abständen, folgender Absatz (grau)."""
        w = self.werte()
        grau = {"schrift": "Liberation Sans", "groesse_pt": 7.5, "farbe": ABSATZ_VORSCHAU_GRAU}
        f = {"schrift": "Liberation Sans", "groesse_pt": 9.0, "farbe": Farbe.SYMBOL}
        bf = {"einzug_links": w["einzug"] * _MM, "einzug_rechts": w["rechts"] * _MM, "einzug_erste": w["erste"] * _MM,
              "abstand_vor": w["vor"] * 0.8, "abstand_nach": w["nach"] * 0.8,
              "ausrichtung": w["ausr"], "richtung": "rtl" if w["rtl"] else None}
        if w["zeilen_art"] == "faktor":
            bf.update({"zeilenabstand_art": "vielfach", "zeilenabstand": w["zeilen"] * 100})
        else:
            bf.update({"zeilenabstand_art": w["zeilen_art"], "zeilenabstand": w["zeilen_pt"] / 0.75 * _MM / 3.78})
        zeichne_absaetze(p, rect.adjusted(6, 4, -6, -4), [
            ({}, grau, "Vorhergehender Absatz " * 6), ({k: v for k, v in bf.items() if v is not None}, f, "Beispieltext " * 14),
            ({}, grau, "Folgender Absatz " * 6)])
