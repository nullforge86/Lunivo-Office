"""Qt-freier ODT/FODT-Leser für Textabsätze, Zeichenformate und Listen."""
from __future__ import annotations

import zipfile
import base64
import xml.etree.ElementTree as ET

from lunivo_writer.core.document import CharacterFormat, Document, Image, ListFormat, Paragraph, ParagraphFormat, Section, TextRun
from lunivo_writer.core.document.values import Brush, Color, Length
from lunivo_writer.dienste.odt_xml import GRENZE_BYTES, MAX_WIEDERHOLUNG, NS, _kurz, _px, _pt, _q, _text_von
from lunivo_writer.modelle.bericht import DocumentIOError, IOReport
from lunivo_writer.modelle.seite import HeaderFooter, PageSettings, px_to_mm


class NichtImModell(Exception):
    """ODT-Inhalt, der noch nicht ohne Qt vollständig übernommen wird."""


class _Stile:
    def __init__(self):
        self.stile: dict[tuple[str, str], ET.Element] = {}
        self.standard: dict[str, ET.Element] = {}
        self.listen: dict[str, ET.Element] = {}
        self.schriften: dict[str, str] = {}
        self.seiten: dict[str, ET.Element] = {}
        self.cache: dict[tuple[str, str | None, str], dict[str, str]] = {}

    def lesen(self, wurzel: ET.Element | None) -> None:
        if wurzel is None:
            return
        for element in wurzel.iter(_q("style:font-face")):
            name = element.get(_q("style:name"), "")
            self.schriften[name] = (element.get(_q("svg:font-family")) or name).strip("'\"")
        for bereich in ("office:styles", "office:automatic-styles"):
            container = wurzel.find(_q(bereich))
            if container is None:
                continue
            for element in container:
                name, familie = element.get(_q("style:name"), ""), element.get(_q("style:family"), "")
                if element.tag == _q("style:style"):
                    self.stile[familie, name] = element
                elif element.tag == _q("style:default-style"):
                    self.standard[familie] = element
                elif element.tag == _q("text:list-style"):
                    self.listen[name] = element
                elif element.tag == _q("style:page-layout"):
                    self.seiten[name] = element

    def eigenschaften(self, familie: str, name: str | None, art: str) -> dict[str, str]:
        key = (familie, name, art)
        if key in self.cache:
            return self.cache[key]
        kette, gesehen = [], set()
        while name and (familie, name) in self.stile and name not in gesehen:
            gesehen.add(name)
            element = self.stile[familie, name]
            kette.append(element)
            name = element.get(_q("style:parent-style-name"))
        if familie in self.standard:
            kette.append(self.standard[familie])
        werte = {}
        for element in reversed(kette):
            child = element.find(_q(f"style:{art}-properties"))
            if child is not None:
                werte.update({_kurz(k): v for k, v in child.attrib.items()})
        self.cache[key] = werte
        return werte

    def liste_von(self, absatzstil: str | None) -> str | None:
        gesehen = set()
        while absatzstil and absatzstil not in gesehen and ("paragraph", absatzstil) in self.stile:
            gesehen.add(absatzstil)
            style = self.stile["paragraph", absatzstil]
            name = style.get(_q("style:list-style-name"))
            if name:
                return name
            absatzstil = style.get(_q("style:parent-style-name"))
        return None


def _farbe(wert: str | None) -> Color | None:
    if not wert or wert == "transparent" or len(wert) != 7 or wert[0] != "#":
        return None
    try:
        return Color(int(wert[1:3], 16), int(wert[3:5], 16), int(wert[5:7], 16))
    except ValueError:
        return None


def _format(p: dict[str, str], stile: _Stile) -> CharacterFormat:
    family = stile.schriften.get(p.get("style:font-name", ""), "") or p.get("fo:font-family", "").strip("'\"") or None
    size = _pt(p.get("fo:font-size")) or None
    weight = 700 if p.get("fo:font-weight") in {"bold", "600", "700", "800", "900"} else 400 if p.get("fo:font-weight") == "normal" else None
    italic = p.get("fo:font-style") in ("italic", "oblique") if "fo:font-style" in p else None
    underline = p.get("style:text-underline-style") not in (None, "none") if "style:text-underline-style" in p else None
    foreground, background = _farbe(p.get("fo:color")), _farbe(p.get("fo:background-color"))
    props = {}
    if family:
        props["FontFamilies"] = (family,)
    if size:
        props["FontPointSize"] = size
    if weight is not None:
        props["FontWeight"] = weight
    if italic is not None:
        props["FontItalic"] = italic
    if underline is not None:
        props["FontUnderline"] = underline
    if p.get("style:text-line-through-style") not in (None, "none"):
        props["FontStrikeOut"] = True
    if foreground:
        props["ForegroundBrush"] = Brush(1, foreground)
    if background:
        props["BackgroundBrush"] = Brush(1, background)
    position = p.get("style:text-position", "").split()
    if position:
        if position[0] == "super":
            props["TextVerticalAlignment"] = 1
        elif position[0] == "sub":
            props["TextVerticalAlignment"] = 2
    return CharacterFormat(props, family, size, weight, italic, foreground, underline)


def _absatzformat(p: dict[str, str], zeichen: CharacterFormat, level: int | None = None, list_id: int | None = None) -> ParagraphFormat:
    alignment = {"start": "left", "left": "left", "center": "center", "end": "right", "right": "right", "justify": "justify"}.get(p.get("fo:text-align", ""), "left")
    fields = {}
    for source, target in (("fo:margin-left", "left_indent_px"), ("fo:margin-right", "right_indent_px"),
                          ("fo:margin-top", "space_before_px"), ("fo:margin-bottom", "space_after_px"), ("fo:text-indent", "first_line_indent_px")):
        if source in p and not p[source].endswith("%"):
            fields[target] = _px(p[source])
    props = {"PageBreakPolicy": 1} if p.get("fo:break-before") == "page" else {}
    if level is not None:
        props["HeadingLevel"] = level
    return ParagraphFormat(properties=props, char_format=zeichen, list_id=list_id, alignment=alignment, **fields)


class _Leser:
    def __init__(self, inhalt: ET.Element, stilelement: ET.Element | None, metaelement: ET.Element | None, bild_laden=None):
        self.inhalt, self.stilelement, self.metaelement = inhalt, stilelement, metaelement
        self.bild_laden = bild_laden or (lambda _name: None)
        self.stile = _Stile()
        self.stile.lesen(stilelement)
        if inhalt is not stilelement:
            self.stile.lesen(inhalt)
        self.report = IOReport()
        self.listen: dict[int, ListFormat] = {}
        self.listen_ids: dict[tuple[str, int], int] = {}
        self.noten: list = []

    def _runs(self, node: ET.Element, inherited: dict[str, str], aus: list) -> None:
        if node.text:
            fmt = _format(inherited, self.stile)
            if aus and aus[-1].format == fmt:
                aus[-1].text += node.text
            else:
                aus.append(TextRun(node.text, fmt))
        for child in node:
            tag = child.tag
            if tag == _q("text:span"):
                props = dict(inherited)
                props.update(self.stile.eigenschaften("text", child.get(_q("text:style-name")), "text"))
                self._runs(child, props, aus)
            elif tag == _q("text:s"):
                try:
                    count = max(1, min(1000, int(child.get(_q("text:c"), "1"))))
                except ValueError:
                    count = 1
                self._text(" " * count, inherited, aus)
            elif tag in (_q("text:tab"), _q("text:line-break")):
                self._text("\t" if tag == _q("text:tab") else "\u2028", inherited, aus)
            elif tag in (_q("office:annotation"), _q("text:bookmark"), _q("text:bookmark-start"), _q("text:bookmark-end"),
                         _q("text:reference-mark"), _q("text:reference-mark-start"), _q("text:reference-mark-end")):
                if tag == _q("office:annotation"):
                    self.report.warn("Kommentare aus der ODT-Datei wurden nicht übernommen.")
            elif tag == _q("draw:frame"):
                aus.append(self._inline_bild(child))
            elif tag in (_q("draw:rect"), _q("draw:ellipse"), _q("table:table"), _q("text:note")):
                raise NichtImModell(tag)
            else:
                self._runs(child, inherited, aus)
            if child.tail:
                self._text(child.tail, inherited, aus)

    def _text(self, text: str, props: dict[str, str], aus: list) -> None:
        fmt = _format(props, self.stile)
        if aus and isinstance(aus[-1], TextRun) and aus[-1].format == fmt:
            aus[-1].text += text
        else:
            aus.append(TextRun(text, fmt))

    def _inline_bild(self, frame: ET.Element) -> Image:
        if frame.get(_q("text:anchor-type"), "as-char") != "as-char":
            raise NichtImModell("frei verankertes ODT-Bild")
        element = frame.find(_q("draw:image"))
        if element is None:
            raise NichtImModell("ODT-Rahmen ohne eingebettetes Bild")
        href = element.get(_q("xlink:href"), "")
        binary = element.find(_q("office:binary-data"))
        data = None
        if binary is not None and binary.text:
            try:
                data = base64.b64decode(binary.text)
            except ValueError:
                data = None
        elif href and ":" not in href:
            data = self.bild_laden(href.lstrip("./"))
        if not data:
            raise NichtImModell("ODT-Bilddatei nicht lesbar")
        from lunivo_writer.core.document.bildformat import format_erkennen
        art = format_erkennen(data)
        if art not in ("png", "jpeg", "svg", "emf", "wmf"):
            raise NichtImModell("ODT-Bildformat ohne Backenddarstellung")
        breite = _px(frame.get(_q("svg:width")), 64.0)
        hoehe = _px(frame.get(_q("svg:height")), 64.0)
        return Image(data, CharacterFormat({"ImageWidth": breite, "ImageHeight": hoehe}), data, art)

    def _listenstil(self, name: str | None, ebene: int) -> tuple[int, int]:
        style = self.stile.listen.get(name or "")
        item = next((k for k in style if k.get(_q("text:level")) == str(ebene)), None) if style is not None else None
        if item is not None and item.tag == _q("text:list-level-style-number"):
            typ = {"a": -5, "A": -6, "i": -7, "I": -8}.get(item.get(_q("style:num-format"), "1"), -4)
            return typ, ebene
        bullet = item.get(_q("text:bullet-char"), "•") if item is not None else "•"
        return {"◦": -2, "○": -2, "▪": -3, "■": -3}.get(bullet, -1), ebene

    def _paragraph(self, node: ET.Element, listen: tuple[str | None, int] | None = None) -> Paragraph:
        style = node.get(_q("text:style-name"))
        pp = self.stile.eigenschaften("paragraph", style, "paragraph")
        tp = self.stile.eigenschaften("paragraph", style, "text")
        level = None
        if node.tag == _q("text:h"):
            try:
                level = max(1, min(9, int(node.get(_q("text:outline-level"), "1"))))
            except ValueError:
                level = 1
        runs: list = []
        self._runs(node, tp, runs)
        cf = runs[0].format if runs else _format(tp, self.stile)
        lid = None
        if listen is not None:
            list_name, depth = listen
            if not list_name:
                list_name = self.stile.liste_von(style)
            list_style, depth = self._listenstil(list_name, depth)
            key = (list_name or "", depth)
            lid = self.listen_ids.setdefault(key, len(self.listen_ids) + 1)
            self.listen.setdefault(lid, ListFormat({"ListStyle": list_style, "ListIndent": depth}))
        return Paragraph(_absatzformat(pp, cf, level, lid), runs)

    def _inhalte(self, nodes) -> list:
        out = []
        for node in nodes:
            if node.tag in (_q("text:p"), _q("text:h")):
                out.append(self._paragraph(node))
            elif node.tag == _q("text:list"):
                self._liste(node, out)
            elif node.tag == _q("table:table"):
                out.append(self._tabelle(node))
            elif node.tag == _q("draw:frame"):
                raise NichtImModell(node.tag)
            elif node.tag in (_q("text:section"), _q("text:index-body"), _q("text:table-of-content"), _q("text:alphabetical-index"),
                              _q("text:illustration-index"), _q("text:table-index"), _q("text:bibliography"), _q("text:user-index"), _q("text:object-index")):
                out.extend(self._inhalte(list(node)))
        return out

    @staticmethod
    def _repeat(node: ET.Element, key: str) -> int:
        try:
            return max(1, min(MAX_WIEDERHOLUNG, int(node.get(_q(key), "1"))))
        except ValueError:
            return 1

    def _tabelle(self, node: ET.Element):
        from lunivo_writer.core.document import Table, TableCell, TableRow

        row_tags = {_q(k) for k in ("table:table-row",)}
        row_groups = {_q(k) for k in ("table:table-rows", "table:table-header-rows", "table:table-row-group")}
        col_tags = {_q("table:table-column")}
        col_groups = {_q(k) for k in ("table:table-columns", "table:table-header-columns", "table:table-column-group")}
        rows: list[ET.Element] = []
        widths: list[float] = []

        def gather(element: ET.Element) -> None:
            for child in element:
                if child.tag in row_tags:
                    rows.extend([child] * self._repeat(child, "table:number-rows-repeated"))
                elif child.tag in row_groups:
                    gather(child)
                elif child.tag in col_tags:
                    style = self.stile.eigenschaften("table-column", child.get(_q("table:style-name")), "table-column")
                    width = _px(style.get("style:column-width"), 0.0)
                    widths.extend([width] * self._repeat(child, "table:number-columns-repeated"))
                elif child.tag in col_groups:
                    gather(child)
        gather(node)
        cell_tags = {_q("table:table-cell"), _q("table:covered-table-cell")}
        row_cells = []
        for row in rows:
            cells = []
            for child in row:
                if child.tag in cell_tags:
                    cells.extend([child] * self._repeat(child, "table:number-columns-repeated"))
            row_cells.append(cells)
        columns = max([len(cells) for cells in row_cells] + [len(widths), 1])
        table_props = {"TableCellPadding": 4.0, "TableCellSpacing": 0.0}
        if widths and len(widths) == columns and sum(widths) > 0:
            table_props["TableColumnWidthConstraints"] = tuple(Length("percentage", width * 100 / sum(widths)) for width in widths)
        built_rows = []
        for r, cells in enumerate(row_cells):
            row_model = TableRow()
            c = 0
            while c < len(cells):
                cell = cells[c]
                if cell.tag == _q("table:covered-table-cell"):
                    c += 1
                    continue
                try:
                    rowspan = max(1, int(cell.get(_q("table:number-rows-spanned"), "1")))
                    colspan = max(1, int(cell.get(_q("table:number-columns-spanned"), "1")))
                except ValueError:
                    rowspan = colspan = 1
                props = {}
                style = self.stile.eigenschaften("table-cell", cell.get(_q("table:style-name")), "table-cell")
                background = _farbe(style.get("fo:background-color"))
                if background:
                    props["BackgroundBrush"] = Brush(1, background)
                content = self._inhalte(list(cell)) or [Paragraph()]
                row_model.cells.append(TableCell(r, c, rowspan, min(colspan, columns - c), props, content))
                c += min(colspan, columns - c)
            built_rows.append(row_model)
        return Table(max(1, len(built_rows)), columns, table_props, built_rows)

    def _liste(self, node: ET.Element, out: list, stil: str | None = None, ebene: int = 1) -> None:
        stil = node.get(_q("text:style-name")) or stil
        for item in node:
            if item.tag not in (_q("text:list-item"), _q("text:list-header")):
                continue
            for child in item:
                if child.tag in (_q("text:p"), _q("text:h")):
                    out.append(self._paragraph(child, (stil, ebene) if item.tag == _q("text:list-item") else None))
                elif child.tag == _q("text:list"):
                    self._liste(child, out, stil, ebene + 1)
                else:
                    out.extend(self._inhalte([child]))

    def _seite(self) -> PageSettings:
        page = PageSettings()
        masters = self.stilelement.find(_q("office:master-styles")) if self.stilelement is not None else None
        if masters is None:
            return page
        master = next(iter(masters.findall(_q("style:master-page"))), None)
        if master is None:
            return page
        layout = self.stile.seiten.get(master.get(_q("style:page-layout-name"), ""))
        properties = layout.find(_q("style:page-layout-properties")) if layout is not None else None
        if properties is not None:
            attrs = {_kurz(k): v for k, v in properties.attrib.items()}
            for field, key in (("width_mm", "fo:page-width"), ("height_mm", "fo:page-height"), ("margin_left_mm", "fo:margin-left"),
                               ("margin_right_mm", "fo:margin-right"), ("margin_top_mm", "fo:margin-top"), ("margin_bottom_mm", "fo:margin-bottom")):
                if key in attrs:
                    setattr(page, field, px_to_mm(_px(attrs[key])))
            bgcolor = attrs.get("fo:background-color")
            if bgcolor and bgcolor != "transparent":
                page.color = bgcolor
            page.seiten_format = {"a": "klein", "A": "gross", "i": "roem_klein", "I": "roem_gross"}.get(attrs.get("style:num-format", "1"), "dezimal")
            for element_name, margin_attr, distance_attr, edge in (("header", "margin_top_mm", "kopf_abstand_mm", "bottom"),
                                                                    ("footer", "margin_bottom_mm", "fuss_abstand_mm", "top")):
                style = layout.find(f"{_q(f'style:{element_name}-style')}/{_q('style:header-footer-properties')}") if layout is not None else None
                if style is None or master.find(_q("style:" + element_name)) is None:
                    continue
                values = {_kurz(k): v for k, v in style.attrib.items()}
                margin = getattr(page, margin_attr)
                extra = px_to_mm(_px(values.get("fo:min-height") or values.get("svg:height"), 0)
                                 + _px(values.get(f"fo:margin-{edge}"), 0))
                setattr(page, distance_attr, margin)
                setattr(page, margin_attr, margin + max(extra, 5.0))
        for attr, tag in (("header", "header"), ("footer", "footer"), ("first_header", "header-first"), ("first_footer", "footer-first")):
            el = master.find(_q("style:" + tag))
            if el is not None:
                text = "\n".join(_text_von(p) for p in el.iter() if p.tag in (_q("text:p"), _q("text:h"))).strip("\n")
                para = next((p for p in el.iter() if p.tag in (_q("text:p"), _q("text:h"))), None)
                align = self.stile.eigenschaften("paragraph", para.get(_q("text:style-name")) if para is not None else None, "paragraph").get("fo:text-align")
                setattr(page, attr, HeaderFooter(text, {"start": "left", "left": "left", "center": "center", "end": "right", "right": "right", "justify": "justify"}.get(align, "center")))
        page.diff_first = master.find(_q("style:header-first")) is not None or master.find(_q("style:footer-first")) is not None
        for tag, ort in (("header", "kopf"), ("footer", "fuss"), ("header-first", "kopf1"), ("footer-first", "fuss1")):
            parent = master.find(_q("style:" + tag))
            if parent is None:
                continue
            for frame in parent.iter(_q("draw:frame")):
                image = frame.find(_q("draw:image"))
                if image is None:
                    continue
                href = image.get(_q("xlink:href"), "")
                embedded = image.find(_q("office:binary-data"))
                data = None
                if embedded is not None and embedded.text:
                    try:
                        data = base64.b64decode(embedded.text)
                    except ValueError:
                        data = None
                elif href and not ":" in href:
                    data = self.bild_laden(href.lstrip("./"))
                if not data:
                    self.report.warn("Ein Bild in der Kopf- oder Fußzeile der ODT-Datei wurde nicht übernommen.")
                    continue
                page.bilder.append({"ort": ort, "bild": data, "b": _px(frame.get(_q("svg:width")), 64.0),
                                    "h": _px(frame.get(_q("svg:height")), 64.0), "bh": "seite", "bv": "seite",
                                    "ah": "", "av": "", "xh": _px(frame.get(_q("svg:x")), 0.0),
                                    "yv": _px(frame.get(_q("svg:y")), 0.0)})
        return page

    def run(self):
        body = self.inhalt.find(f"{_q('office:body')}/{_q('office:text')}")
        if body is None:
            raise DocumentIOError("Die Datei ist kein OpenDocument-Text (ODT) oder beschädigt.")
        content = self._inhalte(list(body))
        page = self._seite()
        standard = self.stile.eigenschaften("paragraph", "Standard", "text")
        grund = _format(standard, self.stile)
        title = self.metaelement.find(f".//{_q('dc:title')}") if self.metaelement is not None else None
        author = self.metaelement.find(f".//{_q('meta:initial-creator')}") if self.metaelement is not None else None
        if author is None and self.metaelement is not None:
            author = self.metaelement.find(f".//{_q('dc:creator')}")
        meta = {"title": title.text or "" if title is not None else "", "author": author.text or "" if author is not None else ""}
        return Document([Section("naechste", page, content)], default_format=grund, document_margin=0.0, lists=self.listen), page, meta, self.report


def _xml(data: bytes) -> ET.Element:
    from lunivo_writer.dienste.import_grenzen import sicheres_xml
    return sicheres_xml(data)


def lese_odt_modell(path: str, flach: bool = False):
    """→ (Document, PageSettings, meta, report), oder None bei Konstrukten mit Qt-Rückfall."""
    from lunivo_writer.dienste.import_grenzen import pruefe_paket
    if flach:
        try:
            with open(path, "rb") as file:
                data = file.read(GRENZE_BYTES + 1)
        except OSError as exc:
            raise DocumentIOError(f"Datei nicht lesbar: {exc.strerror or exc}") from exc
        if len(data) > GRENZE_BYTES:
            raise DocumentIOError("Die Datei ist zu groß, um sie sicher zu öffnen.")
        root = _xml(data)
        reader = _Leser(root, root, root.find(_q("office:meta")))
    else:
        pruefe_paket(path, "ODT")
        try:
            with zipfile.ZipFile(path) as archive:
                if sum(item.file_size for item in archive.infolist()) > GRENZE_BYTES:
                    raise DocumentIOError("Die ODT-Datei ist entpackt zu groß, um sie sicher zu öffnen.")
                names = set(archive.namelist())
                if "content.xml" not in names:
                    raise DocumentIOError("Die Datei ist kein gültiges ODT-Dokument oder beschädigt (content.xml fehlt).")
                content = _xml(archive.read("content.xml"))
                styles = _xml(archive.read("styles.xml")) if "styles.xml" in names else None
                metadata = _xml(archive.read("meta.xml")) if "meta.xml" in names else None
                bilddaten = {}
                for image in styles.iter(_q("draw:image")) if styles is not None else ():
                    href = image.get(_q("xlink:href"), "").lstrip("./")
                    if href in names:
                        bilddaten[href] = archive.read(href)
                bild_laden = bilddaten.get
        except (zipfile.BadZipFile, KeyError, OSError) as exc:
            raise DocumentIOError("Die Datei ist kein gültiges ODT-Dokument oder beschädigt.") from exc
        reader = _Leser(content, styles, metadata, bild_laden)
    try:
        return reader.run()
    except NichtImModell:
        return None
