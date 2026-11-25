"""Optionen — das Fenster hinter „☰ Menü ▸ Optionen“ (F9): sechs Seiten in einer flachen Liste, oben eine Suche.

Lesen · Anzeige · Schreiben · Speichern · Drucken und PDF · Name und KI. Jede Seite zeigt nur das Häufige; der Rest steht unter
„Weitere Einstellungen“ (eingeklappt, mit der Tastatur erreichbar). Werte gelten sofort. Konzept: ``dokumentation/konzepte/konzept-optionen.md``.
"""
from __future__ import annotations

from vcl.qt.widgets.bausteine.bausteine.feld.feld import zeilenfeld

from vcl.qt.widgets.bausteine.basis.darstellung import grundschrift

from vcl.qt.widgets.bausteine.geruest.rollen import reihe as _reihe, spalte as _spalte

from vcl.qt.widgets.bausteine.geruest.rollen import reihe as _reihe, spalte as _spalte

from writer.baukasten.basis.daten import text as _t

from PySide6.QtCore import QEvent, QTimer, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QFrame, QLineEdit, QListWidget, QListWidgetItem, QScrollArea, QStackedWidget, QTreeWidget,
    QTreeWidgetItem, QWidget,
)

from framework.datentypen.farben import Farbe
from writer.baukasten.basis import daten
from writer.baukasten.basis.daten import text as _t
from writer.baukasten.geruest import module
from vcl.qt.widgets.bausteine.basis.beschriftung import text_label
from vcl.qt.widgets.bausteine.basis.dialog_rahmen import knopfzeile
from vcl.qt.widgets.bausteine.geruest.einklappgruppe import EinklappGruppe
from vcl.qt.widgets.bausteine.geruest.spalten import ZweiSpalter
from vcl.qt.widgets.dialoge.optionen_seiten.ansicht import AnsichtSeiten
from vcl.qt.widgets.dialoge.optionen_seiten.datei import DateiSeiten
from vcl.qt.widgets.dialoge.optionen_seiten.befehle import BefehleSeiten
from vcl.qt.widgets.dialoge.optionen_seiten.gemeinsam import erklaerung as _erklaerung
from vcl.qt.widgets.dialoge.optionen_seiten.lesen import LesenSeiten
from vcl.qt.widgets.dialoge.optionen_seiten.lunivo import LunivoSeiten
from vcl.qt.widgets.dialoge.optionen_seiten.name_ki import NameKiSeiten
from writer.baukasten.basis.mass import ABSTAND_KEIN, ABSTAND_NORMAL, BREITE_NAVIGATION_OPTIONEN, GROESSE_FENSTER_OPTIONEN, HOEHE_FELD, HOEHE_LISTE_ANBIETER, MARGIN_NAVIGATION_EINTRAG, MARGIN_OBEN_OPTIONEN_GRUPPE, PADDING_LINKS_OPTIONEN_HINWEIS, PADDING_NAVIGATION_EINTRAG, PADDING_OPTIONEN_ERKLAERUNG, PADDING_OPTIONEN_GRUPPE, PADDING_OPTIONEN_VORSCHAU, PADDING_OPTIONEN_WAHL, RADIUS_FELD, RADIUS_KARTE, RADIUS_KLEIN, RADIUS_MITTEL, RAND_BOX, RAND_KEIN, RAND_UNTEN, SCHRIFT_HINWEIS, SCHRIFT_KLEIN

ERKLAERUNG_LEER = _t("optionen.rahmen.zeig_auf_eine_einstellung_hier_steht_was")



_DATEN = daten.lade("optionen")          # Alias früherer Seitennamen und die Bereiche, die dort gleich aufklappen: Daten, kein Code
ALIAS = _DATEN.get("alias", {})
AUFKLAPPEN = _DATEN.get("aufklappen", {})

class OptionenAnsicht(LesenSeiten, AnsichtSeiten, DateiSeiten, BefehleSeiten, LunivoSeiten, NameKiSeiten, QWidget):
    """Alle Optionen als Ansicht (Liste und Suche links, Seite rechts) — sie steht in der Datei-Ansicht („☰ Menü ▸ Erweiterte
    Einstellungen“) und im Dialog `OptionenDialog`. Werte gelten sofort."""


    def __init__(self, fenster, seite: str | None = None):
        super().__init__()
        self.w = fenster
        self.setObjectName("optAnsicht")
        grundschrift(self)
        links = QWidget(); links.setObjectName("optLinks"); links.setAttribute(Qt.WA_StyledBackground, True)
        lv = _spalte("panel", links)
        self.suche = zeilenfeld("frei")
        self.suche.setPlaceholderText(_t("optionen.rahmen.einstellung_suchen")); self.suche.setToolTip(_t("optionen.rahmen.suchen_strg_f"))
        self.suche.setClearButtonEnabled(True)
        self.suche.setMinimumHeight(HOEHE_FELD)
        self.suche.setAccessibleName(_t("optionen.rahmen.einstellung_suchen_2"))
        self.treffer = QListWidget(); self.treffer.setMaximumHeight(HOEHE_LISTE_ANBIETER); self.treffer.hide()
        self.treffer.setAccessibleName(_t("optionen.rahmen.suchergebnisse"))
        self.baum = QTreeWidget()
        self.baum.setObjectName("optNavigation")
        self.baum.setHeaderHidden(True)
        self.baum.setRootIsDecorated(False)
        self.baum.setIndentation(0)
        self.baum.setFocusPolicy(Qt.StrongFocus)
        self.baum.setAccessibleName(_t("optionen.rahmen.seiten_der_optionen"))
        lv.addWidget(self.suche); lv.addWidget(self.treffer); lv.addWidget(self.baum, 1)
        self.stapel = QStackedWidget()
        self.scroll = sc = QScrollArea(); sc.setObjectName("optSeite"); sc.setWidgetResizable(True); sc.setFrameShape(QFrame.NoFrame)
        sc.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        halter = QWidget(); hl = _reihe("standard", halter)
        hl.addWidget(self.stapel)                                         # die Seite füllt die ganze Breite; ihre Kacheln ordnen sich selbst
        sc.setWidget(halter)
        rechts = QWidget(); rv = _spalte("kein", rechts)
        rv.addWidget(sc, 1)
        self.erklaerzeile = text_label(ERKLAERUNG_LEER, umbruch=True)
        self.erklaerzeile.setObjectName("optErklaerung")
        rv.addWidget(self.erklaerzeile)
        self.spalten = ZweiSpalter(links, rechts, links_breite=BREITE_NAVIGATION_OPTIONEN, oben="links", gestapelt_stretch=(1, 2))   # schmal: die Liste oben
        h = _spalte("kein", self); h.addWidget(self.spalten)
        self.knoten: dict[str, QTreeWidgetItem] = {}
        self.seiten = [(m.schluessel, _t(m.titel), getattr(self, m.bauer)) for m in module.liste("optionen")]
        for key, titel, bauen in self.seiten:
            it = QTreeWidgetItem([titel])
            it.setData(0, Qt.UserRole, key)
            it.setData(0, Qt.AccessibleDescriptionRole, _t("optionen.rahmen.seite_0_von_1").format(len(self.knoten) + 1, len(self.seiten)))
            self.baum.addTopLevelItem(it)
            self.knoten[key] = it
            self.stapel.addWidget(bauen(titel))
            it.setData(0, Qt.UserRole + 1, self.stapel.count() - 1)
        self.baum.currentItemChanged.connect(lambda cur, _p: cur and cur.data(0, Qt.UserRole + 1) is not None
                                             and self.stapel.setCurrentIndex(cur.data(0, Qt.UserRole + 1)))
        for wid in self.stapel.findChildren(QWidget):                 # Zeigen auf eine Einstellung erklärt sie unten
            wid.installEventFilter(self)
        self.suche.installEventFilter(self)
        self.suche.textChanged.connect(self._suchen)
        self.suche.returnPressed.connect(lambda: self.treffer.count() and self._springe(self.treffer.item(0)))
        self.treffer.itemActivated.connect(self._springe)
        self.treffer.itemClicked.connect(self._springe)
        sc_f = QShortcut(QKeySequence.Find, self); sc_f.setContext(Qt.WidgetWithChildrenShortcut)
        sc_f.activated.connect(lambda: (self.suche.setFocus(), self.suche.selectAll()))
        self._index: list[tuple[str, str, str, QWidget]] = []
        self._index_bauen()
        self.gehe_zu(seite or "lesen")


    def eventFilter(self, obj, ev):
        if obj is self.suche:
            if ev.type() == QEvent.KeyPress and ev.key() == Qt.Key_Down and self.treffer.count():
                self.treffer.setFocus(); self.treffer.setCurrentRow(0)
                return True
            return super().eventFilter(obj, ev)
        if ev.type() in (QEvent.Enter, QEvent.FocusIn) and isinstance(obj, QWidget):
            w = obj
            while w is not None and not w.property("optName"):
                w = w.parentWidget()
            if w is not None:
                self._erklaere(str(w.property("optName")))
        elif ev.type() == QEvent.Leave:
            self.erklaerzeile.setText(ERKLAERUNG_LEER)
        return super().eventFilter(obj, ev)


    def _erklaere(self, name: str) -> None:
        satz = _erklaerung(name)
        self.erklaerzeile.setText(f"{name} — {satz}" if satz else ERKLAERUNG_LEER)


    def gehe_zu(self, key: str):
        """Eine Seite zeigen; frühere Seitennamen führen auf die neue Seite und klappen dort den passenden Bereich auf."""
        seite = ALIAS.get(key, key)
        self.baum.setCurrentItem(self.knoten.get(seite) or self.knoten["lesen"])
        zeigen = getattr(self, "_aussehen_zeigen", None)
        if zeigen is not None:
            zeigen()                                                  # Hell/Dunkel kann inzwischen anderswo umgestellt worden sein
        vorn = AUFKLAPPEN.get(key)
        if vorn:
            for e in self.stapel.currentWidget().findChildren(EinklappGruppe):
                if e.titel.startswith(vorn):
                    e.ausklappen(True)


    # ---- Suche: findet jede Einstellung, auch die eingeklappten, und springt hin --------------------------------------------------------
    def _index_bauen(self) -> None:
        for key, titel, _b in self.seiten:
            seite = self.stapel.widget(self.knoten[key].data(0, Qt.UserRole + 1))
            gesehen: set[str] = set()
            for w in seite.findChildren(QWidget):
                text = str(w.property("optName") or "")
                if not text and isinstance(w, QCheckBox):
                    text = w.text()
                if text and text.lower() not in gesehen:
                    gesehen.add(text.lower())
                    self._index.append((key, titel, text, w))


    def _suchen(self, q: str) -> None:
        q = q.strip().lower()
        self.treffer.clear()
        if not q:
            self.treffer.hide()
            return
        for key, titel, text, w in self._index:
            if q in text.lower() or q in _erklaerung(text).lower():
                it = QListWidgetItem(f"{text}  ·  {titel}")
                it.setData(Qt.UserRole, (key, w))
                self.treffer.addItem(it)
        if not self.treffer.count():
            self.treffer.addItem(QListWidgetItem(_t("optionen.rahmen.nichts_gefunden")))
            self.treffer.item(0).setFlags(Qt.NoItemFlags)
        self.treffer.show()


    def _springe(self, it: QListWidgetItem) -> None:
        ziel = it.data(Qt.UserRole)
        if not ziel:
            return
        key, w = ziel
        self.gehe_zu(key)
        p = w.parentWidget()
        while p is not None:
            if isinstance(p, EinklappGruppe):
                p.ausklappen(True)
            p = p.parentWidget()

        def zeigen():
            self.scroll.ensureWidgetVisible(w, 0, 60)
            fokus = w if w.focusPolicy() != Qt.NoFocus else next((c for c in w.findChildren(QWidget) if c.focusPolicy() != Qt.NoFocus), None)
            if fokus is not None:
                fokus.setFocus()
        QTimer.singleShot(60, zeigen)


    # ---- Befehlslisten (Menüband, Schnellzugriff): zwei Listen mit Hinzufügen / Entfernen, wie in der Vorlage ---------------------------
    def _band_merken(self) -> None:
        """Die Änderung steht in den Einstellungen; das Band wird beim Verlassen der Seite neu gebaut (nicht bei jedem Klick)."""
        self._band_neu = True


    def _band_jetzt(self, *_a) -> None:
        if getattr(self, "_band_neu", False):
            self._band_neu = False
            QTimer.singleShot(0, self.w.neu_bauen_band)


    def hideEvent(self, ev):
        self._band_jetzt()
        super().hideEvent(ev)


class OptionenDialog(QDialog):
    """Die Optionen als eigenes Fenster (für Aufrufe außerhalb der Datei-Ansicht); gleicher Inhalt wie `OptionenAnsicht`."""

    def __init__(self, fenster, seite: str | None = None):
        super().__init__(fenster)
        self.setWindowTitle(_t("optionen.rahmen.optionen"))
        self.resize(*GROESSE_FENSTER_OPTIONEN)
        v = _spalte("aussen", self)
        self.ansicht = OptionenAnsicht(fenster, seite)
        self.baum, self.stapel, self.knoten, self.gehe_zu = self.ansicht.baum, self.ansicht.stapel, self.ansicht.knoten, self.ansicht.gehe_zu
        v.addWidget(self.ansicht, 1)
        v.addWidget(knopfzeile(self, ok_text=_t("optionen.rahmen.fertig"), nur_ok=True))
