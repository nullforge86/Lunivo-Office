"""Diagrammelemente und Teilformate auf das QtCharts-Diagramm anwenden (vor dem Zeichnen): Achsen, Achsentitel, Trendlinien, Schrift und
Linien von Titel, Legende, Achsen, Datenbeschriftungen und Reihen (``daten["teil_format"]``, Aufbau in ``diagramm_format``). Keine Oberfläche."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPen

from . import diagramm_format as F
from . import diagramm_geo as G
from . import diagramm_reihen as R
from . import diagramm_zusatz as Z
from .diagramm_typen import ist_kreis

TREND_ARTEN = ("saeule_gruppiert", "linie", "linie_punkte", "linie_glatt", "flaeche")      # Arten mit Trendlinie (außerdem alle Punktarten ohne Blase)
TREND_BREITE = 1.8


def _waagr_senkr(ch) -> tuple[list, list]:
    return ch.axes(Qt.Horizontal), ch.axes(Qt.Vertical)


def _ist_wertachse(a) -> bool:
    from PySide6.QtCharts import QCategoryAxis, QValueAxis
    return isinstance(a, QValueAxis) and not isinstance(a, QCategoryAxis)


def _achsen_schalten(ch, el: dict) -> None:
    if not el.get("achsen", True):
        for a in ch.axes():
            a.setLabelsVisible(False); a.setLineVisible(False)


def _achsentitel(ch, u: str, el: dict) -> None:
    if not el.get("achsentitel") or ist_kreis(u) or u.startswith("netz"):
        return
    waagr, senkr = _waagr_senkr(ch)
    hb = u.startswith("balken")
    if waagr:
        waagr[0].setTitleText("Werte" if hb else "Rubriken")
    if senkr:
        senkr[0].setTitleText("Rubriken" if hb else "Werte")


def _trend_erlaubt(u: str) -> bool:
    return u in TREND_ARTEN or u.startswith("punkte") and "blase" not in u


def _trendlinien(ch, u: str, el: dict, werte: list, namen: list) -> None:
    from PySide6.QtCharts import QLineSeries
    waagr, senkr = _waagr_senkr(ch)
    if not (el.get("trendlinie") and _trend_erlaubt(u) and waagr and senkr):
        return
    for i, n in enumerate(namen):
        if len(werte[i]) < 2:
            continue
        a0, b0 = Z.trend(werte[i])
        t = QLineSeries(); t.setName(f"Linear ({n})")
        pen = Z.stift({"farbe": R.farbe(i).name(), "breite": TREND_BREITE, "art": "gestrichelt"}); t.setPen(pen)
        versatz = 1 if u.startswith("punkte") else 0
        for j in (0, len(werte[i]) - 1):
            t.append(j + versatz, a0 + b0 * j)
        ch.addSeries(t); t.attachAxis(waagr[0]); t.attachAxis(senkr[0])
        ch.legend().markers(t)[0].setVisible(False)


def _titel_legende(ch, tf: dict, schrift_hex: str) -> None:
    t = Z.text_fuer(tf, "titel")
    if t:
        ch.setTitleFont(F.schrift_aus(ch.titleFont(), t))
        ch.setTitleBrush(QBrush(Qt.transparent if F.text_eigen(t) else F.textfarbe(t, schrift_hex)))      # Verlauf, Kontur, Effekte zeichnet ``Z.eigene_texte``
    t = Z.text_fuer(tf, "legende")
    if t:
        ch.legend().setFont(F.schrift_aus(ch.legend().font(), t))
        ch.legend().setLabelColor(QColor(0, 0, 0, 0) if F.text_eigen(t) else F.textfarbe(t, schrift_hex))
    marken = [m for m in ch.legend().markers() if m.isVisible()]
    for k, m in enumerate(marken):                                             # einzelne Legendeneinträge
        te = tf.get(f"legendeneintrag_{k}", {}).get("text")
        if te:
            tm = {**Z.text_fuer(tf, "legende"), **te}
            m.setFont(F.schrift_aus(m.font(), tm))
            m.setLabelBrush(QBrush(QColor(0, 0, 0, 0) if F.text_eigen(Z.text_fuer(tf, "legende")) else F.textfarbe(tm, schrift_hex)))


def _hauptgitter(ch, u: str, tf: dict) -> None:
    """Linie der Hauptrasterlinien der Wertachse."""
    gl = (tf.get("gitter_haupt") or {}).get("linie")
    if not gl:
        return
    waagr, senkr = _waagr_senkr(ch)
    for a in (waagr if u.startswith("balken") else senkr):
        if _ist_wertachse(a):
            if F.linie_keine(gl):
                a.setGridLineVisible(False)
            else:
                a.setGridLineVisible(True)
                a.setGridLinePen(F.stift({"farbe": a.gridLinePen().color().name(), **gl}))


def _achsen_format(ch, tf: dict, schrift_hex: str) -> None:
    waagr, senkr = _waagr_senkr(ch)
    for teil, liste in (("achse_horizontal", waagr), ("achse_vertikal", senkr)):
        t = Z.text_fuer(tf, teil)
        opt = (tf.get(teil) or {}).get("achse")
        for a in liste:
            if t:
                a.setLabelsFont(F.schrift_aus(a.labelsFont(), t)); a.setTitleFont(F.schrift_aus(a.titleFont(), t))
                fc = F.textfarbe(t, schrift_hex)
                a.setLabelsBrush(QBrush(fc)); a.setTitleBrush(QBrush(fc))
                if F.textwinkel(t):
                    a.setLabelsAngle(int(round(F.textwinkel(t))))
            F.achse_anwenden(a, opt, _ist_wertachse(a))


def _datenbeschriftung(ch, tf: dict, schrift_hex: str) -> None:
    t = Z.text_fuer(tf, "datenbeschriftung")
    if not t:
        return
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


def _reihenformat(fmt: dict, ziel, serie, farbe_name: str) -> None:
    """Linie und Füllung einer Reihe (``linie``, ``fuell`` des Teilformats)."""
    linie, fu = fmt.get("linie"), fmt.get("fuell")
    if F.linie_keine(linie):
        ziel.setPen(QPen(Qt.NoPen))
    elif linie:
        ziel.setPen(F.stift({"farbe": farbe_name, **linie}))
    if F.ist_keine(fu) and hasattr(ziel, "setBrush"):
        ziel.setBrush(QBrush(Qt.NoBrush))
    elif fu and hasattr(ziel, "setBrush"):
        pi, opaz = F.pinsel(fu)
        if pi is not None:
            ziel.setBrush(pi)
        if opaz < 1.0 and serie is not None:
            serie.setOpacity(opaz)


def _luecke(ch, tf: dict, nummern: list) -> None:
    """Lückenbreite gilt für alle Säulen/Balken (QtCharts: eine Breite je Serie)."""
    luecke = next(((tf.get(f"reihe_{nr}") or {}).get("reihe", {}).get("luecke") for nr in nummern
                   if (tf.get(f"reihe_{nr}") or {}).get("reihe", {}).get("luecke") is not None), None)
    if luecke is not None:
        for serie in ch.series():
            if hasattr(serie, "setBarWidth"):
                serie.setBarWidth(F.luecke_zu_breite(luecke))


def _reihen_format(ch, u: str, tf: dict, namen: list, nummern: list) -> None:
    _luecke(ch, tf, nummern)
    for i, (nr, n) in enumerate(zip(nummern, namen)):                       # Füllung und Linie der Reihe
        fmt = tf.get(f"reihe_{nr}") or {}
        if not fmt or ist_kreis(u):
            continue
        serie, bs = G._serie(ch, n)
        ziel = bs if bs is not None else serie
        if ziel is not None:
            _reihenformat(fmt, ziel, serie, R.farbe(i).name())


def anwenden(ch, u: str, el: dict, werte: list, namen: list, nummern: list, tf: dict) -> None:
    """Achsen, Achsentitel, Trendlinien und die Schrift-/Linienformate der Teile (``teil_format``)."""
    _achsen_schalten(ch, el)
    _achsentitel(ch, u, el)
    _trendlinien(ch, u, el, werte, namen)
    if not tf:
        return
    schrift_hex = ch.titleBrush().color().name()
    _titel_legende(ch, tf, schrift_hex)
    _hauptgitter(ch, u, tf)
    _achsen_format(ch, tf, schrift_hex)
    _datenbeschriftung(ch, tf, schrift_hex)
    _reihen_format(ch, u, tf, namen, nummern)
