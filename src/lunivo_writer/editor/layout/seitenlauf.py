"""Der Seitenlauf: die eigene Dokument-Layout-Klasse von Lunivo (``QAbstractTextDocumentLayout``).

Qt setzt ein Dokument in einer Breite und teilt es in gleich hohe Seiten (``QTextDocumentLayout``). Der Seitenlauf setzt es stattdessen
nach dem Seitenplan (``seitenplan.py``): jeder Bereich hat seine eigene Seitengröße, eigene Ränder und sein eigenes Spaltenraster
(auch ungleich breit); Bereiche beginnen auf neuer Seite oder fortlaufend; ein Absatz läuft über Spalten und Seiten.

Cursor, Markierung, Eingabe-Methode und Undo bleiben beim ``QTextEdit``: es fragt nur diese Klasse nach den Zeilen (``hitTest``,
``blockBoundingRect``) und den ``QTextLayout`` der Absätze — so wie es Calligra Words mit seiner eigenen Layout-Klasse tut. Deshalb braucht
die Schicht kein eigenes Eingabe-Widget.

Koordinaten: Blattraum in Bildpunkten der Anzeige, also schon mit dem Zoom (``zoom_setzen``). Die Blätter stehen untereinander
(``BLATT_ABSTAND_PX`` dazwischen), links ausgerichtet. Schrift und Zeilen setzt Qt über das Zeichengerät des Zooms, Maße des Dokuments
(Ränder, Einzüge, Bildgrößen) multipliziert der Lauf selbst mit dem Zoom.

Stand: Absätze, Listen, Tabellen (auch verschachtelte Tabellen), Bilder in der Zeile, schwebende Rahmen und Fußnoten. Der Editor und der Blattweg
für Druck und PDF verwenden dieselbe Anordnung. Dokumente mit Tabellen, Rahmen oder Fußnoten werden derzeit vollständig neu gesetzt."""
from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import QPointF, QRectF, QSizeF, Qt, QUrl

from lunivo_writer.adapter.qt.geometrie import rect_from_qt, rect_to_qt
from lunivo_writer.core.geometry import Rect
from PySide6.QtGui import (QAbstractTextDocumentLayout, QBrush, QColor, QImage, QPen, QPixmap, QTextDocument, QTextFormat, QTextFrame, QTextFrameFormat, QTextLayout,
                           QTextCharFormat, QTextLength, QTextOption, QTextTable)

from lunivo_writer.editor.layout.seitenplan import Bereich, Seitenplan, spalten as spalten_von
from lunivo_writer.editor.layout.seitenplatz import MIN_ZEILENBREITE, Blatt, Zelle, _Ergebnis, _FreiPlatz, _KoerperPlatz, _Stand  # noqa: F401  (Qt-freie Platzklassen)
from lunivo_writer.modelle.seite import PageSettings, mm_to_px

import os

LAUF_STANDARD = os.environ.get("LUNIVO_SEITENLAUF", "1") != "0"           # "0" schaltet den Seitenlauf ab (Vergleich mit der Qt-Anordnung), im Editor wie im Druck
BLATT_ABSTAND_PX = 32.0                 # grauer Zwischenraum zwischen zwei Blättern (bei 100 % Zoom): die eine Stelle, Editor und Lauf lesen sie hier


def unterstuetzt(doc) -> bool:
    """Kennt der Seitenlauf alles, was im Dokument steht? Absätze, Listen, Tabellen (auch verschachtelt), Bilder in der Zeile und schwebende Rahmen
    (Bilder mit Textumfluss) setzt er; ein Rahmen anderer Art wird wie ein Absatzblock gesetzt. Das Dokument braucht keinen Rückfall."""
    return True


KERN_RECHTECKE = os.environ.get("LUNIVO_KERN_RECHTECKE", "0") == "1"       # "1": die Absatzrechtecke kommen aus dem Kern-Umbruch statt aus dem Seitenlauf (Umstellung, siehe Doku)


class Seitenlauf(QAbstractTextDocumentLayout):
    """Setzt ein ``QTextDocument`` nach dem Seitenplan. Der Plan wird bei jeder Änderung des Dokuments neu aus den Abschnittsumbrüchen gebildet;
    ``basis`` ist die Einrichtung des ersten Abschnitts."""

    def __init__(self, doc, basis: PageSettings, zoom: float = 1.0, rand_oben: float = 0.0, fluss: bool = False, lazy: bool = False):
        super().__init__(doc)
        self.basis = basis
        self.fluss = fluss                                      # Druckkopie: Koordinaten des Textflusses (logische Seiten untereinander, x ab Spaltenrand)
        self.lazy = lazy                                        # erst beim Abfragen setzen (Kopien, die oft geändert werden, bevor jemand fragt)
        self._schmutzig = True
        self._max_breite = 0.0
        self.rand_oben = rand_oben                              # Abstand über dem ersten Blatt (mit Zoom)
        self.zoom = 1.0
        self.plan: Seitenplan | None = None
        self.erg = _Ergebnis()
        self._breite = 0.0
        self._hoehe = 0.0
        self._umbr_zw: list[int] = []
        self._umbr_rev = -1
        self._sig: dict[int, tuple] = {}                         # Blocknummer → womit seine Zeilen zuletzt gesetzt wurden (unveränderte Absätze behalten sie)
        self._geaendert: list[tuple[int, int]] = []              # Bereiche des Dokuments, die sich seit dem letzten Setzen geändert haben
        self.fussnoten: dict | None = None                      # Texte der Fußnoten {Id: Text}: unten auf dem Blatt der Marke, der Text darüber verkürzt sich
        self.reserve: dict = {}                                 # Blattindex → Höhe der Fußnoten (ohne Zoom)
        self._ende: list[tuple] | None = None                    # je Block der Stand nach ihm (Bereich, Blatt, Spalte, y, y0, leer, Abstand unten), für das Setzen ab einer Stelle
        self._plan_sig = None
        self._anzahl = -1
        self.endlos: float | None = None                         # Weblayout: Breite in Bildpunkten, ein endloses Blatt ohne Seitenumbrüche
        self._standard = QTextDocument()                         # hält die Standard-Anordnung, deren Bild-Handler dieser Lauf mitbenutzt
        self._bild_handler_uebernehmen()
        self.zoom_setzen(zoom, neu_setzen=False)

    def _bild_handler_uebernehmen(self) -> None:
        """Bilder in der Zeile: Qt erkennt ein Zeilenobjekt nur, wenn die Layout-Klasse einen Handler für seine Art kennt. Aus Python lässt sich keiner
        selbst anlegen (die Schnittstelle ``QTextObjectInterface`` ist nicht aus Python einzubinden); der Bild-Handler der Standard-Anordnung ist ein
        Kind von deren Layout-Objekt und wird hier mitbenutzt — Größe (mit Zoom über das Zeichengerät) und Zeichnen bleiben wie bei Qt."""
        for kind in self._standard.documentLayout().children():
            if kind.metaObject().className() == "QTextImageHandler":
                self.registerHandler(QTextFormat.ImageObject, kind)
                return

    def zoom_setzen(self, zoom: float, neu_setzen: bool = True) -> None:
        """Die Anzeigegröße: alle Maße und die Schrift des Laufs werden mit ``zoom`` gesetzt (Schrift über das Zeichengerät, wie bei Qt)."""
        from lunivo_writer.editor.seite.seiten_aufteilung import zoom_device
        self.zoom = float(zoom)
        self._sig.clear()
        self.setPaintDevice(zoom_device(self.zoom))
        if neu_setzen:
            self.anordnen()
            self.documentSizeChanged.emit(QSizeF(self._breite, self._hoehe))

    def endlos_setzen(self, breite_px: float | None, neu_setzen: bool = True) -> None:
        """Weblayout an (Breite) oder aus (None): ein endloses Blatt dieser Breite statt der Blätter der Seiteneinrichtung."""
        self.endlos = breite_px
        if neu_setzen:
            self.anordnen()
            self.documentSizeChanged.emit(QSizeF(self._breite, self._hoehe))

    def _plan(self) -> Seitenplan:
        if self.endlos is None:
            return Seitenplan.aus_dokument(self.document(), self.basis)
        from lunivo_writer.modelle.seite import px_to_mm
        web = PageSettings(width_mm=px_to_mm(self.endlos), height_mm=1_000_000.0, margin_left_mm=8.0, margin_right_mm=8.0, margin_top_mm=8.0,
                           margin_bottom_mm=8.0)
        return Seitenplan([Bereich(0, web, "naechste", 0, 0, True, spalten=spalten_von(web))])

    # ---- Anordnen ------------------------------------------------------------------------------------------------------
    def voll_setzen(self) -> None:
        """Alles neu setzen (nach einer Änderung von Seite, Zoom oder Weblayout), nicht nur ab dem geänderten Absatz."""
        self._ende = None
        self._sig.clear()
        self.anordnen()

    def anordnen(self) -> None:
        """Das Dokument setzen; mit Fußnoten am Seitenfuß so oft, bis Text und Platz unten zueinander passen."""
        self._setzen()
        if not self.fussnoten or self.fluss:
            return
        from lunivo_writer.editor.seite import fussnoten as FN
        fabrik = FN._notendoc_fabrik(self.fussnoten, FN._notenschrift(self.document()), self.basis.content_width_px)
        for _runde in range(FN.NOTEN_RUNDEN // 6):
            stellen = FN._fussnoten_stellen(self.document())
            je_blatt: dict = {}
            for nr, (pos, nid, _l) in enumerate(stellen, start=1):
                b = self.document().findBlock(pos)
                tl = b.layout()
                y = tl.position().y() + (tl.lineForTextPosition(pos - b.position()).y() if tl.lineCount() else 0.0)
                je_blatt.setdefault(self.blatt_bei_y(y + 1.0), []).append((nr, nid))
            neu = {k: min(FN._notenhoehe(e, fabrik), self.erg.blaetter[k].text_hoehe / self.zoom * FN.NOTEN_SEITENANTEIL) for k, e in je_blatt.items()}
            platz = {}
            for k, e in je_blatt.items():
                h = FN._notenhoehe(e, fabrik)
                y = self.erg.blaetter[k].text_hoehe / self.zoom - h + FN.NOTEN_TRENNER
                eintr = []
                for nr, nid in e:
                    nd = fabrik(nr, nid)
                    eintr.append((y, nd, nid)); y += nd.size().height() + FN.NOTEN_ABSTAND
                platz[k] = {"hoehe": h, "noten": eintr}
            self.erg.fussnoten = platz
            if neu == self.reserve:
                return
            self.reserve = neu
            self._ende = None
            self._setzen()

    def _setzen(self) -> None:
        """Das Dokument setzen. Bei reinem Text (keine Tabellen und Rahmen) nur ab dem ersten geänderten Absatz — und nur bis zu dem, an dem
        Blatt, Spalte und Höhe wieder dieselben sind wie beim letzten Mal; der Rest bleibt, wie er war."""
        self._schmutzig = False
        doc = self.document()
        self.plan = self._plan()
        self._max_breite = max((mm_to_px(b.seite.width_mm) * self.zoom for b in self.plan.bereiche), default=0.0)
        nur_absaetze = not doc.rootFrame().childFrames() and not self.fussnoten
        plan_sig = (self.endlos, self.zoom, tuple(
            (round(b.seite.width_mm, 2), round(b.seite.height_mm, 2), round(b.seite.margin_left_mm, 2), round(b.seite.margin_right_mm, 2),
             round(b.seite.margin_top_mm, 2), round(b.seite.margin_bottom_mm, 2), b.neue_seite, b.auf_seite, tuple((round(c.x, 1), round(c.breite, 1)) for c in b.spalten))
            for b in self.plan.bereiche))
        start, bereich_index, platz = 0, -1, None
        erg = _Ergebnis()
        letzter = -1
        inkr, alte_blaetter, alte_bs = False, [], {}
        if nur_absaetze and self._ende is not None and plan_sig == self._plan_sig and self.erg.blaetter and self._geaendert:
            erste = max(0, min(doc.findBlock(max(0, a)).blockNumber() for a, _e in self._geaendert) - 1)      # ein Absatz davor: „nicht vom nächsten trennen“ blickt voraus
            letzter = max(doc.findBlock(max(0, e)).blockNumber() for _a, e in self._geaendert)
            if 0 <= erste <= len(self._ende):
                erg, inkr = self.erg, True
                if erste > 0:
                    bi, blatt, spalte, y, y0, leer, unten = self._ende[erste - 1]
                    alte_blaetter, alte_bs = erg.blaetter[blatt + 1:], dict(erg.bereich_start)
                    del erg.blaetter[blatt + 1:]
                    erg.bereich_start = {b: k for b, k in erg.bereich_start.items() if k <= blatt}
                    platz = _KoerperPlatz(self, self.plan.bereiche[bi], _Stand(erg.blaetter[blatt], spalte, y, leer, y0), erg)
                    platz._unten = unten
                    bereich_index, start = bi, erste
                else:                                                  # ab dem ersten Absatz: die Blätter entstehen neu, die alten liegen für den Abgleich bereit
                    alte_blaetter, alte_bs = erg.blaetter, dict(erg.bereich_start)
                    erg.blaetter, erg.bereich_start = [], {}
        self._plan_sig = plan_sig
        gleich_viele = doc.blockCount() == self._anzahl
        self._anzahl = doc.blockCount()
        if start == 0 and not inkr:
            self._ende = [] if nur_absaetze else None
        alte_ende = self._ende[start:] if inkr else []
        if inkr:
            del self._ende[start:]
        es = doc.rootFrame().begin() if start == 0 else None
        block_it = doc.findBlockByNumber(start) if start else None
        fertig_bei = None
        while True:
            if es is not None:
                if es.atEnd():
                    break
                block = es.currentBlock()
                tabelle = es.currentFrame() if not block.isValid() else None
                bezug = block if block.isValid() else (doc.findBlock(tabelle.firstPosition()) if tabelle is not None else None)
            else:
                if not block_it.isValid():
                    break
                block, tabelle, bezug = block_it, None, block_it
            if bezug is None or not bezug.isValid():
                if es is not None:
                    es += 1
                continue
            nr = self._bereich_von(bezug)
            bereich = self.plan.bereiche[nr]
            if nr != bereich_index:
                bereich_index = nr
                if platz is None:
                    platz = _KoerperPlatz(self, bereich, self._neues_blatt(erg, bereich), erg)
                    erg.bereich_start[nr] = platz.stand.blatt.index
                    versatz = bereich.seite.erste_seite_versatz_px() * self.zoom if self.endlos is None else 0.0
                    platz.stand.y = platz.stand.y0 = versatz            # lange Kopfzeile: der Text der ersten Seite beginnt darunter
                elif bereich.neue_seite and not bereich.auf_seite:
                    platz.stand = self._neues_blatt(erg, bereich)
                    if self.endlos is None and ((bereich.beginn == "gerade" and platz.stand.blatt.index % 2 == 0) or
                                                (bereich.beginn == "ungerade" and platz.stand.blatt.index % 2 == 1)):
                        platz.stand.blatt.leer = True                      # „gerade/ungerade Seite“: davor eine Leerseite
                        platz.stand = self._neues_blatt(erg, bereich)
                    erg.bereich_start[nr] = platz.stand.blatt.index
                    platz.bereich = bereich
                else:                                                  # fortlaufend auf derselben Seite: neue Ränder und Spalten ab hier
                    platz.bereich = bereich
                    platz.stand.blatt.bereich = nr
                    platz.stand.spalte, platz.stand.y0 = 0, platz.stand.y
            if block.isValid():
                self._absatz(block, platz, erg)
            elif isinstance(tabelle, QTextTable):
                self._tabelle(tabelle, platz, erg)
            elif tabelle is not None:
                self._rahmen(tabelle, platz, erg)
            if nur_absaetze and block.isValid():
                st = platz.stand
                zust = (bereich_index, st.blatt.index, st.spalte, round(st.y, 2), round(st.y0, 2), st.leer, round(platz._unten, 2))
                n = block.blockNumber()
                k = n - start
                alt = alte_ende[k] if 0 <= k < len(alte_ende) else None
                self._ende.append(zust)
                if inkr and gleich_viele and n >= letzter and alt == zust:        # ab hier ist alles wie vorher: der Rest bleibt
                    fertig_bei = n
                    self._ende.extend(alte_ende[k + 1:])
                    jetzt = platz.stand.blatt.index                      # die Blätter danach sind unverändert (gleicher Stand): übernehmen
                    erg.blaetter.extend(b for b in alte_blaetter if b.index > jetzt)
                    erg.bereich_start.update({b: kk for b, kk in alte_bs.items() if kk > jetzt})
                    break
            if es is not None:
                es += 1
            else:
                block_it = block_it.next()
        if fertig_bei is None and inkr:
            del erg.blaetter[platz.stand.blatt.index + 1:]
            for k in [k for k in erg.rechtecke if k >= doc.blockCount()]:
                erg.rechtecke.pop(k, None); erg.anfang.pop(k, None); erg.block_blatt.pop(k, None)
            if self._ende is not None:
                del self._ende[doc.blockCount():]
        self.erg = erg
        self._geaendert.clear()
        self._breite = self._max_breite
        self._hoehe = (erg.blaetter[-1].oben + erg.blaetter[-1].hoehe + BLATT_ABSTAND_PX * self.zoom) if erg.blaetter else 0.0

    def _bereich_von(self, block) -> int:
        """Index des Bereichs, in dem der Block steht (über die Abschnittsumbrüche, je Dokumentstand einmal gelesen)."""
        rev = self.document().revision()
        if self._umbr_rev != rev:
            from lunivo_writer.editor.seite import abschnitte as AB
            self._umbr_zw = [n for n, _t, _p in AB.umbrueche(self.document())]
            self._umbr_rev = rev
        abschnitt = sum(1 for n in self._umbr_zw if n < block.blockNumber())
        return self.plan.bereich_von_abschnitt(abschnitt).index

    def _neues_blatt(self, erg: _Ergebnis, bereich: Bereich) -> _Stand:
        oben = (0.0 if self.endlos is not None else self.rand_oben) if not erg.blaetter else erg.blaetter[-1].oben + erg.blaetter[-1].hoehe + BLATT_ABSTAND_PX * self.zoom
        blatt = Blatt(len(erg.blaetter), oben, bereich.seite, bereich.index, self.zoom)
        blatt.x = 0.0 if self.fluss else (self._max_breite - blatt.breite) / 2
        erg.blaetter.append(blatt)
        return _Stand(blatt, 0, 0.0)

    # ---- Absatz ---------------------------------------------------------------------------------------------------------------
    def _absatz(self, block, platz, erg: _Ergebnis) -> None:
        """Einen Absatz setzen: Zeile für Zeile an den Platz (Seitenfluss oder Zelle), mit Rändern, Einzug, Ausrichtung und Zeilenabstand."""
        z = self.zoom
        bf = block.blockFormat()
        if bf.pageBreakPolicy() & bf.PageBreakFlag.PageBreak_AlwaysBefore and self.endlos is None:
            platz.umbruch_vor()
        platz.abstand(max(0.0, bf.topMargin()) * z, vor=True)
        tl = block.layout()
        opt = self.document().defaultTextOption()
        opt.setAlignment(bf.alignment() if bf.alignment() else Qt.AlignLeft)
        opt.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        tl.setTextOption(opt)
        breite_einzug = self.document().indentWidth()
        liste = block.textList()
        rand_links = bf.leftMargin() * z + bf.indent() * breite_einzug * z + (liste.format().indent() * breite_einzug * z if liste is not None else 0.0)
        rand_rechts = bf.rightMargin() * z
        erste = True
        x_min = y_min = float("inf")
        x_max = y_max = float("-inf")
        erster_platz = None
        gesetzt: list = []
        sig = (block.revision(), round(platz.breite() - rand_links - rand_rechts, 2), round(bf.textIndent() * z, 2), int(bf.alignment()),
               tl.lineCount() > 0)
        if self._regeln_an(platz):
            self._absatz_mit_regeln(block, bf, tl, platz, erg, sig, rand_links, rand_rechts)
            return
        if self._wiederverwenden(block, platz, erg, sig):
            # Der Absatz ist unverändert und seine Zeilen stehen schon: nur neu auf den Platz legen (kein Umbrechen und Formen nochmals)
            for i in range(tl.lineCount()):
                zeile = tl.lineAt(i)
                einzug = bf.textIndent() * z if erste else 0.0
                h = self._zeilenhoehe(zeile.height(), bf)
                x0, y, breite = platz.vergeben(h)
                x = x0 + rand_links + einzug
                gesetzt.append((zeile, x, y))
                if erster_platz is None:
                    erster_platz = platz.stelle()
                    if erster_platz is not None:
                        erg.anfang[block.blockNumber()] = erster_platz
                x_min, y_min = min(x_min, x), min(y_min, y)
                x_max, y_max = max(x_max, x0 + breite - rand_rechts), max(y_max, y + h)
                erste = False
            self._absatz_abschluss(block, tl, bf, platz, erg, gesetzt, x_min, y_min, x_max, y_max, erster_platz)
            return
        self._sig[block.blockNumber()] = sig
        tl.beginLayout()
        while True:
            zeile = tl.createLine()
            if not zeile.isValid():
                break
            einzug = bf.textIndent() * z if erste else 0.0
            vorher = platz.breite()
            zeile.setLineWidth(max(10.0, vorher - rand_links - rand_rechts - einzug))
            h = self._zeilenhoehe(zeile.height(), bf)
            x0, y, breite = platz.vergeben(h)
            if abs(breite - vorher) > 0.01:                              # nächste Spalte oder Seite hat eine andere Breite
                zeile.setLineWidth(max(10.0, breite - rand_links - rand_rechts - einzug))
            x = x0 + rand_links + einzug
            gesetzt.append((zeile, x, y))
            if erster_platz is None:
                erster_platz = platz.stelle()
                if erster_platz is not None:
                    erg.anfang[block.blockNumber()] = erster_platz
            x_min, y_min = min(x_min, x), min(y_min, y)
            x_max, y_max = max(x_max, x0 + breite - rand_rechts), max(y_max, y + h)           # das Rechteck eines Absatzes reicht über die ganze Breite (wie bei Qt)
            erste = False
        tl.endLayout()
        self._sig[block.blockNumber()] = (sig[0], sig[1], sig[2], sig[3], True)
        self._absatz_abschluss(block, tl, bf, platz, erg, gesetzt, x_min, y_min, x_max, y_max, erster_platz)

    # ---- Umbruchregeln: zusammenhalten, nicht vom nächsten trennen, Schusterjungen und Hurenkinder ---------------------------------
    def _regeln_an(self, platz) -> bool:
        """Die Umbruchregeln gelten im Seitenfluss mit gleich breiten Spalten (nicht in Zellen, nicht im Fluss der Druckkopie, nicht im Weblayout)."""
        return (isinstance(platz, _KoerperPlatz) and not self.fluss and self.endlos is None
                and len({round(c.breite, 1) for c in platz.bereich.spalten}) == 1)

    def _raender(self, block, platz) -> tuple[float, float, float]:
        """(Rand links, Rand rechts, Einzug der ersten Zeile) eines Absatzes in Bildpunkten mit Zoom."""
        z, bf = self.zoom, block.blockFormat()
        liste = block.textList()
        w = self.document().indentWidth()
        return (bf.leftMargin() * z + bf.indent() * w * z + (liste.format().indent() * w * z if liste is not None else 0.0), bf.rightMargin() * z,
                bf.textIndent() * z)

    def _option_setzen(self, block) -> None:
        bf = block.blockFormat()
        opt = self.document().defaultTextOption()
        opt.setAlignment(bf.alignment() if bf.alignment() else Qt.AlignLeft)
        opt.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        block.layout().setTextOption(opt)

    def _erste_zeilen(self, block, platz, anzahl: int) -> tuple[list[float], int]:
        """Höhen der ersten ``anzahl`` Zeilen eines Absatzes bei der Breite des Platzes (zum Vorausschauen) und seine Zeilenzahl."""
        tl = block.layout()
        if tl is None or not block.isVisible():
            return [], 0
        links, rechts, einzug = self._raender(block, platz)
        bf = block.blockFormat()
        self._option_setzen(block)
        self._sig.pop(block.blockNumber(), None)                       # die Zeilen werden beim Setzen des Absatzes neu gebildet
        tl.beginLayout()
        hs = []
        n = 0
        while True:
            zl = tl.createLine()
            if not zl.isValid():
                break
            zl.setLineWidth(max(10.0, platz.breite() - links - rechts - (einzug if n == 0 else 0.0)))
            if n < anzahl:
                hs.append(self._zeilenhoehe(zl.height(), bf))
            n += 1
        tl.endLayout()
        return hs, n

    def _umbruch_stelle(self, block, bf, platz, hs: list[float]) -> int | None:
        """Vor welcher Zeile (0 = vor dem ganzen Absatz) beginnt die nächste Spalte oder Seite, damit die Umbruchregeln gelten? None: kein Umbruch nötig. Die Regeln selbst stehen
        Qt-frei in ``core/layout/regeln.py``; hier kommen nur die Höhen aus dem Qt-Textsatz."""
        from lunivo_writer.core.layout.regeln import umbruch_stelle
        from lunivo_writer.editor.seite import absatzopt
        st = platz.stand

        def folge():
            b = block
            while True:
                b = b.next()
                if not b.isValid():
                    return
                hn, zn = self._erste_zeilen(b, platz, 2)
                if not hn:
                    return
                w_b = absatzopt.lesen(b.blockFormat())
                yield w_b, hn, b.blockFormat().topMargin() * self.zoom
        return umbruch_stelle([*hs], absatzopt.lesen(bf), platz._hoehe() - st.y, platz._hoehe(), st.leer, folge)

    def _absatz_mit_regeln(self, block, bf, tl, platz, erg: _Ergebnis, sig: tuple, rand_links: float, rand_rechts: float) -> None:
        """Wie ``_absatz``, aber erst alle Zeilen bilden, dann nach den Umbruchregeln auf die Spalten und Blätter verteilen."""
        z = self.zoom
        wieder = self._wiederverwenden(block, platz, erg, sig)
        w0 = platz.breite()
        if wieder:
            zeilen = [tl.lineAt(i) for i in range(tl.lineCount())]
        else:
            self._sig[block.blockNumber()] = sig
            tl.beginLayout()
            zeilen = []
            while True:
                zl = tl.createLine()
                if not zl.isValid():
                    break
                zl.setLineWidth(max(10.0, w0 - rand_links - rand_rechts - (bf.textIndent() * z if not zeilen else 0.0)))
                zeilen.append(zl)
        hs = [self._zeilenhoehe(zl.height(), bf) for zl in zeilen]
        bruch = self._umbruch_stelle(block, bf, platz, hs)
        x_min = y_min = float("inf")
        x_max = y_max = float("-inf")
        erster_platz = None
        gesetzt: list = []
        for i, (zeile, h) in enumerate(zip(zeilen, hs)):
            if i == bruch and not platz.stand.leer:
                platz._weiter()
            x0, y, breite = platz.vergeben(h)
            x = x0 + rand_links + (bf.textIndent() * z if i == 0 else 0.0)
            gesetzt.append((zeile, x, y))
            if erster_platz is None:
                erster_platz = platz.stelle()
                if erster_platz is not None:
                    erg.anfang[block.blockNumber()] = erster_platz
            x_min, y_min = min(x_min, x), min(y_min, y)
            x_max, y_max = max(x_max, x0 + breite - rand_rechts), max(y_max, y + h)
        if not wieder:
            tl.endLayout()
            self._sig[block.blockNumber()] = (sig[0], sig[1], sig[2], sig[3], True)
        self._absatz_abschluss(block, tl, bf, platz, erg, gesetzt, x_min, y_min, x_max, y_max, erster_platz)

    def _wiederverwenden(self, block, platz, erg: _Ergebnis, sig: tuple) -> bool:
        """Kann der Absatz seine Zeilen behalten? Ja, wenn sich weder er noch seine Breite geändert haben, er Zeilen hat, kein schwebender Rahmen
        die Breite einer Zeile verändert und alle Spalten des Bereichs gleich breit sind."""
        if erg.ausschluesse or not isinstance(platz, (_KoerperPlatz, _FreiPlatz)):
            return False
        frueher = self._sig.get(block.blockNumber())
        if frueher is None or frueher[:4] != sig[:4] or not frueher[4] or not sig[4]:
            return False
        b0, b1 = block.position(), block.position() + block.length()
        if any(a < b1 and e >= b0 for a, e in self._geaendert):
            return False
        sp = getattr(platz, "bereich", None)
        return sp is None or all(abs(c.breite - sp.spalten[0].breite) < 0.01 for c in sp.spalten)

    def _absatz_abschluss(self, block, tl, bf, platz, erg: _Ergebnis, gesetzt: list, x_min, y_min, x_max, y_max, erster_platz) -> None:
        z = self.zoom
        if x_min == float("inf"):                                       # leerer Absatz ohne Zeile
            x0, y, _b = platz.vergeben(0.0)
            x_min = x_max = x0
            y_min = y_max = y
        platz.abstand(max(0.0, bf.bottomMargin()) * z, vor=False)
        # Wie bei Qt: der Absatz liegt an der Ecke seines Rechtecks (``blockBoundingRect``), die Zeilen relativ dazu — das übernimmt der Editor
        # beim Schreibmarkenrechteck (Rechteck links oben + Zeilenlage).
        tl.setPosition(QPointF(x_min, y_min))
        for zeile, x, y in gesetzt:
            zeile.setPosition(QPointF(x - x_min, y - y_min))
        erg.rechtecke[block.blockNumber()] = Rect(x_min, y_min, max(1.0, x_max - x_min), max(1.0, y_max - y_min))
        k = platz.blatt_index() if erster_platz is None else erster_platz[0]
        if k is not None:
            erg.block_blatt[block.blockNumber()] = k

    @staticmethod
    def _zeilenhoehe(h: float, bf) -> float:
        """Zeilenhöhe nach Zeilenabstand des Absatzes (Rechnung in ``core/textlayout/paragraph.zeilenhoehe``)."""
        from lunivo_writer.core.textlayout.paragraph import zeilenhoehe
        art, wert = {1: "proportional", 2: "fixed", 3: "min"}.get(int(bf.lineHeightType())), bf.lineHeight()
        return zeilenhoehe(h, art, wert) if art and wert else h

    # ---- Rahmen (schwebende Bilder mit Textumfluss) -----------------------------------------------------------------------
    def _rahmen(self, rahmen: QTextFrame, platz, erg: _Ergebnis) -> None:
        """Ein Rahmen im Text. Schwebend (links oder rechts): am Rand der Spalte an der aktuellen Höhe, der folgende Text läuft darum herum.
        Sonst oder in einer Zelle: der Inhalt steht wie ein Absatzblock im Fluss."""
        z = self.zoom
        fmt = rahmen.frameFormat()
        seite = {QTextFrameFormat.FloatLeft: "links", QTextFrameFormat.FloatRight: "rechts"}.get(fmt.position())
        rand = max(0.0, fmt.margin()) * z
        innen = (max(0.0, fmt.padding()) + max(0.0, fmt.border())) * z
        if seite is None or not isinstance(platz, _KoerperPlatz):
            es = rahmen.begin()
            while not es.atEnd():
                b = es.currentBlock()
                if b.isValid():
                    self._absatz(b, platz, erg)
                elif isinstance(es.currentFrame(), QTextTable):
                    self._tabelle(es.currentFrame(), platz, erg)
                es += 1
            return
        w_fest = fmt.width()
        if w_fest.type() == QTextLength.FixedLength:
            breite = w_fest.rawValue() * z
        elif w_fest.type() == QTextLength.PercentageLength:
            breite = platz.breite() * w_fest.rawValue() / 100.0
        else:
            breite = platz.breite() / 3
        # Inhalt messen (Höhe), dann an die Stelle setzen
        messen = _FreiPlatz(0.0, 0.0, max(10.0, breite))
        marke = len(erg.zellen)
        self._rahmen_inhalt(rahmen, messen, erg)
        del erg.zellen[marke:]
        h_fest = fmt.height()
        hoehe = h_fest.rawValue() * z if h_fest.type() == QTextLength.FixedLength else messen.y
        st = platz.stand
        spalte_links = platz.links()
        w_spalte = platz.breite()
        x = spalte_links + rand if seite == "links" else spalte_links + w_spalte - breite - 2 * innen - rand
        y = st.blatt.oben + st.blatt.text_oben + st.y + rand
        self._rahmen_inhalt(rahmen, _FreiPlatz(x + innen, y + innen, max(10.0, breite)), erg)
        erg.ausschluesse.append((st.blatt.index, st.spalte, Rect(x - rand, y - rand, breite + 2 * innen + 2 * rand, hoehe + 2 * innen + 2 * rand), seite))
        erg.tabellen[rahmen.firstPosition()] = Rect(x, y, breite + 2 * innen, hoehe + 2 * innen)

    def _rahmen_inhalt(self, rahmen: QTextFrame, platz, erg: _Ergebnis) -> None:
        es = rahmen.begin()
        while not es.atEnd():
            b = es.currentBlock()
            if b.isValid():
                self._absatz(b, platz, erg)
            elif isinstance(es.currentFrame(), QTextTable):
                self._tabelle(es.currentFrame(), platz, erg)
            es += 1

    # ---- Tabelle ----------------------------------------------------------------------------------------------------------------
    def _tabelle(self, tabelle: QTextTable, platz, erg: _Ergebnis) -> None:
        """Eine Tabelle setzen: Spaltenbreiten aus den Vorgaben, Zeilenhöhen aus dem Inhalt der Zellen, Zeilen untereinander (im Seitenfluss auf
        das nächste Blatt, wenn eine Zeile nicht mehr passt), Zellen mit Füllung und Rahmen für das Zeichnen."""
        z = self.zoom
        tf = tabelle.format()
        aussen = max(0.0, tf.margin()) * z
        verfuegbar = max(20.0, platz.breite() - 2 * aussen)
        spalten_n, zeilen_n = tabelle.columns(), tabelle.rows()
        if spalten_n == 0 or zeilen_n == 0:
            return
        luecke, polster, rand = max(0.0, tf.cellSpacing()) * z, max(0.0, tf.cellPadding()) * z, max(0.0, tf.border()) * z
        breite_tab = self._tabellenbreite(tf, verfuegbar, z)
        breiten = self._spaltenbreiten(tabelle, tf, breite_tab, luecke, z)
        xs = [luecke]
        for b in breiten[:-1]:
            xs.append(xs[-1] + b + luecke)
        ausr = tf.alignment()
        frei = max(0.0, verfuegbar - breite_tab)
        platz_links_alt = platz.links()
        x0 = platz.links() + aussen + (frei / 2 if ausr & Qt.AlignHCenter else frei if ausr & Qt.AlignRight else 0.0)
        # Zellen je Zeile und ihre Maße
        start: dict = {}
        for r in range(zeilen_n):
            for c in range(spalten_n):
                zelle = tabelle.cellAt(r, c)
                if zelle.isValid() and zelle.row() == r and zelle.column() == c:
                    start[(r, c)] = zelle
        def breite_von(zelle) -> float:
            c, n = zelle.column(), zelle.columnSpan()
            return sum(breiten[c:c + n]) + luecke * (n - 1)
        def innen(zelle) -> tuple[float, float, float, float]:
            cf = zelle.format().toTableCellFormat()
            p = polster
            def pad(eig, wert):
                return max(0.0, wert * z) if cf.hasProperty(eig) else p
            return (pad(QTextFormat.TableCellLeftPadding, cf.leftPadding()), pad(QTextFormat.TableCellTopPadding, cf.topPadding()),
                    pad(QTextFormat.TableCellRightPadding, cf.rightPadding()), pad(QTextFormat.TableCellBottomPadding, cf.bottomPadding()))
        hoehen = [0.0] * zeilen_n
        inhalt_h: dict = {}                                                 # Höhe des Zellinhalts je Zelle (für die senkrechte Ausrichtung)
        zusatz = []                                                         # Zellen über mehrere Zeilen: (Startzeile, Endzeile, nötige Höhe)
        for (r, c), zelle in start.items():
            l, o, rr, u = innen(zelle)
            h_inhalt = self._zellinhalt(zelle, 0.0, 0.0, max(10.0, breite_von(zelle) - l - rr - rand), erg, messen=True)
            h = h_inhalt + o + u + rand                                      # wie Qt: zwei Zeilen teilen sich einen Rahmenstrich
            inhalt_h[(r, c)] = h_inhalt
            if zelle.rowSpan() > 1:
                zusatz.append((r, r + zelle.rowSpan() - 1, h))
            else:
                hoehen[r] = max(hoehen[r], h)
            from lunivo_writer.editor.tabelle.tabelleneigenschaften import Z_MINHOEHE
            if zelle.rowSpan() == 1 and zelle.format().hasProperty(Z_MINHOEHE):
                hoehen[r] = max(hoehen[r], zelle.format().doubleProperty(Z_MINHOEHE) * z)
        for a, b, h in zusatz:                                              # fehlende Höhe geht an die letzte Zeile der Zelle
            fehlt = h - sum(hoehen[a:b + 1]) - luecke * (b - a)
            if fehlt > 0:
                hoehen[b] += fehlt
        # Setzen
        y_zeile = [0.0] * zeilen_n
        oben_tab = None
        platz.abstand(aussen + luecke + rand, vor=True)
        unten_tab = 0.0
        wiederholt: list = []
        kopf_n = min(max(0, tf.headerRowCount()), zeilen_n - 1) if isinstance(platz, _KoerperPlatz) else 0
        for r in range(zeilen_n):
            if kopf_n and r >= kopf_n and not platz.stand.leer and platz.stand.y + hoehen[r] + luecke > platz._hoehe() + 0.01 \
                    and sum(hoehen[:kopf_n]) + hoehen[r] < platz._hoehe():
                platz._weiter()                                             # die Zeile steht auf dem nächsten Blatt: die Kopfzeilen davor wiederholen
                kopf_y = [platz.zeile_vergeben(hoehen[h] + luecke) for h in range(kopf_n)]
                wiederholt.append((kopf_y, platz.links() - platz_links_alt))
            y_zeile[r] = platz.zeile_vergeben(hoehen[r] + luecke)
            if oben_tab is None:
                oben_tab = y_zeile[r]
            unten_tab = max(unten_tab, y_zeile[r] + hoehen[r])
        gesetzt: dict = {}
        for (r, c), zelle in start.items():
            l, o, rr, u = innen(zelle)
            bis = min(zeilen_n - 1, r + zelle.rowSpan() - 1)
            y0 = y_zeile[r]
            h = (y_zeile[bis] + hoehen[bis]) - y0 if bis > r else hoehen[r]
            if bis > r and y_zeile[bis] < y_zeile[r]:                        # Zelle über einen Seitenwechsel: bis zum Ende der Startzeile
                h = hoehen[r]
            x = x0 + xs[c]
            rechteck = Rect(x, y0, breite_von(zelle), h)
            z_neu = Zelle(rechteck, zelle.format(), tf, rand)
            erg.zellen.append(z_neu)
            gesetzt[(r, c)] = z_neu
            frei_h = h - o - u - rand - inhalt_h.get((r, c), 0.0)
            va = zelle.format().verticalAlignment()
            versatz = max(0.0, frei_h) / 2 if va == QTextCharFormat.AlignMiddle else max(0.0, frei_h) if va == QTextCharFormat.AlignBottom else 0.0
            self._zellinhalt(zelle, x + rand / 2 + l, y0 + rand / 2 + o + versatz, max(10.0, breite_von(zelle) - l - rr - rand), erg, messen=False)
        for kopf_y, dx in wiederholt:
            self._kopfzeilen_wiederholen(start, kopf_n, y_zeile, kopf_y, dx, gesetzt, erg)
        if oben_tab is not None:
            erg.tabellen[tabelle.firstPosition()] = Rect(x0, oben_tab, breite_tab, max(1.0, unten_tab - oben_tab))
        platz.abstand(aussen + rand, vor=False)

    def _kopfzeilen_wiederholen(self, start, kopf_n, y_alt, y_neu, dx, gesetzt, erg) -> None:
        """Die Kopfzeilen einer Tabelle noch einmal oben auf dem neuen Blatt: Zellen (Füllung, Rahmen) und die Absätze darin, nur verschoben."""
        for (r, c), zelle in start.items():
            alt = gesetzt.get((r, c))
            if r >= kopf_n or zelle.rowSpan() > 1 or alt is None:
                continue
            dy = y_neu[r] - y_alt[r]
            blocke = []
            b, ende = zelle.firstCursorPosition().block(), zelle.lastCursorPosition().block()
            while b.isValid():
                blocke.append((b.blockNumber(), dx, dy))
                if b == ende:
                    break
                b = b.next()
            erg.kopien.append((Zelle(alt.rechteck.translated(dx, dy), alt.format, alt.tabelle, alt.rand), blocke))

    def _tabellenbreite(self, tf, verfuegbar: float, z: float) -> float:
        w = tf.width()
        if w.type() == QTextLength.FixedLength:
            return min(verfuegbar, max(20.0, w.rawValue() * z))
        if w.type() == QTextLength.PercentageLength:
            return max(20.0, verfuegbar * w.rawValue() / 100.0)
        return verfuegbar

    def _spaltenbreiten(self, tabelle, tf, breite_tab: float, luecke: float, z: float) -> list[float]:
        n = tabelle.columns()
        vorgaben = list(tf.columnWidthConstraints())
        vorgaben += [QTextLength()] * (n - len(vorgaben))
        innen = max(10.0, breite_tab - luecke * (n + 1))
        fest = [(i, v.rawValue() * z) for i, v in enumerate(vorgaben[:n]) if v.type() == QTextLength.FixedLength]
        proz = [(i, innen * v.rawValue() / 100.0) for i, v in enumerate(vorgaben[:n]) if v.type() == QTextLength.PercentageLength]
        frei = [i for i, v in enumerate(vorgaben[:n]) if v.type() == QTextLength.VariableLength]
        b = [0.0] * n
        for i, w in fest + proz:
            b[i] = w
        rest = innen - sum(b)
        for i in frei:
            b[i] = max(10.0, rest / len(frei)) if rest > 0 else 10.0
        summe = sum(b)
        if summe > 0 and abs(summe - innen) > 0.5 and (summe > innen or not frei):    # zu breit oder keine freie Spalte: auf die Tabellenbreite bringen
            b = [w * innen / summe for w in b]
        return b

    def _zellinhalt(self, zelle, x: float, y: float, breite: float, erg: _Ergebnis, messen: bool) -> float:
        """Den Inhalt einer Zelle (Absätze und verschachtelte Tabellen) von (x, y) an setzen. → Höhe des Inhalts."""
        platz = _FreiPlatz(x, y, breite)
        marke = len(erg.zellen)
        es = zelle.begin()
        while not es.atEnd():
            b = es.currentBlock()
            if b.isValid():
                self._absatz(b, platz, erg)
            else:
                f = es.currentFrame()
                if isinstance(f, QTextTable):
                    self._tabelle(f, platz, erg)
                elif f is not None:
                    self._rahmen(f, platz, erg)
            es += 1
        if messen:                                                       # nur messen: die Zellen verschachtelter Tabellen kommen beim Setzen nochmals
            del erg.zellen[marke:]
        return platz.y - y

    # ---- QAbstractTextDocumentLayout ---------------------------------------------------------------------------------------
    def documentChanged(self, position: int, chars_removed: int, chars_added: int) -> None:
        self._geaendert.append((position, position + max(chars_removed, chars_added)))
        if self.lazy:
            self._schmutzig = True
            return
        self.anordnen()
        self.documentSizeChanged.emit(QSizeF(self._breite, self._hoehe))

    def _sicher(self) -> None:
        """Bei einer ``lazy`` gesetzten Kopie: jetzt setzen, wenn seit dem letzten Setzen etwas geändert wurde."""
        if self._schmutzig and self.lazy:
            self.anordnen()

    def draw(self, painter, ctx) -> None:
        """Den Text zeichnen: alle Absätze, die im Zeichenbereich liegen, mit Auswahl und Schreibmarke."""
        self._sicher()
        auswahl = list(ctx.selections) if getattr(ctx, "selections", None) else []
        klipp = ctx.clip if ctx.clip.isValid() else None
        self._tabellen_zeichnen(painter, klipp)
        b = self.document().begin()
        while b.isValid():
            r = self.erg.rechtecke.get(b.blockNumber())
            if r is not None and (klipp is None or r.adjusted(-4, -4, 4, 4).intersects(rect_from_qt(klipp))):
                formate = []
                for s in auswahl:
                    c = s.cursor
                    von, bis = c.selectionStart() - b.position(), c.selectionEnd() - b.position()
                    if bis > 0 and von < b.length():
                        fr = QTextLayout.FormatRange()
                        fr.start, fr.length, fr.format = max(0, von), min(b.length(), bis) - max(0, von), s.format
                        formate.append(fr)
                b.layout().draw(painter, QPointF(0, 0), formate)
                if b.textList() is not None:
                    self._listenzeichen(painter, b)
            b = b.next()
        for zelle, blocke in self.erg.kopien:                                 # wiederholte Kopfzeilen: derselbe Text noch einmal, ohne Auswahl
            if klipp is not None and not zelle.rechteck.adjusted(-4, -4, 4, 4).intersects(rect_from_qt(klipp)):
                continue
            for nr, dx, dy in blocke:
                tl = self.document().findBlockByNumber(nr).layout()
                if tl is not None:
                    tl.draw(painter, QPointF(dx, dy))
        if ctx.cursorPosition >= 0:
            bl = self.document().findBlock(ctx.cursorPosition)
            if bl.isValid():
                bl.layout().drawCursor(painter, QPointF(0, 0), ctx.cursorPosition - bl.position())

    def _listenzeichen(self, painter, block) -> None:
        """Aufzählungszeichen oder Nummer links vor der ersten Zeile eines Listenabsatzes (wie ``QTextDocumentLayout``)."""
        from PySide6.QtGui import QFontMetricsF, QTextListFormat
        liste = block.textList()
        tl = block.layout()
        if tl is None or tl.lineCount() == 0 or liste is None:
            return
        zeile = tl.lineAt(0)
        pos = zeile.position() + tl.position()
        schrift = tl.font()
        fm = QFontMetricsF(schrift, self.paintDevice())
        art = liste.format().style()
        grund_y = pos.y() + zeile.ascent()
        from lunivo_writer.adapter.qt.rendering import QtRenderBackend
        from lunivo_writer.core.geometry import Point, Rect as _Rect
        from lunivo_writer.core.rendering import Style
        backend = QtRenderBackend(painter)
        vorder = block.charFormat().foreground()
        farbe = (vorder.color() if vorder.style() != Qt.NoBrush else QColor("black")).getRgb()
        if art in (QTextListFormat.ListDisc, QTextListFormat.ListCircle, QTextListFormat.ListSquare):
            d = fm.height() / 3.0
            mx, my = pos.x() - d * 1.8, grund_y - fm.ascent() / 2.4
            stil = Style(color=farbe, width=1.0, filled=art != QTextListFormat.ListCircle)
            if art != QTextListFormat.ListSquare:
                backend.draw_ellipse(Point(mx, my), d / 2, d / 2, stil)
            else:
                backend.draw_rect(_Rect(mx - d / 2, my - d / 2, d, d), stil)
        else:
            text = liste.itemText(block)
            backend.draw_text(text, Point(pos.x() - fm.horizontalAdvance(text + " "), grund_y), schrift, Style(color=farbe))

    def _tabellen_zeichnen(self, painter, klipp) -> None:
        """Füllung und Rahmen der Tabellenzellen (hinter dem Text), über das Rendering-Backend. Rahmen je Zelle und Seite, sonst der Rahmen der Tabelle."""
        from lunivo_writer.adapter.qt.dokument import eigenschaften
        from lunivo_writer.adapter.qt.rendering import QtRenderBackend
        from lunivo_writer.core.rendering.tabelle import ausfuehren, zelle_anweisungen
        backend = QtRenderBackend(painter)
        for zelle in self.erg.zellen + [k[0] for k in self.erg.kopien]:
            if klipp is not None and not zelle.rechteck.adjusted(-4, -4, 4, 4).intersects(rect_from_qt(klipp)):
                continue
            if zelle.anweisungen is None:
                zelle.anweisungen = zelle_anweisungen(zelle.rechteck, eigenschaften(zelle.format.toTableCellFormat()), eigenschaften(zelle.tabelle), zelle.rand, self.zoom)
            ausfuehren(backend, zelle.anweisungen)

    def hitTest(self, punkt, genauigkeit) -> int:
        """Die Textposition am Punkt (Blattraum): die nächste Zeile, dann das Zeichen in ihr."""
        self._sicher()
        beste, abstand = None, float("inf")
        b = self.document().begin()
        while b.isValid():
            tl = b.layout()
            for i in range(tl.lineCount()):
                zeile = tl.lineAt(i)
                r = zeile.rect().translated(tl.position())
                dy = 0.0 if r.top() <= punkt.y() <= r.bottom() else min(abs(punkt.y() - r.top()), abs(punkt.y() - r.bottom()))
                dx = 0.0 if r.left() <= punkt.x() <= r.right() else min(abs(punkt.x() - r.left()), abs(punkt.x() - r.right()))     # nebeneinander liegende Spalten
                d = (dx * dx + dy * dy) ** 0.5
                if d < abstand:
                    abstand, beste = d, (b, zeile)
            b = b.next()
        if beste is None:
            return -1 if genauigkeit == Qt.ExactHit else 0
        if genauigkeit == Qt.ExactHit and abstand > 0.0:                    # wie Qt: ein genauer Treffer liegt auf einer Zeile, sonst -1 (nichts getroffen)
            return -1
        b, zeile = beste
        return b.position() + zeile.xToCursor(punkt.x() - b.layout().position().x())

    def pageCount(self) -> int:
        self._sicher()
        if self.fluss:                                               # logische Seiten: eine je Spalte und Blatt
            return max(1, len(self.erg.blaetter) * max(1, len(self.plan.bereiche[-1].spalten) if self.plan else 1))
        return max(1, len(self.erg.blaetter))

    def documentSize(self) -> QSizeF:
        self._sicher()
        if self.fluss and self.erg.blaetter:
            return QSizeF(self.erg.blaetter[-1].seite.spalten_breite_px * self.zoom, self.pageCount() * self.erg.blaetter[-1].fluss_hoehe)
        return QSizeF(self._breite, self._hoehe)

    def frameBoundingRect(self, rahmen) -> QRectF:
        self._sicher()
        if isinstance(rahmen, QTextFrame):
            r = self.erg.tabellen.get(rahmen.firstPosition())
            if r is not None:
                return rect_to_qt(r)
        return QRectF(0, 0, self._breite, self._hoehe)

    def blockBoundingRect(self, block) -> QRectF:
        self._sicher()
        if KERN_RECHTECKE:
            r = self._kern_rechteck(block)
            if r is not None:
                return rect_to_qt(r)
        return rect_to_qt(self.erg.rechtecke.get(block.blockNumber(), Rect()))

    def _kern_rechteck(self, block) -> Rect | None:
        """Das Rechteck des ersten Zeilenstücks des Absatzes aus dem Qt-freien Seitenumbruch (``core/layout``); ``None``, wenn der Absatz dort nicht steht."""
        from lunivo_writer.adapter.qt.dokument import document_from_qt
        from lunivo_writer.core.layout import umbrechen
        from lunivo_writer.dienste.textsatz import standard_engine
        if self.__dict__.get("_kern_stand") != self.document().revision():
            self._kern = umbrechen(document_from_qt(self.document(), self.basis), standard_engine())
            self._kern_stand = self.document().revision()
        ort = self._kern.absaetze.get(self._kern_pfad(block))
        if ort is None or not ort.zeilen:
            return None
        seite, _z, r = ort.zeilen[0]
        return Rect(r.x, r.y, r.width, ort.satz.hoehe)

    def _kern_pfad(self, block):
        """Der Pfad des Absatzes im Kern (Abschnitt, Absatz): wie ``core/editing.absaetze``, nur für Absätze auf der obersten Ebene."""
        return (0, block.blockNumber())

    # ---- Bilder in der Zeile: Größe über den Bild-Handler, Zeichnen hier (Vektor für SVG und Metafile) -------------------------
    def drawInlineObject(self, painter, rechteck, objekt, position: int, format) -> None:
        if not format.isImageFormat():
            return
        bild = self._bild(format.toImageFormat())
        if bild is None or bild.isNull():
            return
        from lunivo_writer.editor.objekte import bilddaten as BD
        BD.zeichnen(painter, rechteck, bild)                            # SVG und Metafile als Vektor, sonst die Bildpunkte

    def _bild(self, f):
        r = self.document().resource(QTextDocument.ImageResource, QUrl(f.name()))
        if isinstance(r, QImage):
            return r
        if isinstance(r, QPixmap):
            return r.toImage()
        bild = QImage(f.name())
        return bild if not bild.isNull() else None

    # ---- Abfragen für Anzeige und Prüfung ------------------------------------------------------------------------------------
    def ort(self, y: float) -> tuple[int, float]:
        """(Blatt 1-basiert, y ab dem oberen Textrand des Blattes) zu einem y des Laufs — für Lesezeichen, Notizen, Verweise und Blasen."""
        self._sicher()
        bl = self.erg.blaetter[self.blatt_bei_y(y + 0.5)]
        return bl.index + 1, y - (bl.oben + bl.text_oben)

    def seitenwechsel(self) -> list[int]:
        """Zeichenstelle, an der jedes weitere Blatt beginnt (der erste Absatz, der dort anfängt) — für „Gehe zu Seite“."""
        self._sicher()
        erste: dict = {}
        for nr, k in self.erg.block_blatt.items():
            if k > 0 and (k not in erste or nr < erste[k]):
                erste[k] = nr
        doc = self.document()
        return sorted(doc.findBlockByNumber(nr).position() for nr in erste.values())

    def seitennummern(self, start: int = 0) -> list[int]:
        """Die angezeigte Seitennummer je Blatt: ab ``start`` + 1 (Einrichtung des Dokuments), „Beginnen mit“ eines Abschnitts setzt neu an."""
        self._sicher()
        versatz, aus = start, []
        wechsel = {k: b for b, k in self.erg.bereich_start.items()}
        for k in range(len(self.erg.blaetter)):
            b = wechsel.get(k)
            if b is not None and self.plan.bereiche[b].seite.seiten_start > 0:
                versatz = self.plan.bereiche[b].seite.seiten_start - 1 - k
            aus.append(k + 1 + versatz)
        return aus

    def zeilennummern(self, art: str = ""):
        """(Blattindex, y, Zeilenhöhe, Nummer) für jede nummerierte Zeile in Blattkoordinaten; ``art`` „seite“: auf jedem Blatt neu ab 1."""
        from lunivo_writer.editor.seite import zeilennummern as ZN
        self._sicher()
        nr, blatt_nr = 0, -1
        b = self.document().begin()
        while b.isValid():
            tl = b.layout()
            if b.isVisible() and tl is not None and not ZN.unterdrueckt(b) and b.blockNumber() in self.erg.rechtecke:
                for i in range(tl.lineCount()):
                    z = tl.lineAt(i)
                    y = tl.position().y() + z.y()
                    k = self.blatt_bei_y(y + 1.0)
                    if art == "seite" and k != blatt_nr:
                        nr = 0
                    blatt_nr = k
                    nr += 1
                    yield k, y, z.height(), nr
            b = b.next()

    def frei_index(self) -> dict:
        """Die frei positionierten Bilder je Blatt (1-basiert) wie ``freie_bilder.koerper_index``, aber nach den Blättern des Laufs:
        {Blatt: [(Angabe, y des Absatzes in der Spalte ohne Zoom, Spalte)]}."""
        from lunivo_writer.editor.objekte import freie_bilder as FB
        self._sicher()
        z = max(self.zoom, 1e-9)
        out: dict = {}
        b = self.document().begin()
        while b.isValid():
            liste = FB.aus_absatz(b.blockFormat())
            anfang = self.erg.anfang.get(b.blockNumber()) if liste else None
            if anfang:
                blatt, spalte, y = anfang
                for i, a in enumerate(liste):
                    out.setdefault(blatt + 1, []).append((dict(a, _blk=b.blockNumber(), _idx=i), y / z, spalte))
            b = b.next()
        return out

    def blatt_von_block(self, blocknummer: int) -> int:
        """Das Blatt, auf dem der Block beginnt (0-basiert)."""
        return self.erg.block_blatt.get(blocknummer, 0)

    @property
    def blaetter(self) -> list[Blatt]:
        return self.erg.blaetter

    def blatt_bei_y(self, y: float) -> int:
        """Das Blatt, auf dem oder nach dem Punkt y (Blattraum) liegt; im Zwischenraum das davor."""
        k = 0
        for b in self.erg.blaetter:
            if y >= b.oben:
                k = b.index
            else:
                break
        return k
