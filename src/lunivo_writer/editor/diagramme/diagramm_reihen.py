"""Datenreihen des Diagramms: je Diagrammart die QtCharts-Serien und -Achsen aufbauen (Säulen, Linien, Flächen, Punkte, Blasen, Kreis, Kurs, Netz,
Kombination). Keine Oberfläche; Beschriftung und Formate setzen ``diagramm_elemente`` und ``diagramm_stile``, gezeichnet wird in ``diagramm.py``.

``aufbauen(ch, u, d)`` nimmt die Werte als ``Daten`` und stellt die Serien in das Diagramm ``ch``. Die Reihenfarben kommen aus der Palette
(``palette_setzen`` / ``farbe``), die ``diagramm.bild`` für die Dauer einer Zeichnung belegt."""
from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import QMargins, QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QPen, QRadialGradient

from .diagramm_typen import FARBEN, ist_kreis, kombi_vorgabe

_PALETTE = FARBEN
KURS_VOLUMEN_PLATZ = 2.6          # Kurs mit Volumen: die Säulen belegen nur den unteren Teil (Höchstwert mal diesen Faktor)
BLASE_MIN, BLASE_SPANNE = 10, 36  # Blasendurchmesser: kleinste Blase und Spanne bis zur größten (px)
BLASE_KACHEL = 0.4                # Blasen in Kacheln sind kleiner


def palette_setzen(liste: list[str] | None) -> None:
    """Belegt die Reihenfarben für die folgende Zeichnung; ``None`` stellt die Standardfarben wieder her."""
    global _PALETTE
    _PALETTE = FARBEN if liste is None else liste


def farbe(i: int) -> QColor:
    return QColor(_PALETTE[i % len(_PALETTE)])


@dataclass
class Daten:
    """Die Werte einer Zeichnung, wie sie die Serien brauchen."""
    kategorien: list
    namen: list
    werte: list
    hoechst: float = 1.0
    gestapelt: bool = False
    kombi: list | None = None
    kachel: bool = False
    legende: bool = True
    labels: bool = False
    tf: dict = field(default_factory=dict)
    nummern: list = field(default_factory=list)


def _auf_hundert(werte: list[list[float]]) -> list[list[float]]:
    """Jede Rubrik auf die Summe 100 bringen."""
    summen = [sum(abs(w[j]) for w in werte if j < len(w)) or 1.0 for j in range(max((len(w) for w in werte), default=0))]
    return [[v / summen[j] * 100.0 for j, v in enumerate(w)] for w in werte]


def _hoechstwert(werte: list[list[float]], gestapelt: bool) -> float:
    """Größter Wert; bei gestapelten Reihen die größte Rubriksumme."""
    if gestapelt and werte:
        return max((sum(w[j] for w in werte if j < len(w)) for j in range(max(len(w) for w in werte))), default=1.0)
    return max((max(w) for w in werte if w), default=1.0)


def werte_vorbereiten(u: str, reihen: dict) -> tuple[list[str], list[list[float]], bool, float]:
    """(Namen, Werte, gestapelt, größter Wert). Bei „100 %“ (Linie, Fläche) wird jede Rubrik auf die Summe 100 gebracht."""
    namen = list(reihen)
    werte = [[float(v) for v in reihen[n]] for n in namen]
    prozent = u.startswith(("linie", "flaeche")) and u.endswith("_100")
    if prozent:
        werte = _auf_hundert(werte)
    gestapelt = u.endswith("_gestapelt") or (u.endswith("_100") and u.startswith(("linie", "flaeche")))
    return namen, werte, gestapelt, _hoechstwert(werte, gestapelt)


def achsen(ch, u: str, d: Daten, serie_liste, waagrecht: bool = False, kategorie: bool = True):
    """Rubrik- (oder Wert-) und Wertachse anlegen, an die Serien hängen und die Wertachse einteilen. → (Achse 1, Wertachse)."""
    from PySide6.QtCharts import QBarCategoryAxis, QValueAxis
    ax = QBarCategoryAxis() if kategorie else QValueAxis()
    if kategorie:
        ax.append(d.kategorien)
    ay = QValueAxis()
    ch.addAxis(ax, Qt.AlignLeft if waagrecht else Qt.AlignBottom)
    ch.addAxis(ay, Qt.AlignBottom if waagrecht else Qt.AlignLeft)
    for s in serie_liste:
        s.attachAxis(ax); s.attachAxis(ay)
    if u.endswith("_100"):
        ay.setRange(0, 100)
    else:
        ay.setRange(min(0.0, min((min(w) for w in d.werte if w), default=0.0)), max(d.hoechst, 1e-9))
        ay.applyNiceNumbers()                               # 0 … 5 statt 0 … 4,8
    return ax, ay


def _kreis(ch, u: str, d: Daten) -> None:
    from PySide6.QtCharts import QPieSeries
    s = QPieSeries()
    if u == "ring":
        s.setHoleSize(0.45)
    eigen = u in ("kreis_3d", "kreis_von_kreis", "kreis_balken")       # diese zeichnet ``diagramm_kreis`` selbst; die Scheiben von QtCharts bleiben unsichtbar
    for i, (k, v) in enumerate(zip(d.kategorien, d.werte[0] if d.werte else [])):
        sl = s.append(k, v); sl.setColor(farbe(i)); sl.setLabelVisible(not d.legende or d.labels)
        sl.setLabel(f"{k}: {v:g}" if d.labels else k)
        if eigen:
            sl.setBrush(QBrush(Qt.transparent)); sl.setPen(QPen(Qt.NoPen)); sl.setLabelVisible(False)
    ch.addSeries(s)
    if eigen:
        for m, sl in zip(ch.legend().markers(s), s.slices()):
            m.setBrush(QBrush(farbe(s.slices().index(sl)))); m.setPen(QPen(Qt.NoPen))


def _kurs_volumen(ch, ax, werte: list) -> None:
    """Volumen: Säulen auf eigener Achse links, nur im unteren Teil; die Kurse stehen an der Achse rechts."""
    from PySide6.QtCharts import QBarSeries, QBarSet, QValueAxis
    vs = QBarSeries(); bs = QBarSet("Volumen"); bs.setColor(farbe(1)); bs.setBorderColor(farbe(1))
    for v in werte[0]:
        bs.append(v)
    vs.append(bs); vs.setBarWidth(0.6); ch.addSeries(vs)
    av = QValueAxis(); ch.addAxis(av, Qt.AlignLeft); vs.attachAxis(ax); vs.attachAxis(av)
    av.setRange(0, max(max(werte[0], default=1.0), 1e-9) * KURS_VOLUMEN_PLATZ); av.applyNiceNumbers()


def _kurs(ch, u: str, d: Daten) -> None:
    from PySide6.QtCharts import QBarCategoryAxis, QValueAxis
    volumen = u.startswith("kurs_v") and len(d.werte) > 1
    preise = d.werte[1:] if volumen else d.werte
    ax = QBarCategoryAxis(); ax.append(d.kategorien); ch.addAxis(ax, Qt.AlignBottom)
    if volumen:
        _kurs_volumen(ch, ax, d.werte)
    s = _kerzen(d, preise, u.endswith("ohts"))
    ch.addSeries(s)
    ay = QValueAxis(); ch.addAxis(ay, Qt.AlignRight if volumen else Qt.AlignLeft); s.attachAxis(ax); s.attachAxis(ay)
    tief = min((min(w) for w in preise if w), default=0.0)
    spitze = max((max(w) for w in preise if w), default=1.0)
    ay.setRange(min(0.0, tief), max(spitze, 1e-9)); ay.applyNiceNumbers()


def _kerzen(d: Daten, preise, ohlc: bool):
    """Die Kerzenserie: je Rubrik Eröffnung (nur bei Open-High-Low-Close), Hoch, Tief und Schluss aus den Reihen."""
    from PySide6.QtCharts import QCandlestickSeries, QCandlestickSet
    s = QCandlestickSeries(); s.setIncreasingColor(QColor("#ffffff")); s.setDecreasingColor(farbe(0))
    s.setBodyWidth(0.25 if ohlc else 0.04); s.setPen(QPen(QColor("#3c4043"), 1.5)); s.setName("Kurs")
    for j in range(len(d.kategorien)):
        spalte = [w[j] for w in preise if j < len(w)] or [0.0]
        schluss = spalte[-1]
        auf = spalte[0] if ohlc else schluss
        s.append(QCandlestickSet(auf, max(spalte), min(spalte), schluss, float(j)))
    return s


def _saeulen(ch, u: str, d: Daten) -> None:
    from PySide6.QtCharts import (
        QBarSeries, QBarSet, QHorizontalBarSeries, QHorizontalPercentBarSeries, QHorizontalStackedBarSeries, QPercentBarSeries,
        QStackedBarSeries,
    )
    klasse = {"saeule_gruppiert": QBarSeries, "saeule_gestapelt": QStackedBarSeries, "saeule_100": QPercentBarSeries,
              "balken_gruppiert": QHorizontalBarSeries, "balken_gestapelt": QHorizontalStackedBarSeries,
              "balken_100": QHorizontalPercentBarSeries}[u]
    s = klasse()
    for i, n in enumerate(d.namen):
        bs = QBarSet(n); bs.setColor(farbe(i)); bs.setBorderColor(farbe(i))
        for v in d.werte[i]:
            bs.append(v)
        s.append(bs)
    ch.addSeries(s)
    achsen(ch, u, d, [s], waagrecht=u.startswith("balken"))


def _flaeche(ch, u: str, d: Daten) -> None:
    from PySide6.QtCharts import QAreaSeries, QCategoryAxis, QLineSeries, QValueAxis
    stapel = u != "flaeche"
    unten = [0.0] * len(d.kategorien)
    serien = []
    for i, n in enumerate(d.namen):
        oben = [(unten[j] if stapel else 0.0) + v for j, v in enumerate(d.werte[i])]
        hoch, tief = QLineSeries(), QLineSeries()
        for j, v in enumerate(oben):
            hoch.append(j, v); tief.append(j, unten[j] if stapel else 0.0)
        a = QAreaSeries(hoch, tief); a.setName(n)
        hoch.setParent(a); tief.setParent(a)                # QAreaSeries übernimmt die Linien nicht selbst
        c = farbe(i); c.setAlpha(200 if stapel else 150); a.setColor(c); a.setBorderColor(farbe(i))
        ch.addSeries(a); serien.append(a)
        if stapel:
            unten = oben
    ax = QCategoryAxis(); ax.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
    for j, k in enumerate(d.kategorien):
        ax.append(k, j)
    ax.setRange(0, max(1, len(d.kategorien) - 1))
    ay = QValueAxis(); ch.addAxis(ax, Qt.AlignBottom); ch.addAxis(ay, Qt.AlignLeft)
    for a in serien:
        a.attachAxis(ax); a.attachAxis(ay)
    ay.setRange(0, max(d.hoechst, 1e-9)); ay.applyNiceNumbers()


def _blasen(ch, u: str, d: Daten) -> None:
    """Blasen: ab drei Reihen X = 1., Y = 2., Größe = 3. Reihe; sonst X = Rubriknummer, Y = Wert, Größe = Wertebetrag. Je Blase eine Serie
    (QtCharts kennt nur eine Punktgröße je Serie); nur die erste jeder Reihe steht in der Legende."""
    from PySide6.QtCharts import QScatterSeries
    namen, werte = d.namen, d.werte
    voll = len(werte) >= 3
    gruppen = [(namen[1], list(werte[0]), list(werte[1]), list(werte[2]), 1)] if voll else \
        [(n, [j + 1 for j in range(len(w))], list(w), [abs(v) for v in w], i) for i, (n, w) in enumerate(zip(namen, werte))]
    groesse = max((max(g[3], default=0.0) for g in gruppen), default=1.0) or 1.0
    faktor = BLASE_KACHEL if d.kachel else 1.0
    serien = []
    for name, xs, ys, gs, nr in gruppen:
        for k, (x, y, g) in enumerate(zip(xs, ys, gs)):
            s = QScatterSeries(); s.setName(name); s.setMarkerSize(faktor * (BLASE_MIN + BLASE_SPANNE * (abs(g) / groesse) ** 0.5))
            _blase_faerben(s, u, nr)
            s.append(float(x), float(y))
            ch.addSeries(s); serien.append(s)
            if k:
                ch.legend().markers(s)[0].setVisible(False)
    achsen(ch, u, d, serien, kategorie=False)
    _blasen_achsen(ch, d.kategorien, d.werte)


def _blase_faerben(s, u: str, nr: int) -> None:
    """Farbe der Blase; „3D-Blase“ mit Kugelverlauf."""
    c = farbe(nr)
    if u == "punkte_blase_3d":
        gr = QRadialGradient(0.35, 0.35, 0.75); gr.setCoordinateMode(QRadialGradient.ObjectBoundingMode)
        gr.setColorAt(0.0, c.lighter(185)); gr.setColorAt(1.0, c.darker(150))
        s.setBrush(QBrush(gr)); s.setPen(QPen(c.darker(160), 1))
    else:
        c.setAlpha(190); s.setColor(c); s.setBorderColor(farbe(nr))


def _achse_mit_luft(achse, wr: list, kategorien: list, erste_ohne_dreier: bool) -> None:
    lo, hi = min(0.0, min(wr)), max(wr)
    spanne = (hi - lo) or 1.0
    achse.setRange(lo - (0.08 * spanne if lo < 0 else 0.0), hi + 0.18 * spanne); achse.applyNiceNumbers()
    if erste_ohne_dreier:
        achse.setRange(0, len(kategorien) + 1); achse.setTickCount(len(kategorien) + 2); achse.setLabelFormat("%d")


def _blasen_achsen(ch, kategorien, werte) -> None:
    """Achsen der Blasen mit Luft für die großen Punkte."""
    waagr, senkr = ch.axes(Qt.Horizontal), ch.axes(Qt.Vertical)
    voll = len(werte) >= 3
    xs = werte[0] if voll else [j + 1 for j in range(len(kategorien))]
    ys = werte[1] if voll else [v for w in werte for v in w]
    for achse, wr in ((waagr[0] if waagr else None, xs), (senkr[0] if senkr else None, ys)):
        if achse is None or not wr:
            continue
        _achse_mit_luft(achse, wr, kategorien, achse is waagr[0] and not voll)


def _punkte(ch, u: str, d: Daten) -> None:
    from PySide6.QtCharts import QLineSeries, QScatterSeries, QSplineSeries
    serien = []
    glatt, linien = "_glatt" in u, u.startswith(("punkte_glatt", "punkte_gerade"))
    punkte_an = u == "punkte" or u.endswith("_punkte")
    for i, n in enumerate(d.namen):
        if punkte_an:
            s = QScatterSeries(); s.setName(n); s.setColor(farbe(i)); s.setMarkerSize(9); s.setBorderColor(farbe(i))
            for j, v in enumerate(d.werte[i]):
                s.append(j + 1, v)
            ch.addSeries(s); serien.append(s)
        if linien:
            ls = QSplineSeries() if glatt else QLineSeries(); ls.setPen(QPen(farbe(i), 2))
            for j, v in enumerate(d.werte[i]):
                ls.append(j + 1, v)
            ch.addSeries(ls); serien.append(ls)
            if punkte_an:
                ch.legend().markers(ls)[0].setVisible(False)
            else:
                ls.setName(n)
    ax, _ay = achsen(ch, u, d, serien, kategorie=False)
    ax.setRange(0, len(d.kategorien) + 1); ax.setTickCount(len(d.kategorien) + 2); ax.setLabelFormat("%d")


def _netz(ch, u: str, d: Daten) -> None:
    from PySide6.QtCharts import QAreaSeries, QCategoryAxis, QLineSeries, QPolarChart, QValueAxis
    kategorien, werte = d.kategorien, d.werte
    winkel = QCategoryAxis(); winkel.setRange(0, len(kategorien)); winkel.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
    for j, k in enumerate(kategorien):
        winkel.append(k, j)
    radius = QValueAxis(); radius.setLabelFormat("%.0f"); radius.setRange(0, max(d.hoechst, 1e-9)); radius.applyNiceNumbers()
    ch.addAxis(winkel, QPolarChart.PolarOrientationAngular); ch.addAxis(radius, QPolarChart.PolarOrientationRadial)
    for i, n in enumerate(d.namen):
        ls = QLineSeries(); ls.setName(n); ls.setPen(QPen(farbe(i), 2)); ls.setPointsVisible(u == "netz_punkte")
        for j, v in enumerate(werte[i] + werte[i][:1]):
            ls.append(QPointF(j, v))
        if u == "netz_gefuellt":
            null = QLineSeries()
            for j in range(len(werte[i]) + 1):
                null.append(QPointF(j, 0))
            a = QAreaSeries(ls, null); a.setName(n); ls.setParent(a); null.setParent(a)
            c = farbe(i); c.setAlpha(110); a.setColor(c); a.setBorderColor(farbe(i))
            ch.addSeries(a); a.attachAxis(winkel); a.attachAxis(radius)
            continue
        ch.addSeries(ls); ls.attachAxis(winkel); ls.attachAxis(radius)


def _linien(ch, u: str, d: Daten) -> None:
    from PySide6.QtCharts import QLineSeries, QSplineSeries
    serien = []
    stapel = [0.0] * len(d.kategorien)
    for i, n in enumerate(d.namen):
        rf = (d.tf.get(f"reihe_{d.nummern[i]}") or {}).get("reihe") or {} if i < len(d.nummern) else {}
        s = QSplineSeries() if (u == "linie_glatt" or rf.get("glatt")) else QLineSeries()
        s.setName(n); s.setPen(QPen(farbe(i), 2.5)); s.setPointsVisible(u.startswith("linie_punkte") or bool(rf.get("punkte")))
        for j, v in enumerate(d.werte[i]):
            if d.gestapelt and j < len(stapel):
                stapel[j] += v; v = stapel[j]
            s.append(j, v)
        ch.addSeries(s); serien.append(s)
    achsen(ch, u, d, serien)


def _kombi_saeulen(ch, kombi: list, d: Daten, sek: bool, zuordnung: list, hoch: dict) -> None:
    from PySide6.QtCharts import QBarSeries, QBarSet, QStackedBarSeries
    for art, klasse in (("saeule", QBarSeries), ("saeule_gestapelt", QStackedBarSeries)):
        idx = [i for i, (t, s2) in enumerate(kombi) if t == art and s2 == sek]
        if not idx:
            continue
        s = klasse()
        for i in idx:
            bs = QBarSet(d.namen[i]); bs.setColor(farbe(i)); bs.setBorderColor(farbe(i))
            for v in d.werte[i]:
                bs.append(v)
            s.append(bs)
        ch.addSeries(s); zuordnung.append((s, sek))
        h = (max((sum(d.werte[i][j] for i in idx if j < len(d.werte[i])) for j in range(len(d.kategorien))), default=0.0)
             if art == "saeule_gestapelt" else max((max(d.werte[i]) for i in idx if d.werte[i]), default=0.0))
        hoch[sek] = max(hoch[sek], h)


def _kombi_flaechen(ch, kombi: list, d: Daten, sek: bool, zuordnung: list, hoch: dict) -> None:
    from PySide6.QtCharts import QAreaSeries, QLineSeries
    unten = [0.0] * len(d.kategorien)
    for i, (t, s2) in enumerate(kombi):
        if s2 != sek or not t.startswith("flaeche"):
            continue
        gest = t == "flaeche_gestapelt"
        oben = [(unten[j] if gest else 0.0) + v for j, v in enumerate(d.werte[i])]
        o, u2 = QLineSeries(), QLineSeries()
        for j, v in enumerate(oben):
            o.append(j, v); u2.append(j, unten[j] if gest else 0.0)
        a = QAreaSeries(o, u2); a.setName(d.namen[i]); o.setParent(a); u2.setParent(a)
        c = farbe(i); c.setAlpha(170); a.setColor(c); a.setBorderColor(farbe(i))
        ch.addSeries(a); zuordnung.append((a, sek)); hoch[sek] = max(hoch[sek], max(oben, default=0.0))
        if gest:
            unten = oben


def _kombi_linien(ch, kombi: list, d: Daten, sek: bool, zuordnung: list, hoch: dict) -> None:
    from PySide6.QtCharts import QLineSeries
    for i, (t, s2) in enumerate(kombi):
        if s2 != sek or not t.startswith("linie"):
            continue
        ls = QLineSeries(); ls.setName(d.namen[i]); ls.setPen(QPen(farbe(i), 2.5)); ls.setPointsVisible(t == "linie_punkte")
        for j, v in enumerate(d.werte[i]):
            ls.append(j, v)
        ch.addSeries(ls); zuordnung.append((ls, sek)); hoch[sek] = max(hoch[sek], max(d.werte[i], default=0.0))


def _kombination(ch, u: str, d: Daten) -> None:
    """Jede Reihe mit eigenem Typ; Reihen mit Sekundärachse an einer zweiten Werteachse rechts."""
    from PySide6.QtCharts import QBarCategoryAxis, QValueAxis
    kombi = list(d.kombi or kombi_vorgabe(u, len(d.namen)))
    kombi = kombi + [("saeule", False)] * (len(d.namen) - len(kombi))
    ax = QBarCategoryAxis(); ax.append(d.kategorien); ch.addAxis(ax, Qt.AlignBottom)
    links, rechts = QValueAxis(), QValueAxis()
    ch.addAxis(links, Qt.AlignLeft)
    zuordnung: list[tuple[object, bool]] = []
    hoch = {False: 0.0, True: 0.0}
    for sek in (False, True):
        _kombi_saeulen(ch, kombi, d, sek, zuordnung, hoch)
        _kombi_flaechen(ch, kombi, d, sek, zuordnung, hoch)
        _kombi_linien(ch, kombi, d, sek, zuordnung, hoch)
    if any(sek for _s, sek in zuordnung):
        ch.addAxis(rechts, Qt.AlignRight)
    for s, sek in zuordnung:
        s.attachAxis(ax); s.attachAxis(rechts if sek else links)
    for achse, sek in ((links, False), (rechts, True)):
        achse.setRange(0, max(hoch[sek], 1e-9)); achse.applyNiceNumbers()


# Reihenfolge zählt: die erste passende Art gewinnt, alles andere sind Linien
_ARTEN = (
    (ist_kreis, _kreis),
    (lambda u: u == "kombination" or u.startswith("kombi_"), _kombination),
    (lambda u: u.startswith("kurs"), _kurs),
    (lambda u: u.startswith(("saeule", "balken")), _saeulen),
    (lambda u: u.startswith("flaeche"), _flaeche),
    (lambda u: u.startswith("punkte_blase"), _blasen),
    (lambda u: u.startswith("punkte"), _punkte),
    (lambda u: u.startswith("netz"), _netz),
)


def aufbauen(ch, u: str, d: Daten) -> None:
    """Stellt die Serien der Diagrammart ``u`` in das Diagramm."""
    for passt, bauen in _ARTEN:
        if passt(u):
            bauen(ch, u, d)
            return
    _linien(ch, u, d)


def kachel_ausstatten(ch) -> None:
    """Kleines Bildchen (Untertypen im Fenster): schmale Ränder, keine Achsenschrift, Raster und Beschriftungen."""
    ch.setMargins(QMargins(2, 2, 2, 2))
    for achse in ch.axes():
        achse.setLabelsVisible(False); achse.setGridLineVisible(False)
    for serie in ch.series():
        if hasattr(serie, "setLabelsVisible"):
            serie.setLabelsVisible(False)


def datenbeschriftung_ein(ch) -> None:
    for serie in ch.series():
        if hasattr(serie, "setLabelsVisible"):
            serie.setLabelsVisible(True)
        elif hasattr(serie, "setPointLabelsVisible"):
            serie.setPointLabelsVisible(True)
