"""Textdarstellung für frei positionierte Objekte."""

from PySide6.QtCore import QRectF, QUrl, Qt
from PySide6.QtGui import (QBrush, QColor, QFont, QFontMetricsF, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QTextCursor,
                           QTextDocument, QTextOption)

from lunivo_writer.editor.objekte import freie_bilder as FB
from lunivo_writer.editor.text.mehrstufig import nummer_text

ARTEN = ("wordart", "textfeld", "form", "diagramm", "smartart", "piktogramm", "zeichenbereich")
TEXT_ARTEN = ("wordart", "textfeld")                                 # Arten mit Text zum Schreiben (Texttools, Eingabefeld im Objekt)
STANDARD_MASS = {"form": (160, 120), "diagramm": (480, 300), "zeichenbereich": (567, 302)}         # Größe in Bildpunkten, wenn beim Einfügen keine angegeben ist
FORM_STANDARD = {"form": "Rechteck", "fuell": "#4a8fd8", "linie": "#1f3864", "strich": 2.0, "text": ""}
TEXTFELD_STANDARD = {"text": "", "schrift": "Liberation Sans", "pt": 11, "farbe": "#1f1f1f"}
TEXTFELD_FUELL = {"art": "farbe", "farbe": "#ffffff"}
TEXTFELD_RAND = {"b": 1.5, "farbe": "#1f3864", "art": "einfach"}
WORDART_STANDARD = {"text": "Hier Text einfügen", "vorlage": 0, "pt": 36, "schrift": "Liberation Sans"}
_SS = 2                                                              # Zeichnen in doppelter Auflösung (scharf auch bei Zoom)


# ---- Gemeinsame Hilfen: Listenmarken, Textrichtung, Effekte ---------------------------------------------------------------
RICHTUNGEN = ("waagerecht", "senkrecht_rl", "senkrecht_lr", "dreh90", "dreh270", "asiatisch270")
_PUNKTE = {"disc": "\u25cf", "circle": "\u25cb", "square": "\u25a0"}


def listenmarken(liste, anzahl: int) -> list[str]:
    """Die Marke jeder Zeile (mit Leerzeichen dahinter): Aufzählungszeichen oder Nummer nach dem Listenwert aus ``editor/text/listen.py``
    (``stil``, ``praefix``, ``suffix``, ``start``) oder einer mehrstufigen Liste (``ebenen``). Leer: keine Liste."""
    if not liste:
        return [""] * anzahl
    if isinstance(liste, str):                                       # alte Schreibweise
        liste = {"stil": "disc"} if liste == "punkt" else {"stil": "dezimal", "praefix": "", "suffix": ".", "start": 1}
    if liste.get("ebenen"):
        z = liste["ebenen"][0].get("format") or "\u2022"
        return [f"{z} "] * anzahl
    stil = liste.get("stil", "disc")
    if stil in _PUNKTE:
        return [_PUNKTE[stil] + " "] * anzahl
    start = int(liste.get("start", 1))
    return [f"{liste.get('praefix', '')}{nummer_text(stil, start + i)}{liste.get('suffix', '')} " for i in range(anzahl)]


def richtung_anwenden(img: QImage, richtung: str | None, zeilenbaender: list | None = None) -> QImage:
    """Die Textrichtung am fertigen (waagerecht gesetzten) Bild: senkrecht_rl und dreh90 laufen von oben nach unten (Zeilen von rechts nach links),
    senkrecht_lr ebenso, aber die Zeilen folgen von links nach rechts, dreh270 dreht gegen den Uhrzeigersinn, asiatisch270 setzt lateinische
    Schrift wie senkrecht_rl (asiatische Zeichen werden nicht besonders gedreht)."""
    from PySide6.QtGui import QTransform
    if richtung in (None, "", "waagerecht"):
        return img
    if richtung == "vertikal":
        richtung = "senkrecht_rl"
    if richtung == "senkrecht_lr" and zeilenbaender:                 # Zeilen in umgekehrter Reihenfolge stapeln
        neu = QImage(img.size(), QImage.Format_ARGB32); neu.fill(Qt.transparent)
        q = QPainter(neu); y = 0
        for (y0, hh) in reversed(zeilenbaender):
            q.drawImage(0, y, img, 0, y0, img.width(), hh); y += hh
        q.end(); img = neu
    grad = 270 if richtung == "dreh270" else 90
    return img.transformed(QTransform().rotate(grad), Qt.SmoothTransformation)


def _gedreht(richtung: str | None) -> bool:
    return richtung not in (None, "", "waagerecht")


def effekte_auf_text(img: QImage, ef: dict, text_hoehe: float, farbe: str) -> QImage:
    """Leuchten und Spiegelung am fertig gezeichneten Text (durchsichtiges Bild in doppelter Auflösung)."""
    if not ef:
        return img
    out = QImage(img.size(), QImage.Format_ARGB32); out.fill(Qt.transparent)
    q = QPainter(out)
    if "leuchten" in ef:
        glut = QColor((ef["leuchten"] or {}).get("farbe") or farbe)
        maske = QImage(img.size(), QImage.Format_ARGB32); maske.fill(Qt.transparent)
        m = QPainter(maske); m.drawImage(0, 0, img); m.setCompositionMode(QPainter.CompositionMode_SourceIn); m.fillRect(maske.rect(), glut); m.end()
        q.setOpacity(0.16)
        import math
        for rad in (4, 8, 12):
            for k in range(12):
                w = 2 * math.pi * k / 12
                q.drawImage(round(math.cos(w) * rad), round(math.sin(w) * rad), maske)
        q.setOpacity(1.0)
    q.drawImage(0, 0, img)
    if "reflektion" in ef:                                           # Spiegelbild unter dem Text, nach unten verblassend
        th = int(text_hoehe * _SS)
        unten = img.copy(0, 0, img.width(), max(1, min(th, img.height()))).mirrored(False, True)
        r = QPainter(unten); r.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        g = QLinearGradient(0, 0, 0, unten.height()); g.setColorAt(0, QColor(0, 0, 0, 110)); g.setColorAt(0.7, QColor(0, 0, 0, 0))
        r.fillRect(unten.rect(), g); r.end()
        q.drawImage(0, th, unten)
    q.end()
    return out


# ---- Läufe: Text mit Zeichenformat je Abschnitt -------------------------------------------------------------------------------
ZEICHEN_SCHLUESSEL = ("fett", "kursiv", "unter", "unterfarbe", "durch", "hoch", "tief", "hervor", "fuell", "kontur", "schrift", "pt")


def anzeige_laeufe(d: dict) -> list[dict]:
    """Die Läufe, die das Objekt zeigt: ``[{"t": Text, <Zeichenschlüssel>…}]`` (Schlüssel, die fehlen, gelten für das ganze Objekt)."""
    if "gezeigt" in d:
        return d.get("gezeigt_laeufe") or [{"t": d["gezeigt"]}]
    return d.get("laeufe") or [{"t": d.get("text", "")}]


def laeufe_text(laeufe: list[dict]) -> str:
    return "".join(r["t"] for r in laeufe)


def laeufe_ab(laeufe: list[dict], von: int, bis: int | None = None) -> list[dict]:
    """Der Ausschnitt ``[von, bis)`` des Gesamttextes mit seinen Formaten."""
    out, pos = [], 0
    for r in laeufe:
        n = len(r["t"]); a, e = max(von, pos), min(pos + n if bis is None else bis, pos + n)
        if e > a:
            out.append({**r, "t": r["t"][a - pos:e - pos]})
        pos += n
    return out


def laeufe_zusammen(laeufe: list[dict]) -> list[dict]:
    """Benachbarte Läufe mit gleichem Format zu einem verbinden (leere fallen weg)."""
    out: list[dict] = []
    for r in laeufe:
        if not r["t"]:
            continue
        if out and {k: v for k, v in out[-1].items() if k != "t"} == {k: v for k, v in r.items() if k != "t"}:
            out[-1] = {**out[-1], "t": out[-1]["t"] + r["t"]}
        else:
            out.append(dict(r))
    return out


def _zeilen_laeufe(laeufe: list[dict]) -> list[list[dict]]:
    """Läufe in Zeilen (Absätze) teilen."""
    zeilen: list[list[dict]] = [[]]
    for r in laeufe:
        teile = r["t"].split("\n")
        for i, t in enumerate(teile):
            if i:
                zeilen.append([])
            if t:
                zeilen[-1].append({**r, "t": t})
    return zeilen


# ---- WordArt zeichnen ---------------------------------------------------------------------------------------------------
def wordart_zeichnen(d: dict) -> QImage:
    from lunivo_writer.editor.dokument import einfuegen as E
    laeufe = anzeige_laeufe(d)
    text = laeufe_text(laeufe) or " "
    pt = float(d.get("pt", 36))
    if d.get("vorlage") is None:                                       # alter Weg: Stil und Farbe
        return E.wordart_bild(text, d.get("stil", "Verlauf"), d.get("schrift", "Liberation Sans"), int(pt), d.get("farbe", "#2f78bd"))
    _n, f1, f2, kontur, kb, schatten = E.WORDART_VORLAGEN[int(d["vorlage"])]
    if "fuell" in d:
        f1 = f2 = d["fuell"] or None
    if "kontur" in d:
        kontur = d["kontur"] or None
        kb = float(d.get("kontur_breite", 1.5)) * 96 / 72 / max(1.0, pt / 36) if kontur else 0
    elif "kontur_breite" in d and kontur:
        kb = float(d["kontur_breite"]) * 96 / 72 / max(1.0, pt / 36)

    def eff(r: dict) -> dict:                                          # das Format eines Laufs: seine eigenen Angaben vor denen des Objekts
        return {k: r.get(k, d.get(k)) for k in ZEICHEN_SCHLUESSEL}

    def schrift_von(e: dict) -> QFont:
        f = QFont(e["schrift"] or "Liberation Sans"); f.setPointSizeF(float(e["pt"] or pt))
        f.setBold(True if e["fett"] is None else bool(e["fett"])); f.setItalic(bool(e["kursiv"]))
        if e["hoch"] or e["tief"]:
            f.setPointSizeF(f.pointSizeF() * 0.6)
        return f

    zeilen = _zeilen_laeufe(laeufe) or [[]]
    marken = listenmarken(d.get("liste"), len(zeilen))
    basis = eff({})
    segmente = []                                                      # je Zeile: [(Text, Format, Schrift, Metrik)]
    for m_, zl in zip(marken, zeilen):
        seg = ([(m_, basis)] if m_ else []) + [(r["t"], eff(r)) for r in zl]
        segmente.append([(t, e, schrift_von(e), QFontMetricsF(schrift_von(e))) for t, e in seg])
    einzug = 24.0 * int(d.get("einzug") or 0)
    fm0 = QFontMetricsF(schrift_von(basis))
    hoehen = [max([m_[3].height() for m_ in sg] or [fm0.height()]) for sg in segmente]
    asz = [max([m_[3].ascent() for m_ in sg] or [fm0.ascent()]) for sg in segmente]
    faktor = float(d.get("zeilenabstand") or 1.0)
    breiten = [sum(m_[3].horizontalAdvance(m_[0]) for m_ in sg) + einzug for sg in segmente]
    ys, y_ = [], 20.0
    for hh, aa in zip(hoehen, asz):
        ys.append(y_ + aa); y_ += hh * faktor
    b, h = int(max(breiten)) + 40, int(y_ - (hoehen[-1] * faktor - hoehen[-1]) ) + 20
    ef = d.get("effekt") or {}
    if isinstance(ef, str):                                            # alte Schreibweise: Name
        ef = {({"schatten": "schatten", "spiegelung": "reflektion", "leuchten": "leuchten"}.get(ef.lower(), ef.lower())): {}}
    spiegel = "reflektion" in ef
    img = QImage(b * _SS, (h * 2 if spiegel else h) * _SS, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing); p.scale(_SS, _SS)
    gesamt = QPainterPath()
    gruppen: dict[tuple, QPainterPath] = {}                           # nach Füllung und Kontur des Laufs
    hervor: list[tuple[str, QPainterPath]] = []
    linien: list[tuple] = []                                          # Unterstreichungen eigener Art/Farbe
    ausr = d.get("ausr", "links")
    for i, sg in enumerate(segmente):
        x = {"mitte": (max(breiten) - breiten[i]) / 2, "rechts": max(breiten) - breiten[i]}.get(ausr, 0) + einzug
        einzeln = len(sg) <= 1 or (len(sg) == 2 and bool(marken[i]))
        woerter = (sg[-1][0].split(" ") if sg else [])
        verteilen = ausr in ("block", "verteilt") and einzeln and len(woerter) > 1 and (ausr == "verteilt" or i < len(segmente) - 1)
        xx = 20 + x
        for t, e, f, fm in sg:
            y = ys[i] + (-fm.height() * 0.35 if e["hoch"] else fm.height() * 0.2 if e["tief"] else 0)
            teile = [t]
            if verteilen and t is sg[-1][0]:
                summe = sum(fm.horizontalAdvance(w_) for w_ in woerter)
                luecke = (max(breiten) - einzug - summe - (fm.horizontalAdvance(sg[0][0]) if marken[i] else 0)) / (len(woerter) - 1)
                teile = woerter
            pf = QPainterPath()
            x0 = xx
            for w_ in teile:
                pf.addText(xx, y, f, w_); xx += fm.horizontalAdvance(w_) + (luecke if verteilen and t is sg[-1][0] else 0)
            breite_t = xx - x0
            if e["unter"]:
                art_u = e["unter"] if isinstance(e["unter"], str) else "einfach"
                if art_u == "einfach" and not e["unterfarbe"]:
                    pf.addRect(x0, y + fm.underlinePos() + 1, breite_t, max(1.0, fm.lineWidth()))
                else:                                                # andere Linienart oder eigene Farbe: nach dem Text mit textfx gezeichnet
                    linien.append((x0, x0 + breite_t, y, art_u, e["unterfarbe"] or e["fuell"] or f1 or "#000000", f.pointSizeF() * 96 / 72))
            if e["durch"]:
                pf.addRect(x0, y - fm.strikeOutPos(), breite_t, max(1.0, fm.lineWidth()))
            if e["hervor"]:
                hp = QPainterPath(); hp.addRect(x0, y - fm.ascent(), breite_t, fm.height()); hervor.append((e["hervor"], hp))
            gesamt.addPath(pf)
            kl = e["kontur"] if e["kontur"] is not None else kontur
            fl = e["fuell"] if e["fuell"] is not None else None
            gruppen.setdefault((fl, kl or None), QPainterPath()).addPath(pf)
    if "leuchten" in ef:
        glut = QColor((ef["leuchten"] or {}).get("farbe") or f2 or kontur or "#4f93d1"); glut.setAlpha(60)
        for br in (14, 9, 5):
            pen = QPen(glut, br); pen.setJoinStyle(Qt.RoundJoin); p.setPen(pen); p.setBrush(Qt.NoBrush); p.drawPath(gesamt)
    if "schatten" in ef:
        schatten = (ef["schatten"] or {}).get("farbe") or schatten or "#6b6b6b"
    if schatten:
        dd = max(2.0, pt / 14)
        p.setPen(Qt.NoPen); p.setBrush(QColor(schatten)); p.translate(dd, dd); p.drawPath(gesamt); p.translate(-dd, -dd)
    for farbe_h, hp in hervor:                                        # Texthervorhebung: Hintergrund hinter dem Text
        p.setPen(Qt.NoPen); p.setBrush(QColor(farbe_h)); p.drawPath(hp)
    for (fl, kl), pf in gruppen.items():
        if fl is not None:
            brush = QBrush(QColor(fl)) if fl else QBrush(Qt.NoBrush)
        elif f1:
            g = QLinearGradient(0, 20, 0, h - 20); g.setColorAt(0, QColor(f1)); g.setColorAt(1, QColor(f2 or f1)); brush = QBrush(g)
        else:
            brush = QBrush(Qt.NoBrush)
        if kl:
            pen = QPen(QColor(kl)); pen.setWidthF((kb or 1.5 * 96 / 72 / max(1.0, pt / 36)) * max(1.0, pt / 36)); pen.setJoinStyle(Qt.RoundJoin); p.setPen(pen)
        else:
            p.setPen(Qt.NoPen)
        p.setBrush(brush); p.drawPath(pf)
    if linien:
        from lunivo_writer.editor.text.textfx import _unterstrich
        for x0_, x1_, y_u, art_u, farbe_u, px in linien:
            _unterstrich(p, [(x0_, x1_)], art_u, y_u, float(px), QColor(farbe_u))
    p.end()
    if spiegel:                                                      # Spiegelbild darunter, nach unten verblassend
        unten = img.copy(0, 0, b * _SS, h * _SS).mirrored(False, True)
        q = QPainter(unten); q.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        g = QLinearGradient(0, 0, 0, h * _SS); g.setColorAt(0, QColor(0, 0, 0, 110)); g.setColorAt(0.6, QColor(0, 0, 0, 0))
        q.fillRect(unten.rect(), g); q.end()
        q = QPainter(img); q.drawImage(0, h * _SS, unten); q.end()
    return richtung_anwenden(img, d.get("richtung"), [(int((ys[i] - asz[i]) * _SS), int(hoehen[i] * faktor * _SS)) for i in range(len(segmente))])


# ---- Textfeld zeichnen --------------------------------------------------------------------------------------------------
def _zeichenformat(d: dict, lauf: dict, vorlage, farbe_ueber: str | None = None):
    """Das Zeichenformat eines Laufs: seine eigenen Angaben, sonst die des Objekts."""
    from PySide6.QtGui import QTextCharFormat
    e = {k: lauf.get(k, d.get(k)) for k in ZEICHEN_SCHLUESSEL}
    cf = QTextCharFormat()
    cf.setFontWeight(QFont.Bold if e["fett"] else QFont.Normal)
    cf.setFontItalic(bool(e["kursiv"])); cf.setFontUnderline(bool(e["unter"])); cf.setFontStrikeOut(bool(e["durch"]))
    if isinstance(e["unter"], str) and e["unter"]:
        from lunivo_writer.editor.text.unterstreichung import unter_format
        cf.merge(unter_format(e["unter"]))
    if e["unterfarbe"] and e["unter"]:
        cf.setUnderlineColor(QColor(e["unterfarbe"]))
    if e["schrift"]:
        cf.setFontFamilies([e["schrift"]])
    if e["pt"]:
        cf.setFontPointSize(float(e["pt"]))
    if e["hoch"]:
        cf.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
    elif e["tief"]:
        cf.setVerticalAlignment(QTextCharFormat.AlignSubScript)
    if e["hervor"]:
        cf.setBackground(QColor(e["hervor"]))
    kontur = e["kontur"] if e["kontur"] is not None else (vorlage[3] if vorlage and "kontur" not in d else None)
    if kontur:
        cf.setTextOutline(QPen(QColor(kontur), float(d.get("kontur_breite", 0.75)) * 96 / 72))
    if farbe_ueber:
        cf.setForeground(QColor(farbe_ueber))
    elif "fuell" in lauf:
        cf.setForeground(QColor(lauf["fuell"]) if lauf["fuell"] else QColor(0, 0, 0, 0))
    return cf


def _textdoc(d: dict, laeufe: list[dict], b: float, h: float, farbe_ueber: str | None = None):
    """Das Textdokument eines Textfelds (Klartext mit Zeichenformaten) für die Läufe; → (Dokument, innere Breite, innere Höhe)."""
    from PySide6.QtGui import QTextBlockFormat
    doc = QTextDocument()
    f = QFont(d.get("schrift", "Liberation Sans")); f.setPointSizeF(float(d.get("pt", 11)))
    doc.setDefaultFont(f); doc.setDocumentMargin(0)
    o = QTextOption(); o.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
    o.setAlignment({"mitte": Qt.AlignHCenter, "rechts": Qt.AlignRight, "block": Qt.AlignJustify, "verteilt": Qt.AlignJustify}.get(d.get("ausr"), Qt.AlignLeft))
    doc.setDefaultTextOption(o)
    vorlage = None
    if d.get("vorlage") is not None:
        from lunivo_writer.editor.dokument import einfuegen as E
        vorlage = E.WORDART_VORLAGEN[int(d["vorlage"])]
    bf = QTextBlockFormat()
    bf.setLeftMargin(24.0 * int(d.get("einzug") or 0))
    if d.get("zeilenabstand"):
        bf.setLineHeight(float(d["zeilenabstand"]) * 100, QTextBlockFormat.ProportionalHeight.value)
    if d.get("ausr") == "verteilt":
        bf.setAlignment(Qt.AlignJustify)
    zeilen = _zeilen_laeufe(laeufe) or [[]]
    marken = listenmarken(d.get("liste"), len(zeilen))
    c = QTextCursor(doc)
    for i, (m_, zl) in enumerate(zip(marken, zeilen)):
        if i:
            c.insertBlock(bf)
        else:
            c.setBlockFormat(bf)
        if m_:
            c.insertText(m_, _zeichenformat(d, {}, vorlage, farbe_ueber))
        for r in zl:
            c.insertText(r["t"], _zeichenformat(d, r, vorlage, farbe_ueber))
    rand = 8.0
    doc.setTextWidth(max(10.0, b - 2 * rand))
    farbe = d.get("fuell") if d.get("fuell") else (vorlage[1] if vorlage and "fuell" not in d else d.get("farbe", "#1f1f1f"))
    doc.setProperty("farbe", farbe)
    return doc, b - 2 * rand, h - 2 * rand


def _text_passt(d: dict, laeufe: list[dict], b: float, h: float) -> int:
    """Wie viele Zeichen der Läufe im Feld ``b`` x ``h`` stehen (Anfang der ersten Zeile, die nicht mehr passt) — für verknüpfte Textfelder."""
    gesamt = laeufe_text(laeufe)
    doc, _bi, hi = _textdoc(d, laeufe, b, h)
    lay = doc.documentLayout()
    blk = doc.firstBlock()
    zeilen = len(_zeilen_laeufe(laeufe) or [[]])
    marken = listenmarken(d.get("liste"), zeilen)
    while blk.isValid():
        bl = blk.layout()
        r = lay.blockBoundingRect(blk)
        for i in range(bl.lineCount()):
            li = bl.lineAt(i)
            if r.top() + li.y() + li.height() > hi + 0.5:
                n = blk.blockNumber()
                versatz = sum(len(m_) for m_ in marken[: n + 1])
                return max(0, blk.position() + li.textStart() - versatz)
        blk = blk.next()
    return len(gesamt)


def textfeld_zeichnen(d: dict, b: float, h: float) -> QImage:
    """Nur der Text (durchsichtig); Füllung und Rand legt die Angabe des Bildes darum (so wirken Füllung und Kontur der Schnellleiste).
    Gezeichnet werden alle Schlüssel der Texttools: fett, kursiv, unter, durch, hoch, tief, hervor, fuell/farbe, kontur, effekt (schatten,
    reflektion, leuchten), vorlage, ausr (block, verteilt), liste, einzug, zeilenabstand, richtung. Bei verknüpften Feldern steht in ``gezeigt``
    der Teil des Textes, der in diesem Feld steht."""
    richt = d.get("richtung")
    if richt == "vertikal":
        richt = "senkrecht_rl"
    drehen = _gedreht(richt)
    if drehen:
        b, h = h, b
    img = QImage(max(1, int(b * _SS)), max(1, int(h * _SS)), QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    doc, bi, hi = _textdoc(d, anzeige_laeufe(d), b, h)
    farbe = doc.property("farbe")
    from PySide6.QtGui import QAbstractTextDocumentLayout
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.TextAntialiasing); p.scale(_SS, _SS)
    p.translate(8, 8); p.setClipRect(QRectF(0, 0, bi, hi))
    ef = d.get("effekt") or {}
    if "schatten" in ef:
        sf = (ef["schatten"] or {}).get("farbe") or "#8a8a8a"
        sdoc, _a, _b = _textdoc(d, anzeige_laeufe(d), b, h, sf)
        ctx = QAbstractTextDocumentLayout.PaintContext()
        ctx.palette.setColor(ctx.palette.ColorRole.Text, QColor(sf))
        p.save(); p.translate(2, 2); sdoc.documentLayout().draw(p, ctx); p.restore()
    ctx = QAbstractTextDocumentLayout.PaintContext()
    ctx.palette.setColor(ctx.palette.ColorRole.Text, QColor(farbe))
    doc.documentLayout().draw(p, ctx)
    p.end()
    if "leuchten" in ef or "reflektion" in ef:
        img = effekte_auf_text(img, {k: v for k, v in ef.items() if k in ("leuchten", "reflektion")}, 8 + doc.size().height(), farbe)
    bander = None
    if richt == "senkrecht_lr":
        bander = []
        blk = doc.firstBlock(); lay = doc.documentLayout()
        while blk.isValid():
            bl = blk.layout(); r = lay.blockBoundingRect(blk)
            for i in range(bl.lineCount()):
                li = bl.lineAt(i); bander.append((int((8 + r.top() + li.y()) * _SS), int(li.height() * _SS)))
            blk = blk.next()
        # Rand oben/unten als eigene Bänder, damit nichts verloren geht
        if bander:
            rest = [(0, bander[0][0])] if bander[0][0] > 0 else []
            bander = rest + bander
            letzte = bander[-1][0] + bander[-1][1]
            if letzte < img.height():
                bander.append((letzte, img.height() - letzte))
    return richtung_anwenden(img, richt, bander)


