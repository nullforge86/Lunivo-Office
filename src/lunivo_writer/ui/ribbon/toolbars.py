"""Oberfläche „Symbolleisten“: ☰ Menü + obere Leiste (Datei/Dokument) + untere Leiste (Text) + Zusammenhangsleiste.

Gleiche Schnittstelle
wie RegisterBand (aktualisieren, kontext, felder, menue_knopf), damit das Fenster beide gleich behandeln kann.
"""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QComboBox, QFontComboBox, QFrame, QHBoxLayout, QToolButton, QVBoxLayout, QWidget,
)

from lunivo_writer.ui.baukasten.basis.texte import trennlinie
from lunivo_writer.ui.theme import kopf_symbolfarbe
from lunivo_writer.ui.widgets import icons
from lunivo_writer.ui.contextual.image_tools import BILDTOOLS, FORMTOOLS, SMARTARTTOOLS, ZEICHENTOOLS
from lunivo_writer.ui.contextual.text_tools import TEXTTOOLS
from lunivo_writer.ui.contextual.table_tools import TABELLENTOOLS
from lunivo_writer.ui.ribbon.ribbon_bar import NICHT_DA, STILE_KATALOG
from lunivo_writer.ui.baukasten.basis.mass import (
    ABSTAND_ENG,
    BREITE_LEISTENKNOPF_MIN,
    ICON_GROSS,
    ICON_NORMAL,
    RAND_KEIN,
    RAND_SYMBOLLEISTE,
)
from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Auswahlfeld, Schriftauswahl
from lunivo_writer.ui.baukasten.dropdown.dropdown_knopf import DropdownKnopf

T = "trenner"
# (Symbol, Tooltip, Aktion)
OBEN = [
    ("neu", "Neu (Strg+N)", "neu"), ("oeffnen", "Öffnen (Strg+O)", "oeffnen"), ("speichern", "Speichern (Strg+S)", "speichern"),
    ("unter", "Speichern unter", "speichernUnter"), T,
    ("drucken", "Drucken (Strg+P)", "drucken"), ("vorschau", "Druckvorschau", "vorschau"),
    ("pdf", "Als PDF exportieren", "speichernPdf"), T,
    ("kleben", "Einfügen (Strg+V)", "einfuegen"), ("ohneformat", "Einfügen ohne Formatierung", "einfuegenOhne"),
    ("schere", "Ausschneiden (Strg+X)", "ausschneiden"), ("kopie", "Kopieren (Strg+C)", "kopieren"),
    ("pinsel", "Format übertragen", "formatUebertragen"), ("zurueck", "Rückgängig (Strg+Z)", "rueckgaengig"),
    ("vor", "Wiederholen (Strg+Y)", "wiederholen"), T,
    ("lupe", "Suchen und Ersetzen (Strg+F)", "suchen"), T,
    ("haken", "Prüfen (F7)", "rechtschreibung"), ("gruendlich", "Gründlich prüfen", "gruendlichPruefen"), T,
    ("umbruch", "Seitenumbruch (Strg+Enter)", "seitenumbruch"), ("tabelle", "Tabelle einfügen", "tabelleRaster"),
    ("bild", "Bild", "bild"), ("stift", "Formen", "formenGalerie"), ("saeule", "Diagramm", "diagramm"), T,
    ("kette", "Hyperlink", "hyperlink"), ("kopfz", "Kopfzeile", "kopfFussZeigen"), ("fussz", "Fußzeile", "fusszeileBearbeiten"),
    ("seitenzahl", "Seitenzahl", "seitenzahlKlappe"), T,
    ("textrahmen", "Textfeld", "textfeld"), ("omega", "Sonderzeichen", "sonderzeichen"), T,
    ("verfolgt", "Änderungen verfolgen", "verfolgen"), ("notiz", "Neuer Kommentar", "kommentar"), T,
    ("optionen", "Optionen (F9)", "w.optionenOeffnen"),
]
UNTEN_A = [("groesserA", "Schrift vergrößern", "schriftGroesser"), ("kleinerA", "Schrift verkleinern", "schriftKleiner"),
           ("radierer", "Formatierung löschen", "schlicht"), T,
           ("F", "Fett (Strg+B)", "fett"), ("K", "Kursiv (Strg+I)", "kursiv"), ("U", "Unterstrichen (Strg+U)", "unter"),
           ("S", "Durchgestrichen", "durch"), ("hoch", "Hochgestellt", "hoch"), ("tief", "Tiefgestellt", "tief"),
           ("marker", "Hervorheben", "hervorhebenJetzt"), ("farbe", "Schriftfarbe", "schriftfarbeJetzt"),
           ("schreibweise", "Groß-/Kleinschreibung", "schreibweise"), ("unterart", "Unterstreichungsart", "unterstrichArt"),
           ("texteffekt", "Texteffekte", "texteffekte"), T,
           ("punkte", "Aufzählung", "punkte"), ("zahlen", "Nummerierung", "zahlen"), ("weniger", "Einzug verringern", "einzugWeniger"),
           ("mehr", "Einzug vergrößern", "einzugMehr"), ("ebeneHoch", "Listenebene erhöhen", "ebeneHoeher"),
           ("ebeneTief", "Listenebene verringern", "ebeneTiefer"), ("links", "Linksbündig", "links"),
           ("mitte", "Zentriert", "mitte"), ("rechts", "Rechtsbündig", "rechts"), ("block", "Blocksatz", "block")]
UNTEN_B = [("rahmen", "Absatzrahmen", "absatzRahmen"), ("toenung", "Absatzschattierung", "absatzSchattierung"),
           ("sortieren", "Sortieren", "sortieren"), ("steuerzeichen", "Steuerzeichen", "steuerzeichenZeigen")]
ZEILENABSTAENDE = [("1.0", "1,0"), ("1.15", "1,15"), ("1.5", "1,5"), ("2.0", "2,0"), ("2.5", "2,5"), ("3.0", "3,0")]
GROESSEN = [8, 9, 10, 10.5, 11, 12, 14, 16, 18, 20, 24, 28, 36, 48, 72]
# Zeichen, die gar kein Symbol sind (F K U S) — als Buchstabe gezeigt
BUCHSTABEN = {"F": ("F", "bold"), "K": ("K", "italic"), "U": ("U", "underline"), "S": ("S", "strike")}


class Symbolleisten(QWidget):
    def __init__(self, befehle):
        super().__init__()
        self.b = befehle
        self.knoepfe: list[tuple[QToolButton, str | None, bool]] = []
        self.schalter: list[tuple[QToolButton, str]] = []
        self.felder: dict[str, QWidget] = {}
        self.kontext_index: dict = {}
        self.fehlend: list[str] = []
        v = QVBoxLayout(self)
        v.setContentsMargins(*RAND_SYMBOLLEISTE)
        v.setSpacing(ABSTAND_ENG)
        self.menue_knopf = QToolButton()
        self.menue_knopf.setText("Menü")
        self.menue_knopf.setIcon(icons.icon("menu", ICON_NORMAL, kopf_symbolfarbe())); self.menue_knopf.setIconSize(QSize(ICON_NORMAL, ICON_NORMAL))
        self.menue_knopf.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.menue_knopf.setAutoRaise(True)
        z1 = self._zeile(v)
        z1.addWidget(self.menue_knopf)
        self._trenner(z1)
        self._fuellen(z1, OBEN)
        z1.addStretch(1)
        z2 = self._zeile(v)
        stil = Auswahlfeld(); stil.addItems(["Fließtext"] + [n for n in STILE_KATALOG if n not in ("Standard", "Kein Abstand")])
        stil.rolle("formatvorlage", "leiste")
        font = Schriftauswahl(); font.rolle("schrift", "leiste")
        groesse = Auswahlfeld(); groesse.setEditable(True); groesse.rolle("groesse", "leiste")
        groesse.addItems([str(x) for x in GROESSEN])
        self.felder.update(stil=stil, font=font, groesse=groesse)
        for w in (font, groesse):
            z2.addWidget(w)
        self._fuellen(z2, UNTEN_A)
        abstand = Auswahlfeld()
        for wert, name in ZEILENABSTAENDE:
            abstand.addItem("Zeilen " + name, float(wert))
        abstand.addItem("Mehr…", "mehr")
        abstand.rolle("abstand", "leiste")
        abstand.activated.connect(lambda _: self._abstand(abstand))
        z2.addWidget(abstand)
        self._fuellen(z2, UNTEN_B)
        self._trenner(z2)
        z2.addWidget(stil)
        z2.addStretch(1)
        self.zusammenhang = QWidget()
        self.z3 = QHBoxLayout(self.zusammenhang)
        self.z3.setContentsMargins(*RAND_KEIN)
        self.z3.setSpacing(0)
        v.addWidget(self.zusammenhang)
        self.zusammenhang.hide()
        self._kontext_name = None
        linie = trennlinie(tief=True)
        v.addWidget(linie)

    def _zeile(self, v) -> QHBoxLayout:
        h = QHBoxLayout(); h.setSpacing(0); h.setContentsMargins(*RAND_KEIN)
        v.addLayout(h)
        return h

    def _trenner(self, h):
        s = trennlinie(senkrecht=True, tief=True)
        h.addWidget(s)

    def _fuellen(self, h: QHBoxLayout, liste):
        for e in liste:
            if e == T:
                self._trenner(h)
                continue
            sym, tip, akt = e
            h.addWidget(self._knopf(sym, tip, akt))

    def _knopf(self, sym: str, tip: str, akt: str, haken: bool = False) -> QToolButton:
        k = QToolButton()
        k.setAutoRaise(True)
        a = QAction(k)
        if icons.hat(sym):
            a.setIcon(icons.icon(sym, ICON_GROSS))
            k.setIconSize(QSize(ICON_GROSS, ICON_GROSS))
            k.setToolButtonStyle(Qt.ToolButtonIconOnly)
        else:
            a.setText(BUCHSTABEN.get(sym, (sym,))[0])
            f = k.font()
            if sym == "F": f.setBold(True)
            if sym == "K": f.setItalic(True)
            if sym == "U": f.setUnderline(True)
            if sym == "S": f.setStrikeOut(True)
            k.setFont(f)
            k.setMinimumWidth(BREITE_LEISTENKNOPF_MIN)
        a.setToolTip(tip)
        k.setDefaultAction(a)
        k.setToolTip(tip)
        if icons.hat(sym):                                     # Rechtsklick: Symbol austauschen
            k.setContextMenuPolicy(Qt.CustomContextMenu)
            k.customContextMenuRequested.connect(lambda _p, s=sym: self.b.symbolTauschen(None, s))
        ok = self.b.hat(akt)
        if ok:
            a.triggered.connect(lambda _=False, t=akt, kk=k: (self.b.tun(t, kk), self.aktualisieren()))
            if haken or self.b.zustand(akt) is not None:
                a.setCheckable(True)
                self.schalter.append((k, akt))
        else:
            k.setProperty("fehlt", True)
            k.setEnabled(False)
            k.setToolTip(NICHT_DA.format(tip.split(" (")[0]))
            self.fehlend.append(akt)
        self.knoepfe.append((k, akt, akt not in ("neu", "oeffnen", "w.optionenOeffnen")))
        return k

    def _abstand(self, box: QComboBox):
        w = box.currentData()
        if w == "mehr":
            self.b.w.paragraph_dialog()
        elif self.b.ed:
            self.b.ed.set_line_spacing(float(w))

    # ---- gleiche Schnittstelle wie RegisterBand ----------------------------------------------
    def kontext(self, name: str, sichtbar: bool, aktivieren: bool = False) -> None:
        if name not in ("tabelle", "bild", "form", "smartart", "zeichen", "text"):
            return
        if sichtbar and self._kontext_name != name:
            self._kontext_name = name
            while self.z3.count():
                it = self.z3.takeAt(0)
                if it.widget():
                    it.widget().deleteLater()
            plan = TABELLENTOOLS if name == "tabelle" else FORMTOOLS if name == "form" else ZEICHENTOOLS if name == "zeichen" else TEXTTOOLS if name == "text" else SMARTARTTOOLS if name == "smartart" else BILDTOOLS
            for g in plan["gruppen"]:
                for e in g["knoepfe"]:
                    if e.get("symbol") == "//":
                        continue
                    if e.get("klappe") and not e.get("tun"):
                        fn = getattr(self.b, "menue_" + e["klappe"], None)
                        if fn:
                            kn = DropdownKnopf(); kn.setAutoRaise(True)
                            kn.setIcon(icons.icon(e["symbol"], ICON_GROSS)); kn.setToolTip(e["name"])
                            kn.menue_setzen(fn(), geteilt=False)
                            self.z3.addWidget(kn)
                        continue
                    if not e.get("tun"):
                        continue
                    self.z3.addWidget(self._knopf(e["symbol"], e["name"], e["tun"]))
                self._trenner(self.z3)
            self.z3.addStretch(1)
            self.zusammenhang.show()
        elif not sichtbar and self._kontext_name == name:
            self._kontext_name = None
            self.zusammenhang.hide()

    def aktualisieren(self, hat_dokument: bool | None = None) -> None:
        import shiboken6
        self.schalter = [e for e in self.schalter if shiboken6.isValid(e[0])]              # abgebaute Knöpfe der Kontext-Leiste
        for k, name in self.schalter:
            a = k.defaultAction()
            a.blockSignals(True)
            a.setChecked(bool(self.b.zustand(name)))
            a.blockSignals(False)
        if hat_dokument is not None:
            import shiboken6
            self.knoepfe = [e for e in self.knoepfe if shiboken6.isValid(e[0])]       # Knöpfe der Bildleiste können inzwischen abgebaut sein
            for k, name, braucht in self.knoepfe:
                if braucht and not k.property("fehlt"):
                    k.setEnabled(hat_dokument)
