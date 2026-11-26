"""Freie bilder daten: aus ``vcl.qt.rendering.formen.freie_bilder`` herausgelöst."""
from __future__ import annotations
from core.formatierung.farben.farben import Farbe


EMU_PX = 9525.0                                              # 1 px bei 96 dpi


def emu_zu_px(emu) -> float:
    try:
        return float(emu) / EMU_PX
    except (TypeError, ValueError):
        return 0.0


# ---- Bilddaten lesen (auch EMF mit eingebettetem Bild) ----------------------------------------------------------------------
MAX_BILDPUNKTE = 100_000_000          # größere Bilder aus fremden Dokumenten werden nicht dekodiert (Speicher: 4 Byte je Bildpunkt)


# ---- Zweifarbig („Duoton“) ------------------------------------------------------------------------------------------------
SCHEMA = {"tx1": Farbe.SCHWARZ, "dk1": Farbe.SCHWARZ, "bg1": Farbe.WEISS, "lt1": Farbe.WEISS, "tx2": "#1f497d", "dk2": "#1f497d", "bg2": "#eeece1",
          "lt2": "#eeece1", "accent1": "#4f81bd", "accent2": "#c0504d", "accent3": "#9bbb59", "accent4": "#8064a2", "accent5": "#4bacc6",
          "accent6": "#f79646"}


def text_gerade(dreh: float, fx: dict | None) -> bool:
    """„Text nicht drehen“: Form und Füllung gedreht, der Text bleibt aufrecht."""
    return bool(dreh and ((fx or {}).get("drehung") or {}).get("text_gerade"))


def ohne_hilfsangaben(a: dict) -> dict:
    return {k: v for k, v in a.items() if not k.startswith("_")}


def vorne_hinten(objekte, hinter: bool):
    return [o for o in objekte if bool(o[0].get("hinter")) == hinter]
