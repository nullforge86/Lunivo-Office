"""ODT (OpenDocument-Text) direkt schreiben — ohne Umwandlungsprogramm.

Geschrieben wird aus dem ``QTextDocument``: ``content.xml`` (Absätze, Überschriften, Zeichenformat, Listen, Tabellen, Bilder als
``Pictures/*.png``), ``styles.xml`` (Standardschrift, Seitengröße, Seitenränder, Kopf- und Fußzeile) und ``meta.xml`` (Titel, Autor).
Das Paket: ``mimetype`` zuerst und unkomprimiert, Manifest mit allen Teilen. (Qts eigener ODF-Schreiber setzt Tabellen hinter
Listen fehlerhaft zusammen und legt keine Seitenangaben an; deshalb nicht verwendet.)
"""
from __future__ import annotations

import io
import zipfile
from xml.sax.saxutils import escape

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QUrl, Qt
from PySide6.QtGui import (QImage, QPixmap, QTextBlock, QTextBlockFormat, QTextCharFormat, QTextDocument, QTextFormat, QTextLength,
                           QTextListFormat, QTextTable)

from lunivo_writer.models.page import HeaderFooter, PageSettings
from lunivo_writer.models.report import IOReport

MIMETYPE = b"application/vnd.oasis.opendocument.text"
_NS = ('xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
       'xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" '
       'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" '
       'xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" '
       'xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" '
       'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" '
       'xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" '
       'xmlns:xlink="http://www.w3.org/1999/xlink" '
       'xmlns:dc="http://purl.org/dc/elements/1.1/" '
       'xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" '
       'xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"')
_AUSRICHTUNG = {"left": "start", "center": "center", "right": "end", "justify": "justify"}


def _mm(wert: float) -> str:
    return f"{max(0.0, float(wert)):.2f}mm"


def _absatz(hf: HeaderFooter, stil: str) -> str:
    """Kopf-/Fußzeilentext als ODF-Absätze; {PAGE} und {PAGES} werden zu Feldern."""
    zeilen = []
    for zeile in hf.text.split("\n"):
        teile, rest = [], zeile
        while rest:
            pos = [(rest.find(t), t) for t in ("{PAGE}", "{PAGES}") if rest.find(t) >= 0]
            if not pos:
                teile.append(escape(rest)); break
            i, t = min(pos)
            teile.append(escape(rest[:i]))
            teile.append("<text:page-number text:select-page=\"current\">1</text:page-number>" if t == "{PAGE}"
                         else "<text:page-count>1</text:page-count>")
            rest = rest[i + len(t):]
        zeilen.append(f'<text:p text:style-name="{stil}">{"".join(teile)}</text:p>')
    return "".join(zeilen)


def _styles_xml(page: PageSettings, doc: QTextDocument | None = None) -> str:
    kopf = not page.header.is_empty() or (page.diff_first and not page.first_header.is_empty())
    fuss = not page.footer.is_empty() or (page.diff_first and not page.first_footer.is_empty())
    # ODF misst den oberen Rand bis zur Kopfzeile; Lunivo (wie Word) bis zum Text. Mit Kopfzeile: Rand = Kopfabstand,
    # Kopfzeilenbereich = Rest bis zum Text.
    rand_oben = min(page.kopf_abstand_mm, page.margin_top_mm) if kopf else page.margin_top_mm
    rand_unten = min(page.fuss_abstand_mm, page.margin_bottom_mm) if fuss else page.margin_bottom_mm
    kopf_stil = (f'<style:header-style><style:header-footer-properties fo:min-height="{_mm(page.margin_top_mm - rand_oben - 5)}" '
                 f'fo:margin-bottom="5mm"/></style:header-style>') if kopf else "<style:header-style/>"
    fuss_stil = (f'<style:footer-style><style:header-footer-properties fo:min-height="{_mm(page.margin_bottom_mm - rand_unten - 5)}" '
                 f'fo:margin-top="5mm"/></style:footer-style>') if fuss else "<style:footer-style/>"
    hintergrund = f' fo:background-color="{escape(page.color)}"' if page.color else ""
    stile = []
    for name, hf in (("Kopf", page.header), ("Fuss", page.footer), ("KopfErste", page.first_header), ("FussErste", page.first_footer)):
        stile.append(f'<style:style style:name="Lunivo{name}" style:family="paragraph"><style:paragraph-properties '
                     f'fo:text-align="{_AUSRICHTUNG.get(hf.align, "center")}"/></style:style>')
    seite = []
    if not page.header.is_empty():
        seite.append(f"<style:header>{_absatz(page.header, 'LunivoKopf')}</style:header>")
    if page.diff_first and kopf:
        seite.append(f"<style:header-first>{_absatz(page.first_header, 'LunivoKopfErste')}</style:header-first>")
    if not page.footer.is_empty():
        seite.append(f"<style:footer>{_absatz(page.footer, 'LunivoFuss')}</style:footer>")
    if page.diff_first and fuss:
        seite.append(f"<style:footer-first>{_absatz(page.first_footer, 'LunivoFussErste')}</style:footer-first>")
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            f'<office:document-styles {_NS} office:version="1.3">'
            f'<office:styles>{_standard(doc)}{"".join(stile)}</office:styles>'
            '<office:automatic-styles><style:page-layout style:name="LunivoSeite">'
            f'<style:page-layout-properties fo:page-width="{_mm(page.width_mm)}" fo:page-height="{_mm(page.height_mm)}" '
            f'style:print-orientation="{"landscape" if page.landscape else "portrait"}" '
            f'fo:margin-top="{_mm(rand_oben)}" fo:margin-bottom="{_mm(rand_unten)}" '
            f'fo:margin-left="{_mm(page.margin_left_mm)}" fo:margin-right="{_mm(page.margin_right_mm)}"{hintergrund}/>'
            f"{kopf_stil}{fuss_stil}</style:page-layout></office:automatic-styles>"
            '<office:master-styles><style:master-page style:name="Standard" style:page-layout-name="LunivoSeite">'
            f'{"".join(seite)}</style:master-page></office:master-styles></office:document-styles>')


def _standard(doc: QTextDocument | None) -> str:
    """Standardschrift des Dokuments als Vorgabe für alle Absätze, dazu die Vorlage „Standard“."""
    f = doc.defaultFont() if doc is not None else None
    name = escape(f.family(), {'"': "&quot;"}) if f is not None else "Liberation Sans"
    groesse = (f.pointSizeF() if f is not None and f.pointSizeF() > 0 else 11.0)
    return (f'<style:default-style style:family="paragraph"><style:text-properties style:font-name="{name}" fo:font-family="{name}" '
            f'fo:font-size="{groesse:g}pt"/></style:default-style>'
            '<style:style style:name="Standard" style:family="paragraph" style:class="text"/>')


def _manifest(namen: list[str]) -> str:
    eintraege = [f'<manifest:file-entry manifest:media-type="{MIMETYPE.decode()}" manifest:full-path="/"/>']
    for n in namen:
        if n in ("mimetype", "META-INF/manifest.xml") or n.endswith("/"):
            continue
        typ = "text/xml" if n.endswith(".xml") else ("image/png" if n.endswith(".png") else
                                                    "image/jpeg" if n.endswith((".jpg", ".jpeg")) else "application/octet-stream")
        eintraege.append(f'<manifest:file-entry manifest:media-type="{typ}" manifest:full-path="{escape(n)}"/>')
    return (f'<?xml version="1.0" encoding="UTF-8"?><manifest:manifest {_NS} manifest:version="1.3">'
            + "".join(eintraege) + "</manifest:manifest>")


def bild_aus_format(doc: QTextDocument, cf) -> QImage | None:
    """Das Bild hinter einem Bildformat (Ressource im Dokument oder Datei), sonst None."""
    name = cf.toImageFormat().name()
    res = doc.resource(QTextDocument.ImageResource, QUrl(name))
    if isinstance(res, QImage):
        img = res
    elif isinstance(res, (bytes, QByteArray)):
        img = QImage.fromData(res)
    elif isinstance(res, QPixmap):
        img = res.toImage()
    else:
        img = QImage(name)
    return None if img.isNull() else img


def spannweite(t: QTextTable, r: int, c: int) -> tuple[int, int]:
    """Wie viele Spalten und Zeilen die Zelle mit Ursprung (r, c) überdeckt (gezählt, nicht columnSpan(): das liefert für
    verbundene Zellen aus DOCX nicht immer den echten Wert)."""
    def gleich(rr: int, cc: int) -> bool:
        z = t.cellAt(rr, cc)
        return z.row() == r and z.column() == c
    breit = 1
    while c + breit < t.columns() and gleich(r, c + breit):
        breit += 1
    hoch = 1
    while r + hoch < t.rows() and gleich(r + hoch, c):
        hoch += 1
    return breit, hoch


def _png(img: QImage) -> bytes:
    puffer = QByteArray()
    geraet = QBuffer(puffer)
    geraet.open(QIODevice.WriteOnly)
    img.save(geraet, "PNG")
    geraet.close()
    return bytes(puffer)


def _odf(element: str, attr: dict | None = None, inhalt: str | None = None) -> str:
    """Ein Element des ODF-Tabellenmodells (Namensraum ``table:``) als XML-Text."""
    name = "table:" + element
    a = "".join(f' {k}="{escape(v, {chr(34): "&quot;"})}"' for k, v in (attr or {}).items())
    return f"<{name}{a}/>" if inhalt is None else f"<{name}{a}>{inhalt}</{name}>"


def _laenge(px: float) -> str:
    return f"{px * 25.4 / 96:.2f}mm"


class _Inhalt:
    """Baut content.xml aus dem QTextDocument: Absätze, Überschriften, Zeichenformat, Listen, Tabellen, Bilder."""

    def __init__(self, doc: QTextDocument, rep: IOReport):
        self.doc, self.rep = doc, rep
        self.absatz_stile: dict[tuple, str] = {}
        self.text_stile: dict[tuple, str] = {}
        self.listen_stile: dict[int, tuple[str, str]] = {}      # id(QTextList) → (Name, XML)
        self.schriften: set[str] = set()
        self.bilder: dict[str, bytes] = {}
        self.tabellen = 0

    # ---- Formate ---------------------------------------------------------------------------------------------------------
    def _absatz_stil(self, bf: QTextBlockFormat) -> str:
        a = bf.alignment()
        ausr = "center" if a & Qt.AlignHCenter else "end" if a & Qt.AlignRight else "justify" if a & Qt.AlignJustify else "start"
        schl = (ausr, round(bf.leftMargin() + bf.indent() * self.doc.indentWidth(), 2), round(bf.rightMargin(), 2),
                round(bf.topMargin(), 2), round(bf.bottomMargin(), 2), round(bf.textIndent(), 2),
                bool(bf.pageBreakPolicy() & QTextFormat.PageBreak_AlwaysBefore))
        if schl not in self.absatz_stile:
            self.absatz_stile[schl] = f"P{len(self.absatz_stile) + 1}"
        return self.absatz_stile[schl]

    def _text_stil(self, cf: QTextCharFormat) -> str | None:
        fam = cf.fontFamilies()
        name = fam[0] if isinstance(fam, (list, tuple)) and fam else ""
        va = cf.verticalAlignment()
        schl = (name, round(cf.fontPointSize(), 2), cf.fontWeight() >= 600, cf.fontItalic(),
                cf.fontUnderline() or cf.underlineStyle() != QTextCharFormat.NoUnderline, cf.fontStrikeOut(),
                "super" if va == QTextCharFormat.AlignSuperScript else "sub" if va == QTextCharFormat.AlignSubScript else "",
                cf.foreground().color().name() if cf.hasProperty(QTextFormat.ForegroundBrush) and cf.foreground().style() != Qt.NoBrush else "",
                cf.background().color().name() if cf.hasProperty(QTextFormat.BackgroundBrush) and cf.background().style() != Qt.NoBrush else "")
        if not any(schl):
            return None
        if name:
            self.schriften.add(name)
        if schl not in self.text_stile:
            self.text_stile[schl] = f"T{len(self.text_stile) + 1}"
        return self.text_stile[schl]

    def _listen_stil(self, liste) -> str:
        if id(liste) not in self.listen_stile:
            lf = liste.format()
            name = f"L{len(self.listen_stile) + 1}"
            stil = lf.style()
            ebenen = []
            for n in range(1, 11):
                einzug = f'<style:list-level-properties text:list-level-position-and-space-mode="label-alignment">' \
                         f'<style:list-level-label-alignment text:label-followed-by="listtab" fo:text-indent="-6.35mm" ' \
                         f'fo:margin-left="{6.35 * n:.2f}mm"/></style:list-level-properties>'
                if stil in (QTextListFormat.ListDisc, QTextListFormat.ListCircle, QTextListFormat.ListSquare):
                    zeichen = {QTextListFormat.ListDisc: "•", QTextListFormat.ListCircle: "◦", QTextListFormat.ListSquare: "▪"}[stil]
                    ebenen.append(f'<text:list-level-style-bullet text:level="{n}" text:bullet-char="{zeichen}">{einzug}'
                                  "</text:list-level-style-bullet>")
                else:
                    fmt = {QTextListFormat.ListLowerAlpha: "a", QTextListFormat.ListUpperAlpha: "A",
                           QTextListFormat.ListLowerRoman: "i", QTextListFormat.ListUpperRoman: "I"}.get(stil, "1")
                    ebenen.append(f'<text:list-level-style-number text:level="{n}" style:num-suffix="." style:num-format="{fmt}">'
                                  f"{einzug}</text:list-level-style-number>")
            self.listen_stile[id(liste)] = (name, f'<text:list-style style:name="{name}">{"".join(ebenen)}</text:list-style>')
        return self.listen_stile[id(liste)][0]

    # ---- Inhalt ----------------------------------------------------------------------------------------------------------
    def _text(self, s: str) -> str:
        teile, i = [], 0
        while i < len(s):
            ch = s[i]
            if ch == "\t":
                teile.append("<text:tab/>")
            elif ch in "\u2028\n":
                teile.append("<text:line-break/>")
            elif ch == "\ufffc":
                pass
            elif ch == " " and i + 1 < len(s) and s[i + 1] == " ":
                n = 1
                while i + n < len(s) and s[i + n] == " ":
                    n += 1
                teile.append(" " + (f'<text:s text:c="{n - 1}"/>' if n > 1 else ""))
                i += n
                continue
            elif ord(ch) < 32:
                pass
            else:
                teile.append(escape(ch))
            i += 1
        return "".join(teile)

    def _bild(self, cf) -> str:
        img = bild_aus_format(self.doc, cf)
        if img is None:
            self.rep.warn("Ein Bild war nicht lesbar und fehlt in der ODT-Datei.")
            return ""
        name = f"Pictures/bild{len(self.bilder) + 1}.png"
        self.bilder[name] = _png(img)
        f = cf.toImageFormat()
        b, h = f.width() or img.width(), f.height() or img.height()
        return (f'<draw:frame draw:name="Bild{len(self.bilder)}" text:anchor-type="as-char" svg:width="{_laenge(b)}" '
                f'svg:height="{_laenge(h)}"><draw:image xlink:href="{name}" xlink:type="simple" xlink:show="embed" '
                'xlink:actuate="onLoad"/></draw:frame>')

    def absatz(self, block: QTextBlock) -> str:
        bf = block.blockFormat()
        inhalt = []
        it = block.begin()
        while not it.atEnd():
            frag = it.fragment()
            cf = frag.charFormat()
            if cf.isImageFormat():
                inhalt.append(self._bild(cf))
            else:
                t = self._text(frag.text())
                stil = self._text_stil(cf)
                inhalt.append(f'<text:span text:style-name="{stil}">{t}</text:span>' if stil and t else t)
            it += 1
        stil = self._absatz_stil(bf)
        stufe = bf.headingLevel()
        if 1 <= stufe <= 10:
            return f'<text:h text:style-name="{stil}" text:outline-level="{stufe}">{"".join(inhalt)}</text:h>'
        return f'<text:p text:style-name="{stil}">{"".join(inhalt)}</text:p>'

    def tabelle(self, t: QTextTable) -> str:
        self.tabellen += 1
        zeilen, spalten = t.rows(), t.columns()
        breiten = t.format().columnWidthConstraints()
        zeilen_xml = []
        spalten_xml = []
        for c in range(spalten):
            anteil = breiten[c].rawValue() if c < len(breiten) and breiten[c].type() == QTextLength.PercentageLength else 100 / spalten
            spalten_xml.append(_odf("table-column", {"table:style-name": f"Sp{max(1, round(anteil))}"}))
            self.absatz_stile.setdefault(("spalte", max(1, round(anteil))), f"Sp{max(1, round(anteil))}")
        for r in range(zeilen):
            zellen = []
            for c in range(spalten):
                zelle = t.cellAt(r, c)
                if zelle.row() != r or zelle.column() != c:
                    zellen.append(_odf("covered-table-cell"))
                    continue
                attr = {"office:value-type": "string", "table:style-name": "Zelle"}
                breit, hoch = spannweite(t, r, c)
                if breit > 1:
                    attr["table:number-columns-spanned"] = str(breit)
                if hoch > 1:
                    attr["table:number-rows-spanned"] = str(hoch)
                zellen.append(_odf("table-cell", attr, self._rahmen_inhalt(zelle.begin()) or "<text:p/>"))
            zeilen_xml.append(_odf("table-row", {}, "".join(zellen)))
        out = [_odf("table", {"table:name": f"Tabelle{self.tabellen}", "table:style-name": "Tab"}, "".join(spalten_xml + zeilen_xml))]
        return "".join(out)

    def _rahmen_inhalt(self, it) -> str:
        teile: list[str] = []
        listen: list = []                                  # offene Listen (QTextList), außen zuerst

        def listen_schliessen(bis: int) -> None:
            while len(listen) > bis:
                listen.pop()
                teile.append("</text:list-item></text:list>")

        while not it.atEnd():
            fr, blk = it.currentFrame(), it.currentBlock()
            if fr is not None:
                listen_schliessen(0)
                if isinstance(fr, QTextTable):
                    teile.append(self.tabelle(fr))
                else:
                    teile.append(self._rahmen_inhalt(fr.begin()))
            elif blk.isValid():
                liste = blk.textList()
                if liste is None:
                    listen_schliessen(0)
                    teile.append(self.absatz(blk))
                else:
                    tiefe = max(1, liste.format().indent())
                    while listen and (listen[-1] is not liste and max(1, listen[-1].format().indent()) >= tiefe):
                        listen_schliessen(len(listen) - 1)
                    if listen and listen[-1] is liste:
                        teile.append("</text:list-item><text:list-item>")
                    else:
                        teile.append(f'<text:list text:style-name="{self._listen_stil(liste)}"><text:list-item>')
                        listen.append(liste)
                    teile.append(self.absatz(blk))
            it += 1
        listen_schliessen(0)
        return "".join(teile)

    def xml(self) -> str:
        koerper = self._rahmen_inhalt(self.doc.rootFrame().begin())
        stile = []
        for schl, name in self.absatz_stile.items():
            if schl[0] == "spalte":
                stile.append(f'<style:style style:name="{name}" style:family="table-column"><style:table-column-properties '
                             f'style:rel-column-width="{schl[1] * 100}*"/></style:style>')
                continue
            ausr, links, rechts, oben, unten, einzug, umbruch = schl
            stile.append(f'<style:style style:name="{name}" style:family="paragraph" style:parent-style-name="Standard">'
                         f'<style:paragraph-properties fo:text-align="{ausr}" fo:margin-left="{_laenge(links)}" '
                         f'fo:margin-right="{_laenge(rechts)}" fo:margin-top="{_laenge(oben)}" fo:margin-bottom="{_laenge(unten)}" '
                         f'fo:text-indent="{_laenge(einzug)}"' + (' fo:break-before="page"' if umbruch else "") + "/></style:style>")
        for (name, groesse, fett, kursiv, unter, durch, lage, farbe, hg), stil in self.text_stile.items():
            a = []
            if name:
                a.append(f'style:font-name="{escape(name, {chr(34): "&quot;"})}"')
            if groesse:
                a.append(f'fo:font-size="{groesse:g}pt"')
            if fett:
                a.append('fo:font-weight="bold"')
            if kursiv:
                a.append('fo:font-style="italic"')
            if unter:
                a.append('style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color"')
            if durch:
                a.append('style:text-line-through-style="solid"')
            if lage:
                a.append(f'style:text-position="{lage} 58%"')
            if farbe:
                a.append(f'fo:color="{farbe}"')
            if hg:
                a.append(f'fo:background-color="{hg}"')
            stile.append(f'<style:style style:name="{stil}" style:family="text"><style:text-properties {" ".join(a)}/></style:style>')
        stile.append('<style:style style:name="Tab" style:family="table"><style:table-properties style:width="100%" '
                     'table:align="margins"/></style:style>')
        stile.append('<style:style style:name="Zelle" style:family="table-cell"><style:table-cell-properties '
                     'fo:padding="1mm" fo:border="0.5pt solid #000000"/></style:style>')
        stile.extend(x for _n, x in self.listen_stile.values())
        schriften = "".join(f'<style:font-face style:name="{escape(n, {chr(34): "&quot;"})}" '
                            f'svg:font-family="{escape(n, {chr(34): "&quot;"})}"/>' for n in sorted(self.schriften))
        return ('<?xml version="1.0" encoding="UTF-8"?>'
                f'<office:document-content {_NS} office:version="1.3">'
                f"<office:font-face-decls>{schriften}</office:font-face-decls>"
                f'<office:automatic-styles>{"".join(stile)}</office:automatic-styles>'
                f"<office:body><office:text>{koerper}</office:text></office:body></office:document-content>")


def _meta_xml(meta: dict) -> str:
    teile = []
    if meta.get("title"):
        teile.append(f"<dc:title>{escape(meta['title'])}</dc:title>")
    if meta.get("author"):
        teile.append(f"<meta:initial-creator>{escape(meta['author'])}</meta:initial-creator><dc:creator>{escape(meta['author'])}</dc:creator>")
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            f'<office:document-meta {_NS} office:version="1.3"><office:meta><meta:generator>Lunivo Writer</meta:generator>'
            f'{"".join(teile)}</office:meta></office:document-meta>')


def odt_daten(doc: QTextDocument, page: PageSettings, meta: dict | None = None) -> tuple[bytes, IOReport]:
    """Baut die ODT-Datei im Speicher. → (Inhalt, Bericht über nicht Übernommenes)."""
    rep = IOReport()
    inhalt = _Inhalt(doc, rep)
    teile = {"content.xml": inhalt.xml().encode("utf-8"), "styles.xml": _styles_xml(page, doc).encode("utf-8"),
             "meta.xml": _meta_xml(meta or {}).encode("utf-8")}
    teile.update(inhalt.bilder)
    aus = io.BytesIO()
    with zipfile.ZipFile(aus, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), MIMETYPE, compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/manifest.xml", _manifest(list(teile)), compress_type=zipfile.ZIP_DEFLATED)
        for n, daten in teile.items():
            z.writestr(n, daten, compress_type=zipfile.ZIP_STORED if n.endswith(".png") else zipfile.ZIP_DEFLATED)
    _verluste_melden(rep, page, meta or {}, "ODT")
    return aus.getvalue(), rep


def _verluste_melden(rep: IOReport, page: PageSettings, meta: dict, fmt: str) -> None:
    """Was der direkte ODT-/RTF-Weg nicht mitnimmt — damit nichts still verloren geht."""
    noten = meta.get("noten") or {}
    if any(noten.get(a) for a in noten):
        rep.warn(f"Fuß- und Endnoten werden in {fmt} nicht gespeichert (nur in DOCX).")
    if meta.get("kommentare"):
        rep.warn(f"Kommentare werden in {fmt} nicht gespeichert (nur in DOCX).")
    if page.watermark:
        rep.warn(f"Das Wasserzeichen wird in {fmt} nicht gespeichert.")
    if page.border:
        rep.warn(f"Der Seitenrahmen wird in {fmt} nicht gespeichert.")
    if int(page.spalten or 1) > 1:
        rep.warn(f"Textspalten werden in {fmt} nicht gespeichert.")
    if page.bilder:
        rep.warn(f"Bilder in Kopf- und Fußzeile werden in {fmt} nicht gespeichert.")
