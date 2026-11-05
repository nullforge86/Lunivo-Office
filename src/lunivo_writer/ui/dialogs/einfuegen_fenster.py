"""Kleine Fenster des Reiters Einfügen nach den Vorlagen: „Zahl“, „Felder“, „Text in Tabelle umwandeln“, „Tabelle in Text konvertieren“.

    d = ZahlDialog(parent)                 # if d.exec(): d.ergebnis() → "XIV"
    d = FelderDialog(parent, kontext)      # if d.exec(): d.feld() → (Anweisung, Ergebnis)
    d = TrennerDialog(parent, zu_tabelle=True, texte=[…])   # if d.exec(): d.trenner(), d.spalten()

Die Fenster ändern das Dokument nicht; der Aufrufer (``Befehle``) fügt das Ergebnis ein.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup, QComboBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QRadioButton, QSpinBox, QVBoxLayout, QWidget,
)

from lunivo_writer.ui.baukasten.texte import hinweis_stil
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig
from lunivo_writer.editor import felder as F
from lunivo_writer.editor import tabelle_text as TT
from lunivo_writer.editor import zahlformat as Z
from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
from lunivo_writer.ui.baukasten.formular_gitter import FlussLayout, FormularGitter, UmbruchSchalter, abschnittstitel
from lunivo_writer.ui.baukasten.mass import (
    BREITE_SCHIENE,
    BREITE_SEITENLEISTE,
    GROESSE_KNOPF_QUADRAT,
    GROESSE_RASTER_DATEIEN,
    HOEHE_EINGABE_TEXT,
    HOEHE_KNOPF,
    HOEHE_KNOPF_GROSS,
    HOEHE_KNOPF_HOCH,
    HOEHE_LISTE_MITTEL,
    ICON_GROSS,
    ICON_LISTE,
    RAND_KEIN,
    ZUGABE_LISTE,
)
from lunivo_writer.ui.baukasten.auswahlfeld import Auswahlfeld


def _titel(text: str, feld) -> QLabel:
    t = QLabel(text); t.setBuddy(feld)
    return t


class ZahlDialog(PanelFaehig, QDialog):
    """Feld „Zahl“, darunter die Liste „Zahlentyp“ (wie die Vorlage „Zahl“)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zahl")
        v = QVBoxLayout(self)
        self.zahl = QLineEdit(); self.zahl.setMinimumHeight(HOEHE_KNOPF); self.zahl.setAccessibleName("Zahl")
        v.addWidget(_titel("&Zahl", self.zahl)); v.addWidget(self.zahl)
        self.typ = QListWidget(); self.typ.setAccessibleName("Zahlentyp")
        for k, t in Z.TYPEN:
            it = QListWidgetItem(t); it.setData(Qt.UserRole, k); self.typ.addItem(it)
        self.typ.setCurrentRow(0)
        self.typ.setMinimumHeight(self.typ.sizeHintForRow(0) * 5 + ZUGABE_LISTE)
        v.addWidget(_titel("Zahlen&typ", self.typ)); v.addWidget(self.typ)
        self.hinweis = QLabel(""); hinweis_stil(self.hinweis); self.hinweis.setWordWrap(True)
        v.addWidget(self.hinweis)
        self.ok = fussleiste(self, v, bei_ok=self._pruefen)
        self.typ.itemDoubleClicked.connect(lambda _i: self._pruefen())
        self.zahl.textChanged.connect(lambda _t: self.hinweis.setText(""))
        self.resize(BREITE_SEITENLEISTE, 0)

    def ergebnis(self) -> str:
        """Die Zahl im gewählten Typ; ``ValueError`` bei falscher Eingabe."""
        text = self.zahl.text().strip().replace(".", "")
        if not text.isdigit():
            raise ValueError("Bitte eine ganze Zahl eingeben.")
        return Z.zahl_text(int(text), self.typ.currentItem().data(Qt.UserRole))

    def _pruefen(self) -> None:
        try:
            self.ergebnis()
        except ValueError as e:
            self.hinweis.setText(str(e)); self.zahl.setFocus()
            return
        self.accept()


class FelderDialog(PanelFaehig, QDialog):
    """„Felder“ wie in der Vorlage: links „Feld auswählen“ mit den Feldnamen, rechts „Feldeigenschaften“ mit Feldfunktionen,
    Assistent (je Feld eigene Felder), Beschreibung und „Formatierung bei Aktualisierung beibehalten“. OK ist grau, solange die
    Feldfunktion nichts ergibt (z. B. eine Formel nur aus „=“)."""

    def __init__(self, parent=None, kontext: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Felder")
        self.kontext = kontext or {}
        self._sperre = False
        v = QVBoxLayout(self)
        g = FormularGitter(); v.addLayout(g, 1)
        g.breit(abschnittstitel("Feld auswählen"))
        self.liste = QListWidget(); self.liste.setAccessibleName("Feldnamen"); self.liste.addItems(list(F.FELDER))
        g.zeile(_titel("Feldna&men:", self.liste), self.liste)
        g.breit(abschnittstitel("Feldeigenschaften"))
        self.anweisung = QLineEdit()
        self.anweisung.setAccessibleName("Feldfunktionen")
        g.zeile(_titel("&Feldfunktionen:", self.anweisung), self.anweisung)
        g.breit(QLabel("Assistent:"))
        self._assistent_platz = QVBoxLayout(); self._assistent_platz.setContentsMargins(*RAND_KEIN)     # wird je Feld neu gefüllt
        self._assistent = self._assistent_host = None
        g.breit(self._assistent_platz)
        g.breit(QLabel("Beschreibung:"))
        self.beschreibung = QLabel(); self.beschreibung.setWordWrap(True); hinweis_stil(self.beschreibung)
        g.breit(self.beschreibung)
        self.formatierung = UmbruchSchalter("Formatierung bei Aktualisierung &beibehalten"); self.formatierung.setChecked(True)
        g.breit(self.formatierung)
        self.ok = fussleiste(self, v)
        self._felder: dict[str, QWidget] = {}
        self.liste.currentTextChanged.connect(self._zeigen)
        self.liste.itemDoubleClicked.connect(lambda _i: self.ok.isEnabled() and self.accept())
        self.anweisung.textChanged.connect(self._pruefen)
        self.liste.setCurrentRow(0)

    def kompakt_machen(self) -> None:
        """In der Seitenleiste: die Feldnamen als Liste von begrenzter Höhe."""
        self.liste.setFixedHeight(self.liste.sizeHintForRow(0) * 9 + ZUGABE_LISTE)

    # ---- Assistent je Feld ----------------------------------------------------------------------------------------------
    def _zeile(self, schl: str, text: str, w: QWidget, aktiv: bool = True) -> QWidget:
        lab = _titel(text, w)
        w.setMinimumHeight(HOEHE_KNOPF_GROSS); w.setEnabled(aktiv); lab.setEnabled(aktiv)
        self._assistent.zeile(lab, w)
        self._felder[schl] = w
        return w

    def _box(self, eintraege, bearbeitbar: bool = False, daten=None) -> QComboBox:
        b = Auswahlfeld(); b.setEditable(bearbeitbar)
        for i, t in enumerate(eintraege):
            b.addItem(t, (daten[i] if daten else t))
        return b

    def _zeigen(self, name: str) -> None:
        if self._assistent_host is not None:
            self._assistent_platz.removeWidget(self._assistent_host); self._assistent_host.hide(); self._assistent_host.deleteLater()
        self._assistent_host = QWidget(); self._assistent = FormularGitter(self._assistent_host)
        self._assistent_platz.addWidget(self._assistent_host)
        self._felder = {}
        self.name = name
        k = self.kontext
        marken = list(k.get("textmarken", []))
        if name == "Formel":
            fmt = self._zeile("format", "&Zahlenformat:", self._box([""] + F.ZAHLENFORMATE, bearbeitbar=True))
            fkt = self._zeile("funktion", "Funktion &einfügen:", self._box([""] + F.FUNKTIONEN))
            ber = self._zeile("bereich", "&Tabellenbereich:", self._box([""] + F.BEREICHE), bool(k.get("in_tabelle")))
            mrk = self._zeile("marke", "Textmar&ke einfügen:", self._box([""] + marken), bool(marken))
            fmt.currentTextChanged.connect(self._formel_format)
            for box in (fkt, ber, mrk):
                box.activated.connect(lambda _i, box=box: self._formel_einsetzen(box))
        elif name == "Hyperlink":
            self._zeile("text", "&Adresse:", QLineEdit())
        elif name in ("Seite", "NumPages", "SectionPages"):
            self._zeile("art", "&Zahlenformat:", self._box([t for _k, t in F.SCHREIBWEISEN], daten=[k_ for k_, _t in F.SCHREIBWEISEN]))
        elif name == "PageRef":
            self._zeile("text", "&Textmarke:", self._box(marken), bool(marken))
        elif name == "Seq":
            self._zeile("text", "&Kategorie:", self._box(F.SEQ_KATEGORIEN, bearbeitbar=True))
            self._zeile("art", "&Zahlenformat:", self._box([t for _k, t in F.SCHREIBWEISEN], daten=[k_ for k_, _t in F.SCHREIBWEISEN]))
        elif name == "TC":
            self._zeile("text", "&Eintragstext:", QLineEdit())
            e = QSpinBox(); e.setRange(1, 9); self._zeile("ebene", "E&bene:", e)
        elif name in ("Uhrzeit", "PrintDate"):
            vorgabe = "HH:mm" if name == "Uhrzeit" else "dd.MM.yyyy"
            box = self._box(F.DATUMSFORMATE, bearbeitbar=True); box.setCurrentText(vorgabe)
            self._zeile("datum", "&Datumsformat:", box)
        elif name == "TOC":
            von, bis = QSpinBox(), QSpinBox(); von.setRange(1, 9); bis.setRange(1, 9); bis.setValue(3)
            self._zeile("von", "Ebenen &von:", von); self._zeile("bis", "Ebenen &bis:", bis)
        elif name == "Dokumentvariable":
            self._zeile("text", "&Name:", QLineEdit())
        elif name == "Seriendruckfeld":
            self._zeile("text", "&Feldname:", self._box(list(k.get("serienfelder", [])), bearbeitbar=True))
        elif name == "StyleRef":
            self._zeile("text", "&Formatvorlage:", self._box([f"Überschrift {i}" for i in range(1, 10)] + ["Titel", "Untertitel"],
                                                             bearbeitbar=True))
        for w in self._felder.values():
            for sig in ("textChanged", "currentTextChanged", "valueChanged"):
                if name != "Formel" and hasattr(w, sig):
                    getattr(w, sig).connect(self._bauen)
        self.beschreibung.setText(F.FELDER.get(name, ("", ""))[0])
        self._sperre = True
        self.anweisung.setText(F.vorgabe(name))
        self._sperre = False
        self._bauen()

    def _wert(self, schl: str):
        w = self._felder.get(schl)
        if isinstance(w, QComboBox):
            return w.currentData() if not w.isEditable() and w.currentData() is not None else w.currentText()
        if isinstance(w, QSpinBox):
            return w.value()
        return w.text() if w is not None else ""

    def _bauen(self, *_):
        """Feldfunktion aus dem Assistenten (außer bei Formel, die man selbst schreibt)."""
        n = self.name
        if n == "Formel":
            self._pruefen(); return
        art = self._wert("art")
        sw = f" \\* {art}" if art and art != "ARABIC" else ""
        text = str(self._wert("text") or "").strip()
        neu = {"Hyperlink": f'HYPERLINK "{text}"', "Seite": "PAGE" + sw, "NumPages": "NUMPAGES" + sw,
               "SectionPages": "SECTIONPAGES" + sw, "PageRef": f"PAGEREF {text}".strip(),
               "Seq": f"SEQ {text.replace(' ', '_') or 'Abbildung'} \\* {art or 'ARABIC'}",
               "TC": f'TC "{text}" \\l {self._wert("ebene")}', "Uhrzeit": f'TIME \\@ "{self._wert("datum")}"',
               "PrintDate": f'PRINTDATE \\@ "{self._wert("datum")}"', "TOC": f'TOC \\o "{self._wert("von")}-{self._wert("bis")}" \\h',
               "Dokumentvariable": f"DOCVARIABLE {text}".strip(), "Seriendruckfeld": f"MERGEFIELD {text}".strip(),
               "StyleRef": f'STYLEREF "{text}"'}.get(n)
        if neu is not None and not self._sperre:
            self.anweisung.setText(neu)
        self._pruefen()

    def _formel_format(self, muster: str) -> None:
        import re
        ohne = re.sub(r'\s*\\#\s*"[^"]*"', "", self.anweisung.text()).rstrip()
        self.anweisung.setText(ohne + (f' \\# "{muster}"' if muster.strip() else ""))

    def _formel_einsetzen(self, box: QComboBox) -> None:
        t = box.currentText()
        if not t:
            return
        if box is self._felder.get("funktion"):
            t += "()"
        pos = self.anweisung.cursorPosition() or len(self.anweisung.text())
        alt = self.anweisung.text()
        self.anweisung.setText(alt[:pos] + t + alt[pos:])
        self.anweisung.setCursorPosition(pos + (len(t) - 1 if t.endswith("()") else len(t)))
        box.setCurrentIndex(0)

    def _gueltig(self) -> bool:
        a = self.anweisung.text().strip()
        if not a:
            return False
        if a.startswith("="):
            try:
                F.formel(a[1:], self.kontext)
            except ValueError:
                return False
            return True
        wort = a.split()[0].upper()
        return not (wort in ("PAGEREF", "DOCVARIABLE", "MERGEFIELD") and len(a.split()) < 2) and a != 'HYPERLINK ""'

    def _pruefen(self, *_):
        self.ok.setEnabled(self._gueltig())

    def feld(self) -> tuple[str, str]:
        """(Feldanweisung, Ergebnis); mit „Formatierung beibehalten“ trägt die Anweisung ``\\* MERGEFORMAT``."""
        a = self.anweisung.text().strip()
        text = self._wert("text") if self.name == "TC" else F.ergebnis(a, self.kontext)
        if self.formatierung.isChecked() and F.MERGEFORMAT not in a:
            a += " " + F.MERGEFORMAT
        return a, text


class AutoTextDialog(PanelFaehig, QDialog):
    """„AutoText erstellen“: Name für die Markierung (Vorschlag: ihre ersten Wörter)."""

    def __init__(self, parent=None, markierung: str = ""):
        super().__init__(parent)
        self.setWindowTitle("AutoText erstellen")
        v = QVBoxLayout(self)
        self.feld = QLineEdit(" ".join(markierung.split()[:4])[:40]); self.feld.setMinimumHeight(HOEHE_KNOPF_GROSS)
        t = _titel("Bitte geben Sie einen &Namen für den AutoText-Eintrag an:", self.feld); t.setWordWrap(True)
        v.addWidget(t); v.addWidget(self.feld); v.addStretch(1)
        self.ok = fussleiste(self, v)
        self.feld.textChanged.connect(lambda x: self.ok.setEnabled(bool(x.strip())))
        self.ok.setEnabled(bool(self.feld.text().strip()))

    def name(self) -> str:
        return self.feld.text().strip()


class TrennerDialog(PanelFaehig, QDialog):
    """„Text in Tabelle umwandeln“ (mit Spaltenzahl) oder „Tabelle in Text konvertieren“: woran getrennt wird."""

    def __init__(self, parent=None, *, zu_tabelle: bool = True, texte: list[str] | None = None):
        super().__init__(parent)
        self.zu_tabelle, self.texte = zu_tabelle, list(texte or [])
        self.setWindowTitle("Text in Tabelle umwandeln" if zu_tabelle else "Tabelle in Text konvertieren")
        v = QVBoxLayout(self)
        fg = FormularGitter()                                                  # passt sich der Breite an (Seitenleiste)
        v.addLayout(fg)
        if zu_tabelle:
            self._spalten = QSpinBox(); self._spalten.setRange(1, 63); self._spalten.setMinimumHeight(HOEHE_KNOPF)
            self._zeilen = QLabel()
            fg.zeile(_titel("&Spaltenanzahl:", self._spalten), self._spalten)
            fg.zeile("Zeilenanzahl:", self._zeilen)
        t = QLabel("Text trennen bei"); f = t.font(); f.setBold(True); t.setFont(f)
        fg.breit(t)
        # Tabelle → Text wie in der Vorlage: Absätze, Tabstopps, Kommata, Andere (untereinander)
        self._liste = TT.TRENNER if zu_tabelle else [("\n", "&Absätze"), ("\t", "&Tabstopps"), (",", "&Kommata")]
        self._gruppe = QButtonGroup(self)
        g = FlussLayout(14) if zu_tabelle else QVBoxLayout()                   # Text → Tabelle: Reihe, die umbricht; Tabelle → Text: untereinander
        for i, (_z, text) in enumerate(self._liste):
            r = QRadioButton(text); self._gruppe.addButton(r, i); g.addWidget(r)
        andere = QRadioButton("A&ndere:"); self._gruppe.addButton(andere, len(self._liste))
        self.andere = QLineEdit("-"); self.andere.setMaxLength(1); self.andere.setMaximumWidth(BREITE_SCHIENE); self.andere.setMinimumHeight(HOEHE_KNOPF)
        self.andere.setAlignment(Qt.AlignCenter); self.andere.setAccessibleName("Anderes Trennzeichen")
        z = FlussLayout(6); z.addWidget(andere); z.addWidget(self.andere)
        fg.breit(g); fg.breit(z)
        if not zu_tabelle:
            self.geschachtelt = UmbruchSchalter("&Geschachtelte Tabellen umwandeln"); self.geschachtelt.setChecked(True)
            self.geschachtelt.setToolTip("Ohne Haken bleiben Tabellen in Zellen Tabellen und stehen hinter dem Text.")
            fg.breit(self.geschachtelt)
        self.andere.textEdited.connect(lambda _t: andere.setChecked(True))
        vorgabe = "\t" if any("\t" in s for s in self.texte) or not zu_tabelle else "\n"
        self._gruppe.button([k for k, _t in self._liste].index(vorgabe)).setChecked(True)
        self._gruppe.idToggled.connect(lambda _i, an: an and self._zaehlen())
        self.andere.textChanged.connect(lambda _t: self._zaehlen())
        v.addStretch(1)
        fussleiste(self, v)
        self._zaehlen()

    def trenner(self) -> str:
        i = self._gruppe.checkedId()
        return self._liste[i][0] if i < len(self._liste) else (self.andere.text() or "-")

    def spalten(self) -> int | None:
        return self._spalten.value() if self.zu_tabelle else None

    def _zaehlen(self) -> None:
        if not self.zu_tabelle:
            return
        z = TT.zellen(self.texte, self.trenner())
        self._spalten.setValue(max((len(r) for r in z), default=1))
        self._zeilen.setText(str(len(z)))


class SeitenzahlDialog(PanelFaehig, QDialog):
    """„Seitenzahl einfügen“ wie in der Vorlage: Format und Position, Kapitelnummer einbeziehen (Formatvorlage, Trennzeichen, Beispiele),
    Seitennummerierung (fortsetzen oder beginnen mit) und „Übernehmen für“ (gesamtes Dokument, von aktueller Seite, aktueller Abschnitt).

        d = SeitenzahlDialog(parent, page)     # page: Einrichtung des aktuellen Abschnitts (Vorbelegung)
        if d.exec(): d.werte()   # {"ort", "ausrichtung", "muster", "format", "start", "kapitel": (Ebene, Zeichen), "bereich"}
    """

    BEREICHE = (("dokument", "Gesamtes &Dokument"), ("seite", "Von aktueller Seite (&p)"), ("abschnitt", "Aktueller Abschnit&t"))

    def __init__(self, parent=None, page=None):
        super().__init__(parent)
        from lunivo_writer.editor import seitenzahl as SZ
        self.setWindowTitle("Seitenzahl einfügen")
        v = QVBoxLayout(self)
        g = FormularGitter()                                                # passt sich der Breite an (Seitenleiste), nichts wird abgeschnitten
        self.muster = Auswahlfeld(); self.position = Auswahlfeld()
        for muster, fmt, t in SZ.MUSTER:
            self.muster.addItem(t, (muster, fmt))
        for ort, ausr, t in SZ.POSITIONEN:
            self.position.addItem(t, (ort, ausr))
        self.position.setCurrentIndex(6)                                    # „Unten zentriert“
        for text, feld in (("&Format:", self.muster), ("Position (&s):", self.position)):
            feld.setMinimumHeight(HOEHE_KNOPF)
            g.zeile(_titel(text, feld), feld)
        self.kapitel = UmbruchSchalter("&Kapitelnummer einbeziehen"); g.breit(self.kapitel)
        self.ebene = Auswahlfeld(); self.trenner = Auswahlfeld()
        for n in range(1, 10):
            self.ebene.addItem(f"Überschrift {n}", n)
        for z, t, _docx in SZ.TRENNER:
            self.trenner.addItem(t, z)
        self.beispiel = QLabel()
        self._kapitel_teile = []
        for text, feld in (("Kapitel beginnt mit Formatvorlage (&C):", self.ebene), ("Trennzeichen &verwenden:", self.trenner),
                           ("Beispiele:", self.beispiel)):
            if isinstance(feld, QComboBox):
                feld.setMinimumHeight(HOEHE_KNOPF)
            t = _titel(text, feld)
            g.zeile(t, feld)
            self._kapitel_teile += [t, feld]
        g.breit(abschnittstitel("Seitennummerierung"))
        self.fortsetzen = QRadioButton("Fortsetzen vom vorherigen Abschnitt (&o)"); self.beginnen = QRadioButton("&Beginnen mit:")
        self.start = QSpinBox(); self.start.setRange(1, 9999); self.start.setMinimumHeight(HOEHE_KNOPF)
        self.start.setAccessibleName("Beginnen mit")
        g.breit(self.fortsetzen)
        z = FlussLayout(6); z.addWidget(self.beginnen); z.addWidget(self.start); g.breit(z)
        g.breit(abschnittstitel("Übernehmen für"))
        self.bereich = QButtonGroup(self)
        u = FlussLayout(10)
        for i, (_k, t) in enumerate(self.BEREICHE):
            r = QRadioButton(t); self.bereich.addButton(r, i); u.addWidget(r)
        g.breit(u)
        v.addLayout(g)
        v.addStretch(1)
        self.bereich.button(0).setChecked(True)
        fussleiste(self, v)
        if page is not None:                                                  # Vorbelegung aus der Einrichtung
            for i, (_m, fmt, _t) in enumerate(SZ.MUSTER):
                if fmt == page.seiten_format:
                    self.muster.setCurrentIndex(i); break
            self.kapitel.setChecked(bool(page.kapitel_ebene))
            self.ebene.setCurrentIndex(max(0, (page.kapitel_ebene or 1) - 1))
            self.trenner.setCurrentIndex(max(0, self.trenner.findData(page.kapitel_trenner)))
            if page.seiten_start > 0:
                self.beginnen.setChecked(True); self.start.setValue(page.seiten_start)
        if not self.beginnen.isChecked():
            self.fortsetzen.setChecked(True)
        self.kapitel.toggled.connect(self._zustand); self.beginnen.toggled.connect(self._zustand)
        self.trenner.currentIndexChanged.connect(self._zustand)
        self._zustand()

    def _zustand(self, *_a) -> None:
        for w in self._kapitel_teile:
            w.setEnabled(self.kapitel.isChecked())
        tr = self.trenner.currentData()
        self.beispiel.setText(f"1{tr}1, 1{tr}A")
        self.start.setEnabled(self.beginnen.isChecked())

    def werte(self) -> dict:
        muster, fmt = self.muster.currentData()
        ort, ausr = self.position.currentData()
        return {"ort": ort, "ausrichtung": ausr, "muster": muster, "format": fmt,
                "start": self.start.value() if self.beginnen.isChecked() else 0,
                "kapitel": (self.ebene.currentData() if self.kapitel.isChecked() else 0, self.trenner.currentData()),
                "bereich": self.BEREICHE[self.bereich.checkedId()][0]}


class HyperlinkDialog(PanelFaehig, QDialog):
    """„Hyperlink“ wie in der Vorlage: links „Link zu“ (Datei oder Webseite, Aktuelles Dokument, E-Mail-Adresse), oben „Anzuzeigender Text“
    und „QuickInfo …“, darunter je Ziel eine Seite. Das Fenster fügt nichts ein; ``ergebnis()`` liefert, was der Aufrufer braucht.

        d = HyperlinkDialog(parent, text="markierter Text", ziele=verweise.querverweis_ziele(ed), ordner=..., adressen=[...])
        if d.exec(): d.ergebnis()   # {"art": "datei"|"dokument"|"mail", "href" | "ziel", "text", "tipp"}
    """

    def __init__(self, parent=None, *, text: str = "", ziele: list[dict] | None = None, ordner: str = "", adressen: list[str] | None = None):
        super().__init__(parent)
        import os
        from PySide6.QtCore import QDir, QSize
        from PySide6.QtWidgets import (
            QFileSystemModel, QInputDialog, QListView, QPushButton, QStackedWidget, QToolButton, QTreeWidget, QTreeWidgetItem, QWidget,
        )
        from lunivo_writer.ui.widgets import icons
        self._os, self._QInputDialog = os, QInputDialog
        self.setWindowTitle("Hyperlink")
        self.tipp = ""
        rechts = QVBoxLayout(self)
        z = FormularGitter()                                                   # passt sich der Breite an (Seitenleiste: untereinander)
        z.breit(abschnittstitel("Link zu"))
        self.arten = QButtonGroup(self)
        fl = FlussLayout(6)                                                    # die drei Ziele, bei Platzmangel untereinander
        for i, (sym, name) in enumerate((("kette", "&Datei oder Webseite"), ("textmarke", "Aktuelles D&okument"),
                                         ("briefumschlag", "E-Mail-Adre&sse"))):
            b = QToolButton(); b.setText(name); b.setIcon(icons.icon(sym, ICON_LISTE)); b.setIconSize(QSize(ICON_LISTE, ICON_LISTE)); b.setCheckable(True)
            b.setToolButtonStyle(Qt.ToolButtonTextBesideIcon); b.setAutoRaise(True); b.setMinimumHeight(HOEHE_KNOPF_HOCH)
            self.arten.addButton(b, i); fl.addWidget(b)
        z.breit(fl)
        self.text = QLineEdit(text); self.text.setMinimumHeight(HOEHE_KNOPF)
        quick = QPushButton("&QuickInfo …"); quick.setMinimumHeight(HOEHE_KNOPF); quick.clicked.connect(self._quickinfo)
        z.zeile(_titel("Anzuzeigender &Text:", self.text), self.text); z.breit(quick)
        rechts.addLayout(z)
        self.seiten = QStackedWidget(); rechts.addWidget(self.seiten, 1)
        # Seite 1: Datei oder Webseite
        s1 = QWidget(); v1 = QVBoxLayout(s1); v1.setContentsMargins(*RAND_KEIN)
        oz = QHBoxLayout()
        self.ordner = Auswahlfeld(); self.ordner.setEditable(True); self.ordner.setMinimumHeight(HOEHE_KNOPF); self.ordner.setAccessibleName("Ordner")
        start = ordner if ordner and os.path.isdir(ordner) else QDir.homePath()
        for p in dict.fromkeys([start, QDir.homePath()] + [os.path.join(QDir.homePath(), n) for n in ("Schreibtisch", "Desktop", "Dokumente")]):
            if os.path.isdir(p):
                self.ordner.addItem(icons.icon("oeffnen", ICON_GROSS), p)
        hoch = QToolButton(); hoch.setIcon(icons.icon("trefferHoch", ICON_GROSS)); hoch.setToolTip("Übergeordneter Ordner"); hoch.setFixedSize(*GROESSE_KNOPF_QUADRAT)
        hoch.setAccessibleName("Übergeordneter Ordner")
        oz.addWidget(self.ordner, 1); oz.addWidget(hoch); v1.addLayout(oz)
        self.modell = QFileSystemModel(self); self.modell.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
        self.dateien = QListView(); self.dateien.setModel(self.modell); self.dateien.setViewMode(QListView.ListMode)
        self.dateien.setFlow(QListView.TopToBottom); self.dateien.setWrapping(True); self.dateien.setResizeMode(QListView.Adjust)
        self.dateien.setGridSize(QSize(*GROESSE_RASTER_DATEIEN)); self.dateien.setUniformItemSizes(True); self.dateien.setMinimumHeight(HOEHE_LISTE_MITTEL)
        self.dateien.setAccessibleName("Dateien")
        v1.addWidget(self.dateien, 1)
        az = FormularGitter()
        self.adresse = QLineEdit(); self.adresse.setMinimumHeight(HOEHE_KNOPF); self.adresse.setPlaceholderText("https://… oder Pfad einer Datei")
        marken = QPushButton("&Lesezeichen …"); marken.setMinimumHeight(HOEHE_KNOPF); marken.setEnabled(False)
        marken.setToolTip("Sprungziele in fremden Dateien kann Lunivo noch nicht auslesen.")
        az.zeile(_titel("Adr&esse:", self.adresse), self.adresse); az.breit(marken)
        v1.addLayout(az)
        self.seiten.addWidget(s1)
        # Seite 2: Aktuelles Dokument
        s2 = QWidget(); v2 = QVBoxLayout(s2); v2.setContentsMargins(*RAND_KEIN)
        self.stellen = QTreeWidget(); self.stellen.setHeaderHidden(True); self.stellen.setAccessibleName("Stelle im Dokument")
        v2.addWidget(_titel("&Wählen Sie eine Stelle im Dokument:", self.stellen)); v2.addWidget(self.stellen, 1)
        anfang = QTreeWidgetItem(["Anfang des Dokuments"]); anfang.setData(0, Qt.UserRole, {"art": "Anfang", "block": 0, "text": ""})
        self.stellen.addTopLevelItem(anfang)
        gruppen = {}
        for z_ in ziele or []:
            art = "Überschriften" if z_["art"] == "Überschrift" else "Textmarken" if z_["art"] == "Textmarke" else None
            if art is None:
                continue
            if art not in gruppen:
                gruppen[art] = QTreeWidgetItem([art]); gruppen[art].setFlags(Qt.ItemIsEnabled); self.stellen.addTopLevelItem(gruppen[art])
            it = QTreeWidgetItem([z_["text"]]); it.setData(0, Qt.UserRole, z_); gruppen[art].addChild(it)
        self.stellen.expandAll(); self.stellen.setCurrentItem(anfang)
        self.seiten.addWidget(s2)
        # Seite 3: E-Mail-Adresse
        s3 = QWidget(); v3 = QVBoxLayout(s3); v3.setContentsMargins(*RAND_KEIN); g3 = FormularGitter(); v3.addLayout(g3, 1)
        self.mail = QLineEdit(); self.mail.setMinimumHeight(HOEHE_KNOPF); self.betreff = QLineEdit(); self.betreff.setMinimumHeight(HOEHE_KNOPF)
        self.zuletzt = QListWidget(); self.zuletzt.addItems(adressen or []); self.zuletzt.setAccessibleName("Zuletzt verwendete E-Mail-Adressen")
        g3.zeile(_titel("E-&Mail-Adresse:", self.mail), self.mail)
        g3.zeile(_titel("&Betreff:", self.betreff), self.betreff)
        g3.zeile(_titel("&Zuletzt verwendete E-Mail-Adressen:", self.zuletzt), self.zuletzt)
        self.seiten.addWidget(s3)
        self.ok = fussleiste(self, rechts)
        # Verbindungen
        self.arten.idClicked.connect(lambda i: (self.seiten.setCurrentIndex(i), self._pruefen()))
        self.ordner.currentTextChanged.connect(self._ordner_zeigen)
        hoch.clicked.connect(lambda: self._ordner_setzen(os.path.dirname(self.ordner.currentText().rstrip(os.sep)) or os.sep))
        self.dateien.clicked.connect(lambda i: self.adresse.setText(self.modell.filePath(i)))
        self.dateien.doubleClicked.connect(self._doppelklick)
        self.zuletzt.currentTextChanged.connect(self.mail.setText)
        for f in (self.adresse, self.mail):
            f.textChanged.connect(lambda _t: self._pruefen())
        self.stellen.currentItemChanged.connect(lambda *_: self._pruefen())
        self.arten.button(0).setChecked(True)
        self._ordner_zeigen(self.ordner.currentText())
        self._pruefen()

    def _ordner_setzen(self, pfad: str) -> None:
        if self.ordner.findText(pfad) < 0:
            self.ordner.addItem(pfad)
        self.ordner.setCurrentText(pfad)

    def _ordner_zeigen(self, pfad: str) -> None:
        if self._os.path.isdir(pfad):
            self.dateien.setRootIndex(self.modell.setRootPath(pfad))

    def _doppelklick(self, i) -> None:
        pfad = self.modell.filePath(i)
        if self.modell.isDir(i):
            self._ordner_setzen(pfad)
        else:
            self.adresse.setText(pfad); self._pruefen()
            if self.ok.isEnabled():
                self.accept()

    def _quickinfo(self) -> None:
        t, ok = self._QInputDialog.getText(self, "QuickInfo für Hyperlink", "QuickInfo-Text:", text=self.tipp)
        if ok:
            self.tipp = t.strip()

    def art_waehlen(self, i: int) -> None:
        self.arten.button(i).setChecked(True); self.seiten.setCurrentIndex(i); self._pruefen()

    def _pruefen(self) -> None:
        i = self.arten.checkedId()
        if i == 0:
            gut = bool(self.adresse.text().strip())
        elif i == 1:
            it = self.stellen.currentItem()
            gut = it is not None and it.data(0, Qt.UserRole) is not None
        else:
            gut = "@" in self.mail.text()
        self.ok.setEnabled(gut)

    @staticmethod
    def adresse_zu_href(adresse: str) -> str:
        """Eingabe → Linkziel: Dateipfad → file://…, „www.…“ → https://…, sonst unverändert."""
        import os
        from PySide6.QtCore import QUrl
        a = adresse.strip()
        if a.startswith(("/", "~")):
            return QUrl.fromLocalFile(os.path.expanduser(a)).toString()
        if "://" not in a and not a.startswith(("mailto:", "#")) and "." in a and " " not in a:
            return "https://" + a
        return a

    def ergebnis(self) -> dict:
        from PySide6.QtCore import QUrl, QUrlQuery
        i = self.arten.checkedId()
        r = {"text": self.text.text().strip(), "tipp": self.tipp}
        if i == 1:
            r.update(art="dokument", ziel=self.stellen.currentItem().data(0, Qt.UserRole))
            r["text"] = r["text"] or r["ziel"].get("text") or "Anfang des Dokuments"
        elif i == 2:
            u = QUrl("mailto:" + self.mail.text().strip())
            if self.betreff.text().strip():
                q = QUrlQuery(); q.addQueryItem("subject", self.betreff.text().strip()); u.setQuery(q)
            r.update(art="mail", href=u.toString(), adresse=self.mail.text().strip())
            r["text"] = r["text"] or self.mail.text().strip()
        else:
            r.update(art="datei", href=self.adresse_zu_href(self.adresse.text()))
            r["text"] = r["text"] or self.adresse.text().strip()
        return r


class ObjektDialog(PanelFaehig, QDialog):
    """„Objekt einfügen“ wie in der Vorlage. „Neu“ (ein eingebettetes Office-Objekt anlegen) kann Lunivo nicht und bleibt grau;
    „Aus Datei erstellen“ fügt Text, Dokument oder Bild ein, mit „Als Symbol anzeigen“ ein Dateisymbol mit Link auf die Datei."""

    TYPEN = ("DOCX-Dokument", "ODT-Dokument", "XLSX-Tabelle", "PPTX-Präsentation")

    def __init__(self, parent=None, *, als_symbol: bool = False, ordner: str = ""):
        super().__init__(parent)
        from PySide6.QtWidgets import QFrame, QPushButton
        self.setWindowTitle("Objekt einfügen")
        self._ordner = ordner
        v = QVBoxLayout(self)
        g = FormularGitter()                                                   # in der Seitenleiste untereinander: Art, Objekttyp, Datei, Symbol
        self.neu = QRadioButton("&Neu"); self.aus_datei = QRadioButton("&Aus Datei erstellen")
        self.neu.setEnabled(False); self.neu.setToolTip("Eingebettete Office-Objekte kann Lunivo nicht anlegen.")
        self.aus_datei.setChecked(True)
        links = FlussLayout(14); links.addWidget(self.neu); links.addWidget(self.aus_datei)
        g.breit(links)
        self.typen = QListWidget(); self.typen.addItems(list(self.TYPEN)); self.typen.setEnabled(False); self.typen.setMaximumHeight(HOEHE_EINGABE_TEXT)
        g.breit(_titel("Objekt&typ:", self.typen)); g.breit(self.typen)
        self.datei = QLineEdit(); self.datei.setMinimumHeight(HOEHE_KNOPF); self.datei.setAccessibleName("Datei")
        such = QPushButton("&Durchsuchen …"); such.setMinimumHeight(HOEHE_KNOPF); such.clicked.connect(self._suchen)
        g.zeile(_titel("&Datei:", self.datei), self.datei); g.breit(such)
        self.symbol = UmbruchSchalter("Als Sym&bol anzeigen"); self.symbol.setChecked(als_symbol)
        g.breit(self.symbol)
        g.breit(abschnittstitel("Ergebnis"))
        v.addLayout(g)
        kasten = QFrame(); kasten.setFrameShape(QFrame.StyledPanel); kh = QVBoxLayout(kasten)
        self.ergebnis_text = QLabel(); self.ergebnis_text.setWordWrap(True); kh.addWidget(self.ergebnis_text)
        v.addWidget(kasten)
        self.ok = fussleiste(self, v)
        self.datei.textChanged.connect(lambda _t: self._beschreiben()); self.symbol.toggled.connect(lambda _a: self._beschreiben())
        self._beschreiben()

    def _suchen(self) -> None:
        from lunivo_writer.ui.baukasten.speichern_fenster import datei_waehlen
        pfade = datei_waehlen(self, "Datei für das Objekt wählen", self.datei.text() or self._ordner, "Alle Dateien (*)")
        if pfade:
            self.datei.setText(pfade[0])

    def art(self) -> str:
        """"symbol" | "bild" | "text" | "" (keine Datei)."""
        import os
        pfad = self.datei.text().strip()
        if not pfad or not os.path.isfile(pfad):
            return ""
        if self.symbol.isChecked():
            return "symbol"
        endung = os.path.splitext(pfad)[1].lower()
        if endung in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg"):
            return "bild"
        if endung in (".docx", ".odt", ".rtf", ".txt", ".md"):
            return "text"
        return "symbol"

    def _beschreiben(self) -> None:
        import os
        a = self.art()
        name = os.path.basename(self.datei.text().strip())
        self.ok.setEnabled(bool(a))
        self.ergebnis_text.setText({
            "": "Wählen Sie eine Datei. Ihr Inhalt wird in das Dokument eingefügt.",
            "bild": f"Fügt das Bild „{name}“ in Ihr Dokument ein.",
            "text": f"Fügt den Inhalt von „{name}“ in Ihr Dokument ein (Text, Tabellen und Bilder).",
            "symbol": f"Fügt ein Symbol für „{name}“ ein. Ein Klick darauf öffnet die Datei."
                      + ("" if self.symbol.isChecked() else " (Den Inhalt dieser Dateiart kann Lunivo nicht einbetten.)"),
        }[a])
