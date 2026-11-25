"""Qt-freie Fachlogik für Querverweise und Quellenkürzel."""

import re


def querverweis_text_bilden(ziel: dict, wie: str, cursor_position: int,
                            seitenzahl=None, oben_unten: bool = False) -> str:
    richtung = "oben" if ziel["pos"] < cursor_position else "unten"
    if wie == "obenunten":
        return richtung
    if wie == "seite":
        text = str(seitenzahl)
    elif wie == "nummer":
        text = ziel.get("nummer") or ziel["text"]
    elif wie == "nur_text":
        text = ziel.get("inhalt", ziel["text"])
    else:
        text = (ziel.get("inhalt", ziel["text"])
                if ziel["art"] in ("Textmarke", "Nummeriertes Element")
                else ziel["text"])
    if oben_unten and wie in ("seite", "nummer"):
        text += " " + richtung
    return text


def quelle_tag_bilden(quellen: list[dict], q: dict) -> str:
    """Eindeutiger Kurzname (Nachname + Jahr)."""
    basis = re.sub(r"\W+", "", (q.get("autor", "").split(",")[0].split(";")[0] or q.get("titel", "Quelle")))[:20] or "Quelle"
    basis += re.sub(r"\D", "", q.get("jahr", ""))[:4]
    tag, i = basis, 2
    vorhanden = {x["tag"] for x in quellen}
    while tag in vorhanden:
        tag = f"{basis}{i}"
        i += 1
    return tag
