"""Drucken und Druckvorschau des Dokuments: dieselbe Layoutberechnung und derselbe Renderer wie die Zeichenfläche und das PDF.

Seitenauswahl und Blattseiten (vorder/rück), mehrere Seiten pro Blatt, anderes Papier, Kopien, Sortierung und beidseitiger Druck folgen der Wahl des
Druckfensters. Die Vorschau rastert dieselben Seiten.
"""
from __future__ import annotations

import math

from PySide6.QtCore import QMarginsF, QRectF, QSizeF, Qt
from PySide6.QtGui import QImage, QPageLayout, QPageSize, QPainter

from lunivo_writer.adapter.qt.rendering import QtRenderBackend
from lunivo_writer.core.document import Dokument
from lunivo_writer.core.geometry import mm_to_px
from lunivo_writer.core.layout import LayoutEngine
from lunivo_writer.core.layout import formatwerte as F
from lunivo_writer.core.rendering import DokumentRenderer

PAPIER = {"A3": (297, 420), "A4": (210, 297), "A5": (148, 210), "B5": (176, 250), "Letter": (216, 279), "Legal": (216, 356)}
PRO_BLATT = {1: (1, 1), 2: (2, 1), 4: (2, 2), 6: (3, 2), 9: (3, 3), 16: (4, 4)}


def papier_name(b_mm: float, h_mm: float) -> str:
    """„A4“ für 210 × 297 (mit 2 mm Toleranz, in beiden Lagen), sonst „Benutzerdefiniert“."""
    kurz, lang = sorted((b_mm, h_mm))
    for n, (b, h) in PAPIER.items():
        if abs(kurz - b) <= 2 and abs(lang - h) <= 2:
            return n
    return "Benutzerdefiniert"


def bereich_lesen(text: str, gesamt: int) -> list | None:
    """„1-3, 5“ → [1, 2, 3, 5]. Seiten außerhalb 1..gesamt fallen weg; ungültige Eingabe oder nichts Übriges → None."""
    seiten: list = []
    for teil in text.replace(";", ",").split(","):
        teil = teil.strip()
        if not teil:
            continue
        try:
            if "-" in teil:
                a, _, b = teil.partition("-")
                von, bis = (int(a) if a.strip() else 1), (int(b) if b.strip() else gesamt)
            else:
                von = bis = int(teil)
        except ValueError:
            return None
        if von > bis:
            von, bis = bis, von
        seiten += [n for n in range(max(1, von), min(gesamt, bis) + 1) if n not in seiten]
    return seiten or None


def seiten_nach_wahl(ein: dict, gesamt: int) -> list:
    """Welche Seiten das Druckfenster meint (aufsteigend); ohne gültigen Bereich alle."""
    alle = list(range(1, gesamt + 1))
    if ein.get("bereich") == "seiten":
        alle = bereich_lesen(ein.get("seiten_text", ""), gesamt) or []
        alle.sort()
    wahl = ein.get("blattseiten", "alle")
    if wahl == "vorder":
        alle = [n for n in alle if n % 2 == 1]
    elif wahl == "rueck":
        alle = [n for n in alle if n % 2 == 0]
    return alle


def blatt_zeichnen(p: QPainter, rect: QRectF, bilder: list, pro_blatt: int, rand: float = 0.0) -> None:
    """Setzt die Seitenbilder in einem Raster auf das Blatt; jedes wird ins eigene Feld eingepasst (Seitenverhältnis bleibt)."""
    sp, ze = PRO_BLATT.get(pro_blatt, (1, 1))
    if rect.width() > rect.height() and pro_blatt in (2, 6):        # Querblatt: Raster drehen
        sp, ze = ze, sp
    zw, zh = rect.width() / sp, rect.height() / ze
    p.setRenderHint(QPainter.SmoothPixmapTransform)
    for i, img in enumerate(bilder[:sp * ze]):
        feld = QRectF(rect.left() + (i % sp) * zw + rand, rect.top() + (i // sp) * zh + rand, zw - 2 * rand, zh - 2 * rand)
        if img.isNull():
            continue
        f = min(feld.width() / img.width(), feld.height() / img.height())
        w, h = img.width() * f, img.height() * f
        p.drawImage(QRectF(feld.left() + (feld.width() - w) / 2, feld.top() + (feld.height() - h) / 2, w, h), img)


class Ausgabe:
    """Das Dokument einmal gesetzt; jede Seite lässt sich in beliebiger Größe rastern oder auf einen Zeichner malen (Vorschau, Druck)."""

    def __init__(self, dokument: Dokument, engine=None, nur_formular: bool = False, optionen: dict | None = None):
        if nur_formular:                                   # „Nur Formulardaten drucken“: in einer Kopie bleibt nur der Inhalt der Felder sichtbar
            import copy
            from lunivo_writer.editor.dokument import formular
            dokument = copy.deepcopy(dokument)
            formular.nur_formulardaten(dokument)
        self.dokument = dokument
        opt = optionen or {}
        self._layout = LayoutEngine(engine, {"versteckt": True} if opt.get("versteckt") else None)
        self._erg = self._layout.berechnen(dokument)
        self._blasen = opt.get("blasen")                    # ``{"konfig": sprechblasen.konfig_lesen, "schrift": "mittel"}`` oder None
        self._blasen_je_seite = self._blasen_sammeln() if self._blasen else {}
        self._renderer = DokumentRenderer(self._layout.engine)
        self._grund = F.schrift(dict(dokument.standardformat))

    def anzahl(self) -> int:
        return len(self._erg.seiten)

    def seite_mm(self, n: int) -> tuple:
        """Breite und Höhe der Seite ``n`` (ab 1) in Millimetern."""
        e = self._erg.seiten[n - 1].einrichtung
        return (e.width_mm, e.height_mm) if e is not None else (210.0, 297.0)

    def groesse_px(self, n: int, zoom: float = 1.0) -> tuple:
        """Größe der Seite n bei 96 dpi mal Zoom."""
        b, h = self.seite_mm(n)
        return max(1, round(mm_to_px(b) * zoom)), max(1, round(mm_to_px(h) * zoom))

    def _blasen_sammeln(self) -> dict:
        """Seite (0-basiert) → [(Blase, y der Textstelle auf dem Blatt)] der Kommentare und Änderungen, die als Sprechblasen neben der Seite stehen."""
        from lunivo_writer.core.editing import Bearbeitungssitzung
        from lunivo_writer.core.editing.suche import offset_zu_position
        from lunivo_writer.editor.objekte import sprechblasen as SB
        k = self._blasen["konfig"]
        if not SB.aktiv(k):
            return {}
        sitzung = Bearbeitungssitzung(self.dokument)                      # nur lesen: dasselbe Dokument, keine Kopie
        je_seite: dict = {}
        for bl in SB.sammeln_modell(sitzung, k["verwenden"]):
            pos = offset_zu_position(self.dokument, bl.von)
            stelle = self._erg.cursor(pos.absatz_id, pos.versatz)
            if stelle is not None:
                je_seite.setdefault(stelle[0], []).append((bl, stelle[1].y))
        return je_seite

    def malen(self, p: QPainter, n: int) -> None:
        """Die Seite ``n`` mit dem Ursprung links oben auf den Zeichner malen (Maße in 96-dpi-Bildpunkten). Mit Sprechblasen wird die Seite so verkleinert,
        dass die Blasen daneben auf das Blatt passen."""
        if not self._blasen_je_seite.get(n - 1):
            self._renderer.zeichne_seite(QtRenderBackend(p), self.dokument, self._erg, n - 1, self._grund)
            return
        from PySide6.QtGui import QFont
        from lunivo_writer.editor.objekte import sprechblasen as SB
        k = self._blasen["konfig"]
        b, h = self.groesse_px(n)
        luecke, breite = mm_to_px(SB.LUECKE_MM), mm_to_px(SB.breite_mm(k))
        f = b / (b + luecke + breite)
        rechts = k.get("rand", "Rechts") == "Rechts"
        font = QFont(); font.setPixelSize(max(7, SB.blasen_px(self._blasen.get("schrift", "mittel"))))
        liste = self._blasen_je_seite[n - 1]
        hoehen = [SB.messen(bl, breite, font) for bl, _y in liste]
        ys = SB.stapeln([y for _b, y in liste], hoehen, h)
        p.save()
        p.scale(f, f)
        x_seite = 0.0 if rechts else breite + luecke
        p.save(); p.translate(x_seite, 0)
        self._renderer.zeichne_seite(QtRenderBackend(p), self.dokument, self._erg, n - 1, self._grund)
        p.restore()
        x_blase = b + luecke if rechts else 0.0
        for (bl, y_text), y, hh in zip(liste, ys, hoehen):
            r = QRectF(x_blase, y, breite, hh)
            if k.get("linien", True):
                SB.verbindung(p, bl, x_seite + b if rechts else x_seite, y_text, r, rechts)
            SB.zeichnen(p, bl, r, font, druck=True)
        p.restore()

    def bild(self, n: int, zoom: float = 1.0) -> QImage:
        gr = self.groesse_px(n, zoom)
        bild = QImage(gr[0], gr[1], QImage.Format_RGB32)
        bild.fill(Qt.white)
        p = QPainter(bild)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        p.scale(zoom, zoom)
        self.malen(p, n)
        p.end()
        return bild


class Zwischenseiten(Ausgabe):
    """Die Seiten der Druckvorschau."""

    def __init__(self, dokument: Dokument, opt: dict | None = None):
        super().__init__(dokument, optionen=opt)


def seitenzahl(dokument: Dokument) -> int:
    return Ausgabe(dokument).anzahl()


def vorschau_bild(dokument: Dokument, nummern: list, breite_px: int = 640, optionen: dict | None = None) -> list:
    """Die Seiten ``nummern`` (ab 1) auf die gewünschte Breite gerastert — für die Vorschau im Druckfenster."""
    a = Ausgabe(dokument, optionen=optionen)
    aus = []
    for n in nummern:
        if 1 <= n <= a.anzahl():
            aus.append(a.bild(n, breite_px / a.groesse_px(n)[0]))
    return aus


def drucken(printer, dokument: Dokument, ein: dict) -> int:
    """Druckt nach der Wahl ``ein`` (Ergebnis des Druckfensters). → Zahl der gedruckten Blätter."""
    from PySide6.QtPrintSupport import QPrinter
    a = Ausgabe(dokument, nur_formular=bool(ein.get("nur_formular")), optionen=ein.get("optionen"))
    seiten = seiten_nach_wahl(ein, a.anzahl())
    if not seiten:
        return 0
    printer.setCopyCount(max(1, int(ein.get("kopien", 1))))
    printer.setCollateCopies(bool(ein.get("sortieren", True)))
    printer.setDuplex({"lang": QPrinter.DuplexLongSide, "kurz": QPrinter.DuplexShortSide}.get(ein.get("beidseitig", "aus"), QPrinter.DuplexNone))
    pro_blatt = int(ein.get("pro_blatt", 1))
    if ein.get("umgekehrt"):
        seiten.reverse()
    b0, h0 = a.seite_mm(seiten[0])
    b, h = ein.get("papier_mm") or (b0, h0)
    quer = bool(ein.get("quer", b0 > h0))
    kurz, lang = sorted((b, h))
    printer.setPageLayout(QPageLayout(QPageSize(QSizeF(kurz, lang), QPageSize.Millimeter), QPageLayout.Landscape if quer else QPageLayout.Portrait,
                                      printer.pageLayout().margins() if pro_blatt > 1 else QMarginsF(0, 0, 0, 0),
                                      QPageLayout.Millimeter))
    p = QPainter(printer)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.TextAntialiasing)
    anders = pro_blatt > 1 or abs(min(b, h) - min(b0, h0)) > 1 or quer != (b0 > h0)
    feld = printer.pageRect(QPrinter.DevicePixel)
    if not anders:
        faktor = printer.resolution() / 96.0
        for i, n in enumerate(seiten):
            if i:
                printer.newPage()
            p.save()
            p.scale(faktor, faktor)
            a.malen(p, n)
            p.restore()
        p.end()
        return len(seiten)
    breite = int(feld.width() / max(1, PRO_BLATT.get(pro_blatt, (1, 1))[0]))
    for i in range(0, len(seiten), pro_blatt):
        if i:
            printer.newPage()
        bilder = [a.bild(n, breite / a.groesse_px(n)[0]) for n in seiten[i:i + pro_blatt]]
        blatt_zeichnen(p, QRectF(feld), bilder, pro_blatt, rand=feld.width() * 0.01 if pro_blatt > 1 else 0.0)
    p.end()
    return math.ceil(len(seiten) / pro_blatt)
