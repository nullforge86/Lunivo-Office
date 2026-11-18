"""Bildvergleich zweier Seitenbilder ohne Zusatzbibliotheken (nur Qt).

Ein einfacher Pixelvergleich entscheidet nie allein: Kantenglättung und Schrift-Rendering verschieben einzelne Bildpunkte. Deshalb werden beide Bilder auf ein grobes Raster (Zellen von
``ZELLE`` Bildpunkten) verkleinert; verglichen wird die **Tintenmenge je Zelle** (mittlere Dunkelheit). Eine Zelle gilt erst als abweichend, wenn ihre Tintenmenge um mehr als
``zellanteil`` des Wertebereichs abweicht. Zusätzlich werden gemessen:

* Inhaltsrahmen (Bereich mit Tinte) → Randabweichungen in mm,
* Zeilenprofil (Tinte je Rasterzeile) → vertikaler Versatz des Inhalts in mm (verschobene Textbereiche, andere Zeilenumbrüche),
* Tintenverhältnis (Lunivo : Referenz) → Hinweis auf fehlende oder zusätzliche Inhalte,
* zusammenhängende abweichende Bereiche mit Richtung (fehlt in Lunivo / zusätzlich in Lunivo / anders gesetzt).

Die Messwerte sind Messwerte. Die Zuordnung einer Ursache (z. B. „anderer Zeilenumbruch“) geschieht in ``pruefarten`` nur dort, wo ein Messwert sie belegt.
"""
from __future__ import annotations

from collections import deque

ZELLE = 8                                    # Bildpunkte je Rasterzelle (bei 96 dpi etwa 2 mm)
MIN_TINTE = 3.0                              # mittlere Dunkelheit (0–255), ab der eine Zelle als „mit Inhalt“ gilt
MAX_SHIFT = 12                               # größter geprüfter vertikaler Versatz in Rasterzeilen


def _raster(bild, gw: int, gh: int) -> list[bytes]:
    """Dunkelheit (255 - Grau) je Rasterzelle, zeilenweise."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QImage
    klein = bild.scaled(gw, gh, Qt.IgnoreAspectRatio, Qt.SmoothTransformation).convertToFormat(QImage.Format_Grayscale8)
    bpl = klein.bytesPerLine()
    daten = bytes(klein.constBits())
    zeilen = []
    for y in range(gh):
        zeilen.append(bytes(255 - b for b in daten[y * bpl:y * bpl + gw]))
    return zeilen


def vergleiche(ref, lun, zellanteil: float, mm_pro_px: float) -> dict:
    """``ref``/``lun``: QImage. ``mm_pro_px``: Millimeter je Bildpunkt des Lunivo-Bilds (25,4/96 bei 96 dpi)."""
    from PySide6.QtCore import Qt
    breite, hoehe = lun.width(), lun.height()
    gw, gh = max(4, -(-breite // ZELLE)), max(4, -(-hoehe // ZELLE))
    gw += (-gw) % 4
    if (ref.width(), ref.height()) != (breite, hoehe):
        ref = ref.scaled(breite, hoehe, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    r, l = _raster(ref, gw, gh), _raster(lun, gw, gh)
    schwelle = max(1.0, zellanteil * 255.0)
    abweichend = []
    tinte_r = tinte_l = 0
    zellen_mit_inhalt = 0
    zeile_r = [0] * gh
    zeile_l = [0] * gh
    rahmen_r = [gw, gh, -1, -1]
    rahmen_l = [gw, gh, -1, -1]
    for y in range(gh):
        zr, zl = r[y], l[y]
        sr, sl = sum(zr), sum(zl)
        zeile_r[y], zeile_l[y] = sr, sl
        tinte_r += sr
        tinte_l += sl
        if sr == 0 and sl == 0:
            continue
        for x in range(gw):
            a, b = zr[x], zl[x]
            if a > MIN_TINTE:
                rahmen_r[0], rahmen_r[1], rahmen_r[2], rahmen_r[3] = min(rahmen_r[0], x), min(rahmen_r[1], y), max(rahmen_r[2], x), max(rahmen_r[3], y)
            if b > MIN_TINTE:
                rahmen_l[0], rahmen_l[1], rahmen_l[2], rahmen_l[3] = min(rahmen_l[0], x), min(rahmen_l[1], y), max(rahmen_l[2], x), max(rahmen_l[3], y)
            if a > MIN_TINTE or b > MIN_TINTE:
                zellen_mit_inhalt += 1
                if abs(a - b) > schwelle:
                    abweichend.append((x, y, b - a))
    zell_mm = ZELLE * mm_pro_px

    def _rahmen_mm(rh):
        if rh[2] < 0:
            return None
        return [round(rh[0] * zell_mm, 1), round(rh[1] * zell_mm, 1), round((rh[2] + 1) * zell_mm, 1), round((rh[3] + 1) * zell_mm, 1)]
    rr, rl = _rahmen_mm(rahmen_r), _rahmen_mm(rahmen_l)
    rand = None
    if rr and rl:
        rand = {"links": round(rl[0] - rr[0], 1), "oben": round(rl[1] - rr[1], 1), "rechts": round(rl[2] - rr[2], 1), "unten": round(rl[3] - rr[3], 1)}
    return {
        "raster": [gw, gh], "zelle_px": ZELLE, "zellen_mit_inhalt": zellen_mit_inhalt, "zellen_abweichend": len(abweichend),
        "anteil": (len(abweichend) / zellen_mit_inhalt) if zellen_mit_inhalt else 0.0,
        "tinte_ref": tinte_r, "tinte_lun": tinte_l, "tintenverhaeltnis": (tinte_l / tinte_r) if tinte_r else None,
        "rahmen_ref_mm": rr, "rahmen_lun_mm": rl, "rand_abweichung_mm": rand,
        "vertikaler_versatz_mm": round(_versatz(zeile_r, zeile_l) * zell_mm, 1) if tinte_r and tinte_l else None,
        "bereiche": _bereiche(abweichend, r, l, zell_mm, mm_pro_px),
        "groesse_lun_px": [breite, hoehe],
    }


def _versatz(a: list[int], b: list[int]) -> int:
    """Verschiebung (in Rasterzeilen) von ``b`` gegenüber ``a`` mit der kleinsten Summe der Abweichungen; 0, wenn keine Verschiebung besser ist als keine."""
    n = len(a)
    bester, beste_summe = 0, None
    for k in range(-MAX_SHIFT, MAX_SHIFT + 1):
        s = 0
        for i in range(max(0, k), min(n, n + k)):
            s += abs(a[i - k] - b[i])
        if beste_summe is None or s < beste_summe or (s == beste_summe and abs(k) < abs(bester)):
            bester, beste_summe = k, s
    return bester


def _bereiche(zellen: list, r: list[bytes], l: list[bytes], zell_mm: float, mm_pro_px: float) -> list[dict]:
    """Zusammenhängende abweichende Zellen (8er-Nachbarschaft) als Rechtecke in Bildpunkten des Lunivo-Bilds, größte zuerst, höchstens 60."""
    menge = {(x, y): d for x, y, d in zellen}
    gesehen: set = set()
    aus = []
    for start in menge:
        if start in gesehen:
            continue
        gesehen.add(start)
        schlange = deque([start])
        x0 = x1 = start[0]
        y0 = y1 = start[1]
        n, summe, tinte = 0, 0, 0
        while schlange:
            x, y = schlange.popleft()
            n += 1
            summe += menge[(x, y)]
            tinte += r[y][x] + l[y][x]
            x0, x1, y0, y1 = min(x0, x), max(x1, x), min(y0, y), max(y1, y)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    p = (x + dx, y + dy)
                    if p in menge and p not in gesehen:
                        gesehen.add(p)
                        schlange.append(p)
        if summe < -0.25 * tinte:
            art = "fehlt in Lunivo"
        elif summe > 0.25 * tinte:
            art = "zusätzlich in Lunivo"
        else:
            art = "anders gesetzt"
        aus.append({"x": x0 * ZELLE, "y": y0 * ZELLE, "w": (x1 - x0 + 1) * ZELLE, "h": (y1 - y0 + 1) * ZELLE, "zellen": n, "art": art,
                    "mm": [round(x0 * zell_mm, 1), round(y0 * zell_mm, 1)]})
    aus.sort(key=lambda b: -b["zellen"])
    return aus[:60]
