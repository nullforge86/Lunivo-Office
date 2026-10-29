"""Freie Objekte mit Parametern (WordArt, Textfeld): EIN gemeinsamer Baustein.

Ein solches Objekt ist ein frei positioniertes Bild (siehe ``freie_bilder``): Auswahlrahmen, acht Griffe, Drehgriff, Verschieben und die
Schnellleiste daneben (Layout, Formstil, Füllung, Kontur) kommen aus ``ui/document/freie_bilder_bedienung.py``. Dieser Baustein ergänzt nur,
was die beiden Arten unterscheidet: ihre Parameter (``art`` und ``daten`` an der Angabe des Bildes) und das Zeichnen daraus.
Neue Art = ein Eintrag in ``ZEICHNER``. Kein HTML: gezeichnet wird mit QPainter und QTextDocument (Klartext).
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, QUrl, Qt
from PySide6.QtGui import (QBrush, QColor, QFont, QFontMetricsF, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QTextCursor,
                           QTextDocument, QTextOption)

from lunivo_writer.editor import freie_bilder as FB
from lunivo_writer.editor.mehrstufig import nummer_text

ARTEN = ("wordart", "textfeld", "form")
FORM_STANDARD = {"form": "Rechteck", "fuell": {"art": "farbe", "farbe": "#4a8fd8"}, "rand": {"b": 2.0, "farbe": "#1f3864", "art": "einfach"}, "text": ""}
FORM_MASS = (95, 95)                                                 # Standardgröße wie in WPS: etwa 2,5 cm
ZEICHENBEREICH_DATEN = {"form": "Rechteck", "fuell": None, "rand": {"b": 1.0, "farbe": "#adb5bd", "art": "gestrichelt"}, "text": "", "kinder": []}
ZB_VERSATZ = 24                                                      # jede neue Form im Zeichenbereich etwas rechts unterhalb der vorigen
TEXTFELD_STANDARD = {"text": "", "schrift": "Liberation Sans", "pt": 11, "farbe": "#1f1f1f"}
TEXTFELD_FUELL = {"art": "farbe", "farbe": "#ffffff"}
TEXTFELD_RAND = {"b": 1.5, "farbe": "#1f3864", "art": "einfach"}
WORDART_STANDARD = {"text": "Hier Text einfügen", "vorlage": 0, "pt": 36, "schrift": "Liberation Sans"}
_SS = 2                                                              # Zeichnen in doppelter Auflösung (scharf auch bei Zoom)


# ---- Gemeinsame Hilfen: Listenmarken, Textrichtung, Effekte ---------------------------------------------------------------
RICHTUNGEN = ("waagerecht", "senkrecht_rl", "senkrecht_lr", "dreh90", "dreh270", "asiatisch270")
_PUNKTE = {"disc": "\u25cf", "circle": "\u25cb", "square": "\u25a0"}


def listenmarken(liste, anzahl: int) -> list[str]:
    """Die Marke jeder Zeile (mit Leerzeichen dahinter): Aufzählungszeichen oder Nummer nach dem Listenwert aus ``editor/listen.py``
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
    from lunivo_writer.editor import einfuegen as E
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
        from lunivo_writer.editor.textfx import _unterstrich
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
        from lunivo_writer.ui.baukasten.text_format import unter_format
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
        from lunivo_writer.editor import einfuegen as E
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


def form_stil(d: dict) -> tuple[dict | None, dict | None]:
    """(Füllung, Kontur) einer Form als Wörterbücher wie bei den anderen freien Objekten (siehe ``freie_bilder.fuell_pinsel``/``_stift``)."""
    f = d.get("fuell")
    return ({"art": "farbe", "farbe": f} if isinstance(f, str) and f else (f or None)), (d.get("rand") or None)


def form_zeichnen(d: dict, b: float, h: float) -> QImage:
    """Die Form (Galerie ``editor/formen_katalog.py``) in b × h Bildpunkten mit Füllung (Farbe, Verlauf, Muster, Textur), Kontur samt Strichart und
    Text; ein Zeichenbereich (``kinder``) zeichnet seine Formen hinein."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPainter
    from lunivo_writer.editor import formen_katalog as K
    b, h = max(2, int(round(b))), max(2, int(round(h)))
    img = QImage(b, h, QImage.Format_ARGB32_Premultiplied); img.fill(0)
    fuell, rand = form_stil(d)
    name = d.get("form", "Rechteck")
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
    m = (float(rand.get("b", 1.0)) if rand else 0.0) / 2 + 1
    r = QRectF(m, m, b - 2 * m, h - 2 * m)
    if K.hat(name):
        pen = FB._stift(rand) if rand else Qt.NoPen
        pen.setJoinStyle(Qt.RoundJoin) if rand else None
        p.setPen(pen)
        pinsel = None if K.ist_linie(name) else FB.fuell_pinsel(fuell, r)
        p.setBrush(pinsel if pinsel is not None else Qt.NoBrush)
        p.drawPath(K.pfad(name, r))
    else:                                                            # ältere Namen (Textfeld, Sprechblase …): wie bisher
        p.end()
        from lunivo_writer.editor import einfuegen as E
        img = E.form_bild(name, b, h, (fuell or {}).get("farbe", ""), (rand or {}).get("farbe", "#00000000"), float((rand or {}).get("b", 2.0)), "")
        p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
    for k in d.get("kinder", []):
        kd = {x: y for x, y in k.items() if x not in ("x", "y", "breite", "hoehe")}
        p.drawImage(int(k["x"]), int(k["y"]), form_zeichnen(kd, k["breite"], k["hoehe"]))
    if d.get("text"):
        hell = fuell and fuell.get("art", "farbe") == "farbe" and QColor(fuell["farbe"]).lightness() < 140
        p.setPen(QColor("#ffffff" if hell else "#000000")); f = p.font(); f.setPointSizeF(12); p.setFont(f)
        p.drawText(r, Qt.AlignCenter | Qt.TextWordWrap, d["text"])
    p.end()
    return img


def zeichnen(art: str, d: dict, b: float = 0, h: float = 0) -> QImage:
    if art == "form":
        return form_zeichnen(d, b, h)
    return wordart_zeichnen(d) if art == "wordart" else textfeld_zeichnen(d, b, h)


def _anzeige_mass(art: str, img: QImage, b: float, h: float) -> tuple[float, float]:
    """Größe auf dem Blatt in Bildpunkten: WordArt aus dem Bild (ohne Überbreite), Textfeld wie vorgegeben."""
    return (img.width() / _SS, img.height() / _SS) if art == "wordart" else (b, h)


def form_einfuegen(ed, name: str, b: float = 0, h: float = 0, **daten) -> tuple | None:
    """Einfügen ▸ Formen: ist ein Zeichenbereich ausgewählt, kommt die Form hinein; sonst als freies Objekt in Standardgröße (wie ein Klick in WPS),
    ausgewählt, mit Griffen."""
    if not (b or h or daten) and in_zeichenbereich(ed, name):
        return ed._frei_sel
    return einfuegen(ed, "form", dict(FORM_STANDARD, form=name, **daten), b or FORM_MASS[0], h or FORM_MASS[1])


def zeichenbereich_einfuegen(ed) -> tuple | None:
    """Einfügen ▸ Formen ▸ Neuer Zeichenbereich: freies Objekt (15 × 8 cm) ohne Füllung mit gestricheltem grauem Rand, das Formen aufnimmt."""
    from lunivo_writer.editor import formen as F
    return einfuegen(ed, "form", {**ZEICHENBEREICH_DATEN, "kinder": []}, min(F.ZEICHENBEREICH[0], ed.page.content_width_px), F.ZEICHENBEREICH[1])


def ist_zeichenbereich(ed) -> bool:
    d = daten_lesen(ed, "form")
    return d is not None and "kinder" in d


def in_zeichenbereich(ed, name: str) -> bool:
    """Form in den ausgewählten Zeichenbereich setzen (sie bewegt sich mit ihm); False, wenn keiner ausgewählt ist."""
    from lunivo_writer.editor import formen_katalog as K
    z = ziel(ed)
    if z is None or z[0] != "form" or "kinder" not in z[1]:
        return False
    d, a = z[1], z[3]
    kinder = list(d["kinder"]); n = len(kinder)
    kb, kh = (min(FORM_MASS[0], a["b"] - 16), min(FORM_MASS[1], a["h"] - 16))
    x = 8 + (n * ZB_VERSATZ) % max(1, int(a["b"] - kb - 16)); y = 8 + (n * ZB_VERSATZ) % max(1, int(a["h"] - kh - 16))
    kinder.append(dict(FORM_STANDARD, form=name, x=x, y=y, breite=kb, hoehe=kh))
    return _aendern_innen(ed, "form", kinder=kinder)


# ---- Einfügen -----------------------------------------------------------------------------------------------------------
def einfuegen(ed, art: str, daten: dict, b: float = 0, h: float = 0) -> tuple | None:
    """Fügt das Objekt als freies Bild am Absatz der Schreibmarke ein (steht dort Text, in einem neuen Absatz darunter), wählt es aus —
    mit Rahmen, Griffen und Schnellleiste — und lässt keine Textmarkierung zurück. → Schlüssel des Objekts."""
    doc = ed.document()
    img = zeichnen(art, daten, b, h)
    bb, hh = _anzeige_mass(art, img, b, h)
    maxw = ed.page.content_width_px
    if bb > maxw:
        hh, bb = hh * maxw / bb, maxw
    c = ed.textCursor(); c.clearSelection()
    c.beginEditBlock()
    if c.block().text().strip() or c.block().length() > 1:
        from PySide6.QtGui import QTextBlockFormat
        c.movePosition(QTextCursor.EndOfBlock); c.insertBlock(QTextBlockFormat())
    name = FB.neuer_name(doc)
    doc.addResource(QTextDocument.ImageResource, QUrl(name), img)
    a = {"n": name, "b": bb, "h": hh, "bh": "spalte", "xh": 0.0, "bv": "absatz", "yv": 0.0, "ah": "", "av": "", "hinter": False,
         "ellipse": False, "dreh": 0.0, "art": art, "daten": dict(daten)}
    if art == "textfeld":
        a["fuell"], a["rand"] = dict(TEXTFELD_FUELL), dict(TEXTFELD_RAND)
    FB.an_absatz(QTextCursor(c.block()), a)
    blk, idx = c.block().blockNumber(), len(FB.aus_absatz(c.block().blockFormat())) - 1
    c.endEditBlock()
    ed.setTextCursor(c)
    doc.setModified(True)
    ed._frei_rev = None
    ed._frei_liste()                                                 # legt beim ersten Mal die Zustände an (setzt die Auswahl zurück)
    ed._frei_sel = ("t", blk, idx)
    ed.viewport().update()
    if hasattr(ed.window(), "_sync_format"):
        ed.window()._sync_format()
    if art == "textfeld":                                            # wie in WPS: die Schreibmarke steht gleich im leeren Textfeld
        bearbeiten_starten(ed)
    return ed._frei_sel


# ---- Lesen und Ändern ---------------------------------------------------------------------------------------------------------
def ziel(ed):
    """(Art, Daten, Schlüssel, Angabe, Bild) des gewählten Objekts oder None."""
    sel = getattr(ed, "_frei_sel", None)
    if sel is None:
        return None
    for key, a, bild, _r, _h, _n in ed._frei_liste():
        if key == sel:
            return (a["art"], dict(a.get("daten", {})), key, a, bild) if a.get("art") in ARTEN else None
    return None


def art_gewaehlt(ed) -> str | None:
    z = ziel(ed)
    return z[0] if z else None


def daten_lesen(ed, art: str) -> dict | None:
    z = ziel(ed)
    return z[1] if z and z[0] == art else None


def aendern(ed, art: str, **kw) -> bool:
    """Parameter des gewählten Objekts ändern (siehe ``_aendern_innen``). Schreibt der Benutzer gerade im Objekt und hat Text markiert, gelten
    Zeichenformate (``ZEICHEN_SCHLUESSEL``) nur für die Markierung; sonst für das ganze Objekt."""
    w = getattr(ed, "_frei_edit", None)
    if w is not None and kw and set(kw) <= set(ZEICHEN_SCHLUESSEL) and w.textCursor().hasSelection() and art_gewaehlt(ed) == art:
        w.textCursor().mergeCharFormat(_format_aus_kw(kw))
        edit_uebernehmen(ed)
        return True
    edit_uebernehmen(ed)                                             # zuerst den eben getippten Text sichern
    ok = _aendern_innen(ed, art, **kw)
    if ok and getattr(ed, "_frei_edit", None) is not None:
        _edit_laden(ed); _edit_stil(ed); edit_platzieren(ed)
    return ok


def _aendern_innen(ed, art: str, **kw) -> bool:
    """Parameter des gewählten Objekts ändern und neu zeichnen. ``breite``/``hoehe`` (px) ändern die Größe; ``form_fuell`` (Farbe oder ``""``)
    und ``form_linie`` (Farbe oder ``""``) die Füllung und den Rand des Objekts; alle anderen Schlüssel gehören zu ``daten``."""
    from lunivo_writer.editor import bildlayout as BL
    z = ziel(ed)
    if z is None or z[0] != art:
        return False
    _art, d, key, a, bild = z
    if art == "form":
        return _form_aendern(ed, d, key, a, kw)
    neu = dict(a)
    b, h = float(a["b"]), float(a["h"])
    if kw.get("vorlage") is not None:                                # eine Vorlage setzt Füllung, Kontur und Effekt neu
        for k in ("fuell", "kontur", "kontur_breite", "effekt"):
            if k not in kw:
                d.pop(k, None)
    if "text" in kw and "laeufe" not in kw:                          # neuer Text ohne Formate (Dialog, Vorlage): die Läufe gelten nicht mehr
        d.pop("laeufe", None)
    for k in kw:                                                     # ein Zeichenformat für das ganze Objekt löscht gleiche Angaben der Läufe
        if k in ZEICHEN_SCHLUESSEL and d.get("laeufe"):
            d["laeufe"] = laeufe_zusammen([{x: y for x, y in r.items() if x != k} for r in d["laeufe"]])
            if all(len(r) == 1 for r in d["laeufe"]):
                d.pop("laeufe")
    for k, v in kw.items():
        if k == "laeufe":
            if v:
                d["laeufe"] = v
            else:
                d.pop("laeufe", None)
        elif k == "breite":
            b = float(v)
        elif k == "hoehe":
            h = float(v)
        elif k == "form_fuell":
            neu["fuell"] = {"art": "farbe", "farbe": v} if v else None
        elif k == "form_strich":
            neu["rand"] = {**(a.get("rand") or TEXTFELD_RAND), "b": float(v) * 96 / 72}
        elif k == "form_effekt":
            if v:
                neu["fx"] = v
            else:
                neu.pop("fx", None)
        elif k == "form_linie":
            neu["rand"] = {**(a.get("rand") or TEXTFELD_RAND), "farbe": v} if v else None
        elif v is None:
            d.pop(k, None)
        else:
            d[k] = v
    if set(kw) - {"form_fuell", "form_linie", "form_strich", "form_effekt"}:
        if art == "wordart":                                         # die Größe folgt dem Bild: gleicher Maßstab wie vorher
            faktor = a["b"] / max(1.0, bild.width() / _SS)
            img = wordart_zeichnen(d)
            b, h = img.width() / _SS * faktor, img.height() / _SS * faktor
        else:
            img = textfeld_zeichnen(d, b, h)
        n = FB.neuer_name(ed.document())
        ed.document().addResource(QTextDocument.ImageResource, QUrl(n), img)
        neu["n"], neu["b"], neu["h"], neu["daten"] = n, b, h, d
    BL._speichern_frei(ed, key, neu)
    if art == "textfeld":
        kette_aktualisieren(ed)
    return True


def _form_neu_zeichnen(ed, neu: dict, d: dict) -> dict:
    n = FB.neuer_name(ed.document())
    ed.document().addResource(QTextDocument.ImageResource, QUrl(n), form_zeichnen(d, neu["b"], neu["h"]))
    neu["n"], neu["daten"] = n, d
    return neu


def _form_aendern(ed, d: dict, key, a: dict, kw: dict) -> bool:
    """Form ändern: ``form`` (Art der Form), ``text``, ``fuell``, ``rand``, ``kinder`` gehören zu ``daten``; ``form_fuell``/``form_linie`` (Farbe),
    ``form_strich`` (pt)/``form_effekt`` wie bei den anderen freien Objekten; ``breite``/``hoehe`` ändern die Größe."""
    from lunivo_writer.editor import bildlayout as BL
    neu = dict(a)
    for k, v in kw.items():
        if k == "breite":
            neu["b"] = float(v)
        elif k == "hoehe":
            neu["h"] = float(v)
        elif k == "form_fuell":
            d["fuell"] = {"art": "farbe", "farbe": v} if v else None
        elif k == "form_linie":
            d["rand"] = {**(form_stil(d)[1] or FORM_STANDARD["rand"]), "farbe": v} if v else None
        elif k == "form_strich":
            d["rand"] = {**(form_stil(d)[1] or FORM_STANDARD["rand"]), "b": float(v) * 96 / 72}
        elif k == "form_effekt":
            if v:
                neu["fx"] = v
            else:
                neu.pop("fx", None)
        elif v is not None:
            d[k] = v
    BL._speichern_frei(ed, key, _form_neu_zeichnen(ed, neu, d))
    return True


def form_format_uebernehmen(neu: dict, ed) -> dict:
    """Füllung und Kontur aus den allgemeinen Menüs (``bildlayout.format_setzen``): bei einer Form gehören sie in ``daten`` (die Form wird mit Verlauf,
    Muster, Textur und Strichart neu gezeichnet), nicht als Rechteck hinter das Bild."""
    d = dict(neu.get("daten", {}))
    if "fuell" in neu:
        d["fuell"] = neu.pop("fuell")
    if "rand" in neu:
        d["rand"] = neu.pop("rand")
    return _form_neu_zeichnen(ed, neu, d)


def form_format_lesen(a: dict) -> tuple[dict | None, dict | None]:
    return form_stil(a.get("daten", {}))


def nach_groesse(ed, neu: dict) -> dict:
    """Nach dem Ziehen der Griffe: eine Form wird in der neuen Größe frisch gezeichnet, ein Textfeld in der neuen Größe frisch gesetzt (Zeilenumbruch folgt der Breite)."""
    if neu.get("art") == "textfeld" and neu.get("n"):
        n = FB.neuer_name(ed.document())
        ed.document().addResource(QTextDocument.ImageResource, QUrl(n), textfeld_zeichnen(neu.get("daten", {}), neu["b"], neu["h"]))
        neu = dict(neu, n=n)
    elif neu.get("art") == "form" and neu.get("n"):
        neu = _form_neu_zeichnen(ed, dict(neu), dict(neu.get("daten", {})))
    return neu


def text_bereich(a: dict, bild: QImage) -> QRectF | None:
    """Wo der Text im Objekt liegt, als Anteil (0..1) von Breite/Höhe — für die graue Textmarkierung wie in WPS (nur WordArt)."""
    if a.get("art") != "wordart" or bild is None or bild.isNull():
        return None
    w, h = bild.width() / _SS, bild.height() / _SS
    if "reflektion" in (a.get("daten", {}).get("effekt") or {}):
        h /= 2
        return QRectF(20 / w, 20 / (h * 2), (w - 40) / w, (h - 40) / (h * 2))
    return QRectF(20 / w, 20 / h, (w - 40) / w, (h - 40) / h)


# ---- Schreiben im Objekt ---------------------------------------------------------------------------------------------------
def _format_aus_kw(kw: dict):
    """Zeichenformat für das Eingabefeld aus Schlüsseln der Texttools (nur die genannten)."""
    from PySide6.QtGui import QTextCharFormat
    cf = QTextCharFormat()
    for k, v in kw.items():
        if k == "fett":
            cf.setFontWeight(QFont.Bold if v else QFont.Normal)
        elif k == "kursiv":
            cf.setFontItalic(bool(v))
        elif k == "unter":
            cf.setFontUnderline(bool(v))
            if isinstance(v, str) and v:
                from lunivo_writer.ui.baukasten.text_format import unter_format
                cf.merge(unter_format(v))
        elif k == "unterfarbe":
            cf.setUnderlineColor(QColor(v) if v else QColor())
        elif k == "durch":
            cf.setFontStrikeOut(bool(v))
        elif k == "hoch" or k == "tief":
            cf.setVerticalAlignment(QTextCharFormat.AlignSuperScript if k == "hoch" and v else QTextCharFormat.AlignSubScript if k == "tief" and v
                                    else QTextCharFormat.AlignNormal)
        elif k == "hervor":
            cf.setBackground(QColor(v) if v else QColor(0, 0, 0, 0))
        elif k == "fuell":
            cf.setForeground(QColor(v) if v else QColor(0, 0, 0, 0))
        elif k == "kontur":
            cf.setTextOutline(QPen(QColor(v), 1.0) if v else QPen(Qt.NoPen))
        elif k == "schrift" and v:
            cf.setFontFamilies([v])
        elif k == "pt" and v:
            cf.setFontPointSize(float(v))
    return cf


def _lauf_aus_format(cf, basis: dict) -> dict:
    """Die Zeichenschlüssel, die ein Format ausdrücklich setzt und die vom Objekt abweichen."""
    from PySide6.QtGui import QTextFormat
    lauf: dict = {}

    def setze(k, wert):
        if wert != basis.get(k):
            lauf[k] = wert
    if cf.hasProperty(QTextFormat.FontWeight):
        setze("fett", cf.fontWeight() >= QFont.DemiBold)
    if cf.hasProperty(QTextFormat.FontItalic):
        setze("kursiv", cf.fontItalic())
    if cf.hasProperty(QTextFormat.TextUnderlineStyle) or cf.hasProperty(QTextFormat.FontUnderline):
        setze("unter", cf.fontUnderline())
    if cf.hasProperty(QTextFormat.FontStrikeOut):
        setze("durch", cf.fontStrikeOut())
    if cf.hasProperty(QTextFormat.TextVerticalAlignment):
        va = cf.verticalAlignment()
        setze("hoch", va == QTextCharFormat.AlignSuperScript); setze("tief", va == QTextCharFormat.AlignSubScript)
    if cf.hasProperty(QTextFormat.BackgroundBrush):
        c = cf.background().color(); setze("hervor", c.name() if c.alpha() else "")
    if cf.hasProperty(QTextFormat.ForegroundBrush):
        c = cf.foreground().color(); setze("fuell", (c.name(QColor.HexArgb) if c.alpha() < 255 else c.name()) if c.alpha() else "")
    if cf.hasProperty(QTextFormat.TextOutline):
        pen = cf.textOutline(); setze("kontur", pen.color().name() if pen.style() != Qt.NoPen else "")
    if cf.hasProperty(QTextFormat.FontFamilies) and cf.fontFamilies():
        setze("schrift", cf.fontFamilies()[0])
    if cf.hasProperty(QTextFormat.FontPointSize):
        setze("pt", cf.fontPointSize())
    return {k: v for k, v in lauf.items() if not (v in (False, "", None) and basis.get(k) in (None, False, ""))}


def _basis(d: dict, art: str) -> dict:
    return {k: d.get(k, True if (k == "fett" and art == "wordart") else None) for k in ZEICHEN_SCHLUESSEL}


def _widget_laeufe(w, d: dict, art: str) -> list[dict] | None:
    """Die Läufe aus dem Eingabefeld; ``None``, wenn der ganze Text ohne eigene Formate ist."""
    basis = _basis(d, art)
    laeufe: list[dict] = []
    blk = w.document().firstBlock(); erste = True
    while blk.isValid():
        if not erste:
            laeufe.append({"t": "\n"})
        erste = False
        it = blk.begin()
        while not it.atEnd():
            fr = it.fragment()
            if fr.isValid() and fr.text():
                laeufe.append({"t": fr.text(), **_lauf_aus_format(fr.charFormat(), basis)})
            it += 1
        blk = blk.next()
    laeufe = laeufe_zusammen(laeufe)
    if all(len(r) == 1 for r in laeufe):
        return None
    return laeufe


def _edit_laden(ed) -> None:
    """Das Eingabefeld mit den Läufen des Objekts füllen (Auswahl bleibt erhalten)."""
    w = getattr(ed, "_frei_edit", None)
    z = ziel(ed)
    if w is None or z is None:
        return
    art, d, _k, _a, _b = z
    c0 = w.textCursor(); pos, anker = c0.position(), c0.anchor()
    w.blockSignals(True)
    w.clear()
    c = w.textCursor()
    from PySide6.QtGui import QTextCharFormat
    for r in (d.get("laeufe") or [{"t": d.get("text", "")}]):
        c.insertText(r["t"], _format_aus_kw({k: v for k, v in r.items() if k in ZEICHEN_SCHLUESSEL}))
    w.blockSignals(False)
    c = w.textCursor(); n = len(w.toPlainText())
    c.setPosition(min(anker, n)); c.setPosition(min(pos, n), QTextCursor.KeepAnchor); w.setTextCursor(c)


def _edit_stil(ed) -> None:
    """Schrift, Farbe und Ausrichtung des Eingabefeldes folgen den Parametern des Objekts (auch nach einem Knopf der Texttools)."""
    w = getattr(ed, "_frei_edit", None)
    z = ziel(ed)
    if w is None or z is None:
        return
    art, d, _key, a, _bild = z
    z_ = ed.zoom
    f = QFont(d.get("schrift", "Liberation Sans")); f.setPixelSize(max(6, round(float(d.get("pt", 36 if art == "wordart" else 11)) * 96 / 72 * z_)))
    f.setBold(bool(d.get("fett", art == "wordart"))); f.setItalic(bool(d.get("kursiv"))); f.setUnderline(bool(d.get("unter"))); f.setStrikeOut(bool(d.get("durch")))
    w.setFont(f); w.document().setDefaultFont(f)
    farbe = d.get("fuell") or d.get("farbe") or ("#2f78bd" if art == "wordart" else "#1f1f1f")
    grund = "transparent"
    fu = a.get("fuell")
    if art == "textfeld" and fu and fu.get("art") == "farbe":
        grund = fu["farbe"]
    w.setStyleSheet(f"QTextEdit {{ background: {grund}; color: {farbe}; border: none; selection-background-color: #8a9ab0; }}")


def edit_platzieren(ed) -> None:
    """Das Eingabefeld deckt das Objekt (folgt dem Blatt beim Scrollen und Zoomen)."""
    w = getattr(ed, "_frei_edit", None)
    if w is None:
        return
    for key, _a, r, _h, _n in ed._frei_treffer:
        if key == ed._frei_edit_key:
            rand = int((8 if ed._frei_edit_art == "textfeld" else 20) * ed.zoom)
            w.setGeometry(r.toRect().adjusted(rand, rand, -rand, -rand))
            return


def bearbeiten_starten(ed) -> bool:
    """Schreibt direkt im gewählten Objekt (WordArt oder Textfeld): ein Eingabefeld über dem Text. Eingabe, Markieren, Rückschritt und Enter
    (neue Zeile) wirken wie im Text; Esc oder ein Klick außerhalb beendet und übernimmt. Die Knöpfe der Texttools wirken auf die Markierung,
    ohne Markierung auf das ganze Objekt (``aendern``)."""
    from PySide6.QtWidgets import QTextEdit
    z = ziel(ed)
    if z is None:
        return False
    bearbeiten_beenden(ed)
    art, d, key, _a, _b = z
    if d.get("von"):                                                 # Folgefeld einer Verknüpfung: der Text gehört dem ersten Feld
        return False

    class Feld(QTextEdit):
        def keyPressEvent(self, e):
            if e.key() == Qt.Key_Escape:
                bearbeiten_beenden(ed); return
            super().keyPressEvent(e)

        def focusOutEvent(self, e):
            super().focusOutEvent(e)
            if getattr(ed, "_frei_edit", None) is self and e.reason() not in (Qt.PopupFocusReason, Qt.ActiveWindowFocusReason):
                bearbeiten_beenden(ed)

        def insertFromMimeData(self, quelle):                        # Einfügen: nur Text
            self.insertPlainText(quelle.text())

    w = Feld(ed.viewport())
    w.setFrameShape(Feld.NoFrame); w.setAcceptRichText(False)
    w.setLineWrapMode(Feld.WidgetWidth if art == "textfeld" else Feld.NoWrap)
    w.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff); w.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    ed._frei_edit, ed._frei_edit_key, ed._frei_edit_art = w, key, art
    _edit_laden(ed)
    ed._frei_edit_text, ed._frei_edit_laeufe = w.toPlainText(), _widget_laeufe(w, d, art)
    _edit_stil(ed)
    ed._frei_liste(); edit_platzieren(ed)
    w.show(); w.setFocus()
    c = w.textCursor(); c.select(QTextCursor.Document) if art == "wordart" else c.movePosition(QTextCursor.End); w.setTextCursor(c)
    ed.viewport().update()
    return True


def auswahl_daten(ed) -> dict | None:
    """Die Zeichenformate der Markierung (oder der Schreibmarke) im Eingabefeld — wirksame Werte, auch die des Objekts. Für den Zustand der
    Knöpfe der Texttools; ``None``, wenn nicht im Objekt geschrieben wird."""
    w = getattr(ed, "_frei_edit", None)
    z = ziel(ed)
    if w is None or z is None:
        return None
    art, d, _k, _a, _b = z
    basis = _basis(d, art)
    c = w.textCursor()
    if c.hasSelection():
        c = QTextCursor(w.document()); c.setPosition(w.textCursor().selectionStart() + 1)
    return {**basis, **_lauf_aus_format(c.charFormat(), basis)}


def edit_uebernehmen(ed) -> None:
    """Der eingegebene Text mit seinen Formaten kommt ins Objekt (ohne das Feld zu schließen)."""
    w = getattr(ed, "_frei_edit", None)
    z = ziel(ed)
    if w is None or z is None:
        return
    art, d, _k, _a, _b = z
    text, laeufe = w.toPlainText(), _widget_laeufe(w, d, art)
    if text != ed._frei_edit_text or laeufe != ed._frei_edit_laeufe:
        ed._frei_edit_text, ed._frei_edit_laeufe = text, laeufe
        kw = {"text": text if art == "textfeld" else (text or " "), "laeufe": laeufe}
        _aendern_innen(ed, art, **kw)


def bearbeiten_beenden(ed) -> None:
    w = getattr(ed, "_frei_edit", None)
    if w is None:
        return
    edit_uebernehmen(ed)
    ed._frei_edit = None
    w.hide(); w.deleteLater()
    ed.viewport().update(); ed.setFocus()


# ---- Textoptionen der Seitenleiste „Formatierung“ -----------------------------------------------------------------------------
def text_werte_lesen(ed) -> dict | None:
    """Die Textoptionen (Format von ``texteffekt.py``) des gewählten Objekts."""
    z = ziel(ed)
    if z is None:
        return None
    d = z[1]
    w = {"fuell": "farbe", "farbe": d.get("fuell") or d.get("farbe") or "", "transparenz": 0, "kontur": bool(d.get("kontur")),
         "kontur_farbe": d.get("kontur") or "#000000", "kontur_breite": float(d.get("kontur_breite", 0.75)), "kontur_art": "einfach"}
    if "fuell" in d and not d["fuell"]:
        w["fuell"] = "keine"
    return w


def text_werte_anwenden(ed, werte: dict) -> bool:
    """Die Textoptionen der Seitenleiste wirken auf den Text im gewählten Objekt: Füllung (Farbe, Transparenz), Kontur (Farbe, Breite)."""
    art = art_gewaehlt(ed)
    if art is None:
        return False
    kw: dict = {}
    if werte.get("fuell") == "keine":
        kw["fuell"] = ""
    elif werte.get("farbe") or werte.get("transparenz"):
        c = QColor(werte.get("farbe") or "#000000"); c.setAlphaF(1.0 - float(werte.get("transparenz", 0)) / 100)
        kw["fuell"] = c.name(QColor.HexArgb) if c.alpha() < 255 else c.name()
    if werte.get("kontur"):
        kw["kontur"] = werte.get("kontur_farbe", "#000000"); kw["kontur_breite"] = float(werte.get("kontur_breite", 0.75))
    elif "kontur" in werte:
        kw["kontur"] = ""
    return aendern(ed, art, **kw) if kw else False


# ---- Verknüpfte Textfelder -----------------------------------------------------------------------------------------------------
def _textfelder(ed) -> list[tuple[tuple, dict]]:
    """Alle Textfelder des Textes: (Schlüssel, Angabe) — frisch aus den Absätzen gelesen."""
    out = []
    b = ed.document().firstBlock()
    while b.isValid():
        for i, a in enumerate(FB.aus_absatz(b.blockFormat())):
            if a.get("art") == "textfeld":
                out.append((("t", b.blockNumber(), i), a))
        b = b.next()
    return out


def _speichern_angabe(ed, key: tuple, a: dict) -> None:
    ed._frei_absatz_aendern(key[1], key[2], a)


def _neu_setzen(ed, key: tuple, a: dict) -> dict:
    """Das Bild des Textfelds aus seinen Daten neu zeichnen und die Angabe sichern."""
    n = FB.neuer_name(ed.document())
    ed.document().addResource(QTextDocument.ImageResource, QUrl(n), textfeld_zeichnen(a.get("daten", {}), a["b"], a["h"]))
    a = dict(a, n=n)
    _speichern_angabe(ed, key, a)
    return a


def verknuepfen(ed, von_key: tuple, nach_key: tuple) -> bool:
    """Textfeld ``von`` mit Textfeld ``nach`` verknüpfen: was in ``von`` nicht mehr passt, läuft in ``nach`` weiter (wie „Verknüpfung erstellen“ in
    WPS). Der Text von ``nach`` wird an den von ``von`` gehängt. Nicht möglich: gleiche Felder, ``von`` hat schon einen Nachfolger, ``nach`` einen
    Vorgänger, Kreisverknüpfung. → True bei Erfolg."""
    import uuid
    felder = dict(_textfelder(ed))
    if von_key == nach_key or von_key not in felder or nach_key not in felder:
        return False
    a, b = felder[von_key], felder[nach_key]
    da, db = dict(a.get("daten", {})), dict(b.get("daten", {}))
    if da.get("weiter") or db.get("von"):
        return False
    if da.get("von") and da["von"] == db.get("id"):                 # b ist der Vorgänger von a: Kreis
        return False
    da.setdefault("id", uuid.uuid4().hex[:8]); db.setdefault("id", uuid.uuid4().hex[:8])
    kopf = da
    while kopf.get("von"):                                           # a mitten in einer Kette: nach oben bis zum Kopf, Kreis ausschließen
        nxt = next((x["daten"] for _k, x in felder.items() if x.get("daten", {}).get("id") == kopf["von"]), None)
        if nxt is None or nxt.get("id") == db["id"]:
            return False
        kopf = nxt
    if db.get("text"):
        if da.get("laeufe") or db.get("laeufe"):
            la = da.get("laeufe") or [{"t": da.get("text", "")}]; lb = db.get("laeufe") or [{"t": db["text"]}]
            da["laeufe"] = laeufe_zusammen(la + ([{"t": "\n"}] if da.get("text") else []) + lb)
        da["text"] = (da.get("text", "") + ("\n" if da.get("text") else "") + db["text"])
        db["text"] = ""; db.pop("laeufe", None)
    da["weiter"], db["von"] = db["id"], da["id"]
    _speichern_angabe(ed, von_key, dict(a, daten=da)); _speichern_angabe(ed, nach_key, dict(b, daten=db))
    kette_aktualisieren(ed)
    return True


def loesen(ed, key: tuple) -> bool:
    """Die Verknüpfung des Textfelds zu seinem Nachfolger lösen (steht ``key`` am Ende einer Kette, die zu seinem Vorgänger): der Nachfolger
    behält den Text, der in ihm stand; das Feld davor zeigt weiter seinen Text, der Rest wird abgeschnitten. → True, wenn etwas gelöst wurde."""
    felder = dict(_textfelder(ed))
    if key not in felder:
        return False
    d = felder[key].get("daten", {})
    if not d.get("weiter") and d.get("von"):                         # ``key`` ist ein Nachfolger: die Verknüpfung davor lösen
        key = next((k for k, x in felder.items() if x.get("daten", {}).get("weiter") == d.get("id")), None)
        if key is None:
            return False
        d = felder[key].get("daten", {})
    if not d.get("weiter"):
        return False
    nach = next((k for k, x in felder.items() if x.get("daten", {}).get("id") == d["weiter"]), None)
    da = dict(d); da.pop("weiter", None); da.pop("gezeigt_rest", None)
    _speichern_angabe(ed, key, dict(felder[key], daten=da))
    if nach is not None:
        db = dict(felder[nach].get("daten", {})); db.pop("von", None)
        db["text"] = db.pop("gezeigt", db.get("text", ""))           # behält, was in ihm stand
        gl = db.pop("gezeigt_laeufe", None)
        if gl:
            db["laeufe"] = gl
        else:
            db.pop("laeufe", None)
        _speichern_angabe(ed, nach, dict(felder[nach], daten=db))
    kette_aktualisieren(ed)
    return True


def ist_verknuepft(ed, key: tuple) -> bool:
    d = dict(_textfelder(ed)).get(key, {}).get("daten", {})
    return bool(d.get("weiter") or d.get("von"))


def kette_aktualisieren(ed) -> None:
    """Jede Kette neu verteilen: der Text des ersten Feldes (mit seinen Zeichenformaten) füllt ein Feld nach dem anderen; geändert werden nur
    Felder, deren Anteil sich ändert."""
    felder = _textfelder(ed)
    nach_id = {a.get("daten", {}).get("id"): (k, a) for k, a in felder if a.get("daten", {}).get("id")}
    gesehen: set = set()
    for k, a in felder:
        d = a.get("daten", {})
        if d.get("von") or k in gesehen:
            continue
        if not d.get("weiter"):
            if "gezeigt" in d:                                       # nicht (mehr) verknüpft
                d2 = {x: y for x, y in d.items() if x not in ("gezeigt", "gezeigt_laeufe")}; _neu_setzen(ed, k, dict(a, daten=d2))
            continue
        voll = d.get("laeufe") or [{"t": d.get("text", "")}]
        kette = [(k, a)]
        nxt = d
        while nxt.get("weiter") and nxt["weiter"] in nach_id:
            kette.append(nach_id[nxt["weiter"]]); nxt = kette[-1][1].get("daten", {})
        frisch = {kk: aa for kk, aa in _textfelder(ed)}               # aktuelle Angaben (Schlüssel bleiben)
        gesamt, off = laeufe_text(voll), 0
        for kk, aa in kette:
            aa = frisch.get(kk, aa); dd = dict(aa.get("daten", {}))
            gesehen.add(kk)
            rest = laeufe_ab(voll, off)
            if dd.get("weiter"):
                cut = _text_passt(dd, rest, aa["b"], aa["h"])
            else:
                cut = len(laeufe_text(rest))
            zeigt = laeufe_ab(rest, 0, cut)
            skip = len(laeufe_text(rest)[cut:]) - len(laeufe_text(rest)[cut:].lstrip("\n "))
            off += cut + skip
            text = laeufe_text(zeigt).rstrip("\n")
            neu_l = laeufe_zusammen(laeufe_ab(zeigt, 0, len(text))) if d.get("laeufe") else None
            if dd.get("gezeigt") != text or dd.get("gezeigt_laeufe") != neu_l or "gezeigt" not in dd:
                dd["gezeigt"] = text
                if neu_l is not None:
                    dd["gezeigt_laeufe"] = neu_l
                else:
                    dd.pop("gezeigt_laeufe", None)
                _neu_setzen(ed, kk, dict(aa, daten=dd))
