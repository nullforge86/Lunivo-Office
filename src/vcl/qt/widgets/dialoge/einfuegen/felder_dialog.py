"""Felder dialog: aus ``vcl.qt.widgets.dialoge.einfuegen.einfuegen_fenster`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QComboBox, QDialog, QLabel, QListWidget, QSpinBox, QWidget
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.rendering import textfelder as F
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, UmbruchSchalter, abschnittstitel
from vcl.qt.widgets.bausteine.abstaende.mass import EINFUEGEN_LISTE_ZEILEN
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.abstaende.mass import HOEHE_KNOPF_GROSS, ZUGABE_LISTE
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.dialoge.einfuegen.einfuegen_fenster_hilfen import _titel


class FelderDialog(PanelFaehig, QDialog):
    """„Felder“ wie in der Vorlage: links „Feld auswählen“ mit den Feldnamen, rechts „Feldeigenschaften“ mit Feldfunktionen,
    Assistent (je Feld eigene Felder), Beschreibung und „Formatierung bei Aktualisierung beibehalten“. OK ist grau, solange die
    Feldfunktion nichts ergibt (z. B. eine Formel nur aus „=“)."""

    def __init__(self, parent=None, kontext: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Felder")
        self.kontext = kontext or {}
        self._sperre = False
        v = _spalte("standard", self)
        g = FormularGitter(); v.addLayout(g, 1)
        g.breit(abschnittstitel("Feld auswählen"))
        self.liste = QListWidget(); self.liste.setAccessibleName("Feldnamen"); self.liste.addItems(list(F.FELDER))
        g.zeile(_titel("Feldna&men:", self.liste), self.liste)
        g.breit(abschnittstitel("Feldeigenschaften"))
        self.anweisung = zeilenfeld("frei")
        self.anweisung.setAccessibleName("Feldfunktionen")
        g.zeile(_titel("&Feldfunktionen:", self.anweisung), self.anweisung)
        g.breit(QLabel("Assistent:"))
        self._assistent_platz = _spalte("standard")     # wird je Feld neu gefüllt
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
        self.liste.setFixedHeight(self.liste.sizeHintForRow(0) * EINFUEGEN_LISTE_ZEILEN + ZUGABE_LISTE)

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

    # Feldname → Methode, die dessen Assistentenfelder baut
    _ASSISTENTEN = {"Formel": "_assistent_formel", "Hyperlink": "_assistent_adresse", "Seite": "_assistent_zahlenformat",
                    "NumPages": "_assistent_zahlenformat", "SectionPages": "_assistent_zahlenformat", "PageRef": "_assistent_seitenverweis",
                    "Seq": "_assistent_seq", "TC": "_assistent_tc", "Uhrzeit": "_assistent_datum", "PrintDate": "_assistent_datum",
                    "TOC": "_assistent_toc", "Dokumentvariable": "_assistent_variable", "Seriendruckfeld": "_assistent_serienfeld",
                    "StyleRef": "_assistent_formatvorlage"}

    def _assistent_formel(self, name: str) -> None:
        k = self.kontext
        marken = list(k.get("textmarken", []))
        fmt = self._zeile("format", "&Zahlenformat:", self._box([""] + F.ZAHLENFORMATE, bearbeitbar=True))
        fkt = self._zeile("funktion", "Funktion &einfügen:", self._box([""] + F.FUNKTIONEN))
        ber = self._zeile("bereich", "&Tabellenbereich:", self._box([""] + F.BEREICHE), bool(k.get("in_tabelle")))
        mrk = self._zeile("marke", "Textmar&ke einfügen:", self._box([""] + marken), bool(marken))
        fmt.currentTextChanged.connect(self._formel_format)
        for box in (fkt, ber, mrk):
            box.activated.connect(lambda _i, box=box: self._formel_einsetzen(box))

    def _assistent_adresse(self, name: str) -> None:
        self._zeile("text", "&Adresse:", zeilenfeld("frei"))

    def _assistent_zahlenformat(self, name: str) -> None:
        self._zeile("art", "&Zahlenformat:", self._box([t for _k, t in F.SCHREIBWEISEN], daten=[k_ for k_, _t in F.SCHREIBWEISEN]))

    def _assistent_seitenverweis(self, name: str) -> None:
        marken = list(self.kontext.get("textmarken", []))
        self._zeile("text", "&Textmarke:", self._box(marken), bool(marken))

    def _assistent_seq(self, name: str) -> None:
        self._zeile("text", "&Kategorie:", self._box(F.SEQ_KATEGORIEN, bearbeitbar=True))
        self._assistent_zahlenformat(name)

    def _assistent_tc(self, name: str) -> None:
        self._zeile("text", "&Eintragstext:", zeilenfeld("frei"))
        e = QSpinBox(); e.setRange(1, 9); self._zeile("ebene", "E&bene:", e)

    def _assistent_datum(self, name: str) -> None:
        vorgabe = "HH:mm" if name == "Uhrzeit" else "dd.MM.yyyy"
        box = self._box(F.DATUMSFORMATE, bearbeitbar=True); box.setCurrentText(vorgabe)
        self._zeile("datum", "&Datumsformat:", box)

    def _assistent_toc(self, name: str) -> None:
        von, bis = QSpinBox(), QSpinBox(); von.setRange(1, 9); bis.setRange(1, 9); bis.setValue(3)
        self._zeile("von", "Ebenen &von:", von); self._zeile("bis", "Ebenen &bis:", bis)

    def _assistent_variable(self, name: str) -> None:
        self._zeile("text", "&Name:", zeilenfeld("frei"))

    def _assistent_serienfeld(self, name: str) -> None:
        self._zeile("text", "&Feldname:", self._box(list(self.kontext.get("serienfelder", [])), bearbeitbar=True))

    def _assistent_formatvorlage(self, name: str) -> None:
        self._zeile("text", "&Formatvorlage:", self._box([f"Überschrift {i}" for i in range(1, 10)] + ["Titel", "Untertitel"],
                                                         bearbeitbar=True))

    def _zeigen(self, name: str) -> None:
        if self._assistent_host is not None:
            self._assistent_platz.removeWidget(self._assistent_host); self._assistent_host.hide(); self._assistent_host.deleteLater()
        self._assistent_host = QWidget(); self._assistent = FormularGitter(self._assistent_host)
        self._assistent_platz.addWidget(self._assistent_host)
        self._felder = {}
        self.name = name
        bauer = self._ASSISTENTEN.get(name)
        if bauer:
            getattr(self, bauer)(name)
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
