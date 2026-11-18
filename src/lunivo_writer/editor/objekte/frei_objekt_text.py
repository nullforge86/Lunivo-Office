"""Textdarstellung für frei positionierte Objekte."""

from PySide6.QtCore import QRectF, QUrl, Qt
from PySide6.QtGui import (QBrush, QColor, QFont, QFontMetricsF, QImage, QLinearGradient, QPainter, QPainterPath, QPen)

from lunivo_writer.editor.objekte import freie_bilder as FB
from lunivo_writer.editor.objekte.bildeffekte import gespiegelt
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
        unten = gespiegelt(img.copy(0, 0, img.width(), max(1, min(th, img.height()))), senkrecht=True)
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
def _wa_stil(d: dict, pt: float) -> tuple:
    """Füllung, Kontur, Konturbreite und Schatten aus Vorlage und Objektangaben."""
    from lunivo_writer.editor.dokument import einfuegen as E
    _n, f1, f2, kontur, kb, schatten = E.WORDART_VORLAGEN[int(d["vorlage"])]
    if "fuell" in d:
        f1 = f2 = d["fuell"] or None
    if "kontur" in d:
        kontur = d["kontur"] or None
        kb = float(d.get("kontur_breite", 1.5)) * 96 / 72 / max(1.0, pt / 36) if kontur else 0
    elif "kontur_breite" in d and kontur:
        kb = float(d["kontur_breite"]) * 96 / 72 / max(1.0, pt / 36)
    return f1, f2, kontur, kb, schatten


def _wa_format(d: dict, r: dict) -> dict:
    """Das Format eines Laufs: seine eigenen Angaben vor denen des Objekts."""
    return {k: r.get(k, d.get(k)) for k in ZEICHEN_SCHLUESSEL}


def _wa_schrift(e: dict, pt: float) -> QFont:
    f = QFont(e["schrift"] or "Liberation Sans"); f.setPointSizeF(float(e["pt"] or pt))
    f.setBold(True if e["fett"] is None else bool(e["fett"])); f.setItalic(bool(e["kursiv"]))
    if e["hoch"] or e["tief"]:
        f.setPointSizeF(f.pointSizeF() * 0.6)
    return f


def _wa_segmente(d: dict, laeufe: list, pt: float) -> tuple:
    """Je Zeile [(Text, Format, Schrift, Metrik)]; dazu die Listenmarken und das Grundformat."""
    zeilen = _zeilen_laeufe(laeufe) or [[]]
    marken = listenmarken(d.get("liste"), len(zeilen))
    basis = _wa_format(d, {})
    segmente = []
    for m_, zl in zip(marken, zeilen):
        seg = ([(m_, basis)] if m_ else []) + [(r["t"], _wa_format(d, r)) for r in zl]
        segmente.append([(t, e, _wa_schrift(e, pt), QFontMetricsF(_wa_schrift(e, pt))) for t, e in seg])
    return segmente, marken, basis


def _wa_masse(d: dict, segmente: list, basis: dict, pt: float) -> dict:
    """Zeilenhöhen, Grundlinien, Breiten und Bildgröße des WordArt-Bildes."""
    einzug = 24.0 * int(d.get("einzug") or 0)
    fm0 = QFontMetricsF(_wa_schrift(basis, pt))
    hoehen = [max([m_[3].height() for m_ in sg] or [fm0.height()]) for sg in segmente]
    asz = [max([m_[3].ascent() for m_ in sg] or [fm0.ascent()]) for sg in segmente]
    faktor = float(d.get("zeilenabstand") or 1.0)
    breiten = [sum(m_[3].horizontalAdvance(m_[0]) for m_ in sg) + einzug for sg in segmente]
    ys, y_ = [], 20.0
    for hh, aa in zip(hoehen, asz):
        ys.append(y_ + aa); y_ += hh * faktor
    b, h = int(max(breiten)) + 40, int(y_ - (hoehen[-1] * faktor - hoehen[-1])) + 20
    return {"einzug": einzug, "hoehen": hoehen, "asz": asz, "faktor": faktor, "breiten": breiten, "ys": ys, "b": b, "h": h}


def _wa_effekte(d: dict) -> dict:
    ef = d.get("effekt") or {}
    if isinstance(ef, str):                                            # alte Schreibweise: Name
        ef = {({"schatten": "schatten", "spiegelung": "reflektion", "leuchten": "leuchten"}.get(ef.lower(), ef.lower())): {}}
    return ef


def _wa_verteilt(sg: list, marke, ausr: str, letzte: bool) -> bool:
    einzeln = len(sg) <= 1 or (len(sg) == 2 and bool(marke))
    woerter = (sg[-1][0].split(" ") if sg else [])
    return ausr in ("block", "verteilt") and einzeln and len(woerter) > 1 and (ausr == "verteilt" or not letzte)


def _wa_text_pfad(t: str, e: dict, f: QFont, fm: QFontMetricsF, xx: float, y: float, luecke) -> tuple:
    """Pfad eines Laufs (bei `luecke` wortweise verteilt) und die Endposition."""
    pf = QPainterPath()
    for w_ in (t.split(" ") if luecke is not None else [t]):
        pf.addText(xx, y, f, w_); xx += fm.horizontalAdvance(w_) + (luecke or 0)
    return pf, xx


def _wa_zeile(i: int, sg: list, ctx: dict, aus: tuple) -> None:
    """Fügt die Pfade einer Zeile zu (gesamt, gruppen, hervor, linien) hinzu."""
    gesamt, gruppen, hervor, linien = aus
    breiten, einzug, marke = ctx["breiten"], ctx["einzug"], ctx["marken"][i]
    ausr = ctx["ausr"]
    x = {"mitte": (max(breiten) - breiten[i]) / 2, "rechts": max(breiten) - breiten[i]}.get(ausr, 0) + einzug
    woerter = (sg[-1][0].split(" ") if sg else [])
    verteilen = _wa_verteilt(sg, marke, ausr, i >= len(ctx["marken"]) - 1)
    xx = 20 + x
    for t, e, f, fm in sg:
        y = ctx["ys"][i] + (-fm.height() * 0.35 if e["hoch"] else fm.height() * 0.2 if e["tief"] else 0)
        luecke = None
        if verteilen and t is sg[-1][0]:
            summe = sum(fm.horizontalAdvance(w_) for w_ in woerter)
            luecke = (max(breiten) - einzug - summe - (fm.horizontalAdvance(sg[0][0]) if marke else 0)) / (len(woerter) - 1)
        x0 = xx
        pf, xx = _wa_text_pfad(t, e, f, fm, xx, y, luecke)
        _wa_dekoration(pf, e, f, fm, (x0, xx - x0, y), ctx["f1"], aus)
        gesamt.addPath(pf)
        kl = e["kontur"] if e["kontur"] is not None else ctx["kontur"]
        gruppen.setdefault((e["fuell"], kl or None), QPainterPath()).addPath(pf)


def _wa_dekoration(pf: QPainterPath, e: dict, f: QFont, fm: QFontMetricsF, lage: tuple, f1, aus: tuple) -> None:
    """Unterstreichung, Durchstreichung und Hervorhebung eines Laufs."""
    x0, breite_t, y = lage
    _g, _gr, hervor, linien = aus
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


def _wa_glut_schatten(p: QPainter, gesamt: QPainterPath, ef: dict, stil: tuple, pt: float) -> None:
    f1, f2, kontur, schatten = stil
    if "leuchten" in ef:
        glut = QColor((ef["leuchten"] or {}).get("farbe") or f2 or kontur or "#4f93d1"); glut.setAlpha(60)
        for br in (14, 9, 5):
            pen = QPen(glut, br); pen.setJoinStyle(Qt.RoundJoin); p.setPen(pen); p.setBrush(Qt.NoBrush); p.drawPath(gesamt)
    if "schatten" in ef:
        schatten = (ef["schatten"] or {}).get("farbe") or schatten or "#6b6b6b"
    if schatten:
        dd = max(2.0, pt / 14)
        p.setPen(Qt.NoPen); p.setBrush(QColor(schatten)); p.translate(dd, dd); p.drawPath(gesamt); p.translate(-dd, -dd)


def _wa_fuellen(p: QPainter, gruppen: dict, stil: tuple, h: int, pt: float) -> None:
    f1, f2, kb = stil
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


def _wa_spiegeln(img: QImage, b: int, h: int) -> None:
    """Spiegelbild unter das Bild setzen, nach unten verblassend."""
    unten = gespiegelt(img.copy(0, 0, b * _SS, h * _SS), senkrecht=True)
    q = QPainter(unten); q.setCompositionMode(QPainter.CompositionMode_DestinationIn)
    g = QLinearGradient(0, 0, 0, h * _SS); g.setColorAt(0, QColor(0, 0, 0, 110)); g.setColorAt(0.6, QColor(0, 0, 0, 0))
    q.fillRect(unten.rect(), g); q.end()
    q = QPainter(img); q.drawImage(0, h * _SS, unten); q.end()


def wordart_zeichnen(d: dict) -> QImage:
    from lunivo_writer.editor.dokument import einfuegen as E
    laeufe = anzeige_laeufe(d)
    text = laeufe_text(laeufe) or " "
    pt = float(d.get("pt", 36))
    if d.get("vorlage") is None:                                       # alter Weg: Stil und Farbe
        return E.wordart_bild(text, d.get("stil", "Verlauf"), d.get("schrift", "Liberation Sans"), int(pt), d.get("farbe", "#2f78bd"))
    f1, f2, kontur, kb, schatten = _wa_stil(d, pt)
    segmente, marken, basis = _wa_segmente(d, laeufe, pt)
    m = _wa_masse(d, segmente, basis, pt)
    b, h, faktor = m["b"], m["h"], m["faktor"]
    ef = _wa_effekte(d)
    spiegel = "reflektion" in ef
    img = QImage(b * _SS, (h * 2 if spiegel else h) * _SS, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing); p.scale(_SS, _SS)
    aus = (QPainterPath(), {}, [], [])                                 # gesamt; Gruppen nach Füllung/Kontur; Hervorhebungen; eigene Linien
    ctx = {**m, "marken": marken, "ausr": d.get("ausr", "links"), "kontur": kontur, "f1": f1}
    for i, sg in enumerate(segmente):
        _wa_zeile(i, sg, ctx, aus)
    gesamt, gruppen, hervor, linien = aus
    _wa_glut_schatten(p, gesamt, ef, (f1, f2, kontur, schatten), pt)
    for farbe_h, hp in hervor:                                        # Texthervorhebung: Hintergrund hinter dem Text
        p.setPen(Qt.NoPen); p.setBrush(QColor(farbe_h)); p.drawPath(hp)
    _wa_fuellen(p, gruppen, (f1, f2, kb), h, pt)
    if linien:
        from lunivo_writer.editor.text.textfx import _unterstrich
        for x0_, x1_, y_u, art_u, farbe_u, px in linien:
            _unterstrich(p, [(x0_, x1_)], art_u, y_u, float(px), QColor(farbe_u))
    p.end()
    if spiegel:
        _wa_spiegeln(img, b, h)
    ys, asz, hoehen = m["ys"], m["asz"], m["hoehen"]
    return richtung_anwenden(img, d.get("richtung"), [(int((ys[i] - asz[i]) * _SS), int(hoehen[i] * faktor * _SS)) for i in range(len(segmente))])


# ---- Textfeld zeichnen --------------------------------------------------------------------------------------------------
def _zeichen_dict(d: dict, lauf: dict, vorlage, farbe_ueber: str | None, standard_farbe: str) -> dict:
    """Das Zeichenformat eines Laufs im Dokumentenmodell: seine eigenen Angaben, sonst die des Objekts."""
    e = {k: lauf.get(k, d.get(k)) for k in ZEICHEN_SCHLUESSEL}
    z: dict = {"schrift": e["schrift"] or d.get("schrift", "Liberation Sans"), "groesse_pt": float(e["pt"] or d.get("pt", 11))}
    if e["fett"]:
        z["fett"] = True
    if e["kursiv"]:
        z["kursiv"] = True
    if e["unter"]:
        z["unterstrichen"] = True
        if isinstance(e["unter"], str) and e["unter"] != "einfach":
            z["unter_art"] = e["unter"]
        if e["unterfarbe"]:
            z["unter_farbe"] = e["unterfarbe"]
    if e["durch"]:
        z["durchgestrichen"] = True
    if e["hoch"]:
        z["hoch_tief"] = "hoch"
    elif e["tief"]:
        z["hoch_tief"] = "tief"
    if e["hervor"]:
        z["marker"] = e["hervor"]
    kontur = e["kontur"] if e["kontur"] is not None else (vorlage[3] if vorlage and "kontur" not in d else None)
    if kontur:
        z["effekt"] = {"kontur": True, "kontur_farbe": kontur, "kontur_breite": float(d.get("kontur_breite", 0.75))}
    if farbe_ueber:
        z["farbe"] = farbe_ueber
    elif "fuell" in lauf:
        z["farbe"] = lauf["fuell"] or "#00000000"                       # leer = ausdrücklich keine Füllung
    else:
        z["farbe"] = standard_farbe
    return z


TEXTRAND = 8.0                                                 # Standard-Innenabstand des Textes im Feld (Bildpunkte); ``d["innen"]`` = [links, oben, rechts, unten] überschreibt ihn


def _innen(d: dict) -> tuple[float, float, float, float]:
    """Innenabstand links, oben, rechts, unten — aus ``d["innen"]`` (zum Beispiel aus bodyPr lIns/tIns/rIns/bIns einer DOCX), sonst ``TEXTRAND``."""
    w = d.get("innen")
    if isinstance(w, (list, tuple)) and len(w) == 4:
        try:
            return tuple(max(0.0, float(x)) for x in w)
        except (TypeError, ValueError):
            pass
    return (TEXTRAND,) * 4


class _Satz:
    """Das gesetzte Textfeld: ein Dokument in der Größe des Feldes (Innenabstand = Seitenrand), gesetzt von der Layout-Engine des Kerns. Was nicht mehr
    passt, steht auf Seite 2 — daran erkennen verknüpfte Felder, wie viel Text in ein Feld passt."""

    def __init__(self, d: dict, laeufe: list[dict], b: float, h: float, farbe_ueber: str | None = None):
        from lunivo_writer.core.document import neues_dokument
        from lunivo_writer.core.document.dokument import Absatz, Lauf
        from lunivo_writer.core.layout import LayoutEngine
        from lunivo_writer.modelle.seite import PageSettings
        vorlage = None
        if d.get("vorlage") is not None:
            from lunivo_writer.editor.dokument import einfuegen as E
            vorlage = E.WORDART_VORLAGEN[int(d["vorlage"])]
        self.farbe = d.get("fuell") if d.get("fuell") else (vorlage[1] if vorlage and "fuell" not in d else d.get("farbe", "#1f1f1f"))
        li, ob, re_, un = _innen(d)
        self.innen_oben = ob
        breit = max(10.0, b - li - re_)
        mm = 25.4 / 96.0                                               # Bildpunkte → Millimeter
        seite = PageSettings(width_mm=(li + breit + min(4.0, breit * 0.01) + re_) * mm, height_mm=max(1.0, h) * mm, margin_left_mm=li * mm,
                             margin_right_mm=re_ * mm, margin_top_mm=ob * mm, margin_bottom_mm=un * mm)    # kleine Toleranz: Schriftmaße weichen um Bruchteile ab
        self.dok = neues_dokument(seite)
        af: dict = {"ausrichtung": "block" if d.get("ausr") in ("block", "verteilt") else d.get("ausr") if d.get("ausr") in ("mitte", "rechts") else "links"}
        if d.get("einzug"):
            af["einzug_links"] = 24.0 * int(d["einzug"])
        if d.get("zeilenabstand"):
            af.update({"zeilenabstand_art": "vielfach", "zeilenabstand": float(d["zeilenabstand"]) * 100})
        zeilen = _zeilen_laeufe(laeufe) or [[]]
        self.marken = listenmarken(d.get("liste"), len(zeilen))
        self.absatz_ids: list[int] = []
        self.laengen: list[int] = []
        bloecke = []
        for m_, zl in zip(self.marken, zeilen):
            inhalte = []
            if m_:
                inhalte.append(Lauf(m_, _zeichen_dict(d, {}, vorlage, farbe_ueber, self.farbe)))
            inhalte += [Lauf(r["t"], _zeichen_dict(d, r, vorlage, farbe_ueber, self.farbe)) for r in zl]
            a = Absatz(self.dok.neue_id(), inhalte, dict(af))
            bloecke.append(a)
            self.absatz_ids.append(a.id)
            self.laengen.append(sum(len(r["t"]) for r in zl))
        self.dok.abschnitte[0].bloecke = bloecke
        self.layout = LayoutEngine()
        self.erg = self.layout.berechnen(self.dok)

    def zeilen_seite1(self) -> list:
        return [p.rect for p in self.erg.seiten[0].plaetze if p.art == "zeile" and not p.kopie]

    def text_hoehe(self) -> float:
        """Obere Kante des Innenraums bis zur Unterkante der letzten Zeile auf dem Feld."""
        return max([r.bottom for r in self.zeilen_seite1()] + [self.innen_oben])

    def malen(self, p: QPainter) -> None:
        from lunivo_writer.adapter.qt.rendering import QtRenderBackend
        from lunivo_writer.core.rendering import DokumentRenderer
        DokumentRenderer(self.layout.engine).zeichne_seite(QtRenderBackend(p), self.dok, self.erg, 0, None)


def _text_passt(d: dict, laeufe: list[dict], b: float, h: float) -> int:
    """Wie viele Zeichen der Läufe im Feld ``b`` x ``h`` stehen (Anfang der ersten Zeile, die nicht mehr passt) — für verknüpfte Textfelder."""
    satz = _Satz(d, laeufe, b, h)
    vorher = 0                                                         # Zeichen der Absätze davor samt Zeilenwechsel
    for i, aid in enumerate(satz.absatz_ids):
        ort = satz.erg.absaetze.get(aid)
        if ort is not None:
            for seite, zi, _r in ort.zeilen:
                if seite > 0:
                    return max(0, vorher + max(0, ort.satz.zeilen[zi].box.start - len(satz.marken[i] or "")))
        vorher += satz.laengen[i] + 1
    return len(laeufe_text(laeufe))


def _text_malen(img: QImage, d: dict, satz: _Satz, b: float, h: float) -> None:
    """Den gesetzten Text ins Bild malen; mit dem Effekt „Schatten“ darunter derselbe Text in der Schattenfarbe, leicht versetzt."""
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.TextAntialiasing); p.scale(_SS, _SS)
    ef = d.get("effekt") or {}
    if "schatten" in ef:
        sf = (ef["schatten"] or {}).get("farbe") or "#8a8a8a"
        p.save(); p.translate(2, 2); _Satz(d, anzeige_laeufe(d), b, h, sf).malen(p); p.restore()
    satz.malen(p)
    p.end()


def _zeilenbaender(satz: _Satz, hoehe: int) -> list[tuple[int, int]]:
    """(oben, Höhe) jeder Textzeile in Bildpunkten des Bildes; dazu der Rand darüber und darunter als eigene Bänder, damit nichts verloren geht."""
    bander = [(int(r.y * _SS), int(r.height * _SS)) for r in satz.zeilen_seite1()]
    if not bander:
        return bander
    if bander[0][0] > 0:
        bander.insert(0, (0, bander[0][0]))
    letzte = bander[-1][0] + bander[-1][1]
    if letzte < hoehe:
        bander.append((letzte, hoehe - letzte))
    return bander


def textfeld_zeichnen(d: dict, b: float, h: float) -> QImage:
    """Nur der Text (durchsichtig); Füllung und Rand legt die Angabe des Bildes darum (so wirken Füllung und Kontur der Schnellleiste).
    Gezeichnet werden alle Schlüssel der Texttools: fett, kursiv, unter, durch, hoch, tief, hervor, fuell/farbe, kontur, effekt (schatten,
    reflektion, leuchten), vorlage, ausr (block, verteilt), liste, einzug, zeilenabstand, richtung. Bei verknüpften Feldern steht in ``gezeigt``
    der Teil des Textes, der in diesem Feld steht. Gesetzt wird der Text vom Kern (``LayoutEngine``), gezeichnet vom ``DokumentRenderer``."""
    richt = d.get("richtung")
    if richt == "vertikal":
        richt = "senkrecht_rl"
    if _gedreht(richt):
        b, h = h, b
    img = QImage(max(1, int(b * _SS)), max(1, int(h * _SS)), QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    satz = _Satz(d, anzeige_laeufe(d), b, h)
    _text_malen(img, d, satz, b, h)
    ef = d.get("effekt") or {}
    if "leuchten" in ef or "reflektion" in ef:
        img = effekte_auf_text(img, {k: v for k, v in ef.items() if k in ("leuchten", "reflektion")}, satz.text_hoehe(), satz.farbe)
    return richtung_anwenden(img, richt, _zeilenbaender(satz, img.height()) if richt == "senkrecht_lr" else None)
