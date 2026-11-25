"""RTF direkt in das Dokumentmodell (``core.document.Dokument``) lesen — ohne das bisherige Modell als Zwischenschritt.

Der Zerleger (``rtf/zerleger.py``) sammelt Text, Formate, Tabellen und Bildbytes ohne Qt; hier entsteht daraus das ``Dokument``: Absätze mit Ausrichtung, Einzügen,
Abständen, Seitenumbruch und Überschriftenebene, Läufe mit Schrift, Größe, fett, kursiv, unterstrichen, durchgestrichen, hoch/tief, Farbe und Hintergrund, Listen,
Tabellen (Spaltenbreiten aus den Zellgrenzen), Bilder im Text sowie Seiteneinrichtung samt Kopf- und Fußzeile. Bilder in Kopf-/Fußzeilen löst der Zerleger nicht
auf; dann gibt ``lese_rtf_dokument`` ``None`` zurück und der Aufrufer nimmt den bisherigen Weg."""
from __future__ import annotations

from lunivo_writer.kern.dokument.dokument import Abschnitt, Absatz, Dokument, FreiesObjekt, InlineObjekt, Kommentar, Lauf, Note, ListenDefinition, ListenEbene, Tabelle, Zelle, neues_dokument
from lunivo_writer.kern.dokument.formatvorlagen import eingebaute_vorlagen
from lunivo_writer.dienste.rtf.modell import Abschnittswechsel, daten_lesen as _daten_lesen, Absatz as RtfAbsatz, NichtImModell, Tabelle as RtfTabelle, Ziel
from lunivo_writer.dienste.rtf.zerleger import Zerleger
from lunivo_writer.kern.dokument.bericht import IOReport
from lunivo_writer.kern.dokument.seite import HeaderFooter

_TWIP_JE_PX = 15.0


def _hex(wert) -> str | None:
    return wert if isinstance(wert, str) and len(wert) == 7 and wert[0] == "#" else None


def _zeichenformat(z: Zerleger, roh: tuple) -> dict:
    p = dict(roh)
    f: dict = {}
    familie = z.schriften.get(p.get("f"), z.schriften.get(z.standard_schrift, "Liberation Serif"))
    if familie:
        f["schrift"] = familie
    f["groesse_pt"] = max(1.0, float(p.get("fs", 24)) / 2)
    if p.get("b"):
        f["fett"] = True
    if p.get("i"):
        f["kursiv"] = True
    if p.get("ul"):
        f["unterstrichen"] = True
    if p.get("strike"):
        f["durchgestrichen"] = True
    if p.get("va") in ("super", "sub"):
        f["hoch_tief"] = "hoch" if p["va"] == "super" else "tief"
    if p.get("umbruch"):
        f["umbruch"] = p["umbruch"]
    if p.get("caps"):
        f["grossbuchstaben"] = True
    if p.get("scaps"):
        f["kapitaelchen"] = True
    if p.get("expnd"):
        f["zeichenabstand"], f["zeichenabstand_art"] = p["expnd"], 1
    if p.get("scalex") and p["scalex"] != 100:
        f["skalierung"] = float(p["scalex"])
    if p.get("up"):
        f["versatz_pt"] = p["up"]
    if p.get("v"):
        f["versteckt"] = True
    if p.get("link"):
        f["link"] = p["link"]
    for schluessel, name in (("cf", "farbe"), ("cb", "marker")):
        index = p.get(schluessel)
        if isinstance(index, int) and 0 <= index < len(z.farben) and _hex(z.farben[index]):
            f[name] = z.farben[index]
    return f


def _absatzformat(roh: dict, z: Zerleger | None = None) -> dict:
    f: dict = {}
    sl = roh.get("sl")
    if sl:                                                              # Zeilenabstand: \\slmult1 = Vielfaches von 240stel, sonst mindestens (positiv) oder genau (negativ)
        if roh.get("slmult") == 1 and sl > 0:
            f["zeilenabstand_art"], f["zeilenabstand"] = "vielfach", sl / 240.0
        elif sl < 0:
            f["zeilenabstand_art"], f["zeilenabstand"] = "genau", -sl / _TWIP_JE_PX
        else:
            f["zeilenabstand_art"], f["zeilenabstand"] = "mindestens", sl / _TWIP_JE_PX
    if roh.get("tabs"):
        f["tabstopps"] = [[pos / _TWIP_JE_PX, art] for pos, art, _fuell in roh["tabs"]]
        fuell = next((fz for _p, _a, fz in roh["tabs"] if fz), "")
        if fuell:
            f["tabfuell"] = fuell
    if z is not None and isinstance(roh.get("cbpat"), int) and 0 <= roh["cbpat"] < len(z.farben) and _hex(z.farben[roh["cbpat"]]):
        f["hintergrund"] = z.farben[roh["cbpat"]]
    if roh.get("rahmen") and z is not None and not getattr(z, "_rahmen_gemeldet", False):
        z._rahmen_gemeldet = True
        z.report.warn("Absatzrahmen aus der RTF-Datei wurden nicht übernommen.")
    ausrichtung = {"qc": "mitte", "qr": "rechts", "qj": "block"}.get(roh.get("q"))
    if ausrichtung:
        f["ausrichtung"] = ausrichtung
    if roh.get("pagebb") or roh.get("pagebb_einmal"):
        f["seitenumbruch_vor"] = True
    if roh.get("h"):
        f["vorlage"] = f"Überschrift {max(1, min(9, int(roh['h'])))}"
    for rtf, name in (("sb", "abstand_vor"), ("sa", "abstand_nach"), ("li", "einzug_links"), ("ri", "einzug_rechts"), ("fi", "einzug_erste")):
        if roh.get(rtf):
            f[name] = float(roh[rtf]) / _TWIP_JE_PX
    return f


class _Aufbau:
    def __init__(self, z: Zerleger):
        self.z = z
        self.dok = neues_dokument(z.seite)
        self.dok.abschnitte[0].bloecke = []
        self.dok.standardformat = {"schrift": z.schriften.get(z.standard_schrift, "Liberation Serif"), "groesse_pt": 12.0}
        self.listen: dict[str, int] = {}
        self.vorlagen_noetig = False
        self.bilder = 0
        self._frei: list = []                                           # frei verankerte Formen des Absatzes in Arbeit
        self.komm_modell: dict[int, int] = {}

    def liste(self, art: str) -> int:
        if art not in self.listen:
            lid = self.dok.neue_id()
            self.dok.listen[lid] = ListenDefinition(lid, [ListenEbene("dezimal" if art == "zahl" else "disc")])
            self.listen[art] = lid
        return self.listen[art]

    _ZAHLENART = {0: "dezimal", 1: "roem_gross", 2: "roem_klein", 3: "gross", 4: "klein", 23: "disc", 255: "zeichen"}

    def _liste_ls(self, ls: int):
        """Die Liste zu ``\\lsN`` aus ``\\listtable``/``\\listoverridetable`` (Zahlenart je Ebene) als Liste des Modells; ``None`` ohne Definition."""
        schluessel = f"ls{ls}"
        if schluessel in self.listen:
            return self.listen[schluessel]
        ebenen = self.z.listen_def.get(self.z.list_ls.get(ls))
        if not ebenen:
            return None
        modell = [ListenEbene(self._ZAHLENART.get(e.get("levelnfc", e.get("levelnfcn", 0)), "dezimal"), "", max(1, int(e.get("levelstartat", 1)))) for e in ebenen[:9]]
        lid = self.dok.neue_id()
        self.dok.listen[lid] = ListenDefinition(lid, modell or [ListenEbene("dezimal")])
        self.listen[schluessel] = lid
        return lid

    def _kommentar_id(self, nr: int) -> int:
        if nr not in self.komm_modell:
            k = self.z.kommentare[nr]
            kid = self.dok.neue_id()
            self.dok.kommentare[kid] = Kommentar(kid, k["autor"], "", "", k["text"])
            self.komm_modell[nr] = kid
        return self.komm_modell[nr]

    def _bild_schluessel(self, lauf: tuple) -> str:
        """Die Bilddaten eines ``b_raw``-Laufs als Ressource des Dokuments → Schlüssel."""
        self.bilder += 1
        schluessel = f"rtf-bild-{self.bilder}"
        self.dok.ressourcen[schluessel] = lauf[1]
        return schluessel

    def _roh_schluessel(self, roh: dict) -> str:
        """Bilddaten, die kein Decoder kennt, als Ressource des Dokuments ablegen → Schlüssel (für das unveränderte Zurückschreiben)."""
        self.bilder += 1
        schluessel = f"rtf-roh-{self.bilder}"
        self.dok.ressourcen[schluessel] = roh["daten"]
        return schluessel

    def _roh_bild(self, roh: dict) -> InlineObjekt:
        """Ein Bild im Text in unbekanntem Format: ein erhaltenes Objekt (``roh``), das beim Speichern als RTF unverändert zurückkommt."""
        breite = float((roh.get("gw") or 0) / 15 or (roh.get("w") or 0) or 64.0)
        hoehe = float((roh.get("gh") or 0) / 15 or (roh.get("h") or 0) or 64.0)
        daten = {"grund": "Bild in unbekanntem RTF-Format", "rtf_roh": {"ressource": self._roh_schluessel(roh), "blip": roh.get("blip"), "gw": roh.get("gw"), "gh": roh.get("gh")}}
        return InlineObjekt(self.dok.neue_id(), "roh", breite, hoehe, "", daten, "")

    def _form(self, d: dict, inhalte: list) -> None:
        """Eine Form (``\\shp``): als Objekt im Text (Ergebnis eines ``SHAPE``-Feldes) oder als frei verankertes Objekt des Absatzes, der gerade entsteht."""
        daten, ressource = dict(d.get("daten") or {}), ""
        if d.get("bild") is not None and d["art"] == "bild":
            ressource = self._bild_schluessel(d["bild"])
        if d.get("fuellbild") is not None and isinstance(daten.get("fuell"), dict):
            daten["fuell"] = {**daten["fuell"], "n": self._bild_schluessel(d["fuellbild"])}
        if d.get("roh_bild") is not None:
            roh = d["roh_bild"]
            daten["rtf_roh"] = {"ressource": self._roh_schluessel(roh), "blip": roh.get("blip"), "gw": roh.get("gw"), "gh": roh.get("gh")}
        lage = d["lage"]
        if lage.get("imtext"):
            inhalte.append(InlineObjekt(self.dok.neue_id(), d["art"], d["breite"], d["hoehe"], ressource, daten, d.get("alt", "")))
            return
        self._frei.append(FreiesObjekt(self.dok.neue_id(), 0, d["art"], d["breite"], d["hoehe"], bezug_h=lage["bezug_h"], x=lage["x"], bezug_v=lage["bezug_v"], y=lage["y"],
                                       umbruch=lage["umbruch"], ebene=lage.get("ebene", 0), ressource=ressource, daten=daten, alt_text=d.get("alt", "")))

    def absatz(self, a: RtfAbsatz) -> Absatz:
        inhalte = []
        self._frei = []
        for lauf in a.laeufe:
            if lauf[0] == "t" and lauf[1]:
                f = _zeichenformat(self.z, lauf[2])
                nr = dict(lauf[2]).get("komm")
                if nr in self.z.kommentare:
                    f["kommentar"] = self._kommentar_id(nr)
                inhalte.append(Lauf(lauf[1], f))
            elif lauf[0] == "n":
                nid = self.dok.neue_id()
                self.dok.noten.setdefault(lauf[1], {})[nid] = Note(nid, lauf[1], lauf[2])
                inhalte.append(Lauf("?", {"note": f"{lauf[1]}:{nid}", "hoch_tief": "hoch"}))
            elif lauf[0] == "shape":
                self._form(lauf[1], inhalte)
            elif lauf[0] == "b_roh":
                inhalte.append(self._roh_bild(lauf[1]))
            elif lauf[0] == "b_raw":
                daten, (breite, hoehe), _art = lauf[1], lauf[2], lauf[3]
                self.bilder += 1
                schluessel = f"rtf-bild-{self.bilder}"
                self.dok.ressourcen[schluessel] = daten
                inhalte.append(InlineObjekt(self.dok.neue_id(), "bild", float(breite), float(hoehe), schluessel))
        format = _absatzformat(a.props, self.z)
        if format.get("vorlage"):
            self.vorlagen_noetig = True
        ls_liste = self._liste_ls(a.props.get("ls")) if a.props.get("ls") is not None else None
        absatz = Absatz(self.dok.neue_id(), inhalte, format, liste_id=ls_liste if ls_liste is not None else (self.liste(a.liste) if a.liste else None),
                        ebene=min(8, int(a.props.get("ilvl") or 0)) if ls_liste is not None else 0)
        for o in self._frei:
            o.anker = absatz.id
            self.dok.objekte[o.id] = o
        self._frei = []
        if inhalte and isinstance(inhalte[0], Lauf):
            absatz.zeichenformat = dict(inhalte[0].format)
        return absatz

    def tabelle(self, t: RtfTabelle) -> Tabelle:
        spalten = max((len(zellen) for zellen, _g in t.zeilen), default=1)
        zeilen = []
        for zellen, _grenzen in t.zeilen:
            reihe = [Zelle([self.absatz(a) for a in absaetze] or [Absatz(self.dok.neue_id())]) for absaetze in zellen]
            while len(reihe) < spalten:
                reihe.append(Zelle([Absatz(self.dok.neue_id())]))
            zeilen.append(reihe)
        breiten = [0.0] * spalten
        grenzen = t.zeilen[0][1] if t.zeilen else []
        if len(grenzen) == spalten:
            vorher = 0
            for i, g in enumerate(grenzen):
                breiten[i] = max(0.0, (g - vorher) / _TWIP_JE_PX)
                vorher = g
        self._verbunden(zeilen, t.merken)
        for r, zeile in enumerate(zeilen):                              # Zellschattierung (\\clcbpat)
            bgs = t.hintergruende[r] if r < len(t.hintergruende) else []
            for c, zelle in enumerate(zeile):
                idx = bgs[c] if c < len(bgs) else None
                if isinstance(idx, int) and 0 <= idx < len(self.z.farben) and _hex(self.z.farben[idx]) and zelle.verdeckt_von is None:
                    zelle.format = {**(zelle.format or {}), "hintergrund": self.z.farben[idx]}
        return Tabelle(self.dok.neue_id(), zeilen, breiten, [0.0] * len(zeilen), {"rahmen_breite": 1.0, "rahmen_farbe": "#000000"})

    def _verbunden(self, zeilen: list, merken: list) -> None:
        """Verbundene Zellen (\\clmgf/\\clmrg waagerecht, \\clvmgf/\\clvmrg senkrecht): die erste Zelle spannt, die übrigen sind verdeckt."""
        for r, zeile in enumerate(zeilen):
            marken = merken[r] if r < len(merken) else []
            for c, zelle in enumerate(zeile):
                m = marken[c] if c < len(marken) else set()
                if "clmgf" in m:
                    n = 1
                    while c + n < len(zeile) and c + n < len(marken) and "clmrg" in marken[c + n]:
                        zeile[c + n] = Zelle([Absatz(self.dok.neue_id())], {}, 1, 1, (r, c))
                        n += 1
                    zelle.spaltenspanne = n
                if "clvmgf" in m:
                    n = 1
                    while r + n < len(zeilen) and c < len(zeilen[r + n]) and r + n < len(merken) and c < len(merken[r + n]) and "clvmrg" in merken[r + n][c]:
                        zeilen[r + n][c] = Zelle([Absatz(self.dok.neue_id())], {}, 1, 1, (r, c))
                        n += 1
                    zelle.zeilenspanne = n

    def abschnitte(self, ziel: Ziel) -> list[list]:
        """Blöcke je Abschnitt: der Haupttext wird an jedem ``\\sect`` geteilt; ein leerer Rest am Ende zählt nicht als eigener Abschnitt."""
        gruppen: list[list] = [[]]
        for teil in ziel.teile:
            if isinstance(teil, Abschnittswechsel):
                gruppen.append([])
            else:
                gruppen[-1].append(teil)
        while len(gruppen) > 1 and not gruppen[-1]:
            gruppen.pop()
        return [self.bloecke_aus(g) for g in gruppen]

    def bloecke(self, ziel: Ziel) -> list:
        return self.bloecke_aus(ziel.teile)

    def bloecke_aus(self, teile: list) -> list:
        aus: list = []
        for teil in teile:
            if isinstance(teil, RtfAbsatz):
                aus.append(self.absatz(teil))
            elif isinstance(teil, RtfTabelle):
                aus.append(self.tabelle(teil))
            else:
                raise NichtImModell(f"Unbekannter RTF-Block: {type(teil).__name__}")
        # vor jeder Tabelle und am Ende steht ein Absatz
        ordnung: list = []
        for b in aus:
            if isinstance(b, Tabelle) and (not ordnung or isinstance(ordnung[-1], Tabelle)):
                ordnung.append(Absatz(self.dok.neue_id()))
            ordnung.append(b)
        if not ordnung or isinstance(ordnung[-1], Tabelle):
            ordnung.append(Absatz(self.dok.neue_id()))
        return ordnung


_KF_ORT = {"header": "kopf", "footer": "fuss", "first_header": "kopf1", "first_footer": "fuss1"}


def _kopf_fuss_bilder(ziel: Ziel, key: str, page, report) -> list:
    """Bilder in Kopf- und Fußzeilen als Seitenbilder (``PageSettings.bilder``, wie bei DOCX und ODT); Formen und andere Objekte dort stehen im Bericht."""
    ort = _KF_ORT.get(key)
    bilder = []
    laeufe = [lauf for a in ziel.teile if isinstance(a, RtfAbsatz) for lauf in a.laeufe] + list(ziel.laeufe)
    for lauf in laeufe:
        if lauf[0] == "b_raw" and ort:
            daten, (bw, bh) = lauf[1], lauf[2]
            yv = page.kopf_abstand_mm * 96 / 25.4 if ort.startswith("kopf") else max(0.0, (page.height_mm - page.fuss_abstand_mm) * 96 / 25.4 - float(bh))
            bilder.append({"ort": ort, "bild": daten, "b": float(bw), "h": float(bh), "bh": "rand", "bv": "seite", "ah": "left", "av": "", "xh": 0.0, "yv": yv})
        elif lauf[0] in ("shape", "b_roh"):
            report.warn("Eine Form oder ein Bild in unbekanntem Format in einer Kopf- oder Fußzeile der RTF-Datei wurde nicht übernommen.")
    return bilder


def _kopf_fuss(ziel: Ziel) -> HeaderFooter:
    absatzteile = [t for t in ziel.teile if isinstance(t, RtfAbsatz)]
    if ziel.laeufe:
        absatzteile.append(RtfAbsatz({}, ziel.laeufe, None))
    text = "\n".join("".join(lauf[1] for lauf in a.laeufe if lauf[0] == "t").replace(" ", "\n") for a in absatzteile).strip("\n")
    ausrichtung = {"qc": "center", "qr": "right", "qj": "justify"}.get(absatzteile[0].props.get("q", "") if absatzteile else "", "left")
    return HeaderFooter(text, ausrichtung)


def lese_rtf_dokument(path: str):
    """RTF → ``(Dokument, PageSettings, meta, IOReport)``; ``None``, wenn der Zerleger etwas nicht ohne Qt auflösen kann."""
    z = Zerleger(_daten_lesen(path), modell=True)
    try:
        z.run()
    except NichtImModell:
        return None
    aufbau = _Aufbau(z)
    page = z.seite
    try:
        gruppen = aufbau.abschnitte(z.haupt)
        aufbau.dok.abschnitte[0].bloecke = gruppen[0]
        for key, (ziel, _props) in z.kopf_fuss.items():
            if "?" in key:
                basis = key.split("?", 1)[0]
                if basis in z.kopf_fuss:
                    continue
                key = basis
            setattr(page, key, _kopf_fuss(ziel))
            page.bilder.extend(_kopf_fuss_bilder(ziel, key, page, z.report))
    except NichtImModell:
        return None
    page.diff_first = z.titel_erste
    if not z.titel_erste:
        page.first_header, page.first_footer = HeaderFooter(), HeaderFooter()
    dok = aufbau.dok
    import copy
    infos = z.sek_liste                                               # Eigenschaften je Abschnitt (\\sectd, \\pgwsxn, \\marglsxn …, \\sbk…); gelten nur für ihren Abschnitt

    def seite_von(i: int):
        s = copy.copy(page) if i else page
        for k, v in (infos[i] if i < len(infos) else {}).items():
            if k != "beginn":
                setattr(s, k, v)
        return s
    dok.abschnitte[0].seite = seite_von(0)
    for i, rest in enumerate(gruppen[1:], 1):
        info = infos[i] if i < len(infos) else {}
        dok.abschnitte.append(Abschnitt(dok.neue_id(), rest, seite_von(i), info.get("beginn", "naechste")))
    if aufbau.vorlagen_noetig:
        dok.vorlagen.update(eingebaute_vorlagen())
    meta = dict(z.meta)
    for k, v in meta.items():
        if isinstance(v, (str, int, float, bool)):
            dok.eigenschaften[k] = v
    return dok, page, meta, z.report if z.report is not None else IOReport()
