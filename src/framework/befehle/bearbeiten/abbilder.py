"""Abbilder des Dokuments für die Bedienung: unveränderliche Beschreibungen von Absatz, Tabelle, Zelle, Objekt und Liste sowie Abfragen über das
ganze Dokument – alles anhand der Kennung. Die Abbilder tragen dieselben Feldnamen wie das Dokumentmodell, sind aber Kopien: Wer sie ändert,
ändert das Dokument nicht."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from framework.anbindung import Daten, fest
from framework.sitzungen import sitzung as _steuerung

Stelle = tuple[int, int]


@dataclass(frozen=True)
class Absatzabbild:
    id: int
    format: Mapping[str, Daten]
    zeichenformat: Mapping[str, Daten]
    liste_id: int | None
    ebene: int
    laenge: int
    inhalt: str

    def text(self) -> str:
        return self.inhalt


@dataclass(frozen=True)
class Zellabbild:
    absatz_ids: tuple[int, ...]              # Ids der Absätze direkt in der Zelle
    format: Mapping[str, Daten]
    zeilenspanne: int
    spaltenspanne: int
    verdeckt_von: tuple[int, int] | None
    text: str = ""                           # der Text der Absätze direkt in der Zelle, durch Zeilenwechsel getrennt


@dataclass(frozen=True)
class Tabellenabbild:
    id: int
    zellen: tuple[tuple[Zellabbild, ...], ...]
    spaltenbreiten: tuple[float, ...]
    zeilenhoehen: tuple[float, ...]
    format: Mapping[str, Daten]

    @property
    def zeilen(self) -> int:
        return len(self.zellen)

    @property
    def spalten(self) -> int:
        return len(self.zellen[0]) if self.zellen else 0

    def anker(self, zeile: int, spalte: int) -> tuple[int, int]:
        """Die Gitterstelle der sichtbaren Zelle, zu der (zeile, spalte) gehört."""
        return self.zellen[zeile][spalte].verdeckt_von or (zeile, spalte)

    def zelle(self, zeile: int, spalte: int) -> Zellabbild:
        """Die sichtbare Zelle, zu der (zeile, spalte) gehört."""
        z, s = self.anker(zeile, spalte)
        return self.zellen[z][s]


@dataclass(frozen=True)
class Objektabbild:
    """Ein Objekt des Dokuments: frei positioniert (``frei``) oder im Text. Felder, die es nur bei der einen Art gibt, sind bei der anderen leer."""
    id: int
    frei: bool
    art: str
    breite: float
    hoehe: float
    ressource: str
    daten: Mapping[str, Daten]
    alt_text: str
    anker: int | None = None
    bezug_h: str = ""
    x: float = 0.0
    ausr_h: str = ""
    bezug_v: str = ""
    y: float = 0.0
    ausr_v: str = ""
    umbruch: str = ""
    ebene: int = 0
    format: Mapping[str, Daten] | None = None


@dataclass(frozen=True)
class Ebenenabbild:
    stil: str
    format: str
    start: int
    ausr: str
    einzug: float
    zeichen: Mapping[str, Daten] | None
    zusatz: Mapping[str, Daten] | None


@dataclass(frozen=True)
class Listenabbild:
    id: int
    ebenen: tuple[Ebenenabbild, ...]
    name: str


def _sitzung(kennung: int):
    return _steuerung._sitzungen[kennung].sitzung


def _absatz(a) -> Absatzabbild:
    return Absatzabbild(a.id, fest(a.format), fest(a.zeichenformat), a.liste_id, a.ebene, a.laenge, a.text())


def _tabelle(t) -> Tabellenabbild:
    return Tabellenabbild(t.id, tuple(tuple(Zellabbild(tuple(b.id for b in z.bloecke if hasattr(b, "inhalte")), fest(z.format), z.zeilenspanne, z.spaltenspanne,
                                                       None if z.verdeckt_von is None else (z.verdeckt_von[0], z.verdeckt_von[1]),
                                                       "\n".join(b.text() for b in z.bloecke if hasattr(b, "inhalte"))) for z in zeile)
                                      for zeile in t.zellen),
                          tuple(t.spaltenbreiten), tuple(t.zeilenhoehen), fest(t.format))


def _frei(o) -> Objektabbild:
    return Objektabbild(o.id, True, o.art, o.breite, o.hoehe, o.ressource, fest(o.daten), o.alt_text, o.anker, o.bezug_h, o.x, o.ausr_h, o.bezug_v, o.y,
                        o.ausr_v, o.umbruch, o.ebene)


def _inline(o) -> Objektabbild:
    return Objektabbild(o.id, False, o.art, o.breite, o.hoehe, o.ressource, fest(o.daten), o.alt_text, format=fest(o.format))


# ---- Absätze ---------------------------------------------------------------------------------------------------------------------------------------
def absatz(kennung: int, absatz_id: int) -> Absatzabbild:
    return _absatz(_sitzung(kennung)._absatz(absatz_id))


def absatz_an_marke(kennung: int) -> Absatzabbild:
    s = _sitzung(kennung)
    return _absatz(s._absatz(s.auswahl.kopf.absatz_id))


def absatzlaengen(kennung: int) -> tuple[tuple[int, int], ...]:
    """(Id, Länge) aller Absätze in Dokumentreihenfolge."""
    return tuple((a.id, a.laenge) for a in _sitzung(kennung).dokument.absaetze())


def letzter_absatz(kennung: int) -> int:
    """Die Id des letzten Absatzes des Dokuments."""
    return list(_sitzung(kennung).dokument.absaetze())[-1].id


def verwendete_vorlagen(kennung: int) -> frozenset[str]:
    """Die Namen der Formatvorlagen, die Absätze des Dokuments tragen."""
    return frozenset(a.format.get("vorlage") or "Standard" for a in _sitzung(kennung).dokument.absaetze())


def sortierbare_absaetze(kennung: int) -> tuple[tuple[int, str], ...]:
    """(Id, Text) der Absätze, die „Sortieren“ umstellt: die der Auswahl, ohne Auswahl alle des ersten Textflusses; leer, wenn Tabellen
    dazwischenstehen."""
    s = _sitzung(kennung)
    if s.auswahl.leer:                                      # ohne Markierung: alle Absätze des ersten Textflusses
        ids = [b.id for b in s.dokument.abschnitte[0].bloecke if hasattr(b, "inhalte")]
        if len(ids) != len(s.dokument.abschnitte[0].bloecke):
            ids = []
    else:
        von, bis = s._bereich()
        _b, liste, i0, _a = s.dokument.finde(von.absatz_id)
        ende = s.dokument.finde(bis.absatz_id)
        ids = [b.id for b in liste[i0:ende[2] + 1] if hasattr(b, "inhalte")] if ende is not None and ende[1] is liste else []
        if len(ids) != (ende[2] - i0 + 1 if ende is not None else 0):
            ids = []
    return tuple((i, s._absatz(i).text()) for i in ids)


def dokumenttext(kennung: int) -> str:
    """Der Text des Dokuments, Absätze durch Zeilenwechsel getrennt."""
    return _sitzung(kennung).dokument.text()


def standardformat(kennung: int) -> Mapping[str, Daten]:
    """Das Grundformat des Dokuments (Schrift, Größe …)."""
    return fest(_sitzung(kennung).dokument.standardformat)


def vorlage_vorhanden(kennung: int, name: str) -> bool:
    return name in _sitzung(kennung).dokument.vorlagen


def bereiche_mit(kennung: int, schluessel: str) -> tuple[tuple[Stelle, Stelle], ...]:
    """Zusammenhängende Bereiche (je Absatz), deren Zeichenformat ``schluessel`` trägt; ein Bereich endet, wo sich dessen Wert ändert."""
    return tuple(((b.anker[0], b.anker[1]), (b.kopf[0], b.kopf[1])) for b in _sitzung(kennung).bereiche(lambda f: schluessel in f, lambda f: f.get(schluessel)))


def aenderungsbereiche(kennung: int) -> tuple[tuple[Stelle, Stelle], ...]:
    """Bereiche nachverfolgter Änderungen; ein Bereich endet, wo Art, Bearbeiter oder Zeit wechseln."""
    return tuple(((b.anker[0], b.anker[1]), (b.kopf[0], b.kopf[1]))
                 for b in _sitzung(kennung).bereiche(lambda f: "aenderung" in f, lambda f: (f["aenderung"], f.get("autor", ""), f.get("datum", ""))))


def notenbereiche(kennung: int) -> tuple[tuple[Stelle, Stelle], ...]:
    """Die Stellen der Notenzeichen im Text."""
    return tuple(((b.anker[0], b.anker[1]), (b.kopf[0], b.kopf[1])) for b in _sitzung(kennung).bereiche(lambda f: "note" in f))


# ---- Tabellen --------------------------------------------------------------------------------------------------------------------------------------
def tabelle(kennung: int, tabellen_id: int) -> Tabellenabbild:
    return _tabelle(_sitzung(kennung)._tabelle(tabellen_id))


def tabelle_von(kennung: int, absatz_id: int) -> tuple[Tabellenabbild, int, int] | None:
    """(Tabelle, Zeile, Spalte) der innersten Zelle, in der der Absatz steht – ``None`` im Fließtext."""
    stelle = _sitzung(kennung).tabelle_von(absatz_id)
    return None if stelle is None else (_tabelle(stelle[0]), stelle[1], stelle[2])


def zellen_im_bereich(kennung: int) -> tuple[int, tuple[tuple[int, int], ...]] | None:
    """(Tabellen-Id, Zellen) der Zellen, die die Auswahl in einer Tabelle überstreicht – ``None`` außerhalb."""
    r = _sitzung(kennung).zellen_im_bereich()
    return None if r is None else (r[0], tuple((z, s) for z, s in r[1]))


# ---- Objekte ---------------------------------------------------------------------------------------------------------------------------------------
def objekt(kennung: int, objekt_id: int | None) -> Objektabbild | None:
    """Das frei positionierte Objekt mit der Id oder ``None``."""
    o = _sitzung(kennung).dokument.objekte.get(objekt_id)
    return None if o is None else _frei(o)


def objekte(kennung: int) -> tuple[Objektabbild, ...]:
    """Alle frei positionierten Objekte des Dokuments."""
    return tuple(_frei(o) for o in _sitzung(kennung).dokument.objekte.values())


def inline(kennung: int, objekt_id: int) -> Objektabbild | None:
    """Das Objekt im Text mit der Id oder ``None``."""
    f = _sitzung(kennung)._inline(objekt_id)
    return None if f is None else _inline(f[2])


def objekt_position(kennung: int, objekt_id: int) -> Stelle | None:
    """Die Textstelle vor einem Objekt im Text; bei einem freien Objekt der Anfang seines Ankerabsatzes."""
    p = _sitzung(kennung).objekt_position(objekt_id)
    return None if p is None else (p[0], p[1])


def ressource(kennung: int, name: str) -> bytes | None:
    """Die Bilddaten einer Ressource des Dokuments."""
    return _sitzung(kennung).dokument.ressourcen.get(name)


# ---- Listen, Noten, Kommentare, Quellen --------------------------------------------------------------------------------------------------------------
def liste(kennung: int, liste_id: int | None) -> Listenabbild | None:
    d = _sitzung(kennung).dokument.listen.get(liste_id) if liste_id is not None else None
    if d is None:
        return None
    return Listenabbild(d.id, tuple(Ebenenabbild(e.stil, e.format, e.start, e.ausr, e.einzug, fest(e.zeichen), fest(e.zusatz)) for e in d.ebenen), d.name)


def noten(kennung: int) -> Mapping[str, Mapping[int, str]]:
    """Art der Note → (Id → Text)."""
    return fest({art: {n.id: n.text for n in noten.values()} for art, noten in _sitzung(kennung).dokument.noten.items()})


def kommentare(kennung: int) -> Mapping[int, Mapping[str, Daten]]:
    """Id des Kommentars → Bearbeiter, Initialen, Zeit, Text und ob er erledigt ist."""
    return fest({k.id: {"autor": k.autor, "initialen": k.initialen, "datum": k.datum, "text": k.text, "geloest": k.geloest}
                 for k in _sitzung(kennung).dokument.kommentare.values()})


def quellen(kennung: int) -> tuple[Mapping[str, Daten], ...]:
    return tuple(fest(dict(q)) for q in _sitzung(kennung).dokument.quellen)


def eigenschaft(kennung: int, name: str) -> Daten:
    """Eine Eigenschaft des Dokuments (zum Beispiel ``zitierweise``) oder ``None``."""
    return fest(_sitzung(kennung).dokument.eigenschaften.get(name))


# ---- Abschnitte ------------------------------------------------------------------------------------------------------------------------------------
def abschnitt_index(kennung: int, block_id: int) -> int:
    """Der Abschnitt (Index), in dem der Absatz oder die Tabelle steht."""
    return _sitzung(kennung).abschnitt_index(block_id)


def abschnitte_anzahl(kennung: int) -> int:
    return len(_sitzung(kennung).dokument.abschnitte)


def abschnitt_beginn(kennung: int, index: int) -> str:
    return _sitzung(kennung).dokument.abschnitte[index].beginn


def abschnitt_erster_absatz(kennung: int, index: int) -> int | None:
    """Die Id des ersten Absatzes des Abschnitts; ``None``, wenn es den Abschnitt nicht gibt oder er keinen Absatz hat."""
    d = _sitzung(kennung).dokument
    if not 0 <= index < len(d.abschnitte):
        return None
    erster = next((b for b in d.abschnitte[index].bloecke if hasattr(b, "inhalte")), None)
    return None if erster is None else erster.id


def seite_felder(kennung: int, index: int) -> Mapping[str, Daten]:
    """Die Seiteneinrichtung des Abschnitts ``index`` (höchstens der letzte) als Wörterbuch ihrer Felder; Kopf- und Fußzeilen ebenfalls als
    Wörterbuch."""
    import dataclasses
    abschnitte = _sitzung(kennung).dokument.abschnitte
    return fest(dataclasses.asdict(abschnitte[min(index, len(abschnitte) - 1)].seite))


def metadaten(kennung: int) -> Mapping[str, Daten]:
    """Die Metadaten des Dokuments (Titel, Bearbeiter, Sprache …), wie sie beim Öffnen gelesen wurden."""
    return fest(dict(_steuerung._sitzungen[kennung].meta))


def metadatum_setzen(kennung: int, name: str, wert: Daten) -> None:
    """Einen Eintrag der Metadaten des Dokuments setzen."""
    _steuerung._sitzungen[kennung].meta[name] = wert


def metadatum_entfernen(kennung: int, name: str) -> None:
    """Einen Eintrag der Metadaten des Dokuments entfernen (fehlt er, geschieht nichts)."""
    _steuerung._sitzungen[kennung].meta.pop(name, None)
