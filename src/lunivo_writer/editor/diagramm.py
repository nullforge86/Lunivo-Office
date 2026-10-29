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
from PySide6.QtGui import QBrush, QColor, QFont, QImage, QPainter, QPen
from PySide6.QtWidgets import QGraphicsScene

from lunivo_writer.editor import diagramm_format as F
from lunivo_writer.editor import diagramm_zusatz as Z

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


def _art(daten: dict) -> str:
    u = daten.get("art", "saeule_gruppiert")
    return ALT.get(VORLAGEN[u][0] if u in VORLAGEN else u, VORLAGEN[u][0] if u in VORLAGEN else u)


def _filtern(kategorien: list[str], reihen: dict, ausgeblendet: dict | None) -> tuple[list[int], list[int], list[str], dict]:
    """Diagrammfilter: → (Stellen der sichtbaren Reihen, Stellen der sichtbaren Rubriken, Rubriken, Reihen) ohne die ausgeblendeten."""
    aus = ausgeblendet or {}
    namen = list(reihen)
    nummern = [i for i, n in enumerate(namen) if n not in set(aus.get("reihen") or [])]
    keep = [j for j, k in enumerate(kategorien) if k not in set(aus.get("rubriken") or [])]
    return (nummern, keep, [kategorien[j] for j in keep],
            {namen[i]: [reihen[namen[i]][j] for j in keep if j < len(reihen[namen[i]])] for i in nummern})


def bild(untertyp: str, titel: str, kategorien: list[str], reihen: dict[str, list[float]], b: int = 640, h: int = 400,
         legende: bool = True, kombi: list[tuple[str, bool]] | None = None, farben: list[str] | None = None,
         kachel: bool = False, titel_an: bool = True, legende_pos: str = "unten", labels: bool = False, stil: int = 0, skala: float = 1.0,
         elemente: dict | None = None, ausgeblendet: dict | None = None, teil_format: dict | None = None, geo: dict | None = None) -> QImage:
    """``skala``: Bild in dieser Auflösung (Maße ``b``/``h`` logisch, das Bild ist ``skala``-mal so groß, Schrift bleibt scharf).
    ``kachel``: kleines Bildchen ohne Beschriftung, Titel und Legende (Untertypen im Fenster). ``titel_an``: Titel zeigen;
    ``legende_pos``: ``unten`` | ``oben`` | ``links`` | ``rechts`` (``legende`` schaltet sie ganz ab); ``labels``: Datenbeschriftungen;
    ``stil``: Nummer in ``STILE``. Neu: ``elemente`` (achsen, achsentitel, datentabelle, fehlerindikatoren, gitter, trendlinie), ``ausgeblendet``
    (Diagrammfilter), ``teil_format`` (Formate je Diagrammteil, siehe ``diagramm_zusatz``); ``geo``: ein leeres Wörterbuch, das mit den Rechtecken
    der Teile gefüllt wird (``diagramm_geo``)."""
    global _PALETTE
    if untertyp in VORLAGEN:
        untertyp, farben = VORLAGEN[untertyp][0], farben or VORLAGEN[untertyp][1]
    u = ALT.get(untertyp, untertyp)
    basis = list(farben or FARBEN)
    tf = dict(teil_format or {})
    namen_alle = list(reihen)
    if kachel:
        nummern, kat, reihen_f, kombi_f = list(range(len(namen_alle))), kategorien, reihen, kombi
        _PALETTE = basis
    else:
        nummern, keep, kat, reihen_f = _filtern(kategorien, reihen, ausgeblendet)
        kombi_f = [kombi[i] for i in nummern if i < len(kombi)] if kombi else kombi
        if u in ("kreis", "ring"):
            _PALETTE = [basis[j % len(basis)] for j in keep] or basis
        else:
            _PALETTE = [F.hauptfarbe((tf.get(f"reihe_{i}") or {}).get("fuell")) or basis[i % len(basis)] for i in nummern] or basis
    el = {**Z.STANDARD_ELEMENTE, **(elemente or {})}
    ex = STIL_EXTRA.get(stil, {})
    opt = {"el": el, "tf": tf, "nummern": nummern, "geo": geo, "ex": ex}
    try:
        return _bild(untertyp, "" if kachel or not titel_an else titel, kat, reihen_f, b, h, legende and not kachel, kombi_f, kachel,
                     legende_pos, (labels or bool(ex.get("labels"))) and not kachel, stil, skala, opt)
    finally:
        _PALETTE = FARBEN


def bild_aus_daten(d: dict, b: float, h: float, skala: float = 1.0, geo: dict | None = None) -> QImage:
    """Das Diagramm aus den gespeicherten Daten (``a["daten"]``) in b × h Bildpunkten."""
    kombi = [(k[0], bool(k[1])) for k in d.get("kombi") or []] or None
    return bild(d.get("art", "saeule_gruppiert"), d.get("titel", ""), list(d.get("kategorien") or BEISPIEL_KATEGORIEN),
                dict(d.get("reihen") or BEISPIEL_REIHEN), max(120, round(b)), max(90, round(h)), legende=d.get("legende", True),
                kombi=kombi, farben=d.get("farben"), titel_an=d.get("titel_an", True), legende_pos=d.get("legende_pos", "unten"),
                labels=d.get("labels", False), stil=int(d.get("stil", 0)), skala=skala, elemente=d.get("elemente"),
                ausgeblendet=d.get("ausgeblendet"), teil_format=d.get("teil_format"), geo=geo)


def _bild(untertyp, titel, kategorien, reihen, b, h, legende, kombi, kachel=False, legende_pos="unten", labels=False, stil=0, skala=1.0,
          opt=None) -> QImage:
    from PySide6.QtCharts import (
        QAreaSeries, QBarCategoryAxis, QBarSeries, QBarSet, QCategoryAxis, QChart, QHorizontalBarSeries,
        QHorizontalPercentBarSeries, QHorizontalStackedBarSeries, QLineSeries, QPercentBarSeries, QPieSeries, QPolarChart, QScatterSeries,
        QSplineSeries, QStackedBarSeries, QValueAxis, QCandlestickSeries, QCandlestickSet,
    )
    opt = opt or {"el": dict(Z.STANDARD_ELEMENTE), "tf": {}, "nummern": list(range(len(reihen))), "geo": None, "ex": {}}
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
            sl = s.append(k, v); sl.setColor(_farbe(i)); sl.setLabelVisible(not legende or labels)
            sl.setLabel(f"{k}: {v:g}" if labels else k)
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
            rf = (opt["tf"].get(f"reihe_{opt['nummern'][i]}") or {}).get("reihe") or {} if i < len(opt["nummern"]) else {}
            s = QSplineSeries() if (u == "linie_glatt" or rf.get("glatt")) else QLineSeries()
            s.setName(n); s.setPen(QPen(_farbe(i), 2.5)); s.setPointsVisible(u == "linie_punkte" or bool(rf.get("punkte")))
            for j, v in enumerate(werte[i]):
                s.append(j, v)
            ch.addSeries(s); serien.append(s)
        achsen(serien)
    ch.legend().setVisible(legende)
    ch.legend().setAlignment({"oben": Qt.AlignTop, "links": Qt.AlignLeft, "rechts": Qt.AlignRight}.get(legende_pos, Qt.AlignBottom))
    if labels and not kachel:
        for serie in ch.series():
            if hasattr(serie, "setLabelsVisible"):
                serie.setLabelsVisible(True)
            elif hasattr(serie, "setPointLabelsVisible"):
                serie.setPointLabelsVisible(True)
    el, tf, nummern, geo, ex = opt["el"], opt["tf"], opt["nummern"], opt["geo"], opt["ex"]
    _stil_anwenden(ch, stil, kachel, bool(el.get("gitter", True)))
    if kachel:
        ch.setMargins(__import__("PySide6.QtCore", fromlist=["QMargins"]).QMargins(2, 2, 2, 2))
        for achse in ch.axes():
            achse.setLabelsVisible(False); achse.setGridLineVisible(False)
        for serie in ch.series():
            if hasattr(serie, "setLabelsVisible"):
                serie.setLabelsVisible(False)
    else:
        _elemente_anwenden(ch, u, el, werte, namen, nummern, tf)
    schrift = QColor(STILE[stil][2] if 0 <= stil < len(STILE) else "#3c4043")
    tab_h = (len(namen) + 1) * Z.TABELLE_ZEILE + 8 if el.get("datentabelle") and not kachel and namen else 0
    ch_h = max(60.0, h - tab_h)
    # ohne sichtbares Fenster: das Diagramm in eine eigene Szene setzen, auf die Bildgröße bringen und die Szene auf eine durchsichtige Ebene malen
    szene = QGraphicsScene(); szene.addItem(ch)
    ch.setPos(0, 0); ch.resize(b, ch_h)
    szene.setSceneRect(QRectF(0, 0, b, ch_h))
    px, py = max(1, round(b * skala)), max(1, round(h * skala))
    ebene = QImage(px, py, QImage.Format_ARGB32); ebene.fill(Qt.transparent)
    p = QPainter(ebene); p.setRenderHint(QPainter.Antialiasing); p.scale(skala, skala)
    szene.render(p, QRectF(0, 0, b, ch_h), QRectF(0, 0, b, ch_h)); p.end()
    brauch_geo = geo is not None or bool(tf) or (el.get("fehlerindikatoren") and not kachel)
    g = {}
    if brauch_geo and not kachel:
        from lunivo_writer.editor import diagramm_geo as G
        legenden = list(kategorien) if u in ("kreis", "ring") else ["Kurs"] if u.startswith("kurs") else list(namen)
        g = G.geometrie(ch, u, kategorien, werte, namen, nummern, b, ch_h, titel, legende, bool(el.get("achsen", True)), legenden)
        g["diagrammbereich"] = QRectF(0, 0, b, h)               # mit der Datentabelle
        for teil in ("titel", "legende"):                        # das Feld um den Text: Größe und Ränder aus den Textoptionen
            if teil in g and tf.get(teil):
                g[teil] = F.box_rect(teil, g[teil], _text_fuer(tf, teil), b)
        if geo is not None:
            geo.update(g)
    img = QImage(px, py, QImage.Format_ARGB32)
    img.fill(QColor(STILE[stil][1] if 0 <= stil < len(STILE) and not kachel else "white"))
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing); p.scale(skala, skala)
    if g and tf:
        Z.hintergruende(p, g, tf, QColor(STILE[stil][1] if 0 <= stil < len(STILE) else "white"))
    p.resetTransform(); p.drawImage(0, 0, ebene); p.scale(skala, skala)
    if g and tf:
        _eigene_texte(p, ch, g, tf, titel, schrift.name(), legende)
    if g and el.get("fehlerindikatoren") and namen:
        from lunivo_writer.editor import diagramm_geo as G
        Z.fehlerindikatoren(p, ch, u, G.punkte(ch, u, kategorien, werte, namen), hoechst, schrift)
    if g and tf:
        Z.linien(p, g, tf)
        _pfeile(p, ch, u, kategorien, werte, namen, nummern, tf)
    if ex.get("rahmen") and not kachel:
        p.setBrush(Qt.NoBrush); p.setPen(QPen(QColor(ex["rahmen"]), 2)); p.drawRect(QRectF(1, 1, b - 2, h - 2))
    if tab_h:
        Z.tabelle(p, QRectF(8, ch_h, b - 16, tab_h - 6), kategorien, namen, werte, [_farbe(i) for i in range(len(namen))], schrift)
    p.end()
    szene.removeItem(ch)
    return img


# Stile des Diagramms (Diagrammtools ▸ Diagrammstile): (Name, Grund, Schrift, Raster); die ersten vier behalten ihre Nummer
STILE = [("Standard", "#ffffff", "#3c4043", True), ("Ohne Raster", "#ffffff", "#3c4043", False),
         ("Hellgrau", "#f1f3f5", "#343a40", True), ("Dunkel", "#2b2d42", "#f1f3f5", True),
         ("Fetter Titel", "#ffffff", "#212529", True), ("Mit Datenbeschriftung", "#ffffff", "#3c4043", False),
         ("Mit Rahmen", "#ffffff", "#1f3864", True), ("Hellblau", "#e7f1fb", "#1c4f8c", True),
         ("Warm", "#fff4e6", "#7a3e00", True), ("Hellgrün", "#ebf7ee", "#1d4f28", False),
         ("Nachtblau", "#14213d", "#e5e5e5", True), ("Schwarz", "#000000", "#ffffff", False),
         ("Papier", "#fdf6e3", "#586e75", True), ("Hoher Kontrast", "#ffffff", "#000000", True)]
# Zusätze einzelner Stile: titel_pt/titel_fett (Titelschrift), labels (Datenbeschriftungen), rahmen (Farbe), raster_farbe
STIL_EXTRA = {4: {"titel_pt": 16, "titel_fett": True}, 5: {"labels": True}, 6: {"rahmen": "#1f3864"}, 7: {"raster_farbe": "#b9d4f5"},
              8: {"raster_farbe": "#ffd8a8"}, 10: {"raster_farbe": "#3a4a6b"}, 11: {"labels": True},
              12: {"rahmen": "#93a1a1", "raster_farbe": "#eee8d5"}, 13: {"titel_pt": 14, "titel_fett": True, "rahmen": "#000000", "raster_farbe": "#868e96"}}


def stile_liste() -> list[dict]:
    """Alle Formatvorlagen (Diagrammstile) für die Galerie: {nr, name, grund, schrift, raster, **Zusätze}."""
    return [{"nr": i, "name": n, "grund": g, "schrift": s, "raster": r, **STIL_EXTRA.get(i, {})} for i, (n, g, s, r) in enumerate(STILE)]


def _monochrom(basis: str) -> list[str]:
    """Sechs Töne einer Farbe, vom dunklen zum hellen."""
    c = QColor(basis)
    return [c.darker(f).name() for f in (170, 130)] + [c.name()] + [c.lighter(f).name() for f in (130, 165, 205)]


# Farbschemen (Diagrammstile ▸ Farben): Gruppe → [(Name, sechs Farben)]
FARBSCHEMEN = [
    ("Farbig", [("Farbig 1", ["#4a8fd8", "#ef8a3c", "#9aa0a6", "#f2b705", "#2f6fb5", "#5aa454"]),
                ("Farbig 2", ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6", "#e67e22"]),
                ("Farbig 3", ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51", "#8ab17d"]),
                ("Farbig 4", ["#6a4c93", "#1982c4", "#8ac926", "#ffca3a", "#ff595e", "#52a9a1"])]),
    ("Monochrom", [(f"Monochrom {i + 1}", _monochrom(c)) for i, c in
                   enumerate(["#4a8fd8", "#ef8a3c", "#868e96", "#f2b705", "#2f6fb5", "#5aa454", "#c0392b", "#7e57c2"])]),
]


def farbschemen_gruppen() -> list[tuple[str, list[tuple[str, list[str]]]]]:
    """Die Gruppen „Farbig“ und „Monochrom“ mit ihren Farbzeilen (Kopie von ``FARBSCHEMEN``)."""
    return [(g, [(n, list(f)) for n, f in z]) for g, z in FARBSCHEMEN]


def farbschemen_flach() -> list[tuple[str, list[str]]]:
    """Alle Farbzeilen hintereinander (Nummer = Argument von ``diagrammFarben``)."""
    return [(n, list(f)) for _g, z in FARBSCHEMEN for n, f in z]


def _stil_anwenden(ch, stil: int, kachel: bool, gitter: bool = True) -> None:
    """Schrift- und Rasterfarben des Stils. Den Grund malt ``_bild`` selbst (das Diagramm liegt auf einer durchsichtigen Ebene)."""
    from PySide6.QtGui import QBrush
    if kachel or not 0 <= stil < len(STILE):
        return
    _n, _grund, schrift, raster = STILE[stil]
    ex = STIL_EXTRA.get(stil, {})
    ch.setBackgroundVisible(False)
    ch.setTitleBrush(QBrush(QColor(schrift)))
    if ex.get("titel_pt"):
        f = ch.titleFont(); f.setPointSizeF(ex["titel_pt"]); f.setBold(bool(ex.get("titel_fett"))); ch.setTitleFont(f)
    ch.legend().setLabelColor(QColor(schrift))
    for achse in ch.axes():
        achse.setGridLineVisible(raster and gitter)
        achse.setLabelsColor(QColor(schrift))
        if ex.get("raster_farbe"):
            achse.setGridLinePen(QPen(QColor(ex["raster_farbe"]), 1))
        if hasattr(achse, "setLinePenColor"):
            achse.setLinePenColor(QColor(schrift))


def _elemente_anwenden(ch, u: str, el: dict, werte, namen, nummern, tf: dict) -> None:
    """Achsen, Achsentitel, Trendlinien und die Schrift-/Linienformate der Teile (``teil_format``)."""
    from PySide6.QtCharts import QCategoryAxis, QLineSeries, QValueAxis
    achsen = ch.axes()
    if not el.get("achsen", True):
        for a in achsen:
            a.setLabelsVisible(False); a.setLineVisible(False)
    kreis, polar = u in ("kreis", "ring"), u.startswith("netz")
    waagr, senkr = ch.axes(Qt.Horizontal), ch.axes(Qt.Vertical)
    if el.get("achsentitel") and not kreis and not polar:
        hb = u.startswith("balken")
        if waagr:
            waagr[0].setTitleText("Werte" if hb else "Rubriken")
        if senkr:
            senkr[0].setTitleText("Rubriken" if hb else "Werte")
    if el.get("trendlinie") and u in ("saeule_gruppiert", "linie", "linie_punkte", "linie_glatt", "punkte", "punkte_linien", "flaeche") and waagr and senkr:
        for i, n in enumerate(namen):
            if len(werte[i]) < 2:
                continue
            a0, b0 = Z.trend(werte[i])
            t = QLineSeries(); t.setName(f"Linear ({n})")
            pen = Z.stift({"farbe": _farbe(i).name(), "breite": 1.8, "art": "gestrichelt"}); t.setPen(pen)
            versatz = 1 if u.startswith("punkte") else 0
            for j in (0, len(werte[i]) - 1):
                t.append(j + versatz, a0 + b0 * j)
            ch.addSeries(t); t.attachAxis(waagr[0]); t.attachAxis(senkr[0])
            ch.legend().markers(t)[0].setVisible(False)
    if not tf:
        return
    schrift_hex = ch.titleBrush().color().name()

    def text(teil: str) -> dict:
        return _text_fuer(tf, teil)
    t = text("titel")
    if t:
        ch.setTitleFont(F.schrift_aus(ch.titleFont(), t))
        ch.setTitleBrush(QBrush(Qt.transparent if F.text_eigen(t) else F.textfarbe(t, schrift_hex)))      # Verlauf, Kontur, Effekte zeichnet ``_eigene_texte``
    t = text("legende")
    if t:
        ch.legend().setFont(F.schrift_aus(ch.legend().font(), t))
        ch.legend().setLabelColor(QColor(0, 0, 0, 0) if F.text_eigen(t) else F.textfarbe(t, schrift_hex))
    marken = [m for m in ch.legend().markers() if m.isVisible()]
    for k, m in enumerate(marken):                                             # einzelne Legendeneinträge
        te = tf.get(f"legendeneintrag_{k}", {}).get("text")
        if te:
            tm = {**text("legende"), **te}
            m.setFont(F.schrift_aus(m.font(), tm))
            m.setLabelBrush(QBrush(QColor(0, 0, 0, 0) if F.text_eigen(text("legende")) else F.textfarbe(tm, schrift_hex)))
    for teil, liste in (("achse_horizontal", waagr), ("achse_vertikal", senkr)):
        t = text(teil)
        opt = (tf.get(teil) or {}).get("achse")
        for a in liste:
            if t:
                a.setLabelsFont(F.schrift_aus(a.labelsFont(), t)); a.setTitleFont(F.schrift_aus(a.titleFont(), t))
                fc = F.textfarbe(t, schrift_hex)
                a.setLabelsBrush(QBrush(fc)); a.setTitleBrush(QBrush(fc))
                if F.textwinkel(t):
                    a.setLabelsAngle(int(round(F.textwinkel(t))))
            F.achse_anwenden(a, opt, isinstance(a, QValueAxis) and not isinstance(a, QCategoryAxis))
    t = text("datenbeschriftung")
    if t:
        f, fc = F.schrift_aus(QFont(), t), F.textfarbe(t, schrift_hex)
        for serie in ch.series():
            if hasattr(serie, "barSets"):
                for bs in serie.barSets():
                    bs.setLabelFont(f); bs.setLabelBrush(QBrush(fc))
            elif hasattr(serie, "slices"):
                for sl in serie.slices():
                    sl.setLabelFont(f); sl.setLabelBrush(QBrush(fc))
            elif hasattr(serie, "setPointLabelsFont"):
                serie.setPointLabelsFont(f); serie.setPointLabelsColor(fc)
    from lunivo_writer.editor import diagramm_geo as G
    luecke = next(((tf.get(f"reihe_{nr}") or {}).get("reihe", {}).get("luecke") for nr in nummern
                   if (tf.get(f"reihe_{nr}") or {}).get("reihe", {}).get("luecke") is not None), None)
    if luecke is not None:                                                     # Lückenbreite gilt für alle Säulen/Balken (QtCharts: eine Breite je Serie)
        for serie in ch.series():
            if hasattr(serie, "setBarWidth"):
                serie.setBarWidth(F.luecke_zu_breite(luecke))
    for i, (nr, n) in enumerate(zip(nummern, namen)):                       # Füllung und Linie der Reihe
        fmt = tf.get(f"reihe_{nr}") or {}
        if not fmt or kreis:
            continue
        serie, bs = G._serie(ch, n)
        ziel = bs if bs is not None else serie
        if ziel is None:
            continue
        linie, fu = fmt.get("linie"), fmt.get("fuell")
        if F.linie_keine(linie):
            ziel.setPen(QPen(Qt.NoPen))
        elif linie:
            ziel.setPen(F.stift({"farbe": _farbe(i).name(), **linie}))
        if F.ist_keine(fu) and hasattr(ziel, "setBrush"):
            ziel.setBrush(QBrush(Qt.NoBrush))
        elif fu and hasattr(ziel, "setBrush"):
            pi, opaz = F.pinsel(fu)
            if pi is not None:
                ziel.setBrush(pi)
            if opaz < 1.0 and serie is not None:
                serie.setOpacity(opaz)


def _text_fuer(tf: dict, teil: str) -> dict:
    """Das Textformat eines Teils: die Angaben des Diagrammbereichs gelten für alle, der Teil überschreibt sie."""
    basis = (tf.get("diagrammbereich") or {}).get("text") or {}
    return {**basis, **((tf.get(teil) or {}).get("text") or {})}


def _eigene_texte(p, ch, g: dict, tf: dict, titel: str, standard: str, legende_an: bool) -> None:
    """Titel und Legende mit Textfüllung (Verlauf, Keine), Kontur und Effekten: QtCharts zeichnet sie durchsichtig, hier kommt der Text selbst darüber."""
    from lunivo_writer.editor import diagramm_geo as G
    t = _text_fuer(tf, "titel")
    if titel and "titel" in g and F.text_eigen(t):
        F.text_zeichnen(p, F.text_feld(g["titel"], t), titel, ch.titleFont(), t, standard, True)
    tl = _text_fuer(tf, "legende")
    marken = [m for m in ch.legend().markers() if m.isVisible()]
    if legende_an and F.text_eigen(tl):
        for k, ((_e, tr), m) in enumerate(zip(G.legenden_items(ch), marken)):
            te = {**tl, **((tf.get(f"legendeneintrag_{k}") or {}).get("text") or {})}
            F.text_zeichnen(p, tr.adjusted(4, 2, -4, -2), m.label(), F.schrift_aus(ch.legend().font(), te), te, standard)


def _pfeile(p, ch, u: str, kategorien, werte, namen, nummern, tf: dict) -> None:
    """Pfeile und Linienenden an Linien- und Kurvenreihen (``linie.pfeil_anfang`` / ``pfeil_ende``)."""
    if not (u.startswith(("linie", "punkte_linien")) and namen):
        return
    wollen = [nr for nr in nummern if ((tf.get(f"reihe_{nr}") or {}).get("linie") or {}).get("pfeil_anfang", "keiner") != "keiner"
              or ((tf.get(f"reihe_{nr}") or {}).get("linie") or {}).get("pfeil_ende", "keiner") != "keiner"]
    if not wollen:
        return
    from lunivo_writer.editor import diagramm_geo as G
    pts = G.punkte(ch, u, kategorien, werte, namen)
    for k, nr in enumerate(nummern):
        lin = (tf.get(f"reihe_{nr}") or {}).get("linie") or {}
        if nr not in wollen or k >= len(pts) or len(pts[k]) < 2:
            continue
        farbe = QColor(lin.get("farbe") or _farbe(k).name())
        farbe.setAlphaF(max(0.0, min(1.0, 1.0 - float(lin.get("transparenz", 0) or 0) / 100.0)))
        br, gr = float(lin.get("breite", 2.5)), float(lin.get("pfeil_groesse", 1.0))
        a, b2, y, z = pts[k][0], pts[k][1], pts[k][-1], pts[k][-2]
        F.pfeil_zeichnen(p, QPointF(a[0], a[1]), QPointF(b2[0], b2[1]), lin.get("pfeil_anfang", "keiner"), br, gr, farbe)
        F.pfeil_zeichnen(p, QPointF(y[0], y[1]), QPointF(z[0], z[1]), lin.get("pfeil_ende", "keiner"), br, gr, farbe)


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


# ---- Diagrammteile (Auswahl, Anklicken) -----------------------------------------------------------------------------------------
def _legenden_namen(u: str, namen: list[str], kategorien: list[str]) -> list[str]:
    return list(kategorien) if u in ("kreis", "ring") else ["Kurs"] if u.startswith("kurs") else list(namen)


def teile(daten: dict) -> list[tuple[str, str]]:
    """Die wählbaren Teile des Diagramms (Schlüssel, Anzeigename), in der Reihenfolge des Feldes „Diagrammbereich“: Diagrammbereich,
    Zeichnungsbereich, Diagrammtitel, Legende, Achsen, Reihen, Legendeneinträge. Teile, die ausgeschaltet sind (Titel, Legende, Achsen,
    ausgeblendete Reihen), fehlen."""
    u = _art(daten)
    el = Z.elemente_wirksam(daten)
    kat = list(daten.get("kategorien") or BEISPIEL_KATEGORIEN)
    reihen = dict(daten.get("reihen") or BEISPIEL_REIHEN)
    nummern, _keep, kat_f, _rf = _filtern(kat, reihen, daten.get("ausgeblendet"))
    namen_alle = list(reihen)
    out = [("diagrammbereich", "Diagrammbereich"), ("zeichnungsbereich", "Zeichnungsbereich")]
    if el["titel"] and daten.get("titel"):
        out.append(("titel", "Diagrammtitel"))
    if el["legende"] != "aus":
        out.append(("legende", "Legende"))
    if el["achsen"] and u not in ("kreis", "ring") and not u.startswith("netz"):
        hb = u.startswith("balken")
        out += [("achse_horizontal", "Horizontal (Wert) Achse" if hb else "Horizontal (Rubrik) Achse"),
                ("achse_vertikal", "Vertikal (Rubrik) Achse" if hb else "Vertikal (Wert) Achse")]
    out += [(f"reihe_{i}", f"Reihe „{namen_alle[i]}“") for i in nummern]
    if el["datenbeschriftung"]:
        out.append(("datenbeschriftung", "Datenbeschriftungen"))
    if el["legende"] != "aus":
        out += [(f"legendeneintrag_{k}", f"Legendeneintrag „{n}“")
                for k, n in enumerate(_legenden_namen(u, [namen_alle[i] for i in nummern], kat_f))]
    return out


def teil_geo(daten: dict, b: float, h: float) -> dict:
    """Wie ``teil_rechtecke``, aber mit allen Angaben der Geometrie (auch ``balken_<i>`` = Liste der einzelnen Balken einer Reihe)."""
    geo: dict = {}
    bild_aus_daten(daten, b, h, 1.0, geo)
    return geo


def teil_rechtecke(daten: dict, b: float, h: float) -> dict:
    """Schlüssel (siehe ``teile``) → QRectF in Bildpunkten des gezeichneten Bildes (b × h, logische Maße) — zum Anklicken. Die Lage kommt
    aus der QtCharts-Geometrie des fertig gesetzten Diagramms; Titel, Achsen und Legendeneinträge sind Näherungen."""
    erlaubt = {k for k, _n in teile(daten)}
    return {k: QRectF(r) for k, r in teil_geo(daten, b, h).items() if k in erlaubt and isinstance(r, QRectF)}
