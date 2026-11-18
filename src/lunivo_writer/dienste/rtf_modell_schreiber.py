"""RTF direkt aus dem Dokumentmodell (``core.document.Dokument``) schreiben, ohne ``QTextDocument`` und ohne Umwandlung ins bisherige Modell.

Absätze (Ausrichtung, Einzüge, Abstände, Seitenumbruch, Überschriftenebene), Zeichenformat (Schrift, Größe, fett, kursiv, unterstrichen, durchgestrichen,
hoch/tief, Farbe, Hintergrund), Listen (Aufzählungszeichen und Nummern), Tabellen mit verbundenen Zellen, Bilder im Text (JPEG, EMF, WMF und PNG bleiben
Original; anderes wird PNG), Seitengröße, Seitenränder, Kopf- und Fußzeile. Seiteneinrichtung, Kopf-/Fußzeile und Tabellen der Datei baut die gemeinsame Basis in
``rtf_schreiber`` (nur ``PageSettings``, nichts von Qt-Dokumenten). Maße im Modell sind Bildpunkte (96 dpi): 1 px = 15 Twip."""
from __future__ import annotations

from lunivo_writer.core.document.bildformat import format_erkennen
from lunivo_writer.core.document.dokument import Absatz, Dokument, InlineObjekt, Rahmen, Tabelle
from lunivo_writer.core.document.formatvorlagen import ueberschriftsebene
from lunivo_writer.core.document.listen import listenmarken
from lunivo_writer.dienste.rtf_schreiber import _Rtf, _px, _text
from lunivo_writer.modelle.bericht import IOReport

_AUSRICHTUNG = {"mitte": r"\qc", "rechts": r"\qr", "block": r"\qj"}
_PUNKTE = {"scheibe": "•", "kreis": "◦", "quadrat": "▪", "disc": "•", "circle": "◦", "square": "▪"}
_AUFZAEHLUNG = "•◦▪"


class _RtfModell(_Rtf):
    def __init__(self, dok: Dokument, page):
        self.dok, self.page = dok, page
        self.schriften: list[str] = []
        self.farben: list[str] = []
        self.report = IOReport()
        self._gemeldet: set[str] = set()
        self.marken = listenmarken(dok)

    def farbe_hex(self, hexwert: str) -> int:
        n = hexwert.lower()
        if n not in self.farben:
            self.farben.append(n)
        return self.farben.index(n) + 1                   # Eintrag 0 ist „Automatisch“

    # ---- Zeichen ----
    def zeichen_modell(self, f: dict) -> str:
        teile = [r"\plain"]
        name = f.get("schrift")
        if isinstance(name, (list, tuple)):
            name = name[0] if name else None
        name = name or self.dok.standardformat.get("schrift") or "Liberation Sans"
        teile.append(f"\\f{self.schrift(str(name))}")
        groesse = f.get("groesse_pt") or self.dok.standardformat.get("groesse_pt") or 11
        teile.append(f"\\fs{round(float(groesse) * 2)}")
        if f.get("fett") or (f.get("gewicht") or 0) >= 600:
            teile.append(r"\b")
        if f.get("kursiv"):
            teile.append(r"\i")
        if f.get("unterstrichen"):
            teile.append(r"\ul")
        if f.get("durchgestrichen") or f.get("doppelt_durch"):
            teile.append(r"\strike")
        if f.get("hoch_tief") == "hoch":
            teile.append(r"\super")
        elif f.get("hoch_tief") == "tief":
            teile.append(r"\sub")
        if f.get("farbe"):
            teile.append(f"\\cf{self.farbe_hex(f['farbe'])}")
        if f.get("marker"):
            teile.append(f"\\chcbpat{self.farbe_hex(f['marker'])}")
        return "".join(teile) + " "

    def bild_modell(self, x: InlineObjekt) -> str:
        roh = self.dok.ressourcen.get(x.ressource)
        if not roh:
            self._warn("Ein Bild war nicht lesbar und fehlt in der RTF-Datei.")
            return ""
        art = format_erkennen(roh)
        pb = ph = 0
        if art == "svg":
            from lunivo_writer.editor.objekte import bilddaten as BD
            roh, art = BD.png_bytes(BD.svg_raster(roh, max(1, round(x.breite)))), "png"
        elif art not in ("png", "jpeg", "emf", "wmf"):
            from PySide6.QtCore import QBuffer, QIODevice
            from PySide6.QtGui import QImage
            img = QImage.fromData(roh)
            if img.isNull():
                self._warn("Ein Bild war nicht lesbar und fehlt in der RTF-Datei.")
                return ""
            puffer = QBuffer()
            puffer.open(QIODevice.WriteOnly)
            img.save(puffer, "PNG")
            roh, art = bytes(puffer.data()), "png"
        if art == "png" or art == "jpeg":
            from PySide6.QtGui import QImage
            img = QImage.fromData(roh)
            pb, ph = img.width(), img.height()
        if art == "wmf":
            roh = roh[22:] if roh[:4] == b"\xd7\xcd\xc6\x9a" else roh               # Platzhalterkopf
        blip = {"png": "pngblip", "jpeg": "jpegblip", "emf": "emfblip", "wmf": "wmetafile8"}[art]
        if art in ("emf", "wmf"):
            pb, ph = round(x.breite * 26.4583), round(x.hoehe * 26.4583)            # Metafile: 0,01 mm
        return (f"{{\\pict\\{blip}\\picw{pb}\\pich{ph}\\picwgoal{_px(x.breite)}\\pichgoal{_px(x.hoehe)}\n" + roh.hex() + "}")

    # ---- Absätze ----
    def _listen_praefix_modell(self, a: Absatz) -> tuple[float, str]:
        text = self.marken.get(a.id, "")
        definition = self.dok.listen.get(a.liste_id)
        ebene = definition.ebenen[min(max(a.ebene, 0), len(definition.ebenen) - 1)] if definition and definition.ebenen else None
        if text in _AUFZAEHLUNG or (ebene is not None and ebene.stil in _PUNKTE):
            zeichen = text if text in _AUFZAEHLUNG else _PUNKTE.get(ebene.stil, "•")
            art = r"\pnlvlblt{\pntxtb " + _text(zeichen) + "}"
        else:
            zeichen = text or "1."
            art = r"\pnlvlbody\pndec\pnstart1{\pntxta .}"
        return 36.0 * (a.ebene + 1), "{\\pntext " + _text(zeichen) + r"\tab}{\*\pn" + art + "}"

    def absatz_modell(self, a: Absatz, in_tabelle: bool = False) -> str:
        f = a.format
        teile = [r"\pard\plain"]
        if in_tabelle:
            teile.append(r"\intbl")
        teile.append(_AUSRICHTUNG.get(f.get("ausrichtung", ""), r"\ql"))
        links = float(f.get("einzug_links") or 0.0)
        praefix = ""
        if a.liste_id is not None and a.liste_id in self.dok.listen:
            mehr, praefix = self._listen_praefix_modell(a)
            links += mehr
            teile.append(f"\\fi-{_px(22.0)}")
        elif f.get("einzug_erste"):
            teile.append(f"\\fi{_px(f['einzug_erste'])}")
        if links:
            teile.append(f"\\li{_px(links)}")
        if f.get("einzug_rechts"):
            teile.append(f"\\ri{_px(f['einzug_rechts'])}")
        if f.get("abstand_vor"):
            teile.append(f"\\sb{_px(f['abstand_vor'])}")
        if f.get("abstand_nach"):
            teile.append(f"\\sa{_px(f['abstand_nach'])}")
        if f.get("seitenumbruch_vor"):
            teile.append(r"\pagebb")
        stufe = ueberschriftsebene(self.dok, a)
        if 1 <= stufe <= 9:
            teile.append(f"\\s{stufe}\\outlinelevel{stufe - 1}")
        out = ["".join(teile) + " " + praefix]
        for x in a.inhalte:
            if isinstance(x, InlineObjekt):
                out.append(self.zeichen_modell(x.format) + self.bild_modell(x))
            elif x.text:
                out.append("{" + self.zeichen_modell(x.format) + _text(x.text.replace("￼", "")) + "}")
        return "".join(out)

    # ---- Tabellen ----
    def _zeilenkopf_modell(self, t: Tabelle, r: int, breite: int) -> str:
        kopf = [r"\trowd\trgaph108"]
        spalten = len(t.zellen[r])
        gesamt = sum(t.spaltenbreiten) if t.spaltenbreiten and sum(t.spaltenbreiten) > 0 else 0.0
        rechts = 0.0
        for c, z in enumerate(t.zellen[r]):
            if z.verdeckt_von is not None:
                z0, s0 = z.verdeckt_von
                kopf.append((r"\clmrg" if s0 < c else "") + (r"\clvmrg" if z0 < r else ""))
            else:
                kopf.append((r"\clmgf" if z.spaltenspanne > 1 else "") + (r"\clvmgf" if z.zeilenspanne > 1 else ""))
            rechts = breite * (sum(t.spaltenbreiten[:c + 1]) / gesamt) if gesamt else breite * (c + 1) / spalten
            kopf.append(r"\clbrdrt\brdrs\clbrdrl\brdrs\clbrdrb\brdrs\clbrdrr\brdrs" + f"\\cellx{round(rechts)}")
        return "".join(kopf)

    def _zelle_modell(self, z) -> str:
        absaetze = []
        for b in z.bloecke:
            if isinstance(b, Absatz):
                absaetze.append(self.absatz_modell(b, True))
            else:
                self._warn("Verschachtelte Tabellen werden in RTF als Text in der Zelle gespeichert.")
                absaetze.extend(self.absatz_modell(a, True) for a in _absaetze(b))
        return r"\par ".join(absaetze) + r"\cell "

    def tabelle_modell(self, t: Tabelle) -> str:
        p = self.page
        breite = round(max(0.0, p.width_mm - p.margin_left_mm - p.margin_right_mm) * 1440 / 25.4)
        out = []
        for r, zeile in enumerate(t.zellen):
            out.append(self._zeilenkopf_modell(t, r, breite))
            for z in zeile:
                out.append(r"\pard\intbl\cell " if z.verdeckt_von is not None else self._zelle_modell(z))
            out.append(r"\row ")
        return "\n".join(out)

    def run_modell(self) -> bytes:
        teile = []
        for ab in self.dok.abschnitte:
            for b in ab.bloecke:
                if isinstance(b, Tabelle):
                    teile.append(("TABELLE", self.tabelle_modell(b)))
                elif isinstance(b, Rahmen):
                    teile.extend(("ABSATZ", self.absatz_modell(a)) for a in _absaetze(b))
                else:
                    teile.append(("ABSATZ", self.absatz_modell(b)))
        koerper = []
        for i, (art, inhalt) in enumerate(teile):
            koerper.append(inhalt)
            if art == "ABSATZ" and i != len(teile) - 1:
                koerper.append(r"\par" + "\n")
        seite, kopf = self._kopf_rtf(self._seite_rtf())
        schriften, farben, stile = self._tabellen_rtf()
        text = (r"{\rtf1\ansi\ansicpg1252\uc1\deff0" + "\n"
                + "{\\fonttbl" + schriften + "}\n{\\colortbl" + farben + "}\n{\\stylesheet{\\s0 Normal;}" + stile + "}\n"
                + "{\\*\\generator Lunivo Writer;}" + seite + "\n" + kopf + "".join(koerper) + "\n}")
        return text.encode("ascii")


def _absaetze(block):
    from lunivo_writer.core.document.dokument import absaetze_in
    return list(absaetze_in([block]))


def rtf_modell_daten(dok: Dokument, page, meta: dict | None = None) -> tuple[bytes, IOReport]:
    """Baut die RTF-Datei im Speicher. → (Inhalt, Bericht über nicht Übernommenes)."""
    from lunivo_writer.dienste.odt_schreiber import _verluste_melden
    w = _RtfModell(dok, page)
    daten = w.run_modell()
    _verluste_melden(w.report, page, meta or {}, "RTF")
    if dok.objekte:
        w.report.warn("Frei positionierte Bilder werden in RTF nicht gespeichert (in DOCX und ODT schon).")
    if len(dok.abschnitte) > 1:
        w.report.warn("In RTF gilt die Seiteneinrichtung des ersten Abschnitts für das ganze Dokument.")
    return daten, w.report
