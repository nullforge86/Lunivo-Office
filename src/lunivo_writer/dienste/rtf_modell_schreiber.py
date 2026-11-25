"""RTF direkt aus dem Dokumentmodell (``core.document.Dokument``) schreiben, ohne ``QTextDocument`` und ohne Umwandlung ins bisherige Modell.

Absätze (Ausrichtung, Einzüge, Abstände, Seitenumbruch, Überschriftenebene), Zeichenformat (Schrift, Größe, fett, kursiv, unterstrichen, durchgestrichen,
hoch/tief, Farbe, Hintergrund), Listen (Aufzählungszeichen und Nummern), Tabellen mit verbundenen Zellen, Bilder im Text (JPEG, EMF, WMF und PNG bleiben
Original; anderes wird PNG), Seitengröße, Seitenränder, Kopf- und Fußzeile. Seiteneinrichtung, Kopf-/Fußzeile und Tabellen der Datei baut die gemeinsame Basis in
``rtf_basis`` (nur ``PageSettings``, ohne Qt). Maße im Modell sind Bildpunkte (96 dpi): 1 px = 15 Twip."""
from __future__ import annotations

from lunivo_writer.core.document.bildformat import format_erkennen
from lunivo_writer.core.document.dokument import Absatz, Dokument, InlineObjekt, Rahmen, Tabelle
from lunivo_writer.core.document.formatvorlagen import ueberschriftsebene
from lunivo_writer.core.document.listen import listenmarken
from lunivo_writer.core.document.bildformat import masse
from lunivo_writer.dienste.rtf.formen_schreiben import shape_rtf
from lunivo_writer.dienste.rtf_basis import RtfBasis, _px, _text, verluste_melden
from lunivo_writer.modelle.bericht import IOReport

_AUSRICHTUNG = {"mitte": r"\qc", "rechts": r"\qr", "block": r"\qj"}
_PUNKTE = {"scheibe": "•", "kreis": "◦", "quadrat": "▪", "disc": "•", "circle": "◦", "square": "▪"}
_AUFZAEHLUNG = "•◦▪"


class _RtfModell(RtfBasis):
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

    def _roh_pict(self, r: dict) -> str:
        """Ein beim Lesen aufbewahrtes Bild in unbekanntem RTF-Format unverändert als ``\\pict`` zurückschreiben."""
        daten = self.dok.ressourcen.get(str(r.get("ressource") or ""))
        if not daten:
            self._warn("Ein aufbewahrtes Bild in unbekanntem Format fehlt im Dokument und konnte nicht in die RTF-Datei geschrieben werden.")
            return ""
        maße = (f"\\picwgoal{int(r['gw'])}" if r.get("gw") else "") + (f"\\pichgoal{int(r['gh'])}" if r.get("gh") else "")
        return f"{{\\pict\\{r.get('blip') or 'pngblip'}{maße}\n" + bytes(daten).hex() + "}"

    def bild_modell(self, x: InlineObjekt) -> str:
        if x.art == "roh" and x.daten.get("rtf_roh"):
            return self._roh_pict(x.daten["rtf_roh"])
        if x.art == "roh":
            self._warn(f"Ein Objekt ({x.daten.get('grund', 'unbekannte Art')}) lässt sich nur in DOCX erhalten und fehlt in der RTF-Datei.")
            return ""
        roh = self.dok.ressourcen.get(x.ressource)
        if not roh:
            self._warn("Ein Bild war nicht lesbar und fehlt in der RTF-Datei.")
            return ""
        art = format_erkennen(roh)
        pb = ph = 0
        if art not in ("png", "jpeg", "emf", "wmf"):                                    # andere Bildformate lassen sich ohne Qt nicht umwandeln
            self._warn(f"Ein Bild im Format {(art or 'unbekannt').upper()} wird in RTF nicht gespeichert (RTF kennt nur PNG, JPEG, EMF und WMF).")
            return ""
        if art in ("png", "jpeg"):
            groesse = masse(roh)
            pb, ph = (round(groesse[0]), round(groesse[1])) if groesse else (0, 0)
        if art == "wmf":
            roh = roh[22:] if roh[:4] == b"\xd7\xcd\xc6\x9a" else roh               # Platzhalterkopf
        blip = {"png": "pngblip", "jpeg": "jpegblip", "emf": "emfblip", "wmf": "wmetafile8"}[art]
        if art in ("emf", "wmf"):
            pb, ph = round(x.breite * 26.4583), round(x.hoehe * 26.4583)            # Metafile: 0,01 mm
        return (f"{{\\pict\\{blip}\\picw{pb}\\pich{ph}\\picwgoal{_px(x.breite)}\\pichgoal{_px(x.hoehe)}\n" + roh.hex() + "}")

    # ---- Formen ----
    _FORMARTEN = ("form", "textfeld", "wordart", "gruppe")

    def _form_schreiben(self, art: str, breite: float, hoehe: float, daten: dict, lage: dict, ressource: str = "", ebene: int = 0) -> str:
        """Eine Form, ein Textfeld, WordArt-Text, einen Bildrahmen oder eine Gruppe (in ihren Teilen) als RTF-Form."""
        if art == "gruppe":
            teile = []
            for e in daten.get("elemente") or []:
                teillage = {**lage, "x": float(lage.get("x") or 0.0) + e["x"], "y": float(lage.get("y") or 0.0) + e["y"]}
                if e["art"] == "bild":
                    teile.append(self._form_schreiben("bild", e["b"], e["h"], {}, teillage, e.get("ressource", ""), ebene))
                else:
                    teile.append(self._form_schreiben(e["art"], e["b"], e["h"], e.get("angabe") or {}, teillage, "", ebene))
            return "".join(teile)
        pict = ""
        if art == "bild":
            pict = self.bild_modell(InlineObjekt(0, "bild", breite, hoehe, ressource))
            if not pict:
                return ""
        roh = daten.get("rtf_roh")
        return shape_rtf(art, breite, hoehe, daten, lage, self._warn, ebene, pict, self._roh_pict(roh) if isinstance(roh, dict) else "")

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
        kopf = "".join(teile)
        out = [kopf + " " + praefix]
        self._inline_x, hoechste = 0.0, 0.0
        offen = None                                                              # Id des gerade offenen Kommentarbereichs
        for x in a.inhalte:
            kid = x.format.get("kommentar") if not isinstance(x, InlineObjekt) else None
            if kid != offen:
                if offen is not None:
                    out.append(self._kommentar_ende(offen))
                offen = kid if kid is not None and int(kid) in self.dok.kommentare else None
                if offen is not None:
                    out.append(f"{{\\*\\atrfstart {int(offen)}}}")
            if isinstance(x, InlineObjekt) and x.art in self._FORMARTEN and not self.dok.ressourcen.get(x.ressource):
                out.append(self._form_schreiben(x.art, x.breite, x.hoehe, x.daten, {"bezug_h": "spalte", "bezug_v": "absatz", "x": self._inline_x, "y": 0.0, "umbruch": "oben_unten"}))
                self._inline_x += x.breite + 8.0                                  # RTF kennt keine Formen im Text: sie stehen nebeneinander am Absatz, der Text fließt darunter
                hoechste = max(hoechste, x.hoehe)
            elif isinstance(x, InlineObjekt):
                out.append(self.zeichen_modell(x.format) + self.bild_modell(x))
            elif x.format.get("note") and self._note_modell(str(x.format["note"])):
                out.append(self._note_modell(str(x.format["note"])))
            elif x.format.get("umbruch") in ("seite", "spalte"):                      # Umbruch mitten im Absatz
                out.append("\\page " if x.format["umbruch"] == "seite" else "\\column ")
            elif x.text:
                out.append("{" + self.zeichen_modell(x.format) + _text(x.text.replace("￼", "")) + "}")
        if offen is not None:
            out.append(self._kommentar_ende(offen))
        if hoechste:                                                                 # der folgende Absatz beginnt unter den Formen dieses Absatzes
            out[0] = kopf + f"\\sa{round((hoechste + 6.0) * 15)}" + " " + praefix
        for o in self.dok.objekte.values():                                          # frei verankerte Objekte des Absatzes
            if o.anker == a.id:
                out.append(self._form_schreiben(o.art, o.breite, o.hoehe, o.daten, {"bezug_h": o.bezug_h, "bezug_v": o.bezug_v, "x": o.x, "y": o.y, "umbruch": o.umbruch},
                                                o.ressource if o.art == "bild" else "", o.ebene))
        return "".join(out)

    def _note_modell(self, marke: str) -> str:
        """Fuß-/Endnote: Verweiszeichen mit der Note als Unterziel; leer, wenn die Note im Modell fehlt."""
        art, _, nummer = marke.partition(":")
        n = self.dok.noten.get(art, {}).get(int(nummer)) if art in ("f", "e") and nummer.isdigit() else None
        if n is None:
            return ""
        return ("{\\super\\chftn {\\footnote" + ("\\ftnalt" if art == "e" else "") + " \\pard\\plain {\\super\\chftn } " + _text(n.text) + "}}")

    def _kommentar_ende(self, kid) -> str:
        k = self.dok.kommentare[int(kid)]
        return (f"{{\\*\\atrfend {int(kid)}}}{{\\super {{\\*\\atnid {_text(k.initialen or '')}}}{{\\*\\atnauthor {_text(k.autor or '')}}}\\chatn"
                f"{{\\*\\annotation{{\\*\\atnref {int(kid)}}}\\pard\\plain \\chatn  {_text(k.text or '')}}}}}")

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
        for nr, ab in enumerate(self.dok.abschnitte):
            if nr:
                teile.append(("ABSCHNITT", ""))                          # Abschnittsende (\\sect) statt Absatzende
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
                koerper.append((r"\sect\sectd" if teile[i + 1][0] == "ABSCHNITT" else r"\par") + "\n")
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
    w = _RtfModell(dok, page)
    daten = w.run_modell()
    verluste_melden(w.report, page, "RTF")
    if len(dok.abschnitte) > 1:
        w.report.warn("In RTF gilt die Seiteneinrichtung des ersten Abschnitts für das ganze Dokument.")
    return daten, w.report
