"""Smartart daten: aus ``vcl.qt.rendering.smartart.smartart`` herausgelöst."""
from __future__ import annotations
import copy
import re
from core.formatierung.farben.farben import Farbe


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


# ---- Katalog und Einfügen ----------------------------------------------------------------------------------------------------------------
def katalogeintrag(schluessel: str) -> dict:
    return next((e for e in LAYOUT_KATALOG if e["schluessel"] == schluessel), LAYOUT_KATALOG[0])


def neue_daten(eintrag=None, farben: str = "Blau") -> dict:
    """Daten eines neuen SmartArt aus einem Katalogeintrag (oder dessen Schlüssel); ohne Angabe das Standard-Layout (Organigramm) mit Mustertext."""
    e = eintrag if isinstance(eintrag, dict) else katalogeintrag(eintrag or STANDARD_LAYOUT)
    return {"layout": e["schluessel"], "farben": farben, "text": e["muster"]}


def einfuegen_daten(daten) -> dict:
    """Die Daten, mit denen ein SmartArt als freies Objekt eingefügt wird. ``daten`` = Daten (``layout``, ``text`` …), ein Eintrag aus
    ``LAYOUT_KATALOG`` oder dessen Schlüssel."""
    if not isinstance(daten, dict) or ("muster" in daten and "schluessel" in daten):
        daten = neue_daten(daten)
    return dict(daten)


def text_gegen_knoten(d0: dict | None, neu: dict) -> None:
    """Ein neuer ``text`` ohne neue Knoten: weicht er vom Text der vorhandenen Knoten (``d0`` = Daten des gewählten SmartArt) ab, ersetzt er sie;
    sonst bleibt alles, wie es ist."""
    if "text" not in neu or "knoten" in neu:
        return
    d0 = d0 or {}
    if not d0.get("knoten"):
        return
    if neu["text"] != text_aus_knoten(knoten_von(d0)):
        neu["knoten"] = None; neu["auswahl"] = None
    else:
        neu.pop("text")                                                  # unverändert: Knoten (mit Ids und Assistenten) bleiben


# ---- Knoten im gewählten SmartArt (Auswahl, Treffer, Text, Befehle) --------------------------------------------------------------------
def knoten_gewaehlt(d: dict | None) -> str | None:
    """Id des gewählten Knotens im SmartArt mit den Daten ``d`` oder None."""
    a = d.get("auswahl") if d else None
    return a if a and _index(knoten_von(d), a) is not None else None


def knoten_waehlbar(d: dict | None, ident) -> bool:
    """Ob der Knoten gewählt werden kann (``ident`` leer: die Auswahl aufheben geht immer, sofern es ein SmartArt gibt)."""
    return d is not None and not (ident and _index(knoten_von(d), ident) is None)


def knoten_text(d: dict | None, ident) -> str | None:
    """Der Text des Knotens (ohne Aufzählungspunkte) oder None."""
    kn = knoten_von(d) if d else []
    i = _index(kn, ident)
    return kn[i]["text"] if i is not None else None


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


def format_lesen(d: dict | None) -> dict | None:
    """Werte für die Seitenleiste: ``{"format": …, "gewaehlt": Id | None}`` — das Format des gewählten Knotens, ohne Auswahl das von allen Knoten."""
    if d is None:
        return None
    ident = knoten_gewaehlt(d)
    if ident:
        kn = knoten_von(d)
        return {"teil": "diagrammbereich", "format": kn[_index(kn, ident)].get("format") or {}, "gewaehlt": ident}
    return {"teil": "diagrammbereich", "format": d.get("format") or {}, "gewaehlt": None}


def kann(d: dict | None, was: str, richtung: str = "") -> bool:
    """Ob ein Knotenbefehl gerade geht (zum Ausgrauen): ``level`` (erhoehen/reduzieren), ``verschieben`` (vor/zurueck), ``knoten`` (ein Knoten ist
    gewählt), ``hierarchie`` (das Layout kennt Hierarchie-Varianten und Assistenten)."""
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
