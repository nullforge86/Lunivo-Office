"""Formen, Linien, Textrahmen und Gruppen nach ODT schreiben (Gegenstück zu ``odt_formen``), Qt-frei.

Eine Form wird zu ``draw:rect``, ``draw:ellipse``, ``draw:line`` oder ``draw:custom-shape`` (Art ``ooxml-<Name>``, die LibreOffice und Word-Importe kennen), ein Textfeld zu einem
``draw:frame`` mit ``draw:text-box``, eine Gruppe zu ``draw:g`` mit allen Teilen. Füllungen: einfarbig, Verlauf (``draw:gradient``), Muster als Schraffur (``draw:hatch``; Prozentmuster als
Mischfarbe) und Bild (``draw:fill-image``). Die benannten Verläufe, Schraffuren und Füllbilder gehören nach ``styles.xml`` (``zeichen_vorlagen``); Bilddaten kommen nach ``bilder``.
WordArt wird als Text mit seiner Schrift geschrieben; die Effekte (Verlauf, Kontur, Schatten, Verformung) kennt ODT so nicht und stehen im Bericht."""
from __future__ import annotations

from xml.sax.saxutils import escape

from lunivo_writer.kern.dokument.bildformat import FORMATE, format_erkennen
from lunivo_writer.dienste.docx_formen import _GEOMETRIE_UMGEKEHRT
from lunivo_writer.dienste.odt_basis import ATTR_QUOTE, AUSR_H, AUSR_V, BEZUG_H, BEZUG_V, ODT_BILDFORMATE, _laenge

_DREH = {"h": ("0", "single"), "v": ("900", "single"), "ab": ("1350", "single"), "auf": ("450", "single"), "raster": ("0", "double"), "karo": ("450", "double")}
FORMEN = ("form", "textfeld", "gruppe", "wordart")


def _a(wert) -> str:
    return escape(str(wert), ATTR_QUOTE)


def _mischen(vorn: str, hinten: str, anteil: float) -> str:
    """Mischfarbe aus Muster- und Grundfarbe (Prozentmuster, die ODT nicht kennt)."""
    try:
        v = [int(vorn[i:i + 2], 16) for i in (1, 3, 5)]
        h = [int((hinten or "#ffffff")[i:i + 2], 16) for i in (1, 3, 5)]
    except ValueError:
        return vorn
    return "#" + "".join(f"{round(a * anteil + b * (1 - anteil)):02x}" for a, b in zip(v, h))


class FormenSchreiber:
    """Schreibt die Zeichenobjekte eines Dokuments; hält die dafür nötigen Vorlagen (Grafikstile in ``stile``, benannte Zeichenvorlagen in ``zeichen_vorlagen``)."""

    def __init__(self, stile: list, bilder: dict, bericht, ressourcen: dict):
        self.stile, self.bilder, self.rep, self.ressourcen = stile, bilder, bericht, ressourcen
        self.zeichen_vorlagen: list[str] = []
        self.n = 0
        self._gemeldet: set = set()

    def _melden(self, text: str) -> None:
        if text not in self._gemeldet:
            self._gemeldet.add(text)
            self.rep.warn(text)

    # ---- Füllung und Kontur
    def _fuell_eigenschaften(self, voll) -> str:
        if voll == {}:
            return ' draw:fill="none"'
        if not isinstance(voll, dict) or not voll:
            return ""
        art, farbe = voll.get("art", "farbe"), voll.get("farbe") or ""
        if art in ("farbe", "verlauf"):
            return f' draw:fill="solid" draw:fill-color="{_a(farbe)}"' if farbe else ' draw:fill="none"'
        if art == "graduell":
            stops = voll.get("stops") or []
            start, ende = (stops[0][1], stops[-1][1]) if len(stops) >= 2 else (voll.get("hell") or farbe, voll.get("dunkel") or "#ffffff")
            if len(stops) > 2:
                self._melden("Ein Farbverlauf mit mehr als zwei Farben wurde in der ODT-Datei auf Anfangs- und Endfarbe verkürzt.")
            self.n += 1
            name = f"LunivoVerlauf{self.n}"
            winkel = int(round((90.0 - float(voll.get("winkel", 90.0))) % 360))
            self.zeichen_vorlagen.append(f'<draw:gradient draw:name="{name}" draw:display-name="{name}" draw:style="linear" draw:start-color="{_a(start)}" '
                                         f'draw:end-color="{_a(ende)}" draw:start-intensity="100%" draw:end-intensity="100%" draw:angle="{winkel}deg" draw:border="0%"/>')
            return f' draw:fill="gradient" draw:fill-gradient-name="{name}"'
        if art == "muster":
            key = str(voll.get("key") or "rein")
            grund = voll.get("grund") or ""
            if key == "rein":
                return f' draw:fill="solid" draw:fill-color="{_a(farbe)}"'
            if key.startswith("pct"):
                self._melden("Ein Prozentmuster wurde in der ODT-Datei als Mischfarbe geschrieben (ODT kennt nur Linienschraffuren).")
                try:
                    anteil = float(key[3:].replace("_", ".")) / 100.0
                except ValueError:
                    anteil = 0.5
                return f' draw:fill="solid" draw:fill-color="{_mischen(farbe or "#000000", grund, anteil)}"'
            dichte, _, richtung = key.partition("_")
            drehung, stil = _DREH.get(richtung, ("0", "single"))
            self.n += 1
            name = f"LunivoSchraffur{self.n}"
            self.zeichen_vorlagen.append(f'<draw:hatch draw:name="{name}" draw:display-name="{name}" draw:style="{stil}" draw:color="{_a(farbe or "#000000")}" '
                                         f'draw:distance="{"0.05cm" if dichte == "hell" else "0.125cm"}" draw:rotation="{drehung}"/>')
            solid = ' draw:fill-hatch-solid="true"' if grund else ""
            return f' draw:fill="hatch" draw:fill-hatch-name="{name}"{solid}' + (f' draw:fill-color="{_a(grund)}"' if grund else "")
        if art == "bild":
            roh = self.ressourcen.get(str(voll.get("n") or ""))
            fmt = format_erkennen(roh) if roh else None
            if not roh or fmt not in ODT_BILDFORMATE:
                self._melden("Eine Bildfüllung hat kein Format, das ODT übernehmen kann; die Form bleibt ohne Füllung.")
                return ' draw:fill="none"'
            self.n += 1
            pfad = f"Pictures/fuellung{self.n}.{FORMATE[fmt][0]}"
            self.bilder[pfad] = roh
            name = f"LunivoBild{self.n}"
            self.zeichen_vorlagen.append(f'<draw:fill-image draw:name="{name}" draw:display-name="{name}" xlink:href="{pfad}" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/>')
            return f' draw:fill="bitmap" draw:fill-image-name="{name}" style:repeat="stretch"'
        return ""

    def _pfeilmarke(self, pfeil: str) -> str:
        """Pfeilspitzen als Linienenden (``draw:marker-start``/``-end``); die Markenvorlage steht einmal in ``styles.xml``."""
        if pfeil not in ("anfang", "ende", "beide"):
            return ""
        if "LunivoPfeil" not in self._gemeldet:
            self._gemeldet.add("LunivoPfeil")
            self.zeichen_vorlagen.append('<draw:marker draw:name="LunivoPfeil" draw:display-name="Pfeil" svg:viewBox="0 0 20 30" svg:d="m10 0-10 30h20z"/>')
        return ((' draw:marker-start="LunivoPfeil" draw:marker-start-width="0.3cm"' if pfeil in ("anfang", "beide") else "")
                + (' draw:marker-end="LunivoPfeil" draw:marker-end-width="0.3cm"' if pfeil in ("ende", "beide") else ""))

    def _kontur_eigenschaften(self, rand: dict | None, linie: str = "", strich: float = 0.0, pfeil: str = "") -> str:
        farbe = (rand or {}).get("farbe") or linie
        if not farbe:
            return ' draw:stroke="none"'
        b = float((rand or {}).get("b") or strich or 1.0)
        art = (rand or {}).get("art") or "einfach"
        if art in ("gepunktet", "fein_gestrichelt", "gestrichelt", "strichpunkt", "strichpunktpunkt"):
            self.n += 1
            name = f"LunivoStrich{self.n}"
            punkt, luecke = ("0.04cm", "0.08cm") if art == "gepunktet" else ("0.2cm", "0.15cm")
            self.zeichen_vorlagen.append(f'<draw:stroke-dash draw:name="{name}" draw:display-name="{name}" draw:style="rect" draw:dots1="1" draw:dots1-length="{punkt}" draw:distance="{luecke}"/>')
            return f' draw:stroke="dash" draw:stroke-dash="{name}" svg:stroke-width="{_laenge(b)}" svg:stroke-color="{_a(farbe)}"{self._pfeilmarke(pfeil)}'
        return f' draw:stroke="solid" svg:stroke-width="{_laenge(b)}" svg:stroke-color="{_a(farbe)}"{self._pfeilmarke(pfeil)}'

    def _grafikstil(self, voll, rand, linie: str, strich: float, lage: dict | None, hinter: bool, extra: str = "", pfeil: str = "") -> str:
        self.n += 1
        name = f"LunivoZ{self.n}"
        if lage is None:
            pos = ""
        else:
            pos = (f' style:wrap="run-through" style:run-through="{"background" if hinter else "foreground"}"'
                   f' style:horizontal-pos="{AUSR_H.get(lage.get("ah") or "", "from-left")}" style:horizontal-rel="{BEZUG_H.get(lage.get("bh"), "paragraph")}"'
                   f' style:vertical-pos="{AUSR_V.get(lage.get("av") or "", "from-top")}" style:vertical-rel="{BEZUG_V.get(lage.get("bv"), "paragraph")}"')
        self.stile.append(f'<style:style style:name="{name}" style:family="graphic"><style:graphic-properties{self._kontur_eigenschaften(rand, linie, strich, pfeil)}'
                          f'{self._fuell_eigenschaften(voll)}{extra}{pos}/></style:style>')
        return name

    # ---- Text
    def _absaetze(self, text: str, innen: dict, mitte: bool) -> str:
        self.n += 1
        name = f"LunivoT{self.n}"
        eig = ""
        if innen.get("schrift"):
            eig += f' fo:font-family="{_a(innen["schrift"])}"'
        if innen.get("pt"):
            eig += f' fo:font-size="{float(innen["pt"]):g}pt"'
        if innen.get("farbe"):
            eig += f' fo:color="{_a(innen["farbe"])}"'
        if innen.get("fett"):
            eig += ' fo:font-weight="bold"'
        if innen.get("kursiv"):
            eig += ' fo:font-style="italic"'
        self.stile.append(f'<style:style style:name="{name}" style:family="paragraph"><style:paragraph-properties fo:text-align="{"center" if mitte else "start"}"/>'
                          f'<style:text-properties{eig}/></style:style>')
        return "".join(f'<text:p text:style-name="{name}">{escape(z)}</text:p>' for z in (text or "").split("\n"))

    # ---- Objekte
    def element(self, art: str, breite: float, hoehe: float, daten: dict, alt: str, lage: dict | None, nr: int, x: float = 0.0, y: float = 0.0, hinter: bool = False) -> str:
        """Das Zeichenobjekt als XML-Text; ``lage`` = ``{"ah", "av", "bh", "bv"}`` bei freier Verankerung (sonst im Text), ``x``/``y`` = Versatz (Bildpunkte)."""
        if art == "gruppe":
            return self._gruppe(breite, hoehe, daten, alt, lage, nr, x, y, hinter)
        innen = daten.get("daten") if isinstance(daten.get("daten"), dict) else {}
        verankerung = f'text:anchor-type="{"as-char" if lage is None else "paragraph"}"'
        ort = "" if lage is None else (f' svg:x="{_laenge(x)}"' if not lage.get("ah") else "") + (f' svg:y="{_laenge(y)}"' if not lage.get("av") else "")
        masse = f'svg:width="{_laenge(breite)}" svg:height="{_laenge(hoehe)}"'
        beschr = f"<svg:desc>{escape(alt)}</svg:desc>" if alt else ""
        dreh = float(daten.get("dreh", 0) or 0)
        if dreh:
            self._melden("Die Drehung von Zeichenobjekten wird in der ODT-Datei nicht gespeichert.")
        if art == "textfeld":
            rand = daten.get("rand") if isinstance(daten.get("rand"), dict) else None
            pad = innen.get("innen") if isinstance(innen.get("innen"), (list, tuple)) and len(innen["innen"]) == 4 else None
            extra = (f' fo:padding-left="{_laenge(pad[0])}" fo:padding-top="{_laenge(pad[1])}" fo:padding-right="{_laenge(pad[2])}" fo:padding-bottom="{_laenge(pad[3])}"') if pad else ""
            stil = self._grafikstil(daten.get("fuell"), rand, "", 0.0, lage, hinter, extra)
            return (f'<draw:frame draw:style-name="{stil}" draw:name="Textfeld{nr}" {verankerung}{ort} {masse}><draw:text-box>'
                    f'{self._absaetze(str(innen.get("text") or ""), innen, False)}</draw:text-box>{beschr}</draw:frame>')
        if art == "wordart":
            self._melden("WordArt wurde in der ODT-Datei als Text mit seiner Schrift gespeichert; Verlauf, Kontur, Schatten und Verformung gehen dabei verloren.")
            stil = self._grafikstil({}, None, "", 0.0, lage, hinter)
            return (f'<draw:frame draw:style-name="{stil}" draw:name="WordArt{nr}" {verankerung}{ort} {masse}><draw:text-box>'
                    f'{self._absaetze(str(innen.get("text") or ""), innen, True)}</draw:text-box>{beschr}</draw:frame>')
        # Form
        kind = str(innen.get("form") or "rechteck").casefold()
        rand = daten.get("rand") if isinstance(daten.get("rand"), dict) else None
        voll = daten.get("fuell") if "fuell" in daten else ({"art": "farbe", "farbe": innen["fuell"]} if innen.get("fuell") else {})
        offen = kind == "linie" or bool(innen.get("offen"))
        stil = self._grafikstil({} if offen else voll, rand, str(innen.get("linie") or ""), float(innen.get("strich") or 0.0), lage, hinter, "", str(innen.get("pfeil") or ""))
        text = self._absaetze(str(innen.get("text") or ""), innen, True) if str(innen.get("text") or "").strip() else "<text:p/>"
        gemeinsam = f'draw:style-name="{stil}" draw:name="Form{nr}" {verankerung}{ort}'
        if innen.get("pfad_norm"):
            d = " ".join(o[0] + (" " + " ".join(str(int(round(float(v) * 10000))) for v in o[1:]) if len(o) > 1 else "") for o in innen["pfad_norm"])
            return f'<draw:path {gemeinsam} {masse} svg:viewBox="0 0 10000 10000" svg:d="{d}">{text}{beschr}</draw:path>'
        if kind == "rechteck":
            return f'<draw:rect {gemeinsam} {masse}>{text}{beschr}</draw:rect>'
        if kind in ("ellipse", "kreis"):
            return f'<draw:ellipse {gemeinsam} {masse}>{text}{beschr}</draw:ellipse>'
        if kind == "linie":
            runter = bool(daten.get("flipV"))
            x1, y1, x2, y2 = (0.0, hoehe, breite, 0.0) if runter else (0.0, 0.0, breite, hoehe)
            versatz = (f' svg:x1="{_laenge(x + x1)}" svg:y1="{_laenge(y + y1)}" svg:x2="{_laenge(x + x2)}" svg:y2="{_laenge(y + y2)}"')
            return f'<draw:line draw:style-name="{stil}" draw:name="Linie{nr}" {verankerung}{versatz}>{beschr}</draw:line>'
        prst = innen.get("docx_geometrie") or _GEOMETRIE_UMGEKEHRT.get(kind)
        if not prst:
            self._melden(f"Die Form „{kind}“ hat in ODT keinen Namen und wurde als Rechteck geschrieben.")
            return f'<draw:rect {gemeinsam} {masse}>{text}{beschr}</draw:rect>'
        return (f'<draw:custom-shape {gemeinsam} {masse}>{text}{beschr}<draw:enhanced-geometry draw:type="ooxml-{prst}" svg:viewBox="0 0 21600 21600" '
                'draw:enhanced-path="M 0 0 L 21600 0 21600 21600 0 21600 Z N"/></draw:custom-shape>')

    def _gruppe(self, breite, hoehe, daten, alt, lage, nr, x, y, hinter) -> str:
        teile = []
        for i, e in enumerate(daten.get("elemente") or [], 1):
            if e.get("art") == "bild":
                roh = self.ressourcen.get(str(e.get("ressource") or ""))
                fmt = format_erkennen(roh) if roh else None
                if not roh or fmt not in ODT_BILDFORMATE:
                    self._melden("Ein Bild in einer Gruppe hat kein Format, das ODT übernehmen kann, und fehlt in der ODT-Datei.")
                    continue
                self.n += 1
                pfad = f"Pictures/gruppe{self.n}.{FORMATE[fmt][0]}"
                self.bilder[pfad] = roh
                teile.append(f'<draw:frame draw:name="GruppenBild{nr}_{i}" text:anchor-type="paragraph" svg:x="{_laenge(x + e["x"])}" svg:y="{_laenge(y + e["y"])}" '
                             f'svg:width="{_laenge(e["b"])}" svg:height="{_laenge(e["h"])}"><draw:image xlink:href="{pfad}" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/></draw:frame>')
                continue
            teile.append(self.element(e["art"], e["b"], e["h"], e.get("angabe") or {}, "", {"ah": "", "av": "", "bh": "spalte", "bv": "absatz"}, nr * 100 + i, x + e["x"], y + e["y"]))
        return f'<draw:g draw:name="Gruppe{nr}" text:anchor-type="{"as-char" if lage is None else "paragraph"}">{"".join(teile)}</draw:g>'
