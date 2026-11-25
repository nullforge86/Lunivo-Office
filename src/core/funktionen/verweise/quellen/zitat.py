"""Zitate im Text einfügen: der Zitattext je Zitierweise, die Quelle wird bei Bedarf im Dokument angelegt."""
from __future__ import annotations

from core.funktionen.verweise.quellen.literatur import zitat


def zitat_einfuegen(ed, q: dict) -> None:
    quellen = ed.quellen
    nr = 1 + [x["tag"] for x in quellen].index(q["tag"]) if q["tag"] in [x["tag"] for x in quellen] else 1
    text = zitat(q, ed.zitierweise, nr)

    def f(s):
        with s.gruppe("Zitat"):
            if not any(x.get("tag") == q["tag"] for x in s.dokument.quellen):
                s.quelle_setzen(q)
            s.zitat_einfuegen(q["tag"], text)
            s.text_einfuegen(" ", format={})
    ed.ansicht._aendern(f)
