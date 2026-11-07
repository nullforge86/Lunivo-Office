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

from . import diagramm_format as F
from . import diagramm_zusatz as Z

# (Gruppe, Symbol aus symbole.json, [(Untertyp, Name)])
TYPEN = [
    ("Säule", "saeule", [("saeule_gruppiert", "Gruppierte Säule"), ("saeule_gestapelt", "Gestapelte Säule"),
                         ("saeule_100", "100 % gestapelte Säule")]),
    ("Linie", "linie", [("linie", "Linie"), ("linie_gestapelt", "Gestapelte Linie"), ("linie_100", "100 % gestapelte Linie"),
                        ("linie_punkte", "Linie mit Datenpunkten"), ("linie_punkte_gestapelt", "Gestapelte Linie mit Datenpunkten"),
                        ("linie_punkte_100", "100 % gestapelte Linie mit Datenpunkten")]),
    ("Kreis", "kreis", [("kreis", "Kreis"), ("kreis_3d", "3D-Kreis"), ("kreis_von_kreis", "Kreis von Kreis"),
                        ("kreis_balken", "Balken von Kreis"), ("ring", "Ring")]),
    ("Balken", "balkenquer", [("balken_gruppiert", "Gruppierte Balken"), ("balken_gestapelt", "Gestapelte Balken"),
                              ("balken_100", "100 % gestapelte Balken")]),
    ("Fläche", "flaeche", [("flaeche", "Fläche"), ("flaeche_gestapelt", "Gestapelte Fläche"), ("flaeche_100", "100 % gestapelte Fläche")]),
    ("X Y (Punkt)", "punktwolke", [("punkte", "Punkte"), ("punkte_glatt_punkte", "Punkt mit geglätteten Linien und Datenpunkten"),
                                   ("punkte_glatt", "Punkt mit geglätteten Linien"), ("punkte_gerade_punkte", "Punkt mit geraden Linien und Datenpunkten"),
                                   ("punkte_gerade", "Punkt mit geraden Linien"), ("punkte_blase", "Blase"), ("punkte_blase_3d", "3D-Blase")]),
    ("Kurs", "kurs", [("kurs_hts", "Höchst-Tiefst-Schluss"), ("kurs_ohts", "Eröffnung-Höchst-Tiefst-Schluss"),
                      ("kurs_vhts", "Volumen-Höchst-Tiefst-Schluss"), ("kurs_vohts", "Volumen-Eröffnung-Höchst-Tiefst-Schluss")]),
    ("Netz", "netz", [("netz", "Netz"), ("netz_punkte", "Netz mit Datenpunkten"), ("netz_gefuellt", "Gefülltes Netz")]),
    ("Kombination", "kombination", [("kombination", "Gruppierte Säulenlinie"),
                                    ("kombi_sekundaer", "Gruppierte Säule - Linie auf Sekundärachse"),
                                    ("kombi_flaeche", "Gestapelte Fläche - Gruppierte Säule"),
                                    ("kombi_eigen", "Benutzerdefinierte Kombination")]),
]
# Reihentypen der Kombination (Spalte „Diagrammtyp“ im Fenster)
KOMBI_TYPEN = [("saeule", "Gruppierte Säule"), ("saeule_gestapelt", "Gestapelte Säule"), ("linie", "Linie"),
               ("linie_punkte", "Linie mit Datenpunkten"), ("flaeche", "Fläche"), ("flaeche_gestapelt", "Gestapelte Fläche")]
# Vorlagen: fertige Farbreihen zu einer Diagrammart. Nicht mehr in ``TYPEN`` (die Gruppe „Vorlagen“ im Fenster ist eine eigene, später
# benutzerverwaltete Liste); die feste Liste bleibt für ältere Dokumente und das Menü „Diagrammstile ▸ Vorlagen“.
VORLAGEN = {
    "vorlage_klar": ("saeule_gruppiert", ["#4a8fd8", "#ef8a3c", "#9aa0a6", "#f2b705", "#2f6fb5", "#5aa454"]),
    "vorlage_blau": ("saeule_gruppiert", ["#1c4f8c", "#3a7bd5", "#7fb0ea", "#b9d4f5", "#0e2f57", "#5c93d8"]),
    "vorlage_gruen": ("linie_punkte", ["#2b7a3d", "#5aa454", "#9bcf8b", "#1d4f28", "#77b86a", "#c4e3b9"]),
    "vorlage_warm": ("balken_gruppiert", ["#c0392b", "#e67e22", "#f1c40f", "#d35400", "#e74c3c", "#f39c12"]),
    "vorlage_grau": ("flaeche", ["#3c4043", "#80868b", "#bdc1c6", "#5f6368", "#9aa0a6", "#dadce0"]),
    "vorlage_kreis": ("kreis", ["#4a8fd8", "#ef8a3c", "#5aa454", "#f2b705", "#9b59b6", "#e74c3c"]),
}
NAMEN = {u: n for _g, _s, unter in TYPEN for u, n in unter}
NAMEN["linie_glatt"] = "Geglättete Linie"          # versteckter Altname: wird gezeichnet, steht aber nicht mehr im Fenster
# Beispieldaten, mit denen das Fenster öffnet (wie in der Vorlage: vier Rubriken, drei Datenreihen)
BEISPIEL_KATEGORIEN = ["Rubrik 1", "Rubrik 2", "Rubrik 3", "Rubrik 4"]
BEISPIEL_REIHEN = {"Datenreihe 1": [4.1, 2.8, 3.3, 4.6], "Datenreihe 2": [2.6, 4.2, 1.7, 2.9], "Datenreihe 3": [1.9, 2.2, 3.1, 4.8]}
FARBEN = ["#4a8fd8", "#ef8a3c", "#9aa0a6", "#f2b705", "#2f6fb5", "#5aa454"]
# frühere Namen (gespeicherte Diagramme, ältere Aufrufe)
ALT = {"Säulen": "saeule_gruppiert", "Balken": "balken_gruppiert", "Linie": "linie", "Kreis": "kreis",
       "punkte_linien": "punkte_gerade_punkte"}       # „Punkt mit Linien“ (Punkte und gerade Linien)


def ist_kreis(u: str) -> bool:
    """Alle Kreisarten (Kreis, 3D-Kreis, Kreis/Balken von Kreis, Ring)."""
    return u.startswith("kreis") or u == "ring"


def hat_linien(u: str) -> bool:
    """Arten mit Linienreihen (Pfeile, Linienformat)."""
    return u.startswith(("linie", "punkte_gerade", "punkte_glatt"))


def beispiel(untertyp: str) -> tuple[str, list[str], dict[str, list[float]]]:
    """Beispieldaten für die Vorschau im Fenster nach Art des Untertyps (wie die Vorlage): (Titel, Rubriken, Reihen)."""
    u = ALT.get(untertyp, untertyp)
    if u.startswith("kreis") or u == "ring":
        return "Vertrieb", ["1. Quartal", "2. Quartal", "3. Quartal", "4. Quartal"], {"Vertrieb": [8.2, 3.2, 1.4, 1.2]}
    datum = ["05/01/2002", "06/01/2002", "07/01/2002", "08/01/2002"]
    if u.startswith("kurs_v"):
        r = {"Volumen": [4500.0, 6800.0, 5200.0, 7400.0]}
    elif u.startswith("kurs"):
        r = {}
    elif u.startswith(("flaeche", "netz")):
        return "Diagrammtitel", datum, dict(BEISPIEL_REIHEN)
    else:
        return "Diagrammtitel", list(BEISPIEL_KATEGORIEN), dict(BEISPIEL_REIHEN)
    r.update({"Eröffnung": [44.0, 25.0, 38.0, 50.0], "Höchst": [55.0, 57.0, 57.0, 58.0], "Tiefst": [11.0, 12.0, 13.0, 11.0],
              "Schluss": [25.0, 38.0, 50.0, 34.0]} if "o" in u.split("_")[1] else {"Höchst": [55.0, 57.0, 57.0, 58.0], "Tiefst": [11.0, 12.0, 13.0, 11.0],
                                                                                    "Schluss": [25.0, 38.0, 50.0, 34.0]})
    return "Diagrammtitel", datum, r


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
        if ist_kreis(u):
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


NAMEN_QUELLEN = ("zeile1", "spalte_a", "keine")


def namen_angewendet(kategorien: list[str], reihen: dict, ausgeblendet: dict | None, quelle: str | None) -> tuple[list[str], dict, dict | None]:
    """Namensquelle (Reiter „Name“ des Diagrammfilters) auf die Daten anwenden, ohne sie zu ändern: ``zeile1`` = wie gespeichert; ``spalte_a`` = die
    Namen kommen aus der ersten Spalte, Reihen und Rubriken tauschen die Plätze; ``keine`` = „Reihe 1 …“ und „1 …“. Der Filter wandert mit."""
    aus = {k: list(v) for k, v in (ausgeblendet or {}).items()}
    if quelle == "spalte_a" and reihen:
        namen = list(reihen)
        neu = {k: [(reihen[n][j] if j < len(reihen[n]) else 0.0) for n in namen] for j, k in enumerate(kategorien)}
        return namen, neu, ({"reihen": aus.get("rubriken", []), "rubriken": aus.get("reihen", [])} if aus else None)
    if quelle == "keine":
        rn = {n: f"Reihe {i + 1}" for i, n in enumerate(reihen)}
        kn = {k: str(j + 1) for j, k in enumerate(kategorien)}
        return (list(kn.values()), {rn[n]: v for n, v in reihen.items()},
                {"reihen": [rn[x] for x in aus.get("reihen", []) if x in rn], "rubriken": [kn[x] for x in aus.get("rubriken", []) if x in kn]} if aus else None)
    return kategorien, reihen, ausgeblendet or None


def bild_aus_daten(d: dict, b: float, h: float, skala: float = 1.0, geo: dict | None = None) -> QImage:
    """Das Diagramm aus den gespeicherten Daten (``a["daten"]``) in b × h Bildpunkten."""
    F.OBJEKT_DREH = float(d.get("objekt_dreh") or 0.0)
    kombi = [(k[0], bool(k[1])) for k in d.get("kombi") or []] or None
    kat, reihen, aus = namen_angewendet(list(d.get("kategorien") or BEISPIEL_KATEGORIEN), dict(d.get("reihen") or BEISPIEL_REIHEN),
                                        d.get("ausgeblendet"), d.get("namen_quelle"))
    if d.get("namen_quelle") == "spalte_a":
        kombi = None
    return bild(d.get("art", "saeule_gruppiert"), d.get("titel", ""), kat, reihen, max(120, round(b)), max(90, round(h)), legende=d.get("legende", True),
                kombi=kombi, farben=d.get("farben"), titel_an=d.get("titel_an", True), legende_pos=d.get("legende_pos", "unten"),
                labels=d.get("labels", False), stil=int(d.get("stil", 0)), skala=skala, elemente=d.get("elemente"),
                ausgeblendet=aus, teil_format=d.get("teil_format"), geo=geo)


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
    if u.startswith(("linie", "flaeche")) and u.endswith("_100"):           # 100 %: jede Rubrik auf Summe 100 bringen, dann wie gestapelt
        summen = [sum(abs(w[j]) for w in werte if j < len(w)) or 1.0 for j in range(max((len(w) for w in werte), default=0))]
        werte = [[v / summen[j] * 100.0 for j, v in enumerate(w)] for w in werte]
    gestapelt = u.endswith("_gestapelt") or (u.endswith("_100") and u.startswith(("linie", "flaeche")))
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

    if ist_kreis(u):
        s = QPieSeries()
        if u == "ring":
            s.setHoleSize(0.45)
        eigen = u in ("kreis_3d", "kreis_von_kreis", "kreis_balken")       # diese zeichnet ``diagramm_kreis`` selbst; die Scheiben von QtCharts bleiben unsichtbar
        for i, (k, v) in enumerate(zip(kategorien, werte[0] if werte else [])):
            sl = s.append(k, v); sl.setColor(_farbe(i)); sl.setLabelVisible(not legende or labels)
            sl.setLabel(f"{k}: {v:g}" if labels else k)
            if eigen:
                sl.setBrush(QBrush(Qt.transparent)); sl.setPen(QPen(Qt.NoPen)); sl.setLabelVisible(False)
        ch.addSeries(s)
        if eigen:
            for m, sl in zip(ch.legend().markers(s), s.slices()):
                m.setBrush(QBrush(_farbe(s.slices().index(sl)))); m.setPen(QPen(Qt.NoPen))
    elif u == "kombination" or u.startswith("kombi_"):
        _kombination(ch, kombi or kombi_vorgabe(u, len(namen)), namen, werte, kategorien)
    elif u.startswith("kurs"):
        volumen = u.startswith("kurs_v") and len(werte) > 1
        preise = werte[1:] if volumen else werte
        ohlc = u.endswith("ohts")
        ax = QBarCategoryAxis(); ax.append(kategorien); ch.addAxis(ax, Qt.AlignBottom)
        if volumen:                                             # Volumen: Säulen auf eigener Achse links, nur im unteren Teil; Kurse an der Achse rechts
            vs = QBarSeries(); bs = QBarSet("Volumen"); bs.setColor(_farbe(1)); bs.setBorderColor(_farbe(1))
            for v in werte[0]:
                bs.append(v)
            vs.append(bs); vs.setBarWidth(0.6); ch.addSeries(vs)
            av = QValueAxis(); ch.addAxis(av, Qt.AlignLeft); vs.attachAxis(ax); vs.attachAxis(av)
            av.setRange(0, max(max(werte[0], default=1.0), 1e-9) * 2.6); av.applyNiceNumbers()
        s = QCandlestickSeries(); s.setIncreasingColor(QColor("#ffffff")); s.setDecreasingColor(_farbe(0))
        s.setBodyWidth(0.25 if ohlc else 0.04); s.setPen(QPen(QColor("#3c4043"), 1.5)); s.setName("Kurs")
        for j in range(len(kategorien)):
            spalte = [w[j] for w in preise if j < len(w)] or [0.0]
            schluss = spalte[-1]
            auf = spalte[0] if ohlc else schluss
            s.append(QCandlestickSet(auf, max(spalte), min(spalte), schluss, float(j)))
        ch.addSeries(s)
        ay = QValueAxis(); ch.addAxis(ay, Qt.AlignRight if volumen else Qt.AlignLeft); s.attachAxis(ax); s.attachAxis(ay)
        tief = min((min(w) for w in preise if w), default=0.0)
        spitze = max((max(w) for w in preise if w), default=1.0)
        ay.setRange(min(0.0, tief), max(spitze, 1e-9)); ay.applyNiceNumbers()
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
        stapel = u != "flaeche"
        unten = [0.0] * len(kategorien)
        serien = []
        for i, n in enumerate(namen):
            oben = [(unten[j] if stapel else 0.0) + v for j, v in enumerate(werte[i])]
            hoch, tief = QLineSeries(), QLineSeries()
            for j, v in enumerate(oben):
                hoch.append(j, v); tief.append(j, unten[j] if stapel else 0.0)
            a = QAreaSeries(hoch, tief); a.setName(n)
            hoch.setParent(a); tief.setParent(a)                # QAreaSeries übernimmt die Linien nicht selbst
            c = _farbe(i); c.setAlpha(200 if stapel else 150); a.setColor(c); a.setBorderColor(_farbe(i))
            ch.addSeries(a); serien.append(a)
            if stapel:
                unten = oben
        ax = QCategoryAxis(); ax.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
        for j, k in enumerate(kategorien):
            ax.append(k, j)
        ax.setRange(0, max(1, len(kategorien) - 1))
        ay = QValueAxis(); ch.addAxis(ax, Qt.AlignBottom); ch.addAxis(ay, Qt.AlignLeft)
        for a in serien:
            a.attachAxis(ax); a.attachAxis(ay)
        ay.setRange(0, max(hoechst, 1e-9)); ay.applyNiceNumbers()
    elif u.startswith("punkte_blase"):
        serien = _blasen(ch, u, kategorien, werte, namen, kachel)
        achsen(serien, kategorie=False)
        _blasen_achsen(ch, kategorien, werte)
    elif u.startswith("punkte"):
        serien = []
        glatt, linien = "_glatt" in u, u.startswith(("punkte_glatt", "punkte_gerade"))
        punkte_an = u == "punkte" or u.endswith("_punkte")
        for i, n in enumerate(namen):
            if punkte_an:
                s = QScatterSeries(); s.setName(n); s.setColor(_farbe(i)); s.setMarkerSize(9); s.setBorderColor(_farbe(i))
                for j, v in enumerate(werte[i]):
                    s.append(j + 1, v)
                ch.addSeries(s); serien.append(s)
            if linien:
                ls = QSplineSeries() if glatt else QLineSeries(); ls.setPen(QPen(_farbe(i), 2))
                for j, v in enumerate(werte[i]):
                    ls.append(j + 1, v)
                ch.addSeries(ls); serien.append(ls)
                if punkte_an:
                    ch.legend().markers(ls)[0].setVisible(False)
                else:
                    ls.setName(n)
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
        stapel = [0.0] * len(kategorien)
        for i, n in enumerate(namen):
            rf = (opt["tf"].get(f"reihe_{opt['nummern'][i]}") or {}).get("reihe") or {} if i < len(opt["nummern"]) else {}
            s = QSplineSeries() if (u == "linie_glatt" or rf.get("glatt")) else QLineSeries()
            s.setName(n); s.setPen(QPen(_farbe(i), 2.5)); s.setPointsVisible(u.startswith("linie_punkte") or bool(rf.get("punkte")))
            for j, v in enumerate(werte[i]):
                if gestapelt and j < len(stapel):
                    stapel[j] += v; v = stapel[j]
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
    szene.render(p, QRectF(0, 0, b, ch_h), QRectF(0, 0, b, ch_h))
    if u in ("kreis_3d", "kreis_von_kreis", "kreis_balken") and werte:
        from . import diagramm_kreis as K
        K.zeichnen(p, QRectF(ch.plotArea()), u, kategorien, werte[0], [_farbe(i) for i in range(len(kategorien))], labels and not kachel,
                   QColor(STILE[stil][2] if 0 <= stil < len(STILE) else "#3c4043"))
    p.end()
    brauch_geo = geo is not None or bool(tf) or (el.get("fehlerindikatoren") and not kachel)
    g = {}
    if brauch_geo and not kachel:
        from . import diagramm_geo as G
        legenden = _legenden_namen(u, namen, kategorien)
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
        from . import diagramm_geo as G
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
    kreis, polar = ist_kreis(u), u.startswith("netz")
    waagr, senkr = ch.axes(Qt.Horizontal), ch.axes(Qt.Vertical)
    if el.get("achsentitel") and not kreis and not polar:
        hb = u.startswith("balken")
        if waagr:
            waagr[0].setTitleText("Werte" if hb else "Rubriken")
        if senkr:
            senkr[0].setTitleText("Rubriken" if hb else "Werte")
    if el.get("trendlinie") and (u in ("saeule_gruppiert", "linie", "linie_punkte", "linie_glatt", "flaeche") or u.startswith("punkte") and "blase" not in u) and waagr and senkr:
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
    gl = (tf.get("gitter_haupt") or {}).get("linie")                            # Linie der Hauptrasterlinien der Wertachse
    if gl:
        hb_ = u.startswith("balken")
        for a in (waagr if hb_ else senkr):
            if isinstance(a, QValueAxis) and not isinstance(a, QCategoryAxis):
                if F.linie_keine(gl):
                    a.setGridLineVisible(False)
                else:
                    a.setGridLineVisible(True)
                    a.setGridLinePen(F.stift({"farbe": a.gridLinePen().color().name(), **gl}))
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
    from . import diagramm_geo as G
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
    from . import diagramm_geo as G
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
    if not (hat_linien(u) and namen):
        return
    wollen = [nr for nr in nummern if ((tf.get(f"reihe_{nr}") or {}).get("linie") or {}).get("pfeil_anfang", "keiner") != "keiner"
              or ((tf.get(f"reihe_{nr}") or {}).get("linie") or {}).get("pfeil_ende", "keiner") != "keiner"]
    if not wollen:
        return
    from . import diagramm_geo as G
    pts = G.punkte(ch, u, kategorien, werte, namen)
    for k, nr in enumerate(nummern):
        lin = (tf.get(f"reihe_{nr}") or {}).get("linie") or {}
        if nr not in wollen or k >= len(pts) or len(pts[k]) < 2:
            continue
        farbe = QColor(lin.get("farbe") or _farbe(k).name())
        farbe.setAlphaF(max(0.0, min(1.0, 1.0 - float(lin.get("transparenz", 0) or 0) / 100.0)))
        br, (gr_a, gr_e) = float(lin.get("breite", 2.5)), F.pfeil_groessen(lin)
        a, b2, y, z = pts[k][0], pts[k][1], pts[k][-1], pts[k][-2]
        F.pfeil_zeichnen(p, QPointF(a[0], a[1]), QPointF(b2[0], b2[1]), lin.get("pfeil_anfang", "keiner"), br, gr_a, farbe)
        F.pfeil_zeichnen(p, QPointF(y[0], y[1]), QPointF(z[0], z[1]), lin.get("pfeil_ende", "keiner"), br, gr_e, farbe)


def _blasen(ch, u: str, kategorien, werte, namen, kachel: bool) -> list:
    """Blasen: ab drei Reihen X = 1., Y = 2., Größe = 3. Reihe; sonst X = Rubriknummer, Y = Wert, Größe = Wertebetrag. Je Blase eine Serie
    (QtCharts kennt nur eine Punktgröße je Serie); nur die erste jeder Reihe steht in der Legende."""
    from PySide6.QtCharts import QScatterSeries
    voll = len(werte) >= 3
    gruppen = [(namen[1], list(werte[0]), list(werte[1]), list(werte[2]), 1)] if voll else \
        [(n, [j + 1 for j in range(len(w))], list(w), [abs(v) for v in w], i) for i, (n, w) in enumerate(zip(namen, werte))]
    groesse = max((max(g[3], default=0.0) for g in gruppen), default=1.0) or 1.0
    faktor = 0.4 if kachel else 1.0
    serien = []
    for name, xs, ys, gs, farbe in gruppen:
        for k, (x, y, g) in enumerate(zip(xs, ys, gs)):
            s = QScatterSeries(); s.setName(name); s.setMarkerSize(faktor * (10 + 36 * (abs(g) / groesse) ** 0.5))
            c = _farbe(farbe)
            if u == "punkte_blase_3d":
                from PySide6.QtGui import QRadialGradient
                gr = QRadialGradient(0.35, 0.35, 0.75); gr.setCoordinateMode(QRadialGradient.ObjectBoundingMode)
                gr.setColorAt(0.0, c.lighter(185)); gr.setColorAt(1.0, c.darker(150))
                s.setBrush(QBrush(gr)); s.setPen(QPen(c.darker(160), 1))
            else:
                c.setAlpha(190); s.setColor(c); s.setBorderColor(_farbe(farbe))
            s.append(float(x), float(y))
            ch.addSeries(s); serien.append(s)
            if k:
                ch.legend().markers(s)[0].setVisible(False)
    return serien


def _blasen_achsen(ch, kategorien, werte) -> None:
    """Achsen der Blasen mit Luft für die großen Punkte."""
    waagr, senkr = ch.axes(Qt.Horizontal), ch.axes(Qt.Vertical)
    voll = len(werte) >= 3
    xs = werte[0] if voll else [j + 1 for j in range(len(kategorien))]
    ys = werte[1] if voll else [v for w in werte for v in w]
    for achse, wr in ((waagr[0] if waagr else None, xs), (senkr[0] if senkr else None, ys)):
        if achse is None or not wr:
            continue
        lo, hi = min(0.0, min(wr)), max(wr)
        spanne = (hi - lo) or 1.0
        achse.setRange(lo - (0.08 * spanne if lo < 0 else 0.0), hi + 0.18 * spanne); achse.applyNiceNumbers()
        if achse is waagr[0] and not voll:
            achse.setRange(0, len(kategorien) + 1); achse.setTickCount(len(kategorien) + 2); achse.setLabelFormat("%d")


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
    return list(kategorien) if ist_kreis(u) else (["Volumen", "Kurs"] if u.startswith("kurs_v") else ["Kurs"]) if u.startswith("kurs") else list(namen)


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
    if el["achsen"] and not ist_kreis(u) and not u.startswith("netz"):
        hb = u.startswith("balken")
        out += [("achse_horizontal", "Horizontal (Wert) Achse" if hb else "Horizontal (Rubrik) Achse"),
                ("achse_vertikal", "Vertikal (Rubrik) Achse" if hb else "Vertikal (Wert) Achse")]
        if el.get("gitter", True):                                       # Hauptrasterlinie der Wertachse (Foto: direkt nach den Achsen)
            out.append(("gitter_haupt", "Horizontal (Wert) Achse Hauptrasterlinie" if hb else "Vertikal (Wert) Achse Hauptrasterlinie"))
    out += [(f"reihe_{i}", f'Reihe"{namen_alle[i]}"') for i in nummern]
    if el["datenbeschriftung"]:
        out.append(("datenbeschriftung", "Datenbeschriftungen"))
    if el["legende"] != "aus":
        out += [(f"legendeneintrag_{k}", f"Legendeneintrag „{n}“")
                for k, n in enumerate(_legenden_namen(u, [namen_alle[i] for i in nummern], kat_f))]
    return out


def teil_geo(daten: dict, b: float, h: float) -> dict:
    """Wie ``teil_rechtecke``, aber mit allen Angaben der Geometrie (auch ``balken_<n>`` = Liste der einzelnen Balken einer Reihe)."""
    geo: dict = {}
    bild_aus_daten(daten, b, h, 1.0, geo)
    return geo


def teil_rechtecke(daten: dict, b: float, h: float) -> dict:
    """Schlüssel (siehe ``teile``) → QRectF in Bildpunkten des gezeichneten Bildes (b × h, logische Maße) — zum Anklicken. Die Lage kommt
    aus der QtCharts-Geometrie des fertig gesetzten Diagramms; Titel, Achsen und Legendeneinträge sind Näherungen."""
    erlaubt = {k for k, _n in teile(daten)}
    return {k: QRectF(r) for k, r in teil_geo(daten, b, h).items() if k in erlaubt and isinstance(r, QRectF)}
