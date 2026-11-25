"""Diagramm format daten: aus ``vcl.qt.rendering.diagramme.diagramm_format`` herausgelöst."""
from __future__ import annotations


FX_SCHLUESSEL = ("schatten", "reflektion", "leuchten", "weich", "d3", "drehung")


FX_NUR_HINTER = ("schatten", "reflektion", "leuchten", "d3")           # hinter einem Balken, den QtCharts selbst darüber zeichnet


PX_PT = 96.0 / 72.0


PFEIL_GROESSEN = ((1.0, "Klein"), (1.5, "Mittel"), (2.0, "Groß"), (3.0, "Sehr groß"))     # Größe je Pfeil (Anfang und Ende getrennt)


PFEILE = (("keiner", "Kein Pfeil"), ("pfeil", "Pfeil"), ("offen", "Offener Pfeil"), ("oval", "Oval"), ("raute", "Raute"))


FELD_STANDARD = {"vertikal": "mitte", "richtung": "waagerecht", "winkel": 0.0, "anpassen": True, "umbruch": True, "gerade": False,
                 "raender": {"l": 0.0, "o": 0.0, "r": 0.0, "u": 0.0}}


# Vertikale Ausrichtung in der Reihenfolge der Vorlage (Foto 54): „zentriert“ = auch waagerecht mittig (die älteren Schlüssel oben/mitte/unten meinten das schon);
# ohne „zentriert“ steht der Text am linken Rand des Feldes
VERTIKAL = (("oben_links", "Oben"), ("oben", "Oben zentriert"), ("mitte_links", "Mitte"), ("mitte", "Mitte zentriert"),
            ("unten_links", "Unten"), ("unten", "Unten zentriert"))


# Vorbelegung der Ränder des Diagrammtitels (Foto 54): links/rechts 0,10 Inch, oben/unten 0,05 Inch, gespeichert in pt
RAENDER_TITEL = {"l": 7.2, "o": 3.6, "r": 7.2, "u": 3.6}


# ---- Füllung ---------------------------------------------------------------------------------------------------------------------
def fuell_dict(f) -> dict | None:
    """Die Füllung als Wörterbuch; None bei Automatisch (nicht gesetzt) und bei „Keine Füllung“ (``""``)."""
    if not f:
        return None
    return {"art": "farbe", "farbe": f} if isinstance(f, str) else f


def ist_keine(f) -> bool:
    return f == "" or (isinstance(f, dict) and f.get("art") == "keine")


def hauptfarbe(f) -> str | None:
    """Die Farbe, mit der eine Reihe (Legende, Linien, Kreisstücke) gezeichnet wird, wenn der Pinsel selbst nicht möglich ist."""
    d = fuell_dict(f)
    if d is None:
        return None
    if d.get("art", "farbe") in ("graduell", "verlauf"):
        return d.get("dunkel") or d.get("farbe")
    return d.get("farbe") or d.get("dunkel")


_BILDER: dict = {}


# ---- Linie -----------------------------------------------------------------------------------------------------------------------
# Strichtypen des Diagramms in der Reihenfolge der Vorlage (Foto 29): die eine Liste, aus der auch die Seitenleiste ihre Auswahl baut
STRICHTYPEN = (("einfach", "Durchgezogen"), ("rundpunkt", "Rundpunkt"), ("quadratpunkt", "Quadratpunkt"), ("gestrichelt", "Strich"),
               ("strichpunkt", "Strich-Punkt"), ("lang", "Langer Strich"), ("lang_strichpunkt", "Langer Strich-Punkt"),
               ("lang_strichpunktpunkt", "Langer Strich-Punkt-Punkt"))


_ALT_STRICH = {"gepunktet": "quadratpunkt", "fein_gestrichelt": "gestrichelt", "strichpunktpunkt": "lang_strichpunktpunkt"}   # ältere Schlüssel → Auswahl


def strich_schluessel(art: str | None) -> str:
    """Der Schlüssel der Auswahl ``STRICHTYPEN`` zu einer gespeicherten Strichart (ältere Dokumente: ``gepunktet`` …)."""
    art = art or "einfach"
    return art if any(art == k for k, _n in STRICHTYPEN) else _ALT_STRICH.get(art, "einfach")


def linie_keine(linie) -> bool:
    return isinstance(linie, dict) and bool(linie.get("keine"))


# ---- Text ------------------------------------------------------------------------------------------------------------------------
def feld_von(t: dict | None, teil: str | None = None) -> dict:
    """Das Textfeld eines Teils mit Vorgaben; ``teil="titel"`` belegt die Ränder vor (``RAENDER_TITEL``), alle anderen Teile bleiben bei 0."""
    f = (t or {}).get("feld") or {}
    basis = RAENDER_TITEL if teil == "titel" else FELD_STANDARD["raender"]
    return {**FELD_STANDARD, **f, "raender": {**basis, **(f.get("raender") or {})}}


def textwinkel(t: dict | None) -> float:
    """Der Winkel des Textes in Grad (im Uhrzeigersinn): Textrichtung und benutzerdefinierter Winkel zusammen."""
    f = feld_von(t)
    basis = {"waagerecht": 0.0, "dreh90": 90.0, "dreh270": -90.0, "gestapelt": 0.0}.get(f["richtung"], 0.0)
    return max(-180.0, min(180.0, basis + float(f["winkel"] or 0.0)))


def effekt_von(t: dict | None) -> dict:
    return (t or {}).get("effekt") or {}


def text_eigen(t: dict | None) -> bool:
    """Muss der Text selbst gezeichnet werden (QtCharts kann Verläufe, Kontur, Schatten … nicht)? Gilt für Titel und Legende."""
    if not t:
        return False
    e = effekt_von(t)
    if e.get("fuell") in ("keine", "verlauf", "muster", "bild") or e.get("kontur") or any(e.get(k) for k in ("schatten", "reflektion", "leuchten", "d3", "text_3d", "fuell_pinsel")):
        return True
    if (e.get("warp") or {}).get("art", "keine") != "keine":
        return True
    f = feld_von(t)
    return bool(f["richtung"] != "waagerecht" or f["winkel"] or f["anpassen"] is False or f["vertikal"].endswith("_links") or (f["gerade"] and OBJEKT_DREH))


OBJEKT_DREH = 0.0              # Drehung des Diagramms auf dem Blatt (Grad), für „Text nicht drehen“; ``diagramm.bild_aus_daten`` setzt sie je Zeichnung


def schrift_aus(basis, t: dict | None):
    """Die Schrift (``FontSpec`` des Kerns) mit den Angaben des Textformats ``t`` (Name, Größe, fett, kursiv) über der Grundschrift ``basis``."""
    from core.textsatz import FontSpec
    if not t:
        return basis
    return FontSpec(t.get("name") or basis.family, float(t["groesse"]) if t.get("groesse") else basis.size_pt,
                    (700 if t["fett"] else 400) if "fett" in t else basis.weight, bool(t["kursiv"]) if "kursiv" in t else basis.italic)


# ---- Achse und Reihe --------------------------------------------------------------------------------------------------------------
def achse_anwenden(achse, opt: dict | None, wert: bool) -> None:
    """Die Optionen einer Achse (``achse`` im Teilformat) auf die QtCharts-Achse. ``wert``: Wertachse (Minimum, Maximum, Hauptintervall)."""
    if not opt:
        return
    if wert and hasattr(achse, "setRange"):
        _wertachse_anwenden(achse, opt)
    if opt.get("umkehren") and hasattr(achse, "setReverse"):
        achse.setReverse(True)
    if opt.get("beschriftung") == "keine":
        achse.setLabelsVisible(False)


def _wertachse_anwenden(achse, opt: dict) -> None:
    """Bereich, Hauptintervall, Nebenintervall und Zahlenmuster der Wertachse."""
    lo, hi = opt.get("min"), opt.get("max")
    if lo is not None or hi is not None:
        a = float(lo) if lo is not None else achse.min()
        b = float(hi) if hi is not None else achse.max()
        if b > a:
            achse.setRange(a, b)
    if opt.get("intervall") and hasattr(achse, "setTickInterval") and float(opt["intervall"]) > 0:
        achse.setTickType(achse.TickType.TicksDynamic)
        achse.setTickAnchor(achse.min()); achse.setTickInterval(float(opt["intervall"]))
    neben = opt.get("neben")                                     # Nebenintervall → Anzahl der Hilfsstriche zwischen zwei Hauptstrichen
    if neben and float(neben) > 0 and hasattr(achse, "setMinorTickCount"):
        haupt = float(opt["intervall"]) if opt.get("intervall") else (achse.max() - achse.min()) / max(1, achse.tickCount() - 1)
        achse.setMinorTickCount(max(0, int(round(haupt / float(neben))) - 1))
    if opt.get("format") and hasattr(achse, "setLabelFormat"):   # QtCharts kennt nur printf-Muster („%.1f“, „%d“), keine Tabellenkalkulations-Formatecodes
        achse.setLabelFormat(str(opt["format"]))


def luecke_zu_breite(prozent: float) -> float:
    """Lückenbreite in Prozent der Säulenbreite → ``barWidth`` der Serie (Anteil der Kategorie, den die Säulen füllen)."""
    return 1.0 / (1.0 + max(0.0, min(500.0, float(prozent))) / 100.0)


def pfeil_groessen(linie: dict) -> tuple[float, float]:
    """(Größe des Anfangspfeils, Größe des Endpfeils); fehlt die eigene, gilt die gemeinsame ``pfeil_groesse`` älterer Dokumente."""
    alt = float(linie.get("pfeil_groesse", 1.0))
    return float(linie.get("pfeil_groesse_anfang", alt)), float(linie.get("pfeil_groesse_ende", alt))
