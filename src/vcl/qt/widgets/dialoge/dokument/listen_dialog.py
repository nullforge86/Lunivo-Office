"""Listen dialog: aus ``vcl.qt.widgets.dialoge.dokument.liste_dialog`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
import json
from PySide6.QtCore import QRectF, QSize, Qt
from framework.schnittstellen.einstellungen import Einstellungen
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QDialog, QListView, QListWidget, QListWidgetItem, QWidget
from writer.anbindung import listen as L
from writer.anbindung import mehrstufig as M
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import VorschauFlaeche, fussleiste
from vcl.qt.widgets.bausteine.symbole.medien.listen_symbole import liste_zeichner
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FENSTER_LISTE, HOEHE_EINGABE_TEXT, HOEHE_LISTENVORSCHAU, HOEHE_TEXT_NORMAL, HOEHE_ZEILE_ZULETZT, RAND_FENSTER_LISTE, RAND_KEIN
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.abstaende.mass import LISTE_KACHEL_ZUGABE, LISTE_KACHELN_REIHEN, SCHRIFT_LISTE_TITEL_PT
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import gruppe, FormularGitter
from vcl.qt.widgets.bausteine.interaktion.felder.angepasste_reiter import AngepassteReiter
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.dialoge.dokument.gliederung_anpassen_dialog import GliederungAnpassenDialog
from vcl.qt.widgets.dialoge.dokument.kachel_fueller import _KachelFueller
from vcl.qt.widgets.dialoge.dokument.liste_dialog_hilfen import _KACHEL, _bild, _gl_bild
from vcl.qt.widgets.dialoge.dokument.nummerierung_anpassen_dialog import NummerierungAnpassenDialog


_SCHLUESSEL = "listen/benutzer"


def benutzerlisten() -> list[dict]:
    try:
        d = json.loads(str(Einstellungen().get(_SCHLUESSEL, "[]") or "[]"))
        return [L.liste(x["stil"], x["praefix"], x["suffix"], x["start"]) for x in d if x.get("stil") in L.stile()]
    except (ValueError, KeyError, TypeError):
        return []


def _merke(listen: list[dict]) -> None:
    Einstellungen().set(_SCHLUESSEL, json.dumps(listen, ensure_ascii=False))


def _raster(eintraege: list[dict | None], bild=None) -> QListWidget:
    w = QListWidget(); w.setViewMode(QListView.IconMode); w.setResizeMode(QListView.Adjust); w.setMovement(QListView.Static)
    w.setIconSize(_KACHEL); w.setGridSize(QSize(_KACHEL.width() + 12, _KACHEL.height() + 8)); w.setSpacing(0)
    w.setMinimumHeight(LISTE_KACHELN_REIHEN * (_KACHEL.height() + LISTE_KACHEL_ZUGABE) + LISTE_KACHEL_ZUGABE)
    for s in eintraege:
        it = QListWidgetItem((bild or _bild)(s), ""); it.setData(Qt.UserRole, s)
        w.addItem(it)
    return w


class ListenDialog(PanelFaehig, QDialog):
    ALS_PANEL = True                                          # öffnet sich in der Seitenleiste (siehe zusatz_panel)

    def kompakt_machen(self) -> None:
        """Für die schmale Seitenleiste: kleinere Kacheln (drei je Zeile), Reiter mit Überlauf hinter „•••“, Fenster ohne feste Größe."""
        self._fueller = [_KachelFueller(w, 4) for w in (self.r_punkte, self.r_zahlen, self.r_gl)]       # vier Kacheln je Zeile, die ganze Breite ausgefüllt
        self.liste.setMinimumHeight(HOEHE_ZEILE_ZULETZT); self.liste.setMaximumHeight(HOEHE_TEXT_NORMAL); self.vorschau.setFixedHeight(HOEHE_LISTENVORSCHAU)
        for i, (kurz, voll) in enumerate((("Aufzählung", "Aufzählungszeichen"), ("Nummern", "Nummerierung"), ("Gliederung", "Gliederung nummeriert"),
                                          ("Eigene", "Benutzerdefinierte Liste"))):
            self.reiter.setTabText(i, kurz); self.reiter.setTabToolTip(i, voll)
        self.setMinimumSize(0, 0)

    def passe_an(self, breite: int, hoehe: int) -> None:
        """Je breiter die Seitenleiste, desto mehr Kacheln je Zeile (vier bis sechs), damit die Auswahl ohne Rollen auskommt."""
        spalten = 6 if breite >= 520 else 5 if breite >= 420 else 4
        for f in getattr(self, "_fueller", []):
            f.spalten = spalten; f._anpassen()

    def __init__(self, parent=None, aktuell: dict | None = None, *, seite: str = "aufzaehlung"):
        super().__init__(parent)
        self.setWindowTitle("Nummerierung und Aufzählungszeichen"); self.resize(*GROESSE_FENSTER_LISTE)
        self._benutzer = benutzerlisten()
        v = _spalte("standard", self)
        self.reiter = AngepassteReiter(); v.addWidget(self.reiter, 1)
        self.r_punkte = _raster([None, L.liste("disc"), L.liste("square")] + [M.aufzaehlung(g) for g in M.glyphen()], bild=_gl_bild)
        self.r_zahlen = _raster([None] + [L.liste(*n) for n in L.nummerierungen()])
        self.r_gl = _raster([None] + [g for _n, g in M.vorlagen()], bild=_gl_bild)
        self.reiter.addTab(self.r_punkte, "Aufzählungszeichen"); self.reiter.addTab(self.r_zahlen, "Nummerierung")
        self.reiter.addTab(self.r_gl, "Gliederung nummeriert")
        # ---- Benutzerdefinierte Liste
        b = QWidget(); bg = FormularGitter(b); bg.setContentsMargins(*RAND_FENSTER_LISTE)
        self.liste = QListWidget(); self.vorschau = VorschauFlaeche(self._male, 150)
        self.liste.setMinimumHeight(HOEHE_EINGABE_TEXT)
        bg.reihe(("Benutzerdefinierte Liste:", self.liste), ("Listenvorschau:", self.vorschau))        # gleich breit wie in der Vorlage, schmal untereinander
        self.reiter.addTab(b, "Benutzerdefinierte Liste")
        self._fuelle_benutzer()
        # ---- Knöpfe
        self.anpassen = knopf("standard", "Anpassen …"); self.loeschen = knopf("standard", "Löschen")
        self.anpassen.clicked.connect(self._anpassen); self.loeschen.clicked.connect(self._loeschen)
        gruppe = QWidget(); gh = FlussLayout(6); gruppe.setLayout(gh); gh.setContentsMargins(*RAND_KEIN)       # unter allen Reitern dieselbe Zeile, ohne Rahmen
        gh.addWidget(self.anpassen); gh.addWidget(self.loeschen)
        v.addWidget(gruppe)
        fussleiste(self, v)
        self._anfangsauswahl(aktuell, seite)
        self.reiter.currentChanged.connect(self._knoepfe)
        for w in (self.r_punkte, self.r_zahlen, self.r_gl, self.liste):
            w.currentRowChanged.connect(self._knoepfe)
        for w in (self.r_punkte, self.r_zahlen, self.r_gl):
            w.itemDoubleClicked.connect(lambda *_: self.accept())
        self._knoepfe()

    def _anfangsauswahl(self, aktuell: dict | None, seite: str) -> None:
        """Die Auswahl beim Öffnen: das bisherige Format, sonst die Vorgabe des Aufrufs (Aufzählung oder Nummerierung)."""
        for w in (self.r_punkte, self.r_zahlen, self.r_gl):
            w.setCurrentRow(0)
        if not aktuell:
            self.reiter.setCurrentIndex({"nummerierung": 1}.get(seite, 0))
            return
        raster = self._raster_zu(aktuell)
        i = next((i for i in range(raster.count()) if raster.item(i).data(Qt.UserRole) == aktuell), None)
        if i is None and raster in (self.r_gl, self.r_punkte):
            self._eintragen_gl(aktuell, raster); i = raster.count() - 1
        elif i is None and raster is self.r_zahlen:              # ein eigenes Format: oben in die Auswahl der Nummerierung
            self._eintragen(aktuell); i = raster.count() - 1
        if i is not None:
            raster.setCurrentRow(i)
        self.reiter.setCurrentWidget(raster)

    def _raster_zu(self, aktuell: dict):
        """Das Raster, in dem ein bisheriges Format steht: Gliederung, Aufzählung oder Nummerierung."""
        if "ebenen" in aktuell:
            return self.r_punkte if M.ist_aufzaehlung(aktuell) else self.r_gl
        return self.r_punkte if L.stile()[aktuell["stil"]][1] else self.r_zahlen

    # ---- Benutzerdefiniert
    def _fuelle_benutzer(self) -> None:
        self.liste.clear()
        if not self._benutzer:
            self.liste.addItem("Keine Liste"); return
        for s in self._benutzer:
            it = QListWidgetItem(L.marke(s).replace("|", "  ")); it.setData(Qt.UserRole, s); self.liste.addItem(it)

    def _male(self, p, rect) -> None:
        it = self.liste.currentItem()
        s = it.data(Qt.UserRole) if it else None
        if s:
            liste_zeichner(L.marke(s))(p, QRectF(rect).adjusted(50, 10, -50, -10))
        else:
            p.setPen(QColor(Farbe.TINTE)); f = p.font(); f.setPointSize(SCHRIFT_LISTE_TITEL_PT); p.setFont(f)
            p.drawText(QRectF(rect), Qt.AlignCenter, "Keine")

    def _eintragen(self, s: dict) -> None:
        """Ein selbst angepasstes Format kommt in den Reiter „Nummerierung“ und in die Liste der eigenen Formate."""
        it = QListWidgetItem(_bild(s), ""); it.setData(Qt.UserRole, s); self.r_zahlen.addItem(it)
        if s not in self._benutzer:
            self._benutzer.append(s); _merke(self._benutzer); self._fuelle_benutzer()

    def _eintragen_gl(self, d: dict, raster: QListWidget | None = None) -> None:
        it = QListWidgetItem(_gl_bild(d), ""); it.setData(Qt.UserRole, d); (raster or self.r_gl).addItem(it)

    def _aktuell(self) -> QWidget:
        return self.reiter.currentWidget()

    def _auswahl(self) -> dict | None:
        w = self._aktuell()
        it = w.currentItem() if isinstance(w, QListWidget) else self.liste.currentItem()
        return it.data(Qt.UserRole) if it else None

    def _knoepfe(self, *_) -> None:
        s = self._auswahl()
        self.anpassen.setEnabled(s is not None)
        self.loeschen.setVisible(self._aktuell() not in (self.r_punkte, self.r_zahlen, self.r_gl))
        self.loeschen.setEnabled(s is not None)
        self.vorschau.update()

    def _anpassen(self) -> None:
        from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import zeige_unter
        s = self._auswahl()
        if s is not None and "ebenen" not in s and L.stile()[s["stil"]][1]:      # Punkt, Kreis, Quadrat: als eigenes Zeichen anpassen
            s = M.aufzaehlung({"disc": "●", "circle": "○", "square": "■"}[s["stil"]])
        if s is not None and "ebenen" in s:
            bullets = M.ist_aufzaehlung(s)
            g = GliederungAnpassenDialog(self, s, titel="Aufzählungszeichen anpassen" if bullets else "Gliederung anpassen")

            def fertig_gl() -> None:
                ziel = self.r_punkte if M.ist_aufzaehlung(g.defn()) else self.r_gl
                self._eintragen_gl(g.defn(), ziel)
                self.reiter.setCurrentWidget(ziel); ziel.setCurrentRow(ziel.count() - 1)
            zeige_unter(self, g, fertig_gl)
            return
        d = NummerierungAnpassenDialog(self, s)

        def fertig_nr() -> None:
            if d.spec():
                self._eintragen(d.spec())
                self.reiter.setCurrentWidget(self.r_zahlen); self.r_zahlen.setCurrentRow(self.r_zahlen.count() - 1)
        zeige_unter(self, d, fertig_nr)

    def _loeschen(self) -> None:
        s = self._auswahl()
        if s in self._benutzer:
            self._benutzer.remove(s); _merke(self._benutzer); self._fuelle_benutzer()
        self._knoepfe()

    def ergebnis(self) -> dict | None:
        """Die gewählte Liste, oder None bei „Kein“."""
        return self._auswahl()
