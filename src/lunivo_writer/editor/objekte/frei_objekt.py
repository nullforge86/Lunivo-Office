"""Freie Objekte mit Parametern (WordArt, Textfeld): EIN gemeinsamer Baustein.

Ein solches Objekt ist ein frei positioniertes Bild (siehe ``freie_bilder``): Auswahlrahmen, acht Griffe, Drehgriff, Verschieben und die
Schnellleiste daneben (Layout, Formstil, Füllung, Kontur) kommen aus ``ui/document/bearbeitung/freie_bilder_bedienung.py``. Dieser Baustein ergänzt nur,
was die beiden Arten unterscheidet: ihre Parameter (``art`` und ``daten`` an der Angabe des Bildes) und das Zeichnen daraus.
Neue Art = ein Eintrag in ``ZEICHNER``. Kein HTML: gezeichnet wird mit QPainter und QTextDocument (Klartext).
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, QUrl, Qt
from PySide6.QtGui import (QBrush, QColor, QFont, QFontMetricsF, QImage, QLinearGradient, QPainter, QPainterPath, QPen, QTextCursor,
                           QTextDocument, QTextOption)

from lunivo_writer.editor.objekte import freie_bilder as FB
from lunivo_writer.editor.text.mehrstufig import nummer_text

from lunivo_writer.editor.objekte.frei_objekt_text import (
    ARTEN, TEXT_ARTEN, STANDARD_MASS, FORM_STANDARD, TEXTFELD_STANDARD,
    TEXTFELD_FUELL, TEXTFELD_RAND, WORDART_STANDARD, _SS, RICHTUNGEN,
    _PUNKTE, ZEICHEN_SCHLUESSEL, listenmarken, richtung_anwenden, _gedreht, effekte_auf_text,
    anzeige_laeufe, laeufe_text, laeufe_ab, laeufe_zusammen, _zeilen_laeufe,
    wordart_zeichnen, _zeichenformat, _textdoc, _text_passt, textfeld_zeichnen,
)


def _form_zeichnen(d: dict, b: float, h: float) -> QImage:
    """Eine Form (``editor/objekte/formen.py``/``einfuegen.py``) in b × h Bildpunkten, in doppelter Auflösung."""
    from lunivo_writer.editor.dokument import einfuegen as E
    k = {**FORM_STANDARD, **d}
    b, h = (b, h) if b and h else STANDARD_MASS["form"]
    return E.form_bild(k["form"], max(2, round(b)), max(2, round(h)), k["fuell"] or "", k["linie"] or "#00000000",
                       float(k["strich"]), k["text"], skala=_SS, adj=k.get("adj"), fuell_art=k.get("fuell_art") or "",
                       punkte=k.get("punkte"))


def _diagramm_zeichnen(d: dict, b: float, h: float) -> QImage:
    """Ein Diagramm (``editor/diagramme/diagramm.py``) aus den gespeicherten Daten, in b × h Bildpunkten, in doppelter Auflösung."""
    from lunivo_writer.editor.diagramme import diagramm as D
    b, h = (b, h) if b and h else STANDARD_MASS["diagramm"]
    return D.bild_aus_daten(d, b, h, _SS)


def _smartart_zeichnen(d: dict, _b: float, _h: float) -> QImage:
    from lunivo_writer.editor.objekte import smartart as SA
    return SA.zeichnen(d)


def _piktogramm_zeichnen(d: dict, _b: float, _h: float) -> QImage:
    from lunivo_writer.editor.dokument import einfuegen as E
    return E.piktogramm_bild(d.get("name", "star"), 96, d.get("farbe", "#1f2328"))


def _zeichenbereich_zeichnen(d: dict, b: float, h: float) -> QImage:
    """Zeichenbereich (``editor/objekte/formen.py``): gestrichelter Rand und die ``kinder`` (Formen mit Lage x/y), in doppelter Auflösung."""
    from lunivo_writer.editor.objekte import formen as F
    b, h = (b, h) if b and h else STANDARD_MASS["zeichenbereich"]
    return F.zeichenbereich_bild(dict(d, breite=round(b), hoehe=round(h)), _SS)


# Art → Funktion(daten, breite, höhe) → Bild. Neue Art = ein Eintrag hier (und in ARTEN).
ZEICHNER = {"wordart": lambda d, b, h: wordart_zeichnen(d), "textfeld": textfeld_zeichnen, "form": _form_zeichnen,
            "diagramm": _diagramm_zeichnen, "smartart": _smartart_zeichnen, "piktogramm": _piktogramm_zeichnen,
            "zeichenbereich": _zeichenbereich_zeichnen}
NEU_ZEICHNEN = ("textfeld", "form", "diagramm", "zeichenbereich")                      # Arten, die nach einer Größenänderung in der neuen Größe frisch gezeichnet werden


def zeichnen(art: str, d: dict, b: float = 0, h: float = 0) -> QImage:
    return ZEICHNER[art](d, b, h)


def _anzeige_mass(art: str, img: QImage, b: float, h: float) -> tuple[float, float]:
    """Größe auf dem Blatt in Bildpunkten: WordArt aus dem Bild (ohne Überbreite), SmartArt wie das Bild (sofern keine Größe vorgegeben),
    Textfeld, Form und Diagramm wie vorgegeben (sonst die Standardgröße)."""
    if art == "wordart":
        return img.width() / _SS, img.height() / _SS
    if art in ("smartart", "piktogramm"):
        return (b, h) if b and h else (float(img.width()), float(img.height()))
    return (b, h) if b and h else STANDARD_MASS.get(art, (b, h))


# ---- Einfügen -----------------------------------------------------------------------------------------------------------
def einfuegen(ed, art: str, daten: dict, b: float = 0, h: float = 0) -> tuple | None:
    """Fügt das Objekt als freies Bild am Absatz der Schreibmarke ein (steht dort Text, in einem neuen Absatz darunter), wählt es aus —
    mit Rahmen, Griffen und Schnellleiste — und lässt keine Textmarkierung zurück. → Schlüssel des Objekts."""
    doc = ed.document()
    if art in STANDARD_MASS and not (b and h):
        b, h = STANDARD_MASS[art]
    img = zeichnen(art, daten, b, h)
    bb, hh = _anzeige_mass(art, img, b, h)
    key = bild_einfuegen(ed, img, bb, hh, art, daten)
    if art == "textfeld":                                            # wie in der Vorlage: die Schreibmarke steht gleich im leeren Textfeld
        bearbeiten_starten(ed)
    return key


def bild_einfuegen(ed, img: QImage, bb: float, hh: float, art: str | None = None, daten: dict | None = None, alt: str = "") -> tuple:
    """Der gemeinsame Weg aller freien Bilder: ``img`` als Ressource, die Angabe am Absatz der Schreibmarke (steht dort Text, in einem neuen
    Absatz darunter), Größe auf die Inhaltsbreite begrenzt, danach ausgewählt (Rahmen, Griffe, Schnellleiste) ohne Textmarkierung.
    ``art``/``daten`` nur bei Objekten mit Parametern (siehe ``ZEICHNER``); ein gewöhnliches Bild (Datei, Bildschirmfoto) hat keine.
    → Schlüssel des Objekts."""
    doc = ed.document()
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
         "ellipse": False, "dreh": 0.0}
    if art:
        a["art"], a["daten"] = art, dict(daten or {})
    if alt:
        a["alt"] = alt
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
    return ed._frei_sel


# ---- Lesen und Ändern ---------------------------------------------------------------------------------------------------------
def ziel(ed):
    """(Art, Daten, Schlüssel, Angabe, Bild) des gewählten Objekts (WordArt, Textfeld, Form, Diagramm, SmartArt) oder None."""
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


def _daten_vorbereiten(d: dict, kw: dict) -> None:
    """Vor dem Ändern: Vorlage und neuer Text setzen Altes zurück, ein Zeichenformat fürs ganze Objekt löscht gleiche Angaben der Läufe."""
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


def _form_daten_setzen(d: dict, k: str, v) -> None:
    """Bei einer Form: Farben der Form selbst, kein Kasten ums Bild."""
    if k == "form_fuell":
        d["fuell"] = v or ""
    elif k == "form_linie":
        d["linie"] = v or ""
    else:
        d["strich"] = float(v)


def _kasten_setzen(neu: dict, a: dict, k: str, v) -> None:
    """Füllung, Strichstärke, Effekt und Linie des Kastens ums Objekt."""
    if k == "form_fuell":
        neu["fuell"] = {"art": "farbe", "farbe": v} if v else None
    elif k == "form_strich":
        neu["rand"] = {**(a.get("rand") or TEXTFELD_RAND), "b": float(v) * 96 / 72}
    elif k == "form_effekt":
        if v:
            neu["fx"] = v
        else:
            neu.pop("fx", None)
    else:                                                            # form_linie
        neu["rand"] = {**(a.get("rand") or TEXTFELD_RAND), "farbe": v} if v else None


def _eintrag_setzen(art: str, k: str, v, d: dict, neu: dict, a: dict) -> None:
    """Ein Schlüssel von ``kw`` (außer Größe) in ``daten`` oder in den Kasten schreiben."""
    if k == "laeufe":
        if v:
            d["laeufe"] = v
        else:
            d.pop("laeufe", None)
    elif art == "form" and k in ("form_fuell", "form_linie", "form_strich"):
        _form_daten_setzen(d, k, v)
    elif k == "untertyp":                                          # Diagramm: Diagrammart (in den Daten unter „art“)
        d["art"] = v
    elif k in ("form_fuell", "form_strich", "form_effekt", "form_linie"):
        _kasten_setzen(neu, a, k, v)
    elif v is None:
        d.pop(k, None)
    else:
        d[k] = v


def _bild_erneuern(ed, art: str, d: dict, a: dict, bild, b: float, h: float) -> tuple:
    """Neues Bild des Objekts zeichnen und als Dokument-Ressource anlegen: (Name, Breite, Höhe)."""
    if art == "smartart":                                        # Breite bleibt, die Höhe folgt dem neuen Bild
        img = zeichnen(art, d, b, h)
        h = b * img.height() / max(1, img.width())
    elif art == "wordart":                                         # die Größe folgt dem Bild: gleicher Maßstab wie vorher
        faktor = a["b"] / max(1.0, bild.width() / _SS)
        img = wordart_zeichnen(d)
        b, h = img.width() / _SS * faktor, img.height() / _SS * faktor
    else:
        img = zeichnen(art, d, b, h)
    n = FB.neuer_name(ed.document())
    ed.document().addResource(QTextDocument.ImageResource, QUrl(n), img)
    return n, b, h


def _aendern_innen(ed, art: str, **kw) -> bool:
    """Parameter des gewählten Objekts ändern und neu zeichnen. ``breite``/``hoehe`` (px) ändern die Größe; ``form_fuell`` (Farbe oder ``""``)
    und ``form_linie`` (Farbe oder ``""``) die Füllung und den Rand des Objekts; alle anderen Schlüssel gehören zu ``daten``."""
    from lunivo_writer.editor.objekte import bildlayout as BL
    z = ziel(ed)
    if z is None or z[0] != art:
        return False
    _art, d, key, a, bild = z
    neu = dict(a)
    b, h = float(a["b"]), float(a["h"])
    _daten_vorbereiten(d, kw)
    for k, v in kw.items():
        if k == "breite":
            b = float(v)
        elif k == "hoehe":
            h = float(v)
        else:
            _eintrag_setzen(art, k, v, d, neu, a)
    neu_zeichnen = set(kw) - {"form_fuell", "form_linie", "form_strich", "form_effekt"} or (
        art == "form" and set(kw) & {"form_fuell", "form_linie", "form_strich"})
    if neu_zeichnen:
        n, b, h = _bild_erneuern(ed, art, d, a, bild, b, h)
        neu["n"], neu["b"], neu["h"], neu["daten"] = n, b, h, d
    BL._speichern_frei(ed, key, neu)
    if art == "textfeld":
        kette_aktualisieren(ed)
    return True


def daten_still(ed, art: str, **kw) -> bool:
    """Daten des gewählten Objekts ändern, ohne das Bild neu zu zeichnen (z. B. die Auswahl eines Diagrammteils); None entfernt den Schlüssel."""
    from lunivo_writer.editor.objekte import bildlayout as BL
    z = ziel(ed)
    if z is None or z[0] != art:
        return False
    _art, d, key, a, _bild = z
    for k, v in kw.items():
        if v is None:
            d.pop(k, None)
        else:
            d[k] = v
    BL._speichern_frei(ed, key, dict(a, daten=d))
    return True


def nach_groesse(ed, neu: dict) -> dict:
    """Nach dem Ziehen der Griffe: Textfeld, Form und Diagramm werden in der neuen Größe frisch gezeichnet (Zeilenumbruch folgt der Breite,
    Linien und Schrift bleiben scharf); SmartArt skaliert nur."""
    if neu.get("art") in NEU_ZEICHNEN and neu.get("n"):
        n = FB.neuer_name(ed.document())
        ed.document().addResource(QTextDocument.ImageResource, QUrl(n), zeichnen(neu["art"], neu.get("daten", {}), neu["b"], neu["h"]))
        neu = dict(neu, n=n)
    return neu


def text_bereich(a: dict, bild: QImage) -> QRectF | None:
    """Wo der Text im Objekt liegt, als Anteil (0..1) von Breite/Höhe — für die graue Textmarkierung wie in der Vorlage (nur WordArt)."""
    if a.get("art") != "wordart" or bild is None or bild.isNull():
        return None
    w, h = bild.width() / _SS, bild.height() / _SS
    if "reflektion" in (a.get("daten", {}).get("effekt") or {}):
        h /= 2
        return QRectF(20 / w, 20 / (h * 2), (w - 40) / w, (h - 40) / (h * 2))
    return QRectF(20 / w, 20 / h, (w - 40) / w, (h - 40) / h)


# ---- Schreiben im Objekt ---------------------------------------------------------------------------------------------------
def _fmt_unter(cf, k, v) -> None:
    cf.setFontUnderline(bool(v))
    if isinstance(v, str) and v:
        from lunivo_writer.editor.text.unterstreichung import unter_format
        cf.merge(unter_format(v))


def _fmt_hoch_tief(cf, k, v) -> None:
    from PySide6.QtGui import QTextCharFormat
    cf.setVerticalAlignment(QTextCharFormat.AlignSuperScript if k == "hoch" and v else QTextCharFormat.AlignSubScript if k == "tief" and v
                            else QTextCharFormat.AlignNormal)


def _fmt_schrift(cf, k, v) -> None:
    if v:
        cf.setFontFamilies([v])


def _fmt_pt(cf, k, v) -> None:
    if v:
        cf.setFontPointSize(float(v))


# Schlüssel der Texttools -> Setzer auf dem Zeichenformat (cf, Schlüssel, Wert)
_FORMAT_SETZER = {
    "fett": lambda cf, k, v: cf.setFontWeight(QFont.Bold if v else QFont.Normal),
    "kursiv": lambda cf, k, v: cf.setFontItalic(bool(v)),
    "unter": _fmt_unter,
    "unterfarbe": lambda cf, k, v: cf.setUnderlineColor(QColor(v) if v else QColor()),
    "durch": lambda cf, k, v: cf.setFontStrikeOut(bool(v)),
    "hoch": _fmt_hoch_tief,
    "tief": _fmt_hoch_tief,
    "hervor": lambda cf, k, v: cf.setBackground(QColor(v) if v else QColor(0, 0, 0, 0)),
    "fuell": lambda cf, k, v: cf.setForeground(QColor(v) if v else QColor(0, 0, 0, 0)),
    "kontur": lambda cf, k, v: cf.setTextOutline(QPen(QColor(v), 1.0) if v else QPen(Qt.NoPen)),
    "schrift": _fmt_schrift,
    "pt": _fmt_pt,
}


def _format_aus_kw(kw: dict):
    """Zeichenformat für das Eingabefeld aus Schlüsseln der Texttools (nur die genannten)."""
    from PySide6.QtGui import QTextCharFormat
    cf = QTextCharFormat()
    for k, v in kw.items():
        setzer = _FORMAT_SETZER.get(k)
        if setzer:
            setzer(cf, k, v)
    return cf


def _lauf_aus_format(cf, basis: dict) -> dict:
    """Die Zeichenschlüssel, die ein Format ausdrücklich setzt und die vom Objekt abweichen."""
    from PySide6.QtGui import QTextCharFormat, QTextFormat
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
    if z is None or z[0] not in TEXT_ARTEN:
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
    if z is None or z[0] not in TEXT_ARTEN:
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
    if art not in TEXT_ARTEN:
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
    """Textfeld ``von`` mit Textfeld ``nach`` verknüpfen: was in ``von`` nicht mehr passt, läuft in ``nach`` weiter (wie „Verknüpfung erstellen“).
    Der Text von ``nach`` wird an den von ``von`` gehängt. Nicht möglich: gleiche Felder, ``von`` hat schon einen Nachfolger, ``nach`` einen
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


def _kette_glieder(k, a, nach_id: dict) -> list:
    """Alle Felder einer Kette ab ``(k, a)`` in Reihenfolge."""
    kette = [(k, a)]
    nxt = a.get("daten", {})
    while nxt.get("weiter") and nxt["weiter"] in nach_id:
        kette.append(nach_id[nxt["weiter"]]); nxt = kette[-1][1].get("daten", {})
    return kette


def _kette_verteilen(ed, kette: list, voll: list, hat_laeufe: bool, gesehen: set) -> None:
    """Den vollen Text auf die Felder der Kette verteilen; nur Felder mit geändertem Anteil neu setzen."""
    frisch = {kk: aa for kk, aa in _textfelder(ed)}               # aktuelle Angaben (Schlüssel bleiben)
    off = 0
    for kk, aa in kette:
        aa = frisch.get(kk, aa); dd = dict(aa.get("daten", {}))
        gesehen.add(kk)
        rest = laeufe_ab(voll, off)
        cut = _text_passt(dd, rest, aa["b"], aa["h"]) if dd.get("weiter") else len(laeufe_text(rest))
        zeigt = laeufe_ab(rest, 0, cut)
        skip = len(laeufe_text(rest)[cut:]) - len(laeufe_text(rest)[cut:].lstrip("\n "))
        off += cut + skip
        text = laeufe_text(zeigt).rstrip("\n")
        neu_l = laeufe_zusammen(laeufe_ab(zeigt, 0, len(text))) if hat_laeufe else None
        if dd.get("gezeigt") != text or dd.get("gezeigt_laeufe") != neu_l or "gezeigt" not in dd:
            dd["gezeigt"] = text
            if neu_l is not None:
                dd["gezeigt_laeufe"] = neu_l
            else:
                dd.pop("gezeigt_laeufe", None)
            _neu_setzen(ed, kk, dict(aa, daten=dd))


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
        _kette_verteilen(ed, _kette_glieder(k, a, nach_id), voll, bool(d.get("laeufe")), gesehen)
