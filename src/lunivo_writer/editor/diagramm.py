"""Diagramme als Bild (Einfügen ▸ Diagramm), gezeichnet mit QtCharts. Keine Oberfläche.

    bild("saeule_gestapelt", "Umsatz", ["Q1", "Q2"], {"Nord": [3, 4], "Süd": [2, 5]})   # → QImage

``TYPEN`` ordnet die Untertypen den Gruppen der linken Liste im Fenster zu (wie in der Vorlage: Säule, Linie, Kreis, Balken, Fläche, X Y (Punkt),
Kurs, Netz, Kombination, Vorlagen).

Kombination: ``kombi`` = [(Reihentyp aus ``KOMBI_TYPEN``, Sekundärachse)] je Datenreihe; ``kombi_vorgabe`` liefert die Belegung der
fertigen Kombinationen. Vorlagen: ``VORLAGEN`` = Name → (Untertyp, Farben); ``bild`` nimmt die Farben über ``farben``.
Kurs: Höchst = größter, Tiefst = kleinster Wert der Rubrik, Schluss = letzte, Eröffnung = erste Datenreihe.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPen
from PySide6.QtWidgets import QGraphicsScene

# (Gruppe, Symbol aus symbole.json, [(Untertyp, Name)])
TYPEN = [
    ("Säule", "saeule", [("saeule_gruppiert", "Gruppierte Säule"), ("saeule_gestapelt", "Gestapelte Säule"),
                         ("saeule_100", "100 % gestapelte Säule")]),
    ("Linie", "linie", [("linie", "Linie"), ("linie_punkte", "Linie mit Datenpunkten"), ("linie_glatt", "Geglättete Linie")]),
    ("Kreis", "kreis", [("kreis", "Kreis"), ("ring", "Ring")]),
    ("Balken", "balkenquer", [("balken_gruppiert", "Gruppierte Balken"), ("balken_gestapelt", "Gestapelte Balken"),
                              ("balken_100", "100 % gestapelte Balken")]),
    ("Fläche", "flaeche", [("flaeche", "Fläche"), ("flaeche_gestapelt", "Gestapelte Fläche")]),
    ("X Y (Punkt)", "punktwolke", [("punkte", "Punkt"), ("punkte_linien", "Punkt mit Linien")]),
    ("Kurs", "kurs", [("kurs_hts", "Höchst-Tiefst-Schluss"), ("kurs_ohts", "Eröffnung-Höchst-Tiefst-Schluss")]),
    ("Netz", "netz", [("netz", "Netz"), ("netz_punkte", "Netz mit Datenpunkten"), ("netz_gefuellt", "Gefülltes Netz")]),
    ("Kombination", "kombination", [("kombination", "Gruppierte Säulenlinie"),
                                    ("kombi_sekundaer", "Gruppierte Säule - Linie auf Sekundärachse"),
                                    ("kombi_flaeche", "Gestapelte Fläche - Gruppierte Säule"),
                                    ("kombi_eigen", "Benutzerdefinierte Kombination")]),
    ("Vorlagen", "vorlagen", [("vorlage_klar", "Klar"), ("vorlage_blau", "Blautöne"), ("vorlage_gruen", "Grüntöne"),
                              ("vorlage_warm", "Warme Farben"), ("vorlage_grau", "Graustufen"), ("vorlage_kreis", "Kreis bunt")]),
]
# Reihentypen der Kombination (Spalte „Diagrammtyp“ im Fenster)
KOMBI_TYPEN = [("saeule", "Gruppierte Säule"), ("saeule_gestapelt", "Gestapelte Säule"), ("linie", "Linie"),
               ("linie_punkte", "Linie mit Datenpunkten"), ("flaeche", "Fläche"), ("flaeche_gestapelt", "Gestapelte Fläche")]
# Vorlagen: fertige Farbreihen zu einer Diagrammart
VORLAGEN = {
    "vorlage_klar": ("saeule_gruppiert", ["#4a8fd8", "#ef8a3c", "#9aa0a6", "#f2b705", "#2f6fb5", "#5aa454"]),
    "vorlage_blau": ("saeule_gruppiert", ["#1c4f8c", "#3a7bd5", "#7fb0ea", "#b9d4f5", "#0e2f57", "#5c93d8"]),
    "vorlage_gruen": ("linie_punkte", ["#2b7a3d", "#5aa454", "#9bcf8b", "#1d4f28", "#77b86a", "#c4e3b9"]),
    "vorlage_warm": ("balken_gruppiert", ["#c0392b", "#e67e22", "#f1c40f", "#d35400", "#e74c3c", "#f39c12"]),
    "vorlage_grau": ("flaeche", ["#3c4043", "#80868b", "#bdc1c6", "#5f6368", "#9aa0a6", "#dadce0"]),
    "vorlage_kreis": ("kreis", ["#4a8fd8", "#ef8a3c", "#5aa454", "#f2b705", "#9b59b6", "#e74c3c"]),
}
NAMEN = {u: n for _g, _s, unter in TYPEN for u, n in unter}
# Beispieldaten, mit denen das Fenster öffnet (wie in der Vorlage: vier Rubriken, drei Datenreihen)
BEISPIEL_KATEGORIEN = ["Rubrik 1", "Rubrik 2", "Rubrik 3", "Rubrik 4"]
BEISPIEL_REIHEN = {"Datenreihe 1": [4.1, 2.8, 3.3, 4.6], "Datenreihe 2": [2.6, 4.2, 1.7, 2.9], "Datenreihe 3": [1.9, 2.2, 3.1, 4.8]}
FARBEN = ["#4a8fd8", "#ef8a3c", "#9aa0a6", "#f2b705", "#2f6fb5", "#5aa454"]
# frühere Namen (gespeicherte Diagramme, ältere Aufrufe)
ALT = {"Säulen": "saeule_gruppiert", "Balken": "balken_gruppiert", "Linie": "linie", "Kreis": "kreis"}


_PALETTE = FARBEN


def _farbe(i: int) -> QColor:
    return QColor(_PALETTE[i % len(_PALETTE)])


def kombi_vorgabe(untertyp: str, anzahl: int) -> list[tuple[str, bool]]:
    """Belegung der Kombinationstabelle für eine fertige Kombination (die letzte Reihe ist Linie bzw. Säule)."""
    if anzahl <= 0:
        return []
    if untertyp == "kombi_flaeche":
        return [("flaeche_gestapelt", False)] * max(1, anzahl - 1) + [("saeule", False)] * (anzahl > 1)
    letzte = ("linie", untertyp == "kombi_sekundaer")
    return [("saeule", False)] * max(1, anzahl - 1) + [letzte] * (anzahl > 1)


def bild(untertyp: str, titel: str, kategorien: list[str], reihen: dict[str, list[float]], b: int = 640, h: int = 400,
         legende: bool = True, kombi: list[tuple[str, bool]] | None = None, farben: list[str] | None = None,
         kachel: bool = False) -> QImage:
    """``kachel``: kleines Bildchen ohne Beschriftung, Titel und Legende (Untertypen im Fenster)."""
    global _PALETTE
    if untertyp in VORLAGEN:
        untertyp, farben = VORLAGEN[untertyp][0], farben or VORLAGEN[untertyp][1]
    _PALETTE = list(farben or FARBEN)
    try:
        return _bild(untertyp, "" if kachel else titel, kategorien, reihen, b, h, legende and not kachel, kombi, kachel)
    finally:
        _PALETTE = FARBEN


def _bild(untertyp, titel, kategorien, reihen, b, h, legende, kombi, kachel=False) -> QImage:
    from PySide6.QtCharts import (
        QAreaSeries, QBarCategoryAxis, QBarSeries, QBarSet, QCategoryAxis, QChart, QHorizontalBarSeries,
        QHorizontalPercentBarSeries, QHorizontalStackedBarSeries, QLineSeries, QPercentBarSeries, QPieSeries, QPolarChart, QScatterSeries,
        QSplineSeries, QStackedBarSeries, QValueAxis, QCandlestickSeries, QCandlestickSet,
    )
    u = ALT.get(untertyp, untertyp)
    ch = QPolarChart() if u.startswith("netz") else QChart()
    ch.setTitle(titel); ch.setAnimationOptions(QChart.NoAnimation); ch.setBackgroundRoundness(0)
    namen = list(reihen)
    werte = [[float(v) for v in reihen[n]] for n in namen]
    gestapelt = u.endswith("_gestapelt")
    if gestapelt and werte:
        hoechst = max((sum(w[j] for w in werte if j < len(w)) for j in range(max(len(w) for w in werte))), default=1.0)
    else:
        hoechst = max((max(w) for w in werte if w), default=1.0)

    def achsen(serie_liste, waagrecht: bool = False, kategorie: bool = True):
        ax = QBarCategoryAxis() if kategorie else QValueAxis()
        if kategorie:
            ax.append(kategorien)
        ay = QValueAxis()
        ch.addAxis(ax, Qt.AlignLeft if waagrecht else Qt.AlignBottom)
        ch.addAxis(ay, Qt.AlignBottom if waagrecht else Qt.AlignLeft)
        for s in serie_liste:
            s.attachAxis(ax); s.attachAxis(ay)
        if u.endswith("_100"):
            ay.setRange(0, 100)
        else:
            ay.setRange(min(0.0, min((min(w) for w in werte if w), default=0.0)), max(hoechst, 1e-9))
            ay.applyNiceNumbers()                               # 0 … 5 statt 0 … 4,8
        return ax, ay

    if u in ("kreis", "ring"):
        s = QPieSeries()
        if u == "ring":
            s.setHoleSize(0.45)
        for i, (k, v) in enumerate(zip(kategorien, werte[0] if werte else [])):
            sl = s.append(k, v); sl.setColor(_farbe(i)); sl.setLabelVisible(not legende); sl.setLabel(k)
        ch.addSeries(s)
    elif u == "kombination" or u.startswith("kombi_"):
        _kombination(ch, kombi or kombi_vorgabe(u, len(namen)), namen, werte, kategorien)
    elif u.startswith("kurs"):
        s = QCandlestickSeries(); s.setIncreasingColor(QColor("#ffffff")); s.setDecreasingColor(_farbe(0))
        s.setBodyWidth(0.25 if u == "kurs_ohts" else 0.04); s.setPen(QPen(QColor("#3c4043"), 1.5)); s.setName("Kurs")
        for j in range(len(kategorien)):
            spalte = [w[j] for w in werte if j < len(w)] or [0.0]
            schluss = spalte[-1]
            auf = spalte[0] if u == "kurs_ohts" else schluss
            s.append(QCandlestickSet(auf, max(spalte), min(spalte), schluss, float(j)))
        ch.addSeries(s)
        ax = QBarCategoryAxis(); ax.append(kategorien); ay = QValueAxis()
        ch.addAxis(ax, Qt.AlignBottom); ch.addAxis(ay, Qt.AlignLeft); s.attachAxis(ax); s.attachAxis(ay)
        tief = min((min(w) for w in werte if w), default=0.0)
        ay.setRange(min(0.0, tief), max(hoechst, 1e-9)); ay.applyNiceNumbers()
    elif u.startswith(("saeule", "balken")):
        klasse = {"saeule_gruppiert": QBarSeries, "saeule_gestapelt": QStackedBarSeries, "saeule_100": QPercentBarSeries,
                  "balken_gruppiert": QHorizontalBarSeries, "balken_gestapelt": QHorizontalStackedBarSeries,
                  "balken_100": QHorizontalPercentBarSeries}[u]
        s = klasse()
        for i, n in enumerate(namen):
            bs = QBarSet(n); bs.setColor(_farbe(i)); bs.setBorderColor(_farbe(i))
            for v in werte[i]:
                bs.append(v)
            s.append(bs)
        ch.addSeries(s)
        achsen([s], waagrecht=u.startswith("balken"))
    elif u.startswith("flaeche"):
        unten = [0.0] * len(kategorien)
        serien = []
        for i, n in enumerate(namen):
            oben = [(unten[j] if u == "flaeche_gestapelt" else 0.0) + v for j, v in enumerate(werte[i])]
            hoch, tief = QLineSeries(), QLineSeries()
            for j, v in enumerate(oben):
                hoch.append(j, v); tief.append(j, unten[j] if u == "flaeche_gestapelt" else 0.0)
            a = QAreaSeries(hoch, tief); a.setName(n)
            hoch.setParent(a); tief.setParent(a)                # QAreaSeries übernimmt die Linien nicht selbst
            c = _farbe(i); c.setAlpha(200 if u == "flaeche_gestapelt" else 150); a.setColor(c); a.setBorderColor(_farbe(i))
            ch.addSeries(a); serien.append(a)
            if u == "flaeche_gestapelt":
                unten = oben
        ax = QCategoryAxis(); ax.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
        for j, k in enumerate(kategorien):
            ax.append(k, j)
        ax.setRange(0, max(1, len(kategorien) - 1))
        ay = QValueAxis(); ch.addAxis(ax, Qt.AlignBottom); ch.addAxis(ay, Qt.AlignLeft)
        for a in serien:
            a.attachAxis(ax); a.attachAxis(ay)
        ay.setRange(0, max(hoechst, 1e-9)); ay.applyNiceNumbers()
    elif u.startswith("punkte"):
        serien = []
        for i, n in enumerate(namen):
            s = QScatterSeries(); s.setName(n); s.setColor(_farbe(i)); s.setMarkerSize(9); s.setBorderColor(_farbe(i))
            for j, v in enumerate(werte[i]):
                s.append(j + 1, v)
            ch.addSeries(s); serien.append(s)
            if u == "punkte_linien":
                ls = QLineSeries(); ls.setPen(QPen(_farbe(i), 2))
                for j, v in enumerate(werte[i]):
                    ls.append(j + 1, v)
                ch.addSeries(ls); serien.append(ls)
                ch.legend().markers(ls)[0].setVisible(False)
        ax, _ay = achsen(serien, kategorie=False)
        ax.setRange(0, len(kategorien) + 1); ax.setTickCount(len(kategorien) + 2); ax.setLabelFormat("%d")
    elif u.startswith("netz"):
        winkel = QCategoryAxis(); winkel.setRange(0, len(kategorien)); winkel.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
        for j, k in enumerate(kategorien):
            winkel.append(k, j)
        radius = QValueAxis(); radius.setLabelFormat("%.0f"); radius.setRange(0, max(hoechst, 1e-9)); radius.applyNiceNumbers()
        ch.addAxis(winkel, QPolarChart.PolarOrientationAngular); ch.addAxis(radius, QPolarChart.PolarOrientationRadial)
        for i, n in enumerate(namen):
            ls = QLineSeries(); ls.setName(n); ls.setPen(QPen(_farbe(i), 2)); ls.setPointsVisible(u == "netz_punkte")
            for j, v in enumerate(werte[i] + werte[i][:1]):
                ls.append(QPointF(j, v))
            if u == "netz_gefuellt":
                null = QLineSeries()
                for j in range(len(werte[i]) + 1):
                    null.append(QPointF(j, 0))
                a = QAreaSeries(ls, null); a.setName(n); ls.setParent(a); null.setParent(a)
                c = _farbe(i); c.setAlpha(110); a.setColor(c); a.setBorderColor(_farbe(i))
                ch.addSeries(a); a.attachAxis(winkel); a.attachAxis(radius)
                continue
            ch.addSeries(ls); ls.attachAxis(winkel); ls.attachAxis(radius)
    else:                                                       # Linien
        serien = []
        for i, n in enumerate(namen):
            s = QSplineSeries() if u == "linie_glatt" else QLineSeries()
            s.setName(n); s.setPen(QPen(_farbe(i), 2.5)); s.setPointsVisible(u == "linie_punkte")
            for j, v in enumerate(werte[i]):
                s.append(j, v)
            ch.addSeries(s); serien.append(s)
        achsen(serien)
    ch.legend().setVisible(legende); ch.legend().setAlignment(Qt.AlignBottom)
    if kachel:
        ch.setMargins(__import__("PySide6.QtCore", fromlist=["QMargins"]).QMargins(2, 2, 2, 2))
        for achse in ch.axes():
            achse.setLabelsVisible(False); achse.setGridLineVisible(False)
        for serie in ch.series():
            if hasattr(serie, "setLabelsVisible"):
                serie.setLabelsVisible(False)
    # ohne sichtbares Fenster: das Diagramm in eine eigene Szene setzen, auf die Bildgröße bringen und die Szene malen
    szene = QGraphicsScene(); szene.addItem(ch)
    ch.setPos(0, 0); ch.resize(b, h)
    szene.setSceneRect(QRectF(0, 0, b, h))
    img = QImage(b, h, QImage.Format_ARGB32); img.fill(QColor("white"))
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing); szene.render(p, QRectF(0, 0, b, h), QRectF(0, 0, b, h)); p.end()
    szene.removeItem(ch)
    return img


def _kombination(ch, kombi: list[tuple[str, bool]], namen: list[str], werte: list[list[float]], kategorien: list[str]) -> None:
    """Jede Reihe mit eigenem Typ; Reihen mit Sekundärachse an einer zweiten Werteachse rechts."""
    from PySide6.QtCharts import QAreaSeries, QBarCategoryAxis, QBarSeries, QBarSet, QLineSeries, QStackedBarSeries, QValueAxis
    kombi = list(kombi) + [("saeule", False)] * (len(namen) - len(kombi))
    ax = QBarCategoryAxis(); ax.append(kategorien); ch.addAxis(ax, Qt.AlignBottom)
    links, rechts = QValueAxis(), QValueAxis()
    ch.addAxis(links, Qt.AlignLeft)
    zuordnung: list[tuple[object, bool]] = []
    hoch = {False: 0.0, True: 0.0}
    for sek in (False, True):
        for art, klasse in (("saeule", QBarSeries), ("saeule_gestapelt", QStackedBarSeries)):
            idx = [i for i, (t, s2) in enumerate(kombi) if t == art and s2 == sek]
            if not idx:
                continue
            s = klasse()
            for i in idx:
                bs = QBarSet(namen[i]); bs.setColor(_farbe(i)); bs.setBorderColor(_farbe(i))
                for v in werte[i]:
                    bs.append(v)
                s.append(bs)
            ch.addSeries(s); zuordnung.append((s, sek))
            h = (max((sum(werte[i][j] for i in idx if j < len(werte[i])) for j in range(len(kategorien))), default=0.0)
                 if art == "saeule_gestapelt" else max((max(werte[i]) for i in idx if werte[i]), default=0.0))
            hoch[sek] = max(hoch[sek], h)
        unten = [0.0] * len(kategorien)
        for i, (t, s2) in enumerate(kombi):
            if s2 != sek or not t.startswith("flaeche"):
                continue
            gest = t == "flaeche_gestapelt"
            oben = [(unten[j] if gest else 0.0) + v for j, v in enumerate(werte[i])]
            o, u2 = QLineSeries(), QLineSeries()
            for j, v in enumerate(oben):
                o.append(j, v); u2.append(j, unten[j] if gest else 0.0)
            a = QAreaSeries(o, u2); a.setName(namen[i]); o.setParent(a); u2.setParent(a)
            c = _farbe(i); c.setAlpha(170); a.setColor(c); a.setBorderColor(_farbe(i))
            ch.addSeries(a); zuordnung.append((a, sek)); hoch[sek] = max(hoch[sek], max(oben, default=0.0))
            if gest:
                unten = oben
        for i, (t, s2) in enumerate(kombi):
            if s2 != sek or not t.startswith("linie"):
                continue
            ls = QLineSeries(); ls.setName(namen[i]); ls.setPen(QPen(_farbe(i), 2.5)); ls.setPointsVisible(t == "linie_punkte")
            for j, v in enumerate(werte[i]):
                ls.append(j, v)
            ch.addSeries(ls); zuordnung.append((ls, sek)); hoch[sek] = max(hoch[sek], max(werte[i], default=0.0))
    if any(sek for _s, sek in zuordnung):
        ch.addAxis(rechts, Qt.AlignRight)
    for s, sek in zuordnung:
        s.attachAxis(ax); s.attachAxis(rechts if sek else links)
    for achse, sek in ((links, False), (rechts, True)):
        achse.setRange(0, max(hoch[sek], 1e-9)); achse.applyNiceNumbers()
