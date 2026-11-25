"""Textdarstellung für frei positionierte Objekte."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QLinearGradient, QPainter

from core.objekte.bilder.modell.bildeffekte import gespiegelt

ARTEN = ("wordart", "textfeld", "form", "diagramm", "smartart", "piktogramm", "zeichenbereich")
TEXT_ARTEN = ("wordart", "textfeld")                                 # Arten mit Text zum Schreiben (Texttools, Eingabefeld im Objekt)
STANDARD_MASS = {"form": (160, 120), "diagramm": (480, 300), "zeichenbereich": (567, 302)}         # Größe in Bildpunkten, wenn beim Einfügen keine angegeben ist
FORM_STANDARD = {"form": "Rechteck", "fuell": "#4a8fd8", "linie": "#1f3864", "strich": 2.0, "text": ""}
TEXTFELD_STANDARD = {"text": "", "schrift": "Liberation Sans", "pt": 11, "farbe": "#1f1f1f"}
TEXTFELD_FUELL = {"art": "farbe", "farbe": "#ffffff"}
TEXTFELD_RAND = {"b": 1.5, "farbe": "#1f3864", "art": "einfach"}
WORDART_STANDARD = {"text": "Hier Text einfügen", "vorlage": 0, "pt": 36, "schrift": "Liberation Sans"}
_SS = 2                                                              # Zeichnen in doppelter Auflösung (scharf auch bei Zoom)


# ---- Gemeinsame Hilfen: Listenmarken, Textrichtung, Effekte ---------------------------------------------------------------
RICHTUNGEN = ("waagerecht", "senkrecht_rl", "senkrecht_lr", "dreh90", "dreh270", "asiatisch270")
from core.layout.drucklayout.ausgabe.text.wordartobjekt import _PUNKTE, listenmarken  # noqa: E402,F401  (Listenmarken: reine Datenhilfe des Kerns)


def richtung_anwenden(img: QImage, richtung: str | None, zeilenbaender: list | None = None) -> QImage:
    """Die Textrichtung am fertigen (waagerecht gesetzten) Bild: senkrecht_rl und dreh90 laufen von oben nach unten (Zeilen von rechts nach links),
    senkrecht_lr ebenso, aber die Zeilen folgen von links nach rechts, dreh270 dreht gegen den Uhrzeigersinn, asiatisch270 setzt lateinische
    Schrift wie senkrecht_rl (asiatische Zeichen werden nicht besonders gedreht)."""
    from PySide6.QtGui import QTransform
    if richtung in (None, "", "waagerecht"):
        return img
    if richtung == "vertikal":
        richtung = "senkrecht_rl"
    if richtung == "senkrecht_lr" and zeilenbaender:                 # Zeilen in umgekehrter Reihenfolge stapeln
        neu = QImage(img.size(), QImage.Format_ARGB32); neu.fill(Qt.transparent)
        q = QPainter(neu); y = 0
        for (y0, hh) in reversed(zeilenbaender):
            q.drawImage(0, y, img, 0, y0, img.width(), hh); y += hh
        q.end(); img = neu
    grad = 270 if richtung == "dreh270" else 90
    return img.transformed(QTransform().rotate(grad), Qt.SmoothTransformation)


def _gedreht(richtung: str | None) -> bool:
    return richtung not in (None, "", "waagerecht")


def effekte_auf_text(img: QImage, ef: dict, text_hoehe: float, farbe: str) -> QImage:
    """Leuchten und Spiegelung am fertig gezeichneten Text (durchsichtiges Bild in doppelter Auflösung)."""
    if not ef:
        return img
    out = QImage(img.size(), QImage.Format_ARGB32); out.fill(Qt.transparent)
    q = QPainter(out)
    if "leuchten" in ef:
        glut = QColor((ef["leuchten"] or {}).get("farbe") or farbe)
        maske = QImage(img.size(), QImage.Format_ARGB32); maske.fill(Qt.transparent)
        m = QPainter(maske); m.drawImage(0, 0, img); m.setCompositionMode(QPainter.CompositionMode_SourceIn); m.fillRect(maske.rect(), glut); m.end()
        q.setOpacity(0.16)
        import math
        for rad in (4, 8, 12):
            for k in range(12):
                w = 2 * math.pi * k / 12
                q.drawImage(round(math.cos(w) * rad), round(math.sin(w) * rad), maske)
        q.setOpacity(1.0)
    q.drawImage(0, 0, img)
    if "reflektion" in ef:                                           # Spiegelbild unter dem Text, nach unten verblassend
        th = int(text_hoehe * _SS)
        unten = gespiegelt(img.copy(0, 0, img.width(), max(1, min(th, img.height()))), senkrecht=True)
        r = QPainter(unten); r.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        g = QLinearGradient(0, 0, 0, unten.height()); g.setColorAt(0, QColor(0, 0, 0, 110)); g.setColorAt(0.7, QColor(0, 0, 0, 0))
        r.fillRect(unten.rect(), g); r.end()
        q.drawImage(0, th, unten)
    q.end()
    return out


# ---- Läufe: Text mit Zeichenformat je Abschnitt -------------------------------------------------------------------------------
from core.layout.drucklayout.ausgabe.text.wordartobjekt import ZEICHEN_SCHLUESSEL, anzeige_laeufe, laeufe_text  # noqa: E402,F401


def laeufe_ab(laeufe: list[dict], von: int, bis: int | None = None) -> list[dict]:
    """Der Ausschnitt ``[von, bis)`` des Gesamttextes mit seinen Formaten."""
    out, pos = [], 0
    for r in laeufe:
        n = len(r["t"]); a, e = max(von, pos), min(pos + n if bis is None else bis, pos + n)
        if e > a:
            out.append({**r, "t": r["t"][a - pos:e - pos]})
        pos += n
    return out


def laeufe_zusammen(laeufe: list[dict]) -> list[dict]:
    """Benachbarte Läufe mit gleichem Format zu einem verbinden (leere fallen weg)."""
    out: list[dict] = []
    for r in laeufe:
        if not r["t"]:
            continue
        if out and {k: v for k, v in out[-1].items() if k != "t"} == {k: v for k, v in r.items() if k != "t"}:
            out[-1] = {**out[-1], "t": out[-1]["t"] + r["t"]}
        else:
            out.append(dict(r))
    return out


from core.layout.drucklayout.ausgabe.text.wordartobjekt import zeilen_laeufe as _zeilen_laeufe  # noqa: E402,F401


# ---- WordArt zeichnen ---------------------------------------------------------------------------------------------------
def wordart_zeichnen(d: dict) -> QImage:
    """Das WordArt-Objekt als Bild in doppelter Auflösung; Satz und Zeichnung kommen vom Kern (``core/rendering/wordartobjekt.py``), hier wird nur die Textrichtung am Bild angewendet."""
    from core.layout.drucklayout.ausgabe.text.wordartobjekt import wordart_rgba
    from framework.dokumentverwaltung.ausgabe.textsatz import standard_engine
    from core.bearbeitung import einfuegen as E
    laeufe = anzeige_laeufe(d)
    text = laeufe_text(laeufe) or " "
    pt = float(d.get("pt", 36))
    if d.get("vorlage") is None:                                       # alter Weg: Stil und Farbe
        return E.wordart_bild(text, d.get("stil", "Verlauf"), d.get("schrift", "Liberation Sans"), int(pt), d.get("farbe", "#2f78bd"))
    erg = wordart_rgba(d, standard_engine(), E.WORDART_VORLAGEN, _SS)
    img = QImage(bytes(erg["rgba"]), erg["w"], erg["h"], erg["w"] * 4, QImage.Format_RGBA8888).copy()
    ys, asz, hoehen, faktor = erg["ys"], erg["asz"], erg["hoehen"], erg["faktor"]
    return richtung_anwenden(img, d.get("richtung"), [(int((ys[i] - asz[i]) * _SS), int(hoehen[i] * faktor * _SS)) for i in range(erg["zeilen"])])


# ---- Textfeld zeichnen --------------------------------------------------------------------------------------------------
def _zeichen_dict(d: dict, lauf: dict, vorlage, farbe_ueber: str | None, standard_farbe: str) -> dict:
    """Das Zeichenformat eines Laufs im Dokumentenmodell: seine eigenen Angaben, sonst die des Objekts."""
    e = {k: lauf.get(k, d.get(k)) for k in ZEICHEN_SCHLUESSEL}
    z: dict = {"schrift": e["schrift"] or d.get("schrift", "Liberation Sans"), "groesse_pt": float(e["pt"] or d.get("pt", 11))}
    if e["fett"]:
        z["fett"] = True
    if e["kursiv"]:
        z["kursiv"] = True
    if e["unter"]:
        z["unterstrichen"] = True
        if isinstance(e["unter"], str) and e["unter"] != "einfach":
            z["unter_art"] = e["unter"]
        if e["unterfarbe"]:
            z["unter_farbe"] = e["unterfarbe"]
    if e["durch"]:
        z["durchgestrichen"] = True
    if e["hoch"]:
        z["hoch_tief"] = "hoch"
    elif e["tief"]:
        z["hoch_tief"] = "tief"
    if e["hervor"]:
        z["marker"] = e["hervor"]
    kontur = e["kontur"] if e["kontur"] is not None else (vorlage[3] if vorlage and "kontur" not in d else None)
    if kontur:
        z["effekt"] = {"kontur": True, "kontur_farbe": kontur, "kontur_breite": float(d.get("kontur_breite", 0.75))}
    if farbe_ueber:
        z["farbe"] = farbe_ueber
    elif "fuell" in lauf:
        z["farbe"] = lauf["fuell"] or "#00000000"                       # leer = ausdrücklich keine Füllung
    else:
        z["farbe"] = standard_farbe
    return z


TEXTRAND = 8.0                                                 # Standard-Innenabstand des Textes im Feld (Bildpunkte); ``d["innen"]`` = [links, oben, rechts, unten] überschreibt ihn


def _innen(d: dict) -> tuple[float, float, float, float]:
    """Innenabstand links, oben, rechts, unten — aus ``d["innen"]`` (zum Beispiel aus bodyPr lIns/tIns/rIns/bIns einer DOCX), sonst ``TEXTRAND``."""
    w = d.get("innen")
    if isinstance(w, (list, tuple)) and len(w) == 4:
        try:
            return tuple(max(0.0, float(x)) for x in w)
        except (TypeError, ValueError):
            pass
    return (TEXTRAND,) * 4


class _Satz:
    """Das gesetzte Textfeld: ein Dokument in der Größe des Feldes (Innenabstand = Seitenrand), gesetzt von der Layout-Engine des Kerns. Was nicht mehr
    passt, steht auf Seite 2 — daran erkennen verknüpfte Felder, wie viel Text in ein Feld passt."""

    def __init__(self, d: dict, laeufe: list[dict], b: float, h: float, farbe_ueber: str | None = None):
        from core.dokument import neues_dokument
        from core.dokument.dokument import Absatz, Lauf
        from core.layout import LayoutEngine
        from core.dokument.abschnitte.seite import PageSettings
        vorlage = None
        if d.get("vorlage") is not None:
            from core.bearbeitung import einfuegen as E
            vorlage = E.WORDART_VORLAGEN[int(d["vorlage"])]
        self.farbe = d.get("fuell") if d.get("fuell") else (vorlage[1] if vorlage and "fuell" not in d else d.get("farbe", "#1f1f1f"))
        li, ob, re_, un = _innen(d)
        self.innen_oben = ob
        breit = max(10.0, b - li - re_)
        mm = 25.4 / 96.0                                               # Bildpunkte → Millimeter
        seite = PageSettings(width_mm=(li + breit + min(4.0, breit * 0.01) + re_) * mm, height_mm=max(1.0, h) * mm, margin_left_mm=li * mm,
                             margin_right_mm=re_ * mm, margin_top_mm=ob * mm, margin_bottom_mm=un * mm)    # kleine Toleranz: Schriftmaße weichen um Bruchteile ab
        self.dok = neues_dokument(seite)
        af: dict = {"ausrichtung": "block" if d.get("ausr") in ("block", "verteilt") else d.get("ausr") if d.get("ausr") in ("mitte", "rechts") else "links"}
        if d.get("einzug"):
            af["einzug_links"] = 24.0 * int(d["einzug"])
        if d.get("zeilenabstand"):
            af.update({"zeilenabstand_art": "vielfach", "zeilenabstand": float(d["zeilenabstand"]) * 100})
        zeilen = _zeilen_laeufe(laeufe) or [[]]
        self.marken = listenmarken(d.get("liste"), len(zeilen))
        self.absatz_ids: list[int] = []
        self.laengen: list[int] = []
        bloecke = []
        for m_, zl in zip(self.marken, zeilen):
            inhalte = []
            if m_:
                inhalte.append(Lauf(m_, _zeichen_dict(d, {}, vorlage, farbe_ueber, self.farbe)))
            inhalte += [Lauf(r["t"], _zeichen_dict(d, r, vorlage, farbe_ueber, self.farbe)) for r in zl]
            a = Absatz(self.dok.neue_id(), inhalte, dict(af))
            bloecke.append(a)
            self.absatz_ids.append(a.id)
            self.laengen.append(sum(len(r["t"]) for r in zl))
        self.dok.abschnitte[0].bloecke = bloecke
        self.layout = LayoutEngine()
        self.erg = self.layout.berechnen(self.dok)

    def zeilen_seite1(self) -> list:
        return [p.rect for p in self.erg.seiten[0].plaetze if p.art == "zeile" and not p.kopie]

    def text_hoehe(self) -> float:
        """Obere Kante des Innenraums bis zur Unterkante der letzten Zeile auf dem Feld."""
        return max([r.bottom for r in self.zeilen_seite1()] + [self.innen_oben])

    def malen(self, p: QPainter) -> None:
        from vcl.qt.rendering.formen.anzeige import seite_malen
        seite_malen(p, self.layout.engine, self.dok, self.erg, 0, None)


def _text_passt(d: dict, laeufe: list[dict], b: float, h: float) -> int:
    """Wie viele Zeichen der Läufe im Feld ``b`` x ``h`` stehen (Anfang der ersten Zeile, die nicht mehr passt) — für verknüpfte Textfelder."""
    satz = _Satz(d, laeufe, b, h)
    vorher = 0                                                         # Zeichen der Absätze davor samt Zeilenwechsel
    for i, aid in enumerate(satz.absatz_ids):
        ort = satz.erg.absaetze.get(aid)
        if ort is not None:
            for seite, zi, _r in ort.zeilen:
                if seite > 0:
                    return max(0, vorher + max(0, ort.satz.zeilen[zi].box.start - len(satz.marken[i] or "")))
        vorher += satz.laengen[i] + 1
    return len(laeufe_text(laeufe))


def _text_malen(img: QImage, d: dict, satz: _Satz, b: float, h: float) -> None:
    """Den gesetzten Text ins Bild malen; mit dem Effekt „Schatten“ darunter derselbe Text in der Schattenfarbe, leicht versetzt."""
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.TextAntialiasing); p.scale(_SS, _SS)
    ef = d.get("effekt") or {}
    if "schatten" in ef:
        sf = (ef["schatten"] or {}).get("farbe") or "#8a8a8a"
        p.save(); p.translate(2, 2); _Satz(d, anzeige_laeufe(d), b, h, sf).malen(p); p.restore()
    satz.malen(p)
    p.end()


def _zeilenbaender(satz: _Satz, hoehe: int) -> list[tuple[int, int]]:
    """(oben, Höhe) jeder Textzeile in Bildpunkten des Bildes; dazu der Rand darüber und darunter als eigene Bänder, damit nichts verloren geht."""
    bander = [(int(r.y * _SS), int(r.height * _SS)) for r in satz.zeilen_seite1()]
    if not bander:
        return bander
    if bander[0][0] > 0:
        bander.insert(0, (0, bander[0][0]))
    letzte = bander[-1][0] + bander[-1][1]
    if letzte < hoehe:
        bander.append((letzte, hoehe - letzte))
    return bander


def textfeld_zeichnen(d: dict, b: float, h: float) -> QImage:
    """Nur der Text (durchsichtig); Füllung und Rand legt die Angabe des Bildes darum (so wirken Füllung und Kontur der Schnellleiste).
    Gezeichnet werden alle Schlüssel der Texttools: fett, kursiv, unter, durch, hoch, tief, hervor, fuell/farbe, kontur, effekt (schatten,
    reflektion, leuchten), vorlage, ausr (block, verteilt), liste, einzug, zeilenabstand, richtung. Bei verknüpften Feldern steht in ``gezeigt``
    der Teil des Textes, der in diesem Feld steht. Gesetzt wird der Text vom Kern (``LayoutEngine``), gezeichnet vom ``DokumentRenderer``."""
    richt = d.get("richtung")
    if richt == "vertikal":
        richt = "senkrecht_rl"
    if _gedreht(richt):
        b, h = h, b
    img = QImage(max(1, int(b * _SS)), max(1, int(h * _SS)), QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    satz = _Satz(d, anzeige_laeufe(d), b, h)
    _text_malen(img, d, satz, b, h)
    ef = d.get("effekt") or {}
    if "leuchten" in ef or "reflektion" in ef:
        img = effekte_auf_text(img, {k: v for k, v in ef.items() if k in ("leuchten", "reflektion")}, satz.text_hoehe(), satz.farbe)
    return richtung_anwenden(img, richt, _zeilenbaender(satz, img.height()) if richt == "senkrecht_lr" else None)
