"""ODT (OpenDocument-Text) direkt schreiben — ohne Umwandlungsprogramm.

Geschrieben wird aus dem ``QTextDocument``: ``content.xml`` (Absätze, Überschriften, Zeichenformat, Listen, Tabellen, Bilder als
``Pictures/*.png``), ``styles.xml`` (Standardschrift, Seitengröße, Seitenränder, Kopf- und Fußzeile) und ``meta.xml`` (Titel, Autor).
Das Paket: ``mimetype`` zuerst und unkomprimiert, Manifest mit allen Teilen. (Qts eigener ODF-Schreiber setzt Tabellen hinter
Listen fehlerhaft zusammen und legt keine Seitenangaben an; deshalb nicht verwendet.)

Aufteilung: ``odt_schreiben_basis`` (Namensräume, Maße, Bilder, freie Rahmen), ``odt_seite_schreiben`` (styles.xml), hier der Inhalt
(content.xml), die Metadaten und das Paket.
"""
from __future__ import annotations

import io
import zipfile
from xml.sax.saxutils import escape

from PySide6.QtCore import Qt
from PySide6.QtGui import (QTextBlock, QTextBlockFormat, QTextCharFormat, QTextDocument, QTextFormat, QTextLength,
                           QTextListFormat, QTextTable)

from lunivo_writer.editor.objekte import bilddaten as BD
from lunivo_writer.editor.text.fragmente import absatz_fragmente
from lunivo_writer.editor.dokument.zusatz import B_BILDANKER, P_DEKORATIV, P_NOTE
from lunivo_writer.modelle.seite import PageSettings
from lunivo_writer.modelle.bericht import IOReport
from lunivo_writer.dienste.odt_schreiben_basis import (                       # noqa: F401  (rtf_writer, odt_bilder greifen hier zu)
    _NS, AUSR_H, AUSR_V, BEZUG_H, BEZUG_V, MIMETYPE, _bild_elemente, _bild_stil, _frei_form, _frei_rahmen, _frei_stil, _laenge, _mm, _odf, _png, bild_aus_format, spannweite,
)
from lunivo_writer.dienste.odt_seite_schreiben import ODF_ZAHL, _styles_xml          # noqa: F401

_ATTR_QUOTE = {chr(34): "&quot;"}
_BILDTYPEN = {endung: typ for endung, typ in BD.FORMATE.values()}                      # Dateiendung → Medientyp für das Manifest
_BILDTYPEN["jpeg"] = "image/jpeg"
_LISTEN_ZEICHEN = {QTextListFormat.ListDisc: "•", QTextListFormat.ListCircle: "◦", QTextListFormat.ListSquare: "▪"}
_LISTEN_ZAHL = {QTextListFormat.ListLowerAlpha: "a", QTextListFormat.ListUpperAlpha: "A",
                QTextListFormat.ListLowerRoman: "i", QTextListFormat.ListUpperRoman: "I"}
_TEXT_SONDER = {"\t": "<text:tab/>", "\u2028": "<text:line-break/>", "\n": "<text:line-break/>", "\ufffc": ""}   # Zeichen → ODF-Element
_VERTIKAL = {QTextCharFormat.AlignSuperScript: "super", QTextCharFormat.AlignSubScript: "sub"}
_STAND_TAB_STIL = ('<style:style style:name="Tab" style:family="table"><style:table-properties style:width="100%" '
                   'table:align="margins"/></style:style>')
_STAND_ZELLE_STIL = ('<style:style style:name="Zelle" style:family="table-cell"><style:table-cell-properties '
                     'fo:padding="1mm" fo:border="0.5pt solid #000000"/></style:style>')


def _manifest(namen: list[str]) -> str:
    eintraege = [f'<manifest:file-entry manifest:media-type="{MIMETYPE.decode()}" manifest:full-path="/"/>']
    for n in namen:
        if n in ("mimetype", "META-INF/manifest.xml") or n.endswith("/"):
            continue
        typ = "text/xml" if n.endswith(".xml") else _BILDTYPEN.get(n.rsplit(".", 1)[-1].lower(), "application/octet-stream")
        eintraege.append(f'<manifest:file-entry manifest:media-type="{typ}" manifest:full-path="{escape(n)}"/>')
    return (f'<?xml version="1.0" encoding="UTF-8"?><manifest:manifest {_NS} manifest:version="1.3">'
            + "".join(eintraege) + "</manifest:manifest>")


def _text_zeichen(ch: str) -> str:
    """Ein Zeichen des Dokumenttexts als ODF-Text (Sonderzeichen → Elemente, Steuerzeichen entfallen)."""
    if ch in _TEXT_SONDER:
        return _TEXT_SONDER[ch]
    return "" if ord(ch) < 32 else escape(ch)


def _leerzeichen_lauf(s: str, i: int) -> tuple[str, int]:
    """Mehrere Leerzeichen ab ``i`` → (ODF-Text, Länge des Laufs): ein echtes Leerzeichen plus ``text:s`` für den Rest."""
    n = 1
    while i + n < len(s) and s[i + n] == " ":
        n += 1
    return " " + (f'<text:s text:c="{n - 1}"/>' if n > 1 else ""), n


def _text_xml(s: str) -> str:
    teile, i = [], 0
    while i < len(s):
        if s[i] == " " and s[i + 1:i + 2] == " ":
            xml, n = _leerzeichen_lauf(s, i)
            teile.append(xml)
            i += n
            continue
        teile.append(_text_zeichen(s[i]))
        i += 1
    return "".join(teile)


def _farbe(cf: QTextCharFormat, eigenschaft: int, pinsel) -> str:
    """Farbname des Pinsels, wenn das Format ihn gesetzt hat und er nicht leer ist, sonst ``""``."""
    return pinsel().color().name() if cf.hasProperty(eigenschaft) and pinsel().style() != Qt.NoBrush else ""


def _text_schluessel(cf: QTextCharFormat) -> tuple:
    """Alles am Zeichenformat, was ODF in eine Textvorlage schreibt (gleiche Schlüssel → gleiche Vorlage)."""
    fam = cf.fontFamilies()
    return ((fam[0] if isinstance(fam, (list, tuple)) and fam else ""), round(cf.fontPointSize(), 2), cf.fontWeight() >= 600,
            cf.fontItalic(), cf.fontUnderline() or cf.underlineStyle() != QTextCharFormat.NoUnderline, cf.fontStrikeOut(),
            _VERTIKAL.get(cf.verticalAlignment(), ""),
            _farbe(cf, QTextFormat.ForegroundBrush, cf.foreground), _farbe(cf, QTextFormat.BackgroundBrush, cf.background))


def _text_eigenschaften(name, groesse, fett, kursiv, unter, durch, lage, farbe, hg) -> str:
    """Die Attribute einer Textvorlage; nur gesetzte Eigenschaften erscheinen."""
    paare = ((name, f'style:font-name="{escape(name, _ATTR_QUOTE)}"'), (groesse, f'fo:font-size="{groesse:g}pt"'),
             (fett, 'fo:font-weight="bold"'), (kursiv, 'fo:font-style="italic"'),
             (unter, 'style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color"'),
             (durch, 'style:text-line-through-style="solid"'), (lage, f'style:text-position="{lage} 58%"'),
             (farbe, f'fo:color="{farbe}"'), (hg, f'fo:background-color="{hg}"'))
    return " ".join(s for gesetzt, s in paare if gesetzt)


def _absatz_vorlage_xml(name: str, schl: tuple) -> str:
    """Eine Absatz- oder Spaltenvorlage (``schl`` wie in ``_Inhalt._absatz_stil`` bzw. ``("spalte", Prozent)``)."""
    if schl[0] == "spalte":
        return (f'<style:style style:name="{name}" style:family="table-column"><style:table-column-properties '
                f'style:rel-column-width="{schl[1] * 100}*"/></style:style>')
    ausr, links, rechts, oben, unten, einzug, umbruch = schl
    return (f'<style:style style:name="{name}" style:family="paragraph" style:parent-style-name="Standard">'
            f'<style:paragraph-properties fo:text-align="{ausr}" fo:margin-left="{_laenge(links)}" '
            f'fo:margin-right="{_laenge(rechts)}" fo:margin-top="{_laenge(oben)}" fo:margin-bottom="{_laenge(unten)}" '
            f'fo:text-indent="{_laenge(einzug)}"' + (' fo:break-before="page"' if umbruch else "") + "/></style:style>")


def _listen_ebene_xml(stil, n: int) -> str:
    """Eine Ebene (1–10) einer Listenvorlage: Aufzählungszeichen oder Zahlenart je nach Listenformat."""
    einzug = (f'<style:list-level-properties text:list-level-position-and-space-mode="label-alignment">'
              f'<style:list-level-label-alignment text:label-followed-by="listtab" fo:text-indent="-6.35mm" '
              f'fo:margin-left="{6.35 * n:.2f}mm"/></style:list-level-properties>')
    if stil in _LISTEN_ZEICHEN:
        return (f'<text:list-level-style-bullet text:level="{n}" text:bullet-char="{_LISTEN_ZEICHEN[stil]}">{einzug}'
                "</text:list-level-style-bullet>")
    return (f'<text:list-level-style-number text:level="{n}" style:num-suffix="." style:num-format="{_LISTEN_ZAHL.get(stil, "1")}">'
            f"{einzug}</text:list-level-style-number>")


class _Inhalt:
    """Baut content.xml aus dem QTextDocument: Absätze, Überschriften, Zeichenformat, Listen, Tabellen, Bilder."""

    def __init__(self, doc: QTextDocument, rep: IOReport, meta: dict | None = None):
        self.doc, self.rep = doc, rep
        self.noten = (meta or {}).get("noten", {})
        self.absatz_stile: dict[tuple, str] = {}
        self.text_stile: dict[tuple, str] = {}
        self.listen_stile: dict[int, tuple[str, str]] = {}      # id(QTextList) → (Name, XML)
        self.schriften: set[str] = set()
        self.bilder: dict[str, bytes] = {}
        self.tabellen = 0
        self.rahmen_stile: list[str] = []

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
        schl = _text_schluessel(cf)
        if not any(schl):
            return None
        if schl[0]:
            self.schriften.add(schl[0])
        if schl not in self.text_stile:
            self.text_stile[schl] = f"T{len(self.text_stile) + 1}"
        return self.text_stile[schl]

    def _listen_stil(self, liste) -> str:
        if id(liste) not in self.listen_stile:
            name = f"L{len(self.listen_stile) + 1}"
            stil = liste.format().style()
            ebenen = "".join(_listen_ebene_xml(stil, n) for n in range(1, 11))
            self.listen_stile[id(liste)] = (name, f'<text:list-style style:name="{name}">{ebenen}</text:list-style>')
        return self.listen_stile[id(liste)][0]

    # ---- Inhalt ----------------------------------------------------------------------------------------------------------
    def _bild(self, cf) -> str:
        img = bild_aus_format(self.doc, cf)
        if img is None:
            self.rep.warn("Ein Bild war nicht lesbar und fehlt in der ODT-Datei.")
            return ""
        bild = _bild_elemente(img, f"bild{len(self.bilder) + 1}", self.bilder)
        f = cf.toImageFormat()
        b, h = f.width() or img.width(), f.height() or img.height()
        stil = ""
        if f.hasProperty(P_DEKORATIV) and f.property(P_DEKORATIV):               # dekorativ: Rahmenvorlage mit loext:decorative
            nr = len(self.rahmen_stile) + 1
            self.rahmen_stile.append(_bild_stil(f"Fr{nr}"))
            stil = f' draw:style-name="Fr{nr}"'
        return (f'<draw:frame{stil} draw:name="Bild{len(self.bilder)}" text:anchor-type="as-char" svg:width="{_laenge(b)}" '
                f'svg:height="{_laenge(h)}">{bild}</draw:frame>')

    def _freie_bilder(self, bf: QTextBlockFormat) -> list[str]:
        if not bf.hasProperty(B_BILDANKER):
            return []
        from lunivo_writer.editor.objekte import freie_bilder as FB
        out = []
        for a in FB.aus_absatz(bf):
            if a.get("art") == "form":
                nr = len(self.rahmen_stile) + 1
                stil = f"Fr{nr}"
                self.rahmen_stile.append(_frei_stil(stil, a))
                form = _frei_form(a, nr, stil)
                if form:
                    out.append(form)
                else:
                    self.rep.warn("Eine freie Form wurde nicht in die ODT-Datei übernommen.")
                continue
            img = FB.bild_im_dokument(self.doc, a.get("n", ""))
            if img is None:
                self.rep.warn("Ein Bild war nicht lesbar und fehlt in der ODT-Datei.")
                continue
            nr = len(self.rahmen_stile) + 1
            self.rahmen_stile.append(_frei_stil(f"Fr{nr}", a))
            out.append(_frei_rahmen(a, img, nr, f"Fr{nr}", self.bilder))
        return out

    def _note(self, text: str, cf: QTextCharFormat) -> str | None:
        marke = cf.stringProperty(P_NOTE)
        if ":" not in marke:
            return None
        art, nummer = marke.split(":", 1)
        if art not in ("f", "e") or not nummer.isdigit():
            return None
        eintraege = self.noten.get(art, {})
        inhalt = eintraege.get(int(nummer), eintraege.get(nummer)) if isinstance(eintraege, dict) else None
        if inhalt is None:
            return None
        klass = "endnote" if art == "e" else "footnote"
        ident = ("etn" if art == "e" else "ftn") + nummer
        absatz = f"<text:p>{_text_xml(str(inhalt))}</text:p>"
        stil = self._text_stil(cf)
        citation = _text_xml(text)
        citation_xml = f'<text:span text:style-name="{stil}">{citation}</text:span>' if stil else citation
        return (f'<text:note text:id="{ident}" text:note-class="{klass}">'
                f"<text:note-citation>{citation_xml}</text:note-citation>"
                f"<text:note-body>{absatz}</text:note-body></text:note>")

    def absatz(self, block: QTextBlock) -> str:
        bf = block.blockFormat()
        inhalt = self._freie_bilder(bf)
        for frag in absatz_fragmente(block):
            cf = frag.charFormat()
            if cf.isImageFormat():
                inhalt.append(self._bild(cf))
            else:
                note = self._note(frag.text(), cf)
                if note is not None:
                    inhalt.append(note)
                    continue
                t = _text_xml(frag.text())
                stil = self._text_stil(cf)
                inhalt.append(f'<text:span text:style-name="{stil}">{t}</text:span>' if stil and t else t)
        stil = self._absatz_stil(bf)
        stufe = bf.headingLevel()
        if 1 <= stufe <= 10:
            return f'<text:h text:style-name="{stil}" text:outline-level="{stufe}">{"".join(inhalt)}</text:h>'
        return f'<text:p text:style-name="{stil}">{"".join(inhalt)}</text:p>'

    # ---- Tabellen --------------------------------------------------------------------------------------------------------
    def _spalten_xml(self, t: QTextTable) -> list[str]:
        spalten, breiten = t.columns(), t.format().columnWidthConstraints()
        out = []
        for c in range(spalten):
            anteil = breiten[c].rawValue() if c < len(breiten) and breiten[c].type() == QTextLength.PercentageLength else 100 / spalten
            prozent = max(1, round(anteil))
            out.append(_odf("table-column", {"table:style-name": f"Sp{prozent}"}))
            self.absatz_stile.setdefault(("spalte", prozent), f"Sp{prozent}")
        return out

    def _zelle_xml(self, t: QTextTable, r: int, c: int) -> str:
        zelle = t.cellAt(r, c)
        if zelle.row() != r or zelle.column() != c:
            return _odf("covered-table-cell")
        attr = {"office:value-type": "string", "table:style-name": "Zelle"}
        breit, hoch = spannweite(t, r, c)
        if breit > 1:
            attr["table:number-columns-spanned"] = str(breit)
        if hoch > 1:
            attr["table:number-rows-spanned"] = str(hoch)
        return _odf("table-cell", attr, self._rahmen_inhalt(zelle.begin()) or "<text:p/>")

    def tabelle(self, t: QTextTable) -> str:
        self.tabellen += 1
        spalten_xml = self._spalten_xml(t)
        zeilen_xml = [_odf("table-row", {}, "".join(self._zelle_xml(t, r, c) for c in range(t.columns()))) for r in range(t.rows())]
        return _odf("table", {"table:name": f"Tabelle{self.tabellen}", "table:style-name": "Tab"}, "".join(spalten_xml + zeilen_xml))

    # ---- Rahmen, Listen --------------------------------------------------------------------------------------------------
    @staticmethod
    def _listen_schliessen(listen: list, teile: list[str], bis: int) -> None:
        while len(listen) > bis:
            listen.pop()
            teile.append("</text:list-item></text:list>")

    def _listenpunkt(self, blk: QTextBlock, liste, listen: list, teile: list[str]) -> None:
        """Der Absatz ``blk`` als Listenpunkt von ``liste``: offene Listen auf die passende Tiefe bringen, dann Punkt öffnen."""
        tiefe = max(1, liste.format().indent())
        while listen and (listen[-1] is not liste and max(1, listen[-1].format().indent()) >= tiefe):
            self._listen_schliessen(listen, teile, len(listen) - 1)
        if listen and listen[-1] is liste:
            teile.append("</text:list-item><text:list-item>")
        else:
            teile.append(f'<text:list text:style-name="{self._listen_stil(liste)}"><text:list-item>')
            listen.append(liste)
        teile.append(self.absatz(blk))

    def _rahmen_inhalt(self, it) -> str:
        teile: list[str] = []
        listen: list = []                                  # offene Listen (QTextList), außen zuerst
        while not it.atEnd():
            fr, blk = it.currentFrame(), it.currentBlock()
            if fr is not None:
                self._listen_schliessen(listen, teile, 0)
                teile.append(self.tabelle(fr) if isinstance(fr, QTextTable) else self._rahmen_inhalt(fr.begin()))
            elif blk.isValid():
                liste = blk.textList()
                if liste is None:
                    self._listen_schliessen(listen, teile, 0)
                    teile.append(self.absatz(blk))
                else:
                    self._listenpunkt(blk, liste, listen, teile)
            it += 1
        self._listen_schliessen(listen, teile, 0)
        return "".join(teile)

    # ---- Dokument --------------------------------------------------------------------------------------------------------
    def _vorlagen_xml(self) -> str:
        stile = [_absatz_vorlage_xml(name, schl) for schl, name in self.absatz_stile.items()]
        stile.extend(f'<style:style style:name="{stil}" style:family="text"><style:text-properties '
                     f'{_text_eigenschaften(*schl)}/></style:style>' for schl, stil in self.text_stile.items())
        stile.extend((_STAND_TAB_STIL, _STAND_ZELLE_STIL))
        stile.extend(x for _n, x in self.listen_stile.values())
        stile.extend(self.rahmen_stile)
        return "".join(stile)

    def _schriften_xml(self) -> str:
        return "".join(f'<style:font-face style:name="{escape(n, _ATTR_QUOTE)}" svg:font-family="{escape(n, _ATTR_QUOTE)}"/>'
                       for n in sorted(self.schriften))

    def xml(self) -> str:
        koerper = self._rahmen_inhalt(self.doc.rootFrame().begin())
        return ('<?xml version="1.0" encoding="UTF-8"?>'
                f'<office:document-content {_NS} office:version="1.3">'
                f"<office:font-face-decls>{self._schriften_xml()}</office:font-face-decls>"
                f'<office:automatic-styles>{self._vorlagen_xml()}</office:automatic-styles>'
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
    inhalt = _Inhalt(doc, rep, meta)
    kf_bilder: dict[str, bytes] = {}
    teile = {"content.xml": inhalt.xml().encode("utf-8"), "styles.xml": _styles_xml(page, doc, kf_bilder).encode("utf-8"),
             "meta.xml": _meta_xml(meta or {}).encode("utf-8")}
    teile.update(inhalt.bilder)
    teile.update(kf_bilder)
    aus = io.BytesIO()
    with zipfile.ZipFile(aus, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), MIMETYPE, compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/manifest.xml", _manifest(list(teile)), compress_type=zipfile.ZIP_DEFLATED)
        for n, daten in teile.items():
            z.writestr(n, daten, compress_type=zipfile.ZIP_STORED if n.rsplit(".", 1)[-1].lower() in _BILDTYPEN else zipfile.ZIP_DEFLATED)
    _verluste_melden(rep, page, meta or {}, "ODT")
    return aus.getvalue(), rep


def _verluste_melden(rep: IOReport, page: PageSettings, meta: dict, fmt: str) -> None:
    """Was der direkte ODT-/RTF-Weg nicht mitnimmt — damit nichts still verloren geht."""
    noten = meta.get("noten") or {}
    verluste = ((any(noten.get(a) for a in noten) and fmt != "ODT", f"Fuß- und Endnoten werden in {fmt} nicht gespeichert (nur in DOCX)."),
                (meta.get("kommentare"), f"Kommentare werden in {fmt} nicht gespeichert (nur in DOCX)."),
                (page.watermark, f"Das Wasserzeichen wird in {fmt} nicht gespeichert."),
                (page.border, f"Der Seitenrahmen wird in {fmt} nicht gespeichert."),
                (int(page.spalten or 1) > 1, f"Textspalten werden in {fmt} nicht gespeichert."),
                (page.bilder and fmt != "ODT", f"Bilder in Kopf- und Fußzeile werden in {fmt} nicht gespeichert."))
    for betroffen, text in verluste:
        if betroffen:
            rep.warn(text)
