"""Diagramme als Bild (Einfügen ▸ Diagramm), gezeichnet mit QtCharts. Keine Oberfläche.

    bild("saeule_gestapelt", "Umsatz", ["Q1", "Q2"], {"Nord": [3, 4], "Süd": [2, 5]})   # → QImage

``TYPEN`` ordnet die Untertypen den Gruppen der linken Liste im Fenster zu (wie in der Vorlage: Säule, Linie, Kreis, Balken, Fläche, X Y (Punkt),
Kurs, Netz, Kombination). Eine Gruppe ohne Untertypen ist in Lunivo noch nicht möglich und bleibt im Fenster grau.
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
    ("Kurs", "kurs", []),
    ("Netz", "netz", [("netz", "Netz")]),
    ("Kombination", "kombination", [("kombination", "Gruppierte Säule und Linie")]),
]
NAMEN = {u: n for _g, _s, unter in TYPEN for u, n in unter}
# Beispieldaten, mit denen das Fenster öffnet (wie in der Vorlage: vier Rubriken, drei Datenreihen)
BEISPIEL_KATEGORIEN = ["Rubrik 1", "Rubrik 2", "Rubrik 3", "Rubrik 4"]
BEISPIEL_REIHEN = {"Datenreihe 1": [4.1, 2.8, 3.3, 4.6], "Datenreihe 2": [2.6, 4.2, 1.7, 2.9], "Datenreihe 3": [1.9, 2.2, 3.1, 4.8]}
FARBEN = ["#4a8fd8", "#ef8a3c", "#9aa0a6", "#f2b705", "#2f6fb5", "#5aa454"]
# frühere Namen (gespeicherte Diagramme, ältere Aufrufe)
ALT = {"Säulen": "saeule_gruppiert", "Balken": "balken_gruppiert", "Linie": "linie", "Kreis": "kreis"}


def _farbe(i: int) -> QColor:
    return QColor(FARBEN[i % len(FARBEN)])


def bild(untertyp: str, titel: str, kategorien: list[str], reihen: dict[str, list[float]], b: int = 640, h: int = 400,
         legende: bool = True) -> QImage:
    from PySide6.QtCharts import (
        QAreaSeries, QBarCategoryAxis, QBarSeries, QBarSet, QCategoryAxis, QChart, QHorizontalBarSeries,
        QHorizontalPercentBarSeries, QHorizontalStackedBarSeries, QLineSeries, QPercentBarSeries, QPieSeries, QPolarChart, QScatterSeries,
        QSplineSeries, QStackedBarSeries, QValueAxis,
    )
    u = ALT.get(untertyp, untertyp)
    ch = QPolarChart() if u == "netz" else QChart()
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
    elif u.startswith(("saeule", "balken")) or u == "kombination":
        klasse = {"saeule_gruppiert": QBarSeries, "saeule_gestapelt": QStackedBarSeries, "saeule_100": QPercentBarSeries,
                  "balken_gruppiert": QHorizontalBarSeries, "balken_gestapelt": QHorizontalStackedBarSeries,
                  "balken_100": QHorizontalPercentBarSeries, "kombination": QBarSeries}[u]
        s = klasse()
        balken = namen[:-1] if u == "kombination" and len(namen) > 1 else namen
        for i, n in enumerate(balken):
            bs = QBarSet(n); bs.setColor(_farbe(i)); bs.setBorderColor(_farbe(i))
            for v in werte[namen.index(n)]:
                bs.append(v)
            s.append(bs)
        ch.addSeries(s)
        serien = [s]
        if u == "kombination" and len(namen) > 1:
            ls = QLineSeries(); ls.setName(namen[-1]); ls.setPen(QPen(_farbe(len(namen) - 1), 2.5))
            for i, v in enumerate(werte[-1]):
                ls.append(i, v)
            ch.addSeries(ls); serien.append(ls)
        achsen(serien, waagrecht=u.startswith("balken"))
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
    elif u == "netz":
        winkel = QCategoryAxis(); winkel.setRange(0, len(kategorien)); winkel.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
        for j, k in enumerate(kategorien):
            winkel.append(k, j)
        radius = QValueAxis(); radius.setLabelFormat("%.0f"); radius.setRange(0, max(hoechst, 1e-9)); radius.applyNiceNumbers()
        ch.addAxis(winkel, QPolarChart.PolarOrientationAngular); ch.addAxis(radius, QPolarChart.PolarOrientationRadial)
        for i, n in enumerate(namen):
            ls = QLineSeries(); ls.setName(n); ls.setPen(QPen(_farbe(i), 2))
            for j, v in enumerate(werte[i] + werte[i][:1]):
                ls.append(QPointF(j, v))
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
    # ohne sichtbares Fenster: das Diagramm in eine eigene Szene setzen, auf die Bildgröße bringen und die Szene malen
    szene = QGraphicsScene(); szene.addItem(ch)
    ch.setPos(0, 0); ch.resize(b, h)
    szene.setSceneRect(QRectF(0, 0, b, h))
    img = QImage(b, h, QImage.Format_ARGB32); img.fill(QColor("white"))
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing); szene.render(p, QRectF(0, 0, b, h), QRectF(0, 0, b, h)); p.end()
    szene.removeItem(ch)
    return img
