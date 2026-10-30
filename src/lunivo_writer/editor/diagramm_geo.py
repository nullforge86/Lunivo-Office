"""Lage der Diagrammteile im gezeichneten Bild (aus der QtCharts-Geometrie nach dem Layout). Keine Oberfläche.

``geometrie`` füllt ein Wörterbuch Schlüssel → QRectF (Bildpunkte, logische Maße ``b`` × ``h``) und liefert zu jeder Reihe die Punkte
(``punkte``) für Fehlerindikatoren und Effekte. Schlüssel: ``diagrammbereich``, ``zeichnungsbereich``, ``titel``, ``legende``,
``achse_horizontal``, ``achse_vertikal``, ``reihe_<n>``, ``legendeneintrag_<n>``; ``balken_<n>`` = Liste der einzelnen Balken einer Reihe.
Die Nummer ``i`` ist die Stelle der Reihe in den gespeicherten Daten (nicht die Stelle nach dem Filtern)."""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QFontMetricsF


def _serie(ch, name: str):
    """Die Serie zur Datenreihe ``name`` (bei Säulen/Balken der Satz in der Serie); → (Serie, Satz oder None)."""
    for s in ch.series():
        if hasattr(s, "barSets"):
            for bs in s.barSets():
                if bs.label() == name:
                    return s, bs
        elif s.name() == name:
            return s, None
    return (ch.series()[0], None) if ch.series() else (None, None)


def punkte(ch, u: str, kategorien: list[str], werte: list[list[float]], namen: list[str]) -> list[list[tuple[float, float, float]]]:
    """Je Reihe die Punkte (x, y, Wert) in Bildpunkten, Säulen/Balken in der Mitte ihres Balkens. Gestapelte Typen: Oberkante des Stapels."""
    pa = ch.plotArea()
    out: list[list[tuple[float, float, float]]] = []
    n = max(1, len(kategorien))
    m = max(1, len(namen))
    waagrecht = u.startswith("balken")
    saeule = u.startswith(("saeule", "balken"))
    gruppiert = u in ("saeule_gruppiert", "balken_gruppiert")
    stapel = [0.0] * n
    for i, name in enumerate(namen):
        s, _bs = _serie(ch, name)
        reihe = []
        for j, v in enumerate(werte[i][:n]):
            wert = v
            if u.endswith("_gestapelt") or u.endswith("_100"):
                stapel[j] += v
                wert = stapel[j]
            if s is None:
                continue
            if waagrecht:
                ax = ch.axes(Qt.Horizontal)[0]
                lo, hi = ax.min(), ax.max()
                x = pa.left() + (wert - lo) / max(1e-9, hi - lo) * pa.width()
                y = pa.bottom() - (j + 0.5) * pa.height() / n
            else:
                p = ch.mapToPosition(QPointF(j + (1 if u.startswith("punkte") else 0), wert), s)
                x, y = p.x(), p.y()
                if gruppiert:
                    catw = pa.width() / n
                    gruppe = catw * s.barWidth()
                    x = pa.left() + (j + 0.5) * catw - gruppe / 2 + (i + 0.5) * gruppe / m
            reihe.append((x, y, v))
        out.append(reihe)
    return out


def _balken(ch, u: str, punkte_: list[tuple[float, float, float]], i: int, m: int, n: int) -> list[QRectF]:
    """Die einzelnen Balken einer Reihe (nur Säulen/Balken)."""
    pa = ch.plotArea()
    waagrecht = u.startswith("balken")
    cat = (pa.height() if waagrecht else pa.width()) / max(1, n)
    s = ch.series()[0]
    gruppe = cat * (s.barWidth() if hasattr(s, "barWidth") else 0.5)
    breite = gruppe / m if u.endswith("_gruppiert") else gruppe
    rects = []
    for x, y, _v in punkte_:
        if waagrecht:
            rects.append(QRectF(pa.left(), y - breite / 2, max(0.0, x - pa.left()), breite))
        else:
            rects.append(QRectF(x - breite / 2, y, breite, max(0.0, pa.bottom() - y)))
    return rects


def legenden_items(ch) -> list[tuple[QRectF, QRectF]]:
    """Je Eintrag der Legende (Rechteck des Eintrags, Rechteck des Beschriftungstextes) aus den Grafikelementen von QtCharts, in Bildpunkten;
    leer, wenn die Legende nichts hat. Die Reihenfolge ist die der Legendenzeichen."""
    from PySide6.QtWidgets import QGraphicsTextItem
    out = []
    for gruppe in ch.legend().childItems():
        for eintrag in gruppe.childItems():
            texte = [c for c in eintrag.childItems() if isinstance(c, QGraphicsTextItem)]
            if texte:
                out.append((QRectF(eintrag.sceneBoundingRect()), QRectF(texte[0].sceneBoundingRect())))
    return out


def titel_rect(ch) -> QRectF | None:
    """Das Rechteck des Titeltextes (QtCharts-Element), sonst None."""
    from PySide6.QtWidgets import QGraphicsTextItem
    for c in ch.childItems():
        if isinstance(c, QGraphicsTextItem) and c.toPlainText() == ch.title() and c.toPlainText():
            return QRectF(c.sceneBoundingRect())
    return None


def _legendeneintraege(ch, namen: list[str], r: QRectF) -> list[QRectF]:
    """Die Einträge der Legende: aus den Grafikelementen von QtCharts; ohne sie eine Näherung (nebeneinander oben/unten, untereinander links/rechts)."""
    echt = [e for e, _t in legenden_items(ch)]
    if echt:
        return echt
    lg = ch.legend()
    fm = QFontMetricsF(lg.font())
    ms = [m for m in lg.markers() if m.isVisible()]
    breiten = [fm.height() + 6 + fm.horizontalAdvance(m.label()) + 12 for m in ms]
    waagrecht = lg.alignment() in (Qt.AlignTop, Qt.AlignBottom)
    out = []
    if waagrecht:
        x = r.center().x() - sum(breiten) / 2
        for w in breiten:
            out.append(QRectF(x, r.top(), w, r.height())); x += w
    else:
        zh = fm.height() + 6
        y = r.center().y() - zh * len(ms) / 2
        for w in breiten:
            out.append(QRectF(r.left(), y, r.width(), zh)); y += zh
    return out


def geometrie(ch, u: str, kategorien: list[str], werte: list[list[float]], namen: list[str], nummern: list[int], b: float, h: float,
              titel: str, legende_an: bool, achsen_an: bool, legenden_namen: list[str]) -> dict:
    """Alle Teile → Rechteck (siehe Kopf); ``nummern`` = Stelle jeder sichtbaren Reihe in den gespeicherten Daten."""
    geo: dict = {"diagrammbereich": QRectF(0, 0, b, h)}
    pa = QRectF(ch.plotArea())
    geo["zeichnungsbereich"] = pa
    if titel:
        echt = titel_rect(ch)
        if echt is not None:
            geo["titel"] = echt
        else:
            fm = QFontMetricsF(ch.titleFont())
            w = fm.horizontalAdvance(titel) + 10
            geo["titel"] = QRectF((b - w) / 2, 6, w, fm.height() + 4)
    if legende_an:
        r = QRectF(ch.legend().geometry())
        geo["legende"] = r
        for k, eintrag in enumerate(_legendeneintraege(ch, legenden_namen, r)):
            geo[f"legendeneintrag_{k}"] = eintrag
    polar = u.startswith("netz")
    if achsen_an and not polar and u not in ("kreis", "ring"):
        geo["achse_horizontal"] = QRectF(pa.left(), pa.bottom(), pa.width(), max(14.0, min(24.0, h - pa.bottom() - 2)))
        geo["achse_vertikal"] = QRectF(max(0.0, pa.left() - 40), pa.top(), min(40.0, pa.left()), pa.height())
    if u in ("kreis", "ring") or polar or u.startswith(("kurs", "kombi")) or not namen:
        for nr in nummern:
            geo[f"reihe_{nr}"] = QRectF(pa)
        return geo
    pts = punkte(ch, u, kategorien, werte, namen)
    saeule = u.startswith(("saeule", "balken"))
    for k, nr in enumerate(nummern):
        if saeule:
            rects = _balken(ch, u, pts[k], k, len(namen), len(kategorien))
            geo[f"balken_{nr}"] = rects
            geo[f"reihe_{nr}"] = _vereinigung(rects) if rects else QRectF(pa)
        else:
            geo[f"reihe_{nr}"] = _umhuellung(pts[k], pa)
    return geo


def _vereinigung(rects: list[QRectF]) -> QRectF:
    r = QRectF(rects[0])
    for x in rects[1:]:
        r = r.united(x)
    return r


def _umhuellung(pts: list[tuple[float, float, float]], pa: QRectF) -> QRectF:
    if not pts:
        return QRectF(pa)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return QRectF(min(xs) - 6, min(ys) - 6, max(xs) - min(xs) + 12, max(ys) - min(ys) + 12).intersected(pa.adjusted(-6, -6, 6, 6))
