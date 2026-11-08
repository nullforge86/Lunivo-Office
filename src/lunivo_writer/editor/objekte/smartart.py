"""SmartArt: Listen, Prozesse, Hierarchien (Organigramm), Zyklen und Pyramiden aus einem Baum von Knoten.

Das Objekt ist ein Bild mit gespeicherten Daten (P_OBJEKT, art „smartart“) oder ein freies Objekt (``editor/objekte/frei_objekt.py``): Layout, Knoten
und Farbschema. Es lässt sich jederzeit umstellen und neu schreiben, auch nach dem Speichern als DOCX und erneutem Öffnen in Lunivo Writer.
Grenze: In DOCX steht es als Bild (Titel „lunivo:…“); andere Programme zeigen das Bild, bearbeiten es aber nicht als SmartArt.

Daten (``a["daten"]``): ``layout`` (Schlüssel aus ``LAYOUTS``), ``farben``, ``text`` (eingerückter Text, zwei Leerzeichen je Ebene; Zeilen mit
„• “ sind Aufzählungspunkte des Knotens davor), ``knoten`` = [{id, text, ebene, bullets: [Text], assistent: bool}] in Baumreihenfolge (fehlt er,
entsteht er aus ``text``; sind beide da, gilt ``knoten`` und ``text`` ist dazu gleichgezogen), ``auswahl`` (id des gewählten Knotens),
``hierarchie`` (standard | beide | haengend_links | haengend_rechts), ``stil`` (0 flach, 1 einfach, 2 hell, 3 kräftig, 4 3D/Glanz), ``rtl`` (Layout von
rechts nach links)."""
from __future__ import annotations

import copy
import json
import math
import re

from PySide6.QtCore import QPointF, QRectF, Qt, QUrl
from PySide6.QtGui import (QBrush, QColor, QFont, QImage, QLinearGradient, QPainter, QPen, QPolygonF, QTextDocument, QTextImageFormat)

from lunivo_writer.editor.dokument.zusatz import P_OBJEKT

from lunivo_writer.core.farben import Farbe
from lunivo_writer.editor.diagramme import diagramm_format as F
# Die 15 Layouts des Dialogs „SmartArt-Grafik auswählen“ in der Reihenfolge der Galerie (Zeile für Zeile, vier Spalten) …
KATALOG_LAYOUTS = ["Organigramm", "Blockraster", "Punktliste", "Balkenliste", "Beschreibungsliste", "Spaltenrahmen", "Spalten", "Bildliste",
                   "Perspektive", "Radial", "Prozess", "Konvergenz", "Kartenprozess", "Kreisbeziehung", "Segmentzyklus"]
# … und die älteren Layouts, die weiter gezeichnet werden (bestehende Dokumente, DOCX-Rundweg), aber nicht mehr im Dialog und Menü stehen.
ALTE_LAYOUTS = ["Liste", "Hierarchie", "Zyklus", "Pyramide", "Gruppen", "Matrix", "Chevron", "Zielscheibe", "Trichter", "Zeitachse", "Stufen"]
LAYOUTS = KATALOG_LAYOUTS + ALTE_LAYOUTS
FARBEN = {"Blau": (Farbe.AKZENT, "#5b9bd5", "#a9c9ea"), "Grün": ("#2d8a4e", "#5fb877", "#b4dfc0"), "Orange": ("#e67700", "#f4a259", "#fbd5ae"),
          "Grau": ("#495057", Farbe.GRAU, "#ced4da"), "Bunt": (Farbe.AKZENT, "#e67700", "#2d8a4e")}
MUSTER = {"Organigramm": "Text\n  Text\n    Text\n    Text\n    Text", "Liste": "Erster Punkt\nZweiter Punkt\nDritter Punkt",
          "Prozess": "Planen\nUmsetzen\nPrüfen\nAbschließen",
          "Hierarchie": "Leitung\n  Team A\n    Aufgabe 1\n  Team B", "Zyklus": "Idee\nEntwurf\nTest\nStart", "Pyramide": "Spitze\nMitte\nBasis",
          "Spalten": "Planung\n  Ziele\n  Budget\nUmsetzung\n  Team\n  Termine\nAbschluss\n  Bericht",
          "Gruppen": "Vertrieb\n  Inland\n  Ausland\nTechnik\n  Entwicklung\n  Support",
          "Matrix": "Stärken\nSchwächen\nChancen\nRisiken", "Chevron": "Analyse\nKonzept\nBau\nÜbergabe",
          "Radial": "Kern\nIdee A\nIdee B\nIdee C\nIdee D", "Zielscheibe": "Ziel\nMaßnahme\nAufgabe", "Trichter": "Interessenten\nAngebote\nAufträge",
          "Zeitachse": "2024\n2025\n2026\n2027", "Stufen": "Einstieg\nAufbau\nProfi\nExperte",
          "Blockraster": "Planung\nEntwurf\nBau\nTest\nStart",
          "Punktliste": "Erste Gruppe\n  • Punkt A\n  • Punkt B\nZweite Gruppe\n  • Punkt C\n  • Punkt D",
          "Balkenliste": "Ziel A\n  • Detail 1\n  • Detail 2\nZiel B\n  • Detail 3\nZiel C\n  • Detail 4",
          "Beschreibungsliste": "Begriff A\n  • Erklärung 1\n  • Erklärung 2\nBegriff B\n  • Erklärung 3\nBegriff C\n  • Erklärung 4",
          "Spaltenrahmen": "Überschrift\n  Spalte 1\n  Spalte 2\n  Spalte 3\nFußzeile",
          "Bildliste": "Erster Eintrag\n  • Text 1\n  • Text 2\nZweiter Eintrag\n  • Text 3\nDritter Eintrag\n  • Text 4",
          "Perspektive": "Spalte A\n  • Punkt 1\n  • Punkt 2\nSpalte B\n  • Punkt 3\nSpalte C\n  • Punkt 4",
          "Konvergenz": "Idee A\nIdee B\nIdee C\nErgebnis",
          "Kartenprozess": "Entwurf\nPrüfung\nFreigabe",
          "Kreisbeziehung": "Kern\nBereich A\nBereich B\nBereich C\nBereich D",
          "Segmentzyklus": "Planen\nUmsetzen\nPrüfen\nAnpassen"}
BESCHREIBUNGEN = {
    "Organigramm": "Hiermit stellen Sie hierarchische Informationen oder Berichtsbeziehungen in einer Organisation dar. Die Assistentenform und das "
                   "hängende Layout „Organigramm“ sind für dieses Layout verfügbar.",
    "Liste": "Zeigt nicht aufeinanderfolgende Informationen oder Gruppen von Informationen untereinander. Eingerückte Zeilen bilden Unterpunkte.",
    "Prozess": "Hiermit stellen Sie die Schritte eines Ablaufs nacheinander dar, durch Pfeile verbunden.",
    "Hierarchie": "Stellt hierarchische Informationen oder Berichtsbeziehungen dar, etwa den Aufbau einer Organisation. Eingerückte Zeilen sind untergeordnet.",
    "Zyklus": "Zeigt einen fortlaufenden Prozess, dessen Schritte im Kreis wieder von vorn beginnen.",
    "Pyramide": "Zeigt Beziehungen, die nach oben schmaler werden, etwa Grundlagen unten und Spitze oben.",
    "Spalten": "Hiermit stellen Sie Gruppen dar: je Spalte ein Kopfkasten mit den zugehörigen Aufzählungspunkten darunter.",
    "Gruppen": "Fasst zusammengehörige Punkte in umrahmten Gruppen zusammen.",
    "Matrix": "Zeigt vier Teile in einem Quadrat, etwa für eine Stärken-Schwächen-Analyse.",
    "Chevron": "Zeigt einen Ablauf als Reihe von Pfeilen, die nach rechts weisen.",
    "Radial": "Hiermit stellen Sie Beziehungen zu einem zentralen Kern dar, um den die übrigen Punkte durch Pfeile verbunden angeordnet sind.",
    "Zielscheibe": "Zeigt Ebenen, die sich wie Ringe um ein Ziel in der Mitte legen.",
    "Trichter": "Zeigt, wie sich Mengen in Stufen verringern, etwa vom Interesse zum Auftrag.",
    "Zeitachse": "Zeigt Ereignisse oder Zeitpunkte entlang einer Linie.",
    "Stufen": "Zeigt Schritte, die treppenartig aufeinander aufbauen.",
    "Blockraster": "Hiermit stellen Sie zusammengehörige Informationen als Raster aus gleich großen Blöcken dar.",
    "Punktliste": "Hiermit stellen Sie Gruppen von Informationen dar, unter denen je Gruppe eine Liste von Aufzählungspunkten steht.",
    "Balkenliste": "Hiermit stellen Sie Überschriften als waagerechte Balken dar, daneben je ein Rahmen mit Aufzählungstext.",
    "Beschreibungsliste": "Hiermit stellen Sie Begriffe mit ihren Erklärungen dar: links der Begriff, rechts ein Rahmen mit Text.",
    "Spaltenrahmen": "Hiermit stellen Sie Spalten unter einer gemeinsamen Überschrift dar, abgeschlossen durch eine Fußzeile.",
    "Bildliste": "Hiermit stellen Sie Einträge mit je einem Bild und beschreibendem Text untereinander dar.",
    "Perspektive": "Hiermit stellen Sie Gruppen als nebeneinander stehende, perspektivisch geneigte Spalten mit Text dar.",
    "Konvergenz": "Hiermit stellen Sie dar, wie mehrere Ideen oder Teile zu einem gemeinsamen Ergebnis zusammenlaufen.",
    "Kartenprozess": "Hiermit stellen Sie die Schritte eines Ablaufs als gestapelte Karten dar, durch Pfeile verbunden.",
    "Kreisbeziehung": "Hiermit stellen Sie Beziehungen dar: Um einen großen Kreis liegen überlappende Kreise, die zu ihm gehören.",
    "Segmentzyklus": "Hiermit stellen Sie einen fortlaufenden Prozess als in Segmente geteilten Kreis mit Beschriftungen außen dar."}
ANZEIGENAMEN = {"Organigramm": "Organigramm", "Liste": "Einfache Liste", "Prozess": "Einfacher Prozess", "Hierarchie": "Hierarchie",
                "Zyklus": "Einfacher Zyklus", "Pyramide": "Pyramide", "Spalten": "Gruppierte Spalten", "Gruppen": "Gruppenliste", "Matrix": "Matrix",
                "Chevron": "Pfeilprozess", "Radial": "Radial", "Zielscheibe": "Zielscheibe", "Trichter": "Trichter", "Zeitachse": "Zeitachse",
                "Stufen": "Aufsteigende Stufen", "Blockraster": "Blockraster", "Punktliste": "Liste mit Aufzählung", "Balkenliste": "Horizontale Liste",
                "Beschreibungsliste": "Beschreibungsliste", "Spaltenrahmen": "Gruppierte Spalten", "Bildliste": "Bildliste",
                "Perspektive": "Perspektivische Spalten", "Konvergenz": "Konvergenz", "Kartenprozess": "Kartenprozess", "Kreisbeziehung": "Kreisbeziehung",
                "Segmentzyklus": "Segmentzyklus"}
ANZEIGENAMEN["Spalten"] = "Spaltenliste"; ANZEIGENAMEN["Prozess"] = "Basisprozess"
# Der Katalog des Dialogs „SmartArt-Grafik auswählen“ und des Menüs „Layout ändern“: 15 Layouts in der Reihenfolge der Galerie, Organigramm zuerst.
# Je Eintrag: schluessel (aus KATALOG_LAYOUTS), name, beschreibung, muster (Mustertext)
LAYOUT_KATALOG = [{"schluessel": k, "name": ANZEIGENAMEN[k], "beschreibung": BESCHREIBUNGEN[k], "muster": MUSTER[k]} for k in KATALOG_LAYOUTS]
STANDARD_LAYOUT = "Organigramm"
HIERARCHIEN = (("standard", "Standard"), ("beide", "Beide"), ("haengend_links", "Hängend links"), ("haengend_rechts", "Hängend rechts"))
HIERARCHIE_LAYOUTS = ("Organigramm", "Hierarchie")                       # nur hier wirken Assistent und Hierarchie-Varianten
STILE = ("Flach", "Einfach", "Hell", "Kräftig", "3D")                      # Formenstile (``smartartStil``)
BULLET = "• "


# ---- Datenmodell: Baum aus Knoten ---------------------------------------------------------------------------------------------------
def punkte(text: str) -> list[tuple[int, str]]:
    """[(Ebene, Text)] — die Ebene ergibt sich aus der Einrückung (je zwei Leerzeichen oder ein Tabulator)."""
    out = []
    for zeile in text.splitlines():
        if not zeile.strip():
            continue
        roh = zeile.replace("\t", "  ")
        out.append(((len(roh) - len(roh.lstrip(" "))) // 2, zeile.strip()))
    return out


def knoten_aus_text(text: str) -> list[dict]:
    """Der Knotenbaum (flach, in Reihenfolge) aus dem eingerückten Text; Zeilen mit „• “ werden Aufzählungspunkte des Knotens davor."""
    kn: list[dict] = []
    for e, t in punkte(text):
        if t.startswith(BULLET) and kn:
            kn[-1]["bullets"].append(t[len(BULLET):].strip())
            continue
        kn.append({"id": f"k{len(kn) + 1}", "text": t, "ebene": e, "bullets": []})
    return _glatt(kn)


def _glatt(kn: list[dict]) -> list[dict]:
    """Ebenen so begrenzen, dass kein Knoten mehr als eine Ebene unter seinem Vorgänger steht (der erste steht auf Ebene 0)."""
    for i, k in enumerate(kn):
        k["ebene"] = 0 if i == 0 else max(0, min(int(k["ebene"]), kn[i - 1]["ebene"] + 1))
    return kn


def knoten_von(daten: dict) -> list[dict]:
    """Die Knoten des SmartArt als Kopie: aus ``daten["knoten"]``, sonst aus ``daten["text"]``."""
    kn = daten.get("knoten")
    if isinstance(kn, list) and kn:
        out = [{"id": str(k.get("id") or f"k{i + 1}"), "text": str(k.get("text", "")), "ebene": int(k.get("ebene", 0)),
                "bullets": [str(b) for b in k.get("bullets") or []], **({"assistent": True} if k.get("assistent") else {}),
                **({"format": copy.deepcopy(k["format"])} if k.get("format") else {})} for i, k in enumerate(kn)]
        return _glatt(out)
    return knoten_aus_text(daten.get("text", ""))


def text_aus_knoten(kn: list[dict]) -> str:
    """Der eingerückte Text zu den Knoten (Aufzählungspunkte als „• “-Zeilen eine Ebene tiefer)."""
    zeilen = []
    for k in kn:
        zeilen.append("  " * k["ebene"] + k["text"])
        zeilen += ["  " * (k["ebene"] + 1) + BULLET + b for b in k["bullets"]]
    return "\n".join(zeilen)


def _knotentext(k: dict) -> str:
    return k["text"] + "".join("\n" + BULLET + b for b in k["bullets"])


def _neue_id(kn: list[dict]) -> str:
    nummern = [int(m.group(1)) for k in kn if (m := re.fullmatch(r"k(\d+)", k["id"]))]
    return f"k{max(nummern, default=0) + 1}"


def _index(kn: list[dict], ident) -> int | None:
    return next((i for i, k in enumerate(kn) if k["id"] == ident), None)


def _ende(kn: list[dict], i: int) -> int:
    """Index hinter dem letzten Nachkommen von Knoten ``i`` (Ende seines Teilbaums)."""
    j = i + 1
    while j < len(kn) and kn[j]["ebene"] > kn[i]["ebene"]:
        j += 1
    return j


def _geschwister(kn: list[dict], i: int, richtung: int) -> int | None:
    """Beginn des vorigen (-1) bzw. nächsten (+1) Geschwisters von ``i`` (gleiche Ebene, gleicher Elternknoten) oder None."""
    e = kn[i]["ebene"]
    if richtung > 0:
        j = _ende(kn, i)
        return j if j < len(kn) and kn[j]["ebene"] == e else None
    j = i - 1
    while j >= 0 and kn[j]["ebene"] > e:
        j -= 1
    return j if j >= 0 and kn[j]["ebene"] == e else None


# ---- Knoten bearbeiten (reine Funktionen: liefern eine geänderte Kopie oder None) --------------------------------------------------------
FORM_WIE = ("nach", "vor", "unter", "ueber", "assistent")


def form_einfuegen(kn: list[dict], ident, wie: str, text: str = "Text") -> tuple[list[dict], str] | None:
    """Neuen Knoten einfügen relativ zu ``ident`` (ohne gültige Auswahl: hinter den letzten obersten Knoten): ``nach`` (Geschwister dahinter), ``vor``
    (Geschwister davor), ``unter`` (letztes Kind), ``ueber`` (neuer Elternknoten darüber, der Knoten wird sein Kind), ``assistent`` (Assistent: erstes
    Kind, im Organigramm auf einer eigenen Zeile). → (Knoten, id des neuen) oder None."""
    if wie not in FORM_WIE:
        return None
    kn = copy.deepcopy(kn)
    neu = {"id": _neue_id(kn), "text": text, "ebene": 0, "bullets": []}
    if not kn:
        return [neu], neu["id"]
    i = _index(kn, ident)
    if i is None:
        i = max((j for j, k in enumerate(kn) if k["ebene"] == 0), default=0)
        wie = "nach" if wie in ("vor", "ueber") else wie
    e = kn[i]["ebene"]
    if wie == "nach":
        neu["ebene"] = e; kn.insert(_ende(kn, i), neu)
    elif wie == "vor":
        neu["ebene"] = e; kn.insert(i, neu)
    elif wie == "unter":
        neu["ebene"] = e + 1; kn.insert(_ende(kn, i), neu)
    elif wie == "ueber":
        neu["ebene"] = e
        for k in kn[i:_ende(kn, i)]:
            k["ebene"] += 1
        kn.insert(i, neu)
    else:
        neu["ebene"] = e + 1; neu["assistent"] = True
        j = i + 1
        while j < len(kn) and kn[j]["ebene"] == e + 1 and kn[j].get("assistent"):
            j = _ende(kn, j)
        kn.insert(j, neu)
    return kn, neu["id"]


def kann_level(kn: list[dict], ident, richtung: str) -> bool:
    """Ob ``level(..., "erhoehen")`` bzw. ``"reduzieren"`` für den Knoten geht (der erste Knoten und Knoten, die schon Kind ihres Vorgängers sind,
    lassen sich nicht erhöhen; Knoten der obersten Ebene nicht reduzieren)."""
    i = _index(kn, ident)
    if i is None:
        return False
    if richtung == "erhoehen":
        return i > 0 and kn[i]["ebene"] <= kn[i - 1]["ebene"]
    return kn[i]["ebene"] > 0


def level(kn: list[dict], ident, richtung: str) -> list[dict] | None:
    """Knoten samt Teilbaum eine Ebene tiefer (``erhoehen``) oder höher (``reduzieren``); None, wenn es nicht geht."""
    if not kann_level(kn, ident, richtung):
        return None
    kn = copy.deepcopy(kn)
    i = _index(kn, ident)
    d = 1 if richtung == "erhoehen" else -1
    for k in kn[i:_ende(kn, i)]:
        k["ebene"] += d
    kn[i].pop("assistent", None)
    return kn


def kann_verschieben(kn: list[dict], ident, richtung: str) -> bool:
    i = _index(kn, ident)
    return i is not None and _geschwister(kn, i, 1 if richtung == "zurueck" else -1) is not None


def verschieben(kn: list[dict], ident, richtung: str) -> list[dict] | None:
    """Knoten samt Teilbaum vor das vorige (``vor``) bzw. hinter das nächste (``zurueck``) Geschwister; None, wenn keins da ist."""
    if not kann_verschieben(kn, ident, richtung):
        return None
    kn = copy.deepcopy(kn)
    i = _index(kn, ident)
    ende = _ende(kn, i)
    teil = kn[i:ende]
    if richtung == "vor":
        j = _geschwister(kn, i, -1)
        del kn[i:ende]
        kn[j:j] = teil
    else:
        n_ende = _ende(kn, ende)                                 # Ende des nächsten Geschwisters
        del kn[i:ende]
        kn[n_ende - len(teil):n_ende - len(teil)] = teil
    return kn


def aufzaehlung(kn: list[dict], ident, text: str = "Text") -> list[dict] | None:
    """Einen Aufzählungspunkt an den Knoten hängen."""
    i = _index(kn, ident)
    if i is None:
        return None
    kn = copy.deepcopy(kn)
    kn[i]["bullets"].append(text)
    return kn


# ---- Zeichnen: gemeinsamer Zustand, Hilfen ---------------------------------------------------------------------------------------------
def zeichnen_mit_knoten(daten: dict) -> tuple[QImage, dict[str, QRectF]]:
    """Das SmartArt als Bild und dazu die Rechtecke aller Knoten (id → QRectF in Bildpunkten dieses Bildes)."""
    from lunivo_writer.editor.objekte import smartart_zeichnen as zeichner

    kn = knoten_von(daten)
    pts = [(k["ebene"], _knotentext(k)) for k in kn] or [(0, "…")]
    zeichner._ZU.update(stil=int(daten.get("stil", 1)), rtl=bool(daten.get("rtl")), b=520, reg={}, ids=[k["id"] for k in kn], knoten=kn,
               hier=daten.get("hierarchie", "standard"), fmt=[k.get("format") for k in kn], fmt_alle=daten.get("format") or {})
    img = zeichner._ZEICHNER.get(daten.get("layout", "Liste"), zeichner._pyramide)(daten, pts, 520)
    reg, letzt = dict(zeichner._ZU["reg"]), QRectF(0, 0, img.width(), img.height())
    for ident in zeichner._ZU["ids"]:                                                 # jeder Knoten hat ein Rechteck: sonst das des Knotens davor
        letzt = reg.setdefault(ident, letzt)
    return img, reg


def zeichnen(daten: dict) -> QImage:
    return zeichnen_mit_knoten(daten)[0]


def knoten_rechtecke(daten: dict, b: float = 0, h: float = 0) -> dict[str, QRectF]:
    """id → QRectF der Knoten aus dem Zeichnen. Mit ``b``/``h`` (Größe des Objekts auf dem Blatt) umgerechnet in dessen Bildpunkte, sonst in
    Bildpunkten des gezeichneten Bildes."""
    img, reg = zeichnen_mit_knoten(daten)
    if not (b and h):
        return reg
    sx, sy = b / img.width(), h / img.height()
    return {k: QRectF(r.x() * sx, r.y() * sy, r.width() * sx, r.height() * sy) for k, r in reg.items()}


# ---- Katalog und Einfügen ----------------------------------------------------------------------------------------------------------------
def katalogeintrag(schluessel: str) -> dict:
    return next((e for e in LAYOUT_KATALOG if e["schluessel"] == schluessel), LAYOUT_KATALOG[0])


def neue_daten(eintrag=None, farben: str = "Blau") -> dict:
    """Daten eines neuen SmartArt aus einem Katalogeintrag (oder dessen Schlüssel); ohne Angabe das Standard-Layout (Organigramm) mit Mustertext."""
    e = eintrag if isinstance(eintrag, dict) else katalogeintrag(eintrag or STANDARD_LAYOUT)
    return {"layout": e["schluessel"], "farben": farben, "text": e["muster"]}


def einfuegen(ed, daten) -> None:
    """Fügt das SmartArt als freies Objekt ein (``editor/objekte/frei_objekt.py``): Rahmen, Griffe und Schnellleiste wie bei WordArt. ``daten`` = Daten
    (``layout``, ``text`` …), ein Eintrag aus ``LAYOUT_KATALOG`` oder dessen Schlüssel."""
    from lunivo_writer.editor.objekte import frei_objekt as FO
    if not isinstance(daten, dict) or ("muster" in daten and "schluessel" in daten):
        daten = neue_daten(daten)
    FO.einfuegen(ed, "smartart", dict(daten))


def _inline_daten(ed) -> dict | None:
    """Daten eines älteren, im Text sitzenden SmartArt-Bildes (aus vorhandenen Dokumenten)."""
    f = ed.bild_format()
    if f is None or not f.hasProperty(P_OBJEKT):
        return None
    try:
        o = json.loads(f.property(P_OBJEKT))
    except (ValueError, TypeError):
        return None
    return dict(o.get("daten", {})) if o.get("art") == "smartart" else None


def daten_der_auswahl(ed) -> dict | None:
    """Daten des gewählten SmartArt: zuerst das freie Objekt, sonst ein älteres Bild im Text."""
    from lunivo_writer.editor.objekte import frei_objekt as FO
    d = FO.daten_lesen(ed, "smartart")
    return d if d is not None else _inline_daten(ed)


def aendern(ed, **felder) -> bool:
    """Daten des gewählten SmartArt ändern und neu zeichnen (Breite bleibt, Seitenverhältnis folgt). Ein neuer ``text`` (anders als der zu den
    Knoten gehörende) ersetzt die Knoten; ``knoten=None``, ``auswahl=None``, ``hierarchie=None`` und ``rtl=None`` entfernen die Angabe."""
    from lunivo_writer.editor.objekte import frei_objekt as FO
    neu = {k: v for k, v in felder.items() if v is not None or k in ("knoten", "auswahl", "hierarchie", "rtl", "format")}
    if "text" in neu and "knoten" not in neu:
        d0 = daten_der_auswahl(ed) or {}
        if d0.get("knoten") and neu["text"] != text_aus_knoten(knoten_von(d0)):
            neu["knoten"] = None; neu["auswahl"] = None
        elif d0.get("knoten"):
            neu.pop("text")                                              # unverändert: Knoten (mit Ids und Assistenten) bleiben
    if FO.art_gewaehlt(ed) == "smartart":
        return FO.aendern(ed, "smartart", **neu) if neu else True
    c = ed._bild_cursor()
    d = _inline_daten(ed)
    if c is None or d is None:
        return False
    for k, v in neu.items():
        if v is None:
            d.pop(k, None)
        else:
            d[k] = v
    img = zeichnen(d)
    f = c.charFormat().toImageFormat()
    name = f"obj-{id(img)}-{ed.document().revision()}"
    ed.document().addResource(QTextDocument.ImageResource, QUrl(name), img)
    breite = f.width() or img.width()
    f2 = QTextImageFormat(f)
    f2.setName(name); f2.setWidth(breite); f2.setHeight(breite * img.height() / img.width())
    f2.setProperty(P_OBJEKT, json.dumps({"art": "smartart", "daten": d}, ensure_ascii=False, separators=(",", ":")))
    f2.setProperty(0x100000 + 0x101 + 1, "SmartArt: " + d.get("layout", "Liste") + " mit " + str(len(knoten_von(d))) + " Punkten")
    c.setCharFormat(f2)
    ed.document().setModified(True)
    return True


# ---- Knoten im gewählten SmartArt (Auswahl, Treffer, Text, Befehle) --------------------------------------------------------------------
def knoten_gewaehlt(ed) -> str | None:
    """Id des gewählten Knotens des gewählten SmartArt (freies Objekt) oder None."""
    from lunivo_writer.editor.objekte import frei_objekt as FO
    d = FO.daten_lesen(ed, "smartart")
    a = d.get("auswahl") if d else None
    return a if a and _index(knoten_von(d), a) is not None else None


def knoten_waehlen(ed, ident) -> bool:
    """Knoten wählen (None: Auswahl aufheben). Das Bild wird nicht neu gezeichnet."""
    from lunivo_writer.editor.objekte import frei_objekt as FO
    d = FO.daten_lesen(ed, "smartart")
    if d is None or (ident and _index(knoten_von(d), ident) is None):
        return False
    return FO.daten_still(ed, "smartart", auswahl=ident or None)


def knoten_bei(ed, pos) -> str | None:
    """Die Id des Knotens unter ``pos`` (QPointF im Editor, dieselben Koordinaten wie die Rechtecke von ``ed._frei_liste()``) im gewählten SmartArt;
    Drehung und Zoom sind berücksichtigt. Kein Treffer: None."""
    from lunivo_writer.editor.objekte import frei_objekt as FO
    z = FO.ziel(ed)
    if z is None or z[0] != "smartart":
        return None
    _art, d, key, a, _bild_ = z
    r = next((x[3] for x in ed._frei_liste() if x[0] == key), None)
    if r is None or r.width() <= 0 or r.height() <= 0:
        return None
    from PySide6.QtGui import QTransform
    p = QPointF(pos)
    dreh = float(a.get("dreh", 0.0) or 0.0)
    if dreh:
        p = QTransform().translate(r.center().x(), r.center().y()).rotate(-dreh).translate(-r.center().x(), -r.center().y()).map(p)
    b, h = float(a["b"]), float(a["h"])
    lp = QPointF((p.x() - r.x()) * b / r.width(), (p.y() - r.y()) * h / r.height())
    schl = (json.dumps({k: v for k, v in d.items() if k != "auswahl"}, sort_keys=True, default=str), round(b), round(h))
    c = getattr(ed, "_sa_knoten_cache", None)
    if c is None or c[0] != schl:
        c = (schl, knoten_rechtecke(d, b, h)); ed._sa_knoten_cache = c
    treffer = sorted((rr.width() * rr.height(), k) for k, rr in c[1].items() if rr.contains(lp))
    return treffer[0][1] if treffer else None


def knoten_text(ed, ident) -> str | None:
    """Der Text des Knotens (ohne Aufzählungspunkte) oder None."""
    d = daten_der_auswahl(ed)
    kn = knoten_von(d) if d else []
    i = _index(kn, ident)
    return kn[i]["text"] if i is not None else None


def knoten_text_setzen(ed, ident, text: str) -> bool:
    """Den Text eines Knotens setzen (Eintippen im Knoten) und neu zeichnen."""
    d = daten_der_auswahl(ed)
    kn = knoten_von(d) if d else []
    i = _index(kn, ident)
    if i is None:
        return False
    kn[i]["text"] = text.replace("\n", " ")
    return _knoten_schreiben(ed, kn, ident)


def _knoten_schreiben(ed, kn: list[dict], auswahl) -> bool:
    return aendern(ed, knoten=kn, text=text_aus_knoten(kn), auswahl=auswahl)


# ---- Formatierung (Seitenleiste „Formatierung“): Füllung, Linie, Effekte, Text — im Format des Diagramm-Teilformats --------------------------------
FORMAT_SCHLUESSEL = ("fuell", "linie", "schatten", "leuchten", "reflektion", "weich", "d3", "drehung", "text")


def _format_mischen(fmt: dict, kw: dict) -> dict:
    """Angaben in ein Format einarbeiten: None/False entfernt, ``linie``/``text`` werden mit den vorhandenen Angaben zusammengeführt."""
    for k, v in kw.items():
        if k not in FORMAT_SCHLUESSEL:
            continue
        if v is None or v is False:
            fmt.pop(k, None)
        elif k in ("linie", "text") and isinstance(v, dict):
            neu = {a: b for a, b in {**(fmt.get(k) or {}), **v}.items() if b is not None}
            fmt[k] = neu
            if not neu:
                fmt.pop(k)
        else:
            fmt[k] = v
    return fmt


def format_lesen(ed) -> dict | None:
    """Werte für die Seitenleiste: ``{"format": …, "gewaehlt": Id | None}`` — das Format des gewählten Knotens, ohne Auswahl das von allen Knoten."""
    d = daten_der_auswahl(ed)
    if d is None:
        return None
    ident = knoten_gewaehlt(ed)
    if ident:
        kn = knoten_von(d)
        return {"teil": "diagrammbereich", "format": kn[_index(kn, ident)].get("format") or {}, "gewaehlt": ident}
    return {"teil": "diagrammbereich", "format": d.get("format") or {}, "gewaehlt": None}


def format_setzen(ed, **kw) -> bool:
    """Format des gewählten Knotens (ohne Auswahl: aller Knoten) ändern; ``kw`` wie ``teil_format`` des Diagramms (``fuell``, ``linie``, ``schatten`` …, ``text``)."""
    d = daten_der_auswahl(ed)
    if d is None or not (set(kw) & set(FORMAT_SCHLUESSEL)):
        return False
    ident = knoten_gewaehlt(ed)
    kn = knoten_von(d)
    if ident:
        k = kn[_index(kn, ident)]
        fmt = _format_mischen(dict(k.get("format") or {}), kw)
        k.pop("format", None)
        if fmt:
            k["format"] = fmt
        return _knoten_schreiben(ed, kn, ident)
    fmt = _format_mischen(dict(d.get("format") or {}), kw)
    for k in kn:                                                             # „alle Knoten“ gilt: gleiche Angaben einzelner Knoten fallen weg
        eigen = {a: b for a, b in (k.get("format") or {}).items() if a not in kw}
        k.pop("format", None)
        if eigen:
            k["format"] = eigen
    return aendern(ed, format=fmt or None, knoten=kn, text=text_aus_knoten(kn), auswahl=d.get("auswahl"))


def befehl_form(ed, wie: str) -> bool:
    """``smartartFormEinfuegen``: neuen Knoten relativ zum gewählten (``wie`` siehe ``form_einfuegen``); der neue Knoten wird gewählt."""
    d = daten_der_auswahl(ed)
    if d is None:
        return False
    r = form_einfuegen(knoten_von(d), d.get("auswahl"), wie)
    return bool(r) and _knoten_schreiben(ed, r[0], r[1])


def befehl_level(ed, richtung: str) -> bool:
    d = daten_der_auswahl(ed)
    neu = level(knoten_von(d), d.get("auswahl"), richtung) if d else None
    return neu is not None and _knoten_schreiben(ed, neu, d.get("auswahl"))


def befehl_verschieben(ed, richtung: str) -> bool:
    d = daten_der_auswahl(ed)
    neu = verschieben(knoten_von(d), d.get("auswahl"), richtung) if d else None
    return neu is not None and _knoten_schreiben(ed, neu, d.get("auswahl"))


def befehl_aufzaehlung(ed) -> bool:
    d = daten_der_auswahl(ed)
    neu = aufzaehlung(knoten_von(d), d.get("auswahl")) if d else None
    return neu is not None and _knoten_schreiben(ed, neu, d.get("auswahl"))


def kann(ed, was: str, richtung: str = "") -> bool:
    """Ob ein Knotenbefehl gerade geht (zum Ausgrauen): ``level`` (erhoehen/reduzieren), ``verschieben`` (vor/zurueck), ``knoten`` (ein Knoten ist
    gewählt), ``hierarchie`` (das Layout kennt Hierarchie-Varianten und Assistenten)."""
    d = daten_der_auswahl(ed)
    if d is None:
        return False
    kn, a = knoten_von(d), d.get("auswahl")
    if was == "hierarchie":
        return d.get("layout", "Liste") in HIERARCHIE_LAYOUTS
    if was == "knoten":
        return _index(kn, a) is not None
    if was == "level":
        return kann_level(kn, a, richtung)
    if was == "verschieben":
        return kann_verschieben(kn, a, richtung)
    return False
