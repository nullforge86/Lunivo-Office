"""Gliederung anpassen dialog: aus ``vcl.qt.widgets.dialoge.dokument.liste_dialog`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.farben.darstellung import eigenschaft
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QDialog, QLabel, QListView, QListWidget, QWidget
import copy
from core.listen.mehrstufig import mehrstufig as M
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import VorschauFlaeche, fussleiste
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_ENG, GROESSE_EBENENZEILE, GROESSE_FENSTER_GLIEDERUNG_ANPASSEN, HOEHE_KNOPF_HOCH, RAND_DIALOG_GRUPPE, RAND_KEIN
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import gruppe, FormularGitter, UmbruchSchalter, abschnittstitel
from vcl.qt.widgets.dialoge.dokument.liste_dialog_hilfen import _Zahlenformat
from vcl.qt.widgets.dialoge.dokument.positionen import _Positionen


class GliederungAnpassenDialog(PanelFaehig, QDialog):
    """„Gliederung anpassen“ (auch „Aufzählungszeichen anpassen“): je Ebene Zahlenformat, Zahlenart, Startzahl, Schriftart, Position und Text,
    dazu Nummerieren nach Norm, Verbinden mit Formatvorlage, Text danach und Neu nummerieren nach."""

    def __init__(self, parent=None, defn: dict | None = None, *, titel: str = "Gliederung anpassen"):
        super().__init__(parent)
        self.setWindowTitle(titel); self.resize(*GROESSE_FENSTER_GLIEDERUNG_ANPASSEN)
        self._e = copy.deepcopy((defn or M.VORLAGEN[0][1])["ebenen"])
        self._ebene = 0
        v = _spalte("standard", self)
        grp = gruppe("Zahlenformat"); g = FormularGitter(grp); g.setContentsMargins(*RAND_DIALOG_GRUPPE)
        self.ebenen = QListWidget()                                          # die neun Ebenen in einer Reihe: spart Höhe und Breite
        self.ebenen.setFlow(QListView.LeftToRight); self.ebenen.setWrapping(False); self.ebenen.setSpacing(ABSTAND_ENG)
        self.ebenen.setFixedHeight(HOEHE_KNOPF_HOCH); self.ebenen.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.ebenen.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ebenen.addItems([str(i + 1) for i in range(M.EBENEN)])
        for i in range(self.ebenen.count()):
            self.ebenen.item(i).setSizeHint(QSize(*GROESSE_EBENENZEILE)); self.ebenen.item(i).setTextAlignment(Qt.AlignCenter)
        g.reihe(("Ebene:", self.ebenen))
        self.zf = _Zahlenformat("① bis ⑨ stehen für die Nummern der Ebenen 1 bis 9", breit=True)
        self.format, self.art, self.start, self.schrift = self.zf.format, self.zf.art, self.zf.start, self.zf.schrift
        g.breit(self.zf)
        self.vorher = Auswahlfeld()
        g.zeile("Vorherige Nummerierungsebene:", self.vorher)
        g.breit(self.schrift)
        v.addWidget(grp)
        v.addWidget(abschnittstitel("Vorschau"))
        self.vorschau = VorschauFlaeche(self._male, 150); v.addWidget(self.vorschau)
        self.mehr = knopf("standard", "Erweitern", umschaltbar=True); self.mehr.toggled.connect(self._erweitern)
        self.ok = fussleiste(self, v, self.mehr)
 # ---- erweiterter Teil (wie in der Vorlage unter „Reduzieren“)
        self.unten = QWidget(); ug = FormularGitter(self.unten); ug.setContentsMargins(*RAND_KEIN)
        self.position = _Positionen(); ug.breit(self.position)
        self.norm = UmbruchSchalter("Nummerieren nach Norm")
        self.vorlage = Auswahlfeld(); self.vorlage.addItem("(Keine Formatvorlage)", "")
        from core.formatvorlagen.zeichen import stile
        for n in stile.namen():
            self.vorlage.addItem(n, n)
        self.danach = Auswahlfeld()
        for k, name in (("tab", "Tabstoppzeichen"), ("leer", "Leerzeichen"), ("nichts", "Nichts")):
            self.danach.addItem(name, k)
        self.neu = UmbruchSchalter("Neu nummerieren nach:"); self.neu_ebene = Auswahlfeld()
        ug.breit(self.norm)
        ug.zeile("Verbinden mit Formatvorlage:", self.vorlage)
        ug.zeile("Text danach:", self.danach)
        ug.breit(self.neu); ug.breit(self.neu_ebene)
        v.addWidget(self.unten); self.unten.setVisible(False)
        self.hinweis = QLabel(); eigenschaft(self.hinweis, rolle="warnung"); v.addWidget(self.hinweis)
        self.ebenen.currentRowChanged.connect(self._wechsel)
        for sig in (self.zf.geaendert, self.position.geaendert, self.norm.toggled, self.vorlage.currentIndexChanged, self.danach.currentIndexChanged,
                    self.neu.toggled, self.neu_ebene.currentIndexChanged):
            sig.connect(lambda *_: self._lesen())
        self.vorher.activated.connect(self._vorher_gewaehlt)
        self.ebenen.setCurrentRow(0)

    def _erweitern(self, an: bool) -> None:
        self.mehr.setText("Reduzieren" if an else "Erweitern"); self.unten.setVisible(an)
        self.adjustSize()

    def _wechsel(self, i: int) -> None:
        if i < 0:
            return
        self._ebene = i
        e = self._e[i]
        gesperrt = (self.norm, self.vorlage, self.danach, self.neu, self.neu_ebene)
        for w in gesperrt:
            w.blockSignals(True)
        self.zf.setze(e["format"], e["stil"], e["start"], e.get("zeichen"))
        self.position.setze(e["ausr"], e.get("ausr_art", "links"), e.get("tab", e["einzug"]), e["einzug"])
        self.norm.setChecked(bool(e.get("norm"))); self.vorlage.setCurrentIndex(max(0, self.vorlage.findData(e.get("vorlage", ""))))
        self.danach.setCurrentIndex(max(0, self.danach.findData(e.get("danach", "tab"))))
        self.neu_ebene.clear()
        for k in range(i):
            self.neu_ebene.addItem(f"Ebene {k + 1}", k + 1)
        self.neu.setEnabled(i > 0); self.neu_ebene.setEnabled(i > 0 and e.get("neu") is not None)
        self.neu.setChecked(e.get("neu") is not None and i > 0)
        if e.get("neu") is not None and i > 0:
            self.neu_ebene.setCurrentIndex(max(0, self.neu_ebene.findData(e["neu"])))
        for w in gesperrt:
            w.blockSignals(False)
        self.vorher.clear(); self.vorher.addItem("")
        for k in range(i):
            self.vorher.addItem(f"Ebene {k + 1}", k)
        self.vorher.setEnabled(i > 0)
        self._pruefen()

    def _lesen(self) -> None:
        e = self._e[self._ebene]
        p = self.position.werte()
        e.update(format=self.format.text(), stil=self.art.currentData(), start=self.start.value(), ausr=p["ausr"], einzug=p["einzug"])
        for k, wert, vorgabe in (("tab", p["tab"], p["einzug"]), ("ausr_art", p["ausr_art"], "links"), ("danach", self.danach.currentData(), "tab"),
                                 ("vorlage", self.vorlage.currentData(), ""), ("norm", self.norm.isChecked(), False),
                                 ("neu", self.neu_ebene.currentData() if self.neu.isChecked() and self._ebene > 0 else None, None)):
            if wert == vorgabe or wert is None:
                e.pop(k, None)
            else:
                e[k] = wert
        self.neu_ebene.setEnabled(self._ebene > 0 and self.neu.isChecked())
        if self.zf.zeichen:
            e["zeichen"] = dict(self.zf.zeichen)
        else:
            e.pop("zeichen", None)
        self._pruefen()

    def _vorher_gewaehlt(self, _i: int) -> None:
        k = self.vorher.currentData()
        if k is None:
            return
        zeichen = M.PLATZHALTER[k]
        if zeichen not in self.format.text():
            self.format.setText(zeichen + "." + self.format.text()); self._lesen()

    def _pruefen(self) -> None:
        schlecht = [i + 1 for i, e in enumerate(self._e) if not e["format"]]
        self.hinweis.setText("" if not schlecht else f"Das Zahlenformat der Ebene {schlecht[0]} darf nicht leer sein.")
        self.ok.setEnabled(not schlecht)
        self.vorschau.update()

    def defn(self) -> dict:
        return {"ebenen": [M.ebene_aus(e) for e in self._e]}

    def _male(self, p, rect) -> None:
        """Die neun Ebenen mit ihren Nummern; die gewählte Ebene hat schwarze Linien, die anderen graue (wie in der Vorlage)."""
        d = self.defn()
        zaehler = [0] * M.EBENEN
        r = QRectF(rect).adjusted(10, 8, -10, -8)
        h = r.height() / (M.EBENEN + 1)
        f = p.font(); f.setPixelSize(max(8, int(h * 0.62))); p.setFont(f)
        y = r.top()
        for n in range(1, M.EBENEN + 1):
            M.zaehlen(zaehler, d, n)
            t = M.nummer_der_ebene(d, zaehler, n)
            e = d["ebenen"][n - 1]
            x = r.left() + e["ausr"] * 1.1
            aktuell = n - 1 == self._ebene
            p.setPen(QColor(Farbe.TINTE_DUNKEL)); p.drawText(QRectF(x, y, 120, h), Qt.AlignVCenter | Qt.AlignLeft, t)
            tx = max(r.left() + e.get("tab", e["einzug"]) * 1.1, x + p.fontMetrics().horizontalAdvance(t) + 5)
            pen = QPen(QColor(Farbe.TINTE_DUNKEL if aktuell else Farbe.GRAU_HELL), 3 if aktuell else 3); pen.setCapStyle(Qt.FlatCap)
            p.setPen(pen); p.drawLine(int(tx), int(y + h / 2), int(r.right()), int(y + h / 2))
            if aktuell:                                           # die zweite Zeile des gewählten Absatzes
                y += h * 0.9
                p.drawLine(int(r.left() + e["einzug"] * 1.1), int(y + h / 2), int(r.right()), int(y + h / 2))
            y += h
