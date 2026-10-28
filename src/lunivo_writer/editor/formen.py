"""Formen nachträglich ändern (Füllung, Kontur, Vorlage, Größe) und Formen zu einer Gruppe zusammenfassen.

Eine Form ist ein Bild, an dem ihre Parameter hängen (P_OBJEKT, JSON). Beim Ändern wird das Bild aus den Parametern neu gezeichnet.
Eine Gruppe ist EIN Bild aus mehreren Formen nebeneinander (in der Zeile, wie im Text); ihre Einzelformen bleiben als Parameter
gespeichert, „Gruppierung aufheben“ setzt sie wieder einzeln ein. Frei schwebende Z-Ordnung kennt Qt nicht — Gruppen sind daher
Zeilenobjekte, keine frei verschiebbaren Zeichenflächen."""
from __future__ import annotations

import json

from PySide6.QtCore import QUrl
from PySide6.QtGui import QColor, QImage, QPainter, QTextCursor, QTextDocument, QTextImageFormat

from lunivo_writer.editor import einfuegen as E
from lunivo_writer.editor.zusatz import P_OBJEKT

from lunivo_writer.core.farben import Farbe
STANDARD = {"fuell": Farbe.AKZENT_DUNKEL, "linie": "#1f3864", "strich": 2.0, "text": ""}
VORLAGEN = [("Blau", Farbe.AKZENT_DUNKEL, "#1f3864", 2.0), ("Grün", "#6bbf59", "#2d6a1f", 2.0), ("Orange", "#f4a259", "#9c4f0a", 2.0),
            ("Rot", "#e5645f", "#8c1d18", 2.0), ("Grau", "#ced4da", "#495057", 2.0), ("Nur Kontur", "", "#1f3864", 2.5),
            ("Dunkel", "#2b2d42", Farbe.SCHWARZ, 1.5), ("Hell mit dicker Kontur", "#fff3bf", "#e67700", 5.0)]
GRUPPEN_ABSTAND = 8


def objekt(f: QTextImageFormat) -> dict | None:
    if f is None or not f.hasProperty(P_OBJEKT):
        return None
    try:
        return json.loads(f.property(P_OBJEKT))
    except (ValueError, TypeError):
        return None


def ist_form(f) -> bool:
    o = objekt(f)
    return bool(o) and o.get("art") in ("form", "gruppe")


def form_daten(o: dict, breite: float, hoehe: float) -> dict:
    d = dict(STANDARD); d.update(o.get("daten", {}))
    d["breite"], d["hoehe"] = int(round(breite)), int(round(hoehe))
    return d


def _zeichnen(d: dict) -> QImage:
    return E.form_bild(d["form"], d["breite"], d["hoehe"], d["fuell"], d["linie"], d["strich"], d["text"])


def _gruppe_zeichnen(kinder: list[dict]) -> QImage:
    bilder = [_zeichnen(k) for k in kinder]
    b = sum(i.width() for i in bilder) + GRUPPEN_ABSTAND * (len(bilder) - 1)
    h = max(i.height() for i in bilder)
    img = E._leer(b, h)
    p = QPainter(img)
    x = 0
    for i in bilder:
        p.drawImage(x, (h - i.height()) // 2, i)
        x += i.width() + GRUPPEN_ABSTAND
    p.end()
    return img


def _ersetzen(ed, c: QTextCursor, img: QImage, o: dict, f: QTextImageFormat, breite: float, hoehe: float) -> None:
    name = f"obj-{id(img)}-{ed.document().revision()}"
    ed.document().addResource(QTextDocument.ImageResource, QUrl(name), img)
    f = QTextImageFormat(f)
    f.setName(name); f.setWidth(breite); f.setHeight(hoehe)
    f.setProperty(P_OBJEKT, json.dumps(o, ensure_ascii=False, separators=(",", ":")))
    c.setCharFormat(f)
    ed.document().setModified(True)


def aendern(ed, **felder) -> bool:
    """Parameter der markierten Form ändern (fuell, linie, strich, text, form, breite, hoehe) und neu zeichnen."""
    c = ed._bild_cursor()
    if c is None:
        return False
    f = c.charFormat().toImageFormat()
    o = objekt(f)
    if not o or o.get("art") != "form":
        return False
    d = form_daten(o, f.width(), f.height())
    d.update({k: v for k, v in felder.items() if v is not None})
    if "form" not in d:
        return False
    o["daten"] = d
    _ersetzen(ed, c, _zeichnen(d), o, f, d["breite"], d["hoehe"])
    return True


def vorlage(ed, name: str) -> bool:
    for n, fu, li, st in VORLAGEN:
        if n == name:
            return aendern(ed, fuell=fu, linie=li, strich=st)
    return False


def _auswahl_formen(ed) -> list[tuple[int, QTextImageFormat]]:
    """Alle Formbilder der Markierung (Position, Format); nur wenn die Markierung sonst leer ist."""
    c = ed.textCursor()
    if not c.hasSelection():
        return []
    doc = ed.document()
    von, bis = c.selectionStart(), c.selectionEnd()
    out = []
    for pos in range(von, bis):
        ch = doc.characterAt(pos)
        if ch == "￼":
            cc = QTextCursor(doc); cc.setPosition(pos + 1)
            fmt = cc.charFormat()
            if fmt.isImageFormat():
                out.append((pos, fmt.toImageFormat()))
        elif not ch.isspace():
            return []
    return out


def gruppieren(ed) -> str:
    """→ '' bei Erfolg, sonst die Begründung."""
    bilder = _auswahl_formen(ed)
    if not bilder:
        return "Markieren Sie mindestens zwei Formen (und nichts außer Formen) nebeneinander."
    kinder = []
    for _pos, f in bilder:
        o = objekt(f)
        if not o or o.get("art") != "form":
            return "Nur einfache Formen lassen sich gruppieren."
        kinder.append(form_daten(o, f.width(), f.height()))
    if len(kinder) < 2:
        return "Eine Gruppe braucht mindestens zwei Formen."
    img = _gruppe_zeichnen(kinder)
    c = ed.textCursor()
    c.beginEditBlock()
    c.removeSelectedText()
    alt = "Gruppe aus " + ", ".join(k["form"] for k in kinder)
    ed.setTextCursor(c)
    E.qimage_einfuegen(ed, img, alt, "gruppe", {"kinder": kinder})
    c.endEditBlock()
    return ""


def gruppe_aufheben(ed) -> str:
    c = ed._bild_cursor()
    if c is None:
        return "Keine Gruppe ausgewählt."
    f = c.charFormat().toImageFormat()
    o = objekt(f)
    if not o or o.get("art") != "gruppe":
        return "Das ausgewählte Objekt ist keine Gruppe."
    kinder = o["daten"]["kinder"]
    c.beginEditBlock()
    c.removeSelectedText()
    ed.setTextCursor(c)
    for k in kinder:
        E.qimage_einfuegen(ed, _zeichnen(k), "Form: " + k["form"], "form", k)
    c.endEditBlock()
    return ""


# ---- Zeichenbereich (Einfügen ▸ Formen ▸ Neuer Zeichenbereich) -------------------------------------------------------------------
# Ein Bild der Größe 15 × 8 cm, das Formen aufnimmt: ist es markiert (oder steht die Schreibmarke direkt davor), kommt eine Form aus
# der Formen-Klappe hinein statt in den Text. Die Formen stehen als ``kinder`` (Form, Lage x/y, Größe) am Bild und werden bei
# jeder Änderung neu gezeichnet; der gestrichelte Rand zeigt den Bereich.
ZEICHENBEREICH = (567, 302)
ZB_VERSATZ = 24                                                   # jede neue Form etwas rechts unterhalb der vorigen


def zeichenbereich_bild(d: dict) -> QImage:
    from PySide6.QtCore import QRectF, Qt
    from PySide6.QtGui import QPen
    b, h = int(d.get("breite", ZEICHENBEREICH[0])), int(d.get("hoehe", ZEICHENBEREICH[1]))
    img = E._leer(b, h)
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(Farbe.GRAU_HELL), 1, Qt.DashLine)); p.drawRect(QRectF(0.5, 0.5, b - 1, h - 1))
    for k in d.get("kinder", []):
        p.drawImage(int(k["x"]), int(k["y"]), _zeichnen(dict(STANDARD, **k)))
    p.end()
    return img


def zeichenbereich_einfuegen(ed) -> None:
    d = {"breite": min(ZEICHENBEREICH[0], int(ed.page.content_width_px)), "hoehe": ZEICHENBEREICH[1], "kinder": []}
    E.qimage_einfuegen(ed, zeichenbereich_bild(d), "Zeichenbereich", "zeichenbereich", d)


def in_zeichenbereich(ed, form: str) -> bool:
    """Form in den markierten Zeichenbereich setzen; False, wenn keiner markiert ist (dann kommt die Form in den Text)."""
    c = ed._bild_cursor()
    if c is None:
        return False
    f = c.charFormat().toImageFormat()
    o = objekt(f)
    if not o or o.get("art") != "zeichenbereich":
        return False
    d = dict(o.get("daten", {}))
    kinder = list(d.get("kinder", []))
    b, h = int(d.get("breite", ZEICHENBEREICH[0])), int(d.get("hoehe", ZEICHENBEREICH[1]))
    kb, kh = (min(240, b - 16), 60) if E_ist_linie(form) else (min(160, b - 16), min(120, h - 16))
    n = len(kinder)
    x = 8 + (n * ZB_VERSATZ) % max(1, b - kb - 16)
    y = 8 + (n * ZB_VERSATZ) % max(1, h - kh - 16)
    kinder.append({"form": form, "x": x, "y": y, "breite": kb, "hoehe": kh})
    d["kinder"] = kinder
    o["daten"] = d
    _ersetzen(ed, c, zeichenbereich_bild(d), o, f, f.width(), f.height())
    return True


def E_ist_linie(form: str) -> bool:
    from lunivo_writer.editor import formen_katalog as K
    return K.ist_linie(form)
