"""Weitere Bildtools für frei positionierte Bilder (Datei, Bildschirmfoto, Piktogramm): Seitenverhältnis sperren, transparente Farbe,
Bild ändern (andere Datei, gleiche Größe und Rahmen), Bilder komprimieren, Bild zurücksetzen, Helligkeit/Kontrast (nicht zerstörend). Die Angabe des Bildes steht in
``freie_bilder``; geschrieben wird über ``bildlayout``. Kein HTML: QImage."""
from __future__ import annotations

from PySide6.QtCore import QRect, QUrl, Qt
from PySide6.QtGui import QColor, QImage, QTextDocument

from lunivo_writer.editor import bildlayout as BL
from lunivo_writer.editor import bildzuschnitt as BZ
from lunivo_writer.editor import freie_bilder as FB

KOMPRIMIEREN_FAKTOR = 1.5                                           # Bildpunkte je Anzeigepunkt nach dem Komprimieren (entspricht 144 dpi)
BILD_ARTEN = (None, "piktogramm")


def frei_bild(ed):
    """Das gewählte freie Bild (Datei, Bildschirmfoto, Piktogramm) als Ziel für ``bildlayout``, sonst None."""
    z = BL.ziel(ed) if ed else None
    return z if z is not None and z[0] == "frei" and z[2].get("art") in BILD_ARTEN else None


def sperre(z) -> bool:
    return bool(z and z[2].get("sperre"))


def sperre_umschalten(ed, z, an: bool | None = None) -> bool:
    """Seitenverhältnis sperren: Ziehen an den Kanten hält es dann auch, die Größen-Eingabe ebenfalls."""
    if z is None or z[0] != "frei":
        return False
    neu = not z[2].get("sperre") if an is None else bool(an)
    BL._speichern_frei(ed, z[1], {**z[2], "sperre": True} if neu else {k: v for k, v in z[2].items() if k != "sperre"})
    return True


def farbe_transparent(img: QImage, farbe: QColor, toleranz: int = 12) -> QImage:
    """Alle Bildpunkte, die ``farbe`` (innerhalb der Toleranz je Farbkanal) gleichen, werden durchsichtig."""
    out = img.convertToFormat(QImage.Format_ARGB32)
    r0, g0, b0 = farbe.red(), farbe.green(), farbe.blue()
    punkte = memoryview(out.bits()).cast("B").cast("I")             # ein 32-Bit-Wert je Bildpunkt (A, R, G, B)
    treffer: dict[int, bool] = {}
    for i, v in enumerate(punkte):
        t = treffer.get(v)
        if t is None:
            t = treffer[v] = (abs(((v >> 16) & 255) - r0) <= toleranz and abs(((v >> 8) & 255) - g0) <= toleranz and abs((v & 255) - b0) <= toleranz)
        if t:
            punkte[i] = 0
    return out


def transparent(ed, z, farbe: QColor, toleranz: int = 12) -> bool:
    return BL.frei_bild_ersetzen(ed, z, lambda img: farbe_transparent(img, farbe, toleranz))


def aendern(ed, z, bild: QImage, alt: str | None = None) -> bool:
    """Bild ändern: ``bild`` ersetzt den Inhalt; Größe, Lage, Rahmen, Füllung und Effekte bleiben, Zuschnitt und Farbänderung entfallen.
    Bei anderem Seitenverhältnis bleibt die Breite, die Höhe folgt."""
    if z is None or z[0] != "frei" or bild is None or bild.isNull():
        return False
    a = z[2]
    name = FB.neuer_name(ed.document())
    ed.document().addResource(QTextDocument.ImageResource, QUrl(name), bild)
    neu = {k: v for k, v in a.items() if k not in ("zu", "maske", "orig", "art", "daten")}
    neu["n"] = name
    neu["h"] = float(a["b"]) * bild.height() / max(1, bild.width())
    if alt is not None:
        neu["alt"] = alt
    BL._speichern_frei(ed, z[1], neu)
    return True


def aus_datei(ed, z, pfad: str) -> bool:
    img = QImage(pfad)
    return aendern(ed, z, img) if not img.isNull() else False


def komprimieren(ed, z, beschnitt_loeschen: bool = True) -> tuple[int, int] | None:
    """Bild komprimieren: weggeschnittene Bereiche löschen (wenn ``beschnitt_loeschen``) und auf ``KOMPRIMIEREN_FAKTOR`` × Anzeigegröße
    verkleinern (nie vergrößern). → (Bildpunkte vorher, nachher) oder None, wenn nichts zu tun war."""
    if z is None or z[0] != "frei":
        return None
    a = z[2]
    q = FB.bild_im_dokument(ed.document(), a.get("n", ""))
    if q is None:
        return None
    vorher = q.width() * q.height()
    img, neu = q, dict(a)
    l, o, r, u = BZ.lesen(a)
    if beschnitt_loeschen and any((l, o, r, u)):
        w, h = q.width(), q.height()
        img = q.copy(QRect(round(l * w), round(o * h), max(1, round(w * (1 - l - r))), max(1, round(h * (1 - o - u)))))
        neu.pop("zu", None)
        l = o = r = u = 0.0
    voll_b = float(a["b"]) / max(0.05, 1 - l - r)                    # Anzeigebreite des ganzen Bildes
    ziel_b = max(16, round(voll_b * KOMPRIMIEREN_FAKTOR))
    if ziel_b < img.width():
        img = img.scaledToWidth(ziel_b, mode=Qt.SmoothTransformation)
    if img is q:
        return None
    name = FB.neuer_name(ed.document())
    ed.document().addResource(QTextDocument.ImageResource, QUrl(name), img)
    neu["n"] = name
    neu.pop("orig", None)
    BL._speichern_frei(ed, z[1], neu)
    return vorher, img.width() * img.height()


# ---- Helligkeit und Kontrast (nicht zerstörend: ``hell`` und ``kontrast`` in der Angabe, in Prozent -100 bis 100) -------------------------------
SCHRITT = 10                                                       # „Heller/Dunkler“ und „Kontrast erhöhen/verringern“ ändern um 10 %
_KORRIGIERT: dict = {}                                             # kleiner Zwischenspeicher: (Bildschlüssel, hell, kontrast) → Bild


def werte(a: dict | None) -> tuple[int, int]:
    """(Helligkeit, Kontrast) in Prozent aus der Angabe des Bildes."""
    a = a or {}
    return int(a.get("hell", 0) or 0), int(a.get("kontrast", 0) or 0)


def korrigiert(bild: QImage, hell: int, kontrast: int) -> QImage:
    """Das Bild mit Helligkeit und Kontrast (Prozent): Kontrast streckt die Werte um die Mitte, Helligkeit verschiebt sie; Alpha bleibt.
    Rechnet über eine Tabelle je Farbwert (``bytes.translate``), das Original bleibt unverändert."""
    if not (hell or kontrast) or bild is None or bild.isNull():
        return bild
    schl = (bild.cacheKey(), hell, kontrast)
    if schl in _KORRIGIERT:
        return _KORRIGIERT[schl]
    f = (100 + kontrast) / 100.0 if kontrast <= 0 else 100.0 / max(1.0, 100 - kontrast * 0.9)
    tab = bytes(max(0, min(255, int(round((v - 127.5) * f + 127.5 + hell * 2.55)))) for v in range(256))
    q = bild.convertToFormat(QImage.Format_ARGB32)
    roh = bytes(q.constBits())
    out = bytearray(roh)
    for kanal in (0, 1, 2):                                        # B, G, R; Kanal 3 (Alpha) bleibt
        out[kanal::4] = roh[kanal::4].translate(tab)
    neu = QImage(bytes(out), q.width(), q.height(), q.bytesPerLine(), QImage.Format_ARGB32).copy()
    if len(_KORRIGIERT) > 6:
        _KORRIGIERT.clear()
    _KORRIGIERT[schl] = neu
    return neu


def korrektur_setzen(ed, z, hell: int | None = None, kontrast: int | None = None) -> bool:
    """Helligkeit und/oder Kontrast (begrenzt auf -100 bis 100) des freien Bildes setzen; 0 entfernt die Angabe."""
    if z is None or z[0] != "frei":
        return False
    neu = dict(z[2])
    for k, v in (("hell", hell), ("kontrast", kontrast)):
        if v is None:
            continue
        v = max(-100, min(100, int(v)))
        if v:
            neu[k] = v
        else:
            neu.pop(k, None)
    BL._speichern_frei(ed, z[1], neu)
    return True


def korrektur_schritt(ed, z, hell: int = 0, kontrast: int = 0) -> bool:
    """Helligkeit/Kontrast um die Schritte ``hell``/``kontrast`` (Prozent) ändern."""
    h, k = werte(z[2] if z else None)
    return korrektur_setzen(ed, z, h + hell, k + kontrast)


def zuruecksetzen(ed, z) -> bool:
    """Bild zurücksetzen: ursprüngliches Bild (vor Farbänderungen), kein Zuschnitt, keine Maske, Rahmen, Füllung, Effekte und Drehung weg;
    die Breite bleibt, die Höhe folgt dem Seitenverhältnis. Alternativtext und Lage bleiben."""
    if z is None or z[0] != "frei":
        return False
    a = z[2]
    n = a.get("orig") or a.get("n")
    q = FB.bild_im_dokument(ed.document(), n)
    if q is None:
        return False
    b = float(a["b"]) / max(0.05, 1 - BZ.lesen(a)[0] - BZ.lesen(a)[2])
    neu = {k: v for k, v in a.items() if k not in ("zu", "maske", "orig", "rand", "fuell", "fx", "sperre", "ellipse", "dreh", "hell", "kontrast")}
    neu.update(n=n, b=b, h=b * q.height() / max(1, q.width()), ellipse=False, dreh=0.0)
    BL._speichern_frei(ed, z[1], neu)
    return True
