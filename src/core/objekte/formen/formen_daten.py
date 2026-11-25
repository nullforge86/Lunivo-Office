"""Formen daten: aus ``vcl.qt.rendering.formen.formen`` herausgelöst."""
from __future__ import annotations
from core.formatierung.farben.farben import Farbe


STANDARD = {"fuell": Farbe.AKZENT_DUNKEL, "linie": "#1f3864", "strich": 2.0, "text": ""}


VORLAGEN = [("Blau", Farbe.AKZENT_DUNKEL, "#1f3864", 2.0), ("Grün", "#6bbf59", "#2d6a1f", 2.0), ("Orange", "#f4a259", "#9c4f0a", 2.0),
            ("Rot", "#e5645f", "#8c1d18", 2.0), ("Grau", "#ced4da", "#495057", 2.0), ("Nur Kontur", "", "#1f3864", 2.5),
            ("Dunkel", "#2b2d42", Farbe.SCHWARZ, 1.5), ("Hell mit dicker Kontur", "#fff3bf", "#e67700", 5.0)]


GRUPPEN_ABSTAND = 8


def form_daten(o: dict, breite: float, hoehe: float) -> dict:
    d = dict(STANDARD); d.update(o.get("daten", {}))
    d["breite"], d["hoehe"] = int(round(breite)), int(round(hoehe))
    return d


_FO_SCHLUESSEL = {"fuell": "form_fuell", "linie": "form_linie", "strich": "form_strich", "text": "text", "form": "form",
                  "breite": "breite", "hoehe": "hoehe"}


def frei_daten(ed) -> dict | None:
    """Die Parameter der gewählten Form als freies Objekt (Kopie) oder None."""
    from vcl.qt.rendering.formen import frei_objekt as FO
    return FO.daten_lesen(ed, "form")


# ---- Zeichenbereich (Einfügen ▸ Formen ▸ Neuer Zeichenbereich) -------------------------------------------------------------------
# Ein freies Objekt der Art „zeichenbereich“, das Formen aufnimmt: ist es gewählt, kommt eine Form aus der Formen-Klappe hinein statt als eigenes
# Objekt aufs Blatt. Die Formen stehen als ``kinder`` (Form, Lage x/y, Größe in Bildpunkten) in den Daten des Bereichs und werden bei jeder
# Änderung neu gezeichnet (``frei_objekt._zeichenbereich_zeichnen``); der gestrichelte Rand zeigt den Bereich.
ZB_VERSATZ = 24                                                   # jede neue Form etwas rechts unterhalb der vorigen


ZB_RAND = 8                                                       # Abstand der ersten Form zum Rand des Bereichs


def zeichenbereich_einfuegen(ed):
    """Einen leeren Zeichenbereich als freies Objekt einfügen (Größe: ``STANDARD_MASS["zeichenbereich"]``, höchstens die Inhaltsbreite). → Id."""
    from vcl.qt.rendering.formen import frei_objekt as FO
    return FO.einfuegen(ed, "zeichenbereich", {"kinder": []})


def in_zeichenbereich(ed, form: str) -> bool:
    """Form in den gewählten Zeichenbereich setzen; False, wenn keiner gewählt ist (dann kommt die Form als eigenes Objekt aufs Blatt)."""
    from vcl.qt.rendering.formen import formen_katalog as K
    from vcl.qt.rendering.formen import frei_objekt as FO
    z = FO.ziel(ed)
    if z is None or z[0] != "zeichenbereich":
        return False
    d, a = z[1], z[3]
    b, h = int(a["b"]), int(a["h"])
    kinder = list(d.get("kinder", []))
    kb, kh = (min(240, b - 2 * ZB_RAND), 60) if K.ist_linie(form) else (min(160, b - 2 * ZB_RAND), min(120, h - 2 * ZB_RAND))
    n = len(kinder)
    x = ZB_RAND + (n * ZB_VERSATZ) % max(1, b - kb - 2 * ZB_RAND)
    y = ZB_RAND + (n * ZB_VERSATZ) % max(1, h - kh - 2 * ZB_RAND)
    kinder.append({"form": form, "x": x, "y": y, "breite": kb, "hoehe": kh})
    return FO.aendern(ed, "zeichenbereich", kinder=kinder)
