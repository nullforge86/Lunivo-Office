"""Woran sich eine Chat-Antwort bezieht (Markierung/Schreibmarke zum Sendezeitpunkt) und ob sie noch passt. Reine Logik, ohne Qt.

Der Bezug liegt nur im Speicher: ``alt`` (der markierte Text) wird nie gesendet, gespeichert oder protokolliert."""
from __future__ import annotations

from lunivo_writer.ai import ki as K

MELDUNG_GEAENDERT = "Der Text hat sich seit der Frage geändert. Nichts wurde geändert."
MELDUNG_EDITOR = "Die Frage gehört zu einem anderen Dokument. Nichts wurde geändert."
MELDUNG_KEIN_BEZUG = "Zu dieser Antwort gibt es keine Stelle im Text. Nichts wurde geändert."
MELDUNG_ANGEWENDET = "Diese Antwort wurde schon ins Dokument übernommen."
MELDUNG_OHNE_MARKIERUNG = "Die Frage wurde ohne Markierung gestellt. Zum Ersetzen die Stelle markieren und neu fragen."


def bezug_bauen(von: int, bis: int, markiert: bool, revision: int, alt: str, dokument,
                 editor_obj=None, dokument_obj=None) -> dict:
    """Bezug mit Editor-Kennung und optionalen Objektidentitäten zur sicheren Dokumentzuordnung."""
    von, bis = min(von, bis), max(von, bis)
    return {"von": von, "bis": bis, "markiert": bool(markiert), "revision": revision,
            "alt": alt if markiert else "", "dokument": dokument,
            "editor_obj": editor_obj, "dokument_obj": dokument_obj}


def bezug_angewendet() -> dict:
    """Marke für Aktionen, die ihr Ergebnis selbst schon ins Dokument geschrieben haben (Wirkung „ersetzen“/„anhängen“)."""
    return {"angewendet": True}


def bezug_pruefen(bezug: dict | None, revision_jetzt: int | None, editor_jetzt,
                   dokument_jetzt=None, editor_obj_jetzt=None) -> tuple[bool, str]:
    """(ok, Grund). Gleiche Revision, Editor-Kennung und – sofern erfasst – dieselben Objektidentitäten."""
    if not bezug:
        return False, MELDUNG_KEIN_BEZUG
    if bezug.get("angewendet"):
        return False, MELDUNG_ANGEWENDET
    if editor_jetzt is None or revision_jetzt is None or bezug["dokument"] != editor_jetzt:
        return False, MELDUNG_EDITOR
    if bezug.get("editor_obj") is not None and bezug["editor_obj"] is not editor_obj_jetzt:
        return False, MELDUNG_EDITOR
    if bezug.get("dokument_obj") is not None and bezug["dokument_obj"] is not dokument_jetzt:
        return False, MELDUNG_EDITOR
    if bezug["revision"] != revision_jetzt:
        return False, MELDUNG_GEAENDERT
    return True, ""


def vorschau_stuecke(alt: str, neu: str) -> list[tuple[str, str]]:
    """Alt → neu als Stücke (art, text); art: „gleich“, „entfernt“, „neu“. Ohne Farben und Markup.
    Bei zu großen Texten (``ki.aenderungen`` liefert None) zwei Blöcke: alt entfernt, neu neu."""
    bl = K.aenderungen(alt, neu)
    if bl is None:
        return [s for s in (("entfernt", alt), ("neu", neu)) if s[1]]
    out: list[tuple[str, str]] = []
    pos = 0
    for b in bl:
        if b["von"] > pos:
            out.append(("gleich", alt[pos:b["von"]]))
        if b["bis"] > b["von"]:
            out.append(("entfernt", alt[b["von"]:b["bis"]]))
        if b["text"]:
            out.append(("neu", b["text"]))
        pos = b["bis"]
    if pos < len(alt):
        out.append(("gleich", alt[pos:]))
    return out


def vorschau_einfuegen(neu: str) -> list[tuple[str, str]]:
    """Einfache Vorschau fürs Einfügen: nur der neue Text."""
    return [("neu", neu)] if neu else []
