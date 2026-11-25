"""Absatzsatz im Fluss: Läufe, Listenmarken, Objekte in der Zeile, Absatzregeln. Ohne Qt. Teil des Flusses in ``seitenlayout.py``."""
from __future__ import annotations

import dataclasses
from lunivo_writer.core.dokument.dokument import Absatz, InlineObjekt, Lauf, Rahmen
from lunivo_writer.core.geometrie import Rect, mm_to_px
from lunivo_writer.core.textsatz.paragraph import OBJEKT, Absatzsatz, Objekt, absatz_setzen
from lunivo_writer.core.layout import formatwerte as F, regeln
from .ergebnis import AbsatzOrt, Platz, Seite
from .objektlayout import OBJEKT_ABSTAND, UMBRUCH_MIT_UMFLUSS, objekt_rechteck
from .geometrie import STANDARD_OBJEKT



def _umbruch_art(satz, z):
    """``"seite"`` oder ``"spalte"``, wenn die Zeile mit einem Seiten- bzw. Spaltenumbruch endet (Zeilenwechsel-Zeichen mit dem Zeichenformat ``umbruch``), sonst ``None``."""
    i = z.ende - 1
    if i < z.box.start or satz.text[i] != "\u2028":
        return None
    for lauf in satz.laeufe:
        if lauf.start <= i < lauf.ende:
            return lauf.stil.get("umbruch") if isinstance(lauf.stil, dict) else None
    return None


umbruch_art = _umbruch_art                                                    # öffentlich für die Anzeige der Formatierungszeichen

class AbsatzLayout:
    """Absatzsatz im Fluss: Läufe, Listenmarken, Objekte in der Zeile, Absatzregeln."""

    @staticmethod
    def marken_von(a: Absatz, art: str = "f") -> list:
        """[(Zeichenstelle, Noten-Id)] der Notenmarken im Absatz; ``art`` „f“ Fußnoten, „e“ Endnoten."""
        res, pos = [], 0
        for x in a.inhalte:
            if isinstance(x, Lauf):
                v = x.format.get("note")
                if isinstance(v, str) and v.startswith(art + ":") and v[2:].isdigit():
                    res.append((pos, int(v[2:])))
                pos += len(x.text)
            else:
                pos += 1
        return res

    def regeln_an(self) -> bool:
        """Die Umbruchregeln gelten im Seitenfluss mit gleich breiten Spalten (nicht in Zellen und Rahmen)."""
        return self.seite is not None and self.seite.index >= 0 and len({round(b, 1) for _x, b in self.spalten}) == 1

    def satz(self, a: Absatz, af: dict, breite: float, ausschluss=None):
        """Den Absatz setzen: → (Absatzsatz, (Abstand davor, Abstand danach), Listenmarke, Abstand der Marke vom linken Rand)."""
        laeufe: list = []
        for x in a.inhalte:
            if isinstance(x, Lauf):
                if not x.text:
                    continue
                z = F.zeichenformat(self.dok, a, x.format)
                font, stil = F.schrift(z), self.lese_stil(F.stil(z), z)
                if F.kapitaelchen(z):
                    laeufe.extend((t, f, stil) for t, f in F.kapitaelchen_stuecke(x.text, font))
                elif self.opt.get("silben"):
                    laeufe.extend((t, font, st) for t, st in self.silben_stuecke(F.schreibweise(x.text, z), stil))
                else:
                    laeufe.append((F.schreibweise(x.text, z), font, stil))
            elif isinstance(x, InlineObjekt):
                b = x.breite or STANDARD_OBJEKT[0]
                h = x.hoehe or STANDARD_OBJEKT[1]
                laeufe.append((OBJEKT, Objekt(b, h), {"objekt": x.id}))
        links, rechts, erste = F.einzuege(af)
        marke, marke_x = self.marken.get(a.id), 0.0
        definition = self.dok.listen.get(a.liste_id) if a.liste_id is not None else None
        if marke is not None and definition is not None and definition.ebenen:
            ausr, text = F.listen_einzug(definition.ebenen[min(max(a.ebene, 0), len(definition.ebenen) - 1)])
            if "einzug_links" not in af:
                links = text
            if "einzug_erste" not in af:
                erste = 0.0                                                # der Text beginnt in allen Zeilen bei ``einzug``, die Marke steht davor
            marke_x = max(0.0, links - (text - ausr))
        art, wert = F.zeilenabstand(af)
        luft = float(self.opt.get("zeilenluft") or 1.0)
        if luft != 1.0:                                               # Lesehilfe: mehr oder weniger Luft zwischen den Zeilen
            art, wert = ("proportional", 100.0 * luft) if art == "single" else (art, wert * luft if art == "proportional" else wert)
        leer = F.schrift(F.zeichenformat(self.dok, a, a.zeichenformat))
        tabs, tab_abstand = F.tabstopps(af, self.dok)
        satz = absatz_setzen(self.engine, laeufe, breite, F.ausrichtung(af), erste, links, rechts, art, wert, leer, ausschluss, tabs, tab_abstand,
                             F.tabfuellung(af), F.richtung(af), self.trenner())
        return satz, F.abstaende(af), marke, marke_x

    def trenner(self):
        """Die Trennfunktion der Silbentrennung (``textlayout.trennung``), wenn sie für den Abschnitt (``seite.silbentrennung``) oder die Ansicht
        (``opt["silbentrennung"]``) gilt; sonst ``None``."""
        an = self.opt.get("silbentrennung")
        if an is None:
            an = bool(getattr(getattr(self, "einr", None), "silbentrennung", False))
        if not an:
            return None
        sprache = str(self.opt.get("sprache") or getattr(getattr(self, "einr", None), "silben_sprache", None) or self.dok.eigenschaften.get("sprache") or "de_DE")
        if sprache not in self._trenner_cache:
            from lunivo_writer.core.textsatz.trennung import trenner_fuer
            self._trenner_cache[sprache] = trenner_fuer(sprache)
        return self._trenner_cache[sprache]

    _trenner_cache: dict = {}

    def silben_stuecke(self, text: str, stil: dict) -> list:
        """Der Text in Stücke je Silbe mit abwechselnden Farben (Lesehilfe „Silbenfarben“); ``opt["silben"]``: ``funktion`` (Wort → Silben), ``farben``
        ((r, g, b, a) …), ``darstellung`` („Schriftfarbe“, „Hintergrund (Marker)“ oder beides), ``einsilbig``, ``neu_pro_wort``, ``mindestens``."""
        k = self.opt["silben"]
        farben = k["farben"]
        aus: list = []
        pos, n = 0, 0
        for m in self._WORT.finditer(text):
            wort = m.group(0)
            teile = k["funktion"](wort)
            if len(wort) < k.get("mindestens", 4) or (len(teile) < 2 and not k.get("einsilbig", True)):
                continue
            if m.start() > pos:
                aus.append((text[pos:m.start()], stil))
            if k.get("neu_pro_wort", True):
                n = 0
            for t in teile:
                f = farben[n % len(farben)]
                st = dict(stil)
                if k.get("darstellung", "Schriftfarbe") in ("Schriftfarbe", "Schriftfarbe und Hintergrund"):
                    st["color"] = f
                if k.get("darstellung") in ("Hintergrund (Marker)", "Schriftfarbe und Hintergrund"):
                    st["highlight"] = (f[0], f[1], f[2], 70)
                aus.append((t, st))
                n += 1
            pos = m.end()
        if pos < len(text):
            aus.append((text[pos:], stil))
        return aus or [(text, stil)]

    def lese_stil(self, stil: dict, z: dict) -> dict:
        """Der Stil eines Textstücks mit den Einstellungen der Lesehilfe (Buchstaben- und Wortabstand) und ohne ausgeblendeten Text."""
        if self.opt.get("versteckt") is False and z.get("versteckt"):
            stil = dict(stil, color=(0, 0, 0, 0), underline=False, strike=False, highlight=None)
        if self.opt.get("buchstaben"):
            stil = dict(stil, sperrung=stil.get("sperrung", 0.0) + float(self.opt["buchstaben"]))
        if self.opt.get("wort"):
            stil = dict(stil, wortabstand=stil.get("wortabstand", 0.0) + float(self.opt["wort"]))
        return stil

    def umbruch_stelle(self, hs: list, w: dict, folge: list):
        def naechste():
            for b in folge:
                if not isinstance(b, Absatz):
                    return
                bf = F.absatzformat(self.dok, b)
                satz, (oben, _u), _m, _x = self.satz(b, bf, self.breite())
                yield F.regeln(bf), [z.hoehe for z in satz.zeilen], oben
        return regeln.umbruch_stelle(hs, w, self.frei() - self.y, self.frei(), self.leer, naechste)

    def objekte_platzieren(self, a: Absatz) -> None:
        """Frei positionierte Objekte dieses Absatzes auf die Seite legen; Objekte mit Umfluss engen den folgenden Text ein."""
        for o in sorted(self.frei_an.get(a.id, ()), key=lambda x: x.ebene) if self.frei_an else ():
            p = self.einr
            if self.seite.index < 0:                                       # in Zelle oder Rahmen: Lage relativ zum Ankerabsatz und zur Spalte
                o = dataclasses.replace(o, bezug_h="spalte", bezug_v="absatz")
            r = objekt_rechteck(o, mm_to_px(p.width_mm), mm_to_px(p.height_mm), self.rand_links, self.rand_oben,
                                p.content_width_px, p.content_height_px, self.rand_oben + self.y, self.links(), self.seite.nummer, self.breite())
            self.seite.plaetze.append(Platz("objekt", r, o.id, daten=o.umbruch))
            if self.seite.index >= 0:
                self.erg.objekte[o.id] = (self.seite.index, r)
            if o.umbruch in UMBRUCH_MIT_UMFLUSS:
                mitte = self.links() + self.breite() / 2
                art = "voll" if o.umbruch == "oben_unten" else "links" if r.center.x < mitte else "rechts"
                zone = r.adjusted(-OBJEKT_ABSTAND, -OBJEKT_ABSTAND, OBJEKT_ABSTAND, OBJEKT_ABSTAND)
                self.ausschluesse.append((self.seite.index, self.spalte, zone, art))

    def absatz(self, a: Absatz, folge: list = ()) -> None:
        af = F.absatzformat(self.dok, a)
        web = bool(self.opt.get("web"))
        if F.umbruch_vor(af) and not self.leer and not web:
            self.neue_seite()
        elif F.spaltenumbruch_vor(af) and not self.leer:
            self.weiter()
        oben, _unten = F.abstaende(af)
        hat_objekte = bool(self.frei_an) and a.id in self.frei_an
        if hat_objekte and not self.leer:
            erste_h = self.satz(a, af, self.breite())[0].zeilen[0].hoehe
            if self.y + max(0.0, oben - self.unten) + erste_h > self.frei() + 0.01:
                self.weiter()                                              # das Ankerobjekt folgt der ersten Zeile auf die nächste Seite
        self.abstand_vor(oben)
        if hat_objekte:
            self.objekte_platzieren(a)
        satz, (_o, unten), marke, marke_x = self.satz(a, af, self.breite(), self.ausschluss_fuer() if self.ausschluesse else None)
        ort = AbsatzOrt(a.id, satz, marke=marke, marke_x=marke_x, ohne_zeilennummer=F.option(af, "ohne_zeilennr"),
                        hintergrund=F.hintergrund(af), rahmen=F.absatzrahmen(af))
        self.erg.absaetze[a.id] = ort
        self.endnoten.extend(nid for _stelle, nid in self.marken_von(a, "e"))
        marken = self.marken_von(a)
        bruch = self.umbruch_stelle([z.hoehe for z in satz.zeilen], F.regeln(af), list(folge)) if self.regeln_an() and satz.zeilen else None
        erzwungen = None                                                       # Seiten-/Spaltenumbruch am Ende der vorigen Zeile (Umbruch mitten im Absatz)
        for i, z in enumerate(satz.zeilen):
            if erzwungen:
                self.neue_seite() if erzwungen == "seite" else self.weiter()
                erzwungen = None
            if i == bruch and not self.leer:
                self.weiter()
            neu = [nid for stelle, nid in marken if z.box.start <= stelle < z.ende and nid in self.noten_text]
            extra = 0.0
            if neu and self.seite.index >= 0:
                bisher = self.noten.get(self.seite.index, [])
                extra = self.noten_hoehe(bisher + [(0, nid) for nid in neu]) - self.noten_hoehe(bisher)
            self.platz_fuer(z.hoehe, extra)
            if neu and self.seite.index >= 0:
                for nid in neu:
                    self.noten_zaehler += 1
                    self.noten.setdefault(self.seite.index, []).append((self.noten_zaehler, nid))
            r = Rect(self.links(), self.rand_oben + self.y, self.breite(), z.hoehe)
            ort.zeilen.append((self.seite.index, i, r))
            self.seite.plaetze.append(Platz("zeile", r, a.id, i))
            self.y += z.hoehe
            self.leer = False
            erzwungen = None if web else _umbruch_art(satz, z)
        self.unten = unten
        self.y += unten
        if erzwungen:                                                          # der Absatz endet mit einem Umbruch: der nächste Block beginnt auf der neuen Seite bzw. in der nächsten Spalte
            self.neue_seite() if erzwungen == "seite" else self.weiter()
        if F.umbruch_nach(af) and not self.opt.get("web"):
            self.neue_seite()
