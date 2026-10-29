"""Punkte einer Form bearbeiten mit der Maus (Zeichentools ▸ Form bearbeiten ▸ Punkte bearbeiten); Rechnen in ``editor/freiform.py``.

Im Bearbeitungsmodus zeigt die gewählte Form ihre Punkte als kleine Quadrate (Kurven-Steuerpunkte als Kreise): Ziehen verschiebt einen Punkt
(das Bild zeichnet sich dabei laufend neu, gespeichert wird erst beim Loslassen — ein Rückgängig-Schritt), Rechtsklick oder Entf löscht den
gewählten Punkt, Doppelklick auf eine Kante fügt einen Punkt ein, Esc oder ein Klick daneben beendet den Modus. Die Funktionen bekommen den
Editor (``DocumentEditor``) und hängen am Zustand in seinem ``__dict__``: ``_fp_key`` (Schlüssel der Form im Modus), ``_fp_sel`` (gewählter
Punkt), ``_fp_zug`` (Index des gezogenen Elements), ``_fp_arbeit`` (Punktliste während des Ziehens)."""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPen, QTransform

from lunivo_writer.editor import freiform as FF

TREFFER = 8.0                                                 # so nah (Bildschirmpunkte) trifft die Maus einen Punkt
KANTE = 6.0                                                   # so nah trifft sie eine Kante


# ---- Zustand ---------------------------------------------------------------------------------------------------------------------
def aktiv(ed) -> bool:
    k = ed.__dict__.get("_fp_key")
    return k is not None and k == getattr(ed, "_frei_sel", None)


def starten(ed) -> bool:
    """Die gewählte Form in eine Freiform umwandeln (falls nötig; ein Schritt für Rückgängig) und den Modus einschalten."""
    from lunivo_writer.editor import frei_objekt as FO
    z = FO.ziel(ed)
    if z is None or z[0] != "form":
        return False
    _art, d, _key, a, _bild = z
    if not d.get("punkte"):
        if not FO.aendern(ed, "form", form=FF.NAME, punkte=FF.aus_form(d, float(a["b"]), float(a["h"])), adj=None):
            return False
    ed.__dict__["_fp_key"] = ed._frei_sel
    ed.__dict__["_fp_sel"] = None
    ed.__dict__["_fp_zug"] = None
    ed.viewport().update()
    return True


def beenden(ed) -> None:
    for k in ("_fp_key", "_fp_sel", "_fp_zug", "_fp_arbeit"):
        ed.__dict__[k] = None
    ed._frei_vorlaeufig.clear() if hasattr(ed, "_frei_vorlaeufig") else None
    ed.viewport().update()


# ---- Abbildung -------------------------------------------------------------------------------------------------------------------
def _eintrag(ed):
    k = ed.__dict__.get("_fp_key")
    for key, a, r, hinten, n in getattr(ed, "_frei_treffer", []):
        if key == k and (a.get("daten") or {}).get("punkte"):                      # wurde die Form getauscht, ist der Modus vorbei
            return key, a, r, n
    return None


def _punkte(ed, a) -> list:
    return ed.__dict__.get("_fp_arbeit") or (a.get("daten") or {}).get("punkte") or []


class _Abb:
    """Anteil (0..1) im Zeichenrechteck der Form ↔ Bildschirm (Editorkoordinaten) für ein Objekt (Zoom, Lage, Drehung)."""

    def __init__(self, a: dict, r: QRectF):
        b, h = float(a["b"]), float(a["h"])
        inn = FF.innen(a.get("daten") or {}, b, h)
        sx, sy = r.width() / max(1.0, b), r.height() / max(1.0, h)
        self.rect = QRectF(r.x() + inn.x() * sx, r.y() + inn.y() * sy, inn.width() * sx, inn.height() * sy)
        dreh = float(a.get("dreh", 0.0) or 0.0)
        self.vor = QTransform().translate(r.center().x(), r.center().y()).rotate(dreh).translate(-r.center().x(), -r.center().y())
        self.rueck = self.vor.inverted()[0]

    def zu_schirm(self, x: float, y: float) -> QPointF:
        return self.vor.map(QPointF(self.rect.left() + x * self.rect.width(), self.rect.top() + y * self.rect.height()))

    def zu_anteil(self, pos: QPointF) -> tuple[float, float]:
        q = self.rueck.map(pos)
        return (q.x() - self.rect.left()) / max(1e-9, self.rect.width()), (q.y() - self.rect.top()) / max(1e-9, self.rect.height())


def _punkt_bei(punkte: list, abb: _Abb, pos: QPointF):
    """Index des Punkts (oder Steuerpunkts) unter der Maus; Punkte gehen vor Steuerpunkten."""
    rl = FF.rollen(punkte)
    best = None
    for i, e in enumerate(punkte):
        if rl[i] == "zu":
            continue
        c = abb.zu_schirm(e[1], e[2])
        d = max(abs(pos.x() - c.x()), abs(pos.y() - c.y()))
        if d <= TREFFER and (best is None or (rl[i] == "knoten", -d) > (best[1], -best[2])):
            best = (i, rl[i] == "knoten", d)
    return best[0] if best else None


# ---- Zeichnen --------------------------------------------------------------------------------------------------------------------
def zeichnen(ed, p, r: QRectF, a: dict) -> None:
    """Punkte (Quadrate), Steuerpunkte (Kreise mit Haltelinie) und den gewählten Punkt (gefüllt) der Form."""
    punkte = _punkte(ed, a)
    abb = _Abb(a, r)
    rl = FF.rollen(punkte)
    sel = ed.__dict__.get("_fp_sel")
    p.save()
    p.setPen(QPen(QColor("#8c8c8c"), 1, Qt.DotLine))
    for i, e in enumerate(punkte):                                            # Haltelinien der Kurven
        if rl[i] == "steuer":
            nachbar = i - 1 if punkte[i][0] == FF.C else i + 1                  # erster Steuerpunkt: zum Anfang, zweiter: zum Ende der Kurve
            if 0 <= nachbar < len(punkte) and rl[nachbar] == "knoten":
                p.drawLine(abb.zu_schirm(e[1], e[2]), abb.zu_schirm(punkte[nachbar][1], punkte[nachbar][2]))
    for i, e in enumerate(punkte):
        if rl[i] == "zu":
            continue
        c = abb.zu_schirm(e[1], e[2])
        if rl[i] == "steuer":
            p.setPen(QPen(QColor("#1c7ed6"), 1.2)); p.setBrush(QColor("white")); p.drawEllipse(c, 3.5, 3.5)
        else:
            p.setPen(QPen(QColor("black"), 1.2)); p.setBrush(QColor("#1c7ed6") if i == sel else QColor("white"))
            p.drawRect(QRectF(c.x() - 4, c.y() - 4, 8, 8))
    p.restore()


# ---- Maus und Tasten -------------------------------------------------------------------------------------------------------------
def _speichern(ed, punkte: list) -> None:
    from lunivo_writer.editor import frei_objekt as FO
    ed._frei_vorlaeufig.clear()
    ed.__dict__["_fp_arbeit"] = None
    FO.aendern(ed, "form", punkte=punkte)
    ed.viewport().update()


def _vorschau(ed, key, a, punkte) -> None:
    """Das Bild der Form mit den vorläufigen Punkten neu zeichnen — ohne Dokumentschritt."""
    from lunivo_writer.editor import frei_objekt as FO
    d = {**FO.FORM_STANDARD, **(a.get("daten") or {}), "form": FF.NAME, "punkte": punkte}
    n = ed.__dict__.get("_fp_vz", 0) + 1
    ed.__dict__["_fp_vz"] = n
    ed._frei_vorlaeufig[key] = {**a, "_vorschau": FO.zeichnen("form", d, a["b"], a["h"]), "_vz": n}
    ed.viewport().update()


def maus(ed, e, art: str) -> bool:
    """True, wenn das Ereignis zum Bearbeiten der Punkte gehört (art: press, move, release, doppel)."""
    t = _eintrag(ed)
    if t is None:
        beenden(ed)
        return False
    key, a, r, _n = t
    pos = e.position()
    punkte = _punkte(ed, a)
    abb = _Abb(a, r)
    if art == "press":
        i = _punkt_bei(punkte, abb, pos)
        if e.button() == Qt.RightButton:
            if i is None:
                return False
            neu = FF.loeschen(punkte, i)
            if neu is not None:
                ed.__dict__["_fp_sel"] = None
                _speichern(ed, neu)
            return True
        if e.button() != Qt.LeftButton:
            return False
        if i is not None:
            ed.__dict__["_fp_sel"] = i
            ed.__dict__["_fp_zug"] = i
            ed.__dict__["_fp_arbeit"] = [list(x) for x in punkte]
            ed.viewport().update()
            return True
        x, y = abb.zu_anteil(pos)
        k = FF.naechste_kante(punkte, x, y, abb.rect.width(), abb.rect.height())
        if k is not None and k[0] <= KANTE:
            ed.__dict__["_fp_sel"] = None
            ed.viewport().update()
            return True                                                          # auf einer Kante: nichts beenden (Doppelklick fügt ein)
        beenden(ed)                                                              # Klick daneben: Modus aus, der Klick gilt normal weiter
        return False
    if art == "move":
        zug = ed.__dict__.get("_fp_zug")
        if zug is None or not (e.buttons() & Qt.LeftButton):
            return False
        x, y = abb.zu_anteil(pos)
        x, y = min(1.0, max(0.0, x)), min(1.0, max(0.0, y))
        arbeit = FF.verschieben(ed.__dict__["_fp_arbeit"], zug, x, y)
        ed.__dict__["_fp_arbeit"] = arbeit
        _vorschau(ed, key, a, arbeit)
        return True
    if art == "release":
        if ed.__dict__.get("_fp_zug") is None:
            return False
        arbeit = ed.__dict__["_fp_arbeit"]
        ed.__dict__["_fp_zug"] = None
        if arbeit != (a.get("daten") or {}).get("punkte"):
            _speichern(ed, arbeit)
        else:
            ed._frei_vorlaeufig.clear(); ed.__dict__["_fp_arbeit"] = None; ed.viewport().update()
        return True
    if art == "doppel":
        x, y = abb.zu_anteil(pos)
        if _punkt_bei(punkte, abb, pos) is not None:
            return True
        neu = FF.einfuegen(punkte, x, y, abb.rect.width(), abb.rect.height(), KANTE)
        if neu is None:
            return False
        ed.__dict__["_fp_sel"] = neu[1]
        _speichern(ed, neu[0])
        return True
    return False


def taste(ed, e) -> bool:
    """Esc beendet den Modus, Entf/Rücktaste löscht den gewählten Punkt (nie die ganze Form)."""
    if not aktiv(ed):
        return False
    if e.key() == Qt.Key_Escape:
        beenden(ed)
        return True
    if e.key() in (Qt.Key_Delete, Qt.Key_Backspace):
        t = _eintrag(ed)
        sel = ed.__dict__.get("_fp_sel")
        if t is not None and sel is not None:
            neu = FF.loeschen(_punkte(ed, t[1]), sel)
            if neu is not None:
                ed.__dict__["_fp_sel"] = None
                _speichern(ed, neu)
        return True
    return False
