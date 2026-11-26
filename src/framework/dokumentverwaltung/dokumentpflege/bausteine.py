"""Textbausteine: markierter Text mit Formatierung unter einem Namen merken und später einfügen."""
from __future__ import annotations

import json
import os

from core.dokument.serialisierung import bloecke_aus_daten, bloecke_zu_daten
from system.plattform.pfade import data_dir


def _pfad() -> str:
    return os.path.join(data_dir(), "bausteine.json")


def laden() -> list[dict]:
    try:
        with open(_pfad(), encoding="utf-8") as fh:
            d = json.load(fh)
        return [b for b in d if isinstance(b, dict) and b.get("name") and (b.get("absaetze") or b.get("text"))]
    except (OSError, ValueError):
        return []


def speichern(liste: list[dict]) -> None:
    try:
        tmp = _pfad() + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(liste, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, _pfad())
    except OSError:
        pass


def standard() -> list[dict]:
    """Die mitgelieferten Bausteine (Briefe, Bewerbungen …); sie lassen sich einfügen, aber nicht ändern."""
    try:
        from system.plattform import ressourcen_pfade as pfade
        with open(os.path.join(pfade.RESSOURCEN, "bausteine_standard.json"), encoding="utf-8") as fh:
            return [dict(b, standard=True) for b in json.load(fh)]
    except (OSError, ValueError, ImportError):
        return []


def alle() -> list[dict]:
    """Mitgelieferte und eigene Bausteine (Eigene zuletzt)."""
    return standard() + laden()


def finde_kuerzel(kuerzel: str) -> dict | None:
    """Der Baustein zu einem Kürzel (Eigene gehen vor den mitgelieferten)."""
    k = (kuerzel or "").strip()
    return next((b for b in reversed(alle()) if k and b.get("kuerzel") == k), None) if k else None


def hinzufuegen(name: str, bloecke: list, kuerzel: str = "") -> None:
    """Merkt den Ausschnitt (``Bearbeitungssitzung.ausschnitt``: Blöcke des Dokumentmodells) unter ``name``."""
    liste = [b for b in laden() if b["name"] != name]
    text = "\n".join(b.text() for b in bloecke if hasattr(b, "text"))
    liste.append({"name": name, "kuerzel": (kuerzel or "").strip(), "bloecke": bloecke_zu_daten(bloecke), "text": text})
    speichern(liste)


def entfernen(name: str) -> None:
    speichern([b for b in laden() if b["name"] != name])


def _alte_bloecke(absaetze: list) -> list:
    """Bausteine im älteren Format (``absaetze``: Textstücke mit ``fett``, ``kursiv`` … je Absatz) als Absätze des Dokumentmodells."""
    from core.dokument.dokument import Absatz, Lauf
    aus = []
    for a in absaetze:
        laeufe = []
        for r in a.get("runs", []):
            fmt = {}
            for alt, neu in (("fett", "fett"), ("kursiv", "kursiv"), ("unter", "unterstrichen"), ("durch", "durchgestrichen"), ("farbe", "farbe"),
                             ("marker", "marker"), ("pt", "groesse_pt"), ("schrift", "schrift")):
                if r.get(alt):
                    fmt[neu] = r[alt]
            if r.get("hoch"):
                fmt["hoch_tief"] = "hoch"
            elif r.get("tief"):
                fmt["hoch_tief"] = "tief"
            if r.get("t"):
                laeufe.append(Lauf(r["t"], fmt))
        aus.append(Absatz(0, laeufe, {"ausrichtung": a["ausr"]} if a.get("ausr") in ("mitte", "rechts", "block") else {}))
    return aus


def bloecke_von(baustein):
    """Die Blöcke des Bausteins mit seiner Formatierung; ``None`` für einen Eintrag ohne Blockdaten (einfacher Text)."""
    if baustein.get("bloecke"):
        return bloecke_aus_daten(baustein["bloecke"])
    if baustein.get("absaetze"):
        return _alte_bloecke(baustein["absaetze"])
    return None


def einfuegen(editor, baustein: dict) -> None:
    """Fügt den Baustein mit seiner Formatierung an der Schreibmarke ein; ein Eintrag ohne Blockdaten kommt als einfacher Text."""
    if baustein.get("bloecke"):
        bloecke = bloecke_aus_daten(baustein["bloecke"])
    elif baustein.get("absaetze"):
        bloecke = _alte_bloecke(baustein["absaetze"])
    else:
        editor.ansicht._aendern(lambda s: s.text_einfuegen(baustein.get("text", "")))
        return
    editor.ansicht._aendern(lambda s: s.ausschnitt_einfuegen(bloecke))
