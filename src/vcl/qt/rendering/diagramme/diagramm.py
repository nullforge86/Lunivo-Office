"""Diagramme als Bild (Einfügen ▸ Diagramm), gezeichnet von der Kern-Engine (``core.layout.drucklayout.ausgabe.diagrammzeichner``). Keine Oberfläche.

    bild("saeule_gestapelt", "Umsatz", ["Q1", "Q2"], {"Nord": [3, 4], "Süd": [2, 5]})   # → QImage

``TYPEN`` ordnet die Untertypen den Gruppen der linken Liste im Fenster zu (wie in der Vorlage: Säule, Linie, Kreis, Balken, Fläche, X Y (Punkt),
Kurs, Netz, Kombination, Vorlagen).

Kombination: ``kombi`` = [(Reihentyp aus ``KOMBI_TYPEN``, Sekundärachse)] je Datenreihe; ``kombi_vorgabe`` liefert die Belegung der
fertigen Kombinationen. Vorlagen: ``VORLAGEN`` = Name → (Untertyp, Farben); ``bild`` nimmt die Farben über ``farben``.
Kurs: Höchst = größter, Tiefst = kleinster Wert der Rubrik, Schluss = letzte, Eröffnung = erste Datenreihe.
"""
from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QImage

from writer.anbindung import diagramm_zusatz as Z
# Katalog und Gestaltung stehen in eigenen Modulen; die Namen bleiben hier erreichbar (``diagramm.TYPEN``, ``diagramm.STILE`` …)
from writer.anbindung.diagrammtypen import art as _art
from writer.anbindung.diagrammtypen import beispiel
from writer.anbindung.diagrammtypen import hat_linien
from writer.anbindung.diagrammtypen import ist_kreis
from writer.anbindung.diagrammtypen import kombi_vorgabe
from writer.anbindung.diagrammtypen import beispiel_kategorien
from writer.anbindung.diagrammtypen import beispiel_reihen
from writer.anbindung.diagrammtypen import kombi_typen
from writer.anbindung.diagrammtypen import namen as _namen
from writer.anbindung.diagrammtypen import typen
from writer.anbindung.diagrammtypen import vorlagen
from vcl.qt.rendering.diagramme.diagramm_stile import FARBSCHEMEN, farbschemen_flach, farbschemen_gruppen
from writer.anbindung.diagramm_stile_modell import stil_extra
from writer.anbindung.diagramm_stile_modell import stile
from writer.anbindung.diagramm_stile_modell import stile_liste


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
    ``stil``: Nummer in ``STILE``. ``elemente`` (achsen, achsentitel, datentabelle, fehlerindikatoren, gitter, trendlinie), ``ausgeblendet``
    (Diagrammfilter), ``teil_format`` (Formate je Diagrammteil); ``geo``: ein leeres Wörterbuch, das mit den Rechtecken der Teile gefüllt wird.
    Gezeichnet wird vom Kern (``core.layout.drucklayout.ausgabe.diagrammzeichner``); hier entsteht nur der Qt-Behälter für die Anzeige."""
    d = {"art": untertyp, "titel": titel, "kategorien": kategorien, "reihen": reihen, "legende": legende, "kombi": kombi, "farben": farben, "kachel": kachel,
         "titel_an": titel_an, "legende_pos": legende_pos, "labels": labels, "stil": stil, "elemente": elemente, "ausgeblendet": ausgeblendet,
         "teil_format": teil_format}
    return _kern_bild(d, b, h, skala, geo)


def _kern_bild(d: dict, b: float, h: float, skala: float, geo: dict | None) -> QImage:
    from vcl.qt.rendering.formen import raster_bild
    from writer.anbindung import zeichnen as ZW
    b, h = max(1, round(b)), max(1, round(h))
    kern_geo: dict = {}

    def erzeuge(flaeche: tuple) -> tuple:
        rasterbild, teile_geo = ZW.diagramm(flaeche, (0, 0, b, h), d, geo is not None)
        kern_geo.update(teile_geo)
        return rasterbild
    bild = raster_bild(b, h, erzeuge, (255, 255, 255, 255), skala)
    if geo is not None:
        for k, r in kern_geo.items():
            geo[k] = [QRectF(*x) for x in r] if isinstance(r, list) else QRectF(*r)
    return bild


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
    return _kern_bild(d, max(120, round(b)), max(90, round(h)), skala, geo)


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
    kat = list(daten.get("kategorien") or beispiel_kategorien())
    reihen = dict(daten.get("reihen") or beispiel_reihen())
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