"""Sprechblasen beim Drucken und im PDF: Die Seite wird verkleinert, daneben stehen die Kommentar-Blasen
(Darstellung und Stapelung: ``editor/objekte/sprechblasen.py``)."""
from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QFont, QPainter, QTextDocument

from lunivo_writer.modelle.seite import PageSettings, mm_to_px


def blasen_geometrie(page: PageSettings, opt: dict | None) -> dict | None:
    """Platz für Sprechblasen beim Drucken: Die Seite wird verkleinert, daneben stehen die Blasen. → None ohne Blasen."""
    bd = (opt or {}).get("blasen")
    if not bd:
        return None
    from lunivo_writer.editor.objekte import sprechblasen as SB
    k = bd["konfig"]
    pw, ph = mm_to_px(page.width_mm), mm_to_px(page.height_mm)
    bw, gap = mm_to_px(SB.breite_mm(k)), mm_to_px(SB.LUECKE_MM)

    def faktor(sw: float, sh: float) -> float:
        return min((sw - bw - gap) / pw, sh / ph)
    f_hoch = faktor(pw, ph)
    f_quer = faktor(ph, pw) if not page.landscape else f_hoch
    aus = k["ausrichtung"]
    quer = (not page.landscape) and (aus == "Querformat" or (aus == "Automatisch" and f_quer > f_hoch + 0.02))
    sw, sh = (ph, pw) if quer else (pw, ph)
    f = min(1.0, faktor(sw, sh))
    links = k["rand"] == "Links"
    x_page = bw + gap if links else 0.0
    return {"quer": quer, "f": f, "sw": sw, "sh": sh, "pw": pw, "x_page": x_page, "links": links,
            "x_blasen": 0.0 if links else pw * f + gap, "bw": bw, "mt": mm_to_px(page.margin_top_mm), "k": k}


def blasen_pro_seite(d: QTextDocument, page: PageSettings, liste: list[int], bd: dict, ort=None) -> dict[int, list]:
    """{Blattseite (1-basiert): [(Blase, y in px auf der Textfläche)]} — die Blasen stammen aus der Kopie selbst."""
    from lunivo_writer.editor.objekte import sprechblasen as SB
    from lunivo_writer.editor.seite.pdf_struktur import fluss_ort
    ort = ort or fluss_ort(page.content_height_px, max(1, int(page.spalten)))
    lay = d.documentLayout()
    out: dict[int, list] = {}
    for bl in SB.sammeln(d, bd.get("kommentare", {}), bd["konfig"]["verwenden"]):
        b = d.findBlock(bl.von)
        if not b.isValid() or b.layout() is None:
            continue
        ln = b.layout().lineForTextPosition(bl.von - b.position())
        y = lay.blockBoundingRect(b).top() + (ln.y() if ln.isValid() else 0)
        seite, yr = ort(y)
        out.setdefault(seite, []).append((bl, yr))
    return out


def blasen_zeichnen(p: QPainter, eintraege: list, geo: dict) -> None:
    from lunivo_writer.editor.objekte import sprechblasen as SB
    if not eintraege:
        return
    font = QFont("Liberation Sans")
    font.setPixelSize(11)
    w, f = geo["bw"], geo["f"]
    hoehen = [SB.messen(bl, w, font) for bl, _y in eintraege]
    anker = [geo["mt"] * f + y * f for _bl, y in eintraege]
    ys = SB.stapeln(anker, hoehen, geo["sh"] - 12)
    kante = geo["x_page"] + (0 if geo["links"] else geo["pw"] * f)
    for (bl, _y), yy, h, a in zip(eintraege, ys, hoehen, anker):
        r = QRectF(geo["x_blasen"], yy, w, h)
        if geo["k"]["linien"]:
            SB.verbindung(p, bl, kante, a + 8, r, not geo["links"])
        SB.zeichnen(p, bl, r, font, druck=True)
