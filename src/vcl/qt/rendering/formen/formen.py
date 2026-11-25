from __future__ import annotations
from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QImage, QPainter
from vcl.qt.rendering.formen import bild_einfuegen as BE
from vcl.qt.rendering.formen import einfuegen as E
from vcl.qt.rendering.formen import form_einfuegen as FE
from core.formatierung.farben.farben import Farbe
from core.objekte.formen.formen_daten import GRUPPEN_ABSTAND, STANDARD, VORLAGEN, _FO_SCHLUESSEL, form_daten


def _zeichnen(d: dict) -> QImage:
    return FE.form_bild(d["form"], d["breite"], d["hoehe"], d["fuell"], d["linie"], d["strich"], d["text"], adj=d.get("adj"),
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
        BE.qimage_einfuegen(ed, img, alt, "gruppe", {"kinder": kinder})
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
            BE.qimage_einfuegen(ed, _zeichnen(k), "Form: " + k["form"], "form", k)
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
        bild = FE.form_bild(f["form"], int(f["breite"]), int(f["hoehe"]), f["fuell"], f["linie"], float(f["strich"]), f["text"], skala=skala)
        p.drawImage(QRectF(float(f["x"]), float(f["y"]), float(f["breite"]), float(f["hoehe"])), bild)
    p.end()
    return img


# ---- Anpassungsgriff (die gelbe Raute) und Formwechsel ----------------------------------------------------------------------------
def anpass_griffe(form: str, rect, adj=None) -> list:
    """Lage aller Anpassungsgriffe der Form im Rechteck ``rect`` (QRectF, beliebiges Koordinatensystem; Ergebnis im selben) — leer, wenn die Form
    keine hat. ``adj`` = Parameterliste aus ``daten["adj"]`` (fehlt sie: Standardwerte)."""
    from vcl.qt.rendering.formen import formen_anpassen as A
    return A.griffe(form, rect, adj)


def anpass_griff(form: str, rect, adj=None, index: int = 0):
    """Lage des Griffs ``index`` (QPointF) oder None, wenn die Form keinen hat."""
    g = anpass_griffe(form, rect, adj)
    return g[index] if 0 <= index < len(g) else None


def anpassen(form: str, wert: float, adj=None, index: int = 0) -> list[float]:
    """Neue Parameterliste für ``daten["adj"]``: Parameter ``index`` = ``wert`` (begrenzt), die übrigen bleiben; leer bei einer Form ohne Griff."""
    from vcl.qt.rendering.formen import formen_anpassen as A
    return A.setzen(form, wert, adj, index)


def anpass_setzen(ed, wert: float, index: int = 0) -> bool:
    """Parameter ``index`` der gewählten freien Form setzen und neu zeichnen."""
    from vcl.qt.rendering.formen import frei_objekt as FO
    d = FO.daten_lesen(ed, "form")
    if d is None or not anpass_griffe(d.get("form", "Rechteck"), QRectF(0, 0, 1, 1)):
        return False
    return FO.aendern(ed, "form", adj=anpassen(d["form"], wert, d.get("adj"), index))


def form_wechseln(ed, name: str) -> bool:
    """Die gewählte freie Form durch ``name`` ersetzen; Größe, Füllung und Kontur bleiben, die Anpassung (``adj``) fällt weg."""
    from vcl.qt.rendering.formen import formen_katalog as K
    from vcl.qt.rendering.formen import frei_objekt as FO
    if FO.daten_lesen(ed, "form") is None or not (K.hat(name) or name in ("Rechteck", "Textfeld")):
        return False
    return FO.aendern(ed, "form", form=name, adj=None, punkte=None)


def frei_daten(ed) -> dict | None:
    """Die Parameter der gewählten Form als freies Objekt (Kopie) oder None."""
    from vcl.qt.rendering.formen import frei_objekt as FO
    return FO.daten_lesen(ed, "form")


# ---- Zeichenbereich (Einfügen ▸ Formen ▸ Neuer Zeichenbereich) -------------------------------------------------------------------
# Ein freies Objekt der Art „zeichenbereich“, das Formen aufnimmt: ist es gewählt, kommt eine Form aus der Formen-Klappe hinein statt als eigenes
# Objekt aufs Blatt. Die Formen stehen als ``kinder`` (Form, Lage x/y, Größe in Bildpunkten) in den Daten des Bereichs und werden bei jeder
# Änderung neu gezeichnet (``frei_objekt._zeichenbereich_zeichnen``); der gestrichelte Rand zeigt den Bereich.
ZB_VERSATZ = 24                                                   # jede neue Form etwas rechts unterhalb der vorigen


ZB_RAND = 8                                                       # Abstand der ersten Form zum Rand des Bereichs


def zeichenbereich_einfuegen(ed):
    """Einen leeren Zeichenbereich als freies Objekt einfügen (Größe: ``STANDARD_MASS["zeichenbereich"]``, höchstens die Inhaltsbreite). → Id."""
    from vcl.qt.rendering.formen import frei_objekt as FO
    return FO.einfuegen(ed, "zeichenbereich", {"kinder": []})


def in_zeichenbereich(ed, form: str) -> bool:
    """Form in den gewählten Zeichenbereich setzen; False, wenn keiner gewählt ist (dann kommt die Form als eigenes Objekt aufs Blatt)."""
    from vcl.qt.rendering.formen import formen_katalog as K
    from vcl.qt.rendering.formen import frei_objekt as FO
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
