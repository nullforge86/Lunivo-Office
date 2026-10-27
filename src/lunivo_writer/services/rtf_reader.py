"""RTF direkt lesen — ohne Umwandlungsprogramm.

Ein Zerleger für Rich Text Format (Microsoft RTF 1.9): Gruppen ``{…}``, Steuerwörter ``\\wort123``, ``\\'hh`` und ``\\uN``. Übernommen:
Absätze (Ausrichtung, Einzüge, Abstände, Seitenumbruch, Überschriftenebene), Zeichenformat (Schrift, Größe, fett, kursiv,
unterstrichen, durchgestrichen, hoch/tief, Farbe, Hintergrund), Listen (aus dem angezeigten Listentext), Tabellen, Bilder (PNG,
JPEG, EMF mit Bitmap), Seitengröße, Seitenränder, Kopf- und Fußzeile mit Seitenzahl, Titel und Autor. Was fehlt (Fußnoten,
Kommentare, Zeichnungen), meldet der Bericht. Maße in RTF: Twip = 1/20 pt; 15 Twip = 1 px bei 96 dpi.
"""
from __future__ import annotations

import re

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import (QBrush, QColor, QFont, QImage, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument,
                           QTextFormat, QTextFrameFormat, QTextImageFormat, QTextLength, QTextListFormat, QTextTableFormat)

from lunivo_writer.models.page import HeaderFooter, PageSettings
from lunivo_writer.models.report import DocumentIOError, IOReport

GRENZE_BYTES = 512 * 1024 * 1024
TWIP_PRO_MM = 1440 / 25.4
_TOKEN = re.compile(rb"\\([a-zA-Z]{1,32})(-?\d{1,10})? ?|\\'([0-9a-fA-F]{2})|\\(.)|([{}])|([^\\{}\r\n]+)|[\r\n]+", re.S)
_ZEICHEN = {"emdash": "\u2014", "endash": "\u2013", "bullet": "\u2022", "lquote": "\u2018", "rquote": "\u2019",
            "ldblquote": "\u201c", "rdblquote": "\u201d", "emspace": "\u2003", "enspace": "\u2002", "qmspace": "\u2005",
            "tab": "\t", "line": "\u2028", "lbr": "\u2028"}
_SYMBOL = {"~": "\u00a0", "_": "\u2011", "-": "", "{": "{", "}": "}", "\\": "\\", "\n": None, "\r": None}
_KOPF_FUSS = {"header": "header", "headerl": "header", "headerr": "header", "footer": "footer", "footerl": "footer",
              "footerr": "footer", "headerf": "first_header", "footerf": "first_footer"}
_UEBERSPRINGEN = {"info", "stylesheet", "fonttbl", "colortbl", "listtable", "listoverridetable", "revtbl", "rsidtbl",
                  "generator", "xmlnstbl", "themedata", "colorschememapping", "latentstyles", "datastore", "fldinst",
                  "pnseclvl", "pn", "nonshppict", "object", "objdata", "template", "userprops", "docvar", "bkmkstart",
                  "bkmkend", "pgdsctbl", "filetbl", "mmathPr", "wgrffmtfilter", "listpicture", "ftnsep", "ftnsepc",
                  "aftnsep", "aftnsepc", "ftncn", "aftncn", "fontemb", "fontfile", "falt", "panose", "leveltext",
                  "levelnumbers", "comment", "keywords", "subject", "operator", "company", "manager", "category", "doccomm",
                  "hlinkbase", "creatim", "revtim", "printim", "buptim", "title", "author", "pict", "field", "fldrslt",
                  "shppict", "listtext", "pntext", "footnote", "annotation", "atnid", "atnauthor", "atndate", "atnref"}
# feste Farben von \highlightN (RTF-Spezifikation)
_MARKER = {1: "#000000", 2: "#0000ff", 3: "#00ffff", 4: "#00ff00", 5: "#ff00ff", 6: "#ff0000", 7: "#ffff00", 8: "#ffffff",
           9: "#000080", 10: "#008080", 11: "#008000", 12: "#800080", 13: "#800000", 14: "#808000", 15: "#808080", 16: "#c0c0c0"}


class _Absatz:
    def __init__(self, props: dict, laeufe: list, liste: str | None):
        self.props, self.laeufe, self.liste = props, laeufe, liste


class _Tabelle:
    def __init__(self):
        self.zeilen: list[tuple[list[list[_Absatz]], list[int]]] = []


class _Ziel:
    """Sammelt Absätze und Tabellen — für den Haupttext und je Kopf-/Fußzeile."""

    def __init__(self, haupt: bool):
        self.haupt = haupt
        self.teile: list = []
        self.laeufe: list = []
        self.liste: str | None = None
        self.zelle: list[_Absatz] = []
        self.reihe: list[list[_Absatz]] = []
        self.tabelle: _Tabelle | None = None

    def text(self, s: str, zeichen: dict) -> None:
        if not s:
            return
        schl = tuple(sorted(zeichen.items()))
        if self.laeufe and self.laeufe[-1][0] == "t" and self.laeufe[-1][2] == schl:
            self.laeufe[-1] = ("t", self.laeufe[-1][1] + s, schl)
        else:
            self.laeufe.append(("t", s, schl))

    def absatz(self, absatz: dict) -> None:
        a = _Absatz(dict(absatz), self.laeufe, self.liste)
        self.laeufe, self.liste = [], None
        if self.haupt and absatz.get("intbl"):
            self.zelle.append(a)
            return
        self.tabelle = None
        self.teile.append(a)

    def zelle_ende(self, absatz: dict) -> None:
        if self.laeufe or not self.zelle:
            self.absatz(dict(absatz, intbl=True))
        self.reihe.append(self.zelle)
        self.zelle = []

    def reihe_ende(self, cellx: list[int]) -> None:
        if self.zelle or self.laeufe:
            self.zelle_ende({"intbl": True})
        if self.tabelle is None:
            self.tabelle = _Tabelle()
            self.teile.append(self.tabelle)
        self.tabelle.zeilen.append((self.reihe, list(cellx)))
        self.reihe = []

    def abschliessen(self, absatz: dict) -> None:
        if self.laeufe:
            self.absatz(dict(absatz, intbl=False))
        if self.reihe or self.zelle:
            self.reihe_ende([])


class _Zerleger:
    def __init__(self, daten: bytes):
        self.daten = daten
        self.report = IOReport()
        self.schriften: dict[int, str] = {}
        self.farben: list[str | None] = []
        self.stile: dict[int, int] = {}                     # \sN → Überschriftenebene
        self.codepage = "cp1252"
        self.standard_schrift = 0
        self.seite = PageSettings()
        self.titel_erste = False
        self.meta = {"title": "", "author": ""}
        self.haupt = _Ziel(True)
        self.kopf_fuss: dict[str, tuple[_Ziel, dict]] = {}

    def run(self) -> None:
        zeichen = {"f": None, "fs": 24}
        absatz: dict = {}
        g = {"z": zeichen, "a": absatz, "uc": 1, "ziel": self.haupt, "dest": None, "puffer": None, "feld": None}
        stapel: list[dict] = []
        cellx: list[int] = []
        ueberspringe = 0                                       # noch zu überspringende Ersatzzeichen nach \uN
        stern = False
        bild: dict | None = None
        d = self.daten
        pos = 0
        n = len(d)
        while pos < n:
            m = _TOKEN.match(d, pos)
            if m is None:
                pos += 1
                continue
            pos = m.end()
            wort, zahl, hexwert, symbol, klammer, text = m.groups()
            if wort is None and hexwert is None and symbol is None and klammer is None and text is None:
                continue                                       # Zeilenumbruch in der Datei: ohne Bedeutung
            if klammer == b"{":
                stapel.append(g)
                g = dict(g, z=dict(g["z"]), a=g["a"])
                g.pop("kf_wurzel", None)
                g["neu"] = True
                if len(stapel) > 2000:
                    raise DocumentIOError("Die RTF-Datei ist zu tief verschachtelt und wird nicht geöffnet.")
                continue
            if klammer == b"}":
                self._gruppe_ende(g)
                if not stapel:
                    break
                alt = g
                g = stapel.pop()
                if alt["dest"] in ("pict",) and alt.get("bild") is not None:
                    self._bild_fertig(alt["bild"], g)
                continue
            neu = g.pop("neu", False)
            dest = g["dest"]
            if text is not None or hexwert is not None:
                if hexwert is not None:
                    roh = bytes([int(hexwert, 16)])
                    if dest == "pict":
                        continue
                else:
                    roh = text
                if dest == "pict":
                    g["bild"]["hex"].append(roh)
                    continue
                s = roh.decode(self.codepage, errors="replace")
                if ueberspringe:
                    weg = min(ueberspringe, len(s))
                    s, ueberspringe = s[weg:], ueberspringe - weg
                self._text(g, s)
                continue
            if symbol is not None:
                sym = symbol.decode("latin-1")
                if sym == "*":
                    stern = True
                    if neu:
                        g["neu"] = True                      # das Steuerwort nach \* beginnt die Gruppe
                    continue
                if sym in "\n\r":
                    self._steuer(g, "par", None, neu=False)
                    continue
                if sym in _SYMBOL:
                    self._text(g, _SYMBOL[sym] or "")
                continue
            w = wort.decode("ascii")
            z = int(zahl) if zahl is not None else None
            if w == "bin" and z:
                if dest == "pict":
                    g["bild"]["bin"] = d[pos:pos + z]
                pos += max(0, z)
                continue
            if neu and stern and w not in ("shppict", "fldinst"):
                g["dest"] = "skip"
                stern = False
                continue
            stern = False
            if dest == "skip":
                continue
            if w == "u" and z is not None:
                self._text(g, chr(z + 65536 if z < 0 else z) if (z + 65536 if z < 0 else z) < 0xD800 or
                           (z + 65536 if z < 0 else z) > 0xDFFF else _ersatzpaar(g, z + 65536 if z < 0 else z))
                ueberspringe = g["uc"]
                continue
            if w == "uc" and z is not None:
                g["uc"] = max(0, z)
                continue
            if neu:
                if self._ziel_beginnen(g, w, z):
                    continue
            if dest == "pict":
                self._bild_wort(g["bild"], w, z)
                continue
            if w == "cellx" and z is not None:
                cellx.append(z)
                continue
            if w == "trowd":
                cellx = []
                continue
            if w == "row" or w == "nestrow":
                if w == "nestrow":
                    self.report.warn("Verschachtelte Tabellen aus der RTF-Datei wurden vereinfacht übernommen.")
                g["ziel"].reihe_ende(cellx)
                continue
            self._steuer(g, w, z, neu)
        self.haupt.abschliessen(absatz)

    # ---- Gruppenziele ---------------------------------------------------------------------------------------------------
    def _ziel_beginnen(self, g: dict, w: str, z: int | None) -> bool:
        if w in ("fonttbl", "colortbl", "stylesheet", "info"):
            g["dest"] = w
            g["puffer"] = []
            if w == "colortbl":
                g["farbe"] = [None, None, None]
            return True
        if g["dest"] in ("fonttbl", "stylesheet") and w in ("f", "s") and z is not None:
            g["eintrag"] = z
        if g["dest"] == "info" and w in ("title", "author"):
            g["dest"] = "info-" + w
            g["puffer"] = []
            return True
        if g["dest"] in ("info", "info-title", "info-author") and w not in ("title", "author"):
            g["dest"] = "skip" if g["dest"] == "info" else g["dest"]
            return g["dest"] == "skip"
        if w in _KOPF_FUSS:
            ziel = _Ziel(False)
            self.kopf_fuss[_KOPF_FUSS[w] + ("" if w in ("header", "footer", "headerf", "footerf") else "?" + w)] = (ziel, {})
            g["ziel"] = ziel
            g["a"] = {}
            g["kf_wurzel"] = True
            return True
        if w == "pict":
            g["dest"] = "pict"
            g["bild"] = {"hex": [], "art": None, "w": None, "h": None, "gw": None, "gh": None, "sx": 100, "sy": 100}
            return True
        if w == "shppict":
            return True
        if w in ("listtext", "pntext"):
            g["dest"] = "listentext"
            g["puffer"] = []
            return True
        if w == "field":
            g["feld"] = {"inst": []}
            return True
        if w == "fldinst":
            g["dest"] = "fldinst"
            return True
        if w == "fldrslt":
            feld = g.get("feld") or {"inst": []}
            anw = "".join(feld["inst"]).strip().upper()
            if not g["ziel"].haupt and (anw.startswith("NUMPAGES") or anw.startswith("PAGE")):
                g["ziel"].text("{PAGES}" if anw.startswith("NUMPAGES") else "{PAGE}", g["z"])
                g["dest"] = "skip"
            return True
        if w == "footnote":
            self.report.warn("Fuß- und Endnoten aus der RTF-Datei wurden nicht übernommen.")
            g["dest"] = "skip"
            return True
        if w in ("annotation", "atnid", "atnauthor", "atndate", "atnref"):
            self.report.warn("Kommentare aus der RTF-Datei wurden nicht übernommen.")
            g["dest"] = "skip"
            return True
        if w in ("shp", "shpgrp", "do"):
            self.report.warn("Zeichnungen und Formen aus der RTF-Datei wurden nicht übernommen.")
            g["dest"] = "skip"
            return True
        if w in _UEBERSPRINGEN and w not in ("title", "author"):
            g["dest"] = "skip"
            return True
        return False

    def _gruppe_ende(self, g: dict) -> None:
        dest = g["dest"]
        if dest in ("fonttbl", "stylesheet") and g.get("puffer") is not None and "eintrag" in g:
            name = "".join(g["puffer"]).split(";")[0].strip()
            if dest == "fonttbl" and name:
                self.schriften[g["eintrag"]] = name
            elif dest == "stylesheet":
                m = re.match(r"(?:heading|überschrift|berschrift)\s*(\d)", name, re.I)
                if m and g["eintrag"] not in self.stile:
                    self.stile[g["eintrag"]] = int(m.group(1))
        elif dest in ("info-title", "info-author"):
            self.meta["title" if dest == "info-title" else "author"] = "".join(g["puffer"]).strip()
        elif dest == "listentext":
            t = "".join(g["puffer"]).strip()
            g["ziel"].liste = "zahl" if re.match(r"^[\w]+[.)]?$", t) and t[:1].isalnum() else "punkt"
        if g.get("kf_wurzel") and g["ziel"].laeufe:
            g["ziel"].absatz(g["a"])

    def _text(self, g: dict, s: str) -> None:
        dest = g["dest"]
        if dest in (None,):
            g["ziel"].text(s, g["z"])
        elif dest in ("fonttbl", "stylesheet", "info-title", "info-author", "listentext"):
            g["puffer"].append(s)
        elif dest == "colortbl":
            for ch in s:
                if ch == ";":
                    r, gr, b = g["farbe"]
                    self.farben.append(None if r is None and gr is None and b is None
                                       else "#%02x%02x%02x" % (r or 0, gr or 0, b or 0))
                    g["farbe"] = [None, None, None]
        elif dest == "fldinst":
            feld = g.get("feld")
            if feld is not None:
                feld["inst"].append(s)

    # ---- Steuerwörter ---------------------------------------------------------------------------------------------------
    def _steuer(self, g: dict, w: str, z: int | None, neu: bool) -> None:
        zf, ab = g["z"], g["a"]
        if g["dest"] == "colortbl":
            if w in ("red", "green", "blue") and z is not None:
                g["farbe"][("red", "green", "blue").index(w)] = max(0, min(255, z))
            return
        if g["dest"] not in (None,):
            return
        an = z is None or z != 0
        if w in _ZEICHEN:
            g["ziel"].text(_ZEICHEN[w], zf)
        elif w == "par":
            g["ziel"].absatz(ab)
            ab.pop("pagebb_einmal", None)
        elif w == "page":
            if g["ziel"].laeufe:
                g["ziel"].absatz(ab)
            ab["pagebb_einmal"] = True
        elif w in ("cell", "nestcell"):
            g["ziel"].zelle_ende(ab) if g["ziel"].haupt else g["ziel"].text("\t", zf)
        elif w == "pard":
            einmal = ab.get("pagebb_einmal")
            ab.clear()
            if einmal:
                ab["pagebb_einmal"] = True
        elif w == "plain":
            zf.clear()
            zf.update({"f": None, "fs": 24})
        elif w in ("ql", "qc", "qr", "qj"):
            ab["q"] = w
        elif w in ("li", "ri", "fi", "sb", "sa") and z is not None:
            ab[w] = z
        elif w == "intbl":
            ab["intbl"] = True
        elif w == "pagebb":
            ab["pagebb"] = an
        elif w == "s" and z is not None:
            if z in self.stile:
                ab["h"] = self.stile[z]
        elif w == "outlinelevel" and z is not None and 0 <= z <= 8:
            ab["h"] = z + 1
        elif w in ("b", "i", "strike", "striked"):
            zf["strike" if w == "striked" else w] = an
        elif w in ("ul", "uld", "uldb", "uldash", "uldashd", "uldashdd", "ulth", "ulw", "ulwave", "uldb", "ulhwave", "ulldash",
                   "ulthd", "ulthdash", "ulthdashd", "ulthdashdd", "ulthldash", "ululdbwave"):
            zf["ul"] = an
        elif w == "ulnone":
            zf["ul"] = False
        elif w in ("super", "sub"):
            zf["va"] = w
        elif w == "nosupersub":
            zf.pop("va", None)
        elif w == "fs" and z:
            zf["fs"] = z
        elif w == "f" and z is not None:
            zf["f"] = z
        elif w == "cf" and z is not None:
            zf["cf"] = z
        elif w in ("cb", "chcbpat") and z is not None:
            zf["cb"] = z
        elif w == "highlight" and z is not None:
            zf["hl"] = z
        elif w == "ansicpg" and z:
            try:
                "".encode(f"cp{z}")
                self.codepage = f"cp{z}"
            except LookupError:
                pass
        elif w == "deff" and z is not None:
            self.standard_schrift = z
        elif w in ("paperw", "pgwsxn") and z:
            self.seite.width_mm = z / TWIP_PRO_MM
        elif w in ("paperh", "pghsxn") and z:
            self.seite.height_mm = z / TWIP_PRO_MM
        elif w in ("margl", "marglsxn") and z is not None:
            self.seite.margin_left_mm = z / TWIP_PRO_MM
        elif w in ("margr", "margrsxn") and z is not None:
            self.seite.margin_right_mm = z / TWIP_PRO_MM
        elif w in ("margt", "margtsxn") and z is not None:
            self.seite.margin_top_mm = z / TWIP_PRO_MM
        elif w in ("margb", "margbsxn") and z is not None:
            self.seite.margin_bottom_mm = z / TWIP_PRO_MM
        elif w == "headery" and z is not None:
            self.seite.kopf_abstand_mm = z / TWIP_PRO_MM
        elif w == "footery" and z is not None:
            self.seite.fuss_abstand_mm = z / TWIP_PRO_MM
        elif w == "titlepg":
            self.titel_erste = True
        elif w == "chpgn" and not g["ziel"].haupt:
            g["ziel"].text("{PAGE}", zf)

    # ---- Bilder ---------------------------------------------------------------------------------------------------------
    def _bild_wort(self, b: dict, w: str, z: int | None) -> None:
        if w in ("pngblip", "jpegblip", "emfblip", "wmetafile", "dibitmap", "wbitmap", "macpict"):
            b["art"] = w
        elif w in ("picw", "pich", "picwgoal", "pichgoal", "picscalex", "picscaley") and z is not None:
            b[{"picw": "w", "pich": "h", "picwgoal": "gw", "pichgoal": "gh", "picscalex": "sx", "picscaley": "sy"}[w]] = z

    def _bild_fertig(self, b: dict, g: dict) -> None:
        if "bin" in b:
            daten = b["bin"]
        else:
            roh = re.sub(rb"[^0-9a-fA-F]", b"", b"".join(b["hex"]))
            daten = bytes.fromhex(roh[: len(roh) // 2 * 2].decode("ascii"))
        from lunivo_writer.editor.freie_bilder import bild_aus_daten
        img = bild_aus_daten(daten) if b["art"] in ("pngblip", "jpegblip", "emfblip", None) else QImage()
        if img.isNull():
            self.report.warn("Ein Bild aus der RTF-Datei hat ein nicht lesbares Format und wurde übersprungen.")
            return
        bw = (b["gw"] / 15 if b["gw"] else img.width()) * b["sx"] / 100
        bh = (b["gh"] / 15 if b["gh"] else img.height()) * b["sy"] / 100
        g["ziel"].laeufe.append(("b", img, (bw, bh)))

    # ---- Ergebnis -------------------------------------------------------------------------------------------------------
    def zeichenformat(self, schl: tuple) -> QTextCharFormat:
        z = dict(schl)
        cf = QTextCharFormat()
        f = z.get("f")
        name = self.schriften.get(f if f is not None else self.standard_schrift)
        if name:
            cf.setFontFamilies([name])
        cf.setFontPointSize(max(1, z.get("fs", 24)) / 2)
        if z.get("b"):
            cf.setFontWeight(QFont.Bold)
        if z.get("i"):
            cf.setFontItalic(True)
        if z.get("ul"):
            cf.setFontUnderline(True)
        if z.get("strike"):
            cf.setFontStrikeOut(True)
        if z.get("va") == "super":
            cf.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        elif z.get("va") == "sub":
            cf.setVerticalAlignment(QTextCharFormat.AlignSubScript)
        farbe = self._farbe(z.get("cf"))
        if farbe:
            cf.setForeground(QBrush(QColor(farbe)))
        hg = _MARKER.get(z["hl"]) if z.get("hl") else self._farbe(z.get("cb"))
        if hg:
            cf.setBackground(QBrush(QColor(hg)))
        return cf

    def _farbe(self, i: int | None) -> str | None:
        if i is None or i <= 0 or i >= len(self.farben):
            return None
        return self.farben[i]


def _ersatzpaar(g: dict, wert: int) -> str:
    """Hälften eines UTF-16-Ersatzpaars (\\u-Paar für Zeichen außerhalb der BMP) zusammensetzen."""
    if 0xD800 <= wert <= 0xDBFF:
        g["hoch"] = wert
        return ""
    hoch = g.pop("hoch", None)
    if hoch is None:
        return "\ufffd"
    return chr(0x10000 + ((hoch - 0xD800) << 10) + (wert - 0xDC00))


def _absatzformat(a: dict) -> QTextBlockFormat:
    bf = QTextBlockFormat()
    bf.setAlignment({"qc": Qt.AlignHCenter, "qr": Qt.AlignRight, "qj": Qt.AlignJustify}.get(a.get("q", ""), Qt.AlignLeft))
    for k, setzen in (("li", bf.setLeftMargin), ("ri", bf.setRightMargin), ("sb", bf.setTopMargin), ("sa", bf.setBottomMargin)):
        if a.get(k):
            setzen(max(0, a[k]) / 15)
    if a.get("fi"):
        bf.setTextIndent(a["fi"] / 15)
    if a.get("pagebb") or a.get("pagebb_einmal"):
        bf.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore)
    if a.get("h"):
        bf.setHeadingLevel(a["h"])
    return bf


class _Bauer:
    def __init__(self, z: _Zerleger, doc: QTextDocument):
        self.z, self.doc = z, doc
        self.bild_n = 0

    def absatz(self, a: _Absatz, cur: QTextCursor, frei: bool, liste_vorher: dict) -> None:
        bf = _absatzformat(a.props)
        if a.liste:
            bf.setTextIndent(0)
            bf.setLeftMargin(0)
        erstes = next((lf for lf in a.laeufe if lf[0] == "t"), None)
        grund = self.z.zeichenformat(erstes[2]) if erstes else self.z.zeichenformat(tuple(sorted({"fs": 24}.items())))
        if frei:
            cur.setBlockFormat(bf)
            cur.setBlockCharFormat(grund)
        else:
            cur.insertBlock(bf, grund)
        if a.liste:
            ebene = max(1, round(a.props.get("li", 0) / 360)) if a.props.get("li") else 1
            vorher = liste_vorher.get("l")
            if vorher is not None and liste_vorher.get("art") == a.liste and liste_vorher.get("ebene") == ebene:
                vorher.add(cur.block())
            else:
                lf = QTextListFormat()
                lf.setStyle(QTextListFormat.ListDecimal if a.liste == "zahl" else QTextListFormat.ListDisc)
                lf.setIndent(ebene)
                liste_vorher.update(l=cur.createList(lf), art=a.liste, ebene=ebene)
        else:
            liste_vorher.clear()
        for lauf in a.laeufe:
            if lauf[0] == "t":
                cur.insertText(lauf[1], self.z.zeichenformat(lauf[2]))
            else:
                self.bild_n += 1
                name = f"rtf-bild-{self.bild_n}"
                self.doc.addResource(QTextDocument.ImageResource, QUrl(name), lauf[1])
                f = QTextImageFormat()
                f.setName(name)
                f.setWidth(lauf[2][0])
                f.setHeight(lauf[2][1])
                cur.insertImage(f)

    def teile(self, teile: list, cur: QTextCursor) -> None:
        frei = True
        liste: dict = {}
        for t in teile:
            if isinstance(t, _Absatz):
                self.absatz(t, cur, frei, liste)
                frei = False
                continue
            liste.clear()
            spalten = max(max((len(r) for r, _c in t.zeilen), default=1), 1)
            tf = QTextTableFormat()
            tf.setCellPadding(4)
            tf.setCellSpacing(0)
            tf.setBorder(1)
            tf.setBorderBrush(QBrush(QColor("#000000")))
            tf.setBorderStyle(QTextFrameFormat.BorderStyle_Solid)
            grenzen = next((c for r, c in t.zeilen if len(c) == spalten), None)
            if grenzen and grenzen[-1] > 0:
                breiten = [b - a for a, b in zip([0] + grenzen[:-1], grenzen)]
                if all(b > 0 for b in breiten):
                    tf.setColumnWidthConstraints([QTextLength(QTextLength.PercentageLength, 100 * b / sum(breiten)) for b in breiten])
            if not frei:
                cur.insertBlock()
            tab = cur.insertTable(len(t.zeilen), spalten, tf)
            for r, (reihe, _c) in enumerate(t.zeilen):
                for c, zelle in enumerate(reihe):
                    zc = tab.cellAt(r, c).firstCursorPosition()
                    zfrei, zliste = True, {}
                    for a in zelle:
                        self.absatz(a, zc, zfrei, zliste)
                        zfrei = False
            cur.setPosition(tab.lastPosition() + 1)
            frei = True


def _kopf_fuss_text(ziel: _Ziel, z: _Zerleger) -> HeaderFooter:
    absaetze = [a for a in ziel.teile if isinstance(a, _Absatz)]
    if ziel.laeufe:
        absaetze.append(_Absatz({}, ziel.laeufe, None))
    zeilen = ["".join(lf[1] for lf in a.laeufe if lf[0] == "t").replace("\u2028", "\n") for a in absaetze]
    text = "\n".join(zeilen).strip("\n")
    ausr = "left"
    if absaetze:
        ausr = {"qc": "center", "qr": "right", "qj": "justify"}.get(absaetze[0].props.get("q", ""), "left")
    if any(lf[0] == "b" for a in absaetze for lf in a.laeufe):
        z.report.warn("Bilder in Kopf- und Fußzeile aus der RTF-Datei wurden nicht übernommen.")
    return HeaderFooter(text, ausr)


def read_rtf(path: str):
    """→ (QTextDocument, PageSettings, meta-dict, IOReport). Wirft DocumentIOError."""
    try:
        with open(path, "rb") as fh:
            daten = fh.read(GRENZE_BYTES + 1)
    except OSError as e:
        raise DocumentIOError(f"Datei nicht lesbar: {e.strerror or e}") from e
    if len(daten) > GRENZE_BYTES:
        raise DocumentIOError("Die RTF-Datei ist zu groß, um sie sicher zu öffnen.")
    if not daten.lstrip().startswith(b"{\\rtf"):
        raise DocumentIOError("Die Datei ist kein gültiges RTF-Dokument oder beschädigt.")
    z = _Zerleger(daten)
    z.run()
    doc = QTextDocument()
    doc.setDocumentMargin(0)
    df = QFont(z.schriften.get(z.standard_schrift) or "Liberation Serif")
    df.setPointSizeF(12.0)
    doc.setDefaultFont(df)
    _Bauer(z, doc).teile(z.haupt.teile, QTextCursor(doc))
    page = z.seite
    for schl, (ziel, _a) in z.kopf_fuss.items():
        if "?" in schl:                                       # linke/rechte Seiten: nur, wenn es keine allgemeine gibt
            basis = schl.split("?")[0]
            if basis in z.kopf_fuss:
                continue
            schl = basis
        setattr(page, schl, _kopf_fuss_text(ziel, z))
    page.diff_first = z.titel_erste and (not page.first_header.is_empty() or not page.first_footer.is_empty() or True)
    if not z.titel_erste:
        page.first_header, page.first_footer = HeaderFooter(), HeaderFooter()
    from lunivo_writer.editor.zusatz import leere_meta
    meta = dict(z.meta)
    meta.update(leere_meta())
    doc.setModified(False)
    return doc, page, meta, z.report
