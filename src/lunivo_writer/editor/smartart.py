"""SmartArt: Listen, Prozesse, Hierarchien (Organigramm), Zyklen und Pyramiden aus einem Baum von Knoten.

Das Objekt ist ein Bild mit gespeicherten Daten (P_OBJEKT, art „smartart“) oder ein freies Objekt (``editor/frei_objekt.py``): Layout, Knoten
und Farbschema. Es lässt sich jederzeit umstellen und neu schreiben, auch nach dem Speichern als DOCX und erneutem Öffnen in Lunivo Writer.
Grenze: In DOCX steht es als Bild (Titel „lunivo:…“); Word und LibreOffice zeigen das Bild, bearbeiten es aber nicht als SmartArt.

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

from lunivo_writer.editor.zusatz import P_OBJEKT

from lunivo_writer.core.farben import Farbe
from lunivo_writer.editor import diagramm_format as F
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
_ZU: dict = {"stil": 1, "rtl": False, "b": 520, "reg": {}, "ids": [], "knoten": [], "hier": "standard", "fmt": [], "fmt_alle": {}}


def _format_von(nr) -> dict | None:
    """Das Format des Knotens Nummer ``nr`` (Format wie ``teil_format`` des Diagramms): das des Knotens über dem von allen Knoten (``daten["format"]``)."""
    alle = _ZU.get("fmt_alle") or {}
    eigen = _ZU["fmt"][nr] if nr is not None and 0 <= nr < len(_ZU["fmt"]) else None
    if not alle and not eigen:
        return None
    f = {**alle, **(eigen or {})}
    for k in ("linie", "text"):
        if alle.get(k) and (eigen or {}).get(k):
            f[k] = {**alle[k], **eigen[k]}
    return f


def _spiegel(r: QRectF) -> QRectF:
    return QRectF(_ZU["b"] - r.right(), r.top(), r.width(), r.height()) if _ZU["rtl"] else QRectF(r)


def _merke(i, r: QRectF) -> None:
    """Rechteck des Knotens Nummer ``i`` (Stelle in der Knotenliste) für ``knoten_rechtecke`` merken."""
    if i is not None and 0 <= i < len(_ZU["ids"]):
        _ZU["reg"][_ZU["ids"][i]] = _spiegel(r)


def _farbe(daten: dict, ebene: int) -> QColor:
    f = FARBEN.get(daten.get("farben", "Blau"), FARBEN["Blau"])
    return QColor(f[min(ebene, 2)] if daten.get("farben") != "Bunt" else f[ebene % 3])


def _stilfarbe(c: QColor) -> QColor:
    """Die Füllfarbe, die der Formenstil aus der Farbe macht (für den Textkontrast)."""
    s = _ZU["stil"]
    return c.lighter(185) if s == 2 else c.darker(112) if s == 3 else QColor(c)


def _text_farbe(c: QColor) -> QColor:
    return QColor(Farbe.WEISS) if c.lightness() < 150 else QColor(Farbe.TINTE_DUNKEL)


def _fuellen(p: QPainter, c: QColor, r: QRectF) -> None:
    """Stift und Pinsel nach dem Formenstil: 0 flach (ohne Rand), 1 einfach, 2 hell (Farbrand), 3 kräftig (dicker dunkler Rand), 4 3D (Verlauf)."""
    s, f = _ZU["stil"], _stilfarbe(c)
    if s == 0:
        p.setPen(Qt.NoPen); p.setBrush(QBrush(f))
    elif s == 2:
        p.setPen(QPen(c, 2)); p.setBrush(QBrush(f))
    elif s == 3:
        p.setPen(QPen(c.darker(170), 3)); p.setBrush(QBrush(f))
    elif s == 4:
        g = QLinearGradient(r.topLeft(), r.bottomLeft()); g.setColorAt(0, c.lighter(150)); g.setColorAt(1, c.darker(120))
        p.setPen(QPen(c.darker(150), 1.5)); p.setBrush(QBrush(g))
    else:
        p.setPen(QPen(c.darker(125), 1.5)); p.setBrush(QBrush(f))


def _text_zeichnen(p: QPainter, r: QRectF, flags, t: str) -> None:
    """Text immer ungespiegelt (auch bei „von rechts nach links“, wo die Formen gespiegelt werden)."""
    if _ZU["rtl"]:
        p.save(); p.resetTransform(); p.drawText(_spiegel(r), flags, t); p.restore()
    else:
        p.drawText(r, flags, t)


def _schrift(p: QPainter, text: str, groesse: float) -> None:
    f = QFont(p.font()); f.setPointSizeF(groesse if "\n" not in text else min(groesse, 9.0)); p.setFont(f)


def _kasten(p: QPainter, r: QRectF, text: str, c: QColor, rund: float = 8, nr=None) -> None:
    fm = _format_von(nr)
    _fuellen(p, c, r)
    if fm:                                                                   # eigenes Format (Füllung, Linie, Effekte, Text) über dem Formenstil
        fu, li, fx = fm.get("fuell"), fm.get("linie"), F.fx_normal(fm)
        if fx:
            F.teil_zeichnen(p, r, {"fuell": fu if fu is not None else c.name(), **fx}, c); p.setBrush(Qt.NoBrush)
        elif fu is not None:
            br, opaz = F.pinsel(fu, r)
            if br is None:
                p.setBrush(Qt.NoBrush)
            else:
                if opaz < 1 and br.style() == Qt.SolidPattern:
                    col = QColor(br.color()); col.setAlphaF(opaz); br = QBrush(col)
                p.setBrush(br)
        if li:
            p.setPen(Qt.NoPen if F.linie_keine(li) else F.stift(li, c.darker(125).name(), r))
    p.drawRoundedRect(r, rund, rund)
    if _ZU["stil"] == 4:                                                    # Glanz: die obere Hälfte heller
        p.setPen(Qt.NoPen); p.setBrush(QColor(255, 255, 255, 55))
        p.drawRoundedRect(QRectF(r.left() + 2, r.top() + 2, r.width() - 4, r.height() / 2 - 2), rund, rund)
    p.setPen(_text_farbe(_stilfarbe(c)))
    _schrift(p, text, 11)
    t = (fm or {}).get("text")
    if t:
        p.setFont(F.schrift_aus(p.font(), t))
        if t.get("farbe") or t.get("effekt"):
            p.setPen(F.textfarbe(t, p.pen().color().name()))
    _text_zeichnen(p, r.adjusted(6, 3, -6, -3), Qt.AlignCenter | Qt.TextWordWrap, text)
    _merke(nr, r)


def _pfeil(p: QPainter, a: QPointF, b: QPointF, c: QColor) -> None:
    p.setPen(QPen(c, 2)); p.drawLine(a, b)
    w = math.atan2(b.y() - a.y(), b.x() - a.x())
    for d in (0.45, -0.45):
        p.drawLine(b, QPointF(b.x() - 9 * math.cos(w - d), b.y() - 9 * math.sin(w - d)))


def _bild(b: float, h: float) -> tuple[QImage, QPainter]:
    img = QImage(int(b), int(h), QImage.Format_ARGB32); img.fill(Qt.transparent)
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing)
    if _ZU["rtl"]:
        p.translate(int(b), 0); p.scale(-1, 1)
    return img, p


def _text(p: QPainter, r: QRectF, t: str, c: QColor, groesse: float = 11) -> None:
    p.setPen(_text_farbe(_stilfarbe(c))); _schrift(p, t, groesse)
    _text_zeichnen(p, r, Qt.AlignCenter | Qt.TextWordWrap, t)


def _gruppen(pts: list[tuple[int, str]]) -> list[tuple[int, str, list[tuple[int, str]]]]:
    """Oberste Ebene als Überschrift, alles Eingerückte darunter als Unterpunkte: [(Nr. der Überschrift, Text, [(Nr., Unterpunkt)])]."""
    out: list[tuple[int, str, list[tuple[int, str]]]] = []
    for i, (e, t) in enumerate(pts):
        if e == 0 or not out:
            out.append((i, t, []))
        else:
            out[-1][2].append((i, t))
    return out


def _bunt(daten: dict, i: int) -> QColor:
    return _farbe(daten, i if daten.get("farben") == "Bunt" else 0)


def _spalten(daten: dict, pts, b: int) -> QImage:
    g = _gruppen(pts)
    n = len(g)
    bw = (b - 16 - (n - 1) * 10) / n
    zeilen = max(len(k) for _i, _t, k in g)
    img, p = _bild(b, 16 + 50 + max(1, zeilen) * 34 + 14)
    for i, (ni, t, kinder) in enumerate(g):
        x = 8 + i * (bw + 10)
        c = _bunt(daten, i)
        p.setPen(QPen(c.darker(125), 1.5)); p.setBrush(QBrush(c.lighter(185)))
        p.drawRoundedRect(QRectF(x, 36, bw, img.height() - 44), 6, 6)
        _kasten(p, QRectF(x, 8, bw, 44), t, c, nr=ni)
        for j, (nj, k) in enumerate(kinder):
            r = QRectF(x + 4, 60 + j * 34, bw - 8, 30)
            _text(p, r, k, c.lighter(185)); _merke(nj, r)
    p.end()
    return img


def _gruppenliste(daten: dict, pts, b: int) -> QImage:
    g = _gruppen(pts)
    img, p = _bild(b, 16 + len(g) * 62)
    for i, (ni, t, kinder) in enumerate(g):
        y = 8 + i * 62
        c = _bunt(daten, i)
        _kasten(p, QRectF(8, y, 130, 54), t, c, nr=ni)
        n = max(1, len(kinder))
        kw = (b - 16 - 146 - (n - 1) * 8) / n
        for j, (nj, k) in enumerate(kinder):
            _kasten(p, QRectF(146 + j * (kw + 8), y + 6, kw, 42), k, _farbe(daten, 1 if daten.get("farben") != "Bunt" else i), 6, nr=nj)
    p.end()
    return img


def _matrix(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    sp = 2 if n > 1 else 1
    zl = -(-n // sp)
    kw, kh = (b - 16 - (sp - 1) * 10) / sp, 84
    img, p = _bild(b, 16 + zl * kh + (zl - 1) * 10)
    for i, (_e, t) in enumerate(pts):
        z, s = divmod(i, sp)
        _kasten(p, QRectF(8 + s * (kw + 10), 8 + z * (kh + 10), kw, kh), t,
                _bunt(daten, i) if daten.get("farben") == "Bunt" else _farbe(daten, 0 if (z + s) % 2 == 0 else 1), 10, nr=i)
    p.end()
    return img


def _chevron(daten: dict, pts, b: int) -> QImage:
    je = 4
    zeilen = -(-len(pts) // je)
    n = min(len(pts), je)
    sp = 14.0
    w = (b - 16 + (n - 1) * 8) / n                                          # Pfeile greifen ineinander
    img, p = _bild(b, 16 + zeilen * 84)
    for i, (_e, t) in enumerate(pts):
        z, s = divmod(i, je)
        x, y, h = 8 + s * (w - 8), 8 + z * 84, 72
        c = _bunt(daten, i)
        poly = QPolygonF([QPointF(x, y), QPointF(x + w - sp, y), QPointF(x + w, y + h / 2), QPointF(x + w - sp, y + h), QPointF(x, y + h),
                          QPointF(x + sp, y + h / 2)])
        _fuellen(p, c, QRectF(x, y, w, h)); p.drawPolygon(poly)
        _text(p, QRectF(x + sp + 4, y + 4, w - 2 * sp - 8, h - 8), t, c, 10.5)
        _merke(i, QRectF(x, y, w, h))
    p.end()
    return img


def _radial(daten: dict, pts, b: int) -> QImage:
    h = 380
    img, p = _bild(b, h)
    mx, my = b / 2, h / 2
    rest = pts[1:]
    n = max(1, len(rest))
    pos = [QPointF(mx + 190 * math.cos(-math.pi / 2 + 2 * math.pi * i / n), my + 135 * math.sin(-math.pi / 2 + 2 * math.pi * i / n)) for i in range(len(rest))]
    for q in pos:                                                    # Pfeile vom Kern zu den Kästen, jeweils am Rand der Kästen
        dx, dy = q.x() - mx, q.y() - my
        def rand(hb, hh):
            return min(hb / abs(dx) if dx else 1e9, hh / abs(dy) if dy else 1e9)
        t0, t1 = rand(62 + 4, 40 + 4), 1 - rand(56 + 4, 24 + 4)
        if t1 > t0:
            _pfeil(p, QPointF(mx + dx * t0, my + dy * t0), QPointF(mx + dx * t1, my + dy * t1), QColor(Farbe.GRAU))
    for i, q in enumerate(pos):
        _kasten(p, QRectF(q.x() - 56, q.y() - 24, 112, 48), rest[i][1], _farbe(daten, 1 if daten.get("farben") != "Bunt" else i + 1), 24, nr=i + 1)
    _kasten(p, QRectF(mx - 62, my - 40, 124, 80), pts[0][1], _farbe(daten, 0), 40, nr=0)
    p.end()
    return img


def _zielscheibe(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    band = 34.0
    rad = max(150.0, band * n + 20)
    img, p = _bild(b, 2 * rad + 16)
    mx, my = b / 2, rad + 8
    for i, (_e, t) in enumerate(pts):
        r = rad - i * (rad - 20) / n
        c = _bunt(daten, i) if daten.get("farben") == "Bunt" else _farbe(daten, min(i, 2)).lighter(100 + 25 * max(0, i - 2))
        _fuellen(p, c, QRectF(mx - r, my - r, 2 * r, 2 * r)); p.drawEllipse(QPointF(mx, my), r, r)
        feld = QRectF(mx - r * 0.7, my - r + 4, r * 1.4, (rad - 20) / n - 6 if n > 1 else 40)
        _text(p, feld, t, c); _merke(i, feld)
    p.end()
    return img


def _trichter(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    zh = 54
    img, p = _bild(b, 16 + n * zh)
    mitte, halb = b / 2, (b - 16) / 2
    for i, (_e, t) in enumerate(pts):
        oben, unten = 8 + i * zh, 8 + (i + 1) * zh - 4
        bo, bu = halb * (1 - i / (n + 1)), halb * (1 - (i + 1) / (n + 1))
        c = _farbe(daten, i if daten.get("farben") == "Bunt" else min(i, 2))
        _fuellen(p, c, QRectF(mitte - bo, oben, 2 * bo, unten - oben))
        p.drawPolygon(QPolygonF([QPointF(mitte - bo, oben), QPointF(mitte + bo, oben), QPointF(mitte + bu, unten), QPointF(mitte - bu, unten)]))
        _text(p, QRectF(mitte - bu * 0.85, oben, bu * 1.7, unten - oben), t, c)
        _merke(i, QRectF(mitte - bo, oben, 2 * bo, unten - oben))
    p.end()
    return img


def _zeitachse(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    img, p = _bild(b, 220)
    y = 110.0
    p.setPen(QPen(QColor(Farbe.GRAU), 3)); p.drawLine(QPointF(8, y), QPointF(b - 8, y))
    raster = (b - 16) / n
    for i, (_e, t) in enumerate(pts):
        x = 8 + raster * (i + 0.5)
        c = _bunt(daten, i)
        oben = i % 2 == 0
        p.setPen(QPen(QColor(Farbe.GRAU), 1.5)); p.drawLine(QPointF(x, y), QPointF(x, y - 26 if oben else y + 26))
        _kasten(p, QRectF(x - min(raster - 6, 120) / 2, y - 80 if oben else y + 26, min(raster - 6, 120), 54), t, c, nr=i)
        _fuellen(p, c, QRectF(x - 8, y - 8, 16, 16)); p.drawEllipse(QPointF(x, y), 8, 8)
    p.end()
    return img


def _stufen(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    sh = 44
    h = 16 + n * sh + 20
    img, p = _bild(b, h)
    sw = (b - 16) / n
    for i, (_e, t) in enumerate(pts):
        r = QRectF(8 + i * sw, h - 8 - (i + 1) * sh - 0, sw - 4, (i + 1) * sh)
        _kasten(p, r, "", _bunt(daten, i) if daten.get("farben") == "Bunt" else _farbe(daten, min(i, 2)), 4, nr=i)
        _text(p, QRectF(r.left() + 2, r.top() + 2, r.width() - 4, 38), t, _farbe(daten, i if daten.get("farben") == "Bunt" else min(i, 2)), 10.5)
    p.end()
    return img


# ---- Organigramm / Hierarchie ---------------------------------------------------------------------------------------------------------
def _baum(pts) -> list[dict]:
    """Die Wurzeln des Knotenbaums; jeder Knoten {i (Nr.), t (Text), e (Ebene), k (Kinder), a (Assistent)}."""
    kn = _ZU["knoten"]
    wurzeln: list[dict] = []
    stapel: list[dict] = []
    for i, (e, t) in enumerate(pts):
        n = {"i": i, "t": t, "e": e, "k": [], "a": bool(kn[i].get("assistent")) if i < len(kn) else False}
        while stapel and stapel[-1]["e"] >= e:
            stapel.pop()
        (stapel[-1]["k"] if stapel else wurzeln).append(n)
        stapel.append(n)
    return wurzeln


def _alle(n: dict):
    yield n
    for k in n["k"]:
        yield from _alle(k)


def _standard_baum(daten: dict, wurzeln, b: int) -> QImage:
    """Blätter nebeneinander, Eltern mittig über ihren Kindern; Assistenten stehen eine Zeile unter dem Eltern, die übrigen Kinder darunter."""
    blaetter = [0]
    maxz = [0]

    def zeilen(n, z):
        n["z"] = z; maxz[0] = max(maxz[0], z)
        ass = [c for c in n["k"] if c["a"]]
        for c in ass:
            zeilen(c, z + 1)
        for c in (c for c in n["k"] if not c["a"]):
            zeilen(c, z + 1 + (1 if ass else 0))

    def setze(n):
        if not n["k"]:
            n["x"] = blaetter[0]; blaetter[0] += 1
        else:
            kinder = [c for c in n["k"] if c["a"]] + [c for c in n["k"] if not c["a"]]
            for k in kinder:
                setze(k)
            n["x"] = (kinder[0]["x"] + kinder[-1]["x"]) / 2
    for w in wurzeln:
        zeilen(w, 0); setze(w)
    spalten = max(1, blaetter[0])
    bw = min(130.0, (b - 16) / spalten - 8)
    img, p = _bild(b, 16 + (maxz[0] + 1) * 78)
    raster = (b - 16) / spalten

    def box(n):
        return QRectF(8 + n["x"] * raster + (raster - bw) / 2, 8 + n["z"] * 78, bw, 50)

    def mal(n):
        r = box(n)
        for k in n["k"]:
            kr = box(k)
            mitte = (r.bottom() + kr.top()) / 2
            p.setPen(QPen(QColor(Farbe.GRAU), 1.5))
            p.drawLine(QPointF(r.center().x(), r.bottom()), QPointF(r.center().x(), mitte))
            p.drawLine(QPointF(r.center().x(), mitte), QPointF(kr.center().x(), mitte))
            p.drawLine(QPointF(kr.center().x(), mitte), QPointF(kr.center().x(), kr.top()))
        _kasten(p, r, n["t"], _farbe(daten, n["e"]), nr=n["i"])
        for k in n["k"]:
            mal(k)
    for w in wurzeln:
        mal(w)
    p.end()
    return img


def _haengend_baum(daten: dict, wurzeln, b: int, variante: str) -> QImage:
    """Hängende Layouts: die Kinder stehen untereinander neben einer senkrechten Linie unter dem Eltern (links, rechts oder abwechselnd beidseits)."""
    tiefe = max((n["e"] for w in wurzeln for n in _alle(w)), default=0)
    versatz = 26.0
    bw = max(70.0, min(150.0, b - 16 - (tiefe + 1) * versatz * (2 if variante == "beide" else 1)))
    zh = 46.0

    def platz(n, x, z, seite):
        """Knoten bei Spalte x (linke Kante) und Zeile z; → nächste freie Zeile. ``seite``: rechts | links | beide."""
        n["x"], n["z"], n["seite"] = x, z, seite
        if not n["k"]:
            return z + 1
        if seite == "beide":
            zz = {"rechts": z + 1, "links": z + 1}
            for j, c in enumerate(n["k"]):
                s = "rechts" if j % 2 == 0 else "links"
                cx = x + bw / 2 + 10 if s == "rechts" else x + bw / 2 - 10 - bw
                zz[s] = platz(c, cx, zz[s], s)
            return max(zz.values())
        zn = z + 1
        for c in n["k"]:
            zn = platz(c, x + versatz if seite == "rechts" else x - versatz, zn, seite)
        return zn
    zeile = 0
    for w in wurzeln:
        zeile = platz(w, 0.0, zeile, "beide" if variante == "beide" else variante.replace("haengend_", ""))
    alle = [n for w in wurzeln for n in _alle(w)]
    links = min(n["x"] for n in alle)
    breite = max(n["x"] for n in alle) + bw - links
    ox = 8 - links + max(0.0, (b - 16 - breite) / 2)
    img, p = _bild(b, 16 + zeile * zh + 4)

    def box(n):
        return QRectF(n["x"] + ox, 8 + n["z"] * zh, bw, zh - 8)

    def mal(n):
        r = box(n)
        if n["k"]:
            tx = r.center().x() if n["seite"] == "beide" else r.left() + versatz / 2 if n["seite"] == "rechts" else r.right() - versatz / 2
            p.setPen(QPen(QColor(Farbe.GRAU), 1.5))
            p.drawLine(QPointF(tx, r.bottom()), QPointF(tx, max(box(c).center().y() for c in n["k"])))
            for c in n["k"]:
                kr = box(c)
                p.drawLine(QPointF(tx, kr.center().y()), QPointF(kr.left() if kr.center().x() > tx else kr.right(), kr.center().y()))
        _kasten(p, r, n["t"], _farbe(daten, n["e"]), 6, nr=n["i"])
        for c in n["k"]:
            mal(c)
    for w in wurzeln:
        mal(w)
    p.end()
    return img


def _organigramm(daten: dict, pts, b: int) -> QImage:
    wurzeln = _baum(pts)
    v = _ZU["hier"]
    return _haengend_baum(daten, wurzeln, b, v) if v in ("beide", "haengend_links", "haengend_rechts") else _standard_baum(daten, wurzeln, b)


def _liste(daten: dict, pts, b: int) -> QImage:
    img, p = _bild(b, 16 + len(pts) * 46)
    for i, (e, t) in enumerate(pts):
        _kasten(p, QRectF(8 + e * 36, 8 + i * 46, b - 16 - e * 36, 38), t, _farbe(daten, e), nr=i)
    p.end()
    return img


def _prozess(daten: dict, pts, b: int) -> QImage:
    je_zeile = 4
    zeilen = -(-len(pts) // je_zeile)
    bw = (b - 16 - (min(len(pts), je_zeile) - 1) * 34) / min(len(pts), je_zeile)
    img, p = _bild(b, 16 + zeilen * 96)
    for i, (e, t) in enumerate(pts):
        z, s = divmod(i, je_zeile)
        r = QRectF(8 + s * (bw + 34), 8 + z * 96, bw, 80)
        _kasten(p, r, t, _farbe(daten, 0 if daten.get("farben") != "Bunt" else i), nr=i)
        if i < len(pts) - 1 and s < je_zeile - 1:
            _pfeil(p, QPointF(r.right() + 4, r.center().y()), QPointF(r.right() + 30, r.center().y()), QColor(Farbe.GRAU))
    p.end()
    return img


def _zyklus(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    durchm = 380
    img, p = _bild(b, durchm + 16)
    mx, my, rad = b / 2, (durchm + 16) / 2, (durchm - 90) / 2
    pos = [QPointF(mx + rad * 1.35 * math.cos(-math.pi / 2 + 2 * math.pi * i / n), my + rad * math.sin(-math.pi / 2 + 2 * math.pi * i / n))
           for i in range(n)]
    for i in range(n):
        a, c = pos[i], pos[(i + 1) % n]
        if n > 1:
            w = math.atan2(c.y() - a.y(), c.x() - a.x())
            _pfeil(p, QPointF(a.x() + 62 * math.cos(w), a.y() + 30 * math.sin(w)), QPointF(c.x() - 66 * math.cos(w), c.y() - 33 * math.sin(w)),
                   QColor(Farbe.GRAU))
    for i, (e, t) in enumerate(pts):
        _kasten(p, QRectF(pos[i].x() - 56, pos[i].y() - 26, 112, 52), t, _farbe(daten, i if daten.get("farben") == "Bunt" else 0), 26, nr=i)
    p.end()
    return img


def _pyramide(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    zh = 54
    img, p = _bild(b, 16 + n * zh)
    mitte = b / 2
    for i, (e, t) in enumerate(pts):
        oben, unten = 8 + i * zh, 8 + (i + 1) * zh - 4
        bo, bu = (i / n) * (b - 16) / 2 + 0.0, ((i + 1) / n) * (b - 16) / 2
        poly = QPolygonF([QPointF(mitte - bo, oben), QPointF(mitte + bo, oben), QPointF(mitte + bu, unten), QPointF(mitte - bu, unten)])
        c = _farbe(daten, i if daten.get("farben") == "Bunt" else min(i, 2))
        _fuellen(p, c, QRectF(mitte - bu, oben, 2 * bu, unten - oben)); p.drawPolygon(poly)
        p.setPen(_text_farbe(_stilfarbe(c))); _schrift(p, t, 11)
        _text_zeichnen(p, QRectF(mitte - bu * 0.8, oben, bu * 1.6, unten - oben), Qt.AlignCenter | Qt.TextWordWrap, t)
        _merke(i, QRectF(mitte - bu, oben, 2 * bu, unten - oben))
    p.end()
    return img


# ---- Layouts des Dialogs (Foto-Katalog): Raster, Listen mit Aufzählung, Spaltenrahmen, Bildliste, Perspektive, Konvergenz, Karten, Kreise ------
def _eintraege(pts) -> list[tuple[int, str, list[str], list[int]]]:
    """Oberste Ebene als Eintrag: [(Nr., Überschrift, Textzeilen (Aufzählungspunkte und Unterpunkte), [Nr. der Unterpunkte])]."""
    out = []
    for ni, t, kinder in _gruppen(pts):
        kopf, *rest = t.split("\n")
        zeilen = [z.removeprefix(BULLET).strip() for z in rest]
        for _nj, k in kinder:
            zeilen += [z.removeprefix(BULLET).strip() for z in k.split("\n")]
        out.append((ni, kopf, zeilen, [nj for nj, _k in kinder]))
    return out


def _merke_mehrere(nummern, r: QRectF) -> None:
    for nj in nummern:
        _merke(nj, r)


def _zeilen(p: QPainter, r: QRectF, zeilen: list[str], grund: QColor, kopf: str = "") -> None:
    """Aufzählungszeilen linksbündig in ``r`` (Textfarbe nach dem Untergrund ``grund``); ``kopf`` steht vorweg, wenn gegeben."""
    p.setPen(_text_farbe(_stilfarbe(grund))); _schrift(p, "x", 10)
    t = "\n".join(([kopf] if kopf else []) + [BULLET + z for z in zeilen])
    _text_zeichnen(p, r, Qt.AlignLeft | Qt.AlignVCenter, t)


def _blockraster(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    kw, kh = (b - 16 - 10) / 2, 64
    zl = -(-n // 2)
    img, p = _bild(b, 16 + zl * kh + (zl - 1) * 10)
    for i, (_e, t) in enumerate(pts):
        z, s = divmod(i, 2)
        allein = i == n - 1 and n % 2 == 1                                  # ein einzelner letzter Block steht mittig
        x = (b - kw) / 2 if allein else 8 + s * (kw + 10)
        _kasten(p, QRectF(x, 8 + z * (kh + 10), kw, kh), t, _bunt(daten, i), 4, nr=i)
    p.end()
    return img


def _punktliste(daten: dict, pts, b: int) -> QImage:
    es = _eintraege(pts)
    hoehen = [44 + 6 + max(1, len(z)) * 17 for _ni, _k, z, _c in es]
    img, p = _bild(b, 16 + sum(hoehen) + (len(es) - 1) * 12)
    y = 8.0
    for (ni, kopf, zeilen, kinder), h in zip(es, hoehen):
        c = _bunt(daten, ni)
        _kasten(p, QRectF(8, y, b - 16, 44), kopf, c, 4, nr=ni)
        feld = QRectF(16, y + 48, b - 32, h - 48)
        _zeilen(p, feld, zeilen, QColor("white")); _merke_mehrere(kinder, feld)
        y += h + 12
    p.end()
    return img


def _balkenliste(daten: dict, pts, b: int) -> QImage:
    es = _eintraege(pts)
    zh = 60
    img, p = _bild(b, 16 + len(es) * zh)
    for i, (ni, kopf, zeilen, kinder) in enumerate(es):
        y = 8 + i * zh
        c = _bunt(daten, i)
        rahmen = QRectF(b * 0.34, y + 6, b * 0.66 - 8, zh - 14)
        _fuellen(p, c.lighter(185), rahmen); p.drawRect(rahmen)
        _kasten(p, QRectF(8, y, b * 0.5, zh - 6), kopf, c, 3, nr=ni)
        feld = QRectF(b * 0.5 + 10, y + 8, b * 0.5 - 20, zh - 18)
        _zeilen(p, feld, zeilen, c.lighter(185)); _merke_mehrere(kinder, feld)
    p.end()
    return img


def _beschreibungsliste(daten: dict, pts, b: int) -> QImage:
    es = _eintraege(pts)
    zh = 66
    img, p = _bild(b, 16 + len(es) * zh)
    for i, (ni, kopf, zeilen, kinder) in enumerate(es):
        y = 8 + i * zh
        c = _bunt(daten, i)
        rahmen = QRectF(b * 0.36, y, b * 0.64 - 8, zh - 8)
        _fuellen(p, c.lighter(185), rahmen); p.drawRect(rahmen)
        _kasten(p, QRectF(8, y, b * 0.3, zh - 8), kopf, c, 3, nr=ni)
        feld = QRectF(b * 0.36 + 10, y + 4, b * 0.64 - 28, zh - 16)
        _zeilen(p, feld, zeilen, c.lighter(185)); _merke_mehrere(kinder, feld)
    p.end()
    return img


def _spaltenrahmen(daten: dict, pts, b: int) -> QImage:
    g = _gruppen(pts)
    spalten = g[0][2] if g else []
    fuss = g[-1] if len(g) > 1 else None
    n = max(1, len(spalten))
    h = 300
    img, p = _bild(b, h)
    c = _bunt(daten, 0)
    rahmen = QRectF(8, 8, b - 16, h - 16)
    _fuellen(p, c.lighter(185), rahmen); p.drawRect(rahmen)
    kopf = QRectF(8, 8, b - 16, 52)
    _kasten(p, kopf, g[0][1] if g else "", c, 0, nr=g[0][0] if g else None)
    fu = QRectF(8, h - 8 - 44, b - 16, 44)
    _kasten(p, fu, fuss[1] if fuss else "", c, 0, nr=fuss[0] if fuss else None)
    breite = (b - 16) / n
    for i, (nj, t) in enumerate(spalten):
        r = QRectF(8 + i * breite, 60, breite, h - 16 - 52 - 44)
        p.setPen(QPen(c.darker(125), 1.5)); p.setBrush(Qt.NoBrush); p.drawRect(r)
        _text(p, r.adjusted(4, 4, -4, -4), t, c.lighter(185)); _merke(nj, r)
    p.end()
    return img


def _bildliste(daten: dict, pts, b: int) -> QImage:
    es = _eintraege(pts)
    zh = 80
    img, p = _bild(b, 16 + len(es) * zh)
    for i, (ni, kopf, zeilen, kinder) in enumerate(es):
        y = 8 + i * zh
        c = _bunt(daten, i)
        r = QRectF(8, y, b - 16, zh - 8)
        _fuellen(p, c, r); p.drawRect(r)
        bild = QRectF(16, y + 8, zh - 24, zh - 24)                           # Platzhalter für das Bild: Rahmen mit Sonne und Hügel
        p.setPen(QPen(c.darker(150), 1)); p.setBrush(QColor("white")); p.drawRect(bild)
        p.setPen(Qt.NoPen); p.setBrush(c.lighter(150))
        p.drawEllipse(QPointF(bild.left() + bild.width() * 0.7, bild.top() + bild.height() * 0.3), bild.width() * 0.1, bild.width() * 0.1)
        p.drawPolygon(QPolygonF([QPointF(bild.left() + 3, bild.bottom() - 3), QPointF(bild.left() + bild.width() * 0.4, bild.top() + bild.height() * 0.45),
                                 QPointF(bild.right() - 3, bild.bottom() - 3)]))
        feld = QRectF(bild.right() + 12, y + 4, r.right() - bild.right() - 20, zh - 16)
        _zeilen(p, feld, zeilen, c, kopf); _merke(ni, r); _merke_mehrere(kinder, r)
    p.end()
    return img


def _perspektive(daten: dict, pts, b: int) -> QImage:
    es = _eintraege(pts)
    n = len(es)
    h = 300
    img, p = _bild(b, h)
    w = (b - 16 - (n - 1) * 8) / n
    for i, (ni, kopf, zeilen, kinder) in enumerate(es):
        x = 8 + i * (w + 8)
        c = _bunt(daten, i)
        poly = QPolygonF([QPointF(x, 8 + 36), QPointF(x + w, 8), QPointF(x + w, h - 8), QPointF(x, h - 8 - 36)])      # links niedriger: perspektivisch geneigt
        _fuellen(p, c, QRectF(x, 8, w, h - 16)); p.drawPolygon(poly)
        feld = QRectF(x + 6, 52, w - 12, h - 104)
        _zeilen(p, feld, zeilen, c, kopf)
        _merke(ni, QRectF(x, 8, w, h - 16)); _merke_mehrere(kinder, QRectF(x, 8, w, h - 16))
    p.end()
    return img


def _konvergenz(daten: dict, pts, b: int) -> QImage:
    quellen, ziel = (pts[:-1], pts[-1]) if len(pts) > 1 else ([], pts[0])
    h = 320
    img, p = _bild(b, h)
    mx, my, rad = b / 2, h - 8 - 52, 52.0
    n = len(quellen)
    boxen = []
    for i in range(n):
        t = 0.0 if n == 1 else -1 + 2 * i / (n - 1)
        boxen.append(QRectF(mx + t * (b / 2 - 80) - 65, 12 + 60 * abs(t), 130, 62))
    for r in boxen:                                                           # Pfeile zuerst, die Kästen decken ihre Enden
        a = QPointF(r.center().x(), r.bottom())
        w = math.atan2(my - a.y(), mx - a.x())
        _pfeil(p, QPointF(r.center().x(), r.bottom() + 3), QPointF(mx - (rad + 4) * math.cos(w), my - (rad + 4) * math.sin(w)), QColor(Farbe.GRAU))
    for i, r in enumerate(boxen):
        _kasten(p, r, quellen[i][1], _bunt(daten, i), 4, nr=i)
    _kasten(p, QRectF(mx - rad, my - rad, 2 * rad, 2 * rad), ziel[1], _farbe(daten, 0 if daten.get("farben") != "Bunt" else n), rad, nr=len(pts) - 1)
    p.end()
    return img


def _kartenprozess(daten: dict, pts, b: int) -> QImage:
    je = 3
    zeilen = -(-len(pts) // je)
    n = min(len(pts), je)
    bw = (b - 16 - (n - 1) * 60 - 20) / n
    img, p = _bild(b, 16 + zeilen * 110 + 10)
    for i, (_e, t) in enumerate(pts):
        z, s = divmod(i, je)
        r = QRectF(8 + s * (bw + 60) + 20, 8 + z * 110 + 20, bw, 70)
        c = _bunt(daten, i)
        for d in (2, 1):                                                      # zwei Karten dahinter, leicht versetzt
            _fuellen(p, c.lighter(150 + 20 * d), QRectF(r.x() - 10 * d, r.y() - 10 * d, bw, 70)); p.drawRoundedRect(QRectF(r.x() - 10 * d, r.y() - 10 * d, bw, 70), 4, 4)
        _kasten(p, r, t, c, 4, nr=i)
        if i < len(pts) - 1 and s < je - 1:
            _pfeil(p, QPointF(r.right() + 4, r.center().y()), QPointF(r.right() + 36, r.center().y()), QColor(Farbe.GRAU))
    p.end()
    return img


def _kreisbeziehung(daten: dict, pts, b: int) -> QImage:
    h = 400
    img, p = _bild(b, h)
    mx, my, rad = b / 2, h / 2, 120.0
    rest = pts[1:]
    n = len(rest)
    c0 = _farbe(daten, 0)
    _fuellen(p, c0, QRectF(mx - rad, my - rad, 2 * rad, 2 * rad)); p.drawEllipse(QPointF(mx, my), rad, rad)
    for i in range(n):
        a = -math.pi / 2 + 2 * math.pi * i / n
        q = QPointF(mx + rad * math.cos(a), my + rad * math.sin(a))             # die kleinen Kreise sitzen auf dem Rand des großen
        c = _bunt(daten, i + 1) if daten.get("farben") == "Bunt" else _farbe(daten, 1)
        c.setAlpha(215)
        r = QRectF(q.x() - 48, q.y() - 48, 96, 96)
        _kasten(p, r, rest[i][1], c, 48, nr=i + 1)
    _text(p, QRectF(mx - 60, my - 40, 120, 80), pts[0][1], c0); _merke(0, QRectF(mx - 60, my - 40, 120, 80))
    p.end()
    return img


def _segmentzyklus(daten: dict, pts, b: int) -> QImage:
    n = len(pts)
    h = 360
    img, p = _bild(b, h)
    mx, my, rad = b / 2, h / 2, 100.0
    kreis = QRectF(mx - rad, my - rad, 2 * rad, 2 * rad)
    for i in range(n):
        c = _bunt(daten, i) if daten.get("farben") == "Bunt" else _farbe(daten, 0 if i % 2 == 0 else 1)
        _fuellen(p, c, kreis)
        p.drawPie(kreis, int((90 - 360 * i / n) * 16), int(-360 / n * 16))
    p.setPen(QPen(QColor("white"), 3)); p.setBrush(QColor("white")); p.drawEllipse(QPointF(mx, my), 30, 30)
    p.setPen(QPen(QColor(Farbe.GRAU), 3)); p.setBrush(Qt.NoBrush)
    p.drawArc(QRectF(mx - 16, my - 16, 32, 32), 30 * 16, 290 * 16)
    for i, (_e, t) in enumerate(pts):
        a = -math.pi / 2 + 2 * math.pi * (i + 0.5) / n
        c = _bunt(daten, i) if daten.get("farben") == "Bunt" else _farbe(daten, 1)
        cx = min(max(mx + (rad + 95) * math.cos(a), 8 + 75), b - 8 - 75)
        cy = min(max(my + (rad + 30) * math.sin(a), 8 + 31), h - 8 - 31)
        _kasten(p, QRectF(cx - 75, cy - 31, 150, 62), t, c.lighter(160), 3, nr=i)
    p.end()
    return img


_ZEICHNER = {"Organigramm": _organigramm, "Hierarchie": _organigramm, "Liste": _liste, "Prozess": _prozess, "Zyklus": _zyklus, "Pyramide": _pyramide,
             "Spalten": _spalten, "Gruppen": _gruppenliste, "Matrix": _matrix, "Chevron": _chevron, "Radial": _radial,
             "Zielscheibe": _zielscheibe, "Trichter": _trichter, "Zeitachse": _zeitachse, "Stufen": _stufen,
             "Blockraster": _blockraster, "Punktliste": _punktliste, "Balkenliste": _balkenliste, "Beschreibungsliste": _beschreibungsliste,
             "Spaltenrahmen": _spaltenrahmen, "Bildliste": _bildliste, "Perspektive": _perspektive, "Konvergenz": _konvergenz,
             "Kartenprozess": _kartenprozess, "Kreisbeziehung": _kreisbeziehung, "Segmentzyklus": _segmentzyklus}


def zeichnen_mit_knoten(daten: dict) -> tuple[QImage, dict[str, QRectF]]:
    """Das SmartArt als Bild und dazu die Rechtecke aller Knoten (id → QRectF in Bildpunkten dieses Bildes)."""
    kn = knoten_von(daten)
    pts = [(k["ebene"], _knotentext(k)) for k in kn] or [(0, "…")]
    _ZU.update(stil=int(daten.get("stil", 1)), rtl=bool(daten.get("rtl")), b=520, reg={}, ids=[k["id"] for k in kn], knoten=kn,
               hier=daten.get("hierarchie", "standard"), fmt=[k.get("format") for k in kn], fmt_alle=daten.get("format") or {})
    img = _ZEICHNER.get(daten.get("layout", "Liste"), _pyramide)(daten, pts, 520)
    reg, letzt = dict(_ZU["reg"]), QRectF(0, 0, img.width(), img.height())
    for ident in _ZU["ids"]:                                                 # jeder Knoten hat ein Rechteck: sonst das des Knotens davor
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
    """Fügt das SmartArt als freies Objekt ein (``editor/frei_objekt.py``): Rahmen, Griffe und Schnellleiste wie bei WordArt. ``daten`` = Daten
    (``layout``, ``text`` …), ein Eintrag aus ``LAYOUT_KATALOG`` oder dessen Schlüssel."""
    from lunivo_writer.editor import frei_objekt as FO
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
    from lunivo_writer.editor import frei_objekt as FO
    d = FO.daten_lesen(ed, "smartart")
    return d if d is not None else _inline_daten(ed)


def aendern(ed, **felder) -> bool:
    """Daten des gewählten SmartArt ändern und neu zeichnen (Breite bleibt, Seitenverhältnis folgt). Ein neuer ``text`` (anders als der zu den
    Knoten gehörende) ersetzt die Knoten; ``knoten=None``, ``auswahl=None``, ``hierarchie=None`` und ``rtl=None`` entfernen die Angabe."""
    from lunivo_writer.editor import frei_objekt as FO
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
    from lunivo_writer.editor import frei_objekt as FO
    d = FO.daten_lesen(ed, "smartart")
    a = d.get("auswahl") if d else None
    return a if a and _index(knoten_von(d), a) is not None else None


def knoten_waehlen(ed, ident) -> bool:
    """Knoten wählen (None: Auswahl aufheben). Das Bild wird nicht neu gezeichnet."""
    from lunivo_writer.editor import frei_objekt as FO
    d = FO.daten_lesen(ed, "smartart")
    if d is None or (ident and _index(knoten_von(d), ident) is None):
        return False
    return FO.daten_still(ed, "smartart", auswahl=ident or None)


def knoten_bei(ed, pos) -> str | None:
    """Die Id des Knotens unter ``pos`` (QPointF im Editor, dieselben Koordinaten wie die Rechtecke von ``ed._frei_liste()``) im gewählten SmartArt;
    Drehung und Zoom sind berücksichtigt. Kein Treffer: None."""
    from lunivo_writer.editor import frei_objekt as FO
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
