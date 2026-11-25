"""Grundgerüst für kleine Dialoge: Formular, optionale Vorschau, OK/Abbrechen und Zusatzknöpfe wie „Entfernen“."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QDialog, QPushButton, QWidget

from vcl.qt.widgets.bausteine.basis.raster import Anordnung, PlanRaster, kanten_anordnung

from vcl.qt.widgets.bausteine.felder.formular_gitter import FormularGitter, felder_angleichen
from framework.datentypen.farben import Farbe
from writer.baukasten.basis.mass import ICON_NORMAL, RAND_KEIN
from vcl.qt.widgets.bausteine.bausteine.knopf.knopf import knopf



class _KnopfLayout(PlanRaster):
    """Zusatzknöpfe links, „Abbrechen“ und „OK“ rechts — in einer Gitterzeile, wenn sie nebeneinander passen; sonst stehen die Zusatzknöpfe
    (umbrechend) in den Gitterzeilen darüber. Ein ``QGridLayout`` (``PlanRaster``): die Zellen folgen der Breite."""
    KNOPF_B, ABSTAND, ZEILE_H = 120, 10, 34

    def __init__(self):
        self._extras: list = []
        self._haupt: list = []
        super().__init__()
        self.setContentsMargins(*RAND_KEIN)                                   # Außenrand kommt vom Fenster (Rolle „fenster“), nicht von der Knopfzeile

    def extra(self, widget) -> None:
        self._extras.append(self.element_widget(widget)); self.invalidate()

    def haupt(self, widget) -> None:
        self._haupt.append(self.element_widget(widget)); self.invalidate()

    def _neu_aufnehmen(self, item) -> None:
        self._extras.append(item); self.invalidate()

    def _vergessen(self, it) -> None:
        s = self._schluessel(it)
        self._extras = [i for i in self._extras if self._schluessel(i) is not s]
        self._haupt = [i for i in self._haupt if self._schluessel(i) is not s]

    def sizeHint(self) -> QSize:
        return QSize(self.minimumSize().width(), self.heightForWidth(10000))

    def minimumSize(self) -> QSize:
        b = len(self._haupt) * self.KNOPF_B + max(0, len(self._haupt) - 1) * self.ABSTAND
        e = max((i.minimumSize().width() for i in self._extras), default=0)
        m = self.contentsMargins()
        return QSize(max(b, e) + m.left() + m.right(), self.ZEILE_H + m.top() + m.bottom())

    def _anordnung(self, w: int) -> Anordnung:
        plaetze, hoehe = self._plan(w)
        return kanten_anordnung([(it, x, y, bw, self.ZEILE_H) for it, x, y, bw in plaetze], w, hoehe)

    def _plan(self, w: int):
        a = self.ABSTAND
        breiten = [max(i.sizeHint().width(), i.minimumSize().width()) for i in self._extras]
        eb = sum(breiten) + a * max(0, len(breiten) - 1)
        hb = len(self._haupt) * self.KNOPF_B + max(0, len(self._haupt) - 1) * a
        out, y = [], 0
        if self._extras and eb + a + hb > w:                              # zu eng für eine Zeile: Zusatzknöpfe oben, umbrechend
            x = 0
            if len(breiten) == 1:
                breiten = [w]                                              # ein einzelner Zusatzknopf allein in seiner Zeile: volle Breite wie die Felder
            for it, bw in zip(self._extras, breiten):
                if x > 0 and x + bw > w:
                    x = 0; y += self.ZEILE_H + a
                out.append((it, x, y, min(bw, w))); x += bw + a
            y += self.ZEILE_H + a
            hoehe = y + self.ZEILE_H
        else:
            x = 0
            for it, bw in zip(self._extras, breiten):
                out.append((it, x, 0, bw)); x += bw + a
            hoehe = self.ZEILE_H
        x = w - hb
        for it in self._haupt:
            out.append((it, max(0, x), y, self.KNOPF_B)); x += self.KNOPF_B + a
        return out, hoehe


class Knopfzeile(QWidget):
    """Die Knopfzeile unten in jedem Fenster — der einzige Ort, der sie baut: links Zusatzknöpfe, rechts „Abbrechen“ und „OK“ (gleich breit).
    Passen alle nebeneinander, stehen sie in einer Zeile; sonst rücken die Zusatzknöpfe in eine Zeile darüber.
    ``nur_ok`` lässt „Abbrechen“ weg, ``schliessen`` macht aus dem einen Knopf „Schließen“."""

    def __init__(self, dialog: QDialog, *links: QPushButton, bei_ok: Callable | None = None, ok_text: str = "OK",
                 abbrechen_text: str = "Abbrechen", nur_ok: bool = False, schliessen: bool = False):
        super().__init__()
        self.dialog = dialog
        self.zeile = _KnopfLayout(); self.setLayout(self.zeile)
        self.zeile.setProperty("schmal_nein", True)                          # ein fertiger Baustein: der Notbehelf `schmal_machen` darf ihn nicht umbauen
        for k in links:
            self.zusatz_knopf(k)
        if schliessen:
            ok_text, nur_ok, bei_ok = "Schließen", True, dialog.reject
        self.abbrechen, self.ok = knopf("standard", abbrechen_text), knopf("standard", ok_text, standard=True)
        self.abbrechen.setIcon(_symbol("kreuz")); self.ok.setIcon(_symbol("haken"))
        for k in (self.abbrechen, self.ok):                                  # wie in der Vorlage: breite Knöpfe mit Symbol
            k.setIconSize(QSize(ICON_NORMAL, ICON_NORMAL))
        self.abbrechen.clicked.connect(dialog.reject); self.ok.clicked.connect(bei_ok or dialog.accept)
        if not nur_ok:
            self.zeile.haupt(self.abbrechen)
        self.zeile.haupt(self.ok)
        felder_angleichen(self)                                              # Knöpfe in FELDHOEHE wie die Felder

    def zusatz_knopf(self, k: QPushButton) -> QPushButton:
        self.zeile.extra(k)
        return k

    def zusatz(self, text: str, aktion: Callable | None = None, *, schliesst: bool = True) -> QPushButton:
        """Knopf neben OK/Abbrechen (z. B. „Entfernen“); ``schliesst`` beendet das Fenster mit OK."""
        k = knopf("standard", text)
        def klick():
            if aktion:
                aktion()
            if schliesst:
                self.dialog.accept()
        k.clicked.connect(klick)
        return self.zusatz_knopf(k)


def knopfzeile(dialog: QDialog, *links: QPushButton, **kw) -> Knopfzeile:
    """Eine Knopfzeile für ``dialog`` (zum Einsetzen in ein Layout); Wahlmöglichkeiten wie bei ``Knopfzeile``."""
    return Knopfzeile(dialog, *links, **kw)


def fussleiste(dialog: QDialog, layout, *links: QPushButton, bei_ok: Callable | None = None, ok_text: str = "OK",
               abbrechen_text: str = "Abbrechen", nur_ok: bool = False) -> QPushButton:
    """Knopfzeile unten ins ``layout`` setzen. Gibt den OK-Knopf zurück (``bei_ok`` ersetzt ``accept``, z. B. zum Prüfen vor dem Schließen)."""
    z = Knopfzeile(dialog, *links, bei_ok=bei_ok, ok_text=ok_text, abbrechen_text=abbrechen_text, nur_ok=nur_ok)
    layout.addWidget(z)
    return z.ok


def _symbol(art: str):
    """Lucide-Symbol für Abbrechen oder Bestätigen."""
    from vcl.qt.widgets.bausteine.bauteile import symbole
    return symbole.icon("x" if art == "kreuz" else "check", ICON_NORMAL)


class VorschauFlaeche(QWidget):
    """Weißes Blatt, auf das der Dialog mit ``zeichne(painter, rect)`` seine Vorschau malt."""

    def __init__(self, zeichne: Callable[[QPainter, QRect], None], hoehe: int = 120, flaeche: bool = True):
        """``flaeche=False``: kein weißes Feld mit Rand; ``zeichne`` malt direkt auf den Fensterhintergrund (z. B. ein einzelnes Blatt)."""
        super().__init__()
        self._zeichne = zeichne
        self._flaeche = flaeche
        self.setMinimumHeight(hoehe)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if self._flaeche:
            p.fillRect(self.rect(), QColor(Farbe.PAPIER))
            p.setPen(self.palette().mid().color()); p.drawRect(self.rect().adjusted(0, 0, -1, -1))
        self._zeichne(p, self.rect().adjusted(8, 8, -8, -8))


class DialogRahmen(QDialog):
    """Unterklassen füllen ``self.form`` (``zeile(...)``) und liefern ``ergebnis()``. Wer sich ändert, ruft ``aktualisieren()``."""

    def __init__(self, parent=None, titel: str = "", vorschau: Callable[[QPainter, QRect], None] | None = None):
        super().__init__(parent)
        self.setWindowTitle(titel)
        from vcl.qt.widgets.bausteine.geruest.rollen import spalte
        v = spalte("fenster", self)
        self.form = FormularGitter(); self.form.einspaltig = True; self.form.beschriftung_natuerlich = True
        v.addLayout(self.form)
        self.vorschau = VorschauFlaeche(vorschau) if vorschau else None
        if self.vorschau:
            v.addWidget(self.vorschau)
        self.knoepfe = Knopfzeile(self)
        v.addWidget(self.knoepfe, 1)                                   # überzählige Höhe bekommt die Knopfzeile (wie beim früheren Formular), nicht das Formular

    def zeile(self, beschriftung: str, widget) -> None:
        self.form.zeile(beschriftung, widget)

    def zusatzknopf(self, text: str, aktion: Callable | None = None, *, schliesst: bool = True) -> QPushButton:
        """Knopf neben OK/Abbrechen (z. B. „Entfernen“); ``schliesst`` beendet den Dialog mit OK."""
        return self.knoepfe.zusatz(text, aktion, schliesst=schliesst)

    def aktualisieren(self, *_) -> None:
        if self.vorschau:
            self.vorschau.update()

    def ergebnis(self):
        raise NotImplementedError

    def showEvent(self, e) -> None:
        """Beim ersten Anzeigen: aufeinanderfolgende kurze Ankreuzfelder, Optionen und Knöpfe einer Gitterspalte kommen ins ``KartenRaster``."""
        if not getattr(self, "_raster_geordnet", False):
            self._raster_geordnet = True
            from vcl.qt.widgets.bausteine.felder.karten_raster import kurze_gruppen_ins_raster
            kurze_gruppen_ins_raster(self)
        super().showEvent(e)
