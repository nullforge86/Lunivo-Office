"""Zuschneiden frei positionierter Bilder — nicht zerstörend (die Bilddaten bleiben unverändert).

An der Angabe des Bildes (siehe ``freie_bilder``) stehen zwei Zusätze:
``zu`` = [links, oben, rechts, unten], jeweils als Anteil (0 bis 0,95) des ganzen Bildes, der abgeschnitten wird · ``maske`` = Name einer
Form aus ``formen_katalog`` (Nach Form zuschneiden). ``b``/``h`` der Angabe sind die Größe des sichtbaren Ausschnitts.
Gezeichnet wird der Ausschnitt über ``anzeige`` (``freie_bilder.objekte_der_seite``), also in Editor, Druck, PDF und Vorschau gleich.
Kein HTML: QImage und QPainter.
"""
from __future__ import annotations

from PySide6.QtCore import QRect, QRectF, Qt
from PySide6.QtGui import QBrush, QImage, QPainter

from lunivo_writer.editor import formen_katalog as K

GRENZE = 0.95                                                       # so viel darf höchstens (je Achse) abgeschnitten werden
VERHAELTNISSE = (("1:1", 1, 1), ("4:3", 4, 3), ("3:4", 3, 4), ("3:2", 3, 2), ("2:3", 2, 3), ("16:9", 16, 9), ("9:16", 9, 16),
                 ("16:10", 16, 10), ("5:4", 5, 4), ("21:9", 21, 9))
_MERK: dict = {}


def formen_kategorien() -> list[tuple[str, list[str]]]:
    """Die Formen zum Zuschneiden: (Kategorie, [Formnamen]) aus dem Formenkatalog, ohne Linien — für die Galerie."""
    return [(kat, [n for n in formen if not K.ist_linie(n)]) for kat, formen in K.KATEGORIEN if kat != "Linie"]


def lesen(a: dict) -> tuple[float, float, float, float]:
    """(links, oben, rechts, unten) als Anteile; ohne Zuschnitt (0, 0, 0, 0)."""
    zu = a.get("zu") or (0, 0, 0, 0)
    try:
        l, o, r, u = (max(0.0, min(GRENZE, float(x))) for x in zu)
    except (TypeError, ValueError):
        return 0.0, 0.0, 0.0, 0.0
    if l + r > GRENZE:
        r = max(0.0, GRENZE - l)
    if o + u > GRENZE:
        u = max(0.0, GRENZE - o)
    return l, o, r, u


def hat(a: dict) -> bool:
    return any(lesen(a)) or bool(a.get("maske"))


def anzeige(bild: QImage, a: dict) -> QImage:
    """Der sichtbare Ausschnitt von ``bild`` (mit Formmaske); ohne Zuschnitt und Maske das Bild selbst. Zwischengespeichert."""
    if bild is None or bild.isNull() or not hat(a):
        return bild
    zu, maske = lesen(a), a.get("maske") or ""
    if maske and (not K.hat(maske) or K.ist_linie(maske)):
        maske = ""
    schl = (id(bild), bild.cacheKey(), zu, maske)
    if schl in _MERK:
        return _MERK[schl][1]
    w, h = bild.width(), bild.height()
    l, o, r, u = zu
    rc = QRect(round(l * w), round(o * h), max(1, round(w * (1 - l - r))), max(1, round(h * (1 - o - u))))
    teil = bild.copy(rc)
    if maske:
        out = QImage(teil.size(), QImage.Format_ARGB32_Premultiplied); out.fill(Qt.transparent)
        p = QPainter(out); p.setRenderHint(QPainter.Antialiasing); p.setPen(Qt.NoPen); p.setBrush(QBrush(teil))
        p.drawPath(K.pfad(maske, QRectF(0, 0, teil.width(), teil.height())))
        p.end()
        teil = out
    if len(_MERK) > 24:
        _MERK.pop(next(iter(_MERK)))
    _MERK[schl] = (bild, teil)                                      # das Quellbild bleibt erhalten, damit die Kennung nicht neu vergeben wird
    return teil


# ---- Ändern ---------------------------------------------------------------------------------------------------------------------
def _quelle(ed, a: dict) -> QImage | None:
    from lunivo_writer.editor import freie_bilder as FB
    return FB.bild_im_dokument(ed.document(), a.get("n", ""))


def _skalen(a: dict) -> tuple[float, float]:
    """Anzeigepunkte je Anteil des ganzen Bildes (waagerecht, senkrecht)."""
    l, o, r, u = lesen(a)
    return float(a["b"]) / max(0.05, 1 - l - r), float(a["h"]) / max(0.05, 1 - o - u)


def setzen(ed, z, zu="__nicht__", maske="__nicht__", b: float | None = None, h: float | None = None) -> bool:
    """Zuschnitt ``zu`` = (links, oben, rechts, unten) als Anteile (None: Zuschnitt entfernen) und/oder Formmaske (``""``: entfernen); was nicht
    angegeben ist, bleibt. Die Größe des Bildes passt sich so an, dass der sichtbare Teil gleich groß bleibt (nichts wird gestaucht); ``b``/``h``
    überschreiben das."""
    from lunivo_writer.editor import bildlayout as BL
    if z is None or z[0] != "frei":
        return False
    a = z[2]
    if a.get("art") not in (None, "piktogramm"):
        return False
    sx, sy = _skalen(a)
    l0, o0, r0, u0 = lesen(a)
    neu = dict(a)
    if isinstance(zu, str):                                         # nicht angegeben
        l, o, r, u = l0, o0, r0, u0
    elif zu is None:
        l = o = r = u = 0.0
        neu.pop("zu", None)
    else:
        l, o, r, u = lesen({"zu": zu})
        if any((l, o, r, u)):
            neu["zu"] = [round(l, 5), round(o, 5), round(r, 5), round(u, 5)]
        else:
            neu.pop("zu", None)
    if maske != "__nicht__":
        if maske:
            neu["maske"] = maske
        else:
            neu.pop("maske", None)
    neu["b"] = float(b) if b is not None else max(8.0, sx * (1 - l - r))
    neu["h"] = float(h) if h is not None else max(8.0, sy * (1 - o - u))
    if b is None and not a.get("ah"):                               # der Bildinhalt bleibt an seinem Platz, der Rahmen wandert
        neu["xh"] = float(a.get("xh", 0.0)) + sx * (l - l0)
    if h is None and not a.get("av"):
        neu["yv"] = float(a.get("yv", 0.0)) + sy * (o - o0)
    BL._speichern_frei(ed, z[1], neu)
    return True


def skala(ed, z, breite: float, hoehe: float) -> bool:
    """Nach Skala (Seitenverhältnis) zuschneiden: der größte mittige Ausschnitt mit diesem Verhältnis; die Breite des Rahmens bleibt."""
    if z is None or z[0] != "frei" or breite <= 0 or hoehe <= 0:
        return False
    q = _quelle(ed, z[2])
    if q is None:
        return False
    w, h = float(q.width()), float(q.height())
    ziel = breite / hoehe
    if w / h > ziel:                                                # zu breit: seitlich beschneiden
        fx, fy = (h * ziel) / w, 1.0
    else:
        fx, fy = 1.0, (w / ziel) / h
    ax, ay = (1 - fx) / 2, (1 - fy) / 2
    b = float(z[2]["b"])
    return setzen(ed, z, (ax, ay, ax, ay), b=b, h=b * hoehe / breite)


def skala_text(ed, z, text) -> bool:
    """``"16:9"`` (oder ``(16, 9)``) → ``skala``."""
    if isinstance(text, (tuple, list)):
        return skala(ed, z, float(text[0]), float(text[1]))
    try:
        s = str(text).replace("/", ":").split(":")
        return skala(ed, z, float(s[0]), float(s[1]))
    except (ValueError, IndexError):
        return False


def form(ed, z, name: str) -> bool:
    """Nach Form zuschneiden: der Ausschnitt wird in die Form (Name aus dem Formenkatalog) eingepasst; Zuschnitt bleibt."""
    if not K.hat(name) or K.ist_linie(name):
        return False
    return setzen(ed, z, maske=name)


def zuruecksetzen(ed, z) -> bool:
    """Form und Größe zurücksetzen: Maske und Zuschnitt weg, das ganze Bild in der bisherigen Breite im ursprünglichen Seitenverhältnis."""
    if z is None or z[0] != "frei":
        return False
    q = _quelle(ed, z[2])
    if q is None:
        return False
    b = float(z[2]["b"]) / max(0.05, 1 - lesen(z[2])[0] - lesen(z[2])[2])
    return setzen(ed, z, zu=None, maske="", b=b, h=b * q.height() / max(1, q.width()))


def aus_ziehen(a0: dict, neu: dict, griff: str) -> dict:
    """Zuschneiden durch Ziehen an einem Griff: ``a0`` die Angabe vor dem Ziehen, ``neu`` die mit der gezogenen Größe (``b``, ``h``).
    Der Bildinhalt bleibt an seinem Platz; Ziehen nach innen schneidet ab, nach außen holt Abgeschnittenes zurück (höchstens bis zum Bildrand).
    → die Angabe mit neuem ``zu``, ``b``, ``h`` (und Versatz)."""
    sx, sy = _skalen(a0)
    l, o, r, u = lesen(a0)
    db, dh = float(a0["b"]) - float(neu["b"]), float(a0["h"]) - float(neu["h"])            # > 0: kleiner geworden
    out = dict(neu)
    if "w" in griff:
        l = max(0.0, min(GRENZE - r, l + db / sx))
    if "e" in griff:
        r = max(0.0, min(GRENZE - l, r + db / sx))
    if "n" in griff:
        o = max(0.0, min(GRENZE - u, o + dh / sy))
    if "s" in griff:
        u = max(0.0, min(GRENZE - o, u + dh / sy))
    nb, nh = max(8.0, sx * (1 - l - r)), max(8.0, sy * (1 - o - u))
    if "w" in griff:
        out["xh"] = float(neu.get("xh", 0.0)) + (float(neu["b"]) - nb)                    # die linke Kante liegt dort, wo sie nach dem Abschneiden liegt
    if "n" in griff:
        out["yv"] = float(neu.get("yv", 0.0)) + (float(neu["h"]) - nh)
    out["b"], out["h"] = nb, nh
    if any((l, o, r, u)):
        out["zu"] = [round(l, 5), round(o, 5), round(r, 5), round(u, 5)]
    else:
        out.pop("zu", None)
    return out
