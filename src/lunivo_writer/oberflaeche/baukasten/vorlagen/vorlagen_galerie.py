"""Die Seite „Neu“: leeres Dokument direkt starten oder Standard- und eigene Vorlagen getrennt durchsuchen.

    g = VorlagenGalerie(settings, kann_speichern=True)
    g.gewaehlt.connect(lambda art, wert: ...)      # art: "leer" | "geruest" (wert = Muster) | "datei" (wert = Pfad)
    g.als_vorlage.connect(...)                     # „Dieses Dokument als Vorlage behalten …“

Die Vorschauen entstehen nach und nach (ein Blatt je Takt), damit die Seite sofort da ist; fertige bleiben im Speicher.
"""
from __future__ import annotations

import os

from PySide6.QtCore import QSize, Qt, QTimer, QUrl, Signal
from PySide6.QtGui import QColor, QDesktopServices, QIcon, QImage, QPainter, QPixmap
from lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste import UeberlaufLeiste
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QToolButton, QVBoxLayout,
                               QWidget)
from lunivo_writer.oberflaeche.baukasten.basis.texte import hinweis_stil, trennlinie
from lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster import EingabeFenster
from lunivo_writer.oberflaeche.baukasten.felder.karten_raster import kachel_gitter, kacheln_legen
from lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster import Dateifenster

from lunivo_writer.editor.dokument import vorlagen
from lunivo_writer.oberflaeche.bauteile import symbole

from lunivo_writer.kern.farben import Farbe
from lunivo_writer.oberflaeche.baukasten.basis.mass import (
    ABSTAND_GROSS,
    ABSTAND_PAAR,
    BREITE_GALERIE_HINWEIS_MIN,
    BREITE_VORLAGENSUCHE,
    GROESSE_VORLAGE_KACHEL,
    HOEHE_FELD,
    HOEHE_KNOPF,
    ICON_GROSS,
    ICON_NORMAL,
    ICON_VORLAGE_PLATZHALTER,
    RAND_VORLAGENGALERIE,
    RAND_VORLAGEN_FUSS,
)

_FLAECHE_HELL = "#f1f3f5"   # Vordergrund der Stapel-Kachel: bewusst fest (Gruppe C)
KACHEL = QSize(*GROESSE_VORLAGE_KACHEL)
_VORSCHAU: dict[tuple, QPixmap] = {}                     # (Art, Schlüssel, Änderungszeit) → Bild, solange das Programm läuft


def _blatt_bild(doc, page) -> QPixmap:
    """Erste Seite eines Dokuments, auf Kachelbreite verkleinert."""
    from lunivo_writer.adapter.qt.dokument import document_from_qt
    from lunivo_writer.adapter.qt.seitenbild import seiten_aus_modell
    img = seiten_aus_modell(document_from_qt(doc, page), 0.8)[0]                    # Modell → Seitenumbruch ohne Qt → Backend
    return QPixmap.fromImage(img.scaled(KACHEL, Qt.KeepAspectRatio, Qt.SmoothTransformation))


def _geruest_bild(muster: dict, benutzer: dict) -> QPixmap:
    from PySide6.QtCore import QDate, QLocale
    from PySide6.QtWidgets import QTextEdit
    from lunivo_writer.modelle.seite import PageSettings
    ed = QTextEdit()
    vorlagen.aufbauen(ed, muster["zeilen"], benutzer, QLocale("de_DE").toString(QDate.currentDate(), "d. MMMM yyyy"))
    from PySide6.QtGui import QBrush, QTextCharFormat, QTextCursor
    c = QTextCursor(ed.document()); c.select(QTextCursor.Document)
    f = QTextCharFormat(); f.setForeground(QBrush(QColor(Farbe.SCHWARZ))); f.setBackground(QBrush(Qt.NoBrush))
    c.mergeCharFormat(f)                                      # in der Vorschau sind die Lücken schlichter Text: lesbar, ohne Farbe und Gelb
    return _blatt_bild(ed.document(), PageSettings())


def _datei_bild(pfad: str) -> QPixmap:
    from lunivo_writer.dienste import datei_dienst as formats
    g = formats.load(pfad)
    return _blatt_bild(g.doc, g.page)


class _Kachel(QToolButton):
    """Ein Blatt mit Name darunter; eine Rubrik zeigt zusätzlich ein Ordnerzeichen mit der Zahl ihrer Vorlagen."""

    def __init__(self, name: str, art: str, wert, schluessel: tuple, anzahl: int = 0):
        super().__init__()
        self.name, self.art, self.wert, self.schluessel, self.anzahl = name, art, wert, schluessel, anzahl
        self.gruppe = "geruest"
        self.setText(name); self.setToolTip(name)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon); self.setAutoRaise(True); self.setCursor(Qt.PointingHandCursor)
        self.setIconSize(KACHEL); self.setFixedSize(KACHEL.width() + 12, KACHEL.height() + 44)
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
        p.setBrush(QColor(0, 0, 0, 190)); p.setPen(Qt.NoPen); p.drawRoundedRect(6, KACHEL.height() - 34, 58, 26, 6, 6)
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
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_VORLAGENGALERIE); v.setSpacing(ABSTAND_GROSS)
        kopf = QHBoxLayout(); kopf.setSpacing(ABSTAND_GROSS)
        self.zurueck = QPushButton("Neu"); self.zurueck.setIcon(symbole.icon("arrow-left", ICON_NORMAL)); self.zurueck.setFlat(True); self.zurueck.setCursor(Qt.PointingHandCursor)
        self.zurueck.clicked.connect(lambda: self.rubrik_oeffnen(None)); kopf.addWidget(self.zurueck)
        self.titel = QLabel("Neu"); f = self.titel.font(); f.setPointSizeF(f.pointSizeF() + 8); f.setBold(True); self.titel.setFont(f)
        kopf.addWidget(self.titel); kopf.addStretch(1)
        self.leer_knopf = QPushButton("Neues leeres Dokument")
        self.leer_knopf.setIcon(symbole.icon("file-plus", ICON_GROSS)); self.leer_knopf.setIconSize(QSize(ICON_GROSS, ICON_GROSS))
        self.leer_knopf.setMinimumHeight(HOEHE_KNOPF)
        self.leer_knopf.clicked.connect(lambda: self.gewaehlt.emit("leer", None))
        kopf.addWidget(self.leer_knopf)
        self.neue_rubrik = QPushButton("Neue Rubrik …")
        self.neue_rubrik.clicked.connect(self._rubrik_anlegen)
        kopf.addWidget(self.neue_rubrik)
        v.addLayout(kopf)
        self.reiter_w = UeberlaufLeiste(); self.reiter_w.setObjectName("bandReiter")            # dieselbe Gestalt wie die Register des Bandes
        self.reiter_w.setDrawBase(False); self.reiter_w.setExpanding(False); self.reiter_w.setCursor(Qt.PointingHandCursor)
        self.reiter_w.setFocusPolicy(Qt.StrongFocus); self.reiter_w.setAccessibleName("Vorlagenbereiche")
        self._schluessel = ("geruest", "eigene")
        for text in ("Standardvorlagen", "Meine Vorlagen"):
            self.reiter_w.addTab(text)
        self.reiter_w.currentChanged.connect(lambda i: self._reiter_setzen(self._schluessel[i]))
        v.addWidget(self.reiter_w, 0, Qt.AlignLeft)
        linie = trennlinie(tief=True); v.addWidget(linie)
        self.suche = QLineEdit(); self.suche.setPlaceholderText("Vorlage suchen"); self.suche.setClearButtonEnabled(True)
        self.suche.setFixedWidth(BREITE_VORLAGENSUCHE); self.suche.setMinimumHeight(HOEHE_KNOPF); self.suche.textChanged.connect(self._anordnen)
        v.addWidget(self.suche)
        self.flaeche = QScrollArea(); self.flaeche.setWidgetResizable(True); self.flaeche.setFrameShape(QFrame.NoFrame)
        self.raster_w = QWidget(); self.raster = kachel_gitter((), 1, eltern=self.raster_w, rand=None, abstand=ABSTAND_PAAR, oben_links=True)
        self.flaeche.setWidget(self.raster_w); v.addWidget(self.flaeche, 1)
        self.leer = QLabel(); self.leer.setWordWrap(True); hinweis_stil(self.leer); v.addWidget(self.leer)

        fuss = QHBoxLayout(); fuss.setContentsMargins(*RAND_VORLAGEN_FUSS)
        hin = QLabel("Geöffnet wird immer eine Abschrift. Die Vorlage selbst bleibt, wie sie ist — auch nach dem dritten Brief.")
        hinweis_stil(hin); hin.setWordWrap(True); hin.setMinimumWidth(BREITE_GALERIE_HINWEIS_MIN); fuss.addWidget(hin, 1)   # darf umbrechen, sonst wird das Fenster breiter als der Schirm
        self.speichern = QPushButton("Dieses Dokument als Vorlage behalten …"); self.speichern.setEnabled(kann_speichern)
        self.speichern.clicked.connect(lambda: self.als_vorlage.emit(self._ziel()))
        waehlen = QPushButton("Vorlagenordner wählen …"); waehlen.clicked.connect(self._ordner_waehlen)
        oeffnen = QPushButton("Vorlagenordner öffnen"); oeffnen.clicked.connect(self._ordner_oeffnen)
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
        self.ordner = vorlagen.vorlagenordner(self.settings)
        self.rubriken: dict[str, dict] = {}
        for m in vorlagen.muster():
            r = self.rubriken.setdefault(m.get("rubrik") or m["name"], {"geruest": [], "dateien": [], "pfad": None})
            r["geruest"].append(m)
        unter, self.lose = vorlagen.rubriken(self.ordner)
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
            k.setToolTip(f"{name} — {n} Vorlage{'n' if n != 1 else ''}")
            self._kacheln.append(k)
            n_g += bool(r["geruest"]); n_e += bool(r["dateien"])
            r["kacheln"] = [self._geruest_kachel(m) for m in r["geruest"]] + [self._datei_kachel(p) for p in r["dateien"]]
            self.suche_alle += r["kacheln"]
        for p in self.lose:
            k = self._datei_kachel(p); self._kacheln.append(k); self.suche_alle.append(k); n_e += 1
        for i, text in enumerate((f"Standardvorlagen  {n_g}", f"Meine Vorlagen  {n_e}")):
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
        self.titel.setText(self._rubrik if in_rubrik else "Neu")
        if sicht:
            self.leer.clear()
        elif in_rubrik:
            self.leer.setText(f"In „{self._rubrik}“ liegt noch nichts. Lege Dokumente in den Ordner {self._ziel()} (.docx, .dotx, .odt oder .txt) "
                              "— oder nimm „Dieses Dokument als Vorlage behalten …“.")
        elif self._reiter == "eigene" and not self.suche.text().strip():
            self.leer.setText(f"Der Ordner {self.ordner} enthält noch keine Vorlagen. Lege dort Dokumente ab, oder in Unterordnern als Rubriken "
                              "(zum Beispiel „Lebenslauf“) — oder nimm „Dieses Dokument als Vorlage behalten …“.")
        else:
            self.leer.setText("Nichts gefunden.")

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._anordnen()

    # ---- Ordner ----------------------------------------------------------------------------------------------------
    def _rubrik_anlegen(self) -> None:
        name, ok = EingabeFenster.getText(self, "Neue Rubrik", "Name der Rubrik (zum Beispiel „Lebenslauf“):")
        name = name.strip().replace("/", "-").replace("\\", "-") if ok else ""
        if not name or name.startswith("."):
            return
        os.makedirs(os.path.join(self.ordner, name), exist_ok=True)
        self.neu_lesen(); self.rubrik_oeffnen(next((n for n in self.rubriken if n.lower() == name.lower()), name))

    def _ordner_waehlen(self) -> None:
        p = Dateifenster.getExistingDirectory(self, "Vorlagenordner", vorlagen.vorlagenordner(self.settings))
        if p:
            self.settings.set("vorlagen/ordner", p); self.neu_lesen()

    def _ordner_oeffnen(self) -> None:
        o = self._ziel() or vorlagen.vorlagenordner(self.settings)
        os.makedirs(o, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(o))

    def neu_lesen(self) -> None:
        """Der Ordner wird bei jedem Öffnen der Seite neu gelesen."""
        gemerkt = self._rubrik
        self._daten_lesen(); self._bauen()
        self._rubrik = gemerkt if gemerkt in self.rubriken else None
        self._anordnen()
