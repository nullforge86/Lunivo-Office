"""Native Word-Diagramme (``c:chart`` in ``word/charts/``) lesen und als Bild darstellen.

Gelesen werden Säulen/Balken (gruppiert, gestapelt, 100 %), Linien, Flächen und Kreise mit Rubriken, Reihennamen, Werten und Reihenfarben sowie der Titel.
Gezeichnet wird im Kern (``core/rendering/diagrammzeichner.py``), ohne Qt. Hier steht nur das Lesen der Daten.
Alles Weitere (Achsentitel, Datenbeschriftungen, Sekundärachsen, Datenquelle) bleibt unbeachtet; unbekannte Diagrammarten liefern ``None``."""
from __future__ import annotations

_C = "{http://schemas.openxmlformats.org/drawingml/2006/chart}"
_A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


def _texte(el) -> list[str]:
    return ["".join(pt.findtext(_C + "v") or "") for pt in sorted(el.iter(_C + "pt"), key=lambda p: int(p.get("idx") or 0))] if el is not None else []


def _zahlen(el) -> list[float]:
    aus = []
    for t in _texte(el):
        try:
            aus.append(float(t))
        except ValueError:
            aus.append(0.0)
    return aus


def _untertyp(plot) -> str | None:
    gruppe = (plot.find(_C + "grouping").get("val") if plot.find(_C + "grouping") is not None else "standard")
    art = plot.tag.replace(_C, "")
    if art == "barChart":
        richtung = plot.find(_C + "barDir")
        waagerecht = richtung is not None and richtung.get("val") == "bar"
        name = "balken" if waagerecht else "saeule"
        return f"{name}_{'gestapelt' if gruppe == 'stacked' else '100' if gruppe == 'percentStacked' else 'gruppiert'}"
    if art == "lineChart":
        return "linie" + ("_gestapelt" if gruppe == "stacked" else "_100" if gruppe == "percentStacked" else "")
    if art == "areaChart":
        return "flaeche" + ("_gestapelt" if gruppe == "stacked" else "_100" if gruppe == "percentStacked" else "")
    if art == "pieChart":
        return "kreis"
    if art == "doughnutChart":
        return "ring"
    return None


def diagramm_daten(xml: bytes) -> dict | None:
    """Die Zeichendaten (wie ``bild_aus_daten`` sie nimmt) aus dem Diagrammteil; ``None``, wenn die Art nicht unterstützt wird."""
    import xml.etree.ElementTree as ET
    try:
        wurzel = ET.fromstring(xml)
    except ET.ParseError:
        return None
    flaeche = wurzel.find(f"{_C}chart/{_C}plotArea")
    if flaeche is None:
        return None
    plots = [p for p in flaeche if p.tag.endswith("Chart")]
    if len(plots) != 1:
        return None                                              # Kombinationen und leere Diagramme: nicht darstellbar
    plot = plots[0]
    untertyp = _untertyp(plot)
    if untertyp is None:
        return None
    kategorien: list[str] = []
    reihen: dict[str, list[float]] = {}
    farben: list[str] = []
    for nr, ser in enumerate(plot.findall(_C + "ser")):
        if not kategorien:
            kategorien = _texte(ser.find(_C + "cat"))
        name = "".join(t for t in _texte(ser.find(_C + "tx"))) or ser.findtext(f"{_C}tx/{_C}v") or f"Reihe {nr + 1}"
        while name in reihen:
            name += " "
        reihen[name] = _zahlen(ser.find(_C + "val"))
        farbe = ser.find(f"{_C}spPr/{_A}solidFill/{_A}srgbClr")
        if farbe is not None and farbe.get("val"):
            farben.append("#" + farbe.get("val"))
    if not reihen:
        return None
    laenge = max(len(v) for v in reihen.values())
    kategorien = (kategorien + [str(i + 1) for i in range(len(kategorien), laenge)])[:laenge]
    titel = " ".join(t.text or "" for t in wurzel.iterfind(f"{_C}chart/{_C}title//{_A}t"))
    d = {"art": untertyp, "titel": titel.strip(), "kategorien": kategorien, "reihen": reihen, "legende": len(reihen) > 1 or plot.tag.endswith("pieChart"),
         "titel_an": bool(titel.strip())}
    if len(farben) == len(reihen):
        d["farben"] = farben
    wert_opt: dict = _wertbereich(untertyp, plot, reihen, flaeche.find(f"{_C}valAx"))
    stellen = _zahlenstellen(flaeche.find(f"{_C}valAx/{_C}numFmt"))
    if stellen is not None:
        wert_opt["stellen"] = stellen
    d["wert"] = wert_opt
    d["titel_an"] = bool(d["titel"])
    luecke = plot.find(f"{_C}gapWidth")
    if plot.tag.endswith("barChart"):
        d["luecke"] = float(luecke.get("val")) if luecke is not None and (luecke.get("val") or "").isdigit() else 150.0       # Standard in Word
    return d


def _schritt(spanne: float) -> float:
    """Hauptintervall wie Word: etwa acht Teilstriche , auf 1, 2 oder 5 mal Zehnerpotenz gerundet."""
    import math
    roh = spanne / 10.0 if spanne > 0 else 1.0
    exp = math.floor(math.log10(roh))
    for faktor in (1, 2, 5, 10):
        if faktor * 10 ** exp >= roh:
            return faktor * 10 ** exp
    return 10 ** (exp + 1)


def _wertbereich(untertyp: str, plot, reihen: dict, wertachse) -> dict:
    """Wertachse (Minimum, Maximum, Hauptintervall): aus der Datei, sonst wie Word; nur für nicht gestapelte Diagramme mit positiven Werten."""
    import math
    opt: dict = {}
    skala = wertachse.find(f"{_C}scaling") if wertachse is not None else None
    for name, schl in (("min", "min"), ("max", "max")):
        el = skala.find(_C + name) if skala is not None else None
        if el is not None and el.get("val"):
            try:
                opt[schl] = float(el.get("val"))
            except ValueError:
                pass
    einheit = wertachse.find(f"{_C}majorUnit") if wertachse is not None else None
    if einheit is not None and einheit.get("val"):
        try:
            opt["intervall"] = float(einheit.get("val"))
        except ValueError:
            pass
    if untertyp.endswith(("_gestapelt", "_100")) or untertyp in ("kreis", "ring"):
        return opt
    werte = [w for v in reihen.values() for w in v]
    if not werte or min(werte) < 0:
        return opt
    spitze = max(werte)
    if "intervall" not in opt and spitze > 0:
        opt["intervall"] = _schritt(spitze * 1.05)
    if "max" not in opt and spitze > 0 and opt.get("intervall"):
        opt["max"] = math.ceil(spitze * 1.05 / opt["intervall"] - 1e-9) * opt["intervall"]
    opt.setdefault("min", 0.0)
    return opt


def _zahlenstellen(numfmt) -> int | None:
    """Nachkommastellen aus dem Excel-Formatcode der Wertachse (``0`` → 0, ``0.00`` → 2); ``None`` bei anderem (Prozent, Datum …)."""
    code = (numfmt.get("formatCode") if numfmt is not None else "") or ""
    if not code or code in ("General", "Standard") or "%" in code or any(c in code for c in "dmyhsE"):
        return None
    return len(code.split(".", 1)[1].rstrip(";")) if "." in code else 0


def ohne_datenquelle(xml: bytes) -> str:
    """Diagrammteil als Text ohne den Verweis auf die eingebettete Arbeitsmappe (sie wird nicht mitgeführt)."""
    import re
    text = xml.decode("utf-8", errors="replace")
    return re.sub(r"<c:externalData\b.*?</c:externalData>|<c:externalData\b[^>]*/>", "", text, flags=re.S)
