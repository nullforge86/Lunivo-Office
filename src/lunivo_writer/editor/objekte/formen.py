"""Formen nachträglich ändern (Füllung, Kontur, Vorlage, Größe) und Formen zu einer Gruppe zusammenfassen.

Eine Form ist ein Bild, an dem ihre Parameter hängen (P_OBJEKT, JSON). Beim Ändern wird das Bild aus den Parametern neu gezeichnet.
Eine Gruppe ist EIN Bild aus mehreren Formen nebeneinander (in der Zeile, wie im Text); ihre Einzelformen bleiben als Parameter
gespeichert, „Gruppierung aufheben“ setzt sie wieder einzeln ein. Frei schwebende Z-Ordnung kennt Qt nicht — Gruppen sind daher
Zeilenobjekte, keine frei verschiebbaren Zeichenflächen."""
from __future__ import annotations

import json

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QImage, QPainter

from lunivo_writer.editor.dokument import einfuegen as E

from lunivo_writer.oberflaeche.baukasten.farben.farben import Farbe
STANDARD = {"fuell": Farbe.AKZENT_DUNKEL, "linie": "#1f3864", "strich": 2.0, "text": ""}
VORLAGEN = [("Blau", Farbe.AKZENT_DUNKEL, "#1f3864", 2.0), ("Grün", "#6bbf59", "#2d6a1f", 2.0), ("Orange", "#f4a259", "#9c4f0a", 2.0),
            ("Rot", "#e5645f", "#8c1d18", 2.0), ("Grau", "#ced4da", "#495057", 2.0), ("Nur Kontur", "", "#1f3864", 2.5),
            ("Dunkel", "#2b2d42", Farbe.SCHWARZ, 1.5), ("Hell mit dicker Kontur", "#fff3bf", "#e67700", 5.0)]
GRUPPEN_ABSTAND = 8


def form_daten(o: dict, breite: float, hoehe: float) -> dict:
    d = dict(STANDARD); d.update(o.get("daten", {}))
    d["breite"], d["hoehe"] = int(round(breite)), int(round(hoehe))
    return d


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


_FO_SCHLUESSEL = {"fuell": "form_fuell", "linie": "form_linie", "strich": "form_strich", "text": "text", "form": "form",
                  "breite": "breite", "hoehe": "hoehe"}


def frei_daten(ed) -> dict | None:
    """Die Parameter der gewählten Form als freies Objekt (Kopie) oder None."""
    from lunivo_writer.editor.objekte import frei_objekt as FO
    return FO.daten_lesen(ed, "form")


def aendern(ed, **felder) -> bool:
    """Parameter der markierten Form ändern (fuell, linie, strich, text, form, breite, hoehe) und neu zeichnen. Eine als freies Objekt
    gewählte Form (``editor/objekte/frei_objekt.py``) geht vor; sonst gilt das Bild im Text (ältere Dokumente)."""
    from lunivo_writer.editor.objekte import frei_objekt as FO
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


# ---- Zeichenbereich (Einfügen ▸ Formen ▸ Neuer Zeichenbereich) -------------------------------------------------------------------
# Ein freies Objekt der Art „zeichenbereich“, das Formen aufnimmt: ist es gewählt, kommt eine Form aus der Formen-Klappe hinein statt als eigenes
# Objekt aufs Blatt. Die Formen stehen als ``kinder`` (Form, Lage x/y, Größe in Bildpunkten) in den Daten des Bereichs und werden bei jeder
# Änderung neu gezeichnet (``frei_objekt._zeichenbereich_zeichnen``); der gestrichelte Rand zeigt den Bereich.
ZB_VERSATZ = 24                                                   # jede neue Form etwas rechts unterhalb der vorigen
ZB_RAND = 8                                                       # Abstand der ersten Form zum Rand des Bereichs


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


def zeichenbereich_einfuegen(ed):
    """Einen leeren Zeichenbereich als freies Objekt einfügen (Größe: ``STANDARD_MASS["zeichenbereich"]``, höchstens die Inhaltsbreite). → Id."""
    from lunivo_writer.editor.objekte import frei_objekt as FO
    return FO.einfuegen(ed, "zeichenbereich", {"kinder": []})


def in_zeichenbereich(ed, form: str) -> bool:
    """Form in den gewählten Zeichenbereich setzen; False, wenn keiner gewählt ist (dann kommt die Form als eigenes Objekt aufs Blatt)."""
    from lunivo_writer.editor.objekte import formen_katalog as K
    from lunivo_writer.editor.objekte import frei_objekt as FO
    z = FO.ziel(ed)
    if z is None or z[0] != "zeichenbereich":
        return False
    d, a = z[1], z[3]
    b, h = int(a["b"]), int(a["h"])
    kinder = list(d.get("kinder", []))
    kb, kh = (min(240, b - 2 * ZB_RAND), 60) if K.ist_linie(form) else (min(160, b - 2 * ZB_RAND), min(120, h - 2 * ZB_RAND))
    n = len(kinder)
    x = ZB_RAND + (n * ZB_VERSATZ) % max(1, b - kb - 2 * ZB_RAND)
    y = ZB_RAND + (n * ZB_VERSATZ) % max(1, h - kh - 2 * ZB_RAND)
    kinder.append({"form": form, "x": x, "y": y, "breite": kb, "hoehe": kh})
    return FO.aendern(ed, "zeichenbereich", kinder=kinder)
