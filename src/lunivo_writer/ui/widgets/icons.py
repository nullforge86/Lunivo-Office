"""Einheitliche Office-Symbole: 24×24-Strichzeichnungen aus Lucide, mit Qt gerendert."""
from __future__ import annotations

import json
import os
import re
import tempfile
from lunivo_writer.core import paths

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPalette, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

_PFADE: dict | None = None
_CACHE: dict = {}
STRICH = 1.05         # schlanke Office-Kontur bei typischen Symbolgrößen von 16–20 px
FAKTOR = 1.0          # Größe der Symbole (Optionen ▸ Darstellung)


_ORIGINAL: dict | None = None


def pfade_original() -> dict:
    """Die mitgelieferten Symbole, ohne Austausch."""
    global _ORIGINAL
    if _ORIGINAL is None:
        with open(os.path.join(paths.SYMBOLE, "symbole.json"), encoding="utf-8") as fh:
            _ORIGINAL = json.load(fh)
    return _ORIGINAL


def pfade() -> dict:
    global _PFADE
    if _PFADE is None:
        _PFADE = dict(pfade_original())
    return _PFADE


def uebersteuern(tausch: dict) -> None:
    """Austausch {Symbolname: Katalogname} anwenden (Ansicht ▸ Symbol austauschen); leere Zuordnung stellt alles zurück."""
    global _PFADE
    _PFADE = dict(pfade_original())
    kat = katalog()
    for alt, neu in (tausch or {}).items():
        if alt not in _PFADE:
            continue
        if neu in kat:
            _PFADE[alt] = kat[neu]
        elif str(neu).startswith(EIGEN):                         # eigene Zeichnung (siehe eigene_zeichnung)
            _PFADE[alt] = neu
    leeren()


_KATALOG: dict | None = None


def katalog() -> dict:
    """Alle 1800 Lucide-Symbole (Name → 24×24-Pfad) — für Piktogramm einfügen und Symbol austauschen."""
    global _KATALOG
    if _KATALOG is None:
        with open(os.path.join(paths.SYMBOLE, "symbolkatalog.json"), encoding="utf-8") as fh:
            _KATALOG = json.load(fh)
    return _KATALOG


def katalog_bild(name: str, px: int = 96, farbe: str = "#1f2328", strich: float = STRICH) -> QImage:
    img = QImage(px, px, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    d = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{farbe}" stroke-width="{strich}" '
         f'stroke-linecap="round" stroke-linejoin="round"><path d="{katalog()[name]}"/></svg>').encode()
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    QSvgRenderer(QByteArray(d)).render(p, QRectF(0, 0, px, px))
    p.end()
    return img


def pfad_bild(pfad: str, px: int = 48, farbe: str = "#1f2328") -> QImage:
    """Eine Zeichnung (Katalogpfad oder eigene) als Bild — für Vorschau und Auswahlfenster."""
    img = QImage(px, px, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    QSvgRenderer(QByteArray(_svg(pfad, farbe))).render(p, QRectF(0, 0, px, px))
    p.end()
    return img


# Farbstriche unter Symbolen wie in Word: Name → Farbe (Schriftfarbe rot, Hervorheben gelb, Tönung blau, Rahmen/Schatten bleiben neutral)
AKZENT = {"schriftfarbe": "#e03131", "marker": "#fcc419", "absatztoenung": "#74c0fc", "toenung": "#74c0fc"}

def hat(name: str) -> bool:
    return name in pfade() or name in katalog()


def _symbolpfad(name: str) -> str | None:
    """Gibt zuerst das semantische Standardsymbol, sonst das Lucide-Katalogsymbol zurück."""
    return pfade().get(name) or katalog().get(name)


EIGEN = "#e#"          # Vorsatz einer eigenen Zeichnung im Austausch: #e# + JSON {d, s, x, y, f}


def eigene_zeichnung(text: str, gefuellt: bool = False) -> str | None:
    """SVG oder Pfaddaten → Zeichnung, auf 24 × 24 gebracht und mittig eingepasst (Zeichenkette für den Austausch).
    ``None``, wenn daraus nichts Zeichenbares wird. Eine Zeichnung, die schon in 0–24 liegt, bleibt unverändert."""
    text = (text or "").strip()
    pfade_ = re.findall(r'\bd\s*=\s*"([^"]+)"', text)
    d = " ".join(" ".join(pfade_).split()) if pfade_ else (" ".join(text.split()) if "<" not in text else "")
    if not d or not re.fullmatch(r"[MmLlHhVvCcSsQqTtAaZz0-9eE\s,.+\-]+", d):
        return None
    probe = QSvgRenderer(QByteArray(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2000 -2000 6000 6000"><path id="p" d="{d}"/></svg>'.encode()))
    if not probe.isValid():
        return None
    b = probe.boundsOnElement("p")
    if b.width() <= 0 and b.height() <= 0:
        return None
    schon_24 = bool(re.search(r'viewBox\s*=\s*"\s*0[ ,]+0[ ,]+24[ ,]+24\s*"', text)) and b.left() >= -0.5 and b.top() >= -0.5 \
        and b.right() <= 24.5 and b.bottom() <= 24.5
    if schon_24:
        s, x, y = 1.0, 0.0, 0.0
    else:
        s = 20.0 / max(b.width(), b.height(), 0.0001)
        x, y = 12 - s * (b.left() + b.width() / 2), 12 - s * (b.top() + b.height() / 2)
    return EIGEN + json.dumps({"d": d, "s": round(s, 5), "x": round(x, 4), "y": round(y, 4), "f": bool(gefuellt)})


def _svg(pfad: str, farbe: str) -> bytes:
    if pfad.startswith(EIGEN):
        e = json.loads(pfad[len(EIGEN):])
        s = e["s"]
        zug = f'transform="translate({e["x"]} {e["y"]}) scale({s})"'
        if e.get("f"):
            return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path {zug} fill="{farbe}" d="{e["d"]}"/></svg>').encode()
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{farbe}" stroke-width="{STRICH / s:.4f}" '
                f'stroke-linecap="round" stroke-linejoin="round"><path {zug} d="{e["d"]}"/></svg>').encode()
    strich = STRICH + (0.05 if QColor(farbe).lightness() > 220 else 0)      # minimaler Ausgleich für helle Symbole auf dunklem Grund
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{farbe}" '
            f'stroke-width="{strich}" stroke-linecap="round" stroke-linejoin="round"><path d="{pfad}"/></svg>').encode()


def svg_datei(name: str, farbe: str) -> str:
    """Lucide-SVG als Datei für Qt-Stylesheets, die SVG-Daten nicht direkt annehmen."""
    pfad = _symbolpfad(name)
    if pfad is None:
        return ""
    ordner = os.path.join(tempfile.gettempdir(), "lunivo-writer-icons")
    os.makedirs(ordner, exist_ok=True)
    # Strichstärke im Cache-Schlüssel halten: alte SVGs aus früheren Starts
    # dürfen nach einer Stiländerung nicht weiter in Qt-Stylesheets auftauchen.
    datei = os.path.join(ordner, f"{name}_{farbe.lstrip('#')}_{STRICH:g}.svg")
    if not os.path.exists(datei):
        with open(datei, "wb") as fh:
            fh.write(_svg(pfad, farbe))
    return datei.replace("\\", "/")


def _pixmap(name: str, farbe: str, px: int) -> QPixmap:
    key = (name, farbe, px)
    if key in _CACHE:
        return _CACHE[key]
    ratio = 2
    img = QImage(px * ratio, px * ratio, QImage.Format_ARGB32_Premultiplied)
    img.fill(Qt.transparent)
    # Auch Katalognamen und semantische Namen werden durch denselben Renderer gezeichnet.
    pfad = _symbolpfad(name)
    if pfad is None:
        return QPixmap()
    r = QSvgRenderer(QByteArray(_svg(pfad, farbe)))
    p = QPainter(img)
    r.render(p, QRectF(0, 0, px * ratio, px * ratio))
    p.end()
    pm = QPixmap.fromImage(img)
    pm.setDevicePixelRatio(ratio)
    _CACHE[key] = pm
    return pm


def icon(name: str, px: int = 20) -> QIcon:
    px = max(10, int(round(px * FAKTOR)))
    """Symbol in den Farben der aktuellen Palette (hell/dunkel), ausgegraut wenn deaktiviert."""
    pfad = _symbolpfad(name)
    if pfad is None:
        return QIcon()
    pal = QApplication.palette()
    normal = pal.color(QPalette.ButtonText).name()
    if QColor(normal).lightness() > 128:                 # dunkler Hintergrund: Symbole fast weiß, damit man sie gut erkennt
        normal = "#f4f6f8"
    off = pal.color(QPalette.Disabled, QPalette.ButtonText).name()
    ic = QIcon()
    ic.addPixmap(_pixmap(name, normal, px), QIcon.Normal)
    ic.addPixmap(_pixmap(name, off, px), QIcon.Disabled)
    return ic


def icon_aus_pfad(pfad: str, px: int = 20) -> QIcon:
    """Ein Liniensymbol aus einem Pfad (24er-Raster, Strichstil wie die übrigen Symbole) in den Farben der Palette."""
    px = max(10, int(round(px * FAKTOR)))
    pal = QApplication.palette()
    normal = pal.color(QPalette.ButtonText).name()
    if QColor(normal).lightness() > 128:
        normal = "#f4f6f8"
    off = pal.color(QPalette.Disabled, QPalette.ButtonText).name()
    ic = QIcon()
    for farbe, modus in ((normal, QIcon.Normal), (off, QIcon.Disabled)):
        img = QImage(px * 2, px * 2, QImage.Format_ARGB32_Premultiplied)
        img.fill(Qt.transparent)
        p = QPainter(img)
        QSvgRenderer(QByteArray(_svg(pfad, farbe))).render(p, QRectF(0, 0, px * 2, px * 2))
        p.end()
        pm = QPixmap.fromImage(img)
        pm.setDevicePixelRatio(2)
        ic.addPixmap(pm, modus)
    return ic


def leeren() -> None:
    _CACHE.clear()


def setze(knopf, name: str, px: int = 20) -> None:
    """Symbol auf einen Knopf setzen und den Namen merken: beim Wechsel zwischen hell und dunkel bekommt er sein Symbol in der neuen Farbe zurück."""
    knopf.setProperty("symbolName", name)
    knopf.setProperty("symbolPx", px)
    knopf.setIcon(icon(name, px))


def alle_neu() -> None:
    """Nach einem Farbwechsel: alle Knöpfe mit gemerktem Symbol neu beziehen (der Zwischenspeicher ist dann schon geleert)."""
    for w in QApplication.allWidgets():
        name = w.property("symbolName")
        if not name:
            continue
        px = int(w.property("symbolPx") or 20)
        if hasattr(w, "setIcon"):
            w.setIcon(icon(str(name), px))
        elif hasattr(w, "setPixmap"):
            w.setPixmap(icon(str(name), px).pixmap(px, px))
