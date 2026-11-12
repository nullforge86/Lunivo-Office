"""Aufbau von Gruppen und Schaltflächen im Menüband."""
from __future__ import annotations

import json
import os
from lunivo_writer.oberflaeche.baukasten.basis.texte import hinweis_stil, trennlinie
from lunivo_writer.kern import pfade

from PySide6.QtCore import QPropertyAnimation, QRectF, QSize, QTimer, Qt, Signal
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPainter
from PySide6.QtWidgets import (
    QCheckBox, QFontComboBox, QFrame, QHBoxLayout, QLabel, QMenu, QScrollArea, QSizePolicy, QStackedWidget, QToolButton,
    QVBoxLayout, QWidget,
)

from lunivo_writer.oberflaeche.baukasten.dropdown.objektmenues.bild_diagramm_menues import FELDER, GALERIEN, KLAPPEN
from lunivo_writer.oberflaeche.baukasten.formatierung.text_format import groesse_feld, schrift_feld
from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import STYLES
from lunivo_writer.oberflaeche.bauteile import symbole
from lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste import MenueListe
from lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste import UeberlaufLeiste
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import tabellen_gitter
from lunivo_writer.oberflaeche.baukasten.felder.karten_raster import kachel_gitter
from lunivo_writer.oberflaeche.thema import kopf_symbolfarbe
from lunivo_writer.oberflaeche.band.plan import plan
from lunivo_writer.oberflaeche.band.band_bausteine import _SperrKasten

from lunivo_writer.kern.farben import Farbe
from lunivo_writer.oberflaeche.baukasten.basis.mass import (
    DROPDOWN_HOEHE,
    ABSTAND_DICHT,
    ABSTAND_ENG,
    ABSTAND_KLEIN,
    BREITE_AUFKLAPPPFEIL,
    BREITE_BAND_GRUPPENKNOPF,
    BREITE_GRUPPENTRENNER,
    BREITE_MASSFELD_BAND,
    BREITE_RANDFELD_BAND,
    BREITE_VORLAGEN_AKTUALISIEREN,
    GROESSE_BANDKNOPF_ICON_KLEIN,
    GROESSE_GRUPPEN_STARTER,
    HOEHE_BAND_GRUPPENKNOPF,
    HOEHE_BAND_GRUPPENKNOPF_KOMPAKT,
    ICON_GROSS,
    ICON_KLEIN,
    ICON_NORMAL,
    PADDING_BANDKNOPF,
    RAND_BANDGALERIE,
    RAND_BANDREITER,
    RAND_KEIN,
    RAND_POPUP_KOPF,
    SCHRIFT_BANDGRUPPE_TITEL,
    SCHRIFT_BANDKNOPF,
)
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld import Schriftauswahl
from lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf import DropdownKnopf


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
        v = QVBoxLayout(rahmen)
        v.setContentsMargins(1 if self.kompakt else 3, 2, 1 if self.kompakt else 3, 0)
        v.setSpacing(0)
        if self.kompakt:
            rahmen.setToolTip(g["name"])                 # die Unterschrift entfällt; der Name steht im Hinweis
        inhalt = QHBoxLayout()
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
        fuss = QHBoxLayout()
        fuss.setContentsMargins(*RAND_KEIN)
        t = QLabel("" if g.get("ohne_titel") else g["name"].upper())     # Kontext-Reiter wie in der Vorlage: Gruppen ohne Unterschrift
        t.setVisible(not self.kompakt)
        t.setAlignment(Qt.AlignCenter)
        hinweis_stil(t, zusatz="font-size: " f"{SCHRIFT_BANDGRUPPE_TITEL}" "pt; letter-spacing: 1px;")
        fuss.addStretch(1)
        fuss.addWidget(t)
        if g.get("pfeil"):
            p = QToolButton()
            p.setText("↘")
            p.setAutoRaise(True)
            p.setFixedSize(*GROESSE_GRUPPEN_STARTER)
            p.setStyleSheet("font-size: " f"{SCHRIFT_BANDGRUPPE_TITEL}" "pt;")
            p.setToolTip(g["name"] + " — Einstellungen")
            p.clicked.connect(lambda _=False, a=g["pfeil"]: self.b.tun(a))
            p.setEnabled(self.b.hat(g["pfeil"]))
            if not self.b.hat(g["pfeil"]):
                self.fehlend.append(g["pfeil"])
            fuss.addWidget(p)
        fuss.addStretch(1)
        v.addLayout(fuss)
        return rahmen

    def _knoepfe_geordnet(self, g: dict, inhalt: QHBoxLayout):
        """Knöpfe in der Reihenfolge der Liste: große stehen allein, aufeinanderfolgende kleine bilden eine Spalte aus zwei Zeilen."""
        lauf: list[dict] = []
        felder: list = []                                     # aufeinanderfolgende Eingabefelder stehen übereinander (wie die Kleinknöpfe)

        def feldspalte():
            if felder:
                host = QWidget()
                v = QVBoxLayout(host)
                v.setContentsMargins(*RAND_KEIN)
                v.setSpacing(ABSTAND_DICHT)
                for w in felder:
                    v.addWidget(w)
                v.addStretch(1)
                inhalt.addWidget(host, 0, Qt.AlignTop)
                felder.clear()

        def spalte(felder_behalten=False):
            if not felder_behalten:
                feldspalte()
            for i in range(0, len(lauf), 2):                    # je Spalte zwei Zeilen
                host = QWidget()
                v = QVBoxLayout(host)
                v.setContentsMargins(*RAND_KEIN)
                v.setSpacing(ABSTAND_DICHT)
                for e in lauf[i:i + 2]:
                    v.addWidget(self._knopf(e, False))
                v.addStretch(1)
                inhalt.addWidget(host, 0, Qt.AlignTop)
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

    def _knoepfe_schrift(self, g: dict, inhalt: QHBoxLayout):
        """Wie in der Vorlage: oben Schriftname und -größe, daneben die Größen-/Löschknöpfe; darunter die Zeichenformate."""
        from lunivo_writer.oberflaeche.bauteile.live_vorschau import VorschauCombo, VorschauFontCombo
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
        v = QVBoxLayout()
        v.setSpacing(ABSTAND_ENG)
        v.setContentsMargins(*RAND_KEIN)
        for i, zeile in enumerate(zeilen):
            h = QHBoxLayout()
            h.setSpacing(ABSTAND_DICHT)
            h.setContentsMargins(*RAND_KEIN)
            if i == 0:
                h.addWidget(font)
                h.addWidget(groesse)
                h.addSpacing(3)
            for e in zeile:
                h.addWidget(self._knopf(e, False))
            h.addStretch(1)
            v.addLayout(h)
        v.addStretch(1)
        inhalt.addLayout(v)

    def _knoepfe_tt_schrift(self, g: dict, inhalt: QHBoxLayout, art: str = "tt"):
        """Texttools: Schriftname und -größe oben (wirken auf das markierte WordArt/Textfeld), darunter die Zeichenformate — wie bei Start.
        ``art="tab"`` (Tabellentools): dieselben Felder, aber sie wirken auf den Text der Schreibmarke / der markierten Zellen (Felder ``tab_font``, ``tab_groesse``)."""
        font = schrift_feld(Schriftauswahl())
        groesse = groesse_feld()
        if art == "tab":
            def pt_setzen(*_):
                self.b.tabGroesse(groesse.currentText())
            font.activated.connect(lambda _i: self.b.tabSchriftart(font.currentFont().family()))
            groesse.activated.connect(pt_setzen)
            groesse.lineEdit().editingFinished.connect(pt_setzen)
        else:
            font.activated.connect(lambda _i: self.b.ttSchriftart(font.currentText()))
            groesse.activated.connect(lambda _i: self.b.ttGroesse(groesse.currentText()))
            groesse.lineEdit().returnPressed.connect(lambda: self.b.ttGroesse(groesse.currentText()))
        self.felder.update({art + "_font": font, art + "_groesse": groesse})
        zeilen, aktuell = [], []
        for e in g["knoepfe"]:
            if e.get("zeilenumbruch"):
                zeilen.append(aktuell)
                aktuell = []
            else:
                aktuell.append(e)
        zeilen.append(aktuell)
        v = QVBoxLayout()
        v.setSpacing(ABSTAND_ENG)
        v.setContentsMargins(*RAND_KEIN)
        for i, zeile in enumerate(zeilen):
            h = QHBoxLayout()
            h.setSpacing(ABSTAND_DICHT)
            h.setContentsMargins(*RAND_KEIN)
            if i == 0:
                h.addWidget(font)
                h.addWidget(groesse)
                h.addSpacing(3)
            for e in zeile:
                h.addWidget(self._knopf(e, False))
            h.addStretch(1)
            v.addLayout(h)
        v.addStretch(1)
        inhalt.addLayout(v)

    def _knoepfe_galerie(self, g: dict, inhalt: QHBoxLayout):
        """Eine Galerie wie in der Vorlage: drei Kacheln zum Anklicken und daneben ein Pfeil mit der ganzen Auswahl (Befehl ``galerie_<name>``)."""
        bau = GALERIEN.get(g["galerie"])                          # erst die Bausteine der Oberfläche, sonst ``galerie_<name>`` des Befehlsbausteins
        spec = (lambda: bau(self.b)) if bau else getattr(self.b, "galerie_" + g["galerie"], None)
        if spec is None:
            self.fehlend.append("galerie_" + g["galerie"])
            return
        spec = spec()
        spec = dict(spec, kacheln=spec["kacheln"][:int(g.get("kacheln") or len(spec["kacheln"]))])   # ``"kacheln": N``: nur N Kacheln im Band, alle Einträge bleiben im Pfeil-Menü
        rahmen = QFrame()
        rahmen.setFrameShape(QFrame.StyledPanel)
        h = QHBoxLayout(rahmen)
        h.setContentsMargins(*RAND_BANDGALERIE)
        h.setSpacing(ABSTAND_ENG)
        zeilen = int(g.get("zeilen") or 1)                       # ``"zeilen": 2``: Kacheln in mehreren Reihen (Linien und Pfeile)
        spalten = -(-len(spec["kacheln"]) // zeilen)
        raster = kachel_gitter((), spalten, abstand=ABSTAND_ENG) if zeilen > 1 else None
        if raster is not None:
            h.addLayout(raster)
        for nr, (tipp, pm, tun) in enumerate(spec["kacheln"]):
            k = QToolButton()
            k.setAutoRaise(True)
            k.setIcon(QIcon(pm))
            k.setIconSize(pm.size())
            k.setFixedSize(pm.width() + 8, pm.height() + 8)
            k.setToolTip(tipp); k.setCursor(Qt.PointingHandCursor)                  # klickbare Kachel: Hand
            k.clicked.connect(lambda _=False, f=tun: (f(), self.aktualisieren()))
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

    def _knoepfe_raender(self, g: dict, inhalt: QHBoxLayout):
        """Der Rand-Knopf und daneben wie in der Vorlage die vier Maßfelder Oben/Unten/Links/Rechts (in der gewählten Maßeinheit)."""
        from lunivo_writer.oberflaeche.dialoge.dokument_dialoge import _MassSpin
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

    def _knoepfe_masse(self, g: dict, inhalt: QHBoxLayout):
        """Höhe und Breite des markierten Bildes (Zeichentools); „Seitenverhältnis sperren“ hält das Verhältnis beim Ändern.
        ``"sperre": "bild"`` (Bildtools): Breite oben, Höhe unten; rechts daneben stehen die ersten beiden Knöpfe der Gruppe
        (Sperre = Schalter ``bildSeitenverhaeltnis``, dann „Größe zurücksetzen“).
        ``"befehl"`` nennt den Aufruf (Vorgabe ``zeichenMasse(breite_mm, hoehe_mm)``); ``"verhaeltnis": False`` lässt Sperre und Verhältnis weg
        und meldet nur das geänderte Maß (Tabellentools: ``tabelleMasse``)."""
        from lunivo_writer.oberflaeche.dialoge.dokument_dialoge import _MassSpin
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
            sperre = QCheckBox("Seitenverhältnis sperren"); sperre.setChecked(True)
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

    def _knoepfe(self, g: dict, inhalt: QHBoxLayout):
        art = g.get("felder")
        if art in self._FELDER_BAUER:
            return getattr(self, self._FELDER_BAUER[art])(g, inhalt)
        if art == "tab_zeile":
            return self._knoepfe_tt_schrift(g, inhalt, "tab")
        if g.get("galerie"):
            return self._knoepfe_galerie(g, inhalt)
        if g.get("reihenfolge"):
            return self._knoepfe_geordnet(g, inhalt)
        if art:
            self._knoepfe_formatfelder(inhalt)
        self._knoepfe_gitter(g["knoepfe"], inhalt)

    def _knoepfe_formatfelder(self, inhalt: QHBoxLayout) -> None:
        """Formatvorlage, Schriftart und Größe als Spalte vor den Knöpfen."""
        spalte = QVBoxLayout()
        spalte.setSpacing(ABSTAND_ENG)
        from lunivo_writer.oberflaeche.bauteile.live_vorschau import VorschauCombo, VorschauFontCombo
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
        for w in (stil, font, groesse):
            spalte.addWidget(w)
        inhalt.addLayout(spalte)
        self.felder.update(stil=stil, font=font, groesse=groesse)

    def _gitter_fuellen(self, gitter, explizit: bool, zeilen: list, kleine: list) -> None:
        """Die kleinen Knöpfe ins Gitter: explizit zeilenweise, sonst spaltenweise in zwei Zeilen."""
        if explizit:
            for r, zeile in enumerate(zeilen):
                for c, e in enumerate(zeile):
                    gitter.addWidget(self._knopf(e, False), r, c)
        else:
            for i, e in enumerate(kleine):
                gitter.addWidget(self._knopf(e, False), i % 2, i // 2)

    def _knoepfe_gitter(self, eintraege: list, inhalt: QHBoxLayout) -> None:
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
            inhalt.addWidget(host, 0, Qt.AlignTop)
