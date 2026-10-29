"""Diagramm: Elemente (Diagrammelemente-Liste), Teilformate und Zusätze, die QtCharts nicht selbst zeichnet. Keine Oberfläche.

Die Daten des Diagramms (``a["daten"]``) kennen zusätzlich zu den Angaben aus ``editor/diagramm.py``:
``elemente``      {achsen, achsentitel, datentabelle, fehlerindikatoren, gitter, trendlinie: bool} — fehlt ein Schlüssel, gilt ``STANDARD_ELEMENTE``;
                  Titel, Legende (mit Lage) und Datenbeschriftungen liegen weiter in ``titel_an``, ``legende``/``legende_pos``, ``labels``;
``ausgeblendet``  {"reihen": [Namen], "rubriken": [Namen]} (Diagrammfilter);
``teil_format``   Teil-Schlüssel → {fuell, linie, schatten, reflektion, leuchten, weich, d3, drehung, text, achse, reihe} (jeder Schlüssel darf fehlen,
                  Aufbau in ``diagramm_format``);
``teil``          der gewählte Diagrammteil (Schlüssel wie in ``diagramm.teile``); ``alt_titel``/``alt_beschreibung``: Alternativtext."""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QFontMetricsF, QPainter, QPen

ELEMENTE = ("achsen", "achsentitel", "titel", "datenbeschriftung", "datentabelle", "fehlerindikatoren", "gitter", "legende", "trendlinie")
ELEMENT_NAMEN = {"achsen": "Achsen", "achsentitel": "Achsentitel", "titel": "Diagrammtitel", "datenbeschriftung": "Datenbeschriftungen",
                 "datentabelle": "Datentabelle", "fehlerindikatoren": "Fehlerindikatoren", "gitter": "Gitternetzlinien", "legende": "Legende",
                 "trendlinie": "Trendlinie"}
STANDARD_ELEMENTE = {"achsen": True, "achsentitel": False, "datentabelle": False, "fehlerindikatoren": False, "gitter": True, "trendlinie": False}
LEGENDEN_LAGEN = ("oben", "unten", "links", "rechts")
FEHLER_ANTEIL = 0.1                  # Fehlerindikatoren: feste Balken ± 10 % des größten Wertes
TABELLE_ZEILE = 20.0                 # Höhe einer Zeile der Datentabelle in Bildpunkten


def elemente_wirksam(d: dict) -> dict:
    """Alle neun Elemente mit ihrem Wert: Wahrheitswerte, bei ``legende`` die Lage (``oben`` … ``rechts``) oder ``aus``."""
    el = {**STANDARD_ELEMENTE, **(d.get("elemente") or {})}
    el["titel"] = bool(d.get("titel_an", True))
    el["datenbeschriftung"] = bool(d.get("labels", False))
    el["legende"] = d.get("legende_pos", "unten") if d.get("legende", True) else "aus"
    return el


def trend(werte: list[float]) -> tuple[float, float]:
    """Lineare Regression y = a + b·x über x = 0 … n-1 → (a, b)."""
    n = len(werte)
    if n < 2:
        return (werte[0] if werte else 0.0), 0.0
    mx, my = (n - 1) / 2, sum(werte) / n
    s = sum((x - mx) ** 2 for x in range(n))
    b = sum((x - mx) * (v - my) for x, v in enumerate(werte)) / s
    return my - b * mx, b


def stift(linie: dict | None, standard_farbe: str = "#3c4043") -> QPen:
    """Stift aus {farbe, breite (Bildpunkte), art}; die Strichart kommt aus ``freie_bilder._stift`` (dieselbe wie bei Bildern und Formen)."""
    from lunivo_writer.editor import freie_bilder as FB
    linie = linie or {}
    return FB._stift({"b": float(linie.get("breite", 1.0)), "farbe": linie.get("farbe", standard_farbe), "art": linie.get("art", "einfach")})


def schrift_aus(basis: QFont, text: dict | None) -> QFont:
    from lunivo_writer.editor import diagramm_format as F
    return F.schrift_aus(basis, text)


# ---- Zeichnen im fertigen Bild ---------------------------------------------------------------------------------------------------
def hintergruende(p: QPainter, geo: dict, tf: dict, grund: QColor | None = None) -> None:
    """Füllung und Effekte von Diagrammbereich, Zeichnungsbereich, Titel, Legende und Reihen — unter dem Diagramm (``diagramm_format``).
    Die Effekte des Diagrammbereichs liegen am Objekt selbst (``a["fx"]``), nicht hier."""
    from lunivo_writer.editor import diagramm_format as F
    grund = grund or QColor("white")
    for teil in ("diagrammbereich", "zeichnungsbereich", "legende", "titel"):
        fmt, r = tf.get(teil) or {}, geo.get(teil)
        if r is None or not fmt:
            continue
        if teil == "diagrammbereich":
            F.flaeche_zeichnen(p, r, fmt.get("fuell"))
        else:
            F.teil_zeichnen(p, r, fmt, grund)
    for schl, fmt in tf.items():
        if schl.startswith("reihe_") and F.fx_normal(fmt):
            farbe = QColor(F.hauptfarbe(fmt.get("fuell")) or "#4a8fd8")
            for r in geo.get("balken_" + schl[6:], []):
                F.teil_zeichnen(p, r, {"fuell": {"art": "farbe", "farbe": farbe.name()}, **{k: v for k, v in fmt.items() if k in F.FX_NUR_HINTER}}, grund, True)


def linien(p: QPainter, geo: dict, tf: dict) -> None:
    """Die Linien (Rahmen) der Teile mit ``linie`` — über dem Diagramm."""
    from lunivo_writer.editor import diagramm_format as F
    p.setBrush(Qt.NoBrush)
    for teil in ("diagrammbereich", "zeichnungsbereich", "legende", "titel"):
        fmt, r = tf.get(teil) or {}, geo.get(teil)
        if r is not None and fmt.get("linie"):
            F.rahmen_zeichnen(p, r, fmt["linie"])


def fehlerindikatoren(p: QPainter, ch, u: str, pts: list[list[tuple[float, float, float]]], hoechst: float, farbe: QColor) -> None:
    """Feste Balken ± ``FEHLER_ANTEIL`` des Höchstwerts an jedem Punkt (nicht bei Balken, Kreis, Netz und gestapelten Typen)."""
    if u.startswith(("balken", "kreis", "ring", "netz")) or u.endswith(("_gestapelt", "_100")) or not ch.axes(Qt.Vertical):
        return
    ax = ch.axes(Qt.Vertical)[0]
    if not hasattr(ax, "max"):
        return
    pa = ch.plotArea()
    px = pa.height() / max(1e-9, ax.max() - ax.min())
    d = hoechst * FEHLER_ANTEIL * px
    p.setPen(QPen(farbe, 1.4))
    for reihe in pts:
        for x, y, _v in reihe:
            p.drawLine(QPointF(x, y - d), QPointF(x, y + d))
            p.drawLine(QPointF(x - 4, y - d), QPointF(x + 4, y - d))
            p.drawLine(QPointF(x - 4, y + d), QPointF(x + 4, y + d))


def tabelle(p: QPainter, r: QRectF, kategorien: list[str], namen: list[str], werte: list[list[float]], farben: list[QColor], schrift: QColor) -> None:
    """Datentabelle: Kopfzeile mit den Rubriken, darunter je Reihe ein Farbfeld, der Name und die Werte."""
    f = QFont(p.font()); f.setPointSizeF(8.5); p.setFont(f)
    fm = QFontMetricsF(f)
    namens_b = min(r.width() * 0.3, max([fm.horizontalAdvance(n) for n in namen] + [30.0]) + 26)
    spalten = max(1, len(kategorien))
    sb = (r.width() - namens_b) / spalten
    p.setPen(QPen(schrift, 0.8)); p.setBrush(Qt.NoBrush)
    p.drawRect(r)
    for z in range(1, len(namen) + 1):
        p.drawLine(QPointF(r.left(), r.top() + z * TABELLE_ZEILE), QPointF(r.right(), r.top() + z * TABELLE_ZEILE))
    for s in range(spalten + 1):
        x = r.left() + (namens_b if s else 0) + max(0, s - 1) * sb
        p.drawLine(QPointF(x, r.top()), QPointF(x, r.bottom()))
    for j, k in enumerate(kategorien):
        p.drawText(QRectF(r.left() + namens_b + j * sb, r.top(), sb, TABELLE_ZEILE), Qt.AlignCenter, fm.elidedText(k, Qt.ElideRight, int(sb) - 4))
    for i, n in enumerate(namen):
        y = r.top() + (i + 1) * TABELLE_ZEILE
        p.setPen(Qt.NoPen); p.setBrush(farben[i % len(farben)]); p.drawRect(QRectF(r.left() + 5, y + 6, 8, 8))
        p.setPen(QPen(schrift)); p.drawText(QRectF(r.left() + 17, y, namens_b - 19, TABELLE_ZEILE), Qt.AlignVCenter | Qt.AlignLeft,
                                            fm.elidedText(n, Qt.ElideRight, int(namens_b) - 21))
        for j in range(len(kategorien)):
            if j < len(werte[i]):
                p.drawText(QRectF(r.left() + namens_b + j * sb, y, sb, TABELLE_ZEILE), Qt.AlignCenter, f"{werte[i][j]:g}")
