"""Die Seite „Neu“: leeres Dokument direkt starten oder Standard- und eigene Vorlagen getrennt durchsuchen.

    g = VorlagenGalerie(settings, kann_speichern=True)
    g.gewaehlt.connect(lambda art, wert: ...)      # art: "leer" | "geruest" (wert = Muster) | "datei" (wert = Pfad)
    g.als_vorlage.connect(...)                     # „Dieses Dokument als Vorlage behalten …“

Die Vorschauen entstehen nach und nach (ein Blatt je Takt), damit die Seite sofort da ist; fertige bleiben im Speicher.
"""
from __future__ import annotations

from vcl.qt.widgets.bausteine.farben.darstellung import rolle as _rolle

from vcl.qt.widgets.bausteine.skalierung.daten import text as _t

from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte

from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte

import os

from PySide6.QtCore import QSize, Qt, QTimer, QUrl, Signal
from PySide6.QtGui import QColor, QDesktopServices, QIcon, QImage, QPainter, QPixmap
from vcl.qt.widgets.bausteine.interaktion.felder.ueberlauf_leiste import UeberlaufLeiste
from PySide6.QtWidgets import QFrame, QLabel, QLineEdit, QPushButton, QScrollArea, QToolButton, QWidget
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil, trennlinie
from vcl.qt.widgets.dialoge.dokument.eingabe_fenster import EingabeFenster
from vcl.qt.widgets.bausteine.interaktion.felder.karten_raster import kachel_gitter, kacheln_legen
from vcl.qt.widgets.dialoge.dokument.speichern_fenster import Dateifenster

from writer.anbindung import vorlagen as _vorlagen
from writer.anbindung.vorlagenordner import vorlagen_ordner_pfad
from writer.funktionen import ansicht as AN
from vcl.qt.widgets.bausteine.symbole.bauteile import symbole

from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_GROSS, ABSTAND_PAAR, BREITE_GALERIE_HINWEIS_MIN, BREITE_VORLAGENSUCHE, GROESSE_VORLAGE_KACHEL, HOEHE_FELD, HOEHE_KNOPF, ICON_GROSS, ICON_NORMAL, ICON_VORLAGE_PLATZHALTER, RAND_VORLAGENGALERIE, RAND_VORLAGEN_FUSS

from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.abstaende.mass import RADIUS_ZEICHNUNG_KACHEL, VORLAGENKACHEL_ZUGABE_BREIT, VORLAGENKACHEL_ZUGABE_HOCH
from vcl.qt.widgets.bausteine.farben.farben import BILDCHEN_FLAECHE_HELL as _FLAECHE_HELL, SCHATTEN_KACHEL # Vordergrund der Stapel-Kachel: bewusst fest
KACHEL = QSize(*GROESSE_VORLAGE_KACHEL)
_VORSCHAU: dict[tuple, QPixmap] = {}                     # (Art, Schlüssel, Änderungszeit) → Bild, solange das Programm läuft


def _blatt_bild(ausgabe: int) -> QPixmap:
    """Erste Seite der Ausgabe ``ausgabe`` des Frameworks, auf Kachelbreite verkleinert (Layout und Rendering im Kern; Qt rastert nur)."""
    from vcl.qt.drucken.drucken import Ausgabe
    img = Ausgabe(None, nummer=ausgabe).bild(1, 0.8)
    return QPixmap.fromImage(img.scaled(KACHEL, Qt.KeepAspectRatio, Qt.SmoothTransformation))


def _geruest_bild(muster: dict, benutzer: dict) -> QPixmap:
    from PySide6.QtCore import QDate, QLocale
    return _blatt_bild(AN.ausgabe_aus_geruest(muster["zeilen"], benutzer, QLocale("de_DE").toString(QDate.currentDate(), _t("vorlagen.d_mmmm_yyyy"))))


def _datei_bild(pfad: str) -> QPixmap:
    return _blatt_bild(AN.ausgabe_aus_datei(pfad))                                  # Kern: Laden, Layout, Rendering; Qt zeigt nur das Bild


class _Kachel(QToolButton):
    """Ein Blatt mit Name darunter; eine Rubrik zeigt zusätzlich ein Ordnerzeichen mit der Zahl ihrer Vorlagen."""

    def __init__(self, name: str, art: str, wert, schluessel: tuple, anzahl: int = 0):
        super().__init__()
        self.name, self.art, self.wert, self.schluessel, self.anzahl = name, art, wert, schluessel, anzahl
        self.gruppe = "geruest"
        self.setText(name); self.setToolTip(name)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon); self.setAutoRaise(True); self.setCursor(Qt.PointingHandCursor)
        self.setIconSize(KACHEL); self.setFixedSize(KACHEL.width() + VORLAGENKACHEL_ZUGABE_BREIT, KACHEL.height() + VORLAGENKACHEL_ZUGABE_HOCH)
        self.setIcon(QIcon(self._platzhalter(art == "leer")))

    def _platzhalter(self, symbol: bool = False) -> QPixmap:
        pm = QPixmap(KACHEL); pm.fill(QColor(Farbe.PAPIER))
        if symbol:
            p = QPainter(pm); ic = symbole.icon("neu", ICON_VORLAGE_PLATZHALTER).pixmap(ICON_VORLAGE_PLATZHALTER, ICON_VORLAGE_PLATZHALTER)
            p.setOpacity(0.35); p.drawPixmap((KACHEL.width() - 56) // 2, (KACHEL.height() - 56) // 2, ic); p.end()
        return pm

    def bild_setzen(self, pm: QPixmap) -> None:
        if self.art == "rubrik":
            pm = self._mit_ordnerzeichen(pm)
        self.setIcon(QIcon(pm))

    def _mit_ordnerzeichen(self, pm: QPixmap) -> QPixmap:
        """Eine Rubrik: das erste Blatt, dahinter angedeutet weitere, vorn ein Schild mit der Zahl."""
        out = QPixmap(KACHEL); out.fill(Qt.transparent)
        p = QPainter(out); p.setRenderHint(QPainter.Antialiasing)
        w, h = pm.width(), pm.height()
        vorn = pm.scaled(w - 16, h - 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        for dx, dy in ((16, 0), (8, 8)):                             # zwei Blätter dahinter, nur an der Kante zu sehen
            p.setPen(QColor(Farbe.GRAU_HELL)); p.setBrush(QColor(_FLAECHE_HELL)); p.drawRect(dx, dy, vorn.width() - 1, vorn.height() - 1)
        p.drawPixmap(0, 16, vorn)
        p.setBrush(QColor(*SCHATTEN_KACHEL)); p.setPen(Qt.NoPen); p.drawRoundedRect(6, KACHEL.height() - 34, 58, 26, RADIUS_ZEICHNUNG_KACHEL, RADIUS_ZEICHNUNG_KACHEL)
        p.setPen(QColor(Farbe.PAPIER)); p.drawText(6, KACHEL.height() - 34, 58, 26, Qt.AlignCenter, f"▣ {self.anzahl}")
        p.end()
        return out


class VorlagenGalerie(QWidget):
    gewaehlt = Signal(str, object)
    als_vorlage = Signal(str)                                 # Zielordner („“ = Vorlagenordner selbst)

    def __init__(self, settings, kann_speichern: bool, benutzer: dict | None = None, parent=None):
        super().__init__(parent)
        self.settings, self._benutzer = settings, benutzer or {}
        self._reiter, self._rubrik = "geruest", None
        self._offen: list[_Kachel] = []
        v = _spalte("fenster", self)
        kopf = _reihe("inhalt")
        self.zurueck = knopf("standard", _t("vorlagen.neu"), symbol="arrow-left", ohne_rand=True, hand=True)
        self.zurueck.clicked.connect(lambda: self.rubrik_oeffnen(None)); kopf.addWidget(self.zurueck)
        self.titel = _rolle(QLabel(_t("vorlagen.neu")), "seitentitel")
        kopf.addWidget(self.titel); kopf.addStretch(1)
        self.leer_knopf = knopf("standard", _t("vorlagen.neues_leeres_dokument"))
        self.leer_knopf.setIcon(symbole.icon("file-plus", ICON_GROSS)); self.leer_knopf.setIconSize(QSize(ICON_GROSS, ICON_GROSS))
        self.leer_knopf.setObjectName("optFertig"); self.leer_knopf.setCursor(Qt.PointingHandCursor)
        self.leer_knopf.clicked.connect(lambda: self.gewaehlt.emit("leer", None))
        self.neue_rubrik = knopf("standard", _t("vorlagen.neue_rubrik"))
        self.neue_rubrik.clicked.connect(self._rubrik_anlegen)
        kopf.addWidget(self.neue_rubrik)
        v.addLayout(kopf)
        aktion = _reihe("standard"); aktion.addWidget(self.leer_knopf); aktion.addStretch(1)       # Hauptaktion: direkt unter der Überschrift
        v.addLayout(aktion)
        self.reiter_w = UeberlaufLeiste(); self.reiter_w.setObjectName("bandReiter")            # dieselbe Gestalt wie die Register des Bandes
        self.reiter_w.setDrawBase(False); self.reiter_w.setExpanding(False); self.reiter_w.setCursor(Qt.PointingHandCursor)
        self.reiter_w.setFocusPolicy(Qt.StrongFocus); self.reiter_w.setAccessibleName(_t("vorlagen.vorlagenbereiche"))
        self._schluessel = ("geruest", "eigene")
        for text in (_t("vorlagen.standardvorlagen"), _t("vorlagen.meine_vorlagen")):
            self.reiter_w.addTab(text)
        self.reiter_w.currentChanged.connect(lambda i: self._reiter_setzen(self._schluessel[i]))
        v.addWidget(self.reiter_w, 0, Qt.AlignLeft)
        linie = trennlinie(tief=True); v.addWidget(linie)
        self.suche = zeilenfeld("frei", platzhalter=_t("vorlagen.vorlage_suchen")); self.suche.setClearButtonEnabled(True)
        self.suche.setFixedWidth(BREITE_VORLAGENSUCHE); self.suche.setMinimumHeight(HOEHE_KNOPF); self.suche.textChanged.connect(self._anordnen)
        v.addWidget(self.suche)
        self.flaeche = QScrollArea(); self.flaeche.setWidgetResizable(True); self.flaeche.setFrameShape(QFrame.NoFrame)
        self.raster_w = QWidget(); self.raster = kachel_gitter((), 1, eltern=self.raster_w, rand=None, abstand=ABSTAND_PAAR, oben_links=True)
        self.flaeche.setWidget(self.raster_w); v.addWidget(self.flaeche, 1)
        self.leer = QLabel(); self.leer.setWordWrap(True); hinweis_stil(self.leer); v.addWidget(self.leer)

        fuss = _reihe("fuss")
        hin = QLabel(_t("vorlagen.geoeffnet_wird_immer_eine_abschrift_die"))
        hinweis_stil(hin); hin.setWordWrap(True); hin.setMinimumWidth(BREITE_GALERIE_HINWEIS_MIN); fuss.addWidget(hin, 1)   # darf umbrechen, sonst wird das Fenster breiter als der Schirm
        self.speichern = knopf("standard", _t("vorlagen.dieses_dokument_als_vorlage_behalten"), aktiv=kann_speichern)
        self.speichern.clicked.connect(lambda: self.als_vorlage.emit(self._ziel()))
        waehlen = knopf("standard", _t("vorlagen.vorlagenordner_waehlen"), aktion=self._ordner_waehlen)
        oeffnen = knopf("standard", _t("vorlagen.vorlagenordner_oeffnen"), aktion=self._ordner_oeffnen)
        for k in (self.speichern, waehlen, oeffnen):
            k.setMinimumHeight(HOEHE_FELD); fuss.addWidget(k)
        self.vorlagen_aktionen = (self.speichern, waehlen, oeffnen)
        v.addLayout(fuss)

        self._kacheln: list[_Kachel] = []
        self._timer = QTimer(self); self._timer.setInterval(15); self._timer.timeout.connect(self._naechstes_bild)
        self._daten_lesen()
        self._bauen()
        self._reiter_setzen("geruest")

    # ---- Daten: Rubriken aus Gerüsten und Unterordnern ---------------------------------------------------------------------
    def _daten_lesen(self) -> None:
        self.ordner = vorlagen_ordner_pfad(self.settings)
        self.rubriken: dict[str, dict] = {}
        for m in _vorlagen.muster():
            r = self.rubriken.setdefault(m.get("rubrik") or m["name"], {"geruest": [], "dateien": [], "pfad": None})
            r["geruest"].append(m)
        unter, self.lose = _vorlagen.rubriken(self.ordner)
        for name, dateien in unter.items():
            gleich = next((n for n in self.rubriken if n.lower() == name.lower()), name)
            r = self.rubriken.setdefault(gleich, {"geruest": [], "dateien": [], "pfad": None})
            r["dateien"] += dateien; r["pfad"] = os.path.join(self.ordner, name)

    def _ziel(self) -> str:
        """Wohin „Dieses Dokument als Vorlage behalten“ ablegt: in die geöffnete Rubrik, sonst in den Vorlagenordner."""
        if self._rubrik is None:
            return ""
        r = self.rubriken.get(self._rubrik, {})
        return r.get("pfad") or os.path.join(self.ordner, self._rubrik)

    def _stempel(self, p: str) -> float:
        try:
            return os.path.getmtime(p)
        except OSError:
            return 0

    def _datei_kachel(self, p: str, gruppe: str = "eigene") -> _Kachel:
        k = _Kachel(os.path.splitext(os.path.basename(p))[0], "datei", p, ("datei", p, self._stempel(p)))
        k.gruppe = gruppe; k.clicked.connect(lambda _=False, p=p: self.gewaehlt.emit("datei", p))
        return k

    def _geruest_kachel(self, m: dict) -> _Kachel:
        k = _Kachel(m["name"], "geruest", m, ("geruest", m["name"]))
        k.clicked.connect(lambda _=False, m=m: self.gewaehlt.emit("geruest", m))
        return k

    def _bauen(self) -> None:
        for k in self._kacheln:
            k.deleteLater()
        self._kacheln = []
        self.suche_alle: list[_Kachel] = []                 # alle Vorlagen flach (für die Suche)
        n_g = n_e = 0
        for name, r in self.rubriken.items():
            n = len(r["geruest"]) + len(r["dateien"])
            k = _Kachel(name, "rubrik", name, ("rubrik", name, n, tuple(self._stempel(p) for p in r["dateien"])), n)
            k.gruppe = "gemischt" if r["geruest"] and r["dateien"] else ("geruest" if r["geruest"] else "eigene")
            k.clicked.connect(lambda _=False, n=name: self.rubrik_oeffnen(n))
            k.setToolTip(_t("vorlagen.0_1_vorlage_2").format(name, n, 'n' if n != 1 else ''))
            self._kacheln.append(k)
            n_g += bool(r["geruest"]); n_e += bool(r["dateien"])
            r["kacheln"] = [self._geruest_kachel(m) for m in r["geruest"]] + [self._datei_kachel(p) for p in r["dateien"]]
            self.suche_alle += r["kacheln"]
        for p in self.lose:
            k = self._datei_kachel(p); self._kacheln.append(k); self.suche_alle.append(k); n_e += 1
        for i, text in enumerate((_t("vorlagen.standardvorlagen_0").format(n_g), _t("vorlagen.meine_vorlagen_0").format(n_e))):
            self.reiter_w.setTabText(i, text)
        self._offen = self._kacheln + self.suche_alle
        self._timer.start()

    def _naechstes_bild(self) -> None:
        while self._offen:
            k = self._offen.pop(0)
            try:
                if k.art == "rubrik":
                    r = self.rubriken.get(k.wert); erste = r["kacheln"][0] if r and r.get("kacheln") else None
                    if erste is None:
                        continue
                    pm = _VORSCHAU.get(erste.schluessel)
                    if pm is None:
                        pm = self._bild_fuer(erste); _VORSCHAU[erste.schluessel] = pm
                    k.bild_setzen(pm)
                    continue
                if k.schluessel not in _VORSCHAU:
                    _VORSCHAU[k.schluessel] = self._bild_fuer(k)
                    k.bild_setzen(_VORSCHAU[k.schluessel])
                    return
                k.bild_setzen(_VORSCHAU[k.schluessel])
            except Exception:                                     # eine Datei, die sich nicht lesen lässt, bleibt ein leeres Blatt
                continue
        self._timer.stop()

    def _bild_fuer(self, k: _Kachel) -> QPixmap:
        return _geruest_bild(k.wert, self._benutzer) if k.art == "geruest" else _datei_bild(k.wert)

    # ---- Anzeige ---------------------------------------------------------------------------------------------------
    def rubrik_oeffnen(self, name: str | None) -> None:
        self._rubrik = name
        self.suche.clear()
        self._anordnen()
        if name is not None:
            self._offen = [k for k in self.rubriken.get(name, {}).get("kacheln", []) if k.schluessel not in _VORSCHAU]
            self._timer.start()

    def _reiter_setzen(self, schl: str) -> None:
        self._reiter = schl
        eigene = schl == "eigene"
        self.neue_rubrik.setVisible(eigene)
        i = self._schluessel.index(schl)
        if self.reiter_w.currentIndex() != i:
            self.reiter_w.setCurrentIndex(i)
            return                                                    # currentChanged ruft uns noch einmal auf
        self._anordnen()

    def _sichtbar(self) -> list[_Kachel]:
        text = self.suche.text().strip().lower()
        if self._rubrik is not None:
            return [k for k in self.rubriken.get(self._rubrik, {}).get("kacheln", []) if text in k.name.lower()]
        wahl = {"geruest": ("geruest", "gemischt"), "eigene": ("eigene", "gemischt")}[self._reiter]
        if text:                                            # die Reiter sind beim Suchen ausgeblendet: die Suche gilt für alle Vorlagen, auch in Rubriken
            return [k for k in self.suche_alle if text in k.name.lower()]
        return [k for k in self._kacheln if k.gruppe in wahl]

    def _anordnen(self, *_a) -> None:
        sicht = self._sichtbar()
        while self.raster.count():
            self.raster.takeAt(0)
        alle = self._kacheln + self.suche_alle
        for k in alle:
            k.setVisible(k in sicht)
        spalten = max(1, (max(self.width(), 600) - 100) // (KACHEL.width() + 30))
        kacheln_legen(self.raster, sicht, spalten)
        in_rubrik = self._rubrik is not None
        self.zurueck.setVisible(in_rubrik); self.reiter_w.setVisible(not in_rubrik and not self.suche.text().strip())
        self.neue_rubrik.setVisible(not in_rubrik and self._reiter == "eigene")
        self.titel.setText(self._rubrik if in_rubrik else _t("vorlagen.neu"))
        if sicht:
            self.leer.clear()
        elif in_rubrik:
            self.leer.setText(_t("vorlagen.in_0_liegt_noch_nichts_lege_dokumente_in").format(self._rubrik, self._ziel()))
        elif self._reiter == "eigene" and not self.suche.text().strip():
            self.leer.setText(_t("vorlagen.der_ordner_0_enthaelt_noch_keine_vorlage").format(self.ordner))
        else:
            self.leer.setText(_t("vorlagen.nichts_gefunden"))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._anordnen()

    # ---- Ordner ----------------------------------------------------------------------------------------------------
    def _rubrik_anlegen(self) -> None:
        name, ok = EingabeFenster.getText(self, _t("vorlagen.neue_rubrik_2"), _t("vorlagen.name_der_rubrik_zum_beispiel_lebenslauf"))
        name = name.strip().replace("/", "-").replace("\\", "-") if ok else ""
        if not name or name.startswith("."):
            return
        os.makedirs(os.path.join(self.ordner, name), exist_ok=True)
        self.neu_lesen(); self.rubrik_oeffnen(next((n for n in self.rubriken if n.lower() == name.lower()), name))

    def _ordner_waehlen(self) -> None:
        p = Dateifenster.getExistingDirectory(self, _t("vorlagen.vorlagenordner"), vorlagen_ordner_pfad(self.settings))
        if p:
            self.settings.set("vorlagen/ordner", p); self.neu_lesen()

    def _ordner_oeffnen(self) -> None:
        o = self._ziel() or vorlagen_ordner_pfad(self.settings)
        os.makedirs(o, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(o))

    def neu_lesen(self) -> None:
        """Der Ordner wird bei jedem Öffnen der Seite neu gelesen."""
        gemerkt = self._rubrik
        self._daten_lesen(); self._bauen()
        self._rubrik = gemerkt if gemerkt in self.rubriken else None
        self._anordnen()
