"""Backstage-Ansicht des Reiters „Datei“: links die Befehlsliste, rechts die Seite zum gewählten Befehl.

Das Menü links folgt Kays Vorbild (Bildschirmfoto „Menü“). Befehle ohne eigene Seite (Speichern, Beenden)
führen sofort aus und schließen die Ansicht; PDF- und Bildexport, Neu (Vorlagen), Öffnen (Zuletzt verwendet und Dateiauswahl),
Speichern unter, Drucken, Dokumentverschlüsselung, Hilfe und Optionen zeigen ihre Seite rechts.
"""
from __future__ import annotations

from lunivo_writer.oberflaeche.baukasten.basis.raster import RasterSpalte
from lunivo_writer.oberflaeche.baukasten.basis.darstellung import grundschrift, rolle as _rolle

from lunivo_writer.oberflaeche.baukasten.geruest.rollen import anwenden, raender, reihe as _reihe, spalte as _spalte

import os

from datetime import datetime

from PySide6.QtCore import QSize, Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QKeySequence, QPainter, QPalette, QPen, QShortcut
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QFrame, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QScrollArea,
    QStackedWidget, QStyledItemDelegate, QToolButton, QWidget,
)

from lunivo_writer.oberflaeche.baukasten.basis import daten
from lunivo_writer.oberflaeche.baukasten.basis.daten import text as _t
from lunivo_writer.oberflaeche.baukasten.bausteine.feld.feld import zeilenfeld
from lunivo_writer.oberflaeche.baukasten.bausteine.haken.haken import haken
from lunivo_writer.oberflaeche.baukasten.bausteine.knopf.knopf import knopf, werkzeugknopf
from lunivo_writer.oberflaeche.baukasten.geruest.befehlsseite import befehlsseite, gruppenkopf, inhaltsseite, seitenrahmen
from lunivo_writer.oberflaeche.baukasten.medien.datei_symbole import datei_symbol
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FormularGitter
from lunivo_writer.oberflaeche.bauteile import symbole

from lunivo_writer.farmwork.datentypen.farben import Farbe
from lunivo_writer.oberflaeche.baukasten.geruest.spalten import ZweiSpalter
from lunivo_writer.oberflaeche.baukasten.basis.mass import ABSTAND_ENG, ABSTAND_GROSS, ABSTAND_KEIN, ABSTAND_KLEIN, ABSTAND_MITTEL, ABSTAND_SPALTE, ABSTAND_BLOCK, ABSTAND_NORMAL, BREITE_FELD_ORT, BREITE_NAMENSFELD, BREITE_NAVIGATION_BACKSTAGE, BREITE_NAVIGATION_OPTIONEN, BREITE_ZEILENHINWEIS, HOEHE_ABSTAND_LISTE, HOEHE_TRENNER_LISTE, HOEHE_ZEILE_ZULETZT, ICON_GROSS, ICON_KACHEL, ICON_KLEIN, ICON_KNOPF_GROSS, ICON_LISTE, ICON_NORMAL, PADDING_BACKSTAGE_KNOPF, PADDING_BACKSTAGE_ZURUECK, PADDING_LINKS_BACKSTAGE_LISTE, PADDING_NAVIGATION_EINTRAG, RADIUS_FELD, RADIUS_KLEIN, RAND_BACKSTAGE_SEITE, RAND_FUSS_BACKSTAGE, RAND_FUSS_RECHTS, RAND_KEIN, RAND_KOPF_LINKS, RAND_LISTENKOPF, RAND_ZEILE, RAND_ZEILE_BACKSTAGE, RAND_ZULETZT_ZEILE, SCHRIFT_LISTE, SCHRIFT_UEBERSCHRIFT, SCHRIFT_UEBERSCHRIFT_KLEIN

# Das Menü links (Schlüssel, Beschriftung, Symbol, Art: "seite" | "tun" | "trenner", Ziel) steht in ressourcen/daten/datei_ansicht.json.
_DATEN = daten.lade("datei_ansicht")
EINTRAEGE = [(e["schluessel"], _t(e["text"]) if "text" in e else "", e.get("symbol", ""), e["art"], e.get("ziel")) for e in _DATEN.get("menue", [])]
MIT_DOKUMENT = tuple(e["schluessel"] for e in _DATEN.get("menue", []) if e.get("mit_dokument"))
MIT_PFEIL = tuple(e["schluessel"] for e in _DATEN.get("menue", []) if e.get("pfeil"))
SYMBOLE = _DATEN.get("symbole", {})


def symbol(name: str, px: int = ICON_LISTE):
    return symbole.icon(SYMBOLE.get(name, name), px)


class _Zeile(QStyledItemDelegate):
    """Zeichnet die Trennlinien quer über die Liste und den kleinen Pfeil rechts bei Einträgen mit eigener Seite."""

    def paint(self, p: QPainter, opt, idx):
        art = idx.data(ART)
        if art == "trenner":
            p.save()
            p.setPen(QPen(opt.palette.color(QPalette.Mid).lighter(130), 1))
            y = opt.rect.center().y()
            p.drawLine(opt.rect.left(), y, opt.rect.right(), y)
            p.restore()
            return
        super().paint(p, opt, idx)
        if idx.data(PFEIL):
            p.save()
            pm = symbole.icon("chevron-right", ICON_KLEIN).pixmap(ICON_KLEIN, ICON_KLEIN)
            p.drawPixmap(opt.rect.right() - 18, opt.rect.center().y() - 7, pm)
            p.restore()


ART, PFEIL = Qt.UserRole + 1, Qt.UserRole + 2



class Backstage(QWidget):
    schliessen = Signal()

    def __init__(self, fenster):
        super().__init__()
        self.w = fenster
        self.setObjectName("bsAnsicht")
        grundschrift(self)
        links = QWidget()
        links.setObjectName("bsLinks")
        ll = _spalte("listenkopf", links)
        self.liste = QListWidget()
        self.liste.setObjectName("bsListe")
        self.liste.setIconSize(QSize(ICON_LISTE, ICON_LISTE))
        self.liste.setFocusPolicy(Qt.StrongFocus)
        self.liste.setAccessibleName(_t("datei.navigation.name"))
        self.liste.setAccessibleDescription(_t("datei.navigation.beschreibung"))
        self.liste.setItemDelegate(_Zeile(self.liste))
        self.liste.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.liste.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        ll.addWidget(self.liste, 1)
        self._links = links                                          # bei den Optionen ausgeblendet
        self.rechts = QWidget()
        self.rechts.setObjectName("bsRechts")
        rl = _spalte("standard", self.rechts)
        self.stapel = QStackedWidget()
        rl.addWidget(self.stapel)
        # bildschirmbreit: die Menüleiste steht immer links (breit_ab=0 = ohne Umbruch), aber aus dem gemeinsamen Baustein
        self.spalten = ZweiSpalter(links, self.rechts, breit_ab=0, links_breite=BREITE_NAVIGATION_BACKSTAGE)
        lay = _spalte("kein", self); lay.addWidget(self.spalten)
        self.zeilen: dict[str, QListWidgetItem] = {}
        for schl, text, sym, art, _b in EINTRAEGE:
            it = QListWidgetItem(text)
            it.setData(ART, art)
            it.setData(PFEIL, schl in MIT_PFEIL)
            if art == "trenner":
                it.setFlags(Qt.NoItemFlags)
                it.setSizeHint(QSize(BREITE_ZEILENHINWEIS, HOEHE_TRENNER_LISTE))
                it.setText("")
            else:
                it.setIcon(symbol(sym))
                it.setSizeHint(QSize(BREITE_ZEILENHINWEIS, HOEHE_ABSTAND_LISTE))
            self.zeilen[schl] = it
            self.liste.addItem(it)
        self.liste.itemClicked.connect(self._gewaehlt)
        self.liste.itemActivated.connect(self._aktiviert)
        self.seiten: dict[str, QWidget] = {}
        QShortcut(QKeySequence(Qt.Key_Escape), self, activated=self.schliessen.emit)
        self._frischen_sich_selbst = True

    # ---- Aufbau der Seiten (bei jedem Öffnen frisch, damit Zahlen und Listen stimmen) ----------------------------
    def oeffnen(self, seite: str = "zuletzt", unter: str | None = None):
        """``unter``: bei „optionen“ die Seite der Optionen, die gleich offen sein soll (z. B. „ki“)."""
        self._optionen_unter = unter
        self._links.show()
        while self.stapel.count():
            w = self.stapel.widget(0)
            self.stapel.removeWidget(w)
            w.deleteLater()
        self.seiten.clear()
        haben_dok = self.w.current_tab() is not None
        for schl in MIT_DOKUMENT:
            self.zeilen[schl].setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable if haben_dok else Qt.NoItemFlags)
        if seite not in self._alle_seiten() or (not haben_dok and seite not in ("zuletzt", "optionen")):
            seite = "zuletzt"
        self._zeigen(seite)

    @staticmethod
    def _alle_seiten() -> list[str]:
        ziele = [e["ziel"] for e in _DATEN["menue"] if e["art"] == "seite"] + list(_DATEN["seiten"]) + _DATEN.get("zusatzseiten", []) + list(_DATEN.get("inhaltsseiten", {}))
        return list(dict.fromkeys(ziele))

    def _seite_sicher(self, schl: str) -> QWidget:
        """Seiten werden erst beim ersten Zeigen gebaut (Lazy Loading); jedes Öffnen der Ansicht beginnt frisch."""
        w = self.seiten.get(schl)
        if w is None:
            if schl in _DATEN["seiten"]:
                w = self._aus_beschreibung(schl)
            elif schl in _DATEN.get("inhaltsseiten", {}):
                w = self._inhaltsseite(schl)
            else:
                w = getattr(self, "_" + schl)()
            self.seiten[schl] = w
            self.stapel.addWidget(w)
        return w

    def optionen_seite(self) -> str | None:
        """Schlüssel der Optionenseite, die gerade offen ist (z. B. „ansicht“)."""
        a = getattr(self.seiten.get("optionen"), "_ansicht", None)
        it = a.baum.currentItem() if a is not None else None
        return it.data(0, 0x100) if it is not None else None

    def _optionen(self) -> QWidget:
        """Platzhalter: die Optionen werden erst gebaut, wenn die Seite zum ersten Mal gezeigt wird."""
        ph = QWidget()
        _spalte("kein", ph)
        ph._ansicht = None
        return ph

    def _optionen_zeigen(self) -> None:
        from lunivo_writer.oberflaeche.dialoge.optionen import OptionenAnsicht
        ph = self._seite_sicher("optionen")
        self._links.hide()                                           # die Optionen füllen die ganze Breite; das Menü ist für die Dauer weg
        if ph._ansicht is None:
            v = ph.layout()                                                     # keine Lücke zwischen Optionen und Fußleiste: die linke Fläche bleibt ganz
            kopf = QWidget(); kopf.setObjectName("optKopf")
            kh = _reihe("kein", kopf)
            kopf_links = QWidget(); kopf_links.setObjectName("optLinks"); kopf_links.setFixedWidth(BREITE_NAVIGATION_OPTIONEN)         # die linke Fläche beginnt schon in der Kopfzeile
            kopf_links.setAttribute(Qt.WA_StyledBackground, True)
            kl = _reihe("kopf", kopf_links)
            zurueck = knopf("standard", _t("datei.optionen.zurueck"), symbol="arrow-left", objektname="optZurueck", ohne_rand=True, hand=True,
                            tooltip=_t("datei.optionen.zurueck.tipp"), name=_t("datei.optionen.zurueck"), aktion=self.schliessen.emit)
            kl.addWidget(zurueck); kl.addStretch(1)
            kh.addWidget(kopf_links); kh.addStretch(1)
            ph._ansicht = OptionenAnsicht(self.w, getattr(self, "_optionen_unter", None))
            fuss = QWidget(); fh = _reihe("kein", fuss)
            unten_links = QWidget(); unten_links.setObjectName("optLinks"); unten_links.setFixedWidth(BREITE_NAVIGATION_OPTIONEN)     # die linke Fläche läuft bis ganz unten durch
            unten_links.setAttribute(Qt.WA_StyledBackground, True)
            rechts_fuss = _reihe("fuss")
            fertig = knopf("standard", _t("datei.optionen.fertig"), objektname="optFertig", hand=True, aktion=self.schliessen.emit)
            rechts_fuss.addStretch(1); rechts_fuss.addWidget(fertig)
            fh.addWidget(unten_links); fh.addLayout(rechts_fuss, 1)
            ph._kopf, ph._fertig, ph._zurueck = kopf, fertig, zurueck
            v.addWidget(kopf); v.addWidget(ph._ansicht, 1); v.addWidget(fuss)
        elif getattr(self, "_optionen_unter", None):
            ph._ansicht.gehe_zu(self._optionen_unter)

    def _zeigen(self, schl: str):
        self._seite_sicher(schl)
        zeigen = getattr(self, f"_{schl}_zeigen", None)                 # Seiten, die erst beim Zeigen fertig gebaut werden
        if zeigen is not None:
            zeigen()
        self.stapel.setCurrentWidget(self.seiten[schl])
        menue = _DATEN.get("inhaltsseiten", {}).get(schl, {}).get("gehoert_zu", schl)              # eine Unterseite hebt den Menüpunkt hervor, zu dem sie gehört
        zeile = next((self.zeilen[e[0]] for e in EINTRAEGE if e[3] == "seite" and e[4] == menue), None)
        if zeile is None:
            self.liste.clearSelection()
            self.liste.setCurrentItem(None)
        else:
            self.liste.setCurrentItem(zeile)

    def _aktiviert(self, it: QListWidgetItem):
        """Eingabetaste in der Liste; ein Mausklick meldet sich zugleich über ``itemClicked`` und darf nicht doppelt wirken."""
        if QApplication.mouseButtons() == Qt.NoButton:
            self._gewaehlt(it)

    def _gewaehlt(self, it: QListWidgetItem):
        schl = next(k for k, v in self.zeilen.items() if v is it)
        art, ziel = next((e[3], e[4]) for e in EINTRAEGE if e[0] == schl)
        if art == "seite":
            self._zeigen(ziel)
        elif art == "tun":
            self.schliessen.emit()
            self.w.befehle.tun(ziel)

    def _speicherort(self):
        t = self.w.current_tab()
        if t and t.path and os.path.exists(t.path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(os.path.abspath(t.path))))
        else:
            self.w.statusBar().showMessage(_t("datei.speicherort.fehlt"), 5000)

    # ---- Bausteine -------------------------------------------------------------------------------------------
    def _seite(self, titel: str) -> tuple[QScrollArea, RasterSpalte]:
        return seitenrahmen(titel)

    @staticmethod
    def _gruppe(v: RasterSpalte, text: str, hinweis: str = ""):
        gruppenkopf(v, text, hinweis)

    def _inhaltsseite(self, schluessel: str) -> QWidget:
        """Seiten, deren Inhalt ein Fachmodul liefert (z. B. die Hilfe): sie erscheinen im Dashboard selbst, nie in einer Seitenleiste."""
        import importlib
        spec = _DATEN["inhaltsseiten"][schluessel]
        inhalt = getattr(importlib.import_module(spec["modul"]), spec["bauer"])()
        return inhaltsseite(_t(spec["titel"]), inhalt, spec.get("scrollen", True))

    def _aus_beschreibung(self, schluessel: str) -> QWidget:
        """Seiten, die nur aus Titel, Gruppen und Befehlsknöpfen bestehen (Hilfe, Speichern unter, Öffnen mit): Inhalt aus der Datendatei."""
        def ausloeser(k: dict) -> None:
            if "seite" in k:
                self._zeigen(k["seite"])
            elif "aktion" in k:
                getattr(self, "_" + k["aktion"])()
            else:
                self.schliessen.emit(); self.w.befehle.tun(k["befehl"])
        return befehlsseite(_DATEN["seiten"][schluessel], ausloeser, lambda k: "befehl" not in k or self.w.befehle.hat(k["befehl"]))

    # ---- Seiten ------------------------------------------------------------------------------------------------
    def _zuletzt(self):
        """Rechts neben dem Menü: die zuletzt verwendeten Dateien (Name, Ordner, Datum; ✕ nimmt sie aus der Liste)."""
        sa, v = self._seite("")
        anwenden(v, "zuletzt_liste")
        kopf = _reihe("standard")
        t = QLabel(_t("datei.zuletzt.titel")); t.setObjectName("bsZuletzt")
        oeffnen = knopf("standard", _t("datei.zuletzt.weitere"), objektname="optFertig", symbol="oeffnen", symbolgroesse="gross", symbol_einpassen=True, hand=True,
                        tooltip=_t("datei.zuletzt.weitere.tipp"), name=_t("datei.zuletzt.weitere"), aktion=lambda: (self.schliessen.emit(), self.w.open_dialog()))
        kopf.addWidget(t); kopf.addStretch(1)
        v.addLayout(kopf)
        v.addSpacing(ABSTAND_NORMAL)
        knoepfe = _reihe("standard"); knoepfe.addWidget(oeffnen); knoepfe.addStretch(1)   # direkt unter der Überschrift
        v.addLayout(knoepfe)
        v.addSpacing(ABSTAND_BLOCK)
        pfade = self.w.settings.recent()
        if not pfade:
            h = QLabel(_t("datei.zuletzt.leer"))
            h.setObjectName("bsHinweis")
            v.addWidget(h)
        heim = os.path.expanduser("~")
        for p in pfade:
            zeile = _reihe("eng")
            ordner = os.path.dirname(p)
            ordner = ("~" + ordner[len(heim):] if ordner.startswith(heim) else ordner) + "/"
            sym = datei_symbol(p)                                    # vollständiges, formatspezifisches Blatt
            k = knopf("standard", objektname="bsDatei", hand=True, name=os.path.basename(p), tooltip=p,              # sichtbar sind Name, Ordner und Datum als eigene Zeilen
                      symbol_einpassen=False, aktiv=os.path.exists(p), aktion=lambda p=p: (self.schliessen.emit(), self.w.open_path(p)))
            k.setIcon(sym if not sym.isNull() else symbol("datei", ICON_KACHEL))
            k.setIconSize(QSize(ICON_KACHEL, ICON_KACHEL))
            text = _spalte("kein")
            name = QLabel(os.path.basename(p)); name.setAttribute(Qt.WA_TransparentForMouseEvents)
            ort = QLabel(ordner); ort.setObjectName("bsHinweis"); ort.setAttribute(Qt.WA_TransparentForMouseEvents)
            ort.setMaximumWidth(BREITE_FELD_ORT)
            ort.setText(ort.fontMetrics().elidedText(ordner, Qt.ElideRight, 380))
            text.addWidget(name); text.addWidget(ort)
            innen = _reihe("zuletzt", k)
            innen.addLayout(text); innen.addStretch(1)
            try:
                datum = datetime.fromtimestamp(os.path.getmtime(p))
                heute = datetime.now().date() == datum.date()
                d = QLabel((_t("datei.zuletzt.heute") + datum.strftime("%H:%M")) if heute else datum.strftime("%d.%m. %H:%M"))
            except OSError:
                d = QLabel("")
            d.setObjectName("bsHinweis"); d.setAttribute(Qt.WA_TransparentForMouseEvents)
            innen.addWidget(d)
            weg = werkzeugknopf("standard", objektname="bsKlein", symbolbild=symbol("weg", ICON_KLEIN), bildgroesse=QSize(ICON_KLEIN, ICON_KLEIN), flach=False,
                                tooltip=_t("datei.zuletzt.entfernen"), hand=True, aktion=lambda p=p: (self.w.settings.remove_recent(p), self.oeffnen("zuletzt")))
            zeile.addWidget(k, 1); zeile.addWidget(weg)
            v.addLayout(zeile)
        v.addStretch(1)
        return sa

    def _vorlage(self) -> QWidget:
        """Platzhalter: die Galerie mit den Vorschauen wird erst gebaut, wenn die Seite gezeigt wird."""
        ph = QWidget()
        _spalte("kein", ph)
        ph._ansicht = None
        return ph

    def _vorlage_zeigen(self) -> None:
        from lunivo_writer.oberflaeche.baukasten.vorlagen.vorlagen_galerie import VorlagenGalerie
        ph = self._seite_sicher("vorlage")
        if ph._ansicht is None:
            g = VorlagenGalerie(self.w.settings, self.w.current_tab() is not None, self.w.benutzerdaten())
            g.gewaehlt.connect(lambda art, wert: (self.schliessen.emit(), self.w.neu_aus_wahl(art, wert)))
            g.als_vorlage.connect(lambda ziel: (self.schliessen.emit(), self.w.als_vorlage_speichern(ziel or None)))
            ph.layout().addWidget(g); ph._ansicht = g
        else:
            ph._ansicht.neu_lesen()

    def _drucken(self) -> QWidget:
        """Platzhalter: das Druckfenster samt Vorschau wird erst gebaut, wenn die Seite gezeigt wird."""
        ph = QWidget()
        _spalte("kein", ph)
        ph._ansicht = None
        return ph

    def _pdf(self) -> QWidget:
        """Platzhalter für den eingebetteten PDF-Export, frisch je Öffnen des Datei-Menüs."""
        ph = QScrollArea()
        ph.setObjectName("bsSeite")
        ph.setWidgetResizable(True)
        ph.setFrameShape(QFrame.NoFrame)
        ph._ansicht = None
        return ph

    def _pdf_zeigen(self) -> None:
        ph = self._seite_sicher("pdf")
        if ph._ansicht is None:
            ph._ansicht = self.w.pdf_export_widget()
            ph.setWidget(ph._ansicht)

    def _bild(self) -> QWidget:
        """Platzhalter für den Bildexport in der rechten Menüspalte."""
        ph = QScrollArea()
        ph.setObjectName("bsSeite")
        ph.setWidgetResizable(True)
        ph.setFrameShape(QFrame.NoFrame)
        ph._ansicht = None
        return ph

    def _bild_zeigen(self) -> None:
        ph = self._seite_sicher("bild")
        if ph._ansicht is None:
            ph._ansicht = self.w.bild_export_widget()
            ph.setWidget(ph._ansicht)

    def _drucken_zeigen(self) -> None:
        ph = self._seite_sicher("drucken")
        t = self.w.current_tab()
        if ph._ansicht is not None or t is None:
            return
        v = ph.layout()
        ph._ansicht = self.w.druck_ansicht(t)
        v.addWidget(ph._ansicht, 1)
        fuss = _reihe("fuss")
        hilfe = knopf("standard", _t("datei.drucken.hilfe"), rolle="aktion", aktion=self.w.druck_hilfe)
        drucken = knopf("standard", _t("datei.drucken.drucken"), objektname="optFertig", standard=True, hand=True)
        drucken.clicked.connect(lambda: (self.schliessen.emit(), self.w.drucke_nach_wahl(t, ph._ansicht.ergebnis())))
        ph._ansicht.geaendert.connect(lambda: drucken.setEnabled(ph._ansicht.gueltig()))
        fuss.addWidget(hilfe); fuss.addStretch(1); fuss.addWidget(drucken)
        v.addLayout(fuss)

    def _schuetzen(self):
        sa, v = self._seite(_t("datei.schuetzen.titel"))
        t = self.w.current_tab()
        self._gruppe(v, _t("datei.schuetzen.gruppe.kennwort"), _t("datei.schuetzen.gruppe.kennwort.hinweis"))
        kennwort_form = QWidget(); kg = FormularGitter(kennwort_form); raender(kg, "zeile"); kg.einspaltig = True; kg.beschriftung_voll = True
        kg.beschriftungsabstand = ABSTAND_GROSS; kg.zeilenabstand = ABSTAND_MITTEL
        kennwort = zeilenfeld("frei", platzhalter=_t("datei.schuetzen.kennwort"), passwort=True)
        bestaetigung = zeilenfeld("frei", platzhalter=_t("datei.schuetzen.bestaetigung"), passwort=True)
        kennwort.setAccessibleName(_t("datei.schuetzen.kennwort")); bestaetigung.setAccessibleName(_t("datei.schuetzen.bestaetigung.name"))
        kennwort.setEnabled(t is not None); bestaetigung.setEnabled(t is not None)
        kg.zeile(_t("datei.schuetzen.kennwort.beschriftung"), kennwort); kg.zeile(_t("datei.schuetzen.bestaetigung.beschriftung"), bestaetigung)
        v.addWidget(kennwort_form)

        hinweis = QLabel(_t("datei.schuetzen.warnung"))
        hinweis.setWordWrap(True); hinweis.setObjectName("bsHinweis"); v.addWidget(hinweis)
        status = QLabel(); status.setWordWrap(True); status.setObjectName("bsHinweis")
        if t is None:
            status.setText(_t("datei.kein_dokument"))
        elif t.meta.get("kennwort"):
            status.setText(_t("datei.schuetzen.status.geplant"))
        else:
            status.setText(_t("datei.schuetzen.status.ungeschuetzt"))
        v.addWidget(status)

        aktionen = _reihe("standard")
        setzen = knopf("standard", _t("datei.schuetzen.setzen"), objektname="optFertig", aktiv=t is not None)
        entfernen = knopf("standard", _t("datei.schuetzen.entfernen"), rolle="aktion", aktiv=bool(t and t.meta.get("kennwort")))
        aktionen.addWidget(setzen); aktionen.addWidget(entfernen); aktionen.addStretch(1); v.addLayout(aktionen)

        def setze_kennwort():
            if not kennwort.text():
                status.setText(_t("datei.schuetzen.fehler.leer")); kennwort.setFocus(); return
            if kennwort.text() != bestaetigung.text():
                status.setText(_t("datei.schuetzen.fehler.verschieden")); bestaetigung.setFocus(); return
            t.meta["kennwort"] = kennwort.text(); t.editor.document().setModified(True)
            kennwort.clear(); bestaetigung.clear(); entfernen.setEnabled(True)
            status.setText(_t("datei.schuetzen.status.gesetzt"))

        def entferne_kennwort():
            t.meta.pop("kennwort", None); t.editor.document().setModified(True)
            kennwort.clear(); bestaetigung.clear(); entfernen.setEnabled(False)
            status.setText(_t("datei.schuetzen.status.entfernt"))

        setzen.clicked.connect(setze_kennwort); entfernen.clicked.connect(entferne_kennwort)

        self._gruppe(v, _t("datei.schuetzen.gruppe.datenschutz"), _t("datei.schuetzen.gruppe.datenschutz.hinweis"))
        for key, label, default in (
            ("sicherheit/markup_oeffnen", _t("datei.schuetzen.markup"), True),
            ("sicherheit/personendaten_weg", _t("datei.schuetzen.personendaten"), False),
        ):
            box = haken("standard", label, an=self.w.settings.get_bool(key, default))
            box.toggled.connect(lambda an, k=key: self.w.settings.set(k, an))
            v.addWidget(box)

        self._gruppe(v, _t("datei.schuetzen.gruppe.dokument"), _t("datei.schuetzen.gruppe.dokument.hinweis"))
        eigenschaften = knopf("standard", _t("datei.schuetzen.eigenschaften"), objektname="bsKnopf", hand=True, symbol="info", symbolgroesse="gross", symbol_merken=True,
                              tooltip=_t("datei.schuetzen.eigenschaften.tipp"), name=_t("datei.schuetzen.eigenschaften"), aktion=lambda: self._zeigen("info"))
        v.addWidget(eigenschaften)
        self._gruppe(v, _t("datei.schuetzen.gruppe.bearbeitung"), _t("datei.schuetzen.gruppe.bearbeitung.hinweis"))
        sperren = haken("standard", _t("datei.schuetzen.sperren"), an=bool(t and getattr(t, "gesperrt", False)), aktiv=t is not None)
        sperren.toggled.connect(lambda an: t and an != bool(getattr(t, "gesperrt", False)) and self.w.toggle_sperre())
        v.addWidget(sperren)
        self._gruppe(v, _t("datei.schuetzen.gruppe.signatur"), _t("datei.schuetzen.gruppe.signatur.hinweis"))
        k = knopf("standard", _t("datei.schuetzen.signatur"), objektname="bsKnopf", aktiv=False)
        v.addWidget(k)
        v.addStretch(1)
        return sa

    def _info(self):
        sa, v = self._seite(_t("datei.info.titel"))
        t = self.w.current_tab()
        if t is None:
            h = QLabel(_t("datei.kein_dokument"))
            h.setObjectName("bsHinweis")
            v.addWidget(h)
            v.addStretch(1)
            return sa
        self._info_allgemein(v, t)
        self._info_statistik(v, t.editor)
        self._info_eigenschaften(v, t)
        v.addStretch(1)
        return sa

    def _info_allgemein(self, v, t):
        groesse = os.path.getsize(t.path) if t.path and os.path.exists(t.path) else None
        self._gruppe(v, _t("datei.info.gruppe.allgemein"))
        for name, wert in ((_t("datei.info.name"), t.title), (_t("datei.info.ort"), t.path or _t("datei.info.ungespeichert")),
                           (_t("datei.info.groesse"), f"{groesse / 1024:.1f} KB" if groesse is not None else "–"),
                           (_t("datei.info.papier"), f"{t.page.paper_name()} {_t('datei.info.quer') if t.page.landscape else _t('datei.info.hoch')}")):
            self._zeile(v, name, QLabel(str(wert)))

    def _info_statistik(self, v, ed):
        text = ed.document().toPlainText()
        absaetze = sum(1 for z in text.split("\n") if z.strip())
        self._gruppe(v, _t("datei.info.gruppe.statistik"))
        for name, wert in ((_t("datei.info.seiten"), ed.page_count), (_t("datei.info.absaetze"), absaetze), (_t("datei.info.woerter"), ed.word_count()),
                           (_t("datei.info.zeichen"), len(text.replace(" ", "").replace("\n", ""))), (_t("datei.info.zeichen_mit"), len(text.replace("\n", "")))):
            self._zeile(v, name, QLabel(str(wert)))

    def _info_eigenschaften(self, v, t):
        self._gruppe(v, _t("datei.info.gruppe.eigenschaften"), _t("datei.info.gruppe.eigenschaften.hinweis"))
        for schl, name in (("author", _t("datei.info.verfasser")), ("title", _t("datei.info.titel_feld"))):
            e = zeilenfeld("frei", t.meta.get(schl, "") or "")
            e.editingFinished.connect(lambda e=e, s=schl, t=t: self._meta_setzen(t, s, e.text()))
            self._zeile(v, name, e)

    def _meta_setzen(self, t, schl: str, wert: str):
        if (t.meta.get(schl, "") or "") != wert:
            t.meta[schl] = wert
            t.editor.document().setModified(True)

    @staticmethod
    def _zeile(v: RasterSpalte, name: str, feld: QWidget):
        row = _reihe("standard")
        n = QLabel(name)
        n.setFixedWidth(BREITE_NAMENSFELD)
        row.addWidget(n)
        row.addWidget(feld)
        row.addStretch(1)
        v.addLayout(row)
