"""Aufbau von Gruppen und Schaltflächen im Menüband."""
from __future__ import annotations

import json
import os
from vcl.qt.widgets.bausteine.abstaende.raster import RasterSpalte, RasterZeile
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil, trennlinie
from system import pfade

from PySide6.QtCore import QPropertyAnimation, QRectF, QSize, QTimer, Qt, Signal
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPainter
from PySide6.QtWidgets import (
    QCheckBox, QFontComboBox, QFrame, QLabel, QMenu, QScrollArea, QSizePolicy, QStackedWidget, QToolButton,
    QWidget,
)

from vcl.qt.widgets.menues.dropdown.objektmenues.bild_diagramm_menues import FELDER, GALERIEN, KLAPPEN
from vcl.qt.widgets.dialoge.formatierung.text_format import groesse_feld, schrift_feld
from vcl.qt.widgets.dokumentansicht.bearbeitung.kern_editor import STYLES
from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
from vcl.qt.widgets.bausteine.interaktion.felder.ueberlauf_leiste import UeberlaufLeiste
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import tabellen_gitter
from vcl.qt.widgets.bausteine.interaktion.felder.karten_raster import kachel_gitter
from vcl.qt.widgets.bausteine.farben.thema.thema import kopf_symbolfarbe
from writer.werkzeugleisten.plan import plan
from vcl.qt.widgets.ribbon.band_bausteine import _SperrKasten

from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.interaktion.haken.haken import haken
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import werkzeugknopf
from vcl.qt.widgets.bausteine.rahmen.rahmen.rahmen import rahmen as rahmen_baustein
from vcl.qt.widgets.bausteine.abstaende.mass import BANDGRUPPE_ABSTAND, BANDGRUPPE_KNOPF_ZUGABE, BANDGRUPPE_RAND_KOMPAKT, BANDGRUPPE_RAND_NORMAL, BANDGRUPPE_RAND_OBEN
from vcl.qt.widgets.bausteine.abstaende.mass import DROPDOWN_GROSS_HOEHE, DROPDOWN_HOEHE, ABSTAND_DICHT, ABSTAND_ENG, ABSTAND_KLEIN, BREITE_AUFKLAPPPFEIL, BREITE_BAND_GRUPPENKNOPF, BREITE_GRUPPENTRENNER, BREITE_MASSFELD_BAND, BREITE_RANDFELD_BAND, BREITE_VORLAGEN_AKTUALISIEREN, GROESSE_BANDKNOPF_ICON_KLEIN, GROESSE_GRUPPEN_STARTER, HOEHE_BAND_GRUPPENKNOPF, HOEHE_BAND_GRUPPENKNOPF_KOMPAKT, ICON_GROSS, ICON_KLEIN, ICON_NORMAL, PADDING_BANDKNOPF, RAND_BANDGALERIE, RAND_BANDREITER, RAND_KEIN, RAND_POPUP_KOPF, SCHRIFT_BANDGRUPPE_TITEL, SCHRIFT_BANDKNOPF
from vcl.qt.widgets.menues.dropdown.schriftauswahl import Schriftauswahl
from vcl.qt.widgets.menues.dropdown.dropdown_knopf import DropdownKnopf


def _zeilen_teilen(eintraege: list) -> tuple[bool, list]:
    """Die kleinen Einträge in Zeilen: ``//`` oder ein Zeilenumbruch beginnt eine neue (dann ``explizit``); sonst entscheidet das Gitter."""
    explizit, zeilen, aktuell = False, [], []
    for e in eintraege:
        if e.get("zeilenumbruch") or e.get("symbol") == "//":
            explizit = True
            zeilen.append(aktuell)
            aktuell = []
        elif not e.get("gross") and not e.get("hinweis"):
            aktuell.append(e)
    zeilen.append(aktuell)
    return explizit, zeilen


class BandGruppenBaustein:
    """Erzeugt die Gruppeninhalte und deren Schaltflächen-Anordnungen."""

    def _gruppe(self, g: dict) -> QWidget:
        rahmen = QWidget()
        v = RasterSpalte(rahmen)
        seite = BANDGRUPPE_RAND_KOMPAKT if self.kompakt else BANDGRUPPE_RAND_NORMAL
        v.setContentsMargins(seite, BANDGRUPPE_RAND_OBEN, seite, 0)
        v.setSpacing(0)
        if self.kompakt:
            rahmen.setToolTip(g["name"])                 # die Unterschrift entfällt; der Name steht im Hinweis
        inhalt = RasterZeile()
        inhalt.setSpacing(ABSTAND_DICHT)
        inhalt.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        v.addLayout(inhalt, 1)
        if g.get("katalog") == "raender":
            inhalt.addWidget(self._raender())
        elif g.get("katalog"):
            inhalt.addWidget(self._stile(int(g.get("spalten") or 3)))
        else:
            self._knoepfe(g, inhalt)
        if self.kompakt and not g.get("pfeil"):
            if not g.get("ohne_titel"):
                QLabel(g["name"].upper(), rahmen).hide()           # Unterschrift bleibt als verborgene Beschriftung (Aufbau prüfbar)
            return rahmen
        fuss = RasterZeile()
        fuss.setContentsMargins(*RAND_KEIN)
        t = QLabel("" if g.get("ohne_titel") else g["name"].upper())     # Kontext-Reiter wie in der Vorlage: Gruppen ohne Unterschrift
        t.setVisible(not self.kompakt)
        t.setAlignment(Qt.AlignCenter)
        hinweis_stil(t, zusatz="font-size: " f"{SCHRIFT_BANDGRUPPE_TITEL}" "pt; letter-spacing: 1px;")
        fuss.addStretch(1)
        fuss.addWidget(t)
        if g.get("pfeil"):
            p = werkzeugknopf("fest", symbolbild=symbole.icon("arrow-down-right", GROESSE_GRUPPEN_STARTER[0]),    # Lucide-Symbol statt Schriftzeichen „↘“
                              bildgroesse=QSize(*GROESSE_GRUPPEN_STARTER), groesse=GROESSE_GRUPPEN_STARTER, name=g["name"] + " — Einstellungen",
                              tooltip=g["name"] + " — Einstellungen", aktion=lambda a=g["pfeil"]: self.b.tun(a), aktiv=self.b.hat(g["pfeil"]))
            if not self.b.hat(g["pfeil"]):
                self.fehlend.append(g["pfeil"])
            fuss.addWidget(p)
        fuss.addStretch(1)
        v.addLayout(fuss)
        return rahmen

    def _knoepfe_geordnet(self, g: dict, inhalt: RasterZeile):
        """Knöpfe in der Reihenfolge der Liste: große stehen allein, aufeinanderfolgende kleine bilden eine Spalte aus zwei Zeilen."""
        lauf: list[dict] = []
        felder: list = []                                     # aufeinanderfolgende Eingabefelder stehen übereinander (wie die Kleinknöpfe)

        def rasterspalte(teile: list) -> None:
            """Eine Spalte im Raster des Bandes: so hoch wie ein großer Knopf, das erste Teil oben bündig, das letzte unten bündig."""
            host = QWidget()
            v = RasterSpalte(host)
            v.setContentsMargins(*RAND_KEIN)
            v.setSpacing(ABSTAND_DICHT)
            for n, w in enumerate(teile):
                if n:
                    v.addStretch(1)
                v.addWidget(w)
            if len(teile) == 1:
                v.addStretch(1)
            host.setMinimumHeight(DROPDOWN_GROSS_HOEHE[self.kompakt])
            inhalt.addWidget(host, 0, Qt.AlignTop)

        def feldspalte():
            if felder:
                rasterspalte(list(felder))
                felder.clear()

        def spalte(felder_behalten=False):
            if not felder_behalten:
                feldspalte()
            for i in range(0, len(lauf), 2):                    # je Spalte zwei Zeilen
                rasterspalte([self._knopf(e, False) for e in lauf[i:i + 2]])
            lauf.clear()
        for e in g["knoepfe"]:
            if e.get("feld"):                                     # ein Eingabefeld, das der Befehls-Baustein liefert (band_feld)
                spalte(felder_behalten=True)
                bau = FELDER.get(e["feld"])                    # erst die Felder der Oberfläche, sonst ``feld_<name>`` des Befehlsbausteins
                w = bau(self.b) if bau else self.b.band_feld(e["feld"])
                if w is not None:
                    self.felder[e["feld"]] = w
                    felder.append(w)
            elif e.get("gross"):
                spalte()
                inhalt.addWidget(self._knopf(e, True), 0, Qt.AlignTop)
            else:
                feldspalte()
                lauf.append(e)
        spalte()

    def _knoepfe_schrift(self, g: dict, inhalt: RasterZeile):
        """Wie in der Vorlage: oben Schriftname und -größe, daneben die Größen-/Löschknöpfe; darunter die Zeichenformate."""
        from vcl.qt.widgets.bausteine.symbole.bauteile.live_vorschau import VorschauCombo, VorschauFontCombo
        vs = self.b.w.vorschau

        def _zu_pt(t):
            try:
                return float(t.replace(",", "."))
            except ValueError:
                return None
        font = schrift_feld(VorschauFontCombo(lambda n: vs.zeigen(lambda e: e.set_font_family(n)), vs.ende))
        groesse = groesse_feld(VorschauCombo(lambda t: (pt := _zu_pt(t)) is not None and vs.zeigen(lambda e: e.set_font_size(pt)), vs.ende))
        stil = VorschauCombo(lambda n: vs.zeigen(lambda e: e.apply_style("Standard" if n == "Fließtext" else n)), vs.ende)
        stil.setAccessibleName("Formatvorlage")
        font.setAccessibleName("Schriftart"); groesse.setAccessibleName("Schriftgröße")
        stil.addItems(["Fließtext"] + [n for n in STYLES if n != "Standard"])
        stil.setParent(self)                                   # die Stile stehen in der Galerie; die Auswahl bleibt nur für den Abgleich
        stil.hide()
        self.felder.update(stil=stil, font=font, groesse=groesse)
        zeilen, aktuell = [], []
        for e in g["knoepfe"]:
            if e.get("zeilenumbruch"):
                zeilen.append(aktuell)
                aktuell = []
            else:
                aktuell.append(e)
        zeilen.append(aktuell)
        v = RasterSpalte()
        v.setSpacing(ABSTAND_ENG)
        v.setContentsMargins(*RAND_KEIN)
        for i, zeile in enumerate(zeilen):
            h = RasterZeile()
            h.setSpacing(ABSTAND_DICHT)
            h.setContentsMargins(*RAND_KEIN)
            if i == 0:
                h.addWidget(font)
                h.addWidget(groesse)
                h.addSpacing(BANDGRUPPE_ABSTAND)
            for e in zeile:
                h.addWidget(self._knopf(e, False))
            h.addStretch(1)
            v.addLayout(h)
        v.addStretch(1)
        inhalt.addLayout(v)

    def _knoepfe_tt_schrift(self, g: dict, inhalt: RasterZeile):
        """Texttools: Schriftname und -größe oben (wirken auf das markierte WordArt/Textfeld), darunter die Zeichenformate — wie bei Start."""
        font = schrift_feld(Schriftauswahl())
        groesse = groesse_feld()
        font.activated.connect(lambda _i: self.b.ttSchriftart(font.currentText()))
        groesse.activated.connect(lambda _i: self.b.ttGroesse(groesse.currentText()))
        groesse.lineEdit().returnPressed.connect(lambda: self.b.ttGroesse(groesse.currentText()))
        self.felder.update(tt_font=font, tt_groesse=groesse)
        zeilen, aktuell = [], []
        for e in g["knoepfe"]:
            if e.get("zeilenumbruch"):
                zeilen.append(aktuell)
                aktuell = []
            else:
                aktuell.append(e)
        zeilen.append(aktuell)
        v = RasterSpalte()
        v.setSpacing(ABSTAND_ENG)
        v.setContentsMargins(*RAND_KEIN)
        for i, zeile in enumerate(zeilen):
            h = RasterZeile()
            h.setSpacing(ABSTAND_DICHT)
            h.setContentsMargins(*RAND_KEIN)
            if i == 0:
                h.addWidget(font)
                h.addWidget(groesse)
                h.addSpacing(BANDGRUPPE_ABSTAND)
            for e in zeile:
                h.addWidget(self._knopf(e, False))
            h.addStretch(1)
            v.addLayout(h)
        v.addStretch(1)
        inhalt.addLayout(v)

    def _knoepfe_galerie(self, g: dict, inhalt: RasterZeile):
        """Eine Galerie wie in der Vorlage: drei Kacheln zum Anklicken und daneben ein Pfeil mit der ganzen Auswahl (Befehl ``galerie_<name>``)."""
        bau = GALERIEN.get(g["galerie"])                          # erst die Bausteine der Oberfläche, sonst ``galerie_<name>`` des Befehlsbausteins
        spec = (lambda: bau(self.b)) if bau else getattr(self.b, "galerie_" + g["galerie"], None)
        if spec is None:
            self.fehlend.append("galerie_" + g["galerie"])
            return
        spec = spec()
        spec = dict(spec, kacheln=spec["kacheln"][:int(g.get("kacheln") or len(spec["kacheln"]))])   # ``"kacheln": N``: nur N Kacheln im Band, alle Einträge bleiben im Pfeil-Menü
        rahmen = rahmen_baustein("panel")
        h = RasterZeile(rahmen)
        h.setContentsMargins(*RAND_BANDGALERIE)
        h.setSpacing(ABSTAND_ENG)
        zeilen = int(g.get("zeilen") or 1)                       # ``"zeilen": 2``: Kacheln in mehreren Reihen (Linien und Pfeile)
        spalten = -(-len(spec["kacheln"]) // zeilen)
        raster = kachel_gitter((), spalten, abstand=ABSTAND_ENG) if zeilen > 1 else None
        if raster is not None:
            h.addLayout(raster)
        for nr, (tipp, pm, tun) in enumerate(spec["kacheln"]):
            k = werkzeugknopf("fest", symbolbild=QIcon(pm), bildgroesse=pm.size(),
                              groesse=(pm.width() + BANDGRUPPE_KNOPF_ZUGABE, pm.height() + BANDGRUPPE_KNOPF_ZUGABE),
                              tooltip=tipp, hand=True,                                  # klickbare Kachel: Hand
                              aktion=lambda f=tun: (f(), self.aktualisieren()))
            if raster is not None:
                raster.addWidget(k, nr // spalten, nr % spalten)
            else:
                h.addWidget(k)
            self.knoepfe.append((k, None, True))
        mehr = DropdownKnopf()
        mehr.setAutoRaise(True)
        mehr.setArrowType(Qt.DownArrow)
        mehr.setToolTip(spec["name"])
        mehr.menue_setzen(spec["menue"], geteilt=False, besitzen=True)
        mehr.groesse_rolle("mehr", "band"); mehr.setCursor(Qt.PointingHandCursor)
        h.addWidget(mehr)
        self.knoepfe.append((mehr, None, True))
        inhalt.addWidget(rahmen, 0, Qt.AlignTop)

    def _knoepfe_raender(self, g: dict, inhalt: RasterZeile):
        """Der Rand-Knopf und daneben wie in der Vorlage die vier Maßfelder Oben/Unten/Links/Rechts (in der gewählten Maßeinheit)."""
        from vcl.qt.widgets.bausteine.interaktion.felder.mass_feld import MassSpin as _MassSpin
        self._knoepfe_geordnet(g, inhalt)
        host = QWidget()
        gitter = tabellen_gitter(host, waagerecht=ABSTAND_KLEIN, senkrecht=ABSTAND_ENG)       # Menüband: Beschriftung und Maßfeld in festen Zellen
        spins = {}
        for zeile, spalte, schl, name in ((0, 0, "oben", "Oben:"), (0, 2, "unten", "Unten:"), (1, 0, "links", "Links:"), (1, 2, "rechts", "Rechts:")):
            sp = _MassSpin()
            sp.setRange(0.0, 200.0)
            sp.setDecimals(1)
            sp.setSingleStep(1.0)
            sp.setKeyboardTracking(False)
            sp.setFixedWidth(BREITE_RANDFELD_BAND); sp.setMinimumHeight(DROPDOWN_HOEHE); sp.setProperty("dropdownFeld", True)
            gitter.addWidget(QLabel(name), zeile, spalte)
            gitter.addWidget(sp, zeile, spalte + 1)
            spins[schl] = sp
            self.felder["rand_" + schl] = sp
            self.knoepfe.append((sp, None, True))
        for sp in spins.values():
            sp.valueChanged.connect(lambda _v, sps=spins: self.b.setzeRaender(
                sps["oben"].value(), sps["unten"].value(), sps["links"].value(), sps["rechts"].value()))
        inhalt.addWidget(host, 0, Qt.AlignTop)

    def _knoepfe_masse(self, g: dict, inhalt: RasterZeile):
        """Höhe und Breite des markierten Bildes (Zeichentools); „Seitenverhältnis sperren“ hält das Verhältnis beim Ändern.
        ``"sperre": "bild"`` (Bildtools): Breite oben, Höhe unten; rechts daneben stehen die ersten beiden Knöpfe der Gruppe
        (Sperre = Schalter ``bildSeitenverhaeltnis``, dann „Größe zurücksetzen“).
        ``"befehl"`` nennt den Aufruf (Vorgabe ``zeichenMasse(breite_mm, hoehe_mm)``); ``"verhaeltnis": False`` lässt Sperre und Verhältnis weg
        und meldet nur das geänderte Maß (Tabellentools: ``tabelleMasse``)."""
        from vcl.qt.widgets.bausteine.interaktion.felder.mass_feld import MassSpin as _MassSpin
        bild = g.get("sperre") == "bild"
        befehl = g.get("befehl", "zeichenMasse")
        verh = g.get("verhaeltnis", True)
        vor = g.get("praefix") or ("bt_" if bild else "bild_")   # eigene Feldnamen: Bildtools, Zeichentools und SmartArt-Design haben je ein Paar
        host = QWidget()
        gitter = tabellen_gitter(host, waagerecht=ABSTAND_KLEIN, senkrecht=ABSTAND_ENG)       # Menüband: Beschriftung, Maßfeld und Sperre in festen Zellen
        spins = {}
        if bild:                                                  # große Knöpfe (Zuschneiden) stehen links vor den Feldern
            for e in (e for e in g["knoepfe"] if e.get("gross")):
                inhalt.addWidget(self._knopf(e, True), 0, Qt.AlignTop)
        zeilen = (("breite", "Breite:"), ("hoehe", "Höhe:")) if bild else (("hoehe", "Höhe:"), ("breite", "Breite:"))
        for zeile, (schl, name) in enumerate(zeilen):
            sp = _MassSpin(); sp.setRange(1.0, 2000.0); sp.setDecimals(1); sp.setSingleStep(1.0); sp.setKeyboardTracking(False); sp.setFixedWidth(BREITE_MASSFELD_BAND); sp.setMinimumHeight(DROPDOWN_HOEHE); sp.setProperty("dropdownFeld", True)
            gitter.addWidget(QLabel(name), zeile, 0); gitter.addWidget(sp, zeile, 1)
            spins[schl] = sp
            self.felder[vor + schl] = sp
            self.knoepfe.append((sp, None, True))
        sperre = None
        if bild:
            kl = [e for e in g["knoepfe"] if not e.get("gross")]
            if kl:                                                # Seitenverhältnis sperren: Kontrollkästchen, Zustand = Bild (an_bildSeitenverhaeltnis)
                kasten = _SperrKasten(kl[0]["name"], self.b)
                gitter.addWidget(kasten, 0, 2)
                self.felder[vor + "sperrkasten"] = kasten
                self.knoepfe.append((kasten, kl[0].get("tun"), True))
            for zeile, e in enumerate(kl[1:2], 1):
                gitter.addWidget(self._knopf(e, False), zeile, 2)
        elif verh:
            sperre = haken("standard", "Seitenverhältnis sperren", an=True)
            gitter.addWidget(sperre, 2, 0, 1, 2)
            self.felder[vor + "sperre"] = sperre
        verhaeltnis = [1.0]

        def gesperrt() -> bool:
            if not verh:
                return False
            return bool(self.b.an_bildSeitenverhaeltnis()) if bild else sperre.isChecked()

        def geaendert(wer: str):
            b, h = spins["breite"].value(), spins["hoehe"].value()
            if not verh:
                getattr(self.b, befehl)(**{("breite_mm" if wer == "breite" else "hoehe_mm"): b if wer == "breite" else h})
                return
            if gesperrt() and verhaeltnis[0] > 0:
                for sp in spins.values():
                    sp.blockSignals(True)
                if wer == "breite":
                    h = b / verhaeltnis[0]; spins["hoehe"].setValue(h)
                else:
                    b = h * verhaeltnis[0]; spins["breite"].setValue(b)
                for sp in spins.values():
                    sp.blockSignals(False)
            else:
                verhaeltnis[0] = b / max(0.1, h)
            getattr(self.b, befehl)(b, h)
        spins["breite"].valueChanged.connect(lambda _v: geaendert("breite"))
        spins["hoehe"].valueChanged.connect(lambda _v: geaendert("hoehe"))
        self.felder[vor + "verhaeltnis"] = verhaeltnis
        inhalt.addWidget(host, 0, Qt.AlignTop)

    _FELDER_BAUER = {"raender": "_knoepfe_raender", "masse": "_knoepfe_masse", "zeile": "_knoepfe_schrift", "tt_zeile": "_knoepfe_tt_schrift"}

    def _knoepfe(self, g: dict, inhalt: RasterZeile):
        art = g.get("felder")
        if art in self._FELDER_BAUER:
            return getattr(self, self._FELDER_BAUER[art])(g, inhalt)
        if g.get("galerie"):
            return self._knoepfe_galerie(g, inhalt)
        if g.get("reihenfolge"):
            return self._knoepfe_geordnet(g, inhalt)
        if art:
            self._knoepfe_formatfelder(inhalt)
        self._knoepfe_gitter(g["knoepfe"], inhalt)

    def _knoepfe_formatfelder(self, inhalt: RasterZeile) -> None:
        """Formatvorlage, Schriftart und Größe als Spalte vor den Knöpfen."""
        spalte = RasterSpalte()
        spalte.setSpacing(ABSTAND_ENG)
        for w in self._formatfelder():
            spalte.addWidget(w)
        inhalt.addLayout(spalte)

    def _formatfelder(self) -> tuple:
        """Die Felder Formatvorlage, Schriftart und Schriftgröße mit Live-Vorschau; sie stehen danach in ``felder`` (``stil``, ``font``, ``groesse``)."""
        from vcl.qt.widgets.bausteine.symbole.bauteile.live_vorschau import VorschauCombo, VorschauFontCombo
        vs = self.b.w.vorschau

        def _zu_pt(t):
            try:
                return float(t.replace(",", "."))
            except ValueError:
                return None
        stil = VorschauCombo(lambda n: vs.zeigen(lambda e: e.apply_style("Standard" if n == "Fließtext" else n)), vs.ende)
        stil.setAccessibleName("Formatvorlage")
        stil.rolle("formatvorlage", "band")
        stil.addItems(["Fließtext"] + [n for n in STYLES if n != "Standard"])
        font = schrift_feld(VorschauFontCombo(lambda n: vs.zeigen(lambda e: e.set_font_family(n)), vs.ende))
        groesse = groesse_feld(VorschauCombo(lambda t: (pt := _zu_pt(t)) is not None and vs.zeigen(lambda e: e.set_font_size(pt)), vs.ende))
        font.setAccessibleName("Schriftart"); groesse.setAccessibleName("Schriftgröße")
        self.felder.update(stil=stil, font=font, groesse=groesse)
        return stil, font, groesse

    def _gitter_fuellen(self, gitter, explizit: bool, zeilen: list, kleine: list) -> None:
        """Die kleinen Knöpfe ins Gitter: explizit zeilenweise, sonst spaltenweise in zwei Zeilen."""
        zwei = len([z for z in zeilen if z]) == 2 if explizit else len(kleine) > 1       # genau zwei Zeilen: obere oben bündig, untere unten bündig
        lage = (Qt.AlignTop, Qt.AlignBottom) if zwei else (Qt.AlignmentFlag(0), Qt.AlignmentFlag(0))
        if explizit:
            for r, zeile in enumerate(zeilen):
                for c, e in enumerate(zeile):
                    gitter.addWidget(self._knopf(e, False), r, c, lage[min(r, 1)])
        else:
            for i, e in enumerate(kleine):
                gitter.addWidget(self._knopf(e, False), i % 2, i // 2, lage[i % 2])

    def _knoepfe_gitter(self, eintraege: list, inhalt: RasterZeile) -> None:
        """Große Knöpfe nebeneinander, kleine im Gitter (zwei Zeilen oder explizite Zeilen)."""
        grosse = [e for e in eintraege if e.get("gross")]
        kleine = [e for e in eintraege if not e.get("gross") and not e.get("hinweis") and e.get("symbol") != "//"]
        for e in grosse:
            inhalt.addWidget(self._knopf(e, True), 0, Qt.AlignTop)
        explizit, zeilen = _zeilen_teilen(eintraege)
        gitter = tabellen_gitter(rand=None, abstand=ABSTAND_DICHT)
        self._gitter_fuellen(gitter, explizit, zeilen, kleine)
        if kleine:
            host = QWidget()
            host.setLayout(gitter)
            host.setMinimumHeight(DROPDOWN_GROSS_HOEHE[self.kompakt])          # dasselbe Raster wie die großen Knöpfe: oben und unten bündig
            inhalt.addWidget(host, 0, Qt.AlignTop)
