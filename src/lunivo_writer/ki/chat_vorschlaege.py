"""Welche Aufgaben der Chat vorschlägt — je Zustand (Markierung / Dokument / leeres Dokument). Schicht 1: nur Daten aus ``ki``, kein Qt."""
from __future__ import annotations

from lunivo_writer.ki import ki as K

def _eintrag(id_: str, konfig) -> dict | None:
    if id_ in K.VORLAGE_ANWEISUNG:
        titel, anw = K.VORLAGE_ANWEISUNG[id_]
        return {"id": id_, "titel": titel, "anweisung": anw}
    if id_ == "zusammenfassen":
        return {"id": id_, "titel": "Zusammenfassen", "anweisung": K.ANWEISUNG_ZUSAMMENFASSUNG}
    if id_ == "uebersetzen":
        sprache = konfig["sprache"] if konfig is not None else "Englisch"
        return {"id": id_, "titel": "Text übersetzen", "anweisung": K.anweisung_uebersetzung(sprache)}
    if id_ in K._AKTION_SATZ:
        return {"id": id_, "titel": dict(K.TEXT_AKTIONEN).get(id_, id_), "anweisung": K._AKTION_SATZ[id_]}
    return None


# Die Chips der Vorlage, immer in dieser Reihenfolge (id, braucht Text)
_VORLAGE = (("dokument_zusammenfassen", True), ("umschreiben", True), ("vereinfachen", True), ("erweitern_inhalt", True), ("korrektur", True),
            ("zusammenfassung", True), ("uebersetzen", True), ("inhaltsverzeichnis", True), ("titel", True), ("kernpunkte", True))


def chat_vorschlaege(auswahl: bool, leer: bool, konfig=None) -> list[dict]:
    """Immer die zehn Chips der Vorlage. Jeder Eintrag: {id, titel, anweisung, aktiv, hinweis}; ``aktiv`` ist False, wenn der Chip Text braucht und das Dokument leer
    ist (``hinweis`` erklärt es für den Tooltip). Mit Markierung gilt der Chip für die Markierung. Eigene Assistenten (``konfig``) kommen dazu, wenn es Text gibt."""
    r = []
    for id_, braucht_text in _VORLAGE:
        e = _eintrag(id_, konfig)
        if e is None:
            continue
        sperre = braucht_text and leer
        e["aktiv"] = not sperre
        e["hinweis"] = "Zuerst Text ins Dokument schreiben" if sperre else ("Gilt für die Markierung" if auswahl else "Gilt für das ganze Dokument")
        r.append(e)
    if konfig is not None and not leer:
        r += [{"id": "assistent:" + a["id"], "titel": a["name"], "anweisung": a["prompt"], "aktiv": True, "hinweis": ""} for a in konfig.assistenten("aktion")]
    return r
