"""Qt-Textdokument ↔ ``core.document.Document``: verlustfreie Umwandlung in beide Richtungen.

``document_from_qt`` liest ein ``QTextDocument`` in das Qt-freie Modell, ``document_to_qt`` baut aus dem Modell ein ``QTextDocument``. Alle Eigenschaften der Formate gehen
mit (benannt nach ``QTextFormat.Property``, Lunivos eigene als ``user:<Zahl>``); was das Modell nicht abbilden kann (Farbverlauf, Bildmuster als Pinsel, unbekannte Werttypen),
löst ``NichtUebertragbar`` aus, statt es stillschweigend zu verlieren. Der Editor und der DOCX-Import arbeiten weiter auf ``QTextDocument``; diese Umwandlung ist die Brücke
(Phase 4, Rundlaufprüfung: ``vergleichen``)."""
from __future__ import annotations

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QPointF, QUrl, Qt
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QGradient, QImage, QLinearGradient, QPen, QRadialGradient, QPixmap, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument, QTextFormat, QTextFrameFormat,
                           QTextImageFormat, QTextListFormat, QTextLength, QTextOption, QTextTable, QTextTableFormat)

from lunivo_writer.core.document import (Brush, CharacterFormat, Color, Document, Frame, GradientBrush, Image, Length, LineSpacing, ListFormat, Paragraph, ParagraphFormat, Pen, RowHeight, Section, Table, TextureBrush,
                                         TableCell, TableRow, TabStop, TextRun)
from lunivo_writer.editor.objekte import bilddaten
from lunivo_writer.editor.seite import abschnitte as AB


class NichtUebertragbar(Exception):
    """Ein Wert oder Aufbau des Qt-Dokuments hat im Modell (noch) keine Entsprechung."""


# ---- Eigenschaften ------------------------------------------------------------------------------------------------------------
_NAMEN = {int(v): k for k, v in QTextFormat.Property.__members__.items()}
_IDS = {k: int(v) for k, v in QTextFormat.Property.__members__.items()}
_OBJEKTINDEX = int(QTextFormat.ObjectIndex)                                   # gehört dem Dokument, nicht dem Format
_ART = {QTextLength.VariableLength: "variable", QTextLength.FixedLength: "fixed", QTextLength.PercentageLength: "percentage"}
_ART_UMGEKEHRT = {v: k for k, v in _ART.items()}


def _name(i: int) -> str:
    return _NAMEN.get(i) or f"user:{i}"


def _id(name: str) -> int:
    return _IDS[name] if name in _IDS else int(name.split(":", 1)[1])


def _wert(v, name: str):
    if isinstance(v, (bool, int, float, str)):
        return v
    if isinstance(v, QBrush):
        g = v.gradient()
        if g is not None:
            return _verlauf(g)
        if not v.textureImage().isNull():
            return TextureBrush(int(getattr(v.style(), "value", v.style())), _png(v.textureImage()))
        return Brush(int(getattr(v.style(), "value", v.style())), _farbe(v.color()))
    if isinstance(v, QPen):
        return Pen(_wert(v.brush(), name), v.widthF(), int(getattr(v.style(), "value", v.style())), int(getattr(v.capStyle(), "value", v.capStyle())),
                   int(getattr(v.joinStyle(), "value", v.joinStyle())))
    if isinstance(v, QColor):
        return _farbe(v)
    if isinstance(v, QTextLength):
        return Length(_ART[v.type()], float(v.rawValue()))
    if isinstance(v, QTextOption.Tab):
        return TabStop(float(v.position), int(getattr(v.type, "value", v.type)), v.delimiter)
    if isinstance(v, (list, tuple)):
        return tuple(_wert(x, name) for x in v)
    raise NichtUebertragbar(f"{name}: Werttyp {type(v).__name__}")


def _verlauf(g) -> GradientBrush:
    art = g.type()
    if art == QGradient.Type.LinearGradient:
        art_, punkte = "linear", (g.start().x(), g.start().y(), g.finalStop().x(), g.finalStop().y())
    elif art == QGradient.Type.RadialGradient:
        art_, punkte = "radial", (g.center().x(), g.center().y(), g.radius(), g.focalPoint().x(), g.focalPoint().y())
    elif art == QGradient.Type.ConicalGradient:
        art_, punkte = "conical", (g.center().x(), g.center().y(), g.angle())
    else:
        raise NichtUebertragbar(f"Verlauf der Art {art}")
    return GradientBrush(art_, punkte, tuple((float(p), _farbe(c)) for p, c in g.stops()), int(getattr(g.spread(), "value", g.spread())),
                         int(getattr(g.coordinateMode(), "value", g.coordinateMode())))


def _verlauf_zurueck(v: GradientBrush):
    if v.kind == "linear":
        g = QLinearGradient(v.punkte[0], v.punkte[1], v.punkte[2], v.punkte[3])
    elif v.kind == "radial":
        g = QRadialGradient(QPointF(v.punkte[0], v.punkte[1]), v.punkte[2], QPointF(v.punkte[3], v.punkte[4]))
    else:
        g = QConicalGradient(QPointF(v.punkte[0], v.punkte[1]), v.punkte[2])
    for pos, c in v.stops:
        g.setColorAt(pos, _zurueck(c))
    g.setSpread(QGradient.Spread(v.spread))
    g.setCoordinateMode(QGradient.CoordinateMode(v.mode))
    return g


def _farbe(c: QColor) -> Color:
    return Color(c.red(), c.green(), c.blue(), c.alpha())


def _zurueck(v):
    if isinstance(v, Color):
        return QColor(v.r, v.g, v.b, v.a)
    if isinstance(v, Brush):
        return QBrush(_zurueck(v.color), Qt.BrushStyle(v.style))
    if isinstance(v, GradientBrush):
        return QBrush(_verlauf_zurueck(v))
    if isinstance(v, TextureBrush):
        return QBrush(QImage.fromData(v.png, "PNG"))
    if isinstance(v, Pen):
        stift = QPen(_zurueck(v.brush), v.width, Qt.PenStyle(v.style), Qt.PenCapStyle(v.cap), Qt.PenJoinStyle(v.join))
        return stift
    if isinstance(v, Length):
        return QTextLength(_ART_UMGEKEHRT[v.kind], v.value)
    if isinstance(v, TabStop):
        return QTextOption.Tab(v.position, QTextOption.TabType(v.kind), v.delimiter)
    if isinstance(v, tuple):
        return [_zurueck(x) for x in v]
    return v


_SCHRIFTMERKMALE = int(QTextFormat.FontFeatures)                              # PySide kann diesen Wert (Zuordnung Tag → Zahl) nicht lesen und stürzt in ``properties()`` ab


def eigenschaften(fmt: QTextFormat) -> dict:
    """Alle Eigenschaften eines Formats als {Name: neutraler Wert}."""
    if fmt.hasProperty(_SCHRIFTMERKMALE):
        if fmt.isCharFormat() and fmt.toCharFormat().font().featureTags():
            raise NichtUebertragbar("FontFeatures: OpenType-Schriftmerkmale")
        fmt = type(fmt)(fmt)                                                      # Kopie ohne die leere Zuordnung
        fmt.clearProperty(_SCHRIFTMERKMALE)
    props = {}
    for k, v in fmt.properties().items():
        if k == _OBJEKTINDEX or (isinstance(v, dict) and not v):             # leere Zuordnungen (Schriftmerkmale, Variationsachsen) sind der Standardwert
            continue
        props[_name(k)] = _wert(v, _name(k))
    return props


def _setzen(fmt: QTextFormat, props: dict) -> None:
    for name, v in props.items():
        fmt.setProperty(_id(name), _zurueck(v))


_ALIGNMENT_QT = {"left": 0x1, "right": 0x2, "center": 0x4, "justify": 0x8}


def absatzformat_aus_qt(fmt: QTextBlockFormat, char_format: CharacterFormat | None = None,
                        list_id: int | None = None, visible: bool = True) -> ParagraphFormat:
    """Absatzformat samt unverändertem Qt-Eigenschaften-Bag und semantischen Ausrichtungs-, Abstands- und Einzugswerten lesen."""
    props = eigenschaften(fmt)
    roh = props.get("BlockAlignment")
    try:
        horizontal = int(roh) & 0xF
    except (TypeError, ValueError):
        horizontal = 0
    ausrichtung = next((name for name, bit in (("justify", 0x8), ("center", 0x4), ("right", 0x2), ("left", 0x1))
                        if horizontal & bit), None)
    pixelwerte = {}
    for feld, eigenschaft in (("space_before_px", "BlockTopMargin"), ("space_after_px", "BlockBottomMargin"),
                              ("left_indent_px", "BlockLeftMargin"), ("right_indent_px", "BlockRightMargin"),
                              ("first_line_indent_px", "TextIndent")):
        wert = props.get(eigenschaft)
        pixelwerte[feld] = float(wert) if isinstance(wert, (int, float)) and not isinstance(wert, bool) else None
    zeilenabstand = None
    if "LineHeightType" in props:
        try:
            art = {0: "single", 1: "proportional", 2: "fixed", 3: "minimum"}.get(int(props["LineHeightType"]))
            wert = props.get("LineHeight", 0.0)
            if art is not None and isinstance(wert, (int, float)) and not isinstance(wert, bool):
                zeilenabstand = LineSpacing(art, float(wert))
        except (TypeError, ValueError):
            pass
    return ParagraphFormat(props, char_format or CharacterFormat(), list_id, visible, ausrichtung, **pixelwerte, line_spacing=zeilenabstand)


def absatzformat_zu_qt_properties(fmt: ParagraphFormat) -> dict:
    """Semantische Absatzwerte in den Qt-Eigenschafts-Bag schreiben; unbekannte Werte und Alignment-Bits bleiben erhalten."""
    props = dict(fmt.properties)
    if fmt.alignment in _ALIGNMENT_QT:
        try:
            bisher = int(props.get("BlockAlignment", 0))
        except (TypeError, ValueError):
            bisher = 0
        props["BlockAlignment"] = (bisher & ~0xF) | _ALIGNMENT_QT[fmt.alignment]
    for feld, eigenschaft in (("space_before_px", "BlockTopMargin"), ("space_after_px", "BlockBottomMargin"),
                              ("left_indent_px", "BlockLeftMargin"), ("right_indent_px", "BlockRightMargin"),
                              ("first_line_indent_px", "TextIndent")):
        wert = getattr(fmt, feld)
        if wert is not None:
            props[eigenschaft] = wert
    if fmt.line_spacing is not None:
        zeilenarten = {"single": (0, 1.0), "proportional": (1, 1.0), "multiple": (1, 100.0),
                       "fixed": (2, 1.0), "minimum": (3, 1.0)}
        umrechnung = zeilenarten.get(fmt.line_spacing.kind)
        if umrechnung is not None:
            art, faktor = umrechnung
            props["LineHeightType"] = art
            props["LineHeight"] = fmt.line_spacing.value * faktor
    return props


def zeichenformat_aus_qt(fmt: QTextFormat) -> CharacterFormat:
    """Zeichenformat samt verlustfreiem Qt-Eigenschaften-Bag und häufigen semantischen Feldern lesen."""
    props = eigenschaften(fmt)
    familie = props.get("FontFamilies", props.get("FontFamily"))
    if isinstance(familie, (tuple, list)):
        familie = familie[0] if familie else None
    if not isinstance(familie, str):
        familie = None
    groesse = props.get("FontPointSize")
    if not isinstance(groesse, (int, float)) or groesse <= 0:
        px = props.get("FontPixelSize")
        groesse = float(px) * 72.0 / 96.0 if isinstance(px, (int, float)) and px > 0 else None
    gewicht = props.get("FontWeight")
    if not isinstance(gewicht, (int, float)) or isinstance(gewicht, bool):
        gewicht = None
    kursiv = props.get("FontItalic") if "FontItalic" in props else None
    if kursiv is not None:
        kursiv = bool(kursiv)
    pinsel = props.get("ForegroundBrush")
    farbe = pinsel.color if isinstance(pinsel, Brush) and pinsel.style == 1 else pinsel if isinstance(pinsel, Color) else None
    unter = None
    if "FontUnderline" in props or "TextUnderlineStyle" in props:
        unter = bool(props.get("FontUnderline") or props.get("TextUnderlineStyle", 0))
    return CharacterFormat(props, familie, float(groesse) if groesse is not None else None,
                          int(gewicht) if gewicht is not None else None, kursiv, farbe, unter)


def zeichenformat_zu_qt_properties(fmt: CharacterFormat) -> dict:
    """Semantische Zeichenfelder in den verlustfreien Qt-Eigenschaften-Bag überführen; unbekannte Werte bleiben erhalten."""
    props = dict(fmt.properties)
    familie = props.get("FontFamilies", props.get("FontFamily"))
    if isinstance(familie, (tuple, list)):
        familie = familie[0] if familie else None
    if fmt.family is not None and fmt.family != familie:
        if isinstance(props.get("FontFamilies"), (tuple, list)):
            alt = tuple(props["FontFamilies"])
            props["FontFamilies"] = (fmt.family, *alt[1:])
        elif "FontFamily" in props:
            props["FontFamily"] = fmt.family
        else:
            props["FontFamilies"] = (fmt.family,)
    groesse = props.get("FontPointSize")
    if not isinstance(groesse, (int, float)) or groesse <= 0:
        px = props.get("FontPixelSize")
        groesse = float(px) * 72.0 / 96.0 if isinstance(px, (int, float)) and px > 0 else None
    if fmt.size_pt is not None and fmt.size_pt != groesse:
        if "FontPointSize" in props or "FontPixelSize" not in props:
            props["FontPointSize"] = fmt.size_pt
        if "FontPixelSize" in props:
            props["FontPixelSize"] = fmt.size_pt * 96.0 / 72.0
    if fmt.weight is not None and fmt.weight != props.get("FontWeight"):
        props["FontWeight"] = fmt.weight
    if fmt.italic is not None and fmt.italic != props.get("FontItalic"):
        props["FontItalic"] = fmt.italic
    pinsel = props.get("ForegroundBrush")
    aktuelle_farbe = pinsel.color if isinstance(pinsel, Brush) and pinsel.style == 1 else pinsel if isinstance(pinsel, Color) else None
    if fmt.foreground_color is not None and fmt.foreground_color != aktuelle_farbe:
        stil = pinsel.style if isinstance(pinsel, Brush) else 1
        props["ForegroundBrush"] = Brush(stil, fmt.foreground_color)
    unter = bool(props.get("FontUnderline") or props.get("TextUnderlineStyle", 0))
    if fmt.underline is not None and fmt.underline != unter:
        props["FontUnderline"] = fmt.underline
        if not fmt.underline and "TextUnderlineStyle" in props:
            props["TextUnderlineStyle"] = 0
    return props


# ---- Qt → Modell --------------------------------------------------------------------------------------------------------------
class _Lesen:
    def __init__(self, doc: QTextDocument):
        self.doc = doc
        self.listen: dict[int, int] = {}                 # Objektindex der Liste → Nummer im Modell
        self.listenformate: dict[int, ListFormat] = {}


def _bild_daten(doc: QTextDocument, name: str):
    r = doc.resource(QTextDocument.ImageResource, QUrl(name))
    if isinstance(r, QPixmap):
        r = r.toImage()
    return r if isinstance(r, QImage) and not r.isNull() else None


def _png(img: QImage) -> bytes:
    puffer = QByteArray()
    geraet = QBuffer(puffer)
    geraet.open(QIODevice.WriteOnly)
    img.save(geraet, "PNG")
    geraet.close()
    return bytes(puffer.data())


def _bild(cf: QTextCharFormat, ctx: _Lesen, name: str | None = None) -> Image:
    img = _bild_daten(ctx.doc, name if name is not None else cf.toImageFormat().name())
    quelle = bilddaten.quelle_zu(img) if img is not None else None
    return Image(_png(img) if img is not None else b"", zeichenformat_aus_qt(cf),
                 quelle.daten if quelle else None, quelle.format if quelle else None, quelle.ersatz_png if quelle else None,
                 bool(quelle.nur_raster) if quelle else False)


def bild_aus_qimage(img: QImage) -> Image:
    """Ein ``QImage`` (mit seinem Original aus der Ablage) als Modell-``Image``."""
    quelle = bilddaten.quelle_zu(img)
    return Image(_png(img), CharacterFormat(), quelle.daten if quelle else None, quelle.format if quelle else None, quelle.ersatz_png if quelle else None,
                 bool(quelle.nur_raster) if quelle else False)


def bild_aus_format(cf: QTextCharFormat, doc: QTextDocument) -> Image:
    """Das Bild zu einem Bildformat (Name → Bild im Ressourcenspeicher von ``doc``) als Modell-``Image``."""
    return _bild(cf, _Lesen(doc))


def _absatz(b, ctx: _Lesen, oberste_ebene: bool):
    bf = b.blockFormat()
    props = eigenschaften(bf)
    abschnitt = None
    if oberste_ebene and bf.hasProperty(AB.B_ABSCHNITT):
        abschnitt = AB.lesen(bf)
        props.pop(_name(int(AB.B_ABSCHNITT)), None)
    liste = b.textList()
    list_id = None
    if liste is not None:
        key = bf.objectIndex()
        if key not in ctx.listen:
            ctx.listen[key] = len(ctx.listen) + 1
            ctx.listenformate[ctx.listen[key]] = ListFormat(eigenschaften(liste.format()))
        list_id = ctx.listen[key]
    runs = []
    it = b.begin()
    while not it.atEnd():
        f = it.fragment()
        cf = f.charFormat()
        if cf.isImageFormat():
            runs += [_bild(cf, ctx) for _ in range(max(1, len(f.text())))]
        else:
            runs.append(TextRun(f.text(), zeichenformat_aus_qt(cf)))
        it += 1
    absatzformat = absatzformat_aus_qt(bf, zeichenformat_aus_qt(b.charFormat()), list_id, b.isVisible())
    absatzformat.properties = props
    return Paragraph(absatzformat, runs), abschnitt


def _inhalt(it, ctx: _Lesen, oberste_ebene: bool = False, abschnitte: list | None = None) -> list:
    aus = []
    while not it.atEnd():
        b = it.currentBlock()
        if b.isValid():
            p, abschnitt = _absatz(b, ctx, oberste_ebene)
            aus.append(p)
            if abschnitt is not None and abschnitte is not None:
                abschnitte.append((len(aus), abschnitt))
        else:
            f = it.currentFrame()
            if isinstance(f, QTextTable):
                aus.append(_tabelle(f, ctx))
            elif f is not None:
                aus.append(Frame(eigenschaften(f.frameFormat()), _inhalt(f.begin(), ctx)))
        it += 1
    return aus


def _tabelle(t: QTextTable, ctx: _Lesen) -> Table:
    from lunivo_writer.core.layout.seitenumbruch import P_ZEILE_HOEHE_ART, P_ZEILE_MINHOEHE
    tab = Table(t.rows(), t.columns(), eigenschaften(t.format()))
    for r in range(t.rows()):
        zeile = TableRow()
        for c in range(t.columns()):
            z = t.cellAt(r, c)
            if z.isValid() and z.row() == r and z.column() == c:
                zeile.cells.append(TableCell(r, c, z.rowSpan(), z.columnSpan(), eigenschaften(z.format()), _inhalt(z.begin(), ctx)))
        werte = [z.properties.get(P_ZEILE_MINHOEHE) for z in zeile.cells]
        werte = [v for v in werte if isinstance(v, (int, float)) and v > 0]
        zeile.minimum_height_px = max(werte) if werte else None
        art = next((z.properties.get(P_ZEILE_HOEHE_ART) for z in zeile.cells if z.properties.get(P_ZEILE_HOEHE_ART) in ("minimum", "exact")), None)
        if art is not None and zeile.minimum_height_px is not None:
            zeile.row_height = RowHeight(art, zeile.minimum_height_px)
        elif zeile.minimum_height_px is not None:
            zeile.row_height = RowHeight("minimum", zeile.minimum_height_px)
        tab.table_rows.append(zeile)
    return tab


def _enum(v) -> int:
    return int(getattr(v, "value", v))


def textoption_lesen(o: QTextOption) -> dict:
    return {"tab_stop_distance": float(o.tabStopDistance()), "wrap_mode": _enum(o.wrapMode()), "alignment": _enum(o.alignment()),
            "direction": _enum(o.textDirection()), "flags": _enum(o.flags()), "design_metrics": bool(o.useDesignMetrics()),
            "tabs": tuple(_wert(t, "tabs") for t in o.tabs())}


def textoption_setzen(o: QTextOption, w: dict) -> None:
    if not w:
        return
    o.setTabStopDistance(w["tab_stop_distance"])
    o.setWrapMode(QTextOption.WrapMode(w["wrap_mode"]))
    o.setAlignment(Qt.AlignmentFlag(w["alignment"]))
    o.setTextDirection(Qt.LayoutDirection(w["direction"]))
    o.setFlags(QTextOption.Flag(w["flags"]))
    o.setUseDesignMetrics(w["design_metrics"])
    o.setTabs([_zurueck(t) for t in w["tabs"]])


def schnitte_bilden(oben: list, marken: list, page) -> list:
    """Die obersten Blöcke an den Abschnittsmarken in ``Section`` teilen: ``marken`` = [(Zahl der Blöcke bis einschließlich des Marken-Absatzes, (Beginn, PageSettings des folgenden Abschnitts))]."""
    schnitte, start, art, seite = [], 0, "naechste", page
    for ende, (typ, ps) in marken:
        schnitte.append(Section(art, seite, oben[start:ende]))
        start, art, seite = ende, typ, ps
    schnitte.append(Section(art, seite, oben[start:]))
    return schnitte


def medien_sammeln(modell: Document, doc: QTextDocument) -> dict:
    """Die Bilder, auf die Absätze nur mit einem Namen verweisen (frei positionierte Bilder und ihre Füllbilder, ``B_BILDANKER``), aus dem Ressourcenspeicher von ``doc``
    als Modell-``Image`` — damit sie mit dem Modell wandern und beim Zurückbauen wieder da sind."""
    import json
    from lunivo_writer.editor.dokument.zusatz import B_BILDANKER
    schluessel = f"user:{int(B_BILDANKER)}"
    medien: dict = {}

    def pruefen(blocks: list) -> None:
        for b in blocks:
            if isinstance(b, Paragraph):
                roh = b.format.properties.get(schluessel)
                if not isinstance(roh, str):
                    continue
                try:
                    angaben = json.loads(roh)
                except ValueError:
                    continue
                for a in angaben if isinstance(angaben, list) else []:
                    for name in (a.get("n"), (a.get("fuell") or {}).get("n")):
                        if name and name not in medien and _bild_daten(doc, name) is not None:
                            medien[name] = _bild(QTextImageFormat(), _Lesen(doc), name)
            elif isinstance(b, Table):
                for z in b.table_rows:
                    for c in z.cells:
                        pruefen(c.content)
            elif isinstance(b, Frame):
                pruefen(b.content)
    for s in modell.sections:
        pruefen(s.content)
    return medien


def document_from_qt(doc: QTextDocument, page=None) -> Document:
    """Das Qt-Dokument als Modell. ``page``: Seiteneinrichtung des ersten Abschnitts (``PageSettings``); spätere Abschnitte kommen aus den Abschnittsmarken des Dokuments."""
    ctx = _Lesen(doc)
    marken: list = []
    oben = _inhalt(doc.rootFrame().begin(), ctx, True, marken)
    schnitte = schnitte_bilden(oben, marken, page)
    grund = QTextCharFormat()
    grund.setFont(doc.defaultFont())
    modell = Document(schnitte, zeichenformat_aus_qt(grund), doc.documentMargin(), doc.indentWidth(),
                      eigenschaften(doc.rootFrame().frameFormat()), textoption_lesen(doc.defaultTextOption()), dict(ctx.listenformate))
    modell.media = medien_sammeln(modell, doc)
    return modell


# ---- Modell → Qt --------------------------------------------------------------------------------------------------------------
class _Schreiben:
    def __init__(self, doc: QTextDocument, modell: Document):
        self.doc, self.modell = doc, modell
        self.listen: dict[int, object] = {}
        self.unsichtbar: list = []
        self.bildzaehler = 0


def _runs_schreiben(cursor: QTextCursor, p: Paragraph, ctx: _Schreiben) -> None:
    for r in p.runs:
        cf = QTextCharFormat()
        if isinstance(r, TextRun):
            _setzen(cf, zeichenformat_zu_qt_properties(r.format))
            if r.text:
                cursor.insertText(r.text, cf)
            continue
        fmt = QTextImageFormat()
        _setzen(fmt, zeichenformat_zu_qt_properties(r.format))
        if r.raster_png:
            img = QImage.fromData(r.raster_png, "PNG")
            ctx.doc.addResource(QTextDocument.ImageResource, QUrl(fmt.name()), img)
            if r.original:
                bilddaten.merken(img, r.original, r.fallback_png, r.raster_only)
        cursor.insertImage(fmt)


def _absatz_schreiben(cursor: QTextCursor, p: Paragraph, ctx: _Schreiben, frisch: bool, marke: str | None) -> None:
    props = absatzformat_zu_qt_properties(p.format)
    if marke is not None:
        props[_name(int(AB.B_ABSCHNITT))] = marke
    bf, cf = QTextBlockFormat(), QTextCharFormat()
    _setzen(bf, props)
    _setzen(cf, zeichenformat_zu_qt_properties(p.format.char_format))
    if frisch:
        cursor.setBlockFormat(bf)
        cursor.setBlockCharFormat(cf)
    else:
        cursor.insertBlock(bf, cf)
    if p.format.list_id is not None:
        liste = ctx.listen.get(p.format.list_id)
        if liste is None:
            lf = QTextListFormat()
            _setzen(lf, ctx.modell.lists[p.format.list_id].properties)
            ctx.listen[p.format.list_id] = cursor.createList(lf)
        else:
            liste.add(cursor.block())
    _runs_schreiben(cursor, p, ctx)
    if not p.format.visible:
        ctx.unsichtbar.append(cursor.block())


def _inhalt_schreiben(cursor: QTextCursor, bloecke: list, ctx: _Schreiben, frisch: bool = True, letzte_marke: str | None = None) -> bool:
    for i, blk in enumerate(bloecke):
        if isinstance(blk, Paragraph):
            _absatz_schreiben(cursor, blk, ctx, frisch, letzte_marke if i == len(bloecke) - 1 else None)
            frisch = False
        elif isinstance(blk, Table):
            from lunivo_writer.core.layout.seitenumbruch import P_ZEILE_HOEHE_ART, P_ZEILE_MINHOEHE
            tf = QTextTableFormat()
            _setzen(tf, blk.properties)
            tabelle = cursor.insertTable(blk.rows, blk.columns, tf)
            zellen = [z for zeile in blk.table_rows for z in zeile.cells]
            for z in zellen:
                if z.row_span > 1 or z.column_span > 1:
                    tabelle.mergeCells(z.row, z.column, z.row_span, z.column_span)
            for z in zellen:
                zelle = tabelle.cellAt(z.row, z.column)
                zf = QTextCharFormat()
                eig = dict(z.properties)
                if z.row < len(blk.table_rows):
                    zeile = blk.table_rows[z.row]
                    hoehe = zeile.row_height
                    if hoehe is not None:
                        eig[P_ZEILE_MINHOEHE] = float(hoehe.value_px)
                        eig[P_ZEILE_HOEHE_ART] = hoehe.kind
                    elif zeile.minimum_height_px is not None:
                        eig[P_ZEILE_MINHOEHE] = float(zeile.minimum_height_px)
                        eig[P_ZEILE_HOEHE_ART] = "minimum"
                _setzen(zf, eig)
                zelle.setFormat(zf)
                _inhalt_schreiben(zelle.firstCursorPosition(), z.content, ctx)
            cursor.setPosition(tabelle.lastPosition() + 1)
            frisch = True
        elif isinstance(blk, Frame):
            ff = QTextFrameFormat()
            _setzen(ff, blk.properties)
            rahmen = cursor.insertFrame(ff)
            _inhalt_schreiben(rahmen.firstCursorPosition(), blk.content, ctx)
            cursor.setPosition(rahmen.lastPosition() + 1)
            frisch = True
    return frisch


def document_to_qt(modell: Document) -> QTextDocument:
    """Aus dem Modell ein neues ``QTextDocument`` (Abschnittsmarken, Listen, Tabellen, Rahmen und Bilder inbegriffen)."""
    doc = QTextDocument()
    grund = QTextCharFormat()
    _setzen(grund, zeichenformat_zu_qt_properties(modell.default_format))
    doc.setDefaultFont(grund.font())
    doc.setDocumentMargin(modell.document_margin)
    doc.setIndentWidth(modell.indent_width)
    wurzel = doc.rootFrame().frameFormat()
    _setzen(wurzel, modell.root_properties)
    doc.rootFrame().setFrameFormat(wurzel)
    opt = doc.defaultTextOption()
    textoption_setzen(opt, modell.text_option)
    doc.setDefaultTextOption(opt)
    ctx = _Schreiben(doc, modell)
    for name, bild in modell.media.items():                                     # Bilder, auf die nur ein Name verweist
        if bild.raster_png:
            img = QImage.fromData(bild.raster_png, "PNG")
            doc.addResource(QTextDocument.ImageResource, QUrl(name), img)
            if bild.original:
                bilddaten.merken(img, bild.original, bild.fallback_png, bild.raster_only)
    cursor = QTextCursor(doc)
    frisch = True
    for i, s in enumerate(modell.sections):
        marke = AB.eintrag(modell.sections[i + 1].kind, modell.sections[i + 1].page) if i + 1 < len(modell.sections) else None
        frisch = _inhalt_schreiben(cursor, s.content, ctx, frisch, marke)
    for b in ctx.unsichtbar:
        b.setVisible(False)
    return doc


# ---- Rundlaufprüfung ----------------------------------------------------------------------------------------------------------
def _signatur(it, doc: QTextDocument, aus: list, tiefe: str = "") -> None:
    while not it.atEnd():
        b = it.currentBlock()
        if b.isValid():
            liste = b.textList()
            aus.append((tiefe + "absatz", b.text(), eigenschaften(b.blockFormat()), eigenschaften(b.charFormat()), b.isVisible(),
                        None if liste is None else (eigenschaften(liste.format()), liste.itemNumber(b))))
            f = b.begin()
            while not f.atEnd():
                fr = f.fragment()
                cf = fr.charFormat()
                bild = None
                if cf.isImageFormat():
                    img = _bild_daten(doc, cf.toImageFormat().name())
                    q = bilddaten.quelle_zu(img) if img is not None else None
                    bild = None if img is None else (img.width(), img.height(), _png(img), q.format if q else None, q.daten if q else None)
                eig = eigenschaften(cf)
                if bild is None and aus and aus[-1][0] == tiefe + "stueck" and aus[-1][3] is None and aus[-1][2] == eig:
                    aus[-1] = (aus[-1][0], aus[-1][1] + fr.text(), eig, None)         # gleich formatierte Nachbarstücke zählen als eines (Qt teilt sie nach leeren Standardwerten)
                else:
                    aus.append((tiefe + "stueck", fr.text(), eig, bild))
                f += 1
        else:
            fr = it.currentFrame()
            if isinstance(fr, QTextTable):
                aus.append((tiefe + "tabelle", fr.rows(), fr.columns(), eigenschaften(fr.format())))
                for r in range(fr.rows()):
                    for c in range(fr.columns()):
                        z = fr.cellAt(r, c)
                        if z.isValid() and z.row() == r and z.column() == c:
                            aus.append((tiefe + "zelle", r, c, z.rowSpan(), z.columnSpan(), eigenschaften(z.format())))
                            _signatur(z.begin(), doc, aus, tiefe + "  ")
            elif fr is not None:
                aus.append((tiefe + "rahmen", eigenschaften(fr.frameFormat())))
                _signatur(fr.begin(), doc, aus, tiefe + "  ")
        it += 1


def vergleichen(a: QTextDocument, b: QTextDocument) -> list[str]:
    """Unterschiede zweier Qt-Dokumente in Text, Formaten, Listen, Tabellen, Rahmen und Bildern (leer: gleich). Für die Rundlaufprüfung Qt → Modell → Qt."""
    sa, sb = [], []
    _signatur(a.rootFrame().begin(), a, sa)
    _signatur(b.rootFrame().begin(), b, sb)
    funde = []
    if len(sa) != len(sb):
        funde.append(f"Aufbau: {len(sa)} gegen {len(sb)} Elemente")
    for i, (x, y) in enumerate(zip(sa, sb)):
        if x != y:
            funde.append(f"Element {i} ({x[0]}): {x[1:3]!r} gegen {y[1:3]!r}"[:300])
            if len(funde) >= 5:
                break
    ra, rb = eigenschaften(a.rootFrame().frameFormat()), eigenschaften(b.rootFrame().frameFormat())
    if ra != rb or a.documentMargin() != b.documentMargin() or a.defaultFont() != b.defaultFont():
        funde.append("Dokumentrahmen, Rand oder Grundschrift")
    if textoption_lesen(a.defaultTextOption()) != textoption_lesen(b.defaultTextOption()):
        funde.append("Grundeinstellung des Textsatzes (Tabstoppabstand, Umbruchart, …)")
    return funde
