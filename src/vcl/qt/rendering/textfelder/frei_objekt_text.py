from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QLinearGradient, QPainter
from vcl.qt.rendering.formen import gespiegelt
from core.formatierung.farben.farben import Farbe
from vcl.qt.widgets.bausteine.farben.farben import DURCHSICHTIG, SCHATTENANSATZ
from core.layout.drucklayout.ausgabe.text.wordartobjekt import listenmarken
from core.layout.drucklayout.ausgabe.text.wordartobjekt import anzeige_laeufe, laeufe_text
from core.layout.drucklayout.ausgabe.text.wordartobjekt import zeilen_laeufe as _zeilen_laeufe  # noqa: E402,F401
from core.objekte.textfelder.modell.frei_objekt_text_daten import _SS, _gedreht, _innen, _zeichen_dict


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
        g = QLinearGradient(0, 0, 0, unten.height()); g.setColorAt(0, QColor(*SCHATTENANSATZ)); g.setColorAt(0.7, QColor(*DURCHSICHTIG))
        r.fillRect(unten.rect(), g); r.end()
        q.drawImage(0, th, unten)
    q.end()
    return out


# ---- WordArt zeichnen ---------------------------------------------------------------------------------------------------
def wordart_zeichnen(d: dict) -> QImage:
    """Das WordArt-Objekt als Bild in doppelter Auflösung; Satz und Zeichnung kommen vom Kern (``core/rendering/wordartobjekt.py``), hier wird nur die Textrichtung am Bild angewendet."""
    from core.layout.drucklayout.ausgabe.text.wordartobjekt import wordart_rgba
    from framework.dokumentverwaltung.ausgabe.textsatz import standard_engine
    from vcl.qt.rendering.formen import einfuegen as E
    laeufe = anzeige_laeufe(d)
    text = laeufe_text(laeufe) or " "
    pt = float(d.get("pt", 36))
    if d.get("vorlage") is None:                                       # alter Weg: Stil und Farbe
        from vcl.qt.rendering import wordart as WE
        return WE.wordart_bild(text, d.get("stil", "Verlauf"), d.get("schrift", "Liberation Sans"), int(pt), d.get("farbe", Farbe.WORDART_BLAU))
    erg = wordart_rgba(d, standard_engine(), E.WORDART_VORLAGEN, _SS)
    img = QImage(bytes(erg["rgba"]), erg["w"], erg["h"], erg["w"] * 4, QImage.Format_RGBA8888).copy()
    ys, asz, hoehen, faktor = erg["ys"], erg["asz"], erg["hoehen"], erg["faktor"]
    return richtung_anwenden(img, d.get("richtung"), [(int((ys[i] - asz[i]) * _SS), int(hoehen[i] * faktor * _SS)) for i in range(erg["zeilen"])])


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
            from vcl.qt.rendering.formen import einfuegen as E
            vorlage = E.WORDART_VORLAGEN[int(d["vorlage"])]
        self.farbe = d.get("fuell") if d.get("fuell") else (vorlage[1] if vorlage and "fuell" not in d else d.get("farbe", Farbe.TEXT_STANDARD))
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
        from vcl.qt.rendering.formen import seite_malen
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
        sf = (ef["schatten"] or {}).get("farbe") or Farbe.SCHATTEN_GRAU
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
