from __future__ import annotations
from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QImage, QPainter
from vcl.qt.rendering.formen import einfuegen as E
from core.formatierung.farben.farben import Farbe
from core.objekte.formen.formen_daten import GRUPPEN_ABSTAND, STANDARD, VORLAGEN, _FO_SCHLUESSEL, form_daten


def _zeichnen(d: dict) -> QImage:
    return E.form_bild(d["form"], d["breite"], d["hoehe"], d["fuell"], d["linie"], d["strich"], d["text"], adj=d.get("adj"),
                       fuell_art=d.get("fuell_art") or "", punkte=d.get("punkte"))


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


def aendern(ed, **felder) -> bool:
    """Parameter der markierten Form ändern (fuell, linie, strich, text, form, breite, hoehe) und neu zeichnen. Eine als freies Objekt
    gewählte Form (``editor/objekte/frei_objekt.py``) geht vor; sonst gilt das Bild im Text (ältere Dokumente)."""
    from vcl.qt.rendering.formen import frei_objekt as FO
    if FO.art_gewaehlt(ed) == "form":
        kw = {_FO_SCHLUESSEL[k]: v for k, v in felder.items() if v is not None and k in _FO_SCHLUESSEL}
        return FO.aendern(ed, "form", **kw) if kw else True
    i = ed.inline_gewaehlt()
    if i is None or i.art != "form":
        return False
    d = form_daten({"daten": i.daten.get("daten") or {}}, i.breite, i.hoehe)
    d.update({k: v for k, v in felder.items() if v is not None})
    if "form" not in d:
        return False
    return ed.inline_neu_zeichnen(_zeichnen(d), d, d["breite"], d["hoehe"])


def vorlage(ed, name: str) -> bool:
    for n, fu, li, st in VORLAGEN:
        if n == name:
            return aendern(ed, fuell=fu, linie=li, strich=st)
    return False


def gruppieren(ed) -> str:
    """→ '' bei Erfolg, sonst die Begründung."""
    objekte = ed.inline_objekte_der_auswahl()
    if not objekte:
        return "Markieren Sie mindestens zwei Formen (und nichts außer Formen) nebeneinander."
    kinder = []
    for o in objekte:
        if o.art != "form":
            return "Nur einfache Formen lassen sich gruppieren."
        kinder.append(form_daten({"daten": o.daten.get("daten") or {}}, o.breite, o.hoehe))
    if len(kinder) < 2:
        return "Eine Gruppe braucht mindestens zwei Formen."
    img = _gruppe_zeichnen(kinder)
    alt = "Gruppe aus " + ", ".join(k["form"] for k in kinder)
    with ed.sitzung.gruppe("Gruppieren"):
        ed.sitzung.loeschen()
        E.qimage_einfuegen(ed, img, alt, "gruppe", {"kinder": kinder})
    return ""


def gruppe_aufheben(ed) -> str:
    g = ed.inline_gewaehlt()
    if g is None:
        return "Keine Gruppe ausgewählt."
    if g.art != "gruppe":
        return "Das ausgewählte Objekt ist keine Gruppe."
    kinder = (g.daten.get("daten") or {}).get("kinder", [])
    with ed.sitzung.gruppe("Gruppierung aufheben"):
        ed.sitzung.loeschen()
        for k in kinder:
            E.qimage_einfuegen(ed, _zeichnen(k), "Form: " + k["form"], "form", k)
    return ""


def zeichenbereich_bild(d: dict, skala: float = 1.0) -> QImage:
    """Der Bereich ``d`` (``breite``, ``hoehe``, ``kinder``) als Bild, ``skala``-fach aufgelöst (Maße bleiben logisch)."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPen
    b, h = int(d.get("breite", 567)), int(d.get("hoehe", 302))
    img = E._leer(max(1, round(b * skala)), max(1, round(h * skala)))
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
    p.scale(skala, skala)
    p.setPen(QPen(QColor(Farbe.GRAU_HELL), 1, Qt.DashLine)); p.drawRect(QRectF(0.5, 0.5, b - 1, h - 1))
    for k in d.get("kinder", []):
        f = {**STANDARD, **k}
        bild = E.form_bild(f["form"], int(f["breite"]), int(f["hoehe"]), f["fuell"], f["linie"], float(f["strich"]), f["text"], skala=skala)
        p.drawImage(QRectF(float(f["x"]), float(f["y"]), float(f["breite"]), float(f["hoehe"])), bild)
    p.end()
    return img
