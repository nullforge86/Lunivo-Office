"""RTF direkt in das Dokumentmodell (``core.document.Dokument``) lesen — ohne das bisherige Modell als Zwischenschritt.

Der Zerleger (``rtf/zerleger.py``) sammelt Text, Formate, Tabellen und Bildbytes ohne Qt; hier entsteht daraus das ``Dokument``: Absätze mit Ausrichtung, Einzügen,
Abständen, Seitenumbruch und Überschriftenebene, Läufe mit Schrift, Größe, fett, kursiv, unterstrichen, durchgestrichen, hoch/tief, Farbe und Hintergrund, Listen,
Tabellen (Spaltenbreiten aus den Zellgrenzen), Bilder im Text sowie Seiteneinrichtung samt Kopf- und Fußzeile. Bilder in Kopf-/Fußzeilen löst der Zerleger nicht
auf; dann gibt ``lese_rtf_dokument`` ``None`` zurück und der Aufrufer nimmt den bisherigen Weg."""
from __future__ import annotations

from lunivo_writer.core.document.dokument import Absatz, Dokument, InlineObjekt, Lauf, ListenDefinition, ListenEbene, Tabelle, Zelle, neues_dokument
from lunivo_writer.core.document.formatvorlagen import eingebaute_vorlagen
from lunivo_writer.dienste.rtf.leser import _daten_lesen
from lunivo_writer.dienste.rtf.modell import Absatz as RtfAbsatz, NichtImModell, Tabelle as RtfTabelle, Ziel
from lunivo_writer.dienste.rtf.zerleger import Zerleger
from lunivo_writer.modelle.bericht import IOReport
from lunivo_writer.modelle.seite import HeaderFooter

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
    for schluessel, name in (("cf", "farbe"), ("cb", "marker")):
        index = p.get(schluessel)
        if isinstance(index, int) and 0 <= index < len(z.farben) and _hex(z.farben[index]):
            f[name] = z.farben[index]
    return f


def _absatzformat(roh: dict) -> dict:
    f: dict = {}
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

    def liste(self, art: str) -> int:
        if art not in self.listen:
            lid = self.dok.neue_id()
            self.dok.listen[lid] = ListenDefinition(lid, [ListenEbene("dezimal" if art == "zahl" else "disc")])
            self.listen[art] = lid
        return self.listen[art]

    def absatz(self, a: RtfAbsatz) -> Absatz:
        inhalte = []
        for lauf in a.laeufe:
            if lauf[0] == "t" and lauf[1]:
                inhalte.append(Lauf(lauf[1], _zeichenformat(self.z, lauf[2])))
            elif lauf[0] == "b_raw":
                daten, (breite, hoehe), _art = lauf[1], lauf[2], lauf[3]
                self.bilder += 1
                schluessel = f"rtf-bild-{self.bilder}"
                self.dok.ressourcen[schluessel] = daten
                inhalte.append(InlineObjekt(self.dok.neue_id(), "bild", float(breite), float(hoehe), schluessel))
        format = _absatzformat(a.props)
        if format.get("vorlage"):
            self.vorlagen_noetig = True
        absatz = Absatz(self.dok.neue_id(), inhalte, format, liste_id=self.liste(a.liste) if a.liste else None)
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
        return Tabelle(self.dok.neue_id(), zeilen, breiten, [0.0] * len(zeilen), {"rahmen_breite": 1.0, "rahmen_farbe": "#000000"})

    def bloecke(self, ziel: Ziel) -> list:
        aus: list = []
        for teil in ziel.teile:
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


def _kopf_fuss(ziel: Ziel) -> HeaderFooter:
    if any(lauf[0] != "t" for a in ziel.teile if isinstance(a, RtfAbsatz) for lauf in a.laeufe) or any(lauf[0] != "t" for lauf in ziel.laeufe):
        raise NichtImModell("Bilder in RTF-Kopf- oder Fußzeilen")
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
        aufbau.dok.abschnitte[0].bloecke = aufbau.bloecke(z.haupt)
        for key, (ziel, _props) in z.kopf_fuss.items():
            if "?" in key:
                basis = key.split("?", 1)[0]
                if basis in z.kopf_fuss:
                    continue
                key = basis
            setattr(page, key, _kopf_fuss(ziel))
    except NichtImModell:
        return None
    page.diff_first = z.titel_erste
    if not z.titel_erste:
        page.first_header, page.first_footer = HeaderFooter(), HeaderFooter()
    dok = aufbau.dok
    dok.abschnitte[0].seite = page
    if aufbau.vorlagen_noetig:
        dok.vorlagen.update(eingebaute_vorlagen())
    meta = dict(z.meta)
    for k, v in meta.items():
        if isinstance(v, (str, int, float, bool)):
            dok.eigenschaften[k] = v
    return dok, page, meta, z.report if z.report is not None else IOReport()
