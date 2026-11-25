"""Einstellungen für „Silben farbig“: alles, was jemand mit Legasthenie braucht, um es für sich passend zu machen."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.bausteine.haken.haken import haken
from vcl.qt.widgets.bausteine.bausteine.knopf.knopf import knopf

from vcl.qt.widgets.bausteine.basis.darstellung import eigenschaft, farbknopf

from vcl.qt.widgets.bausteine.geruest.rollen import reihe as _reihe, spalte as _spalte

from PySide6.QtWidgets import QCheckBox, QDialog, QLabel, QPushButton, QSpinBox, QTextEdit, QWidget
from vcl.qt.widgets.bausteine.dropdown.auswahlfeld import Auswahlfeld

from vcl.qt.widgets.bausteine.basis.texte import hinweis_stil
from vcl.qt.widgets.bausteine.felder.formular_gitter import UmbruchSchalter, FlussLayout, FormularGitter
from core.editor.text import silbenfarben as S
from PySide6.QtGui import QBrush, QColor, QFont, QSyntaxHighlighter, QTextCharFormat
from vcl.qt.widgets.bausteine import weitere_farben


from vcl.qt.widgets.bausteine.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.basis.dialog_rahmen import knopfzeile
from framework.datentypen.farben import Farbe
from writer.baukasten.basis.mass import GROESSE_KNOPF_SILBE, HOEHE_TEXT_NORMAL, RADIUS_FELD, RAND_KEIN, SCHRIFT_VORSCHAU
from writer.baukasten.basis.mass import DROPDOWN_ZEICHEN_KURZ
class SilbenDialog(PanelFaehig, QDialog):
    def __init__(self, fenster):
        super().__init__(fenster)
        self.w = fenster
        self.setWindowTitle("Silben farbig — Einstellungen")
        self._alt = S.konfig_lesen(fenster.settings)
        k = dict(self._alt)
        v = _spalte("standard", self)
        info = QLabel("Jede Silbe eines Wortes bekommt abwechselnd eine andere Farbe. Das ändert nur die Anzeige — nicht den Text, "
                      "nicht die Datei. Die Silben sind deutsche Sprechsilben (Wan-de-rung); bei Fremdwörtern, Namen und seltenen Zusammensetzungen kann eine Grenze falsch liegen.")
        info.setWordWrap(True)
        hinweis_stil(info)
        v.addWidget(info)
        self.an = haken("standard", "Silben farbig anzeigen")
        self.an.setChecked(k["an"])
        v.addWidget(self.an)
        f = FormularGitter()
        self.palette = Auswahlfeld()
        self.palette.addItems(list(S.PALETTEN))
        self.palette.zeichen(DROPDOWN_ZEICHEN_KURZ)
        self.palette.setCurrentText(k["palette"])
        self.eigene_box = QWidget()
        eh = FlussLayout(); self.eigene_box.setLayout(eh)
        eh.setContentsMargins(*RAND_KEIN)
        self.eigene = list(k["eigene"])
        self.eigene_knoepfe = []
        for i in range(3):
            b = knopf("standard")
            b.setFixedSize(*GROESSE_KNOPF_SILBE)
            b.clicked.connect(lambda _=False, i=i: self._farbe_waehlen(i))
            self.eigene_knoepfe.append(b)
            eh.addWidget(b)
        self.anzahl = QSpinBox()
        self.anzahl.setRange(2, 3)
        self.anzahl.setValue(k["anzahl_eigene"])
        self.anzahl.setPrefix("Anzahl: ")
        eh.addWidget(self.anzahl)
        self.darstellung = Auswahlfeld()
        self.darstellung.addItems(S.DARSTELLUNGEN)
        self.darstellung.zeichen(DROPDOWN_ZEICHEN_KURZ)
        self.darstellung.setCurrentText(k["darstellung"])
        f.reihe(("Farben", self.palette), ("Darstellung", self.darstellung))
        f.zeile("Eigene Farben", self.eigene_box)
        self.fett = haken("standard", "Fett")
        self.fett.setChecked(k["fett"])
        self.mindestens = QSpinBox()
        self.mindestens.setRange(2, 10)
        self.mindestens.setValue(k["mindestens"])
        self.mindestens.setSuffix(" Buchstaben")
        f.reihe(("Wörter einfärben ab", self.mindestens), ("", self.fett))
        self.einsilbig = UmbruchSchalter("Auch Wörter einfärben, die sich nicht teilen lassen")
        self.einsilbig.setChecked(k["einsilbig"])
        f.breit(self.einsilbig)
        self.neu = UmbruchSchalter("Jedes Wort beginnt wieder mit der ersten Farbe")
        self.neu.setChecked(k["neu_pro_wort"])
        f.breit(self.neu)
        self.absatz = UmbruchSchalter("Nur im Absatz mit dem Cursor (ruhigeres Bild)")
        self.absatz.setChecked(k["nur_absatz"])
        f.breit(self.absatz)
        self.drucken = haken("standard", "Auch beim Drucken und im PDF")
        self.drucken.setChecked(k["drucken"])
        f.breit(self.drucken)
        v.addLayout(f)
        v.addWidget(QLabel("Vorschau"))
        self.vorschau = QTextEdit()
        self.vorschau.setReadOnly(True)
        self.vorschau.setPlainText(S.BEISPIEL)
        self.vorschau.setFixedHeight(HOEHE_TEXT_NORMAL)
        eigenschaft(self.vorschau, rolle="vorschautext")
        self._hl = SilbenFarben(self.vorschau.document(), {**k, "an": True, "nur_absatz": False})
        v.addWidget(self.vorschau)
        self.hinweis = QLabel("")
        eigenschaft(self.hinweis, rolle="fehler")
        v.addWidget(self.hinweis)
        standard = knopf("standard", "Standard", aktion=self._standard)
        v.addWidget(knopfzeile(self, standard))
        for c in (self.an, self.fett, self.einsilbig, self.neu, self.absatz, self.drucken):
            c.toggled.connect(lambda *_: self.anwenden())
        for c in (self.palette, self.darstellung):
            c.currentTextChanged.connect(lambda *_: self.anwenden())
        for c in (self.mindestens, self.anzahl):
            c.valueChanged.connect(lambda *_: self.anwenden())
        self._knoepfe_faerben()
        self._zustand()

    def _farbe_waehlen(self, i: int) -> None:
        c = weitere_farben(self, self.eigene[i], "Farbe für Silbe " + str(i + 1))
        if c is not None:
            self.eigene[i] = c.name()
            self._knoepfe_faerben()
            self.anwenden()

    def _knoepfe_faerben(self) -> None:
        for b, c in zip(self.eigene_knoepfe, self.eigene):
            farbknopf(b, c)

    def _zustand(self) -> None:
        eigene = self.palette.currentText() == "Eigene Farben"
        self.eigene_box.setEnabled(eigene)
        self.eigene_knoepfe[2].setEnabled(eigene and self.anzahl.value() == 3)

    def konfig(self) -> dict:
        return {"an": self.an.isChecked(), "palette": self.palette.currentText(), "eigene": list(self.eigene),
                "anzahl_eigene": self.anzahl.value(), "darstellung": self.darstellung.currentText(), "fett": self.fett.isChecked(),
                "einsilbig": self.einsilbig.isChecked(), "neu_pro_wort": self.neu.isChecked(), "mindestens": self.mindestens.value(),
                "nur_absatz": self.absatz.isChecked(), "drucken": self.drucken.isChecked(), "sprache": "de_DE"}

    def anwenden(self) -> None:
        """Wirkt sofort auf Vorschau und alle offenen Dokumente (Abbrechen stellt den alten Stand wieder her)."""
        self._zustand()
        k = self.konfig()
        self._hl.neu_konfigurieren({**k, "an": True, "nur_absatz": False})
        S.konfig_speichern(self.w.settings, k)
        self.w.silbenfarben_anwenden()

    def _standard(self) -> None:
        d = dict(S.STANDARD, an=self.an.isChecked())
        self.palette.setCurrentText(d["palette"]); self.eigene = list(d["eigene"]); self.anzahl.setValue(d["anzahl_eigene"])
        self.darstellung.setCurrentText(d["darstellung"]); self.fett.setChecked(d["fett"]); self.mindestens.setValue(d["mindestens"])
        self.einsilbig.setChecked(d["einsilbig"]); self.neu.setChecked(d["neu_pro_wort"]); self.absatz.setChecked(d["nur_absatz"])
        self.drucken.setChecked(d["drucken"])
        self._knoepfe_faerben()
        self.anwenden()

    def reject(self) -> None:
        S.konfig_speichern(self.w.settings, self._alt)
        self.w.silbenfarben_anwenden()
        super().reject()


# ---- Anzeige der Silbenfarben im Vorschaufeld dieses Fensters (eigenes Qt-Textfeld, kein Dokument) ----------------------------------------
def _silbenformate(k: dict) -> list[QTextCharFormat]:
    out = []
    for hexfarbe in S.farben(k):
        f = QTextCharFormat()
        c = QColor(hexfarbe)
        if k["darstellung"] in ("Schriftfarbe", "Schriftfarbe und Hintergrund"):
            f.setForeground(QBrush(c))
        if k["darstellung"] in ("Hintergrund (Marker)", "Schriftfarbe und Hintergrund"):
            t = QColor(c)
            t.setAlpha(60)
            f.setBackground(QBrush(t))
        if k["fett"]:
            f.setFontWeight(QFont.Bold)
        out.append(f)
    return out


class SilbenFarben(QSyntaxHighlighter):
    """Färbt die Silben im Anzeige-Layout des Dokuments ein; verändert weder Text noch Formatierung."""

    def __init__(self, doc, konfig: dict, aktueller_block=None):
        super().__init__(doc)
        self.k = dict(konfig)
        self._aktuell = aktueller_block or (lambda: -1)
        self._f = _silbenformate(self.k)
        self.rehighlight()

    def highlightBlock(self, text: str) -> None:
        k = self.k
        if k["nur_absatz"] and self.currentBlock().blockNumber() != self._aktuell():
            return
        z = 0
        n = len(self._f)
        for m in S._WORT.finditer(text):
            w = m.group()
            teile = S.silben(w, k["sprache"]) if len(w) >= k["mindestens"] else (w,)
            if len(teile) == 1 and not k["einsilbig"]:
                continue
            if k["neu_pro_wort"]:
                z = 0
            pos = m.start()
            for t in teile:
                self.setFormat(pos, len(t), self._f[z % n])
                pos += len(t)
                z += 1

    def neu_konfigurieren(self, konfig: dict) -> None:
        self.k = dict(konfig)
        self._f = _silbenformate(self.k)
        self.rehighlight()
