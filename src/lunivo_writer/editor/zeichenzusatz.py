"""Zeichenzusätze der Gruppe „Schriftart“ ▸ Groß-/Kleinschreibung: Eingeschlossene Zeichen und Phonetisches Leitzeichen.

Beide hängen als Eigenschaft am Zeichenformat (``P_UMSCHLOSSEN``, ``P_RUBY`` in ``editor/zusatz.py``) und werden von Lunivo selbst gezeichnet
(``editor/textfx.py``). Hier steht nur das Reine: wie so eine Eigenschaft als Text aussieht und wie man sie liest. Kein Qt-Fenster.

    P_UMSCHLOSSEN  "kreis|reduzieren"                     Form und Vorlage (reduzieren | erweitern)
    P_RUBY         "Ruby-Text|zentriert|0|7"              Text über dem Basistext, Ausrichtung, Abstand (pt), Größe (pt)
"""
from __future__ import annotations

FORMEN = (("kreis", "Kreis"), ("quadrat", "Quadrat"), ("dreieck", "Dreieck"), ("raute", "Raute"))
VORLAGEN = (("ohne", "Ohne"), ("reduzieren", "Text reduzieren"), ("erweitern", "Symbol erweitern"))
AUSRICHTUNGEN = (("zentriert", "Zentriert"), ("links", "Links"), ("rechts", "Rechts"), ("verteilt", "Verteilt"))


def umschlossen_text(form: str, vorlage: str) -> str:
    return "" if vorlage == "ohne" or form not in dict(FORMEN) else f"{form}|{vorlage}"


def umschlossen_lesen(text: str) -> tuple[str, str] | None:
    teile = (text or "").split("|")
    return (teile[0], teile[1]) if len(teile) == 2 and teile[0] in dict(FORMEN) and teile[1] in ("reduzieren", "erweitern") else None


def ruby_text(ruby: str, ausrichtung: str = "zentriert", abstand: float = 0.0, groesse: float = 7.0) -> str:
    ruby = ruby.replace("|", " ")
    return f"{ruby}|{ausrichtung}|{abstand:g}|{groesse:g}" if ruby.strip() else ""


def ruby_lesen(text: str) -> dict | None:
    teile = (text or "").split("|")
    if len(teile) != 4 or not teile[0]:
        return None
    try:
        return {"ruby": teile[0], "ausrichtung": teile[1], "abstand": float(teile[2]), "groesse": float(teile[3])}
    except ValueError:
        return None
