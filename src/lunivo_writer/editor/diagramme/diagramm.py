"""Diagramme als Bild (Einfügen ▸ Diagramm), gezeichnet mit QtCharts. Keine Oberfläche.

    bild("saeule_gestapelt", "Umsatz", ["Q1", "Q2"], {"Nord": [3, 4], "Süd": [2, 5]})   # → QImage

``TYPEN`` ordnet die Untertypen den Gruppen der linken Liste im Fenster zu (wie in der Vorlage: Säule, Linie, Kreis, Balken, Fläche, X Y (Punkt),
Kurs, Netz, Kombination, Vorlagen).

Kombination: ``kombi`` = [(Reihentyp aus ``KOMBI_TYPEN``, Sekundärachse)] je Datenreihe; ``kombi_vorgabe`` liefert die Belegung der
fertigen Kombinationen. Vorlagen: ``VORLAGEN`` = Name → (Untertyp, Farben); ``bild`` nimmt die Farben über ``farben``.
Kurs: Höchst = größter, Tiefst = kleinster Wert der Rubrik, Schluss = letzte, Eröffnung = erste Datenreihe.
"""
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPen
from PySide6.QtWidgets import QGraphicsScene

from . import diagramm_elemente as E
from . import diagramm_format as F
from . import diagramm_reihen as R
from . import diagramm_stile as S
from . import diagramm_zusatz as Z
# Katalog und Gestaltung stehen in eigenen Modulen; die Namen bleiben hier erreichbar (``diagramm.TYPEN``, ``diagramm.STILE`` …)
from .diagramm_typen import (                                                                    # noqa: F401
    ALT, BEISPIEL_KATEGORIEN, BEISPIEL_REIHEN, FARBEN, KOMBI_TYPEN, NAMEN, TYPEN, VORLAGEN, _art, beispiel, hat_linien, ist_kreis, kombi_vorgabe,
)
from .diagramm_stile import (                                                                    # noqa: F401
    FARBSCHEMEN, STIL_EXTRA, STILE, farbschemen_flach, farbschemen_gruppen, stile_liste,
)


def _filtern(kategorien: list[str], reihen: dict, ausgeblendet: dict | None) -> tuple[list[int], list[int], list[str], dict]:
    """Diagrammfilter: → (Stellen der sichtbaren Reihen, Stellen der sichtbaren Rubriken, Rubriken, Reihen) ohne die ausgeblendeten."""
    aus = ausgeblendet or {}
    namen = list(reihen)
    nummern = [i for i, n in enumerate(namen) if n not in set(aus.get("reihen") or [])]
    keep = [j for j, k in enumerate(kategorien) if k not in set(aus.get("rubriken") or [])]
    return (nummern, keep, [kategorien[j] for j in keep],
            {namen[i]: [reihen[namen[i]][j] for j in keep if j < len(reihen[namen[i]])] for i in nummern})


def _palette_und_daten(u: str, kategorien: list, reihen: dict, ausgeblendet: dict | None, kombi, kachel: bool, tf: dict, farben: list):
    """Belegt die Palette der Zeichnung und liefert die gefilterten Daten: → (Stellen der Reihen, Rubriken, Reihen, Kombination)."""
    if kachel:
        R.palette_setzen(farben)
        return list(range(len(reihen))), kategorien, reihen, kombi
    nummern, keep, kat, reihen_f = _filtern(kategorien, reihen, ausgeblendet)
    kombi_f = [kombi[i] for i in nummern if i < len(kombi)] if kombi else kombi
    if ist_kreis(u):
        R.palette_setzen([farben[j % len(farben)] for j in keep] or farben)
    else:
        R.palette_setzen([F.hauptfarbe((tf.get(f"reihe_{i}") or {}).get("fuell")) or farben[i % len(farben)] for i in nummern] or farben)
    return nummern, kat, reihen_f, kombi_f


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
    if untertyp in VORLAGEN:
        untertyp, farben = VORLAGEN[untertyp][0], farben or VORLAGEN[untertyp][1]
    u = ALT.get(untertyp, untertyp)
    tf = dict(teil_format or {})
    nummern, kat, reihen_f, kombi_f = _palette_und_daten(u, kategorien, reihen, ausgeblendet, kombi, kachel, tf, list(farben or FARBEN))
    el = {**Z.STANDARD_ELEMENTE, **(elemente or {})}
    ex = STIL_EXTRA.get(stil, {})
    opt = {"el": el, "tf": tf, "nummern": nummern, "geo": geo, "ex": ex}
    try:
        return _bild(untertyp, "" if kachel or not titel_an else titel, kat, reihen_f, b, h, legende and not kachel, kombi_f, kachel,
                     legende_pos, (labels or bool(ex.get("labels"))) and not kachel, stil, skala, opt)
    finally:
        R.palette_setzen(None)


NAMEN_QUELLEN = ("zeile1", "spalte_a", "keine")


def _namen_aus_spalte_a(kategorien: list[str], reihen: dict, aus: dict) -> tuple[list[str], dict, dict | None]:
    namen = list(reihen)
    neu = {k: [(reihen[n][j] if j < len(reihen[n]) else 0.0) for n in namen] for j, k in enumerate(kategorien)}
    return namen, neu, ({"reihen": aus.get("rubriken", []), "rubriken": aus.get("reihen", [])} if aus else None)


def _namen_keine(kategorien: list[str], reihen: dict, aus: dict) -> tuple[list[str], dict, dict | None]:
    rn = {n: f"Reihe {i + 1}" for i, n in enumerate(reihen)}
    kn = {k: str(j + 1) for j, k in enumerate(kategorien)}
    return (list(kn.values()), {rn[n]: v for n, v in reihen.items()},
            {"reihen": [rn[x] for x in aus.get("reihen", []) if x in rn], "rubriken": [kn[x] for x in aus.get("rubriken", []) if x in kn]} if aus else None)


def namen_angewendet(kategorien: list[str], reihen: dict, ausgeblendet: dict | None, quelle: str | None) -> tuple[list[str], dict, dict | None]:
    """Namensquelle (Reiter „Name“ des Diagrammfilters) auf die Daten anwenden, ohne sie zu ändern: ``zeile1`` = wie gespeichert; ``spalte_a`` = die
    Namen kommen aus der ersten Spalte, Reihen und Rubriken tauschen die Plätze; ``keine`` = „Reihe 1 …“ und „1 …“. Der Filter wandert mit."""
    aus = {k: list(v) for k, v in (ausgeblendet or {}).items()}
    if quelle == "spalte_a" and reihen:
        return _namen_aus_spalte_a(kategorien, reihen, aus)
    if quelle == "keine":
        return _namen_keine(kategorien, reihen, aus)
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


@dataclass
class _Zeichnung:
    """Was das Zeichnen eines fertig aufgebauten Diagramms braucht."""
    ch: object
    u: str
    titel: str
    kategorien: list
    werte: list
    namen: list
    nummern: list
    hoechst: float
    b: int
    h: int
    ch_h: float
    skala: float
    stil: int
    kachel: bool
    legende: bool
    labels: bool
    el: dict
    tf: dict
    ex: dict
    geo: dict | None
    schrift: QColor
    tab_h: float


def _ebene_malen(z: _Zeichnung, szene: QGraphicsScene) -> QImage:
    """Das Diagramm auf eine durchsichtige Ebene malen (ohne sichtbares Fenster: in einer eigenen Szene auf Bildgröße)."""
    z.ch.setPos(0, 0); z.ch.resize(z.b, z.ch_h)
    szene.setSceneRect(QRectF(0, 0, z.b, z.ch_h))
    ebene = QImage(max(1, round(z.b * z.skala)), max(1, round(z.h * z.skala)), QImage.Format_ARGB32); ebene.fill(Qt.transparent)
    p = QPainter(ebene); p.setRenderHint(QPainter.Antialiasing); p.scale(z.skala, z.skala)
    szene.render(p, QRectF(0, 0, z.b, z.ch_h), QRectF(0, 0, z.b, z.ch_h))
    if z.u in ("kreis_3d", "kreis_von_kreis", "kreis_balken") and z.werte:
        from . import diagramm_kreis as K
        K.zeichnen(p, QRectF(z.ch.plotArea()), z.u, z.kategorien, z.werte[0], [R.farbe(i) for i in range(len(z.kategorien))],
                   z.labels and not z.kachel, S.stil_schrift(z.stil))
    p.end()
    return ebene


def _geometrie(z: _Zeichnung) -> dict:
    """Lage der Teile (für Texte, Fehlerindikatoren, Pfeile und zum Anklicken); leer, wenn nichts davon gebraucht wird."""
    brauch_geo = z.geo is not None or bool(z.tf) or (z.el.get("fehlerindikatoren") and not z.kachel)
    if not brauch_geo or z.kachel:
        return {}
    from . import diagramm_geo as G
    legenden = _legenden_namen(z.u, z.namen, z.kategorien)
    g = G.geometrie(z.ch, z.u, z.kategorien, z.werte, z.namen, z.nummern, z.b, z.ch_h, z.titel, z.legende, bool(z.el.get("achsen", True)), legenden)
    g["diagrammbereich"] = QRectF(0, 0, z.b, z.h)               # mit der Datentabelle
    for teil in ("titel", "legende"):                        # das Feld um den Text: Größe und Ränder aus den Textoptionen
        if teil in g and z.tf.get(teil):
            g[teil] = F.box_rect(teil, g[teil], Z.text_fuer(z.tf, teil), z.b)
    if z.geo is not None:
        z.geo.update(g)
    return g


def _zusaetze_malen(p: QPainter, z: _Zeichnung, g: dict) -> None:
    """Was QtCharts nicht selbst zeichnet: Texte mit Effekten, Fehlerindikatoren, Linien, Pfeile, Rahmen, Datentabelle."""
    if g and z.tf:
        Z.eigene_texte(p, z.ch, g, z.tf, z.titel, z.schrift.name(), z.legende)
    if g and z.el.get("fehlerindikatoren") and z.namen:
        from . import diagramm_geo as G
        Z.fehlerindikatoren(p, z.ch, z.u, G.punkte(z.ch, z.u, z.kategorien, z.werte, z.namen), z.hoechst, z.schrift)
    if g and z.tf:
        Z.linien(p, g, z.tf)
        Z.pfeile(p, z.ch, z.u, z.kategorien, z.werte, z.namen, z.nummern, z.tf)
    if z.ex.get("rahmen") and not z.kachel:
        p.setBrush(Qt.NoBrush); p.setPen(QPen(QColor(z.ex["rahmen"]), 2)); p.drawRect(QRectF(1, 1, z.b - 2, z.h - 2))
    if z.tab_h:
        Z.tabelle(p, QRectF(8, z.ch_h, z.b - 16, z.tab_h - 6), z.kategorien, z.namen, z.werte, [R.farbe(i) for i in range(len(z.namen))], z.schrift)


def _bild_malen(z: _Zeichnung, ebene: QImage, g: dict) -> QImage:
    """Grund, Hintergründe der Teile, die Ebene mit dem Diagramm und die Zusätze zu einem Bild zusammensetzen."""
    img = QImage(ebene.width(), ebene.height(), QImage.Format_ARGB32)
    img.fill(S.stil_grund(z.stil, z.kachel))
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing); p.scale(z.skala, z.skala)
    if g and z.tf:
        Z.hintergruende(p, g, z.tf, S.stil_grund(z.stil))
    p.resetTransform(); p.drawImage(0, 0, ebene); p.scale(z.skala, z.skala)
    _zusaetze_malen(p, z, g)
    p.end()
    return img


def _chart(u: str, titel: str):
    from PySide6.QtCharts import QChart, QPolarChart
    ch = QPolarChart() if u.startswith("netz") else QChart()
    ch.setTitle(titel); ch.setAnimationOptions(QChart.NoAnimation); ch.setBackgroundRoundness(0)
    return ch


def _legende_einstellen(ch, legende: bool, legende_pos: str) -> None:
    ch.legend().setVisible(legende)
    ch.legend().setAlignment({"oben": Qt.AlignTop, "links": Qt.AlignLeft, "rechts": Qt.AlignRight}.get(legende_pos, Qt.AlignBottom))


def _bild(untertyp, titel, kategorien, reihen, b, h, legende, kombi, kachel=False, legende_pos="unten", labels=False, stil=0, skala=1.0,
          opt=None) -> QImage:
    opt = opt or {"el": dict(Z.STANDARD_ELEMENTE), "tf": {}, "nummern": list(range(len(reihen))), "geo": None, "ex": {}}
    u = ALT.get(untertyp, untertyp)
    ch = _chart(u, titel)
    el, tf, nummern, geo, ex = opt["el"], opt["tf"], opt["nummern"], opt["geo"], opt["ex"]
    namen, werte, gestapelt, hoechst = R.werte_vorbereiten(u, reihen)
    R.aufbauen(ch, u, R.Daten(kategorien, namen, werte, hoechst, gestapelt, kombi, kachel, legende, labels, tf, nummern))
    _legende_einstellen(ch, legende, legende_pos)
    if labels and not kachel:
        R.datenbeschriftung_ein(ch)
    S.stil_anwenden(ch, stil, kachel, bool(el.get("gitter", True)))
    if kachel:
        R.kachel_ausstatten(ch)
    else:
        E.anwenden(ch, u, el, werte, namen, nummern, tf)
    tab_h = (len(namen) + 1) * Z.TABELLE_ZEILE + 8 if el.get("datentabelle") and not kachel and namen else 0
    z = _Zeichnung(ch, u, titel, kategorien, werte, namen, nummern, hoechst, b, h, max(60.0, h - tab_h), skala, stil, kachel, legende, labels,
                   el, tf, ex, geo, S.stil_schrift(stil), tab_h)
    szene = QGraphicsScene(); szene.addItem(ch)
    ebene = _ebene_malen(z, szene)
    img = _bild_malen(z, ebene, _geometrie(z))
    szene.removeItem(ch)
    return img


# ---- Diagrammteile (Auswahl, Anklicken) -----------------------------------------------------------------------------------------
def _legenden_namen(u: str, namen: list[str], kategorien: list[str]) -> list[str]:
    return list(kategorien) if ist_kreis(u) else (["Volumen", "Kurs"] if u.startswith("kurs_v") else ["Kurs"]) if u.startswith("kurs") else list(namen)


def _achsenteile(u: str, el: dict) -> list[tuple[str, str]]:
    """Achsen und Hauptrasterlinie der Wertachse (nur Arten mit Achsen)."""
    if not el["achsen"] or ist_kreis(u) or u.startswith("netz"):
        return []
    hb = u.startswith("balken")
    out = [("achse_horizontal", "Horizontal (Wert) Achse" if hb else "Horizontal (Rubrik) Achse"),
           ("achse_vertikal", "Vertikal (Rubrik) Achse" if hb else "Vertikal (Wert) Achse")]
    if el.get("gitter", True):                                       # Hauptrasterlinie der Wertachse (Foto: direkt nach den Achsen)
        out.append(("gitter_haupt", "Horizontal (Wert) Achse Hauptrasterlinie" if hb else "Vertikal (Wert) Achse Hauptrasterlinie"))
    return out


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
    out += _achsenteile(u, el)
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