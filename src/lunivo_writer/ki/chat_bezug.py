"""Woran sich eine Chat-Antwort bezieht (Markierung/Schreibmarke zum Sendezeitpunkt) und ob sie noch passt. Reine Logik, ohne Qt.

Der Bezug liegt nur im Speicher: ``alt`` (der markierte Text) wird nie gesendet, gespeichert oder protokolliert."""
from __future__ import annotations

from lunivo_writer.ki import ki as K
from lunivo_writer.editor.text import ki_markdown

MELDUNG_GEAENDERT = "Der Text hat sich seit der Frage geändert. Nichts wurde geändert."
MELDUNG_EDITOR = "Die Frage gehört zu einem anderen Dokument. Nichts wurde geändert."
ANLIEGEN_AEHNLICH = 0.5      # Wortähnlichkeit (difflib), ab der eine Antwort ohne Marker als Überarbeitung des Dokuments gilt
MELDUNG_KEIN_BEZUG = "Zu dieser Antwort gibt es keine Stelle im Text. Nichts wurde geändert."
MELDUNG_ANGEWENDET = "Diese Antwort wurde schon ins Dokument übernommen."
MELDUNG_KEINE_REZENSION = "Als Rezension geht nur eine Überarbeitung des Textes (einzelne Wörter geändert). Diese Antwort bitte einfügen oder ersetzen."
MELDUNG_OHNE_VERFOLGUNG = "Dieser Editor kann keine Änderungen verfolgen. Nichts wurde geändert."
MELDUNG_REZENSION = "Als Änderungen eingetragen. Im Reiter „Überprüfen“ einzeln annehmen oder ablehnen; Strg+Z macht alles rückgängig."
MELDUNG_OHNE_MARKIERUNG = "Die Frage wurde ohne Markierung gestellt und die Antwort ist keine Überarbeitung des Dokuments. Zum Ersetzen die Stelle markieren und neu fragen."


def bezug_bauen(von: int, bis: int, markiert: bool, revision: int, alt: str, dokument,
                 editor_obj=None, dokument_obj=None, ganz: str = "") -> dict:
    """``ganz``: ohne Markierung der Dokumenttext zum Sendezeitpunkt (nur für den Vorher/Nachher-Vergleich, nie gesendet oder gespeichert).
    Bezug mit Editor-Kennung und optionalen Objektidentitäten zur sicheren Dokumentzuordnung."""
    von, bis = min(von, bis), max(von, bis)
    return {"von": von, "bis": bis, "markiert": bool(markiert), "revision": revision,
            "alt": alt if markiert else "", "ganz": "" if markiert else ganz, "dokument": dokument,
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
    if ki_markdown.hat_struktur(neu):         # formatierte Antwort: Wortvergleich der Klartexte statt des Markdown-Textes
        neu = ki_markdown.klartext(neu)
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


def _aehnlichkeit(alt: str, neu: str) -> float:
    """Wortähnlichkeit 0..1 (Wörter und Zwischenräume wie in ``ki_diff``)."""
    import difflib
    a, n = K._STUECKE.findall(alt), K._STUECKE.findall(neu)
    if not a or not n or len(a) * len(n) > 400000:
        return 0.0
    return difflib.SequenceMatcher(None, a, n, autojunk=False).ratio()


def ersetz_schritte(alt: str, neu: str) -> list[tuple[int, int, str]] | None:
    """Ersetzen als Wortänderungen [(von, bis, text)] in „alt“-Zeichenstellen, von hinten nach vorn — so bleibt die Formatierung des Dokuments
    (Schrift, Absatzformat) an allen unveränderten Stellen erhalten. Nur bei einer Überarbeitung (Wortähnlichkeit ab ``ANLIEGEN_AEHNLICH``);
    sonst None = die Stelle als Ganzes ersetzen. Derselbe Vergleich wie die Vorschau (``ki_diff.aenderungen``, Klartext bei formatierter Antwort)."""
    if not alt:
        return None
    if ki_markdown.hat_struktur(neu):
        neu = ki_markdown.klartext(neu)
    if _aehnlichkeit(alt, neu) < ANLIEGEN_AEHNLICH:
        return None
    bl = K.aenderungen(alt, neu)
    if bl is None:
        return None
    return [(b["von"], b["bis"], b["text"]) for b in reversed(bl)]


def vorher_der_nachricht(nachricht: dict, bezug: dict | None) -> str:
    """Text der Stelle zum Fragezeitpunkt, mit dem die Antwort verglichen wird: die Markierung (``alt``); ohne Markierung der ganze Dokumenttext (``ganz``),
    aber nur bei einer Überarbeitung (Marker in der Antwort oder Wortähnlichkeit ab ``ANLIEGEN_AEHNLICH``). Sonst "". Einzige Stelle dieser Entscheidung."""
    from lunivo_writer.ki import chat_antwort as CA
    if not bezug:
        return ""
    if bezug.get("markiert") and bezug.get("alt"):
        return bezug["alt"]
    ganz = bezug.get("ganz") or ""
    if not ganz.strip():
        return ""
    if CA.MARKE_ANFANG in nachricht.get("text", "") or _aehnlichkeit(ganz, CA.kern_von(nachricht)) >= ANLIEGEN_AEHNLICH:
        return ganz
    return ""


def vorschau_der_nachricht(nachricht: dict, bezug: dict | None) -> list[tuple[str, str]] | None:
    """Stücke Kern gegen die Stelle aus ``vorher_der_nachricht``; None, wenn es keine gibt. Prüft nicht, ob der Bezug noch passt."""
    from lunivo_writer.ki import chat_antwort as CA
    vorher = vorher_der_nachricht(nachricht, bezug)
    return vorschau_stuecke(vorher, CA.kern_von(nachricht)) if vorher else None


def vorschau_einfuegen(neu: str) -> list[tuple[str, str]]:
    """Einfache Vorschau fürs Einfügen: nur der neue Text."""
    return [("neu", neu)] if neu else []
