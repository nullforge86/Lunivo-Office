"""„Suchen und Ersetzen“ in der linken Seitenleiste — aufgebaut wie das Fenster der Vorlage, aber als Feld neben dem Text:
Reiter Suchen, Ersetzen und Gehe zu. Oben das Suchfeld mit Pfeilen für vorherigen/nächsten Treffer und der Trefferzahl, im Reiter Ersetzen
das Ersatzfeld mit „Ersetzen“ und „Alle ersetzen“; darunter zwei einklappbare Abschnitte: „Suchoptionen“ (Richtung, Groß/klein …) und
„Weitere Werkzeuge“ (Format, Sonderzeichen, Hervorheben, Suchen in). Eingabe sucht weiter, Umschalt+Eingabe zurück, Esc schließt.

Unterfenster (Schriftart, Absatz, Tabstopps, Formatvorlage für „Format“) öffnen sich als Seite in derselben linken Leiste — die rechte
Seitenleiste bleibt, wie sie ist. Die Suche selbst steht ohne Oberfläche in ``editor/suche.py``, die Sprungziele in ``editor/gehe_zu.py``.
"""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextBlockFormat, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton,
    QStackedWidget, QTabBar, QToolButton, QVBoxLayout, QWidget,
)

from lunivo_writer.editor import gehe_zu as G
from lunivo_writer.editor import suche as S
from lunivo_writer.ui.baukasten.einklappgruppe import EinklappGruppe
from lunivo_writer.ui.baukasten.menue_liste import MenueListe
from lunivo_writer.ui.widgets import icons

RICHTUNGEN = (("abwaerts", "Abwärts"), ("aufwaerts", "Aufwärts"), ("alles", "Alles"))
ZEICHEN_NAMEN = {"schrift": "Schriftart", "groesse": "Größe", "fett": "Fett", "kursiv": "Kursiv", "farbe": "Schriftfarbe", "unter": "Unterstreichung",
                 "unterfarbe": "Unterstreichungsfarbe", "durch": "Durchgestrichen", "doppelt": "Doppelt durchgestrichen", "hoch": "Hochgestellt",
                 "tief": "Tiefgestellt", "kapital": "Kapitälchen", "gross": "Großbuchstaben", "abstand": "Zeichenabstand", "betonung": "Betonungszeichen",
                 "skala": "Skalieren", "position": "Position"}
ABSATZ_NAMEN = {"ausr": "Ausrichtung", "einzug": "Einzug links", "rechts": "Einzug rechts", "erste": "Erste Zeile", "vor": "Abstand vor",
                "nach": "Abstand nach", "zeilen": "Zeilenabstand", "ebene": "Gliederungsebene"}
KNOPF_H = 34


def _gleich(a, b) -> bool:
    if isinstance(a, float) or isinstance(b, float):
        try:
            return abs(float(a or 0) - float(b or 0)) < 0.06
        except (TypeError, ValueError):
            return False
    return a == b


def _format_text(f: dict) -> str:
    """„Format: Fett, Schriftart: Arial, Hervorgehoben“ — was als Bedingung an einem Feld hängt."""
    teile = []
    for k, v in f.get("zeichen", {}).items():
        n = ZEICHEN_NAMEN.get(k, k)
        teile.append(n if v is True else f"Nicht {n.lower()}" if v is False else f"{n}: {v}")
    for k, v in f.get("absatz", {}).items():
        teile.append(f"{ABSATZ_NAMEN.get(k, k)}: {v}")
    if f.get("tabs"):
        teile.append("Tabstopps: " + "; ".join(f"{m:g} mm" for m in f["tabs"]))
    if f.get("stil"):
        teile.append(f"Formatvorlage: {f['stil']}")
    if f.get("hervor") is not None:
        teile.append("Hervorgehoben" if f["hervor"] else "Nicht hervorgehoben")
    return ", ".join(teile)


def _linie() -> QFrame:
    l = QFrame(); l.setFrameShape(QFrame.HLine); l.setFrameShadow(QFrame.Plain); l.setStyleSheet("color: palette(midlight);")
    return l


class FormatvorlageWahl(QDialog):
    """Eine Formatvorlage aus der Liste wählen (für „Format ▸ Formatvorlage …“ beim Suchen und Ersetzen)."""

    def __init__(self, parent=None, aktuell: str = ""):
        super().__init__(parent)
        from lunivo_writer.editor import stile
        from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
        from lunivo_writer.ui.ribbon.ribbon_bar import STILE_KATALOG
        self.setWindowTitle("Formatvorlage suchen")
        v = QVBoxLayout(self)
        v.addWidget(QLabel("Formatvorlage:"))
        self.liste = QListWidget()
        for n in STILE_KATALOG + [n for n in stile.namen() if n not in STILE_KATALOG]:
            self.liste.addItem(n)
        treffer = self.liste.findItems(aktuell or "Standard", Qt.MatchExactly)
        self.liste.setCurrentItem(treffer[0] if treffer else self.liste.item(0))
        self.liste.itemDoubleClicked.connect(lambda _i: self.accept())
        v.addWidget(self.liste, 1)
        fussleiste(self, v)

    def name(self) -> str:
        return self.liste.currentItem().text() if self.liste.currentItem() else ""


class SuchenFeld(QWidget):
    """Inhalt des Feldes „Suchen und ersetzen“. ``unterfenster(dialog) -> bool`` zeigt ein Unterfenster in der linken Leiste (wie ``exec``)."""
    schliessen = Signal()

    def __init__(self, get_editor: Callable, unterfenster: Callable[[QDialog], bool]):
        super().__init__()
        self.get_editor, self.unterfenster = get_editor, unterfenster
        self.hervorheben = True                    # Lesehervorhebung: alle Treffer farbig hinterlegt
        self.bereich: tuple[int, int] | None = None # „Suchen in ▸ Aktuelle Auswahl“
        self.formate: dict[str, dict] = {"suchen": {}, "ersetzen": {}}
        self._fokus = "suchen"                    # für welches Feld „Format“ und „Spezial“ gelten
        v = QVBoxLayout(self); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(8)
        self.reiter = QTabBar(); self.reiter.setExpanding(False); self.reiter.setDrawBase(True)
        for t in ("Suchen", "Ersetzen", "Gehe zu"):
            self.reiter.addTab(t)
        v.addWidget(self.reiter)
        self.seiten = QStackedWidget(); v.addWidget(self.seiten, 1)
        self.seiten.addWidget(self._bau_suchen())
        self.seiten.addWidget(self._bau_gehe_zu())
        self.reiter.currentChanged.connect(self._reiter)
        self._reiter(0)

    # ---- Aufbau: Suchen und Ersetzen ----------------------------------------------------------------------------------------------
    def _feld(self) -> QComboBox:
        c = QComboBox(); c.setEditable(True); c.setInsertPolicy(QComboBox.NoInsert); c.setMinimumHeight(KNOPF_H)
        c.lineEdit().setClearButtonEnabled(True)
        return c

    def _knopf(self, text: str, menue: MenueListe | None = None) -> QPushButton:
        k = QPushButton(text); k.setMinimumHeight(KNOPF_H)
        if menue is not None:
            k.setMenu(menue)
        return k

    def _sprung(self, symbol: str, tipp: str) -> QToolButton:
        """Pfeilknopf neben dem Suchfeld (vorheriger/nächster Treffer) — quadratisch, so hoch wie das Feld."""
        k = QToolButton(); k.setIcon(icons.icon(symbol, 18)); k.setFixedSize(KNOPF_H + 2, KNOPF_H + 2)
        k.setToolTip(tipp); k.setAccessibleName(tipp)
        return k

    @staticmethod
    def _titel(text: str, feld: QWidget) -> QLabel:
        l = QLabel(text); l.setBuddy(feld)
        f = l.font(); f.setBold(True); l.setFont(f)
        return l

    def _bau_suchen(self) -> QWidget:
        """Aufbau von oben nach unten: was man sucht (Feld, Pfeile, Trefferzahl), was man einsetzt (nur Reiter Ersetzen), dann zwei
        einklappbare Abschnitte — „Suchoptionen“ und „Weitere Werkzeuge“ —, damit nicht alle Knöpfe auf einmal dastehen."""
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 0); v.setSpacing(6)
        # 1. Suchen nach: Feld mit Pfeilen, darunter die Treffer
        self.such_combo = self._feld(); self.suchfeld = self.such_combo.lineEdit(); self.suchfeld.setPlaceholderText("Suchbegriff eingeben")
        self.such_combo.setAccessibleName("Suchen nach")
        v.addWidget(self._titel("Suchen &nach", self.such_combo))
        z = QHBoxLayout(); z.setSpacing(4)
        self.vorherige = self._sprung("trefferHoch", "Vorherigen Treffer suchen (Umschalt+Eingabe)")
        self.weiter = self._sprung("trefferRunter", "Nächsten Treffer suchen (Eingabe)")
        z.addWidget(self.such_combo, 1); z.addWidget(self.vorherige); z.addWidget(self.weiter)
        v.addLayout(z)
        self.treffer = QLabel("Keine Suchergebnisse"); self.treffer.setStyleSheet("color: palette(mid);"); self.treffer.setWordWrap(True)
        self.treffer.setAccessibleName("Suchergebnis")
        v.addWidget(self.treffer)
        self.such_format = QLabel(); self.such_format.setWordWrap(True); v.addWidget(self.such_format)
        # 2. Ersetzen durch (nur im Reiter Ersetzen)
        self.ersatz_bereich = QWidget(); ev = QVBoxLayout(self.ersatz_bereich); ev.setContentsMargins(0, 8, 0, 0); ev.setSpacing(6)
        self.ersatz_combo = self._feld(); self.ersatzfeld = self.ersatz_combo.lineEdit(); self.ersatzfeld.setPlaceholderText("Ersatztext eingeben")
        self.ersatz_combo.setAccessibleName("Ersetzen durch")
        self.ersatz_titel = self._titel("Ersetzen &durch", self.ersatz_combo)
        ev.addWidget(self.ersatz_titel); ev.addWidget(self.ersatz_combo)
        self.ersatz_format = QLabel(); self.ersatz_format.setWordWrap(True); ev.addWidget(self.ersatz_format)
        self.ersetz_zeile = QWidget(); ez = QHBoxLayout(self.ersetz_zeile); ez.setContentsMargins(0, 0, 0, 0); ez.setSpacing(6)
        self.ersetzen = self._knopf("&Ersetzen"); self.alle_ersetzen = self._knopf("&Alle ersetzen")
        ez.addWidget(self.ersetzen, 1); ez.addWidget(self.alle_ersetzen, 1)
        ev.addWidget(self.ersetz_zeile)
        v.addWidget(self.ersatz_bereich)
        v.addWidget(_linie())
        # 3. Suchoptionen (eingeklappt; die Zusammenfassung zeigt, was gerade gilt)
        self.optionen_gruppe = EinklappGruppe("Suchoptionen")
        self.erweitern = self.optionen_gruppe.knopf
        self.optionen_text = QLabel(); self.optionen_text.setWordWrap(True); self.optionen_text.setStyleSheet("color: palette(mid);")
        self.optionen = self.optionen_gruppe.inhalt
        ov = self.optionen_gruppe.innen; ov.setSpacing(4)
        rz = QHBoxLayout(); self.richtung = QComboBox(); self.richtung.setMinimumHeight(KNOPF_H)
        for k, t in RICHTUNGEN:
            self.richtung.addItem(t, k)
        rl = QLabel("Such&richtung:"); rl.setBuddy(self.richtung)
        rz.addWidget(rl); rz.addWidget(self.richtung, 1); ov.addLayout(rz)
        self.gross = QCheckBox("Groß-/Kleinschreibung beachten"); self.ganz = QCheckBox("Nur ganzes Wort suchen")
        self.platzhalter = QCheckBox("Platzhalter verwenden"); self.praefix = QCheckBox("Präfix beachten"); self.suffix = QCheckBox("Suffix beachten")
        self.satzzeichen = QCheckBox("Interpunktionszeichen ignorieren"); self.leerzeichen = QCheckBox("Leerzeichen ignorieren")
        for c in (self.gross, self.ganz, self.platzhalter, self.praefix, self.suffix, self.satzzeichen, self.leerzeichen):
            c.setMinimumHeight(28); ov.addWidget(c); c.toggled.connect(lambda _a: self._optionen_neu())
        v.addWidget(self.optionen_gruppe)
        v.addWidget(self.optionen_text)
        self.erweitern.toggled.connect(lambda offen: self.optionen_text.setVisible(not offen))   # eingeklappt: kurz, was gilt
        # 4. Weitere Werkzeuge: Format, Spezial, Lesehervorhebung, Suchen in — zwei Reihen zu je zwei Knöpfen
        self.werkzeuge = EinklappGruppe("Weitere Werkzeuge")
        g = QGridLayout(); g.setSpacing(6)
        self.format_menue = MenueListe(self); self.format_menue.aboutToShow.connect(self._format_menue_fuellen)
        self.spezial_menue = MenueListe(self); self.spezial_menue.aboutToShow.connect(self._spezial_menue_fuellen)
        self.format_knopf = self._knopf("Format", self.format_menue); self.spezial_knopf = self._knopf("Sonderzeichen", self.spezial_menue)
        self.format_knopf.setToolTip("Nach Schrift, Absatz, Tabstopps, Formatvorlage oder Hervorhebung suchen")
        self.spezial_knopf.setToolTip("Absatzmarke, Tabstopp, Platzhalter und andere Sonderzeichen einfügen")
        lese = MenueListe(self)
        lese.eintrag("Alle hervorheben", lambda: self._hervorheben(True))
        lese.eintrag("Hervorhebung löschen", lambda: self._hervorheben(False))
        self.suchen_in = MenueListe(self); self.suchen_in.aboutToShow.connect(self._suchen_in_fuellen)
        self.lese_knopf = self._knopf("Hervorheben", lese); self.in_knopf = self._knopf("Suchen in", self.suchen_in)
        self.lese_knopf.setToolTip("Lesehervorhebung: alle Treffer farbig hinterlegen oder die Hervorhebung löschen")
        self.in_knopf.setToolTip("Im ganzen Dokument oder nur in der aktuellen Auswahl suchen")
        g.addWidget(self.format_knopf, 0, 0); g.addWidget(self.spezial_knopf, 0, 1)
        g.addWidget(self.lese_knopf, 1, 0); g.addWidget(self.in_knopf, 1, 1)
        self.lese_zeile = self.lese_knopf
        self.werkzeuge.innen.addLayout(g)
        v.addWidget(self.werkzeuge)
        v.addStretch(1)
        # Verbindungen
        self.suchfeld.textChanged.connect(lambda _t: (self._optionen_neu(), self.zaehlen()))
        self.ersatzfeld.returnPressed.connect(self.ersetzen_eins)
        for feld, name in ((self.suchfeld, "suchen"), (self.ersatzfeld, "ersetzen")):
            feld.installEventFilter(self); feld.setProperty("such_rolle", name)
        self.richtung.currentIndexChanged.connect(lambda _i: self._optionen_neu())
        self.vorherige.clicked.connect(lambda: self.weitersuchen(True)); self.weiter.clicked.connect(lambda: self.weitersuchen(False))
        self.ersetzen.clicked.connect(self.ersetzen_eins); self.alle_ersetzen.clicked.connect(self.ersetzen_alle)
        # Tab-Reihenfolge wie die Leserichtung: Feld, Pfeile, Ersatzfeld, Ersetzen-Knöpfe, Abschnitte
        kette = [self.such_combo, self.vorherige, self.weiter, self.ersatz_combo, self.ersetzen, self.alle_ersetzen, self.erweitern,
                 self.richtung, self.gross, self.ganz, self.platzhalter, self.praefix, self.suffix, self.satzzeichen, self.leerzeichen,
                 self.werkzeuge.knopf, self.format_knopf, self.spezial_knopf, self.lese_knopf, self.in_knopf]
        for x, y in zip(kette, kette[1:]):
            QWidget.setTabOrder(x, y)
        self._optionen_neu()
        return w

    def eventFilter(self, obj, e) -> bool:
        if e.type() == e.Type.FocusIn and obj.property("such_rolle"):
            self._fokus = obj.property("such_rolle")
        if e.type() == e.Type.KeyPress and obj is self.suchfeld and e.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.weitersuchen(bool(e.modifiers() & Qt.ShiftModifier))
            return True
        return super().eventFilter(obj, e)

    def keyPressEvent(self, e) -> None:
        if e.key() == Qt.Key_Escape:                                # Esc schließt das Feld (wie das ✕ oben)
            self.schliessen.emit(); return
        super().keyPressEvent(e)

    # ---- Aufbau: Gehe zu ---------------------------------------------------------------------------------------------------------
    def _bau_gehe_zu(self) -> QWidget:
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(6)
        self.elemente = QListWidget(); self.elemente.addItems(list(G.ELEMENTE)); self.elemente.setCurrentRow(0)
        self.elemente.setAccessibleName("Gehe zu Element")
        v.addWidget(self._titel("Gehe zu &Element", self.elemente))
        self.elemente.setMinimumHeight(self.elemente.sizeHintForRow(0) * len(G.ELEMENTE) + 8)          # alle Elemente ohne Rollen
        v.addWidget(self.elemente)
        self.eingabe = QLineEdit(); self.eingabe.setMinimumHeight(KNOPF_H)
        self.eingabe_titel = QLabel(G.EINGABE["Seite"]); self.eingabe_titel.setBuddy(self.eingabe)
        v.addWidget(self.eingabe_titel); v.addWidget(self.eingabe)
        hilfe = QLabel("Geben Sie + und – ein, um sich relativ zur derzeitigen Position zu bewegen.\nBeispiel: Mit +4 springen Sie um vier "
                       "Elemente weiter.")
        hilfe.setWordWrap(True); hilfe.setStyleSheet("color: palette(mid);"); v.addWidget(hilfe)
        self.gehe_meldung = QLabel(); self.gehe_meldung.setStyleSheet("color: palette(mid);"); self.gehe_meldung.setWordWrap(True)
        v.addWidget(self.gehe_meldung)
        z = QHBoxLayout()
        self.zurueck = self._knopf("Zurück"); self.gehe_weiter = self._knopf("Weiter"); self.gehe_weiter.setDefault(True)
        for k in (self.zurueck, self.gehe_weiter):
            z.addWidget(k, 1)
        v.addLayout(z); v.addStretch(1)
        self.elemente.currentTextChanged.connect(self._element_gewaehlt)
        self.eingabe.textChanged.connect(lambda t: self.gehe_weiter.setText("Gehe zu" if t.strip() else "Weiter"))
        self.eingabe.textChanged.connect(lambda _t: self.zurueck.setEnabled(not self.eingabe.text().strip()))
        self.eingabe.returnPressed.connect(lambda: self.gehe(1))
        self.zurueck.clicked.connect(lambda: self.gehe(-1)); self.gehe_weiter.clicked.connect(lambda: self.gehe(1))
        return w

    def _element_gewaehlt(self, t: str) -> None:
        self.eingabe_titel.setText(G.EINGABE.get(t, "Nummer eingeben:")); self.gehe_meldung.clear()

    def gehe(self, richtung: int) -> None:
        ed = self.get_editor()
        if ed is None:
            return
        art = self.elemente.currentItem().text() if self.elemente.currentItem() else "Seite"
        pos = G.ziel(ed, art, self.eingabe.text(), richtung)
        if pos is None:
            self.gehe_meldung.setText(f"Kein Element „{art}“ an dieser Stelle." if G.positionen(ed, art) else f"Das Dokument enthält kein Element „{art}“.")
            return
        self.gehe_meldung.clear()
        G.springen(ed, pos)

    # ---- Steuerung ------------------------------------------------------------------------------------------------------------------
    def zeige(self, reiter: str = "Suchen", element: str = "") -> None:
        """Reiter „Suchen“, „Ersetzen“ oder „Gehe zu“ zeigen; bei „Gehe zu“ optional das Element (Seite, Abschnitt …) wählen."""
        i = {"Suchen": 0, "Ersetzen": 1, "Gehe zu": 2}.get(reiter, 0)
        self.reiter.setCurrentIndex(i); self._reiter(i)
        if i == 2:
            gef = self.elemente.findItems({"Bild": "Grafik"}.get(element, element) or "Seite", Qt.MatchExactly)
            if gef:
                self.elemente.setCurrentItem(gef[0])
            self.eingabe.setFocus(); self.eingabe.selectAll()
        else:
            self.suchfeld.setFocus(); self.suchfeld.selectAll()

    def _reiter(self, i: int) -> None:
        self.seiten.setCurrentIndex(1 if i == 2 else 0)
        ersetzen = i == 1
        self.ersatz_bereich.setVisible(ersetzen)
        self.ersatz_format.setVisible(ersetzen and bool(self.formate["ersetzen"]))
        if not ersetzen and self._fokus == "ersetzen":
            self._fokus = "suchen"

    def _optionen_neu(self) -> None:
        pl = self.platzhalter.isChecked()
        sonder = "^" in self.suchfeld.text()
        self.ganz.setEnabled(not pl and not sonder)
        for c in (self.praefix, self.suffix):
            c.setEnabled(not pl and not sonder)
        for c in (self.satzzeichen, self.leerzeichen):
            c.setEnabled(not pl)
        teile = [self.richtung.currentText()]
        for c in (self.gross, self.ganz, self.platzhalter, self.praefix, self.suffix, self.satzzeichen, self.leerzeichen):
            if c.isChecked() and c.isEnabled():
                teile.append(c.text())
        if self.bereich is not None:
            teile.append("Aktuelle Auswahl")
        self.optionen_text.setText("Gilt jetzt: " + ", ".join(teile))
        for feld, label in (("suchen", self.such_format), ("ersetzen", self.ersatz_format)):
            t = _format_text(self.formate[feld])
            label.setText("Format: " + t if t else ""); label.setVisible(bool(t) and (feld == "suchen" or self.reiter.currentIndex() == 1))

    # ---- Auftrag --------------------------------------------------------------------------------------------------------------------
    def auftrag(self) -> S.Suchauftrag:
        pl = self.platzhalter.isChecked()
        ein = lambda c: c.isChecked() and c.isEnabled()      # noqa: E731
        a = S.Suchauftrag(self.suchfeld.text(), gross=self.gross.isChecked() or pl, ganz=ein(self.ganz), platzhalter=pl, praefix=ein(self.praefix),
                          suffix=ein(self.suffix), ohne_satzzeichen=ein(self.satzzeichen), ohne_leerzeichen=ein(self.leerzeichen))
        self._bedingungen(a, self.formate["suchen"])
        return a

    def _bedingungen(self, a: S.Suchauftrag, f: dict) -> None:
        ed = self.get_editor()
        if f.get("zeichen"):
            from lunivo_writer.ui.baukasten.text_format import aus_format
            soll = dict(f["zeichen"])
            fam, gr = (ed.document().defaultFont().family(), ed.document().defaultFont().pointSizeF()) if ed is not None else ("", 0.0)
            a.zeichen.append(lambda cf: (lambda w: all(_gleich(w.get(k), v) for k, v in soll.items()))(aus_format(cf, fam, gr)))
        if f.get("hervor") is not None:
            an = f["hervor"]
            a.zeichen.append(lambda cf: (cf.background().style() != Qt.NoBrush) == an)
        if f.get("absatz"):
            from lunivo_writer.ui.baukasten.absatz_dialog import aus_block
            soll_a = dict(f["absatz"])
            a.absatz.append(lambda b: (lambda w: all(_gleich(w.get(k), v) for k, v in soll_a.items()))(aus_block(b.blockFormat())))
        if f.get("tabs"):
            from lunivo_writer.ui.baukasten.tabstopp_dialog import aus_block as tabs
            soll_t = list(f["tabs"])
            a.absatz.append(lambda b: all(any(abs(m - t[0]) < 0.6 for t in tabs(b.blockFormat())) for m in soll_t))
        if f.get("stil") and ed is not None:
            name = f["stil"]
            a.absatz.append(lambda b: ed._stil_name(b.blockFormat()) == name)

    def _ersatz_formate(self):
        """Zeichenformat und Absatz-Änderung für „Ersetzen durch“ (aus „Format“ am Ersetzen-Feld)."""
        f = self.formate["ersetzen"]
        cf = None
        if f.get("zeichen_format") is not None or f.get("hervor") is not None:
            cf = QTextCharFormat(f["zeichen_format"]) if f.get("zeichen_format") is not None else QTextCharFormat()
            if f.get("hervor") is True:
                from PySide6.QtGui import QColor
                cf.setBackground(QColor("#ffec99"))
            elif f.get("hervor") is False:
                cf.clearBackground()
        ed = self.get_editor()

        def absatz(c: QTextCursor) -> None:
            if f.get("absatz_format") is not None:
                c.mergeBlockFormat(f["absatz_format"])
            if f.get("tabs"):
                from lunivo_writer.ui.baukasten.tabstopp_dialog import zu_block
                bf = c.blockFormat(); zu_block(bf, [(m, "links", "") for m in f["tabs"]]); c.setBlockFormat(bf)
            if f.get("stil") and ed is not None:
                ed._stil_auf_block(c.block(), f["stil"])
        return cf, (absatz if (f.get("absatz_format") is not None or f.get("tabs") or f.get("stil")) else None)

    # ---- Suchen ---------------------------------------------------------------------------------------------------------------------
    def _bereich(self) -> tuple[int, int | None]:
        return self.bereich if self.bereich is not None else (0, None)

    def zaehlen(self) -> list[tuple[int, int]]:
        ed = self.get_editor()
        a = self.auftrag()
        if ed is None or a.leer:
            self.treffer.setText("Keine Suchergebnisse")
            if ed is not None:
                ed.set_suchtreffer([])
            return []
        if not S.gueltig(a):
            self.treffer.setText("Der Suchtext enthält ungültige Platzhalter.")
            ed.set_suchtreffer([])
            return []
        von, bis = self._bereich()
        alle = S.treffer(ed.document(), a, von, bis)
        ed.set_suchtreffer(alle if self.hervorheben else [])
        if not alle:
            self.treffer.setText("Keine Suchergebnisse")
            return alle
        sel = ed.textCursor()
        nr = next((i + 1 for i, t in enumerate(alle) if t == (sel.selectionStart(), sel.selectionEnd())), 0)
        self.treffer.setText(f"{nr} von {len(alle)}" if nr else f"{len(alle)} Treffer")
        return alle

    def weitersuchen(self, vorherige: bool = False) -> bool:
        """„Weitersuchen“ (in der eingestellten Richtung) oder „Vorherige suchen“ (entgegen). Abwärts und Aufwärts halten am Ende an,
        „Alles“ läuft herum."""
        ed = self.get_editor()
        a = self.auftrag()
        if ed is None or a.leer or not S.gueltig(a):
            return False
        self._merken(self.such_combo)
        richtung = self.richtung.currentData()
        rueck = (richtung == "aufwaerts") != vorherige
        c = ed.textCursor()
        ab = c.selectionStart() if rueck else (c.selectionEnd() if c.hasSelection() else c.position())
        von, bis = self._bereich()
        t = S.naechster(ed.document(), a, ab, rueck, von, bis, umlauf=richtung == "alles" or self.bereich is not None)
        if t is None:
            self.treffer.setText("Das Ende des Dokuments ist erreicht." if not rueck else "Der Anfang des Dokuments ist erreicht.")
            if not S.treffer(ed.document(), a, von, bis):
                self.treffer.setText("Keine Suchergebnisse")
            return False
        self._waehle(ed, t)
        ed.ensureCursorVisible()
        self.zaehlen()
        return True

    @staticmethod
    def _waehle(ed, t) -> None:
        c = QTextCursor(ed.document()); c.setPosition(t[0]); c.setPosition(t[1], QTextCursor.KeepAnchor); ed.setTextCursor(c)

    def _merken(self, combo: QComboBox) -> None:
        t = combo.currentText()
        if t and combo.findText(t) < 0:
            combo.insertItem(0, t)
            combo.setCurrentIndex(0)

    def ersetzen_eins(self) -> None:
        ed = self.get_editor()
        a = self.auftrag()
        if ed is None or a.leer:
            return
        self._merken(self.ersatz_combo)
        c = ed.textCursor()
        sel = (c.selectionStart(), c.selectionEnd())
        von, bis = self._bereich()
        if c.hasSelection() and sel in S.treffer(ed.document(), a, von, bis):
            cf, absatz = self._ersatz_formate()
            roh = S.roh_text(ed.document())[sel[0]:sel[1]]
            neu = S.ersatz_text(a, self.ersatzfeld.text(), roh, QApplication.clipboard().text())
            k = QTextCursor(ed.document()); k.beginEditBlock()
            ende = S.ersetzen(ed.document(), sel[0], sel[1], neu, cf, absatz)
            k.endEditBlock()
            c = QTextCursor(ed.document()); c.setPosition(ende); ed.setTextCursor(c)
        self.weitersuchen(False)

    def ersetzen_alle(self) -> int:
        ed = self.get_editor()
        a = self.auftrag()
        if ed is None or a.leer or not S.gueltig(a):
            return 0
        self._merken(self.ersatz_combo)
        cf, absatz = self._ersatz_formate()
        von, bis = self._bereich()
        n = S.alle_ersetzen(ed.document(), a, self.ersatzfeld.text(), von, bis, cf, absatz, QApplication.clipboard().text())
        self.zaehlen()
        self.treffer.setText(f"{n} Ersetzung(en)" if n else "Keine Suchergebnisse")
        return n

    def _hervorheben(self, an: bool) -> None:
        self.hervorheben = an
        self.zaehlen()

    def _suchen_in_fuellen(self) -> None:
        m = self.suchen_in; m.clear()
        ed = self.get_editor()
        auswahl = ed is not None and ed.textCursor().hasSelection() and self.bereich is None
        m.eintrag("Aktuelle Auswahl", lambda: self._suchen_in(True), aktiv=auswahl or self.bereich is not None, haken=self.bereich is not None)
        m.eintrag("Hauptdokument", lambda: self._suchen_in(False), haken=self.bereich is None)

    def _suchen_in(self, auswahl: bool) -> None:
        """Wie in der Vorlage: alle Treffer im gewählten Teil finden und zeigen; „Aktuelle Auswahl“ begrenzt auch die weitere Suche."""
        ed = self.get_editor()
        if ed is None:
            return
        if auswahl and self.bereich is None:
            c = ed.textCursor(); self.bereich = (c.selectionStart(), c.selectionEnd())
        elif not auswahl:
            self.bereich = None
        self.hervorheben = True
        self._optionen_neu()
        alle = self.zaehlen()
        if alle:
            self.treffer.setText(f"{len(alle)} Treffer " + ("in der Auswahl" if self.bereich else "im Dokument"))

    # ---- Format und Spezial ---------------------------------------------------------------------------------------------------------
    def _format_menue_fuellen(self) -> None:
        m = self.format_menue; m.clear()
        m.eintrag("Schriftart …", self._format_schrift)
        m.eintrag("Absatz …", self._format_absatz)
        m.eintrag("Tabstopps …", self._format_tabs)
        m.eintrag("Formatvorlage …", self._format_stil)
        m.eintrag("Hervorheben", self._format_hervor)
        m.trenner()
        m.eintrag("Formatierung löschen", self._format_loeschen, aktiv=bool(self.formate[self._fokus]))

    def _spezial_menue_fuellen(self) -> None:
        m = self.spezial_menue; m.clear()
        liste = S.SPEZIAL_ERSETZEN if self._fokus == "ersetzen" else S.SPEZIAL
        for name, code in liste:
            m.eintrag(name, lambda c=code: self._spezial(c))

    def _spezial(self, code: str) -> None:
        feld = self.ersatzfeld if self._fokus == "ersetzen" else self.suchfeld
        feld.insert(code); feld.setFocus()

    def _geaendert(self) -> None:
        self._optionen_neu(); self.zaehlen()

    def _format_schrift(self) -> None:
        from lunivo_writer.ui.baukasten.schriftart_dialog import SchriftartDialog
        from lunivo_writer.ui.baukasten.text_format import ZEICHEN, aus_format, zu_format
        d = SchriftartDialog(self)
        vorher = d.werte()
        if not self.unterfenster(d):
            return
        nachher = d.werte()
        schluessel = set(aus_format(QTextCharFormat()))
        neu = {k: v for k, v in nachher.items() if k in schluessel and not _gleich(v, vorher.get(k))}
        f = self.formate[self._fokus]
        f["zeichen"] = {**f.get("zeichen", {}), **neu}
        if self._fokus == "ersetzen":                       # nur die geänderten Eigenschaften kommen auf den Ersatztext
            alt, ganz = zu_format({**ZEICHEN, **vorher}), zu_format({**ZEICHEN, **nachher})
            alt_p = alt.properties()
            cf = QTextCharFormat(f["zeichen_format"]) if f.get("zeichen_format") is not None else QTextCharFormat()
            for pid, wert in ganz.properties().items():
                if alt_p.get(pid) != wert:
                    cf.setProperty(pid, wert)
            f["zeichen_format"] = cf
        self._geaendert()

    def _format_absatz(self) -> None:
        from lunivo_writer.ui.baukasten.absatz_dialog import AbsatzDialog, aus_block
        d = AbsatzDialog(self, aus_block(QTextBlockFormat()))
        vorher = d.werte()
        if not self.unterfenster(d):
            return
        nachher = d.werte()
        neu = {k: v for k, v in nachher.items() if k in ABSATZ_NAMEN and not _gleich(v, vorher.get(k))}
        f = self.formate[self._fokus]
        f["absatz"] = {**f.get("absatz", {}), **neu}
        if self._fokus == "ersetzen":
            f["absatz_format"] = _absatz_format(f["absatz"])
        self._geaendert()

    def _format_tabs(self) -> None:
        from lunivo_writer.ui.baukasten.tabstopp_dialog import TabstoppDialog
        d = TabstoppDialog(self, [])
        if self.unterfenster(d) and d.stopps():
            self.formate[self._fokus]["tabs"] = [m for m, _a, _f in d.stopps()]
            self._geaendert()

    def _format_stil(self) -> None:
        d = FormatvorlageWahl(self, self.formate[self._fokus].get("stil", ""))
        if self.unterfenster(d) and d.name():
            self.formate[self._fokus]["stil"] = d.name()
            self._geaendert()

    def _format_hervor(self) -> None:
        """Wie in der Vorlage: erster Klick „Hervorgehoben“, zweiter „Nicht hervorgehoben“, dritter ohne Bedingung."""
        f = self.formate[self._fokus]
        f["hervor"] = {None: True, True: False, False: None}[f.get("hervor")]
        if f["hervor"] is None:
            f.pop("hervor")
        self._geaendert()

    def _format_loeschen(self) -> None:
        self.formate[self._fokus] = {}
        self._geaendert()


def _absatz_format(w: dict) -> QTextBlockFormat:
    """Die geänderten Absatzwerte als Absatzformat (für „Ersetzen durch“): nur, was im Fenster geändert wurde."""
    from lunivo_writer.models.page import mm_to_px
    bf = QTextBlockFormat()
    if "ausr" in w:
        bf.setAlignment({"mitte": Qt.AlignHCenter, "rechts": Qt.AlignRight, "block": Qt.AlignJustify}.get(w["ausr"], Qt.AlignLeft))
    if "einzug" in w:
        bf.setLeftMargin(mm_to_px(w["einzug"]))
    if "rechts" in w:
        bf.setRightMargin(mm_to_px(w["rechts"]))
    if "erste" in w:
        bf.setTextIndent(mm_to_px(w["erste"]))
    if "vor" in w:
        bf.setTopMargin(w["vor"] / 0.75)
    if "nach" in w:
        bf.setBottomMargin(w["nach"] / 0.75)
    if "zeilen" in w:
        bf.setLineHeight(w["zeilen"] * 100, QTextBlockFormat.LineHeightTypes.ProportionalHeight.value)
    if "ebene" in w:
        bf.setHeadingLevel(int(w["ebene"]))
    return bf
