"""Sprechblasen: Kommentare und verfolgte Änderungen als Blasen im Seitenrand, mit Verbindungslinien zum Text.

Einstellungen (Optionen ▸ Änderungen verfolgen ▸ Sprechblasen), gelesen mit `konfig_lesen`:
  verwenden   „Nur für Kommentare“ | „Immer“ (auch Einfügungen/Löschungen) | „Nie“
  breite_mm   bevorzugte Breite;  empfohlen: die empfohlene Breite (60 mm) statt des eigenen Wertes
  rand        „Rechts“ | „Links“;  linien: Verbindungslinien zum Text
  ausrichtung Papierausrichtung beim Drucken mit Sprechblasen: „Automatisch“ | „Beibehalten“ | „Querformat“
Anzeige und Druck benutzen dieselben Zeichenfunktionen.
"""
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter

from lunivo_writer.editor.dokument.zusatz import AUTOR_FARBEN

EMPFOHLENE_BREITE_MM = 60.0
STANDARD = {"verwenden": "Nur für Kommentare", "breite_mm": 60.0, "empfohlen": True, "rand": "Rechts", "linien": True,
            "ausrichtung": "Automatisch"}
VERWENDEN = ["Nur für Kommentare", "Immer", "Nie"]
RAND = ["Rechts", "Links"]
AUSRICHTUNG = ["Automatisch", "Beibehalten", "Querformat"]
LUECKE_MM = 10.0                      # Abstand zwischen Seite und Blasenfläche: die Blasen stehen deutlich neben dem Blatt, nicht fast im Dokument
BLASE_UEBERABTASTUNG = 2.0            # die Blase wird doppelt so fein gerechnet und glatt verkleinert: scharfe Kreise, Ränder und Schrift
BLASE_RAND = 6.0                      # Platz um die Blase für den weichen Schatten


def konfig_lesen(settings) -> dict:
    k = dict(STANDARD)
    g = lambda n: "sprechblasen/" + n                                      # noqa: E731
    v = settings.get(g("verwenden"), k["verwenden"])
    k["verwenden"] = v if v in VERWENDEN else k["verwenden"]
    try:
        k["breite_mm"] = min(120.0, max(30.0, float(settings.get(g("breite_mm"), k["breite_mm"]))))
    except (TypeError, ValueError):
        pass
    k["empfohlen"] = settings.get_bool(g("empfohlen"), k["empfohlen"])
    r = settings.get(g("rand"), k["rand"])
    k["rand"] = r if r in RAND else k["rand"]
    k["linien"] = settings.get_bool(g("linien"), k["linien"])
    a = settings.get(g("ausrichtung"), k["ausrichtung"])
    k["ausrichtung"] = a if a in AUSRICHTUNG else k["ausrichtung"]
    return k


def breite_mm(k: dict) -> float:
    return EMPFOHLENE_BREITE_MM if k["empfohlen"] else k["breite_mm"]


def aktiv(k: dict) -> bool:
    return k["verwenden"] != "Nie"


@dataclass
class Blase:
    von: int
    bis: int
    autor: str
    datum: str
    art: str                          # „kommentar“ | „ins“ | „del“
    text: str
    farbe: str
    kid: int | None = None


def autor_farbe(autor: str) -> str:
    import hashlib
    return AUTOR_FARBEN[int(hashlib.md5((autor or "?").encode()).hexdigest(), 16) % len(AUTOR_FARBEN)]


def _kuerzen(t: str, n: int = 90) -> str:
    t = " ".join(t.split())
    return t if len(t) <= n else t[: n - 1] + "…"


def sammeln_modell(sitzung, verwenden: str = "Nur für Kommentare") -> list[Blase]:
    """Alle Blasen des Dokuments in Textreihenfolge (Stellen im Rohtext) aus dem Dokumentmodell."""
    from lunivo_writer.core.editing.suche import position_zu_offset, roh_text
    if verwenden == "Nie":
        return []
    d = sitzung.dokument
    out: list[Blase] = []
    kom: dict[int, list[int]] = {}
    for fund in sitzung.bereiche(lambda f: "kommentar" in f, lambda f: f["kommentar"]):
        a = sitzung._absatz(fund.anker.absatz_id)
        versatz, kid = 0, None
        for x in a.inhalte:
            if versatz == fund.anker.versatz:
                kid = int(x.format["kommentar"])
            versatz += len(x.text) if hasattr(x, "text") else 1
        if kid is not None:
            r = kom.setdefault(kid, [position_zu_offset(d, fund.anker), position_zu_offset(d, fund.kopf)])
            r[0], r[1] = min(r[0], position_zu_offset(d, fund.anker)), max(r[1], position_zu_offset(d, fund.kopf))
    for kid, (v, e) in kom.items():
        k = d.kommentare.get(kid)
        out.append(Blase(v, e, k.autor if k else "", k.datum if k else "", "kommentar", k.text if k else "",
                         "#f5a623" if (k and not k.geloest) else "#9aa5b1", kid))
    if verwenden == "Immer":
        text = roh_text(d)
        for fund, art, autor, datum in sitzung.aenderungen():
            v, e = position_zu_offset(d, fund.anker), position_zu_offset(d, fund.kopf)
            out.append(Blase(v, e, autor, datum, art, ("Eingefügt: " if art == "ins" else "Gelöscht: ") + _kuerzen(text[v:e]), autor_farbe(autor)))
    return sorted(out, key=lambda x: (x.von, x.bis))


def _kopf(bl: Blase) -> str:
    d = (bl.datum or "")[:10]
    return (bl.autor or "Unbekannt") + ((" · " + d) if d else "")


# Schriftgröße der Kommentare: Bildpunkte der Blase im Editor bei 100 % Zoom, und Punkt in den Karten links (Menü Kommentare ▸ Schriftgröße)
SCHRIFTEN = {"klein": (12, 10.0), "mittel": (14, 11.5), "gross": (17, 14.0)}


def blasen_px(key: str) -> int:
    return SCHRIFTEN.get(key, SCHRIFTEN["mittel"])[0]


def karten_pt(key: str) -> float:
    return SCHRIFTEN.get(key, SCHRIFTEN["mittel"])[1]


KOPF_HOEHE = 24.0                                  # die Kopfzeile: Kreis mit Initial, Name, Datum, Menüzeichen


def blasen_schrift(px: float):
    """Die Schrift der Blasen als Beschreibung des Kerns: Grundschrift des Dokuments, Größe aus Bildpunkten (96 dpi) in Punkt. Keine Qt-Schrift."""
    from lunivo_writer.core.layout.formatwerte import STANDARD_FAMILIE
    from lunivo_writer.core.textlayout import FontSpec
    return FontSpec(STANDARD_FAMILIE, max(1.0, px) * 72.0 / 96.0, 400, False)


def messen(bl: Blase, breite: float, font) -> float:
    """Höhe der Blase bei gegebener Breite (alles in Bildpunkten des Zeichengeräts); gemessen vom Kern."""
    from lunivo_writer.core.rendering import blasen
    from lunivo_writer.dienste.textsatz import standard_engine
    return blasen.messen(standard_engine(), bl.text or " ", breite, font)


def stapeln(anker_y: list[float], hoehen: list[float], unten: float, abstand: float = 6.0) -> list[float]:
    """Obere Kanten der Blasen: so nah wie möglich an ihrem Anker, ohne sich zu überlappen (und nicht unter `unten`)."""
    ys: list[float] = []
    cur = -1e9
    for a, h in zip(anker_y, hoehen):
        y = max(a, cur)
        ys.append(y)
        cur = y + h + abstand
    # von unten nach oben zurückschieben, wenn die Spalte über das Seitenende hinausläuft
    ende = unten
    for i in range(len(ys) - 1, -1, -1):
        if ys[i] + hoehen[i] > ende:
            ys[i] = max(0.0, ende - hoehen[i])
        ende = ys[i] - abstand
    return ys


def _ortszeit(iso: str) -> str:
    """„2026-10-22 12:11“ in der Ortszeit (die Datei speichert UTC; die Karte links zeigt auch Ortszeit)."""
    import datetime
    try:
        return datetime.datetime.fromisoformat(iso).astimezone().strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return (iso or "")[:16].replace("T", " ")


def menue_rect(r: QRectF) -> QRectF:
    """Die Fläche des Menüzeichens „☰“ oben rechts in der Blase (für den Klick)."""
    return QRectF(r.right() - 28, r.y() + 6, 24, KOPF_HOEHE + 4)


def zeichnen(p: QPainter, bl: Blase, r: QRectF, font, druck: bool = False) -> None:
    """Eine Blase zeichnen wie eine Karte: Kreis mit Initial, Name fett, Datum, Menüzeichen, darunter der Text — Farben des Designs, Kreis in der Farbe des Kommentars. Gezeichnet vom Kern."""
    from PySide6.QtGui import QGuiApplication, QPalette
    from lunivo_writer.oberflaeche.zeichnen.anzeige import kern_malen
    from lunivo_writer.core.geometry import Rect
    from lunivo_writer.core.rendering import blasen
    from lunivo_writer.dienste.textsatz import standard_engine
    pal = QPalette() if druck else QGuiApplication.palette()                # im Druck immer helle Farben, nie die des dunklen Designs

    def farbe(c: QColor) -> tuple:
        return c.red(), c.green(), c.blue(), c.alpha()
    farben = (farbe(pal.color(QPalette.Button)), farbe(pal.color(QPalette.Mid)), farbe(pal.color(QPalette.ButtonText)))
    fb = QColor(bl.farbe)
    engine = standard_engine()
    kern_malen(p, r, lambda z: blasen.zeichne_blase(z, engine, bl.autor, _ortszeit(bl.datum), farbe(fb), bl.text or "", Rect(r.x(), r.y(), r.width(), r.height()), font, farben), rand=BLASE_RAND, ueber=BLASE_UEBERABTASTUNG)


def verbindung(p: QPainter, bl: Blase, x_text: float, y_text: float, r: QRectF, rechts: bool) -> None:
    """Linie vom Text zur Blase: waagerecht aus dem Seitenrand, dann zur Mitte der Kopfzeile."""
    from lunivo_writer.oberflaeche.zeichnen.anzeige import kern_malen
    from lunivo_writer.core.geometry import Rect
    from lunivo_writer.core.rendering import blasen
    c = QColor(bl.farbe)
    flaeche = QRectF(min(x_text, r.left()) - 12, min(y_text, r.top()) - 2, abs(r.left() - x_text) + r.width() + 24, abs(y_text - r.top()) + r.height() + 4)
    kern_malen(p, flaeche, lambda z: blasen.verbindung(z, (c.red(), c.green(), c.blue(), c.alpha()), x_text, y_text, Rect(r.x(), r.y(), r.width(), r.height()), rechts), rand=BLASE_RAND, ueber=BLASE_UEBERABTASTUNG)
