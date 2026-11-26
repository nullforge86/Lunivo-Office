"""Listen an der Schreibmarke: die Beschreibung der Listenfenster (einfache Liste oder Gliederung) in die Ebenen des Modells umsetzen und zurück,
und die Liste auf die Auswahl anwenden – anhand der Kennung des Dokuments."""
from __future__ import annotations

import dataclasses
from collections.abc import Mapping

from framework.anbindung import Daten, fest
from framework.sitzungen import sitzung as _steuerung

PUNKTE = ("disc", "circle", "square")
ZAHLEN_TIEFER = ("dezimal", "klein", "roem_klein")


def _sitzung(kennung: int):
    return _steuerung._sitzungen[kennung].sitzung


def _spec_zu_ebenen(spec) -> list:
    """Die 9 Ebenen einer Liste des Modells für die Beschreibung, die die Listenfenster liefern (einfache Liste oder Gliederung)."""
    from core.dokument import LISTEN_EBENEN, ListenEbene
    from core.listen import PLATZHALTER
    if "ebenen" in spec:
        aus = []
        for x in spec["ebenen"][:LISTEN_EBENEN]:
            zusatz = {k: x[k] for k in ("tab", "ausr_art", "danach", "neu", "norm", "vorlage") if x.get(k)}
            if x.get("zeichen"):
                zusatz["zeichenformat"] = dict(x["zeichen"])
            fmt, stil = x.get("format", ""), x.get("stil", "dezimal")
            if stil in PUNKTE:
                aus.append(ListenEbene(stil=stil, ausr=x["ausr"], einzug=x["einzug"], zusatz=zusatz))
            elif not any(ch in fmt for ch in PLATZHALTER):
                aus.append(ListenEbene(stil="zeichen", zeichen=fmt or "•", ausr=x["ausr"], einzug=x["einzug"], zusatz=zusatz))
            else:
                aus.append(ListenEbene(stil=stil, format=fmt, start=int(x.get("start", 1)), ausr=x["ausr"], einzug=x["einzug"], zusatz=zusatz))
        while len(aus) < LISTEN_EBENEN:
            i = len(aus)
            aus.append(dataclasses.replace(aus[-1], ausr=aus[-1].ausr + 6.3, einzug=aus[-1].einzug + 6.3) if aus else ListenEbene(ausr=6.3 * i, einzug=6.3 * (i + 1)))
        return aus
    pos = spec.get("pos") or {}
    stil = spec["stil"]
    zusatz_pos = {k: pos[k] for k in ("tab", "ausr_art", "danach") if pos.get(k)}
    ebenen = []
    for i in range(LISTEN_EBENEN):
        ausr, einzug = pos.get("ausr", 0.0) + 6.3 * i, pos.get("einzug", 6.3) + 6.3 * i
        zusatz = dict(zusatz_pos)
        if spec.get("zeichen"):
            zusatz["zeichenformat"] = dict(spec["zeichen"])
        if stil in PUNKTE:
            rest = [s for s in PUNKTE if s != stil]
            ebenen.append(ListenEbene(stil=([stil] + rest)[i % 3], ausr=ausr, einzug=einzug, zusatz=zusatz))
        else:
            art = stil if i == 0 else ZAHLEN_TIEFER[i % 3]
            ebenen.append(ListenEbene(stil=art, format=spec.get("praefix", "") + PLATZHALTER[i] + spec.get("suffix", "."), start=int(spec.get("start", 1)) if i == 0 else 1,
                                      ausr=ausr, einzug=einzug, zusatz=zusatz))
    return ebenen


def _ebenen_zu_spec(ebenen: list) -> dict:
    """Das Gegenstück: die Beschreibung der Liste für die Listenfenster (einfach, wenn sie genau so entstanden sein kann, sonst Gliederung)."""
    from core.dokument import AUFZAEHLUNGEN
    from core.listen import PLATZHALTER, ZEICHEN_DER_AUFZAEHLUNG
    from core.listen.aufzaehlungen import liste
    from core.listen.mehrstufig import ebene
    if ebenen and all(e.stil in PUNKTE for e in ebenen) and _spec_zu_ebenen(liste(ebenen[0].stil)) == ebenen:
        return liste(ebenen[0].stil)
    e0 = ebenen[0]
    if e0.stil in ("dezimal", "klein", "gross", "roem_klein", "roem_gross") and e0.format.count(PLATZHALTER[0]) == 1 and not e0.zusatz:
        vor, _s, nach = e0.format.partition(PLATZHALTER[0])
        einfach = liste(e0.stil, vor, nach, e0.start)
        if _spec_zu_ebenen(einfach) == ebenen:
            return einfach
    aus = []
    for e in ebenen:
        mehr = {k: e.zusatz[k] for k in ("tab", "ausr_art", "danach", "neu", "norm", "vorlage") if e.zusatz.get(k)}
        if e.stil in AUFZAEHLUNGEN:
            zeichen = e.zeichen or ZEICHEN_DER_AUFZAEHLUNG.get(e.stil, "•")
            aus.append(ebene("dezimal", zeichen, 1, e.ausr, e.einzug, e.zusatz.get("zeichenformat"), **mehr))
        else:
            aus.append(ebene(e.stil, e.format or PLATZHALTER[len(aus)] + ".", e.start, e.ausr, e.einzug, e.zusatz.get("zeichenformat"), **mehr))
    return {"ebenen": aus}


def liste_spec(kennung: int) -> Mapping[str, Daten] | None:
    """Beschreibung der Liste am Absatz der Schreibmarke (für die Listenfenster), ``None`` ohne Liste."""
    s = _sitzung(kennung)
    d = s.dokument
    a = s._absatz(s.auswahl.kopf.absatz_id)
    definition = d.listen.get(a.liste_id) if a.liste_id is not None else None
    return fest(_ebenen_zu_spec(definition.ebenen)) if definition is not None and definition.ebenen else None


def liste_setzen(kennung: int, spec: Mapping[str, Daten]) -> bool:
    """Wendet die Liste auf die Absätze der Auswahl an. Folgt sie unmittelbar auf eine gleiche Liste, zählt sie weiter. ``False``, wenn der Kern ablehnt."""
    from core.bearbeitung import BearbeitungsFehler
    ebenen = _spec_zu_ebenen(spec)
    s = _sitzung(kennung)
    try:
        with s.gruppe("Liste"):
            absaetze = list(s.dokument.absaetze())
            start, _ende = s._bereich()
            i = next((k for k, a in enumerate(absaetze) if a.id == start.absatz_id), 0)
            davor = absaetze[i - 1] if i > 0 else None
            alt = s.dokument.listen.get(davor.liste_id) if davor is not None and davor.liste_id is not None else None
            lid = alt.id if alt is not None and alt.ebenen == ebenen else s.liste_anlegen(ebenen)
            s.liste_anwenden(lid)
    except BearbeitungsFehler:
        return False
    return True
