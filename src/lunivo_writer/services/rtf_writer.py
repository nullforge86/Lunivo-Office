"""RTF direkt schreiben — ohne Umwandlungsprogramm.

Geschrieben wird aus dem ``QTextDocument``: Absätze (Ausrichtung, Einzüge, Abstände, Seitenumbruch, Überschriftenebene),
Zeichenformat (Schrift, Größe, fett, kursiv, unterstrichen, durchgestrichen, hoch/tief, Farbe, Hintergrund), Listen (als
Aufzählungszeichen bzw. Nummer), Tabellen, Bilder (PNG), Seitengröße, Seitenränder, Kopf- und Fußzeile mit Seitenzahl.
Maßeinheit in RTF ist Twip (1/20 pt); 1 px bei 96 dpi = 15 Twip, 1 mm = 56,69 Twip.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTextBlock, QTextCharFormat, QTextDocument, QTextFormat, QTextFrame, QTextListFormat, QTextTable

from lunivo_writer.models.page import HeaderFooter, PageSettings
from lunivo_writer.models.report import IOReport
from lunivo_writer.services.odt_writer import _png, _verluste_melden, bild_aus_format, spannweite

TWIP_PRO_MM = 1440 / 25.4
TWIP_PRO_PX = 15
_AUSRICHTUNG = {"left": r"\ql", "center": r"\qc", "right": r"\qr", "justify": r"\qj"}


def _mm(wert: float) -> int:
    return round(max(0.0, float(wert)) * TWIP_PRO_MM)


def _px(wert: float) -> int:
    return round(float(wert) * TWIP_PRO_PX)


def _text(s: str) -> str:
    """Text RTF-sicher: Steuerzeichen maskiert, alles außerhalb von ASCII als \\uN? (UTF-16, mit Ersatzpaaren)."""
    out = []
    for ch in s:
        o = ord(ch)
        if ch in "\\{}":
            out.append("\\" + ch)
        elif ch == "\t":
            out.append(r"\tab ")
        elif ch in " \n":
            out.append(r"\line ")
        elif ch == " ":
            out.append(r"\~")
        elif 32 <= o < 128:
            out.append(ch)
        elif o < 32:
            continue
        else:
            for einheit in ch.encode("utf-16-le").hex(" ", 2).split():
                wert = int(einheit[2:4] + einheit[0:2], 16)
                out.append(f"\\u{wert - 65536 if wert > 32767 else wert}?")
    return "".join(out)


class _Rtf:
    def __init__(self, doc: QTextDocument, page: PageSettings):
        self.doc, self.page = doc, page
        self.schriften: list[str] = []
        self.farben: list[str] = []
        self.report = IOReport()
        self._gemeldet: set[str] = set()

    def _warn(self, text: str) -> None:
        if text not in self._gemeldet:
            self._gemeldet.add(text)
            self.report.warn(text)

    def schrift(self, name: str) -> int:
        name = name or "Liberation Sans"
        if name not in self.schriften:
            self.schriften.append(name)
        return self.schriften.index(name)

    def farbe(self, c: QColor) -> int:
        n = c.name()
        if n not in self.farben:
            self.farben.append(n)
        return self.farben.index(n) + 1                   # Eintrag 0 ist „Automatisch“

    # ---- Zeichen ---------------------------------------------------------------------------------------------------------------
    def zeichen(self, cf: QTextCharFormat) -> str:
        teile = [r"\plain"]
        fam = cf.fontFamilies() if hasattr(cf, "fontFamilies") else None
        name = (fam[0] if isinstance(fam, (list, tuple)) and fam else None) or self.doc.defaultFont().family()
        teile.append(f"\\f{self.schrift(name)}")
        groesse = cf.fontPointSize() or self.doc.defaultFont().pointSizeF() or 11
        teile.append(f"\\fs{round(groesse * 2)}")
        if cf.fontWeight() >= 600:
            teile.append(r"\b")
        if cf.fontItalic():
            teile.append(r"\i")
        if cf.fontUnderline() or cf.underlineStyle() != QTextCharFormat.NoUnderline:
            teile.append(r"\ul")
        if cf.fontStrikeOut():
            teile.append(r"\strike")
        va = cf.verticalAlignment()
        if va == QTextCharFormat.AlignSuperScript:
            teile.append(r"\super")
        elif va == QTextCharFormat.AlignSubScript:
            teile.append(r"\sub")
        if cf.hasProperty(QTextFormat.ForegroundBrush) and cf.foreground().style() != Qt.NoBrush:
            teile.append(f"\\cf{self.farbe(cf.foreground().color())}")
        if cf.hasProperty(QTextFormat.BackgroundBrush) and cf.background().style() != Qt.NoBrush:
            teile.append(f"\\chcbpat{self.farbe(cf.background().color())}")
        return "".join(teile) + " "

    def bild(self, cf: QTextCharFormat) -> str:
        img = bild_aus_format(self.doc, cf)
        if img is None:
            self._warn("Ein Bild war nicht lesbar und fehlt in der RTF-Datei.")
            return ""
        f = cf.toImageFormat()
        b = f.width() or img.width()
        h = f.height() or img.height()
        return (f"{{\\pict\\pngblip\\picw{img.width()}\\pich{img.height()}\\picwgoal{_px(b)}\\pichgoal{_px(h)}\n"
                + _png(img).hex() + "}")

    # ---- Absätze ---------------------------------------------------------------------------------------------------------------
    def absatz(self, block: QTextBlock, in_tabelle: bool = False) -> str:
        bf = block.blockFormat()
        teile = [r"\pard\plain"]
        if in_tabelle:
            teile.append(r"\intbl")
        a = bf.alignment()
        if a & Qt.AlignHCenter:
            teile.append(r"\qc")
        elif a & Qt.AlignRight:
            teile.append(r"\qr")
        elif a & Qt.AlignJustify:
            teile.append(r"\qj")
        else:
            teile.append(r"\ql")
        links = bf.leftMargin() + bf.indent() * self.doc.indentWidth()
        liste = block.textList()
        praefix = ""
        if liste is not None:
            lf = liste.format()
            links += max(1, lf.indent()) * self.doc.indentWidth()
            stil = lf.style()
            if stil in (QTextListFormat.ListDisc, QTextListFormat.ListCircle, QTextListFormat.ListSquare):
                zeichen = {QTextListFormat.ListDisc: "•", QTextListFormat.ListCircle: "◦", QTextListFormat.ListSquare: "▪"}[stil]
            else:
                zeichen = liste.itemText(block) or f"{liste.itemNumber(block) + 1}."
            # \pntext ist der angezeigte Listentext (für Leser ohne Listen), \pn die Liste selbst (Word, WPS und andere)
            art = r"\pnlvlblt{\pntxtb " + _text(zeichen) + "}" if zeichen in "\u2022\u25e6\u25aa" else (
                r"\pnlvlbody\pndec\pnstart1{\pntxta .}")
            praefix = "{\\pntext " + _text(zeichen) + r"\tab}{\*\pn" + art + "}"
            teile.append(f"\\fi-{_px(self.doc.indentWidth() * 0.6)}")
        elif bf.textIndent():
            teile.append(f"\\fi{_px(bf.textIndent())}")
        if links:
            teile.append(f"\\li{_px(links)}")
        if bf.rightMargin():
            teile.append(f"\\ri{_px(bf.rightMargin())}")
        if bf.topMargin():
            teile.append(f"\\sb{_px(bf.topMargin())}")
        if bf.bottomMargin():
            teile.append(f"\\sa{_px(bf.bottomMargin())}")
        if bf.pageBreakPolicy() & QTextFormat.PageBreak_AlwaysBefore:
            teile.append(r"\pagebb")
        stufe = bf.headingLevel()
        if 1 <= stufe <= 9:
            teile.append(f"\\s{stufe}\\outlinelevel{stufe - 1}")
        out = ["".join(teile) + " " + praefix]
        it = block.begin()
        while not it.atEnd():
            frag = it.fragment()
            cf = frag.charFormat()
            if cf.isImageFormat():
                out.append(self.zeichen(cf) + self.bild(cf))
            else:
                out.append("{" + self.zeichen(cf) + _text(frag.text().replace("￼", "")) + "}")
            it += 1
        return "".join(out)

    def tabelle(self, t: QTextTable) -> str:
        zeilen, spalten = t.rows(), t.columns()
        breite = _mm(self.page.width_mm - self.page.margin_left_mm - self.page.margin_right_mm)
        out = []
        for r in range(zeilen):
            kopf = [r"\trowd\trgaph108"]
            for c in range(spalten):
                zelle = t.cellAt(r, c)
                z0, s0 = zelle.row(), zelle.column()
                breit, hoch = spannweite(t, z0, s0)
                if (z0, s0) == (r, c):
                    kopf.append((r"\clmgf" if breit > 1 else "") + (r"\clvmgf" if hoch > 1 else ""))
                else:
                    kopf.append((r"\clmrg" if s0 < c else "") + (r"\clvmrg" if z0 < r else ""))
                kopf.append(r"\clbrdrt\brdrs\clbrdrl\brdrs\clbrdrb\brdrs\clbrdrr\brdrs" + f"\\cellx{round(breite * (c + 1) / spalten)}")
            out.append("".join(kopf))
            for c in range(spalten):
                zelle = t.cellAt(r, c)
                if (zelle.row(), zelle.column()) != (r, c):           # verbunden: Inhalt steht in der Ursprungszelle
                    out.append(r"\pard\intbl\cell ")
                    continue
                absaetze = []
                it = zelle.begin()
                while not it.atEnd():
                    fr, blk = it.currentFrame(), it.currentBlock()
                    if fr is not None:
                        self._warn("Verschachtelte Tabellen werden in RTF als Text in der Zelle gespeichert.")
                        absaetze.extend(self.absatz(b, True) for b in _bloecke(fr))
                    elif blk.isValid():
                        absaetze.append(self.absatz(blk, True))
                    it += 1
                out.append(r"\par ".join(absaetze) + r"\cell ")
            out.append(r"\row ")
        return "\n".join(out)

    def rahmen(self, frame: QTextFrame) -> list[str]:
        teile: list[str] = []
        it = frame.begin()
        while not it.atEnd():
            fr, blk = it.currentFrame(), it.currentBlock()
            if fr is not None:
                if isinstance(fr, QTextTable):
                    teile.append(("TABELLE", self.tabelle(fr)))
                else:
                    teile.extend(self.rahmen(fr))
            elif blk.isValid():
                teile.append(("ABSATZ", self.absatz(blk)))
            it += 1
        return teile

    # ---- Seite, Kopf- und Fußzeile ---------------------------------------------------------------------------------------------
    def kopf_fuss(self, art: str, hf: HeaderFooter) -> str:
        if hf.is_empty():
            return ""
        zeilen = []
        for zeile in hf.text.split("\n"):
            t = _text(zeile).replace("{PAGES}", r"{\field{\*\fldinst NUMPAGES}{\fldrslt 1}}").replace("{PAGE}", r"\chpgn ")
            zeilen.append(t)
        return ("{\\" + art + r"\pard\plain" + _AUSRICHTUNG.get(hf.align, r"\qc") + " " + r"\par ".join(zeilen) + r"\par}" + "\n")

    def run(self) -> bytes:
        teile = self.rahmen(self.doc.rootFrame())
        koerper = []
        for i, (art, inhalt) in enumerate(teile):
            koerper.append(inhalt)
            letzter = i == len(teile) - 1
            if art == "ABSATZ" and not letzter:
                koerper.append(r"\par" + "\n")
        p = self.page
        seite = (f"\\paperw{_mm(p.width_mm)}\\paperh{_mm(p.height_mm)}\\margl{_mm(p.margin_left_mm)}\\margr{_mm(p.margin_right_mm)}"
                 f"\\margt{_mm(p.margin_top_mm)}\\margb{_mm(p.margin_bottom_mm)}\\headery{_mm(p.kopf_abstand_mm)}"
                 f"\\footery{_mm(p.fuss_abstand_mm)}" + (r"\landscape" if p.landscape else "")
                 + (r"\titlepg" if p.diff_first else ""))
        kopf = self.kopf_fuss("header", p.header) + self.kopf_fuss("footer", p.footer)
        if p.diff_first:
            kopf += self.kopf_fuss("headerf", p.first_header) + self.kopf_fuss("footerf", p.first_footer)
        schriften = "".join(f"{{\\f{i}\\fnil\\fcharset0 {_text(n)};}}" for i, n in enumerate(self.schriften or ["Liberation Sans"]))
        farben = ";" + "".join(f"\\red{int(c[1:3], 16)}\\green{int(c[3:5], 16)}\\blue{int(c[5:7], 16)};" for c in self.farben)
        stile = "".join(f"{{\\s{n}\\outlinelevel{n - 1} heading {n};}}" for n in range(1, 10))
        text = (r"{\rtf1\ansi\ansicpg1252\uc1\deff0" + "\n"
                + "{\\fonttbl" + schriften + "}\n{\\colortbl" + farben + "}\n{\\stylesheet{\\s0 Normal;}" + stile + "}\n"
                + "{\\*\\generator Lunivo Writer;}" + seite + "\n" + kopf + "".join(koerper) + "\n}")
        return text.encode("ascii")


def _bloecke(frame: QTextFrame):
    it = frame.begin()
    while not it.atEnd():
        fr, blk = it.currentFrame(), it.currentBlock()
        if fr is not None:
            yield from _bloecke(fr)
        elif blk.isValid():
            yield blk
        it += 1


def rtf_daten(doc: QTextDocument, page: PageSettings, meta: dict | None = None) -> tuple[bytes, IOReport]:
    """Baut die RTF-Datei im Speicher. → (Inhalt, Bericht über nicht Übernommenes)."""
    w = _Rtf(doc, page)
    daten = w.run()
    _verluste_melden(w.report, page, meta or {}, "RTF")
    return daten, w.report
